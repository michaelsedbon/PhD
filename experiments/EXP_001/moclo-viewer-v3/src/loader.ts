import { AppData, DataBundle, Mutation, CDSRegion, Tile } from './types';

interface RawMutations {
    [pos: string]: { o: string; m: string; c: string; a: string; g: string };
}

export async function loadAllData(): Promise<AppData> {
    const [bundleRes, mutRes, seqRes, cdsRes] = await Promise.all([
        fetch('/data_bundle_v2.json'),
        fetch('/mutations.json'),
        fetch('/genome_seq.txt'),
        fetch('/cds_regions.json'),
    ]);

    const bundle: DataBundle = await bundleRes.json();
    const rawMut: RawMutations = await mutRes.json();
    const genomeSeq: string = (await seqRes.text()).trim();
    const cdsRegions: CDSRegion[] = await cdsRes.json();

    // Parse mutations
    const mutations = new Map<number, Mutation>();
    for (const [pos, m] of Object.entries(rawMut)) {
        const p = parseInt(pos);
        mutations.set(p, {
            position: p,
            original: m.o,
            mutant: m.m,
            codon_change: m.c,
            amino_acid: m.a,
            gene: m.g,
        });
    }

    // Index tiles by group
    const tilesByGroup = new Map<number, Tile[]>();
    for (const tile of bundle.tiles) {
        const arr = tilesByGroup.get(tile.lvl1_group) || [];
        arr.push(tile);
        tilesByGroup.set(tile.lvl1_group, arr);
    }
    // Sort tiles within each group by position
    for (const [, tiles] of tilesByGroup) {
        tiles.sort((a, b) => a.position - b.position);
    }

    return { bundle, mutations, genomeSeq, cdsRegions, tilesByGroup };
}
