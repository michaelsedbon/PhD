"""
Initialization — create the GC grid, place agents, generate founders.

GPU-optimized version using padded fixed-size arrays.
All agents pre-allocated to MAX_* capacity with alive mask.

Implements Algorithm 9 from Robert et al.
"""

import jax
import jax.numpy as jnp

from .config import GCConfig
from .state import (
    GCState, CentroblastState, CentrocyteState, TCellState,
    FDCState, StromalState, OutputCellState,
    MAX_CB, MAX_CC, MAX_TC, MAX_FDC, MAX_STROMAL, MAX_OUT,
    empty_centroblasts, empty_centrocytes, empty_tcells,
    empty_fdcs, empty_stromal, empty_output,
    CENTROBLAST, CENTROCYTE, TCELL, FDC, STROMAL, EMPTY, CB_G1,
)
from .affinity import (
    create_antigen, create_founders_at_distance, batch_affinity,
)


def _random_positions_in_zone(
    n: int,
    sphere_mask: jnp.ndarray,
    zone: str,
    grid_n: int,
    rng_key: jnp.ndarray,
    grid_cell_type: jnp.ndarray = None,
) -> jnp.ndarray:
    """Pick n random free positions inside the sphere, in DZ or LZ.

    DZ = x < center, LZ = x >= center.

    Returns: int32 (n, 3) positions.
    """
    center = grid_n // 2
    coords = jnp.arange(grid_n)
    x_grid = coords[:, None, None]  # broadcasts to (G, G, G)

    if zone == "DZ":
        zone_mask = x_grid < center
    else:
        zone_mask = x_grid >= center

    valid_mask = sphere_mask & zone_mask
    if grid_cell_type is not None:
        valid_mask = valid_mask & (grid_cell_type == EMPTY)

    # Flatten and select using probability sampling
    valid_flat = valid_mask.ravel()
    all_indices = jnp.arange(valid_flat.shape[0])
    probs = valid_flat.astype(jnp.float32)
    probs = probs / jnp.maximum(probs.sum(), 1.0)

    chosen_flat = jax.random.choice(rng_key, all_indices, (n,), replace=False, p=probs)

    # Convert flat to 3D
    G = grid_n
    positions = jnp.stack([
        chosen_flat // (G * G),
        (chosen_flat % (G * G)) // G,
        chosen_flat % G,
    ], axis=-1).astype(jnp.int32)

    return positions


def initialize_gc(config: GCConfig, rng_key: jnp.ndarray = None) -> GCState:
    """Initialize the full GC state with padded arrays.

    All agent arrays are pre-allocated to MAX_* capacity.
    Only the first N slots are marked alive.
    """
    if rng_key is None:
        rng_key = jax.random.PRNGKey(42)

    G = config.grid_n
    L = config.shape_space_dim

    keys = jax.random.split(rng_key, 10)

    # ── Grid ──
    grid_cell_type = jnp.zeros((G, G, G), dtype=jnp.int8)
    grid_cell_id = jnp.full((G, G, G), -1, dtype=jnp.int32)

    # Sphere mask
    center = G // 2
    coords = jnp.arange(G) - center
    xx, yy, zz = jnp.meshgrid(coords, coords, coords, indexing='ij')
    dist_sq = xx**2 + yy**2 + zz**2
    sphere_mask = dist_sq <= center**2

    # ── Antigen ──
    antigen = create_antigen(L, keys[0])

    # ── FDCs (light zone) ──
    fdc_pos = _random_positions_in_zone(
        config.n_fdcs, sphere_mask, "LZ", G, keys[1], grid_cell_type
    )
    fdcs = empty_fdcs()
    fdcs = fdcs._replace(
        position=fdcs.position.at[:config.n_fdcs].set(fdc_pos),
        antigen_amount=fdcs.antigen_amount.at[:config.n_fdcs].set(
            config.n_antigen_per_fdc
        ),
        alive=fdcs.alive.at[:config.n_fdcs].set(True),
    )
    # Place on grid
    for i in range(config.n_fdcs):
        x, y, z = fdc_pos[i, 0], fdc_pos[i, 1], fdc_pos[i, 2]
        grid_cell_type = grid_cell_type.at[x, y, z].set(FDC)
        grid_cell_id = grid_cell_id.at[x, y, z].set(i)

    # ── Stromal cells (dark zone) ──
    stromal_pos = _random_positions_in_zone(
        config.n_stromal, sphere_mask, "DZ", G, keys[2], grid_cell_type
    )
    stromal = empty_stromal()
    stromal = stromal._replace(
        position=stromal.position.at[:config.n_stromal].set(stromal_pos),
        alive=stromal.alive.at[:config.n_stromal].set(True),
    )
    for i in range(config.n_stromal):
        x, y, z = stromal_pos[i, 0], stromal_pos[i, 1], stromal_pos[i, 2]
        grid_cell_type = grid_cell_type.at[x, y, z].set(STROMAL)
        grid_cell_id = grid_cell_id.at[x, y, z].set(i)

    # ── T cells (light zone) ──
    tc_pos = _random_positions_in_zone(
        config.n_tcells, sphere_mask, "LZ", G, keys[3], grid_cell_type
    )
    tcells = empty_tcells()
    tcells = tcells._replace(
        position=tcells.position.at[:config.n_tcells].set(tc_pos),
        polarity=tcells.polarity.at[:config.n_tcells].set(
            jax.random.normal(keys[4], (config.n_tcells, 3))
        ),
        alive=tcells.alive.at[:config.n_tcells].set(True),
    )
    for i in range(config.n_tcells):
        x, y, z = tc_pos[i, 0], tc_pos[i, 1], tc_pos[i, 2]
        grid_cell_type = grid_cell_type.at[x, y, z].set(TCELL)
        grid_cell_id = grid_cell_id.at[x, y, z].set(i)

    # ── Founder centroblasts (dark zone) ──
    founder_seqs = create_founders_at_distance(
        config.n_founders, antigen,
        config.initial_hamming_min, config.initial_hamming_max,
        keys[5],
    )
    founder_affs = batch_affinity(
        founder_seqs, antigen, config.affinity_gamma, config.affinity_eta,
    )
    founder_pos = _random_positions_in_zone(
        config.n_founders, sphere_mask, "DZ", G, keys[6], grid_cell_type
    )
    founder_pols = jax.random.normal(keys[7], (config.n_founders, 3))
    pol_norms = jnp.linalg.norm(founder_pols, axis=-1, keepdims=True)
    founder_pols = founder_pols / jnp.maximum(pol_norms, 1e-8)

    # Fill padded CB arrays
    cbs = empty_centroblasts(L)
    n = config.n_founders
    cbs = cbs._replace(
        position=cbs.position.at[:n].set(founder_pos),
        polarity=cbs.polarity.at[:n].set(founder_pols),
        sequence=cbs.sequence.at[:n].set(founder_seqs),
        affinity=cbs.affinity.at[:n].set(founder_affs),
        phase=cbs.phase.at[:n].set(CB_G1),
        phase_clock=cbs.phase_clock.at[:n].set(0.0),
        remaining_divisions=cbs.remaining_divisions.at[:n].set(config.founder_divisions),
        clone_id=cbs.clone_id.at[:n].set(jnp.arange(n)),
        responsive_cxcl12=cbs.responsive_cxcl12.at[:n].set(True),
        responsive_cxcl13=cbs.responsive_cxcl13.at[:n].set(True),
        alive=cbs.alive.at[:n].set(True),
    )
    for i in range(config.n_founders):
        x, y, z = founder_pos[i, 0], founder_pos[i, 1], founder_pos[i, 2]
        grid_cell_type = grid_cell_type.at[x, y, z].set(CENTROBLAST)
        grid_cell_id = grid_cell_id.at[x, y, z].set(i)

    # ── Chemokine fields ──
    cxcl12 = jnp.zeros((G, G, G), dtype=jnp.float32)
    cxcl13 = jnp.zeros((G, G, G), dtype=jnp.float32)

    # ── Empty centrocytes and output cells ──
    ccs = empty_centrocytes(L)
    outputs = empty_output(L)

    return GCState(
        grid_cell_type=grid_cell_type,
        grid_cell_id=grid_cell_id,
        sphere_mask=sphere_mask,
        cxcl12=cxcl12,
        cxcl13=cxcl13,
        centroblasts=cbs,
        centrocytes=ccs,
        tcells=tcells,
        fdcs=fdcs,
        stromal=stromal,
        output_cells=outputs,
        antigen=antigen,
        time=0.0,
    )
