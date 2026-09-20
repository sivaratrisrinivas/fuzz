# Reconstructing adapter artifacts

Default path: `train/artifacts/qwen25-0.5b-reconstruct-lora`

Produced by `python3 train/train_lora.py` on `Qwen/Qwen2.5-0.5B-Instruct` (CPU LoRA).
Play still defaults to `Qwen/Qwen2.5-7B-Instruct` on Hugging Face. Point the helper at this
adapter with:

```
FUZZ_SMART_ROBOT_BACKEND=local
FUZZ_SMART_ROBOT_ADAPTER_BASE=Qwen/Qwen2.5-0.5B-Instruct
FUZZ_SMART_ROBOT_ADAPTER=train/artifacts/qwen25-0.5b-reconstruct-lora
```

If this directory has no `adapter_config.json`, run `python3 train/download_adapter.py`
(prints the train commands unless `FUZZ_SMART_ROBOT_ADAPTER_REPO` is set).
