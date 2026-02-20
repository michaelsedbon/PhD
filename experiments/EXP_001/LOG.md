# EXP_001 — Restriction Site Analysis for Genome Tiling

**Start Date:** 2026-02-20  
**Goal:** Pick the best Type IIS restriction enzyme for Golden Gate assembly of ~7 kb PCR tiles covering the *E. coli* MG1655 genome.

---

## Context

- Work Package 2 of the Sedbon_BF proposal: polyploidy-inspired genome-scale hypermutation
- ~7 kb fragments will be PCR-amplified from the E. coli MG1655 genome
- Fragments go into Lvl0 MoClo plasmids, then 11-fragment Golden Gate into Lvl1 (T7 replisome)
- Need to choose a Type IIS enzyme with minimal sites so internal sites can be removed via silent mutations during PCR

**Candidate enzymes:** BsaI, BbsI, BsmBI, SapI, BtgZI, AarI, Esp3I, BpiI

---

## Genome

- **Organism:** *Escherichia coli* str. K-12 substr. MG1655
- **Accession:** U00096.3
- **Length:** 4,641,652 bp
- **Genes:** 4,651 | **CDS:** 4,318

---

## Results

### Enzyme comparison

| Enzyme | Recognition | Sites | Sites/kb | Min gap (bp) | Max gap (bp) | Free 7kb windows | % genome in free ≥7kb |
|--------|------------|-------|----------|-------------|-------------|-------------------|----------------------|
| **BsaI** | **GGTCTC** | **261** | **0.06** | **10** | **~100k** | **152** | **~90%** |
| SapI | GCTCTTC | 683 | 0.15 | 3 | ~50k | 240 | ~80% |
| AarI | CACCTGC | 1,107 | 0.24 | 1 | ~30k | 207 | ~65% |
| BsmBI | CGTCTC | 1,127 | 0.24 | 6 | ~35k | 211 | ~60% |
| Esp3I | CGTCTC | 1,127 | 0.24 | 6 | ~35k | 211 | ~60% |
| BbsI | GAAGAC | 1,748 | 0.38 | 2 | ~20k | 132 | ~25% |
| BpiI | GAAGAC | 1,748 | 0.38 | 2 | ~20k | 132 | ~25% |
| BtgZI | GCGATG | 5,410 | 1.17 | 1 | — | 0 | 0% |

> BsmBI/Esp3I and BbsI/BpiI are isoschizomer pairs (identical results expected).

---

### Enzyme ranking

![Enzyme ranking comparison](data/enzyme_ranking.png)

[→ Interactive version](data/enzyme_ranking.html)

---

### Site positions across the genome

![Site positions linear map](data/site_positions_linear.png)

[→ Interactive version](data/site_positions_linear.html)

---

### Site density in 7 kb sliding windows (top 3 candidates)

![Sliding window site density](data/site_density_7kb_window.png)

[→ Interactive version](data/site_density_7kb_window.html)

**Colour key:** 🟢 0 sites | 🟡 1 site | 🟠 2 sites | 🔴 3+ sites

---

### Gap-size distribution

![Gap distribution histograms](data/gap_distribution.png)

[→ Interactive version](data/gap_distribution.html)

Red dashed line = 7 kb threshold.

---

### BsaI — Domestication effort

![BsaI domestication donut chart](data/domestication_donut.png)

[→ Interactive version](data/domestication_donut.html)

---

## Conclusion

**BsaI** is the clear best choice:
- Only **261 sites** in 4.64 Mb (0.06/kb)
- **71% of 7 kb windows** are completely site-free
- **~90% of the genome** lies within stretches ≥ 7 kb with no BsaI site
- For tiles with internal sites, most have only **1 site** → easily domesticated by a single silent mutation in the PCR primer

**BtgZI** is eliminated — 5,410 sites, zero 7 kb site-free windows.

---

## Output Files

| File | Description |
|------|-------------|
| `restriction_utils.py` | Python module (genome download, site mapping, statistics) |
| `restriction_site_analysis.ipynb` | Full analysis notebook (Plotly, dark theme) |
| `data/restriction_site_summary.csv` | Summary statistics for all enzymes |
| `data/site_positions_linear.html` / `.png` | Linear genome map of all sites |
| `data/site_density_7kb_window.html` / `.png` | Sliding window density (top 3) |
| `data/gap_distribution.html` / `.png` | Gap size histograms (top 3) |
| `data/enzyme_ranking.html` / `.png` | Enzyme comparison bar charts |
| `data/domestication_donut.html` / `.png` | BsaI domestication effort breakdown |

