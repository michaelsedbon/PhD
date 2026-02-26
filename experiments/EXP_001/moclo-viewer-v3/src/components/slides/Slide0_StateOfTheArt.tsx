import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

/* ── Relevant bibliography ──────────────────────────────────────────── */

interface Reference {
    project: string;
    team: string;
    year: number;
    organism: string;
    size: string;
    method: string;
    relevance: string;
    color: string;
    url: string;
}

const REFERENCES: Reference[] = [
    {
        project: 'CATCH',
        team: 'Jiang & Zhu (Tsinghua)',
        year: 2015,
        organism: 'E. coli (and others)',
        size: 'Up to 100 kb',
        method: 'In-vitro Cas9 excision from gel plugs + Gibson assembly into cloning vector',
        relevance: 'First targeted cloning of large genome segments. Proven on E. coli.',
        color: '#90caf9',
        url: 'https://doi.org/10.1038/ncomms9101',
    },
    {
        project: 'CAPTURE',
        team: 'Zhao Lab (UIUC)',
        year: 2021,
        organism: 'Various bacteria',
        size: '10–113 kb',
        method: 'Cas12a digestion + T4 polymerase assembly + in vivo Cre-lox circularization',
        relevance: '~100% cloning efficiency up to 113 kb. 150× more efficient than CATCH.',
        color: '#66bb6a',
        url: 'https://doi.org/10.1038/s41467-021-21275-4',
    },
    {
        project: 'CReATiNG',
        team: 'Ehrenreich Lab (USC)',
        year: 2023,
        organism: 'S. cerevisiae',
        size: '51–64 kb segments',
        method: 'Cas9 excision + BAC/YAC capture + homologous recombination assembly in yeast',
        relevance: 'Tiled chromosome segments with programmable adapters. Closest to a modular library concept.',
        color: '#ab47bc',
        url: 'https://doi.org/10.1038/s41467-023-44112-2',
    },
    {
        project: 'REXER / GENESIS',
        team: 'Chin Lab (MRC-LMB)',
        year: 2019,
        organism: 'E. coli',
        size: '100 kb replacement',
        method: 'λ Red recombination + CRISPR selection for sequential genome segment replacement',
        relevance: 'Proven for replacing 100 kb E. coli genome segments. Used to build Syn61.',
        color: '#4fc3f7',
        url: 'https://doi.org/10.1038/s41596-020-00464-3',
    },
    {
        project: 'BASIS / CGS',
        team: 'Chin Lab (MRC-LMB)',
        year: 2023,
        organism: 'E. coli',
        size: '0.5–1.1 Mb',
        method: 'BAC stepwise insertion + continuous genome synthesis',
        relevance: 'Megabase assembly in E. coli BACs. Built Syn57 (2025).',
        color: '#42a5f5',
        url: 'https://doi.org/10.1038/s41586-023-06268-1',
    },
];

/* ── Technique analysis ─────────────────────────────────────────────── */

interface Technique {
    name: string;
    applicable: string;
    applicableClass: string;
    pros: string[];
    cons: string[];
    color: string;
}

const TECHNIQUES: Technique[] = [
    {
        name: 'CAPTURE',
        applicable: '✅ Best fit for extraction',
        applicableClass: 'applicability-yes',
        color: '#66bb6a',
        pros: [
            '~100% efficiency up to 113 kb — proven on diverse bacteria',
            'Works in E. coli, complete in 3–4 days',
            'Just design 2 guide RNAs per 100 kb region — trivial',
            'Direct cloning into any vector, including T7 replisome plasmid',
        ],
        cons: [
            'Each 100 kb region is a one-off clone — no modularity',
            'To target a different region, redesign gRNAs and repeat',
            'No ability to mix-and-match sub-regions after mutagenesis',
        ],
    },
    {
        name: 'CATCH',
        applicable: '✅ Viable alternative',
        applicableClass: 'applicability-yes',
        color: '#90caf9',
        pros: [
            'Simpler protocol — Cas9 + Gibson assembly in one step',
            'Proven on E. coli genome up to 100 kb',
        ],
        cons: [
            'Gibson assembly efficiency drops significantly at 100 kb',
            'Lower colony yield than CAPTURE for large fragments',
            'Same one-off limitation as CAPTURE',
        ],
    },
    {
        name: 'CReATiNG',
        applicable: '⚠️ Not directly applicable',
        applicableClass: 'applicability-partial',
        color: '#ab47bc',
        pros: [
            'Programmable adapters — closest to a modular tiling concept',
            'Could mutagenize segments in yeast before transfer',
        ],
        cons: [
            'Yeast-only — would need to shuttle DNA back to E. coli for T7',
            'Assembly via HR, not a standardized system',
            'Max demonstrated size ~64 kb, not 100 kb',
        ],
    },
    {
        name: 'MoClo Tiling',
        applicable: '✅ Designed — see next slides',
        applicableClass: 'applicability-yes',
        color: '#00e5ff',
        pros: [
            'Full genome pre-tiled into standardized ~7 kb parts',
            'Assemble any combination of tiles into larger constructs',
            'After T7 mutagenesis, dissect which tiles carry beneficial mutations',
            'Swap individual wild-type / mutant tiles → combinatorial testing',
        ],
        cons: [
            'Large upfront investment: ~686 cloning reactions to build the library',
            'BsaI domestication required for ~30% of tiles',
            '~7 kb tiles → need multi-level assembly (Lvl1/Lvl2) to reach 100 kb',
            'Golden Gate efficiency decreases beyond ~30 kb per level',
        ],
    },
];

export default function Slide0StateOfTheArt({ data }: Props) {
    const { stats } = data.bundle;

    return (
        <div className="slide">
            <h1 className="slide-title">Cloning Large <em>E. coli</em> Genome Segments</h1>
            <p className="slide-subtitle">
                How to clone ~100 kb of the <em>E. coli</em> genome into a T7 replisome for high-rate mutagenesis
            </p>

            {/* Intro */}
            <div className="slide-section">
                <div className="sota-intro-box">
                    <div className="sota-intro-goal">
                        <div className="sota-intro-icon">🎯</div>
                        <div>
                            <h3>Objective</h3>
                            <p>
                                Clone <strong>~100 kb chunks</strong> of the <em>E. coli</em> MG1655 genome
                                into a <strong>T7 replisome vector</strong>, where the T7 DNA polymerase's
                                low fidelity provides <strong>elevated mutation rates</strong> on the cloned
                                region. Select for phenotypes, then characterize the mutations.
                            </p>
                        </div>
                    </div>
                    <div className="sota-intro-question">
                        <div className="sota-intro-icon">❓</div>
                        <div>
                            <h3>Key Question</h3>
                            <p>
                                What is the <strong>best cloning strategy</strong> to get 100 kb of genomic DNA
                                into the T7 vector? Is a full MoClo tiling library necessary, or can we
                                use <strong>direct cloning</strong> methods like CAPTURE?
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bibliography table */}
            <div className="slide-section">
                <h2>Relevant Bibliography</h2>
                <div className="sota-table-wrapper">
                    <table className="sota-table">
                        <thead>
                            <tr>
                                <th>Project</th>
                                <th>Year</th>
                                <th>Organism</th>
                                <th>Size</th>
                                <th>Method</th>
                                <th>Why It Matters</th>
                            </tr>
                        </thead>
                        <tbody>
                            {REFERENCES.map((r) => (
                                <tr key={r.project}>
                                    <td>
                                        <a
                                            href={r.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="sota-project-link"
                                            style={{ borderLeftColor: r.color }}
                                        >
                                            {r.project}
                                            <span className="sota-link-icon">↗</span>
                                        </a>
                                    </td>
                                    <td className="sota-year">{r.year}</td>
                                    <td className="sota-org"><em>{r.organism}</em></td>
                                    <td className="sota-size">{r.size}</td>
                                    <td className="sota-cloning">{r.method}</td>
                                    <td className="sota-highlight">{r.relevance}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Technique analysis */}
            <div className="slide-section">
                <h2>Analysis of Relevant Techniques</h2>
                <p className="slide-sub-desc">
                    Which methods can clone ~100 kb <em>E. coli</em> genomic DNA into a T7 replisome vector?
                </p>
                <div className="sota-table-wrapper">
                    <table className="sota-table applicability-table">
                        <thead>
                            <tr>
                                <th>Method</th>
                                <th>Verdict</th>
                                <th>Pros</th>
                                <th>Cons</th>
                            </tr>
                        </thead>
                        <tbody>
                            {TECHNIQUES.map((t) => (
                                <tr key={t.name}>
                                    <td
                                        className="sota-project-link"
                                        style={{ borderLeftColor: t.color }}
                                    >
                                        {t.name}
                                    </td>
                                    <td className={t.applicableClass}>{t.applicable}</td>
                                    <td className="applicability-pros">
                                        <ul className="pros-cons-list">
                                            {t.pros.map((p, i) => <li key={i}>{p}</li>)}
                                        </ul>
                                    </td>
                                    <td className="applicability-cons">
                                        <ul className="pros-cons-list">
                                            {t.cons.map((c, i) => <li key={i}>{c}</li>)}
                                        </ul>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Conclusion */}
            <div className="slide-section">
                <h2>Conclusion</h2>
                <div className="sota-gap-grid">
                    <div className="sota-gap-card problem">
                        <div className="sota-gap-icon">⚡</div>
                        <h3>Simplest Path: CAPTURE</h3>
                        <p>
                            For <strong>one-shot cloning</strong> of a 100 kb region into T7,
                            <strong> CAPTURE is the fastest and most efficient method</strong>.
                            Design 2 guide RNAs, extract the chunk, assemble into the T7 vector.
                            Done in 3–4 days at ~100% efficiency.
                            No library construction needed.
                        </p>
                    </div>
                    <div className="sota-gap-card solution">
                        <div className="sota-gap-icon">🧬</div>
                        <h3>MoClo: For Downstream Dissection</h3>
                        <p>
                            A MoClo tiling adds value <strong>after</strong> mutagenesis — if you want to
                            identify which sub-region carries the beneficial mutation and recombine
                            tiles from different mutagenesis experiments.
                            A complete <strong>{stats.total_tiles}-tile genome design</strong> has been
                            prepared — <strong>explore it in the following slides</strong>.
                        </p>
                    </div>
                </div>
            </div>

            {/* Timeline */}
            <div className="slide-section">
                <h2>Timeline</h2>
                <div className="sota-timeline">
                    {[...REFERENCES].sort((a, b) => a.year - b.year).map((r) => (
                        <div className="sota-timeline-item" key={r.project}>
                            <div className="sota-timeline-dot" style={{ background: r.color }} />
                            <div className="sota-timeline-year">{r.year}</div>
                            <div className="sota-timeline-label">{r.project}</div>
                        </div>
                    ))}
                    <div className="sota-timeline-item ours">
                        <div className="sota-timeline-dot" style={{ background: '#00e5ff' }} />
                        <div className="sota-timeline-year">2026</div>
                        <div className="sota-timeline-label">MoClo Genome Library</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
