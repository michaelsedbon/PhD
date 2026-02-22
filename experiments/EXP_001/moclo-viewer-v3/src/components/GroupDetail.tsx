import { useMemo, useState, useRef, useEffect, useCallback } from 'react';
import { AppData, ViewState, CDSRegion, Mutation } from '../types';

interface Props {
    data: AppData;
    groupId: number;
    onNavigate: (v: ViewState) => void;
}

const NT_COLORS: Record<string, string> = {
    A: '#3fb950', T: '#f85149', G: '#d29922', C: '#58a6ff',
};

export default function GroupDetail({ data, groupId, onNavigate }: Props) {
    const group = data.bundle.lvl1_groups[groupId];
    const tiles = data.tilesByGroup.get(groupId) || [];
    const pct = Math.round((group.ready_tiles / group.total_tiles) * 100);
    const [showDomesticated, setShowDomesticated] = useState(false);

    // Mutations in this group's region
    const groupMutations = useMemo(() => {
        const muts: Mutation[] = [];
        for (const [pos, m] of data.mutations) {
            if (pos >= group.start && pos < group.end) {
                muts.push(m);
            }
        }
        return muts.sort((a, b) => a.position - b.position);
    }, [data.mutations, group]);

    // CDS regions overlapping this group
    const groupCDS = useMemo(() => {
        return data.cdsRegions
            .filter(c => c.end > group.start && c.start < group.end)
            .sort((a, b) => a.start - b.start);
    }, [data.cdsRegions, group]);

    // Unique genes
    const genes = useMemo(() => {
        const seen = new Map<string, CDSRegion>();
        for (const cds of groupCDS) {
            if (cds.gene && !seen.has(cds.gene)) {
                seen.set(cds.gene, cds);
            }
        }
        return Array.from(seen.values());
    }, [groupCDS]);

    // Genome-wide context info
    const genomeLen = data.bundle.genome.length;
    const groupPctOfGenome = ((group.length / genomeLen) * 100).toFixed(2);
    const groupStartPct = (group.start / genomeLen) * 100;

    return (
        <div className="group-detail">
            {/* Info cards */}
            <div className="group-info-cards">
                <div className="info-card">
                    <div className="value">{(group.length / 1000).toFixed(1)} kb</div>
                    <div className="label">Length</div>
                </div>
                <div className="info-card">
                    <div className="value">{group.total_tiles}</div>
                    <div className="label">Total Tiles</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--green)' }}>{group.ready_tiles}</div>
                    <div className="label">GG-Ready</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: group.blocked_tiles_count > 0 ? 'var(--red)' : 'var(--green)' }}>
                        {group.blocked_tiles_count}
                    </div>
                    <div className="label">Blocked</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: pct >= 70 ? 'var(--green)' : 'var(--orange)' }}>
                        {pct}%
                    </div>
                    <div className="label">Readiness</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--orange)' }}>{groupMutations.length}</div>
                    <div className="label">Mutations</div>
                </div>
                <div className="info-card">
                    <div className="value" style={{ color: 'var(--purple)' }}>{genes.length}</div>
                    <div className="label">Genes</div>
                </div>
                <div className="info-card">
                    <div className="value mono" style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                        {group.start.toLocaleString()} – {group.end.toLocaleString()}
                    </div>
                    <div className="label">Genomic Range</div>
                </div>
            </div>

            {/* Genome context strip */}
            <div className="genome-context-section">
                <h3>Position on Genome — {groupPctOfGenome}% of total ({(genomeLen / 1e6).toFixed(2)} Mb)</h3>
                <div className="genome-context-bar">
                    <div className="context-track">
                        {/* All other groups dimmed */}
                        {data.bundle.lvl1_groups.map(g => (
                            <div
                                key={g.id}
                                className={`ctx-group ${g.id === groupId ? 'current' : ''}`}
                                style={{
                                    left: `${(g.start / genomeLen) * 100}%`,
                                    width: `${Math.max((g.length / genomeLen) * 100, 0.3)}%`,
                                }}
                                title={`G${g.id}: ${g.start.toLocaleString()} – ${g.end.toLocaleString()}`}
                                onClick={() => { if (g.id !== groupId) onNavigate({ view: 'group', groupId: g.id }); }}
                            />
                        ))}
                    </div>
                    <div className="context-marker" style={{ left: `${groupStartPct}%`, width: `${Math.max(parseFloat(groupPctOfGenome), 0.5)}%` }} />
                </div>
                <div className="context-labels">
                    <span>0</span>
                    <span>{group.start.toLocaleString()}</span>
                    <span>{group.end.toLocaleString()}</span>
                    <span>{genomeLen.toLocaleString()}</span>
                </div>
            </div>

            {/* Genes in this group */}
            {genes.length > 0 && (
                <div className="genes-section">
                    <h3>Genes in This Group ({genes.length})</h3>
                    <div className="gene-list">
                        {genes.map((cds, i) => {
                            const geneStart = Math.max(cds.start, group.start);
                            const geneEnd = Math.min(cds.end, group.end);
                            const geneMuts = groupMutations.filter(m => m.position >= cds.start && m.position < cds.end);
                            return (
                                <div key={i} className="gene-card">
                                    <div className="gene-header">
                                        <span className="gene-name-big">{cds.gene}</span>
                                        <span className={`badge ${cds.complement ? 'info' : 'ready'}`}>
                                            {cds.complement ? '(−) strand' : '(+) strand'}
                                        </span>
                                    </div>
                                    <div className="gene-meta">
                                        <span>{geneStart.toLocaleString()} – {geneEnd.toLocaleString()}</span>
                                        <span>{((geneEnd - geneStart) / 1000).toFixed(1)} kb</span>
                                        {geneMuts.length > 0 && (
                                            <span className="badge mutation">{geneMuts.length} mutation{geneMuts.length > 1 ? 's' : ''}</span>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Tile layout grid */}
            <div className="genome-canvas-wrapper">
                <h3>Tile Layout</h3>
                <div className="tiles-grid">
                    {tiles.map(t => (
                        <div
                            key={t.id}
                            className={`tile-block ${t.gg_ready ? 'ready' : 'blocked'}`}
                            onClick={() => onNavigate({ view: 'tile', tileId: t.id })}
                        >
                            <div className="tile-pos">P{t.position}</div>
                            <div className="tile-id">T{t.id}</div>
                            <div className="tile-oh">
                                <span className="badge overhang">{t.overhang_left}</span>
                                {' → '}
                                <span className="badge overhang">{t.overhang_right}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Tile detail table */}
            <div className="tile-table-wrapper">
                <table className="tile-table">
                    <thead>
                        <tr>
                            <th>Tile</th>
                            <th>Position</th>
                            <th>Overhangs</th>
                            <th>Length</th>
                            <th>GC%</th>
                            <th>BsaI Sites</th>
                            <th>Status</th>
                            <th>Boundary</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tiles.map(t => (
                            <tr key={t.id} onClick={() => onNavigate({ view: 'tile', tileId: t.id })}>
                                <td><strong>T{t.id}</strong></td>
                                <td>P{t.position}</td>
                                <td className="mono">{t.overhang_left} / {t.overhang_right}</td>
                                <td className="mono">{(t.length / 1000).toFixed(1)} kb</td>
                                <td className="mono">{t.gc_content.toFixed(1)}%</td>
                                <td style={{ color: t.internal_bsai > 0 ? 'var(--red)' : 'var(--text-muted)' }}>
                                    {t.internal_bsai}
                                </td>
                                <td>
                                    <span className={`badge ${t.gg_ready ? 'ready' : 'blocked'}`}>
                                        {t.gg_ready ? 'Ready' : 'Blocked'}
                                    </span>
                                </td>
                                <td style={{ fontSize: 11, color: 'var(--text-muted)' }}>{t.boundary_type}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Group alignment canvas — genome annotation with mutations */}
            <GroupAlignmentCanvas
                data={data}
                group={group}
                groupCDS={groupCDS}
                groupMutations={groupMutations}
                showDomesticated={showDomesticated}
                onToggleDomesticated={() => setShowDomesticated(v => !v)}
            />

            {/* Mutations detail list with toggle */}
            {groupMutations.length > 0 && (
                <div className="domestication-section">
                    <div className="dom-header-row">
                        <h3>
                            <span className="badge mutation">{groupMutations.length} mutations</span>
                            {' '}BsaI domestication sites
                        </h3>
                        <label className="dom-toggle">
                            <input
                                type="checkbox"
                                checked={showDomesticated}
                                onChange={() => setShowDomesticated(v => !v)}
                            />
                            <span className="toggle-slider" />
                            <span className="toggle-label">Show domesticated</span>
                        </label>
                    </div>
                    <div className="mutation-list">
                        {groupMutations.map((m, i) => (
                            <div key={i} className="mutation-item rich">
                                <span className="pos">{m.position.toLocaleString()}</span>
                                <span className="gene-name">{m.gene}</span>
                                <span className="change">
                                    {showDomesticated ? (
                                        <>
                                            <span className="nt-old">{m.original}</span>
                                            <span className="arrow">→</span>
                                            <span className="nt-new">{m.mutant}</span>
                                        </>
                                    ) : (
                                        <span className="nt-old">{m.original}</span>
                                    )}
                                </span>
                                <span className="codon">{m.codon_change}</span>
                                <span className="amino">{m.amino_acid} (silent)</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

/* ── Group-level alignment canvas ──────────────────────────────────── */

interface AlignProps {
    data: AppData;
    group: { id: number; start: number; end: number; length: number };
    groupCDS: CDSRegion[];
    groupMutations: Mutation[];
    showDomesticated: boolean;
    onToggleDomesticated: () => void;
}

function GroupAlignmentCanvas({ data, group, groupCDS, groupMutations, showDomesticated, onToggleDomesticated }: AlignProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wrapRef = useRef<HTMLDivElement>(null);
    const [zoom, setZoom] = useState(1);

    const groupSeq = useMemo(() => {
        return data.genomeSeq.substring(group.start, group.end).toUpperCase();
    }, [data.genomeSeq, group.start, group.end]);

    const mutPositions = useMemo(() => {
        return new Set(groupMutations.map(m => m.position));
    }, [groupMutations]);

    const mutMap = useMemo(() => {
        const m = new Map<number, Mutation>();
        for (const mut of groupMutations) {
            m.set(mut.position, mut);
        }
        return m;
    }, [groupMutations]);

    // Find all BsaI sites in wildtype sequence
    const bsaISites = useMemo(() => {
        const sites: number[] = [];
        const fwd = 'GGTCTC';
        const rev = 'GAGACC';
        for (let i = 0; i <= groupSeq.length - 6; i++) {
            const sub = groupSeq.substring(i, i + 6);
            if (sub === fwd || sub === rev) {
                sites.push(group.start + i);
            }
        }
        return sites;
    }, [groupSeq, group.start]);

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        const wrap = wrapRef.current;
        if (!canvas || !wrap) return;

        const dpr = window.devicePixelRatio || 1;
        const containerW = wrap.clientWidth;
        const bpPerPx = Math.max(1, Math.floor(groupSeq.length / (containerW * zoom)));
        const canvasW = Math.ceil(groupSeq.length / bpPerPx);

        // Track heights
        const scaleH = 16;     // position scale
        const gcH = 24;        // GC heatmap
        const cdsH = 20;       // CDS track
        const bsaiH = 12;      // BsaI sites
        const mutH = 14;       // mutation markers
        const padding = 4;
        const totalH = scaleH + gcH + padding + cdsH + padding + bsaiH + padding + mutH;

        canvas.width = canvasW * dpr;
        canvas.height = totalH * dpr;
        canvas.style.width = `${canvasW}px`;
        canvas.style.height = `${totalH}px`;

        const ctx = canvas.getContext('2d')!;
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, canvasW, totalH);

        // Track 1: Position scale
        let y = 0;
        ctx.fillStyle = '#30363d';
        ctx.fillRect(0, y, canvasW, scaleH);
        ctx.fillStyle = '#6e7681';
        ctx.font = '9px Inter, sans-serif';
        ctx.textBaseline = 'middle';
        ctx.textAlign = 'center';
        const tickInterval = Math.max(1000, Math.ceil(groupSeq.length / 20 / 1000) * 1000);
        for (let pos = Math.ceil(group.start / tickInterval) * tickInterval; pos < group.end; pos += tickInterval) {
            const px = Math.floor((pos - group.start) / bpPerPx);
            ctx.fillStyle = '#484f58';
            ctx.fillRect(px, y, 1, scaleH);
            ctx.fillStyle = '#8b949e';
            ctx.fillText(`${(pos / 1000).toFixed(0)}k`, px, y + scaleH / 2);
        }

        // Track 2: GC content heatmap
        y = scaleH;
        for (let i = 0; i < groupSeq.length; i += bpPerPx) {
            const chunk = groupSeq.substring(i, Math.min(i + bpPerPx, groupSeq.length));
            const gc = (chunk.split('').filter(c => c === 'G' || c === 'C').length) / chunk.length;
            const px = Math.floor(i / bpPerPx);
            const r = Math.round(210 * (1 - gc) + 88 * gc);
            const g = Math.round(153 * (1 - gc) + 166 * gc);
            const b = Math.round(34 * (1 - gc) + 255 * gc);
            ctx.fillStyle = `rgb(${r},${g},${b})`;
            ctx.fillRect(px, y, 1, gcH);
        }

        // Track 3: CDS regions
        y = scaleH + gcH + padding;
        ctx.fillStyle = '#21262d';
        ctx.fillRect(0, y, canvasW, cdsH);
        for (const cds of groupCDS) {
            const cx = Math.max(0, Math.floor((cds.start - group.start) / bpPerPx));
            const cw = Math.max(1, Math.ceil((Math.min(cds.end, group.end) - Math.max(cds.start, group.start)) / bpPerPx));
            ctx.fillStyle = cds.complement
                ? 'rgba(188,140,255,0.5)'
                : 'rgba(57,210,192,0.5)';
            ctx.fillRect(cx, y, cw, cdsH);

            // Gene label if wide enough
            if (cw > 30) {
                ctx.fillStyle = '#e6edf3';
                ctx.font = '8px Inter, sans-serif';
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';
                const labelX = Math.max(cx + 3, 0);
                ctx.save();
                ctx.beginPath();
                ctx.rect(cx, y, cw, cdsH);
                ctx.clip();
                ctx.fillText(cds.gene, labelX, y + cdsH / 2);
                ctx.restore();
            }
        }

        // Track 4: BsaI sites
        y = scaleH + gcH + padding + cdsH + padding;
        ctx.fillStyle = '#161b22';
        ctx.fillRect(0, y, canvasW, bsaiH);
        ctx.fillStyle = 'rgba(248,81,73,0.9)';
        for (const sitePos of bsaISites) {
            const px = Math.floor((sitePos - group.start) / bpPerPx);
            ctx.fillRect(px - 1, y + 1, 3, bsaiH - 2);
        }

        // Track 5: Mutation markers
        y = scaleH + gcH + padding + cdsH + padding + bsaiH + padding;
        ctx.fillStyle = '#161b22';
        ctx.fillRect(0, y, canvasW, mutH);
        for (const mPos of mutPositions) {
            const px = Math.floor((mPos - group.start) / bpPerPx);
            if (showDomesticated) {
                // Show green dot for domesticated
                ctx.fillStyle = 'rgba(63,185,80,0.9)';
                ctx.beginPath();
                ctx.arc(px, y + mutH / 2, 3, 0, Math.PI * 2);
                ctx.fill();
            } else {
                // Show orange triangle for wildtype
                ctx.fillStyle = 'rgba(210,153,34,0.9)';
                ctx.beginPath();
                ctx.moveTo(px, y + 2);
                ctx.lineTo(px + 3, y + mutH - 2);
                ctx.lineTo(px - 3, y + mutH - 2);
                ctx.closePath();
                ctx.fill();
            }
        }
    }, [groupSeq, group, groupCDS, bsaISites, mutPositions, zoom, showDomesticated]);

    useEffect(() => { draw(); }, [draw]);
    useEffect(() => {
        const handler = () => draw();
        window.addEventListener('resize', handler);
        return () => window.removeEventListener('resize', handler);
    }, [draw]);

    return (
        <div className="alignment-section">
            <div className="alignment-header">
                <h3>
                    Group Alignment
                    {bsaISites.length > 0 && (
                        <span className="badge blocked" style={{ marginLeft: 8 }}>
                            {bsaISites.length} BsaI site{bsaISites.length > 1 ? 's' : ''}
                        </span>
                    )}
                    {groupMutations.length > 0 && (
                        <span className="badge mutation" style={{ marginLeft: 6 }}>
                            {groupMutations.length} mutation{groupMutations.length > 1 ? 's' : ''}
                        </span>
                    )}
                </h3>
                <div className="alignment-controls">
                    <label className="dom-toggle compact">
                        <input
                            type="checkbox"
                            checked={showDomesticated}
                            onChange={onToggleDomesticated}
                        />
                        <span className="toggle-slider" />
                        <span className="toggle-label">{showDomesticated ? 'Domesticated' : 'Wildtype'}</span>
                    </label>
                    <button onClick={() => setZoom(z => Math.max(z / 1.5, 0.5))}>−</button>
                    <span className="zoom-label">{zoom.toFixed(1)}×</span>
                    <button onClick={() => setZoom(z => Math.min(z * 1.5, 10))}>+</button>
                    <button onClick={() => setZoom(1)}>Reset</button>
                </div>
            </div>
            {/* Track legend */}
            <div className="alignment-legend">
                <span><span className="al-swatch gc" /> GC Content</span>
                <span><span className="al-swatch cds-plus" /> CDS (+)</span>
                <span><span className="al-swatch cds-minus" /> CDS (−)</span>
                <span><span className="al-swatch bsai" /> BsaI Site</span>
                <span><span className="al-swatch mut" /> {showDomesticated ? 'Domesticated' : 'Mutation'}</span>
            </div>
            <div className="alignment-canvas-wrap" ref={wrapRef}>
                <canvas ref={canvasRef} />
            </div>
        </div>
    );
}
