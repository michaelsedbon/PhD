# EXP_002 — Documentation Index

Index of all markdown and documentation files in this experiment.

---

## Planning & Architecture

| File | Description |
|------|-------------|
| `summary.md` | Experiment overview, goals, and progress |
| `LOG.md` | Chronological experiment log |
| `SCRIPT_INDEX.md` | Script and file index |
| `DOC_INDEX.md` | This file |

## Simulation Documentation

| File | Description |
|------|-------------|
| `docs/brainstorm_gpu_germinal_center.md` | Architecture brainstorm (JAX, SoA, GPU strategy) |
| `docs/shape_space_explainer.md` | Shape space concept explained (L=4, Hamming, Gaussian) |
| `docs/selection_model_analysis.md` | 4 selection models for synthetic GC |
| `docs/flow_diagram_A_natural_GC.md` | Flow Diagram A — 3D lattice GC (paper reproduction) |
| `docs/flow_diagram_B_bacterial_GC.md` | Flow Diagram B — bacterial synthetic GC |
| `docs/implementation_plan.md` | Phase 0 implementation plan |
| `docs/handoff_checklist.md` | Master handoff checklist (all phases) |
| `docs/open_questions.md` | Scientific questions for GC parameter exploration (Q1-Q11) |
| `docs/model_reference_natural_gc.md` | Comprehensive model reference: all parameters, tuning, equations |
| `docs/analysis_mullers_ratchet.md` | Muller's ratchet analysis — why affinity degrades at high mutation |
| `CODE_REVIEW.md` | Clickable code debug doc for all 11 natural GC modules |

## Results & Analysis

| File | Description |
|------|-------------|
| `simulation/results/archive/RESULTS.md` | Archive of early runs with embedded plots |
| `simulation/results/sweep/SWEEP_ANALYSIS.md` | L=400 parameter sweep: heatmaps, row-by-row analysis |
| `simulation/results/controls/CONTROLS.md` | 5 simulation validation controls |
| `simulation/results/SWEEP_COMPARISON.md` | L=400 vs L=40 sweep comparison with next steps |
| `simulation/results/sweep_L40/` | L=40 GPU validation sweep heatmaps and results |
| `simulation/results/sweep_T7_rates/T7_RATES_ANALYSIS.md` | Corrected T7 rate sweep: 24 runs, 5 key findings |
| `presentation/GC_Simulation_Lab_Meeting.pptx` | 20-slide lab meeting presentation |
| `simulation/results/OVERNIGHT_RESULTS.md` | 3 overnight experiments: multi-seed, GC vs DE, N=10⁷ |
| `simulation/results/multiseed_V4/` | Multi-seed V4 boundary: 40 runs, per-cycle history |
| `simulation/results/gc_vs_de/` | GC vs Directed Evolution: 36 runs, per-cycle history |
| `simulation/results/scaling_10M/` | N=10⁷ scaling: 8 runs (pop cap issue) |
