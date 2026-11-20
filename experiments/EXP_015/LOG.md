# EXP_015 — Log

> Notion is ground truth for the bench record:
> [What does the 2xHA tag cost?](https://app.notion.com/p/41b165923a2180eda332d4007222f04b)
> This log records local work — design decisions, scripts, analysis.

## 2026-11-17 — Experiment opened, bench run, infrastructure built

**DONE — design.** Settled after several rounds of simplification against a hard constraint of
**24 rotor spots**. Scope cut from the original two-question plan (2xHA cost + five-point GFP
titration across three strains) to **MS_S_052 vs MS_S_056 at 100 and 1000 nM, in triplicate,
each against its own uninduced arm**. MS_S_051 not used; a flask was grown and discarded from
the day's plan. Final count **22 labelling tubes = one rotor load**, so every tube sees
identical spin, wash and read timing.

**DONE — arithmetic checked rather than inherited.** EXP_014's depletion figure back-calculates
to **≥38.6 pmol of sites per OD·mL (≥29,000 sites/cell, ≥1.9× Costan's 15,300)**, a *lower*
bound because that arm was ligand-limited. Cell input set at **0.3 OD·mL** from that number:
it is the largest input that keeps the 100 nM arm in ligand excess (20 pmol GFP against
≥11.6 pmol sites = 1.7×).

**DECIDED — standard curve replaces the reference wells.** 8 points, 2-fold from 1000 nM, in
wash buffer at the same 150 µL fill volume as the Tier-1 wells. n = 1 per point is correct: a
curve is self-checking because an outlier shows as a deviation from the line, which is exactly
what a lone reference well cannot do. EXP_014's "GFP reference" wells G5–G7 turned out to
contain no GFP and were caught only by QC.

**DECIDED — read at two gains.** EXP_014 measured 41,511 RFU at 365 nM at gain 100 against a
~65,000 ceiling, so 1000 nM scales to ~114,000. Without a second gain, **all 12 Tier-1 wells
from the 1000 nM rack would return `OVER`** and the bead-capture deliverable with them. Cell
wells off gain 100, Tier 1 and the curve off gain 75; EXP_014's gain100/gain75 = 8.716 (median
residual 1.3 % over three decades) is carried as a **prior, to be refit on this plate**.

**DONE (user) — cultures.** Overnights back-diluted 1:1000 into 30 mL LB + kanamycin.
**OD600 at T+3 h: MS_S_052 0.56, MS_S_056 0.64** (1:10 readings), roughly 2× EXP_014's
induction density of 0.19–0.39.

**ADVISED, outcome not confirmed:** dilute back to OD600 0.30 before the split — it would
restore comparability with EXP_014's growth phase and remove the 14 % density difference
between the two strains being compared. **Whether this was done is not recorded**; left blank
on the Notion page rather than inferred. The harvest ODs (056 running consistently denser than
052) are consistent with the flasks having been split as they were, but that is an inference,
not a record.

**DONE (user) — split and induction.** 12 × **3.1 mL** (planned 4 mL), 6 induced with
**6.70 µL of aTc 100 µM** → 100 ng/mL, 6 uninduced. Arithmetic: 100 µM × 462.9 g/mol =
46.29 ng/µL; 310 ng ÷ 46.29 = 6.70 µL.

**OBSERVED — harvest OD600 at 2.5 h induction** (1:10 readings × 10):

| | A | B | C |
|---|---|---|---|
| 052 induced | 2.4 | **1.7** | 2.7 |
| 052 uninduced | 2.3 | 2.6 | 2.2 |
| 056 induced | 3.0 | 2.7 | 2.9 |
| 056 uninduced | 2.6 | 3.3 | 3.4 |

⚠ **Against EXP_014's harvest range of 1.13–1.61, these cells are at or past the end of
exponential.** Recorded, not corrected. The 052/056 ratio is unaffected — both strains, same
condition, same day — but **pmol per OD·mL will describe late-exponential/stationary cells**,
where display density is no longer dilution-dominated, and is therefore not interchangeable
with a capacity measured in exponential phase.

⚠ **052-I-B at OD600 1.7 is ~30 % below its siblings.** Flagged, not adjusted. Its draw volume
is correspondingly larger.

**DONE — cell input normalised.** `V = 0.3 ÷ OD600` per draw, identical for every labelling
tube including the no-GFP ones, so all 22 reactions hold the same cell number:

| Tube | V (µL) | Tube | V (µL) |
|---|---|---|---|
| 052-I-A | 125 | 056-I-A | 100 |
| 052-I-B | 176 | 056-I-B | 111 |
| 052-I-C | 111 | 056-I-C | 103 |
| 052-U-A | 130 | 056-U-A | 115 |
| 052-U-B | 115 | 056-U-B | 91 |
| 052-U-C | 136 | 056-U-C | 88 |

**DECIDED — scale kept at 0.3 OD·mL / 200 µL** (user question, 2026-11-17). Doubling cells and
label together preserves every excess ratio and would have doubled the pellet and given Tier 1
real margin, but needed 2.4 mL more of 1000 nM parent and there was not enough `PC01538_001`
left. **Doubling cells alone was rejected**: it puts the 100 nM arm at 0.86× excess (20 pmol
against ≥23.2 pmol of sites), i.e. ligand-limited — EXP_014's failure mode and the reason this
experiment exists.

**NOT RUN — the `NC` no-cells carry-through control.** Offered twice, 2 rotor spots were free.
Handling loss therefore remains an upper bound inferred from mass balance, as in EXP_014, where
it sat at an unexplained 17–39 %.

**DONE — plate map built**, 59 wells at 150 µL: 22 cells · 22 Tier 1 · 8 standard curve ·
2 × 100 nM QC · 3 buffer blanks · 2 wash-2 checks.
[data/EXP_015_plate_map.xlsx](data/EXP_015_plate_map.xlsx) from
[scripts/make_plate_map_015.py](scripts/make_plate_map_015.py).
**Wells are ordered dim (row A) → bright (row F)** so the 1000 nM Tier-1 block sits five rows
from the blanks: a black plate holds lateral crosstalk under ~0.1 %, but 0.1 % of 114,000 is
~114 RFU, the same magnitude as the autofluorescence being measured. The same logic sets the
fill order — blanks first, 1000 nM Tier 1 last.

**DONE — analysis notebook built**,
[scripts/EXP_015_analysis.ipynb](scripts/EXP_015_analysis.ipynb), generated by
[scripts/build_notebook_015.py](scripts/build_notebook_015.py). Structure follows EXP_014's:
**QC before any binder is plotted**, then the standard curve, normalisation, the headline
comparison with Welch tests, the uninduced null, Tier 1 → capacity, mass balance, wash
sufficiency, plate-position QC, export.

**DONE — one source of truth.** The layout, run constants, harvest ODs and draw volumes live in
[scripts/exp015_layout.py](scripts/exp015_layout.py); both the plate-map generator and the
notebook import it. EXP_014 kept the layout in two places and they drifted, and a regeneration
of its workbook destroyed hand-entered results — hence the overwrite warning in the generator's
docstring.

**Values still unrecorded** (tracked as `None` in `exp015_layout.py::UNRECORDED`, to fail loudly
rather than be filled in): whether the flasks were diluted back, OD at induction, time aTc
added, harvest time, room temperature, wash-buffer pH, LB formulation, kanamycin concentration.
EXP_014 left the same fields blank and its wash temperature is now unknowable.

## 2026-11-17 (evening) — plate read and analysis

**DONE — plate read**, 18:38–18:43, instrument chamber 26.0 °C. Export saved as
[data/Book1.xlsx](data/Book1.xlsx). OD600 then fluorescence at **three gains: 50, 75 and 100**.

**⚠ DEVIATION — the plate was CLEAR** (Greiner 96 flat bottom transparent, 655101), not the
black/clear-bottom plate the layout assumed. The dim→bright row ordering was designed around a
black plate's ~0.1 % crosstalk specification, which does not apply.

**OBSERVED — crosstalk measured, not assumed.** The layout left E7–E12 and D11–D12 empty
directly above row F, the brightest block (~12,700 RFU blanked at gain 75). Those wells read
**+2 to +4 RFU over blank = 0.03 %**. Negligible; the clear plate cost nothing. This was
available only because the unfilled wells were inside the read area.

**OBSERVED — gain 100 saturates exactly as predicted.** All 12 row-F wells and the top curve
point S1 returned `OVER` at gain 100. Gain 75 carries them. **gain100/gain75 = 8.633** measured
here against EXP_014's 8.716 — reproduced to 0.9 %. gain75/gain50 = 22.940.

**⚠ OBSERVED — the standard curve is sublinear.** RFU per nM falls from 15.8 at 7.8 nM to
12.3 at 1000 nM, a 22 % compression that is monotonic and far outside the noise. A line through
the origin misfits the low end by **+27 %** — precisely where the depleted 100 nM Tier-1
samples sit. Fitted instead as a power law, **RFU = 17.53 · nM^0.9469**, residuals ≤ 4.6 %
across three decades. All concentration conversions use it.

**OBSERVED — the 100 nM working solution measures 94.0 nM** (two wells, 94.2 and 93.8), −6 %
of nominal. Used as C0 for the 100 nM arm in place of the nominal value.

**⚠ OBSERVED — cells did not pellet completely.** Recovery through the washes was ~25–35 % of
input OD·mL against EXP_014's 46 %, and **every Tier-1 and wash supernatant carries cells**
(OD600 0.005–0.028 over blank). Those cells carry bound GFP, which inflates apparent *free*
GFP and so **underestimates capacity**. Corrected directly as
`carried RFU = OD600(supernatant well) × F/OD600(matching cell arm)`; the correction is 6 % of
signal on the 100 nM Tier-1 wells and <0.5 % on the 1000 nM ones. Both corrected and
uncorrected figures are reported.

**⚠ OBSERVED — S1 cannot serve as C0 for the 1000 nM arm.** The uninduced Tier-1 wells read
1026–1085 nM, i.e. **3–8 % above** the S1 standard, giving negative depletion. Those tubes
captured essentially nothing, so their true free concentration *is* the starting concentration;
the offset is systematic between a standard tube and a Tier-1 tube. **C0 for the 1000 nM arm is
therefore taken from the strain-matched uninduced arms**, which cancels it exactly.

### OBSERVED — results

F/OD600, blanked, gain 100, autofluorescence not subtracted (× autofluorescence in brackets):

| | 100 nM | 1000 nM |
|---|---|---|
| MS_S_052 | **31,073 ± 175** (52.4×) | **31,035 ± 718** (52.3×) |
| MS_S_056 | **10,017 ± 277** (15.3×) | **9,928 ± 315** (15.2×) |
| **ratio 052/056** | **3.10×** (Welch p = 3.8 × 10⁻⁷) | **3.13×** (p = 4.7 × 10⁻⁵) |

Triplicate CVs **0.6–3.2 %**.

**OBSERVED — non-specific binding, from the 2 × 2 (± induction, ± GFP).** F/OD600 at 1000 nM:

| | no GFP | +1000 nM | GFP contributes |
|---|---|---|---|
| 052 uninduced | 477 | 724 | **247** |
| 052 induced | 594 | 31,035 | **30,441** |
| 056 uninduced | 512 | 676 | **164** |
| 056 induced | 653 | 9,928 | **9,275** |

Non-specific binding is **0.8 %** (052) and **1.8 %** (056) of the total GFP signal, so
**98–99 % of the readout is induction-dependent display**. Agrees with EXP_014's MS_S_051
intimin null (0.8–1.1× autofluorescence across four aTc doses).

⚠ **Correction to an earlier entry in this log.** The uninduced arms were first reported as
1.52× and 1.32× autofluorescence, with 052's flagged "ELEVATED — leaky display or non-specific
binding". **That framing was wrong and the flag is withdrawn.** Fold-over-autofluorescence on a
near-background well exaggerates a difference of a couple of hundred F/OD600 units; against the
30,441 the induced arm gains, the same number is 0.8 %. The absolute comparison is the correct
one and the null is clean. Figure `data/EXP_015_induction.html` plots it on a log axis, because
on a linear axis the uninduced bars are invisible — which is itself the result.

Display capacity from Tier 1, each strain from the arm where its measurement is honest:

| Strain | Capacity | Sites/cell | From | Depletion |
|---|---|---|---|---|
| MS_S_052 | **41.5 ± 32.9 pmol/OD·mL** | ~31,000 | 1000 nM | 6 % |
| MS_S_056 | **17.4 ± 1.9 pmol/OD·mL** | ~13,100 | 100 nM | 28 % |

**INFERRED — three conclusions.**

1. **The 2xHA tag costs 3.11×, and the cost is identical at 100 and 1000 nM** → it is a
   **display** cost (fewer molecules on the surface), not a binding cost. Had it been a binding
   cost, 056 would have caught up as ligand rose.
2. **Signal is flat between 100 and 1000 nM within each strain** (1000/100 = 1.00 and 0.99) →
   both concentrations are on the plateau, and since they bracket 365 nM, **EXP_014's 365 nM
   was saturating** — when ligand was in excess, which it was not for 052 in EXP_014.
3. **EXP_014's 2.58× was a floor, as predicted.** With GFP in genuine excess it is **3.11×**.

**OBSERVED — two washes were sufficient, but only the OD read proves it.** Raw, the wash-2
supernatants read 32 and 13 RFU above a blank of 27 ± 1.0 — 32 and 13 SD above, which looks
like GFP still coming off. Both wells carry cells, and the carried-cell signal accounts for
**28 of 32** and **10 of 13** RFU; corrected, they sit at +4 and +3 RFU. EXP_014 reached the
same conclusion but could not have distinguished the two explanations, having read no OD on
those wells.

**Each strain has exactly one honest arm, and they are different arms.** At 1000 nM, 056
depletes ~2 %, below the 3–8 % systematic floor — noise. At 100 nM, 052 depletes 75 % —
ligand-limited, so a floor. Cross-check: 056's two arms give 17.4 and 16.9 pmol/OD·mL,
agreeing to 3 %, which validates the method where it can be validated. 052's two arms disagree
by 1.8× exactly as expected from its ligand limitation. **MS_S_052's capacity carries a 79 %
SD** because 6 % depletion is close to the systematic floor; it is the weakest number here.

**Caveat on 052's capacity:** 41.5 pmol/OD·mL from fluorescence-ratio reasoning should be
~3.1 × 17.4 = 54 pmol/OD·mL. The measured 41.5 ± 32.9 covers that, but does not pin it. To
measure 052's capacity properly, label at **300–400 nM**, where it would deplete 20–30 % —
well above the floor and well below ligand limitation.

**DONE — analysis notebook rewritten against the real export** and executed end to end:
[scripts/EXP_015_analysis.ipynb](scripts/EXP_015_analysis.ipynb). Outputs
`EXP_015_tidy.csv`, `EXP_015_summary.csv`, `EXP_015_tier1.csv`, `EXP_015_ratios.csv`, and the
figures `EXP_015_readout.html`, `EXP_015_tier1.html`, `EXP_015_curve.html`,
`EXP_015_plate_heatmap.html`.

**PENDING:** the `MS_96WP` registry row for this plate; transcription of the headline numbers
onto the Notion page; the parent project summary. Still unrecorded from the bench: whether the
flasks were diluted back, OD at induction, time aTc added, harvest time, **room temperature
during labelling** (the 26.0 °C in the file is the instrument chamber at read time, not the
same thing), wash-buffer pH, LB formulation, kanamycin concentration.
