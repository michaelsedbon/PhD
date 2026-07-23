#pragma once

#include <QMainWindow>
#include <QVector>

class Workspace;
class DnaStudioWorkspace;
class QStackedWidget;
class QActionGroup;
class QToolBar;

// Shell window: owns the global menu bar + the left activity bar, and hosts each
// workspace in a stacked widget. Switching a workspace swaps the whole UI and
// rebuilds the menu bar from that workspace + the shell's View/Help menus.
class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);

    // Forwarded to the DNA workspace so File→Open / CLI file args still work.
    void importPaths(const QStringList &paths, const QString &folder = QString());

private:
    void addWorkspace(Workspace *ws);
    void buildActivityBar();
    void switchTo(int index);
    void rebuildMenus();

    QStackedWidget *m_stack = nullptr;
    QToolBar       *m_activityBar = nullptr;
    QActionGroup   *m_activityGroup = nullptr;
    QVector<Workspace *> m_workspaces;
    DnaStudioWorkspace   *m_dna = nullptr;
    int m_current = -1;
};
