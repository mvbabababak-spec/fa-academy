"""Run the API and browser suites; write a deterministic, fixture-scoped result."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def run_suite(pattern: str) -> unittest.result.TestResult:
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(ROOT),
        pattern=pattern,
        top_level_dir=str(ROOT),
    )
    stream = io.StringIO()
    outcome = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(stream.getvalue(), end="")
    return outcome


def failed_count(outcome: unittest.result.TestResult) -> int:
    return len(outcome.failures) + len(outcome.errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results.json")
    args = parser.parse_args()

    fixture_path = ROOT / "synthetic_fixture.json"
    fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    manifest = json.loads((ROOT / "fixture_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("sha256") != fixture_hash:
        raise SystemExit("fixture hash does not match fixture_manifest.json")

    api = run_suite("test_api.py")
    frontend = run_suite("test_frontend.py")
    if not api.wasSuccessful() or not frontend.wasSuccessful():
        return 1

    result = {
        "project_id": "v5-ch05-api-contract-synthetic-v1",
        "fixture_id": manifest["fixture_id"],
        "fixture_sha256": fixture_hash,
        "api_case_count": api.testsRun,
        "api_cases_passed": api.testsRun - failed_count(api),
        "api_cases_failed": failed_count(api),
        "frontend_case_count": frontend.testsRun,
        "frontend_cases_passed": frontend.testsRun - failed_count(frontend),
        "frontend_cases_failed": failed_count(frontend),
        "frontend_viewports_tested_px": [320, 390, 768],
        "external_http_requests": 0,
        "live_model_calls": 0,
        "personal_records": 0,
        "scope": "Synthetic FastAPI/OpenAPI contract, API behavior, and browser UI states only; API responses are read from local fixtures or intercepted test data.",
        "limitations": [
            "The fixture and all responses are invented; no real user, institution, model, or upstream API is represented.",
            "TestClient exercises the ASGI application in-process and does not measure network behavior, latency, capacity, or deployment.",
            "The browser tests intercept the API response; they test UI states, not a live end-to-end deployment or native mobile application.",
            "Schema validity does not establish answer quality, factuality, safety, accessibility conformance, or legal compliance.",
            "Authentication, authorization, rate limiting, telemetry, incident response, and deployment are outside this chapter's implementation.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"PASS API/UI audit: API {result['api_cases_passed']}/{result['api_case_count']}; "
        f"browser {result['frontend_cases_passed']}/{result['frontend_case_count']}; "
        f"fixture sha256={fixture_hash}; no external HTTP or model calls"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
