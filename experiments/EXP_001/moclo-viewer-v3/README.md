# MoClo Genome Viewer — V2

Interactive browser for the *E. coli* K-12 MG1655 Golden Gate genome tiling — **686 Lvl0 parts** across **46 Lvl1 assemblies** with **standardized positional overhangs**.

## What's new in V2

| | V1 | V2 |
|---|---|---|
| Tiles per Lvl1 group | 11 | **15** |
| Total Lvl1 groups | 63 | **46** (−27%) |
| Avg Lvl1 size | 73.6 kb | **100.9 kb** |
| Overhangs | Genome-derived (unique) | **Standardized** (interchangeable) |
| Junction scars | Seamless | 4-nt scar (99.7% intergenic) |

V2 uses a fixed set of **16 positional overhangs** so all tiles at the same position are interchangeable across Lvl1 groups, enabling combinatorial library construction and chimeric assemblies.

## Quick start

```bash
cd experiments/EXP_001/moclo-viewer
npm install        # first time only
npm run dev        # starts on http://localhost:5173
```

> To switch between V1 and V2 data, change the fetch URL in `src/App.tsx` from `data_bundle.json` to `data_bundle_v2.json` (or vice versa). Both bundles are in `public/`.

## How it works

The viewer loads a pre-computed JSON data bundle (generated from the analysis CSVs) containing every tile's coordinates, primers, overhangs, domestication status, and Lvl1 group assignments.

### Three interactive panels

**1. Genome canvas** (top)

A canvas-rendered linear map of the full 4.64 Mb genome with two tracks:

- **Lvl1 Groups** — 46 coloured blocks (green = all tiles ready, yellow/orange = some need domestication)
- **Lvl0 Tiles** — 686 blocks coloured by internal BsaI count

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

- **Assembled Lvl1 construct** — up to 15 tiles with their standardized 4-nt overhangs between them, flanked by backbone elements. Orange dots mark tiles needing domestication.
- **Genome alignment** — a proportional bar showing where each tile maps on the genome.
- **Tile list** — all tiles with size, status, and overhang pairs.

Click any tile in the construct diagram, alignment track, or list to select it.

**3. Part detail panel** (right sidebar)

Full molecular detail for the selected tile:

- **Overview** — genomic coordinates, length, GC%, Lvl1 group, position index, boundary type
- **MoClo Lvl0 construct** — visual diagram: `pICH — BsaI — [overhang_L] — [insert] — [overhang_R] — BsaI — pICH`
- **Tile primers** — forward and reverse sequences with colour-coded regions:
  - Purple = BsaI recognition site (`CGTCTCN`)
  - Blue = 4-nt standardized overhang
  - Grey = genome-binding region
- **Mutagenic primers** (if tile needs domestication) — each internal BsaI site with its silent mutation, codon change, gene name, and primer pair
- **OE-PCR plan** (if domestication needed) — sub-fragment diagram and table with coordinates and Tm values

## Colour legend

| Colour | Meaning |
|--------|---------|
| 🟢 Green | GG-ready (0 internal BsaI sites) |
| 🟡 Yellow | 1 internal BsaI site |
| 🟠 Orange | 2 internal BsaI sites |
| 🔴 Red | 3+ internal BsaI sites |
| 🔵 Blue | Standardized junction overhangs / accent |
| 🟣 Purple | BsaI recognition sites in primers |

## Standardized overhangs (V2)

The 16 positional overhangs ensure that **any tile at position *i*** can be used in **any Lvl1 group**:

| Pos | Junction | Overhang | Pos | Junction | Overhang |
|-----|----------|----------|-----|----------|----------|
| 0 | BB → T0 | `AATA` | 8 | T7 → T8 | `AGAT` |
| 1 | T0 → T1 | `AACT` | 9 | T8 → T9 | `AGCA` |
| 2 | T1 → T2 | `AAGC` | 10 | T9 → T10 | `TAAT` |
| 3 | T2 → T3 | `ATAA` | 11 | T10 → T11 | `TATC` |
| 4 | T3 → T4 | `ATTC` | 12 | T11 → T12 | `TACA` |
| 5 | T4 → T5 | `ATGT` | 13 | T12 → T13 | `TTAC` |
| 6 | T5 → T6 | `ACAC` | 14 | T13 → T14 | `TTCT` |
| 7 | T6 → T7 | `ACTT` | 15 | T14 → BB | `TGAA` |

Design constraints: no palindromes, no homopolymer runs ≥ 3, Hamming distance ≥ 2 between all pairs, no BsaI site overlap, no reverse-complement duplicates.

## Data pipeline

The data bundle is generated from four source CSVs produced by `pipeline_v2.py`:

```
v2_tiles.csv                      → tile coordinates, primers, overhangs, boundary types
pcr_simulation.csv                → GC content, internal BsaI counts, GG readiness
domestication_primers.csv         → mutagenic primer sequences for each internal site
domestication_subfragments.csv    → OE-PCR sub-fragment coordinates and primers
```

To regenerate the data bundle after re-running analysis scripts:

```bash
cd experiments/EXP_001
python3 pipeline_v2.py
python3 generate_data_bundle.py   # outputs public/data_bundle_v2.json
```

## Key statistics

| Metric | Value |
|--------|-------|
| Genome | *E. coli* K-12 MG1655 — 4.64 Mb |
| Total Lvl0 tiles | 686 |
| Lvl1 groups | 46 (15 tiles each, except last group with 11) |
| GG-ready tiles | 480 (70%) |
| Tiles needing domestication | 206 |
| BsaI sites to remove | 261 |
| Total oligos | 1,894 |
| CDS-safe boundaries | 99.7% |

## Tech stack

- **Vite** + **React 19** + **TypeScript**
- **Tailwind CSS v4** — utility-first styling
- **shadcn/ui** — Card, Badge, Tooltip, ScrollArea, Separator, Tabs components
- **HTML Canvas** — genome track rendering (performant with 686+ elements)
- **Inter** + **JetBrains Mono** — typography
