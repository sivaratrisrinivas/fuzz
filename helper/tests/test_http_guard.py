"""Body cap, XFF rate-limit key, idle-IP cleanup, HF-fail empty markers, Vercel reconstruct."""

from __future__ import annotations

import http.client
import importlib.util
import json
import os
import sys
import threading
import unittest
from collections import deque
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

HELPER_SRC = Path(__file__).resolve().parent.parent / "src"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(HELPER_SRC) not in sys.path:
    sys.path.insert(0, str(HELPER_SRC))


def _load_vercel_reconstruct():
    path = REPO_ROOT / "api" / "reconstruct.py"
    spec = importlib.util.spec_from_file_location("vercel_reconstruct", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestParseContentLength(unittest.TestCase):
    def test_requires_integer_and_rejects_oversize(self):
        from thin_helper.contract import ContractError
        from thin_helper.http_guard import MAX_BODY_BYTES, parse_content_length

        self.assertEqual(parse_content_length("12"), 12)
        with self.assertRaises(ContractError) as missing:
            parse_content_length(None)
        self.assertEqual(missing.exception.code, "invalid_content_length")
        with self.assertRaises(ContractError) as bad:
            parse_content_length("nope")
        self.assertEqual(bad.exception.code, "invalid_content_length")
        with self.assertRaises(ContractError) as huge:
            parse_content_length(str(MAX_BODY_BYTES + 1))
        self.assertEqual(huge.exception.code, "payload_too_large")


class TestClientIpFromHeaders(unittest.TestCase):
    def test_xff_uses_rightmost_hop_not_spoofed_leftmost(self):
        from thin_helper.http_guard import client_ip_from_headers

        self.assertEqual(
            client_ip_from_headers({"X-Forwarded-For": "1.1.1.1, 2.2.2.2, 10.0.0.1"}),
            "10.0.0.1",
        )
        self.assertEqual(
            client_ip_from_headers({"x-forwarded-for": "8.8.8.8"}),
            "8.8.8.8",
        )

    def test_prefers_real_ip_and_vercel_forwarded_for(self):
        from thin_helper.http_guard import client_ip_from_headers

        self.assertEqual(
            client_ip_from_headers(
                {
                    "X-Forwarded-For": "1.1.1.1, 9.9.9.9",
                    "X-Real-IP": "4.4.4.4",
                }
            ),
            "4.4.4.4",
        )
        self.assertEqual(
            client_ip_from_headers({"x-vercel-forwarded-for": "5.5.5.5, 6.6.6.6"}),
            "6.6.6.6",
        )


class TestRateLimitCleanupAndVercelDefault(unittest.TestCase):
    def setUp(self):
        from thin_helper import http_guard as guard

        self.guard = guard
        self.guard._hits.clear()
        self._old_limit = os.environ.get("FUZZ_RATE_LIMIT_PER_MINUTE")
        self._old_vercel = os.environ.get("VERCEL")

    def tearDown(self):
        self.guard._hits.clear()
        if self._old_limit is None:
            os.environ.pop("FUZZ_RATE_LIMIT_PER_MINUTE", None)
        else:
            os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = self._old_limit
        if self._old_vercel is None:
            os.environ.pop("VERCEL", None)
        else:
            os.environ["VERCEL"] = self._old_vercel

    def test_empty_deque_idle_ips_are_dropped(self):
        self.guard._hits["stale"] = deque()
        with patch("thin_helper.http_guard.time.monotonic", return_value=1.0):
            self.assertIsNone(self.guard.check_rate_limit("fresh"))
        self.assertNotIn("stale", self.guard._hits)
        self.assertIn("fresh", self.guard._hits)

    def test_expired_window_drops_then_restarts_bucket(self):
        os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = "1"
        with patch("thin_helper.http_guard.time.monotonic", return_value=0.0):
            self.assertIsNone(self.guard.check_rate_limit("1.1.1.1"))
            self.assertIsNotNone(self.guard.check_rate_limit("1.1.1.1"))
        with patch("thin_helper.http_guard.time.monotonic", return_value=61.0):
            self.assertIsNone(self.guard.check_rate_limit("1.1.1.1"))
        self.assertEqual(len(self.guard._hits["1.1.1.1"]), 1)

    def test_tracked_ips_capped(self):
        old_max = self.guard.MAX_TRACKED_IPS
        self.guard.MAX_TRACKED_IPS = 3
        try:
            with patch("thin_helper.http_guard.time.monotonic", return_value=10.0):
                for i in range(6):
                    self.guard.check_rate_limit(f"ip-{i}")
            self.assertLessEqual(len(self.guard._hits), 3)
        finally:
            self.guard.MAX_TRACKED_IPS = old_max

    def test_vercel_default_rate_limit_is_12_else_30(self):
        os.environ.pop("FUZZ_RATE_LIMIT_PER_MINUTE", None)
        os.environ["VERCEL"] = "1"
        self.assertEqual(self.guard.rate_limit_per_minute(), 12)
        os.environ.pop("VERCEL", None)
        self.assertEqual(self.guard.rate_limit_per_minute(), 30)


class TestHfFailureEmptyMarkers(unittest.TestCase):
    def test_play_hf_failure_returns_empty_markers_not_oak_tree_sample(self):
        from thin_helper.smart_robot import (
            call_play_smart_robot,
            empty_markers,
            sample_reconstruction_text,
        )

        with patch("thin_helper.smart_robot.use_huggingface", return_value=True), patch(
            "thin_helper.smart_robot.call_huggingface",
            side_effect=OSError("hf down"),
        ):
            text = call_play_smart_robot("locked prompt")
        self.assertEqual(text, empty_markers())
        sample = sample_reconstruction_text()
        self.assertNotEqual(text.strip(), sample.strip())
        self.assertNotIn("ancient oak", text.lower())
        self.assertIn("ancient oak", sample.lower())

    def test_timeout_default_is_at_most_25s(self):
        from thin_helper.smart_robot import call_huggingface

        captured = {}

        class FakeClient:
            def __init__(self, model, token=None, timeout=None, **kwargs):
                captured["timeout"] = timeout
                self.chat = self
                self.completions = self

            def create(self, **kwargs):
                raise RuntimeError("no network")

        old_timeout = os.environ.get("FUZZ_SMART_ROBOT_TIMEOUT_S")
        old_token = os.environ.get("HF_TOKEN")
        os.environ.pop("FUZZ_SMART_ROBOT_TIMEOUT_S", None)
        os.environ["HF_TOKEN"] = "test-token"
        try:
            with patch("huggingface_hub.InferenceClient", FakeClient):
                with self.assertRaises(RuntimeError):
                    call_huggingface("prompt")
            self.assertLessEqual(float(captured["timeout"]), 25)
        finally:
            if old_timeout is None:
                os.environ.pop("FUZZ_SMART_ROBOT_TIMEOUT_S", None)
            else:
                os.environ["FUZZ_SMART_ROBOT_TIMEOUT_S"] = old_timeout
            if old_token is None:
                os.environ.pop("HF_TOKEN", None)
            else:
                os.environ["HF_TOKEN"] = old_token


class TestFastApiBodyCap(unittest.TestCase):
    def setUp(self):
        os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = "1000"
        from fastapi.testclient import TestClient
        from thin_helper.main import app

        self.client = TestClient(app)

    def test_oversized_body_is_400_payload_too_large(self):
        from thin_helper.http_guard import MAX_BODY_BYTES

        r = self.client.post(
            "/reconstruct",
            content=b"x" * (MAX_BODY_BYTES + 8),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["code"], "payload_too_large")


class TestVercelReconstructPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_vercel_reconstruct()

    def setUp(self):
        from thin_helper import http_guard as guard

        self.guard = guard
        self.guard._hits.clear()
        self._old_limit = os.environ.get("FUZZ_RATE_LIMIT_PER_MINUTE")
        os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = "1000"

    def tearDown(self):
        self.guard._hits.clear()
        if self._old_limit is None:
            os.environ.pop("FUZZ_RATE_LIMIT_PER_MINUTE", None)
        else:
            os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = self._old_limit

    def _post(self, body: bytes, headers: dict | None = None, content_length: int | str | None = None):
        httpd = HTTPServer(("127.0.0.1", 0), self.mod.handler)
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.handle_request, daemon=True)
        thread.start()
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=8)
        out = {"Content-Type": "application/json"}
        if headers:
            out.update(headers)
        if content_length is None:
            out["Content-Length"] = str(len(body))
        else:
            out["Content-Length"] = str(content_length)
        try:
            conn.request("POST", "/reconstruct", body=body, headers=out)
            resp = conn.getresponse()
            raw = resp.read()
            status = resp.status
            resp_headers = {k.lower(): v for k, v in resp.getheaders()}
        finally:
            conn.close()
            thread.join(timeout=8)
            httpd.server_close()
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            payload = {"_raw": raw.decode("utf-8", errors="replace")}
        return status, payload, resp_headers

    def test_invalid_and_oversized_content_length_are_400_before_sanitize(self):
        from thin_helper.http_guard import MAX_BODY_BYTES

        sneaky = json.dumps(
            {"final_fuzz": "x", "fresh_clues": [], "original_memory": "The old oak tree"}
        ).encode("utf-8")
        status, body, _ = self._post(sneaky, content_length=MAX_BODY_BYTES + 1)
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "payload_too_large")
        self.assertNotEqual(body.get("code"), "memory_rejected")

        status, body, _ = self._post(b'{"final_fuzz":"x","fresh_clues":[]}', content_length="nope")
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "invalid_content_length")

    def test_hard_rate_limit_uses_rightmost_xff_and_retry_after(self):
        os.environ["FUZZ_RATE_LIMIT_PER_MINUTE"] = "1"
        payload = b'{"final_fuzz":"abc","fresh_clues":[]}'
        first, first_body, _ = self._post(
            payload,
            headers={"X-Forwarded-For": "8.8.8.8, 10.0.0.9"},
        )
        self.assertEqual(first, 200, first_body)
        second, second_body, second_headers = self._post(
            payload,
            headers={"X-Forwarded-For": "1.2.3.4, 10.0.0.9"},
        )
        self.assertEqual(second, 429, second_body)
        self.assertEqual(second_body["code"], "rate_limited")
        self.assertIn("retry-after", second_headers)
        spoofed_left, spoofed_body, _ = self._post(
            payload,
            headers={"X-Forwarded-For": "10.0.0.9, 8.8.8.8"},
        )
        self.assertEqual(spoofed_left, 200, spoofed_body)


if __name__ == "__main__":
    unittest.main()
