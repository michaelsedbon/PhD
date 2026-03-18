"""
Cell cycle — centroblast division machinery (GPU-optimized).

Hybrid approach: uses int(jnp.sum()) for early exit (1 cheap sync),
then vectorized scatter (no Python for-loops) for the actual work.
"""

import jax
import jax.numpy as jnp

from .state import (
    CentroblastState, CentrocyteState,
    CB_G1, CB_S, CB_G2, CB_M,
    CC_UNSELECTED, CENTROBLAST, CENTROCYTE,
    MAX_CB, MAX_CC,
    allocate_slots,
)
from .affinity import mutate_sequence, batch_affinity


# ─── Phase progression (already vectorized) ─────────────────────────────


def progress_phases(
    cbs: CentroblastState,
    dt: float,
    phase_durations: jnp.ndarray,
) -> CentroblastState:
    """Advance cell cycle timers (vectorized)."""
    new_clock = cbs.phase_clock + dt
    current_duration = phase_durations[cbs.phase]
    phase_complete = new_clock >= current_duration

    next_phase = (cbs.phase + 1) % 4
    new_phase = jnp.where(phase_complete & cbs.alive, next_phase, cbs.phase)
    new_clock = jnp.where(phase_complete & cbs.alive, 0.0, new_clock)
    new_clock = jnp.where(cbs.alive, new_clock, cbs.phase_clock)

    return cbs._replace(phase=new_phase, phase_clock=new_clock)


# ─── Division detection ────────────────────────────────────────────────


def find_dividing_cells(cbs: CentroblastState) -> jnp.ndarray:
    """Find centroblasts that should divide. Returns bool (MAX_CB,)."""
    return (
        (cbs.phase == CB_G1) &
        (cbs.phase_clock == 0.0) &
        (cbs.remaining_divisions > 0) &
        cbs.alive
    )


# ─── Division + Mutation (vectorized scatter, 1 sync for early exit) ──


def divide_and_mutate(
    cbs: CentroblastState,
    dividing_mask: jnp.ndarray,
    antigen: jnp.ndarray,
    rng_key: jnp.ndarray,
    mutation_prob: float,
    gamma: float,
    eta: float,
    grid_cell_type: jnp.ndarray,
    grid_cell_id: jnp.ndarray,
    sphere_mask: jnp.ndarray,
) -> tuple:
    """Divide centroblasts — vectorized scatter, no Python for-loops.

    Uses 1 sync point (int(jnp.sum())) for early exit,
    then fully vectorized scatter for actual work.
    """
    n_dividing = int(jnp.sum(dividing_mask))
    if n_dividing == 0:
        return cbs, grid_cell_type, grid_cell_id

    L = antigen.shape[0]
    k1, k2, k3 = jax.random.split(rng_key, 3)

    # Get dividing indices and free slots
    dividing_indices = jnp.where(dividing_mask, size=n_dividing)[0]
    free_slots = allocate_slots(cbs.alive, n_dividing)
    valid = free_slots >= 0

    # Decrement parent remaining_divisions
    new_remaining = cbs.remaining_divisions - dividing_mask.astype(jnp.int32)

    # Create daughter data (all at once via vmap)
    parent_seqs = cbs.sequence[dividing_indices]
    should_mutate = jax.random.uniform(k1, (n_dividing,)) < mutation_prob
    mut_keys = jax.random.split(k2, n_dividing)

    def _maybe_mutate(seq, key, do_mutate):
        mutated = mutate_sequence(seq, key, 10, L)
        return jnp.where(do_mutate, mutated, seq)

    daughter_seqs = jax.vmap(_maybe_mutate)(parent_seqs, mut_keys, should_mutate)
    daughter_affs = batch_affinity(daughter_seqs, antigen, gamma, eta)

    daughter_pols = jax.random.normal(k3, (n_dividing, 3))
    pol_norms = jnp.linalg.norm(daughter_pols, axis=-1, keepdims=True)
    daughter_pols = daughter_pols / jnp.maximum(pol_norms, 1e-8)

    daughter_pos = cbs.position[dividing_indices]
    daughter_remaining = cbs.remaining_divisions[dividing_indices] - 1
    daughter_clone_id = cbs.clone_id[dividing_indices]

    # Vectorized scatter into free slots (no Python for-loop)
    safe_slots = jnp.maximum(free_slots, 0)

    # First: decrement parents
    cbs = cbs._replace(remaining_divisions=new_remaining)

    # Then: scatter daughters into free slots
    cbs = cbs._replace(
        position=cbs.position.at[safe_slots].set(
            jnp.where(valid[:, None], daughter_pos, cbs.position[safe_slots])
        ),
        polarity=cbs.polarity.at[safe_slots].set(
            jnp.where(valid[:, None], daughter_pols, cbs.polarity[safe_slots])
        ),
        sequence=cbs.sequence.at[safe_slots].set(
            jnp.where(valid[:, None], daughter_seqs, cbs.sequence[safe_slots])
        ),
        affinity=cbs.affinity.at[safe_slots].set(
            jnp.where(valid, daughter_affs, cbs.affinity[safe_slots])
        ),
        phase=cbs.phase.at[safe_slots].set(
            jnp.where(valid, CB_G1, cbs.phase[safe_slots])
        ),
        phase_clock=cbs.phase_clock.at[safe_slots].set(
            jnp.where(valid, 0.0, cbs.phase_clock[safe_slots])
        ),
        remaining_divisions=cbs.remaining_divisions.at[safe_slots].set(
            jnp.where(valid, daughter_remaining, cbs.remaining_divisions[safe_slots])
        ),
        clone_id=cbs.clone_id.at[safe_slots].set(
            jnp.where(valid, daughter_clone_id, cbs.clone_id[safe_slots])
        ),
        responsive_cxcl12=cbs.responsive_cxcl12.at[safe_slots].set(
            jnp.where(valid, True, cbs.responsive_cxcl12[safe_slots])
        ),
        responsive_cxcl13=cbs.responsive_cxcl13.at[safe_slots].set(
            jnp.where(valid, True, cbs.responsive_cxcl13[safe_slots])
        ),
        alive=cbs.alive.at[safe_slots].set(
            jnp.where(valid, True, cbs.alive[safe_slots])
        ),
    )

    return cbs, grid_cell_type, grid_cell_id


# ─── CB → CC transition (vectorized scatter, 1 sync) ────────────────


def find_transition_to_cc(cbs: CentroblastState) -> jnp.ndarray:
    """Find CBs that should become CCs. Returns bool (MAX_CB,)."""
    return (cbs.remaining_divisions <= 0) & cbs.alive


def transition_cb_to_cc(
    cbs: CentroblastState,
    ccs: CentrocyteState,
    transition_mask: jnp.ndarray,
    grid_cell_type: jnp.ndarray,
    grid_cell_id: jnp.ndarray,
) -> tuple:
    """Move CBs → CC slots — vectorized scatter, no Python for-loop."""
    n_transition = int(jnp.sum(transition_mask))
    if n_transition == 0:
        return cbs, ccs, grid_cell_type, grid_cell_id

    G = grid_cell_type.shape[0]

    trans_indices = jnp.where(transition_mask, size=n_transition)[0]
    cc_slots = allocate_slots(ccs.alive, n_transition)
    valid = cc_slots >= 0
    safe_cc_slot = jnp.maximum(cc_slots, 0)

    # Read CB data
    cb_pos = cbs.position[trans_indices]
    cb_pol = cbs.polarity[trans_indices]
    cb_seq = cbs.sequence[trans_indices]
    cb_aff = cbs.affinity[trans_indices]
    cb_cid = cbs.clone_id[trans_indices]

    # Vectorized scatter into CC slots
    ccs = ccs._replace(
        position=ccs.position.at[safe_cc_slot].set(
            jnp.where(valid[:, None], cb_pos, ccs.position[safe_cc_slot])
        ),
        polarity=ccs.polarity.at[safe_cc_slot].set(
            jnp.where(valid[:, None], cb_pol, ccs.polarity[safe_cc_slot])
        ),
        sequence=ccs.sequence.at[safe_cc_slot].set(
            jnp.where(valid[:, None], cb_seq, ccs.sequence[safe_cc_slot])
        ),
        affinity=ccs.affinity.at[safe_cc_slot].set(
            jnp.where(valid, cb_aff, ccs.affinity[safe_cc_slot])
        ),
        state=ccs.state.at[safe_cc_slot].set(
            jnp.where(valid, CC_UNSELECTED, ccs.state[safe_cc_slot])
        ),
        fdc_clock=ccs.fdc_clock.at[safe_cc_slot].set(
            jnp.where(valid, 0.0, ccs.fdc_clock[safe_cc_slot])
        ),
        tc_clock=ccs.tc_clock.at[safe_cc_slot].set(
            jnp.where(valid, 0.0, ccs.tc_clock[safe_cc_slot])
        ),
        tc_signal=ccs.tc_signal.at[safe_cc_slot].set(
            jnp.where(valid, 0.0, ccs.tc_signal[safe_cc_slot])
        ),
        n_fdc_contacts=ccs.n_fdc_contacts.at[safe_cc_slot].set(
            jnp.where(valid, 0, ccs.n_fdc_contacts[safe_cc_slot])
        ),
        diff_clock=ccs.diff_clock.at[safe_cc_slot].set(
            jnp.where(valid, 0.0, ccs.diff_clock[safe_cc_slot])
        ),
        clone_id=ccs.clone_id.at[safe_cc_slot].set(
            jnp.where(valid, cb_cid, ccs.clone_id[safe_cc_slot])
        ),
        responsive_cxcl12=ccs.responsive_cxcl12.at[safe_cc_slot].set(
            jnp.where(valid, True, ccs.responsive_cxcl12[safe_cc_slot])
        ),
        responsive_cxcl13=ccs.responsive_cxcl13.at[safe_cc_slot].set(
            jnp.where(valid, True, ccs.responsive_cxcl13[safe_cc_slot])
        ),
        alive=ccs.alive.at[safe_cc_slot].set(
            jnp.where(valid, True, ccs.alive[safe_cc_slot])
        ),
    )

    # Kill CBs
    new_cb_alive = cbs.alive.at[trans_indices].set(
        jnp.where(valid, False, cbs.alive[trans_indices])
    )
    cbs = cbs._replace(alive=new_cb_alive)

    # Update grid: CB → CC at positions
    pos_flat = cb_pos[:, 0] * G * G + cb_pos[:, 1] * G + cb_pos[:, 2]
    grid_type_flat = grid_cell_type.ravel()
    grid_id_flat = grid_cell_id.ravel()

    grid_type_flat = grid_type_flat.at[pos_flat].set(
        jnp.where(valid, CENTROCYTE, grid_type_flat[pos_flat])
    )
    grid_id_flat = grid_id_flat.at[pos_flat].set(
        jnp.where(valid, safe_cc_slot, grid_id_flat[pos_flat])
    )

    grid_cell_type = grid_type_flat.reshape(G, G, G).astype(jnp.int8)
    grid_cell_id = grid_id_flat.reshape(G, G, G)

    return cbs, ccs, grid_cell_type, grid_cell_id
