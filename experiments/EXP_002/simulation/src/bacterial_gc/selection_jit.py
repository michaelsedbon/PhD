"""
JIT-compiled selection for Bacterial GC — fully GPU-accelerable.

All operations use fixed-size arrays with boolean masks.
No data-dependent shapes → everything @jax.jit compilable.
"""

import jax
import jax.numpy as jnp
from functools import partial


@partial(jax.jit, static_argnums=(5, 6, 7))
def apply_selection_jit(
    affinities,   # float32[N_MAX]
    alive,        # bool[N_MAX]
    in_lz,        # bool[N_MAX]
    div_counter,  # int32[N_MAX]
    rng_key,
    hill_n,       # static float
    hill_k,       # static float
    unselected_return_fraction,  # static float
):
    """JIT-compiled Hill function selection on LZ cells.

    - LZ cells undergo Hill selection: P(survive) = a^n / (a^n + K^n)
    - Survivors reset div_counter and return to DZ
    - Dead LZ cells: fraction resurrected as "unselected return"
    - Non-LZ cells unchanged
    """
    k1, k2 = jax.random.split(rng_key)

    is_lz = alive & in_lz

    # Hill function survival — applied to ALL cells, masked later
    aff_n = jnp.power(jnp.maximum(affinities, 1e-10), hill_n)
    k_n = hill_k ** hill_n
    survival_prob = aff_n / (aff_n + k_n)

    # Bernoulli survival roll for all cells
    rolls = jax.random.uniform(k1, affinities.shape)
    survived = rolls < survival_prob

    # LZ cells that didn't survive → die
    lz_died = is_lz & ~survived
    lz_survived = is_lz & survived

    # New alive: kill LZ dead
    new_alive = alive & ~lz_died

    # Unselected return: resurrect some dead LZ cells via Bernoulli
    n_lz_dead = jnp.sum(lz_died).astype(jnp.float32)
    return_prob = jnp.minimum(unselected_return_fraction, 1.0)
    return_rolls = jax.random.uniform(k2, affinities.shape)
    should_return = lz_died & (return_rolls < return_prob)
    new_alive = new_alive | should_return

    # Reset div_counter for all LZ cells going back to DZ (survivors + returned)
    going_back = lz_survived | should_return
    new_div_counter = jnp.where(going_back, 0, div_counter)

    # Clear LZ flag for all
    new_in_lz = jnp.zeros_like(in_lz)

    return new_alive, new_in_lz, new_div_counter


@partial(jax.jit, static_argnums=(5, 6))
def apply_top_fraction_jit(
    affinities,   # float32[N_MAX]
    alive,        # bool[N_MAX]
    in_lz,        # bool[N_MAX]
    div_counter,  # int32[N_MAX]
    rng_key,
    keep_fraction, # static float — fraction of LZ cells to keep (e.g. 0.10)
    unselected_return_fraction,  # static float
):
    """Competitive selection: keep the top keep_fraction of LZ cells by affinity.

    Unlike Hill (independent), this is competitive — survival depends on
    being better than other cells, not just crossing a threshold.
    Mimics T cell help scarcity in the natural GC.
    """
    k1 = rng_key

    is_lz = alive & in_lz
    n_lz = jnp.sum(is_lz)
    n_keep = jnp.maximum((n_lz * keep_fraction).astype(jnp.int32), 1)

    # Assign priority: LZ cells get their affinity, others get -inf
    priority = jnp.where(is_lz, affinities, -jnp.inf)

    # Sort descending to find the affinity threshold for top keep_fraction
    sorted_affs = jnp.sort(priority)[::-1]
    safe_idx = jnp.clip(n_keep - 1, 0, affinities.shape[0] - 1)
    threshold = sorted_affs[safe_idx]

    # LZ cells above threshold survive, others die
    lz_survived = is_lz & (affinities >= threshold)
    lz_died = is_lz & ~lz_survived

    # New alive: kill LZ dead
    new_alive = alive & ~lz_died

    # Unselected return: resurrect some dead LZ cells via Bernoulli
    return_prob = jnp.minimum(unselected_return_fraction, 1.0)
    return_rolls = jax.random.uniform(k1, affinities.shape)
    should_return = lz_died & (return_rolls < return_prob)
    new_alive = new_alive | should_return

    # Reset div_counter for all LZ cells going back to DZ (survivors + returned)
    going_back = lz_survived | should_return
    new_div_counter = jnp.where(going_back, 0, div_counter)

    # Clear LZ flag for all
    new_in_lz = jnp.zeros_like(in_lz)

    return new_alive, new_in_lz, new_div_counter


@partial(jax.jit, static_argnums=(4,))
def apply_directed_evolution_jit(
    affinities,   # float32[N_MAX]
    alive,        # bool[N_MAX]
    div_counter,  # int32[N_MAX]
    rng_key,
    keep_fraction, # static float
):
    """JIT-compiled directed evolution: keep top-K by affinity."""
    n_alive = jnp.sum(alive)
    n_keep = jnp.maximum((n_alive * keep_fraction).astype(jnp.int32), 1)

    # Assign priority: alive cells get their affinity, dead get -inf
    priority = jnp.where(alive, affinities, -jnp.inf)

    # Sort descending, find threshold
    sorted_affs = jnp.sort(priority)[::-1]
    safe_idx = jnp.clip(n_keep - 1, 0, affinities.shape[0] - 1)
    threshold = sorted_affs[safe_idx]

    # Keep cells above threshold
    new_alive = alive & (affinities >= threshold)

    # Reset div_counter for survivors
    new_div_counter = jnp.where(new_alive, 0, div_counter)

    # Clear LZ
    new_in_lz = jnp.zeros_like(alive)

    return new_alive, new_in_lz, new_div_counter
