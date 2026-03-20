# Selection Model Analysis for the Synthetic GC

## How Selection Works in the Paper (Natural GC)

In the hyphasma model, selection is **two-stage competitive**:

### Stage 1: Antigen Collection (FDC screening)
- Centrocyte migrates through the Light Zone
- When it encounters an FDC fragment carrying antigen:
  - **Probability of capture** depends on BCR affinity (Gaussian of Hamming distance)
  - Capture increments `nFDCcontacts` (number of antigens internalized)
- This phase is **time-limited** (`collectFDCperiod`, same for all cells)
- Higher affinity → more antigens grabbed in the same time window

### Stage 2: T Cell Help (Competitive)
- After collection, centrocyte searches for a T follicular helper (Tfh)
- When it meets a Tfh:
  - The Tfh cell only signals to **the neighboring B cell with the most antigen** (`nFDCcontacts`)
  - Signal must be sustained for `tcRescueTime` to be rescued
- If no T cell rescue within `tcTime` → **apoptosis**
- This creates a **tournament / competitive** bottleneck

### Result
Selection is effectively: **collect proportionally, then compete locally**. It's not a global tournament — competition is among neighbors of the same T cell. This gives a stochastic, spatially-local selection pressure.

---

## How Selection Works In Your Synthetic GC

### WP1: Bead-Based Selection (Static Antigen)

```
E. coli with nanobody on surface → incubate with antigen-coated magnetic beads
→ wash → pull down with magnet → unbound bacteria die
```

**Mechanism**:
- Each bacterium displays a nanobody variant
- Biotinylated RBD antigen is attached to streptavidin-coated magnetic beads
- Bacteria are mixed with beads
- **Binding probability** depends on nanobody-RBD affinity (Kd)
- Magnetic pulldown retains bound bacteria; washing removes the rest

**This is closest to**: A combination of **proportional** and **threshold**
- Binding is stochastic and affinity-dependent (proportional element)
- The magnet + wash creates a hard cutoff (threshold element)
- Wash stringency (number/volume of washes) tunes the threshold

**Mathematical model**:
```
P(survive) = P(bind_bead) × P(stay_bound_during_wash)

P(bind_bead) ∝ f(affinity, [bead_concentration], incubation_time)

# Simple model: first-order binding kinetics
P(bind) = 1 - exp(-kon × [beads] × t)
P(stay_bound) ∝ exp(-koff × wash_time)

# Where kon is roughly constant and koff depends on affinity:
koff = koff_max × exp(-affinity / kT)   
# Or simply: koff ∝ 1/affinity
```

**Tuneable parameters in the experiment**:
| Parameter | Effect | Analogous GC parameter |
|---|---|---|
| Bead concentration | How many beads per bacterium | Number of FDCs |
| Incubation time | Time to bind | `collectFDCperiod` |
| Wash stringency | Threshold cutoff | T cell help stringency |
| Bead antigen density | Valency / avidity effects | Antigen amount on FDC |

### WP2: Phage Infection Gating (Co-evolving Antigen)

```
E. coli with nanobody → phage (carrying RBD on pIII) must bind nanobody to infect 
→ infection delivers Im3 immunity gene → colicin E3 kills uninfected cells
```

**This is closest to**: **Threshold with proportional gating**
- Phage binds to displayed nanobody → affinity determines infection probability
- Infection = survival (Im3 protects from colicin)
- No infection = death (binary)

**Mathematical model**:
```
P(survive) = P(infected_by_phage)

P(infected) = 1 - exp(-infection_rate × [phage] × t)

# infection_rate ∝ kon(nanobody, RBD) ∝ affinity
```

This is beautifully analogous to the FDC antigen capture step in the paper!

---

## Proposed Selection Models to Implement

For the simulation, I recommend implementing **three selection modes** so you can explore which best matches your experimental system:

### Model A: Soft Proportional (Default)
```python
P(survive) = affinity^n / (affinity^n + K^n)    # Hill function
```
- Parameters: `n` (Hill coefficient = sharpness), `K` (half-max affinity)
- Smooth selection: everyone has a chance, but high affinity is favored
- This is the most biologically realistic for bead assays

### Model B: Hard Threshold
```python
P(survive) = 1 if affinity > threshold else 0
```
- Parameters: `threshold`
- Binary: above threshold lives, below dies
- Good for very stringent washes / colicin kill

### Model C: Tournament (Top-K)
```python
# Sort by affinity, keep top fraction
survivors = top_fraction(population, keep_ratio=0.1)
```
- Parameters: `keep_ratio`
- Exactly reproduces FACS sorting or bead capture with limited beads
- Closest to the T cell help model (competitive)

### Model D: Stochastic Binding + Wash (Physics-Based)
```python
P(bind) = 1 - exp(-kon(affinity) × [beads] × t_incubation)
P(stay)  = exp(-koff(affinity) × t_wash)
P(survive) = P(bind) × P(stay)
```
- Most realistic for bead-based selection
- Parameters directly map to experimental knobs

> **Recommendation**: Implement all four. They're each ~5 lines of code. Use Model A (Hill) as default for parameter sweeps because it has only 2 parameters and captures the essential selection-strength tradeoff.

---

## Selection Stringency and Your Parameter Exploration

Your goal is to run parameter sweeps / genetic algorithms to explore:

| Parameter | Range to explore | What it affects |
|---|---|---|
| Mutation rate | 10⁻⁴ to 10⁻¹ per base per division | Diversity vs. mutational load |
| Selection stringency (K, n) | K: 0.1–0.9, n: 1–10 | Breadth vs. peak affinity |
| Migration frequency | Every 1–24 hours | How often DZ↔LZ transfer |
| Transfer fraction | 1%–50% of population | Bottleneck severity |
| Number of cycles | 1–50 | Total maturation rounds |
| Population size per well | 10⁴–10⁹ | Diversity sampling |

The simulation should output **heatmaps** of:
- Final mean affinity vs. (mutation_rate, selection_stringency)
- Sequence diversity vs. (transfer_fraction, n_cycles)
- Probability of finding >1 distinct epitope vs. (population_size, migration_frequency)
