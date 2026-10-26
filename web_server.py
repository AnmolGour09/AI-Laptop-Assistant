"""Serve the Jarvis frontend and issue short-lived LiveKit room tokens."""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants


ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("jarvis.web")


class JarvisRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self'; img-src 'self' data:; connect-src 'self' https: wss:; "
            "media-src 'self' blob:; object-src 'none'; base-uri 'none'; "
            "frame-ancestors 'none'",
        )
        super().end_headers()

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._send_json(200, {"status": "ok"})
            return
        if self.path.startswith("/api/"):
            self._send_json(404, {"error": "API route not found"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/token":
            self._send_json(404, {"error": "API route not found"})
            return
        if not self._is_same_origin_request():
            self._send_json(403, {"error": "Requests must come from this local Jarvis page"})
            return

        content_length = self.headers.get("Content-Length", "0")
        try:
            if int(content_length) > 1024:
                self._send_json(413, {"error": "Request body is too large"})
                return
        except ValueError:
            self._send_json(400, {"error": "Invalid request"})
            return

        livekit_url = os.getenv("LIVEKIT_URL", "").strip()
        api_key = os.getenv("LIVEKIT_API_KEY", "").strip()
        api_secret = os.getenv("LIVEKIT_API_SECRET", "").strip()
        if not livekit_url or not api_key or not api_secret:
            self._send_json(
                503,
                {"error": "Set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET in .env"},
            )
            return
        if not livekit_url.startswith(("wss://", "ws://")):
            self._send_json(503, {"error": "LIVEKIT_URL must use ws:// or wss://"})
            return

        room_name = f"jarvis-{uuid.uuid4().hex}"
        identity = f"user-{uuid.uuid4().hex[:12]}"
        try:
            token = (
                AccessToken(api_key, api_secret)
                .with_identity(identity)
                .with_ttl(timedelta(minutes=15))
                .with_grants(
                    VideoGrants(
                        room_join=True,
                        room=room_name,
                        can_publish=True,
                        can_subscribe=True,
                        can_publish_data=True,
                    )
                )
                .to_jwt()
            )
        except Exception:
            logger.exception("Unable to issue a LiveKit room token")
            self._send_json(503, {"error": "Unable to issue a LiveKit token; check the server configuration"})
            return

        self._send_json(200, {"url": livekit_url, "token": token, "room": room_name})

    def _is_same_origin_request(self) -> bool:
        origin = self.headers.get("Origin")
        host = self.headers.get("Host", "").lower()
        if not origin or not host:
            return False
        parsed = urlsplit(origin)
        return (
            parsed.scheme == "http"
            and parsed.hostname in {"localhost", "127.0.0.1"}
            and parsed.netloc.lower() == host
            and not parsed.path
            and not parsed.query
            and not parsed.fragment
        )

    def _send_json(self, status: int, payload: dict[str, str]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        logger.info("%s - %s", self.address_string(), format % args)


def main() -> None:
    port = int(os.getenv("JARVIS_WEB_PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), JarvisRequestHandler)
    logger.info("Jarvis frontend: http://127.0.0.1:%s", port)
    logger.info("Use run.bat to start the frontend and agent worker together")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping Jarvis frontend server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
