"""Pipeline Model Controls — batch vs pipeline at N=10K.

Compares the old batch model (all cells migrate at once) with the new
pipeline model (continuous sampling of DZ → LZ).

Matched for total doublings and selection events:
- Batch: 140 cycles × 12 doublings = 1,680 total doublings, 140 selections
- Pipeline: 560 cycles × 3 doublings = 1,680 total doublings, 560 selections
"""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ['JAX_PLATFORMS'] = 'cuda,cpu'

import jax
print(f"JAX devices: {jax.devices()}", flush=True)

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_jit import run_experiment_jit, run_experiment_pipeline_jit

OUT_DIR = 'results/pipeline_controls'
os.makedirs(OUT_DIR, exist_ok=True)

BASE_CONFIG = dict(
    n_founders=50, shape_space_dim=40,
    initial_hamming_min=5, initial_hamming_max=10,
    n_cycles=140, growth_mode='turbidostat',
    dz_growth_hours=6.0, doubling_time=0.5, dz_divisions=6,
    selection_model='hill', hill_n=3.0, hill_k=0.3,
    unselected_return_fraction=0.0, affinity_gamma=10.5,
    affinity_eta=2.0,
    turbidostat_target_n=10_000,
)

controls = [
    # Batch: old model, top-fraction 10%, V4
    {'name': 'batch_tf10_V4', 'mode': 'batch', 'rate': 1e-5,
     'keep': 0.10, 'rate_name': 'V4'},
    # Pipeline: sample 50%, keep 10%, 3 doublings, V4
    {'name': 'pipe_s50_tf10_V4', 'mode': 'pipeline', 'rate': 1e-5,
     'keep': 0.10, 'sample': 0.50, 'doublings': 3, 'rate_name': 'V4'},
    # Pipeline: sample 30%, keep 10%, 3 doublings, V4
    {'name': 'pipe_s30_tf10_V4', 'mode': 'pipeline', 'rate': 1e-5,
     'keep': 0.10, 'sample': 0.30, 'doublings': 3, 'rate_name': 'V4'},
    # Pipeline: sample 50%, keep 30%, 3 doublings, V4
    {'name': 'pipe_s50_tf30_V4', 'mode': 'pipeline', 'rate': 1e-5,
     'keep': 0.30, 'sample': 0.50, 'doublings': 3, 'rate_name': 'V4'},
    # Batch: old model, top-fraction 10%, V3
    {'name': 'batch_tf10_V3', 'mode': 'batch', 'rate': 1e-6,
     'keep': 0.10, 'rate_name': 'V3'},
    # Pipeline: sample 50%, keep 10%, 3 doublings, V3
    {'name': 'pipe_s50_tf10_V3', 'mode': 'pipeline', 'rate': 1e-6,
     'keep': 0.10, 'sample': 0.50, 'doublings': 3, 'rate_name': 'V3'},
    # Pipeline: sample 50%, keep 10%, 6 doublings, V4 (longer DZ)
    {'name': 'pipe_s50_tf10_V4_dz6', 'mode': 'pipeline', 'rate': 1e-5,
     'keep': 0.10, 'sample': 0.50, 'doublings': 6, 'rate_name': 'V4'},
]

results = []
total = len(controls)

print(f"\n{'='*70}")
print(f"Pipeline Controls: {total} runs")
print(f"{'='*70}\n")

for i, ctrl in enumerate(controls):
    print(f"[{i+1}/{total}] {ctrl['name']}", flush=True)

    config = BacterialConfig(**{**BASE_CONFIG, 'mutation_rate': ctrl['rate']})
    t0 = time.time()

    if ctrl['mode'] == 'batch':
        # Old batch model with top-fraction selection
        history = run_experiment_jit(
            config, seed=42,
            selection_mode='top_fraction',
            gc_keep_fraction=ctrl['keep'],
        )
    else:
        # New pipeline model
        doublings = ctrl.get('doublings', 3)
        # Match total doublings: 1680 total, so n_mini_cycles = 1680 / doublings
        total_mc = int(1680 / doublings)
        history = run_experiment_pipeline_jit(
            config, seed=42,
            gc_keep_fraction=ctrl['keep'],
            sample_fraction=ctrl.get('sample', 0.50),
            mini_cycle_doublings=doublings,
            total_mini_cycles=total_mc,
            snapshot_interval=max(1, total_mc // 140),
        )

    elapsed = time.time() - t0

    init_aff = history[0].mean_affinity
    final_aff = history[-1].mean_affinity
    delta = final_aff - init_aff

    row = {
        'name': ctrl['name'],
        'mode': ctrl['mode'],
        'rate': ctrl['rate'],
        'rate_name': ctrl['rate_name'],
        'keep_fraction': ctrl['keep'],
        'sample_fraction': ctrl.get('sample', 1.0),
        'doublings': ctrl.get('doublings', 12),
        'init_aff': round(init_aff, 4),
        'final_aff': round(final_aff, 4),
        'delta_aff': round(delta, 4),
        'final_diversity': round(history[-1].diversity, 2),
        'final_pop': history[-1].n_total,
        'time_s': round(elapsed, 1),
    }
    results.append(row)

    verdict = "MATUR" if delta > 0.02 else ("DEGRAD" if delta < -0.02 else "STABLE")
    print(f"  Δ={delta:+.4f} [{verdict}] pop={row['final_pop']:,} div={row['final_diversity']:.2f} ({elapsed:.0f}s)\n", flush=True)

    with open(os.path.join(OUT_DIR, 'results.json'), 'w') as f:
        json.dump(results, f, indent=2)

print(f"\n{'='*70}")
print(f"DONE: {total} runs")
print(f"{'='*70}")

print(f"\n{'Name':<25} {'Mode':<10} {'Rate':<10} {'Samp':>5} {'Keep':>5} {'Δaff':>8} {'Div':>6} {'Pop':>8}")
print("-" * 82)
for r in results:
    print(f"{r['name']:<25} {r['mode']:<10} {r['rate_name']:<10} {r['sample_fraction']:>5.0%} {r['keep_fraction']:>5.0%} {r['delta_aff']:>+8.4f} {r['final_diversity']:>6.2f} {r['final_pop']:>8,}")
