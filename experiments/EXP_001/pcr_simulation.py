#!/usr/bin/env python3
"""
pcr_simulation.py — Simulate PCR amplification and Golden Gate assembly feasibility

Reads tiles.csv from the primer design step, then:
  1. Simulates in-silico PCR for each tile
  2. Classifies tiles as "ready" (0 internal BsaI) vs "needs domestication"
  3. Groups into Lvl1 assemblies and identifies complete vs incomplete groups
  4. Generates visualizations of genome coverage and missing regions

Usage:
    python3 pcr_simulation.py
"""

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

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

# Plotly theme
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
# 1. PCR SIMULATION
# ═══════════════════════════════════════════════════════════════════

def simulate_pcr(tiles_df: pd.DataFrame, genome_seq: str) -> pd.DataFrame:
    """
    Simulate in-silico PCR for each tile.
    Verify amplicon matches expected coordinates and check for internal BsaI sites.
    """
    results = []
    genome_len = len(genome_seq)

    for _, row in tiles_df.iterrows():
        start, end = int(row['start']), int(row['end'])
        length = end - start

        # Extract amplicon sequence
        amplicon = genome_seq[start:end].upper()

        # Count internal BsaI sites (the ones BsaI would cut during Golden Gate)
        # We need to check for sites that are NOT at the very ends (primer overhangs)
        internal_fwd = 0
        internal_rev = 0
        positions = []

        # Check forward sites (GGTCTC)
        pos = 0
        while True:
            pos = amplicon.find(BSAI_SITE, pos)
            if pos == -1:
                break
            positions.append(('fwd', start + pos))
            internal_fwd += 1
            pos += 1

        # Check reverse sites (GAGACC)
        pos = 0
        while True:
            pos = amplicon.find(BSAI_RC, pos)
            if pos == -1:
                break
            positions.append(('rev', start + pos))
            internal_rev += 1
            pos += 1

        total_internal = internal_fwd + internal_rev
        # "Ready" = can go straight into Golden Gate without being cut internally
        ready = total_internal == 0

        results.append({
            'tile': int(row['tile']),
            'start': start,
            'end': end,
            'length': length,
            'lvl1_group': int(row['lvl1_group']),
            'amplicon_gc': 100 * (amplicon.count('G') + amplicon.count('C')) / len(amplicon),
            'internal_bsai_fwd': internal_fwd,
            'internal_bsai_rev': internal_rev,
            'internal_bsai_total': total_internal,
            'pcr_ready': ready,
            'gg_ready': ready,  # Golden Gate ready (no internal cuts)
            'site_positions': '; '.join(f"{s[0]}:{s[1]}" for s in positions) if positions else 'none',
        })

    return pd.DataFrame(results)


# ═══════════════════════════════════════════════════════════════════
# 2. LVL1 ASSEMBLY ANALYSIS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Lvl1Group:
    group_id: int
    tiles: List[int]
    start: int
    end: int
    length: int
    total_tiles: int
    ready_tiles: int
    blocked_tiles: int
    blocked_tile_ids: List[int]
    complete: bool
    coverage_bp: int = 0
    missing_bp: int = 0


def analyze_lvl1_groups(pcr_df: pd.DataFrame) -> List[Lvl1Group]:
    """Analyze each Lvl1 group for completeness."""
    groups = []

    for grp_id in sorted(pcr_df['lvl1_group'].unique()):
        grp = pcr_df[pcr_df['lvl1_group'] == grp_id]
        ready = grp[grp['gg_ready']]
        blocked = grp[~grp['gg_ready']]

        g = Lvl1Group(
            group_id=grp_id,
            tiles=grp['tile'].tolist(),
            start=int(grp['start'].min()),
            end=int(grp['end'].max()),
            length=int(grp['end'].max() - grp['start'].min()),
            total_tiles=len(grp),
            ready_tiles=len(ready),
            blocked_tiles=len(blocked),
            blocked_tile_ids=blocked['tile'].tolist(),
            complete=len(blocked) == 0,
            coverage_bp=int(ready['length'].sum()),
            missing_bp=int(blocked['length'].sum()),
        )
        groups.append(g)

    return groups


# ═══════════════════════════════════════════════════════════════════
# 3. VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════

def plot_pcr_overview(pcr_df: pd.DataFrame, genome_len: int):
    """Tile-level PCR results: ready vs blocked — filled shapes for visibility."""
    fig = go.Figure()

    # Group tiles by status for fewer traces with filled shapes
    categories = [
        ('Ready (0 sites)', GREEN, pcr_df['gg_ready']),
        ('1 site',          YELLOW, pcr_df['internal_bsai_total'] == 1),
        ('2 sites',         ORANGE, pcr_df['internal_bsai_total'] == 2),
        ('3+ sites',        RED,    pcr_df['internal_bsai_total'] >= 3),
    ]

    for cat_name, color, mask in categories:
        subset = pcr_df[mask]
        if subset.empty:
            continue
        xs, ys, texts = [], [], []
        for _, row in subset.iterrows():
            x0, x1 = row['start'] / 1e6, row['end'] / 1e6
            xs += [x0, x1, x1, x0, x0, None]
            ys += [0, 0, 1, 1, 0, None]
            hover = "Tile %d | %s-%s (%s bp) | BsaI: %d | GC: %.1f%%" % (
                int(row['tile']),
                f"{int(row['start']):,}", f"{int(row['end']):,}",
                f"{int(row['length']):,}",
                int(row['internal_bsai_total']),
                row['amplicon_gc'],
            )
            texts += [hover] * 6

        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill='toself',
            fillcolor=color, line=dict(width=0),
            name=cat_name, text=texts,
            hoverinfo='text', hoveron='fills',
        ))

    n_ready = int(pcr_df['gg_ready'].sum())
    n_total = len(pcr_df)
    fig.update_layout(
        title=f'In-silico PCR simulation — {n_ready}/{n_total} tiles Golden Gate ready ({100*n_ready/n_total:.0f}%)',
        xaxis_title='Genome position (Mb)',
        height=300, width=1400,
        legend=dict(orientation='h', y=1.12, x=0.5, xanchor='center'),
        **LAYOUT,
    )
    fig.update_xaxes(**AXIS, range=[0, genome_len / 1e6])
    fig.update_yaxes(showticklabels=False, range=[-0.05, 1.05], **AXIS)
    save_fig(fig, 'pcr_simulation', height=300)


def plot_lvl1_assemblies(groups: List[Lvl1Group], pcr_df: pd.DataFrame, genome_len: int):
    """Lvl1 assembly map — filled shapes for visibility."""
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.4, 0.6],
        vertical_spacing=0.12,
        subplot_titles=[
            'Lvl1 assembly groups — genome coverage',
            'Individual tile status within each Lvl1 group',
        ],
    )

    # ── Row 1: Lvl1 groups — categorized ──
    lvl1_cats = [
        ('Complete', GREEN, [g for g in groups if g.complete]),
        ('1-2 blocked', YELLOW, [g for g in groups if not g.complete and g.blocked_tiles <= 2]),
        ('3-4 blocked', ORANGE, [g for g in groups if not g.complete and 3 <= g.blocked_tiles <= 4]),
        ('5+ blocked', RED, [g for g in groups if not g.complete and g.blocked_tiles >= 5]),
    ]

    for cat_name, color, cat_groups in lvl1_cats:
        if not cat_groups:
            continue
        xs, ys, texts = [], [], []
        for g in cat_groups:
            x0, x1 = g.start / 1e6, g.end / 1e6
            xs += [x0, x1, x1, x0, x0, None]
            ys += [0, 0, 1, 1, 0, None]
            status = "COMPLETE" if g.complete else "INCOMPLETE"
            hover = "Lvl1-%d | %s-%s (%s bp) | %d/%d ready | %s" % (
                g.group_id, f"{g.start:,}", f"{g.end:,}", f"{g.length:,}",
                g.ready_tiles, g.total_tiles, status,
            )
            texts += [hover] * 6
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill='toself',
            fillcolor=color, line=dict(width=0),
            name=cat_name, text=texts,
            hoverinfo='text', hoveron='fills',
        ), row=1, col=1)

    # Group number labels
    for g in groups:
        mid = (g.start + g.end) / 2 / 1e6
        fig.add_annotation(
            x=mid, y=0.5,
            text=f"<b>{g.group_id}</b>",
            showarrow=False,
            font=dict(size=7, color='white'),
            xref='x', yref='y',
        )

    # ── Row 2: Individual tiles ──
    tile_cats = [
        ('Ready tile', GREEN, pcr_df[pcr_df['gg_ready']]),
        ('Blocked tile', RED, pcr_df[~pcr_df['gg_ready']]),
    ]

    for cat_name, color, subset in tile_cats:
        if subset.empty:
            continue
        xs, ys, texts = [], [], []
        for _, row in subset.iterrows():
            x0, x1 = row['start'] / 1e6, row['end'] / 1e6
            xs += [x0, x1, x1, x0, x0, None]
            ys += [0, 0, 1, 1, 0, None]
            sites = int(row['internal_bsai_total'])
            hover = "T%d (Lvl1-%d) | %s-%s | %s" % (
                int(row['tile']), int(row['lvl1_group']),
                f"{int(row['start']):,}", f"{int(row['end']):,}",
                "Ready" if row['gg_ready'] else f"{sites} BsaI sites",
            )
            texts += [hover] * 6
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill='toself',
            fillcolor=color, line=dict(width=0),
            name=cat_name, text=texts,
            hoverinfo='text', hoveron='fills',
            showlegend=True,
        ), row=2, col=1)

    n_complete = sum(1 for g in groups if g.complete)
    fig.update_layout(
        title=f'Lvl1 Assembly Map — {n_complete}/{len(groups)} groups complete',
        height=450, width=1400,
        legend=dict(orientation='h', y=1.08, x=0.5, xanchor='center'),
        **LAYOUT,
    )
    fig.update_xaxes(title_text='Genome position (Mb)', row=2, col=1, **AXIS,
                     range=[0, genome_len / 1e6])
    fig.update_xaxes(**AXIS, row=1, col=1, range=[0, genome_len / 1e6])
    fig.update_yaxes(showticklabels=False, range=[-0.05, 1.05], **AXIS, row=1, col=1)
    fig.update_yaxes(showticklabels=False, range=[-0.05, 1.05], **AXIS, row=2, col=1)

    for ann in fig.layout.annotations:
        if ann.font and ann.font.color is None:
            ann.font.color = TEXT_CLR

    save_fig(fig, 'lvl1_assembly_map', height=450)


def plot_genome_coverage(pcr_df: pd.DataFrame, genome_len: int):
    """
    Circular-style overview: what fraction of the genome is captured
    without any domestication needed.
    """
    ready = pcr_df[pcr_df['gg_ready']]
    blocked = pcr_df[~pcr_df['gg_ready']]

    ready_bp = int(ready['length'].sum())
    blocked_bp = int(blocked['length'].sum())
    total_bp = ready_bp + blocked_bp

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'domain'}, {'type': 'xy'}]],
        subplot_titles=['Genome coverage without domestication', 'Blocked tiles — internal BsaI site count'],
        horizontal_spacing=0.08,
    )

    # Donut chart
    fig.add_trace(go.Pie(
        values=[ready_bp, blocked_bp],
        labels=['Captured directly', 'Needs domestication'],
        marker=dict(colors=[GREEN, RED], line=dict(color=DARK_BG, width=3)),
        hole=0.65,
        textinfo='percent',
        textfont=dict(size=14, color='white'),
        hovertemplate='%{label}<br>%{value:,} bp (%{percent})<extra></extra>',
    ), row=1, col=1)

    fig.add_annotation(
        text=f"<b>{ready_bp/1e6:.2f} Mb</b><br>captured",
        x=0.195, y=0.5, font=dict(size=16, color=GREEN),
        showarrow=False, xref='paper', yref='paper',
    )

    # Bar chart: blocked tiles by site count
    site_counts = blocked['internal_bsai_total'].value_counts().sort_index()
    colors_bar = [YELLOW if n == 1 else ORANGE if n == 2 else RED for n in site_counts.index]

    fig.add_trace(go.Bar(
        x=[f'{n} site{"s" if n > 1 else ""}' for n in site_counts.index],
        y=site_counts.values,
        marker_color=colors_bar,
        marker_line=dict(color=DARK_BG, width=1),
        text=site_counts.values,
        textposition='outside',
        textfont=dict(color=TEXT_CLR),
        hovertemplate='%{x}: %{y} tiles<extra></extra>',
    ), row=1, col=2)

    fig.update_yaxes(title_text='Number of tiles', row=1, col=2, **AXIS)
    fig.update_xaxes(row=1, col=2, **AXIS)

    fig.update_layout(
        title=f'Genome capture analysis — {100*ready_bp/total_bp:.1f}% directly clonable',
        height=400, width=1200, showlegend=False,
        **LAYOUT,
    )
    for ann in fig.layout.annotations:
        if ann.font and ann.font.color is None:
            ann.font.color = TEXT_CLR

    save_fig(fig, 'genome_coverage', width=1200, height=400)


def plot_missing_detail(groups: List[Lvl1Group], pcr_df: pd.DataFrame):
    """Detailed view of incomplete Lvl1 groups — filled shapes for visibility."""
    incomplete = [g for g in groups if not g.complete]
    if not incomplete:
        print("  All Lvl1 groups are complete — no missing tiles!")
        return

    # Limit to showing at most 20 groups
    show = incomplete[:20]
    n_show = len(show)

    fig = go.Figure()

    # Draw tiles as filled scatter rectangles, each group on its own y-band
    # We'll use numeric y and set labels via tick text
    y_labels = []
    y_positions = []

    # Build traces per status category across all groups
    cat_data = {
        'Ready':    {'color': GREEN,  'opacity': 0.35, 'xs': [], 'ys': [], 'texts': []},
        '1 site':   {'color': YELLOW, 'opacity': 1.0,  'xs': [], 'ys': [], 'texts': []},
        '2 sites':  {'color': ORANGE, 'opacity': 1.0,  'xs': [], 'ys': [], 'texts': []},
        '3+ sites': {'color': RED,    'opacity': 1.0,  'xs': [], 'ys': [], 'texts': []},
    }

    for i, g in enumerate(reversed(show)):
        y_label = f"Lvl1-{g.group_id}"
        y_labels.append(y_label)
        y_positions.append(i)

        grp_tiles = pcr_df[pcr_df['lvl1_group'] == g.group_id].sort_values('start')
        group_start = g.start
        y_lo = i - 0.4
        y_hi = i + 0.4

        for _, row in grp_tiles.iterrows():
            ready = row['gg_ready']
            sites = int(row['internal_bsai_total'])
            x0 = (row['start'] - group_start) / 1e3
            x1 = (row['end'] - group_start) / 1e3

            hover = "T%d | %s-%s (%s bp) | BsaI: %d | %s" % (
                int(row['tile']),
                f"{int(row['start']):,}", f"{int(row['end']):,}",
                f"{int(row['length']):,}", sites,
                "Ready" if ready else "BLOCKED",
            )

            if ready:
                cat = 'Ready'
            elif sites == 1:
                cat = '1 site'
            elif sites == 2:
                cat = '2 sites'
            else:
                cat = '3+ sites'

            cat_data[cat]['xs'] += [x0, x1, x1, x0, x0, None]
            cat_data[cat]['ys'] += [y_lo, y_lo, y_hi, y_hi, y_lo, None]
            cat_data[cat]['texts'] += [hover] * 6

    for cat_name, d in cat_data.items():
        if not d['xs']:
            continue
        fig.add_trace(go.Scatter(
            x=d['xs'], y=d['ys'], fill='toself',
            fillcolor=d['color'], line=dict(width=0),
            opacity=d['opacity'],
            name=cat_name, text=d['texts'],
            hoverinfo='text', hoveron='fills',
        ))

    fig_height = max(350, 80 + n_show * 40)
    fig.update_layout(
        title=f'Incomplete Lvl1 groups — blocked tiles highlighted ({len(incomplete)} groups)',
        xaxis_title='Position within Lvl1 group (kb)',
        height=fig_height, width=1400,
        legend=dict(orientation='h', y=1.04, x=0.5, xanchor='center'),
        **LAYOUT,
    )
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(
        tickvals=y_positions, ticktext=y_labels,
        **AXIS,
    )

    save_fig(fig, 'incomplete_lvl1_detail', height=fig_height)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXP_001 — PCR Simulation & Assembly Feasibility")
    print("=" * 60)

    # Load genome
    record = download_mg1655()
    genome_seq = str(record.seq).upper()
    genome_len = len(genome_seq)
    print(f"Genome: {genome_len:,} bp")

    # Load tiles
    tiles_df = pd.read_csv(DATA_DIR / 'tiles.csv')
    print(f"Tiles loaded: {len(tiles_df)}")

    # ── 1. Simulate PCR ──
    print(f"\n{'='*60}")
    print(f"1. IN-SILICO PCR SIMULATION")
    print(f"{'='*60}")

    pcr_df = simulate_pcr(tiles_df, genome_seq)

    n_ready = pcr_df['gg_ready'].sum()
    n_blocked = len(pcr_df) - n_ready
    ready_bp = int(pcr_df[pcr_df['gg_ready']]['length'].sum())
    blocked_bp = int(pcr_df[~pcr_df['gg_ready']]['length'].sum())

    print(f"\n  PCR products: {len(pcr_df)} amplicons")
    print(f"  Total amplified: {(ready_bp + blocked_bp)/1e6:.2f} Mb ({100*(ready_bp+blocked_bp)/genome_len:.1f}% of genome)")
    print(f"\n  Golden Gate ready (0 internal BsaI sites):")
    print(f"    {n_ready} tiles ({100*n_ready/len(pcr_df):.1f}%)")
    print(f"    {ready_bp:,} bp ({100*ready_bp/genome_len:.1f}% of genome)")
    print(f"\n  Needs domestication:")
    print(f"    {n_blocked} tiles ({100*n_blocked/len(pcr_df):.1f}%)")
    print(f"    {blocked_bp:,} bp ({100*blocked_bp/genome_len:.1f}% of genome)")

    # Breakdown by site count
    print(f"\n  Blocked tile breakdown:")
    blocked = pcr_df[~pcr_df['gg_ready']]
    for n_sites in sorted(blocked['internal_bsai_total'].unique()):
        count = len(blocked[blocked['internal_bsai_total'] == n_sites])
        bp = int(blocked[blocked['internal_bsai_total'] == n_sites]['length'].sum())
        print(f"    {n_sites} sites: {count} tiles ({bp:,} bp)")

    # GC content stats
    gc = pcr_df['amplicon_gc']
    print(f"\n  Amplicon GC content: {gc.mean():.1f}% ± {gc.std():.1f}%")
    print(f"    Range: {gc.min():.1f}% – {gc.max():.1f}%")

    # ── 2. Lvl1 assembly analysis ──
    print(f"\n{'='*60}")
    print(f"2. LVL1 ASSEMBLY ANALYSIS")
    print(f"{'='*60}")

    groups = analyze_lvl1_groups(pcr_df)

    n_complete = sum(1 for g in groups if g.complete)
    n_incomplete = len(groups) - n_complete

    print(f"\n  Total Lvl1 groups: {len(groups)}")
    print(f"  Complete (all tiles ready): {n_complete} ({100*n_complete/len(groups):.0f}%)")
    print(f"  Incomplete (≥1 blocked tile): {n_incomplete} ({100*n_incomplete/len(groups):.0f}%)")

    # Coverage by complete groups
    complete_bp = sum(g.length for g in groups if g.complete)
    incomplete_bp = sum(g.length for g in groups if not g.complete)
    print(f"\n  Genome covered by complete Lvl1 groups:")
    print(f"    {complete_bp:,} bp ({100*complete_bp/genome_len:.1f}%)")
    print(f"  Genome in incomplete Lvl1 groups:")
    print(f"    {incomplete_bp:,} bp ({100*incomplete_bp/genome_len:.1f}%)")

    # Detail for incomplete groups
    incomplete_groups = [g for g in groups if not g.complete]
    if incomplete_groups:
        print(f"\n  {'─'*50}")
        print(f"  INCOMPLETE LVL1 GROUPS:")
        print(f"  {'─'*50}")
        print(f"  {'Group':>6s}  {'Start':>10s}  {'End':>10s}  {'Ready':>6s}  {'Blocked':>8s}  Blocked tiles")
        print(f"  {'─'*6}  {'─'*10}  {'─'*10}  {'─'*6}  {'─'*8}  {'─'*30}")

        for g in incomplete_groups:
            blocked_detail = []
            for tid in g.blocked_tile_ids:
                row = pcr_df[pcr_df['tile'] == tid].iloc[0]
                blocked_detail.append(f"T{tid}({int(row['internal_bsai_total'])}s)")

            print(f"  {g.group_id:6d}  {g.start:10,}  {g.end:10,}  "
                  f"{g.ready_tiles:3d}/{g.total_tiles:2d}  "
                  f"{g.blocked_tiles:8d}  {', '.join(blocked_detail)}")

    # ── 3. Save PCR results ──
    pcr_df.to_csv(DATA_DIR / 'pcr_simulation.csv', index=False)
    print(f"\n  ✓ pcr_simulation.csv")

    # Lvl1 summary
    lvl1_rows = []
    for g in groups:
        lvl1_rows.append({
            'group': g.group_id,
            'start': g.start,
            'end': g.end,
            'length': g.length,
            'total_tiles': g.total_tiles,
            'ready_tiles': g.ready_tiles,
            'blocked_tiles': g.blocked_tiles,
            'complete': g.complete,
            'coverage_bp': g.coverage_bp,
            'missing_bp': g.missing_bp,
            'blocked_tile_ids': ', '.join(str(t) for t in g.blocked_tile_ids) if g.blocked_tile_ids else '',
        })
    pd.DataFrame(lvl1_rows).to_csv(DATA_DIR / 'lvl1_assembly_summary.csv', index=False)
    print(f"  ✓ lvl1_assembly_summary.csv")

    # ── 4. Visualizations ──
    print(f"\n{'='*60}")
    print(f"3. GENERATING VISUALIZATIONS")
    print(f"{'='*60}")

    plot_pcr_overview(pcr_df, genome_len)
    plot_lvl1_assemblies(groups, pcr_df, genome_len)
    plot_genome_coverage(pcr_df, genome_len)
    plot_missing_detail(groups, pcr_df)

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"  {n_ready}/{len(pcr_df)} tiles can be cloned directly ({100*n_ready/len(pcr_df):.0f}%)")
    print(f"  {n_complete}/{len(groups)} Lvl1 groups fully assemblable ({100*n_complete/len(groups):.0f}%)")
    print(f"  {ready_bp/1e6:.2f} Mb captured without domestication ({100*ready_bp/genome_len:.1f}%)")
    print(f"  {blocked_bp/1e6:.2f} Mb needs domestication ({100*blocked_bp/genome_len:.1f}%)")
    print(f"\n{'='*60}")
    print(f"DONE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
