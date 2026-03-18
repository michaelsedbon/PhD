"""
Parameter sweep for Bacterial GC.

Sweeps mutation_rate × hill_k at N=10K, L=400, 140 cycles.
Runs sequentially (each takes ~7 min), logs selection survival rate.
Generates summary JSON, heatmaps, and a results markdown file.
"""

import sys, os, json, time, itertools
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Force CPU for determinism and RAM efficiency
os.environ['JAX_PLATFORMS'] = 'cpu'

import jax
import jax.numpy as jnp

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_gpu import run_experiment_gpu
from bacterial_gc.analysis import plot_experiment, Snapshot

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ─── Sweep Grid ──────────────────────────────────────────────────────────────

SWEEP_GRID = {
    'mutation_rate':  [0.0001, 0.0003, 0.0005, 0.001],
    'hill_k':         [0.05,   0.1,    0.2,    0.3],
    'selection_mode': ['gc', 'directed_evolution'],
}

# For directed evolution, keep_fraction by hill_k
# (maps hill_k to an equivalent DE stringency)
DE_KEEP_FRACTIONS = {
    0.05: 0.01,   # very stringent: keep top 1%
    0.1:  0.05,   # stringent: keep top 5%
    0.2:  0.10,   # moderate: keep top 10%
    0.3:  0.20,   # permissive: keep top 20%
}

# Fixed parameters
FIXED = dict(
    n_founders=50,
    shape_space_dim=400,
    initial_hamming_min=50,
    initial_hamming_max=100,
    n_cycles=140,
    turbidostat_target_n=10_000,
    growth_mode='turbidostat',
    dz_growth_hours=6.0,
    doubling_time=0.5,
    dz_divisions=6,
    selection_model='hill',
    hill_n=3.0,
    unselected_return_fraction=0.1,
    affinity_gamma=105.0,
)


def compute_selection_survival(history: list) -> float:
    """Estimate average selection survival rate across cycles."""
    if len(history) < 3:
        return 0.0

    survival_rates = []
    for i in range(1, len(history)):
        snap = history[i]
        prev = history[i-1]
        if prev.n_total > 0 and snap.n_total > 0:
            # Approximate: population after selection / population before selection
            # This is rough since growth also changes pop, but gives an indication
            ratio = snap.n_total / max(prev.n_total, 1)
            survival_rates.append(min(ratio, 1.0))  # cap at 1

    return float(np.mean(survival_rates)) if survival_rates else 0.0


def run_single(mutation_rate: float, hill_k: float, out_dir: str,
               selection_mode: str = 'gc', seed: int = 42) -> dict:
    """Run one sweep point and return results dict."""
    config = BacterialConfig(
        mutation_rate=mutation_rate,
        hill_k=hill_k,
        **FIXED,
    )

    mode_short = 'gc' if selection_mode == 'gc' else 'de'
    de_keep = DE_KEEP_FRACTIONS.get(hill_k, 0.1)
    label = f"{mode_short}_mut{mutation_rate}_k{hill_k}"
    print(f"  [{label}] Starting... (keep={de_keep:.0%} for DE)", flush=True)

    t0 = time.time()
    history = run_experiment_gpu(config, seed=seed,
                                 selection_mode=selection_mode,
                                 de_keep_fraction=de_keep)
    elapsed = time.time() - t0

    # Save plot
    plot_path = os.path.join(out_dir, f"{label}.png")
    plot_experiment(history, plot_path)

    # Extract key metrics
    first = history[1] if len(history) > 1 else history[0]
    last = history[-1]

    # Mutations per gene per division
    mut_per_gene = mutation_rate * config.shape_space_dim

    result = {
        'mutation_rate': mutation_rate,
        'hill_k': hill_k,
        'selection_mode': selection_mode,
        'de_keep_fraction': de_keep if selection_mode == 'directed_evolution' else None,
        'mut_per_gene_per_div': mut_per_gene,
        'n_cycles': len(history) - 1,
        'elapsed_s': round(elapsed, 1),
        'initial_mean_aff': round(first.mean_affinity, 4),
        'final_mean_aff': round(last.mean_affinity, 4),
        'affinity_change': round(last.mean_affinity - first.mean_affinity, 4),
        'initial_max_aff': round(first.max_affinity, 4),
        'final_max_aff': round(last.max_affinity, 4),
        'initial_diversity': round(first.diversity, 2),
        'final_diversity': round(last.diversity, 2),
        'final_population': last.n_total,
        'final_top_clone_frac': round(last.top_clone_fraction, 3),
        'selection_survival_approx': round(compute_selection_survival(history), 3),
        'plot_path': plot_path,
        'extinct': last.n_total == 0,
    }

    status = "MATURATION" if result['affinity_change'] > 0.01 else (
        "STABLE" if result['affinity_change'] > -0.05 else "DEGRADATION"
    )
    result['status'] = status

    print(f"  [{label}] Done in {elapsed:.0f}s | "
          f"aff: {first.mean_affinity:.3f}→{last.mean_affinity:.3f} ({status}) | "
          f"div: {first.diversity:.1f}→{last.diversity:.1f} | "
          f"pop: {last.n_total}", flush=True)

    return result


def make_heatmap(results: list, out_dir: str):
    """Generate heatmap plots from sweep results — GC vs DE side-by-side."""
    modes = sorted(set(r.get('selection_mode', 'gc') for r in results))
    mut_rates = sorted(set(r['mutation_rate'] for r in results))
    hill_ks = sorted(set(r['hill_k'] for r in results))

    n_modes = len(modes)
    fig, axes = plt.subplots(n_modes, 3, figsize=(18, 5 * n_modes))
    if n_modes == 1:
        axes = [axes]

    for mi, mode in enumerate(modes):
        mode_results = [r for r in results if r.get('selection_mode', 'gc') == mode]

        aff_change = np.full((len(mut_rates), len(hill_ks)), np.nan)
        diversity = np.full((len(mut_rates), len(hill_ks)), np.nan)
        survival = np.full((len(mut_rates), len(hill_ks)), np.nan)

        for r in mode_results:
            i = mut_rates.index(r['mutation_rate'])
            j = hill_ks.index(r['hill_k'])
            aff_change[i, j] = r['affinity_change']
            diversity[i, j] = r['final_diversity']
            survival[i, j] = r['selection_survival_approx']

        mode_label = 'Bacterial GC' if mode == 'gc' else 'Directed Evolution'

        im1 = axes[mi][0].imshow(aff_change, cmap='RdYlGn', aspect='auto',
                                  vmin=-0.3, vmax=0.1)
        axes[mi][0].set_title(f'{mode_label}: Affinity Change', fontsize=11)
        plt.colorbar(im1, ax=axes[mi][0])

        im2 = axes[mi][1].imshow(diversity, cmap='viridis', aspect='auto',
                                  vmin=0, vmax=6)
        axes[mi][1].set_title(f'{mode_label}: Final Diversity', fontsize=11)
        plt.colorbar(im2, ax=axes[mi][1])

        im3 = axes[mi][2].imshow(survival, cmap='coolwarm', aspect='auto',
                                  vmin=0.5, vmax=1.0)
        axes[mi][2].set_title(f'{mode_label}: Survival Rate', fontsize=11)
        plt.colorbar(im3, ax=axes[mi][2])

        for ax in axes[mi]:
            ax.set_xticks(range(len(hill_ks)))
            ax.set_xticklabels([f'{k}' for k in hill_ks])
            ax.set_xlabel('Hill K / DE stringency →')
            ax.set_yticks(range(len(mut_rates)))
            ax.set_yticklabels([f'{r}' for r in mut_rates])
            ax.set_ylabel('Mutation rate')

            for i in range(len(mut_rates)):
                for j in range(len(hill_ks)):
                    if ax == axes[mi][0]: val = aff_change[i, j]
                    elif ax == axes[mi][1]: val = diversity[i, j]
                    else: val = survival[i, j]
                    if not np.isnan(val):
                        ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                                color='white' if abs(val) > 0.15 else 'black',
                                fontsize=9, fontweight='bold')

    fig.suptitle('Parameter Sweep: GC vs Directed Evolution (N=10K, L=400, 140 cycles)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'sweep_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Heatmap saved to {out_dir}/sweep_heatmap.png")


def make_results_md(results: list, out_dir: str):
    """Generate markdown summary of sweep results."""
    results_sorted = sorted(results, key=lambda r: (r['mutation_rate'], r['hill_k']))

    lines = [
        '# Parameter Sweep Results',
        '',
        f'**Date**: {time.strftime("%Y-%m-%d %H:%M")}',
        f'**N**: {FIXED["turbidostat_target_n"]:,}',
        f'**L**: {FIXED["shape_space_dim"]}',
        f'**Cycles**: {FIXED["n_cycles"]}',
        f'**Unselected return**: {FIXED["unselected_return_fraction"]}',
        '',
        '## Heatmap',
        '',
        '![Sweep Heatmap](sweep_heatmap.png)',
        '',
        '## Results Table',
        '',
        '| Mode | mut_rate | mut/gene/div | hill_k | Status | Δ affinity | Final aff | Final div | Survival | Final pop | Top clone |',
        '|---|---|---|---|---|---|---|---|---|---|---|',
    ]

    for r in results_sorted:
        mode = r.get('selection_mode', 'gc')
        lines.append(
            f"| {mode} | {r['mutation_rate']} | {r['mut_per_gene_per_div']:.2f} | {r['hill_k']} | "
            f"**{r['status']}** | {r['affinity_change']:+.4f} | {r['final_mean_aff']:.3f} | "
            f"{r['final_diversity']:.2f} | {r['selection_survival_approx']:.1%} | "
            f"{r['final_population']:,} | {r['final_top_clone_frac']:.1%} |"
        )

    lines += [
        '',
        '## Individual Run Plots',
        '',
    ]

    for r in results_sorted:
        label = f"mut{r['mutation_rate']}_k{r['hill_k']}"
        lines.append(f"### mutation_rate={r['mutation_rate']}, hill_k={r['hill_k']} → **{r['status']}**")
        lines.append(f"![{label}]({label}.png)")
        lines.append('')

    lines += [
        '## Key Observations',
        '',
        '*(To be filled after analysis)*',
        '',
    ]

    md_path = os.path.join(out_dir, 'SWEEP_RESULTS.md')
    with open(md_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  Results MD saved to {md_path}")


def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'results', 'sweep')
    os.makedirs(out_dir, exist_ok=True)

    mut_rates = SWEEP_GRID['mutation_rate']
    hill_ks = SWEEP_GRID['hill_k']
    modes = SWEEP_GRID['selection_mode']

    combos = list(itertools.product(modes, mut_rates, hill_ks))
    print(f"=== Parameter Sweep: {len(combos)} runs ===", flush=True)
    print(f"    selection_mode: {modes}")
    print(f"    mutation_rate: {mut_rates}")
    print(f"    hill_k: {hill_ks}")
    print(f"    N={FIXED['turbidostat_target_n']:,}, L={FIXED['shape_space_dim']}, "
          f"cycles={FIXED['n_cycles']}")
    print()

    results = []
    for i, (mode, mut_rate, hill_k) in enumerate(combos):
        print(f"--- Run {i+1}/{len(combos)} ---", flush=True)
        result = run_single(mut_rate, hill_k, out_dir,
                            selection_mode=mode)
        results.append(result)

        # Save intermediate results
        with open(os.path.join(out_dir, 'sweep_results.json'), 'w') as f:
            json.dump(results, f, indent=2)

    print(f"\n=== All {len(combos)} runs complete ===\n", flush=True)

    # Generate outputs
    make_heatmap(results, out_dir)
    make_results_md(results, out_dir)

    # Summary
    matured = [r for r in results if r['status'] == 'MATURATION']
    stable = [r for r in results if r['status'] == 'STABLE']
    degraded = [r for r in results if r['status'] == 'DEGRADATION']
    extinct = [r for r in results if r['extinct']]

    print(f"\nSummary:")
    print(f"  MATURATION: {len(matured)}")
    print(f"  STABLE: {len(stable)}")
    print(f"  DEGRADATION: {len(degraded)}")
    print(f"  EXTINCT: {len(extinct)}")


if __name__ == '__main__':
    main()
