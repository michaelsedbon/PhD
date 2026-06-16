#include "MainWindow.h"
#include "CircularMapView.h"

#include <QMenuBar>
#include <QToolBar>
#include <QToolButton>
#include <QStatusBar>
#include <QDockWidget>
#include <QTreeWidget>
#include <QTableWidget>
#include <QHeaderView>
#include <QTabWidget>
#include <QSplitter>
#include <QGroupBox>
#include <QCheckBox>
#include <QComboBox>
#include <QSpinBox>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QWidgetAction>

namespace {

QIcon ic(const QString &name) { return QIcon(QStringLiteral(":/icons/%1.svg").arg(name)); }

// A toolbar button with icon above text, optional dropdown caret — Geneious style.
QToolButton *toolButton(const QString &icon, const QString &text, bool menu = false) {
    auto *b = new QToolButton;
    b->setIcon(ic(icon));
    b->setText(text);
    b->setIconSize(QSize(18, 18));
    b->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    if (menu) b->setPopupMode(QToolButton::MenuButtonPopup);
    b->setAutoRaise(true);
    return b;
}

QTreeWidgetItem *node(const QString &text, const QString &icon, int count = -1) {
    auto *it = new QTreeWidgetItem;
    it->setText(0, text);
    if (!icon.isEmpty()) it->setIcon(0, ic(icon));
    if (count >= 0) { it->setText(1, QString::number(count)); }
    return it;
}

} // namespace

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("DNA Studio");
    setWindowIcon(ic("dna"));
    resize(1480, 940);

    buildMenuBar();
    buildMainToolBar();

    // Left dock — source tree
    auto *leftDock = new QDockWidget("Sources", this);
    leftDock->setWidget(buildSourceTree());
    leftDock->setFeatures(QDockWidget::DockWidgetMovable | QDockWidget::DockWidgetClosable);
    addDockWidget(Qt::LeftDockWidgetArea, leftDock);

    // Center — document table over viewer (resizable split)
    auto *split = new QSplitter(Qt::Vertical, this);
    split->addWidget(buildDocumentTable());
    split->addWidget(buildViewer());
    split->setStretchFactor(0, 0);
    split->setStretchFactor(1, 1);
    split->setSizes({220, 680});
    setCentralWidget(split);

    // Right dock — options inspector
    auto *rightDock = new QDockWidget("Inspector", this);
    rightDock->setWidget(buildOptionsPanel());
    rightDock->setFeatures(QDockWidget::DockWidgetMovable | QDockWidget::DockWidgetClosable);
    rightDock->setMinimumWidth(260);
    addDockWidget(Qt::RightDockWidgetArea, rightDock);

    buildStatusBar();
    loadMockPlasmid();
}

// --------------------------------------------------------------- menu bar ----

void MainWindow::buildMenuBar() {
    const char *menus[] = {"File", "Edit", "View", "Tools",
                           "Sequence", "Annotate && Predict", "Help"};
    for (const char *m : menus) {
        QMenu *menu = menuBar()->addMenu(m);
        menu->addAction("(placeholder)")->setEnabled(false);
    }
}

// ----------------------------------------------------------- main toolbar ----

void MainWindow::buildMainToolBar() {
    auto *tb = addToolBar("Main");
    tb->setMovable(false);
    tb->setIconSize(QSize(18, 18));

    tb->addWidget(toolButton("arrow-left",  "Back"));
    tb->addWidget(toolButton("arrow-right", "Forward"));
    tb->addSeparator();
    tb->addWidget(toolButton("plus",       "Add",            true));
    tb->addWidget(toolButton("upload",     "Export",         true));
    tb->addWidget(toolButton("search",     "BLAST"));
    tb->addWidget(toolButton("workflow",   "Workflows",      true));
    tb->addWidget(toolButton("align",      "Align/Assemble", true));
    tb->addWidget(toolButton("git-branch", "Tree"));
    tb->addWidget(toolButton("dna",        "Primers"));
    tb->addWidget(toolButton("scissors",   "Cloning"));

    auto *spacer = new QWidget; spacer->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
    tb->addWidget(spacer);

    auto *searchBox = new QLineEdit; searchBox->setPlaceholderText("Search Everywhere");
    searchBox->setMaximumWidth(260); searchBox->addAction(ic("search"), QLineEdit::LeadingPosition);
    tb->addWidget(searchBox);
    tb->addWidget(toolButton("help-circle", "Help", true));
}

// ----------------------------------------------------------- source tree -----

QWidget *MainWindow::buildSourceTree() {
    auto *tree = new QTreeWidget;
    tree->setColumnCount(2);
    tree->setHeaderHidden(true);
    tree->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    tree->header()->setSectionResizeMode(1, QHeaderView::ResizeToContents);
    tree->setIndentation(14);
    tree->setMinimumWidth(220);

    auto *local = node("Local", "folder");
    struct Grp { const char *name; int count; };
    const Grp groups[] = {
        {"Sample Documents", 0}, {"Alignments", 8}, {"Cloning", 12},
        {"Contig Assembly", 7}, {"Genomes", 234}, {"Plasmids from NEB", 27},
        {"Primers", 12}, {"Protein Documents", 6}, {"Tree Documents", 4}};
    for (const auto &gp : groups)
        local->addChild(node(gp.name, "folder", gp.count));

    auto *refs = node("Reference Features", "database", 0);
    refs->addChild(node("Geneious Plasmid Features", "database", 841));

    auto *ncbi = node("NCBI", "database");
    for (auto *n : {"Gene", "Genome", "Nucleotide", "Protein", "PubMed", "Structure", "Taxonomy"})
        ncbi->addChild(node(n, "database"));

    tree->addTopLevelItem(local);
    tree->addTopLevelItem(refs);
    tree->addTopLevelItem(node("Deleted Items", "folder", 0));
    tree->addTopLevelItem(node("Cloud", "database"));
    tree->addTopLevelItem(node("Operations", "workflow"));
    tree->addTopLevelItem(ncbi);
    tree->addTopLevelItem(node("UniProt", "database"));
    local->setExpanded(true);
    ncbi->setExpanded(true);

    // Select "Plasmids from NEB" to mirror the reference screenshot
    tree->setCurrentItem(local->child(5));
    return tree;
}

// -------------------------------------------------------- document table -----

QWidget *MainWindow::buildDocumentTable() {
    auto *wrap = new QWidget;
    auto *v = new QVBoxLayout(wrap); v->setContentsMargins(0, 0, 0, 0); v->setSpacing(0);

    // Filter / header strip
    auto *bar = new QWidget; bar->setStyleSheet("background:#252526;border-bottom:1px solid #3c3c3c;");
    auto *h = new QHBoxLayout(bar); h->setContentsMargins(8, 5, 8, 5);
    auto *filterBtn = new QPushButton(ic("filter"), "Filter");
    h->addWidget(filterBtn); h->addStretch();
    auto *sel = new QLabel("1 of 27 selected"); sel->setStyleSheet("color:#9d9d9d;");
    h->addWidget(sel);
    h->addWidget(new QPushButton(ic("columns"), "Columns"));
    v->addWidget(bar);

    const QStringList cols = {"", "Name", "Description", "Modified", "Organism",
                              "Sequence Length", "Topology", "Molecule Type", "Taxonomy"};
    struct Row { const char *name, *desc; int len; };
    const QVector<Row> rows = {
        {"LITMUS 28i",  "Cloning vector LITMUS28i, complete sequence", 2823},
        {"LITMUS 38i",  "Cloning vector LITMUS38i, complete sequence", 2814},
        {"pACYC177",    "Cloning vector pACYC177, complete sequence",  3941},
        {"pACYC184",    "Cloning vector pACYC184, complete sequence",  4245},
        {"pBeloBAC11",  "Cloning vector pBeloBAC11, complete sequence",7507},
        {"pBR322",      "Cloning vector pBR322, complete sequence",    4361},
        {"pET11c",      "Cloning vector pET11c, complete sequence",    5672},
        {"pGPS1.1",     "Transposon donor vector pGPS1.1, complete sequence", 4814},
        {"pGPS2.1",     "Transposon donor vector pGPS2.1, complete sequence", 4490},
    };
    auto *t = new QTableWidget(rows.size(), cols.size());
    t->setHorizontalHeaderLabels(cols);
    t->verticalHeader()->setVisible(false);
    t->setSelectionBehavior(QAbstractItemView::SelectRows);
    t->setEditTriggers(QAbstractItemView::NoEditTriggers);
    t->setShowGrid(false);
    t->setAlternatingRowColors(true);
    t->horizontalHeader()->setSectionResizeMode(2, QHeaderView::Stretch);
    t->setColumnWidth(0, 28);

    for (int r = 0; r < rows.size(); ++r) {
        auto *chk = new QTableWidgetItem();
        chk->setCheckState(rows[r].name == QString("pACYC177") ? Qt::Checked : Qt::Unchecked);
        t->setItem(r, 0, chk);
        t->setItem(r, 1, new QTableWidgetItem(rows[r].name));
        t->setItem(r, 2, new QTableWidgetItem(rows[r].desc));
        t->setItem(r, 3, new QTableWidgetItem("06 Dec 2012 12:12 AM"));
        t->setItem(r, 4, new QTableWidgetItem("Cloning vector"));
        t->setItem(r, 5, new QTableWidgetItem(QString::number(rows[r].len)));
        t->setItem(r, 6, new QTableWidgetItem("circular"));
        t->setItem(r, 7, new QTableWidgetItem("DNA"));
        t->setItem(r, 8, new QTableWidgetItem("other sequences"));
    }
    t->selectRow(2);
    v->addWidget(t);
    return wrap;
}

// -------------------------------------------------------------- viewer -------

QWidget *MainWindow::buildViewer() {
    auto *tabs = new QTabWidget;
    tabs->setDocumentMode(true);

    auto *seqTab = new QWidget;
    auto *v = new QVBoxLayout(seqTab); v->setContentsMargins(0, 0, 0, 0); v->setSpacing(0);

    // Viewer sub-toolbar
    auto *sub = new QToolBar;
    sub->setIconSize(QSize(15, 15));
    sub->setStyleSheet("QToolBar{background:#252526;border-bottom:1px solid #3c3c3c;}");
    auto add = [&](const QString &i, const QString &t) {
        auto *a = sub->addAction(ic(i), t); return a; };
    add("upload", "Extract");
    add("rotate-cw", "R.C.");
    add("type", "Translate");
    add("edit", "Add/Edit Annotation");
    add("lock", "Allow Editing");
    add("sparkles", "Annotate & Predict");
    add("save", "Save");
    auto *sp = new QWidget; sp->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
    sub->addWidget(sp);
    auto *zoomOutAct = sub->addAction(ic("zoom-out"), "Zoom out");
    m_zoomBox = new QSpinBox; m_zoomBox->setRange(1, 500); m_zoomBox->setSuffix(" %");
    m_zoomBox->setMaximumWidth(80);
    sub->addWidget(m_zoomBox);
    auto *zoomInAct = sub->addAction(ic("zoom-in"), "Zoom in");
    auto *fitAct    = sub->addAction(ic("maximize"), "Fit");
    v->addWidget(sub);

    m_map = new CircularMapView;
    v->addWidget(m_map, 1);

    // wire zoom controls
    connect(m_zoomBox, qOverload<int>(&QSpinBox::valueChanged), m_map, &CircularMapView::setZoomPercent);
    connect(m_map, &CircularMapView::zoomChanged, this, &MainWindow::onZoomChanged);
    connect(m_map, &CircularMapView::hovered, this, &MainWindow::onHover);
    connect(zoomOutAct, &QAction::triggered, m_map, &CircularMapView::zoomOut);
    connect(zoomInAct,  &QAction::triggered, m_map, &CircularMapView::zoomIn);
    connect(fitAct,     &QAction::triggered, m_map, &CircularMapView::fitToView);

    tabs->addTab(seqTab, "Sequence View");
    tabs->addTab(new QWidget, "Annotations");
    tabs->addTab(new QWidget, "Text View");
    tabs->addTab(new QWidget, "Lineage");
    tabs->addTab(new QWidget, "Info");
    return tabs;
}

// --------------------------------------------------------- options panel -----

QWidget *MainWindow::buildOptionsPanel() {
    auto *panel = new QWidget;
    auto *v = new QVBoxLayout(panel); v->setContentsMargins(10, 10, 10, 10); v->setSpacing(8);

    auto *grp = new QGroupBox("General");
    auto *gv = new QVBoxLayout(grp); gv->setSpacing(4);

    auto *colorRow = new QHBoxLayout;
    colorRow->addWidget(new QLabel("Colors:"));
    auto *colors = new QComboBox; colors->addItem("A C G T"); colorRow->addWidget(colors, 1);
    gv->addLayout(colorRow);

    auto addToggle = [&](const QString &label, bool checked) {
        auto *c = new QCheckBox(label); c->setChecked(checked); gv->addWidget(c); return c; };
    addToggle("Graphs", true);
    auto *annot   = addToggle("Annotations", true);
    addToggle("Complement", false);
    auto *transl  = addToggle("Translation", false);
    addToggle("Restriction Sites", false);
    addToggle("Circular Overview", false);
    auto *linear  = addToggle("Linear View", false);
    addToggle("Wrap", false);
    auto *names   = addToggle("Show Name", true);
    addToggle("Show Description", false);

    connect(annot,  &QCheckBox::toggled, this, [this](bool on){ m_map->setShowAnnotations(on); });
    connect(transl, &QCheckBox::toggled, this, [this](bool on){ m_map->setShowTranslation(on); });
    connect(linear, &QCheckBox::toggled, this, [this](bool on){ m_map->setLinearView(on); });
    connect(names,  &QCheckBox::toggled, this, [this](bool on){ m_map->setShowNames(on); });

    v->addWidget(grp);

    auto *hint = new QLabel(
        "Scroll: rotate plasmid\nOption + Scroll: zoom\nHover: base / residue readout");
    hint->setStyleSheet("color:#6e6e6e;font-size:11px;");
    v->addWidget(hint);
    v->addStretch();
    return panel;
}

// -------------------------------------------------------------- status bar ---

void MainWindow::buildStatusBar() {
    m_memLabel = new QLabel("3,941 / 47,152 MB Memory");
    m_hoverLabel = new QLabel("Mouse over the plasmid to inspect bases");
    statusBar()->addWidget(m_memLabel);
    statusBar()->addPermanentWidget(m_hoverLabel);
}

// ------------------------------------------------------------- mock data -----

void MainWindow::loadMockPlasmid() {
    const int N = 3941;
    QString seq; seq.reserve(N);
    quint32 s = 0x9e3779b9;                    // deterministic pseudo-random sequence
    const char bases[] = "ACGT";
    for (int i = 0; i < N; ++i) {
        s = s * 1664525u + 1013904223u;
        seq += QChar(bases[(s >> 24) & 3]);
    }
    m_map->setSequence(seq);
    m_map->setTitle("pACYC177");

    QVector<Feature> feats = {
        {"bla signal peptide", 3760, 3840,  1, QColor("#d16ad1"),  16, 12},
        {"bla CDS",            3840,  560,  1, QColor("#f2e23a"), -14, 12},
        {"bla gene",           3800,  600,  1, QColor("#3fa54a"), -28, 12},
        {"rep origin",          800, 1300,  1, QColor("#4f9fe0"), -14, 12},
        {"aph(3')-Ia CDS",     2000, 2750, -1, QColor("#f2e23a"), -14, 12},
        {"aph(3')-Ia gene",    1980, 2780, -1, QColor("#3fa54a"), -28, 12},
    };
    m_map->setFeatures(feats);
    m_map->fitToView();
    QSignalBlocker block(m_zoomBox);
    m_zoomBox->setValue(m_map->zoomPercent());
}

// ----------------------------------------------------------------- slots -----

void MainWindow::onHover(int base, QChar nt, int residue, const QString &aa) {
    QString s = QString("Mouse over base %L1 (%2)").arg(base).arg(nt);
    if (residue > 0) s += QString(", residue %1 (%2)").arg(residue).arg(aa);
    m_hoverLabel->setText(s);
}

void MainWindow::onZoomChanged(int percent) {
    if (m_zoomBox->value() != percent) {
        QSignalBlocker block(m_zoomBox);
        m_zoomBox->setValue(percent);
    }
}
