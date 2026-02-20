#!/usr/bin/env python3
"""
Import papers from the Grant Application Zotero collection into the
PhD Lab Notion bibliography database.

Each paper is tagged with Application Field = "MOST Maimonide" so it
can be filtered during grant writing.

Usage:
    python3 scripts/import_zotero_to_notion.py              # Import papers
    python3 scripts/import_zotero_to_notion.py --dry-run     # Preview only
    python3 scripts/import_zotero_to_notion.py --list        # List Zotero items
"""

import os
import sys
import yaml
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from notion_client import (
    CONFIG, query_database, get_title_from_page,
    get_property_value, create_page,
)

# --- Zotero config (from Grant_application/project.yaml) ---
GRANT_DIR = os.path.join(PROJECT_DIR, 'Grant_application')
GRANT_CONFIG_PATH = os.path.join(GRANT_DIR, 'project.yaml')

with open(GRANT_CONFIG_PATH) as f:
    grant_config = yaml.safe_load(f)

ZOTERO_API_KEY = grant_config['zotero']['api_key']
ZOTERO_LIBRARY_ID = str(grant_config['zotero']['library_id'])
ZOTERO_LIBRARY_TYPE = grant_config['zotero']['library_type']
ZOTERO_COLLECTION_ID = grant_config['zotero'].get('collection_id', '')

# Notion bibliography database
BIB_DB = CONFIG['notion']['bibliography_db']

# Tag to apply to every imported paper
APPLICATION_FIELD_TAG = "MOST Maimonide"

# ─── Subject mapping ────────────────────────────────────────────────
# Maps keywords found in title/abstract/tags to Subject multi_select values.
SUBJECT_KEYWORDS = {
    'SARS-CoV-2': ['sars-cov-2', 'covid', 'coronavirus', 'sars'],
    'Directed Evolution': ['directed evolution', 'pace', 'phage-assisted',
                           'mutagenesis', 'continuous evolution', 'evolv'],
    'Phage Display': ['phage display', 'phage-display', 'filamentous phage',
                      'm13', 'bacteriophage'],
    'Antibodies': ['antibod', 'neutraliz', 'monoclonal', 'nanobod', 'bnab',
                   'immunoglobulin'],
    'Immunology': ['germinal center', 'germinal centre', 'b cell', 'memory b',
                   'immune', 'vaccine', 'immuniz'],
    'Virology': ['viral', 'virus', 'influenza', 'dengue', 'rbd',
                 'receptor binding domain', 'spike'],
    'Synthetic Biology': ['synthetic biology', 'synthetic bacterial',
                          'crispr', 'gene circuit', 'toolbox'],
    'Protein Engineering': ['protein engineer', 'epitope', 'affinity maturation',
                            'mutational scanning'],
}


def classify_subjects(title, abstract='', tags=None):
    """Return a list of Subject tags based on keyword matching."""
    text = f"{title} {abstract} {' '.join(tags or [])}".lower()
    subjects = []
    for subject, keywords in SUBJECT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            subjects.append(subject)
    return subjects or ['General']


# ─── Zotero API ─────────────────────────────────────────────────────

def fetch_zotero_items():
    """Fetch all items from the grant application's Zotero collection (JSON)."""
    base_url = f"https://api.zotero.org/{ZOTERO_LIBRARY_TYPE}s/{ZOTERO_LIBRARY_ID}/"
    if ZOTERO_COLLECTION_ID:
        endpoint = f"collections/{ZOTERO_COLLECTION_ID}/items"
    else:
        endpoint = "items"

    headers = {
        'Zotero-API-Key': ZOTERO_API_KEY,
        'Zotero-API-Version': '3',
    }

    all_items = []
    start = 0
    limit = 100

    while True:
        url = f"{base_url}{endpoint}?format=json&limit={limit}&start={start}&itemType=-attachment"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        all_items.extend(items)
        if len(items) < limit:
            break
        start += limit

    return all_items


def extract_paper_info(item):
    """Extract structured info from a Zotero JSON item."""
    data = item.get('data', {})
    title = data.get('title', '').strip()
    if not title:
        return None

    # Build DOI/URL
    doi = data.get('DOI', '')
    url = data.get('url', '')
    if doi and not url:
        url = f"https://doi.org/{doi}"

    abstract = data.get('abstractNote', '')
    tags = [t.get('tag', '') for t in data.get('tags', [])]

    # Journal info
    journal = data.get('publicationTitle', '') or data.get('journalAbbreviation', '')
    year = data.get('date', '')[:4] if data.get('date') else ''

    # Authors
    creators = data.get('creators', [])
    authors = []
    for c in creators:
        last = c.get('lastName', '')
        first = c.get('firstName', '')
        if last:
            authors.append(f"{last}, {first}" if first else last)

    return {
        'title': title,
        'url': url,
        'doi': doi,
        'abstract': abstract,
        'tags': tags,
        'journal': journal,
        'year': year,
        'authors': authors,
    }


# ─── Notion helpers ─────────────────────────────────────────────────

def get_existing_titles(database_id):
    """Get a set of lowercase titles already in the Notion bibliography."""
    pages = query_database(database_id)
    titles = set()
    for page in pages:
        title = get_title_from_page(page)
        if title:
            titles.add(title.strip().lower())
    return titles


def build_notion_properties(paper, subjects):
    """Build Notion API properties dict for a bibliography entry."""
    props = {
        'Paper name': {
            'title': [{'text': {'content': paper['title'][:2000]}}]
        },
        'Subject': {
            'multi_select': [{'name': s} for s in subjects]
        },
        'Project relevance': {
            'multi_select': [{'name': APPLICATION_FIELD_TAG}]
        },
    }
    if paper['url']:
        props['URL'] = {'url': paper['url']}
    return props


# ─── Main ────────────────────────────────────────────────────────────

def import_papers(dry_run=False):
    """Import Zotero papers into Notion bibliography."""
    print(f"Fetching papers from Zotero collection {ZOTERO_COLLECTION_ID}...")
    items = fetch_zotero_items()
    print(f"  Found {len(items)} items in Zotero.\n")

    print("Fetching existing Notion bibliography...")
    existing_titles = get_existing_titles(BIB_DB)
    print(f"  {len(existing_titles)} papers already in Notion.\n")

    created = 0
    skipped_dup = 0
    skipped_empty = 0
    errors = 0

    for item in items:
        paper = extract_paper_info(item)
        if not paper:
            skipped_empty += 1
            continue

        # Deduplicate by title
        if paper['title'].strip().lower() in existing_titles:
            skipped_dup += 1
            print(f"  ⏭ Already exists: {paper['title'][:80]}")
            continue

        subjects = classify_subjects(paper['title'], paper['abstract'], paper['tags'])

        if dry_run:
            print(f"  [DRY RUN] Would import: {paper['title'][:80]}")
            print(f"            Subjects: {', '.join(subjects)}")
            print(f"            URL: {paper['url']}")
            created += 1
            continue

        try:
            props = build_notion_properties(paper, subjects)
            create_page(BIB_DB, props)
            created += 1
            print(f"  ✅ Imported: {paper['title'][:80]}")
            print(f"     Subjects: {', '.join(subjects)}")
        except Exception as e:
            errors += 1
            print(f"  ❌ Failed: {paper['title'][:80]} — {e}")

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{'='*50}")
    print(f"{prefix}Import Complete!")
    print(f"  {'Would create' if dry_run else 'Created'}: {created}")
    print(f"  Already in Notion: {skipped_dup}")
    print(f"  Empty/skipped: {skipped_empty}")
    if errors:
        print(f"  Errors: {errors}")
    print(f"{'='*50}")

    return created


def list_items():
    """List all items in the Zotero collection."""
    items = fetch_zotero_items()
    print(f"\n📚 Zotero Collection ({len(items)} items)\n")
    for i, item in enumerate(items, 1):
        paper = extract_paper_info(item)
        if not paper:
            continue
        subjects = classify_subjects(paper['title'], paper['abstract'], paper['tags'])
        authors_str = paper['authors'][0] if paper['authors'] else 'Unknown'
        if len(paper['authors']) > 1:
            authors_str += ' et al.'
        print(f"  {i:3d}. {paper['title'][:80]}")
        print(f"       {authors_str} ({paper['year']}) — {paper['journal']}")
        print(f"       Subjects: {', '.join(subjects)}")
        print()


if __name__ == '__main__':
    if '--list' in sys.argv:
        list_items()
    elif '--dry-run' in sys.argv:
        import_papers(dry_run=True)
    else:
        import_papers()
