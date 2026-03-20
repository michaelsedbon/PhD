"""
JIT-compiled simulation runner — fully GPU-accelerable.

Uses incremental Hamming optimization for memory-efficient N=10M on GPU.
"""

import time
import jax
import jax.numpy as jnp
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from germinal_center.affinity import create_founders_at_distance, batch_affinity

from .config import BacterialConfig
from .state_gpu import BacterialStateGPU
from .state import Snapshot
from .growth_jit import turbidostat_growth_jit, turbidostat_growth_no_migrate_jit, sample_to_lz_jit
from .selection_jit import apply_selection_jit, apply_directed_evolution_jit, apply_top_fraction_jit


def initialize_jit(config: BacterialConfig, rng_key: jnp.ndarray, device=None):
    """Create initial population on the specified device (GPU or CPU)."""
    k1, k2 = jax.random.split(rng_key)

    L = config.shape_space_dim
    antigen = jnp.zeros(L, dtype=jnp.int32)
    N = config.n_founders
    n_max = config.turbidostat_target_n * 2

    est_gb = n_max * (L * 4 + 21) / 1e9  # +21 for hamming(4) + other scalars
    print(f"  N_MAX={n_max:,}, L={L}, est memory: {est_gb:.2f} GB", flush=True)

    if device is None:
        try:
            device = jax.devices('gpu')[0]
            print(f"  Using GPU: {device}", flush=True)
        except RuntimeError:
            device = jax.devices('cpu')[0]
            print(f"  Using CPU: {device}", flush=True)

    def _put(arr):
        return jax.device_put(arr, device)

    # Create founders on CPU first
    founder_seqs = create_founders_at_distance(
        N, antigen, config.initial_hamming_min, config.initial_hamming_max, k1,
    )
    founder_affs = batch_affinity(founder_seqs, antigen,
                                  config.affinity_gamma, config.affinity_eta)
    # Compute founder Hamming distances
    founder_hamming = jnp.sum(founder_seqs != antigen[None, :], axis=1).astype(jnp.float32)
    # Recompute founder affinities with corrected formula to be consistent
    founder_affs = jnp.exp(-((founder_hamming / config.affinity_gamma) ** config.affinity_eta))

    # Allocate all arrays on target device
    sequences = _put(jnp.zeros((n_max, L), dtype=jnp.int8))
    affinities = _put(jnp.zeros(n_max, dtype=jnp.float32))
    hamming = _put(jnp.zeros(n_max, dtype=jnp.float32))
    clone_id = _put(jnp.zeros(n_max, dtype=jnp.int32))
    generation = _put(jnp.zeros(n_max, dtype=jnp.int32))
    cell_id = _put(jnp.zeros(n_max, dtype=jnp.int32))
    parent_id = _put(jnp.full(n_max, -1, dtype=jnp.int32))
    alive = _put(jnp.zeros(n_max, dtype=jnp.bool_))
    div_counter = _put(jnp.zeros(n_max, dtype=jnp.int32))
    in_lz = _put(jnp.zeros(n_max, dtype=jnp.bool_))

    # Write founders
    sequences = sequences.at[:N].set(_put(founder_seqs.astype(jnp.int8)))
    affinities = affinities.at[:N].set(_put(founder_affs))
    hamming = hamming.at[:N].set(_put(founder_hamming))
    clone_id = clone_id.at[:N].set(_put(jnp.arange(N, dtype=jnp.int32)))
    cell_id = cell_id.at[:N].set(_put(jnp.arange(N, dtype=jnp.int32)))
    parent_id = parent_id.at[:N].set(_put(jnp.full(N, -1, dtype=jnp.int32)))
    alive = alive.at[:N].set(True)

    state = BacterialStateGPU(
        sequences=sequences, affinities=affinities, hamming=hamming,
        clone_id=clone_id, generation=generation, cell_id=cell_id,
        parent_id=parent_id, alive=alive, div_counter=div_counter,
        in_lz=in_lz, antigen=_put(antigen),
        next_id=_put(jnp.array([N], dtype=jnp.int32)),
        cycle=_put(jnp.array([0], dtype=jnp.int32)),
    )

    return state


def snapshot_jit(state: BacterialStateGPU, cycle: int) -> Snapshot:
    """Capture metrics — works on GPU arrays."""
    alive = state.alive
    n_alive = int(jnp.sum(alive))

    if n_alive == 0:
        return Snapshot(cycle=cycle, n_total=0, n_dz=0, n_lz=0, n_extracted=0,
                       mean_affinity=0.0, max_affinity=0.0, median_affinity=0.0,
                       std_affinity=0.0, diversity=0.0, n_unique_clones=0,
                       top_clone_fraction=0.0)

    alive_affs = state.affinities[state.alive]
    alive_clones = state.clone_id[state.alive]

    # Clone diversity (Shannon entropy)
    unique, counts = jnp.unique(alive_clones, return_counts=True, size=min(n_alive, 10000))
    counts = counts[counts > 0]
    total = jnp.sum(counts)
    probs = counts / jnp.maximum(total, 1)
    entropy = -jnp.sum(probs * jnp.log(probs + 1e-10))
    top_clone_frac = float(jnp.max(counts) / jnp.maximum(total, 1))

    n_lz = int(jnp.sum(alive & state.in_lz))

    return Snapshot(
        cycle=cycle,
        n_total=n_alive,
        n_dz=n_alive - n_lz,
        n_lz=n_lz,
        n_extracted=0,
        mean_affinity=float(jnp.mean(alive_affs)),
        max_affinity=float(jnp.max(alive_affs)),
        median_affinity=float(jnp.median(alive_affs)),
        std_affinity=float(jnp.std(alive_affs)),
        diversity=float(entropy),
        n_unique_clones=int(counts.shape[0]),
        top_clone_fraction=top_clone_frac,
    )


def run_experiment_jit(config: BacterialConfig, seed: int = 42,
                       selection_mode: str = 'gc',
                       de_keep_fraction: float = 0.01,
                       gc_keep_fraction: float = 0.10) -> list:
    """Run a full experiment using JIT-compiled GPU kernels."""
    t0 = time.time()
    rng_key = jax.random.PRNGKey(seed)

    print(f"Initializing JIT state (L={config.shape_space_dim})...", flush=True)
    rng_key, init_key = jax.random.split(rng_key)
    state = initialize_jit(config, init_key)
    print(f"  Init took {time.time()-t0:.1f}s", flush=True)

    n_rounds = int(config.dz_growth_hours / config.doubling_time)
    history = [snapshot_jit(state, 0)]

    for cycle in range(1, config.n_cycles + 1):
        t_cycle = time.time()
        rng_key, k1, k2 = jax.random.split(rng_key, 3)

        # Growth phase (turbidostat with incremental Hamming JIT)
        (state_seqs, state_affs, state_hamming, state_alive, state_in_lz,
         state_divc, state_cid, state_gen) = turbidostat_growth_jit(
            state.sequences, state.affinities, state.hamming,
            state.alive, state.in_lz, state.div_counter,
            state.clone_id, state.generation, state.antigen, k1,
            config.mutation_rate, config.affinity_gamma,
            config.affinity_eta,
            config.shape_space_dim, config.turbidostat_target_n,
            config.dz_divisions, n_rounds,
        )

        state = state._replace(
            sequences=state_seqs, affinities=state_affs,
            hamming=state_hamming,
            alive=state_alive, in_lz=state_in_lz,
            div_counter=state_divc, clone_id=state_cid,
            generation=state_gen,
        )

        # Selection phase
        if selection_mode == 'directed_evolution':
            new_alive, new_in_lz, new_divc = apply_directed_evolution_jit(
                state.affinities, state.alive, state.div_counter,
                k2, de_keep_fraction,
            )
        elif selection_mode == 'top_fraction':
            new_alive, new_in_lz, new_divc = apply_top_fraction_jit(
                state.affinities, state.alive, state.in_lz, state.div_counter,
                k2, gc_keep_fraction,
                config.unselected_return_fraction,
            )
        else:
            new_alive, new_in_lz, new_divc = apply_selection_jit(
                state.affinities, state.alive, state.in_lz, state.div_counter,
                k2, config.hill_n, config.hill_k,
                config.unselected_return_fraction,
            )

        state = state._replace(alive=new_alive, in_lz=new_in_lz, div_counter=new_divc)

        # Snapshot
        snap = snapshot_jit(state, cycle)
        history.append(snap)

        elapsed = time.time() - t_cycle
        if cycle <= 3 or cycle % 10 == 0 or cycle == config.n_cycles:
            print(f"  Cycle {cycle}/{config.n_cycles}: N={snap.n_total} | "
                  f"mean_aff={snap.mean_affinity:.4f} max={snap.max_affinity:.4f} "
                  f"diversity={snap.diversity:.2f} ({elapsed:.1f}s)", flush=True)

    return history


def run_experiment_pipeline_jit(config: BacterialConfig, seed: int = 42,
                                gc_keep_fraction: float = 0.10,
                                sample_fraction: float = 0.50,
                                mini_cycle_doublings: int = 3,
                                total_mini_cycles: int = 560,
                                snapshot_interval: int = 4) -> list:
    """Pipeline model: continuous DZ-LZ cycling.

    Every mini_cycle_doublings doublings:
    1. Grow DZ cells for k rounds (turbidostat)
    2. Sample sample_fraction of DZ cells → LZ
    3. Competitive selection: keep top gc_keep_fraction of LZ
    4. Survivors return to DZ (div_counter reset)

    Snapshots taken every snapshot_interval mini-cycles.

    Args:
        config: BacterialConfig (growth/mutation params)
        seed: random seed
        gc_keep_fraction: fraction of LZ cells to keep (competitive)
        sample_fraction: fraction of DZ cells sampled to LZ each round
        mini_cycle_doublings: growth rounds per mini-cycle (e.g. 3 = 1.5h)
        total_mini_cycles: total number of pipeline cycles
        snapshot_interval: take a snapshot every N mini-cycles
    """
    t0 = time.time()
    rng_key = jax.random.PRNGKey(seed)

    print(f"Pipeline model: {mini_cycle_doublings} doublings/cycle, "
          f"sample={sample_fraction:.0%}, keep={gc_keep_fraction:.0%}, "
          f"{total_mini_cycles} cycles", flush=True)

    rng_key, init_key = jax.random.split(rng_key)
    state = initialize_jit(config, init_key)
    print(f"  Init took {time.time()-t0:.1f}s", flush=True)

    history = [snapshot_jit(state, 0)]

    for mc in range(1, total_mini_cycles + 1):
        t_cycle = time.time()
        rng_key, k1, k2, k3 = jax.random.split(rng_key, 4)

        # Step 1: Growth (no auto-migration)
        (state_seqs, state_affs, state_hamming, state_alive, state_in_lz,
         state_divc, state_cid, state_gen) = turbidostat_growth_no_migrate_jit(
            state.sequences, state.affinities, state.hamming,
            state.alive, state.in_lz, state.div_counter,
            state.clone_id, state.generation, state.antigen, k1,
            config.mutation_rate, config.affinity_gamma,
            config.affinity_eta,
            config.shape_space_dim, config.turbidostat_target_n,
            mini_cycle_doublings,
        )

        state = state._replace(
            sequences=state_seqs, affinities=state_affs,
            hamming=state_hamming,
            alive=state_alive, in_lz=state_in_lz,
            div_counter=state_divc, clone_id=state_cid,
            generation=state_gen,
        )

        # Step 2: Sample fraction of DZ → LZ
        new_in_lz = sample_to_lz_jit(state.alive, state.in_lz, k2, sample_fraction)
        state = state._replace(in_lz=new_in_lz)

        # Step 3: Competitive selection on LZ cells
        new_alive, new_in_lz, new_divc = apply_top_fraction_jit(
            state.affinities, state.alive, state.in_lz, state.div_counter,
            k3, gc_keep_fraction,
            config.unselected_return_fraction,
        )
        state = state._replace(alive=new_alive, in_lz=new_in_lz, div_counter=new_divc)

        # Snapshot at intervals
        if mc % snapshot_interval == 0 or mc == total_mini_cycles:
            snap = snapshot_jit(state, mc)
            history.append(snap)

            elapsed = time.time() - t_cycle
            if mc <= snapshot_interval * 3 or mc % (snapshot_interval * 10) == 0 or mc == total_mini_cycles:
                print(f"  Mini-cycle {mc}/{total_mini_cycles}: N={snap.n_total} | "
                      f"mean_aff={snap.mean_affinity:.4f} max={snap.max_affinity:.4f} "
                      f"diversity={snap.diversity:.2f} ({elapsed:.1f}s)", flush=True)

    return history
