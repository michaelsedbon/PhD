#!/usr/bin/env python3
"""
Sync bibliography from the Notion "Synthetica Biblio" database.

For each paper in the bibliography:
1. Download the PDF attachment (if any) → papers/
2. Convert PDF to text → papers_txt/
3. Append a stub entry to papers_txt/INDEX.md

Only processes papers not already downloaded.

Usage:
    python3 sync_bibliography.py          # Sync new papers
    python3 sync_bibliography.py --list   # List all papers in the database
"""

import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from notion_client import (
    CONFIG, query_database, get_title_from_page,
    get_property_value, download_file, sanitize_filename
)
from pdf_to_text import pdf_to_text

BIB_DB = CONFIG['notion']['bibliography_db']
PAPERS_DIR = os.path.join(PROJECT_DIR, 'papers')
PAPERS_TXT_DIR = os.path.join(PROJECT_DIR, 'papers_txt')
INDEX_PATH = os.path.join(PAPERS_TXT_DIR, 'INDEX.md')


def get_existing_papers():
    """Get set of already-downloaded PDF basenames (without extension)."""
    if not os.path.exists(PAPERS_DIR):
        return set()
    return {os.path.splitext(f)[0] for f in os.listdir(PAPERS_DIR) if f.endswith('.pdf')}


def get_indexed_papers():
    """Get set of paper filenames already in INDEX.md."""
    if not os.path.exists(INDEX_PATH):
        return set()
    with open(INDEX_PATH, 'r') as f:
        content = f.read()
    # Extract filenames from **File:** lines
    import re
    return set(re.findall(r'\*\*File:\*\*\s*`([^`]+)`', content))


def make_paper_filename(title, subjects=None):
    """Generate a clean filename from paper title."""
    # Take first 5 meaningful words
    words = title.split()[:5]
    name = '_'.join(words)
    name = sanitize_filename(name)
    return name


def append_to_index(title, filename, subjects=None, url=None):
    """Append a new stub entry to INDEX.md."""
    entry = f"""
## {title}
**File:** `{filename}`
**Subjects:** {', '.join(subjects) if subjects else 'N/A'}
**URL:** {url if url else 'N/A'}

*(Auto-generated stub — update summary after reviewing the paper.)*

---
"""
    with open(INDEX_PATH, 'a') as f:
        f.write(entry)


def sync():
    """Sync bibliography from Notion."""
    os.makedirs(PAPERS_DIR, exist_ok=True)
    os.makedirs(PAPERS_TXT_DIR, exist_ok=True)

    existing = get_existing_papers()
    indexed = get_indexed_papers()

    print(f"Fetching bibliography from Notion...")
    pages = query_database(BIB_DB)
    print(f"Found {len(pages)} papers in bibliography.")

    downloaded = 0
    skipped = 0
    no_pdf = 0
    errors = 0

    for page in pages:
        title = get_title_from_page(page)
        subjects = get_property_value(page, 'Subject') or []
        url = get_property_value(page, 'URL') or ''
        paper_files = get_property_value(page, 'Paper') or []

        if not title:
            continue

        filename_base = make_paper_filename(title, subjects)

        # Check if already downloaded
        if filename_base in existing:
            skipped += 1
            continue

        if not paper_files:
            no_pdf += 1
            print(f"  ⚠ No PDF attached: {title}")
            continue

        # Download the first PDF
        pdf_info = paper_files[0]
        pdf_url = pdf_info.get('url', '')
        if not pdf_url:
            no_pdf += 1
            continue

        pdf_path = os.path.join(PAPERS_DIR, f'{filename_base}.pdf')

        try:
            print(f"  ↓ Downloading: {title}")
            download_file(pdf_url, pdf_path)
            downloaded += 1

            # Convert to text
            try:
                txt_path = pdf_to_text(pdf_path, PAPERS_TXT_DIR)
            except Exception as e:
                print(f"  ⚠ Text extraction failed: {e}")

            # Add to INDEX.md
            txt_filename = f'{filename_base}.txt'
            if txt_filename not in indexed:
                append_to_index(title, txt_filename, subjects, url)
                print(f"  📝 Added to INDEX.md")

        except Exception as e:
            print(f"  ✗ Failed: {title} — {e}")
            errors += 1

    print(f"\n{'='*50}")
    print(f"Bibliography Sync Complete!")
    print(f"  Downloaded: {downloaded}")
    print(f"  Already present: {skipped}")
    print(f"  No PDF attached: {no_pdf}")
    print(f"  Errors: {errors}")
    print(f"{'='*50}")

    return downloaded


def list_papers():
    """List all papers in the bibliography database."""
    pages = query_database(BIB_DB)
    print(f"\n📚 Synthetica Bibliography ({len(pages)} papers)\n")
    for i, page in enumerate(pages, 1):
        title = get_title_from_page(page)
        subjects = get_property_value(page, 'Subject') or []
        url = get_property_value(page, 'URL') or ''
        paper_files = get_property_value(page, 'Paper') or []
        has_pdf = '📄' if paper_files else '  '
        subj_str = ', '.join(subjects) if subjects else ''
        print(f"  {i:3d}. {has_pdf} {title}")
        if subj_str:
            print(f"       Subjects: {subj_str}")
        if url:
            print(f"       URL: {url}")
    print()


if __name__ == '__main__':
    if '--list' in sys.argv:
        list_papers()
    else:
        sync()
