#pragma once

#include <QWidget>
#include <QVector>
#include <QString>
#include <QColor>

#include "SequenceDocument.h"

// The plasmid / sequence view — the heart of the app.
//
//  * Scroll wheel            → rotate the plasmid (spin the focus base).
//  * Option/Alt + scroll     → zoom in / out (radius grows, arc flattens).
//  * The focus base stays anchored near the top-center; as you zoom in the
//    circle's center slides down off-screen so the sequence is always centered.
//  * Progressive level-of-detail: arcs → bp ruler → annotation bands → colored
//    base ticks → readable A/C/G/T letters → amino-acid translation.
class CircularMapView : public QWidget {
    Q_OBJECT
public:
    explicit CircularMapView(QWidget *parent = nullptr);

    void setSequence(const QString &seq);
    void setFeatures(const QVector<Feature> &features);
    void setTitle(const QString &name) { m_title = name; update(); }
    void setDocument(const SequenceDocument &doc);   // load a whole record + fit

    int    zoomPercent() const;
    void   setZoomPercent(int percent);

public slots:
    void setShowAnnotations(bool on) { m_showAnnotations = on; update(); }
    void setShowNames(bool on)       { m_showNames = on; update(); }
    void setShowTranslation(bool on) { m_translate = on; update(); }
    void setLinearView(bool on)      { m_linear = on; update(); }
    void zoomIn()                    { applyZoom(1.25); }
    void zoomOut()                   { applyZoom(1.0 / 1.25); }
    void fitToView();                // zoom out so the whole plasmid is visible

signals:
    void hovered(int base, QChar nucleotide, int residue, const QString &aa);
    void zoomChanged(int percent);

protected:
    void paintEvent(QPaintEvent *) override;
    void wheelEvent(QWheelEvent *) override;
    void mouseMoveEvent(QMouseEvent *) override;
    void resizeEvent(QResizeEvent *) override;

private:
    struct Geom { double Cx, Cy, R; bool fits; };
    Geom geometry() const;                     // current circle center + radius
    QPointF mapBase(double base, double offsetPx, const Geom &g) const;
    double  baseAtPoint(const QPointF &p, const Geom &g) const;
    void    applyZoom(double factor);
    double  minPpb() const;                     // ppb at which whole plasmid just fits

    void drawRuler(QPainter &p, const Geom &g);
    void drawFeatures(QPainter &p, const Geom &g);
    void drawBases(QPainter &p, const Geom &g);

    QColor baseColor(QChar c) const;
    static QChar translateCodon(const QString &codon, QString *threeLetter, QString *fullName);

    QString m_seq;
    QString m_title = "untitled";
    QVector<Feature> m_features;

    double m_ppb   = 0.05;   // pixels per base (the zoom level)
    double m_focus = 0.0;    // base index anchored at the top / focus point

    bool m_showAnnotations = true;
    bool m_showNames       = true;
    bool m_translate       = false;
    bool m_linear          = false;
    bool m_userZoomed      = false;   // once true, stop auto-fitting on resize
};
