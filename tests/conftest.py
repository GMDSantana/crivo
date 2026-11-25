"""

╔██████╗██████╗ ██╗██╗     ██╗╔██████╗
██╔════╝██╔══██╗██║╚██╗   ██╔╝██╔═══██╗
██║     ██████╔╝██║ ╚██╗ ██╔╝ ██║   ██║
██║     ██╔██═╝ ██║  ╚████╔╝  ██║   ██╝
╚██████╗██║ ██╗ ██║   ╚██╔╝   ╚██████╝
© Guilherme Santana
https://gmdsantana.com
https://github.com/GMDSantana/crivo

"""

# Shared fixtures, including a small local HTTP server so the web scraper can
# be tested end to end without touching the internet.

import collections
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

PAGE_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Café</title></head>
<body>
<a href="/about">About</a>
<a href='https://external.example.org/x?a=1&amp;b=2'>External</a>
<img src=img/logo.png>
<form action="/login"></form>
<a href="#top">Top</a>
<a href="javascript:void(0)">JS</a>
<a href="mailto:security@example.com">Mail</a>
<p>Servers: 10.20.30.40 and 2001:db8::42, docs at https://docs.example.com/guide.</p>
<p>Café ☕ api.example.com</p>
</body></html>
"""

_flaky_counts = collections.Counter()
_hits = collections.Counter()  # requests per path, for crawl tests

# A small website for crawl tests. Each page contains a marker IP in
# 127.1.0.0/16 so tests can tell which pages were fetched. "{other}" is the
# same server reached as "localhost", i.e. a different site.
SITE_PAGES = {
    "/site/": (
        "root 127.1.0.1 root.example.com "
        '<a href="/site/a">a</a> <a href="b">b</a> '
        '<a href="{other}/site/offsite">offsite</a> '
        '<img src="/site/image.png"> <a href="/site/missing">missing</a> '
        '<a href="/site/redirect-in">in</a> <a href="/site/redirect-out">out</a> '
        '<a href="/site/binary">binary</a> <a href="/site/a#again">a again</a> '
        '<a href="mailto:x@example.com">mail</a>'
    ),
    "/site/a": 'page a 127.1.0.2 a.example.com <a href="/site/a2">a2</a> <a href="/site/">home</a>',
    "/site/a2": 'page a2 127.1.0.3 <a href="/site/a3">a3</a>',
    "/site/a3": "page a3 127.1.0.4",
    "/site/b": 'page b 127.1.0.5 b.example.com <a href="/site/a">a</a>',
    "/site/c": "page c 127.1.0.6",
    "/site/offsite": "offsite 127.1.0.99",
    "/site/secret": "secret 127.1.0.98",
}
SITE_REDIRECTS = {
    "/site/redirect-in": "/site/c",
    "/site/redirect-out": "{other}/site/secret",
    "/site/loop": "/site/loop",
}


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep test output quiet
        pass

    def _send(self, status, body, content_type="text/html", headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parts = urlsplit(self.path)
        query = parse_qs(parts.query)
        path = parts.path
        _hits[path] += 1
        other = f"http://localhost:{self.server.server_address[1]}"

        if path in SITE_PAGES:
            self._send(200, SITE_PAGES[path].format(other=other).encode("utf-8"))
        elif path in SITE_REDIRECTS:
            self.send_response(302)
            self.send_header("Location", SITE_REDIRECTS[path].format(other=other))
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif path == "/site/binary":
            self._send(200, b"binary 127.1.0.97", "application/octet-stream")
        elif path == "/site/image.png":
            self._send(200, b"\x89PNG 127.1.0.96", "image/png")
        elif path == "/page":
            self._send(200, PAGE_HTML.encode("utf-8"))
        elif path == "/latin1":
            self._send(200, "Olá 192.0.2.7 süd.example.com".encode("latin-1"), "text/plain; charset=ISO-8859-1")
        elif path == "/nocharset":
            self._send(200, "Olá 192.0.2.8 açaí.example.com nocharset.example.com".encode("utf-8"), "text/plain")
        elif path == "/json":
            self._send(200, b'{"next": "https:\\/\\/api.example.com\\/v2\\/items"}', "application/json")
        elif path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/page")
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif path == "/notfound":
            self._send(404, b"not found", "text/plain")
        elif path == "/flaky":
            key = query.get("key", ["default"])[0]
            fail_times = int(query.get("fail", ["1"])[0])
            _flaky_counts[key] += 1
            if _flaky_counts[key] <= fail_times:
                self._send(503, b"busy", "text/plain")
            else:
                self._send(200, b"recovered 198.51.100.9", "text/plain")
        elif path == "/slow":
            time.sleep(float(query.get("delay", ["2"])[0]))
            self._send(200, b"too late 203.0.113.1", "text/plain")
        elif path == "/big":
            size = int(query.get("size", ["200000"])[0])
            self._send(200, b"203.0.113.5 " + b"a" * size, "text/plain")
        else:
            self._send(404, b"unknown", "text/plain")


@pytest.fixture(scope="session")
def http_server():
    """Starts a local HTTP server and yields its base URL, e.g. http://127.0.0.1:12345."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    yield f"http://{host}:{port}"
    server.shutdown()
    server.server_close()


@pytest.fixture
def http_hits():
    """Counter of requests per path received by the local HTTP server."""
    return _hits


@pytest.fixture(autouse=True)
def _no_proxy_for_localhost(monkeypatch):
    # Make sure requests never sends local test traffic through an HTTP proxy.
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
