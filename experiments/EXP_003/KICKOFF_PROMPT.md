# EXP_003 Kickoff — Bacterial Synthetic Germinal Center: GPU Simulation v2

## Your Role

I'm building a **GPU-accelerated simulation of a bacterial synthetic germinal center (GC)** in Python using **JAX**. I'll be coding this myself directly on a remote server with an NVIDIA GPU. I need you as a **copilot** — help me design the architecture first (flow diagram), then guide me through implementation. I have no experience coding on the GPU.

## First Step: Read Reference Documents

Before doing anything, read these documents in order. They're all in this experiment folder:

### 1. Grant Proposal (the science)
📄 [grant_proposal.md](docs/grant_proposal.md)  
The full Maimonide 2026 grant proposal. Read the section on the synthetic germinal center — it describes the core biology and experimental approach.

### 2. Parameter–Biology Reference (the mapping)
📄 [PARAMETER_BIOLOGY_REFERENCE.md](docs/PARAMETER_BIOLOGY_REFERENCE.md)  
Maps every simulation parameter to its biological reality. Includes all 6 T7 polymerase variant mutation rates, natural GC selection parameters, population biology, and our existing simulation results. **This is the key reference for biologically grounded parameter choices.**

### 3. Scientific Questions (what we're investigating)
📄 [open_questions.md](docs/open_questions.md)  
12 scientific questions we want to answer with the simulation. Q1-Q4 are answered from EXP_002. The new focus is Q12: *Does population size relax the diversification requirement before selection?*

### 4. Selection Model Analysis (how selection works)
📄 [selection_model_analysis.md](docs/selection_model_analysis.md)  
Comparison of independent (Hill) vs competitive (top-fraction) selection. Key finding from EXP_002: competitive selection at 10% survival preserves population while being equally effective for maturation.

### 5. Shape Space Explainer (the affinity model)
📄 [shape_space_explainer.md](docs/shape_space_explainer.md)  
How affinity is computed from genotype: `affinity = exp(-( hamming(cell, antigen) / γ )^η)`. Incremental Hamming updates for GPU efficiency.

### 6. Muller's Ratchet Analysis (mutation load)
📄 [mullers_ratchet.md](docs/mullers_ratchet.md)  
Why high mutation rates degrade affinity in asexual populations. The maturation boundary sits between T7 V3 (10⁻⁶) and V4 (10⁻⁵).

### 7. Key Papers (in `docs/papers/`)
- **Robert_How_to_Simulate_GC.txt** — The reference GC simulation model (hyphasma). Read the selection steps in detail: antigen collection + T cell competition.
- **Mesin_GC_Dynamics.txt** — Comprehensive review of GC biology (Mesin 2016). Key: ~10-30% of LZ cells survive per cycle.
- **Diercks_T7_Replisome.txt** — The T7 replisome mutation system we're using. 5 polymerase variants spanning 10⁻⁸ to 10⁻⁵ sub/bp/rep.
- **Victora_Nussenzweig_GC_Review.txt** — GC biology fundamentals.
- **Tas_Visualizing_Affinity_Maturation.txt** — Clonal diversity in GCs (50-200 founders, diversity maintained during maturation).
- **Shinnakasu_Regulated_Selection_GC.txt** — Regulated selection mechanisms.
- **Sprumont_GC_Clonal_Diversity.txt** — GC output and clonal diversity.
- **Ravikumar_OrthoRep.txt** — OrthoRep: continuous in vivo mutagenesis (related technology).

---

## Project Overview

### The Biology

The **germinal center** is where antibodies get better over time through:
1. **Dark Zone (DZ)**: B cells divide rapidly, accumulating random mutations (somatic hypermutation)
2. **Light Zone (LZ)**: Mutated cells compete for limited T cell help — only the **top ~10-30%** by antigen-binding affinity survive
3. **Cycling**: Survivors return to the DZ for more mutation. Dead cells are replaced by growth.

Our **bacterial version** replaces B cells with bacteria displaying nanobodies, and T cell help with **bead-based affinity selection** controlled by a pipetting robot:
- **DZ** = well with growing bacteria (turbidostat at ~10⁶-10⁷ cells)
- **LZ** = selection step: robot takes a fraction of DZ bacteria, incubates with antigen-coated magnetic beads, washes, keeps binders
- **Cycling** = continuous pipeline: every ~1.5h, the robot samples cells from DZ → LZ, returns selected cells, loads new batch

### The Simulation Architecture — Pipeline Model

The simulation uses a **continuous pipeline** rather than batch cycles:

```
Every mini-cycle (e.g. every 3 doublings / 1.5h):
  1. GROW: all DZ cells divide (turbidostat maintains population at target N)
     - Daughters inherit parent sequence + possible point mutation
     - Mutation rate: per-position-per-division (configurable)
     - Turbidostat: if N > target, randomly cull back to target
  
  2. SAMPLE: randomly move X% of DZ cells → LZ
     - Models the robot aspirating a fraction of the culture
  
  3. SELECT: competitive selection on LZ cells
     - Rank all LZ cells by affinity
     - Keep only the top Y% (models limited bead binding sites)
     - Kill the rest (wash away unbound)
  
  4. RETURN: survivors go back to DZ (div_counter reset)
```

### Key Data Structures (all fixed-size arrays for GPU)

```
sequences:    int8[N_MAX, L]     — each cell's genotype (L positions)
affinities:   float32[N_MAX]     — binding affinity to target antigen
hamming:      float32[N_MAX]     — Hamming distance to antigen (for fast affinity calc)
alive:        bool[N_MAX]        — slot is occupied
in_lz:        bool[N_MAX]        — cell is in LZ (awaiting selection)
div_counter:  int32[N_MAX]       — divisions since last selection
clone_id:     int32[N_MAX]       — founder lineage tracking
```

- **N_MAX** = 2 × target_n (buffer for growth before dilution)
- Dead slots (alive=False) are reused for daughters via argsort-based slot allocation

### Affinity Model (shape space)

```
affinity(cell) = exp(-( hamming_distance(cell, antigen) / γ )^η)
```
- `γ = 10.5` (Gaussian width)
- `η = 2.0` (Gaussian exponent)
- Perfect match (hamming=0) → affinity = 1.0
- Each mutation changes hamming by ±1 → **incremental affinity update** (no need to recompute full sequence comparison)

### Parameter Summary

| Parameter | Symbol | Biological meaning | Values to test |
|---|---|---|---|
| **Mutation rate** | `mutation_rate` | T7 polymerase fidelity (per bp per div) | V3: 10⁻⁶, V4: 10⁻⁵, V5: 10⁻⁴ |
| **Shape space dim** | `L` | Abstract nanobody gene length | 40 |
| **Population size** | `target_n` | Turbidostat capacity | 10K, 1M, 10M |
| **Sample fraction** | `sample_fraction` | % of DZ taken to LZ each round | 30-50% |
| **Keep fraction** | `keep_fraction` | % of LZ cells surviving selection | 10-30% |
| **Mini-cycle doublings** | `mini_cycle_doublings` | Growth rounds between selections | 3 (=1.5h) |
| **N founders** | `n_founders` | Initial library size | 50 |
| **Total mini-cycles** | `total_mini_cycles` | Experiment duration | 560 (~35 days) |

See `docs/PARAMETER_BIOLOGY_REFERENCE.md` for the full mapping with T7 variant rates and natural GC values.

### GPU/JAX Constraints
- All arrays must be **fixed size** (N_MAX) — JAX JIT requires static shapes
- Use **boolean masks** instead of dynamic indexing
- No Python-level data-dependent control flow inside JIT-compiled functions
- Use `jax.jit` with `static_argnums` for parameters that change between runs but not within a run

### Server Setup
- Ubuntu server at `172.16.1.80`, user `michael`
- Python 3.11 with JAX + CUDA in a venv at `~/gc_simulation/.venv`
- NVIDIA GPU available, set `JAX_PLATFORMS=cuda,cpu`
- Working directory for this experiment: create at `~/gc_simulation/EXP_003/`

### Key Learnings from EXP_002 (what to keep / change)

**Keep:**
- Incremental Hamming distance for memory-efficient affinity updates
- argsort-based free-slot assignment for daughters
- `int8` sequences for memory efficiency
- Turbidostat dilution model
- Shannon entropy for diversity tracking

**Change (new in v2):**
- **Pipeline model** instead of batch (continuous DZ→LZ cycling)
- **Competitive selection** (top-fraction) instead of Hill (independent)
- **Random LZ sampling** — only X% of DZ goes to LZ each mini-cycle
- Clean, modular code structure from scratch

---

## What I Need First

**Create a comprehensive flow diagram** of the entire simulation showing:
1. Initialization (founder creation, array allocation)
2. The pipeline mini-cycle loop (grow → sample → select → return)
3. Data flow between arrays at each step
4. Where JIT boundaries should be (which functions get `@jax.jit`)
5. Snapshot/metrics collection points
6. How the pipeline maps to the actual robot workflow

After the flow diagram is approved, I'll start coding each function one by one with your guidance.
