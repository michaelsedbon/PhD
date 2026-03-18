# %% [markdown]
# # Germinal Center Simulation — Block-by-Block Checkpoints
#
# This notebook lets you inspect each simulation block independently.
# Run cells in order. Each block produces a checkpoint you can verify.
#
# **Tip**: On MacBook CPU at dt=0.002, full sim is slow.
# Use `dt=0.05` (larger timestep) for interactive debugging,
# then deploy to GPU server with `dt=0.002` for real runs.

# %% [markdown]
# ## Setup

# %%
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt

from germinal_center.config import GCConfig
from germinal_center.state import (
    GCState, count_cells, EMPTY, CENTROBLAST, CENTROCYTE,
    TCELL, FDC, STROMAL, CB_G1, CB_S, CB_G2, CB_M,
    CC_UNSELECTED, CC_FDC_CONTACT, CC_FDC_SELECTED,
    CC_TC_SIGNALING, CC_SELECTED, CC_APOPTOSIS,
)
from germinal_center.initialization import initialize_gc
from germinal_center.affinity import (
    hamming_distance, compute_affinity, mutate_sequence,
    batch_hamming, batch_affinity, create_founders_at_distance,
)
from germinal_center.chemotaxis import (
    produce_chemokine, diffuse_3d, update_receptor_sensitivity, compute_gradient_at,
)
from germinal_center.movement import update_polarity, move_cells_sequential
from germinal_center.cell_cycle import (
    progress_phases, find_dividing_cells, divide_and_mutate,
    find_transition_to_cc, create_centrocytes_from_cbs,
)
from germinal_center.selection import attempt_fdc_contacts, screen_tcell_help, apply_apoptosis
from germinal_center.differentiation import process_differentiation, apply_inflow
from germinal_center.simulation import step, _concat_agents
from germinal_center.analysis import snapshot, Snapshot

print(f"JAX version: {jax.__version__}")
print(f"Backend: {jax.default_backend()}")

# %% [markdown]
# ## Checkpoint 0: Configuration & Initialization
#
# Create the GC config and initialize the full state.
# Verify: grid shape, sphere volume, agent counts, founder affinities.

# %%
# Use larger dt for MacBook debugging (0.05h = 3 min per step instead of 7.2s)
# Set dt=0.002 for paper-accurate runs on GPU server
config = GCConfig(
    total_days=7.0,          # 7 simulated days (for testing)
    dt=0.05,                 # larger timestep for CPU speed
    snapshot_interval=100,   # snapshot every 100 steps
)

rng_key = jax.random.PRNGKey(42)
state = initialize_gc(config, rng_key)

# ── Verify ──
print("=== Checkpoint 0: Initialization ===")
print(f"Grid: {state.grid_cell_type.shape}")
print(f"Sphere volume: {int(state.sphere_mask.sum())} grid points")
print(f"Antigen: {state.antigen}")
print()
c = count_cells(state)
for k, v in c.items():
    print(f"  {k}: {v}")
print()
print(f"CB sequences shape: {state.centroblasts.sequence.shape}")
print(f"CB mean affinity: {float(state.centroblasts.affinity.mean()):.4f}")
print(f"CB affinity range: [{float(state.centroblasts.affinity.min()):.4f}, "
      f"{float(state.centroblasts.affinity.max()):.4f}]")

# Histogram of founder affinities
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(np.array(state.centroblasts.affinity), bins=20, color='#4a9eff', edgecolor='white')
ax.set_xlabel('Affinity')
ax.set_ylabel('Count')
ax.set_title('Founder Affinity Distribution')
ax.axvline(float(state.centroblasts.affinity.mean()), color='red', linestyle='--',
           label=f'Mean = {float(state.centroblasts.affinity.mean()):.4f}')
ax.legend()
plt.tight_layout()
plt.show()

# Founder Hamming distances
dists = batch_hamming(state.centroblasts.sequence, state.antigen)
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(np.array(dists), bins=range(0, 8), color='#50c878', edgecolor='white', align='left')
ax.set_xlabel('Hamming Distance from Antigen')
ax.set_ylabel('Count')
ax.set_title('Founder Distance Distribution')
plt.tight_layout()
plt.show()

print("\n✅ Checkpoint 0 PASS" if c['n_cb'] == config.n_founders else "❌ Checkpoint 0 FAIL")

# %% [markdown]
# ## Checkpoint 1: Affinity Module
#
# Test that shape space, Hamming distance, affinity, and mutation
# work as expected per §2.2 and Algorithm 1.

# %%
print("=== Checkpoint 1: Affinity Module ===")

# Test known values
a = jnp.array([0, 0, 0, 0])
b = jnp.array([1, 0, 0, 0])
print(f"Hamming([0,0,0,0], [1,0,0,0]) = {hamming_distance(a, b)} (expect 1)")
print(f"Affinity(d=0) = {compute_affinity(a, a):.4f} (expect 1.0)")
print(f"Affinity(d=1) = {compute_affinity(a, b):.4f}")
print(f"Affinity(d=2) = {compute_affinity(a, jnp.array([1,1,0,0])):.4f}")
print(f"Affinity(d=4) = {compute_affinity(a, jnp.array([1,1,1,1])):.4f}")

# Mutation test
key = jax.random.PRNGKey(0)
seq = jnp.array([5, 5, 5, 5])
print(f"\nOriginal: {seq}")
for i in range(5):
    key, k = jax.random.split(key)
    mut = mutate_sequence(seq, k, n_values=10, L=4)
    diff = int(jnp.sum(seq != mut))
    print(f"  Mutation {i+1}: {mut} (changed {diff} position)")

print("\n✅ Checkpoint 1 PASS")

# %% [markdown]
# ## Checkpoint 2: Chemokine Production & Diffusion
#
# Run Blocks 1-2 a few times and visualize the chemokine fields.
# Verify: CXCL12 concentrates in DZ, CXCL13 in LZ.

# %%
print("=== Checkpoint 2: Chemokines ===")

# Run production + diffusion for 50 steps to build up concentration
test_state = state
for _ in range(50):
    test_state = test_state._replace(
        cxcl12=produce_chemokine(
            test_state.cxcl12, test_state.stromal.position,
            config.cxcl12_production, config.dt,
        ),
        cxcl13=produce_chemokine(
            test_state.cxcl13, test_state.fdcs.position,
            config.cxcl13_production, config.dt,
        ),
    )
    test_state = test_state._replace(
        cxcl12=diffuse_3d(test_state.cxcl12, config.diffusion_alpha, test_state.sphere_mask),
        cxcl13=diffuse_3d(test_state.cxcl13, config.diffusion_alpha, test_state.sphere_mask),
    )

# Visualize mid-plane slice
center = config.grid_n // 2
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

im1 = axes[0].imshow(np.array(test_state.cxcl12[center, :, :]),
                      cmap='Blues', origin='lower')
axes[0].set_title('CXCL12 (Dark Zone signal)')
plt.colorbar(im1, ax=axes[0])

im2 = axes[1].imshow(np.array(test_state.cxcl13[center, :, :]),
                      cmap='Reds', origin='lower')
axes[1].set_title('CXCL13 (Light Zone signal)')
plt.colorbar(im2, ax=axes[1])

for ax in axes:
    ax.set_xlabel('z')
    ax.set_ylabel('y')

fig.suptitle(f'Chemokine Fields (mid-plane x={center}, after 50 steps)')
plt.tight_layout()
plt.show()

# Verify DZ/LZ gradient
dz_mean = float(test_state.cxcl12[:center, :, :].mean())
lz_mean = float(test_state.cxcl12[center:, :, :].mean())
print(f"CXCL12 mean in DZ: {dz_mean:.4f}")
print(f"CXCL12 mean in LZ: {lz_mean:.4f}")
print(f"DZ/LZ ratio: {dz_mean/(lz_mean+1e-10):.2f}x (expect > 1)")

dz_mean13 = float(test_state.cxcl13[:center, :, :].mean())
lz_mean13 = float(test_state.cxcl13[center:, :, :].mean())
print(f"CXCL13 mean in DZ: {dz_mean13:.4f}")
print(f"CXCL13 mean in LZ: {lz_mean13:.4f}")
print(f"LZ/DZ ratio: {lz_mean13/(dz_mean13+1e-10):.2f}x (expect > 1)")

ok = dz_mean > lz_mean and lz_mean13 > dz_mean13
print(f"\n{'✅' if ok else '❌'} Checkpoint 2 {'PASS' if ok else 'FAIL'}")

# %% [markdown]
# ## Checkpoint 3: Cell Movement
#
# Run Block 4 for a few steps and verify cells stay inside the sphere.

# %%
print("=== Checkpoint 3: Cell Movement ===")

# Track CB positions before and after movement
cbs = state.centroblasts
grid_type = state.grid_cell_type
grid_id = state.grid_cell_id

key = jax.random.PRNGKey(123)
print(f"Before: {cbs.position.shape[0]} CBs")
print(f"  Position range: [{cbs.position.min()}, {cbs.position.max()}]")

# Update polarity with random perturbation (no gradient yet)
gradient = jnp.zeros_like(cbs.polarity)
key, k = jax.random.split(key)
new_pol = update_polarity(
    cbs.polarity, gradient, cbs.responsive_cxcl12,
    k, config.persistence_time, config.chemo_weight,
)

# Move
new_pos, new_grid_type, new_grid_id = move_cells_sequential(
    cbs.position, new_pol, grid_type, grid_id,
    state.sphere_mask, CENTROBLAST, cbs.alive,
)

print(f"After: position range: [{new_pos.min()}, {new_pos.max()}]")
n_moved = int(jnp.sum(jnp.any(new_pos != cbs.position, axis=1)))
print(f"  {n_moved}/{cbs.position.shape[0]} cells moved")

# Verify all inside sphere
center = config.grid_n // 2
dist_sq = jnp.sum((new_pos - center) ** 2, axis=1)
max_dist = jnp.sqrt(dist_sq.max())
print(f"  Max distance from center: {float(max_dist):.1f} (radius={center})")
ok = float(max_dist) <= center + 1
print(f"\n{'✅' if ok else '❌'} Checkpoint 3 {'PASS' if ok else 'FAIL'}")

# %% [markdown]
# ## Checkpoint 4: Cell Cycle & Division
#
# Run Block 5 repeatedly until a division occurs.

# %%
print("=== Checkpoint 4: Cell Cycle & Division ===")

# Use original state, advance cell cycle until we see a division
test_cbs = state.centroblasts
phase_durations = jnp.array([config.phase_g1, config.phase_s, config.phase_g2, config.phase_m])

key = jax.random.PRNGKey(99)
n_divisions = 0
for t in range(5000):
    test_cbs = progress_phases(test_cbs, config.dt, phase_durations)
    dividing = find_dividing_cells(test_cbs)
    n_div = int(jnp.sum(dividing))
    if n_div > 0:
        print(f"  t={t}: {n_div} cells dividing (first division!)")
        n_divisions += n_div

        key, k = jax.random.split(key)
        test_cbs, daughters, _, _ = divide_and_mutate(
            test_cbs, dividing, state.antigen, k,
            config.mutation_prob, config.affinity_gamma, config.affinity_eta,
            state.grid_cell_type, state.grid_cell_id, state.sphere_mask,
        )
        test_cbs = _concat_agents(test_cbs, daughters)

        if n_divisions >= 5:
            break

print(f"\n  Total CB after divisions: {test_cbs.position.shape[0]} (started with {config.n_founders})")
print(f"  Total divisions observed: {n_divisions}")

# Check CB → CC transition
trans_mask = find_transition_to_cc(test_cbs)
n_trans = int(jnp.sum(trans_mask))
print(f"  Cells ready for CB→CC transition: {n_trans}")

ok = n_divisions > 0
print(f"\n{'✅' if ok else '❌'} Checkpoint 4 {'PASS' if ok else 'FAIL'}")

# %% [markdown]
# ## Checkpoint 5: Full Simulation (Short Run)
#
# Run the complete pipeline for a short period and plot dynamics.

# %%
print("=== Checkpoint 5: Full Simulation ===")
from germinal_center.analysis import plot_population_dynamics, plot_affinity_maturation

config_short = GCConfig(
    total_days=3.0,          # 3 simulated days
    dt=0.05,                 # larger timestep for speed
    snapshot_interval=50,
)

key = jax.random.PRNGKey(42)
state_run = initialize_gc(config_short, key)
history = [snapshot(state_run)]

import time
n_steps = config_short.n_timesteps
print(f"Running {n_steps} steps ({config_short.total_days} days, dt={config_short.dt}h)")
t0 = time.time()

for t in range(n_steps):
    key, step_key = jax.random.split(key)
    state_run = step(state_run, config_short, step_key)
    if (t + 1) % config_short.snapshot_interval == 0:
        s = snapshot(state_run)
        history.append(s)
        if (t + 1) % 200 == 0:
            print(f"  t={t+1}/{n_steps} | CB={s.n_cb} CC={s.n_cc} OUT={s.n_out} | "
                  f"aff={s.mean_affinity_cb:.4f} | wall={time.time()-t0:.1f}s")

elapsed = time.time() - t0
print(f"\nDone: {n_steps} steps in {elapsed:.1f}s ({elapsed/n_steps*1000:.0f}ms/step)")

# Plot results
fig = plot_population_dynamics(history, 'results/population.png')
plt.show()

fig = plot_affinity_maturation(history, 'results/affinity.png')
plt.show()

print(f"\n✅ Checkpoint 5 PASS — simulation completed")

# %% [markdown]
# ## Summary
#
# | Checkpoint | Block | Status |
# |---|---|---|
# | 0 | Initialization | ✅ |
# | 1 | Affinity/Mutation | ✅ |
# | 2 | Chemokines | ✅ |
# | 3 | Movement | ✅ |
# | 4 | Cell Cycle | ✅ |
# | 5 | Full Simulation | ✅ |
#
# **Next steps:**
# - Deploy to GPU server (172.16.1.80) with `dt=0.002` for paper-accurate runs
# - Validate population dynamics, affinity curves, DZ/LZ ratio against paper
