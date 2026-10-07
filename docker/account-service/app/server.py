import os
from http.server import BaseHTTPRequestHandler, HTTPServer

APP_NAME = os.getenv("APP_NAME", "account-service")
APP_VERSION = os.getenv("APP_VERSION", "v1")
PORT = int(os.getenv("PORT", "8080"))


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        if self.path == "/version":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(
                f"{APP_NAME}:{APP_VERSION}\n".encode()
            )
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(
            f"{APP_NAME} {APP_VERSION}\n".encode()
        )

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Starting {APP_NAME} {APP_VERSION} on port {PORT}")

server.serve_forever()
