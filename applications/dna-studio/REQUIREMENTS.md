# DNA Studio — Requirements (v0.1, layout shell)

A C++ / Qt 6 desktop DNA-editing application, layout inspired by **Geneious Prime**.
Theme follows the SYNTHETICA Lab design guidelines (VS Code dark, Lucide icons).

> **Scope of v0.1:** *Layout shell only.* Build the full window chrome and all four
> panes with mock/placeholder data. No real sequence parsing, editing, or algorithms yet.

---

## 1. Window layout (the 4-pane IDE structure)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Menu bar:  File · Edit · View · Tools · Sequence · Annotate&Predict · Help │
├──────────────────────────────────────────────────────────────────────────┤
│ Toolbar:  ◀ ▶ │ Add Export BLAST Workflows Align/Assemble Tree Primers …   │
├───────────────┬──────────────────────────────────────────┬────────────────┤
│               │ ┌ Filter ─────────────────── 1/27 · Cols ┐│                │
│  SOURCE TREE  │ │  Document table (Name·Desc·Modified·…)  ││  OPTIONS       │
│  (left dock)  │ │  ─────────── splitter ─────────────────││  INSPECTOR     │
│  Local        │ │ Tabs: Sequence·Annotations·Text·Lineage ││  "General"     │
│  NCBI/UniProt │ │  [ viewer sub-toolbar ]                 ││  (right dock)  │
│               │ │  ┌ circular / linear map canvas ┐       ││  checkboxes    │
├───────────────┴──────────────────────────────────────────┴────────────────┤
│ Status bar:  1,380 / 47,152 MB Memory          Mouse over base 2,917 (C)   │
└──────────────────────────────────────────────────────────────────────────┘
```

| Region | Qt construct | Notes |
|--------|--------------|-------|
| Menu bar | `QMenuBar` | 7 top menus, placeholder actions |
| Main toolbar | `QToolBar` (non-floatable) | Back/Forward + action buttons, Lucide icons, dropdown carets |
| Left: Source tree | `QDockWidget` + `QTreeWidget` | Collapsible hierarchy, per-node item counts, folder/db icons |
| Center | `QSplitter(Vertical)` as central widget | Top = document table, bottom = viewer |
| Center-top: Document list | `QTableView`/`QTableWidget` | Filter bar, "N of M selected", Columns toggle, sortable headers |
| Center-bottom: Viewer | `QTabWidget` | Tabs + sub-toolbar + `QGraphicsView` map canvas |
| Right: Options inspector | `QDockWidget` + checkboxes | "General" group, display toggles, zoom controls |
| Status bar | `QStatusBar` | Memory gauge (left), mouseover readout (right) |

All panels are **resizable** (splitters) and the side panels are **dockable / closable**
via `QDockWidget`.

---

## 2. Component inventory

### 2.1 Menu bar
`File · Edit · View · Tools · Sequence · Annotate & Predict · Help`
(actions are stubs in v0.1; `View` toggles the dock panels.)

### 2.2 Main toolbar
Back ◀ · Forward ▶ · │ · Add · Export · BLAST · Workflows · Align/Assemble ·
Tree · Primers · Cloning · Help. Buttons show icon + text; several carry a
dropdown caret (`QToolButton` `MenuButtonPopup`).

### 2.3 Source tree (left)
- **Local**: Sample Documents, Alignments, Cloning, Contig Assembly, Genomes,
  Plasmids from NEB, Primers, Protein Documents, Tree Documents
- **Reference Features** › Geneious Plasmid Features (841)
- Deleted Items · Cloud · Operations · Luma
- **NCBI**: Gene, Genome, Nucleotide, Protein, PubMed, Structure, Taxonomy
- **UniProt**
- Each leaf/group shows an item count.

### 2.4 Document table (center-top)
Columns: ☑ · Name · Description · Modified · Organism · Sequence Length ·
Topology · Molecule Type · Taxonomy. Mock rows = the NEB plasmid set
(LITMUS 28i, pACYC177/184, pBR322, pET11c, pGPS1.1…). Header strip:
`Filter` button, `1 of 27 selected`, `Columns` button.

### 2.5 Viewer (center-bottom)
- Tabs: `Sequence View · Annotations · Text View · Lineage · Info`
- Sub-toolbar: Extract · R.C. · Translate · Add/Edit Annotation · Allow Editing ·
  Annotate & Predict · Save · (right) zoom %, fit buttons
- Canvas: `QGraphicsView` showing a **mock circular plasmid map** (outer ring,
  bp ruler ticks, a few colored annotation arcs, center label `pACYC177 / 3,941 bp`).

### 2.6 Options inspector (right)
Group **General**. Toggles: Colors (ACGT) · Graphs · Annotations · Complement ·
Translation · Restriction Sites · Circular Overview · Linear View · Wrap ·
Show Name · Show Description. Each row may have an `Options` affordance.
Zoom controls at top.

### 2.7 Status bar
Left: `1,380 / 47,152 MB Memory`. Right: `Mouse over base 2,917 (C)` (mock).

---

## 3. Theme (SYNTHETICA — VS Code dark)

Applied via a Qt stylesheet (`resources/theme.qss`). Tokens:

| Token | Hex |
|-------|-----|
| bg-primary | `#1e1e1e` |
| bg-secondary | `#252526` |
| bg-tertiary | `#2d2d2d` |
| bg-hover | `#2a2d2e` |
| bg-active | `#37373d` |
| bg-input | `#3c3c3c` |
| border | `#3c3c3c` |
| text-primary | `#cccccc` |
| text-secondary | `#9d9d9d` |
| text-muted | `#6e6e6e` |
| accent-blue | `#569cd6` |

Font: **Inter** (fallback to system). Icons: **Lucide** SVGs in
`resources/icons/` (a starter set is hand-authored in Lucide style; drop real
Lucide SVGs in to replace).

---

## 4. Non-goals for v0.1
- No file I/O / FASTA / GenBank parsing
- No real sequence editing, translation, restriction, alignment, or BLAST
- No persistence/settings
- Single hard-coded mock dataset

---

## 5. Open questions (to refine before v0.2)
1. **Sequence engine**: build our own model (`Sequence`, `Annotation`, `Feature`)
   or wrap an existing C++ bioinformatics lib (e.g. SeqAn, Biopp)?
2. **File formats** to support first: FASTA, GenBank (.gb), SnapGene (.dna)?
3. **Linear vs circular** map — which to implement first in v0.2?
4. **Editing model**: read-only viewer first, or in-place sequence editing early?
5. **Project/library storage**: flat files vs SQLite document store (Geneious uses
   a local DB)?
6. **Platform priority**: macOS only first, or cross-platform from the start?
