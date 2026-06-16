#pragma once

#include <QString>
#include <QVector>
#include <QColor>

// A single annotated feature on the sequence (gene, CDS, origin, …).
// Coordinates are 1-based inclusive. If end < start the feature wraps the origin.
struct Feature {
    QString name;
    QString type = "misc_feature";   // INSDC/GenBank feature key
    int start = 1;
    int end = 1;
    int strand = 1;          // +1 forward, -1 reverse, 0 none
    bool directional = true; // draw as an arrow (false → plain capsule)
    QColor color = Qt::yellow;
    double offsetPx = -14;   // radial offset from the DNA ring centerline (+ outward, - inward)
    double thickness = 12;   // band thickness in px
};

// One sequence record — a plasmid, gene, primer, etc.
struct SequenceDocument {
    QString name;
    QString description;
    QString organism = "—";
    QString moleculeType = "DNA";
    QString modified = "—";
    QString sequence;            // ACGT…
    bool circular = true;
    QVector<Feature> features;

    int length() const { return sequence.size(); }
    QString topology() const { return circular ? "circular" : "linear"; }
};
