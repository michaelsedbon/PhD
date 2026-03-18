"""
Germinal Center Simulation — Phase 0 (Paper Reproduction)

Implements the hyphasma model from:
  Robert et al. "How to Simulate a Germinal Center" (2017)
"""

from .config import GCConfig
from .state import GCState
from .affinity import compute_affinity, hamming_distance, mutate_sequence

__all__ = [
    'GCConfig',
    'GCState',
    'compute_affinity',
    'hamming_distance',
    'mutate_sequence',
]
