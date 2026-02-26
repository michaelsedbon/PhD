import { AppData, ViewState, TOTAL_SLIDES } from '../types';
import Slide0StateOfTheArt from './slides/Slide0_StateOfTheArt';
import Slide1EnzymeSelection from './slides/Slide1_EnzymeSelection';
import Slide2Overview from './slides/Slide1_Overview';
import Slide3Domestication from './slides/Slide2_Domestication';
import Slide4MoCloStandard from './slides/Slide3_MoCloStandard';
import Slide5PCRPlan from './slides/Slide4_PCRPlan';
import Slide6BuildingLvl1 from './slides/Slide5_BuildingLvl1';
import Slide7Combinations from './slides/Slide6_Combinations';

interface Props {
    data: AppData;
    slideIndex: number;
    onNavigate: (v: ViewState) => void;
}

const SLIDE_TITLES = [
    'State of the Art',
    'Enzyme Selection',
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
                    {slideIndex === 0 && <Slide0StateOfTheArt {...slideProps} />}
                    {slideIndex === 1 && <Slide1EnzymeSelection {...slideProps} />}
                    {slideIndex === 2 && <Slide2Overview {...slideProps} />}
                    {slideIndex === 3 && <Slide3Domestication {...slideProps} />}
                    {slideIndex === 4 && <Slide4MoCloStandard {...slideProps} />}
                    {slideIndex === 5 && <Slide5PCRPlan {...slideProps} />}
                    {slideIndex === 6 && <Slide6BuildingLvl1 {...slideProps} />}
                    {slideIndex === 7 && <Slide7Combinations {...slideProps} />}
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

