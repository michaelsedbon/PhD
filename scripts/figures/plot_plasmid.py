#!/usr/bin/env python3
"""Annotated plasmid figures from a GenBank file.

    python3 scripts/figures/plot_plasmid.py MS_C_031.gb [--zoom 1370:1600]
                                                        [--nested-on-circle]

Requires: pip install dna_features_viewer pycirclize

Writes, next to the input:
  <name>_circular.pdf/.png   circular overview (pyCirclize) + GC content / skew
  <name>_linear.pdf/.png     linear map of the whole construct
  <name>_zoom.pdf/.png       linear zoom on a region, if --zoom is given

Cloning bookkeeping (primer_bind, Fragment, ligation, source, gene, mRNA and
single-base regulatory points that duplicate a drawn promoter) is filtered out.
Features nested inside a larger feature of a different type are dropped from the
CIRCULAR overview only - they crowd a narrow sector - but kept in the linear
views, where dna_features_viewer stacks them on separate rows.

Every colour and line in each figure is explained in its legend.
"""
import argparse
import os
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from Bio import SeqIO
from Bio.SeqFeature import SeqFeature, SimpleLocation
from dna_features_viewer import BiopythonTranslator
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from pycirclize import Circos

# --- feature types drawn, with colour and legend wording ----------------------
TYPE_COLORS = {
    "rep_origin": "#569cd6",
    "CDS": "#4ec9b0",
    "promoter": "#dcdcaa",
    "protein_bind": "#c586c0",
    "misc_structure": "#e06c75",
    "misc_feature": "#9c9c9c",
    "terminator": "#ce9178",
}
TYPE_LABELS = {
    "rep_origin": "Origin of replication",
    "CDS": "Coding sequence",
    "promoter": "Promoter",
    "protein_bind": "Protein binding site",
    "misc_structure": "RNA structural site",
    "misc_feature": "Annotated region / cloning scar",
    "terminator": "Terminator",
}

# Shorter display names so labels fit.
RENAME = {
    "R6K gamma ori": "R6K γ ori",
    "Extension (35 bp Gibson arm)": "Gibson arm",
    "phiOR cassette (T7 ori)": "phiOR cassette (T7 ori)",
    "phiOR promoter (class III, -17..+1)": "phiOR promoter",
    "phiOR AT-rich melting region": "AT-rich melting region",
    "ori-phi1.1 (T7 PRIMARY origin of replication)": "ori-phi1.1 (T7 primary origin)",
    "phi1.1A promoter (-17 to +6)": "phi1.1A promoter",
    "phi1.1B promoter (-17 to +6)": "phi1.1B promoter",
    "Origin essential region (14.75-15.0 map units)": "Origin essential region",
    "A+T-rich origin core (73.8% A+T)": "A+T-rich origin core",
    "Gene 4 primase recognition site 5'-GGGTC-3'": "Gene 4 primase site",
    "RNase III site R1.1 misc structure": "RNase III site R1.1",
}

# Labels of duplicate annotations of an element drawn under another name.
DROP_LABELS = {"T7 promoter"}

# Cloning scars and bookkeeping markers. On a small construct these are worth
# showing; on a multi-gene build they outnumber the genes and bury them, so
# --drop-scars removes them. Matched case-insensitively against the label.
SCAR_PATTERNS = (
    "gibson", "homology arm", "extension (", "sd ", "spacer", "linker",
    "junction", "provenance", "note_0", "biobrick",
)


# Transcription-unit palette, matching the hand-drawn TU schematic for the
# T7-ORACLE builds so a map and that diagram can sit on the same slide.
TU_COLORS = ["#2e8b6b", "#e09f3e", "#2b6ca3", "#c77fb4"]
BACKBONE_COLOR = "#b0b0b0"


def find_tus(features, length):
    """[(name, start, end)] for the construct's transcription units.

    Prefers explicit `TU<n>` block annotations. Falls back to pairing each
    promoter with the end of the terminator that closes it, which is how the
    blocks are laid out when nobody has drawn them in yet.
    """
    blocks = []
    for f in features:
        lab = f.qualifiers.get("label", [""])[0].strip()
        if re.fullmatch(r"TU\s*\d+", lab, re.I):
            blocks.append((lab.upper().replace(" ", ""),
                           int(f.location.start), int(f.location.end)))
    if blocks:
        return sorted(blocks, key=lambda b: b[1])

    proms = sorted((int(f.location.start), int(f.location.end))
                   for f in features if f.type == "promoter")
    terms = sorted((int(f.location.start), int(f.location.end))
                   for f in features if f.type == "terminator")
    for ps, pe in proms:
        after = [(ts, te) for ts, te in terms if ts >= pe]
        if not after:
            continue
        # the CLOSING terminator is the first one after the promoter; a
        # terminator is often annotated twice (complete + 5'/3' portion), so
        # extend to the far end of that overlapping cluster - but no further,
        # or the unit swallows everything downstream.
        first_start = after[0][0]
        end = max(te for ts, te in after if ts <= first_start)
        if not blocks or ps >= blocks[-1][2]:
            blocks.append((f"TU{len(blocks) + 1}", ps, end))
    return blocks


def tu_of(f, tus):
    """Index of the TU containing f's midpoint, or None for backbone."""
    s, e = span(f)
    mid = (s + e) / 2
    for i, (_, ts, te) in enumerate(tus):
        if ts <= mid < te:
            return i
    return None


def is_scar(f):
    lab = f.qualifiers.get("label", [""])[0].lower()
    return any(p in lab for p in SCAR_PATTERNS)


def label_of(f):
    raw = f.qualifiers.get("label", [f.type])[0]
    return RENAME.get(raw, raw)


def keep(f):
    return (f.type in TYPE_COLORS
            and f.qualifiers.get("label", [""])[0] not in DROP_LABELS)


def span(f):
    return int(f.location.start), int(f.location.end)


def is_nested(f, others):
    """True if f is a sub-feature of a larger one, for circular-map purposes.

    Two cases count. A feature strictly inside a LARGER FEATURE OF ITS OWN TYPE
    is a fragment call (pLannotate reports partial CDS hits inside the real
    one). A feature inside a larger feature of a different type is detail of
    that element - EXCEPT when the container is a misc_feature, because that is
    how a transcription-unit block is annotated, and the genes inside it are
    the whole point of the map rather than its detail.
    """
    s, e = span(f)
    for g in others:
        if g is f:
            continue
        gs, ge = span(g)
        if not (gs <= s and e <= ge and (ge - gs) > (e - s)):
            continue
        if g.type == f.type or g.type != "misc_feature":
            return True
    return False


# --- linear views -------------------------------------------------------------
class PlasmidTranslator(BiopythonTranslator):
    def compute_feature_color(self, feature):
        return TYPE_COLORS.get(feature.type, "#cccccc")

    def compute_feature_label(self, feature):
        return label_of(feature)

    def compute_filtered_features(self, features):
        return [f for f in features if keep(f)]

    def compute_feature_fontdict(self, feature):
        return {"fontsize": 7}


def legend_handles(types):
    return [Patch(facecolor=TYPE_COLORS[t], edgecolor="black", lw=0.5,
                  label=TYPE_LABELS[t])
            for t in TYPE_COLORS if t in types]


def plot_linear(gb, name, feats, out, title, crop=None, width=12):
    record = PlasmidTranslator().translate_record(gb)
    if crop:
        record = record.crop(crop)
    ax, _ = record.plot(figure_width=width)
    ax.set_title(title, fontsize=11)
    ax.legend(handles=legend_handles({f.type for f in feats}),
              loc="upper left", fontsize=7, ncol=2, frameon=False,
              title="Feature type", title_fontsize=7)
    ax.figure.savefig(out + ".pdf", bbox_inches="tight")
    ax.figure.savefig(out + ".png", dpi=300, bbox_inches="tight")
    plt.close(ax.figure)


# --- circular view ------------------------------------------------------------
def gc_profile(seq, window=50, step=10):
    n = len(seq)
    pos, gc = [], []
    for i in range(0, n, step):
        w = seq[i:i + window]
        if len(w) < window:
            w += seq[:window - len(w)]
        pos.append(min(i + window / 2, n - 1))
        gc.append(100 * (w.count("G") + w.count("C")) / len(w))
    skew = np.cumsum([1 if b == "G" else -1 if b == "C" else 0 for b in seq])
    gc_mean = 100 * (seq.count("G") + seq.count("C")) / n
    return np.array(pos), np.array(gc), skew, gc_mean


def drawable(f, length):
    """Exact-coordinate copies of f, one per location part.

    pyCirclize cannot parse a fuzzy boundary (``<1422..2937``, how Geneious
    writes a CDS that is genuinely partial) or a ``join(...)`` that wraps the
    origin, so the feature is rebuilt with plain integer positions purely for
    drawing. The underlying record is untouched.
    """
    out = []
    for part in f.location.parts:
        s, e = int(part.start), int(part.end)
        if e <= s:
            e = length
        g = SeqFeature(SimpleLocation(s, e, strand=part.strand or 1),
                       type=f.type)
        g.qualifiers = f.qualifiers
        out.append(g)
    return out


def plot_circular(name, seq, feats, out, color_of=None, legend_extra=None):
    length = len(seq)
    circos = Circos(sectors={name: length})
    sector = circos.sectors[0]
    color_of = color_of or (lambda f: TYPE_COLORS[f.type])

    ring = sector.add_track((88, 96))
    ring.axis(fc="#f3f3f3", ec="#bbbbbb", lw=0.4)
    for f in feats:
        for g in drawable(f, length):
            ring.genomic_features([g], plotstyle="arrow",
                                  fc=color_of(f), ec="black", lw=0.4)

    # Long features label just outside the ring; short ones are staggered onto
    # outer tiers and joined by a leader line so they do not collide.
    # The same element is often annotated more than once (a complete
    # terminator plus its 5'/3' portions, a marker called twice by different
    # databases). Label each distinct name once, on its longest instance.
    by_label = {}
    for f in feats:
        s, e = span(f)
        prev = by_label.get(label_of(f))
        if prev is None or (e - s) > (span(prev)[1] - span(prev)[0]):
            by_label[label_of(f)] = f

    leaders, tier = [], 0
    for f in sorted(by_label.values(), key=lambda f: span(f)[0]):
        s, e = span(f)
        mid = (s + e) / 2
        if e - s >= length * 0.08:
            r = 101
        else:
            r = 112 + 12 * (tier % 3)       # three tiers for dense constructs
            tier += 1
            leaders.append((sector.x_to_rad(mid), r))
        sector.text(label_of(f), r=r, size=7.5, adjust_rotation=True,
                    orientation="horizontal", x=mid)

    # aim for ~12 ticks, snapped to a round number
    target = length / 12
    interval = min((x for x in (50, 100, 250, 500, 1000, 2000, 2500, 5000)
                    if x >= target), default=10000)
    ring.xticks_by_interval(interval, outer=False,
                            label_formatter=lambda v: f"{v:,.0f}",
                            label_size=6, tick_length=1.5,
                            line_kws=dict(lw=0.5, color="#555555"),
                            text_kws=dict(color="#555555"))

    pos, gc, skew, gc_mean = gc_profile(seq)
    gc_track = sector.add_track((68, 84))
    gc_track.axis(fc="none", ec="#dddddd", lw=0.4)
    gc_track.fill_between(pos, gc, gc_mean, vmin=gc.min(), vmax=gc.max(),
                          fc="#8a6fbf", alpha=0.7, lw=0)

    skew_track = sector.add_track((52, 66))
    skew_track.axis(fc="none", ec="#dddddd", lw=0.4)
    skew_track.line(np.arange(length), skew, vmin=skew.min(), vmax=skew.max(),
                    color="#d08770", lw=0.8)

    fig = circos.plotfig(figsize=(7.5, 7.5))
    ax = fig.axes[0]
    for rad, r in leaders:
        ax.plot([rad, rad], [97, r - 3], color="#999999", lw=0.4, zorder=0,
                clip_on=False)
    ax.text(0.5, 0.5, f"{name}\n{length} bp\n{gc_mean:.1f}% GC",
            ha="center", va="center", fontsize=11, linespacing=1.6,
            transform=ax.transAxes)

    handles = (legend_extra if legend_extra is not None
               else legend_handles({f.type for f in feats})) + [
        Patch(facecolor="#8a6fbf", alpha=0.7, edgecolor="none",
              label=f"GC content, 50 bp window (deviation from {gc_mean:.1f}% mean)"),
        Line2D([], [], color="#d08770", lw=1.2, label="Cumulative GC skew (G-C)"),
        Line2D([], [], color="#555555", lw=0.5, label="Position scale (bp)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=7,
               frameon=False, bbox_to_anchor=(0.5, -0.09))
    fig.savefig(out + ".pdf", bbox_inches="tight")
    fig.savefig(out + ".png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return gc_mean


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("genbank")
    ap.add_argument("--zoom", help="region to zoom, e.g. 1370:1600")
    ap.add_argument("--nested-on-circle", action="store_true",
                    help="also draw nested sub-features on the circular map "
                         "(fine for sparse constructs, crowded for dense ones)")
    ap.add_argument("--color-by-tu", action="store_true",
                    help="colour features by the transcription unit they sit "
                         "in, using the TU schematic's palette, instead of by "
                         "feature type")
    ap.add_argument("--drop-scars", action="store_true",
                    help="drop Gibson arms, SD sequences, linkers and other "
                         "cloning bookkeeping (see SCAR_PATTERNS) - usually "
                         "needed for multi-gene constructs")
    args = ap.parse_args()

    rec = SeqIO.read(args.genbank, "genbank")
    seq = str(rec.seq).upper()
    name = os.path.splitext(os.path.basename(args.genbank))[0]
    stem = os.path.join(os.path.dirname(args.genbank) or ".", name)

    feats = [f for f in rec.features if keep(f)]
    if args.drop_scars:
        feats = [f for f in feats if not is_scar(f)]
    nested = [f for f in feats if is_nested(f, feats)]
    outer = feats if args.nested_on_circle else [f for f in feats
                                                 if f not in nested]

    color_of = legend_extra = None
    if args.color_by_tu:
        tus = find_tus(rec.features, len(seq))
        if not tus:
            sys.exit("--color-by-tu: no TU blocks or promoter/terminator "
                     "pairs found in this record")
        # Name each TU by the CDSs inside it, so the legend reads as biology.
        contents = []
        for i, (tu_name, ts, te) in enumerate(tus):
            # Name the unit by its substantial CDSs: pLannotate also reports
            # tiny spurious hits ("nagE", "hypothetical protein") that would
            # otherwise dominate the legend.
            genes = sorted((f for f in feats
                            if f.type == "CDS" and tu_of(f, tus) == i
                            and span(f)[1] - span(f)[0] >= 300),
                           key=lambda f: span(f)[0] - span(f)[1])
            seen = list(dict.fromkeys(label_of(f).replace(" CDS", "")
                                      for f in genes))
            contents.append(f"{tu_name}  ({ts + 1:,}-{te:,})"
                            + (f" — {', '.join(seen[:2])}" if seen else ""))
        color_of = (lambda f: TU_COLORS[tu_of(f, tus) % len(TU_COLORS)]
                    if tu_of(f, tus) is not None else BACKBONE_COLOR)
        legend_extra = [
            Patch(facecolor=TU_COLORS[i % len(TU_COLORS)], edgecolor="black",
                  lw=0.5, label=contents[i]) for i in range(len(tus))
        ] + [Patch(facecolor=BACKBONE_COLOR, edgecolor="black", lw=0.5,
                   label="Backbone (outside any transcription unit)")]
        print("transcription units:")
        for c in contents:
            print("  " + c)

    gc_mean = plot_circular(name, seq, outer, stem + "_circular",
                            color_of=color_of, legend_extra=legend_extra)
    plot_linear(args.genbank, name, feats, stem + "_linear",
                f"{name} - linear view")
    if args.zoom:
        a, b = (int(v) for v in args.zoom.split(":"))
        plot_linear(args.genbank, name, feats, stem + "_zoom",
                    f"{name} - {a:,}-{b:,} bp", crop=(a, b), width=10)

    print(f"{name}: {len(seq)} bp, {gc_mean:.1f}% GC, "
          f"{len(feats)} features kept ({len(outer)} on the circular map)")
    if nested:
        print("nested (linear views only):")
        for f in nested:
            s, e = span(f)
            print(f"  {f.type:14s} {s+1:>5}-{e:<5} {label_of(f)}")


if __name__ == "__main__":
    main()
