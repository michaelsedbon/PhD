#include "MainWindow.h"
#include "CircularMapView.h"
#include "SequenceIO.h"
#include "FeatureTypes.h"

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
#include <QFileDialog>
#include <QMessageBox>
#include <QShortcut>

namespace {

constexpr int kFolderRole = Qt::UserRole + 1;     // stores a library folder key on tree items

QIcon ic(const QString &name) { return QIcon(QStringLiteral(":/icons/%1.svg").arg(name)); }

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
    if (count >= 0) it->setText(1, QString::number(count));
    return it;
}

// Deterministic pseudo-random ACGT sequence (so each sample looks distinct & stable).
QString genSeq(int len, quint32 seed) {
    QString s; s.reserve(len);
    quint32 x = seed * 2654435761u + 1u;
    const char b[] = "ACGT";
    for (int i = 0; i < len; ++i) { x = x * 1664525u + 1013904223u; s += QChar(b[(x >> 24) & 3]); }
    return s;
}

Feature feat(const QString &n, const QString &type, int s, int e, int strand, double off) {
    Feature f; f.name = n; f.type = type; f.start = s; f.end = e; f.strand = strand;
    f.color = FeatureTypes::colorFor(type);
    f.directional = FeatureTypes::directionalFor(type) && strand != 0;
    f.offsetPx = off; f.thickness = 12; return f;
}

} // namespace

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("DNA Studio");
    setWindowIcon(ic("dna"));
    resize(1480, 940);

    loadSampleLibrary();           // build the library first so tree counts are accurate
    buildMenuBar();
    buildMainToolBar();

    auto *leftDock = new QDockWidget("Sources", this);
    leftDock->setWidget(buildSourceTree());
    leftDock->setFeatures(QDockWidget::DockWidgetMovable | QDockWidget::DockWidgetClosable);
    addDockWidget(Qt::LeftDockWidgetArea, leftDock);

    auto *split = new QSplitter(Qt::Vertical, this);
    split->addWidget(buildDocumentTable());
    split->addWidget(buildViewer());
    split->setStretchFactor(0, 0);
    split->setStretchFactor(1, 1);
    split->setSizes({220, 680});
    setCentralWidget(split);

    auto *rightDock = new QDockWidget("Inspector", this);
    rightDock->setWidget(buildOptionsPanel());
    rightDock->setFeatures(QDockWidget::DockWidgetMovable | QDockWidget::DockWidgetClosable);
    rightDock->setMinimumWidth(260);
    addDockWidget(Qt::RightDockWidgetArea, rightDock);

    buildStatusBar();
    buildEditMenu();               // needs m_map (built in buildViewer)

    connect(m_map, &CircularMapView::selectionChanged, this, &MainWindow::onSelectionChanged);
    connect(m_map, &CircularMapView::documentEdited,   this, &MainWindow::onDocumentEdited);

    // Open on "Plasmids from NEB" with pACYC177 selected.
    m_tree->setCurrentItem(m_tree->topLevelItem(0)->child(5));
}

// --------------------------------------------------------------- menu bar ----

void MainWindow::buildMenuBar() {
    QMenu *file = menuBar()->addMenu("File");
    QAction *open = file->addAction("Open…");
    open->setShortcut(QKeySequence::Open);
    connect(open, &QAction::triggered, this, &MainWindow::openFiles);
    file->addSeparator();
    QAction *quit = file->addAction("Quit");
    quit->setShortcut(QKeySequence::Quit);
    connect(quit, &QAction::triggered, this, &QWidget::close);

    m_editMenu = menuBar()->addMenu("Edit");   // filled by buildEditMenu() once the map exists
    for (const char *m : {"View", "Tools", "Sequence", "Annotate && Predict", "Help"})
        menuBar()->addMenu(m)->addAction("(placeholder)")->setEnabled(false);
}

void MainWindow::buildEditMenu() {
    auto *undo = m_editMenu->addAction("Undo");
    undo->setShortcut(QKeySequence::Undo);
    connect(undo, &QAction::triggered, m_map, &CircularMapView::undo);
    m_editMenu->addSeparator();

    auto *copy = m_editMenu->addAction("Copy");
    copy->setShortcut(QKeySequence::Copy);
    connect(copy, &QAction::triggered, m_map, &CircularMapView::copySelection);

    auto *paste = m_editMenu->addAction("Paste");
    paste->setShortcut(QKeySequence::Paste);
    connect(paste, &QAction::triggered, m_map, &CircularMapView::pasteClipboard);

    auto *del = m_editMenu->addAction("Delete Selection");
    del->setShortcut(QKeySequence::Delete);
    connect(del, &QAction::triggered, m_map, &CircularMapView::deleteSelection);
    m_editMenu->addSeparator();

    auto *selAll = m_editMenu->addAction("Select All");
    selAll->setShortcut(QKeySequence::SelectAll);
    connect(selAll, &QAction::triggered, m_map, &CircularMapView::selectAll);

    auto *ann = m_editMenu->addAction("Add Annotation…");
    connect(ann, &QAction::triggered, m_map, &CircularMapView::addAnnotation);
    m_editMenu->addSeparator();

    auto *find = m_editMenu->addAction("Find…");
    find->setShortcut(QKeySequence::Find);                 // Cmd/Ctrl+F
    connect(find, &QAction::triggered, this, &MainWindow::showFindBar);

    auto *findNext = m_editMenu->addAction("Find Next");
    findNext->setShortcut(QKeySequence::FindNext);          // Cmd/Ctrl+G
    connect(findNext, &QAction::triggered, m_map, &CircularMapView::nextHit);

    auto *findPrev = m_editMenu->addAction("Find Previous");
    findPrev->setShortcut(QKeySequence::FindPrevious);      // Cmd/Ctrl+Shift+G
    connect(findPrev, &QAction::triggered, m_map, &CircularMapView::prevHit);
}

void MainWindow::showFindBar() {
    m_findBar->show();
    m_findEdit->setFocus();
    m_findEdit->selectAll();
    if (!m_findEdit->text().isEmpty()) doFind();
}

void MainWindow::doFind() {
    m_map->findMatches(m_findEdit->text(), m_findMm->value(), m_findBoth->isChecked());
}

// ----------------------------------------------------------- main toolbar ----

void MainWindow::buildMainToolBar() {
    auto *tb = addToolBar("Main");
    tb->setMovable(false);
    tb->setIconSize(QSize(18, 18));

    tb->addWidget(toolButton("arrow-left",  "Back"));
    tb->addWidget(toolButton("arrow-right", "Forward"));
    tb->addSeparator();
    auto *addBtn = toolButton("plus", "Add", true);
    connect(addBtn, &QToolButton::clicked, this, &MainWindow::openFiles);
    tb->addWidget(addBtn);
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
    m_tree = new QTreeWidget;
    m_tree->setColumnCount(2);
    m_tree->setHeaderHidden(true);
    m_tree->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    m_tree->header()->setSectionResizeMode(1, QHeaderView::ResizeToContents);
    m_tree->setIndentation(14);
    m_tree->setMinimumWidth(220);

    auto *local = node("Local", "folder");
    struct Grp { const char *name; int count; };
    const char *names[] = {"Sample Documents", "Alignments", "Cloning", "Contig Assembly",
                           "Genomes", "Plasmids from NEB", "Primers", "Protein Documents",
                           "Tree Documents"};
    for (const char *nm : names) {
        auto *child = node(nm, "folder", m_library.value(nm).size());   // honest count
        child->setData(0, kFolderRole, nm);          // every Local folder is navigable
        local->addChild(child);
    }

    auto *refs = node("Reference Features", "database", 0);
    refs->addChild(node("Geneious Plasmid Features", "database", 841));

    auto *ncbi = node("NCBI", "database");
    for (auto *n : {"Gene", "Genome", "Nucleotide", "Protein", "PubMed", "Structure", "Taxonomy"})
        ncbi->addChild(node(n, "database"));

    m_tree->addTopLevelItem(local);
    m_tree->addTopLevelItem(refs);
    m_tree->addTopLevelItem(node("Deleted Items", "folder", 0));
    m_tree->addTopLevelItem(node("Cloud", "database"));
    m_tree->addTopLevelItem(node("Operations", "workflow"));
    m_tree->addTopLevelItem(ncbi);
    m_tree->addTopLevelItem(node("UniProt", "database"));
    local->setExpanded(true);
    ncbi->setExpanded(true);

    connect(m_tree, &QTreeWidget::currentItemChanged, this, &MainWindow::onFolderChanged);
    return m_tree;
}

// -------------------------------------------------------- document table -----

QWidget *MainWindow::buildDocumentTable() {
    auto *wrap = new QWidget;
    auto *v = new QVBoxLayout(wrap); v->setContentsMargins(0, 0, 0, 0); v->setSpacing(0);

    auto *bar = new QWidget; bar->setStyleSheet("background:#252526;border-bottom:1px solid #3c3c3c;");
    auto *h = new QHBoxLayout(bar); h->setContentsMargins(8, 5, 8, 5);
    h->addWidget(new QPushButton(ic("filter"), "Filter"));
    h->addStretch();
    m_selLabel = new QLabel("—"); m_selLabel->setStyleSheet("color:#9d9d9d;");
    h->addWidget(m_selLabel);
    h->addWidget(new QPushButton(ic("columns"), "Columns"));
    v->addWidget(bar);

    const QStringList cols = {"Name", "Description", "Modified", "Organism",
                              "Sequence Length", "Topology", "Molecule Type"};
    m_table = new QTableWidget(0, cols.size());
    m_table->setHorizontalHeaderLabels(cols);
    m_table->verticalHeader()->setVisible(false);
    m_table->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_table->setSelectionMode(QAbstractItemView::SingleSelection);
    m_table->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_table->setShowGrid(false);
    m_table->setAlternatingRowColors(true);
    m_table->horizontalHeader()->setSectionResizeMode(1, QHeaderView::Stretch);
    connect(m_table, &QTableWidget::itemSelectionChanged, this, &MainWindow::onDocRowChanged);
    v->addWidget(m_table);
    return wrap;
}

// -------------------------------------------------------------- viewer -------

QWidget *MainWindow::buildViewer() {
    auto *tabs = new QTabWidget;
    tabs->setDocumentMode(true);

    auto *seqTab = new QWidget;
    auto *v = new QVBoxLayout(seqTab); v->setContentsMargins(0, 0, 0, 0); v->setSpacing(0);

    auto *sub = new QToolBar;
    sub->setIconSize(QSize(15, 15));
    sub->setStyleSheet("QToolBar{background:#252526;border-bottom:1px solid #3c3c3c;}");
    auto add = [&](const QString &i, const QString &t) { return sub->addAction(ic(i), t); };
    add("upload", "Extract");
    add("rotate-cw", "R.C.");
    add("type", "Translate");
    auto *annAct = add("edit", "Add/Edit Annotation");
    connect(annAct, &QAction::triggered, [this]{ m_map->addAnnotation(); });
    m_editAction = add("lock", "Allow Editing");
    m_editAction->setCheckable(true);
    m_editAction->setToolTip("Unlock the sequence so it can be edited (protects against accidental deletion)");
    connect(m_editAction, &QAction::toggled, [this](bool on){ m_map->setEditable(on); });
    add("sparkles", "Annotate & Predict");
    add("save", "Save");
    auto *sp = new QWidget; sp->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
    sub->addWidget(sp);
    auto *zoomOutAct = sub->addAction(ic("zoom-out"), "Zoom out");
    zoomOutAct->setShortcut(QKeySequence::ZoomOut);
    m_zoomBox = new QSpinBox; m_zoomBox->setRange(1, 500); m_zoomBox->setSuffix(" %");
    m_zoomBox->setMaximumWidth(80);
    sub->addWidget(m_zoomBox);
    auto *zoomInAct = sub->addAction(ic("zoom-in"), "Zoom in");
    zoomInAct->setShortcut(QKeySequence::ZoomIn);
    auto *fitAct    = sub->addAction(ic("maximize"), "Fit");
    fitAct->setShortcut(QKeySequence("Ctrl+0"));
    v->addWidget(sub);

    // Find bar (hidden until Cmd+F)
    m_findBar = new QWidget;
    m_findBar->setStyleSheet("background:#2d2d2d;border-bottom:1px solid #3c3c3c;");
    auto *fl = new QHBoxLayout(m_findBar); fl->setContentsMargins(8, 4, 8, 4); fl->setSpacing(8);
    fl->addWidget(new QLabel("Find:"));
    m_findEdit = new QLineEdit; m_findEdit->setPlaceholderText("sequence e.g. GAATTC");
    m_findEdit->setMaximumWidth(260);
    m_findEdit->setStyleSheet("font-family:'SF Mono','Consolas',monospace;");
    fl->addWidget(m_findEdit);
    fl->addWidget(new QLabel("Max mismatches:"));
    m_findMm = new QSpinBox; m_findMm->setRange(0, 10); m_findMm->setMaximumWidth(56);
    fl->addWidget(m_findMm);
    m_findBoth = new QCheckBox("Both strands"); m_findBoth->setChecked(true);
    fl->addWidget(m_findBoth);
    auto *prevBtn = new QPushButton("‹ Prev");
    auto *nextBtn = new QPushButton("Next ›");
    fl->addWidget(prevBtn); fl->addWidget(nextBtn);
    m_findCount = new QLabel("—"); m_findCount->setStyleSheet("color:#9d9d9d;");
    fl->addWidget(m_findCount);
    fl->addStretch();
    auto *closeBtn = new QPushButton("✕"); closeBtn->setMaximumWidth(28);
    fl->addWidget(closeBtn);
    m_findBar->hide();
    v->addWidget(m_findBar);

    m_map = new CircularMapView;
    v->addWidget(m_map, 1);

    connect(m_zoomBox, qOverload<int>(&QSpinBox::valueChanged), m_map, &CircularMapView::setZoomPercent);
    connect(m_map, &CircularMapView::zoomChanged, this, &MainWindow::onZoomChanged);
    connect(m_map, &CircularMapView::hovered, this, &MainWindow::onHover);
    connect(zoomOutAct, &QAction::triggered, m_map, &CircularMapView::zoomOut);
    connect(zoomInAct,  &QAction::triggered, m_map, &CircularMapView::zoomIn);
    connect(fitAct,     &QAction::triggered, m_map, &CircularMapView::fitToView);

    // Find wiring
    connect(m_findEdit, &QLineEdit::textChanged, this, &MainWindow::doFind);
    connect(m_findMm,   qOverload<int>(&QSpinBox::valueChanged), this, &MainWindow::doFind);
    connect(m_findBoth, &QCheckBox::toggled, this, &MainWindow::doFind);
    connect(m_findEdit, &QLineEdit::returnPressed, m_map, &CircularMapView::nextHit);
    connect(nextBtn, &QPushButton::clicked, m_map, &CircularMapView::nextHit);
    connect(prevBtn, &QPushButton::clicked, m_map, &CircularMapView::prevHit);
    connect(closeBtn, &QPushButton::clicked, this, [this]{ m_findBar->hide(); m_map->clearFind(); m_map->setFocus(); });
    auto *escFind = new QShortcut(QKeySequence(Qt::Key_Escape), m_findBar);
    connect(escFind, &QShortcut::activated, this, [this]{ m_findBar->hide(); m_map->clearFind(); m_map->setFocus(); });
    connect(m_map, &CircularMapView::findResults, this, [this](int count, int current){
        if (m_findEdit->text().isEmpty()) m_findCount->setText("—");
        else if (count == 0) m_findCount->setText("no matches");
        else m_findCount->setText(QString("%1 of %2").arg(current).arg(count));
    });

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
    m_linearCheck = addToggle("Linear View", false);
    addToggle("Wrap", false);
    auto *names   = addToggle("Show Name", true);
    addToggle("Show Description", false);

    connect(annot,  &QCheckBox::toggled, this, [this](bool on){ m_map->setShowAnnotations(on); });
    connect(transl, &QCheckBox::toggled, this, [this](bool on){ m_map->setShowTranslation(on); });
    connect(m_linearCheck, &QCheckBox::toggled, this, [this](bool on){ m_map->setLinearView(on); });
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
    m_memLabel = new QLabel("Ready");
    m_selStatus = new QLabel("");
    m_hoverLabel = new QLabel("Hover the plasmid to inspect bases");
    statusBar()->addWidget(m_memLabel);
    statusBar()->addPermanentWidget(m_selStatus);
    statusBar()->addPermanentWidget(m_hoverLabel);
}

// ------------------------------------------------------------- library -------

void MainWindow::loadSampleLibrary() {
    auto mk = [](const QString &name, const QString &desc, int len, bool circ,
                 quint32 seed, QVector<Feature> feats) {
        SequenceDocument d;
        d.name = name; d.description = desc; d.sequence = genSeq(len, seed);
        d.circular = circ; d.organism = "synthetic construct";
        d.modified = "06 Dec 2012 12:12 AM"; d.features = feats;
        return d;
    };

    m_library["Plasmids from NEB"] = {
        mk("pACYC177", "Cloning vector pACYC177, complete sequence", 3941, true, 11, {
            feat("bla signal peptide", "sig_peptide", 3760, 3840,  1,  16),
            feat("bla CDS",            "CDS",         3840,  560,  1, -14),
            feat("bla gene",           "gene",        3800,  600,  1, -28),
            feat("rep origin",         "rep_origin",   800, 1300,  1, -14),
            feat("aph(3')-Ia CDS",     "CDS",         2000, 2750, -1, -14),
            feat("aph(3')-Ia gene",    "gene",        1980, 2780, -1, -28)}),
        mk("pBR322", "Cloning vector pBR322, complete sequence", 4361, true, 22, {
            feat("bla (AmpR)",  "CDS",        86,  946, -1, -14),
            feat("tetA (TetR)", "CDS",       1525, 2715, 1, -14),
            feat("ori",         "rep_origin", 2935, 3535, 1, -14)}),
        mk("pUC19", "Cloning vector pUC19, complete sequence", 2686, true, 33, {
            feat("lacZα", "CDS",          146,  469, 1, -14),
            feat("MCS",   "misc_feature", 396,  455, 1,  16),
            feat("AmpR",  "CDS",         1000, 1860, -1, -14),
            feat("ori",   "rep_origin",  2100, 2700, 1, -14)}),
        mk("pET11c", "Expression vector pET11c, complete sequence", 5672, true, 44, {
            feat("T7 promoter", "promoter",   200,  260, 1,  16),
            feat("bla (AmpR)",  "CDS",       1000, 1860, -1, -14),
            feat("lacI",        "CDS",       3000, 4080, -1, -14),
            feat("ori",         "rep_origin", 4500, 5100, 1, -14)}),
    };
    m_library["Sample Documents"] = {
        mk("EGFP", "Enhanced green fluorescent protein CDS", 720, false, 55, {
            feat("EGFP CDS", "CDS", 1, 720, 1, -14)}),
        mk("Insert fragment", "Synthetic insert with ORF and promoter", 1500, false, 66, {
            feat("promoter", "promoter", 1,   90, 1, -14),
            feat("ORF",      "CDS",      100, 900, 1, -14)}),
    };
    m_library["Primers"] = {
        mk("M13 fwd", "M13 forward sequencing primer", 17, false, 77, {}),
        mk("T7 promoter primer", "T7 promoter primer", 20, false, 88, {}),
    };
}

void MainWindow::populateTable(const QString &folder) {
    const auto &docs = m_library.value(folder);
    QSignalBlocker block(m_table);
    m_table->setRowCount(docs.size());
    for (int r = 0; r < docs.size(); ++r) {
        const SequenceDocument &d = docs[r];
        m_table->setItem(r, 0, new QTableWidgetItem(d.name));
        m_table->setItem(r, 1, new QTableWidgetItem(d.description));
        m_table->setItem(r, 2, new QTableWidgetItem(d.modified));
        m_table->setItem(r, 3, new QTableWidgetItem(d.organism));
        m_table->setItem(r, 4, new QTableWidgetItem(QString::number(d.length())));
        m_table->setItem(r, 5, new QTableWidgetItem(d.topology()));
        m_table->setItem(r, 6, new QTableWidgetItem(d.moleculeType));
    }
    m_selLabel->setText(QString("%1 document%2").arg(docs.size()).arg(docs.size() == 1 ? "" : "s"));
}

void MainWindow::showDocument(const SequenceDocument &doc) {
    m_map->setDocument(doc);
    if (m_linearCheck) { QSignalBlocker b(m_linearCheck); m_linearCheck->setChecked(!doc.circular); }
    if (m_editAction)  { QSignalBlocker b(m_editAction); m_editAction->setChecked(false); }
    m_map->setEditable(false);     // every document re-locks on open
    m_memLabel->setText(QString("%1 — %L2 bp (%3)")
                            .arg(doc.name).arg(doc.length()).arg(doc.topology()));
    m_selStatus->clear();
    QSignalBlocker zb(m_zoomBox); m_zoomBox->setValue(m_map->zoomPercent());
}

// ----------------------------------------------------------------- slots -----

void MainWindow::onFolderChanged() {
    QTreeWidgetItem *it = m_tree->currentItem();
    if (!it) return;
    const QString folder = it->data(0, kFolderRole).toString();
    if (folder.isEmpty()) return;          // non-folder node (NCBI, UniProt, …) — ignore
    m_currentFolder = folder;
    populateTable(folder);                 // updates table even for empty folders
    if (m_table->rowCount() > 0) {
        m_table->selectRow(0);             // triggers onDocRowChanged → loads the document
    } else {
        m_table->clearSelection();
        m_map->setSequence(QString());     // empty viewer
        m_memLabel->setText(QString("%1 — empty").arg(folder));
        m_selStatus->clear();
        m_hoverLabel->setText("");
    }
}

void MainWindow::onDocRowChanged() {
    int row = m_table->currentRow();
    const auto &docs = m_library.value(m_currentFolder);
    if (row < 0 || row >= docs.size()) return;
    m_selLabel->setText(QString("1 of %1 selected").arg(docs.size()));
    showDocument(docs[row]);
}

void MainWindow::onSelectionChanged(int lo, int hi, int length) {
    if (length <= 0) { m_selStatus->clear(); return; }
    m_selStatus->setText(QString("Selection: %L1–%L2  (%L3 bp)").arg(lo).arg(hi).arg(length));
}

void MainWindow::onDocumentEdited() {
    int row = m_table->currentRow();
    auto &docs = m_library[m_currentFolder];
    if (row < 0 || row >= docs.size()) return;
    docs[row].sequence = m_map->sequence();      // persist edits back into the library
    docs[row].features = m_map->features();
    if (auto *cell = m_table->item(row, 4)) cell->setText(QString::number(docs[row].length()));
    m_memLabel->setText(QString("%1 — %L2 bp (%3)")
                            .arg(docs[row].name).arg(docs[row].length()).arg(docs[row].topology()));
}

void MainWindow::openFiles() {
    const QStringList paths = QFileDialog::getOpenFileNames(
        this, "Open sequence files", QString(), SequenceIO::fileFilter());
    importPaths(paths);
}

void MainWindow::importPaths(const QStringList &paths, const QString &folderArg) {
    if (paths.isEmpty()) return;
    const QString folder = !folderArg.isEmpty() ? folderArg
                         : !m_currentFolder.isEmpty() ? m_currentFolder
                         : QStringLiteral("Sample Documents");

    int loaded = 0; QStringList failed;
    for (const QString &p : paths) {
        bool ok = false;
        SequenceDocument doc = SequenceIO::load(p, &ok);
        if (ok) { m_library[folder].append(doc); ++loaded; }
        else failed << QFileInfo(p).fileName();
    }

    if (loaded) {
        m_currentFolder = folder;
        populateTable(folder);
        m_table->selectRow(m_library[folder].size() - 1);   // show the last import
    }
    if (!failed.isEmpty())
        QMessageBox::warning(this, "Import",
            "Could not read:\n" + failed.join('\n') +
            "\n\nSupported: FASTA (.fa/.fasta) and GenBank (.gb/.gbk).");
}

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
