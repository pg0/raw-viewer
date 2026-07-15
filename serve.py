#!/usr/bin/env python3
"""Local dev server for the RAW viewer.

LibRaw-Wasm is a pthreads build (shared WebAssembly memory), so the page must be
*cross-origin isolated* for SharedArrayBuffer to be available. That requires two
response headers a plain `python -m http.server` does not send:

    Cross-Origin-Opener-Policy:   same-origin
    Cross-Origin-Embedder-Policy: require-corp

This server adds them and serves .wasm / .js with the correct MIME types.
Run it (or serve.cmd), then open http://localhost:8791/ .
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8791


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".wasm": "application/wasm",
    }

    def end_headers(self):
        # Cross-origin isolation so SharedArrayBuffer (pthreads) works.
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        # No caching during development.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler))
    print("RAW viewer serving at http://localhost:%d/  (Ctrl+C to stop)" % PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
