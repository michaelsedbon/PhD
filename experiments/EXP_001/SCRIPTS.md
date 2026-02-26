# EXP_001 — Script Index

All Python scripts for the MoClo genome tiling pipeline.  
**Viewer → [michaelsedbon.github.io/PhD/](https://michaelsedbon.github.io/PhD/)** · **[README](moclo-viewer-v3/README.md)**

## Core Pipeline

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `pipeline_v2.py` | **Main pipeline** — tiles genome, assigns overhangs, designs primers, runs domestication | `data/MG1655.gb`, `data/tiles.csv` | `data/v2_tiles.csv`, `data/v2_lvl1_groups.csv`, `data_bundle_v2.json` |
| `primer_design.py` | Primer design utilities (Tm calculation, BsaI adapters) | — | Imported by `pipeline_v2.py` |
| `restriction_utils.py` | BsaI site scanning and junction conflict detection | — | Imported by `pipeline_v2.py` |

## Analysis & Enrichment

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `pcr_simulation.py` | Simulate PCR reactions, predict product sizes, check amplification feasibility | `data/v2_tiles.csv`, `data/MG1655.gb` | `data/pcr_simulation.csv` |
| `domestication_primers.py` | Design mutagenic OE-PCR primers for BsaI site removal | `data/v2_tiles.csv`, `data/MG1655.gb` | `data/domestication_primers.csv`, `data/domestication_subfragments.csv` |
| `extract_gene_products.py` | Extract gene names, products, and functional categories from GenBank | `data/MG1655.gb` | `data/gene_products.json` |
| `enrich_kegg_pathways.py` | Fetch KEGG pathway annotations for all genes | `data/gene_products.json` | `data/gene_products.json` (enriched with pathways) |
| `fetch_kegg_reactions.py` | Download KEGG reaction diagrams for pathway visualization | `data/gene_products.json` | `data/kegg_reactions/` |
| `analyze_v2_lvl1.py` | Compute Lvl1 group statistics, clonability scores, QC metrics | `data/v2_tiles.csv`, `data/v2_lvl1_groups.csv` | Terminal output / analysis |

## GenBank Export

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `export_genbank_clones.py` | Generate annotated Lvl0 clone GenBank files (pICH41308 backbone + insert) | `data/v2_tiles.csv`, `data/domestication_primers.csv`, backbone `.gbk` | `data/genbank_clones/tile_XXX.gb` (686 files) |
| `export_lvl1_assemblies.py` | Generate annotated Lvl1 assembly GenBank files (15-tile Golden Gate products) | `data/v2_tiles.csv`, `data/v2_lvl1_groups.csv`, `data/domestication_primers.csv` | `data/genbank_lvl1/lvl1_group_XXX.gb` (46 files) |
| `export_primer_genbank.py` | Generate annotated GenBank files for all primers (amplification + mutagenic + subfragment) | `data/v2_tiles.csv`, `data/domestication_primers.csv`, `data/domestication_subfragments.csv` | `data/genbank_primers/` (2,698 records) |

## Typical Run Order

```bash
cd experiments/EXP_001

# 1. Core pipeline (tiles, primers, domestication)
python3 pipeline_v2.py

# 2. Post-pipeline analysis
python3 pcr_simulation.py
python3 domestication_primers.py
python3 extract_gene_products.py
python3 enrich_kegg_pathways.py
python3 fetch_kegg_reactions.py

# 3. GenBank export
python3 export_genbank_clones.py
python3 export_lvl1_assemblies.py
python3 export_primer_genbank.py
```

## Data Files

| File | Description |
|------|-------------|
| `data/MG1655.gb` | E. coli K-12 MG1655 genome (GenBank, U00096.3) |
| `data/tiles.csv` | V1 tile boundaries (input) |
| `data/v2_tiles.csv` | V2 tiles with primers, overhangs, domestication status |
| `data/v2_lvl1_groups.csv` | Lvl1 group summaries |
| `data/domestication_primers.csv` | Mutagenic primers for BsaI removal |
| `data/domestication_subfragments.csv` | OE-PCR subfragment details |
| `data/pcr_simulation.csv` | PCR simulation results |
| `data/gene_products.json` | Gene annotations + KEGG pathways |
| `data/genbank_clones/` | 686 Lvl0 clone GenBank files |
| `data/genbank_lvl1/` | 46 Lvl1 assembly GenBank files |
| `data/genbank_primers/` | 2,698 primer GenBank records (by_tile/, by_group/, combined) |
