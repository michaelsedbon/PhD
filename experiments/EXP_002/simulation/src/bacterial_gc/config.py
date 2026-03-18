"""
Configuration for the Bacterial Synthetic GC simulation (Phase 1).

Maps to experimental knobs: culture conditions, transfer protocol,
selection stringency, mutation rates.
"""

from dataclasses import dataclass


@dataclass
class BacterialConfig:
    """All parameters for the bacterial GC experiment."""

    # === Shape space (shared with Phase 0) ===
    shape_space_dim: int = 4            # L — sequence length
    affinity_gamma: float = 2.8         # Γ — Gaussian width
    affinity_eta: float = 2.0           # η — Gaussian exponent

    # === Growth ===
    growth_mode: str = "batch"          # "batch" or "turbidostat"
    carrying_capacity: int = 10_000     # K — max population (batch mode)
    doubling_time: float = 0.5          # hours (~30 min)
    dz_growth_hours: float = 6.0        # hours of growth in DZ per cycle

    # Turbidostat-specific
    turbidostat_target_n: int = 10_000  # target population maintained
    turbidostat_dilution_factor: float = 0.5  # dilute to this fraction when N exceeds 2×target

    # === Mutation ===
    mutation_rate: float = 1e-3         # probability per position per division

    # === Migration (division-triggered) ===
    dz_divisions: int = 6              # divisions before auto-migration to LZ
    unselected_return_fraction: float = 0.0  # fraction of unselected LZ cells returned to DZ

    # === Selection ===
    selection_model: str = "hill"       # "hill", "threshold", "topk", "bead_binding"
    # Hill (Model A)
    hill_n: float = 3.0                 # Hill coefficient (sharpness)
    hill_k: float = 0.3                 # Half-max affinity
    # Threshold (Model B)
    threshold: float = 0.5             # Hard affinity cutoff
    # Top-K (Model C)
    keep_fraction: float = 0.1         # Keep top 10% by affinity
    # Bead binding (Model D)
    bead_kon_scale: float = 1.0        # kon(aff) = bead_kon_scale * aff
    bead_koff_scale: float = 1.0       # koff(aff) = bead_koff_scale * (1 - aff)
    bead_concentration: float = 1.0    # [beads] in arbitrary units
    bead_incubation_time: float = 1.0  # hours
    bead_wash_time: float = 0.5        # hours

    # === Output extraction ===
    extraction_fraction: float = 0.0    # fraction of survivors extracted per cycle

    # === Experiment structure ===
    n_cycles: int = 10                  # total GC cycles
    n_founders: int = 1000             # initial library size
    initial_hamming_min: int = 4       # min Hamming distance of founders
    initial_hamming_max: int = 8       # max Hamming distance

    @property
    def growth_rate(self) -> float:
        """Exponential growth rate r = ln(2) / doubling_time."""
        import math
        return math.log(2) / self.doubling_time

    @property
    def n_doublings(self) -> float:
        """Expected doublings during DZ growth period."""
        return self.dz_growth_hours / self.doubling_time
