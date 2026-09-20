"""Shared Smart Robot chat contract used by play, bench, Training, and the validate script.

GS-T6 used a user-only chat call while ReconstructCoordinator._default_model_caller sent a
format system prompt. That made the committed GS-T6 table not production-identical.
This module is the single source for:

- FORMAT_SYSTEM_PROMPT (play)
- build_smart_robot_messages (system + user)
- extract_chat_content (empty string when content is missing; never dump the raw object)
- temperature / max_tokens / default model family

Play, bench, and Training must all call this so numbers match the live helper.

Default base family is Qwen2.5 Instruct (ADR-0002). Swap via FUZZ_SMART_ROBOT_MODEL.
A task-specific LoRA adapter (CPU-trained on Qwen2.5-0.5B-Instruct) is optional via
FUZZ_SMART_ROBOT_ADAPTER. Hugging Face remains the production path when a token or
dedicated endpoint is set. Original Memory never enters this module.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
ADAPTER_BASE_DEFAULT = "Qwen/Qwen2.5-0.5B-Instruct"
MAX_TOKENS = 1200
TEMPERATURE = 0.7

FORMAT_SYSTEM_PROMPT = (
    "You reconstruct text using exact === STEP 1 === through === STEP 4 === then "
    "=== RECONSTRUCTED MEMORY === markers. Output ONLY the five markers with content "
    "after each. No preamble. No explanations. No meta-commentary."
)

EMPTY_MARKERS = (
    "=== STEP 1 ===\n\n"
    "=== STEP 2 ===\n\n"
    "=== STEP 3 ===\n\n"
    "=== STEP 4 ===\n\n"
    "=== RECONSTRUCTED MEMORY ===\n"
)

_local_bundle: Any = None


def hf_token() -> Optional[str]:
    return os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")


def resolved_model_name() -> str:
    return os.environ.get("FUZZ_SMART_ROBOT_MODEL", DEFAULT_MODEL)


def resolved_adapter_base() -> str:
    return os.environ.get("FUZZ_SMART_ROBOT_ADAPTER_BASE", ADAPTER_BASE_DEFAULT)


def adapter_path() -> Optional[Path]:
    raw = os.environ.get("FUZZ_SMART_ROBOT_ADAPTER", "").strip()
    if not raw:
        return None
    path = Path(raw)
    return path if path.exists() else None


def build_smart_robot_messages(prompt: str) -> list[dict[str, str]]:
    """Play-identical chat turns: format system prompt + locked user prompt."""
    return [
        {"role": "system", "content": FORMAT_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]


def extract_chat_content(result: Any) -> str:
    """Return message content, or "" if choices/content are missing.

    A missing field must not become str(result). That dump is non-empty, so callers
    would treat a response object as Smart Robot text.
    """
    if isinstance(result, str):
        return result
    content = None
    choices = getattr(result, "choices", None)
    if choices and len(choices) > 0:
        first_choice = choices[0]
        message = getattr(first_choice, "message", None)
        if message is not None:
            content = getattr(message, "content", None)
            if content is None and isinstance(message, dict):
                content = message.get("content")
    if content is None and isinstance(result, dict):
        dict_choices = result.get("choices") or []
        if dict_choices:
            message = dict_choices[0].get("message") or {}
            content = message.get("content")
    if content is None:
        return ""
    return str(content)


def use_huggingface() -> bool:
    backend = os.environ.get("FUZZ_SMART_ROBOT_BACKEND", "").strip().lower()
    if backend == "local":
        return False
    if backend == "hf":
        return True
    return bool(hf_token() or os.environ.get("FUZZ_HF_ENDPOINT_URL"))


def call_huggingface(prompt: str) -> str:
    """One Smart Robot chat_completion on Hugging Face. Raises if client/token missing.

    Empty text is returned as "" so callers can persist raw_output, then fail.
    Uses play-identical system + user messages.
    """
    try:
        from huggingface_hub import InferenceClient
    except Exception as exc:
        raise RuntimeError("huggingface_hub is not installed") from exc
    token = hf_token()
    if not token and not os.environ.get("FUZZ_HF_ENDPOINT_URL"):
        raise RuntimeError("HF_TOKEN is not set")
    model = resolved_model_name()
    endpoint = os.environ.get("FUZZ_HF_ENDPOINT_URL")
    use_model = endpoint or model
    timeout_s = float(os.environ.get("FUZZ_SMART_ROBOT_TIMEOUT_S", "25"))
    client = InferenceClient(model=use_model, token=token, timeout=timeout_s)
    messages = build_smart_robot_messages(prompt)
    try:
        result = client.chat.completions.create(
            model=use_model,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return str(extract_chat_content(result))
    except (AttributeError, TypeError):
        logger.info("Falling back to client.chat_completion (older huggingface_hub version).")
        result = client.chat_completion(
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return str(extract_chat_content(result))


def _load_local_bundle() -> tuple[Any, Any]:
    global _local_bundle
    if _local_bundle is not None:
        return _local_bundle
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as exc:
        raise RuntimeError(
            "Local Smart Robot path needs transformers and torch. "
            "Install train/requirements.txt or set HF_TOKEN for the Hugging Face path."
        ) from exc

    base = resolved_adapter_base()
    adapter = adapter_path()
    tokenizer = AutoTokenizer.from_pretrained(base, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(base, trust_remote_code=True)
    if adapter is not None:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, str(adapter))
    model.eval()
    if hasattr(torch, "set_grad_enabled"):
        torch.set_grad_enabled(False)
    _local_bundle = (tokenizer, model)
    logger.info(
        "Loaded local Smart Robot base=%s adapter=%s",
        base,
        str(adapter) if adapter else "none",
    )
    return _local_bundle


def call_local_adapter(prompt: str) -> str:
    """CPU/GPU local generate with optional LoRA adapter. Play-identical chat template."""
    import torch

    tokenizer, model = _load_local_bundle()
    messages = build_smart_robot_messages(prompt)
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt")
    if hasattr(model, "device"):
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
    max_new = int(os.environ.get("FUZZ_SMART_ROBOT_MAX_NEW_TOKENS", str(MAX_TOKENS)))
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new,
            temperature=TEMPERATURE,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )
    prompt_len = inputs["input_ids"].shape[1]
    decoded = tokenizer.decode(output_ids[0][prompt_len:], skip_special_tokens=True)
    return decoded.strip()


def empty_markers() -> str:
    return EMPTY_MARKERS


def sample_reconstruction_text() -> str:
    here = Path(__file__).resolve().parent
    sample_path = here.parent.parent / "prompts" / "sample-reconstruction-01.md"
    return sample_path.read_text(encoding="utf-8")


def call_play_smart_robot(prompt: str) -> str:
    """Play helper default: HF when configured, else local adapter, else empty markers.

    Hugging Face failures return empty markers so the box can run buildProgressiveStep
    on the actual fight-end data. Play must never return sample-reconstruction-01.md
    (the oak-tree validation sample) as a successful Reconstructed Memory.
    """
    if use_huggingface():
        try:
            return call_huggingface(prompt)
        except Exception as exc:
            logger.warning(
                "Smart Robot one-call failed (%s: %s). Empty markers for box fallback.",
                type(exc).__name__,
                exc,
            )
            return empty_markers()
    if adapter_path() is not None or os.environ.get("FUZZ_SMART_ROBOT_BACKEND", "").lower() == "local":
        try:
            return call_local_adapter(prompt)
        except Exception as exc:
            logger.warning(
                "Local Smart Robot failed (%s: %s). Empty markers for box fallback.",
                type(exc).__name__,
                exc,
            )
            return empty_markers()
    return empty_markers()
