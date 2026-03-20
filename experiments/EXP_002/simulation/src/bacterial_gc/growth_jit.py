"""
JIT-compiled growth for Bacterial GC — memory-optimized with incremental Hamming.

Key optimization: mutations are applied as single-point writes with incremental
Hamming distance updates. This avoids creating 3 × N_MAX × L intermediate arrays
(one_hot, delta, daughter_seqs), reducing GPU memory from ~14 GB to ~5 GB at N=10M.

Strategy for division:
  - Use cumsum-based slot assignment for daughters
  - Mutations: single .at[slot, pos].add(dir) per daughter
  - Affinity: exp(-γ(h/L)²) updated via delta_h = ±1, no sequence recomputation
"""

import jax
import jax.numpy as jnp
from functools import partial


@partial(jax.jit, static_argnums=(11, 12, 13))
def grow_one_doubling_jit(
    sequences,    # int32[N_MAX, L]
    affinities,   # float32[N_MAX]
    hamming,      # float32[N_MAX] — current Hamming distance to antigen
    alive,        # bool[N_MAX]
    in_lz,        # bool[N_MAX]
    div_counter,  # int32[N_MAX]
    clone_id,     # int32[N_MAX]
    generation,   # int32[N_MAX]
    antigen,      # int32[L]
    rng_key,
    mutation_rate, # float (traced, not static)
    gamma,         # static float — Gaussian width Γ
    eta,           # static float — Gaussian exponent η
    L,             # static int
):
    """One round of division — incremental Hamming, minimal memory.

    Instead of creating full N×L intermediate arrays for mutations,
    this version:
    1. Copies parent sequences to daughter slots (scatter)
    2. Applies ONE point mutation per daughter (single position write)
    3. Updates Hamming distance incrementally (±1 per mutation)
    4. Computes affinity from Hamming without touching sequences again
    """
    N_MAX = sequences.shape[0]
    k1, k2, k3 = jax.random.split(rng_key, 3)

    # Which cells can divide: alive AND in DZ (not LZ)
    can_divide = alive & ~in_lz

    # Find free (dead) slots using argsort — dead slots sort first
    # This is JIT-compatible because argsort returns a fixed-size array
    free_priority = alive.astype(jnp.int32)  # 0=dead (first), 1=alive (last)
    free_slots = jnp.argsort(free_priority)  # dead slots at the front

    # For each dividing cell, assign it the next free slot via cumsum
    # cumsum gives each dividing cell a unique index 0..n_dividing-1
    daughter_offset = jnp.cumsum(can_divide.astype(jnp.int32)) - 1  # 0-indexed
    # Map to actual free slot: free_slots[daughter_offset[i]]
    daughter_slot = free_slots[daughter_offset]
    daughter_slot = jnp.clip(daughter_slot, 0, N_MAX - 1)

    # == Step 1: Copy parent data to daughter slots ==
    # Use scatter: for each i where can_divide[i], copy to daughter_slot[i]

    # Copy parent sequences to daughters
    # This IS an N_MAX × L operation but it's a gather+scatter, not an arithmetic temp
    new_sequences = sequences.at[daughter_slot].set(
        jnp.where(can_divide[:, None], sequences, sequences[daughter_slot])
    )

    # Copy Hamming distances (scalar per cell — tiny)
    new_hamming = hamming.at[daughter_slot].set(
        jnp.where(can_divide, hamming, hamming[daughter_slot])
    )

    # == Step 2: Apply point mutations to daughters ==
    # Each daughter gets 0 or 1 mutation (single position)
    per_cell_mut_prob = mutation_rate * L
    should_mutate = jax.random.uniform(k1, (N_MAX,)) < per_cell_mut_prob
    mut_pos = jax.random.randint(k2, (N_MAX,), 0, L)
    mut_dir = jax.random.choice(k3, jnp.array([-1, 1], dtype=jnp.int8), (N_MAX,))

    # Only mutate daughters of dividing cells
    actually_mutate = should_mutate & can_divide

    # Get the current value at mutation position for each cell
    # old_val = sequences[i, mut_pos[i]] — need to gather
    cell_indices = jnp.arange(N_MAX)
    old_val = new_sequences[cell_indices, mut_pos]  # gather from daughter seqs
    old_val_at_daughter = new_sequences[daughter_slot, mut_pos]

    # Compute new value after mutation
    new_val = old_val_at_daughter + mut_dir

    # Was the old value a mismatch with antigen?
    antigen_val = antigen[mut_pos]
    was_mismatch = (old_val_at_daughter != antigen_val).astype(jnp.float32)
    now_mismatch = (new_val != antigen_val).astype(jnp.float32)
    delta_h = now_mismatch - was_mismatch  # -1, 0, or +1

    # Apply mutation to sequence: only at daughter_slot[i], position mut_pos[i]
    # We need a vectorized scatter: seq[daughter_slot[i], mut_pos[i]] += mut_dir[i]
    # Use .at with both indices
    mutation_delta = jnp.where(actually_mutate, mut_dir, jnp.int8(0))
    new_sequences = new_sequences.at[daughter_slot, mut_pos].add(mutation_delta)

    # Update Hamming incrementally
    hamming_delta = jnp.where(actually_mutate, delta_h, 0.0)
    new_hamming = new_hamming.at[daughter_slot].add(hamming_delta)

    # == Step 3: Compute daughter affinities from Hamming ==
    # Only for daughter slots — use the updated Hamming
    daughter_hamming = new_hamming[daughter_slot]
    daughter_affs = jnp.exp(-((daughter_hamming / gamma) ** eta))
    new_affinities = affinities.at[daughter_slot].set(
        jnp.where(can_divide, daughter_affs, affinities[daughter_slot])
    )

    # == Step 4: Metadata ==
    new_clone_id = clone_id.at[daughter_slot].set(
        jnp.where(can_divide, clone_id, clone_id[daughter_slot])
    )
    new_generation = generation.at[daughter_slot].set(
        jnp.where(can_divide, generation + 1, generation[daughter_slot])
    )
    new_alive = alive.at[daughter_slot].set(
        jnp.where(can_divide, True, alive[daughter_slot])
    )
    new_in_lz = in_lz.at[daughter_slot].set(
        jnp.where(can_divide, False, in_lz[daughter_slot])
    )

    # Increment div_counter for parents that divide
    new_div_counter = jnp.where(can_divide, div_counter + 1, div_counter)
    new_div_counter = new_div_counter.at[daughter_slot].set(
        jnp.where(can_divide, new_div_counter, new_div_counter[daughter_slot])
    )

    return (new_sequences, new_affinities, new_hamming, new_alive, new_in_lz,
            new_div_counter, new_clone_id, new_generation)


@partial(jax.jit, static_argnums=(3,))
def dilute_to_target_jit(alive, affinities, rng_key, target_n):
    """Kill random alive cells until target_n remain. JIT-compiled.

    Uses Bernoulli sampling: each alive cell kept with P = target_n / n_alive.
    """
    n_alive = jnp.sum(alive).astype(jnp.float32)
    target = jnp.float32(target_n)

    keep_prob = jnp.minimum(target / jnp.maximum(n_alive, 1.0), 1.0)
    rolls = jax.random.uniform(rng_key, alive.shape)
    keep = (rolls < keep_prob) & alive

    return keep


def turbidostat_growth_jit(
    sequences, affinities, hamming, alive, in_lz, div_counter,
    clone_id, generation, antigen, rng_key,
    mutation_rate, gamma, eta, L, target_n, dz_divisions, n_rounds,
):
    """Run turbidostat growth for n_rounds.

    Uses Python for-loop with per-step JIT calls.
    """
    for i in range(n_rounds):
        rng_key, k_div, k_dil = jax.random.split(rng_key, 3)

        (sequences, affinities, hamming, alive, in_lz,
         div_counter, clone_id, generation) = grow_one_doubling_jit(
            sequences, affinities, hamming, alive, in_lz, div_counter,
            clone_id, generation, antigen, k_div,
            mutation_rate, gamma, eta, L,
        )

        alive = dilute_to_target_jit(alive, affinities, k_dil, target_n)

    # Mark cells ready for LZ migration
    ready_mask = div_counter >= dz_divisions
    new_in_lz = alive & ready_mask

    return (sequences, affinities, hamming, alive, new_in_lz,
            div_counter, clone_id, generation)


def turbidostat_growth_no_migrate_jit(
    sequences, affinities, hamming, alive, in_lz, div_counter,
    clone_id, generation, antigen, rng_key,
    mutation_rate, gamma, eta, L, target_n, n_rounds,
):
    """Run turbidostat growth for n_rounds WITHOUT auto-LZ migration.

    Used by the pipeline model where LZ migration is done by random sampling,
    not by div_counter threshold.
    """
    for i in range(n_rounds):
        rng_key, k_div, k_dil = jax.random.split(rng_key, 3)

        (sequences, affinities, hamming, alive, in_lz,
         div_counter, clone_id, generation) = grow_one_doubling_jit(
            sequences, affinities, hamming, alive, in_lz, div_counter,
            clone_id, generation, antigen, k_div,
            mutation_rate, gamma, eta, L,
        )

        alive = dilute_to_target_jit(alive, affinities, k_dil, target_n)

    # NO LZ migration here — pipeline model handles it separately
    return (sequences, affinities, hamming, alive, in_lz,
            div_counter, clone_id, generation)


@partial(jax.jit, static_argnums=(3,))
def sample_to_lz_jit(alive, in_lz, rng_key, sample_fraction):
    """Randomly sample a fraction of DZ cells → move to LZ.

    Only DZ cells (alive & not in_lz) are eligible for sampling.
    Models the robot taking n% of the DZ well for selection.
    """
    is_dz = alive & ~in_lz
    rolls = jax.random.uniform(rng_key, alive.shape)
    sampled = is_dz & (rolls < sample_fraction)
    new_in_lz = in_lz | sampled
    return new_in_lz
