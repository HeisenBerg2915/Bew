#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Create an event loop for compatibility
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()


def main():
    start_health_server()

    from .bot import Bot

    app = Bot()
    app.run()


if __name__ == "__main__":
    main()
