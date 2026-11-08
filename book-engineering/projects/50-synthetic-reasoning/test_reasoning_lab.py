"""Tests for the narrow, offline synthetic reasoning fixture."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import torch

from reasoning_lab import (
    audit_records,
    curriculum_order,
    load_jsonl,
    run_demo,
    self_consistency_vote,
    soft_target_kl,
    split_by_group,
    validate_records,
)

FIXTURE = Path(__file__).with_name("sample_traces.jsonl")


class FixtureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.source_bytes = load_jsonl(FIXTURE)

    def test_fixture_has_twelve_rows_and_six_groups(self):
        self.assertEqual(len(self.rows), 12)
        self.assertEqual(len({row["group_id"] for row in self.rows}), 6)

    def test_fixture_validates_exact_addition(self):
        self.assertEqual(validate_records(self.rows), [])

    def test_incorrect_trace_is_rejected(self):
        rows = [dict(row) for row in self.rows]
        rows[0]["teacher_trace"] = "2 + 3 = 6"
        self.assertTrue(any("does not match" in error for error in validate_records(rows)))

    def test_incorrect_answer_is_rejected(self):
        rows = [dict(row) for row in self.rows]
        rows[0]["answer"] = "999"
        self.assertTrue(any("does not match" in error for error in validate_records(rows)))

    def test_duplicate_ids_are_rejected(self):
        rows = [dict(row) for row in self.rows]
        rows[1]["id"] = rows[0]["id"]
        self.assertTrue(any("duplicate id" in error for error in validate_records(rows)))

    def test_non_fixture_label_source_is_rejected(self):
        rows = [dict(row) for row in self.rows]
        rows[0]["label_source"] = "human"
        self.assertTrue(any("label_source" in error for error in validate_records(rows)))

    def test_difficulty_must_match_the_documented_rule(self):
        rows = [dict(row) for row in self.rows]
        rows[0]["difficulty"] = "hard"
        self.assertTrue(any("difficulty should" in error for error in validate_records(rows)))

    def test_empty_fixture_is_rejected(self):
        self.assertEqual(validate_records([]), ["fixture has no records"])

    def test_invalid_jsonl_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.jsonl"
            path.write_text("{not json}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid JSON"):
                load_jsonl(path)


class SplitAndCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, _ = load_jsonl(FIXTURE)

    def test_group_split_is_repeatable(self):
        self.assertEqual(split_by_group(self.rows, 50), split_by_group(self.rows, 50))

    def test_no_group_crosses_splits(self):
        parts = split_by_group(self.rows, 50)
        group_sets = {name: {row["group_id"] for row in rows} for name, rows in parts.items()}
        self.assertFalse(group_sets["train"] & group_sets["validation"])
        self.assertFalse(group_sets["train"] & group_sets["test"])
        self.assertFalse(group_sets["validation"] & group_sets["test"])
        self.assertEqual(set.union(*group_sets.values()), {row["group_id"] for row in self.rows})

    def test_fixture_split_counts(self):
        parts = split_by_group(self.rows, 50)
        self.assertEqual({key: len(value) for key, value in parts.items()}, {"train": 8, "validation": 2, "test": 2})
        self.assertEqual({key: len({row["group_id"] for row in value}) for key, value in parts.items()}, {"train": 4, "validation": 1, "test": 1})

    def test_all_records_of_one_group_stay_together(self):
        parts = split_by_group(self.rows, 50)
        group_to_split = {row["group_id"]: name for name, subset in parts.items() for row in subset}
        for row in self.rows:
            self.assertIn(row, parts[group_to_split[row["group_id"]]])

    def test_curriculum_orders_easy_medium_hard(self):
        ordered = curriculum_order(self.rows)
        ranks = {"easy": 0, "medium": 1, "hard": 2}
        self.assertEqual([ranks[row["difficulty"]] for row in ordered], sorted(ranks[row["difficulty"]] for row in ordered))

    def test_curriculum_is_stable_by_id_within_bucket(self):
        ordered = curriculum_order(self.rows)
        for level in ("easy", "medium", "hard"):
            ids = [row["id"] for row in ordered if row["difficulty"] == level]
            self.assertEqual(ids, sorted(ids))

    def test_split_requires_three_groups(self):
        with self.assertRaisesRegex(ValueError, "three distinct groups"):
            split_by_group(self.rows[:2], 50)


class DistillationAndInferenceHelpersTests(unittest.TestCase):
    def test_equal_logits_have_zero_kl(self):
        logits = torch.tensor([[1.0, 2.0, -1.0], [0.0, 0.5, 2.0]])
        self.assertAlmostEqual(float(soft_target_kl(logits, logits, 2.0)), 0.0, places=6)

    def test_mismatched_logits_have_positive_kl(self):
        teacher = torch.tensor([[3.0, 0.0, -1.0], [0.0, 3.0, -1.0]])
        student = torch.zeros_like(teacher)
        self.assertGreater(float(soft_target_kl(student, teacher, 2.0)), 0.0)

    def test_distillation_loss_has_finite_student_gradient(self):
        student = torch.tensor([[0.1, 0.2, -0.1]], requires_grad=True)
        teacher = torch.tensor([[1.2, -0.2, 0.0]])
        soft_target_kl(student, teacher, 1.5).backward()
        self.assertTrue(torch.isfinite(student.grad).all())

    def test_distillation_loss_rejects_bad_temperature(self):
        logits = torch.zeros((1, 2))
        for value in (0.0, -1.0, float("inf"), float("nan")):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "temperature"):
                soft_target_kl(logits, logits, value)

    def test_distillation_loss_rejects_shape_mismatch(self):
        with self.assertRaisesRegex(ValueError, "same batch-by-class"):
            soft_target_kl(torch.zeros((2, 3)), torch.zeros((2, 4)), 1.0)

    def test_self_consistency_returns_majority(self):
        answer, counts = self_consistency_vote([" 42 ", "41", "42", "42", "43"])
        self.assertEqual(answer, "42")
        self.assertEqual(counts, {"41": 1, "42": 3, "43": 1})

    def test_self_consistency_tie_uses_first_candidate(self):
        self.assertEqual(self_consistency_vote(["B", "A"])[0], "B")

    def test_self_consistency_rejects_empty_or_blank_candidate(self):
        for candidates in ([], ["", "answer"], ["   "]):
            with self.subTest(candidates=candidates), self.assertRaisesRegex(ValueError, "candidate list"):
                self_consistency_vote(candidates)

    def test_audit_reports_no_training_and_exact_hash(self):
        rows, source_bytes = load_jsonl(FIXTURE)
        result = audit_records(rows, source_bytes, seed=50)
        import hashlib
        self.assertEqual(result["sha256"], hashlib.sha256(source_bytes).hexdigest())
        self.assertFalse(result["training_performed"])
        self.assertFalse(result["language_model_loaded"])
        self.assertEqual(result["status"], "synthetic_fixture_audit_complete")

    def test_demo_has_only_fixture_level_claims(self):
        rows, _ = load_jsonl(FIXTURE)
        result = run_demo(rows)
        self.assertEqual(result["vote_winner"], "125")
        self.assertEqual(result["candidate_budget"], 5)
        self.assertFalse(result["training_performed"])
        self.assertIn("not model sampling", result["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
