"""Controls for Top-Fraction (Competitive) Selection Model.

4 controls to validate the model works correctly before benchmarking:
1. fraction=1.0 (no selection) → drift only, no maturation
2. fraction=0.01 (very strong) → fast maturation, low diversity
3. fraction=0.10 (natural GC) → moderate maturation
4. Hill K=0.3 vs top_fraction at ~82% survival → should give similar results?
"""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ['JAX_PLATFORMS'] = 'cuda,cpu'

import jax
print(f"JAX devices: {jax.devices()}", flush=True)

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_jit import run_experiment_jit

OUT_DIR = 'results/selection_controls'
os.makedirs(OUT_DIR, exist_ok=True)

BASE_CONFIG = dict(
    n_founders=50, shape_space_dim=40,
    initial_hamming_min=5, initial_hamming_max=10,
    n_cycles=140, growth_mode='turbidostat',
    dz_growth_hours=6.0, doubling_time=0.5, dz_divisions=6,
    selection_model='hill', hill_n=3.0, hill_k=0.3,
    unselected_return_fraction=0.1, affinity_gamma=10.5,
    affinity_eta=2.0,
    mutation_rate=1e-5,  # V4 rate — boundary case
    turbidostat_target_n=10_000,
)

controls = [
    # Control 1: No selection (keep 100%)
    {'name': 'tf_100pct', 'mode': 'top_fraction', 'fraction': 1.0,
     'expected': 'No maturation — drift only'},
    # Control 2: Very strong selection (keep 1%)
    {'name': 'tf_1pct', 'mode': 'top_fraction', 'fraction': 0.01,
     'expected': 'Strong maturation, very low diversity'},
    # Control 3: Natural GC strength (keep 10%)
    {'name': 'tf_10pct', 'mode': 'top_fraction', 'fraction': 0.10,
     'expected': 'Good maturation, moderate diversity'},
    # Control 4: Moderate selection (keep 30%)
    {'name': 'tf_30pct', 'mode': 'top_fraction', 'fraction': 0.30,
     'expected': 'Moderate maturation'},
    # Control 5: Hill K=0.3 for comparison (keep ~82%)
    {'name': 'hill_k03', 'mode': 'gc', 'hill_k': 0.3,
     'expected': 'Known good — should match overnight data'},
    # Control 6: Top-fraction at ~82% (matched to Hill K=0.3)
    {'name': 'tf_82pct', 'mode': 'top_fraction', 'fraction': 0.82,
     'expected': 'Should be similar to Hill K=0.3 (same survival rate)'},
    # Control 7: Strong Hill K=1.0 for comparison
    {'name': 'hill_k10', 'mode': 'gc', 'hill_k': 1.0,
     'expected': 'Much stronger selection than K=0.3'},
    # Control 8: Top-fraction at ~17% (matched to Hill K=1.0)
    {'name': 'tf_17pct', 'mode': 'top_fraction', 'fraction': 0.17,
     'expected': 'Should be different from Hill K=1.0 (competitive vs independent)'},
]

results = []
total = len(controls)

print(f"\n{'='*70}")
print(f"Selection Controls: {total} runs")
print(f"{'='*70}\n")

for i, ctrl in enumerate(controls):
    print(f"[{i+1}/{total}] {ctrl['name']}: {ctrl['expected']}", flush=True)

    config = BacterialConfig(**BASE_CONFIG)
    if ctrl['mode'] == 'gc' and 'hill_k' in ctrl:
        config = BacterialConfig(**{**BASE_CONFIG, 'hill_k': ctrl['hill_k']})

    t0 = time.time()
    history = run_experiment_jit(
        config, seed=42,
        selection_mode=ctrl['mode'],
        gc_keep_fraction=ctrl.get('fraction', 0.10),
    )
    elapsed = time.time() - t0

    init_aff = history[0].mean_affinity
    final_aff = history[-1].mean_affinity
    delta = final_aff - init_aff

    row = {
        'name': ctrl['name'],
        'mode': ctrl['mode'],
        'fraction': ctrl.get('fraction', None),
        'hill_k': ctrl.get('hill_k', None),
        'expected': ctrl['expected'],
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

    with open(os.path.join(OUT_DIR, 'controls.json'), 'w') as f:
        json.dump(results, f, indent=2)

print(f"\n{'='*70}")
print(f"DONE: {total} runs")
print(f"{'='*70}")

# Summary table
print(f"\n{'Name':<15} {'Mode':<15} {'Frac/K':>8} {'Δaff':>8} {'Div':>6} {'Pop':>8}")
print("-" * 70)
for r in results:
    fk = r.get('fraction') or r.get('hill_k', '')
    print(f"{r['name']:<15} {r['mode']:<15} {fk:>8} {r['delta_aff']:>+8.4f} {r['final_diversity']:>6.2f} {r['final_pop']:>8,}")
