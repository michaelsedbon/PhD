"""
run.py — CLI entry point for the GC simulation.

Usage:
    python run.py                          # default 21-day simulation
    python run.py --days 7 --seed 123      # 7-day simulation with seed
    python run.py --snapshot-interval 200  # more frequent snapshots
"""

import argparse
import sys
import os

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
    parser = argparse.ArgumentParser(description='Germinal Center Simulation')
    parser.add_argument('--days', type=float, default=21.0, help='Simulated days')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--snapshot-interval', type=int, default=500,
                        help='Timesteps between snapshots')
    parser.add_argument('--output-dir', type=str, default='results',
                        help='Output directory for plots')
    args = parser.parse_args()

    config = GCConfig(
        total_days=args.days,
        snapshot_interval=args.snapshot_interval,
    )

    print(f"Config: {config.total_days} days, dt={config.dt}h, "
          f"{config.n_timesteps} steps")

    history = run_simulation(config, seed=args.seed)

    # Save plots
    os.makedirs(args.output_dir, exist_ok=True)
    plot_population_dynamics(history, f'{args.output_dir}/population.png')
    plot_affinity_maturation(history, f'{args.output_dir}/affinity.png')
    plot_dz_lz_ratio(history, f'{args.output_dir}/dz_lz_ratio.png')
    plot_diversity(history, f'{args.output_dir}/diversity.png')
    print(f"Plots saved to {args.output_dir}/")


if __name__ == '__main__':
    main()
