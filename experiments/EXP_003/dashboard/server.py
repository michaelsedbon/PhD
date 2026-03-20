"""
EXP_003 Simulation Dashboard — FastAPI Backend
Serves the frontend and provides real-time server health + simulation results.

Run: cd dashboard && pip install -r requirements.txt && python server.py
Access: http://172.16.1.80:8050
"""

import asyncio
import json
import math
import os
import subprocess
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import psutil
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
# On the GPU server, simulation results and docs live here:
SIM_ROOT = Path.home() / "gc_simulation" / "EXP_003"
RESULTS_DIR = SIM_ROOT / "results"
DOCS_DIR = SIM_ROOT / "docs"
FLOW_DIAGRAM_PATH = DOCS_DIR / "flow_diagram_v2_pipeline.md"

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="EXP_003 Simulation Dashboard", version="1.1.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Health history (in-memory ring buffer) ─────────────────────────────────────
HEALTH_HISTORY: deque = deque(maxlen=300)
BOOT_TIME = psutil.boot_time()


# ══════════════════════════════════════════════════════════════════════════════
# DATA ADAPTER — normalise our JSON output to what the frontend expects
# ══════════════════════════════════════════════════════════════════════════════

def _normalise_run(raw: dict) -> dict:
    """
    Adapt our simulation output format to the dashboard's expected schema.
    Handles both legacy and current formats gracefully.
    """
    config = raw.get("config", {})
    # Our output uses 'snapshots', dashboard expects 'metrics'
    metrics = raw.get("metrics") or raw.get("snapshots", [])

    normalised_metrics = []
    for m in metrics:
        nm = dict(m)  # shallow copy
        # Field renames: n_dz → n_in_dz etc.
        if "n_in_dz" not in nm and "n_dz" in nm:
            nm["n_in_dz"] = nm.pop("n_dz")
        if "n_in_lz" not in nm and "n_lz" in nm:
            nm["n_in_lz"] = nm.pop("n_lz")
        if "n_in_buffer" not in nm and "n_buffer" in nm:
            nm["n_in_buffer"] = nm.pop("n_buffer")
        # Generate clone_size_distribution from top_clones if missing
        if "clone_size_distribution" not in nm and "top_clones" in nm:
            nm["clone_size_distribution"] = [
                c.get("frequency", 0) for c in nm["top_clones"]
            ]
        normalised_metrics.append(nm)

    return {
        "timestamp": raw.get("timestamp", ""),
        "config": config,
        "metrics": normalised_metrics,
        "timing": raw.get("timing", {}),
    }


def _iter_result_files():
    """Walk results/ and all sweep subdirectories for JSON files."""
    if not RESULTS_DIR.exists():
        return
    # Direct children
    for f in sorted(RESULTS_DIR.iterdir()):
        if f.suffix == ".json":
            yield f
    # Sweep subdirectories (sweep_*)
    for subdir in sorted(RESULTS_DIR.iterdir()):
        if subdir.is_dir() and subdir.name.startswith("sweep"):
            for f in sorted(subdir.iterdir()):
                if f.suffix == ".json" and f.name != "manifest.json":
                    yield f


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _get_gpu_info() -> dict:
    """Parse nvidia-smi for GPU stats. Returns empty dict if unavailable."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return {}
        line = result.stdout.strip().split("\n")[0]
        parts = [p.strip() for p in line.split(",")]
        return {
            "gpu_name": parts[0],
            "gpu_temp": int(parts[1]),
            "gpu_utilization": int(parts[2]),
            "gpu_memory_used_mb": int(parts[3]),
            "gpu_memory_total_mb": int(parts[4]),
        }
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return {}


def _get_nvidia_smi_full() -> str:
    """Get full nvidia-smi output for display."""
    try:
        result = subprocess.run(
            ["nvidia-smi"], capture_output=True, text=True, timeout=5
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def _collect_health() -> dict:
    """Collect all system health metrics."""
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime_seconds = time.time() - BOOT_TIME

    data = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=0),
        "ram_used_gb": round(mem.used / (1024 ** 3), 2),
        "ram_total_gb": round(mem.total / (1024 ** 3), 2),
        "disk_used_gb": round(disk.used / (1024 ** 3), 1),
        "disk_total_gb": round(disk.total / (1024 ** 3), 1),
        "uptime": int(uptime_seconds),
        "gpu_name": None,
        "gpu_temp": None,
        "gpu_utilization": None,
        "gpu_memory_used_mb": None,
        "gpu_memory_total_mb": None,
    }

    gpu = _get_gpu_info()
    if gpu:
        data.update(gpu)

    return data


# ── Background health poller ───────────────────────────────────────────────────

async def _health_poll_loop():
    """Poll system health every 2 seconds into the ring buffer."""
    psutil.cpu_percent(interval=0)
    await asyncio.sleep(1)

    while True:
        try:
            data = _collect_health()
            HEALTH_HISTORY.append(data)
        except Exception:
            pass
        await asyncio.sleep(2)


@app.on_event("startup")
async def startup():
    asyncio.create_task(_health_poll_loop())


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — Health
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
async def api_health():
    """Current system health snapshot."""
    data = _collect_health()
    data["nvidia_smi_raw"] = _get_nvidia_smi_full()
    return JSONResponse(data)


@app.get("/api/health/history")
async def api_health_history():
    """Last 300 data points (polled every 2s = ~10 min window)."""
    return JSONResponse(list(HEALTH_HISTORY))


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — Individual Runs
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/runs")
async def api_runs():
    """List simulation result files from the results directory (incl. sweep subdirs)."""
    runs = []
    for f in _iter_result_files():
        try:
            with open(f) as fh:
                raw = json.load(fh)

            config = raw.get("config", {})
            metrics = raw.get("metrics") or raw.get("snapshots", [])
            n_snapshots = len(metrics)

            # Determine sweep folder (if any)
            sweep_id = f.parent.name if f.parent != RESULTS_DIR else None

            runs.append({
                "id": f.stem,
                "filename": f.name,
                "sweep_id": sweep_id,
                "path": str(f.relative_to(RESULTS_DIR)),
                "config": {
                    "target_n": config.get("target_n"),
                    "mutation_rate": config.get("sim_mutation_rate") or config.get("mutation_rate"),
                    "paper_mutation_rate": config.get("paper_mutation_rate"),
                    "keep_fraction": config.get("keep_fraction"),
                    "sample_fraction": config.get("sample_fraction"),
                    "leak_fraction": config.get("leak_fraction"),
                    "incubation_time": config.get("incubation_time"),
                    "total_mini_cycles": config.get("total_mini_cycles"),
                    "L": config.get("L"),
                    "gamma": config.get("gamma"),
                },
                "timestamp": raw.get("timestamp", f.stat().st_mtime),
                "status": "completed" if n_snapshots > 0 else "empty",
                "n_snapshots": n_snapshots,
            })
        except (json.JSONDecodeError, Exception):
            runs.append({
                "id": f.stem,
                "filename": f.name,
                "sweep_id": None,
                "path": str(f.relative_to(RESULTS_DIR)),
                "config": {},
                "timestamp": f.stat().st_mtime,
                "status": "error",
                "n_snapshots": 0,
            })

    return JSONResponse(runs)


@app.get("/api/runs/{run_path:path}")
async def api_run_detail(run_path: str):
    """Full simulation results JSON for a specific run."""
    if not RESULTS_DIR.exists():
        raise HTTPException(404, "Results directory not found")

    # Support both flat (run_id.json) and sweep paths (sweep_2026-03-19/name.json)
    fpath = RESULTS_DIR / run_path
    if not fpath.suffix:
        fpath = fpath.with_suffix(".json")
    if not fpath.exists():
        raise HTTPException(404, f"Run '{run_path}' not found")

    try:
        with open(fpath) as fh:
            raw = json.load(fh)
        return JSONResponse(_normalise_run(raw))
    except json.JSONDecodeError:
        raise HTTPException(500, "Malformed JSON in run file")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — Sweep Explorer
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/sweeps")
async def api_sweeps():
    """List available sweep folders with their manifest data."""
    if not RESULTS_DIR.exists():
        return JSONResponse([])

    sweeps = []
    for subdir in sorted(RESULTS_DIR.iterdir()):
        if not subdir.is_dir() or not subdir.name.startswith("sweep"):
            continue

        manifest = {}
        manifest_path = subdir / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
            except Exception:
                pass

        n_runs = len([f for f in subdir.iterdir() if f.suffix == ".json" and f.name != "manifest.json"])

        sweeps.append({
            "id": subdir.name,
            "n_runs": n_runs,
            "manifest": manifest,
        })

    return JSONResponse(sweeps)


@app.get("/api/sweeps/{sweep_id}/summary")
async def api_sweep_summary(sweep_id: str):
    """
    Pre-computed summary of every run in a sweep.
    Returns a flat array with config + final metrics for each run,
    optimized for heatmap/ranking charts (no full time-series).
    """
    sweep_dir = RESULTS_DIR / sweep_id
    if not sweep_dir.exists() or not sweep_dir.is_dir():
        raise HTTPException(404, f"Sweep '{sweep_id}' not found")

    summaries = []
    for f in sorted(sweep_dir.iterdir()):
        if f.suffix != ".json" or f.name == "manifest.json":
            continue
        try:
            with open(f) as fh:
                raw = json.load(fh)

            config = raw.get("config", {})
            snapshots = raw.get("metrics") or raw.get("snapshots", [])
            timing = raw.get("timing", {})

            if not snapshots:
                continue

            final = snapshots[-1]
            initial = snapshots[0]

            # Pre-compute convergence: cycle at which 50% of final aff reached
            final_aff = final.get("mean_affinity", 0)
            initial_aff = initial.get("mean_affinity", 0)
            half_aff = initial_aff + (final_aff - initial_aff) * 0.5
            convergence_50 = final.get("cycle", len(snapshots))
            for s in snapshots:
                if s.get("mean_affinity", 0) >= half_aff:
                    convergence_50 = s.get("cycle", 0)
                    break

            summaries.append({
                "run_id": f.stem,
                "path": f"{sweep_id}/{f.stem}",
                # Config params for filtering
                "target_n": config.get("target_n"),
                "paper_mutation_rate": config.get("paper_mutation_rate"),
                "keep_fraction": config.get("keep_fraction"),
                "sample_fraction": config.get("sample_fraction"),
                "leak_fraction": config.get("leak_fraction"),
                "incubation_time": config.get("incubation_time"),
                "n_doublings": config.get("n_doublings"),
                # Final metrics
                "final_mean_affinity": final.get("mean_affinity", 0),
                "final_max_affinity": final.get("max_affinity", 0),
                "final_min_affinity": final.get("min_affinity", 0),
                "final_std_affinity": final.get("std_affinity", 0),
                "final_n_clones": final.get("n_unique_clones", 0),
                "final_shannon": final.get("shannon_entropy", 0),
                "final_simpson": final.get("simpson_index", 0),
                "final_top_clone_frac": final.get("top_clone_fraction", 0),
                "final_mean_hamming": final.get("mean_hamming", 0),
                "final_n_alive": final.get("n_alive", 0),
                # Initial metrics
                "initial_mean_affinity": initial.get("mean_affinity", 0),
                "initial_n_clones": initial.get("n_unique_clones", 0),
                "initial_shannon": initial.get("shannon_entropy", 0),
                "initial_mean_hamming": initial.get("mean_hamming", 0),
                # Derived
                "convergence_cycle_50": convergence_50,
                "total_cycles": final.get("cycle", len(snapshots)),
                # Timing
                "run_seconds": timing.get("run_seconds", 0),
            })
        except Exception:
            continue

    return JSONResponse(summaries)


@app.get("/api/sweeps/{sweep_id}/grouped-timeseries")
async def api_sweep_grouped_timeseries(sweep_id: str):
    """
    Grouped time-series: average metrics per mutation variant across all runs.
    Returns compact arrays suitable for Chart.js multi-line plots.
    """
    sweep_dir = RESULTS_DIR / sweep_id
    if not sweep_dir.exists() or not sweep_dir.is_dir():
        raise HTTPException(404, f"Sweep '{sweep_id}' not found")

    # Collect time-series grouped by paper_mutation_rate
    groups = {}  # rate -> list of run time-series

    for f in sorted(sweep_dir.iterdir()):
        if f.suffix != ".json" or f.name == "manifest.json":
            continue
        try:
            with open(f) as fh:
                raw = json.load(fh)
            config = raw.get("config", {})
            snapshots = raw.get("metrics") or raw.get("snapshots", [])
            if not snapshots:
                continue

            rate = config.get("paper_mutation_rate", 0)
            rate_key = f"{rate:.2e}"

            if rate_key not in groups:
                groups[rate_key] = {"rate": rate, "runs": []}

            groups[rate_key]["runs"].append({
                "cycles": [s.get("cycle", i) for i, s in enumerate(snapshots)],
                "mean_affinity": [s.get("mean_affinity", 0) for s in snapshots],
                "max_affinity": [s.get("max_affinity", 0) for s in snapshots],
                "shannon_entropy": [s.get("shannon_entropy", 0) for s in snapshots],
                "n_unique_clones": [s.get("n_unique_clones", 0) for s in snapshots],
                "top_clone_fraction": [s.get("top_clone_fraction", 0) for s in snapshots],
                "mean_hamming": [s.get("mean_hamming", 0) for s in snapshots],
            })
        except Exception:
            continue

    # Compute averages per group
    result = []
    for rate_key, group in sorted(groups.items(), key=lambda x: x[1]["rate"]):
        runs = group["runs"]
        if not runs:
            continue

        # Use the shortest run's length for alignment
        min_len = min(len(r["cycles"]) for r in runs)
        n = len(runs)

        avg = {"rate": group["rate"], "rate_key": rate_key, "n_runs": n}
        for metric in ["mean_affinity", "max_affinity", "shannon_entropy",
                        "n_unique_clones", "top_clone_fraction", "mean_hamming"]:
            means = []
            sems = []
            for i in range(min_len):
                vals = [r[metric][i] for r in runs]
                mu = sum(vals) / n
                var = sum((v - mu) ** 2 for v in vals) / max(n - 1, 1)
                means.append(mu)
                sems.append(math.sqrt(var / n))
            avg[metric] = means
            avg[f"{metric}_sem"] = sems
        avg["cycles"] = runs[0]["cycles"][:min_len]
        result.append(avg)

    return JSONResponse(result)


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — Sweep Notes
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/sweeps/{sweep_id}/notes")
async def api_sweep_notes_get(sweep_id: str):
    """Read the notes markdown for a sweep."""
    notes_path = RESULTS_DIR / sweep_id / "notes.md"
    if notes_path.exists():
        return JSONResponse({"content": notes_path.read_text(encoding="utf-8")})
    return JSONResponse({"content": ""})


@app.put("/api/sweeps/{sweep_id}/notes")
async def api_sweep_notes_put(sweep_id: str, req: Request):
    """Save notes markdown for a sweep."""
    sweep_dir = RESULTS_DIR / sweep_id
    if not sweep_dir.exists():
        raise HTTPException(404, f"Sweep '{sweep_id}' not found")
    body = await req.json()
    content = body.get("content", "")
    notes_path = sweep_dir / "notes.md"
    notes_path.write_text(content, encoding="utf-8")
    return JSONResponse({"ok": True})


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — Active Sweep Progress
# ══════════════════════════════════════════════════════════════════════════════
#
# This endpoint is polled by the frontend every 5 seconds to show live sweep
# progress in the Server Health tab.  It scans all results/sweep_*/progress.json
# files and returns whichever is most relevant:
#
#   1. If any progress.json has status "running"  → return it (live sweep)
#   2. If none running but some "completed"       → return the most recent one
#   3. If no progress.json files exist at all      → return {"status": "idle"}
#
# The progress.json files are written by sim.progress.SweepProgressTracker
# which is integrated into the sweep scripts (overnight_sweep.py,
# sweep_population_size.py).
#
# Schema: see sim/progress.py docstring for full progress.json specification.

@app.get("/api/sweeps/active")
async def api_sweeps_active():
    """Return the currently active (or most recently completed) sweep progress.

    Response possibilities:
      - ``{"status": "idle"}`` — no progress files found
      - Full progress.json content with ``status: "running"``
      - Full progress.json content with ``status: "completed"``
    """
    if not RESULTS_DIR.exists():
        return JSONResponse({"status": "idle"})

    running = None
    completed_list = []

    for subdir in RESULTS_DIR.iterdir():
        if not subdir.is_dir() or not subdir.name.startswith("sweep"):
            # Also check non-sweep dirs like "overnight_sweep"
            if not subdir.is_dir():
                continue
        progress_path = subdir / "progress.json"
        if not progress_path.exists():
            continue
        try:
            with open(progress_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        status = data.get("status", "")
        if status == "running":
            running = data
            break  # only one can be running at a time
        elif status == "completed":
            completed_list.append(data)

    if running:
        return JSONResponse(running)

    if completed_list:
        # Return the most recently started completed sweep
        completed_list.sort(
            key=lambda d: d.get("started_at", ""),
            reverse=True,
        )
        return JSONResponse(completed_list[0])

    return JSONResponse({"status": "idle"})


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — Docs
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/docs/flow")
async def api_docs_flow():
    """Raw markdown content of the flow diagram."""
    if not FLOW_DIAGRAM_PATH.exists():
        raise HTTPException(404, "Flow diagram not found")

    content = FLOW_DIAGRAM_PATH.read_text(encoding="utf-8")
    return JSONResponse({"content": content, "filename": FLOW_DIAGRAM_PATH.name})


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8050,
        reload=False,
        log_level="info",
    )
