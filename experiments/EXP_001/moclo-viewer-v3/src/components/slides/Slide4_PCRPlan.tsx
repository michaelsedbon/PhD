import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

export default function Slide4PCRPlan({ data }: Props) {
    const { stats, tiles } = data.bundle;

    // Compute PCR breakdown
    let totalSubfragments = 0;
    let totalMutagenicPrimers = 0;
    const bsaiBreakdown = [0, 0, 0, 0]; // 1, 2, 3, 4+ sites
    for (const tile of tiles) {
        if (tile.domestication) {
            totalSubfragments += tile.domestication.subfragments.length;
            totalMutagenicPrimers += tile.domestication.primers.length * 2;
            const n = tile.domestication.n_sites;
            if (n >= 4) bsaiBreakdown[3]++;
            else bsaiBreakdown[n - 1]++;
        }
    }

    const totalAmplificationPrimers = stats.total_tiles * 2;

    return (
        <div className="slide">
            <h1 className="slide-title">PCR Preparation</h1>
            <p className="slide-subtitle">
                Building all {stats.total_tiles} Lvl0 parts — two workflows
            </p>

            {/* Two workflows side by side */}
            <div className="slide-columns">
                <div className="slide-column">
                    <div className="workflow-card green-border">
                        <h3>Workflow A — Simple Amplification</h3>
                        <div className="workflow-stat green">{stats.ready_tiles}</div>
                        <div className="workflow-label">GG-Ready tiles</div>
                        <div className="workflow-desc">
                            Single PCR with amplification primers. Each tile produces a BsaI-free
                            insert ready for Lvl0 cloning.
                        </div>
                        <div className="workflow-details">
                            <div><strong>{totalAmplificationPrimers}</strong> amplification oligos</div>
                            <div><strong>{stats.ready_tiles}</strong> PCR reactions</div>
                        </div>
                    </div>
                </div>
                <div className="slide-column">
                    <div className="workflow-card red-border">
                        <h3>Workflow B — OE-PCR Domestication</h3>
                        <div className="workflow-stat red">{stats.blocked_tiles}</div>
                        <div className="workflow-label">Blocked tiles</div>
                        <div className="workflow-desc">
                            Multi-step OE-PCR: amplify subfragments with mutagenic primers,
                            then assemble into the domesticated full-length tile.
                        </div>
                        <div className="workflow-details">
                            <div><strong>{totalMutagenicPrimers}</strong> mutagenic oligos</div>
                            <div><strong>{totalSubfragments}</strong> subfragment reactions</div>
                            <div><strong>{stats.blocked_tiles}</strong> assembly reactions</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* BsaI breakdown */}
            <div className="slide-section">
                <h2>Internal BsaI Site Distribution</h2>
                <div className="bsai-breakdown">
                    {[1, 2, 3, 4].map((n, i) => (
                        <div key={n} className="bsai-bar-row">
                            <div className="bsai-label">{n === 4 ? '4+' : n} site{n > 1 ? 's' : ''}</div>
                            <div className="bsai-bar">
                                <div
                                    className="bsai-bar-fill"
                                    style={{
                                        width: `${(bsaiBreakdown[i] / stats.blocked_tiles) * 100}%`,
                                        background: n === 1 ? 'var(--orange)' : n === 2 ? '#e8863a' : 'var(--red)',
                                    }}
                                />
                            </div>
                            <div className="bsai-count">{bsaiBreakdown[i]} tiles</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Summary */}
            <div className="slide-stats-row">
                <div className="slide-stat">
                    <div className="slide-stat-value">{stats.total_primers.toLocaleString()}</div>
                    <div className="slide-stat-label">Total Oligos</div>
                </div>
                <div className="slide-stat">
                    <div className="slide-stat-value">{stats.total_pcr_reactions.toLocaleString()}</div>
                    <div className="slide-stat-label">Total PCR Reactions</div>
                </div>
            </div>

            {/* Interactive figure */}
            <div className="slide-figures-row single">
                <div className="slide-figure wide">
                    <h3>PCR Simulation Results</h3>
                    <iframe src="/figures/pcr_simulation.html" title="PCR simulation" />
                </div>
            </div>
        </div>
    );
}
