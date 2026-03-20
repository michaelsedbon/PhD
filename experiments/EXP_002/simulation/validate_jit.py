"""Broad head-to-head validation: Old code vs JIT code at same seed.

Tests 3 T7 rates × 2 K values = 6 conditions.
Runs both old and JIT at seed=42, compares Δaffinity directly.
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Force CPU for old code, will switch for JIT
os.environ['JAX_PLATFORMS'] = 'cuda,cpu'

import jax
print(f"JAX devices: {jax.devices()}", flush=True)

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_jit import run_experiment_jit
from bacterial_gc.simulation_gpu import run_experiment_gpu

# Test matrix: 3 rates × 2 K values
T7_RATES = {
    'WT (1e-9)': 1e-9,
    'V3 (1e-6)': 1e-6,
    'V4 (1e-5)': 1e-5,
}
K_VALUES = [0.1, 0.3]

print("=" * 70)
print("HEAD-TO-HEAD: Old Code vs JIT Code (same seed=42)")
print("=" * 70)
print(f"{'Rate':<15} {'K':<5} {'Old Δ':>8} {'JIT Δ':>8} {'Diff':>8} {'Match'}")
print("-" * 70)

all_match = True
for rate_name, rate in T7_RATES.items():
    for K in K_VALUES:
        config = BacterialConfig(
            n_founders=50, shape_space_dim=40,
            initial_hamming_min=5, initial_hamming_max=10,
            n_cycles=140, growth_mode='turbidostat',
            dz_growth_hours=6.0, doubling_time=0.5, dz_divisions=6,
            selection_model='hill', hill_n=3.0, hill_k=K,
            unselected_return_fraction=0.1, affinity_gamma=10.5,
            mutation_rate=rate, turbidostat_target_n=10_000,
        )

        # Run OLD code
        t0 = time.time()
        old_hist = run_experiment_gpu(config, seed=42)
        old_time = time.time() - t0
        old_delta = old_hist[-1].mean_affinity - old_hist[0].mean_affinity

        # Run JIT code
        t0 = time.time()
        jit_hist = run_experiment_jit(config, seed=42)
        jit_time = time.time() - t0
        jit_delta = jit_hist[-1].mean_affinity - jit_hist[0].mean_affinity

        diff = jit_delta - old_delta

        # Match = same direction (both positive or both negative)
        same_dir = (old_delta > 0 and jit_delta > 0) or (old_delta < 0 and jit_delta < 0) or (abs(old_delta) < 0.02 and abs(jit_delta) < 0.02)
        status = "✅" if same_dir else "❌"
        if not same_dir:
            all_match = False

        print(f"{rate_name:<15} {K:<5} {old_delta:>+8.4f} {jit_delta:>+8.4f} {diff:>+8.4f} {status}  "
              f"(old:{old_time:.0f}s jit:{jit_time:.0f}s)", flush=True)

print("-" * 70)
print(f"{'✅ ALL CONSISTENT' if all_match else '❌ INCONSISTENCIES FOUND'}")
print(f"\nSpeedup ratio: JIT includes GPU compilation overhead on first run")
