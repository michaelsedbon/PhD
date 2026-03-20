# EXP_003 Dashboard — Agent Handoff Prompt

> **Copy this entire file as a prompt to another agent** so it can populate the dashboard with simulation results.

---

## Your Task

You are working on the EXP_003 simulation — a GPU-accelerated bacterial synthetic germinal center simulation written in JAX. The simulation code lives on a remote GPU server at `michael@172.16.1.80` under `~/gc_simulation/EXP_003/`.

A monitoring dashboard is already built and running at **http://172.16.1.80:8050**. The dashboard has three tabs:

1. **Server Health** — real-time GPU/CPU/RAM monitoring (already working)
2. **Simulation Results** — browse & visualize completed runs (needs data)
3. **Architecture & Design** — renders the flow diagram markdown (already working)

**Your job**: Make the simulation write results in the exact JSON format the dashboard expects, so the "Simulation Results" tab populates with charts.

---

## Server Access

- **Host:** `172.16.1.80`
- **User:** `michael`
- **SSH:** Key-based auth (ed25519) — no password needed
- **Python venv:** `~/gc_simulation/EXP_003/.venv/` (has JAX, FastAPI, psutil installed)
- **GPU:** NVIDIA RTX 2080 Ti (11 GB VRAM), CUDA 13.1

```bash
ssh michael@172.16.1.80
source ~/gc_simulation/EXP_003/.venv/bin/activate
```

---

## Directory Structure on Server

```
~/gc_simulation/EXP_003/
├── sim/                    # Simulation code (Python/JAX) — MAY NOT EXIST YET
│   ├── config.py           # Config dataclass
│   ├── state.py            # GCState dataclass
│   ├── grow.py             # DZ growth + mutation
│   ├── select.py           # Competitive LZ selection
│   ├── pipeline.py         # run_one_mini_cycle()
│   ├── run.py              # run_simulation() — outer loop + snapshots
│   ├── metrics.py          # collect_snapshot()
│   └── ...
│
├── results/                # ← OUTPUT DIR: put JSON files here
│   └── *.json              # One file per simulation run
│
├── docs/                   # Reference documents
│   ├── flow_diagram_v2_pipeline.md   # Full architecture (900+ lines)
│   ├── PARAMETER_BIOLOGY_REFERENCE.md
│   └── ...
│
├── dashboard/              # Dashboard app (already deployed, don't modify)
│   ├── server.py           # FastAPI backend on port 8050
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js          # Chart.js visualizations
│   └── requirements.txt
│
└── .venv/                  # Python virtualenv
```

---

## Required JSON Output Format

Each simulation run must write a **single JSON file** to `~/gc_simulation/EXP_003/results/`. The filename becomes the run ID (e.g., `run_001.json` → ID = `run_001`).

### Top-level structure

```json
{
  "timestamp": "2026-03-20T10:15:30.123456",
  "config": {
    "target_n": 10000,
    "mutation_rate": 1e-5,
    "keep_fraction": 0.1,
    "sample_fraction": 0.3,
    "total_mini_cycles": 560,
    "L": 40,
    "gamma": 10.5
  },
  "metrics": [
    { ... snapshot at cycle 0 ... },
    { ... snapshot at cycle 10 ... },
    { ... snapshot at cycle 20 ... }
  ]
}
```

### Config fields (used in run list display)

| Field | Type | Description |
|-------|------|-------------|
| `target_n` | int | Chemostat steady-state population |
| `mutation_rate` | float | Per-position per-division rate |
| `keep_fraction` | float | Fraction of LZ kept after selection (0.1–0.3) |
| `sample_fraction` | float | Fraction of DZ sampled to LZ (0.3–0.5) |
| `total_mini_cycles` | int | Total experiment length |
| `L` | int | Shape space dimensions (40) |
| `gamma` | float | Affinity Gaussian width (10.5) |

### Metrics array — each snapshot object

Each entry in the `metrics` array is a snapshot collected every N cycles. **All of these fields are read by the frontend charts:**

```json
{
  "mean_affinity": 0.42,
  "max_affinity": 0.95,
  "min_affinity": 0.01,

  "n_alive": 10000,
  "n_in_dz": 7000,
  "n_in_lz": 3000,
  "n_in_buffer": 0,

  "shannon_entropy": 3.2,
  "simpson_index": 0.05,

  "n_unique_clones": 45,

  "clone_size_distribution": [0.25, 0.15, 0.12, 0.08, ...],

  "hamming_histogram": [0, 0, 5, 12, 45, 120, 300, ...]
}
```

### Field-to-chart mapping

| JSON field | Chart | Type |
|------------|-------|------|
| `mean_affinity`, `max_affinity`, `min_affinity` | Affinity Maturation (line, 3 series) | time-series |
| `n_alive`, `n_in_dz`, `n_in_lz`, `n_in_buffer` | Population Dynamics (line, 4 series) | time-series |
| `shannon_entropy` | Shannon Entropy (line, left Y-axis) | time-series |
| `simpson_index` | Simpson Index (line, right Y-axis) | time-series |
| `n_unique_clones` | Unique Clones (area chart) | time-series |
| `clone_size_distribution` | Top 20 Clone Frequencies (bar chart) | final snapshot only |
| `hamming_histogram` | Hamming Distance Distribution (bar + slider) | per-snapshot |

> **The `clone_size_distribution` should be a descending-sorted list of clone fractions** (sum to 1.0). Only the last snapshot's distribution is used for the bar chart, but ALL snapshots' `hamming_histogram` are accessible via the time slider.

---

## Simulation Architecture Summary

The simulation models a bacterial synthetic germinal center with a **pipeline model**:

1. **SAMPLE**: Random fraction of DZ cells → LZ (first cycle only, then auto-fed from buffer)
2. **GROW DZ**: DZ cells divide + mutate (T7 replisome, replication-coupled) during LZ incubation
3. **SELECT LZ**: Competitive top-fraction selection + leak (imperfect bead washout)
4. **BUFFER**: Extract DZ overflow before returning LZ survivors
5. **RETURN**: LZ survivors → DZ (div_counter reset)
6. **BALANCE**: Buffer → next LZ batch, sacrifice excess to maintain constant population

Full architecture details are in `~/gc_simulation/EXP_003/docs/flow_diagram_v2_pipeline.md`.

### Key parameters

```python
Config(
    target_n       = 10_000,      # steady-state pop (start small for dev)
    L              = 40,           # shape space dimensions
    mutation_rate  = 1e-5,         # per position per division (T7 V3 rate)
    gamma          = 10.5,         # affinity Gaussian width
    eta            = 2.0,          # affinity exponent
    doubling_time  = 30,           # minutes
    incubation_time= 60,           # minutes (→ 2 doublings)
    sample_fraction= 0.3,          # DZ → LZ fraction
    keep_fraction  = 0.1,          # LZ survival fraction
    leak_fraction  = 0.001,        # imperfect washout survival
    n_founders     = 50,           # initial library size
    total_mini_cycles = 100,       # start with 100 for testing
    alphabet_size  = 4,            # ACGT
)
```

### Affinity function

```python
affinity = exp(-(hamming_distance / gamma) ** eta)
```

### collect_snapshot() should compute

```python
def collect_snapshot(state):
    alive_mask = state.alive
    alive_aff = state.affinities[alive_mask]
    alive_ham = state.hamming[alive_mask]
    alive_clones = state.clone_id[alive_mask]

    # Clone frequencies
    unique_clones, counts = jnp.unique(alive_clones, return_counts=True)
    freqs = counts / counts.sum()
    sorted_freqs = jnp.sort(freqs)[::-1]  # descending

    return {
        "mean_affinity": float(alive_aff.mean()),
        "max_affinity": float(alive_aff.max()),
        "min_affinity": float(alive_aff.min()),
        "n_alive": int(alive_mask.sum()),
        "n_in_dz": int((alive_mask & ~state.in_lz & ~state.in_buffer).sum()),
        "n_in_lz": int((alive_mask & state.in_lz).sum()),
        "n_in_buffer": int((alive_mask & state.in_buffer).sum()),
        "shannon_entropy": float(-jnp.sum(freqs * jnp.log(freqs + 1e-12))),
        "simpson_index": float(jnp.sum(freqs ** 2)),
        "n_unique_clones": int(len(unique_clones)),
        "clone_size_distribution": sorted_freqs.tolist(),
        "hamming_histogram": jnp.bincount(alive_ham, length=state.L + 1).tolist(),
    }
```

---

## How to Verify

After a simulation writes `results/run_001.json`, visit **http://172.16.1.80:8050**, click the "Simulation Results" tab, and confirm:

1. The run appears in the list with config metadata
2. Clicking the run shows all 7 charts populated
3. The Hamming distance slider scrubs through timepoints
4. The comparison feature works (select two runs → overlay affinity curves)

---

## Dashboard Tech Stack (for reference, don't modify)

- **Backend:** FastAPI + psutil + nvidia-smi (Python, port 8050)
- **Frontend:** Vanilla HTML/CSS/JS, Chart.js 4, Lucide icons
- **API:** `/api/runs` (list), `/api/runs/<id>` (detail JSON)
- **Theme:** Dark (Synthetica), Inter font, accent color `#818cf8`

---

## Quick Test: Generate Synthetic Data

To test the dashboard immediately before the real simulation is ready, create a synthetic run:

```python
import json, math, random
from datetime import datetime

config = {
    "target_n": 10000, "mutation_rate": 1e-5, "keep_fraction": 0.1,
    "sample_fraction": 0.3, "total_mini_cycles": 100, "L": 40, "gamma": 10.5
}

metrics = []
for cycle in range(0, 100, 5):  # snapshot every 5 cycles
    t = cycle / 100
    metrics.append({
        "mean_affinity": 0.05 + 0.6 * t + random.gauss(0, 0.02),
        "max_affinity": min(1.0, 0.2 + 0.75 * t + random.gauss(0, 0.03)),
        "min_affinity": max(0.0, 0.01 + 0.1 * t + random.gauss(0, 0.01)),
        "n_alive": 10000 + random.randint(-200, 200),
        "n_in_dz": 7000 + random.randint(-100, 100),
        "n_in_lz": 3000 + random.randint(-100, 100),
        "n_in_buffer": random.randint(0, 50),
        "shannon_entropy": max(0, 3.9 - 2.5 * t + random.gauss(0, 0.1)),
        "simpson_index": min(1, 0.02 + 0.4 * t ** 2 + random.gauss(0, 0.01)),
        "n_unique_clones": max(1, int(50 - 40 * t + random.gauss(0, 2))),
        "clone_size_distribution": sorted(
            [random.random() for _ in range(max(1, int(50 - 40 * t)))],
            reverse=True
        ),
        "hamming_histogram": [
            max(0, int(1000 * math.exp(-((d - (20 - 8 * t)) ** 2) / (2 * (3 + t) ** 2))))
            for d in range(41)
        ],
    })
    # Normalize clone frequencies
    total = sum(metrics[-1]["clone_size_distribution"])
    metrics[-1]["clone_size_distribution"] = [
        round(f / total, 6) for f in metrics[-1]["clone_size_distribution"]
    ]

result = {"timestamp": datetime.now().isoformat(), "config": config, "metrics": metrics}

with open("results/synthetic_test_001.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"Wrote {len(metrics)} snapshots to results/synthetic_test_001.json")
```

Run this on the server:
```bash
ssh michael@172.16.1.80
cd ~/gc_simulation/EXP_003
mkdir -p results
source .venv/bin/activate
python -c '<paste the script above>'
```

Then refresh the dashboard and click "Simulation Results" — you should see the run appear.
