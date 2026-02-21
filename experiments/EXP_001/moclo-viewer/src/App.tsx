import { useEffect, useState, useCallback } from 'react';
import type { DataBundle, Tile, Lvl1Group } from '@/types';
import { GenomeCanvas } from '@/components/GenomeCanvas';
import { Lvl1AssemblyView } from '@/components/Lvl1AssemblyView';
import { PartDetailPanel } from '@/components/PartDetailPanel';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { TooltipProvider } from '@/components/ui/tooltip';

const GREEN = '#3fb950';
const ACCENT = '#58a6ff';

function StatsBar({ data }: { data: DataBundle }) {
  const s = data.stats;
  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-zinc-900/80 border-b border-zinc-800">
      <span className="text-sm font-semibold text-zinc-100">MoClo Viewer</span>
      <span className="text-xs text-zinc-500">·</span>
      <span className="text-xs text-zinc-400">{data.genome.name}</span>
      <span className="text-xs text-zinc-600">({(data.genome.length / 1e6).toFixed(2)} Mb)</span>
      <div className="ml-auto flex items-center gap-2">
        <Badge variant="outline" className="text-[10px] border-zinc-700 text-zinc-400">
          {s.total_tiles} tiles
        </Badge>
        <Badge variant="outline" className="text-[10px]" style={{ borderColor: GREEN, color: GREEN }}>
          {s.ready_tiles} ready
        </Badge>
        <Badge variant="outline" className="text-[10px]" style={{ borderColor: ACCENT, color: ACCENT }}>
          {s.total_lvl1_groups} Lvl1 groups → {s.complete_after}/{s.total_lvl1_groups} complete
        </Badge>
      </div>
    </div>
  );
}

function GroupSelector({ groups, selectedGroup, onSelectGroup }: {
  groups: Lvl1Group[];
  selectedGroup: number | null;
  onSelectGroup: (id: number) => void;
}) {
  return (
    <div className="flex items-center gap-1 flex-wrap px-4 py-2 bg-zinc-950/50 border-b border-zinc-800">
      <span className="text-[10px] text-zinc-600 uppercase tracking-wider mr-2 flex-shrink-0">Lvl1 Groups</span>
      {groups.map(g => {
        const isSelected = selectedGroup === g.id;
        const color = g.complete_before ? GREEN : '#d29922';
        return (
          <button
            key={g.id}
            onClick={() => onSelectGroup(g.id)}
            className="text-[10px] font-mono px-1.5 py-0.5 rounded transition-all"
            style={{
              background: isSelected ? `${ACCENT}20` : 'transparent',
              border: isSelected ? `1px solid ${ACCENT}` : '1px solid transparent',
              color: isSelected ? '#fff' : color,
            }}
          >
            {g.id}
          </button>
        );
      })}
    </div>
  );
}

export default function App() {
  const [data, setData] = useState<DataBundle | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null);
  const [selectedTile, setSelectedTile] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/data_bundle.json')
      .then(r => r.json())
      .then((d: DataBundle) => {
        setData(d);
        setSelectedGroup(0);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load data:', err);
        setLoading(false);
      });
  }, []);

  const handleSelectGroup = useCallback((id: number) => {
    setSelectedGroup(id);
    setSelectedTile(null);
  }, []);

  const handleSelectTile = useCallback((id: number) => {
    setSelectedTile(id);
    if (data) {
      const tile = data.tiles.find(t => t.id === id);
      if (tile && tile.lvl1_group !== selectedGroup) {
        setSelectedGroup(tile.lvl1_group);
      }
    }
  }, [data, selectedGroup]);

  if (loading) {
    return (
      <div className="h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-zinc-400 text-sm animate-pulse">Loading MoClo data…</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-red-400 text-sm">Failed to load data</div>
      </div>
    );
  }

  const currentGroup = data.lvl1_groups.find(g => g.id === selectedGroup) || null;
  const currentTile = data.tiles.find(t => t.id === selectedTile) || null;

  return (
    <TooltipProvider>
      <div className="h-screen bg-zinc-950 flex flex-col overflow-hidden">
        {/* Stats bar */}
        <StatsBar data={data} />

        {/* Genome canvas */}
        <div className="px-4 pt-3 pb-1 bg-zinc-950">
          <GenomeCanvas
            tiles={data.tiles}
            groups={data.lvl1_groups}
            genomeLength={data.genome.length}
            selectedTile={selectedTile}
            selectedGroup={selectedGroup}
            onSelectTile={handleSelectTile}
            onSelectGroup={handleSelectGroup}
          />
        </div>

        {/* Group selector */}
        <GroupSelector
          groups={data.lvl1_groups}
          selectedGroup={selectedGroup}
          onSelectGroup={handleSelectGroup}
        />

        {/* Main content area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left: Lvl1 Assembly View */}
          <div className="flex-1 overflow-hidden">
            <ScrollArea className="h-full">
              <div className="p-4">
                {currentGroup ? (
                  <Lvl1AssemblyView
                    group={currentGroup}
                    tiles={data.tiles}
                    selectedTile={selectedTile}
                    onSelectTile={handleSelectTile}
                  />
                ) : (
                  <div className="text-zinc-500 text-sm text-center py-12">
                    Select an Lvl1 group to view its assembly
                  </div>
                )}
              </div>
            </ScrollArea>
          </div>

          {/* Right: Part detail panel */}
          <div className="w-[380px] border-l border-zinc-800 bg-zinc-950/50 overflow-hidden flex-shrink-0">
            {currentTile ? (
              <div className="h-full p-3">
                <PartDetailPanel tile={currentTile} />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-zinc-600 text-xs space-y-2">
                  <div className="text-2xl">🧬</div>
                  <div>Click a tile to view details</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}
