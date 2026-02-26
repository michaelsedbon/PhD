#!/usr/bin/env python3
"""Enrich gene_products.json with KEGG pathway annotations for E. coli K-12 MG1655.

Downloads gene→pathway mappings and pathway names from the KEGG REST API,
then maps bNNNN locus tags to gene names via the GenBank file.

Usage:
    python3 enrich_kegg_pathways.py
"""

import json
import re
import urllib.request
from pathlib import Path
from collections import defaultdict

GB_PATH = Path(__file__).parent / "data" / "MG1655.gb"
GP_PATH = Path(__file__).parent / "moclo-viewer-v3" / "public" / "gene_products.json"

# ── Broad "overview" pathway IDs to SKIP (too generic, not useful for grouping) ──
SKIP_PATHWAYS = {
    "eco01100",  # Metabolic pathways (catch-all)
    "eco01110",  # Biosynthesis of secondary metabolites
    "eco01120",  # Microbial metabolism in diverse environments
    "eco01200",  # Carbon metabolism
    "eco01210",  # 2-Oxocarboxylic acid metabolism
    "eco01230",  # Biosynthesis of amino acids
    "eco01232",  # Nucleotide metabolism
    "eco01240",  # Biosynthesis of cofactors
    "eco01250",  # Biosynthesis of nucleotide sugars
}


def fetch_kegg(endpoint: str) -> str:
    """Fetch text from KEGG REST API."""
    url = f"https://rest.kegg.jp/{endpoint}"
    print(f"  Fetching {url} ...")
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8")


def parse_genbank_locus_to_gene(gb_path: Path) -> dict[str, str]:
    """Parse bNNNN locus_tag → gene name from GenBank flat file."""
    with open(gb_path) as f:
        content = f.read()

    locus_to_gene = {}
    blocks = content.split("     CDS ")
    for block in blocks[1:]:
        gene_m = re.search(r'/gene="([^"]+)"', block)
        locus_m = re.search(r'/locus_tag="([^"]+)"', block)
        if gene_m and locus_m:
            locus_to_gene[locus_m.group(1)] = gene_m.group(1)
    return locus_to_gene


def main():
    # 1. Parse GenBank for locus_tag → gene name mapping
    print("Step 1: Parsing GenBank for locus tags...")
    locus_to_gene = parse_genbank_locus_to_gene(GB_PATH)
    print(f"  Found {len(locus_to_gene)} locus_tag → gene mappings")

    # 2. Fetch pathway names from KEGG
    print("\nStep 2: Fetching pathway names...")
    pathway_text = fetch_kegg("list/pathway/eco")
    pathway_names: dict[str, str] = {}
    for line in pathway_text.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            pid = parts[0].strip()       # e.g., "eco00010"
            name = parts[1].strip()
            # Remove "- Escherichia coli K-12 MG1655" suffix
            name = re.sub(r"\s*-\s*Escherichia coli.*$", "", name)
            pathway_names[pid] = name
    print(f"  Found {len(pathway_names)} pathways")

    # 3. Fetch gene → pathway links
    print("\nStep 3: Fetching gene-pathway links...")
    link_text = fetch_kegg("link/pathway/eco")
    gene_pathways: dict[str, list[str]] = defaultdict(list)
    for line in link_text.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            eco_gene = parts[0].strip()   # e.g., "eco:b0114"
            pid = parts[1].strip().replace("path:", "")  # e.g., "eco00010"
            if pid in SKIP_PATHWAYS:
                continue
            locus = eco_gene.replace("eco:", "")  # "b0114"
            gene_name = locus_to_gene.get(locus, None)
            if gene_name and pid in pathway_names:
                gene_pathways[gene_name].append(pathway_names[pid])

    n_mapped = len(gene_pathways)
    total_links = sum(len(v) for v in gene_pathways.values())
    print(f"  Mapped {n_mapped} genes to pathways ({total_links} total links)")

    # 4. Load existing gene_products.json and enrich
    print("\nStep 4: Enriching gene_products.json...")
    with open(GP_PATH) as f:
        gp = json.load(f)

    enriched = 0
    for entry in gp:
        gene = entry["gene"]
        pws = gene_pathways.get(gene, [])
        entry["pathways"] = sorted(set(pws))
        if pws:
            enriched += 1

    print(f"  Enriched {enriched}/{len(gp)} genes with pathway data")
    print(f"  Remaining {len(gp) - enriched} genes have no KEGG pathway")

    # 5. Summary of pathway distribution
    all_pathways: dict[str, int] = defaultdict(int)
    for entry in gp:
        for pw in entry["pathways"]:
            all_pathways[pw] += 1
    print(f"\nTop 20 pathways by gene count:")
    for pw, count in sorted(all_pathways.items(), key=lambda x: -x[1])[:20]:
        print(f"  {pw}: {count}")

    # 6. Write enriched file
    with open(GP_PATH, "w") as f:
        json.dump(gp, f, indent=2)
    print(f"\nWrote enriched data to {GP_PATH}")


if __name__ == "__main__":
    main()
