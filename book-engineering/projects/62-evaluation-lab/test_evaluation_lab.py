from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import evaluation_lab as lab


class EvaluationLabTests(unittest.TestCase):
    def test_fixture_schema_and_group_disjoint_splits(self) -> None:
        rows = lab.load_jsonl(lab.ROOT / "sample_evaluation.jsonl")
        counts = lab.validate_rows(rows)
        self.assertEqual(counts, {"test": 6, "train": 4, "validation": 2})

    def test_duplicate_case_id_is_rejected(self) -> None:
        rows = lab.load_jsonl(lab.ROOT / "sample_evaluation.jsonl")
        with self.assertRaisesRegex(ValueError, "duplicate case_id"):
            lab.validate_rows(rows + [dict(rows[0])])

    def test_group_leakage_across_splits_is_rejected(self) -> None:
        rows = lab.load_jsonl(lab.ROOT / "sample_evaluation.jsonl")
        changed = dict(rows[0], case_id="new-id", split="test")
        with self.assertRaisesRegex(ValueError, "crosses splits"):
            lab.validate_rows(rows + [changed])

    def test_accuracy_macro_f1_and_wilson_interval(self) -> None:
        metrics = lab.classification_metrics([1, 0, 1, 0], [1, 1, 1, 0])
        self.assertEqual(metrics["correct"], 3)
        self.assertEqual(metrics["n"], 4)
        self.assertAlmostEqual(metrics["accuracy"], 0.75)
        self.assertAlmostEqual(metrics["macro_f1"], 0.7333333333333334)
        self.assertLess(metrics["accuracy_wilson_95"][0], 0.75)
        self.assertGreater(metrics["accuracy_wilson_95"][1], 0.75)

    def test_paired_group_bootstrap_is_reproducible(self) -> None:
        rows = [row for row in lab.load_jsonl(lab.ROOT / "sample_evaluation.jsonl") if row["split"] == "test"]
        first = lab.paired_group_bootstrap(rows, repetitions=500, seed=19)
        second = lab.paired_group_bootstrap(rows, repetitions=500, seed=19)
        self.assertEqual(first, second)
        self.assertEqual(first["groups"], 3)
        self.assertAlmostEqual(first["observed_candidate_minus_baseline_accuracy"], 1 / 6)

    def test_overlap_screen_returns_review_flags_not_provenance(self) -> None:
        result = lab.screen_for_overlap(
            ["A benchmark question: is 2 plus 2 equal to 4?", "A different prompt about astronomy"],
            ["A benchmark question: is 2 plus 2 equal to 4?"],
        )
        self.assertTrue(result[0]["flagged_for_review"])
        self.assertEqual(result[0]["reason"], "normalized_exact_match")
        self.assertIn("does not establish", result[0]["interpretation"])
        self.assertFalse(result[1]["flagged_for_review"])

    def test_pairwise_agreement_reports_denominator(self) -> None:
        result = lab.pairwise_percent_agreement({"x": [1, 1, 0], "y": [0, 0, 0]})
        self.assertEqual(result["pair_comparisons"], 6)
        self.assertEqual(result["pair_agreements"], 4)
        self.assertAlmostEqual(result["percent_agreement"], 2 / 3)

    def test_bootstrap_needs_multiple_groups(self) -> None:
        row = {"group_id": "one", "reference": 1, "baseline": 1, "candidate": 1}
        with self.assertRaisesRegex(ValueError, "at least two groups"):
            lab.paired_group_bootstrap([row], repetitions=100)

    def test_fixture_run_is_json_serializable_and_limited(self) -> None:
        result = lab.run_fixture()
        encoded = json.dumps(result)
        self.assertIn("Synthetic", encoded)
        self.assertEqual(result["test_case_count"], 6)
        self.assertTrue(any("fabricated" in item for item in result["limitations"]))
        self.assertEqual(len(result["overlap_screen"]), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
