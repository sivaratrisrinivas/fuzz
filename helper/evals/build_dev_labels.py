#!/usr/bin/env python3
"""Write evals/traces_dev.jsonl: the 132 real traces in bench/ with a hand label each.

usable=true means the raw output holds a Memory-style reconstruction attempt (residual Fuzz
stars allowed) that should be shown to the player. usable=false means there is nothing to show:
the model stopped before STEP 4, looped, echoed the prompt, refused, or talked about the task.
Labels were made by reading every raw output (agent-made, needs a human spot check).
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

NOT_USABLE = {
    # GS-T6, 7B GGUF
    "t6/night-bus/0.6": "stopped_before_step4",
    "t6/night-bus/1.0": "prompt_echo",
    "t6/kitchen-radio/0.2": "stopped_before_step4",
    "t6/kitchen-radio/0.4": "stopped_before_step4",
    "t6/kitchen-radio/1.0": "stopped_before_step4",
    "t6/library-rain/0.5": "stopped_before_step4",
    "t6/library-rain/1.0": "stopped_before_step4",
    "t6/porch-storm/0.6": "stopped_before_step4",
    "t6/porch-storm/0.9": "stopped_before_step4",
    "t6/porch-storm/1.0": "task_talk",
    # GS-T32 before (0.5B base)
    "before/night-bus/0.3": "loop_no_final",
    "before/night-bus/0.6": "loop_no_final",
    "before/night-bus/0.9": "prompt_echo",
    "before/night-bus/1.0": "prompt_echo",
    "before/kitchen-radio/0.3": "task_talk",
    "before/kitchen-radio/0.4": "stopped_before_step4",
    "before/kitchen-radio/0.5": "task_talk",
    "before/kitchen-radio/0.6": "task_talk",
    "before/kitchen-radio/0.7": "stopped_before_step4",
    "before/kitchen-radio/0.9": "task_talk",
    "before/kitchen-radio/1.0": "task_talk",
    "before/library-rain/0.2": "prompt_echo",
    "before/library-rain/0.5": "stopped_before_step4",
    "before/library-rain/0.8": "no_words",
    "before/library-rain/0.9": "stopped_before_step4",
    "before/library-rain/1.0": "task_talk",
    "before/porch-storm/0.1": "prompt_echo",
    "before/porch-storm/0.2": "prompt_echo",
    "before/porch-storm/0.4": "task_talk",
    "before/porch-storm/0.8": "task_talk",
    "before/porch-storm/1.0": "task_talk",
    # GS-T32 after (0.5B LoRA)
    "after/night-bus/1.0": "prompt_echo",
    "after/kitchen-radio/1.0": "stopped_before_step4",
    "after/library-rain/0.9": "refusal",
    "after/porch-storm/1.0": "task_talk",
}

SOURCES = [
    ("t6", "bench/gs-t6-reconstruction-accuracy.json"),
    ("before", "bench/gs-t32-before.json"),
    ("after", "bench/gs-t32-after.json"),
]


def main() -> None:
    rows = []
    for tag, path in SOURCES:
        for t in json.loads((ROOT / path).read_text())["trials"]:
            key = f"{tag}/{t['memory_id']}/{t['fuzz_level']}"
            rows.append({
                "id": key,
                "fuzz_level": t["fuzz_level"],
                "raw_output": t["raw_output"] or "",
                "usable": key not in NOT_USABLE,
                "failure": NOT_USABLE.get(key, ""),
                "old_status": t["status"],
            })
    missing = set(NOT_USABLE) - {r["id"] for r in rows}
    assert not missing, missing
    with open(HERE / "traces_dev.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} rows, {sum(not r['usable'] for r in rows)} not usable")


if __name__ == "__main__":
    main()
