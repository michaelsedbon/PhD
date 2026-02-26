#!/usr/bin/env python3
"""
Explore the citation network around seed papers using Semantic Scholar.

Given one or more seed papers (by DOI, title, or Semantic Scholar ID), this
script retrieves citations, references, and ML-based recommendations, then
ranks and displays the results.

Usage:
    # Single paper
    python3 scripts/explore_paper_network.py --doi "10.1038/ncomms9101"

    # Multiple seeds (finds intersection / shared network)
    python3 scripts/explore_paper_network.py \
        --doi "10.1038/ncomms9101" \
        --doi "10.1126/science.aad8711"

    # Filter by keyword and minimum citations
    python3 scripts/explore_paper_network.py \
        --doi "10.1038/ncomms9101" \
        --keyword "E. coli" --min-citations 10

    # Search by title instead of DOI
    python3 scripts/explore_paper_network.py \
        --title "CATCH Cas9 targeting chromosome"

    # Save markdown report
    python3 scripts/explore_paper_network.py \
        --doi "10.1038/ncomms9101" \
        --output agent_papers_txt/network_report.md
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from urllib.parse import quote

import requests

# ─── Config ──────────────────────────────────────────────────────────

BASE_URL = "https://api.semanticscholar.org"
GRAPH_URL = f"{BASE_URL}/graph/v1"
RECS_URL = f"{BASE_URL}/recommendations/v1"

PAPER_FIELDS = "title,year,citationCount,referenceCount,externalIds,abstract,url,openAccessPdf"
NETWORK_FIELDS = "title,year,citationCount,externalIds,abstract,url,openAccessPdf"

# Rate limiting: S2 allows 1 req/s without key (shared pool of 1000/s)
REQUEST_DELAY = 0.35  # be polite

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)


# ─── API helpers ─────────────────────────────────────────────────────

def _get(url, params=None):
    """Make a GET request with rate limiting and error handling."""
    time.sleep(REQUEST_DELAY)
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            print("  ⏳ Rate limited, waiting 5s...")
            time.sleep(5)
            resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"  ⚠ API error: {e}")
        return None


def _post(url, json_data):
    """Make a POST request with rate limiting."""
    time.sleep(REQUEST_DELAY)
    try:
        resp = requests.post(url, json=json_data, timeout=30)
        if resp.status_code == 429:
            print("  ⏳ Rate limited, waiting 5s...")
            time.sleep(5)
            resp = requests.post(url, json=json_data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"  ⚠ API error: {e}")
        return None


# ─── Paper resolution ────────────────────────────────────────────────

def resolve_paper_by_doi(doi):
    """Look up a paper by DOI."""
    url = f"{GRAPH_URL}/paper/DOI:{doi}"
    return _get(url, {"fields": PAPER_FIELDS})


def resolve_paper_by_id(paper_id):
    """Look up a paper by Semantic Scholar ID."""
    url = f"{GRAPH_URL}/paper/{paper_id}"
    return _get(url, {"fields": PAPER_FIELDS})


def search_paper_by_title(title, limit=5):
    """Search for papers by title string."""
    url = f"{GRAPH_URL}/paper/search"
    data = _get(url, {"query": title, "fields": PAPER_FIELDS, "limit": limit})
    if data and data.get("data"):
        return data["data"]
    return []


def resolve_paper(identifier, by="doi"):
    """Resolve a paper by DOI, title, or ID."""
    if by == "doi":
        return resolve_paper_by_doi(identifier)
    elif by == "title":
        results = search_paper_by_title(identifier, limit=1)
        return results[0] if results else None
    elif by == "id":
        return resolve_paper_by_id(identifier)
    return None


# ─── Network exploration ─────────────────────────────────────────────

def get_citations(paper_id, limit=100):
    """Get papers that cite this paper."""
    all_papers = []
    offset = 0
    while offset < limit:
        batch = min(100, limit - offset)
        url = f"{GRAPH_URL}/paper/{paper_id}/citations"
        data = _get(url, {"fields": NETWORK_FIELDS, "limit": batch, "offset": offset})
        if not data or not data.get("data"):
            break
        for item in data["data"]:
            p = item.get("citingPaper")
            if p and p.get("title"):
                all_papers.append(p)
        if "next" not in data:
            break
        offset = data["next"]
    return all_papers


def get_references(paper_id, limit=100):
    """Get papers that this paper references."""
    all_papers = []
    offset = 0
    while offset < limit:
        batch = min(100, limit - offset)
        url = f"{GRAPH_URL}/paper/{paper_id}/references"
        data = _get(url, {"fields": NETWORK_FIELDS, "limit": batch, "offset": offset})
        if not data or not data.get("data"):
            break
        for item in data["data"]:
            p = item.get("citedPaper")
            if p and p.get("title"):
                all_papers.append(p)
        if "next" not in data:
            break
        offset = data["next"]
    return all_papers


def get_recommendations(paper_ids, limit=50):
    """Get ML-based paper recommendations from Semantic Scholar."""
    url = f"{RECS_URL}/papers/"
    payload = {"positivePaperIds": paper_ids}
    data = _post(url, payload)
    if data and data.get("recommendedPapers"):
        return data["recommendedPapers"][:limit]
    return []


# ─── Filtering & ranking ─────────────────────────────────────────────

def extract_doi(paper):
    """Extract DOI from a paper's externalIds."""
    ids = paper.get("externalIds") or {}
    return ids.get("DOI", "")


def matches_keyword(paper, keywords):
    """Check if a paper matches any of the given keywords."""
    if not keywords:
        return True
    text = (paper.get("title", "") + " " + (paper.get("abstract") or "")).lower()
    return any(kw.lower() in text for kw in keywords)


def filter_and_rank(papers, keywords=None, min_citations=0, min_year=None):
    """Filter papers by keyword/citations/year and sort by citation count."""
    filtered = []
    seen_ids = set()

    for p in papers:
        pid = p.get("paperId")
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)

        # Filter by citation count
        cites = p.get("citationCount") or 0
        if cites < min_citations:
            continue

        # Filter by year
        year = p.get("year")
        if min_year and (not year or year < min_year):
            continue

        # Filter by keyword
        if not matches_keyword(p, keywords):
            continue

        filtered.append(p)

    # Sort by citation count descending
    filtered.sort(key=lambda x: x.get("citationCount") or 0, reverse=True)
    return filtered


def find_multi_seed_overlap(seed_networks):
    """Find papers that appear in multiple seed networks (intersection)."""
    paper_counts = defaultdict(lambda: {"paper": None, "seeds": 0, "sources": []})

    for seed_title, source_label, papers in seed_networks:
        seen_in_seed = set()
        for p in papers:
            pid = p.get("paperId")
            if not pid or pid in seen_in_seed:
                continue
            seen_in_seed.add(pid)
            paper_counts[pid]["paper"] = p
            paper_counts[pid]["seeds"] += 1
            paper_counts[pid]["sources"].append(f"{seed_title[:30]}({source_label})")

    # Return papers ordered by: number of seed appearances, then citations
    results = list(paper_counts.values())
    results.sort(key=lambda x: (x["seeds"], (x["paper"].get("citationCount") or 0)), reverse=True)
    return results


# ─── Display ─────────────────────────────────────────────────────────

def format_table(papers, limit=30, show_abstract=False):
    """Format papers as a readable table."""
    lines = []
    lines.append(f"\n{'#':>3}  {'Year':>4}  {'Cited':>6}  {'DOI':<30}  Title")
    lines.append(f"{'─'*3}  {'─'*4}  {'─'*6}  {'─'*30}  {'─'*50}")

    for i, p in enumerate(papers[:limit], 1):
        year = p.get("year") or "?"
        cites = p.get("citationCount") or 0
        doi = extract_doi(p) or "-"
        title = (p.get("title") or "Untitled")[:80]
        lines.append(f"{i:>3}  {year:>4}  {cites:>6}  {doi:<30}  {title}")

        if show_abstract and p.get("abstract"):
            abstract = p["abstract"][:200].replace("\n", " ")
            lines.append(f"     └─ {abstract}...")

    if len(papers) > limit:
        lines.append(f"\n  ... and {len(papers) - limit} more papers")

    return "\n".join(lines)


def format_overlap_table(overlap_results, limit=30):
    """Format multi-seed overlap results."""
    lines = []
    lines.append(f"\n{'#':>3}  {'Seeds':>5}  {'Year':>4}  {'Cited':>6}  {'DOI':<30}  Title")
    lines.append(f"{'─'*3}  {'─'*5}  {'─'*4}  {'─'*6}  {'─'*30}  {'─'*50}")

    for i, entry in enumerate(overlap_results[:limit], 1):
        p = entry["paper"]
        seeds = entry["seeds"]
        year = p.get("year") or "?"
        cites = p.get("citationCount") or 0
        doi = extract_doi(p) or "-"
        title = (p.get("title") or "Untitled")[:70]
        lines.append(f"{i:>3}  {seeds:>5}  {year:>4}  {cites:>6}  {doi:<30}  {title}")

    return "\n".join(lines)


def write_markdown_report(seed_papers, results_by_source, overlap_results, output_path):
    """Write a markdown report of the exploration."""
    lines = []
    lines.append("# Paper Network Exploration Report\n")
    lines.append(f"Generated by `explore_paper_network.py`\n")

    # Seed papers
    lines.append("## Seed Papers\n")
    for sp in seed_papers:
        doi = extract_doi(sp) or "N/A"
        lines.append(f"- **{sp.get('title', 'Unknown')}** ({sp.get('year', '?')})")
        lines.append(f"  - DOI: `{doi}` | Citations: {sp.get('citationCount', 0)} | References: {sp.get('referenceCount', 0)}")
    lines.append("")

    # Overlap results (if multi-seed)
    if overlap_results and len(seed_papers) > 1:
        lines.append("## Papers Appearing in Multiple Seed Networks\n")
        lines.append("| # | Seeds | Year | Cited | DOI | Title |")
        lines.append("|---|-------|------|-------|-----|-------|")
        for i, entry in enumerate(overlap_results[:50], 1):
            p = entry["paper"]
            doi = extract_doi(p) or "-"
            title = (p.get("title") or "?").replace("|", "\\|")
            lines.append(f"| {i} | {entry['seeds']} | {p.get('year', '?')} | {p.get('citationCount', 0)} | {doi} | {title} |")
        lines.append("")

    # Per-source results
    for source_label, papers in results_by_source:
        lines.append(f"## {source_label}\n")
        lines.append(f"Found **{len(papers)}** papers.\n")
        lines.append("| # | Year | Cited | DOI | Title |")
        lines.append("|---|------|-------|-----|-------|")
        for i, p in enumerate(papers[:30], 1):
            doi = extract_doi(p) or "-"
            title = (p.get("title") or "?").replace("|", "\\|")
            lines.append(f"| {i} | {p.get('year', '?')} | {p.get('citationCount', 0)} | {doi} | {title} |")
        lines.append("")

    report = "\n".join(lines)
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    print(f"\n📝 Report saved to {output_path}")


# ─── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Explore paper citation networks via Semantic Scholar"
    )
    parser.add_argument(
        "--doi", action="append", default=[],
        help="DOI of a seed paper (can specify multiple)"
    )
    parser.add_argument(
        "--title", action="append", default=[],
        help="Title of a seed paper to search for (can specify multiple)"
    )
    parser.add_argument(
        "--id", action="append", default=[],
        help="Semantic Scholar paper ID (can specify multiple)"
    )
    parser.add_argument(
        "--keyword", action="append", default=None,
        help="Filter results by keyword in title/abstract (can specify multiple)"
    )
    parser.add_argument(
        "--min-citations", type=int, default=0,
        help="Minimum citation count to include"
    )
    parser.add_argument(
        "--min-year", type=int, default=None,
        help="Minimum publication year"
    )
    parser.add_argument(
        "--limit", type=int, default=30,
        help="Maximum papers to show per category (default: 30)"
    )
    parser.add_argument(
        "--max-network", type=int, default=200,
        help="Maximum papers to fetch per network direction (default: 200)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Save markdown report to this file path"
    )
    parser.add_argument(
        "--no-citations", action="store_true",
        help="Skip fetching citations"
    )
    parser.add_argument(
        "--no-references", action="store_true",
        help="Skip fetching references"
    )
    parser.add_argument(
        "--no-recommendations", action="store_true",
        help="Skip fetching ML recommendations"
    )
    parser.add_argument(
        "--abstract", action="store_true",
        help="Show paper abstracts in output"
    )

    args = parser.parse_args()

    # ── Resolve seed papers ──
    seed_papers = []
    seed_ids = []

    for doi in args.doi:
        print(f"🔍 Resolving DOI: {doi}")
        p = resolve_paper("doi", by="doi") if False else resolve_paper(doi, by="doi")
        if p:
            print(f"   ✅ {p['title'][:70]} ({p.get('year', '?')}) — {p.get('citationCount', 0)} citations")
            seed_papers.append(p)
            seed_ids.append(p["paperId"])
        else:
            print(f"   ❌ Could not resolve DOI: {doi}")

    for title in args.title:
        print(f"🔍 Searching: {title}")
        p = resolve_paper(title, by="title")
        if p:
            print(f"   ✅ {p['title'][:70]} ({p.get('year', '?')}) — {p.get('citationCount', 0)} citations")
            seed_papers.append(p)
            seed_ids.append(p["paperId"])
        else:
            print(f"   ❌ Could not find paper: {title}")

    for sid in args.id:
        print(f"🔍 Looking up ID: {sid}")
        p = resolve_paper(sid, by="id")
        if p:
            print(f"   ✅ {p['title'][:70]} ({p.get('year', '?')}) — {p.get('citationCount', 0)} citations")
            seed_papers.append(p)
            seed_ids.append(p["paperId"])
        else:
            print(f"   ❌ Could not resolve ID: {sid}")

    if not seed_papers:
        print("\n❌ No seed papers found. Provide at least one --doi, --title, or --id.")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"Exploring network for {len(seed_papers)} seed paper(s)")
    print(f"{'='*70}")

    # ── Gather network ──
    all_seed_networks = []  # (seed_title, source, papers)
    results_by_source = []  # (label, papers) for report

    for sp in seed_papers:
        pid = sp["paperId"]
        stitle = sp.get("title", "?")[:40]

        # Citations
        if not args.no_citations:
            print(f"\n📥 Fetching citations for: {stitle}...")
            citations = get_citations(pid, limit=args.max_network)
            citations = filter_and_rank(citations, args.keyword, args.min_citations, args.min_year)
            print(f"   Found {len(citations)} papers citing this work")
            if citations:
                all_seed_networks.append((stitle, "cites", citations))
                results_by_source.append((f"Citations of: {stitle}", citations))
                print(format_table(citations, limit=args.limit, show_abstract=args.abstract))

        # References
        if not args.no_references:
            print(f"\n📚 Fetching references for: {stitle}...")
            references = get_references(pid, limit=args.max_network)
            references = filter_and_rank(references, args.keyword, args.min_citations, args.min_year)
            print(f"   Found {len(references)} papers referenced by this work")
            if references:
                all_seed_networks.append((stitle, "refs", references))
                results_by_source.append((f"References of: {stitle}", references))
                print(format_table(references, limit=args.limit, show_abstract=args.abstract))

    # Recommendations (uses all seeds together)
    if not args.no_recommendations and seed_ids:
        print(f"\n🤖 Fetching ML recommendations...")
        recs = get_recommendations(seed_ids, limit=args.max_network)
        recs = filter_and_rank(recs, args.keyword, args.min_citations, args.min_year)
        print(f"   Got {len(recs)} recommendations")
        if recs:
            all_seed_networks.append(("ALL", "recs", recs))
            results_by_source.append(("ML Recommendations", recs))
            print(format_table(recs, limit=args.limit, show_abstract=args.abstract))

    # ── Multi-seed overlap ──
    overlap_results = None
    if len(seed_papers) > 1 and all_seed_networks:
        print(f"\n{'='*70}")
        print("🔗 Papers appearing in MULTIPLE seed networks (most relevant)")
        print(f"{'='*70}")
        overlap_results = find_multi_seed_overlap(all_seed_networks)
        multi = [r for r in overlap_results if r["seeds"] >= 2]
        if multi:
            print(format_overlap_table(multi, limit=args.limit))
        else:
            print("  No papers found in multiple networks.")

    # ── Save report ──
    if args.output:
        output_path = args.output
        if not os.path.isabs(output_path):
            output_path = os.path.join(PROJECT_DIR, output_path)
        write_markdown_report(seed_papers, results_by_source, overlap_results, output_path)

    print(f"\n✅ Done!")


if __name__ == "__main__":
    main()
