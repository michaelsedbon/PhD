# EXP_015 — What does the 2xHA tag cost? GFP titration to saturation

| Field | Value |
|-------|-------|
| **Status** | ✅ Complete — 2026-11-17. **The 2xHA tag costs 3.1× of display, not of binding** |
| **Started** | 2026-11-17 |
| **Project** | [Synthetic Germinal Center](../../projects/synthetic_germinal_center/summary.md) — subsystem 1, display |
| **Notion (ground truth)** | [What does the 2xHA tag cost?](https://app.notion.com/p/41b165923a2180eda332d4007222f04b) |
| **Predecessor** | [EXP_014](../EXP_014/summary.md) — display confirmed, 57.9× over autofluorescence |
| **Strains** | MS_S_052 (Enhancer, no HA), MS_S_056 (Enhancer + 2xHA) |
| **Antigen** | eGFP-GSG-His6-GSGGS-AviTag, A206 wild type, prep `PC01538_001` |
| **Equipment** | Tecan Infinite 200 Pro |

> **Notion is ground truth for this experiment.** The bench record, registry rows and all
> observations live on the Notion page above. This folder holds analysis, scripts and figures.

---

## Overview

EXP_014 established that the Neae intimin display platform works in our hands and that
**MS_S_052 (no HA) reads 2.58× higher than MS_S_056 (+2xHA)**. That figure is not trustworthy:
the 052 arm **stripped 98.3 % of its GFP bath**, so it was ligand-limited and 2.58× is a floor
rather than a measurement.

This experiment repeats the comparison with **GFP in genuine excess**, in triplicate, at two
concentrations that bracket EXP_014's 365 nM.

## Goal

| # | Question | How it is answered |
|---|----------|--------------------|
| Q1 | Does the 2xHA tag cost **display** or **binding**? | ratio 052/056 at 100 vs 1000 nM — equal ratio = display cost, shrinking ratio = binding cost |
| Q2 | Was EXP_014's 365 nM saturating? | within a strain, signal at 100 ≈ 1000 nM means both are on the plateau, and 365 nM lies between them |
| Q3 | **What is the absolute display capacity?** | Tier 1 supernatant against a standard curve → **pmol captured per OD·mL** |

Q3 is the deliverable that feeds the next step: sizing bead capture (antigen per cell, beads
per cell). EXP_014 could only bound it from below at **≥38.6 pmol per OD·mL (≥29,000 sites
per cell)**.

## Design

| Parameter | Value | Why |
|---|---|---|
| Cell input | **0.3 OD·mL** per labelling tube | set by the 100 nM arm: 20 pmol GFP against ≥11.6 pmol sites = 1.7× excess. More cells would make it ligand-limited, which is EXP_014's failure |
| Label | **200 µL**, 30 min, room temperature | |
| GFP | **100 and 1000 nM** | bracket EXP_014's 365 nM; 1000 nM gives ~17× excess |
| Null | **uninduced arm of each strain** | strain-matched — same cells, same plasmid, same handling; better matched than MS_S_051 for a 052-vs-056 comparison |
| Replication | **n = 3** per strain per state | split replicates from one flask, **not** biological |
| Standard curve | **8 points, 2-fold from 1000 nM** | converts Tier 1 into nM directly rather than a depletion fraction against one reference well |
| Reader | ex 478 / em 515, BOTTOM, **gain 100 and gain 75** | 1000 nM reads ~114,000 at gain 100 against a ~65,000 ceiling — all 12 Tier-1 wells from that rack would return `OVER` |

**22 labelling tubes = one rotor load**, so every tube sees identical spin, wash and read
timing and there is no differential signal decay between batches.

## Progress

| Date | What |
|------|------|
| 2026-11-17 | Experiment opened. Design settled after several rounds of simplification against a 24-spot rotor limit. Flasks back-diluted 1:1000 into 30 mL; **OD600 0.56 / 0.64 at T+3 h**, roughly 2× EXP_014's induction density. Split into 12 × 3.1 mL, induced 6 with 6.70 µL aTc 100 µM → 100 ng/mL. **Harvest OD600 2.2–3.4** at 2.5 h. 22 labelling tubes at 0.3 OD·mL each. |
| 2026-11-17 (pm) | **Plate read and analysed.** 59 wells, three gains (50/75/100), 26.0 °C. **Result: the 2xHA tag costs 3.11×, identically at 100 and 1000 nM — a display cost.** Four deviations handled in the analysis: clear plate (crosstalk measured at 0.03 %, negligible), gain 100 saturated on all 12 row-F wells as predicted, standard curve sublinear (power-law fit; a line through the origin misfits the low end by 27 %), and incomplete pelleting (cells in every supernatant, corrected). |

## Results

**The 2xHA tag costs 3.1× of display.** Plate read 2026-11-17, gain 100 for cell wells,
gain 75 for everything cell-free. F/OD600, blanked (× autofluorescence in brackets):

| | 100 nM | 1000 nM |
|---|---|---|
| MS_S_052 (no HA) | **31,073 ± 175** (52.4×) | **31,035 ± 718** (52.3×) |
| MS_S_056 (+2xHA) | **10,017 ± 277** (15.3×) | **9,928 ± 315** (15.2×) |
| **ratio 052 / 056** | **3.10×** (p = 3.8 × 10⁻⁷) | **3.13×** (p = 4.7 × 10⁻⁵) |

Triplicate CVs 0.6–3.2 %.

Three findings:

1. **The cost is identical at 100 and 1000 nM, so it is a *display* cost** — fewer molecules on
   the surface. A binding cost would have let 056 catch up as ligand rose; it does not.
2. **Signal is flat between 100 and 1000 nM within each strain** (ratios 1.00 and 0.99), so both
   are on the plateau. Since they bracket 365 nM, **EXP_014's 365 nM was saturating** — given
   ligand in excess, which it was not for 052 in EXP_014.
3. **EXP_014's 2.58× was a floor, exactly as predicted.** With GFP in genuine excess it is
   **3.11×**.

**Display capacity** from Tier 1 against the standard curve, each strain taken from the arm
where its measurement is honest:

| Strain | Capacity | Sites/cell | From | Depletion |
|---|---|---|---|---|
| MS_S_052 | 41.5 ± 32.9 pmol/OD·mL | ~31,000 | 1000 nM | 6 % |
| MS_S_056 | **17.4 ± 1.9 pmol/OD·mL** | **~13,100** | 100 nM | 28 % |

MS_S_056's figure is the solid one, and it sits close to Costan 2024's 15,300 adhesins/cell.
**MS_S_052's carries a 79 % SD** and should not be quoted as a measurement — see the caveat
below.

**The signal is induction-dependent.** Each strain was run as a 2 × 2 (± induction, ± GFP), so
non-specific binding is measurable directly rather than inferred:

| | no GFP | +1000 nM | GFP contributes |
|---|---|---|---|
| 052 uninduced | 477 | 724 | **247** |
| 052 induced | 594 | 31,035 | **30,441** |
| 056 uninduced | 512 | 676 | **164** |
| 056 induced | 653 | 9,928 | **9,275** |

Non-specific binding is **0.8 %** of signal for 052 and **1.8 %** for 056, agreeing with
EXP_014's MS_S_051 intimin null (0.8–1.1× autofluorescence across four aTc doses).
Figure: `data/EXP_015_induction.html`, log y-axis.

**Two washes were sufficient**, but only the OD600 read proves it: raw, the wash-2 supernatants
read 32 and 13 RFU above a blank of 27 ± 1.0, which looks like carryover. Both wells contain
cells, and the carried-cell signal accounts for 28 of 32 and 10 of 13 RFU. Corrected, both sit
at the blank.

Figures: `data/EXP_015_readout.html`, `data/EXP_015_tier1.html`, `data/EXP_015_curve.html`,
`data/EXP_015_plate_heatmap.html`. Analysis:
[scripts/EXP_015_analysis.ipynb](scripts/EXP_015_analysis.ipynb).

## Caveats on the result

| Caveat | Detail |
|---|---|
| **MS_S_052's capacity is not pinned** | At 1000 nM it depletes only 6 %, close to the 3–8 % systematic offset between a standard tube and a Tier-1 tube. SD is 79 %. The fluorescence ratio implies ~54 pmol/OD·mL; the measurement covers that but does not establish it. **To measure it properly, label at 300–400 nM** — 20–30 % depletion, above the floor and below ligand limitation |
| **Each strain has only one honest arm** | At 1000 nM, 056 depletes ~2 % (noise). At 100 nM, 052 depletes 75 % (ligand-limited, a floor). Cross-check: 056's two arms agree to 3 % (17.4 vs 16.9), which validates the method where it can be validated |
| **Non-specific binding is negligible** | The uninduced arms read 1.52× (052) and 1.32× (056) autofluorescence, which sounds elevated but is the wrong frame. In absolute terms GFP adds 247 and 164 F/OD600 to uninduced cells against 30,441 and 9,275 to induced ones — **0.8 % and 1.8 % of signal**. 98–99 % of the readout is induction-dependent display |
| **Capacity describes stationary-phase cells** | Harvest OD 2.2–3.4 against EXP_014's 1.13–1.61 |
| **Cells did not pellet completely** | ~25–35 % OD recovery against EXP_014's 46 %; every supernatant carries cells. Corrected for explicitly, but it is why the 100 nM Tier-1 numbers needed a 6 % adjustment |
| **Mass balance: 39–68 % recovery** | The GFP on the cells accounts for only 39–68 % of what left the bath (`EXP_015_calibration.html`), i.e. **32–61 % is lost through the two washes** — worse than EXP_014's inferred 17–39 %. **This does not affect capacity**, which is measured from the bath *before* washing, nor the 052/056 ratio, since both strains are washed identically. It does mean the cell-side fluorescence is not a route to absolute capacity. The `NC` no-cells control would have measured the loss directly; it was offered twice and not run |

## On the record

| Item | Note |
|---|---|
| **Harvest OD 2.2–3.4** | against EXP_014's 1.13–1.61 — at or past the end of exponential. The 052/056 ratio is unaffected (same condition both strains), but **pmol per OD·mL describes late-exponential/stationary cells** and is not interchangeable with a figure measured in exponential phase |
| **052-I-B at OD 1.7** | ~30 % below its siblings (2.4, 2.7). Flagged, not adjusted |
| **Scale not raised** | doubling cells and label together was rejected for lack of `PC01538_001`; doubling cells alone was rejected because it puts the 100 nM arm at 0.86× excess |
| **`NC` handling control not run** | the no-cells carry-through tube was offered and declined, so handling loss stays an upper bound inferred from mass balance, as in EXP_014 (17–39 %, unexplained) |
| **Clear plate, not black** | Greiner 655101 flat-bottom transparent. The dim→bright row ordering was designed around a black plate's ~0.1 % crosstalk spec. Crosstalk was therefore **measured** from the unfilled wells beside row F: **+2 to +4 RFU on a ~12,700 RFU neighbour = 0.03 %**. Negligible — nothing is affected |
| **Standard curve is sublinear** | RFU/nM falls 22 % from 7.8 to 1000 nM, monotonic and far outside noise. Fitted as `RFU = 17.53 · nM^0.9469` (residuals ≤ 4.6 %). A line through the origin would have overstated the low end by 27 %, exactly where the depleted Tier-1 samples sit |
| **S1 is not usable as C0 at 1000 nM** | The uninduced Tier-1 wells read 3–8 % *above* S1, giving negative depletion. C0 is taken from the strain-matched uninduced arms instead, which cancels the offset |
| **100 nM solution measured 94.0 nM** | −6 % of nominal; used as C0 rather than the nominal value |
| **Gain ratio reproduced** | gain100/gain75 = **8.633** here against EXP_014's 8.716, 0.9 % apart |
| **Still unrecorded** | whether the flasks were diluted back before the split, OD at induction, time aTc added, harvest time, **room temperature during labelling** (the 26.0 °C in the export is the instrument chamber at read time, not the same thing), wash-buffer pH, LB formulation, kanamycin concentration. Tracked in `scripts/exp015_layout.py::UNRECORDED` |
| **PC01538_001 MW** | the prep's own mg/mL and mM imply 33.3 kDa against 30.12 kDa from the sequence. All concentrations computed from the sequence MW; the error is systematic and cancels in the 052/056 ratio |

## Document Index

| Document | Description |
|----------|-------------|
| [summary.md](summary.md) <span style="background:#1a6fff;color:#fff;padding:2px 8px;border-radius:12px;font-size:11px">Main</span> | This file — overview, goal, design, progress |
| [LOG.md](LOG.md) <span style="background:#d29922;color:#0d1117;padding:2px 8px;border-radius:12px;font-size:11px">Log</span> | Chronological work log |
| [DOC_INDEX.md](DOC_INDEX.md) <span style="background:#66bb6a;color:#0d1117;padding:2px 8px;border-radius:12px;font-size:11px">Reference</span> | Index of all markdown files |
| [SCRIPT_INDEX.md](SCRIPT_INDEX.md) <span style="background:#66bb6a;color:#0d1117;padding:2px 8px;border-radius:12px;font-size:11px">Reference</span> | Index of scripts and data files |

## References

Carried from [EXP_014](../EXP_014/summary.md), all verified in the local library per the
verify-before-citing rule. No new citations are introduced by this experiment.

| Paper | Relevance |
|-------|-----------|
| Costan et al. 2024, *Matter* 7(6):2125–2143, [10.1016/j.matt.2024.03.019](https://doi.org/10.1016/j.matt.2024.03.019) | Characterises pDSG339 = MS_C_019; aTc → adhesins-per-cell calibration (15,300/cell at 300 ng/mL); the 365 nM labelling protocol |
| Kirchhofer et al. 2010, *Nat Struct Mol Biol* 17:133–138, [10.1038/nsmb.1727](https://doi.org/10.1038/nsmb.1727) | Enhancer/GBP1 structure; ~1.5× eGFP fluorescence enhancement on binding |
| Kubala et al. 2010, *Protein Sci* 19:2389–2401, [10.1002/pro.519](https://doi.org/10.1002/pro.519) | GFP:nanobody thermodynamics — Kd 1.4 nM, koff 1.24 × 10⁻⁴ s⁻¹ (t½ 93 min) |
| Zacharias et al. 2002, *Science*, [10.1126/science.1068539](https://doi.org/10.1126/science.1068539) | Wild-type GFP dimer Kd = 0.11 mM — the basis for the ≤ 1 µM working ceiling |
| Fridy et al. 2014, *Nat Methods*, [10.1038/nmeth.3170](https://doi.org/10.1038/nmeth.3170) | LaG affinity ladder; Enhancer Kd 1.4 nM |
