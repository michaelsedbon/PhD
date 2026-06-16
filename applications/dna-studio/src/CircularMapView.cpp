#include "CircularMapView.h"

#include <QPainter>
#include <QPainterPath>
#include <QWheelEvent>
#include <QMouseEvent>
#include <QHash>
#include <QPair>
#include <cmath>

namespace {

constexpr double kPpbAt100  = 8.0;   // px/base that we call "100%"
constexpr double kMaxPpb    = 40.0;  // fully zoomed in (big readable letters)
constexpr double kFitMargin = 90.0;  // viewport padding when the whole circle fits

// True if 1-based position `pos` falls inside feature `f` (handles origin wrap).
bool inFeature(const Feature &f, int pos) {
    if (f.end >= f.start) return pos >= f.start && pos <= f.end;
    return pos >= f.start || pos <= f.end;   // wraps the origin
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
    setAttribute(Qt::WA_OpaquePaintEvent);
}

void CircularMapView::setSequence(const QString &seq) {
    m_seq = seq.toUpper();
    m_focus = 0.0;
    update();
}

void CircularMapView::setFeatures(const QVector<Feature> &features) {
    m_features = features;
    update();
}

// ---------------------------------------------------------------- geometry ---

double CircularMapView::minPpb() const {
    const int N = qMax(1, m_seq.size());
    double m = qMin(width(), height()) - kFitMargin;
    if (m < 60) m = 60;
    return m * M_PI / N;   // 2R == m  ⇒  ppb == m·π/N
}

CircularMapView::Geom CircularMapView::geometry() const {
    Geom g;
    const int N = qMax(1, m_seq.size());
    g.R  = (N * m_ppb) / (2.0 * M_PI);
    g.Cx = width() / 2.0;
    g.fits = (!m_linear) && (2 * g.R <= qMin(width(), height()) - kFitMargin);
    if (g.fits) {
        g.Cy = height() / 2.0;                 // whole plasmid centered
    } else {
        g.Cy = height() * 0.40 + g.R;          // focus pinned near top; center slides down
    }
    return g;
}

QPointF CircularMapView::mapBase(double base, double offsetPx, const Geom &g) const {
    if (m_linear) {
        double x = g.Cx + (base - m_focus) * m_ppb;
        double y = height() * 0.45 - offsetPx;     // +offset = outward = up
        return {x, y};
    }
    const int N = qMax(1, m_seq.size());
    double phi = 2.0 * M_PI * (base - m_focus) / N;   // 0 == top, clockwise
    double r = g.R + offsetPx;
    return { g.Cx + r * std::sin(phi), g.Cy - r * std::cos(phi) };
}

double CircularMapView::baseAtPoint(const QPointF &p, const Geom &g) const {
    const int N = qMax(1, m_seq.size());
    double base;
    if (m_linear) {
        base = m_focus + (p.x() - g.Cx) / m_ppb;
    } else {
        double phi = std::atan2(p.x() - g.Cx, -(p.y() - g.Cy));   // 0 == top
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
    m_linear = false;
    m_userZoomed = false;
    m_ppb = minPpb();
    emit zoomChanged(zoomPercent());
    update();
}

// ------------------------------------------------------------------ events ---

void CircularMapView::wheelEvent(QWheelEvent *e) {
    double steps = e->angleDelta().y() / 120.0;
    if (steps == 0) steps = e->angleDelta().x() / 120.0;

    if (e->modifiers() & Qt::AltModifier) {          // Option/Alt + scroll → zoom
        applyZoom(std::pow(1.18, steps));
    } else {                                          // scroll → rotate / scroll along
        const int N = qMax(1, m_seq.size());
        double basesPerStep = qBound(N * 0.005, 50.0 / m_ppb, N * 0.06);
        m_focus -= steps * basesPerStep;             // scroll down advances forward
        m_focus = std::fmod(m_focus, double(N));
        if (m_focus < 0) m_focus += N;
        update();
    }
    e->accept();
}

void CircularMapView::resizeEvent(QResizeEvent *) {
    if (!m_userZoomed) {               // keep the whole plasmid fitted until the user zooms
        m_ppb = minPpb();
        emit zoomChanged(zoomPercent());
    }
    update();
}

void CircularMapView::mouseMoveEvent(QMouseEvent *e) {
    if (m_seq.isEmpty()) return;
    const int N = m_seq.size();
    Geom g = geometry();
    int b0 = int(std::floor(baseAtPoint(e->position(), g))) % N;
    if (b0 < 0) b0 += N;
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

    // DNA backbone
    p.setPen(QPen(QColor("#9d9d9d"), 1.4));
    p.setBrush(Qt::NoBrush);
    if (m_linear) {
        double y = height() * 0.45;
        p.drawLine(QPointF(0, y), QPointF(width(), y));
    } else {
        p.drawEllipse(QPointF(g.Cx, g.Cy), g.R, g.R);   // Qt clips to viewport
    }

    drawRuler(p, g);
    if (m_showAnnotations) drawFeatures(p, g);
    if (m_ppb >= 3.0)      drawBases(p, g);

    // Center / bottom title
    p.setPen(QColor("#cccccc"));
    QFont tf = font(); tf.setPointSizeF(11); p.setFont(tf);
    QPointF c = g.fits ? QPointF(g.Cx, height() / 2.0) : QPointF(g.Cx, height() - 34);
    p.drawText(QRectF(c.x() - 150, c.y() - 16, 300, 16), Qt::AlignCenter, m_title);
    p.drawText(QRectF(c.x() - 150, c.y(), 300, 16), Qt::AlignCenter,
               QString("%L1 bp").arg(m_seq.size()));
}

void CircularMapView::drawRuler(QPainter &p, const Geom &g) {
    const int N = m_seq.size();
    double interval = niceInterval(70.0 / m_ppb);
    QFont f = font(); f.setPointSizeF(8.0); p.setFont(f);
    QRectF view = rect().adjusted(-40, -40, 40, 40);

    for (double b = 0; b < N; b += interval) {
        QPointF a = mapBase(b, 1, g);
        QPointF o = mapBase(b, 7, g);
        if (!view.contains(a)) continue;
        p.setPen(QPen(QColor("#7a7a7a"), 1.0));
        p.drawLine(a, o);
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

        int segs = qBound(2, int(lenB * m_ppb / 6.0), 600);
        QPainterPath band;
        for (int i = 0; i <= segs; ++i) {              // outer edge forward
            double b = startB + lenB * i / segs;
            QPointF pt = mapBase(b, f.offsetPx + half, g);
            (i == 0) ? band.moveTo(pt) : band.lineTo(pt);
        }
        for (int i = segs; i >= 0; --i) {              // inner edge back
            double b = startB + lenB * i / segs;
            band.lineTo(mapBase(b, f.offsetPx - half, g));
        }
        band.closeSubpath();
        p.setPen(QPen(f.color.darker(140), 1.0));
        p.setBrush(f.color);
        p.drawPath(band);

        // strand arrowhead
        double tipB = (f.strand >= 0) ? startB + lenB : startB;
        double backB = tipB - f.strand * qMin(lenB, 18.0 / m_ppb);
        QPointF tip  = mapBase(tipB, f.offsetPx, g);
        QPointF wOut = mapBase(backB, f.offsetPx + half * 1.6, g);
        QPointF wIn  = mapBase(backB, f.offsetPx - half * 1.6, g);
        QPainterPath arrow; arrow.moveTo(tip); arrow.lineTo(wOut); arrow.lineTo(wIn);
        arrow.closeSubpath();
        p.drawPath(arrow);

        // label along the band
        if (m_showNames && lenB * m_ppb > 40) {
            double midB = startB + lenB / 2.0;
            QPointF mp = mapBase(midB, f.offsetPx, g);
            p.save();
            p.translate(mp);
            if (!m_linear) {
                double phi = 2.0 * M_PI * (midB - m_focus) / N;
                double deg = phi * 180.0 / M_PI + 90.0;   // tangent
                if (deg > 90 && deg < 270) deg += 180;    // keep upright
                p.rotate(deg);
            }
            QFont lf = font(); lf.setPointSizeF(8.5); lf.setBold(true); p.setFont(lf);
            p.setPen(Qt::white);
            p.drawText(QRectF(-80, -8, 160, 16), Qt::AlignCenter, f.name);
            p.restore();
        }
    }
}

void CircularMapView::drawBases(QPainter &p, const Geom &g) {
    const int N = m_seq.size();
    bool letters = m_ppb >= 7.0;
    double visHalf = width() / m_ppb;                  // bases spanning the viewport width
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

        if (!letters) {                                // colored tick marks
            QPointF outp = mapBase(b, 6, g);
            p.setPen(QPen(baseColor(c), 1.4));
            p.drawLine(onRing, outp);
        } else {                                        // readable letters
            QPointF pt = mapBase(b, 11, g);
            p.save();
            p.translate(pt);
            if (!m_linear) {
                double phi = 2.0 * M_PI * (b - m_focus) / N;
                p.rotate(phi * 180.0 / M_PI);          // upright pointing outward
            }
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
