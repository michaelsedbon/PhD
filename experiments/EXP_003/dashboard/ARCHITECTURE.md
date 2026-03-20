# EXP_003 Dashboard — Architecture & Usage

## Overview

The EXP_003 simulation dashboard visualises parameter sweep results for the bacterial GC (Germinal Centre) model. Each sweep produces a directory of JSON result files under `results/sweep_YYYY-MM-DD/`. The dashboard loads these results via a FastAPI backend and renders them in the browser.

## Directory Structure

```
EXP_003/
├── dashboard/
│   ├── server.py              # FastAPI backend (uvicorn --reload)
│   └── static/
│       ├── index.html         # Frontend layout
│       ├── app.js             # All rendering logic
│       └── style.css          # Dark theme
├── results/
│   ├── sweep_2026-03-19/      # First sweep (432 runs, multi-param)
│   │   ├── manifest.json      # Sweep config, intent, parameters
│   │   ├── notes.md           # Conclusions & notes
│   │   └── N*.json            # Per-run result files
│   └── sweep_2026-03-20/      # Population size sweep (72 runs)
│       ├── manifest.json
│       ├── notes.md
│       └── N*.json
├── sim/                       # Simulation code (JAX)
├── overnight_sweep.py         # Multi-param sweep runner
└── sweep_population_size.py   # Population-focused sweep runner
```

## How Sweeps Work

### 1. Design the sweep

Decide which parameters to sweep and which to fix. Write a Python script based on `overnight_sweep.py` or `sweep_population_size.py`.

### 2. Write the manifest

Every sweep **must** include a `manifest.json` with:

```json
{
  "sweep_id": "sweep_YYYY-MM-DD",
  "intent": "What this sweep aims to test (shown in dashboard header)",
  "hypothesis": "What we expect to find",
  "decision_criteria": "What result changes our next experiment",
  "fixed_parameters": { ... },
  "swept_parameters": { ... }
}
```

### 3. Run the sweep

```bash
cd ~/gc_simulation/EXP_003
source .venv/bin/activate
nohup python3 my_sweep.py > sweep_log.txt 2>&1 &
```

### 4. Design the visualisation

**Each sweep gets its own set of plots**, tailored to the question it's answering. There is no one-size-fits-all. The dashboard auto-detects the sweep type based on data and shows/hides sections.

Current sweep types:
- **Multi-param sweep** (2 N values): Parallel coords, heatmaps, 3D scatter, paired comparison, time courses
- **Population-size sweep** (>2 N values): N-scaling lines, relative change, box plots, R² heatmap, verdict card

### 5. Write conclusions

After analysis, edit `notes.md` in the sweep directory (editable from the dashboard's "Edit" button). Include:
- Key findings with numbers
- R² values, mean changes, statistical tests
- Recommendations for next sweep
- Open questions

---

## Per-Experiment Plot Design

### Principle

Plots should be designed **per experiment** based on the question being asked. Do NOT add generic catch-all plots. Each sweep explores a specific hypothesis — the plots should directly answer that hypothesis.

### Process

1. Run the sweep
2. Review the data in the dashboard (summary tables always load)
3. **Work together** to decide which plots would best answer the question
4. Implement the plots as new render functions in `app.js`
5. Add corresponding HTML sections in `index.html`
6. Show/hide logic in `applyFilters()` determines which sections appear per sweep

### Adding a new plot type

1. Add HTML section with unique `id` (e.g., `section-my-plot`) in `index.html`
2. Add `show('section-my-plot', condition)` in `applyFilters()`
3. Add `this.renderMyPlot()` call in the appropriate condition block
4. Add `renderMyPlot()` function in `app.js`

---

## Pre-computed Plots (Future)

### Goal

Move heavy computation from the browser to a server-side Python script. Benefits:
- Instant load times
- Reproducible outputs
- Traceable: every plot links to its source data

### Architecture

```
results/sweep_YYYY-MM-DD/
├── manifest.json
├── notes.md
├── N*.json                        # Raw run results
└── precomputed/
    ├── plot_index.json             # Maps plot IDs to files + source runs
    ├── n_scaling_affinity.json     # Pre-computed traces for Plotly
    ├── n_scaling_shannon.json
    ├── r2_matrix_affinity.json
    ├── r2_matrix_shannon.json
    ├── boxplot_affinity.json
    ├── boxplot_shannon.json
    ├── relchange_affinity.json
    ├── relchange_shannon.json
    └── verdict.json
```

### plot_index.json format

```json
{
  "sweep_id": "sweep_2026-03-20",
  "generated_at": "2026-03-20T16:30:00",
  "plots": [
    {
      "id": "n_scaling_affinity",
      "title": "Affinity vs Population Size",
      "file": "n_scaling_affinity.json",
      "source_runs": ["N10000_mu-delta28_k0.05.json", ...],
      "description": "Mean affinity vs target_n per (mutation × keep) condition"
    }
  ]
}
```

### Pre-computation script

A Python script (`precompute_plots.py`) reads raw run JSONs, computes all traces, and writes the pre-computed files. The frontend checks for `precomputed/plot_index.json` first; if present, loads traces directly. If not, falls back to computing in-browser.

### Traceability

Every pre-computed file records:
- Which source run files were used
- What computation was performed
- Timestamp of generation

This means we can always go back and verify how a plot was generated.
