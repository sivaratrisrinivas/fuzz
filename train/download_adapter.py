#!/usr/bin/env python3
"""Fetch a published Reconstructing adapter if it is not committed locally.

Usage:
  python3 train/download_adapter.py

Looks at FUZZ_SMART_ROBOT_ADAPTER_REPO (default: none) and writes
train/artifacts/qwen25-0.5b-reconstruct-lora/. If the directory already has
adapter_config.json, this is a no-op. The committed tree prefers in-repo weights
so a clean checkout can eval without extra credentials.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "train" / "artifacts" / "qwen25-0.5b-reconstruct-lora"


def main() -> int:
    if (DEST / "adapter_config.json").exists():
        print(f"Adapter already present at {DEST}")
        return 0
    repo = os.environ.get("FUZZ_SMART_ROBOT_ADAPTER_REPO", "").strip()
    if not repo:
        print(
            "No adapter at "
            f"{DEST} and FUZZ_SMART_ROBOT_ADAPTER_REPO is unset.\n"
            "Train locally:\n"
            "  pip install -r train/requirements.txt\n"
            "  python3 train/synthesize_dataset.py\n"
            "  python3 train/train_lora.py\n"
            "GPU (optional QLoRA on a larger Qwen2.5 Instruct):\n"
            "  FUZZ_TRAIN_GPU=1 FUZZ_SMART_ROBOT_ADAPTER_BASE=Qwen/Qwen2.5-7B-Instruct "
            "python3 train/train_lora.py --output train/artifacts/qwen25-7b-reconstruct-lora"
        )
        return 1
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=repo, local_dir=str(DEST))
    print(f"Downloaded {repo} -> {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
