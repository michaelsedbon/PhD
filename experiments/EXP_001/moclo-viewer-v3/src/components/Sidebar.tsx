import { useState, useMemo } from 'react';
import { AppData, ViewState, Tile } from '../types';

interface Props {
    data: AppData;
    view: ViewState;
    onNavigate: (v: ViewState) => void;
}

type Tab = 'groups' | 'tiles';

export default function Sidebar({ data, view, onNavigate }: Props) {
    const [tab, setTab] = useState<Tab>('groups');
    const [search, setSearch] = useState('');
    const { bundle } = data;

    const filteredGroups = useMemo(() => {
        if (!search) return bundle.lvl1_groups;
        const q = search.toLowerCase();
        return bundle.lvl1_groups.filter(g =>
            `group ${g.id}`.includes(q) || `g${g.id}`.includes(q)
        );
    }, [bundle.lvl1_groups, search]);

    const filteredTiles = useMemo(() => {
        if (!search) return bundle.tiles;
        const q = search.toLowerCase();
        return bundle.tiles.filter(t =>
            `t${t.id}`.includes(q) ||
            `tile ${t.id}`.includes(q) ||
            `p${t.position}`.includes(q) ||
            t.overhang_left.toLowerCase().includes(q) ||
            t.overhang_right.toLowerCase().includes(q)
        );
    }, [bundle.tiles, search]);

    return (
        <div className="sidebar">
            {/* Header */}
            <div className="sidebar-header">
                <h1>🧬 MoClo V2</h1>
                <div className="subtitle">
                    {bundle.genome.name} · {(bundle.genome.length / 1e6).toFixed(2)} Mb
                </div>
            </div>

            {/* Stats */}
            <div className="sidebar-stats">
                <div className="stat-card">
                    <div className="stat-value">{bundle.stats.total_tiles}</div>
                    <div className="stat-label">Tiles</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: 'var(--green)' }}>
                        {bundle.stats.ready_tiles}
                    </div>
                    <div className="stat-label">GG-Ready</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: 'var(--red)' }}>
                        {bundle.stats.blocked_tiles}
                    </div>
                    <div className="stat-label">Blocked</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: 'var(--blue)' }}>
                        {bundle.stats.total_lvl1_groups}
                    </div>
                    <div className="stat-label">Lvl1 Groups</div>
                </div>
            </div>

            {/* Recombine button */}
            <button
                className={`sidebar-recombine ${view.view === 'recombine' ? 'active' : ''}`}
                onClick={() => onNavigate({ view: 'recombine' })}
            >
                🧬 Recombination Lab
            </button>

            {/* Search */}
            <div className="sidebar-search">
                <input
                    type="text"
                    placeholder={tab === 'groups' ? 'Search groups…' : 'Search tiles…'}
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
            </div>

            {/* Tab nav */}
            <div className="sidebar-nav">
                <button
                    className={tab === 'groups' ? 'active' : ''}
                    onClick={() => { setTab('groups'); setSearch(''); }}
                >
                    Groups ({bundle.lvl1_groups.length})
                </button>
                <button
                    className={tab === 'tiles' ? 'active' : ''}
                    onClick={() => { setTab('tiles'); setSearch(''); }}
                >
                    Tiles ({bundle.tiles.length})
                </button>
            </div>

            {/* List */}
            <div className="sidebar-list">
                {tab === 'groups' ? (
                    filteredGroups.map(g => {
                        const pct = Math.round((g.ready_tiles / g.total_tiles) * 100);
                        const active = view.view === 'group' && view.groupId === g.id;
                        const barColor = pct >= 70 ? 'var(--green)' : pct >= 40 ? 'var(--orange)' : 'var(--red)';
                        return (
                            <div
                                key={g.id}
                                className={`group-item ${active ? 'active' : ''}`}
                                onClick={() => onNavigate({ view: 'group', groupId: g.id })}
                            >
                                <span className="group-id">G{g.id}</span>
                                <div className="group-bar">
                                    <div
                                        className="group-bar-fill"
                                        style={{ width: `${pct}%`, background: barColor }}
                                    />
                                </div>
                                <span className="group-pct">{pct}%</span>
                            </div>
                        );
                    })
                ) : (
                    filteredTiles.map((t: Tile) => {
                        const active = view.view === 'tile' && view.tileId === t.id;
                        return (
                            <div
                                key={t.id}
                                className={`group-item ${active ? 'active' : ''}`}
                                onClick={() => onNavigate({ view: 'tile', tileId: t.id })}
                            >
                                <span className="group-id">T{t.id}</span>
                                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                                    P{t.position}
                                </span>
                                <span style={{ flex: 1 }} />
                                <span className={`badge ${t.gg_ready ? 'ready' : 'blocked'}`}>
                                    {t.gg_ready ? 'Ready' : `${t.internal_bsai} BsaI`}
                                </span>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
