# EXP_003 — Log

## 2026-03-19

### Setup
- Created experiment scaffold
- Copied reference docs from EXP_002 and grant application
- Copied key papers (GC biology, T7 replisome, selection models)
- Designed pipeline flow diagram v2 (`docs/flow_diagram_v2_pipeline.md`)

### Simulation Implementation
- Built complete simulation codebase on GPU server (`172.16.1.80`)
- Core modules: `config.py`, `state.py`, `init.py`, `grow.py`, `sample.py`, `select.py`, `affinity.py`, `balance.py`, `buffer.py`, `return_dz.py`, `pipeline.py`, `run.py`, `metrics.py`
- Competitive top-fraction selection model (not Hill)
- Continuous pipeline DZ→LZ cycling with fractional sampling

### Overnight Sweep (432 runs)
- Launched `overnight_sweep.py` — full 6-axis parameter grid
- Grid: 4 mutation rates × 3 keep × 3 sample × 3 leak × 2 incubation × 2 target N
- Results in `results/overnight_sweep/`

### Dashboard v1
- Built FastAPI + vanilla JS dashboard (`dashboard/`)
- Tabs: Server Health, Simulation Results, Architecture & Design, Sweep Explorer
- Real-time GPU/CPU/RAM monitoring with Chart.js time series
- Sweep Explorer with filters, parallel coordinates, heatmaps, 3D plots

## 2026-03-20

### Population Size Sweep (72 runs)
- Launched `sweep_population_size.py` — 6 target Ns (10K–5M) × 4 mutation rates × 3 keep fractions
- Intent: determine if population size affects affinity maturation
- Results in `results/sweep_2026-03-20/`

### Dashboard Improvements
- Added Sweep Explorer: faceted heatmaps, 3D surface plots, paired N comparison, time courses with SEM bands
- Parallel coordinates now only shown for multi-parameter sweeps (hidden for N-scaling sweeps)
- Experiment intent section now dynamically populated from sweep `manifest.json`
- Population Size Scaling plots with error bars (SEM across replicates)

### Live Sweep Progress Tracking
- Created `sim/progress.py` with `SweepProgressTracker` class
- Both sweep scripts now write live `progress.json` during execution
- Added `GET /api/sweeps/active` API endpoint to `server.py`
- Dashboard Server Health tab shows live progress card: animated progress bar, ETA, timing stats, mini run table, and Plotly affinity scatter
- Polls every 5s via `setTimeout`, stops on completion
