"""
Analysis — snapshots, plotting, and history persistence for the bacterial GC.
"""

import json
import csv
import os
import jax.numpy as jnp
import numpy as np

from .state import BacterialState, Snapshot, DZ, LZ, EXTRACTED


def save_history(history: list, base_path: str):
    """Save per-cycle snapshot history as both JSON and CSV.
    
    Args:
        history: List of Snapshot namedtuples from a simulation run.
        base_path: Path without extension. Will create {base_path}.json and {base_path}.csv
    """
    records = []
    for snap in history:
        records.append({
            'cycle': int(snap.cycle),
            'n_total': int(snap.n_total),
            'n_dz': int(snap.n_dz),
            'n_lz': int(snap.n_lz),
            'n_extracted': int(snap.n_extracted),
            'mean_affinity': round(float(snap.mean_affinity), 6),
            'max_affinity': round(float(snap.max_affinity), 6),
            'median_affinity': round(float(snap.median_affinity), 6),
            'std_affinity': round(float(snap.std_affinity), 6),
            'diversity': round(float(snap.diversity), 4),
            'n_unique_clones': int(snap.n_unique_clones),
            'top_clone_fraction': round(float(snap.top_clone_fraction), 6),
        })
    
    # JSON
    json_path = base_path + '.json'
    with open(json_path, 'w') as f:
        json.dump(records, f, indent=2)
    
    # CSV
    csv_path = base_path + '.csv'
    if records:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
    
    print(f"  History saved: {json_path} ({len(records)} cycles)")


def load_history(base_path: str) -> list:
    """Load history from JSON, returning list of Snapshot namedtuples."""
    json_path = base_path + '.json'
    with open(json_path, 'r') as f:
        records = json.load(f)
    
    return [Snapshot(**r) for r in records]


def snapshot(state: BacterialState) -> Snapshot:
    """Capture metrics at this point in time."""
    alive = state.alive
    affs = state.affinities[alive] if jnp.any(alive) else jnp.array([0.0])

    # Clone diversity (Shannon entropy)
    clones = state.clone_id[alive] if jnp.any(alive) else jnp.array([0])
    unique, counts = jnp.unique(clones, return_counts=True, size=min(int(jnp.sum(alive)), 10000))
    counts = counts[counts > 0]
    total = jnp.sum(counts)
    probs = counts / jnp.maximum(total, 1)
    entropy = -jnp.sum(probs * jnp.log(probs + 1e-10))

    n_alive = int(jnp.sum(alive))
    top_clone_frac = float(jnp.max(counts) / jnp.maximum(total, 1)) if n_alive > 0 else 0.0

    return Snapshot(
        cycle=state.cycle,
        n_total=n_alive,
        n_dz=int(jnp.sum(alive & (state.compartment == DZ))),
        n_lz=int(jnp.sum(alive & (state.compartment == LZ))),
        n_extracted=int(jnp.sum(state.compartment == EXTRACTED)),
        mean_affinity=float(jnp.mean(affs)),
        max_affinity=float(jnp.max(affs)),
        median_affinity=float(jnp.median(affs)),
        std_affinity=float(jnp.std(affs)),
        diversity=float(entropy),
        n_unique_clones=int(counts.shape[0]),
        top_clone_fraction=top_clone_frac,
    )


def plot_experiment(history: list, save_path: str = None, title: str = 'Bacterial GC Experiment'):
    """Generate 4-panel overview of the experiment."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available, skipping plots")
        return

    cycles = [s.cycle for s in history]
    n_total = [s.n_total for s in history]
    mean_aff = [s.mean_affinity for s in history]
    max_aff = [s.max_affinity for s in history]
    median_aff = [s.median_affinity for s in history]
    diversity = [s.diversity for s in history]
    n_clones = [s.n_unique_clones for s in history]
    top_frac = [s.top_clone_fraction for s in history]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(title, fontsize=14, fontweight='bold')

    # Population
    ax = axes[0, 0]
    ax.plot(cycles, n_total, 'b-o', markersize=4)
    ax.set_ylabel('Population')
    ax.set_title('Population Dynamics')
    ax.set_xlabel('Cycle')
    ax.grid(True, alpha=0.3)

    # Affinity
    ax = axes[0, 1]
    ax.plot(cycles, mean_aff, 'b-o', markersize=4, label='Mean')
    ax.plot(cycles, max_aff, 'orange', marker='o', markersize=4, label='Max')
    ax.plot(cycles, median_aff, 'g--', markersize=3, label='Median')
    ax.set_ylabel('Affinity')
    ax.set_title('Affinity Maturation')
    ax.set_xlabel('Cycle')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Diversity
    ax = axes[1, 0]
    ax.plot(cycles, diversity, 'r-o', markersize=4)
    ax.set_ylabel('Shannon Entropy')
    ax.set_title('Clonal Diversity')
    ax.set_xlabel('Cycle')
    ax.grid(True, alpha=0.3)

    # Clone dominance
    ax = axes[1, 1]
    ax.plot(cycles, top_frac, 'm-o', markersize=4, label='Top clone fraction')
    ax2 = ax.twinx()
    ax2.plot(cycles, n_clones, 'c--', markersize=3, label='Unique clones')
    ax2.set_ylabel('Unique clones', color='c')
    ax.set_ylabel('Top clone fraction', color='m')
    ax.set_title('Clone Dominance')
    ax.set_xlabel('Cycle')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.close()
