#!/usr/bin/env python3
"""
Sync experiments from the Notion "SYNTHETICA Lab Notebook" database.

For each experiment entry:
1. Create experiments/EXP_XXX/ folder
2. Fetch the full page content → experiments/EXP_XXX/summary.md
3. If Airtable links exist → fetch_airtable.py to pull data
4. Append entry to experiments/EXP_INDEX.md

Only processes experiments not already synced.

Usage:
    python3 sync_experiments.py          # Sync new experiments
    python3 sync_experiments.py --list   # List all experiments
    python3 sync_experiments.py --force  # Re-sync all experiments (overwrite)
"""

import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from notion_client import (
    CONFIG, query_database, get_title_from_page,
    get_property_value, get_page_content_as_markdown
)

LAB_DB = CONFIG['notion']['lab_notebook_db']
EXPERIMENTS_DIR = os.path.join(PROJECT_DIR, 'experiments')
EXP_INDEX_PATH = os.path.join(EXPERIMENTS_DIR, 'EXP_INDEX.md')


def get_existing_experiments():
    """Get set of already-synced experiment IDs."""
    if not os.path.exists(EXPERIMENTS_DIR):
        return set()
    return {d for d in os.listdir(EXPERIMENTS_DIR)
            if os.path.isdir(os.path.join(EXPERIMENTS_DIR, d)) and d.startswith('EXP_')}


def get_indexed_experiments():
    """Get set of experiment IDs already in EXP_INDEX.md."""
    if not os.path.exists(EXP_INDEX_PATH):
        return set()
    with open(EXP_INDEX_PATH, 'r') as f:
        content = f.read()
    import re
    return set(re.findall(r'## (EXP_\d+)', content))


def append_to_exp_index(exp_id, title, start_date='', airtable_links=None):
    """Append a new experiment entry to EXP_INDEX.md."""
    airtable_str = ', '.join(airtable_links) if airtable_links else 'None'
    entry = f"""
## {exp_id}
**Title:** {title}
**Start Date:** {start_date if start_date else 'N/A'}
**Airtable Links:** {airtable_str}
**Folder:** `experiments/{exp_id}/`

*(Auto-generated stub — update summary after reviewing the experiment.)*

---
"""
    with open(EXP_INDEX_PATH, 'a') as f:
        f.write(entry)


def sync(force=False):
    """Sync experiments from Notion."""
    os.makedirs(EXPERIMENTS_DIR, exist_ok=True)

    existing = get_existing_experiments()
    indexed = get_indexed_experiments()

    print(f"Fetching experiments from Notion Lab Notebook...")
    pages = query_database(LAB_DB)
    print(f"Found {len(pages)} experiment entries.")

    synced = 0
    skipped = 0
    errors = 0

    for page in pages:
        title = get_title_from_page(page)
        exp_number = get_property_value(page, 'Exp Number') or ''
        start_date = get_property_value(page, 'Start Date') or ''
        airtable_links = get_property_value(page, 'Airtable Link') or []

        if not exp_number:
            print(f"  ⚠ No experiment number: {title}")
            continue

        exp_id = exp_number  # e.g., "EXP_001"

        # Skip if already synced (unless force)
        if exp_id in existing and not force:
            skipped += 1
            continue

        exp_dir = os.path.join(EXPERIMENTS_DIR, exp_id)
        os.makedirs(exp_dir, exist_ok=True)

        # Fetch full page content as markdown
        page_id = page['id']
        try:
            print(f"  📓 Syncing: {exp_id} — {title}")
            content = get_page_content_as_markdown(page_id)

            # Write summary.md
            summary_path = os.path.join(exp_dir, 'summary.md')
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"# {exp_id}: {title}\n\n")
                f.write(f"**Start Date:** {start_date}\n")
                f.write(f"**Airtable Links:** {', '.join(airtable_links) if airtable_links else 'None'}\n\n")
                f.write("---\n\n")
                f.write(content)

            print(f"  ✅ Written: {summary_path}")

            # If Airtable links exist, try to fetch data
            if airtable_links:
                try:
                    from fetch_airtable import fetch_table_data
                    for table_name in airtable_links:
                        data_path = os.path.join(exp_dir, f'airtable_{table_name}.json')
                        fetch_table_data(table_name, data_path)
                        print(f"  📊 Fetched Airtable data: {table_name}")
                except ImportError:
                    print(f"  ⚠ fetch_airtable.py not available, skipping Airtable data")
                except Exception as e:
                    print(f"  ⚠ Airtable fetch failed: {e}")

            # Add to EXP_INDEX.md
            if exp_id not in indexed or force:
                append_to_exp_index(exp_id, title, start_date, airtable_links)
                print(f"  📝 Added to EXP_INDEX.md")

            synced += 1

        except Exception as e:
            print(f"  ✗ Failed: {exp_id} — {e}")
            errors += 1

    print(f"\n{'='*50}")
    print(f"Experiment Sync Complete!")
    print(f"  Synced: {synced}")
    print(f"  Already present: {skipped}")
    print(f"  Errors: {errors}")
    print(f"{'='*50}")

    return synced


def list_experiments():
    """List all experiments in the lab notebook."""
    pages = query_database(LAB_DB)
    print(f"\n🔬 SYNTHETICA Lab Notebook ({len(pages)} experiments)\n")
    for i, page in enumerate(pages, 1):
        title = get_title_from_page(page)
        exp_number = get_property_value(page, 'Exp Number') or 'N/A'
        start_date = get_property_value(page, 'Start Date') or ''
        airtable_links = get_property_value(page, 'Airtable Link') or []
        at_str = f" → Airtable: {', '.join(airtable_links)}" if airtable_links else ''
        print(f"  {i:3d}. [{exp_number}] {title}  {start_date}{at_str}")
    print()


if __name__ == '__main__':
    if '--list' in sys.argv:
        list_experiments()
    elif '--force' in sys.argv:
        sync(force=True)
    else:
        sync()
