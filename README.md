# PhD Lab

AI-assisted lab workspace for the PhD project. Integrates with Notion (lab notebook + bibliography) and Airtable (reagents & labware inventory).

## Setup

### 1. Credentials

All credentials are stored in **`config.yaml`** (gitignored). Edit it with your Notion and Airtable tokens:

- **Notion Integration Token** — from [notion.so/my-integrations](https://www.notion.so/my-integrations)
- **Notion Database IDs** — Lab Notebook + Bibliography (32-char IDs from the database URLs)
- **Airtable Token** — from [airtable.com/create/tokens](https://airtable.com/create/tokens)
- **Airtable Base ID** — from the Airtable URL (`appXXXXXXXX`)

### 2. Share Notion Integration

Make sure the Notion integration is connected to both databases:
1. Open each database in Notion
2. Click "..." → "Connections" → Add your integration

### 3. Python Dependencies

```bash
pip3 install requests pyyaml pymupdf
```

### 4. Verify

```bash
python3 scripts/notion_client.py --test
```

## Usage

### Sync Bibliography (new papers)
```bash
python3 scripts/sync_bibliography.py        # Download new papers
python3 scripts/sync_bibliography.py --list  # List all papers
```

### Sync Experiments (new entries)
```bash
python3 scripts/sync_experiments.py          # Sync new experiments
python3 scripts/sync_experiments.py --list   # List all experiments
python3 scripts/sync_experiments.py --force  # Re-sync all
```

### AI Assistant Workflows

When working with the AI assistant, use these commands:
- **`/catch-up`** — Sync everything and report what's new
- **`/sync-bibliography`** — Sync bibliography only
- **`/sync-experiments`** — Sync experiments only
- **`/update-experiment`** — Log findings to an experiment

## Project Structure

```
PhD/
├── .agent/                    # AI assistant config
│   ├── MANIFEST.md            # Project memory
│   └── workflows/             # Slash-command workflows
├── config.yaml                # API credentials (gitignored)
├── scripts/                   # Python sync scripts
├── papers/                    # Downloaded reference PDFs
├── papers_txt/                # Plain-text extracts
│   └── INDEX.md               # Paper index for AI lookup
├── experiments/               # Per-experiment folders
│   └── EXP_INDEX.md           # Experiment index for AI lookup
├── applications/              # Lab web applications
└── README.md                  # This file
```
