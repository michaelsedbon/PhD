# Implementation Plan: Phase 0 — Reproduce Hyphasma GC Simulation

## Goal

Reproduce the key results from Robert et al. *"How to Simulate a Germinal Center"* (hyphasma model) using **Python + JAX**, producing:
1. A **Jupyter notebook** with each block independently testable (checkpointed)
2. A **standalone Python package** with CLI for batch runs
3. A **flow diagram** (handoff document) mapping every simulation block to a specific function

This is Phase 0 — faithful reproduction of the paper. Phase 1 (adapt to bacterial system) is not covered here.

---

## User Review Required

> [!NOTE]
> **GPU confirmed**: RTX 2080 Ti (11 GB VRAM) on server `172.16.1.80`. This is more than enough for Phase 0 (3D lattice, ~10⁴ cells, ~10 MB VRAM). For Phase 1 bacterial sim at 10⁸, VRAM is tight (~7-9 GB) but feasible with careful memory management. At 10⁹ we would need batched processing or a bigger GPU.

> [!NOTE]
> **Scope confirmed**: Full 3D lattice reproduction of the paper (with spatial movement, chemotaxis, FDCs, T cells). This will be rewritten in Phase 1 for the well-mixed bacterial model.

---

## Project Structure

```
projects/synthetic_germinal_center/simulation/
├── docs/
│   ├── brainstorm_gpu_germinal_center.md    [EXISTS]
│   ├── shape_space_explainer.md             [EXISTS]
│   ├── selection_model_analysis.md          [EXISTS]
│   ├── flow_diagram_A_natural_GC.md        [EXISTS] — 3D lattice GC (paper)
│   ├── flow_diagram_B_bacterial_GC.md       [EXISTS] — well-mixed bacterial GC
│   └── parameters.md                        [NEW] — all paper parameters (Tables 1-2)
├── src/
│   └── germinal_center/
│       ├── __init__.py                      [NEW]
│       ├── config.py                        [NEW] — parameter dataclass
│       ├── state.py                         [NEW] — GC state (grid + agent arrays)
│       ├── affinity.py                      [NEW] — shape space, Hamming, Gaussian
│       ├── chemotaxis.py                    [NEW] — diffusion solver, receptor updates
│       ├── movement.py                      [NEW] — persistent random walk + gradients
│       ├── cell_cycle.py                    [NEW] — G1→S→G2→M→division
│       ├── mutation.py                      [NEW] — shape space mutation
│       ├── selection.py                     [NEW] — FDC collection + T cell help
│       ├── differentiation.py              [NEW] — recycling, output, inflow
│       ├── initialization.py               [NEW] — sphere grid, FDCs, founder clones
│       ├── simulation.py                    [NEW] — main simulation loop
│       └── analysis.py                      [NEW] — metrics, plots
├── notebooks/
│   └── 01_reproduce_paper.ipynb             [NEW] — checkpointed notebook
├── tests/
│   └── test_affinity.py                     [NEW] — unit tests for affinity computation
├── run.py                                   [NEW] — CLI entry point
└── requirements.txt                         [NEW]
```

---

## Proposed Changes

### Core Data Structures

#### [NEW] [config.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/config.py)

Dataclass holding all simulation parameters from Tables 1-2 of the paper. Every parameter has a docstring with its unit and paper source.

#### [NEW] [state.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/state.py)

GC state representation:
- `Grid[N,N,N]` — cell type + cell ID per grid point
- `CXCL12[N,N,N]`, `CXCL13[N,N,N]` — chemokine concentrations
- Agent lists as Structure of Arrays (SoA): `CBState`, `CCState`, `TCState`, `FDCState`, `OutState`
- Each agent carries: position, polarity, sequence, affinity, state, clocks, clone_id

---

### Module 1: Affinity (Paper Algorithm 1)

#### [NEW] [affinity.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/affinity.py)

- `hamming_distance(seq_a, seq_b) → int` — count differing positions
- `compute_affinity(bcr_seq, antigen_seq, gamma, eta) → float` — Gaussian of Hamming
- `mutate_sequence(seq, rng_key) → new_seq` — ±1 on one random position
- `create_antigen(L) → sequence` — fixed target sequence
- `create_initial_bcrs(n_clones, L, initial_distance, rng_key) → sequences` — founders at given Hamming distance

---

### Module 2: Chemotaxis (Paper Algorithm 2)

#### [NEW] [chemotaxis.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/chemotaxis.py)

- `diffuse_chemokine(concentration_grid, D, dt, dx, boundary) → grid` — finite-difference diffusion
- `update_receptor_sensitivity(cell, local_concentration, config) → cell` — desensitize at high dose, resensitize at low
- `produce_chemokine(grid, cell_positions, production_rates) → grid` — source terms from FDCs/stromal cells

---

### Module 3: Movement (Paper Algorithm 3)

#### [NEW] [movement.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/movement.py)

- `update_polarity(cell, chemokine_gradient, config) → polarity` — biased persistent random walk
- `find_target_position(cell, polarity, grid) → (x,y,z)` — best grid point in polarity direction
- `move_cells(cells, grid, chemokines, config) → (cells, grid)` — batch movement with exclusion

---

### Module 4: Cell Cycle (Paper Algorithm 4)

#### [NEW] [cell_cycle.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/cell_cycle.py)

- `progress_cell_cycle(cell, dt) → cell` — advance timers through G1→S→G2→M
- `divide_cell(parent_cell, grid, rng_key) → (daughter1, daughter2, grid)` — create daughter at neighbor position
- `apply_mutation_at_division(cell, antigen, rng_key, config) → cell` — mutate BCR, recompute affinity

---

### Module 5: Selection (Paper Algorithms 5, 6, 7)

#### [NEW] [selection.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/selection.py)

- `attempt_fdc_contact(centrocyte, fdc_fragments, grid, config) → centrocyte` — affinity-dependent antigen capture
- `screen_for_tcell_help(centrocyte, tcells, grid, config) → centrocyte` — find Tfh, check if best B cell
- `update_tcells(tcells, centrocytes, config) → tcells` — repolarize synapse to best interactor
- `apply_apoptosis(centrocyte, config) → alive` — kill if no T cell rescue in time

---

### Module 6: Differentiation (Paper Algorithm 8)

#### [NEW] [differentiation.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/differentiation.py)

- `recycle_to_centroblast(centrocyte, config) → centroblast` — selected CC → CB, reset clocks, set division count (Hill function of affinity)
- `differentiate_to_output(centrocyte, config) → output_cell` — become output cell
- `apply_inflow(gc_state, config, time) → gc_state` — add new founder cells during early phase

---

### Module 7: Initialization (Paper Algorithm 9)

#### [NEW] [initialization.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/initialization.py)

- `create_grid(N) → Grid` — NxNxN grid, sphere mask
- `place_fdcs(grid, n_fdcs, dendrite_length, antigen_per_fdc) → (grid, fdcs)` — multi-fragment FDCs in light zone
- `place_stromal_cells(grid, n_stromal) → (grid, stromal)` — in dark zone
- `place_tcells(grid, n_tcells) → (grid, tcells)` — in light zone
- `create_founder_clones(n_founders, antigen, initial_distance, config) → centroblasts`
- `initialize_chemokines(grid, fdcs, stromal, config) → (CXCL12, CXCL13)` — steady-state initial conditions

---

### Module 8: Main Loop & Analysis

#### [NEW] [simulation.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/simulation.py)

```python
def run_simulation(config) → History:
    state = initialize(config)
    history = []
    for t in range(config.n_timesteps):
        state = step(state, config, t)
        if t % config.snapshot_interval == 0:
            history.append(snapshot(state))
    return history

def step(state, config, t):
    state = produce_chemokine(state)
    state = diffuse_chemokines(state)
    state = update_receptor_sensitivity(state)
    state = move_all_cells(state)
    state = progress_cell_cycles(state)      # divide + mutate
    state = attempt_fdc_contacts(state)       # antigen collection
    state = screen_tcell_help(state)          # T cell selection
    state = apply_apoptosis(state)
    state = differentiate(state)
    state = apply_inflow(state, t)
    state = compact_dead_cells(state)
    return state
```

#### [NEW] [analysis.py](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/src/germinal_center/analysis.py)

- `plot_population_dynamics(history)` — N_CB, N_CC, N_out vs time
- `plot_affinity_maturation(history)` — mean/max affinity vs time
- `plot_dz_lz_ratio(history)` — DZ/LZ cell count ratio vs time
- `plot_clone_phylogeny(history)` — lineage tree
- `compute_diversity_metrics(history)` — Shannon entropy, clone count

---

## Flow Diagrams (Handoff Documents)

Two detailed flow diagrams have been created:

- **[Flow Diagram A](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/docs/flow_diagram_A_natural_GC.md)** — Natural GC (paper reproduction): 11 blocks, 3D lattice, ~10⁴ cells, paper algorithms 1-9
- **[Flow Diagram B](file:///Users/michaelsedbon/Documents/PhD/projects/synthetic_germinal_center/simulation/docs/flow_diagram_B_bacterial_GC.md)** — Bacterial synthetic GC: 7 blocks + 2 future stubs, well-mixed, ~10⁸ bacteria, 4 selection models

Each maps every block to exact function signatures, input/output data structures, and key parameters.

---

## Verification Plan

### Automated Tests

1. **Affinity unit tests** — `pytest tests/test_affinity.py`
   - Hamming distance: known inputs/outputs
   - Affinity: distance 0 → 1.0, distance 4 → expected value
   - Mutation: output differs in exactly one position by ±1

2. **Initialization checks** — in notebook checkpoint
   - Grid has correct sphere geometry
   - FDCs are in light zone, stromal in dark zone
   - Founder clones at expected Hamming distance

3. **Conservation checks** — in notebook checkpoint
   - Total cell count is tracked (births - deaths = population change)
   - No cells outside the grid sphere
   - Chemokine mass conservation (production - boundary loss)

### Visual Validation (Notebook Checkpoints)

4. **Checkpoint 1**: Grid visualization — 2D slice showing DZ/LZ, FDCs, initial cells
5. **Checkpoint 2**: Chemotaxis — CXCL12/CXCL13 concentration profiles (should show DZ/LZ gradient)
6. **Checkpoint 3**: Movement — cell trajectories show persistent random walk + DZ/LZ bias
7. **Checkpoint 4**: Cell cycle — division rate matches expected doubling time
8. **Checkpoint 5**: Full simulation — population dynamics qualitatively match paper figures

### Quantitative Benchmarks

9. **Population peak**: GC should reach ~1000-3000 cells around day 7-10
10. **Affinity**: Mean affinity should increase ~10-fold over 21 days
11. **DZ/LZ ratio**: Should be ~2:1 (matching experimental data)
