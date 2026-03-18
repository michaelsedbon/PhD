"""
GPU-optimized simulation loop for Bacterial GC.

Orchestrates growth → migration → selection → recycling.
Each sub-step is JIT-compiled. The outer loop runs in Python.
"""

import jax
import jax.numpy as jnp
import time

from .config import BacterialConfig
from .state_gpu import BacterialStateGPU, empty_state, count_alive, count_in_lz
from .growth_gpu import turbidostat_growth
from .selection_gpu import apply_selection_gpu, apply_directed_evolution
from .analysis import Snapshot  # reuse CPU snapshot type

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from germinal_center.affinity import create_founders_at_distance, batch_affinity


def initialize_gpu(config: BacterialConfig, rng_key: jnp.ndarray) -> BacterialStateGPU:
    """Create initial population in padded GPU arrays."""
    k1, k2 = jax.random.split(rng_key)

    L = config.shape_space_dim
    antigen = jnp.zeros(L, dtype=jnp.int32)
    N = config.n_founders

    # Compute N_MAX based on target population + headroom for doubling
    n_rounds = int(config.dz_growth_hours / config.doubling_time)
    # Population never exceeds 2*target_n (divide then immediately dilute).
    # Need headroom for the division step before dilution.
    n_max = config.turbidostat_target_n * 2
    n_max = min(n_max, 2_000_000)  # cap at 2M to fit GPU (11 GB VRAM)

    state = empty_state(L=L, n_max=n_max)

    # Create founder sequences
    founder_seqs = create_founders_at_distance(
        N, antigen, config.initial_hamming_min, config.initial_hamming_max, k1,
    )
    founder_affs = batch_affinity(founder_seqs, antigen,
                                  config.affinity_gamma, config.affinity_eta)

    # Write founders into first N slots
    new_seqs = state.sequences.at[:N].set(founder_seqs)
    new_affs = state.affinities.at[:N].set(founder_affs)
    new_clone_id = state.clone_id.at[:N].set(jnp.arange(N, dtype=jnp.int32))
    new_cell_id = state.cell_id.at[:N].set(jnp.arange(N, dtype=jnp.int32))
    new_parent_id = state.parent_id.at[:N].set(jnp.full(N, -1, dtype=jnp.int32))
    new_alive = state.alive.at[:N].set(True)

    return state._replace(
        sequences=new_seqs,
        affinities=new_affs,
        clone_id=new_clone_id,
        cell_id=new_cell_id,
        parent_id=new_parent_id,
        alive=new_alive,
        antigen=antigen,
        next_id=jnp.array([N], dtype=jnp.int32),
        cycle=jnp.array([0], dtype=jnp.int32),
    )


def snapshot_gpu(state: BacterialStateGPU) -> Snapshot:
    """Capture metrics from GPU state (same format as CPU snapshots)."""
    alive = state.alive
    n_total = int(jnp.sum(alive))

    if n_total == 0:
        return Snapshot(
            cycle=int(state.cycle[0]),
            n_total=0, n_dz=0, n_lz=0, n_extracted=0,
            mean_affinity=0.0, max_affinity=0.0,
            median_affinity=0.0, std_affinity=0.0,
            diversity=0.0, n_unique_clones=0, top_clone_fraction=0.0,
        )

    affs = state.affinities[alive]
    clones = state.clone_id[alive]
    n_lz = int(jnp.sum(state.in_lz & alive))

    # Diversity: Shannon entropy over clone IDs
    _, counts = jnp.unique(clones, return_counts=True, size=n_total)
    counts = counts[counts > 0]
    freqs = counts / jnp.sum(counts)
    entropy = -jnp.sum(freqs * jnp.log2(jnp.maximum(freqs, 1e-10)))

    n_unique = int(jnp.sum(counts > 0))
    top_frac = float(jnp.max(counts) / jnp.sum(counts))

    return Snapshot(
        cycle=int(state.cycle[0]),
        n_total=n_total,
        n_dz=n_total - n_lz,
        n_lz=n_lz,
        n_extracted=0,
        mean_affinity=float(jnp.mean(affs)),
        max_affinity=float(jnp.max(affs)),
        median_affinity=float(jnp.median(affs)),
        std_affinity=float(jnp.std(affs)),
        diversity=float(entropy),
        n_unique_clones=n_unique,
        top_clone_fraction=top_frac,
    )


def run_cycle_gpu(
    state: BacterialStateGPU,
    config: BacterialConfig,
    cycle: int,
    rng_key: jnp.ndarray,
    selection_mode: str = 'gc',
    de_keep_fraction: float = 0.01,
) -> BacterialStateGPU:
    """One cycle: grow → select.

    Args:
        selection_mode: 'gc' (Hill + unselected return) or 'directed_evolution' (top-K).
        de_keep_fraction: For directed_evolution mode, fraction of cells to keep.
    """
    k1, k2 = jax.random.split(rng_key)

    n_rounds = int(config.dz_growth_hours / config.doubling_time)

    # Step 1: Turbidostat growth (division + dilution, n_rounds times)
    state = turbidostat_growth(
        state, n_rounds,
        config.mutation_rate, config.affinity_gamma, config.affinity_eta,
        config.shape_space_dim, config.turbidostat_target_n,
        config.dz_divisions, k1,
    )

    # Step 2: Selection
    if selection_mode == 'directed_evolution':
        state = apply_directed_evolution(state, k2, de_keep_fraction)
    else:
        state = apply_selection_gpu(
            state, k2,
            config.hill_n, config.hill_k,
            config.unselected_return_fraction,
        )

    # Update cycle counter
    state = state._replace(cycle=jnp.array([cycle], dtype=jnp.int32))

    return state


def run_experiment_gpu(config: BacterialConfig, seed: int = 42,
                       selection_mode: str = 'gc',
                       de_keep_fraction: float = 0.01) -> list:
    """Run the full bacterial GC experiment on GPU."""
    key = jax.random.PRNGKey(seed)

    print(f"Initializing GPU state (L={config.shape_space_dim})...", flush=True)
    t0 = time.time()
    state = initialize_gpu(config, key)
    n_max = state.alive.shape[0]
    print(f"  N_MAX={n_max:,}, init took {time.time()-t0:.1f}s", flush=True)

    # Memory estimate
    mem_gb = (n_max * config.shape_space_dim * 4 +  # sequences
              n_max * 4 * 6 +  # affinities, clone_id, gen, cell_id, parent_id, div_counter
              n_max * 2) / 1e9  # alive, in_lz
    print(f"  Estimated memory: {mem_gb:.2f} GB", flush=True)

    history = [snapshot_gpu(state)]

    for cycle in range(config.n_cycles):
        key, cycle_key = jax.random.split(key)

        t_cycle = time.time()
        state = run_cycle_gpu(state, config, cycle + 1, cycle_key,
                              selection_mode=selection_mode,
                              de_keep_fraction=de_keep_fraction)
        dt = time.time() - t_cycle

        snap = snapshot_gpu(state)
        history.append(snap)

        n_alive = count_alive(state)
        print(f"  Cycle {cycle+1}/{config.n_cycles}: "
              f"N={n_alive} | "
              f"mean_aff={snap.mean_affinity:.4f} "
              f"max={snap.max_affinity:.4f} "
              f"diversity={snap.diversity:.2f} "
              f"({dt:.1f}s)", flush=True)

        if n_alive == 0:
            print("  Population extinct!")
            break

    return history
