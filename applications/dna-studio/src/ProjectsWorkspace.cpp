#include "ProjectsWorkspace.h"
#include "HttpServer.h"
#include "LabConfig.h"

#include <QApplication>
#include <QMenuBar>
#include <QToolBar>
#include <QDockWidget>
#include <QListWidget>
#include <QComboBox>
#include <QPlainTextEdit>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QSplitter>
#include <QStatusBar>
#include <QFile>
#include <QDir>
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QDesktopServices>
#include <QUrl>
#include <QWebEngineView>
#include <QWebEngineSettings>
#include <QFontDatabase>

namespace {
QIcon ic(const QString &name) { return QIcon(QStringLiteral(":/icons/%1.svg").arg(name)); }
}

ProjectsWorkspace::ProjectsWorkspace(QWidget *parent) : Workspace(parent) {
    setWindowIcon(ic("workflow"));

    // In-process web server rooted at the repo — starts with the app, dies with it.
    m_server = new HttpServer(this);
    m_server->start(LabConfig::repoRoot());

    auto *tb = addToolBar("Projects");
    tb->setMovable(false);
    tb->setIconSize(QSize(18, 18));
    tb->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);

    tb->addWidget(new QLabel("  Project: "));
    m_projectBox = new QComboBox;
    m_projectBox->setMinimumWidth(220);
    tb->addWidget(m_projectBox);
    tb->addSeparator();
    auto *overview = tb->addAction(ic("maximize"), "Overview");
    connect(overview, &QAction::triggered, this, &ProjectsWorkspace::showOverview);
    auto *reload = tb->addAction(ic("rotate-cw"), "Reload");
    connect(reload, &QAction::triggered, this, &ProjectsWorkspace::reloadView);
    tb->addSeparator();
    auto *browser = tb->addAction(ic("upload"), "Open in Browser");
    connect(browser, &QAction::triggered, this, [this]{
        if (m_web) QDesktopServices::openUrl(m_web->url());
    });

    auto *leftDock = new QDockWidget("Blocks", this);
    leftDock->setWidget(buildNavigator());
    leftDock->setFeatures(QDockWidget::DockWidgetMovable | QDockWidget::DockWidgetClosable);
    leftDock->setMinimumWidth(230);
    addDockWidget(Qt::LeftDockWidgetArea, leftDock);

    setCentralWidget(buildViewer());

    statusBar()->showMessage(m_server->isRunning()
        ? QString("Flowchart server running at %1").arg(m_server->baseUrl())
        : QString("Could not start local server on 127.0.0.1"));

    loadProjects();
    connect(m_projectBox, qOverload<int>(&QComboBox::currentIndexChanged),
            this, &ProjectsWorkspace::onProjectChanged);
    if (!m_projects.isEmpty()) onProjectChanged(0);
}

QWidget *ProjectsWorkspace::buildNavigator() {
    auto *wrap = new QWidget;
    auto *v = new QVBoxLayout(wrap); v->setContentsMargins(0, 0, 0, 0); v->setSpacing(0);
    m_blocks = new QListWidget;
    m_blocks->setStyleSheet("QListWidget::item{padding:7px 8px;border-bottom:1px solid #2a2a2a;}");
    connect(m_blocks, &QListWidget::currentRowChanged, this, &ProjectsWorkspace::onBlockSelected);
    v->addWidget(m_blocks);
    return wrap;
}

QWidget *ProjectsWorkspace::buildViewer() {
    auto *split = new QSplitter(Qt::Horizontal, this);

    // Left: the live rendered flowchart (repo's own render.html).
    m_web = new QWebEngineView;
    m_web->settings()->setAttribute(QWebEngineSettings::LocalContentCanAccessRemoteUrls, true);
    m_web->settings()->setAttribute(QWebEngineSettings::LocalContentCanAccessFileUrls, true);
    split->addWidget(m_web);

    // Right: .mmd source editor for the selected block.
    auto *editWrap = new QWidget;
    auto *ev = new QVBoxLayout(editWrap); ev->setContentsMargins(0, 0, 0, 0); ev->setSpacing(0);
    auto *bar = new QWidget; bar->setStyleSheet("background:#252526;border-bottom:1px solid #3c3c3c;");
    auto *bh = new QHBoxLayout(bar); bh->setContentsMargins(8, 5, 8, 5);
    m_editorPath = new QLabel("Select a block to edit its source");
    m_editorPath->setStyleSheet("color:#9d9d9d;font-size:11px;");
    bh->addWidget(m_editorPath); bh->addStretch();
    auto *saveBtn = new QPushButton(ic("save"), "Save + Render");
    connect(saveBtn, &QPushButton::clicked, this, &ProjectsWorkspace::saveBlock);
    bh->addWidget(saveBtn);
    ev->addWidget(bar);

    m_editor = new QPlainTextEdit;
    QFont mono("SF Mono"); mono.setStyleHint(QFont::Monospace); mono.setPointSize(11);
    if (!QFontDatabase::families().contains("SF Mono")) mono = QFontDatabase::systemFont(QFontDatabase::FixedFont);
    m_editor->setFont(mono);
    m_editor->setStyleSheet("QPlainTextEdit{background:#1e1e1e;color:#d4d4d4;border:none;padding:8px;}");
    m_editor->setPlaceholderText("Mermaid .mmd source of the selected block appears here.");
    ev->addWidget(m_editor, 1);
    split->addWidget(editWrap);

    split->setStretchFactor(0, 3);
    split->setStretchFactor(1, 2);
    split->setSizes({860, 560});
    return split;
}

void ProjectsWorkspace::loadProjects() {
    // Discover projects that ship a FLOWCHART/ dir with a blocks.json manifest.
    m_projects.clear();
    const QString root = LabConfig::repoRoot();
    QDir projects(root + "/projects");
    for (const QString &proj : projects.entryList(QDir::Dirs | QDir::NoDotAndDotDot)) {
        const QString fcRel = QString("projects/%1/FLOWCHART").arg(proj);
        if (QFileInfo::exists(root + "/" + fcRel + "/render.html")) {
            QString nice = proj; nice.replace('_', ' ');
            m_projects.append({nice, fcRel});
            m_projectBox->addItem(nice);
        }
    }
    if (m_projects.isEmpty())
        m_projectBox->addItem("(no FLOWCHART projects found)");
}

void ProjectsWorkspace::loadBlocksFor(const Project &p) {
    m_blocks->clear();
    const QString root = LabConfig::repoRoot();
    QFile mf(root + "/" + p.flowchartDir + "/blocks.json");
    if (!mf.open(QIODevice::ReadOnly)) return;
    const QJsonArray arr = QJsonDocument::fromJson(mf.readAll()).object().value("blocks").toArray();

    auto *ov = new QListWidgetItem(ic("maximize"), "Overview (all blocks)");
    ov->setData(Qt::UserRole, QString());        // empty file = overview
    m_blocks->addItem(ov);
    for (const QJsonValue &v : arr) {
        const QJsonObject o = v.toObject();
        auto *it = new QListWidgetItem(ic("git-branch"), o.value("title").toString());
        it->setData(Qt::UserRole, o.value("file").toString());   // e.g. S1_bacterial_display.mmd
        m_blocks->addItem(it);
    }
}

void ProjectsWorkspace::loadUrl(const QString &relPathWithQuery) {
    if (!m_web || !m_server->isRunning()) return;
    m_web->load(QUrl(m_server->baseUrl() + "/" + relPathWithQuery));
}

void ProjectsWorkspace::onProjectChanged(int index) {
    if (index < 0 || index >= m_projects.size()) return;
    m_projectIndex = index;
    loadBlocksFor(m_projects[index]);
    m_blocks->setCurrentRow(0);   // Overview
}

void ProjectsWorkspace::onBlockSelected() {
    auto *it = m_blocks->currentItem();
    if (!it || m_projectIndex < 0) return;
    const Project &p = m_projects[m_projectIndex];
    const QString file = it->data(Qt::UserRole).toString();
    m_openBlockFile = file;

    if (file.isEmpty()) {                        // Overview
        loadUrl(p.flowchartDir + "/render.html");
        m_editor->clear();
        m_editorPath->setText("Overview — pick a single block to edit its source");
        m_editor->setReadOnly(true);
        return;
    }

    const QString blockName = QFileInfo(file).completeBaseName();
    loadUrl(QString("%1/render.html?block=%2").arg(p.flowchartDir, blockName));

    // Load the .mmd source into the editor.
    QFile f(LabConfig::repoRoot() + "/" + p.flowchartDir + "/blocks/" + file);
    if (f.open(QIODevice::ReadOnly)) {
        m_editor->setReadOnly(false);
        m_editor->setPlainText(QString::fromUtf8(f.readAll()));
        m_editorPath->setText(p.flowchartDir + "/blocks/" + file);
    } else {
        m_editor->setReadOnly(true);
        m_editor->setPlainText("");
        m_editorPath->setText("(could not open " + file + ")");
    }
}

void ProjectsWorkspace::showOverview() {
    if (m_blocks->count() > 0) m_blocks->setCurrentRow(0);
}

void ProjectsWorkspace::reloadView() {
    if (m_web) m_web->reload();
}

void ProjectsWorkspace::saveBlock() {
    if (m_openBlockFile.isEmpty() || m_projectIndex < 0 || m_editor->isReadOnly()) return;
    const Project &p = m_projects[m_projectIndex];
    const QString path = LabConfig::repoRoot() + "/" + p.flowchartDir + "/blocks/" + m_openBlockFile;
    QFile f(path);
    if (f.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        f.write(m_editor->toPlainText().toUtf8());
        f.close();
        statusBar()->showMessage("Saved " + m_openBlockFile + " — re-rendering…", 3000);
        reloadView();
    } else {
        statusBar()->showMessage("Could not write " + path, 4000);
    }
}

void ProjectsWorkspace::populateMenus(QMenuBar *mb) {
    QMenu *file = mb->addMenu("File");
    auto *save = file->addAction("Save Block");
    save->setShortcut(QKeySequence::Save);
    connect(save, &QAction::triggered, this, &ProjectsWorkspace::saveBlock);
    auto *reload = file->addAction("Reload");
    reload->setShortcut(QKeySequence::Refresh);
    connect(reload, &QAction::triggered, this, &ProjectsWorkspace::reloadView);
    file->addSeparator();
    auto *quit = file->addAction("Quit");
    quit->setShortcut(QKeySequence::Quit);
    connect(quit, &QAction::triggered, qApp, &QApplication::quit);

    mb->addMenu("Edit")->addAction("(placeholder)")->setEnabled(false);

    QMenu *proj = mb->addMenu("Project");
    auto *ov = proj->addAction("Overview");
    connect(ov, &QAction::triggered, this, &ProjectsWorkspace::showOverview);
    proj->addSeparator();
    proj->addAction("Link Experiment (EXP_XXX)…")->setEnabled(false);
}
