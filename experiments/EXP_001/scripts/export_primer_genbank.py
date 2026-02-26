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

PRIMER_FLANK = 20  # Must match domestication_primers.py
BSAI_ADAPTER_LEN = 7  # GGTCTCN
OVERHANG_LEN = 4  # standardized 4-nt overhang


def make_primer_record(name, seq, primer_type, direction, tm, tile_id,
                       gene=None, note=None, binding_start=None, binding_end=None,
                       mutation_pos=None):
    """Create a SeqRecord for a single primer with binding/overlap annotations.

    binding_start/binding_end: 0-indexed positions of the binding region within the primer.
    Everything outside this range is annotated as overlap/adapter (non-binding tail).
    mutation_pos: position of the introduced mutation within the primer (for mutagenic only).
    """
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

    seq_len = len(seq)

    if binding_start is not None and binding_end is not None:
        # Binding region (anneals to template)
        bind_feat = SeqFeature(
            FeatureLocation(binding_start, binding_end),
            type='primer_bind',
            qualifiers={
                'label': [name],
                'note': [f"{primer_type} {direction} — binding region"],
                'tile': [str(tile_id)],
            },
        )
        if tm:
            bind_feat.qualifiers['melting_temperature'] = [str(tm)]
        if gene:
            bind_feat.qualifiers['gene'] = [gene]
        rec.features.append(bind_feat)

        # Non-binding tail (overlap / adapter)
        if binding_start > 0:
            tail_label = 'OE-PCR overlap' if primer_type == 'mutagenic' else 'BsaI adapter + overhang'
            tail_feat = SeqFeature(
                FeatureLocation(0, binding_start),
                type='misc_feature',
                qualifiers={
                    'label': [f"{name}_tail"],
                    'note': [tail_label],
                },
            )
            rec.features.append(tail_feat)

        if binding_end < seq_len:
            tail_label = 'OE-PCR overlap' if primer_type == 'mutagenic' else 'BsaI adapter + overhang'
            tail_feat = SeqFeature(
                FeatureLocation(binding_end, seq_len),
                type='misc_feature',
                qualifiers={
                    'label': [f"{name}_tail"],
                    'note': [tail_label],
                },
            )
            rec.features.append(tail_feat)

        # Mutation marker (for mutagenic primers)
        if mutation_pos is not None and 0 <= mutation_pos < seq_len:
            mut_feat = SeqFeature(
                FeatureLocation(mutation_pos, mutation_pos + 1),
                type='variation',
                qualifiers={
                    'label': ['mutation'],
                    'note': ['Introduced silent mutation for BsaI domestication'],
                },
            )
            if gene:
                mut_feat.qualifiers['gene'] = [gene]
            rec.features.append(mut_feat)
    else:
        # Fallback: annotate entire sequence as primer_bind
        feat = SeqFeature(
            FeatureLocation(0, seq_len),
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

    # Amplification primers — 5' tail is BsaI adapter (7nt) + overhang (4nt) = 11nt
    amp_fwd = tile['fwd_primer']
    amp_rev = tile['rev_primer']
    adapter_tail = BSAI_ADAPTER_LEN + OVERHANG_LEN  # 11 nt non-binding 5' tail

    records.append(make_primer_record(
        name=f"T{tid}_amp_fwd",
        seq=amp_fwd,
        primer_type='amplification',
        direction='forward',
        tm=tile['fwd_tm'],
        tile_id=tid,
        binding_start=adapter_tail,
        binding_end=len(amp_fwd),
    ))
    records.append(make_primer_record(
        name=f"T{tid}_amp_rev",
        seq=amp_rev,
        primer_type='amplification',
        direction='reverse',
        tm=tile['rev_tm'],
        tile_id=tid,
        binding_start=adapter_tail,
        binding_end=len(amp_rev),
    ))

    # Mutagenic primers (for BsaI domestication)
    # These are 41 nt centered on the mutation (pos 20).
    # FWD primer: 5' tail (0..20) = overlap, 3' (21..41) = binding
    # REV primer: 5' (0..20) = binding, 3' tail (21..41) = overlap
    if tid in dom_primers:
        for i, dp in enumerate(dom_primers[tid]):
            site_pos = dp['site_genome_pos']
            gene = dp.get('gene', '')
            fwd_seq = dp['mutagenic_fwd']
            rev_seq = dp['mutagenic_rev']
            plen = len(fwd_seq)
            mut_pos = PRIMER_FLANK  # mutation at center

            records.append(make_primer_record(
                name=f"T{tid}_mut{i}_fwd",
                seq=fwd_seq,
                primer_type='mutagenic',
                direction='forward',
                tm=dp['fwd_tm'],
                tile_id=tid,
                gene=gene,
                note=f"BsaI site at {site_pos}",
                binding_start=mut_pos + 1,  # 3' of mutation = binding
                binding_end=plen,
                mutation_pos=mut_pos,
            ))
            records.append(make_primer_record(
                name=f"T{tid}_mut{i}_rev",
                seq=rev_seq,
                primer_type='mutagenic',
                direction='reverse',
                tm=dp['rev_tm'],
                tile_id=tid,
                gene=gene,
                note=f"BsaI site at {site_pos}",
                binding_start=0,           # 5' of mutation = binding
                binding_end=mut_pos,
                mutation_pos=mut_pos,
            ))

    # Subfragment primers (these reuse tile amp primers or mutagenic primers,
    # so they have the same structure — annotate based on type)
    if tid in dom_subfragments:
        for sf in dom_subfragments[tid]:
            sf_idx = sf.get('subfragment_index', sf.get('index', '?'))
            sf_fwd = sf['fwd_primer']
            sf_rev = sf['rev_primer']

            # Subfragment fwd: if it starts with GGTCTCN it's an amplification primer reuse
            if sf_fwd[:6] == 'GGTCTC':
                bind_s, bind_e = adapter_tail, len(sf_fwd)
            else:
                # It's a mutagenic primer — binding is the 3' half
                bind_s, bind_e = PRIMER_FLANK + 1, len(sf_fwd)

            records.append(make_primer_record(
                name=f"T{tid}_sf{sf_idx}_fwd",
                seq=sf_fwd,
                primer_type='subfragment',
                direction='forward',
                tm=sf['fwd_tm'],
                tile_id=tid,
                note=f"Subfragment {sf_idx}",
                binding_start=bind_s,
                binding_end=bind_e,
            ))

            # Subfragment rev: if it starts with GGTCTCN it's an amplification primer reuse
            if sf_rev[:6] == 'GGTCTC':
                bind_s, bind_e = adapter_tail, len(sf_rev)
            else:
                # It's a mutagenic primer — binding is the 5' half
                bind_s, bind_e = 0, PRIMER_FLANK

            records.append(make_primer_record(
                name=f"T{tid}_sf{sf_idx}_rev",
                seq=sf_rev,
                primer_type='subfragment',
                direction='reverse',
                tm=sf['rev_tm'],
                tile_id=tid,
                note=f"Subfragment {sf_idx}",
                binding_start=bind_s,
                binding_end=bind_e,
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
