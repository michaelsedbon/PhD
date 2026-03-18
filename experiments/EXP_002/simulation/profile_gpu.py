"""
Per-block profiling script — run this on the server to identify bottlenecks.
Paste each section into a notebook cell or run directly.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/gc_simulation/src'))

import jax
import jax.numpy as jnp

from germinal_center.config import GCConfig
from germinal_center.state import count_cells, CENTROBLAST, CENTROCYTE, TCELL
from germinal_center.initialization import initialize_gc
from germinal_center.chemotaxis import produce_chemokine, diffuse_3d, update_receptor_sensitivity, compute_gradient_at
from germinal_center.movement import update_polarity, move_cells_parallel
from germinal_center.cell_cycle import progress_phases, find_dividing_cells, divide_and_mutate, find_transition_to_cc, transition_cb_to_cc
from germinal_center.selection import attempt_fdc_contacts, screen_tcell_help, apply_apoptosis
from germinal_center.differentiation import process_differentiation, apply_inflow
from germinal_center.simulation import step

config = GCConfig(dt=0.05, total_days=0.01)
key = jax.random.PRNGKey(42)
state = initialize_gc(config, key)

# Warmup
key, sk = jax.random.split(key)
state = step(state, config, sk)
jax.block_until_ready(state.grid_cell_type)
print(f"Backend: {jax.default_backend()}")
print(f"CB={int(jnp.sum(state.centroblasts.alive))}")

# ── 1. Pure step speed (no snapshots) ──
t0 = time.time()
for _ in range(50):
    key, sk = jax.random.split(key)
    state = step(state, config, sk)
jax.block_until_ready(state.grid_cell_type)
pure = time.time() - t0
print(f"\n=== PURE STEP: {pure/50*1000:.0f}ms/step ({50/pure:.1f} steps/s) ===")

# ── 2. Per-block profiling ──
dt = config.dt
pds = jnp.array([config.phase_g1, config.phase_s, config.phase_g2, config.phase_m])

results = {}
N = 20

# Chemokine production + diffusion
t0 = time.time()
for _ in range(N):
    c12 = produce_chemokine(state.cxcl12, state.stromal.position[state.stromal.alive], config.cxcl12_production, dt)
    c13 = produce_chemokine(state.cxcl13, state.fdcs.position[state.fdcs.alive], config.cxcl13_production, dt)
    c12 = diffuse_3d(c12, config.diffusion_alpha, state.sphere_mask)
    c13 = diffuse_3d(c13, config.diffusion_alpha, state.sphere_mask)
jax.block_until_ready(c12)
results['chemokines'] = (time.time()-t0)/N*1000

# CB Movement
key, k = jax.random.split(key)
ks = jax.random.split(k, N*2).reshape(N, 2, 2)
t0 = time.time()
for i in range(N):
    g = compute_gradient_at(state.cxcl12, state.centroblasts.position)
    p = update_polarity(state.centroblasts.polarity, g, state.centroblasts.responsive_cxcl12, state.centroblasts.alive, ks[i,0], config.persistence_time, config.chemo_weight)
    pos, gt, gi = move_cells_parallel(state.centroblasts.position, p, state.centroblasts.alive, state.grid_cell_type, state.grid_cell_id, state.sphere_mask, CENTROBLAST, ks[i,1])
jax.block_until_ready(pos)
results['movement_CB'] = (time.time()-t0)/N*1000

# CC Movement
t0 = time.time()
for i in range(N):
    g = compute_gradient_at(state.cxcl13, state.centrocytes.position)
    p = update_polarity(state.centrocytes.polarity, g, state.centrocytes.responsive_cxcl13, state.centrocytes.alive, ks[i,0], config.persistence_time, config.chemo_weight)
    pos, gt, gi = move_cells_parallel(state.centrocytes.position, p, state.centrocytes.alive, state.grid_cell_type, state.grid_cell_id, state.sphere_mask, CENTROCYTE, ks[i,1])
jax.block_until_ready(pos)
results['movement_CC'] = (time.time()-t0)/N*1000

# TC Movement
t0 = time.time()
for i in range(N):
    p = update_polarity(state.tcells.polarity, jnp.zeros_like(state.tcells.polarity), jnp.zeros(state.tcells.alive.shape, dtype=jnp.bool_), state.tcells.alive, ks[i,0], config.persistence_time, 0.0)
    pos, gt, gi = move_cells_parallel(state.tcells.position, p, state.tcells.alive, state.grid_cell_type, state.grid_cell_id, state.sphere_mask, TCELL, ks[i,1])
jax.block_until_ready(pos)
results['movement_TC'] = (time.time()-t0)/N*1000

# Cell cycle
t0 = time.time()
for _ in range(N):
    cbs = progress_phases(state.centroblasts, dt, pds)
jax.block_until_ready(cbs.phase)
results['cell_cycle'] = (time.time()-t0)/N*1000

# Division
t0 = time.time()
for _ in range(N):
    dm = find_dividing_cells(state.centroblasts)
    cbs2, gt, gi = divide_and_mutate(state.centroblasts, dm, state.antigen, ks[0,0], config.mutation_prob, config.affinity_gamma, config.affinity_eta, state.grid_cell_type, state.grid_cell_id, state.sphere_mask)
jax.block_until_ready(cbs2.alive)
results['division'] = (time.time()-t0)/N*1000

# CB→CC transition
t0 = time.time()
for _ in range(N):
    tm = find_transition_to_cc(state.centroblasts)
    cb, cc, gt, gi = transition_cb_to_cc(state.centroblasts, state.centrocytes, tm, state.grid_cell_type, state.grid_cell_id)
jax.block_until_ready(cb.alive)
results['cb_to_cc'] = (time.time()-t0)/N*1000

# FDC contacts
t0 = time.time()
for _ in range(N):
    cc, fd = attempt_fdc_contacts(state.centrocytes, state.fdcs, state.grid_cell_type, state.antigen, dt, config.collect_fdc_period, config.affinity_gamma, config.affinity_eta, ks[0,0])
jax.block_until_ready(cc.state)
results['fdc_contacts'] = (time.time()-t0)/N*1000

# TC help
t0 = time.time()
for _ in range(N):
    cc, tc = screen_tcell_help(state.centrocytes, state.tcells, dt, config.tc_time, config.tc_rescue_time, ks[0,0])
jax.block_until_ready(cc.state)
results['tc_help'] = (time.time()-t0)/N*1000

# Apoptosis
t0 = time.time()
for _ in range(N):
    cc, gt, gi = apply_apoptosis(state.centrocytes, state.grid_cell_type, state.grid_cell_id)
jax.block_until_ready(gt)
results['apoptosis'] = (time.time()-t0)/N*1000

# Differentiation
t0 = time.time()
for _ in range(N):
    cb, cc, out, gt, gi = process_differentiation(state.centroblasts, state.centrocytes, state.output_cells, dt, config.diff_delay, config.prob_output, config.n_div_min, config.n_div_max, config.n_div_hill_n, config.n_div_hill_k, ks[0,0], state.grid_cell_type, state.grid_cell_id)
jax.block_until_ready(cb.alive)
results['differentiation'] = (time.time()-t0)/N*1000

# Inflow
key, ki = jax.random.split(key)
t0 = time.time()
for _ in range(N):
    cb, gt = apply_inflow(state.centroblasts, state.time, state.antigen, config.inflow_hours, config.n_founders, config.initial_hamming_min, config.initial_hamming_max, config.founder_divisions, config.affinity_gamma, config.affinity_eta, config.n_timesteps, dt, ki, state.grid_cell_type, state.sphere_mask)
jax.block_until_ready(cb.alive)
results['inflow'] = (time.time()-t0)/N*1000

# ── Results ──
print(f"\n{'Block':<20} {'ms/call':>8}")
print("-" * 30)
total = 0
for name, ms in sorted(results.items(), key=lambda x: -x[1]):
    print(f"{name:<20} {ms:8.1f}")
    total += ms
print("-" * 30)
print(f"{'SUM':<20} {total:8.1f}")
print(f"{'ACTUAL step':<20} {pure/50*1000:8.1f}")
print(f"{'Overhead':<20} {pure/50*1000-total:8.1f}")
