"""Unit tests for deterministic trace arithmetic and schema rejection."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import inference_lab as lab


FIXTURE_PATH = Path(__file__).with_name("sample_trace.json")


class KVCacheTests(unittest.TestCase):
    def test_reference_profile_is_half_gib_per_sequence(self) -> None:
        self.assertEqual(
            lab.estimate_kv_cache_bytes(
                layers=32, kv_heads=8, head_dim=128, bytes_per_element=2,
                tokens=4096,
            ),
            536_870_912,
        )

    def test_cache_scales_linearly_with_sequences(self) -> None:
        one = lab.estimate_kv_cache_bytes(
            layers=32, kv_heads=8, head_dim=128, bytes_per_element=2,
            tokens=4096,
        )
        eight = lab.estimate_kv_cache_bytes(
            layers=32, kv_heads=8, head_dim=128, bytes_per_element=2,
            tokens=4096, sequences=8,
        )
        self.assertEqual(eight, one * 8)

    def test_nonpositive_cache_dimension_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "layers"):
            lab.estimate_kv_cache_bytes(
                layers=0, kv_heads=8, head_dim=128, bytes_per_element=2,
                tokens=4096,
            )

    def test_boolean_is_not_an_integer_dimension(self) -> None:
        with self.assertRaisesRegex(ValueError, "sequences"):
            lab.estimate_kv_cache_bytes(
                layers=32, kv_heads=8, head_dim=128, bytes_per_element=2,
                tokens=4096, sequences=True,
            )


class PercentileTests(unittest.TestCase):
    def test_nearest_rank_percentiles(self) -> None:
        values = [5, 1, 4, 2, 3]
        self.assertEqual(lab.nearest_rank_percentile(values, 50), 3)
        self.assertEqual(lab.nearest_rank_percentile(values, 95), 5)
        self.assertEqual(lab.nearest_rank_percentile(values, 0), 1)

    def test_empty_percentile_sample_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            lab.nearest_rank_percentile([], 50)

    def test_out_of_range_percentile_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            lab.nearest_rank_percentile([1, 2], 101)

    def test_nonfinite_percentile_sample_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite number"):
            lab.nearest_rank_percentile([1, float("nan")], 50)


class TraceAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_fixture_has_two_runs_and_four_gib_cache_estimate(self) -> None:
        result = lab.analyze_fixture(self.fixture)
        self.assertEqual(len(result["runs"]), 2)
        self.assertEqual(result["kv_cache_estimate"]["bytes_per_sequence"], 536_870_912)
        self.assertEqual(result["kv_cache_estimate"]["bytes_for_concurrency"], 4_294_967_296)
        self.assertEqual(result["kv_cache_estimate"]["GiB_for_concurrency"], 4.0)

    def test_failed_requests_are_counted_but_not_in_latency_percentiles(self) -> None:
        summary = lab.summarize_run(self.fixture["runs"][0])
        self.assertEqual(summary["requests"]["attempted"], 6)
        self.assertEqual(summary["requests"]["successful"], 5)
        self.assertEqual(summary["requests"]["failed_or_timed_out"], 1)
        self.assertEqual(summary["requests"]["error_rate"], 1 / 6)
        self.assertEqual(summary["latency"]["ttft"]["count"], 5)

    def test_request_and_token_rates_use_declared_window(self) -> None:
        summary = lab.summarize_run(self.fixture["runs"][0])
        self.assertEqual(summary["requests"]["successful_requests_per_s"], 2.5)
        self.assertEqual(summary["tokens_per_s"]["prompt"], 1088.0)
        self.assertEqual(summary["tokens_per_s"]["completion"], 234.0)

    def test_ttft_and_end_to_end_percentiles_are_derived_from_request_times(self) -> None:
        summary = lab.summarize_run(self.fixture["runs"][0])
        self.assertEqual(summary["latency"]["ttft"]["p50_ms"], 230.0)
        self.assertEqual(summary["latency"]["ttft"]["p95_ms"], 350.0)
        self.assertEqual(summary["latency"]["end_to_end"]["p50_ms"], 800.0)
        self.assertEqual(summary["latency"]["end_to_end"]["p95_ms"], 1080.0)

    def test_tpot_uses_first_output_and_completion_token_count(self) -> None:
        run = copy.deepcopy(self.fixture["runs"][0])
        run["requests"] = [run["requests"][0]]
        summary = lab.summarize_run(run)
        expected = (620 - 160) / (64 - 1)
        self.assertAlmostEqual(summary["latency"]["estimated_tpot"]["p50_ms"], expected)

    def test_single_completion_token_has_no_tpot_sample(self) -> None:
        run = {
            "run_id": "one-token", "runtime": "fixture", "configuration": {},
            "window_ms": 100, "requests": [
                {"request_id": "only", "arrival_ms": 0, "first_output_ms": 10,
                 "finish_ms": 20, "prompt_tokens": 1, "completion_tokens": 1,
                 "status": "ok"}
            ],
        }
        self.assertEqual(lab.summarize_run(run)["latency"]["estimated_tpot"]["count"], 0)

    def test_trace_digest_is_stable_for_the_fixture_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.json"
            path.write_bytes(FIXTURE_PATH.read_bytes())
            first = lab.run(path)
            second = lab.run(path)
        self.assertEqual(first["fixture_sha256"], second["fixture_sha256"])
        self.assertEqual(first["fixture_id"], self.fixture["fixture_id"])


class SchemaValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_empty_run_list_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["runs"] = []
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            lab.validate_fixture(fixture)

    def test_duplicate_run_ids_are_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["runs"][1]["run_id"] = fixture["runs"][0]["run_id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            lab.validate_fixture(fixture)

    def test_duplicate_request_ids_are_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["runs"][0]["requests"][1]["request_id"] = fixture["runs"][0]["requests"][0]["request_id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            lab.validate_fixture(fixture)

    def test_finish_before_first_output_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["runs"][0]["requests"][0]["finish_ms"] = 100
        with self.assertRaisesRegex(ValueError, "arrival <= first output <= finish"):
            lab.validate_fixture(fixture)

    def test_success_without_completion_tokens_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["runs"][0]["requests"][0]["completion_tokens"] = 0
        with self.assertRaisesRegex(ValueError, "positive integer"):
            lab.validate_fixture(fixture)

    def test_unknown_status_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["runs"][0]["requests"][0]["status"] = "maybe"
        with self.assertRaisesRegex(ValueError, "status"):
            lab.validate_fixture(fixture)

    def test_negative_prompt_token_count_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["runs"][0]["requests"][0]["prompt_tokens"] = -1
        with self.assertRaisesRegex(ValueError, "non-negative"):
            lab.validate_fixture(fixture)

    def test_zero_window_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["runs"][0]["window_ms"] = 0
        with self.assertRaisesRegex(ValueError, "window_ms must be positive"):
            lab.validate_fixture(fixture)

    def test_unknown_schema_version_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["schema_version"] = 2
        with self.assertRaisesRegex(ValueError, "schema_version"):
            lab.validate_fixture(fixture)


if __name__ == "__main__":
    unittest.main()
