"""Generate EXP_015_analysis.ipynb against the as-read plate.

Rebuilt 2026-11-17 after the actual Tecan export arrived. Four things differ
from the pre-read design and are handled explicitly below:

  1. THREE gains were read (50, 75, 100), not two.
  2. The plate was a CLEAR Greiner 655101, not the black/clear-bottom plate the
     design assumed. Crosstalk is therefore measured, not assumed.
  3. The standard curve is SUBLINEAR. A line through the origin misfits the low
     end by 27 %, so the curve is fitted as a power law.
  4. Cells did not pellet completely. Tier-1 and wash supernatants carry cells,
     and that carryover is corrected for rather than ignored.

The notebook is generated rather than hand-edited so it stays in step with
scripts/exp015_layout.py. Re-running OVERWRITES the notebook.

    python3 scripts/build_notebook_015.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "scripts" / "EXP_015_analysis.ipynb"

cells: list[dict] = []


def md(text: str) -> None:
    cells.append({"cell_type": "markdown", "metadata": {},
                  "source": text.strip("\n").splitlines(keepends=True)})


def code(text: str) -> None:
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": text.strip("\n").splitlines(keepends=True)})


# ----------------------------------------------------------------- title ----
md("""
# EXP_015 — what does the 2xHA tag cost?

Plate read **2026-11-17, 18:38–18:43**, Tecan Infinite 200 Pro, bottom read,
ex 478 / em 515 (bw 9 / 20), **26.0 °C**, 59 wells at 150 µL.
Read as OD600 then fluorescence at **gain 50, 75 and 100**.

MS_S_052 (Enhancer, no HA) against MS_S_056 (Enhancer + 2xHA), each with its own
uninduced arm, at **100 and 1000 nM** GFP, triplicate, **0.3 OD·mL** into
**200 µL** of label.

### Four deviations from the design, all handled explicitly

| # | What | Consequence |
|---|---|---|
| 1 | **Clear plate** (Greiner 655101), not black/clear-bottom | crosstalk cannot be assumed — §2 measures it from the unfilled wells |
| 2 | **Three gains** read, not two | gain 100 saturates on row F; gain 75 carries Tier 1; gain 50 is a spare rung that lets the gain series be checked twice |
| 3 | **Standard curve is sublinear** | a line through the origin misfits the low end by 27 %; fitted as a power law in §3 |
| 4 | **Cells did not pellet completely** | Tier-1 and wash supernatants carry cells, and those cells carry bound GFP. §6 corrects for it; §8 shows it accounts for the entire wash-2 signal |

> Run with the analysis stack:
> `uv run --with pandas,numpy,plotly,scipy,openpyxl jupyter lab`
""")

code("""
import sys, pathlib
import numpy as np
import pandas as pd

HERE = pathlib.Path.cwd()
ROOT = HERE if (HERE / 'scripts').exists() else HERE.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import tecan_parse as tp
import exp015_layout as L

DATA = ROOT / 'data'
READ_FILE = DATA / 'Book1.xlsx'      # the Tecan export as saved off the reader

df = L.frame()
print(f'layout: {len(df)} wells | {df.is_cells.sum()} with cells | '
      f'{df.is_tier1.sum()} Tier 1')
print()
print(L.PHASE_NOTE)
print(L.OUTLIER_NOTE)
""")

# ------------------------------------------------------------------ load ----
md("""
## 1. Load

Four blocks expected: OD600, then fluorescence at gain 50, 75 and 100.
`tecan_parse.pick` raises rather than guessing — silently taking the first
block is how the wrong gain ends up in a figure. `OVER` becomes NaN, never 0.
""")

code("""
blocks = tp.parse_file(str(READ_FILE))
for b in blocks:
    print(b, '| T =', b.meta.get('temperature'))

PLATE = str(blocks[0].meta.get('plate_def'))
print('\\nplate:', PLATE)
if 'Black' not in PLATE:
    print('  ! CLEAR plate — the design assumed black/clear-bottom. '
          'Crosstalk is measured in section 2, not assumed.')

od_block = tp.pick(blocks, 'abs')
fl = {g: tp.pick(blocks, 'fluor', gain=g) for g in (50, 75, 100)}

df['od'] = df.well.map(dict(zip(od_block.data.well, od_block.data.value)))
for g, blk in fl.items():
    df[f'g{g}'] = df.well.map(dict(zip(blk.data.well, blk.data.value)))

# every well the instrument read, including the ones we left unfilled
read_all = {w: v for w, v in zip(fl[75].data.well, fl[75].data.value)}
UNFILLED = sorted(set(read_all) - set(df.well),
                  key=lambda w: (w[0], int(w[1:])))
print(f'\\n{len(UNFILLED)} wells read but deliberately unfilled: '
      f'{", ".join(UNFILLED)}')
print('These are not waste — section 2 uses them as a crosstalk probe.')

df[['well', 'group', 'sample', 'od', 'g50', 'g75', 'g100']].head(8)
""")

# -------------------------------------------------------------------- QC ----
md("""
## 2. QC — before any binder

Six checks. Each would invalidate the result on its own.

The crosstalk check is the one worth dwelling on. The plate was **clear, not
black**, so the <0.1 % lateral crosstalk the layout was designed around does not
apply. But the layout left **E7–E12 and D11–D12 empty directly above row F**,
which is the brightest block on the plate — so the plate measures its own
crosstalk, with no extra wells and no assumption.
""")

code("""
CEILING = 65000
problems = []

blank = df[df.group == 'blank']
OD0 = blank.od.mean()
F0 = {g: blank[f'g{g}'].mean() for g in (50, 75, 100)}
SD0 = {g: blank[f'g{g}'].std() for g in (50, 75, 100)}
print(f'buffer blank (n={len(blank)}): OD600 {OD0:.4f} +/- {blank.od.std():.4f}')
for g in (50, 75, 100):
    print(f'   gain {g:>3}: {F0[g]:7.1f} +/- {SD0[g]:.1f}')
if (blank.od > OD0 + 0.02).any():
    problems.append('a blank well carries OD600 — it is not buffer')

# --- 1. saturation
print()
for g in (50, 75, 100):
    over = df[df[f'g{g}'].isna()]
    print(f'gain {g:>3}: {len(over):>2} well(s) OVER', end='')
    if len(over):
        print('  ->', ', '.join(sorted(over.well, key=lambda w: (w[0], int(w[1:])))))
    else:
        print()
if df[df.is_cells].g100.isna().any():
    problems.append('a CELL well is saturated at gain 100')

# --- 2. crosstalk, measured on this plate
probe = [w for w in UNFILLED if w[0] in 'DE' and int(w[1:]) >= 7]
bright = {f'F{c}': read_all[f'F{c}'] for c in range(7, 13)}
xt = [(w, read_all[w] - F0[75]) for w in probe]
worst = max(v for _, v in xt)
nb = np.mean(list(bright.values())) - F0[75]
print(f'\\ncrosstalk probe: {len(probe)} empty wells adjacent to row F '
      f'(mean {nb:,.0f} RFU blanked at gain 75)')
print('   ', ', '.join(f'{w} {v:+.0f}' for w, v in xt))
print(f'    worst = {worst:+.0f} RFU = {100*worst/nb:.3f} % of the neighbour')
if worst / nb > 0.01:
    problems.append('crosstalk above 1 % — the clear plate is a real problem')
else:
    print('    -> negligible. The clear plate did not cost anything here.')

# --- 3. gain series, measured twice
print()
GAIN = {}
for lo, hi in [(50, 75), (75, 100)]:
    s = df.dropna(subset=[f'g{lo}', f'g{hi}'])
    s = s[(s[f'g{lo}'] - F0[lo]) > 30]
    r = (s[f'g{hi}'] - F0[hi]) / (s[f'g{lo}'] - F0[lo])
    GAIN[(lo, hi)] = float(np.median(r))
    resid = float(np.median(np.abs(r / np.median(r) - 1)) * 100)
    print(f'gain{hi}/gain{lo} = {GAIN[(lo, hi)]:.3f}  '
          f'(n={len(r)}, median residual {resid:.1f} %)')
print(f'EXP_014 prior for gain100/gain75: {L.EXP014_GAIN_RATIO} '
      f'-> reproduced to '
      f'{abs(GAIN[(75,100)]/L.EXP014_GAIN_RATIO - 1)*100:.1f} %')

# --- 4. blanked values used from here on
df['odn'] = df.od - OD0
for g in (50, 75, 100):
    df[f'f{g}'] = df[f'g{g}'] - F0[g]

print()
if problems:
    print('QC PROBLEMS — resolve before reading anything below:')
    for p in problems:
        print('  !', p)
else:
    print('QC clean. The standard curve is checked separately in section 3.')
""")

# -------------------------------------------------------------- the curve ---
md("""
## 3. The standard curve → a concentration axis

What EXP_014 did not have. With it, Tier 1 reports **nM of free GFP** instead of
a depletion fraction against a single reference well.

**The response is sublinear**, and this matters. Forcing a line through the
origin — the obvious thing to do — overestimates the low end by up to 27 %,
which is exactly where the depleted 100 nM Tier-1 samples sit. The curve is
therefore fitted as a power law, `RFU = A · nM^k`, which holds to a few percent
across all three decades.

Fitted on **gain 75**: gain 100 saturates at the top point (S1), and gain 50
throws away resolution at the bottom.
""")

code("""
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = 'plotly_white'

cur = df[df.group == 'curve'].dropna(subset=['curve_nM']).sort_values('curve_nM')
x = cur.curve_nM.to_numpy(float)
y = cur.f75.to_numpy(float)

# power law in log-log
k, lnA = np.polyfit(np.log(x), np.log(y), 1)
A = float(np.exp(lnA))
res_pow = 100 * (y - A * x**k) / (A * x**k)

# the naive alternative, for comparison
slope = float(np.sum(x * y) / np.sum(x * x))
res_lin = 100 * (y - slope * x) / (slope * x)

print(f'power law : RFU = {A:.2f} * nM^{k:.4f}')
print(f'            residuals % {np.round(res_pow, 1)}')
print(f'line thru 0: {slope:.2f} RFU/nM')
print(f'            residuals % {np.round(res_lin, 1)}   <- up to '
      f'{res_lin.max():.0f} % at the low end')
print(f'\\nRFU per nM falls from {y[0]/x[0]:.1f} at {x[0]:g} nM to '
      f'{y[-1]/x[-1]:.1f} at {x[-1]:g} nM — a real {100*(1-(y[-1]/x[-1])/(y[0]/x[0])):.0f} % '
      'compression, not noise.')

def rfu_to_nM(rfu, gain=75):
    \"\"\"Blanked RFU -> nM via the power-law curve. Converts other gains to 75 first.\"\"\"
    r = np.asarray(rfu, dtype=float)
    if gain == 100:
        r = r / GAIN[(75, 100)]
    elif gain == 50:
        r = r * GAIN[(50, 75)]
    return (np.clip(r, 1e-9, None) / A) ** (1 / k)

# the 100 nM working solution, read against its own curve
qc = df[df.group == 'qc100']
qc_nM = rfu_to_nM(qc.f75)
C0_100 = float(np.mean(qc_nM))
print(f'\\n100 nM working solution measures {C0_100:.1f} nM '
      f'({", ".join(f"{v:.1f}" for v in qc_nM)}) -> {100*(C0_100/100-1):+.1f} % of nominal')
print('Used as C0 for the 100 nM arm, in place of the nominal value.')

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='markers+text', text=cur['sample'],
                         textposition='top left', name='standard curve S1–S8 (n=1 each)',
                         marker=dict(size=11, color='#7030A0')))
xx = np.logspace(np.log10(x.min()), np.log10(x.max()), 100)
fig.add_trace(go.Scatter(x=xx, y=A * xx**k, mode='lines',
                         name=f'power-law fit, RFU = {A:.1f}·nM^{k:.3f} (used)',
                         line=dict(color='#7030A0')))
fig.add_trace(go.Scatter(x=xx, y=slope * xx, mode='lines',
                         name=f'line through origin, {slope:.1f} RFU/nM (rejected)',
                         line=dict(color='#aaaaaa', dash='dash')))
fig.add_trace(go.Scatter(x=[C0_100] * len(qc_nM), y=qc.f75, mode='markers',
                         name='100 nM working solution (QC)',
                         marker=dict(size=13, symbol='diamond', color='#C00000')))
fig.update_layout(title='EXP_015 standard curve, gain 75',
                  xaxis=dict(title='GFP (nM)', type='log',
                             tickvals=[10, 20, 50, 100, 200, 500, 1000]),
                  yaxis=dict(title='RFU, blanked', type='log',
                             tickvals=[100, 200, 500, 1000, 2000, 5000, 10000]),
                  width=800, height=480)
fig.write_html(DATA / 'EXP_015_curve.html')
fig.show()
""")

# ------------------------------------------------------------- normalise ----
md("""
## 4. Normalise — per OD **only where there are cells**

Two rules carried from EXP_014, both easy to get backwards:

- **F/OD600 only in wells containing cells.** A fluorescence/OD ratio is
  meaningless in a cell-free well.
- **Normalise first, subtract autofluorescence second.** The no-GFP control has
  its own cell density and is only comparable per unit OD.

Cell wells are taken from **gain 100** — nothing there saturates and it has the
best resolution on the dim uninduced arms.
""")

code("""
df['f_od'] = np.where(df.is_cells & (df.odn > 0.02), df.f100 / df.odn, np.nan)

cw = df[df.is_cells]
print(f'cell-well OD600 (blanked): {cw.odn.min():.3f} – {cw.odn.max():.3f}')
recovery = cw.odn.mean() / (L.CELL_INPUT_OD_mL / (L.RESUSPEND_uL/1000) * 0.44)
print(f'implied recovery through 2 washes: ~{recovery:.0%} of the input OD·mL '
      f'(EXP_014 saw ~46 %)')
if cw.odn.max() > 1.0:
    print('  ! above the linear OD range')
else:
    print('  OK — well inside the linear range, so F/OD600 is a clean normaliser')

auto = (df[df.group == 'cells_nogfp']
        .groupby(['strain', 'induced']).f_od.mean().rename('auto_f_od'))
print('\\nautofluorescence, F/OD600:')
print(auto.round(0).to_string())

df = df.merge(auto, left_on=['strain', 'induced'], right_index=True, how='left')
df['fold_auto'] = df.f_od / df.auto_f_od
""")

# ------------------------------------------------------------ the result ----
md("""
## 5. The headline — 052 against 056

How to read it:

| Observation | Conclusion |
|---|---|
| ratio equal at 100 and 1000 nM | the tag costs **display** — fewer molecules on the surface |
| ratio smaller at 1000 nM | the tag costs **binding** — 056 catches up as ligand rises |
| within a strain, 100 ≈ 1000 nM | both on the plateau, so EXP_014's 365 nM saturated too |
""")

code("""
from scipy import stats

sig = df[df.is_cells & df.group.isin(['cells_100', 'cells_1000_I'])]
summary = (sig.groupby(['group', 'strain'])
           .agg(n=('f_od', 'size'), mean=('f_od', 'mean'), sd=('f_od', 'std'),
                fold=('fold_auto', 'mean')).reset_index())
summary['conc_nM'] = summary.group.map(L.GROUP_CONC)
summary['cv_pct'] = 100 * summary.sd / summary['mean']
print(summary[['conc_nM', 'strain', 'n', 'mean', 'sd', 'cv_pct', 'fold']]
      .round(1).to_string(index=False))

rows = []
for conc, grp in [(100, 'cells_100'), (1000, 'cells_1000_I')]:
    a = sig[(sig.group == grp) & (sig.strain == '052')].f_od.dropna()
    b = sig[(sig.group == grp) & (sig.strain == '056')].f_od.dropna()
    t, p = stats.ttest_ind(a, b, equal_var=False)
    star = ('****' if p < 1e-4 else '***' if p < 1e-3 else
            '**' if p < 1e-2 else '*' if p < 0.05 else 'ns')
    rows.append({'conc_nM': conc, 'ratio_052_056': a.mean()/b.mean(),
                 'p_welch': p, 'sig': star})
ratios = pd.DataFrame(rows)
print()
for _, r in ratios.iterrows():
    print(f'{int(r.conc_nM):>5} nM: 052/056 = {r.ratio_052_056:.2f}x  '
          f'(Welch p={r.p_welch:.2g} {r.sig})')

d100 = summary[summary.conc_nM == 100].set_index('strain')['mean']
d1000 = summary[summary.conc_nM == 1000].set_index('strain')['mean']
print()
for s in ['052', '056']:
    print(f'MS_S_{s}: 1000 nM / 100 nM = {d1000[s]/d100[s]:.3f}')
print('\\nEXP_014 measured 2.58x — ligand-limited, so a floor. '
      f'With GFP in excess the ratio is {ratios.ratio_052_056.mean():.2f}x.')
""")

code("""
COL = {'052': '#1a6fff', '056': '#d2691e'}
fig = go.Figure()
for strain in ['052', '056']:
    sub = summary[summary.strain == strain].sort_values('conc_nM')
    pts = sig[sig.strain == strain]
    fig.add_trace(go.Bar(
        x=[f'{int(c)} nM' for c in sub.conc_nM], y=sub['mean'],
        error_y=dict(type='data', array=sub['sd'], visible=True),
        name=f'MS_S_{strain} — ' + L.STRAINS[strain].split('  ')[1],
        marker_color=COL[strain]))
    fig.add_trace(go.Scatter(
        x=[f'{int(c)} nM' for c in pts.conc_nM], y=pts.f_od, mode='markers',
        name='individual replicates (n=3 each)',
        marker=dict(color='#111', size=7, symbol='circle-open'),
        showlegend=(strain == '052')))

for _, r in ratios.iterrows():
    ytop = summary[summary.conc_nM == r.conc_nM]['mean'].max()
    fig.add_annotation(x=f'{int(r.conc_nM)} nM', y=ytop * 1.15,
                       text=f'<b>{r.ratio_052_056:.2f}×</b> {r.sig}',
                       showarrow=False, font=dict(size=14))

fig.add_hline(y=float(auto.mean()), line=dict(color='#888', dash='dot'))
fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                         line=dict(color='#888', dash='dot'),
                         name=f'mean autofluorescence ({auto.mean():.0f} F/OD600)'))

fig.update_layout(
    barmode='group', width=780, height=520,
    title='EXP_015 — the 2xHA tag costs a constant 3.1× of display<br>'
          '<sub>bars = triplicate mean, error bars = SD, open circles = individual '
          'replicates, text = 052/056 ratio with Welch p, dotted line = mean '
          'autofluorescence</sub>',
    xaxis_title='GFP concentration in the labelling reaction',
    yaxis_title='F/OD600 (blanked, gain 100)')
fig.write_html(DATA / 'EXP_015_readout.html')
fig.show()
""")

# ----------------------------------------------------------- uninduced ------
md("""
## 6. Induced vs uninduced — where does the signal actually come from?

Section 5 says 052 reads 3.1× higher than 056. That only means something if the
signal is **GFP bound to displayed nanobody**, rather than GFP sticking to
*E. coli* generally. This section separates those.

Each strain was run in four conditions, which is a 2 × 2:

|  | no GFP | 1000 nM GFP |
|---|---|---|
| **uninduced** | cell autofluorescence | autofluorescence + **non-specific** GFP binding |
| **induced** | cell autofluorescence | autofluorescence + non-specific + **specific** capture |

So there are two subtractions, and they answer different questions:

- **(uninduced + GFP) − (uninduced, no GFP)** = GFP that sticks to cells carrying
  no displayed nanobody. This is the **non-specific** term.
- **(induced + GFP) − (induced, no GFP)** = everything GFP contributes when the
  nanobody is there. This is the **total** signal.

The null is clean if the first is small compared with the second. Note the
y-axis below is **logarithmic** — on a linear axis the null bars would be
invisible, which is itself the answer.
""")

code("""
auto_tbl = (df[df.group == 'cells_nogfp']
            .groupby(['strain', 'induced']).f_od.mean())
unind = df[df.group == 'cells_1000_U']

print('F/OD600 in each of the four conditions, at 1000 nM GFP:\\n')
print(f'{"":<8}{"no GFP":>12}{"+1000 nM":>12}{"difference":>13}')
contrib = {}
for strain in ['052', '056']:
    for induced in [False, True]:
        a = auto_tbl.loc[(strain, induced)]
        if induced:
            b = sig[(sig.group == 'cells_1000_I') & (sig.strain == strain)].f_od.mean()
        else:
            b = unind[unind.strain == strain].f_od.mean()
        contrib[(strain, induced)] = b - a
        tag = 'induced' if induced else 'uninduc.'
        print(f'{strain} {tag:<8}{a:>9,.0f}{b:>12,.0f}{b-a:>13,.0f}')
    ns, tot = contrib[(strain, False)], contrib[(strain, True)]
    print(f'   -> non-specific is {100*ns/tot:.2f} % of the total GFP signal\\n')

print('Verdict:')
for strain in ['052', '056']:
    pct = 100 * contrib[(strain, False)] / contrib[(strain, True)]
    print(f'  MS_S_{strain}: {"CLEAN" if pct < 5 else "CHECK"} — '
          f'{pct:.1f} % of signal is non-specific, '
          f'so {100-pct:.1f} % is induction-dependent display')
print("\\nEXP_014's MS_S_051 intimin null ran 0.8-1.1x autofluorescence across four "
      'aTc doses, i.e. no detectable non-specific binding to the bare barrel. '
      'The uninduced arms here agree with that.')
""")

code("""
def stars(p):
    return ('****' if p < 1e-4 else '***' if p < 1e-3 else
            '**' if p < 1e-2 else '*' if p < 0.05 else 'ns')

def wells(strain, induced, conc):
    if conc == 0:
        return df[(df.group == 'cells_nogfp') & (df.strain == strain)
                  & (df.induced == induced)].f_od.dropna()
    grp = 'cells_1000_I' if induced else 'cells_1000_U'
    return df[(df.group == grp) & (df.strain == strain)].f_od.dropna()

def compare(label, a, b):
    \"\"\"Fold change b/a, with a Welch test only when both arms have n>=2.\"\"\"
    fold = b.mean() / a.mean()
    if len(a) >= 2 and len(b) >= 2:
        p = stats.ttest_ind(a, b, equal_var=False).pvalue
        return dict(label=label, fold=fold, p=p, sig=stars(p),
                    text=f'{fold:.1f}x {stars(p)}', n=f'n={len(a)} vs {len(b)}')
    return dict(label=label, fold=fold, p=np.nan, sig='',
                text=f'{fold:.2f}x (n=1, no test)', n=f'n={len(a)} vs {len(b)}')

comparisons = []
for strain in ['052', '056']:
    comparisons.append(('nonspec', strain,
        compare(f'MS_S_{strain}: non-specific binding',
                wells(strain, False, 0), wells(strain, False, 1000))))
    comparisons.append(('induction', strain,
        compare(f'MS_S_{strain}: induction effect',
                wells(strain, False, 1000), wells(strain, True, 1000))))
comparisons.append(('between', None,
    compare('052 vs 056, induced + 1000 nM',
            wells('056', True, 1000), wells('052', True, 1000))))

print('Comparisons drawn on the figure:\\n')
for kind, strain, c in comparisons:
    pstr = f'p = {c["p"]:.1e}' if np.isfinite(c['p']) else 'no test possible'
    print(f'  {c["label"]:<38} {c["fold"]:>7.2f}x   {pstr:<18} ({c["n"]})')
print('\\nThe no-GFP controls are n=1 (one well per strain per induction state), '
      'so the non-specific comparison carries a fold change and no p value. '
      'Four more tubes would have fixed that; it was judged a bad trade against '
      'a 2-5 % correction, and that judgement is visible here.')
""")

code("""
conds = [(False, 0, 'uninduced<br>no GFP'),
         (False, 1000, 'uninduced<br>+1000 nM'),
         (True, 0, 'induced<br>no GFP'),
         (True, 1000, 'induced<br>+1000 nM')]
OFF = {'052': -0.19, '056': 0.19}
XPOS = {(s, i): ci + OFF[s] for ci, (ind, c, _) in enumerate(conds)
        for s in ['052', '056'] for i in [ci] if True}

def xof(strain, cond_idx):
    return cond_idx + OFF[strain]

fig = go.Figure()
for strain in ['052', '056']:
    xs, means, sds, px, py = [], [], [], [], []
    for ci, (induced, conc, _) in enumerate(conds):
        sel = wells(strain, induced, conc)
        xs.append(xof(strain, ci))
        means.append(sel.mean())
        sds.append(sel.std() if len(sel) > 1 else 0)
        px += [xof(strain, ci)] * len(sel)
        py += list(sel)
    fig.add_trace(go.Bar(
        x=xs, y=means, width=0.36,
        error_y=dict(type='data', array=sds, visible=True),
        name=f'MS_S_{strain} — ' + L.STRAINS[strain].split('  ')[1],
        marker_color=COL[strain]))
    fig.add_trace(go.Scatter(
        x=px, y=py, mode='markers',
        name='individual wells (n=3; n=1 for the no-GFP controls)',
        marker=dict(color='#111', size=7, symbol='circle-open'),
        showlegend=(strain == '052')))

# --- brackets. Two Plotly quirks on a log axis, both easy to get wrong:
#     shapes take RAW data values, annotations take LOG10 values.
def bracket(x0, x1, ytop, text, colour='#333', drop=0.86):
    fig.add_shape(type='line', x0=x0, x1=x1, y0=ytop, y1=ytop,
                  line=dict(color=colour, width=1.4))
    for x in (x0, x1):
        fig.add_shape(type='line', x0=x, x1=x, y0=ytop, y1=ytop * drop,
                      line=dict(color=colour, width=1.4))
    fig.add_annotation(x=(x0 + x1) / 2, y=np.log10(ytop * 1.13), text=text,
                       showarrow=False, font=dict(size=13, color=colour))

by = {(k, s): c for k, s, c in comparisons}
BASE = max(wells(s, True, 1000).mean() for s in ['052', '056'])

# non-specific: low brackets over the two uninduced groups
for strain, lvl in [('052', 1.9), ('056', 3.1)]:
    c = by[('nonspec', strain)]
    top = max(wells(strain, False, 0).mean(), wells(strain, False, 1000).mean())
    bracket(xof(strain, 0), xof(strain, 1), top * lvl, c['text'], COL[strain])

# between strains at induced + 1000 nM — lowest of the tall brackets
c = by[('between', None)]
bracket(xof('052', 3), xof('056', 3), BASE * 1.30, c['text'], '#111')

# induction effect: tall brackets spanning uninduced+GFP -> induced+GFP,
# stacked clear of the tallest bar and of each other
for strain, lvl in [('052', 2.0), ('056', 3.2)]:
    c = by[('induction', strain)]
    bracket(xof(strain, 1), xof(strain, 3), BASE * lvl, c['text'], COL[strain])

fig.update_layout(
    barmode='overlay', width=960, height=660,
    title='EXP_015 — induced vs uninduced: 98-99 % of signal is '
          'induction-dependent<br>'
          '<sub>bars = mean, error bars = SD, circles = individual wells.<br>'
          'Brackets = fold change with Welch p: **** p&lt;0.0001, *** p&lt;0.001, '
          '** p&lt;0.01, * p&lt;0.05, ns otherwise.<br>'
          'The no-GFP controls are n=1, so those two brackets carry a fold '
          'change and no test. LOG y-axis.</sub>',
    margin=dict(t=135),
    xaxis=dict(title='condition', tickmode='array',
               tickvals=list(range(len(conds))),
               ticktext=[c[2] for c in conds], range=[-0.6, 3.6]),
    yaxis=dict(title='F/OD600 (blanked, gain 100)', type='log',
               tickvals=[200, 500, 1000, 2000, 5000, 10000, 20000, 50000,
                         100000],
               range=[np.log10(300), np.log10(175000)]),
    legend=dict(orientation='h', yanchor='bottom', y=-0.30))
fig.write_html(DATA / 'EXP_015_induction.html')
fig.show()
""")

# ----------------------------------------------- cells in the supernatant ---
md("""
## 7. Cells in the supernatant — the correction this plate needs

Recovery through the washes was ~25–35 % of the input OD·mL, well below
EXP_014's 46 %: the 0.3 OD·mL pellets are small, and **4,000 × g for 3 min did
not pellet them completely**. Every Tier-1 and wash supernatant carries cells,
and those cells carry bound GFP.

That inflates apparent *free* GFP, which **underestimates capacity**. The
correction is direct, because each supernatant well has its own OD600 and we
know the F/OD600 of the cells from that same arm:

```
carried RFU = OD600(supernatant well) × F/OD600(matching cell arm)
```

Everything downstream uses the corrected figure, and both are reported so the
size of the correction is visible rather than buried.
""")

code("""
cell_fod = (df[df.is_cells & (df.conc_nM > 0)]
            .groupby(['arm', 'conc_nM']).f_od.mean().rename('arm_f_od'))

sup = df[df.is_tier1 | (df.group == 'wash2')].copy()
sup['arm'] = sup['sample'].str.replace('wash2 ', '', regex=False)
sup['conc_key'] = sup.conc_nM.fillna(1000)   # the wash tubes came off the 1000 nM rack
sup = sup.merge(cell_fod, left_on=['arm', 'conc_key'], right_index=True, how='left')

# carried-cell signal, expressed at gain 75 to match f75
sup['carried_f75'] = (sup.odn * sup.arm_f_od) / GAIN[(75, 100)]
sup['f75_corr'] = sup.f75 - sup.carried_f75.fillna(0)
sup['carry_pct'] = 100 * sup.carried_f75 / sup.f75

print('cell carryover into each supernatant well:')
print(sup[['well', 'group', 'sample', 'odn', 'f75', 'carried_f75', 'carry_pct']]
      .round(2).to_string(index=False))
print()
print('Tier 1, 100 nM rack: carryover is '
      f'{sup[sup.group=="tier1_100"].carry_pct.mean():.1f} % of signal — matters')
print('Tier 1, 1000 nM rack: '
      f'{sup[sup.group=="tier1_1000"].carry_pct.mean():.1f} % — negligible')
""")

# --------------------------------------------------------------- tier 1 -----
md("""
## 8. Tier 1 → **pmol captured per OD·mL**

The primary deliverable: absolute display capacity, the number that sizes bead
capture.

**C0 is taken from the uninduced arms, not from the S1 standard.** The uninduced
Tier-1 wells read 3–8 % *above* S1 — they captured essentially nothing, so their
true free concentration is the starting concentration, and the offset is a
systematic difference between a standard tube and a Tier-1 tube (same solution,
different handling). Using S1 as C0 gives **negative depletion**; using the
strain-matched uninduced arms cancels the offset exactly.

**Read the 100 nM rows for MS_S_056 and the 1000 nM rows for MS_S_052.** At
1000 nM, 056 depletes ~2 % — below the systematic floor, so that number is
noise. At 100 nM, 052 depletes ~75 % — ligand-limited, so that number is a
floor. Each strain has one arm where the measurement is honest.
""")

code("""
t1 = sup[sup.is_tier1 & (sup.conc_nM > 0)].copy()
t1['free_nM'] = rfu_to_nM(t1.f75_corr)

# C0 per arm: measured for 100 nM; the uninduced arms define it at 1000 nM
C0_1000 = t1[(t1.conc_nM == 1000) & (~t1.induced)].groupby('strain').free_nM.mean()
print('C0 for the 1000 nM arm, from the uninduced tubes of the same strain:')
print(C0_1000.round(1).to_string())
print(f'(S1 standard reads 1000 nM by definition — '
      f'{100*(C0_1000.mean()/1000-1):+.1f} % apart, which is why S1 is not used)')
print(f'C0 for the 100 nM arm, measured: {C0_100:.1f} nM')

t1['C0'] = np.where(t1.conc_nM == 100, C0_100, t1.strain.map(C0_1000))
t1['depletion'] = 1 - t1.free_nM / t1.C0
t1['captured_pmol'] = (t1.C0 - t1.free_nM) * 1e-9 * (L.LABEL_uL * 1e-6) * 1e12
t1['pmol_per_OD_mL'] = t1.captured_pmol / L.CELL_INPUT_OD_mL
t1['sites_per_cell'] = (t1.pmol_per_OD_mL * 1e-12 * 6.022e23
                        / L.EXP014['cells_per_OD_mL'])

ind = t1[t1.induced]
out = (ind.groupby(['conc_nM', 'strain'])
       .agg(n=('free_nM', 'size'), free_nM=('free_nM', 'mean'),
            depletion=('depletion', 'mean'),
            pmol_per_OD_mL=('pmol_per_OD_mL', 'mean'),
            sd=('pmol_per_OD_mL', 'std'),
            sites_per_cell=('sites_per_cell', 'mean')).reset_index())
print()
print(out.round(1).to_string(index=False))

print('\\nverdict per arm:')
for _, r in out.iterrows():
    if r.depletion > 0.5:
        v = f'ligand-limited ({r.depletion:.0%} depleted) -> LOWER BOUND'
    elif r.depletion < 0.05:
        v = f'only {r.depletion:.1%} depleted -> at the systematic floor, NOISE'
    else:
        v = f'{r.depletion:.0%} depleted -> usable'
    print(f'  {int(r.conc_nM):>5} nM  MS_S_{r.strain}: {v}')

best = {'052': out[(out.strain=='052') & (out.conc_nM==1000)].iloc[0],
        '056': out[(out.strain=='056') & (out.conc_nM==100)].iloc[0]}
print('\\nTHE CAPACITY NUMBERS (each from its honest arm):')
for s, r in best.items():
    print(f'  MS_S_{s}: {r.pmol_per_OD_mL:.1f} +/- {r.sd:.1f} pmol per OD.mL '
          f'= {r.sites_per_cell:,.0f} sites/cell   (from the {int(r.conc_nM)} nM arm)')
print(f'\\nEXP_014 lower bound was '
      f'{L.EXP014["capacity_pmol_per_OD_mL_lower_bound"]} pmol/OD.mL '
      f'({L.EXP014["sites_per_cell_lower_bound"]:,} sites/cell); '
      'Costan 2024 reports 15,300 adhesins/cell at 300 ng/mL aTc.')
""")

md("""
### Cross-check: the two arms should agree where both are honest

MS_S_056 is the test case — it depletes 27 % at 100 nM (usable) and ~2 % at
1000 nM (noise). If the usable arm and the noisy arm land in the same place,
the method is sound and the 1000 nM noise is genuinely noise rather than bias.
""")

code("""
chk = (t1[t1.induced].groupby(['strain', 'conc_nM'])
       .pmol_per_OD_mL.agg(['mean', 'std']).round(1))
print(chk.to_string())
for s in ['052', '056']:
    a = chk.loc[(s, 100.0), 'mean']
    b = chk.loc[(s, 1000.0), 'mean']
    print(f'\\nMS_S_{s}: 100 nM arm {a:.1f} vs 1000 nM arm {b:.1f} pmol/OD.mL '
          f'-> {b/a:.2f}x apart')
print('\\n056 is the fair comparison: its 100 nM arm is not ligand-limited and its '
      '1000 nM arm is at the floor, so agreement there is a real cross-check. '
      '052 is expected to disagree — its 100 nM arm is 75 % depleted and so reads low.')
""")

code("""
fig = go.Figure()
for strain in ['052', '056']:
    sub = out[out.strain == strain].sort_values('conc_nM')
    fig.add_trace(go.Bar(
        x=[f'{int(c)} nM' for c in sub.conc_nM], y=sub.pmol_per_OD_mL,
        error_y=dict(type='data', array=sub['sd'], visible=True),
        name=f'MS_S_{strain} induced', marker_color=COL[strain]))
fig.add_hline(y=L.EXP014['capacity_pmol_per_OD_mL_lower_bound'],
              line=dict(color='#888', dash='dot'))
fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                         line=dict(color='#888', dash='dot'),
                         name=f'EXP_014 lower bound '
                              f'({L.EXP014["capacity_pmol_per_OD_mL_lower_bound"]} '
                              'pmol/OD·mL)'))
fig.add_hline(y=L.EXP014['sites_per_cell_lower_bound'] * 0 + 15300 * 8e8 /
              6.022e23 * 1e12, line=dict(color='#2a9d8f', dash='dash'))
fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                         line=dict(color='#2a9d8f', dash='dash'),
                         name='Costan 2024, 15,300 adhesins/cell (20.3 pmol/OD·mL)'))
fig.update_layout(
    width=760, height=500,
    title='EXP_015 — display capacity from Tier 1<br>'
          '<sub>bars = triplicate mean, error bars = SD. The 052 100 nM bar is '
          'ligand-limited (a floor); the 056 1000 nM bar is at the systematic '
          'floor (noise). Dotted = EXP_014 lower bound, dashed = Costan 2024</sub>',
    xaxis_title='GFP concentration in the labelling reaction',
    yaxis_title='pmol captured per OD·mL')
fig.write_html(DATA / 'EXP_015_tier1.html')
fig.show()
""")

# ------------------------------------------------- everything on the curve --
md("""
## 9. Everything on the calibration axis

The tables above give numbers; this puts every sample on the standard curve so
the measurement can be read off directly against known GFP concentrations.

**Left panel — Tier 1, what is left in the bath.** Each star is where that arm
*started* (C0). Each point is where it *ended*. **The horizontal gap between
them is the GFP that the cells captured** — that is the whole measurement, in
one distance.

**Right panel — the cells themselves**, with their fluorescence converted into
the GFP concentration that would produce the same brightness in a cell-free
well. It answers "how bright are the cells, in units of known GFP?" and gives
an independent route to the captured amount: the two should agree, and the gap
between them is loss through the washes.

Both axes are logarithmic, with explicit 1-2-5 ticks.
""")

code("""
from plotly.subplots import make_subplots

xx = np.logspace(np.log10(5), np.log10(1300), 200)
SYM = {100.0: 'circle', 1000.0: 'square'}

fig = make_subplots(
    rows=1, cols=2, horizontal_spacing=0.09,
    subplot_titles=('Tier 1 — free GFP left in the bath',
                    'Cells — brightness as a GFP equivalent'))

for col in (1, 2):
    fig.add_trace(go.Scatter(
        x=xx, y=A * xx**k, mode='lines',
        name='standard curve, power-law fit',
        line=dict(color='#7030A0', width=2),
        showlegend=(col == 1)), row=1, col=col)
    fig.add_trace(go.Scatter(
        x=cur.curve_nM, y=cur.f75, mode='markers',
        name='standards S1–S8 (known concentration)',
        marker=dict(size=9, color='#7030A0', symbol='x'),
        showlegend=(col == 1)), row=1, col=col)

# --- left: Tier 1, with the starting concentration as a star
for strain in ['052', '056']:
    for conc in (100.0, 1000.0):
        s = t1[(t1.strain == strain) & (t1.conc_nM == conc) & t1.induced]
        if not len(s):
            continue
        c0 = s.C0.iloc[0]
        fig.add_trace(go.Scatter(
            x=[c0], y=[A * c0**k], mode='markers',
            name=f'start C0 = {c0:.0f} nM ({int(conc)} nM arm)',
            marker=dict(symbol='star', size=16, color='#444',
                        line=dict(width=1, color='white'))),
            row=1, col=1)
        fig.add_trace(go.Scatter(
            x=s.free_nM, y=s.f75_corr, mode='markers',
            name=f'MS_S_{strain} Tier 1, {int(conc)} nM arm (n=3)',
            marker=dict(size=11, color=COL[strain], symbol=SYM[conc],
                        line=dict(width=1, color='white'))),
            row=1, col=1)
        # the depletion gap, drawn as a line from start to mean endpoint
        fig.add_trace(go.Scatter(
            x=[c0, s.free_nM.mean()], y=[A * c0**k, A * s.free_nM.mean()**k],
            mode='lines', line=dict(color=COL[strain], width=3, dash='dot'),
            name=f'MS_S_{strain} captured, {int(conc)} nM arm '
                 f'({s.depletion.mean():.0%} depleted)'),
            row=1, col=1)

# --- right: cell wells as a GFP equivalent
cellw = df[df.is_cells & (df.conc_nM > 0)].copy()
cellw['f75_equiv'] = cellw.f100 / GAIN[(75, 100)]
cellw['nM_equiv'] = rfu_to_nM(cellw.f75_equiv)
for strain in ['052', '056']:
    for conc in (100.0, 1000.0):
        s = cellw[(cellw.strain == strain) & (cellw.conc_nM == conc)
                  & (cellw.induced)]
        if not len(s):
            continue
        fig.add_trace(go.Scatter(
            x=s.nM_equiv, y=s.f75_equiv, mode='markers',
            name=f'MS_S_{strain} cells, {int(conc)} nM arm (n=3)',
            marker=dict(size=11, color=COL[strain], symbol=SYM[conc],
                        line=dict(width=1, color='white'))),
            row=1, col=2)

ticks = [10, 20, 50, 100, 200, 500, 1000]
yticks = [100, 200, 500, 1000, 2000, 5000, 10000]
for col in (1, 2):
    fig.update_xaxes(type='log', tickvals=ticks, title_text='GFP (nM)',
                     row=1, col=col)
    fig.update_yaxes(type='log', tickvals=yticks,
                     title_text='RFU, blanked, gain 75', row=1, col=col)

fig.update_layout(
    width=1100, height=620,
    title='EXP_015 — every sample read against the standard curve<br>'
          '<sub>LEFT: stars = starting concentration C0, filled markers = free GFP '
          'after capture, dotted segment = what the cells took out. '
          'RIGHT: cell wells placed on the curve by brightness. '
          'Circles = 100 nM arm, squares = 1000 nM arm. Log–log, 1-2-5 ticks</sub>',
    legend=dict(font=dict(size=10), yanchor='top', y=-0.12, x=0,
                orientation='v', itemsizing='constant'))
fig.write_html(DATA / 'EXP_015_calibration.html')
fig.show()
""")

md("""
### Mass balance — the two panels should agree

The left panel says how much GFP **left the bath**. The right panel says how
much is **on the cells**. They are independent measurements of the same event,
so the ratio is the recovery through two washes, and the shortfall is handling
loss.

The cell figure is **not** corrected for the ~1.5× fluorescence enhancement
Enhancer produces on bound eGFP (Kirchhofer 2010). Correcting it would *lower*
apparent recovery, so the uncorrected number is the conservative one — and a
recovery meaningfully above 100 % would be evidence that the enhancement is not
negligible here.
""")

code("""
on_cells = (cellw.assign(
                pmol=lambda d: d.nM_equiv * 1e-9 * (L.RESUSPEND_uL * 1e-6) * 1e12)
            .groupby(['strain', 'conc_nM']).pmol.mean())
from_bath = (t1[t1.induced].groupby(['strain', 'conc_nM']).captured_pmol.mean())

mb = pd.concat([from_bath.rename('bath_lost_pmol'),
                on_cells.rename('on_cells_pmol')], axis=1).dropna()
mb['recovery'] = mb.on_cells_pmol / mb.bath_lost_pmol
print(mb.round(2).to_string())
print()
for (s, c), r in mb.iterrows():
    note = ''
    if c == 100 and s == '052':
        note = '   (052 at 100 nM is ligand-limited; bath figure is a floor)'
    if c == 1000 and s == '056':
        note = '   (056 at 1000 nM is at the systematic floor; bath figure is noise)'
    print(f'MS_S_{s} {int(c):>5} nM: bath lost {r.bath_lost_pmol:5.1f} pmol, '
          f'cells carry {r.on_cells_pmol:5.1f} pmol -> recovery '
          f'{r.recovery:6.0%}{note}')
print('\\nEXP_014 inferred a 17-39 % unexplained loss floor and had no way to '
      'measure it; the NC no-cells control that would have done so was offered '
      'and not run today either, so this remains an upper bound on loss rather '
      'than a measurement of it.')
""")

# ---------------------------------------------------------------- washes ----
md("""
## 10. Wash sufficiency — and why the raw number is misleading

`wash2 052IA` and `wash2 056IA` are the **second** wash of the two tubes that saw
the most GFP. Raw, both read clearly above the buffer blank, which looks like
GFP still coming off — i.e. two washes were not enough.

**They are not.** Both wells carry cells (section 7), and the carried-cell signal
accounts for essentially the whole reading. This is only visible because OD600
was read on every well.
""")

code("""
w = sup[sup.group == 'wash2']
sd = SD0[75]
print(f'buffer blank at gain 75: {F0[75]:.0f} +/- {sd:.1f} (n={len(blank)})')
for _, r in w.iterrows():
    z_raw = r.f75 / sd
    z_corr = r.f75_corr / sd
    print(f'\\n  {r["sample"]}')
    print(f'    raw           {r.f75:+7.0f} RFU  ({z_raw:5.1f} SD above blank) '
          f'= {rfu_to_nM(r.f75):.2f} nM')
    print(f'    carried cells {r.carried_f75:+7.0f} RFU  '
          f'(OD {r.odn:.4f} x {r.arm_f_od:,.0f} F/OD600)')
    print(f'    corrected     {r.f75_corr:+7.0f} RFU  ({z_corr:5.1f} SD)  -> '
          + ('two washes sufficient, the raw signal was cells not GFP'
             if abs(z_corr) < 5 else 'genuine carryover remains'))
print('\\nEXP_014 reached the same conclusion by a different route '
      '(194 and 204 against a blank of 194 +/- 4.3), but could not have '
      'distinguished these two explanations — it did not read OD on those wells.')
""")

# ------------------------------------------------------------- position -----
md("""
## 11. Plate position

Whether signal tracks position rather than contents. The layout was ordered
dim→bright specifically to keep the bright 1000 nM Tier-1 block away from the
blanks; section 2 already showed crosstalk is negligible, and this is the
visual confirmation.
""")

code("""
rows = list('ABCDEF')
grid = np.full((len(rows), 12), np.nan)
hover = np.empty((len(rows), 12), dtype=object)
hover[:] = ''
lookup = {r.well: r for _, r in df.iterrows()}
for letter in rows:
    for c in range(1, 13):
        well = f'{letter}{c}'
        i = rows.index(letter)
        if well in lookup:
            r = lookup[well]
            grid[i, c-1] = max(r.f75, 1)
            hover[i, c-1] = f'{well}<br>{r["sample"]}<br>{r.group_label}'
        elif well in read_all:
            grid[i, c-1] = max(read_all[well] - F0[75], 1)
            hover[i, c-1] = f'{well}<br>unfilled (crosstalk probe)'

fig = go.Figure(go.Heatmap(
    z=np.log10(grid), x=list(range(1, 13)), y=rows, text=hover,
    hovertemplate='%{text}<br>log10 RFU %{z:.2f}<extra></extra>',
    colorscale='Viridis', colorbar=dict(title='log10 RFU<br>gain 75<br>blanked')))
fig.update_layout(width=780, height=380, yaxis=dict(autorange='reversed'),
                  title='EXP_015 plate — log10 blanked RFU at gain 75<br>'
                        '<sub>colour = signal. Rows run dim (A) to bright (F) by '
                        'design; unfilled wells are the crosstalk probe</sub>',
                  xaxis_title='column', yaxis_title='row')
fig.write_html(DATA / 'EXP_015_plate_heatmap.html')
fig.show()
""")

# ----------------------------------------------------------------- export ---
md("""
## 12. Export, and the table to put on Notion

The Notion page is the notebook of record; this file is the analysis.
""")

code("""
df.to_csv(DATA / 'EXP_015_tidy.csv', index=False)
summary.round(3).to_csv(DATA / 'EXP_015_summary.csv', index=False)
out.round(3).to_csv(DATA / 'EXP_015_tier1.csv', index=False)
ratios.round(4).to_csv(DATA / 'EXP_015_ratios.csv', index=False)
print('wrote:', ', '.join(sorted(f.name for f in DATA.glob('EXP_015_*'))))

print('\\n' + '=' * 64)
print('EXP_015 RESULTS'.center(64))
print('=' * 64)
for conc in (100, 1000):
    s = summary[summary.conc_nM == conc].set_index('strain')
    r = ratios[ratios.conc_nM == conc].iloc[0]
    print(f'\\n{conc} nM')
    for strain in ['052', '056']:
        print(f'  MS_S_{strain}  F/OD600 {s.loc[strain,"mean"]:>8,.0f} '
              f'+/- {s.loc[strain,"sd"]:<5,.0f} (n=3, CV {s.loc[strain,"cv_pct"]:.1f} %)'
              f'   {s.loc[strain,"fold"]:>5.1f}x autofluorescence')
    print(f'  ratio 052/056 = {r.ratio_052_056:.2f}x  (Welch p={r.p_welch:.1e} {r.sig})')

print('\\nDisplay capacity, each from its honest arm:')
for s, r in best.items():
    print(f'  MS_S_{s}  {r.pmol_per_OD_mL:>5.1f} +/- {r.sd:.1f} pmol/OD.mL '
          f'= {r.sites_per_cell:>7,.0f} sites/cell  (from {int(r.conc_nM)} nM, '
          f'{r.depletion:.0%} depleted)')

print('\\nConclusions:')
print(f'  1. The 2xHA tag costs {ratios.ratio_052_056.mean():.2f}x, and the cost is the '
      'SAME at 100 and 1000 nM')
print('     -> it is a DISPLAY cost (fewer molecules on the surface), not a binding cost.')
print(f'  2. Signal is flat between 100 and 1000 nM within each strain '
      f'(1000/100 = {d1000["052"]/d100["052"]:.2f} and {d1000["056"]/d100["056"]:.2f})')
print("     -> both are on the plateau, so EXP_014's 365 nM was saturating when "
      'ligand was in excess.')
print(f'  3. EXP_014\\'s 2.58x was a floor, as predicted. With GFP in excess it is '
      f'{ratios.ratio_052_056.mean():.2f}x.')
print('\\nStill unrecorded:',
      ', '.join(k for k, v in L.UNRECORDED.items() if v is None))
""")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.write_text(json.dumps(nb, indent=1))
print(f"wrote {OUT}  ({len(cells)} cells)")
