#pragma once

#include <QMainWindow>

class CircularMapView;
class QLabel;
class QSpinBox;

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);

private slots:
    void onHover(int base, QChar nt, int residue, const QString &aa);
    void onZoomChanged(int percent);

private:
    void buildMenuBar();
    void buildMainToolBar();
    QWidget *buildSourceTree();
    QWidget *buildDocumentTable();
    QWidget *buildViewer();
    QWidget *buildOptionsPanel();
    void buildStatusBar();
    void loadMockPlasmid();

    CircularMapView *m_map = nullptr;
    QSpinBox *m_zoomBox = nullptr;
    QLabel   *m_memLabel = nullptr;
    QLabel   *m_hoverLabel = nullptr;
};
