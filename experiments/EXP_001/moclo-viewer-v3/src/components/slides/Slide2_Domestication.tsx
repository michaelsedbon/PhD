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
                Eliminating internal BsaI sites (GGTCTC/GAGACC) via synonymous codon substitutions
            </p>

            {/* Problem explanation */}
            <div className="slide-section">
                <h2>Internal Site Interference</h2>
                <div className="slide-explanation">
                    <p>
                        Tiles containing internal <strong>BsaI recognition sites</strong> (<code>GGTCTC</code> / <code>GAGACC</code>)
                        are cleaved during Golden Gate assembly, preventing correct ligation.
                        Each site is destroyed by a <strong>single synonymous nucleotide substitution</strong> within the
                        recognition hexamer, preserving the encoded protein.
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
                <h2>OE-PCR Assembly of Domesticated Tiles</h2>
                <div className="slide-explanation">
                    <p>
                        Mutagenic primers encode the synonymous substitution at their 3′ end.
                        Subfragments are amplified individually, then fused by <strong>Overlap Extension PCR (OE-PCR)</strong>
                        using the outer tile primers — yielding the full domesticated tile in two PCR rounds.
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
