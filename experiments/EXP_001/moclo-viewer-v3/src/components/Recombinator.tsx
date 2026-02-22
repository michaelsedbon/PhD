import { useMemo, useState, useCallback } from 'react';
import Plot from 'react-plotly.js';
import { AppData, ViewState, GeneProduct, Tile } from '../types';

/* ── Color palette (same as QCDashboard) ──────────────────────────── */
const CATEGORY_COLORS: Record<string, string> = {
    'Transport': '#58a6ff', 'Kinase / Phosphatase': '#3fb950',
    'Redox Enzymes': '#f85149', 'Biosynthesis': '#d29922',
    'Transferase': '#bc8cff', 'Regulation': '#39d2c0',
    'Transcription': '#ff7b72', 'Translation': '#79c0ff',
    'DNA Maintenance': '#d2a8ff', 'Mobile Elements': '#ffa657',
    'Motility': '#56d364', 'Membrane': '#7ee787',
    'Fimbriae / Pili': '#f778ba', 'Proteolysis': '#ff9bce',
    'Chaperones / Stress': '#ffdf5d', 'Uncharacterized': '#484f58',
    'Lyase / Isomerase': '#a5d6ff', 'Hydrolase': '#ffc680',
    'Other': '#6e7681', 'Unknown': '#30363d',
};
function getCatColor(cat: string) { return CATEGORY_COLORS[cat] || '#6e7681'; }

/* ── Plotly shared config ─────────────────────────────────────────── */
const DARK: Record<string, any> = {
    paper_bgcolor: 'transparent', plot_bgcolor: '#161b22',
    font: { family: 'Inter, system-ui, sans-serif', size: 12, color: '#c9d1d9' },
    margin: { l: 50, r: 20, t: 10, b: 40 }, autosize: true,
    xaxis: { gridcolor: '#21262d', zerolinecolor: '#21262d' },
    yaxis: { gridcolor: '#21262d', zerolinecolor: '#21262d' },
};
const PCFG: Record<string, any> = { responsive: true, displayModeBar: false };

interface Props {
    data: AppData;
    onNavigate: (v: ViewState) => void;
}

export default function Recombinator({ data, onNavigate }: Props) {
    const { bundle, geneProducts } = data;
    const nPos = bundle.design.tiles_per_group; // 15

    // ── Index tiles by position ──
    const tilesByPosition = useMemo(() => {
        const m = new Map<number, Tile[]>();
        for (const t of bundle.tiles) {
            const arr = m.get(t.position) || [];
            arr.push(t);
            m.set(t.position, arr);
        }
        // Sort each position by group
        for (const [, arr] of m) arr.sort((a, b) => a.lvl1_group - b.lvl1_group);
        return m;
    }, [bundle.tiles]);

    // ── Genes per tile ──
    const tileGenes = useMemo(() => {
        const m = new Map<number, GeneProduct[]>();
        for (const t of bundle.tiles) {
            const genes = geneProducts.filter(g => g.end > t.start && g.start < t.end);
            m.set(t.id, genes);
        }
        return m;
    }, [bundle.tiles, geneProducts]);

    // ── State: selected tile ID at each position ──
    const getGroupTiles = useCallback((gid: number) => {
        const result: (number | null)[] = [];
        for (let p = 0; p < nPos; p++) {
            const candidates = tilesByPosition.get(p) || [];
            const tile = candidates.find(t => t.lvl1_group === gid);
            result.push(tile ? tile.id : null);
        }
        return result;
    }, [tilesByPosition, nPos]);

    const [selected, setSelected] = useState<(number | null)[]>(() => getGroupTiles(0));
    const [compareGroup, setCompareGroup] = useState(0);

    // ── Computed stats for current selection ──
    const assemblyStats = useMemo(() => {
        const allGenes: GeneProduct[] = [];
        const catCounts: Record<string, number> = {};
        let totalGenes = 0;
        let ggReady = 0;
        let totalBsai = 0;
        let totalLength = 0;

        for (let p = 0; p < nPos; p++) {
            const tid = selected[p];
            if (tid === null) continue;
            const tile = bundle.tiles[tid];
            if (tile.gg_ready) ggReady++;
            totalBsai += tile.internal_bsai;
            totalLength += tile.length;

            const genes = tileGenes.get(tid) || [];
            for (const g of genes) {
                allGenes.push(g);
                catCounts[g.category] = (catCounts[g.category] || 0) + 1;
                totalGenes++;
            }
        }

        const categories = Object.entries(catCounts).sort((a, b) => b[1] - a[1]);
        return { allGenes, categories, totalGenes, ggReady, totalBsai, totalLength, nSelected: selected.filter(Boolean).length };
    }, [selected, bundle.tiles, tileGenes, nPos]);

    // ── Comparison group stats ──
    const compareStats = useMemo(() => {
        const compareTiles = getGroupTiles(compareGroup);
        const catCounts: Record<string, number> = {};
        for (let p = 0; p < nPos; p++) {
            const tid = compareTiles[p];
            if (tid === null) continue;
            const genes = tileGenes.get(tid) || [];
            for (const g of genes) {
                catCounts[g.category] = (catCounts[g.category] || 0) + 1;
            }
        }
        return Object.entries(catCounts).sort((a, b) => b[1] - a[1]);
    }, [compareGroup, getGroupTiles, tileGenes, nPos]);

    // ── Preset strategies ──
    const applyPreset = useCallback((strategy: string) => {
        if (strategy === 'original') {
            setSelected(getGroupTiles(compareGroup));
            return;
        }
        if (strategy === 'random') {
            const result: (number | null)[] = [];
            for (let p = 0; p < nPos; p++) {
                const candidates = tilesByPosition.get(p) || [];
                result.push(candidates[Math.floor(Math.random() * candidates.length)].id);
            }
            setSelected(result);
            return;
        }
        if (strategy === 'maxGG') {
            const result: (number | null)[] = [];
            for (let p = 0; p < nPos; p++) {
                const candidates = tilesByPosition.get(p) || [];
                // Prefer: gg_ready=true, then fewest internal_bsai
                const sorted = [...candidates].sort((a, b) => {
                    if (a.gg_ready !== b.gg_ready) return a.gg_ready ? -1 : 1;
                    return a.internal_bsai - b.internal_bsai;
                });
                result.push(sorted[0].id);
            }
            setSelected(result);
            return;
        }
        if (strategy === 'minBsaI') {
            const result: (number | null)[] = [];
            for (let p = 0; p < nPos; p++) {
                const candidates = tilesByPosition.get(p) || [];
                const sorted = [...candidates].sort((a, b) => a.internal_bsai - b.internal_bsai);
                result.push(sorted[0].id);
            }
            setSelected(result);
            return;
        }
        if (strategy === 'maxDiversity') {
            // Greedy: at each position, pick tile that adds the most NEW categories
            const result: (number | null)[] = [];
            const coveredCats = new Set<string>();
            for (let p = 0; p < nPos; p++) {
                const candidates = tilesByPosition.get(p) || [];
                let bestTile = candidates[0];
                let bestNewCats = -1;
                for (const t of candidates) {
                    const genes = tileGenes.get(t.id) || [];
                    const newCats = new Set(genes.map(g => g.category).filter(c => !coveredCats.has(c)));
                    if (newCats.size > bestNewCats) {
                        bestNewCats = newCats.size;
                        bestTile = t;
                    }
                }
                // Add this tile's categories to covered
                const bestGenes = tileGenes.get(bestTile.id) || [];
                for (const g of bestGenes) coveredCats.add(g.category);
                result.push(bestTile.id);
            }
            setSelected(result);
            return;
        }
        if (strategy === 'minDiversity') {
            // Greedy: at each position, pick tile whose categories overlap most with already-covered
            const result: (number | null)[] = [];
            const coveredCats = new Map<string, number>();
            for (let p = 0; p < nPos; p++) {
                const candidates = tilesByPosition.get(p) || [];
                if (p === 0) {
                    // First position: pick tile with fewest distinct categories
                    let bestTile = candidates[0];
                    let fewest = Infinity;
                    for (const t of candidates) {
                        const genes = tileGenes.get(t.id) || [];
                        const cats = new Set(genes.map(g => g.category));
                        if (cats.size < fewest && cats.size > 0) {
                            fewest = cats.size;
                            bestTile = t;
                        }
                    }
                    const bestGenes = tileGenes.get(bestTile.id) || [];
                    for (const g of bestGenes) coveredCats.set(g.category, (coveredCats.get(g.category) || 0) + 1);
                    result.push(bestTile.id);
                } else {
                    // Subsequent: pick tile with highest overlap ratio (fewest new cats)
                    let bestTile = candidates[0];
                    let bestScore = -Infinity;
                    for (const t of candidates) {
                        const genes = tileGenes.get(t.id) || [];
                        if (genes.length === 0) continue;
                        const cats = genes.map(g => g.category);
                        const overlapCount = cats.filter(c => coveredCats.has(c)).length;
                        const score = overlapCount / cats.length;
                        if (score > bestScore) {
                            bestScore = score;
                            bestTile = t;
                        }
                    }
                    const bestGenes = tileGenes.get(bestTile.id) || [];
                    for (const g of bestGenes) coveredCats.set(g.category, (coveredCats.get(g.category) || 0) + 1);
                    result.push(bestTile.id);
                }
            }
            setSelected(result);
            return;
        }
    }, [nPos, tilesByPosition, tileGenes, getGroupTiles, compareGroup]);

    // ── Comparison chart data ──
    const allCatLabels = useMemo(() => {
        const all = new Set<string>();
        for (const [cat] of assemblyStats.categories) all.add(cat);
        for (const [cat] of compareStats) all.add(cat);
        return Array.from(all).sort((a, b) => {
            const aCount = assemblyStats.categories.find(([c]) => c === a)?.[1] || 0;
            const bCount = assemblyStats.categories.find(([c]) => c === b)?.[1] || 0;
            return bCount - aCount;
        });
    }, [assemblyStats.categories, compareStats]);

    // ── Render ──
    return (
        <div className="recombinator">
            <h2 className="recomb-title">🧬 Lvl1 Recombination Lab</h2>
            <p className="recomb-subtitle">
                Build custom Lvl1 assemblies by picking tiles from any group at each of {nPos} positions.
                Tiles at the same position share overhangs and are fully interchangeable.
            </p>

            {/* Presets */}
            <div className="recomb-presets">
                <span className="presets-label">Optimization Presets:</span>
                <button className="preset-btn diversity" onClick={() => applyPreset('maxDiversity')}>
                    🌈 Max Diversity
                </button>
                <button className="preset-btn focus" onClick={() => applyPreset('minDiversity')}>
                    🎯 Min Diversity
                </button>
                <button className="preset-btn gg" onClick={() => applyPreset('maxGG')}>
                    ✅ Max GG-Ready
                </button>
                <button className="preset-btn bsai" onClick={() => applyPreset('minBsaI')}>
                    ✂️ Min BsaI
                </button>
                <button className="preset-btn random" onClick={() => applyPreset('random')}>
                    🎲 Random
                </button>
                <div className="preset-original">
                    <button className="preset-btn original" onClick={() => applyPreset('original')}>
                        📋 Original
                    </button>
                    <select
                        value={compareGroup}
                        onChange={e => setCompareGroup(Number(e.target.value))}
                        className="group-select"
                    >
                        {bundle.lvl1_groups.map(g => (
                            <option key={g.id} value={g.id}>G{g.id}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Score Cards */}
            <div className="recomb-scores">
                <div className="score-card">
                    <span className="score-value accent-blue">{assemblyStats.categories.length}</span>
                    <span className="score-label">Categories</span>
                </div>
                <div className="score-card">
                    <span className="score-value accent-purple">{assemblyStats.totalGenes}</span>
                    <span className="score-label">Genes</span>
                </div>
                <div className="score-card">
                    <span className="score-value accent-green">{assemblyStats.ggReady}/{assemblyStats.nSelected}</span>
                    <span className="score-label">GG-Ready</span>
                </div>
                <div className="score-card">
                    <span className={`score-value ${assemblyStats.totalBsai > 0 ? 'accent-red' : 'accent-green'}`}>
                        {assemblyStats.totalBsai}
                    </span>
                    <span className="score-label">BsaI Sites</span>
                </div>
                <div className="score-card">
                    <span className="score-value accent-cyan">{(assemblyStats.totalLength / 1000).toFixed(1)} kb</span>
                    <span className="score-label">Total Length</span>
                </div>
            </div>

            {/* Assembly Slots */}
            <div className="recomb-slots-wrap">
                <h3>Assembly Slots</h3>
                <div className="recomb-slots">
                    {Array.from({ length: nPos }, (_, p) => {
                        const tid = selected[p];
                        const tile = tid !== null ? bundle.tiles[tid] : null;
                        const genes = tid !== null ? (tileGenes.get(tid) || []) : [];
                        const candidates = tilesByPosition.get(p) || [];

                        // Dominant category
                        const catCounts: Record<string, number> = {};
                        for (const g of genes) catCounts[g.category] = (catCounts[g.category] || 0) + 1;
                        const topCat = Object.entries(catCounts).sort((a, b) => b[1] - a[1])[0];

                        return (
                            <div key={p} className="recomb-slot" style={{ borderTopColor: topCat ? getCatColor(topCat[0]) : '#30363d' }}>
                                <div className="slot-header">
                                    <span className="slot-pos">P{p}</span>
                                    <span className="slot-oh">{bundle.design.standard_overhangs[p]}→{bundle.design.standard_overhangs[p + 1]}</span>
                                </div>
                                <select
                                    value={tid ?? ''}
                                    onChange={e => {
                                        const newSelected = [...selected];
                                        newSelected[p] = e.target.value ? Number(e.target.value) : null;
                                        setSelected(newSelected);
                                    }}
                                    className="slot-select"
                                >
                                    {candidates.map(c => {
                                        const cGenes = tileGenes.get(c.id) || [];
                                        return (
                                            <option key={c.id} value={c.id}>
                                                T{c.id} (G{c.lvl1_group}) — {cGenes.length} genes {c.gg_ready ? '✓' : `⚠${c.internal_bsai}`}
                                            </option>
                                        );
                                    })}
                                </select>
                                {tile && (
                                    <div className="slot-info">
                                        <span className="slot-source">G{tile.lvl1_group}</span>
                                        <span className="slot-genes">{genes.length} genes</span>
                                        <span className={`slot-status ${tile.gg_ready ? 'ready' : 'blocked'}`}>
                                            {tile.gg_ready ? '✓ GG' : `⚠ ${tile.internal_bsai} BsaI`}
                                        </span>
                                    </div>
                                )}
                                {topCat && (
                                    <div className="slot-cat" style={{ color: getCatColor(topCat[0]) }}>
                                        {topCat[0]}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Category Breakdown Chart */}
            <div className="recomb-chart-card">
                <h3>Functional Category Breakdown</h3>
                <div className="recomb-plot">
                    <Plot
                        data={[{
                            y: assemblyStats.categories.map(([c]) => c).reverse(),
                            x: assemblyStats.categories.map(([, v]) => v).reverse(),
                            type: 'bar',
                            orientation: 'h',
                            marker: { color: assemblyStats.categories.map(([c]) => getCatColor(c)).reverse() },
                            hovertemplate: '%{y}: %{x} genes<extra></extra>',
                        }]}
                        layout={{
                            ...DARK,
                            margin: { l: 140, r: 20, t: 10, b: 40 },
                            xaxis: { ...DARK.xaxis, title: { text: 'Gene count', font: { size: 11, color: '#8b949e' } } },
                        }}
                        config={PCFG}
                        useResizeHandler
                        style={{ width: '100%', height: '100%' }}
                    />
                </div>
            </div>

            {/* Comparison Chart */}
            <div className="recomb-chart-card">
                <h3>Custom vs Original G{compareGroup}</h3>
                <div className="recomb-plot">
                    <Plot
                        data={[
                            {
                                name: 'Custom Assembly',
                                y: allCatLabels.slice().reverse(),
                                x: allCatLabels.map(c => assemblyStats.categories.find(([cc]) => cc === c)?.[1] || 0).reverse(),
                                type: 'bar',
                                orientation: 'h',
                                marker: { color: '#58a6ff' },
                                hovertemplate: '%{y}: %{x} genes<extra>Custom</extra>',
                            },
                            {
                                name: `G${compareGroup} Original`,
                                y: allCatLabels.slice().reverse(),
                                x: allCatLabels.map(c => compareStats.find(([cc]) => cc === c)?.[1] || 0).reverse(),
                                type: 'bar',
                                orientation: 'h',
                                marker: { color: '#6e768166' },
                                hovertemplate: '%{y}: %{x} genes<extra>G' + compareGroup + '</extra>',
                            },
                        ]}
                        layout={{
                            ...DARK,
                            margin: { l: 140, r: 20, t: 10, b: 40 },
                            barmode: 'group',
                            showlegend: true,
                            legend: { orientation: 'h' as const, y: -0.15, x: 0.5, xanchor: 'center' as const, font: { size: 11, color: '#8b949e' } },
                            xaxis: { ...DARK.xaxis, title: { text: 'Gene count', font: { size: 11, color: '#8b949e' } } },
                        }}
                        config={PCFG}
                        useResizeHandler
                        style={{ width: '100%', height: '100%' }}
                    />
                </div>
            </div>

            {/* Gene List */}
            <div className="recomb-gene-list">
                <h3>Genes in Custom Assembly ({assemblyStats.totalGenes})</h3>
                <div className="qc-gene-list">
                    <div className="gene-list-header">
                        <span>Gene</span>
                        <span>Product</span>
                        <span>Category</span>
                        <span>Source</span>
                    </div>
                    {assemblyStats.allGenes.slice(0, 150).map((gp, i) => {
                        // Find which tile this gene is on
                        const sourceTile = selected.find(tid => {
                            if (tid === null) return false;
                            const t = bundle.tiles[tid];
                            return gp.end > t.start && gp.start < t.end;
                        });
                        const tile = sourceTile !== null && sourceTile !== undefined ? bundle.tiles[sourceTile] : null;

                        return (
                            <div key={i} className="gene-list-row">
                                <span className="gl-gene">{gp.gene}</span>
                                <span className="gl-product">{gp.product || '—'}</span>
                                <span>
                                    <span className="cat-tag" style={{ background: getCatColor(gp.category) + '33', color: getCatColor(gp.category) }}>
                                        {gp.category}
                                    </span>
                                </span>
                                <span className="gl-group">
                                    {tile ? `T${tile.id} (G${tile.lvl1_group})` : '—'}
                                </span>
                            </div>
                        );
                    })}
                    {assemblyStats.allGenes.length > 150 && (
                        <div className="gene-list-more">
                            Showing 150 of {assemblyStats.allGenes.length} genes.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
