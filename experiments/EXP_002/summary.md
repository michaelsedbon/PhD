# EXP_002: GPU Simulation of Synthetic Germinal Center

**Start Date:** 2026-03-16
**Status:** In progress
**Airtable Links:** None
**Project:** [The Synthetic Germinal Center](../../projects/synthetic_germinal_center/summary.md)

---

## Overview

Build a GPU-ready simulation of the synthetic germinal center described in the Maimonide 2026 proposal. The simulation models the bacterial "immune side" — populations of *E. coli* carrying nanobody variants undergoing cycles of mutagenic growth, migration, and affinity-based selection.

## Goal

1. **Phase 0**: Reproduce the hyphasma agent-based GC model (Robert et al.) to validate the simulation framework
2. **Phase 1**: Adapt to the bacterial synthetic GC (well-mixed compartments, bead selection, robotic transfers)
3. **Phase 2**: Scale to 10⁸ bacteria on GPU (JAX on RTX 2080 Ti, 11 GB)
4. **Phase 3**: Extend to 96-well parallel simulation
5. **Phase 4**: Add antigen co-evolution (future)

## Hardware

- **GPU**: RTX 2080 Ti (11 GB VRAM) on server `172.16.1.80`
- **Framework**: Python + JAX

## Progress

- [x] Paper and proposal read
- [x] Architecture brainstormed (JAX, SoA, particle-based)
- [x] Shape space and selection models documented
- [x] Flow Diagram A (natural GC) created
- [x] Flow Diagram B (bacterial GC) created
- [x] Master handoff checklist created
- [x] Phase 0 implementation (11 modules, 15 unit tests, 6 checkpoints passed)
- [x] Phase 0.75 GPU rewrite (padded arrays, vmap, vectorized scatter)
- [x] Deployed to GPU server (RTX 2080 Ti, 185ms/step)
- [x] Fixed T cell rescue bug (signal rate scaling)
- [x] Parameter tuning (founder_divisions, n_div_max, tc_time, collect_fdc_period)
- [/] 7-day validation v3 running (founder_div=4, n_div_max=2)
- [x] Phase 1 bacterial sim v1 (batch mode — too slow)
- [x] Phase 1 bacterial sim v2 (turbidostat + division-triggered migration — working!)
- [x] Phase 1 GPU modules created (state_gpu.py, growth_gpu.py, selection_gpu.py, simulation_gpu.py)
- [x] N=1M CPU simulation (108 min, 140 cycles) — Muller's ratchet observed
- [x] Parameter sweep L=400 N=10K: 4×4 grid (mutation_rate × hill_k)
- [x] Simulation validation controls (5 controls, all passing)
- [x] L-scaling analysis (L=400→L=40 with scaled parameters)
- [x] L=40 GPU validation sweep — completed, scaling validated
- [x] L=400 vs L=40 comparison — [SWEEP_COMPARISON.md](simulation/results/SWEEP_COMPARISON.md)
- [x] Directed evolution baseline comparison — [OVERNIGHT_RESULTS.md](simulation/results/OVERNIGHT_RESULTS.md)
- [x] Corrected sweep with actual T7 variant rates — [T7_RATES_ANALYSIS.md](simulation/results/sweep_T7_rates/T7_RATES_ANALYSIS.md)
- [x] Lab meeting presentation (20 slides) — [GC_Simulation_Lab_Meeting.pptx](presentation/GC_Simulation_Lab_Meeting.pptx)
- [x] JIT GPU optimization (380× speedup) — [JIT_VALIDATION_REPORT.md](simulation/results/JIT_VALIDATION_REPORT.md)
- [x] Q4: N-scaling to 10⁷ (81 runs) — [Q4_ANALYSIS.md](simulation/results/q4_n_scaling/Q4_ANALYSIS.md)
- [x] Q3: DZ/LZ cycling speed sweep (48 runs) — [Q3_ANALYSIS.md](simulation/results/q3_cycling/Q3_ANALYSIS.md)
- [ ] Q6: Multi-epitope breadth
- [ ] Phase 3: 96-well parallel simulation

## Results

### Natural GC (Phase 0)

| Run | Peak GC | DZ/LZ | Affinity | Lifespan | Issue |
|---|---|---|---|---|---|
| v1 (6 div, no TC fix) | 7500 | — | None | Dies day 3.5 | TC rescue bug |
| v2 (2 div, 1 recycle) | 750 | 2:1 ✅ | 0.13→0.30 ✅ | Dies day 4 | GC too small |
| v3 (4 div, 2 recycle) | — | — | — | Running | — |

### Bacterial GC (Phase 1)

| Version | Mode | Architecture | Mean Aff | Max Aff | Diversity | Issue |
|---|---|---|---|---|---|---|
| v1 | Batch | Random 10% transfer | 0.13→0.15 | 0.88 | Flat | Selection diluted |
| v2 | Turbidostat | Division-triggered | 0.13→**0.53** | **1.00** | 6.9→3.4 | Working ✅ |

### Parameter Sweep (L=400, N=10K, 140 cycles)

See [SWEEP_ANALYSIS.md](simulation/results/sweep/SWEEP_ANALYSIS.md) for full analysis.

| mut_rate | K=0.05 | K=0.1 | K=0.2 | K=0.3 |
|---|---|---|---|---|
| **0.0001** | DEGRAD | DEGRAD | STABLE | **MATUR ✅** |
| **0.0003** | DEGRAD | DEGRAD | DEGRAD | DEGRAD |
| **0.0005** (T7) | DEGRAD | DEGRAD | DEGRAD | DEGRAD |
| **0.001** | DEGRAD | DEGRAD | DEGRAD | DEGRAD |

> **Key finding**: Mutation rates used were 10-100× ABOVE actual T7 variant range. Only maturation at lowest rate (=highest T7 variant). Real T7 rates should show maturation across the board.

### Validation Controls

See [CONTROLS.md](simulation/results/controls/CONTROLS.md) — 5 controls, all passing.

### GPU Performance

| Metric | Before Rewrite | After Rewrite | Speedup |
|---|---|---|---|
| GPU ms/step | 3,600 | **185** | 19x |
| MacBook CPU ms/step | 1,600 | **80** | 20x |

## References

- Robert et al. *"How to Simulate a Germinal Center"* (2017) — [PDF](../../papers/modeling/How_to_Simulate_a_Germinal.pdf)
- Maimonide 2026 proposal — [DOCX](../../Grant_application/Maimonide_2026/proposal_form_latest.docx)
