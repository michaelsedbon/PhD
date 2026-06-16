# DNA Studio

A C++ / Qt 6 desktop DNA-editing app, layout inspired by **Geneious Prime**, themed
with the SYNTHETICA Lab design system (VS Code dark, Lucide-style icons).

See [REQUIREMENTS.md](REQUIREMENTS.md) for the full spec.

## Status — v0.2

- ✅ Full 4-pane IDE shell: menu bar, main toolbar, dockable source tree, document
  table, tabbed viewer, options inspector, status bar. All panes resizable.
- ✅ **Interactive plasmid / sequence view** (`CircularMapView`) — the centerpiece:
  - **Scroll wheel** → rotate the plasmid (spin the focus base).
  - **Option/Alt + scroll** → zoom; radius grows, center slides down, arc flattens,
    focus base stays pinned near top-center.
  - Progressive level-of-detail: arcs → bp ruler → annotation bands w/ names →
    colored base ticks → readable A/C/G/T letters.
  - Live hover readout in the status bar (base, nucleotide, residue, amino acid).
  - Inspector toggles: Annotations, Show Name, Linear View, Translation.
- ✅ **Working navigation** — a document library wired tree → table → viewer. Every
  Local folder is selectable (counts are real); selecting a folder lists its
  documents and selecting a document loads its sequence, features and topology.
- ✅ **File import** — FASTA + GenBank readers (`SequenceIO`). File → Open, the **Add**
  button, or a path on the command line (`dna-studio file.gb`). GenBank features
  (CDS/gene/origin/promoter/…) are parsed, colored by type, and auto-laid out on
  radial tracks.
- ✅ **Selection + editing** — left-drag selects a base range (nearest-base snapping,
  highlighted with a half-base pad so the first/last bases are clearly included, with a
  status-bar readout). Right-click or the **Edit** menu: Copy, Paste, Add Annotation,
  Delete, Select All. **Deletion is protected**: sequences are locked by default
  (the **Allow Editing** toolbar toggle unlocks), and deleting asks for confirmation.
  Every edit is **undoable (Ctrl+Z)**.
- ✅ **Annotation types** — a Geneious-style Add Annotation dialog with the INSDC/GenBank
  feature-key vocabulary (`FeatureTypes`), each with its own color; pick a type,
  direction, and (optional) custom color. Directional types (CDS, gene, promoter, RBS,
  primer_bind, …) draw as real **block arrows**; non-directional ones (rep_origin,
  terminator, misc_feature, protein_bind, …) draw as plain capsules. (FASTA carries no
  annotations of its own — types come from the GenBank/EMBL feature vocabulary.)
- ✅ **Interactive annotations** — click an annotation to select it (white outline),
  **double-click to edit** it (name/type/direction/color), and Delete to remove it
  (annotations delete freely with undo — no sequence lock needed). Labels are
  **horizontal**, zoom-adaptive, centered on the feature's visible portion, with a
  readability halo, and hidden when they wouldn't fit (no clutter).
- ✅ **Selection-centered zoom** — when a base range is selected (drag or Find), zooming
  keeps that stretch centered.
- ✅ **Find (Cmd+F)** — a find bar searches for a subsequence and highlights **all
  hits** around the plasmid (green bands). Supports **approximate matching** up to a
  configurable **Hamming distance** (max mismatches) and searches **both strands**;
  each **mismatched base is flagged in red** inside the hit. **Cmd+G / Cmd+Shift+G**
  (or Next/Prev) cycle hits, rotating each to the top and selecting it; **Esc** closes.
- 🔜 Restriction sites, BLAST, save/export, multi-record files — see REQUIREMENTS.md.

> Sample library is generated in-memory; import real `.gb`/`.fasta` files for actual
> sequences. Edits live in memory (no save/export yet) but persist while the app runs.

## Build

Requires **Qt 6.3+** and **CMake 3.16+**.

```bash
# macOS (Homebrew)
brew install qt cmake

cmake -S . -B build -DCMAKE_PREFIX_PATH="$(brew --prefix qt)"
cmake --build build
./build/dna-studio.app/Contents/MacOS/dna-studio    # macOS bundle
# or ./build/dna-studio on Linux
```

On Linux: `sudo apt install qt6-base-dev qt6-svg-dev cmake build-essential`.

## Layout of the code

| File | Role |
|------|------|
| `src/main.cpp` | App entry; loads `theme.qss`, sets font |
| `src/MainWindow.{h,cpp}` | Window chrome + all four panes + mock data wiring |
| `src/CircularMapView.{h,cpp}` | The interactive plasmid/sequence canvas |
| `resources/theme.qss` | SYNTHETICA dark stylesheet (VS Code palette) |
| `resources/icons/*.svg` | Lucide-style icon set (swap in real Lucide SVGs freely) |
| `resources/resources.qrc` | Qt resource bundle |

## Controls (Sequence View)

| Input | Action |
|-------|--------|
| Scroll | Rotate plasmid / scroll along sequence |
| Option (Alt) + Scroll | Zoom in / out |
| Left-drag | Select a base range (zoom keeps it centered) |
| Click an annotation | Select it; click empty space to clear |
| Double-click an annotation | Edit it (name/type/direction/color) |
| Right-click | Context menu (annotation- or base-aware) |
| Ctrl+Z / Ctrl+C / Ctrl+V / Ctrl+A | Undo / Copy / Paste / Select All |
| Cmd/Ctrl+F | Open Find bar (search subsequence, with mismatch tolerance) |
| Cmd/Ctrl+G / Cmd/Ctrl+Shift+G | Find next / previous hit |
| Cmd/Ctrl + / − / 0 | Zoom in / out / fit |
| Esc | Close Find bar |
| Toolbar `+` / `−` / Fit | Zoom in / out / fit whole plasmid |
| Toolbar **Allow Editing** | Unlock the sequence for deletion/paste |
| Zoom % box | Set zoom directly |
| Hover | Base / residue readout in status bar |
| Inspector › Linear View | Toggle circular ↔ linear rendering |
