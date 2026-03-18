"""
Run 7-day GC simulation with dt=0.05 (fast preview mode).
Save snapshots, history pickle, and plots.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from germinal_center.config import GCConfig
from germinal_center.simulation import run_simulation
from germinal_center.analysis import (
    plot_population_dynamics,
    plot_affinity_maturation,
    plot_dz_lz_ratio,
    plot_diversity,
)


def main():
    os.makedirs('results', exist_ok=True)

    config = GCConfig(
        total_days=7.0,
        dt=0.05,
        snapshot_interval=50,
    )

    print(f"Config: {config.total_days} days, dt={config.dt}h, "
          f"{config.n_timesteps} steps")
    print(f"Expected time: ~{config.n_timesteps * 1.5 / 60:.0f} min")

    t0 = time.time()
    history = run_simulation(config, seed=42)
    elapsed = time.time() - t0

    print(f"\nDone in {elapsed:.0f}s ({elapsed/60:.1f} min)")

    # Save history
    import pickle
    with open('results/history_7day.pkl', 'wb') as f:
        pickle.dump(history, f)
    print("Saved history to results/history_7day.pkl")

    # Save plots
    plot_population_dynamics(history, 'results/population_7day.png')
    plot_affinity_maturation(history, 'results/affinity_7day.png')
    plot_dz_lz_ratio(history, 'results/dz_lz_7day.png')
    plot_diversity(history, 'results/diversity_7day.png')
    print("Plots saved to results/")

    # Print final stats
    s = history[-1]
    print(f"\nFinal state (t={s.time_hours:.1f}h):")
    print(f"  CB: {s.n_cb}")
    print(f"  CC: {s.n_cc}")
    print(f"  Output: {s.n_out}")
    print(f"  Mean CB affinity: {s.mean_affinity_cb:.4f}")


if __name__ == '__main__':
    main()
