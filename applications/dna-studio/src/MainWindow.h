#pragma once

#include <QMainWindow>
#include <QHash>
#include <QVector>
#include "SequenceDocument.h"

class CircularMapView;
class QLabel;
class QSpinBox;
class QCheckBox;
class QTreeWidget;
class QTableWidget;

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);

    // Import sequence files into a folder (default: current). Used by File→Open and the CLI.
    void importPaths(const QStringList &paths, const QString &folder = QString());

private slots:
    void onHover(int base, QChar nt, int residue, const QString &aa);
    void onZoomChanged(int percent);
    void onFolderChanged();
    void onDocRowChanged();
    void openFiles();

private:
    void buildMenuBar();
    void buildMainToolBar();
    QWidget *buildSourceTree();
    QWidget *buildDocumentTable();
    QWidget *buildViewer();
    QWidget *buildOptionsPanel();
    void buildStatusBar();

    void loadSampleLibrary();
    void populateTable(const QString &folder);
    void showDocument(const SequenceDocument &doc);

    CircularMapView *m_map = nullptr;
    QSpinBox    *m_zoomBox = nullptr;
    QLabel      *m_memLabel = nullptr;
    QLabel      *m_hoverLabel = nullptr;
    QLabel      *m_selLabel = nullptr;
    QCheckBox   *m_linearCheck = nullptr;
    QTreeWidget *m_tree = nullptr;
    QTableWidget *m_table = nullptr;

    QHash<QString, QVector<SequenceDocument>> m_library;   // folder name → documents
    QString m_currentFolder;
};
