from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from deployment_gate import (
    DEFAULT_FIXTURE,
    canonical_bytes,
    evaluate_scenario,
    is_digest,
    run_fixture,
    sha256_digest,
)

PROJECT_DIR = Path(__file__).resolve().parent


def read_fixture() -> dict:
    return json.loads(DEFAULT_FIXTURE.read_text(encoding="utf-8"))


class ReleaseGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = read_fixture()
        self.current = copy.deepcopy(self.fixture["current_release"])
        self.policy = copy.deepcopy(self.fixture["policy"])
        self.scenario = copy.deepcopy(self.fixture["scenarios"][0])

    def evaluate(self, scenario: dict | None = None, current: dict | None = None, policy: dict | None = None) -> dict:
        return evaluate_scenario(
            scenario or copy.deepcopy(self.scenario),
            current or copy.deepcopy(self.current),
            policy or copy.deepcopy(self.policy),
        )

    def test_fixture_sha256_is_stable(self) -> None:
        first = hashlib.sha256(DEFAULT_FIXTURE.read_bytes()).hexdigest()
        second = hashlib.sha256(DEFAULT_FIXTURE.read_bytes()).hexdigest()
        self.assertEqual(first, second)
        self.assertEqual(first, "4b8824611574ac3ed631bdc81bc78037116afec70acee6942151c59f8ad3a57f")

    def test_canonical_json_has_stable_order_and_spacing(self) -> None:
        self.assertEqual(canonical_bytes({"b": 2, "a": 1}), b'{"a":1,"b":2}')

    def test_digest_format_accepts_sha256_hex(self) -> None:
        self.assertTrue(is_digest("sha256:" + "a" * 64))

    def test_digest_format_rejects_mutable_tag(self) -> None:
        self.assertFalse(is_digest("latest"))

    def test_digest_format_rejects_short_value(self) -> None:
        self.assertFalse(is_digest("sha256:abcd"))

    def test_healthy_rollout_promotes_all_stages(self) -> None:
        result = self.evaluate()
        self.assertEqual(result["decision"], "promoted")
        self.assertEqual(result["promoted_stages_percent"], [5, 25, 100])
        self.assertEqual(result["active_release_id"], "candidate-r4")
        self.assertTrue(result["simulated_only"])

    def test_fixture_latency_regression_rolls_back_to_previous_release(self) -> None:
        scenario = copy.deepcopy(self.fixture["scenarios"][1])
        result = self.evaluate(scenario)
        self.assertEqual(result["decision"], "rolled_back")
        self.assertEqual(result["failed_at_percent"], 25)
        self.assertEqual(result["active_release_id"], "stable-r3")
        self.assertEqual(result["promoted_stages_percent"], [5])
        self.assertTrue(result["rollback_performed"])

    def test_fixture_with_unverified_provenance_is_blocked(self) -> None:
        scenario = copy.deepcopy(self.fixture["scenarios"][2])
        result = self.evaluate(scenario)
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("provenance_not_verified", result["blocked_reasons"])
        self.assertEqual(result["active_release_id"], "stable-r3")

    def test_changed_component_without_rehash_is_blocked(self) -> None:
        self.scenario["candidate"]["components"]["service"]["revision"] = "tampered"
        result = self.evaluate()
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("candidate_digest_mismatch", result["blocked_reasons"])

    def test_provenance_subject_must_match_candidate_bundle(self) -> None:
        self.scenario["candidate"]["provenance"]["subject_digest"] = "sha256:" + "0" * 64
        result = self.evaluate()
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("provenance_subject_mismatch", result["blocked_reasons"])

    def test_mutable_bundle_tag_is_blocked(self) -> None:
        self.scenario["candidate"]["bundle_digest"] = "release-latest"
        self.scenario["candidate"]["provenance"]["subject_digest"] = "release-latest"
        result = self.evaluate()
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("candidate_digest_invalid", result["blocked_reasons"])

    def test_incomplete_component_set_is_blocked(self) -> None:
        del self.scenario["candidate"]["components"]["tokenizer"]
        result = self.evaluate()
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("candidate_components_incomplete", result["blocked_reasons"])

    def test_unit_test_failure_blocks_before_rollout(self) -> None:
        self.scenario["candidate"]["gates"]["unit_tests"] = "failed"
        result = self.evaluate()
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("gate_not_passed:unit_tests", result["blocked_reasons"])
        self.assertEqual(result["promoted_stages_percent"], [])

    def test_missing_model_evaluation_record_blocks(self) -> None:
        del self.scenario["candidate"]["gates"]["model_evaluation_record"]
        result = self.evaluate()
        self.assertIn("gate_not_passed:model_evaluation_record", result["blocked_reasons"])

    def test_security_scan_failure_blocks(self) -> None:
        self.scenario["candidate"]["gates"]["security_scan"] = "failed"
        result = self.evaluate()
        self.assertIn("gate_not_passed:security_scan", result["blocked_reasons"])

    def test_production_requires_approval(self) -> None:
        self.scenario["approval_status"] = "pending"
        result = self.evaluate()
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("production_approval_missing", result["blocked_reasons"])

    def test_staging_does_not_require_production_approval(self) -> None:
        self.scenario["target"] = "staging"
        self.scenario.pop("approval_status")
        result = self.evaluate()
        self.assertEqual(result["decision"], "promoted")

    def test_backward_compatibility_is_required_for_safe_rollback(self) -> None:
        self.scenario["candidate"]["backward_compatible"] = False
        result = self.evaluate()
        self.assertIn("rollback_compatibility_not_confirmed", result["blocked_reasons"])

    def test_reusing_current_release_id_is_blocked(self) -> None:
        self.scenario["candidate"]["release_id"] = self.current["release_id"]
        result = self.evaluate()
        self.assertIn("candidate_release_id_not_new", result["blocked_reasons"])

    def test_candidate_with_current_digest_is_blocked(self) -> None:
        self.scenario["candidate"]["components"] = copy.deepcopy(self.current["components"])
        self.scenario["candidate"]["bundle_digest"] = self.current["bundle_digest"]
        self.scenario["candidate"]["provenance"]["subject_digest"] = self.current["bundle_digest"]
        result = self.evaluate()
        self.assertIn("candidate_matches_current_release", result["blocked_reasons"])

    def test_invalid_previous_release_blocks_new_release(self) -> None:
        current = copy.deepcopy(self.current)
        current["bundle_digest"] = "latest"
        result = self.evaluate(current=current)
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("current_release_digest_invalid", result["blocked_reasons"])

    def test_insufficient_canary_sample_holds_without_promotion(self) -> None:
        self.scenario["observations"][0]["requests"] = 99
        result = self.evaluate()
        self.assertEqual(result["decision"], "hold")
        self.assertEqual(result["held_at_percent"], 5)
        self.assertEqual(result["promoted_stages_percent"], [])
        self.assertEqual(result["active_release_id"], "stable-r3")

    def test_error_rate_at_threshold_is_accepted(self) -> None:
        for observation in self.scenario["observations"]:
            observation["errors"] = int(observation["requests"] * self.policy["max_error_rate"])
        result = self.evaluate()
        self.assertEqual(result["decision"], "promoted")

    def test_error_rate_above_threshold_rolls_back(self) -> None:
        self.scenario["observations"][0]["errors"] = 21
        result = self.evaluate()
        self.assertEqual(result["decision"], "rolled_back")
        self.assertIn("canary_error_rate_over_limit", result["blocked_reasons"])

    def test_p95_at_threshold_is_accepted(self) -> None:
        for observation in self.scenario["observations"]:
            observation["p95_ms"] = self.policy["max_p95_ms"]
        result = self.evaluate()
        self.assertEqual(result["decision"], "promoted")

    def test_p95_over_threshold_rolls_back(self) -> None:
        self.scenario["observations"][0]["p95_ms"] = self.policy["max_p95_ms"] + 1
        result = self.evaluate()
        self.assertEqual(result["decision"], "rolled_back")
        self.assertIn("canary_p95_over_limit", result["blocked_reasons"])

    def test_observation_stages_must_match_policy(self) -> None:
        self.scenario["observations"][1]["traffic_percent"] = 20
        result = self.evaluate()
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("rollout_observations_do_not_match_policy", result["blocked_reasons"])

    def test_invalid_error_count_blocks(self) -> None:
        self.scenario["observations"][0]["errors"] = self.scenario["observations"][0]["requests"] + 1
        result = self.evaluate()
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("error_count_invalid", result["blocked_reasons"])

    def test_negative_latency_blocks(self) -> None:
        self.scenario["observations"][0]["p95_ms"] = -1
        result = self.evaluate()
        self.assertIn("p95_latency_invalid", result["blocked_reasons"])

    def test_missing_health_policy_blocks(self) -> None:
        del self.policy["max_p95_ms"]
        result = self.evaluate(policy=self.policy)
        self.assertEqual(result["decision"], "blocked")
        self.assertIn("health_policy_invalid", result["blocked_reasons"])

    def test_duplicate_scenario_names_are_rejected(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["scenarios"][1]["name"] = payload["scenarios"][0]["name"]
        with self.assertRaisesRegex(ValueError, "unique"):
            run_fixture(payload, "0" * 64)

    def test_empty_scenarios_are_rejected(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["scenarios"] = []
        with self.assertRaisesRegex(ValueError, "at least one"):
            run_fixture(payload, "0" * 64)

    def test_result_reports_no_external_or_production_activity(self) -> None:
        raw = DEFAULT_FIXTURE.read_bytes()
        result = run_fixture(json.loads(raw), hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["external_network_requests"], 0)
        self.assertEqual(result["cloud_deployments"], 0)
        self.assertEqual(result["production_writes"], 0)
        self.assertEqual(result["model_inference_calls"], 0)
        self.assertFalse(result["gpu_used"])
        self.assertEqual(result["personal_records"], 0)

    def test_cli_output_matches_committed_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "results.json"
            subprocess.run(
                [sys.executable, str(PROJECT_DIR / "deployment_gate.py"), "--fixture", str(DEFAULT_FIXTURE), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            expected = json.loads((PROJECT_DIR / "results.json").read_text(encoding="utf-8"))
            actual = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_cli_result_is_deterministic(self) -> None:
        raw = DEFAULT_FIXTURE.read_bytes()
        payload = json.loads(raw)
        first = run_fixture(payload, hashlib.sha256(raw).hexdigest())
        second = run_fixture(payload, hashlib.sha256(raw).hexdigest())
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
