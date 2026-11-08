#!/usr/bin/env python3
"""Loopback-only HTTP smoke service; it returns a fixed synthetic label, not a model."""
from __future__ import annotations

import argparse
import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

MAX_BODY_BYTES = 1024


class SyntheticReleaseServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], release_id: str):
        if not ipaddress.ip_address(address[0]).is_loopback:
            raise ValueError("the demonstration server may bind only to a loopback address")
        if not release_id or len(release_id) > 80:
            raise ValueError("release_id must contain 1 to 80 characters")
        self.release_id = release_id
        super().__init__(address, SyntheticReleaseHandler)


class SyntheticReleaseHandler(BaseHTTPRequestHandler):
    server: SyntheticReleaseServer
    protocol_version = "HTTP/1.1"

    def _send_json(self, status: int, value: dict[str, Any]) -> None:
        body = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path == "/healthz":
            self._send_json(200, {"ok": True, "release_id": self.server.release_id, "synthetic": True})
        elif self.path == "/version":
            self._send_json(200, {"release_id": self.server.release_id, "model_execution": False, "synthetic": True})
        else:
            self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path != "/predict":
            self._send_json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid_content_length"})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(413, {"error": "body_size_not_allowed"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "application_json_required"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        if (
            not isinstance(payload, dict)
            or set(payload) != {"sample_id"}
            or not isinstance(payload.get("sample_id"), str)
            or not payload["sample_id"].startswith("synthetic-")
        ):
            self._send_json(400, {"error": "synthetic_sample_id_required"})
            return
        self._send_json(200, {
            "release_id": self.server.release_id,
            "sample_id": payload["sample_id"],
            "prediction": "synthetic-label-a",
            "model_execution": False,
            "synthetic": True,
        })

    def log_message(self, _format: str, *_args: Any) -> None:
        # Do not log request bodies, sample identifiers, or header values.
        return


def create_server(host: str = "127.0.0.1", port: int = 8765, release_id: str = "demo-r1") -> SyntheticReleaseServer:
    return SyntheticReleaseServer((host, port), release_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="must be a loopback address")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--release-id", default="demo-r1")
    args = parser.parse_args()
    try:
        server = create_server(args.host, args.port, args.release_id)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Synthetic local smoke service on http://{args.host}:{server.server_port}; no model or cloud is used.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
