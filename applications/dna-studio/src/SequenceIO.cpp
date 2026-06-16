#include "SequenceIO.h"
#include "FeatureTypes.h"

#include <QFile>
#include <QFileInfo>
#include <QTextStream>
#include <QRegularExpression>
#include <algorithm>
#include <climits>

namespace SequenceIO {

namespace {

QString trimQual(QString s) {
    s = s.trimmed();
    if (s.startsWith('"')) s.remove(0, 1);
    if (s.endsWith('"'))   s.chop(1);
    return s;
}

} // namespace

// Greedy radial-track allocation so overlapping features stack inward.
void layoutFeatures(QVector<Feature> &features) {
    std::sort(features.begin(), features.end(),
              [](const Feature &a, const Feature &b){ return a.start < b.start; });
    QVector<int> rowEnd;                            // last end on each row
    for (Feature &f : features) {
        int row = 0;
        for (; row < rowEnd.size(); ++row)
            if (f.start > rowEnd[row]) break;
        if (row == rowEnd.size()) rowEnd.append(0);
        rowEnd[row] = f.end;
        f.offsetPx  = -18.0 - row * 22.0;
        f.thickness = 17.0;
    }
}

// ------------------------------------------------------------------ FASTA ----

SequenceDocument loadFasta(const QString &path, bool *ok) {
    SequenceDocument doc;
    QFile f(path);
    if (!f.open(QFile::ReadOnly | QFile::Text)) { if (ok) *ok = false; return doc; }
    QTextStream in(&f);
    QString seq;
    bool first = true;
    while (!in.atEnd()) {
        QString line = in.readLine();
        if (line.startsWith('>')) {
            if (!first) break;                      // only the first record
            line.remove(0, 1);
            int sp = line.indexOf(QRegularExpression("\\s"));
            doc.name = (sp < 0) ? line.trimmed() : line.left(sp);
            doc.description = (sp < 0) ? "" : line.mid(sp + 1).trimmed();
            first = false;
        } else {
            for (QChar c : line)
                if (c.isLetter()) seq += c.toUpper();
        }
    }
    doc.sequence = seq;
    doc.circular = false;                            // FASTA carries no topology
    doc.moleculeType = "DNA";
    if (doc.name.isEmpty()) doc.name = QFileInfo(path).completeBaseName();
    doc.modified = QFileInfo(path).lastModified().toString("dd MMM yyyy hh:mm AP");
    if (ok) *ok = !seq.isEmpty();
    return doc;
}

// ---------------------------------------------------------------- GenBank ----

SequenceDocument loadGenBank(const QString &path, bool *ok) {
    SequenceDocument doc;
    QFile f(path);
    if (!f.open(QFile::ReadOnly | QFile::Text)) { if (ok) *ok = false; return doc; }
    const QStringList lines = QString::fromUtf8(f.readAll()).split('\n');

    QString seq;
    bool inFeatures = false, inOrigin = false;
    Feature cur; bool haveCur = false;
    auto flush = [&] { if (haveCur) { doc.features.append(cur); haveCur = false; } };

    for (const QString &raw : lines) {
        const QString line = raw;
        if (line.startsWith("//")) break;

        if (line.startsWith("LOCUS")) {
            const QStringList t = line.split(QRegularExpression("\\s+"), Qt::SkipEmptyParts);
            if (t.size() > 1) doc.name = t[1];
            doc.circular = line.contains("circular", Qt::CaseInsensitive);
            continue;
        }
        if (line.startsWith("DEFINITION")) { doc.description = line.mid(12).trimmed(); continue; }
        if (line.startsWith("  ORGANISM")) { doc.organism = line.mid(12).trimmed(); continue; }
        if (line.startsWith("FEATURES"))   { inFeatures = true; continue; }
        if (line.startsWith("ORIGIN"))     { flush(); inFeatures = false; inOrigin = true; continue; }
        if (!line.isEmpty() && !line.at(0).isSpace()) { inFeatures = false; } // a new top-level key

        if (inOrigin) {
            for (QChar c : line) if (c.isLetter()) seq += c.toUpper();
            continue;
        }

        if (inFeatures) {
            // Feature key line: 5 spaces, key at col 5, location at col 21.
            if (line.length() > 6 && line.at(5) != ' ' && !line.trimmed().startsWith('/')) {
                flush();
                const QString key = line.mid(5, 16).trimmed();
                const QString loc = line.mid(21).trimmed();
                if (key.compare("source", Qt::CaseInsensitive) == 0) { haveCur = false; continue; }
                cur = Feature{};
                cur.name = key;
                cur.type = key;
                cur.color = FeatureTypes::colorFor(key);
                cur.directional = FeatureTypes::directionalFor(key);
                cur.strand = loc.contains("complement") ? -1 : 1;
                static const QRegularExpression num("(\\d+)");
                auto it = num.globalMatch(loc);
                int lo = INT_MAX, hi = 0;
                while (it.hasNext()) {
                    int v = it.next().captured(1).toInt();
                    lo = qMin(lo, v); hi = qMax(hi, v);
                }
                cur.start = (lo == INT_MAX) ? 1 : lo;
                cur.end   = (hi == 0) ? cur.start : hi;
                haveCur = true;
            } else if (haveCur && line.trimmed().startsWith('/')) {
                const QString q = line.trimmed();
                // Prefer a human label over the raw feature key.
                for (const QString &tag : {QStringLiteral("/gene="),
                                           QStringLiteral("/product="),
                                           QStringLiteral("/label=")}) {
                    if (q.startsWith(tag)) {
                        QString val = trimQual(q.mid(tag.length()));
                        if (!val.isEmpty()) cur.name = val;
                        break;
                    }
                }
            }
        }
    }
    flush();

    doc.sequence = seq;
    if (doc.name.isEmpty()) doc.name = QFileInfo(path).completeBaseName();
    doc.modified = QFileInfo(path).lastModified().toString("dd MMM yyyy hh:mm AP");
    layoutFeatures(doc.features);
    if (ok) *ok = !seq.isEmpty();
    return doc;
}

// --------------------------------------------------------------- dispatch ----

SequenceDocument load(const QString &path, bool *ok) {
    const QString ext = QFileInfo(path).suffix().toLower();
    if (ext == "gb" || ext == "gbk" || ext == "genbank" || ext == "gbff" || ext == "ape")
        return loadGenBank(path, ok);
    if (ext == "fa" || ext == "fasta" || ext == "fna" || ext == "ffn" || ext == "seq")
        return loadFasta(path, ok);

    // Sniff: GenBank starts with LOCUS, FASTA with '>'.
    QFile f(path);
    if (f.open(QFile::ReadOnly | QFile::Text)) {
        QString head = QString::fromUtf8(f.read(64));
        f.close();
        if (head.startsWith("LOCUS")) return loadGenBank(path, ok);
        if (head.trimmed().startsWith('>')) return loadFasta(path, ok);
    }
    return loadGenBank(path, ok);
}

QString fileFilter() {
    return "Sequence files (*.gb *.gbk *.genbank *.gbff *.fa *.fasta *.fna);;"
           "GenBank (*.gb *.gbk *.genbank *.gbff);;FASTA (*.fa *.fasta *.fna);;All files (*)";
}

} // namespace SequenceIO
