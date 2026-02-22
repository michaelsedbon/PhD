#!/usr/bin/env python3
"""Extract gene product annotations from E. coli K-12 MG1655 GenBank file
and classify them into functional categories."""

import re
import json
from pathlib import Path

GB_PATH = Path(__file__).parent / "data" / "MG1655.gb"
OUT_PATH = Path(__file__).parent / "moclo-viewer-v3" / "public" / "gene_products.json"

# Also load cds_regions.json for coordinate cross-reference
CDS_PATH = Path(__file__).parent / "moclo-viewer-v3" / "public" / "cds_regions.json"

CATEGORY_RULES = [
    # (keywords_in_product, category_name)
    (["transporter", "permease", "symporter", "antiporter", "efflux", "abc transporter", "porin"], "Transport"),
    (["kinase", "phosphatase"], "Kinase / Phosphatase"),
    (["reductase", "oxidase", "dehydrogenase", "oxidoreductase"], "Redox Enzymes"),
    (["synthase", "synthetase"], "Biosynthesis"),
    (["transferase", "acetyltransferase", "methyltransferase"], "Transferase"),
    (["regulator", "repressor", "activator", "regulatory", "response regulator"], "Regulation"),
    (["transcription", "sigma factor", "rna polymerase"], "Transcription"),
    (["ribosom", "translation", "trna", "rrna"], "Translation"),
    (["dna repair", "dna replicat", "dna polymer", "helicase", "recomb", "topoisomerase", "ligase"], "DNA Maintenance"),
    (["transposase", "insertion element", "is element"], "Mobile Elements"),
    (["flagell", "motil", "chemotaxis", "cheA", "cheB"], "Motility"),
    (["outer membrane", "lipoprotein", "membrane protein"], "Membrane"),
    (["fimbr", "pilus", "pilin", "curli"], "Fimbriae / Pili"),
    (["protease", "peptidase", "proteinase"], "Proteolysis"),
    (["chaperone", "heat shock", "cold shock"], "Chaperones / Stress"),
    (["hypothetical", "uncharacterized", "duf", "predicted protein"], "Uncharacterized"),
    (["lyase", "aldolase", "isomerase", "mutase", "racemase", "epimerase"], "Lyase / Isomerase"),
    (["hydrolase", "esterase", "lipase", "phospholipase"], "Hydrolase"),
]


def categorize(product: str) -> str:
    p = product.lower()
    for keywords, category in CATEGORY_RULES:
        for kw in keywords:
            if kw in p:
                return category
    return "Other"


def parse_genbank_products(gb_path: Path) -> dict[str, str]:
    """Parse CDS gene->product mappings from GenBank flat file."""
    with open(gb_path) as f:
        content = f.read()

    gene_products = {}
    # Split into feature blocks
    blocks = content.split("     CDS ")
    for block in blocks[1:]:
        gene_m = re.search(r'/gene="([^"]+)"', block)
        prod_m = re.search(r'/product="(.+?)"', block, re.DOTALL)
        if gene_m and prod_m:
            gene = gene_m.group(1)
            # Clean multiline product strings
            product = " ".join(prod_m.group(1).replace("\n", " ").split())
            gene_products[gene] = product
    return gene_products


def main():
    # Parse GenBank
    gb_products = parse_genbank_products(GB_PATH)
    print(f"Parsed {len(gb_products)} gene-product pairs from GenBank")

    # Load CDS regions for coordinates
    with open(CDS_PATH) as f:
        cds_regions = json.load(f)

    # Build output
    results = []
    matched = 0
    for cds in cds_regions:
        gene = cds["gene"]
        product = gb_products.get(gene, "")
        category = categorize(product) if product else "Unknown"
        results.append({
            "gene": gene,
            "start": cds["start"],
            "end": cds["end"],
            "complement": cds["complement"],
            "product": product,
            "category": category,
        })
        if product:
            matched += 1

    print(f"Matched {matched}/{len(cds_regions)} CDS regions to products")

    # Category summary
    from collections import Counter
    cats = Counter(r["category"] for r in results)
    print("\nCategory distribution:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")

    # Write output
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {len(results)} entries to {OUT_PATH}")


if __name__ == "__main__":
    main()
