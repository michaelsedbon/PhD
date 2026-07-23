#include "MainWindow.h"
#include "Workspace.h"
#include "DnaStudioWorkspace.h"
#include "NotebookWorkspace.h"
#include "ProjectsWorkspace.h"

#include <QStackedWidget>
#include <QToolBar>
#include <QMenuBar>
#include <QActionGroup>
#include <QAction>

namespace {
QIcon ic(const QString &name) { return QIcon(QStringLiteral(":/icons/%1.svg").arg(name)); }
}

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("DNA Studio");
    setWindowIcon(ic("dna"));
    resize(1480, 940);

    m_stack = new QStackedWidget;
    setCentralWidget(m_stack);

    buildActivityBar();

    // Register workspaces (order defines ⌘1 / ⌘2 / ⌘3).
    m_dna = new DnaStudioWorkspace;
    addWorkspace(m_dna);
    addWorkspace(new NotebookWorkspace);
    addWorkspace(new ProjectsWorkspace);

    switchTo(0);
}

void MainWindow::buildActivityBar() {
    // Slim VS Code-style vertical bar on the far left; icon-only, exclusive toggles.
    m_activityBar = new QToolBar("Workspaces");
    m_activityBar->setObjectName("activityBar");
    m_activityBar->setMovable(false);
    m_activityBar->setFloatable(false);
    m_activityBar->setIconSize(QSize(24, 24));
    m_activityBar->setToolButtonStyle(Qt::ToolButtonIconOnly);
    m_activityBar->setStyleSheet(
        "QToolBar#activityBar{background:#2d2d2d;border-right:1px solid #1a1a1a;spacing:4px;padding:6px 4px;}"
        "QToolBar#activityBar QToolButton{padding:8px;border-radius:6px;}"
        "QToolBar#activityBar QToolButton:checked{background:#094771;}"
        "QToolBar#activityBar QToolButton:hover{background:#3a3a3a;}");
    addToolBar(Qt::LeftToolBarArea, m_activityBar);

    m_activityGroup = new QActionGroup(this);
    m_activityGroup->setExclusive(true);
    // Per-workspace actions are added as each workspace registers (see addWorkspace).
}

void MainWindow::addWorkspace(Workspace *ws) {
    const int index = m_workspaces.size();
    m_workspaces.append(ws);
    m_stack->addWidget(ws);

    auto *act = new QAction(ic(ws->wsIconName()), ws->wsTitle(), this);
    act->setCheckable(true);
    act->setToolTip(QString("%1  (⌘%2)").arg(ws->wsTitle()).arg(index + 1));
    connect(act, &QAction::triggered, this, [this, index]{ switchTo(index); });
    m_activityGroup->addAction(act);
    m_activityBar->addAction(act);
}

void MainWindow::switchTo(int index) {
    if (index < 0 || index >= m_workspaces.size() || index == m_current) return;
    m_current = index;
    m_stack->setCurrentIndex(index);
    if (auto *a = m_activityGroup->actions().value(index)) a->setChecked(true);
    setWindowTitle(QString("%1 — Lab Suite").arg(m_workspaces[index]->wsTitle()));
    rebuildMenus();
}

void MainWindow::rebuildMenus() {
    menuBar()->clear();
    Workspace *ws = m_workspaces.value(m_current);
    if (ws) ws->populateMenus(menuBar());

    // Shell-owned View menu: workspace switcher + standard view items.
    QMenu *view = menuBar()->addMenu("View");
    for (int i = 0; i < m_workspaces.size(); ++i) {
        Workspace *w = m_workspaces[i];
        auto *a = view->addAction(ic(w->wsIconName()), w->wsTitle());
        a->setShortcut(QKeySequence(QString("Ctrl+%1").arg(i + 1)));
        a->setCheckable(true);
        a->setChecked(i == m_current);
        connect(a, &QAction::triggered, this, [this, i]{ switchTo(i); });
    }
    view->addSeparator();
    auto *full = view->addAction("Enter Full Screen");
    full->setShortcut(QKeySequence(Qt::CTRL | Qt::META | Qt::Key_F));
    connect(full, &QAction::triggered, this, [this]{
        setWindowState(windowState() ^ Qt::WindowFullScreen);
    });

    QMenu *help = menuBar()->addMenu("Help");
    help->addAction("DNA Studio Lab Suite")->setEnabled(false);
}

void MainWindow::importPaths(const QStringList &paths, const QString &folder) {
    if (m_dna) {
        switchTo(0);
        m_dna->importPaths(paths, folder);
    }
}
