"""
Unit tests for the affinity module.

Tests:
  - Hamming distance: known inputs/outputs
  - Affinity: distance 0 → 1.0, distance L → near-zero
  - Mutation: output differs in exactly one position by ±1
  - Batch versions produce same results
  - Founder creation at correct distances
"""

import pytest
import jax
import jax.numpy as jnp
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from germinal_center.affinity import (
    hamming_distance,
    compute_affinity,
    mutate_sequence,
    batch_hamming,
    batch_affinity,
    batch_mutate,
    create_antigen,
    create_founders_at_distance,
)


class TestHammingDistance:
    def test_identical(self):
        a = jnp.array([1, 2, 3, 4])
        assert hamming_distance(a, a) == 0

    def test_all_different(self):
        a = jnp.array([1, 2, 3, 4])
        b = jnp.array([5, 6, 7, 8])
        assert hamming_distance(a, b) == 4

    def test_one_different(self):
        a = jnp.array([1, 2, 3, 4])
        b = jnp.array([1, 2, 3, 5])
        assert hamming_distance(a, b) == 1

    def test_two_different(self):
        a = jnp.array([1, 2, 3, 4])
        b = jnp.array([1, 5, 3, 8])
        assert hamming_distance(a, b) == 2


class TestAffinity:
    def test_perfect_match(self):
        """Distance 0 should give affinity 1.0."""
        a = jnp.array([1, 2, 3, 4])
        aff = compute_affinity(a, a, gamma=2.8, eta=2.0)
        assert float(aff) == pytest.approx(1.0, abs=1e-5)

    def test_max_distance(self):
        """Distance L=4 should give low affinity."""
        a = jnp.array([1, 2, 3, 4])
        b = jnp.array([5, 6, 7, 8])
        aff = compute_affinity(a, b, gamma=2.8, eta=2.0)
        # exp(-(4/2.8)^2) ≈ exp(-2.04) ≈ 0.13
        assert float(aff) < 0.2
        assert float(aff) > 0.0

    def test_monotonic_decrease(self):
        """Affinity should decrease with distance."""
        antigen = jnp.array([0, 0, 0, 0])
        d0 = jnp.array([0, 0, 0, 0])
        d1 = jnp.array([1, 0, 0, 0])
        d2 = jnp.array([1, 1, 0, 0])
        d3 = jnp.array([1, 1, 1, 0])

        a0 = float(compute_affinity(d0, antigen))
        a1 = float(compute_affinity(d1, antigen))
        a2 = float(compute_affinity(d2, antigen))
        a3 = float(compute_affinity(d3, antigen))

        assert a0 > a1 > a2 > a3

    def test_range(self):
        """Affinity should be in [0, 1]."""
        a = jnp.array([3, 7, 1, 9])
        b = jnp.array([0, 0, 0, 0])
        aff = float(compute_affinity(a, b))
        assert 0.0 <= aff <= 1.0


class TestMutation:
    def test_one_position_changes(self):
        """Mutation should change exactly one position."""
        seq = jnp.array([5, 5, 5, 5])
        key = jax.random.PRNGKey(0)
        mutated = mutate_sequence(seq, key, n_values=10, L=4)
        n_diffs = int(jnp.sum(seq != mutated))
        assert n_diffs == 1

    def test_change_by_one(self):
        """The changed position should differ by ±1 (mod n_values)."""
        seq = jnp.array([5, 5, 5, 5])
        key = jax.random.PRNGKey(0)
        mutated = mutate_sequence(seq, key, n_values=10, L=4)
        diffs = mutated - seq
        # Find the changed position
        changed = jnp.where(diffs != 0)[0]
        assert len(changed) == 1
        diff_val = int(diffs[changed[0]])
        assert diff_val in [-1, 1, 9, -9]  # ±1 mod 10

    def test_deterministic(self):
        """Same key should produce same mutation."""
        seq = jnp.array([5, 5, 5, 5])
        key = jax.random.PRNGKey(42)
        m1 = mutate_sequence(seq, key, n_values=10, L=4)
        m2 = mutate_sequence(seq, key, n_values=10, L=4)
        assert jnp.array_equal(m1, m2)


class TestBatchOperations:
    def test_batch_hamming(self):
        """Batch Hamming should match single computations."""
        antigen = jnp.array([0, 0, 0, 0])
        bcrs = jnp.array([
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [1, 1, 1, 1],
        ])
        dists = batch_hamming(bcrs, antigen)
        expected = jnp.array([0, 1, 2, 4])
        assert jnp.array_equal(dists, expected)

    def test_batch_affinity(self):
        """Batch affinity should match single computations."""
        antigen = jnp.array([0, 0, 0, 0])
        bcrs = jnp.array([
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 1, 1, 1],
        ])
        batch_aff = batch_affinity(bcrs, antigen)
        single_affs = jnp.array([
            compute_affinity(bcrs[0], antigen),
            compute_affinity(bcrs[1], antigen),
            compute_affinity(bcrs[2], antigen),
        ])
        assert jnp.allclose(batch_aff, single_affs, atol=1e-5)


class TestFounderCreation:
    def test_correct_distance_range(self):
        """Founders should be at Hamming distance [min, max] from antigen."""
        antigen = jnp.array([0, 0, 0, 0])
        key = jax.random.PRNGKey(0)
        founders = create_founders_at_distance(
            50, antigen, hamming_min=2, hamming_max=3, rng_key=key
        )
        dists = batch_hamming(founders, antigen)
        assert jnp.all(dists >= 2)
        assert jnp.all(dists <= 3)

    def test_shape(self):
        """Output should have correct shape."""
        antigen = jnp.array([0, 0, 0, 0])
        key = jax.random.PRNGKey(0)
        founders = create_founders_at_distance(
            20, antigen, hamming_min=4, hamming_max=4, rng_key=key
        )
        assert founders.shape == (20, 4)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
