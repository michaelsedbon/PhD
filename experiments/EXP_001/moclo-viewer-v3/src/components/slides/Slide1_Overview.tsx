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

            {/* Lvl1 assembly groups */}
            <div className="slide-section">
                <h2>{stats.total_tiles} Tiles → {stats.total_lvl1_groups} Lvl1 Assemblies (~{Math.round(genome.length / stats.total_lvl1_groups / 1000)} kb each)</h2>
                <div style={{ display: 'flex', gap: '2px', flexWrap: 'wrap', marginTop: '12px' }}>
                    {data.bundle.lvl1_groups.map((g) => {
                        const groupTiles = data.bundle.tiles.filter(t => t.lvl1_group === g.id);
                        const readyCount = groupTiles.filter(t => t.gg_ready).length;
                        const allReady = readyCount === groupTiles.length;
                        const widthPct = Math.max(1.2, (g.length / genome.length) * 100);
                        const readyFrac = readyCount / groupTiles.length;
                        // Color: green if all ready, gradient to red if many blocked
                        const bg = allReady
                            ? 'rgba(63, 185, 80, 0.7)'
                            : readyFrac > 0.7
                                ? 'rgba(210, 153, 34, 0.7)'
                                : 'rgba(248, 81, 73, 0.7)';
                        return (
                            <div
                                key={g.id}
                                title={`Lvl1-${g.id}: ${groupTiles.length} tiles, ${readyCount} ready, ${(g.length/1000).toFixed(0)} kb`}
                                style={{
                                    width: `${widthPct}%`,
                                    height: '38px',
                                    background: bg,
                                    borderRadius: '3px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '9px',
                                    color: '#e6edf3',
                                    fontWeight: 600,
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    flexShrink: 0,
                                }}
                            >
                                {g.id}
                            </div>
                        );
                    })}
                </div>
                <div className="tile-minimap-legend" style={{ marginTop: '8px' }}>
                    <span className="legend-item"><span className="legend-dot ready" /> All tiles GG-ready</span>
                    <span className="legend-item"><span className="legend-dot" style={{ backgroundColor: '#d29922' }} /> Some tiles need domestication</span>
                    <span className="legend-item"><span className="legend-dot blocked" /> Many tiles need domestication</span>
                </div>
            </div>

        </div>
    );
}
