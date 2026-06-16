#include "MainWindow.h"

#include <QApplication>
#include <QFile>
#include <QFontDatabase>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    app.setApplicationName("DNA Studio");
    app.setOrganizationName("SYNTHETICA Lab");

    // Apply the SYNTHETICA dark theme (VS Code palette).
    QFile qss(":/theme.qss");
    if (qss.open(QFile::ReadOnly | QFile::Text))
        app.setStyleSheet(QString::fromUtf8(qss.readAll()));

    // Prefer Inter if installed; otherwise fall back to the system UI font.
    if (QFontDatabase::families().contains("Inter")) {
        QFont f("Inter", 10);
        app.setFont(f);
    }

    MainWindow w;
    w.show();

    // Allow opening files passed on the command line (also enables "Open With").
    QStringList files = app.arguments().mid(1);
    if (!files.isEmpty()) w.importPaths(files);

    return app.exec();
}
