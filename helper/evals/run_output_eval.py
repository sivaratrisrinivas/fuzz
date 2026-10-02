#!/usr/bin/env python3
"""Output-quality eval for Reconstructing: parser plus output checks, old versus new.

Three sets:
  dev        132 real traces from bench/ (GS-T6 7B, GS-T32 0.5B base and LoRA), hand labeled.
             The rules in output_check.py were written from these, so dev is not a fair test.
  heldout    fresh traces from a model the rules never saw, on 12 new Memories
             (evals/traces_heldout.json, labels in evals/heldout_labels.json).
  synthetic  generated outputs with a known Memory: marker style x wrapper x ending x trailer,
             plus outputs that must be rejected. Split dev/test by case hash.

Metrics on labeled traces:
  shown_usable    usable traces where the player gets a non-empty Memory with no task chatter
  blocked_bad     not-usable traces where the helper returns empty (Box uses its fallback)

  python evals/run_output_eval.py            # print report
  python evals/run_output_eval.py --check    # exit 1 if below evals/baseline.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from thin_helper.output_check import _MARKER_LEAK, _META, clean_reconstruction, rejected  # noqa: E402
from thin_helper.reconstruct_coordinator import ReconstructCoordinator  # noqa: E402

COORD = ReconstructCoordinator(model_caller=lambda prompt: "")


def old_parse(raw_output: str) -> str:
    """The parser on main before this change, kept here as the comparison point."""
    cleaned = raw_output.strip()
    cleaned = re.sub(r"^```(?:text|markdown)?\n?|```$", "", cleaned, flags=re.IGNORECASE).strip()
    matches = list(re.finditer(r"=== (?:STEP \d+|RECONSTRUCTED MEMORY) ===", cleaned, re.IGNORECASE))
    if not matches:
        return re.sub(r"\n---+[\s\S]*$", "", cleaned).strip()
    memory = ""
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        if "RECONSTRUCTED MEMORY" in m.group(0).upper():
            memory = re.sub(r"\n---+[\s\S]*$", "", cleaned[m.end():end].strip()).strip()
    return memory


def new_pipeline(raw_output: str) -> tuple[str, list[str]]:
    memory, flags = clean_reconstruction(COORD.parse_reconstruction(raw_output))
    return ("" if rejected(flags) else memory), flags


def has_chatter(text: str) -> bool:
    return bool(_META.search(text) or _MARKER_LEAK.search(text))


def score_labeled(rows: list[dict]) -> dict:
    out = {}
    for name, fn in (("old", lambda r: old_parse(r)), ("new", lambda r: new_pipeline(r)[0])):
        good = bad = n_usable = n_bad = chatter_shown = 0
        for row in rows:
            shown = fn(row["raw_output"])
            if shown and has_chatter(shown):
                chatter_shown += 1
            if row["usable"]:
                n_usable += 1
                good += bool(shown) and not has_chatter(shown)
            else:
                n_bad += 1
                bad += not shown
        out[name] = {
            "shown_usable": [good, n_usable],
            "blocked_bad": [bad, n_bad],
            "shown_with_chatter": [chatter_shown, len(rows)],
        }
    return out


MEMORIES = [
    "The first time I rode the night bus home the windows were fogged and someone had drawn a heart.",
    "Sunday mornings the kitchen radio played the station my mother trusted.",
    "We sat on the porch and counted the seconds between lightning and thunder.",
    "I hid in the back aisle of the library when the rain turned the street silver.",
    "My uncle ran beside my bicycle and let go before I noticed.",
    "The fruit seller saved the ripest mangoes for my sister every summer.",
    "Our dog came home at dawn after the storm, muddy and shaking.",
    "Th* fir*t time I r*de the ni*ht bus the w*ndows were f*gged.",
    "We flew kites from the roof.\n\nMy kite tangled with the neighbor's and both strings snapped.",
]
MARKERS = {
    "exact": "=== {} ===",
    "lower": "=== {l} ===",
    "nospace": "==={}===",
    "split": "===\n{} ===",
    "markdown": "### {}",
    "bold": "**{}**",
    "colon": "{}:",
}
WRAPPERS = ("none", "fence_text", "fence_plain", "lead_line")
ENDINGS = ("final", "missing_final", "repeated")
TRAILERS = {
    "none": "",
    "meta": "\n\nThis reconstruction is a best guess with visible Quiet Rewrite changes.",
    "rule_notes": "\n\n---\nNotes: kept the strongest clues.",
    "note": "\n\nNote: I changed a few words so it is not an exact copy.",
    "repeat": "\n\n{memory}",
}
BAD_FINALS = {
    "placeholder": "[the final Reconstructed Memory. This is your Best Guess.]",
    "task_talk": "The player felt the Feeling Lesson while the Smart Robot cleaned the Fuzz.",
    "refusal": "I'm sorry, but I can't help with that request.",
    "stars_only": "******* **** ********",
    "prompt_echo": "Do one last quiet pass over the whole thing. Clean up the flow and meaning.",
    "headers": "FINAL FUZZ:\n*h* *i*st",
}


def marker(style: str, label: str) -> str:
    return MARKERS[style].replace("{l}", label.lower()).replace("{}", label)


def build(style: str, wrapper: str, ending: str, body_final: str, trailer: str) -> str:
    parts = [f"{marker(style, f'STEP {i}')}\nstep {i} draft text" for i in (1, 2, 3)]
    step4 = body_final if ending == "missing_final" else "step 4 draft text"
    parts.append(f"{marker(style, 'STEP 4')}\n{step4}")
    if ending == "final":
        parts.append(f"{marker(style, 'RECONSTRUCTED MEMORY')}\n{body_final}")
    elif ending == "repeated":
        parts.append(f"{marker(style, 'RECONSTRUCTED MEMORY')}\nan earlier draft")
        parts.append(f"{marker(style, 'STEP 4')}\nstep 4 again")
        parts.append(f"{marker(style, 'RECONSTRUCTED MEMORY')}\n{body_final}")
    text = "\n\n".join(parts) + trailer
    if wrapper == "fence_text":
        text = f"```text\n{text}\n```"
    elif wrapper == "fence_plain":
        text = f"```\n{text}\n```"
    elif wrapper == "lead_line":
        text = f"Here are the steps.\n\n{text}"
    return text


def split_for(case_id: str) -> str:
    return "test" if int(hashlib.sha256(case_id.encode()).hexdigest(), 16) % 2 else "dev"


def synthetic_cases() -> list[dict]:
    cases = []
    i = 0
    for style in MARKERS:
        for wrapper in WRAPPERS:
            for ending in ENDINGS:
                for tname, trailer in TRAILERS.items():
                    memory = MEMORIES[i % len(MEMORIES)]
                    i += 1
                    if tname == "repeat" and "\n\n" in memory:
                        memory = MEMORIES[0]
                    raw = build(style, wrapper, ending, memory, trailer.replace("{memory}", memory))
                    cid = f"ok/{style}/{wrapper}/{ending}/{tname}"
                    cases.append({"id": cid, "raw": raw, "expect": memory, "split": split_for(cid)})
                for bname, bad in BAD_FINALS.items():
                    raw = build(style, wrapper, ending, bad, "")
                    cid = f"bad/{style}/{wrapper}/{ending}/{bname}"
                    cases.append({"id": cid, "raw": raw, "expect": "", "split": split_for(cid)})
    for style in MARKERS:
        raw = "\n\n".join(f"{marker(style, f'STEP {i}')}\nstep {i} draft text" for i in (1, 2, 3))
        cid = f"bad/{style}/none/stopped_at_step3/-"
        cases.append({"id": cid, "raw": raw, "expect": "", "split": split_for(cid)})
    return cases


def score_synthetic(cases: list[dict]) -> dict:
    out: dict = {}
    for split in ("dev", "test"):
        sub = [c for c in cases if c["split"] == split]
        res = {}
        for name, fn in (("old", old_parse), ("new", lambda r: new_pipeline(r)[0])):
            correct = sum(fn(c["raw"]).strip() == c["expect"].strip() for c in sub)
            res[name] = [correct, len(sub)]
        res["new_misses"] = [c["id"] for c in sub if new_pipeline(c["raw"])[0].strip() != c["expect"].strip()]
        out[split] = res
    return out


def load_heldout() -> list[dict] | None:
    traces, labels = HERE / "traces_heldout.json", HERE / "heldout_labels.json"
    if not (traces.exists() and labels.exists()):
        return None
    lab = json.loads(labels.read_text())["labels"]
    rows = []
    for t in json.loads(traces.read_text())["trials"]:
        key = f"{t['memory_id']}/{t['fuzz_level']}"
        if key in lab:
            rows.append({"id": key, "raw_output": t["raw_output"], "usable": lab[key]["usable"]})
    return rows


def faithfulness_report() -> dict | None:
    """What the player actually reads on held-out traces, and whether the residual_fuzz flag finds echoes."""
    path, traces = HERE / "faithfulness_heldout.json", HERE / "traces_heldout.json"
    if not (path.exists() and traces.exists()):
        return None
    lab = json.loads(path.read_text())["labels"]
    counts: dict[str, int] = {}
    tp = fn = tn = fp = 0
    for t in json.loads(traces.read_text())["trials"]:
        key = f"{t['memory_id']}/{t['fuzz_level']}"
        if key not in lab:
            continue
        memory, flags = new_pipeline(t["raw_output"])
        counts[lab[key]] = counts.get(lab[key], 0) + 1
        echo, flagged = lab[key] == "echo_fuzz", "residual_fuzz" in flags
        tp += echo and flagged
        fn += echo and not flagged
        fp += flagged and not echo
        tn += not echo and not flagged
    return {"labels": counts, "residual_fuzz_flag": {"tp": tp, "fn": fn, "tn": tn, "fp": fp}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    dev = [json.loads(line) for line in (HERE / "traces_dev.jsonl").read_text().splitlines() if line]
    report = {"dev_real": {"n": len(dev), **score_labeled(dev)}}
    held = load_heldout()
    if held:
        report["heldout_real"] = {"n": len(held), **score_labeled(held)}
    faith = faithfulness_report()
    if faith:
        report["heldout_faithfulness"] = faith
    cases = synthetic_cases()
    report["synthetic"] = {"n": len(cases), **score_synthetic(cases)}

    def frac(p):
        return f"{p[0]}/{p[1]}"

    for key in ("dev_real", "heldout_real"):
        if key in report:
            r = report[key]
            for name in ("old", "new"):
                m = r[name]
                print(f"{key:13s} {name}: shown_usable {frac(m['shown_usable'])}, blocked_bad "
                      f"{frac(m['blocked_bad'])}, shown_with_chatter {frac(m['shown_with_chatter'])}")
    if faith:
        f = faith["residual_fuzz_flag"]
        print(f"heldout shown outputs by hand label: {faith['labels']}")
        print(f"residual_fuzz flag vs echo_fuzz label: caught {f['tp']}/{f['tp'] + f['fn']}, "
              f"clean readable passed {f['tn']}/{f['tn'] + f['fp']}")
    for split in ("dev", "test"):
        s = report["synthetic"][split]
        print(f"synthetic {split:4s} old {frac(s['old'])}, new {frac(s['new'])}")
        for miss in s["new_misses"][:10]:
            print(f"   new miss: {miss}")
    if args.json:
        args.json.write_text(json.dumps(report, indent=1) + "\n")
    if args.check:
        base = json.loads((HERE / "baseline.json").read_text())
        problems = []
        for key, floors in base.items():
            if key == "heldout_faithfulness":
                f = report.get(key, {}).get("residual_fuzz_flag")
                if f is None:
                    problems.append(f"{key} missing")
                elif f["tp"] < floors["min_echo_caught"] or f["fp"] > floors["max_readable_flagged"]:
                    problems.append(f"{key} residual_fuzz flag {f}")
                continue
            if key == "synthetic":
                for split, floor in floors.items():
                    got = report["synthetic"][split]["new"]
                    if got[0] < floor:
                        problems.append(f"synthetic {split} {got[0]} < {floor}")
                continue
            got = report.get(key, {}).get("new")
            if got is None:
                problems.append(f"{key} missing")
                continue
            for metric, floor in floors.items():
                if got[metric][0] < floor:
                    problems.append(f"{key} {metric} {got[metric][0]} < {floor}")
        if problems:
            print("REGRESSION: " + "; ".join(problems))
            return 1
        print("output-quality gates pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
