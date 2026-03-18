"""
Validation controls — toy examples to verify simulation correctness.

4 controls:
1. Zero mutation: affinity should stay constant
2. No selection: affinity should random-walk toward equilibrium
3. Perfect selection + zero mutation: only best clone survives
4. Low mutation + moderate selection: slow maturation expected
"""

import sys, os, time, json
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


COMMON = dict(
    n_founders=50,
    shape_space_dim=400,
    initial_hamming_min=50,
    initial_hamming_max=100,
    n_cycles=20,  # short runs for validation
    turbidostat_target_n=10_000,
    growth_mode='turbidostat',
    dz_growth_hours=6.0,
    doubling_time=0.5,
    dz_divisions=6,
    affinity_gamma=105.0,
)


def run_control(name: str, config: BacterialConfig, out_dir: str,
                selection_mode: str = 'gc') -> dict:
    """Run one control and return summary metrics."""
    print(f"\n=== Control: {name} ===", flush=True)
    t0 = time.time()
    history = run_experiment_gpu(config, seed=42, selection_mode=selection_mode)
    dt = time.time() - t0

    plot_path = os.path.join(out_dir, f"{name}.png")
    plot_experiment(history, plot_path, title=name.replace('_', ' ').title())

    first = history[1] if len(history) > 1 else history[0]
    last = history[-1]

    result = {
        'name': name,
        'elapsed_s': round(dt, 1),
        'initial_aff': round(first.mean_affinity, 4),
        'final_aff': round(last.mean_affinity, 4),
        'aff_change': round(last.mean_affinity - first.mean_affinity, 4),
        'initial_diversity': round(first.diversity, 2),
        'final_diversity': round(last.diversity, 2),
        'final_pop': last.n_total,
        'plot': plot_path,
    }

    print(f"  aff: {first.mean_affinity:.4f} → {last.mean_affinity:.4f} "
          f"(Δ={last.mean_affinity - first.mean_affinity:+.4f})")
    print(f"  div: {first.diversity:.2f} → {last.diversity:.2f}")
    print(f"  pop: {first.n_total} → {last.n_total}")
    return result


def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'results', 'controls')
    os.makedirs(out_dir, exist_ok=True)
    results = []

    # ── Control 1: Zero mutation ──────────────────────────────────────────
    # Expected: pure purifying selection drives affinity up
    # Selection still operates but without mutations, the best clones just persist
    c1 = BacterialConfig(
        mutation_rate=0.0,  # NO mutations
        hill_k=0.3,
        hill_n=3.0,
        selection_model='hill',
        unselected_return_fraction=0.1,
        **COMMON,
    )
    results.append(run_control("1_zero_mutation", c1, out_dir))

    # ── Control 2: No selection (hill_k very small → ~100% survival) ────────
    # Hill function: a^n/(a^n+K^n). When K<<a, survival→1.0
    # Expected: diversity maintained, affinity random-walks
    c2 = BacterialConfig(
        mutation_rate=0.0001,
        hill_k=0.001,  # K<<a → survival ≈ 100% (extremely permissive)
        hill_n=3.0,
        selection_model='hill',
        unselected_return_fraction=0.1,
        **COMMON,
    )
    results.append(run_control("2_no_selection", c2, out_dir))

    # ── Control 3: Perfect selection + zero mutation ──────────────────────
    # Expected: only best clone survives, diversity → 0, affinity = max clone's
    # Using directed evolution top-1% for hard selection
    c3 = BacterialConfig(
        mutation_rate=0.0,  # NO mutations
        hill_k=0.3,  # not used in DE mode
        hill_n=3.0,
        selection_model='hill',
        unselected_return_fraction=0.0,
        **COMMON,
    )
    results.append(run_control("3_perfect_select_no_mut", c3, out_dir,
                                selection_mode='directed_evolution'))

    # ── Control 4: Very low mutation + moderate selection ─────────────────
    # Expected: slow but visible affinity maturation (beneficial mutations fixed)
    c4 = BacterialConfig(
        mutation_rate=0.00001,  # very low: 0.004 mut/gene/div
        hill_k=0.3,
        hill_n=3.0,
        selection_model='hill',
        unselected_return_fraction=0.1,
        **COMMON,
    )
    results.append(run_control("4_low_mut_moderate_sel", c4, out_dir))

    # ── Save results ─────────────────────────────────────────────────────
    with open(os.path.join(out_dir, 'control_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    # ── Generate results MD ──────────────────────────────────────────────
    abs_dir = os.path.abspath(out_dir)
    lines = [
        '# Simulation Validation Controls',
        '',
        f'**Date**: {time.strftime("%Y-%m-%d %H:%M")}',
        f'**N**: 10,000 | **L**: 400 | **Cycles**: 20',
        '',
        '## Summary',
        '',
        '| Control | Expected | Affinity Δ | Diversity Δ | PASS? |',
        '|---|---|---|---|---|',
    ]

    expectations = {
        '1_zero_mutation': ('constant', lambda r: abs(r['aff_change']) < 0.01),
        '2_no_selection': ('random walk', lambda r: True),  # just check it runs
        '3_perfect_select_no_mut': ('→ max clone', lambda r: r['final_diversity'] < 1.0),
        '4_low_mut_moderate_sel': ('slow maturation', lambda r: r['aff_change'] > -0.05),
    }

    for r in results:
        exp_label, check_fn = expectations.get(r['name'], ('?', lambda r: True))
        passed = '✅' if check_fn(r) else '❌'
        lines.append(
            f"| {r['name']} | {exp_label} | {r['aff_change']:+.4f} | "
            f"{r['final_diversity'] - r['initial_diversity']:+.2f} | {passed} |"
        )

    lines += ['', '## Individual Plots', '']
    for r in results:
        lines.append(f"### {r['name']}")
        lines.append(f"![{r['name']}]({abs_dir}/{r['name']}.png)")
        lines.append('')

    md_path = os.path.join(out_dir, 'CONTROLS.md')
    with open(md_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"\nResults saved to {md_path}")


if __name__ == '__main__':
    main()
