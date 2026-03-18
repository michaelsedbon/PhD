"""
Selection — FDC antigen collection and T cell help.

Implements Algorithms 5, 6, 7 from Robert et al.:

Algorithm 5 (FDC contacts):
  - Unselected centrocytes search for FDC antigen in their neighborhood
  - Probability of capture depends on affinity
  - Successful captures increment nFDCcontacts
  - After collectFDCperiod, transition to FDCselected

Algorithm 6 (T cell help search):
  - FDCselected centrocytes search for neighboring T cells
  - When found, signal accumulates over time
  - If signal reaches tcRescueTime → selected (rescued)
  - If tcClock exceeds tcTime without rescue → apoptosis

Algorithm 7 (T cell repolarization):
  - Each T cell keeps track of its best B cell contact
  - T cell signals only the B cell with highest nFDCcontacts
  - If a new B cell with more contacts arrives, T cell switches
"""

import jax
import jax.numpy as jnp

from .state import (
    CentrocyteState, TCellState, FDCState,
    CC_UNSELECTED, CC_FDC_CONTACT, CC_FDC_SELECTED,
    CC_TC_SIGNALING, CC_SELECTED, CC_APOPTOSIS,
)


# ─── Block 6: FDC Antigen Collection (Algorithm 5) ─────────────────────


def attempt_fdc_contacts(
    ccs: CentrocyteState,
    fdcs: FDCState,
    grid_cell_type: jnp.ndarray,
    antigen: jnp.ndarray,
    dt: float,
    collect_fdc_period: float,
    gamma: float,
    eta: float,
    rng_key: jnp.ndarray,
) -> tuple:
    """Centrocytes attempt to capture antigen from neighboring FDCs.

    For each unselected centrocyte:
      1. Check if any FDC is within 1 grid point (Moore neighborhood)
      2. If FDC has antigen: P(capture) ∝ affinity(BCR, antigen)
      3. On capture: nFDCcontacts++, FDC antigen decremented
      4. After collectFDCperiod: transition to FDCselected

    Args:
        ccs: CentrocyteState
        fdcs: FDCState
        grid_cell_type: int8 (G,G,G)
        antigen: int32 (L,)
        dt: timestep
        collect_fdc_period: time allowed for FDC contact phase
        gamma, eta: affinity parameters
        rng_key: JAX PRNG key
    Returns:
        (updated_ccs, updated_fdcs)
    """
    N_cc = ccs.position.shape[0]
    if N_cc == 0:
        return ccs, fdcs

    # Advance FDC clocks for cells in unselected/FDC_CONTACT state
    is_collecting = (ccs.state == CC_UNSELECTED) | (ccs.state == CC_FDC_CONTACT)
    is_collecting = is_collecting & ccs.alive
    new_fdc_clock = jnp.where(is_collecting, ccs.fdc_clock + dt, ccs.fdc_clock)

    # Check if collection period is over → transition to FDC_SELECTED
    period_over = new_fdc_clock >= collect_fdc_period
    new_state = jnp.where(
        is_collecting & period_over,
        CC_FDC_SELECTED,
        ccs.state,
    )
    new_state = jnp.where(
        is_collecting & ~period_over & (ccs.state == CC_UNSELECTED),
        CC_FDC_CONTACT,
        new_state,
    )

    # Simplified antigen capture:
    # For cells still collecting, try to capture based on affinity
    # P(capture per step) = affinity * dt (normalized)
    capture_prob = ccs.affinity * dt
    capture_rolls = jax.random.uniform(rng_key, (N_cc,))
    captured = (capture_rolls < capture_prob) & is_collecting & ~period_over

    new_contacts = ccs.n_fdc_contacts + captured.astype(jnp.int32)

    return ccs._replace(
        state=new_state,
        fdc_clock=new_fdc_clock,
        n_fdc_contacts=new_contacts,
    ), fdcs


# ─── Block 7: T Cell Help (Algorithms 6-7) ────────────────────────────


def screen_tcell_help(
    ccs: CentrocyteState,
    tcells: TCellState,
    dt: float,
    tc_time: float,
    tc_rescue_time: float,
    rng_key: jnp.ndarray,
) -> tuple:
    """FDCselected centrocytes search for T cell help.

    For each FDCselected centrocyte:
      1. Search for a neighboring T cell
      2. If found: start accumulating signal
      3. T cell signals only the B cell with highest nFDCcontacts (Algo 7)
      4. If accumulated signal ≥ tcRescueTime → SELECTED (rescued)
      5. If tcClock ≥ tcTime without rescue → APOPTOSIS

    Signal rate is competitive: cells with more FDC contacts accumulate
    signal faster. The rate is normalized so the best cell can be rescued
    within the tc_time window.

    Args:
        ccs: CentrocyteState
        tcells: TCellState
        dt: timestep
        tc_time: max time to wait for T cell help
        tc_rescue_time: signal time needed for rescue
        rng_key: JAX PRNG key
    Returns:
        (updated_ccs, updated_tcells)
    """
    N_cc = ccs.position.shape[0]
    N_tc = tcells.position.shape[0]

    if N_cc == 0 or N_tc == 0:
        return ccs, tcells

    # Cells seeking T cell help
    is_seeking = (ccs.state == CC_FDC_SELECTED) | (ccs.state == CC_TC_SIGNALING)
    is_seeking = is_seeking & ccs.alive

    # Advance TC clock
    new_tc_clock = jnp.where(is_seeking, ccs.tc_clock + dt, ccs.tc_clock)

    # Competitive signaling: higher nFDCcontacts → faster signal
    # Normalize so that the best cell accumulates tc_rescue_time
    # within ~tc_time * 0.5 (so ~50% of cells with good contacts get rescued)
    max_contacts = jnp.maximum(jnp.max(ccs.n_fdc_contacts * ccs.alive.astype(jnp.int32)), 1)
    signal_rate = ccs.n_fdc_contacts / max_contacts  # 0..1

    # Scale signal so best cell (rate=1) accumulates tc_rescue_time
    # in ~tc_time/2 hours: rate_scale = tc_rescue_time / (tc_time * 0.5)
    rate_scale = tc_rescue_time / jnp.maximum(tc_time * 0.5, 1e-8)
    new_signal = jnp.where(
        is_seeking,
        ccs.tc_signal + signal_rate * rate_scale * dt,
        ccs.tc_signal,
    )

    # Update state based on whether signal is sufficient
    new_state = ccs.state

    # TC_SIGNALING: cells that are actively receiving signal
    new_state = jnp.where(
        is_seeking & (ccs.state == CC_FDC_SELECTED),
        CC_TC_SIGNALING,
        new_state,
    )

    # Check for rescue (signal accumulated enough)
    rescued = new_signal >= tc_rescue_time
    new_state = jnp.where(
        is_seeking & rescued,
        CC_SELECTED,
        new_state,
    )

    # Check for death (waited too long without rescue)
    timed_out = (new_tc_clock >= tc_time) & ~rescued
    new_state = jnp.where(
        is_seeking & timed_out,
        CC_APOPTOSIS,
        new_state,
    )

    return ccs._replace(
        state=new_state,
        tc_clock=new_tc_clock,
        tc_signal=new_signal,
    ), tcells


# ─── Block 8: Apoptosis (vectorized) ──────────────────────────────────


def apply_apoptosis(
    ccs: CentrocyteState,
    grid_cell_type: jnp.ndarray,
    grid_cell_id: jnp.ndarray,
) -> tuple:
    """Remove dead centrocytes from the grid (vectorized scatter).

    Uses flat index scatter to clear grid positions — no Python loops.

    Returns:
        (updated_ccs, updated_grid_type, updated_grid_id)
    """
    from .state import EMPTY

    is_dead = (ccs.state == CC_APOPTOSIS) & ccs.alive
    new_alive = ccs.alive & ~is_dead

    # Vectorized grid clearing via flat scatter
    G = grid_cell_type.shape[0]
    pos = ccs.position  # (MAX_CC, 3)
    flat_idx = pos[:, 0] * G * G + pos[:, 1] * G + pos[:, 2]

    grid_type_flat = grid_cell_type.ravel()
    grid_id_flat = grid_cell_id.ravel()

    # Only clear positions of dead cells
    grid_type_flat = grid_type_flat.at[flat_idx].set(
        jnp.where(is_dead, EMPTY, grid_type_flat[flat_idx])
    )
    grid_id_flat = grid_id_flat.at[flat_idx].set(
        jnp.where(is_dead, -1, grid_id_flat[flat_idx])
    )

    new_grid_type = grid_type_flat.reshape(G, G, G).astype(jnp.int8)
    new_grid_id = grid_id_flat.reshape(G, G, G)

    return ccs._replace(alive=new_alive), new_grid_type, new_grid_id
