"""
GC simulation state — padded fixed-size arrays for GPU acceleration.

All cell arrays are pre-allocated to MAX_* capacity with an `alive` mask.
New cells fill free slots. Dead cells just flip alive=False.
No array concatenation → fully JIT-compatible.

Design:
  - Each agent type has a fixed-size array (MAX_CB, MAX_CC, etc.)
  - `alive` mask tracks which slots are in use
  - `allocate_slots()` finds free slots for new cells
  - Grid arrays are always (G, G, G) — never change shape
"""

import jax
import jax.numpy as jnp
from typing import NamedTuple

# ─── Array capacity ──────────────────────────────────────────────────────

MAX_CB = 10_000     # max centroblasts
MAX_CC = 5_000      # max centrocytes
MAX_TC = 200        # max T cells (fixed population)
MAX_FDC = 50        # max FDCs (fixed population)
MAX_STROMAL = 100   # max stromal cells (fixed population)
MAX_OUT = 5_000     # max output cells

# ─── Cell type constants (for grid) ──────────────────────────────────────

EMPTY = 0
CENTROBLAST = 1
CENTROCYTE = 2
TCELL = 3
FDC = 4
STROMAL = 5
OUTPUT = 6

# ─── Cell phase / state constants ────────────────────────────────────────

# Centroblast phases
CB_G1 = 0
CB_S = 1
CB_G2 = 2
CB_M = 3

# Centrocyte states
CC_UNSELECTED = 0
CC_FDC_CONTACT = 1
CC_FDC_SELECTED = 2
CC_TC_SIGNALING = 3
CC_SELECTED = 4
CC_APOPTOSIS = 5


# ─── Agent state NamedTuples ────────────────────────────────────────────


class CentroblastState(NamedTuple):
    """Centroblast state arrays — all shape (MAX_CB, ...)."""
    position: jnp.ndarray          # (MAX_CB, 3) int32
    polarity: jnp.ndarray          # (MAX_CB, 3) float32
    sequence: jnp.ndarray          # (MAX_CB, L) int32
    affinity: jnp.ndarray          # (MAX_CB,) float32
    phase: jnp.ndarray             # (MAX_CB,) int8
    phase_clock: jnp.ndarray       # (MAX_CB,) float32
    remaining_divisions: jnp.ndarray  # (MAX_CB,) int32
    clone_id: jnp.ndarray          # (MAX_CB,) int32
    responsive_cxcl12: jnp.ndarray # (MAX_CB,) bool
    responsive_cxcl13: jnp.ndarray # (MAX_CB,) bool
    alive: jnp.ndarray             # (MAX_CB,) bool


class CentrocyteState(NamedTuple):
    """Centrocyte state arrays — all shape (MAX_CC, ...)."""
    position: jnp.ndarray          # (MAX_CC, 3) int32
    polarity: jnp.ndarray          # (MAX_CC, 3) float32
    sequence: jnp.ndarray          # (MAX_CC, L) int32
    affinity: jnp.ndarray          # (MAX_CC,) float32
    state: jnp.ndarray             # (MAX_CC,) int8
    fdc_clock: jnp.ndarray         # (MAX_CC,) float32
    tc_clock: jnp.ndarray          # (MAX_CC,) float32
    tc_signal: jnp.ndarray         # (MAX_CC,) float32
    n_fdc_contacts: jnp.ndarray    # (MAX_CC,) int32
    diff_clock: jnp.ndarray        # (MAX_CC,) float32
    clone_id: jnp.ndarray          # (MAX_CC,) int32
    responsive_cxcl12: jnp.ndarray # (MAX_CC,) bool
    responsive_cxcl13: jnp.ndarray # (MAX_CC,) bool
    alive: jnp.ndarray             # (MAX_CC,) bool


class TCellState(NamedTuple):
    """T cell state arrays — all shape (MAX_TC, ...)."""
    position: jnp.ndarray          # (MAX_TC, 3) int32
    polarity: jnp.ndarray          # (MAX_TC, 3) float32
    alive: jnp.ndarray             # (MAX_TC,) bool


class FDCState(NamedTuple):
    """FDC state arrays — all shape (MAX_FDC, ...)."""
    position: jnp.ndarray          # (MAX_FDC, 3) int32
    antigen_amount: jnp.ndarray    # (MAX_FDC,) float32
    alive: jnp.ndarray             # (MAX_FDC,) bool


class StromalState(NamedTuple):
    """Stromal cell state — all shape (MAX_STROMAL, ...)."""
    position: jnp.ndarray          # (MAX_STROMAL, 3) int32
    alive: jnp.ndarray             # (MAX_STROMAL,) bool


class OutputCellState(NamedTuple):
    """Output cell state — all shape (MAX_OUT, ...)."""
    position: jnp.ndarray          # (MAX_OUT, 3) int32
    polarity: jnp.ndarray          # (MAX_OUT, 3) float32
    sequence: jnp.ndarray          # (MAX_OUT, L) int32
    affinity: jnp.ndarray          # (MAX_OUT,) float32
    clone_id: jnp.ndarray          # (MAX_OUT,) int32
    alive: jnp.ndarray             # (MAX_OUT,) bool


class GCState(NamedTuple):
    """Complete germinal center state."""
    grid_cell_type: jnp.ndarray    # (G, G, G) int8
    grid_cell_id: jnp.ndarray      # (G, G, G) int32
    sphere_mask: jnp.ndarray       # (G, G, G) bool
    cxcl12: jnp.ndarray            # (G, G, G) float32
    cxcl13: jnp.ndarray            # (G, G, G) float32
    centroblasts: CentroblastState
    centrocytes: CentrocyteState
    tcells: TCellState
    fdcs: FDCState
    stromal: StromalState
    output_cells: OutputCellState
    antigen: jnp.ndarray           # (L,) int32
    time: float


# ─── Slot allocator ──────────────────────────────────────────────────────


def allocate_slots(alive: jnp.ndarray, n: int) -> jnp.ndarray:
    """Find `n` free slots in a padded array.

    Returns indices of the first `n` slots where alive == False.
    If fewer than `n` are free, returns -1 for overflow slots.

    This is JIT-compatible because the output shape is static (n,).

    Args:
        alive: bool (MAX,) — alive mask.
        n: number of slots needed (static int).
    Returns:
        int32 (n,) — indices of free slots (-1 if overflow).
    """
    # Cumsum of ~alive gives "how many free slots up to here"
    free_mask = ~alive
    cumsum = jnp.cumsum(free_mask)

    # The i-th free slot is where cumsum == i+1 and free_mask is True
    # We want first n such positions
    # Use a scan approach: for each target 1..n, find first position
    # where cumsum reaches that target

    max_slots = alive.shape[0]

    # Create an index for each free position
    # free_indices[i] = position of the (i+1)-th free slot
    # This is: argwhere(free_mask), but padded to n elements

    # Efficient approach: use argsort of ~alive (free slots sort first)
    # Then take the first n indices
    sort_key = jnp.where(free_mask, jnp.arange(max_slots), max_slots + jnp.arange(max_slots))
    sorted_indices = jnp.argsort(sort_key)
    free_indices = sorted_indices[:n]

    # Mark overflow (where the slot isn't actually free)
    is_valid = free_mask[free_indices]
    return jnp.where(is_valid, free_indices, -1)


def count_alive(alive: jnp.ndarray) -> jnp.ndarray:
    """Count alive cells (JIT-friendly, returns JAX scalar)."""
    return jnp.sum(alive)


# ─── Empty state constructors ───────────────────────────────────────────


def empty_centroblasts(L: int = 4) -> CentroblastState:
    """Create empty padded centroblast state."""
    return CentroblastState(
        position=jnp.zeros((MAX_CB, 3), dtype=jnp.int32),
        polarity=jnp.zeros((MAX_CB, 3), dtype=jnp.float32),
        sequence=jnp.zeros((MAX_CB, L), dtype=jnp.int32),
        affinity=jnp.zeros(MAX_CB, dtype=jnp.float32),
        phase=jnp.zeros(MAX_CB, dtype=jnp.int8),
        phase_clock=jnp.zeros(MAX_CB, dtype=jnp.float32),
        remaining_divisions=jnp.zeros(MAX_CB, dtype=jnp.int32),
        clone_id=jnp.zeros(MAX_CB, dtype=jnp.int32),
        responsive_cxcl12=jnp.zeros(MAX_CB, dtype=jnp.bool_),
        responsive_cxcl13=jnp.zeros(MAX_CB, dtype=jnp.bool_),
        alive=jnp.zeros(MAX_CB, dtype=jnp.bool_),
    )


def empty_centrocytes(L: int = 4) -> CentrocyteState:
    """Create empty padded centrocyte state."""
    return CentrocyteState(
        position=jnp.zeros((MAX_CC, 3), dtype=jnp.int32),
        polarity=jnp.zeros((MAX_CC, 3), dtype=jnp.float32),
        sequence=jnp.zeros((MAX_CC, L), dtype=jnp.int32),
        affinity=jnp.zeros(MAX_CC, dtype=jnp.float32),
        state=jnp.zeros(MAX_CC, dtype=jnp.int8),
        fdc_clock=jnp.zeros(MAX_CC, dtype=jnp.float32),
        tc_clock=jnp.zeros(MAX_CC, dtype=jnp.float32),
        tc_signal=jnp.zeros(MAX_CC, dtype=jnp.float32),
        n_fdc_contacts=jnp.zeros(MAX_CC, dtype=jnp.int32),
        diff_clock=jnp.zeros(MAX_CC, dtype=jnp.float32),
        clone_id=jnp.zeros(MAX_CC, dtype=jnp.int32),
        responsive_cxcl12=jnp.zeros(MAX_CC, dtype=jnp.bool_),
        responsive_cxcl13=jnp.zeros(MAX_CC, dtype=jnp.bool_),
        alive=jnp.zeros(MAX_CC, dtype=jnp.bool_),
    )


def empty_tcells() -> TCellState:
    """Create empty padded T cell state."""
    return TCellState(
        position=jnp.zeros((MAX_TC, 3), dtype=jnp.int32),
        polarity=jnp.zeros((MAX_TC, 3), dtype=jnp.float32),
        alive=jnp.zeros(MAX_TC, dtype=jnp.bool_),
    )


def empty_fdcs() -> FDCState:
    """Create empty padded FDC state."""
    return FDCState(
        position=jnp.zeros((MAX_FDC, 3), dtype=jnp.int32),
        antigen_amount=jnp.zeros(MAX_FDC, dtype=jnp.float32),
        alive=jnp.zeros(MAX_FDC, dtype=jnp.bool_),
    )


def empty_stromal() -> StromalState:
    """Create empty padded stromal state."""
    return StromalState(
        position=jnp.zeros((MAX_STROMAL, 3), dtype=jnp.int32),
        alive=jnp.zeros(MAX_STROMAL, dtype=jnp.bool_),
    )


def empty_output(L: int = 4) -> OutputCellState:
    """Create empty padded output cell state."""
    return OutputCellState(
        position=jnp.zeros((MAX_OUT, 3), dtype=jnp.int32),
        polarity=jnp.zeros((MAX_OUT, 3), dtype=jnp.float32),
        sequence=jnp.zeros((MAX_OUT, L), dtype=jnp.int32),
        affinity=jnp.zeros(MAX_OUT, dtype=jnp.float32),
        clone_id=jnp.zeros(MAX_OUT, dtype=jnp.int32),
        alive=jnp.zeros(MAX_OUT, dtype=jnp.bool_),
    )


# ─── Count cells helper ─────────────────────────────────────────────────


def count_cells(state: GCState) -> dict:
    """Count alive cells of each type (non-JIT helper for logging)."""
    n_cb = int(jnp.sum(state.centroblasts.alive))
    n_cc = int(jnp.sum(state.centrocytes.alive))
    n_tc = int(jnp.sum(state.tcells.alive))
    n_fdc = int(jnp.sum(state.fdcs.alive))
    n_out = int(jnp.sum(state.output_cells.alive))
    return {
        'n_cb': n_cb,
        'n_cc': n_cc,
        'n_tc': n_tc,
        'n_fdc': n_fdc,
        'n_out': n_out,
        'n_total': n_cb + n_cc + n_tc + n_fdc + n_out,
        'n_bcells': n_cb + n_cc,
    }
