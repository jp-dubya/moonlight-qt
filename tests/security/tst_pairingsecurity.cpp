#include <QtTest>
#include <QTemporaryDir>
#include "backend/nvpairingmanager.h"
#include "backend/nvcomputer.h"
extern "C" const char* LiGetLaunchUrlQueryParameters(void) { return ""; }
class PairingSecurityTest : public QObject {
    Q_OBJECT
private slots:
    void responseBounds() {
        for (int hash : {20, 32}) {
            for (int size = 0; size < hash + 16; ++size)
                QVERIFY(!NvPairingManager::validChallengeResponse(QByteArray(size, 'x'), hash));
            QVERIFY(NvPairingManager::validChallengeResponse(QByteArray(hash + 16, 'x'), hash));
        }
    }
    void malformedCertificates() {
        QTemporaryDir directory;
        QCoreApplication::setOrganizationName("LocalMoonlightSecurityTests");
        QCoreApplication::setApplicationName("Isolated");
        QSettings::setDefaultFormat(QSettings::IniFormat);
        QSettings::setPath(QSettings::IniFormat, QSettings::UserScope, directory.path());
        NvComputer computer;
        computer.activeAddress = NvAddress("127.0.0.1", 47989);
        computer.activeHttpsPort = 47984;
        computer.isNvidiaServerSoftware = false;
        NvPairingManager manager(&computer);
        for (const QByteArray bad : {QByteArray(), QByteArray("garbage"), QByteArray("-----BEGIN CERTIFICATE-----\nbroken\n-----END CERTIFICATE-----")}) {
            QVERIFY(manager.getSignatureFromPemCert(bad).isEmpty());
            QVERIFY(!manager.verifySignature("payload", "signature", bad));
        }
    }
};
QTEST_GUILESS_MAIN(PairingSecurityTest)
#include "tst_pairingsecurity.moc"
