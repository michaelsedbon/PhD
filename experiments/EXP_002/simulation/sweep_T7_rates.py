"""
Corrected parameter sweep with REAL T7 polymerase variant mutation rates.

Previous sweeps used rates 10-100× above actual T7 range.
This sweep uses biologically grounded rates from the Maimonide proposal.

At L=40, mutation_rate is scaled ×10 from the real per-base rate
(because L=40 is ~10× shorter than a real ~360bp nanobody gene).

Rate table:
  Label            Real rate (/bp/div)    L=40 rate      mut/gene/div
  WT E. coli DNAP  ~10⁻⁹                 10⁻⁸           4×10⁻⁷
  T7 V1 (WT+exo)   ~10⁻⁸                 10⁻⁷           4×10⁻⁶
  T7 V2             ~10⁻⁷                 10⁻⁶           4×10⁻⁵
  T7 V3 (exo⁻)     ~10⁻⁶                 10⁻⁵           4×10⁻⁴
  T7 V4 (err-prone) ~10⁻⁵                10⁻⁴           4×10⁻³
  T7 V5 (highest)   ~10⁻⁴                10⁻³           0.04
"""

import sys, os, json, time, itertools
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

os.environ['JAX_PLATFORMS'] = 'cpu'

import jax
import jax.numpy as jnp

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_gpu import run_experiment_gpu
from bacterial_gc.analysis import plot_experiment

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ─── Biologically grounded mutation rates ────────────────────────────────────

RATE_LABELS = {
    1e-8:  'WT E. coli',
    1e-7:  'T7 V1 (WT+exo)',
    1e-6:  'T7 V2',
    1e-5:  'T7 V3 (exo⁻)',
    1e-4:  'T7 V4 (error-prone)',
    1e-3:  'T7 V5 (highest)',
}

REAL_RATES = {  # L=40 rate → real per-base rate (÷10)
    1e-8:  1e-9,
    1e-7:  1e-8,
    1e-6:  1e-7,
    1e-5:  1e-6,
    1e-4:  1e-5,
    1e-3:  1e-4,
}

SWEEP_GRID = {
    'mutation_rate': [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3],
    'hill_k':        [0.05, 0.1, 0.2, 0.3],
}

FIXED = dict(
    n_founders=50,
    shape_space_dim=40,
    initial_hamming_min=5,
    initial_hamming_max=10,
    n_cycles=140,
    turbidostat_target_n=10_000,
    growth_mode='turbidostat',
    dz_growth_hours=6.0,
    doubling_time=0.5,
    dz_divisions=6,
    selection_model='hill',
    hill_n=3.0,
    unselected_return_fraction=0.1,
    affinity_gamma=10.5,
)


def run_single(mutation_rate: float, hill_k: float, out_dir: str, seed: int = 42) -> dict:
    config = BacterialConfig(mutation_rate=mutation_rate, hill_k=hill_k, **FIXED)

    real_rate = REAL_RATES[mutation_rate]
    label_name = RATE_LABELS[mutation_rate]
    label = f"mut{mutation_rate}_k{hill_k}"
    title = f"{label_name} (rate={real_rate:.0e}), K={hill_k}"

    print(f"  [{label_name}, K={hill_k}] Starting...", flush=True)

    t0 = time.time()
    history = run_experiment_gpu(config, seed=seed)
    elapsed = time.time() - t0

    plot_path = os.path.join(out_dir, f"{label}.png")
    plot_experiment(history, plot_path, title=title)

    first = history[1] if len(history) > 1 else history[0]
    last = history[-1]

    result = {
        'mutation_rate_L40': mutation_rate,
        'real_rate': real_rate,
        'label': label_name,
        'hill_k': hill_k,
        'mut_per_gene_per_div': round(mutation_rate * 40, 8),
        'n_cycles': len(history) - 1,
        'elapsed_s': round(elapsed, 1),
        'initial_mean_aff': round(first.mean_affinity, 4),
        'final_mean_aff': round(last.mean_affinity, 4),
        'affinity_change': round(last.mean_affinity - first.mean_affinity, 4),
        'final_max_aff': round(last.max_affinity, 4),
        'initial_diversity': round(first.diversity, 2),
        'final_diversity': round(last.diversity, 2),
        'final_population': last.n_total,
        'final_top_clone_frac': round(last.top_clone_fraction, 3),
        'extinct': last.n_total == 0,
    }

    status = "MATURATION" if result['affinity_change'] > 0.01 else (
        "STABLE" if result['affinity_change'] > -0.05 else "DEGRADATION"
    )
    result['status'] = status

    print(f"  [{label_name}, K={hill_k}] Done in {elapsed:.0f}s | "
          f"aff: {first.mean_affinity:.3f}→{last.mean_affinity:.3f} ({status}) | "
          f"div: {first.diversity:.1f}→{last.diversity:.1f} | "
          f"pop: {last.n_total}", flush=True)

    return result


def make_heatmap(results: list, out_dir: str):
    mut_rates = sorted(set(r['mutation_rate_L40'] for r in results))
    hill_ks = sorted(set(r['hill_k'] for r in results))

    aff_change = np.full((len(mut_rates), len(hill_ks)), np.nan)
    diversity = np.full((len(mut_rates), len(hill_ks)), np.nan)

    for r in results:
        i = mut_rates.index(r['mutation_rate_L40'])
        j = hill_ks.index(r['hill_k'])
        aff_change[i, j] = r['affinity_change']
        diversity[i, j] = r['final_diversity']

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    im1 = axes[0].imshow(aff_change, cmap='RdYlGn', aspect='auto', vmin=-0.3, vmax=0.15)
    axes[0].set_title('Affinity Change (Δ mean over 140 cycles)', fontsize=12)
    plt.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(diversity, cmap='viridis', aspect='auto', vmin=0, vmax=6)
    axes[1].set_title('Final Diversity (Shannon Entropy)', fontsize=12)
    plt.colorbar(im2, ax=axes[1])

    for ax in axes:
        ax.set_xticks(range(len(hill_ks)))
        ax.set_xticklabels([f'{k}' for k in hill_ks])
        ax.set_xlabel('Hill K (selection stringency)')
        ax.set_yticks(range(len(mut_rates)))
        ax.set_yticklabels([f'{RATE_LABELS[r]}\n({REAL_RATES[r]:.0e}/bp)' for r in mut_rates])
        ax.set_ylabel('Polymerase variant')

        for i in range(len(mut_rates)):
            for j in range(len(hill_ks)):
                val = aff_change[i, j] if ax == axes[0] else diversity[i, j]
                if not np.isnan(val):
                    color = 'white' if abs(val) > 0.1 else 'black'
                    ax.text(j, i, f'{val:+.3f}' if ax == axes[0] else f'{val:.2f}',
                            ha='center', va='center', color=color,
                            fontsize=9, fontweight='bold')

    fig.suptitle('Corrected Sweep — Real T7 Polymerase Variant Rates\n'
                 f'L=40, N={FIXED["turbidostat_target_n"]:,}, {FIXED["n_cycles"]} cycles',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'T7_rates_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Heatmap saved")


def make_results_md(results: list, out_dir: str):
    results_sorted = sorted(results, key=lambda r: (r['mutation_rate_L40'], r['hill_k']))

    lines = [
        '# Corrected Sweep — Real T7 Polymerase Variant Rates',
        '',
        f'**Date**: {time.strftime("%Y-%m-%d %H:%M")}',
        f'**N**: {FIXED["turbidostat_target_n"]:,} | **L**: {FIXED["shape_space_dim"]} | '
        f'**Cycles**: {FIXED["n_cycles"]}',
        '',
        '## Rate Table',
        '',
        '| Variant | Real rate (/bp/div) | L=40 rate | mut/gene/div |',
        '|---|---|---|---|',
    ]
    for rate in SWEEP_GRID['mutation_rate']:
        lines.append(f'| {RATE_LABELS[rate]} | {REAL_RATES[rate]:.0e} | {rate:.0e} | '
                     f'{rate * 40:.2e} |')

    lines += [
        '',
        '## Heatmap',
        '',
        '![T7 rates heatmap](T7_rates_heatmap.png)',
        '',
        '## Results Table',
        '',
        '| Variant | K | Status | Δ aff | Final aff | Diversity | Pop | Time |',
        '|---|---|---|---|---|---|---|---|',
    ]

    for r in results_sorted:
        lines.append(
            f"| {r['label']} | {r['hill_k']} | **{r['status']}** | "
            f"{r['affinity_change']:+.4f} | {r['final_mean_aff']:.3f} | "
            f"{r['final_diversity']:.2f} | {r['final_population']:,} | "
            f"{r['elapsed_s']:.0f}s |"
        )

    # Summary
    matured = [r for r in results if r['status'] == 'MATURATION']
    stable = [r for r in results if r['status'] == 'STABLE']
    degraded = [r for r in results if r['status'] == 'DEGRADATION']

    lines += [
        '',
        '## Summary',
        '',
        f'- **MATURATION**: {len(matured)} runs',
        f'- **STABLE**: {len(stable)} runs',
        f'- **DEGRADATION**: {len(degraded)} runs',
        '',
        '## Individual Plots',
        '',
    ]

    for r in results_sorted:
        label = f"mut{r['mutation_rate_L40']}_k{r['hill_k']}"
        lines.append(f"### {r['label']}, K={r['hill_k']} → **{r['status']}**")
        lines.append(f"![{label}]({label}.png)")
        lines.append('')

    md_path = os.path.join(out_dir, 'T7_RATES_RESULTS.md')
    with open(md_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  Results MD saved to {md_path}")


def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'results', 'sweep_T7_rates')
    os.makedirs(out_dir, exist_ok=True)

    mut_rates = SWEEP_GRID['mutation_rate']
    hill_ks = SWEEP_GRID['hill_k']

    combos = list(itertools.product(mut_rates, hill_ks))
    print(f"=== Corrected T7 Rate Sweep: {len(combos)} runs ===", flush=True)
    print(f"    Variants: {[RATE_LABELS[r] for r in mut_rates]}")
    print(f"    hill_k: {hill_ks}")
    print(f"    N={FIXED['turbidostat_target_n']:,}, L={FIXED['shape_space_dim']}, "
          f"gamma={FIXED['affinity_gamma']}, cycles={FIXED['n_cycles']}")
    print()

    results = []
    for i, (mut_rate, hill_k) in enumerate(combos):
        print(f"--- Run {i+1}/{len(combos)} ---", flush=True)
        result = run_single(mut_rate, hill_k, out_dir)
        results.append(result)

        # Save incrementally
        with open(os.path.join(out_dir, 'T7_rates_results.json'), 'w') as f:
            json.dump(results, f, indent=2)

    print(f"\n=== All {len(combos)} runs complete ===\n", flush=True)

    make_heatmap(results, out_dir)
    make_results_md(results, out_dir)

    matured = [r for r in results if r['status'] == 'MATURATION']
    stable = [r for r in results if r['status'] == 'STABLE']
    degraded = [r for r in results if r['status'] == 'DEGRADATION']

    print(f"\nSummary:")
    print(f"  MATURATION: {len(matured)}")
    print(f"  STABLE: {len(stable)}")
    print(f"  DEGRADATION: {len(degraded)}")


if __name__ == '__main__':
    main()
