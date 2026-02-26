#!/usr/bin/env python3
"""
Push a local experiment's lab notebook (markdown files) to Notion.

For a given EXP_XXX:
1. Creates a child database "Lab Documents" inside the experiment's Notion page
2. Creates one database entry per .md file, with the content parsed into Notion blocks
3. Replaces the experiment's main page body with summary.md content

Usage:
    python3 scripts/push_experiment_to_notion.py EXP_001
    python3 scripts/push_experiment_to_notion.py EXP_001 --dry-run
"""

import os
import re
import sys
import time
import json
import argparse
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from notion_client import (
    CONFIG, HEADERS,
    query_database, get_title_from_page, get_property_value,
    get_block_children, append_blocks_to_page,
)
import requests

# ─── Config ──────────────────────────────────────────────────────────

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/michaelsedbon/PhD/main"
LAB_DB_ID = CONFIG['notion']['lab_notebook_db']

# Map filenames to a type tag
FILE_TYPE_MAP = {
    'summary.md': 'Summary',
    'LOG.md': 'Log',
    'REPORT.md': 'Report',
    'V2_REPORT.md': 'Report',
    'PRIMER_DESIGN_REPORT.md': 'Report',
    'PCR_SIMULATION_REPORT.md': 'Report',
    'DOMESTICATION_REPORT.md': 'Report',
    'SCRIPTS.md': 'Scripts',
    'state_of_the_art_ecoli_genome_libraries.md': 'Literature Review',
}

# Files to exclude from the database (summary goes on the main page)
EXCLUDE_FROM_DB = set()  # We include summary.md in the DB too

# ─── Notion API helpers ──────────────────────────────────────────────

def create_database(parent_page_id, title, properties):
    """Create a child database inside a Notion page."""
    url = 'https://api.notion.com/v1/databases'
    body = {
        'parent': {'type': 'page_id', 'page_id': parent_page_id},
        'is_inline': True,
        'title': [{'type': 'text', 'text': {'content': title}}],
        'properties': properties,
    }
    resp = requests.post(url, headers=HEADERS, json=body)
    if not resp.ok:
        print(f"Error creating database: {resp.status_code}")
        print(resp.text)
        resp.raise_for_status()
    return resp.json()


def create_page_in_db(database_id, properties, children=None):
    """Create a page in a database, optionally with child blocks."""
    url = 'https://api.notion.com/v1/pages'
    body = {
        'parent': {'database_id': database_id},
        'properties': properties,
    }
    if children:
        # Notion accepts max 100 children on page creation
        body['children'] = children[:100]
    resp = requests.post(url, headers=HEADERS, json=body)
    if not resp.ok:
        print(f"Error creating page: {resp.status_code}")
        print(resp.text)
        resp.raise_for_status()
    page = resp.json()

    # Append remaining blocks in batches
    if children and len(children) > 100:
        page_id = page['id']
        remaining = children[100:]
        for i in range(0, len(remaining), 100):
            batch = remaining[i:i+100]
            append_blocks_to_page(page_id, batch)
            time.sleep(0.35)

    return page


def delete_block(block_id):
    """Delete a single block."""
    url = f'https://api.notion.com/v1/blocks/{block_id}'
    resp = requests.delete(url, headers=HEADERS)
    resp.raise_for_status()


def clear_page_content(page_id):
    """Delete all blocks from a page."""
    blocks = get_block_children(page_id)
    for b in blocks:
        delete_block(b['id'])
        time.sleep(0.15)
    print(f"  Cleared {len(blocks)} existing blocks")


# ─── Markdown → Notion block converter ──────────────────────────────

# Module-level context set by markdown_to_blocks
_current_exp_dir_relative = ''


def resolve_link_url(url):
    """Convert a relative URL to a GitHub raw URL. Pass through absolute URLs."""
    if url.startswith('http://') or url.startswith('https://'):
        return url
    # Relative link — convert to GitHub raw URL
    full_relative = os.path.join(_current_exp_dir_relative, url)
    full_relative = os.path.normpath(full_relative)
    return f"{GITHUB_RAW_BASE}/{full_relative}"


def rich_text(content, bold=False, code=False, italic=False, link=None):
    """Create a Notion rich_text object."""
    t = {'type': 'text', 'text': {'content': content}}
    if link:
        t['text']['link'] = {'url': resolve_link_url(link)}
    annotations = {}
    if bold: annotations['bold'] = True
    if code: annotations['code'] = True
    if italic: annotations['italic'] = True
    if annotations:
        t['annotations'] = annotations
    return t


def parse_inline(text):
    """Parse inline markdown (bold, code, italic, links) into rich_text array."""
    parts = []
    # Regex to find: **bold**, `code`, *italic*, [text](url)
    pattern = r'(\*\*(.+?)\*\*|`([^`]+)`|\*([^*]+)\*|\[([^\]]+)\]\(([^)]+)\))'
    last_end = 0

    for m in re.finditer(pattern, text):
        # Add plain text before this match
        if m.start() > last_end:
            plain = text[last_end:m.start()]
            if plain:
                parts.append(rich_text(plain))

        if m.group(2):  # **bold**
            parts.append(rich_text(m.group(2), bold=True))
        elif m.group(3):  # `code`
            parts.append(rich_text(m.group(3), code=True))
        elif m.group(4):  # *italic*
            parts.append(rich_text(m.group(4), italic=True))
        elif m.group(5) and m.group(6):  # [text](url)
            parts.append(rich_text(m.group(5), link=m.group(6)))

        last_end = m.end()

    # Trailing text
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            parts.append(rich_text(remaining))

    if not parts:
        parts.append(rich_text(text))

    return parts


def truncate_rich_text(rt_list, max_len=2000):
    """Ensure total content length doesn't exceed Notion's limit."""
    total = 0
    result = []
    for rt in rt_list:
        content = rt['text']['content']
        remaining = max_len - total
        if remaining <= 0:
            break
        if len(content) > remaining:
            rt = dict(rt)
            rt['text'] = dict(rt['text'])
            rt['text']['content'] = content[:remaining]
            result.append(rt)
            break
        result.append(rt)
        total += len(content)
    return result


def parse_table(lines):
    """Parse markdown table lines into a Notion table block."""
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)

    # Skip separator row (----)
    data_rows = []
    for row in rows:
        if all(re.match(r'^[-:]+$', cell) for cell in row if cell):
            continue
        data_rows.append(row)

    if not data_rows:
        return None

    num_cols = max(len(r) for r in data_rows)

    table_rows = []
    for row in data_rows:
        # Pad row to num_cols
        while len(row) < num_cols:
            row.append('')
        cells = []
        for cell in row[:num_cols]:
            cells.append(truncate_rich_text(parse_inline(cell)))
        table_rows.append({
            'object': 'block',
            'type': 'table_row',
            'table_row': {'cells': cells}
        })

    return {
        'object': 'block',
        'type': 'table',
        'table': {
            'table_width': num_cols,
            'has_column_header': True,
            'has_row_header': False,
            'children': table_rows,
        }
    }


def resolve_image_url(img_path, exp_dir_relative):
    """Convert a local image path to a GitHub raw URL."""
    # Handle relative paths like data/enzyme_ranking.png
    if img_path.startswith('http'):
        return img_path
    full_relative = os.path.join(exp_dir_relative, img_path)
    full_relative = os.path.normpath(full_relative)
    return f"{GITHUB_RAW_BASE}/{full_relative}"


def markdown_to_blocks(md_text, exp_dir_relative):
    """Convert markdown text to a list of Notion blocks."""
    global _current_exp_dir_relative
    _current_exp_dir_relative = exp_dir_relative
    lines = md_text.split('\n')
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Headings
        heading_match = re.match(r'^(#{1,3})\s+(.+)', stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            htype = f'heading_{level}'
            blocks.append({
                'object': 'block',
                'type': htype,
                htype: {'rich_text': truncate_rich_text(parse_inline(text))}
            })
            i += 1
            continue

        # Divider
        if re.match(r'^---+$', stripped):
            blocks.append({'object': 'block', 'type': 'divider', 'divider': {}})
            i += 1
            continue

        # Image: ![alt](path)
        img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)', stripped)
        if img_match:
            alt = img_match.group(1)
            path = img_match.group(2)
            url = resolve_image_url(path, exp_dir_relative)
            blocks.append({
                'object': 'block',
                'type': 'image',
                'image': {
                    'type': 'external',
                    'external': {'url': url},
                    'caption': [rich_text(alt)] if alt else []
                }
            })
            i += 1
            continue

        # Table: lines starting with |
        if stripped.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            table_block = parse_table(table_lines)
            if table_block:
                blocks.append(table_block)
            continue

        # Code block
        if stripped.startswith('```'):
            lang = stripped[3:].strip() or 'plain text'
            # Map common languages
            lang_map = {
                'bash': 'bash', 'python': 'python', 'python3': 'python',
                'markdown': 'markdown', 'json': 'json', 'csv': 'plain text',
                '': 'plain text',
            }
            lang = lang_map.get(lang, lang)
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_text = '\n'.join(code_lines)
            if len(code_text) > 2000:
                code_text = code_text[:1997] + '...'
            blocks.append({
                'object': 'block',
                'type': 'code',
                'code': {
                    'rich_text': [rich_text(code_text)],
                    'language': lang,
                }
            })
            continue

        # Blockquote / callout
        if stripped.startswith('>'):
            quote_text = stripped[1:].strip()
            # Check for callout pattern (emoji at start)
            if quote_text and ord(quote_text[0]) > 127:
                emoji = quote_text[0]
                content = quote_text[1:].strip()
                # Check for **Note:** or **Key ...** pattern
                if content.startswith('**'):
                    blocks.append({
                        'object': 'block',
                        'type': 'callout',
                        'callout': {
                            'rich_text': truncate_rich_text(parse_inline(content)),
                            'icon': {'type': 'emoji', 'emoji': emoji},
                        }
                    })
                else:
                    blocks.append({
                        'object': 'block',
                        'type': 'callout',
                        'callout': {
                            'rich_text': truncate_rich_text(parse_inline(content)),
                            'icon': {'type': 'emoji', 'emoji': emoji},
                        }
                    })
            else:
                blocks.append({
                    'object': 'block',
                    'type': 'quote',
                    'quote': {'rich_text': truncate_rich_text(parse_inline(quote_text))}
                })
            i += 1
            continue

        # Bulleted list
        if re.match(r'^[-*]\s+', stripped):
            text = re.sub(r'^[-*]\s+', '', stripped)
            blocks.append({
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {'rich_text': truncate_rich_text(parse_inline(text))}
            })
            i += 1
            continue

        # Numbered list
        num_match = re.match(r'^(\d+)[.)]\s+(.+)', stripped)
        if num_match:
            text = num_match.group(2)
            blocks.append({
                'object': 'block',
                'type': 'numbered_list_item',
                'numbered_list_item': {'rich_text': truncate_rich_text(parse_inline(text))}
            })
            i += 1
            continue

        # Link-only line (like [→ Interactive version](url)) — make a bookmark or paragraph
        link_only = re.match(r'^\[([^\]]+)\]\(([^)]+)\)$', stripped)
        if link_only:
            blocks.append({
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {'rich_text': truncate_rich_text(parse_inline(stripped))}
            })
            i += 1
            continue

        # Paragraph (default) — collect continuation lines
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            # Stop if next line is a block-level element
            if (not next_line or
                    next_line.startswith('#') or
                    next_line.startswith('---') or
                    next_line.startswith('|') or
                    next_line.startswith('```') or
                    next_line.startswith('>') or
                    next_line.startswith('![') or
                    re.match(r'^[-*]\s+', next_line) or
                    re.match(r'^\d+[.)]\s+', next_line)):
                break
            para_lines.append(next_line)
            i += 1

        para_text = ' '.join(para_lines)
        if len(para_text) > 2000:
            # Split long paragraphs
            chunks = [para_text[j:j+2000] for j in range(0, len(para_text), 2000)]
            for chunk in chunks:
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {'rich_text': truncate_rich_text(parse_inline(chunk))}
                })
        else:
            blocks.append({
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {'rich_text': truncate_rich_text(parse_inline(para_text))}
            })

    return blocks


# ─── Find experiment page ────────────────────────────────────────────

def find_experiment_page(exp_id):
    """Find the Notion page for an experiment by its EXP_xxx property or title."""
    pages = query_database(LAB_DB_ID)
    for page in pages:
        title = get_title_from_page(page)
        exp_num = get_property_value(page, 'EXP_xxx')
        if exp_num == exp_id or exp_id.lower() in title.lower():
            return page
    return None


# ─── Main logic ──────────────────────────────────────────────────────

def get_md_files(exp_dir):
    """Get all markdown files in the experiment directory (not in subdirs)."""
    md_files = []
    for f in sorted(os.listdir(exp_dir)):
        if f.endswith('.md') and os.path.isfile(os.path.join(exp_dir, f)):
            md_files.append(f)
    return md_files


def classify_file(filename):
    """Get display name and type for a markdown file."""
    name = os.path.splitext(filename)[0]
    # Make it title-case friendly
    display = name.replace('_', ' ').title()
    doc_type = FILE_TYPE_MAP.get(filename, 'Report')
    return display, doc_type


def push_experiment(exp_id, dry_run=False):
    """Push an experiment's markdown files to Notion."""
    exp_dir = os.path.join(PROJECT_DIR, 'experiments', exp_id)
    exp_dir_relative = f"experiments/{exp_id}"

    if not os.path.isdir(exp_dir):
        print(f"❌ Experiment directory not found: {exp_dir}")
        sys.exit(1)

    # Find Notion page
    print(f"🔍 Finding Notion page for {exp_id}...")
    page = find_experiment_page(exp_id)
    if not page:
        print(f"❌ No Notion page found for {exp_id}")
        sys.exit(1)

    page_id = page['id']
    page_title = get_title_from_page(page)
    print(f"  Found: {page_title} ({page_id})")

    # Get markdown files
    md_files = get_md_files(exp_dir)
    print(f"\n📄 Found {len(md_files)} markdown files:")
    for f in md_files:
        display, doc_type = classify_file(f)
        print(f"  - {f} → {display} [{doc_type}]")

    if dry_run:
        print("\n🏃 Dry run — parsing all files...")
        for f in md_files:
            filepath = os.path.join(exp_dir, f)
            with open(filepath, 'r') as fh:
                md_text = fh.read()
            blocks = markdown_to_blocks(md_text, exp_dir_relative)
            print(f"  {f}: {len(blocks)} blocks")
        print("\n✅ Dry run complete. No changes made to Notion.")
        return

    # ── Step 1: Clear existing page content ──
    print(f"\n🗑️  Clearing existing page content...")
    clear_page_content(page_id)
    time.sleep(0.5)

    # ── Step 2: Create child database ──
    print(f"\n📊 Creating 'Lab Documents' database...")
    db_properties = {
        'Name': {'title': {}},
        'Type': {
            'select': {
                'options': [
                    {'name': 'Report', 'color': 'blue'},
                    {'name': 'Log', 'color': 'green'},
                    {'name': 'Summary', 'color': 'purple'},
                    {'name': 'Scripts', 'color': 'orange'},
                    {'name': 'Literature Review', 'color': 'yellow'},
                ]
            }
        },
        'Filename': {'rich_text': {}},
        'Last Modified': {'date': {}},
    }
    db = create_database(page_id, 'Lab Documents', db_properties)
    db_id = db['id']
    print(f"  Created database: {db_id}")
    time.sleep(0.5)

    # ── Step 3: Populate database entries ──
    print(f"\n📝 Creating database entries...")
    for f in md_files:
        filepath = os.path.join(exp_dir, f)
        display, doc_type = classify_file(f)

        # Read and parse markdown
        with open(filepath, 'r') as fh:
            md_text = fh.read()
        blocks = markdown_to_blocks(md_text, exp_dir_relative)

        # Get file modification time
        mtime = os.path.getmtime(filepath)
        mod_date = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime('%Y-%m-%d')

        # Build properties
        props = {
            'Name': {'title': [{'text': {'content': display}}]},
            'Type': {'select': {'name': doc_type}},
            'Filename': {'rich_text': [{'text': {'content': f}}]},
            'Last Modified': {'date': {'start': mod_date}},
        }

        print(f"  Creating: {display} ({len(blocks)} blocks)...", end='', flush=True)
        entry = create_page_in_db(db_id, props, blocks)
        print(f" ✅")
        time.sleep(0.5)

    # ── Step 4: Populate main page with summary.md ──
    summary_path = os.path.join(exp_dir, 'summary.md')
    if os.path.exists(summary_path):
        print(f"\n📖 Populating main page with summary.md...")
        with open(summary_path, 'r') as fh:
            summary_text = fh.read()
        summary_blocks = markdown_to_blocks(summary_text, exp_dir_relative)

        # Append in batches (database was already added as first child)
        for i in range(0, len(summary_blocks), 100):
            batch = summary_blocks[i:i+100]
            append_blocks_to_page(page_id, batch)
            time.sleep(0.35)
        print(f"  Added {len(summary_blocks)} blocks to main page")

    print(f"\n✅ Done! Pushed {len(md_files)} documents to Notion.")
    print(f"   Database: 'Lab Documents' with {len(md_files)} entries")
    print(f"   Main page: populated with summary.md")
    print(f"   🔗 {page.get('url', '')}")


# ─── CLI ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Push experiment lab notebook to Notion')
    parser.add_argument('experiment', help='Experiment ID (e.g. EXP_001)')
    parser.add_argument('--dry-run', action='store_true', help='Parse files without modifying Notion')
    args = parser.parse_args()

    push_experiment(args.experiment, dry_run=args.dry_run)
