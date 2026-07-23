#include "HttpServer.h"

#include <QTcpServer>
#include <QTcpSocket>
#include <QHostAddress>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QMimeDatabase>
#include <QMimeType>
#include <QUrl>

HttpServer::HttpServer(QObject *parent) : QObject(parent) {}

bool HttpServer::start(const QString &rootDir) {
    m_root = QDir(rootDir).absolutePath();
    if (!m_server) {
        m_server = new QTcpServer(this);
        connect(m_server, &QTcpServer::newConnection, this, &HttpServer::onNewConnection);
    }
    if (m_server->isListening()) return true;
    return m_server->listen(QHostAddress::LocalHost, 0);   // ephemeral port
}

bool HttpServer::isRunning() const { return m_server && m_server->isListening(); }
quint16 HttpServer::port() const { return m_server ? m_server->serverPort() : 0; }
QString HttpServer::baseUrl() const { return QStringLiteral("http://127.0.0.1:%1").arg(port()); }

void HttpServer::onNewConnection() {
    while (m_server->hasPendingConnections()) {
        QTcpSocket *sock = m_server->nextPendingConnection();
        m_buffers.insert(sock, QByteArray());
        connect(sock, &QTcpSocket::readyRead, this, [this, sock]{
            QByteArray &buf = m_buffers[sock];
            buf += sock->readAll();
            // A GET/HEAD request ends at the blank line; we don't consume request bodies.
            if (buf.contains("\r\n\r\n")) {
                const QByteArray req = buf;
                m_buffers.remove(sock);
                respond(sock, req);
            }
        });
        connect(sock, &QTcpSocket::disconnected, this, [this, sock]{
            m_buffers.remove(sock);
            sock->deleteLater();
        });
    }
}

QByteArray HttpServer::mimeFor(const QString &path) {
    if (path.endsWith(".js")  || path.endsWith(".mjs")) return "text/javascript; charset=utf-8";
    if (path.endsWith(".mmd")) return "text/plain; charset=utf-8";
    if (path.endsWith(".html")) return "text/html; charset=utf-8";
    if (path.endsWith(".css"))  return "text/css; charset=utf-8";
    if (path.endsWith(".json")) return "application/json; charset=utf-8";
    if (path.endsWith(".svg"))  return "image/svg+xml";
    QMimeType mt = QMimeDatabase().mimeTypeForFile(path);
    return mt.isValid() ? mt.name().toUtf8() : QByteArray("application/octet-stream");
}

void HttpServer::respond(QTcpSocket *sock, const QByteArray &request) {
    auto send = [&](int code, const QByteArray &status, const QByteArray &mime,
                    const QByteArray &body, bool headOnly) {
        QByteArray hdr = "HTTP/1.1 " + QByteArray::number(code) + " " + status + "\r\n";
        hdr += "Content-Type: " + mime + "\r\n";
        hdr += "Content-Length: " + QByteArray::number(body.size()) + "\r\n";
        hdr += "Access-Control-Allow-Origin: *\r\n";
        hdr += "Cache-Control: no-store\r\n";
        hdr += "Connection: close\r\n\r\n";
        sock->write(hdr);
        if (!headOnly) sock->write(body);
        sock->flush();
        sock->disconnectFromHost();
    };

    // Parse the request line: METHOD /path?query HTTP/1.1
    const int eol = request.indexOf("\r\n");
    const QByteArray line = eol >= 0 ? request.left(eol) : request;
    const QList<QByteArray> parts = line.split(' ');
    if (parts.size() < 2 || (parts[0] != "GET" && parts[0] != "HEAD")) {
        send(405, "Method Not Allowed", "text/plain", "405", false);
        return;
    }
    const bool headOnly = parts[0] == "HEAD";

    QByteArray target = parts[1];
    const int q = target.indexOf('?');
    if (q >= 0) target = target.left(q);                       // drop query string
    QString rel = QUrl::fromPercentEncoding(target);
    while (rel.startsWith('/')) rel.remove(0, 1);
    if (rel.isEmpty()) rel = "index.html";

    // Resolve within the root; reject anything escaping it.
    const QString full = QDir(m_root).absoluteFilePath(rel);
    const QString canonical = QFileInfo(full).canonicalFilePath();
    if (canonical.isEmpty() || !(canonical == m_root || canonical.startsWith(m_root + "/"))) {
        send(404, "Not Found", "text/plain", "404 Not Found", headOnly);
        return;
    }
    QFile f(canonical);
    if (QFileInfo(canonical).isDir() || !f.open(QIODevice::ReadOnly)) {
        send(404, "Not Found", "text/plain", "404 Not Found", headOnly);
        return;
    }
    send(200, "OK", mimeFor(canonical), f.readAll(), headOnly);
}
