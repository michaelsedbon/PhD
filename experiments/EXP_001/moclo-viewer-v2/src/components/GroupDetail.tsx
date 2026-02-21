import { useMemo } from 'react';
import { AppData, ViewState } from '../types';

interface Props {
    data: AppData;
    groupId: number;
    onNavigate: (v: ViewState) => void;
}

export default function GroupDetail({ data, groupId, onNavigate }: Props) {
    const group = data.bundle.lvl1_groups[groupId];
    const tiles = data.tilesByGroup.get(groupId) || [];
    const pct = Math.round((group.ready_tiles / group.total_tiles) * 100);

    // Mutations in this group's region
    const groupMutations = useMemo(() => {
        const muts: { position: number; gene: string; change: string }[] = [];
        for (const [pos, m] of data.mutations) {
            if (pos >= group.start && pos < group.end) {
                muts.push({
                    position: pos,
                    gene: m.gene,
                    change: `${m.original}→${m.mutant}`,
                });
            }
        }
        return muts;
    }, [data.mutations, group]);

    // CDS regions overlapping this group
    const groupCDS = useMemo(() => {
        return data.cdsRegions.filter(c => c.end > group.start && c.start < group.end);
    }, [data.cdsRegions, group]);

    return (
        <div className="group-detail">
            {/* Info cards */}
            <div className="group-info-cards">
                <div className="info-card">
                    <div className="value">{(group.length / 1000).toFixed(1)} kb</div>
                    <div className="label">Length</div>
                </div>
                <div className="info-card">
                    <div className="value">{group.total_tiles}</div>
                    <div className="label">Total Tiles</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--green)' }}>{group.ready_tiles}</div>
                    <div className="label">GG-Ready</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: group.blocked_tiles_count > 0 ? 'var(--red)' : 'var(--green)' }}>
                        {group.blocked_tiles_count}
                    </div>
                    <div className="label">Blocked</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: pct >= 70 ? 'var(--green)' : 'var(--orange)' }}>
                        {pct}%
                    </div>
                    <div className="label">Readiness</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--orange)' }}>{groupMutations.length}</div>
                    <div className="label">Mutations</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--purple)' }}>{groupCDS.length}</div>
                    <div className="label">CDS Regions</div>
                </div>
                <div className="info-card">
                    <div className="value mono" style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                        {group.start.toLocaleString()} – {group.end.toLocaleString()}
                    </div>
                    <div className="label">Genomic Range</div>
                </div>
            </div>

            {/* Tile layout grid */}
            <div className="genome-canvas-wrapper">
                <h3>Tile Layout</h3>
                <div className="tiles-grid">
                    {tiles.map(t => (
                        <div
                            key={t.id}
                            className={`tile-block ${t.gg_ready ? 'ready' : 'blocked'}`}
                            onClick={() => onNavigate({ view: 'tile', tileId: t.id })}
                        >
                            <div className="tile-pos">P{t.position}</div>
                            <div className="tile-id">T{t.id}</div>
                            <div className="tile-oh">
                                <span className="badge overhang">{t.overhang_left}</span>
                                {' → '}
                                <span className="badge overhang">{t.overhang_right}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Tile detail table */}
            <div className="tile-table-wrapper">
                <table className="tile-table">
                    <thead>
                        <tr>
                            <th>Tile</th>
                            <th>Position</th>
                            <th>Overhangs</th>
                            <th>Length</th>
                            <th>GC%</th>
                            <th>BsaI Sites</th>
                            <th>Status</th>
                            <th>Boundary</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tiles.map(t => (
                            <tr key={t.id} onClick={() => onNavigate({ view: 'tile', tileId: t.id })}>
                                <td><strong>T{t.id}</strong></td>
                                <td>P{t.position}</td>
                                <td className="mono">{t.overhang_left} / {t.overhang_right}</td>
                                <td className="mono">{(t.length / 1000).toFixed(1)} kb</td>
                                <td className="mono">{t.gc_content.toFixed(1)}%</td>
                                <td style={{ color: t.internal_bsai > 0 ? 'var(--red)' : 'var(--text-muted)' }}>
                                    {t.internal_bsai}
                                </td>
                                <td>
                                    <span className={`badge ${t.gg_ready ? 'ready' : 'blocked'}`}>
                                        {t.gg_ready ? 'Ready' : 'Blocked'}
                                    </span>
                                </td>
                                <td style={{ fontSize: 11, color: 'var(--text-muted)' }}>{t.boundary_type}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Mutations in group */}
            {groupMutations.length > 0 && (
                <div className="domestication-section">
                    <h3>
                        <span className="badge mutation">{groupMutations.length} mutations</span>
                        in this group's region
                    </h3>
                    <div className="mutation-list">
                        {groupMutations.map((m, i) => (
                            <div key={i} className="mutation-item">
                                <span className="pos">{m.position.toLocaleString()}</span>
                                <span className="change">{m.change}</span>
                                <span className="gene-name">{m.gene}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
