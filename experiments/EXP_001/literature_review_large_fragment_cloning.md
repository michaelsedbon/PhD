# Literature Review — Large Fragment Cloning for T7 Replisome Mutagenesis

**Date:** 2026-02-26  
**Context:** EXP_001 — Which method best serves our goal of cloning ~100 kb *E. coli* genome segments into a T7 replisome for high-rate mutagenesis?

---

## Objective

Clone **~100 kb chunks** of the *E. coli* MG1655 genome into a **T7 replisome vector**, where the T7 DNA polymerase's low fidelity provides elevated mutation rates on the cloned region. After selection for phenotypes, characterize the mutations.

---

## Relevant Papers

| Paper | Year | Lab | Key Achievement |
|-------|------|-----|-----------------|
| **CATCH** — Cas9-Assisted Targeting of CHromosome segments | 2015 | Jiang & Zhu (Tsinghua) | First targeted cloning of large (up to 100 kb) genome segments via in-vitro Cas9 excision + Gibson assembly |
| **CAPTURE** — Cas12a-Assisted Precise Targeted cloning Using in vivo Cre-lox REcombination | 2021 | Zhao Lab (UIUC) | ~100% cloning efficiency up to 113 kb. 150× more efficient than CATCH. Works on diverse bacteria |
| **CReATiNG** — Cloning, Reprogramming, and Assembling Tiled Natural Genomic DNA | 2023 | Ehrenreich Lab (USC) | Tiled chromosome segments with programmable adapters in yeast. Closest to a modular library concept |
| **REXER / GENESIS** — Replicon EXcision Enhanced Recombination | 2019 | Chin Lab (MRC-LMB) | Proven replacement of 100 kb *E. coli* genome segments. Used to build Syn61 |
| **BASIS / CGS** — BAC Stepwise Insertion + Continuous Genome Synthesis | 2023 | Chin Lab (MRC-LMB) | Megabase-scale genome assembly in *E. coli* BACs. Built Syn57 (rE.coli-57, 2025) |

---

## Analysis: Which Technique for Our Goal?

### CAPTURE — Best fit for one-shot extraction

| | |
|---|---|
| **Verdict** | ✅ Best fit for extraction |
| **How it works** | Cas12a cuts flanking the target region → T4 polymerase assembles into vector → in vivo Cre-lox circularizes in *E. coli* |
| **Pros** | ~100% efficiency up to 113 kb; works in *E. coli*; done in 3–4 days; just 2 guide RNAs per region; direct cloning into any vector including T7 replisome |
| **Cons** | Each 100 kb region is a one-off clone — no modularity; to target a different region, redesign gRNAs and repeat; no ability to mix-and-match sub-regions after mutagenesis |

### CATCH — Viable alternative

| | |
|---|---|
| **Verdict** | ✅ Viable but less efficient |
| **How it works** | In-vitro Cas9 excision from gel plugs + Gibson assembly into cloning vector |
| **Pros** | Simpler protocol; proven on *E. coli* up to 100 kb |
| **Cons** | Gibson assembly efficiency drops at 100 kb; lower colony yield than CAPTURE; same one-off limitation |

### CReATiNG — Not directly applicable

| | |
|---|---|
| **Verdict** | ⚠️ Yeast-only |
| **How it works** | Cas9 excision + BAC/YAC capture + HR assembly in yeast with programmable adapters |
| **Pros** | Programmable adapters — closest to a modular tiling concept; could mutagenize segments in yeast before transfer |
| **Cons** | Yeast-only — would need to shuttle back to *E. coli* for T7; assembly via HR, not standardized; max demonstrated ~64 kb |

### MoClo Tiling — For downstream dissection

| | |
|---|---|
| **Verdict** | ✅ Designed (see viewer) |
| **How it works** | Genome pre-tiled into 686 standardized ~7 kb Lvl0 parts → Golden Gate assembly into Lvl1/Lvl2 |
| **Pros** | Full genome coverage in reusable parts; assemble any combination of tiles; after T7 mutagenesis, identify which tile carries the mutation; swap WT/mutant tiles for combinatorial testing |
| **Cons** | ~686 cloning reactions upfront; BsaI domestication needed for ~30% of tiles; multi-level assembly (Lvl1/Lvl2) to reach 100 kb; Golden Gate efficiency decreases beyond ~30 kb per level |

---

## Conclusion

**For one-shot cloning of a 100 kb region into T7, CAPTURE is the fastest and most efficient method.** Design 2 guide RNAs, extract the chunk, assemble into the T7 vector. Done in 3–4 days at ~100% efficiency. No library construction needed.

**MoClo adds value after mutagenesis** — if the goal is to identify *which* sub-region carries a beneficial mutation and recombine tiles from different mutagenesis experiments. The 686-tile genome design has been prepared and is documented in the MoClo Viewer.

### Decision matrix

| If your goal is… | Use… |
|---|---|
| Clone one 100 kb region → T7 → select | **CAPTURE** |
| Clone multiple different 100 kb regions → T7 → select | **CAPTURE** (repeat with new gRNAs, still simpler) |
| After mutagenesis, figure out which ~7 kb sub-region matters | **MoClo** (swap tiles, test combinations) |
| Build a permanent, reusable genome library | **MoClo** |
| Reinsert mutated chunks back into the genome | **REXER/GENESIS** (proven for 100 kb replacement) |

---

## References

1. Jiang, W. et al. (2015). Cas9-Assisted Targeting of CHromosome segments CATCH enables one-step targeted cloning of large gene clusters. *Nat. Commun.*, 6, 8101. [DOI: 10.1038/ncomms9101](https://doi.org/10.1038/ncomms9101)
2. Liang, M. et al. (2021). CAPTURE: Cas12a-Assisted Precise Targeted cloning Using in vivo Cre-lox REcombination. *Nat. Commun.*, 12, 1039. [DOI: 10.1038/s41467-021-21275-4](https://doi.org/10.1038/s41467-021-21275-4)
3. Hughes, R.A. et al. (2023). Building synthetic chromosomes from natural DNA. *Nat. Commun.*, 14, 8337. [DOI: 10.1038/s41467-023-44112-2](https://doi.org/10.1038/s41467-023-44112-2)
4. Fredens, J. et al. (2019). Total synthesis of *Escherichia coli* with a recoded genome. *Nature*, 569, 514-518. [DOI: 10.1038/s41586-019-1192-5](https://doi.org/10.1038/s41586-019-1192-5)
5. Robertson, W.E. et al. (2023). Sense codon reassignment enables viral resistance and encoded polymer synthesis. *Science*, 372, 1057. [DOI: 10.1038/s41586-023-06268-1](https://doi.org/10.1038/s41586-023-06268-1)
