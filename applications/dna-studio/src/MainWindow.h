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
class QMenu;
class QAction;
class QLineEdit;
class QWidget;

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
    void onSelectionChanged(int lo, int hi, int length);
    void onDocumentEdited();
    void openFiles();
    void showFindBar();
    void doFind();

private:
    void buildMenuBar();
    void buildEditMenu();          // populated after the map exists
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
    QLabel      *m_selStatus = nullptr;
    QLabel      *m_selLabel = nullptr;
    QCheckBox   *m_linearCheck = nullptr;
    QTreeWidget *m_tree = nullptr;
    QTableWidget *m_table = nullptr;
    QMenu       *m_editMenu = nullptr;
    QAction     *m_editAction = nullptr;   // "Allow Editing" toggle

    // find bar
    QWidget   *m_findBar = nullptr;
    QLineEdit *m_findEdit = nullptr;
    QSpinBox  *m_findMm = nullptr;
    QCheckBox *m_findBoth = nullptr;
    QLabel    *m_findCount = nullptr;

    QHash<QString, QVector<SequenceDocument>> m_library;   // folder name → documents
    QString m_currentFolder;
};
