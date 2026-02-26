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
                            The Kohara bank and ASKA library are <strong>not assembly-compatible</strong>.
                            No group has built a <strong>MoClo-tiled, interchangeable</strong> library of <em>E.&nbsp;coli</em>.
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
