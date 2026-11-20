"""EXP_015 - single source of truth for the as-performed run.

Everything downstream (the plate-map workbook, the analysis notebook) imports
from here. EXP_014 kept the layout in two places and they drifted; this module
exists so that cannot happen again.

Nothing in here is inferred. Values the bench has not yet supplied are None,
and the notebook is expected to fail loudly rather than fill them in.
"""

from __future__ import annotations

# --------------------------------------------------------------- the run ----
DATE = "2026-11-17"
STRAINS = {
    "052": "MS_S_052  Enhancer, no HA",
    "056": "MS_S_056  Enhancer + 2xHA",
}

CULTURE_mL = 3.1              # per induction tube, as performed (planned 4.0)
ATC_uL_PER_TUBE = 6.70        # of 100 uM = 46.29 ng/uL -> 100 ng/mL final
ATC_ng_per_mL = 100
INDUCTION_H = 2.5

CELL_INPUT_OD_mL = 0.3        # per labelling tube, identical for all 22
LABEL_uL = 200
LABEL_TEMP = "room temperature"   # record the actual value
N_WASHES = 2
WASH_uL = 1000
WASH_TEMP = "ice-cold"
RESUSPEND_uL = 300
WELL_uL = 150                 # one fill volume for every well on the plate
SPIN = "4,000 x g, 3 min (Thermo Heraeus Pico 17, RCF mode)"

# Reader — as performed
EX_nm, EM_nm = 478, 515
EX_BW, EM_BW = 9, 20
GAINS = (50, 75, 100)         # three were read, not the two planned
GAIN_HI = 100                 # cell wells
GAIN_LO = 75                  # Tier 1 and the standard curve
EXP014_GAIN_RATIO = 8.716     # gain100/gain75 prior; measured 8.633 here (0.9 % apart)
MEASURED_GAIN_RATIO = 8.633

# ⚠ DEVIATION: the plate was CLEAR, not the black/clear-bottom plate the layout
# assumed. Crosstalk was therefore measured rather than assumed, using the
# unfilled wells left beside the bright row F: worst case +4 RFU on a ~12,700
# RFU neighbour = 0.03 %. Negligible, so nothing is affected.
PLATE = ("Greiner 96 Flat Bottom Transparent Polystyrene, "
         "Cat. No. 655101/655161/655192")

READ_TIME = "2026-11-17 18:38-18:43"
PLATE_READ_TEMP_C = 26.0      # instrument chamber at read time. NOT the room
                              # temperature during labelling, which is unrecorded.

# Antigen
GFP_PREP = "PC01538_001"
GFP_MW_kDa = 30.12            # from sequence; the prep's own mg/mL vs mM imply
                              # 33.3 kDa, an 11 % inconsistency recorded in EXP_014
CONCS_nM = (100, 1000)

# ------------------------------------------------------- values to record ---
# Left None on purpose. A missing value is information; see LAB_RECORD_PROTOCOL.
UNRECORDED = {
    "diluted_back_before_split": None,   # flasks were 0.56 / 0.64 at T+3 h
    "od_at_induction_052": None,
    "od_at_induction_056": None,
    "time_atc_added": None,
    "time_harvest": None,
    "room_temperature_C": None,
    "wash_buffer_pH": None,
    "lb_formulation": None,
    "kanamycin_ug_per_mL": None,
}

# ------------------------------------------------------------ harvest OD ----
# Measured 1:10; OD600 = reading x 10.
HARVEST_OD = {
    "052IA": 2.4, "052IB": 1.7, "052IC": 2.7,
    "052UA": 2.3, "052UB": 2.6, "052UC": 2.2,
    "056IA": 3.0, "056IB": 2.7, "056IC": 2.9,
    "056UA": 2.6, "056UB": 3.3, "056UC": 3.4,
}
# V = 0.3 / OD600, rounded to the microlitre actually pipetted
V_uL = {k: round(CELL_INPUT_OD_mL / od * 1000) for k, od in HARVEST_OD.items()}

OUTLIER_NOTE = (
    "052IB harvested at OD600 1.7 against 2.4 and 2.7 for its siblings (~30 % low). "
    "Flagged, not adjusted."
)
PHASE_NOTE = (
    "Harvest OD600 2.2-3.4 against EXP_014's 1.13-1.61: at or past the end of "
    "exponential. The 052/056 ratio is unaffected (same condition both strains), "
    "but pmol per OD.mL describes late-exponential/stationary cells."
)

# ------------------------------------------------------- prior from EXP_014 --
EXP014 = {
    "capacity_pmol_per_OD_mL_lower_bound": 38.6,   # from 98.3 % depletion; A LOWER BOUND
    "sites_per_cell_lower_bound": 29_000,
    "cells_per_OD_mL": 8e8,
    "fold_052": 57.9,
    "fold_056": 22.5,
    "ratio_052_056": 2.58,
    "autofluor_RFU": (503, 565),
    "buffer_blank_RFU": 194,
    "buffer_blank_SD": 4.3,
}

# ----------------------------------------------------------------- arms ------
I_ARMS = ["052IA", "052IB", "052IC", "056IA", "056IB", "056IC"]
U_ARMS = ["052UA", "052UB", "052UC", "056UA", "056UB", "056UC"]
NOGFP_ARMS = ["052IA", "056IA", "052UA", "056UA"]

CURVE = [("S8", 7.8), ("S7", 15.6), ("S6", 31.3), ("S5", 62.5),
         ("S4", 125.0), ("S3", 250.0), ("S2", 500.0), ("S1", 1000.0)]

# group key -> (legend label, hex fill, has_cells, expected)
GROUPS = {
    "blank": ("Buffer blank - wash buffer only, no cells, no GFP",
              "D9D9D9", False, "~0 (defines zero)"),
    "cells_nogfp": ("Cells, NO GFP - autofluorescence control",
                    "BDD7EE", True, "~140 RFU over blank"),
    "cells_100": ("Cells labelled at 100 nM GFP",
                  "A9D18E", True, "moderate"),
    "cells_1000_U": ("Cells UNINDUCED, 1000 nM GFP - non-specific binding",
                     "E2F0D9", True, "~autofluorescence if clean"),
    "cells_1000_I": ("Cells INDUCED, 1000 nM GFP - primary signal",
                     "548235", True, "052 ~6,000 / 056 ~2,400 RFU"),
    "wash2": ("Wash 2 supernatant - wash sufficiency check",
              "FFE699", False, "~buffer blank if 2 washes suffice"),
    "curve": ("Standard curve S1-S8, 2-fold from 1000 nM",
              "B4A7D6", False, "7.8 - 1000 nM"),
    "qc100": ("100 nM working solution - dilution QC",
              "D9D2E9", False, "must land on the curve"),
    "tier1_nogfp": ("Tier 1 from the no-GFP tubes",
                    "FBE5D6", False, "~0"),
    "tier1_100": ("Tier 1 from the 100 nM rack - free GFP after capture",
                  "F4B183", False, "~40-100 nM"),
    "tier1_1000": ("Tier 1 from the 1000 nM rack - free GFP after capture",
                   "C55A11", False, "~940-1000 nM"),
}


def _build_wells() -> list[tuple[str, str, str]]:
    """(well, group, sample). Ordered dim -> bright down the plate."""
    out: list[tuple[str, str, str]] = []

    def row(letter: str, items):
        for i, (group, sample) in enumerate(items, start=1):
            out.append((f"{letter}{i}", group, sample))

    row("A",
        [("blank", f"blank {i}") for i in (1, 2, 3)]
        + [("cells_nogfp", a) for a in NOGFP_ARMS]
        + [("tier1_nogfp", a) for a in NOGFP_ARMS])
    row("B",
        [("cells_1000_U", a) for a in U_ARMS]
        + [("cells_100", a) for a in I_ARMS])
    row("C",
        [("cells_1000_I", a) for a in I_ARMS]
        + [("wash2", "wash2 052IA"), ("wash2", "wash2 056IA")])
    row("D",
        [("curve", f"{n} {nm:g} nM") for n, nm in CURVE]
        + [("qc100", "100 nM QC a"), ("qc100", "100 nM QC b")])
    row("E", [("tier1_100", a) for a in I_ARMS])
    row("F",
        [("tier1_1000", a) for a in I_ARMS]
        + [("tier1_1000", a) for a in U_ARMS])
    return out


WELLS = _build_wells()
assert len(WELLS) == 59, f"expected 59 wells, built {len(WELLS)}"

# group -> which GFP concentration the tube saw (None where not applicable)
GROUP_CONC = {
    "cells_nogfp": 0, "cells_100": 100, "cells_1000_U": 1000,
    "cells_1000_I": 1000, "tier1_nogfp": 0, "tier1_100": 100,
    "tier1_1000": 1000,
}
GROUP_INDUCED = {
    "cells_100": True, "cells_1000_I": True, "cells_1000_U": False,
    "tier1_100": True, "tier1_1000": None,   # row F mixes I and U; read the sample
}


def frame():
    """The layout as a tidy DataFrame, one row per well."""
    import pandas as pd

    rows = []
    for well, group, sample in WELLS:
        label, hexcolor, has_cells, expected = GROUPS[group]
        arm = sample if sample in HARVEST_OD else None
        rows.append({
            "well": well,
            "group": group,
            "group_label": label,
            "colour": hexcolor,
            "sample": sample,
            "arm": arm,
            "strain": arm[:3] if arm else None,
            "induced": (arm[3] == "I") if arm else None,
            "is_cells": has_cells,
            "is_tier1": group.startswith("tier1"),
            "conc_nM": GROUP_CONC.get(group),
            "curve_nM": next((nm for n, nm in CURVE if sample.startswith(n + " ")), None),
            "harvest_od": HARVEST_OD.get(arm) if arm else None,
            "v_uL": V_uL.get(arm) if arm else None,
            "fill_uL": WELL_uL,
            "expected": expected,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(f"EXP_015 {DATE}: {len(WELLS)} wells, {WELL_uL} uL each")
    for arm in I_ARMS + U_ARMS:
        print(f"  {arm}  OD600 {HARVEST_OD[arm]:.1f}  V {V_uL[arm]:3d} uL")
    missing = [k for k, v in UNRECORDED.items() if v is None]
    print(f"\nSTILL UNRECORDED ({len(missing)}): {', '.join(missing)}")
