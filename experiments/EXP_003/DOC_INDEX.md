# EXP_003 — Document Index

## Experiment Files

| File | Description |
|---|---|
| `summary.md` | Experiment overview, architecture, and progress |
| `LOG.md` | Chronological work log |
| `DOC_INDEX.md` | This file |
| `KICKOFF_PROMPT.md` | Full context prompt for new chat |

## Scientific Documents (`docs/`)

| File | Description |
|---|---|
| `flow_diagram_v2_pipeline.md` | Pipeline flow diagram (current model design) |
| `flow_diagram_bacterial_GC.md` | Prior flow diagram (batch model, superseded) |
| `PARAMETER_BIOLOGY_REFERENCE.md` | Parameter-to-biology mapping |
| `open_questions.md` | Scientific questions (Q1–Q12) |
| `selection_model_analysis.md` | Hill vs competitive selection |
| `shape_space_explainer.md` | Affinity / shape space model |
| `mullers_ratchet.md` | Mutation load analysis |
| `grant_proposal.md` | Maimonide 2026 grant proposal text |
| `handoff_live_sweep_tracking.md` | Spec for live sweep tracking feature |

## Dashboard (`dashboard/`)

| File | Description |
|---|---|
| `server.py` | FastAPI backend — health monitoring, sweep APIs, docs serving |
| `static/index.html` | Dashboard HTML (4 tabs: Health, Results, Docs, Sweep Explorer) |
| `static/app.js` | Frontend JS — polling, charts, sweep visualizations |
| `static/style.css` | Design system (dark theme, Synthetica brand) |

**Dashboard URL**: http://172.16.1.80:8050

## Simulation Code (on server: `~/gc_simulation/EXP_003/`)

| File | Description |
|---|---|
| `overnight_sweep.py` | 432-run full parameter sweep script |
| `sweep_population_size.py` | 72-run population size sweep script |
| `sim/config.py` | Simulation parameters dataclass |
| `sim/run.py` | Simulation runner + result saving |
| `sim/pipeline.py` | Pipeline orchestrator (one DZ→LZ cycle) |
| `sim/progress.py` | Live sweep progress tracker |
| `sim/metrics.py` | Per-snapshot metric collection |
| `sim/grow.py` | Turbidostat growth + mutation |
| `sim/select.py` | Competitive top-fraction selection |
| `sim/affinity.py` | Shape-space affinity calculation |

## Key Papers (`docs/papers/`)

| File | Description |
|---|---|
| `Robert_How_to_Simulate_GC.txt` | Robert et al. — hyphasma GC simulation model |
| `Mesin_GC_Dynamics.txt` | Mesin 2016 — GC B cell dynamics review |
| `Diercks_T7_Replisome.txt` | Diercks 2024 — orthogonal T7 replisome for in vivo mutagenesis |
| `Victora_Nussenzweig_GC_Review.txt` | Victora 2012 — GC biology review |
| `Tas_Visualizing_Affinity_Maturation.txt` | Tas 2016 — clonal diversity & affinity maturation |
| `Shinnakasu_Regulated_Selection_GC.txt` | Shinnakasu — regulated selection of GC cells |
| `Sprumont_GC_Clonal_Diversity.txt` | Sprumont — GC clonal diversity output |
| `Ravikumar_OrthoRep.txt` | Ravikumar 2018 — OrthoRep continuous mutagenesis |
