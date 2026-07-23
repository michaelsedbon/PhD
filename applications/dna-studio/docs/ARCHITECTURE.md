# DNA Studio → Lab Suite: Architecture & Scope

**Status:** Phase 0 (workspace shell) — in progress
**Last updated:** 2026-07-21

## Vision

One desktop app that hosts several *workspaces*, each of which looks and behaves like
its own dedicated piece of software, with a shared data core that lets objects in one
workspace link to objects in another.

Three workspaces to start:

| Workspace       | Purpose                                              | Operates on                       |
|-----------------|------------------------------------------------------|-----------------------------------|
| **DNA Studio**  | Sequence / construct design & annotation (existing)  | sequence files / `Construct`      |
| **Lab Notebook**| Obsidian-style markdown editor over the PhD repo     | the real `.md` files on disk      |
| **Projects**    | Live view + editing of the Mermaid subsystem maps    | the real `FLOWCHART/*.mmd` files  |

The user switches workspaces from a left **activity bar** (VS Code style) and from the
**View menu** (⌘1 / ⌘2 / ⌘3). Each switch swaps the whole UI: toolbar, side panels,
menus, and status bar.

### Design decisions (from the 2026-07-21 requirements session)

- **Notebook = a markdown vault, not a new data model.** It behaves like Obsidian:
  browse and edit the real `.md` files in the PhD repo (`experiments/EXP_XXX/…`,
  `projects/…`), with live preview and `[[wiki-links]]`. It links *directly* to the
  existing experiment folders rather than storing note content separately.
- **Projects = the existing Mermaid flowcharts, editable in-app.** The
  `projects/*/FLOWCHART/` system (`.mmd` blocks + `flowchart-core.js` + `render.html`)
  is already a full custom renderer with category colours, a `@REFS/@PARAMS/@NOTES`
  table parser, and clickable Zotero/Notion/PDF links. We **reuse it verbatim** by
  embedding `render.html` in a `QWebEngineView`, with a source-editor pane beside it
  so a `.mmd` edit re-renders live. No re-implementation, no drift.
- **Repo/Zotero links are first-class.** `zotero://`, `notion://`, and
  `/papers/…` / `experiments/EXP_XXX` links resolve from inside the app.
- **Storage = a single `.labproj` file.** It holds only app-level data — the vault
  root path, the cross-link graph, and settings — while *content* stays as the real
  repo files. `.labproj` is the index/graph; the repo is the truth.

### Rendering strategy

| Content            | Renderer                    | Why                                           |
|--------------------|-----------------------------|-----------------------------------------------|
| Markdown notes     | Qt-native `QTextEdit::setMarkdown` (preview) + `QPlainTextEdit` (source) | No heavy dep; CommonMark + GFM tables built in |
| Mermaid flowcharts | `QWebEngineView` → existing `render.html` | Full fidelity with the existing custom engine; live edit |

`QWebEngineView` is available in the installed Homebrew Qt 6. The flowchart page uses
`fetch()` to assemble block files, which needs a real HTTP origin. The Projects
workspace therefore runs an **in-process** static file server (`HttpServer`, a small
`QTcpServer` on `127.0.0.1`) rooted at the repo, and points the web view at
`http://127.0.0.1:<port>/projects/<project>/FLOWCHART/render.html`.

Because the server lives *inside the app process*, it starts automatically on launch
and is torn down automatically on quit — no external `python`, works identically from
Finder or a terminal, and can never be orphaned. (Two earlier approaches were rejected:
a `python3 -m http.server` subprocess didn't spawn reliably under Finder's stripped
environment; a custom `QWebEngineUrlSchemeHandler` tripped `render.html`'s `fetch()`
guard because Chromium restricts `fetch()` over non-standard schemes.)

Caveat: `flowchart-core.js` imports Mermaid from `cdn.jsdelivr.net`, so the flowchart
needs internet to render (same as the existing browser workflow). Bundling Mermaid into
the repo would make it work offline.

## The key architectural idea: workspace shell

```
ShellWindow  (top-level QMainWindow — owns the global menu bar + activity bar)
│
├── Activity bar (left, fixed ~52px): DNA · Notebook · Projects   ← switches workspaces
│
└── QStackedWidget  (central)                       ← one page per workspace
     ├── DnaStudioWorkspace   (a child QMainWindow: own toolbar + Sources/Inspector docks)
     ├── NotebookWorkspace    (a child QMainWindow: own toolbar + entry list + editor)
     └── ProjectsWorkspace    (a child QMainWindow: own toolbar + board + inspector)
```

**Why child `QMainWindow`s?** Each workspace needs its own toolbars and dockable side
panels. A `QMainWindow` used as a child widget (`Qt::Widget` flag) gives every workspace
an independent set of toolbars + dock areas + status bar — so they really do feel like
separate apps. The shell only owns the menu bar and the activity bar.

**Menus.** On macOS only the top-level window's menu bar shows in the global bar, so the
shell owns it. On every switch the shell clears the menu bar and calls
`Workspace::populateMenus(menuBar())` on the newly-active workspace, then appends the
shell's own **View** (workspace switcher + full screen) and **Help** menus. Each
workspace therefore controls File / Edit / its module-specific menus.

### `Workspace` interface (src/Workspace.h)

```cpp
class Workspace : public QMainWindow {
    Workspace(parent) { setWindowFlags(Qt::Widget); }  // behave as a child widget
    virtual QString wsTitle() const = 0;      // "DNA Studio"
    virtual QString wsIconName() const = 0;   // resource icon key, e.g. "dna"
    virtual void populateMenus(QMenuBar*) = 0;// contribute File/Edit/module menus
};
```

Adding a fourth workspace later = write one `Workspace` subclass + register it in the
shell. Nothing else changes.

## Shared data core (Phase 2+)

The payoff is cross-linking. All three workspaces sit on top of one document store so a
notebook entry can point at a construct, a task can point at an entry, etc.

```
LabStore (single source of truth, persisted to a project file / SQLite)
├── Construct   { id, name, sequence, topology, features[], createdBy, links[] }
├── NoteEntry   { id, title, richText, date, tags[], links[] }
├── Project     { id, name, description, tasks[] }
└── Task        { id, title, status, assignee, due, links[] }

Link { fromType, fromId, toType, toId, relation }   // e.g. NoteEntry→Construct "used"
```

Every object has a stable `id` (UUID). A **`Link`** is a typed, bidirectional edge
between any two objects. UI affordances this unlocks:

- In a notebook entry: "🔗 Link construct" → picker → inline chip that opens the construct
  in DNA Studio.
- In DNA Studio, an Inspector tab **"Referenced in"** listing notebook entries / tasks
  that mention this construct.
- In a task: attach the construct(s) and notebook entries it depends on.
- Global **"Search Everywhere"** (already in the toolbar) queries across all object types.

Persistence: a `.labproj` bundle (JSON manifest + SQLite for entries/links, sequence
files on disk). Until then, workspaces keep their current in-memory sample data.

## Phasing

- **Phase 0 — Shell & switching (this session).** Extract the DNA UI into
  `DnaStudioWorkspace`. Add `ShellWindow` with activity bar + View-menu switcher.
  Add `NotebookWorkspace` and `ProjectsWorkspace` as *functional skeletons* (real
  layouts + sample content, no persistence). Everything switches cleanly.
- **Phase 1 — Flesh out each workspace's own features** (notebook editor, board DnD,
  etc.) driven by the design-requirements session that follows.
- **Phase 2 — `LabStore` + persistence** (`.labproj`, load/save, undo across the app).
- **Phase 3 — Cross-linking UI** (link pickers, "Referenced in" panels, global search).
- **Phase 4 — Integrations** (Notion sync, BLAST, export, templates).

## Open design questions (for the requirements session)

1. **Notebook**: freeform rich text, or structured/templated entries (protocol, result,
   observation)? Version history per entry? Signatures/timestamps for GLP-style rigor?
2. **Projects**: kanban board, Gantt/timeline, or both? Task ↔ experiment mapping to the
   existing `experiments/EXP_XXX` filesystem convention?
3. **Linking**: which relations matter (`used`, `produced`, `references`, `blocks`)?
   Should links be typed or freeform?
4. **Storage**: single `.labproj` bundle vs. a lab-wide database. Multi-user later?
5. **Identity**: reuse the PhD repo's `EXP_XXX` IDs and Zotero keys as first-class link
   targets?
