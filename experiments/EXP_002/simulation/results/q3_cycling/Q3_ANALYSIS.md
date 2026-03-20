# Q3: DZ/LZ Cycling Speed — Analysis

> **Date**: 2026-03-19
> **Runtime**: 6.5 hours (GPU, 48 runs)
> **Question**: Does faster DZ/LZ cycling counter Muller's ratchet at high mutation rates?

---

## Summary

**48 runs**: 4 cycling speeds × 2 rates × 2 N values × 3 seeds, all at K=0.3.

`dz_divisions` controls how many doublings occur before cells migrate DZ→LZ for selection:
- **dz_div=2**: 6 selections per cycle (most frequent)
- **dz_div=4**: 3 selections per cycle
- **dz_div=6**: 2 selections per cycle (default)
- **dz_div=12**: 1 selection per cycle (least frequent)

### Δ Affinity by Cycling Speed × N × Rate (mean of 3 seeds)

| dz_div | Selections/cycle | N=10K V4 | N=10K V5 | N=10M V4 | N=10M V5 |
|---|---|---|---|---|---|
| **2** | 6 | ✅ +0.19 | ✅ +0.15 | ✅ **+0.22** | ✅ +0.18 |
| **4** | 3 | ✅ +0.19 | ✅ **+0.17** | ✅ +0.20 | ✅ +0.18 |
| **6** | 2 (default) | ✅ +0.19 | ✅ +0.16 | ✅ +0.20 | ✅ **+0.19** |
| **12** | 1 | ✅ +0.18 | ✅ +0.15 | ✅ +0.21 | ✅ +0.18 |

### Diversity by Cycling Speed × N × Rate

| dz_div | N=10K V4 | N=10K V5 | N=10M V4 | N=10M V5 |
|---|---|---|---|---|
| **2** | 2.01 | 1.73 | **3.43** | **3.42** |
| **4** | 1.62 | 1.68 | **3.43** | **3.44** |
| **6** | 1.88 | 1.65 | **3.45** | **3.42** |
| **12** | 1.83 | 1.67 | **3.44** | **3.44** |

---

## Key Findings

### 1. Cycling speed has minimal effect on maturation

**This is the main result.** Across all conditions, Δaffinity varies by only ±0.02 regardless of cycling speed:
- N=10K V4: +0.18 to +0.19 (essentially flat)
- N=10M V5: +0.18 to +0.19 (essentially flat)
- No clear trend with faster or slower cycling

### 2. Cycling speed does not affect diversity

Diversity is essentially identical across all cycling speeds:
- N=10M: 3.42-3.45 regardless of dz_divisions
- N=10K: 1.62-2.01 (some variation, no clear trend)

### 3. The system is robust to cycling frequency

Whether selection happens once per cycle or 6 times per cycle, the outcome is the same. This means:
- The GC architecture works across a wide range of migration frequencies
- There is no need to precisely tune DZ/LZ cycling in the experimental system
- Muller's ratchet is **not rescued by faster cycling** — it is determined entirely by selection strength (K) and mutation rate

---

## Implications

1. **Experimental flexibility**: The cycling frequency is not a critical parameter. The microfluidic/robotic transfer timing between DZ and LZ compartments does not need to be precisely optimised.

2. **The prediction from open_questions.md was wrong**: We hypothesised that frequent cycling (`dz_divisions=2`) could counter Muller's ratchet. In fact, the ratchet is controlled by K, not cycling speed.

3. **Simplification opportunity**: Since cycling speed doesn't matter, the experimental protocol can use whatever transfer frequency is most convenient (e.g., daily transfers at `dz_divisions=6`).
