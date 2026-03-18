# L=40 GPU Validation Sweep

**Date**: 2026-03-17 15:05
**N**: 10,000
**L**: 40
**Gamma**: 10.5
**Cycles**: 140
**Platform**: GPU (CUDA)

## Heatmap

![L=40 GPU Heatmap](/home/michael/gc_simulation/results/sweep_L40/sweep_L40_heatmap.png)

## Results Table

| L40 rate | ≡ L400 rate | mut/gene | hill_k | Status | Δ aff | Final aff | Final div | Pop | Time |
|---|---|---|---|---|---|---|---|---|---|
| 0.001 | 0.0001 | 0.04 | 0.05 | **DEGRADATION** | -0.3965 | 0.164 | 2.29 | 9,306 | 606s |
| 0.001 | 0.0001 | 0.04 | 0.1 | **DEGRADATION** | -0.3074 | 0.254 | 1.80 | 9,037 | 687s |
| 0.001 | 0.0001 | 0.04 | 0.2 | **DEGRADATION** | -0.2021 | 0.364 | 0.94 | 8,284 | 706s |
| 0.001 | 0.0001 | 0.04 | 0.3 | **STABLE** | -0.0194 | 0.555 | 0.17 | 8,395 | 692s |
| 0.003 | 0.0003 | 0.12 | 0.05 | **DEGRADATION** | -0.4277 | 0.104 | 1.57 | 7,969 | 810s |
| 0.003 | 0.0003 | 0.12 | 0.1 | **DEGRADATION** | -0.3490 | 0.183 | 1.43 | 7,615 | 846s |
| 0.003 | 0.0003 | 0.12 | 0.2 | **DEGRADATION** | -0.2696 | 0.269 | 0.27 | 6,455 | 858s |
| 0.003 | 0.0003 | 0.12 | 0.3 | **DEGRADATION** | -0.1806 | 0.369 | 0.43 | 5,865 | 848s |
| 0.005 | 0.0005 | 0.20 | 0.05 | **DEGRADATION** | -0.4265 | 0.080 | 1.35 | 6,428 | 845s |
| 0.005 | 0.0005 | 0.20 | 0.1 | **DEGRADATION** | -0.3589 | 0.149 | -0.00 | 6,209 | 820s |
| 0.005 | 0.0005 | 0.20 | 0.2 | **DEGRADATION** | -0.2679 | 0.248 | 0.47 | 5,486 | 914s |
| 0.005 | 0.0005 | 0.20 | 0.3 | **DEGRADATION** | -0.1880 | 0.340 | -0.00 | 5,099 | 1106s |
| 0.01 | 0.001 | 0.40 | 0.05 | **DEGRADATION** | -0.3776 | 0.064 | -0.00 | 4,672 | 1142s |
| 0.01 | 0.001 | 0.40 | 0.1 | **DEGRADATION** | -0.3335 | 0.110 | 1.11 | 3,974 | 1204s |
| 0.01 | 0.001 | 0.40 | 0.2 | **DEGRADATION** | -0.2849 | 0.172 | -0.00 | 3,102 | 1197s |
| 0.01 | 0.001 | 0.40 | 0.3 | **DEGRADATION** | -0.2572 | 0.217 | -0.00 | 2,605 | 1277s |

## Individual Plots

### rate=0.001 (≡0.0001@L400), K=0.05 → **DEGRADATION**
![mut0.001_k0.05](/home/michael/gc_simulation/results/sweep_L40/mut0.001_k0.05.png)

### rate=0.001 (≡0.0001@L400), K=0.1 → **DEGRADATION**
![mut0.001_k0.1](/home/michael/gc_simulation/results/sweep_L40/mut0.001_k0.1.png)

### rate=0.001 (≡0.0001@L400), K=0.2 → **DEGRADATION**
![mut0.001_k0.2](/home/michael/gc_simulation/results/sweep_L40/mut0.001_k0.2.png)

### rate=0.001 (≡0.0001@L400), K=0.3 → **STABLE**
![mut0.001_k0.3](/home/michael/gc_simulation/results/sweep_L40/mut0.001_k0.3.png)

### rate=0.003 (≡0.0003@L400), K=0.05 → **DEGRADATION**
![mut0.003_k0.05](/home/michael/gc_simulation/results/sweep_L40/mut0.003_k0.05.png)

### rate=0.003 (≡0.0003@L400), K=0.1 → **DEGRADATION**
![mut0.003_k0.1](/home/michael/gc_simulation/results/sweep_L40/mut0.003_k0.1.png)

### rate=0.003 (≡0.0003@L400), K=0.2 → **DEGRADATION**
![mut0.003_k0.2](/home/michael/gc_simulation/results/sweep_L40/mut0.003_k0.2.png)

### rate=0.003 (≡0.0003@L400), K=0.3 → **DEGRADATION**
![mut0.003_k0.3](/home/michael/gc_simulation/results/sweep_L40/mut0.003_k0.3.png)

### rate=0.005 (≡0.0005@L400), K=0.05 → **DEGRADATION**
![mut0.005_k0.05](/home/michael/gc_simulation/results/sweep_L40/mut0.005_k0.05.png)

### rate=0.005 (≡0.0005@L400), K=0.1 → **DEGRADATION**
![mut0.005_k0.1](/home/michael/gc_simulation/results/sweep_L40/mut0.005_k0.1.png)

### rate=0.005 (≡0.0005@L400), K=0.2 → **DEGRADATION**
![mut0.005_k0.2](/home/michael/gc_simulation/results/sweep_L40/mut0.005_k0.2.png)

### rate=0.005 (≡0.0005@L400), K=0.3 → **DEGRADATION**
![mut0.005_k0.3](/home/michael/gc_simulation/results/sweep_L40/mut0.005_k0.3.png)

### rate=0.01 (≡0.001@L400), K=0.05 → **DEGRADATION**
![mut0.01_k0.05](/home/michael/gc_simulation/results/sweep_L40/mut0.01_k0.05.png)

### rate=0.01 (≡0.001@L400), K=0.1 → **DEGRADATION**
![mut0.01_k0.1](/home/michael/gc_simulation/results/sweep_L40/mut0.01_k0.1.png)

### rate=0.01 (≡0.001@L400), K=0.2 → **DEGRADATION**
![mut0.01_k0.2](/home/michael/gc_simulation/results/sweep_L40/mut0.01_k0.2.png)

### rate=0.01 (≡0.001@L400), K=0.3 → **DEGRADATION**
![mut0.01_k0.3](/home/michael/gc_simulation/results/sweep_L40/mut0.01_k0.3.png)
