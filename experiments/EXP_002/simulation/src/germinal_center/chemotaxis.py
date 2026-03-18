"""
Chemotaxis — chemokine production, diffusion, and receptor sensitivity.

Implements Algorithm 2 from Robert et al.:
  - CXCL12: produced by stromal cells in the dark zone
  - CXCL13: produced by FDCs in the light zone
  - Diffusion: finite-difference Laplacian on 3D grid
  - Receptor sensitivity: desensitize at high concentration, resensitize at low

Boundary conditions: Dirichlet (concentration = 0 at sphere boundary)
"""

import jax
import jax.numpy as jnp
from functools import partial


# ─── Chemokine production (Algorithm 2, production step) ───────────────────


def produce_chemokine(
    field: jnp.ndarray,
    source_positions: jnp.ndarray,
    rate: float,
    dt: float,
) -> jnp.ndarray:
    """Add chemokine production from source cells.

    Each source cell adds `rate * dt` to its grid point.

    Args:
        field: float32 (N, N, N) — current chemokine concentration.
        source_positions: int32 (M, 3) — positions of producing cells.
        rate: production rate per cell per hour.
        dt: timestep in hours.
    Returns:
        Updated field with production added.
    """
    if source_positions.shape[0] == 0:
        return field

    # Add production at each source position
    production = rate * dt
    x, y, z = source_positions[:, 0], source_positions[:, 1], source_positions[:, 2]
    return field.at[x, y, z].add(production)


# ─── Diffusion (Algorithm 2, diffusion step) ──────────────────────────────


@partial(jax.jit, static_argnums=())
def _diffuse_3d_single(
    field: jnp.ndarray,
    alpha: float,
    sphere_mask: jnp.ndarray,
) -> jnp.ndarray:
    """Single diffusion step (assumes alpha ≤ 1/6)."""
    laplacian = (
        jnp.roll(field, 1, axis=0) + jnp.roll(field, -1, axis=0) +
        jnp.roll(field, 1, axis=1) + jnp.roll(field, -1, axis=1) +
        jnp.roll(field, 1, axis=2) + jnp.roll(field, -1, axis=2) -
        6.0 * field
    )
    new_field = field + alpha * laplacian
    new_field = jnp.where(sphere_mask, new_field, 0.0)
    return jnp.maximum(new_field, 0.0)


def diffuse_3d(
    field: jnp.ndarray,
    alpha: float,
    sphere_mask: jnp.ndarray,
) -> jnp.ndarray:
    """3D finite-difference diffusion with automatic sub-stepping.

    Discrete Laplacian: ∇²u ≈ (1/dx²) Σ (u_neighbor - u_center)
    Update: u_new = u + α * ∇²u  where α = D*dt/dx²

    If α > 1/6 (stability limit for 3D), automatically splits into
    sub-steps so each sub-step has α_sub ≤ 1/6.

    Args:
        field: float32 (N, N, N) — concentration field.
        alpha: D * dt / dx² — total diffusion parameter.
        sphere_mask: bool (N, N, N) — True inside the GC sphere.
    Returns:
        Updated concentration field.
    """
    MAX_ALPHA = 1.0 / 6.0  # stability limit

    if alpha <= MAX_ALPHA:
        return _diffuse_3d_single(field, alpha, sphere_mask)

    # Sub-step: split into n_sub steps each with alpha_sub ≤ MAX_ALPHA
    import math
    n_sub = math.ceil(alpha / MAX_ALPHA)
    alpha_sub = alpha / n_sub

    for _ in range(n_sub):
        field = _diffuse_3d_single(field, alpha_sub, sphere_mask)

    return field


# ─── Receptor sensitivity (Algorithm 2, receptor update) ──────────────────


def update_receptor_sensitivity(
    positions: jnp.ndarray,
    responsive: jnp.ndarray,
    chemokine_field: jnp.ndarray,
    desensitize_thresh: float,
    resensitize_thresh: float,
) -> jnp.ndarray:
    """Update chemokine receptor sensitivity for a batch of cells.

    Paper: "Cells are desensitized at high chemokine concentration
    and resensitized when concentration drops."

    Args:
        positions: int32 (N, 3) — cell positions.
        responsive: bool (N,) — current sensitivity state.
        chemokine_field: float32 (N_grid, N_grid, N_grid) — concentration.
        desensitize_thresh: concentration above which receptor desensitizes.
        resensitize_thresh: concentration below which receptor resensitizes.
    Returns:
        Updated bool (N,) — new sensitivity states.
    """
    if positions.shape[0] == 0:
        return responsive

    # Sample local concentration at each cell's position
    x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]
    local_conc = chemokine_field[x, y, z]

    # Desensitize if concentration is high
    new_responsive = jnp.where(local_conc > desensitize_thresh, False, responsive)
    # Resensitize if concentration is low
    new_responsive = jnp.where(local_conc < resensitize_thresh, True, new_responsive)

    return new_responsive


# ─── Gradient computation (for movement bias) ─────────────────────────────


def compute_gradient_at(
    field: jnp.ndarray,
    positions: jnp.ndarray,
) -> jnp.ndarray:
    """Compute chemokine gradient at cell positions using central differences.

    Args:
        field: float32 (N, N, N) — concentration field.
        positions: int32 (M, 3) — cell positions.
    Returns:
        float32 (M, 3) — gradient vector at each position.
    """
    if positions.shape[0] == 0:
        return jnp.zeros((0, 3), dtype=jnp.float32)

    x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]
    N = field.shape[0]

    # Central differences with clamping at boundaries
    dx = (field[jnp.clip(x + 1, 0, N - 1), y, z] -
          field[jnp.clip(x - 1, 0, N - 1), y, z]) / 2.0
    dy = (field[x, jnp.clip(y + 1, 0, N - 1), z] -
          field[x, jnp.clip(y - 1, 0, N - 1), z]) / 2.0
    dz = (field[x, y, jnp.clip(z + 1, 0, N - 1)] -
          field[x, y, jnp.clip(z - 1, 0, N - 1)]) / 2.0

    return jnp.stack([dx, dy, dz], axis=-1)
