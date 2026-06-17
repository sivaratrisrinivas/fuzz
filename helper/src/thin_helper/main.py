"""Thin helper (Python) entrypoint - FastAPI shell.

Per ADR-0001: Python/FastAPI thin helper computer.
Per PRD + issue #2 (this slice): only shell, no implementation of Reconstructing, no prompt construction,
no Smart Robot call yet. Those come in later vertical slices (#5, #6) after prompt validation (#3).

The live fight box owns the real-time Dissolving, The Waves, Fuzz Levels, Rewriting and Fresh Clues capture
(Perfect Help timing). The thin helper receives only final Fuzz + list of Fresh Clues (position/spot, words, Fuzz Level)
at the end of the Endless Fight, then forgets everything after one Smart Robot call.

All terms here are from the locked glossary in CONTEXT.md.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .reconstruct_coordinator import ReconstructCoordinator

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fuzz Thin Helper",
    description=(
        "Thin helper for the Fuzz game (Feeling Science, Real Experience, Word Lesson). "
        "Coordinator for Smart Robot Reconstructing using exactly 4 Cleaning Steps, "
        "Best Guess via Creative Guessing (not Exact Copy), Fresh Clues for Perfect Help. "
        "Ephemeral only - forgets all data (Fuzz, Fresh Clues) immediately after the call. "
        "See PRD #1, ADR-0001, CONTEXT.md, issues #2/#5/#6."
    ),
    version="0.3.0-issue6-one-call-ephemeral",
)

# CORS middleware for dev: allows the live fight box (Bun dev server on port 3000)
# to call the thin helper (port 8000) directly without proxy during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# The Reconstruct Coordinator (deep module, only entrypoint per issue #5) is instantiated here.
# It owns Prompt Constructor + parsing + (for this slice) the stubbed reconstruct path using validated #3 sample.
_coordinator = ReconstructCoordinator()


@app.get("/")
def read_root():
    """Health / placeholder for the thin helper shell."""
    return {
        "status": "thin-helper-shell-ready",
        "message": (
            "Thin helper shell running. "
            "Future Reconstruct Coordinator will handle one Smart Robot call for Reconstructing "
            "with the 4 Cleaning Steps after the Endless Fight in the live fight box. "
            "No Memory or data is stored."
        ),
        "glossary": "Uses only terms from CONTEXT.md: Memory, Fuzz, Fresh Clues, 4 Cleaning Steps, Quiet Rewrite, etc.",
    }


@app.get("/health")
def health():
    return {"status": "ok", "component": "thin helper (Python) shell per issue #2"}


@app.post("/reconstruct")
def reconstruct_endpoint(payload: dict):
    """Basic endpoint (issue #5 ACs).

    Receives the data contract {final_fuzz, fresh_clues: [...] } produced by the live fight box at end of Endless Fight.
    Delegates to the Reconstruct Coordinator (the only entrypoint), which builds the locked prompt and (for this slice)
    returns structured 4 Cleaning Steps + Reconstructed Memory using the stubbed #3 sample path.
    Real Smart Robot one-call + immediate forget of all data is implemented in #6.

    Thin coordinator only. Privacy: only contract fields are accepted; original Memory never enters the helper.
    """
    try:
        result = _coordinator.reconstruct_from_fight_end(payload)
        return result
    except Exception as exc:
        logger.exception("Reconstructing failed during one Smart Robot call (ephemeral forget still applies).")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Reconstructing encountered an issue. The Smart Robot may be slow or unavailable.",
                "detail": str(exc),
                "note": "Original Memory never entered the helper. All data has been ephemerally forgotten.",
            },
        )
