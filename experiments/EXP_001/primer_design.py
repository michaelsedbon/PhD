#!/usr/bin/env python3
"""
primer_design.py — Golden Gate genome tiling primer designer for E. coli MG1655

Part of EXP_001: designs ~7 kb Lvl0 tiles with BsaI overhangs,
grouped for 11-fragment Lvl1 assembly.

Includes:
  - Operon inference from GenBank
  - Boundary scoring (prefer inter-operon gaps, near BsaI sites)
  - Primer design with Tm optimization
  - Hierarchical overhang system for Lvl0 → Lvl1 assembly
  - BsaI domestication analysis (synonymous mutations)

Usage:
    python3 primer_design.py
"""

import math
import os
import sys
from bisect import bisect_left, bisect_right
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Local
sys.path.insert(0, str(Path(__file__).parent))
from restriction_utils import download_mg1655, find_sites

# ── Configuration ───────────────────────────────────────────────────
DATA_DIR        = Path(__file__).parent / "data"
TARGET_TILE_BP  = 7000          # ideal tile size
FLEX_BP         = 1000          # search ±this around ideal cut
TILES_PER_LVL1  = 11            # tiles per Lvl1 assembly
OPERON_GAP_MAX  = 50            # bp — max intergenic gap to call "same operon"
TM_TARGET       = 60.0          # °C
TM_TOL          = 2.0           # ±°C
BIND_MIN        = 18            # min primer binding region
BIND_MAX        = 25            # max primer binding region
BSAI_SITE       = "GGTCTC"
BSAI_RC         = "GAGACC"
BSAI_SITE_LEN   = 6

# Plotly dark theme
DARK_BG  = '#0d1117'
CARD_BG  = '#161b22'
GRID_CLR = '#21262d'
TEXT_CLR = '#c9d1d9'
ACCENT   = '#58a6ff'
GREEN    = '#3fb950'
YELLOW   = '#d29922'
ORANGE   = '#db6d28'
RED      = '#f85149'
PALETTE  = ['#58a6ff', '#3fb950', '#d29922', '#db6d28', '#f85149', '#bc8cff', '#f778ba', '#79c0ff']

LAYOUT = dict(
    template='plotly_dark',
    paper_bgcolor=DARK_BG,
    plot_bgcolor=CARD_BG,
    font=dict(family='Inter, system-ui, sans-serif', size=13, color=TEXT_CLR),
    margin=dict(l=60, r=30, t=60, b=50),
)
AXIS = dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR)


def save_fig(fig, name, width=1400, height=600):
    fig.write_html(DATA_DIR / f'{name}.html', include_plotlyjs='cdn')
    fig.write_image(DATA_DIR / f'{name}.png', width=width, height=height, scale=2)
    print(f"  ✓ {name}.html + .png")


# ── Codon tables ────────────────────────────────────────────────────

CODON_TABLE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

AA_TO_CODONS: Dict[str, List[str]] = {}
for codon, aa in CODON_TABLE.items():
    AA_TO_CODONS.setdefault(aa, []).append(codon)


def rc(seq: str) -> str:
    """Reverse complement."""
    comp = str.maketrans('ATCGatcg', 'TAGCtagc')
    return seq.translate(comp)[::-1]


# ── Tm calculation (nearest-neighbor) ──────────────────────────────
# SantaLucia 1998 parameters (1M NaCl)

NN_PARAMS = {
    'AA': (-7.9, -22.2), 'TT': (-7.9, -22.2),
    'AT': (-7.2, -20.4), 'TA': (-7.2, -21.3),
    'CA': (-8.5, -22.7), 'TG': (-8.5, -22.7),
    'GT': (-8.4, -22.4), 'AC': (-8.4, -22.4),
    'CT': (-7.8, -21.0), 'AG': (-7.8, -21.0),
    'GA': (-8.2, -22.2), 'TC': (-8.2, -22.2),
    'CG': (-10.6, -27.2), 'GC': (-9.8, -24.4),
    'GG': (-8.0, -19.9), 'CC': (-8.0, -19.9),
}

def calc_tm(seq: str, c_primer: float = 250e-9, c_salt: float = 0.05) -> float:
    """Nearest-neighbor Tm (°C) for a primer sequence."""
    seq = seq.upper()
    dH = 0.0  # kcal/mol
    dS = 0.0  # cal/(mol·K)
    for i in range(len(seq) - 1):
        dinuc = seq[i:i+2]
        if dinuc in NN_PARAMS:
            h, s = NN_PARAMS[dinuc]
            dH += h
            dS += s
    # Initiation
    dH += 0.1   # initiation correction
    dS += -2.8
    # Salt correction
    dS += 0.368 * len(seq) * math.log(c_salt)
    R = 1.987  # cal/(mol·K)
    tm = (dH * 1000) / (dS + R * math.log(c_primer / 4)) - 273.15
    return tm


# ── Data structures ────────────────────────────────────────────────

@dataclass
class Gene:
    name: str
    locus_tag: str
    start: int
    end: int
    strand: int  # +1 or -1
    gene_type: str  # 'CDS', 'tRNA', 'rRNA', etc.

@dataclass
class Operon:
    genes: List[Gene]
    start: int = 0
    end: int = 0
    strand: int = 0

    def __post_init__(self):
        self.start = min(g.start for g in self.genes)
        self.end = max(g.end for g in self.genes)
        self.strand = self.genes[0].strand

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def gene_names(self) -> str:
        return ", ".join(g.name for g in self.genes)

@dataclass
class BsaISite:
    position: int         # 0-based start of the 6-bp recognition site
    strand: int           # +1 (GGTCTC) or -1 (GAGACC on top strand)
    in_cds: bool = False
    gene_name: str = ""
    codon_pos: int = -1   # which nt of the codon the site starts at
    can_domesticate: bool = True
    mutation: str = ""    # proposed mutation description

@dataclass
class Tile:
    index: int
    start: int
    end: int
    length: int = 0
    lvl1_group: int = 0
    overhang_left: str = ""
    overhang_right: str = ""
    fwd_primer: str = ""
    rev_primer: str = ""
    fwd_tm: float = 0.0
    rev_tm: float = 0.0
    boundary_score: int = 0      # 0=inter-operon, 1=intra-operon, 2=in CDS
    internal_bsai_sites: int = 0
    primer_domesticated: int = 0  # sites covered by primer binding region
    needs_extra_domestication: int = 0
    operon_broken: bool = False

    def __post_init__(self):
        self.length = self.end - self.start


# ═══════════════════════════════════════════════════════════════════
# 1. OPERON INFERENCE
# ═══════════════════════════════════════════════════════════════════

def extract_genes(record) -> List[Gene]:
    """Extract gene features from GenBank record."""
    genes = []
    for f in record.features:
        if f.type not in ('CDS', 'tRNA', 'rRNA', 'ncRNA'):
            continue
        genes.append(Gene(
            name=f.qualifiers.get('gene', f.qualifiers.get('locus_tag', ['?']))[0],
            locus_tag=f.qualifiers.get('locus_tag', ['?'])[0],
            start=int(f.location.start),
            end=int(f.location.end),
            strand=f.location.strand,
            gene_type=f.type,
        ))
    genes.sort(key=lambda g: g.start)
    return genes


def infer_operons(genes: List[Gene]) -> List[Operon]:
    """
    Group genes into operons:
    consecutive same-strand genes with intergenic gap ≤ OPERON_GAP_MAX.
    """
    if not genes:
        return []

    operons = []
    current = [genes[0]]
    for g in genes[1:]:
        prev = current[-1]
        gap = g.start - prev.end
        if g.strand == prev.strand and gap <= OPERON_GAP_MAX:
            current.append(g)
        else:
            operons.append(Operon(genes=current))
            current = [g]
    operons.append(Operon(genes=current))
    return operons


def print_operon_stats(operons: List[Operon]):
    """Print operon statistics."""
    lengths = [op.length for op in operons]
    gene_counts = [len(op.genes) for op in operons]
    singletons = sum(1 for op in operons if len(op.genes) == 1)

    print(f"\n{'='*60}")
    print(f"OPERON ANALYSIS")
    print(f"{'='*60}")
    print(f"Total operons inferred:  {len(operons)}")
    print(f"Singletons (1 gene):     {singletons} ({100*singletons/len(operons):.0f}%)")
    print(f"Multi-gene operons:      {len(operons)-singletons}")
    print(f"")
    print(f"Operon length (bp):")
    print(f"  Median: {int(np.median(lengths)):,}")
    print(f"  Mean:   {int(np.mean(lengths)):,}")
    print(f"  Max:    {max(lengths):,} ({operons[np.argmax(lengths)].gene_names[:50]}...)")
    print(f"  Min:    {min(lengths):,}")
    print(f"")
    print(f"Genes per operon:")
    print(f"  Median: {np.median(gene_counts):.0f}")
    print(f"  Mean:   {np.mean(gene_counts):.1f}")
    print(f"  Max:    {max(gene_counts)}")

    # Distribution table
    gc = Counter(gene_counts)
    print(f"\n  Genes  Operons")
    for n in sorted(gc)[:10]:
        print(f"  {n:5d}   {gc[n]:5d}")
    if max(gene_counts) > 10:
        print(f"  11+     {sum(v for k,v in gc.items() if k > 10):5d}")


def plot_operon_distribution(operons: List[Operon]):
    """Plot operon length distribution."""
    lengths = [op.length for op in operons]
    gene_counts = [len(op.genes) for op in operons]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=['Operon length distribution', 'Genes per operon'],
                        horizontal_spacing=0.1)

    fig.add_trace(go.Histogram(
        x=lengths, nbinsx=100,
        marker_color=ACCENT,
        marker_line=dict(color=DARK_BG, width=0.5),
        hovertemplate='%{x:,.0f} bp: %{y} operons<extra></extra>',
    ), row=1, col=1)
    fig.add_vline(x=7000, line=dict(color=RED, width=2, dash='dash'), row=1, col=1)
    fig.add_annotation(
        text='7 kb tile size', x=7000, y=0.95,
        xref='x domain', yref='y domain',
        showarrow=True, arrowhead=2, ax=40, ay=0,
        font=dict(size=10, color=RED),
    )

    fig.add_trace(go.Histogram(
        x=gene_counts, nbinsx=max(gene_counts),
        marker_color=GREEN,
        marker_line=dict(color=DARK_BG, width=0.5),
        hovertemplate='%{x} genes: %{y} operons<extra></extra>',
    ), row=1, col=2)

    fig.update_xaxes(title_text='Length (bp)', row=1, col=1, **AXIS)
    fig.update_yaxes(title_text='Count', row=1, col=1, **AXIS)
    fig.update_xaxes(title_text='Genes per operon', row=1, col=2, **AXIS)
    fig.update_yaxes(title_text='Count', row=1, col=2, **AXIS)

    fig.update_layout(title='Operon structure in E. coli MG1655', height=450, showlegend=False, **LAYOUT)
    for ann in fig.layout.annotations:
        if ann.font.color is None:
            ann.font.color = TEXT_CLR

    save_fig(fig, 'operon_length_distribution', height=450)


# ═══════════════════════════════════════════════════════════════════
# 2. BOUNDARY SCORING
# ═══════════════════════════════════════════════════════════════════

def build_boundary_scores(genes: List[Gene], operons: List[Operon],
                          genome_len: int) -> np.ndarray:
    """
    Build an array scoring each bp as a tile-boundary candidate.
    0 = inter-operon gap (best)
    1 = intra-operon intergenic
    2 = inside CDS (worst)
    """
    scores = np.zeros(genome_len, dtype=np.int8)

    # Mark all CDS regions as score=2
    for g in genes:
        if g.gene_type == 'CDS':
            scores[g.start:g.end] = 2

    # Mark intra-operon intergenic regions as score=1
    for op in operons:
        if len(op.genes) < 2:
            continue
        sorted_genes = sorted(op.genes, key=lambda g: g.start)
        for i in range(len(sorted_genes) - 1):
            g1_end = sorted_genes[i].end
            g2_start = sorted_genes[i+1].start
            if g2_start > g1_end:
                scores[g1_end:g2_start] = 1

    return scores


# ═══════════════════════════════════════════════════════════════════
# 3. TILING
# ═══════════════════════════════════════════════════════════════════

def find_bsai_sites_detailed(seq_str: str, genes: List[Gene]) -> List[BsaISite]:
    """Find all BsaI sites with CDS context."""
    sites = []

    # Forward strand: GGTCTC
    pos = 0
    while True:
        pos = seq_str.find(BSAI_SITE, pos)
        if pos == -1:
            break
        sites.append(BsaISite(position=pos, strand=1))
        pos += 1

    # Reverse strand: GAGACC on top strand
    pos = 0
    while True:
        pos = seq_str.find(BSAI_RC, pos)
        if pos == -1:
            break
        sites.append(BsaISite(position=pos, strand=-1))
        pos += 1

    # Annotate CDS context
    cds_intervals = [(g.start, g.end, g.strand, g.name)
                     for g in genes if g.gene_type == 'CDS']
    cds_intervals.sort()

    for site in sites:
        site_range = range(site.position, site.position + BSAI_SITE_LEN)
        for cds_start, cds_end, cds_strand, gene_name in cds_intervals:
            if cds_start > site.position + BSAI_SITE_LEN:
                break
            if any(bp in range(cds_start, cds_end) for bp in site_range):
                site.in_cds = True
                site.gene_name = gene_name
                break

    sites.sort(key=lambda s: s.position)
    return sites


def tile_genome(genome_len: int, boundary_scores: np.ndarray,
                bsai_positions: List[int]) -> List[Tuple[int, int, int]]:
    """
    Tile the genome into ~7 kb fragments.
    Returns list of (start, end, boundary_score).
    """
    bsai_set = set(bsai_positions)
    tiles = []
    pos = 0

    while pos < genome_len:
        ideal_end = pos + TARGET_TILE_BP
        if ideal_end >= genome_len:
            # Last tile wraps to genome end
            tiles.append((pos, genome_len, 0))
            break

        # Search window
        search_start = max(pos + TARGET_TILE_BP - FLEX_BP, pos + 3000)
        search_end = min(pos + TARGET_TILE_BP + FLEX_BP, genome_len)

        best_pos = ideal_end
        best_score = boundary_scores[ideal_end]
        best_bsai_dist = _min_bsai_dist(ideal_end, bsai_positions)

        for p in range(search_start, search_end):
            score = boundary_scores[p]
            if score < best_score:
                best_score = score
                best_pos = p
                best_bsai_dist = _min_bsai_dist(p, bsai_positions)
            elif score == best_score:
                # Tie-break: PREFER positions near a BsaI site
                # (within primer binding region ≈ 25bp)
                d = _min_bsai_dist(p, bsai_positions)
                if d <= BIND_MAX and (best_bsai_dist > BIND_MAX or d < best_bsai_dist):
                    best_pos = p
                    best_bsai_dist = d

        tiles.append((pos, best_pos, int(best_score)))
        pos = best_pos

    return tiles


def _min_bsai_dist(pos: int, bsai_positions: List[int]) -> int:
    """Min distance from pos to any BsaI site."""
    if not bsai_positions:
        return 999999
    idx = bisect_left(bsai_positions, pos)
    dists = []
    for i in (idx - 1, idx, idx + 1):
        if 0 <= i < len(bsai_positions):
            dists.append(abs(pos - bsai_positions[i]))
    return min(dists) if dists else 999999


# ═══════════════════════════════════════════════════════════════════
# 4. PRIMER DESIGN
# ═══════════════════════════════════════════════════════════════════

def design_primer_pair(seq_str: str, tile_start: int, tile_end: int,
                       genome_len: int, bsai_sites: List[BsaISite]
                       ) -> Tuple[str, str, float, float, int]:
    """
    Design forward and reverse primers for a tile.

    Returns: (fwd_primer, rev_primer, fwd_tm, rev_tm, primer_domesticated_count)
    """
    domesticated = 0

    # ── Forward primer ──
    # Binding region = start of tile
    fwd_bind, fwd_tm = _optimize_binding(seq_str, tile_start, direction=1)
    # Check if any BsaI site falls within binding region
    fwd_bind, fwd_dom = _domesticate_in_binding(
        fwd_bind, tile_start, tile_start + len(fwd_bind), bsai_sites, seq_str, direction=1)
    domesticated += fwd_dom
    fwd_tm = calc_tm(fwd_bind)

    # Overhang = 4 nt at tile start
    overhang_fwd = seq_str[tile_start:tile_start + 4].upper()
    # Full primer: extra + BsaI + spacer + overhang + binding
    fwd_primer = f"CGTCTC{'N'}{overhang_fwd}{fwd_bind}"

    # ── Reverse primer ──
    # Binding region = end of tile (we need RC)
    rev_bind_start = max(tile_end - BIND_MAX, tile_start)
    rev_bind, rev_tm = _optimize_binding(seq_str, tile_end, direction=-1)
    rev_bind, rev_dom = _domesticate_in_binding(
        rev_bind, tile_end - len(rev_bind), tile_end, bsai_sites, seq_str, direction=-1)
    domesticated += rev_dom
    rev_tm = calc_tm(rev_bind)

    # Overhang = RC of 4 nt at tile end
    overhang_rev = rc(seq_str[tile_end - 4:tile_end].upper())
    # Full primer: extra + BsaI + spacer + overhang + binding(RC)
    rev_primer = f"CGTCTC{'N'}{overhang_rev}{rc(rev_bind)}"

    return fwd_primer, rev_primer, fwd_tm, rev_tm, domesticated


def _optimize_binding(seq_str: str, pos: int, direction: int) -> Tuple[str, float]:
    """Find binding region length that gives closest Tm to target."""
    best_seq = ""
    best_tm = 0.0
    best_diff = 999.0

    for length in range(BIND_MIN, BIND_MAX + 1):
        if direction == 1:
            bind = seq_str[pos:pos + length].upper()
        else:
            bind = seq_str[pos - length:pos].upper()

        if len(bind) < length:
            continue

        tm = calc_tm(bind)
        diff = abs(tm - TM_TARGET)
        if diff < best_diff:
            best_diff = diff
            best_seq = bind
            best_tm = tm

    return best_seq, best_tm


def _domesticate_in_binding(bind_seq: str, bind_start: int, bind_end: int,
                            bsai_sites: List[BsaISite], full_seq: str,
                            direction: int) -> Tuple[str, int]:
    """
    If any BsaI site overlaps the primer binding region, introduce a
    silent mutation in the primer to destroy it.
    """
    domesticated = 0
    bind_list = list(bind_seq)

    for site in bsai_sites:
        site_end = site.position + BSAI_SITE_LEN
        # Check overlap
        if site.position < bind_end and site_end > bind_start:
            # Site overlaps binding region — mutate one base
            # Find the position within the binding region
            rel_pos = site.position - bind_start
            # Change the 3rd base of the recognition site (index 2)
            # GGTCTC → GGTaTc or GAGACC → GAGtCC
            mut_offset = 2 if site.strand == 1 else 3
            abs_pos = site.position + mut_offset
            if bind_start <= abs_pos < bind_end:
                idx = abs_pos - bind_start
                original = bind_list[idx]
                # Pick a different base
                for alt in 'ACGT':
                    if alt != original.upper():
                        bind_list[idx] = alt
                        # Verify the site is destroyed
                        new_seq = ''.join(bind_list)
                        if BSAI_SITE not in new_seq and BSAI_RC not in new_seq:
                            domesticated += 1
                            break
                else:
                    bind_list[idx] = original  # revert if no valid mutation

    return ''.join(bind_list), domesticated


# ═══════════════════════════════════════════════════════════════════
# 5. DOMESTICATION ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def analyze_domestication(tile: Tile, bsai_sites: List[BsaISite],
                          seq_str: str, genes: List[Gene]) -> List[dict]:
    """
    For each internal BsaI site in a tile, propose a domestication strategy.
    """
    results = []
    for site in bsai_sites:
        if site.position < tile.start or site.position >= tile.end:
            continue

        # Check if within primer binding region (already handled)
        if (site.position < tile.start + BIND_MAX or
            site.position + BSAI_SITE_LEN > tile.end - BIND_MAX):
            continue  # covered by primer domestication

        info = {
            'position': site.position,
            'strand': '+' if site.strand == 1 else '-',
            'in_cds': site.in_cds,
            'gene': site.gene_name if site.in_cds else 'intergenic',
            'mutation': '',
        }

        if site.in_cds:
            # Propose synonymous mutation
            info['mutation'] = _propose_synonymous(site, seq_str, genes)
        else:
            # Intergenic — any single base change works
            mut_pos = site.position + 2
            orig = seq_str[mut_pos].upper()
            alt = 'A' if orig != 'A' else 'T'
            info['mutation'] = f"pos {mut_pos}: {orig}→{alt} (intergenic)"

        results.append(info)

    return results


def _propose_synonymous(site: BsaISite, seq_str: str,
                        genes: List[Gene]) -> str:
    """Propose a synonymous codon change to destroy a BsaI site in a CDS."""
    # Find the CDS containing this site
    for g in genes:
        if g.gene_type != 'CDS':
            continue
        if g.start <= site.position < g.end:
            # Determine reading frame
            if g.strand == 1:
                frame_offset = (site.position - g.start) % 3
            else:
                frame_offset = (g.end - site.position - 1) % 3

            # Try mutating position 2 of the recognition site
            for mut_offset in [2, 3, 4, 1, 0, 5]:
                mut_pos = site.position + mut_offset
                if mut_pos < g.start or mut_pos >= g.end:
                    continue

                # Get the codon containing this position
                if g.strand == 1:
                    codon_start = g.start + ((mut_pos - g.start) // 3) * 3
                    codon = seq_str[codon_start:codon_start + 3].upper()
                    codon_idx = mut_pos - codon_start
                else:
                    codon_end = g.end - ((g.end - mut_pos - 1) // 3) * 3
                    codon_start = codon_end - 3
                    codon = rc(seq_str[codon_start:codon_end]).upper()
                    codon_idx = codon_end - mut_pos - 1

                if len(codon) != 3 or codon not in CODON_TABLE:
                    continue

                aa = CODON_TABLE[codon]
                # Try all synonymous codons
                for alt_codon in AA_TO_CODONS.get(aa, []):
                    if alt_codon == codon:
                        continue
                    if alt_codon[codon_idx] != codon[codon_idx]:
                        # This changes the base at our target position
                        # Verify it destroys the BsaI site
                        new_seq = list(seq_str)
                        if g.strand == 1:
                            new_seq[codon_start:codon_start + 3] = list(alt_codon)
                        else:
                            rc_alt = rc(alt_codon)
                            new_seq[codon_start:codon_start + 3] = list(rc_alt)
                        test_region = ''.join(new_seq[site.position:site.position + BSAI_SITE_LEN])
                        if BSAI_SITE not in test_region and BSAI_RC not in test_region:
                            orig_base = seq_str[mut_pos].upper()
                            new_base = new_seq[mut_pos].upper()
                            return (f"pos {mut_pos}: {orig_base}→{new_base} "
                                    f"({codon}→{alt_codon}, {aa}, {g.name})")

            return f"pos {site.position}: manual review needed ({g.name})"

    return "unknown CDS context"


# ═══════════════════════════════════════════════════════════════════
# 6. VISUALISATION
# ═══════════════════════════════════════════════════════════════════

def plot_tiling_map(tiles: List[Tile], genome_len: int):
    """Plot genome map coloured by domestication burden."""
    fig = go.Figure()

    # Colour tiles by domestication burden
    for tile in tiles:
        total_dom = tile.internal_bsai_sites
        if total_dom == 0:
            color = GREEN
        elif total_dom <= 1:
            color = YELLOW
        elif total_dom <= 2:
            color = ORANGE
        else:
            color = RED

        fig.add_trace(go.Bar(
            x=[(tile.end - tile.start) / 1e6],
            y=['Tiles'],
            base=[tile.start / 1e6],
            orientation='h',
            marker_color=color,
            marker_line=dict(color=DARK_BG, width=0.5),
            hovertemplate=(
                f'Tile {tile.index}<br>'
                f'{tile.start:,}–{tile.end:,} ({tile.length:,} bp)<br>'
                f'Internal BsaI: {tile.internal_bsai_sites}<br>'
                f'Primer domesticated: {tile.primer_domesticated}<br>'
                f'Lvl1 group: {tile.lvl1_group}'
                '<extra></extra>'
            ),
            showlegend=False,
        ))

    # Add Lvl1 group boundaries
    for tile in tiles:
        if tile.index % TILES_PER_LVL1 == 0 and tile.index > 0:
            fig.add_vline(
                x=tile.start / 1e6,
                line=dict(color=ACCENT, width=1.5, dash='dot'),
            )

    fig.update_layout(
        title=f'Genome tiling map — {len(tiles)} tiles, coloured by domestication burden',
        xaxis_title='Genome position (Mb)',
        height=200, width=1400,
        bargap=0,
        **LAYOUT,
    )
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(showticklabels=False, **AXIS)

    save_fig(fig, 'tiling_map', height=200)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load genome ──
    print("=" * 60)
    print("EXP_001 — Golden Gate Primer Design")
    print("=" * 60)

    record = download_mg1655()
    seq_str = str(record.seq).upper()
    genome_len = len(seq_str)
    print(f"Genome: {genome_len:,} bp")

    # ── 1. Operon inference ──
    genes = extract_genes(record)
    operons = infer_operons(genes)
    print_operon_stats(operons)
    plot_operon_distribution(operons)

    # ── 2. Boundary scores ──
    boundary_scores = build_boundary_scores(genes, operons, genome_len)
    n_intergenic = np.sum(boundary_scores == 0)
    n_intra_op   = np.sum(boundary_scores == 1)
    n_cds        = np.sum(boundary_scores == 2)
    print(f"\nBoundary scores: inter-operon={n_intergenic:,}bp  "
          f"intra-operon={n_intra_op:,}bp  CDS={n_cds:,}bp")

    # ── 3. BsaI sites ──
    bsai_sites = find_bsai_sites_detailed(seq_str, genes)
    bsai_positions = sorted(s.position for s in bsai_sites)
    print(f"BsaI sites: {len(bsai_sites)}")

    # ── 4. Tile the genome ──
    raw_tiles = tile_genome(genome_len, boundary_scores, bsai_positions)
    print(f"\n{'='*60}")
    print(f"TILING RESULTS")
    print(f"{'='*60}")
    print(f"Tiles: {len(raw_tiles)}")

    tile_lengths = [e - s for s, e, _ in raw_tiles]
    print(f"Tile length: median={int(np.median(tile_lengths)):,}  "
          f"mean={int(np.mean(tile_lengths)):,}  "
          f"min={min(tile_lengths):,}  max={max(tile_lengths):,}")

    score_counts = Counter(sc for _, _, sc in raw_tiles)
    print(f"Boundary quality: inter-operon={score_counts.get(0,0)}  "
          f"intra-operon={score_counts.get(1,0)}  "
          f"in-CDS={score_counts.get(2,0)}")

    # ── 5. Build Tile objects with primers ──
    tiles: List[Tile] = []
    for i, (start, end, score) in enumerate(raw_tiles):
        tile = Tile(
            index=i,
            start=start,
            end=end,
            lvl1_group=i // TILES_PER_LVL1,
            boundary_score=score,
        )

        # Design primers
        fwd, rev, fwd_tm, rev_tm, primer_dom = design_primer_pair(
            seq_str, start, end, genome_len, bsai_sites)
        tile.fwd_primer = fwd
        tile.rev_primer = rev
        tile.fwd_tm = round(fwd_tm, 1)
        tile.rev_tm = round(rev_tm, 1)
        tile.primer_domesticated = primer_dom

        # Overhangs
        tile.overhang_left = seq_str[start:start + 4]
        tile.overhang_right = seq_str[end - 4:end] if end <= genome_len else seq_str[end - 4:genome_len]

        # Internal BsaI sites (excluding those in primer binding region)
        internal = [s for s in bsai_sites
                    if start + BIND_MAX <= s.position < end - BIND_MAX
                    and start <= s.position < end]
        tile.internal_bsai_sites = len(internal) + primer_dom
        tile.needs_extra_domestication = len(internal)

        tiles.append(tile)

    # ── 6. Overhang uniqueness check per Lvl1 group ──
    print(f"\n{'='*60}")
    print(f"OVERHANG ANALYSIS")
    print(f"{'='*60}")
    n_lvl1_groups = max(t.lvl1_group for t in tiles) + 1
    print(f"Lvl1 groups: {n_lvl1_groups} (of {TILES_PER_LVL1} tiles each)")

    overhang_issues = 0
    for grp in range(n_lvl1_groups):
        grp_tiles = [t for t in tiles if t.lvl1_group == grp]
        overhangs = set()
        for t in grp_tiles:
            overhangs.add(t.overhang_left)
            overhangs.add(t.overhang_right)
        expected = len(grp_tiles) + 1  # N tiles → N+1 junctions
        if len(overhangs) < expected:
            print(f"  ⚠ Group {grp}: {len(overhangs)} unique overhangs (need {expected})")
            overhang_issues += 1

    if overhang_issues == 0:
        print(f"  ✓ All {n_lvl1_groups} groups have unique junction overhangs")

    # ── 7. Domestication summary ──
    print(f"\n{'='*60}")
    print(f"DOMESTICATION SUMMARY")
    print(f"{'='*60}")

    dom_counts = Counter(t.internal_bsai_sites for t in tiles)
    for n in sorted(dom_counts):
        pct = 100 * dom_counts[n] / len(tiles)
        bar = '█' * int(pct / 2)
        print(f"  {n} sites: {dom_counts[n]:4d} tiles ({pct:5.1f}%)  {bar}")

    primer_dom_total = sum(t.primer_domesticated for t in tiles)
    extra_dom_total = sum(t.needs_extra_domestication for t in tiles)
    print(f"\n  Domesticated by primers: {primer_dom_total} sites")
    print(f"  Need extra domestication: {extra_dom_total} sites (overlap extension/synthesis)")

    # ── 8. Primer stats ──
    fwd_tms = [t.fwd_tm for t in tiles]
    rev_tms = [t.rev_tm for t in tiles]
    print(f"\n{'='*60}")
    print(f"PRIMER STATISTICS")
    print(f"{'='*60}")
    print(f"Forward Tm: {np.mean(fwd_tms):.1f} ± {np.std(fwd_tms):.1f} °C "
          f"(range {min(fwd_tms):.1f}–{max(fwd_tms):.1f})")
    print(f"Reverse Tm: {np.mean(rev_tms):.1f} ± {np.std(rev_tms):.1f} °C "
          f"(range {min(rev_tms):.1f}–{max(rev_tms):.1f})")

    # ── 9. Save outputs ──
    print(f"\n{'='*60}")
    print(f"SAVING OUTPUTS")
    print(f"{'='*60}")

    # Tiles CSV
    tile_rows = []
    for t in tiles:
        dom_details = analyze_domestication(t, bsai_sites, seq_str, genes)
        tile_rows.append({
            'tile': t.index,
            'start': t.start,
            'end': t.end,
            'length': t.length,
            'lvl1_group': t.lvl1_group,
            'overhang_left': t.overhang_left,
            'overhang_right': t.overhang_right,
            'fwd_primer': t.fwd_primer,
            'rev_primer': t.rev_primer,
            'fwd_tm': t.fwd_tm,
            'rev_tm': t.rev_tm,
            'boundary_type': ['inter-operon', 'intra-operon', 'in-CDS'][t.boundary_score],
            'internal_bsai_total': t.internal_bsai_sites,
            'primer_domesticated': t.primer_domesticated,
            'extra_domestication': t.needs_extra_domestication,
            'domestication_details': '; '.join(d['mutation'] for d in dom_details) or 'none',
        })

    df_tiles = pd.DataFrame(tile_rows)
    df_tiles.to_csv(DATA_DIR / 'tiles.csv', index=False)
    print(f"  ✓ tiles.csv ({len(tiles)} tiles)")

    # Summary CSV
    summary = {
        'total_tiles': len(tiles),
        'genome_bp': genome_len,
        'tile_median_bp': int(np.median(tile_lengths)),
        'tile_mean_bp': int(np.mean(tile_lengths)),
        'lvl1_groups': n_lvl1_groups,
        'tiles_per_lvl1': TILES_PER_LVL1,
        'boundary_inter_operon': score_counts.get(0, 0),
        'boundary_intra_operon': score_counts.get(1, 0),
        'boundary_in_cds': score_counts.get(2, 0),
        'tiles_site_free': dom_counts.get(0, 0),
        'tiles_1_site': dom_counts.get(1, 0),
        'tiles_2plus_sites': sum(v for k, v in dom_counts.items() if k >= 2),
        'primer_domesticated': primer_dom_total,
        'extra_domestication': extra_dom_total,
        'fwd_tm_mean': round(np.mean(fwd_tms), 1),
        'rev_tm_mean': round(np.mean(rev_tms), 1),
    }
    pd.DataFrame([summary]).to_csv(DATA_DIR / 'tiling_summary.csv', index=False)
    print(f"  ✓ tiling_summary.csv")

    # Plots
    plot_tiling_map(tiles, genome_len)

    print(f"\n{'='*60}")
    print(f"DONE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
