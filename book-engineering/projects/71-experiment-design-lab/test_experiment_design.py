import copy
import json
import unittest
from pathlib import Path

import experiment_design as lab

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / "analysis_plan.json").read_text(encoding="utf-8"))
FIXTURE = json.loads((ROOT / "synthetic_paired_scores.json").read_text(encoding="utf-8"))


class ExperimentDesignTests(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(PLAN)
        self.fixture = copy.deepcopy(FIXTURE)

    def test_locked_plan_names_independent_group_as_analysis_and_resampling_unit(self):
        lab.validate_plan(self.plan)
        self.assertEqual(self.plan["analysis_unit"], "task_group")
        self.assertEqual(self.plan["resampling_unit"], "task_group")

    def test_fixture_has_eight_groups_sixteen_tasks_and_thirty_two_rows(self):
        rows = lab.validate_fixture(self.fixture, self.plan)
        self.assertEqual(len(rows), 32)
        self.assertEqual(len({row["group_id"] for row in rows}), 8)
        self.assertEqual(len({row["task_id"] for row in rows}), 16)

    def test_analysis_is_deterministic_and_does_not_report_a_p_value(self):
        first = lab.analyze(self.fixture, self.plan, "fixture-hash", "plan-hash")
        second = lab.analyze(self.fixture, self.plan, "fixture-hash", "plan-hash")
        self.assertEqual(first, second)
        self.assertIsNone(first["primary_result"]["p_value"])
        self.assertFalse(first["inference_authorized"])
        self.assertEqual(first["design"]["resampling_unit"], "task_group")

    def test_mean_is_calculated_from_group_level_paired_differences(self):
        result = lab.analyze(self.fixture, self.plan, "fixture-hash", "plan-hash")
        differences = [row["paired_difference"] for row in result["group_results"]]
        self.assertEqual(result["primary_result"]["mean_paired_difference"], 0.0421875)
        self.assertAlmostEqual(result["primary_result"]["mean_paired_difference"], sum(differences) / 8, delta=1e-8)
        self.assertEqual(result["design"]["independent_groups"], 8)

    def test_interval_resamples_groups_and_is_ordered(self):
        result = lab.analyze(self.fixture, self.plan, "fixture-hash", "plan-hash")
        interval = result["primary_result"]["bootstrap_percentile_interval"]
        self.assertEqual(interval["unit_resampled"], "task_group_within_topic")
        self.assertEqual(interval["stratification_factor"], "topic")
        self.assertEqual(interval["strata_count"], 3)
        self.assertLessEqual(interval["lower"], interval["upper"])
        self.assertEqual(interval["replicates"], 2000)

    def test_rejects_fixture_not_marked_synthetic(self):
        self.fixture["synthetic"] = False
        with self.assertRaisesRegex(ValueError, "synthetic"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_plan_that_claims_real_preregistration(self):
        self.plan["status"] = "preregistered"
        with self.assertRaisesRegex(ValueError, "preregistration"):
            lab.validate_plan(self.plan)

    def test_rejects_pseudoreplication_plan(self):
        self.plan["resampling_unit"] = "observation_row"
        with self.assertRaisesRegex(ValueError, "resampling unit"):
            lab.validate_plan(self.plan)

    def test_rejects_different_topic_inside_one_group(self):
        self.fixture["observations"][1]["topic"] = "different"
        with self.assertRaisesRegex(ValueError, "multiple topics"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_duplicate_paired_observation(self):
        self.fixture["observations"].append(copy.deepcopy(self.fixture["observations"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_missing_repetition(self):
        self.fixture["observations"].pop(0)
        with self.assertRaisesRegex(ValueError, "repetitions are incomplete"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_unequal_tasks_per_group(self):
        self.fixture["observations"] = [row for row in self.fixture["observations"] if row["task_id"] != "g01-t02"]
        with self.assertRaisesRegex(ValueError, "task count is unbalanced"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_topic_block_with_too_few_independent_groups(self):
        for row in self.fixture["observations"]:
            if row["group_id"] == "g02":
                row["topic"] = "isolated-topic"
        with self.assertRaisesRegex(ValueError, "too few independent groups"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_task_id_reused_across_groups(self):
        for row in self.fixture["observations"]:
            if row["task_id"] == "g02-t01":
                row["task_id"] = "g01-t01"
        with self.assertRaisesRegex(ValueError, "appears in multiple groups"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_out_of_range_or_non_finite_scores(self):
        self.fixture["observations"][0]["candidate_score"] = 1.01
        with self.assertRaisesRegex(ValueError, r"in \[0, 1\]"):
            lab.validate_fixture(self.fixture, self.plan)
        self.fixture = copy.deepcopy(FIXTURE)
        self.fixture["observations"][0]["baseline_score"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_boolean_score_and_invalid_repetition(self):
        self.fixture["observations"][0]["baseline_score"] = True
        with self.assertRaisesRegex(ValueError, "numeric"):
            lab.validate_fixture(self.fixture, self.plan)
        self.fixture = copy.deepcopy(FIXTURE)
        self.fixture["observations"][0]["repetition"] = 0
        with self.assertRaisesRegex(ValueError, "positive integer"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_design_count_mismatch(self):
        self.plan["design"]["group_count"] = 7
        with self.assertRaisesRegex(ValueError, "group count"):
            lab.validate_fixture(self.fixture, self.plan)

    def test_rejects_p_value_or_invalid_bootstrap_configuration(self):
        self.plan["analysis"]["report_p_value"] = True
        with self.assertRaisesRegex(ValueError, "p-value"):
            lab.validate_plan(self.plan)
        self.plan = copy.deepcopy(PLAN)
        self.plan["analysis"]["bootstrap_replicates"] = 20
        with self.assertRaisesRegex(ValueError, "at least 100"):
            lab.validate_plan(self.plan)

    def test_rejects_fixture_id_mismatch(self):
        self.fixture["fixture_id"] = "other"
        with self.assertRaisesRegex(ValueError, "fixture_id"):
            lab.validate_fixture(self.fixture, self.plan)


if __name__ == "__main__":
    unittest.main()
