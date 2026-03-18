"""
GPU-optimized bacterial growth — turbidostat with padded arrays.

HYBRID CPU/GPU STRATEGY:
- All arrays (sequences, metadata) live on CPU (unlimited RAM)
- Affinity computation sent to GPU in chunks of CHUNK_SIZE
- This allows N=10^6+ at L=400 on an 11 GB GPU

The GPU handles only the compute-heavy part (Hamming distance + exp),
while CPU handles indexing, scatter, and bookkeeping.
"""

import jax
import jax.numpy as jnp
import numpy as np
from functools import partial
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from germinal_center.affinity import batch_affinity

from .state_gpu import BacterialStateGPU

# Chunk size for GPU affinity computation.
# At L=400: 200K × 400 × 4 bytes = 320 MB per chunk → GPU-safe
CHUNK_SIZE = 200_000


def batch_affinity_chunked(
    bcrs: jnp.ndarray,
    antigen: jnp.ndarray,
    gamma: float,
    eta: float,
    chunk_size: int = CHUNK_SIZE,
) -> jnp.ndarray:
    """Compute affinity in GPU-safe chunks.

    Explicitly transfers chunks to GPU, computes, transfers back to CPU.
    This allows arbitrarily large populations on a small GPU.
    """
    N = bcrs.shape[0]
    cpu = jax.devices('cpu')[0]

    # Try to use GPU if available, fall back to CPU
    try:
        gpu = jax.devices('gpu')[0]
    except RuntimeError:
        gpu = cpu

    if N <= chunk_size:
        chunk_gpu = jax.device_put(bcrs, gpu)
        antigen_gpu = jax.device_put(antigen, gpu)
        result = batch_affinity(chunk_gpu, antigen_gpu, gamma, eta)
        return jax.device_put(result, cpu)

    antigen_gpu = jax.device_put(antigen, gpu)
    chunks = []
    for i in range(0, N, chunk_size):
        end = min(i + chunk_size, N)
        chunk_gpu = jax.device_put(bcrs[i:end], gpu)
        aff_chunk = batch_affinity(chunk_gpu, antigen_gpu, gamma, eta)
        chunks.append(jax.device_put(aff_chunk, cpu))

    return jnp.concatenate(chunks)


def _apply_mutations(
    sequences: jnp.ndarray,
    should_mutate: jnp.ndarray,
    mut_dims: jnp.ndarray,
    mut_dirs: jnp.ndarray,
) -> jnp.ndarray:
    """Apply point mutations via scatter-add."""
    N = sequences.shape[0]
    cell_idx = jnp.arange(N)
    delta = jnp.zeros_like(sequences)
    delta = delta.at[cell_idx, mut_dims].add(
        jnp.where(should_mutate, mut_dirs, 0)
    )
    return sequences + delta


def grow_one_doubling(
    state: BacterialStateGPU,
    rng_key: jnp.ndarray,
    mutation_rate: float,
    gamma: float,
    eta: float,
    L: int,
) -> BacterialStateGPU:
    """One round of cell division — every alive DZ cell produces one daughter.

    Uses CPU for bookkeeping, GPU for affinity computation via chunking.
    """
    k1, k2, k3 = jax.random.split(rng_key, 3)

    alive = state.alive & ~state.in_lz  # only DZ cells divide
    alive_idx = jnp.where(alive)[0]
    n_alive = alive_idx.shape[0]

    if n_alive == 0:
        return state

    # Find free slots for daughters
    dead_idx = jnp.where(~state.alive)[0]
    n_free = dead_idx.shape[0]
    n_daughters = min(n_alive, n_free)

    if n_daughters == 0:
        return state

    # Parent indices and daughter slots
    parent_idx = alive_idx[:n_daughters]
    daughter_slots = dead_idx[:n_daughters]

    # Copy parent sequences to daughters
    parent_seqs = state.sequences[parent_idx]

    # Apply mutations to daughters
    per_cell_mut_prob = mutation_rate * L
    should_mutate = jax.random.uniform(k1, (n_daughters,)) < per_cell_mut_prob
    mut_dims = jax.random.randint(k2, (n_daughters,), 0, L)
    mut_dirs = jax.random.choice(k3, jnp.array([-1, 1]), (n_daughters,))

    daughter_seqs = _apply_mutations(parent_seqs, should_mutate, mut_dims, mut_dirs)

    # Compute affinities for daughters — CHUNKED for GPU memory safety
    daughter_affs = batch_affinity_chunked(daughter_seqs, state.antigen, gamma, eta)

    # Daughter metadata
    next_id = int(state.next_id[0])
    daughter_cell_ids = jnp.arange(next_id, next_id + n_daughters, dtype=jnp.int32)
    daughter_parent_ids = state.cell_id[parent_idx]
    daughter_clone_ids = state.clone_id[parent_idx]
    daughter_gens = state.generation[parent_idx] + 1

    # Write daughters into free slots
    new_seqs = state.sequences.at[daughter_slots].set(daughter_seqs)
    new_affs = state.affinities.at[daughter_slots].set(daughter_affs)
    new_clones = state.clone_id.at[daughter_slots].set(daughter_clone_ids)
    new_gens = state.generation.at[daughter_slots].set(daughter_gens)
    new_cell_ids = state.cell_id.at[daughter_slots].set(daughter_cell_ids)
    new_parent_ids = state.parent_id.at[daughter_slots].set(daughter_parent_ids)
    new_alive = state.alive.at[daughter_slots].set(True)
    new_in_lz = state.in_lz.at[daughter_slots].set(False)

    # Division counter: increment for parents AND daughters
    new_div_counter = state.div_counter.at[parent_idx].add(1)
    parent_div_vals = state.div_counter[parent_idx] + 1
    new_div_counter = new_div_counter.at[daughter_slots].set(parent_div_vals)

    new_next_id = jnp.array([next_id + n_daughters], dtype=jnp.int32)

    return state._replace(
        sequences=new_seqs,
        affinities=new_affs,
        clone_id=new_clones,
        generation=new_gens,
        cell_id=new_cell_ids,
        parent_id=new_parent_ids,
        alive=new_alive,
        div_counter=new_div_counter,
        in_lz=new_in_lz,
        next_id=new_next_id,
    )


def dilute_to_target(
    state: BacterialStateGPU,
    rng_key: jnp.ndarray,
    target_n: int,
) -> BacterialStateGPU:
    """Random dilution: kill random alive cells until target_n remain."""
    alive_idx = jnp.where(state.alive)[0]
    n_alive = alive_idx.shape[0]

    if n_alive <= target_n:
        return state

    keep_idx = jax.random.choice(rng_key, alive_idx, shape=(target_n,), replace=False)
    new_alive = jnp.zeros_like(state.alive)
    new_alive = new_alive.at[keep_idx].set(True)

    return state._replace(alive=new_alive)


def turbidostat_growth(
    state: BacterialStateGPU,
    n_rounds: int,
    mutation_rate: float,
    gamma: float,
    eta: float,
    L: int,
    target_n: int,
    dz_divisions: int,
    rng_key: jnp.ndarray,
) -> BacterialStateGPU:
    """Run turbidostat growth for n_rounds of doubling+dilution.

    After all rounds, marks cells with div_counter >= dz_divisions as in_lz.
    """
    for i in range(n_rounds):
        rng_key, k_div, k_dil = jax.random.split(rng_key, 3)
        state = grow_one_doubling(state, k_div, mutation_rate, gamma, eta, L)
        state = dilute_to_target(state, k_dil, target_n)

    # Mark cells ready for LZ migration
    ready_mask = state.div_counter >= dz_divisions
    new_in_lz = state.alive & ready_mask

    return state._replace(in_lz=new_in_lz)
