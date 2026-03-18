# Knowledge Base Guide — Diploid E. coli

> This guide defines the structure, templates, and rules for this project's knowledge base.

## Directory Structure

```
projects/diploid_ecoli/knowledge/
├── GUIDE.md              ← This file
├── structure.md          ← System architecture + topology
├── hardware.md           ← Device inventory + wiring
├── software.md           ← Dashboards, analysis tools
├── firmware/             ← Per-device firmware docs
├── api/                  ← Per-service API docs
└── images/               ← Embedded screenshots
```

## When to Update

Update the knowledge base when you:

- Add, remove, or modify a physical device → `hardware.md`
- Write or change firmware → `firmware/<device>.md`
- Add or change API endpoints → `api/<service>.md`
- Change network config, IPs, or deployment → `structure.md` or `software.md`
- Add a new knowledge base file → update `nav.yaml`

## Templates

### Firmware Doc Template

```markdown
# DEVICE_ID — Description

| Field | Value |
|-------|-------|
| **Device ID** | `DEVICE_ID` |
| **MCU** | ... |
| **Function** | ... |
| **Source** | `experiments/EXP_XXX/firmware/` |

## Pin Map
## Communication Protocol
## Build & Flash
## Changelog
```

### API Doc Template

```markdown
# Service Name API

| Field | Value |
|-------|-------|
| **Base URL** | `http://...` |
| **Framework** | ... |
| **Source** | `experiments/EXP_XXX/firmware/` |

## Endpoints
## Code Examples
```
