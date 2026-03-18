"""
Overnight 21-day GC simulation with tuned parameters.
Run on GPU server: nohup python3 run_overnight.py > results/overnight.log 2>&1 &
"""

import sys, os, time, pickle
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
        dt=0.05,  # coarse dt for reasonable overnight runtime
        snapshot_interval=100,
        # Tuned parameters
        founder_divisions=2,    # 9h first DZ visit (close to experimental 8h)
        n_div_max=1,            # minimum recycled DZ time (4.5h)
        tc_time=1.0,            # more time for T cell selection
        collect_fdc_period=1.0, # more antigen collection time
        prob_output=0.03,       # stronger recycling → bigger GC
    )

    print(f"Overnight run: {config.total_days} days, dt={config.dt}h, "
          f"{config.n_timesteps} steps")
    print(f"Tuned params: founder_div={config.founder_divisions}, "
          f"n_div_max={config.n_div_max}, tc_time={config.tc_time}, "
          f"fdc_period={config.collect_fdc_period}, "
          f"p_output={config.prob_output}")

    t0 = time.time()
    history = run_simulation(config, seed=42)
    elapsed = time.time() - t0

    print(f"\nDone in {elapsed:.0f}s ({elapsed/3600:.1f}h)")
    print(f"ms/step: {elapsed/config.n_timesteps*1000:.0f}")

    # Save history
    with open('results/history_overnight.pkl', 'wb') as f:
        pickle.dump(history, f)

    # Save plots
    plot_population_dynamics(history, 'results/pop_overnight.png')
    plot_affinity_maturation(history, 'results/aff_overnight.png')
    plot_dz_lz_ratio(history, 'results/dzlz_overnight.png')
    plot_diversity(history, 'results/div_overnight.png')
    print("Plots saved to results/")

    # Summary
    s = history[-1]
    print(f"\nFinal (t={s.time_hours:.1f}h):")
    print(f"  CB={s.n_cb}, CC={s.n_cc}, Out={s.n_out}")
    print(f"  Mean aff CB={s.mean_affinity_cb:.4f}")
    print(f"  Max aff={s.max_affinity:.4f}")
    print(f"  DZ/LZ={s.dz_lz_ratio:.2f}")


if __name__ == '__main__':
    main()
