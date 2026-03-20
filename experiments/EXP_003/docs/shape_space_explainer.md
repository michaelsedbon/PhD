# Shape Space — Explained

## The Problem

We need a way to represent antibodies (BCRs / nanobodies) and antigens as data objects, and a way to compute how well they bind (affinity). Real protein folding is impossibly expensive to simulate for millions of cells, so we use an abstraction called **shape space**.

## The Idea (Perelson & Oster, 1979)

Think of every possible antibody shape as a **point in a multi-dimensional grid**.

A BCR is a coordinate: e.g. `[3, 5, 9, 4]`
The antigen (target) is also a coordinate: e.g. `[5, 5, 9, 2]`

Each dimension represents an abstract "feature" of the binding interface (could be charge, shape, hydrophobicity — it doesn't map to anything specific). The point is: **two molecules that are "close" in shape space bind well**.

## Distance = Hamming Distance

The **Hamming distance** between two sequences is the number of positions where they differ:

```
BCR    = [3, 5, 9, 4]
Antigen = [5, 5, 9, 2]
           ↑        ↑
Hamming distance = 2  (positions 0 and 3 differ)
```

## Affinity = Gaussian of Distance

The affinity (binding strength) is computed as:

```
affinity = exp( - (hamming_distance ^ η) / (Γ ^ η) )
```

Where:
- `η = 2` (sharpness parameter — makes the Gaussian fall off quadratically)
- `Γ` is the **width** of the affinity Gaussian (tunable parameter)

**Examples** (with Γ=2.8, η=2):

| Hamming distance | Affinity | Interpretation |
|---|---|---|
| 0 | 1.000 | Perfect match |
| 1 | 0.879 | Very good binding |
| 2 | 0.601 | Moderate binding |
| 3 | 0.319 | Weak binding |
| 4 | 0.131 | Very weak |

This means:
- **Distance 0** = perfect antibody (identical to antigen in shape space)
- **Distance 4** = very poor antibody (all positions wrong)

## Mutation = ±1 in One Dimension

When a cell divides in the dark zone, one random position changes by +1 or -1:

```
Before mutation: [3, 5, 9, 4]
                        ↑
After mutation:  [3, 5, 8, 4]   (position 2 decreased by 1)
```

This may **increase** affinity (if it brings the BCR closer to the antigen) or **decrease** it (if it moves it further away). This mirrors the random nature of somatic hypermutation.

## Why L=4?

The dimensionality `L` controls the **ratio of beneficial to detrimental mutations**:

| L | Neighbors | How many improve affinity? |
|---|---|---|
| 1 | 2 | ~50% (1/2) |
| 2 | 4 | ~25-50% (1-2/4) |
| **4** | **8** | **~12-25% (1-2/8)** |
| 10 | 20 | ~5-10% |

L=4 was found optimal by Meyer-Hermann et al. (2001) because it produces a realistic ratio of beneficial vs. detrimental mutations (~1:3 to 1:7), matching experimental observations of antibody affinity maturation rates.

## Visual Intuition (2D Example)

Imagine a 2D shape space (L=2). The antigen sits at position (3,5):

```
    1  2  3  4  5  6  7
  ┌──┬──┬──┬──┬──┬──┬──┐
7 │  │  │  │  │  │  │  │
  ├──┼──┼──┼──┼──┼──┼──┤
6 │  │  │  │  │  │  │  │
  ├──┼──┼──┼──┼──┼──┼──┤
5 │  │  │ 🎯│  │  │  │  │  ← Antigen at (3,5)
  ├──┼──┼──┼──┼──┼──┼──┤
4 │  │  │  │  │  │  │  │
  ├──┼──┼──┼──┼──┼──┼──┤
3 │  │  │  │  │ 🔵│  │  │  ← BCR at (5,3) → Hamming dist = 2
  ├──┼──┼──┼──┼──┼──┼──┤
2 │  │  │  │  │  │  │  │
  ├──┼──┼──┼──┼──┼──┼──┤
1 │  │  │  │  │  │  │  │
  └──┴──┴──┴──┴──┴──┴──┘
```

The closer a BCR is to the antigen (🎯), the higher its affinity. Mutations move the BCR one step in one dimension. Affinity maturation is the process of random walks + selection gradually pushing the population towards the target.

## For Your Synthetic GC

In your bacterial system:
- Each *E. coli* carries a nanobody variant (= a BCR position in shape space)
- The antigen (RBD on beads/phage) = a fixed target point
- Error-prone replication = mutation (±1 in one dimension)
- Bead binding / phage infection = selection based on affinity

Later, we can extend shape space to:
- **Longer sequences** (L=50-200 binary) for more realistic mutation landscapes
- **NK landscapes** to introduce epistasis (mutations interact)
- **Real nucleotide sequences** with ML-predicted binding affinities
