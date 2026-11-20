# EXP_015 — Script & Data Index

## Scripts

| File | Purpose |
|------|---------|
| [scripts/exp015_layout.py](scripts/exp015_layout.py) | **Single source of truth.** Run constants, the 59-well layout, harvest ODs, draw volumes, EXP_014 priors, and the `UNRECORDED` dict of values the bench has not yet supplied. Everything else imports it. Run standalone to print the draw volumes and what is still missing |
| [scripts/make_plate_map_015.py](scripts/make_plate_map_015.py) | Generates the plate-map workbook from the layout module. ⚠ **Re-running OVERWRITES the workbook** — in EXP_014 a regeneration destroyed hand-entered results |
| [scripts/build_notebook_015.py](scripts/build_notebook_015.py) | Generates the analysis notebook. ⚠ Re-running overwrites it; move anything hand-typed into the layout module first |
| [scripts/EXP_015_analysis.ipynb](scripts/EXP_015_analysis.ipynb) | Analysis: QC → standard curve → normalisation → 052 vs 056 → uninduced null → Tier 1 capacity → mass balance → wash check → position QC → export |
| [scripts/tecan_parse.py](scripts/tecan_parse.py) | Tecan i-control `.xlsx` parser, copied unchanged from EXP_014. Handles plate blocks and wavelength scans, maps `OVER` to NaN (never 0), raises on an ambiguous block match |

**Running the notebook** — no system Python here has pandas:

```bash
uv run --with pandas,numpy,plotly,scipy,openpyxl jupyter lab
```

## Data

| File | Description |
|------|-------------|
| [data/EXP_015_plate_map.xlsx](data/EXP_015_plate_map.xlsx) | 4 sheets — `Plate map` (colour-coded grid + legend naming every fill), `Well list` (59 rows, yellow columns to fill at the reader, self-computing F/OD600), `Fill order` (dim → bright), `As performed` (run constants, harvest ODs, still-unrecorded fields) |
| [data/Book1.xlsx](data/Book1.xlsx) | **Input** — the Tecan export, 2026-11-17 18:38–18:43. OD600 + fluorescence at gain 50, 75 and 100. The notebook reads exactly this path |

### Analysis outputs (written by the notebook)

| File | Description |
|------|-------------|
| `data/EXP_015_tidy.csv` | Per-well tidy table — blanked values at all three gains, F/OD600, fold over autofluorescence |
| `data/EXP_015_summary.csv` | Per-condition means, SDs, CVs, fold over autofluorescence |
| `data/EXP_015_tier1.csv` | Tier 1 → free nM, depletion, pmol per OD·mL, sites per cell |
| `data/EXP_015_ratios.csv` | 052/056 ratio with Welch p at each concentration |
| `data/EXP_015_readout.html` | F/OD600 by strain and concentration, with the ratio on each pair |
| `data/EXP_015_tier1.html` | Display capacity, against EXP_014's lower bound and Costan 2024 |
| `data/EXP_015_induction.html` | Induced vs uninduced 2x2, log axis, with fold-change brackets and Welch p |
| `data/EXP_015_calibration.html` | Every sample placed on the standard curve: Tier 1 (start -> end = depletion) and cells as a GFP equivalent |
| `data/EXP_015_curve.html` | Standard curve — power-law fit used, line-through-origin shown rejected |
| `data/EXP_015_plate_heatmap.html` | Plate position QC, including the unfilled crosstalk-probe wells |
