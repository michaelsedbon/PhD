import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

export default function Slide2Domestication({ data }: Props) {
    const { stats } = data.bundle;

    // Count total BsaI sites and subfragments
    let totalSites = 0;
    let totalSubfragments = 0;
    let totalMutagenicOligos = 0;
    for (const tile of data.bundle.tiles) {
        if (tile.domestication) {
            totalSites += tile.domestication.n_sites;
            totalSubfragments += tile.domestication.subfragments.length;
            totalMutagenicOligos += tile.domestication.primers.length * 2;
        }
    }

    return (
        <div className="slide">
            <h1 className="slide-title">Domestication Process</h1>
            <p className="slide-subtitle">
                Removing internal BsaI recognition sites by silent mutation
            </p>

            {/* Problem explanation */}
            <div className="slide-section">
                <h2>The Problem</h2>
                <div className="slide-explanation">
                    <p>
                        Golden Gate cloning uses <strong>BsaI</strong> (a Type IIS restriction enzyme) to cut DNA at precise positions.
                        If a Lvl0 tile contains <strong>internal BsaI recognition sites</strong> (<code>GGTCTC</code> or its
                        reverse complement <code>GAGACC</code>), the enzyme will cut inside the tile — destroying the insert.
                    </p>
                </div>

                {/* Diagram: BsaI cutting inside vs outside */}
                <div className="slide-diagram">
                    <div className="diagram-row">
                        <div className="diagram-label good">✓ GG-Ready Tile</div>
                        <div className="diagram-construct">
                            <span className="d-part bsai">BsaI▸</span>
                            <span className="d-part oh">AATA</span>
                            <span className="d-part insert good">Genomic Insert — no internal BsaI</span>
                            <span className="d-part oh">AACT</span>
                            <span className="d-part bsai">◂BsaI</span>
                        </div>
                    </div>
                    <div className="diagram-row">
                        <div className="diagram-label bad">✗ Blocked Tile</div>
                        <div className="diagram-construct">
                            <span className="d-part bsai">BsaI▸</span>
                            <span className="d-part oh">AATA</span>
                            <span className="d-part insert bad">
                                Genomic Insert — <span className="d-cut">✂ GGTCTC</span> — rest of insert
                            </span>
                            <span className="d-part oh">AACT</span>
                            <span className="d-part bsai">◂BsaI</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Solution */}
            <div className="slide-section">
                <h2>The Solution — Silent Mutations + OE-PCR</h2>
                <div className="slide-explanation">
                    <p>
                        Each internal BsaI site is destroyed by a <strong>single silent nucleotide change</strong> —
                        the codon is altered but the encoded amino acid remains the same. The mutagenic primers
                        are used in an <strong>Overlap Extension PCR (OE-PCR)</strong> workflow to assemble the
                        domesticated tile from subfragments.
                    </p>
                </div>

                {/* OE-PCR diagram */}
                <div className="slide-diagram">
                    <div className="diagram-label neutral">OE-PCR Workflow</div>
                    <div className="oep-flow">
                        <div className="oep-step">
                            <div className="oep-num">1</div>
                            <div className="oep-text">Amplify subfragments with mutagenic primers</div>
                        </div>
                        <div className="oep-arrow">→</div>
                        <div className="oep-step">
                            <div className="oep-num">2</div>
                            <div className="oep-text">Subfragments overlap at mutation sites</div>
                        </div>
                        <div className="oep-arrow">→</div>
                        <div className="oep-step">
                            <div className="oep-num">3</div>
                            <div className="oep-text">Final PCR assembles the full domesticated tile</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats */}
            <div className="slide-stats-row">
                <div className="slide-stat">
                    <div className="slide-stat-value red">{stats.blocked_tiles}</div>
                    <div className="slide-stat-label">Tiles to Domesticate</div>
                </div>
                <div className="slide-stat">
                    <div className="slide-stat-value orange">{totalSites}</div>
                    <div className="slide-stat-label">BsaI Sites to Remove</div>
                </div>
                <div className="slide-stat">
                    <div className="slide-stat-value purple">{totalMutagenicOligos}</div>
                    <div className="slide-stat-label">Mutagenic Oligos</div>
                </div>
                <div className="slide-stat">
                    <div className="slide-stat-value blue">{totalSubfragments}</div>
                    <div className="slide-stat-label">OE-PCR Subfragments</div>
                </div>
            </div>

            {/* Interactive figures */}
            <div className="slide-figures-row">
                <div className="slide-figure">
                    <h3>Before vs After Domestication</h3>
                    <iframe src="/figures/domestication_before_after.html" title="Domestication before/after" />
                </div>
                <div className="slide-figure">
                    <h3>Domestication Effort by Group</h3>
                    <iframe src="/figures/domestication_effort.html" title="Domestication effort" />
                </div>
            </div>
        </div>
    );
}
