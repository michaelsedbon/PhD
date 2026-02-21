import type { Tile, Lvl1Group } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface Lvl1AssemblyViewProps {
    group: Lvl1Group;
    tiles: Tile[];
    selectedTile: number | null;
    onSelectTile: (id: number) => void;
}

const GREEN = '#3fb950';
const YELLOW = '#d29922';
const ORANGE = '#db6d28';
const RED = '#f85149';
const ACCENT = '#58a6ff';

function tileColor(tile: Tile): string {
    if (tile.gg_ready) return GREEN;
    if (tile.internal_bsai === 1) return YELLOW;
    if (tile.internal_bsai === 2) return ORANGE;
    return RED;
}

function statusLabel(tile: Tile): string {
    if (tile.gg_ready) return 'Ready';
    return `${tile.internal_bsai} BsaI site${tile.internal_bsai > 1 ? 's' : ''}`;
}

export function Lvl1AssemblyView({ group, tiles, selectedTile, onSelectTile }: Lvl1AssemblyViewProps) {
    const groupTiles = tiles
        .filter(t => t.lvl1_group === group.id)
        .sort((a, b) => a.start - b.start);

    return (
        <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-3 text-sm">
                    <span className="text-zinc-100">Lvl1 Group {group.id}</span>
                    <Badge
                        variant="outline"
                        className="text-[10px]"
                        style={{ borderColor: group.complete_before ? GREEN : ORANGE, color: group.complete_before ? GREEN : ORANGE }}
                    >
                        {group.complete_before ? '✓ Complete' : `${group.blocked_tiles_count} blocked`}
                    </Badge>
                    <span className="text-zinc-500 text-xs ml-auto">
                        {(group.start / 1000).toFixed(0)}–{(group.end / 1000).toFixed(0)} kb · {(group.length / 1000).toFixed(1)} kb
                    </span>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* ── Assembled construct diagram ── */}
                <div className="space-y-1.5">
                    <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">Assembled Lvl1 construct</div>
                    <div className="flex items-center overflow-x-auto py-2 px-1 gap-0">
                        {/* Backbone start */}
                        <div className="flex-shrink-0 flex items-center">
                            <div className="h-8 w-6 rounded-l bg-zinc-700 flex items-center justify-center">
                                <span className="text-[8px] text-zinc-400 rotate-[-90deg]">BB</span>
                            </div>
                        </div>

                        {groupTiles.map((tile, i) => {
                            const isSelected = selectedTile === tile.id;
                            const color = tileColor(tile);
                            return (
                                <div key={tile.id} className="flex items-center flex-shrink-0">
                                    {/* Junction overhang */}
                                    <div className="flex flex-col items-center mx-0.5">
                                        <div
                                            className="text-[9px] font-mono font-bold px-0.5 rounded"
                                            style={{ color: ACCENT }}
                                        >
                                            {tile.overhang_left}
                                        </div>
                                        <div className="w-0.5 h-3 bg-zinc-600" />
                                    </div>

                                    {/* Tile block */}
                                    <button
                                        onClick={() => onSelectTile(tile.id)}
                                        className="relative group cursor-pointer transition-all"
                                        style={{
                                            border: isSelected ? `2px solid white` : `1px solid ${color}40`,
                                            borderRadius: '4px',
                                        }}
                                    >
                                        <div
                                            className="h-8 flex items-center justify-center px-2 min-w-[40px]"
                                            style={{
                                                background: `${color}20`,
                                                borderRadius: '3px',
                                            }}
                                        >
                                            <div className="flex flex-col items-center">
                                                <span className="text-[10px] font-bold" style={{ color }}>T{tile.id}</span>
                                                <span className="text-[8px] text-zinc-500">{(tile.length / 1000).toFixed(1)}k</span>
                                            </div>
                                        </div>
                                        {/* Status indicator */}
                                        {!tile.gg_ready && (
                                            <div
                                                className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full border border-zinc-900"
                                                style={{ background: color }}
                                            />
                                        )}
                                    </button>

                                    {/* Last tile: right overhang */}
                                    {i === groupTiles.length - 1 && (
                                        <div className="flex flex-col items-center mx-0.5">
                                            <div
                                                className="text-[9px] font-mono font-bold px-0.5 rounded"
                                                style={{ color: ACCENT }}
                                            >
                                                {tile.overhang_right}
                                            </div>
                                            <div className="w-0.5 h-3 bg-zinc-600" />
                                        </div>
                                    )}
                                </div>
                            );
                        })}

                        {/* Backbone end */}
                        <div className="flex-shrink-0">
                            <div className="h-8 w-6 rounded-r bg-zinc-700 flex items-center justify-center">
                                <span className="text-[8px] text-zinc-400 rotate-[-90deg]">BB</span>
                            </div>
                        </div>
                    </div>
                </div>

                <Separator className="bg-zinc-800" />

                {/* ── Genome alignment ── */}
                <div className="space-y-1.5">
                    <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">Genome alignment</div>
                    <div className="relative h-10 rounded bg-zinc-800/50 overflow-hidden">
                        {groupTiles.map(tile => {
                            const left = ((tile.start - group.start) / group.length) * 100;
                            const width = (tile.length / group.length) * 100;
                            const isSelected = selectedTile === tile.id;
                            const color = tileColor(tile);
                            return (
                                <button
                                    key={tile.id}
                                    onClick={() => onSelectTile(tile.id)}
                                    className="absolute top-1 bottom-1 cursor-pointer transition-opacity hover:opacity-100"
                                    style={{
                                        left: `${left}%`,
                                        width: `${width}%`,
                                        background: `${color}40`,
                                        borderLeft: `1px solid ${color}`,
                                        borderRight: `1px solid ${color}`,
                                        opacity: isSelected ? 1 : 0.6,
                                        outline: isSelected ? `2px solid white` : 'none',
                                        borderRadius: '2px',
                                    }}
                                >
                                    <span className="text-[8px] font-bold absolute inset-0 flex items-center justify-center" style={{ color }}>
                                        {tile.id}
                                    </span>
                                </button>
                            );
                        })}
                        {/* Axis labels */}
                        <div className="absolute bottom-0 left-0 text-[8px] text-zinc-600 px-1">
                            {(group.start / 1000).toFixed(0)}k
                        </div>
                        <div className="absolute bottom-0 right-0 text-[8px] text-zinc-600 px-1">
                            {(group.end / 1000).toFixed(0)}k
                        </div>
                    </div>
                </div>

                {/* ── Tile list ── */}
                <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">Tiles ({groupTiles.length})</div>
                <div className="grid grid-cols-1 gap-1">
                    {groupTiles.map(tile => {
                        const color = tileColor(tile);
                        const isSelected = selectedTile === tile.id;
                        return (
                            <button
                                key={tile.id}
                                onClick={() => onSelectTile(tile.id)}
                                className="flex items-center gap-2 px-2 py-1.5 rounded text-left transition-colors"
                                style={{
                                    background: isSelected ? `${color}15` : 'transparent',
                                    border: isSelected ? `1px solid ${color}40` : '1px solid transparent',
                                }}
                            >
                                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
                                <span className="text-xs font-mono text-zinc-300 w-8">T{tile.id}</span>
                                <span className="text-[10px] text-zinc-500">{(tile.length / 1000).toFixed(1)} kb</span>
                                <span className="text-[10px] ml-auto" style={{ color }}>
                                    {statusLabel(tile)}
                                </span>
                                <span className="text-[10px] font-mono text-zinc-600">
                                    {tile.overhang_left}…{tile.overhang_right}
                                </span>
                            </button>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}
