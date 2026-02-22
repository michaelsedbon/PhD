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

/* ── Helper: compute stats for an assembly (list of tile IDs) ───── */
function computeGroupStats(
    tileIds: (number | null)[],
    tiles: Tile[],
    tileGenes: Map<number, GeneProduct[]>,
) {
    const catCounts: Record<string, number> = {};
    let totalGenes = 0, ggReady = 0, totalBsai = 0, totalLength = 0;
    for (const tid of tileIds) {
        if (tid === null) continue;
        const tile = tiles[tid];
        if (tile.gg_ready) ggReady++;
        totalBsai += tile.internal_bsai;
        totalLength += tile.length;
        const genes = tileGenes.get(tid) || [];
        for (const g of genes) {
            catCounts[g.category] = (catCounts[g.category] || 0) + 1;
            totalGenes++;
        }
    }
    return { catCounts, totalGenes, ggReady, totalBsai, totalLength, nCats: Object.keys(catCounts).length };
}

/* ── Helper: filter cat vector by exclusion set ─────────────────── */
function filteredCatVector(cv: Record<string, number>, excluded: Set<string>): Record<string, number> {
    if (excluded.size === 0) return cv;
    const r: Record<string, number> = {};
    for (const [c, n] of Object.entries(cv)) {
        if (!excluded.has(c)) r[c] = n;
    }
    return r;
}

export default function Recombinator({ data, onNavigate }: Props) {
    const { bundle, geneProducts } = data;
    const nPos = bundle.design.tiles_per_group; // 15
    const nGroups = bundle.lvl1_groups.length; // 46

    // ── Mode toggle ──
    const [mode, setMode] = useState<'single' | 'genome'>('single');

    // ── Category exclusion ──
    const [excludedCats, setExcludedCats] = useState<Set<string>>(new Set(['Other', 'Uncharacterized', 'Unknown']));
    const [showCatFilter, setShowCatFilter] = useState(false);

    // ── Expanded group in genome table ──
    const [expandedGroup, setExpandedGroup] = useState<number | null>(null);

    // ── Index tiles by position ──
    const tilesByPosition = useMemo(() => {
        const m = new Map<number, Tile[]>();
        for (const t of bundle.tiles) {
            const arr = m.get(t.position) || [];
            arr.push(t);
            m.set(t.position, arr);
        }
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

    // ── Category vector per tile (for optimization) ──
    const tileCatVector = useMemo(() => {
        const m = new Map<number, Record<string, number>>();
        for (const [tid, genes] of tileGenes) {
            const counts: Record<string, number> = {};
            for (const g of genes) counts[g.category] = (counts[g.category] || 0) + 1;
            m.set(tid, counts);
        }
        return m;
    }, [tileGenes]);

    // ── All categories sorted by frequency ──
    const allCategories = useMemo(() => {
        const s = new Set<string>();
        for (const gp of geneProducts) s.add(gp.category);
        const arr = Array.from(s);
        arr.sort((a, b) => {
            const countA = geneProducts.filter(g => g.category === a).length;
            const countB = geneProducts.filter(g => g.category === b).length;
            return countB - countA;
        });
        return arr;
    }, [geneProducts]);

    const toggleCatExclusion = useCallback((cat: string) => {
        setExcludedCats(prev => {
            const next = new Set(prev);
            if (next.has(cat)) next.delete(cat); else next.add(cat);
            return next;
        });
    }, []);

    const getGroupTiles = useCallback((gid: number) => {
        const result: (number | null)[] = [];
        for (let p = 0; p < nPos; p++) {
            const candidates = tilesByPosition.get(p) || [];
            const tile = candidates.find(t => t.lvl1_group === gid);
            result.push(tile ? tile.id : null);
        }
        return result;
    }, [tilesByPosition, nPos]);

    // ── Original genome arrangement ──
    const originalArrangement = useMemo(() => {
        const arr: (number | null)[][] = [];
        for (let g = 0; g < nGroups; g++) arr.push(getGroupTiles(g));
        return arr;
    }, [nGroups, getGroupTiles]);

    // ═══════════════════════════════════════════════════════════════════
    //  SINGLE GROUP MODE STATE
    // ═══════════════════════════════════════════════════════════════════
    const [selected, setSelected] = useState<(number | null)[]>(() => getGroupTiles(0));
    const [compareGroup, setCompareGroup] = useState(0);

    const assemblyStats = useMemo(() => {
        const allGenes: GeneProduct[] = [];
        const catCounts: Record<string, number> = {};
        let totalGenes = 0, ggReady = 0, totalBsai = 0, totalLength = 0;
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

    const compareStats = useMemo(() => {
        const compareTiles = getGroupTiles(compareGroup);
        const catCounts: Record<string, number> = {};
        for (let p = 0; p < nPos; p++) {
            const tid = compareTiles[p];
            if (tid === null) continue;
            const genes = tileGenes.get(tid) || [];
            for (const g of genes) catCounts[g.category] = (catCounts[g.category] || 0) + 1;
        }
        return Object.entries(catCounts).sort((a, b) => b[1] - a[1]);
    }, [compareGroup, getGroupTiles, tileGenes, nPos]);

    // ── Single-group presets (with category exclusion) ──
    const applyPreset = useCallback((strategy: string) => {
        if (strategy === 'original') { setSelected(getGroupTiles(compareGroup)); return; }
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
            const result: (number | null)[] = [];
            const coveredCats = new Set<string>();
            for (let p = 0; p < nPos; p++) {
                const candidates = tilesByPosition.get(p) || [];
                let bestTile = candidates[0];
                let bestNewCats = -1;
                for (const t of candidates) {
                    const genes = tileGenes.get(t.id) || [];
                    // Only count non-excluded categories for scoring
                    const newCats = new Set(genes.map(g => g.category).filter(c => !excludedCats.has(c) && !coveredCats.has(c)));
                    if (newCats.size > bestNewCats) { bestNewCats = newCats.size; bestTile = t; }
                }
                const bestGenes = tileGenes.get(bestTile.id) || [];
                for (const g of bestGenes) {
                    if (!excludedCats.has(g.category)) coveredCats.add(g.category);
                }
                result.push(bestTile.id);
            }
            setSelected(result);
            return;
        }
        if (strategy === 'minDiversity') {
            const result: (number | null)[] = [];
            const coveredCats = new Map<string, number>();
            for (let p = 0; p < nPos; p++) {
                const candidates = tilesByPosition.get(p) || [];
                if (p === 0) {
                    let bestTile = candidates[0], fewest = Infinity;
                    for (const t of candidates) {
                        const genes = tileGenes.get(t.id) || [];
                        // Count only non-excluded categories
                        const cats = new Set(genes.map(g => g.category).filter(c => !excludedCats.has(c)));
                        if (cats.size < fewest && cats.size > 0) { fewest = cats.size; bestTile = t; }
                    }
                    const bestGenes = tileGenes.get(bestTile.id) || [];
                    for (const g of bestGenes) {
                        if (!excludedCats.has(g.category))
                            coveredCats.set(g.category, (coveredCats.get(g.category) || 0) + 1);
                    }
                    result.push(bestTile.id);
                } else {
                    let bestTile = candidates[0], bestScore = -Infinity;
                    for (const t of candidates) {
                        const genes = tileGenes.get(t.id) || [];
                        if (genes.length === 0) continue;
                        // Only score non-excluded categories for overlap
                        const cats = genes.map(g => g.category).filter(c => !excludedCats.has(c));
                        if (cats.length === 0) continue;
                        const overlapCount = cats.filter(c => coveredCats.has(c)).length;
                        const score = overlapCount / cats.length;
                        if (score > bestScore) { bestScore = score; bestTile = t; }
                    }
                    const bestGenes = tileGenes.get(bestTile.id) || [];
                    for (const g of bestGenes) {
                        if (!excludedCats.has(g.category))
                            coveredCats.set(g.category, (coveredCats.get(g.category) || 0) + 1);
                    }
                    result.push(bestTile.id);
                }
            }
            setSelected(result);
            return;
        }
    }, [nPos, tilesByPosition, tileGenes, getGroupTiles, compareGroup, excludedCats]);

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

    // ═══════════════════════════════════════════════════════════════════
    //  GENOME-WIDE MODE STATE
    // ═══════════════════════════════════════════════════════════════════
    const [genomeArrangement, setGenomeArrangement] = useState<(number | null)[][] | null>(null);
    const [activeGenomeStrategy, setActiveGenomeStrategy] = useState<string | null>(null);

    // ── Genome-wide optimization algorithms (with category exclusion) ──
    const applyGenomePreset = useCallback((strategy: string) => {
        const nG = nGroups;
        const result: (number | null)[][] = Array.from({ length: nG }, () => new Array(nPos).fill(null));

        if (strategy === 'original') {
            setGenomeArrangement(originalArrangement.map(g => [...g]));
            setActiveGenomeStrategy('original');
            return;
        }

        if (strategy === 'random') {
            for (let p = 0; p < nPos; p++) {
                const candidates = [...(tilesByPosition.get(p) || [])];
                for (let i = candidates.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [candidates[i], candidates[j]] = [candidates[j], candidates[i]];
                }
                for (let g = 0; g < candidates.length && g < nG; g++) {
                    result[g][p] = candidates[g].id;
                }
            }
            setGenomeArrangement(result);
            setActiveGenomeStrategy('random');
            return;
        }

        if (strategy === 'maxDiversity') {
            const groupCats: Set<string>[] = Array.from({ length: nG }, () => new Set());
            for (let p = 0; p < nPos; p++) {
                const candidates = [...(tilesByPosition.get(p) || [])];
                const pairs: { g: number; tile: Tile; score: number }[] = [];
                for (let g = 0; g < Math.min(candidates.length, nG); g++) {
                    for (const t of candidates) {
                        const cv = filteredCatVector(tileCatVector.get(t.id) || {}, excludedCats);
                        const newCats = Object.keys(cv).filter(c => !groupCats[g].has(c)).length;
                        pairs.push({ g, tile: t, score: newCats });
                    }
                }
                pairs.sort((a, b) => b.score - a.score);
                const usedTiles = new Set<number>();
                const usedGroups = new Set<number>();
                for (const { g, tile } of pairs) {
                    if (usedTiles.has(tile.id) || usedGroups.has(g)) continue;
                    result[g][p] = tile.id;
                    const cv = filteredCatVector(tileCatVector.get(tile.id) || {}, excludedCats);
                    for (const c of Object.keys(cv)) groupCats[g].add(c);
                    usedTiles.add(tile.id);
                    usedGroups.add(g);
                    if (usedGroups.size >= Math.min(candidates.length, nG)) break;
                }
            }
            setGenomeArrangement(result);
            setActiveGenomeStrategy('maxDiversity');
            return;
        }

        if (strategy === 'minDiversity') {
            const groupCats: Map<string, number>[] = Array.from({ length: nG }, () => new Map());

            const pos0 = [...(tilesByPosition.get(0) || [])];
            pos0.sort((a, b) => {
                const av = filteredCatVector(tileCatVector.get(a.id) || {}, excludedCats);
                const bv = filteredCatVector(tileCatVector.get(b.id) || {}, excludedCats);
                const aTop = Object.entries(av).sort((x, y) => y[1] - x[1])[0]?.[0] || '';
                const bTop = Object.entries(bv).sort((x, y) => y[1] - x[1])[0]?.[0] || '';
                return aTop.localeCompare(bTop);
            });
            for (let g = 0; g < Math.min(pos0.length, nG); g++) {
                result[g][0] = pos0[g].id;
                const cv = filteredCatVector(tileCatVector.get(pos0[g].id) || {}, excludedCats);
                for (const [c, n] of Object.entries(cv)) groupCats[g].set(c, n);
            }

            for (let p = 1; p < nPos; p++) {
                const candidates = [...(tilesByPosition.get(p) || [])];
                const pairs: { g: number; tile: Tile; score: number }[] = [];
                for (let g = 0; g < Math.min(candidates.length, nG); g++) {
                    for (const t of candidates) {
                        const cv = filteredCatVector(tileCatVector.get(t.id) || {}, excludedCats);
                        const cats = Object.keys(cv);
                        if (cats.length === 0) { pairs.push({ g, tile: t, score: 0 }); continue; }
                        const totalGenes = Object.values(cv).reduce((s, v) => s + v, 0);
                        const overlapGenes = cats.reduce((s, c) => s + (groupCats[g].has(c) ? (cv[c] || 0) : 0), 0);
                        pairs.push({ g, tile: t, score: overlapGenes / totalGenes });
                    }
                }
                pairs.sort((a, b) => b.score - a.score);
                const usedTiles = new Set<number>();
                const usedGroups = new Set<number>();
                for (const { g, tile } of pairs) {
                    if (usedTiles.has(tile.id) || usedGroups.has(g)) continue;
                    result[g][p] = tile.id;
                    const cv = filteredCatVector(tileCatVector.get(tile.id) || {}, excludedCats);
                    for (const [c, n] of Object.entries(cv)) groupCats[g].set(c, (groupCats[g].get(c) || 0) + n);
                    usedTiles.add(tile.id);
                    usedGroups.add(g);
                    if (usedGroups.size >= Math.min(candidates.length, nG)) break;
                }
            }
            setGenomeArrangement(result);
            setActiveGenomeStrategy('minDiversity');
            return;
        }

        if (strategy === 'maxGG') {
            const groupScores = new Array(nG).fill(0);
            for (let p = 0; p < nPos; p++) {
                const candidates = [...(tilesByPosition.get(p) || [])];
                candidates.sort((a, b) => {
                    if (a.gg_ready !== b.gg_ready) return a.gg_ready ? -1 : 1;
                    return a.internal_bsai - b.internal_bsai;
                });
                const groupOrder = Array.from({ length: Math.min(candidates.length, nG) }, (_, i) => i)
                    .sort((a, b) => groupScores[a] - groupScores[b]);
                for (let i = 0; i < groupOrder.length; i++) {
                    const g = groupOrder[i];
                    result[g][p] = candidates[i].id;
                    if (candidates[i].gg_ready) groupScores[g]++;
                }
            }
            setGenomeArrangement(result);
            setActiveGenomeStrategy('maxGG');
            return;
        }

        if (strategy === 'minBsaI') {
            const groupBsai = new Array(nG).fill(0);
            for (let p = 0; p < nPos; p++) {
                const candidates = [...(tilesByPosition.get(p) || [])];
                candidates.sort((a, b) => a.internal_bsai - b.internal_bsai);
                const groupOrder = Array.from({ length: Math.min(candidates.length, nG) }, (_, i) => i)
                    .sort((a, b) => groupBsai[b] - groupBsai[a]);
                for (let i = 0; i < groupOrder.length; i++) {
                    const g = groupOrder[i];
                    result[g][p] = candidates[i].id;
                    groupBsai[g] += candidates[i].internal_bsai;
                }
            }
            setGenomeArrangement(result);
            setActiveGenomeStrategy('minBsaI');
            return;
        }
    }, [nGroups, nPos, tilesByPosition, tileCatVector, originalArrangement, excludedCats]);

    // ── Genome-wide stats ──
    const genomeStats = useMemo(() => {
        if (!genomeArrangement) return null;
        const stats = genomeArrangement.map(groupTiles =>
            computeGroupStats(groupTiles, bundle.tiles, tileGenes)
        );
        const avgCats = stats.reduce((s, st) => s + st.nCats, 0) / stats.length;
        const avgGG = stats.reduce((s, st) => s + st.ggReady, 0) / stats.length;
        const avgBsai = stats.reduce((s, st) => s + st.totalBsai, 0) / stats.length;
        const totalBsai = stats.reduce((s, st) => s + st.totalBsai, 0);
        const totalGG = stats.reduce((s, st) => s + st.ggReady, 0);
        return { perGroup: stats, avgCats, avgGG, avgBsai, totalBsai, totalGG };
    }, [genomeArrangement, bundle.tiles, tileGenes]);

    // ── Original genome stats (for comparison) ──
    const origStats = useMemo(() => {
        const stats = originalArrangement.map(groupTiles =>
            computeGroupStats(groupTiles, bundle.tiles, tileGenes)
        );
        const avgCats = stats.reduce((s, st) => s + st.nCats, 0) / stats.length;
        const avgGG = stats.reduce((s, st) => s + st.ggReady, 0) / stats.length;
        const avgBsai = stats.reduce((s, st) => s + st.totalBsai, 0) / stats.length;
        const totalBsai = stats.reduce((s, st) => s + st.totalBsai, 0);
        const totalGG = stats.reduce((s, st) => s + st.ggReady, 0);
        return { perGroup: stats, avgCats, avgGG, avgBsai, totalBsai, totalGG };
    }, [originalArrangement, bundle.tiles, tileGenes]);

    // ═══════════════════════════════════════════════════════════════════
    //  RENDER
    // ═══════════════════════════════════════════════════════════════════
    return (
        <div className="recombinator">
            <h2 className="recomb-title">🧬 Lvl1 Recombination Lab</h2>
            <p className="recomb-subtitle">
                Build custom Lvl1 assemblies by picking tiles from any group at each of {nPos} positions.
                Tiles at the same position share overhangs and are fully interchangeable.
            </p>

            {/* Mode toggle */}
            <div className="recomb-mode-toggle">
                <button className={mode === 'single' ? 'active' : ''} onClick={() => setMode('single')}>
                    🔬 Single Group
                </button>
                <button className={mode === 'genome' ? 'active' : ''} onClick={() => setMode('genome')}>
                    🌐 Genome-Wide
                </button>
            </div>

            {/* ── Category Exclusion Filter ────────────────────────── */}
            <div className="cat-filter-section">
                <button className="cat-filter-toggle" onClick={() => setShowCatFilter(!showCatFilter)}>
                    <span>⚙️ Category Filter</span>
                    <span className="cat-filter-badge">{excludedCats.size} excluded</span>
                    <span className="cat-filter-arrow">{showCatFilter ? '▲' : '▼'}</span>
                </button>
                {showCatFilter && (
                    <div className="cat-filter-panel">
                        <p className="cat-filter-hint">
                            Excluded categories are <strong>ignored during optimization scoring</strong> — their genes still appear in results,
                            but the algorithm won't bias toward tiles dominated by these annotations.
                        </p>
                        <div className="cat-filter-actions">
                            <button onClick={() => setExcludedCats(new Set())}>Include All</button>
                            <button onClick={() => setExcludedCats(new Set(['Other', 'Uncharacterized', 'Unknown']))}>
                                Exclude Vague
                            </button>
                        </div>
                        <div className="cat-filter-grid">
                            {allCategories.map(cat => {
                                const isExcluded = excludedCats.has(cat);
                                const count = geneProducts.filter(g => g.category === cat).length;
                                return (
                                    <label key={cat} className={`cat-filter-item ${isExcluded ? 'excluded' : ''}`}>
                                        <input
                                            type="checkbox"
                                            checked={!isExcluded}
                                            onChange={() => toggleCatExclusion(cat)}
                                        />
                                        <span className="cat-filter-dot" style={{ background: getCatColor(cat) }} />
                                        <span className="cat-filter-name">{cat}</span>
                                        <span className="cat-filter-count">{count}</span>
                                    </label>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>

            {mode === 'single' ? (
                // ═══════════════════════════════════════════════════════
                //  SINGLE GROUP MODE
                // ═══════════════════════════════════════════════════════
                <>
                    <div className="recomb-presets">
                        <span className="presets-label">Optimization Presets:</span>
                        <button className="preset-btn diversity" onClick={() => applyPreset('maxDiversity')}>🌈 Max Diversity</button>
                        <button className="preset-btn focus" onClick={() => applyPreset('minDiversity')}>🎯 Min Diversity</button>
                        <button className="preset-btn gg" onClick={() => applyPreset('maxGG')}>✅ Max GG-Ready</button>
                        <button className="preset-btn bsai" onClick={() => applyPreset('minBsaI')}>✂️ Min BsaI</button>
                        <button className="preset-btn random" onClick={() => applyPreset('random')}>🎲 Random</button>
                        <div className="preset-original">
                            <button className="preset-btn original" onClick={() => applyPreset('original')}>📋 Original</button>
                            <select value={compareGroup} onChange={e => setCompareGroup(Number(e.target.value))} className="group-select">
                                {bundle.lvl1_groups.map(g => (<option key={g.id} value={g.id}>G{g.id}</option>))}
                            </select>
                        </div>
                    </div>

                    <div className="recomb-scores">
                        <div className="score-card"><span className="score-value accent-blue">{assemblyStats.categories.length}</span><span className="score-label">Categories</span></div>
                        <div className="score-card"><span className="score-value accent-purple">{assemblyStats.totalGenes}</span><span className="score-label">Genes</span></div>
                        <div className="score-card"><span className="score-value accent-green">{assemblyStats.ggReady}/{assemblyStats.nSelected}</span><span className="score-label">GG-Ready</span></div>
                        <div className="score-card"><span className={`score-value ${assemblyStats.totalBsai > 0 ? 'accent-red' : 'accent-green'}`}>{assemblyStats.totalBsai}</span><span className="score-label">BsaI Sites</span></div>
                        <div className="score-card"><span className="score-value accent-cyan">{(assemblyStats.totalLength / 1000).toFixed(1)} kb</span><span className="score-label">Total Length</span></div>
                    </div>

                    <div className="recomb-slots-wrap">
                        <h3>Assembly Slots</h3>
                        <div className="recomb-slots">
                            {Array.from({ length: nPos }, (_, p) => {
                                const tid = selected[p];
                                const tile = tid !== null ? bundle.tiles[tid] : null;
                                const genes = tid !== null ? (tileGenes.get(tid) || []) : [];
                                const candidates = tilesByPosition.get(p) || [];
                                const catCounts: Record<string, number> = {};
                                for (const g of genes) catCounts[g.category] = (catCounts[g.category] || 0) + 1;
                                const topCat = Object.entries(catCounts).sort((a, b) => b[1] - a[1])[0];
                                return (
                                    <div key={p} className="recomb-slot" style={{ borderTopColor: topCat ? getCatColor(topCat[0]) : '#30363d' }}>
                                        <div className="slot-header">
                                            <span className="slot-pos">P{p}</span>
                                            <span className="slot-oh">{bundle.design.standard_overhangs[p]}→{bundle.design.standard_overhangs[p + 1]}</span>
                                        </div>
                                        <select value={tid ?? ''} onChange={e => { const ns = [...selected]; ns[p] = e.target.value ? Number(e.target.value) : null; setSelected(ns); }} className="slot-select">
                                            {candidates.map(c => {
                                                const cG = tileGenes.get(c.id) || [];
                                                return (<option key={c.id} value={c.id}>T{c.id} (G{c.lvl1_group}) — {cG.length} genes {c.gg_ready ? '✓' : `⚠${c.internal_bsai}`}</option>);
                                            })}
                                        </select>
                                        {tile && (<div className="slot-info"><span className="slot-source">G{tile.lvl1_group}</span><span className="slot-genes">{genes.length} genes</span><span className={`slot-status ${tile.gg_ready ? 'ready' : 'blocked'}`}>{tile.gg_ready ? '✓ GG' : `⚠ ${tile.internal_bsai} BsaI`}</span></div>)}
                                        {topCat && (<div className="slot-cat" style={{ color: getCatColor(topCat[0]) }}>{topCat[0]}</div>)}
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <div className="recomb-chart-card">
                        <h3>Functional Category Breakdown</h3>
                        <div className="recomb-plot">
                            <Plot
                                data={[{ y: assemblyStats.categories.map(([c]) => c).reverse(), x: assemblyStats.categories.map(([, v]) => v).reverse(), type: 'bar', orientation: 'h', marker: { color: assemblyStats.categories.map(([c]) => getCatColor(c)).reverse() }, hovertemplate: '%{y}: %{x} genes<extra></extra>' }]}
                                layout={{ ...DARK, margin: { l: 140, r: 20, t: 10, b: 40 }, xaxis: { ...DARK.xaxis, title: { text: 'Gene count', font: { size: 11, color: '#8b949e' } } } }}
                                config={PCFG} useResizeHandler style={{ width: '100%', height: '100%' }}
                            />
                        </div>
                    </div>

                    <div className="recomb-chart-card">
                        <h3>Custom vs Original G{compareGroup}</h3>
                        <div className="recomb-plot">
                            <Plot
                                data={[
                                    { name: 'Custom Assembly', y: allCatLabels.slice().reverse(), x: allCatLabels.map(c => assemblyStats.categories.find(([cc]) => cc === c)?.[1] || 0).reverse(), type: 'bar', orientation: 'h', marker: { color: '#58a6ff' }, hovertemplate: '%{y}: %{x} genes<extra>Custom</extra>' },
                                    { name: `G${compareGroup} Original`, y: allCatLabels.slice().reverse(), x: allCatLabels.map(c => compareStats.find(([cc]) => cc === c)?.[1] || 0).reverse(), type: 'bar', orientation: 'h', marker: { color: '#6e768166' }, hovertemplate: '%{y}: %{x} genes<extra>G' + compareGroup + '</extra>' },
                                ]}
                                layout={{ ...DARK, margin: { l: 140, r: 20, t: 10, b: 40 }, barmode: 'group', showlegend: true, legend: { orientation: 'h' as const, y: -0.15, x: 0.5, xanchor: 'center' as const, font: { size: 11, color: '#8b949e' } }, xaxis: { ...DARK.xaxis, title: { text: 'Gene count', font: { size: 11, color: '#8b949e' } } } }}
                                config={PCFG} useResizeHandler style={{ width: '100%', height: '100%' }}
                            />
                        </div>
                    </div>

                    <div className="recomb-gene-list">
                        <h3>Genes in Custom Assembly ({assemblyStats.totalGenes})</h3>
                        <div className="qc-gene-list">
                            <div className="gene-list-header"><span>Gene</span><span>Product</span><span>Category</span><span>Source</span></div>
                            {assemblyStats.allGenes.slice(0, 150).map((gp, i) => {
                                const sourceTile = selected.find(tid => { if (tid === null) return false; const t = bundle.tiles[tid]; return gp.end > t.start && gp.start < t.end; });
                                const tile = sourceTile !== null && sourceTile !== undefined ? bundle.tiles[sourceTile] : null;
                                return (
                                    <div key={i} className="gene-list-row">
                                        <span className="gl-gene">{gp.gene}</span>
                                        <span className="gl-product">{gp.product || '—'}</span>
                                        <span><span className="cat-tag" style={{ background: getCatColor(gp.category) + '33', color: getCatColor(gp.category) }}>{gp.category}</span></span>
                                        <span className="gl-group">{tile ? `T${tile.id} (G${tile.lvl1_group})` : '—'}</span>
                                    </div>
                                );
                            })}
                            {assemblyStats.allGenes.length > 150 && (<div className="gene-list-more">Showing 150 of {assemblyStats.allGenes.length} genes.</div>)}
                        </div>
                    </div>
                </>
            ) : (
                // ═══════════════════════════════════════════════════════
                //  GENOME-WIDE MODE
                // ═══════════════════════════════════════════════════════
                <>
                    <div className="recomb-presets">
                        <span className="presets-label">Genome-Wide Strategy:</span>
                        <button className={`preset-btn diversity ${activeGenomeStrategy === 'maxDiversity' ? 'active' : ''}`} onClick={() => applyGenomePreset('maxDiversity')}>🌈 Max Diversity</button>
                        <button className={`preset-btn focus ${activeGenomeStrategy === 'minDiversity' ? 'active' : ''}`} onClick={() => applyGenomePreset('minDiversity')}>🎯 Min Diversity</button>
                        <button className={`preset-btn gg ${activeGenomeStrategy === 'maxGG' ? 'active' : ''}`} onClick={() => applyGenomePreset('maxGG')}>✅ Max GG-Ready</button>
                        <button className={`preset-btn bsai ${activeGenomeStrategy === 'minBsaI' ? 'active' : ''}`} onClick={() => applyGenomePreset('minBsaI')}>✂️ Min BsaI</button>
                        <button className={`preset-btn random ${activeGenomeStrategy === 'random' ? 'active' : ''}`} onClick={() => applyGenomePreset('random')}>🎲 Random</button>
                        <button className={`preset-btn original ${activeGenomeStrategy === 'original' ? 'active' : ''}`} onClick={() => applyGenomePreset('original')}>📋 Original</button>
                    </div>

                    {!genomeStats ? (
                        <div className="genome-empty">
                            <p>Select a genome-wide strategy above to reassign all {bundle.tiles.length} tiles across {nGroups} groups.</p>
                            <p className="genome-empty-hint">Each tile stays at its overhang position but moves to a different group to optimize the chosen objective.</p>
                        </div>
                    ) : (
                        <>
                            {/* Genome-wide score cards */}
                            <div className="recomb-scores">
                                <div className="score-card">
                                    <span className="score-value accent-blue">{genomeStats.avgCats.toFixed(1)}</span>
                                    <span className="score-label">Avg Categories/Group</span>
                                    <span className="score-delta">{origStats.avgCats.toFixed(1)} original</span>
                                </div>
                                <div className="score-card">
                                    <span className="score-value accent-green">{genomeStats.totalGG}</span>
                                    <span className="score-label">Total GG-Ready</span>
                                    <span className="score-delta">{origStats.totalGG} original</span>
                                </div>
                                <div className="score-card">
                                    <span className={`score-value ${genomeStats.totalBsai > origStats.totalBsai ? 'accent-red' : 'accent-green'}`}>{genomeStats.totalBsai}</span>
                                    <span className="score-label">Total BsaI Sites</span>
                                    <span className="score-delta">{origStats.totalBsai} original</span>
                                </div>
                                <div className="score-card">
                                    <span className="score-value accent-purple">{genomeStats.avgGG.toFixed(1)}/{nPos}</span>
                                    <span className="score-label">Avg GG-Ready/Group</span>
                                    <span className="score-delta">{origStats.avgGG.toFixed(1)}/{nPos} original</span>
                                </div>
                            </div>

                            {/* Diversity heatmap */}
                            <div className="recomb-chart-card">
                                <h3>Category Distribution Across Groups {activeGenomeStrategy !== 'original' ? `(${activeGenomeStrategy})` : '(Original)'}</h3>
                                <div className="recomb-plot tall">
                                    <Plot
                                        data={[{
                                            z: genomeStats.perGroup.map(s => allCategories.map(c => s.catCounts[c] || 0)),
                                            x: allCategories,
                                            y: genomeStats.perGroup.map((_, i) => `G${i}`),
                                            type: 'heatmap',
                                            colorscale: [[0, '#0d1117'], [0.3, '#1a3a5c'], [0.6, '#264f7a'], [1, '#58a6ff']],
                                            hovertemplate: 'G%{y} · %{x}: %{z} genes<extra></extra>',
                                        }]}
                                        layout={{
                                            ...DARK,
                                            margin: { l: 50, r: 20, t: 10, b: 100 },
                                            xaxis: { ...DARK.xaxis, tickangle: -45, tickfont: { size: 9, color: '#8b949e' } },
                                            yaxis: { ...DARK.yaxis, tickfont: { size: 9, color: '#8b949e' }, autorange: 'reversed' as const },
                                        }}
                                        config={PCFG} useResizeHandler style={{ width: '100%', height: '100%' }}
                                    />
                                </div>
                            </div>

                            {/* Comparison charts */}
                            <div className="recomb-chart-card">
                                <h3>Category Diversity per Group: Optimized vs Original</h3>
                                <div className="recomb-plot">
                                    <Plot
                                        data={[
                                            { name: activeGenomeStrategy || 'Optimized', x: genomeStats.perGroup.map((_, i) => `G${i}`), y: genomeStats.perGroup.map(s => s.nCats), type: 'bar', marker: { color: '#58a6ff' }, hovertemplate: 'G%{x}: %{y} categories<extra>Optimized</extra>' },
                                            { name: 'Original', x: origStats.perGroup.map((_, i) => `G${i}`), y: origStats.perGroup.map(s => s.nCats), type: 'bar', marker: { color: '#6e768166' }, hovertemplate: 'G%{x}: %{y} categories<extra>Original</extra>' },
                                        ]}
                                        layout={{ ...DARK, barmode: 'group', showlegend: true, legend: { orientation: 'h' as const, y: -0.2, x: 0.5, xanchor: 'center' as const, font: { size: 11, color: '#8b949e' } }, xaxis: { ...DARK.xaxis, tickfont: { size: 9, color: '#8b949e' } }, yaxis: { ...DARK.yaxis, title: { text: 'Distinct categories', font: { size: 11, color: '#8b949e' } } } }}
                                        config={PCFG} useResizeHandler style={{ width: '100%', height: '100%' }}
                                    />
                                </div>
                            </div>

                            <div className="recomb-chart-card">
                                <h3>BsaI Sites per Group: Optimized vs Original</h3>
                                <div className="recomb-plot">
                                    <Plot
                                        data={[
                                            { name: activeGenomeStrategy || 'Optimized', x: genomeStats.perGroup.map((_, i) => `G${i}`), y: genomeStats.perGroup.map(s => s.totalBsai), type: 'bar', marker: { color: '#f85149' }, hovertemplate: 'G%{x}: %{y} BsaI sites<extra>Optimized</extra>' },
                                            { name: 'Original', x: origStats.perGroup.map((_, i) => `G${i}`), y: origStats.perGroup.map(s => s.totalBsai), type: 'bar', marker: { color: '#6e768166' }, hovertemplate: 'G%{x}: %{y} BsaI sites<extra>Original</extra>' },
                                        ]}
                                        layout={{ ...DARK, barmode: 'group', showlegend: true, legend: { orientation: 'h' as const, y: -0.2, x: 0.5, xanchor: 'center' as const, font: { size: 11, color: '#8b949e' } }, xaxis: { ...DARK.xaxis, tickfont: { size: 9, color: '#8b949e' } }, yaxis: { ...DARK.yaxis, title: { text: 'Internal BsaI sites', font: { size: 11, color: '#8b949e' } } } }}
                                        config={PCFG} useResizeHandler style={{ width: '100%', height: '100%' }}
                                    />
                                </div>
                            </div>

                            {/* Per-group summary table with expandable rows */}
                            <div className="recomb-chart-card">
                                <h3>Per-Group Summary <span className="table-hint">(click a row to inspect tiles)</span></h3>
                                <div className="genome-table-wrap">
                                    <table className="genome-table">
                                        <thead>
                                            <tr>
                                                <th></th>
                                                <th>Group</th>
                                                <th>Categories</th>
                                                <th>Genes</th>
                                                <th>GG-Ready</th>
                                                <th>BsaI</th>
                                                <th>Length</th>
                                                <th>Δ Cats</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {genomeStats.perGroup.map((s, g) => {
                                                const orig = origStats.perGroup[g];
                                                const deltaCats = s.nCats - orig.nCats;
                                                const isExpanded = expandedGroup === g;
                                                const groupTileIds = genomeArrangement![g];
                                                return (
                                                    <>
                                                        <tr key={g} className={`gt-row ${isExpanded ? 'expanded' : ''}`} onClick={() => setExpandedGroup(isExpanded ? null : g)}>
                                                            <td className="gt-expand">{isExpanded ? '▼' : '▶'}</td>
                                                            <td className="gt-group">G{g}</td>
                                                            <td><span className="accent-blue">{s.nCats}</span></td>
                                                            <td>{s.totalGenes}</td>
                                                            <td><span className="accent-green">{s.ggReady}/{nPos}</span></td>
                                                            <td><span className={s.totalBsai > 0 ? 'accent-red' : 'accent-green'}>{s.totalBsai}</span></td>
                                                            <td>{(s.totalLength / 1000).toFixed(1)} kb</td>
                                                            <td className={deltaCats > 0 ? 'accent-green' : deltaCats < 0 ? 'accent-red' : ''}>
                                                                {deltaCats > 0 ? `+${deltaCats}` : deltaCats}
                                                            </td>
                                                        </tr>
                                                        {isExpanded && (
                                                            <tr key={`${g}-detail`} className="gt-detail-row">
                                                                <td colSpan={8}>
                                                                    <div className="gt-detail-content">
                                                                        <div className="gt-detail-tiles">
                                                                            {groupTileIds.map((tid, p) => {
                                                                                if (tid === null) return (
                                                                                    <div key={p} className="gt-tile empty">
                                                                                        <span className="gt-tile-pos">P{p}</span>
                                                                                        <span className="gt-tile-empty">—</span>
                                                                                    </div>
                                                                                );
                                                                                const tile = bundle.tiles[tid];
                                                                                const genes = tileGenes.get(tid) || [];
                                                                                const catCounts: Record<string, number> = {};
                                                                                for (const gn of genes) catCounts[gn.category] = (catCounts[gn.category] || 0) + 1;
                                                                                const topCat = Object.entries(catCounts).sort((a, b) => b[1] - a[1])[0];
                                                                                const origTile = originalArrangement[g][p];
                                                                                const isSwapped = origTile !== tid;
                                                                                return (
                                                                                    <div key={p} className={`gt-tile ${isSwapped ? 'swapped' : ''}`} style={{ borderTopColor: topCat ? getCatColor(topCat[0]) : '#30363d' }}>
                                                                                        <div className="gt-tile-header">
                                                                                            <span className="gt-tile-pos">P{p}</span>
                                                                                            {isSwapped && <span className="gt-tile-swap">↻</span>}
                                                                                        </div>
                                                                                        <span className="gt-tile-id">T{tid}</span>
                                                                                        <span className="gt-tile-src">from G{tile.lvl1_group}</span>
                                                                                        <span className="gt-tile-genes">{genes.length} genes</span>
                                                                                        <span className={`gt-tile-status ${tile.gg_ready ? 'ready' : 'blocked'}`}>
                                                                                            {tile.gg_ready ? '✓' : `⚠${tile.internal_bsai}`}
                                                                                        </span>
                                                                                        {topCat && <span className="gt-tile-cat" style={{ color: getCatColor(topCat[0]) }}>{topCat[0]}</span>}
                                                                                    </div>
                                                                                );
                                                                            })}
                                                                        </div>
                                                                        {/* Top categories for this group */}
                                                                        <div className="gt-detail-cats">
                                                                            {Object.entries(s.catCounts)
                                                                                .sort((a, b) => b[1] - a[1])
                                                                                .slice(0, 10)
                                                                                .map(([cat, count]) => (
                                                                                    <span key={cat} className="cat-tag" style={{ background: getCatColor(cat) + '33', color: getCatColor(cat) }}>
                                                                                        {cat}: {count}
                                                                                    </span>
                                                                                ))
                                                                            }
                                                                        </div>
                                                                    </div>
                                                                </td>
                                                            </tr>
                                                        )}
                                                    </>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    );
}
