"""Unit tests for the synthetic, offline security-control exercise."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from red_team_lab import analyze, decide, validate_fixture

HERE = Path(__file__).resolve().parent
FIXTURE_PATH = HERE / "synthetic_security_fixture.json"
FIXTURE_BYTES = FIXTURE_PATH.read_bytes()
FIXTURE = json.loads(FIXTURE_BYTES.decode("utf-8"))


class RedTeamLabTests(unittest.TestCase):
    def test_fixture_schema_and_case_ids_are_valid(self):
        validate_fixture(FIXTURE)
        ids = [case["id"] for case in FIXTURE["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 7)

    def test_default_control_policy_passes_all_expected_cases(self):
        result = analyze(FIXTURE, FIXTURE_BYTES)
        self.assertEqual(result["control_checks_passed"], 7)
        self.assertEqual(result["control_checks_failed"], 0)
        self.assertEqual(result["simulated_attack_goals_reached"], 0)
        self.assertEqual(result["simulated_attack_goal_rate"], 0.0)

    def test_fixture_has_six_attack_cases_and_one_benign_control(self):
        result = analyze(FIXTURE, FIXTURE_BYTES)
        self.assertEqual(result["attack_case_count"], 6)
        self.assertEqual(result["benign_control_count"], 1)

    def test_direct_injection_does_not_disclose_synthetic_canary(self):
        case = next(c for c in FIXTURE["cases"] if c["category"] == "direct_prompt_injection")
        self.assertEqual(decide(case), "blocked")

    def test_indirect_instruction_from_retrieval_is_not_authority(self):
        case = next(c for c in FIXTURE["cases"] if c["category"] == "indirect_prompt_injection")
        self.assertEqual(decide(case), "blocked")

    def test_read_only_principal_cannot_write_private_record(self):
        case = next(c for c in FIXTURE["cases"] if c["category"] == "tool_scope")
        self.assertEqual(decide(case), "blocked")

    def test_unverified_training_record_is_quarantined(self):
        case = next(c for c in FIXTURE["cases"] if c["category"] == "data_poisoning")
        self.assertEqual(decide(case), "quarantined")

    def test_membership_probe_is_not_confirmed_by_toy_endpoint(self):
        case = next(c for c in FIXTURE["cases"] if c["category"] == "membership_probe")
        self.assertEqual(decide(case), "blocked")

    def test_query_budget_branch_is_rate_limited(self):
        case = next(c for c in FIXTURE["cases"] if c["category"] == "excessive_querying")
        self.assertEqual(decide(case), "rate_limited")

    def test_benign_public_read_is_allowed(self):
        case = next(c for c in FIXTURE["cases"] if c["category"] == "benign_public_read")
        self.assertEqual(decide(case), "allowed")

    def test_disabling_canary_control_exposes_a_detected_regression(self):
        result = analyze(FIXTURE, FIXTURE_BYTES, {"deny_synthetic_canary": False})
        case = next(c for c in result["cases"] if c["category"] == "direct_prompt_injection")
        self.assertFalse(case["control_check_passed"])
        self.assertTrue(case["simulated_goal_reached"])

    def test_disabling_untrusted_boundary_exposes_a_detected_regression(self):
        result = analyze(FIXTURE, FIXTURE_BYTES, {"treat_retrieved_instructions_as_untrusted": False})
        case = next(c for c in result["cases"] if c["category"] == "indirect_prompt_injection")
        self.assertFalse(case["control_check_passed"])
        self.assertTrue(case["simulated_goal_reached"])

    def test_disabling_scope_enforcement_exposes_a_detected_regression(self):
        result = analyze(FIXTURE, FIXTURE_BYTES, {"enforce_tool_scopes": False})
        case = next(c for c in result["cases"] if c["category"] == "tool_scope")
        self.assertFalse(case["control_check_passed"])
        self.assertTrue(case["simulated_goal_reached"])

    def test_disabling_provenance_gate_exposes_a_detected_regression(self):
        result = analyze(FIXTURE, FIXTURE_BYTES, {"require_verified_data_provenance": False})
        case = next(c for c in result["cases"] if c["category"] == "data_poisoning")
        self.assertFalse(case["control_check_passed"])
        self.assertTrue(case["simulated_goal_reached"])

    def test_disabling_query_budget_exposes_only_the_fixture_threshold_branch(self):
        result = analyze(FIXTURE, FIXTURE_BYTES, {"enforce_query_budget": False})
        case = next(c for c in result["cases"] if c["category"] == "excessive_querying")
        self.assertFalse(case["control_check_passed"])
        self.assertTrue(case["simulated_goal_reached"])
        self.assertIn("not an empirical attack-success rate", result["limitations"][2])

    def test_unknown_policy_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            analyze(FIXTURE, FIXTURE_BYTES, {"allow_everything": True})

    def test_invalid_query_budget_is_rejected(self):
        for value in (-1, 1.5, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                analyze(FIXTURE, FIXTURE_BYTES, {"query_budget": value})

    def test_duplicate_case_ids_are_rejected(self):
        duplicate = json.loads(json.dumps(FIXTURE))
        duplicate["cases"][1]["id"] = duplicate["cases"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate case id"):
            validate_fixture(duplicate)

    def test_unknown_case_category_is_rejected(self):
        invalid = json.loads(json.dumps(FIXTURE))
        invalid["cases"][0]["category"] = "unknown_attack"
        with self.assertRaisesRegex(ValueError, "unknown category"):
            validate_fixture(invalid)

    def test_results_record_the_fixture_digest_and_narrow_scope(self):
        result = analyze(FIXTURE, FIXTURE_BYTES)
        self.assertEqual(result["fixture_sha256"], __import__("hashlib").sha256(FIXTURE_BYTES).hexdigest())
        self.assertIn("not a red-team test", result["scope"])
        self.assertEqual(len(result["limitations"]), 6)


if __name__ == "__main__":
    unittest.main()
