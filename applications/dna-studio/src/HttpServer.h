#pragma once

#include <QObject>
#include <QString>
#include <QHash>

class QTcpServer;
class QTcpSocket;

// A minimal in-process static file server on 127.0.0.1. Runs inside the app (no
// external process, no python) so it starts with the app and is torn down with it
// automatically — it cannot be orphaned. Gives embedded web content (the flowchart
// render.html) the real http:// origin it needs for fetch() and ES modules.
class HttpServer : public QObject {
    Q_OBJECT
public:
    explicit HttpServer(QObject *parent = nullptr);

    // Begin serving `rootDir` on an ephemeral localhost port. Returns true if listening.
    bool start(const QString &rootDir);
    bool isRunning() const;
    quint16 port() const;
    QString baseUrl() const;              // http://127.0.0.1:<port>  (no trailing slash)

private slots:
    void onNewConnection();

private:
    void respond(QTcpSocket *sock, const QByteArray &request);
    static QByteArray mimeFor(const QString &path);

    QTcpServer *m_server = nullptr;
    QString m_root;
    QHash<QTcpSocket *, QByteArray> m_buffers;   // per-connection request accumulation
};
