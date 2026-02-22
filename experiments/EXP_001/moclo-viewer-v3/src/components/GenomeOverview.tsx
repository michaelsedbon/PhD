import { useRef, useEffect, useMemo } from 'react';
import { AppData, ViewState } from '../types';

interface Props {
    data: AppData;
    onNavigate: (v: ViewState) => void;
}

const TRACK_H = 20;
const GAP = 4;
const CDS_ROW_H = 14;
const MUT_ROW_H = 10;
const GROUP_LABEL_H = 16;
const PADDING = 16;

export default function GenomeOverview({ data, onNavigate }: Props) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wrapRef = useRef<HTMLDivElement>(null);
    const { bundle, cdsRegions, mutations } = data;
    const genomeLen = bundle.genome.length;

    // Precompute tile lookup by pixel
    const tileRanges = useMemo(() => {
        return bundle.tiles.map(t => ({
            id: t.id,
            start: t.start,
            end: t.end,
            groupId: t.lvl1_group,
            ready: t.gg_ready,
        }));
    }, [bundle.tiles]);

    useEffect(() => {
        const canvas = canvasRef.current;
        const wrap = wrapRef.current;
        if (!canvas || !wrap) return;

        const dpr = window.devicePixelRatio || 1;
        const w = wrap.clientWidth - PADDING * 2;
        const totalH = GROUP_LABEL_H + TRACK_H + GAP + CDS_ROW_H + GAP + MUT_ROW_H + GAP * 2;

        canvas.width = w * dpr;
        canvas.height = totalH * dpr;
        canvas.style.width = `${w}px`;
        canvas.style.height = `${totalH}px`;

        const ctx = canvas.getContext('2d')!;
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, w, totalH);

        const x = (pos: number) => (pos / genomeLen) * w;

        // ── Lvl1 group boundary labels ──
        let y = 0;
        ctx.font = '9px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        for (const g of bundle.lvl1_groups) {
            const gx = x(g.start);
            const gw = Math.max(x(g.end) - gx, 1);
            if (gw > 20) {
                ctx.fillStyle = g.id % 2 === 0 ? 'rgba(88,166,255,0.08)' : 'rgba(188,140,255,0.06)';
                ctx.fillRect(gx, y, gw, GROUP_LABEL_H);
                ctx.fillStyle = '#6e7681';
                ctx.fillText(`${g.id}`, gx + gw / 2, y + GROUP_LABEL_H / 2);
            }
        }

        // ── Tile track ──
        y = GROUP_LABEL_H;
        for (const t of bundle.tiles) {
            const tx = x(t.start);
            const tw = Math.max(x(t.end) - tx, 1);
            ctx.fillStyle = t.gg_ready
                ? 'rgba(63,185,80,0.6)'
                : 'rgba(248,81,73,0.6)';
            ctx.fillRect(tx, y, tw - 0.5, TRACK_H);
        }

        // ── CDS track ──
        y += TRACK_H + GAP;
        for (const cds of cdsRegions) {
            const cx = x(cds.start);
            const cw = Math.max(x(cds.end) - cx, 0.5);
            ctx.fillStyle = cds.complement
                ? 'rgba(188,140,255,0.35)'
                : 'rgba(57,210,192,0.35)';
            ctx.fillRect(cx, y, cw, CDS_ROW_H);
        }

        // ── Mutations track ──
        y += CDS_ROW_H + GAP;
        ctx.fillStyle = 'rgba(210,153,34,0.7)';
        for (const [pos] of mutations) {
            const mx = x(pos);
            ctx.fillRect(mx, y, 1.5, MUT_ROW_H);
        }

    }, [bundle, cdsRegions, mutations, genomeLen]);

    // Click handler
    const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();
        const px = e.clientX - rect.left;
        const w = rect.width;
        const genomePos = (px / w) * genomeLen;

        // Find tile at this position
        const tile = tileRanges.find(t => genomePos >= t.start && genomePos < t.end);
        if (tile) {
            onNavigate({ view: 'group', groupId: tile.groupId });
        }
    };

    return (
        <div className="genome-overview">
            <div className="genome-canvas-wrapper">
                <h3>Genome Map — {bundle.tiles.length} tiles across {bundle.lvl1_groups.length} Lvl1 groups</h3>
                <div ref={wrapRef} style={{ padding: `0 ${PADDING}px` }}>
                    <canvas
                        ref={canvasRef}
                        onClick={handleClick}
                        style={{ cursor: 'pointer' }}
                    />
                </div>
                <div className="genome-legend">
                    <div className="legend-item">
                        <div className="legend-dot" style={{ background: 'rgba(63,185,80,0.6)' }} />
                        GG-Ready tile
                    </div>
                    <div className="legend-item">
                        <div className="legend-dot" style={{ background: 'rgba(248,81,73,0.6)' }} />
                        Blocked tile (BsaI)
                    </div>
                    <div className="legend-item">
                        <div className="legend-dot" style={{ background: 'rgba(57,210,192,0.35)' }} />
                        CDS (+)
                    </div>
                    <div className="legend-item">
                        <div className="legend-dot" style={{ background: 'rgba(188,140,255,0.35)' }} />
                        CDS (−)
                    </div>
                    <div className="legend-item">
                        <div className="legend-dot" style={{ background: 'rgba(210,153,34,0.7)', width: 3 }} />
                        Mutation
                    </div>
                </div>
            </div>

            {/* Summary stats cards */}
            <div className="group-info-cards">
                <div className="info-card">
                    <div className="value">{bundle.stats.total_tiles}</div>
                    <div className="label">Total Tiles</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--green)' }}>{bundle.stats.ready_tiles}</div>
                    <div className="label">GG-Ready</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--red)' }}>{bundle.stats.blocked_tiles}</div>
                    <div className="label">Need Domestication</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--blue)' }}>{bundle.stats.total_lvl1_groups}</div>
                    <div className="label">Lvl1 Groups</div>
                </div>
                <div className="info-card">
                    <div className="value">{bundle.stats.total_primers.toLocaleString()}</div>
                    <div className="label">Total Oligos</div>
                </div>
                <div className="info-card">
                    <div className="value">{bundle.stats.total_pcr_reactions.toLocaleString()}</div>
                    <div className="label">PCR Reactions</div>
                </div>
                <div className="info-card">
                    <div className="value">{bundle.design.tiles_per_group}</div>
                    <div className="label">Tiles / Group</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--purple)' }}>{bundle.design.overhang_type}</div>
                    <div className="label">Overhang Type</div>
                </div>
            </div>

            {/* Overhang table */}
            <div className="genome-canvas-wrapper">
                <h3>Standardized Overhang Set ({bundle.design.standard_overhangs.length} overhangs)</h3>
                <div className="tiles-grid" style={{ gap: 6, justifyContent: 'flex-start' }}>
                    {bundle.design.standard_overhangs.map((oh, i) => (
                        <div key={i} className="tile-block ready" style={{ minWidth: 60, flex: 'none', padding: '8px 12px' }}>
                            <div className="tile-pos">Pos {i}</div>
                            <div className="tile-id" style={{ fontFamily: 'var(--font-mono)', letterSpacing: 2 }}>{oh}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
