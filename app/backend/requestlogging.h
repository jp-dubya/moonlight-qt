#pragma once
#include <QUrl>
#include <QUrlQuery>
namespace RequestLogging {
inline QString redacted(const QUrl& url) {
    QUrl safe(url);
    QUrlQuery query(safe);
    for (const auto& item : query.queryItems()) {
        const auto name = item.first.toLower();
        if (name.contains("key") || name.contains("secret") || name.contains("challenge") ||
            name.contains("token") || name.contains("cert") || name.contains("salt") || name.contains("auth")) {
            query.removeAllQueryItems(item.first);
            query.addQueryItem(item.first, "REDACTED");
        }
    }
    safe.setQuery(query);
    return safe.toString();
}
}
