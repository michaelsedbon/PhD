import { useRef, useEffect, useMemo, useState, useCallback } from 'react';
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

/* ── Helper: draw histogram on canvas ──────────────────────────────── */
function drawHistogram(
    canvas: HTMLCanvasElement,
    values: number[],
    binCount: number,
    label: string,
    color: string,
    unit: string = '',
) {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.parentElement!.clientWidth;
    const h = 180;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;

    const ctx = canvas.getContext('2d')!;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    if (values.length === 0) return;

    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    const binW = range / binCount;

    const bins = new Array(binCount).fill(0);
    for (const v of values) {
        const idx = Math.min(Math.floor((v - min) / binW), binCount - 1);
        bins[idx]++;
    }
    const maxBin = Math.max(...bins);

    const padLeft = 40;
    const padBottom = 28;
    const padTop = 8;
    const plotW = w - padLeft - 10;
    const plotH = h - padBottom - padTop;
    const barW = plotW / binCount;

    // Axes
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padLeft, padTop);
    ctx.lineTo(padLeft, h - padBottom);
    ctx.lineTo(w - 10, h - padBottom);
    ctx.stroke();

    // Y-axis labels
    ctx.font = '9px Inter, sans-serif';
    ctx.fillStyle = '#6e7681';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let i = 0; i <= 4; i++) {
        const val = Math.round((maxBin / 4) * i);
        const yPos = h - padBottom - (plotH * i) / 4;
        ctx.fillText(`${val}`, padLeft - 6, yPos);
        ctx.strokeStyle = '#21262d';
        ctx.beginPath();
        ctx.moveTo(padLeft, yPos);
        ctx.lineTo(w - 10, yPos);
        ctx.stroke();
    }

    // Bars
    for (let i = 0; i < binCount; i++) {
        const barH = maxBin > 0 ? (bins[i] / maxBin) * plotH : 0;
        const bx = padLeft + i * barW + 1;
        const by = h - padBottom - barH;
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.8;
        ctx.fillRect(bx, by, barW - 2, barH);
        ctx.globalAlpha = 1;
    }

    // X-axis labels
    ctx.fillStyle = '#6e7681';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    const step = Math.max(1, Math.floor(binCount / 6));
    for (let i = 0; i <= binCount; i += step) {
        const val = min + i * binW;
        const xPos = padLeft + i * barW;
        let lbl: string;
        if (unit === 'kb') lbl = `${(val / 1000).toFixed(1)}`;
        else if (unit === '%') lbl = `${val.toFixed(0)}%`;
        else lbl = `${val.toFixed(0)}`;
        ctx.fillText(lbl, xPos, h - padBottom + 4);
    }

    // Title
    ctx.fillStyle = '#8b949e';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`${label}${unit ? ` (${unit})` : ''}`, w / 2, h - 6);
}

/* ── Helper: draw bar chart on canvas ──────────────────────────────── */
function drawBarChart(
    canvas: HTMLCanvasElement,
    labels: string[],
    values: number[],
    color: string | string[],
    ylabel: string = '',
) {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.parentElement!.clientWidth;
    const h = 180;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;

    const ctx = canvas.getContext('2d')!;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    if (values.length === 0) return;

    const maxVal = Math.max(...values);
    const padLeft = 40;
    const padBottom = 28;
    const padTop = 8;
    const plotW = w - padLeft - 10;
    const plotH = h - padBottom - padTop;
    const barW = plotW / values.length;

    // Axes
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padLeft, padTop);
    ctx.lineTo(padLeft, h - padBottom);
    ctx.lineTo(w - 10, h - padBottom);
    ctx.stroke();

    // Grid + Y labels
    ctx.font = '9px Inter, sans-serif';
    ctx.fillStyle = '#6e7681';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let i = 0; i <= 4; i++) {
        const val = Math.round((maxVal / 4) * i);
        const yPos = h - padBottom - (plotH * i) / 4;
        ctx.fillText(`${val}`, padLeft - 6, yPos);
        ctx.strokeStyle = '#21262d';
        ctx.beginPath();
        ctx.moveTo(padLeft, yPos);
        ctx.lineTo(w - 10, yPos);
        ctx.stroke();
    }

    // Bars
    for (let i = 0; i < values.length; i++) {
        const barH = maxVal > 0 ? (values[i] / maxVal) * plotH : 0;
        const bx = padLeft + i * barW + 1;
        const by = h - padBottom - barH;
        ctx.fillStyle = typeof color === 'string' ? color : (color[i] || '#6e7681');
        ctx.globalAlpha = 0.8;
        ctx.fillRect(bx, by, barW - 2, barH);
        ctx.globalAlpha = 1;
    }

    // X labels (sparse)
    ctx.fillStyle = '#6e7681';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    const step = Math.max(1, Math.floor(values.length / 12));
    for (let i = 0; i < labels.length; i += step) {
        ctx.fillText(labels[i], padLeft + i * barW + barW / 2, h - padBottom + 4);
    }

    // Y label
    if (ylabel) {
        ctx.fillStyle = '#8b949e';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(ylabel, w / 2, h - 6);
    }
}

/* ── Helper: horizontal bar chart ──────────────────────────────────── */
function drawHorizontalBars(
    canvas: HTMLCanvasElement,
    data: { label: string; value: number; color: string }[],
) {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.parentElement!.clientWidth;
    const barH = 22;
    const gap = 3;
    const padLeft = 130;
    const padRight = 50;
    const h = data.length * (barH + gap) + 10;

    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;

    const ctx = canvas.getContext('2d')!;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    const maxVal = Math.max(...data.map(d => d.value));
    const plotW = w - padLeft - padRight;

    for (let i = 0; i < data.length; i++) {
        const y = i * (barH + gap) + 4;
        const barW = maxVal > 0 ? (data[i].value / maxVal) * plotW : 0;

        // Label
        ctx.font = '10px Inter, sans-serif';
        ctx.fillStyle = '#e6edf3';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillText(data[i].label, padLeft - 8, y + barH / 2);

        // Bar
        ctx.fillStyle = data[i].color;
        ctx.globalAlpha = 0.75;
        ctx.fillRect(padLeft, y, barW, barH);
        ctx.globalAlpha = 1;

        // Value
        ctx.fillStyle = '#8b949e';
        ctx.textAlign = 'left';
        ctx.fillText(`${data[i].value}`, padLeft + barW + 6, y + barH / 2);
    }
}

/* ── Heatmap: categories × groups ──────────────────────────────────── */
function drawCategoryHeatmap(
    canvas: HTMLCanvasElement,
    categories: string[],
    groups: number[],
    matrix: number[][],  // [catIdx][groupIdx]
) {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.parentElement!.clientWidth;
    const cellW = Math.max(8, Math.floor((w - 140) / groups.length));
    const cellH = 16;
    const padLeft = 130;
    const padTop = 20;
    const h = padTop + categories.length * cellH + 30;

    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;

    const ctx = canvas.getContext('2d')!;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    const maxVal = Math.max(...matrix.flat().filter(v => v > 0), 1);

    // Group labels on top
    ctx.font = '8px Inter, sans-serif';
    ctx.fillStyle = '#6e7681';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    const groupStep = Math.max(1, Math.floor(groups.length / 15));
    for (let g = 0; g < groups.length; g += groupStep) {
        ctx.fillText(`G${groups[g]}`, padLeft + g * cellW + cellW / 2, padTop - 2);
    }

    for (let c = 0; c < categories.length; c++) {
        const y = padTop + c * cellH;

        // Category label
        ctx.font = '9px Inter, sans-serif';
        ctx.fillStyle = '#e6edf3';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillText(categories[c], padLeft - 6, y + cellH / 2);

        for (let g = 0; g < groups.length; g++) {
            const val = matrix[c][g];
            const intensity = val > 0 ? Math.min(val / maxVal, 1) : 0;
            const x = padLeft + g * cellW;

            if (intensity > 0) {
                const catColor = getCatColor(categories[c]);
                // Parse hex/named color to get RGB
                ctx.fillStyle = catColor;
                ctx.globalAlpha = 0.15 + intensity * 0.75;
                ctx.fillRect(x, y, cellW - 1, cellH - 1);
                ctx.globalAlpha = 1;
            } else {
                ctx.fillStyle = '#0d1117';
                ctx.fillRect(x, y, cellW - 1, cellH - 1);
            }
        }
    }

    // Legend
    const ly = padTop + categories.length * cellH + 8;
    ctx.font = '9px Inter, sans-serif';
    ctx.fillStyle = '#6e7681';
    ctx.textAlign = 'left';
    ctx.fillText('Low', padLeft, ly + 6);
    for (let i = 0; i < 5; i++) {
        ctx.fillStyle = '#58a6ff';
        ctx.globalAlpha = 0.15 + (i / 4) * 0.75;
        ctx.fillRect(padLeft + 25 + i * 12, ly, 10, 10);
        ctx.globalAlpha = 1;
    }
    ctx.fillStyle = '#6e7681';
    ctx.fillText('High', padLeft + 25 + 5 * 12 + 4, ly + 6);
}

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

    // ── Canvas refs ──
    const tileLenRef = useRef<HTMLCanvasElement>(null);
    const gcRef = useRef<HTMLCanvasElement>(null);
    const genesPerGrpRef = useRef<HTMLCanvasElement>(null);
    const bsaiPerGrpRef = useRef<HTMLCanvasElement>(null);
    const catBarRef = useRef<HTMLCanvasElement>(null);
    const heatmapRef = useRef<HTMLCanvasElement>(null);

    const drawAll = useCallback(() => {
        if (tileLenRef.current) drawHistogram(tileLenRef.current, tileLengths, 25, 'Tile Length', '#58a6ff', 'kb');
        if (gcRef.current) drawHistogram(gcRef.current, tileGCs, 25, 'GC Content', '#39d2c0', '%');

        const groupLabels = bundle.lvl1_groups.map(g => `G${g.id}`);
        if (genesPerGrpRef.current) drawBarChart(genesPerGrpRef.current, groupLabels, genesPerGroup, '#bc8cff', 'Genes per group');
        if (bsaiPerGrpRef.current) {
            const bsaiColors = bsaiPerGroup.map(v => v > 0 ? '#f85149' : '#21262d');
            drawBarChart(bsaiPerGrpRef.current, groupLabels, bsaiPerGroup, bsaiColors, 'Internal BsaI sites');
        }
        if (catBarRef.current) {
            drawHorizontalBars(catBarRef.current, categoryCounts.map(([cat, count]) => ({
                label: cat,
                value: count,
                color: getCatColor(cat),
            })));
        }
        if (heatmapRef.current) {
            drawCategoryHeatmap(
                heatmapRef.current,
                heatmapCategories,
                bundle.lvl1_groups.map(g => g.id),
                heatmapMatrix,
            );
        }
    }, [tileLengths, tileGCs, genesPerGroup, bsaiPerGroup, categoryCounts, heatmapCategories, heatmapMatrix, bundle.lvl1_groups]);

    useEffect(() => { drawAll(); }, [drawAll]);
    useEffect(() => {
        const handler = () => drawAll();
        window.addEventListener('resize', handler);
        return () => window.removeEventListener('resize', handler);
    }, [drawAll]);

    return (
        <div className="qc-dashboard">
            <h2 className="qc-title">Assembly QC Dashboard</h2>

            {/* Row 1: Histograms */}
            <div className="qc-row">
                <div className="qc-chart-card">
                    <h3>Tile Length Distribution</h3>
                    <div className="qc-canvas-wrap"><canvas ref={tileLenRef} /></div>
                    <div className="qc-stat-row">
                        <span>Min: {(Math.min(...tileLengths) / 1000).toFixed(1)} kb</span>
                        <span>Avg: {(tileLengths.reduce((a, b) => a + b, 0) / tileLengths.length / 1000).toFixed(1)} kb</span>
                        <span>Max: {(Math.max(...tileLengths) / 1000).toFixed(1)} kb</span>
                    </div>
                </div>
                <div className="qc-chart-card">
                    <h3>GC Content Distribution</h3>
                    <div className="qc-canvas-wrap"><canvas ref={gcRef} /></div>
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
                    <div className="qc-canvas-wrap"><canvas ref={genesPerGrpRef} /></div>
                </div>
                <div className="qc-chart-card">
                    <h3>Internal BsaI Sites per Group</h3>
                    <div className="qc-canvas-wrap"><canvas ref={bsaiPerGrpRef} /></div>
                </div>
            </div>

            {/* Row 3: Functional categories */}
            <div className="qc-chart-card full">
                <h3>Functional Category Distribution ({geneProducts.length} genes)</h3>
                <div className="qc-canvas-wrap"><canvas ref={catBarRef} /></div>
            </div>

            {/* Row 4: Heatmap */}
            <div className="qc-chart-card full">
                <h3>Functional Diversity per Group</h3>
                <p className="qc-subtitle">Gene count by functional category across all {bundle.lvl1_groups.length} Lvl1 groups</p>
                <div className="qc-canvas-wrap"><canvas ref={heatmapRef} /></div>
            </div>

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
