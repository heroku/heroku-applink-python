# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import ssl
import subprocess
import tempfile
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

type Handler = Callable[[BaseHTTPRequestHandler], None]


@dataclass
class TlsServer:
    url: str
    ca_file: str
    requests: list[BaseHTTPRequestHandler] = field(default_factory=list)
    handlers: list[Handler] = field(default_factory=list)

    def respond(self, *handlers: Handler) -> None:
        self.handlers = list(handlers)
        self.requests.clear()

    def client_context(self) -> ssl.SSLContext:
        return ssl.create_default_context(cafile=self.ca_file)


def respond_with(
    status: int, body: bytes | str = b"", headers: dict[str, str] | None = None
) -> Handler:
    data = body.encode() if isinstance(body, str) else body

    def handler(request: BaseHTTPRequestHandler) -> None:
        request.send_response(status)
        for name, value in (headers or {}).items():
            request.send_header(name, value)
        request.send_header("Content-Length", str(len(data)))
        request.end_headers()
        request.wfile.write(data)

    return handler


@contextmanager
def tls_server() -> Iterator[TlsServer]:
    with tempfile.TemporaryDirectory() as directory:
        key = Path(directory) / "key.pem"
        cert = Path(directory) / "cert.pem"
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "ec",
                "-pkeyopt",
                "ec_paramgen_curve:prime256v1",
                "-nodes",
                "-keyout",
                str(key),
                "-out",
                str(cert),
                "-days",
                "1",
                "-subj",
                "/CN=localhost",
                "-addext",
                "subjectAltName=DNS:localhost,IP:127.0.0.1",
            ],
            check=True,
            capture_output=True,
        )
        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(cert, key)

        state = TlsServer(url="", ca_file=str(cert))

        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                state.requests.append(self)
                if len(state.handlers) > 1:
                    state.handlers.pop(0)(self)
                elif state.handlers:
                    state.handlers[0](self)

            def log_message(self, format: str, *args: object) -> None:
                pass

        class QuietServer(ThreadingHTTPServer):
            def handle_error(self, request: object, client_address: object) -> None:
                pass

        httpd = QuietServer(("127.0.0.1", 0), RequestHandler)
        httpd.daemon_threads = True
        httpd.socket = server_context.wrap_socket(httpd.socket, server_side=True)
        state.url = f"https://localhost:{httpd.server_address[1]}"
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield state
        finally:
            httpd.shutdown()
            httpd.server_close()
