#!/usr/bin/env python3
"""
export_primer_genbank.py — Generate annotated GenBank files for all primers.

Exports:
  - Per-tile primer .gb files (amplification + mutagenic primers)
  - Per-group primer .gb files (all primers for all tiles in the group)
  - Combined all_primers.gb

Each primer is a short linear DNA record with annotations for:
  - Primer type (amplification_fwd/rev, mutagenic_fwd/rev, subfragment_fwd/rev)
  - Tm
  - Associated tile and gene
"""

import csv, os, json
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation

# ── Paths ──────────────────────────────────────────────────────────────
TILES_CSV       = 'data/v2_tiles.csv'
DOMEST_CSV      = 'data/domestication_primers.csv'
DOMEST_SF_CSV   = 'data/domestication_subfragments.csv'
OUT_DIR         = 'data/genbank_primers'
OUT_BY_TILE     = os.path.join(OUT_DIR, 'by_tile')
OUT_BY_GROUP    = os.path.join(OUT_DIR, 'by_group')

os.makedirs(OUT_BY_TILE, exist_ok=True)
os.makedirs(OUT_BY_GROUP, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────

tiles = []
with open(TILES_CSV) as f:
    for row in csv.DictReader(f):
        tiles.append(row)
print(f"Loaded {len(tiles)} tiles")

# Domestication mutagenic primers
dom_primers = {}  # tile_id -> list of rows
with open(DOMEST_CSV) as f:
    for row in csv.DictReader(f):
        tid = int(row['tile'])
        dom_primers.setdefault(tid, []).append(row)

# Domestication subfragment primers
dom_subfragments = {}  # tile_id -> list of rows
if os.path.exists(DOMEST_SF_CSV):
    with open(DOMEST_SF_CSV) as f:
        for row in csv.DictReader(f):
            tid = int(row['tile'])
            dom_subfragments.setdefault(tid, []).append(row)

print(f"Loaded domestication data for {len(dom_primers)} tiles, subfragments for {len(dom_subfragments)} tiles")


def make_primer_record(name, seq, primer_type, direction, tm, tile_id, gene=None, note=None):
    """Create a SeqRecord for a single primer."""
    desc_parts = [
        f"Tile {tile_id}",
        primer_type,
        direction,
        f"Tm={tm}°C",
    ]
    if gene:
        desc_parts.append(f"gene={gene}")
    if note:
        desc_parts.append(note)

    rec = SeqRecord(
        Seq(seq),
        id=name,
        name=name,
        description=' | '.join(desc_parts),
        annotations={
            'molecule_type': 'DNA',
            'topology': 'linear',
        },
    )

    # Add primer feature spanning full length
    feat = SeqFeature(
        FeatureLocation(0, len(seq)),
        type='primer_bind',
        qualifiers={
            'label': [name],
            'note': [f"{primer_type} {direction}"],
            'tile': [str(tile_id)],
        },
    )
    if tm:
        feat.qualifiers['melting_temperature'] = [str(tm)]
    if gene:
        feat.qualifiers['gene'] = [gene]
    rec.features.append(feat)

    return rec


def get_tile_primers(tile):
    """Get all primer records for a given tile."""
    tid = int(tile['id'])
    records = []

    # Amplification primers
    records.append(make_primer_record(
        name=f"T{tid}_amp_fwd",
        seq=tile['fwd_primer'],
        primer_type='amplification',
        direction='forward',
        tm=tile['fwd_tm'],
        tile_id=tid,
    ))
    records.append(make_primer_record(
        name=f"T{tid}_amp_rev",
        seq=tile['rev_primer'],
        primer_type='amplification',
        direction='reverse',
        tm=tile['rev_tm'],
        tile_id=tid,
    ))

    # Mutagenic primers (for BsaI domestication)
    if tid in dom_primers:
        for i, dp in enumerate(dom_primers[tid]):
            site_pos = dp['site_genome_pos']
            gene = dp.get('gene', '')
            records.append(make_primer_record(
                name=f"T{tid}_mut{i}_fwd",
                seq=dp['mutagenic_fwd'],
                primer_type='mutagenic',
                direction='forward',
                tm=dp['fwd_tm'],
                tile_id=tid,
                gene=gene,
                note=f"BsaI site at {site_pos}",
            ))
            records.append(make_primer_record(
                name=f"T{tid}_mut{i}_rev",
                seq=dp['mutagenic_rev'],
                primer_type='mutagenic',
                direction='reverse',
                tm=dp['rev_tm'],
                tile_id=tid,
                gene=gene,
                note=f"BsaI site at {site_pos}",
            ))

    # Subfragment primers
    if tid in dom_subfragments:
        for sf in dom_subfragments[tid]:
            sf_idx = sf.get('subfragment_index', sf.get('index', '?'))
            records.append(make_primer_record(
                name=f"T{tid}_sf{sf_idx}_fwd",
                seq=sf['fwd_primer'],
                primer_type='subfragment',
                direction='forward',
                tm=sf['fwd_tm'],
                tile_id=tid,
                note=f"Subfragment {sf_idx}",
            ))
            records.append(make_primer_record(
                name=f"T{tid}_sf{sf_idx}_rev",
                seq=sf['rev_primer'],
                primer_type='subfragment',
                direction='reverse',
                tm=sf['rev_tm'],
                tile_id=tid,
                note=f"Subfragment {sf_idx}",
            ))

    return records


# ── Generate per-tile primer files ─────────────────────────────────────

from Bio import SeqIO

all_records = []
groups = {}  # group_id -> list of records

for tile in tiles:
    tid = int(tile['id'])
    gid = int(tile['lvl1_group'])
    
    records = get_tile_primers(tile)
    all_records.extend(records)
    groups.setdefault(gid, []).extend(records)

    # Write per-tile file
    out_path = os.path.join(OUT_BY_TILE, f'tile_{tid:03d}_primers.gb')
    with open(out_path, 'w') as f:
        SeqIO.write(records, f, 'genbank')

print(f"Generated {len(tiles)} per-tile primer GenBank files in {OUT_BY_TILE}/")

# ── Generate per-group primer files ────────────────────────────────────

for gid, records in sorted(groups.items()):
    out_path = os.path.join(OUT_BY_GROUP, f'group_{gid:03d}_primers.gb')
    with open(out_path, 'w') as f:
        SeqIO.write(records, f, 'genbank')

print(f"Generated {len(groups)} per-group primer GenBank files in {OUT_BY_GROUP}/")

# ── Combined file ──────────────────────────────────────────────────────

combined_path = os.path.join(OUT_DIR, 'all_primers.gb')
with open(combined_path, 'w') as f:
    SeqIO.write(all_records, f, 'genbank')

print(f"\nTotal primer records: {len(all_records)}")
print(f"Combined file: {combined_path}")
print("Done!")
