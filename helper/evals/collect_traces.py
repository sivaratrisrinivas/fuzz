#!/usr/bin/env python3
"""Collect fresh Smart Robot traces on held-out Memories through any OpenAI-compatible endpoint.

Uses the play pipeline: FuzzSimulator starring (bun), PromptConstructor, and the play chat
messages from smart_robot.build_smart_robot_messages. Only the raw model text is stored, so
the parser and output checks can be scored on traces they were not designed on.

  OPENAI_BASE_URL=https://api.groq.com/openai/v1 OPENAI_API_KEY=... \
    python evals/collect_traces.py --model allam-2-7b --output evals/traces_heldout.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "helper" / "src"))

from thin_helper.prompt_constructor import PromptConstructor  # noqa: E402
from thin_helper.smart_robot import build_smart_robot_messages  # noqa: E402


def load_bench():
    path = ROOT / "bench" / "gs_t6_reconstruction_accuracy.py"
    spec = importlib.util.spec_from_file_location("gs_t6_bench", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def call(base_url: str, key: str, model: str, prompt: str, max_tokens: int) -> str:
    body = {
        "model": model,
        "messages": build_smart_robot_messages(prompt),
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }
    for attempt in range(6):
        try:
            r = httpx.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json=body,
                timeout=120,
            )
        except httpx.HTTPError as exc:
            print(f"  network error: {exc}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            wait = float(r.headers.get("retry-after") or 5 * (attempt + 1))
            print(f"  HTTP {r.status_code}, waiting {wait:.0f}s", file=sys.stderr)
            time.sleep(min(wait, 120))
            continue
        r.raise_for_status()
        return r.json()["choices"][0]["message"].get("content") or ""
    raise RuntimeError("model call kept failing")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--memories", type=Path, default=HERE / "memories_heldout.json")
    ap.add_argument("--levels", default="0.0,0.3,0.6,0.9")
    ap.add_argument("--max-tokens", type=int, default=1200)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not key:
        print("set OPENAI_API_KEY or GROQ_API_KEY", file=sys.stderr)
        return 2
    bench = load_bench()
    pc = PromptConstructor()
    memories = json.loads(args.memories.read_text())["memories"]
    levels = [float(x) for x in args.levels.split(",")]
    done = {}
    if args.output.exists():
        done = {(t["memory_id"], t["fuzz_level"]): t for t in json.loads(args.output.read_text())["trials"]}
    trials = []
    for m in memories:
        for i, lvl in enumerate(levels):
            if (m["id"], lvl) in done:
                trials.append(done[(m["id"], lvl)])
                continue
            fuzz = bench.dissolve_with_product_simulator(m["text"], lvl, 1000 + i, m["id"])["final_fuzz"]
            raw = call(base_url, key, args.model, pc.build_prompt(fuzz, []), args.max_tokens)
            trials.append({"memory_id": m["id"], "fuzz_level": lvl, "final_fuzz": fuzz, "raw_output": raw})
            print(f"{m['id']} {lvl}: {len(raw)} chars", flush=True)
            args.output.write_text(json.dumps({"model": args.model, "trials": trials}, indent=1) + "\n")
    args.output.write_text(json.dumps({"model": args.model, "trials": trials}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
