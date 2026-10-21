# Agent Papers Index

Papers downloaded and verified by the AI assistant during conversations.
Each paper was cited by the assistant and its claims were verified against the actual text.

---

## Li et al. 2010 — An improved calcium chloride method preparation and transformation of competent cells
- **Authors:** Xiaowei Li, Xin Sui, Yan Zhang, Yepeng Sun, Yan Zhao, Ying Zhai, Qingyu Wang (Jilin University, Changchun, PR China)
- **Year:** 2010
- **Journal:** African Journal of Biotechnology 9(50):8549–8554
- **DOI:** 10.5897/AJB10.105
- **Retrieved:** 2026-09-24 (open access, AJOL direct PDF; `pdftotext -layout` extract). No paywall.
- **Cited in context of:** EXP_006 — cross-checking the CaCl₂ concentrations in the Pawlowski protocols.io protocol against an independent, systematically optimised source.
- **Key content verified (direct quotes):**
  - CaCl₂ titration is systematic: "We used 0, 25, 50, 75, 100, 125, 150 and 200 mmol/l icecold CaCl2 solution to prepare the competent cells and then transformed with pUC19 to test the transformation efficiency."
  - Optimum and the falloff: "the transformation efficiency of competent cells increased together with the concentration of CaCl2 solution and reached the maximum when the concentration 75 mmol/l, then decreased rapidly when the concentration exceeded 100 mmol/l."
  - Abstract summary: "the optimal transformation efficiency were obtained when the concentration of CaCl2 was 75 mmol/l, OD600 of the culture meets 0.35 to 0.45, the temperature of rotation was 4°C, rotation speed was 1000 g and rotation time was 5 min."
  - Glycerol effect: "the transformation efficiency would increase about 10 to 30 times when adding 15% glycerine into CaCl2 solution."
  - Efficiency reached: "the transformation efficiency could average reach as high as 1.5 × 10⁸" (cfu/µg, pUC19, DH5α).
  - Baseline comparator M1 "was prepared according to the classical CaCl2 method" of Sambrook & Russell (2001).
- **Relevance to EXP_006:** 0 mM gives no competence, so the "10 mM CaCl₂" line in the Pawlowski Materials list is not merely suboptimal — it sits far below the useful range. 75–100 mM is the plateau; the protocol's 100 mM wash and 85 mM freezing solution both fall inside it.
- **File:** `Li_2010_improved_CaCl2_competent_cells.txt` (PDF: `../agent_papers/Li_2010_improved_CaCl2_competent_cells.pdf`)

---

## Smit & van Elsas 1990 — Determination of plasmid transfer frequency in soil: Consequences of bacterial mating on selective agar media
- **Authors:** E. Smit, J.D. van Elsas (Institute for Soil Fertility Research, Wageningen, NL)
- **Year:** 1990
- **Journal:** Current Microbiology 21:151–157
- **DOI:** 10.1007/BF02091834
- **Retrieved:** 2026-07-17 (Sci-Hub mirror `sci-hub.ee` → `sci.bban.top` PDF; `pdftotext -layout` extract). Unpaywall: closed, no OA copy.
- **Cited in context of:** plate mating / post-mating conjugation as an artifact inflating transconjugant counts.
- **Key content verified (direct quotes):**
  - Threshold: "the maximum number of donor and recipient cells per Petri dish that could be plated without conjugation taking place was about 10⁵ (20°C curve)" — x-axis is log √(D×R).
  - "The number of parental cells that could be plated without conjugation taking place at 4°C was about 10⁶, tenfold higher than at 20°C."
  - "The percentage of the total number of transconjugants resulting from matings on selective plates without nalidixic acid was found to vary from 30 to 85% depending on the number of parent cells."
  - "Matings on plates did not occur at low donor and recipient cell densities (< 10⁴ cells per plate)."
  - Nx fix: "The use of Nx (with Rp) almost completely inhibited matings between freshly cultured donor and recipient cells (Table 1)."
  - Strains/plasmid: *Pseudomonas fluorescens* R2f + broad-host-range **RP4** (Km/Tc/Ap); recipients = spontaneous Rp^r Sm^r and Rp^r Nx^r mutants of R2f.
- **File:** `Smit_1990_plate_mating_artifact_soil_plasmid_transfer.txt` (PDF: `../agent_papers/Smit_1990_plate_mating_artifact_soil_plasmid_transfer.pdf`)

---

## Walter, Porteous, Fieland, Seidler & Armstrong 1991 — Formation of transconjugants on plating media following in situ conjugation experiments
- **Authors:** Michael V. Walter, L. Arlene Porteous, Valerie P. Fieland, Ramon J. Seidler, John L. Armstrong (US EPA / ManTech, Environmental Research Laboratory-Corvallis, OR)
- **Year:** 1991
- **Journal:** Canadian Journal of Microbiology 37(9):703–707
- **DOI:** 10.1139/m91-119
- **Retrieved:** 2026-07-17 (Sci-Hub mirror `sci-hub.ee` → `sci.bban.top` PDF; `pdftotext -layout` extract + page-image verification of Tables 1–2). Unpaywall: closed, no OA copy.
- **Cited in context of:** plate mating artifact; nalidixic acid counter-selection.
- **Key content verified (direct quotes):**
  - "Conjugation on agar plates following mating trials can cause transconjugant numbers to be overestimated."
  - "Addition of nalidixic acid to selective media reduced the number of transconjugants from broth matings by 10-fold and the number of transconjugants from plate mating after incubation in broth by 100-fold." (Body text instead says plate mating dropped "nearly three orders of magnitude", 4.87→2.36 log₁₀ cfu/mL — abstract/body discrepancy.)
  - "the addition of nalidixic acid to selective agar eliminated all plate matings" — scope per Discussion: "By use of Nal, plate mating can be eliminated when plating from both soil and soil slurry environments, and significantly reduced when plating from broth."
  - Nonsterile soil: "in the absence of Nal, about 4.00 log cfu/g were detected at 0, 2, and 4 h. No transconjugants were detected when samples were plated onto media containing Nal" → "transconjugants formed only as a result of plate mating."
  - Strains/plasmid: *Pseudomonas cepacia*; donor = proline auxotroph with **R388::Tn1721** (IncW; Tp^r Tc^r); recipient = prototroph resistant to 500 µg/mL nalidixic acid.
- **File:** `Walter_1991_transconjugant_formation_on_plating_media.txt` (PDF: `../agent_papers/Walter_1991_transconjugant_formation_on_plating_media.pdf`)

---

## Vo, Ronda, Klompe, Chen, Acree, Wang & Sternberg 2021 — CRISPR RNA-guided integrases for high-efficiency, multiplexed bacterial genome engineering
- **Authors:** Phuc Leo H. Vo, Carlotta Ronda, Sanne E. Klompe, Ethan E. Chen, Christopher Acree, Harris H. Wang, Samuel H. Sternberg
- **Year:** 2021
- **Journal:** Nature Biotechnology 39(4):480–489
- **DOI:** 10.1038/s41587-020-00745-y
- **Retrieved:** 2026-06-25 (user-supplied PDF from Downloads; `pdftotext -layout` extract)
- **Cited in context of:** CAST/INTEGRATE DNA-tape design ([CAST_DNA_tape_DESIGN.md](../plasmids/Klompe2019_VchCAST/CAST_DNA_tape_DESIGN.md)) — optimized integration efficiency, target immunity, orthogonal integrases for iterative insertions, and integrase/recombinase resets.
- **Key content verified (direct quotes):**
  - Optimized system: "achieves highly accurate and marker-free DNA integration of up to 10 kilobases at ~100% efficiency in bacteria."
  - Target immunity: "Tn7 and Tn7-like transposons exhibit target immunity, whereby integration is prevented at target sites already containing another transposon copy"; the *V. cholerae* transposon "also exhibited target immunity, with ~20% relative efficiency at target sites ~5 kb away" (restored at a site >1 Mbp from the pre-existing insertion).
  - Orthogonality: developed **ShoINT** (Type V-K, *Scytonema hofmannii*); each RNA-guided integrase was "exclusively active on its respective" cognate transposon substrate, enabling iterative insertions without re-mobilizing the pre-existing mini-Tn.
  - Single-plasmid **pSPIN** system; self-targeting mitigated via target immunity (**pSPIN-R**); multiplexed insertions + **Cre-LoxP** deletions.
- **File:** `Vo_2021_INTEGRATE_high_efficiency_multiplexed.txt`

---

## Chasteen, Ayriss, Pavlik & Bradbury 2006 — Eliminating helper phage from phage display
- **Authors:** L. Chasteen, J. Ayriss, P. Pavlik, A. R. M. Bradbury
- **Year:** 2006
- **Journal:** Nucleic Acids Research 34(21):e145 (open access)
- **DOI:** 10.1093/nar/gkl772 · **PMID:** 17088290 · **PMC:** PMC1693883
- **Retrieved:** 2026-06-16 (Europe PMC full-text XML; PDF endpoint returned empty, text extract only)
- **Cited in context of:** Note_005 toxin/antitoxin two-phage design — precedent for stripping M13 so all phage proteins are supplied in *trans*, and for controlling display valency.
- **Key content verified (direct quotes):**
  - Bacterial packaging cell lines replace helper phage: "we have eliminated the need to add helper phage by using 'bacterial packaging cell lines'... These cell lines contain M13-based helper plasmids that express phage packaging proteins which assemble phagemid particles as efficiently as helper phage, but without helper phage contamination."
  - Helper-plasmid design: based on M13mp19, "the M13 origin was removed and replaced with the p15a origin... the polylinker and lac gene... were replaced by the chloramphenicol resistance gene... to create M13cp."
  - Why helper DNA is not packaged: "The absence of packaging signals in these helper plasmids prevents their DNA from being packaged"; genome's single packaging site selected by evolution so "elimination provides no alternative signals."
  - Genome integration failed: "we attempted to integrate portions of M13 into the E.coli genome by Tn5 transposition... none was able to package phagemid DNA."
  - Valency control via g3 form: full-length g3 (M13cp) = monovalent; truncated CT-domain-only g3 (M13cp-CT) = highest display; Δg3 (M13cp-dg3) = multivalent; sg3 (4 stops) gave only 10⁶/ml.
  - Titers: M13cp gave 10¹¹⁻¹² phagemid particles/ml, equal to M13K07 helper phage.
- **File:** `Chasteen_2006_eliminating_helper_phage_from_phage_display.txt`

---

## Klasse 2014 — Neutralization of Virus Infectivity by Antibodies: Old Problems in New Perspectives
- **Authors:** P. J. Klasse
- **Year:** 2014
- **Journal:** Advances in Biology 2014:157895 (open access)
- **DOI:** 10.1155/2014/157895 · **PMID:** 27099867 · **PMC:** PMC4835181
- **Retrieved:** 2026-06-03 (PMC full text)
- **Cited in context of:** Weizmann interview prep (Theme 5) — the dedicated review on mechanisms of antibody neutralization of viruses.
- **Key content verified (direct quotes):** Defines neutralization as "reduction in viral infectivity by the binding of antibodies to the surface of viral particles (virions), thereby blocking a step in the viral replication cycle that precedes virally encoded transcription or synthesis." Mechanisms: block attachment ("prevent the virions from attaching"); post-attachment neutralization ("coreceptor engagement, endocytosis, fusion, or penetration"); prevent conformational change/genome extrusion; aggregation ("dome-shaped curve"); occupancy/coating threshold ("minimum neutralizing occupancy would constitute the neutralization threshold"; "occupancy is the equivalent of stoichiometry"); intracellular TRIM21 (naked viruses only — "would not affect... enveloped viruses"); bivalency/cross-linking enabling PAN; single-hit vs multi-hit molecularity.
- **File:** `Klasse_2014_neutralization_virus_infectivity.txt`

---

## Heesters, Myers & Carroll 2014 — Follicular dendritic cells: dynamic antigen libraries
- **Authors:** Balthasar A. Heesters, Riley C. Myers, Michael C. Carroll
- **Year:** 2014
- **Journal:** Nat Rev Immunol 14:495-504
- **DOI:** 10.1038/nri3689 · **PMID:** 24948364
- **Downloaded:** 2026-06-03 (Sci-Hub)
- **Cited in context of:** Weizmann interview prep (Theme 4) — how FDCs capture, retain, and replenish antigen for GC selection.
- **Key content verified (direct quotes):** FDCs "retain intact opsonized antigen for long periods... generally accepted that FDCs can retain antigen for up to 12 months... estimated to retain antigen for years"; "intact opsonized antigen can still be observed 3 months after antigen injection." Delivery route set by size: "antigens... smaller than 70 kDa (approximately 5.5 nm) flow directly to the FDCs via the conduit network," larger complexes via SCS macrophages, "intact bacteria, viruses and other large antigens are captured and processed in the medulla." FDCs retain intact virions (HIV reservoir), capture ICs via CR1/CR2 (CD35/CD21) + FcγRIIb, internalize into a non-degradative recycling endosome and periodically re-display. NOTE: review gives retention *duration* + 70 kDa size cutoff, but **no per-FDC molecule count**.
- **File:** `Heesters_Carroll_2014_FDC_antigen_libraries.txt`

---

## Di Noia & Neuberger 2007 — Molecular mechanisms of antibody somatic hypermutation
- **Authors:** Javier M. Di Noia, Michael S. Neuberger
- **Year:** 2007
- **Journal:** Annu Rev Biochem 76:1-22
- **DOI:** 10.1146/annurev.biochem.76.061705.090740 · **PMID:** 17328676
- **Downloaded:** 2026-06-02 (Sci-Hub)
- **Cited in context of:** Weizmann interview prep (Theme 4, AID-focused review) — exact mechanism of AID/SHM.
- **Key content verified (direct quotes):** SHM introduces substitutions "at a frequency of around 10⁻³ per base pair per generation into a domain that starts some 150 nucleotides downstream of the IgV promoter and extends over about 2 kb." AID acts by "targeted deamination of deoxycytidine residues" (dC→dU) on single-stranded DNA exposed during transcription, "on the transcribed or non-transcribed DNA strand with equal probability"; "the targeting of individual bases is, however, not random," with C:G hot spots in a WRCY consensus and germline codon usage concentrating hotspots in CDRs. U:G lesion then processed three ways (replication→transitions; UNG→transversions; MSH2/MSH6→pol η→A:T mutations).
- **File:** `DiNoia_Neuberger_2007_SHM_mechanisms.txt`

---

## Chaplin 2010 — Overview of the immune response
- **Authors:** David D. Chaplin
- **Year:** 2010
- **Journal:** J Allergy Clin Immunol 2010;125(2 Suppl 2):S3-23
- **DOI:** 10.1016/j.jaci.2009.12.980 · **PMID:** 20176265
- **Downloaded:** 2026-06-02 (Sci-Hub)
- **Cited in context of:** Weizmann interview prep (Theme 0 orientation review) — big-picture summary of innate + adaptive immunity for the synthetic germinal center project.
- **Key content verified:** Full review read. Covers self/nonself discrimination; innate vs adaptive features; hematopoietic lineages; MHC class I (endogenous→CD8) vs class II (exogenous→CD4) antigen presentation; T-cell development (thymic positive/negative selection, AIRE) and TCR/CD3 signaling + costimulation; CD4 subsets (Th1/Th2/Th17/Treg) and superantigens; B-cell development, allelic exclusion, receptor editing; **AID-driven class-switch recombination + somatic hypermutation in germinal centers**; T-dependent (CD40–CD40L) vs T-independent responses; secondary lymphoid tissue architecture (FDCs, HEVs, S1P egress); Jak/STAT cytokine signaling; innate effectors (TLRs, NLR/inflammasome, collectins, phagocytes, NK cells, 3-pathway complement); leukocyte adhesion cascade; apoptotic homeostasis; tolerance/autoimmunity/atopy.
- **File:** `Chaplin_2010_clean.txt` (column-aware extract; raw extract also at `Chaplin_2010_overview_immune_response.txt`)

---

## CATCH — Cas9-Assisted Targeting of CHromosome segments
- **Authors:** Wenjun Jiang, Xuejin Zhao, Tslil Gabrieli, Chunbo Lou, Yuval Ebenstein, Ting F. Zhu
- **Year:** 2015
- **Journal:** Nature Communications
- **DOI:** 10.1038/ncomms9101
- **Downloaded:** 2026-02-26
- **Cited in context of:** Who has worked on cloning large E. coli genome portions
- **Key finding verified:** CATCH enables targeted cloning of **up to 100 kb** bacterial genomic sequences in a single step. Cas9 excises target segments from chromosomes in vitro (in agarose gel plugs), then Gibson assembly ligates them into a cloning vector. Demonstrated on E. coli genome segments containing lacZ. No size-dependent loss of cloning efficiency up to 100 kb.
- **Zotero:** [`FA5R6IR3`](zotero://select/library/items/FA5R6IR3) · [📄 local PDF](../agent_papers/CATCH_Cas9_targeting_chromosome_segments.pdf)
- **File:** `CATCH_Cas9_targeting_chromosome_segments.txt`

---

## CAPTURE — Cas12a-Assisted Precise Targeted Cloning Using In Vivo Cre-Lox Recombination
- **Authors:** Behnam Enghiad, Chunshuai Huang, Fang Guo, Guangde Jiang, Bin Wang, S. Kasra Tabatabaei, Teresa A. Martin, Huimin Zhao
- **Year:** 2021
- **Journal:** Nature Communications
- **DOI:** 10.1038/s41467-021-21275-4
- **Downloaded:** 2026-02-26
- **Cited in context of:** Large DNA fragment cloning methods, alternatives to CATCH
- **Key finding verified:** CAPTURE clones **10–113 kb** genomic fragments with **~100% efficiency** regardless of GC-content. Uses Cas12a (staggered cuts) + T4 polymerase exo+fill-in assembly + in vivo Cre-lox circularization in E. coli. Cloned **47 BGCs** from 14 Streptomyces and 3 Bacillus species, including 3 BGCs **>100 kb** (100, 103, 113 kb). In vivo circularization was **~150-fold** more efficient than in vitro for 73 kb DNA. Cloning takes **3–4 days**. Table 1 lists all 43 uncharacterized BGCs with sizes and efficiencies.
- **File:** `CAPTURE_Cas12a_targeted_cloning_Zhao_2021.txt`

---

## CReATiNG — Building Synthetic Chromosomes from Natural DNA
- **Authors:** Alessandro L. V. Coradini, Christopher Ne Ville, Zachary A. Krieger, Joshua Roemer, Cara Hull, Shawn Yang, Daniel T. Lusk, Ian M. Ehrenreich
- **Year:** 2023
- **Journal:** Nature Communications
- **DOI:** 10.1038/s41467-023-44112-2
- **Downloaded:** 2026-02-26
- **Cited in context of:** Building modular genome libraries from natural DNA, closest concept to MoClo genome tiling
- **Key finding verified:** CReATiNG (Cloning, Reprogramming, and Assembling Tiled Natural Genomic DNA) builds synthetic chromosomes from **cloned natural chromosome segments** in yeast. Uses Cas9 to excise **51–64 kb segments** from donor chromosomes, captures them in BAC/YAC vectors (pASC1) with programmable flanking adapters, then assembles segments via homologous recombination in recipient yeast cells. Demonstrated on S. cerevisiae ChrI (230 kb): cloned 3 segments at **93% efficiency** (14/15 colonies), assembled with **80% efficiency**. Built **27 inter-strain/inter-species recombinant chromosomes**. Deleted **39% of ChrI** (91.7 kb) in a multiplex deletion experiment with 11 segments (3.8–21 kb each). Yeast-only system — **NOT applicable to E. coli**, segments are **NOT MoClo-compatible**.
- **File:** `Building_synthetic_chromosomes_CReATiNG_Ehrenreich_2023.txt`

---

## BASIS/CGS — Continuous Synthesis of E. coli Genome Sections (abstract only)
- **Authors:** Jérôme F. Zürcher, Askar A. Kleefeldt, Louise F. H. Funke, Jakob Birnbaum, Julius Fredens, et al. (Chin Lab)
- **Year:** 2023
- **Journal:** Nature
- **DOI:** 10.1038/s41586-023-06268-1
- **Downloaded:** 2026-02-26 (PDF not available — verified from abstract only)
- **Cited in context of:** Large-scale E. coli genome synthesis, megabase DNA assembly
- **Key finding (from abstract):** **BASIS** (BAC stepwise insertion synthesis) assembles megabase-scale DNA in E. coli episomes. Assembled **1.1 Mb of human DNA** including exons, introns, repetitive sequences, LINEs/SINEs. **CGS** (continuous genome synthesis) replaces sequential **100 kb stretches** of the E. coli genome with synthetic DNA. Synthesized **0.5 Mb** of the E. coli genome from 5 episomes in **10 days**. Authors estimate complete genome synthesis from functional designs in **<2 months** by parallelizing CGS.
- **Note:** ⚠️ Could not download PDF — claims verified from abstract only, not full text.

---

## Perelson & Oster — Theoretical Studies of Clonal Selection (shape-space foundation)
- **Authors:** Alan S. Perelson, George F. Oster
- **Year:** 1979
- **Journal:** J. Theor. Biol. 81:645–670
- **DOI:** 10.1016/0022-5193(79)90275-3
- **Downloaded:** 2026-04-10
- **Cited in context of:** EXP_003 affinity model — where the shape-space concept comes from
- **Key finding verified:** Introduces the "shape space" framework: antibodies and antigens are represented as points in an abstract multi-dimensional metric space, with recognition probability depending on the Euclidean/Hamming distance between them. Derives minimal antibody repertoire sizes (~10⁵–10⁶) from probabilistic matching arguments. **Does not specify a Gaussian affinity formula** — that comes later (Meyer-Hermann 2001). This paper is the conceptual foundation but the explicit `a(h) = exp(−(h/γ)^η)` form is Meyer-Hermann's.
- **File:** `Perelson_Oster_1979_shape_space_clonal_selection.txt`

---

## Meyer-Hermann et al. — Recycling Probability and Dynamical Properties of GC Reactions
- **Authors:** Michael Meyer-Hermann, Andreas Deutsch, Michal Or-Guil
- **Year:** 2001
- **Journal:** J. Theor. Biol. 210:265–285
- **DOI:** 10.1006/jtbi.2001.2297
- **Downloaded:** 2026-04-10
- **Cited in context of:** EXP_003 affinity model — the Gaussian `a(h)` formula and the L=4 choice
- **Key findings verified:**
  - Introduces the **Gaussian affinity function** `a = exp(−(h/Γ)^η)` on a shape-space lattice. This is the explicit form used in hyphasma and downstream GC simulations.
  - **Shape-space dimension `D = 4` is justified by a diffusion argument** (Section 2.5): with a max-mutation count `Nmax = 8` and a total centroblast population `Nc ≈ 12 000`, the number of lattice points inside a radius-8 sphere grows exponentially with `D`. For the diffusion process to cover the antigen before the centroblast population plateaus, `D = 4` is the upper bound. The authors explicitly say: "From the point of view of a pure diffusion process this is an upper bound for the shape space dimension." They check `D = 5, 6` and find effects <10%.
  - **Key caveat from the paper itself:** "We want to remind that we are dealing with a phenotype space in this model and that a genotype space probably requires a substantially higher dimension." — this is exactly what our EXP_003 simulation does (sequence-level, L=40).
  - The 1:3 to 1:7 beneficial:detrimental ratio often quoted for L=4 comes from this paper's nearest-neighbor counting in the D=4 lattice model.
- **File:** `Meyer-Hermann_2001_recycling_probability_GC.txt`

---

## Rothbauer et al. 2006 — Targeting and tracing antigens in live cells with fluorescent nanobodies
- **Authors:** Ulrich Rothbauer, Kourosh Zolghadr, Sergei Tillib, … Serge Muyldermans, M. Cristina Cardoso, Heinrich Leonhardt
- **Year:** 2006
- **Journal:** Nat Methods 3(11):887–9
- **DOI:** 10.1038/nmeth953 · **PMID:** 17060912
- **Downloaded:** 2026-06-11 (Sci-Hub)
- **Cited in context of:** Synthetic GC flowchart, subsystem 1 (bacterial display) — the foundational **anti-GFP nanobody (GFP-binding protein, "GBP")** whose sequence can be displayed on E. coli.
- **Key content verified (direct quotes):** "We fused the epitope-recognizing fragment of heavy-chain antibodies from *Camelidae* sp. with fluorescent proteins to generate fluorescent, antigen-binding nanobodies (chromobodies)." The single-domain **GFP-binding** nanobody (GBP) recognizes and traces GFP antigen in living cells "throughout S phase and mitosis." Text confirms "GFP-binding" nanobody used as the antigen-recognition module. This is the original GBP later commercialized as GFP-Trap.
- **File:** `Rothbauer_2006_fluorescent_nanobodies_chromobodies.txt`

---

## Kirchhofer et al. 2010 — Modulation of protein properties in living cells using nanobodies
- **Authors:** Axel Kirchhofer, Jonas Helma, Katrin Schmidthals, … Karl-Peter Hopfner, Ulrich Rothbauer
- **Year:** 2010 (online 2009-12-13)
- **Journal:** Nat Struct Mol Biol 17(1):133–8
- **DOI:** 10.1038/nsmb.1727 · **PMID:** 20010839
- **Downloaded:** 2026-06-11 (Sci-Hub)
- **Cited in context of:** Subsystem 1 — the **GFP-Enhancer and GFP-Minimizer** anti-GFP nanobodies (best-characterized, crystal structures), the recommended display candidate.
- **Key content verified (direct quotes):** "One nanobody could reversibly reduce GFP fluorescence by a factor of 5, whereas its displacement by a second nanobody caused an increase by a factor of 10." "Structural analysis of GFP–nanobody complexes revealed that the two nanobodies induce subtle opposing changes in the chromophore environment." Full text names them "**Enhancer**" (101 occurrences) and "**Minimizer**" (58); both are camelid VHH single-domain antibodies functional inside living cells. Sequences + structures are published.
- **File:** `Kirchhofer_2010_GFP_enhancer_minimizer_nanobodies.txt`

---

## Kubala et al. 2010 — Structural and thermodynamic analysis of the GFP:GFP-nanobody complex
- **Authors:** Marta H. Kubala, Oleksiy Kovtun, Kirill Alexandrov, Brett M. Collins
- **Year:** 2010
- **Journal:** Protein Sci 19(12):2389–401
- **DOI:** 10.1002/pro.519 · **PMID:** 20945358 · **PMC:** PMC3009406
- **Retrieved:** 2026-06-11 (Europe PMC full text)
- **Cited in context of:** Subsystem 1 — open-access source of the **explicit anti-GFP nanobody amino-acid sequence** + binding interface + specificity controls.
- **Key content verified (direct quotes):** "the GFP-nanobody can also **bind YFP**, it **cannot bind the closely related CFP** or other fluorescent proteins from the mFruit series." "we have engineered a CFP variant (**I146N**) that is also able to bind the GFP-nanobody with high affinity." Provides the VHH sequence (MeSH: Amino Acid Sequence) and ITC affinity data — useful specificity controls for the display readout (GFP+/YFP+, CFP− as a negative control).
- **Table II — the GBP1/Enhancer affinity compilation (verified 2026-10-21):** the often-quoted "0.23–0.59 nM" for the GFP-nanobody is **NOT one SPR measurement**; it is the span of three prior studies by three different methods, tabulated here. **SPR 0.32 nM** (their ref 30) · **SPR 0.23 nM** (their ref 6 = Rothbauer 2006, Nat Methods 3:887–889) · **quartz crystal microbalance 0.59 ± 0.11 nM** (their ref 4 = Kirchhofer 2010, NSMB 17:133–138) · **Octet interferometry 1.40 nM** (Kubala's own). Text: "The measured Kd of 1.4 nM is very similar to those reported previously (0.23–0.59 nM)". So a same-method (SPR) number for the Enhancer is **0.23–0.32 nM**, and any comparison with the Fridy LaG SPR values is still **cross-study**, different instruments and labs.
- **File:** `Kubala_2010_GFP_nanobody_complex_structure.txt`

---

## Zhang et al. 2020 — Structure-based engineering of anti-GFP nanobody tandems as ultra-high-affinity reagents for purification
- **Authors:** Ziyue Zhang, Yao Wang, Yu Ding, Motoyuki Hattori
- **Year:** 2020
- **Journal:** Sci Rep 10(1):6239
- **DOI:** 10.1038/s41598-020-62606-7 · **PMID:** 32277083 · **PMC:** PMC7148334
- **Downloaded:** 2026-06-11 (Sci-Hub PDF + Europe/PMC full text)
- **Cited in context of:** Subsystem 1 (bacterial display) — a **second anti-GFP nanobody (LaG16)** with measured affinity + crystal structure, and the non-overlapping-epitope tandem strategy. User-requested reference.
- **Key content verified (direct quotes):** "we report the crystal structure of **GFPuv in complex with the anti-GFP nanobody LaG16 at 1.67 Å** resolution." "The LaG16 binding site was on the **opposite side of the GFP β-barrel from the binding site of the GFP-enhancer**… indicating that the GFP-enhancer and LaG16 can bind to GFP together." Affinities by ITC: "**GFPuv exhibits a Kd of 6.7 nM with LaG16 and a Kd of 24.3 nM with GFP-enhancer**"; the GFP-enhancer-(GGGGS)₄-LaG16 tandem reached **Kd 0.5 nM**. Nanobodies expressed in *E. coli* Rosetta(DE3), His-tagged; LaG16 model built on PDB 3K1K (the Kirchhofer Enhancer). PDB 6LR7. Relevant control note: LaG16 and GFP-Enhancer bind **non-overlapping epitopes** — useful if displaying a tandem or doing dual-readout.
- **File:** `Zhang_2020_antiGFP_nanobody_tandems_purification.txt`

---

## De Genst et al. 2004 — Chemical basis for the affinity maturation of a camel single domain antibody
- **Authors:** Erwin De Genst, Fabian Handelberg, Annemieke Van Meirhaeghe, Samuel Vynck, Remy Loris, Lode Wyns, Serge Muyldermans
- **Year:** 2004
- **Journal:** J Biol Chem 279(51):53593–53601
- **DOI:** 10.1074/jbc.M407843200 · **PDB:** 1XFP
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Synthetic GC nanobody proof-of-concept — the canonical *affinity-maturation* trajectory of a nanobody with structural/thermodynamic dissection (benchmark for "can our GC evolve a nanobody").
- **Key content verified (direct quotes):** The anti-lysozyme VHH "cAb-Lys3, accumulated **five amino acid substitutions in CDR1 and CDR2** upon maturation against lysozyme." "Three of these residues have hydrophobic side chains, replacing serines, and participate in the **hydrophobic core of the CDR1** in the mature antibody." Maturation "relies on events **late in the reaction pathway**… a limited perturbation of **ka** and a significantly **decreased kd** upon maturation." "binding reactions and the maturation event are predominantly **enthalpically driven**." Crystal structure of the germline-CDR2-restored mutant deposited as **PDB 1XFP**. Compares to classic affinity-maturation cases (anti-hapten 48G7 pre-organization; HyHEL10 increased complementarity).
- **File:** `DeGenst_2004_affinity_maturation_camel_VHH.txt`

---

## De Genst et al. 2006 — Molecular basis for the preferential cleft recognition by dromedary heavy-chain antibodies
- **Authors:** Erwin De Genst, Karen Silence, Klaas Decanniere, Katja Conrath, Remy Loris, Jörg Kinne, Serge Muyldermans, Lode Wyns
- **Year:** 2006
- **Journal:** PNAS 103(12):4586–4591
- **DOI:** 10.1073/pnas.0505379103
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Synthetic GC nanobody proof-of-concept — the definitive epitope/paratope map of anti-HEWL nanobodies and why nanobodies bind enzyme active-site clefts.
- **Key content verified (direct quotes):** "**Eight single domain antigen-binding fragments** of HCAbs (VHH) with **nanomolar affinities for lysozyme** were isolated from three immunized dromedaries. **Six of eight VHHs compete with small lysozyme inhibitors**" (i.e. active-site binders); the same ~85% active-site proportion appears in the polyclonal HCAb serum response. "The crystal structures of **six VHHs in complex with lysozyme**" were solved. Mechanism: "the compact prolate shape of VHH… presents a **large convex paratope, predominantly formed by the H3 loop** and interacting… into the **concave lysozyme substrate-binding pocket**." Frames HEWL as the canonical model antigen ("eleven different crystal structures of Fab or Fv antibody fragments… in complex with lysozyme, collected over the last two decades"). Epitopes cluster in two nonoverlapping regions.
- **File:** `DeGenst_2006_cleft_recognition_dromedary_HCAb.txt`

---

## Decanniere et al. 2001 — Degenerate interfaces in antigen-antibody complexes
- **Authors:** Klaas Decanniere, T. R. Transue, Aline Desmyter, D. Maes, Serge Muyldermans, Lode Wyns
- **Year:** 2001
- **Journal:** J Mol Biol 313(3):473–478
- **DOI:** 10.1006/jmbi.2001.5075 · **PDB:** 1JTO
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Supporting structure for the cAb-Lys3–HEWL paratope (the 1JTO complex referenced as the lysozyme:nanobody example in Kubala 2010).
- **Key content verified (direct quotes):** Reports "the camel variable domain antibody fragment **cAb-Lys3** and its antigen **hen egg white lysozyme**" — multiple complexes in the asymmetric unit plus "a third cAb-Lys3–hen lysozyme complex in a different crystal form," showing the interface is reproduced across crystal forms (degenerate/robust interface).
- **File:** `Decanniere_2001_degenerate_interfaces_antigen_antibody.txt`

---

## Desmyter et al. 1996 — Crystal structure of a camel single-domain VH antibody fragment in complex with lysozyme
- **Authors:** Aline Desmyter, T. R. Transue, M. Arbabi Ghahroudi, M.-H. Dao Thi, F. Poortmans, R. Hamers, Serge Muyldermans, Lode Wyns
- **Year:** 1996
- **Journal:** Nat Struct Biol 3(9):803–811
- **DOI:** 10.1038/nsb0996-803 · **PDB:** 1MEL
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** The **first-ever VHH–antigen crystal structure** (cAb-Lys3 long CDR3 inserting into the lysozyme active site) — historical origin of the nanobody-paratope paradigm.
- **Key content verified (OCR'd 2026-06-15, tesseract):** "Crystal structure of a camel single-[domain VH antibody fragment in complex] with lysozyme." Confirms the defining feature: the **CDR3 (H3) loop is long (~14 aa avg)** and **deviates from canonical structure**, with part of CDR3 inserting toward the lysozyme active site. Original scanned PDF was image-only; full text now available via OCR (minor OCR artifacts present).
- **File:** `Desmyter_1996_cAbLys3_lysozyme_VHH_complex_structure.txt` (OCR'd full text)

---

## Akiba et al. 2019 — Structural and thermodynamic basis for recognition of the HEWL substrate-binding cleft by a single-domain antibody
- **Authors:** Hiroki Akiba, Hiroko Tamura, Masato Kiyoshi, Saeko Yanaka, Kenji Sugase, Jose M. M. Caaveiro, Kouhei Tsumoto
- **Year:** 2019 · **Journal:** Sci Rep 9:15481 · **DOI:** 10.1038/s41598-019-50722-y
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Synthetic GC nanobody proof-of-concept — modern, high-quality structural+thermodynamic dissection of an anti-HEWL VHH that binds the active-site cleft; template for *measuring* evolved binders.
- **Key content verified (direct quote):** "Structural and thermodynamic basis for the recognition of the substrate-binding cleft on hen egg lysozyme by a single-domain antibody." VHHs "developed from heavy chain-only antibodies of camelids"; high affinity/specificity rivaling IgGs despite small size.
- **File:** `Akiba_2019_singledomain_Ab_HEWL_cleft_thermodynamics.txt`

---

## Amit, Mariuzza, Phillips & Poljak 1986 — Three-dimensional structure of an antigen-antibody complex at 2.8 Å resolution
- **Authors:** A. G. Amit, R. A. Mariuzza, S. E. V. Phillips, R. J. Poljak
- **Year:** 1986 · **Journal:** Science 233(4765):747–753 · **DOI:** 10.1126/science.2426778
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Reading-list Tier 1 — the **first antibody–protein-antigen co-crystal structure** (Fab D1.3–lysozyme); historical reason HEWL became the model antigen for epitope/affinity-maturation studies.
- **Key content verified (direct quote):** describes the "complex between an antigen (lysozyme) and the Fab" (D1.3).
- **File:** `Amit_1986_D13_lysozyme_first_Ab_antigen_structure.txt`

---

## Goodnow et al. 1988 — Altered immunoglobulin expression and functional silencing of self-reactive B lymphocytes in transgenic mice
- **Authors:** Christopher C. Goodnow, J. Crosbie, S. Adelstein, et al.
- **Year:** 1988 · **Journal:** Nature 334:676–682 · **DOI:** 10.1038/334676a0
- **Downloaded:** 2026-06-15 (Sci-Hub; OCR'd, scanned original)
- **Cited in context of:** Reading-list Tier 1 — the **MD4 anti-HEL BCR-transgenic** model (B-cell tolerance/anergy), foundational HEL-BCR tool.
- **Key content verified (OCR'd direct quote):** title "functional silencing of self-reactive B lymphocytes in transgenic mice."
- **File:** `Goodnow_1988_MD4_antiHEL_transgenic_tolerance.txt`

---

## Phan et al. 2006 — High affinity germinal center B cells are actively selected into the plasma cell compartment
- **Authors:** Tri Giang Phan, Dean Paus, Tyani D. Chan, et al. (Robert Brink lab)
- **Year:** 2006 · **Journal:** J Exp Med 203(11):2419–2424 · **DOI:** 10.1084/jem.20061254
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Reading-list Tier 1 — the **SWHEL** system; clearest demonstration that HEL affinity directly governs GC output (affinity maturation readout).
- **Key content verified:** discusses "maturation of the immune response" and selection of high-affinity GC B cells into the plasma-cell compartment (SWHEL/HEL).
- **File:** `Phan_2006_SWHEL_high_affinity_GC_to_plasma_cell.txt`

---

## Paus et al. 2006 — Antigen recognition strength regulates the choice between extrafollicular plasma cell and germinal center B cell differentiation
- **Authors:** Dean Paus, Tri Giang Phan, Tyani D. Chan, et al. (Robert Brink lab)
- **Year:** 2006 · **Journal:** J Exp Med 203(4):1081–1091 · **DOI:** 10.1084/jem.20060087
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Reading-list Tier 1 — sets the **affinity threshold for GC entry** (SWHEL/HEL); selection-stringency expectations for a synthetic GC.
- **Key content verified:** plasma cells "generated from the rapid extra-[follicular response]" vs GC fate as a function of antigen recognition strength.
- **File:** `Paus_2006_antigen_strength_GC_vs_extrafollicular.txt`

---

## Foote & Milstein 1991 — Kinetic maturation of an immune response
- **Authors:** Jefferson Foote, César Milstein
- **Year:** 1991 · **Journal:** Nature 352:530–532 · **DOI:** 10.1038/352530a0
- **Downloaded:** 2026-06-15 (Sci-Hub; OCR'd, scanned original)
- **Cited in context of:** Reading-list Tier 2 — foundational framing that affinity maturation tunes **rate constants**.
- **Key content verified (OCR'd quote):** "Is the affinity maturation of antibodies under thermodynamic or [kinetic control]"; notes an immunoglobulin "with an extremely high on-rate constant," with maturation later reflected in the off-rate.
- **File:** `Foote_Milstein_1991_kinetic_maturation_immune_response.txt`

---

## Li et al. 2003 — X-ray snapshots of the maturation of an antibody response to a protein antigen
- **Authors:** Yili Li, Hua Li, Fei Yang, Sandra J. Smith-Gill, Roy A. Mariuzza
- **Year:** 2003 · **Journal:** Nat Struct Biol 10(6):482–488 · **DOI:** 10.1038/nsb930
- **Downloaded:** 2026-06-15 (Sci-Hub) — ⚠️ first attempt with DOI 10.1038/nsb945 returned the wrong paper (a Granzyme A structure); corrected to nsb930.
- **Cited in context of:** Reading-list Tier 2 — HyHEL antibody series vs the *same* HEWL epitope across maturation stages; the conventional-Ab comparison De Genst 2004 contrasts cAb-Lys3 against.
- **Key content verified (direct quote):** "The few crystallographic studies of affinity maturation thus far have…"; maturation enhances binding via buried apolar surface + improved shape complementarity.
- **File:** `Li_2003_HyHEL_xray_snapshots_affinity_maturation.txt`

---

## Muyldermans 2013 — Nanobodies: natural single-domain antibodies
- **Authors:** Serge Muyldermans
- **Year:** 2013 · **Journal:** Annu Rev Biochem 82:775–797 · **DOI:** 10.1146/annurev-biochem-063011-092449
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Reading-list Tier 3 — canonical nanobody review (CDR usage, affinity ranges, framework, engineering).
- **Key content verified (direct quote):** title "Nanobodies: Natural [Single-Domain Antibodies]."
- **File:** `Muyldermans_2013_nanobodies_review_AnnuRevBiochem.txt`

---

## Zimmermann et al. 2018 — Synthetic single domain antibodies for the conformational trapping of membrane proteins (sybodies)
- **Authors:** Iwan Zimmermann, Pascal Egloff, Cedric A. J. Hutter, et al. (Markus Seeger lab)
- **Year:** 2018 · **Journal:** eLife 7:e34317 · **DOI:** 10.7554/eLife.34317
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Reading-list Tier 3 — in-vitro nanobody **selection/maturation platform** (ribosome→phage→yeast display); realistic DE workflow + affinity outcomes.
- **Key content verified (direct quote):** "an in vitro selection platform based on synthetic single domain antibodies named sybodies."
- **File:** `Zimmermann_2018_sybodies_synthetic_nanobody_platform.txt`

---

## McMahon et al. 2018 — Yeast surface display platform for rapid discovery of conformationally selective nanobodies
- **Authors:** Conor McMahon, Alexander S. Baier, Roberta Pascolutti, et al. (Andrew Kruse lab)
- **Year:** 2018 · **Journal:** Nat Struct Mol Biol 25(3):289–296 · **DOI:** 10.1038/s41594-018-0028-6
- **Downloaded:** 2026-06-15 (Sci-Hub)
- **Cited in context of:** Reading-list Tier 3 — yeast-display nanobody discovery + affinity ranking; comparison point for a selection readout.
- **Key content verified (direct quote):** "VHH domains (also called nanobodies) can be readily expressed in [yeast]."
- **File:** `McMahon_2018_yeast_display_nanobody_discovery.txt`

---

## Fernandez-Lopez et al. 2005 — Unsaturated fatty acids are inhibitors of bacterial conjugation
- **Authors:** Raul Fernandez-Lopez, Cristina Machón, … Manuel Espinosa, Erich Lanka, Fernando de la Cruz
- **Year:** 2005
- **Journal:** Microbiology (Reading) 151(Pt 11):3517–3526
- **DOI:** 10.1099/mic.0.28216-0 · **PMID:** 16272375
- **Downloaded:** 2026-06-11 (Sci-Hub)
- **Cited in context of:** Subsystem 2 (receptor/phage gate) — candidate **chemical disruptors of conjugation** (EXP2b). ⚠️ Proven for *conjugation*, NOT yet for M13 infectability.
- **Key content verified (direct quotes):** A high-throughput bioluminescence assay screened >12,000 microbial extracts using plasmid R388 in E. coli. "Two separate compounds were identified from these fractions: **linoleic acid** and **dehydrocrepenynic acid**." "the chemical class of **unsaturated fatty acids act as true inhibitors of conjugation**." Activity tested against R388, R1 and RP4 transfer systems. (Mechanism targets the conjugation/T4SS machinery, not literal pilus dissolution.)
- **File:** `FernandezLopez_2005_unsat_fatty_acids_conjugation_inhibitor.txt`

---

## Clarke et al. 2008 — F-pili dynamics by live-cell imaging
- **Authors:** Margaret Clarke, Lucinda Maddera, Robin L. Harris, Philip M. Silverman
- **Year:** 2008
- **Journal:** PNAS 105(46):17978–81
- **DOI:** 10.1073/pnas.0806786105 · **PMID:** 19004777 · **PMC:** PMC2582581
- **Retrieved:** 2026-06-11 (Europe PMC full text)
- **Cited in context of:** Subsystem 2 — establishes that F-pili **spontaneously cycle** extension/retraction, so "retracted" is the native off-state (basis of the repressible-*tra* gate design).
- **Key content verified (direct quotes):** "F-pili normally undergo cycles of **extension and retraction in the absence of any obvious triggering event**, such as contact with a recipient cell." Contacts "are able to survive the shear forces felt by bacteria in liquid media." "extension and retraction are accompanied by **rotation about the long axis** of the filament." Confirmed independently by Goldlust 2023 (same labeling approach).
- **File:** `Clarke_2008_Fpili_dynamics_live_cell.txt`

---

## Maier et al. 2004 — A force-dependent switch reverses type IV pilus retraction
- **Authors:** Berenike Maier, Michael Koomey, Michael P. Sheetz
- **Year:** 2004
- **Journal:** PNAS 101(30):10961–6
- **DOI:** 10.1073/pnas.0402305101 · **PMID:** 15256598 · **PMC:** PMC503726
- **Retrieved:** 2026-06-11 (Europe PMC full text)
- **Cited in context of:** Subsystem 2 — the **contrast** case. ⚠️ This is **type IV pilus / *Neisseria*, NOT the F-pilus**: cited only to show that type IV pili have a PilT retraction motor that F-pili lack.
- **Key content verified (direct quotes):** "In *Neisseria gonorrhoeae*, **pilus retraction is a highly irreversible process that depends on PilT**, an AAA ATPase family member." With reduced PilT, "the application of high external forces (F = 110 ± 10 pN) induces processive pilus elongation." "a **force-dependent molecular switch** can induce pilus elongation by reversing the retraction mechanism." PilT (51 mentions) — the motor F-pili do not encode.
- **File:** `Maier_2004_typeIV_pilus_retraction_force_switch.txt`

---

## Harb et al. 2020 — ssRNA phage penetration triggers detachment of the F-pilus
- **Authors:** Laith Harb, Karthik Chamakura, Pratick Khara, Peter J. Christie, Ry Young, Lanying Zeng
- **Year:** 2020
- **Journal:** PNAS 117(41):25751–25758
- **DOI:** 10.1073/pnas.2011901117 · **PMID:** 32989140 · **PMC:** PMC7568308
- **Retrieved:** 2026-06-11 (Europe PMC full text)
- **Cited in context of:** Subsystem 3 (infection gating) — phage engagement perturbs the receptor; relevant if decoy phages are pilus-specific.
- **Key content verified (direct quotes):** "ssRNA phage infection **triggers the release of F-pili** from host cells, and that higher multiplicity of infection (MOI) correlates with **detachment of longer F-pili**." gRNA entry "requires the F-plasmid–encoded coupling protein, **TraD**," but "TraD is not essential for pilus detachment." Proposed model: pilus retraction pulls the Mat–gRNA complex into the T4SS channel, "causing a torsional stress that **breaks the mature F-pilus** at the cell surface."
- **File:** `Harb_2020_ssRNA_phage_Fpilus_detachment.txt`

---

## Goldlust et al. 2023 — The F pilus serves as a conduit for the DNA during conjugation between physically distant bacteria
- **Authors:** Kelly Goldlust, Adrien Ducret, Manuel Halte, Annick Dedieu-Berne, Marc Erhardt, Christian Lesterlin
- **Year:** 2023
- **Journal:** PNAS 120(47):e2310842120
- **DOI:** 10.1073/pnas.2310842120 · **PMID:** 37963249 · **PMC:** PMC10666033
- **Retrieved:** 2026-06-11 (PubMed Central full text — no PDF, publisher render endpoint down)
- **Cited in context of:** Subsystem 2 — quantitative **F-pilus extension/retraction kinetics** (gate-criterion numbers) via maleimide live-cell labeling; also a **chemical-disruption lead (NaCN)**.
- **Key content verified (direct quotes):** "the pilus is a highly dynamic structure that undergoes **cycles of extension and retraction** … even in the absence of recipient cells." Measured **extension 49.5 ± 50 nm/s** and **retraction 47.5 ± 45 nm/s**; reversal "occurs at any pilus length … random rather than precisely regulated by an internal clock." Number of pili per cell 0–5; mean length 1.05 ± 0.92 µm; lumen "28 Å." Labeling: TraA "serine 54 was substituted by a cysteine for bioconjugation with Alexa Fluor-Maleimide." **NaCN lead:** cites Novotny & Fives-Taylor that "pili disassembly induced by **NaCN** hinders the adsorption of R17 bacteriophage to the sides of the pili but do not affect the adsorption of **M13 phage to the pili tips**."
- **File:** `Goldlust_2023_Fpilus_DNA_conduit.txt`

---

## Cabezón et al. 2014 — Towards an integrated model of bacterial conjugation
- **Authors:** Elena Cabezón, Jorge Ripoll-Rozada, Alejandro Peña, Fernando de la Cruz, Ignacio Arechaga
- **Year:** 2014
- **Journal:** FEMS Microbiol Rev 39(1):81–95
- **DOI:** 10.1111/1574-6976.12085 · **PMID:** 25154632
- **Downloaded:** 2026-06-11 (Sci-Hub)
- **Cited in context of:** Subsystems 2–4 — review framing for the **T4SS / conjugation machinery** and the rationale for targeting it with inhibitors.
- **Key content verified (direct quotes):** "DNA transfer is mediated by a membrane-associated macromolecular machinery called **Type IV secretion system (T4SS)**." "the search for specific **inhibitors** of different T4SS components opens a novel approach to **restrict plasmid dissemination**." Proposes "a model for **pilus biogenesis** and substrate transfer in conjugative systems" (T4SS: 69 mentions; pilus biogenesis: 19).
- **File:** `Cabezon_2014_integrated_model_conjugation.txt`


---

## Liu, Lu, Cai et al. 2024 — A broad neutralizing nanobody against SARS-CoV-2 engineered from an approved drug
- **Authors:** Qianyun Liu, Yuchi Lu, Chenguang Cai, … Hangtian Guo, Ke Lan, Yu Chen, Shin-Chen Hou, Yi Xiong (Wuhan Univ. / ShanghaiTech / Nanjing Univ. / Shenzhen Bay Lab)
- **Year:** 2024
- **Journal:** Cell Death & Disease 15:458
- **DOI:** 10.1038/s41419-024-06802-7 · **PMID:** 38937437 · **PMC:** PMC11211474
- **Retrieved:** 2026-08-17 (Europe PMC full-text XML + open-access PDF render; CC BY 4.0 — no Sci-Hub needed)
- **Cited in context of:** sourcing a sequence-defined **anti-SARS-CoV-2 RBD nanobody (VHH60)** as a model antigen–binder pair.
- **Key content verified (direct quotes / structural records):**
  - VHH60 was "directly produced from an engineering nanobody library based on a commercialized nanobody" — **caplacizumab** (anti-vWF VHH, EMA 2018 / FDA 2019) used as the humanised framework donor for a phage library screened against RBD.
  - Affinity: "an affinity of **2.56 nM**"; competes with human ACE2.
  - Epitope: binds RBD at "**S351, S470-471 and S493-494**" via CDR2 + CDR3; superposition onto the RBD–ACE2 model (PDB 7XO9) "shows there is a steric hindrance between VHH60 and ACE2."
  - Structures deposited: **PDB 8XK2** (RBD:VHH60 crystal, 3.40 Å) and **PDB 8XKI** (WT Spike:VHH60 cryo-EM, 3.79 Å, "1-up" conformation). Epitope compared to VHH-72 (PDB 6WAQ).
  - In vivo: "suppressed SARS-CoV-2 infection and propagation 50-fold better and protected mice from death for twice as long as the control group."
  - **Sequence note (from PDB 8XK2/8XKI chains, not the article body):** VHH60 = `EVQLVESGGGLVQPGGSLRLSCAASGRTFRVNLMGWFRQAPGKGRELVASINGFDDITYYPDSVEGRFTISRDNAKRMVYLQMNSLRAEDTAVYYCAAYDSDYDGRLFNYWGQGTQVTVSS` (121 aa). All four frameworks are **100% identical to caplacizumab** (PDB 7EOW chain B); only CDR1/2/3 differ — confirming the paper's CDR-grafting claim.
- **File:** `Liu_2024_VHH60_broad_neutralizing_nanobody_SARSCoV2.txt` (PDF: `../agent_papers/Liu_2024_VHH60_broad_neutralizing_nanobody_SARSCoV2.pdf`)

---

## Govaert, Pellis, Deschacht, Vincke, Conrath, Muyldermans & Saerens 2012 — Dual beneficial effect of interloop disulfide bond for single domain antibody fragments
- **Authors:** Jorn Govaert, Mireille Pellis, Nick Deschacht, Cécile Vincke, Katja Conrath, Serge Muyldermans, Dirk Saerens (VUB / VIB, Brussels)
- **Year:** 2012
- **Journal:** J Biol Chem 287(3):1970–1979
- **DOI:** 10.1074/jbc.M111.242818 · **PMID:** 22128183 · **PMC:** PMC3283254
- **Retrieved:** 2026-08-17 (PMC HTML full text; JBC PDF endpoint returns 403, Europe PMC XML empty)
- **Cited in context of:** whether cAb-Lys3's **non-canonical CDR1–CDR3 interloop disulfide** is a liability for *E. coli* expression / bacterial surface display.
- **Key content verified (direct quotes):**
  - Method: "The selected variants were recloned from pHEN4 or pBTL into pHEN6 and expressed as soluble proteins in the **periplasm of E. coli WK6**."
  - **The decisive result:** "**All variants of cAbAn33 and cAbLys3 were expressed at levels similar to the parental clones.** Surprisingly, the cAbPSA-N7 variants revealed at least a **20-fold increase in expression** compared with the original clone, pointing to possible difficulties of E. coli to express and fold the cAbPSA-N7 with an interloop disulfide bond." → the penalty is **clone-specific, and cAb-Lys3 is not affected**.
  - Cost of removing the bond from cAb-Lys3: Cys-Cys **Tm 69 °C, KD 16 nM** vs Ser-Pro **Tm 59 °C, KD 152 nM** (~10× affinity loss). The extra disulfide is **stabilising and affinity-enhancing**, not a burden.
  - Conclusion: "An interloop disulfide bond **stabilizes the domain and rigidifies the long third antigen-binding loop**, leading to stronger antigen interaction… This beneficial effect explains in vivo antibody maturation favoring antibodies with an interloop disulfide bond."
- **File:** `Govaert_2012_interloop_disulfide_sdAb_dual_benefit.txt` (no PDF — JBC paywalled, PMC HTML only)


---

# Diploid E. coli — recombination & large-fragment cloning (added 2026-08-22)

_Reading list: [reading_list_recombination_and_large_fragment_cloning.md](../projects/diploid_ecoli/knowledge/reading_list_recombination_and_large_fragment_cloning.md)_

---

## Shizuya, Birren, Kim, Mancino, Slepak, Tachiiri & Simon 1992 — Cloning and stable maintenance of 300-kb fragments of human DNA in E. coli using an F-factor-based vector
- **Authors:** Hiroaki Shizuya, Bruce Birren, Ung-Jin Kim, Valeria Mancino, Tatiana Slepak, Yoshiaki Tachiiri, Melvin Simon
- **Year:** 1992
- **Journal:** PNAS 89(18):8794–8797
- **DOI:** 10.1073/pnas.89.18.8794 · **PMC:** PMC50007
- **Retrieved:** 2026-08-22 (PMC scanned PDF, OCR via pdftotext)
- **Cited in context of:** How BACs work — the F-factor basis of the diploid E. coli payload replicon
- **Key content verified:**
  - "The oriS and repE genes mediate the unidirectional replication of the F factor while parA and parB maintain copy number at a level of one or two per E. coli genome."
  - "Individual clones of human DNA appear to be maintained with a high degree of structural stability in the host, even after 100 generations of serial growth."
  - Structural stability of large inserts is a consequence of single-copy maintenance, not a separate engineered property.
- **Zotero:** [`6ZFA4TFC`](zotero://select/library/items/6ZFA4TFC) · [📄 local PDF](../agent_papers/Shizuya_1992_BAC_F_factor_300kb.pdf)
- **File:** `Shizuya_1992_BAC_F_factor_300kb.txt`

---

## Kline 1985 — A review of mini-F plasmid maintenance
- **Authors:** Bruce C. Kline (Mayo Clinic)
- **Year:** 1985
- **Journal:** Plasmid 14:1–16
- **DOI:** 10.1016/0147-619X(85)90027-7
- **Retrieved:** 2026-08-22 (Sci-Hub PDF, OCR via pdftotext; loss-rate exponent illegible in scan)
- **Cited in context of:** How the F plasmid is replicated and its copy number controlled
- **Key content verified:**
  - "The number of plasmids per cell approximates the number of chromosomes per cell (Frame and Bishop, 1971) and F is rarely lost at cell division"
  - Replication control is by iteron arrays (oriS/incB, copB/incC) titrating the RepE initiator protein — hence iteron-mediated incompatibility between F-derived replicons.
- **Zotero:** [`GAF393CQ`](zotero://select/library/items/GAF393CQ) · [📄 local PDF](../agent_papers/Kline_1985_mini_F_plasmid_maintenance_review.pdf)
- **File:** `Kline_1985_mini_F_plasmid_maintenance_review.txt`

---

## Bouet & Funnell 2019 — Plasmid Localization and Partition in Enterobacteriaceae
- **Authors:** Jean-Yves Bouet, Barbara E. Funnell
- **Year:** 2019
- **Journal:** EcoSal Plus 8(2)
- **DOI:** 10.1128/ecosalplus.ESP-0003-2019 · **PMC:** PMC11573283
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** How the F plasmid is segregated at 1–2 copies per cell
- **Key content verified:**
  - "Almost all partition systems identified to date consist of three components, one or more copies of a partition site (the ‘centromere’), a centromere-binding protein (CBP), and an NTPase (ATPase or GTPase)."
  - "For low-copy-number plasmids, however, an active partition process is critical to prevent plasmid loss at cell division."
  - "The F plasmid centromere, parSF, is composed of 12 direct repeats of 43 bp, 10 of which contain the 16-bp inverted repeat to which its CBP (ParBF) binds."
  - ParA/ParB stoichiometry is dosage-sensitive: over- or under-expression destabilises the plasmid (IncI/IncG incompatibility).
- **Zotero:** [`2T5EK655`](zotero://select/library/items/2T5EK655) · [📄 local PDF](../agent_papers/BouetFunnell_2019_plasmid_partition_enterobacteriaceae.pdf)
- **File:** `BouetFunnell_2019_plasmid_partition_enterobacteriaceae.txt`

---

## Low 1972 — Escherichia coli K-12 F-prime factors, old and new
- **Authors:** K. Brooks Low (Yale)
- **Year:** 1972
- **Journal:** Bacteriological Reviews 36(4):587–607
- **DOI:** 10.1128/br.36.4.587-607.1972 · **PMC:** PMC408333
- **Retrieved:** 2026-08-22 (PMC scanned PDF, OCR via pdftotext (two-column interleave — quotes de-columned before extraction))
- **Cited in context of:** Historical precedent: has anyone carried ~100 kb of the E. coli chromosome on an F replicon before?
- **Key content verified:**
  - "F-prime transfer to a recA− strain results with high efficiency in formation of stable merodiploids."
  - "the use of recA− recipients is preferable to recover potentially unstable (e.g., very long) F-primes"
  - F′ merodiploids are the direct ancestor of the diploid E. coli design; the classical field found long F′s unstable in rec+ hosts and routinely moved to recA− recipients.
- **Zotero:** [`CUBKD7CK`](zotero://select/library/items/CUBKD7CK) · [📄 local PDF](../agent_papers/Low_1972_Fprime_factors_old_and_new.pdf)
- **File:** `Low_1972_Fprime_factors_old_and_new.txt`

---

## Shen & Huang 1986 — Homologous recombination in Escherichia coli: dependence on substrate length and homology
- **Authors:** Peng Shen, Hillard V. Huang
- **Year:** 1986
- **Journal:** Genetics 112(3):441–457
- **DOI:** 10.1093/genetics/112.3.441 · **PMC:** PMC1202756
- **Retrieved:** 2026-08-22 (PMC scanned PDF, OCR via pdftotext)
- **Cited in context of:** Is there a size dependency to plasmid–chromosome homologous recombination?
- **Key content verified:**
  - "Recombination is linearly dependent on the length of the homologous sequences. In both RecBC and RecF-dependent pathways there is a minimal length, called the minimal efficient processing segment (MEPS), below which recombination becomes inefficient. The length of MEPS is between 23-27 base pairs (bp) and between 44-90 bp for the RecBC- and RecF-dependent pathways, respectively."
  - "The recombinant frequencies measured using the wild-type strain AB1157 are linearly dependent on substrate length in the range 27-405 bp… a slope of 3.5 × 10⁻⁴/bp"
  - "In wild-type E. coli, reduction of homology from 100% to 90% decreases recombinant frequency over 40-fold."
  - Assay design worth copying: cointegrate formation by a single reciprocal exchange, scored as selectable phage infective centres.
- **Zotero:** [`XA7S6IPV`](zotero://select/library/items/XA7S6IPV) · [📄 local PDF](../agent_papers/ShenHuang_1986_HR_length_homology_dependence.pdf)
- **File:** `ShenHuang_1986_HR_length_homology_dependence.txt`

---

## Watt, Ingles, Urdea & Rutter 1985 — Homology requirements for recombination in Escherichia coli
- **Authors:** Valerie M. Watt, C. James Ingles, Mickey S. Urdea, William J. Rutter
- **Year:** 1985
- **Journal:** PNAS 82(14):4768–4772
- **DOI:** 10.1073/pnas.82.14.4768 · **PMC:** PMC390986
- **Retrieved:** 2026-08-22 (PMC scanned PDF, OCR via pdftotext)
- **Cited in context of:** Independent confirmation of the homology-length dependence of recombination
- **Key content verified:**
  - "A minimum of ≈20 base pairs in a completely homologous segment is required for significant recombination. There is an exponential increase in the frequency of recombination when the length of homologous DNA is increased from 20 base pairs to 74 base pairs and an apparently linear increase with longer DNA segments."
  - "Mismatches within a homologous segment can dramatically decrease the frequency of recombination."
- **Zotero:** [`6HWMGB45`](zotero://select/library/items/6HWMGB45) · [📄 local PDF](../agent_papers/Watt_1985_homology_requirements_recombination.pdf)
- **File:** `Watt_1985_homology_requirements_recombination.txt`

---

## Yu, Ellis, Lee, Jenkins, Copeland & Court 2000 — An efficient recombination system for chromosome engineering in Escherichia coli
- **Authors:** Daiguan Yu, Hilary M. Ellis, E-Chiang Lee, Nancy A. Jenkins, Neal G. Copeland, Donald L. Court
- **Year:** 2000
- **Journal:** PNAS 97(11):5978–5983
- **DOI:** 10.1073/pnas.100127597 · **PMC:** PMC18544
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** Homology-length dependence in the λ Red (recombineering) pathway, for contrast with RecA
- **Key content verified:**
  - "No recombinants were found with 10 bp of homology, and less than ten recombinants were found in each of three experiments with 20 bp of homology. From 20 bp to 40 bp of homology, homologous recombination increased by four orders of magnitude."
  - "Maximal recombination levels are achieved with induction times from 7.5–17.5 min at 42°C, and a homology segment of 40–50 bp."
  - Red saturates at ~40–50 bp; RecA keeps scaling with length. Choose the pathway to match whether you want a switch or a dial.
- **Zotero:** [`PASHG9FF`](zotero://select/library/items/PASHG9FF) · [📄 local PDF](../agent_papers/Yu_2000_lambda_Red_recombineering_chromosome.pdf)
- **File:** `Yu_2000_lambda_Red_recombineering_chromosome.txt`

---

## Vulić, Dionisio, Taddei & Radman 1997 — Molecular keys to speciation: DNA polymorphism and the control of genetic exchange in enterobacteria
- **Authors:** Marin Vulić, Francisco Dionisio, François Taddei, Miroslav Radman
- **Year:** 1997
- **Journal:** PNAS 94(18):9763–9767
- **DOI:** 10.1073/pnas.94.18.9763 · **PMC:** PMC23264
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** What decreases (and what increases) the plasmid↔chromosome recombination rate
- **Key content verified:**
  - "The results of crosses with either the same donor or the same recipient show that recombination frequency decreases exponentially with increasing sequence divergence"
  - "Inactivation of the MMR system (mutS) increases the level of recombination proportionally to the extent of sequence divergence—i.e., decreases the slope of the graph without changing the intercept—whereas overproduction of mismatch-binding proteins (pmutSL) increases the slope."
  - "inactivation of MMR and overproduction of RecA (mutS recAo98) relaxes the genetic barrier in the range of divergence examined in these experiments, allowing efficient recombination between bacteria as diverged as E. coli and S. typhimurium."
  - Consequence for the diploid platform: mutation supply and write efficiency are coupled and fight each other; MMR is the divergence sensor that closes the write channel.
- **Zotero:** [`52KR6DSK`](zotero://select/library/items/52KR6DSK) · [📄 local PDF](../agent_papers/Vulic_1997_divergence_MMR_recombination_barrier.pdf)
- **File:** `Vulic_1997_divergence_MMR_recombination_barrier.txt`

---

## Murphy 1998 — Use of bacteriophage λ recombination functions to promote gene replacement in Escherichia coli
- **Authors:** Kenan C. Murphy
- **Year:** 1998
- **Journal:** J. Bacteriol. 180(8):2063–2071
- **DOI:** 10.1128/JB.180.8.2063-2071.1998 · **PMC:** PMC107131
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** Has anyone engineered an E. coli strain with enhanced recombination?
- **Key content verified:**
  - "The levels of λ Red-promoted recombination varied between 15- and 130-fold greater than that seen with the recBC sbcBC strain, depending on the amount of DNA electroporated, the extent of flanking homology, and how the λ Red functions were supplied."
  - "I found that chromosomally encoded λ Red promoted recombination 63-fold higher than in a recBC sbcBC strain"
  - Strain KM22 (ΔrecBCD::Plac-red) is the archetype hyper-recombinogenic E. coli and the ancestor of DY330/HME63/SW102/EcNR1.
- **Zotero:** [`XWK578GQ`](zotero://select/library/items/XWK578GQ) · [📄 local PDF](../agent_papers/Murphy_1998_lambda_Red_gene_replacement.pdf)
- **File:** `Murphy_1998_lambda_Red_gene_replacement.txt`

---

## Datsenko & Wanner 2000 — One-step inactivation of chromosomal genes in Escherichia coli K-12 using PCR products
- **Authors:** Kirill A. Datsenko, Barry L. Wanner
- **Year:** 2000
- **Journal:** PNAS 97(12):6640–6645
- **DOI:** 10.1073/pnas.120163297 · **PMC:** PMC18686
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** Background on λ Red recombineering as the standard enhanced-recombination method
- **Key content verified:**
  - "a selectable antibiotic resistance gene that is generated by PCR by using primers with 36-nt homology extensions (H1 and H2)"
  - "Because of the limited homology that is required for gene disruption when using the Red system, a new PCR fragment can recombine at the new targeted gene or at the scar of an earlier gene disruption."
- **Zotero:** [`CGI6WRA7`](zotero://select/library/items/CGI6WRA7) · [📄 local PDF](../agent_papers/Datsenko_Wanner_2000_lambda_Red_onestep.pdf)
- **File:** `Datsenko_Wanner_2000_lambda_Red_onestep.txt`

---

## Wang, Isaacs, Carr, Sun, Xu, Forest & Church 2009 — Programming cells by multiplex genome engineering and accelerated evolution (MAGE)
- **Authors:** Harris H. Wang, Farren J. Isaacs, Peter A. Carr, Zachary Z. Sun, George Xu, Craig R. Forest, George M. Church
- **Year:** 2009
- **Journal:** Nature 460:894–898
- **DOI:** 10.1038/nature08187 · **PMC:** PMC4590770
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** Combining enhanced recombination with a mutator; the closest existing competitor to the diploid platform
- **Key content verified:**
  - "Replacement of mutS with the chloramphenicol resistance gene (cmR cassette) in EcNR1 produced EcNR2 (mutS−, λ-Red+)."
  - "Twenty-four genetic components in the DXP pathway were modified simultaneously using a complex pool of synthetic DNA, creating over 4.3 billion combinatorial genomic variants per day."
  - "Owing to high voltage (18 kV cm−1) electroporation, ~95% of cells are killed at each cycle." — MAGE’s diversity is externally metered and costly per cycle; the diploid platform proposes an internal, continuous alternative.
- **Zotero:** [`PXHCB8T6`](zotero://select/library/items/PXHCB8T6) · [📄 local PDF](../agent_papers/Wang_2009_MAGE_multiplex_genome_engineering.pdf)
- **File:** `Wang_2009_MAGE_multiplex_genome_engineering.txt`

---

## Jiang, Bikard, Cox, Zhang & Marraffini 2013 — RNA-guided editing of bacterial genomes using CRISPR-Cas systems
- **Authors:** Wenyan Jiang, David Bikard, David Cox, Feng Zhang, Luciano A. Marraffini
- **Year:** 2013
- **Journal:** Nat. Biotechnol. 31:233–239
- **DOI:** 10.1038/nbt.2508 · **PMC:** PMC3748948
- **Retrieved:** 2026-08-22 (Europe PMC full-text XML (open access))
- **Cited in context of:** Does CRISPR with homologous repair work in E. coli?
- **Key content verified:**
  - "This background is higher than the recombineering efficiency of the rpsL mutation, 5.3×10⁻⁵, which suggested that in order to obtain 65 % CRISPR-assisted editing, Cas9 cleavage should induce oligonucleotide recombination."
  - "Alone or together with recombineering, CRISPR assisted editing induces recombination at the targeted locus and kills non-edited cells leading to a recovery of close to a 100% of edited cells."
  - E. coli has no NHEJ, so a Cas9 cut is lethal unless repaired by HR — CRISPR acts as counter-selection *and* as a recombination trigger. Directly relevant to write-channel gating (D3).
- **Zotero:** [`7KFCBA97`](zotero://select/library/items/7KFCBA97) · [📄 local PDF](../agent_papers/Jiang_2013_CRISPR_Cas9_bacterial_genome_editing.pdf)
- **File:** `Jiang_2013_CRISPR_Cas9_bacterial_genome_editing.txt`

---

## Pyne, Moo-Young, Chung & Chou 2015 — Coupling the CRISPR/Cas9 system with λ Red recombineering enables simplified chromosomal gene replacement in Escherichia coli
- **Authors:** Michael E. Pyne, Murray Moo-Young, Duane A. Chung, C. Perry Chou
- **Year:** 2015
- **Journal:** Appl. Environ. Microbiol. 81(15):5103–5114
- **DOI:** 10.1128/AEM.01248-15 · **PMC:** PMC4495200
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** Size limits of CRISPR-assisted homologous recombination in E. coli
- **Key content verified:**
  - "Generally, recombination efficiency decreased with increasing size of chromosomal deletion, yet not in a linear manner across the sizes of deletion assessed."
  - "Deletion of a 19,378-bp region, comprising a total of 19 chromosomal genes, yielded the lowest recombination efficiency, 3%."
  - "A major drop in recombination efficiency (>80%) was observed by increasing the size of deletion from 818 bp to 2,428 bp." — the size penalty is a step function, then a plateau (8–11% from 2.4–11 kb).
  - Without CRISPR selection the same events ran at 0–0.68%: CRISPR buys ~1.5–2 orders of magnitude.
- **Zotero:** [`F929VXEI`](zotero://select/library/items/F929VXEI) · [📄 local PDF](../agent_papers/Pyne_2015_CRISPR_Cas9_lambda_Red_Ecoli.pdf)
- **File:** `Pyne_2015_CRISPR_Cas9_lambda_Red_Ecoli.txt`

---

## Durfee, Nelson, Baldwin, Plunkett, Burland, Mau, Petrosino, Qin, Muzny, Ayele, Gibbs, Csörgő, Pósfai, Weinstock & Blattner 2008 — The complete genome sequence of Escherichia coli DH10B
- **Authors:** Tim Durfee, Richard Nelson, Schuyler Baldwin, Guy Plunkett III, Valerie Burland, Bob Mau, Joseph F. Petrosino, Xiang Qin, Donna M. Muzny, Mulu Ayele, Richard A. Gibbs, Bálint Csörgő, György Pósfai, George M. Weinstock, Frederick R. Blattner
- **Year:** 2008
- **Journal:** J. Bacteriol. 190(7):2597–2606
- **DOI:** 10.1128/JB.01695-07 · **PMC:** PMC2293198
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** How cloning strains were made, and what that did to recombination and clone stability
- **Key content verified:**
  - "Among the engineered gene replacements were recA1 to improve clone stability by inhibiting the homologous recombination system; endA1, which inactivates the encoded periplasmic DNA-specific endonuclease, thereby enhancing DNA stability during transformation"
  - "we demonstrate that DH10B has a 13.5-fold higher mutation rate than MG1655, resulting from a dramatic increase in insertion sequence (IS) transposition, especially IS150. IS elements appear to have remodeled genome architecture, providing homologous recombination sites for a 113,260-bp tandem duplication and an inversion."
  - "analysis of sequenced bacterial artificial chromosome (BAC) clones derived from DH10B shows a high incidence of insertion sequence (IS) transposition from the chromosome into the cloned fragment"
  - Warning for the diploid design: recA1 does not prevent IS-mediated rearrangement, and DH10B actively seeds IS elements into BAC inserts. Consider an IS-free chassis.
- **Zotero:** [`XN7PHHC6`](zotero://select/library/items/XN7PHHC6) · [📄 local PDF](../agent_papers/Durfee_2008_DH10B_genome_cloning_strain.pdf)
- **File:** `Durfee_2008_DH10B_genome_cloning_strain.txt`

---

## Lee, Yu, Martinez de Velasco, Tessarollo, Swing, Court, Jenkins & Copeland 2001 — A highly efficient E. coli-based chromosome engineering system adapted for recombinogenic targeting and subcloning of BAC DNA
- **Authors:** E-Chiang Lee, Daiguan Yu, J. Martinez de Velasco, Lino Tessarollo, Deborah A. Swing, Donald L. Court, Nancy A. Jenkins, Neal G. Copeland
- **Year:** 2001
- **Journal:** Genomics 73(1):56–65
- **DOI:** 10.1006/geno.2000.6451
- **Retrieved:** 2026-08-22 (Sci-Hub PDF, pdftotext)
- **Cited in context of:** In vivo retrieval of large genomic fragments onto a plasmid (gap repair) — the chromosome→plasmid write direction
- **Key content verified:**
  - "Importantly, the recombination is proficient with DNA homologies as short as 30–50 bp, making it possible to use PCR-amplified fragments as the targeting cassette."
  - "we show that fragments as large as 80 kb can be subcloned from BACs by gap repair using this recombination system"
  - No in vitro handling of long DNA, hence no shear ceiling — but the target must already be resident in the cell.
- **Zotero:** [`WRRJ4ANW`](zotero://select/library/items/WRRJ4ANW) · [📄 local PDF](../agent_papers/Lee_2001_recombinogenic_targeting_subcloning_BAC_DNA.pdf)
- **File:** `Lee_2001_recombinogenic_targeting_subcloning_BAC_DNA.txt`

---

## Seed, Parker & Davidson 1982 — Representation of DNA sequences in recombinant DNA libraries prepared by restriction enzyme partial digestion
- **Authors:** Brian Seed, Richard C. Parker, Norman Davidson
- **Year:** 1982
- **Journal:** Gene 19:201–209
- **DOI:** 10.1016/0378-1119(82)90007-5
- **Retrieved:** 2026-08-22 (Sci-Hub PDF, pdftotext (OCR))
- **Cited in context of:** Tuning restriction-enzyme partial digestion to hit a target insert size — the theory
- **Key content verified:**
  - "If all restriction sites in the target DNA can be cleaved with the same rate, optimum incorporation of sequences is observed when the number average length of the digested DNA equals the desired average length of the cloned insert."
  - "Overdigestion severely reduces the fraction of sequences present in a sample of clones. Heterogeneity in restriction enzyme cleavage rates also reduces the fraction incorporated, and underdigestion improves sequence representation in the face of cleavage rate heterogeneity."
  - Important correction to the intuitive model: a partial digest does not produce a distribution *centred* on the target size. What you tune is the number-average length; the centring comes from subsequent size selection.
- **Zotero:** [`4GH2FSUI`](zotero://select/library/items/4GH2FSUI) · [📄 local PDF](../agent_papers/Seed_1982_partial_digestion_library_representation.pdf)
- **File:** `Seed_1982_partial_digestion_library_representation.txt`

---

## Osoegawa, Woon, Zhao, Frengen, Tateno, Catanese & de Jong 1998 — An improved approach for construction of bacterial artificial chromosome libraries
- **Authors:** Kazutoyo Osoegawa, Peng Yeong Woon, Baohui Zhao, Eirik Frengen, Minako Tateno, Joseph J. Catanese, Pieter J. de Jong
- **Year:** 1998
- **Journal:** Genomics 52(1):1–8
- **DOI:** 10.1006/geno.1998.5423
- **Retrieved:** 2026-08-22 (Sci-Hub PDF, pdftotext)
- **Cited in context of:** Tuning partial digestion to hit a target insert size — the practice, at BAC scale
- **Key content verified:**
  - "partial digestion was performed with MboI … for the PAC library construction or EcoRI restriction enzyme/EcoRI methylase … for the BAC library construction"
  - "inserts with a larger average size (160–230 kb) and a uniform size distribution can now be expected."
  - Two transferable tricks: (i) run the nuclease *against* its cognate methylase so site availability is titrated rather than reaction time; (ii) double size selection within a single PFGE gel to strip small fragments that would otherwise dominate the ligation.
- **Zotero:** [`P6EFHVR5`](zotero://select/library/items/P6EFHVR5) · [📄 local PDF](../agent_papers/Osoegawa_1998_improved_BAC_library_construction.pdf)
- **File:** `Osoegawa_1998_improved_BAC_library_construction.txt`

---

## Foster 2006 — Methods for determining spontaneous mutation rates
- **Authors:** Patricia L. Foster
- **Year:** 2006
- **Journal:** Methods in Enzymology 409:195–213
- **DOI:** 10.1016/S0076-6879(05)09012-9 · **PMC:** PMC2041832
- **Retrieved:** 2026-08-22 (PMC HTML full text)
- **Cited in context of:** Converting a measured recombinant frequency into a per-cell-per-generation rate (D2 methodology)
- **Key content verified:**
  - "Among replicate cultures, the distribution of the numbers of mutations that were sustained is Poisson, but the distribution of the numbers of mutants that result is far from Poisson, and is usually referred to as the Luria-Delbrück distribution."
  - "There are two basic methods to determine mutation rates: mutant accumulation and fluctuation analysis."
  - "Since the final number of cells in a culture, Nt, arose from Nt-1 divisions, the mutation rate is: u = m/(Nt-1) ≈ m/Nt"
  - Applies to recombination exactly as to mutation: a single plate gives a jackpot-dominated frequency, not a rate. Use parallel cultures + MSS maximum likelihood (rSalvador/FALCOR).
- **Zotero:** [`KJRP6RX3`](zotero://select/library/items/KJRP6RX3) · [📄 local PDF](../agent_papers/Foster_2006_methods_determining_spontaneous_mutation_rates.pdf)
- **File:** `Foster_2006_methods_determining_spontaneous_mutation_rates.txt`

---

## Park & Kim 2021 — Gene-specific mutagenesis enables rapid continuous evolution of enzymes in vivo (eMutaT7)
- **Authors:** Hyun Park, Seokhee Kim (Seoul National University)
- **Year:** 2021 · **Journal:** Nucleic Acids Research 49(6):e32
- **DOI:** 10.1093/nar/gkaa1231 · **PMID:** 33406230 · **PMC:** PMC8034631
- **Retrieved:** 2026-08-27 (Europe PMC full-text XML)
- **Cited in context of:** MutaT7 follow-ups — first big rate improvement over Moore 2018.
- **Key content verified:**
  - eMutaT7 = **PmCDA1** (sea-lamprey cytidine deaminase) fused to T7 RNAP, expressed from P_BAD; replaces rApo1.
  - "up to ~4 mutations per 1 kb per day"; "3.4 × 10⁻⁵ mutations base⁻¹ generation⁻¹".
  - "This mutation rate is 7–11-fold higher than that of MutaT7"; direct head-to-head with MutaT7 under matched promoter/strain confirms the gain is not a growth-condition artifact.
  - Rate is **tunable by arabinose** concentration.
  - Off-target: rifampicin-resistance frequency with vs without mutator is similar → genome-wide off-target mutagenesis stays low.
  - Still C:G→T:A dominant (same spectrum limitation as MutaT7).
- **File:** `Park_Kim_2021_eMutaT7_gene_specific_mutagenesis.txt`

---

## Álvarez, Mencía, de Lorenzo & Fernández 2020 — In vivo diversification of target genomic sites using processive base deaminase fusions blocked by dCas9 (T7-DIVA)
- **Authors:** Beatriz Álvarez, Mario Mencía, Víctor de Lorenzo, Luis Ángel Fernández (CNB-CSIC, Madrid)
- **Year:** 2020 · **Journal:** Nature Communications 11:6436
- **DOI:** 10.1038/s41467-020-20230-z · **PMID:** 33353963 · **PMC:** PMC7755918
- **Retrieved:** 2026-08-27 (Europe PMC full-text XML)
- **Cited in context of:** MutaT7 follow-ups — boundary control without terminators; chromosomal targets.
- **Key content verified:**
  - Fusions of several base deaminases (incl. AID) to T7RNAP; "transitions C to T or A to G on both DNA strands and in long DNA segments".
  - **dCas9 + custom crRNA used as a physical "roadblock"** to stop T7RNAP elongation and delimit the mutagenized window — an alternative to Moore's 4× T7 terminator array.
  - Works on a **chromosomal** cassette (sacB-gfp-URA3, later sacB-gfp-TEM-1 replacing *flu* in MG1655), not just episomes; host is Δung Δnfi.
  - Strand asymmetry confirmed: higher C mutation rate on the non-template strand for the CD-T7RNAP fusions.
  - Demonstrated by evolving **TEM-1** β-lactamase to ceftazidime resistance.
- **File:** `Alvarez_2020_T7DIVA_dCas9_bounded_deaminase_T7RNAP.txt`

---

## Mengiste et al. 2023 — Expanded MutaT7 toolkit efficiently and simultaneously accesses all possible transition mutations in bacteria
- **Authors:** Aza A. Mengiste, Robert H. Wilson, Rachel F. Weissman, Louis J. Papa III, Samuel J. Hendel, Christopher L. Moore, Vincent L. Butty, Matthew D. Shoulders (MIT)
- **Year:** 2023 · **Journal:** Nucleic Acids Research 51(6):e31
- **DOI:** 10.1093/nar/gkad003 · **PMID:** 36715334 · **PMC:** PMC10085711
- **Retrieved:** 2026-08-27 (Europe PMC full-text XML)
- **Cited in context of:** MutaT7 follow-ups — the Shoulders lab's own sequel to Moore 2018.
- **Key content verified:**
  - New chimeras: **MutaT7^A→G** (TadA7.10–T7RNAP) and **eMutaT7^A→G** (**TadA8e**–T7RNAP via XTEN linker); both deaminate dA→dI, read as G.
  - "adenosine deaminase-bearing mutators (MutaT7^A→G or eMutaT7^A→G) can be employed in tandem with a cytidine deaminase-bearing mutator (MutaT7^C→T) to introduce all possible transition mutations simultaneously" — dual strains Dual7 / Dual8.
  - Covers all four transition classes → ~80 amino-acid-level transformations accessible.
  - Mutators genomically integrated by two-step λ-Red recombineering.
- **File:** `Mengiste_2023_expanded_MutaT7_toolkit_all_transitions.txt`

---

## Seo, Koh, Eom, Kim & Kim 2023 — A dual gene-specific mutator system installs all transition mutations at similar frequencies in vivo (eMutaT7^transition)
- **Authors:** Dongwon Seo, Beomhee Koh, Ga Eul Eom, Hyun Woo Kim, Seokhee Kim (SNU)
- **Year:** 2023 · **Journal:** Nucleic Acids Research 51(11):e59
- **DOI:** 10.1093/nar/gkad266 · **PMID:** 37070179 · **PMC:** PMC10250238
- **Retrieved:** 2026-08-27 (Europe PMC full-text XML)
- **Cited in context of:** MutaT7 follow-ups — parallel solution to the same spectrum problem, from the eMutaT7 lab.
- **Key content verified:**
  - Two separate mutator proteins: **PmCDA1–T7RNAP** and **TadA-8e–T7RNAP**, co-expressed.
  - "installs all transition mutations (C:G→T:A and A:T→G:C) at comparable frequencies"; "~6.7 substitutions in 1.3 kb gene during 80-h in vivo mutagenesis" (preprint quoted 3.4 × 10⁻⁵ mutations base⁻¹ generation⁻¹, ~1.3 mutations kb⁻¹ day⁻¹).
  - Validated by TEM-1 evolution; recovered mutations "found in clinical isolates".
  - **Transversions remain inaccessible** — acknowledged limitation of all deaminase-based mutators.
- **File:** `Seo_2023_eMutaT7transition_dual_mutator.txt`

---

## Shao, Zhang, Jin, Ding & Chen 2025 — An orthogonal transcription mutation system generating all transition mutations for accelerated protein evolution in vivo
- **Authors:** Mengyao Shao, Zhongnan Zhang, Xinru Jin, Jiaxuan Ding, Guo-Qiang Chen (Tsinghua)
- **Year:** 2025 · **Journal:** Nature Communications 16:6041
- **DOI:** 10.1038/s41467-025-61354-4 · **PMID:** 40593783 · **PMC:** PMC12218169
- **Retrieved:** 2026-08-27 (Europe PMC full-text XML)
- **Cited in context of:** MutaT7 follow-ups — host-range and orthogonality expansion.
- **Key content verified:**
  - Orthogonal transcription mutators (OTM) built on **three phage RNAPs: MmP1, K1F, VP4** (not T7), each with its own cognate promoter → mutually orthogonal, multiplexable.
  - Deaminases: PmCDA1–UGI (C:G→T:A) and adenosine deaminase (A:T→G:C).
  - ">1,500,000-fold increased mutation rates"; works in **Halomonas bluephagenesis** (non-model, T7 system works poorly there) as well as E. coli.
  - Applied to fluorescent proteins, chromoproteins, cytoskeletal/division proteins, sigma factor, LysE exporter — "within a single day".
- **File:** `Shao_2025_orthogonal_transcription_mutation_system.txt`

---


---

# Note_012 open-question sweep (2026-08-27)

Seven parallel literature agents, one per question cluster of
[Note_012 — MutaT7 × Diploid E. coli](../projects/diploid_ecoli/knowledge/mutaT7_episomal_tile_concept.md).
Every paper below was downloaded, text-extracted and read; quotes are verbatim from those extracts.
Per-cluster answers with full reasoning live in
[`projects/diploid_ecoli/knowledge/note012_answers/`](../projects/diploid_ecoli/knowledge/note012_answers/).

## λ-Red recombineering at large insert size — the genome-write step

_How big a linear fragment λ-Red can move, how efficiency scales with length and homology, in-vivo liberation vs electroporation, and RecBCD/Gam._
_Added 2026-08-27 for [Note_012 open questions](../projects/diploid_ecoli/knowledge/note012_answers/). Findings: [`A1_lambda_red_findings.md`](../projects/diploid_ecoli/knowledge/note012_answers/A1_lambda_red_findings.md)._

---

# Staging catalog — A1_lambda_red (retrieved 2026-08-27)

All texts in `agent_papers_txt/`, PDFs (where a PDF was fetched) in `agent_papers/`.
Route key: EPMC-XML = Europe PMC `fullTextXML`; EPMC-PDF = `europepmc.org/articles/<PMCID>?pdf=render`;
SH = Sci-Hub via `scripts/fetch_papers.py`; DIRECT = publisher/repository direct download.

---

## Murphy KC 2016 — λ Recombination and Recombineering
- **Note (2026-08-27):** this file was previously mis-filed under "Court & Thomason 2016". Verified against
  the article header and Crossref: sole author **Kenan C. Murphy**; James M. Slauch is the EcoSal editor.
  DOI 10.1128/ecosalplus.ESP-0011-2015 · PMID 27223821 · PMC11575712. Claims previously attributed to
  "Court & Thomason 2016" in the Note_012 answer set belong to this chapter.
Authors: Court DL, Thomason LC (EcoSal Plus review; authors listed in file header)
Journal: EcoSal Plus (ASM) | DOI: 10.1128/ecosalplus.ESP-0011-2015 | PMC11575712
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: authoritative size limits, λ Exo processivity, RecA-dependent vs -independent regimes, Gam/RecBCD, in vivo cloning with I-SceI.
Key verified quotes:
- "Recombineering frequencies dropped dramatically when the insert size increased from 1 kb to 4.5 kb. The same effect was seen by Maresca et al. (273)."
- "RecA-independent recombineering decreases with increasing size of the linear DNA (273), probably a reflection of the limited ability of λ Exo to make a complete ssDNA intermediate for dsDNA substrates 3 kb and greater in vivo."
- "Maresca et al. (273) also showed that recombineering decreases dramatically when dsDNA insertions are increased from 1 to 4.5 kb, consistent with the limited processivity reported for λ Exo of ∼3 kb (43)." [ref 43 = Carter & Radding 1971 JBC 246:2502]
- "Using recombineering, insertions of drugR markers of 1 to 2 kb in size have routinely been performed using λ Red and RecET. However, it has generally been observed (although often not reported) that larger sizes of DNA are less efficiently incorporated, if at all."
- "Large insertions using recombineering is most efficiently done by exploiting an in vivo cloning type of strategy … where both the insert and the target are linearized by digestion with the meganuclease I-SceI restriction enzyme."
- "Another in vivo cloning method takes advantage of Red/RecET promoted repair of dsDNA breaks to integrate long DNA fragments (5 to 50 kb) into BACs."
- "Substrates containing longer regions of flanking homologies (e.g., 0.5 to 1 kb), which show a large RecA dependency, have not been tested using this type of methodology."
- "These substrates, however, contained 1 kb of flanking homology and the recombination observed was largely dependent on RecA."
- "λ Gam (11.6 kDa, 98 amino acids) has been shown to inhibit all the known activities of the RecBCD enzyme … It does this by binding to RecBCD and preventing the enzyme from binding to dsDNA ends."
- "It has been proposed that there are low levels of RecBCD activity in cells expressing Gam from a plasmid, perhaps because of the inability of Gam to inhibit an ongoing RecBCD reaction … or because of insufficient Gam expression."
- "Sergueev et al. (92) showed that Gam is lethal to E. coli when overexpressed from the PL operon via a defective prophage."
- "Dabert and Smith (36) showed that appropriately positioned Chi sites allowed the host RecABCD system to promote gene replacement with linear fragments of 6.5 kb in length, although not with the frequency or the limited homology requirements exhibited by the λ Red system."
- "Fukiya et al. (245) deleted two regions of the E. coli chromosome greater that 100 kb in size with 100% efficiency." [Cre/loxP, not linear-fragment recombineering]
File: `agent_papers_txt/Murphy_2016_lambda_recombination_recombineering_EcoSal.txt`

## Kuhlman & Cox 2010 — Site-specific chromosomal integration of large synthetic constructs
Authors: Kuhlman TE, Cox EC
Journal: Nucleic Acids Research 38:e92 | DOI: 10.1093/nar/gkp1193 | PMC2847246
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: in vivo (I-SceI) liberation of a donor fragment + λ-Red; size-vs-efficiency; 25-bp landing pads.
Key verified quotes:
- "For large fragments, it becomes increasingly difficult to generate PCR product in sufficient quantity, and the increased size of these fragments makes transformation and integration significantly less efficient."
- "Other laboratories have reported the successful and reliable integration of fragments up to ∼3.5 kb (13–16). In addition, integration efficiency can be enhanced by another order of magnitude by including homology regions 1 kb or larger (7)."
- "1000–4500-bp inserts containing the neo gene and bearing 50-bp flanking homology regions were inserted into the lacZ gene of strain K-12 MG1655 pTKRED via the method of Datsenko and Wanner (6)." [Figure 1 = efficiency vs insert size]
- "This method has proven to be very easy to use and highly successful, allowing us to insert large (7 kb) fragments into several chromosomal locations without a single failure."
- "The 25-bp size of the landing pad regions was chosen specifically to reduce the efficiency of λ-Red mediated homologous recombination 1000–10 000× below that obtained with larger (>40 bp) homology regions (7)."
- "The use of I-SceI to introduce double-strand breaks in the landing pad and donor increases the efficiency of recombination at these sites by ∼5000× (18)."
- "Induction of λ-Red increases the efficiency of insertion considerably, with the least effective insertion position (essQ-cspB) yielding 19.2% successful integrants. Without the induction of λ-Red, the efficiency of fragment insertion drops to 5.5%." (atpI-gidB and nth-ydgR: "∼100% successful integration with or without the addition of 2 mM IPTG")
- "The constitutive expression of RecA allows for efficient recombineering of recA− host strains, such as the common laboratory strain DH5α (7)."
File: `agent_papers_txt/KuhlmanCox_2010_site_specific_integration_large_constructs.txt`

## Rivero-Muller, Lajic & Huhtaniemi 2007 — ALFIRE
Title: Assisted large fragment insertion by Red/ET-recombination (ALFIRE)
Journal: Nucleic Acids Research 35:e78 | DOI: 10.1093/nar/gkm250 | PMC1904275
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: **in vivo vs in vitro liberation of a ~55 kb linear fragment** — the single most relevant published comparison for the Note_012 design.
Key verified quotes:
- "We have humanized the mouse luteinizing hormone receptor gene (Lhcgr) by inserting a ∼55 kb fragment from a BAC clone containing the human Lhcgr gene into a 170 kb BAC clone comprising the entire mouse orthologue."
- "Only 2/32 PCR screened colonies (6.3%) showed correct integration of the ∼55 kb hLhcgr insert (Table 1). This might be due to low-transformation efficiency of long linear fragments."
- Table 1 (verbatim numbers): "In vitro – 32 2 6.3 | In E. coli 0 32 0 0 | 15 32 22 69 | 20 32 16 50 | 30 32 6 19"  (cTc induction minutes, tested colonies, positive colonies, efficiency %)
- "The vector pSC101BADγβαA-I-SceI[amp] encodes the Redγ, Redβ, Redα and RecA proteins as well as the homing endonuclease I-SceI."
- "it requires two homology regions of >42 bp in a linear fragment, double strand breaks (DSBs) in both ends, and another linear or circular plasmid in order for recombination to take place."
File: `agent_papers_txt/RiveroMuller_2007_ALFIRE_large_fragment_insertion_RedET.txt`

## Maresca et al. 2010 — Single-stranded heteroduplex intermediates in λ Red homologous recombination
Authors: Maresca M, Erler A, Fu J, Friedrich A, Zhang Y, Stewart AF
Journal: BMC Molecular Biology 11:54 | DOI: 10.1186/1471-2199-11-54 | PMC2918612
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: deletion size vs insertion size asymmetry; the mechanistic ceiling at ~3 kb.
Key verified quotes:
- "Whereas beta recombination can generate deletions in target BACs of at least 50 kb at about the same efficiency as small deletions, the converse event of insertion is very sensitive to increasing size."
- "Insertions up to 3 kb are most efficiently achieved using beta recombination, however at greater sizes, an alternative Red-mediated mechanism(s) appears to be equally efficient."
- "there was overall very little drop in efficiency with increasing size of deletion from 0.5 to 50 kb. Furthermore, the strand preference for the LSP was maintained throughout all deletion sizes, even to 50 kb."
- "At 1 kb, the LSP preference was large, whereas at 2 kb it was diminished and at 3 kb there appeared to be no preference for the LSP … This relationship between length and efficiency of beta recombination could be due to limitations in the processivity or speed of Redα exonuclease activity."
File: `agent_papers_txt/Maresca_2010_ssDNA_heteroduplex_intermediates_lambdaRed.txt`

## Mosberg, Lajoie & Church 2010 — λ Red recombineering occurs through a fully single-stranded intermediate
Journal: Genetics 186:791–799 | DOI: 10.1534/genetics.110.120782 | PMC2975298
Retrieved: 2026-08-27, EPMC-PDF + pdftotext
Cited in context of: mechanism setting the size ceiling (λ Exo must degrade one full strand; Beta anneals at the fork).
Key verified quote:
- "Here, we propose an alternative in which lambda exonuclease entirely degrades one strand, while leaving the other strand intact as single-stranded DNA. This single-stranded intermediate then recombines via beta recombinase-catalyzed annealing at the replication fork."
File: `agent_papers_txt/Mosberg_2010_lambdaRed_ssDNA_intermediate.txt`

## Mosberg, Gregg, Lajoie, Wang & Church 2012 — Rational removal of endogenous nucleases
Journal: PLoS ONE 7:e44638 | DOI: 10.1371/journal.pone.0044638 | PMC3434165
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: nuclease-deletion strain backgrounds (Q6).
Key verified quotes:
- "we identify ExoVII as a nuclease which degrades the ends of single-stranded DNA (ssDNA) oligonucleotides and double-stranded DNA (dsDNA) cassettes."
- "The first, Gam, inhibits the endogenous RecBCD and SbcCD nucleases [23], which would otherwise degrade the exogenous dsDNA recombineering cassettes."
- "removing a set of five exonucleases (RecJ, ExoI, ExoVII, ExoX, and Lambda Exo) substantially improves the performance of co-selection multiplex automatable genome engineering (CoS-MAGE)." [abstract]
File: `agent_papers_txt/Mosberg_2012_removal_endogenous_nucleases_lambdaRed.txt`
(Companion: Mosberg PhD thesis, Harvard DASH, `agent_papers_txt/Mosberg_2013_thesis_lambdaRed_recombination_genome_engineering.txt`, DIRECT.)

## Chung ME, Yeh IH, Sung LY, Wu MY, Chao YP, Ng IS, Hu YC 2017 — Enhanced integration of large DNA into E. coli chromosome by CRISPR/Cas9
Journal: Biotechnology and Bioengineering 114:172–183 | DOI: 10.1002/bit.26056
Retrieved: 2026-08-27, SH
Cited in context of: **the quantitative size–efficiency curve for λ-Red ± Cas9 selection with 50 bp arms**.
Key verified quotes:
- "the recombineering-assisted efficiency was only 19%, 1% and 0% at 3.9, 5.4 and 7.0 kb, respectively, while the CRISPR/Cas9 system conferred high fidelity recombination at efficiencies as high as 92%, 71% and 61% at 3.9, 5.4 and 7.0 kb, respectively"
- "the CRISPR/Cas9 group … conferred recombination efficiencies as high as 89%, 91%, 92%, 71% and 61% at 1.4, 2.4, 3.9, 5.4 and 7.0 kb, respectively"
- "the recombination frequencies for the CRISPR/Cas9 group were 823-fold higher than those of the Control group"
- "all 10 colonies from the 1.4, 2.4, 3.9 and 5.4 kb groups gave the correct amplicon sizes, yet 5 out of 10 white colonies in the 7 kb group did not give amplicons of correct size (7 kb)."
- "CRISPR/Cas9 system also enabled the integration of donor DNA of 10 and 12 kb into the lacZ locus, albeit at lower efficiency (Fig. S8)."
- "in RecA-deficient MG1655 the CRISPR/Cas9 system remarkably improved the recombination efficiency to 99%" / "underscoring the importance of RecA in the λ-Red-assisted dsDNA integration"
- On Li et al. 2015: "increasing the DNA size significantly decreased the editing efficiency, which dropped to 35% at 5 kb and to 14% at 8 kb. Notably, such efficiency also required the use of homology arms as long as 500 bp."
File: `agent_papers_txt/Chung_2017_enhanced_integration_large_DNA_CRISPR.txt`

## Bassalo MC, Garst AD, Halweg-Edwards AL, Grau WC, Domaille DW, Mutalik VK, Arkin AP, Gill RT 2016 — Rapid and efficient one-step metabolic pathway integration in E. coli
Journal: ACS Synthetic Biology 5:561–568 | DOI: 10.1021/acssynbio.5b00187
Retrieved: 2026-08-27, SH
Cited in context of: current best single-step λ-Red+Cas9 insertion sizes; homology-arm length effect on *absolute* yield.
Key verified quotes:
- "Efficiency ranged from 84-95% over homology arm lengths of 50 to 600 bp."
- "When 600 bp of homology was used, 50% of cells that survive electroporation form CFUs (CFUs/viable cells) … However, we observed a 3 orders of magnitude drop in the amount of CFUs/viable cells when 50 bp of homology was used (Figure 2d)."
- "Co-transformation of the linear 10 kb construct with the genome-targeting gRNA resulted in successful integration of the entire pathway, with 50% of colonies displaying correct genomic junctions" (100 bp homology arms, strain BW25113 + pSIM5/pSIM521 + pX2-Cas9)
- "other efforts from our group utilized the integration strategy into SS9 to achieve 100% integration efficiency of a 5.7 kb isopropanol pathway as well as 25% integration efficiency for a 14 kb construct involved in natural product biosynthesis (data not shown)."
File: `agent_papers_txt/Bassalo_2016_onestep_pathway_integration.txt`

## Jiang Y, Chen B, Duan C, Sun B, Yang J, Yang S 2015 — Multigene editing in the E. coli genome via the CRISPR-Cas9 system
Journal: Applied and Environmental Microbiology 81:2506–2514 | DOI: 10.1128/AEM.04023-14 | PMC4357945
Retrieved: 2026-08-27, EPMC-PDF
Cited in context of: **homology-arm length series at a fixed 4.5 kb insert**.
Key verified quotes:
- "a very low mutation efficiency of 6% ± 4% was obtained when we inserted evgAS into the yjcS locus" (40 bp homology extensions)
- "We extended the homologous length in the donor DNA to ∼400 bp for the same targeting site, and a higher insertion rate of 28% ± 10% was obtained"
- "High mutation rates (92% ± 0% and 75% ± 18%, respectively) were obtained when ybaS (1.3 kb) and evgAS (4.5 kb) were inserted into yjcS" (donor carried on plasmid pTargetT with 733 bp homologous region)
- "a deficiency of cas9 in pCas or targeting sgRNA in pTarget resulted in a low level of recombination efficiency (<5%) through λ-Red recombination"
File: `agent_papers_txt/JiangY_2015_multigene_editing_CRISPR_Cas9.txt`

## Juhas M & Ajioka JW 2016 — Lambda Red recombinase-mediated integration of high molecular weight DNA into the E. coli chromosome
Journal: Microbial Cell Factories 15:172 | DOI: 10.1186/s12934-016-0571-y | PMC5050610
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: 15 kb and 50 kb chromosomal integrations — but *iterative*, 3–7 kb per round.
Key verified quotes:
- "we integrated 15 kb DNA encoding sucrose catabolism and lactose metabolism and transport operons into the fliK locus … Furthermore, with this system we integrated 50 kb of Bacillus subtilis 168 DNA into two target sites"
- "Seven DNA fragments (each approximatelly 6–7 kb in length) were first cloned into p14kan and pJScav … The alternative use of kan and cat-yfp cassettes led to the integration of all seven DNA fragments (with total length of approximately 50 kb)"
- "Sequences homologous to the target region in the E. coli chromosome (at least 60 bp in length) are introduced into the PCR amplified DNA fragments on primers."
- "the largest DNA integrated into E. coli chromosome by previous lambda Red recombinase-based approaches was about 10 kb [12–16]."
File: `agent_papers_txt/Juhas_2016_lambdaRed_highMW_DNA_integration_Ecoli.txt`

## Su B, Song D, Zhu H 2020 — Homology-dependent recombination of large synthetic pathways into E. coli genome via λ-Red and CRISPR/Cas9 dependent selection
Journal: Microbial Cell Factories 19:108 | DOI: 10.1186/s12934-020-01360-x | PMC7245811
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: state-of-the-art summary table of maximum λ-Red integration sizes.
Key verified quotes:
- "Chromosomal integration of DNA modules with the size of about 2000 bp could be accomplished through λ-Red promoted HDR with high efficiency [4]. However, the recombination efficiency could decrease drastically for large DNA modules (> 2000 bp) and chromosomal integration of DNA module which was larger than 2500 bp using λ-Red promoted HDR was very difficult [5]."
- "Currently, the maximum length of the integrated DNA modules was about 10 kb assisted by the λ-Red promoted HDR [5]."
- "we can integrate as large as 12 kb DNA module into the chromosome of E. coli W3110 in a single step … The efficiency of this method can reach 100%" (NB: single-crossover plasmid integration + λ-Red deletion of redundant sequence, not a linear substrate)
- Comparison table (verbatim): "I-SceI endonuclease Combined λ-Red and I-SceI Cleavage 19.x … Five Markerless | λ-Red recombination λ-Red assisted … fliK 15 Four Markerless … fliK 50 Seven Markerless | CRISPR/Cas9 Combined λ-Red and CRISPR/Cas9 60 Desired locus 7 One Markerless [12] | CRISPR/Cas9 Combined λ-Red and CRISPR/Cas9 50 Desired locus 10 One Markerless [13] | RecA homologous recombination Combined λ-Red, RecA and CRISPR/Cas9 100 IS5 12 One Markerless This study"
- "To facilitate the high efficiency and the preparation of the DNA modules, about 3–4 kb of the entire DNA module was optimal."
File: `agent_papers_txt/Su_2020_large_synthetic_pathways_lambdaRed_CRISPR_integration.txt`

## Fu J, Bian X, Hu S, Wang H, Huang F, Seibert PM, Plaza A, Xia L, Müller R, Stewart AF, Zhang Y 2012 — Full-length RecE enhances linear-linear homologous recombination
Journal: Nature Biotechnology 30:440–446 | DOI: 10.1038/nbt.2183
Retrieved: 2026-08-27, DIRECT (ncifrederick.cancer.gov copy)
Cited in context of: RecET vs λ Red; LLHR vs LCHR; 51–52 kb direct cloning.
Key verified quotes:
- "the restriction sites that were used to release EcoRI (10 kb), AseI (17 kb), BstZ17I (36 kb) and XhoI (51 kb) fragments." / "In all instances, full-length RecE was more than 20 times better, which was critically important for the longest (51 kb), most difficult cloning exercise."
- "both require at least 30 bp of homology with efficiencies steadily increasing as the amounts of homology increase."
- "Red-mediated recombination in an LCHR assay requires pir expression in trans … However, both the complete Red operon and RecET-Redγ mediated LLHR in the absence of pir expression, implying that replication is not required … the Red operon is more suited to LCHR, whereas RecET is more suited to LLHR."
- "we could not directly clone the largest P. luminescens PKS-NRPS clusters (plu2670; ~52 kb) using LLHR alone" … "This two-step cloning method yielded 6/21 correct, 52-kb plu2670 clones."
File: `agent_papers_txt/Fu_2012_fulllength_RecE_LLHR_direct_cloning.txt`

## Wiktor J, van der Does M, Büller L, Sherratt DJ, Dekker C 2018 — Direct observation of end resection by RecBCD in vivo
Journal: Nucleic Acids Research | DOI: 10.1093/nar/gkx1290 | PMC5829741
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: **quantifying the competing fate — RecBCD degradation of a liberated linear fragment** and the ΔrecD lever.
Key verified quotes:
- "Real-time imaging shows that RecBCD during end resection degrades DNA with remarkably high speed (∼1.6 kb/s) and high processivity (>∼100 kb)."
- "Deletion of the recD gene drastically decreased the length of resection, allowing for recombination with short ectopic plasmid homologies and significantly increasing the efficiency of horizontal gene transfer between strains."
- "the end resection process in the mutant cells was very strongly reduced and showed ∼50% resection only for the closest +1 kb marker, while the resection of any farther-out markers was not detectable at all"
- "After 4h induction, the difference was very pronounced for the case of ΔrecD cells (∼20-fold increase, t-test P ≤ 0.01…). Interestingly, recombination with the chromosome was not detected in the wild-type cells, even for the χ+ construct."
File: `agent_papers_txt/Wiktor_2018_RecBCD_end_resection_direct_observation.txt`

## Murphy KC 1991 — λ Gam protein inhibits the helicase and chi-stimulated recombination activities of E. coli RecBCD
Journal: Journal of Bacteriology 173:5808–5821 | PMC208314
Retrieved: 2026-08-27, EPMC-PDF
Cited in context of: mechanism/limits of Gam protection.
File: `agent_papers_txt/Murphy_1991_Gam_inhibits_RecBCD.txt`

## Dabert P & Smith GR 1997 — Gene replacement with linear DNA fragments in wild-type E. coli: enhancement by chi sites
Journal: Genetics 145:877–889 | PMC1207893
Retrieved: 2026-08-27, EPMC-PDF
Cited in context of: RecABCD-mediated replacement with 6.5 kb linear fragments; Chi as a design lever.
File: `agent_papers_txt/DabertSmith_1997_gene_replacement_linear_chi.txt`

## Rong R, Slupska MM, Chiang JH, Miller JH 2004 — Engineering large fragment insertions into the chromosome of E. coli
Journal: Gene 336:73–80 | DOI: 10.1016/j.gene.2004.02.054
Retrieved: 2026-08-27, SH
Cited in context of: 20 kb heterologous insertion using multi-kb homology arms (RecA pathway).
Key verified quote:
- "Two fragments of the E. coli genome, 5.5 and 6.5 kb in length, were introduced into the vector for homologous recombination … a 20-kb fragment from Lactococcus lactis genomic DNA has been successfully integrated into the chromosome of the E. coli strain J93-140."
File: `agent_papers_txt/Rong_2004_large_fragment_insertions_Ecoli_chromosome.txt`

## Isaacs FJ et al. 2011 — Precise manipulation of chromosomes in vivo enables genome-wide codon replacement (CAGE)
Journal: Science | DOI: 10.1126/science.1205822 | PMC5472332
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: "conjugative assembly" as the >100 kb route.
Key verified quotes:
- "Transfer of 1/32 of the genome (~150 kb) occurs at a frequency of ~10−4"
- "This five-stage process transfers genomic fragments ranging in size from ~154 kb to ~2.3 Mb in a controlled manner"
- "This strategy allowed us to use a tractable ~2-kb cassette in place of a cumbersome 30-kb Hfr fragment for consecutive manipulations throughout the genome."
File: `agent_papers_txt/Isaacs_2011_CAGE_genome_wide_codon_replacement.txt`

## Lee DJ, Bingle LEH, Heurlier K, Pallen MJ, Penn CW, Busby SJW, Hobman JL 2009 — Gene doctoring
Journal: BMC Microbiology 9:252 | PMC2796669
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: in vivo I-SceI liberation of the donor ("gene gorging" lineage).
Key verified quote:
- "Herring and co-workers disrupted chromosomal genes by introducing amber mutations, using long regions of homology to the chromosome and reported that the recombination frequency for gene gorging was between 1-15%."
File: `agent_papers_txt/Lee_2009_gene_doctoring_ISceI_donor_recombineering.txt`

## Wei Y, Deng P, Mohsin A, Yang Y, Zhou H, Guo M et al. 2017 — An electroporation-free method based on Red recombineering (I-CreI in vivo excision)
Journal: PLoS ONE 12:e0186891 | DOI: 10.1371/journal.pone.0186891 | PMC5655456
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: in vivo excision of the donor from a landing-pad plasmid (500 bp arms), no electroporation.
Key verified quote:
- "we present an electroporation-free λ-Red recombination method in which target DNA fragments are excised by I-CreI endonuclease in vivo from the landing pad plasmid."
- "Between the I-CreI recognition sites, there were two 500-bp homologous arms (XL and XR) and a cat cassette flanked by two I-SceI recognition sites."
File: `agent_papers_txt/Wei_2017_electroporation_free_Red_ICreI_in_vivo_excision.txt`

## Reisch CR & Prather KLJ 2015 — The no-SCAR system
Journal: Scientific Reports 5:15096 | DOI: 10.1038/srep15096 | PMC4604488
Retrieved: 2026-08-27, EPMC-XML
Cited in context of: Cas9 counterselection + λ-Red, plasmid-cured workflow.
File: `agent_papers_txt/ReischPrather_2015_noSCAR_Cas9_recombineering.txt`

## Yang J, Sun B, Huang H, Jiang Y, Diao L, Chen B, Xu C, Wang X, Liu J, Jiang W, Yang S 2014 — High-efficiency scarless genetic modification using λ Red and I-SceI cleavage
Journal: Applied and Environmental Microbiology 80:3826–3834 | DOI: 10.1128/AEM.00313-14 | PMC4054230
Retrieved: 2026-08-27, EPMC-PDF
Cited in context of: in vivo I-SceI donor liberation, iterative markerless editing.
File: `agent_papers_txt/Yang_2014_scarless_lambdaRed_ISceI.txt`

## Sabri S, Steen JA, Bongers M, Nielsen LK, Vickers CE 2013 — KIKO vectors
Journal: Microbial Cell Factories 12:60 | PMC3706339 | Retrieved 2026-08-27, EPMC-XML
File: `agent_papers_txt/Sabri_2013_KIKO_vectors_large_DNA_integration.txt`

## Wang H et al. 2018 — ExoCET
Journal: Nucleic Acids Research 46:e28 | DOI: 10.1093/nar/gkx1249 | PMC5861427 | Retrieved 2026-08-27, EPMC-XML
File: `agent_papers_txt/Wang_2018_ExoCET_RecET_direct_cloning.txt`

## Murphy KC & Campellone KG 2003 — λ Red-mediated recombinogenic engineering of EHEC/EPEC
Journal: BMC Molecular Biology 4:11 | PMC317293 | Retrieved 2026-08-27, EPMC-XML
Key verified quote: "Deletion of O-islands #130–131 (one replacement) occurred at a frequency similar to that seen with lacZ gene (~100 KanR transformants per 10^8 cell survivors)"
File: `agent_papers_txt/MurphyCampellone_2003_lambdaRed_EHEC_EPEC_recombineering.txt`

## Zhang Y, Muyrers JP, Testa G, Stewart AF 2000 — DNA cloning by homologous recombination in E. coli
Journal: Nature Biotechnology 18:1314–1317 | DOI: 10.1038/82449 | Retrieved 2026-08-27, SH
Cited in context of: gap-repair retrieval of 0.8–28 kb targets at 30–100%.
File: `agent_papers_txt/Zhang_2000_DNA_cloning_by_homologous_recombination.txt`

## Colloms SD et al. 2014 — Rapid metabolic pathway assembly using serine integrase site-specific recombination (SIRA)
Journal: Nucleic Acids Research | DOI: 10.1093/nar/gkt1101 | PMC3936721 | Retrieved 2026-08-27, EPMC-XML
File: `agent_papers_txt/Colloms_2014_serine_integrase_pathway_assembly.txt`

---

## Cas9 targeting of the T7 promoter — the excision step

_PAM availability in an 18 bp T7 promoter, guide specificity, in vivo double-cut excision in bacteria, and dCas9 roadblocks._
_Added 2026-08-27 for [Note_012 open questions](../projects/diploid_ecoli/knowledge/note012_answers/). Findings: [`A2_cas9_pT7_findings.md`](../projects/diploid_ecoli/knowledge/note012_answers/A2_cas9_pT7_findings.md)._

---

New extracts added by this agent. (Do not merge into INDEX.md/CATALOG.md until the
swarm finishes.)

## Walton, Christie, Whittaker, Kleinstiver 2020 — Unconstrained genome targeting with near-PAMless engineered CRISPR–Cas9 variants
- Authors: Russell T. Walton, Kathleen A. Christie, Madelynn N. Whittaker, Benjamin P. Kleinstiver
- Journal: Science 368:290–296 (2020)
- DOI: 10.1126/science.aba8853  (PMC7297043)
- Retrieved: 2026-08-27, NCBI efetch db=pmc id=7297043 full-text XML -> text (the
  Europe PMC / Unpaywall PDF routes returned a CAPTCHA page, not a PDF)
- Cited in context of: PAM-relaxed SpCas9 variants as a fallback if the NGG PAM
  placement at the T7 promoter is awkward.
- Key verified quotes:
  - "We developed a variant named SpG capable of targeting an expanded set of NGN
    PAMs, and further optimized this enzyme to develop a near-PAMless SpCas9
    variant named SpRY (NRN>NYN PAMs)."
  - "SpRY nuclease and base-editor variants can target almost all PAMs, exhibiting
    robust activities on a wide range of sites with NRN PAMs in human cells and
    lower but substantial activity on those with NYN PAMs."
  - "these results demonstrate that SpCas9 PAM preference can be relaxed to a
    single NGN nucleotide motif by designing a more tolerant PI domain"
- File: `agent_papers_txt/Walton_2020_SpG_SpRY_nearPAMless_Cas9.txt`

## Hu, Miller, Geurts, Tang, Chen, Sun, Zeina, Gao, Rees, Lin, Liu 2018 — Evolved Cas9 variants with broad PAM compatibility and high DNA specificity
- Journal: Nature 556:57–63 (2018)
- DOI: 10.1038/nature26155  (PMC5951633)
- Retrieved: 2026-08-27, Europe PMC fullTextXML -> text
- Cited in context of: xCas9 as a PAM-relaxed alternative; also its higher DNA specificity.
- Key verified quotes:
  - "Here we used phage-assisted continuous evolution (PACE) to evolve an expanded
    PAM SpCas9 variant (xCas9) that can recognize a broad range of PAM sequences
    including NG, GAA, and GAT."
  - "The clone with the highest PAM depletion score, xCas9 3.7, depleted NG, NNG,
    GAA, GAT, and CAA PAMs >= 100-fold compared to the starting library"
  - "despite its broadened PAM compatibility, xCas9 has much greater DNA
    specificity than SpCas9, with substantially lower genome-wide off-target
    activity"
- File: `agent_papers_txt/Hu_2018_xCas9_broad_PAM_high_specificity.txt`

## Zetsche et al. 2015 — Cpf1 Is a Single RNA-Guided Endonuclease of a Class 2 CRISPR-Cas System
- Journal: Cell 163:759–771 (2015)
- DOI: 10.1016/j.cell.2015.09.038  (PMC4638220)
- Retrieved: 2026-08-27, NCBI efetch db=pmc id=4638220 full-text XML -> text
- Cited in context of: Cas12a/Cpf1 T-rich PAM and staggered cut geometry as an
  alternative nuclease for cutting at the AT-rich T7 promoter.
- Key verified quotes:
  - "Cpf1 is a single RNA-guided endonuclease lacking tracrRNA, and it utilizes a
    T-rich protospacer adjacent motif. Moreover, Cpf1 cleaves DNA via a staggered
    DNA double stranded break."
  - "We found that the PAM for FnCpf1 is located upstream of the 5' end of the
    displaced strand of the protospacer and has the sequence 5'-TTN"
  - "The staggered cleavage site of FnCpf1 is distant from the PAM: cleavage occurs
    after the 18th base on the non-targeted (+) strand and after the 23rd base on
    the targeted (-) strand"
  - "Cpf1 introduces a staggered DNA double stranded break with a 4 or 5-nt 5' overhang."
  - NOTE: the commonly quoted "TTTV" PAM for AsCpf1/LbCpf1 is NOT stated in this
    paper; Zetsche 2015 states 5'-TTN (and that "5'-CTA but not 5'-TCA was also
    efficiently targeted"). Treat TTTV as [UNVERIFIED here].
- File: `agent_papers_txt/Zetsche_2015_Cpf1_class2_endonuclease.txt`

## Cui & Bikard 2016 — Consequences of Cas9 cleavage in the chromosome of Escherichia coli
- Journal: Nucleic Acids Research 44:4243–4251 (2016)
- DOI: 10.1093/nar/gkw223  (PMC4872102)
- Retrieved: 2026-08-27, Europe PMC fullTextXML -> text
- Cited in context of: fate of Cas9-generated free DNA ends in E. coli; why a
  double cut is lethal/degradative rather than "clean excision".
- Key verified quotes:
  - "simultaneous cleavage of all copies of the Escherichia coli chromosome at the
    same position cannot be repaired, leading to cell death. However, inefficient
    cleavage can be tolerated through continuous repair by the HR pathway."
  - "In the absence of a template for HR, extensive recession of the DNA ends by
    RecBCD and other nucleases is likely the cause of cell death."
  - "The Gam protein of phage Mu binds double stranded ends and protects the phage
    DNA from degradation by host exonulceases" ... "The expression of Gam reduced
    the number of colonies recovered after transformation of both pCas9::lacZ1 and
    pCas9::lacZ2 by a factor of 242x and 15x respectively"
  - "the introduction of a heterologous NHEJ system from Mycobacterium tuberculosis
    does not rescue cells from Cas9-mediated killing but did enable the introduction
    of small deletions at the target at low frequencies."
- File: `agent_papers_txt/CuiBikard_2016_consequences_Cas9_cleavage_Ecoli.txt`

## Standage-Beier, Zhang & Wang 2015 — Targeted Large-Scale Deletion of Bacterial Genomes Using CRISPR-Nickases
- Journal: ACS Synthetic Biology 4:1217–1225 (2015)
- DOI: 10.1021/acssynbio.5b00132  (PMC4655420)
- Retrieved: 2026-08-27, Europe PMC fullTextXML -> text
- Cited in context of: the only published bacterial route to multi-10-kb
  "two-lesion" excision in vivo — and it deliberately uses nickases, not DSBs.
- Key verified quotes:
  - "While CRISPR directed double-stranded DNA breaks are highly lethal in many
    bacteria, we show that CRISPR-guided nickase systems can be programmed to make
    precise, nonlethal, single-stranded incisions in targeted genomic regions."
  - "We demonstrate that dual-targeted nicking enables deletion of 36 and 97 Kb of
    the genome. Furthermore, multiplex targeting enables deletion of 133 Kb"
  - "sgRNA targeting GFP showed no viable colony forming units when wildtype Cas9
    (Cas9 WT) was expressed, while nicking or catalytically inactive [variants did]"
  - "The current efficiency of CRISPR-nickase targeted deletion is relatively low,
    especially compared to efficiencies of site-specific recombinases"
- File: `agent_papers_txt/StandageBeier_2015_large_deletions_CRISPR_nickases.txt`

## Bergmiller 2025 — Programming CRISPRi to control the lifecycle of bacteriophage T7
- Journal: Frontiers in Microbiology 16:1497650 (2025)
- DOI: 10.3389/fmicb.2025.1497650  (PMC11863960)
- Retrieved: 2026-08-27, Europe PMC fullTextXML -> text
- Cited in context of: strand-dependence of the dCas9 roadblock (supporting
  Alvarez 2020's non-template-strand design rule).
- Key verified quote:
  - "All sgRNAs were 20 nt long and targeted the non-template strand, which has
    been shown to effectively cause a strong roadblock for RNAP"
  - "Transcription blockage requires a single guide RNA (sgRNA) that programmes
    dCas9 to bind to the non-coding strand at a specific DNA target containing an
    NGG protospacer-adjacent motif (PAM)."
  - Caveat: this paper blocks the *E. coli* RNAP-transcribed T7 early region and
    gp1, not T7RNAP elongation itself.
- File: `agent_papers_txt/Bergmiller_2025_CRISPRi_control_T7_phage_lifecycle.txt`

## Reference sequence records used for the in-silico analysis (not papers)
- NC_001604.1  Enterobacteria phage T7, complete genome (source of the 7 native
  class III promoters, incl. phi10 at 22887..22904)
- LT727576.1   Bacterial expression vector pET-3a, complete sequence
- LT727489.1   Bacterial expression vector pET-11a, complete sequence
- OL989373.1   Cloning vector pET-28a-ZaTdT12-R335L-K337G (stock pET-28a(+)
  backbone; `regulatory 4984..5002 /note="T7 promoter"`)
- U51113.1     Cloning vector pBeloBAC11
- EU140750.1   Cloning vector pCC1BAC, complete sequence
- NC_000913.3  E. coli K-12 MG1655, complete genome (off-target reference)

## Downloads that FAILED
- Imburgio et al. 2000, Biochemistry 39:10419 (comprehensive T7 promoter-variant
  collection), DOI 10.1021/bi0003390 — not open access; Unpaywall has no OA copy;
  three Sci-Hub mirrors returned no PDF embed. Any statement about *which single
  base substitution* inactivates a T7 promoter is therefore marked [UNVERIFIED].
- Jiang Y. et al. 2015, AEM 81:2506 (multigene editing in E. coli), PMC4357945 —
  publisher blocks XML download ("The publisher of this article does not allow
  downloading of the full text in XML form."); no OA PDF. Not cited.

---

## T7 RNAP termination & processivity across genomic DNA

_Class I/II terminators, whether T7 RNAP reads E. coli intrinsic terminators, stall-site prediction, and the real processivity distribution._
_Added 2026-08-27 for [Note_012 open questions](../projects/diploid_ecoli/knowledge/note012_answers/). Findings: [`A3_t7_termination_findings.md`](../projects/diploid_ecoli/knowledge/note012_answers/A3_t7_termination_findings.md)._

---

# Catalog entries — A3_t7_termination (retrieved 2026-08-27)

All PDFs in `agent_papers/`, text extracts in `agent_papers_txt/`.
Route abbreviations: PMC = Europe PMC / PMC OA PDF; SCIHUB = Sci-Hub mirror by DOI;
OCR = scanned PDF rendered with `pdftoppm -r 300` + `tesseract`.

---

## Macdonald 1994 — Characterization of Two Types of Termination Signal for Bacteriophage T7 RNA Polymerase
Authors: Lynn E. Macdonald, Russell K. Durbin, John J. Dunn, William T. McAllister
Journal: J. Mol. Biol. 238:145-158 (1994)
DOI: 10.1006/jmbi.1994.1277  · PMID 8158645
Retrieved: 2026-08-27, SCIHUB (scanned PDF; text produced by OCR)
Cited in context of: definition of the two T7RNAP terminator types (T7-Tphi vs PTH), exact
Tphi and PTH sequences, termination efficiencies, UTP-dependence, termination-defective RNAPs.
Key verified quotes:
- "The late bacteriophage T7 terminator (T7-T[phi]) encodes an RNA sequence that can form a stable
  stem-loop structure followed by a run of six uridylate residues; termination occurs at a 3' G
  residue just downstream of the U run."
- "A sequence within the human preproparathyroid hormone (PTH) gene that encodes an interrupted
  run of six U residues, but lacks an apparent stem-loop structure, also serves as an efficient
  terminator for T7 RNA polymerase."
- "... T7 RNAP has been reported to terminate at some of these bacterial termination signals
  (Young, 1979; Jeng et al., 1990, 1992; Christiansen, 1988; Macdonald et al., 1993). However, the
  phage RNAP appears to require a more stable stem-loop structure and/or a longer U-run than does
  the bacterial RNAP for efficient termination ... and does not recognize all rho-independent
  terminators, most notably the termination signal for E. coli RNAP that lies at the end of the
  early region of T7 DNA (T7-Te; Dunn & Studier, 1980)."
- Fig. 1 sequence (T7-Tphi region, OCR):
  `CTAGCATAACCCCTTGGGGCCTCTAAACGGGTCTTGAGGGGTTTTTTGCTGA`
  wild-type termination efficiency 0.70-0.71; minimal element (-43 to +6) alone <0.15;
  downstream of the phi10 promoter "dramatically increased to as high as 0.98".
- Fig. 6 sequence (PTH terminator region, pLM44):
  `CATGGTTAAGGTAATGATTGTCATGCTTGCCATCTGTTTTCTTGCAAGATCAGA`  (efficiency 0.65);
  minimal 31 bp element (-24 to +7) "recognized nearly as efficiently as the intact signal".
- Table 1: "the efficiency of termination at the PTH terminator increases from 0.66 to 0.96 as the
  concentration of UTP is decreased" (0.5 mM -> 0.0025 mM UTP; T7-Tphi 0.62 -> 0.78 over same range).
File: agent_papers_txt/Macdonald_1994_two_classes_T7RNAP_termination_signals.txt

---

## Lyakhov 1998 — Pausing and Termination by Bacteriophage T7 RNA Polymerase
Authors: Dmitry L. Lyakhov, Biao He, Xing Zhang, F. William Studier, John J. Dunn, William T. McAllister
Journal: J. Mol. Biol. 280:201-213 (1998)
DOI: 10.1006/jmbi.1998.1854 · PMID 9654445
Retrieved: 2026-08-27, SCIHUB
Cited in context of: the class I / class II nomenclature and the ATCTGTT consensus.
Key verified quotes:
- "Termination at class I sites (typified by the signal found in the late region of T7 DNA, T[phi])
  involves the formation of a stable stem-loop structure in the nascent RNA ahead of the point of
  termination, and results in termination near runs of U. Class II sites, typified by a signal
  first identified in the cloned human preproparathyroid hormone (PTH) gene, generate no evident
  structure in the RNA but contain a conserved sequence ahead of the point of termination, and also
  contain runs of U."
- "We conclude that the 7 bp sequence ATCTGTT (5' to 3' in the non-template strand) causes
  transcribing T7 or T3 RNA polymerase to pause. Termination 6 to 8 bp past this sequence is
  favored by the presence of runs of U, perhaps because they destabilize an RNA:DNA hybrid."
- "Additional class II sites that cause pausing or termination by T7 RNAP have been identified
  within the E. coli rrnB T1 termination site, in adenovirus DNA, in a cDNA copy of vesicular
  stomatitis virus (VSV), and possibly at sites within bacteriophage lambda DNA."
- "In the absence of lysozyme, the apparent termination efficiency at T[phi] or PTH was essentially
  invariant, being about 80% for T[phi] and 55% for PTH ..."
- CJ (concatemer junction) behaves mostly as a pause: "declining rapidly from about 60% at five
  seconds to about 25% by 120 seconds".
File: agent_papers_txt/Lyakhov_1998_pausing_and_termination_T7RNAP.txt

---

## Lyakhov 1997 — Mutant Bacteriophage T7 RNA Polymerases with Altered Termination Properties
Authors: Dmitry L. Lyakhov, Biao He, Xing Zhang, F. W. Studier, John J. Dunn, William T. McAllister
Journal: J. Mol. Biol. 269:28-40 (1997)
DOI: 10.1006/jmbi.1997.1015 · PMID 9192998
Retrieved: 2026-08-27, SCIHUB
Cited in context of: (i) DIRECT evidence that T7 RNAP terminates at E. coli rrnB T1/T2;
(ii) existence of class-II read-through T7 RNAP variants; (iii) their processivity.
Key verified quotes:
- "These signals include a terminator found fortuitously in the human preproparathyroid hormone
  (PTH) gene, a pause site found in the concatamer junction (CJ) of replicating T7 DNA, and
  termination signals that are also utilized by Escherichia coli RNAP (e.g. rrnB T1 and T2)."
- "Whereas the mutant enzymes terminate normally at the late terminator in T7 DNA (T[phi]) and
  rrnB T2, they fail to terminate at one of the termination sites of rrnB T1, and also fail to
  recognize the PTH and CJ signals. The mutant enzymes exhibit normal processivity on linear
  templates, but show a slightly reduced processivity on supercoiled templates ..."
- Table 2, termination efficiencies of WILD-TYPE T7 RNAP in vitro:
  T[phi] 0.80 · rrnB T1 site A 0.65 · rrnB T2 0.64 · PTH 0.54 · rrnB T1 site B 0.62 · CJ 0.29
  (T3 RNAP: T[phi] 0.66, PTH 0.53, CJ 0.30; SP6: T[phi] 0.64, PTH 0.80)
- Table 2, mutants del163-4, 163-9A, del172-3, WIHM(178-193), insG180, insG181, R173C:
  PTH, rrnB T1 site B and CJ all <0.01, while T[phi] stays 0.72-0.77, rrnB T1 site A 0.68-0.70
  and rrnB T2 0.60-0.64.
- "the AUCUGUU sequence ... is found in the PTH, CJ and rrnB T1-site B termination signals"
- "Whereas the processivity of del172-3 (and other termination-defective RNAPs) is nearly identical
  with that of the WT enzyme on linear templates, the processivity of del172-3 on supercoiled
  templates is slightly reduced (ca twofold ...)"
File: agent_papers_txt/Lyakhov_1997_mutant_T7RNAP_altered_termination_properties.txt

---

## Jeng 1990 — Transcription Termination by Bacteriophage T7 RNA Polymerase at Rho-independent Terminators
Authors: Shih-Tong Jeng, Jeffrey F. Gardner, Richard I. Gumport
Journal: J. Biol. Chem. 265(7):3823-3830 (1990)
DOI: 10.1016/s0021-9258(19)39668-1 · PMID 2406263
Retrieved: 2026-08-27, SCIHUB (CC BY open access)
Cited in context of: the crux question — does T7 RNAP respond to E. coli intrinsic terminators?
Key verified quotes:
- "The rrnC terminator and thr attenuator are rho-independent terminators that stop both E. coli
  RNA polymerase (9-16) and T7 RNA polymerase efficiently (this work). In addition, the E. coli
  rrnBT1 terminator, another rho-independent terminator, also terminates T7 RNA polymerase in
  vitro (17, 18)."
- "T7 RNA polymerase fails to terminate at Te, a rho-independent terminator for the bacterial RNA
  polymerase that is also present in the T7 genome (19-22). Thus, not all transcription termination
  structures with the rho-independent structural motif effectively terminate the phage polymerase."
- "Results from these experiments indicate that complete readthrough occurs when there are four or
  fewer deoxyadenosine residues. With 5 template deoxyadenosine residues there is 5% termination
  increasing to 32% with 8 deoxyadenosines, the value produced by the wild-type attenuator."
- "The bacterial enzyme terminates more efficiently with the wild-type attenuator than does T7
  polymerase (90 versus 43%), and the variants have a less pronounced effect with a maximum
  decrease to 70% termination."
- Table II: wild-type thr attenuator = 43 +/- 3 % termination by T7 RNAP; every single-base
  mismatch in the G+C stem drops it to 4-20 %.
- "In all these variants, the termination efficiency of the rrnC terminator remains essentially
  constant at 29-32%."
- "Increasing the ionic strength to 150 mM NaCl or 150 mM potassium glutamate increases the
  termination efficiency of T7 RNA polymerase to 60%." ... "The termination efficiency of T7 RNA
  polymerase increased from 40% to approximately 80% as the rNTP concentration was decreased
  through this range [1 mM -> 100 uM]."
- "T7 RNA polymerase requires a more perfect region of dyad symmetry and a longer deoxyadenosine
  tract than does the bacterial enzyme to terminate with maximum efficiency."
File: agent_papers_txt/Jeng_1990_T7RNAP_termination_at_rho_independent_terminators.txt

---

## Jeng 1992 — Transcription Termination in Vitro by Bacteriophage T7 RNA Polymerase: the Role of Sequence Elements Within and Surrounding a Rho-independent Transcription Terminator
Authors: Shih-Tong Jeng, Jeffrey F. Gardner, Richard I. Gumport
Journal: J. Biol. Chem. 267(27):19306-19312 (1992)
DOI: 10.1016/s0021-9258(18)41775-9 · PMID 1527050
Retrieved: 2026-08-27, SCIHUB
Cited in context of: which E. coli intrinsic terminators T7 RNAP does and does not read.
Key verified quotes:
- "Bacteriophage T7 RNA polymerase has been reported to terminate at some rho-independent
  terminators, including T[phi], a late terminator found in the T7 genome ... and rrnBT1 of E. coli
  ... but it is unable to recognize some other rho-independent terminators, such as Te, an early
  terminator of phage T7 ... and the anti-rrnBT1 terminator."
File: agent_papers_txt/Jeng_1992_T7RNAP_termination_invitro_sequence_elements.txt

---

## Hartvig 1996 — Intrinsic termination of T7 RNA polymerase mediated by either RNA or DNA
Authors: Lars Hartvig, Jan Christiansen
Journal: EMBO J. 15(17):4767-4774 (1996)
DOI: 10.1002/j.1460-2075.1996.tb00854.x · PMID 8887568 · PMC452209
Retrieved: 2026-08-27, PMC
Cited in context of: mechanism of class I vs class II termination; independent noting of the
rrnB T1 / PTH alignment (per Lyakhov 1998).
File: agent_papers_txt/Hartvig_1996_intrinsic_termination_T7RNAP_RNA_or_DNA.txt

---

## Calvopina-Chavez 2022 — Engineering efficient termination of bacteriophage T7 RNA polymerase transcription
Authors: Diana G. Calvopina-Chavez, Mikaela A. Gardner, Joel S. Griffitts
Journal: G3 (Bethesda) 12(6):jkac070 (2022)
DOI: 10.1093/g3journal/jkac070 · PMID 35348690 · PMC9157156 · CC BY
Retrieved: 2026-08-27, PMC
Cited in context of: IN VIVO terminator efficiencies for T7RNAP; class II sites are inert in vivo;
best available synthetic T7 terminators.
Key verified quotes:
- "T7 RNA polymerase is prone to read-through transcription due to its high processivity. As a
  consequence, enforcing efficient transcriptional termination is difficult. The termination
  hairpin found natively in the T7 genome is adapted to be inefficient, exhibiting 62% termination
  efficiency in vivo and even lower efficiency in vitro."
- "By embedding a previously discovered 8-nucleotide T7 polymerase pause sequence within a
  synthetic hairpin sequence, we observed in vivo termination efficiency of 91%; by joining 2 short
  sequences into a tandem 2-hairpin structure, termination efficiency was increased to 98% in vivo
  and 91% in vitro."
- "T7RNAP transcribes DNA at a higher rate than E. coli RNA polymerase ... but its high
  processivity can result in read-through transcription and even circumnavigation of the entire
  expression plasmid."
- "For reasons not well understood, the VSV pause sequence is not effective in vivo (Du et al.
  2009, 2012). This may be due to differences in transcription rate, DNA topology, or other
  unknown cellular factors."
- "T7nat exhibits 62% termination efficiency ... T7pause shows no detectable activity [in vivo]."
- Table 1 sequences (verbatim):
  T7nat   `AACCCCTTGGGGCCTCTAAACGGGTCTTGAGGGGTTTTTTTT`
  T7pause `CtatctgttatctgttC`
  T7hyb9  `AACAGATAGCCGCGttcgCGCGGCtatctgttTTTTTTCAGATAACAGATACttcgGtatctgttatctgttTTTTTT`
  T7hyb10 `AGATAACAGATACttcgGtatctgttatctgttTTTTTTcAACAGATAGCCGCGttcgCGCGGCtatctgttTTTTTT`
- "Two out of 3 of the most successful T7 polymerase terminators also facilitated termination of
  the bacterial polymerase with around 99% efficiency."
File: agent_papers_txt/Calvopina_2022_engineering_efficient_T7RNAP_termination.txt

---

## Du 2012 — Multigene expression in vivo: supremacy of large versus small terminators for T7 RNA polymerase
Authors: Liping Du, Seth Villarreal, Anthony C. Forster
Journal: Biotechnol. Bioeng. 109(4):1043-1050 (2012)
DOI: 10.1002/bit.24379 · PMID 22094962 · PMC3312007
Retrieved: 2026-08-27, SCIHUB
Cited in context of: independent confirmation that class II terminators fail in vivo; in vivo
efficiency of the class I T[phi] terminator; tandem-terminator spacing.
Key verified quotes:
- "we address hypotheses raised in that study by showing that VSV or preproparathyroid hormone
  (PTH) small terminators spaced further apart can work independently (i.e., more efficiently)
  in vitro, and that VSV and PTH terminations are severely inhibited in vivo. Surprisingly, the
  difference between class II terminator function in vivo versus in vitro is not due to differences
  in plasmid supercoiling, as supercoiling had a minimal effect on termination in vitro."
- "each standard 100 bp class I terminator, T[phi] ... (70% termination in vitro and in vivo;
  Studier and Moffatt, 1986)"
- "This demonstrated independent termination at tandem terminators with a high combined efficiency
  of 90%. The VSV terminator-16 bp spacer-VSV terminator sequence is only 52 bp long ..."
- prior work with tandem VSV spaced 8 bp: "second and third VSV terminations (12-41%) were less
  efficient compared with the first (51-62%)".
File: agent_papers_txt/Du_2012_supremacy_large_vs_small_terminators_T7RNAP.txt

---

## Mukherjee 2003 — Discontinuous movement and conformational change during pausing and termination by T7 RNA polymerase
Authors: Srabani Mukherjee, Luis G. Brieba, Rui Sousa
Journal: EMBO J. 22(24):6483-6493 (2003)
DOI: 10.1093/emboj/cdg618 · PMID 14657021 · PMC291813
Retrieved: 2026-08-27, PMC
Cited in context of: Sousa-lab mechanism of T7RNAP pausing/termination (conformational reversal
from elongation to initiation-like state).
File: agent_papers_txt/Mukherjee_2003_discontinuous_movement_pausing_termination_T7RNAP.txt

---

## He 1998 — Characterization of an unusual, sequence-specific termination signal for T7 RNA polymerase
Authors: Biao He, Alexander Kukarin, Dmitry Temiakov, S. T. Chin-Bow, D. L. Lyakhov, M. Rong, R. K. Durbin, W. T. McAllister
Journal: J. Biol. Chem. 273(30):18802-18811 (1998)
DOI: 10.1074/jbc.273.30.18802 · PMID 9668054
Retrieved: 2026-08-27, SCIHUB
Cited in context of: class II signal requires duplex DNA downstream; single-stranded class II
signal pauses but terminates poorly.
File: agent_papers_txt/He_1998_unusual_sequence_specific_termination_signal_T7RNAP.txt

---

## Zhang & Studier 1997 — mechanism of pausing at the T7 concatemer junction
Authors: Xing Zhang, F. William Studier
Journal: J. Mol. Biol. (1997)
DOI: 10.1006/jmbi.1996.0800
Retrieved: 2026-08-27, SCIHUB
Cited in context of: the CJ class II pause site; class II conservation across T7/T3/K11.
File: agent_papers_txt/Zhang_Studier_1997_mechanism_pausing_T7RNAP_concatemer_junction.txt

---

## Iost 1992 — Bacteriophage T7 RNA polymerase travels far ahead of ribosomes in vivo
Authors: Isabelle Iost, Jacqueline Guillerez, Marc Dreyfus
Journal: J. Bacteriol. 174(2):619-622 (1992)
DOI: 10.1128/jb.174.2.619-622.1992 · PMID 1729251 · PMC205757
Retrieved: 2026-08-27, PMC
Cited in context of: IN VIVO T7RNAP elongation rate; the Rho question.
Key verified quotes:
- "On this basis, the elongation rates are ca. 200 and 25 nt/s for the T7 and host RNA polymerases,
  respectively. This eightfold difference is unmistakable."
- "Neglecting the induction lag, the average translation rate is then 7 codons (21 nt) per s."
- "Therefore, transcription by T7 RNA polymerase generates extensive ribosome-free mRNA regions
  behind the polymerase. Although these regions may bind the rho factor, it is not known whether
  this can induce termination of transcription. However, should this occur, the rho effect upon T7
  RNA polymerase would still differ radically from that upon the E. coli enzyme, insofar as
  ribosomes, lagging far behind transcription, are now unlikely to interfere with rho action."
File: agent_papers_txt/Iost_1992_T7RNAP_travels_far_ahead_of_ribosomes_in_vivo.txt

---

## Kim & Larson 2007 — Single-molecule analysis of 1D diffusion and transcription elongation of T7 RNA polymerase along individual stretched DNA molecules
Authors: Ji Hoon Kim, Ronald G. Larson
Journal: Nucleic Acids Res. 35(11):3848-3858 (2007)
DOI: 10.1093/nar/gkm332 · PMID 17526520 · PMC1920259
Retrieved: 2026-08-27, PMC
Cited in context of: single-molecule T7 elongation rates (no run-length measurement).
Key verified quotes:
- "T7 DNA (39.9 kbp, Boca Scientific) was used as supplied."
- "rate is found to be 42 +/- 8 nt/s (n = 16) for 0.2 mM NTPs, which agrees well with recent single
  molecule measurement under similar conditions (43 +/- 3.2 nt/s for 0.25 mM ...)"
- "We obtain Vmax = 149 nt/s and KM = 0.4 mM"
- rates: "30 +/- 8 nt/s (n = 11) for 0.1 mM NTP, 49 +/- 4 nt/s (n = 9) for 0.2 mM NTP,
  72 +/- 13 nt/s (n = 12) for 0.4 mM NTP, and 95 +/- 15 nt/s ..."
File: agent_papers_txt/KimLarson_2007_single_molecule_1D_diffusion_T7RNAP_elongation.txt

---

## Zernia 2025 — Heterogeneous template-dependent transcription dynamics of T7 RNAP revealed by single-molecule imaging
Authors: Sarah Zernia, Joelle Deplazes-Lauber, Jonas Huber, Johannes Stigler
Journal: Proc. Natl. Acad. Sci. USA 122(50):e2514125122 (2025)
DOI: 10.1073/pnas.2514125122 · PMID 41364756 · PMC12718388
Retrieved: 2026-08-27, PMC
Cited in context of: THE stress test of T7RNAP processivity — direct single-molecule run-length
measurement on a 49.4 kbp template; pause densities; class II motif recovered de novo.
Key verified quotes:
- "We generated a 49.4 kbp long DNA substrate with two T7 promoter sequences (P1, P2) ..."
- "The high-throughput nature of the assay allowed us to record trajectories of 1,175 individual
  RNAPs. RNAPs transcribed with a single pause-free velocity of 123 +/- 12 nt/s (mean +/- SD)"
- "T7 RNAP spent about 23 +/- 5% of its time in a paused state (Table 1)." Table 1 also gives
  "fraction of dissociation events that occurred during a paused state" = 49 +/- 3 % (standard).
- "While short pauses generally occurred more frequently with an average rate of 0.16 +/- 0.01/kbp,
  long pauses were much rarer overall, occurring at a baseline rate of ~0.04 kbp-1, but showed
  strong enrichment at ~21 kbp and ~40 kbp."
- "The data revealed a monoexponential decay in RNAP survival up to the 40-kbp pause position ...,
  where about 45% of remaining RNAPs stalled and terminated."
- **"To quantify the effect of buffer conditions outside of the strong 40-kbp termination site, we
  calculated the extrapolated mean run length before reaching this position. Both reduced nucleotide
  conditions (11.8 +/- 2.3 kbp) and DMSO (13.7 +/- 1.2 kbp) displayed a reduced run length, compared
  to standard conditions (19.5 +/- 3.6 kbp) (Fig. 4C). Hence, premature termination happens more
  frequently under these conditions leading to heterogeneous RNA transcripts."**
- "Motif 3 matches with the PTH terminator consensus sequence that is known to induce hairpin-free
  pausing and termination of T7 RNAP ... we found a significantly reduced production of transcript
  with the template containing motif 3 ... However, also motif 2, 6, 9, and 11 led to reduced
  transcription, which suggests that there might be alternative pausing signals besides the
  previously reported motif."
- "Generally, no single sequence feature reliably predicted pauses."
- "a reduction of NTPs caused a substantial increase of termination at the 40-kbp site ..., with
  approximately 77% of RNAPs terminating at this position"
File: agent_papers_txt/Zernia_2025_heterogeneous_template_dependent_T7RNAP_single_molecule.txt

---

## Roots & Barrick 2024 — CryptKeeper: a negative design tool for reducing unintentional gene expression in bacteria
Authors: Cameron T. Roots, Jeffrey E. Barrick
Journal: Synthetic Biology (Oxford) 9(1):ysae018 (2024)
DOI: 10.1093/synbio/ysae018 · PMID 39722801 · PMC11669485 · CC BY
Retrieved: 2026-08-27, PMC
Cited in context of: the recommended off-the-shelf scanning pipeline, and the explicit statement
that T7-specific prediction does not exist.
Key verified quotes:
- "Intrinsic (Rho-independent) terminators are predicted using TransTermHP version 2.09 [28].
  Rho-dependent terminators are predicted using a fork of RhoTermPredict version 3.4.0 [23] ...
  CryptKeeper displays predictions of E. coli sigma70 promoters from a fork of the Promoter
  Calculator version 1.2.2 [29]"
- "prediction of intrinsic terminators reaches >90% accuracy and specificity [28] and should
  generalize to many other bacterial species. However, there is almost always some read-through of
  these terminators [42, 43], and this characteristic is not predicted by current tools."
- **"Tools for predicting transcription initiation rates driven by alternative sigma factors,
  transcription driven by T7 RNA polymerase, and quantitative predictions of terminator
  read-through are also needed to complete the picture of transcription in this host."**
File: agent_papers_txt/RootsBarrick_2024_CryptKeeper_negative_design_unintended_expression.txt

---

## Thiel 2001 — Infectious RNA transcribed in vitro from a cDNA copy of the human coronavirus genome cloned in vaccinia virus
Authors: Volker Thiel, Jens Herold, Barbara Schelle, Stuart G. Siddell
Journal: J. Gen. Virol. 82(Pt 6):1273-1281 (2001)
DOI: 10.1099/0022-1317-82-6-1273 · PMID 11369870
Retrieved: 2026-08-27 — **FULL TEXT NOT OBTAINED.** Sci-Hub has no copy for this DOI/PMID;
microbiologyresearch.org is behind Cloudflare (HTTP 403 to both curl and WebFetch); Unpaywall
reports the OA status as BRONZE with only the publisher DOI as the location. **Abstract only**
(verified from Europe PMC, EXT_ID:11369870).
Cited in context of: THIS IS REFERENCE 24 OF MENGISTE 2023 — the primary source of the "30 kb"
T7RNAP processivity figure.
Key verified quotes (abstract):
- "The coronavirus genome is a positive-strand RNA of extraordinary size and complexity. It is
  composed of approximately 30000 nucleotides and it is the largest known autonomously replicating
  RNA."
- "This system is based upon the in vitro transcription of infectious RNA from a cDNA copy of the
  human coronavirus 229E genome that has been cloned and propagated in vaccinia virus."
Claims about the exact IVT conditions (enzyme lot, cap analogue, temperature, yield, whether
full-length RNA was the major product) are [UNVERIFIED] — full text not read.
File: none (no PDF obtained)

---

## Mengiste 2023 — Expanded MutaT7 toolkit efficiently and simultaneously accesses all possible transition mutations in bacteria
(already in the library; re-examined for this task)
Journal: Nucleic Acids Res. 51(6):e31 · DOI 10.1093/nar/gkad003 · PMC10085711
Key verified quote (the sentence the user read as "30 kb"):
- "This 'MutaT7' method relies on a fusion protein, MutaT7 C->T (previously referred to simply as
  MutaT7), composed of the cytidine deaminase rAPOBEC1 and the highly processive T7 RNA polymerase
  (T7RNAP), which is known to unceasingly transcribe at least 30 kb of DNA (24)."
Reference 24, verbatim from the PMC XML ref-list (efetch db=pmc id=PMC10085711):
- "24. Thiel V., Herold J., Schelle B., Siddell S.G. Infectious RNA transcribed in vitro from a
  cDNA copy of the human coronavirus genome cloned in vaccinia virus. J. Gen. Virol. 2001;
  82:1273-1281. 11369870 10.1099/0022-1317-82-6-1273"
Also verified: Mengiste's own processivity test spans only KanR (~800 bp) + ~800 bp filler +
TetR (~1.2 kb), i.e. ~2.8 kb: "the placement of a 'filler' DNA region (~800 bp) between Kan R
(~800 bp) and Tet R (~1.2 kb) allows us to assess the processivity of MutaT7 A->G and eMutaT7 A->G"
and "The general similarity between kanamycin and tetracycline resistance frequencies is consistent
with the processive nature of T7RNAP-based tools".
File: agent_papers_txt/Mengiste_2023_expanded_MutaT7_toolkit_all_transitions.txt


---

## Skinner 2004 — Promoter binding, initiation, and elongation by bacteriophage T7 RNA polymerase: a single-molecule view of the transcription cycle
Authors: Gary M. Skinner, Christoph G. Baumann, Diana M. Quinn, Justin E. Molloy, James G. Hoggett
Journal: J. Biol. Chem. 279(5):3239-3244 (2004)
DOI: 10.1074/jbc.M310471200 · PMID 14597619
Retrieved: 2026-08-27, SCIHUB
Cited in context of: earlier single-molecule work; run length here is template-limited, not a
processivity limit; contrast with Zernia 2025 on pausing.
Key verified quotes:
- "the table in Fig. 3c shows the results of linear regressions for six of the longest events
  (mean run length = 1200 +/- 330 bp), from which a kpol of 43 +/- 3.2 nt s-1 was obtained
  (T = 22 degC)."
- "Reversible pausing of T7 RNAP during elongation was not observed."
- "a T7 RNAP-promoter DNA dissociation rate constant (koff) of ~2.9 s-1" (n = 676 binding events)
- rate for closed complex -> processive EC transition: "0.36 s-1"
NOTE: the ~1200 bp run length is the length of the transcription unit assayed, NOT a processivity
ceiling. Do not quote it as a T7 processivity figure.
File: agent_papers_txt/Skinner_2004_promoter_binding_initiation_elongation_T7RNAP_single_molecule.txt

---

## Thomen 2008 — T7 RNA polymerase studied by force measurements varying cofactor concentration
Authors: P. Thomen, P. J. Lopez, U. Bockelmann, J. Guillerez, M. Dreyfus, F. Heslot
Journal: Biophys. J. 95(5):2423-2433 (2008)
DOI: 10.1529/biophysj.107.125096 · PMID 18708471 · PMC2517023
Retrieved: 2026-08-27, PMC
Cited in context of: optical-tweezers T7 elongation kinetics; the pre-2025 view that T7 pauses are
rare (superseded by Zernia 2025's higher-throughput assay).
Key verified quotes:
- "pauses are extremely rare events with this enzyme. This has been observed both in our experiment
  using the lambda DNA ..."
File: agent_papers_txt/Thomen_2008_T7RNAP_force_measurements_cofactor.txt

---

## Alvarez 2020 — In vivo diversification of target genomic sites using processive base deaminase fusions blocked by dCas9 (T7-DIVA)
(already in the library; re-examined for this task; DOI re-verified via Europe PMC)
Authors: Beatriz Alvarez, Mario Mencia, Victor de Lorenzo, Luis Angel Fernandez
Journal: Nat. Commun. 11:6436 (2020) · DOI 10.1038/s41467-020-20230-z · PMID 33353963 · PMC7755918
Cited in context of: the only IN VIVO demonstration that a deaminase-T7RNAP fusion can be stopped
by a DNA-bound protein roadblock.
Key verified quotes:
- "the mutagenesis of sacB dropped ~10-fold when the double crRNAb.a was expressed"
- "these results demonstrate that targeted dCas9 blockade with a triple crRNA array can be used to
  concentrate the mutagenesis activity of BD-T7RNAP fusions to a specific target gene or gene
  segment, reducing the mutagenesis of downstream DNA regions"
- "The BD-T7RNAP fusions were able to transcribe the gfp gene downstream of URA3 ... This confirms
  that BD-T7RNAP fusions are able to mutate regions downstream of the target gene."
File: agent_papers_txt/Alvarez_2020_T7DIVA_dCas9_bounded_deaminase_T7RNAP.txt

---

## FAILED DOWNLOADS (claims depending on these are marked [SECONDARY] or [UNVERIFIED])
- Dunn J.J. & Studier F.W. (1983) "Complete nucleotide sequence of bacteriophage T7 DNA and the
  locations of T7 genetic elements." J. Mol. Biol. 166:477-535. DOI 10.1016/0022-2836(83)90011-3.
  Not on Sci-Hub, not OA. Everything attributed to it here is quoted from papers that cite it
  (Macdonald 1994, Lyakhov 1998, Calvopina 2022, Jeng 1990/1992) -> marked [SECONDARY].
- Thiel 2001 full text (see above) -> abstract only.

---

## Deaminase–RNAP fusion architecture — linkers & obtainability

_XTEN vs GGS across the MutaT7 family, linker-length titrations, and what is actually deposited._
_Added 2026-08-27 for [Note_012 open questions](../projects/diploid_ecoli/knowledge/note012_answers/). Findings: [`A4_linkers_addgene_findings.md`](../projects/diploid_ecoli/knowledge/note012_answers/A4_linkers_addgene_findings.md)._

---

## Moore, Papa & Shoulders 2018 — A Processive Protein Chimera Introduces Mutations across Defined DNA Regions In Vivo
- **Authors:** Christopher L. Moore, Louis J. Papa III, Matthew D. Shoulders
- **Journal:** J. Am. Chem. Soc. 2018, 140(37):11560–11564
- **DOI:** 10.1021/jacs.8b04001 (PMID 29991261; PMC6166643)
- **Retrieved:** 2026-08-27 — main text from the user's Zotero library (item MHRDILMU, collection "Directed Evolution"); Supporting Information PDF from PubMed Central (`pmc.ncbi.nlm.nih.gov/articles/instance/6166643/bin/NIHMS987007-supplement-SI.pdf`, fetched by solving the NCBI proof-of-work challenge).
- **Cited in context of:** the original MutaT7 (rApo1–T7RNAP); linker identity; mutation window; Addgene obtainability.
- **Key verified quotes:**
  - "The rApo1 gene was amplified from pET28b-BE1 and the T7 RNA polymerase gene was amplified from pTara." (SI, "Cloning and Recombineering")
  - "We assayed for MutaT7 processivity by inserting a tetracycline-resistance (TetR) gene with an inactive, ACG start codon ~1.6 kb downstream of the KanR gene… We observed high levels of MutaT7-dependent tetracycline resistance only in reporter strains having the T7 promoter, consistent with targeted and processive introduction of mutations across a lengthy, multi-kb DNA region"
  - "tolerated an rApo1 N-terminal fusion and still efficiently transcribed tens of kilobases (Figure S1)"
  - SI pages S24–S77 contain full **Plasmid Sequences**, including the construct "BBa J23114 lacO MutaT7" (9,352 bp) — the source of the exact linker (see findings file).
- **Files:** `agent_papers/Moore_2018_MutaT7_processive_protein_chimera.pdf`, `agent_papers_txt/Moore_2018_MutaT7_processive_protein_chimera.txt`; SI: `agent_papers/Moore_2018_MutaT7_SI.pdf`, `agent_papers_txt/Moore_2018_MutaT7_SI.txt`

## Schellenberger et al. 2009 — A recombinant polypeptide extends the in vivo half-life of peptides and proteins in a tunable manner
- **Authors:** Volker Schellenberger, Chia-wei Wang, Nathan C. Geething, Benjamin J. Spink, et al.
- **Journal:** Nature Biotechnology 2009, 27:1186–1190
- **DOI:** 10.1038/nbt.1588 (PMID 19915550). Not open access; no PMC record.
- **Retrieved:** 2026-08-27 via Sci-Hub (sci-hub.ru → sci-hub.red storage). Unpaywall reports `is_oa: false`.
- **Cited in context of:** the origin and design principles of XTEN.
- **Key verified quotes:**
  - "genetic fusion of an unstructured recombinant polypeptide of 864 amino acids, called XTEN, to a peptide or protein provides an apparently generic approach to extend plasma half-life"
  - "In designing a soluble, chemically stable and predominantly unstructured polypeptide that provides a maximal hydrodynamic radius to shield its protein payload, we first excluded hydrophobic amino acids… Cysteine residues can cause heterogeneous disulfide cross-linking."
  - "our initial designs focused exclusively on six amino acids (A, E, G, P, S and T)."
  - "To create a genetically stable, highly expressed, unstructured polypeptide in Escherichia coli, we generated a library of nonrepetitive 36-[mer building blocks]"
- **File:** `agent_papers/Schellenberger_2009_XTEN_recombinant_polypeptide_halflife.pdf`, `agent_papers_txt/Schellenberger_2009_XTEN_recombinant_polypeptide_halflife.txt`

## Komor et al. 2016 — Programmable editing of a target base in genomic DNA without double-stranded DNA cleavage (BE1/BE2/BE3)
- **Authors:** Alexis C. Komor, Yongjoo B. Kim, Michael S. Packer, John A. Zuris, David R. Liu
- **Journal:** Nature 2016, 533:420–424
- **DOI:** 10.1038/nature17946 (PMID 27096365; PMC4873371)
- **Retrieved:** 2026-08-27 from PubMed Central (author manuscript PDF + supplement-1.pdf), via the NCBI proof-of-work route.
- **Cited in context of:** the 16-residue XTEN linker sequence; the only published linker-length↔editing-window titration in the deaminase-fusion family.
- **Key verified quotes:**
  - "Fusing rAPOBEC1 to the N-terminus, but not the C-terminus, of dCas9 preserves deaminase activity (Extended Data Fig. 1a)."
  - "Conversion efficiency was greatest using rAPOBEC1–dCas9 linkers over nine amino acids in length. The number of positions susceptible to deamination (the 'activity window') increases from approximately three to six nt as the linker length was extended from three to 21 amino acids (Extended Data Fig. 1c-f). The 16-residue XTEN linker offered a promising balance between these two characteristics, with an efficient deamination window of approximately five nt, typically from positions 4 to 8 within the protospacer"
  - Methods: "plasmids encoding pET28b-His6-rAPOBEC-linker-dCas9 with GGS, (GGS)3, XTEN, or (GGS)7 linkers"
  - SI Supplementary Sequences, "BE1 for E. Coli expression (His6-rAPOBEC1-XTEN-dCas9)": "…LTFFTIALQSCHYQRLPPHILWATGLK**SGSETPGTSESATPES**DKKYSIGLAIGTNSVGWAVITDEYKVPSK…"
- **Files:** `agent_papers/Komor_2016_BE3_programmable_base_editing.pdf` + `.txt`; `agent_papers/Komor_2016_BE3_SI.pdf` + `agent_papers_txt/Komor_2016_BE3_SI.txt`

## Gaudelli et al. 2017 — Programmable base editing of A•T to G•C in genomic DNA without DNA cleavage (ABE)
- **Authors:** Nicole M. Gaudelli, Alexis C. Komor, Holly A. Rees, Michael S. Packer, Ahmed H. Badran, David I. Bryson, David R. Liu
- **Journal:** Nature 2017, 551:464–471
- **DOI:** 10.1038/nature24644 (PMID 29160308; PMC5726555)
- **Retrieved:** 2026-08-27 — Supplementary Information (`NIHMS913981-supplement-1.docx`) from PubMed Central via the proof-of-work route.
- **Cited in context of:** the 32-aa ABE linker that embeds XTEN; the source of TadA7.10 used by Mengiste 2023.
- **Key verified quotes:**
  - "The architecture of the base editors used during bacterial selection is: TadA*–linker(16 aa)–dCas9."
  - Supplementary Sequences 3, ABE7.10 = "ecTadA(wt) – linker (32 aa) – ecTadA*(7.10) – linker(32 aa) – Cas9 nickase – NLS"; the 32-aa linker is verbatim **SGGSSGGSSGSETPGTSESATPESSGGSSGGS**; the Cas9→NLS junction is **SGGS**.
- **Files:** `agent_papers/Gaudelli_2017_ABE_SI.docx`, `agent_papers_txt/Gaudelli_2017_ABE_SI.txt`

## Chen, Liu, Padula et al. 2020 — Efficient, continuous mutagenesis in human cells using a pseudo-random DNA editor (TRACE)
- **Authors:** Haiqi Chen, Sophia Liu, Samuel Padula, Daniel Lesman, Jonathan L. Marshall, et al.; Fei Chen (corresponding)
- **Journal:** Nature Biotechnology 2020, 38:165–168
- **DOI:** 10.1038/s41587-019-0331-8 (PMID 31844291; PMC7775643)
- **Retrieved:** 2026-08-27 from PubMed Central (author manuscript PDF, Supplementary Tables .docx, Supplementary Data Set 1 .xlsx) via the proof-of-work route.
- **Cited in context of:** MutaT7 logic in mammalian cells; linker; editing window and rate; obtainability.
- **Key verified quotes:**
  - "To generate pAPOBEC-T7 and pAPOBEC-T7-UGI, the Cas9 (D10A) in the pCMV-BE3 construct was replaced with T7 RNAP by Gibson assembly. The original T7 promoter was deleted to avoid self-editing. To generate pAID-T7 and pAID-T7-UGI, rat APOBEC1 in pAPOBEC-T7 and pAPOBEC-T7-UGI was replaced with AID*Δ amplified from pGH335_MS2-AID*Δ-Hygro."
  - "a window of ~2,000 base pairs (bp) downstream of the T7 promoter was amplified by PCR for sequencing"
  - "(0.76 kb−1 C>T and 0.7 kb−1 G>A in pAPOEC-T7; 0.8 kb−1 C>T and 0.74 kb−1 G>A in pAPOBEC-T7-UGI; Fig. 1d)"
  - Supplementary Table 6: "TRACE (our method) | Human | ~2 kbp−1 per 3 days (mainly C->T & G->A) | At least 2000 bp per T7 promoter"
  - Supplementary Data Set 1 primer "To amplify the insert for pAPOBEC-T7": `GAGTCCGCCACACCCGAAAGTAACACCATCAACATTGCTAAGAAC` (= …E S A T P E S | N T I N I A K N…), i.e. the BE3 XTEN linker is retained at the deaminase→T7RNAP junction. Primers 34/38 show `…TCTGGTGGTTCT…` (SGGS) at the T7RNAP→NLS and T7RNAP→UGI junctions.
- **Files:** `agent_papers/Chen_2020_TRACE_T7_continuous_editing_human_cells.pdf` + `.txt`; `agent_papers/Chen_2020_TRACE_SI_Tables.docx` + `agent_papers_txt/Chen_2020_TRACE_SI_Tables.txt`; `agent_papers/Chen_2020_TRACE_SupplementaryDataSet1.xlsx`

## Supplementary material added for papers already in the catalogue
(Not new papers — supplementary files retrieved 2026-08-27 for texts already present in `agent_papers_txt/`.)
- **Park & Kim 2021** (NAR 49:e32, DOI 10.1093/nar/gkaa1231, PMC8034631) — supplementary PDF: `agent_papers/Park_Kim_2021_eMutaT7_SI.pdf`, `agent_papers_txt/Park_Kim_2021_eMutaT7_SI.txt`. Contains the **linker-length titration** (Supplementary Figure 5B) and the primers that define both the XTEN and the original-MutaT7 linkers.
- **Seo et al. 2023** (NAR 51:e58, DOI 10.1093/nar/gkad266, PMC10250238) — supplementary PDF: `agent_papers/Seo_2023_eMutaT7transition_SI.pdf`, `agent_papers_txt/Seo_2023_eMutaT7transition_SI.txt`. Contains Supplementary Figure S5, "Linker optimization of a triple fusion protein, PmCDA1_TadA-8e_T7RNAP".
- **Mengiste et al. 2023** (NAR 51:e31, DOI 10.1093/nar/gkad003) — supplementary PDF (from the user's Zotero item N39K4U2I, "SI revised-V2.pdf"): `agent_papers/Mengiste_2023_SI.pdf`, `agent_papers_txt/Mengiste_2023_SI.txt`. Contains Tables S1–S4 (strains with BCCM accessions, plasmids with GenBank accessions, primers, additional sequences).
- **Álvarez et al. 2020** (Nat Commun 11:6436, DOI 10.1038/s41467-020-20230-z) — Supplementary Information PDF from nature.com: `agent_papers/Alvarez_2020_T7DIVA_SI.pdf`, `agent_papers_txt/Alvarez_2020_T7DIVA_SI.txt`. Contains Supplementary Table 2 with the GenBank accessions for every fusion plasmid.

## NOT OBTAINED
- **Mengiste et al. 2024 — MutaT7^GDE** (ACS Synth. Biol. 2024, 13(9):2693–2701, DOI 10.1021/acssynbio.4c00316, PMID 39190860). Paywalled at ACS (HTTP 403); no PMC record (Europe PMC: `pmcid: None`, `isOpenAccess: N`); not present on Sci-Hub mirrors (sci-hub.ru returns a landing page with no `citation_pdf_url`; .se/.st unreachable). **All statements about this paper's construct details are [UNVERIFIED].**

---

## Mutation rates & the transitions-only ceiling

_What each system actually measured, and why deaminases cannot reach transversions._
_Added 2026-08-27 for [Note_012 open questions](../projects/diploid_ecoli/knowledge/note012_answers/). Findings: [`A5_rates_spectrum_findings.md`](../projects/diploid_ecoli/knowledge/note012_answers/A5_rates_spectrum_findings.md)._

---

# Catalog staging — agent `A5_rates_spectrum` (2026-08-27)

New PDFs/text extracts added this session. Do NOT merge until the swarm finishes.

---

## Moore, Papa & Shoulders 2018 — A Processive Protein Chimera Introduces Mutations across Defined DNA Regions In Vivo
- **Authors:** Christopher L. Moore, Louis J. Papa III, Matthew D. Shoulders
- **Journal:** Journal of the American Chemical Society **140**, 11560–11564 (2018)
- **DOI:** 10.1021/jacs.8b04001  (PMID 29991261, PMC6166643)
- **Retrieved:** 2026-08-27 — PDF already in user's Zotero (item `MHRDILMU`), pulled with `scripts/zotero_fetch.py fetch MHRDILMU`; `pdftotext -layout`.
- **Cited in context of:** the parent MutaT7 (rAPOBEC1–T7RNAP) system; baseline mutation frequency and spectrum; terminator-array delimitation; UGI as alternative to Δung.
- **Key verified quotes:**
  - "four copies of the T7 terminator fully constrained mutagenesis to the intended upstream KanR gene"
  - "Sanger sequencing of streptomycin-resistant DNA isolated from a MutaT7-expressing strain of E. coli again revealed that multiple mutations appeared throughout the targeted rpsL gene, with ~90% C→T mutations and ~10% G→A mutations"
  - "(c) Normalized mutation frequency (number of mutations observed divided by kb of DNA sequenced in associated regions)" [Fig. 3 legend]
  - "the average kanamycin resistance frequency for MP6 was 6.7 × 10–6 versus 5.7 × 10–5 for MutaT7" [NB: appears internally inconsistent with the preceding clause in the accepted manuscript — see findings file]
  - "A disadvantage of MutaT7 is its limited mutational spectrum and an apparent strand bias"
  - "Such co-expression [of UGI] resulted in a high rate of mutagenesis similar to that achieved using Δung cells"
- **File:** `agent_papers_txt/Moore_2018_MutaT7_processive_chimera_JACS.txt`

---

## Halperin, Tou, Wong, Modavi, Schaffer & Dueber 2018 — CRISPR-guided DNA polymerases enable diversification of all nucleotides in a tunable window
- **Journal:** Nature **560**, 248–252 (2018)
- **DOI:** 10.1038/s41586-018-0384-8  (PMID 30069054)
- **Retrieved:** 2026-08-27 — not OA (Unpaywall `is_oa: false`, no PMC record); obtained via Sci-Hub mirror `sci-hub.ee` → `sci.bban.top`; `pdftotext -layout`.
- **Cited in context of:** EvolvR; nick-translation error-prone PolI as a transversion-capable alternative to deaminases; the explicit statement of the cytidine-deaminase amino-acid ceiling.
- **Key verified quotes:**
  - "fluctuation analysis estimated the mutation rate of wild-type E. coli to be approximately 10−10 mutations per nucleotide per generation"
  - "markedly increased the mutation rate at the targeted locus 24,500-fold over the wild type while increasing the global mutation rate 120-fold over the wild type"
  - "elevated the mutation rate at the targeted locus by 212,000-fold (8.7-fold greater than nCas9–PolI3M)"
  - "PolI3M with the additional mutations F742Y and P796H (PolI5M) displayed a mutation rate one nucleotide from the nick that was 7,770,000-fold higher than wild-type cells, and 33-fold higher than PolI3M"
  - "fusing nCas9 to PolI3M resulted in substitutions across an approximately 17-nucleotide window 3′ from the nick"
  - "c, Distribution of the substituted nucleotides; all four nucleotides were substituted by nCas9–PolI3M." — figure values: A (56.5%), T (26.1%), G (8.7%), C (8.7%)
  - "The off-target mutation rate decreased 4.14-fold when [codon-optimised] … the on-target mutation rate only decreased 1.23-fold"
  - Extended Data Fig. 1 legend: "This chart shows which amino acids can (green) and cannot (red) be reached by mutating cytosines and guanines to any other base for each of the 64 codons, highlighting that only 32% of missense mutations are achievable with targeted cytidine deaminases."
- **File:** `agent_papers_txt/Halperin_2018_EvolvR_CRISPR_guided_polymerases.txt`

---

## Chen, Liu, Padula, Lesman, Griswold, Lin, Zhao, Marshall & Chen 2020 — Efficient, continuous mutagenesis in human cells using a pseudo-random DNA editor (TRACE)
- **Journal:** Nature Biotechnology **38**, 165–168 (2020)
- **DOI:** 10.1038/s41587-019-0331-8  (PMID 31844291, PMC7775643)
- **Retrieved:** 2026-08-27 — Europe PMC PDF render 403'd; obtained via Sci-Hub mirror `sci-hub.ee` → `sci.bban.top`; `pdftotext`.
- **Cited in context of:** MutaT7 logic in human cells; UGI-containing vs UGI-free editors and the absence of transversion products; mutation rates per kb.
- **Key verified quotes:**
  - "The most efficient variant, pAID-T7-UGI, showed an average C>T mutation rate of 1.47 mutations per 1,000 bp (kb−1) and an average G>A mutation rate of 3.1 kb−1"
  - "the average mutation rate (0.76 kb−1 C>T and 0.7 kb−1 G>A in pAPOEC-T7; 0.8 kb−1 C>T and 0.74 kb−1 G>A in pAPOBEC-T7-UGI)"
  - "The rate of mutation to other bases from C and G was comparable between conditions (Supplementary Fig. 2b)."
  - "The measured genomic C>T and G>A substitution rate was in the order of 10−6 bp−1 after 6 d of diversification … By contrast, TRACE induced on-target (T7 promoter driven) C>T and G>A mutation rates in the order of 10−3 bp−1"
  - "a window of ~2,000 base pairs (bp) downstream of the T7 promoter"
  - "average C>T and G>A mutation rates in a tunable range from ~0.5 kb−1 to 4 kb−1 within a week"
- **File:** `agent_papers_txt/Chen_2020_TRACE_pseudorandom_DNA_editor.txt`

---

## Ong, Ghode, Narenderan, Lao, Willenborg, Eden, Marsh, Yew & Fredens 2026 — Bridging continuous and discrete evolution through a controllable, hypermutagenic phage-bacteria system (LySE)
- **Journal:** Nature Microbiology **11**, 1585–1597 (2026)
- **DOI:** 10.1038/s41564-026-02346-y
- **Retrieved:** 2026-08-27 — PDF already in user's Zotero (item `2RADSJ4P`), pulled with `scripts/zotero_fetch.py fetch 2RADSJ4P`; `pdftotext`.
- **Cited in context of:** T7 **DNA** polymerase–deaminase fusion (not RNAP); TadA-8e reuse; TadDE dual deaminase; a transition-biased but NOT transition-limited spectrum; 39–40 kb cargo.
- **Key verified quotes:**
  - "We developed a hypermutagenic T7 DNA polymerase variant fused to a dual adenine-cytosine deaminase to install all possible transition mutations at similar frequencies. By relieving pressure from maintaining genome fidelity, we obtained mutation rates of 3.82 × 10−5 substitutions per base."
  - "We fused the adenosine deaminase TadA-8e to the amino terminus of wild-type T7 DNAP with linkers of varying lengths"
  - "The cytosine deaminase PmCDA1 fusion (v6.1) proved to be less effective for mutagenesis compared with TadA-8e (v5.3)."
  - "replaced TadA-8e with a recently engineered dual adenine-cytosine deaminase, TadDE, to create v9"
  - "achieving an error rate of 3.82 × 10−5 s.p.b.—160,000× higher than the determined genomic mutation rate in E. coli (2.39 ± 1.10 × 10−10 s.p.b.)"
  - "NGS-determined error rates were slightly higher, but comparable to fluctuation analysis error rates, at 7.21 × 10−5 s.p.b. and 5.66 × 10−5 s.p.b. for v8 and v9, respectively"
  - "Increasing A:T → G:C transitions by TadA-8e fusion (v8) complements this bias to achieve a balanced A:T → G:C to C:G → T:A transitions ratio of 1.00:0.97 … installing TadDE in v9 reduced adenosine deamination activity, reverting to a biased ratio of 1.00:1.61"
  - "Both v8 and v9 showed clear bias towards transition mutations (67.9–69.2%) over transversion mutations"
  - "The 2 variants showed a uniform distribution of mutations and base transitions throughout the entire 39-kb BAC phagemid"
  - "LySE evolved a 25-fold increase in tetA-encoded tigecycline resistance in 5 cycles"
- **File:** `agent_papers_txt/Ong_2026_hypermutagenic_phage_bacteria_continuous_discrete.txt`

---

## Badran & Liu 2015 — Development of potent in vivo mutagenesis plasmids with broad mutational spectra (MP6)
- **Journal:** Nature Communications **6**, 8425 (2015)
- **DOI:** 10.1038/ncomms9425
- **Retrieved:** 2026-08-27 — open access, direct PDF from nature.com; `pdftotext -layout`.
- **Cited in context of:** the global-mutagen comparator used in Moore 2018 / Mengiste 2023; an all-12-substitution-type spectrum.
- **Key verified quotes:**
  - "When induced, MP6 results in a 322,000‑fold [increase] … MP6 results in an average of 6.2 × 10−6 substitutions per bp per generation"
  - "mutations covering each of the 12 possible transitions and transversions in the rpoB gene are known to endow E. coli with resistance to high levels of rifampin"
  - "MP6 exhibited a wider spectrum still, with a more uniform distribution of transitions and transversions."
  - "XL1-Red results in 8 substitutions per genome per generation, while MP6 in the induced state produces an average of 29 substitutions per genome per generation"
- **File:** `agent_papers_txt/Badran_Liu_2015_MP6_mutagenesis_plasmids.txt`

---

## Ravikumar, Arzumanyan, Obadi, Javanpour & Liu (C.C.) 2018 — Scalable, Continuous Evolution of Genes at Mutation Rates above Genomic Error Thresholds (OrthoRep)
- **Journal:** Cell **175**, 1946–1957.e13 (2018)
- **DOI:** 10.1016/j.cell.2018.10.021  (PMID 30415839, PMC6343851)
- **Retrieved:** 2026-08-27 — cell.com OA link returned HTML; obtained via Sci-Hub mirror `sci-hub.ee` → `sci.bban.top`; `pdftotext -layout`.
- **Cited in context of:** error-prone orthogonal replication as a transversion-capable, non-deaminase alternative; rate ceiling.
- **Key verified quotes:**
  - "mutates user-defined genes at rates of 1 × 10−5 substitutions per base (s.p.b.) without increasing the genomic mutation rate (10−10 s.p.b.) at all. This 100,000-fold mutational acceleration enables the rapid, continuous evolution of genes entirely in vivo."
  - "we have a series of TP-DNAP1s spanning a mutation rate between 10−9 s.p.b. to 10−5 s.p.b."
  - "mutations that restore LEU2 from leu2 (Q180*) include T:A/A:T, T:A/C:G, T:A/G:C, G:C/T:A and G:C/C:G. This leaves the G:C/A:T mutation unrepresented. To measure the rate of this final mutation, we used strain AR-Y401 …" [i.e. the full 6-class spectrum is measured]
  - "TP-DNAP1s … engineered with custom mutational spectra (Table S8)"
- **File:** `agent_papers_txt/Ravikumar_2018_OrthoRep_scalable_continuous_evolution.txt`

---

## Kurt, Zhou, Iyer, Garcia, Miller, Langner, Grünewald & Joung 2021 — CRISPR C-to-G base editors for inducing targeted DNA transversions in human cells (CGBE1)
- **Journal:** Nature Biotechnology **39**, 41–46 (2021)  [online 2020-07-20]
- **DOI:** 10.1038/s41587-020-0609-x  (PMID 32690971, PMC7854778)
- **Retrieved:** 2026-08-27 — Unpaywall listed OA but with no usable PDF URL; obtained via Sci-Hub mirror `sci-hub.ee` → `sci.bban.top`; `pdftotext`.
- **Cited in context of:** removing UGI and *adding* UNG converts a cytidine-deaminase edit from a C→T transition into a C→G transversion; the mechanistic basis for breaking the transition ceiling.
- **Key verified quotes:**
  - "We hypothesized that the … deaminate the C at position 6 to a U with subsequent creation of an abasic site by cellular UNG (base excision …)"
  - "we found that the addition of two uracil glycosylase inhibitor [domains] … reduced efficiency of uracil excision"
  - "CGBE1 induced C-to-G editing with mean frequencies of 20% or higher at 14 of the 25 sites tested"
  - "Highly efficient C-to-G edits were observed for four of the 18 sites …, with mean editing frequencies ranging from 41.7 to 71.5% … with only very low levels of C-to-T or C-to-A byproducts observed"
  - "C-to-G editing was most efficient for Cs embedded in an AT-rich sequence context"
  - "mean indel frequencies of 10.4 and 8.5% for CGBE1 and miniCGBE1, respectively"
- **File:** `agent_papers_txt/Kurt_2021_CGBE_C_to_G_base_editors_transversions.txt`

---

## Tong, Li & Yang 2024 — Programmable G-to-Y base editing using engineered DNA glycosylase (gGBE)
- **Journal:** Life Medicine **3**(1), lnae005 (2024)
- **DOI:** 10.1093/lifemedi/lnae005  (PMID 39872398, PMC11749614)
- **Retrieved:** 2026-08-27 — open access; Europe PMC `fullTextXML` (the original AYBE paper, Tong et al. 2023 Nat Biotechnol 41:1080–1084, DOI 10.1038/s41587-022-01595-6, could NOT be obtained — not OA, no PMC record, absent from all Sci-Hub mirrors tried).
- **Cited in context of:** glycosylase base editors (CGBE / AYBE / gGBE) as the route to transversion outcomes from deaminase chemistry.
- **Key verified quotes:**
  - "the CGBE base editor, which enables C-to-G conversions in mammalian cells and C-to-A conversions in Escherichia coli, and the AYBE adenine transversion base editor, which allows A-to-C or A-to-T conversions, by fusing CBE or ABE with DNA glycosylases"
  - "In AYBE and CGBE, MPG and [UNG] …" [glycosylase excises the deaminated base to give an abasic site]
  - "a remarkable editing efficiency of up to 81.2% for guanine editing, primarily resulting in G-to-C and G-to-T conversions. G-to-Y edits (where Y = C or T) made up as much as 94% of the edits"
- **File:** `agent_papers_txt/Tong_2024_gGBE_GtoY_base_editing_glycosylase.txt`

---

## NOT OBTAINED (marked [UNVERIFIED] wherever referenced)
- **Mengiste, ... & Shoulders 2024 — MutaT7^GDE: A Single Chimera for the Targeted, Balanced, Efficient, and Processive Installation of All Possible Transition Mutations In Vivo.** ACS Synthetic Biology **13**, 2693–2701 (2024). DOI **10.1021/acssynbio.4c00316** (PMID 39190860). *Not* 10.1021/acssynbio.4c00218 (that DOI does not resolve). Paywalled: Unpaywall `is_oa: false`; no PMC record; absent from sci-hub.se/.st/.ru/.ee; no bioRxiv preprint found. **Only the publisher abstract was read** (via Europe PMC), quoted in the findings file and explicitly flagged.
- **Tong et al. 2023 — Programmable A-to-Y base editing (AYBE).** Nat Biotechnol 41, DOI 10.1038/s41587-022-01595-6 (PMID 36624150). Not OA, no PMC, absent from Sci-Hub mirrors. AYBE's spectrum is cited only *second-hand* from the verified Tong 2024 Life Medicine letter.

---

## Targeted in vivo hypermutation — the wider landscape & orthogonal RNAPs

_Systems across bacteria/yeast/mammalian cells, replicon-scoped alternatives, and multiplexing by orthogonal phage RNAPs._
_Added 2026-08-27 for [Note_012 open questions](../projects/diploid_ecoli/knowledge/note012_answers/). Findings: [`A6_landscape_findings.md`](../projects/diploid_ecoli/knowledge/note012_answers/A6_landscape_findings.md)._

---

# A6_landscape — new catalog entries (targeted in vivo hypermutation + orthogonal RNAPs)

Agent: A6_landscape. Retrieved 2026-08-27. Do not merge into INDEX.md/CATALOG.md until the swarm finishes.

---

## Moore, Papa III & Shoulders 2018 — A Processive Protein Chimera Introduces Mutations across Defined DNA Regions In Vivo
- **Authors:** Christopher L. Moore, Louis J. Papa III, Matthew D. Shoulders
- **Journal:** J. Am. Chem. Soc. 140:11560–11564 (2018)
- **DOI:** 10.1021/jacs.8b04001 (PMID 29991261; PMC6166643)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML (author manuscript) → text
- **Cited in context of:** the original MutaT7 (rApo1–T7RNAP); T7 terminator boundary; strand bias; dual opposing promoters
- **Key verified quotes:**
  - "we found that four copies of the T7 terminator fully constrained mutagenesis to the intended upstream KanR gene (Figure S6)"
  - "~90% C → T mutations and ~10% G → A mutations (Figure S9b and Table S6)" (episomal rpsL, StrepR clones)
  - "the average kanamycin resistance frequency for MutaT7 was 6.7 ×10−6 versus 5.7 × 10−5 for MP6"
  - "installing an additional antisense T7 promoter led to the accumulation of both G → A and C → T mutations throughout the target gene"
  - "we observed high levels of MutaT7-dependent tetracycline resistance only in reporter strains having the T7 promoter" (TetR is ~1.6 kb downstream of KanR)
  - "a more flexible alternative is to co-express MutaT7 with the uracil glycosylase inhibitor (UGI)"
- **File:** `agent_papers_txt/Moore_2018_MutaT7_processive_chimera.txt`

## Molina, Rix, Mengiste, … Shoulders 2022 — In vivo hypermutation and continuous evolution
- **Journal:** Nature Reviews Methods Primers 2:36 (2022)
- **DOI:** 10.1038/s43586-022-00130-w (PMC10108624)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** authoritative side-by-side of OrthoRep vs MutaT7 vs EvolvR; cargo-size limits; durability of targeting
- **Key verified quotes:**
  - "The amount of genetic cargo that can be placed on OrthoRep is up to >20 kb, although smaller cargo sizes up to ~7 kb are most tractable. MutaT7 systems may tolerate up to >25 kb based on the processivity of T7 RNAP, although only smaller cargo sizes up to ~2 kb have been tested."
  - "The error-prone polymerase of EvolvR and the deaminase of MutaT7 cause low but measurable off-target mutagenesis, currently a few-hundred-fold lower than on-target mutagenesis."
  - "the elements recruiting hypermutation machinery, such as the T7 promoter or gRNA target site, can themselves become mutated while still allowing the GOI to be replicated and expressed by host machinery. This may allow the system to reduce its own hypermutation rate over time."
  - "targeting only a region of a GOI for evolution … may be possible with MutaT7 by using dCas9 to terminate MutaT7's action in the middle of a GOI"
- **File:** `agent_papers_txt/Molina_2022_in_vivo_hypermutation_continuous_evolution_review.txt`

## Chen, Liu, Cheng, … Chen 2020 — Efficient, continuous mutagenesis in human cells using a pseudo-random DNA editor (TRACE)
- **Journal:** Nature Biotechnology 38:165–168 (2020)
- **DOI:** 10.1038/s41587-019-0331-8 (PMID 31844291; PMC7775643)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** MutaT7 logic in mammalian cells; the "use SP6 for multiplexing" idea
- **Key verified quotes:**
  - "The most efficient variant, pAID-T7-UGI, showed an average C>T mutation rate of 1.47 mutations per 1,000 bp (kb−1) and an average G>A mutation rate of 3.1 kb−1"
  - "TRACE generates nucleotide diversity within the human genome at average C>T and G>A mutation rates in a tunable range from ~0.5 kb−1 to 4 kb−1 within a week. The high editing rate and large editing window (at least 2,000 bp) …"
  - "The measured genomic C>T and G>A substitution rate was in the order of 10−6 bp−1 after 6 d … By contrast, TRACE induced on-target (T7 promoter driven) C>T and G>A mutation rates in the order of 10−3 bp−1"
  - "orthogonal bacteriophage polymerase systems (for example, SP6 RNAP) may permit differential editing on multiple loci"
  - "an elevation of the C>T mutation rate at base −5C in the pAID-T7-UGI condition, reaching on average approximately 0.5% of bases" (promoter self-mutation)
- **File:** `agent_papers_txt/Chen_2020_TRACE_pseudorandom_DNA_editor_human.txt`

## Cravens, Jamil, Kong, Sockolosky & Smolke 2021 — Polymerase-guided base editing enables in vivo mutagenesis and rapid protein engineering (TRIDENT)
- **Journal:** Nature Communications 12:1579 (2021)
- **DOI:** 10.1038/s41467-021-21876-z (PMC7952560)
- **Retrieved:** 2026-08-27, Nature OA PDF (Unpaywall) → pdftotext
- **Cited in context of:** the yeast MutaT7-family system; DNA-repair-factor recruitment to widen spectrum; transversions
- **Key verified quotes:**
  - "TRIDENT (TaRgeted In vivo Diversification ENabled by T7 RNAP) … at mutation rates one-million fold higher than natural genomic error rates"
  - "enabling sustained mutation of all four DNA nucleotides at rates greater than 10−4 mutations per bp"
  - "an overall targeted mutation rate of 10−3 s.p.b., 105–106-fold higher than genomic error rates"
  - "Mutation of the PT7 sequence was minimal, with no single base substitution frequency within PT7 >2 × 10−4, indicating that <0.1% of cells lose targeting activity during the 16 h of mutation induction"
  - "targeting of DNA-repair factors increased rates of A/T mutation by up to 5-fold and increased rates of G mutagenesis by at least 5-fold. However, the overall mutation spectrum remained biased as over 99% of induced mutations are C > T and G > A substitutions"
  - "TRIDENT is the only system able to make both A/T mutations and C/G mutations at similar rates across multiple-kb of DNA"
  - "our experimental design for TRIDENT-directed evolution experiments used a single T7 terminator; however, Moore et al. showed that four or more T7 terminators may be needed"
- **File:** `agent_papers_txt/Cravens_2021_polymerase_guided_base_editing_yeast.txt`

## Halperin, Tou, Wong, Modavi, Schaffer & Dueber 2018 — CRISPR-guided DNA polymerases enable diversification of all nucleotides in a tunable window (EvolvR)
- **Journal:** Nature 560:248–252 (2018)
- **DOI:** 10.1038/s41586-018-0384-8 (PMID 30069054)
- **Retrieved:** 2026-08-27, Sci-Hub (sci-hub.ru) → pdftotext. Not OA.
- **Cited in context of:** Cas-tethered (not RNAP-tethered) targeted mutagenesis; window size
- **Key verified quotes:**
  - "up to 7,770,000-fold greater than rates seen in wild-type cells, and editing windows with lengths of up to 350 nucleotides"
  - "the target plasmid accrued substitutions in an approximately 17-nucleotide window 3′ of the nick site … consistent with the established 15–20 nucleotide processivity of PolI"
  - "Expressing nCas9–PolI3M markedly increased the mutation rate at the targeted locus 24,500-fold over the wild type while increasing the global mutation rate 120-fold over the wild type"
- **File:** `agent_papers_txt/Halperin_2018_EvolvR_CRISPR_guided_DNA_polymerase.txt`

## Hess, Frésard, Han, … Bassik 2016 — Directed evolution using dCas9-targeted somatic hypermutation in mammalian cells (CRISPR-X)
- **Journal:** Nature Methods 13:1036–1042 (2016)
- **DOI:** 10.1038/nmeth.4038 (PMID 27798611; PMC5557288)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** dCas9-MS2-AID mammalian targeted SHM; window
- **Key verified quotes:**
  - "a median mutation frequency of 0.0104 was observed … This translates to a mutation rate of ~1/2000 bp−1, which is similar to that observed for somatic hypermutation"
  - "We aligned these mutations relative to the PAM and observed an increase in the size of the hotspot to span from −50 to +50 bp … the most highly mutated bases are located within the +12 to +32 region" (AID*Δ)
- **File:** `agent_papers_txt/Hess_2016_CRISPRX_dCas9_AID_mammalian.txt`

## Finney-Manchester & Maheshri 2013 — Harnessing mutagenic homologous recombination for targeted mutagenesis in vivo by TaGTEAM
- **Journal:** Nucleic Acids Research 41:e99 (2013)
- **DOI:** 10.1093/nar/gkt150 (PMC3643572)
- **Retrieved:** 2026-08-27, Europe PMC OA PDF → pdftotext
- **Cited in context of:** yeast, non-RNAP, non-Cas targeted mutagenesis over a 20 kb window
- **Key verified quotes:**
  - "By fusing … DNA glycosylase MAG1 to a tetR DNA-binding domain, we are able to elevate mutation rates >800 fold in a specific 20-kb region of the genome or on a plasmid that contains an array of tetO sites"
  - "TaGTEAM generates a broad spectrum of both transitions and transversions. Roughly a quarter of mutants were single-base deletions"
  - Table 1 spectrum column includes GC>TA 26.5%, TA>AT 18.4%, GC>CG 14.3%, Deletions 24.5% (Mag1-sctetR)
- **File:** `agent_papers_txt/FinneyManchester_2013_TaGTEAM_yeast.txt`

## Butt, Ramirez & Mahfouz 2022 — Synthetic evolution of herbicide resistance using a T7 RNAP-based random DNA base editor
- **Journal:** Life Science Alliance 5:e202201538 (2022)
- **DOI:** 10.26508/lsa.202201538 (PMC9526444)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** the MutaT7 family in plants (N. benthamiana transient + stable transgenic rice)
- **Key verified quote:** "we designed, built, and tested a chimeric fusion of T7 RNA Polymerase (RNAP) and deaminase … targeted the T7 promoter-driven acetolactate synthase sequence that had been stably integrated in the rice genome and generated C-to-T and G-to-A transitions"
- **File:** `agent_papers_txt/Butt_2022_T7RNAP_random_DNA_base_editor_plants.txt`

## Wang, Wu, Lv, … Liu 2025 — T7 RNA polymerase-guided base editor for accelerated continuous evolution in Bacillus subtilis (BS-MutaT7)
- **Journal:** Synthetic and Systems Biotechnology (2025)
- **DOI:** 10.1016/j.synbio.2025.04.010 (PMC12083895)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** MutaT7 in a Gram-positive host; the best published evidence for kb-scale processive windows
- **Key verified quotes:**
  - "The target mutation rates reached 1.2 × 10−5 per base per generation (s.p.b.) and 5.8 × 10−5 s.p.b., representing 7000-fold and 37,000-fold increases over the genomic mutation rate"
  - "Both exhibited high processivity, maintaining mutation rates of 5.8 × 10−6 s.p.b. and 2.9 × 10−5 s.p.b. within a 5 kb DNA region."
- **File:** `agent_papers_txt/Wang_2025_T7RNAP_base_editor_Bacillus_subtilis.txt`

## Ong, Ghode, Narenderan, … Fredens 2026 — Bridging continuous and discrete evolution through a controllable, hypermutagenic phage-bacteria system (LySE)
- **Journal:** Nature Microbiology 11:1585–1597 (2026)
- **DOI:** 10.1038/s41564-026-02346-y (Zotero key 2RADSJ4P)
- **Retrieved:** 2026-08-27, Zotero local PDF via `scripts/zotero_fetch.py fetch 2RADSJ4P` → pdftotext
- **Cited in context of:** deaminase fused to a phage *DNA* polymerase; 39 kb cargo; phage-cycle purging of off-target genomic mutations
- **Key verified quotes:**
  - "We developed a hypermutagenic T7 DNA polymerase variant fused to a dual adenine-cytosine deaminase to install all possible transition mutations at similar frequencies … we obtained mutation rates of 3.82 × 10−5 substitutions per base"
  - "3.82 × 10−5 substitutions per base—160,000× higher than the genomic mutation rate of the host E. coli"
  - "LySE enables selection of slow-manifesting metabolic functions by coupling large gene cluster expression to host fitness, with a capacity of up to 39 kilobases (kb)"
  - "T7 phage-mediated cell lysis completely eliminates the E. coli culture after each selection cycle, effectively removing all off-target mutations"
  - "replaced TadA-8e with a recently engineered dual adenine-cytosine deaminase, TadDE"
  - "relevant plasmids are available from Addgene"
- **File:** `agent_papers_txt/Ong_2026_hypermutagenic_phage_bacteria_system.txt`

## Meyer, Ellefson & Ellington 2015 — Directed Evolution of a Panel of Orthogonal T7 RNA Polymerase Variants for in Vivo or in Vitro Synthetic Circuitry
- **Journal:** ACS Synthetic Biology 4:1070–1076 (2015; ePub 2014)
- **DOI:** 10.1021/sb500299c (PMID 25279711)
- **Retrieved:** 2026-08-27, Sci-Hub (sci-hub.ru) → pdftotext. Not OA.
- **Cited in context of:** the "hexacore" orthogonal T7 RNAP:promoter set; crosstalk numbers; multi-polymerase toxicity
- **Key verified quotes (Table 1, promoter sequences and cognate activity vs WT=100):**
  - WT PT7 `TAATACGACTCACTATA` 100.0
  - CGG-R12-KIRV, PCGG `TAATACCGGTCACTATA` 50.5
  - CTGA-R13-AKSRV, PCTGA `TAATACCTGACACTATA` 42.9
  - T3-R5-RRVH, PT3 `TAATAACCCTCACTATA` 160.3
  - K1F-R5-KIKR, PK1F `TAATAACTATCACTATA` 76.2
  - N4-R5-YRNRV, PN4 `TAATAACCCACACTATA` 25.5
  - "Each polymerase showed at least a 3.8-fold selectivity for its cognate promoter over any other promoter … T3-R5-RRVH was quite cross reactive with PT7, showing only a 6.7-fold preference for PT3, while K1F-R5-KIKR prefers PK1F by only 3.8-fold over PT7 and 7.3-fold over PT3."
  - Most-specific panel: "This new panel of polymerases proved to be truly orthogonal, as no polymerase showed more than 2.5% cross-reactivity in vivo (Figure 2a−c)." Members: CGG-R12-KIR 31% activity, ≥34.3-fold; CTGA-R13-AKSIRV 27%, 33.8-fold; T3-R5-RV 39.3%, 46-fold; K1F-R5-IRH 18.5%, ≥9.5-fold; N4-R5-RNRV 14.7%, 9.8-fold.
  - "The high activity of T7 RNA polymerase and its derivatives can potentially lead to toxicity, especially if multiple polymerases are expressed in the same cell."
- **File:** `agent_papers_txt/Meyer_2015_orthogonal_T7RNAP_variant_panel.txt`

## Temme, Hill, Segall-Shapiro, Moser & Voigt 2012 — Modular control of multiple pathways using engineered orthogonal T7 polymerases
- **Journal:** Nucleic Acids Research 40:8773–8781 (2012)
- **DOI:** 10.1093/nar/gks597 (PMID 22743271; PMC3458549)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** the first part-mined orthogonal T7-scaffold RNAP set (T7*, T3, K1F, N4); T7 promoter modularity
- **Key verified quotes:**
  - "This set is highly orthogonal and induces cognate promoters by 8- to 75-fold more than off-target promoters."
  - "Four RNAPs exhibited strong activity (42-, 12-, 17- and 40-fold induction by T7*, T7*(T3), T7*(K1F) and T7*(N4), respectively)"
  - "a spontaneous mutation in the polymerase active site (R632S) arose. This mutation was found to significantly reduce host toxicity while maintaining activity"
  - "The T7 promoter has been shown to be modular, consisting of a 6 bp RNAP-binding region and a 5 bp strength-determining region … We created a promoter library by randomizing the wild-type T7 promoter from −2 bp to +3 bp … Orthogonality is retained for the hybrid promoters"
- **File:** `agent_papers_txt/Temme_2012_orthogonal_T7_polymerases_modular_control.txt`

## Zhu, Liu, Lou, Chen & Liu 2025 — Decoding and reengineering the promoter specificity of T7-like RNA polymerases based on phage genome mining and sequence covariation analysis
- **Journal:** Nucleic Acids Research 53:gkaf140 (2025)
- **DOI:** 10.1093/nar/gkaf140 (PMC11880802)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** the current best orthogonal T7 RNAP:promoter set; head-to-head crosstalk vs Temme 2012 and Meyer 2015
- **Key verified quotes:**
  - "we designed a set of orthogonal T7 RNAP–promoter variants that showed more stringent orthogonality than previously reported sets"
  - "these four pairs were highly orthogonal, with the transcription activity of cognate pairs > 200-fold higher than that of non-cognate pairs"
  - Table 2 ("Orthogonality is defined as the smallest ratio among the activity values of the four cognate pairs divided by the maximum activity of their corresponding RNAP variants with non-cognate promoters"): Domain grafting [Temme 2012] = **8**; CPR [Meyer 2015] = **34**; DCA (this work) = **245**
  - Table 2 promoter positions 6–10 (rest is WT T7 promoter): domain grafting CGACT / ACCCT / ACTAT / ACCCA; CPR CGACT / CCGGT / CCTGA / ACCCA; DCA TAACT / GTCAT / GGGCC / ACCCA with RNAP variants WT, 748K+756H, 748K+756N+758K, 748D+758A
  - "their absolute transcription activities are only ∼1/10 that of the wild-type T7 RNAP–promoter pair"
  - "the combinations of amino acid residue types at only three key positions and the base types at only five key positions dominantly encode the interaction specificities between most T7-like RNAPs and their cognate promoters"
  - "the K1E-like and SP6-like RNAPs may deviate substantially from the other T7-homologous RNAP family members in their promoter specificity determination rules"
- **File:** `agent_papers_txt/Zhu_2025_promoter_specificity_T7like_RNAPs_orthogonal.txt`

## Segall-Shapiro, Meyer, Ellington, Sontag & Voigt 2014 — A 'resource allocator' for transcription based on a highly fragmented T7 RNA polymerase
- **Journal:** Molecular Systems Biology 10:742 (2014)
- **DOI:** 10.15252/msb.20145299 (PMC4299498)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** splitting T7 RNAP into core + σ fragment; capping total active polymerase to control toxicity
- **Key verified quote:** "T7 RNAP (883 amino acids) can be divided into four fragments that have to be co-expressed to function. The DNA-binding loop is encoded in a C-terminal 285-aa 'σ fragment', and fragments with different specificity can direct the remaining 601-aa 'core fragment' to different promoters."
- **File:** `agent_papers_txt/SegallShapiro_2014_fragmented_T7RNAP_resource_allocator.txt`

## Ellefson, Meyer, Hughes, Cannon, Ellington 2014 — Directed evolution of genetic parts and circuits by compartmentalized partnered replication
- **Journal:** Nature Biotechnology 32:97–101 (2014)
- **DOI:** 10.1038/nbt.2714
- **Retrieved:** 2026-08-27, Sci-Hub (sci-hub.ru) → pdftotext. Not OA.
- **Cited in context of:** the CPR selection that produced the CGG-promoter T7 RNAP and, later, the Meyer 2015 hexacore set
- **File:** `agent_papers_txt/Ellefson_2014_compartmentalized_partnered_replication.txt`

## Costello & Badran 2021 — Synthetic Biological Circuits within an Orthogonal Central Dogma
- **Journal:** Trends in Biotechnology 39:59–71 (2021)
- **DOI:** 10.1016/j.tibtech.2020.05.013 (PMC7746572)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** review framing of orthogonal transcription/translation layers
- **File:** `agent_papers_txt/Costello_Badran_2021_orthogonal_central_dogma_review.txt`

## Crook, Abatemarco, Sun, Wagner, Schmitz & Alper 2016 — In vivo continuous evolution of genes and pathways in yeast (ICE)
- **Journal:** Nature Communications 7:13051 (2016)
- **DOI:** 10.1038/ncomms13051 (PMC5071640)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** yeast Ty1-retrotransposon-based in vivo continuous evolution (the "ICE" variant asked about)
- **Key verified quote:** "we synthetically optimize the retrotransposon Ty1 to enable in vivo generation of mutant libraries up to 1.6 × 10^7 l−1 per round, which is the highest of any in vivo mutational generation approach in yeast"
- **File:** `agent_papers_txt/Crook_2016_ICE_in_vivo_continuous_evolution_yeast.txt`

## Chen, Chen, Peng, … 2025 — CRISPR-DNA Polymerase Assisted Targeted Mutagenesis for Regulable Laboratory Evolution (CTRLE)
- **Journal:** Advanced Science (2025)
- **DOI:** 10.1002/advs.202511448 (PMC12677585)
- **Retrieved:** 2026-08-27, NCBI eutils PMC full-text XML
- **Cited in context of:** EvolvR successor with a 2 kb window and all substitution types
- **Key verified quote:** "by integrating mutagenic, high-processivity bacteriophage T5 or T7 DNA polymerases (DNAPs) with CRISPR-Cas9, the study develops an in vivo mutagenesis system that enables all possible types of nucleotide substitutions and an expanded mutation window of up to 2 kilobases, achieving a maximum mutation rate 1.1 × 10^6-fold higher than wild-type Escherichia coli"
- **File:** `agent_papers_txt/Chen_2025_CRISPR_DNAPol_targeted_mutagenesis.txt`

---

## NOT OBTAINED (do not cite beyond the abstract)
- **Mengiste, McDonald, Nguyen Tran, Plank, Wilson, Butty & Shoulders 2024 — MutaT7^GDE**, ACS Synth. Biol. 13:2693–2701, DOI 10.1021/acssynbio.4c00316 (PMID 39190860).
  Not open access; no PMC deposit; Sci-Hub mirrors (se/st/ru/ee/wf/wellesu) all returned no PDF for this DOI on 2026-08-27.
  **Abstract text was retrieved verbatim from Europe PMC** and is the only verified source. Everything beyond the abstract is `[UNVERIFIED]`.

## Already in repo, re-read for this survey (no new file)
- `agent_papers_txt/Alvarez_2020_T7DIVA_dCas9_bounded_deaminase_T7RNAP.txt` (Nat Commun 11:6436, DOI 10.1038/s41467-020-20230-z)
- `agent_papers_txt/Park_Kim_2021_eMutaT7_gene_specific_mutagenesis.txt` (NAR 49:e32, DOI 10.1093/nar/gkaa1231)
- `agent_papers_txt/Mengiste_2023_expanded_MutaT7_toolkit_all_transitions.txt` (NAR 51:e31, DOI 10.1093/nar/gkad003)
- `agent_papers_txt/Seo_2023_eMutaT7transition_dual_mutator.txt` (NAR 51:e59, DOI 10.1093/nar/gkad266)
- `agent_papers_txt/Shao_2025_orthogonal_transcription_mutation_system.txt` (Nat Commun 16, DOI 10.1038/s41467-025-61354-4)
- `papers_txt/hypermutation_systems/An_orthogonal_T7_replisome_for.txt` = **T7-ORACLE**, Diercks et al., Science 389:618 (7 Aug 2025)
- `papers_txt/maimonide/Scalable_Continuous_Evolution_of_Genes.txt` = OrthoRep, Ravikumar et al., Cell 175 (2018), DOI 10.1016/j.cell.2018.10.021
- `papers_txt/maimonide/Rapid_generation_of_potent_antibodies.txt` = AHEAD, Wellner et al., Nat Chem Biol (2021), DOI 10.1038/s41589-021-00832-4
- `papers_txt/directed_evolution/A_system_for_the_continuous.txt` = PACE, Esvelt, Carlson & Liu, Nature 472:499 (2011), DOI 10.1038/nature09929
- `papers_txt/maimonide/Development_of_potent_in_vivo.txt` = MP6, Badran & Liu, Nat Commun 6:8425 (2015), DOI 10.1038/ncomms9425
- `papers_txt/hypermutation_systems/Orthogonal_replication_with_optogenetic_selection.txt` = OptoRep, Wegner et al. (OrthoRep + optogenetic selection)

---

## BAC/F′ cloning at 30 kb & curable oriT vectors

_Defined-window large-fragment cloning, electroporation size curves, and conditionally-replicating mobilisable backbones._
_Added 2026-08-27 for [Note_012 open questions](../projects/diploid_ecoli/knowledge/note012_answers/). Findings: [`A7_bac_vectors_findings.md`](../projects/diploid_ecoli/knowledge/note012_answers/A7_bac_vectors_findings.md)._

---

# Staging catalog — A7_bac_vectors (BAC/F' cloning of a 30 kb tile; curable oriT vectors)
Retrieved 2026-08-27. PDFs in `agent_papers/`, text in `agent_papers_txt/`.

## Sheng, Mancino & Birren 1995 — Transformation of Escherichia coli with large DNA molecules by electroporation
Authors: YuLing Sheng, Valeria Mancino, Bruce Birren
Journal: Nucleic Acids Research 23(11):1990–1996
DOI: 10.1093/nar/23.11.1990 (PMC306974)
Retrieved: 2026-08-27, Europe PMC OA render
Cited in context of: electroporation efficiency vs insert size; host-strain dependence; recommended pulse conditions for >50 kb DNA.
Key verified quotes:
- Table 2 (efficiency, colonies/µg, 25 µF, 200 Ω, 17 kV/cm): "7.3 → 2.3 x 10^9; 80 → 1.9 x 10^8; 150 → 3.2 x 10^7; 240 → 1.2 x 10^6".
- "Molecules of 240 kb transform ~30-fold less well, on a molar basis, than molecules of 80 kb."
- Table 1 (colonies, same DNA sample): 7.3 kb — DH10B 1740, HB101 330, DH5α 1390, XL-1 Blue MR 1370, JS4 1350; 240 kb — DH10B 1220, HB101 6, DH5α 302, XL-1 Blue MR 42, JS4 50.
- "Among all the E.coli strains tested, the strain best transformed by large DNA is DH10B."
- "The conditions we now employ for transformation of molecules >50 kb are: 9 or 12.5 kV/cm, 100 Ω, 25 µF."
- "electroporation introduces bias towards recovery of clones originating from the smallest molecules in the mixture."
- "it is important that large insert libraries be maintained as frozen bacteria and not as DNA stocks."
File: `agent_papers_txt/Sheng_1995_transformation_large_DNA_electroporation.txt`

## Lauritsen et al. 2017 — A versatile one-step CRISPR-Cas9 based approach to plasmid-curing (pFREE)
Authors: Ida Lauritsen, Andreas Porse, Morten O. A. Sommer, Morten H. H. Nørholm
Journal: Microbial Cell Factories 16:135
DOI: 10.1186/s12934-017-0748-z (PMC5540278)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: active CRISPR-based plasmid curing; efficiency numbers; replicon coverage.
Key verified quotes:
- "we obtained curing efficiencies between 40 and 100% for the plasmids most widely used for expression and cloning purposes"
- "after 24 h the vast majority of all three populations were cured with 80–90% of the plated cells being plasmid-free"
- "ColE1-like, p15A and pSC101 replicons accounted for 91% of the plasmids in the Addgene database"
- One-step multi-plasmid curing: "From the tested cells, 80% were completely cured whereas 10% or less contained one or more plasmids and all cells had lost pFREE"
- Self-curing: "90% of the cells were cured of pFREE after 7 h of induction ... After 10 h of pFREE induction, all cells were cured for pFREE"
Addgene: pFREE #92050, pFREE_Amp #92051, pFREE_Cm #92052, pFREE_Zeo #92053 (depositor Morten Nørholm) — verified on addgene.org 2026-08-27.
File: `agent_papers_txt/Lauritsen_2017_pFREE_CRISPR_plasmid_curing.txt`

## Gibson et al. 2008 — One-step assembly in yeast of 25 overlapping DNA fragments to form a complete synthetic Mycoplasma genitalium genome
Authors: D. G. Gibson, G. A. Benders, K. C. Axelrod, J. Zaveri, M. A. Algire, M. Moodie, M. G. Montague, J. C. Venter, H. O. Smith, C. A. Hutchison III
Journal: PNAS 105(51):20404–20409
DOI: 10.1073/pnas.0811011106 (PMC2600582)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: what in vitro / E. coli assembly can and cannot reach; the tiered 6 kb → 24 kb → 72 kb → 145 kb → 592 kb strategy; yeast as the high-ceiling alternative.
Key verified quotes:
- "In the first stage, overlapping ~6-kb DNA cassettes were joined four at a time to form 25 ~24-kb A-series assemblies. Three A-series assemblies were then joined to make 1/8 genome ~72-kb B-series assemblies, and then two B-series assemblies were assembled to make each of the ~145-kb quarter-genome C-series assemblies. We accomplished the final assembly in yeast..."
- "Our 25 A-series assemblies comprising the entire M. genitalium genome were all synthesized and cloned as bacterial artificial chromosomes (BACs) in Escherichia coli"
File: `agent_papers_txt/Gibson_2008_one_step_assembly_yeast_25_fragments.txt`

## Lee, Larionov & Kouprina 2015 — Highly efficient CRISPR/Cas9-mediated TAR cloning of genes and chromosomal loci from complex genomes in yeast
Authors: Nicholas C. O. Lee, Vladimir Larionov, Natalay Kouprina
Journal: Nucleic Acids Research 43(8):e55
DOI: 10.1093/nar/gkv112 (PMC4417148)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: TAR cloning as the high-size-ceiling alternative; baseline vs Cas9-boosted efficiency; YAC→BAC retrofitting.
Key verified quotes:
- "TAR ... allowing the selective isolation of full-length genes ... and entire genomic loci with sizes up to 250 kb from complex genomes in yeast S. cerevisiae"
- "TAR cloning produces YAC clones containing the desired insert at a frequency of 0.5–2% of all clones screened."
- "Twelve NBS1 gene positive colonies were identified among 570 His+ transformants when untreated genomic DNA was used ... (~2%)... the analysis of 100 His+ transformants obtained with the Cas9-treated human genomic DNA, yielded 32 colonies positive for the NBS1 sequence (32%)."
- "In our attempts to clone genes larger than 40 kb from the human and other mammalian genomes, we found it practically impossible to choose suitable restriction enzymes..."
- Retrofit: "YAC/BACs were moved to Escherichia coli by electroporation ... into DH10B bacterial competent cells"
File: `agent_papers_txt/Lee_2015_CRISPR_Cas9_TAR_cloning_yeast.txt`

## Pryor et al. 2020 — Enabling one-pot Golden Gate assemblies of unprecedented complexity using data-optimized assembly design
Authors: J. M. Pryor, V. Potapov, R. J. Kucera, K. Wolf, E. J. Cantor, G. J. S. Lohman
Journal: PLoS ONE 15(9):e0238592
DOI: 10.1371/journal.pone.0238592
Retrieved: 2026-08-27, PLOS OA
Cited in context of: real ceiling of one-pot Golden Gate (fragment count and fidelity, not total kb).
Key verified quotes:
- "we designed a 35-fragment version of the lac operon cassette test system with a predicted assembly fidelity of 65% ... on average 71% of the observed transformants harbored accurately assembled constructs"
- 13-fragment SapI system: "On average, 91% of the observed transformants harbored correctly assembled products."
- "Using the traditional overhang design standards, we could identify high-fidelity overhang sets containing approximately 10–12 overhang pairs."
Note: the test constructs are small (lac operon cassette); no ~30 kb one-pot Golden Gate is demonstrated.
File: `agent_papers_txt/Pryor_2020_GoldenGate_data_optimized_assembly.txt`

## Eichenlaub 1979 — Mutants of the mini-F plasmid pML31 thermosensitive in replication
Authors: Rudolf Eichenlaub
Journal: Journal of Bacteriology 138(2):559–566
DOI: 10.1128/jb.138.2.559-566.1979 (PMC218213)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: does a temperature-sensitive mini-F (i.e. BAC-family) replicon exist? Yes, as classical mutants.
Key verified quotes:
- "Hydroxylamine mutagenesis was used for the induction of thermosensitive replication mutants of the mini-F plasmid pML31."
- "Mutants of type I are fast segregating with the kinetics expected if plasmid replication was blocked immediately. Double-label experiments showed a rapid shut-off of replication in these mutants at 42°C."
- "The mini-F plasmid pML31 is a hybrid plasmid consisting of the EcoRI-generated, 9-kilobase (kb) fragment V of the F factor and a nonreplicating EcoRI fragment of pSC105 (6.75 kb) carrying kanamycin resistance"
File: `agent_papers_txt/Eichenlaub_1979_miniF_pML31_thermosensitive_replication.txt`

## Hashimoto-Gotoh & Sekiguchi 1977 — Mutations to temperature sensitivity in R plasmid pSC101
Journal: Journal of Bacteriology 131(2):405–412
DOI: 10.1128/jb.131.2.405-412.1977 (PMC235445)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: origin of the repA101ts / pSC101ts replicon used in pKD46, pSIM, pFREE-adjacent tooling.
Key verified quote: "Temperature-sensitive (Ts) mutant plasmids isolated from tetracycline resistance plasmid pSC101 ..." (classes of Ts replication/Tc mutants defined; type I loses replication at 42°C).
File: `agent_papers_txt/HashimotoGotoh_1977_pSC101_temperature_sensitivity_mutations.txt`

## Li, Thomason, Sawitzke, Costantino & Court 2013 — Positive and negative selection using the tetA-sacB cassette
Journal: Nucleic Acids Research 41(22):e204
DOI: 10.1093/nar/gkt1075 (PMC3905872)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: counter-selection markers (sacB / tetA) and their escape frequencies.
Key verified quotes:
- "tetA confers sensitivity to the lipophillic chelator fusaric acid; sacB causes sensitivity to sucrose ... coexpression of tetA-sacB is orders of magnitude more sensitive as a counter-selection agent than either gene alone"
- "A low frequency of Tet/SacB resistant colonies (1 x 10^2 /10^8 viable cells)" (i.e. background escape ~1 x 10^-6)
File: `agent_papers_txt/Li_2013_tetA_sacB_positive_negative_selection.txt`

## Wang, Zheng & Lu 2021 — Recent Advances in Strategies for the Cloning of Natural Product Biosynthetic Gene Clusters
Journal: Frontiers in Bioengineering and Biotechnology 9:692797
DOI: 10.3389/fbioe.2021.692797 (PMC8314000)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: survey of high-capacity vectors and their size ceilings; pESAC/oriT vectors; sacB/URA3 counter-screens in PAC/BAC vectors.
Key verified quotes:
- "artificial chromosomal vectors, including YAC, PAC, BAC, and FAC, which harbor the carrying capacity of 100~350 kb"
- "Typically, a cosmid or fosmid vector can only accept relatively small BGCs (up to 45 kb)"
- "Using PAC vector pESAC13 (a derivative of pESAC) harboring an oriT site, which allows for conjugal transfer instead of time-consuming protoplast transformation, a genomic library of Streptomyces tsukubaensis was generated"
- "normally, only 10–50% of the clones carry DNA inserts, depending upon the batch of the vector and insert DNA used"
File: `agent_papers_txt/Wang_2021_strategies_cloning_BGC_review.txt`

## Wild, Hradecna & Szybalski 2002 — Conditionally amplifiable BACs: switching from single-copy to high-copy vectors and genomic clones
Journal: Genome Research 12(9):1434–1444
DOI: 10.1101/gr.130502 (PMC186656)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: single-copy stability vs inducible copy number (pBAC/oriV = the CopyControl / pCC1BAC principle used by CATCH).
Key verified quotes:
- "a novel class of single-copy/high-copy (SC/HC) pBAC/oriV vectors that retain all the advantages of low-copy BAC vectors, but are endowed with a conditional and tightly controlled oriV/TrfA amplification system that allows: (1) a yield of ~100 copies of the vector per host cell when conditionally induced with L-arabinose, and (2) analogous DNA amplification ... of pBAC/oriV clones carrying >100-kb inserts"
File: `agent_papers_txt/Wild_2002_conditionally_amplifiable_BACs.txt`

## Haldimann & Wanner 2001 — Conditional-replication, integration, excision, and retrieval plasmid-host systems (CRIM)
Journal: Journal of Bacteriology 183(21):6384–6393
DOI: 10.1128/jb.183.21.6384-6393.2001 (PMC100134)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: R6Kgamma / pir-dependent conditional origins as a curable-replicon strategy.
Key verified quotes:
- "These CRIM plasmids have the gamma replication origin of R6K, which requires the trans-acting Pi protein (encoded by pir) for replication"
- copy number "(250 per cell) ... in pir+ or pir-116 (high-copy) hosts"; ordinary (pir-negative) hosts are "nonpermissive for CRIM plasmid replication"
File: `agent_papers_txt/Haldimann_Wanner_2001_CRIM_plasmids.txt`

## Fu, Tsai, Luo & Deonier 1991 — Deletion analysis of the F plasmid oriT locus
Journal: Journal of Bacteriology 173(3):1012–1020
DOI: 10.1128/jb.173.3.1012-1020.1991 (PMC207219)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: oriT-only (mob+ tra-) mobilisation with an F helper in trans; minimal oriT size.
Key verified quotes:
- "DNA sequences required for nicking or transfer were revealed by cloning deleted segments of oriT into otherwise nonmobilizable pUC8 vectors and testing for their ability to promote transfer or to be nicked when tra operon functions were provided in trans."
- "Donor strains were RD5042 carrying individual small plasmids having oriT ... RD5042 is RD17 ... carrying F42. The F42 plasmid (classical F' lac) supplied the F tra functions."
- "Earlier deletion analyses had indicated that oriT is confined to a 375-bp BglII-HaeII fragment"; "the loci all contain an 80-bp region that is 80% A+T"
- oriT maps to "kb 66.7 on the F map"
File: `agent_papers_txt/Fu_1991_F_plasmid_oriT_deletion_analysis.txt`

## Frost, Ippen-Ihler & Skurray 1994 — Analysis of the sequence and gene products of the transfer region of the F sex factor
Journal: Microbiological Reviews 58(2):162–210
DOI: 10.1128/mr.58.2.162-210.1994 (PMC372961)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: how much of F is tra; whether inserting a tile elsewhere on F' disturbs transfer.
Key verified quote: "within the 33.3-kb transfer region of this 100-kb IncFI plasmid" (F = 100 kb; tra region = 33.3 kb; oriT at the start of the tra region, "more than 20 tra genes").
File: `agent_papers_txt/Frost_1994_F_transfer_region_sequence_gene_products.txt`

## Jones et al. 2013 — Phage P1-derived artificial chromosomes facilitate heterologous expression of the FK506 gene cluster
Journal: PLoS ONE 8(7):e69319
DOI: 10.1371/journal.pone.0069319 (PMC3708917)
Retrieved: 2026-08-27, PLOS OA
Cited in context of: a real, off-the-shelf single-copy large-insert vector that carries an oriT (pESAC13).
Key verified quotes:
- "pESAC13 contains the phage P1 origin of replication, as well as the phage phiC31 integration system"
- "an oriT site that allows transfer into Streptomyces by conjugation, rather than by time-consuming protoplast transformation"
- "The entire 83.5 kb FK506 gene cluster from Streptomyces tsukubaensis NRRL 18488 present in one 130 kb PAC clone was introduced into four different S. coelicolor..."
File: `agent_papers_txt/Jones_2013_pESAC13_PAC_FK506_conjugation.txt`

## Ferrières et al. 2010 — Silent mischief: bacteriophage Mu insertions contaminate products of E. coli random mutagenesis performed using suicidal transposon delivery plasmids mobilized by broad-host-range RP4 conjugative machinery
Journal: Journal of Bacteriology 192(24):6418–6427
DOI: 10.1128/JB.00621-10 (PMC3008518)
Retrieved: 2026-08-27, Europe PMC OA
Cited in context of: caution on RP4-mobilising donor strains (S17-1, SM10 lambda-pir) carrying cryptic Mu prophage.
File: `agent_papers_txt/Ferrieres_2010_Mu_contamination_RP4_suicide_vectors.txt`

---

## Fischer et al. 2025 — Rapid discovery of monoclonal antibodies by microfluidics-enabled FACS of single pathogen-specific antibody-secreting cells
- **Authors:** Katrin Fischer, Aleksei Lulla, Tsz Y. So, Pehuén Pereyra-Gerber, Matthew I. J. Raybould, Timo N. Kohler, Juan Carlos Yam-Puc, Tomasz S. Kaminski, Robert Hughes, Gwendolyn L. Pyeatt, Florian Leiss-Maier, Paul Brear, Nicholas J. Matheson, Charlotte M. Deane, Marko Hyvönen, James E. D. Thaventhiran, Florian Hollfelder (Cambridge Biochemistry / MRC Toxicology / Oxford Stats)
- **Year:** 2025 (published online 2024-08-14; issue 2025)
- **Journal:** Nature Biotechnology 43:960–970
- **DOI:** 10.1038/s41587-024-02346-5 — PMID 39143416, PMC12167710
- **Retrieved:** 2026-08-29, Europe PMC open access (full-text XML → text extract; rendered PDF)
- **Cited in context of:** single-cell screening of *secreted* antibody phenotype; ASC/plasmablast compartment as an antibody source; hydrogel compartmentalisation as an alternative to droplet microfluidic sorting — relevant to synthetic germinal center selection-cycle design.
- **Key content verified (direct quotes / figures):**
  - Core method: single B cells encapsulated by droplet microfluidics into **benzylguanine(BG)-modified low-melting-point agarose** (25 µm monodisperse beads, ~10⁷ cells/h), demulsified, then functionalised with **anti-light-chain VHH–SNAP-tag fusions** which covalently bind the BG sites — creating a per-cell antibody capture matrix. Secreted IgG stays tethered next to the cell it came from, so genotype–phenotype linkage survives washing.
  - Read-out is **conventional FACS**, not a bespoke droplet sorter: ">10⁷ hydrogel beads per h", multicolour, index sorting. "commercial FACS instruments achieve sorting rates more than ten times higher than droplet microfluidic sorters previously used for antibody discovery (200–600 Hz)".
  - Capture capacity: BG-agarose bead saturates between 1.3 and 2.7 × 10⁹ GFP-SNAP molecules/bead vs. ASC secretion of 10³–10⁵ antibodies/s — matrix never saturates. Contrast with cell-surface capture: ~5 × 10⁵ CD45 molecules per peripheral blood B cell.
  - Anti-κ VHH KD = 0.0167 nM (mouse), anti-human λ VHH KD = 1.35 nM; avidity from bivalent light-chain capture drops k_off so captured antibody does not leak out.
  - Secretion window: 30 min – 1 h 45 min (1 h 45 used for sorts); 92% viability in hydrogel at 4 h.
  - Mouse (RBD-immunised, bone marrow CD138+): 54 paired H/L sequences, 21 HV–LV pairs, 20 VH clonotypes; heavy clonality (IGHV9-1 clone = 37% of all). 26 expressed → 22 (84.6%) bound RBD, but only **2 neutralised** (mRBD1 IC50 3.17 µg/ml, mRBD2 4.61 µg/ml) — "selection of an antibody in an immune response does not guarantee neutralizing capacity." Co-crystal of mRBD2 Fab + RBD (PDB **8BE1**) shows binding to the disulfide-bonded 474–489 loop, overlapping the ACE2 interface.
  - Human (BNT162b2 dose 2, day 7–9 PBMC plasmablasts, one donor): 185 paired sequences, 156 distinct VH, 111 VH clonotypes. 16 expressed → 15/16 (94%) bound RBD (low pM–nM); 12/15 neutralised WT SARS-CoV-2; 10 with IC50 ≈ 10–100 ng/ml, comparable to REGEN-COV. 5 also neutralised Omicron BA.1; hRBD16 IC50 68 ng/ml (WT) vs 398 ng/ml (BA.1).
  - Key control: without VHH capture reagent, **no RBD+ plasmablast population appears** — these cells could not have been found by surface-Ig FACS. Up to 80% of plasmablasts have lost surface Ig.
  - Efficiency claim: >85% true-positive rate overall (95% for plasmablast-derived) vs. 20.3% (42/206) for unbiased post-BNT162b2 plasmablast sorting.
  - Multiplexed counter-selection demo: sorted S1⁺/RBD⁻ ASCs by two-colour tetramer staining + index sorting; 3 of 4 expressed bound S1 at pM, one (hS1-1) neutralised WT at 102.9 ng/ml, none bound RBD by ELISA.
  - Stated limits: encapsulation throughput (10⁷ cells/h) and low sequencing yield (Sanger); planned fix is NGS / LIBRA-seq 10X barcoded-antigen integration.
  - Chip design is open: channel layout `.dxf` at https://openwetware.org/wiki/DropBase; PDMS soft lithography, 1% RAN surfactant in HFE-7500.
- **File:** `Fischer_2025_microfluidic_FACS_single_ASC_mAb_discovery.txt` (PDF: `../agent_papers/Fischer_2025_microfluidic_FACS_single_ASC_mAb_discovery.pdf`)

---

## Stadlbauer, Amanat, … Krammer 2020 — SARS-CoV-2 Seroconversion in Humans: A Detailed Protocol for a Serological Assay, Antigen Production, and Test Setup
- **Authors:** Daniel Stadlbauer, Fatima Amanat, Veronika Chromikova, Kaijun Jiang, Shirin Strohmeier, … Viviana Simon, Florian Krammer (Icahn School of Medicine at Mount Sinai)
- **Year:** 2020
- **Journal:** Current Protocols in Microbiology 57:e100
- **DOI:** 10.1002/cpmc.100 — PMID 32302069, PMC7235504
- **Retrieved:** 2026-08-29, Europe PMC open access (full-text XML → text; rendered PDF)
- **Cited in context of:** the standard, non-refolding route to SARS-CoV-2 RBD — mammalian secreted expression + single-step IMAC; contrast with the E. coli inclusion-body/refold route used by [Fischer 2025](#).
- **Key content verified (direct quotes):**
  - Construct: pCAGGS encoding **soluble RBD with a C-terminal hexa-histidine tag**, signal peptide for secretion (BEI Resources NR-52309).
  - Host: **Expi293F**, transient transfection with ExpiFectamine 293; protein harvested from culture **supernatant** (no lysis, no inclusion bodies, no refolding).
  - Yield: "Expression levels of the RBD are very high in our hands (>20 mg/L culture), while expression levels for the full-length spike are lower (approximately 4 to 5 mg/L)."
  - Purification is one gravity-flow Ni-NTA step: 6 ml resin per 200 ml culture, 2 h batch binding at RT, 4× column-volume washes (20 mM imidazole), elution at 235 mM imidazole, then buffer exchange to PBS on a 10-kDa Amicon. **No SEC, no FPLC.**
  - Explicit accessibility claim: "These steps can be replaced by more advanced purification methodologies, for example, if an Äkta purifier is available. **The methods described below work even in labs not geared toward protein purification.**"
  - Storage guidance: dilute to ~2 mg/ml — "Storage at higher concentrations may result in aggregation of protein."
- **File:** `Stadlbauer_2020_SARSCoV2_RBD_spike_antigen_production_serology_protocol.txt` (PDF: `../agent_papers/Stadlbauer_2020_SARSCoV2_RBD_spike_antigen_production_serology_protocol.pdf`)

---

## Dalvie et al. 2022 — Scalable, methanol-free manufacturing of the SARS-CoV-2 receptor-binding domain in engineered *Komagataella phaffii*
- **Authors:** Neil C. Dalvie et al. (MIT / Bill & Melinda Gates Foundation-funded consortium)
- **Year:** 2022
- **Journal:** Biotechnology and Bioengineering 119(2):657–662
- **DOI:** 10.1002/bit.27979 — PMID 34780057, PMC8653030
- **Retrieved:** 2026-08-29, Europe PMC open access (full-text XML → text; rendered PDF)
- **Cited in context of:** yeast as the low-cost, secreted (non-refolding) route to RBD at manufacturing scale.
- **Key content verified (direct quotes):**
  - "We genetically engineered a manufacturing strain of *K. phaffii* to obviate the requirement for methanol induction of the recombinant gene. Methanol-free production improved the **secreted titer** of the RBD protein by >5X by alleviating protein folding stress."
  - Titers in perfusion: base (methanol-induced) strain ~30 mg/L with significant cell lysis after ~120 h; engineered `mit1+` strain sustained ">50 mg/L/day for the duration of a >200 h campaign", with lower host-cell-protein impurities in the purified pool.
  - "Removal of methanol from the production process enabled to scale up to a **1200 L** pre-existing production facility. This engineered strain is now used to produce an RBD-based vaccine antigen that is currently in clinical trials."
- **File:** `Dalvie_2022_methanol_free_Komagataella_RBD_manufacturing.txt` (PDF: `../agent_papers/Dalvie_2022_methanol_free_Komagataella_RBD_manufacturing.pdf`)

---

## Mora & Bialek 2011 — Are biological systems poised at criticality?
- **Authors:** Thierry Mora, William Bialek (Joseph Henry Laboratories of Physics / Lewis–Sigler Institute, Princeton)
- **Year:** 2011
- **Journal:** Journal of Statistical Physics 144(2):268–302
- **DOI:** 10.1007/s10955-011-0229-4 (preprint arXiv:1012.2242)
- **Retrieved:** 2026-08-29 (arXiv PDF, open access; `pdftotext -layout` extract).
- **Cited in context of:** Note_013 ref [3] — the "life poised at criticality" claim.
- **Key content verified (direct quotes):**
  - Title itself: "Are biological systems poised at criticality?"
  - Abstract: "Remarkably, in all these cases the models that emerge from the data are poised at a very special point in their parameter space—a critical point. This suggests there may be some deeper theoretical principle behind the behavior of these diverse systems."
  - Method is the *inverse* approach: maximum-entropy statistical-mechanics models built directly from data, across three systems — protein families, networks of neurons, flocks of birds.
  - Explicitly hedged: "possibility that biological system poise themselves at or near a critical point remains tantalizing" (sic).
- **File:** `MoraBialek_2011_biological_systems_poised_at_criticality.txt` (PDF: `../agent_papers/MoraBialek_2011_biological_systems_poised_at_criticality.pdf`)

---

## Muñoz 2018 — Colloquium: Criticality and dynamical scaling in living systems
- **Authors:** Miguel A. Muñoz (Instituto Carlos I de Física Teórica y Computacional, Universidad de Granada)
- **Year:** 2018
- **Journal:** Reviews of Modern Physics 90(3):031001
- **DOI:** 10.1103/RevModPhys.90.031001 (preprint arXiv:1712.04499)
- **Retrieved:** 2026-08-29 (arXiv PDF, open access; `pdftotext -layout` extract).
- **Cited in context of:** Note_013 ref [3] — criticality as the robustness/flexibility trade-off; highest-impact review of the field.
- **Key content verified (direct quotes):**
  - Abstract: "Criticality has been argued to provide biological systems with an optimal balance between robustness against perturbations and flexibility to adapt to changing conditions, as well as to confer on them optimal computational capabilities, huge dynamical repertoires, unparalleled sensitivity to stimuli, etc."
  - Body: "living systems need to achieve a tradeoff between robustness (resilience of the system state to external perturbations; which is a property of ordered phase), and flexibility (responsiveness to environmental stimuli, which is a feature of disordered phases). An optimal balance between these two conflicting tendencies can be accomplished by keeping the system dynamical state at the borderline of an order-disorder phase transition, i.e. at criticality."
  - On genomes specifically: "At larger evolutionary scales, criticality might provide networks with an optimal balance between robustness and evolvability under changing conditions (Aldana et al., 2007; Gershenson, 2012; Kaneko, 2012; Torres-Sosa et al., 2012; Wagner, 2005)."
  - Balanced, not boosterish: calls the hypothesis "celebrated and controversial", notes evidence "in some other cases … limited, incomplete, or not fully convincing", and that it "has elicited some healthy skepticism".
- **File:** `Munoz_2018_RMP_criticality_dynamical_scaling_living_systems.txt` (PDF: `../agent_papers/Munoz_2018_RMP_criticality_dynamical_scaling_living_systems.pdf`)

---

## Hidalgo et al. 2014 — Information-based fitness and the emergence of criticality in living systems
- **Authors:** Jorge Hidalgo, Jacopo Grilli, Samir Suweis, Miguel A. Muñoz, Jayanth R. Banavar, Amos Maritan
- **Year:** 2014
- **Journal:** PNAS 111(28):10095–10100
- **DOI:** 10.1073/pnas.1319166111 · PMID 24982145 · PMCID PMC4104871 (preprint arXiv:1307.4325)
- **Retrieved:** 2026-08-29 (arXiv PDF via Unpaywall — PNAS/PMC block scripted PDF fetch; `pdftotext -layout` extract).
- **Cited in context of:** Note_013 — *why* criticality would be selected for; ties criticality to environmental complexity.
- **Key content verified (direct quotes):**
  - "complex adaptive or evolutionary systems can be much more efficient in coping with diverse heterogeneous environmental conditions when operating at criticality."
  - "a community of such systems dynamically self-tunes close to a critical state as the complexity of the environment increases while they remain non-critical for simple and predictable environments."
  - "providing the best possible trade-off between accuracy and flexibility."
  - Note the conditional: criticality is predicted only for *complex/unpredictable* environments, not universally.
- **File:** `Hidalgo_2014_information_based_fitness_criticality.txt` (PDF: `../agent_papers/Hidalgo_2014_information_based_fitness_criticality.pdf`)

---

## Torres-Sosa, Huang & Aldana 2012 — Criticality is an emergent property of genetic networks that exhibit evolvability
- **Authors:** Christian Torres-Sosa, Sui Huang, Maximino Aldana
- **Year:** 2012
- **Journal:** PLoS Computational Biology 8(9):e1002669
- **DOI:** 10.1371/journal.pcbi.1002669
- **Retrieved:** 2026-08-29 (PLOS open-access PDF; `pdftotext -layout` extract).
- **Cited in context of:** Note_013 — the single most on-point paper for the note's argument: criticality emerges from the conservation/innovation trade-off in *genetic* networks.
- **Key content verified (direct quotes):**
  - "critical dynamics of the network permits the coexistence of robustness and flexibility which are necessary to ensure homeostatic stability (of a given phenotype) while allowing for switching between multiple phenotypes (network states)"
  - "criticality naturally emerges from the need to balance between the two essential components of evolvability: phenotype conservation and phenotype innovation under mutations."
  - Model: Darwinian evolution of random Boolean networks that mutate regulatory interactions and grow by gene duplication, selected to (i) preserve acquired attractor phenotypes and (ii) generate new ones.
  - "dynamical criticality and certain elementary topological properties of gene regulatory networks can emerge as a byproduct of the evolvability of the phenotypic landscape."
  - Caveat: this is a Boolean-network simulation, not experimental data.
- **File:** `TorresSosa_2012_criticality_emergent_genetic_networks_evolvability.txt` (PDF: `../agent_papers/TorresSosa_2012_criticality_emergent_genetic_networks_evolvability.pdf`)

---

## Nykter et al. 2008 — Gene expression dynamics in the macrophage exhibit criticality
- **Authors:** Matti Nykter, Nathan D. Price, Maximino Aldana, Stephen A. Ramsey, Stuart A. Kauffman, Leroy E. Hood, Olli Yli-Harja, Ilya Shmulevich
- **Year:** 2008
- **Journal:** PNAS 105(6):1897–1900
- **DOI:** 10.1073/pnas.0711525105 · PMID 18250330 · PMCID PMC2538855
- **Retrieved:** 2026-08-29 — ⚠️ **abstract + key passages only** (PMC/PNAS block scripted PDF download; verified via the PMC full-text page, no local PDF/txt yet).
- **Cited in context of:** Note_013 — the experimental (rather than theoretical) leg of the criticality claim, in gene expression.
- **Key content verified (direct quotes from PMC full text):**
  - "Criticality enables the coordination of complex macroscopic behaviors that strike an optimal balance between stability and adaptability."
  - "we found that macrophage dynamics are indeed critical, providing the most compelling evidence to date for this general principle of dynamics in biological systems."
  - Method: normalized compression distance (NCD), from algorithmic information theory, applied to global gene expression from macrophages stimulated with Toll-like receptor agonists.
  - Result: NCD scatter "lies closely along the main diagonal with a slope of 1, indicating that the underlying dynamical network of the macrophage is operating in the critical regime".
- **File:** *(no local extract — abstract-only verification)*

---

## Balleza et al. 2008 — Critical dynamics in genetic regulatory networks: examples from four kingdoms
- **Authors:** Enrique Balleza, Elena R. Alvarez-Buylla, Alvaro Chaos, Stuart Kauffman, Ilya Shmulevich, Maximino Aldana
- **Year:** 2008
- **Journal:** PLoS ONE 3(6):e2456
- **DOI:** 10.1371/journal.pone.0002456 · PMCID PMC2423472
- **Retrieved:** 2026-08-29 (PLOS open-access PDF; `pdftotext -layout` extract).
- **Cited in context of:** Note_013 ref [3] — the biology-side entry point to criticality; **includes *E. coli***.
- **Key content verified (direct quotes):**
  - Frames criticality biologically, not thermodynamically: "It must be robust enough as to guarantee stability under a broad range of external conditions, and (b) it must be flexible enough to recognize and integrate specific external signals that may help the organism to change and adapt to different environments."
  - "This compromise between robustness and adaptability has been observed in dynamical systems operating at the brink of a phase transition between order and chaos. Such systems are termed critical."
  - Systems analysed: transcription networks of *S. cerevisiae*, ***E. coli***, *B. subtilis*; segment-polarity network of *D. melanogaster*; flower-development network of *A. thaliana*.
  - Method: "hundreds of microarray experiments to infer the nature of the regulatory interactions among genes", implemented as Boolean network models.
  - Result: "to the best of the current experimental data available, the five networks under study indeed operate close to criticality."
  - Speculation flagged as such: "criticality at the genetic level **might** constitute a fundamental evolutionary mechanism".
- **File:** `Balleza_2008_critical_dynamics_GRN_four_kingdoms.txt` (PDF: `../agent_papers/Balleza_2008_critical_dynamics_GRN_four_kingdoms.pdf`)

---

## Shmulevich, Kauffman & Aldana 2005 — Eukaryotic cells are dynamically ordered or critical but not chaotic
- **Authors:** Ilya Shmulevich, Stuart A. Kauffman, Maximino Aldana
- **Year:** 2005
- **Journal:** PNAS 102(38):13439–13444
- **DOI:** 10.1073/pnas.0506771102 · PMID 16155121 · PMCID PMC1224670
- **Retrieved:** 2026-08-29 — ⚠️ **abstract + methods summary only** (PMC blocks scripted PDF download; verified from the PMC full-text page, no local PDF/txt).
- **Cited in context of:** Note_013 — first direct experimental test of the regime question in a real cell.
- **Key content verified (direct quotes from PMC full text):**
  - "here we show what we believe to be the first direct evidence that the underlying genetic network of HeLa cells appears to operate either in the ordered regime or at the border between order and chaos but does not appear to be chaotic."
  - Data: synchronised HeLa cells, cDNA microarray, 48 time points over 2–3 cell cycles.
  - Method: Lempel–Ziv complexity of real time series vs. mock data from random Boolean networks in ordered/critical/chaotic regimes.
  - ⚠️ Note the hedge in the title and result: **"ordered OR critical"** — this paper excludes chaos, it does not establish criticality.
- **File:** *(no local extract — abstract-only verification)*

---

## Daniels et al. 2018 — Criticality distinguishes the ensemble of biological regulatory networks
- **Authors:** Bryan C. Daniels, Hyunju Kim, Douglas Moore, Siyu Zhou, Harrison Smith, Bradley Karas, Stuart A. Kauffman, Sara I. Walker
- **Year:** 2018
- **Journal:** Physical Review Letters 121(13):138102
- **DOI:** 10.1103/PhysRevLett.121.138102 (preprint arXiv:1805.01447)
- **Retrieved:** 2026-08-29 (arXiv PDF, open access; `pdftotext -layout` extract).
- **⚠️ Title differs between versions:** the local PDF is arXiv v1, titled *"Logic and connectivity jointly determine criticality in biological gene regulatory networks"*. The published PRL title is the one above. Same work.
- **Cited in context of:** Note_013 — meta-analysis over many real curated network models rather than a single system.
- **Key content verified (direct quotes):**
  - "we measure average sensitivity for 66 publicly available Boolean network models describing the function of gene regulatory circuits across diverse living processes. We find the average sensitivity values for these networks are clustered around unity, indicating they are near critical."
  - The interesting twist: "many of these gene regulatory networks achieve the near-critical state with ⟨K⟩ and ⟨p⟩ far from that predicted for critical systems" — i.e. criticality is not explained by connectivity/bias alone.
  - "This suggests the local properties of genes interacting within regulatory networks are selected to collectively be near-critical."
- **File:** `Daniels_2018_criticality_distinguishes_biological_regulatory_networks.txt` (PDF: `../agent_papers/Daniels_2018_criticality_distinguishes_biological_regulatory_networks.pdf`)

---

## Park, Costa, Rocha, Albert & Rozum 2023 — Models of cell processes are far from the edge of chaos
- **Authors:** Kyu Hyong Park, Felipe Xavier Costa, Luis M. Rocha, Réka Albert, Jordan C. Rozum
- **Year:** 2023
- **Journal:** PRX Life 1(2):023009
- **DOI:** 10.1103/PRXLife.1.023009 · PMID 38487681 · PMCID PMC10938903
- **Retrieved:** 2026-08-29 — ⚠️ **abstract only** (APS Cloudflare + PMC both block scripted download; abstract verified via Europe PMC REST API).
- **Cited in context of:** Note_013 — **the counter-argument.** Directly contradicts Balleza 2008 / Daniels 2018 on the same class of evidence.
- **Key content verified (direct quote of abstract, Europe PMC):**
  - "a deeper inspection of 72 experimentally supported discrete dynamical models of cell processes reveals previously unobserved order on long time scales, suggesting greater rigidity in these systems than was previously conjectured."
  - "We find that propagation of internal perturbations is transient in most cases, and that even when large perturbation cascades persist, their phenotypic effects are often minimal."
  - "our results suggest that—contrary to current theory—cell processes are ordered and far from the edge of chaos."
  - Tool released: `cubewalkers` (open-source CUDA Python library).
- **File:** *(no local extract — abstract-only verification)*

---

## Diercks et al. 2024 — T7-ORACLE **SUPPLEMENTARY MATERIALS** (bioRxiv preprint SI)
- **Authors:** Christian S. Diercks, Philipp J. Sondermann, Cynthia Rong, David A. Dik, Thomas G. Gillis, Yahui Ban, Peter G. Schultz (Scripps Research)
- **Year:** 2024 (preprint); published *Science* 389:618–622 (7 Aug 2025)
- **DOI:** 10.1101/2024.07.25.605042 (preprint) / 10.1126/science.adp9583 (journal)
- **Zotero:** `zotero://select/library/items/QTTDYXDP`
- **Files:** `agent_papers/Diercks_2024_T7ORACLE_SI.pdf`, `agent_papers_txt/Diercks_2024_T7ORACLE_SI.txt`
- **Retrieved:** 2026-08-30 — bioRxiv open supplementary (`.../DC1/embed/media-1.pdf`); `pdftotext -layout`. The *Science* SI (`science.adp9583_sm.pdf`) is Cloudflare-blocked (HTTP 403).
- **Cited in context of:** rebuilding T7-ORACLE in-house (Note_014) — parts list, backbones, copy number, promoter/RBS audit.
- **Why this file exists:** the main-text PDFs already in the repo (`papers_txt/{hypermutation_systems,maimonide,directed_evolution}/`) are **main text only (5–6 pp)**. All plasmid/strain/backbone data lives in Tables S1–S6, which are only in this SI.
- **Key content verified:**
  - **Table S1 (plasmids):** RP1 `pCD0280` = **pBR322** ori, KanR, P_BAD::gp4 + P_glnS::gp2.5. RP2 `pCD0260–0266` = **pSC101**, GenR, P_polI::gp5 variants. RP3 `pCD0275` = **CloDF13** (printed "CloDF3"), SmR, P_proD::gp3.5–gp1 fusion. Replicons `pOR-1/-3/-4` = **φOR**, CamR; `pOR-2` = **φOR1 + pR6K2**, AmpR. `pSR-1` = pUC, AmpR, *dxs* (qPCR calibrator).
  - **Table S2 (strains):** all in **BW25113** (Keio parent). T7Rep-1…7 = pCD0280 + pCD026X + pCD0275.
  - **Table S3 (rates + copy no.):** replicon copy number is set by the T7 replisome, not an E. coli ori — 1.5 (WT) → 12.5 (Δ28) → **4.1 for the final T7Rep-7**. *Typo:* T7Rep-7 rate printed `1.7×10⁻⁹`, must be `10⁻⁵` (cf. Table S6).
  - **Residue-numbering conflict:** Tables say `R443K`, main text says `V443K`. NC_001604.1 gp5 residue 443 is Val → **V443K correct**.
  - **NEGATIVE RESULT — no sequences anywhere.** Grep for `RBS`, `ribosome`, `Shine`, `Dalgarno`, `UTR`, `terminator`, `linker`, `spacer`, `codon opt`, `GenBank`, `accession`, `Addgene` → **zero hits**. Methods only state: "DNA fragments encoding the open-reading frames of gp1, gp2.5, gp4, gp3.5, and gp5 were purchased from IDT… assembled by Gibson assembly."
  - **NEGATIVE RESULT — no induction documented.** Grep for `arabinose`, `inducer`, `induction`, `IPTG` → **zero hits**, despite gp4 sitting under P_BAD.
  - **Zenodo 10.5281/zenodo.14990911 checked:** contains only a 9.5 kB NGS-analysis code zip — **no sequence files**.
  - **φOR is never defined** — deferred to ref. 32 (Zhang & Studier, *J Mol Biol* 340:707, 2004), which is **not yet in the library**.

---

## Davis, Rubin & Sauer 2011 — Design, construction and characterization of a set of insulated bacterial promoters
- **Authors:** Joseph H. Davis, Adam J. Rubin, Robert T. Sauer (MIT Biology)
- **Year:** 2011 · *Nucleic Acids Res.* 39:1131–1141 · DOI 10.1093/nar/gkq810 · PMID 20843779 · PMC3035448 (open access)
- **Files:** `agent_papers_txt/Davis_2011_insulated_bacterial_promoters_proD.txt`
- **Retrieved:** 2026-08-30 — Europe PMC `fullTextXML`, tags stripped. Full text read.
- **Cited in context of:** identifying **P_proD**, the promoter driving the gp3.5–gp1 fusion on RP3/pCD0275 in T7-ORACLE (Note_014).
- **Key content verified (direct quotes / table):**
  - Table 1 (promoter strengths, RPU normalised to proD = 1.000): `proA` −35 `tttacg` / −10 `taggct` = **0.030**; `proB` `taatat` = **0.119**; `proC` `tatgat` = **0.278**; **`proD` `tttacg`/`tataat` = 1.000**; `j23101` `tttaca`/`tattat` = **0.345**.
  - **proD full sequence** (BioBrick scars lowercase): `ttctagag`CACAGCTAACACCACGTCGTCCCTATCTGCTGCCCTAGGTCTATGAGTGGTTGCTGGATAAC**TTTACG**GGCATGCATAAGGCTCG**TATAAT**ATATTCAGGGAGACCACAACGGTTTCCCTCTACAAATAATTTTGTTTAACTTT`tactagag`
  - The "insulated" design point: a 5′ insulating region fixes the TSS so activity is **not context-dependent**; only the −35/−10 hexamers vary across the pro series.
  - proD carries a **perfect consensus −10 (TATAAT)** and is the strongest of the series (~3× j23101, ~33× proA).
- **Cross-check:** Salis Promoter Calculator (`mcp__bioinfo__predict_promoters`) run on the proD sequence independently returns the top forward hit at TSS 101 with −35 `TTTACG` / −10 `TATAAT`, tx_rate 4702 au — **exactly the published hexamers**.
- **⚠️ Open ambiguity:** T7-ORACLE Table S1 writes "P*proD*". This is most plausibly the Davis *proD* above, but the Schultz lab habitually uses the *E. coli* **proK** (prolyl-tRNA) promoter in its pUltra/pEVOL orthogonal-translation vectors. **proD vs proK is not resolved by the paper** — confirm before building.

---

## Guzman, Belin, Carson & Beckwith 1995 — Tight regulation, modulation, and high-level expression by vectors containing the arabinose PBAD promoter
- **Year:** 1995 · *J. Bacteriol.* 177:4121–4130 · PMID 7608087 · PMC177145
- **Retrieved:** 2026-08-30 — **abstract only**, verbatim from Europe PMC (`resultType=core`). Full text XML returned 404; not open access.
- **Cited in context of:** **P_BAD** driving gp4 on RP1/pCD0280 in T7-ORACLE (Note_014).
- **Key content verified (abstract, verbatim):**
  - "the ratio of induction/repression can be **1,200-fold**, compared with 50-fold for PTAC-based vectors"
  - "expression can be **modulated over a wide range of inducer (arabinose) concentrations** and reduced to extremely low levels by the presence of **glucose**, which represses expression"
  - "the kinetics of induction and repression are very rapid and **significantly affected by the *ara* allele in the host strain**" ← directly relevant: T7-ORACLE's host BW25113 is **Δ(araBAD)567**
  - pBAD vectors carry PBAD **plus *araC***, the positive/negative regulator.
- **⚠️ Everything beyond the abstract is `[UNVERIFIED]`.** The PBAD *sequence* used here was instead taken from the *E. coli* genome directly (NC_000913.3, araBAD/araC intergenic region), not from this paper.

---

## CIDAR MoClo Parts Kit — Volume I, User Guide (Densmore lab / Addgene, rev. 2018-05-29)
- **Type:** Kit documentation (not a peer-reviewed paper)
- **Source:** https://media.addgene.org/cms/filer_public/e3/64/e364349e-eb5a-4ee7-a3a7-d615aa88f817/180529_cidar_vol_i_guide.pdf
- **Files:** `agent_papers/CIDAR_MoClo_VolI_guide_2018.pdf`, `agent_papers_txt/CIDAR_MoClo_VolI_guide_2018.txt`
- **Retrieved:** 2026-08-30 (user-supplied URL). Full guide read; RBS/UTR sections read in detail.
- **Cited in context of:** choosing RBSs for the single-plasmid T7-ORACLE replisome rebuild (Note_014).
- **Key content verified:**
  - **Assembly chemistry:** "golden gate assembly with BsaI and BbsI" — BsaI = stage 1 (parts → TU), **BbsI/BpiI = stage 2** (TU → multi-TU device). Recommends NEB Golden Gate Assembly Mix with BsaI-HFv2 (E1601).
  - **Non-BCD RBSs (Weiss series, short, mutually non-repetitive):** `U1d` = B0032m *medium*; `U2d` = B0033m *weak*; `U3d` = B0034m *strong* (used in the Elowitz repressilator). Guide gives qualitative ranks only, **no fold numbers**.
  - **BCD ladder, strengths relative to BCD2 = 1.0:** `U4d` BCD2 1.0 (strongest) · `U22m` BCD6 0.4–0.9 · `U3m` BCD13 0.5–0.9 · `U2m` BCD11 0.5–0.75 · `U5m` BCD14 0.2–0.7 · `U6d` BCD12 0.2–0.9 · `U6m` BCD20 0.2–0.5 · `U7m` BCD16 0.1–0.3 · `U8m` BCD24 0.08–0.2 · `U5d` BCD8 0.05–0.2 · `U9m` BCD22 0.02–0.1. **Total span ≈ 50×.**
  - **⚠️ CRITICAL (stated twice, verbatim):** "Note that all of the BCDs share approximately 50bp of identical sequence, which makes circuits constructed with multiple BCDs highly prone to recombination (in particular, large deletions). Constructs with multiple BCDs are therefore especially vulnerable to mutational breakage, and **use of multi-BCD constructs is not recommended**."
  - **BCD mechanism:** first RBS translates a fixed 16-aa leader peptide whose sequence contains the second RBS; leader translation disrupts folding between RBS and CDS. The gene of interest keeps its own start codon — **no N-terminal tag on the product**.
  - **⚠️ `U4m` (UTR1, T7 gene 10 leader, Olins 1988):** "Warning: High levels of translation can drive breakage and evolutionary escape… **Not recommended for toxic products, even from repressed promoters**." Data/Experience: "Most constructs expressing a protein with UTR1 off of a high-copy plasmid break quickly or fail to clone."
  - `U17m` Bujard RBS — strong, "roughly comparable to U4m in strength". `U24m`/`U25m` = RiboJ + BCD2 / RiboJ + UTR1 (RiboJ insulates 5′ UTR variability, but still carries BCD/UTR1 homology).
  - Precedent for domestication throughout the kit (E0040→BsaI removed, dCas9 "BbsI-safe" variant, etc.).
- **Derived analysis (this session, tool-backed):** Golden Gate site scan of the five T7 replisome CDSs from NC_001604.1 —
  | gene | len | BsaI | BbsI | BsmBI |
  |---|---|---|---|---|
  | gp1 | 2652 | 0 | 5 | 0 |
  | gp2.5 | 699 | 1 | 5 | 0 |
  | gp3.5 | 456 | 0 | 0 | 1 |
  | gp4A | 1701 | 1 | 2 | 1 |
  | gp5 | 2115 | 3 | 2 | 1 |
  | **TOTAL** | | **5** | **14** | **3** |
  → CIDAR MoClo would require **19 synonymous edits** (5 BsaI + 14 BbsI), which is incompatible with plain PCR off the T7 genome. The original paper avoided this entirely by ordering IDT synthetic ORFs and using **Gibson** assembly.

---

## Chen, Liu, Nielsen, Brophy, Clancy, Peterson & Voigt 2013 — Characterization of 582 natural and synthetic terminators and quantification of their design constraints
- **Authors:** Ying-Ja Chen, Peng Liu, Alec A.K. Nielsen, Jennifer A.N. Brophy (MIT Synthetic Biology Center), Kevin Clancy, Todd Peterson (Life Technologies), Christopher A. Voigt (MIT)
- **Year:** 2013
- **Journal:** Nature Methods 10(7):659–664
- **DOI:** 10.1038/nmeth.2515 · **PMID:** 23727987 (no PMC record — Europe PMC reports "Subscription required", not open access)
- **Files:**
  - `agent_papers/Chen_2013_582_terminators_design_constraints.pdf` → `agent_papers_txt/Chen_2013_582_terminators_design_constraints.txt`
  - `agent_papers/Chen_2013_582_terminators_SI.pdf` → `agent_papers_txt/Chen_2013_582_terminators_SI.txt` (Supplementary Figs. 1–23, Supplementary Table 1, Supplementary Notes 1–11)
  - `agent_papers/Chen_2013_582_terminators_SI_TableS2_natural.xlsx` → `agent_papers_txt/Chen_2013_582_terminators_SI_TableS2_natural.txt` (TSV extract; **317 natural terminators** = 227 forward + 90 reverse)
  - `agent_papers/Chen_2013_582_terminators_SI_TableS3_synthetic.xlsx` → `agent_papers_txt/Chen_2013_582_terminators_SI_TableS3_synthetic.txt` (TSV extract; **265 synthetic terminators**)
  - `agent_papers/Chen_2013_582_terminators_SI_TableS4_removed.xlsx` → `agent_papers_txt/Chen_2013_582_terminators_SI_TableS4_removed.txt` (TSV extract; terminators removed for anomalous expression)
- **Retrieved:** 2026-08-31 — main text via Sci-Hub (`sci-hub.al`, `scripts/fetch_papers.py:download_from_scihub`); **supplementary via the publisher directly** (Nature ESM is free: `media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnmeth.2515/MediaObjects/41592_2013_BFnmeth2515_MOESM205–208_ESM`). `pdftotext -layout` for PDFs, `openpyxl` TSV dump for the XLSX tables.
- **Cited in context of:** the **primary source for CIDAR MoClo terminator strengths** — the TS values quoted in the CIDAR MoClo Vol. I guide (`CIDAR_MoClo_VolI_guide_2018.txt`) for T13m/T17m/T18m all trace back to Supplementary Tables 2 and 3 here.
- **Assay / definition verified (direct quotes):**
  - "Terminator strength (TS) was determined from a simple assay that compares the expression of two fluorescent reporters, one placed before and one after the terminator (Fig. 1a)."
  - Reference point: "the plasmid with no terminator insert was used as reference (**TS = 1.00 ± 0.36 s.d.**)".
  - "Within this library we found **39 strong terminators**, yielding **>50-fold reduction** in downstream expression, that have sufficient sequence diversity to reduce homologous recombination when used together in a design." — confirmed by counting the "Recombination-resistant strong terminator" flag in the SI: **18 natural (Table S2) + 21 synthetic (Table S3) = 39**.
  - "strong and weak terminators are defined as TS > 40 and TS < 3, respectively."
  - Registry baseline: "The strongest forward terminator from the Registry was **BBa_B0010 (TS = 84 ± 12)** … In the library, there are 11 stronger E. coli terminators."
- **TS values verified from the primary supplementary tables** (columns `Average Strength` ± `Standard Deviation of Strength`):

  | Terminator | Source table | TS (raw) | s.d. (raw) | Rounded | Rec.-resistant strong? |
  |---|---|---|---|---|---|
  | `ECK120033737` (natural, *thrLABC*) | Suppl. Table 2 | 312.4964 | 116.7333 | **312 ± 117** | yes |
  | `L3S2P11` (synthetic) | Suppl. Table 3 | 261.5484 | 37.9699 | **262 ± 38** | yes |
  | `L3S2P21` (synthetic) | Suppl. Table 3 | 382.1299 | 18.4240 | **382 ± 18** | yes |
  | `ECK120029600` (natural, *spy*) | Suppl. Table 2 | 378.3780 | 113.7419 | 378 ± 114 | yes |

  - `ECK120033737` sequence (Suppl. Table 2): `ggaaacacagAAAAAAGCCCGCACCTGACAGTGCGGGCTTTTTTTTTcgaccaaagg`
  - `L3S2P11` sequence (Suppl. Table 3): `CTCGGTACCAAATTCCAGAAAAGAGACGCTTTCGAGCGTCTTTTTTCGTTTTGGTCC`
  - `L3S2P21` sequence (Suppl. Table 3): `CTCGGTACCAAATTCCAGAAAAGAGGCCTCCCGAAAGGGGGGCCTTTTTTCGTTTTGGTCC`
  - ⚠️ **Discrepancy vs the CIDAR guide:** the guide lists T13m (= `ECK120033737`) as **313 ± 117**; the primary table gives **312.4964 → 312 ± 117**. Off by one in the last digit (rounding), not a different measurement. `L3S2P11` (T17m, 262 ± 38) and `L3S2P21` (382 ± 18) match the guide exactly.
  - ⚠️ **T18m is not `L3S2P21` verbatim** — CIDAR domesticated it (type-IIS site removed), so the 382 ± 18 above is the value for the **unmodified** `L3S2P21`; the modified part was not re-measured in this paper.
- **Other content verified:** biophysical model of TS from U-tract / loop / hairpin / A-tract free energies (ΔGU, ΔGL, ΔGH, ΔGA, ΔGB → `Predicted TS`, columns present in Tables S2–S3); Scaffold-1 `pheA-1` "was one of the strongest in the library (TS = 244 ± 46), but it was also the most sensitive to changes"; NOT-gate rebuild using `L3S2P21` (Suppl. Note 10).

---

## Costan et al. 2024 — Biophysical characterization of synthetic adhesins for predicting and tuning engineered living material properties
- **Authors:** Sebastián A. Costan, Daniel S. Glass, Ingmar H. Riedel-Kruse *et al.*
- **Year:** 2024
- **Journal:** Matter 7(6):2125–2143
- **DOI:** 10.1016/j.matt.2024.03.019
- **Zotero:** `zotero://select/library/items/VW9WHQQG` (PDF in library; `pdftotext -layout` extract 2026-08-31)
- **Cited in context of:** Note_017 / MS_C_019 — **identifying the anti-GFP display plasmid** and the aTc → adhesins-per-cell calibration for tuning display valency.
- **Key content verified (direct quotes):** Methods, "Plasmids and strains": "**pDSG339 (pSB3K3_TetR_pTet_Neae2v1_antiGFP) (GenBank: MH_492430)**, pDSG320 (pSB3K3_TetR_pTet_Neae2v1_antiEPEA) (GenBank: MH_492391), and pDSG321 (pSB3K3_TetR_pTet_Neae2v1_antiP53TA) (GenBank: MH_492393) are **medium-copy-number plasmids (20–30)**, whereas pDSG288 (pSB4A3_TetR_pTet_Neae2v1_P53TA) (GenBank: MH_492378) is a **low-copy-number plasmid (10–12)**." Nb-Ag pairs characterised: anti-GFP/GFP, anti-EPEA/EPEA, anti-p53/p53TA. Quantifies adhesins per cell, in-membrane diffusion constant, production/decay rates, and bond-breaking force by optical trap.
- **Note:** pDSG339 is **not** deposited at Addgene (searched 2026-08-31; absent from the Glass 115594–115613 block). Sequence-only via GenBank MH492430.
- **File:** `Costan_2024_synthetic_adhesins_biophysical_characterization.txt`

---

## Fridy et al. 2014 — A robust pipeline for rapid production of versatile nanobody repertoires
- **Authors:** Peter C. Fridy, Yinyin Li, Sarah Keegan, Michael K. Thompson *et al.* (Rout / Chait labs)
- **Year:** 2014
- **Journal:** Nature Methods 11:1253–1260
- **DOI:** 10.1038/nmeth.3170 · **PMID:** 25362362 · **PMC:** PMC4272012
- **Downloaded:** 2026-08-31 (PMC full text, HTML → text)
- **Cited in context of:** Note_017 — sourcing an **internally consistent anti-GFP affinity ladder** for the two-strain display discrimination experiment.
- **Key content verified (direct quotes):** "these experiments revealed a **wide range of affinities, with Kds from 0.5 nM to over 20 μM** (Table 1), and identified **16 nanobodies with high affinity binding (≤50 nM)**." Table 1 legend: "**Kds for GFP and mCherry binding were determined by SPR** unless otherwise noted… **GFP epitopes were determined by NMR for LaGs, and grouped into three broad classes (I–III).**"
- **Table 1, anti-GFP LaG panel (SPR Kd / NMR epitope class):** LaG-30 0.5 nM · **LaG-16 0.7 nM (I)** · LaG-41 0.9 nM (II) · LaG-14 1.9 nM (I) · LaG-26 2.6 nM (II) · LaG-9 3.5 nM (I) · LaG-21 7 nM (II) · LaG-27 9.5 nM (II) · LaG-43 11 nM (I) · LaG-2 19 nM (III) · LaG-35 23.5 · LaG-37 24 · LaG-19 24.6 (II) · LaG-3 25 · LaG-24 41 (III) · **LaG-17 50 nM (I)** · LaG-12 56 · LaG-10 97 · LaG-29 110 · LaG-6 310 · LaG-42 600 · LaG-5 14,200 nM.
- **Why it matters here:** **LaG-16 vs LaG-17 = 71× in Kd, same study, same method (SPR), same epitope class I** — a usable affinity ladder, unlike Enhancer vs LaG16 (~3×, and the rank order flips between SPR and ITC).
- **⚠️ Method caveat (verified 2026-10-21, this file):** Table 1 is SPR **"unless otherwise noted"**, and footnote **"1 Kd determined by bead binding assay"** applies to **LaG-5 (14,200 nM)**. Body text confirms affinities were assessed "by **either** surface plasmon resonance (SPR) **or** in vitro binding assays with immobilized nanobodies". **LaG-17 (50 nM) and LaG-6 (310 nM) carry no footnote → SPR, mutually comparable (6.2×). LaG-5 is NOT method-comparable with them** — do not quote a "280× vs LaG-17" ratio without saying it crosses methods.
- **⚠️ Not yet verified:** the **amino-acid sequences** of individual LaG clones are in the supplementary material, which has not been retrieved. LaG-16 was instead taken from **PDB 6LR7 chain B**. **LaG-17 remains unsourced.**
- **File:** `Fridy_2014_llama_nanobody_repertoire_LaG_panel.txt`

---

## Zacharias et al. 2002 — Partitioning of lipid-modified monomeric GFPs into membrane microdomains of live cells
- **Journal:** Science 296:913–916 · **DOI:** 10.1126/science.1068539 · **PMID:** 11988576
- **Downloaded:** 2026-09-14 (Sci-Hub, PDF → text)
- **Cited in context of:** Note_017 — verifying that **MS_C_024 (mEGFP-AviTag-His6) is genuinely monomeric**, i.e. that the antigen cannot present two epitopes and confound an affinity comparison under avidity.
- **Key content verified (direct quotes):** "We suspected the residual clustering to be an artifact of the **known tendency of all forms of GFP to dimerize at high concentrations**"; homoaffinity of purified recombinant YFP measured "by **sedimentation equilibrium analytical ultracentrifugation** … and found a **K_d of 0.11 mM**"; interface hydrophobics replaced "with positively charged residues (**A206K, L221K, or F223R**) … **YFP homoaffinity was reduced to the point that dimerization was essentially eliminated**"; "These mutations caused **no significant alterations in the spectral properties**."
- **Table 1 (dimer K_d by AUC):** wild type **0.11 mM** · L221K 9.7 mM · F223R 4.8 mM · L221K/F223R 2.4 mM · **A206K 74 mM** (footnote: "Due to the **extreme monomeric nature** of this protein…"). A206K = **~670× weaker self-association**, the single best of the three.
- **Why it matters here:** at the ≤ µM antigen concentrations used in a display-binding assay, a 74 mM dimer K_d means a monomer fraction indistinguishable from 1. This is what licenses reading strain-to-strain differences as **nanobody affinity** rather than antigen bivalency.
- **⚠️ Caveats:** (1) K_d values were measured on **YFP, not EGFP** — the Ala206/Leu221/Phe223 interface is shared across avGFP variants, but the numbers are not EGFP numbers. (2) In EGFP's ORF the residue is at **physical position 207** because of the extra Val2 in pEGFP-N1 (U55762); "A206K" is avGFP numbering.
- **File:** `Zacharias_2002_monomeric_GFP_A206K.txt`

---

## Salema & Fernández 2017 — Escherichia coli surface display for the selection of nanobodies
- **Journal:** Microbial Biotechnology 10(6):1468–1484 · **DOI:** 10.1111/1751-7915.12819 · **PMC:** PMC5658595
- **Downloaded:** 2026-08-31 (PMC full text) · **Cited in context of:** Note_017 — can a 4-Cys nanobody (LaG-5) be displayed via intimin?
- **Key content verified (direct quotes):** "the native Ig-like domains of intimin fold and form a disulfide bridge **catalysed by DsbA in the periplasm prior to their translocation**"; "we observed that **folded Ig domains fused to the β-barrel of various ATs were efficiently translocated** to the surface of E. coli"; "Nbs often contain, besides the canonical disulfide bond of Ig domains, **an extra disulfide bond connecting CDR3 and CDR1 (in camels) or CDR3 with CDR2 (in llamas)**"; platform tested with "**three different VHH immune libraries, two from dromedaries and one from llamas**".
- **Conclusion drawn:** the intimin passenger crosses the OM already oxidised and folded — this is the normal working case, so an extra disulfide is not a mechanistic barrier. ⚠️ No paper found names an individual 4-Cys clone displayed via intimin; the argument is from library composition, not a labelled example.
- **File:** `Salema_Fernandez_2017_ecoli_surface_display_selection_nanobodies.txt`

---

## Zhang et al. 2024 — Functional divergence in the affinity and stability of non-canonical cysteines and non-canonical disulfide bonds: insights from a VHH and VNAR study
- **PMC:** PMC11432006 · **Downloaded:** 2026-08-31 (PMC full text)
- **Cited in context of:** Note_017 — prevalence of extra disulfides in VHHs, and whether to engineer LaG-5's out.
- **Key content verified (direct quotes):** "**about 90% of VHHs derived from the Bactrian camel and dromedary have an extra cysteine in CDR1 or FR2**, which enable the generation of a non-canonical disulfide bond which is predominantly situated between CDR1 and CDR3 or FR2 and CDR3"; "**over 40% of VHHs contain a non-canonical cysteine in FR2**, and the corresponding non-canonical disulfide bonds almost occur between FR2 and CDR3"; Cys→mutant affinity loss "**13–211 fold increase** relative to lyso-VNAR" in K_D, while the DTT-reduced protein kept comparable affinity; "it is **unnecessary to exclude** intrabodies which contain non-canonical disulfide bonds during the early screening".
- **Conclusion drawn:** **do not mutate LaG-5's extra cysteines out** — they contribute to binding, not just stability, and removing them would destroy the published K_d.
- **File:** `Zhang_2024_noncanonical_cysteines_disulfides_VHH_VNAR.txt`

---

## Howarth & Ting 2008 — Imaging proteins in live mammalian cells with biotin ligase and monovalent streptavidin
- **Journal:** Nature Protocols 3:534–545 · **DOI:** 10.1038/nprot.2008.20 · **PMID:** 18323822
- **Downloaded:** 2026-09-01 (open copy, Howarth lab, Oxford) · **Cited in context of:** Note_017 — the published purification protocol for Addgene #20857 (pET21a-BirA), and whether BirA needs refolding.
- **Key content verified (direct quotes), Box 1 "BirA EXPRESSION":** "**BirA is an Escherichia coli protein; hence, it expresses to a high level and remains soluble, when overexpressed as a His6-fusion. The His6-fusion protein is isolated in good purity and yield using a nickel-affinity column.**" → **no denaturation/refolding needed.**
- **Protocol specifics:** BL21(DE3) **pLysS**, LB-Amp; ⚠️ "Do not use plates that have been stored at 4 °C and do not use glycerol stocks. Use only freshly transformed plates to ensure optimal expression"; 400 mL culture, induce at A600 0.5–0.7; "**Shake at 30 °C for 3 h. This lower temperature improves the folding efficiency of BirA**"; harvest 8,000 g; lyse in 4 mL + PMSF + protease inhibitors, sonicate 6 × 15 s; **only 0.4 mL packed Ni-NTA**; wash **30 mM imidazole** ×10 CV; elute **100 mM imidazole**, 2 mL; "0.1 mg ml⁻¹ of BirA gives A280 = 0.13" (i.e. A280 of 1 mg/mL ≈ 1.3 — matches the 1.29 computed from the sequence); dilute to 100 µM (3.5 mg/mL) in PBS before dialysis "if the concentration is too high, there will be a lot of aggregation when you dialyze"; dialyse 3 × >3 h vs 1000× PBS; store at 50 µM, −80 °C, "stable indefinitely".
- **⚠️ Contrast:** *monovalent streptavidin* in the same paper DOES require inclusion-body refolding and takes 8 d, vs 4 d for BirA. Do not conflate the two.
- **File:** `Howarth_Ting_2008_BirA_monovalent_streptavidin_protocol.txt`

## Gambill et al. 2023 — A split ribozyme that links detection of a native RNA to orthogonal protein outputs
- **Authors:** Lauren Gambill, August Staubus, Kim Wai Mo, Andrea Ameruoso, James Chappell (Rice University)
- **Year:** 2023
- **Journal:** Nature Communications 14:543
- **DOI:** 10.1038/s41467-023-36073-3 · **PMID:** 36725852
- **Retrieved:** 2026-09-02 (already in Zotero, item `H5GEN97V`; `pdftotext -layout` extract of the article and of the Supplementary Information)
- **Cited in context of:** annotating Addgene plasmids pJEC779 (#234348) and pJEC780 (#234349) from Addgene article 28252881 — identifying every RENDR part, the split site, and the swap points for retargeting and for changing the protein output.
- **Key content verified (direct quotes):**
  - Mechanism: *"a splicing ribozyme is synthetically split into two non-functional fragments that are each appended with RNA guide sequences that are designed to interact with the RNA input… the RNA input co-localizes the two transcribed ribozyme fragments, forming a functional ribozyme complex, and the ribozyme splices together the mRNA of the protein output."*
  - Modular design: *"we redesigned the split ribozyme to be located between the RBS and the CDS of the output protein (Fig. 4a), resulting in a more modular design that eliminates the need to identify a ribozyme insertion site in each new protein-output gene."*
  - Splice site: *"the ribozyme splices together the sfGFP exons at the 5' splice site (blue U), located just upstream of the ribozyme"*; catalytically dead control is the **G264A** mutant.
  - Design rule for new inputs (Supplementary Note 1, step 3): *"identify RNA guide sequences that are the reverse complement of the target sequence and separated by a 5 nt gap"*, then *"(4) Add a 6 nt sequence that will encode a stem between the guide and the ribozyme sequence that is used to enhance split-ribozyme complementation."*
  - Cloning route: golden-gate staging vector **JEC847** with **BsmBI** — *not* deposited in the Addgene article, and no BsmBI site exists in pJEC779/pJEC780.
  - Architectures used (Supplementary Table 1): pJEC779 = `SpecR - CDF - PJ23119 - HP14 - RBS_01 - P1_helix_01 - P1_loop_01 - Stem_01 - Guide_15 - T500 - PJ23119 - Guide_16 - Stem_02 - P1_loop_03 - IGS_01 - Ribozyme - sfGFP - TrrnB`; pJEC780 = `AmpR - ColE1 - PJ23119 - Input_07 - T500`.
  - Part sequences taken from Supplementary Tables 3–5 (`IGS_01 GGGTCA`, `P1_helix_01 TGACCT`, `RBS_01 AGGAGGAA`, `Stem_01 GGATCA`/`Stem_02 TGATCC`, `P1_loop_01 AAATAGCAA`, `P1_loop_03 TAGTTACCTTT`, 387 nt `Ribozyme`, 82 nt `Guide_15`/`Guide_16`, 169 nt `Input_07`).
- **File:** `Gambill_2023_RENDR_split_ribozyme_RNA_detection.txt` · `Gambill_2023_RENDR_SI.txt` (PDFs: `../agent_papers/Gambill_2023_RENDR_split_ribozyme_RNA_detection.pdf`, `../agent_papers/Gambill_2023_RENDR_SI.pdf`)

---

## Romano, Tamanoi & Richardson 1981 — Initiation of DNA replication at the primary origin of bacteriophage T7 by purified proteins: requirement for T7 RNA polymerase
- **Authors:** Louis J. Romano, Fuyuhiko Tamanoi, Charles C. Richardson (Harvard Medical School)
- **Year:** 1981
- **Journal:** Proceedings of the National Academy of Sciences USA 78(7):4107-4111
- **DOI:** 10.1073/pnas.78.7.4107 · **PMID:** 6945573
- **Retrieved:** 2026-09-06 (already in Zotero, item `ZD9HW5WA`, PDF attachment `MG3MY89U`; `pdftotext -layout` extract). PMID resolved via NCBI E-utilities esearch on the title.
- **Cited in context of:** locating and annotating the **primary origin of T7 DNA replication** on NC_001604 — see [`../geneious_exchange/provenance/NC_001604.md`](../geneious_exchange/provenance/NC_001604.md).
- **Key content verified (direct quotes):**
  - Location: *"The primary origin of bacteriophage T7 DNA replication is located 15% of the distance from the left end of the T7 DNA molecule."*
  - Structure: *"This intergenic segment is A+T-rich, contains a single gene 4 protein recognition site, and is preceded by two tandem promoters for T7 RNA polymerase"* (promoters phi1.1A and phi1.1B, Fig. 1).
  - Mapping: *"we recently physically mapped an essential component of the primary origin to within a 129-base pair region between positions 14.75 and 15.0"* — with 39,937 bp / 100 map units = 399.4 bp per unit this is **~5890-5990** on NC_001604.
  - Requirement for transcription: *"upon the addition of T7 RNA polymerase and ribonucleoside triphosphates, 14% of the product molecules have replication bubbles, all of which are located near the primary origin observed in vivo; no such initiation occurs on T7 deletion mutant LG37 DNA, which lacks the primary origin."*
  - Primase site and mechanism A: *"As transcription proceeds through the A+T-rich region, the gene 4 protein recognition site, 5'-G-G-G-T-C-3', is exposed, allowing synthesis of an RNA primer that is then extended by T7 DNA polymerase."*
  - Secondary origins: *"Deletion of the primary origin shifts initiation to secondary origins"*; *"Dunn and Studier (29) identified a hitherto unknown T7 RNA polymerase promoter, fOL [phiOL], at position 1.0; it is also followed by an A+T-rich region. Initiation at this secondary origin should give rise, as in vivo, predominantly to Y forms due to its proximity to the end of the molecule."*
  - Cloned origin: DNA synthesis is *"specific for plasmids containing the primary origin, provided they are first converted to linear forms"* (pAR111 vs pDR100).
- **The sentence that prompted the lookup:** *"Although the precise location and structure of the primary origin of T7 DNA replication is now known, little is known about the molecular mechanisms involved in initiation."*
- **File:** `Romano_1981_T7_primary_origin_of_replication.txt` (PDF: Zotero storage `MG3MY89U`, not copied into `agent_papers/`)

---

## Roots, Lukasiewicz & Barrick 2021 — OSTIR: open source translation initiation rate prediction
- **Authors:** Cameron T. Roots, Alexandra Lukasiewicz, Jeffrey E. Barrick (UT Austin)
- **Year:** 2021
- **Journal:** Journal of Open Source Software 6(64):3362
- **DOI:** 10.21105/joss.03362 · **PMID:** 36177308 · CC BY 4.0
- **Retrieved:** 2026-09-06 (direct from the JOSS paper server, `agent_papers/Roots_2021_OSTIR_JOSS.pdf`, PyMuPDF extract).
- **Cited in context of:** building [`tools/rbs_calculator/`](../tools/rbs_calculator/README.md) — the notebook's engine and every number it prints.
- **Key content verified (direct quotes):**
  - Provenance: *"OSTIR is open source software (GPLv3) derived from the RBS Calculator v1.0 codebase (Salis et al., 2009, 2015; Salis, 2011). OSTIR was rewritten to use the open source ViennaRNA software suite (Lorenz et al., 2011)"*.
  - Why not the original: the RBS Calculator v1.0 *"is not maintained and is only functional when using the NUPACK software suite"*; v2.x is *"proprietary, and this software can only be used to make predictions through a web server that requires user registration"*.
  - Refit: *"Updating OSTIR to be compatible with ViennaRNA and newer RNA folding energy parameters required refitting coefficients in the underlying thermodynamic model"*.
  - **Accuracy (the number to quote):** *"OSTIR predicts translation initiation rates for 53% of the test sequences within 2-fold of the experimentally measured values and for 91% of these sequences the predictions are within 10-fold of the measured values."*
  - Feature relevant to non-*E. coli* work: *"OSTIR allows the user to specify the anti-Shine-Dalgarno sequence used for the ribosome so that predictions can be made for bacterial species other than Escherichia coli"*.
- **File:** `Roots_2021_OSTIR_JOSS_translation_initiation_rate.txt` (PDF: `../agent_papers/Roots_2021_OSTIR_JOSS.pdf`)

---

## Salis, Mirsky & Voigt 2009 — Automated design of synthetic ribosome binding sites to control protein expression
- **Authors:** Howard M. Salis, Ethan A. Mirsky, Christopher A. Voigt
- **Year:** 2009
- **Journal:** Nature Biotechnology 27(10):946-950
- **DOI:** 10.1038/nbt.1568 · **PMID:** 19801975 · **PMCID:** PMC2782888
- **Retrieved:** 2026-09-06. Sci-Hub mirrors all failed; text taken from the **PMC author manuscript** via NCBI E-utilities efetch (db=pmc, PMC2782888) and converted from JATS XML. No PDF in `agent_papers/`.
- **Cited in context of:** the thermodynamic model implemented by OSTIR and documented in [`tools/rbs_calculator/rbs_toolkit.py`](../tools/rbs_calculator/rbs_toolkit.py).
- **Key content verified (direct quotes):**
  - **Energy model (Eq. 2):** *"ΔGtot=ΔGmRNA:rRNA+ΔGstart+ΔGspacing−ΔGstandby−ΔGmRNA where the reference state is a fully unfolded subsequence with ΔGref = 0."*
  - Proportionality: *"The amount of expressed protein E is proportional to the translation initiation rate where the proportionality factor K accounts for any ribosome-mRNA molecular interactions that are independent of mRNA sequence"* — i.e. **arbitrary units; only ratios are meaningful**.
  - 16S rRNA: *"The ΔGmRNA:rRNA term is the energy released when the last 9 nucleotides (nt) of the E. coli 16S rRNA – 3′-AUUCCUCCA-5′ –"* hybridises to the mRNA subsequence.
  - **Spacing optimum:** *"When this distance is increased or decreased from an optimum of 5 nt (or ∼17 Å), the 30S complex becomes distorted, resulting in a decreased"* initiation rate; stretched spacings follow *"ΔGspacing=c1(s−sopt)2+c2(s−sopt), where sopt = 5 nt"*.
  - **Standby site:** *"The ΔGstandby is the work required to unfold any secondary structures sequestering the standby site (ΔGstandby < 0) after 30S complex assembly. We define the standby site as the 4 nucleotides upstream of the 16S r"*RNA binding site.
  - Accuracy of the original: *"Experimental validation of over 100 predictions in Escherichia coli shows that the method is accurate to within a factor of 2.3 over a range of 100,000-fold."*
  - **Context dependence — the reason the notebook screens UTRs in their real CDS context:** *"The design method also correctly predicts that reusing a ribosome binding site sequence in different genetic contexts can result in different protein expression levels."*
  - Folding window: the subsequences folded are *"the nucleotides nstart − 35 to n3 − 4 and n3 to nstart + 35"*.
- **File:** `Salis_2009_RBS_calculator_synthetic_ribosome_binding_sites.txt` (no PDF — PMC author manuscript XML)

---

## Lobinska, Pilpel & Nowak 2023 — Evolutionary safety of lethal mutagenesis driven by antiviral treatment
- **Authors:** Gabriela Lobinska, Yitzhak Pilpel (Weizmann, Dept. Molecular Genetics), Martin A. Nowak (Harvard)
- **Year:** 2023
- **Journal:** PLoS Biology 21(8):e3002214
- **DOI:** 10.1371/journal.pbio.3002214
- **Retrieved:** 2026-09-17 (PLoS open-access PDF, `pdftotext -layout`).
- **Cited in context of:** INSERM IRP 2026 proposal, ref `[26]` — Pilpel's evolutionary-safety formalism as the basis of the proposal's ethics/safety framing, and as a Weizmann-side asset for assessing whether mutation-rate-increasing interventions can generate variants of concern.
- **Key content verified (direct quotes):**
  - Definition: *"We define evolutionary safety as a probabilistic assurance that the treatment will not generate an increased number of mutants."*
  - Method: *"We develop a mathematical framework to estimate the total mutant load produced with and without mutagenic treatment."*
  - Case study and verdict: *"We focus on the case study of Molnupiravir, which is an FDA-approved treatment against Coronavirus Disease-2019 (COVID-19). We estimate that Molnupiravir is narrowly evolutionarily safe, subject to the current estimate of parameters."*
  - Generality: *"We report a simple mathematical rule to determine the fold increase in mutation rate required to obtain evolutionary safety that is also applicable to other pathogen-treatment combinations."*
  - Mitigation levers: safety *"can be improved by restricting treatment with this drug to individuals with a low immunological clearance rate and, in future, by designing treatments that lead to a greater increase in mutation rate."*
- **File:** `Lobinska_2023_evolutionary_safety_lethal_mutagenesis.txt` (PDF: `../agent_papers/Lobinska_2023_evolutionary_safety_lethal_mutagenesis.pdf`)

---

## Lobinska, Tretyachenko, Dahan, Nowak & Pilpel 2024 — The evolutionary safety of mutagenic drugs should be assessed before drug approval
- **Authors:** Gabriela Lobinska, Vyacheslav Tretyachenko, Orna Dahan (Weizmann), Martin A. Nowak (Harvard), Yitzhak Pilpel (Weizmann)
- **Year:** 2024
- **Journal:** PLoS Biology 22(3):e3002570 — **Perspective**, not a research article
- **DOI:** 10.1371/journal.pbio.3002570
- **Retrieved:** 2026-09-17 (PLoS open-access PDF, `pdftotext -layout`).
- **Cited in context of:** INSERM IRP 2026 proposal, ref `[27]` — the policy companion to `[26]`; supports the affirmative safety case for a platform that deliberately elevates mutation rates.
- **Key content verified (direct quotes):**
  - Thesis: *"Some drugs increase the mutation rate of their target pathogen, a potentially concerning mechanism as the pathogen might evolve faster toward an undesired phenotype. We suggest a four-step assessment of evolutionary safety for the approval of such treatments."*
  - Risk framing: *"Mutations in pathogens are concerning. They can cause increased virulence or transmissibility, or resistance to therapy or vaccination."*
  - Mechanism is population-level: *"If the increase in mutation rate is sufficient, the pathogen can acquire a lethal dosage of mutations, triggering an error catastrophe that prevents adaptation or reduces the basic reproductive ratio to below one… Hence, the mechanism of action of mutagenic drugs is based on a population process."*
  - Relates error threshold to *"Muller's ratchet or mutational meltdown."*
  - Balanced stance: *"Mutagenic drugs are problematic, but resistance to antibiotics and antivirals present an urgent need for new drug development. We should thus explore every mechanism of drug action that has any chance of success."*
- **File:** `Lobinska_2024_evolutionary_safety_mutagenic_drugs_approval.txt` (PDF: `../agent_papers/Lobinska_2024_evolutionary_safety_mutagenic_drugs_approval.pdf`)

---

## Khare et al. 2021 — GISAID's Role in Pandemic Response
- **Authors:** Shruti Khare, Céline Gurry, Lucas Freitas, Mark B. Schultz, … Sebastian Maurer-Stroh (GISAID; A*STAR Bioinformatics Institute; FIOCRUZ; Institut Pasteur de Dakar; et al.)
- **Year:** 2021
- **Journal:** China CDC Weekly 3(49):1049–1051
- **DOI:** 10.46234/ccdcw2021.255 · **PMCID:** PMC8668406
- **Retrieved:** 2026-09-17 (Europe PMC `fullTextXML` for PMC8668406, JATS → text; publisher PDF link returned HTML). No PDF in `agent_papers/`.
- **Cited in context of:** INSERM IRP 2026 proposal, ref `[16]` — resolves the draft's `[missing REF]` for "benchmarked against GISAID surveillance data". Chosen over Elbe & Buckland-Merrett 2017 because it is the SARS-CoV-2/EpiCoV-specific description.
- **Key content verified (direct quotes):**
  - Scope: *"GISAID is a global data science initiative and the primary source of genomic and associated metadata of all influenza viruses, Respiratory Syncytial Virus (RSV) and severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)."*
  - Scale: *"over 42,000 participating researchers from 198 nations and data generators from over 3,500 institutions"*; *"over 5 million genetic sequences of SARS-CoV-2 from 194 countries and territories have been made publicly available through GISAID's EpiCoV database as of November 9, 2021."*
  - Variant surveillance — the capability the proposal benchmarks against: *"Tracking the distribution of emerging variants like the Variant of Concern (VOC) Delta (B.1.617.2 and AY lineages) across the globe along with estimation of country-wise prevalence are made possible via GISAID."*
  - Curation: *"all submitted data are reviewed and curated in real-time and annotated by a global team of curators, prior to release."*
  - Database launch dates: *"GISAID's EpiFlu database was launched in May 2008, its EpiCoV database in January 2020 and its EpiRSV database in June 2021."*
- **File:** `Khare_2021_GISAID_role_pandemic_response.txt` (no PDF — Europe PMC JATS XML)

---

## Elbe & Buckland-Merrett 2017 — Data, disease and diplomacy: GISAID's innovative contribution to global health
- **Authors:** Stefan Elbe, Gemma Buckland-Merrett (Centre for Global Health Policy, University of Sussex)
- **Year:** 2017
- **Journal:** Global Challenges 1(1):33–46
- **DOI:** 10.1002/gch2.1018 · **PMID:** 31565258 · **PMCID:** PMC6607375
- **Retrieved:** 2026-09-17 (Europe PMC `fullTextXML` for PMC6607375, JATS → text; Wiley pdfdirect returned HTML). No PDF in `agent_papers/`.
- **Cited in context of:** INSERM IRP 2026 proposal — the **alternative** GISAID citation to `[16]`, for a data-sharing-policy rather than SARS-CoV-2 framing. Not used in the current draft.
- **Key content verified (direct quotes):**
  - Framing: *"The international sharing of virus data is critical for protecting populations against lethal infectious disease outbreaks."*
  - Method: *"Based on more than 20 semi-structured interviews conducted with key informants in the international community."*
  - The five contributions: *"(1) collating the most complete repository of high-quality influenza data in the world; (2) facilitating the rapid sharing of potentially pandemic virus information during recent outbreaks; (3) supporting the World Health Organization's biannual seasonal flu vaccine strain selection process; (4) developing informal mechanisms for conflict resolution around the sharing of virus data; and (5) building greater trust with several countries key to global pandemic preparedness."*
  - **Note:** the initial PMCID guess (PMC5607544) was wrong — it resolves to an unrelated stroke/visual-impairment paper. Correct PMCID confirmed as PMC6607375 via Europe PMC DOI search.
- **File:** `Elbe_2017_GISAID_data_disease_diplomacy.txt` (no PDF — Europe PMC JATS XML)

---

## Messier & Stewart 1997 — Episodic adaptive evolution of primate lysozymes
- **Authors:** Walter Messier, Caro-Beth Stewart (Department of Biological Sciences, University at Albany, SUNY)
- **Year:** 1997
- **Journal:** Nature 385(6612):151–154
- **DOI:** 10.1038/385151a0 · **PMID:** 8990116
- **Retrieved:** 2026-09-17 (Sci-Hub mirror `sci-hub.ee` → `sci.bban.top` PDF; scanned original, **OCR'd** with tesseract at 400 dpi via PyMuPDF rasterisation). Unpaywall: closed, no OA copy; not in Europe PMC (`inEPMC: N`).
- **Cited in context of:** HEWL/HEL grant rewrite (replacing SARS-CoV-2 RBD with a non-pathogen model antigen) — the rigorous demonstration that **lysozyme is a genuine natural target of episodic positive Darwinian selection**, i.e. that the HEWL benchmark is not merely a convenient lab antigen but a protein with a documented adaptive-evolution history. Supplies the "affinity/function under selection" framing without any pathogen.
- **Key content verified (direct quotes, OCR'd):**
  - Design: *"Here we combine tests of neutral rate violation with reconstruction of ancestral sequences to document an episode of positive selection on the lineage leading to the common ancestor of the foregut-fermenting colobine monkeys. This analysis also detected a previously unsuspected adaptive episode on the lineage leading to the common ancestor of the modern hominoid lysozymes. Both adaptive episodes were followed by episodes of negative selection."*
  - **Colobine episode:** *"This ancestral analysis of Ka and Ks pinpointed an episode of adaptive lysozyme sequence evolution (Ka/Ks = 4.7; P < 0.05) on the ancestral colobine lineage"* (between nodes OW and Co, Fig. 2) — *"This period corresponds to the time in evolutionary history when lysozyme was most likely to have been recruited to digest foregut bacteria in the true stomachs of colobine monkeys."*
  - **Hominoid episode:** *"This analysis also identified an episode of positive selection (Ka/Ks = 5.1; P < 0.05) on the ancestral hominoid lineage (between nodes Ca and Ho in Fig. 2) that was not anticipated by previous analyses."* No adaptive explanation offered; *"it might be related to increased neutrophil expression of lysozyme in hominoids as compared with other catarrhines."*
  - **Number of adaptive substitutions (the figure requested):** *"maximum-likelihood analysis suggests that there were nine amino-acid replacements during the brief adaptive episode on the ancestral colobine lineage (Fig. 2), five of which are among those originally identified to have occurred in parallel or convergently along the lineage leading to cow and other ruminant stomach lysozymes."* → **9 replacements (colobine), 5 of them shared with the ruminant convergence set.**
  - *"Similarly, maximum-likelihood analysis suggests that seven amino-acid replacements occurred during the adaptive episode on the ancestral hominoid lysozyme lineage (Fig. 2)."* → **7 replacements (hominoid).**
  - **Negative control:** *"During a similar period along the ancestral cercopithecine lineage, only two amino-acid replacements are reconstructed."* The cercopithecine ancestral lineage Ka/Ks *"is not significantly different from neutral expectation"*; cercopithecines *"can serve as closely related 'negative controls'."*
  - Between-group averages: colobines vs cercopithecines **Ka/Ks = 3.0 (P < 0.05)**; colobines vs hominoids **Ka/Ks = 3.0** (individual range 1.33–3.49); cercopithecines vs hominoids **Ka/Ks = 2.7 (P < 0.05)** (range 1.02–3.28) — *"among the highest known for any whole protein."*
  - Purifying selection afterwards: *"all within-group averages of catarrhine lysozymes show Ka/Ks ratios less than 1.0."*
  - Robustness: intron 3 was sequenced to exclude suppressed synonymous substitution — *"the high Ka/Ks ratios for the catarrhine lysozymes cannot be explained by significant suppression of synonymous substitutions in this gene."*
  - Maximum-parsimony ranges (Fig. 2 caption): Ca to Ho, 3.0–5.9\*; OW to Co, 1.5–5.3\*; OW to Ce, 0.56–2.3 (not significant).
  - ⚠️ OCR artefact to be aware of when re-reading the `.txt`: `Ka` and `Ks` render variously as `K,`/`K,`/`Kg`/`K₈`, and one instance of the colobine-vs-hominoid significance prints as `P > 0.05` where the surrounding text and Fig. 2 asterisks indicate `P < 0.05`. Verify against the PDF before quoting a P value.
- **File:** `Messier_Stewart_1997_episodic_adaptive_evolution_primate_lysozymes.txt` (PDF: `../agent_papers/Messier_Stewart_1997_episodic_adaptive_evolution_primate_lysozymes.pdf`)

---

## Stewart, Schilling & Wilson 1987 — Adaptive evolution in the stomach lysozymes of foregut fermenters
- **Authors:** Caro-Beth Stewart, James W. Schilling, Allan C. Wilson (UC Berkeley Biochemistry; California Biotechnology Inc.)
- **Year:** 1987
- **Journal:** Nature 330(6146):401–404
- **DOI:** 10.1038/330401a0 · **PMID:** 3120013
- **Retrieved:** 2026-09-17 (Sci-Hub mirror `sci-hub.ee` → `sci.bban.top` PDF; scanned original, **OCR'd** with tesseract at 400 dpi). Unpaywall: closed, no OA copy; not in Europe PMC.
- **Cited in context of:** HEWL/HEL grant rewrite — the original **convergent sequence evolution** claim for lysozyme (cow vs langur stomach lysozyme). The paper Messier & Stewart 1997 later put on a statistical footing; together they are the "lysozyme is an evolutionarily live target" pair. Also the source of the *functional* convergence argument (independent recruitment of lysozyme to a digestive role in two mammalian lineages).
- **Key content verified (direct quotes, OCR'd):**
  - Abstract/framing: *"The convergent evolution of a fermentative foregut in two groups of mammals offers an opportunity to study adaptive evolution at the protein level. The appearance of this mode of digestion has been accompanied by the recruitment of lysozyme as a bacteriolytic enzyme in the stomach both in the ruminants (for example the cow) and later in the colobine monkeys (for example the langur)."*
  - The convergence claim: *"Tree analysis suggests that, after foregut fermentation arose in monkeys, the langur lysozyme gained sequence similarity to cow stomach lysozyme and evolved two times faster than the other primate lysozymes. This rapid evolution, coupled with functional and sequence convergence upon cow stomach lysozyme, could imply that positive darwinian selection has driven about 50% of the evolution of langur stomach lysozyme."*
  - **Number of convergent substitutions (the figure requested):** *"five homoplastic replacements (producing Lys 14, Lys 21, Glu 50, Asp 75 and Asn 87 in cow and langur lysozymes) were found to occur along the cow and langur lineages. This number is significantly greater (χ² test, P > 0.95) than the number (0 or 1) of homoplastic replacements found to occur along the other pairs of lineages. Therefore, these five amino-acid replacements are unlikely to have occurred by chance (that is, neutral drift) alone."* → **5 homoplastic (convergent/parallel) replacements: Lys14, Lys21, Glu50, Asp75, Asn87.**
  - Two further parallel events elsewhere on the tree: *"two replacements (producing Leu 17 and Ser 101) appear to have occurred in parallel along the lineage leading to cow and along the lineage leading to the Old World monkeys (baboon and langur)."*
  - Stomach-lysozyme-diagnostic residues: *"Four of the resulting amino acids (Lys 21, Glu 50, Asp 75 and Asn 87) are found only in colobine and ruminant stomach lysozymes (Table 1)."*
  - Parallel vs convergent mechanism: *"Lys 14 and Glu 50 may have been the result of convergent replacements, while the others appear to have been in parallel."*
  - Rate: *"langur lysozyme appears to have evolved about twice as fast as the other primate lysozymes (Fig. 3)"*; *"half or more of the replacements along the langur lysozyme lineage"* made it more cow-like, whereas *"baboon and human lysozymes followed normal divergent paths."*
  - Gene duplication excluded: *"gene duplication is unlikely to explain the link between cow and langur stomach lysozymes"* — the sequences *"are the products of equivalent (orthologous) genes."*
  - Statistical support for shared residues: *"The number of uniquely shared residues between cow and langur is significantly greater than average (χ² test, P > 0.95)."*
  - Novelty framing (useful for a grant intro): *"the well-characterized cases of functional convergence in proteins are not the result of convergent sequence evolution. Haemoglobin and haemocyanin, for example, are functionally convergent but these two types of protein exhibit no sequence similarity."*
  - ⚠️ OCR note: χ² renders as `x*`/`x°`/`x²` and the paper's own convention prints the χ² significance as `P > 0.95` (a confidence level, not a p-value) — quote it as written and gloss it, don't silently convert to `P < 0.05`.
- **File:** `Stewart_1987_adaptive_evolution_stomach_lysozymes_foregut_fermenters.txt` (PDF: `../agent_papers/Stewart_1987_adaptive_evolution_stomach_lysozymes_foregut_fermenters.pdf`)

---

## Leysen et al. 2011 — Molecular basis of bacterial defense against host lysozymes: X-ray structures of periplasmic lysozyme inhibitors PliI and PliC
- **Authors:** S. Leysen, J. M. Van Herreweghe, L. Callewaert, M. Heirbaut, P. Buntinx, C. W. Michiels, S. V. Strelkov (KU Leuven — Biocrystallography; Food Microbiology)
- **Year:** 2011
- **Journal:** J Mol Biol 405(5):1233–1245
- **DOI:** 10.1016/j.jmb.2010.12.007 · **PMID:** 21146533
- **Retrieved:** 2026-09-17 (Sci-Hub mirror `sci-hub.ee` → `sci.bban.top` PDF; born-digital, clean PyMuPDF text extract). Unpaywall: closed, no OA copy.
- **Cited in context of:** HEWL/HEL grant rewrite — **the load-bearing paper for the experimental design.** Establishes (a) the census of bacterial lysozyme-inhibitor families, and (b) that these inhibitors work by **occluding the lysozyme catalytic cleft**, engaging the catalytic residues Glu35/Asp52 of HEWL directly. Any design that selects binders against HEWL's active-site cleft is therefore recapitulating a real, structurally characterised natural binding mode — and, conversely, any HEWL-displaying construct must expect active-site-directed competition.
- **Key content verified (direct quotes):**
  - **Family census — four families, not three.** Abstract: *"So far, three lysozyme inhibitor families have been described: the Ivy (inhibitor of vertebrate lysozyme) family, the MliC/PliC (membrane-associated/periplasmic lysozyme inhibitor of C-type lysozyme) family, and the PliI (periplasmic lysozyme inhibitor of I-type lysozyme) family."* The Introduction updates this: *"Currently, four distinct families of lysozyme inhibitors have been described"* — Ivy, PliC/MliC, **PliI** (I-type), and **PliG** (G-type, *"periplasmic lysozyme inhibitor of G-type lysozyme"*). All *"have been identified only in Gram-negative bacteria, either in the periplasm or anchored to the luminal face of the outer membrane."*
  - **ACTIVE-SITE BINDING — Ivy:** *"The latter structures show that Ivy-Ec and Ivy-Pa inhibit HEWL by a key-lock mechanism where a conserved CKPHDC loop occupies the enzyme's active site."* (Structures: Ivy-Ec alone PDB **1XS0**; Ivy-Ec and Ivy-Pa in complex with HEWL PDB **1GPQ** and **1UUZ**.) → **Yes: a loop inserts into the lysozyme active site.**
  - **ACTIVE-SITE BINDING — MliC/PliC:** *"MliC-Pa inhibits HEWL by a double key-lock mechanism in which two conserved regions occupy the active site of HEWL."* (MliC-Pa–HEWL complex PDB **3F6Z**; MliC-Ec NMR structure PDB **2F09**.)
  - **The catalytic residues are contacted directly** — the sharpest form of the load-bearing fact: *"Specifically, MliC-Pa Ser89 in CS1 forms a hydrogen bond with HEWL Asp52 and MliC-Pa Lys103 in CS2 forms ionic interactions with HEWL Asp52 and Glu35. In addition, MliC-Pa Tyr93 in CS1 and MliC-Pa Thr102 in CS2 accommodate a loop of HEWL by forming hydrogen bonds with Thr47 of HEWL."* (Glu35 and Asp52 are HEWL's two catalytic residues.) CS1 sits *"in loop 4 and the beginning of strand β5"*, CS2 *"in strand β6"*. *"Sequence comparison showed that CS1 and CS2 are present in PliC-St as well."*
  - **ACTIVE-SITE BINDING — PliI:** *"Site-directed mutagenesis suggests that the inhibitory action of PliI-Ah proceeds via an insertion of a loop containing the conserved SGxY motif into the active center of I-type lysozymes. This motif is related to the functional SGxxY motif found in the MliC/PliC family."* Confirmed in the Discussion: *"site-directed mutagenesis experiments suggests that upon inhibition of I-type lysozyme, the conserved SGxY motif is inserted in the catalytic site."* Mutants tested against *Tapes japonica* lysozyme (TjL): S104A, Y107A, S104A/Y107A.
  - New structures reported here: **PliC-St** (*Salmonella typhimurium*, first structure of a periplasmic member of the PliC/MliC family) and **PliI-Ah** (*Aeromonas hydrophila*, first structure in the PliI family). SAXS shows *"both PliC-St and PliI-Ah form stable dimers in solution"*; *"The functional dimer architecture of PliC-St is very different from that of the recently described MliC from Pseudomonas aeruginosa (MliC-Pa), despite the close resemblance of their monomers."*
  - Physiological role and the permeabilisation caveat: *"Gram-negative bacteria produce various types of lysozyme inhibitors that allow them to survive the bactericidal action of lysozyme when their outer membrane is permeabilized"*; *"knockout studies show that they protect bacteria against lysozyme when their outer membrane is permeabilized."*
  - Specificity spread: Ivy proteins are *"mainly active against C-type lysozymes; however, Ivy also shows some activity against goose egg white lysozyme and, to a lesser extent, against T4 lysozyme."*
- **File:** `Leysen_2011_lysozyme_inhibitors_PliI_PliC_structures.txt` (PDF: `../agent_papers/Leysen_2011_lysozyme_inhibitors_PliI_PliC_structures.pdf`)

---

## Monchois, Abergel, Sturgis, Jeudy & Claverie 2001 — Escherichia coli ykfE ORFan gene encodes a potent inhibitor of C-type lysozyme
- **Authors:** Vincent Monchois, Chantal Abergel, James Sturgis, Sandra Jeudy, Jean-Michel Claverie (Information Génétique et Structurale, UMR1889 CNRS-AVENTIS, Marseille)
- **Year:** 2001
- **Journal:** J Biol Chem 276(21):18437–18441
- **DOI:** 10.1074/jbc.M010297200 · **PMID:** 11278658
- **Retrieved:** 2026-09-17 (Sci-Hub mirror `sci-hub.ee` → `sci.bban.top` PDF). Unpaywall reports `is_oa: true` with a publisher PDF at `jbc.org/article/S0021925819317922/pdf`, but that URL returns **HTTP 403** (Cloudflare) to a scripted fetch, so the Sci-Hub route was used instead.
- **Cited in context of:** HEWL/HEL grant rewrite — the **Ivy discovery paper**: the primary citation for "*E. coli* carries a periplasmic, nanomolar inhibitor of C-type lysozyme". Needed because displaying or secreting HEWL from *E. coli* happens in the presence of an endogenous high-affinity competitor.
- **Key content verified (direct quotes):**
  - **Name and assignment:** *"To denote this newly assigned function, ykfE has now been registered under the new gene name Ivy (inhibitor of vertebrate lysozyme) at the E. coli genetic stock center."* → **Ivy = Inhibitor of vertebrate lysozyme.** Gene `ykfE` = Swiss-Prot **P45552**, `b0220` in the Blattner database, a 474-nucleotide ORF, *"part of a single gene operon"*, cloned from *E. coli* K-12 MG1655.
  - **Periplasmic:** *"The ykfE ORF exhibits an N-terminal signal peptide cleaved to produce the mature protein"*; *"The presence of a signal peptide predicted a periplasmic location for its protein product, which is now consistent with its newly assigned function."* Mature Ivy = **15.04 kDa**.
  - **Potency (the figure requested):** *"Activity measurements and fluorescence studies demonstrated that the YkfE gene product is a potent C-type lysozyme inhibitor (Ki ≈ 1 nM)."* Repeated in Results: *"A Ki value of about 1 nM was thus estimated by fitting the experimental data (Fig. 4) with Morrison's equation."* Assay: HEWL (70 nM) pre-incubated with Ivy (0–200 nM), *Micrococcus lysodeikticus* cell walls as substrate.
  - **Kinetic mechanism — competitive, but NOT structurally resolved here:** *"Ki value was determined according to the slow tight binding competitive inhibition model (with no conformational change)"*; *"indicating that Ivy behaves as a slow tight binding inhibitor."* Inhibition is stoichiometric: the homodimer *"strongly interacts with hen and human, and probably all C-type lysozymes, thereby abrogating their activity in a stoichiometric manner."*
  - ⚠️ **Binding mode is NOT established by this paper.** On the specific question "does a loop insert into the lysozyme active site?", the 2001 text says only that the structure was pending: *"The x-ray structure determination of ykfE, both in isolation (7) and in a complex with HEWL, is currently in progress and should allow us to understand the molecular basis of the ykfE-lysozyme interaction at atomic resolution."* The competitive-inhibition kinetics are consistent with active-site occlusion but do not demonstrate it. **For the loop-into-active-site claim, cite Leysen et al. 2011 (which reports it for Ivy-Ec/Ivy-Pa as the CKPHDC loop, PDB 1GPQ/1UUZ) rather than Monchois 2001.**
  - Oligomeric state: *"Under physiological conditions, the protein is a homodimer with a strong affinity for C-type lysozyme, as revealed by co-purification and co-crystallization"*; gel filtration gives *"an apparent molecular mass of about 30 kDa"*; *"these biophysical results suggest that the Ivy homodimer is the physiologically active unit"*, with dimerisation Kd *"much lower than 10⁻⁹ M."*
  - **Specificity:** strong inhibition of HEWL and of human salivary lysozyme (*"Around 50 µg/ml of Ivy is sufficient to observe a decrease of 50% of the activity, which was fully abolished for an Ivy concentration of 0.5 mg per ml of saliva"*). Weak against λ phage lysozyme: *"The activity was only reduced by 15% at a molar ratio of 200:1, Ivy:λ phage lysozyme."* No effect on chitinase: *"We found no inhibitory effect of Ivy on chitinase from S. griseus."*
  - Authors' own caveat on physiological role: *"for Gram-negative bacteria such as E. coli, the presence of an outer membrane impermeable to molecules larger than 0.6 kDa should be sufficient to protect the peptidoglycan moiety from the lysozymes present in the medium."*
- **File:** `Monchois_2001_ykfE_Ivy_inhibitor_C_type_lysozyme.txt` (PDF: `../agent_papers/Monchois_2001_ykfE_Ivy_inhibitor_C_type_lysozyme.pdf`)

---

## Maenaka, Furuta, Tsumoto, Watanabe, Ueda & Kumagai 1996 — A stable phage-display system using a phagemid vector: phage display of hen egg-white lysozyme (HEL), *Escherichia coli* alkaline phosphatase, and anti-HEL monoclonal antibody, HyHEL10
- **Authors:** Katsumi Maenaka, Masaru Furuta, Kouhei Tsumoto, Kimitsuna Watanabe, Yoshitaka Ueda, Izumi Kumagai (Tohoku University; University of Tokyo)
- **Year:** 1996 (received 8 December 1995)
- **Journal:** Biochem Biophys Res Commun 218(3):682–687, article no. 0122
- **DOI:** 10.1006/bbrc.1996.0122 · **PMID:** 8579574
- **Retrieved:** 2026-09-17 (Sci-Hub mirror `sci-hub.ee` → `sci.bban.top` PDF, via DOI; a PMID-only Sci-Hub query failed on all ten mirrors tried). Unpaywall/Europe PMC: closed, not in PMC.
- **⚠️ Attribution correction:** this is the **pLUCK phagemid** paper, but its authors are **Maenaka et al.**, not Iba et al. (Iba/Kurosawa wrote the separate CDR-diversification vector papers). Cite as Maenaka K, Furuta M, Tsumoto K, Watanabe K, Ueda Y, Kumagai I (1996) *Biochem Biophys Res Commun* 218:682–687.
- **Cited in context of:** HEWL/HEL grant rewrite — the precedent that **HEL can be functionally displayed as a pIII fusion on filamentous phage**, and the source of the caveat that doing so requires *repressed* expression because HEL lyses the *E. coli* host. Directly relevant to any phage/phagemid-based HEL display or selection cycle.
- **Key content verified (direct quotes):**
  - **Functional pIII display of HEL confirmed:** *"A phagemid pIII display vector, pLUCK, was constructed by inserting the gene encoding the pIII fusion protein in the opposite direction to that of the lac promoter of pTZ18U. Using this phage display system, two enzymes, hen egg-white lysozyme (HEL) and E. coli alkaline phosphatase, and the single-chain Fv fragment of anti-HEL monoclonal antibody HyHEL10, could be stably and functionally displayed."*
  - **Correct folding of the active-site region — the strongest form of "functional":** *"Phage-HEL was found to bind to both the polyclonal antibody and the scFv of the monoclonal antibody HyHEL10. According to X-ray crystallographic analysis of the HyHEL10-HEL complex, HyHEL10 recognizes a conformational epitope of HEL which contains a part of the active site of HEL. Therefore, it was concluded that HEL displayed on the phage possessed a well-refolded structure, especially in the region surrounding the active site."*
  - **The toxicity problem, stated explicitly:** *"Since HEL is a lytic enzyme for E. coli cells, our novel system is believed to have considerable potential for displaying toxic proteins."* And on the display instability that motivated the design: *"(1) the negative effect of the overexpression of displayed fusion proteins on the maintenance of phagemid vectors (deletion of the toxic gene often occurs) and on the growth of E. coli cells, (2) the low display efficiency… and (3) the poor reproducibility of the display condition."*
  - **Conventional (sense-orientation) display of HEL FAILED:** the earlier Hoogenboom et al. (1991) architecture *"could not stably display the pIII-fusion protein in the cases of trypsin, some antibodies (Tsumoto et al., unpublished results), and hen egg-white lysozyme (shown in the present study)."* Confirmed in Results: *"the phage from pLLZR, in which the geneIII-fused HEL gene was inserted just downstream of the lac promoter in the sense orientation, could not stably and efficiently display HEL."* Same for the scFv: *"the one from pLFVR could not."* → **HEL display works only with the repressed, antisense-orientation construct.**
  - **Expression level — the trade-off, quantified on AP:** the design works *because* expression is low. *"the AP activity of the phage fraction recovered in the former system (ours) was less than that in the latter (the system of Hoogenboom et al.)… This might be due to lower production of the recombinant phage in the pLAP/JM109 system, in which the expression of the mRNA encoding the pIII-fusion protein is repressed."* Table 1: pLAP/JM109 **6.48** vs pLAPR/JM109 **99.6** pmol/min per 100 ml culture (negative phage 0.33) → roughly **15-fold lower display/activity yield**. Authors concede: *"the results obtained indicate that the display in our system is less efficient than that in the previously reported one, it should be noted that a repressed display of this type might enable the stable display of toxic proteins against the growth of E. coli cells."*
  - Mechanism of the repression: *"an mRNA over 4kb in size encoding the HEL-pIII fusion protein is expressed and that the transcriptional starting point is situated in the C-terminal coding region of pIII, which was identified as the promoter for geneVI"*; *"it is possible that the sense mRNA encoding the wild-type and fusion pIIIs can both be repressed by the larger amount of anti-sense RNA which may be expressed under the control of the strong lac promoter."*
  - Construct details for reuse: pLUCK = pelB Shine-Dalgarno + signal peptide → target protein → **c-myc linker (AAAEQKLISEEDLNLP)** → C-terminal domain of geneIII (**pIII residues 198–406**), inserted between KpnI and HindIII of pTZ18U *"in the reverse direction to that of the lac and T7 promoters"*. Target gene cloned **NcoI–NotI**. Derivatives: **pLLZ** (HEL), **pLAP** (alkaline phosphatase), **pLFv** (HyHEL10 scFv); sense-orientation controls **pLLZR/pLAPR/pLFvR** in pTZ19U. Host *E. coli* **JM109**, helper phage **M13KO7** (> 5 × 10¹¹ pfu/ml), kanamycin 50 µg/ml, PEG precipitation.
  - Claim of priority: *"This is the first report of the successful stable display of an enzyme on a filamentous phage (phage-enzyme) using the phagemid pIII display system."*
- **File:** `Maenaka_1996_pLUCK_phagemid_display_HEL_HyHEL10.txt` (PDF: `../agent_papers/Maenaka_1996_pLUCK_phagemid_display_HEL_HyHEL10.pdf`)

---

## Liu, Makova, Adkins, Gibson & Li 2001 — Episodic evolution of growth hormone in primates and emergence of the species specificity of human growth hormone receptor
- **Authors:** Jaw-Ching Liu, Kateryna D. Makova, Ronald M. Adkins, Susan Gibson, Wen-Hsiung Li (UT-Houston; University of Chicago; UMass-Amherst; University of South Alabama)
- **Year:** 2001 (accepted 30 January 2001)
- **Journal:** Mol Biol Evol 18(6):945–953
- **DOI:** 10.1093/oxfordjournals.molbev.a003895 · **PMID:** 11371582
- **Retrieved:** 2026-09-18 (Sci-Hub mirror `sci-hub.al` → `sci.bban.top` PDF, via DOI; the direct fetch needed `--resolve sci.bban.top:443:188.114.96.2` because the local resolver blackholes that host to 127.0.0.1). Unpaywall/Europe PMC: closed, not in PMC. Born-digital, clean PyMuPDF extract — **full text read**, not abstract only.
- **Cited in context of:** [Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md](../Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md) — documenting **human growth hormone (hGH) as a REJECTED alternative model antigen**. hGH's headline attraction was "fast-evolving in primates, classic adaptive-evolution literature". This paper is the primary source for that claim, and it **materially weakens it** — see the caveats below before citing hGH as an adaptive-evolution exemplar.
- **⚠️ The load-bearing co-evolution claim is only weakly supported by this paper.** Read the caveats before using it.
- **Key content verified (direct quotes):**
  - **Episodic rapid evolution — CONFIRMED, and dated.** Abstract: *"Our data showed that the rapid evolution of primate GH occurred during a relatively short period (in the common ancestor of higher primates) and that the rate of change was especially high at functionally important sites, suggesting positive selection."* Discussion: *"it is clear that the evolution of GH in primates was episodic, revealing a low rate in most prosimians and an extremely high rate in the common ancestor of higher primates, but subsequently a much lower rate in extant higher primates."* The burst is on **branch s**, between the tarsier/simian split and the simian common ancestor: *"the synonymous and nonsynonymous rates in branch s are 7 and 12 times as high as the respective average rates in mammals!"* (9.0 × 10⁻⁹ nonsynonymous, 25.1 × 10⁻⁹ synonymous substitutions/site/year vs mammalian averages of 0.74 × 10⁻⁹ and 3.5 × 10⁻⁹). Divergence scale: *"human GH sequence differs from the inferred ancestral sequence by 59 amino acids"* while *"most nonprimate GHs differ from each other by only 0–4 amino acids in the mature peptide"* — a **~33% difference**.
  - **⚠️ POSITIVE SELECTION IS NOT DEMONSTRATED — dN/dS < 1 throughout.** This is the correction. Abstract: *"However, the nonsynonymous rate/synonymous rate ratio at these sites was <1, so relaxation of purifying selection might have played a role in the rapid evolution of the GH gene in simians, possibly as a result of multiple gene duplications."* Results: *"in the ancestral simian lineage (branch s), the dN/dS ratio (ωS = 0.354) is significantly elevated compared with the rates in the other lineages under study (ω0 = 0.081), but it is still <1, providing no evidence for positive selection."* And: *"A maximum-likelihood selection model with heterogeneous dN/dS ratios among sites did not identify any sites with dN/dS > 1 in GH."* Conclusion: *"the dN/dS ratio was found to be <1 for the GH gene and for the functionally important sites of the gene, not giving support for positive selection."* → Cite this paper for **episodic rate acceleration**, not for "positive selection on GH". The positive-selection language in the abstract is explicitly hedged ("suggesting", "might have been adaptive").
  - **GHR species specificity — the mechanism, exactly.** *"Human GH has a high affinity for nonprimate GHRs, but nonprimate GHs have about 3,000-fold lower affinity for human GHR than does human GH (Souza et al. 1995)! Correspondingly, nonprimate GHs fail to stimulate GHR, and consequently, growth, in the rhesus monkey (Carr and Friesen 1976). This phenomenon is called 'species-specificity' of human GHR."* Structural basis: *"The species specificity of human GHR is primarily due to the Leu→Arg change at position 43 of GHR, leading to an unfavorable charge repulsion/steric hindrance between Arg43 of human GHR and His170 of nonprimate GHs (Souza et al. 1995; Behncken et al. 1997). In contrast, human GHR has a high affinity for human GH because the His→Asp change at position 171 (position 170 in nonprimate GHs) forms a favorable salt bridge with Arg43."*
  - **The ORDER of the two changes — the paper's main positive result.** *"Our sequence data of GH genes from three lemurs and two tarsiers revealed His at position 171 of GH… In contrast, our sequence data of GH genes from two New World (NW) monkeys, two Old World (OW) monkeys, and two apes revealed Asp at position 171… These data clearly indicated that the His171Asp replacement in GH occurred in the common ancestor of simians."* And: *"the Leu43Arg replacement in GHR occurred in the common ancestor of OW monkeys, apes, and humans… As this common ancestor is about 15 Myr younger than the common ancestor of simians (Goodman et al. 1998), the His171Asp change in GH obviously preceded the Leu43Arg change in GHR."* Abstract: *"the species specificity of human GHR actually emerged in the common ancestor of Old World primates, but the transitional phase still persists in New World monkeys."*
  - **⚠️ LIGAND–RECEPTOR CO-EVOLUTION — the weakest link. Quote it exactly, with its qualifier.** The paper asserts co-evolution only at the level of **correlated overall tempo**, and explicitly reports that **site-by-site co-evolution at the contact interface did NOT happen**. Abstract: *"Similar to GH, GHR displayed an accelerated rate of evolution in primates. Our data revealed proportionally more amino acid replacements at the functionally important sites in both GH and GHR in simians but, surprisingly, showed few coincidental replacements of amino acids forming the same intermolecular contacts between the two proteins."* Results: *"Of 13 intermolecular contacts (de Vos, Ultsch, and Kossiakoff 1992), only one has been changed at both GH and GHR in the human and the macaque. This is an interaction between sites 171 (GH) and 43 (GHR)… Thus, the majority of the changes at functionally important sites in simian GH are not at the sites that interact with the changed sites in simian GHR."* Discussion: *"An accelerated rate of GH evolution in the common ancestor of the NW and OW monkeys (branch s) corresponds to an accelerated rate of GHR evolution (branch p), although GHR sequences of prosimians are not available. This suggests the coevolution between GH and GHR, but the complete GHR sequences of the bushbaby and the tarsier are needed to directly correlate the evolution of GH and GHR in the common ancestor of simians."* Final sentence of the paper: *"there was no correlation between GH and GHR evolution at contact sites."* → **The strongest defensible statement is: GH and GHR both show accelerated evolution in the simian lineage, and both accumulate proportionally more changes at functionally important sites, but only one of 13 intermolecular contacts changed on both sides. "Ligand and receptor co-evolved residue-for-residue" is NOT supported.**
  - Supporting statistics for the functional-site enrichment: in GH, *"20 changes among the 34 sites (59%) studied have occurred in squirrel monkey, human, or rhesus monkey GH. In contrast, among the 155 other sites in simian GHs, only 58 changes have occurred (37%)… The difference is statistically significant (χ² = 5.27, P < 0.05)."* In GHR, *"we identified 10 amino acid changes in simians… This is in contrast to 50 amino acid changes at 222 other sites of the extracellular domain of GHR… the difference was again statistically significant (χ² = 4.30, P < 0.05). In contrast, there were no changes at these functionally important sites in the outgroup pig and rabbit sequences."*
  - GHR dN/dS: elevated but not significantly >1. Table 4 free-ratio model gives ωP = 0.912 (ancestral primate branch) and ωH = 1.268 (human branch), but *"the difference between the two-ratio model (model C) and the two-ratio model with the constraint of ωH = 1 (model E) was not significant… This suggests that the evolution of the GHR gene in the human branch is not significantly different from the neutral expectation."*
  - Adaptive-story caveat the authors themselves raise: *"the cause or biological basis for the rapid evolution is unclear"*; and on Leu43Arg, *"this change has not occurred in NW monkeys, although the His171Asp change in GH had already occurred in the common ancestor of simians… This finding suggests that there is no advantage for Leu43 to change to Arg in NW monkey GHR."*
- **File:** `Liu_2001_episodic_evolution_GH_primates_GHR_species_specificity.txt` (PDF: `../agent_papers/Liu_2001_episodic_evolution_GH_primates_GHR_species_specificity.pdf`)

---

## Wallis 1996 — The molecular evolution of vertebrate growth hormones: a pattern of near-stasis interrupted by sustained bursts of rapid change
- **Authors:** Michael Wallis (Biochemistry Laboratory, School of Biological Sciences, University of Sussex, Brighton)
- **Year:** 1996 (received 18 September 1995; accepted 2 February 1996)
- **Journal:** J Mol Evol 43(2):93–100
- **DOI:** 10.1007/BF02337353 · **PMID:** 8660433
- **⚠️ DOI correction:** the DOI is **10.1007/BF02337353**, not `…352` (that one resolves to an unrelated interphotoreceptor-retinoid-binding-protein paper). The lowercase form `10.1007/bf02337353` is what Sci-Hub accepted.
- **Retrieved:** 2026-09-18 (Sci-Hub mirror `sci-hub.fr`, via lowercase DOI). Unpaywall/Europe PMC: closed, not in PMC. Scanned-page PDF with a good embedded text layer; a few OCR artefacts in the abstract (e.g. *"tile rate"* = "the rate", *"lou,,ALo, MOLECUI.AR"* = journal masthead). **Full text read**, not abstract only.
- **Cited in context of:** [Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md](../Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md) — documenting **hGH as a REJECTED alternative model antigen**. This is the canonical source for the "GH is a textbook fast-evolving-in-bursts protein" claim that made hGH attractive on the evolution criterion.
- **Key content verified (direct quotes):**
  - **THE FOLD-INCREASE — the secondary-source figure of "at least 25-fold" is CONFIRMED, and the paper's own preferred phrasing is "at least 25–50-fold".** Abstract: *"It has been demonstrated previously that in mammals the evolution of pituitary growth hormone shows an unusual pattern, with an underlying slow rate and at least two sustained bursts of rapid evolution (in the artiodactyls and primates), during which the rate increased at least 25-fold."* Body: *"on two occasions (evolution of GH in artiodactyls and primates) the rate has increased markedly (25–50-fold)."* Discussion: *"The data available for mammalian GHs indicate that during the rapid bursts of evolution occurring in the artiodactyls and primates the rate increased by a factor of at least 25–50."* → **"at least 25-fold" is correct and is the conservative end; "25–50-fold" is the paper's own range.** Note the 25-fold figure is attributed to the earlier Wallis (1994) mammalian analysis and restated here.
  - **The underlying arithmetic (Table 2, rates in substitutions/aa site/year × 10⁹):** slow phase **0.21 ± 0.05** (estimate 1) or **0.28 ± 0.05** (estimate 2); rodents 0.49 ± 0.18; rabbit 0.49 ± 0.14; **rapid phase during ruminant evolution 5.6 ± 1.4** (Ka/Ks 0.30); **rapid phase during primate evolution 10.8 ± 1.3** (Ka/Ks 0.49). → 10.8/0.21 ≈ **51-fold** for the primate burst; 5.6/0.21 ≈ **27-fold** for the ruminant burst. Hence "at least 25-fold", range 25–50.
  - **HOW MANY BURSTS — the count depends on the clade, and the paper's own numbers are these.** In **mammals**: *"at least two sustained bursts of rapid evolution (in the artiodactyls and primates)"*, plus a minor *"two- to threefold"* increase in rodents and a similar slight increase in rabbit. Across **vertebrates**, this paper adds: *"bursts of rapid evolution in the amphibia and the elasmobranchs, and several bursts in the teleosts"*, i.e. *"on at least three occasions the rate increased substantially"* in lower vertebrates. Overall: *"It is concluded that in lower vertebrates, for much of evolutionary time, GH has evolved at a slow rate, similar to the basal rate seen in placental mammals, but that on at least three occasions the rate increased substantially. In teleosts several bursts of rapid evolution have occurred… Nevertheless, the overall picture is similar to that recognized in mammals — a predominant slow basal rate, with occasional sustained bursts."* → **Do not write a single number. Write: at least two bursts in mammals (artiodactyls, primates), at least three more in lower vertebrates (amphibia, elasmobranchs, teleosts), with several within the teleosts, plus a separate pattern in the primate placental GH/lactogen gene family.**
  - **Near-stasis — the basal rate, and the striking illustration of it.** *"for much of lower vertebrate evolution the rate of evolution of GH is low (0.19–0.39 × 10⁻⁹ substitutions/amino acid (aa) site/year), comparable with the basal rate derived for mammalian GHs."* The vivid version: *"The slow underlying rate of evolution in the birds, reptiles, and chondrosts is emphasized by the observation that the GHs of species from these groups that have been studied so far are much more similar to pig GH than is human GH, despite a four- to sixfold-longer period for evolutionary divergence."* And: *"The sequence of dog GH… is identical to that of pig GH (which was previously proposed as identical to the ancestral sequence for the eutherian GH sequences available)"*; cat GH *"differs from that of dog (and pig) at a single residue."*
  - **The bursts slow down again — this is what rules out simple loss of function.** *"In both primates and artiodactyls the rate slowed after the rapid burst, falling back toward the basal rate seen in other mammals."* Argument: *"(a) the proteins concerned all appear to retain their main biological function (growth promotion), (b) there is no evidence for duplicate GH genes in mammals except in the case of primates, where gene duplication appears to have occurred after the burst of rapid evolution, (c) the increased Ka/Ks ratios seen during the rapid evolution of GH in artiodactyls and primates would not be expected if rate changes were due to paralogous rather than orthologous comparisons, and (d) the slowing of the rate after the bursts seen in ruminants and primates argues against loss of function."*
  - **Selection, cautiously claimed.** Abstract: *"It is argued that the bursts of evolution seen for growth hormone are a consequence of selection and that this may reflect changes in the functions of the hormone additional to its basic growth-promoting actions."* Introduction hedges: *"In many cases the bursts of evolution can be best explained as due to the effects of adaptive natural selection, though in a few cases the possibility that they are due to a relaxation of purifying selection, due to loss of function, cannot be completely ruled out."* Note Ka/Ks stays **below 1** even in the primate burst (0.49, Table 2) — the only Ka/Ks > 1 values are in the **placental lactogen** subfamily (e.g. *"for the paired comparison hCS-L vs mGHV, Ka/Ks = 1.77, and Ka is significantly greater than Ks (P < 0.05)"*).
  - Primate GH/placental-lactogen cluster: *"In man the GH gene occurs as one of a cluster of five closely related genes, spanning about 55 kb on chromosome 17"*; *"This analysis suggests that a pattern of near-stasis and bursts of rapid evolution applies for this subfamily of GH-like proteins as it does for the mammalian GHs."* Crucially for the Liu 2001 cross-check: *"the first duplication, giving rise to the placental lactogens and GHs, occurred after the main period of rapid evolution in primate GHs."* (This is the argument Liu et al. 2001 pushes back on, invoking gene conversion.)
- **File:** `Wallis_1996_vertebrate_GH_near_stasis_bursts_rapid_change.txt` (PDF: `../agent_papers/Wallis_1996_vertebrate_GH_near_stasis_bursts_rapid_change.pdf`)

---

## Bass, Greene & Wells 1990 — Hormone phage: an enrichment method for variant proteins with altered binding properties
- **Authors:** Steven Bass, Ronald Greene, James A. Wells (Department of Protein Engineering, Genentech Inc., South San Francisco)
- **Year:** 1990 (received 10 September 1990; accepted 11 September 1990 — a Rapid Communication)
- **Journal:** Proteins: Structure, Function, and Genetics 8(4):309–314
- **DOI:** 10.1002/prot.340080405 · **PMID:** 1708882
- **Retrieved:** 2026-09-18 (Sci-Hub mirror `sci-hub.fr`, via DOI). Unpaywall/Europe PMC: closed, not in PMC. Scanned PDF with a serviceable embedded text layer — a few OCR artefacts, chiefly **roman-numeral "III" rendered as "I11" / "111" / "gene I11"** throughout, and subscripts flattened (IC₅₀ → "IC,₀"). **Full text read**, not abstract only.
- **Cited in context of:** [Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md](../Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md) — documenting **hGH as a REJECTED alternative model antigen**. This is **the origin-of-monovalent-phage-display paper**, and the basis for MODEL_ANTIGEN's claim that "monovalent pIII phage display was *invented* on hGH". That claim is fully supported.
- **Key content verified (direct quotes):**
  - **hGH fused to the C-TERMINAL DOMAIN of M13 gene III — CONFIRMED.** Abstract: *"Human growth hormone (hGH), a 191 residue protein containing two disulfide bonds, was fused to the carboxyl-terminal domain of the gene III protein, a minor coat protein exposed at one end of the filamentous phage M13."* Exact junction: *"The signal sequence and amino-terminal domain of gene III was replaced with the stII signal and entire hGH gene by fusion to residue 198 in the carboxyl-terminal domain of gene III"*; *"This fuses the carboxyl terminus of hGH (Phe-191) to the Pro-198 residue of the gene III protein with the insertion of a glycine residue encoded from the ApaI site."* Vector: **phGH-M13gIII**, *lac* promoter/operator + **stII secretion signal**, pBR322 β-lactamase + ColE1 origin + phage f1 intergenic region.
  - **PHAGEMID + M13KO7 HELPER PHAGE — CONFIRMED.** Abstract: *"The gene fusion was cloned into a plasmid containing origins of replication for Escherichia coli and filamentous phage and was packaged into phagemid particles upon infection by an M13K07 helper phage."* Host *E. coli* **JM101** (lacIᑫ), grown **without IPTG** to keep the fusion repressed. Titres *"varied from 2 to 5 × 10¹¹ colony forming units (cfu)/ml"*; helper titre *"~10¹⁰ plaque forming units (pfu)/ml"*.
  - **MONOVALENCY — the defining innovation, stated as a copy-number control.** Abstract: *"Transcription of the hGH-gene III fusion was controlled so that usually no more than one copy of the fusion protein was displayed along with the four copies of the wild-type gene III protein."* Rationale: *"It was suggested that multiple copies of the gene III fusion can lead to multiple point attachment of the fusion phage to the immobilized target protein"* — the **"chelate effect"** that had capped affinity discrimination in polyvalent peptide libraries. Quantified: *"We estimate that about 10% of the phagemid particles contain one copy of the hGH-gene III fusion protein."*
  - **SELECTION BY BINDING TO THE hGH RECEPTOR — CONFIRMED, on hGHbp-coated beads.** The target is defined as *"hGHbp, human growth hormone binding protein derived from a recombinant fragment corresponding to the extracellular domain of the hGH receptor"*. Format: *"Oxirane polyacrylamide beads (Sigma) were conjugated to the purified extracellular domain of the hGH receptor (hGHbp) containing an extra cysteine residue introduced by site-directed mutagenesis at position 237"*, at *"1.7 pmol hGHbp/mg dry oxirane bead"*, with BSA-coupled beads as the non-specific control. ⚠️ Note for precision: in **this** 1990 paper the receptor is immobilised on **beads** (a small-volume chromatographic format, deliberately chosen over plate panning: *"small volumes are used on the beads (200 µl vs. 6 ml)"*), not on plates.
  - **Enrichment achieved.** Abstract: *"the hGH-gene III phagemid particles were enriched over 5000-fold from non-hGH phage, and 8-fold from a mutant hGH phagemid following a single hGH-specific elution step from hGH receptor-coated beads."* Detail: *"one part of hGH phagemid was mixed with >3000 parts M13K07 phage. After one cycle of binding and elution, 10⁶ phage were recovered and the ratio of phagemid to M13K07 phage was 2 to 1. Thus, a single binding selection step gave >5000-fold enrichment."* The discriminated variant is **R64A**: *"The R64A variant hormone is about 20-fold reduced in receptor binding affinity compared to hGH (Kd values of 7.1 and 0.34 nM, respectively)."* → **wild-type hGH Kd for hGHbp = 0.34 nM.**
  - **Display is correctly folded — checked with conformation-sensitive mAbs.** Abstract: *"The hGH-gene III fusion protein was properly folded, as judged by reactivity with six hGH monoclonal antibodies whose epitopes are sensitive to the folded conformation of hGH."* Body: *"binding for seven of eight Mabs requires that hGH be properly folded. The IC₅₀ values for all Mabs were equivalent to wild-type hGH except for Mab 5 and 6. Both Mabs 5 and 6 are known to have binding determinants near the carboxyl-terminus of hGH which is blocked in the gene III fusion protein."* (This C-terminal occlusion is exactly what Lowman et al. 1991 then fixed by moving the fusion junction to gene III codon 249.)
  - **The stated general ambition — why this is the origin paper.** *"More generally, this expression system may allow other large proteins with discontinuous binding epitopes to be displayed, and binding selections applied to their mutated gene III fusions on filamentous phage."* And the size limit it broke: *"it has been shown that fusion phage are useful only for displaying proteins of less than 100 and preferably less than 50 residues"* — hGH is **22 kDa / 191 residues**. Conclusion: *"The copy number of the gene III fusion protein can be effectively controlled to avoid 'chelate effects' yet maintained at high enough levels in the phagemid pool to permit panning of large epitope libraries (>10¹¹)… Thus, it is possible to sort phagemid particles whose binding constants are down in the nanomolar range."*
- **File:** `Bass_1990_hormone_phage_hGH_gIII_monovalent_display.txt` (PDF: `../agent_papers/Bass_1990_hormone_phage_hGH_gIII_monovalent_display.pdf`)

---

## Lowman, Bass, Simpson & Wells 1991 — Selecting high-affinity binding proteins by monovalent phage display
- **Authors:** Henry B. Lowman, Steven H. Bass, Nancy Simpson, James A. Wells (Department of Protein Engineering, Genentech Inc., South San Francisco)
- **Year:** 1991 (received 15 August 1991; revised 23 September 1991 — an Accelerated Publication)
- **Journal:** Biochemistry 30(45):10832–10838
- **DOI:** 10.1021/bi00109a004 · **PMID:** 1932005
- **Retrieved:** 2026-09-18 (Sci-Hub mirror `sci-hub.box`, via DOI; `sci-hub.fr` was serving a captcha at the time). Unpaywall/Europe PMC: closed, not in PMC. Scanned PDF, good text layer with the same **"gene III" → "gene I11"** OCR artefact as Bass 1990; the PDF's first page carries the tail of the preceding article's reference list (a progesterone-receptor paper) — ignore it, the article proper starts at the title. **Full text read**, not abstract only.
- **Cited in context of:** [Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md](../Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md) — documenting **hGH as a REJECTED alternative model antigen**. This is the source for MODEL_ANTIGEN's "hGH libraries were panned on the immobilised receptor extracellular domain and affinity-matured that way".
- **Key content verified (direct quotes):**
  - **LIBRARY SIZE — "nearly one million", and the per-library figures.** Abstract: *"Nearly one million random mutants of hGH were generated at 12 sites previously shown to modulate binding to the hGH receptor or human prolactin (hPRL) receptor."* The construction: *"Each library, encoding 20⁴ possible variant hGH sequences, contained at least 10⁷ independent transformants."* And the codon arithmetic: *"Mutant libraries were created by substituting four residues simultaneously with the nucleotide sequence NNS (N = A/G/C/T; S = G/C) to generate all possible amino acid substitutions while limiting the total number of codons to 32. Four NNS codons yield 1.05 × 10⁶ possible nucleotide sequences that encode 1.60 × 10⁵ possible polypeptide chains."* → **"nearly one million" = the 1.05 × 10⁶ NNS nucleotide-sequence space of a four-codon cassette, summed over three libraries covering 12 sites; the protein-level diversity per library is 1.6 × 10⁵ and the transformant count is ≥10⁷ per library.** Do not paraphrase this as "a 10⁶-member library was built" without that qualifier.
  - **NUMBER OF RANDOMISED SITES — 12, in three libraries of 4.** *"Three libraries were constructed by cassette mutagenesis that fully mutated four residues at a time."* Named explicitly: **helix 4a** = K172, E174, F176, R178; **helix 1** = F10, M14, H18, H21; **helix 4b** = R167, D171, T175, I179 — the last *"within the E174S/F176Y background"*. Sites were chosen because they *"were shown by alanine-scanning mutagenesis to modulate the binding of the hGHbp and hPRLbp"*.
  - **PANNING ON IMMOBILISED hGH BINDING PROTEIN (the receptor ECD) — CONFIRMED.** Table I is titled *"Identity of hGH Mutants from Three Separate Libraries after Various Cycles of Binding Selection to **Immobilized hGHbp**"*. Method: *"Phagemid particles displaying mutants of hGH were cycled through rounds of binding selection to isolate variants that bind to hGHbp which was linked to oxirane-polyacrylamide beads as described (Bass et al., 1990). Competitive binding experiments with ¹²⁵I-hGH indicated that 58 fmol of functional hGHbp was coupled per microliter of bead suspension."* hGHbp is defined as *"hGH binding protein consisting of the extracellular domain of the hGH receptor"*. Elution: an hGH wash followed by **0.2 M glycine, pH 2** — *"we selected clones that were eluted with glycine (pH 2) after an hGH wash, because this was the more stringent selection."* Rounds: *"After three to six cycles of enrichment"* (abstract) / *"two to six cycles… depending upon the library"*. Monovalency is retained from Bass 1990: *"displayed in a monovalent fashion from filamentous phage particles as fusions to the gene III product of M13 packaged within each particle."*
  - **AFFINITY IMPROVEMENT ACHIEVED — 8-fold in this paper; ~30-fold in a stated-but-unpublished combination.** Discussion: *"over half of the free hormone variants selected had binding affinities greater than wild-type hGH (up to 8-fold tighter)."* The specific winners: *"Two multiple mutants (R167N/D171S/E174S/F176Y/I179T and R167E/D171S/E174S/F176Y) bound about 8-fold stronger to the hGHbp than wild type."* Table II numbers: wild-type hGH **K_D = 0.34 nM**; **E174S/F176Y K_D = 0.06 ± 0.01 nM** (5.6-fold tighter); best helix-4b variants **K_D = 0.04 ± 0.02 nM**. The forward-looking figure: *"preliminary experiments show that combining the highest affinity mutants from the helix 1 and 4a libraries produces a multiple mutant that binds about 30-fold tighter to the hGHbp (K_D ~ 13 pM; H. Lowman and J. Wells, unpublished results)."* ⚠️ That 30-fold / 13 pM number is flagged **unpublished** here — for a published version, cite Lowman & Wells 1993 (~400-fold) instead.
  - **Specificity gain (bonus, and the sharper selling point).** *"the E174S/F176Y mutant binds 200-fold weaker to the hPRLbp than hGH… Since this mutant binds 5.6-fold tighter to the hGHbp than wild-type hGH, the change in preference for binding hGHbp over hPRLbp is about 1100-fold."* And: *"The E174T/F176Y/R178K and R167N/D171S/E174S/F176Y/I179T mutants each bind >500-fold weaker to the hPRLbp than hGH, yielding changes in binding preference of >1000-fold and >4000-fold, respectively."*
  - **⚠️ HIGHLY RELEVANT TO THE MODEL-ANTIGEN REJECTION: this paper explicitly says natural GH sequence conservation is UNCORRELATED with functional importance.** *"In contrast, studies of natural variants that may ascribe functional significance to sequence conservation can be grossly confounded because the protein ligand coevolves with its receptor, and/or the protein contains overlapping functional epitopes that evolve at different rates in vivo. In fact, this appears to be the case for this very epitope on hGH. The sequences of over 21 natural species variants of growth hormone are known… However, we find that the degree of sequence conservation is totally uncorrelated with the alanine-scanning functional studies (Figure 3B). Not surprisingly, 19 of these 21 growth hormones do not bind tightly to the hGHbp. Moreover, three of the residues in the family that are fully conserved (H18, H21, and E174) are irrelevant to hGHbp binding. These are crucial for zinc binding and storage of a dimeric form of growth hormone in vivo."* By contrast, **in vitro** selection did recover function: *"in our in vitro system functional importance correlates with sequence conservation"* (R² = 0.86, Figure 3A). → **This is a direct argument against using natural GH evolution as a "ground-truth trajectory", and is worth citing in the rejection rationale itself.**
  - Vector improvements over Bass 1990, for the record: **phGHam-g3** moves the fusion junction to *"codons 249–406 of the M13 gene III"* (deleting all but one Gly-Gly-Gly-Ser repeat) so the hGH C-terminus stays accessible — *"Binding of pS0132 particles was reduced by >2000-fold for both Medix 2 and 5B7.C10… On the other hand, binding of phGHam-g3 phage was weaker by only about 1.5-fold, 1.2-fold, and 2.3-fold"*; an **amber codon (TAG)** after hGH codon 191 lets the same phagemid express free hormone in a non-suppressor strain (16C9) after selection; and the **alkaline phosphatase (phoA) promoter** replaces *lac*. Host for display: *E. coli* **XL1-Blue** (supE), helper **M13KO7** at MOI ~100.
- **File:** `Lowman_1991_monovalent_phage_display_high_affinity_hGH.txt` (PDF: `../agent_papers/Lowman_1991_monovalent_phage_display_high_affinity_hGH.pdf`)

---

## Lowman & Wells 1993 — Affinity maturation of human growth hormone by monovalent phage display
- **Authors:** Henry B. Lowman, James A. Wells (Department of Protein Engineering, Genentech Inc., South San Francisco)
- **Year:** 1993 (received 3 June 1993; accepted 30 June 1993)
- **Journal:** J Mol Biol 234(3):564–578
- **DOI:** 10.1006/jmbi.1993.1612 · **PMID:** 8254660
- **⚠️ PMID correction:** **8254660**, not 8254658 (that PMID is a CcdB/DNA-gyrase paper in the same JMB issue).
- **Retrieved:** 2026-09-18 (Sci-Hub mirror `sci-hub.fr`, via DOI). Unpaywall/Europe PMC: closed, not in PMC. **This PDF is an image-only scan** (PyMuPDF returned 14 characters); the text file was produced locally by **tesseract 300 dpi OCR, `--psm 1`**, so expect character-level errors — e.g. *"~2 x 10°"* for 2 × 10⁶, *"gene FT"* / *"gene ITI"* for gene III, *"bydrochloride"*, *"thed"*, *"capy"*, *"H. coli"* for *E. coli*. **Abstract and introduction read in full from OCR; quantitative claims below are from those sections.** Figures and tables were not re-verified digit-by-digit — check the PDF before quoting any table value.
- **Cited in context of:** [Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md](../Grant_application/INSERM_IRP_2026/MODEL_ANTIGEN.md) — documenting **hGH as a REJECTED alternative model antigen**. This is the published end point of the hGH affinity-maturation arc (Bass 1990 → Lowman 1991 → here), and the strongest single number for "hGH was affinity-matured by monovalent phage display".
- **Key content verified (direct quotes, OCR):**
  - **The headline: ~400-fold improvement from 15 substitutions.** Abstract: *"by combining affinity enhanced mutants from libraries independently sorted we created an hGH variant with 15 substitutions that bound ~400-fold more tightly to the hGHbp than wild-type hGH."* Restated in the Introduction: *"we produced an hGH variant containing 15 substitutions that bound the hGHbp ~400-fold tighter than wild-type hGH."*
  - **Libraries: five, each ~2 × 10⁶ variants, four codons at a time, panned on IMMOBILISED hGHbp.** Abstract: *"Five different libraries of mutated hGH genes (each containing ~2 × 10⁶ protein variants) were created by randomly mutating four different codons at residues that were shown to be important for receptor binding by structural or functional criteria. Mutated proteins were displayed as single copies from their respective filamentous phagemid particles and sorted in vitro for binding to the immobilized hGHbp. Phagemid particles that bound the immobilized hGHbp were eluted and propagated. After three to seven rounds of binding enrichments, hGH variants were isolated that contained 2 to 4 mutations and exhibited three- to sixfold improvements in binding affinity."*
  - **Kinetic basis of the gain:** *"The affinity enhancements occurred predominantly by slowing the off-rate of the hormone (>60-fold), and partly through increasing the on-rate (up to 4-fold)."*
  - **Why libraries had to be combined rather than enlarged — the transfection ceiling.** *"Because of the limits of DNA transfection efficiency in creating the library we could not sample thoroughly mutations at more than four codons at once. Nonetheless, the free energy effects for these mutations acted cumulatively."* Introduction: *"it was not feasible to generate enough transformants to ensure that all possible residue combinations were represented when more than five or six codons were randomized at once."*
  - **Relationship to alanine scanning:** *"Residues that were shown to be important for binding by alanine-scanning were most highly conserved after binding selection, and interestingly many of them could be further improved. Thus, we found it most effective to randomly mutate the residues that were shown to modulate affinity by alanine-scanning, and to combine the selectants from separate libraries that exhibit the highest affinities."*
  - Construct continuity: *"The plasmid, phGHam-g3 which encodes wild-type hGH fused to the carboxy-terminal domain of M13 gene III (Lowman et al., 1991a), was used to construct parental vectors for cassette mutagenesis"*; *"Phagemid particles that display a single copy of the hGH-gene III fusion protein were prepared by electro-transforming Escherichia coli XL1-Blue cells… and adding M13K07 helper phage… which provides a large excess of the wild-type gene III protein."* Library names include **Minihelix-1 (M1)** — K41, Y42, L45, Q46 — and **loop-1 (L1)** — F54, E56, I58, R64.
  - Motivation, worth noting for any therapeutic-framing caution: *"by improving site 1 affinity further, it may be possible to obtain an even better antagonist that could have utility in treating conditions of growth hormone excess such as acromegaly."*
- **File:** `Lowman_Wells_1993_affinity_maturation_hGH_phage_display.txt` (PDF: `../agent_papers/Lowman_Wells_1993_affinity_maturation_hGH_phage_display.pdf`)

---

## Greiss, Daube, Noireaux & Bar-Ziv 2025 — Bacterial chromosome conformation and cell-free gene expression in synthetic 2D compartments
- **Authors:** Ferdinand Greiss, Shirley S. Daube, Vincent Noireaux, Roy H. Bar-Ziv (Dept. of Chemical and Biological Physics, **Weizmann Institute**; School of Physics and Astronomy, Univ. of Minnesota)
- **Year:** 2025
- **Journal:** Nature Communications 16
- **DOI:** 10.1038/s41467-025-65249-2 | **PMID:** 41238531 | **PMCID:** PMC12618494
- **Retrieved:** 2026-09-24 (Europe PMC open-access `fullTextXML`, tag-stripped to plain text — no Sci-Hub needed, CC-BY OA).
- **Cited in context of:** which Weizmann synthetic-biology group has published work using an **E. coli strain that maintains R6Kγ (pir-dependent) plasmids**.
- **Key content verified (direct quote, Methods — "Engineering the E. coli genome"):**
  - *"To generate the donor plasmid pKD4-HT, we transferred the previously established HaloTag reporter system with N-terminal fused HA tag … from pBEST into pKD4 (Forchheimer plasmid collection, Bacteriology and Genomic repository, Weizmann Institute) using **PirPlus DH10β pir116** (Bacteriology and Genomic repository, Weizmann Institute) as cloning host."*
  - *"We transformed E. coli K-12 MG1655 with the plasmid pSLTS (Forchheimer plasmid collection, Bacteriology and Genomic repository, Weizmann Institute) and induced the lambda red system for homologous recombination."*
  - pKD4 carries the **R6Kγ origin** (Datsenko & Wanner 2000), hence the pir-116 host; the final strain is MG1655 P_R-UTR1-HA-HaloTag, cured of pSLTS at 37 °C.
- **Practical note:** both the pir⁺ host strain and the R6Kγ plasmids are stocked by the Weizmann **Bacteriology & Genomic Repository** (Forchheimer plasmid bank, https://bip.weizmann.ac.il/plasmid/), i.e. available in-house to any Weizmann group on request.
- **File:** `Greiss_2025_bacterial_chromosome_2D_compartments_cellfree.txt` (no PDF — OA XML extract)

---

## Zaretsky et al. 2017 — ICAMs support B cell interactions with T follicular helper cells and promote clonal selection
- **Authors:** Irina Zaretsky, Ofir Atrakchi, Roei D. Mazor, Liat Stoler-Barak, Adi Biram, Sara W. Feigelson, Alexander D. Gitlin, Britta Engelhardt, **Ziv Shulman** (senior/corresponding author, *Correspondence to Ziv Shulman: ziv.shulman@weizmann.ac.il*) — Dept. of Immunology (now Systems Immunology), **Weizmann Institute of Science**, Rehovot; Rockefeller University; Theodor Kocher Institute, Bern
- **Year:** 2017 (issue 6 Nov 2017; Crossref issued 22 Sep 2017)
- **Journal:** Journal of Experimental Medicine 214(11):3435–3448
- **DOI:** 10.1084/jem.20171129 | **PMID:** 28939548 | **PMCID:** PMC5679169
- **Retrieved:** 2026-09-28. Not reachable via rupress.org or PMC direct (Cloudflare / no OA package endpoint); obtained via `scripts/fetch_papers.py` Sci-Hub route. Metadata independently cross-checked against **PubMed efetch** and **Crossref** — all three agree on vol. 214, no. 11, pp. 3435–3448, 2017, doi:10.1084/jem.20171129.
- **Cited in context of:** Inserm IRP 2026 — establishing Ziv Shulman (Systems Immunology, Weizmann) as a supporting collaborator with senior-author standing in germinal-centre B cell selection.
- **Key content verified (direct quotes):**
  - Abstract, the central claim: *"we use in vivo B cell competition models and intravital imaging to examine the adhesive mechanisms governing B cell selection for GC colonization. We find that intercellular adhesion molecule 1 (ICAM-1) and ICAM-2 on B cells are essential for long-lasting cognate Tfh–B cell interactions and efficient selection of low-affinity B cell clones for proliferative clonal expansion."*
  - Contact-duration measurement (intravital two-photon): *"although T cell interactions with ICAM-1/2+/+ B1-8hi B cells lasted a mean of 29 min, T cell interactions with ICAM-1/2−/− B1-8hi B cells were 2.7-fold shorter … contacts lasting more than 15 min were ICAM-1/2 dependent. We conclude that B cell ICAMs are essential for sustained Tfh–B cell interactions, but not for short-lived engagements."*
  - The affinity-threshold result: *"B1-8lo B cells did not effectively enter the GC compartment in ICAM-1/2+/+ chimeric mice (mean 22.8% of GC cells) … However, B1-8lo B cells were 2.4-fold more effective in entering the GC compartment, when competing with endogenous NP-specific B cells in ICAM-1/2−/− chimeras. These results suggest that ICAM molecules are beneficial for selection of low-affinity B cell clones for clonal expansion and GC colonization."*
  - The pMHCII gradient that ties adhesion to affinity: *"B cells presenting lower levels of pMHC​II to T cells depend more on ICAMs for formation of long-lasting interactions with T cells than B cells that present higher levels of pMHC​II."*
  - Scoring convention for the imaging: T–B conjugates counted only if they *"lasted longer than 4 min."*
- **Relevance to the synthetic germinal centre:** the selection step of a GC is not a pure affinity readout — it is a *contact-duration* readout, and an adhesion layer (ICAM-1/2–LFA-1) sets how long a B cell can hold a helper cell and therefore how much low-affinity diversity survives into the expanding compartment. A synthetic selection cycle that scores binding affinity instantaneously will collapse clonal diversity faster than a real GC does; the tunable knob for keeping low-affinity-but-promising clones alive is the *dwell time* of the selection interaction, not the affinity threshold itself.
- **File:** `Zaretsky_2017_ICAMs_Tfh_B_interactions_clonal_selection_GC.txt` (PDF: `../agent_papers/Zaretsky_2017_ICAMs_Tfh_B_interactions_clonal_selection_GC.pdf`, 14 pp.)

---

## Baig et al. 2021 — Synthetic biology open language visual (SBOL Visual) version 3.0
- **Authors:** Hasan Baig, Pedro Fontanarossa, James McLaughlin, James Scott-Brown, Prashant Vaidyanathan, Thomas Gorochowski, Goksel Misirli, Jacob Beal (corresponding), Chris Myers
- **Year:** 2021
- **Journal:** Journal of Integrative Bioinformatics 18(3):20210013
- **DOI:** 10.1515/jib-2021-0013 · **PMID:** 34668358 · **PMC:** PMC8560346
- **Retrieved:** 2026-10-20 (open access, CC BY 4.0; Europe PMC `fullTextXML`). The PMC deposit is abstract-level; the normative specification text is the PDF held locally at `Resources/SBOL_Visual/SBOL Visual 3.0.pdf` (version 3.0, dated 2021-04-14, same editor/author list), which was read directly.
- **Cited in context of:** FIG_001 — the PI mandated SBOL Visual for the MS_C_018 / MS_C_030 design reference; this is the citation the figure legend will carry.
- **Key content verified (direct quotes, from the local specification PDF unless marked):**
  - Scope (abstract, PMC): *"SBOL Visual aims to organize and systematize such conventions in order to produce a coherent language for expressing the structure and function of genetic designs."*
  - What changed in v3 (abstract, PMC): *"The major difference between SBOL Visual 3 and SBOL Visual 2 is that diagrams and glyphs are defined with respect to the SBOL 3 data model rather than the SBOL 2 data model."* Deprecated material removed: *"the deprecated 'insulator' glyph and 'macromolecule' alternative glyphs have been removed."*
  - Glyph requirement 9 (§4.1): *"A sequence feature glyph specification MUST include exactly one horizontal rule for its RECOMMENDED vertical alignment with the nucleic acid backbone."* — this is the rule `scripts/figures/sbol_track.py` reads out of each `*-specification.svg`.
  - Glyph requirement 8 (§4.1): *"A sequence feature or molecular species glyph specification MUST include a rectangular bounding box indicating its extent in space."*
  - Backbone contact (§5.2 rule 1): *"Every feature glyph MUST have its bounding box in contact with the backbone for the nucleic acid construct it describes."*
  - Colour is free (§4.2 rule 2): *"The interior of a glyph MAY be given any fill color, as long as the choice of fill does not interfere with recognizing the glyph."* — the PI's "use the Colors" request is standards-compliant, not a deviation.
  - Horizontal scaling is free (§4.1 rule 11): *"If a sequence feature glyph can represent components of highly variable size or structural complexity, the glyph SHOULD be able to be scaled horizontally to indicate relative scale."*
  - Strand (§5.2 rule 2): a reverse-complement feature *"SHOULD be inverted vertically and horizontally (i.e., rotated 180 degrees)."*
  - Circularity (§5.1 rules 2–3): a backbone *"SHOULD be horizontal in orientation, but MAY use non-horizontal structure to indicate important physical attributes (e.g., a closed loop to indicate a cyclic plasmid)"*; the stylised backbone-shape glyphs *"SHOULD be used as a matched pair, indicating the bounds of the context region"*, each *"concatenated with an Omitted Detail glyph."*
  - Novel glyphs are permitted (§5.2 rule 6 / Fig. 14b): a diagram using *"some novel custom non-conflicting symbol, not matching any glyph defined in this document"* is allowed ("MAY") — the basis for the OE-PCR bracket notation proposed in FIG_001's TOOLKIT.md.
- **Licensing (checked, `Resources/SBOL_Visual/LICENSE.html`):** the specification document is CC BY 4.0; **the glyphs themselves are CC0** — *"to the extent possible under law, the SBOL developers have waived all copyright and related or neighboring rights to SBOL Visual glyphs."* No attribution obligation for publishing the glyph art.
- **File:** `Baig_2021_SBOL_Visual_3.0_specification.txt` (local spec PDF: `../Resources/SBOL_Visual/SBOL Visual 3.0.pdf`, 91 pp.)

---

