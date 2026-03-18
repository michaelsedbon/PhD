# EXP_002 — Script & File Index

Index of all scripts, source code, and generated artifacts.

---

## Source Code — `simulation/src/germinal_center/`

| File | Lines | Description |
|------|-------|-------------|
| `config.py` | 115 | All paper parameters (Tables 1-2) as GCConfig dataclass |
| `affinity.py` | ~200 | Shape space, Hamming distance, Gaussian affinity, mutation |
| `state.py` | ~240 | Padded fixed-size NamedTuples (MAX_CB=10K), slot allocator |
| `chemotaxis.py` | ~140 | 3D diffusion with auto sub-stepping, chemokine production |
| `movement.py` | ~230 | vmap parallel movement + scatter conflict resolution |
| `cell_cycle.py` | ~200 | G1→S→G2→M phases, division into free slots, CB→CC transition |
| `selection.py` | ~240 | FDC antigen capture, T cell help, vectorized apoptosis |
| `differentiation.py` | ~220 | Slot-based recycling, output cells, founder inflow |
| `initialization.py` | ~190 | Spherical grid, agent placement into padded arrays |
| `simulation.py` | ~170 | Main loop orchestrating all 11 blocks |
| `analysis.py` | ~240 | Snapshot dataclass, 4 plot functions |

## Runner Scripts — `simulation/`

| File | Description |
|------|-------------|
| `run.py` | Quick test runner (local) |
| `run_7day.py` | 7-day simulation (dt=0.05, fast preview) |
| `run_21day.py` | 21-day paper reproduction (dt=0.002, GPU) |

## Tests — `simulation/tests/`

| File | Description |
|------|-------------|
| `test_affinity.py` | 15 unit tests for shape space and affinity |

## Notebooks — `simulation/notebooks/`

| File | Description |
|------|-------------|
| `01_block_checkpoints.ipynb` | 6 checkpoint validations (init, affinity, chemokines, movement, division, full pipeline) |

## Server Deployment — `michael@172.16.1.80:~/gc_simulation/`

| Path | Description |
|------|-------------|
| `src/germinal_center/` | Mirror of local source code |
| `.venv/` | Python venv with JAX+CUDA 12 |
| `results/` | Simulation output (plots, pickle, logs) |
| `run_7day.py`, `run_21day.py` | Runner scripts |
| `run_overnight.py` | Overnight 21-day with tuned params |
| `launch_sim.sh` | Shell launcher for nohup execution |

## Source Code — `simulation/src/bacterial_gc/`

| File | Lines | Description |
|------|-------|-------------|
| `config.py` | ~70 | BacterialConfig: growth modes, 4 selection models, all experiment knobs |
| `state.py` | ~60 | BacterialState NamedTuple, Snapshot, no grid |
| `growth.py` | ~140 | Turbidostat growth with per-cell division counters |
| `migration.py` | ~55 | DZ↔LZ robotic transfers (unused in v2 — division-triggered) |
| `selection.py` | ~110 | 4 models: Hill, threshold, top-K, bead binding |
| `simulation.py` | ~180 | Cycle loop: grow → divide-trigger → select → recycle |
| `analysis.py` | ~110 | Snapshot + 4-panel plots (with custom titles) |
| `state_gpu.py` | ~90 | GPU-optimized padded state with pre-allocated arrays |
| `growth_gpu.py` | ~210 | GPU growth: chunked affinity, scatter mutations |
| `selection_gpu.py` | ~75 | GPU selection: Hill + directed evolution (top-K) baseline |
| `simulation_gpu.py` | ~170 | GPU simulation loop with selection_mode (gc/directed_evolution) |

## Sweep & Validation Scripts — `simulation/`

| File | Description |
|------|-------------|
| `sweep.py` | Parameter sweep: mutation_rate × hill_k × selection_mode grid |
| `sweep_L40.py` | L=40 GPU validation sweep with scaled parameters |
| `validate_controls.py` | 5 validation controls (zero mut, no sel, DE, low mut, lethal) |

## Results — `simulation/results/`

| Path | Description |
|------|-------------|
| `archive/RESULTS.md` | Archive of early ad-hoc runs (varied cycle counts) |
| `sweep/SWEEP_ANALYSIS.md` | L=400 sweep heatmaps, row-by-row analysis, commentary |
| `controls/CONTROLS.md` | 5 validation controls with pass/fail verdicts |
| `sweep_L40/` | L=40 GPU validation sweep (in progress) |
