#include "NotebookWorkspace.h"
#include "LabConfig.h"

#include <QApplication>
#include <QMenuBar>
#include <QToolBar>
#include <QDockWidget>
#include <QTreeView>
#include <QFileSystemModel>
#include <QPlainTextEdit>
#include <QTextEdit>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QSplitter>
#include <QStatusBar>
#include <QFile>
#include <QFileInfo>
#include <QFontDatabase>

namespace {
QIcon ic(const QString &name) { return QIcon(QStringLiteral(":/icons/%1.svg").arg(name)); }
}

NotebookWorkspace::NotebookWorkspace(QWidget *parent) : Workspace(parent) {
    setWindowIcon(ic("edit"));

    auto *tb = addToolBar("Notebook");
    tb->setMovable(false);
    tb->setIconSize(QSize(18, 18));
    tb->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    auto *save = tb->addAction(ic("save"), "Save");
    connect(save, &QAction::triggered, this, &NotebookWorkspace::saveFile);
    tb->addSeparator();
    auto *prev = tb->addAction(ic("columns"), "Preview");
    prev->setCheckable(true); prev->setChecked(true);
    connect(prev, &QAction::triggered, this, &NotebookWorkspace::togglePreview);
    tb->addSeparator();
    tb->addAction(ic("dna"), "Link Construct");     // Phase 3
    tb->addAction(ic("upload"), "Export PDF");

    auto *leftDock = new QDockWidget("Vault", this);
    leftDock->setWidget(buildTree());
    leftDock->setFeatures(QDockWidget::DockWidgetMovable | QDockWidget::DockWidgetClosable);
    leftDock->setMinimumWidth(260);
    addDockWidget(Qt::LeftDockWidgetArea, leftDock);

    setCentralWidget(buildEditor());

    statusBar()->showMessage("Vault: " + LabConfig::repoRoot());
}

QWidget *NotebookWorkspace::buildTree() {
    m_fsModel = new QFileSystemModel(this);
    m_fsModel->setRootPath(LabConfig::repoRoot());
    m_fsModel->setNameFilters({"*.md", "*.markdown"});
    m_fsModel->setNameFilterDisables(false);   // hide non-matching files, keep folders

    m_tree = new QTreeView;
    m_tree->setModel(m_fsModel);
    m_tree->setRootIndex(m_fsModel->index(LabConfig::repoRoot()));
    for (int c = 1; c < m_fsModel->columnCount(); ++c) m_tree->hideColumn(c);  // name only
    m_tree->setHeaderHidden(true);
    m_tree->setAnimated(true);
    m_tree->setIndentation(14);
    connect(m_tree, &QTreeView::clicked, this, &NotebookWorkspace::onFileClicked);
    return m_tree;
}

QWidget *NotebookWorkspace::buildEditor() {
    auto *wrap = new QWidget;
    auto *v = new QVBoxLayout(wrap); v->setContentsMargins(0, 0, 0, 0); v->setSpacing(0);

    auto *bar = new QWidget; bar->setStyleSheet("background:#252526;border-bottom:1px solid #3c3c3c;");
    auto *bh = new QHBoxLayout(bar); bh->setContentsMargins(10, 5, 10, 5);
    m_pathLabel = new QLabel("Select a markdown file from the vault");
    m_pathLabel->setStyleSheet("color:#cfcfcf;font-size:12px;");
    bh->addWidget(m_pathLabel);
    bh->addStretch();
    m_dirtyLabel = new QLabel("");
    m_dirtyLabel->setStyleSheet("color:#d29922;font-size:12px;");
    bh->addWidget(m_dirtyLabel);
    v->addWidget(bar);

    auto *split = new QSplitter(Qt::Horizontal);

    m_source = new QPlainTextEdit;
    QFont mono("SF Mono"); mono.setStyleHint(QFont::Monospace); mono.setPointSize(12);
    if (!QFontDatabase::families().contains("SF Mono")) mono = QFontDatabase::systemFont(QFontDatabase::FixedFont);
    m_source->setFont(mono);
    m_source->setStyleSheet("QPlainTextEdit{background:#1e1e1e;color:#d4d4d4;border:none;padding:14px;}");
    m_source->setLineWrapMode(QPlainTextEdit::WidgetWidth);
    m_source->setPlaceholderText("Markdown source.");
    connect(m_source, &QPlainTextEdit::textChanged, this, &NotebookWorkspace::onSourceChanged);
    split->addWidget(m_source);

    m_preview = new QTextEdit;
    m_preview->setReadOnly(true);
    m_preview->setStyleSheet("QTextEdit{background:#191919;color:#d4d4d4;border-left:1px solid #333;padding:14px;}");
    split->addWidget(m_preview);

    split->setStretchFactor(0, 1);
    split->setStretchFactor(1, 1);
    split->setSizes({560, 560});
    v->addWidget(split, 1);
    return wrap;
}

void NotebookWorkspace::onFileClicked(const QModelIndex &index) {
    if (m_fsModel->isDir(index)) return;
    openFile(m_fsModel->filePath(index));
}

void NotebookWorkspace::openFile(const QString &path) {
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly)) return;
    m_openPath = path;
    QSignalBlocker block(m_source);          // don't mark dirty on programmatic load
    m_source->setPlainText(QString::fromUtf8(f.readAll()));
    m_dirty = false;
    m_dirtyLabel->clear();
    m_pathLabel->setText(QDir(LabConfig::repoRoot()).relativeFilePath(path));
    renderPreview();
}

void NotebookWorkspace::onSourceChanged() {
    if (!m_openPath.isEmpty()) {
        m_dirty = true;
        m_dirtyLabel->setText("● unsaved");
    }
    renderPreview();
}

void NotebookWorkspace::renderPreview() {
    if (!m_preview) return;
    // Qt's rich-text engine renders CommonMark + GFM tables natively.
    m_preview->setMarkdown(m_source->toPlainText());
}

void NotebookWorkspace::saveFile() {
    if (m_openPath.isEmpty() || !m_dirty) return;
    QFile f(m_openPath);
    if (f.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        f.write(m_source->toPlainText().toUtf8());
        f.close();
        m_dirty = false;
        m_dirtyLabel->clear();
        statusBar()->showMessage("Saved " + QFileInfo(m_openPath).fileName(), 2500);
    } else {
        statusBar()->showMessage("Could not write " + m_openPath, 4000);
    }
}

void NotebookWorkspace::togglePreview() {
    if (m_preview) m_preview->setVisible(!m_preview->isVisible());
}

void NotebookWorkspace::populateMenus(QMenuBar *mb) {
    QMenu *file = mb->addMenu("File");
    auto *save = file->addAction("Save");
    save->setShortcut(QKeySequence::Save);
    connect(save, &QAction::triggered, this, &NotebookWorkspace::saveFile);
    file->addAction("Export PDF…")->setEnabled(false);
    file->addSeparator();
    auto *quit = file->addAction("Quit");
    quit->setShortcut(QKeySequence::Quit);
    connect(quit, &QAction::triggered, qApp, &QApplication::quit);

    QMenu *edit = mb->addMenu("Edit");
    auto *undo = edit->addAction("Undo"); undo->setShortcut(QKeySequence::Undo);
    connect(undo, &QAction::triggered, this, [this]{ if (m_source) m_source->undo(); });
    auto *redo = edit->addAction("Redo"); redo->setShortcut(QKeySequence::Redo);
    connect(redo, &QAction::triggered, this, [this]{ if (m_source) m_source->redo(); });
    edit->addSeparator();
    auto *cut = edit->addAction("Cut"); cut->setShortcut(QKeySequence::Cut);
    connect(cut, &QAction::triggered, this, [this]{ if (m_source) m_source->cut(); });
    auto *copy = edit->addAction("Copy"); copy->setShortcut(QKeySequence::Copy);
    connect(copy, &QAction::triggered, this, [this]{ if (m_source) m_source->copy(); });
    auto *paste = edit->addAction("Paste"); paste->setShortcut(QKeySequence::Paste);
    connect(paste, &QAction::triggered, this, [this]{ if (m_source) m_source->paste(); });

    QMenu *view = mb->addMenu("Notebook");
    auto *tp = view->addAction("Toggle Preview");
    connect(tp, &QAction::triggered, this, &NotebookWorkspace::togglePreview);
    view->addSeparator();
    view->addAction("Insert [[Wiki-link]]…")->setEnabled(false);   // Phase 3
}
