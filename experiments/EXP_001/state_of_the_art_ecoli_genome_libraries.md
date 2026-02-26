# State of the Art — *E. coli* Genome Libraries

> A review of existing approaches to capturing and manipulating the *E. coli* genome at scale, covering synthetic genomes, ORFeome collections, gene-deletion libraries, early clone banks, and modular-cloning toolkits.

---

## 1. Synthetic Genome Projects

### 1.1 Syn61 — Total synthesis of *E. coli* with a recoded genome

**Fredens et al., Nature, 2019** — Chin Lab (MRC-LMB, Cambridge)

The most ambitious *E. coli* synthetic genome project to date. The authors performed **high-fidelity convergent total synthesis** of a **4.0 Mb** synthetic genome for *E. coli* MDS42, in which **18,214 codons** were systematically recoded:

- All **TCG** → AGC (Ser)
- All **TCA** → AGT (Ser)
- All **TAG** → TAA (stop)

This compression reduced the genetic code from 64 to **61 codons** (59 sense + 2 stop), creating the strain **Syn61**. The recoding freed three codons for potential reassignment to non-canonical amino acids. The work relied on:

- **REXER** (Replicon EXcision Enhanced Recombination): sequential replacement of ~100 kb chromosomal segments with synthetic DNA via λ Red + CRISPR selection.
- **GENESIS** (GENomE Stepwise Interchange Synthesis): iterative REXER across all ~50 segments.

Only **7 corrections** out of 18,214 substitutions were needed. Syn61 is viable, albeit with a ~60% longer doubling time.

> **Key limitation:** Syn61 is a *finished strain* — not a modular library. The synthetic DNA cannot easily be rearranged or remixed.

**Source:** Notion bibliography — Relevance: "Diploid E. coli"; File: `fredens2019.pdf`
**URL:** https://www.nature.com/articles/s41586-019-1192-5

---

### 1.2 rE.coli-57 — Computationally designed 57-codon genome

**Ostrov et al., Science, 2016** — Church Lab (Harvard)

The Church lab computationally designed a radically recoded *E. coli* MG1655 genome (**4.6 Mb**) using only **57 codons** — eliminating 7 codons entirely. The genome was partitioned into **63 segments** (~50 kb each), and each was individually synthesized and tested:

- **91% of segments** were viable when integrated individually.
- The full genome was **not assembled** into a single organism (unlike Syn61).
- The project identified positions where synonymous recoding produced fitness defects, particularly in highly expressed or overlapping genes.

This work provided critical data on the *E. coli* recoding landscape and demonstrated that comprehensive codon reassignment is feasible but requires careful attention to overlapping regulatory elements.

> **Key limitation:** Computational design + individual segment testing, but no complete assembled organism.

**URL:** https://doi.org/10.1126/science.aad8711

---

### 1.3 JCVI-syn3.0 — Minimal synthetic genome

**Hutchison et al., Science, 2016** — Venter Institute

While not *E. coli*, this is a landmark in synthetic genomics. The Venter group created **JCVI-syn3.0**, a *Mycoplasma mycoides* cell with a **531 kb** minimal genome containing only **473 genes** — the smallest genome capable of independent cellular life:

- Hierarchical assembly: 1 kb → 10 kb → 100 kb → full genome in yeast.
- Genome transplantation into a recipient *Mycoplasma* cell.
- ~149 genes (~31%) have unknown functions.

> **Relevance:** Proves genome-scale synthesis is possible; the hierarchical assembly strategy influenced later *E. coli* synthetic genome work.

**URL:** https://doi.org/10.1126/science.aad6253

---

### 1.4 Sc2.0 — First synthetic eukaryotic chromosomes

**International Sc2.0 Consortium, 2017–2024** — Multiple labs worldwide

The Sc2.0 project aims to synthesize the entire **12 Mb** genome of *Saccharomyces cerevisiae* (16 chromosomes). Key features:

- **Bottom-up assembly** of ~10 kb building blocks into full synthetic chromosomes.
- Insertion of **loxPsym** sites (SCRaMbLE system) at non-essential gene 3′ ends, enabling combinatorial Cre-mediated genome rearrangement.
- As of 2024, synthetic versions of multiple chromosomes have been completed and consolidated.

> **Relevance:** SCRaMbLE provides a model for how a modular genome library could enable combinatorial genome engineering — a principle central to MoClo genome libraries.

**URL:** https://doi.org/10.1126/science.aaf4557

---

## 2. ORFeome and Gene Clone Collections

### 2.1 ASKA Library — Complete *E. coli* K-12 ORFeome

**Kitagawa et al., DNA Research, 2005** — National Institute of Genetics (NIG), Japan

The ASKA library (A Complete Set of *E. coli* K-12 ORF Archive) contains **4,122 individually cloned ORFs** from *E. coli* K-12:

- Each ORF is **His-tagged** at the N-terminus and **GFP-fused** at the C-terminus.
- Cloned into an expression vector under IPTG-inducible control with **LacIq** tight repression.
- **SfiI restriction sites** flank each ORF for easy transfer to other vectors.
- Two versions exist: with and without GFP fusion.

Applications include:
- Systematic protein production and purification
- Protein localization via GFP fluorescence
- Protein–protein interaction analysis
- DNA microarray construction

> **Key limitation:** Individual ORFs only — no intergenic/regulatory regions, no flanking context, and **not assembly-compatible** with modular cloning standards (MoClo, Golden Gate).

**Source:** Notion bibliography; File: `Complete_set_of_ORF_clones.txt`
**URL:** https://academic.oup.com/dnaresearch/article/12/5/291/350187

---

### 2.2 Keio Collection — Genome-wide single-gene knockout library

**Baba et al., Molecular Systems Biology, 2006** — NIG Japan

The Keio collection is the standard **single-gene deletion library** for *E. coli* K-12 BW25113:

- Targeted **4,288 ORFs**; successfully obtained knockouts for **3,985 genes**.
- **Two independent mutants** per gene (7,970 strains total) for reproducibility.
- Genes replaced with **kanamycin resistance cassette** flanked by FRT sites (λ Red recombination).
- FRT sites allow cassette removal, leaving an in-frame scar.
- **303 genes** where no mutant could be isolated → candidates for essential genes.

> **Key limitation:** Gene *deletions* only — does not provide cloned DNA parts for assembly.

**URL:** https://doi.org/10.1038/msb4100050

---

## 3. Early Clone Banks

### 3.1 Kohara Clone Bank — Physical map of *E. coli*

**Kohara, Akiyama & Isono, Cell, 1987**

The first **physical map** of the *E. coli* K-12 W3110 genome:

- **~3,400 ordered overlapping lambda phage clones** (~15 kb each) covering the entire **4.7 Mb** genome.
- Generated by restriction enzyme fingerprinting and ordering.
- Standard reference resource for >15 years before genome sequencing was routine.

> **Key limitation:** Lambda phage format — NOT modular, NOT assembly-compatible, difficult to manipulate individual regions.

---

## 4. Modular Cloning (MoClo) Toolkits for *E. coli*

### 4.1 EcoFlex — Multifunctional MoClo kit

**Moore et al., ACS Synthetic Biology, 2016** — Imperial College London

EcoFlex is a **MoClo-compatible** toolkit for *E. coli* synthetic biology:

- Libraries of characterized **promoters, RBSs, terminators, and ORFs**.
- Standardized Golden Gate assembly with Type IIS restriction enzymes (BsaI, BpiI).
- Hierarchical assembly: Lvl0 parts → Lvl1 transcriptional units → Lvl2 multi-gene constructs (up to ~33 kb).

> **Key limitation:** Designed for building *synthetic circuits* from selected parts — not a genome-tiling library.

**URL:** https://doi.org/10.1021/acssynbio.5b00227

---

### 4.2 Expanded MoClo Vector Set (2025)

**ACS Synthetic Biology, 2025**

Recent expansion adding MoClo-compatible **low-copy (p15A) and medium-copy (pBR322) destination vectors**, providing a **500-fold range** in expression levels alongside existing high-copy vectors. Useful for metabolic engineering and dual-plasmid systems.

---

## 5. Genome Engineering Techniques (Supporting Methods)

### 5.1 REXER & GENESIS

**Wang et al., Nature Protocols, 2020** — Chin Lab

Protocols for creating custom synthetic genomes in *E. coli*:
- **REXER**: single-step replacement of >100 kb genomic segments with synthetic DNA.
- **GENESIS**: iterative REXER for stepwise total genome replacement.

**URL:** https://doi.org/10.1038/s41596-020-00464-3

---

### 5.2 MAGE — Multiplex Automated Genome Engineering

**Wang et al., Nature, 2009** — Church Lab

Enables simultaneous modification of many genomic loci using synthetic oligonucleotides and λ Red recombination. Used in the design of the rE.coli-57 recoded genome.

---

### 5.3 CRISPR-Cas12a Multiplex Genome Editing

**Ao et al., Frontiers in Microbiology, 2018**

Multiplex genome editing method for *E. coli* based on CRISPR-Cas12a, enabling efficient multi-locus modifications.

**Source:** Notion bibliography — Relevance: "E coli genome adaptability"
**URL:** https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2018.02307/full

---

## 6. Summary Comparison

| Project | Year | Organism | Scale | Format | Modular? | Assembly-ready? |
|---------|------|----------|-------|--------|----------|-----------------|
| **Kohara Clone Bank** | 1987 | *E. coli* K-12 | 4.7 Mb (genome) | Lambda phage clones | ❌ | ❌ |
| **ASKA Library** | 2005 | *E. coli* K-12 | 4,122 ORFs | Individual plasmids | ❌ | ❌ |
| **Keio Collection** | 2006 | *E. coli* K-12 | 3,985 knockouts | Deletion strains | ❌ | N/A |
| **EcoFlex** | 2016 | *E. coli* | Toolkit (parts) | MoClo Lvl0–Lvl2 | ✅ | ✅ (circuits) |
| **rE.coli-57** | 2016 | *E. coli* MG1655 | 4.6 Mb (design) | 63 × 50 kb segments | ❌ | ❌ |
| **JCVI-syn3.0** | 2016 | *M. mycoides* | 531 kb | Synthetic genome | ❌ | ❌ |
| **Sc2.0** | 2017+ | *S. cerevisiae* | 12 Mb | Synthetic chromosomes | ✅ (SCRaMbLE) | ✅ |
| **Syn61** | 2019 | *E. coli* MDS42 | 4.0 Mb | Synthetic genome | ❌ | ❌ |
| **MoClo Genome Library** | **2026** | ***E. coli* MG1655** | **Full genome** | **MoClo Lvl0 tiles** | **✅** | **✅** |

---

## 7. The Gap

Despite decades of work, **no modular, assembly-compatible library of the *E. coli* genome** exists:

1. **Syn61** and **rE.coli-57** produced finished or designed genomes — but not interchangeable parts.
2. **ASKA** cloned all ORFs — but without intergenic regions, regulatory context, or modular assembly compatibility.
3. **Keio** provides knockouts — but no cloned DNA.
4. **Kohara** covered the genome — but in a non-modular lambda phage format.
5. **EcoFlex** is MoClo-compatible — but is a parts toolkit, not a genome-tiling library.

A **MoClo-tiled genome library** — where every position in the genome is represented by standardized, interchangeable Level 0 parts with defined overhangs — would enable:

- **Combinatorial genome assembly**: mix-and-match tiles from different strains or designs
- **Chimeric constructs**: swap individual genes or regulatory regions while maintaining genomic context
- **Rapid prototyping**: assemble custom genome segments from a library of pre-built parts
- **Evolutionary studies**: create defined genomic variants for experimental evolution

This is the goal of the MoClo Genome Library project (EXP_001).

---

## References

1. Fredens, J., et al. "Total synthesis of Escherichia coli with a recoded genome." *Nature* 569, 514–518 (2019).
2. Ostrov, N., et al. "Design, synthesis, and testing toward a 57-codon genome." *Science* 353, 819–822 (2016).
3. Hutchison, C. A., et al. "Design and synthesis of a minimal bacterial genome." *Science* 351, aad6253 (2016).
4. Richardson, S. M., et al. "Design of a synthetic yeast genome." *Science* 355, 1040–1044 (2017).
5. Kitagawa, M., et al. "Complete set of ORF clones of Escherichia coli ASKA library." *DNA Research* 12, 291–299 (2005).
6. Baba, T., et al. "Construction of Escherichia coli K-12 in-frame, single-gene knockout mutants: the Keio collection." *Molecular Systems Biology* 2, 2006.0008 (2006).
7. Kohara, Y., Akiyama, K. & Isono, K. "The physical map of the whole E. coli chromosome." *Cell* 50, 495–508 (1987).
8. Moore, S. J., et al. "EcoFlex: A Multifunctional MoClo Kit for E. coli Synthetic Biology." *ACS Synthetic Biology* 5, 1059–1069 (2016).
9. Wang, K., et al. "Creating custom synthetic genomes in Escherichia coli with REXER and GENESIS." *Nature Protocols* 15, 2349–2376 (2020).
10. Wang, H. H., et al. "Programming cells by multiplex genome engineering and accelerated evolution." *Nature* 460, 894–898 (2009).
11. Ao, X., et al. "A Multiplex Genome Editing Method for Escherichia coli Based on CRISPR-Cas12a." *Frontiers in Microbiology* 9, 2307 (2018).
