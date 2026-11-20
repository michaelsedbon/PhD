"""Parser for Tecan i-control (.xlsx) exports from the Infinite 200 Pro.

Handles the two block shapes these files contain:

  * fixed-wavelength plate reads - a ``<>`` header row giving the plate column
    numbers, followed by one row per plate row letter;
  * wavelength scans - a ``Wavel.`` header row giving the wavelengths, followed
    by one row per well name (``A1``, ``A2`` ...).

Each block carries its own metadata (mode, wavelengths, gain, temperature), so a
single file may hold an absorbance read and several fluorescence reads at
different gains. ``OVER`` (detector saturated) becomes NaN, never 0 - a
saturated well is missing data, not a zero reading.

Used by EXP_014_analysis.ipynb. Standalone:

    uv run --with openpyxl,pandas python3 scripts/tecan_parse.py <file.xlsx>
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

import pandas as pd
from openpyxl import load_workbook

# metadata labels worth keeping, mapped to short keys
_META = {
    "Mode": "mode",
    "Measurement Wavelength": "abs_nm",
    "Excitation Wavelength": "ex_nm",
    "Emission Wavelength": "em_nm",
    "Excitation Bandwidth": "ex_bw",
    "Emission Bandwidth": "em_bw",
    "Bandwidth": "abs_bw",
    "Gain": "gain",
    "Number of Flashes": "flashes",
    "Integration Time": "integration_us",
    "Part of Plate": "part_of_plate",
    "Plate": "plate_def",
    "Device:": "device",
    "Emission Wavelength Start": "em_start",
    "Emission Wavelength End": "em_end",
    "Excitation Wavelength Start": "ex_start",
    "Excitation Wavelength End": "ex_end",
}

OVER = "OVER"


@dataclass
class Block:
    """One measurement block within a Tecan export."""

    label: str
    sheet: str
    meta: dict = field(default_factory=dict)
    data: pd.DataFrame = field(default_factory=pd.DataFrame)  # long form
    kind: str = "plate"  # "plate" or "scan"

    def __repr__(self) -> str:  # pragma: no cover - display only
        m = self.meta
        if self.kind == "scan":
            where = f"scan {m.get('ex_nm') or m.get('ex_start')}->{m.get('em_nm') or m.get('em_start')}"
        else:
            where = (
                f"abs {m.get('abs_nm')}"
                if "Absorbance" in str(m.get("mode"))
                else f"ex {m.get('ex_nm')}/em {m.get('em_nm')}"
            )
        return (
            f"<Block {self.label!r} [{self.sheet}] {where} gain={m.get('gain')} "
            f"n={len(self.data)}>"
        )


def _num(v):
    """Tecan writes OVER for a saturated detector. That is missing, not zero."""
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s.upper() == OVER:
            return float("nan")
        try:
            return float(s)
        except ValueError:
            return None
    return float(v) if isinstance(v, (int, float)) else None


def parse_file(path: str) -> list[Block]:
    """Return every measurement block in the workbook, in file order."""
    wb = load_workbook(path, data_only=True)
    blocks: list[Block] = []

    for sheet in wb.sheetnames:
        ws = wb[sheet]
        if ws.max_row < 2:
            continue

        carried: dict = {}          # file-level metadata (device, plate def)
        pending: dict = {}          # metadata seen since the last Label:
        label = None
        r = 1
        while r <= ws.max_row:
            a = ws.cell(row=r, column=1).value
            a = a.strip() if isinstance(a, str) else a

            if isinstance(a, str) and a.startswith("Label:"):
                label = a.split("Label:", 1)[1].strip() or f"block{len(blocks)}"
                pending = {}
                r += 1
                continue

            if isinstance(a, str) and a in _META:
                pending[_META[a]] = ws.cell(row=r, column=5).value
                if _META[a] in ("device", "plate_def"):
                    carried[_META[a]] = ws.cell(row=r, column=5).value
                r += 1
                continue

            # temperature sits in column 2 as free text
            if isinstance(a, str) and a.startswith("Device:"):
                carried["device"] = a
                r += 1
                continue
            b = ws.cell(row=r, column=2).value
            if isinstance(b, str) and b.startswith("Temperature:"):
                pending["temperature"] = b.replace("Temperature:", "").strip()
                r += 1
                continue

            # ---- fixed-wavelength plate block: "<>" then row letters
            if a == "<>":
                cols = []
                for c in range(2, ws.max_column + 1):
                    v = ws.cell(row=r, column=c).value
                    if v is None:
                        break
                    cols.append(int(v))
                rows = []
                rr = r + 1
                while rr <= ws.max_row:
                    letter = ws.cell(row=rr, column=1).value
                    if not (isinstance(letter, str) and len(letter.strip()) == 1
                            and letter.strip().isalpha()):
                        break
                    letter = letter.strip().upper()
                    for i, cnum in enumerate(cols):
                        val = _num(ws.cell(row=rr, column=2 + i).value)
                        if val is not None:
                            rows.append({"well": f"{letter}{cnum}", "value": val})
                    rr += 1
                if rows:
                    blocks.append(Block(label or f"block{len(blocks)}", sheet,
                                        {**carried, **pending},
                                        pd.DataFrame(rows), "plate"))
                r = rr
                continue

            # ---- scan block: "Wavel." then one row per well name
            if isinstance(a, str) and a.startswith("Wavel"):
                wls = []
                for c in range(2, ws.max_column + 1):
                    v = ws.cell(row=r, column=c).value
                    if v is None:
                        break
                    wls.append(float(v))
                rows = []
                rr = r + 1
                while rr <= ws.max_row:
                    name = ws.cell(row=rr, column=1).value
                    if not (isinstance(name, str) and len(name) >= 2
                            and name[0].isalpha() and name[1:].isdigit()):
                        break
                    for i, wl in enumerate(wls):
                        val = _num(ws.cell(row=rr, column=2 + i).value)
                        if val is not None:
                            rows.append({"well": name, "wavelength": wl,
                                         "value": val})
                    rr += 1
                if rows:
                    blocks.append(Block(label or f"scan{len(blocks)}", sheet,
                                        {**carried, **pending},
                                        pd.DataFrame(rows), "scan"))
                r = rr
                continue

            r += 1

    return blocks


def pick(blocks: list[Block], mode: str = "fluor", gain=None,
         ex=None, em=None, part=None) -> Block:
    """Pick one plate block. Raises if the choice is ambiguous or absent.

    Deliberately strict: silently taking the first match is how the wrong gain
    ends up in a figure.
    """
    want_abs = mode.lower().startswith("abs")
    cand = []
    for b in blocks:
        if b.kind != "plate":
            continue
        is_abs = "Absorbance" in str(b.meta.get("mode", ""))
        if is_abs != want_abs:
            continue
        if gain is not None and b.meta.get("gain") != gain:
            continue
        if ex is not None and b.meta.get("ex_nm") != ex:
            continue
        if em is not None and b.meta.get("em_nm") != em:
            continue
        if part is not None and b.meta.get("part_of_plate") != part:
            continue
        cand.append(b)
    if not cand:
        raise LookupError(
            f"no {mode} block matching gain={gain} ex={ex} em={em} part={part}. "
            f"Available: {blocks}"
        )
    if len(cand) > 1:
        detail = "\n  ".join(
            f"{c.label!r} sheet={c.sheet} part={c.meta.get('part_of_plate')} "
            f"n={len(c.data)}" for c in cand
        )
        raise LookupError(
            f"{len(cand)} blocks match; pass part= to disambiguate:\n  {detail}"
        )
    return cand[0]


if __name__ == "__main__":  # pragma: no cover
    for path in sys.argv[1:]:
        print(f"\n=== {path}")
        for b in parse_file(path):
            print(" ", b)
            if b.kind == "plate" and len(b.data) <= 12:
                print("   ", b.data.to_dict("records"))
