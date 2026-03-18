"""
Analysis — metrics computation and plotting for GC simulation.

Provides:
  - Snapshot: dataclass capturing key metrics at a point in time
  - Population dynamics plots (N_CB, N_CC, N_out vs time)
  - Affinity maturation curves (mean/max affinity vs time)
  - DZ/LZ ratio vs time
  - Clone diversity (Shannon entropy)
"""

import jax.numpy as jnp
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

from .state import GCState, count_cells


@dataclass
class Snapshot:
    """A snapshot of the GC state at a point in time."""
    time: float                    # hours
    n_cb: int                      # centroblast count
    n_cc: int                      # centrocyte count
    n_tc: int                      # T cell count
    n_out: int                     # output cell count
    n_bcells: int                  # total B cells (CB + CC)
    mean_affinity_cb: float        # mean affinity of centroblasts
    mean_affinity_cc: float        # mean affinity of centrocytes
    max_affinity: float            # max affinity across all B cells
    mean_affinity_out: float       # mean affinity of output cells
    dz_lz_ratio: float            # CB/(CC+1) ratio
    diversity_cb: float            # Shannon entropy of CB clone frequencies
    n_unique_clones: int           # number of unique clones


def snapshot(state: GCState) -> Snapshot:
    """Take a snapshot of the current GC state.

    Args:
        state: GCState
    Returns:
        Snapshot with computed metrics.
    """
    counts = count_cells(state)

    # Affinity statistics
    cb_aff = state.centroblasts.affinity
    cc_aff = state.centrocytes.affinity
    out_aff = state.output_cells.affinity

    cb_alive = state.centroblasts.alive
    cc_alive = state.centrocytes.alive
    out_alive = state.output_cells.alive

    mean_aff_cb = float(jnp.where(
        jnp.sum(cb_alive) > 0,
        jnp.sum(cb_aff * cb_alive) / jnp.maximum(jnp.sum(cb_alive), 1),
        0.0,
    ))
    mean_aff_cc = float(jnp.where(
        jnp.sum(cc_alive) > 0,
        jnp.sum(cc_aff * cc_alive) / jnp.maximum(jnp.sum(cc_alive), 1),
        0.0,
    ))
    mean_aff_out = float(jnp.where(
        jnp.sum(out_alive) > 0,
        jnp.sum(out_aff * out_alive) / jnp.maximum(jnp.sum(out_alive), 1),
        0.0,
    ))

    # Max affinity
    all_affinities = jnp.concatenate([
        cb_aff * cb_alive,
        cc_aff * cc_alive,
    ])
    max_aff = float(jnp.max(all_affinities)) if all_affinities.shape[0] > 0 else 0.0

    # DZ / LZ ratio
    n_cb = counts['n_cb']
    n_cc = counts['n_cc']
    dz_lz = n_cb / max(n_cc, 1)

    # Clone diversity (Shannon entropy)
    if n_cb > 0:
        clone_ids = state.centroblasts.clone_id[state.centroblasts.alive]
        unique_clones, clone_counts = jnp.unique(
            clone_ids, return_counts=True, size=n_cb,
        )
        freqs = clone_counts / jnp.sum(clone_counts)
        freqs = freqs[freqs > 0]
        diversity = float(-jnp.sum(freqs * jnp.log(freqs + 1e-10)))
        n_unique = int(jnp.sum(clone_counts > 0))
    else:
        diversity = 0.0
        n_unique = 0

    return Snapshot(
        time=float(state.time),
        n_cb=n_cb,
        n_cc=n_cc,
        n_tc=counts['n_tc'],
        n_out=counts['n_out'],
        n_bcells=counts['n_bcells'],
        mean_affinity_cb=mean_aff_cb,
        mean_affinity_cc=mean_aff_cc,
        max_affinity=max_aff,
        mean_affinity_out=mean_aff_out,
        dz_lz_ratio=dz_lz,
        diversity_cb=diversity,
        n_unique_clones=n_unique,
    )


# ─── Plotting functions ──────────────────────────────────────────────────


def plot_population_dynamics(history: List[Snapshot], save_path: Optional[str] = None):
    """Plot cell population dynamics over time.

    Args:
        history: list of Snapshots
        save_path: if provided, save figure to this path
    """
    import matplotlib.pyplot as plt

    times = [s.time / 24.0 for s in history]  # Convert to days
    n_cb = [s.n_cb for s in history]
    n_cc = [s.n_cc for s in history]
    n_out = [s.n_out for s in history]
    n_total = [s.n_bcells for s in history]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(times, n_cb, label='Centroblasts (DZ)', color='#4a9eff', linewidth=2)
    ax.plot(times, n_cc, label='Centrocytes (LZ)', color='#ff6b6b', linewidth=2)
    ax.plot(times, n_out, label='Output cells', color='#50c878', linewidth=2)
    ax.plot(times, n_total, label='Total B cells', color='#333', linewidth=2, linestyle='--')

    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Cell count', fontsize=12)
    ax.set_title('GC Population Dynamics', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def plot_affinity_maturation(history: List[Snapshot], save_path: Optional[str] = None):
    """Plot affinity maturation over time.

    Args:
        history: list of Snapshots
        save_path: if provided, save figure
    """
    import matplotlib.pyplot as plt

    times = [s.time / 24.0 for s in history]
    mean_cb = [s.mean_affinity_cb for s in history]
    mean_cc = [s.mean_affinity_cc for s in history]
    max_aff = [s.max_affinity for s in history]
    mean_out = [s.mean_affinity_out for s in history]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(times, mean_cb, label='Mean (CB)', color='#4a9eff', linewidth=2)
    ax.plot(times, mean_cc, label='Mean (CC)', color='#ff6b6b', linewidth=2)
    ax.plot(times, max_aff, label='Max (all B)', color='#ffa500', linewidth=2)
    ax.plot(times, mean_out, label='Mean (output)', color='#50c878', linewidth=2, linestyle='--')

    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Affinity', fontsize=12)
    ax.set_title('Affinity Maturation', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def plot_dz_lz_ratio(history: List[Snapshot], save_path: Optional[str] = None):
    """Plot DZ/LZ cell ratio over time.

    Args:
        history: list of Snapshots
        save_path: if provided, save figure
    """
    import matplotlib.pyplot as plt

    times = [s.time / 24.0 for s in history]
    ratios = [s.dz_lz_ratio for s in history]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, ratios, color='#7c3aed', linewidth=2)
    ax.axhline(y=2.0, color='gray', linestyle='--', alpha=0.5, label='Expected ~2:1')
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('DZ/LZ ratio (CB/CC)', fontsize=12)
    ax.set_title('Dark Zone / Light Zone Ratio', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def plot_diversity(history: List[Snapshot], save_path: Optional[str] = None):
    """Plot clonal diversity over time.

    Args:
        history: list of Snapshots
        save_path: if provided, save figure
    """
    import matplotlib.pyplot as plt

    times = [s.time / 24.0 for s in history]
    diversity = [s.diversity_cb for s in history]
    n_clones = [s.n_unique_clones for s in history]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(times, diversity, color='#e91e63', linewidth=2)
    ax1.set_xlabel('Time (days)', fontsize=12)
    ax1.set_ylabel('Shannon entropy', fontsize=12)
    ax1.set_title('Clonal Diversity', fontsize=14)
    ax1.grid(True, alpha=0.3)

    ax2.plot(times, n_clones, color='#009688', linewidth=2)
    ax2.set_xlabel('Time (days)', fontsize=12)
    ax2.set_ylabel('Unique clones', fontsize=12)
    ax2.set_title('Clone Count', fontsize=14)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig
