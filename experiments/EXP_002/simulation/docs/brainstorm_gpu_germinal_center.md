# Brainstorm: GPU-Ready Synthetic Germinal Center Simulation

## Context

**Paper**: Robert et al. — *How to Simulate a Germinal Center* (hyphasma model)
**Your proposal**: Maimonide 2026 — Synthetic GC in *E. coli* for nanobody affinity maturation

**Goal**: Reproduce the hyphasma agent-based GC model, then adapt it to simulate the bacterial "immune side" of your synthetic GC (mutating bacteria carrying nanobody variants, selection, migration between dark/light zones). GPU-ready for large populations.

---

## 1. What the Paper Models (Summary)

The hyphasma model is an **agent-based model (ABM)** on a 3D lattice:

| Component | Description |
|---|---|
| **Grid** | 3D cubic lattice (~80³), each point = 5 µm. GC is a sphere in the center. |
| **Agents** | Centroblasts (DZ), Centrocytes (LZ), T cells, FDCs, stromal cells, output cells |
| **BCR/Antigen** | Shape space of L=4 integers. Affinity = Gaussian of Hamming distance. |
| **Chemotaxis** | CXCL12 (→DZ) and CXCL13 (→LZ) with diffusion + desensitization |
| **Movement** | Persistent random walk with polarity, biased by chemokine gradients |
| **Cell cycle** | G1 → S → G2 → M division, with timed phases |
| **Mutation** | At division: ±1 on one shape-space coordinate |
| **Selection** | Centrocytes collect antigen from FDCs (affinity-dependent), then compete for T cell help (best antigen presenter wins) |
| **Differentiation** | Selected cells recycle to DZ (centroblasts) or exit as output/plasma cells |
| **Antibody feedback** | Output cells produce antibodies that mask FDC antigens |

### Key Algorithms from the Paper
1. **Algorithm 1** — Mutation (shape space ±1)
2. **Algorithm 2** — Chemotaxis receptor updating (sensitization/desensitization)
3. **Algorithm 3** — Cell movement (persistent random walk + gradient following)
4. **Algorithm 4** — Cell cycle progression (G1→S→G2→M→division)
5. **Algorithm 5** — Antigen collection from FDCs (affinity-dependent capture)
6. **Algorithm 6** — T cell help screening (competitive signaling)
7. **Algorithm 7** — T cell updating (synapse repolarization to best B cell)
8. **Algorithm 8** — Differentiation/recycling/output transitions
9. **Algorithm 9** — Model initialization

---

## 2. Mapping to Your Synthetic GC

Your proposal describes a **bacterial synthetic GC** with:

| Natural GC (paper) | Your Synthetic GC |
|---|---|
| B cells with BCR | *E. coli* displaying nanobody on surface (intimin) |
| Somatic hypermutation | T7 polymerase + error-prone replication (DZ) / MP6 mutagenesis |
| Antigen on FDCs | Biotinylated SARS-CoV-2 RBD on magnetic beads (WP1) or M13 phage-displayed RBD (WP2) |
| Affinity-based selection | Flow cytometry / bead capture / phage infection gating |
| T cell help (competitive) | Colicin E3–Im3 survival signal / growth-based selection |
| DZ ↔ LZ migration | Physical transfer between culture wells (robotic) |
| Clonal expansion | Bacterial growth + division |
| Output / plasma cells | Sequenced, characterized nanobody clones |

### Phase 1 Focus: Immune Side (Bacteria)
Simulate the **bacterial population** undergoing:
- Mutation (error-prone replication modifying a nanobody sequence)
- Selection (affinity-dependent survival/growth)
- Migration (transfer between DZ and LZ compartments)
- Population dynamics (growth, death, bottlenecks)

### Phase 2 (later): Antigen Drift
Add co-evolution of the antigen (phage-displayed RBD mutating under nanobody pressure).

---

## 3. Key Architecture Decisions

### 3.1 Language & Framework

| Option | Pros | Cons |
|---|---|---|
| **Python + JAX** | Easy prototyping, JIT to GPU, vmap for vectorization, great for science | Lattice ABM with exclusion is hard to parallelize |
| **Python + CuPy/Numba** | Close to NumPy, CUDA kernels when needed | Less elegant than JAX, manual kernel management |
| **CUDA C++** | Maximum GPU performance, full control | Slow development, hard to debug |
| **Julia + CUDA.jl** | Fast like C, easy like Python, Agents.jl for ABM | Smaller ecosystem, less GPU ABM tooling |
| **Python + Taichi** | Domain-specific language for particle/grid simulations, GPU native | Newer, less community support |

> [!IMPORTANT]
> **Recommendation: Python + JAX** for the primary implementation.
>
> **Rationale**: JAX gives you GPU acceleration with a Python-friendly API. The key insight is that you don't need to replicate the exact lattice-exclusion ABM on GPU — you can reformulate the model using **Structure of Arrays (SoA)** particle representation where each bacterium is a row in a large array. The grid is only needed for neighbor lookups (which can use spatial hashing). This is a well-known pattern for GPU particle simulations.

### 3.2 The GPU Parallelization Challenge

The original hyphasma is a **serial lattice ABM**: one cell per grid point, sequential updates. This is inherently hard to parallelize because:

1. **Exclusion constraint**: Two cells can't occupy the same grid point → race conditions on GPU
2. **Interaction dependency**: T cell selection depends on which B cell has the most antigen → reduction operations
3. **State-dependent transitions**: Cell state changes depend on neighbors

**Three strategies to handle this:**

#### Strategy A: Reformulate as Particle-Based (Recommended for your case)
- Bacteria are particles with positions, not grid-locked
- Interactions computed via spatial neighbor lists (Cell Lists / spatial hashing)
- No exclusion constraint needed (bacteria in liquid culture don't have lattice exclusion)
- **This maps perfectly to your biological system** — bacteria in a well-mixed culture don't sit on a lattice

#### Strategy B: Lattice-Based with Red-Black Updating
- Checkerboard decomposition: update even/odd sites alternately → no conflicts
- Faithful to the paper's model but less natural for bacteria

#### Strategy C: Hybrid — GPU for population, CPU for interactions
- GPU handles mutation, growth, movement (embarrassingly parallel)
- CPU handles selection events (small population after bottleneck)

> [!TIP]
> **Strategy A is strongly recommended** because your system doesn't need a spatial lattice. The GC paper uses a lattice because immune cells physically crawl through tissue. Your bacteria are in liquid culture — position doesn't matter, only genotype and compartment (DZ vs LZ).

### 3.3 Data Representation

```
# Structure of Arrays — each array has length N_bacteria
sequences:     int32[N, L]       # Shape space (or actual nt sequence)
affinities:    float32[N]        # Pre-computed affinity to antigen
compartment:   int8[N]           # 0=DZ, 1=LZ, 2=output
state:         int8[N]           # cell cycle phase / selection state
clocks:        float32[N, K]     # Various timers per cell
clone_id:      int32[N]          # Lineage tracking
parent_id:     int32[N]          # For tree reconstruction
generation:    int32[N]          # Division count
alive:         bool[N]           # Dead/alive mask
antigen_collected: int32[N]      # FDC contacts equivalent
```

### 3.4 Sequence Representation: Shape Space vs. Real Sequence

| Approach | Detail | GPU-friendly? |
|---|---|---|
| **Shape space (L=4)** | Paper's approach. Each BCR = 4 integers, affinity = Gaussian(Hamming). | ✅ Trivial on GPU |
| **Binary string (L=50–200)** | More realistic. BCR = bitstring, affinity via bit matching. | ✅ Bitwise ops are fast |
| **NK landscape** | Tunable ruggedness. More realistic fitness landscape. | ✅ Lookup table on GPU |
| **Actual nucleotide sequence** | Real nanobody CDR sequences (~300–400 nt). Affinity needs a surrogate model. | ⚠️ Needs ML surrogate |

> [!NOTE]
> **Start with shape space (L=4)** to reproduce the paper. Then extend to longer binary strings or NK landscapes for your synthetic GC. Real nucleotide sequences only make sense with a trained affinity predictor, which is a separate project.

---

## 4. Proposed Simulation Architecture

```
┌─────────────────────────────────────────────────┐
│              SIMULATION ENGINE (JAX)             │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐  │
│  │  CONFIG   │    │  STATE   │    │  HISTORY  │  │
│  │ (params)  │    │ (arrays) │    │ (traces)  │  │
│  └──────────┘    └──────────┘    └───────────┘  │
│                                                  │
│  Per-timestep pipeline:                          │
│  ┌────────────────────────────────────────────┐  │
│  │ 1. grow_and_divide()     [DZ cells]        │  │
│  │ 2. mutate()              [new daughters]   │  │
│  │ 3. migrate_dz_to_lz()   [stochastic]      │  │
│  │ 4. collect_antigen()     [LZ cells]        │  │
│  │ 5. compete_for_help()    [LZ cells]        │  │
│  │ 6. select_or_die()       [LZ cells]        │  │
│  │ 7. differentiate()       [selected cells]  │  │
│  │ 8. migrate_lz_to_dz()   [recyclers]       │  │
│  │ 9. update_antibody_feedback() [optional]   │  │
│  │10. compact_arrays()      [remove dead]     │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │ ANTIGEN MODULE (Phase 2 — stub for now)    │  │
│  │ - antigen_mutate()                         │  │
│  │ - antigen_selection()                      │  │
│  │ - recompute_affinities()                   │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
├─────────────────────────────────────────────────┤
│  OUTPUTS:                                        │
│  - Population traces (N_DZ, N_LZ, N_out vs t)   │
│  - Affinity distribution over time               │
│  - Clone phylogenies                             │
│  - Sequence diversity metrics                    │
└─────────────────────────────────────────────────┘
```

---

## 5. Development Plan

### Phase 0: Reproduce the Paper (Validation)
Reproduce hyphasma results from the paper using the exact shape space + parameters:
1. GC population dynamics (Fig. in paper showing cell counts over time)
2. Affinity maturation curve
3. Dark zone / light zone ratio dynamics

### Phase 1: Adapt to Bacterial Synthetic GC
Remap the model to your bacterial system:
- Replace lattice movement with well-mixed compartments
- Replace FDC antigen presentation with bead-based selection
- Replace T cell help with growth-advantage selection
- Add realistic bacterial growth kinetics (doubling time, carrying capacity)
- Add experimental bottlenecking (transfer volume)

### Phase 2: GPU Scaling
- Profile bottlenecks (mutation, selection, compaction)
- Optimize for N > 10⁶ bacteria
- Benchmark on your available GPU

### Phase 3: Antigen Co-evolution (later)
- Add phage population with its own mutation/selection dynamics
- Cross-interaction: nanobody affinity determines phage fitness and vice versa

---

## 6. Open Questions for Discussion

1. **Sequence representation**: Should we start with shape space (L=4) to validate against the paper, or jump directly to a longer binary representation more relevant to your system? I recommend shape space first.

2. **Spatial structure**: The paper models a 3D GC with cell movement. Your bacterial system is well-mixed within each compartment. Should we still keep a spatial component (e.g., for colony structure on plates), or go fully well-mixed?

3. **Selection model**: The paper uses competitive T cell help (best antigen presenter wins). In your system, how does selection work exactly? Is it:
   - (a) Threshold-based (affinity above X survives)
   - (b) Proportional (higher affinity = higher survival probability)
   - (c) Tournament (top-K survive per round)

4. **Population sizes**: What are the target population sizes you want to simulate? 10⁴ (easy), 10⁶ (moderate on GPU), 10⁸ (needs careful engineering)?

5. **Deliverable format**: You mentioned both a Jupyter notebook (for step-by-step debugging) and standalone code. Should the standalone be:
   - (a) A Python package with CLI
   - (b) A compiled CUDA/C++ binary
   - (c) Both — Python+JAX as primary, with C++ fallback if JAX is too slow

6. **Validation metrics**: What experimental data do you already have (or expect) to validate the simulation against?

---

## 7. Recommended Next Steps

1. **Agree on architecture** — Review this brainstorm, settle on language (JAX), representation (shape space), and spatial model (well-mixed compartments)
2. **Build the flow diagram** — Complete block-by-block simulation flow with function signatures
3. **Implement Phase 0** — Reproduce paper results (notebook + standalone)
4. **Checkpointed notebook** — Each block independently testable with assertions on expected behavior
5. **Adapt for your system** — Swap components block-by-block for bacterial parameters
