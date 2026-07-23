#pragma once

#include "Workspace.h"

class QTreeView;
class QFileSystemModel;
class QPlainTextEdit;
class QTextEdit;
class QLabel;
class QMenuBar;
class QModelIndex;

// Lab Notebook workspace: an Obsidian-style markdown editor over the PhD repo.
// Browses the real .md files (experiments/, projects/, …), edits them in place,
// and shows a live rendered preview. No separate data store — the repo is the vault.
class NotebookWorkspace : public Workspace {
    Q_OBJECT
public:
    explicit NotebookWorkspace(QWidget *parent = nullptr);

    QString wsTitle() const override { return "Lab Notebook"; }
    QString wsIconName() const override { return "edit"; }
    void populateMenus(QMenuBar *mb) override;

private slots:
    void onFileClicked(const QModelIndex &index);
    void onSourceChanged();
    void saveFile();
    void togglePreview();

private:
    QWidget *buildTree();
    QWidget *buildEditor();
    void openFile(const QString &path);
    void renderPreview();

    QTreeView        *m_tree = nullptr;
    QFileSystemModel *m_fsModel = nullptr;
    QPlainTextEdit   *m_source = nullptr;
    QTextEdit        *m_preview = nullptr;
    QLabel           *m_pathLabel = nullptr;
    QLabel           *m_dirtyLabel = nullptr;

    QString m_openPath;
    bool m_dirty = false;
};
