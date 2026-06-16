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
//  * Left-drag               → select a base range (highlighted on the map).
//  * Right-click             → context menu (Copy, Add Annotation, Delete, …).
//  * The focus base stays anchored near the top-center; as you zoom in the
//    circle's center slides down off-screen so the sequence is always centered.
//  * Progressive level-of-detail: arcs → bp ruler → annotation bands → colored
//    base ticks → readable A/C/G/T letters.
//
// Editing is locked by default; destructive ops require setEditable(true) AND a
// confirmation. Every mutation is undoable (Ctrl+Z).
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

    QString sequence() const { return m_seq; }
    const QVector<Feature> &features() const { return m_features; }
    bool isEditable() const { return m_editable; }
    bool hasSelection() const { return m_selLo > 0 && m_selHi >= m_selLo; }
    bool canUndo() const { return !m_undo.isEmpty(); }

    // Approximate search: find all windows matching `query` within `maxMismatch`
    // Hamming distance, optionally on both strands. Mismatched bases are flagged.
    void findMatches(const QString &query, int maxMismatch, bool bothStrands);
    void nextHit();
    void prevHit();
    void clearFind();

public slots:
    void setShowAnnotations(bool on) { m_showAnnotations = on; update(); }
    void setShowNames(bool on)       { m_showNames = on; update(); }
    void setShowTranslation(bool on) { m_translate = on; update(); }
    void setLinearView(bool on)      { m_linear = on; update(); }
    void setEditable(bool on)        { m_editable = on; }
    void zoomIn()                    { applyZoom(1.25); }
    void zoomOut()                   { applyZoom(1.0 / 1.25); }
    void fitToView();                // zoom out so the whole plasmid is visible

    void selectAll();
    void clearSelection();
    void copySelection();
    void pasteClipboard();
    void deleteSelection();          // delete selected bases (protected)
    void deleteActive();             // delete the selected annotation, else selected bases
    void editSelectedFeature();      // open the editor for the selected annotation
    void addAnnotation();
    void undo();

signals:
    void hovered(int base, QChar nucleotide, int residue, const QString &aa);
    void zoomChanged(int percent);
    void selectionChanged(int lo, int hi, int length);   // length 0 == no selection
    void documentEdited();
    void findResults(int count, int current);            // current is 1-based, 0 == none

protected:
    void paintEvent(QPaintEvent *) override;
    void wheelEvent(QWheelEvent *) override;
    void mousePressEvent(QMouseEvent *) override;
    void mouseMoveEvent(QMouseEvent *) override;
    void mouseReleaseEvent(QMouseEvent *) override;
    void mouseDoubleClickEvent(QMouseEvent *) override;
    void contextMenuEvent(QContextMenuEvent *) override;
    void resizeEvent(QResizeEvent *) override;

private:
    struct Geom { double Cx, Cy, R; bool fits; };
    Geom geometry() const;
    QPointF mapBase(double base, double offsetPx, const Geom &g) const;
    double  baseAtPoint(const QPointF &p, const Geom &g) const;
    void    applyZoom(double factor);
    double  minPpb() const;

    QPainterPath bandPath(double startB, double lenB, double offset,
                          double thickness, const Geom &g) const;
    void drawRuler(class QPainter &p, const Geom &g);
    void drawFeatures(class QPainter &p, const Geom &g);
    void drawArcLabel(class QPainter &p, const QString &text, double centerBase,
                      double offsetPx, const QFont &font, const Geom &g);
    void drawFindHits(class QPainter &p, const Geom &g);
    void drawSelection(class QPainter &p, const Geom &g);
    void drawBases(class QPainter &p, const Geom &g);

    QColor baseColor(QChar c) const;
    QString selectionText() const;
    void pushUndo();
    void emitSelection();
    void centerOnSelection();   // anchor m_focus on the selection center (keeps it centered on zoom)
    int  featureAt(const QPointF &pt) const;   // index of the feature under a point, or -1
    void gotoCurrentHit();
    static QString reverseComplement(const QString &s);
    static QChar translateCodon(const QString &codon, QString *threeLetter, QString *fullName);

    QString m_seq;
    QString m_title = "untitled";
    QVector<Feature> m_features;

    double m_ppb   = 0.05;
    double m_focus = 0.0;

    bool m_showAnnotations = true;
    bool m_showNames       = true;
    bool m_translate       = false;
    bool m_linear          = false;
    bool m_userZoomed      = false;

    // selection (1-based inclusive; m_selLo <= 0 means none)
    int  m_selLo = -1, m_selHi = -1;
    bool m_selecting = false;
    bool m_dragged = false;
    double m_pressBase = 0;
    int  m_pressFeature = -1;       // feature under the press point (for click-to-select)
    int  m_selectedFeature = -1;    // currently selected annotation, or -1
    bool m_editable = false;

    struct Snapshot { QString seq; QVector<Feature> feats; int lo, hi; };
    QVector<Snapshot> m_undo;

    // find / approximate search
    struct FindHit { int start; int len; int strand; QVector<int> mm; }; // mm: 1-based mismatch positions
    QVector<FindHit> m_hits;
    int m_currentHit = -1;
};
