# Scientific Questions — Synthetic GC Simulation

Core scientific questions from the Maimonide proposal to investigate with the simulation.
Directly maps to the grant's **Specific Aim 1**: *"Determine how mutation rate, selection stringency, and dark-zone/light-zone cycling frequency interact to shape repertoire clonal breadth and depth of affinity maturation."*

---

## Q1. How Does Mutation Rate Affect Affinity vs. Diversity?

**Background**: The proposal uses **T7 replisome** with 5 polymerase variants spanning mutation rates from **10⁻⁸ to 10⁻⁵ sub/base/replication**. At peak rate on a 360 bp nanobody gene: **~1 mutation per lineage every 10h** under continuous turbidostat culture.

**Question**: What is the optimal mutation rate that maximises affinity maturation while maintaining clonal diversity? Is there a critical threshold where diversity collapses?

**Sweep**: `mutation_rate` ∈ {10⁻⁵, 10⁻⁴, 10⁻³, 10⁻², 10⁻¹} × 20 cycles → measure (mean affinity, Shannon entropy)

**Prediction**: Too low → no evolution. Too high → error catastrophe (beneficial mutations destroyed). Expect a Goldilocks zone.

---

## Q2. How Does Selection Stringency Shape Breadth vs. Depth?

**Background**: Bead-based selection in LZ. Stringency controlled by bead concentration, wash time, and antigen density.

**Question**: Does strong selection (hard threshold) sacrifice breadth for speed? Does weak selection (low Hill K) maintain diversity but evolve too slowly?

**Sweep**: Hill K ∈ {0.1, 0.2, 0.3, 0.5, 0.7} × Hill n ∈ {1, 3, 5, 10}

**Prediction**: Strong selection → fast affinity gain but single-clone dominance. Weak selection → slow but polyclonal. The GC architecture should find a sweet spot.

---

## Q3. How Does DZ/LZ Cycling Frequency Affect the GC?

**Background**: Migration from DZ to LZ occurs after N divisions. Faster cycling = more frequent selection. Slower cycling = more mutations per selection round.

**Question**: What is the optimal number of DZ divisions before selection? Does frequent cycling prevent clone escape or does it kill diversity too fast?

**Sweep**: `dz_divisions` ∈ {2, 4, 6, 8, 12, 20}

**Prediction**: Rare migration (many DZ div) → population drifts, selection can't steer. Frequent migration (few DZ div) → not enough mutations between selections, population stagnates.

**Update (2026-03-17)**: Sweep results show Muller's ratchet dominates at high mutation rates. More frequent DZ→LZ cycling (`dz_divisions=2` instead of 6) could apply more frequent purifying selection, potentially countering mutation load. This is now a **high-priority parameter** to sweep alongside mutation rate. Current default `dz_divisions=6` means only 2 selection events per cycle — reducing to 2 would give 6 selection events.

---

## Q4. How Does Population Size Affect Diversity Maintenance?

**Background**: Natural GC has ~10³–10⁴ B cells. Bacterial GC has **~10⁸ cells per well** (10⁴–10⁵× larger). Proposal says this enables "10⁶-fold more mutational exploration."

**Question**: Does larger population maintain more diverse clones? Is there a minimum population below which diversity collapses? Does the advantage scale linearly or plateau?

**Sweep**: `turbidostat_target_n` ∈ {10³, 10⁴, 10⁵, 10⁶} × 20 cycles

**Prediction**: Larger populations buffer against genetic drift → maintain more unique clones → explore more of the fitness landscape simultaneously.

---

## Q5. Does the DZ/LZ Architecture Outperform Simple Directed Evolution?

**Background**: Standard directed evolution = grow → select → grow (no DZ/LZ separation, no controlled migration). The GC adds compartmentalisation.

**Question**: Does the GC architecture produce broader repertoires than an equivalent number of growth+selection cycles without compartmentalisation?

**Experiment**: Run bacterial sim vs. a "flat" control (no DZ/LZ, just grow-select-grow with same total cells and cycles). Compare Shannon entropy and number of distinct high-affinity clones.

**Prediction**: GC architecture should maintain more diversity (the key claim of the proposal).

---

## Q6. Can the GC Maintain Multiple Epitope Specificities?

**Background**: Proposal goal: *"broadly neutralising repertoires"* covering multiple epitopes on RBD.

**Question**: With multiple antigen targets (epitopes), does the GC maintain clones solving each, or does one peak dominate?

**Experiment**: Place 3 antigens at different positions in shape space. Run 20 cycles. Measure how many antigens have at least one high-affinity clone.

**Prediction**: With soft selection (Hill), multiple peaks can be explored simultaneously. With hard selection, the closest peak dominates.

---

## Q7. Does Returning Unselected Cells to DZ Help?

**Background**: In natural GCs, unselected centrocytes die by apoptosis. In bacteria, we could choose to return some unselected cells.

**Question**: Does `unselected_return_fraction > 0` help maintain diversity without killing affinity maturation?

**Sweep**: `unselected_return_fraction` ∈ {0, 0.1, 0.3, 0.5, 1.0}

**Prediction**: Small fraction (0.1) may help maintain rare clones. Too much (>0.5) dilutes selection signal.

---

## Q8. Antigen Evolution — Does Prior Adaptation Speed Re-Adaptation?

**Background**: WP2 couples GC to evolving antigen. WP3 future: immune memory.

**Question**: If antigen mutates at cycle N/2, how fast does the repertoire re-adapt? Does seeding from a previous GC output accelerate adaptation?

**Status**: Future experiment (Phase 2)

---

## Q9. What Is the Shape of the Affinity Landscape?

**Background**: Current model uses Gaussian affinity on Hamming distance — smooth, single peak per antigen.

**Question**: How sensitive are results to the affinity landscape shape? Does a rugged landscape (many local optima) change the mutation rate vs. diversity relationship?

**Status**: Requires landscape model extension

---

## Q10. How Do 96 Parallel Wells Interact?

**Background**: Proposal uses 96-well format to maintain independent sub-populations.

**Question**: Does occasional inter-well migration (sharing clones between plates) improve overall coverage vs. fully independent wells?

**Status**: Future (Phase 3)

---

## Q11. How Much Does Initial Library Affinity Matter?

**Background**: Founders start with random Hamming distance from antigen (`initial_hamming_min` to `initial_hamming_max`). Higher initial affinity (closer to antigen) means mutations are more likely to be deleterious (more positions to worsen than improve). Lower initial affinity gives more room to improve but requires more cycles.

**Question**: Does starting with a higher-affinity library accelerate maturation or does it just raise the floor without changing dynamics? Is there a sweet spot where founders are close enough to benefit from selection but far enough to have beneficial mutations available?

**Sweep**: `initial_hamming_min/max` ∈ {10-30, 30-60, 50-100, 100-200} at L=400

**Prediction**: Too far (low affinity) → selection can't distinguish clones, drift dominates. Too close (high affinity) → most mutations are deleterious, Muller's ratchet kicks in faster. There should be an optimal initial distance.
