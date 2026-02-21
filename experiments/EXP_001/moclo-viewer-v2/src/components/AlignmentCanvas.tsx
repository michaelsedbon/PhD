import { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { Tile, CDSRegion } from '../types';

interface MutInfo {
    position: number;
    gene: string;
    original: string;
    mutant: string;
    codon: string;
}

interface Props {
    genomeSeq: string;
    tile: Tile;
    cdsRegions: CDSRegion[];
    mutations: MutInfo[];
}

// BSAI recognition: GGTCTC or reverse complement GAGACC
function findBsaISites(seq: string, offset: number): number[] {
    const sites: number[] = [];
    const fwd = 'GGTCTC';
    const rev = 'GAGACC';
    const upper = seq.toUpperCase();
    for (let i = 0; i <= upper.length - 6; i++) {
        const sub = upper.substring(i, i + 6);
        if (sub === fwd || sub === rev) {
            sites.push(offset + i);
        }
    }
    return sites;
}

const NT_COLORS: Record<string, string> = {
    A: '#3fb950',
    T: '#f85149',
    G: '#d29922',
    C: '#58a6ff',
};

type ViewMode = 'overview' | 'sequence';

export default function AlignmentCanvas({ genomeSeq, tile, cdsRegions, mutations }: Props) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wrapRef = useRef<HTMLDivElement>(null);
    const [zoom, setZoom] = useState(1);
    const [viewMode, setViewMode] = useState<ViewMode>('overview');

    const tileSeq = useMemo(() => {
        return genomeSeq.substring(tile.start, tile.end).toUpperCase();
    }, [genomeSeq, tile.start, tile.end]);

    const bsaISites = useMemo(() => {
        return findBsaISites(tileSeq, tile.start);
    }, [tileSeq, tile.start]);

    const mutPositions = useMemo(() => {
        return new Set(mutations.map(m => m.position));
    }, [mutations]);

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        const wrap = wrapRef.current;
        if (!canvas || !wrap) return;

        const dpr = window.devicePixelRatio || 1;
        const containerW = wrap.clientWidth;

        if (viewMode === 'overview') {
            // Overview: 1px per N bases, color-coded
            const bpPerPx = Math.max(1, Math.floor(tileSeq.length / (containerW * zoom)));
            const canvasW = Math.ceil(tileSeq.length / bpPerPx);
            const rowH = 20;
            const cdsH = 14;
            const bsaiH = 8;
            const totalH = rowH + 4 + cdsH + 4 + bsaiH;

            canvas.width = canvasW * dpr;
            canvas.height = totalH * dpr;
            canvas.style.width = `${canvasW}px`;
            canvas.style.height = `${totalH}px`;

            const ctx = canvas.getContext('2d')!;
            ctx.scale(dpr, dpr);
            ctx.clearRect(0, 0, canvasW, totalH);

            // GC content heatmap blocks
            let y = 0;
            for (let i = 0; i < tileSeq.length; i += bpPerPx) {
                const chunk = tileSeq.substring(i, Math.min(i + bpPerPx, tileSeq.length));
                const gc = (chunk.split('').filter(c => c === 'G' || c === 'C').length) / chunk.length;
                const px = Math.floor(i / bpPerPx);

                // Color by GC: blue = high GC, orange = low GC
                const r = Math.round(210 * (1 - gc) + 88 * gc);
                const g = Math.round(153 * (1 - gc) + 166 * gc);
                const b = Math.round(34 * (1 - gc) + 255 * gc);
                ctx.fillStyle = `rgb(${r},${g},${b})`;
                ctx.fillRect(px, y, 1, rowH);

                // Check for mutations in this chunk
                const absStart = tile.start + i;
                const absEnd = tile.start + Math.min(i + bpPerPx, tileSeq.length);
                for (const mPos of mutPositions) {
                    if (mPos >= absStart && mPos < absEnd) {
                        ctx.fillStyle = 'rgba(210,153,34,0.9)';
                        ctx.fillRect(px, y, 1, rowH);
                        break;
                    }
                }
            }

            // CDS track
            y = rowH + 4;
            for (const cds of cdsRegions) {
                const cx = Math.max(0, Math.floor((cds.start - tile.start) / bpPerPx));
                const cw = Math.max(1, Math.ceil((Math.min(cds.end, tile.end) - Math.max(cds.start, tile.start)) / bpPerPx));
                ctx.fillStyle = cds.complement
                    ? 'rgba(188,140,255,0.4)'
                    : 'rgba(57,210,192,0.4)';
                ctx.fillRect(cx, y, cw, cdsH);
            }

            // BsaI sites
            y += cdsH + 4;
            ctx.fillStyle = 'rgba(248,81,73,0.9)';
            for (const sitePos of bsaISites) {
                const px = Math.floor((sitePos - tile.start) / bpPerPx);
                ctx.fillRect(px - 1, y, 3, bsaiH);
            }

        } else {
            // Sequence mode: render base-by-base
            const charW = 8 * zoom;
            const lineH = 16;
            const charsPerLine = Math.max(10, Math.floor(containerW / charW));
            const totalLines = Math.ceil(tileSeq.length / charsPerLine);
            const labelW = 70;
            const canvasW = labelW + charsPerLine * charW;
            const totalH = totalLines * lineH + 20;

            canvas.width = canvasW * dpr;
            canvas.height = totalH * dpr;
            canvas.style.width = `${canvasW}px`;
            canvas.style.height = `${totalH}px`;

            const ctx = canvas.getContext('2d')!;
            ctx.scale(dpr, dpr);
            ctx.clearRect(0, 0, canvasW, totalH);

            ctx.font = `${Math.min(11, charW)}px JetBrains Mono, monospace`;
            ctx.textBaseline = 'middle';

            for (let line = 0; line < totalLines; line++) {
                const startIdx = line * charsPerLine;
                const y = line * lineH;
                const absPos = tile.start + startIdx;

                // Position label
                ctx.fillStyle = '#6e7681';
                ctx.textAlign = 'right';
                ctx.fillText(absPos.toLocaleString(), labelW - 8, y + lineH / 2);
                ctx.textAlign = 'left';

                // Bases
                for (let c = 0; c < charsPerLine; c++) {
                    const idx = startIdx + c;
                    if (idx >= tileSeq.length) break;
                    const base = tileSeq[idx];
                    const baseAbsPos = tile.start + idx;
                    const x = labelW + c * charW;

                    // Highlight BsaI sites
                    const isBsaI = bsaISites.some(s => baseAbsPos >= s && baseAbsPos < s + 6);
                    // Highlight mutations
                    const isMut = mutPositions.has(baseAbsPos);

                    if (isBsaI) {
                        ctx.fillStyle = 'rgba(248,81,73,0.25)';
                        ctx.fillRect(x, y, charW, lineH);
                    }
                    if (isMut) {
                        ctx.fillStyle = 'rgba(210,153,34,0.3)';
                        ctx.fillRect(x, y, charW, lineH);
                    }

                    ctx.fillStyle = NT_COLORS[base] || '#8b949e';
                    if (charW >= 6) {
                        ctx.fillText(base, x + 1, y + lineH / 2);
                    } else {
                        ctx.fillRect(x, y + 2, charW - 0.5, lineH - 4);
                    }
                }
            }
        }
    }, [tileSeq, tile, cdsRegions, bsaISites, mutPositions, zoom, viewMode]);

    useEffect(() => {
        draw();
    }, [draw]);

    // Redraw on resize
    useEffect(() => {
        const handleResize = () => draw();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [draw]);

    const zoomIn = () => setZoom(z => Math.min(z * 1.5, 10));
    const zoomOut = () => setZoom(z => Math.max(z / 1.5, 0.5));
    const resetZoom = () => setZoom(1);

    return (
        <div className="alignment-section">
            <div className="alignment-header">
                <h3>
                    Sequence View
                    {bsaISites.length > 0 && (
                        <span className="badge blocked" style={{ marginLeft: 8 }}>
                            {bsaISites.length} BsaI site{bsaISites.length > 1 ? 's' : ''}
                        </span>
                    )}
                </h3>
                <div className="alignment-controls">
                    <div className="view-toggle">
                        <button
                            className={viewMode === 'overview' ? 'active' : ''}
                            onClick={() => { setViewMode('overview'); setZoom(1); }}
                        >
                            Overview
                        </button>
                        <button
                            className={viewMode === 'sequence' ? 'active' : ''}
                            onClick={() => { setViewMode('sequence'); setZoom(1); }}
                        >
                            Sequence
                        </button>
                    </div>
                    <button onClick={zoomOut}>−</button>
                    <span className="zoom-label">{zoom.toFixed(1)}×</span>
                    <button onClick={zoomIn}>+</button>
                    <button onClick={resetZoom}>Reset</button>
                </div>
            </div>
            <div className="alignment-canvas-wrap" ref={wrapRef}>
                <canvas ref={canvasRef} />
            </div>
        </div>
    );
}
