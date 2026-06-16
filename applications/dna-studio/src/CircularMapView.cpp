#include "CircularMapView.h"
#include "SequenceIO.h"
#include "AnnotationDialog.h"

#include <QPainter>
#include <QPainterPath>
#include <QWheelEvent>
#include <QMouseEvent>
#include <QContextMenuEvent>
#include <QMenu>
#include <QInputDialog>
#include <QLineEdit>
#include <QMessageBox>
#include <QGuiApplication>
#include <QClipboard>
#include <QFontMetricsF>
#include <QHash>
#include <QPair>
#include <cmath>

namespace {

constexpr double kPpbAt100  = 8.0;
constexpr double kMaxPpb    = 40.0;
constexpr double kFitMargin = 90.0;

bool inFeature(const Feature &f, int pos) {
    if (f.end >= f.start) return pos >= f.start && pos <= f.end;
    return pos >= f.start || pos <= f.end;
}

double niceInterval(double raw) {
    if (raw < 1) return 1;
    double mag = std::pow(10.0, std::floor(std::log10(raw)));
    double n = raw / mag;
    double nice = (n < 1.5) ? 1 : (n < 3) ? 2 : (n < 7) ? 5 : 10;
    return nice * mag;
}

} // namespace

CircularMapView::CircularMapView(QWidget *parent) : QWidget(parent) {
    setMouseTracking(true);
    setMinimumSize(320, 320);
    setFocusPolicy(Qt::StrongFocus);
    setAttribute(Qt::WA_OpaquePaintEvent);
}

void CircularMapView::setSequence(const QString &seq) {
    m_seq = seq.toUpper();
    m_focus = 0.0;
    clearSelection();
    m_undo.clear();
    update();
}

void CircularMapView::setFeatures(const QVector<Feature> &features) {
    m_features = features;
    update();
}

void CircularMapView::setDocument(const SequenceDocument &doc) {
    m_seq = doc.sequence.toUpper();
    m_features = doc.features;
    m_title = doc.name;
    m_linear = !doc.circular;
    m_focus = 0.0;
    m_selLo = m_selHi = -1;
    m_selectedFeature = -1;
    m_undo.clear();
    m_hits.clear(); m_currentHit = -1;
    emitSelection();
    emit findResults(0, 0);
    fitToView();
}

// ---------------------------------------------------------------- geometry ---

double CircularMapView::minPpb() const {
    const int N = qMax(1, m_seq.size());
    double m = qMin(width(), height()) - kFitMargin;
    if (m < 60) m = 60;
    return m * M_PI / N;
}

CircularMapView::Geom CircularMapView::geometry() const {
    Geom g;
    const int N = qMax(1, m_seq.size());
    g.R  = (N * m_ppb) / (2.0 * M_PI);
    g.Cx = width() / 2.0;
    g.fits = (!m_linear) && (2 * g.R <= qMin(width(), height()) - kFitMargin);
    g.Cy = g.fits ? height() / 2.0 : height() * 0.40 + g.R;
    return g;
}

QPointF CircularMapView::mapBase(double base, double offsetPx, const Geom &g) const {
    if (m_linear) {
        double x = g.Cx + (base - m_focus) * m_ppb;
        double y = height() * 0.45 - offsetPx;
        return {x, y};
    }
    const int N = qMax(1, m_seq.size());
    double phi = 2.0 * M_PI * (base - m_focus) / N;
    double r = g.R + offsetPx;
    return { g.Cx + r * std::sin(phi), g.Cy - r * std::cos(phi) };
}

double CircularMapView::baseAtPoint(const QPointF &p, const Geom &g) const {
    const int N = qMax(1, m_seq.size());
    double base;
    if (m_linear) {
        base = m_focus + (p.x() - g.Cx) / m_ppb;
    } else {
        double phi = std::atan2(p.x() - g.Cx, -(p.y() - g.Cy));
        base = m_focus + phi / (2.0 * M_PI) * N;
    }
    base = std::fmod(base, double(N));
    if (base < 0) base += N;
    return base;
}

// ------------------------------------------------------------------- zoom ----

int  CircularMapView::zoomPercent() const { return int(std::lround(m_ppb / kPpbAt100 * 100.0)); }

void CircularMapView::centerOnSelection() {
    if (!hasSelection()) return;
    const int N = qMax(1, m_seq.size());
    m_focus = std::fmod((m_selLo + m_selHi) / 2.0 - 1.0, double(N));   // center of [lo,hi]
    if (m_focus < 0) m_focus += N;
}

void CircularMapView::setZoomPercent(int percent) {
    double p = qBound(minPpb() * 0.6, percent / 100.0 * kPpbAt100, kMaxPpb);
    if (qFuzzyCompare(p, m_ppb)) return;
    centerOnSelection();   // keep the selected stretch centered while zooming
    m_ppb = p; m_userZoomed = true; emit zoomChanged(zoomPercent()); update();
}

void CircularMapView::applyZoom(double factor) {
    double p = qBound(minPpb() * 0.6, m_ppb * factor, kMaxPpb);
    if (qFuzzyCompare(p, m_ppb)) return;
    centerOnSelection();   // keep the selected stretch centered while zooming
    m_ppb = p; m_userZoomed = true; emit zoomChanged(zoomPercent()); update();
}

void CircularMapView::fitToView() {
    m_userZoomed = false;          // keeps the current circular/linear mode
    m_ppb = minPpb();
    emit zoomChanged(zoomPercent());
    update();
}

// ------------------------------------------------------------------ events ---

void CircularMapView::wheelEvent(QWheelEvent *e) {
    double steps = e->angleDelta().y() / 120.0;
    if (steps == 0) steps = e->angleDelta().x() / 120.0;

    if (e->modifiers() & Qt::AltModifier) {
        applyZoom(std::pow(1.18, steps));
    } else {
        const int N = qMax(1, m_seq.size());
        double basesPerStep = qBound(N * 0.005, 50.0 / m_ppb, N * 0.06);
        m_focus -= steps * basesPerStep;
        m_focus = std::fmod(m_focus, double(N));
        if (m_focus < 0) m_focus += N;
        update();
    }
    e->accept();
}

void CircularMapView::resizeEvent(QResizeEvent *) {
    if (!m_userZoomed) { m_ppb = minPpb(); emit zoomChanged(zoomPercent()); }
    update();
}

void CircularMapView::mousePressEvent(QMouseEvent *e) {
    if (e->button() != Qt::LeftButton || m_seq.isEmpty()) { QWidget::mousePressEvent(e); return; }
    setFocus();
    Geom g = geometry();
    m_pressBase = baseAtPoint(e->position(), g);
    m_pressFeature = featureAt(e->position());
    m_selecting = true;
    m_dragged = false;
    int b = qBound(1, int(std::lround(m_pressBase)) + 1, m_seq.size());   // nearest base
    m_selLo = m_selHi = b;
    update();
}

void CircularMapView::mouseMoveEvent(QMouseEvent *e) {
    if (m_seq.isEmpty()) return;
    Geom g = geometry();
    double bd = baseAtPoint(e->position(), g);

    const int N = m_seq.size();
    if (m_selecting) {
        if (std::abs(bd - m_pressBase) >= 0.5) { m_dragged = true; m_selectedFeature = -1; }
        int a = qBound(1, int(std::lround(m_pressBase)) + 1, N);
        int b = qBound(1, int(std::lround(bd)) + 1, N);
        m_selLo = qMin(a, b); m_selHi = qMax(a, b);
        emitSelection();
        update();
        return;
    }

    int b0 = int(std::lround(bd)) % N; if (b0 < 0) b0 += N;
    int pos1 = b0 + 1;
    QChar nt = m_seq.at(b0);
    int residue = -1; QString aa;
    for (const Feature &f : m_features) {
        if (f.strand != 1 || !f.name.contains("CDS", Qt::CaseInsensitive)) continue;
        if (!inFeature(f, pos1)) continue;
        int off = pos1 - f.start; if (off < 0) off += N;
        residue = off / 3;
        int s = (f.start - 1) + residue * 3;
        QString codon;
        for (int k = 0; k < 3; ++k) codon += m_seq.at((s + k) % N);
        QString three, full;
        QChar one = translateCodon(codon, &three, &full);
        aa = QString("%1/%2/%3").arg(one).arg(three, full);
        residue += 1;
        break;
    }
    emit hovered(pos1, nt, residue, aa);
}

void CircularMapView::mouseReleaseEvent(QMouseEvent *e) {
    if (!m_selecting) { QWidget::mouseReleaseEvent(e); return; }
    m_selecting = false;
    if (!m_dragged) {
        // a plain click: select the annotation under the cursor (if any), else deselect
        m_selLo = m_selHi = -1;
        m_selectedFeature = m_pressFeature;
        emitSelection();
    } else {
        m_selectedFeature = -1;
        emitSelection();
    }
    update();
}

void CircularMapView::mouseDoubleClickEvent(QMouseEvent *e) {
    if (e->button() != Qt::LeftButton || m_seq.isEmpty()) { QWidget::mouseDoubleClickEvent(e); return; }
    int fi = featureAt(e->position());
    if (fi >= 0) { m_selectedFeature = fi; update(); editSelectedFeature(); }
}

int CircularMapView::featureAt(const QPointF &pt) const {
    if (m_seq.isEmpty()) return -1;
    Geom g = geometry();
    int pos = qBound(1, int(std::lround(baseAtPoint(pt, g))) + 1, m_seq.size());
    double off;
    if (m_linear) off = height() * 0.45 - pt.y();
    else { double r = std::hypot(pt.x() - g.Cx, pt.y() - g.Cy); off = r - g.R; }
    int found = -1;
    for (int i = 0; i < m_features.size(); ++i) {
        const Feature &f = m_features[i];
        bool inRange = (f.end >= f.start) ? (pos >= f.start && pos <= f.end)
                                          : (pos >= f.start || pos <= f.end);
        if (inRange && std::abs(off - f.offsetPx) <= f.thickness / 2.0 + 4.0) found = i; // topmost
    }
    return found;
}

void CircularMapView::contextMenuEvent(QContextMenuEvent *e) {
    // Right-click on an annotation → annotation menu.
    int fi = featureAt(QPointF(e->pos()));
    if (fi >= 0) {
        m_selectedFeature = fi; m_selLo = m_selHi = -1; emitSelection(); update();
        QMenu fmenu(this);
        fmenu.addAction(QString("Annotation: %1 (%2)")
                            .arg(m_features[fi].name, m_features[fi].type))->setEnabled(false);
        fmenu.addSeparator();
        QAction *ed  = fmenu.addAction("Edit Annotation…");
        QAction *del = fmenu.addAction("Delete Annotation");
        QAction *r = fmenu.exec(e->globalPos());
        if (r == ed)       editSelectedFeature();
        else if (r == del) deleteActive();
        return;
    }

    QMenu menu(this);
    const bool sel = hasSelection();
    const QString clip = QGuiApplication::clipboard()->text();

    QAction *copy = menu.addAction("Copy");                 copy->setEnabled(sel);
    QAction *ann  = menu.addAction("Add Annotation…");      ann->setEnabled(sel);
    menu.addSeparator();
    QAction *paste = menu.addAction("Paste");               paste->setEnabled(m_editable && !clip.isEmpty());
    QAction *del   = menu.addAction(m_editable ? "Delete Selection" : "Delete Selection (locked)");
    del->setEnabled(sel);
    menu.addSeparator();
    QAction *all  = menu.addAction("Select All");
    QAction *un   = menu.addAction("Undo");                 un->setEnabled(canUndo());

    QAction *r = menu.exec(e->globalPos());
    if (r == copy)       copySelection();
    else if (r == ann)   addAnnotation();
    else if (r == paste) pasteClipboard();
    else if (r == del)   deleteSelection();
    else if (r == all)   selectAll();
    else if (r == un)    undo();
}

// --------------------------------------------------------------- selection ---

void CircularMapView::emitSelection() {
    if (hasSelection()) emit selectionChanged(m_selLo, m_selHi, m_selHi - m_selLo + 1);
    else                emit selectionChanged(0, 0, 0);
}

void CircularMapView::selectAll() {
    if (m_seq.isEmpty()) return;
    m_selLo = 1; m_selHi = m_seq.size();
    emitSelection(); update();
}

void CircularMapView::clearSelection() {
    m_selLo = m_selHi = -1;
    emitSelection(); update();
}

QString CircularMapView::selectionText() const {
    if (!hasSelection()) return {};
    return m_seq.mid(m_selLo - 1, m_selHi - m_selLo + 1);
}

void CircularMapView::copySelection() {
    if (!hasSelection()) return;
    QGuiApplication::clipboard()->setText(selectionText());
}

// ----------------------------------------------------------------- editing ---

void CircularMapView::pushUndo() {
    m_undo.append({m_seq, m_features, m_selLo, m_selHi});
    if (m_undo.size() > 100) m_undo.removeFirst();
}

void CircularMapView::deleteSelection() {
    if (!hasSelection()) return;
    if (!m_editable) {
        QMessageBox::information(this, "Sequence locked",
            "This sequence is locked to prevent accidental edits.\n\n"
            "Enable “Allow Editing” in the toolbar before deleting nucleotides.");
        return;
    }
    const int len = m_selHi - m_selLo + 1;
    auto r = QMessageBox::warning(this, "Delete nucleotides",
        QString("Delete %L1 bp (positions %L2–%L3)?\n\n"
                "This changes the sequence. You can undo with Ctrl+Z.")
            .arg(len).arg(m_selLo).arg(m_selHi),
        QMessageBox::Yes | QMessageBox::No, QMessageBox::No);
    if (r != QMessageBox::Yes) return;

    pushUndo();
    const int lo = m_selLo, hi = m_selHi;
    m_seq.remove(lo - 1, len);

    QVector<Feature> kept;
    auto adjust = [&](int x) { return (x < lo) ? x : (x <= hi) ? lo - 1 : x - len; };
    for (Feature f : m_features) {
        if (f.end >= f.start) {            // non-wrapping feature
            f.start = adjust(f.start);
            f.end   = adjust(f.end);
            if (f.end >= f.start) kept.append(f);   // drop fully-deleted features
        } else {
            kept.append(f);                // leave origin-wrapping features untouched
        }
    }
    m_features = kept;
    m_selLo = m_selHi = -1;
    emitSelection();
    emit documentEdited();
    update();
}

void CircularMapView::pasteClipboard() {
    if (!m_editable) {
        QMessageBox::information(this, "Sequence locked",
            "Enable “Allow Editing” in the toolbar before pasting nucleotides.");
        return;
    }
    QString t;
    for (QChar c : QGuiApplication::clipboard()->text())
        if (QString("ACGTNacgtn").contains(c)) t += c.toUpper();
    if (t.isEmpty()) return;

    pushUndo();
    const int at = hasSelection() ? m_selLo - 1 : int(std::floor(m_focus));   // 0-based insert
    m_seq.insert(at, t);
    const int L = t.size();
    for (Feature &f : m_features) {
        if (f.start > at) f.start += L;
        if (f.end   > at) f.end   += L;
    }
    m_selLo = at + 1; m_selHi = at + L;
    emitSelection();
    emit documentEdited();
    update();
}

void CircularMapView::addAnnotation() {
    if (!hasSelection()) return;
    QString name, type; int strand; QColor color;
    if (!AnnotationDialog::get(this, m_selLo, m_selHi, name, type, strand, color))
        return;

    pushUndo();
    Feature f;
    f.name = name;
    f.type = type;
    f.start = m_selLo; f.end = m_selHi;
    f.strand = strand;
    f.directional = (strand != 0);
    f.color = color;
    double minOff = 0;
    for (const Feature &e : m_features) minOff = qMin(minOff, e.offsetPx);
    f.offsetPx = minOff - 15.0;
    f.thickness = 12;
    m_features.append(f);
    emit documentEdited();
    update();
}

void CircularMapView::editSelectedFeature() {
    if (m_selectedFeature < 0 || m_selectedFeature >= m_features.size()) return;
    Feature f = m_features[m_selectedFeature];
    QString name = f.name, type = f.type; int strand = f.strand; QColor color = f.color;
    if (!AnnotationDialog::edit(this, f.start, f.end, name, type, strand, color)) return;
    pushUndo();
    Feature &g = m_features[m_selectedFeature];
    g.name = name; g.type = type; g.strand = strand; g.color = color;
    g.directional = (strand != 0);
    emit documentEdited();
    update();
}

void CircularMapView::deleteActive() {
    if (m_selectedFeature >= 0 && m_selectedFeature < m_features.size()) {
        pushUndo();                                  // deleting an annotation is cheap & undoable
        m_features.removeAt(m_selectedFeature);
        m_selectedFeature = -1;
        emit documentEdited();
        update();
    } else {
        deleteSelection();                           // base deletion (protected + confirmed)
    }
}

void CircularMapView::undo() {
    if (m_undo.isEmpty()) return;
    Snapshot s = m_undo.takeLast();
    m_seq = s.seq; m_features = s.feats; m_selLo = s.lo; m_selHi = s.hi;
    m_selectedFeature = -1;
    emitSelection();
    emit documentEdited();
    update();
}

// -------------------------------------------------------------- find ---------

QString CircularMapView::reverseComplement(const QString &s) {
    QString r; r.reserve(s.size());
    for (int i = s.size() - 1; i >= 0; --i) {
        switch (s.at(i).toLatin1()) {
            case 'A': r += 'T'; break; case 'T': r += 'A'; break;
            case 'G': r += 'C'; break; case 'C': r += 'G'; break;
            default:  r += 'N'; break;
        }
    }
    return r;
}

void CircularMapView::findMatches(const QString &query, int maxMismatch, bool bothStrands) {
    m_hits.clear();
    m_currentHit = -1;

    QString q;
    for (QChar c : query) if (QString("ACGTNacgtn").contains(c)) q += c.toUpper();
    const int N = m_seq.size();
    const int ql = q.size();
    if (ql == 0 || ql > N) { update(); emit findResults(0, 0); return; }

    auto scan = [&](const QString &pat, int strand) {
        const int last = m_linear ? (N - ql) : (N - 1);   // circular windows wrap the origin
        for (int s = 0; s <= last; ++s) {
            int mm = 0; QVector<int> pos;
            for (int k = 0; k < ql; ++k) {
                int idx = (s + k) % N;
                if (m_seq.at(idx) != pat.at(k)) {
                    if (++mm > maxMismatch) break;
                    pos.append(idx + 1);
                }
            }
            if (mm <= maxMismatch) m_hits.append({s + 1, ql, strand, pos});
        }
    };
    scan(q, +1);
    if (bothStrands) scan(reverseComplement(q), -1);

    update();
    if (!m_hits.isEmpty()) { m_currentHit = 0; gotoCurrentHit(); }
    else emit findResults(0, 0);
}

void CircularMapView::gotoCurrentHit() {
    if (m_currentHit < 0 || m_currentHit >= m_hits.size()) return;
    const FindHit &h = m_hits[m_currentHit];
    const int N = qMax(1, m_seq.size());
    m_focus = std::fmod((h.start - 1) + h.len / 2.0, double(N));   // rotate hit to the top
    if (h.start + h.len - 1 <= N) { m_selLo = h.start; m_selHi = h.start + h.len - 1; emitSelection(); }
    emit findResults(m_hits.size(), m_currentHit + 1);
    update();
}

void CircularMapView::nextHit() {
    if (m_hits.isEmpty()) return;
    m_currentHit = (m_currentHit + 1) % m_hits.size();
    gotoCurrentHit();
}

void CircularMapView::prevHit() {
    if (m_hits.isEmpty()) return;
    m_currentHit = (m_currentHit - 1 + m_hits.size()) % m_hits.size();
    gotoCurrentHit();
}

void CircularMapView::clearFind() {
    m_hits.clear();
    m_currentHit = -1;
    emit findResults(0, 0);
    update();
}

// ------------------------------------------------------------------- paint ---

void CircularMapView::paintEvent(QPaintEvent *) {
    QPainter p(this);
    p.setRenderHint(QPainter::Antialiasing, true);
    p.fillRect(rect(), QColor("#1e1e1e"));

    if (m_seq.isEmpty()) {
        p.setPen(QColor("#6e6e6e"));
        p.drawText(rect(), Qt::AlignCenter, "No sequence loaded");
        return;
    }

    Geom g = geometry();

    p.setPen(QPen(QColor("#9d9d9d"), 1.4));
    p.setBrush(Qt::NoBrush);
    if (m_linear) {
        double y = height() * 0.45;
        p.drawLine(QPointF(0, y), QPointF(width(), y));
    } else {
        p.drawEllipse(QPointF(g.Cx, g.Cy), g.R, g.R);
    }

    drawRuler(p, g);
    if (m_showAnnotations) drawFeatures(p, g);
    drawFindHits(p, g);
    drawSelection(p, g);
    if (m_ppb >= 3.0) drawBases(p, g);

    p.setPen(QColor("#cccccc"));
    QFont tf = font(); tf.setPointSizeF(11); p.setFont(tf);
    QPointF c = g.fits ? QPointF(g.Cx, height() / 2.0) : QPointF(g.Cx, height() - 34);
    p.drawText(QRectF(c.x() - 150, c.y() - 16, 300, 16), Qt::AlignCenter, m_title);
    p.drawText(QRectF(c.x() - 150, c.y(), 300, 16), Qt::AlignCenter,
               QString("%L1 bp").arg(m_seq.size()));
}

QPainterPath CircularMapView::bandPath(double startB, double lenB, double offset,
                                       double thickness, const Geom &g) const {
    double half = thickness / 2.0;
    int segs = qBound(2, int(lenB * m_ppb / 6.0), 600);
    QPainterPath band;
    for (int i = 0; i <= segs; ++i) {
        double b = startB + lenB * i / segs;
        QPointF pt = mapBase(b, offset + half, g);
        (i == 0) ? band.moveTo(pt) : band.lineTo(pt);
    }
    for (int i = segs; i >= 0; --i)
        band.lineTo(mapBase(startB + lenB * i / segs, offset - half, g));
    band.closeSubpath();
    return band;
}

void CircularMapView::drawRuler(QPainter &p, const Geom &g) {
    const int N = m_seq.size();
    double interval = niceInterval(70.0 / m_ppb);
    QFont f = font(); f.setPointSizeF(8.0); p.setFont(f);
    QRectF view = rect().adjusted(-40, -40, 40, 40);
    for (double b = 0; b < N; b += interval) {
        QPointF a = mapBase(b, 1, g);
        if (!view.contains(a)) continue;
        p.setPen(QPen(QColor("#7a7a7a"), 1.0));
        p.drawLine(a, mapBase(b, 7, g));
        QPointF t = mapBase(b, 20, g);
        p.setPen(QColor("#9d9d9d"));
        QString lab = (b == 0) ? QString::number(N) : QString("%L1").arg((int)b);
        p.drawText(QRectF(t.x() - 24, t.y() - 8, 48, 16), Qt::AlignCenter, lab);
    }
}

void CircularMapView::drawFeatures(QPainter &p, const Geom &g) {
    const int N = m_seq.size();
    // Zoom-adaptive but always-readable label font.
    QFont lf = font();
    lf.setPointSizeF(qBound(8.0, 8.0 + m_ppb * 0.25, 12.0));
    lf.setBold(true);
    const QFontMetricsF fm(lf);

    for (int i = 0; i < m_features.size(); ++i) {
        const Feature &f = m_features[i];
        double startB = f.start - 1;
        double lenB = (f.end >= f.start) ? (f.end - f.start + 1)
                                         : (N - f.start + 1 + f.end);
        if (lenB <= 0) continue;
        double half = f.thickness / 2.0;
        bool selected = (i == m_selectedFeature);

        // Directional features → single block-arrow tapering to the strand tip;
        // non-directional → plain band.
        bool dir = f.directional && f.strand != 0;
        double head = dir ? qBound(2.0, 14.0 / m_ppb, lenB * 0.5) : 0.0;
        auto edge = [&](double b) -> double {
            if (!dir) return half;
            double d = (f.strand >= 0) ? (startB + lenB - b) : (b - startB);
            return (d < head) ? half * (d / head) : half;
        };

        int segs = qBound(8, int(lenB * m_ppb / 5.0), 700);
        QPainterPath path;
        for (int j = 0; j <= segs; ++j)
            (j == 0) ? path.moveTo(mapBase(startB + lenB * j / segs, f.offsetPx + edge(startB + lenB * j / segs), g))
                     : path.lineTo(mapBase(startB + lenB * j / segs, f.offsetPx + edge(startB + lenB * j / segs), g));
        for (int j = segs; j >= 0; --j)
            path.lineTo(mapBase(startB + lenB * j / segs, f.offsetPx - edge(startB + lenB * j / segs), g));
        path.closeSubpath();

        p.setPen(QPen(f.color.darker(150), 1.0));
        p.setBrush(f.color);
        p.drawPath(path);
        if (selected) {                         // highlight the selected annotation
            p.setPen(QPen(QColor("#ffffff"), 2.0));
            p.setBrush(Qt::NoBrush);
            p.drawPath(path);
        }

        // Horizontal label, centered on the *visible* portion of the feature so a
        // feature you've zoomed into still shows its name. Only when it fits.
        if (m_showNames && !f.name.isEmpty()) {
            double mid = startB + lenB / 2.0;
            double rep = mid;                            // representative center nearest focus (handles wrap)
            for (double cand : {mid - N, mid + N})
                if (std::abs(cand - m_focus) < std::abs(rep - m_focus)) rep = cand;
            double fStart = startB + (rep - mid), fEnd = fStart + lenB;
            double W = width() / (2.0 * m_ppb);          // half the on-screen base span
            double visLo = qMax(fStart, m_focus - W), visHi = qMin(fEnd, m_focus + W);
            double tw = fm.horizontalAdvance(f.name);
            if (visHi > visLo && ((visHi - visLo) * m_ppb > tw + 10 || selected)) {
                QPointF mp = mapBase((visLo + visHi) / 2.0, f.offsetPx, g);
                QRectF tr(mp.x() - tw / 2 - 3, mp.y() - fm.height() / 2, tw + 6, fm.height());
                p.setFont(lf);
                p.setPen(QColor(0, 0, 0, 170));          // dark halo for readability over any color
                for (int dx = -1; dx <= 1; ++dx)
                    for (int dy = -1; dy <= 1; ++dy)
                        if (dx || dy) p.drawText(tr.translated(dx, dy), Qt::AlignCenter, f.name);
                p.setPen(Qt::white);
                p.drawText(tr, Qt::AlignCenter, f.name);
            }
        }
    }
}

void CircularMapView::drawFindHits(QPainter &p, const Geom &g) {
    if (m_hits.isEmpty()) return;
    const double off = 9.0, thick = 8.0;
    for (int i = 0; i < m_hits.size(); ++i) {
        const FindHit &h = m_hits[i];
        bool cur = (i == m_currentHit);
        // hit band (green = matched), just outside the ring
        p.setPen(cur ? QPen(QColor("#dcdcaa"), 1.8) : QPen(QColor(78, 201, 176), 1.0));
        p.setBrush(QColor(78, 201, 176, cur ? 130 : 70));
        p.drawPath(bandPath(h.start - 1, h.len, off, thick, g));
        // flag mismatched bases in red
        p.setPen(Qt::NoPen);
        p.setBrush(QColor("#f44747"));
        for (int pos : h.mm)
            p.drawPath(bandPath((pos - 1) - 0.45, 0.9, off, thick, g));
    }
}

void CircularMapView::drawSelection(QPainter &p, const Geom &g) {
    if (!hasSelection()) return;
    // Extend half a base (plus a touch) beyond each end so it's clear the
    // selection includes the first AND last nucleotide.
    const double pad = 0.6;
    double startB = (m_selLo - 1) - pad;            // left edge of first base
    double lenB   = (m_selHi - m_selLo) + 2 * pad;  // out to right edge of last base
    p.setPen(QPen(QColor(86, 156, 214), 1.3));
    p.setBrush(QColor(86, 156, 214, 70));           // translucent accent overlay
    p.drawPath(bandPath(startB, lenB, -12, 52, g));
}

void CircularMapView::drawBases(QPainter &p, const Geom &g) {
    const int N = m_seq.size();
    bool letters = m_ppb >= 7.0;
    double visHalf = width() / m_ppb;
    int lo = int(std::floor(m_focus - visHalf));
    int hi = int(std::ceil(m_focus + visHalf));
    QRectF view = rect().adjusted(-20, -20, 20, 20);

    QFont bf = font(); bf.setPointSizeF(letters ? qMin(13.0, m_ppb * 0.62) : 8.0);
    bf.setBold(true); p.setFont(bf);

    for (int b = lo; b <= hi; ++b) {
        int idx = b % N; if (idx < 0) idx += N;
        QChar c = m_seq.at(idx);
        QPointF onRing = mapBase(b, 2, g);
        if (!view.contains(onRing)) continue;
        if (!letters) {
            p.setPen(QPen(baseColor(c), 1.4));
            p.drawLine(onRing, mapBase(b, 6, g));
        } else {
            QPointF pt = mapBase(b, 11, g);
            p.save();
            p.translate(pt);
            if (!m_linear) p.rotate(2.0 * M_PI * (b - m_focus) / N * 180.0 / M_PI);
            p.setPen(baseColor(c));
            p.drawText(QRectF(-7, -9, 14, 18), Qt::AlignCenter, QString(c));
            p.restore();
        }
    }
}

QColor CircularMapView::baseColor(QChar c) const {
    switch (c.toLatin1()) {
        case 'A': return QColor("#5fb45f");
        case 'C': return QColor("#5b9bd5");
        case 'G': return QColor("#f0a93b");
        case 'T': return QColor("#e06666");
        default:  return QColor("#9d9d9d");
    }
}

// --------------------------------------------------------------- genetics ----

QChar CircularMapView::translateCodon(const QString &codon, QString *three, QString *full) {
    static const QHash<QString, QChar> table = {
        {"TTT",'F'},{"TTC",'F'},{"TTA",'L'},{"TTG",'L'},{"CTT",'L'},{"CTC",'L'},
        {"CTA",'L'},{"CTG",'L'},{"ATT",'I'},{"ATC",'I'},{"ATA",'I'},{"ATG",'M'},
        {"GTT",'V'},{"GTC",'V'},{"GTA",'V'},{"GTG",'V'},{"TCT",'S'},{"TCC",'S'},
        {"TCA",'S'},{"TCG",'S'},{"CCT",'P'},{"CCC",'P'},{"CCA",'P'},{"CCG",'P'},
        {"ACT",'T'},{"ACC",'T'},{"ACA",'T'},{"ACG",'T'},{"GCT",'A'},{"GCC",'A'},
        {"GCA",'A'},{"GCG",'A'},{"TAT",'Y'},{"TAC",'Y'},{"TAA",'*'},{"TAG",'*'},
        {"CAT",'H'},{"CAC",'H'},{"CAA",'Q'},{"CAG",'Q'},{"AAT",'N'},{"AAC",'N'},
        {"AAA",'K'},{"AAG",'K'},{"GAT",'D'},{"GAC",'D'},{"GAA",'E'},{"GAG",'E'},
        {"TGT",'C'},{"TGC",'C'},{"TGA",'*'},{"TGG",'W'},{"CGT",'R'},{"CGC",'R'},
        {"CGA",'R'},{"CGG",'R'},{"AGT",'S'},{"AGC",'S'},{"AGA",'R'},{"AGG",'R'},
        {"GGT",'G'},{"GGC",'G'},{"GGA",'G'},{"GGG",'G'},
    };
    static const QHash<char, QPair<QString,QString>> names = {
        {'A',{"Ala","Alanine"}},{'R',{"Arg","Arginine"}},{'N',{"Asn","Asparagine"}},
        {'D',{"Asp","Aspartic acid"}},{'C',{"Cys","Cysteine"}},{'E',{"Glu","Glutamic acid"}},
        {'Q',{"Gln","Glutamine"}},{'G',{"Gly","Glycine"}},{'H',{"His","Histidine"}},
        {'I',{"Ile","Isoleucine"}},{'L',{"Leu","Leucine"}},{'K',{"Lys","Lysine"}},
        {'M',{"Met","Methionine"}},{'F',{"Phe","Phenylalanine"}},{'P',{"Pro","Proline"}},
        {'S',{"Ser","Serine"}},{'T',{"Thr","Threonine"}},{'W',{"Trp","Tryptophan"}},
        {'Y',{"Tyr","Tyrosine"}},{'V',{"Val","Valine"}},{'*',{"Stop","Stop"}},
    };
    QChar aa = table.value(codon, '?');
    auto it = names.find(aa.toLatin1());
    if (three) *three = (it != names.end()) ? it->first  : "Xaa";
    if (full)  *full  = (it != names.end()) ? it->second : "Unknown";
    return aa;
}
