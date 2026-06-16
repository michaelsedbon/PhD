#pragma once

#include <QString>
#include <QColor>
#include <QVector>

// The INSDC / GenBank feature-key vocabulary that Geneious exposes in its
// annotation editor. (FASTA carries no annotations of its own — these come from
// GenBank/EMBL feature tables.) Each type has a default color and whether it is
// drawn directionally (as an arrow) or as a plain band.
namespace FeatureTypes {

struct Info { QString key; QColor color; bool directional; };

const QVector<Info> &all();
QColor colorFor(const QString &key);
bool   directionalFor(const QString &key);

} // namespace FeatureTypes
