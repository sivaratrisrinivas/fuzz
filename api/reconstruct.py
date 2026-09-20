"""Vercel serverless Reconstructing entry (same-origin /reconstruct rewrite).

Thin helper only: accepts final_fuzz + fresh_clues, rejects original Memory,
one Smart Robot call, ephemeral forget. Hugging Face when HF_TOKEN is set.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER_SRC = ROOT / "helper" / "src"
if str(HELPER_SRC) not in sys.path:
    sys.path.insert(0, str(HELPER_SRC))

from thin_helper.contract import ContractError, sanitize_fight_end  # noqa: E402
from thin_helper.http_guard import new_request_id  # noqa: E402
from thin_helper.reconstruct_coordinator import ReconstructCoordinator  # noqa: E402

_coordinator = ReconstructCoordinator()


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict, request_id: str) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Request-Id", request_id)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        request_id = self.headers.get("x-request-id") or new_request_id()
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(
                400,
                {
                    "error": "Body must be JSON.",
                    "code": "invalid_json",
                    "request_id": request_id,
                    "note": "Original Memory never entered the helper. All data has been ephemerally forgotten.",
                },
                request_id,
            )
            return
        try:
            contract = sanitize_fight_end(payload)
            result = _coordinator.reconstruct_from_fight_end(contract)
            result["request_id"] = request_id
            self._send(200, result, request_id)
        except ContractError as exc:
            self._send(
                400,
                {
                    "error": exc.message,
                    "code": exc.code,
                    "request_id": request_id,
                    "note": "Original Memory never entered the helper. All data has been ephemerally forgotten.",
                },
                request_id,
            )
        except Exception:
            self._send(
                500,
                {
                    "error": "Reconstructing encountered an issue. The Smart Robot may be slow or unavailable.",
                    "code": "reconstruct_failed",
                    "request_id": request_id,
                    "note": "Original Memory never entered the helper. All data has been ephemerally forgotten.",
                },
                request_id,
            )
        finally:
            payload = {}
            contract = {}

    def log_message(self, format: str, *args) -> None:
        # Sizes and path only. Never Fuzz text.
        sys.stderr.write("reconstruct vercel %s\n" % (args[0] if args else format))
