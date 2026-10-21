# What Claude can do in this lab — capability registry

The single, living list of everything the AI agent can do in this PhD workspace. Skim this to
remember what's available. Kept in sync as capabilities are added (see "Maintenance" at the end).

> **Do these need to be skills/workflows?** Not to *use* — I can call any installed tool or
> connected service directly. Wrapping matters for **reliability + memory**: a capability is
> "wired in" when it's one of (a) an **MCP tool** (first-class, e.g. the Geneious bridge), (b) a
> **script** in `scripts/`, or (c) a **skill/workflow** in `.agent/`. Everything wired in is
> listed below and, for lab skills/workflows, indexed in [.agent/README.md](.agent/README.md).

---

## 1. Geneious (live, via the bridge)

The "PhD Lab Tools" plugin runs a localhost bridge; I drive Geneious through MCP tools.

**Bridge 1.1 (2026-08-30)** adds folder control: `geneious_list_folders` (browse the database
tree by path), `geneious_create_folder`, and a `folder:` argument on `geneious_import_genbank`
that files a document at an arbitrary path, creating parents as needed. Before 1.1 imports could
only land in whatever folder was selected in the UI. Requires installing
`applications/geneious-addgene-plugin/build/AddgeneImporter.gplugin` and restarting Geneious —
check `geneious_health` reports `"bridge": "1.1"`.
**Bridge 1.3 (2026-08-31)** makes importing work from **files on disk**:
`geneious_import_genbank(file_path=…)` has Geneious read the file itself, so a 12 kb construct
no longer has to be pasted through the model's context, and formats only Geneious can parse
(SnapGene `.dna`, `.embl`, `.ab1`) work too. `split_records` (default true) turns a multi-record
file into **one named document per record** — needed for primer lists, which used to collapse
into a single sequence list; `split_records: false` gives that single list back. The bridge also
picks the importer itself now, so Geneious never stops on a modal *"which format is this?"*
dialog that an agent cannot answer.
Details: [applications/geneious-addgene-plugin/BRIDGE.md](applications/geneious-addgene-plugin/BRIDGE.md).

**Bridge 1.4 (2026-08-31)** closes the remaining basic gaps. Documents are now addressable
without the user clicking: `geneious_list_documents(folder)` lists a folder's contents and
`geneious_find_documents(name|text)` searches the database. Full CRUD arrives —
`geneious_export_document` (to a file on disk, the inverse of `file_path` import),
`geneious_move_documents`, `geneious_rename_document`, `geneious_delete_documents`. Editing is no
longer add-only: `geneious_remove_annotations` corrects features, `geneious_edit_sequence` mutates
residues in place, `geneious_set_metadata` writes real document notes (**this is where provenance
belongs now** — no more faking it as a feature). And Geneious's own algorithms are reachable via
`geneious_list_operations` → `geneious_run_operation`, which beats recomputing biology here
because the result is reproducible in the GUI.

⚠ **Destructive tools ask the user first** — delete, remove/replace annotations, edit a sequence,
overwrite a file. They refuse without `confirm: true`, and that flag records the *user's* consent,
not mine. See [CLAUDE.md](CLAUDE.md#destructive-actions-mandatory--ask-first-every-time).

| Capability | How |
|---|---|
| Check Geneious is up | `geneious_health` |
| List documents in a folder, or the **selected** ones | `geneious_list_documents(folder?)` — folder needs bridge ≥ 1.4 |
| Find a document by name or free text | `geneious_find_documents(name\|text, folder?)` — bridge ≥ 1.4 |
| Metadata, notes and folder without the sequence | `geneious_document_info(urn)` — bridge ≥ 1.4 |
| Read a document as annotated GenBank | `geneious_get_document(urn)` |
| Export documents to a file on disk | `geneious_export_document(urns, path, format)` — bridge ≥ 1.4 |
| Add annotations/features to a document | `geneious_annotate(urn, annotations)` |
| Remove or replace annotations ⚠ | `geneious_remove_annotations`, `geneious_annotate(mode="replace")` — bridge ≥ 1.4 |
| Mutate a sequence in place ⚠ | `geneious_edit_sequence(urn, edits)` — bridge ≥ 1.4 |
| Record provenance as a document note | `geneious_set_metadata(urn, note=…)` — bridge ≥ 1.4 |
| Move / rename / delete documents ⚠ | `geneious_move_documents`, `geneious_rename_document`, `geneious_delete_documents` — bridge ≥ 1.4 |
| Show the user a result in the UI | `geneious_select_documents(urns)` — bridge ≥ 1.4 |
| Run Geneious's own algorithms (align, primers, restriction, assembly) | `geneious_list_operations` → `geneious_run_operation` — bridge ≥ 1.4 |
| Poll a long-running operation | `geneious_job_status(job)` — bridge ≥ 1.4 |
| Import a file from disk (`.gb`/`.fasta`/`.dna`/…) | `geneious_import_genbank(file_path, folder?, split_records?)` — bridge ≥ 1.3 |
| Import a multi-record file as one document per record | same, `split_records: true` (default) — bridge ≥ 1.3 |
| Import a new sequence from text | `geneious_import_genbank(genbank, name, folder?)` |
| Browse the database folder tree by path | `geneious_list_folders(path?, depth?)` — bridge ≥ 1.1 |
| Create a folder (parents auto-created) | `geneious_create_folder(path)` — bridge ≥ 1.1 |
| Right-click a doc → export + copy path for me | **Copy reference for Claude** (menu) |
| Export a **whole folder** to CSV (name + sequence) | **File → Export → Documents from Selected Folder…** → format *CSV — sequence name and sequence*; or right-click a selection → **Export sequences to CSV…** |
| Import annotated plasmids from Addgene | **Tools → Import from Addgene…**, or `scripts/addgene_fetch.py` / `addgene_to_geneious.sh` |
| Predict 3D structure of a document's CDSs (ESMFold on NVIDIA NIM) | Right-click → **Fold with ESMFold (NVIDIA)…** |
| Rotate/inspect predicted structures, coloured by pLDDT | **3D Structure (ESMFold)** tab on the document |

**ESMFold folding** — each CDS annotation is translated and folded separately, so a plasmid
yields one model per coding part. Models are stored as PDB files under
`geneious_exchange/structures/<urn>/` (readable by me, PyMOL and ChimeraX) and listed in the 3D
tab.

Backends (2026-08-29): NVIDIA's hosted endpoint `health.api.nvidia.com/v1/biology/nvidia/esmfold`
now returns HTTP 404 *"Function 'a68c59e0-…': Not found for account …"* — the function has been
unpublished, while sibling biology NIMs (MolMIM, ProteinMPNN, Boltz-2) still answer on the same
key, so it is not a key or permission problem. The plugin therefore falls back automatically to
Meta's public **ESM Atlas** API (`api.esmatlas.com/foldSequence/v1/pdb/`, no key, **400-residue
cap**, pLDDT returned 0–1 and rescaled to 0–100 by the plugin). NVIDIA timings when it worked:
~1 s for 130 aa, ~10 s for 800 aa, 1024-residue cap, ~40 requests/min. Chains >400 aa need a
local ESMFold run (GPU server, `fair-esm`) or Boltz-2 until NVIDIA republishes the function.
API key lives in `~/.nvidia_esmfold.json` (mode 600, outside the repo) — never commit it.

## 2. Bioinformatics toolkit (local, offline) — first-class MCP tools

Exposed as the **`bioinfo` MCP server** (`scripts/bioinfo/bioinfo_mcp.py`, runs under
`.venv-bioinfo`) — I call these directly, **no per-task script needed**. All tested against
pJEC779. Verified survey + citations: [BIOINFORMATICS_TOOLKIT.md](BIOINFORMATICS_TOOLKIT.md).

| MCP tool | Capability | Engine | Status |
|---|---|---|---|
| `bioinfo_seq_info` | length, GC%, composition | Biopython | ✅ live |
| `bioinfo_find_orfs` | ORF/gene finding → coords + protein | Pyrodigal | ✅ live |
| `bioinfo_restriction_sites` | restriction map, unique-cutter aware | Bio.Restriction | ✅ live |
| `bioinfo_design_primers` | PCR primers + Tm | primer3-py | ✅ live |
| `bioinfo_codon_optimize` | constraint-based codon opt for a host | DNAChisel | ✅ live |
| `bioinfo_predict_rbs` | RBS / translation-initiation rate | OSTIR | ✅ live |
| *(notebook)* [`tools/rbs_calculator/`](tools/rbs_calculator/README.md) | RBS **workbench**: per-start-codon TIR, SD:16S base-pairing register drawn out, ΔG budget, UTR library screen, saturation-mutagenesis heatmap, design-to-target-TIR + expression ladder | OSTIR + ViennaRNA | ✅ live (kernel `PhD bioinfo (OSTIR)`) |
| `bioinfo_predict_promoters` | σ70 promoter detection + strength + −35/−10 boxes | Salis Promoter Calculator | ✅ live |
| `bioinfo_annotate_plasmid` | identify KNOWN parts (promoters/oris/markers/tags/registry parts + vestigial fragments) w/ %identity + DB | pLannotate | ✅ live |
| *(cloning sim: PCR/Gibson/digest)* | pydna | installed, tool *(planned)* |
| *(transformer codon opt)* | **CodonTransformer** | *(planned — torch + weights)* |
| *(Golden Gate / MoClo assembly sim)* | **DNA Cauldron** | *(planned)* |
| *(Rho-independent terminators — detection)* | **TransTermHP** | *(planned — `conda install -c bioconda transtermhp`, osx-arm64 available)* |
| *(Terminator **strength**)* | **Chen 2013 biophysical model** | `Notes/Note_015/t7oracle_stage1/scripts/07_terminator_model.py` — validated vs all 582 published terminators; R² 0.40, ~3× error. Ranking tool, not calibrated. |
| *(protein structure from CDS)* | **ESMFold** / AlphaFold MCP | *(AlphaFold MCP live; ESMFold planned)* |

**MoClo parts library** — `geneious_exchange/kits/` — 212 parts, renamed to MoClo IDs and
annotated with **BsaI/BbsI sites + 4-nt fusion-site overhangs** (`scripts/addgene_kit_import.py`
downloads + sorts; `scripts/moclo_annotate.py` renames + annotates). CIDAR MoClo (Densmore, 90)
+ CIDAR MoClo v1 (Murray, 122), organized by part type. Standard from the **CIDAR MoClo Vol. I
guide** ([local PDF](geneious_exchange/kits/_docs/CIDAR_MoClo_Vol_I_guide.pdf) ·
[source](https://media.addgene.org/cms/filer_public/e3/64/e364349e-eb5a-4ee7-a3a7-d615aa88f817/180529_cidar_vol_i_guide.pdf)):
BsaI overhangs GGAG=A TACT=B AATG=C AGGT=D GCTT=E; part types A-B promoter, B-C UTR, C-D CDS,
D-E terminator, E-A vector. Drag a kit folder into Geneious to load it (preserves sub-folders).

*New `bioinfo` tools require a Claude Code reload to appear in this session (like `geneious`).*

## 2b. Structure prediction & protein–protein binding

| Capability | How | Notes |
|---|---|---|
| **Co-fold a complex (2+ chains)** — pose + confidence | **Boltz-2** via NVIDIA NIM `health.api.nvidia.com/v1/biology/mit/boltz2/predict` | ✅ live on the existing `~/.nvidia_esmfold.json` key. **~1.5 s** for a ~100-aa 2-chain job. Returns `iptm_scores`, **`pair_chains_iptm_scores`** (per-chain-pair matrix — the right readout for 3+ chains), `confidence_scores`, `complex_plddt`/`iplddt`, `ptm`, `pde`, `affinities` (small-molecule only). Takes **sequences, not structures**. Weight version not pinned. Driver: [scripts/boltz_complex_screen.py](scripts/boltz_complex_screen.py) |
| **Multimer cross-check** | **AlphaFold2-Multimer** NIM `…/deepmind/alphafold2-multimer` | ✅ live on the same key; takes `sequences: [...]` |
| **Boltz-2 offline** | `.venv-boltz/bin/boltz` (2.2.1, Python 3.12, 1.1 GB) | ⚙ installed, **weights not yet downloaded**. Mac M3 Max = MPS only; Boltz's fast kernels are CUDA-only, so expect CPU fallback and hour-scale runs. Use only for offline work, custom MSAs, extra sampling, templates. **The hosted endpoint is the default.** |
| **Binding ΔG / Kd from a complex structure** | **PRODIGY 2.4.0** in `.venv-bioinfo` — `prodigy <file.pdb> --selection A B` | CPU, instant, uses structures you already have. ⚠ **Contact-count driven**: it rewards large sprawling interfaces and returns confident numbers for wrong poses. Validated on *binary, rigid* complexes only. Never quote without an independent pose check. |
| **Antibody/VHH numbering + CDRs** | ANARCI 2026.2.13.2 / abnumber 0.4.4 (`.venv-bioinfo`), IMGT scheme | Used to test whether a predicted interface is CDR-borne |
| **Interface contacts, BSA, figures** | gemmi + PyMOL (`~/.local/bin/pymol`, `pymol-oss` env) | |
| ESMFold monomer | ESM Atlas API (400-aa cap) | NVIDIA's ESMFold NIM is unpublished (404) — see §1 |

⚠ **Known failure modes, established empirically** in
[geneious_exchange/provenance/MS_C_XXX_payload_complexes.md](geneious_exchange/provenance/MS_C_XXX_payload_complexes.md):
ipTM **collapses on chains containing long IDRs** (a matched positive control scored 0.26 on a
full 102-aa disordered antigen vs 0.93 on its 16-aa epitope), and is **uninformative for very
short epitopes** (a 4-mer scored 0.82–0.87 against three different nanobodies, cognate or not).
**Always run non-cognate decoys and a matched positive control** — a bare ipTM is not
interpretable on its own, and ipTM is not affinity.

## 2c. Plasmid & construct figures

| Capability | How | Notes |
|---|---|---|
| **Annotated plasmid map from a `.gb`** — circular, linear, and a zoom panel | [scripts/figures/plot_plasmid.py](scripts/figures/plot_plasmid.py) `<file.gb> [--zoom a:b] [--nested-on-circle] [--drop-scars] [--color-by-tu]` | ✅ live. Circular ring via **pyCirclize**, linear/zoom via **dna_features_viewer**. Writes PDF (vector, for VectorCraft/Illustrator) + 300 dpi PNG next to the input. Deps: `pip install dna_features_viewer pycirclize` (installed in `/opt/anaconda3`). |
| **Design vs sequencing identity panel** — "the clone is correct" in one figure | [scripts/figures/plot_alignment.py](scripts/figures/plot_alignment.py) `<design.gb> <sequencing.gb> [--label-a X --label-b Y]` | ✅ live. Same palette/legend as `plot_plasmid.py` (imports them, so the two never drift). Two feature tracks + an identity bar; prints identity %, mismatch count and their positions. |

⚠ **Treat both records as circular — this is the trap.** An assembler picks an arbitrary origin, so
a sequencing contig is usually *rotated* relative to the design and a naïve base-by-base diff
reports a catastrophic-looking ~96% for a perfect clone. `plot_alignment.py` searches all rotations
(and the reverse complement), reports the offset, and compares in the design's frame. It also
handles `join(...)` locations: a feature wrapping the origin has one part per piece, and collapsing
it to min..max draws one arrow across the whole plasmid.

**Validate before quoting a number.** A panel reading "0 mismatches" is only evidence if the code
can show one — plant a couple of SNPs into a copy of the sequencing file and confirm it reports
them with positions. Done for MS_C_031: 2 planted SNPs → 99.875%, flagged at the right coordinates.

Worked example — **MS_C_031 vs MS_C_031_col3: 1600/1600 bp (100.0000%), 0 mismatches, 0 gaps,
contig rotated 58 bp** (col3 base 1 = design position 59). Note this compares two *consensus*
sequences: it says the assembly equals the design, not that the clone is pure — coverage depth is
a separate claim.

What it does to a Geneious export, and why — a raw `.gb` from Geneious carries 25+ features, most
of them cloning bookkeeping, and drawn naively it is unreadable:

- **Filters** `primer_bind`, `Fragment`, `ligation`, `source`, `gene`, `mRNA` and 1-bp
  `regulatory` points that duplicate a promoter already drawn. Keeps `rep_origin`, `CDS`,
  `promoter`, `protein_bind`, `misc_structure`, `misc_feature`, `terminator`.
- **Colours by feature *type*, not per feature**, so the same element is the same colour across
  every panel of a figure. Palette + legend wording live in `TYPE_COLORS` / `TYPE_LABELS`;
  long Geneious labels are shortened in `RENAME`.
- **Nesting rule** — a feature strictly inside a larger feature of a different type is dropped
  from the *circular* map (it crowds a narrow sector) but kept in the linear views, where
  dna_features_viewer stacks it on its own row. `--nested-on-circle` overrides this for sparse
  constructs. This is why a dense insert wants `--zoom` on that region as its own panel.
- **Legends every graphical element** — feature colours, the GC-content band, the GC-skew line
  and the bp scale ([CLAUDE.md plotting rules](CLAUDE.md#plotting-rules)).

**Multi-gene constructs need both extra flags.** On a 12.8 kb T7-ORACLE build the raw map is
unreadable — ~45 labels, with Gibson arms and SD sequences labelled while the genes hide inside
the TU blocks. `--drop-scars` removes cloning bookkeeping (`SCAR_PATTERNS`), and `--color-by-tu`
colours every feature by the **transcription unit** it sits in, using the TU schematic's palette
(`TU_COLORS`: TU1 green, TU2 orange, TU3 blue, TU4 pink) so a map and that diagram can share a
slide. TUs come from `TU<n>` block annotations when present, else from promoter→terminator pairs.
Duplicate annotations of one element (terminator + its 5'/3' portions, a marker called twice) are
labelled once, on the longest instance.

Tested on MS_C_025 (phiOR secondary T7 ori), MS_C_031 (ori-phi1.1 primary T7 ori),
MS_C_018 and MS_C_030 (12,823 bp, four TUs; MS_C_030 carries the PA-RNAP fusion in TU2).
⚠ Not wired into the Nature house style ([scripts/figures/figstyle.py](scripts/figures/figstyle.py)) —
that targets 89 mm panels at 6 pt, these render at 7.5 in. Restyle in VectorCraft, or size it
down first, if a map goes into a `/figure` build.

## 3. Connected AI services (MCP)

| Service | What | Status |
|---|---|---|
| **AlphaFold** | Fetch/analyze predicted structures, confidence (pLDDT/PAE), export for PyMOL/ChimeraX | ✅ connected |
| **pymol** ([agentic-pymol](applications/agentic-pymol/)) | Two-way control of a **live** PyMOL GUI session — manipulate the scene you're looking at, read back RMSDs, contacts, coords, sequences | ⚙ registered; needs GUI + *Plugin → agentic-pymol → Start Listening* each session (port 9877) |
| **biomcp** | Genes, variants, clinical trials, drug/disease lookup, article search | ✅ connected |
| **PubMed** | Article search / full text / citations | ⚠ needs auth (`/mcp`) |
| **Notion** | Read/write lab Notion (experiment pages) | ✅ connected |
| **Airtable** (official, `https://mcp.airtable.com/mcp`) | Read/write the PhD base (`appKnwstP97N9d4yF`: Strains, Constructs, MoClo_Parts) — records, schema/fields, linked-record resolution, views, interfaces, automations (~43 tools) | ⚙ registered in [.mcp.json](.mcp.json); needs a Claude Code restart to load. Auth = PAT from `config.yaml`. Fallback without MCP: [scripts/fetch_airtable.py](scripts/fetch_airtable.py) (read-only) + REST API |
| **Google Drive** | Search/read/create Drive files | ✅ connected |
| **VectorCraft** (`~/bin/vectorcraft-cli/vectorcraft-cli mcp`) | Live control of the VectorCraft vector-illustration app: draw shapes/paths/text, place SVG/PDF, effects, render previews, export SVG/PDF/PNG — every menu item is a command (`command_list` / `command_run`). For figures, circuit schematics, graphical abstracts. SBOL Visual 3.0 glyphs (159 SVGs + spec + font) in [Resources/SBOL_Visual/](Resources/SBOL_Visual/) — import with `file.place {path, rect}` | ✅ connected (2026-10-20). Live mode needs the app started with `--control 7979`, else headless fallback. All tools allowed in [.claude/settings.json](.claude/settings.json) |
| Gmail, Google Calendar | | ⚠ need auth |

**Geneious ➜ Airtable oligo sync** — [tools/airtable_sync/](tools/airtable_sync/README.md) — a
notebook the user runs: pushes every (or a chosen subset of) `MS_O_` document from `PhD/MS_O_XXX`
into the Airtable *Oligos* table — residues → `Sequence`, document Description → `Usage
Descritption`, the GenBank export → the `gb file ` attachment. It also **works out how each primer
is used** by scanning every nucleotide document under `PhD/` (~223 docs, 6 s): documents that *name*
the primer → `Used in constructuct`; wherever its 3′ 18 nt anneal → `Possibly Bind Construct`; the
strand of that match → `Direction`; keywords in the description → `Usage` *(heuristic)*. Direction
and Usage were validated against the hand-entered values (36/36 and 33/33 agree). Backs up both
databases to `BACKUP/geneious_airtable_sync/<stamp>/` first, fills only empty cells (conflicts shown
side by side, never overwritten unless asked), only ever *adds* links, appends attachments, deletes
nothing. `DRY_RUN = True` by default.

**Figure team (`/figure`)** — the main session becomes an orchestrator that talks to the PI and
dispatches four subagents ([.claude/agents/](.claude/agents/)): `figure-science` (story, panel
claims, data provenance, questions for the PI), `figure-toolsmith` (notation standards + packages,
e.g. SBOL Visual; registry [VISUAL_LIBRARIES.md](.agent/figure_guidelines/VISUAL_LIBRARIES.md)),
`figure-design` (Nature spec compliance — [NATURE_FIGURE_SPEC.md](.agent/figure_guidelines/NATURE_FIGURE_SPEC.md),
read-only on the canvas) and `figure-builder` (sole VectorCraft writer). Figures live in
[figures/](figures/FIG_INDEX.md). Tooling in [scripts/figures/](scripts/figures/):
`audit_figure.py` (automated Nature checks + colour-blindness renders), `fork_notebook.py` (copy the
PI's analysis notebooks into a figure, restyle the copy, run under a write-guard — originals never
edited), `figstyle.py` + `nature_style.mplstyle` (matplotlib + plotly house style).

## 4. Literature & data

- Verify + fetch papers: `papers_txt/CATALOG.md` → Sci-Hub/Zotero → extract (see the citation rules in [CLAUDE.md](CLAUDE.md)).
- Open a paper in Zotero: `open "zotero://open-pdf/library/items/KEY"`.
- **`⌘⌥Z` in VS Code** — cursor on any markdown line carrying a Zotero link or item key opens that paper in
  Zotero's reader. Needed because VS Code's markdown preview only follows `http:`/`https:`/`mailto:`/`vscode:`
  and silently drops `zotero://`. Wiring: [scripts/zotero_open.py](scripts/zotero_open.py) +
  [.vscode/tasks.json](.vscode/tasks.json) + a user keybinding. Also usable standalone:
  `python3 scripts/zotero_open.py --key XA7S6IPV`.
- Add papers to Zotero programmatically (web API v3, credentials in `config.yaml`): create items from Crossref
  metadata by DOI, dedupe against the library by DOI, and upload PDF attachments. Item keys are stable across
  the server and the local library, so `zotero://` links written into docs keep working after sync.
- Read/unread tracking in Zotero via the [Zotero Reading List](https://github.com/Dominic-DallOsto/zotero-reading-list)
  plugin (New / To Read / In Progress / Read / Not Reading; Alt+1–5). Status is written to each
  item's **Extra** field as `Read_Status:` and `Read_Status_Date:`, so it is queryable from
  `zotero.sqlite` or any export — usable to filter unread papers when building reading lists.
- Download Addgene plasmids by article/ID (§1).

## 5. Skills & workflows (lab)

Full index: [.agent/README.md](.agent/README.md) (15 skills, 24 slash-command workflows) and
[.agent/MANIFEST.md](.agent/MANIFEST.md). Experiment scaffolding, Notion sync, plotting, etc.

### Structural biology (installed 2026-08-30, user-scope `~/.claude/skills/`)

| Skill | What | Notes |
|---|---|---|
| **proteus** ([repo](https://github.com/jvogan/proteus), MIT) | One skill covering PyMOL + ChimeraX + AlphaFold DB + RCSB PDB + **UniProt** + Rosetta. 50 scripts: `uniprot_lookup.py`, `fetch_alphafold.py`, `pae_report.py`, `interface_report.py`, `pocket_report.py`, `variant_map.py`, `target_dossier.py`, … | **Needs Python ≥3.10 — the default `python3` here is 3.9.8 and every script fails on it.** Run with `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`. Self-check: `scripts/proteus_doctor.py`. Supersedes the uninstalled `uniprot-database` skill. |
| **pymol-claw** ([repo](https://github.com/BioTender-max/PyMolClaw), MIT) | 13 headless figure scripts — `align` (RMSD), `binding_site`, `ppi`, `active_site`, `surface`, `mutation`, `distance`, `spectrum` (B-factor/pLDDT), `goodsell`, `density`, `ensemble`, `animation`, `overview`. Emits PNG + PML + PSE. | Runs on `python3` 3.9 fine (stdlib + subprocess). **Copies every output to `~/Desktop` unasked.** |

Both locate PyMOL via `shutil.which("pymol")`, and nothing was on PATH, so
[~/.local/bin/pymol](file:///Users/michaelsedbon/.local/bin/pymol) is a shim. Editing no repo file,
it survives `git pull`.

> ⚠ **Do not use `/Applications/PyMOL.app` for figures.** That bundled PyMOL 3.0.4 is the
> Schrödinger build with a lapsed licence, and it burns a **"License expired" watermark into the
> middle of every rendered image**. Geometry and analysis are fine; the output is not publishable.
> The shim therefore points at **`/opt/anaconda3/envs/pymol-oss/bin/pymol`** — conda-forge
> `pymol-open-source` 3.1.0, unwatermarked (`conda create -n pymol-oss -c conda-forge
> pymol-open-source python=3.11`).

## 6. Rules I follow automatically

- **Plasmid provenance** — every sequence edit is logged in 3 layers with verified citations ([CLAUDE.md](CLAUDE.md#plasmid-provenance-mandatory-when-editing-sequences), [spec](geneious_exchange/provenance/README.md)).
- **Verify before citing** — never cite an unverified paper.
- **Plot legends** — every graphical element labeled.
- **Design guidelines** — dark-theme UI system for lab apps.

---

## Maintenance

When a capability is added (new MCP tool, script, skill, or installed tool), add a row here in
the same session. This file is referenced from [CLAUDE.md](CLAUDE.md) so it stays discoverable.
Legend: ✅ ready · ⏳ installing · ⚠ needs auth · *(planned)*.
