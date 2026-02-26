#!/usr/bin/env python3
"""
V2 Lvl1 Group Analysis — Distribution of lengths, content diversity, and assembly readiness.
Generates a comprehensive multi-panel figure.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────────────────
groups = pd.read_csv(Path(__file__).parent / "data" / "v2_lvl1_groups.csv")
tiles = pd.read_csv(Path(__file__).parent / "data" / "v2_tiles.csv")

# ── Compute per-group metrics ──────────────────────────────────────────────────
group_stats = []
for _, g in groups.iterrows():
    gtiles = tiles[tiles["lvl1_group"] == g["id"]]
    group_stats.append({
        "id": g["id"],
        "length": g["length"],
        "total_tiles": g["total_tiles"],
        "ready_tiles": g["ready_tiles"],
        "blocked_tiles": g["blocked_tiles_count"],
        "readiness_pct": g["ready_tiles"] / g["total_tiles"] * 100,
        "mean_gc": gtiles["gc_content"].mean(),
        "std_gc": gtiles["gc_content"].std(),
        "min_gc": gtiles["gc_content"].min(),
        "max_gc": gtiles["gc_content"].max(),
        "mean_tile_size": gtiles["length"].mean(),
        "std_tile_size": gtiles["length"].std(),
        "min_tile_size": gtiles["length"].min(),
        "max_tile_size": gtiles["length"].max(),
        "total_bsai": gtiles["internal_bsai"].sum(),
        "max_bsai_per_tile": gtiles["internal_bsai"].max(),
    })

gdf = pd.DataFrame(group_stats)

# ── Print summary statistics ───────────────────────────────────────────────────
print("=" * 70)
print("V2 Lvl1 GROUP ANALYSIS")
print("=" * 70)

print(f"\nTotal groups: {len(gdf)}")
print(f"Total tiles:  {tiles.shape[0]}")

print("\n── Group Length Distribution ──")
print(f"  Mean:   {gdf['length'].mean():,.0f} bp")
print(f"  Median: {gdf['length'].median():,.0f} bp")
print(f"  Std:    {gdf['length'].std():,.0f} bp")
print(f"  Min:    {gdf['length'].min():,.0f} bp (Group {gdf.loc[gdf['length'].idxmin(), 'id']})")
print(f"  Max:    {gdf['length'].max():,.0f} bp (Group {gdf.loc[gdf['length'].idxmax(), 'id']})")

print("\n── GC Content per Group ──")
print(f"  Mean across groups: {gdf['mean_gc'].mean():.1f}%")
print(f"  Range of group means: {gdf['mean_gc'].min():.1f}% – {gdf['mean_gc'].max():.1f}%")
print(f"  Overall tile GC range: {tiles['gc_content'].min():.1f}% – {tiles['gc_content'].max():.1f}%")

print("\n── Assembly Readiness per Group ──")
print(f"  Mean readiness: {gdf['readiness_pct'].mean():.1f}%")
print(f"  Most ready:  Group {gdf.loc[gdf['readiness_pct'].idxmax(), 'id']} ({gdf['readiness_pct'].max():.0f}%)")
print(f"  Least ready: Group {gdf.loc[gdf['readiness_pct'].idxmin(), 'id']} ({gdf['readiness_pct'].min():.0f}%)")

print("\n── BsaI Domestication Burden ──")
print(f"  Total internal BsaI sites: {gdf['total_bsai'].sum()}")
print(f"  Mean BsaI sites per group: {gdf['total_bsai'].mean():.1f}")
print(f"  Max BsaI sites in one group: {gdf['total_bsai'].max()} (Group {gdf.loc[gdf['total_bsai'].idxmax(), 'id']})")

print("\n── Tile Size Diversity Within Groups ──")
print(f"  Mean intra-group tile std: {gdf['std_tile_size'].mean():,.0f} bp")
print(f"  Mean tile size:           {tiles['length'].mean():,.0f} bp")
print(f"  Smallest tile overall:    {tiles['length'].min():,} bp")
print(f"  Largest tile overall:     {tiles['length'].max():,} bp")

# ── Generate Figure ────────────────────────────────────────────────────────────
plt.style.use("dark_background")
fig = plt.figure(figsize=(18, 14))
fig.suptitle("V2 Lvl1 Group Analysis — 46 Groups, 686 Tiles", 
             fontsize=16, fontweight="bold", color="#e6edf3", y=0.98)

gs = gridspec.GridSpec(3, 3, hspace=0.35, wspace=0.3,
                       left=0.06, right=0.96, top=0.93, bottom=0.05)

GREEN = "#3fb950"
BLUE = "#58a6ff"
ORANGE = "#d29922"
RED = "#f85149"
PURPLE = "#bc8cff"
GRAY = "#8b949e"

# 1. Group length distribution (histogram)
ax1 = fig.add_subplot(gs[0, 0])
ax1.hist(gdf["length"] / 1000, bins=15, color=BLUE, alpha=0.8, edgecolor="#0d1117")
ax1.axvline(gdf["length"].mean() / 1000, color=ORANGE, ls="--", lw=1.5, label=f'Mean: {gdf["length"].mean()/1000:.1f} kb')
ax1.set_xlabel("Group Length (kb)", fontsize=10)
ax1.set_ylabel("Count", fontsize=10)
ax1.set_title("Group Length Distribution", fontsize=11, fontweight="bold")
ax1.legend(fontsize=8)

# 2. Group length by position (bar)
ax2 = fig.add_subplot(gs[0, 1])
colors2 = [GREEN if l >= 97000 else RED for l in gdf["length"]]
ax2.bar(gdf["id"], gdf["length"] / 1000, color=colors2, alpha=0.8, width=0.7)
ax2.axhline(100, color=ORANGE, ls="--", lw=1, alpha=0.6, label="100 kb target")
ax2.set_xlabel("Lvl1 Group ID", fontsize=10)
ax2.set_ylabel("Length (kb)", fontsize=10)
ax2.set_title("Length per Lvl1 Group", fontsize=11, fontweight="bold")
ax2.legend(fontsize=8)
ax2.set_xlim(-1, 46)

# 3. Readiness per group (stacked bar)
ax3 = fig.add_subplot(gs[0, 2])
ax3.bar(gdf["id"], gdf["ready_tiles"], color=GREEN, alpha=0.8, label="GG-ready")
ax3.bar(gdf["id"], gdf["blocked_tiles"], bottom=gdf["ready_tiles"], color=RED, alpha=0.6, label="Blocked")
ax3.set_xlabel("Lvl1 Group ID", fontsize=10)
ax3.set_ylabel("Tiles", fontsize=10)
ax3.set_title("Assembly Readiness per Group", fontsize=11, fontweight="bold")
ax3.legend(fontsize=8)
ax3.set_xlim(-1, 46)

# 4. GC content per group (box-whisker approach using mean+std)
ax4 = fig.add_subplot(gs[1, 0])
ax4.errorbar(gdf["id"], gdf["mean_gc"], yerr=gdf["std_gc"], 
             fmt="o", color=BLUE, ecolor=GRAY, elinewidth=1, capsize=2, markersize=4)
ax4.axhline(tiles["gc_content"].mean(), color=ORANGE, ls="--", lw=1, alpha=0.6, 
            label=f'Genome mean: {tiles["gc_content"].mean():.1f}%')
ax4.set_xlabel("Lvl1 Group ID", fontsize=10)
ax4.set_ylabel("GC Content (%)", fontsize=10)
ax4.set_title("GC Content per Group (mean ± std)", fontsize=11, fontweight="bold")
ax4.legend(fontsize=8)
ax4.set_xlim(-1, 46)

# 5. GC content histogram of all tiles
ax5 = fig.add_subplot(gs[1, 1])
ax5.hist(tiles["gc_content"], bins=30, color=PURPLE, alpha=0.7, edgecolor="#0d1117")
ax5.axvline(tiles["gc_content"].mean(), color=ORANGE, ls="--", lw=1.5, 
            label=f'Mean: {tiles["gc_content"].mean():.1f}%')
ax5.set_xlabel("GC Content (%)", fontsize=10)
ax5.set_ylabel("Tile Count", fontsize=10)
ax5.set_title("Tile GC Content Distribution", fontsize=11, fontweight="bold")
ax5.legend(fontsize=8)

# 6. Tile size distribution
ax6 = fig.add_subplot(gs[1, 2])
ax6.hist(tiles["length"] / 1000, bins=30, color=GREEN, alpha=0.7, edgecolor="#0d1117")
ax6.axvline(tiles["length"].mean() / 1000, color=ORANGE, ls="--", lw=1.5,
            label=f'Mean: {tiles["length"].mean()/1000:.1f} kb')
ax6.set_xlabel("Tile Size (kb)", fontsize=10)
ax6.set_ylabel("Count", fontsize=10)
ax6.set_title("Tile Size Distribution", fontsize=11, fontweight="bold")
ax6.legend(fontsize=8)

# 7. BsaI burden per group
ax7 = fig.add_subplot(gs[2, 0])
ax7.bar(gdf["id"], gdf["total_bsai"], color=RED, alpha=0.7, width=0.7)
ax7.set_xlabel("Lvl1 Group ID", fontsize=10)
ax7.set_ylabel("Internal BsaI Sites", fontsize=10)
ax7.set_title("Domestication Burden per Group", fontsize=11, fontweight="bold")
ax7.set_xlim(-1, 46)

# 8. Readiness % heatmap-style bar
ax8 = fig.add_subplot(gs[2, 1])
readiness_colors = [GREEN if r >= 80 else ORANGE if r >= 50 else RED for r in gdf["readiness_pct"]]
ax8.bar(gdf["id"], gdf["readiness_pct"], color=readiness_colors, alpha=0.8, width=0.7)
ax8.axhline(gdf["readiness_pct"].mean(), color=BLUE, ls="--", lw=1, 
            label=f'Mean: {gdf["readiness_pct"].mean():.0f}%')
ax8.set_xlabel("Lvl1 Group ID", fontsize=10)
ax8.set_ylabel("Readiness (%)", fontsize=10)
ax8.set_title("GG-Ready Percentage per Group", fontsize=11, fontweight="bold")
ax8.legend(fontsize=8)
ax8.set_ylim(0, 105)
ax8.set_xlim(-1, 46)

# 9. Tile size variability within groups
ax9 = fig.add_subplot(gs[2, 2])
ax9.errorbar(gdf["id"], gdf["mean_tile_size"] / 1000, 
             yerr=gdf["std_tile_size"] / 1000,
             fmt="s", color=PURPLE, ecolor=GRAY, elinewidth=1, capsize=2, markersize=4)
ax9.set_xlabel("Lvl1 Group ID", fontsize=10)
ax9.set_ylabel("Tile Size (kb)", fontsize=10)
ax9.set_title("Tile Size Variability per Group", fontsize=11, fontweight="bold")
ax9.set_xlim(-1, 46)

# Save
out = Path(__file__).parent / "data" / "v2_lvl1_analysis.png"
plt.savefig(out, dpi=180, facecolor="#0d1117")
plt.close()
print(f"\n✅ Figure saved to {out}")
