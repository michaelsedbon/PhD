"""
Shape space, Hamming distance, affinity, and mutation.

Implements the core sequence representation from §2.2 and Algorithm 1
of Robert et al. "How to Simulate a Germinal Center".

Shape space: each BCR and antigen is a vector of L integers.
Affinity = exp(−(d/Γ)^η) where d = Hamming distance.
Mutation: ±1 on one random position.
"""

import jax
import jax.numpy as jnp
from functools import partial


# ─── Single-sequence functions ──────────────────────────────────────────────


def hamming_distance(a: jnp.ndarray, b: jnp.ndarray) -> jnp.ndarray:
    """Hamming distance between two shape-space sequences.

    Args:
        a: int array of shape (L,)
        b: int array of shape (L,)
    Returns:
        Scalar int — number of differing positions.
    """
    return jnp.sum(a != b)


def compute_affinity(
    bcr: jnp.ndarray,
    antigen: jnp.ndarray,
    gamma: float = 2.8,
    eta: float = 2.0,
) -> jnp.ndarray:
    """Compute binding affinity between a BCR and antigen via shape space.

    Affinity = exp(−(d / Γ)^η)
    where d = Hamming distance, Γ = width, η = exponent.

    Paper §2.2: "The affinity of the antibody is calculated as a function
    of the distance of the B-cell receptor in shape space to the antigen."

    Args:
        bcr: int array (L,) — BCR sequence in shape space.
        antigen: int array (L,) — antigen sequence in shape space.
        gamma: Gaussian width parameter Γ.
        eta: Gaussian exponent η (typically 2).
    Returns:
        Scalar float in [0, 1]. 1 = perfect match, ~0 = distant.
    """
    d = hamming_distance(bcr, antigen)
    return jnp.exp(-((d / gamma) ** eta))


@partial(jax.jit, static_argnums=(3,))
def mutate_sequence(
    seq: jnp.ndarray,
    rng_key: jnp.ndarray,
    n_values: int = 10,
    L: int = 4,
) -> jnp.ndarray:
    """Mutate a shape-space sequence: ±1 on one random position.

    Paper Algorithm 1: "pick random position, change by ±1"
    Values wrap around [0, n_values).

    Args:
        seq: int array (L,) — current sequence.
        rng_key: JAX PRNG key.
        n_values: number of possible values per position (default 10).
        L: sequence length (static for JIT).
    Returns:
        Mutated int array (L,).
    """
    k1, k2 = jax.random.split(rng_key)

    # Pick random position to mutate
    pos = jax.random.randint(k1, (), 0, L)

    # Pick direction: +1 or -1
    direction = jax.random.choice(k2, jnp.array([-1, 1]))

    # Apply mutation with wrapping
    new_val = (seq[pos] + direction) % n_values
    return seq.at[pos].set(new_val)


# ─── Batched / vectorized functions ────────────────────────────────────────


@jax.jit
def batch_hamming(bcrs: jnp.ndarray, antigen: jnp.ndarray) -> jnp.ndarray:
    """Hamming distance for a batch of BCRs against one antigen.

    Args:
        bcrs: int array (N, L)
        antigen: int array (L,)
    Returns:
        int array (N,) — distances.
    """
    return jnp.sum(bcrs != antigen[None, :], axis=1)


@jax.jit
def batch_affinity(
    bcrs: jnp.ndarray,
    antigen: jnp.ndarray,
    gamma: float = 2.8,
    eta: float = 2.0,
) -> jnp.ndarray:
    """Compute affinity for a batch of BCRs against one antigen.

    Args:
        bcrs: int array (N, L)
        antigen: int array (L,)
        gamma: Gaussian width Γ.
        eta: Gaussian exponent η.
    Returns:
        float array (N,) — affinities in [0, 1].
    """
    d = batch_hamming(bcrs, antigen)
    return jnp.exp(-((d / gamma) ** eta))


def batch_mutate(
    seqs: jnp.ndarray,
    rng_key: jnp.ndarray,
    mutation_mask: jnp.ndarray,
    n_values: int = 10,
) -> jnp.ndarray:
    """Apply mutations to a batch of sequences.

    Only sequences where mutation_mask=True are mutated.

    Args:
        seqs: int array (N, L)
        rng_key: JAX PRNG key.
        mutation_mask: bool array (N,) — which sequences to mutate.
        n_values: number of possible values per position.
    Returns:
        int array (N, L) — sequences with mutations applied.
    """
    N, L = seqs.shape
    keys = jax.random.split(rng_key, N)

    def _maybe_mutate(seq, key, should_mutate):
        mutated = mutate_sequence(seq, key, n_values, L)
        return jnp.where(should_mutate, mutated, seq)

    return jax.vmap(_maybe_mutate)(seqs, keys, mutation_mask)


# ─── Initialization helpers ────────────────────────────────────────────────


def create_antigen(L: int = 4, rng_key: jnp.ndarray = None, n_values: int = 10) -> jnp.ndarray:
    """Create a fixed antigen sequence.

    Args:
        L: shape space dimension.
        rng_key: JAX PRNG key (if None, uses zeros as antigen).
        n_values: values per position.
    Returns:
        int array (L,) — the antigen.
    """
    if rng_key is None:
        return jnp.zeros(L, dtype=jnp.int32)
    return jax.random.randint(rng_key, (L,), 0, n_values)


def create_founders_at_distance(
    n: int,
    antigen: jnp.ndarray,
    hamming_min: int,
    hamming_max: int,
    rng_key: jnp.ndarray,
    n_values: int = 10,
) -> jnp.ndarray:
    """Create founder BCR sequences at a given Hamming distance from antigen.

    Paper Algorithm 9: "Initial BCR at Hamming distance 4-8 from antigen."

    Strategy: start from antigen, flip `d` random positions by a random offset.

    Args:
        n: number of founders.
        antigen: int array (L,)
        hamming_min: min Hamming distance.
        hamming_max: max Hamming distance.
        rng_key: JAX PRNG key.
        n_values: values per position.
    Returns:
        int array (n, L) — founder BCR sequences.
    """
    L = antigen.shape[0]
    founders = jnp.tile(antigen, (n, 1))  # Start from antigen

    k1, k2, k3 = jax.random.split(rng_key, 3)

    # Random Hamming distance for each founder
    distances = jax.random.randint(k1, (n,), hamming_min, hamming_max + 1)

    # For each founder, pick `d` positions to flip and apply random offsets
    # Since d varies per founder, we use a mask approach:
    # Generate random position priorities, take top-d, apply offset
    position_priorities = jax.random.uniform(k2, (n, L))
    offsets = jax.random.randint(k3, (n, L), 1, n_values)  # offset ∈ [1, n_values)

    # Create mask: flip positions with lowest priority up to `d` positions
    # Sort priorities, threshold at d-th value
    sorted_priorities = jnp.sort(position_priorities, axis=1)
    thresholds = jnp.take_along_axis(
        sorted_priorities,
        jnp.clip(distances - 1, 0, L - 1)[:, None],
        axis=1,
    )[:, 0]
    flip_mask = position_priorities <= thresholds[:, None]

    # Apply flips
    flipped = (founders + offsets * flip_mask) % n_values

    return flipped.astype(jnp.int32)
