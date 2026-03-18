"""
State representation for the Bacterial GC.

Simple NamedTuple — no grid, no padded arrays.
Population size is dynamic between cycles.
"""

from typing import NamedTuple
import jax.numpy as jnp


# Compartment tags
DZ = 0
LZ = 1
EXTRACTED = 2


class BacterialState(NamedTuple):
    """State of the bacterial population."""
    sequences: jnp.ndarray      # int32[N, L] — nanobody genotype
    affinities: jnp.ndarray     # float32[N] — affinity to antigen
    compartment: jnp.ndarray    # int8[N] — DZ=0, LZ=1, EXTRACTED=2
    clone_id: jnp.ndarray       # int32[N] — founder clone identity
    generation: jnp.ndarray     # int32[N] — divisions since founder
    alive: jnp.ndarray          # bool[N]
    antigen: jnp.ndarray        # int32[L] — target antigen (static)
    cycle: int = 0              # current cycle number
    cell_id: jnp.ndarray = None      # int32[N] — unique cell ID for lineage
    parent_id: jnp.ndarray = None    # int32[N] — parent cell ID (-1 for founders)
    next_id: int = 0                 # next available cell ID


class Snapshot(NamedTuple):
    """Metrics captured at each cycle."""
    cycle: int
    n_total: int
    n_dz: int
    n_lz: int
    n_extracted: int
    mean_affinity: float
    max_affinity: float
    median_affinity: float
    std_affinity: float
    diversity: float            # Shannon entropy over clone_ids
    n_unique_clones: int
    top_clone_fraction: float   # fraction of population from most common clone


def count_bacteria(state: BacterialState) -> dict:
    """Count bacteria by compartment."""
    alive = state.alive
    return {
        'n_total': int(jnp.sum(alive)),
        'n_dz': int(jnp.sum(alive & (state.compartment == DZ))),
        'n_lz': int(jnp.sum(alive & (state.compartment == LZ))),
        'n_extracted': int(jnp.sum(state.compartment == EXTRACTED)),
    }
