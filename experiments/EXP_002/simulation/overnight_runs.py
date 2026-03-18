"""
Overnight runs — 3 sequential experiments:

1. Multi-seed V4 boundary (10 seeds at the maturation/degradation edge)
2. GC vs Directed Evolution comparison (6 T7 rates × 4 K values, DE mode)
3. GPU scaling to N=10⁷ (6 T7 rates × 2 K values at L=40)

All runs save per-cycle history (JSON + CSV) for future re-analysis.
"""

import sys, os, json, time, itertools
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

os.environ['JAX_PLATFORMS'] = 'cpu'

import jax
import jax.numpy as jnp

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_gpu import run_experiment_gpu
from bacterial_gc.analysis import plot_experiment, save_history

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ─── Shared config ───────────────────────────────────────────────────

FIXED_L40 = dict(
    n_founders=50,
    shape_space_dim=40,
    initial_hamming_min=5,
    initial_hamming_max=10,
    n_cycles=140,
    growth_mode='turbidostat',
    dz_growth_hours=6.0,
    doubling_time=0.5,
    dz_divisions=6,
    selection_model='hill',
    hill_n=3.0,
    unselected_return_fraction=0.1,
    affinity_gamma=10.5,
)

RATE_LABELS = {
    1e-8:  'WT_Ecoli',
    1e-7:  'T7_V1',
    1e-6:  'T7_V2',
    1e-5:  'T7_V3',
    1e-4:  'T7_V4',
    1e-3:  'T7_V5',
}


def run_single(config, seed, out_dir, label, title, selection_mode='gc', de_keep_fraction=0.01):
    """Run one simulation, save plot + history, return result dict."""
    t0 = time.time()
    history = run_experiment_gpu(config, seed=seed,
                                 selection_mode=selection_mode,
                                 de_keep_fraction=de_keep_fraction)
    elapsed = time.time() - t0

    # Save plot
    plot_path = os.path.join(out_dir, f"{label}.png")
    plot_experiment(history, plot_path, title=title)

    # Save history (JSON + CSV)
    history_path = os.path.join(out_dir, f"{label}_history")
    save_history(history, history_path)

    first = history[1] if len(history) > 1 else history[0]
    last = history[-1]

    result = {
        'label': label,
        'title': title,
        'mutation_rate': config.mutation_rate,
        'hill_k': config.hill_k,
        'N': config.turbidostat_target_n,
        'selection_mode': selection_mode,
        'seed': seed,
        'n_cycles': len(history) - 1,
        'elapsed_s': round(elapsed, 1),
        'initial_mean_aff': round(first.mean_affinity, 4),
        'final_mean_aff': round(last.mean_affinity, 4),
        'affinity_change': round(last.mean_affinity - first.mean_affinity, 4),
        'final_diversity': round(last.diversity, 2),
        'final_population': last.n_total,
        'status': ("MATURATION" if last.mean_affinity - first.mean_affinity > 0.01
                   else ("STABLE" if last.mean_affinity - first.mean_affinity > -0.05
                         else "DEGRADATION")),
    }

    print(f"  [{label}] {elapsed:.0f}s | aff: {first.mean_affinity:.3f}→{last.mean_affinity:.3f} "
          f"({result['status']}) | pop: {last.n_total}", flush=True)
    return result


# =====================================================================
# EXPERIMENT 1: Multi-seed at V4 boundary
# =====================================================================

def run_experiment_1():
    """10 seeds at V4 (10⁻⁵) boundary conditions."""
    print("\n" + "="*70)
    print("EXPERIMENT 1: Multi-seed V4 boundary (10 seeds × 4 K values)")
    print("="*70 + "\n", flush=True)

    out_dir = os.path.join(os.path.dirname(__file__), 'results', 'multiseed_V4')
    os.makedirs(out_dir, exist_ok=True)

    mutation_rate = 1e-4  # T7 V4 at L=40
    hill_ks = [0.05, 0.1, 0.2, 0.3]
    seeds = list(range(10))  # seeds 0-9

    results = []
    total = len(hill_ks) * len(seeds)
    i = 0
    for hill_k in hill_ks:
        for seed in seeds:
            i += 1
            print(f"--- Run {i}/{total} ---", flush=True)
            config = BacterialConfig(
                mutation_rate=mutation_rate, hill_k=hill_k,
                turbidostat_target_n=10_000, **FIXED_L40
            )
            label = f"V4_k{hill_k}_seed{seed}"
            title = f"T7 V4 (10⁻⁵), K={hill_k}, seed={seed}"
            result = run_single(config, seed, out_dir, label, title)
            results.append(result)

            with open(os.path.join(out_dir, 'multiseed_results.json'), 'w') as f:
                json.dump(results, f, indent=2)

    # Summary stats
    print(f"\n--- Multi-seed V4 Summary ---")
    for hill_k in hill_ks:
        k_results = [r for r in results if r['hill_k'] == hill_k]
        affs = [r['affinity_change'] for r in k_results]
        statuses = [r['status'] for r in k_results]
        print(f"  K={hill_k}: Δaff = {np.mean(affs):+.4f} ± {np.std(affs):.4f} "
              f"({statuses.count('MATURATION')}M/{statuses.count('STABLE')}S/{statuses.count('DEGRADATION')}D)")

    return results


# =====================================================================
# EXPERIMENT 2: GC vs Directed Evolution
# =====================================================================

def run_experiment_2():
    """Compare GC and DE modes across T7 rates."""
    print("\n" + "="*70)
    print("EXPERIMENT 2: GC vs Directed Evolution (6 rates × 4 K × 2 modes)")
    print("="*70 + "\n", flush=True)

    out_dir = os.path.join(os.path.dirname(__file__), 'results', 'gc_vs_de')
    os.makedirs(out_dir, exist_ok=True)

    rates = [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]
    # For DE, we only need a subset of K values — use K=0.2, 0.3 (best GC range)
    # Plus de_keep_fraction equivalents
    hill_ks = [0.1, 0.2, 0.3]

    results = []

    # Run DE mode for all rates (top 1% selection, no Hill)
    de_combos = list(itertools.product(rates, [0.01, 0.05, 0.1]))  # keep fractions
    total_de = len(de_combos)
    print(f"Part A: Directed Evolution ({total_de} runs)", flush=True)

    for i, (rate, keep_frac) in enumerate(de_combos):
        print(f"--- DE Run {i+1}/{total_de} ---", flush=True)
        config = BacterialConfig(
            mutation_rate=rate, hill_k=0.3,  # hill_k not used in DE mode
            turbidostat_target_n=10_000, **FIXED_L40
        )
        vname = RATE_LABELS[rate]
        label = f"DE_{vname}_keep{keep_frac}"
        title = f"DE: {vname}, keep={keep_frac*100:.0f}%"
        result = run_single(config, 42, out_dir, label, title,
                           selection_mode='directed_evolution',
                           de_keep_fraction=keep_frac)
        result['keep_fraction'] = keep_frac
        results.append(result)

        with open(os.path.join(out_dir, 'gc_vs_de_results.json'), 'w') as f:
            json.dump(results, f, indent=2)

    # Run GC mode for the same rates at K=0.2, 0.3 (already have K=0.1 from T7 sweep)
    gc_combos = list(itertools.product(rates, hill_ks))
    total_gc = len(gc_combos)
    print(f"\nPart B: GC mode ({total_gc} runs — for comparison)", flush=True)

    for i, (rate, hill_k) in enumerate(gc_combos):
        print(f"--- GC Run {i+1}/{total_gc} ---", flush=True)
        config = BacterialConfig(
            mutation_rate=rate, hill_k=hill_k,
            turbidostat_target_n=10_000, **FIXED_L40
        )
        vname = RATE_LABELS[rate]
        label = f"GC_{vname}_k{hill_k}"
        title = f"GC: {vname}, K={hill_k}"
        result = run_single(config, 42, out_dir, label, title,
                           selection_mode='gc')
        result['keep_fraction'] = None
        results.append(result)

        with open(os.path.join(out_dir, 'gc_vs_de_results.json'), 'w') as f:
            json.dump(results, f, indent=2)

    return results


# =====================================================================
# EXPERIMENT 3: N=10⁷ scaling
# =====================================================================

def run_experiment_3():
    """Scale to N=10⁷ at key T7 rates."""
    print("\n" + "="*70)
    print("EXPERIMENT 3: N=10⁷ scaling (4 rates × 2 K values)")
    print("="*70 + "\n", flush=True)

    out_dir = os.path.join(os.path.dirname(__file__), 'results', 'scaling_10M')
    os.makedirs(out_dir, exist_ok=True)

    # Focus on the interesting rates: V3, V4, V5 + WT baseline
    # K=0.2 and K=0.3 (the most informative)
    rates = [1e-8, 1e-5, 1e-4, 1e-3]  # WT, V3, V4, V5
    hill_ks = [0.2, 0.3]
    N = 10_000_000

    combos = list(itertools.product(rates, hill_ks))
    total = len(combos)
    print(f"N={N:,}, L=40 ({total} runs)", flush=True)

    results = []
    for i, (rate, hill_k) in enumerate(combos):
        print(f"\n--- Run {i+1}/{total} ---", flush=True)

        fixed = dict(FIXED_L40)
        config = BacterialConfig(
            mutation_rate=rate, hill_k=hill_k,
            turbidostat_target_n=N, **fixed
        )
        vname = RATE_LABELS[rate]
        label = f"N10M_{vname}_k{hill_k}"
        title = f"N=10⁷: {vname}, K={hill_k}"
        result = run_single(config, 42, out_dir, label, title)
        results.append(result)

        with open(os.path.join(out_dir, 'scaling_10M_results.json'), 'w') as f:
            json.dump(results, f, indent=2)

    return results


# =====================================================================
# Main: run all 3 sequentially
# =====================================================================

def main():
    t_start = time.time()
    print(f"=== OVERNIGHT RUNS STARTED at {time.strftime('%Y-%m-%d %H:%M')} ===\n", flush=True)

    # Experiment 1: Multi-seed (~2-3h)
    try:
        results_1 = run_experiment_1()
        print(f"\n✅ Experiment 1 complete: {len(results_1)} runs\n", flush=True)
    except Exception as e:
        print(f"\n❌ Experiment 1 failed: {e}\n", flush=True)

    # Experiment 2: GC vs DE (~3-4h)
    try:
        results_2 = run_experiment_2()
        print(f"\n✅ Experiment 2 complete: {len(results_2)} runs\n", flush=True)
    except Exception as e:
        print(f"\n❌ Experiment 2 failed: {e}\n", flush=True)

    # Experiment 3: N=10⁷ (~unknown, could be long)
    try:
        results_3 = run_experiment_3()
        print(f"\n✅ Experiment 3 complete: {len(results_3)} runs\n", flush=True)
    except Exception as e:
        print(f"\n❌ Experiment 3 failed: {e}\n", flush=True)

    total_time = time.time() - t_start
    print(f"\n=== ALL OVERNIGHT RUNS FINISHED ===")
    print(f"Total time: {total_time/3600:.1f} hours")
    print(f"Finished at: {time.strftime('%Y-%m-%d %H:%M')}")


if __name__ == '__main__':
    main()
