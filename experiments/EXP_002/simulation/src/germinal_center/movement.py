"""
Cell movement — vectorized parallel movement with conflict resolution.

GPU-optimized Algorithm 3 from Robert et al.:
  - All cells compute targets in parallel (vmap)
  - Conflicts resolved via random priority
  - Grid updated via vectorized scatter
  - Fully JIT-compatible — no Python loops over cells
"""

import jax
import jax.numpy as jnp
from functools import partial

from .state import EMPTY


# ─── 26-neighborhood offsets (3D Moore neighborhood) ──────────────────────

_OFFSETS = jnp.array([
    [dx, dy, dz]
    for dx in [-1, 0, 1]
    for dy in [-1, 0, 1]
    for dz in [-1, 0, 1]
    if not (dx == 0 and dy == 0 and dz == 0)
], dtype=jnp.int32)  # shape (26, 3)

_OFFSETS_FLOAT = _OFFSETS.astype(jnp.float32)
_OFFSET_NORMS = jnp.linalg.norm(_OFFSETS_FLOAT, axis=-1, keepdims=True)
_OFFSET_DIRS = _OFFSETS_FLOAT / jnp.maximum(_OFFSET_NORMS, 1e-8)  # (26, 3)


# ─── Polarity update (already vectorized) ─────────────────────────────────


@partial(jax.jit, static_argnums=())
def update_polarity(
    polarity: jnp.ndarray,
    gradient: jnp.ndarray,
    responsive: jnp.ndarray,
    alive: jnp.ndarray,
    rng_key: jnp.ndarray,
    persistence_weight: float,
    chemo_weight: float,
) -> jnp.ndarray:
    """Update polarity vectors for a batch of cells (vectorized).

    Args:
        polarity: float32 (MAX, 3)
        gradient: float32 (MAX, 3) — chemokine gradient at cell positions
        responsive: bool (MAX,)
        alive: bool (MAX,)
        rng_key: JAX PRNG key
        persistence_weight, chemo_weight: scalars
    Returns:
        float32 (MAX, 3) — updated polarity (unit vectors, dead cells unchanged)
    """
    N = polarity.shape[0]
    random_vec = jax.random.normal(rng_key, (N, 3))

    grad_contribution = jnp.where(
        responsive[:, None], chemo_weight * gradient, 0.0,
    )

    new_polarity = (
        persistence_weight * polarity + grad_contribution + random_vec
    )

    norms = jnp.linalg.norm(new_polarity, axis=-1, keepdims=True)
    norms = jnp.maximum(norms, 1e-8)
    new_polarity = new_polarity / norms

    # Only update alive cells
    return jnp.where(alive[:, None], new_polarity, polarity)


# ─── Single-cell target computation (for vmap) ──────────────────────────


def _find_target_single(
    pos: jnp.ndarray,
    polarity: jnp.ndarray,
    grid_cell_type: jnp.ndarray,
    sphere_mask: jnp.ndarray,
) -> jnp.ndarray:
    """Find best free neighbor for one cell. Pure JAX, no control flow.

    Returns:
        int32 (3,) — target position (or current pos if no valid neighbor)
    """
    grid_n = grid_cell_type.shape[0]

    candidates = pos[None, :] + _OFFSETS  # (26, 3)
    candidates = jnp.clip(candidates, 0, grid_n - 1)

    cx, cy, cz = candidates[:, 0], candidates[:, 1], candidates[:, 2]
    is_empty = grid_cell_type[cx, cy, cz] == EMPTY
    is_inside = sphere_mask[cx, cy, cz]
    is_valid = is_empty & is_inside

    scores = jnp.sum(_OFFSET_DIRS * polarity[None, :], axis=-1)
    scores = jnp.where(is_valid, scores, -1e10)

    best_idx = jnp.argmax(scores)
    best_pos = candidates[best_idx]

    any_valid = jnp.any(is_valid)
    return jnp.where(any_valid, best_pos, pos)


# ─── Vectorized parallel movement ───────────────────────────────────────


def _pos_to_flat(pos: jnp.ndarray, G: int) -> jnp.ndarray:
    """Convert (N, 3) positions to flat indices in (G, G, G) grid."""
    return pos[:, 0] * G * G + pos[:, 1] * G + pos[:, 2]


def _flat_to_pos(flat: jnp.ndarray, G: int) -> jnp.ndarray:
    """Convert flat indices to (N, 3) positions."""
    x = flat // (G * G)
    y = (flat % (G * G)) // G
    z = flat % G
    return jnp.stack([x, y, z], axis=-1)


def move_cells_parallel(
    positions: jnp.ndarray,
    polarities: jnp.ndarray,
    alive: jnp.ndarray,
    grid_cell_type: jnp.ndarray,
    grid_cell_id: jnp.ndarray,
    sphere_mask: jnp.ndarray,
    cell_type_id: int,
    rng_key: jnp.ndarray,
) -> tuple:
    """Move cells in parallel with conflict resolution.

    Algorithm:
    1. All alive cells compute their desired target (vmap)
    2. Convert targets to flat grid indices for conflict detection
    3. For each target: if multiple cells want it, highest priority wins
    4. Winners move, losers stay
    5. Update grid

    Args:
        positions: int32 (MAX, 3)
        polarities: float32 (MAX, 3)
        alive: bool (MAX,)
        grid_cell_type: int8 (G, G, G)
        grid_cell_id: int32 (G, G, G)
        sphere_mask: bool (G, G, G)
        cell_type_id: int
        rng_key: JAX PRNG key
    Returns:
        (new_positions, new_grid_cell_type, new_grid_cell_id)
    """
    MAX = positions.shape[0]
    G = grid_cell_type.shape[0]

    # 1. All cells compute targets in parallel
    # vmap over the cell axis, broadcasting grid arrays
    find_target_batch = jax.vmap(
        _find_target_single,
        in_axes=(0, 0, None, None),
    )
    targets = find_target_batch(positions, polarities, grid_cell_type, sphere_mask)

    # Check which cells actually want to move
    wants_to_move = alive & jnp.any(targets != positions, axis=-1)

    # 2. Convert to flat indices for conflict detection
    target_flat = _pos_to_flat(targets, G)  # (MAX,)
    current_flat = _pos_to_flat(positions, G)  # (MAX,)

    # 3. Random priority for conflict resolution
    priorities = jax.random.uniform(rng_key, (MAX,))
    priorities = jnp.where(wants_to_move, priorities, -1.0)

    # For each target flat index, find the cell with highest priority
    # Use segment_max approach: scatter priorities into a grid-sized buffer
    # Then each cell checks if it has the highest priority for its target
    grid_size = G * G * G

    # Initialize with -infinity
    max_priority = jnp.full(grid_size, -jnp.inf)
    # Scatter max priority for each target
    max_priority = max_priority.at[target_flat].max(priorities)
    # A cell wins if its priority equals the max at its target
    is_winner = wants_to_move & (priorities == max_priority[target_flat])
    # Tie-breaking: if multiple cells have same priority (unlikely with float),
    # segment_max would have captured one; we accept this tiny probability

    # 4. Compute final positions
    new_positions = jnp.where(is_winner[:, None], targets, positions)

    # 5. Update grid via scatter
    old_flat = _pos_to_flat(positions, G)
    new_flat = _pos_to_flat(new_positions, G)

    grid_type_flat = grid_cell_type.ravel()
    grid_id_flat = grid_cell_id.ravel()

    # Clear old positions of winners: scatter EMPTY where is_winner
    # Only modify positions of cells that actually moved
    clear_vals = jnp.where(is_winner, EMPTY, grid_type_flat[old_flat])
    grid_type_flat = grid_type_flat.at[old_flat].set(clear_vals)

    clear_ids = jnp.where(is_winner, -1, grid_id_flat[old_flat])
    grid_id_flat = grid_id_flat.at[old_flat].set(clear_ids)

    # Set new positions of winners
    cell_indices = jnp.arange(MAX, dtype=jnp.int32)
    set_type_vals = jnp.where(is_winner, cell_type_id, grid_type_flat[new_flat])
    grid_type_flat = grid_type_flat.at[new_flat].set(set_type_vals)

    set_id_vals = jnp.where(is_winner, cell_indices, grid_id_flat[new_flat])
    grid_id_flat = grid_id_flat.at[new_flat].set(set_id_vals)

    new_grid_type = grid_type_flat.reshape(G, G, G).astype(jnp.int8)
    new_grid_id = grid_id_flat.reshape(G, G, G)

    return new_positions, new_grid_type, new_grid_id


# ─── Legacy alias ────────────────────────────────────────────────────────

# Keep old name for compatibility during transition
move_cells_sequential = move_cells_parallel
