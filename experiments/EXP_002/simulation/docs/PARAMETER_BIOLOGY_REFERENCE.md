# Parameter–Biology Reference

Comprehensive mapping of simulation parameters to experimental biology. Use this document as the source of truth when designing experiments.

---

## 1. Mutation Rate

### The T7 Replisome Toolkit

The bacterial GC uses **T7 replisome variants** to control mutation rate. The gene target is a **nanobody gene (~360 bp / ~120 aa)**.

| Variant | Mechanism | Rate (sub/bp/div) | Sim param (L=40) | mut/gene/div | Source |
|---|---|---|---|---|---|
| **WT E. coli** | Native replication | ~10⁻⁹ | 1e-9 | 4×10⁻⁸ | Drake 1998 |
| **T7 V1** (WT + exo⁺) | Wild-type T7 DNAP | ~10⁻⁸ | 1e-8 | 4×10⁻⁷ | Kunkel 2004 |
| **T7 V2** | Reduced exonuclease | ~10⁻⁷ | 1e-7 | 4×10⁻⁶ | Proposal estimate |
| **T7 V3** (exo⁻) | Exonuclease-deficient | ~10⁻⁶ | 1e-6 | 4×10⁻⁵ | Tabor & Richardson |
| **T7 V4** (error-prone) | Error-prone mutant | ~10⁻⁵ | 1e-5 | 4×10⁻⁴ | Proposal |
| **T7 V5** (highest) | Maximum error rate | ~10⁻⁴ | 1e-4 | 4×10⁻³ | Proposal |

> [!IMPORTANT]
> **Simulation scaling**: Our L=40 shape space maps to the nanobody gene. Rate of `1e-5` in the simulation (per position per division) corresponds to T7 V4 in biology. The sharp **maturation boundary** sits between V3 and V4.

### Natural GC comparison
- **SHM rate**: ~10⁻³/bp/division in V regions (~300 bp), i.e. ~0.3 mutations per division per gene
- This is **~100× higher** than T7 V4 but applied to a much smaller target (300 bp vs ~4000 bp genome equivalent in the simulation's abstract space)

### What to test
- **V3 (10⁻⁶)**: Safe maturation at all selection strengths
- **V4 (10⁻⁵)**: Boundary rate — maturation depends on selection stringency
- **V5 (10⁻⁴)**: Maximum T7 rate — only matures with very strong selection

---

## 2. DZ Divisions (Growth Before Selection)

### Parameter: `dz_divisions`
Number of cell doublings in the dark zone before cells migrate to the light zone for selection.

### Biology

**Natural GC** (Robert et al. 2017, Mesin 2016):
- Founder cells: 6-12 divisions (initial expansion, no selection yet)
- Recycled cells: **1-6 divisions** per DZ visit
  - Average: **~2 divisions** (Gitlin et al. 2014, 2015)
  - Range depends on T cell signal strength (stronger signal → more divisions)
  - Hill function: `n_div = P_min + (P_max - P_min) × pMHC^n / (pMHC^n + K^n)` with P_min=1, P_max=6

**Bacterial GC** (your experimental system):
- Determined by **growth time between transfers**
- At 30 min doubling: 3h growth → 6 doublings, 1.5h → 3 doublings
- Controlled by the robot's transfer timing

### What to test
- **dz_divisions=2**: Natural GC average (most frequent selection)
- **dz_divisions=4**: Intermediate
- **dz_divisions=6**: Natural GC max / convenient for experiments (6h growth)

### Impact on mutation load
At V4 (10⁻⁵/pos/div) with L=40:
- **dz_div=2**: 2 × 40 × 10⁻⁵ = 0.0008 mutations per cell per LZ visit
- **dz_div=6**: 6 × 40 × 10⁻⁵ = 0.0024 mutations per cell per LZ visit
- More divisions = more mutations accumulated before each selection round

---

## 3. Selection Mechanism

### Independent (Hill function — our original model)
- Each cell survives with probability: `P = a^n / (a^n + K^n)`
- **Survival is independent** — your fate doesn't depend on your neighbors
- Biologically: models bead binding with excess beads (each cell either binds or doesn't)

| K | Survival (a=0.6) | Interpretation |
|---|---|---|
| 0.1 | 99.2% | Almost no selection |
| 0.3 | 82.2% | Mild selection |
| 0.5 | 50.0% | Strong selection |
| 1.0 | 17.8% | Very strong |
| 1.25 | 9.9% | Natural GC equivalent |

### Competitive (Top-fraction — new model)
- Keep the top X% of LZ cells by affinity, kill the rest
- **Survival is competitive** — depends on being better than others
- Biologically: models limited beads or limited T cell help

| Fraction | Interpretation |
|---|---|
| 10% | Natural GC strength (~Mesin 2016 estimate) |
| 30% | Natural GC permissive end |
| 50% | Moderate competition |
| 82% | Matched to Hill K=0.3 survival rate |

### Key difference (from controls)
At N=10K, V4, 140 cycles:
- Hill K=0.3 (independent, 82% survive): Δ = **+0.20**
- Top-fraction 82% (competitive, 82% survive): Δ = **+0.13**
- Top-fraction 10% (competitive, 10% survive): Δ = **+0.21**

**Same survival rate, different outcomes!** Independent selection stochastically kills cells across the whole affinity range, which paradoxically provides stronger selection per round. Competitive selection only removes the worst.

### Natural GC
- **Two-step process** (Robert et al.): antigen collection (affinity-dependent) → T cell competition (rank-based among neighbors)
- From Mesin 2016: **10-30% of LZ cells** return to DZ per cycle
- Selection is inherently **competitive** due to limited T cell help

### What to test
- **Top-fraction 10%**: Natural GC stringency
- **Top-fraction 30%**: Natural GC permissive
- Compare with Hill at matched survival rates

---

## 4. Population Size

### Parameter: `turbidostat_target_n`

### Biology

**Natural GC**:
- ~1,000-10,000 B cells per GC (Allen 2007, Victora 2010)
- ~50-200 founder clones (Tas et al. 2016)
- Multiple GCs per lymph node (~10-100)

**Bacterial GC** (your system):
- Standard turbidostat: **10⁶-10⁸ cells** (1 mL at OD ~0.1-1.0)
- Microfluidic: **10³-10⁵ cells**
- The proposal's advantage claim: "10⁶-fold more mutational exploration"

### Our simulation results (Q4)
| N | Typical diversity | Affinity |
|---|---|---|
| 10K | 1.6-2.2 | +0.20 |
| 1M | 3.2-3.7 | +0.20 |
| 10M | 3.4-3.9 | +0.20 |

**Finding**: Larger N doubles diversity but doesn't improve affinity. The advantage is **breadth, not depth**.

### What to test
- **N=10K**: Fast runs, natural GC scale
- **N=10M**: Bacterial scale, tests diversity advantage

---

## 5. Unselected Return

### Parameter: `unselected_return_fraction`

### Biology
In the natural GC, a small fraction of cells that fail selection may still survive (not all apoptose immediately). This provides additional diversity maintenance.

- Default: **0.1** (10% of dead LZ cells are recycled back)
- Setting to 0: all unselected cells die (harshest selection)

---

## 6. Number of Cycles

### Parameter: `n_cycles`

### Biology

**Natural GC**: 
- Duration: 3-21+ days
- Cycle time: ~8-12h per LZ-DZ cycle
- Total cycles: ~6-50 complete cycles over the GC lifetime

**Bacterial GC**: 
- Each cycle = growth phase + transfer + selection + regrowth
- At 6h growth: ~4 cycles/day
- 7-day experiment: ~28 cycles
- 35-day experiment: ~140 cycles

### What to test
- **140 cycles**: Standard long experiment (35 days at 4 cycles/day)

---

## Quick Reference: Biologically Grounded Parameter Sets

### "Natural GC" set
```
dz_divisions=2, selection=top_fraction(10%), N=10K, V3-V4
```

### "Bacterial GC — conservative" set
```
dz_divisions=6, selection=top_fraction(30%), N=1M, V4
```

### "Bacterial GC — aggressive" set
```
dz_divisions=6, selection=top_fraction(10%), N=10M, V5
```
