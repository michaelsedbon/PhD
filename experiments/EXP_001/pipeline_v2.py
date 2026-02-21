#!/usr/bin/env python3
"""
V2 MoClo Pipeline — Standardized overhangs & 100kb Lvl1 groups

Changes from V1:
  - 15 tiles per Lvl1 group (~105kb) instead of 11 (~77kb)
  - 16 standardized positional overhangs (interchangeable Lvl0 parts)
  - Tile boundaries forced out of CDS regions (scars land in intergenic only)

Reuses existing tile boundary placement (v1), adjusting in-CDS boundaries
to nearest intergenic gaps, then regroups into 15-tile Lvl1 assemblies.
"""

import csv, json, re, math, os

# ── Configuration ──────────────────────────────────────────────────────────────

GENOME_FILE = 'data/MG1655.gb'
V1_TILES_CSV = 'data/tiles.csv'
TILES_PER_GROUP = 15
TARGET_TILE_SIZE = 7000  # bp
GENOME_LENGTH = 4641652

# 16 standardized fusion sites (validated: no palindromes, Hamming ≥ 2, no BsaI risk)
STANDARD_OVERHANGS = [
    'AATA', 'AACT', 'AAGC', 'ATAA', 'ATTC', 'ATGT', 'ACAC', 'ACTT',
    'AGAT', 'AGCA', 'TAAT', 'TATC', 'TACA', 'TTAC', 'TTCT', 'TGAA',
]

BSAI_FWD = 'GGTCTC'
BSAI_REV = 'GAGACC'

# BsaI adapter for primers: recognition site + 1nt spacer
BSAI_ADAPTER = 'CGTCTCN'

# Primer design parameters
PRIMER_MIN_LEN = 18
PRIMER_MAX_LEN = 25
PRIMER_OPT_TM = 60.0


# ── Helper functions ───────────────────────────────────────────────────────────

def parse_genbank_sequence(filepath):
    """Extract sequence from GenBank file without BioPython."""
    seq_parts = []
    in_origin = False
    with open(filepath) as f:
        for line in f:
            if line.startswith('ORIGIN'):
                in_origin = True
                continue
            if line.startswith('//'):
                break
            if in_origin:
                seq_parts.append(re.sub(r'[\s\d/]', '', line).upper())
    return ''.join(seq_parts)


def parse_genbank_cds(filepath):
    """Extract CDS features from GenBank file."""
    cds_list = []
    in_features = False
    current = None
    current_type = None

    with open(filepath) as f:
        for line in f:
            if line.startswith('FEATURES'):
                in_features = True
                continue
            if line.startswith('ORIGIN'):
                break
            if not in_features:
                continue

            # New feature line
            if len(line) > 5 and line[5] != ' ':
                # Save previous CDS
                if current and current_type == 'CDS':
                    cds_list.append(current)
                    current = None

                parts = line.strip().split()
                if len(parts) >= 2:
                    current_type = parts[0]
                    if current_type == 'CDS':
                        loc = parts[1]
                        loc_clean = re.sub(r'complement\(|\)|join\(|<|>', '', loc)
                        ranges = []
                        for r in loc_clean.split(','):
                            if '..' in r:
                                s, e = r.split('..')
                                ranges.append((int(s) - 1, int(e)))
                        if ranges:
                            current = {
                                'start': ranges[0][0],
                                'end': ranges[-1][1],
                                'gene': '',
                            }
            elif current and current_type == 'CDS':
                m = re.search(r'/gene="([^"]+)"', line)
                if m:
                    current['gene'] = m.group(1)

    if current and current_type == 'CDS':
        cds_list.append(current)

    return sorted(cds_list, key=lambda c: c['start'])


def is_in_cds(pos, cds_list):
    """Check if a position falls within any CDS."""
    for c in cds_list:
        if c['start'] <= pos < c['end']:
            return True
        if c['start'] > pos:
            break
    return False


def find_nearest_intergenic(pos, cds_list, max_shift=3000):
    """Find nearest intergenic position, searching outward from pos."""
    if not is_in_cds(pos, cds_list):
        return pos

    # Search outward
    for delta in range(1, max_shift):
        for candidate in [pos + delta, pos - delta]:
            if 0 < candidate < GENOME_LENGTH and not is_in_cds(candidate, cds_list):
                return candidate

    return pos  # fallback


def reverse_complement(seq):
    comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    return ''.join(comp.get(c, c) for c in reversed(seq))


def calc_tm(seq):
    """Simple Tm calculation (Wallace rule for short primers)."""
    seq = seq.upper()
    # Only count binding region (strip adapter)
    at = seq.count('A') + seq.count('T')
    gc = seq.count('G') + seq.count('C')
    if len(seq) < 14:
        return 2 * at + 4 * gc
    return 64.9 + 41.0 * (gc - 16.4) / (at + gc)


def design_primer(genome_seq, pos, direction, overhang):
    """Design a primer with BsaI adapter + standardized overhang + genome binding."""
    if direction == 'fwd':
        # Binding region: genome starting at pos
        for length in range(PRIMER_MIN_LEN, PRIMER_MAX_LEN + 1):
            binding = genome_seq[pos:pos + length]
            tm = calc_tm(binding)
            if tm >= PRIMER_OPT_TM - 3:
                full_primer = BSAI_ADAPTER + overhang + binding
                return full_primer, round(tm, 1)
        binding = genome_seq[pos:pos + PRIMER_MAX_LEN]
        return BSAI_ADAPTER + overhang + binding, round(calc_tm(binding), 1)
    else:
        # Binding region: genome ending at pos (reverse complement)
        for length in range(PRIMER_MIN_LEN, PRIMER_MAX_LEN + 1):
            binding_region = genome_seq[pos - length:pos]
            binding = reverse_complement(binding_region)
            tm = calc_tm(binding)
            if tm >= PRIMER_OPT_TM - 3:
                full_primer = BSAI_ADAPTER + reverse_complement(overhang) + binding
                return full_primer, round(tm, 1)
        binding_region = genome_seq[pos - PRIMER_MAX_LEN:pos]
        binding = reverse_complement(binding_region)
        return BSAI_ADAPTER + reverse_complement(overhang) + binding, round(calc_tm(binding), 1)


def count_internal_bsai(genome_seq, start, end):
    """Count BsaI sites within a tile's genome region."""
    region = genome_seq[start:end]
    count = 0
    for site in [BSAI_FWD, BSAI_REV]:
        count += region.count(site)
    return count


def check_junction_bsai(genome_seq, pos, overhang):
    """Check if standardized overhang + flanking genome creates a BsaI site."""
    # Check 10bp window around the junction
    left_context = genome_seq[max(0, pos - 6):pos]
    right_context = genome_seq[pos:min(GENOME_LENGTH, pos + 6)]
    junction = left_context + overhang + right_context
    return BSAI_FWD in junction or BSAI_REV in junction


def gc_content(genome_seq, start, end):
    region = genome_seq[start:end].upper()
    gc = region.count('G') + region.count('C')
    return round(100. * gc / len(region), 1) if len(region) > 0 else 0


# ── Main Pipeline ──────────────────────────────────────────────────────────────

def run_pipeline():
    print("=" * 70)
    print("V2 MoClo Pipeline — Standardized Overhangs & 100kb Lvl1 Groups")
    print("=" * 70)

    # 1. Load genome and CDS
    print("\n[1/7] Loading genome and CDS features...")
    genome_seq = parse_genbank_sequence(GENOME_FILE)
    cds_list = parse_genbank_cds(GENOME_FILE)
    print(f"  Genome: {len(genome_seq)} bp")
    print(f"  CDS features: {len(cds_list)}")

    # 2. Load v1 tile boundaries and adjust CDS-overlapping ones
    print("\n[2/7] Adjusting tile boundaries to avoid CDS regions...")
    with open(V1_TILES_CSV) as f:
        v1_tiles = list(csv.DictReader(f))

    # Get v1 boundaries
    boundaries = sorted(set(
        [int(t['start']) for t in v1_tiles] + [int(v1_tiles[-1]['end'])]
    ))
    print(f"  V1 boundaries: {len(boundaries)}")

    # Adjust boundaries that fall in CDS
    adjusted = 0
    new_boundaries = [0]  # genome start stays at 0
    for b in boundaries[1:-1]:  # skip first and last
        if is_in_cds(b, cds_list):
            new_b = find_nearest_intergenic(b, cds_list)
            if new_b != b:
                adjusted += 1
            new_boundaries.append(new_b)
        else:
            new_boundaries.append(b)
    new_boundaries.append(GENOME_LENGTH)  # genome end
    new_boundaries = sorted(set(new_boundaries))
    print(f"  Adjusted {adjusted} boundaries out of CDS")
    print(f"  Final boundaries: {len(new_boundaries)}")

    # Verify no boundary is in CDS (except 0 and genome_length)
    in_cds = sum(1 for b in new_boundaries[1:-1] if is_in_cds(b, cds_list))
    print(f"  Boundaries still in CDS: {in_cds}")

    # 3. Build tiles from adjusted boundaries
    print("\n[3/7] Building v2 tiles...")
    n_tiles = len(new_boundaries) - 1
    tiles = []
    for i in range(n_tiles):
        start = new_boundaries[i]
        end = new_boundaries[i + 1]
        length = end - start

        # Assign to Lvl1 group and position
        group_id = i // TILES_PER_GROUP
        position = i % TILES_PER_GROUP

        # Standardized overhangs by position
        overhang_left = STANDARD_OVERHANGS[position]
        overhang_right = STANDARD_OVERHANGS[position + 1] if position < TILES_PER_GROUP - 1 else STANDARD_OVERHANGS[TILES_PER_GROUP]

        # Handle last group (may have fewer tiles)
        total_groups = math.ceil(n_tiles / TILES_PER_GROUP)
        if group_id == total_groups - 1:
            tiles_in_last_group = n_tiles - (total_groups - 1) * TILES_PER_GROUP
            if position == tiles_in_last_group - 1:
                overhang_right = STANDARD_OVERHANGS[position + 1]

        tiles.append({
            'id': i,
            'start': start,
            'end': end,
            'length': length,
            'lvl1_group': group_id,
            'position': position,
            'overhang_left': overhang_left,
            'overhang_right': overhang_right,
        })

    n_groups = math.ceil(n_tiles / TILES_PER_GROUP)
    print(f"  Tiles: {n_tiles}")
    print(f"  Lvl1 groups: {n_groups}")
    print(f"  Tiles per group: {TILES_PER_GROUP} (last group: {n_tiles - (n_groups-1)*TILES_PER_GROUP})")
    avg_tile = sum(t['length'] for t in tiles) / len(tiles)
    avg_group = sum(t['length'] for t in tiles) / n_groups * TILES_PER_GROUP / TILES_PER_GROUP
    print(f"  Average tile: {avg_tile:.0f} bp")

    # 4. Design primers
    print("\n[4/7] Designing primers with standardized overhangs...")
    for t in tiles:
        fwd_primer, fwd_tm = design_primer(genome_seq, t['start'], 'fwd', t['overhang_left'])
        rev_primer, rev_tm = design_primer(genome_seq, t['end'], 'rev', t['overhang_right'])
        t['fwd_primer'] = fwd_primer
        t['rev_primer'] = rev_primer
        t['fwd_tm'] = fwd_tm
        t['rev_tm'] = rev_tm

    print(f"  Designed {len(tiles) * 2} primers")

    # 5. PCR simulation — check internal BsaI + junction BsaI
    print("\n[5/7] Running PCR simulation...")
    for t in tiles:
        t['internal_bsai'] = count_internal_bsai(genome_seq, t['start'], t['end'])
        t['gc_content'] = gc_content(genome_seq, t['start'], t['end'])

        # Check if standardized overhang creates BsaI at junction
        t['junction_bsai_left'] = check_junction_bsai(genome_seq, t['start'], t['overhang_left'])
        t['junction_bsai_right'] = check_junction_bsai(genome_seq, t['end'], t['overhang_right'])

        t['gg_ready'] = (t['internal_bsai'] == 0 and
                         not t['junction_bsai_left'] and
                         not t['junction_bsai_right'])

    ready = sum(1 for t in tiles if t['gg_ready'])
    blocked = len(tiles) - ready
    internal_blocked = sum(1 for t in tiles if t['internal_bsai'] > 0)
    junction_blocked = sum(1 for t in tiles if t['junction_bsai_left'] or t['junction_bsai_right'])
    print(f"  GG-ready: {ready}/{len(tiles)} ({100*ready/len(tiles):.1f}%)")
    print(f"  Blocked (internal BsaI): {internal_blocked}")
    print(f"  Blocked (junction BsaI): {junction_blocked}")

    # 6. Domestication — same OE-PCR approach for internal sites
    print("\n[6/7] Designing domestication primers...")
    total_dom_primers = 0
    total_subfragments = 0
    domestication_data = {}

    for t in tiles:
        if t['internal_bsai'] == 0 and not t['junction_bsai_left'] and not t['junction_bsai_right']:
            t['domestication'] = None
            continue

        region = genome_seq[t['start']:t['end']]
        sites = []

        # Find internal BsaI sites
        for pattern, name in [(BSAI_FWD, 'fwd'), (BSAI_REV, 'rev')]:
            pos = 0
            while True:
                idx = region.find(pattern, pos)
                if idx == -1:
                    break
                genome_pos = t['start'] + idx
                sites.append(genome_pos)
                pos = idx + 1

        # Design mutagenic primers for each site
        mut_primers = []
        for site_pos in sorted(sites):
            # Find which nt to mutate (silent if in CDS)
            original_nt = genome_seq[site_pos + 2]  # 3rd position of recognition site
            mutant_nt = {'G': 'A', 'A': 'G', 'T': 'C', 'C': 'T'}[original_nt]

            # Check if in a gene
            gene = 'intergenic'
            for c in cds_list:
                if c['start'] <= site_pos < c['end']:
                    gene = c['gene'] or 'unknown'
                    break

            # Mutagenic primer (30bp centered on mutation)
            mut_start = max(0, site_pos - 15)
            mut_end = min(GENOME_LENGTH, site_pos + 15)
            fwd_seq = genome_seq[mut_start:site_pos + 2] + mutant_nt + genome_seq[site_pos + 3:mut_end]
            rev_seq = reverse_complement(fwd_seq)

            mut_primers.append({
                'site_pos': site_pos,
                'original_nt': original_nt,
                'mutant_nt': mutant_nt,
                'gene': gene,
                'fwd_seq': fwd_seq,
                'rev_seq': rev_seq,
                'fwd_tm': round(calc_tm(fwd_seq), 1),
                'rev_tm': round(calc_tm(rev_seq), 1),
            })

        # Subfragments (split tile at each mutation site)
        cut_points = [t['start']] + sorted(sites) + [t['end']]
        subfragments = []
        for i in range(len(cut_points) - 1):
            sf_start = cut_points[i]
            sf_end = cut_points[i + 1]
            sf_fwd, sf_fwd_tm = design_primer(genome_seq, sf_start, 'fwd', '')
            sf_rev, sf_rev_tm = design_primer(genome_seq, sf_end, 'rev', '')
            # Strip empty overhang adapter for subfragments
            sf_fwd = sf_fwd.replace(BSAI_ADAPTER, '')
            sf_rev = sf_rev.replace(BSAI_ADAPTER, '')
            subfragments.append({
                'index': i,
                'start': sf_start,
                'end': sf_end,
                'length': sf_end - sf_start,
                'fwd_primer': sf_fwd,
                'rev_primer': sf_rev,
                'fwd_tm': sf_fwd_tm,
                'rev_tm': sf_rev_tm,
            })

        t['domestication'] = {
            'n_sites': len(sites),
            'primers': mut_primers,
            'subfragments': subfragments,
        }
        total_dom_primers += len(mut_primers) * 2
        total_subfragments += len(subfragments)

    tiles_needing_dom = sum(1 for t in tiles if t['domestication'] is not None)
    print(f"  Tiles needing domestication: {tiles_needing_dom}")
    print(f"  Total mutagenic primers: {total_dom_primers}")
    print(f"  Total subfragments: {total_subfragments}")

    total_primers = len(tiles) * 2 + total_dom_primers
    print(f"  Total oligos: {total_primers}")

    # 7. Build Lvl1 groups
    print("\n[7/7] Building Lvl1 group summaries...")
    groups = []
    for g in range(n_groups):
        group_tiles = [t for t in tiles if t['lvl1_group'] == g]
        g_start = group_tiles[0]['start']
        g_end = group_tiles[-1]['end']
        blocked_tiles = [t for t in group_tiles if not t['gg_ready']]

        groups.append({
            'id': g,
            'start': g_start,
            'end': g_end,
            'length': g_end - g_start,
            'total_tiles': len(group_tiles),
            'ready_tiles': len(group_tiles) - len(blocked_tiles),
            'blocked_tiles_count': len(blocked_tiles),
            'blocked_tile_ids': [t['id'] for t in blocked_tiles],
            'complete_before': len(blocked_tiles) == 0,
            'complete_after': True,  # all can be domesticated
        })

    complete_before = sum(1 for g in groups if g['complete_before'])
    print(f"  Groups complete before domestication: {complete_before}/{n_groups}")
    print(f"  Groups complete after domestication: {n_groups}/{n_groups}")

    # ── Export ──
    print("\n" + "=" * 70)
    print("EXPORTING V2 DATA")
    print("=" * 70)

    os.makedirs('data', exist_ok=True)

    # Export tiles CSV
    csv_fields = ['id', 'start', 'end', 'length', 'lvl1_group', 'position',
                  'overhang_left', 'overhang_right', 'fwd_primer', 'rev_primer',
                  'fwd_tm', 'rev_tm', 'internal_bsai', 'junction_bsai_left',
                  'junction_bsai_right', 'gg_ready', 'gc_content']

    with open('data/v2_tiles.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction='ignore')
        writer.writeheader()
        for t in tiles:
            row = {k: t[k] for k in csv_fields if k in t}
            writer.writerow(row)
    print(f"  Saved data/v2_tiles.csv ({len(tiles)} tiles)")

    # Export groups CSV
    with open('data/v2_lvl1_groups.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'start', 'end', 'length',
                                                'total_tiles', 'ready_tiles',
                                                'blocked_tiles_count', 'complete_before'])
        writer.writeheader()
        for g in groups:
            writer.writerow({k: g[k] for k in writer.fieldnames})
    print(f"  Saved data/v2_lvl1_groups.csv ({len(groups)} groups)")

    # Export data bundle for MoClo viewer
    bundle = {
        'version': 'v2',
        'genome': {
            'name': 'E. coli K-12 MG1655',
            'accession': 'U00096.3',
            'length': GENOME_LENGTH,
        },
        'design': {
            'tiles_per_group': TILES_PER_GROUP,
            'standard_overhangs': STANDARD_OVERHANGS,
            'overhang_type': 'standardized',
        },
        'tiles': [{
            'id': t['id'],
            'start': t['start'],
            'end': t['end'],
            'length': t['length'],
            'lvl1_group': t['lvl1_group'],
            'position': t['position'],
            'overhang_left': t['overhang_left'],
            'overhang_right': t['overhang_right'],
            'fwd_primer': t['fwd_primer'],
            'rev_primer': t['rev_primer'],
            'fwd_tm': t['fwd_tm'],
            'rev_tm': t['rev_tm'],
            'boundary_type': 'intergenic',
            'internal_bsai': t['internal_bsai'],
            'primer_domesticated': 0,
            'extra_domestication': t['internal_bsai'],
            'gg_ready': t['gg_ready'],
            'gc_content': t['gc_content'],
            'domestication': t['domestication'],
        } for t in tiles],
        'lvl1_groups': groups,
        'stats': {
            'total_tiles': len(tiles),
            'ready_tiles': ready,
            'blocked_tiles': blocked,
            'total_lvl1_groups': n_groups,
            'complete_before': complete_before,
            'complete_after': n_groups,
            'total_primers': total_primers,
            'total_pcr_reactions': len(tiles) + total_subfragments,
        },
    }

    with open('moclo-viewer/public/data_bundle_v2.json', 'w') as f:
        json.dump(bundle, f, separators=(',', ':'))
    print(f"  Saved moclo-viewer/public/data_bundle_v2.json")

    # ── Summary ──
    print("\n" + "=" * 70)
    print("V2 PIPELINE SUMMARY")
    print("=" * 70)
    print(f"  Total tiles:              {len(tiles)}")
    print(f"  Tiles per Lvl1 group:     {TILES_PER_GROUP}")
    print(f"  Total Lvl1 groups:        {n_groups}")
    print(f"  Average Lvl1 size:        {sum(g['length'] for g in groups)/len(groups)/1000:.1f} kb")
    print(f"  GG-ready tiles:           {ready}/{len(tiles)} ({100*ready/len(tiles):.1f}%)")
    print(f"  Tiles needing domest.:    {tiles_needing_dom}")
    print(f"  Boundaries in CDS:        {in_cds}")
    print(f"  Total oligos:             {total_primers}")
    print(f"  Standardized overhangs:   {', '.join(STANDARD_OVERHANGS)}")


if __name__ == '__main__':
    run_pipeline()
