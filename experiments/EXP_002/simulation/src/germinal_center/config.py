"""
Configuration dataclass for the Germinal Center simulation.

All parameters from Robert et al. "How to Simulate a Germinal Center" Tables 1-2.
Each parameter has its paper source and unit documented.
"""

from dataclasses import dataclass, field
from typing import Optional
import jax.numpy as jnp


@dataclass
class GCConfig:
    """Full configuration for the natural GC simulation (Phase 0)."""

    # === Grid ===
    grid_n: int = 80                    # lattice points per side
    dx: float = 5.0                     # µm, lattice spacing
    dt: float = 0.002                   # h, timestep (7.2 s)

    # === Simulation time ===
    total_days: float = 21.0            # simulated days
    snapshot_interval: int = 500        # timesteps between snapshots

    # === Shape space (Algorithm 1, §2.2) ===
    shape_space_dim: int = 4            # L — number of dimensions
    affinity_gamma: float = 2.8         # Γ — Gaussian width
    affinity_eta: float = 2.0           # η — Gaussian exponent (default 2 from paper)

    # === Chemotaxis (Algorithm 2) ===
    diffusion_D: float = 1000.0         # µm²/h, diffusion coefficient
    cxcl12_production: float = 1.0      # relative production rate
    cxcl13_production: float = 1.0      # relative production rate
    desensitize_threshold: float = 0.5  # concentration above which receptor desensitizes
    resensitize_threshold: float = 0.1  # concentration below which receptor resensitizes

    # === Movement (Algorithm 3) ===
    speed_cb: float = 7.5               # µm/min, centroblast speed
    speed_cc: float = 5.0               # µm/min, centrocyte speed
    speed_tc: float = 5.0               # µm/min, T cell speed
    speed_out: float = 5.0              # µm/min, output cell speed
    persistence_time: float = 0.025     # h, polarity persistence (1.5 min)
    chemo_weight: float = 0.5           # weight of chemokine gradient vs. persistence

    # === Cell cycle (Algorithm 4) ===
    phase_g1: float = 1.0               # h
    phase_s: float = 2.0                # h
    phase_g2: float = 1.0               # h
    phase_m: float = 0.5                # h
    # Total ~4.5h per cycle, ~6h with variation

    # === Mutation (Algorithm 1) ===
    mutation_prob: float = 0.5          # probability of mutation per division
    lethal_fraction: float = 0.3        # fraction of mutations that are lethal

    # === Selection — FDC contacts (Algorithm 5) ===
    collect_fdc_period: float = 0.7     # h, time centrocyte spends trying to collect antigen
    antigen_saturation: float = 1.0     # normalized antigen amount per FDC fragment

    # === Selection — T cell help (Algorithms 6-7) ===
    tc_time: float = 0.5               # h, max time centrocyte can wait for T cell help
    tc_rescue_time: float = 2.0        # h, signaling time needed to be rescued

    # === Differentiation (Algorithm 8) ===
    diff_delay: float = 0.5            # h, delay before differentiation decision
    prob_output: float = 0.05          # probability of becoming output cell (vs. recycle)
    n_div_hill_n: float = 2.0          # Hill coefficient for division count
    n_div_hill_k: float = 0.5          # Hill half-max for division count
    n_div_min: int = 1                 # min divisions after recycling
    n_div_max: int = 6                 # max divisions after recycling

    # === Initialization (Algorithm 9) ===
    n_founders: int = 100              # initial B cell clones
    n_fdcs: int = 20                   # FDCs in light zone
    n_fdc_arms: int = 6                # dendrite arms per FDC
    n_antigen_per_fdc: int = 300       # antigen portions per FDC
    n_tcells: int = 100                # Tfh cells in light zone
    n_stromal: int = 50                # CXCL12-producing cells in dark zone
    initial_hamming_min: int = 4       # min Hamming distance of founders
    initial_hamming_max: int = 8       # max Hamming distance of founders
    founder_divisions: int = 6         # divisions before first LZ entry
    inflow_hours: float = 72.0         # h, duration of founder cell inflow (~3 days)

    # === Derived properties ===
    @property
    def n_timesteps(self) -> int:
        """Total number of timesteps."""
        return int(self.total_days * 24.0 / self.dt)

    @property
    def grid_radius(self) -> float:
        """GC sphere radius in grid points."""
        return self.grid_n / 2.0

    @property
    def grid_center(self) -> int:
        """Center of the lattice."""
        return self.grid_n // 2

    @property
    def speed_cb_grid(self) -> float:
        """CB speed in grid points per timestep."""
        return (self.speed_cb * 60.0 * self.dt) / self.dx  # µm/min → grid/dt

    @property
    def speed_cc_grid(self) -> float:
        """CC speed in grid points per timestep."""
        return (self.speed_cc * 60.0 * self.dt) / self.dx

    @property
    def diffusion_alpha(self) -> float:
        """Diffusion stability parameter: α = D*dt/dx²."""
        return self.diffusion_D * self.dt / (self.dx ** 2)
