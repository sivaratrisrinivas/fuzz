"""Thin helper (Python) entrypoint - FastAPI.

Per ADR-0001: Python/FastAPI thin helper computer.
Per PRD + issues #2/#5/#6: Reconstruct Coordinator is the only Reconstructing entrypoint.
The live fight box owns the real-time Dissolving, The Waves, Fuzz Levels, Rewriting and Fresh Clues capture
(Perfect Help timing). The thin helper receives only final Fuzz + list of Fresh Clues (position/spot, words, Fuzz Level)
at the end of the Endless Fight, then immediately forgets everything after one Smart Robot call.

Production (GS-T32): health, request timeouts, structured errors, per-IP rate limits, CORS from env,
request logging without storing Fuzz text, rejection of original Memory fields.

All terms here are from the locked glossary in CONTEXT.md.
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .contract import ContractError, sanitize_fight_end
from .http_guard import check_rate_limit, client_ip, error_body, new_request_id
from .reconstruct_coordinator import ReconstructCoordinator
from .smart_robot import DEFAULT_MODEL, resolved_model_name

logger = logging.getLogger("thin_helper")
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=os.environ.get("FUZZ_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s request_id=%(request_id)s %(message)s",
    )


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


logger.addFilter(_RequestIdFilter())


def _cors_origins() -> list[str]:
    raw = os.environ.get("FUZZ_CORS_ORIGINS", "").strip()
    if raw:
        return [item.strip() for item in raw.split(",") if item.strip()]
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("thin helper starting model=%s", resolved_model_name(), extra={"request_id": "-"})
    yield
    logger.info("thin helper stopping; ephemeral forget still applies", extra={"request_id": "-"})


app = FastAPI(
    title="Fuzz Thin Helper",
    description=(
        "Thin helper for the Fuzz game (Feeling Science, Real Experience, Word Lesson). "
        "Coordinator for Smart Robot Reconstructing using exactly 4 Cleaning Steps, "
        "Best Guess via Creative Guessing (not Exact Copy), Fresh Clues for Perfect Help. "
        "Ephemeral only - immediately forgets all data (Fuzz, Fresh Clues) after the call. "
        "See PRD #1, ADR-0001, CONTEXT.md, issues #2/#5/#6."
    ),
    version="0.4.0-gs-t32",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)

# The Reconstruct Coordinator (deep module, only entrypoint per issue #5) is instantiated here.
# It owns Prompt Constructor + parsing + one Smart Robot call + immediate ephemeral forget (issue #6).
_coordinator = ReconstructCoordinator()


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or new_request_id()
    request.state.request_id = request_id
    started = time.monotonic()
    response = await call_next(request)
    duration_ms = int((time.monotonic() - started) * 1000)
    response.headers["X-Request-Id"] = request_id
    # Structured request log: method, path, status, duration, never Fuzz text.
    logger.info(
        "http method=%s path=%s status=%s duration_ms=%s ip=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        client_ip(request),
        extra={"request_id": request_id},
    )
    return response


@app.get("/")
def read_root():
    """Health / placeholder for the thin helper shell."""
    return {
        "status": "thin-helper-shell-ready",
        "message": (
            "Thin helper shell running. "
            "The Reconstruct Coordinator handles one Smart Robot call for Reconstructing "
            "with the 4 Cleaning Steps after the Endless Fight in the live fight box. "
            "No Memory or data is stored. The helper immediately forgets Fuzz and Fresh Clues."
        ),
        "glossary": "Uses only terms from CONTEXT.md: Memory, Fuzz, Fresh Clues, 4 Cleaning Steps, Quiet Rewrite, etc.",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "component": "thin helper (Python) shell per issue #2",
        "model": resolved_model_name(),
        "default_model_family": DEFAULT_MODEL,
        "ephemeral": True,
        "accepts_memory": False,
    }


@app.get("/ready")
def ready():
    return {"status": "ready", "component": "thin helper"}


@app.post("/reconstruct")
def reconstruct_endpoint(payload: dict, request: Request):
    """Basic endpoint (issue #5 ACs) with GS-T32 production guards.

    Receives the data contract {final_fuzz, fresh_clues: [...] } produced by the live fight box at end of Endless Fight.
    Rejects original Memory fields. Rate-limits by IP. Delegates to the Reconstruct Coordinator (the only entrypoint).
    Real Smart Robot one-call + immediate forget of all data is implemented in #6.

    Thin coordinator only. Privacy: only contract fields are accepted; original Memory never enters the helper.
    Request logs record sizes and counts, never Fuzz text.
    """
    request_id = getattr(request.state, "request_id", new_request_id())
    ip = client_ip(request)
    retry_after = check_rate_limit(ip)
    if retry_after is not None:
        body = error_body(
            code="rate_limited",
            message="Too many Reconstructing requests. Try again shortly.",
            request_id=request_id,
            status=429,
        )
        body.headers["Retry-After"] = str(retry_after)
        return body

    try:
        contract = sanitize_fight_end(payload)
    except ContractError as exc:
        status = 400
        return error_body(code=exc.code, message=exc.message, request_id=request_id, status=status)

    logger.info(
        "reconstruct fuzz_chars=%s fresh_clues=%s",
        len(contract["final_fuzz"]),
        len(contract["fresh_clues"]),
        extra={"request_id": request_id},
    )

    try:
        result = _coordinator.reconstruct_from_fight_end(contract)
        result["request_id"] = request_id
        return result
    except Exception as exc:
        logger.exception(
            "Reconstructing failed during one Smart Robot call (ephemeral forget still applies).",
            extra={"request_id": request_id},
        )
        return error_body(
            code="reconstruct_failed",
            message="Reconstructing encountered an issue. The Smart Robot may be slow or unavailable.",
            request_id=request_id,
            status=500,
        )
    finally:
        payload = {}
        contract = {}
