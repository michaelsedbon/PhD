"""
L=40 GPU validation sweep — same grid as L=400 CPU sweep but with scaled parameters.

Purpose: validate that reducing L from 400 to 40 (with scaled mutation_rate and gamma)
produces the same qualitative results, before scaling up to N=10^7 on GPU.

Scaling rules (keeping mutations/gene/division constant):
- L: 400 → 40 (÷10)
- mutation_rate: ×10 (so rate × L stays the same)
- affinity_gamma: 105 → 10.5 (÷10)
- initial_hamming_min: 50 → 5 (÷10)
- initial_hamming_max: 100 → 10 (÷10)
"""

import sys, os, json, time, itertools
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Use GPU
os.environ['JAX_PLATFORMS'] = 'cuda,cpu'

import jax
import jax.numpy as jnp

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_gpu import run_experiment_gpu
from bacterial_gc.analysis import plot_experiment, Snapshot

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ─── Sweep Grid (scaled from L=400) ─────────────────────────────────────────

# Original L=400 rates: [0.0001, 0.0003, 0.0005, 0.001]
# Scaled ×10 for L=40:
SWEEP_GRID = {
    'mutation_rate': [0.001, 0.003, 0.005, 0.01],
    'hill_k':        [0.05,  0.1,   0.2,   0.3],
}

# Label mapping for comparison with L=400 results
L400_RATE_MAP = {0.001: 0.0001, 0.003: 0.0003, 0.005: 0.0005, 0.01: 0.001}

FIXED = dict(
    n_founders=50,
    shape_space_dim=40,           # ÷10
    initial_hamming_min=5,         # ÷10
    initial_hamming_max=10,        # ÷10
    n_cycles=140,
    turbidostat_target_n=10_000,
    growth_mode='turbidostat',
    dz_growth_hours=6.0,
    doubling_time=0.5,
    dz_divisions=6,
    selection_model='hill',
    hill_n=3.0,
    unselected_return_fraction=0.1,
    affinity_gamma=10.5,           # ÷10
)


def compute_selection_survival(history: list) -> float:
    if len(history) < 3:
        return 0.0
    survival_rates = []
    for i in range(1, len(history)):
        snap = history[i]
        prev = history[i-1]
        if prev.n_total > 0 and snap.n_total > 0:
            ratio = snap.n_total / max(prev.n_total, 1)
            survival_rates.append(min(ratio, 1.0))
    return float(np.mean(survival_rates)) if survival_rates else 0.0


def run_single(mutation_rate: float, hill_k: float, out_dir: str, seed: int = 42) -> dict:
    config = BacterialConfig(mutation_rate=mutation_rate, hill_k=hill_k, **FIXED)

    l400_rate = L400_RATE_MAP.get(mutation_rate, mutation_rate)
    label = f"mut{mutation_rate}_k{hill_k}"
    print(f"  [{label}] Starting (L=40, equiv L400 rate={l400_rate})...", flush=True)

    t0 = time.time()
    history = run_experiment_gpu(config, seed=seed)
    elapsed = time.time() - t0

    plot_path = os.path.join(out_dir, f"{label}.png")
    plot_experiment(history, plot_path)

    first = history[1] if len(history) > 1 else history[0]
    last = history[-1]
    mut_per_gene = mutation_rate * config.shape_space_dim

    result = {
        'mutation_rate': mutation_rate,
        'equivalent_L400_rate': l400_rate,
        'hill_k': hill_k,
        'mut_per_gene_per_div': mut_per_gene,
        'L': 40,
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
    mut_rates = sorted(set(r['mutation_rate'] for r in results))
    hill_ks = sorted(set(r['hill_k'] for r in results))

    aff_change = np.full((len(mut_rates), len(hill_ks)), np.nan)
    diversity = np.full((len(mut_rates), len(hill_ks)), np.nan)

    for r in results:
        i = mut_rates.index(r['mutation_rate'])
        j = hill_ks.index(r['hill_k'])
        aff_change[i, j] = r['affinity_change']
        diversity[i, j] = r['final_diversity']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    im1 = axes[0].imshow(aff_change, cmap='RdYlGn', aspect='auto', vmin=-0.3, vmax=0.1)
    axes[0].set_title('L=40 GPU: Affinity Change', fontsize=12)
    plt.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(diversity, cmap='viridis', aspect='auto', vmin=0, vmax=6)
    axes[1].set_title('L=40 GPU: Final Diversity', fontsize=12)
    plt.colorbar(im2, ax=axes[1])

    for ax in axes:
        ax.set_xticks(range(len(hill_ks)))
        ax.set_xticklabels([f'{k}' for k in hill_ks])
        ax.set_xlabel('Hill K')
        ax.set_yticks(range(len(mut_rates)))
        ax.set_yticklabels([f'{r}\n(≡{L400_RATE_MAP.get(r, r)} @L400)' for r in mut_rates])
        ax.set_ylabel('Mutation rate (L=40)')

        for i in range(len(mut_rates)):
            for j in range(len(hill_ks)):
                val = aff_change[i, j] if ax == axes[0] else diversity[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                            color='white' if abs(val) > 0.15 else 'black',
                            fontsize=10, fontweight='bold')

    fig.suptitle('L=40 GPU Validation (N=10K, 140 cycles — compare with L=400 CPU)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'sweep_L40_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Heatmap saved to {out_dir}/sweep_L40_heatmap.png")


def make_results_md(results: list, out_dir: str):
    results_sorted = sorted(results, key=lambda r: (r['mutation_rate'], r['hill_k']))
    abs_dir = os.path.abspath(out_dir)

    lines = [
        '# L=40 GPU Validation Sweep',
        '',
        f'**Date**: {time.strftime("%Y-%m-%d %H:%M")}',
        f'**N**: {FIXED["turbidostat_target_n"]:,}',
        f'**L**: {FIXED["shape_space_dim"]}',
        f'**Gamma**: {FIXED["affinity_gamma"]}',
        f'**Cycles**: {FIXED["n_cycles"]}',
        f'**Platform**: GPU (CUDA)',
        '',
        '## Heatmap',
        '',
        f'![L=40 GPU Heatmap]({abs_dir}/sweep_L40_heatmap.png)',
        '',
        '## Results Table',
        '',
        '| L40 rate | ≡ L400 rate | mut/gene | hill_k | Status | Δ aff | Final aff | Final div | Pop | Time |',
        '|---|---|---|---|---|---|---|---|---|---|',
    ]

    for r in results_sorted:
        lines.append(
            f"| {r['mutation_rate']} | {r['equivalent_L400_rate']} | "
            f"{r['mut_per_gene_per_div']:.2f} | {r['hill_k']} | "
            f"**{r['status']}** | {r['affinity_change']:+.4f} | "
            f"{r['final_mean_aff']:.3f} | {r['final_diversity']:.2f} | "
            f"{r['final_population']:,} | {r['elapsed_s']:.0f}s |"
        )

    lines += ['', '## Individual Plots', '']
    for r in results_sorted:
        label = f"mut{r['mutation_rate']}_k{r['hill_k']}"
        lines.append(f"### rate={r['mutation_rate']} (≡{r['equivalent_L400_rate']}@L400), K={r['hill_k']} → **{r['status']}**")
        lines.append(f"![{label}]({abs_dir}/{label}.png)")
        lines.append('')

    md_path = os.path.join(out_dir, 'SWEEP_L40_RESULTS.md')
    with open(md_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  Results MD saved to {md_path}")


def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'results', 'sweep_L40')
    os.makedirs(out_dir, exist_ok=True)

    mut_rates = SWEEP_GRID['mutation_rate']
    hill_ks = SWEEP_GRID['hill_k']

    combos = list(itertools.product(mut_rates, hill_ks))
    print(f"=== L=40 GPU Validation Sweep: {len(combos)} runs ===", flush=True)
    print(f"    mutation_rate (L=40): {mut_rates}")
    print(f"    equivalent L=400:    {[L400_RATE_MAP[r] for r in mut_rates]}")
    print(f"    hill_k: {hill_ks}")
    print(f"    N={FIXED['turbidostat_target_n']:,}, L={FIXED['shape_space_dim']}, "
          f"gamma={FIXED['affinity_gamma']}, cycles={FIXED['n_cycles']}")
    print()

    results = []
    for i, (mut_rate, hill_k) in enumerate(combos):
        print(f"--- Run {i+1}/{len(combos)} ---", flush=True)
        result = run_single(mut_rate, hill_k, out_dir)
        results.append(result)

        with open(os.path.join(out_dir, 'sweep_L40_results.json'), 'w') as f:
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
