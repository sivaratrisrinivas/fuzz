#!/usr/bin/env python3
"""GS-T6: Reconstructing accuracy across Fuzz Levels.

Closest harness: helper/scripts/validate-smart-robot-on-dev.py
This script imports that file's one-call helpers (prompt build + Smart Robot chat)
and scores the Reconstructed Memory with ReconstructCoordinator.parse_reconstruction,
the same parser the thin helper uses in play.

Dissolving matches box/src/fuzz-simulator.ts: selected characters become '*'.
Fresh Clues are left empty so the curve is Fuzz Level only.

One command from the repo root:
  pip install -r helper/requirements.txt && python3 bench/gs_t6_reconstruction_accuracy.py

Writes bench/gs-t6-reconstruction-accuracy.json and prints a markdown table.
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import random
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parent.parent
HELPER_SRC = ROOT / "helper" / "src"
HARNESS_PATH = ROOT / "helper" / "scripts" / "validate-smart-robot-on-dev.py"
MEMORIES_PATH = ROOT / "bench" / "gs-t6-memories.json"
DEFAULT_OUTPUT = ROOT / "bench" / "gs-t6-reconstruction-accuracy.json"
SEED = 42
# Eleven points from intact Memory to fully dissolved, enough to see collapse.
FUZZ_LEVELS = [round(i / 10, 1) for i in range(11)]

sys.path.insert(0, str(HELPER_SRC))


def load_harness():
    spec = importlib.util.spec_from_file_location("validate_smart_robot_on_dev", HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load closest harness at {HARNESS_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_coordinator_class():
    from thin_helper.reconstruct_coordinator import ReconstructCoordinator

    return ReconstructCoordinator


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def bag_f1(original: str, reconstructed: str) -> float:
    orig = tokenize(original)
    recon = tokenize(reconstructed)
    if not orig and not recon:
        return 1.0
    if not orig or not recon:
        return 0.0
    overlap = sum((Counter(orig) & Counter(recon)).values())
    precision = overlap / max(len(recon), 1)
    recall = overlap / max(len(orig), 1)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def edit_similarity(original: str, reconstructed: str) -> float:
    denom = max(len(original), len(reconstructed), 1)
    return 1.0 - (levenshtein(original, reconstructed) / denom)


def remaining_clue_ratio(original: str, fuzz: str) -> float:
    if not original:
        return 1.0
    n = min(len(original), len(fuzz))
    same = sum(1 for i in range(n) if original[i] == fuzz[i])
    extra = abs(len(original) - len(fuzz))
    return same / max(len(original) + extra, 1)


def dissolve_memory(original: str, fuzz_level: float, rng: random.Random) -> str:
    """Replace fuzz_level fraction of characters with '*', same junk as FuzzSimulator."""
    if fuzz_level <= 0 or not original:
        return original
    n = len(original)
    k = min(n, int(round(fuzz_level * n)))
    indices = list(range(n))
    rng.shuffle(indices)
    chars = list(original)
    for i in indices[:k]:
        chars[i] = "*"
    return "".join(chars)


def git_sha() -> Optional[str]:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def cpu_model() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def memory_gb() -> Optional[float]:
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = float(line.split()[1])
                    return round(kb / (1024 * 1024), 2)
    except (OSError, ValueError, IndexError):
        return None
    return None


def gpu_name() -> str:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out.splitlines()[0] if out else "none"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "none"


def collect_hardware() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu": cpu_model(),
        "cpu_count": os.cpu_count(),
        "memory_gb": memory_gb(),
        "gpu": gpu_name(),
    }


def mean(values: list[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def fmt(value: Optional[float], digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def print_table(summaries: list[dict[str, Any]]) -> None:
    headers = [
        "Fuzz level",
        "Remaining clues",
        "Word F1",
        "Edit similarity",
        "Exact match",
        "Failures",
    ]
    rows = []
    for row in summaries:
        n = row["n"]
        n_ok = row["n_ok"]
        exact = row["exact_match_count"]
        rows.append(
            [
                f"{row['fuzz_level']:.1f}",
                fmt(row["mean_remaining_clue_ratio"]),
                fmt(row["mean_word_f1"]),
                fmt(row["mean_edit_similarity"]),
                f"{exact}/{n_ok}" if n_ok else f"0/{n_ok}",
                f"{row['n_failed']}/{n}",
            ]
        )
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def line(cells: list[str], sep: str = " | ") -> str:
        return "| " + sep.join(cell.ljust(widths[i]) for i, cell in enumerate(cells)) + " |"

    print(line(headers))
    print("| " + " | ".join("-" * w for w in widths) + " |")
    for row in rows:
        print(line(row))


def summarize(trials: list[dict[str, Any]], levels: list[float]) -> list[dict[str, Any]]:
    out = []
    for level in levels:
        subset = [t for t in trials if t["fuzz_level"] == level]
        ok = [t for t in subset if t["status"] == "ok"]
        failed = [t for t in subset if t["status"] != "ok"]
        out.append(
            {
                "fuzz_level": level,
                "n": len(subset),
                "n_ok": len(ok),
                "n_failed": len(failed),
                "mean_remaining_clue_ratio": mean(
                    [t["remaining_clue_ratio"] for t in subset]
                ),
                "mean_word_f1": mean([t["word_f1"] for t in ok if t["word_f1"] is not None]),
                "mean_edit_similarity": mean(
                    [t["edit_similarity"] for t in ok if t["edit_similarity"] is not None]
                ),
                "exact_match_count": sum(1 for t in ok if t["exact_match"]),
                "exact_match_rate": (
                    sum(1 for t in ok if t["exact_match"]) / len(ok) if ok else None
                ),
                "errors": [t["error"] for t in failed],
            }
        )
    return out


def run_trial(
    *,
    memory_id: str,
    original: str,
    fuzz_level: float,
    seed: int,
    build_prompt: Callable[..., str],
    call_smart_robot: Callable[[str], str],
    parse_reconstruction: Callable[[str], dict],
) -> dict[str, Any]:
    rng = random.Random(f"{seed}:{memory_id}:{fuzz_level}")
    fuzz = dissolve_memory(original, fuzz_level, rng)
    remaining = remaining_clue_ratio(original, fuzz)
    trial: dict[str, Any] = {
        "memory_id": memory_id,
        "fuzz_level": fuzz_level,
        "final_fuzz": fuzz,
        "remaining_clue_ratio": remaining,
        "replaced_chars": sum(1 for a, b in zip(original, fuzz) if a != b)
        + abs(len(original) - len(fuzz)),
        "status": "ok",
        "error": None,
        "reconstructed_memory": None,
        "word_f1": None,
        "edit_similarity": None,
        "exact_match": None,
    }
    try:
        prompt = build_prompt(fuzz, [])
        raw = call_smart_robot(prompt)
        parsed = parse_reconstruction(raw)
        recon = (parsed.get("reconstructed_memory") or "").strip()
        if not recon:
            raise RuntimeError("parsed reconstructed_memory was empty")
        trial["reconstructed_memory"] = recon
        trial["word_f1"] = bag_f1(original, recon)
        trial["edit_similarity"] = edit_similarity(original, recon)
        trial["exact_match"] = original.strip() == recon
    except Exception as exc:
        trial["status"] = "failed"
        trial["error"] = f"{type(exc).__name__}: {exc}"
    return trial


def main() -> int:
    harness = load_harness()
    ReconstructCoordinator = load_coordinator_class()
    coordinator = ReconstructCoordinator()
    memories_doc = json.loads(MEMORIES_PATH.read_text(encoding="utf-8"))
    memories = memories_doc["memories"]
    model_name = harness.resolved_model_name()
    date_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hardware = collect_hardware()
    sha = git_sha()

    print("GS-T6 Reconstructing accuracy across Fuzz Levels")
    print(f"Closest harness: {HARNESS_PATH.relative_to(ROOT)}")
    print(f"Model: {model_name}")
    print(f"Date: {date_iso}")
    print(f"Dataset size: {len(memories)} memories")
    print(f"Fuzz levels: {FUZZ_LEVELS}")
    print(f"Hardware: {hardware}")
    print(f"Git SHA: {sha}")
    print()

    trials: list[dict[str, Any]] = []
    total = len(memories) * len(FUZZ_LEVELS)
    done = 0
    for mem in memories:
        for level in FUZZ_LEVELS:
            done += 1
            print(
                f"[{done}/{total}] memory={mem['id']} fuzz_level={level:.1f} ...",
                flush=True,
            )
            trial = run_trial(
                memory_id=mem["id"],
                original=mem["text"],
                fuzz_level=level,
                seed=SEED,
                build_prompt=harness.build_full_prompt,
                call_smart_robot=harness.call_smart_robot,
                parse_reconstruction=coordinator.parse_reconstruction,
            )
            if trial["status"] == "ok":
                print(
                    f"  ok word_f1={fmt(trial['word_f1'])} "
                    f"edit={fmt(trial['edit_similarity'])} "
                    f"remaining={fmt(trial['remaining_clue_ratio'])}",
                    flush=True,
                )
            else:
                print(f"  FAILED {trial['error']}", flush=True)
            trials.append(trial)

    by_level = summarize(trials, FUZZ_LEVELS)
    payload = {
        "gate": "GS-T6",
        "title": "Reconstructing accuracy across Fuzz Levels",
        "date": date_iso,
        "model": model_name,
        "model_source": "huggingface_inference_client",
        "temperature": harness.TEMPERATURE,
        "max_tokens": harness.MAX_TOKENS,
        "seed": SEED,
        "dataset_size": len(memories),
        "dataset_path": str(MEMORIES_PATH.relative_to(ROOT)),
        "fresh_clues": [],
        "fresh_clues_note": (
            "Empty on purpose. This sweep isolates Fuzz Level. Player Rewriting is not mixed in."
        ),
        "quiet_rewrite_note": (
            "The locked prompt asks for a Quiet Rewrite, so exact match can stay low even when Fuzz is light."
        ),
        "hardware": hardware,
        "git_sha": sha,
        "closest_harness": str(HARNESS_PATH.relative_to(ROOT)),
        "fuzz_levels": FUZZ_LEVELS,
        "by_fuzz_level": by_level,
        "trials": trials,
    }
    DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"Wrote {DEFAULT_OUTPUT.relative_to(ROOT)}")
    print()
    print("## Results")
    print()
    print_table(by_level)
    n_failed = sum(1 for t in trials if t["status"] != "ok")
    print()
    print(f"Trials: {len(trials)}. Failures: {n_failed}.")
    return 1 if n_failed == len(trials) else 0


if __name__ == "__main__":
    raise SystemExit(main())
