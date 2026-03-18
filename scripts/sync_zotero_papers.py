#!/usr/bin/env python3
"""
Sync papers from the PhD Zotero collection and its sub-collections
into organized local directories.

Only syncs papers under the PhD collection (key: XYEH4FPT).
Downloads PDFs, extracts text, and maintains tiered indexes
(CATALOG.md + per-collection INDEX.md).

Usage:
    python3 scripts/sync_zotero_papers.py              # Sync all collections
    python3 scripts/sync_zotero_papers.py --dry-run     # Preview only
    python3 scripts/sync_zotero_papers.py --list        # List collections
    python3 scripts/sync_zotero_papers.py --rebuild      # Rebuild indexes from existing files
"""

import os
import re
import sys
import yaml
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from pdf_to_text import pdf_to_text

# Load config
CONFIG_PATH = os.path.join(PROJECT_DIR, 'config.yaml')
with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

ZOTERO_API_KEY = CONFIG['zotero']['api_key']
ZOTERO_LIBRARY_ID = str(CONFIG['zotero']['library_id'])
ZOTERO_LIBRARY_TYPE = CONFIG['zotero']['library_type']

PAPERS_DIR = os.path.join(PROJECT_DIR, 'papers')
PAPERS_TXT_DIR = os.path.join(PROJECT_DIR, 'papers_txt')
CATALOG_PATH = os.path.join(PAPERS_TXT_DIR, 'CATALOG.md')

HEADERS = {
    'Zotero-API-Key': ZOTERO_API_KEY,
    'Zotero-API-Version': '3',
}
BASE_URL = f"https://api.zotero.org/{ZOTERO_LIBRARY_TYPE}s/{ZOTERO_LIBRARY_ID}/"

# PhD collection key in Zotero (only sync this collection and its children)
PHD_COLLECTION_KEY = 'XYEH4FPT'


def sanitize_dirname(name):
    """Convert collection name to a safe directory name."""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name


def sanitize_filename(title):
    """Generate a clean filename from paper title."""
    words = title.split()[:5]
    name = '_'.join(words)
    name = re.sub(r'[^\w\-.]', '', name)
    return name


def fetch_phd_subcollections():
    """Fetch sub-collections under the PhD collection only."""
    url = f"{BASE_URL}collections/{PHD_COLLECTION_KEY}/collections?format=json&limit=100"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    collections = []
    for item in resp.json():
        data = item.get('data', {})
        collections.append({
            'key': data.get('key', ''),
            'name': data.get('name', ''),
            'parent': data.get('parentCollection', False),
        })
    return collections


def fetch_collection_items(collection_key):
    """Fetch all items from a specific collection."""
    all_items = []
    start = 0
    limit = 100

    while True:
        url = f"{BASE_URL}collections/{collection_key}/items?format=json&limit={limit}&start={start}&itemType=-attachment"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        all_items.extend(items)
        if len(items) < limit:
            break
        start += limit

    return all_items


def fetch_item_attachments(item_key):
    """Fetch attachments for an item (to get PDF download URL)."""
    url = f"{BASE_URL}items/{item_key}/children?format=json&itemType=attachment"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def extract_paper_info(item):
    """Extract structured info from a Zotero item."""
    data = item.get('data', {})
    title = data.get('title', '').strip()
    if not title:
        return None

    doi = data.get('DOI', '')
    url = data.get('url', '')
    if doi and not url:
        url = f"https://doi.org/{doi}"

    abstract = data.get('abstractNote', '')
    tags = [t.get('tag', '') for t in data.get('tags', [])]

    return {
        'key': item.get('key', ''),
        'title': title,
        'url': url,
        'doi': doi,
        'abstract': abstract,
        'tags': tags,
    }


def download_pdf_from_zotero(item_key, dest_path):
    """Download a PDF attachment from Zotero."""
    attachments = fetch_item_attachments(item_key)
    for att in attachments:
        data = att.get('data', {})
        if data.get('contentType') == 'application/pdf':
            att_key = att.get('key', '')
            url = f"{BASE_URL}items/{att_key}/file"
            resp = requests.get(url, headers=HEADERS, stream=True)
            resp.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    return False


def generate_catalog(collections_data):
    """Generate CATALOG.md from organized collection data."""
    lines = [
        '# Paper Catalog',
        '',
        'Compact index of all papers organized by Zotero collection.',
        'Read this first to find relevant papers, then load the per-collection INDEX.md for full summaries.',
        '',
    ]

    total = sum(len(papers) for papers in collections_data.values())
    lines.append(f'**Total: {total} papers across {len(collections_data)} collections.**')
    lines.append('')
    lines.append('---')
    lines.append('')

    for coll_dir, papers in collections_data.items():
        coll_display = coll_dir.replace('_', ' ').title()
        lines.append(f'## {coll_display} ({len(papers)} papers)')
        lines.append('')
        lines.append(f'📂 `{coll_dir}/INDEX.md`')
        lines.append('')
        lines.append('| Title | File |')
        lines.append('|-------|------|')
        for p in papers:
            short_title = p['title'][:80] + ('...' if len(p['title']) > 80 else '')
            lines.append(f"| {short_title} | `{coll_dir}/{p['filename']}` |")
        lines.append('')
        lines.append('---')
        lines.append('')

    return '\n'.join(lines)


def generate_collection_index(coll_name, papers):
    """Generate per-collection INDEX.md."""
    coll_display = coll_name.replace('_', ' ').title()
    lines = [
        f'# {coll_display} — Paper Index',
        '',
        f'Full summaries for {len(papers)} papers in this collection.',
        '',
        '---',
        '',
    ]

    for p in papers:
        lines.append(f"## {p['title']}")
        lines.append(f"**File:** `{p['filename']}`")
        lines.append(f"**URL:** {p.get('url', 'N/A')}")
        lines.append('')
        if p.get('summary'):
            lines.append(p['summary'])
        else:
            lines.append('*(Summary pending — read the full text to generate one.)*')
        lines.append('')
        lines.append('---')
        lines.append('')

    return '\n'.join(lines)


def load_existing_summaries(coll_dir):
    """Load existing summaries from a collection INDEX.md to preserve them."""
    index_path = os.path.join(PAPERS_TXT_DIR, coll_dir, 'INDEX.md')
    summaries = {}
    if not os.path.exists(index_path):
        return summaries

    with open(index_path, 'r') as f:
        content = f.read()

    blocks = re.split(r'\n---\n', content)
    for block in blocks:
        title_match = re.search(r'^## (.+)$', block, re.MULTILINE)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        # Extract summary (non-metadata lines)
        lines = block.split('\n')
        summary_lines = []
        for line in lines:
            if line.startswith('## ') or line.startswith('**File:**') or line.startswith('**URL:**') or line.startswith('**Subjects:**'):
                continue
            if line.strip() and '*(Summary pending' not in line:
                summary_lines.append(line)
        summary = '\n'.join(summary_lines).strip()
        if summary:
            summaries[title.lower()] = summary

    return summaries


def sync(dry_run=False):
    """Sync papers from PhD Zotero collection into organized directories."""
    print("Fetching PhD sub-collections...")
    collections = fetch_phd_subcollections()
    print(f"  Found {len(collections)} sub-collections under PhD.\n")

    for coll in collections:
        print(f"  • {coll['name']} (key: {coll['key']})")
    print()

    collections_data = {}

    # First, sync top-level PhD items (not in any sub-collection) → uncategorized/
    print(f"\n{'='*50}")
    print(f"PhD top-level items → uncategorized/")
    print(f"{'='*50}")
    top_items = fetch_collection_items(PHD_COLLECTION_KEY)
    # Filter out items that are in sub-collections
    subcoll_keys = {c['key'] for c in collections}
    top_only = []
    for item in top_items:
        item_colls = set(item.get('data', {}).get('collections', []))
        # Keep if the item is only in the PhD collection (not in any sub-collection)
        if not item_colls.intersection(subcoll_keys):
            top_only.append(item)
    print(f"  {len(top_only)} items (not in any sub-collection)")

    if top_only:
        existing_summaries = load_existing_summaries('uncategorized')
        txt_dir = os.path.join(PAPERS_TXT_DIR, 'uncategorized')
        pdf_dir = os.path.join(PAPERS_DIR, 'uncategorized')
        if not dry_run:
            os.makedirs(txt_dir, exist_ok=True)
            os.makedirs(pdf_dir, exist_ok=True)
        papers = []
        for item in top_only:
            info = extract_paper_info(item)
            if not info:
                continue
            filename_base = sanitize_filename(info['title'])
            txt_filename = f"{filename_base}.txt"
            pdf_path = os.path.join(pdf_dir, f"{filename_base}.pdf")
            txt_path = os.path.join(txt_dir, txt_filename)
            if not os.path.exists(txt_path) and not dry_run:
                try:
                    if download_pdf_from_zotero(info['key'], pdf_path):
                        print(f"  ↓ Downloaded: {info['title'][:60]}")
                        try:
                            pdf_to_text(pdf_path, txt_dir)
                        except Exception as e:
                            print(f"  ⚠ Text extraction failed: {e}")
                    else:
                        print(f"  ⚠ No PDF: {info['title'][:60]}")
                except Exception as e:
                    print(f"  ✗ Failed: {info['title'][:60]} — {e}")
            summary = existing_summaries.get(info['title'].lower(), '')
            papers.append({'title': info['title'], 'filename': txt_filename,
                           'url': info['url'], 'summary': summary})
        collections_data['uncategorized'] = papers
        if not dry_run and papers:
            idx = generate_collection_index('uncategorized', papers)
            with open(os.path.join(txt_dir, 'INDEX.md'), 'w') as f:
                f.write(idx)
            print(f"  📝 Updated uncategorized/INDEX.md ({len(papers)} entries)")

    # Then sync each sub-collection
    for coll in collections:
        coll_dir = sanitize_dirname(coll['name'])
        print(f"\n{'='*50}")
        print(f"Collection: {coll['name']} → {coll_dir}/")
        print(f"{'='*50}")

        items = fetch_collection_items(coll['key'])
        print(f"  {len(items)} items")

        # Load existing summaries to preserve them
        existing_summaries = load_existing_summaries(coll_dir)

        pdf_dir = os.path.join(PAPERS_DIR, coll_dir)
        txt_dir = os.path.join(PAPERS_TXT_DIR, coll_dir)

        if not dry_run:
            os.makedirs(pdf_dir, exist_ok=True)
            os.makedirs(txt_dir, exist_ok=True)

        papers = []
        for item in items:
            info = extract_paper_info(item)
            if not info:
                continue

            filename_base = sanitize_filename(info['title'])
            txt_filename = f"{filename_base}.txt"
            pdf_path = os.path.join(pdf_dir, f"{filename_base}.pdf")
            txt_path = os.path.join(txt_dir, txt_filename)

            # Check if already downloaded
            already_has_text = os.path.exists(txt_path)

            if not already_has_text and not dry_run:
                # Try to download PDF
                try:
                    if download_pdf_from_zotero(info['key'], pdf_path):
                        print(f"  ↓ Downloaded: {info['title'][:60]}")
                        try:
                            pdf_to_text(pdf_path, txt_dir)
                            print(f"  📝 Extracted text")
                        except Exception as e:
                            print(f"  ⚠ Text extraction failed: {e}")
                    else:
                        print(f"  ⚠ No PDF attachment: {info['title'][:60]}")
                except Exception as e:
                    print(f"  ✗ Download failed: {info['title'][:60]} — {e}")
            elif already_has_text:
                pass  # silently skip

            # Preserve existing summary if we have one
            summary = existing_summaries.get(info['title'].lower(), '')

            papers.append({
                'title': info['title'],
                'filename': txt_filename,
                'url': info['url'],
                'summary': summary,
            })

        collections_data[coll_dir] = papers

        # Generate per-collection INDEX.md
        if not dry_run and papers:
            index_content = generate_collection_index(coll_dir, papers)
            index_path = os.path.join(txt_dir, 'INDEX.md')
            with open(index_path, 'w') as f:
                f.write(index_content)
            print(f"  📝 Updated {coll_dir}/INDEX.md ({len(papers)} entries)")

    # Generate CATALOG.md
    if not dry_run:
        catalog_content = generate_catalog(collections_data)
        with open(CATALOG_PATH, 'w') as f:
            f.write(catalog_content)
        print(f"\n📝 Updated CATALOG.md")

    total = sum(len(p) for p in collections_data.values())
    print(f"\n{'='*50}")
    print(f"{'[DRY RUN] ' if dry_run else ''}Zotero Sync Complete!")
    print(f"  Collections: {len(collections_data)}")
    print(f"  Papers: {total}")
    print(f"{'='*50}")


def list_collections():
    """List PhD sub-collections."""
    collections = fetch_phd_subcollections()
    print(f"\n📚 PhD Collection — {len(collections)} sub-collections\n")
    for coll in collections:
        items = fetch_collection_items(coll['key'])
        print(f"  {coll['name']} (key: {coll['key']}) — {len(items)} items")
    top = fetch_collection_items(PHD_COLLECTION_KEY)
    print(f"\n  Top-level: {len(top)} items")
    print()


if __name__ == '__main__':
    if '--list' in sys.argv:
        list_collections()
    elif '--rebuild' in sys.argv:
        # Rebuild indexes from existing files without downloading
        sync(dry_run=False)
    elif '--dry-run' in sys.argv:
        sync(dry_run=True)
    else:
        sync()
