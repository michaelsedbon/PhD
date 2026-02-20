#!/usr/bin/env python3
"""
domestication_primers.py — Design mutagenic primers for overlap extension PCR

Reads tiles.csv (which already contains silent mutation data) and:
  1. Designs mutagenic primer pairs for each internal BsaI site
  2. Computes sub-fragment structure for each blocked tile
  3. Re-runs Lvl1 assembly analysis assuming all tiles domesticated
  4. Generates before/after comparison visualizations

Usage:
    python3 domestication_primers.py
"""

import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).parent))
from restriction_utils import download_mg1655

# ── Configuration ───────────────────────────────────────────────────
DATA_DIR       = Path(__file__).parent / "data"
TILES_PER_LVL1 = 11
BSAI_SITE      = "GGTCTC"
BSAI_RC        = "GAGACC"
PRIMER_FLANK   = 20          # bp of context flanking the mutation in each primer
MIN_TM         = 50.0
MAX_TM         = 65.0

# Plotly theme (same as pcr_simulation)
DARK_BG  = '#0d1117'
CARD_BG  = '#161b22'
GRID_CLR = '#21262d'
TEXT_CLR = '#c9d1d9'
ACCENT   = '#58a6ff'
GREEN    = '#3fb950'
YELLOW   = '#d29922'
ORANGE   = '#db6d28'
RED      = '#f85149'
DIM      = '#30363d'
PURPLE   = '#bc8cff'

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


# ═══════════════════════════════════════════════════════════════════
# HELPER: Tm estimation (simple nearest-neighbor approx)
# ═══════════════════════════════════════════════════════════════════

def estimate_tm(seq: str) -> float:
    """Simple Tm estimate using Wallace rule (<14 bp) or salt-adjusted."""
    seq = seq.upper()
    gc = seq.count('G') + seq.count('C')
    at = seq.count('A') + seq.count('T')
    if len(seq) < 14:
        return 2 * at + 4 * gc
    # Salt-adjusted: Tm = 81.5 + 16.6*log10(0.05) + 41*(G+C)/N - 675/N
    import math
    n = len(seq)
    return 81.5 + 16.6 * math.log10(0.05) + 41 * gc / n - 675 / n


def reverse_complement(seq: str) -> str:
    comp = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N',
            'a': 't', 't': 'a', 'g': 'c', 'c': 'g', 'n': 'n'}
    return ''.join(comp.get(c, c) for c in reversed(seq))


# ═══════════════════════════════════════════════════════════════════
# 1. PARSE DOMESTICATION DETAILS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MutationSite:
    """A single BsaI site requiring domestication."""
    genome_pos: int          # Position of the mutation in the genome
    original_nt: str         # Original nucleotide
    mutant_nt: str           # Replacement nucleotide
    codon_change: str        # e.g., "GAC→GAT" or "intergenic"
    amino_acid: str          # e.g., "D" or ""
    gene: str                # e.g., "dnaJ" or "intergenic"


@dataclass
class DomesticationTarget:
    """A tile that needs domestication via overlap extension PCR."""
    tile_id: int
    tile_start: int
    tile_end: int
    tile_length: int
    lvl1_group: int
    n_internal_sites: int
    n_primer_domesticated: int
    n_extra_sites: int
    mutations: List[MutationSite]
    fwd_primer: str          # Original tile fwd primer
    rev_primer: str          # Original tile rev primer


def parse_domestication_details(details: str) -> List[MutationSite]:
    """Parse the domestication_details column from tiles.csv."""
    if pd.isna(details) or details == 'none' or details.strip() == '':
        return []

    mutations = []
    # Format: "pos 14838: C→T (GAC→GAT, D, dnaJ); pos 18890: T→C (GGT→GGC, G, nhaR)"
    # or:     "pos 228014: T→A (intergenic)"
    parts = details.split('; ')
    for part in parts:
        # Match: pos NNNN: X→Y (codon_info)
        m = re.match(
            r'pos (\d+): ([ACGT])→([ACGT]) \((.+)\)',
            part.strip()
        )
        if not m:
            continue

        pos = int(m.group(1))
        orig = m.group(2)
        mut = m.group(3)
        info = m.group(4)

        if info == 'intergenic':
            codon_change = 'intergenic'
            aa = ''
            gene = 'intergenic'
        else:
            # Format: "GAC→GAT, D, dnaJ"
            info_parts = [x.strip() for x in info.split(',')]
            codon_change = info_parts[0] if len(info_parts) >= 1 else ''
            aa = info_parts[1] if len(info_parts) >= 2 else ''
            gene = info_parts[2] if len(info_parts) >= 3 else ''

        mutations.append(MutationSite(
            genome_pos=pos,
            original_nt=orig,
            mutant_nt=mut,
            codon_change=codon_change,
            amino_acid=aa,
            gene=gene,
        ))

    return mutations


# ═══════════════════════════════════════════════════════════════════
# 2. DESIGN MUTAGENIC PRIMERS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MutagenicPrimerPair:
    """A pair of overlapping mutagenic primers for one BsaI site."""
    site_pos: int            # Genome position of mutation
    fwd_seq: str             # Mutagenic forward primer (5'→3')
    rev_seq: str             # Mutagenic reverse primer (5'→3')
    fwd_tm: float
    rev_tm: float
    mutation: MutationSite


@dataclass
class SubFragment:
    """One PCR sub-fragment of a domesticated tile."""
    frag_index: int
    start: int
    end: int
    length: int
    fwd_primer: str
    rev_primer: str
    fwd_tm: float
    rev_tm: float


@dataclass
class DomesticationPlan:
    """Complete plan for domesticating one tile."""
    tile_id: int
    lvl1_group: int
    tile_start: int
    tile_end: int
    n_sites: int
    primer_pairs: List[MutagenicPrimerPair]
    sub_fragments: List[SubFragment]
    total_primers: int       # Including original tile primers


def design_mutagenic_primers(
    target: DomesticationTarget,
    genome_seq: str,
) -> DomesticationPlan:
    """
    Design mutagenic primer pairs for overlap extension PCR.

    For each internal BsaI site, create overlapping primers with the mutation.
    The tile gets split into N+1 sub-fragments (N = number of sites).
    """
    mutations = sorted(target.mutations, key=lambda m: m.genome_pos)
    primer_pairs = []

    for mut in mutations:
        pos = mut.genome_pos
        # The mutation is at this genome position
        # Design primers centered on the mutation site

        # Forward mutagenic primer: upstream context + mutation + downstream context
        fwd_start = max(target.tile_start, pos - PRIMER_FLANK)
        fwd_end = min(target.tile_end, pos + PRIMER_FLANK + 1)
        fwd_seq_list = list(genome_seq[fwd_start:fwd_end].upper())

        # Insert mutation at the correct position
        mut_offset = pos - fwd_start
        if 0 <= mut_offset < len(fwd_seq_list):
            fwd_seq_list[mut_offset] = mut.mutant_nt
        fwd_seq = ''.join(fwd_seq_list)

        # Reverse mutagenic primer: reverse complement
        rev_seq = reverse_complement(fwd_seq)

        fwd_tm = estimate_tm(fwd_seq)
        rev_tm = estimate_tm(rev_seq)

        primer_pairs.append(MutagenicPrimerPair(
            site_pos=pos,
            fwd_seq=fwd_seq,
            rev_seq=rev_seq,
            fwd_tm=fwd_tm,
            rev_tm=rev_tm,
            mutation=mut,
        ))

    # Compute sub-fragments
    # Original tile: [tile_start --- site1 --- site2 --- tile_end]
    # Sub-fragments: [tile_start..site1], [site1..site2], [site2..tile_end]
    # Each internal boundary uses mutagenic primers for overlap

    sub_fragments = []
    boundaries = [target.tile_start] + [m.genome_pos for m in mutations] + [target.tile_end]

    for i in range(len(boundaries) - 1):
        frag_start = boundaries[i]
        frag_end = boundaries[i + 1]

        if i == 0:
            # First fragment: original tile fwd primer → mutagenic rev
            fwd_p = target.fwd_primer
            rev_p = primer_pairs[0].rev_seq if primer_pairs else target.rev_primer
        elif i == len(boundaries) - 2:
            # Last fragment: mutagenic fwd → original tile rev primer
            fwd_p = primer_pairs[-1].fwd_seq
            rev_p = target.rev_primer
        else:
            # Middle fragment: mutagenic fwd → mutagenic rev
            fwd_p = primer_pairs[i - 1].fwd_seq
            rev_p = primer_pairs[i].rev_seq

        sub_fragments.append(SubFragment(
            frag_index=i,
            start=frag_start,
            end=frag_end,
            length=frag_end - frag_start,
            fwd_primer=fwd_p,
            rev_primer=rev_p,
            fwd_tm=estimate_tm(fwd_p[-20:]),  # Use last 20bp for Tm
            rev_tm=estimate_tm(rev_p[:20]),
        ))

    # Total new primers = 2 * N_sites (mutagenic pairs)
    # Original tile primers are reused for sub-fragments 0 and N
    total_primers = 2 * len(mutations)

    return DomesticationPlan(
        tile_id=target.tile_id,
        lvl1_group=target.lvl1_group,
        tile_start=target.tile_start,
        tile_end=target.tile_end,
        n_sites=len(mutations),
        primer_pairs=primer_pairs,
        sub_fragments=sub_fragments,
        total_primers=total_primers,
    )


# ═══════════════════════════════════════════════════════════════════
# 3. ASSEMBLY ANALYSIS — BEFORE / AFTER
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Lvl1Group:
    group_id: int
    total_tiles: int
    ready_before: int
    blocked_before: int
    ready_after: int
    blocked_after: int
    complete_before: bool
    complete_after: bool
    start: int
    end: int
    length: int


def analyze_before_after(tiles_df: pd.DataFrame) -> List[Lvl1Group]:
    """Analyze Lvl1 groups before and after domestication."""
    groups = []

    for grp_id in sorted(tiles_df['lvl1_group'].unique()):
        grp = tiles_df[tiles_df['lvl1_group'] == grp_id]

        ready_before = int((grp['internal_bsai_total'] == 0).sum())
        blocked_before = len(grp) - ready_before

        # After domestication: ALL tiles are ready (domestication removes all internal sites)
        ready_after = len(grp)
        blocked_after = 0

        groups.append(Lvl1Group(
            group_id=grp_id,
            total_tiles=len(grp),
            ready_before=ready_before,
            blocked_before=blocked_before,
            ready_after=ready_after,
            blocked_after=blocked_after,
            complete_before=blocked_before == 0,
            complete_after=True,  # All complete after domestication
            start=int(grp['start'].min()),
            end=int(grp['end'].max()),
            length=int(grp['end'].max() - grp['start'].min()),
        ))

    return groups


# ═══════════════════════════════════════════════════════════════════
# 4. VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════

def plot_before_after_lvl1(groups: List[Lvl1Group], genome_len: int):
    """Side-by-side comparison of Lvl1 assembly before and after domestication."""
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.5, 0.5],
        vertical_spacing=0.15,
        subplot_titles=[
            'BEFORE domestication — Lvl1 assembly status',
            'AFTER domestication — Lvl1 assembly status (all complete)',
        ],
    )

    # ── Row 1: Before ──
    before_cats = [
        ('Complete', GREEN, [g for g in groups if g.complete_before]),
        ('1-2 blocked', YELLOW, [g for g in groups if not g.complete_before and g.blocked_before <= 2]),
        ('3-4 blocked', ORANGE, [g for g in groups if not g.complete_before and 3 <= g.blocked_before <= 4]),
        ('5+ blocked', RED, [g for g in groups if not g.complete_before and g.blocked_before >= 5]),
    ]

    for cat_name, color, cat_groups in before_cats:
        if not cat_groups:
            continue
        xs, ys, texts = [], [], []
        for g in cat_groups:
            x0, x1 = g.start / 1e6, g.end / 1e6
            xs += [x0, x1, x1, x0, x0, None]
            ys += [0, 0, 1, 1, 0, None]
            hover = "Lvl1-%d | %d/%d ready | %s" % (
                g.group_id, g.ready_before, g.total_tiles,
                "COMPLETE" if g.complete_before else f"{g.blocked_before} blocked",
            )
            texts += [hover] * 6
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill='toself',
            fillcolor=color, line=dict(width=0),
            name=cat_name, text=texts,
            hoverinfo='text', hoveron='fills',
        ), row=1, col=1)

    # ── Row 2: After (all green) ──
    xs, ys, texts = [], [], []
    for g in groups:
        x0, x1 = g.start / 1e6, g.end / 1e6
        xs += [x0, x1, x1, x0, x0, None]
        ys += [0, 0, 1, 1, 0, None]
        hover = "Lvl1-%d | %d/%d ready | COMPLETE" % (
            g.group_id, g.total_tiles, g.total_tiles,
        )
        texts += [hover] * 6
    fig.add_trace(go.Scatter(
        x=xs, y=ys, fill='toself',
        fillcolor=GREEN, line=dict(width=0),
        name='All complete', text=texts,
        hoverinfo='text', hoveron='fills',
        showlegend=True,
    ), row=2, col=1)

    n_before = sum(1 for g in groups if g.complete_before)
    n_after = len(groups)
    fig.update_layout(
        title=f'Lvl1 Assembly: {n_before}/{len(groups)} → {n_after}/{len(groups)} complete after domestication',
        height=450, width=1400,
        legend=dict(orientation='h', y=1.08, x=0.5, xanchor='center'),
        **LAYOUT,
    )
    for r in [1, 2]:
        fig.update_xaxes(range=[0, genome_len / 1e6], **AXIS, row=r, col=1)
        fig.update_yaxes(showticklabels=False, range=[-0.05, 1.05], **AXIS, row=r, col=1)
    fig.update_xaxes(title_text='Genome position (Mb)', row=2, col=1)

    for ann in fig.layout.annotations:
        if ann.font and ann.font.color is None:
            ann.font.color = TEXT_CLR

    save_fig(fig, 'domestication_before_after', height=450)


def plot_domestication_effort(plans: List[DomesticationPlan]):
    """Visualize the domestication effort: primers needed, sub-fragments per tile."""
    # Sub-fragments distribution
    n_frags = [len(p.sub_fragments) for p in plans]
    frag_counts = Counter(n_frags)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            'Sub-fragments per domesticated tile',
            'Domestication effort summary',
        ],
        column_widths=[0.5, 0.5],
    )

    # Bar chart: sub-fragment distribution
    labels = sorted(frag_counts.keys())
    values = [frag_counts[k] for k in labels]
    colors = [YELLOW if k == 2 else ORANGE if k == 3 else RED for k in labels]

    fig.add_trace(go.Bar(
        x=[f'{k} frags' for k in labels],
        y=values,
        marker_color=colors,
        text=values,
        textposition='outside',
        showlegend=False,
    ), row=1, col=1)

    # Summary stats as a table-like bar
    total_tiles = len(plans)
    total_sites = sum(p.n_sites for p in plans)
    total_primers = sum(p.total_primers for p in plans)
    total_subfrags = sum(len(p.sub_fragments) for p in plans)

    categories = ['Tiles to\ndomesticate', 'BsaI sites\nto remove', 'New primers\nneeded', 'Sub-fragment\nPCRs']
    values2 = [total_tiles, total_sites, total_primers, total_subfrags]
    colors2 = [YELLOW, ORANGE, ACCENT, PURPLE]

    fig.add_trace(go.Bar(
        x=categories,
        y=values2,
        marker_color=colors2,
        text=values2,
        textposition='outside',
        showlegend=False,
    ), row=1, col=2)

    fig.update_layout(
        title='Domestication effort overview',
        height=400, width=1400,
        **LAYOUT,
    )
    for c in [1, 2]:
        fig.update_xaxes(**AXIS, row=1, col=c)
        fig.update_yaxes(**AXIS, row=1, col=c)

    for ann in fig.layout.annotations:
        if ann.font and ann.font.color is None:
            ann.font.color = TEXT_CLR

    save_fig(fig, 'domestication_effort', height=400)


def plot_tile_status_after(tiles_df: pd.DataFrame, genome_len: int):
    """Show tile status after domestication — all tiles now ready."""
    fig = go.Figure()

    # All tiles are now green (ready)
    xs, ys, texts = [], [], []
    for _, row in tiles_df.iterrows():
        x0, x1 = row['start'] / 1e6, row['end'] / 1e6
        xs += [x0, x1, x1, x0, x0, None]
        ys += [0, 0, 1, 1, 0, None]
        was_blocked = row['internal_bsai_total'] > 0
        hover = "Tile %d (Lvl1-%d) | %s | %s" % (
            int(row['tile']), int(row['lvl1_group']),
            f"{int(row['start']):,}-{int(row['end']):,}",
            "was blocked → domesticated" if was_blocked else "already ready"
        )
        texts += [hover] * 6

    fig.add_trace(go.Scatter(
        x=xs, y=ys, fill='toself',
        fillcolor=GREEN, line=dict(width=0),
        name='All tiles ready', text=texts,
        hoverinfo='text', hoveron='fills',
    ))

    fig.update_layout(
        title=f'After domestication — all {len(tiles_df)} tiles Golden Gate ready (100%)',
        xaxis_title='Genome position (Mb)',
        height=300, width=1400,
        legend=dict(orientation='h', y=1.12, x=0.5, xanchor='center'),
        **LAYOUT,
    )
    fig.update_xaxes(**AXIS, range=[0, genome_len / 1e6])
    fig.update_yaxes(showticklabels=False, range=[-0.05, 1.05], **AXIS)
    save_fig(fig, 'tiles_after_domestication', height=300)


# ═══════════════════════════════════════════════════════════════════
# 5. MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("EXP_001 — Domestication Primer Design")
    print("=" * 60)

    # Load genome
    record = download_mg1655()
    genome_seq = str(record.seq).upper()
    genome_len = len(genome_seq)
    print(f"Genome: {genome_len:,} bp")

    # Load tile data
    tiles_df = pd.read_csv(DATA_DIR / 'tiles.csv')
    print(f"Tiles loaded: {len(tiles_df)}")

    # ── 1. Parse domestication targets ──
    print("\n" + "=" * 60)
    print("1. PARSING DOMESTICATION TARGETS")
    print("=" * 60)

    targets = []
    for _, row in tiles_df.iterrows():
        n_extra = int(row['extra_domestication'])
        if n_extra == 0:
            continue

        mutations = parse_domestication_details(row['domestication_details'])
        if not mutations:
            continue

        targets.append(DomesticationTarget(
            tile_id=int(row['tile']),
            tile_start=int(row['start']),
            tile_end=int(row['end']),
            tile_length=int(row['length']),
            lvl1_group=int(row['lvl1_group']),
            n_internal_sites=int(row['internal_bsai_total']),
            n_primer_domesticated=int(row['primer_domesticated']),
            n_extra_sites=n_extra,
            mutations=mutations,
            fwd_primer=str(row['fwd_primer']),
            rev_primer=str(row['rev_primer']),
        ))

    print(f"\n  Tiles needing overlap extension PCR: {len(targets)}")
    total_sites = sum(t.n_extra_sites for t in targets)
    print(f"  Total internal BsaI sites to remove: {total_sites}")

    # Also count primer-domesticated tiles
    primer_dom = tiles_df[tiles_df['primer_domesticated'] > 0]
    print(f"  Tiles already domesticated by primer overlap: {len(primer_dom)}")

    # ── 2. Design mutagenic primers ──
    print("\n" + "=" * 60)
    print("2. DESIGNING MUTAGENIC PRIMERS")
    print("=" * 60)

    plans = []
    primer_rows = []

    for target in targets:
        plan = design_mutagenic_primers(target, genome_seq)
        plans.append(plan)

        # Collect primer data for CSV output
        for pp in plan.primer_pairs:
            primer_rows.append({
                'tile': plan.tile_id,
                'lvl1_group': plan.lvl1_group,
                'site_genome_pos': pp.site_pos,
                'original_nt': pp.mutation.original_nt,
                'mutant_nt': pp.mutation.mutant_nt,
                'codon_change': pp.mutation.codon_change,
                'amino_acid': pp.mutation.amino_acid,
                'gene': pp.mutation.gene,
                'mutagenic_fwd': pp.fwd_seq,
                'mutagenic_rev': pp.rev_seq,
                'fwd_tm': round(pp.fwd_tm, 1),
                'rev_tm': round(pp.rev_tm, 1),
                'primer_length': len(pp.fwd_seq),
            })

    primers_df = pd.DataFrame(primer_rows)
    primers_df.to_csv(DATA_DIR / 'domestication_primers.csv', index=False)
    print(f"\n  ✓ domestication_primers.csv ({len(primers_df)} primer pairs)")

    # Sub-fragment summary
    summary_rows = []
    for plan in plans:
        for sf in plan.sub_fragments:
            summary_rows.append({
                'tile': plan.tile_id,
                'lvl1_group': plan.lvl1_group,
                'fragment_index': sf.frag_index,
                'frag_start': sf.start,
                'frag_end': sf.end,
                'frag_length': sf.length,
                'fwd_primer': sf.fwd_primer,
                'rev_primer': sf.rev_primer,
                'fwd_tm': round(sf.fwd_tm, 1),
                'rev_tm': round(sf.rev_tm, 1),
            })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(DATA_DIR / 'domestication_subfragments.csv', index=False)
    print(f"  ✓ domestication_subfragments.csv ({len(summary_df)} sub-fragments)")

    # ── 3. Print statistics ──
    total_new_primers = sum(p.total_primers for p in plans)
    total_subfrags = sum(len(p.sub_fragments) for p in plans)
    frag_counts = Counter(len(p.sub_fragments) for p in plans)

    print(f"\n  Total new mutagenic primers: {total_new_primers}")
    print(f"  Total sub-fragment PCRs: {total_subfrags}")
    print(f"  Sub-fragments per tile:")
    for k in sorted(frag_counts.keys()):
        print(f"    {k} fragments: {frag_counts[k]} tiles")

    # Primer Tm stats
    all_tms = [pp.fwd_tm for plan in plans for pp in plan.primer_pairs] + \
              [pp.rev_tm for plan in plans for pp in plan.primer_pairs]
    print(f"\n  Mutagenic primer Tm: {np.mean(all_tms):.1f}°C ± {np.std(all_tms):.1f}°C")
    print(f"    Range: {min(all_tms):.1f}–{max(all_tms):.1f}°C")

    # ── 4. Assembly analysis — before vs after ──
    print("\n" + "=" * 60)
    print("3. LVL1 ASSEMBLY — BEFORE vs AFTER DOMESTICATION")
    print("=" * 60)

    groups = analyze_before_after(tiles_df)

    n_complete_before = sum(1 for g in groups if g.complete_before)
    n_complete_after = sum(1 for g in groups if g.complete_after)
    n_total = len(groups)

    bp_before = sum(g.length for g in groups if g.complete_before)
    bp_after = sum(g.length for g in groups if g.complete_after)

    print(f"\n  Lvl1 groups: {n_total}")
    print(f"  Complete BEFORE domestication: {n_complete_before}/{n_total} ({100*n_complete_before/n_total:.0f}%)")
    print(f"  Complete AFTER  domestication: {n_complete_after}/{n_total} ({100*n_complete_after/n_total:.0f}%)")
    print(f"\n  Assemblable genome BEFORE: {bp_before:,} bp ({100*bp_before/genome_len:.1f}%)")
    print(f"  Assemblable genome AFTER:  {bp_after:,} bp ({100*bp_after/genome_len:.1f}%)")

    # Tiles summary
    ready_before = int((tiles_df['internal_bsai_total'] == 0).sum())
    print(f"\n  Tiles ready BEFORE: {ready_before}/{len(tiles_df)} ({100*ready_before/len(tiles_df):.0f}%)")
    print(f"  Tiles ready AFTER:  {len(tiles_df)}/{len(tiles_df)} (100%)")

    # ── 5. Visualizations ──
    print("\n" + "=" * 60)
    print("4. GENERATING VISUALIZATIONS")
    print("=" * 60)

    plot_before_after_lvl1(groups, genome_len)
    plot_domestication_effort(plans)
    plot_tile_status_after(tiles_df, genome_len)

    # ── 6. Summary ──
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Tiles requiring domestication: {len(targets)} (+ {len(primer_dom)} via primer overlap)")
    print(f"  Internal BsaI sites to remove: {total_sites}")
    print(f"  New mutagenic primers to order: {total_new_primers}")
    print(f"  Sub-fragment PCRs needed: {total_subfrags}")
    print(f"  Overlap extension assemblies: {len(targets)}")
    print(f"\n  RESULT: {n_complete_before} → {n_complete_after} of {n_total} Lvl1 groups become assemblable")
    print(f"  RESULT: {100*bp_before/genome_len:.1f}% → {100*bp_after/genome_len:.1f}% genome coverage")
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
