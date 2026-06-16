#include "AnnotationDialog.h"
#include "FeatureTypes.h"

#include <QFormLayout>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QComboBox>
#include <QPushButton>
#include <QDialogButtonBox>
#include <QColorDialog>
#include <QPixmap>

namespace {
QIcon swatch(const QColor &c) {
    QPixmap pm(14, 14); pm.fill(c);
    return QIcon(pm);
}
}

AnnotationDialog::AnnotationDialog(int lo, int hi, QWidget *parent) : QDialog(parent) {
    setWindowTitle("Add Annotation");
    setModal(true);

    auto *form = new QFormLayout;

    form->addRow("Region:", new QLabel(QString("%L1 – %L2  (%L3 bp)")
                                           .arg(lo).arg(hi).arg(hi - lo + 1)));

    m_name = new QLineEdit("new feature");
    m_name->selectAll();
    form->addRow("Name:", m_name);

    m_type = new QComboBox;
    for (const auto &t : FeatureTypes::all())
        m_type->addItem(swatch(t.color), t.key);
    m_type->setCurrentText("CDS");
    form->addRow("Type:", m_type);

    m_dir = new QComboBox;
    m_dir->addItems({"Forward →", "Reverse ←", "None"});
    form->addRow("Direction:", m_dir);

    m_colorBtn = new QPushButton("Color…");
    form->addRow("Color:", m_colorBtn);

    auto *buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);

    auto *root = new QVBoxLayout(this);
    root->addLayout(form);
    root->addWidget(buttons);

    connect(buttons, &QDialogButtonBox::accepted, this, &QDialog::accept);
    connect(buttons, &QDialogButtonBox::rejected, this, &QDialog::reject);
    connect(m_type, &QComboBox::currentTextChanged, this, &AnnotationDialog::onTypeChanged);
    connect(m_colorBtn, &QPushButton::clicked, this, &AnnotationDialog::pickColor);

    onTypeChanged();   // initialise color + direction from the default type
}

void AnnotationDialog::onTypeChanged() {
    const QString t = m_type->currentText();
    m_color = FeatureTypes::colorFor(t);
    const bool dir = FeatureTypes::directionalFor(t);
    if (dir) {
        m_dir->setEnabled(true);
        if (m_dir->currentIndex() == 2) m_dir->setCurrentIndex(0);  // None → Forward
    } else {
        m_dir->setCurrentIndex(2);   // None
        m_dir->setEnabled(false);
    }
    refreshSwatch();
}

void AnnotationDialog::pickColor() {
    QColor c = QColorDialog::getColor(m_color, this, "Annotation color");
    if (c.isValid()) { m_color = c; refreshSwatch(); }
}

void AnnotationDialog::refreshSwatch() {
    m_colorBtn->setIcon(swatch(m_color));
}

QString AnnotationDialog::name() const { return m_name->text().trimmed(); }
QString AnnotationDialog::type() const { return m_type->currentText(); }

int AnnotationDialog::strand() const {
    switch (m_dir->currentIndex()) {
        case 0:  return 1;
        case 1:  return -1;
        default: return 0;
    }
}

bool AnnotationDialog::get(QWidget *parent, int lo, int hi,
                          QString &name, QString &type, int &strand, QColor &color) {
    AnnotationDialog d(lo, hi, parent);
    if (d.exec() != QDialog::Accepted || d.name().isEmpty()) return false;
    name = d.name(); type = d.type(); strand = d.strand(); color = d.color();
    return true;
}
