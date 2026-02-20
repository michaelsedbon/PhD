#!/usr/bin/env python3
"""
Shared Notion API client for the Personal Lab workspace.

Loads config from config.yaml and provides helper functions for:
- Querying databases
- Fetching page content (blocks → markdown)
- Downloading file attachments
"""

import os
import re
import json
import time
import requests
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

def load_config():
    """Load config from config.yaml."""
    config_path = os.path.join(PROJECT_DIR, 'config.yaml')
    with open(config_path) as f:
        return yaml.safe_load(f)

CONFIG = load_config()
NOTION_TOKEN = CONFIG['notion']['token']
NOTION_VERSION = '2022-06-28'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': NOTION_VERSION,
    'Content-Type': 'application/json',
}


def query_database(database_id, filter_obj=None, sorts=None, start_cursor=None):
    """
    Query a Notion database. Returns all pages (handles pagination).
    """
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    all_results = []
    has_more = True
    cursor = start_cursor

    while has_more:
        body = {}
        if filter_obj:
            body['filter'] = filter_obj
        if sorts:
            body['sorts'] = sorts
        if cursor:
            body['start_cursor'] = cursor

        resp = requests.post(url, headers=HEADERS, json=body)
        if not resp.ok:
            print(f"Error querying database: {resp.status_code}")
            print(resp.text)
            resp.raise_for_status()
        data = resp.json()

        all_results.extend(data.get('results', []))
        has_more = data.get('has_more', False)
        cursor = data.get('next_cursor')

    return all_results


def get_page(page_id):
    """Fetch a single page object."""
    url = f'https://api.notion.com/v1/pages/{page_id}'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_block_children(block_id):
    """Fetch all child blocks of a block (handles pagination)."""
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'
    all_blocks = []
    has_more = True
    cursor = None

    while has_more:
        params = {'page_size': 100}
        if cursor:
            params['start_cursor'] = cursor

        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()

        all_blocks.extend(data.get('results', []))
        has_more = data.get('has_more', False)
        cursor = data.get('next_cursor')

    return all_blocks


def rich_text_to_plain(rich_text_list):
    """Convert a Notion rich_text array to plain text."""
    return ''.join(rt.get('plain_text', '') for rt in rich_text_list)


def blocks_to_markdown(blocks, indent=0):
    """
    Convert a list of Notion blocks to markdown text.
    Recursively handles nested blocks.
    """
    lines = []
    prefix = '  ' * indent

    for block in blocks:
        btype = block.get('type', '')
        bdata = block.get(btype, {})

        if btype == 'paragraph':
            text = rich_text_to_plain(bdata.get('rich_text', []))
            lines.append(f'{prefix}{text}')
            lines.append('')

        elif btype in ('heading_1', 'heading_2', 'heading_3'):
            level = int(btype[-1])
            text = rich_text_to_plain(bdata.get('rich_text', []))
            lines.append(f'{prefix}{"#" * level} {text}')
            lines.append('')

        elif btype == 'bulleted_list_item':
            text = rich_text_to_plain(bdata.get('rich_text', []))
            lines.append(f'{prefix}- {text}')

        elif btype == 'numbered_list_item':
            text = rich_text_to_plain(bdata.get('rich_text', []))
            lines.append(f'{prefix}1. {text}')

        elif btype == 'to_do':
            text = rich_text_to_plain(bdata.get('rich_text', []))
            checked = '☑' if bdata.get('checked') else '☐'
            lines.append(f'{prefix}{checked} {text}')

        elif btype == 'toggle':
            text = rich_text_to_plain(bdata.get('rich_text', []))
            lines.append(f'{prefix}<details><summary>{text}</summary>')

        elif btype == 'code':
            text = rich_text_to_plain(bdata.get('rich_text', []))
            lang = bdata.get('language', '')
            lines.append(f'{prefix}```{lang}')
            lines.append(text)
            lines.append(f'{prefix}```')
            lines.append('')

        elif btype == 'callout':
            text = rich_text_to_plain(bdata.get('rich_text', []))
            icon = bdata.get('icon', {}).get('emoji', '💡')
            lines.append(f'{prefix}> {icon} {text}')
            lines.append('')

        elif btype == 'quote':
            text = rich_text_to_plain(bdata.get('rich_text', []))
            lines.append(f'{prefix}> {text}')
            lines.append('')

        elif btype == 'divider':
            lines.append(f'{prefix}---')
            lines.append('')

        elif btype == 'image':
            img_type = bdata.get('type', '')
            url = ''
            if img_type == 'file':
                url = bdata.get('file', {}).get('url', '')
            elif img_type == 'external':
                url = bdata.get('external', {}).get('url', '')
            caption = rich_text_to_plain(bdata.get('caption', []))
            lines.append(f'{prefix}![{caption}]({url})')
            lines.append('')

        elif btype == 'table':
            # Fetch table rows
            pass

        elif btype == 'child_database':
            title = bdata.get('title', 'Embedded Database')
            lines.append(f'{prefix}📊 **Embedded Database:** {title}')
            lines.append('')

        else:
            # Generic fallback
            text = ''
            if 'rich_text' in bdata:
                text = rich_text_to_plain(bdata['rich_text'])
            if text:
                lines.append(f'{prefix}{text}')
                lines.append('')

        # Handle nested children
        if block.get('has_children'):
            children = get_block_children(block['id'])
            nested = blocks_to_markdown(children, indent + 1)
            lines.append(nested)

            if btype == 'toggle':
                lines.append(f'{prefix}</details>')
                lines.append('')

    return '\n'.join(lines)


def get_page_content_as_markdown(page_id):
    """Fetch all blocks of a page and convert to markdown."""
    blocks = get_block_children(page_id)
    return blocks_to_markdown(blocks)


def get_title_from_page(page):
    """Extract the title from a Notion page object."""
    props = page.get('properties', {})
    for prop_name, prop_data in props.items():
        if prop_data.get('type') == 'title':
            return rich_text_to_plain(prop_data.get('title', []))
    return 'Untitled'


def get_property_value(page, property_name):
    """
    Extract a property value from a Notion page.
    Returns the value in a simplified form depending on type.
    """
    props = page.get('properties', {})
    prop = props.get(property_name, {})
    ptype = prop.get('type', '')

    if ptype == 'title':
        return rich_text_to_plain(prop.get('title', []))
    elif ptype == 'rich_text':
        return rich_text_to_plain(prop.get('rich_text', []))
    elif ptype == 'number':
        return prop.get('number')
    elif ptype == 'select':
        sel = prop.get('select')
        return sel.get('name', '') if sel else ''
    elif ptype == 'multi_select':
        return [opt.get('name', '') for opt in prop.get('multi_select', [])]
    elif ptype == 'date':
        d = prop.get('date')
        return d.get('start', '') if d else ''
    elif ptype == 'url':
        return prop.get('url', '')
    elif ptype == 'email':
        return prop.get('email', '')
    elif ptype == 'phone_number':
        return prop.get('phone_number', '')
    elif ptype == 'checkbox':
        return prop.get('checkbox', False)
    elif ptype == 'files':
        files = prop.get('files', [])
        result = []
        for f in files:
            if f.get('type') == 'file':
                result.append({
                    'name': f.get('name', ''),
                    'url': f.get('file', {}).get('url', ''),
                    'expiry': f.get('file', {}).get('expiry_time', ''),
                })
            elif f.get('type') == 'external':
                result.append({
                    'name': f.get('name', ''),
                    'url': f.get('external', {}).get('url', ''),
                })
        return result
    elif ptype == 'relation':
        return [r.get('id', '') for r in prop.get('relation', [])]
    elif ptype == 'status':
        s = prop.get('status')
        return s.get('name', '') if s else ''
    else:
        return None


def download_file(url, dest_path):
    """Download a file from a URL (works for Notion S3 signed URLs)."""
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(dest_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return dest_path


def append_blocks_to_page(page_id, blocks):
    """Append blocks to a page or block."""
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'
    resp = requests.patch(url, headers=HEADERS, json={'children': blocks})
    resp.raise_for_status()
    return resp.json()


def sanitize_filename(name):
    """Make a string safe for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.strip('. ')
    return name[:200]


# --- CLI test mode ---
if __name__ == '__main__':
    import sys
    if '--test' in sys.argv:
        print("Testing Notion API connection...")
        try:
            # Test lab notebook
            lab_db = CONFIG['notion']['lab_notebook_db']
            results = query_database(lab_db)
            print(f"✅ Lab Notebook: {len(results)} entries found")
            for r in results[:3]:
                title = get_title_from_page(r)
                print(f"   - {title}")

            # Test bibliography
            bib_db = CONFIG['notion']['bibliography_db']
            results = query_database(bib_db)
            print(f"✅ Bibliography: {len(results)} entries found")
            for r in results[:3]:
                title = get_title_from_page(r)
                print(f"   - {title}")

            print("\n✅ All Notion connections working!")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            sys.exit(1)
    else:
        print("Usage: python3 notion_client.py --test")
