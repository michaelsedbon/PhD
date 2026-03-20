# EXP_003 Simulation Dashboard

Real-time GPU server monitoring and simulation results viewer for the bacterial synthetic germinal centre experiment.

![Server Health Tab](docs/screenshot_health.png)

---

## Features

| Tab | What it shows |
|-----|---------------|
| **🖥️ Server Health** | GPU temp / VRAM / utilization, CPU %, RAM, disk, uptime, time-series charts (10 min window), raw `nvidia-smi` output |
| **📊 Simulation Results** | Browse completed runs, inspect per-run metrics (affinity maturation, population dynamics, diversity, clone frequencies, Hamming distance distribution with time-slider), compare two runs side-by-side |
| **📐 Architecture & Design** | Renders `flow_diagram_v2_pipeline.md` with Mermaid diagram support and syntax-highlighted code blocks |

## Tech Stack

- **Backend:** Python 3 · FastAPI · Uvicorn · psutil · nvidia-smi
- **Frontend:** Vanilla HTML / CSS / JS (no build step)
- **Charts:** Chart.js 4
- **Markdown:** Marked.js + Highlight.js + Mermaid.js

---

## Quick Start

### On the GPU server

```bash
# 1. SSH into the server
ssh michael@172.16.1.80

# 2. Navigate to the dashboard
cd ~/gc_simulation/EXP_003/dashboard

# 3. Install dependencies (first time only)
pip install -r requirements.txt

# 4. Run the server
python server.py
```

Open **http://172.16.1.80:8050** in your browser.

### Run in the background (persistent)

```bash
nohup python server.py > /tmp/exp003-dashboard.log 2>&1 &
```

To stop it:

```bash
kill $(lsof -ti :8050) 2>/dev/null
```

---

## Project Structure

```
dashboard/
├── server.py              # FastAPI backend — health polling, runs API, docs API
├── static/
│   ├── index.html         # Single-page app shell (3 tabs)
│   ├── style.css          # Synthetica dark theme (1100+ lines)
│   └── app.js             # Frontend modules: health, runs, docs (~950 lines)
├── requirements.txt       # fastapi, uvicorn[standard], psutil
└── README.md              # This file
```

## API Reference

All endpoints return JSON unless noted.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the dashboard HTML |
| `GET` | `/api/health` | Current system snapshot: CPU, RAM, disk, GPU temp/VRAM/util, raw nvidia-smi |
| `GET` | `/api/health/history` | Ring buffer of last 300 data points (~10 min at 2 s intervals) |
| `GET` | `/api/runs` | List all `*.json` files in the results directory with config summaries |
| `GET` | `/api/runs/<id>` | Full simulation results JSON for a specific run |
| `GET` | `/api/docs/flow` | Raw markdown content of the flow diagram |

### Health response example

```json
{
  "timestamp": "2026-03-19T17:00:00.123456",
  "cpu_percent": 12.3,
  "ram_used_gb": 14.2,
  "ram_total_gb": 31.3,
  "disk_used_gb": 120.5,
  "disk_total_gb": 500.0,
  "uptime": 345600,
  "gpu_name": "NVIDIA RTX 4090",
  "gpu_temp": 42,
  "gpu_utilization": 85,
  "gpu_memory_used_mb": 18200,
  "gpu_memory_total_mb": 24564,
  "nvidia_smi_raw": "..."
}
```

## Expected Server Paths

| Path | Purpose |
|------|---------|
| `~/gc_simulation/EXP_003/results/*.json` | Simulation output files (auto-discovered) |
| `~/gc_simulation/EXP_003/docs/flow_diagram_v2_pipeline.md` | Architecture diagram rendered in the Docs tab |

## Configuration

The server listens on **`0.0.0.0:8050`** by default. Edit the bottom of `server.py` to change the port:

```python
uvicorn.run("server:app", host="0.0.0.0", port=8050)
```

Health polling runs every **2 seconds** into a ring buffer of **300 entries** (~10 min window). Adjust `HEALTH_HISTORY` maxlen and the sleep interval in `_health_poll_loop()`.
