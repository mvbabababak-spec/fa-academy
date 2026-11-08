"""Deterministic unit tests for the synthetic chapter 63 lab."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import model_behavior_lab as lab

ROOT = Path(__file__).resolve().parent
FIXTURE_PATH = ROOT / "synthetic_behavior_fixture.json"
FIXTURE_BYTES = FIXTURE_PATH.read_bytes()
FIXTURE = json.loads(FIXTURE_BYTES.decode("utf-8"))
RESULT = lab.analyze(FIXTURE, FIXTURE_BYTES)


class BehaviorLabTests(unittest.TestCase):
    def test_fixture_is_explicitly_synthetic_and_hashed(self):
        self.assertTrue(FIXTURE["synthetic"])
        self.assertEqual(RESULT["fixture_sha256"], hashlib.sha256(FIXTURE_BYTES).hexdigest())

    def test_claim_status_counts_and_resolved_denominator(self):
        audit = RESULT["claim_evidence_audit"]
        self.assertEqual(audit["counts_by_fixture_status"], {
            "contradicted": 2, "supported": 4, "unverified": 2
        })
        self.assertEqual(audit["resolved_count"], 6)
        self.assertAlmostEqual(audit["support_fraction_among_resolved"], 4 / 6)

    def test_unverified_claims_are_not_counted_as_contradictions(self):
        audit = RESULT["claim_evidence_audit"]
        self.assertEqual(audit["unverified_count_excluded_from_denominator"], 2)
        self.assertNotEqual(audit["support_fraction_among_resolved"], 4 / 8)

    def test_invalid_claim_status_is_rejected(self):
        data = copy.deepcopy(FIXTURE)
        data["claims"][0]["status"] = "probably-true"
        with self.assertRaisesRegex(ValueError, "evidence status"):
            lab.validate_fixture(data)

    def test_duplicate_ids_are_rejected(self):
        data = copy.deepcopy(FIXTURE)
        data["claims"][1]["id"] = data["claims"][0]["id"]
        with self.assertRaisesRegex(ValueError, "IDs must be unique"):
            lab.validate_fixture(data)

    def test_probabilities_must_be_finite_and_bounded(self):
        for value in (-0.01, 1.01, float("nan")):
            data = copy.deepcopy(FIXTURE)
            data["classification_cases"][0]["probability_positive"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                lab.validate_fixture(data)

    def test_group_confusion_counts_and_gaps(self):
        audit = RESULT["classification_audit"]
        self.assertEqual(audit["overall"]["confusion"], {"tp": 3, "tn": 5, "fp": 1, "fn": 3})
        self.assertAlmostEqual(audit["synthetic_group_slices"]["synthetic_cohort_a"]["accuracy"], 5 / 6)
        self.assertAlmostEqual(audit["synthetic_group_slices"]["synthetic_cohort_b"]["accuracy"], 3 / 6)
        self.assertAlmostEqual(audit["max_absolute_group_gap"]["accuracy"], 1 / 3)
        self.assertAlmostEqual(audit["max_absolute_group_gap"]["true_positive_rate"], 1 / 3)
        self.assertAlmostEqual(audit["max_absolute_group_gap"]["false_positive_rate"], 1 / 3)

    def test_brier_score_and_ece_are_descriptive(self):
        overall = RESULT["classification_audit"]["overall"]
        self.assertAlmostEqual(overall["brier_score"], 2.0377 / 12)
        self.assertGreaterEqual(overall["top_label_ece_equal_width_5_bins"], 0)
        self.assertLessEqual(overall["top_label_ece_equal_width_5_bins"], 1)
        self.assertEqual(sum(item["count"] for item in overall["calibration_bins"]), 12)
        self.assertIn("depends on binning", overall["calibration_note"])

    def test_group_slice_keeps_rates_undefined_when_denominator_is_zero(self):
        rows = [
            {"id": "n1", "group": "only-negative", "label": 0, "probability_positive": 0.1},
            {"id": "n2", "group": "only-negative", "label": 0, "probability_positive": 0.2},
        ]
        result = lab.audit_classification(rows)["synthetic_group_slices"]["only-negative"]
        self.assertIsNone(result["true_positive_rate"])
        self.assertEqual(result["false_positive_rate"], 0.0)

    def test_paired_robustness_summary_uses_only_declared_pairs(self):
        audit = RESULT["paired_robustness_audit"]
        self.assertEqual(audit["label_preserving_pair_count"], 6)
        self.assertAlmostEqual(audit["prediction_consistency"], 4 / 6)
        self.assertAlmostEqual(audit["baseline_accuracy_on_pairs"], 5 / 6)
        self.assertAlmostEqual(audit["variant_accuracy_on_pairs"], 3 / 6)
        self.assertAlmostEqual(audit["accuracy_difference_variant_minus_baseline"], -2 / 6)

    def test_pairs_not_declared_label_preserving_are_rejected(self):
        data = copy.deepcopy(FIXTURE)
        data["robustness_pairs"][0]["label_preserving"] = False
        with self.assertRaisesRegex(ValueError, "not declared label-preserving"):
            lab.validate_fixture(data)

    def test_toy_explanation_additivity_and_ablation_are_checked(self):
        audit = RESULT["toy_explanation_audit"]
        self.assertEqual(audit["case_count"], 4)
        self.assertLessEqual(audit["max_additivity_error"], 1e-12)
        self.assertLessEqual(audit["max_ablation_error"], 1e-12)
        self.assertEqual(audit["cases"][1]["largest_absolute_contribution"], "surface_proxy")

    def test_weight_and_feature_names_must_match(self):
        data = copy.deepcopy(FIXTURE)
        del data["explanation_cases"][0]["features"]["surface_proxy"]
        with self.assertRaisesRegex(ValueError, "names must match"):
            lab.validate_fixture(data)

    def test_nonsynthetic_input_is_rejected(self):
        data = copy.deepcopy(FIXTURE)
        data["synthetic"] = False
        with self.assertRaisesRegex(ValueError, "explicitly identify itself as synthetic"):
            lab.validate_fixture(data)

    def test_cli_writes_deterministic_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "result.json"
            command = [sys.executable, str(ROOT / "model_behavior_lab.py"), "--output", str(output)]
            first = subprocess.run(command, check=True, capture_output=True, text=True)
            first_bytes = output.read_bytes()
            second = subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertEqual(first.returncode, second.returncode)
            self.assertEqual(first_bytes, output.read_bytes())
            self.assertIn("Wrote synthetic behavior audit", first.stdout)
            self.assertEqual(json.loads(first_bytes), RESULT)


if __name__ == "__main__":
    unittest.main()
