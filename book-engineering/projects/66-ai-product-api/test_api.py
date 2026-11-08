"""Contract tests for the synthetic FastAPI service; no socket or model is used."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import FIXTURE, app

client = TestClient(app)
ROOT = Path(__file__).resolve().parent


class ApiContractTests(unittest.TestCase):
    def assert_problem(self, response, status: int) -> dict:
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.headers["content-type"], "application/problem+json")
        body = response.json()
        self.assertEqual(body["status"], status)
        self.assertTrue(body["type"].startswith("https://example.invalid/problems/"))
        self.assertTrue(body["title"])
        self.assertTrue(body["detail"])
        return body

    def test_catalog_list_matches_synthetic_fixture(self) -> None:
        response = client.get("/v1/catalog")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["contract_version"], "1.0")
        self.assertIsNone(body["next_cursor"])
        self.assertEqual(len(body["items"]), 1)
        self.assertEqual(body["items"][0]["id"], FIXTURE["records"][0]["id"])
        self.assertNotIn("answer_fa", body["items"][0])
        self.assertNotIn("answer_en", body["items"][0])

    def test_catalog_query_limit_is_bounded(self) -> None:
        response = client.get("/v1/catalog?limit=0")
        self.assert_problem(response, 422)

    def test_get_catalog_item_returns_only_public_fields(self) -> None:
        record = FIXTURE["records"][0]
        response = client.get(f"/v1/catalog/items/{record['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {key: record[key] for key in ("id", "title", "url")})

    def test_unknown_catalog_item_is_problem_details(self) -> None:
        body = self.assert_problem(client.get("/v1/catalog/items/not-in-fixture"), 404)
        self.assertEqual(body["type"], "https://example.invalid/problems/not-found")

    def test_assist_persian_response_obeys_schema(self) -> None:
        response = client.post("/v1/assist", json={"question": "سلام", "locale": "fa"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body), {"contract_version", "request_id", "status", "answer", "sources"})
        self.assertEqual(body["contract_version"], "1.0")
        self.assertEqual(body["status"], "completed")
        self.assertEqual(body["answer"], FIXTURE["records"][0]["answer_fa"])
        self.assertEqual(body["sources"][0]["id"], FIXTURE["records"][0]["id"])
        self.assertNotIn("سلام", body["answer"])

    def test_assist_english_response_uses_same_contract(self) -> None:
        response = client.post("/v1/assist", json={"question": "hello", "locale": "en"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["answer"], FIXTURE["records"][0]["answer_en"])
        self.assertEqual(body["sources"][0]["id"], "guide-001")

    def test_whitespace_only_question_is_rejected(self) -> None:
        body = self.assert_problem(client.post("/v1/assist", json={"question": "   "}), 422)
        self.assertEqual(body["type"], "https://example.invalid/problems/empty-question")

    def test_unknown_request_field_is_rejected_without_echo(self) -> None:
        sentinel = "DO_NOT_ECHO_PRIVATE_SENTINEL"
        body = self.assert_problem(
            client.post("/v1/assist", json={"question": "سلام", "private_note": sentinel}),
            422,
        )
        self.assertNotIn(sentinel, json.dumps(body, ensure_ascii=False))

    def test_question_longer_than_contract_limit_is_rejected(self) -> None:
        self.assert_problem(client.post("/v1/assist", json={"question": "x" * 301}), 422)

    def test_unsupported_locale_is_rejected(self) -> None:
        self.assert_problem(client.post("/v1/assist", json={"question": "hello", "locale": "ar"}), 422)

    def test_openapi_documents_paths_bounds_and_problem_media_type(self) -> None:
        response = client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        spec = response.json()
        self.assertEqual(spec["openapi"], "3.1.0")
        self.assertIn("post", spec["paths"]["/v1/assist"])
        request_schema = spec["components"]["schemas"]["AssistRequest"]
        self.assertEqual(request_schema["properties"]["question"]["maxLength"], 300)
        self.assertFalse(request_schema["additionalProperties"])
        self.assertIn("application/problem+json", spec["paths"]["/v1/assist"]["post"]["responses"]["422"]["content"])

    def test_demo_is_local_persian_rtl_html_without_external_resources(self) -> None:
        response = client.get("/demo")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        text = response.text
        self.assertIn('<html lang="fa" dir="rtl">', text)
        self.assertIn('aria-live="polite"', text)
        self.assertNotIn("https://fonts.", text)
        self.assertNotIn("<script src=", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
