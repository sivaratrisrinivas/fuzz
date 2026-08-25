"""GS-T6 adversarial-review fixes: missing chat content and persist-then-fail."""

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HELPER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = HELPER_ROOT.parent
HARNESS = _load_module(
    "validate_smart_robot_on_dev",
    HELPER_ROOT / "scripts" / "validate-smart-robot-on-dev.py",
)
BENCH = _load_module(
    "gs_t6_reconstruction_accuracy",
    REPO_ROOT / "bench" / "gs_t6_reconstruction_accuracy.py",
)


class TestExtractChatContentMissing(unittest.TestCase):
    def test_returns_content_from_object_and_dict(self):
        class Message:
            content = "hello"

        class Choice:
            message = Message()

        class Result:
            choices = [Choice()]

        self.assertEqual(HARNESS.extract_chat_content(Result()), "hello")
        self.assertEqual(
            HARNESS.extract_chat_content({"choices": [{"message": {"content": "dict"}}]}),
            "dict",
        )
        self.assertEqual(HARNESS.extract_chat_content("plain"), "plain")

    def test_empty_choices_or_missing_content_returns_empty_string(self):
        class EmptyChoices:
            choices = []

        class MessageNone:
            content = None

        class ChoiceNone:
            message = MessageNone()

        class ResultNone:
            choices = [ChoiceNone()]

        self.assertEqual(HARNESS.extract_chat_content(EmptyChoices()), "")
        self.assertEqual(HARNESS.extract_chat_content(ResultNone()), "")
        self.assertEqual(HARNESS.extract_chat_content({"choices": []}), "")
        self.assertEqual(
            HARNESS.extract_chat_content({"choices": [{"message": {"content": None}}]}),
            "",
        )
        self.assertEqual(HARNESS.extract_chat_content({"choices": [{"message": {}}]}), "")
        dumped = HARNESS.extract_chat_content({"id": "cmpl", "choices": []})
        self.assertEqual(dumped, "")
        self.assertNotIn("cmpl", dumped)


class TestRunTrialPersistsRawThenFails(unittest.TestCase):
    def test_empty_reply_is_stored_then_marked_failed(self):
        with patch.object(
            BENCH,
            "dissolve_with_product_simulator",
            return_value={"final_fuzz": "abc", "replaced_chars": 1, "fuzz_simulator_level": 0.5},
        ):
            trial = BENCH.run_trial(
                memory_id="night-bus",
                original="abc",
                fuzz_level=0.5,
                seed=42,
                build_prompt=lambda fuzz, clues: "prompt",
                call_smart_robot=lambda prompt: "",
                parse_reconstruction=lambda raw: {"reconstructed_memory": "should not parse"},
            )
        self.assertEqual(trial["raw_output"], "")
        self.assertEqual(trial["status"], "failed")
        self.assertIn("empty text", trial["error"])
        self.assertIsNone(trial["word_f1"])

    def test_hf_call_smart_robot_returns_empty_instead_of_raising(self):
        class FakeChatCompletions:
            def create(self, *, model, messages, max_tokens, temperature):
                return {"choices": [{"message": {"content": None}}]}

        class FakeChat:
            completions = FakeChatCompletions()

        class FakeInferenceClient:
            def __init__(self, model, token):
                self.chat = FakeChat()

        with patch.object(HARNESS, "InferenceClient", FakeInferenceClient), patch.dict(
            "os.environ", {"HF_TOKEN": "test-token"}, clear=False
        ):
            text = HARNESS.call_smart_robot("locked prompt")
        self.assertEqual(text, "")

        with patch.object(
            BENCH,
            "dissolve_with_product_simulator",
            return_value={"final_fuzz": "abc", "replaced_chars": 1, "fuzz_simulator_level": 0.5},
        ), patch.object(HARNESS, "InferenceClient", FakeInferenceClient), patch.dict(
            "os.environ", {"HF_TOKEN": "test-token"}, clear=False
        ):
            trial = BENCH.run_trial(
                memory_id="night-bus",
                original="abc",
                fuzz_level=0.5,
                seed=42,
                build_prompt=lambda fuzz, clues: "prompt",
                call_smart_robot=HARNESS.call_smart_robot,
                parse_reconstruction=lambda raw: {"reconstructed_memory": "should not parse"},
            )
        self.assertEqual(trial["raw_output"], "")
        self.assertEqual(trial["status"], "failed")
        self.assertIn("empty text", trial["error"])
        self.assertIsNone(trial["word_f1"])

    def test_parse_empty_keeps_returned_raw(self):
        raw = "=== STEP 1 ===\n\n=== RECONSTRUCTED MEMORY ===\n"
        with patch.object(
            BENCH,
            "dissolve_with_product_simulator",
            return_value={"final_fuzz": "abc", "replaced_chars": 1, "fuzz_simulator_level": 0.5},
        ):
            trial = BENCH.run_trial(
                memory_id="night-bus",
                original="abc",
                fuzz_level=0.5,
                seed=42,
                build_prompt=lambda fuzz, clues: "prompt",
                call_smart_robot=lambda prompt: raw,
                parse_reconstruction=lambda text: {"reconstructed_memory": ""},
            )
        self.assertEqual(trial["raw_output"], raw)
        self.assertEqual(trial["status"], "failed")
        self.assertIn("parsed reconstructed_memory was empty", trial["error"])


if __name__ == "__main__":
    unittest.main()
