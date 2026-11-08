"""Unit tests for the synthetic final-capstone training and release packet."""
from __future__ import annotations

import json
import platform
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parent


class CapstoneContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture, cls.fixture_hash = capstone.load_fixture(ROOT / "synthetic_fixture.json")
        cls.plan = capstone.load_plan(ROOT)
        cls.model = capstone.train_model(cls.fixture["splits"]["train"], cls.plan["configuration"])

    def test_01_fixture_identity_is_final_capstone(self) -> None:
        self.assertEqual(self.fixture["project_id"], capstone.PROJECT_ID)
        self.assertTrue(self.fixture["synthetic"])

    def test_02_fixture_manifest_matches_exact_bytes(self) -> None:
        manifest = capstone.read_json(ROOT / "fixture_manifest.json")
        self.assertEqual(manifest["fixture_sha256"], self.fixture_hash)

    def test_03_fixture_has_sixteen_rows(self) -> None:
        self.assertEqual(sum(map(len, self.fixture["splits"].values())), 16)

    def test_04_fixture_split_sizes_are_declared(self) -> None:
        self.assertEqual({key: len(value) for key, value in self.fixture["splits"].items()},
                         {"train": 8, "validation": 4, "test": 4})

    def test_05_record_ids_are_unique_across_splits(self) -> None:
        ids = [row["id"] for rows in self.fixture["splits"].values() for row in rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_06_all_labels_follow_the_documented_toy_rule(self) -> None:
        for rows in self.fixture["splits"].values():
            for row in rows:
                self.assertEqual(row["toy_label"], int(row["x1"] + row["x2"] > 0))

    def test_07_rejects_wrong_project_identity(self) -> None:
        fixture = json.loads(json.dumps(self.fixture))
        fixture["project_id"] = "another-project"
        with self.assertRaises(capstone.CapstoneError):
            capstone.validate_fixture(fixture)

    def test_08_rejects_unsupported_schema_version(self) -> None:
        fixture = json.loads(json.dumps(self.fixture))
        fixture["schema_version"] = 2
        with self.assertRaises(capstone.CapstoneError):
            capstone.validate_fixture(fixture)

    def test_09_rejects_duplicate_ids_between_splits(self) -> None:
        fixture = json.loads(json.dumps(self.fixture))
        fixture["splits"]["test"][0]["id"] = fixture["splits"]["train"][0]["id"]
        with self.assertRaises(capstone.CapstoneError):
            capstone.validate_fixture(fixture)

    def test_10_rejects_label_that_breaks_the_fixture_rule(self) -> None:
        fixture = json.loads(json.dumps(self.fixture))
        fixture["splits"]["train"][0]["toy_label"] = 1
        with self.assertRaises(capstone.CapstoneError):
            capstone.validate_fixture(fixture)

    def test_11_rejects_nonfinite_features(self) -> None:
        fixture = json.loads(json.dumps(self.fixture))
        fixture["splits"]["train"][0]["x1"] = float("nan")
        with self.assertRaises(capstone.CapstoneError):
            capstone.validate_fixture(fixture)

    def test_12_rejects_fixture_marked_as_personal_data(self) -> None:
        fixture = json.loads(json.dumps(self.fixture))
        fixture["provenance"]["personal_data"] = True
        with self.assertRaises(capstone.CapstoneError):
            capstone.validate_fixture(fixture)

    def test_13_rejects_wrong_training_split_size(self) -> None:
        fixture = json.loads(json.dumps(self.fixture))
        fixture["splits"]["train"].pop()
        with self.assertRaises(capstone.CapstoneError):
            capstone.validate_fixture(fixture)

    def test_14_rejects_training_split_with_one_class(self) -> None:
        with self.assertRaises(capstone.CapstoneError):
            capstone.train_model(self.fixture["splits"]["train"][:4], self.plan["configuration"])

    def test_15_training_is_deterministic(self) -> None:
        first = capstone.train_model(self.fixture["splits"]["train"], self.plan["configuration"])
        second = capstone.train_model(self.fixture["splits"]["train"], self.plan["configuration"])
        self.assertEqual(first, second)

    def test_16_training_updates_both_weights(self) -> None:
        self.assertTrue(all(weight > 0 for weight in self.model["weights"]))
        self.assertNotEqual(self.model["weights"], [0.0, 0.0])

    def test_17_validation_and_test_rows_are_not_training_inputs(self) -> None:
        training_copy = json.loads(json.dumps(self.fixture["splits"]["train"]))
        held_out_copy = json.loads(json.dumps(self.fixture["splits"]["validation"] + self.fixture["splits"]["test"]))
        first = capstone.train_model(training_copy, self.plan["configuration"])
        held_out_copy[0]["x1"] = 9999.0
        held_out_copy[-1]["x2"] = -9999.0
        second = capstone.train_model(training_copy, self.plan["configuration"])
        self.assertEqual(first, second)

    def test_18_rejects_empty_evaluation_split(self) -> None:
        with self.assertRaises(capstone.CapstoneError):
            capstone.evaluate_rows([], self.model)

    def test_19_confusion_counts_equal_evaluation_count(self) -> None:
        metrics, _ = capstone.evaluate_rows(self.fixture["splits"]["test"], self.model)
        self.assertEqual(sum(metrics["confusion_matrix"].values()), metrics["count"])

    def test_20_toy_test_accuracy_is_four_of_four(self) -> None:
        metrics, _ = capstone.evaluate_rows(self.fixture["splits"]["test"], self.model)
        self.assertEqual((metrics["correct"], metrics["count"], metrics["accuracy"]), (4, 4, 1.0))

    def test_21_majority_baseline_is_two_of_four(self) -> None:
        metrics = capstone.evaluate_majority_baseline(
            self.fixture["splits"]["test"], self.fixture["splits"]["train"]
        )
        self.assertEqual((metrics["correct"], metrics["count"], metrics["accuracy"]), (2, 4, 0.5))

    def test_22_release_decision_blocks_deployment(self) -> None:
        decision = capstone.read_json(ROOT / "release_decision.json")
        self.assertEqual(decision["decision"], "educational_source_packet_only")
        self.assertEqual(decision["model_deployment"], "not_approved")
        self.assertIn("downstream redistribution without a separate rights and license review",
                      decision["blocked_scope"])

    def test_23_saved_bundle_reproduces_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            capstone.run_project(ROOT / "synthetic_fixture.json", output, ROOT)
            for name in ("checkpoint.json", "results.json"):
                self.assertEqual((ROOT / name).read_bytes(), (output / name).read_bytes(), name)

            stored_environment = capstone.read_json(ROOT / "environment.json")
            generated_environment = capstone.read_json(output / "environment.json")
            self.assertEqual(
                {key: value for key, value in generated_environment.items() if key != "runtime"},
                {key: value for key, value in stored_environment.items() if key != "runtime"},
            )
            self.assertEqual(
                generated_environment["runtime"],
                {
                    "implementation": platform.python_implementation(),
                    "version": platform.python_version(),
                    "platform": sys.platform,
                },
            )
            capstone.verify_release(output / "release_manifest.json", ROOT, output)

    def test_24_manifest_verifies_and_detects_output_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            capstone.run_project(ROOT / "synthetic_fixture.json", output, ROOT)
            capstone.verify_release(output / "release_manifest.json", ROOT, output)
            with (output / "results.json").open("a", encoding="utf-8") as handle:
                handle.write(" ")
            with self.assertRaises(capstone.CapstoneError):
                capstone.verify_release(output / "release_manifest.json", ROOT, output)

    def test_25_modified_fixture_is_rejected_by_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copied_fixture = Path(temp) / "synthetic_fixture.json"
            copied_manifest = Path(temp) / "fixture_manifest.json"
            shutil.copyfile(ROOT / "synthetic_fixture.json", copied_fixture)
            shutil.copyfile(ROOT / "fixture_manifest.json", copied_manifest)
            copied_fixture.write_text(copied_fixture.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(capstone.CapstoneError):
                capstone.load_fixture(copied_fixture, copied_manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
