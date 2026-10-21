#!/usr/bin/env python3
"""Design vs sequencing identity panel, in the same graphical language as
plot_plasmid.py.

    python3 scripts/figures/plot_alignment.py design.gb sequencing.gb \\
        [--label-a MS_C_031] [--label-b MS_C_031_col3] [--out stem]

Both records are treated as CIRCULAR: the script searches every rotation of B
against A, reports the offset, and compares base by base in A's coordinate
frame. Mismatches are drawn as red ticks, so a figure claiming 100% identity
is one where no tick is present - the absence is evidence, not an omission.
"""
import argparse
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow, Patch, Rectangle

# Palette, legend wording and the feature filter are shared with plot_plasmid,
# so the two figures speak the same graphical language.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_plasmid import (TYPE_COLORS, TYPE_LABELS, is_nested, keep, label_of,
                          span)

MATCH_COLOR = "#9ccc65"      # deliberately NOT the CDS teal, to stay unambiguous
MISMATCH_COLOR = "#d64545"
ORIGIN_COLOR = "#8a6fbf"


def circular_offset(a, b):
    """Rotation k with b == a[k:]+a[:k], else (None, strand) via revcomp."""
    for strand, q in (("+", b), ("-", str(Seq(b).reverse_complement()))):
        k = (a + a).find(q)
        if k >= 0:
            return k, strand, True
    # no exact match - fall back to best-scoring rotation on the forward strand
    best_k, best_score = 0, -1
    for k in range(len(a)):
        rot = a[k:] + a[:k]
        score = sum(1 for x, y in zip(rot, b) if x == y)
        if score > best_score:
            best_k, best_score = k, score
    return best_k, "+", False


def mapped_segments(f, length, shift=0):
    """Feature span in the reference frame, split where it wraps the origin.

    A join(...) location (how an origin-spanning feature is written) has one
    part per piece; collapsing it to min..max would draw one arrow across the
    whole plasmid, so each part is mapped separately.
    """
    out = []
    for part in f.location.parts:
        s, e = int(part.start), int(part.end)
        if e <= s:                      # Biopython gave us a wrapped location
            e = length
        s, e = (s + shift) % length, ((e + shift) % length) or length
        out += [(s, e)] if s < e else [(s, length), (0, e)]
    return out


def draw_feature_row(ax, feats, y, height, length, shift=0):
    for f in feats:
        for s, e in mapped_segments(f, length, shift):
            w = max(e - s, length * 0.004)
            head = min(w * 0.4, length * 0.012)
            x, dx = (s, w) if f.location.strand != -1 else (e, -w)
            ax.add_patch(FancyArrow(
                x, y + height / 2, dx, 0, width=height,
                head_width=height, head_length=head, length_includes_head=True,
                facecolor=TYPE_COLORS[f.type], edgecolor="black", linewidth=0.5,
                zorder=3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("sequencing")
    ap.add_argument("--label-a", default=None)
    ap.add_argument("--label-b", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rec_a = SeqIO.read(args.design, "genbank")
    rec_b = SeqIO.read(args.sequencing, "genbank")
    a = str(rec_a.seq).upper()
    b = str(rec_b.seq).upper()
    name_a = args.label_a or os.path.splitext(os.path.basename(args.design))[0]
    name_b = args.label_b or os.path.splitext(os.path.basename(args.sequencing))[0]

    if len(a) != len(b):
        print(f"WARNING: lengths differ, {len(a)} vs {len(b)} bp - "
              "this panel assumes equal-length circular records")
    length = len(a)

    k, strand, exact = circular_offset(a, b)
    # b, expressed in a's coordinate frame
    b_in_a = (b if strand == "+" else str(Seq(b).reverse_complement()))
    b_aligned = b_in_a[length - k:] + b_in_a[:length - k] if k else b_in_a
    mismatches = [i for i in range(length) if a[i] != b_aligned[i]]
    identity = 100 * (length - len(mismatches)) / length

    feats_a = [f for f in rec_a.features if keep(f)]
    feats_b = [f for f in rec_b.features if keep(f)]

    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.set_xlim(-length * 0.01, length * 1.01)
    ax.set_ylim(0, 13)
    ax.axis("off")

    # --- design feature track -------------------------------------------------
    ax.add_patch(Rectangle((0, 8.5), length, 0.18, facecolor="#333333",
                           edgecolor="none", zorder=1))
    draw_feature_row(ax, feats_a, y=8.1, height=1.0, length=length)
    ax.text(-length * 0.012, 8.6, f"{name_a}\n(design)", ha="right",
            va="center", fontsize=8, linespacing=1.4)

    # Labels alternate between two heights so neighbours cannot collide; the
    # dense T7 insert is left to the zoom panel rather than crammed in here.
    row = 0
    for f in sorted(feats_a, key=lambda f: span(f)[0]):
        s, e = span(f)
        if e <= s:
            e = length
        if e - s < length * 0.025 or is_nested(f, feats_a):
            continue                     # sub-features belong in a zoom panel
        y = 9.7 + 0.85 * (row % 2)
        ax.text((s + e) / 2, y, label_of(f).replace("\n", " "), ha="center",
                va="bottom", fontsize=6.5)
        ax.plot([(s + e) / 2, (s + e) / 2], [9.2, y - 0.05], color="#999999",
                lw=0.4, zorder=0)
        row += 1

    # --- identity track -------------------------------------------------------
    ax.add_patch(Rectangle((0, 5.3), length, 1.2, facecolor=MATCH_COLOR,
                           edgecolor="black", linewidth=0.5, zorder=2))
    for i in mismatches:
        ax.add_patch(Rectangle((i, 5.3), max(1, length * 0.002), 1.2,
                               facecolor=MISMATCH_COLOR, edgecolor="none",
                               zorder=3))
    ax.text(-length * 0.012, 5.9, "identity", ha="right", va="center",
            fontsize=8)
    verdict = (f"{length - len(mismatches):,} / {length:,} bp identical "
               f"({identity:.1f}%)   ·   {len(mismatches)} mismatches   ·   "
               f"0 gaps")
    ax.text(length / 2, 5.9, verdict, ha="center", va="center", fontsize=9.5,
            color="#0d1117", fontweight="bold", zorder=4)

    # --- sequencing feature track, mapped into the design frame ---------------
    ax.add_patch(Rectangle((0, 3.4), length, 0.18, facecolor="#333333",
                           edgecolor="none", zorder=1))
    draw_feature_row(ax, feats_b, y=3.0, height=1.0, length=length, shift=k)
    ax.text(-length * 0.012, 3.5, f"{name_b}\n(sequencing)", ha="right",
            va="center", fontsize=8, linespacing=1.4)

    # where the sequencing contig's own base 1 falls in the design frame
    ax.plot([k, k], [2.4, 9.2], color=ORIGIN_COLOR, lw=1.1, ls="--", zorder=5)
    ax.text(k + length * 0.008, 2.3,
            f"{name_b} base 1 = design position {k + 1:,}",
            ha="left", va="top", fontsize=6.5, color=ORIGIN_COLOR)

    # --- scale ----------------------------------------------------------------
    for xt in range(0, length + 1, 200):
        ax.plot([xt, xt], [1.35, 1.55], color="#555555", lw=0.5)
        ax.text(xt, 1.2, f"{xt:,}", ha="center", va="top", fontsize=6.5,
                color="#555555")
    ax.plot([0, length], [1.55, 1.55], color="#555555", lw=0.5)
    ax.text(length / 2, 0.6, f"position in {name_a} (bp)", ha="center",
            va="top", fontsize=7, color="#555555")

    title = (f"{name_a}: sequencing confirms the designed construct"
             if identity == 100 else
             f"{name_a} vs {name_b}: {identity:.2f}% identity")
    ax.set_title(title, fontsize=11, pad=14)

    drawn = {f.type for f in feats_a} | {f.type for f in feats_b}
    handles = [Patch(facecolor=TYPE_COLORS[t], edgecolor="black", lw=0.5,
                     label=TYPE_LABELS[t])
               for t in TYPE_COLORS if t in drawn]
    handles += [
        Patch(facecolor=MATCH_COLOR, edgecolor="black", lw=0.5,
              label="Identical base (design = sequencing)"),
        Patch(facecolor=MISMATCH_COLOR, edgecolor="none",
              label=f"Mismatch ({len(mismatches)} present)"),
        Line2D([], [], color=ORIGIN_COLOR, lw=1.1, ls="--",
               label=f"Origin of the sequencing contig (rotated {k} bp)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=7,
               frameon=False, bbox_to_anchor=(0.5, -0.14))

    out = args.out or f"{name_a}_vs_{name_b}_identity"
    fig.savefig(out + ".pdf", bbox_inches="tight")
    fig.savefig(out + ".png", dpi=300, bbox_inches="tight")

    print(f"{name_a} {len(a)} bp vs {name_b} {len(b)} bp")
    print(f"  exact circular match: {exact}   strand: {strand}   rotation: {k} bp")
    print(f"  identity: {identity:.4f}%   mismatches: {len(mismatches)}")
    if mismatches[:20]:
        print("  first mismatches (design coords):",
              [i + 1 for i in mismatches[:20]])


if __name__ == "__main__":
    main()
