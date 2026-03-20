"""Benchmark JIT-compiled simulation at various N."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

os.environ['JAX_PLATFORMS'] = 'cuda,cpu'

import jax
print(f"JAX devices: {jax.devices()}", flush=True)

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_jit import run_experiment_jit

Ns = [10_000, 100_000, 1_000_000, 10_000_000]

for N in Ns:
    print(f"\n{'='*60}")
    print(f"  N = {N:,}")
    print(f"{'='*60}")

    config = BacterialConfig(
        n_founders=50,
        shape_space_dim=40,
        initial_hamming_min=5,
        initial_hamming_max=10,
        n_cycles=5,  # Short benchmark — just 5 cycles
        growth_mode='turbidostat',
        dz_growth_hours=6.0,
        doubling_time=0.5,
        dz_divisions=6,
        selection_model='hill',
        hill_n=3.0,
        hill_k=0.3,
        unselected_return_fraction=0.1,
        affinity_gamma=10.5,
        mutation_rate=1e-4,
        turbidostat_target_n=N,
    )

    t0 = time.time()
    try:
        history = run_experiment_jit(config, seed=42)
        total = time.time() - t0
        last = history[-1]
        print(f"\n  RESULT: {total:.1f}s total, "
              f"{total/5:.1f}s/cycle, "
              f"N_final={last.n_total:,}, "
              f"aff={last.mean_affinity:.4f}")
    except Exception as e:
        print(f"\n  ERROR: {e}")
        import traceback
        traceback.print_exc()
    print(flush=True)

print("\nBenchmark complete!")
