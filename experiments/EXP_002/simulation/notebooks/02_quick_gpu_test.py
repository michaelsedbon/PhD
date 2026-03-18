# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: GC Simulation
#     language: python
#     name: gc_sim
# ---

# %% [markdown]
# # Quick GPU Test — Coarse-Grain GC Simulation
#
# Run a short simulation (1 day, dt=0.05) on GPU to verify everything works.
# Should take ~30s after JIT compilation.

# %%
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/gc_simulation/src'))

import jax
import jax.numpy as jnp
print(f"JAX backend: {jax.default_backend()}")
print(f"Devices: {jax.devices()}")

# %%
from germinal_center.config import GCConfig
from germinal_center.initialization import initialize_gc
from germinal_center.simulation import step
from germinal_center.state import count_cells

config = GCConfig(dt=0.05, total_days=1.0, snapshot_interval=10)
print(f"Config: {config.total_days} day, dt={config.dt}h, {config.n_timesteps} steps")

# %%
# Initialize
key = jax.random.PRNGKey(42)
state = initialize_gc(config, key)
c = count_cells(state)
print(f"Initial: CB={c['n_cb']}, TC={c['n_tc']}, FDC={c['n_fdc']}")
print(f"Grid: {state.grid_cell_type.shape}, Sphere points: {int(jnp.sum(state.sphere_mask))}")

# %%
# Warmup step (JIT compilation — takes ~10s on GPU)
key, sk = jax.random.split(key)
t0 = time.time()
state = step(state, config, sk)
jax.block_until_ready(state.grid_cell_type)
print(f"JIT compile: {time.time()-t0:.1f}s")
c = count_cells(state)
print(f"After 1 step: CB={c['n_cb']}, CC={c['n_cc']}, OUT={c['n_out']}")

# %%
# Run 1-day simulation (480 steps at dt=0.05)
from germinal_center.analysis import snapshot

history = [snapshot(state)]
times_list = []

t0 = time.time()
for t in range(config.n_timesteps - 1):
    key, sk = jax.random.split(key)
    state = step(state, config, sk)
    if (t + 1) % 10 == 0:
        history.append(snapshot(state))
        c = count_cells(state)
        elapsed = time.time() - t0
        rate = (t + 1) / elapsed
        print(f"  step {t+1}/{config.n_timesteps}: CB={c['n_cb']} CC={c['n_cc']} OUT={c['n_out']} | {rate:.1f} steps/s")

jax.block_until_ready(state.grid_cell_type)
total = time.time() - t0
print(f"\nDone: {config.n_timesteps} steps in {total:.1f}s ({total/config.n_timesteps*1000:.0f}ms/step)")

# %%
# Plot results
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Population dynamics
ax = axes[0, 0]
times = [s.time / 24.0 for s in history]
ax.plot(times, [s.n_cb for s in history], label='CB (DZ)', color='#4a9eff', lw=2)
ax.plot(times, [s.n_cc for s in history], label='CC (LZ)', color='#ff6b6b', lw=2)
ax.plot(times, [s.n_out for s in history], label='Output', color='#50c878', lw=2)
ax.set_xlabel('Time (days)')
ax.set_ylabel('Cell count')
ax.set_title('Population Dynamics')
ax.legend()
ax.grid(alpha=0.3)

# Affinity
ax = axes[0, 1]
ax.plot(times, [s.mean_affinity_cb for s in history], label='Mean CB', color='#4a9eff', lw=2)
ax.plot(times, [s.max_affinity for s in history], label='Max', color='#ffa500', lw=2)
ax.set_xlabel('Time (days)')
ax.set_ylabel('Affinity')
ax.set_title('Affinity Maturation')
ax.legend()
ax.grid(alpha=0.3)
ax.set_ylim(0, 1)

# DZ/LZ ratio
ax = axes[1, 0]
ax.plot(times, [s.dz_lz_ratio for s in history], color='#7c3aed', lw=2)
ax.axhline(y=2.0, color='gray', ls='--', alpha=0.5, label='Expected ~2:1')
ax.set_xlabel('Time (days)')
ax.set_ylabel('DZ/LZ ratio')
ax.set_title('Dark Zone / Light Zone')
ax.legend()
ax.grid(alpha=0.3)

# Diversity
ax = axes[1, 1]
ax.plot(times, [s.diversity_cb for s in history], color='#e91e63', lw=2)
ax.set_xlabel('Time (days)')
ax.set_ylabel('Shannon entropy')
ax.set_title('Clonal Diversity')
ax.grid(alpha=0.3)

fig.suptitle(f'GC Simulation — 1 day @ dt={config.dt}h on {jax.default_backend().upper()}', fontsize=14, fontweight='bold')
fig.tight_layout()
plt.show()

# %%
# Summary
c = count_cells(state)
print(f"Final state (t={state.time:.1f}h = {state.time/24:.2f} days):")
print(f"  Centroblasts:  {c['n_cb']}")
print(f"  Centrocytes:   {c['n_cc']}")
print(f"  Output cells:  {c['n_out']}")
print(f"  Total B cells: {c['n_bcells']}")
print(f"  Mean CB affinity: {history[-1].mean_affinity_cb:.4f}")
print(f"  Max affinity:     {history[-1].max_affinity:.4f}")
print(f"\nPerformance: {total/config.n_timesteps*1000:.0f}ms/step on {jax.default_backend().upper()}")
