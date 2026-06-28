"""Minimal HTTP server for beerfetch.

GET /api/sysinfo — static hardware overview (JSON).
GET /api/live    — live CPU load 0..1 (JSON), sampled per request.
GET /live        — ambient bar view that polls /api/live.
All other GET requests serve the sysinfo UI panel.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from .system import collect_sysinfo, read_cpu_sample
from .parse import cpu_load
from .live import render_live_page
from .ui import render_page


class _Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):  # suppress default access log noise
        pass

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, body, status=200):
        enc = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(enc)))
        self.end_headers()
        self.wfile.write(enc)

    def do_GET(self):
        if self.path == "/api/sysinfo":
            try:
                data = collect_sysinfo()
                self._json({"ok": True, "sysinfo": data})
            except Exception as exc:
                self._json({"ok": False, "error": str(exc)}, status=500)
        elif self.path == "/api/live":
            try:
                cur = read_cpu_sample()
                load = cpu_load(self.server.last_cpu, cur)
                self.server.last_cpu = cur
                self._json({"ok": True, "cpu": load})
            except Exception as exc:
                self._json({"ok": False, "error": str(exc)}, status=500)
        elif self.path == "/live":
            self._html(render_live_page())
        else:
            self._html(render_page())


class BeerFetchServer(HTTPServer):
    def __init__(self, server_address):
        super().__init__(server_address, _Handler)
        # last (total, idle) CPU sample, for the /api/live delta
        self.last_cpu = read_cpu_sample()
