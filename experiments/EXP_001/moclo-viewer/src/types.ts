// Data types for the MoClo genome viewer

export interface MutagenicPrimer {
    site_pos: number;
    original_nt: string;
    mutant_nt: string;
    codon_change: string;
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

export interface DomesticationInfo {
    n_sites: number;
    primers: MutagenicPrimer[];
    subfragments: SubFragment[];
}

export interface Tile {
    id: number;
    start: number;
    end: number;
    length: number;
    lvl1_group: number;
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
    gc_content: number | null;
    domestication: DomesticationInfo | null;
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
    genome: { name: string; accession: string; length: number };
    tiles: Tile[];
    lvl1_groups: Lvl1Group[];
    stats: Stats;
}
