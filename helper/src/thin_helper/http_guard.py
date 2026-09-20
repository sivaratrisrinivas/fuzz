"""Rate limits, request ids, body-size guards, and structured errors for the thin helper.

Logs request metadata only (sizes, counts, duration). Never logs Fuzz text,
Fresh Clues words, prompts, or Reconstructed Memory.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections import deque
from typing import Any, Mapping, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from .contract import ContractError

# Match box/nginx.conf client_max_body_size 64k.
MAX_BODY_BYTES = 64 * 1024
MAX_TRACKED_IPS = 4096

_lock = threading.Lock()
_hits: dict[str, deque[float]] = {}


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]


def _header(headers: Mapping[str, Any], name: str) -> str:
    if hasattr(headers, "get"):
        value = headers.get(name)
        if value:
            return str(value).strip()
        # BaseHTTPRequestHandler headers are case-insensitive; Mapping may not be.
        lower = name.lower()
        for key in getattr(headers, "keys", lambda: [])():
            if str(key).lower() == lower:
                got = headers.get(key)
                if got:
                    return str(got).strip()
    return ""


def client_ip_from_headers(headers: Mapping[str, Any], fallback: str = "unknown") -> str:
    """Rate-limit key from headers. Rightmost X-Forwarded-For hop is the trusted proxy peer.

    nginx overwrites X-Forwarded-For with $remote_addr (not the client-supplied chain).
    Vercel appends the connecting IP; the rightmost hop is that peer, not a spoofed leftmost value.
    """
    real_ip = _header(headers, "x-real-ip") or _header(headers, "x-vercel-forwarded-for")
    if real_ip:
        return real_ip.split(",")[-1].strip() or fallback
    forwarded = _header(headers, "x-forwarded-for")
    if forwarded:
        hops = [h.strip() for h in forwarded.split(",") if h.strip()]
        if hops:
            return hops[-1]
    return fallback


def client_ip(request: Request) -> str:
    fallback = "unknown"
    if request.client and request.client.host:
        fallback = request.client.host
    return client_ip_from_headers(request.headers, fallback=fallback)


def parse_content_length(raw: Optional[str], *, max_bytes: int = MAX_BODY_BYTES) -> int:
    """Return body length to read, or raise ContractError for invalid/oversized Content-Length."""
    if raw is None or str(raw).strip() == "":
        raise ContractError("invalid_content_length", "Content-Length is required.")
    try:
        length = int(str(raw).strip())
    except (TypeError, ValueError) as exc:
        raise ContractError("invalid_content_length", "Content-Length must be an integer.") from exc
    if length < 0:
        raise ContractError("invalid_content_length", "Content-Length is invalid.")
    if length > max_bytes:
        raise ContractError(
            "payload_too_large",
            f"Request body exceeds {max_bytes} bytes.",
        )
    return length


def rate_limit_per_minute() -> int:
    default = "12" if os.environ.get("VERCEL") else "30"
    try:
        return max(1, int(os.environ.get("FUZZ_RATE_LIMIT_PER_MINUTE", default)))
    except ValueError:
        return int(default)


def _evict_oldest_locked() -> None:
    if not _hits:
        return
    oldest_ip = min(_hits.items(), key=lambda kv: kv[1][-1] if kv[1] else 0)[0]
    _hits.pop(oldest_ip, None)


def _drop_empty_locked() -> None:
    empty = [ip for ip, q in _hits.items() if not q]
    for ip in empty:
        _hits.pop(ip, None)
    while len(_hits) > MAX_TRACKED_IPS:
        _evict_oldest_locked()


def check_rate_limit(ip: str) -> Optional[int]:
    """Return retry-after seconds when limited, else None."""
    window = 60.0
    limit = rate_limit_per_minute()
    now = time.monotonic()
    with _lock:
        q = _hits.get(ip)
        if q is None:
            if len(_hits) >= MAX_TRACKED_IPS:
                _evict_oldest_locked()
            _hits[ip] = deque([now])
            return None
        while q and now - q[0] >= window:
            q.popleft()
        if not q:
            _hits.pop(ip, None)
            _drop_empty_locked()
            if len(_hits) >= MAX_TRACKED_IPS:
                _evict_oldest_locked()
            _hits[ip] = deque([now])
            return None
        if len(q) >= limit:
            retry = int(max(1, window - (now - q[0])))
            _drop_empty_locked()
            return retry
        q.append(now)
        _drop_empty_locked()
        return None


def error_body(*, code: str, message: str, request_id: str, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": message,
            "code": code,
            "request_id": request_id,
            "note": "Original Memory never entered the helper. All data has been ephemerally forgotten.",
        },
    )
