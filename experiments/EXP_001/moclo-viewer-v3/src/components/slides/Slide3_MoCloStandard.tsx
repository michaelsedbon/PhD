import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

export default function Slide3MoCloStandard({ data }: Props) {
    const overhangs = data.bundle.design.standard_overhangs;
    const tilesPerGroup = data.bundle.design.tiles_per_group;

    return (
        <div className="slide">
            <h1 className="slide-title">MoClo Standard — Standardized Adapters</h1>
            <p className="slide-subtitle">
                Type IIS Golden Gate cloning with interchangeable positional overhangs
            </p>

            {/* Golden Gate mechanism */}
            <div className="slide-section">
                <h2>Golden Gate Assembly</h2>
                <div className="slide-explanation">
                    <p>
                        <strong>BsaI</strong> is a Type IIS restriction enzyme — it cuts <strong>outside</strong> its
                        recognition site, producing a programmable 4-nt overhang. Parts with matching overhangs are
                        ligated directionally in a single-pot reaction.
                    </p>
                </div>

                <div className="slide-diagram">
                    <div className="diagram-label neutral">BsaI Cloning Mechanism</div>
                    <div className="diagram-construct bsai-mech">
                        <span className="d-part bsai">GGTCTC</span>
                        <span className="d-part spacer">N₁</span>
                        <span className="d-part oh-large">NNNN</span>
                        <span className="d-arrow">⟶ cuts here, leaving 4-nt overhang</span>
                    </div>
                </div>
            </div>

            {/* V2 innovation */}
            <div className="slide-section">
                <h2>V2 Innovation — Standardized Overhangs</h2>
                <div className="slide-explanation">
                    <p>
                        Instead of using genome-derived overhangs (V1), V2 assigns <strong>{overhangs.length} fixed 4-nt
                            overhangs</strong> to positional junctions. Every tile at position <em>i</em> in
                        any Lvl1 group uses the <strong>same flanking overhangs</strong> — making them fully interchangeable.
                    </p>
                </div>

                {/* Overhang table */}
                <div className="overhang-grid">
                    {overhangs.map((oh, i) => {
                        const junctionLabel = i === 0
                            ? 'BB → T0'
                            : i === overhangs.length - 1
                                ? `T${i - 1} → BB`
                                : `T${i - 1} → T${i}`;
                        return (
                            <div key={i} className="overhang-card">
                                <div className="oh-pos">Pos {i}</div>
                                <div className="oh-seq">{oh}</div>
                                <div className="oh-junction">{junctionLabel}</div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Construct diagram */}
            <div className="slide-section">
                <h2>Lvl0 Construct Design</h2>
                <div className="slide-diagram">
                    <div className="diagram-label neutral">Lvl0 in pICH Backbone</div>
                    <div className="diagram-construct">
                        <span className="d-part backbone">pICH</span>
                        <span className="d-arrow-sm">—</span>
                        <span className="d-part bsai">BsaI▸</span>
                        <span className="d-part oh">OH_L</span>
                        <span className="d-part insert good">Genomic Insert (~6.7 kb avg)</span>
                        <span className="d-part oh">OH_R</span>
                        <span className="d-part bsai">◂BsaI</span>
                        <span className="d-arrow-sm">—</span>
                        <span className="d-part backbone">pICH</span>
                    </div>
                </div>
            </div>

            {/* Key benefit */}
            <div className="slide-highlight-box">
                <div className="highlight-icon">🔄</div>
                <div className="highlight-text">
                    <strong>Interchangeability:</strong> Any of the {tilesPerGroup} tiles at position <em>i</em> can be used
                    in <strong>any</strong> of the {data.bundle.stats.total_lvl1_groups} Lvl1 groups without redesigning primers.
                </div>
            </div>
        </div>
    );
}
