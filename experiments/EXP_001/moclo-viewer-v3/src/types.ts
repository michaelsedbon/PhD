/* ── Data types for V3 MoClo Viewer ─────────────────────────────────── */

export interface Tile {
    id: number;
    start: number;
    end: number;
    length: number;
    lvl1_group: number;
    position: number;
    overhang_left: string;
    overhang_right: string;
    fwd_primer: string;
    rev_primer: string;
    fwd_tm: number;
    rev_tm: number;
    boundary_type: string;
    internal_bsai: number;
    primer_domesticated: number;
    extra_domestication: number;
    gg_ready: boolean;
    gc_content: number;
    domestication: DomesticationInfo | null;
}

export interface DomesticationInfo {
    n_sites: number;
    primers: DomesticationPrimer[];
    subfragments: SubFragment[];
}

export interface DomesticationPrimer {
    site_pos: number;
    original_nt: string;
    mutant_nt: string;
    gene: string;
    fwd_seq: string;
    rev_seq: string;
    fwd_tm: number;
    rev_tm: number;
}

export interface SubFragment {
    index: number;
    start: number;
    end: number;
    length: number;
    fwd_primer: string;
    rev_primer: string;
    fwd_tm: number;
    rev_tm: number;
}

export interface Lvl1Group {
    id: number;
    start: number;
    end: number;
    length: number;
    total_tiles: number;
    ready_tiles: number;
    blocked_tiles_count: number;
    blocked_tile_ids: number[];
    complete_before: boolean;
    complete_after: boolean;
}

export interface Mutation {
    position: number;
    original: string;
    mutant: string;
    codon_change: string;
    amino_acid: string;
    gene: string;
}

export interface CDSRegion {
    start: number;
    end: number;
    complement: boolean;
    gene: string;
}

export interface GeneProduct {
    gene: string;
    start: number;
    end: number;
    complement: boolean;
    product: string;
    category: string;
}

export interface DesignInfo {
    tiles_per_group: number;
    standard_overhangs: string[];
    overhang_type: string;
}

export interface GenomeInfo {
    name: string;
    accession: string;
    length: number;
}

export interface Stats {
    total_tiles: number;
    ready_tiles: number;
    blocked_tiles: number;
    total_lvl1_groups: number;
    complete_before: number;
    complete_after: number;
    total_primers: number;
    total_pcr_reactions: number;
}

export interface DataBundle {
    version: string;
    genome: GenomeInfo;
    design: DesignInfo;
    tiles: Tile[];
    lvl1_groups: Lvl1Group[];
    stats: Stats;
}

export interface AppData {
    bundle: DataBundle;
    mutations: Map<number, Mutation>;
    genomeSeq: string;
    cdsRegions: CDSRegion[];
    tilesByGroup: Map<number, Tile[]>;
    geneProducts: GeneProduct[];
}

// Navigation
export type ViewType = 'presentation' | 'genome' | 'group' | 'tile' | 'recombine';

export interface ViewState {
    view: ViewType;
    slideIndex?: number;
    groupId?: number;
    tileId?: number;
}

export const TOTAL_SLIDES = 6;
