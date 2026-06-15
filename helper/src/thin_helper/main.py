"""Thin helper (Python) entrypoint - FastAPI shell.

Per ADR-0001: Python/FastAPI thin helper computer.
Per PRD + issue #2 (this slice): only shell, no implementation of Reconstructing, no prompt construction,
no Smart Robot call yet. Those come in later vertical slices (#5, #6) after prompt validation (#3).

The live fight box owns the real-time Dissolving, The Waves, Fuzz Levels, Rewriting and Fresh Clues capture
(Perfect Help timing). The thin helper receives only final Fuzz + list of Fresh Clues (position/spot, words, Fuzz Level)
at the end of the Endless Fight, then forgets everything after one Smart Robot call.

All terms here are from the locked glossary in CONTEXT.md.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Fuzz Thin Helper",
    description=(
        "Thin helper for the Fuzz game (Feeling Science, Real Experience, Word Lesson). "
        "Coordinator for Smart Robot Reconstructing using exactly 4 Cleaning Steps, "
        "Best Guess via Creative Guessing (not Exact Copy), Fresh Clues for Perfect Help. "
        "Ephemeral only - forgets all data (Fuzz, Fresh Clues) immediately after the call. "
        "See PRD #1, ADR-0001, CONTEXT.md, issues #2/#5/#6."
    ),
    version="0.1.0-shell",
)


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
