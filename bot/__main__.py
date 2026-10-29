#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the Telegram bot alongside Render's HTTP health endpoint."""
import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .bot import Bot


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health", "/healthz"):
            body = b"OK\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = b"Not Found\n"
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, name="health-http", daemon=True).start()
    print(f"Health server listening on 0.0.0.0:{port}", flush=True)
    return server


if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    health_server = start_health_server()
    app = Bot()
    try:
        app.run()
    finally:
        health_server.shutdown()
        health_server.server_close()
