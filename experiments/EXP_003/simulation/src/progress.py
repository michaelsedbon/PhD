"""
SweepProgressTracker — Real-time progress reporting for simulation sweeps.

This module provides a reusable helper class that sweep scripts import to
report live progress.  After each completed (or failed) run, it writes/updates
a ``progress.json`` file inside the sweep's output directory.  The dashboard
API (``GET /api/sweeps/active``) reads this file to render a live progress
card in the Server Health tab.

Architecture overview
─────────────────────
                  ┌──────────────────┐
  sweep script ──►│ SweepProgressTracker │──► results/<sweep_id>/progress.json
                  └──────────────────┘
                                           │
                  ┌──────────────────┐     │  (reads)
  dashboard API ◄─│ GET /api/sweeps/active │◄─┘
                  └──────────────────┘
                           │
                  ┌──────────────────┐
  frontend JS  ◄──│ polls every 5 s  │
                  └──────────────────┘

Usage in a sweep script
───────────────────────
    from sim.progress import SweepProgressTracker

    tracker = SweepProgressTracker(
        sweep_id   = "sweep_2026-03-20",
        total_runs = 72,
        output_dir = "results/sweep_2026-03-20",
    )

    for i, (run_id, params) in enumerate(grid):
        tracker.start_run(run_id, i + 1, params)

        try:
            results = run_simulation(...)
            tracker.complete_run(
                run_id,
                duration = results["timing"]["run_seconds"],
                final_metrics = {
                    "final_affinity": final["mean_affinity"],
                    "final_shannon":  final["shannon_entropy"],
                    "target_n":       params["target_n"],
                },
            )
        except Exception as e:
            tracker.fail_run(run_id, str(e))

    tracker.finalize()

progress.json schema
────────────────────
{
    "sweep_id":      str,           # e.g. "sweep_2026-03-20"
    "status":        str,           # "running" | "completed"
    "started_at":    str,           # ISO-8601 timestamp
    "finished_at":   str | null,    # ISO-8601 timestamp (set by finalize)
    "total_runs":    int,
    "completed":     int,
    "failed":        int,
    "current_run": {                # null when idle / completed
        "id":        str,
        "index":     int,
        "params":    dict
    },
    "eta_minutes":   float | null,  # estimated minutes remaining
    "runs_completed": [             # last 20 completed runs (ring)
        {
            "id":               str,
            "duration_seconds": float,
            "final_affinity":   float,
            "final_shannon":    float,
            "target_n":         int
        }
    ],
    "timing": {
        "mean_per_run": float,
        "fastest":      float,
        "slowest":      float
    }
}

Notes
─────
- Writes are **atomic**: data is written to a ``.tmp`` file first and then
  renamed, so the dashboard API never reads a half-written file.
- ``runs_completed`` is capped at the **last 20 entries** to keep the JSON
  small and avoid growing unboundedly during long sweeps.
- The class is intentionally stateless across restarts — it reads the existing
  ``progress.json`` on ``__init__`` if one exists, so a sweep can resume after
  a crash without losing progress metadata.
- All metrics in ``complete_run`` are optional via ``final_metrics`` dict —
  the class stores whatever keys are provided.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Maximum number of completed-run entries kept in progress.json.
# Older entries are dropped (FIFO) to keep the file small.
MAX_COMPLETED_RING = 20


class SweepProgressTracker:
    """Track and persist live progress for a simulation sweep.

    Parameters
    ----------
    sweep_id : str
        Unique identifier for the sweep (e.g. ``"sweep_2026-03-20"``).
        Used as a display label in the dashboard.
    total_runs : int
        Total number of simulation runs in the sweep grid.
    output_dir : str | Path
        Directory where the sweep's result JSON files are written.
        ``progress.json`` will be created/updated here.

    Attributes
    ----------
    progress_path : Path
        Absolute path to the ``progress.json`` file being managed.
    data : dict
        In-memory copy of the progress state.  Written to disk after
        every mutation (start / complete / fail / finalize).
    """

    def __init__(self, sweep_id: str, total_runs: int, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.progress_path = self.output_dir / "progress.json"

        # Track durations in-memory for timing stats (not persisted directly)
        self._durations: List[float] = []

        # If a progress file already exists (e.g. resumed sweep), load it
        if self.progress_path.exists():
            try:
                with open(self.progress_path) as f:
                    self.data = json.load(f)
                # Rebuild in-memory durations from existing completed runs
                for r in self.data.get("runs_completed", []):
                    if "duration_seconds" in r:
                        self._durations.append(r["duration_seconds"])
                return
            except (json.JSONDecodeError, KeyError):
                pass  # Corrupt file — start fresh

        # Fresh progress state
        self.data: Dict[str, Any] = {
            "sweep_id": sweep_id,
            "status": "running",
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "finished_at": None,
            "total_runs": total_runs,
            "completed": 0,
            "failed": 0,
            "current_run": None,
            "eta_minutes": None,
            "runs_completed": [],
            "timing": {
                "mean_per_run": 0,
                "fastest": 0,
                "slowest": 0,
            },
        }
        self._write()

    # ── Public API ─────────────────────────────────────────────────────────

    def start_run(self, run_id: str, run_index: int, params: dict) -> None:
        """Signal that a new simulation run is starting.

        Parameters
        ----------
        run_id : str
            Unique identifier for this run (e.g. ``"N500000_mu-triple_k0.1"``).
        run_index : int
            1-based index of this run within the sweep grid.
        params : dict
            Parameter dict for this run — stored verbatim in ``current_run``.
        """
        self.data["current_run"] = {
            "id": run_id,
            "index": run_index,
            "params": params,
        }
        self._write()

    def complete_run(
        self,
        run_id: str,
        duration: float,
        final_metrics: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a successfully completed simulation run.

        Parameters
        ----------
        run_id : str
            Must match the ``run_id`` passed to ``start_run``.
        duration : float
            Wall-clock time in seconds for this run.
        final_metrics : dict, optional
            Arbitrary dict of final-timepoint metrics to store.
            Common keys: ``final_affinity``, ``final_shannon``, ``target_n``.
            All keys are stored as-is in the ``runs_completed`` ring.
        """
        self.data["completed"] += 1

        # Append to ring buffer (capped at MAX_COMPLETED_RING)
        entry: Dict[str, Any] = {
            "id": run_id,
            "duration_seconds": round(duration, 2),
        }
        if final_metrics:
            entry.update(final_metrics)

        self.data["runs_completed"].append(entry)
        if len(self.data["runs_completed"]) > MAX_COMPLETED_RING:
            self.data["runs_completed"] = self.data["runs_completed"][-MAX_COMPLETED_RING:]

        # Update timing statistics
        self._durations.append(duration)
        self.data["timing"] = {
            "mean_per_run": round(sum(self._durations) / len(self._durations), 2),
            "fastest": round(min(self._durations), 2),
            "slowest": round(max(self._durations), 2),
        }

        # Estimate remaining time
        remaining = self.data["total_runs"] - self.data["completed"] - self.data["failed"]
        if remaining > 0 and self._durations:
            mean_s = sum(self._durations) / len(self._durations)
            self.data["eta_minutes"] = round((remaining * mean_s) / 60, 1)
        else:
            self.data["eta_minutes"] = 0

        self._write()

    def fail_run(self, run_id: str, error_message: str = "") -> None:
        """Record a failed simulation run.

        Parameters
        ----------
        run_id : str
            Must match the ``run_id`` passed to ``start_run``.
        error_message : str
            Human-readable error description (truncated to 200 chars).
        """
        self.data["failed"] += 1

        # Also add to runs_completed ring for visibility
        entry = {
            "id": run_id,
            "duration_seconds": 0,
            "error": error_message[:200],
        }
        self.data["runs_completed"].append(entry)
        if len(self.data["runs_completed"]) > MAX_COMPLETED_RING:
            self.data["runs_completed"] = self.data["runs_completed"][-MAX_COMPLETED_RING:]

        # Update ETA (remaining runs decreased)
        remaining = self.data["total_runs"] - self.data["completed"] - self.data["failed"]
        if remaining > 0 and self._durations:
            mean_s = sum(self._durations) / len(self._durations)
            self.data["eta_minutes"] = round((remaining * mean_s) / 60, 1)
        else:
            self.data["eta_minutes"] = 0

        self._write()

    def finalize(self) -> None:
        """Mark the sweep as completed.

        Sets ``status`` to ``"completed"``, records ``finished_at``,
        clears ``current_run``, and sets ETA to 0.
        """
        self.data["status"] = "completed"
        self.data["finished_at"] = datetime.now().isoformat(timespec="seconds")
        self.data["current_run"] = None
        self.data["eta_minutes"] = 0
        self._write()

    # ── Internal ───────────────────────────────────────────────────────────

    def _write(self) -> None:
        """Atomically write progress.json (write-to-tmp + rename).

        This prevents the dashboard API from reading a half-written file.
        """
        tmp_path = self.progress_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(self.data, f, indent=2, default=str)
        os.replace(tmp_path, self.progress_path)
