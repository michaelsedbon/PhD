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
            <h1 className="slide-title">MoClo Standard — Positional Overhangs</h1>
            <p className="slide-subtitle">
                Standardized 4-nt overhang set enabling combinatorial tile interchange across all Lvl1 groups
            </p>

            {/* Golden Gate mechanism */}
            <div className="slide-section">
                <h2>BsaI Cut Mechanism</h2>
                <div className="slide-explanation">
                    <p>
                        BsaI (GGTCTC) cleaves 1/5 nt downstream, generating programmable 4-nt 5′-overhangs.
                        Ligation is directional and scarless in a single-pot restriction–ligation cycle.
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
                <h2>Standardized Overhang Set</h2>
                <div className="slide-explanation">
                    <p>
                        V2 assigns <strong>{overhangs.length} fixed 4-nt overhangs</strong> to positional junctions.
                        Every tile at position <em>i</em> in any Lvl1 group uses the <strong>same flanking overhangs</strong> —
                        enabling direct combinatorial interchange without primer redesign.
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
                    <div className="diagram-label neutral">Lvl0 in Backbone</div>
                    <div className="diagram-construct">
                        <span className="d-part backbone">Backbone</span>
                        <span className="d-arrow-sm">—</span>
                        <span className="d-part bsai">BsaI▸</span>
                        <span className="d-part oh">OH_L</span>
                        <span className="d-part insert good">Genomic Insert (~6.7 kb avg)</span>
                        <span className="d-part oh">OH_R</span>
                        <span className="d-part bsai">◂BsaI</span>
                        <span className="d-arrow-sm">—</span>
                        <span className="d-part backbone">Backbone</span>
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
