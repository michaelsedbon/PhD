"""
Bacterial growth — turbidostat-style with per-cell division tracking.

Models the actual experimental protocol:
- Bacteria grow continuously, diluted every ~30 min to constant density
- Each cell tracks divisions_since_last_selection
- After N divisions, cells auto-migrate to LZ for selection
- Mutation occurs at each division

The turbidostat is simulated as discrete rounds of:
  1. Double the population (with mutation)
  2. Dilute back to target density (random subset dies)
  3. Check which cells have completed enough divisions → move to LZ
"""

import jax
import jax.numpy as jnp
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from germinal_center.affinity import mutate_sequence, batch_affinity


def grow_one_doubling(
    sequences: jnp.ndarray,
    affinities: jnp.ndarray,
    clone_ids: jnp.ndarray,
    generations: jnp.ndarray,
    div_counters: jnp.ndarray,
    cell_ids: jnp.ndarray,
    parent_ids: jnp.ndarray,
    next_id: int,
    antigen: jnp.ndarray,
    mutation_rate: float,
    gamma: float,
    eta: float,
    rng_key: jnp.ndarray,
) -> tuple:
    """One round of division: each cell divides once.

    - Every cell produces one daughter (population doubles)
    - Daughters inherit parent's sequence with possible mutation
    - Division counter increments for both parent and daughter
    - Daughters get new unique cell_ids and record parent's cell_id

    Returns: (seqs, affs, clones, gens, div_counters, cell_ids, parent_ids, next_id)
    """
    N = sequences.shape[0]
    L = sequences.shape[1]
    k1, k2 = jax.random.split(rng_key)

    # Daughters start as copies of parents
    daughter_seqs = sequences.copy()
    daughter_clones = clone_ids.copy()
    daughter_gens = generations + 1
    daughter_divs = div_counters + 1  # both parent and daughter increment

    # Lineage: daughters get new IDs, record parent's ID
    daughter_ids = jnp.arange(next_id, next_id + N, dtype=jnp.int32)
    daughter_parent_ids = cell_ids  # parent of each daughter is the current cell
    new_next_id = next_id + N

    # Apply mutations to daughters
    per_cell_mut_prob = mutation_rate * L
    should_mutate = jax.random.uniform(k1, (N,)) < per_cell_mut_prob
    mut_keys = jax.random.split(k2, N)

    def _maybe_mutate(seq, key, do_mutate):
        mutated = mutate_sequence(seq, key, 10, L)
        return jnp.where(do_mutate, mutated, seq)

    daughter_seqs = jax.vmap(_maybe_mutate)(daughter_seqs, mut_keys, should_mutate)

    # Recompute affinities for mutated daughters
    daughter_affs = batch_affinity(daughter_seqs, antigen, gamma, eta)

    # Parent division counters also increment
    parent_divs = div_counters + 1

    # Concatenate parent + daughter
    all_seqs = jnp.concatenate([sequences, daughter_seqs])
    all_affs = jnp.concatenate([affinities, daughter_affs])
    all_clones = jnp.concatenate([clone_ids, daughter_clones])
    all_gens = jnp.concatenate([generations, daughter_gens])
    all_divs = jnp.concatenate([parent_divs, daughter_divs])
    all_cell_ids = jnp.concatenate([cell_ids, daughter_ids])
    all_parent_ids = jnp.concatenate([parent_ids, daughter_parent_ids])

    return all_seqs, all_affs, all_clones, all_gens, all_divs, all_cell_ids, all_parent_ids, new_next_id


def dilute_to_target(
    sequences, affinities, clone_ids, generations, div_counters,
    cell_ids, parent_ids,
    target_n: int,
    rng_key: jnp.ndarray,
) -> tuple:
    """Random dilution to target population size (turbidostat)."""
    N = sequences.shape[0]
    if N <= target_n:
        return sequences, affinities, clone_ids, generations, div_counters, cell_ids, parent_ids

    keep_idx = jax.random.choice(rng_key, N, shape=(target_n,), replace=False)
    return (
        sequences[keep_idx],
        affinities[keep_idx],
        clone_ids[keep_idx],
        generations[keep_idx],
        div_counters[keep_idx],
        cell_ids[keep_idx],
        parent_ids[keep_idx],
    )


def turbidostat_growth(
    sequences, affinities, clone_ids, generations, div_counters,
    cell_ids, parent_ids, next_id,
    antigen, config, rng_key,
):
    """Run turbidostat growth for config.dz_growth_hours.

    Each round (one doubling time):
    1. Every cell divides (population doubles, mutations applied)
    2. Dilute back to target_n

    Cells track their division count. After config.dz_divisions
    divisions, they are flagged for migration to LZ.

    Returns: (seqs, affs, clones, gens, div_counters, cell_ids, parent_ids, next_id, ready_for_lz_mask)
    """
    n_rounds = int(config.dz_growth_hours / config.doubling_time)

    seqs = sequences
    affs = affinities
    clones = clone_ids
    gens = generations
    divs = div_counters
    cids = cell_ids
    pids = parent_ids
    nid = next_id

    for i in range(n_rounds):
        rng_key, k_div, k_dil = jax.random.split(rng_key, 3)

        # Divide
        seqs, affs, clones, gens, divs, cids, pids, nid = grow_one_doubling(
            seqs, affs, clones, gens, divs, cids, pids, nid,
            antigen, config.mutation_rate,
            config.affinity_gamma, config.affinity_eta, k_div,
        )

        # Dilute (turbidostat)
        seqs, affs, clones, gens, divs, cids, pids = dilute_to_target(
            seqs, affs, clones, gens, divs, cids, pids,
            config.turbidostat_target_n, k_dil,
        )

    # Identify cells ready for LZ (enough divisions since last selection)
    ready_for_lz = divs >= config.dz_divisions

    return seqs, affs, clones, gens, divs, cids, pids, nid, ready_for_lz
