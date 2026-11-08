from __future__ import annotations

import copy
import importlib.util
import json
import math
import unittest
from pathlib import Path

from framework_compare import (
    BACKENDS,
    ComparisonInputError,
    build_report,
    load_fixture,
    reference_result,
    run_backend,
    validate_fixture,
)

ROOT = Path(__file__).resolve().parent
FIXTURE_PATH = ROOT / "sample_problem.json"


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.fixture, self.raw = load_fixture(FIXTURE_PATH)

    def test_fixture_is_synthetic_and_explicitly_disclaims_real_runs(self):
        self.assertEqual(self.fixture["fixture_id"], "v4-ch11-synthetic-gradient-v1")
        self.assertEqual(self.fixture["label_source"], "synthetic_fixture")
        self.assertTrue(all(value is False for value in self.fixture["metadata"].values()))

    def test_fixture_sha_is_stable_and_reported(self):
        import hashlib

        report = build_report(self.fixture, self.raw, "reference")
        self.assertEqual(report["fixture_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(report["summary"]["status"], "reference_only")

    def test_reference_loss_and_gradients_match_closed_form(self):
        self.assertEqual(
            reference_result(self.fixture),
            {"loss": 2.5, "gradient_weight": -2.0, "gradient_bias": -3.0},
        )

    def test_reference_report_is_json_serializable(self):
        report = build_report(self.fixture, self.raw, "reference")
        self.assertEqual(json.loads(json.dumps(report))["reference"]["loss"], 2.5)


class InputValidationTests(unittest.TestCase):
    def setUp(self):
        self.fixture, _ = load_fixture(FIXTURE_PATH)

    def test_rejects_unknown_schema_and_fixture_identity(self):
        altered = copy.deepcopy(self.fixture)
        altered["schema_version"] = 2
        with self.assertRaises(ComparisonInputError):
            validate_fixture(altered)
        altered = copy.deepcopy(self.fixture)
        altered["fixture_id"] = "another-case"
        with self.assertRaises(ComparisonInputError):
            validate_fixture(altered)

    def test_rejects_real_or_unlabelled_fixture(self):
        altered = copy.deepcopy(self.fixture)
        altered["label_source"] = "real_measurement"
        with self.assertRaises(ComparisonInputError):
            validate_fixture(altered)
        altered = copy.deepcopy(self.fixture)
        altered["metadata"]["benchmark_performed"] = True
        with self.assertRaises(ComparisonInputError):
            validate_fixture(altered)

    def test_rejects_mismatched_or_short_arrays(self):
        for x, y in (([0.0, 1.0], [1.0]), ([0.0], [1.0])):
            altered = copy.deepcopy(self.fixture)
            altered["x"], altered["y"] = x, y
            with self.subTest(x=x, y=y), self.assertRaises(ComparisonInputError):
                validate_fixture(altered)

    def test_rejects_boolean_and_nonfinite_numbers(self):
        for value in (True, float("nan"), float("inf")):
            altered = copy.deepcopy(self.fixture)
            altered["x"][0] = value
            with self.subTest(value=value), self.assertRaises(ComparisonInputError):
                validate_fixture(altered)

    def test_rejects_invalid_tolerance(self):
        for tolerance in (0, -1, 0.1, float("nan")):
            altered = copy.deepcopy(self.fixture)
            altered["absolute_tolerance"] = tolerance
            with self.subTest(tolerance=tolerance), self.assertRaises(ComparisonInputError):
                validate_fixture(altered)

    def test_rejects_unknown_backend(self):
        with self.assertRaises(ComparisonInputError):
            build_report(self.fixture, b"{}", "numpy")
        with self.assertRaises(ComparisonInputError):
            run_backend("numpy", self.fixture)


class OptionalFrameworkTests(unittest.TestCase):
    def setUp(self):
        self.fixture, _ = load_fixture(FIXTURE_PATH)

    def _check_backend(self, name: str):
        result = run_backend(name, self.fixture)
        if result["status"] == "not_installed":
            self.skipTest(f"{name} is not installed in this environment")
        self.assertEqual(result["status"], "passed", result)
        self.assertEqual(result["device"], "cpu")
        self.assertLessEqual(max(result["absolute_difference_from_reference"].values()), self.fixture["absolute_tolerance"])

    def test_torch_cpu_adapter_when_installed(self):
        self._check_backend("torch")

    def test_jax_cpu_adapter_when_installed(self):
        self._check_backend("jax")

    def test_tensorflow_cpu_adapter_when_installed(self):
        self._check_backend("tensorflow")

    def test_all_mode_distinguishes_skips_from_failures(self):
        raw = FIXTURE_PATH.read_bytes()
        report = build_report(self.fixture, raw, "all")
        self.assertEqual(set(report["framework_results"]), set(BACKENDS))
        self.assertEqual(report["summary"]["failed"], [])
        self.assertIn(report["summary"]["status"], {"reference_only", "passed_with_skips", "passed"})
        for name, row in report["framework_results"].items():
            if importlib.util.find_spec(name) is None:
                self.assertEqual(row["status"], "not_installed")
            else:
                self.assertIn(row["status"], {"passed", "import_error"})

    def test_fixture_reference_has_finite_values(self):
        self.assertTrue(all(math.isfinite(value) for value in reference_result(self.fixture).values()))


if __name__ == "__main__":
    unittest.main()
