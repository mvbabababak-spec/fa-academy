from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request

from local_stub import create_server


class LocalStubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server("127.0.0.1", 0, "synthetic-release-r4")
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def request_json(self, path: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(self.base_url + path, data=data, method=method)
        if data is not None:
            request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_health_endpoint_reports_current_synthetic_release(self) -> None:
        status, body = self.request_json("/healthz")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["release_id"], "synthetic-release-r4")
        self.assertTrue(body["synthetic"])

    def test_version_endpoint_discloses_stub_not_model_execution(self) -> None:
        status, body = self.request_json("/version")
        self.assertEqual(status, 200)
        self.assertEqual(body["release_id"], "synthetic-release-r4")
        self.assertFalse(body["model_execution"])

    def test_predict_accepts_only_synthetic_sample_id(self) -> None:
        status, body = self.request_json("/predict", "POST", {"sample_id": "synthetic-001"})
        self.assertEqual(status, 200)
        self.assertEqual(body["prediction"], "synthetic-label-a")
        self.assertFalse(body["model_execution"])
        self.assertTrue(body["synthetic"])

    def test_predict_rejects_prompt_or_extra_fields(self) -> None:
        request = urllib.request.Request(
            self.base_url + "/predict",
            data=json.dumps({"sample_id": "synthetic-001", "prompt": "not accepted"}).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(error.exception.code, 400)
        body = json.loads(error.exception.read().decode("utf-8"))
        self.assertEqual(body["error"], "synthetic_sample_id_required")

    def test_unknown_route_returns_not_found(self) -> None:
        request = urllib.request.Request(self.base_url + "/admin")
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(error.exception.code, 404)

    def test_non_loopback_bind_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "loopback"):
            create_server("0.0.0.0", 0, "synthetic-release-r4")


if __name__ == "__main__":
    unittest.main()
