#pragma once

#include <QDialog>
#include <QString>
#include <QColor>

class QLineEdit;
class QComboBox;
class QPushButton;

// Geneious-style annotation editor: name, feature type (with per-type color),
// and direction. Direction is disabled for non-directional types. Used both to
// add a new annotation and to edit an existing one.
class AnnotationDialog : public QDialog {
    Q_OBJECT
public:
    AnnotationDialog(int lo, int hi, QWidget *parent = nullptr,
                     const QString &name = "new feature",
                     const QString &type = "CDS",
                     int strand = 1,
                     const QColor &color = QColor(),
                     const QString &title = "Add Annotation");

    QString name() const;
    QString type() const;
    int     strand() const;   // +1 forward, -1 reverse, 0 none
    QColor  color() const { return m_color; }

    // Convenience wrappers — return true if accepted.
    static bool get(QWidget *parent, int lo, int hi,
                    QString &name, QString &type, int &strand, QColor &color);
    static bool edit(QWidget *parent, int lo, int hi,
                     QString &name, QString &type, int &strand, QColor &color);

private slots:
    void onTypeChanged();
    void pickColor();

private:
    void refreshSwatch();

    QLineEdit   *m_name = nullptr;
    QComboBox   *m_type = nullptr;
    QComboBox   *m_dir = nullptr;
    QPushButton *m_colorBtn = nullptr;
    QColor       m_color;
};
