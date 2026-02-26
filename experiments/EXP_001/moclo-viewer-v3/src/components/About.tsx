import { AppData, ViewState } from '../types';
import { useMemo } from 'react';

interface Props {
    data: AppData;
    onNavigate: (v: ViewState) => void;
}

export default function About({ data }: Props) {
    const { bundle, geneProducts } = data;

    const pathwayStats = useMemo(() => {
        const withPathways = geneProducts.filter(g => g.pathways && g.pathways.length > 0);
        const allPathways = new Set<string>();
        for (const g of geneProducts) for (const p of (g.pathways || [])) allPathways.add(p);
        return { withPathways: withPathways.length, totalPathways: allPathways.size };
    }, [geneProducts]);

    const catStats = useMemo(() => {
        const cats = new Map<string, number>();
        for (const g of geneProducts) cats.set(g.category, (cats.get(g.category) || 0) + 1);
        return Array.from(cats.entries()).sort((a, b) => b[1] - a[1]);
    }, [geneProducts]);

    return (
        <div className="about-page">
            <h2>📖 About this Application</h2>
            <p className="about-intro">
                MoClo Viewer V3 is an interactive tool for exploring and optimizing the <em>E. coli</em> K-12 MG1655
                genome tiling for Modular Cloning (MoClo/Golden Gate) assembly.
            </p>

            {/* ── Design Rationale ── */}
            <section className="about-section">
                <h3>🧬 MoClo Genome Tiling Design</h3>
                <div className="about-card">
                    <h4>Why 15 tiles per Lvl1 group?</h4>
                    <p>
                        The tile count balances <strong>genome coverage</strong> against <strong>assembly complexity</strong>.
                        Golden Gate (Type IIS) efficiency drops with fragment count — 15 is at the practical upper limit
                        for reliable one-pot assembly. Fewer tiles would require more Lvl1 groups (increasing Lvl2 assembly rounds),
                        while more tiles would lower ligation success rates.
                    </p>
                    <p className="about-ref">
                        📄 <em>Engler et al. (2009)</em> — "Golden Gate Shuffling: A One-Pot DNA Shuffling Method Based on Type IIs Restriction Enzymes."
                        <a href="https://doi.org/10.1371/journal.pone.0005553" target="_blank" rel="noopener">PLOS ONE 4(5):e5553</a>
                    </p>
                </div>

                <div className="about-card">
                    <h4>Junction placement: operon-aware intergenic boundaries</h4>
                    <p>
                        Tile boundaries are placed in <strong>intergenic regions</strong> to avoid splitting coding sequences.
                        The design algorithm prioritizes <strong>inter-operon</strong> junctions over intra-operon ones —
                        preserving operon integrity wherever possible. Current design achieves <strong>99.7% CDS-safe</strong> junctions.
                    </p>
                    <p>
                        Each junction introduces a <strong>4-nt scar</strong> from the standardized overhang system.
                        Since these are intergenic, the scars don't disrupt gene function.
                    </p>
                </div>

                <div className="about-card">
                    <h4>Standardized overhangs enable combinatorial libraries</h4>
                    <p>
                        V2 uses a fixed set of <strong>16 positional overhangs</strong> instead of genome-derived ones.
                        This means all tiles at the same position share identical overhang pairs and are
                        <strong> fully interchangeable</strong> across Lvl1 groups — enabling chimeric assemblies
                        and combinatorial library construction.
                    </p>
                    <p>
                        Overhang design constraints: no palindromes, no homopolymer runs ≥3, Hamming distance ≥2 between all pairs,
                        no BsaI site overlap, no reverse-complement duplicates.
                    </p>
                </div>
            </section>

            {/* ── Domestication ── */}
            <section className="about-section">
                <h3>🔧 Domestication (BsaI Removal)</h3>
                <div className="about-card">
                    <p>
                        Golden Gate assembly uses the BsaI restriction enzyme. Any <strong>internal BsaI recognition sites</strong> within
                        Lvl0 tiles must be removed ("domesticated") via <strong>synonymous mutations</strong> — silent codon changes
                        that eliminate the cut site without altering the protein sequence.
                    </p>
                    <p>
                        All {bundle.stats.blocked_tiles} tiles requiring domestication have pre-computed <strong>mutagenic primer pairs</strong> and
                        <strong> OE-PCR (overlap-extension PCR) plans</strong>. Once domestication is complete, all Lvl0 parts
                        become GG-ready.
                    </p>
                    <p className="about-highlight">
                        ✅ <strong>The clonability score assumes all Lvl0 parts are domesticated</strong> — it evaluates assembly
                        success based on fragment characteristics, not BsaI content.
                    </p>
                </div>
            </section>

            {/* ── Clonability Score ── */}
            <section className="about-section">
                <h3>📊 Clonability Score Methodology</h3>
                <div className="about-card">
                    <h4>Composite score (0–100)</h4>
                    <p>
                        The clonability score predicts assembly success for each Lvl1 group based on three fragment-level factors,
                        <strong> assuming all domestication is complete</strong>:
                    </p>

                    <table className="about-table">
                        <thead>
                            <tr><th>Factor</th><th>Weight</th><th>Measures</th><th>Formula</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Fragment Size Balance</strong></td>
                                <td>40%</td>
                                <td>Uniformity of tile lengths within the group</td>
                                <td><code>1 − CV(lengths)</code>, clamped [0, 1]</td>
                            </tr>
                            <tr>
                                <td><strong>GC Uniformity</strong></td>
                                <td>30%</td>
                                <td>How close each tile's GC% is to the optimal 40–60% window</td>
                                <td><code>1 − mean(|GC − 0.5| / 0.2)</code>, clamped [0, 1]</td>
                            </tr>
                            <tr>
                                <td><strong>Fragment Count</strong></td>
                                <td>30%</td>
                                <td>Fewer fragments = easier assembly</td>
                                <td><code>1 − (filled_slots − 1) / max_slots</code></td>
                            </tr>
                        </tbody>
                    </table>

                    <p className="about-formula">
                        <code>Score = 100 × (0.4 × SizeBalance + 0.3 × GCUniformity + 0.3 × FragmentCount)</code>
                    </p>

                    <p className="about-ref">
                        Rationale: Golden Gate efficiency depends on equimolar fragment representation (size balance),
                        ligation efficiency at junctions (GC content affects secondary structure), and total fragment count
                        (more fragments = more combinatorial misligations).
                    </p>
                    <p className="about-ref">
                        📄 <em>Potapov et al. (2018)</em> — "Comprehensive Profiling of Four Base Overhang Ligation Fidelity by T4 DNA Ligase."
                        <a href="https://doi.org/10.1021/acssynbio.8b00333" target="_blank" rel="noopener">ACS Synth. Biol. 7(11):2665–2674</a>
                    </p>
                    <p className="about-ref">
                        📄 <em>Pryor et al. (2020)</em> — "Enabling one-pot Golden Gate assemblies of unprecedented complexity."
                        <a href="https://doi.org/10.1371/journal.pone.0228594" target="_blank" rel="noopener">PLOS ONE 15(2):e0228594</a>
                    </p>
                </div>

                <div className="about-card">
                    <h4>Score interpretation</h4>
                    <table className="about-table compact">
                        <thead>
                            <tr><th>Range</th><th>Label</th><th>Meaning</th></tr>
                        </thead>
                        <tbody>
                            <tr><td className="accent-green">≥ 80</td><td>Excellent</td><td>High predicted assembly success</td></tr>
                            <tr><td className="accent-yellow">60–79</td><td>Good</td><td>Expected to work, minor optimization possible</td></tr>
                            <tr><td className="accent-red">&lt; 60</td><td>Fair</td><td>May need troubleshooting or alternative strategy</td></tr>
                        </tbody>
                    </table>
                </div>
            </section>

            {/* ── Pathway Data ── */}
            <section className="about-section">
                <h3>🗺️ KEGG Pathway Annotations</h3>
                <div className="about-card">
                    <p>
                        Gene-to-pathway mappings are sourced from the <strong>KEGG REST API</strong> (organism: <code>eco</code>,
                        <em>E. coli</em> K-12 MG1655). Broad "overview" pathways (e.g., "Metabolic pathways", "Carbon metabolism")
                        are excluded to keep groupings specific.
                    </p>
                    <div className="about-stats-row">
                        <div className="about-stat">
                            <span className="about-stat-value accent-blue">{pathwayStats.withPathways}</span>
                            <span className="about-stat-label">of {geneProducts.length} genes with KEGG pathways</span>
                        </div>
                        <div className="about-stat">
                            <span className="about-stat-value accent-purple">{pathwayStats.totalPathways}</span>
                            <span className="about-stat-label">unique metabolic pathways</span>
                        </div>
                    </div>
                    <p>
                        The <strong>"🧬 Pathway Focus"</strong> optimization strategy in the Recombinator uses these annotations
                        to create functionally specialized Lvl1 groups — each group is assigned a target pathway, and tiles
                        are greedily allocated to maximize pathway coherence.
                    </p>
                    <p className="about-ref">
                        📄 <em>Kanehisa et al. (2023)</em> — "KEGG for taxonomy-based analysis of pathways and genomes."
                        <a href="https://doi.org/10.1093/nar/gkac963" target="_blank" rel="noopener">Nucleic Acids Res. 51(D1):D483–D489</a>
                    </p>
                </div>
            </section>

            {/* ── Functional Categories ── */}
            <section className="about-section">
                <h3>🏷️ Functional Categories ({catStats.length})</h3>
                <div className="about-card">
                    <p>
                        Each gene is classified into a functional category based on keyword matching against GenBank product annotations.
                        These categories are used for diversity optimization and visualization.
                    </p>
                    <div className="about-cat-grid">
                        {catStats.map(([cat, count]) => (
                            <div key={cat} className="about-cat-item">
                                <span className="about-cat-dot" style={{ background: getCatColor(cat) }} />
                                <span className="about-cat-name">{cat}</span>
                                <span className="about-cat-count">{count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── Optimization Strategies ── */}
            <section className="about-section">
                <h3>⚡ Optimization Strategies</h3>
                <div className="about-card">
                    <table className="about-table">
                        <thead>
                            <tr><th>Strategy</th><th>Objective</th><th>Algorithm</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>🌈 Max Diversity</td>
                                <td>Maximize unique functional categories per group</td>
                                <td>Greedy assignment preferring tiles with novel categories</td>
                            </tr>
                            <tr>
                                <td>🎯 Min Diversity</td>
                                <td>Minimize categories — functionally focused groups</td>
                                <td>Greedy overlap-maximizing with sorted initial seeding</td>
                            </tr>
                            <tr>
                                <td>🧬 Pathway Focus</td>
                                <td>Group tiles by KEGG metabolic pathway</td>
                                <td>Target pathway assignment → greedy pathway-match scoring</td>
                            </tr>
                            <tr>
                                <td>✅ Max GG-Ready</td>
                                <td>Concentrate GG-ready tiles into fewest groups</td>
                                <td>Sort by readiness, round-robin to balance GG count</td>
                            </tr>
                            <tr>
                                <td>✂️ Min BsaI</td>
                                <td>Minimize groups with high internal BsaI count</td>
                                <td>Sort by BsaI count, assign to highest-burden groups</td>
                            </tr>
                            <tr>
                                <td>🎲 Random</td>
                                <td>Random baseline for comparison</td>
                                <td>Fisher-Yates shuffle per position</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            {/* ── Downloads ── */}
            <section className="about-section">
                <h3>📥 Downloads</h3>
                <div className="about-card">
                    <p>
                        All annotated GenBank files and primer/design data are available for download.
                        Clone files can be opened in SnapGene, Geneious, Benchling, or ApE.
                    </p>
                    <div className="download-grid">
                        <a href="/downloads/lvl0_clones.zip" download className="download-card">
                            <div className="download-icon">🧬</div>
                            <div className="download-info">
                                <div className="download-name">Lvl0 Clones</div>
                                <div className="download-desc">686 annotated GenBank files — pICH41308 backbone + genomic insert + domestication mutations</div>
                                <div className="download-meta">3.8 MB · .gb files in ZIP</div>
                            </div>
                        </a>
                        <a href="/downloads/lvl1_assemblies.zip" download className="download-card">
                            <div className="download-icon">🔗</div>
                            <div className="download-info">
                                <div className="download-name">Lvl1 Assemblies</div>
                                <div className="download-desc">46 annotated GenBank files — 15-tile Golden Gate assemblies (~100 kb each) with CDS annotations</div>
                                <div className="download-meta">2.1 MB · .gb files in ZIP</div>
                            </div>
                        </a>
                        <a href="/downloads/csv_data.zip" download className="download-card">
                            <div className="download-icon">📊</div>
                            <div className="download-info">
                                <div className="download-name">Design Data (CSV)</div>
                                <div className="download-desc">Tile coordinates, primers, domestication mutations, PCR simulation, clone & assembly summaries</div>
                                <div className="download-meta">81 KB · 7 CSV files in ZIP</div>
                            </div>
                        </a>
                    </div>
                </div>
            </section>

            {/* ── Key statistics ── */}
            <section className="about-section">
                <h3>📈 Key Statistics</h3>
                <div className="about-stats-grid">
                    <div className="about-stat-card"><div className="about-stat-val">{bundle.genome.length.toLocaleString()} bp</div><div className="about-stat-lbl">Genome Length</div></div>
                    <div className="about-stat-card"><div className="about-stat-val">{bundle.stats.total_tiles}</div><div className="about-stat-lbl">Total Lvl0 Tiles</div></div>
                    <div className="about-stat-card"><div className="about-stat-val">{bundle.stats.total_lvl1_groups}</div><div className="about-stat-lbl">Lvl1 Groups</div></div>
                    <div className="about-stat-card"><div className="about-stat-val">{bundle.design.tiles_per_group}</div><div className="about-stat-lbl">Tiles per Group</div></div>
                    <div className="about-stat-card"><div className="about-stat-val">{bundle.stats.ready_tiles}</div><div className="about-stat-lbl">GG-Ready Tiles</div></div>
                    <div className="about-stat-card"><div className="about-stat-val">{bundle.stats.blocked_tiles}</div><div className="about-stat-lbl">Need Domestication</div></div>
                    <div className="about-stat-card"><div className="about-stat-val">{geneProducts.length}</div><div className="about-stat-lbl">Annotated Genes</div></div>
                    <div className="about-stat-card"><div className="about-stat-val">{bundle.stats.total_primers}</div><div className="about-stat-lbl">Total Oligos</div></div>
                </div>
            </section>
        </div>
    );
}

/* Color helper (duplicated to keep component standalone) */
const CATEGORY_COLORS: Record<string, string> = {
    'Transport': '#58a6ff', 'Kinase / Phosphatase': '#3fb950',
    'Redox Enzymes': '#f85149', 'Biosynthesis': '#d29922',
    'Transferase': '#bc8cff', 'Regulation': '#39d2c0',
    'Transcription': '#ff7b72', 'Translation': '#79c0ff',
    'DNA Maintenance': '#d2a8ff', 'Mobile Elements': '#ffa657',
    'Motility': '#56d364', 'Membrane': '#7ee787',
    'Fimbriae / Pili': '#f778ba', 'Proteolysis': '#ff9bce',
    'Chaperones / Stress': '#ffdf5d', 'Uncharacterized': '#484f58',
    'Lyase / Isomerase': '#a5d6ff', 'Hydrolase': '#ffc680',
    'Other': '#6e7681', 'Unknown': '#30363d',
};
function getCatColor(cat: string) { return CATEGORY_COLORS[cat] || '#6e7681'; }
