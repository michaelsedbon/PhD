"""
GPU-optimized selection for Bacterial GC.

Hill-function selection on LZ cells.
Outer function is NOT JIT'd (uses dynamic indexing for unselected return).
Inner vectorized ops use GPU acceleration via JAX.
"""

import jax
import jax.numpy as jnp

from .state_gpu import BacterialStateGPU


def apply_selection_gpu(
    state: BacterialStateGPU,
    rng_key: jnp.ndarray,
    hill_n: float,
    hill_k: float,
    unselected_return_fraction: float,
) -> BacterialStateGPU:
    """Apply Hill-function selection to cells in LZ.

    - Cells in LZ undergo selection
    - Survival probability: aff^n / (aff^n + K^n)
    - Survivors: reset div_counter, mark back to DZ
    - Dead: marked as not alive
    - Unselected return: fraction of dead LZ cells resurrected to DZ
    """
    k1, k2 = jax.random.split(rng_key)

    lz_idx = jnp.where(state.alive & state.in_lz)[0]
    n_lz = lz_idx.shape[0]

    if n_lz == 0:
        # No cells in LZ — clear in_lz flag and return
        return state._replace(in_lz=jnp.zeros_like(state.in_lz))

    # Hill function survival probability
    affs = state.affinities[lz_idx]
    aff_n = jnp.power(jnp.maximum(affs, 1e-10), hill_n)
    k_n = hill_k ** hill_n
    survival_prob = aff_n / (aff_n + k_n)

    # Bernoulli survival
    survived = jax.random.uniform(k1, (n_lz,)) < survival_prob

    survivor_idx = lz_idx[survived]
    dead_idx = lz_idx[~survived]
    n_dead = dead_idx.shape[0]

    # Kill dead LZ cells
    new_alive = state.alive.at[dead_idx].set(False)

    # Reset div_counter for survivors (going back to DZ)
    new_div_counter = state.div_counter.at[survivor_idx].set(0)

    # Unselected return: resurrect fraction of dead LZ cells
    n_return = int(n_dead * unselected_return_fraction)
    if n_return > 0 and n_dead > 0:
        return_idx = jax.random.choice(k2, dead_idx, shape=(n_return,), replace=False)
        new_alive = new_alive.at[return_idx].set(True)
        new_div_counter = new_div_counter.at[return_idx].set(0)

    # Clear LZ flag for all
    new_in_lz = jnp.zeros_like(state.in_lz)

    return state._replace(
        alive=new_alive,
        div_counter=new_div_counter,
        in_lz=new_in_lz,
    )


def apply_directed_evolution(
    state: BacterialStateGPU,
    rng_key: jnp.ndarray,
    keep_fraction: float = 0.01,
) -> BacterialStateGPU:
    """Standard directed evolution: keep top keep_fraction by affinity, kill rest.

    This is the baseline comparison for the GC architecture.
    No unselected return, no probabilistic selection — pure top-K.
    All alive cells go through selection (no DZ/LZ distinction).

    Args:
        state: Current population state.
        rng_key: PRNG key (unused but kept for API consistency).
        keep_fraction: Fraction of population to keep (e.g., 0.01 = top 1%).
    """
    alive_idx = jnp.where(state.alive)[0]
    n_alive = alive_idx.shape[0]

    if n_alive == 0:
        return state._replace(in_lz=jnp.zeros_like(state.in_lz))

    # Sort alive cells by affinity (descending)
    alive_affs = state.affinities[alive_idx]
    n_keep = max(int(n_alive * keep_fraction), 1)

    # Top-K: keep highest affinity
    top_k_local = jnp.argsort(-alive_affs)[:n_keep]
    keep_idx = alive_idx[top_k_local]

    # Kill all, resurrect keepers
    new_alive = jnp.zeros_like(state.alive)
    new_alive = new_alive.at[keep_idx].set(True)

    # Reset div_counter for survivors
    new_div_counter = state.div_counter.at[keep_idx].set(0)

    # Clear LZ flag
    new_in_lz = jnp.zeros_like(state.in_lz)

    return state._replace(
        alive=new_alive,
        div_counter=new_div_counter,
        in_lz=new_in_lz,
    )

