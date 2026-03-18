#!/usr/bin/env python3
"""
GPU runner for Bacterial GC simulation.

Usage on server:
    source .venv/bin/activate
    python3 run_gpu.py
"""

import sys
sys.path.insert(0, 'src')

from bacterial_gc.config import BacterialConfig
from bacterial_gc.simulation_gpu import run_experiment_gpu
from bacterial_gc.analysis import plot_experiment


def main():
    config = BacterialConfig(
        n_founders=50,
        shape_space_dim=400,            # 360bp nanobody gene
        initial_hamming_min=50,
        initial_hamming_max=100,
        n_cycles=140,                    # 7 days (~20 cycles/day)
        turbidostat_target_n=1_000_000,  # 10^6 cells
        growth_mode='turbidostat',
        dz_growth_hours=6.0,
        doubling_time=0.5,
        dz_divisions=6,
        mutation_rate=0.0005,            # T7 peak: ~0.18 mut/gene/gen
        selection_model='hill',
        hill_n=3.0,
        hill_k=0.3,
        unselected_return_fraction=0.1,  # realistic bead selection
        affinity_gamma=105.0,
    )

    import time
    print(f"=== Bacterial GC GPU Run ===")
    print(f"N_target={config.turbidostat_target_n:,}")
    print(f"L={config.shape_space_dim}, cycles={config.n_cycles}")
    print(f"mut_rate={config.mutation_rate}, unsel_return={config.unselected_return_fraction}")
    print()

    t0 = time.time()
    history = run_experiment_gpu(config, seed=42)
    elapsed = time.time() - t0

    plot_experiment(history, 'results/bacterial_gpu_L400.png')
    print(f"\nTotal: {elapsed:.1f}s ({elapsed/60:.1f}min)")


if __name__ == '__main__':
    main()
