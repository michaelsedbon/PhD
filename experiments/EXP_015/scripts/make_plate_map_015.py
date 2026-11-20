"""EXP_015 plate map generator -> data/EXP_015_plate_map.xlsx

59 wells, 150 uL each, one black / clear-bottom 96-well plate.

The layout itself lives in exp015_layout.py and is imported, not restated:
EXP_014 kept it in two places and they drifted.

Layout principle: wells run DIM -> BRIGHT down the plate, so the
autofluorescence and blank wells (tens of RFU) sit far from the 1000 nM Tier-1
wells (~10^5 RFU). Black plates hold lateral crosstalk under ~0.1 %, but 0.1 %
of 114,000 is ~114 RFU — the same size as the autofluorescence being measured.

WARNING: re-running this OVERWRITES the workbook. In EXP_014 a regeneration
destroyed hand-entered results. If readings have been typed in, do not run it.

    python3 scripts/make_plate_map_015.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp015_layout as L  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data" / "EXP_015_plate_map.xlsx"

BY_WELL = {w: (g, s) for w, g, s in L.WELLS}

thin = Side(style="thin", color="999999")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
BOLD = Font(bold=True)
YELLOW = PatternFill("solid", fgColor="FFF2CC")


def dark(hexcolor: str) -> bool:
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (0, 2, 4))
    return (0.299 * r + 0.587 * g + 0.114 * b) < 140


wb = Workbook()

# ---- Sheet 1: the plate grid ------------------------------------------------
ws = wb.active
ws.title = "Plate map"

ws["A1"] = "EXP_015 - plate map"
ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = (f"Black / clear-bottom 96-well plate. {len(L.WELLS)} wells, "
            f"{L.WELL_uL} uL in every well - one fill volume throughout.")
ws["A3"] = (f"Read OD600, then fluorescence ex {L.EX_nm} / em {L.EM_nm} "
            f"(bw {L.EX_BW} / {L.EM_BW}), BOTTOM, AT GAIN {L.GAIN_HI} AND AGAIN AT "
            f"GAIN {L.GAIN_LO}. Set the read area to the whole plate.")
ws["A4"] = ("Wells run dim (row A) to bright (row F) so the autofluorescence and "
            "blank wells sit far from the 1000 nM Tier-1 wells.")

TOP = 6
for c in range(1, 13):
    cell = ws.cell(row=TOP, column=c + 1, value=c)
    cell.font = BOLD
    cell.alignment = CENTER

for r, letter in enumerate("ABCDEFGH"):
    ws.cell(row=TOP + 1 + r, column=1, value=letter).font = BOLD
    ws.cell(row=TOP + 1 + r, column=1).alignment = CENTER
    for c in range(1, 13):
        well = f"{letter}{c}"
        cell = ws.cell(row=TOP + 1 + r, column=c + 1)
        cell.border = BORDER
        cell.alignment = CENTER
        if well in BY_WELL:
            group, sample = BY_WELL[well]
            _, hexcolor, _, _ = L.GROUPS[group]
            cell.value = sample
            cell.fill = PatternFill("solid", fgColor=hexcolor)
            cell.font = Font(size=9, color="FFFFFF" if dark(hexcolor) else "000000")
        else:
            cell.value = "empty"
            cell.font = Font(size=9, color="AAAAAA", italic=True)

ws.column_dimensions["A"].width = 4
for c in range(2, 14):
    ws.column_dimensions[get_column_letter(c)].width = 15
for r in range(TOP + 1, TOP + 9):
    ws.row_dimensions[r].height = 30

leg = TOP + 10
ws.cell(row=leg, column=1, value="LEGEND - every colour used above").font = BOLD
for c, h in [(1, "Colour"), (2, "What it is"), (6, "Cells?"), (7, "Expected")]:
    ws.cell(row=leg + 1, column=c, value=h).font = BOLD

for i, (key, (label, hexcolor, has_cells, expected)) in enumerate(L.GROUPS.items()):
    r = leg + 2 + i
    swatch = ws.cell(row=r, column=1)
    swatch.fill = PatternFill("solid", fgColor=hexcolor)
    swatch.border = BORDER
    n = sum(1 for _, g, _ in L.WELLS if g == key)
    ws.cell(row=r, column=2, value=f"{label}  (n = {n})")
    ws.cell(row=r, column=6, value="yes" if has_cells else "no")
    ws.cell(row=r, column=7, value=expected)

r = leg + 2 + len(L.GROUPS)
ws.cell(row=r + 1, column=1, value='"empty" = no well filled. Rows G and H are unused.')
ws.cell(row=r + 2, column=1,
        value=("F/OD600 is computed ONLY for wells containing cells. "
               "Cell-free wells use blanked RFU."))

# ---- Sheet 2: well list ------------------------------------------------------
wl = wb.create_sheet("Well list")
headers = ["Well", "Group", "Sample", "Contains cells", "Volume (uL)",
           "Expected", "OD600", f"RFU gain {L.GAIN_HI}", f"RFU gain {L.GAIN_LO}",
           "F/OD600"]
for c, h in enumerate(headers, start=1):
    cell = wl.cell(row=1, column=c, value=h)
    cell.font = BOLD
    cell.fill = PatternFill("solid", fgColor="D9D9D9")
    cell.border = BORDER

for i, (well, group, sample) in enumerate(L.WELLS, start=2):
    label, hexcolor, has_cells, expected = L.GROUPS[group]
    c1 = wl.cell(row=i, column=1, value=well)
    c1.fill = PatternFill("solid", fgColor=hexcolor)
    c1.font = Font(color="FFFFFF" if dark(hexcolor) else "000000")
    wl.cell(row=i, column=2, value=label)
    wl.cell(row=i, column=3, value=sample)
    wl.cell(row=i, column=4, value="yes" if has_cells else "no")
    wl.cell(row=i, column=5, value=L.WELL_uL)
    wl.cell(row=i, column=6, value=expected)
    for c in (7, 8, 9):
        wl.cell(row=i, column=c).fill = YELLOW
        wl.cell(row=i, column=c).border = BORDER
    if has_cells:
        wl.cell(row=i, column=10,
                value=f'=IF(AND(ISNUMBER(H{i}),ISNUMBER(G{i}),G{i}<>0),H{i}/G{i},"")')
    else:
        wl.cell(row=i, column=10, value="n/a - cell-free")

for c, w in enumerate([7, 44, 16, 13, 12, 26, 10, 14, 14, 12], start=1):
    wl.column_dimensions[get_column_letter(c)].width = w
wl.freeze_panes = "A2"

note = len(L.WELLS) + 3
wl.cell(row=note, column=1, value="YELLOW = fill in at the plate reader.").font = BOLD
for k, text in enumerate([
    ("F/OD600 is left blank for cell-free wells on purpose - a fluorescence/OD ratio "
     "is meaningless there and an autofilled formula would invite its use."),
    ("Autofluorescence is subtracted AFTER normalising to OD600, not before: the "
     "no-GFP control well has its own cell density."),
    (f"Cell wells are read off gain {L.GAIN_HI}; Tier 1 and the standard curve off "
     f"gain {L.GAIN_LO}. Convert with this plate's own gain series, not EXP_014's "
     f"{L.EXP014_GAIN_RATIO}."),
], start=1):
    wl.cell(row=note + k, column=1, value=text)

# ---- Sheet 3: fill order -----------------------------------------------------
fo = wb.create_sheet("Fill order")
fo["A1"] = "Order to fill the plate"
fo["A1"].font = Font(bold=True, size=14)
fo["A2"] = ("Fill DIM wells first and the 1000 nM Tier-1 wells last, so a tip that "
            "has touched a bright well never goes near a blank afterwards.")

steps = [
    ("1", "A1-A3", "3 buffer blanks", "wash buffer"),
    ("2", "A4-A7", "4 cell wells, no GFP", "autofluorescence controls"),
    ("3", "A8-A11", "4 Tier 1, no GFP", "from tubes noG 052IA / 056IA / 052UA / 056UA"),
    ("4", "B1-B6", "6 cell wells, uninduced 1000 nM", "the strain-matched null"),
    ("5", "B7-B12", "6 cell wells, 100 nM", ""),
    ("6", "C1-C6", "6 cell wells, induced 1000 nM", "the primary signal"),
    ("7", "C7-C8", "2 wash-2 supernatants", "wash sufficiency"),
    ("8", "D1-D8", "standard curve S8 -> S1", "dim to bright, change tips every step"),
    ("9", "D9-D10", "2 wells of the 100 nM working solution", "must land on the curve"),
    ("10", "E1-E6", "6 Tier 1 from the 100 nM rack", ""),
    ("11", "F1-F12", "12 Tier 1 from the 1000 nM rack", "brightest - fill last"),
]
for c, h in enumerate(["Step", "Wells", "What", "Note"], start=1):
    fo.cell(row=4, column=c, value=h).font = BOLD
for i, s in enumerate(steps, start=5):
    for c, v in enumerate(s, start=1):
        fo.cell(row=i, column=c, value=v)
for c, w in enumerate([6, 10, 44, 46], start=1):
    fo.column_dimensions[get_column_letter(c)].width = w

fo.cell(row=len(steps) + 7, column=1,
        value=("Mix each cell tube immediately before dispensing - the pellets are "
               "small and settle fast.")).font = BOLD

# ---- Sheet 4: as performed ---------------------------------------------------
ap = wb.create_sheet("As performed")
ap["A1"] = "EXP_015 - as performed"
ap["A1"].font = Font(bold=True, size=14)

rows = [
    ("Date", L.DATE),
    ("Culture volume per induction tube", f"{L.CULTURE_mL} mL (planned 4.0)"),
    ("aTc per induced tube", f"{L.ATC_uL_PER_TUBE} uL of 100 uM -> "
                             f"{L.ATC_ng_per_mL} ng/mL"),
    ("Induction", f"{L.INDUCTION_H} h, 37 C shaking"),
    ("Cell input per labelling tube", f"{L.CELL_INPUT_OD_mL} OD.mL"),
    ("Labelling", f"{L.LABEL_uL} uL, 30 min, {L.LABEL_TEMP}"),
    ("GFP concentrations", ", ".join(f"{c} nM" for c in L.CONCS_nM)),
    ("Washes", f"{L.N_WASHES} x {L.WASH_uL} uL, {L.WASH_TEMP}"),
    ("Resuspension", f"{L.RESUSPEND_uL} uL"),
    ("Spin", L.SPIN),
    ("Antigen", f"{L.GFP_PREP}, {L.GFP_MW_kDa} kDa from sequence"),
]
for i, (k, v) in enumerate(rows, start=3):
    ap.cell(row=i, column=1, value=k).font = BOLD
    ap.cell(row=i, column=2, value=v)

r0 = len(rows) + 5
ap.cell(row=r0, column=1, value="Harvest OD600 and draw volumes").font = BOLD
for c, h in enumerate(["Tube", "OD600", "V = 0.3/OD600 (uL)"], start=1):
    ap.cell(row=r0 + 1, column=c, value=h).font = BOLD
for i, arm in enumerate(L.I_ARMS + L.U_ARMS, start=r0 + 2):
    ap.cell(row=i, column=1, value=arm)
    ap.cell(row=i, column=2, value=L.HARVEST_OD[arm])
    ap.cell(row=i, column=3, value=L.V_uL[arm])

r1 = r0 + 2 + len(L.I_ARMS + L.U_ARMS) + 2
ap.cell(row=r1, column=1, value="STILL UNRECORDED").font = Font(bold=True, color="C00000")
for i, (k, v) in enumerate(L.UNRECORDED.items(), start=r1 + 1):
    ap.cell(row=i, column=1, value=k)
    cell = ap.cell(row=i, column=2, value=v if v is not None else "")
    if v is None:
        cell.fill = YELLOW
        cell.border = BORDER

r2 = r1 + len(L.UNRECORDED) + 2
ap.cell(row=r2, column=1, value="Notes on the record").font = BOLD
ap.cell(row=r2 + 1, column=1, value=L.PHASE_NOTE)
ap.cell(row=r2 + 2, column=1, value=L.OUTLIER_NOTE)

for c, w in enumerate([38, 60], start=1):
    ap.column_dimensions[get_column_letter(c)].width = w

OUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUT)
print(f"wrote {OUT}  ({len(L.WELLS)} wells)")
