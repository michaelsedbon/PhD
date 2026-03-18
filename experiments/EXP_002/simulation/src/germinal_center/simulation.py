"""
Simulation — main loop orchestrating all 11 blocks.
GPU-optimized using padded fixed-size arrays.

All blocks operate on fixed-size padded arrays.
No array concatenation, no dynamic shapes.
"""

import jax
import jax.numpy as jnp
from tqdm import trange

from .config import GCConfig
from .state import (
    GCState, count_cells,
    CENTROBLAST, CENTROCYTE, TCELL, FDC,
)
from .chemotaxis import produce_chemokine, diffuse_3d, update_receptor_sensitivity, compute_gradient_at
from .movement import update_polarity, move_cells_parallel
from .cell_cycle import progress_phases, find_dividing_cells, divide_and_mutate, find_transition_to_cc, transition_cb_to_cc
from .selection import attempt_fdc_contacts, screen_tcell_help, apply_apoptosis
from .differentiation import process_differentiation, apply_inflow
from .analysis import snapshot


def step(state: GCState, config: GCConfig, rng_key: jnp.ndarray) -> GCState:
    """Execute one simulation timestep (all 11 blocks).

    Uses padded fixed-size arrays throughout. No concatenation or dynamic shapes.
    """
    k = jax.random.split(rng_key, 10)
    dt = config.dt
    phase_durations = jnp.array([config.phase_g1, config.phase_s, config.phase_g2, config.phase_m])

    cbs = state.centroblasts
    ccs = state.centrocytes
    tcells = state.tcells
    fdcs = state.fdcs
    grid_type = state.grid_cell_type
    grid_id = state.grid_cell_id

    # ── Block 1-2: Chemokine production + diffusion ──
    cxcl12 = produce_chemokine(
        state.cxcl12, state.stromal.position[state.stromal.alive],
        config.cxcl12_production, dt,
    )
    cxcl13 = produce_chemokine(
        state.cxcl13, fdcs.position[fdcs.alive],
        config.cxcl13_production, dt,
    )
    cxcl12 = diffuse_3d(cxcl12, config.diffusion_alpha, state.sphere_mask)
    cxcl13 = diffuse_3d(cxcl13, config.diffusion_alpha, state.sphere_mask)

    # ── Block 3: Receptor sensitivity ──
    cbs = cbs._replace(
        responsive_cxcl12=update_receptor_sensitivity(
            cbs.position, cbs.responsive_cxcl12, cxcl12,
            config.desensitize_threshold, config.resensitize_threshold,
        ),
        responsive_cxcl13=update_receptor_sensitivity(
            cbs.position, cbs.responsive_cxcl13, cxcl13,
            config.desensitize_threshold, config.resensitize_threshold,
        ),
    )

    # ── Block 4: Movement (vectorized parallel) ──
    # CB movement (CXCL12 gradient → DZ)
    cb_gradient = compute_gradient_at(cxcl12, cbs.position)
    cb_polarity = update_polarity(
        cbs.polarity, cb_gradient, cbs.responsive_cxcl12, cbs.alive,
        k[0], config.persistence_time, config.chemo_weight,
    )
    cbs = cbs._replace(polarity=cb_polarity)
    new_cb_pos, grid_type, grid_id = move_cells_parallel(
        cbs.position, cbs.polarity, cbs.alive,
        grid_type, grid_id, state.sphere_mask, CENTROBLAST, k[1],
    )
    cbs = cbs._replace(position=new_cb_pos)

    # CC movement (CXCL13 gradient → LZ)
    cc_gradient = compute_gradient_at(cxcl13, ccs.position)
    cc_polarity = update_polarity(
        ccs.polarity, cc_gradient, ccs.responsive_cxcl13, ccs.alive,
        k[2], config.persistence_time, config.chemo_weight,
    )
    ccs = ccs._replace(polarity=cc_polarity)
    new_cc_pos, grid_type, grid_id = move_cells_parallel(
        ccs.position, ccs.polarity, ccs.alive,
        grid_type, grid_id, state.sphere_mask, CENTROCYTE, k[3],
    )
    ccs = ccs._replace(position=new_cc_pos)

    # TC movement
    tc_polarity = update_polarity(
        tcells.polarity, jnp.zeros_like(tcells.polarity), 
        jnp.zeros(tcells.alive.shape, dtype=jnp.bool_), tcells.alive,
        k[4], config.persistence_time, 0.0,
    )
    tcells = tcells._replace(polarity=tc_polarity)
    new_tc_pos, grid_type, grid_id = move_cells_parallel(
        tcells.position, tcells.polarity, tcells.alive,
        grid_type, grid_id, state.sphere_mask, TCELL, k[5],
    )
    tcells = tcells._replace(position=new_tc_pos)

    # ── Block 5: Cell cycle progression ──
    cbs = progress_phases(cbs, dt, phase_durations)

    # ── Block 5b: Division ──
    dividing = find_dividing_cells(cbs)
    cbs, grid_type, grid_id = divide_and_mutate(
        cbs, dividing, state.antigen, k[6],
        config.mutation_prob, config.affinity_gamma, config.affinity_eta,
        grid_type, grid_id, state.sphere_mask,
    )

    # ── Block 5c: CB → CC transition ──
    transition_mask = find_transition_to_cc(cbs)
    cbs, ccs, grid_type, grid_id = transition_cb_to_cc(
        cbs, ccs, transition_mask, grid_type, grid_id,
    )

    # ── Block 6: FDC antigen collection ──
    ccs, fdcs = attempt_fdc_contacts(
        ccs, fdcs, grid_type, state.antigen,
        dt, config.collect_fdc_period,
        config.affinity_gamma, config.affinity_eta, k[7],
    )

    # ── Block 7: T cell help ──
    ccs, tcells = screen_tcell_help(
        ccs, tcells, dt, config.tc_time, config.tc_rescue_time, k[8],
    )

    # ── Block 8: Apoptosis ──
    ccs, grid_type, grid_id = apply_apoptosis(ccs, grid_type, grid_id)

    # ── Block 9: Differentiation (recycling + output) ──
    cbs, ccs, outputs, grid_type, grid_id = process_differentiation(
        cbs, ccs, state.output_cells,
        dt, config.diff_delay, config.prob_output,
        config.n_div_min, config.n_div_max,
        config.n_div_hill_n, config.n_div_hill_k,
        k[9], grid_type, grid_id,
    )

    # ── Block 10: Founder inflow ──
    k_inflow = jax.random.fold_in(rng_key, 999)
    cbs, grid_type = apply_inflow(
        cbs, state.time,
        state.antigen, config.inflow_hours,
        config.n_founders, config.initial_hamming_min, config.initial_hamming_max,
        config.founder_divisions, config.affinity_gamma, config.affinity_eta,
        config.n_timesteps, dt, k_inflow, grid_type, state.sphere_mask,
    )

    # ── Advance time ──
    new_time = state.time + dt

    return state._replace(
        grid_cell_type=grid_type,
        grid_cell_id=grid_id,
        cxcl12=cxcl12,
        cxcl13=cxcl13,
        centroblasts=cbs,
        centrocytes=ccs,
        tcells=tcells,
        fdcs=fdcs,
        output_cells=outputs,
        time=new_time,
    )


def run_simulation(config: GCConfig, seed: int = 42) -> list:
    """Run the full simulation and return history of snapshots."""
    from .initialization import initialize_gc

    key = jax.random.PRNGKey(seed)
    state = initialize_gc(config, key)
    history = [snapshot(state)]

    n_steps = config.n_timesteps
    print(f"Running {n_steps} timesteps ({config.total_days} simulated days)")
    print(f"Snapshot every {config.snapshot_interval} steps")

    for t in trange(n_steps, desc="Simulating GC"):
        key, step_key = jax.random.split(key)
        state = step(state, config, step_key)
        if (t + 1) % config.snapshot_interval == 0:
            history.append(snapshot(state))

    return history
