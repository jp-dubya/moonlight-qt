#pragma once
#include <QDir>
#include <QFileInfo>
#include <QRegularExpression>
#include <QUuid>

namespace HostCache {
inline QString key(const QString& id) {
    static const QRegularExpression format(QStringLiteral("\\A(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\})\\z"));
    const QUuid uuid(id);
    return format.match(id).hasMatch() && !uuid.isNull() ? uuid.toString(QUuid::WithoutBraces) : QString();
}
inline QString directory(const QString& root, const QString& id, bool create) {
    const auto leaf = key(id);
    const auto base = QFileInfo(root).canonicalFilePath();
    if (leaf.isEmpty() || base.isEmpty()) return {};
    const auto path = QDir(base).filePath(leaf);
    if (QFileInfo(path).isSymLink()) return {};
    if (!QFileInfo::exists(path) && (!create || !QDir(base).mkdir(leaf))) return {};
    const auto canonical = QFileInfo(path).canonicalFilePath();
    if (!QFileInfo(path).isDir() || canonical != path) return {};
    return path;
}
}
