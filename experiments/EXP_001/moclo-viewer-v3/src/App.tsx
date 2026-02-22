import { useState, useEffect, useCallback } from 'react';
import { AppData, ViewState, TOTAL_SLIDES } from './types';
import { loadAllData } from './loader';
import Sidebar from './components/Sidebar';
import GenomeOverview from './components/GenomeOverview';
import GroupDetail from './components/GroupDetail';
import TileDetail from './components/TileDetail';
import PresentationView from './components/PresentationView';

export default function App() {
    const [data, setData] = useState<AppData | null>(null);
    const [view, setView] = useState<ViewState>({ view: 'presentation', slideIndex: 0 });

    useEffect(() => {
        loadAllData().then(setData);
    }, []);

    const navigate = useCallback((v: ViewState) => setView(v), []);

    // Arrow key navigation for presentation
    useEffect(() => {
        if (view.view !== 'presentation') return;
        const handler = (e: KeyboardEvent) => {
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault();
                setView(prev => {
                    const idx = prev.slideIndex ?? 0;
                    if (idx < TOTAL_SLIDES - 1) {
                        return { view: 'presentation', slideIndex: idx + 1 };
                    }
                    return prev;
                });
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                setView(prev => {
                    const idx = prev.slideIndex ?? 0;
                    if (idx > 0) {
                        return { view: 'presentation', slideIndex: idx - 1 };
                    }
                    return prev;
                });
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [view.view]);

    if (!data) {
        return (
            <div className="loading">
                <div className="spinner" />
                <div className="loading-text">Loading MoClo V3…</div>
            </div>
        );
    }

    // Presentation mode
    if (view.view === 'presentation') {
        return (
            <PresentationView
                data={data}
                slideIndex={view.slideIndex ?? 0}
                onNavigate={navigate}
            />
        );
    }

    // Explorer mode
    return (
        <div className="app">
            <Sidebar data={data} view={view} onNavigate={navigate} />
            <div className="main-content">
                <ExplorerHeader view={view} data={data} onNavigate={navigate} />
                <div className="view-body">
                    {view.view === 'genome' && (
                        <GenomeOverview data={data} onNavigate={navigate} />
                    )}
                    {view.view === 'group' && view.groupId !== undefined && (
                        <GroupDetail data={data} groupId={view.groupId} onNavigate={navigate} />
                    )}
                    {view.view === 'tile' && view.tileId !== undefined && (
                        <TileDetail data={data} tileId={view.tileId} onNavigate={navigate} />
                    )}
                </div>
            </div>
        </div>
    );
}

function ExplorerHeader({ view, data, onNavigate }: {
    view: ViewState;
    data: AppData;
    onNavigate: (v: ViewState) => void;
}) {
    const tile = view.tileId !== undefined ? data.bundle.tiles[view.tileId] : null;
    const group = view.groupId !== undefined
        ? data.bundle.lvl1_groups[view.groupId]
        : tile
            ? data.bundle.lvl1_groups[tile.lvl1_group]
            : null;

    return (
        <div className="view-header">
            <div className="breadcrumb">
                <button
                    className="back-to-pres"
                    onClick={() => onNavigate({ view: 'presentation', slideIndex: 0 })}
                >
                    ← Presentation
                </button>
                <span className="sep">·</span>
                <button onClick={() => onNavigate({ view: 'genome' })}>Genome</button>
                {(view.view === 'group' || view.view === 'tile') && group && (
                    <>
                        <span className="sep">›</span>
                        <button onClick={() => onNavigate({ view: 'group', groupId: group.id })}>
                            Group {group.id}
                        </button>
                    </>
                )}
                {view.view === 'tile' && tile && (
                    <>
                        <span className="sep">›</span>
                        <span>Tile {tile.id}</span>
                    </>
                )}
            </div>
            <h2>
                {view.view === 'genome' && 'Genome Overview'}
                {view.view === 'group' && group && `Lvl1 Group ${group.id}`}
                {view.view === 'tile' && tile && `Tile ${tile.id} — P${tile.position}`}
            </h2>
        </div>
    );
}
