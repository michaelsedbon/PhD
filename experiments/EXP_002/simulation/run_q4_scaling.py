"""Experiment 1 (Q4): Population N-Scaling at V4/V5 boundary.

Tests whether larger populations shift the maturation boundary.
3 N values × 3 T7 rates × 3 K values × 3 seeds = 81 runs.
"""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ['JAX_PLATFORMS'] = 'cuda,cpu'

import jax
print(f"JAX devices: {jax.devices()}", flush=True)

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_jit import run_experiment_jit

OUT_DIR = 'results/q4_n_scaling'
os.makedirs(OUT_DIR, exist_ok=True)

# Experiment matrix
N_VALUES = [10_000, 1_000_000, 10_000_000]
T7_RATES = {'V3_1e-6': 1e-6, 'V4_1e-5': 1e-5, 'V5_1e-4': 1e-4}
K_VALUES = [0.1, 0.2, 0.3]
SEEDS = [42, 123, 456]

total = len(N_VALUES) * len(T7_RATES) * len(K_VALUES) * len(SEEDS)
done = 0
t_start = time.time()

print(f"\n{'='*70}")
print(f"Q4: N-Scaling — {total} runs")
print(f"{'='*70}\n")

results = []
for N in N_VALUES:
    for rate_name, rate in T7_RATES.items():
        for K in K_VALUES:
            for seed in SEEDS:
                done += 1
                tag = f"N{N}__{rate_name}__K{K}__s{seed}"
                print(f"[{done}/{total}] {tag}", flush=True)

                config = BacterialConfig(
                    n_founders=50, shape_space_dim=40,
                    initial_hamming_min=5, initial_hamming_max=10,
                    n_cycles=140, growth_mode='turbidostat',
                    dz_growth_hours=6.0, doubling_time=0.5, dz_divisions=6,
                    selection_model='hill', hill_n=3.0, hill_k=K,
                    unselected_return_fraction=0.1, affinity_gamma=10.5,
                    affinity_eta=2.0,
                    mutation_rate=rate, turbidostat_target_n=N,
                )

                t0 = time.time()
                history = run_experiment_jit(config, seed=seed)
                elapsed = time.time() - t0

                init_aff = history[0].mean_affinity
                final_aff = history[-1].mean_affinity
                delta = final_aff - init_aff

                row = {
                    'N': N, 'rate_name': rate_name, 'rate': rate,
                    'K': K, 'seed': seed,
                    'init_aff': round(init_aff, 4),
                    'final_aff': round(final_aff, 4),
                    'delta_aff': round(delta, 4),
                    'final_diversity': round(history[-1].diversity, 2),
                    'final_pop': history[-1].n_total,
                    'time_s': round(elapsed, 1),
                }
                results.append(row)

                verdict = "MATUR" if delta > 0.02 else ("DEGRAD" if delta < -0.02 else "STABLE")
                print(f"  Δ={delta:+.4f} [{verdict}] pop={row['final_pop']:,} div={row['final_diversity']:.2f} ({elapsed:.0f}s)", flush=True)

                # Save incrementally
                with open(os.path.join(OUT_DIR, 'results.json'), 'w') as f:
                    json.dump(results, f, indent=2)

elapsed_total = time.time() - t_start
print(f"\n{'='*70}")
print(f"DONE: {total} runs in {elapsed_total/3600:.1f}h")
print(f"Results saved to {OUT_DIR}/results.json")
print(f"{'='*70}")
