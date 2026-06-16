#include "CircularMapView.h"
#include "SequenceIO.h"

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
    m_undo.clear();
    emitSelection();
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

void CircularMapView::setZoomPercent(int percent) {
    double p = qBound(minPpb() * 0.6, percent / 100.0 * kPpbAt100, kMaxPpb);
    if (qFuzzyCompare(p, m_ppb)) return;
    m_ppb = p; m_userZoomed = true; emit zoomChanged(zoomPercent()); update();
}

void CircularMapView::applyZoom(double factor) {
    double p = qBound(minPpb() * 0.6, m_ppb * factor, kMaxPpb);
    if (qFuzzyCompare(p, m_ppb)) return;
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
    m_selecting = true;
    int b = int(std::floor(m_pressBase)) + 1;
    m_selLo = m_selHi = b;
    update();
}

void CircularMapView::mouseMoveEvent(QMouseEvent *e) {
    if (m_seq.isEmpty()) return;
    Geom g = geometry();
    double bd = baseAtPoint(e->position(), g);

    if (m_selecting) {
        int a = int(std::floor(m_pressBase)) + 1;
        int b = int(std::floor(bd)) + 1;
        m_selLo = qMin(a, b); m_selHi = qMax(a, b);
        emitSelection();
        update();
        return;
    }

    const int N = m_seq.size();
    int b0 = int(std::floor(bd)) % N; if (b0 < 0) b0 += N;
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
    Geom g = geometry();
    double rel = baseAtPoint(e->position(), g);
    if (std::abs(rel - m_pressBase) < 0.5) clearSelection();   // a plain click clears
    else emitSelection();
    update();
}

void CircularMapView::contextMenuEvent(QContextMenuEvent *e) {
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
    bool ok = false;
    QString name = QInputDialog::getText(this, "Add Annotation",
        QString("Name for annotation over %L1–%L2:").arg(m_selLo).arg(m_selHi),
        QLineEdit::Normal, "new feature", &ok);
    if (!ok || name.trimmed().isEmpty()) return;

    pushUndo();
    Feature f;
    f.name = name.trimmed();
    f.start = m_selLo; f.end = m_selHi; f.strand = 1;
    f.color = QColor("#c586c0");
    double minOff = 0;
    for (const Feature &e : m_features) minOff = qMin(minOff, e.offsetPx);
    f.offsetPx = minOff - 15.0;
    f.thickness = 12;
    m_features.append(f);
    emit documentEdited();
    update();
}

void CircularMapView::undo() {
    if (m_undo.isEmpty()) return;
    Snapshot s = m_undo.takeLast();
    m_seq = s.seq; m_features = s.feats; m_selLo = s.lo; m_selHi = s.hi;
    emitSelection();
    emit documentEdited();
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
    for (const Feature &f : m_features) {
        double startB = f.start - 1;
        double lenB = (f.end >= f.start) ? (f.end - f.start + 1)
                                         : (N - f.start + 1 + f.end);
        if (lenB <= 0) continue;
        double half = f.thickness / 2.0;

        p.setPen(QPen(f.color.darker(140), 1.0));
        p.setBrush(f.color);
        p.drawPath(bandPath(startB, lenB, f.offsetPx, f.thickness, g));

        double tipB = (f.strand >= 0) ? startB + lenB : startB;
        double backB = tipB - f.strand * qMin(lenB, 18.0 / m_ppb);
        QPainterPath arrow;
        arrow.moveTo(mapBase(tipB, f.offsetPx, g));
        arrow.lineTo(mapBase(backB, f.offsetPx + half * 1.6, g));
        arrow.lineTo(mapBase(backB, f.offsetPx - half * 1.6, g));
        arrow.closeSubpath();
        p.drawPath(arrow);

        if (m_showNames && lenB * m_ppb > 40) {
            double midB = startB + lenB / 2.0;
            QPointF mp = mapBase(midB, f.offsetPx, g);
            p.save();
            p.translate(mp);
            if (!m_linear) {
                double deg = 2.0 * M_PI * (midB - m_focus) / N * 180.0 / M_PI + 90.0;
                if (deg > 90 && deg < 270) deg += 180;
                p.rotate(deg);
            }
            QFont lf = font(); lf.setPointSizeF(8.5); lf.setBold(true); p.setFont(lf);
            p.setPen(Qt::white);
            p.drawText(QRectF(-80, -8, 160, 16), Qt::AlignCenter, f.name);
            p.restore();
        }
    }
}

void CircularMapView::drawSelection(QPainter &p, const Geom &g) {
    if (!hasSelection()) return;
    double startB = m_selLo - 1;
    double lenB = m_selHi - m_selLo + 1;
    p.setPen(QPen(QColor(86, 156, 214), 1.2));
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
