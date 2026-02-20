"""
restriction_utils.py — Utilities for mapping Type IIS restriction sites in E. coli MG1655.

Part of EXP_001: Restriction site analysis for Golden Gate genome tiling.

Usage:
    # As a module
    from restriction_utils import download_mg1655, find_sites, site_stats

    # Standalone test
    python3 restriction_utils.py
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

from Bio import Entrez, SeqIO
from Bio.Restriction import (
    BsaI, BbsI, BsmBI, SapI, BtgZI, AarI, Esp3I, BpiI,
    RestrictionBatch,
)
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
GENOME_ACCESSION = "U00096.3"           # E. coli K-12 MG1655
GENOME_FILENAME  = "MG1655.gb"
Entrez.email = "exp001@lab.local"        # NCBI requires an email

# Canonical set of Golden-Gate / MoClo Type IIS enzymes
TYPE_IIS_ENZYMES = {
    "BsaI":  BsaI,
    "BbsI":  BbsI,
    "BsmBI": BsmBI,
    "SapI":  SapI,
    "BtgZI": BtgZI,
    "AarI":  AarI,
    "Esp3I": Esp3I,
    "BpiI":  BpiI,
}

# ---------------------------------------------------------------------------
# Genome download
# ---------------------------------------------------------------------------

def download_mg1655(force: bool = False) -> SeqRecord:
    """
    Download the annotated E. coli K-12 MG1655 genome from NCBI GenBank.
    Caches the file locally in ``data/MG1655.gb``.

    Parameters
    ----------
    force : bool
        If True, re-download even if cached file exists.

    Returns
    -------
    SeqRecord
        The parsed GenBank record.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / GENOME_FILENAME

    if filepath.exists() and not force:
        print(f"✓ Using cached genome: {filepath}")
    else:
        print(f"↓ Downloading {GENOME_ACCESSION} from NCBI …")
        handle = Entrez.efetch(
            db="nucleotide",
            id=GENOME_ACCESSION,
            rettype="gb",
            retmode="text",
        )
        with open(filepath, "w") as f:
            f.write(handle.read())
        handle.close()
        print(f"✓ Saved to {filepath}")

    record = SeqIO.read(filepath, "genbank")
    return record


# ---------------------------------------------------------------------------
# Restriction site finding
# ---------------------------------------------------------------------------

def find_sites(record: SeqRecord, enzyme_name: str) -> List[int]:
    """
    Find all cut-site positions for *enzyme_name* in *record*.

    Uses Biopython's Restriction module which searches both strands.

    Parameters
    ----------
    record : SeqRecord
        The genome record.
    enzyme_name : str
        Name of the enzyme (must be in TYPE_IIS_ENZYMES).

    Returns
    -------
    list of int
        Sorted 1-based positions of recognition sites.
    """
    enzyme = TYPE_IIS_ENZYMES[enzyme_name]
    rb = RestrictionBatch([enzyme])
    result = rb.search(record.seq, linear=False)
    positions = sorted(result[enzyme])
    return positions


def find_all_sites(record: SeqRecord) -> Dict[str, List[int]]:
    """Map all Type IIS enzymes and return {name: [positions]}."""
    return {name: find_sites(record, name) for name in TYPE_IIS_ENZYMES}


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def site_stats(positions: List[int], genome_len: int) -> dict:
    """
    Compute summary statistics for a list of restriction-site positions.

    Returns
    -------
    dict with keys: count, density_per_kb, mean_spacing, min_spacing, max_spacing
    """
    n = len(positions)
    if n == 0:
        return {
            "count": 0,
            "density_per_kb": 0.0,
            "mean_spacing": float("inf"),
            "min_spacing": float("inf"),
            "max_spacing": float("inf"),
        }

    spacings = [positions[i + 1] - positions[i] for i in range(n - 1)]
    # Circular genome: add wrap-around spacing
    spacings.append(genome_len - positions[-1] + positions[0])

    return {
        "count": n,
        "density_per_kb": n / (genome_len / 1000),
        "mean_spacing": sum(spacings) / len(spacings),
        "min_spacing": min(spacings),
        "max_spacing": max(spacings),
    }


def sites_per_window(
    positions: List[int],
    genome_len: int,
    window_size: int = 7000,
) -> List[Tuple[int, int]]:
    """
    For every 1 kb step across the genome, count how many restriction sites
    fall within a window of *window_size* bp centred on that position.

    Returns a list of (position, count) tuples.
    """
    from bisect import bisect_left, bisect_right

    pos_sorted = sorted(positions)
    results = []
    step = 1000
    for start in range(0, genome_len, step):
        end = start + window_size
        if end <= genome_len:
            count = bisect_right(pos_sorted, end) - bisect_left(pos_sorted, start)
        else:
            # Wrap around circular genome
            count = (
                bisect_right(pos_sorted, genome_len) - bisect_left(pos_sorted, start)
                + bisect_right(pos_sorted, end - genome_len)
            )
        results.append((start, count))
    return results


def site_free_windows(
    positions: List[int],
    genome_len: int,
    window_size: int = 7000,
) -> List[Tuple[int, int]]:
    """
    Find all maximal contiguous stretches of the genome (≥ window_size bp)
    that contain zero restriction sites.

    Returns a list of (start, length) tuples.
    """
    if not positions:
        return [(0, genome_len)]

    pos_sorted = sorted(positions)
    free = []

    # Gaps between consecutive sites
    for i in range(len(pos_sorted) - 1):
        gap = pos_sorted[i + 1] - pos_sorted[i]
        if gap >= window_size:
            free.append((pos_sorted[i], gap))

    # Wrap-around gap
    gap = genome_len - pos_sorted[-1] + pos_sorted[0]
    if gap >= window_size:
        free.append((pos_sorted[-1], gap))

    return free


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pandas as pd

    print("=" * 60)
    print("EXP_001 — Restriction Site Analysis")
    print("=" * 60)

    record = download_mg1655()
    genome_len = len(record.seq)
    print(f"\nGenome: {record.description}")
    print(f"Length: {genome_len:,} bp")

    n_cds = sum(1 for f in record.features if f.type == "CDS")
    n_gene = sum(1 for f in record.features if f.type == "gene")
    print(f"Genes: {n_gene:,}  |  CDS: {n_cds:,}\n")

    all_sites = find_all_sites(record)

    rows = []
    for name, positions in sorted(all_sites.items(), key=lambda x: len(x[1])):
        stats = site_stats(positions, genome_len)
        free = site_free_windows(positions, genome_len, window_size=7000)
        stats["site_free_7kb_windows"] = len(free)
        stats["enzyme"] = name
        rows.append(stats)
        print(f"{name:6s}  {stats['count']:5d} sites  "
              f"({stats['density_per_kb']:.2f}/kb)  "
              f"min gap {stats['min_spacing']:,} bp  "
              f"site-free 7kb windows: {len(free)}")

    df = pd.DataFrame(rows).set_index("enzyme")
    df.to_csv(DATA_DIR / "restriction_site_summary.csv")
    print(f"\n✓ Summary saved to {DATA_DIR / 'restriction_site_summary.csv'}")
