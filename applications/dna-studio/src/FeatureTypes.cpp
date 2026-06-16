#include "FeatureTypes.h"

namespace FeatureTypes {

const QVector<Info> &all() {
    // key, color, directional. Ordered roughly as Geneious groups them.
    static const QVector<Info> table = {
        {"CDS",            QColor("#f2c14e"), true},
        {"gene",           QColor("#5ec27a"), true},
        {"mRNA",           QColor("#4ec9b0"), true},
        {"tRNA",           QColor("#4ec9b0"), true},
        {"rRNA",           QColor("#4ec9b0"), true},
        {"ncRNA",          QColor("#4ec9b0"), true},
        {"misc_RNA",       QColor("#4ec9b0"), true},
        {"promoter",       QColor("#8bc34a"), true},
        {"RBS",            QColor("#e0a042"), true},
        {"terminator",     QColor("#e06666"), false},
        {"enhancer",       QColor("#9ccc65"), false},
        {"polyA_signal",   QColor("#d0894a"), false},
        {"5'UTR",          QColor("#c0b15a"), true},
        {"3'UTR",          QColor("#c0b15a"), true},
        {"exon",           QColor("#f2c14e"), true},
        {"intron",         QColor("#8a8f98"), true},
        {"sig_peptide",    QColor("#d16ad1"), true},
        {"mat_peptide",    QColor("#d98cc0"), true},
        {"primer_bind",    QColor("#6fb7e6"), true},
        {"protein_bind",   QColor("#b07cc6"), false},
        {"regulatory",     QColor("#c586c0"), false},
        {"rep_origin",     QColor("#4f9fe0"), false},
        {"oriT",           QColor("#4f9fe0"), true},
        {"repeat_region",  QColor("#b08968"), false},
        {"mobile_element", QColor("#a9744f"), true},
        {"stem_loop",      QColor("#b07cc6"), false},
        {"misc_feature",   QColor("#9aa0a6"), false},
        {"source",         QColor("#6e6e6e"), false},
    };
    return table;
}

QColor colorFor(const QString &key) {
    for (const Info &i : all())
        if (i.key.compare(key, Qt::CaseInsensitive) == 0) return i.color;
    return QColor("#9aa0a6");
}

bool directionalFor(const QString &key) {
    for (const Info &i : all())
        if (i.key.compare(key, Qt::CaseInsensitive) == 0) return i.directional;
    return false;
}

} // namespace FeatureTypes
