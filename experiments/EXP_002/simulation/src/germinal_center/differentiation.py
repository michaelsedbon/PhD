"""
Differentiation — recycling, output cell creation, and founder inflow.
Hybrid GPU: 1 sync for early exit, vectorized scatter for inner work.
"""

import jax
import jax.numpy as jnp

from .state import (
    CentroblastState, CentrocyteState, OutputCellState,
    CC_SELECTED, CB_G1, CENTROBLAST, EMPTY,
    MAX_CB, MAX_CC, MAX_OUT,
    allocate_slots,
)
from .affinity import create_founders_at_distance, batch_affinity


# ─── Block 9: Differentiation / Recycling ────────────────────────────


def process_differentiation(
    cbs: CentroblastState,
    ccs: CentrocyteState,
    outputs: OutputCellState,
    dt: float,
    diff_delay: float,
    prob_output: float,
    n_div_min: int,
    n_div_max: int,
    n_div_hill_n: float,
    n_div_hill_k: float,
    rng_key: jnp.ndarray,
    grid_cell_type: jnp.ndarray,
    grid_cell_id: jnp.ndarray,
) -> tuple:
    """Hybrid: 1 sync for early exit, vectorized scatter for work."""
    G = grid_cell_type.shape[0]
    k1, k2 = jax.random.split(rng_key)

    is_selected = (ccs.state == CC_SELECTED) & ccs.alive
    new_diff_clock = jnp.where(is_selected, ccs.diff_clock + dt, ccs.diff_clock)
    ready = is_selected & (new_diff_clock >= diff_delay)
    ccs = ccs._replace(diff_clock=new_diff_clock)

    n_ready = int(jnp.sum(ready))
    if n_ready == 0:
        return cbs, ccs, outputs, grid_cell_type, grid_cell_id

    ready_indices = jnp.where(ready, size=n_ready)[0]

    # Fate decision
    fate_rolls = jax.random.uniform(k1, (n_ready,))
    is_output_fate = fate_rolls < prob_output
    is_recycle_fate = ~is_output_fate

    n_recycle = int(jnp.sum(is_recycle_fate))
    n_output = int(jnp.sum(is_output_fate))

    # ── Recycled cells → CB slots (vectorized scatter) ──
    if n_recycle > 0:
        recycle_ready_idx = jnp.where(is_recycle_fate, size=n_recycle)[0]
        recycle_cc_indices = ready_indices[recycle_ready_idx]
        cb_slots = allocate_slots(cbs.alive, n_recycle)
        valid = cb_slots >= 0
        safe_slot = jnp.maximum(cb_slots, 0)

        # Hill function
        contacts = ccs.n_fdc_contacts[recycle_cc_indices].astype(jnp.float32)
        hill = contacts ** n_div_hill_n / (
            contacts ** n_div_hill_n + n_div_hill_k ** n_div_hill_n + 1e-8
        )
        n_divs = (n_div_min + (n_div_max - n_div_min) * hill).astype(jnp.int32)

        cbs = cbs._replace(
            position=cbs.position.at[safe_slot].set(
                jnp.where(valid[:, None], ccs.position[recycle_cc_indices], cbs.position[safe_slot])
            ),
            polarity=cbs.polarity.at[safe_slot].set(
                jnp.where(valid[:, None], ccs.polarity[recycle_cc_indices], cbs.polarity[safe_slot])
            ),
            sequence=cbs.sequence.at[safe_slot].set(
                jnp.where(valid[:, None], ccs.sequence[recycle_cc_indices], cbs.sequence[safe_slot])
            ),
            affinity=cbs.affinity.at[safe_slot].set(
                jnp.where(valid, ccs.affinity[recycle_cc_indices], cbs.affinity[safe_slot])
            ),
            phase=cbs.phase.at[safe_slot].set(
                jnp.where(valid, CB_G1, cbs.phase[safe_slot])
            ),
            phase_clock=cbs.phase_clock.at[safe_slot].set(
                jnp.where(valid, 0.0, cbs.phase_clock[safe_slot])
            ),
            remaining_divisions=cbs.remaining_divisions.at[safe_slot].set(
                jnp.where(valid, n_divs, cbs.remaining_divisions[safe_slot])
            ),
            clone_id=cbs.clone_id.at[safe_slot].set(
                jnp.where(valid, ccs.clone_id[recycle_cc_indices], cbs.clone_id[safe_slot])
            ),
            responsive_cxcl12=cbs.responsive_cxcl12.at[safe_slot].set(
                jnp.where(valid, True, cbs.responsive_cxcl12[safe_slot])
            ),
            responsive_cxcl13=cbs.responsive_cxcl13.at[safe_slot].set(
                jnp.where(valid, True, cbs.responsive_cxcl13[safe_slot])
            ),
            alive=cbs.alive.at[safe_slot].set(
                jnp.where(valid, True, cbs.alive[safe_slot])
            ),
        )

        # Update grid: CC → CB
        pos = ccs.position[recycle_cc_indices]
        pos_flat = pos[:, 0] * G * G + pos[:, 1] * G + pos[:, 2]
        grid_type_flat = grid_cell_type.ravel()
        grid_id_flat = grid_cell_id.ravel()
        grid_type_flat = grid_type_flat.at[pos_flat].set(
            jnp.where(valid, CENTROBLAST, grid_type_flat[pos_flat])
        )
        grid_id_flat = grid_id_flat.at[pos_flat].set(
            jnp.where(valid, safe_slot, grid_id_flat[pos_flat])
        )
        grid_cell_type = grid_type_flat.reshape(G, G, G).astype(jnp.int8)
        grid_cell_id = grid_id_flat.reshape(G, G, G)

    # ── Output cells → output slots (vectorized scatter) ──
    if n_output > 0:
        output_ready_idx = jnp.where(is_output_fate, size=n_output)[0]
        output_cc_indices = ready_indices[output_ready_idx]
        out_slots = allocate_slots(outputs.alive, n_output)
        valid_out = out_slots >= 0
        safe_out = jnp.maximum(out_slots, 0)

        outputs = outputs._replace(
            position=outputs.position.at[safe_out].set(
                jnp.where(valid_out[:, None], ccs.position[output_cc_indices], outputs.position[safe_out])
            ),
            polarity=outputs.polarity.at[safe_out].set(
                jnp.where(valid_out[:, None], ccs.polarity[output_cc_indices], outputs.polarity[safe_out])
            ),
            sequence=outputs.sequence.at[safe_out].set(
                jnp.where(valid_out[:, None], ccs.sequence[output_cc_indices], outputs.sequence[safe_out])
            ),
            affinity=outputs.affinity.at[safe_out].set(
                jnp.where(valid_out, ccs.affinity[output_cc_indices], outputs.affinity[safe_out])
            ),
            clone_id=outputs.clone_id.at[safe_out].set(
                jnp.where(valid_out, ccs.clone_id[output_cc_indices], outputs.clone_id[safe_out])
            ),
            alive=outputs.alive.at[safe_out].set(
                jnp.where(valid_out, True, outputs.alive[safe_out])
            ),
        )

    # Kill differentiated CCs
    new_cc_alive = ccs.alive.at[ready_indices].set(False)
    ccs = ccs._replace(alive=new_cc_alive)

    return cbs, ccs, outputs, grid_cell_type, grid_cell_id


# ─── Block 10: Founder Cell Inflow ──────────────────────────────────


def apply_inflow(
    cbs: CentroblastState,
    current_time: float,
    antigen: jnp.ndarray,
    config_inflow_hours: float,
    config_n_founders: int,
    config_hamming_min: int,
    config_hamming_max: int,
    config_founder_divisions: int,
    config_gamma: float,
    config_eta: float,
    n_timesteps_total: int,
    dt: float,
    rng_key: jnp.ndarray,
    grid_cell_type: jnp.ndarray,
    sphere_mask: jnp.ndarray,
) -> tuple:
    """Add founder cells — vectorized scatter, early exit."""
    L = antigen.shape[0]
    G = grid_cell_type.shape[0]

    if current_time > config_inflow_hours:
        return cbs, grid_cell_type

    inflow_steps = int(config_inflow_hours / dt)
    founders_per_step = max(1, config_n_founders // inflow_steps)
    n = min(founders_per_step, 10)

    k1, k2, k3, k4 = jax.random.split(rng_key, 4)

    free_slots = allocate_slots(cbs.alive, n)
    slot_valid = free_slots >= 0
    safe_slots = jnp.maximum(free_slots, 0)

    # Create founders
    seqs = create_founders_at_distance(
        n, antigen, config_hamming_min, config_hamming_max, k1,
    )
    affs = batch_affinity(seqs, antigen, config_gamma, config_eta)

    # DZ positions
    center = G // 2
    x_coords = jnp.arange(G)
    dz_mask = x_coords[:, None, None] < center
    valid = sphere_mask & dz_mask & (grid_cell_type == EMPTY)

    valid_flat = valid.ravel()
    all_indices = jnp.arange(valid_flat.shape[0])
    probs = valid_flat.astype(jnp.float32)
    probs = probs / jnp.maximum(probs.sum(), 1.0)
    chosen_flat = jax.random.choice(k3, all_indices, shape=(n,), replace=False, p=probs)

    positions = jnp.stack([
        chosen_flat // (G * G),
        (chosen_flat % (G * G)) // G,
        chosen_flat % G,
    ], axis=-1).astype(jnp.int32)

    pols = jax.random.normal(k2, (n, 3))
    pol_norms = jnp.linalg.norm(pols, axis=-1, keepdims=True)
    pols = pols / jnp.maximum(pol_norms, 1e-8)
    clone_ids = jax.random.randint(k4, (n,), 0, 100000)

    # Vectorized scatter
    cbs = cbs._replace(
        position=cbs.position.at[safe_slots].set(
            jnp.where(slot_valid[:, None], positions, cbs.position[safe_slots])
        ),
        polarity=cbs.polarity.at[safe_slots].set(
            jnp.where(slot_valid[:, None], pols, cbs.polarity[safe_slots])
        ),
        sequence=cbs.sequence.at[safe_slots].set(
            jnp.where(slot_valid[:, None], seqs, cbs.sequence[safe_slots])
        ),
        affinity=cbs.affinity.at[safe_slots].set(
            jnp.where(slot_valid, affs, cbs.affinity[safe_slots])
        ),
        phase=cbs.phase.at[safe_slots].set(
            jnp.where(slot_valid, CB_G1, cbs.phase[safe_slots])
        ),
        phase_clock=cbs.phase_clock.at[safe_slots].set(
            jnp.where(slot_valid, 0.0, cbs.phase_clock[safe_slots])
        ),
        remaining_divisions=cbs.remaining_divisions.at[safe_slots].set(
            jnp.where(slot_valid, config_founder_divisions, cbs.remaining_divisions[safe_slots])
        ),
        clone_id=cbs.clone_id.at[safe_slots].set(
            jnp.where(slot_valid, clone_ids, cbs.clone_id[safe_slots])
        ),
        responsive_cxcl12=cbs.responsive_cxcl12.at[safe_slots].set(
            jnp.where(slot_valid, True, cbs.responsive_cxcl12[safe_slots])
        ),
        responsive_cxcl13=cbs.responsive_cxcl13.at[safe_slots].set(
            jnp.where(slot_valid, True, cbs.responsive_cxcl13[safe_slots])
        ),
        alive=cbs.alive.at[safe_slots].set(
            jnp.where(slot_valid, True, cbs.alive[safe_slots])
        ),
    )

    pos_flat = positions[:, 0] * G * G + positions[:, 1] * G + positions[:, 2]
    grid_type_flat = grid_cell_type.ravel()
    grid_type_flat = grid_type_flat.at[pos_flat].set(
        jnp.where(slot_valid, CENTROBLAST, grid_type_flat[pos_flat])
    )
    grid_cell_type = grid_type_flat.reshape(G, G, G).astype(jnp.int8)

    return cbs, grid_cell_type
