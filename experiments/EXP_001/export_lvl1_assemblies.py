#!/usr/bin/env python3
"""
Export annotated GenBank files for all 46 Lvl1 MoClo assemblies.

Each Lvl1 = BsaI Golden Gate assembly of 15 Lvl0 tiles (from their pICH41308 backbones)
into a single ~100 kb construct. Tiles are joined at standardized 4-nt overhangs.

The script produces the theoretical assembly product: the concatenated tile inserts
with all CDS/gene features transferred from the MG1655 genome.

Usage:
    cd experiments/EXP_001
    python3 export_lvl1_assemblies.py
"""

import csv, os
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation

# ── Configuration ──────────────────────────────────────────────────────────────

GENOME_GB = 'data/MG1655.gb'
TILES_CSV = 'data/v2_tiles.csv'
GROUPS_CSV = 'data/v2_lvl1_groups.csv'
DOMEST_CSV = 'data/domestication_primers.csv'
LVL0_DIR = 'data/genbank_clones'
OUTPUT_DIR = 'data/genbank_lvl1'

BSAI_FWD = 'GGTCTC'
BSAI_REV = 'GAGACC'


def load_genome():
    """Load MG1655 genome sequence and CDS/gene features."""
    rec = SeqIO.read(GENOME_GB, 'genbank')
    seq = str(rec.seq).upper()

    features = []
    for f in rec.features:
        if f.type in ('CDS', 'gene'):
            gene = f.qualifiers.get('gene', [''])[0]
            product = f.qualifiers.get('product', [''])[0]
            features.append({
                'type': f.type,
                'start': int(f.location.start),
                'end': int(f.location.end),
                'strand': f.location.strand,
                'gene': gene,
                'product': product,
            })

    print(f"  Genome: {len(seq)} bp, {len(features)} gene/CDS features")
    return seq, features


def load_tiles():
    """Load v2 tiles from CSV, grouped by Lvl1 group."""
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
                'internal_bsai': int(row['internal_bsai']),
                'gg_ready': row['gg_ready'] == 'True',
            })

    # Group by Lvl1 group
    groups = {}
    for t in tiles:
        gid = t['lvl1_group']
        if gid not in groups:
            groups[gid] = []
        groups[gid].append(t)

    # Sort tiles within each group by position
    for gid in groups:
        groups[gid].sort(key=lambda t: t['position'])

    print(f"  Tiles: {len(tiles)} in {len(groups)} Lvl1 groups")
    return tiles, groups


def load_domestication_mutations():
    """Load domestication mutations indexed by tile ID."""
    mutations = {}
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
    print(f"  Domestication mutations: {total}")
    return mutations


def apply_mutations(genome_seq, tile_start, tile_end, mutations):
    """Apply domestication mutations to a tile's insert sequence."""
    insert = list(genome_seq[tile_start:tile_end])
    for mut in mutations:
        genome_pos = mut['site_genome_pos']
        if tile_start <= genome_pos < tile_end:
            local_pos = genome_pos - tile_start + 2
            if 0 <= local_pos < len(insert):
                if insert[local_pos] == mut['original_nt']:
                    insert[local_pos] = mut['mutant_nt']
    return ''.join(insert)


def build_lvl1_assembly(group_id, group_tiles, genome_seq, cds_features, mutations):
    """Build a Lvl1 assembly: concatenation of all tile inserts joined by overhangs."""

    # Assembly sequence: OH_L_tile0 + insert_0 + OH_R_tile0(=OH_L_tile1) + insert_1 + ...
    # In Golden Gate, the overhangs are the junction — each is 4 nt shared between adjacent tiles
    assembly_seq = ''
    tile_boundaries = []  # (assembly_start, assembly_end, tile_id, genome_start, genome_end)
    overhang_positions = []  # (assembly_pos, overhang_seq)

    for i, tile in enumerate(group_tiles):
        tile_muts = mutations.get(tile['id'], [])

        # Add left overhang (only for the first tile — subsequent ones are shared junctions)
        if i == 0:
            oh = tile['overhang_left']
            overhang_positions.append((len(assembly_seq), oh, 'left-terminal'))
            assembly_seq += oh

        # Add insert (with domestication mutations)
        insert_start = len(assembly_seq)
        if tile_muts:
            insert_seq = apply_mutations(genome_seq, tile['start'], tile['end'], tile_muts)
        else:
            insert_seq = genome_seq[tile['start']:tile['end']]
        assembly_seq += insert_seq
        insert_end = len(assembly_seq)

        tile_boundaries.append((insert_start, insert_end, tile['id'], tile['start'], tile['end']))

        # Add right overhang / junction
        oh = tile['overhang_right']
        junction_type = 'right-terminal' if i == len(group_tiles) - 1 else f'junction T{tile["position"]}→T{group_tiles[i+1]["position"]}'
        overhang_positions.append((len(assembly_seq), oh, junction_type))
        assembly_seq += oh

    # Create SeqRecord
    g_start = group_tiles[0]['start']
    g_end = group_tiles[-1]['end']
    n_tiles = len(group_tiles)

    rec = SeqRecord(
        Seq(assembly_seq),
        id=f"lvl1_group_{group_id:03d}",
        name=f"lvl1_g{group_id:03d}",
        description=(
            f"Lvl1 MoClo assembly | Group {group_id} | "
            f"{n_tiles} tiles | "
            f"E. coli MG1655 {g_start:,}-{g_end:,} | "
            f"{len(assembly_seq):,} bp"
        ),
        annotations={
            'molecule_type': 'DNA',
            'topology': 'circular',
            'organism': 'synthetic construct',
        },
    )

    # Add tile insert features
    for (asm_start, asm_end, tile_id, gen_start, gen_end) in tile_boundaries:
        rec.features.append(SeqFeature(
            FeatureLocation(asm_start, asm_end, strand=1),
            type='misc_feature',
            qualifiers={
                'label': [f'Tile {tile_id}'],
                'note': [f'Genome {gen_start:,}-{gen_end:,} ({gen_end - gen_start:,} bp)'],
                'ApEinfo_fwdcolor': ['#b3e6b3'],
                'ApEinfo_revcolor': ['#b3e6b3'],
            },
        ))

    # Add overhang/junction features
    for (asm_pos, oh_seq, oh_type) in overhang_positions:
        rec.features.append(SeqFeature(
            FeatureLocation(asm_pos, asm_pos + 4, strand=1),
            type='misc_feature',
            qualifiers={
                'label': [f'OH {oh_seq}'],
                'note': [f'Standardized overhang ({oh_type})'],
                'ApEinfo_fwdcolor': ['#ffcc66'],
                'ApEinfo_revcolor': ['#ffcc66'],
            },
        ))

    # Transfer CDS/gene features from genome
    for cds in cds_features:
        # Check each tile boundary for overlap
        for (asm_start, asm_end, tile_id, gen_start, gen_end) in tile_boundaries:
            cds_clip_start = max(cds['start'], gen_start)
            cds_clip_end = min(cds['end'], gen_end)
            if cds_clip_start >= cds_clip_end:
                continue

            # Map to assembly coordinates
            offset = cds_clip_start - gen_start
            length = cds_clip_end - cds_clip_start
            plasmid_start = asm_start + offset
            plasmid_end = plasmid_start + length

            qualifiers = {}
            if cds['gene']:
                qualifiers['gene'] = [cds['gene']]
                qualifiers['label'] = [cds['gene']]
            if cds['product']:
                qualifiers['product'] = [cds['product']]
            if cds_clip_start > cds['start'] or cds_clip_end < cds['end']:
                qualifiers['note'] = [f'Truncated (genome {cds["start"]:,}-{cds["end"]:,})']

            rec.features.append(SeqFeature(
                FeatureLocation(plasmid_start, plasmid_end, strand=cds['strand']),
                type=cds['type'],
                qualifiers=qualifiers,
            ))

    # Add domestication mutation features
    for (asm_start, asm_end, tile_id, gen_start, gen_end) in tile_boundaries:
        tile_muts = mutations.get(tile_id, [])
        for mut in tile_muts:
            genome_pos = mut['site_genome_pos']
            if gen_start <= genome_pos < gen_end:
                local_pos = genome_pos - gen_start + 2
                plasmid_pos = asm_start + local_pos
                rec.features.append(SeqFeature(
                    FeatureLocation(plasmid_pos, plasmid_pos + 1, strand=1),
                    type='misc_feature',
                    qualifiers={
                        'label': [f'Dom {mut["original_nt"]}→{mut["mutant_nt"]}'],
                        'note': [
                            f'BsaI domestication | {mut["codon_change"]} | '
                            f'Gene: {mut["gene"]} | Genome: {genome_pos:,}'
                        ],
                        'ApEinfo_fwdcolor': ['#ff6b6b'],
                        'ApEinfo_revcolor': ['#ff6b6b'],
                    },
                ))

    return rec


def main():
    print("=" * 70)
    print("Lvl1 Assembly GenBank Export")
    print("=" * 70)

    print("\n[1/3] Loading data...")
    genome_seq, cds_features = load_genome()
    tiles, groups = load_tiles()
    mutations = load_domestication_mutations()

    print(f"\n[2/3] Building {len(groups)} Lvl1 assemblies...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_records = []
    summary_rows = []

    for group_id in sorted(groups.keys()):
        group_tiles = groups[group_id]
        rec = build_lvl1_assembly(group_id, group_tiles, genome_seq, cds_features, mutations)
        all_records.append(rec)

        # Write individual file
        out_path = os.path.join(OUTPUT_DIR, f"lvl1_group_{group_id:03d}.gb")
        SeqIO.write(rec, out_path, 'genbank')

        n_cds = sum(1 for f in rec.features if f.type == 'CDS')
        n_genes = sum(1 for f in rec.features if f.type == 'gene')
        n_dom = sum(1 for f in rec.features if 'Dom' in str(f.qualifiers.get('label', '')))

        summary_rows.append({
            'group_id': group_id,
            'assembly_length': len(rec.seq),
            'n_tiles': len(group_tiles),
            'genome_start': group_tiles[0]['start'],
            'genome_end': group_tiles[-1]['end'],
            'cds_features': n_cds,
            'gene_features': n_genes,
            'domestication_mutations': n_dom,
            'total_features': len(rec.features),
            'file': f"lvl1_group_{group_id:03d}.gb",
        })

    # Write combined file
    print(f"\n[3/3] Writing output files...")
    all_path = os.path.join(OUTPUT_DIR, 'all_lvl1_assemblies.gb')
    SeqIO.write(all_records, all_path, 'genbank')
    print(f"  {all_path} ({len(all_records)} records)")

    # Write summary CSV
    summary_path = os.path.join(OUTPUT_DIR, 'lvl1_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"  {summary_path}")

    # Stats
    print(f"\n{'=' * 70}")
    print(f"EXPORT SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total Lvl1 assemblies:    {len(all_records)}")
    avg_len = sum(r['assembly_length'] for r in summary_rows) / len(summary_rows)
    print(f"  Average assembly size:    {avg_len/1000:,.1f} kb")
    total_cds = sum(r['cds_features'] for r in summary_rows)
    total_genes = sum(r['gene_features'] for r in summary_rows)
    print(f"  Total CDS features:       {total_cds}")
    print(f"  Total gene features:      {total_genes}")
    total_dom = sum(r['domestication_mutations'] for r in summary_rows)
    print(f"  Domestication mutations:  {total_dom}")
    print(f"  Output directory:         {OUTPUT_DIR}/")
    print(f"  Individual files:         lvl1_group_000.gb — lvl1_group_{max(groups.keys()):03d}.gb")
    print(f"  Combined file:            all_lvl1_assemblies.gb")


if __name__ == '__main__':
    main()
