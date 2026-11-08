from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from paper_reproduction import FIXTURE_ID, evaluate, run

HERE = Path(__file__).resolve().parent
PACKET_PATH = HERE / "synthetic_paper_packet.json"
MANIFEST_PATH = HERE / "fixture_manifest.json"


def load_fixture():
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


class PaperReproductionTests(unittest.TestCase):
    def test_fixture_hash_matches_manifest(self):
        packet_hash = hashlib.sha256(PACKET_PATH.read_bytes()).hexdigest()
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["fixture_id"], FIXTURE_ID)
        self.assertEqual(manifest["sha256"], packet_hash)
        self.assertTrue(manifest["synthetic"])
        self.assertEqual(manifest["observation_count"], 8)

    def test_default_claim_statuses_are_explicit_and_partial(self):
        result = evaluate(load_fixture())
        self.assertEqual([claim["claim_id"] for claim in result["claim_results"]], ["C1", "C2", "C3"])
        self.assertEqual([claim["status"] for claim in result["claim_results"]], [
            "reproduced_within_tolerance", "blocked", "not_assessed",
        ])
        self.assertEqual(result["overall_status"], "partial_or_unassessed")
        self.assertTrue(result["synthetic"])

    def test_mae_and_improvement_are_computed_from_rows(self):
        c1 = evaluate(load_fixture())["claim_results"][0]
        metrics = c1["metrics"]
        self.assertEqual(metrics["baseline_mae"], 0.5)
        self.assertEqual(metrics["reported_candidate_mae_from_rows"], 0.4)
        self.assertEqual(metrics["rerun_candidate_mae"], 0.42)
        self.assertEqual(metrics["relative_improvement_vs_baseline"], 0.16)
        self.assertEqual(c1["status"], "reproduced_within_tolerance")

    def test_missing_c1_artifact_blocks_execution(self):
        packet = load_fixture()
        packet["claims"][0]["artifacts_available"]["analysis_code"] = False
        c1 = evaluate(packet)["claim_results"][0]
        self.assertEqual(c1["status"], "blocked")
        self.assertEqual(c1["missing_artifacts"], ["analysis_code"])

    def test_missing_checkpoint_is_not_evidence_against_c2(self):
        c2 = evaluate(load_fixture())["claim_results"][1]
        self.assertEqual(c2["status"], "blocked")
        self.assertEqual(c2["missing_artifacts"], ["checkpoint_sha256", "tokenizer_sha256"])
        self.assertIn("شاهدی علیه درستی", c2["interpretation"])

    def test_missing_independent_group_leaves_generalization_unassessed(self):
        c3 = evaluate(load_fixture())["claim_results"][2]
        self.assertEqual(c3["status"], "not_assessed")
        self.assertEqual(c3["missing_required_groups"], ["fictional-domain-B"])

    def test_large_metric_disagreement_is_not_reproduced(self):
        packet = load_fixture()
        for row in packet["protocol"]["rows"]:
            row["rerun_prediction"] = row["target"] + 0.9
        c1 = evaluate(packet)["claim_results"][0]
        self.assertEqual(c1["status"], "not_reproduced")
        self.assertIn("اختلاف به‌تنهایی", c1["interpretation"])

    def test_zero_baseline_does_not_divide_by_zero_or_claim_improvement(self):
        packet = load_fixture()
        for row in packet["protocol"]["rows"]:
            row["baseline_prediction"] = row["target"]
            row["reported_prediction"] = row["target"]
            row["rerun_prediction"] = row["target"]
        packet["protocol"]["published"].update({
            "baseline_mae": 0.0,
            "candidate_mae": 0.0,
            "minimum_relative_improvement": 0.0,
        })
        c1 = evaluate(packet)["claim_results"][0]
        self.assertIsNone(c1["metrics"]["relative_improvement_vs_baseline"])
        self.assertEqual(c1["status"], "not_reproduced")

    def test_duplicate_row_ids_are_rejected(self):
        packet = load_fixture()
        packet["protocol"]["rows"][1]["row_id"] = packet["protocol"]["rows"][0]["row_id"]
        with self.assertRaisesRegex(ValueError, "duplicate row_id"):
            evaluate(packet)

    def test_non_finite_numbers_are_rejected(self):
        packet = load_fixture()
        packet["protocol"]["rows"][0]["target"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite number"):
            evaluate(packet)

    def test_unsupported_metric_is_rejected(self):
        packet = load_fixture()
        packet["protocol"]["metric"] = "accuracy"
        with self.assertRaisesRegex(ValueError, "only the declared MAE"):
            evaluate(packet)

    def test_non_synthetic_packet_is_rejected(self):
        packet = load_fixture()
        packet["synthetic"] = False
        with self.assertRaisesRegex(ValueError, "only the declared synthetic"):
            evaluate(packet)

    def test_run_writes_stable_result_with_fixture_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "result.json"
            first = run(PACKET_PATH, output)
            first_bytes = output.read_bytes()
            second = run(PACKET_PATH, output)
            self.assertEqual(first, second)
            self.assertEqual(first_bytes, output.read_bytes())
            self.assertEqual(first["fixture_sha256"], hashlib.sha256(PACKET_PATH.read_bytes()).hexdigest())

    def test_manifest_mismatch_is_rejected_before_result_is_written(self):
        packet = load_fixture()
        packet["protocol"]["rows"][0]["target"] = 9.0
        with tempfile.TemporaryDirectory() as directory:
            changed_packet = Path(directory) / "changed_packet.json"
            output = Path(directory) / "result.json"
            changed_packet.write_text(json.dumps(packet), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "do not match the declared manifest"):
                run(changed_packet, output, MANIFEST_PATH)
            self.assertFalse(output.exists())

    def test_cli_uses_relative_inputs_and_writes_requested_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "cli-results.json"
            completed = subprocess.run(
                [sys.executable, str(HERE / "paper_reproduction.py"),
                 "--packet", str(PACKET_PATH), "--manifest", str(MANIFEST_PATH), "--output", str(output)],
                cwd=directory, check=True, capture_output=True, text=True,
            )
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("partial_or_unassessed", completed.stdout)
            self.assertEqual(result["project_id"], FIXTURE_ID)
            self.assertEqual(result["status_counts"], {
                "blocked": 1, "not_assessed": 1, "reproduced_within_tolerance": 1,
            })

    def test_input_object_is_not_mutated(self):
        packet = load_fixture()
        original = copy.deepcopy(packet)
        evaluate(packet)
        self.assertEqual(packet, original)


if __name__ == "__main__":
    unittest.main()
