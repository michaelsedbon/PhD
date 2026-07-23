#pragma once

#include <QMainWindow>

class QMenuBar;

// A Workspace is a self-contained "mini application" hosted inside the shell.
// It is a QMainWindow used as a *child* widget (Qt::Widget flag) so it keeps its
// own toolbars, dock areas and status bar — making each workspace feel like a
// separate piece of software. The shell owns the global menu bar and asks the
// active workspace to populate it on every switch.
class Workspace : public QMainWindow {
    Q_OBJECT
public:
    explicit Workspace(QWidget *parent = nullptr) : QMainWindow(parent) {
        setWindowFlags(Qt::Widget);   // render as an embedded child, not a top-level window
    }

    virtual QString wsTitle() const = 0;       // e.g. "DNA Studio" — shown in the title & activity bar
    virtual QString wsIconName() const = 0;    // resource icon key, e.g. "dna" → :/icons/dna.svg

    // Add this workspace's menus (File, Edit, module-specific…) to the shell's menu bar.
    // Called fresh on every activation; the shell clears the bar beforehand.
    virtual void populateMenus(QMenuBar *mb) = 0;
};
