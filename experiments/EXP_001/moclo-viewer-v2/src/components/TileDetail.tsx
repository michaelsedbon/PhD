import { useMemo } from 'react';
import { AppData, ViewState } from '../types';
import AlignmentCanvas from './AlignmentCanvas';

interface Props {
    data: AppData;
    tileId: number;
    onNavigate: (v: ViewState) => void;
}

export default function TileDetail({ data, tileId, onNavigate }: Props) {
    const tile = data.bundle.tiles[tileId];
    const group = data.bundle.lvl1_groups[tile.lvl1_group];

    // CDS regions overlapping tile
    const tileCDS = useMemo(() => {
        return data.cdsRegions.filter(c => c.end > tile.start && c.start < tile.end);
    }, [data.cdsRegions, tile]);

    // Mutations within tile
    const tileMutations = useMemo(() => {
        const muts: { position: number; gene: string; original: string; mutant: string; codon: string }[] = [];
        for (const [pos, m] of data.mutations) {
            if (pos >= tile.start && pos < tile.end) {
                muts.push({
                    position: pos,
                    gene: m.gene,
                    original: m.original,
                    mutant: m.mutant,
                    codon: m.codon_change,
                });
            }
        }
        return muts;
    }, [data.mutations, tile]);

    const dom = tile.domestication;

    return (
        <div className="tile-detail">
            {/* Header info cards */}
            <div className="tile-header-cards">
                <div className="tile-header-card">
                    <div className="label">Tile ID</div>
                    <div className="value">T{tile.id}</div>
                </div>
                <div className="tile-header-card">
                    <div className="label">Position</div>
                    <div className="value">P{tile.position}</div>
                </div>
                <div className="tile-header-card">
                    <div className="label">Lvl1 Group</div>
                    <div className="value">
                        <button
                            style={{
                                background: 'none', border: 'none', color: 'var(--blue)',
                                cursor: 'pointer', fontSize: 14, fontWeight: 600,
                                fontFamily: 'var(--font-sans)', padding: 0,
                            }}
                            onClick={() => onNavigate({ view: 'group', groupId: group.id })}
                        >
                            G{group.id}
                        </button>
                    </div>
                </div>
                <div className="tile-header-card">
                    <div className="label">Length</div>
                    <div className="value">{(tile.length / 1000).toFixed(1)} kb</div>
                </div>
                <div className="tile-header-card">
                    <div className="label">GC Content</div>
                    <div className="value">{tile.gc_content.toFixed(1)}%</div>
                </div>
                <div className="tile-header-card">
                    <div className="label">Status</div>
                    <div className="value">
                        <span className={`badge ${tile.gg_ready ? 'ready' : 'blocked'}`}>
                            {tile.gg_ready ? 'GG-Ready' : `${tile.internal_bsai} BsaI`}
                        </span>
                    </div>
                </div>
                <div className="tile-header-card">
                    <div className="label">Boundary</div>
                    <div className="value" style={{ fontSize: 12 }}>{tile.boundary_type}</div>
                </div>
                <div className="tile-header-card">
                    <div className="label">Overhangs</div>
                    <div className="value" style={{ fontSize: 12 }}>
                        <span className="badge overhang">{tile.overhang_left}</span>
                        {' → '}
                        <span className="badge overhang">{tile.overhang_right}</span>
                    </div>
                </div>
            </div>

            {/* Genomic range */}
            <div className="genome-canvas-wrapper">
                <h3>Genomic Range</h3>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>
                    {tile.start.toLocaleString()} – {tile.end.toLocaleString()} bp
                    <span style={{ color: 'var(--text-muted)', marginLeft: 8 }}>
                        ({tileCDS.length} CDS regions · {tileMutations.length} mutations)
                    </span>
                </div>
            </div>

            {/* Amplification primers */}
            <div className="primer-section">
                <h3>Amplification Primers</h3>
                <div className="primer-row">
                    <span className="dir fwd">FWD</span>
                    <span className="seq">{tile.fwd_primer}</span>
                    <span className="tm">{tile.fwd_tm.toFixed(1)}°C</span>
                </div>
                <div className="primer-row">
                    <span className="dir rev">REV</span>
                    <span className="seq">{tile.rev_primer}</span>
                    <span className="tm">{tile.rev_tm.toFixed(1)}°C</span>
                </div>
            </div>

            {/* Domestication section */}
            {dom && (
                <div className="domestication-section">
                    <h3>
                        <span className="badge blocked">{dom.n_sites} BsaI site{dom.n_sites > 1 ? 's' : ''}</span>
                        Domestication by OE-PCR
                    </h3>

                    {/* Subfragment diagram */}
                    <div className="subfragment-diagram">
                        {dom.subfragments.map((sf, i) => (
                            <div key={i} style={{ display: 'contents' }}>
                                {i > 0 && <div className="subfrag-arrow">⟶</div>}
                                <div className="subfrag-block">
                                    <div className="subfrag-label">SF{sf.index + 1}</div>
                                    <div className="subfrag-size">{sf.length} bp</div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Mutations */}
                    <h3 style={{ marginTop: 16 }}>
                        <span className="badge mutation">{dom.primers.length} silent mutations</span>
                    </h3>
                    <div className="mutation-list">
                        {dom.primers.map((p, i) => (
                            <div key={i} className="mutation-item">
                                <span className="pos">{p.site_pos.toLocaleString()}</span>
                                <span className="change">{p.original_nt}→{p.mutant_nt}</span>
                                <span className="gene-name">{p.gene}</span>
                            </div>
                        ))}
                    </div>

                    {/* Mutagenic primers */}
                    <h3 style={{ marginTop: 16 }}>Mutagenic Primers</h3>
                    {dom.primers.map((p, i) => (
                        <div key={i} style={{ marginBottom: 12 }}>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>
                                Site at {p.site_pos.toLocaleString()} ({p.gene})
                            </div>
                            <div className="primer-row">
                                <span className="dir fwd">FWD</span>
                                <span className="seq">{p.fwd_seq}</span>
                                <span className="tm">{p.fwd_tm.toFixed(1)}°C</span>
                            </div>
                            <div className="primer-row">
                                <span className="dir rev">REV</span>
                                <span className="seq">{p.rev_seq}</span>
                                <span className="tm">{p.rev_tm.toFixed(1)}°C</span>
                            </div>
                        </div>
                    ))}

                    {/* Subfragment primers */}
                    <h3 style={{ marginTop: 16 }}>Subfragment Primers</h3>
                    {dom.subfragments.map((sf, i) => (
                        <div key={i} style={{ marginBottom: 12 }}>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>
                                Subfragment {sf.index + 1} ({sf.length} bp)
                            </div>
                            <div className="primer-row">
                                <span className="dir fwd">FWD</span>
                                <span className="seq">{sf.fwd_primer}</span>
                                <span className="tm">{sf.fwd_tm.toFixed(1)}°C</span>
                            </div>
                            <div className="primer-row">
                                <span className="dir rev">REV</span>
                                <span className="seq">{sf.rev_primer}</span>
                                <span className="tm">{sf.rev_tm.toFixed(1)}°C</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Alignment */}
            <AlignmentCanvas
                genomeSeq={data.genomeSeq}
                tile={tile}
                cdsRegions={tileCDS}
                mutations={tileMutations}
            />
        </div>
    );
}
