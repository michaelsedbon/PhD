import type { Tile } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';

interface PartDetailPanelProps {
    tile: Tile;
}

const GREEN = '#3fb950';
const YELLOW = '#d29922';
const ORANGE = '#db6d28';
const RED = '#f85149';
const ACCENT = '#58a6ff';
const PURPLE = '#bc8cff';

function tileColor(tile: Tile): string {
    if (tile.gg_ready) return GREEN;
    if (tile.internal_bsai === 1) return YELLOW;
    if (tile.internal_bsai === 2) return ORANGE;
    return RED;
}

function InfoRow({ label, value, mono }: { label: string; value: string | number; mono?: boolean }) {
    return (
        <div className="flex justify-between items-center py-1 text-xs">
            <span className="text-zinc-500">{label}</span>
            <span className={`text-zinc-200 ${mono ? 'font-mono' : ''}`}>{value}</span>
        </div>
    );
}

function PrimerBlock({ label, seq, tm }: { label: string; seq: string; tm: number }) {
    // Highlight BsaI adapter (CGTCTCN) at start
    const hasBsaI = seq.toUpperCase().startsWith('CGTCTCN');

    return (
        <div className="space-y-1">
            <div className="flex items-center gap-2">
                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">{label}</span>
                <span className="text-[10px] text-zinc-600">Tm {tm}°C</span>
            </div>
            <div className="font-mono text-[11px] leading-relaxed bg-zinc-800/50 rounded px-2 py-1.5 break-all">
                {hasBsaI ? (
                    <>
                        <span style={{ color: PURPLE }}>CGTCTCN</span>
                        <span style={{ color: ACCENT }}>{seq.slice(7, 11)}</span>
                        <span className="text-zinc-300">{seq.slice(11)}</span>
                    </>
                ) : (
                    <span className="text-zinc-300">{seq}</span>
                )}
            </div>
            {hasBsaI && (
                <div className="flex gap-2 text-[9px] text-zinc-600">
                    <span><span style={{ color: PURPLE }}>■</span> BsaI site</span>
                    <span><span style={{ color: ACCENT }}>■</span> 4-nt overhang</span>
                    <span><span className="text-zinc-400">■</span> binding region</span>
                </div>
            )}
        </div>
    );
}

export function PartDetailPanel({ tile }: PartDetailPanelProps) {
    const color = tileColor(tile);

    return (
        <ScrollArea className="h-full">
            <div className="space-y-3 p-1">
                {/* ── Header ── */}
                <Card className="border-zinc-800 bg-zinc-900/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="flex items-center gap-2 text-sm">
                            <div className="w-3 h-3 rounded-full" style={{ background: color }} />
                            <span>Tile {tile.id}</span>
                            <Badge
                                variant="outline"
                                className="text-[10px] ml-auto"
                                style={{ borderColor: color, color }}
                            >
                                {tile.gg_ready ? '✓ GG Ready' : `${tile.internal_bsai} BsaI`}
                            </Badge>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-0 pt-0">
                        <InfoRow label="Position" value={`${tile.start.toLocaleString()}–${tile.end.toLocaleString()}`} />
                        <InfoRow label="Length" value={`${tile.length.toLocaleString()} bp`} />
                        <InfoRow label="GC content" value={tile.gc_content !== null ? `${tile.gc_content}%` : 'N/A'} />
                        <InfoRow label="Lvl1 group" value={tile.lvl1_group} />
                        <InfoRow label="Boundary" value={tile.boundary_type} />
                    </CardContent>
                </Card>

                {/* ── MoClo Lvl0 construct ── */}
                <Card className="border-zinc-800 bg-zinc-900/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-xs text-zinc-400">MoClo Lvl0 construct</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                        <div className="flex items-center gap-0 overflow-x-auto py-2">
                            {/* pICH backbone */}
                            <div className="flex-shrink-0 h-7 w-8 bg-zinc-700 rounded-l flex items-center justify-center">
                                <span className="text-[7px] text-zinc-400">pICH</span>
                            </div>

                            {/* BsaI site (left) */}
                            <div className="flex-shrink-0 flex flex-col items-center">
                                <div className="text-[8px] font-mono" style={{ color: PURPLE }}>BsaI</div>
                                <div className="w-3 h-1" style={{ background: PURPLE }} />
                            </div>

                            {/* Left overhang */}
                            <div className="flex-shrink-0 h-7 px-1 flex items-center" style={{ background: `${ACCENT}20`, border: `1px solid ${ACCENT}40`, borderRadius: '2px' }}>
                                <span className="text-[10px] font-mono font-bold" style={{ color: ACCENT }}>{tile.overhang_left}</span>
                            </div>

                            {/* Insert */}
                            <div className="flex-shrink-0 h-7 px-3 flex items-center" style={{ background: `${color}15`, borderTop: `2px solid ${color}`, borderBottom: `2px solid ${color}` }}>
                                <span className="text-[10px] font-mono" style={{ color }}>
                                    {(tile.length / 1000).toFixed(1)} kb insert
                                </span>
                            </div>

                            {/* Right overhang */}
                            <div className="flex-shrink-0 h-7 px-1 flex items-center" style={{ background: `${ACCENT}20`, border: `1px solid ${ACCENT}40`, borderRadius: '2px' }}>
                                <span className="text-[10px] font-mono font-bold" style={{ color: ACCENT }}>{tile.overhang_right}</span>
                            </div>

                            {/* BsaI site (right) */}
                            <div className="flex-shrink-0 flex flex-col items-center">
                                <div className="text-[8px] font-mono" style={{ color: PURPLE }}>BsaI</div>
                                <div className="w-3 h-1" style={{ background: PURPLE }} />
                            </div>

                            {/* pICH backbone */}
                            <div className="flex-shrink-0 h-7 w-8 bg-zinc-700 rounded-r flex items-center justify-center">
                                <span className="text-[7px] text-zinc-400">pICH</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* ── Primers ── */}
                <Card className="border-zinc-800 bg-zinc-900/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-xs text-zinc-400">Primers</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 pt-0">
                        <Tabs defaultValue="tile" className="w-full">
                            <TabsList className="w-full bg-zinc-800">
                                <TabsTrigger value="tile" className="text-[11px] flex-1">Tile primers</TabsTrigger>
                                {tile.domestication && (
                                    <TabsTrigger value="mutagenic" className="text-[11px] flex-1">Mutagenic ({tile.domestication.n_sites})</TabsTrigger>
                                )}
                            </TabsList>
                            <TabsContent value="tile" className="space-y-3 mt-3">
                                <PrimerBlock label="Forward" seq={tile.fwd_primer} tm={tile.fwd_tm} />
                                <Separator className="bg-zinc-800" />
                                <PrimerBlock label="Reverse" seq={tile.rev_primer} tm={tile.rev_tm} />
                            </TabsContent>
                            {tile.domestication && (
                                <TabsContent value="mutagenic" className="space-y-3 mt-3">
                                    {tile.domestication.primers.map((p, i) => (
                                        <div key={i} className="space-y-2">
                                            <div className="flex items-center gap-2">
                                                <Badge variant="outline" className="text-[9px]" style={{ borderColor: ORANGE, color: ORANGE }}>
                                                    Site {i + 1}
                                                </Badge>
                                                <span className="text-[10px] text-zinc-500">
                                                    pos {p.site_pos.toLocaleString()} · {p.original_nt}→{p.mutant_nt}
                                                </span>
                                                <span className="text-[10px] text-zinc-600 ml-auto">
                                                    {p.codon_change} {p.gene !== 'intergenic' ? `(${p.gene})` : ''}
                                                </span>
                                            </div>
                                            <PrimerBlock label={`Mut Fwd ${i + 1}`} seq={p.fwd_seq} tm={p.fwd_tm} />
                                            <PrimerBlock label={`Mut Rev ${i + 1}`} seq={p.rev_seq} tm={p.rev_tm} />
                                            {i < tile.domestication!.primers.length - 1 && <Separator className="bg-zinc-800" />}
                                        </div>
                                    ))}
                                </TabsContent>
                            )}
                        </Tabs>
                    </CardContent>
                </Card>

                {/* ── Domestication / Sub-fragments ── */}
                {tile.domestication && (
                    <Card className="border-zinc-800 bg-zinc-900/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="flex items-center gap-2 text-xs text-zinc-400">
                                OE-PCR plan
                                <Badge variant="outline" className="text-[9px]" style={{ borderColor: ORANGE, color: ORANGE }}>
                                    {tile.domestication.subfragments.length} sub-fragments
                                </Badge>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0 space-y-3">
                            {/* Visual diagram */}
                            <div className="flex items-center gap-0 overflow-x-auto py-1">
                                {tile.domestication.subfragments.map((frag, i) => (
                                    <div key={i} className="flex items-center flex-shrink-0">
                                        <div
                                            className="h-6 px-2 flex items-center rounded"
                                            style={{
                                                background: `${[GREEN, ACCENT, PURPLE, YELLOW][i % 4]}15`,
                                                border: `1px solid ${[GREEN, ACCENT, PURPLE, YELLOW][i % 4]}40`,
                                                minWidth: '50px',
                                            }}
                                        >
                                            <span className="text-[9px] font-mono text-zinc-300">
                                                F{frag.index + 1} · {(frag.length / 1000).toFixed(1)}k
                                            </span>
                                        </div>
                                        {i < tile.domestication!.subfragments.length - 1 && (
                                            <div className="flex flex-col items-center mx-0.5">
                                                <div className="text-[8px]" style={{ color: ORANGE }}>✕</div>
                                                <div className="w-0.5 h-2 bg-zinc-700" />
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                            <div className="text-[10px] text-zinc-500 flex items-center gap-1">
                                <span style={{ color: ORANGE }}>✕</span> = mutation site (BsaI destroyed)
                            </div>

                            {/* Fragment table */}
                            <div className="space-y-1">
                                {tile.domestication.subfragments.map((frag) => (
                                    <div key={frag.index} className="flex items-center gap-2 text-[10px] py-0.5">
                                        <span className="font-mono text-zinc-400 w-6">F{frag.index + 1}</span>
                                        <span className="text-zinc-500">{frag.start.toLocaleString()}–{frag.end.toLocaleString()}</span>
                                        <span className="text-zinc-600">{frag.length.toLocaleString()} bp</span>
                                        <span className="text-zinc-600 ml-auto">Tm {frag.fwd_tm}°/{frag.rev_tm}°C</span>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </ScrollArea>
    );
}
