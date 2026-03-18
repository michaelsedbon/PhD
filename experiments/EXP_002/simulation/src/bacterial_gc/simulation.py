"""
Main simulation loop for the Bacterial Synthetic GC.

Redesigned to match the actual experimental protocol:
- Turbidostat growth with per-cell division counters
- Division-triggered migration to LZ (not random transfers)
- Selection in LZ
- Survivors + optional unselected fraction return to DZ
- Division counters reset for recycled cells

Each cycle:
1. Grow in DZ (turbidostat: divide + dilute, tracking division count)
2. Cells with enough divisions auto-migrate to LZ
3. Selection applied in LZ
4. Survivors return to DZ with reset counters
5. Optional: fraction of unselected also return (diversity maintenance)
"""

import jax
import jax.numpy as jnp

from .config import BacterialConfig
from .state import BacterialState, DZ, LZ, EXTRACTED, count_bacteria
from .growth import turbidostat_growth
from .selection import apply_selection
from .analysis import snapshot

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from germinal_center.affinity import create_founders_at_distance, batch_affinity


def initialize(config: BacterialConfig, rng_key: jnp.ndarray) -> BacterialState:
    """Create initial bacterial population in DZ."""
    k1, k2 = jax.random.split(rng_key)

    L = config.shape_space_dim
    antigen = jnp.zeros(L, dtype=jnp.int32)

    sequences = create_founders_at_distance(
        config.n_founders, antigen,
        config.initial_hamming_min, config.initial_hamming_max, k1,
    )
    affinities = batch_affinity(
        sequences, antigen, config.affinity_gamma, config.affinity_eta,
    )

    return BacterialState(
        sequences=sequences,
        affinities=affinities,
        compartment=jnp.full(config.n_founders, DZ, dtype=jnp.int8),
        clone_id=jnp.arange(config.n_founders, dtype=jnp.int32),
        generation=jnp.zeros(config.n_founders, dtype=jnp.int32),
        alive=jnp.ones(config.n_founders, dtype=jnp.bool_),
        antigen=antigen,
        cycle=0,
        cell_id=jnp.arange(config.n_founders, dtype=jnp.int32),
        parent_id=jnp.full(config.n_founders, -1, dtype=jnp.int32),
        next_id=config.n_founders,
    )


def run_cycle(
    state: BacterialState,
    config: BacterialConfig,
    cycle: int,
    rng_key: jnp.ndarray,
) -> BacterialState:
    """Execute one GC cycle matching the experimental protocol.

    1. Turbidostat growth in DZ (with per-cell division tracking)
    2. Cells with enough divisions → automatically migrate to LZ
    3. Selection in LZ (bead binding / Hill / etc.)
    4. Survivors return to DZ with reset division counter
    5. Optional: fraction of unselected also returns
    """
    k1, k2, k3 = jax.random.split(rng_key, 3)

    # Get current DZ population
    dz_mask = state.alive & (state.compartment == DZ)
    dz_idx = jnp.where(dz_mask)[0]

    if dz_idx.shape[0] == 0:
        return state._replace(cycle=cycle)

    # ── STEP 1: Turbidostat growth ──
    dz_seqs = state.sequences[dz_idx]
    dz_affs = state.affinities[dz_idx]
    dz_clones = state.clone_id[dz_idx]
    dz_gens = state.generation[dz_idx]
    dz_cell_ids = state.cell_id[dz_idx]
    dz_parent_ids = state.parent_id[dz_idx]
    # Division counters: use generation as a proxy if not stored separately
    # We'll track div_since_selection via generation modulo
    div_counters = jnp.zeros(dz_idx.shape[0], dtype=jnp.int32)

    (grown_seqs, grown_affs, grown_clones, grown_gens,
     grown_divs, grown_cell_ids, grown_parent_ids, new_next_id, ready_for_lz) = turbidostat_growth(
        dz_seqs, dz_affs, dz_clones, dz_gens, div_counters,
        dz_cell_ids, dz_parent_ids, state.next_id,
        state.antigen, config, k1,
    )

    n_grown = grown_seqs.shape[0]

    # ── STEP 2: Split into DZ-stay and LZ-migrate ──
    lz_idx = jnp.where(ready_for_lz)[0]
    dz_stay_idx = jnp.where(~ready_for_lz)[0]

    n_to_lz = lz_idx.shape[0]
    n_stay_dz = dz_stay_idx.shape[0]

    if n_to_lz == 0:
        # No cells ready for LZ yet
        return BacterialState(
            sequences=grown_seqs,
            affinities=grown_affs,
            compartment=jnp.full(n_grown, DZ, dtype=jnp.int8),
            clone_id=grown_clones,
            generation=grown_gens,
            alive=jnp.ones(n_grown, dtype=jnp.bool_),
            antigen=state.antigen,
            cycle=cycle,
            cell_id=grown_cell_ids,
            parent_id=grown_parent_ids,
            next_id=new_next_id,
        )

    # Cells going to LZ
    lz_seqs = grown_seqs[lz_idx]
    lz_affs = grown_affs[lz_idx]
    lz_clones = grown_clones[lz_idx]
    lz_gens = grown_gens[lz_idx]
    lz_cell_ids = grown_cell_ids[lz_idx]
    lz_parent_ids = grown_parent_ids[lz_idx]

    # Cells staying in DZ
    dz_seqs_stay = grown_seqs[dz_stay_idx]
    dz_affs_stay = grown_affs[dz_stay_idx]
    dz_clones_stay = grown_clones[dz_stay_idx]
    dz_gens_stay = grown_gens[dz_stay_idx]
    dz_cell_ids_stay = grown_cell_ids[dz_stay_idx]
    dz_parent_ids_stay = grown_parent_ids[dz_stay_idx]

    # ── STEP 3: Selection in LZ ──
    # Create temporary state for LZ cells
    lz_alive = jnp.ones(n_to_lz, dtype=jnp.bool_)
    lz_state = BacterialState(
        sequences=lz_seqs,
        affinities=lz_affs,
        compartment=jnp.full(n_to_lz, LZ, dtype=jnp.int8),
        clone_id=lz_clones,
        generation=lz_gens,
        alive=lz_alive,
        antigen=state.antigen,
        cycle=cycle,
    )

    lz_state = apply_selection(lz_state, config, k2)

    # ── STEP 4: Survivors return to DZ ──
    survivors = lz_state.alive
    n_survived = int(jnp.sum(survivors))

    survivor_idx = jnp.where(survivors)[0]
    surv_seqs = lz_state.sequences[survivor_idx]
    surv_affs = lz_state.affinities[survivor_idx]
    surv_clones = lz_state.clone_id[survivor_idx]
    surv_gens = lz_state.generation[survivor_idx]
    surv_cell_ids = lz_cell_ids[survivor_idx]
    surv_parent_ids = lz_parent_ids[survivor_idx]

    # ── STEP 5: Optional — fraction of unselected also return ──
    dead_idx = jnp.where(~survivors)[0]
    n_dead = dead_idx.shape[0]
    n_unselected_return = int(n_dead * config.unselected_return_fraction)

    if n_unselected_return > 0 and n_dead > 0:
        chosen = jax.random.choice(k3, dead_idx, shape=(n_unselected_return,), replace=False)
        unsel_seqs = lz_state.sequences[chosen]
        unsel_affs = lz_state.affinities[chosen]
        unsel_clones = lz_state.clone_id[chosen]
        unsel_gens = lz_state.generation[chosen]
        unsel_cell_ids = lz_cell_ids[chosen]
        unsel_parent_ids = lz_parent_ids[chosen]

        # Combine survivors + unselected returns + DZ-stay
        all_seqs = jnp.concatenate([dz_seqs_stay, surv_seqs, unsel_seqs])
        all_affs = jnp.concatenate([dz_affs_stay, surv_affs, unsel_affs])
        all_clones = jnp.concatenate([dz_clones_stay, surv_clones, unsel_clones])
        all_gens = jnp.concatenate([dz_gens_stay, surv_gens, unsel_gens])
        all_cell_ids = jnp.concatenate([dz_cell_ids_stay, surv_cell_ids, unsel_cell_ids])
        all_parent_ids = jnp.concatenate([dz_parent_ids_stay, surv_parent_ids, unsel_parent_ids])
    else:
        # Combine survivors + DZ-stay
        all_seqs = jnp.concatenate([dz_seqs_stay, surv_seqs])
        all_affs = jnp.concatenate([dz_affs_stay, surv_affs])
        all_clones = jnp.concatenate([dz_clones_stay, surv_clones])
        all_gens = jnp.concatenate([dz_gens_stay, surv_gens])
        all_cell_ids = jnp.concatenate([dz_cell_ids_stay, surv_cell_ids])
        all_parent_ids = jnp.concatenate([dz_parent_ids_stay, surv_parent_ids])

    n_total = all_seqs.shape[0]

    return BacterialState(
        sequences=all_seqs,
        affinities=all_affs,
        compartment=jnp.full(n_total, DZ, dtype=jnp.int8),
        clone_id=all_clones,
        generation=all_gens,
        alive=jnp.ones(n_total, dtype=jnp.bool_),
        antigen=state.antigen,
        cycle=cycle,
        cell_id=all_cell_ids,
        parent_id=all_parent_ids,
        next_id=new_next_id,
    )


def run_experiment(config: BacterialConfig, seed: int = 42) -> list:
    """Run the full bacterial GC experiment."""
    key = jax.random.PRNGKey(seed)
    state = initialize(config, key)
    history = [snapshot(state)]

    for cycle in range(config.n_cycles):
        key, cycle_key = jax.random.split(key)
        state = run_cycle(state, config, cycle + 1, cycle_key)
        snap = snapshot(state)
        history.append(snap)

        c = count_bacteria(state)
        print(f"  Cycle {cycle+1}/{config.n_cycles}: "
              f"N={c['n_total']} | "
              f"mean_aff={snap.mean_affinity:.4f} "
              f"max={snap.max_affinity:.4f} "
              f"diversity={snap.diversity:.2f}")

    return history
