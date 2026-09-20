#!/usr/bin/env python3
"""PEFT LoRA Training for the Fuzz Smart Robot Reconstructing adapter.

Trains on the locked 4 Cleaning Steps prompt format used in play
(thin_helper.smart_robot.build_smart_robot_messages). Targets are Quiet Rewrite
paraphrases, not verbatim originals.

CPU path (committed demo numbers): Qwen/Qwen2.5-0.5B-Instruct, LoRA r=8, n_gpu_layers=0.
GPU path (optional, not required for the committed table): set FUZZ_TRAIN_GPU=1 to use
QLoRA 4-bit on a larger Qwen2.5 Instruct (7B) if a CUDA device is visible.

Default play model family remains Qwen2.5 Instruct (ADR-0002). Swap serving model with
FUZZ_SMART_ROBOT_MODEL. This adapter is task-specific Training for Reconstructing.

One command from the repo root (CPU):
  pip install -r train/requirements.txt
  python3 train/synthesize_dataset.py
  python3 train/train_lora.py

Smoke (no meaningful adapter, CI-friendly if transformers is installed):
  python3 train/train_lora.py --smoke
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER_SRC = ROOT / "helper" / "src"
sys.path.insert(0, str(HELPER_SRC))
sys.path.insert(0, str(ROOT / "train"))

from thin_helper.smart_robot import (  # noqa: E402
    ADAPTER_BASE_DEFAULT,
    FORMAT_SYSTEM_PROMPT,
    build_smart_robot_messages,
)

DEFAULT_OUT = ROOT / "train" / "artifacts" / "qwen25-0.5b-reconstruct-lora"
TRAIN_JSONL = ROOT / "train" / "data" / "train.jsonl"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train a PEFT LoRA Reconstructing adapter")
    p.add_argument("--model", default=os.environ.get("FUZZ_SMART_ROBOT_ADAPTER_BASE", ADAPTER_BASE_DEFAULT))
    p.add_argument("--data", default=str(TRAIN_JSONL))
    p.add_argument("--output", default=str(DEFAULT_OUT))
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--lora-r", type=int, default=8)
    p.add_argument("--lora-alpha", type=int, default=16)
    p.add_argument("--max-seq-len", type=int, default=1536)
    p.add_argument("--max-steps", type=int, default=-1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--smoke", action="store_true", help="One tiny step to verify the loop")
    return p.parse_args()


def load_rows(path: Path, smoke: bool) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if smoke and len(rows) >= 4:
                break
    if not rows:
        raise RuntimeError(f"No training rows in {path}. Run python3 train/synthesize_dataset.py first.")
    return rows


def main() -> int:
    args = parse_args()
    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig, TaskType, get_peft_model
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            DataCollatorForSeq2Seq,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise RuntimeError(
            "Training needs torch, transformers, datasets, peft. pip install -r train/requirements.txt"
        ) from exc

    gpu = torch.cuda.is_available() and os.environ.get("FUZZ_TRAIN_GPU") == "1"
    if gpu:
        print("GPU path: QLoRA requested via FUZZ_TRAIN_GPU=1", flush=True)
    else:
        print("CPU path: LoRA on Qwen2.5 Instruct (n_gpu_layers=0).", flush=True)

    random.seed(args.seed)
    rows = load_rows(Path(args.data), args.smoke)
    print(f"Training rows: {len(rows)}  model: {args.model}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model_kwargs = {"trust_remote_code": True}
    if gpu:
        try:
            from transformers import BitsAndBytesConfig

            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
            )
            model_kwargs["device_map"] = "auto"
        except Exception as exc:
            print(f"QLoRA bitsandbytes unavailable ({exc}); using full LoRA on GPU.", flush=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, **model_kwargs)
    model.config.use_cache = False

    lora = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
        bias="none",
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    def tokenize_row(row: dict) -> dict:
        messages = build_smart_robot_messages(row["prompt"])
        prompt_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        full_text = prompt_text + row["target"] + (tokenizer.eos_token or "")
        full = tokenizer(full_text, truncation=True, max_length=args.max_seq_len)
        prompt_ids = tokenizer(prompt_text, truncation=True, max_length=args.max_seq_len)["input_ids"]
        labels = list(full["input_ids"])
        prompt_len = min(len(prompt_ids), len(labels))
        labels[:prompt_len] = [-100] * prompt_len
        full["labels"] = labels
        return full

    tokenized = [tokenize_row(r) for r in rows]
    ds = Dataset.from_list(tokenized)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    max_steps = 1 if args.smoke else args.max_steps
    training_args = TrainingArguments(
        output_dir=str(out_dir / "trainer-work"),
        num_train_epochs=args.epochs if max_steps < 0 else 1,
        max_steps=max_steps if max_steps > 0 else -1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4 if not args.smoke else 1,
        learning_rate=args.lr,
        logging_steps=5 if not args.smoke else 1,
        save_strategy="no",
        report_to=[],
        fp16=False,
        bf16=False,
        seed=args.seed,
        remove_unused_columns=False,
        dataloader_num_workers=0,
        use_cpu=not gpu,
    )
    collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        data_collator=collator,
    )
    trainer.train()
    if args.smoke:
        print("Smoke Training finished (adapter not promoted as the demo artifact).", flush=True)
        return 0
    model.save_pretrained(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))
    meta = {
        "base_model": args.model,
        "family": "Qwen2.5 Instruct",
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "target_modules": ["q_proj", "v_proj"],
        "rows": len(rows),
        "epochs": args.epochs,
        "lr": args.lr,
        "max_seq_len": args.max_seq_len,
        "seed": args.seed,
        "cpu_forced": not gpu,
        "prompt": "play-identical FORMAT_SYSTEM_PROMPT + locked 4 Cleaning Steps user prompt",
        "targets": "Quiet Rewrite paraphrases, not verbatim originals",
        "format_system_prompt": FORMAT_SYSTEM_PROMPT,
        "note": (
            "Exact match 0 vs original Memory is by design. Adapter is task-specific. "
            "Default play model remains Qwen/Qwen2.5-7B-Instruct unless FUZZ_SMART_ROBOT_MODEL is set."
        ),
    }
    (out_dir / "train_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote adapter to {out_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
