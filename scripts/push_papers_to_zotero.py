#!/usr/bin/env python3
"""
Push local paper collections to Zotero as sub-collections under the PhD collection.

For each local collection (e.g. germinal_centers/, cloning/):
1. Create a matching sub-collection under "PhD" in Zotero (if it doesn't exist)
2. Search Zotero for papers matching local titles
3. Add matching items to the new sub-collection

Usage:
    python3 scripts/push_papers_to_zotero.py              # Execute
    python3 scripts/push_papers_to_zotero.py --dry-run     # Preview only
"""

import os
import re
import sys
import yaml
import json
import time
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

CONFIG_PATH = os.path.join(PROJECT_DIR, 'config.yaml')
with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

ZOTERO_API_KEY = CONFIG['zotero']['api_key']
ZOTERO_LIBRARY_ID = str(CONFIG['zotero']['library_id'])

HEADERS = {
    'Zotero-API-Key': ZOTERO_API_KEY,
    'Zotero-API-Version': '3',
    'Content-Type': 'application/json',
}
BASE_URL = f"https://api.zotero.org/users/{ZOTERO_LIBRARY_ID}"

# PhD collection key in Zotero
PHD_COLLECTION_KEY = "XYEH4FPT"

PAPERS_TXT_DIR = os.path.join(PROJECT_DIR, 'papers_txt')

# Map local collection dirs → display names for Zotero sub-collections
COLLECTION_NAMES = {
    'germinal_centers': 'Germinal Centers',
    'hypermutation_systems': 'Hypermutation Systems',
    'cloning': 'Cloning',
    'directed_evolution': 'Directed Evolution',
    'reverse_translation': 'Reverse Translation',
    'uncategorized': 'Uncategorized',
}


def get_existing_subcollections():
    """Get existing sub-collections under PhD."""
    url = f"{BASE_URL}/collections/{PHD_COLLECTION_KEY}/collections?format=json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return {c['data']['name']: c['data']['key'] for c in resp.json()}


def create_subcollection(name):
    """Create a sub-collection under PhD."""
    url = f"{BASE_URL}/collections"
    payload = [{'name': name, 'parentCollection': PHD_COLLECTION_KEY}]
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()

    result = resp.json()
    # The API returns a dict with 'successful', 'unchanged', 'failed'
    if result.get('successful'):
        key = list(result['successful'].values())[0]['data']['key']
        return key
    elif result.get('unchanged'):
        key = list(result['unchanged'].values())[0]['data']['key']
        return key
    else:
        print(f"  ❌ Failed to create collection '{name}': {result.get('failed', {})}")
        return None


def search_library_item(title):
    """Search the entire Zotero library for an item by title."""
    # Use first 3 significant words to search
    words = [w for w in title.split() if len(w) > 3][:3]
    query = '+'.join(words)

    url = f"{BASE_URL}/items?format=json&q={query}&itemType=-attachment&limit=10"

    # Retry on rate limit
    for attempt in range(3):
        time.sleep(2)  # Rate limiting — Zotero allows ~10 req/min
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 429:
            wait = int(resp.headers.get('Retry-After', 10))
            print(f"    ⏳ Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        break
    else:
        print(f"    ❌ Rate limit exceeded after retries")
        return None

    items = resp.json()

    # Find best title match
    title_lower = title.lower().strip()
    for item in items:
        item_title = item['data'].get('title', '').lower().strip()
        # Check for substantial overlap
        if title_lower[:50] == item_title[:50]:
            return item
        # Fuzzy: check if most words match
        title_words = set(title_lower.split())
        item_words = set(item_title.split())
        if len(title_words & item_words) >= len(title_words) * 0.7:
            return item

    return None


def add_item_to_collection(item_key, item_version, existing_collections, new_collection_key):
    """Add an existing Zotero item to a collection."""
    if new_collection_key in existing_collections:
        return False  # already in this collection

    updated_collections = existing_collections + [new_collection_key]
    url = f"{BASE_URL}/items/{item_key}"
    payload = {'collections': updated_collections}
    patch_headers = {**HEADERS, 'If-Unmodified-Since-Version': str(item_version)}
    resp = requests.patch(url, headers=patch_headers, json=payload)
    resp.raise_for_status()
    return True


def parse_collection_titles(collection_dir):
    """Get paper titles from a local collection's INDEX.md."""
    index_path = os.path.join(PAPERS_TXT_DIR, collection_dir, 'INDEX.md')
    if not os.path.exists(index_path):
        return []

    with open(index_path, 'r') as f:
        content = f.read()

    titles = re.findall(r'^## (.+)$', content, re.MULTILINE)
    return [t.strip() for t in titles if not t.startswith('#')]


def push(dry_run=False):
    """Push local collections to Zotero."""
    print("Fetching existing PhD sub-collections...")
    existing = get_existing_subcollections()
    print(f"  Existing: {list(existing.keys())}\n")

    stats = {'collections_created': 0, 'items_added': 0, 'items_found': 0,
             'items_not_found': 0, 'items_already_in': 0}

    for local_dir, display_name in COLLECTION_NAMES.items():
        coll_path = os.path.join(PAPERS_TXT_DIR, local_dir)
        if not os.path.isdir(coll_path):
            print(f"  ⏭ Skipping {local_dir}/ (directory not found)")
            continue

        print(f"\n{'='*50}")
        print(f"📁 {display_name} ({local_dir}/)")
        print(f"{'='*50}")

        # Create or find Zotero sub-collection
        if display_name in existing:
            coll_key = existing[display_name]
            print(f"  ✓ Sub-collection exists (key: {coll_key})")
        else:
            if dry_run:
                print(f"  [DRY RUN] Would create sub-collection: {display_name}")
                coll_key = 'DRY_RUN'
            else:
                coll_key = create_subcollection(display_name)
                if coll_key:
                    print(f"  ✓ Created sub-collection (key: {coll_key})")
                    stats['collections_created'] += 1
                else:
                    print(f"  ❌ Failed to create sub-collection")
                    continue

        # Get paper titles from local INDEX.md
        titles = parse_collection_titles(local_dir)
        print(f"  {len(titles)} papers in local collection\n")

        for title in titles:
            # Search Zotero for this paper
            item = search_library_item(title)
            if item:
                stats['items_found'] += 1
                item_key = item['key']
                item_version = item['version']
                item_collections = item['data'].get('collections', [])
                zotero_title = item['data'].get('title', '')[:60]

                if coll_key in item_collections:
                    stats['items_already_in'] += 1
                    print(f"  ⏭ Already in collection: {zotero_title}")
                elif dry_run:
                    print(f"  [DRY RUN] Would add: {zotero_title}")
                    stats['items_added'] += 1
                else:
                    try:
                        add_item_to_collection(item_key, item_version, item_collections, coll_key)
                        stats['items_added'] += 1
                        print(f"  ✅ Added: {zotero_title}")
                    except Exception as e:
                        print(f"  ❌ Failed to add: {zotero_title} — {e}")
            else:
                stats['items_not_found'] += 1
                print(f"  ⚠ Not found in Zotero: {title[:60]}")

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{'='*50}")
    print(f"{prefix}Push Complete!")
    print(f"  Collections created: {stats['collections_created']}")
    print(f"  Papers found in Zotero: {stats['items_found']}")
    print(f"  Papers added to collections: {stats['items_added']}")
    print(f"  Already in correct collection: {stats['items_already_in']}")
    print(f"  Not found in Zotero: {stats['items_not_found']}")
    print(f"{'='*50}")


if __name__ == '__main__':
    push(dry_run='--dry-run' in sys.argv)
