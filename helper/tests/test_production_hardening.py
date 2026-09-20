"""GS-T32 production guards: no Memory fields, rate limits, structured errors, health."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

HELPER_SRC = Path(__file__).resolve().parent.parent / "src"
if str(HELPER_SRC) not in sys.path:
    sys.path.insert(0, str(HELPER_SRC))


class TestProductionHardening(unittest.TestCase):
    def setUp(self):
        os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = "1000"
        from fastapi.testclient import TestClient
        from thin_helper.main import app

        self.client = TestClient(app)

    def test_health_reports_model_family_and_never_accepts_memory(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn("Qwen2.5", body["default_model_family"])
        self.assertFalse(body["accepts_memory"])
        self.assertTrue(body["ephemeral"])
        self.assertIn("4 Cleaning Steps", str(self.client.get("/").json()))

    def test_reconstruct_rejects_original_memory_fields(self):
        r = self.client.post(
            "/reconstruct",
            json={
                "final_fuzz": "The o** o*k",
                "fresh_clues": [],
                "original_memory": "The old oak tree by the river",
            },
        )
        self.assertEqual(r.status_code, 400)
        body = r.json()
        self.assertEqual(body["code"], "memory_rejected")
        self.assertIn("request_id", body)
        self.assertNotIn("The old oak tree by the river", str(body))

    def test_reconstruct_accepts_contract_only_and_returns_structured_result(self):
        r = self.client.post(
            "/reconstruct",
            json={"final_fuzz": "The o** o*k t**e", "fresh_clues": []},
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("reconstructed_memory", body)
        self.assertIn("steps", body)
        self.assertIn("request_id", body)
        self.assertNotIn("original_memory", body)

    def test_rate_limit_returns_structured_429(self):
        os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = "1"
        import importlib
        import thin_helper.http_guard as guard
        import thin_helper.main as main_mod

        importlib.reload(guard)
        importlib.reload(main_mod)
        from fastapi.testclient import TestClient

        client = TestClient(main_mod.app)
        payload = {"final_fuzz": "abc", "fresh_clues": []}
        first = client.post("/reconstruct", json=payload)
        self.assertEqual(first.status_code, 200)
        second = client.post("/reconstruct", json=payload)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(second.json()["code"], "rate_limited")
        self.assertIn("Retry-After", second.headers)
        os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = "1000"
        importlib.reload(guard)
        importlib.reload(main_mod)


class TestPlayIdenticalChat(unittest.TestCase):
    def test_build_smart_robot_messages_matches_play_format_system_prompt(self):
        from thin_helper.smart_robot import FORMAT_SYSTEM_PROMPT, build_smart_robot_messages

        messages = build_smart_robot_messages("locked prompt")
        self.assertEqual(
            messages,
            [
                {"role": "system", "content": FORMAT_SYSTEM_PROMPT},
                {"role": "user", "content": "locked prompt"},
            ],
        )
        self.assertIn("=== STEP 1 ===", FORMAT_SYSTEM_PROMPT)
        self.assertIn("=== RECONSTRUCTED MEMORY ===", FORMAT_SYSTEM_PROMPT)

    def test_validate_script_and_coordinator_share_the_same_messages(self):
        import importlib.util
        from pathlib import Path as P

        from thin_helper.smart_robot import build_smart_robot_messages

        path = P(__file__).resolve().parent.parent / "scripts" / "validate-smart-robot-on-dev.py"
        spec = importlib.util.spec_from_file_location("validate_smart_robot_on_dev", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(
            mod.build_smart_robot_messages("x"),
            build_smart_robot_messages("x"),
        )


if __name__ == "__main__":
    unittest.main()
