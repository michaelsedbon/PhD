import { AppData, ViewState, TOTAL_SLIDES } from '../types';
import Slide1Overview from './slides/Slide1_Overview';
import Slide2Domestication from './slides/Slide2_Domestication';
import Slide3MoCloStandard from './slides/Slide3_MoCloStandard';
import Slide4PCRPlan from './slides/Slide4_PCRPlan';
import Slide5BuildingLvl1 from './slides/Slide5_BuildingLvl1';
import Slide6Combinations from './slides/Slide6_Combinations';

interface Props {
    data: AppData;
    slideIndex: number;
    onNavigate: (v: ViewState) => void;
}

const SLIDE_TITLES = [
    'Genome Tiling Overview',
    'Domestication Process',
    'MoClo Standard',
    'PCR Preparation',
    'Building Lvl1 Assemblies',
    'Combinatorial Potential',
];

export default function PresentationView({ data, slideIndex, onNavigate }: Props) {
    const goTo = (idx: number) => onNavigate({ view: 'presentation', slideIndex: idx });
    const prev = () => { if (slideIndex > 0) goTo(slideIndex - 1); };
    const next = () => {
        if (slideIndex < TOTAL_SLIDES - 1) goTo(slideIndex + 1);
    };
    const enterExplorer = () => onNavigate({ view: 'genome' });

    const slideProps = { data, onNext: next, onEnterExplorer: enterExplorer };

    return (
        <div className="presentation">
            {/* Top bar */}
            <div className="pres-topbar">
                <div className="pres-title">🧬 MoClo V3 — <span>{data.bundle.genome.name}</span></div>
                <div className="pres-slide-label">
                    {slideIndex + 1} / {TOTAL_SLIDES} — {SLIDE_TITLES[slideIndex]}
                </div>
                <button className="pres-explorer-btn" onClick={enterExplorer}>
                    Explorer →
                </button>
            </div>

            {/* Slide content */}
            <div className="pres-content">
                <div className="slide-container">
                    {slideIndex === 0 && <Slide1Overview {...slideProps} />}
                    {slideIndex === 1 && <Slide2Domestication {...slideProps} />}
                    {slideIndex === 2 && <Slide3MoCloStandard {...slideProps} />}
                    {slideIndex === 3 && <Slide4PCRPlan {...slideProps} />}
                    {slideIndex === 4 && <Slide5BuildingLvl1 {...slideProps} />}
                    {slideIndex === 5 && <Slide6Combinations {...slideProps} />}
                </div>
            </div>

            {/* Bottom nav */}
            <div className="pres-nav">
                <button className="nav-arrow" onClick={prev} disabled={slideIndex === 0}>
                    ←
                </button>
                <div className="pres-dots">
                    {Array.from({ length: TOTAL_SLIDES }, (_, i) => (
                        <button
                            key={i}
                            className={`pres-dot ${i === slideIndex ? 'active' : ''} ${i < slideIndex ? 'visited' : ''}`}
                            onClick={() => goTo(i)}
                            title={SLIDE_TITLES[i]}
                        />
                    ))}
                </div>
                <button
                    className="nav-arrow"
                    onClick={slideIndex === TOTAL_SLIDES - 1 ? enterExplorer : next}
                >
                    {slideIndex === TOTAL_SLIDES - 1 ? 'Explorer →' : '→'}
                </button>
            </div>
        </div>
    );
}
