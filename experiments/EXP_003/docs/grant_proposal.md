# MOST Maimonide — Google Doc Snapshot
## Synthetic germinal centres in E. coli for eliciting broadly neutralising nanobody cocktails
*Snapshot taken: 2026-02-28*

---

## 1. Abstract (1484 char)

Germinal centres (GCs) drive iterative cycles of antibody somatic hypermutation and affinity-based selection of B cells, evolving high-affinity antibodies while preserving clonal diversity to face continually evolving pathogens. Building on design rules emerging from recent GC studies linking mutation rate, selection stringency, dark/light-zone compartmentalisation and migration, we will construct artificial GCs to rapidly evolve therapeutic neutralising nanobodies. We will engineer E. coli with an orthogonal error-prone T7 replisome to hypermutate a nanobody surface-display library (mimic of the GC's dark zone) and select binders using receptor-binding domain (RBD; e.g., SARS-CoV-2) on magnetic beads (mimic of the GC's light zone). Parallel 96-well cultures will maintain diversity, while systematic tuning of GC parameters will measure effects on repertoire breadth, selection efficiency and affinity maturation (WP1). Next, we will emulate host–pathogen arms races by coupling the synthetic GC to a continuously evolving antigen: M13 phage-displayed SARS-CoV2's Spike Receptor Binding Domain (RBD) diversified by PACE-like in vivo mutagenesis. Under combined nanobody-displayed selection pressure, RBD should acquire immune-escape mutations seen in circulating variants, supporting variant forecasting and selection of broadly neutralising nanobodies (WP2). The project will deliver evolution-trained nanobody-producing E. coli repertoires, capable of providing rapid response to new viral pathogenic variants, while providing insights to GC design and function.

---

## 2. Scientific background and state of the art

**Overarching context.** Neutralizing monoclonal antibodies (nAbs) emerged during the COVID-19 pandemic as one of the first-line treatments, offering immediate antiviral remedy without requiring time for host immune priming via vaccination [1]. In randomised controlled trials, early outpatient administration of anti-spike neutralizing mAbs reduced nasopharyngeal viral load and lowered the risk of hospitalization or death in high-risk individuals, establishing the clinical principle that timing-critical neutralization of SARS-CoV-2 can change disease trajectory [2]. Two main needs for nAbs emerged: (1) for patients with contraindications for small-molecule antivirals use (e.g., drug–drug interactions, renal/hepatic limitations, or access/logistical barriers) and where rapid viral suppression is prioritised. (2) SARS-CoV-2 evolution repeatedly narrowed the useful lifespan of single antibodies and even cocktails: escape mutations in spike, especially in the receptor-binding domain (RBD), recurrently eroded efficacy, highlighting variant-driven "drug obsolescence" as a core translational bottleneck for antibody therapeutics [3]. Future antibody therapeutics for COVID-19, and for novel (sarbeco)viruses, must therefore be generated and updated on timelines that match epidemic spreading (10 months elapsed before first nAbs were available during COVID19 [22]) and variant emergence. Current assessments explicitly identify neutralising mAbs as a modality whose impact is constrained not by proof-of-concept efficacy, but by the speed of viral antigenic change relative to conventional discovery pipelines [1]. While mono-clonal Abs provide high affinity and neutralization capacity, rapidly evolving viruses can escape them easily, necessitating a clonally diverse Ab treatment (REF).

**Germinal centres as evolutionary machines.** Germinal centres are the evolutionary engines of adaptive immunity. Within these transient microanatomical structures, B cells undergo iterative rounds of somatic hypermutation (SHM) in a spatially segregated dark zone where B cells proliferate, and affinity-based selection in a light zone, where antigen-loaded follicular dendritic cells and T follicular helper (Tfh) cells mediate competitive survival signals [5]. This compartmentalised architecture is thought to efficiently select high affinity antibodies while maintaining clonal diversity to prevent premature convergence on a single dominant clone, properties that enable the immune system to generate broadly neutralising antibody repertoires capable of covering antigenic variation [6].

Despite their importance, the design principles that govern GC performance remain incompletely characterised [7]. How do mutation rate, selection stringency, and dark-zone–to–light-zone cycling frequency interact to shape the breadth and depth of affinity maturation? Computational models have explored these questions in silico [8], but no synthetic analogue of the GC, one that preserves compartmentalised mutation, selection, and clonal diversity, has been constructed, leaving these parameters experimentally inaccessible.

**Limitations of current directed-evolution approaches.** In recent decades, directed-evolution and display-based antibody engineering workflows (phage display[19], yeast display[20], ribosome display[21]) and in vivo continuous-evolution platforms such as PACE[9] and OrthoRep[23] were used to enrich high-affinity viral binders. Yet, often these approaches struggle to select true neutralizers with durable activity against evolving viruses. Selections are typically performed against purified antigens, favoring clones that bind strongly in the assay format, yet do not block entry[b]-relevant conformations, quaternary epitopes, or avidity contexts present on virions or infected cells. Thus, testing of a large number of variants is necessary. Even when potent neutralizers are obtained, SARS-CoV-2 experience underscores how rapidly escape variants can erode Ab activity, so directed evolution that optimizes affinity to a single antigen state can inadvertently narrow breadth unless the selection explicitly penalizes escape and rewards conserved-epitope recognition (10.1016/j.cell.2021.07.027).

These failure modes reflect a fundamental difference from the natural GC processes and immunity: they apply selection globally to a single, well-mixed mutant library population, challenged with a single antigen. This tends to drive rapid convergence toward a small number of dominant Ab clones, sacrificing the repertoire diversity and adaptability towards evolving antigens that are hallmarks of natural GC mechanism and output[9,18].

**Laboratory evolution of RBD as a predictive tool.** The predictive power of laboratory RBD evolution has been recently tested. Directed evolution of yeast-displayed SARS-CoV-2 RBD identified several mutations (i.e., S477N, E484K, and N501Y) before they appeared in circulating variants, demonstrating that laboratory evolution can anticipate natural escape trajectories [4]. However, other occurring mutations (i.e., at positions 468, 490, and 494) were missed, suggesting that additional selective pressures beyond receptor affinity shape viral evolution [4, 24].

---

## 3. Research objectives and specific aims

This project pursues a fully tuneable synthetic analogue of GCs to achieve a dual objective: (1) gain quantitative insight into the design principles of germinal centres: the interplay of mutation rate, selection stringency, spatial compartmentalisation, and inter-zone migration; and (2) harness this understanding to build an efficient, target-agnostic platform for generating broadly neutralising nanobody cocktails[c].

This duality, akin to Pasteur Quadrant application-inspired foundational research, is integrated in two work packages of increased complexity to tackle 3 specific aims:

Building on this proof of principle, the present project directly addresses both translational needs outlined above: by constructing a synthetic germinal centre in E. coli coupled to a continuously co-evolving antigen, we aim to produce diversified, evolution-trained nanobody repertoires on timescales compatible with epidemic response, while simultaneously yielding fundamental insights into the design principles of germinal centre function.

[TODO: Refine specific aims once WP descriptions are finalised.]

---

## 4. Detailed description of the proposed research

### WP1: An E. coli-based synthetic germinal centre

We propose to build a synthetic GC analogue that captures the essential design features of natural GCs: spatially separated mutation (dark zone) and selection (light zone) compartments, tuneable migration frequency between zones, and maintenance of clonal sub-populations to preserve diversity. The system will use E. coli as the host organism, using the orthogonal T7 replisome system [10] for targeted, continuous hypermutation of a synthetic nanobody library displayed on the bacterial surface [11] while maintaining the host bacterial genome under native low-mutation replication regime, akin to somatic hyper mutation of the immunoglobuline genes in B cells. We will combine this regime with bead-based antigen selection for affinity enrichment. To this end the following components will be fitst engineered, tuned and quantified separately and then integrated for selection of antibodies against SARS-CoV-2 RBD.

**Nanobody library construction.**
E. coli displaying a nanobody library will be used as the analog of B cell precursors, using intimin-based bacterial display system [11]. To mimic the diversity of B cell precursors entering a natural GC, the starting library will comprise nanobodies (VHH) of known but varied affinity for SARS-CoV-2 RBD. Xiang et al. identified a large repertoire of RBD-specific nanobodies from a llama immune library, spanning affinities from low-nanomolar to sub-picomolar and covering at least five non-overlapping epitopes [15]. We will clone a defined panel of these nanobodies—including weak (low-nanomolar), moderate, and strong (picomolar) binders targeting distinct epitopes—into a T7-replicated plasmid carrying its own T7 origin of replication. Each[d] nanobody variant will be displayed on the E. coli surface using the intimin-based bacterial display system of Glass et al. [11], for direct antigen-mediated selection.

**Dark zone: nanobody hypermutation via the T7 orthogonal replisome.**
The orthogonal T7 replisome system described by Diercks et al. [10]. Co-expression of an engineered error-prone T7 DNA polymerase supplied in trans [e][f] will restrict hypermutation to the plasmid-borne nanobody gene without elevating the host genomic mutation rate. The reported in vivo error rate of the mutagenic T7 replisome (1.7 × 10⁻⁵ substitutions per base) is 100,000-fold above the E. coli genomic rate. Dark-zone-mimicing cultures will be maintained in separate wells of 96-well deep-well plates, each seeded with a distinct nanobody sub-library or lineage, to preserve clonal diversity and prevent premature convergence, a key feature of natural GC architecture [6].

**Light zone: antigen-mediated selection on beads.**
In the light-zone-mimicing compartment, samples of each of the diversified 96-well populations of nanobody-displaying E. coli will be exposed to biotinylated recombinant SARS-CoV-2 RBD displayed on streptavidin-coated magnetic beads. Following incubation and repeated washes, captured cells will be eluted, expanded and mixed back at varying ratios into their founding population in the 'dark zone' regime (see below). Selection stringency will be tunable by varying the RBD concentration on beads, incubation time, and wash conditions.

**Migration rules and diversity maintenance.**
We will control the migration between dark-zone and light-zone compartments using an automated liquid-handling robot (e.g. Hamilton, Tecan). After selection, surviving cells from the light zone will be migrated back to the dark zone for further hypermutation. Migration frequency and fraction size will be varied systematically to explore their effect on repertoire diversity, following principles from GC modelling [5,6]. The 96-well compartmentalised format ensures that distinct clonal lineages evolve in parallel, on drift-favoring smaller populations, preventing competitive exclusion and maintaining the polyclonal diversity characteristic of natural GC output.

**Readouts and success criteria.**
The synthetic GC will be evaluated on three key metrics: (i) affinity maturation where enrichment of higher-affinity nanobodies tracked by flow cytometry (fluorescently labelled RBD at varying concentrations, yielding affinity distributions for the entire library at each cycle) full-length VHH amplicon sequencing (the 390 bp nanobody gene fits a single MiSeq 2×300 bp read pair) and selected nanobodies quantified using BIAcore (available at Partner 1); (ii) diversity maintenance where clonal diversity across cycles quantified by Shannon entropy and Simpson index; (iii) polyclonality where production of multiple nanobody lineages binding non-overlapping RBD epitopes, assessed by competitive binding assays.

**Immunological memory and sequential variant challenge.**
The diverse nanobody repertoire matured against one RBD variant can be reseeded against a subsequent variant, rather than restarting from a naïve library. We will run sequential campaigns using well-characterised SARS-CoV-2 RBD variants (e.g. Wuhan → Alpha → Delta) and compare the speed of convergence and breadth of the resulting solutions.

**Negative selection: depleting polyreactive binders.**
In natural GCs, checkpoints eliminate self-reactive and polyreactive B-cells that would otherwise dilute the functional repertoire[7]. We will implement an analogous step by counter-selection on decoy beads: before each positive-selection round on RBD-loaded beads, the bacterial library will be pre-incubated with streptavidin-coated magnetic beads loaded with biotinylated bovine serum albumin (BSA) or streptavidin alone. Bacteria captured on decoy beads will be magnetically removed and discarded, so that only clones with low non-specific binding enter the RBD selection step. The stringency of this depletion can be tuned by varying decoy-protein concentration and incubation time, providing an additional GC parameter to explore alongside mutation rate and positive-selection pressure.

[TODO: Add negative-selection modalities for WP1—e.g. counter-selection against non-specific binders. To be discussed.]

### WP2: Co-evolutionary extension

WP2 extends the platform by coupling it to a continuously evolving antigenic population. RBD variants will be displayed on M13 bacteriophage and diversified by PACE-like in vivo mutagenesis, creating an evolutionarily moving target that drives the nanobody repertoire towards broad neutralisation. Because phage infection delivers DNA into the bacterial host, the system also provides a natural channel for recording binding events and for antigen-dependent survival signalling[g], closing the GC analogy from a one-sided selection to a genuine co-evolutionary arms race.

**M13 phage display of RBD variants.**
The SARS-CoV-2 RBD will be cloned into the pCSM phagemid vector as a fusion to the M13 minor coat protein pIII, following Pérez-Massón et al. [16]. Phage particles displaying RBD–pIII fusions will be rescued by super-infection with M13KO7 helper phage. Functional display will be confirmed by phage ELISA against recombinant human ACE2.

**Continuous in vivo mutagenesis of RBD.**
Host E. coli cells will harbour the arabinose-inducible mutagenesis plasmid MP6 [13], which elevates the mutation rate 322,000-fold above baseline ([h][i] 2.3 substitutions per kb per generation). Because only the phage genome replicates rapidly, mutations accumulate preferentially on the phage-borne RBD gene.

**Phage-based light-zone selection with inducible infection.**
Nanobody[j]-displaying E. coli are exposed to evolved RBD-displaying M13 phage. The tra operon on a modified F plasmid is placed under an IPTG-inducible lac promoter, so that in the absence of inducer no F-pilus is produced and M13 cannot initiate infection [17]. The only route for phage association is through the surface-displayed nanobody binding the pIII-fused RBD. After incubation, gentle centrifugation separates nanobody-bound phage (pellet) from unbound escape variants (supernatant). Escape variants are collected and returned to the pathogen mutagenesis cycle. IPTG addition then induces F-pili in the pellet, allowing phage DNA injection exclusively into nanobody-positive bacteria.

**Phage-delivered survival signal via toxin–antitoxin.**
The incoming phage genome encodes an antitoxin gene. After washing, a cognate toxin is added[k]: only productively infected bacteria survive, while all uninfected cells are eliminated, directly mirroring Tfh-mediated positive selection in the GC light zone.

**Lineage tracing via CRISPR spacer acquisition.**
Each[l] phage-infection event will be recorded using a CRISPR-based biological tape recorder [14]. Cas1–Cas2 proteins integrate spacers derived from the infecting phage genome into a genomic CRISPR array, which allows reconstruction of RBD–nanobody co-evolutionary lineages through sequencing.

**Dual selective pressure.**
The platform imposes the same dual pressure as natural viral evolution: nanobody-mediated selection drives immune escape, while ACE2 panning maintains receptor-binding fitness. Only variants that satisfy both objectives persist in the co-evolutionary cycle.

[TODO: Add negative-selection modalities for WP2—e.g. counter-selection against binding to non-RBD coat proteins (autoimmune-like specificities). To be discussed.]

---

## 5. Significance, innovation and potential benefits

[Placeholder — Ariel will add "Pasteur Quadrant" framing. Key points to develop: (i) First synthetic GC analogue preserving compartmentalised mutation, selection, and clonal diversity; (ii) Tuneable platform for studying GC design principles (fundamental contribution); (iii) Target-agnostic: any antigen displayable on beads or phage; (iv) Broadly neutralising polyclonal nanobody cocktails as therapeutics; (v) Co-evolutionary dynamics and variant forecasting.]

---

## 6. Applicability: expected uses and future technological development

The synthetic GC platform operates at TRL 2–4 [m] and addresses three translational axes:

**Broadly neutralising nanobody cocktails.**
The polyclonal nanobody repertoires generated by the platform could serve as immunotherapeutics against SARS-CoV-2 and other viral targets. Unlike monoclonal approaches, the GC-derived cocktails may inherently cover multiple epitopes, reducing the risk of escape.

**Variant forecasting.**
The co-evolutionary trajectories sampled by the system may help forecast naturally arising variants of concern [4], informing proactive vaccine and therapeutic design.

**A target-agnostic platform.**
The synthetic GC is not limited to SARS-CoV-2 RBD. Any soluble antigen that can be biotinylated and loaded onto magnetic beads (WP1) or displayed on M13 phage as a pIII fusion (WP2) is a valid target. This includes other viral surface proteins as well as non-viral targets such as tumour-associated antigens.

---

## 7. Cooperation vectors between research groups

[Placeholder. Should describe: (i) Complementary expertise of French and Israeli teams; (ii) Proposed modes of cooperation (joint experiments, mutual visits, shared reagents and data); (iii) How the collaboration benefits the research; (iv) Planned mutual visits (at least one per year).[n]]

---

## 8. Work plan and Gantt chart

[Placeholder. Should include: (i) 3-year Gantt[o] chart with WP1 and WP2 milestones; (ii) Verbal description of each work step with start/end times;[p] (iii) Key deliverables and decision points.]

---

## 9. Bibliography[q]

[1] D. Corti, L. A. Purcell, G. Snell, and D. Veesler, "Tackling COVID-19 with neutralizing monoclonal antibodies," Cell, vol. 184, no. 12, pp. 3086–3108, Jun. 2021, doi: 10.1016/j.cell.2021.05.005.
[2] D. M. Weinreich et al., "REGEN-COV Antibody Combination and Outcomes in Outpatients with Covid-19," New England Journal of Medicine, vol. 385, no. 23, 2021, doi: 10.1056/NEJMoa2108163.
[3] M. Cox et al., "SARS-CoV-2 variant evasion of monoclonal antibodies based on in vitro studies," Nature Reviews Microbiology, vol. 21, no. 2, pp. 112–124, 2022, doi: 10.1038/s41579-022-00809-7.
[4] J. Zahradník et al., "SARS-CoV-2 variant prediction and antiviral drug design are enabled by RBD in vitro evolution," Nature Microbiology, vol. 6, no. 9, pp. 1188–1198, Aug. 2021, doi: 10.1038/s41564-021-00954-4.
[5] C. D. C. Allen, T. Okada, and J. G. Cyster, "Germinal-Center Organization and Cellular Dynamics," Immunity, vol. 27, no. 2, pp. 190–202, Aug. 2007, doi: 10.1016/j.immuni.2007.07.009.
[6] Y. Adachi et al., "Distinct germinal center selection at local sites shapes memory B cell response to viral escape," Journal of Experimental Medicine, vol. 212, no. 10, pp. 1709–1723, Sep. 2015, doi: 10.1084/jem.20142284.
[7] L. Mesin, J. Ersching, and G. D. Victora, "Germinal Center B Cell Dynamics," Immunity, vol. 45, no. 3, pp. 471–482, Sep. 2016, doi: 10.1016/j.immuni.2016.09.001.
[8] P. A. Robert, A. Rastogi, S. C. Binder, and M. Meyer-Hermann, "How to Simulate a Germinal Center," in Germinal Centers, vol. 1623, D. P. Calado, Ed., New York, NY: Springer New York, 2017, pp. 303–334. doi: 10.1007/978-1-4939-7095-7_22.
[9] S. M. Miller, T. Wang, and D. R. Liu, "Phage-assisted continuous and non-continuous evolution," Nature Protocols, vol. 15, no. 12, pp. 4101–4127, Dec. 2020, doi: 10.1038/s41596-020-00410-3.
[10] C. S. Diercks et al., "An Orthogonal T7 Replisome for Continuous Hypermutation and Accelerated Evolution in E. Coli." Synthetic Biology, Jul. 2024. doi: 10.1101/2024.07.25.605042.
[11] D. S. Glass and I. H. Riedel-Kruse, "A Synthetic Bacterial Cell-Cell Adhesion Toolbox for Programming Multicellular Morphologies and Patterns," Cell, vol. 174, no. 3, pp. 649–658.e16, Jul. 2018, doi: 10.1016/j.cell.2018.06.041.
[12] P. V. Markov, M. Ghafari, M. Beer, M. Leschnik, R. Wolfinger, et al., "The evolution of SARS-CoV-2," Nature Reviews Microbiology, vol. 21, pp. 361–379, 2023, doi: 10.1038/s41579-023-00878-2.
[13] A. H. Badran and D. R. Liu, "Development of potent in vivo mutagenesis plasmids with broad mutational spectra," Nature Communications, vol. 6, no. 1, p. 8425, Oct. 2015, doi: 10.1038/ncomms9425.
[14] R. U. Sheth, S. S. Yim, F. L. Wu, and H. H. Wang, "Multiplex recording of cellular events over time on CRISPR biological tape," Science, vol. 358, no. 6369, pp. 1457–1461, Dec. 2017, doi: 10.1126/science.aao0958.
[15] Y. Xiang et al., "Versatile and multivalent nanobodies efficiently neutralize SARS-CoV-2," Science, vol. 370, no. 6523, pp. 1479–1484, Dec. 2020, doi: 10.1126/science.abe4747.
[16] B. Pérez-Massón et al., "Studying SARS-CoV-2 interactions using phage-displayed receptor binding domain as a model protein," Scientific Reports, vol. 14, no. 1, p. 712, Jan. 2024, doi: 10.1038/s41598-023-50450-4.
[17] L. Riechmann and P. Holliger, "The C-Terminal Domain of TolA Is the Coreceptor for Filamentous Phage Infection of E. coli," Cell, vol. 90, no. 2, pp. 351–360, Jul. 1997, doi: 10.1016/S0092-8674(00)80342-6.
[18] A. Sprumont, A. Rodrigues, S.J. McGowan, C. Bannard, and O. Bannard, "Germinal centers output clonally diverse plasma cell populations expressing high- and low-affinity antibodies," Cell, vol. 186, no. 25, pp. 5486–5499.e13, Dec. 2023, doi: 10.1016/j.cell.2023.10.022.
[19] Zhang, "Evolution of phage display libraries for therapeutic antibody discovery," mAbs, 2023, doi: 10.1080/19420862.2023.2213793.
[20] G.M. Cherf and J.R. Cochran, "Applications of Yeast Surface Display for Protein Engineering," Methods Mol. Biol., vol. 1319, pp. 155–175, 2015.
[21] J. Hanes and A. Plückthun, "In vitro selection and evolution of functional proteins by using ribosome display," PNAS, vol. 94, pp. 4937–4942, 1997.
[22] P.C. Taylor et al., "Neutralizing monoclonal antibodies for treatment of COVID-19," Nature Reviews Immunology, vol. 21, no. 6, 2021, doi: 10.1038/s41577-021-00542-x.
[23] A. Ravikumar et al., "Scalable, Continuous Evolution of Genes at Mutation Rates above Genomic Error Thresholds," Cell, vol. 175, no. 7, 2018, doi: 10.1016/j.cell.2018.10.021.
[24] T.N. Starr, A.J. Greaney, S.K. Hilton, D. Ellis, K.H.D. Crawford, A.S. Dingens, M.J. Navarro, J.E. Bowen, M.A. Tortorici, A.C. Walls, N.P. King, D. Veesler, and J.D. Bloom, "Deep Mutational Scanning of SARS-CoV-2 Receptor Binding Domain Reveals Constraints on Folding and ACE2 Binding," Cell, vol. 182, no. 5, pp. 1295–1310.e20, 2020, doi: 10.1016/j.cell.2020.08.012.
[25] L. Ledsgaard, A. Ljungars, C. Rimbault, C.V. Sørensen, T. Tulika, J. Wade, Y. Wouters, J. McCafferty, and A.H. Laustsen, "Advances in antibody phage display technology," Drug Discovery Today, vol. 27, no. 8, pp. 2151–2169, 2022, doi: 10.1016/j.drudis.2022.05.002.

---

## Tzachi's Comments

- **[a]** Title suggestions:
  - [title 2] Broadly neutralising nanobody cocktails via a Synthetic Germinal Center – PACE Co-Evolution System
  - [title 3] A Programmable Two-Zone Hypermutation–Selection Platform for Rapid, Diverse Neutralizing Nanobody Evolution
- **[b]** "I think you mean conformation of antigen that are present upon entry of virus to the body, but this is not clear"
- **[c]** "we move seamlessly from mAb to nAb, must explain"
- **[d]** "please give estimate of the extent of initial pool clonal diversity"
- **[e]** "@michaelsedbon chromosomal or second plasmid?"
- **[f]** "In the reference paper, it is on a separate plasmid (they actually distribute all the replication proteins into 3 extra plasmids). RP1: T7 helicase-primase (gp4A) + T7 ssDNA-binding protein (gp2.5); RP2: T7 DNA polymerase (gp5); RP3: T7 lysozyme–RNA polymerase translational fusion (gp3.5–gp1). The system is quite heavy, 3 plasmids + the T7 replisome"
- **[g]** "didn't get that..."
- **[h]** "why different from T7 system?"
- **[i]** "The T7 system mutates what has been cloned into the T7 replizome. Here, phages that evaded immunity in the light zones are set to undergo another round of RBD diversification. As they infect E. coli harbouring the mutagenesis plasmid, their genome gets mutated before the phage is assembled, while maintaining genotype-to-phenotype links. To use the T7 system will require an extra cloning steps eveytime the phages return to the RBD mutation loop and the T7 replizome will not be packed in the phage particle (we will loose genotype-to-phenotype link and the ability to use CRISPR tape to track nb-ag binding events)"
- **[j]** "we switch to speak in presence tense e.g. '... e. coli are exposed', but I think we till here spoke in future tense 'e coli will be exposed', which is better"
- **[k]** "explain how toxin is added"
- **[l]** "explain the motivation here better"
- **[m]** "Mentioned in the open call, but should we explain why it meets these technological readiness level by saying where each block of the pipeline sits?"
- **[n]** "From the call"
- **[o]** "The call specifies the 3 years period of fundings"
- **[p]** "In the call, not sure what this means"
- **[q]** "Bibliography must have the 5 most relevant items marked with an asterisk ⭐"

---

## Acronym Ideas

- SynGC-NB — Synthetic Germinal Center for NanoBodies
- EC-GC — E. coli Germinal Center
- nanoGC — nanobody Germinal Center
- GC-PACE — Germinal Center–Phage-Assisted Continuous Evolution
- DARKLIGHT — not an acronym but catchy
- DARWIN — Directed Affinity Refinement With Iterative selection in Nanobodies
- HYPE — HYPermutation Engine
