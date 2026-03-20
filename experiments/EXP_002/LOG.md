# EXP_002 — Experiment Log

Chronological record of all actions, changes, and observations.

---

## 2026-03-16 — Experiment Created

- Initialised experiment folder from template.
- Goal: GPU-ready simulation of the synthetic germinal center (reproduce hyphasma paper, then adapt to bacterial system).
- Read Robert et al. paper, extracted 9 core algorithms.
- Read Maimonide 2026 proposal, identified bacterial adaptation requirements.
- Created brainstorming document covering architecture (JAX, SoA, particle-based).
- Created shape space explainer (L=4, Hamming distance, Gaussian affinity).
- Created selection model analysis (4 models: Hill, threshold, top-K, bead-binding).
- Created Flow Diagram A (natural GC, 11 blocks, paper algorithms 1-9).
- Created Flow Diagram B (bacterial GC, 7 blocks + 2 stubs).
- Confirmed GPU: RTX 2080 Ti (11 GB VRAM) — sufficient for both modes.
- Created implementation plan for Phase 0.
- Created master handoff checklist (Phases 0-4).

## 2026-03-16 — Phase 0 Implementation

- Implemented all 11 modules for Phase 0 (paper reproduction):
  - `config.py` — 98 lines, all paper parameters (Tables 1-2)
  - `affinity.py` — 200 lines, shape space, Hamming, Gaussian, mutation, batch ops
  - `state.py` — 200 lines, NamedTuple SoA for all 6 agent types
  - `chemotaxis.py` — 140 lines, 3D diffusion, production, receptor sensitivity
  - `movement.py` — 180 lines, persistent random walk, 26-neighborhood, exclusion
  - `cell_cycle.py` — 180 lines, G1→S→G2→M, division+mutation, CB→CC transition
  - `selection.py` — 190 lines, FDC antigen capture, T cell help, apoptosis
  - `differentiation.py` — 210 lines, recycling (Hill div count), output, inflow
  - `initialization.py` — 190 lines, spherical grid, FDC/stromal/TC/founder placement
  - `simulation.py` — 200 lines, main loop orchestrating all 11 blocks
  - `analysis.py` — 220 lines, Snapshot dataclass, 4 plot functions
- Wrote 15 unit tests for affinity module — all passing
- Smoke test: GC initialization produces correct grid (80³, 267K sphere points),
  100 founders at mean affinity 0.13, 20 FDCs, 100 T cells
- **Next**: Jupyter notebook with checkpoints, validation against paper

## 2026-03-16 — Pipeline Bugs Fixed + Checkpoints Validated

- Fixed 4 bugs in the simulation pipeline:
  1. `movement.py`: replaced `jax.lax.scan` with numpy Python loop (dynamic array sizes)
  2. `differentiation.py`: `apply_inflow` now places founders at valid DZ positions
  3. `selection.py`: `apply_apoptosis` grid shape corruption from `jnp.where` broadcasting
  4. `chemotaxis.py`: added diffusion sub-stepping (`α > 1/6` → auto split into stable sub-steps)
- All 6 checkpoints pass:
  - CP0: Initialization (100 CB, 100 TC, 20 FDC, 267K sphere points)
  - CP1: Affinity (Hamming, Gaussian, mutation)
  - CP2: Chemokines (CXCL12 DZ>LZ ✓, CXCL13 LZ>DZ ✓)
  - CP3: Movement (100/100 cells moved, all inside sphere)
  - CP4: Cell cycle (100 divisions observed, CB 100→200)
  - CP5: Full pipeline (20 steps in 17.3s, grid stable 80³)
- Created `notebooks/01_block_checkpoints.py` (converted to .ipynb via jupytext)
- Performance: ~0.9s/step at dt=0.05 on MacBook CPU
  - Full 21-day sim at dt=0.002 → ~80h (needs GPU server)
  - Full 7-day sim at dt=0.05 → ~1h (MacBook, fast preview)

## 2026-03-16 — GPU Server Deployment

- Deployed simulation to GPU server `michael@172.16.1.80`
- Server: RTX 2080 Ti (11 GB VRAM), CUDA 13.1, Ubuntu
- Setup: Python venv at `~/gc_simulation/.venv/`, JAX 0.9.1 with CUDA 12
- Benchmarked CPU + GPU backends — GPU slower (3.6s/step) due to Python-loop bottleneck
- Documented credentials in `projects/synthetic_germinal_center/knowledge/software.md`
- Installed ipykernel for VS Code remote Jupyter notebooks (kernel: `gc_sim`)

## 2026-03-16 — GPU Architecture Rewrite (Phase 0.75)

- Rewrote all 7 core modules for GPU-native architecture:
  - `state.py` — padded fixed-size arrays (MAX_CB=10K), `allocate_slots()` via argsort
  - `movement.py` — `jax.vmap` parallel targets + scatter conflict resolution (no Python loop)
  - `cell_cycle.py` — daughters fill free slots, no array concatenation
  - `selection.py` — vectorized flat-scatter for grid clearing
  - `differentiation.py` — slot-based recycling and inflow
  - `initialization.py` — fill first N slots of padded arrays
  - `simulation.py` — orchestrates all blocks with new APIs
- **Result: 22x speedup** (3600→163 ms/step on GPU, 1600→80 ms/step on CPU)
- Fixed movement scatter bug: cell-size (10K) vs grid-flat (512K) broadcast mismatch
- Launched 21-day paper reproduction on GPU server (PID 585664, ETA ~12h)

## 2026-03-16 — T Cell Rescue Bug Fix + Parameter Tuning

- **Found critical bug**: T cell rescue was mathematically impossible
  - `tc_rescue_time=2.0h` but `tc_time=0.5h` — cells need 2h of signal in 0.5h window
  - Signal accumulated at `rate × dt = 0.05/step`, max 0.5 in 10 steps — needs 2.0
  - **All centrocytes died to apoptosis** → GC collapsed at day 3-4, zero output cells
- **Fix**: Signal rate now scaled by `tc_rescue_time / (tc_time × 0.5)` so top cells reach rescue threshold within time window
- Tested 3 GPU optimization approaches for sync elimination:
  - Original (Python for-loops): **163ms/step** ← fastest
  - Zero-sync (vmap over fixed MAX=500): 275ms/step — wasted GPU compute
  - Hybrid (early-exit sync + vectorized scatter): 202ms/step
  - Conclusion: Python for-loops over small n (1-10) are cheaper than unconditional GPU compute

### Parameter Sweep (Manual)

Reviewed all config values against Robert et al. paper and experimental literature:

| Parameter | Original | Tuned v2 | Tuned v3 | Source |
|---|---|---|---|---|
| `founder_divisions` | 6 (27h DZ) | 2 (9h DZ) | 4 (18h DZ) | Victora 2010: 4-8h/visit |
| `n_div_max` | 6 | 1 | 2 | Recycled cells need ≥2 for sustainability |
| `tc_time` | 0.5h | 1.0h | 1.0h | More time for T cell search |
| `collect_fdc_period` | 0.7h | 1.0h | 1.0h | Longer antigen collection |
| `prob_output` | 0.05 | 0.03 | 0.03 | Stronger recycling |
| `lethal_fraction` | 0.3 | removed | removed | Dead code — paper uses shape space |

### Natural GC Validation Runs

| Run | Days | founder_div | n_div_max | Peak GC | Lifespan | DZ/LZ | Affinity |
|---|---|---|---|---|---|---|---|
| v1 (original) | 7 | 6 | 6 | 7500 | Dies day 3.5 | — | No maturation (all CC die) |
| v2 (tuned) | 21 | 2 | 1 | 750 | Dies day 4 | 2:1 ✅ | 0.13→0.30 ✅ |
| v3 (4 div, 2 recycle) | 7 | 4 | 2 | **3500** | Dies day 4 | 2:1 ✅ | 0.13→0.60 ✅ |

- **v1**: TC rescue bug → 100% CC apoptosis → no recycling → GC collapse
- **v2**: TC fix working (DZ/LZ=2:1, affinity maturation ✅), but GC too small (750 vs 3000)
- **v3**: Larger GC (peak 3500), better affinity (mean 0.60, max 0.88), 74 output cells (3× v2), but still collapses at day 4

### Mutation Rate — From Maimonide Proposal

Checked `Grant_application/Maimonide_2026/gdrive_txt/MOST_Maimonide_v3.txt`:
- **WP1 (DZ nanobody hypermutation)**: Error-prone T7 replisome. 5 polymerase variants spanning **10⁻⁸ to 10⁻⁵ sub/base/replication**
  - At peak rate on 360 bp nanobody gene: **~1 mutation per lineage every 10h**
  - This is ~2.8×10⁻⁶ per bp per generation (at 20 min doubling)
  - Much lower than current sim (0.05/pos/div) but much higher than baseline T7 (10⁻⁸)
- **WP2 (phage RBD mutagenesis)**: MP6 plasmid = **2.3 substitutions per kb per generation** (322,000× above baseline)
  - MP6 is used for PHAGE ONLY, not for the nanobody (T7 handles that)
  - This is ~2.3×10⁻³ per bp per generation
- **Key insight**: T7 and MP6 serve different purposes. For the bacterial sim (WP1), the relevant rate is **T7 at 10⁻⁵ per bp per replication**

## 2026-03-16 — Phase 1: Bacterial Synthetic GC

### v1: Initial Implementation

Created 7 modules in `src/bacterial_gc/`:
- `config.py` — experiment knobs (growth mode, 4 selection models, mutation rate, etc.)
- `state.py` — simple NamedTuple, no grid, dynamic sizing
- `growth.py` — batch + turbidostat modes
- `migration.py` — DZ↔LZ robotic transfers
- `selection.py` — 4 models (Hill, threshold, top-K, bead binding)
- `simulation.py` — cycle loop with compaction
- `analysis.py` — snapshots + 4-panel plots

**v1 Result** (batch, random 10% transfer, Hill selection):
- Affinity: 0.130 → 0.153 over 20 cycles — **too slow**
- Root cause: only 10% transferred to selection, 90% stay unselected in DZ → dilution effect

### v2: Redesigned to Match Experimental Protocol

Rewrote `growth.py` and `simulation.py` to match actual turbidostat protocol:
- **Turbidostat growth**: divide + dilute every 30 min, per-cell division counters
- **Division-triggered migration**: cells auto-migrate to LZ after N divisions (not random %)
- **Selective recycling**: only selected cells return to DZ (DZ emptied each cycle)
- `unselected_return_fraction`: tuneable — optionally return some unselected for diversity

**v2 Result** (turbidostat, 6-div trigger, Hill n=3 K=0.3, N=10K):
- Affinity: 0.13 → **0.53** over 20 cycles (4× improvement vs v1)
- Max affinity: **1.0** by cycle 3
- Population: 1000 → 6500 (stable)
- Diversity: 6.9 → 3.4 (healthy decline, no single-clone dominance)
- Top clone: 16% (breadth maintained)
- Runtime: 65s on CPU for 20 cycles

### Shape Space Scaling (L=4 → L=400)

L scaling benchmark at N=10K on server CPU:

| L | Affinity time | Mutation time | Memory |
|---|---|---|---|
| 4 | 0.38ms | 2.54ms | 0.2 MB |
| 20 | 0.70ms | 1.81ms | 0.8 MB |
| 200 | 0.88ms | 1.96ms | 8.0 MB |
| 400 | 3.87ms | 2.12ms | 16.0 MB |

**L=400 (matching 360bp nanobody gene) is computationally feasible.**

Key insight: `mutation_rate` is per-position, so must scale with L to maintain same mutations/gene/generation:
- L=4: rate=0.05 → 0.2 mut/gene/gen
- L=400: rate=0.0005 → 0.18 mut/gene/gen ≈ **T7 peak rate** (~1×10⁻⁴ per bp per gen)

**L=400 + T7 rate result** (Γ=105, H_init=50-100, 20 cycles):
- Population: stable at ~8600 ✅
- Mean affinity: 0.58→0.60 (peak cycle 6), slight decline to 0.58
- Max affinity: 0.80
- Diversity: 3.9→3.0, 36/50 unique clones remain
- Top clone: 10% — no single-clone dominance ✅
- Evolution slow but stable — matches proposal expectation of ~1 mut/10h

## 2026-03-16 — N=10K 140-Cycle Run (7 Days)

**Parameters**: L=400, mutation_rate=0.0005, Γ=105, `unselected_return=0.0`, Hill K=0.3, n=3

**Result**: Population 8800→5000 (decline). **Diversity collapsed to 0 by cycle 100** — single clone takeover. Affinity 0.60→0.30 (degradation, not maturation).

**Diagnosis**: N=10K too small for meaningful evolution. Purifying selection without adaptive evolution.

## 2026-03-16 — GPU Rewrite + Testing

Created 4 GPU modules: `state_gpu.py`, `growth_gpu.py`, `selection_gpu.py`, `simulation_gpu.py`.

**GPU testing results (RTX 2080 Ti, 11 GB VRAM)**:

| Approach | N | Speed | VRAM | Result |
|---|---|---|---|---|
| Pure CPU | 10K | 3s/cycle | 0 | ✅ working |
| Pure CPU | 1M | **45s/cycle** | 0 | ✅ **fastest** |
| GPU CUDA | 100K | 6.1s/cycle | ~2 GB | ✅ fits |
| GPU CUDA | 1M | OOM | 9.6 GB | ❌ doesn't fit |
| Hybrid CPU/GPU | 1M | 50s/cycle | 320 MB chunks | ✅ but slower |

**Conclusion**: Pure CPU is optimal for N=1M at L=400 on 2080 Ti. Transfer overhead for Hamming-distance affinity exceeds GPU compute benefit.

## 2026-03-17 — N=1M 140-Cycle Run (COMPLETE)

**Parameters**: L=400, N=1M, mutation_rate=0.0005, Γ=105, `unselected_return=0.1`, Hill K=0.3, n=3

**Run time**: 108 minutes (45s/cycle), 64% RAM (20 GB)

Final results:
- Population: 875K → **524K** (declining — not sustaining)
- Mean affinity: 0.58 → **0.29** (degradation, NOT maturation)
- Max affinity: 0.80 → **0.42** (best clone also degrades)
- Diversity: 5.63 → **0.96** (declining but never 0)
- Top clone: 2% → **80%** (dominant clone takeover by cycle 140)

> **KEY FINDING**: No affinity maturation even at N=1M. Mutation load (Muller's ratchet) overwhelms selection at T7 rate.

## 2026-03-17 — Parameter Sweep (L=400, N=10K, 140cyc)

- Ran 4×4 grid: `mutation_rate` [0.0001, 0.0003, 0.0005, 0.001] × `hill_k` [0.05, 0.1, 0.2, 0.3]
- **1 MATURATION** (mut=0.0001, K=0.3), 1 STABLE, 14 DEGRADATION
- Selection survival ~100% everywhere — Hill selection is essentially passive
- Stronger selection (lower K) = WORSE outcomes (counter-intuitive)
- See `results/sweep/SWEEP_ANALYSIS.md` for full analysis with heatmaps

## 2026-03-17 — Mutation Rate Calibration

- Discovered sweep mutation rates were **10-100× above** actual T7 variant range
- T7 variants span 10⁻⁸ to 10⁻⁵ sub/base/rep; our sweep used 10⁻⁴ to 10⁻³
- Only maturation point (0.0001) corresponds to highest-error T7 variant (V5)
- Real T7 rates should show maturation across the board
- Corrected sweep planned with rates [10⁻⁸, 10⁻⁷, 10⁻⁶, 10⁻⁵, 10⁻⁴]

## 2026-03-17 — L-Scaling Analysis

- L=400 → L=40: mutation_rate ×10, gamma ÷10, hamming ÷10
- Keeps mutations/gene/division constant
- N=10⁷ fits on GPU at L=40 (1.6 GB vs 16 GB at L=400)
- L=40 GPU validation sweep running on server

## 2026-03-17 — Simulation Validation Controls

5 controls, all passing:
1. **Zero mutation**: aff +0.11 (pure selection works) ✅
2. **No selection (K=0.001)**: pop stable at 10K ✅
3. **DE + no mutation**: single best clone at 0.80 ✅
4. **Low mut (10⁻⁵) + selection**: aff +0.09 maturation ✅
5. **Lethal selection (K=10)**: pop collapses to 2-5 cells ✅

See `results/controls/CONTROLS.md`.

## 2026-03-17 — Directed Evolution Baseline

- Added `apply_directed_evolution` to `selection_gpu.py` (top-K selection)
- Wired into `simulation_gpu.py` via `selection_mode` parameter
- `sweep.py` updated to run both GC and DE modes
- DE maps `hill_k` to equivalent `keep_fraction` (0.05→1%, 0.1→5%, 0.2→10%, 0.3→20%)

## 2026-03-17 — Scientific Questions Updated

- Q3 (DZ/LZ cycling): flagged as high-priority, connection to Muller's ratchet
- Q11 (initial affinity): added — does starting library quality affect maturation dynamics?

## 2026-03-17 — L=40 GPU Validation Sweep COMPLETE

- 16/16 runs complete, total runtime ~4h (CPU, shared with other jobs)
- Results: 0 MATURATION, 1 STABLE, 15 DEGRADATION
- L=400 equivalent: 1 MATURATION, 1 STABLE, 14 DEGRADATION
- **Scaling validated**: same qualitative pattern (mutation rate dominant, weak selection wins)
- Maturation boundary shifted from +0.03 (L=400) to -0.02 (L=40) — within stochastic variation
- Comprehensive comparison: `results/SWEEP_COMPARISON.md`
- Next: corrected sweep with actual T7 rates, then GPU scaling to N=10⁷

## 2026-03-17 — T7 Corrected Sweep COMPLETE

- 24/24 runs done: 6 rates (WT E. coli + T7 V1-V5) × 4 hill_k
- **17 MATURATION, 2 STABLE, 5 DEGRADATION**
- Sharp boundary at T7 V4 (10⁻⁵/bp/div):
  - V3 and below → maturation at ALL selection strengths
  - V4 → depends on selection (weak K≥0.2 rescues maturation)
  - V5 → degradation (except borderline STABLE at K=0.3)
- T7 V2 (10⁻⁷) is the sweet spot: best overall maturation (+0.21)
- Full analysis: `results/sweep_T7_rates/T7_RATES_ANALYSIS.md`
- Generated 20-slide lab meeting presentation: `presentation/GC_Simulation_Lab_Meeting.pptx`

## 2026-03-18 — Overnight Runs COMPLETE (84 runs, 6.3h)

### Experiment 1: Multi-seed V4 boundary (40 runs)
- V4 boundary is SHARP: K=0.3 → 10/10 maturation, K=0.2 → 9/10, K=0.1 → 0/10, K=0.05 → 0/10
- Low variance (±0.03) — outcomes are deterministic, not stochastic

### Experiment 2: GC vs Directed Evolution (36 runs)
- **GC wins at V1-V4 rates** (2-3× better maturation vs DE)
- **DE wins at V5** (highest mutation rate) — aggressive top-K selection purges mutations faster
- DE shows ZERO maturation at low rates (WT, V1, V2) due to pop bottleneck
- Crossover at V4-V5 boundary

### Experiment 3: N=10⁷ scaling (8 runs)
- ⚠ **Population capped at 2M** — all runs STABLE, no maturation signal
- Likely N_MAX allocation or turbidostat cap issue — needs debugging

Full analysis: `results/OVERNIGHT_RESULTS.md`

## 2026-03-18 — JIT GPU Optimization COMPLETE

- **Problem**: N=10⁷ overnight run was stuck at 2M cap and running on CPU (no JIT = no GPU)
- **Solution**: Rewrote growth/selection/simulation as JIT-compiled GPU kernels
- Key techniques:
  1. **Incremental Hamming** — track distance as scalar, mutations update ±1 (saves 10.4 GB intermediates)
  2. **int8 sequences** — 4× smaller arrays (0.8 GB vs 3.2 GB)
  3. **argsort slot assignment** — find actual dead slots for daughters (fixed critical bug)
- **Validation**: 4 head-to-head controls (same seed, old CPU vs JIT GPU) — all within Δ0.03
- **Performance**: N=10M at **4.9s/cycle** (was ~1,870s on CPU = **380× speedup**)
- N=10⁷ experiment now feasible: ~90 min for 8 runs (was 47h)
- Report: `results/JIT_VALIDATION_REPORT.md`

## 2026-03-19 — Q4 N-Scaling COMPLETE (81 runs, 11.1h GPU)

- **3 N values** (10K, 1M, 10M) × 3 T7 rates (V3, V4, V5) × 3 K × 3 seeds
- **Headline result**: Larger N maintains **2× diversity** (3.4-3.9 vs 1.6-2.2) while achieving the **same affinity**
- Δaffinity is nearly identical across all N: V4 K=0.3 gives +0.19 (10K), +0.20 (1M), +0.20 (10M)
- V5 K=0.1 degrades at ALL N values — **population size does not shift the maturation boundary**
- The bacterial GC advantage is **repertoire breadth**, not affinity depth
- Full analysis: `results/q4_n_scaling/Q4_ANALYSIS.md`

## 2026-03-19 — Q3 DZ/LZ Cycling COMPLETE (48 runs, 6.5h GPU)

- 4 cycling speeds (dz_div=2,4,6,12) × 2 rates (V4,V5) × 2 N (10K,10M) × 3 seeds
- **Cycling speed has minimal effect** — Δaff varies by only ±0.02 across all dz_divisions
- Muller's ratchet is NOT rescued by faster cycling — controlled by K alone
- **Experimental implication**: transfer timing is not critical, use whatever is convenient
- Full analysis: `results/q3_cycling/Q3_ANALYSIS.md`
