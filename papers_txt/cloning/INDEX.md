# Cloning — Paper Index

Full summaries for 4 papers in this collection.

---

## Design and synthesis of a minimal bacterial genome
**File:** `Design_and_synthesis_of_a.txt`
**Subjects:** Cloning
**URL:** https://www.science.org/doi/10.1126/science.aad6253

Hutchison, Venter et al. (2016). Reports the creation of **JCVI-syn3.0**, a *Mycoplasma mycoides* cell with a 531 kbp synthetic genome — smaller than any autonomously replicating cell found in nature. Through four iterative design-build-test cycles starting from the 1,079 kbp syn1.0, the team used global Tn5 transposon mutagenesis to classify genes as essential, nonessential, or quasi-essential (needed for robust growth but not absolute viability). The final genome encodes 438 proteins and 35 RNAs (473 genes total), with a ~180 min doubling time. Key challenges included identifying synthetic lethal pairs (redundant genes for essential functions) and quasi-essential genes whose deletion impairs growth without killing the cell. Unexpectedly, 149 genes of unknown function were retained, highlighting undiscovered biology essential for life. The genome was assembled hierarchically: oligonucleotides → 1.4 kb fragments → 7 kb cassettes → one-eighth genome segments → full genome, all in yeast, then transplanted into *M. capricolum*.

---

## The physical map of the whole E. coli chromosome: Application of a new strategy for rapid analysis and sorting of a large genomic library
**File:** `The_physical_map_of_the.txt`
**Subjects:** Cloning
**URL:** https://www.cell.com/cell/abstract/0092-8674(87)90503-4

Kohara, Akiyama & Isono (1987). Landmark paper constructing the first **physical map of the entire *E. coli* chromosome**. ~3,400 lambda phage clones containing overlapping segments of the 4,700 kb genome were isolated and characterized using a novel mass-analysis strategy: partial restriction digests for 8 six-base-recognizing enzymes were sized by hybridization with a vector probe (analogous to nucleotide sequencing). A computer program sorted clones into overlapping groups, which were then linked via mass hybridization. The resulting "Kohara clone bank" became a standard resource for *E. coli* genetics for over 15 years, enabling rapid isolation of any gene with a known map position. However, the library is **not modular** — clones are ordered but overlapping, not designed for reassembly or interchange.

---

## Total synthesis of Escherichia coli with a recoded genome
**File:** `Total_synthesis_of_Escherichia_coli.txt`
**Subjects:** Cloning
**URL:** https://www.nature.com/articles/s41586-019-1192-5

Fredens, Wang, Chin et al. (2019). Reports the creation of **Syn61**, the first *E. coli* with a fully synthetic 4.0 Mb genome. All 18,214 instances of 3 target codons (TCG → AGC, TCA → AGT, TAG → TAA) were removed through genome-wide synonymous codon compression, creating a 61-codon organism. The genome was built using a convergent total synthesis: the designed genome was disconnected into 8 sections (~0.5 Mb each), 37 fragments (~100 kb), and ~10 kb stretches. Assembly used REXER (Replicon Excision for Enhanced Genome Engineering) iterated via GENESIS, complemented by directed conjugation to merge sections. Only 7 positions required corrections from the initial design. Syn61 grows ~1.6× slower than wild-type MDS42 in LB. The freed codons enable deletion of their cognate tRNAs (serT, serU) and release factor prfA, opening the genetic code for non-canonical amino acid incorporation via reassigned codons.

---

## Design, synthesis, and testing toward a 57-codon genome
**File:** `Design,_synthesis,_and_testing_toward.txt`
**Subjects:** Cloning
**URL:** https://www.science.org/doi/10.1126/science.aaf3639

Ostrov, Church et al. (2016). Describes the computational design and partial experimental validation of **rE.coli-57**, a 3.97 Mb *E. coli* genome in which all 62,214 instances of 7 codons (AGA, AGG, AGC, AGU, UUA, UUG, UAG) are replaced with synonymous alternatives. The genome was parsed into 87 segments of ~50 kb each, which were synthesized and individually tested by episomal expression followed by chromosomal deletion of the corresponding wild-type region. At publication, 55 segments (63% of the genome, 2,229 genes) had been validated. 91% of essential genes retained functionality, and only 13 lethal "design exceptions" were found. Fitness impairment was generally limited (<10% doubling time increase). A troubleshooting pipeline was developed to identify and fix lethal codon changes — e.g., synonymous substitutions that disrupted overlapping promoters or mRNA secondary structures. The project was not fully assembled into a single organism at publication time.

---
