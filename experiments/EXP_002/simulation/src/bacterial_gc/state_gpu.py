"""
GPU-optimized state for Bacterial GC — padded fixed-size arrays.

All arrays are pre-allocated at N_MAX and use an `alive` mask.
No dynamic allocation during simulation — everything JIT-compatible.
"""

import jax
import jax.numpy as jnp
from typing import NamedTuple


# Maximum population size — must accommodate doubling during growth.
# At turbidostat_target_n=10^6 with 12 doublings, population peaks at ~2×10^6
# before dilution, so N_MAX=2.5M gives headroom.
N_MAX = 2_500_000

# Default shape space dimension
L_DEFAULT = 400


class BacterialStateGPU(NamedTuple):
    """Fixed-size GPU state. All arrays are [N_MAX] or [N_MAX, L]."""
    sequences: jnp.ndarray      # int32[N_MAX, L]
    affinities: jnp.ndarray     # float32[N_MAX]
    hamming: jnp.ndarray        # float32[N_MAX] — Hamming distance to antigen
    clone_id: jnp.ndarray       # int32[N_MAX]
    generation: jnp.ndarray     # int32[N_MAX]
    cell_id: jnp.ndarray        # int32[N_MAX]
    parent_id: jnp.ndarray      # int32[N_MAX]
    alive: jnp.ndarray          # bool[N_MAX]
    div_counter: jnp.ndarray    # int32[N_MAX] — divisions since last selection
    in_lz: jnp.ndarray          # bool[N_MAX] — True if cell is in LZ for selection
    antigen: jnp.ndarray        # int32[L]
    next_id: jnp.ndarray        # int32[1] — next available cell ID (scalar as array for JIT)
    cycle: jnp.ndarray          # int32[1]


def empty_state(L: int = L_DEFAULT, n_max: int = N_MAX) -> BacterialStateGPU:
    """Allocate empty GPU state with all slots dead.

    Arrays are placed on CPU to avoid GPU OOM at large N.
    Only affinity computation uses GPU via chunked dispatch.
    """
    cpu = jax.devices('cpu')[0]

    def _cpu(arr):
        return jax.device_put(arr, cpu)

    return BacterialStateGPU(
        sequences=_cpu(jnp.zeros((n_max, L), dtype=jnp.int8)),
        affinities=_cpu(jnp.zeros(n_max, dtype=jnp.float32)),
        hamming=_cpu(jnp.zeros(n_max, dtype=jnp.float32)),
        clone_id=_cpu(jnp.zeros(n_max, dtype=jnp.int32)),
        generation=_cpu(jnp.zeros(n_max, dtype=jnp.int32)),
        cell_id=_cpu(jnp.zeros(n_max, dtype=jnp.int32)),
        parent_id=_cpu(jnp.full(n_max, -1, dtype=jnp.int32)),
        alive=_cpu(jnp.zeros(n_max, dtype=jnp.bool_)),
        div_counter=_cpu(jnp.zeros(n_max, dtype=jnp.int32)),
        in_lz=_cpu(jnp.zeros(n_max, dtype=jnp.bool_)),
        antigen=_cpu(jnp.zeros(L, dtype=jnp.int32)),
        next_id=_cpu(jnp.array([0], dtype=jnp.int32)),
        cycle=_cpu(jnp.array([0], dtype=jnp.int32)),
    )


def count_alive(state: BacterialStateGPU) -> int:
    """Count living cells."""
    return int(jnp.sum(state.alive))


def count_in_lz(state: BacterialStateGPU) -> int:
    """Count cells in LZ."""
    return int(jnp.sum(state.alive & state.in_lz))


def allocate_slots(alive: jnp.ndarray, n: int) -> jnp.ndarray:
    """Find n free (dead) slots in the padded array.

    Returns indices of n free slots. If fewer than n free slots exist,
    the extra indices will point to already-alive slots (caller must handle).
    """
    # Dead slots first in argsort
    free_priority = jnp.where(alive, 1, 0)
    sorted_idx = jnp.argsort(free_priority)
    return sorted_idx[:n]
