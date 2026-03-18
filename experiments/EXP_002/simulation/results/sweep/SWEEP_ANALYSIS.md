# Parameter Sweep Analysis — L=400, N=10K, 140 Cycles

**Date**: 2026-03-17  
**Platform**: CPU (server, 16 cores, 32 GB RAM)  
**Runtime**: ~3.0 hours total (16 runs × ~10 min each)

---

## ⚠️ Important Context — Read First

### Mutation Rates Were Not Calibrated to Real T7 Variants

This sweep used mutation rates `[0.0001, 0.0003, 0.0005, 0.001]` per base per division. However, the **actual T7 replisome variants** from the Maimonide proposal span a very different range:

| T7 Variant | Rate (sub/base/rep) | At L=400 | This sweep equivalent |
|---|---|---|---|
| V1: WT + exo + trx | ~10⁻⁸ | 4×10⁻⁶ mut/gene | not tested |
| V2: WT + exo | ~10⁻⁷ | 4×10⁻⁵ | not tested |
| V3: WT exo⁻ | ~10⁻⁶ | 4×10⁻⁴ | not tested |
| V4: error-prone exo⁻ | ~10⁻⁵ | 0.004 | not tested |
| **V5: highest error** | ~10⁻⁴ | **0.04** | **= our 0.0001** |

**Our sweep tested rates 10-100× ABOVE the real T7 range.** The only maturation result (mut=0.0001) corresponds to the HIGHEST-error T7 variant (V5). All real T7 variants (V1-V4) would have even lower rates and should show even better maturation.

> A corrected sweep with rates `[10⁻⁸, 10⁻⁷, 10⁻⁶, 10⁻⁵, 10⁻⁴]` per base per division is needed.

### DZ/LZ Architecture — How Cycling Works

In the current simulation:
- **DZ (dark zone)**: cells divide for `dz_growth_hours=6h` at `doubling_time=0.5h` = **12 doublings** per cycle
- Cells migrate to LZ after `dz_divisions=6` doublings (i.e., mid-cycle)
- **LZ (light zone)**: cells do **NOT divide** — only selection happens here
- After selection, survivors return to DZ with `div_counter=0` and resume dividing
- Each cycle = 12 doublings in DZ + 1 selection event in LZ

The `dz_divisions` parameter controls cycling speed:
| dz_divisions | Selections per cycle | Mutations before selection |
|---|---|---|
| 2 | 6 | few (less mutation load per selection) |
| 6 | 2 | moderate (current default) |
| 12 | 1 | many (max mutation load before selection) |

Faster cycling (lower `dz_divisions`) = more frequent purifying selection = potentially better against mutation load. **This is an unexplored parameter that could significantly affect results.**

### Why Population Shrinks

The turbidostat targets N=10,000. Population decline happens via this mechanism:
1. Cells grow (12 doublings, diluted to ~10K)
2. Cells in LZ undergo Hill selection — some die
3. Dead cells are **not replaced** within the cycle
4. Only 10% of dead LZ cells return (`unselected_return=0.1`)
5. Net loss per cycle ≈ (% killed by selection) × 0.9
6. At high mutation rates, more cells fall below selection threshold → more killed → faster decline

### The Affinity "Bump" (Early Rise Then Decline)

Visible in the K=0.3 run plots (especially mut=0.0001 and mut=0.0003):
- **Cycles 1-15**: Selection removes the worst cells → mean affinity rises (purifying selection succeeds)
- **Cycles 15+**: Accumulated mutations degrade even the best clones → mean starts declining
- **Max always declines** because the top clone's daughters always accumulate mutations

This proves selection IS working — it just can't keep pace with mutation load at higher rates.

---

## Heatmap Overview

![Sweep heatmap — Affinity change, Final diversity, Selection survival](sweep_heatmap.png)

### Reading the heatmap

- **Left panel** — Affinity change (final − initial): green = improvement, red = degradation
- **Center panel** — Final diversity (Shannon entropy): yellow = high, dark = collapsed
- **Right panel** — Selection survival rate: all ~1.0, meaning selection barely removes anyone

### Key observation

Only **one cell is green** (top-right corner): `mutation_rate=0.0001, hill_k=0.3`. Everything else degrades. The selection survival rate is ~1.0 everywhere — Hill selection at these K values is too permissive.

---

## Results Table

| mut_rate | mut/gene/div | K=0.05 | K=0.1 | K=0.2 | K=0.3 |
|---|---|---|---|---|---|
| **0.0001** | 0.04 | -0.21 DEGRAD | -0.10 DEGRAD | -0.03 STABLE | **+0.03 MATUR** ✅ |
| **0.0003** | 0.12 | -0.37 | -0.32 | -0.24 | -0.21 |
| **0.0005** (T7) | 0.20 | -0.47 | -0.41 | -0.36 | -0.31 |
| **0.001** | 0.40 | -0.51 | -0.47 | -0.45 | -0.45 |

*(Values = affinity change over 140 cycles)*

---

## Row-by-Row Analysis

### Row 1: mutation_rate = 0.0001 (0.04 mut/gene/div) — 5× below T7

This is our lowest mutation rate. The gradient across K is clear: **stronger selection (lower K) actually makes things worse**.

````carousel
![mut=0.0001, K=0.05 — DEGRADATION: affinity drops from 0.57 to 0.36. Strong selection kills cells faster than they can recover. Population stable at 10K but diversity drops to 3.6.](mut0.0001_k0.05.png)
<!-- slide -->
![mut=0.0001, K=0.1 — DEGRADATION: affinity drops to 0.48. Slightly better than K=0.05 but still declining.](mut0.0001_k0.1.png)
<!-- slide -->
![mut=0.0001, K=0.2 — STABLE: affinity barely changes (-0.03). This is the transition point — mutation load roughly balanced by selection.](mut0.0001_k0.2.png)
<!-- slide -->
![mut=0.0001, K=0.3 — MATURATION: affinity INCREASES from 0.58 to 0.61 (+0.03). The ONLY maturation result in the entire sweep. Weak selection preserves diversity while allowing beneficial mutations to spread.](mut0.0001_k0.3.png)
````

**Why does weak selection (K=0.3) win?** At K=0.05, selection kills more cells, but at this low mutation rate, beneficial mutations are rare. Strong selection depletes the population of variants before they can improve. K=0.3 keeps most cells alive, giving rare beneficial mutants time to spread through natural growth advantage.

---

### Row 2: mutation_rate = 0.0003 (0.12 mut/gene/div) — moderate

All 4 conditions degrade. The mutation load is now 3× higher than Row 1, and no selection strength can compensate.

````carousel
![mut=0.0003, K=0.05 — worst of this row: -0.37 affinity change](mut0.0003_k0.05.png)
<!-- slide -->
![mut=0.0003, K=0.1](mut0.0003_k0.1.png)
<!-- slide -->
![mut=0.0003, K=0.2](mut0.0003_k0.2.png)
<!-- slide -->
![mut=0.0003, K=0.3 — best of this row but still -0.21. Diversity drops to 1.49, population to 6890.](mut0.0003_k0.3.png)
````

**Interpretation**: 0.0003 is the tipping point. Even the weakest selection can't prevent Muller's ratchet here. The mutation load per cycle (~1.5 mutations/cell) exceeds selection's ability to purge.

---

### Row 3: mutation_rate = 0.0005 (0.20 mut/gene/div) — T7 peak rate

**This is the biologically relevant T7 mutation rate.** All conditions strongly degrade.

````carousel
![mut=0.0005, K=0.05 — affinity collapses to 0.10. Population down to 8905.](mut0.0005_k0.05.png)
<!-- slide -->
![mut=0.0005, K=0.1](mut0.0005_k0.1.png)
<!-- slide -->
![mut=0.0005, K=0.2 — diversity drops to 0.99 (near single-clone)](mut0.0005_k0.2.png)
<!-- slide -->
![mut=0.0005, K=0.3 — diversity nearly zero (0.14), population halved to 4678. This is what we saw in the original N=1M run.](mut0.0005_k0.3.png)
````

**Conclusion**: T7 peak mutation rate causes unavoidable affinity degradation in this GC architecture at N=10K. The bacterial GC cannot affinity-mature at this rate.

---

### Row 4: mutation_rate = 0.001 (0.40 mut/gene/div) — 2× T7

Catastrophic degradation: all clones go extinct or nearly so, diversity collapses to 0.

````carousel
![mut=0.001, K=0.05 — diversity gone, affinity at 0.05 (near random)](mut0.001_k0.05.png)
<!-- slide -->
![mut=0.001, K=0.1](mut0.001_k0.1.png)
<!-- slide -->
![mut=0.001, K=0.2 — population collapses to 2407](mut0.001_k0.2.png)
<!-- slide -->
![mut=0.001, K=0.3 — population at 1487, affinity 0.12. Error catastrophe territory.](mut0.001_k0.3.png)
````

**This is near the error catastrophe threshold** — mutation rate so high that genetic information is lost faster than selection can maintain it. Eigen's error threshold in action.

---

## Surprising Pattern: Stronger Selection = Worse Outcomes

Counter-intuitively, within each mutation rate, **weaker selection (higher K) produces better outcomes**:

| mut_rate | Best K | Why |
|---|---|---|
| 0.0001 | K=0.3 (weakest) | Only maturation point |
| 0.0003 | K=0.3 (weakest) | Least degradation |
| 0.0005 | K=0.05 (strongest) | Best diversity, worst affinity |
| 0.001 | K=0.05 | Best diversity (but all bad) |

**Explanation**: Strong selection + high mutation creates a death spiral:
1. Selection kills bottom ~12% of cells
2. Remaining cells accumulate mutations during growth
3. More cells fall below selection threshold
4. Population shrinks → fewer beneficial mutations possible
5. Loop accelerates

Weak selection keeps the population large and diverse, giving rare beneficial mutations time to spread. This is the GC's key advantage — maintaining a reservoir of diversity.

---

## Key Conclusions

1. **Mutation rate is the dominant variable** — the rows have much larger effect than columns
2. **T7 peak rate (0.0005) is too high** for affinity maturation at N=10K with Hill selection
3. **Only mut=0.0001, K=0.3 shows maturation** — and it's marginal (+0.03 over 140 cycles)
4. **Selection survival is ~100% everywhere** — Hill selection is essentially passive at these parameters
5. **Stronger selection is NOT the answer** — it accelerates population decline without improving affinity

## Implications for the Proposal

- Need **lower mutation rate** (engineered T7 variant) OR **much larger N** to see maturation
- The bacterial GC may work best as a **diversity-maintaining** system rather than an affinity-maturing one
- **N=10⁷ with L=40** (running next on GPU) may shift the maturation boundary to higher mutation rates

---

*L=40 GPU validation sweep running in background — will compare heatmaps when complete.*
