# Corrected Sweep — Real T7 Polymerase Variant Rates

**Date**: 2026-03-17 18:37
**N**: 10,000 | **L**: 40 | **Cycles**: 140

## Rate Table

| Variant | Real rate (/bp/div) | L=40 rate | mut/gene/div |
|---|---|---|---|
| WT E. coli | 1e-09 | 1e-08 | 4.00e-07 |
| T7 V1 (WT+exo) | 1e-08 | 1e-07 | 4.00e-06 |
| T7 V2 | 1e-07 | 1e-06 | 4.00e-05 |
| T7 V3 (exo⁻) | 1e-06 | 1e-05 | 4.00e-04 |
| T7 V4 (error-prone) | 1e-05 | 1e-04 | 4.00e-03 |
| T7 V5 (highest) | 1e-04 | 1e-03 | 4.00e-02 |

## Heatmap

![T7 rates heatmap](T7_rates_heatmap.png)

## Results Table

| Variant | K | Status | Δ aff | Final aff | Diversity | Pop | Time |
|---|---|---|---|---|---|---|---|
| WT E. coli | 0.05 | **MATURATION** | +0.0430 | 0.618 | 3.45 | 9,993 | 102s |
| WT E. coli | 0.1 | **MATURATION** | +0.1125 | 0.688 | 3.66 | 9,962 | 170s |
| WT E. coli | 0.2 | **MATURATION** | +0.1791 | 0.758 | 3.27 | 9,830 | 416s |
| WT E. coli | 0.3 | **MATURATION** | +0.1961 | 0.783 | 3.05 | 9,509 | 489s |
| T7 V1 (WT+exo) | 0.05 | **MATURATION** | +0.0430 | 0.618 | 3.45 | 9,993 | 116s |
| T7 V1 (WT+exo) | 0.1 | **MATURATION** | +0.1125 | 0.688 | 3.66 | 9,962 | 179s |
| T7 V1 (WT+exo) | 0.2 | **MATURATION** | +0.1479 | 0.727 | 3.26 | 9,804 | 411s |
| T7 V1 (WT+exo) | 0.3 | **MATURATION** | +0.1870 | 0.773 | 3.03 | 9,491 | 522s |
| T7 V2 | 0.05 | **MATURATION** | +0.0218 | 0.597 | 3.76 | 9,990 | 128s |
| T7 V2 | 0.1 | **MATURATION** | +0.0964 | 0.672 | 3.66 | 9,962 | 194s |
| T7 V2 | 0.2 | **MATURATION** | +0.1656 | 0.745 | 3.04 | 9,805 | 515s |
| T7 V2 | 0.3 | **MATURATION** | +0.2067 | 0.793 | 2.78 | 9,526 | 586s |
| T7 V3 (exo⁻) | 0.05 | **STABLE** | -0.0007 | 0.574 | 3.60 | 9,991 | 147s |
| T7 V3 (exo⁻) | 0.1 | **MATURATION** | +0.0319 | 0.607 | 3.66 | 9,951 | 198s |
| T7 V3 (exo⁻) | 0.2 | **MATURATION** | +0.1604 | 0.739 | 2.51 | 9,810 | 552s |
| T7 V3 (exo⁻) | 0.3 | **MATURATION** | +0.1894 | 0.776 | 3.12 | 9,493 | 579s |
| T7 V4 (error-prone) | 0.05 | **DEGRADATION** | -0.1013 | 0.472 | 3.43 | 9,973 | 183s |
| T7 V4 (error-prone) | 0.1 | **DEGRADATION** | -0.0658 | 0.508 | 3.23 | 9,901 | 258s |
| T7 V4 (error-prone) | 0.2 | **MATURATION** | +0.0676 | 0.645 | 3.25 | 9,694 | 523s |
| T7 V4 (error-prone) | 0.3 | **MATURATION** | +0.1282 | 0.713 | 2.17 | 9,339 | 556s |
| T7 V5 (highest) | 0.05 | **DEGRADATION** | -0.3965 | 0.164 | 2.29 | 9,306 | 707s |
| T7 V5 (highest) | 0.1 | **DEGRADATION** | -0.3074 | 0.254 | 1.80 | 9,037 | 756s |
| T7 V5 (highest) | 0.2 | **DEGRADATION** | -0.2021 | 0.364 | 0.94 | 8,284 | 726s |
| T7 V5 (highest) | 0.3 | **STABLE** | -0.0194 | 0.555 | 0.17 | 8,395 | 706s |

## Summary

- **MATURATION**: 17 runs
- **STABLE**: 2 runs
- **DEGRADATION**: 5 runs

## Individual Plots

### WT E. coli, K=0.05 → **MATURATION**
![mut1e-08_k0.05](mut1e-08_k0.05.png)

### WT E. coli, K=0.1 → **MATURATION**
![mut1e-08_k0.1](mut1e-08_k0.1.png)

### WT E. coli, K=0.2 → **MATURATION**
![mut1e-08_k0.2](mut1e-08_k0.2.png)

### WT E. coli, K=0.3 → **MATURATION**
![mut1e-08_k0.3](mut1e-08_k0.3.png)

### T7 V1 (WT+exo), K=0.05 → **MATURATION**
![mut1e-07_k0.05](mut1e-07_k0.05.png)

### T7 V1 (WT+exo), K=0.1 → **MATURATION**
![mut1e-07_k0.1](mut1e-07_k0.1.png)

### T7 V1 (WT+exo), K=0.2 → **MATURATION**
![mut1e-07_k0.2](mut1e-07_k0.2.png)

### T7 V1 (WT+exo), K=0.3 → **MATURATION**
![mut1e-07_k0.3](mut1e-07_k0.3.png)

### T7 V2, K=0.05 → **MATURATION**
![mut1e-06_k0.05](mut1e-06_k0.05.png)

### T7 V2, K=0.1 → **MATURATION**
![mut1e-06_k0.1](mut1e-06_k0.1.png)

### T7 V2, K=0.2 → **MATURATION**
![mut1e-06_k0.2](mut1e-06_k0.2.png)

### T7 V2, K=0.3 → **MATURATION**
![mut1e-06_k0.3](mut1e-06_k0.3.png)

### T7 V3 (exo⁻), K=0.05 → **STABLE**
![mut1e-05_k0.05](mut1e-05_k0.05.png)

### T7 V3 (exo⁻), K=0.1 → **MATURATION**
![mut1e-05_k0.1](mut1e-05_k0.1.png)

### T7 V3 (exo⁻), K=0.2 → **MATURATION**
![mut1e-05_k0.2](mut1e-05_k0.2.png)

### T7 V3 (exo⁻), K=0.3 → **MATURATION**
![mut1e-05_k0.3](mut1e-05_k0.3.png)

### T7 V4 (error-prone), K=0.05 → **DEGRADATION**
![mut0.0001_k0.05](mut0.0001_k0.05.png)

### T7 V4 (error-prone), K=0.1 → **DEGRADATION**
![mut0.0001_k0.1](mut0.0001_k0.1.png)

### T7 V4 (error-prone), K=0.2 → **MATURATION**
![mut0.0001_k0.2](mut0.0001_k0.2.png)

### T7 V4 (error-prone), K=0.3 → **MATURATION**
![mut0.0001_k0.3](mut0.0001_k0.3.png)

### T7 V5 (highest), K=0.05 → **DEGRADATION**
![mut0.001_k0.05](mut0.001_k0.05.png)

### T7 V5 (highest), K=0.1 → **DEGRADATION**
![mut0.001_k0.1](mut0.001_k0.1.png)

### T7 V5 (highest), K=0.2 → **DEGRADATION**
![mut0.001_k0.2](mut0.001_k0.2.png)

### T7 V5 (highest), K=0.3 → **STABLE**
![mut0.001_k0.3](mut0.001_k0.3.png)
