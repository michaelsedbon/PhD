import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

/* ── State-of-the-Art comparison data ───────────────────────────────── */

interface PriorWork {
    project: string;
    team: string;
    year: number;
    organism: string;
    size: string;
    approach: string;
    cloning: string;
    highlight: string;
    color: string;
    url: string;
}

const PRIOR_WORKS: PriorWork[] = [
    {
        project: 'Syn61 / GENESIS',
        team: 'Chin Lab (MRC-LMB)',
        year: 2019,
        organism: 'E. coli MDS42',
        size: '4.0 Mb',
        approach: 'REXER — sequential 100 kb segment replacement via λ Red + CRISPR',
        cloning: 'Chemical synthesis → 10 kb stretches assembled into 100 kb BACs in yeast → REXER/GENESIS replaces genomic segments in vivo → directed conjugation merges 8 sections',
        highlight: 'First fully synthetic E. coli. 61-codon genome, recoded all 18,214 TAG, TCA, TCG codons.',
        color: '#4fc3f7',
        url: '/papers/Total_synthesis_Ecoli_recoded_genome.pdf',
    },
    {
        project: 'rE.coli-57',
        team: 'Church Lab (Harvard)',
        year: 2016,
        organism: 'E. coli MG1655',
        size: '4.6 Mb',
        approach: 'Computational design + segment-by-segment synthesis & testing',
        cloning: 'De novo synthesis of 2–4 kb overlapping fragments → assembled into 50 kb segments in yeast → episomal expression in E. coli → λ-integrase for chromosomal integration',
        highlight: 'Designed (not fully assembled) 57-codon genome. Tested 63 segments individually — 91% viable.',
        color: '#81c784',
        url: '/papers/Design,_synthesis,_and_testing_toward.pdf',
    },
    {
        project: 'JCVI-syn3.0',
        team: 'Venter Institute',
        year: 2016,
        organism: 'Mycoplasma mycoides',
        size: '531 kb',
        approach: 'Hierarchical assembly in yeast + genome transplantation',
        cloning: 'Chemical synthesis of oligos → 1.4 kb fragments → 7 kb cassettes (E. coli) → one-eighth genome segments (yeast) → full genome assembly in yeast → transplantation into M. capricolum',
        highlight: 'Minimal genome: 473 genes. First "cell controlled by a chemically synthesized genome" (2010).',
        color: '#ffb74d',
        url: '/papers/Design_and_synthesis_of_a.pdf',
    },
    {
        project: 'Sc2.0',
        team: 'International Consortium',
        year: 2017,
        organism: 'S. cerevisiae',
        size: '12.0 Mb (16 chr)',
        approach: 'Bottom-up synthetic chromosome assembly with SCRaMbLE recombination sites',
        cloning: 'Chemical synthesis of ~750 bp "building blocks" → assembled into 2–4 kb "minichunks" → 10 kb "chunks" → 30–60 kb "megachunks" → full chromosomes, all via homologous recombination in yeast',
        highlight: 'First synthetic eukaryotic chromosomes. Modular design with loxPsym sites for combinatorial rearrangement.',
        color: '#ce93d8',
        url: 'https://doi.org/10.1126/science.aaf4557',
    },
    {
        project: 'Kohara Clone Bank',
        team: 'Kohara, Akiyama & Isono',
        year: 1987,
        organism: 'E. coli K-12 W3110',
        size: '4.7 Mb',
        approach: 'Lambda phage genomic library — ordered overlapping clones',
        cloning: 'Partial Sau3AI digestion of genomic DNA → ligation into λ phage vectors → plaque isolation → restriction mapping via partial digests + vector-probe hybridization → computer-sorted ordering',
        highlight: 'First physical map of E. coli. Standard resource for 15+ years but NOT modular / assembly-ready.',
        color: '#a1887f',
        url: '/papers/The_physical_map_of_the.pdf',
    },
    {
        project: 'CATCH',
        team: 'Jiang & Zhu (Tsinghua)',
        year: 2015,
        organism: 'E. coli (and others)',
        size: 'Up to 100 kb',
        approach: 'Cas9 in-vitro excision of target chromosome segments + Gibson assembly',
        cloning: 'Bacterial cells lysed in agarose gel plugs → RNA-guided Cas9 cleaves chromosome at two designed loci → target segment isolated → Gibson assembly into cloning vector',
        highlight: 'One-step targeted cloning of large gene clusters. Up to 100 kb in a single step — but NOT modular and no standardized overhangs.',
        color: '#90caf9',
        url: 'https://doi.org/10.1038/ncomms9101',
    },
    {
        project: 'ASKA Library',
        team: 'NIG Japan',
        year: 2005,
        organism: 'E. coli K-12',
        size: '4,122 ORFs',
        approach: 'Individual ORF cloning into expression vectors (His-tag + GFP)',
        cloning: 'PCR amplification of each ORF with SfiI-flanked primers → SfiI digestion → ligation into pCA24N vector (IPTG-inducible, His-tag + GFP fusion) → individual clone verification',
        highlight: 'Complete ORFeome. Individual genes only — no intergenic regions, not assembly-compatible.',
        color: '#ef9a9a',
        url: '/papers/Complete_set_of_ORF_clones.pdf',
    },
    {
        project: 'CAPTURE',
        team: 'Zhao Lab (UIUC)',
        year: 2021,
        organism: 'Various bacteria',
        size: '10–113 kb',
        approach: 'Cas12a in-vitro digestion + T4 polymerase assembly + in vivo Cre-lox circularization',
        cloning: 'Cas12a staggered cuts release target fragment → T4 polymerase exo+fill-in assembles with two DNA receivers carrying loxP sites → linear product transformed into E. coli with Cre helper plasmid → in vivo circularization',
        highlight: '47 BGCs cloned at ~100% efficiency, up to 113 kb. 150× more efficient than in vitro. But targets specific loci — NOT a tiling library.',
        color: '#66bb6a',
        url: 'https://doi.org/10.1038/s41467-021-21275-4',
    },
    {
        project: 'CReATiNG',
        team: 'Ehrenreich Lab (USC)',
        year: 2023,
        organism: 'S. cerevisiae',
        size: '230 kb (ChrI)',
        approach: 'Cas9 excision of natural chromosome segments + BAC/YAC capture + in vivo assembly',
        cloning: 'Cas9 + gRNAs excise 51–64 kb segments in donor yeast → captured in BAC/YAC vector (pASC1) with programmable adapter sequences → segments co-transformed into recipient yeast → assembled via homologous recombination',
        highlight: 'Closest to our approach: tiled natural segments with programmable adapters. Built 27 recombinant chromosomes. But yeast-only, NOT Golden Gate.',
        color: '#ab47bc',
        url: 'https://doi.org/10.1038/s41467-023-44112-2',
    },
    {
        project: 'BASIS / CGS',
        team: 'Chin Lab (MRC-LMB)',
        year: 2023,
        organism: 'E. coli',
        size: '0.5–1.1 Mb',
        approach: 'BAC stepwise insertion + continuous genome synthesis',
        cloning: 'BASIS: stepwise insertion of synthetic DNA segments into BAC episomes → assembled 1.1 Mb human DNA. CGS: sequential replacement of 100 kb genomic stretches with synthetic DNA → 0.5 Mb E. coli genome in 10 days',
        highlight: 'Megabase-scale assembly pipeline. Used to build Syn57 (2025). But a synthesis pipeline — NOT a reusable modular parts library.',
        color: '#42a5f5',
        url: 'https://doi.org/10.1038/s41586-023-06268-1',
    },
];

export default function Slide0StateOfTheArt({ data }: Props) {
    const { stats } = data.bundle;

    return (
        <div className="slide">
            <h1 className="slide-title">State of the Art</h1>
            <p className="slide-subtitle">
                Synthetic genomes & genome-scale clone libraries — what exists, and what's missing
            </p>

            {/* Comparison table */}
            <div className="slide-section">
                <div className="sota-table-wrapper">
                    <table className="sota-table">
                        <thead>
                            <tr>
                                <th>Project</th>
                                <th>Year</th>
                                <th>Organism</th>
                                <th>Size</th>
                                <th>DNA Construction</th>
                                <th>Key Insight</th>
                            </tr>
                        </thead>
                        <tbody>
                            {PRIOR_WORKS.map((w) => (
                                <tr key={w.project}>
                                    <td>
                                        <a
                                            href={w.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="sota-project-link"
                                            style={{ borderLeftColor: w.color }}
                                        >
                                            {w.project}
                                            <span className="sota-link-icon">↗</span>
                                        </a>
                                    </td>
                                    <td className="sota-year">{w.year}</td>
                                    <td className="sota-org"><em>{w.organism}</em></td>
                                    <td className="sota-size">{w.size}</td>
                                    <td className="sota-cloning">{w.cloning}</td>
                                    <td className="sota-highlight">{w.highlight}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Gap identification */}
            <div className="slide-section">
                <h2>The Gap — Why Build a MoClo Library?</h2>
                <div className="sota-gap-grid">
                    <div className="sota-gap-card problem">
                        <div className="sota-gap-icon">⚠️</div>
                        <h3>No Modular Genome Library Exists</h3>
                        <p>
                            Syn61 produced a <strong>finished strain</strong> — not reusable parts.
                            CReATiNG tiles natural chromosome segments with adapters — but is <strong>yeast-only</strong> and uses homologous recombination.
                            CAPTURE and BASIS/CGS clone large fragments but are <strong>not modular libraries</strong>.
                            No group has built a <strong>MoClo-tiled, Golden Gate–compatible</strong> library of <em>E.&nbsp;coli</em>.
                        </p>
                    </div>
                    <div className="sota-gap-card solution">
                        <div className="sota-gap-icon">🧬</div>
                        <h3>Our Approach — {stats.total_tiles} MoClo Tiles</h3>
                        <p>
                            <strong>{stats.total_tiles} Lvl0 parts</strong> with <strong>standardized overhangs</strong> —
                            every tile at the same position is <strong>interchangeable</strong> across all {stats.total_lvl1_groups} Lvl1 groups,
                            enabling <strong>combinatorial genome assembly</strong> and chimeric constructs.
                        </p>
                    </div>
                </div>
            </div>

            {/* Timeline */}
            <div className="slide-section">
                <h2>Timeline</h2>
                <div className="sota-timeline">
                    {[...PRIOR_WORKS].sort((a, b) => a.year - b.year).map((w) => (
                        <div className="sota-timeline-item" key={w.project}>
                            <div className="sota-timeline-dot" style={{ background: w.color }} />
                            <div className="sota-timeline-year">{w.year}</div>
                            <div className="sota-timeline-label">{w.project}</div>
                        </div>
                    ))}
                    <div className="sota-timeline-item ours">
                        <div className="sota-timeline-dot" style={{ background: '#00e5ff' }} />
                        <div className="sota-timeline-year">2026</div>
                        <div className="sota-timeline-label">MoClo Genome Library (Ours)</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
