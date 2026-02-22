import { useMemo, useState } from 'react';
import Plot from 'react-plotly.js';
import { AppData, ViewState, GeneProduct } from '../types';

interface Props {
    data: AppData;
    onNavigate: (v: ViewState) => void;
}

/* ── Color palette for categories ──────────────────────────────────── */
const CATEGORY_COLORS: Record<string, string> = {
    'Transport': '#58a6ff',
    'Kinase / Phosphatase': '#3fb950',
    'Redox Enzymes': '#f85149',
    'Biosynthesis': '#d29922',
    'Transferase': '#bc8cff',
    'Regulation': '#39d2c0',
    'Transcription': '#ff7b72',
    'Translation': '#79c0ff',
    'DNA Maintenance': '#d2a8ff',
    'Mobile Elements': '#ffa657',
    'Motility': '#56d364',
    'Membrane': '#7ee787',
    'Fimbriae / Pili': '#f778ba',
    'Proteolysis': '#ff9bce',
    'Chaperones / Stress': '#ffdf5d',
    'Uncharacterized': '#484f58',
    'Lyase / Isomerase': '#a5d6ff',
    'Hydrolase': '#ffc680',
    'Other': '#6e7681',
    'Unknown': '#30363d',
};

function getCatColor(cat: string): string {
    return CATEGORY_COLORS[cat] || '#6e7681';
}

/* ── Shared Plotly theme ───────────────────────────────────────────── */
const DARK_LAYOUT: Record<string, any> = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: '#161b22',
    font: { family: 'Inter, system-ui, sans-serif', size: 12, color: '#c9d1d9' },
    margin: { l: 50, r: 20, t: 10, b: 40 },
    autosize: true,
    xaxis: { gridcolor: '#21262d', zerolinecolor: '#21262d' },
    yaxis: { gridcolor: '#21262d', zerolinecolor: '#21262d' },
};

const PLOTLY_CONFIG: Record<string, any> = {
    responsive: true,
    displayModeBar: false,
};

export default function QCDashboard({ data, onNavigate }: Props) {
    const { bundle, geneProducts } = data;
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

    // ── Precomputed data ──
    const tileLengths = useMemo(() => bundle.tiles.map(t => t.length), [bundle.tiles]);
    const tileGCs = useMemo(() => bundle.tiles.map(t => t.gc_content), [bundle.tiles]);

    const genesPerGroup = useMemo(() => {
        const counts = new Array(bundle.lvl1_groups.length).fill(0);
        for (const gp of geneProducts) {
            for (const grp of bundle.lvl1_groups) {
                if (gp.end > grp.start && gp.start < grp.end) {
                    counts[grp.id]++;
                }
            }
        }
        return counts;
    }, [geneProducts, bundle.lvl1_groups]);

    const bsaiPerGroup = useMemo(() => {
        const counts = new Array(bundle.lvl1_groups.length).fill(0);
        for (const tile of bundle.tiles) {
            counts[tile.lvl1_group] += tile.internal_bsai;
        }
        return counts;
    }, [bundle.tiles, bundle.lvl1_groups.length]);

    const categoryCounts = useMemo(() => {
        const counts: Record<string, number> = {};
        for (const gp of geneProducts) {
            counts[gp.category] = (counts[gp.category] || 0) + 1;
        }
        return Object.entries(counts)
            .sort((a, b) => b[1] - a[1])
            .filter(([, v]) => v > 0);
    }, [geneProducts]);

    // Category × group matrix for heatmap
    const { heatmapCategories, heatmapMatrix } = useMemo(() => {
        const cats = categoryCounts.map(([c]) => c);
        const matrix: number[][] = cats.map(() =>
            new Array(bundle.lvl1_groups.length).fill(0)
        );
        for (const gp of geneProducts) {
            const catIdx = cats.indexOf(gp.category);
            if (catIdx < 0) continue;
            for (const grp of bundle.lvl1_groups) {
                if (gp.end > grp.start && gp.start < grp.end) {
                    matrix[catIdx][grp.id]++;
                }
            }
        }
        return { heatmapCategories: cats, heatmapMatrix: matrix };
    }, [geneProducts, categoryCounts, bundle.lvl1_groups]);

    // Compute outlier groups using Jensen-Shannon divergence
    const outlierGroups = useMemo(() => {
        const cats = heatmapCategories;
        const nGroups = bundle.lvl1_groups.length;
        const nCats = cats.length;

        const proportions: number[][] = [];
        for (let gi = 0; gi < nGroups; gi++) {
            const total = heatmapMatrix.reduce((s, row) => s + row[gi], 0);
            proportions.push(total > 0
                ? heatmapMatrix.map(row => row[gi] / total)
                : new Array(nCats).fill(0)
            );
        }

        const avg = new Array(nCats).fill(0);
        for (let ci = 0; ci < nCats; ci++) {
            for (let gi = 0; gi < nGroups; gi++) {
                avg[ci] += proportions[gi][ci];
            }
            avg[ci] /= nGroups;
        }

        function kl(p: number[], q: number[]): number {
            let sum = 0;
            for (let i = 0; i < p.length; i++) {
                if (p[i] > 0 && q[i] > 0) sum += p[i] * Math.log2(p[i] / q[i]);
            }
            return sum;
        }
        function jsd(p: number[], q: number[]): number {
            const m = p.map((v, i) => (v + q[i]) / 2);
            return (kl(p, m) + kl(q, m)) / 2;
        }

        const divergences = proportions.map((p, gi) => ({
            groupId: gi,
            jsd: jsd(p, avg),
            proportions: p,
        }));

        const enriched = divergences.map(d => {
            const diffs = cats.map((cat, ci) => ({
                cat,
                diff: d.proportions[ci] - avg[ci],
                groupPct: d.proportions[ci] * 100,
                avgPct: avg[ci] * 100,
            }));
            diffs.sort((a, b) => Math.abs(b.diff) - Math.abs(a.diff));
            return { ...d, topDeviations: diffs.slice(0, 3) };
        });

        enriched.sort((a, b) => b.jsd - a.jsd);
        return enriched.slice(0, 6);
    }, [heatmapCategories, heatmapMatrix, bundle.lvl1_groups.length]);

    // Filtered genes for explorer
    const filteredGenes = useMemo(() => {
        let genes = geneProducts;
        if (selectedCategory) {
            genes = genes.filter(g => g.category === selectedCategory);
        }
        return genes;
    }, [geneProducts, selectedCategory]);

    // Gene → group mapping for navigation
    const geneGroupMap = useMemo(() => {
        const map = new Map<string, number>();
        for (const gp of geneProducts) {
            const center = (gp.start + gp.end) / 2;
            for (const grp of bundle.lvl1_groups) {
                if (center >= grp.start && center < grp.end) {
                    map.set(gp.gene, grp.id);
                    break;
                }
            }
        }
        return map;
    }, [geneProducts, bundle.lvl1_groups]);

    // ── Plotly data ──
    const groupLabels = bundle.lvl1_groups.map(g => `G${g.id}`);

    // Stacked 100% bar traces
    const stackedTraces = useMemo(() => {
        // Normalize matrix to percentages per group
        const nGroups = bundle.lvl1_groups.length;
        const totals = new Array(nGroups).fill(0);
        for (const row of heatmapMatrix) {
            for (let gi = 0; gi < nGroups; gi++) totals[gi] += row[gi];
        }
        return heatmapCategories.map((cat, ci) => ({
            x: groupLabels,
            y: groupLabels.map((_, gi) => totals[gi] > 0 ? (heatmapMatrix[ci][gi] / totals[gi]) * 100 : 0),
            name: cat,
            type: 'bar' as const,
            marker: { color: getCatColor(cat) },
            hovertemplate: `%{x}<br>${cat}: %{y:.1f}%<extra></extra>`,
        }));
    }, [heatmapCategories, heatmapMatrix, groupLabels, bundle.lvl1_groups.length]);

    return (
        <div className="qc-dashboard">
            <h2 className="qc-title">Assembly QC Dashboard</h2>

            {/* Row 1: Histograms */}
            <div className="qc-row">
                <div className="qc-chart-card">
                    <h3>Tile Length Distribution</h3>
                    <div className="qc-plot-wrap">
                        <Plot
                            data={[{
                                x: tileLengths.map(v => v / 1000),
                                type: 'histogram',
                                nbinsx: 25,
                                marker: { color: '#58a6ff' },
                                hovertemplate: '%{x:.1f} kb<br>Count: %{y}<extra></extra>',
                            }]}
                            layout={{
                                ...DARK_LAYOUT,
                                xaxis: { ...DARK_LAYOUT.xaxis, title: { text: 'Length (kb)', font: { size: 11, color: '#8b949e' } } },
                                yaxis: { ...DARK_LAYOUT.yaxis, title: { text: 'Count', font: { size: 11, color: '#8b949e' } } },
                                bargap: 0.05,
                            } as any}
                            config={PLOTLY_CONFIG}
                            useResizeHandler
                            style={{ width: '100%', height: '100%' }}
                        />
                    </div>
                    <div className="qc-stat-row">
                        <span>Min: {(Math.min(...tileLengths) / 1000).toFixed(1)} kb</span>
                        <span>Avg: {(tileLengths.reduce((a, b) => a + b, 0) / tileLengths.length / 1000).toFixed(1)} kb</span>
                        <span>Max: {(Math.max(...tileLengths) / 1000).toFixed(1)} kb</span>
                    </div>
                </div>
                <div className="qc-chart-card">
                    <h3>GC Content Distribution</h3>
                    <div className="qc-plot-wrap">
                        <Plot
                            data={[{
                                x: tileGCs,
                                type: 'histogram',
                                nbinsx: 25,
                                marker: { color: '#39d2c0' },
                                hovertemplate: '%{x:.1f}%<br>Count: %{y}<extra></extra>',
                            }]}
                            layout={{
                                ...DARK_LAYOUT,
                                xaxis: { ...DARK_LAYOUT.xaxis, title: { text: 'GC %', font: { size: 11, color: '#8b949e' } } },
                                yaxis: { ...DARK_LAYOUT.yaxis, title: { text: 'Count', font: { size: 11, color: '#8b949e' } } },
                                bargap: 0.05,
                            } as any}
                            config={PLOTLY_CONFIG}
                            useResizeHandler
                            style={{ width: '100%', height: '100%' }}
                        />
                    </div>
                    <div className="qc-stat-row">
                        <span>Min: {Math.min(...tileGCs).toFixed(1)}%</span>
                        <span>Avg: {(tileGCs.reduce((a, b) => a + b, 0) / tileGCs.length).toFixed(1)}%</span>
                        <span>Max: {Math.max(...tileGCs).toFixed(1)}%</span>
                    </div>
                </div>
            </div>

            {/* Row 2: Per-group bars */}
            <div className="qc-row">
                <div className="qc-chart-card">
                    <h3>Genes per Lvl1 Group</h3>
                    <div className="qc-plot-wrap">
                        <Plot
                            data={[{
                                x: groupLabels,
                                y: genesPerGroup,
                                type: 'bar',
                                marker: { color: '#bc8cff' },
                                hovertemplate: '%{x}<br>Genes: %{y}<extra></extra>',
                            }]}
                            layout={{
                                ...DARK_LAYOUT,
                                yaxis: { ...DARK_LAYOUT.yaxis, title: { text: 'Genes', font: { size: 11, color: '#8b949e' } } },
                            } as any}
                            config={PLOTLY_CONFIG}
                            useResizeHandler
                            style={{ width: '100%', height: '100%' }}
                        />
                    </div>
                </div>
                <div className="qc-chart-card">
                    <h3>Internal BsaI Sites per Group</h3>
                    <div className="qc-plot-wrap">
                        <Plot
                            data={[{
                                x: groupLabels,
                                y: bsaiPerGroup,
                                type: 'bar',
                                marker: { color: bsaiPerGroup.map(v => v > 0 ? '#f85149' : '#21262d') },
                                hovertemplate: '%{x}<br>BsaI sites: %{y}<extra></extra>',
                            }]}
                            layout={{
                                ...DARK_LAYOUT,
                                yaxis: { ...DARK_LAYOUT.yaxis, title: { text: 'Sites', font: { size: 11, color: '#8b949e' } } },
                            } as any}
                            config={PLOTLY_CONFIG}
                            useResizeHandler
                            style={{ width: '100%', height: '100%' }}
                        />
                    </div>
                </div>
            </div>

            {/* Row 3: Functional categories */}
            <div className="qc-chart-card full">
                <h3>Functional Category Distribution ({geneProducts.length} genes)</h3>
                <div className="qc-plot-wrap tall">
                    <Plot
                        data={[{
                            y: categoryCounts.map(([c]) => c).reverse(),
                            x: categoryCounts.map(([, v]) => v).reverse(),
                            type: 'bar',
                            orientation: 'h',
                            marker: { color: categoryCounts.map(([c]) => getCatColor(c)).reverse() },
                            hovertemplate: '%{y}<br>Count: %{x}<extra></extra>',
                        }]}
                        layout={{
                            ...DARK_LAYOUT,
                            margin: { l: 140, r: 20, t: 10, b: 40 },
                            xaxis: { ...DARK_LAYOUT.xaxis, title: { text: 'Gene count', font: { size: 11, color: '#8b949e' } } },
                        } as any}
                        config={PLOTLY_CONFIG}
                        useResizeHandler
                        style={{ width: '100%', height: '100%' }}
                    />
                </div>
            </div>

            {/* Row 4: Heatmap */}
            <div className="qc-chart-card full">
                <h3>Functional Diversity per Group</h3>
                <p className="qc-subtitle">Gene count by functional category across all {bundle.lvl1_groups.length} Lvl1 groups</p>
                <div className="qc-plot-wrap tall">
                    <Plot
                        data={[{
                            z: heatmapMatrix,
                            x: groupLabels,
                            y: heatmapCategories,
                            type: 'heatmap',
                            colorscale: [
                                [0, '#0d1117'],
                                [0.25, '#1a3a5c'],
                                [0.5, '#2d6a9f'],
                                [0.75, '#58a6ff'],
                                [1, '#79c0ff'],
                            ],
                            hovertemplate: '%{y}<br>Group %{x}<br>Count: %{z}<extra></extra>',
                            showscale: true,
                            colorbar: {
                                tickfont: { color: '#8b949e', size: 10 },
                                len: 0.8,
                                thickness: 12,
                            },
                        }]}
                        layout={{
                            ...DARK_LAYOUT,
                            margin: { l: 140, r: 60, t: 10, b: 40 },
                        } as any}
                        config={PLOTLY_CONFIG}
                        useResizeHandler
                        style={{ width: '100%', height: '100%' }}
                    />
                </div>
            </div>

            {/* Row 5: Normalized stacked bar chart */}
            <div className="qc-chart-card full">
                <h3>Functional Distribution Uniformity</h3>
                <p className="qc-subtitle">100% stacked bars — similar colors across all groups means uniform functional distribution</p>
                <div className="qc-plot-wrap tall">
                    <Plot
                        data={stackedTraces as any}
                        layout={{
                            ...DARK_LAYOUT,
                            barmode: 'stack',
                            showlegend: true,
                            legend: {
                                orientation: 'h' as const,
                                y: -0.25,
                                x: 0.5,
                                xanchor: 'center' as const,
                                font: { size: 9, color: '#8b949e' },
                            },
                            margin: { l: 50, r: 20, t: 10, b: 40 },
                            yaxis: {
                                ...DARK_LAYOUT.yaxis,
                                title: { text: '%', font: { size: 11, color: '#8b949e' } },
                                range: [0, 100],
                            },
                        } as any}
                        config={PLOTLY_CONFIG}
                        useResizeHandler
                        style={{ width: '100%', height: '100%' }}
                    />
                </div>
            </div>

            {/* Row 6: Outlier groups */}
            {outlierGroups.length > 0 && (
                <div className="qc-chart-card full">
                    <h3>Outlier Groups — Unusual Functional Profiles</h3>
                    <p className="qc-subtitle">Groups with highest Jensen-Shannon divergence from the average distribution</p>
                    <div className="outlier-grid">
                        {outlierGroups.map(o => (
                            <div
                                key={o.groupId}
                                className="outlier-card"
                                onClick={() => onNavigate({ view: 'group', groupId: o.groupId })}
                            >
                                <div className="outlier-header">
                                    <span className="outlier-group">G{o.groupId}</span>
                                    <span className="outlier-score">JSD: {o.jsd.toFixed(4)}</span>
                                </div>
                                <div className="outlier-deviations">
                                    {o.topDeviations.map((d, i) => (
                                        <div key={i} className="outlier-dev">
                                            <span
                                                className="cat-dot"
                                                style={{ background: getCatColor(d.cat) }}
                                            />
                                            <span className="dev-cat">{d.cat}</span>
                                            <span className={`dev-diff ${d.diff > 0 ? 'up' : 'down'}`}>
                                                {d.diff > 0 ? '▲' : '▼'}
                                                {Math.abs(d.diff * 100).toFixed(1)}%
                                            </span>
                                            <span className="dev-detail">
                                                ({d.groupPct.toFixed(0)}% vs {d.avgPct.toFixed(0)}% avg)
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Gene Explorer */}
            <div className="qc-gene-explorer">
                <h3>Gene Explorer</h3>
                <div className="qc-category-pills">
                    <button
                        className={`cat-pill ${selectedCategory === null ? 'active' : ''}`}
                        onClick={() => setSelectedCategory(null)}
                    >
                        All ({geneProducts.length})
                    </button>
                    {categoryCounts.map(([cat, count]) => (
                        <button
                            key={cat}
                            className={`cat-pill ${selectedCategory === cat ? 'active' : ''}`}
                            style={{
                                borderColor: getCatColor(cat),
                                ...(selectedCategory === cat ? { background: getCatColor(cat) + '33' } : {}),
                            }}
                            onClick={() => setSelectedCategory(selectedCategory === cat ? null : cat)}
                        >
                            <span className="cat-dot" style={{ background: getCatColor(cat) }} />
                            {cat} ({count})
                        </button>
                    ))}
                </div>
                <div className="qc-gene-list">
                    <div className="gene-list-header">
                        <span>Gene</span>
                        <span>Product</span>
                        <span>Category</span>
                        <span>Position</span>
                        <span>Group</span>
                    </div>
                    {filteredGenes.slice(0, 100).map((gp, i) => {
                        const grpId = geneGroupMap.get(gp.gene);
                        return (
                            <div
                                key={i}
                                className="gene-list-row"
                                onClick={() => {
                                    if (grpId !== undefined) {
                                        onNavigate({ view: 'group', groupId: grpId });
                                    }
                                }}
                            >
                                <span className="gl-gene">{gp.gene}</span>
                                <span className="gl-product">{gp.product || '—'}</span>
                                <span>
                                    <span className="cat-tag" style={{ background: getCatColor(gp.category) + '33', color: getCatColor(gp.category) }}>
                                        {gp.category}
                                    </span>
                                </span>
                                <span className="gl-pos">{gp.start.toLocaleString()} – {gp.end.toLocaleString()}</span>
                                <span className="gl-group">{grpId !== undefined ? `G${grpId}` : '—'}</span>
                            </div>
                        );
                    })}
                    {filteredGenes.length > 100 && (
                        <div className="gene-list-more">
                            Showing 100 of {filteredGenes.length} genes. Click a category to filter.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
