#!/usr/bin/env python3
"""
Reorganize papers_txt/ into collection subdirectories and generate
a tiered index system (CATALOG.md + per-collection INDEX.md).

Parses the existing INDEX.md to extract paper entries with their subjects,
then moves .txt files into subject-based subdirectories.

Usage:
    python3 scripts/reorganize_papers.py              # Execute
    python3 scripts/reorganize_papers.py --dry-run     # Preview only
"""

import os
import re
import shutil
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PAPERS_TXT_DIR = os.path.join(PROJECT_DIR, 'papers_txt')
INDEX_PATH = os.path.join(PAPERS_TXT_DIR, 'INDEX.md')

# Map raw subject tags → clean collection directory names
SUBJECT_TO_COLLECTION = {
    'HyperMutation Systems': 'hypermutation_systems',
    'Germinal centers': 'germinal_centers',
    'Cloning': 'cloning',
    'Colicin': 'hypermutation_systems',  # merge into hypermutation (related)
    'ST Ctrl DE': 'directed_evolution',
    'Directed evolution Moving Target': 'directed_evolution',
    'Directed evoltion concepts': 'directed_evolution',
    'Reverse Translation': 'reverse_translation',
    'optogenetic T7DNAp': 'hypermutation_systems',
    'N/A': 'uncategorized',
}

# For papers with multiple subjects, use priority order
COLLECTION_PRIORITY = [
    'germinal_centers',
    'hypermutation_systems',
    'cloning',
    'directed_evolution',
    'reverse_translation',
    'uncategorized',
]


def parse_index(index_path):
    """Parse INDEX.md into a list of paper entries."""
    with open(index_path, 'r') as f:
        content = f.read()

    # Split by --- separators
    blocks = re.split(r'\n---\n', content)
    papers = []

    for block in blocks:
        block = block.strip()
        if not block or block.startswith('# Paper Index'):
            continue

        # Extract title
        title_match = re.search(r'^## (.+)$', block, re.MULTILINE)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        # Extract filename
        file_match = re.search(r'\*\*File:\*\*\s*`([^`]+)`', block)
        filename = file_match.group(1).strip() if file_match else None

        # Extract subjects
        subj_match = re.search(r'\*\*Subjects:\*\*\s*(.+)$', block, re.MULTILINE)
        subjects_raw = subj_match.group(1).strip() if subj_match else 'N/A'
        subjects = [s.strip() for s in subjects_raw.split(',')]

        # Extract URL
        url_match = re.search(r'\*\*URL:\*\*\s*(.+)$', block, re.MULTILINE)
        url = url_match.group(1).strip() if url_match else ''

        # Extract summary (everything after the metadata lines)
        lines = block.split('\n')
        summary_lines = []
        past_metadata = False
        for line in lines:
            if past_metadata:
                summary_lines.append(line)
            elif line.startswith('**URL:**') or line.startswith('**Subjects:**') or line.startswith('**File:**'):
                continue
            elif line.startswith('## '):
                continue
            else:
                if line.strip() and not line.startswith('**'):
                    past_metadata = True
                    summary_lines.append(line)

        summary = '\n'.join(summary_lines).strip()

        # Skip duplicate marker entries
        if '*(Duplicate entry' in summary:
            continue

        if filename:
            papers.append({
                'title': title,
                'filename': filename,
                'subjects': subjects,
                'url': url,
                'summary': summary,
            })

    return papers


def assign_collection(subjects):
    """Assign a paper to a single collection based on its subjects."""
    collections = set()
    for subj in subjects:
        coll = SUBJECT_TO_COLLECTION.get(subj, 'uncategorized')
        collections.add(coll)

    # Use priority order to pick one
    for coll in COLLECTION_PRIORITY:
        if coll in collections:
            return coll
    return 'uncategorized'


def generate_catalog(papers_by_collection):
    """Generate CATALOG.md content."""
    lines = [
        '# Paper Catalog',
        '',
        'Compact index of all papers organized by collection.',
        'Read this first to find relevant papers, then load the per-collection INDEX.md for full summaries.',
        '',
        '---',
        '',
    ]

    total = 0
    for coll in COLLECTION_PRIORITY:
        if coll not in papers_by_collection:
            continue
        papers = papers_by_collection[coll]
        coll_display = coll.replace('_', ' ').title()
        lines.append(f'## {coll_display} ({len(papers)} papers)')
        lines.append('')
        lines.append(f'📂 `{coll}/INDEX.md`')
        lines.append('')
        lines.append('| Title | File |')
        lines.append('|-------|------|')
        for p in papers:
            short_title = p['title'][:80] + ('...' if len(p['title']) > 80 else '')
            lines.append(f"| {short_title} | `{coll}/{p['filename']}` |")
        lines.append('')
        lines.append('---')
        lines.append('')
        total += len(papers)

    lines.insert(6, f'**Total: {total} papers across {len(papers_by_collection)} collections.**')
    lines.insert(7, '')

    return '\n'.join(lines)


def generate_collection_index(collection_name, papers):
    """Generate a per-collection INDEX.md."""
    coll_display = collection_name.replace('_', ' ').title()
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
        lines.append(f"**Subjects:** {', '.join(p['subjects'])}")
        lines.append(f"**URL:** {p['url']}")
        lines.append('')
        if p['summary']:
            lines.append(p['summary'])
        else:
            lines.append('*(Summary pending — read the full text to generate one.)*')
        lines.append('')
        lines.append('---')
        lines.append('')

    return '\n'.join(lines)


def reorganize(dry_run=False):
    """Main reorganization logic."""
    print("Parsing INDEX.md...")
    papers = parse_index(INDEX_PATH)
    print(f"  Found {len(papers)} paper entries.\n")

    # Assign collections
    papers_by_collection = {}
    for paper in papers:
        coll = assign_collection(paper['subjects'])
        papers_by_collection.setdefault(coll, []).append(paper)

    print("Collection assignments:")
    for coll in COLLECTION_PRIORITY:
        if coll in papers_by_collection:
            print(f"  {coll}: {len(papers_by_collection[coll])} papers")
    print()

    if dry_run:
        print("[DRY RUN] Would create these directories and move files:\n")

    # Create directories, move files, generate indexes
    for coll, coll_papers in papers_by_collection.items():
        coll_dir = os.path.join(PAPERS_TXT_DIR, coll)

        if dry_run:
            print(f"  📁 {coll}/")
        else:
            os.makedirs(coll_dir, exist_ok=True)

        for paper in coll_papers:
            src = os.path.join(PAPERS_TXT_DIR, paper['filename'])
            dst = os.path.join(coll_dir, paper['filename'])

            if os.path.exists(src):
                if dry_run:
                    print(f"     → {paper['filename']}")
                else:
                    shutil.copy2(src, dst)
                    print(f"  ✓ Copied {paper['filename']} → {coll}/")
            else:
                print(f"  ⚠ File not found: {paper['filename']}")

        # Generate per-collection INDEX.md
        index_content = generate_collection_index(coll, coll_papers)
        index_path = os.path.join(coll_dir, 'INDEX.md')
        if dry_run:
            print(f"     📝 Would create {coll}/INDEX.md ({len(coll_papers)} entries)")
        else:
            with open(index_path, 'w') as f:
                f.write(index_content)
            print(f"  📝 Created {coll}/INDEX.md")

    # Generate CATALOG.md
    catalog_content = generate_catalog(papers_by_collection)
    catalog_path = os.path.join(PAPERS_TXT_DIR, 'CATALOG.md')
    if dry_run:
        print(f"\n  📝 Would create CATALOG.md ({len(papers)} total entries)")
    else:
        with open(catalog_path, 'w') as f:
            f.write(catalog_content)
        print(f"\n  📝 Created CATALOG.md")

    # Keep legacy INDEX.md untouched
    print(f"\n  ℹ Legacy INDEX.md preserved (not modified).")

    print(f"\n{'='*50}")
    print(f"{'[DRY RUN] ' if dry_run else ''}Reorganization Complete!")
    print(f"  Papers processed: {len(papers)}")
    print(f"  Collections created: {len(papers_by_collection)}")
    print(f"{'='*50}")


if __name__ == '__main__':
    reorganize(dry_run='--dry-run' in sys.argv)
