# EXP_002 Simulation — Handoff

**Last updated**: 2026-03-17  
**Status**: T7 corrected sweep COMPLETE ✅ — all major sweeps done

---

## What We Built

A GPU-ready bacterial synthetic GC simulation in Python/JAX:
- `src/bacterial_gc/` — 11 modules (config, state, growth, selection, simulation, analysis + GPU variants)
- `sweep.py`, `sweep_L40.py`, `sweep_T7_rates.py` — parameter sweep scripts
- `validate_controls.py` — 5 validation controls
- `presentation/generate_pptx.js` — 20-slide lab meeting deck
- Server deployment at `michael@172.16.1.80:~/gc_simulation/`

## What We Found

### 1. Muller's Ratchet Dominates at High Mutation Rates
First sweep (L=400, N=10K): only **1/16 conditions showed maturation**. Mutation load overwhelms Hill selection at rates ≥0.0003/bp/div.

### 2. Our First Sweep Used Wrong Rates
Rates were **10-100× above actual T7 range**. T7 variants span 10⁻⁸–10⁻⁴/bp/div; we tested 10⁻⁴–10⁻³.

### 3. Weaker Selection = Better Outcomes
K=0.3 (weakest) always outperforms K=0.05 (strongest). Strong selection kills diversity.

### 4. L=40 Scaling Validated
L=400→L=40 with scaled parameters produces same qualitative results. Enables GPU scaling to N=10⁷.

### 5. Simulation Is Correct (5 Controls Pass)
Zero mutation, no selection, perfect selection, low mutation, lethal — all pass.

### 6. Sharp Maturation Boundary at T7 V4 (10⁻⁵) 🎉
- **V1–V3 (≤10⁻⁶)**: maturation at ALL selection strengths (16/16)
- **V4 (10⁻⁵)**: depends on selection — weak selection rescues it
- **V5 (10⁻⁴)**: degradation everywhere
- **T7 V2 (10⁻⁷) is the sweet spot**: +0.21 affinity, best overall

---

## What's Next (Priority Order)

### HIGH — Immediate follow-ups
- [ ] **GPU scaling N=10⁷** at L=40 — does larger pop shift the V4 boundary? (proposal's key claim)
- [ ] **GC vs directed evolution** — code ready in `selection_gpu.py`, run on T7 rate grid
- [ ] **Multi-seed validation** — 5-10 seeds at V4 boundary to quantify stochastic variation

### MEDIUM — Parameter exploration
- [ ] **DZ/LZ cycling speed** — sweep `dz_divisions` ∈ {2,3,4,6,8,12} (Q3)
- [ ] **Initial affinity sweep** — does library quality matter? (Q11)

### LOW — Future phases
- [ ] Multi-epitope (Q6)
- [ ] 96-well parallel simulation (Q10)

---

## Key Files

| File | What |
|---|---|
| [summary.md](summary.md) | Experiment overview + progress |
| [LOG.md](LOG.md) | Chronological log |
| [open_questions.md](simulation/docs/open_questions.md) | Q1-Q11 scientific questions |
| [SWEEP_ANALYSIS.md](simulation/results/sweep/SWEEP_ANALYSIS.md) | L=400 sweep (first sweep) |
| [SWEEP_COMPARISON.md](simulation/results/SWEEP_COMPARISON.md) | L=400 vs L=40 comparison |
| [CONTROLS.md](simulation/results/controls/CONTROLS.md) | 5 validation controls |
| [T7_RATES_ANALYSIS.md](simulation/results/sweep_T7_rates/T7_RATES_ANALYSIS.md) | **T7 corrected sweep: 24 runs, full analysis** |
| [GC_Simulation_Lab_Meeting.pptx](presentation/GC_Simulation_Lab_Meeting.pptx) | 20-slide lab meeting presentation |
