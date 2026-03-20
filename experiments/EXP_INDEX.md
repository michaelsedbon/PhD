# Experiment Index

This file is auto-maintained by the sync scripts and AI assistant.

---

## EXP_001 — Restriction Site Analysis & Primer Design for Golden Gate Genome Tiling

| Field | Value |
|-------|-------|
| **Objective** | Tile the *E. coli* MG1655 genome (~4.64 Mb) into ~7 kb PCR fragments for Golden Gate assembly into MoClo Lvl0 → Lvl1 constructs |
| **Status** | ✅ Complete (in-silico) |
| **Started** | 2026-02-20 |
| **Organism** | *E. coli* K-12 MG1655 (U00096.3) |
| **Enzyme** | BsaI (GGTCTC) |

### Key Results

| Metric | Value |
|--------|-------|
| Genome tiles designed | **686** (~7 kb each) |
| Tiles GG-ready (no internal BsaI) | 487 / 686 (71%) |
| Tiles requiring OE-PCR domestication | 185 |
| Lvl1 groups (before domestication) | 2 / 63 complete (3%) |
| Lvl1 groups (after domestication) | **63 / 63 complete (100%)** |
| Total primers to order | 1,850 (686 tile pairs + 478 mutagenic) |
| Total PCR reactions | 1,118 |

### Reports

| Report | Description |
|--------|-------------|
| [summary.md](EXP_001/summary.md) | Master summary with all figures |
| [REPORT.md](EXP_001/REPORT.md) | Restriction site analysis |
| [PRIMER_DESIGN_REPORT.md](EXP_001/PRIMER_DESIGN_REPORT.md) | Genome tiling & primer design |
| [PCR_SIMULATION_REPORT.md](EXP_001/PCR_SIMULATION_REPORT.md) | PCR simulation & Lvl1 assembly |
| [DOMESTICATION_REPORT.md](EXP_001/DOMESTICATION_REPORT.md) | OE-PCR domestication primers |
| [V2_REPORT.md](EXP_001/V2_REPORT.md) | V2 redesign — standardized overhangs & 100 kb groups |
| [CODE_REVIEW.md](EXP_001/CODE_REVIEW.md) | Pipeline code review — all algorithmic decisions & potential issues |
| [SCRIPTS.md](EXP_001/SCRIPTS.md) | Script documentation |
| [literature_review_large_fragment_cloning.md](EXP_001/literature_review_large_fragment_cloning.md) | CAPTURE vs CATCH vs MoClo for T7 replisome |
| [state_of_the_art_ecoli_genome_libraries.md](EXP_001/state_of_the_art_ecoli_genome_libraries.md) | Survey of *E. coli* genome library approaches |
| [LOG.md](EXP_001/LOG.md) | Experiment log |

### Scripts

| Script | Purpose |
|--------|---------|
| [restriction_utils.py](EXP_001/scripts/restriction_utils.py) | Genome download, site mapping |
| [primer_design.py](EXP_001/scripts/primer_design.py) | Tiling + primer design |
| [pcr_simulation.py](EXP_001/scripts/pcr_simulation.py) | PCR simulation + Lvl1 analysis |
| [domestication_primers.py](EXP_001/scripts/domestication_primers.py) | OE-PCR mutagenic primer design |
| [pipeline_v2.py](EXP_001/scripts/pipeline_v2.py) | V2 pipeline (standardized overhangs) |

---

## EXP_002 — GPU Simulation of Synthetic Germinal Center

| Field | Value |
|-------|-------|
| **Objective** | Build a GPU-ready simulation (Python+JAX) of the synthetic germinal center: reproduce the hyphasma paper, then adapt to bacterial system with bead-based selection |
| **Status** | 🔄 In progress (planning complete, coding Phase 0) |
| **Started** | 2026-03-16 |
| **GPU** | RTX 2080 Ti (11 GB VRAM) on `172.16.1.80` |
| **Project** | [The Synthetic Germinal Center](../projects/synthetic_germinal_center/summary.md) |

### Key Documents

| Document | Description |
|----------|-------------|
| [summary.md](EXP_002/summary.md) | Experiment overview |
| [Flow Diagram A](EXP_002/simulation/docs/flow_diagram_A_natural_GC.md) | 3D lattice GC (paper reproduction) |
| [Flow Diagram B](EXP_002/simulation/docs/flow_diagram_B_bacterial_GC.md) | Bacterial synthetic GC |
| [Handoff Checklist](EXP_002/simulation/docs/handoff_checklist.md) | Master checklist (Phases 0-4) |
| [Implementation Plan](EXP_002/simulation/docs/implementation_plan.md) | Phase 0 plan |
| [LOG.md](EXP_002/LOG.md) | Experiment log |

---

## EXP_003 — Bacterial Synthetic GC: Pipeline Model & Parameter Sweeps

| Field | Value |
|-------|-------|
| **Objective** | Rewrite the GC simulation with a biologically accurate pipeline model (continuous DZ→LZ cycling), run large-scale parameter sweeps, and build a real-time monitoring dashboard |
| **Status** | 🔄 In progress (simulation running, dashboard live) |
| **Started** | 2026-03-19 |
| **GPU** | RTX 2080 Ti (11 GB VRAM) on `172.16.1.80` |
| **Dashboard** | http://172.16.1.80:8050 |
| **Project** | [The Synthetic Germinal Center](../projects/synthetic_germinal_center/summary.md) |

### Key Results

| Metric | Value |
|--------|-------|
| Simulation modules | 14 (config, state, init, grow, sample, select, affinity, balance, buffer, return_dz, pipeline, run, metrics, progress) |
| Sweep 1 (overnight) | 432 runs — 6-axis parameter grid |
| Sweep 2 (pop. size) | 72 runs — 10K to 5M target N |
| Dashboard tabs | 4 (Server Health, Results, Docs, Sweep Explorer) |

### Key Documents

| Document | Description |
|----------|-------------|
| [summary.md](EXP_003/summary.md) | Full experiment overview, architecture, progress |
| [LOG.md](EXP_003/LOG.md) | Chronological work log |
| [DOC_INDEX.md](EXP_003/DOC_INDEX.md) | Complete document index |
| [flow_diagram_v2_pipeline.md](EXP_003/docs/flow_diagram_v2_pipeline.md) | Pipeline model flow diagram |
| [PARAMETER_BIOLOGY_REFERENCE.md](EXP_003/docs/PARAMETER_BIOLOGY_REFERENCE.md) | Parameter-to-biology mapping |
| [open_questions.md](EXP_003/docs/open_questions.md) | Scientific questions (Q1–Q12) |

---
