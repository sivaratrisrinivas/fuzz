"""Vercel serverless Reconstructing entry (same-origin /reconstruct rewrite).

Thin helper only: accepts final_fuzz + fresh_clues, rejects original Memory,
one Smart Robot call, ephemeral forget. Hugging Face when HF_TOKEN is set.

Hobby / free-tier (honest):
- Function duration is ~10s on Hobby. A Hugging Face Smart Robot call often needs
  longer; failures return empty markers (never sample-reconstruction-01).
- Body is capped at 64 KiB. Invalid or oversized Content-Length is HTTP 400
  before sanitize_fight_end.
- Rate limit is in-memory per instance (default 12/min when VERCEL is set).
  It is not a global quota and resets on cold start.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Mapping, Optional

ROOT = Path(__file__).resolve().parent.parent
HELPER_SRC = ROOT / "helper" / "src"
if str(HELPER_SRC) not in sys.path:
    sys.path.insert(0, str(HELPER_SRC))

from thin_helper.contract import ContractError, sanitize_fight_end  # noqa: E402
from thin_helper import http_guard  # noqa: E402
from thin_helper.reconstruct_coordinator import ReconstructCoordinator  # noqa: E402

_coordinator = ReconstructCoordinator()

_FORGET_NOTE = "Original Memory never entered the helper. All data has been ephemerally forgotten."


class handler(BaseHTTPRequestHandler):
    def _send(
        self,
        status: int,
        payload: dict,
        request_id: str,
        extra_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Request-Id", request_id)
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, code: str, message: str, request_id: str, extra_headers=None) -> None:
        self._send(
            status,
            {
                "error": message,
                "code": code,
                "request_id": request_id,
                "note": _FORGET_NOTE,
            },
            request_id,
            extra_headers=extra_headers,
        )

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        request_id = self.headers.get("x-request-id") or http_guard.new_request_id()
        payload = {}
        contract = {}
        try:
            try:
                length = http_guard.parse_content_length(self.headers.get("Content-Length"))
            except ContractError as exc:
                # Do not read an invalid or oversized body.
                self._error(400, exc.code, exc.message, request_id)
                return

            fallback = "unknown"
            if getattr(self, "client_address", None):
                fallback = self.client_address[0]
            ip = http_guard.client_ip_from_headers(self.headers, fallback=fallback)
            retry_after = http_guard.check_rate_limit(ip)
            if retry_after is not None:
                self._error(
                    429,
                    "rate_limited",
                    "Too many Reconstructing requests. Try again shortly.",
                    request_id,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return

            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._error(400, "invalid_json", "Body must be JSON.", request_id)
                return

            contract = sanitize_fight_end(payload)
            result = _coordinator.reconstruct_from_fight_end(contract)
            result["request_id"] = request_id
            self._send(200, result, request_id)
        except ContractError as exc:
            self._error(400, exc.code, exc.message, request_id)
        except Exception:
            self._error(
                500,
                "reconstruct_failed",
                "Reconstructing encountered an issue. The Smart Robot may be slow or unavailable.",
                request_id,
            )
        finally:
            payload = {}
            contract = {}

    def log_message(self, format: str, *args) -> None:
        # Sizes and path only. Never Fuzz text.
        sys.stderr.write("reconstruct vercel %s\n" % (args[0] if args else format))
