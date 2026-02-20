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
| [LOG.md](EXP_001/LOG.md) | Experiment log |

### Scripts

| Script | Purpose |
|--------|---------|
| [restriction_utils.py](EXP_001/restriction_utils.py) | Genome download, site mapping |
| [primer_design.py](EXP_001/primer_design.py) | Tiling + primer design |
| [pcr_simulation.py](EXP_001/pcr_simulation.py) | PCR simulation + Lvl1 analysis |
| [domestication_primers.py](EXP_001/domestication_primers.py) | OE-PCR mutagenic primer design |

---
