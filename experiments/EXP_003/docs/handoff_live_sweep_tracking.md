# Task: Add Live Sweep Progress Tracking to EXP_003 Dashboard

## Context

The EXP_003 GC simulation dashboard runs at `http://172.16.1.80:8050` (FastAPI backend + vanilla JS frontend). Simulation sweeps are launched via Python scripts (e.g., `sweep_population_size.py`) that iterate over a parameter grid, run simulations sequentially, and write JSON result files to `results/sweep_YYYY-MM-DD/`.

**Server code**: `~/gc_simulation/EXP_003/dashboard/server.py` (FastAPI, uvicorn --reload)  
**Frontend**: `~/gc_simulation/EXP_003/dashboard/static/index.html` + `app.js`  
**Sweep scripts**: `~/gc_simulation/EXP_003/overnight_sweep.py`, `sweep_population_size.py`  
**SSH access**: `michael@172.16.1.80`  
**Local copy**: `/Users/michaelsedbon/Documents/PhD/experiments/EXP_003/dashboard/`

## Goal

Add a live progress tracking system so that when a sweep is running, the dashboard shows real-time progress without needing to SSH into the server. This should work for **future sweeps** — do NOT modify or restart any currently running sweep.

## Architecture (3 components)

### 1. Progress File Writer — `sim/progress.py`

Create a reusable helper class `SweepProgressTracker` that sweep scripts can import. After each completed run, it writes/updates `results/<sweep_id>/progress.json`:

```json
{
  "sweep_id": "sweep_2026-03-20",
  "status": "running",
  "started_at": "2026-03-20T13:42:00",
  "total_runs": 72,
  "completed": 23,
  "failed": 0,
  "current_run": {
    "id": "N500000_mu-triple_k0.1",
    "index": 24,
    "params": {"target_n": 500000, "paper_mutation_rate": 1.04e-5, "keep_fraction": 0.1}
  },
  "eta_minutes": 42.5,
  "runs_completed": [
    {
      "id": "N10000_mu-delta28_k0.05",
      "duration_seconds": 8.2,
      "final_affinity": 0.031,
      "final_shannon": 1.85,
      "target_n": 10000
    }
  ],
  "timing": {
    "mean_per_run": 15.3,
    "fastest": 4.1,
    "slowest": 62.8
  }
}
```

API for sweep scripts:
```python
from sim.progress import SweepProgressTracker

tracker = SweepProgressTracker(sweep_id, total_runs, output_dir)
tracker.start_run(run_id, run_index, params_dict)
tracker.complete_run(run_id, duration, final_metrics_dict)
tracker.fail_run(run_id, error_message)
tracker.finalize()  # sets status="completed"
```

When the sweep finishes, set `"status": "completed"` with final summary.

Then modify **both** `sweep_population_size.py` and `overnight_sweep.py` to use it as reference implementations. Keep `runs_completed` to the **last 20** entries to keep the file small.

### 2. API Endpoint — `server.py`

Add to `server.py`:

```
GET /api/sweeps/active
```

Scans all `results/sweep_*/progress.json` files:
- Returns the one with `"status": "running"` (if any)
- Otherwise returns the most recent `"status": "completed"`
- Returns `{"status": "idle"}` if no progress files exist

### 3. Frontend — Server Health tab

In the **Server Health** tab (first tab, `panel-health`), add a "Sweep Progress" card. It should:

**Auto-refresh** every 5 seconds via polling `/api/sweeps/active`.

**When no sweep is active**: Show a subtle muted message — "No active sweep".

**When a sweep IS running**, show:
- Sweep ID and start time
- Animated progress bar: `"23/72 runs (32%)"` — use CSS animation for the bar fill
- ETA: `"~42 min remaining"`
- Current run: `"Running: N500000_mu-triple_k0.1"`
- Timing stats: `"Mean: 15.3s/run | Fastest: 4.1s | Slowest: 62.8s"`
- Mini table of the **last 5 completed runs** with columns: run_id, duration, affinity, shannon
- Small live Plotly scatter: completed runs' `final_affinity` (y) vs `target_n` or run index (x), updating as new points arrive

**When sweep is completed**: Same layout but with a green `"✓ Complete"` badge, total runtime, and summary stats. Stop polling.

### Style Guide

Match the existing dashboard dark theme. The CSS uses variables:
- `--bg-card`, `--text`, `--text-muted`, `--accent`, `--success`, `--warning`, `--error`
- Cards: `class="card"` with `class="card-title"` for headers
- Icons: Lucide (already loaded via CDN), e.g. `<i data-lucide="activity" class="lucide-icon"></i>`
- Fonts: Inter for UI, JetBrains Mono for numbers/code

### Deployment

After making changes:
1. SCP modified files to server: `scp <local_path> michael@172.16.1.80:~/gc_simulation/EXP_003/<remote_path>`
2. The server auto-reloads on file changes (uvicorn `--reload`)
3. Verify at `http://172.16.1.80:8050`

### Important Notes

- Do NOT restart any currently running sweep. This feature is for **future** sweeps.
- Read `server.py` before adding endpoints — it uses FastAPI with pydantic.
- Read `overnight_sweep.py` and `sweep_population_size.py` to understand the sweep loop structure before modifying them.
- Keep `progress.json` small — summary metrics only, not full run data.
- The frontend polling should use `setTimeout` (not `setInterval`) to avoid stacking requests if the server is slow.
- Add the progress card at the TOP of the Server Health tab, before the existing GPU/CPU/RAM cards.
