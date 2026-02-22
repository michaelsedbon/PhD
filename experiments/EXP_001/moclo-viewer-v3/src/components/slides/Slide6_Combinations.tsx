import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

export default function Slide6Combinations({ data, onEnterExplorer }: Props) {
    const { stats, design } = data.bundle;
    const tilesPerPos = stats.total_lvl1_groups; // each position has as many tiles as groups

    // Calculate combos per position
    const readyByPosition: number[] = [];
    for (let p = 0; p < design.tiles_per_group; p++) {
        const count = data.bundle.tiles.filter(t => t.position === p && t.gg_ready).length;
        readyByPosition.push(count);
    }

    // Total combinations (product of tiles per position) — use log to avoid BigInt issues
    const logCombinations = readyByPosition.reduce((acc, n) => acc + Math.log10(Math.max(n, 1)), 0);
    let combinationStr: string;
    if (logCombinations > 15) {
        combinationStr = `${Math.pow(10, logCombinations - Math.floor(logCombinations)).toFixed(1)} × 10^${Math.floor(logCombinations)}`;
    } else if (logCombinations > 6) {
        const val = Math.pow(10, logCombinations);
        const exp = Math.floor(logCombinations);
        const mantissa = Math.pow(10, logCombinations - exp);
        combinationStr = `${mantissa.toFixed(1)} × 10^${exp}`;
    } else {
        combinationStr = Math.round(Math.pow(10, logCombinations)).toLocaleString();
    }

    return (
        <div className="slide">
            <h1 className="slide-title">Combinatorial Potential</h1>
            <p className="slide-subtitle">
                Interchangeable parts enable massive combinatorial libraries
            </p>

            {/* Key insight */}
            <div className="slide-highlight-box mega">
                <div className="highlight-icon">∞</div>
                <div className="highlight-text">
                    With standardized overhangs, tiles at the same position are <strong>fully interchangeable</strong> across
                    all {stats.total_lvl1_groups} Lvl1 groups. This creates a combinatorial space
                    of <strong className="combo-number">{combinationStr}</strong> possible unique Lvl1 assemblies.
                </div>
            </div>

            {/* Per-position breakdown */}
            <div className="slide-section">
                <h2>Per-Position Interchangeability</h2>
                <div className="position-grid">
                    {readyByPosition.map((n, i) => (
                        <div key={i} className="position-card">
                            <div className="pos-label">P{i}</div>
                            <div className="pos-total">{tilesPerPos > n ? tilesPerPos : n}</div>
                            <div className="pos-ready">{n} ready</div>
                            <div className="pos-oh">
                                {design.standard_overhangs[i]} → {design.standard_overhangs[i + 1]}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Use cases */}
            <div className="slide-section">
                <h2>Applications</h2>
                <div className="use-case-grid">
                    <div className="use-case-card">
                        <div className="uc-icon">🧬</div>
                        <h3>Chimeric Constructs</h3>
                        <p>Mix tiles from different genomic regions to create novel hybrid assemblies</p>
                    </div>
                    <div className="use-case-card">
                        <div className="uc-icon">🔬</div>
                        <h3>Mutant Libraries</h3>
                        <p>Combine wild-type and domesticated variants at each position</p>
                    </div>
                    <div className="use-case-card">
                        <div className="uc-icon">🧩</div>
                        <h3>Modular Segments</h3>
                        <p>Any Lvl1 can be reconstituted from tiles of different groups</p>
                    </div>
                </div>
            </div>

            {/* CTA */}
            <div className="slide-cta">
                <button className="explorer-launch-btn" onClick={onEnterExplorer}>
                    <span className="btn-icon">🔍</span>
                    <span>Enter the MoClo Explorer</span>
                    <span className="btn-arrow">→</span>
                </button>
                <p className="cta-desc">
                    Browse all {stats.total_tiles} tiles, {stats.total_lvl1_groups} groups,
                    domestication details, mutations, and sequence alignments
                </p>
            </div>
        </div>
    );
}
