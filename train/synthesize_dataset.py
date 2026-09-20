#!/usr/bin/env python3
"""Synthesize offline Training data for the Reconstructing adapter (GS-T32).

- Invent Memory texts (not player data)
- Star them with box/src/fuzz-simulator.ts via bench/dissolve-with-simulator.ts
- Optional Fresh Clues (simulated Perfect Help)
- Targets = Quiet Rewrite paraphrases in the locked 4 Cleaning Steps format
- Hold out GS-T6 eval ids + oak-tree (the sample-fight-end-data.json Memory)

Does not send original Memory to the helper; this script is offline Training only.
"""

from __future__ import annotations

import hashlib
import json
import random
import shutil
import subprocess
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "helper" / "src"))
sys.path.insert(0, str(ROOT / "train"))

from build_target import build_target  # noqa: E402
from quiet_rewrite import quiet_rewrite  # noqa: E402
from thin_helper.prompt_constructor import PromptConstructor  # noqa: E402

SEED = 42
TRAIN_LEVELS = [0.2, 0.4, 0.6, 0.8]
DISSOLVE_HELPER = ROOT / "bench" / "dissolve-with-simulator.ts"
GS_T6_PATH = ROOT / "bench" / "gs-t6-memories.json"
SAMPLE_PATH = ROOT / "helper" / "prompts" / "sample-fight-end-data.json"
OUT_DIR = ROOT / "train" / "data"
HOLDOUT_IDS = frozenset({"oak-tree", "night-bus", "kitchen-radio", "library-rain", "porch-storm"})

WHEN = [
    "The first evening I",
    "Late in March I",
    "After the funeral I",
    "On my twenty-third birthday I",
    "The winter I left school I",
    "The week the power failed I",
    "Before dawn one Thursday I",
    "The summer the ferry stopped I",
]
PLACE = [
    "walked the long pier",
    "sat in the last pew",
    "stood under the station clock",
    "waited on the apartment stairs",
    "crossed the frozen creek",
    "leaned on the bakery window",
    "hid behind the rehearsal curtain",
    "rode the empty tram",
]
SENSORY = [
    "The air smelled of salt and warm metal.",
    "A radio in another room played three slow notes.",
    "Rain ticked on the glass like someone counting.",
    "The light was the color of weak tea.",
    "Dust hung in a single bright column.",
    "Someone had left orange peels on the sill.",
    "The floorboards gave a small tired sound.",
    "Steam wrote circles on the kitchen glass.",
]
PERSON = [
    "My sister kept her coat on",
    "An old man folded a newspaper twice",
    "The clerk did not look up",
    "A child traced a heart in the fog",
    "My father hummed without a tune",
    "Two strangers shared one umbrella",
    "The dog pressed against my knee",
    "A neighbor asked if I had eaten",
]
ACTION = [
    "and told a story I already knew.",
    "and asked me to wait five more minutes.",
    "and put a ticket stub in my hand.",
    "and pointed at a name on the wall.",
    "and laughed at a joke that was not funny.",
    "and left before I could answer.",
    "and watched the streetlights smear past.",
    "and counted the seconds between flashes.",
]
ENDING = [
    "I still hear that room when a house is too still.",
    "When I got outside the rain had already ended.",
    "Nobody went back for the chair until morning.",
    "I kept the stub in a book I never finished.",
    "The pavement smelled like dust and warm stone.",
    "I promised I would write and then I did not.",
    "The last lamp over the lot blinked twice and stayed.",
    "I walked home with both pockets full of cold air.",
]


def bun_bin() -> str:
    found = shutil.which("bun")
    if found:
        return found
    home = Path.home() / ".bun" / "bin" / "bun"
    if home.is_file():
        return str(home)
    raise RuntimeError("bun is required to drive box/src/fuzz-simulator.ts")


def dissolve(original: str, fuzz_level: float, seed: int, memory_id: str) -> dict:
    proc = subprocess.run(
        [bun_bin(), str(DISSOLVE_HELPER)],
        input=json.dumps(
            {
                "original": original,
                "fuzz_level": fuzz_level,
                "seed": seed,
                "memory_id": memory_id,
            }
        ),
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip() or f"exit {proc.returncode}"
        raise RuntimeError(f"FuzzSimulator dissolve helper failed: {err}")
    data = json.loads(proc.stdout)
    if "final_fuzz" not in data:
        raise RuntimeError("FuzzSimulator dissolve helper returned no final_fuzz")
    return data


def holdout_texts() -> list[str]:
    texts = []
    gs = json.loads(GS_T6_PATH.read_text(encoding="utf-8"))
    texts.extend(m["text"] for m in gs["memories"])
    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    texts.append(sample["original_memory_for_reference_only"])
    return texts


def ngrams(text: str, n: int = 10) -> set[str]:
    words = text.lower().split()
    return {" ".join(words[i : i + n]) for i in range(0, max(len(words) - n + 1, 0))}


def overlaps_holdout(text: str, banned: list[set[str]]) -> bool:
    grams = ngrams(text)
    return any(grams & b for b in banned)


def content_words(text: str) -> list[tuple[int, str]]:
    import re

    out = []
    for m in re.finditer(r"[A-Za-z][A-Za-z']{3,}", text):
        out.append((m.start(), m.group(0)))
    return out


def maybe_fresh_clues(
    original: str, fuzz: str, rng: random.Random, fuzz_level: float
) -> tuple[str, list[dict]]:
    """Half the rows get 1-2 simulated Fresh Clues restored into the Fuzz."""
    if rng.random() < 0.5:
        return fuzz, []
    words = [w for w in content_words(original) if len(w[1]) >= 4]
    if not words:
        return fuzz, []
    k = 1 if rng.random() < 0.65 else 2
    picks = words[: min(k, len(words))] if len(words) <= k else rng.sample(words, k)
    chars = list(fuzz)
    clues = []
    for start, word in picks:
        for i, ch in enumerate(word):
            idx = start + i
            if 0 <= idx < len(chars) and idx < len(original):
                chars[idx] = original[idx]
        clues.append(
            {
                "spot": f"approx chars {start}-{start + len(word) - 1} (words '{word}' in the Memory)",
                "words": word,
                "fuzz_level": round(fuzz_level * 10, 1),
            }
        )
    return "".join(chars), clues


def make_memories(count: int, banned: list[set[str]]) -> list[dict]:
    combos = list(product(WHEN, PLACE, SENSORY, PERSON, ACTION, ENDING))
    rng = random.Random(SEED)
    rng.shuffle(combos)
    memories = []
    for when, place, sensory, person, action, ending in combos:
        text = f"{when} {place}. {sensory} {person} {action} {ending}"
        if overlaps_holdout(text, banned):
            continue
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
        mem_id = f"syn-{digest}"
        if mem_id in HOLDOUT_IDS:
            continue
        memories.append({"id": mem_id, "text": text})
        if len(memories) >= count:
            break
    if len(memories) < count:
        raise RuntimeError(f"Only synthesized {len(memories)} Memories; need {count}")
    return memories


def main() -> int:
    banned = [ngrams(t) for t in holdout_texts()]
    memories = make_memories(72, banned)
    ctor = PromptConstructor()
    rng = random.Random(SEED)
    rows = []
    total = len(memories) * len(TRAIN_LEVELS)
    done = 0
    print(f"Synthesizing {total} training rows from {len(memories)} Memories ...", flush=True)
    for mem in memories:
        quiet = quiet_rewrite(mem["text"], salt=mem["id"])
        if quiet.strip() == mem["text"].strip():
            raise RuntimeError(f"Quiet Rewrite collapsed to Exact Copy for {mem['id']}")
        for level in TRAIN_LEVELS:
            done += 1
            dissolved = dissolve(mem["text"], level, SEED, mem["id"])
            fuzz, clues = maybe_fresh_clues(mem["text"], dissolved["final_fuzz"], rng, level)
            prompt = ctor.build_prompt(fuzz, clues)
            target = build_target(fuzz, mem["text"], quiet, clues)
            rows.append(
                {
                    "id": f"{mem['id']}-f{level:.1f}",
                    "memory_id": mem["id"],
                    "split": "train",
                    "fuzz_level": level,
                    "memory": mem["text"],
                    "quiet_rewrite": quiet,
                    "final_fuzz": fuzz,
                    "fresh_clues": clues,
                    "prompt": prompt,
                    "target": target,
                    "replaced_chars": dissolved.get("replaced_chars"),
                }
            )
            if done % 20 == 0 or done == total:
                print(f"  {done}/{total}", flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_path = OUT_DIR / "train.jsonl"
    with train_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    gs = json.loads(GS_T6_PATH.read_text(encoding="utf-8"))
    locked = {
        "description": (
            "Locked Reconstructing eval. GS-T6 four Memories only. "
            "oak-tree (sample-fight-end-data.json) is excluded from scoring. "
            "These texts must never appear in train.jsonl."
        ),
        "excluded_memory_ids": sorted(HOLDOUT_IDS),
        "memories": gs["memories"],
        "targets": {m["id"]: quiet_rewrite(m["text"], salt=f"eval-{m['id']}") for m in gs["memories"]},
    }
    locked_path = OUT_DIR / "locked_eval.json"
    locked_path.write_text(json.dumps(locked, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "holdout_ids.json").write_text(
        json.dumps({"excluded_memory_ids": sorted(HOLDOUT_IDS)}, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {train_path} ({len(rows)} rows)")
    print(f"Wrote {locked_path}")
    print(f"Holdout ids: {sorted(HOLDOUT_IDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
