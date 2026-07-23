#pragma once

#include "Workspace.h"
#include <QVector>

class QListWidget;
class QComboBox;
class QPlainTextEdit;
class QLabel;
class QMenuBar;
class QWebEngineView;
class HttpServer;

// Projects workspace: live view + editing of the existing Mermaid subsystem maps.
// Embeds the repo's own render.html (full-fidelity custom renderer) in a web view,
// with a block navigator and a .mmd source editor that re-renders on save.
class ProjectsWorkspace : public Workspace {
    Q_OBJECT
public:
    explicit ProjectsWorkspace(QWidget *parent = nullptr);

    QString wsTitle() const override { return "Projects"; }
    QString wsIconName() const override { return "workflow"; }
    void populateMenus(QMenuBar *mb) override;

private slots:
    void onProjectChanged(int index);
    void onBlockSelected();
    void showOverview();
    void reloadView();
    void saveBlock();

private:
    struct Project { QString name; QString flowchartDir; };   // dir relative to repo root
    struct Block   { QString file;  QString title; };

    QWidget *buildNavigator();
    QWidget *buildViewer();
    void loadProjects();
    void loadBlocksFor(const Project &p);
    void loadUrl(const QString &relPathWithQuery);

    QComboBox      *m_projectBox = nullptr;
    QListWidget    *m_blocks = nullptr;
    QWebEngineView *m_web = nullptr;
    QPlainTextEdit *m_editor = nullptr;
    QLabel         *m_editorPath = nullptr;

    HttpServer *m_server = nullptr;
    QVector<Project> m_projects;
    int m_projectIndex = -1;
    QString m_openBlockFile;   // .mmd currently loaded in the editor (empty = overview)
};
