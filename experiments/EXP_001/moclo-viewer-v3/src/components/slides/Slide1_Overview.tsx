import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

export default function Slide1Overview({ data }: Props) {
    const { stats, genome } = data.bundle;
    const readyPct = ((stats.ready_tiles / stats.total_tiles) * 100).toFixed(1);
    const blockedPct = ((stats.blocked_tiles / stats.total_tiles) * 100).toFixed(1);

    return (
        <div className="slide">
            <h1 className="slide-title">Genome Tiling Overview</h1>
            <p className="slide-subtitle">
                <em>{genome.name}</em> — {(genome.length / 1e6).toFixed(2)} Mb tiled into {stats.total_tiles} Lvl0 parts
            </p>

            {/* Big stats */}
            <div className="slide-stats-row">
                <div className="slide-stat big">
                    <div className="slide-stat-value">{stats.total_tiles}</div>
                    <div className="slide-stat-label">Total Lvl0 Tiles</div>
                </div>
                <div className="slide-stat big green">
                    <div className="slide-stat-value">{stats.ready_tiles}</div>
                    <div className="slide-stat-label">GG-Ready ({readyPct}%)</div>
                    <div className="slide-stat-desc">No internal BsaI sites — ready for Golden Gate cloning</div>
                </div>
                <div className="slide-stat big red">
                    <div className="slide-stat-value">{stats.blocked_tiles}</div>
                    <div className="slide-stat-label">Need Domestication ({blockedPct}%)</div>
                    <div className="slide-stat-desc">Internal BsaI sites must be removed by silent mutation</div>
                </div>
            </div>

            {/* Tile mini-grid */}
            <div className="slide-section">
                <h2>All {stats.total_tiles} Tiles — at a Glance</h2>
                <div className="tile-minimap">
                    {data.bundle.tiles.map(t => (
                        <div
                            key={t.id}
                            className={`tile-dot ${t.gg_ready ? 'ready' : 'blocked'}`}
                            title={`T${t.id} — P${t.position} — G${t.lvl1_group}${t.gg_ready ? '' : ` — ${t.internal_bsai} BsaI`}`}
                        />
                    ))}
                </div>
                <div className="tile-minimap-legend">
                    <span className="legend-item"><span className="legend-dot ready" /> GG-Ready</span>
                    <span className="legend-item"><span className="legend-dot blocked" /> Needs Domestication</span>
                </div>
            </div>

            {/* Interactive figures */}
            <div className="slide-figures-row">
                <div className="slide-figure">
                    <h3>GG-Readiness</h3>
                    <iframe src="/figures/domestication_donut.html" title="Domestication donut" />
                </div>
                <div className="slide-figure">
                    <h3>Genome Tiling Map</h3>
                    <iframe src="/figures/tiling_map.html" title="Tiling map" />
                </div>
            </div>
        </div>
    );
}
