#pragma once

#include <QString>
#include <QFileInfo>
#include <QDir>

// Central place for app-wide paths. For now the vault/repo root is the PhD repo;
// later this comes from the open .labproj file (see docs/ARCHITECTURE.md).
namespace LabConfig {

inline QString repoRoot() {
    // Default to the PhD repo. Overridable later via .labproj / "Open Vault".
    const QString def = QStringLiteral("/Users/michaelsedbon/Documents/PhD");
    return QFileInfo::exists(def) ? def : QDir::homePath();
}

} // namespace LabConfig
