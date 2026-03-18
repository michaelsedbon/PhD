"""
Selection — 4 models for affinity-based selection in the LZ well.

Model A: Hill function (soft proportional)
Model B: Hard threshold
Model C: Top-K (tournament)
Model D: Physics-based bead binding
"""

import jax
import jax.numpy as jnp

from .state import BacterialState, LZ


def apply_selection(
    state: BacterialState,
    config,
    rng_key: jnp.ndarray,
) -> BacterialState:
    """Apply selection to LZ bacteria. Dispatcher for models A-D."""
    lz_mask = state.alive & (state.compartment == LZ)
    lz_affinities = state.affinities

    if config.selection_model == "hill":
        survive = select_hill(lz_affinities, config.hill_n, config.hill_k, rng_key)
    elif config.selection_model == "threshold":
        survive = select_threshold(lz_affinities, config.threshold)
    elif config.selection_model == "topk":
        survive = select_topk(lz_affinities, config.keep_fraction)
    elif config.selection_model == "bead_binding":
        survive = select_bead_binding(
            lz_affinities,
            config.bead_kon_scale, config.bead_koff_scale,
            config.bead_concentration,
            config.bead_incubation_time, config.bead_wash_time,
            rng_key,
        )
    else:
        raise ValueError(f"Unknown selection model: {config.selection_model}")

    # Only apply to LZ cells
    new_alive = state.alive & (~lz_mask | (lz_mask & survive))

    return state._replace(alive=new_alive)


def select_hill(
    affinities: jnp.ndarray,
    n: float,
    k: float,
    rng_key: jnp.ndarray,
) -> jnp.ndarray:
    """Model A: Hill function — soft proportional selection.

    P(survive) = aff^n / (aff^n + K^n)
    Higher affinity → higher survival probability.
    """
    aff_n = jnp.power(jnp.maximum(affinities, 0.0), n)
    k_n = k ** n
    p_survive = aff_n / (aff_n + k_n + 1e-10)

    rolls = jax.random.uniform(rng_key, affinities.shape)
    return rolls < p_survive


def select_threshold(
    affinities: jnp.ndarray,
    threshold: float,
) -> jnp.ndarray:
    """Model B: Hard threshold — survive if affinity > threshold."""
    return affinities >= threshold


def select_topk(
    affinities: jnp.ndarray,
    keep_fraction: float,
) -> jnp.ndarray:
    """Model C: Tournament — keep top fraction by affinity."""
    n_keep = max(1, int(affinities.shape[0] * keep_fraction))
    # Get the threshold that keeps top n_keep
    sorted_affs = jnp.sort(affinities)[::-1]
    cutoff = sorted_affs[min(n_keep - 1, sorted_affs.shape[0] - 1)]
    return affinities >= cutoff


def select_bead_binding(
    affinities: jnp.ndarray,
    kon_scale: float,
    koff_scale: float,
    bead_conc: float,
    t_incub: float,
    t_wash: float,
    rng_key: jnp.ndarray,
) -> jnp.ndarray:
    """Model D: Physics-based bead binding.

    P(bind)  = 1 - exp(-kon(aff) × [beads] × t_incub)
    P(stay)  = exp(-koff(aff) × t_wash)
    P(survive) = P(bind) × P(stay)
    """
    kon = kon_scale * affinities
    koff = koff_scale * (1.0 - affinities)

    p_bind = 1.0 - jnp.exp(-kon * bead_conc * t_incub)
    p_stay = jnp.exp(-koff * t_wash)
    p_survive = p_bind * p_stay

    k1, k2 = jax.random.split(rng_key)
    roll_bind = jax.random.uniform(k1, affinities.shape)
    roll_stay = jax.random.uniform(k2, affinities.shape)

    return (roll_bind < p_bind) & (roll_stay < p_stay)
