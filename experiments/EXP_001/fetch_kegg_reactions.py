#!/usr/bin/env python3
"""
Fetch KEGG pathway reaction data for E. coli K-12 MG1655.
Produces pathway_reactions.json with substrates, products, EC numbers,
and gene mappings for each reaction in each pathway.

Uses KEGG REST API with rate limiting.
Caches intermediate results in kegg_cache/ to allow resuming.
"""

import json, os, re, time, sys, threading
from typing import Optional
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

CACHE_DIR = Path("kegg_cache")
CACHE_DIR.mkdir(exist_ok=True)

OUT_FILE = Path("moclo-viewer-v3/public/pathway_reactions.json")
GP_FILE  = Path("moclo-viewer-v3/public/gene_products.json")

# ──── Rate-limited fetcher ────────────────────────────────────────
_lock = threading.Lock()
_last_req = 0.0

def kegg_get(url: str, cache_key: Optional[str] = None) -> str:
    """Fetch URL with caching and rate limiting."""
    global _last_req
    if cache_key:
        cache_path = CACHE_DIR / f"{cache_key}.txt"
        if cache_path.exists():
            return cache_path.read_text()

    with _lock:
        elapsed = time.time() - _last_req
        if elapsed < 0.35:
            time.sleep(0.35 - elapsed)
        _last_req = time.time()

    for attempt in range(4):
        try:
            req = Request(url, headers={"User-Agent": "MoCloViewer/1.0"})
            resp = urlopen(req, timeout=30)
            text = resp.read().decode("utf-8")
            break
        except HTTPError as e:
            if e.code == 404:
                text = ""
                break
            elif e.code == 403 and attempt < 3:
                wait = 2 ** attempt * 2
                time.sleep(wait)
                continue
            else:
                raise

    if cache_key:
        cache_path = CACHE_DIR / f"{cache_key}.txt"
        cache_path.write_text(text)
    return text


# ──── Parse helpers ──────────────────────────────────────────────
def parse_kegg_entry(text: str) -> dict:
    """Parse a KEGG flat-file entry into sections."""
    sections = {}
    current_key = None
    current_lines = []
    for line in text.split("\n"):
        if line.startswith("///"):
            break
        if line and not line[0].isspace():
            if current_key:
                sections[current_key] = "\n".join(current_lines)
            parts = line.split(None, 1)
            current_key = parts[0]
            current_lines = [parts[1] if len(parts) > 1 else ""]
        elif current_key:
            current_lines.append(line.strip())
    if current_key:
        sections[current_key] = "\n".join(current_lines)
    return sections


def parse_pathway_genes(gene_text: str) -> dict:
    """Parse GENE section → {b_number: {name, ec_list}}."""
    genes = {}
    for line in gene_text.split("\n"):
        line = line.strip()
        # Match with EC numbers
        m = re.match(r"(b\d+)\s+(\w+);.*?\[EC:([\d.\-\s]+)\]", line)
        if m:
            b_num = m.group(1)
            name = m.group(2)
            ec_list = [e.strip() for e in m.group(3).split() if e.strip()]
            genes[b_num] = {"name": name, "ec": ec_list}
        else:
            m2 = re.match(r"(b\d+)\s+(\w+);", line)
            if m2:
                genes[m2.group(1)] = {"name": m2.group(2), "ec": []}
    return genes


def parse_pathway_compounds(compound_text: str) -> dict:
    """Parse COMPOUND section → {compound_id: name}."""
    compounds = {}
    for line in compound_text.split("\n"):
        line = line.strip()
        m = re.match(r"(C\d+)\s+(.+)", line)
        if m:
            compounds[m.group(1)] = m.group(2).strip()
    return compounds


def parse_reaction_equation(eq_text: str, compounds: dict):
    """Parse equation like 'C00002 + C00022 <=> C00008 + C00074'."""
    sides = re.split(r"\s*<=>\s*", eq_text)
    if len(sides) != 2:
        sides = re.split(r"\s*=>\s*", eq_text)
    if len(sides) != 2:
        return [], []

    def parse_side(s):
        items = []
        for part in re.split(r"\s*\+\s*", s.strip()):
            m = re.match(r"(?:\d+\s+)?(C\d+)", part.strip())
            if m:
                cid = m.group(1)
                items.append({"id": cid, "name": compounds.get(cid, cid)})
        return items

    return parse_side(sides[0]), parse_side(sides[1])


# ──── Main ────────────────────────────────────────────────────────
def main():
    with open(GP_FILE) as f:
        gp = json.load(f)

    pathway_names = set()
    for g in gp:
        for pw in g.get("pathways", []):
            pathway_names.add(pw)
    print(f"Found {len(pathway_names)} unique pathways")

    # Get pathway ID mapping
    print("Fetching E. coli pathway list...")
    pw_list_text = kegg_get("https://rest.kegg.jp/list/pathway/eco", "eco_pathway_list")

    name_to_id = {}
    for line in pw_list_text.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            pw_id = parts[0].replace("path:", "")  # eco00010
            pw_name = parts[1].split(" - ")[0].strip()
            name_to_id[pw_name] = pw_id

    mapped = {}
    for pw_name in sorted(pathway_names):
        if pw_name in name_to_id:
            mapped[pw_name] = name_to_id[pw_name]
        else:
            for kegg_name, kegg_id in name_to_id.items():
                if pw_name.lower() in kegg_name.lower() or kegg_name.lower() in pw_name.lower():
                    mapped[pw_name] = kegg_id
                    break

    print(f"Mapped {len(mapped)}/{len(pathway_names)} pathways to KEGG IDs")

    # Collect all compound names globally (for reaction equation parsing)
    global_compounds = {}

    # Step 1: Fetch pathway details + reaction links
    result = {}
    all_rxn_ids = set()

    for i, (pw_name, pw_id) in enumerate(sorted(mapped.items())):
        print(f"[{i+1}/{len(mapped)}] {pw_id}: {pw_name}")

        # Get pathway detail
        pw_text = kegg_get(f"https://rest.kegg.jp/get/{pw_id}", f"pathway_{pw_id}")
        if not pw_text.strip():
            print(f"  ⚠ Empty, skipping")
            continue

        sections = parse_kegg_entry(pw_text)
        genes = parse_pathway_genes(sections.get("GENE", ""))
        compounds = parse_pathway_compounds(sections.get("COMPOUND", ""))
        global_compounds.update(compounds)

        # Use map (reference) pathway for reactions
        map_id = pw_id.replace("eco", "map")
        rxn_link = kegg_get(f"https://rest.kegg.jp/link/rn/{map_id}", f"rxnlink_{map_id}")

        reaction_ids = []
        for line in rxn_link.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                rid = parts[1].replace("rn:", "")
                reaction_ids.append(rid)
                all_rxn_ids.add(rid)

        result[pw_name] = {
            "id": pw_id,
            "description": sections.get("DESCRIPTION", "")[:300],
            "genes": genes,
            "compounds": compounds,
            "reaction_ids": reaction_ids,
        }
        print(f"  → {len(genes)} genes, {len(compounds)} cpds, {len(reaction_ids)} rxns")

    # Step 2: Fetch all unique reactions (sequential with caching)
    print(f"\n  Fetching {len(all_rxn_ids)} unique reactions...")
    rxn_data = {}
    for j, rid in enumerate(sorted(all_rxn_ids)):
        if j % 100 == 0:
            print(f"  [{j}/{len(all_rxn_ids)}]...")
        rxn_text = kegg_get(f"https://rest.kegg.jp/get/rn:{rid}", f"rxn_{rid}")
        if not rxn_text.strip():
            continue
        sections = parse_kegg_entry(rxn_text)
        equation = sections.get("EQUATION", "")
        rxn_name = sections.get("NAME", "").split(";")[0].strip()
        ec_text = sections.get("ENZYME", "")
        ecs = [e.strip() for e in ec_text.split() if re.match(r"\d+\.\d+", e.strip())]
        rxn_data[rid] = {"name": rxn_name, "equation": equation, "ec": ecs}

    # Step 3: Assemble final output
    print("\nAssembling final output...")
    output = {}
    for pw_name, pw_info in result.items():
        genes = pw_info["genes"]
        compounds = pw_info["compounds"]
        compounds.update({k: v for k, v in global_compounds.items() if k not in compounds})

        # EC → genes mapping
        ec_to_genes = {}
        for b_num, info in genes.items():
            for ec in info["ec"]:
                if ec not in ec_to_genes:
                    ec_to_genes[ec] = []
                ec_to_genes[ec].append({"b_number": b_num, "name": info["name"]})

        reactions = []
        for rid in pw_info["reaction_ids"]:
            if rid not in rxn_data:
                continue
            rd = rxn_data[rid]
            substrates, products = parse_reaction_equation(rd["equation"], compounds)
            if not substrates and not products:
                continue

            # Map EC → E. coli genes in this pathway
            rxn_genes = []
            for ec in rd["ec"]:
                for g in ec_to_genes.get(ec, []):
                    if g not in rxn_genes:
                        rxn_genes.append(g)

            reactions.append({
                "id": rid,
                "name": rd["name"],
                "substrates": substrates,
                "products": products,
                "ec": rd["ec"],
                "genes": rxn_genes,
            })

        if reactions:
            output[pw_name] = {
                "id": pw_info["id"],
                "description": pw_info["description"],
                "gene_count": len(genes),
                "reactions": reactions,
            }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    total_rxns = sum(len(p["reactions"]) for p in output.values())
    print(f"\n✅ Done! {len(output)} pathways, {total_rxns} total reactions")
    print(f"   Saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
