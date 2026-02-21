import { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import type { Lvl1Group, Tile } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Mutation {
    o: string;  // original nucleotide
    m: string;  // mutant nucleotide
    c: string;  // codon change
    a: string;  // amino acid
    g: string;  // gene
}

interface AlignmentViewProps {
    group: Lvl1Group;
    tiles: Tile[];
    genomeSeq: string | null;
    mutations: Record<string, Mutation> | null;
}

const CHARS_PER_LINE = 80;
const LINES_VISIBLE = 12;

const NT_COLORS: Record<string, string> = {
    A: '#3fb950',
    T: '#f85149',
    C: '#58a6ff',
    G: '#d29922',
};

const MUT_BG = '#f8514930';
const MUT_BORDER = '#f85149';
const TILE_COLORS = [
    '#3fb95040', '#58a6ff40', '#bc8cff40', '#d2992240',
    '#3fb95040', '#58a6ff40', '#bc8cff40', '#d2992240',
    '#3fb95040', '#58a6ff40', '#bc8cff40', '#d2992240',
    '#3fb95040', '#58a6ff40', '#bc8cff40',
];
const TILE_BORDER_COLORS = [
    '#3fb95080', '#58a6ff80', '#bc8cff80', '#d2992280',
    '#3fb95080', '#58a6ff80', '#bc8cff80', '#d2992280',
    '#3fb95080', '#58a6ff80', '#bc8cff80', '#d2992280',
    '#3fb95080', '#58a6ff80', '#bc8cff80',
];

export function AlignmentView({ group, tiles, genomeSeq, mutations }: AlignmentViewProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [scrollLine, setScrollLine] = useState(0);
    const [jumpPos, setJumpPos] = useState('');

    const groupTiles = useMemo(() =>
        tiles.filter(t => t.lvl1_group === group.id).sort((a, b) => a.start - b.start),
        [tiles, group.id]
    );

    // Extract relevant sequence region
    const regionStart = group.start;
    const regionEnd = group.end;
    const regionLength = regionEnd - regionStart;

    const wtSeq = useMemo(() =>
        genomeSeq ? genomeSeq.slice(regionStart, regionEnd) : null,
        [genomeSeq, regionStart, regionEnd]
    );

    // Build assembled sequence (WT with mutations applied) — use Set for O(1) lookups
    const { assembledSeq, mutationPositions, mutationSet } = useMemo(() => {
        if (!wtSeq || !mutations) return { assembledSeq: null, mutationPositions: [] as number[], mutationSet: new Set<number>() };

        const chars = wtSeq.split('');
        const positions: number[] = [];
        const posSet = new Set<number>();

        for (const [posStr, mut] of Object.entries(mutations)) {
            const genomePos = parseInt(posStr);
            if (genomePos >= regionStart && genomePos < regionEnd) {
                const localPos = genomePos - regionStart;
                chars[localPos] = mut.m;
                positions.push(localPos);
                posSet.add(localPos);
            }
        }

        return { assembledSeq: chars.join(''), mutationPositions: positions, mutationSet: posSet };
    }, [wtSeq, mutations, regionStart, regionEnd]);

    // Tile boundaries in local coordinates — sorted for binary search
    const tileBoundaries = useMemo(() =>
        groupTiles.map(t => ({
            id: t.id,
            localStart: t.start - regionStart,
            localEnd: t.end - regionStart,
            overhangLeft: t.overhang_left,
            overhangRight: t.overhang_right,
        })),
        [groupTiles, regionStart]
    );

    // O(1) tile lookup — pre-built tile boundary start set
    const tileBoundaryStartSet = useMemo(() => {
        const s = new Set<number>();
        for (const tb of tileBoundaries) s.add(tb.localStart);
        return s;
    }, [tileBoundaries]);

    // Binary search for tile index
    const getTileIndex = useCallback((localPos: number): number => {
        let lo = 0, hi = tileBoundaries.length - 1;
        while (lo <= hi) {
            const mid = (lo + hi) >> 1;
            const tb = tileBoundaries[mid];
            if (localPos < tb.localStart) hi = mid - 1;
            else if (localPos >= tb.localEnd) lo = mid + 1;
            else return mid;
        }
        return -1;
    }, [tileBoundaries]);

    const totalLines = Math.ceil(regionLength / CHARS_PER_LINE);
    const maxScroll = Math.max(0, totalLines - LINES_VISIBLE);

    // Find mutations in current view for quick navigation
    const mutationLines = useMemo(() =>
        mutationPositions.map(pos => Math.floor(pos / CHARS_PER_LINE)),
        [mutationPositions]
    );

    const handleWheel = useCallback((e: WheelEvent) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 3 : -3;
        setScrollLine(prev => Math.max(0, Math.min(maxScroll, prev + delta)));
    }, [maxScroll]);

    // Attach wheel listener with passive: false to prevent page scroll
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        canvas.addEventListener('wheel', handleWheel, { passive: false });
        return () => canvas.removeEventListener('wheel', handleWheel);
    }, [handleWheel]);

    const jumpToMutation = useCallback((index: number) => {
        if (mutationLines[index] !== undefined) {
            setScrollLine(Math.max(0, Math.min(maxScroll, mutationLines[index] - 2)));
        }
    }, [mutationLines, maxScroll]);

    const handleJump = useCallback(() => {
        const pos = parseInt(jumpPos);
        if (!isNaN(pos)) {
            const localPos = pos - regionStart;
            if (localPos >= 0 && localPos < regionLength) {
                setScrollLine(Math.max(0, Math.min(maxScroll, Math.floor(localPos / CHARS_PER_LINE) - 2)));
            }
        }
    }, [jumpPos, regionStart, regionLength, maxScroll]);

    const getMutationAt = useCallback((localPos: number): Mutation | null => {
        const genomePos = localPos + regionStart;
        return mutations?.[String(genomePos)] || null;
    }, [mutations, regionStart]);

    // ── Canvas-based rendering ──
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || !wtSeq || !assembledSeq) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        const CHAR_W = 9.6;
        const LABEL_W = 100; // position label + track label
        const LINE_H = 52; // height per alignment line block
        const TILE_TRACK_H = 12;

        const canvasW = LABEL_W + CHARS_PER_LINE * CHAR_W + 60;
        const linesToRender = Math.min(LINES_VISIBLE, totalLines - scrollLine);
        const canvasH = linesToRender * LINE_H + 30; // +30 for legend

        canvas.width = canvasW * dpr;
        canvas.height = canvasH * dpr;
        canvas.style.width = `${canvasW}px`;
        canvas.style.height = `${canvasH}px`;
        ctx.scale(dpr, dpr);

        // Clear
        ctx.fillStyle = '#09090b';
        ctx.fillRect(0, 0, canvasW, canvasH);

        // Legend bar
        ctx.fillStyle = '#27272a';
        ctx.fillRect(0, 0, canvasW, 22);
        ctx.font = '9px Inter, system-ui, sans-serif';
        let lx = 8;
        for (const [nt, color] of Object.entries(NT_COLORS)) {
            ctx.fillStyle = color;
            ctx.fillText(nt, lx, 14);
            lx += 14;
        }
        lx += 8;
        ctx.fillStyle = MUT_BORDER;
        ctx.fillText('▼ mutation', lx, 14);
        lx += 70;
        ctx.fillStyle = '#52525b';
        ctx.fillText('· match', lx, 14);
        ctx.fillStyle = '#52525b';
        ctx.textAlign = 'right';
        ctx.fillText('scroll to navigate', canvasW - 8, 14);
        ctx.textAlign = 'left';

        const baseY = 26;

        for (let li = 0; li < linesToRender; li++) {
            const lineIndex = scrollLine + li;
            const lineStart = lineIndex * CHARS_PER_LINE;
            const lineEnd = Math.min(lineStart + CHARS_PER_LINE, regionLength);
            const genomeStart = regionStart + lineStart;
            const y = baseY + li * LINE_H;

            // Position label
            ctx.fillStyle = '#52525b';
            ctx.font = '10px "JetBrains Mono", monospace';
            ctx.textAlign = 'right';
            ctx.fillText((genomeStart + 1).toLocaleString(), LABEL_W - 30, y + TILE_TRACK_H + 12);
            ctx.textAlign = 'left';

            // Draw each character across the line
            for (let i = lineStart; i < lineEnd; i++) {
                const charIdx = i - lineStart;
                const cx = LABEL_W + charIdx * CHAR_W;
                const wtNt = wtSeq[i];
                const asmNt = assembledSeq[i];
                const isMut = mutationSet.has(i);
                const tileIdx = getTileIndex(i);
                const isTileStart = tileBoundaryStartSet.has(i);

                // ── Tile track ──
                if (tileIdx >= 0) {
                    ctx.fillStyle = TILE_COLORS[tileIdx % TILE_COLORS.length];
                    ctx.fillRect(cx, y, CHAR_W, TILE_TRACK_H);
                    if (isTileStart) {
                        ctx.fillStyle = TILE_BORDER_COLORS[tileIdx % TILE_BORDER_COLORS.length];
                        ctx.fillRect(cx, y, 1, TILE_TRACK_H);
                    }
                }

                // ── WT track ──
                const wtY = y + TILE_TRACK_H + 2;
                if (isMut) {
                    ctx.fillStyle = 'rgba(248, 81, 73, 0.19)';
                    ctx.fillRect(cx, wtY, CHAR_W, 12);
                }
                ctx.fillStyle = NT_COLORS[wtNt] || '#8b949e';
                ctx.font = '11px "JetBrains Mono", monospace';
                ctx.fillText(wtNt, cx + 2, wtY + 10);

                // ── Match track ──
                const matchY = wtY + 12;
                if (isMut) {
                    ctx.fillStyle = MUT_BORDER;
                    ctx.font = '9px "JetBrains Mono", monospace';
                    ctx.fillText('▼', cx + 1, matchY + 8);
                } else {
                    ctx.fillStyle = '#30363d';
                    ctx.font = '9px "JetBrains Mono", monospace';
                    ctx.fillText('·', cx + 3, matchY + 8);
                }

                // ── Assembled track ──
                const asmY = matchY + 10;
                if (isMut) {
                    ctx.fillStyle = 'rgba(248, 81, 73, 0.38)';
                    ctx.fillRect(cx, asmY, CHAR_W, 12);
                    ctx.fillStyle = '#ffffff';
                } else {
                    ctx.fillStyle = NT_COLORS[asmNt] || '#8b949e';
                }
                ctx.font = 'bold 11px "JetBrains Mono", monospace';
                ctx.fillText(asmNt, cx + 2, asmY + 10);
            }

            // Track labels
            ctx.font = '9px Inter, system-ui, sans-serif';
            const trackLabelX = LABEL_W - 25;
            ctx.fillStyle = '#52525b';
            ctx.textAlign = 'right';
            ctx.fillText('WT', trackLabelX, y + TILE_TRACK_H + 12);
            ctx.fillStyle = '#059669';
            ctx.fillText('Lvl1', trackLabelX, y + TILE_TRACK_H + 34);
            ctx.textAlign = 'left';

            // Tile boundary label
            const tileBoundaryHere = tileBoundaries.find(tb => {
                const tbLineStart = Math.floor(tb.localStart / CHARS_PER_LINE);
                return tbLineStart === lineIndex;
            });
            if (tileBoundaryHere) {
                const tbCharIdx = tileBoundaryHere.localStart - lineStart;
                const tbX = LABEL_W + tbCharIdx * CHAR_W;
                ctx.fillStyle = '#71717a';
                ctx.font = '9px Inter, system-ui, sans-serif';
                ctx.fillText(`T${tileBoundaryHere.id}`, tbX, y - 1);
            }
        }
    }, [wtSeq, assembledSeq, scrollLine, totalLines, regionStart, regionLength, mutationSet, getTileIndex, tileBoundaryStartSet, tileBoundaries]);

    if (!wtSeq || !assembledSeq) {
        return (
            <Card className="border-zinc-800 bg-zinc-900/50">
                <CardContent className="py-8 text-center text-zinc-500 text-sm">
                    Loading genome sequence…
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-3 text-sm">
                    <span className="text-zinc-100">Sequence Alignment</span>
                    <Badge variant="outline" className="text-[10px] border-zinc-600 text-zinc-400">
                        {regionLength.toLocaleString()} bp
                    </Badge>
                    {mutationPositions.length > 0 && (
                        <Badge variant="outline" className="text-[10px]" style={{ borderColor: MUT_BORDER, color: MUT_BORDER }}>
                            {mutationPositions.length} mutation{mutationPositions.length !== 1 ? 's' : ''}
                        </Badge>
                    )}
                    <div className="ml-auto flex items-center gap-2">
                        <input
                            type="text"
                            placeholder="Jump to position…"
                            className="text-[10px] bg-zinc-800 border border-zinc-700 rounded px-2 py-0.5 w-32 text-zinc-300 placeholder:text-zinc-600"
                            value={jumpPos}
                            onChange={e => setJumpPos(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleJump()}
                        />
                    </div>
                </CardTitle>

                {/* Mutation quick nav */}
                {mutationPositions.length > 0 && (
                    <div className="flex items-center gap-1 flex-wrap mt-1">
                        <span className="text-[9px] text-zinc-600 uppercase tracking-wider mr-1">Mutations:</span>
                        {mutationPositions.map((pos, i) => {
                            const mut = getMutationAt(pos)!;
                            const genPos = pos + regionStart;
                            return (
                                <button
                                    key={i}
                                    onClick={() => jumpToMutation(i)}
                                    className="text-[9px] font-mono px-1.5 py-0.5 rounded transition-colors hover:bg-red-500/20"
                                    style={{ color: MUT_BORDER, border: `1px solid ${MUT_BORDER}30` }}
                                    title={`${mut.o}→${mut.m} at ${genPos} (${mut.c}, ${mut.g})`}
                                >
                                    {genPos.toLocaleString()} {mut.g}
                                </button>
                            );
                        })}
                    </div>
                )}
            </CardHeader>

            <CardContent className="pt-0">
                {/* Scrollbar indicator */}
                <div className="flex items-center gap-2 mb-2">
                    <div className="flex-1 h-1.5 bg-zinc-800 rounded-full relative">
                        <div
                            className="absolute top-0 h-1.5 bg-zinc-600 rounded-full"
                            style={{
                                left: `${(scrollLine / Math.max(1, totalLines)) * 100}%`,
                                width: `${Math.max(2, (LINES_VISIBLE / totalLines) * 100)}%`,
                            }}
                        />
                        {/* Mutation markers on scrollbar */}
                        {mutationPositions.map((pos, i) => (
                            <div
                                key={i}
                                className="absolute top-0 w-0.5 h-1.5 rounded-full"
                                style={{
                                    left: `${(pos / regionLength) * 100}%`,
                                    background: MUT_BORDER,
                                }}
                            />
                        ))}
                    </div>
                    <span className="text-[9px] text-zinc-600 font-mono w-20 text-right">
                        {(regionStart + scrollLine * CHARS_PER_LINE + 1).toLocaleString()}–{Math.min(regionEnd, regionStart + (scrollLine + LINES_VISIBLE) * CHARS_PER_LINE).toLocaleString()}
                    </span>
                </div>

                {/* Canvas-based sequence view */}
                <div className="overflow-hidden rounded border border-zinc-800 bg-zinc-950/70">
                    <canvas
                        ref={canvasRef}
                        style={{ display: 'block' }}
                    />
                </div>
            </CardContent>
        </Card>
    );
}
