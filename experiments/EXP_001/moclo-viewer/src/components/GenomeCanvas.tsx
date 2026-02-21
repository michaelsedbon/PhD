import { useRef, useEffect, useCallback, useState } from 'react';
import type { Tile, Lvl1Group } from '@/types';

const DARK_BG = '#0d1117';
const CARD_BG = '#161b22';
const GREEN = '#3fb950';
const YELLOW = '#d29922';
const ORANGE = '#db6d28';
const RED = '#f85149';
const ACCENT = '#58a6ff';
const DIM = '#30363d';
const TEXT_CLR = '#8b949e';

interface GenomeCanvasProps {
    tiles: Tile[];
    groups: Lvl1Group[];
    genomeLength: number;
    selectedTile: number | null;
    selectedGroup: number | null;
    onSelectTile: (id: number) => void;
    onSelectGroup: (id: number) => void;
}

function tileColor(tile: Tile): string {
    if (tile.gg_ready) return GREEN;
    if (tile.internal_bsai === 1) return YELLOW;
    if (tile.internal_bsai === 2) return ORANGE;
    return RED;
}

function groupColor(group: Lvl1Group): string {
    if (group.complete_before) return GREEN;
    if (group.blocked_tiles_count <= 2) return YELLOW;
    if (group.blocked_tiles_count <= 4) return ORANGE;
    return RED;
}

export function GenomeCanvas({
    tiles, groups, genomeLength,
    selectedTile, selectedGroup,
    onSelectTile, onSelectGroup,
}: GenomeCanvasProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [viewStart, setViewStart] = useState(0);
    const [viewEnd, setViewEnd] = useState(genomeLength);
    const [isDragging, setIsDragging] = useState(false);
    const [dragStartX, setDragStartX] = useState(0);
    const [dragViewStart, setDragViewStart] = useState(0);
    const [hoveredTile, setHoveredTile] = useState<number | null>(null);
    const [hoveredGroup, setHoveredGroup] = useState<number | null>(null);

    const viewRange = viewEnd - viewStart;

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);
        const W = rect.width;
        const H = rect.height;

        ctx.fillStyle = DARK_BG;
        ctx.fillRect(0, 0, W, H);

        const toX = (pos: number) => ((pos - viewStart) / viewRange) * W;

        // ── Track labels ──
        ctx.fillStyle = TEXT_CLR;
        ctx.font = '11px Inter, system-ui, sans-serif';
        ctx.textBaseline = 'middle';
        ctx.fillText('Lvl1 Groups', 4, 20);
        ctx.fillText('Lvl0 Tiles', 4, 58);

        // ── Lvl1 groups (top track) ──
        const groupY = 10;
        const groupH = 22;
        for (const g of groups) {
            const x1 = Math.max(0, toX(g.start));
            const x2 = Math.min(W, toX(g.end));
            if (x2 < 0 || x1 > W) continue;
            const w = Math.max(1, x2 - x1);

            // Fill
            const isHovered = hoveredGroup === g.id;
            const isSelected = selectedGroup === g.id;
            ctx.globalAlpha = isSelected ? 1.0 : isHovered ? 0.9 : 0.7;
            ctx.fillStyle = groupColor(g);
            ctx.fillRect(x1, groupY, w, groupH);

            // Border for selected
            if (isSelected) {
                ctx.strokeStyle = ACCENT;
                ctx.lineWidth = 2;
                ctx.strokeRect(x1, groupY, w, groupH);
            }

            // Label (if wide enough)
            if (w > 30) {
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 10px Inter, system-ui, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(`${g.id}`, x1 + w / 2, groupY + groupH / 2);
                ctx.textAlign = 'left';
            }
        }
        ctx.globalAlpha = 1;

        // ── Lvl0 tiles (bottom track) ──
        const tileY = 48;
        const tileH = 22;
        for (const t of tiles) {
            const x1 = Math.max(0, toX(t.start));
            const x2 = Math.min(W, toX(t.end));
            if (x2 < 0 || x1 > W) continue;
            const w = Math.max(1, x2 - x1);

            const isHovered = hoveredTile === t.id;
            const isSelected = selectedTile === t.id;
            ctx.globalAlpha = isSelected ? 1.0 : isHovered ? 0.9 : 0.65;
            ctx.fillStyle = tileColor(t);
            ctx.fillRect(x1, tileY, w, tileH);

            if (isSelected) {
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 2;
                ctx.strokeRect(x1, tileY, w, tileH);
            }

            // Tile ID label (if wide enough)
            if (w > 22) {
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#ffffff';
                ctx.font = '9px Inter, system-ui, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(`${t.id}`, x1 + w / 2, tileY + tileH / 2);
                ctx.textAlign = 'left';
            }
        }
        ctx.globalAlpha = 1;

        // ── Axis ──
        const axisY = 80;
        ctx.strokeStyle = DIM;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, axisY);
        ctx.lineTo(W, axisY);
        ctx.stroke();

        // Tick marks
        const tickInterval = viewRange > 3000000 ? 500000
            : viewRange > 1000000 ? 100000
                : viewRange > 500000 ? 50000
                    : viewRange > 100000 ? 10000
                        : viewRange > 50000 ? 5000
                            : 1000;

        ctx.fillStyle = TEXT_CLR;
        ctx.font = '10px Inter, system-ui, sans-serif';
        ctx.textAlign = 'center';
        const firstTick = Math.ceil(viewStart / tickInterval) * tickInterval;
        for (let pos = firstTick; pos <= viewEnd; pos += tickInterval) {
            const x = toX(pos);
            if (x < 30 || x > W - 30) continue;
            ctx.beginPath();
            ctx.moveTo(x, axisY);
            ctx.lineTo(x, axisY + 5);
            ctx.stroke();
            const label = pos >= 1000000 ? `${(pos / 1000000).toFixed(1)} Mb`
                : pos >= 1000 ? `${(pos / 1000).toFixed(0)} kb`
                    : `${pos}`;
            ctx.fillText(label, x, axisY + 15);
        }
        ctx.textAlign = 'left';

        // ── Mini-map (overview bar at bottom) ──
        if (viewRange < genomeLength * 0.95) {
            const mmY = H - 12;
            const mmH = 6;
            ctx.fillStyle = DIM;
            ctx.fillRect(0, mmY, W, mmH);
            const mmX1 = (viewStart / genomeLength) * W;
            const mmX2 = (viewEnd / genomeLength) * W;
            ctx.fillStyle = ACCENT;
            ctx.globalAlpha = 0.6;
            ctx.fillRect(mmX1, mmY, mmX2 - mmX1, mmH);
            ctx.globalAlpha = 1;
        }
    }, [tiles, groups, genomeLength, viewStart, viewEnd, selectedTile, selectedGroup, hoveredTile, hoveredGroup, viewRange]);

    useEffect(() => { draw(); }, [draw]);

    useEffect(() => {
        const handleResize = () => draw();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [draw]);

    // ── Mouse interactions ──
    const getGenomePos = (clientX: number) => {
        const canvas = canvasRef.current;
        if (!canvas) return 0;
        const rect = canvas.getBoundingClientRect();
        const x = clientX - rect.left;
        return viewStart + (x / rect.width) * viewRange;
    };

    const handleWheel = (e: React.WheelEvent) => {
        e.preventDefault();
        const pos = getGenomePos(e.clientX);
        const factor = e.deltaY > 0 ? 1.2 : 0.8;
        const newRange = Math.min(genomeLength, Math.max(5000, viewRange * factor));
        const ratio = (pos - viewStart) / viewRange;
        let newStart = pos - ratio * newRange;
        let newEnd = newStart + newRange;
        if (newStart < 0) { newStart = 0; newEnd = newRange; }
        if (newEnd > genomeLength) { newEnd = genomeLength; newStart = genomeLength - newRange; }
        setViewStart(Math.max(0, newStart));
        setViewEnd(Math.min(genomeLength, newEnd));
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        setDragStartX(e.clientX);
        setDragViewStart(viewStart);
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();

        if (isDragging) {
            const dx = e.clientX - dragStartX;
            const dPos = -(dx / rect.width) * viewRange;
            let newStart = dragViewStart + dPos;
            let newEnd = newStart + viewRange;
            if (newStart < 0) { newStart = 0; newEnd = viewRange; }
            if (newEnd > genomeLength) { newEnd = genomeLength; newStart = genomeLength - viewRange; }
            setViewStart(newStart);
            setViewEnd(newEnd);
        } else {
            // Hit-test
            const x = e.clientX - rect.left;
            const genomePos = viewStart + (x / rect.width) * viewRange;
            const y = e.clientY - rect.top;

            let foundTile: number | null = null;
            let foundGroup: number | null = null;

            if (y >= 10 && y <= 32) {
                for (const g of groups) {
                    if (genomePos >= g.start && genomePos <= g.end) {
                        foundGroup = g.id;
                        break;
                    }
                }
            } else if (y >= 48 && y <= 70) {
                for (const t of tiles) {
                    if (genomePos >= t.start && genomePos <= t.end) {
                        foundTile = t.id;
                        break;
                    }
                }
            }

            setHoveredTile(foundTile);
            setHoveredGroup(foundGroup);
            canvas.style.cursor = (foundTile !== null || foundGroup !== null) ? 'pointer' : isDragging ? 'grabbing' : 'grab';
        }
    };

    const handleMouseUp = (e: React.MouseEvent) => {
        if (isDragging && Math.abs(e.clientX - dragStartX) < 5) {
            // Click
            const canvas = canvasRef.current;
            if (canvas) {
                const rect = canvas.getBoundingClientRect();
                const y = e.clientY - rect.top;
                if (hoveredGroup !== null && y >= 10 && y <= 32) {
                    onSelectGroup(hoveredGroup);
                } else if (hoveredTile !== null && y >= 48 && y <= 70) {
                    onSelectTile(hoveredTile);
                }
            }
        }
        setIsDragging(false);
    };

    const handleDoubleClick = (e: React.MouseEvent) => {
        if (hoveredGroup !== null) {
            const group = groups.find(g => g.id === hoveredGroup);
            if (group) {
                const padding = group.length * 0.1;
                setViewStart(Math.max(0, group.start - padding));
                setViewEnd(Math.min(genomeLength, group.end + padding));
                onSelectGroup(hoveredGroup);
            }
        }
    };

    const zoomToGroup = useCallback((id: number) => {
        const group = groups.find(g => g.id === id);
        if (group) {
            const padding = group.length * 0.1;
            setViewStart(Math.max(0, group.start - padding));
            setViewEnd(Math.min(genomeLength, group.end + padding));
        }
    }, [groups, genomeLength]);

    // Expose zoom method through ref pattern
    useEffect(() => {
        if (selectedGroup !== null) {
            zoomToGroup(selectedGroup);
        }
    }, [selectedGroup, zoomToGroup]);

    return (
        <div ref={containerRef} className="relative w-full">
            <canvas
                ref={canvasRef}
                className="w-full rounded-md"
                style={{ height: 108, cursor: 'grab' }}
                onWheel={handleWheel}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={() => { setIsDragging(false); setHoveredTile(null); setHoveredGroup(null); }}
                onDoubleClick={handleDoubleClick}
            />
            <div className="absolute top-1 right-2 flex gap-1">
                <button
                    onClick={() => { setViewStart(0); setViewEnd(genomeLength); }}
                    className="text-[10px] text-zinc-400 hover:text-white bg-zinc-800/80 px-2 py-0.5 rounded"
                >
                    Reset
                </button>
            </div>
        </div>
    );
}
