const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

// ─── Design System (matches experiment viewer dark theme) ────────────
const COLORS = {
  bg:       "1A1A1F",
  cardBg:   "262630",
  fg:       "FBFBFB",
  muted:    "9A9AA0",
  accent:   "3B82F6",
  accent2:  "6366F1", // indigo
  success:  "22C55E",
  warning:  "F59E0B",
  danger:   "EF4444",
  cyan:     "06B6D4",
  border:   "3A3A44",
  dimBg:    "202028",
};

const FONT = "Calibri";
const FONT_MONO = "Courier New";

// Slide dimensions for 16:9 (10" × 5.625")
const W = 10;
const H = 5.625;

// ─── Helpers ─────────────────────────────────────────────────────────

function addFooter(slide, num, total) {
  slide.addText(`${num} / ${total}`, {
    x: 0, y: H - 0.3, w: W, h: 0.3,
    fontSize: 8, color: COLORS.muted, fontFace: FONT, align: "center"
  });
}

function addSectionLabel(slide, label) {
  slide.addShape("rectangle", {
    x: 0, y: 0, w: W, h: 0.03,
    fill: { color: COLORS.accent }
  });
  slide.addText(label.toUpperCase(), {
    x: 0.5, y: 0.15, w: 3, h: 0.25,
    fontSize: 8, fontFace: FONT, color: COLORS.accent,
    charSpacing: 4, bold: true, margin: 0
  });
}

function imgPath(relPath) {
  const full = path.resolve(__dirname, "..", "simulation", relPath);
  if (fs.existsSync(full)) return full;
  console.warn(`  ⚠ Image not found: ${full}`);
  return null;
}

function addImageSafe(slide, relPath, opts) {
  const p = imgPath(relPath);
  if (p) slide.addImage({ path: p, ...opts });
  else {
    slide.addText(`[Image: ${relPath}]`, {
      x: opts.x, y: opts.y, w: opts.w, h: opts.h,
      fontSize: 10, color: COLORS.muted, fontFace: FONT,
      align: "center", valign: "middle",
      fill: { color: COLORS.dimBg }
    });
  }
}

// ─── Build Presentation ──────────────────────────────────────────────

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Michael Sedbon";
pres.title = "GPU Simulation of a Synthetic Germinal Center";

const TOTAL_SLIDES = 20;
let slideNum = 0;

function newSlide(sectionLabel) {
  slideNum++;
  const slide = pres.addSlide();
  slide.background = { color: COLORS.bg };
  addFooter(slide, slideNum, TOTAL_SLIDES);
  if (sectionLabel) addSectionLabel(slide, sectionLabel);
  return slide;
}

// =====================================================================
// SLIDE 1 — Title
// =====================================================================
{
  const s = newSlide();
  // Accent bar at top
  s.addShape("rectangle", { x: 0, y: 0, w: W, h: 0.06, fill: { color: COLORS.accent } });
  // Title
  s.addText("GPU Simulation of a\nSynthetic Germinal Center", {
    x: 0.8, y: 1.0, w: 8.4, h: 2.2,
    fontSize: 36, fontFace: FONT, color: COLORS.fg,
    bold: true, align: "left", valign: "middle", lineSpacingMultiple: 1.1
  });
  // Subtitle
  s.addText("In silico modelling of affinity maturation\nin an engineered bacterial system", {
    x: 0.8, y: 3.0, w: 7, h: 0.8,
    fontSize: 16, fontFace: FONT, color: COLORS.muted, align: "left"
  });
  // Author + date
  s.addText("Michael Sedbon  ·  Lab Meeting  ·  March 2026", {
    x: 0.8, y: 4.5, w: 5, h: 0.4,
    fontSize: 11, fontFace: FONT, color: COLORS.accent, align: "left"
  });
  // Decorative accent line
  s.addShape("rectangle", { x: 0.8, y: 2.85, w: 2.5, h: 0.03, fill: { color: COLORS.accent } });
}

// =====================================================================
// SLIDE 2 — Problem: Affinity Maturation
// =====================================================================
{
  const s = newSlide("Introduction");
  s.addText("The Challenge: Affinity Maturation", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });
  s.addText([
    { text: "Natural germinal centers (GCs)", options: { bold: true, breakLine: true } },
    { text: "B cells undergo iterative cycles of somatic hypermutation (SHM) in the dark zone and antigen-based selection in the light zone, progressively improving antibody affinity.", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "The problem", options: { bold: true, color: COLORS.warning, breakLine: true } },
    { text: "Standard directed evolution lacks the DZ/LZ architecture. Mutations and selection happen in the same environment, limiting exploration of sequence space.", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Our approach", options: { bold: true, color: COLORS.success, breakLine: true } },
    { text: "Engineer a synthetic GC in E. coli: physically separate mutagenesis (DZ) from selection (LZ) and use robotic transfers to cycle between compartments.", options: {} },
  ], {
    x: 0.5, y: 1.3, w: 5.5, h: 3.5,
    fontSize: 12, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.3, valign: "top"
  });
  // Right side diagram placeholder
  s.addShape("rectangle", {
    x: 6.5, y: 1.2, w: 3.2, h: 3.6,
    fill: { color: COLORS.cardBg }, line: { color: COLORS.border, width: 1 }
  });
  s.addText("DZ → LZ → DZ\ncycle", {
    x: 6.5, y: 2.0, w: 3.2, h: 1.5,
    fontSize: 20, fontFace: FONT, color: COLORS.accent, align: "center", valign: "middle", bold: true
  });
  s.addText("Mutation          Selection\n(Growth)          (Beads)", {
    x: 6.5, y: 3.2, w: 3.2, h: 0.8,
    fontSize: 10, fontFace: FONT_MONO, color: COLORS.muted, align: "center"
  });
}

// =====================================================================
// SLIDE 3 — The Synthetic GC Concept
// =====================================================================
{
  const s = newSlide("Introduction");
  s.addText("The Synthetic Germinal Center", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  // Two cards: DZ and LZ
  // DZ card
  s.addShape("rectangle", {
    x: 0.5, y: 1.4, w: 4.2, h: 3.2,
    fill: { color: COLORS.cardBg }, line: { color: COLORS.border, width: 1 }
  });
  s.addShape("rectangle", { x: 0.5, y: 1.4, w: 4.2, h: 0.04, fill: { color: COLORS.danger } });
  s.addText("DARK ZONE (DZ)", {
    x: 0.7, y: 1.55, w: 3.8, h: 0.35,
    fontSize: 13, fontFace: FONT, color: COLORS.danger, bold: true, margin: 0
  });
  s.addText([
    { text: "• E. coli grow with error-prone T7 RNAP", options: { breakLine: true } },
    { text: "• T7 replicates a nanobody gene cassette", options: { breakLine: true } },
    { text: "• Mutations accumulate at rate set by T7 variant", options: { breakLine: true } },
    { text: "• 6 divisions (doublings) per cycle", options: { breakLine: true } },
    { text: "• Turbidostat maintains constant population", options: {} },
  ], {
    x: 0.7, y: 2.05, w: 3.8, h: 2.3,
    fontSize: 11, fontFace: FONT, color: COLORS.fg, bullet: true, lineSpacingMultiple: 1.4
  });

  // LZ card
  s.addShape("rectangle", {
    x: 5.3, y: 1.4, w: 4.2, h: 3.2,
    fill: { color: COLORS.cardBg }, line: { color: COLORS.border, width: 1 }
  });
  s.addShape("rectangle", { x: 5.3, y: 1.4, w: 4.2, h: 0.04, fill: { color: COLORS.success } });
  s.addText("LIGHT ZONE (LZ)", {
    x: 5.5, y: 1.55, w: 3.8, h: 0.35,
    fontSize: 13, fontFace: FONT, color: COLORS.success, bold: true, margin: 0
  });
  s.addText([
    { text: "• Cells migrate after 6 DZ divisions", options: { breakLine: true } },
    { text: "• Hill function selection: a³/(a³+K³)", options: { breakLine: true } },
    { text: "• Survival depends on affinity to antigen", options: { breakLine: true } },
    { text: "• No division in LZ (selection only)", options: { breakLine: true } },
    { text: "• Survivors return to DZ for next cycle", options: {} },
  ], {
    x: 5.5, y: 2.05, w: 3.8, h: 2.3,
    fontSize: 11, fontFace: FONT, color: COLORS.fg, bullet: true, lineSpacingMultiple: 1.4
  });
}

// =====================================================================
// SLIDE 4 — Architecture: The Cycle
// =====================================================================
{
  const s = newSlide("Introduction");
  s.addText("The GC Cycle", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  // Flow diagram as connected boxes
  const boxes = [
    { label: "Founders\n(n=50)", x: 0.5, y: 2.0, color: COLORS.accent },
    { label: "DZ Growth\n6 divisions", x: 2.3, y: 2.0, color: COLORS.danger },
    { label: "Mutation\n(T7 RNAP)", x: 4.1, y: 2.0, color: COLORS.warning },
    { label: "LZ Selection\nHill: a³/(a³+K³)", x: 5.9, y: 2.0, color: COLORS.success },
    { label: "Return to DZ\n(survivors)", x: 7.7, y: 2.0, color: COLORS.accent },
  ];

  boxes.forEach(b => {
    s.addShape("rectangle", {
      x: b.x, y: b.y, w: 1.6, h: 1.0,
      fill: { color: COLORS.cardBg }, line: { color: b.color, width: 2 }
    });
    s.addText(b.label, {
      x: b.x, y: b.y, w: 1.6, h: 1.0,
      fontSize: 10, fontFace: FONT, color: COLORS.fg, align: "center", valign: "middle"
    });
  });

  // Arrows between boxes
  for (let i = 0; i < boxes.length - 1; i++) {
    s.addShape("rectangle", {
      x: boxes[i].x + 1.6, y: 2.45, w: boxes[i+1].x - boxes[i].x - 1.6, h: 0.02,
      fill: { color: COLORS.muted }
    });
  }

  // Cycle arrow (return)
  s.addText("← Cycle repeats (140 cycles = ~7 GC days) ←", {
    x: 2.0, y: 3.3, w: 6, h: 0.35,
    fontSize: 10, fontFace: FONT, color: COLORS.accent, align: "center"
  });

  // Key parameters
  s.addText([
    { text: "Key parameters:  ", options: { bold: true } },
    { text: "N = 10,000 cells  |  L = 400 (shape space)  |  140 cycles  |  Turbidostat mode", options: {} },
  ], {
    x: 0.5, y: 4.2, w: 9, h: 0.4,
    fontSize: 10, fontFace: FONT_MONO, color: COLORS.muted, align: "left"
  });
}

// =====================================================================
// SLIDE 5 — Shape Space Model
// =====================================================================
{
  const s = newSlide("Simulation Design");
  s.addText("Shape Space & Affinity Model", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  s.addText([
    { text: "Shape space representation", options: { bold: true, breakLine: true } },
    { text: "Each cell's antibody = binary string of length L (400 bases)", options: { breakLine: true } },
    { text: "Antigen = fixed binary target string", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Affinity = Gaussian on Hamming distance:", options: { bold: true, breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "    a(x) = exp( -γ · (d(x, target) / L)² )", options: { fontFace: FONT_MONO, fontSize: 12, breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Where d(x, target) = number of mismatched positions", options: { breakLine: true } },
    { text: "γ = 105 (L=400) or 10.5 (L=40) — controls landscape steepness", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Mutation: each position flips with probability = mutation_rate", options: { bold: true, breakLine: true } },
    { text: "Expected mutations per division = mutation_rate × L", options: {} },
  ], {
    x: 0.5, y: 1.3, w: 9, h: 3.5,
    fontSize: 11, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.3, valign: "top"
  });
}

// =====================================================================
// SLIDE 6 — Selection Model
// =====================================================================
{
  const s = newSlide("Simulation Design");
  s.addText("Hill Function Selection", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  // Formula
  s.addShape("rectangle", {
    x: 1.5, y: 1.3, w: 7, h: 1.0,
    fill: { color: COLORS.cardBg }, line: { color: COLORS.accent, width: 1 }
  });
  s.addText("P(survive) = a³ / (a³ + K³)", {
    x: 1.5, y: 1.3, w: 7, h: 1.0,
    fontSize: 22, fontFace: FONT_MONO, color: COLORS.accent, align: "center", valign: "middle"
  });

  // K value table
  const selData = [
    [
      { text: "K value", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Survival at a=0.58", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Selection type", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
    ],
    ["K = 0.001", "~100%", "No selection (control)"],
    ["K = 0.05", "~99.9%", "Very weak"],
    ["K = 0.1", "~99.5%", "Weak"],
    ["K = 0.2", "~96%", "Moderate"],
    ["K = 0.3", "~88%", "Standard"],
    ["K = 10", "~0.02%", "Lethal (control)"],
  ];
  s.addTable(selData, {
    x: 1.0, y: 2.6, w: 8, h: 2.5,
    fontSize: 10, fontFace: FONT, color: COLORS.fg,
    border: { pt: 0.5, color: COLORS.border },
    colW: [2, 3, 3],
    autoPage: false,
  });
}

// =====================================================================
// SLIDE 7 — Implementation
// =====================================================================
{
  const s = newSlide("Simulation Design");
  s.addText("Implementation: Python + JAX", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  s.addText([
    { text: "Framework", options: { bold: true, color: COLORS.accent, breakLine: true } },
    { text: "Python + JAX (GPU-accelerable NumPy) on RTX 2080 Ti (11 GB VRAM)", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Architecture", options: { bold: true, color: COLORS.accent, breakLine: true } },
    { text: "Padded fixed-size arrays (Structure-of-Arrays) for GPU compatibility", options: { breakLine: true } },
    { text: "11 modules: config, state, growth, migration, selection, simulation, analysis + GPU variants", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Performance (N=10K, L=400)", options: { bold: true, color: COLORS.accent, breakLine: true } },
    { text: "CPU: ~45s/cycle at N=1M  |  GPU: 185ms/step for natural GC", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Validation", options: { bold: true, color: COLORS.accent, breakLine: true } },
    { text: "5 controls pass: zero mutation, no selection, perfect selection, low mutation, lethal selection", options: {} },
  ], {
    x: 0.5, y: 1.3, w: 9, h: 3.8,
    fontSize: 11, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.35, valign: "top"
  });
}

// =====================================================================
// SLIDE 8 — First Runs: Turbidostat v2
// =====================================================================
{
  const s = newSlide("First Results");
  s.addText("First Working Simulation: Turbidostat v2", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  const resData = [
    [
      { text: "Version", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Mode", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Mean Aff", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Max Aff", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Issue", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
    ],
    ["v1 (batch)", "Random 10% transfer", "0.13→0.15", "0.88", "Selection diluted"],
    [
      { text: "v2 (turbidostat)", options: { bold: true, color: COLORS.success } },
      "Division-triggered",
      { text: "0.13→0.53", options: { bold: true, color: COLORS.success } },
      { text: "1.00", options: { bold: true, color: COLORS.success } },
      { text: "Working ✓", options: { color: COLORS.success } },
    ],
  ];
  s.addTable(resData, {
    x: 0.5, y: 1.3, w: 9, h: 1.2,
    fontSize: 11, fontFace: FONT, color: COLORS.fg,
    border: { pt: 0.5, color: COLORS.border },
    autoPage: false,
  });

  s.addText([
    { text: "Key insight: ", options: { bold: true, color: COLORS.warning } },
    { text: "Division-triggered migration (cells move to LZ after 6 doublings rather than random transfer) makes selection work. Affinity increases from 0.13 to 0.53 — genuine maturation.", options: {} },
  ], {
    x: 0.5, y: 2.8, w: 9, h: 1.0,
    fontSize: 12, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.3
  });
}

// =====================================================================
// SLIDE 9 — N=1M Run: Muller's Ratchet
// =====================================================================
{
  const s = newSlide("First Results");
  s.addText("N=1M Run — Muller's Ratchet", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  addImageSafe(s, "results/archive/cpu_1M_140cyc.png", {
    x: 0.3, y: 1.2, w: 5.5, h: 3.5
  });

  s.addShape("rectangle", {
    x: 6.0, y: 1.2, w: 3.7, h: 3.5,
    fill: { color: COLORS.cardBg }, line: { color: COLORS.border, width: 1 }
  });
  s.addText([
    { text: "Parameters", options: { bold: true, color: COLORS.accent, breakLine: true } },
    { text: "N = 1,000,000", options: { breakLine: true } },
    { text: "L = 400, mut_rate = 5×10⁻⁴", options: { breakLine: true } },
    { text: "140 cycles, 108 min runtime", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Result", options: { bold: true, color: COLORS.danger, breakLine: true } },
    { text: "Mean aff: 0.58 → 0.29", options: { breakLine: true } },
    { text: "Max aff: 0.80 → 0.42", options: { breakLine: true } },
    { text: "Top clone: 2% → 80%", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Diagnosis: mutation load\noverwhelms selection\n(Muller's ratchet)", options: { bold: true, color: COLORS.warning } },
  ], {
    x: 6.2, y: 1.4, w: 3.3, h: 3.1,
    fontSize: 10, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.3, valign: "top"
  });
}

// =====================================================================
// SLIDE 10 — Parameter Sweep L=400
// =====================================================================
{
  const s = newSlide("First Results");
  s.addText("Parameter Sweep: mutation_rate × hill_k", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  addImageSafe(s, "results/sweep/sweep_heatmap.png", {
    x: 0.3, y: 1.1, w: 9.4, h: 3.5
  });

  s.addText("L=400, N=10K, 140 cycles  |  4×4 grid  |  1 MATURATION, 1 STABLE, 14 DEGRADATION", {
    x: 0.5, y: 4.7, w: 9, h: 0.3,
    fontSize: 10, fontFace: FONT_MONO, color: COLORS.muted, align: "center"
  });
}

// =====================================================================
// SLIDE 11 — Sweep Analysis
// =====================================================================
{
  const s = newSlide("First Results");
  s.addText("Why Stronger Selection Makes Things Worse", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  s.addText([
    { text: "Counter-intuitive result:", options: { bold: true, color: COLORS.warning, breakLine: true } },
    { text: "K=0.05 (strong selection) degrades FASTER than K=0.3 (weak selection)", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Mechanism — the death spiral:", options: { bold: true, color: COLORS.danger, breakLine: true } },
    { text: "1. Strong selection kills low-affinity cells", options: { breakLine: true } },
    { text: "2. Reduced population → less diversity", options: { breakLine: true } },
    { text: "3. Mutations mostly deleterious at these rates", options: { breakLine: true } },
    { text: "4. Best clone degrades → gets killed → spiral continues", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Why weak selection works:", options: { bold: true, color: COLORS.success, breakLine: true } },
    { text: "K=0.3 gives ~88% survival — keeps population large and diverse.", options: { breakLine: true } },
    { text: "Large population = more chances for rare beneficial mutations to arise.", options: { breakLine: true } },
    { text: "Selection is gentle enough to favor but not destroy.", options: {} },
  ], {
    x: 0.5, y: 1.2, w: 9, h: 3.8,
    fontSize: 11, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.3, valign: "top"
  });
}

// =====================================================================
// SLIDE 12 — Validation Controls
// =====================================================================
{
  const s = newSlide("Validation");
  s.addText("5 Simulation Validation Controls", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  const ctrlData = [
    [
      { text: "#", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Control", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Expected", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Δ Affinity", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Pop", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Verdict", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
    ],
    ["1", "Zero mutation, K=0.3", "Aff rises (pure selection)", { text: "+0.11", options: { bold: true, color: COLORS.success } }, "9,253", { text: "PASS ✓", options: { color: COLORS.success } }],
    ["2", "No selection (K=0.001)", "Pop stable, aff drifts", { text: "-0.05", options: { color: COLORS.warning } }, "10,000", { text: "PASS ✓", options: { color: COLORS.success } }],
    ["3", "DE top-1%, no mutation", "Single best clone", { text: "0.00", options: {} }, "100", { text: "PASS ✓", options: { color: COLORS.success } }],
    ["4", "Low mut (10⁻⁵) + K=0.3", "Slow maturation", { text: "+0.09", options: { bold: true, color: COLORS.success } }, "9,168", { text: "PASS ✓", options: { color: COLORS.success } }],
    ["5", "Lethal selection (K=10)", "Pop collapse", { text: "-0.01", options: { color: COLORS.danger } }, "3", { text: "PASS ✓", options: { color: COLORS.success } }],
  ];
  s.addTable(ctrlData, {
    x: 0.3, y: 1.2, w: 9.4, h: 2.5,
    fontSize: 10, fontFace: FONT, color: COLORS.fg,
    border: { pt: 0.5, color: COLORS.border },
    colW: [0.4, 2.5, 2, 1.5, 1, 1],
    autoPage: false,
  });

  // Key control plots
  addImageSafe(s, "results/controls/1_zero_mutation.png", { x: 0.3, y: 3.8, w: 3.0, h: 1.6 });
  addImageSafe(s, "results/controls/4_low_mut_moderate_sel.png", { x: 3.5, y: 3.8, w: 3.0, h: 1.6 });
  addImageSafe(s, "results/controls/5_lethal_selection.png", { x: 6.7, y: 3.8, w: 3.0, h: 1.6 });
}

// =====================================================================
// SLIDE 13 — Mutation Rate Calibration
// =====================================================================
{
  const s = newSlide("Validation");
  s.addText("Mutation Rate Calibration Error", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  // Warning box
  s.addShape("rectangle", {
    x: 0.5, y: 1.2, w: 9, h: 0.9,
    fill: { color: "3D2200" }, line: { color: COLORS.warning, width: 1 }
  });
  s.addText("⚠  First sweep rates (10⁻⁴ – 10⁻³/bp/div) were 10–100× ABOVE actual T7 variant range", {
    x: 0.7, y: 1.2, w: 8.6, h: 0.9,
    fontSize: 13, fontFace: FONT, color: COLORS.warning, bold: true, align: "left", valign: "middle"
  });

  s.addText([
    { text: "This explains why almost everything degraded —", options: { bold: true, breakLine: true } },
    { text: "we were running at impossibly high mutation rates.", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Control 4 proved maturation works at 10⁻⁵ — which IS a real T7 rate.", options: { color: COLORS.success, breakLine: true } },
  ], {
    x: 0.5, y: 2.3, w: 9, h: 1.2,
    fontSize: 12, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.3
  });
}

// =====================================================================
// SLIDE 14 — T7 Variant Rate Table
// =====================================================================
{
  const s = newSlide("Validation");
  s.addText("T7 Polymerase Variant Rates", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  const t7Data = [
    [
      { text: "Variant", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Description", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Rate (/bp/div)", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "mut/gene/div", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "In sweep?", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
    ],
    [{ text: "WT E. coli", options: { color: COLORS.muted } }, "Normal replication", "10⁻⁹", "4×10⁻⁷", { text: "Baseline", options: { color: COLORS.muted } }],
    ["T7 V1", "WT + exo + thioredoxin", "10⁻⁸", "4×10⁻⁶", { text: "NEW ✓", options: { color: COLORS.success } }],
    ["T7 V2", "WT + exonuclease", "10⁻⁷", "4×10⁻⁵", { text: "NEW ✓", options: { color: COLORS.success } }],
    ["T7 V3", "WT exonuclease⁻", "10⁻⁶", "4×10⁻⁴", { text: "NEW ✓", options: { color: COLORS.success } }],
    ["T7 V4", "Error-prone exo⁻", "10⁻⁵", "4×10⁻³", { text: "NEW ✓", options: { color: COLORS.success } }],
    [{ text: "T7 V5", options: { bold: true } }, "Highest error", { text: "10⁻⁴", options: { bold: true } }, "0.04", { text: "= old 0.0001", options: { color: COLORS.warning } }],
  ];
  s.addTable(t7Data, {
    x: 0.3, y: 1.2, w: 9.4, h: 3.0,
    fontSize: 10, fontFace: FONT, color: COLORS.fg,
    border: { pt: 0.5, color: COLORS.border },
    colW: [1.2, 2.5, 1.8, 1.8, 1.5],
    autoPage: false,
  });

  s.addText("The previous sweep's ONLY maturation point (rate=0.0001) = T7 V5 (highest error variant)", {
    x: 0.5, y: 4.4, w: 9, h: 0.5,
    fontSize: 11, fontFace: FONT, color: COLORS.warning, bold: true, align: "center"
  });
}

// =====================================================================
// SLIDE 15 — L-Scaling
// =====================================================================
{
  const s = newSlide("L-Scaling Validation");
  s.addText("L=400 → L=40: Scaling for GPU", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  const lData = [
    [
      { text: "Parameter", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "L=400", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "L=40", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
      { text: "Rule", options: { bold: true, color: COLORS.accent, fill: { color: COLORS.dimBg } } },
    ],
    ["shape_space_dim", "400", "40", "÷10"],
    ["mutation_rate", "varies", "×10", "rate × L constant"],
    ["affinity_gamma (γ)", "105", "10.5", "÷10"],
    ["initial_hamming", "50-100", "5-10", "÷10"],
    ["N, cycles, dz_div", "same", "same", "unchanged"],
  ];
  s.addTable(lData, {
    x: 0.5, y: 1.2, w: 9, h: 2.2,
    fontSize: 10, fontFace: FONT, color: COLORS.fg,
    border: { pt: 0.5, color: COLORS.border },
    colW: [2.5, 2, 2, 2.5],
    autoPage: false,
  });

  s.addText([
    { text: "Why L=40?  ", options: { bold: true, color: COLORS.accent } },
    { text: "At L=40, N=10⁷ fits in 1.6 GB VRAM vs 16 GB at L=400. This enables GPU-scale experiments on the RTX 2080 Ti.", options: {} },
  ], {
    x: 0.5, y: 3.6, w: 9, h: 0.6,
    fontSize: 11, fontFace: FONT, color: COLORS.fg
  });
}

// =====================================================================
// SLIDE 16 — L=400 vs L=40 Comparison
// =====================================================================
{
  const s = newSlide("L-Scaling Validation");
  s.addText("L=400 vs L=40: Heatmap Comparison", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  addImageSafe(s, "results/sweep/sweep_heatmap.png", { x: 0.1, y: 1.1, w: 4.8, h: 2.6 });
  addImageSafe(s, "results/sweep_L40/sweep_L40_heatmap.png", { x: 5.1, y: 1.1, w: 4.8, h: 2.6 });

  s.addText("L=400 (CPU)", { x: 0.1, y: 3.7, w: 4.8, h: 0.3, fontSize: 10, fontFace: FONT, color: COLORS.muted, align: "center" });
  s.addText("L=40 (GPU validation)", { x: 5.1, y: 3.7, w: 4.8, h: 0.3, fontSize: 10, fontFace: FONT, color: COLORS.muted, align: "center" });

  s.addText([
    { text: "✓ Same qualitative pattern", options: { color: COLORS.success, bold: true } },
    { text: "  |  Maturation boundary at same position  |  Quantitative differences explained by L discretisation", options: { color: COLORS.muted } },
  ], {
    x: 0.3, y: 4.2, w: 9.4, h: 0.5,
    fontSize: 10, fontFace: FONT, color: COLORS.fg, align: "center"
  });
}

// =====================================================================
// SLIDE 17 — Corrected T7 Rate Sweep — Heatmap
// =====================================================================
{
  const s = newSlide("Corrected Results");
  s.addText("Corrected Sweep: Real T7 Variant Rates", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  addImageSafe(s, "results/sweep_T7_rates/T7_rates_heatmap.png", {
    x: 0.3, y: 1.1, w: 9.4, h: 3.5
  });

  s.addText("6 biologically grounded rates × 4 hill_k = 24 runs  |  L=40, N=10K, 140 cycles", {
    x: 0.5, y: 4.7, w: 9, h: 0.3,
    fontSize: 10, fontFace: FONT_MONO, color: COLORS.muted, align: "center"
  });
}

// =====================================================================
// SLIDE 18 — Key Insight
// =====================================================================
{
  const s = newSlide("Corrected Results");
  s.addText("Key Insight: Maturation at Biologically Relevant Rates", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 22, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  // Big success box
  s.addShape("rectangle", {
    x: 0.8, y: 1.3, w: 8.4, h: 1.2,
    fill: { color: "0A2E1A" }, line: { color: COLORS.success, width: 2 }
  });
  s.addText("At real T7 rates (≤10⁻⁵/bp/div), the simulation consistently\nproduces affinity maturation — the system works!", {
    x: 0.8, y: 1.3, w: 8.4, h: 1.2,
    fontSize: 16, fontFace: FONT, color: COLORS.success, bold: true, align: "center", valign: "middle"
  });

  s.addText([
    { text: "What we learned:", options: { bold: true, color: COLORS.accent, breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "1. Mutation rate is the dominant parameter", options: { bold: true, breakLine: true } },
    { text: "   Rate determines maturation vs degradation. Selection strength is secondary.", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "2. Weaker selection consistently outperforms stronger selection", options: { bold: true, breakLine: true } },
    { text: "   K=0.3 (~88% survival) > K=0.05 (~99.9% survival) at every mutation rate.", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "3. There exists a critical mutation rate threshold", options: { bold: true, breakLine: true } },
    { text: "   Below this threshold → maturation. Above → Muller's ratchet.", options: {} },
  ], {
    x: 0.8, y: 2.7, w: 8.4, h: 2.5,
    fontSize: 11, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.25, valign: "top"
  });
}

// =====================================================================
// SLIDE 19 — Next Steps
// =====================================================================
{
  const s = newSlide("Outlook");
  s.addText("Next Steps", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  const steps = [
    { label: "HIGH", color: COLORS.danger, items: [
      "GPU scaling to N=10⁷ — does larger pop shift maturation boundary?",
      "GC vs directed evolution — code ready, run on T7 rate grid",
    ]},
    { label: "MEDIUM", color: COLORS.warning, items: [
      "DZ/LZ cycling speed sweep (dz_divisions ∈ {2,3,4,6,8,12})",
      "Initial library affinity sweep — does quality matter?",
      "Multi-seed validation (5-10 seeds at boundary)",
    ]},
    { label: "FUTURE", color: COLORS.muted, items: [
      "Multi-epitope (3 antigens) — can GC maintain parallel maturation?",
      "96-well parallel simulation",
      "Antigen co-evolution",
    ]},
  ];

  let yOff = 1.3;
  steps.forEach(group => {
    s.addText(group.label, {
      x: 0.5, y: yOff, w: 1.2, h: 0.3,
      fontSize: 9, fontFace: FONT, color: group.color, bold: true, margin: 0,
      charSpacing: 3
    });
    group.items.forEach(item => {
      s.addText("• " + item, {
        x: 1.7, y: yOff, w: 7.8, h: 0.3,
        fontSize: 10, fontFace: FONT, color: COLORS.fg, margin: 0
      });
      yOff += 0.3;
    });
    yOff += 0.25;
  });
}

// =====================================================================
// SLIDE 20 — Open Questions
// =====================================================================
{
  const s = newSlide("Outlook");
  s.addText("Open Scientific Questions", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 24, fontFace: FONT, color: COLORS.fg, bold: true, margin: 0
  });

  const questions = [
    "Q1: How large must N be for reliable maturation?",
    "Q2: What is the max mutation rate for maturation at a given N?",
    "Q3: How does DZ/LZ cycling frequency affect mutation load?",
    "Q4: Does the GC architecture outperform directed evolution?",
    "Q5: How realistic is Hill selection vs bead binding?",
    "Q6: Can the system mature against multiple epitopes?",
    "Q9: How sensitive is maturation to landscape shape?",
    "Q11: How much does initial library affinity matter?",
  ];

  s.addText(
    questions.map((q, i) => ({
      text: q,
      options: {
        bullet: true,
        breakLine: i < questions.length - 1,
        color: i < 4 ? COLORS.fg : COLORS.muted,
        bold: i < 4,
      }
    })),
    {
      x: 0.5, y: 1.2, w: 9, h: 3.8,
      fontSize: 11, fontFace: FONT, color: COLORS.fg, lineSpacingMultiple: 1.6, valign: "top"
    }
  );
}

// ─── Save ────────────────────────────────────────────────────────────

const outPath = path.join(__dirname, "GC_Simulation_Lab_Meeting.pptx");
pres.writeFile({ fileName: outPath })
  .then(() => console.log(`✅ Presentation saved to: ${outPath}`))
  .catch(err => console.error("Error:", err));
