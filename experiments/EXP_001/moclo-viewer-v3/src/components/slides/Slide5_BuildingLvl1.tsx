import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

export default function Slide5BuildingLvl1({ data }: Props) {
    const { stats, design, lvl1_groups } = data.bundle;
    const avgLength = lvl1_groups.reduce((sum, g) => sum + g.length, 0) / lvl1_groups.length;

    return (
        <div className="slide">
            <h1 className="slide-title">Building Lvl1 Assemblies</h1>
            <p className="slide-subtitle">
                Assembling {design.tiles_per_group} Lvl0 tiles into each Lvl1 construct
            </p>

            {/* Assembly diagram */}
            <div className="slide-section">
                <h2>Golden Gate Assembly — Single Pot</h2>
                <div className="slide-explanation">
                    <p>
                        Each Lvl1 group combines <strong>{design.tiles_per_group} Lvl0 tiles</strong> + backbone
                        in a single BsaI Golden Gate reaction. The standardized overhangs ensure directional,
                        scarless ligation of all fragments simultaneously.
                    </p>
                </div>

                {/* Visual assembly */}
                <div className="assembly-diagram">
                    <div className="assembly-backbone">Backbone</div>
                    <div className="assembly-tiles">
                        {Array.from({ length: design.tiles_per_group }, (_, i) => (
                            <div key={i} className="assembly-tile-slot">
                                <div className="asm-oh">{design.standard_overhangs[i]}</div>
                                <div className="asm-tile">T{i}</div>
                                <div className="asm-oh">{design.standard_overhangs[i + 1]}</div>
                            </div>
                        ))}
                    </div>
                    <div className="assembly-backbone">Backbone</div>
                </div>
            </div>

            {/* Stats */}
            <div className="slide-stats-row">
                <div className="slide-stat big blue">
                    <div className="slide-stat-value">{stats.total_lvl1_groups}</div>
                    <div className="slide-stat-label">Lvl1 Groups</div>
                </div>
                <div className="slide-stat big">
                    <div className="slide-stat-value">{design.tiles_per_group}</div>
                    <div className="slide-stat-label">Tiles per Group</div>
                </div>
                <div className="slide-stat big">
                    <div className="slide-stat-value">{(avgLength / 1000).toFixed(1)} kb</div>
                    <div className="slide-stat-label">Avg Group Size</div>
                </div>
                <div className="slide-stat big green">
                    <div className="slide-stat-value">{stats.complete_after}</div>
                    <div className="slide-stat-label">Complete After Domestication</div>
                </div>
            </div>

            {/* Group readiness overview */}
            <div className="slide-section">
                <h2>All {stats.total_lvl1_groups} Groups — Readiness</h2>
                <div className="group-bar-grid">
                    {lvl1_groups.map(g => {
                        const pct = Math.round((g.ready_tiles / g.total_tiles) * 100);
                        return (
                            <div key={g.id} className="group-bar-item">
                                <span className="gb-label">G{g.id}</span>
                                <div className="gb-bar">
                                    <div
                                        className="gb-fill"
                                        style={{
                                            width: `${pct}%`,
                                            background: pct >= 80 ? 'var(--green)' : pct >= 50 ? 'var(--orange)' : 'var(--red)',
                                        }}
                                    />
                                </div>
                                <span className="gb-pct">{pct}%</span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Interactive figure */}
            <div className="slide-figures-row single">
                <div className="slide-figure wide">
                    <h3>Lvl1 Assembly Map</h3>
                    <iframe src="/figures/lvl1_assembly_map.html" title="Lvl1 assembly map" />
                </div>
            </div>
        </div>
    );
}
