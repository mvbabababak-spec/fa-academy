"""Tests for the numerical behavior taught in chapter 45."""
from __future__ import annotations

import json
import unittest

import torch

from precision_lab import (
    calculate_qparams,
    cpu_autocast_probe,
    format_table,
    precision_probe,
    quantization_demo,
    quantize_with_qparams,
    run_lab,
)


class FormatTests(unittest.TestCase):
    def test_format_metadata_uses_runtime_finfo(self):
        rows = {row["name"]: row for row in format_table()}
        self.assertTrue({"FP32", "FP16", "BF16", "FP8 E4M3FN", "FP8 E5M2"}.issubset(rows))
        self.assertEqual(rows["FP32"]["bytes_per_element"], 4)
        self.assertEqual(rows["FP16"]["bytes_per_element"], 2)
        self.assertEqual(rows["BF16"]["bytes_per_element"], 2)
        self.assertEqual(rows["FP8 E4M3FN"]["max_finite"], 448.0)
        self.assertEqual(rows["FP8 E5M2"]["max_finite"], 57344.0)
        self.assertEqual(rows["FP16"]["max_finite"], 65504.0)
        self.assertGreater(rows["BF16"]["max_finite"], rows["FP16"]["max_finite"])
        self.assertEqual(rows["FP8 E4M3FN"]["million_values_decimal_MB"], 1.0)

    def test_cast_probe_reports_underflow_and_overflow_observed_at_runtime(self):
        report = precision_probe()
        rows = {row["name"]: row for row in report["casts"]}
        self.assertEqual(rows["FP16"]["nonzero_to_zero_count"], 1)
        self.assertEqual(rows["FP16"]["infinity_count"], 2)
        self.assertEqual(len(rows["BF16"]["roundtrip_values"]), 5)
        self.assertTrue(rows["FP8 E4M3FN"]["available"])
        self.assertIn("nan_count", rows["FP8 E4M3FN"])
        self.assertIsNotNone(rows["FP32"]["max_abs_error_on_finite_values"])


class AutocastTests(unittest.TestCase):
    def test_cpu_bf16_autocast_keeps_parameters_fp32_and_outputs_finite(self):
        report = cpu_autocast_probe()
        self.assertEqual(report["parameter_dtype_after_autocast"], "torch.float32")
        self.assertEqual(report["output_dtype"], "torch.bfloat16")
        self.assertTrue(report["finite_output"])
        self.assertFalse(report["benchmark_performed"])
        self.assertGreaterEqual(report["max_abs_difference_from_fp32"], 0.0)


class QuantizationTests(unittest.TestCase):
    def test_symmetric_int8_has_exact_zero_and_expected_endpoints(self):
        values = torch.tensor([-1.0, 0.0, 1.0])
        qparams = calculate_qparams(values, bits=8, symmetric=True)
        result = quantize_with_qparams(values, qparams)
        self.assertEqual((qparams["qmin"], qparams["qmax"]), (-127, 127))
        self.assertEqual(qparams["zero_points"], [0])
        self.assertAlmostEqual(qparams["scales"][0], 1.0 / 127.0)
        self.assertEqual(result["codes"].tolist(), [-127, 0, 127])
        self.assertEqual(result["saturation_count"], 0)
        torch.testing.assert_close(result["dequantized"], values, rtol=0, atol=1e-7)

    def test_asymmetric_quantization_uses_a_nonzero_zero_point_when_needed(self):
        values = torch.tensor([-1.0, 0.0, 2.0])
        qparams = calculate_qparams(values, bits=8, symmetric=False)
        result = quantize_with_qparams(values, qparams)
        self.assertEqual((qparams["qmin"], qparams["qmax"]), (-128, 127))
        self.assertNotEqual(qparams["zero_points"][0], 0)
        self.assertEqual(result["codes"][0].item(), -128)
        self.assertEqual(result["codes"][2].item(), 127)
        self.assertLess(result["max_abs_error"], 0.02)

    def test_per_group_scale_reduces_error_in_outlier_example(self):
        report = quantization_demo()
        per_tensor = report["int8_per_tensor"]["result"]
        per_group = report["int8_per_group"]["result"]
        self.assertEqual(len(per_tensor["scales"]), 1)
        self.assertEqual(len(per_group["scales"]), 2)
        self.assertLess(per_group["rmse"], per_tensor["rmse"])
        self.assertEqual(per_group["saturation_count"], 0)

    def test_calibration_range_shift_is_reported_as_saturation(self):
        calibration = torch.tensor([-1.0, -0.5, 0.0, 0.5, 1.0])
        evaluation = torch.tensor([-1.5, -0.2, 1.4])
        qparams = calculate_qparams(calibration, symmetric=True)
        result = quantize_with_qparams(evaluation, qparams)
        self.assertEqual(result["saturation_count"], 2)
        self.assertAlmostEqual(result["saturation_fraction"], 2.0 / 3.0)
        self.assertTrue(bool(torch.isfinite(result["dequantized"]).all().item()))

    def test_zero_input_and_invalid_calibration_are_handled(self):
        zeros = torch.zeros(4)
        qparams = calculate_qparams(zeros)
        result = quantize_with_qparams(zeros, qparams)
        self.assertEqual(qparams["scales"], [1.0])
        self.assertEqual(result["codes"].tolist(), [0, 0, 0, 0])
        with self.assertRaises(ValueError):
            calculate_qparams([])
        with self.assertRaises(ValueError):
            calculate_qparams([float("nan")])
        with self.assertRaises(ValueError):
            calculate_qparams([0.0, 1.0], granularity="group", group_size=0)

    def test_group_parameters_require_matching_layout(self):
        calibration = torch.tensor([0.1, 0.2, 1.0, -1.0])
        qparams = calculate_qparams(calibration, granularity="group", group_size=2)
        with self.assertRaises(ValueError):
            quantize_with_qparams(torch.tensor([0.1, 0.2]), qparams)


class ReportTests(unittest.TestCase):
    def test_complete_report_is_strict_json(self):
        report = run_lab()
        encoded = json.dumps(report, allow_nan=False)
        self.assertIn('"cpu_bf16_autocast"', encoded)
        self.assertIn('"int8_per_group"', encoded)
        self.assertEqual(report["runtime"]["device"], "cpu")


if __name__ == "__main__":
    unittest.main()
