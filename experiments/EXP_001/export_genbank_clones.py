#!/usr/bin/env python3
"""
Export annotated GenBank files for all 686 Lvl0 MoClo clones.

Each clone = pICH41308 backbone + BsaI-mediated ligation of [OH_L—Insert—OH_R]
Domestication mutations are applied to the insert sequence.
CDS features from MG1655 are transferred and clipped to insert boundaries.

Usage:
    cd experiments/EXP_001
    python3 export_genbank_clones.py
"""

import csv, os, sys
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation

# ── Configuration ──────────────────────────────────────────────────────────────

GENOME_GB = 'data/MG1655.gb'
TILES_CSV = 'data/v2_tiles.csv'
DOMEST_CSV = 'data/domestication_primers.csv'
BACKBONE_GB = 'moclo-viewer-v3/data/addgene-plasmid-47998-sequence-68998.gbk'
OUTPUT_DIR = 'data/genbank_clones'

# BsaI cuts 1nt downstream on fwd strand, 5nt downstream on rev strand
# Recognition: GGTCTC(N)1^ on fwd, complement cuts 5nt before on rev
BSAI_FWD = 'GGTCTC'
BSAI_REV = 'GAGACC'


def load_backbone():
    """Load pICH41308 and extract the backbone fragment (between BsaI cut points)."""
    rec = SeqIO.read(BACKBONE_GB, 'genbank')
    seq = str(rec.seq).upper()

    # Find BsaI sites
    fwd_pos = seq.find(BSAI_FWD)  # 2224
    rev_pos = seq.find(BSAI_REV)  # 2834

    # BsaI-HFv2 cuts: fwd strand 1nt after recognition (pos+7), rev 5nt before (pos-1)
    # For fwd site GGTCTC at 2224: cut at 2224+6+1 = 2231 (after the N spacer)
    # For rev site GAGACC at 2834: the fwd cut is at 2834-1 = 2833
    # But in the circular plasmid, the backbone fragment is from rev_cut to fwd_cut
    # going through the origin.

    # The BsaI fwd site at 2224: GGTCTC N^NNNN — cut at 2231, leaving 4nt overhang 2231-2235
    fwd_cut = fwd_pos + 7  # position after the cut (start of overhang)

    # The BsaI rev site (GAGACC) at 2834: on the bottom strand this is GGTCTC
    # Cut occurs 1nt after recognition on the fwd strand = 2834 + 6 - 1 = 2840... 
    # Actually for the reverse complement site:
    # GAGACC at pos 2834 means complement GGTCTC is on bottom strand
    # Bottom strand reads 3'->5': at positions 2839..2834 = CTCTGG, complement = GAGACC
    # BsaI recognizes GGTCTC on bottom strand at positions 2834-2839
    # Cuts: bottom strand 1nt after recognition = before pos 2833
    # Top strand: 5nt after recognition end = after pos 2840
    # So: top strand cut at 2840, bottom strand cut at 2833
    # Overhang on top strand: positions 2834-2837 (4nt, reading bottom strand)
    rev_cut = rev_pos  # position where the bottom strand cuts (start of overhang region)

    # Backbone = from after rev BsaI cut through origin to before fwd BsaI cut
    # In the circular plasmid: rev_cut -> end -> 0 -> fwd_cut
    # This gives us the non-insert portion
    backbone_seq = seq[rev_cut:] + seq[:fwd_cut]

    # Collect backbone features, adjusting coordinates
    backbone_features = []
    plasmid_len = len(seq)
    for f in rec.features:
        if f.type == 'source':
            continue
        start = int(f.location.start)
        end = int(f.location.end)
        # Only keep features within the backbone region
        if start >= rev_cut or end <= fwd_cut:
            # Adjust coordinates
            if start >= rev_cut:
                new_start = start - rev_cut
                new_end = end - rev_cut
                if end > plasmid_len:
                    new_end = end - rev_cut
            else:
                new_start = (plasmid_len - rev_cut) + start
                new_end = (plasmid_len - rev_cut) + end

            if 0 <= new_start < len(backbone_seq) and new_end <= len(backbone_seq):
                new_f = SeqFeature(
                    FeatureLocation(new_start, new_end, strand=f.location.strand),
                    type=f.type,
                    qualifiers=dict(f.qualifiers),
                )
                backbone_features.append(new_f)

    print(f"  Backbone: {len(backbone_seq)} bp (from pICH41308, {len(backbone_features)} features)")
    return backbone_seq, backbone_features


def load_genome():
    """Load MG1655 genome sequence and CDS features."""
    rec = SeqIO.read(GENOME_GB, 'genbank')
    seq = str(rec.seq).upper()

    # Extract CDS features with gene names and products
    cds_features = []
    for f in rec.features:
        if f.type in ('CDS', 'gene'):
            gene = f.qualifiers.get('gene', [''])[0]
            product = f.qualifiers.get('product', [''])[0]
            cds_features.append({
                'type': f.type,
                'start': int(f.location.start),
                'end': int(f.location.end),
                'strand': f.location.strand,
                'gene': gene,
                'product': product,
            })

    print(f"  Genome: {len(seq)} bp, {len(cds_features)} gene/CDS features")
    return seq, cds_features


def load_tiles():
    """Load v2 tiles from CSV."""
    tiles = []
    with open(TILES_CSV) as f:
        for row in csv.DictReader(f):
            tiles.append({
                'id': int(row['id']),
                'start': int(row['start']),
                'end': int(row['end']),
                'length': int(row['length']),
                'lvl1_group': int(row['lvl1_group']),
                'position': int(row['position']),
                'overhang_left': row['overhang_left'],
                'overhang_right': row['overhang_right'],
                'fwd_primer': row['fwd_primer'],
                'rev_primer': row['rev_primer'],
                'internal_bsai': int(row['internal_bsai']),
                'gg_ready': row['gg_ready'] == 'True',
                'gc_content': float(row['gc_content']),
            })
    print(f"  Tiles: {len(tiles)}")
    return tiles


def load_domestication_mutations():
    """Load domestication mutations, indexed by tile ID."""
    mutations = {}  # tile_id -> list of mutations
    with open(DOMEST_CSV) as f:
        for row in csv.DictReader(f):
            tile_id = int(row['tile'])
            if tile_id not in mutations:
                mutations[tile_id] = []
            mutations[tile_id].append({
                'site_genome_pos': int(row['site_genome_pos']),
                'original_nt': row['original_nt'],
                'mutant_nt': row['mutant_nt'],
                'codon_change': row['codon_change'],
                'amino_acid': row['amino_acid'],
                'gene': row['gene'],
            })
    total = sum(len(v) for v in mutations.values())
    print(f"  Domestication mutations: {total} across {len(mutations)} tiles")
    return mutations


def apply_mutations(genome_seq, tile_start, tile_end, mutations):
    """Apply domestication mutations to a tile's insert sequence."""
    insert = list(genome_seq[tile_start:tile_end])
    applied = 0
    for mut in mutations:
        genome_pos = mut['site_genome_pos']
        if tile_start <= genome_pos < tile_end:
            local_pos = genome_pos - tile_start + 2  # +2 because mutation is at 3rd nt of recognition site
            if 0 <= local_pos < len(insert):
                if insert[local_pos] == mut['original_nt']:
                    insert[local_pos] = mut['mutant_nt']
                    applied += 1
    return ''.join(insert), applied


def build_clone(tile, genome_seq, cds_features, mutations, backbone_seq, backbone_features):
    """Build a complete annotated Lvl0 clone GenBank record."""

    # 1. Get insert sequence (with mutations if needed)
    tile_muts = mutations.get(tile['id'], [])
    if tile_muts:
        insert_seq, n_applied = apply_mutations(
            genome_seq, tile['start'], tile['end'], tile_muts
        )
    else:
        insert_seq = genome_seq[tile['start']:tile['end']]
        n_applied = 0

    # 2. Construct full plasmid: backbone + OH_L + insert + OH_R
    oh_l = tile['overhang_left']
    oh_r = tile['overhang_right']
    full_seq = backbone_seq + oh_l + insert_seq + oh_r

    # 3. Create SeqRecord
    tile_label = f"tile_{tile['id']:03d}"
    bsai_count = tile['internal_bsai']
    status = 'GG-Ready' if tile['gg_ready'] else f'{bsai_count} BsaI sites domesticated'
    rec = SeqRecord(
        Seq(full_seq),
        id=tile_label,
        name=tile_label,
        description=(
            f"Lvl0 MoClo clone | Tile {tile['id']} | "
            f"Group {tile['lvl1_group']} Pos {tile['position']} | "
            f"E. coli MG1655 {tile['start']:,}-{tile['end']:,} | "
            f"{status}"
        ),
        annotations={
            'molecule_type': 'DNA',
            'topology': 'circular',
            'organism': 'synthetic construct',
        },
    )

    bb_len = len(backbone_seq)
    oh_l_len = len(oh_l)
    insert_len = len(insert_seq)
    oh_r_len = len(oh_r)

    # 4. Add backbone features (already position-adjusted)
    for bf in backbone_features:
        rec.features.append(SeqFeature(
            FeatureLocation(
                int(bf.location.start),
                int(bf.location.end),
                strand=bf.location.strand
            ),
            type=bf.type,
            qualifiers=dict(bf.qualifiers),
        ))

    # 5. Add overhang features
    rec.features.append(SeqFeature(
        FeatureLocation(bb_len, bb_len + oh_l_len, strand=1),
        type='misc_feature',
        qualifiers={'label': [f'OH_L ({oh_l})'], 'note': ['Left overhang (standardized fusion site)']},
    ))
    rec.features.append(SeqFeature(
        FeatureLocation(bb_len + oh_l_len + insert_len, bb_len + oh_l_len + insert_len + oh_r_len, strand=1),
        type='misc_feature',
        qualifiers={'label': [f'OH_R ({oh_r})'], 'note': ['Right overhang (standardized fusion site)']},
    ))

    # 6. Add genomic insert feature
    insert_start_in_plasmid = bb_len + oh_l_len
    rec.features.append(SeqFeature(
        FeatureLocation(insert_start_in_plasmid, insert_start_in_plasmid + insert_len, strand=1),
        type='misc_feature',
        qualifiers={
            'label': [f'Tile {tile["id"]} insert'],
            'note': [f'E. coli MG1655 {tile["start"]:,}-{tile["end"]:,} ({tile["length"]:,} bp)'],
        },
    ))

    # 7. Transfer CDS/gene features from genome (clipped to insert)
    for cds in cds_features:
        # Check overlap with tile
        cds_start = max(cds['start'], tile['start'])
        cds_end = min(cds['end'], tile['end'])
        if cds_start >= cds_end:
            continue  # no overlap

        # Map to plasmid coordinates
        plasmid_start = insert_start_in_plasmid + (cds_start - tile['start'])
        plasmid_end = insert_start_in_plasmid + (cds_end - tile['start'])

        qualifiers = {}
        if cds['gene']:
            qualifiers['gene'] = [cds['gene']]
            qualifiers['label'] = [cds['gene']]
        if cds['product']:
            qualifiers['product'] = [cds['product']]

        # Mark if truncated
        if cds_start > cds['start'] or cds_end < cds['end']:
            qualifiers['note'] = [f'Truncated (genome {cds["start"]:,}-{cds["end"]:,})']

        rec.features.append(SeqFeature(
            FeatureLocation(plasmid_start, plasmid_end, strand=cds['strand']),
            type=cds['type'],
            qualifiers=qualifiers,
        ))

    # 8. Add domestication mutation features
    for mut in tile_muts:
        genome_pos = mut['site_genome_pos']
        if tile['start'] <= genome_pos < tile['end']:
            local_pos = genome_pos - tile['start'] + 2
            plasmid_pos = insert_start_in_plasmid + local_pos
            rec.features.append(SeqFeature(
                FeatureLocation(plasmid_pos, plasmid_pos + 1, strand=1),
                type='misc_feature',
                qualifiers={
                    'label': [f'Domestication {mut["original_nt"]}→{mut["mutant_nt"]}'],
                    'note': [
                        f'BsaI site removal | {mut["codon_change"]} | '
                        f'AA: {mut["amino_acid"]} | Gene: {mut["gene"]} | '
                        f'Genome pos: {genome_pos:,}'
                    ],
                    'ApEinfo_fwdcolor': ['#ff6b6b'],
                    'ApEinfo_revcolor': ['#ff6b6b'],
                },
            ))

    return rec, n_applied


def main():
    print("=" * 70)
    print("Lvl0 Clone GenBank Export")
    print("=" * 70)

    # Load data
    print("\n[1/3] Loading data...")
    backbone_seq, backbone_features = load_backbone()
    genome_seq, cds_features = load_genome()
    tiles = load_tiles()
    mutations = load_domestication_mutations()

    # Build clones
    print(f"\n[2/3] Building {len(tiles)} annotated clones...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_records = []
    summary_rows = []
    total_mutations_applied = 0

    for i, tile in enumerate(tiles):
        rec, n_muts = build_clone(
            tile, genome_seq, cds_features, mutations,
            backbone_seq, backbone_features
        )
        all_records.append(rec)
        total_mutations_applied += n_muts

        # Write individual file
        out_path = os.path.join(OUTPUT_DIR, f"tile_{tile['id']:03d}.gb")
        SeqIO.write(rec, out_path, 'genbank')

        # Summary
        n_features = len(rec.features)
        n_cds = sum(1 for f in rec.features if f.type == 'CDS')
        n_genes = sum(1 for f in rec.features if f.type == 'gene')
        summary_rows.append({
            'tile_id': tile['id'],
            'plasmid_length': len(rec.seq),
            'insert_length': tile['length'],
            'lvl1_group': tile['lvl1_group'],
            'position': tile['position'],
            'gg_ready': tile['gg_ready'],
            'domestication_mutations': n_muts,
            'cds_features': n_cds,
            'gene_features': n_genes,
            'total_features': n_features,
            'file': f"tile_{tile['id']:03d}.gb",
        })

        if (i + 1) % 100 == 0:
            print(f"    {i + 1}/{len(tiles)} clones exported...")

    # Write concatenated multi-record file
    print(f"\n[3/3] Writing output files...")
    all_path = os.path.join(OUTPUT_DIR, 'all_clones.gb')
    SeqIO.write(all_records, all_path, 'genbank')
    print(f"  {all_path} ({len(all_records)} records)")

    # Write summary CSV
    summary_path = os.path.join(OUTPUT_DIR, 'clone_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"  {summary_path}")

    # Stats
    print(f"\n{'=' * 70}")
    print(f"EXPORT SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total clones:            {len(all_records)}")
    print(f"  GG-ready (no mutations): {sum(1 for r in summary_rows if r['gg_ready'])}")
    print(f"  Domesticated:            {sum(1 for r in summary_rows if r['domestication_mutations'] > 0)}")
    print(f"  Total mutations applied: {total_mutations_applied}")
    avg_len = sum(r['plasmid_length'] for r in summary_rows) / len(summary_rows)
    print(f"  Average plasmid size:    {avg_len:,.0f} bp")
    avg_features = sum(r['total_features'] for r in summary_rows) / len(summary_rows)
    print(f"  Average features/clone:  {avg_features:.1f}")
    print(f"  Output directory:        {OUTPUT_DIR}/")
    print(f"  Individual files:        tile_000.gb — tile_{len(tiles)-1:03d}.gb")
    print(f"  Combined file:           all_clones.gb")


if __name__ == '__main__':
    main()
