# DNA Studio

A C++ / Qt 6 desktop DNA-editing app, layout inspired by **Geneious Prime**, themed
with the SYNTHETICA Lab design system (VS Code dark, Lucide-style icons).

See [REQUIREMENTS.md](REQUIREMENTS.md) for the full spec.

## Status — v0.1

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
- 🔜 Real file I/O (FASTA / GenBank), editing, restriction/BLAST — see open questions
  in REQUIREMENTS.md.

> Currently driven by a single hard-coded mock plasmid (pACYC177, 3941 bp) with mock
> features. No file loading yet.

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
| Toolbar `+` / `−` / Fit | Zoom in / out / fit whole plasmid |
| Zoom % box | Set zoom directly |
| Hover | Base / residue readout in status bar |
| Inspector › Linear View | Toggle circular ↔ linear rendering |
