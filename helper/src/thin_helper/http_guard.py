"""Rate limits, request ids, and structured errors for the thin helper.

Logs request metadata only (sizes, counts, duration). Never logs Fuzz text,
Fresh Clues words, prompts, or Reconstructed Memory.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections import defaultdict, deque
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def rate_limit_per_minute() -> int:
    try:
        return max(1, int(os.environ.get("FUZZ_RATE_LIMIT_PER_MINUTE", "30")))
    except ValueError:
        return 30


def check_rate_limit(ip: str) -> Optional[int]:
    """Return retry-after seconds when limited, else None."""
    window = 60.0
    limit = rate_limit_per_minute()
    now = time.monotonic()
    with _lock:
        q = _hits[ip]
        while q and now - q[0] >= window:
            q.popleft()
        if len(q) >= limit:
            retry = int(max(1, window - (now - q[0])))
            return retry
        q.append(now)
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
