import json
from pathlib import Path
import tempfile
import unittest

from corpus_audit import (
    audit_files,
    audit_records,
    comparison_key,
    evaluation_overlap_candidates,
    load_corpus,
    load_evaluation,
    near_duplicate_pairs,
    quality_flags,
)


HERE = Path(__file__).resolve().parent


class CorpusAuditTests(unittest.TestCase):
    def setUp(self):
        self.corpus = load_corpus(HERE / "sample_corpus.jsonl")
        self.evaluation = load_evaluation(HERE / "sample_evaluation.jsonl")

    def test_sample_reports_exact_near_duplicate_and_evaluation_candidates(self):
        report, summary = audit_records(self.corpus, self.evaluation)
        exact_ids = {(row["left_id"], row["right_id"]) for row in report["exact_duplicate_candidates"]}
        near_ids = {(row["left_id"], row["right_id"]) for row in report["near_duplicate_candidates"]}
        eval_pairs = {(row["evaluation_id"], row["corpus_id"], row["match_type"]) for row in report["evaluation_overlap_candidates"]}
        self.assertIn(("doc-001", "doc-004"), exact_ids)
        self.assertIn(("doc-002", "doc-003"), near_ids)
        self.assertIn(("eval-001", "doc-009", "exact_surface_overlap_candidate"), eval_pairs)
        self.assertIn(("eval-002", "doc-010", "long_contiguous_overlap_candidate"), eval_pairs)
        self.assertEqual(summary["training_rows_exported"], 0)
        self.assertFalse(summary["automatic_training_approval"])

    def test_rights_states_are_flags_not_automatic_permission(self):
        report, summary = audit_records(self.corpus, self.evaluation)
        dispositions = {row["rights_disposition"] for row in report["records"]}
        self.assertIn("fixture_only_not_cleared", dispositions)
        self.assertIn("hold_for_human_review", dispositions)
        self.assertIn("excluded_by_declared_policy", dispositions)
        self.assertNotIn("approved", {value.casefold() for value in dispositions})
        self.assertEqual(summary["corpus_documents"], len(self.corpus))

    def test_quality_flags_do_not_remove_records_and_cover_fixture_cases(self):
        report, _ = audit_records(self.corpus, self.evaluation, min_characters=64)
        by_id = {row["id"]: row for row in report["records"]}
        self.assertIn("below_min_characters", by_id["doc-005"]["quality_flags"])
        self.assertIn("replacement_character_present", by_id["doc-006"]["quality_flags"])
        self.assertIn("repeated_lines_candidate", by_id["doc-007"]["quality_flags"])
        self.assertEqual(len(by_id), len(self.corpus))

    def test_report_contains_ids_and_hashes_but_not_raw_text(self):
        report, _ = audit_records(self.corpus, self.evaluation)
        serialized = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("پیکرهٔ آموزشی باید منشأ", serialized)
        self.assertTrue(all(len(row["content_sha256"]) == 64 for row in report["records"]))
        self.assertFalse(report["raw_text_in_report"])

    def test_comparison_normalization_is_nfc_and_whitespace_only_then_casefold(self):
        self.assertEqual(comparison_key("  ABC  def "), comparison_key("abc\n\tdef"))
        self.assertNotEqual(comparison_key("ی"), comparison_key("ي"))
        self.assertNotEqual(comparison_key("word, next"), comparison_key("word next"))

    def test_duplicate_normalization_detects_spacing_and_case_but_not_punctuation_change(self):
        left = dict(self.corpus[1], id="copy-a", text="Corpus line with   spacing.")
        right = dict(self.corpus[1], id="copy-b", text="corpus line with spacing.")
        punct = dict(self.corpus[1], id="copy-c", text="corpus line with spacing")
        report, _ = audit_records([left, right, punct], self.evaluation)
        pair_ids = {(pair["left_id"], pair["right_id"]) for pair in report["exact_duplicate_candidates"]}
        self.assertIn(("copy-a", "copy-b"), pair_ids)
        self.assertNotIn(("copy-a", "copy-c"), pair_ids)

    def test_evaluation_items_are_separate_and_never_written_as_corpus_records(self):
        report, _ = audit_records(self.corpus, self.evaluation)
        corpus_ids = {row["id"] for row in report["records"]}
        self.assertFalse(corpus_ids & {row["id"] for row in self.evaluation})
        self.assertEqual(len(corpus_ids), len(self.corpus))

    def test_thresholds_and_minimum_lengths_are_validated(self):
        with self.assertRaises(ValueError):
            near_duplicate_pairs(self.corpus, threshold=0)
        with self.assertRaises(ValueError):
            near_duplicate_pairs(self.corpus, threshold=True)
        with self.assertRaises(ValueError):
            near_duplicate_pairs(self.corpus, min_tokens=2, shingle_size=3)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            near_duplicate_pairs(self.corpus, min_tokens=6.5)
        with self.assertRaises(ValueError):
            evaluation_overlap_candidates(self.corpus, self.evaluation, near_threshold=float("nan"))
        with self.assertRaisesRegex(ValueError, "positive integer"):
            evaluation_overlap_candidates(self.corpus, self.evaluation, min_contiguous_tokens=True)
        with self.assertRaises(ValueError):
            quality_flags("text", min_characters=-1)
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            quality_flags("text", min_characters=3.5)

    def test_invalid_manifest_and_duplicate_ids_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.jsonl"
            path.write_text('{"id":', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid JSON"):
                load_corpus(path)
            row = dict(self.corpus[0])
            path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate id"):
                load_corpus(path)

    def test_unknown_rights_status_is_rejected_instead_of_treated_as_approved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad-status.jsonl"
            row = dict(self.corpus[0], rights_review_status="approved")
            path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "rights_review_status"):
                load_corpus(path)

    def test_outputs_are_deterministic_and_do_not_export_raw_corpus(self):
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / "first"
            second = Path(folder) / "second"
            audit_files(HERE / "sample_corpus.jsonl", HERE / "sample_evaluation.jsonl", first)
            audit_files(HERE / "sample_corpus.jsonl", HERE / "sample_evaluation.jsonl", second)
            for name in ("audit.json", "summary.json", "data_card.md"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            audit = json.loads((first / "audit.json").read_text(encoding="utf-8"))
            self.assertEqual(audit["summary"]["training_rows_exported"], 0)

    def test_local_demo_has_no_network_or_model_dependency(self):
        self.assertTrue((HERE / "sample_corpus.jsonl").is_file())
        self.assertTrue((HERE / "sample_evaluation.jsonl").is_file())
        source = (HERE / "corpus_audit.py").read_text(encoding="utf-8")
        self.assertNotIn("requests.", source)
        self.assertNotIn("torch", source)
        self.assertNotIn("urlopen", source)


if __name__ == "__main__":
    unittest.main()
