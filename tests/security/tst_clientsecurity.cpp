#include <QtTest>
#include <QTemporaryDir>
#include <QFile>
#include "../../app/backend/hostcache.h"
#include "../../app/backend/requestlogging.h"
class Security : public QObject {
    Q_OBJECT
private slots:
    void containment() {
        QTemporaryDir temp;
        QVERIFY(temp.isValid());
        QDir root(temp.path());
        QVERIFY(root.mkdir("cache"));
        QVERIFY(root.mkdir("outside"));
        const auto cache = root.filePath("cache");
        QFile sentinel(root.filePath("outside/keep.txt"));
        QVERIFY(sentinel.open(QIODevice::WriteOnly)); sentinel.write("keep"); sentinel.close();
        const QString id = "11111111-2222-4333-8444-555555555555";
        const QStringList invalid = {"", ".", "..", "../outside", root.filePath("outside"), "not-a-uuid", "00000000-0000-0000-0000-000000000000"};
        for (const auto& value : invalid) {
            QVERIFY(HostCache::key(value).isEmpty());
            QVERIFY(HostCache::directory(cache, value, true).isEmpty());
            QVERIFY(HostCache::directory(cache, value, false).isEmpty());
        }
        const auto leaf = QDir(cache).filePath(id);
        QVERIFY(QFile::link(root.filePath("outside"), leaf));
        QVERIFY(HostCache::directory(cache, id, true).isEmpty());
        QVERIFY(HostCache::directory(cache, id, false).isEmpty());
        QVERIFY(QFile::remove(leaf)); // only the temporary symlink
        QCOMPARE(HostCache::directory(cache, id, true), QFileInfo(leaf).canonicalFilePath());
        QCOMPARE(HostCache::key("{" + id.toUpper() + "}"), id);
        QVERIFY(QDir(HostCache::directory(cache, id, false)).removeRecursively());
        QVERIFY(sentinel.exists());
    }
    void logRedaction() {
        const QUrl url("https://localhost/launch?appid=1&rikey=secret1&clientpairingsecret=secret2&token=secret3&salt=secret4&otpauth=secret5");
        const auto safe = RequestLogging::redacted(url);
        for (int i = 1; i <= 5; ++i) QVERIFY(!safe.contains("secret" + QString::number(i)));
        QVERIFY(safe.contains("appid=1"));
        QVERIFY(url.query().contains("secret1"));
    }
    void exclusiveLogs() {
        QTemporaryDir temp;
        QFile target(temp.filePath("target"));
        QVERIFY(target.open(QIODevice::WriteOnly)); target.write("keep"); target.close();
        const auto link = temp.filePath("log");
        QVERIFY(QFile::link(target.fileName(), link));
        QFile log(link);
        QVERIFY(!log.open(QIODevice::WriteOnly | QIODevice::NewOnly, QFileDevice::ReadOwner | QFileDevice::WriteOwner));
        QVERIFY(target.open(QIODevice::ReadOnly)); QCOMPARE(target.readAll(), QByteArray("keep"));
        QFile fresh(temp.filePath("fresh"));
        QVERIFY(fresh.open(QIODevice::WriteOnly | QIODevice::NewOnly, QFileDevice::ReadOwner | QFileDevice::WriteOwner));
        QVERIFY(!(fresh.permissions() & (QFileDevice::ReadGroup | QFileDevice::ReadOther | QFileDevice::WriteGroup | QFileDevice::WriteOther)));
    }
};
QTEST_GUILESS_MAIN(Security)
#include "tst_clientsecurity.moc"
