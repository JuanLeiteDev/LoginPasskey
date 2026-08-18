"""Servidor estático e proxy local sem dependências externas."""

from __future__ import annotations

import http.client
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


FRONTEND_DIR = Path(__file__).resolve().parent
BACKEND_URL = os.getenv("PASSKEY_BACKEND_URL", "http://127.0.0.1:8001")
LISTEN_HOST = os.getenv("PASSKEY_FRONTEND_HOST", "localhost")
LISTEN_PORT = int(os.getenv("PASSKEY_FRONTEND_PORT", "8000"))
HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/api/"):
            self._proxy_request()
            return
        super().do_GET()

    def do_HEAD(self):  # noqa: N802
        if self.path.startswith("/api/"):
            self._proxy_request()
            return
        super().do_HEAD()

    def do_POST(self):  # noqa: N802
        self._proxy_request()

    def do_OPTIONS(self):  # noqa: N802
        self._proxy_request()

    def _proxy_request(self):
        if not self.path.startswith("/api/"):
            self.send_error(404)
            return

        target = urlsplit(BACKEND_URL)
        connection_class = (
            http.client.HTTPSConnection if target.scheme == "https" else http.client.HTTPConnection
        )
        connection = connection_class(target.hostname, target.port, timeout=30)
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length else None
        upstream_path = self.path.removeprefix("/api")
        headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() not in HOP_BY_HOP_HEADERS | {"host", "content-length"}
        }
        if body is not None:
            headers["Content-Length"] = str(len(body))

        try:
            connection.request(self.command, upstream_path, body=body, headers=headers)
            response = connection.getresponse()
            response_body = response.read()
            self.send_response(response.status, response.reason)
            for key, value in response.getheaders():
                if key.lower() not in HOP_BY_HOP_HEADERS | {"content-length"}:
                    self.send_header(key, value)
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(response_body)
        except (OSError, http.client.HTTPException) as error:
            self.send_error(502, f"Backend indisponível: {error}")
        finally:
            connection.close()


if __name__ == "__main__":
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), FrontendHandler)
    print(f"Frontend: http://{LISTEN_HOST}:{LISTEN_PORT}")
    print(f"API proxy: {BACKEND_URL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()
