# EXP_003 — Bacterial Synthetic Germinal Center: GPU Simulation v2

**Date**: 2026-03-19  
**Status**: 🔄 In progress — simulation running, dashboard live  
**Goal**: Rewrite the bacterial GC simulation from scratch with a biologically accurate pipeline model  
**Server**: `172.16.1.80` (RTX 2080 Ti, 11 GB VRAM)  
**Dashboard**: http://172.16.1.80:8050

## Context

Continuation of EXP_002 simulation work. Key lessons from EXP_002:
- **Pipeline model** (continuous DZ→LZ cycling) is more realistic than batch
- **Competitive selection** (top-fraction) better models T cell / bead competition than Hill (independent)
- **N=10M** populations show 2× more diversity than N=10K but no more affinity depth
- The maturation boundary sits between T7 V3 (10⁻⁶) and V4 (10⁻⁵)
- Selection stringency in natural GC is ~10-30% survival per LZ visit

## Simulation Architecture

Complete rewrite of the GC sim as a **continuous pipeline model** (DZ→LZ cycling with fractional sampling). All code in `~/gc_simulation/EXP_003/` on the GPU server.

### Core Modules (`sim/`)

| Module | Purpose |
|--------|---------|
| `config.py` | Simulation parameters (dataclass) |
| `state.py` | Population state arrays |
| `init.py` | Founder population initialization |
| `grow.py` | Turbidostat growth + mutation (DZ) |
| `sample.py` | Fractional sampling from DZ→LZ |
| `select.py` | Competitive top-fraction selection (LZ) |
| `affinity.py` | Shape-space affinity model |
| `balance.py` | Population rebalancing |
| `buffer.py` | Buffer zone management |
| `return_dz.py` | LZ→DZ return |
| `pipeline.py` | Pipeline orchestrator (one cycle) |
| `run.py` | Full simulation runner + result saving |
| `metrics.py` | Per-snapshot metrics collection |
| `progress.py` | Live sweep progress tracker (writes `progress.json`) |

### Mutation Rates (Diercks et al. 2024)

| Variant | Rate (spb/gen) | Label |
|---------|---------------|-------|
| Δ28 (wild-type) | 3.31×10⁻⁸ | Baseline |
| Double (N520M+P560V) | 4.26×10⁻⁶ | ~130× increase |
| Triple (+V443K) | 1.04×10⁻⁵ | ~310× increase |
| Quintuple (+Y24F+Q585R) | 1.73×10⁻⁵ | ~520× increase |

## Sweep Scripts

### Sweep 1: Overnight Parameter Sweep (432 runs)

**Script**: `overnight_sweep.py`  
**Output**: `results/overnight_sweep/`  
**Grid**: 4 mutation rates × 3 keep fractions × 3 sample fractions × 3 leak fractions × 2 incubation times × 2 target Ns = 432 runs

Explores the full operating envelope of the bacterial GC across all parameter axes.

### Sweep 2: Population Size Sweep (72 runs)

**Script**: `sweep_population_size.py`  
**Output**: `results/sweep_2026-03-20/`  
**Grid**: 6 target Ns (10K–5M) × 4 mutation rates × 3 keep fractions = 72 runs  
**Intent**: Definitive test of population size (target_n) effect on affinity and diversity. Spans 3 orders of magnitude to determine if future sweeps can use smaller N.  
**Hypothesis**: Population size has no effect on affinity (confirmed R²=0.990 from sweep 1) but may marginally increase diversity.

## Dashboard

**URL**: http://172.16.1.80:8050  
**Stack**: FastAPI backend + vanilla JS/HTML/CSS frontend  
**Server file**: `dashboard/server.py`  
**Frontend**: `dashboard/static/` (app.js, index.html, style.css)

### Tabs

| Tab | Content |
|-----|---------|
| **Server Health** | GPU temp, VRAM, CPU, RAM, disk, uptime, time-series charts, **live sweep progress card** |
| **Simulation Results** | Browse individual run JSON files, view configs and final metrics |
| **Architecture & Design** | Rendered markdown documentation (flow diagrams, parameter reference, etc.) |
| **Sweep Explorer** | Multi-sweep comparison with filters, heatmaps, 3D plots, parallel coordinates, N-scaling, time courses, notes |

### Sweep Explorer Visualizations

- **Parallel Coordinates** (coloured by affinity / Shannon H) — shown for multi-parameter sweeps
- **Faceted Heatmaps** (mutation × keep → metric, split by N) — for 2-N sweeps
- **3D Surface Plots** (mutation rate × keep fraction × metric)
- **Paired Comparison** (N=100K vs N=1M scatter)
- **Population Size Scaling** (metric vs target_n with SEM error bars) — for N-sweep
- **Dual-Axis Time Courses** (affinity + Shannon H over cycles, grouped by mutation rate)

### Live Sweep Progress Tracking

When a sweep is running, the Server Health tab shows a live progress card:
- Animated progress bar with ETA
- Current run ID and parameters
- Timing stats (mean/fastest/slowest per run)
- Mini table of last 5 completed runs
- Live Plotly scatter of affinity vs run index
- Polls `/api/sweeps/active` every 5 seconds

**Implementation**: `sim/progress.py` (SweepProgressTracker class) → writes `progress.json` → read by API → polled by frontend.

## Reference Documents

See `docs/` folder:
- `grant_proposal.md` — Maimonide 2026 grant proposal text
- `PARAMETER_BIOLOGY_REFERENCE.md` — parameter-to-biology mapping
- `open_questions.md` — scientific questions (Q1–Q12)
- `selection_model_analysis.md` — Hill vs competitive selection
- `flow_diagram_v2_pipeline.md` — pipeline flow diagram (current design)
- `flow_diagram_bacterial_GC.md` — prior flow diagram
- `shape_space_explainer.md` — affinity / shape space model
- `mullers_ratchet.md` — mutation load analysis
- `handoff_live_sweep_tracking.md` — live sweep tracking spec

## Progress

- [x] Flow diagram (pipeline model v2)
- [x] Core data structures (`config.py`, `state.py`)
- [x] Growth (turbidostat + mutation)
- [x] Selection (competitive top-fraction)
- [x] Pipeline runner
- [x] Metrics collection
- [x] Overnight parameter sweep (432 runs)
- [x] Population size sweep (72 runs)
- [x] Dashboard (4-tab, real-time monitoring)
- [x] Live sweep progress tracking
- [ ] Controls & validation
- [ ] Benchmark experiments
- [ ] Further targeted sweeps
