#!/usr/bin/env python3
"""
Fetch data from Airtable tables.

Uses the Airtable REST API to pull records from a specified base/table.

Usage:
    python3 fetch_airtable.py --test                  # Test connection, list tables
    python3 fetch_airtable.py <table_name> [output]   # Fetch table → JSON
    python3 fetch_airtable.py --all <output_dir>      # Fetch all tables → JSON files
"""

import os
import sys
import json
import requests
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

def load_config():
    config_path = os.path.join(PROJECT_DIR, 'config.yaml')
    with open(config_path) as f:
        return yaml.safe_load(f)

CONFIG = load_config()
AIRTABLE_TOKEN = CONFIG['airtable']['token']
AIRTABLE_BASE_ID = CONFIG['airtable']['base_id']

HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_TOKEN}',
    'Content-Type': 'application/json',
}


def list_tables():
    """List all tables in the base."""
    url = f'https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    tables = data.get('tables', [])
    return tables


def fetch_table_records(table_name, view=None):
    """Fetch all records from a table (handles pagination)."""
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}'
    all_records = []
    offset = None

    while True:
        params = {}
        if offset:
            params['offset'] = offset
        if view:
            params['view'] = view

        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()

        all_records.extend(data.get('records', []))
        offset = data.get('offset')
        if not offset:
            break

    return all_records


def fetch_table_data(table_name, output_path=None):
    """
    Fetch all records from a table and optionally save to JSON.
    Returns the records list.
    """
    records = fetch_table_records(table_name)

    # Simplify: extract just the fields from each record
    simplified = []
    for rec in records:
        entry = {'id': rec['id']}
        entry.update(rec.get('fields', {}))
        simplified.append(entry)

    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(simplified, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Saved {len(simplified)} records → {output_path}")

    return simplified


def test_connection():
    """Test the Airtable connection and list all tables."""
    print("Testing Airtable API connection...\n")
    try:
        tables = list_tables()
        print(f"✅ Connected to base: {AIRTABLE_BASE_ID}")
        print(f"   Found {len(tables)} tables:\n")

        for t in tables:
            name = t.get('name', '?')
            fields = t.get('fields', [])
            field_names = [f.get('name', '?') for f in fields]
            print(f"   📊 {name}")
            print(f"      Fields: {', '.join(field_names)}")
            print()

        print("✅ All Airtable connections working!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    if '--test' in sys.argv:
        test_connection()
    elif '--all' in sys.argv:
        output_dir = sys.argv[sys.argv.index('--all') + 1] if len(sys.argv) > sys.argv.index('--all') + 1 else '.'
        tables = list_tables()
        for t in tables:
            name = t['name']
            path = os.path.join(output_dir, f'airtable_{name}.json')
            fetch_table_data(name, path)
    elif len(sys.argv) >= 2:
        table_name = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else f'airtable_{table_name}.json'
        fetch_table_data(table_name, output)
    else:
        print("Usage:")
        print("  python3 fetch_airtable.py --test")
        print("  python3 fetch_airtable.py <table_name> [output.json]")
        print("  python3 fetch_airtable.py --all [output_dir]")
