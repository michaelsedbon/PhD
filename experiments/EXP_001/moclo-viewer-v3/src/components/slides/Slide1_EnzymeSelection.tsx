import { AppData } from '../../types';

interface Props {
    data: AppData;
    onNext: () => void;
    onEnterExplorer: () => void;
}

/* ── Enzyme comparison data ─────────────────────────────────────────── */

interface Enzyme {
    name: string;
    recognition: string;
    sites: number;
    sitesPerKb: number;
    maxGap: number;
    pctFree: number;
    verdict: 'best' | 'ok' | 'poor' | 'eliminated';
}

const ENZYMES: Enzyme[] = [
    { name: 'BsaI', recognition: 'GGTCTC', sites: 261, sitesPerKb: 0.06, maxGap: 96974, pctFree: 93.7, verdict: 'best' },
    { name: 'SapI', recognition: 'GCTCTTC', sites: 683, sitesPerKb: 0.15, maxGap: 43956, pctFree: 74.5, verdict: 'ok' },
    { name: 'AarI', recognition: 'CACCTGC', sites: 1107, sitesPerKb: 0.24, maxGap: 30137, pctFree: 50.9, verdict: 'poor' },
    { name: 'BsmBI', recognition: 'CGTCTC', sites: 1127, sitesPerKb: 0.24, maxGap: 30000, pctFree: 50.9, verdict: 'poor' },
    { name: 'BbsI', recognition: 'GAAGAC', sites: 1748, sitesPerKb: 0.38, maxGap: 25724, pctFree: 29.1, verdict: 'poor' },
    { name: 'BtgZI', recognition: 'GCGATG', sites: 5410, sitesPerKb: 1.17, maxGap: 6921, pctFree: 0.0, verdict: 'eliminated' },
];

const verdictColor = (v: Enzyme['verdict']) => {
    switch (v) {
        case 'best': return '#4fc3f7';
        case 'ok': return '#81c784';
        case 'poor': return '#ffb74d';
        case 'eliminated': return '#ef5350';
    }
};

export default function Slide1EnzymeSelection({ data }: Props) {
    return (
        <div className="slide">
            <h1 className="slide-title">Enzyme Selection</h1>
            <p className="slide-subtitle">
                Type IIS screen across <em>E.&nbsp;coli</em> MG1655 (4.64 Mb) — minimizing internal site burden for ~7 kb Golden Gate tiles
            </p>

            {/* Enzyme comparison table */}
            <div className="slide-section">
                <h2>Recognition Site Frequency — 8 Candidate Enzymes</h2>
                <div className="slide-explanation">
                    <p>
                        Both strands scanned for recognition sites of 8 Type IIS enzymes.
                        Key metric: fraction of the genome contained within contiguous site-free stretches ≥ 7 kb —
                        the threshold for a full tile requiring no domestication.
                    </p>
                </div>
                <div className="sota-table-wrapper">
                    <table className="sota-table enzyme-table">
                        <thead>
                            <tr>
                                <th>Enzyme</th>
                                <th>Recognition</th>
                                <th>Sites</th>
                                <th>Sites/kb</th>
                                <th>Max gap (kb)</th>
                                <th>% genome in free ≥7 kb</th>
                                <th>Verdict</th>
                            </tr>
                        </thead>
                        <tbody>
                            {ENZYMES.map((e) => (
                                <tr key={e.name} className={e.verdict === 'best' ? 'enzyme-best-row' : ''}>
                                    <td style={{ fontWeight: e.verdict === 'best' ? 700 : 400, color: verdictColor(e.verdict) }}>
                                        {e.name}
                                    </td>
                                    <td><code>{e.recognition}</code></td>
                                    <td className="enzyme-num">{e.sites.toLocaleString()}</td>
                                    <td className="enzyme-num">{e.sitesPerKb.toFixed(2)}</td>
                                    <td className="enzyme-num">{(e.maxGap / 1000).toFixed(1)}</td>
                                    <td className="enzyme-num" style={{ fontWeight: e.verdict === 'best' ? 700 : 400 }}>
                                        {e.pctFree.toFixed(1)}%
                                    </td>
                                    <td>
                                        <span
                                            className="enzyme-verdict"
                                            style={{ background: verdictColor(e.verdict) + '22', color: verdictColor(e.verdict) }}
                                        >
                                            {e.verdict === 'best' ? '★ Best' :
                                                e.verdict === 'ok' ? '2nd' :
                                                    e.verdict === 'poor' ? 'Poor' : '✗ Eliminated'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div className="slide-explanation" style={{ marginTop: '12px' }}>
                    <p>
                        <strong>BsaI</strong> dominates: 261 sites — 2.6× fewer than SapI (683), 4.2× fewer than AarI (1,107).
                        93.7% of the genome lies in site-free stretches ≥ 7 kb (vs 74.5% for SapI).
                        BtgZI eliminated — no 7 kb window is site-free.
                    </p>
                </div>
            </div>

            {/* Interactive figures */}
            <div className="slide-figures-row">
                <div className="slide-figure">
                    <h3>Site Density — 7 kb Sliding Window (BsaI vs SapI vs AarI)</h3>
                    <iframe src={`${import.meta.env.BASE_URL}figures/site_density_7kb_window.html`} title="BsaI site density" />
                </div>
                <div className="slide-figure">
                    <h3>BsaI Domestication Breakdown — Sites per 7 kb Tile</h3>
                    <iframe src={`${import.meta.env.BASE_URL}figures/domestication_donut.html`} title="Domestication donut" />
                </div>
            </div>
        </div>
    );
}
