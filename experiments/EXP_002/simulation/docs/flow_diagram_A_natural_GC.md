# Flow Diagram A: Natural Germinal Center (Paper Reproduction)

> **Purpose**: Faithfully reproduce Robert et al. hyphasma model.
> **Scale**: ~10⁴ cells, 3D lattice 80³, ~10 MB VRAM.
> **Spatial model**: 3D grid, sphere geometry, cells occupy single grid points with exclusion.
> **Time step**: dt = 0.002 h (7.2 s), total ~21 simulated days.

---

## System Specificities

| Property | Detail |
|---|---|
| **Space** | 3D cubic lattice N=80, dx=5 µm. GC = sphere of radius N/2. |
| **Agents** | Centroblasts (DZ), Centrocytes (LZ), T cells, FDCs (multi-fragment), Stromal cells, Output cells |
| **Sequence** | Shape space L=4 integers. Affinity = exp(−(Hamming/Γ)^η) |
| **Chemotaxis** | CXCL12 (dark zone, from stromal cells) + CXCL13 (light zone, from FDCs). Diffusion + production + desensitization. |
| **Movement** | Persistent random walk with polarity vector; biased by chemokine gradient; one cell per grid point (exclusion). |
| **Mutation** | At centroblast division: ±1 on one random shape-space position |
| **Selection** | Two-stage: (1) affinity-dependent antigen capture from FDC fragments, (2) competitive T cell help (best antigen presenter wins) |
| **Division** | Cell cycle G1→S→G2→M with timed phases (~6h total). Division count set by Hill(affinity) after recycling. |
| **Differentiation** | Selected centrocyte → recycle to centroblast (DZ) OR exit as output cell |
| **Feedback** | Optional: output cells produce antibodies that mask FDC antigen |

---

## Top-Level Loop

```
simulation.run_simulation(config) → History
│
├── state = initialization.initialize_gc(config)         ← Algorithm 9
│
└── for t in 0 .. n_timesteps:
        state = simulation.step(state, config, t)
        if t % snapshot_interval == 0:
            history.append(analysis.snapshot(state))
```

---

## Per-Timestep Pipeline

```
╔══════════════════════════════════════════════════════════════════════╗
║                     simulation.step(state, config, t)              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ┌─ Block 1: CHEMOKINE PRODUCTION ─────────────────────────────┐   ║
║  │  chemotaxis.produce_chemokine(state)                        │   ║
║  │  Paper: Algorithm 2 (production)                            │   ║
║  │  • Stromal cells produce CXCL12 in dark zone                │   ║
║  │  • FDCs produce CXCL13 in light zone                        │   ║
║  │  In:  grid, fdcs, stromal_cells, rates                      │   ║
║  │  Out: CXCL12[N,N,N], CXCL13[N,N,N]                         │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 2: CHEMOKINE DIFFUSION ──────────────────────────────┐   ║
║  │  chemotaxis.diffuse_chemokines(state, config)               │   ║
║  │  Paper: Algorithm 2 (diffusion)                             │   ║
║  │  • Finite-difference diffusion on 3D grid (D=1000 µm²/h)   │   ║
║  │  • Dirichlet boundary (concentration=0 at sphere edge)      │   ║
║  │  In:  CXCL12, CXCL13, D, dt, dx, boundary                  │   ║
║  │  Out: updated CXCL12, CXCL13                                │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 3: RECEPTOR SENSITIVITY UPDATE ──────────────────────┐   ║
║  │  chemotaxis.update_receptor_sensitivity(state, config)      │   ║
║  │  Paper: Algorithm 2 (receptor)                              │   ║
║  │  • Each motile cell checks local chemokine concentration    │   ║
║  │  • High dose → desensitize (isResponsive=false)             │   ║
║  │  • Low dose → resensitize (isResponsive=true)               │   ║
║  │  In:  all motile cells, local CXCL12/13 values              │   ║
║  │  Out: cell.isResponsive2signals[CXCL12/13]                  │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 4: CELL MOVEMENT ───────────────────────────────────┐    ║
║  │  movement.move_all_cells(state, config)                     │   ║
║  │  Paper: Algorithm 3                                         │   ║
║  │  • Update polarity vector (persistent random walk)          │   ║
║  │  • Bias polarity by chemokine gradient if responsive        │   ║
║  │  • Find free neighboring grid point in polarity direction   │   ║
║  │  • Move cell (swap grid IDs), enforce exclusion             │   ║
║  │  In:  motile cells, grid, chemokines                        │   ║
║  │  Out: updated cell positions, updated grid                  │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 5: CELL CYCLE + DIVISION + MUTATION ────────────────┐    ║
║  │  cell_cycle.progress_and_divide(state, config, rng)         │   ║
║  │  Paper: Algorithm 4 + Algorithm 1                           │   ║
║  │  • Advance centroblast timers: G1→S→G2→M                   │   ║
║  │  • At M phase: divide → daughter at free neighbor position  │   ║
║  │  • At division: mutate BCR (±1 on random shape-space dim)   │   ║
║  │  • Recompute affinity of daughter                           │   ║
║  │  • Decrement remaining_divisions counter                    │   ║
║  │  • If remaining_divisions==0 → transition to centrocyte     │   ║
║  │  In:  centroblasts, grid, antigen, rng_key                  │   ║
║  │  Out: updated/new centroblasts, new centrocytes, grid       │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 6: FDC ANTIGEN COLLECTION ──────────────────────────┐    ║
║  │  selection.attempt_fdc_contacts(state, config)              │   ║
║  │  Paper: Algorithm 5                                         │   ║
║  │  • Centrocyte in "unselected" state checks FDC neighbors    │   ║
║  │  • If FDC fragment nearby with antigen:                     │   ║
║  │    P(capture) depends on affinity(BCR, antigen)             │   ║
║  │  • Successful capture: nFDCcontacts++, antigen removed      │   ║
║  │  • After collectFDCperiod: transition to "FDCselected"      │   ║
║  │  In:  centrocytes (unselected), FDCs, grid                  │   ║
║  │  Out: centrocytes with nFDCcontacts, FDCs with less antigen │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 7: T CELL HELP (COMPETITIVE SELECTION) ─────────────┐   ║
║  │  selection.screen_tcell_help(state, config)                 │   ║
║  │  Paper: Algorithm 6 + Algorithm 7                           │   ║
║  │  • Centrocyte in "FDCselected" state searches for Tfh       │   ║
║  │  • When neighboring Tfh found: start signaling              │   ║
║  │  • Tfh only signals to the B cell with HIGHEST nFDCcontacts │   ║
║  │  • Signal must accumulate for tcRescueTime to be rescued    │   ║
║  │  • If tcClock > tcTime without rescue → apoptosis           │   ║
║  │  In:  centrocytes (FDCselected), T cells, grid              │   ║
║  │  Out: centrocytes → "selected" or "apoptosis"               │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 8: APOPTOSIS ──────────────────────────────────────┐     ║
║  │  selection.apply_apoptosis(state)                           │   ║
║  │  • Remove dead centrocytes from grid                        │   ║
║  │  • Free grid positions                                      │   ║
║  │  In:  centrocytes with state=apoptosis                      │   ║
║  │  Out: cells removed, grid updated                           │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 9: DIFFERENTIATION / RECYCLING ─────────────────────┐   ║
║  │  differentiation.process_transitions(state, config)         │   ║
║  │  Paper: Algorithm 8                                         │   ║
║  │  • Selected centrocyte waits individualDiffDelay             │   ║
║  │  • Then: recycle to centroblast (→DZ) OR become output cell │   ║
║  │  • Recycled CB gets division_count = Hill(nFDCcontacts)     │   ║
║  │  • Recycled CB gets mutation_rate = Hill(affinity)           │   ║
║  │  • Output cell: insensitive to chemokines, exits GC         │   ║
║  │  In:  selected centrocytes                                  │   ║
║  │  Out: new centroblasts + new output cells                   │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 10: FOUNDER CELL INFLOW ────────────────────────────┐    ║
║  │  differentiation.apply_inflow(state, t, config)             │   ║
║  │  Paper: Algorithm 9 (lines 36-47)                           │   ║
║  │  • During early GC (first ~3 days): new founder cells enter │   ║
║  │  • Each founder divides 6 times before entering LZ          │   ║
║  │  • Initial BCR: Hamming distance 4-8 from antigen           │   ║
║  │  In:  gc_state, current time                                │   ║
║  │  Out: new centroblasts added                                │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║                              │                                      ║
║  ┌─ Block 11: HOUSEKEEPING ──────────────────────────────────┐     ║
║  │  state.compact_dead_cells()                                 │   ║
║  │  • Remove dead entries from all agent arrays                │   ║
║  │  In:  all agent lists                                       │   ║
║  │  Out: compacted agent lists                                 │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Function Signatures

### `affinity.py` — Sequence & Binding
| Function | Signature | Paper |
|---|---|---|
| `hamming_distance` | `(a: int[L], b: int[L]) → int` | §2.2 |
| `compute_affinity` | `(bcr: int[L], ag: int[L], Γ, η) → float` | §2.2 |
| `mutate_sequence` | `(seq: int[L], rng) → int[L]` | Algo 1 |
| `batch_affinity` | `(bcrs: int[N,L], ag: int[L], Γ, η) → float[N]` | — |

### `chemotaxis.py` — Signals & Gradients
| Function | Signature | Paper |
|---|---|---|
| `produce` | `(grid, sources, rates) → (CXCL12, CXCL13)` | Algo 2 |
| `diffuse` | `(field[N³], D, dt, dx, bnd) → field[N³]` | Algo 2 |
| `update_sensitivity` | `(cell, conc, thresh_up, thresh_down) → cell` | Algo 2 |

### `movement.py` — 3D Random Walk
| Function | Signature | Paper |
|---|---|---|
| `update_polarity` | `(cell, gradient[3], rng, config) → vec[3]` | Algo 3 |
| `compute_gradient` | `(field[N³], pos[3]) → vec[3]` | Algo 3 |
| `find_free_neighbor` | `(pos[3], dir[3], grid) → pos[3]` | Algo 3 |
| `move_cell` | `(cell, grid, new_pos) → (cell, grid)` | Algo 3 |

### `cell_cycle.py` — Division Machinery
| Function | Signature | Paper |
|---|---|---|
| `progress_phase` | `(cb, dt) → cb` | Algo 4 |
| `check_division` | `(cb) → bool` | Algo 4 |
| `divide` | `(parent, grid, ag, rng, config) → (cb1, cb2, grid)` | Algo 4+1 |

### `selection.py` — Immune Selection
| Function | Signature | Paper |
|---|---|---|
| `attempt_fdc_contact` | `(cc, grid, fdcs, config) → cc` | Algo 5 |
| `find_tcell` | `(cc, grid, tcells) → TC?` | Algo 6 |
| `signal_from_tcell` | `(cc, tc, dt) → cc` | Algo 6 |
| `update_tcell_best` | `(tc, ccs[]) → tc` | Algo 7 |
| `check_rescue` | `(cc, config) → {selected, apoptosis, continue}` | Algo 6 |

### `differentiation.py` — Fate Decisions
| Function | Signature | Paper |
|---|---|---|
| `recycle_to_cb` | `(cc, config) → cb` | Algo 8 |
| `n_divisions_hill` | `(affinity, config) → int` | Algo 8 |
| `output_decision` | `(cc, config) → {recycle, output}` | Algo 8 |
| `apply_inflow` | `(state, t, config) → state` | Algo 9 |

### `initialization.py` — Setup
| Function | Signature | Paper |
|---|---|---|
| `create_spherical_grid` | `(N) → Grid` | Algo 9 |
| `place_fdcs` | `(grid, n, arm_len, n_ag, rng) → (Grid, FDCs)` | Algo 9 |
| `place_stromal` | `(grid, n, rng) → (Grid, Stroma)` | Algo 9 |
| `place_tcells` | `(grid, n, rng) → (Grid, TCs)` | Algo 9 |
| `create_founders` | `(n, ag, hamm_dist, config, rng) → CBs` | Algo 9 |

---

## Key Parameters (Paper Tables 1-2)

| Parameter | Value | Unit |
|---|---|---|
| Grid N | 80 | points |
| dx | 5 | µm |
| dt | 0.002 | h |
| Shape space L | 4 | dims |
| Γ (Gaussian width) | 2.8 | — |
| D (diffusion) | 1000 | µm²/h |
| Speed CB / CC | 7.5 / 5 | µm/min |
| Persistence time | 0.025 | h |
| Cell cycle total | ~6 | h |
| collectFDCperiod | 0.7 | h |
| tcTime | 0.5 | h |
| tcRescueTime | 2 | h |
| N founders | ~100 | cells |
| Initial Hamming dist | 4–8 | — |
| N FDCs / N Tcells | 20 / 100 | cells |
