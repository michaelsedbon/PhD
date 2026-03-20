# Flow Diagram B: Bacterial Synthetic GC (Your System)

> **Purpose**: Simulate the bacterial immune side of the Maimonide synthetic GC.
> **Scale**: 10⁸ bacteria, no spatial grid, ~7-9 GB VRAM on RTX 2080 Ti.
> **Spatial model**: None — well-mixed within each compartment (DZ well, LZ well).
> **Time step**: Discrete cycles (each ~6h growth + selection). Total: 10-50 cycles.
> **Growth model**: Turbidostat — constant density via periodic dilution.
> **Future**: 96 parallel wells, inter-well migration, antigen co-evolution.

---

## System Specificities

| Property | Natural GC (Diagram A) | Bacterial Synthetic GC (Diagram B) |
|---|---|---|
| **Space** | 3D lattice 80³, sphere, cell exclusion | **No grid.** Two well-mixed compartments: DZ well, LZ well |
| **Agents** | Centroblasts, Centrocytes, T cells, FDCs, Stromal | **Bacteria only.** Each has a nanobody genotype + compartment tag |
| **Population** | ~10⁴ | **~10⁸** |
| **Sequence** | Shape space L=4 | Shape space L=4 (same, for validation; extensible to L=50+ later) |
| **Mutation** | At B cell division in DZ (SHM) | **Error-prone replication in DZ well** (T7 polymerase / MP6) |
| **Migration** | Autonomous chemotaxis (CXCL12/13) | **Scheduled robotic pipetting** (transfer fraction every N hours) |
| **Selection** | FDC antigen capture + competitive T cell help | **Bead-based binding (WP1)** or phage-infection gating (WP2) |
| **Division** | Cell cycle G1→S→G2→M (~6h) | **Bacterial growth** (doubling time ~20-40 min, carrying capacity) |
| **Death** | Apoptosis if no T cell rescue | **Wash-out** (bead pulldown), colicin kill, or dilution death |
| **Differentiation** | Recycle to DZ or exit as output | **Recycle to DZ well** or extract for sequencing/characterization |
| **Antigen** | On FDC fragments (static or feedback) | **On magnetic beads (static)** — antigen drift deferred to Phase 2 |
| **Chemotaxis** | CXCL12/CXCL13 diffusion | **Not applicable** |
| **T cells** | Competitive help (best antigen presenter) | **Not applicable** — replaced by selection model |

---

## Data Representation (Structure of Arrays)

```python
# All arrays have length N (current population, up to N_max = 10^8)
# Stored as JAX DeviceArrays on GPU

sequences:          int32[N, L]     # Nanobody genotype in shape space
affinities:         float32[N]      # Pre-computed affinity to antigen
compartment:        int8[N]         # 0 = DZ_well, 1 = LZ_well, 2 = extracted
state:              int8[N]         # 0 = growing, 1 = selected, 2 = dead
generation:         int32[N]        # Number of divisions since founder
clone_id:           int32[N]        # Founder clone identity (for lineage tracking)
parent_id:          int32[N]        # Parent index (for tree reconstruction)
n_divisions_left:   int8[N]         # Remaining doublings before migration to LZ
alive:              bool[N]         # Alive mask (for compaction)
```

**Antigen** (static): `int32[L]` — single target sequence, fixed.

---

## Top-Level Loop

```
bacterial_sim.run_experiment(config) → History
│
├── state = bacterial_init.initialize(config)
│   • Create N_founders bacteria in DZ_well  
│   • Each at Hamming distance d_init from antigen
│   • Set n_divisions_left = config.dz_divisions
│
└── for cycle in 0 .. config.n_cycles:
│       state = bacterial_sim.run_cycle(state, config, cycle)
│       history.append(bacterial_analysis.snapshot(state))
│
│   # A "cycle" = one round of: grow → migrate DZ→LZ → select → migrate LZ→DZ
│   # Analogous to one round through the GC
│
└── return history
```

---

## Per-Cycle Pipeline

Each cycle corresponds to **one experimental round** of the synthetic GC protocol:
1. Grow bacteria in DZ well (turbidostat: repeated doubling + dilution, with mutation)
2. Cells that completed N divisions auto-migrate to LZ well
3. Apply selection in LZ well (bead assay or phage)
4. Survivors return to DZ well (+ optional fraction of unselected)
5. Compact dead cells, log state

```
╔════════════════════════════════════════════════════════════════════════╗
║              bacterial_sim.run_cycle(state, config, cycle)            ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  ┌─ Block 1+2: TURBIDOSTAT GROWTH + MUTATION IN DZ ──────────────┐   ║
║  │  growth.turbidostat_growth(seqs, affs, ..., config, rng)       │   ║
║  │                                                                │   ║
║  │  • Simulates turbidostat: repeated rounds of:                  │   ║
║  │    1. Double population (each cell divides once)               │   ║
║  │    2. Apply mutations to daughters (rate per position per div) │   ║
║  │    3. Dilute back to target_n (random washout)                 │   ║
║  │  • n_rounds = dz_growth_hours / doubling_time                  │   ║
║  │  • Per-cell division counter tracks divisions_since_selection   │   ║
║  │  • Returns ready_for_lz mask (cells with divs >= dz_divisions) │   ║
║  │                                                                │   ║
║  │  Key sub-functions:                                            │   ║
║  │    grow_one_doubling() — divide all, mutate daughters          │   ║
║  │    dilute_to_target() — random subsample to target_n           │   ║
║  │                                                                │   ║
║  │  In:  DZ bacteria, antigen, config (target_n, doubling_time,   │   ║
║  │       dz_growth_hours, dz_divisions, mutation_rate)            │   ║
║  │  Out: grown population + ready_for_lz mask                     │   ║
║  └────────────────────────────────────────────────────────────────┘   ║
║                              │                                        ║
║  ┌─ Block 3: DIVISION-TRIGGERED MIGRATION DZ → LZ ───────────────┐  ║
║  │  (integrated in simulation.run_cycle)                           │  ║
║  │                                                                 │  ║
║  │  • Cells with div_counter >= config.dz_divisions auto-migrate  │  ║
║  │  • NOT random sampling — deterministic based on division count │  ║
║  │  • Remaining cells (div_counter < threshold) stay in DZ        │  ║
║  │  • This mirrors the natural GC: CBs migrate after N divisions  │  ║
║  │                                                                 │  ║
║  │  In:  all DZ bacteria, ready_for_lz mask                       │  ║
║  │  Out: ready cells go to LZ selection, rest stay in DZ           │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                              │                                        ║
║  ┌─ Block 4: SELECTION IN LZ WELL ───────────────────────────────┐   ║
║  │  selection.apply_selection(state, config, rng)                  │  ║
║  │                                                                 │  ║
║  │  • For bacteria in LZ_well, apply one of:                      │  ║
║  │                                                                 │  ║
║  │    MODEL A — Soft Proportional (Hill):                          │  ║
║  │      P(survive) = aff^n / (aff^n + K^n)                        │  ║
║  │                                                                 │  ║
║  │    MODEL B — Hard Threshold:                                    │  ║
║  │      P(survive) = 1 if affinity > threshold else 0             │  ║
║  │                                                                 │  ║
║  │    MODEL C — Tournament (Top-K):                                │  ║
║  │      Keep top config.keep_fraction by affinity                  │  ║
║  │                                                                 │  ║
║  │    MODEL D — Physics-Based Bead Binding:                        │  ║
║  │      P(bind) = 1 - exp(-kon(aff) × [beads] × t_incub)         │  ║
║  │      P(stay) = exp(-koff(aff) × t_wash)                        │  ║
║  │      P(survive) = P(bind) × P(stay)                             │  ║
║  │                                                                 │  ║
║  │  • Dead bacteria: alive=false                                   │  ║
║  │                                                                 │  ║
║  │  In:  bacteria[compartment==LZ], affinities, config             │  ║
║  │  Out: survivors (alive mask updated)                             │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                              │                                        ║
║  ┌─ Block 5: EXTRACTION / OUTPUT ─────────────────────────────────┐  ║
║  │  differentiation.extract_output(state, config)                  │  ║
║  │                                                                 │  ║
║  │  • Optionally remove a fraction of high-affinity survivors      │  ║
║  │    for sequencing / characterization (output cells)             │  ║
║  │  • config.extraction_fraction (e.g. 0 = none, 0.05 = 5%)       │  ║
║  │  • Extracted bacteria: compartment = "extracted"                │  ║
║  │                                                                 │  ║
║  │  In:  bacteria[compartment==LZ, alive], config                  │  ║
║  │  Out: extracted bacteria logged, remaining stay in LZ           │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                              │                                        ║
║  ┌─ Block 6: RECYCLE LZ → DZ  ────────────────────────────────────┐  ║
║  │  (integrated in simulation.run_cycle)                           │  ║
║  │                                                                 │  ║
║  │  • All surviving LZ bacteria return to DZ well                  │  ║
║  │  • Division counters reset to 0 for recycled cells              │  ║
║  │  • OPTIONAL: fraction of unselected also return                 │  ║
║  │    (config.unselected_return_fraction, default=0)               │  ║
║  │  • This completes one GC cycle                                  │  ║
║  │                                                                 │  ║
║  │  In:  survivors + optional unselected, DZ-stay cells            │  ║
║  │  Out: combined DZ population, ready for next growth cycle       │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                              │                                        ║
║  ┌─ Block 7: COMPACTION ─────────────────────────────────────────┐   ║
║  │  state.compact(state)                                           │  ║
║  │                                                                 │  ║
║  │  • Remove dead bacteria from all arrays                         │  ║
║  │  • Resize arrays to N_alive                                     │  ║
║  │  • Critical for GPU memory at 10^8 scale                        │  ║
║  │                                                                 │  ║
║  │  In:  all arrays + alive mask                                   │  ║
║  │  Out: compacted arrays (smaller N)                              │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
║  ┌─ FUTURE STUB: ANTIGEN EVOLUTION ──────────────────────────────┐   ║
║  │  antigen.evolve(state, config)   [NOT IMPLEMENTED]              │  ║
║  │                                                                 │  ║
║  │  • Phase 2: antigen (phage-displayed RBD) mutates under         │  ║
║  │    nanobody pressure, creating an arms race                     │  ║
║  │  • Would add: phage population, phage mutation, phage selection │  ║
║  │  • Interface: antigen.get_current_antigen() → int[L]            │  ║
║  │  • For now: returns config.antigen (static)                     │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
║  ┌─ FUTURE STUB: 96-WELL PARALLELIZATION ────────────────────────┐   ║
║  │  multiwell.manage_wells(states[], config)   [NOT IMPLEMENTED]   │  ║
║  │                                                                 │  ║
║  │  • 96 independent GC simulations running in parallel            │  ║
║  │  • Inter-well migration: transfer bacteria between any wells    │  ║
║  │  • Different selection stringency per well                      │  ║
║  │  • Interface: multiwell.run_plate(configs[96]) → Histories[96]  │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## Function Signatures

### `bacterial_init.py` — Setup
| Function | Signature | Notes |
|---|---|---|
| `initialize` | `(config) → BacterialState` | Create founders in DZ |
| `create_founders` | `(N, antigen, d_init, L, rng) → (seqs, affs)` | Random seqs at Hamming d_init |

### `growth.py` — Turbidostat Growth + Mutation
| Function | Signature | Notes |
|---|---|---|
| `turbidostat_growth` | `(seqs, affs, clones, gens, divs, antigen, config, rng) → (..., ready_for_lz)` | Full turbidostat cycle |
| `grow_one_doubling` | `(seqs, affs, ..., rng) → (2N arrays)` | one round: divide + mutate daughters |
| `dilute_to_target` | `(seqs, ..., target_n, rng) → (target_n arrays)` | Random washout to target |

### Shared from Phase 0 (`germinal_center/affinity.py`)
| Function | Signature | Notes |
|---|---|---|
| `mutate_sequence` | `(seq[L], rng, R, L) → seq[L]` | ±1 on one random position |
| `batch_affinity` | `(seqs[N,L], ag[L], Γ, η) → float[N]` | Vectorized Gaussian affinity |
| `create_founders_at_distance` | `(N, ag, d_min, d_max, rng) → seqs[N,L]` | Founders at Hamming distance |

### `migration.py` — Robotic Transfers (v1 only, not used in v2)
| Function | Signature | Notes |
|---|---|---|
| `transfer_dz_to_lz` | `(state, fraction, rng) → state` | Random subsample DZ → LZ |
| `transfer_lz_to_dz` | `(state) → state` | All survivors LZ → DZ |

### `selection.py` — Affinity-Based Selection
| Function | Signature | Notes |
|---|---|---|
| `apply_selection` | `(state, config, rng) → state` | Dispatcher for models A-D |
| `select_hill` | `(aff[N], n, K, rng) → alive[N]` | Model A: Hill |
| `select_threshold` | `(aff[N], thresh) → alive[N]` | Model B: threshold |
| `select_topk` | `(aff[N], keep_frac) → alive[N]` | Model C: tournament |
| `select_bead_binding` | `(aff[N], kon, koff, beads, t_inc, t_wash, rng) → alive[N]` | Model D: physics |

### `differentiation.py` — Output Extraction
| Function | Signature | Notes |
|---|---|---|
| `extract_output` | `(state, config) → state` | Remove top-affinity for characterization |
| `reset_for_dz` | `(state, config) → state` | Reset division counters for recycled cells |

### `bacterial_sim.py` — Main Loop
| Function | Signature | Notes |
|---|---|---|
| `run_experiment` | `(config) → History` | Full experiment |
| `run_cycle` | `(state, config, cycle, rng) → state` | One DZ→LZ→DZ round |

### `bacterial_analysis.py` — Metrics & Plots
| Function | Signature | Notes |
|---|---|---|
| `snapshot` | `(state) → Snapshot` | Population, affinity stats, diversity |
| `plot_affinity_over_cycles` | `(history) → Figure` | Mean/max affinity per cycle |
| `plot_population_dynamics` | `(history) → Figure` | N per compartment per cycle |
| `plot_diversity` | `(history) → Figure` | Shannon entropy, clone count |
| `plot_clone_phylogeny` | `(history) → Figure` | Lineage tree of top clones |
| `heatmap_parameter_sweep` | `(sweep_results) → Figure` | Affinity vs (mut_rate, sel_stringency) |

### `parameter_sweep.py` — Exploration
| Function | Signature | Notes |
|---|---|---|
| `grid_sweep` | `(param_grid, base_config) → results` | Run sim for each parameter combo |
| `genetic_algorithm` | `(objective_fn, param_bounds, config) → best_params` | Optimize parameters |
| `objective_affinity` | `(config) → float` | Run sim, return mean final affinity |
| `objective_diversity` | `(config) → float` | Run sim, return final diversity |

---

## Key Parameters (Tuneable)

| Parameter | Default | Range to explore | Unit | Experimental knob |
|---|---|---|---|---|
| `N_founders` | 10⁴ | 10²–10⁶ | cells | Initial library size |
| `carrying_capacity_K` | 10⁸ | 10⁶–10⁹ | cells | Culture volume / nutrients |
| `doubling_time` | 30 | 20–60 | min | Strain / media |
| `dz_growth_hours` | 6 | 2–24 | h | Incubation time before transfer |
| `dz_divisions` | 10 | 3–20 | count | How many doublings in DZ |
| `mutation_rate` | 0.05 | 10⁻⁵–10⁻¹ | per pos per div | Mutagenesis error rate |
| `dz_divisions` | 6 | 3–20 | count | Divisions before auto-migration to LZ |
| `unselected_return_fraction` | 0 | 0–1.0 | fraction | Unselected cells returned to DZ |
| `selection_model` | "hill" | A/B/C/D | — | Experimental protocol |
| `hill_n` | 3 | 1–10 | — | Selection sharpness |
| `hill_K` | 0.3 | 0.05–0.9 | affinity | Half-max threshold |
| `threshold` | 0.5 | 0.1–0.9 | affinity | Hard cutoff (model B) |
| `keep_fraction` | 0.1 | 0.01–0.5 | fraction | Top-K (model C) |
| `n_cycles` | 10 | 1–50 | rounds | Total GC cycles |
| `extraction_fraction` | 0 | 0–0.1 | fraction | Output removal |
| `shape_space_L` | 4 | 4–200 | dims | Sequence complexity |
| `Γ` (Gaussian width) | 2.8 | 1–5 | — | Affinity landscape shape |

---

## Notebook Checkpoints (Bacterial Version)

| # | Checkpoint | Verify |
|---|---|---|
| 1 | Initialize founders | N founders at expected Hamming distance, correct affinities |
| 2 | Growth test | Start with 10⁴, grow for 6h at 30min doubling → expect ~10⁸ |
| 3 | Mutation test | Apply mutations, plot affinity distribution shift |
| 4 | Migration test | Transfer 10% of DZ → LZ, verify population split |
| 5 | Selection test A-D | Apply each model, verify survival correlates with affinity |
| 6 | Full cycle (1 round) | Run one complete DZ→LZ→DZ cycle, check population + affinity |
| 7 | Multi-cycle (10 rounds) | Run 10 cycles, verify affinity maturation |
| 8 | Parameter sweep | Sweep mutation_rate × hill_K, generate heatmap |
| 9 | Memory profiling | Run at 10⁶, 10⁷, 10⁸ — measure VRAM and wall time |
