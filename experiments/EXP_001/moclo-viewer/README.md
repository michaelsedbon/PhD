# MoClo Genome Viewer

Interactive browser for the *E. coli* K-12 MG1655 Golden Gate genome tiling — 686 Lvl0 parts and 63 Lvl1 assemblies.

## Quick start

```bash
cd experiments/EXP_001/moclo-viewer
npm install        # first time only
npm run dev        # starts on http://localhost:5173
```

## How it works

The viewer loads a pre-computed `data_bundle.json` (generated from the analysis CSVs) containing every tile's coordinates, primers, overhangs, domestication status, and Lvl1 group assignments.

### Three interactive panels

**1. Genome canvas** (top)

A canvas-rendered linear map of the full 4.64 Mb genome. Two tracks:

- **Lvl1 Groups** — 63 coloured blocks (green = all tiles ready, yellow/orange = some need domestication)
- **Lvl0 Tiles** — 686 blocks coloured by internal BsaI count (green = 0, yellow = 1, orange = 2, red = 3+)

Controls:
| Action | Effect |
|--------|--------|
| Scroll wheel | Zoom in / out |
| Click + drag | Pan |
| Click a tile or group | Select it |
| Double-click a group | Zoom to fit that group |
| Reset button | Return to full genome view |

A minimap at the bottom shows your current viewport position.

**2. Lvl1 Assembly view** (centre)

When a group is selected, this panel shows:

- **Assembled Lvl1 construct** — all 11 tiles drawn with their 4-nt BsaI junction overhangs between them, flanked by backbone elements. Orange dots mark tiles needing domestication.
- **Genome alignment** — a proportional bar showing where each tile maps on the genome.
- **Tile list** — all tiles with size, status, and overhang pairs.

Click any tile in the construct diagram, alignment track, or list to select it.

**3. Part detail panel** (right sidebar)

Shows full molecular detail for the selected tile:

- **Overview** — genomic coordinates, length, GC%, Lvl1 group, boundary type
- **MoClo Lvl0 construct** — visual diagram of the cloned insert: `pICH — BsaI — [overhang_L] — [insert] — [overhang_R] — BsaI — pICH`
- **Tile primers** — forward and reverse sequences with colour-coded regions:
  - Purple = BsaI recognition site (`CGTCTCN`)
  - Blue = 4-nt overhang
  - Grey = genome-binding region
- **Mutagenic primers** (if tile needs domestication) — each internal BsaI site with its silent mutation, codon change, gene name, and primer pair
- **OE-PCR plan** (if domestication needed) — sub-fragment diagram and table with coordinates and Tm values

## Colour legend

| Colour | Meaning |
|--------|---------|
| 🟢 Green | GG-ready (no internal BsaI sites) |
| 🟡 Yellow | 1 internal BsaI site |
| 🟠 Orange | 2 internal BsaI sites |
| 🔴 Red | 3+ internal BsaI sites |
| 🔵 Blue | BsaI junction overhangs / accent |
| 🟣 Purple | BsaI recognition sites in primers |

## Data pipeline

The `data_bundle.json` is generated from four source CSVs:

```
tiles.csv                    → tile coordinates, primers, overhangs, boundary types
pcr_simulation.csv           → GC content, internal BsaI counts, GG readiness
domestication_primers.csv    → mutagenic primer sequences for each internal site
domestication_subfragments.csv → OE-PCR sub-fragment coordinates and primers
```

To regenerate the data bundle after re-running analysis scripts:

```bash
cd experiments/EXP_001
python3 generate_data_bundle.py   # or run the inline script used during setup
```

## Tech stack

- **Vite** + **React** + **TypeScript**
- **Tailwind CSS v4** — utility-first styling
- **shadcn/ui** — Card, Badge, Tooltip, ScrollArea, Separator, Tabs components
- **HTML Canvas** — genome track rendering (performant with 686+ elements)
- **Inter** + **JetBrains Mono** — typography
