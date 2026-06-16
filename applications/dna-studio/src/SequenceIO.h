#pragma once

#include "SequenceDocument.h"
#include <QString>

// Minimal sequence file readers (FASTA + GenBank).
namespace SequenceIO {

SequenceDocument loadFasta(const QString &path, bool *ok = nullptr);
SequenceDocument loadGenBank(const QString &path, bool *ok = nullptr);

// Dispatch on file extension, falling back to content sniffing.
SequenceDocument load(const QString &path, bool *ok = nullptr);

// File dialog filter string.
QString fileFilter();

// Auto-assign radial tracks/colors to a feature list so bands don't overlap.
void layoutFeatures(QVector<Feature> &features);

} // namespace SequenceIO
