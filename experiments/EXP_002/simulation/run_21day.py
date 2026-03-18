"""
Run 21-day GC simulation with paper-accurate dt=0.002h on GPU.
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from germinal_center.config import GCConfig
from germinal_center.simulation import run_simulation
from germinal_center.analysis import (
    plot_population_dynamics, plot_affinity_maturation,
    plot_dz_lz_ratio, plot_diversity,
)


def main():
    os.makedirs('results', exist_ok=True)

    config = GCConfig(
        total_days=21.0,
        dt=0.002,
        snapshot_interval=5000,  # snapshot every 10h
    )

    print(f"Config: {config.total_days} days, dt={config.dt}h, "
          f"{config.n_timesteps} steps")

    t0 = time.time()
    history = run_simulation(config, seed=42)
    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s ({elapsed/3600:.1f}h)")

    import pickle
    with open('results/history_21day.pkl', 'wb') as f:
        pickle.dump(history, f)

    plot_population_dynamics(history, 'results/population_21day.png')
    plot_affinity_maturation(history, 'results/affinity_21day.png')
    plot_dz_lz_ratio(history, 'results/dz_lz_21day.png')
    plot_diversity(history, 'results/diversity_21day.png')
    print("Results saved to results/")

    s = history[-1]
    print(f"\nFinal (t={s.time_hours:.1f}h):")
    print(f"  CB={s.n_cb}, CC={s.n_cc}, Out={s.n_out}")
    print(f"  Mean aff CB={s.mean_affinity_cb:.4f}")


if __name__ == '__main__':
    main()
