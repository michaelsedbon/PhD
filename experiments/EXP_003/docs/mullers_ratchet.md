# Muller's Ratchet in the Bacterial Germinal Center

## Summary

At T7 mutation rate (`0.0005/pos/div`), the bacterial GC simulation shows **affinity degradation** instead of affinity maturation across all tested population sizes (N=10K, N=1M). This is consistent with **Muller's ratchet** — the irreversible accumulation of deleterious mutations in asexual populations.

---

## Experimental Evidence

### Three runs, same parameters except N and `unselected_return`

| Parameter | Run A | Run B | Run C |
|---|---|---|---|
| Population (N) | 10,000 | 10,000 | **1,000,000** |
| Cycles | 140 | 10 | 140 |
| `unselected_return` | 0.0 | 0.1 | 0.1 |
| L | 400 | 400 | 400 |
| Mutation rate | 0.0005/pos/div | 0.0005/pos/div | 0.0005/pos/div |
| Γ (affinity width) | 105 | 105 | 105 |
| Hill K | 0.3 | 0.3 | 0.3 |

### Results

| Metric | Run A (N=10K) | Run B (N=10K) | Run C (N=1M) |
|---|---|---|---|
| Final population | 5,000 | 8,700 | **524,000** |
| Mean affinity | 0.58 → **0.30** | 0.58 → 0.58 | 0.58 → **0.29** |
| Max affinity | 0.80 → 0.30 | 0.80 → 0.77 | 0.80 → **0.42** |
| Diversity (Shannon) | 3.9 → **0** | 5.6 → 5.1 | 5.6 → **0.96** |
| Top clone | 100% (takeover) | 8% | **80%** |

### Plots

```carousel
Run A — N=10K, no unselected return.
Diversity collapsed to 0 by cycle 100 (single clone takeover).
Affinity degraded to 0.30.

![Run A](/experiments/EXP_002/simulation/results/bacterial_L400_7day.png)
```

---

## What Is Muller's Ratchet?

In asexual populations (no recombination), the class of individuals with the **fewest deleterious mutations** can only be lost — never regained. Once a deleterious mutation fixes in the population, it cannot be reversed by combining genomes from two parents.

Each "click" of the ratchet:
1. The best genotype in the population acquires a deleterious mutation in all its descendants
2. No descendants can recombine to regenerate the original best genotype
3. The population's fitness ceiling permanently decreases

This is exactly what we observe: mean affinity monotonically decreases across cycles.

---

## Why It Happens Here

### The mutation budget

At T7 peak mutation rate with L=400:

```
Mutations per cell per division = 0.0005 × 400 = 0.2
Divisions per cycle             = 12 (6h growth / 0.5h doubling time)
Mutations per cell per cycle    = 0.2 × 12 ≈ 2.4
```

For a population of N=1M:
```
Total mutations per cycle       = 2.4 × 1,000,000 = 2,400,000
Beneficial mutations (est.)     = ~1 in 1000 = ~2,400
Deleterious mutations           = ~2,397,600
```

### The selection budget

Hill selection with K=0.3 and mean affinity ~0.58:

```
Survival probability = a³ / (a³ + K³) = 0.58³ / (0.58³ + 0.3³) = 0.88
Cells removed by selection = 12% per cycle
```

**12% removal is insufficient to purge 2.4M deleterious mutations per cycle.** Even with stronger selection, the mutational input vastly exceeds the selective removal.

### Why larger N helps but doesn't solve it

At N=1M vs N=10K:
- **More beneficial mutations appear** (2,400 vs 24 per cycle)
- **But proportionally more deleterious mutations also appear**
- **Selection pressure is the same** (12% removal regardless of N)
- **Result**: diversity declines slower (0.96 vs 0 at cycle 140), but affinity still degrades

The critical difference: at N=10K, beneficial mutations are too rare to be reliably selected, so one neutral/lucky clone takes over by drift. At N=1M, there are enough beneficial mutations to prevent complete fixation, but not enough to outpace the deleterious load.

---

## Comparison with Natural GCs

Natural germinal centers solve Muller's ratchet through:

1. **Low mutation rate per division**: SHM acts on ~1-2 mutations per division across ~300bp V region, but B cells undergo only ~6 divisions per cycle. The per-position rate is ~10⁻³/bp/division — comparable to T7, but the protein coding region is shorter (~100 AA × 3 = 300 bp), so fewer total mutations per gene per cycle
2. **Very strong selection**: Only ~10% of GC B cells survive selection (vs our 88%). The FDC-Tfh competitive selection is far more stringent
3. **Clonal competition**: B cells compete for limiting T cell help — the best clones actively outcompete, not just survive
4. **Small effective population**: Natural GCs have N~1000-10,000. Muller's ratchet is slow at small N when selection is strong enough

### Key difference from our simulation

| Factor | Natural GC | Our bacterial GC |
|---|---|---|
| Selection survival | ~10% | ~88% |
| Mutations/gene/div | ~0.5 | ~0.2 |
| Selection stringency | Competitive (top-K) | Probabilistic (Hill) |
| Population | ~1,000 | 1,000,000 |
| Recombination | No (SHM only) | No |

The critical imbalance: **our selection is too weak relative to our mutation rate.**

---

## Hypotheses and Predictions

### H1: Selection is too weak
**Prediction**: Lowering `hill_k` from 0.3 to 0.1 would increase selection pressure (survival drops from 88% to ~66%) and could stabilize or improve affinity.

### H2: Mutation rate is too high
**Prediction**: Reducing `mutation_rate` from 0.0005 to 0.0001 (5× lower, still within T7 range) would reduce mutational load from 2.4 to 0.48 mutations/cell/cycle. This may be below the threshold for Muller's ratchet.

### H3: Selection frequency matters
**Prediction**: Selecting every 2 doublings instead of every 12 would apply more frequent purifying pressure. Each selection round removes low-affinity cells before they can further propagate.

### H4: The bacterial GC doesn't need affinity maturation
**Prediction**: If the bacterial GC's purpose is **diversity maintenance + initial quality screening** rather than affinity improvement, then the current parameters are correct. The system screens a diverse library rather than hill-climbing a fitness landscape.

---

## Proposed Next Experiments

| Experiment | Change | Expected Outcome |
|---|---|---|
| Stronger selection | `hill_k=0.1` | Affinity stabilizes, diversity drops faster |
| Lower mutation rate | `mutation_rate=0.0001` | Affinity stabilizes or improves slowly |
| Frequent selection | `dz_divisions=2` | Better purging, possible maturation |
| Combined | k=0.1, rate=0.0001 | Best chance of maturation |
| Bead selection | Top-K instead of Hill | Mimics competitive FDC selection |

---

## Implications for the Proposal

1. **T7 mutation rate may need tuning**: The peak rate of ~10⁻⁴/bp/gen creates mutation load that overwhelms Hill selection
2. **Selection stringency is the key lever**: In the real experiment, bead-based selection might be more stringent than Hill K=0.3 implies
3. **The "selection gap"**: The gap between mutation rate and selection strength determines whether the system matures or degrades. This is a measurable quantity in the real experiment
4. **Population size helps diversity but not maturation**: N=1M maintains clonal diversity (Shannon > 0) but cannot prevent affinity decline. The bacterial GC may need a different mechanism than the natural GC
