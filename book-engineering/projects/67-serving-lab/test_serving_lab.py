"""Unit checks for the synthetic service-level serving simulator."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

import serving_lab as lab

ROOT = Path(__file__).resolve().parent
FIXTURE = json.loads((ROOT / "synthetic_serving_trace.json").read_text(encoding="utf-8"))


def one_request(request_id: str, arrival_ms: int, expected: str = "پاسخ نمونه") -> dict:
    return {
        "request_id": request_id,
        "arrival_ms": arrival_ms,
        "model_revision": "toy-r1",
        "prompt_id": "prompt-shared",
        "decoding": {"temperature": 0, "top_p": 1.0, "seed": 0},
        "locale": "fa",
        "context_revision": "context-r1",
        "prompt_tokens": 8,
        "output_tokens": 4,
        "deadline_ms": 500,
        "expected_output": expected,
    }


def fixture_for(*requests: dict) -> dict:
    return {"fixture_id": lab.FIXTURE_ID, "synthetic": True, "requests": list(requests)}


def config(**changes) -> dict:
    result = {
        "name": "test",
        "batch_size": 1,
        "batch_wait_ms": 0,
        "max_queue_size": 8,
        "cache_enabled": False,
        "max_cache_entries": 0,
        "max_cache_bytes": 0,
    }
    result.update(changes)
    return result


class ServingLabTests(unittest.TestCase):
    def test_fixture_is_valid_and_has_twelve_exact_keys(self) -> None:
        lab.validate_fixture(FIXTURE)
        self.assertEqual(len(FIXTURE["requests"]), 24)
        self.assertEqual(len({lab.response_cache_key(item) for item in FIXTURE["requests"]}), 12)

    def test_model_revision_changes_cache_identity(self) -> None:
        request = one_request("a", 0)
        changed = copy.deepcopy(request)
        changed["model_revision"] = "toy-r2"
        self.assertNotEqual(lab.response_cache_key(request), lab.response_cache_key(changed))

    def test_decoding_and_context_change_cache_identity(self) -> None:
        request = one_request("a", 0)
        changed_decoding = copy.deepcopy(request)
        changed_decoding["decoding"]["temperature"] = 0.7
        changed_context = copy.deepcopy(request)
        changed_context["context_revision"] = "context-r2"
        self.assertNotEqual(lab.response_cache_key(request), lab.response_cache_key(changed_decoding))
        self.assertNotEqual(lab.response_cache_key(request), lab.response_cache_key(changed_context))

    def test_little_law_example(self) -> None:
        self.assertEqual(lab.little_average_in_system(20, 0.25), 5.0)
        with self.assertRaises(ValueError):
            lab.little_average_in_system(-1, 0.25)

    def test_nearest_rank_percentile(self) -> None:
        self.assertEqual(lab.nearest_rank_percentile([4, 1, 3, 2], 50), 2.0)
        self.assertEqual(lab.nearest_rank_percentile([4, 1, 3, 2], 95), 4.0)
        self.assertIsNone(lab.nearest_rank_percentile([], 95))

    def test_fixture_runs_are_deterministic(self) -> None:
        first = lab.simulate(FIXTURE, lab.CONFIGURATIONS[1])
        second = lab.simulate(FIXTURE, lab.CONFIGURATIONS[1])
        self.assertEqual(first, second)

    def test_microbatch_forms_a_full_batch_at_the_fourth_arrival(self) -> None:
        result = lab.simulate(FIXTURE, lab.CONFIGURATIONS[1])
        first_batch = result["batch_schedule"][0]
        self.assertEqual(first_batch["batch_size"], 4)
        self.assertEqual(first_batch["start_ms"], 9.0)
        self.assertEqual(result["model_batches"], 6)

    def test_microbatch_run_avoids_queue_rejections_in_fixture(self) -> None:
        result = lab.simulate(FIXTURE, lab.CONFIGURATIONS[1])
        self.assertEqual(result["successful_responses"], 24)
        self.assertEqual(result["queue_rejections"], 0)
        self.assertEqual(result["max_waiting_queue_depth"], 8)

    def test_cache_hits_only_after_first_response_completes(self) -> None:
        early = lab.simulate(
            fixture_for(one_request("first", 0), one_request("too-early", 1)),
            config(cache_enabled=True, max_cache_entries=4, max_cache_bytes=4096),
        )
        self.assertEqual(early["response_cache_hits"], 0)
        self.assertEqual(early["model_compute_requests"], 2)

        late = lab.simulate(
            fixture_for(one_request("first", 0), one_request("after", 100)),
            config(cache_enabled=True, max_cache_entries=4, max_cache_bytes=4096),
        )
        self.assertEqual(late["response_cache_hits"], 1)
        self.assertEqual(late["model_compute_requests"], 1)

    def test_bounded_queue_rejects_instead_of_growing_without_limit(self) -> None:
        requests = [one_request(f"r{i}", i) for i in range(5)]
        result = lab.simulate(
            fixture_for(*requests),
            config(max_queue_size=1),
        )
        self.assertEqual(result["max_waiting_queue_depth"], 1)
        self.assertEqual(result["queue_rejections"], 3)
        self.assertEqual(result["successful_responses"], 2)

    def test_exact_cache_reports_a_wrong_reused_response(self) -> None:
        result = lab.simulate(
            fixture_for(one_request("first", 0, "پاسخ اول"), one_request("changed", 100, "پاسخ تازه")),
            config(cache_enabled=True, max_cache_entries=4, max_cache_bytes=4096),
        )
        self.assertEqual(result["response_cache_hits"], 1)
        self.assertEqual(result["output_integrity_matches"], 1)
        self.assertEqual(result["successful_responses"], 2)
        self.assertEqual(result["output_integrity_rate"], 0.5)

    def test_response_cache_obeys_lru_entry_and_byte_bounds(self) -> None:
        cache = lab.ResponseCache(max_entries=2, max_bytes=6)
        self.assertTrue(cache.store("a", "x", 0))
        self.assertTrue(cache.store("b", "x", 0))
        self.assertEqual(cache.get("a", 1), "x")
        self.assertTrue(cache.store("c", "x", 2))
        self.assertEqual(cache.get("b", 3), None)
        self.assertEqual(cache.get("a", 3), "x")
        self.assertEqual(cache.get("c", 3), "x")
        self.assertLessEqual(cache.payload_bytes, 6)

    def test_cache_entry_larger_than_byte_budget_is_not_stored(self) -> None:
        cache = lab.ResponseCache(max_entries=4, max_bytes=1)
        self.assertFalse(cache.store("k", "v", 0))
        self.assertEqual(cache.payload_bytes, 0)

    def test_full_trace_separates_batching_from_exact_cache(self) -> None:
        baseline = lab.simulate(FIXTURE, lab.CONFIGURATIONS[0])
        batched = lab.simulate(FIXTURE, lab.CONFIGURATIONS[1])
        cached = lab.simulate(FIXTURE, lab.CONFIGURATIONS[2])
        combined = lab.simulate(FIXTURE, lab.CONFIGURATIONS[3])
        self.assertEqual(baseline["queue_rejections"], 4)
        self.assertEqual(batched["queue_rejections"], 0)
        self.assertEqual(cached["response_cache_hits"], 10)
        self.assertEqual(combined["response_cache_hits"], 12)
        self.assertEqual(combined["model_compute_requests"], 12)
        self.assertEqual(combined["output_integrity_rate"], 1.0)

    def test_duplicate_request_ids_are_rejected(self) -> None:
        duplicate = fixture_for(one_request("same", 0), one_request("same", 1))
        with self.assertRaises(lab.FixtureError):
            lab.validate_fixture(duplicate)

    def test_invalid_configuration_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            lab.simulate(FIXTURE, config(batch_size=0))
        with self.assertRaises(ValueError):
            lab.simulate(FIXTURE, config(batch_wait_ms=float("nan")))
        with self.assertRaises(ValueError):
            lab.simulate(FIXTURE, config(cache_enabled="false"))
        with self.assertRaises(ValueError):
            lab.simulate(FIXTURE, config(service_model=[]))

    def test_result_has_no_live_service_claim(self) -> None:
        import hashlib

        raw = (ROOT / "synthetic_serving_trace.json").read_bytes()
        result = lab.analyze_fixture(FIXTURE, hashlib.sha256(raw).hexdigest())
        self.assertFalse(result["model_quality_evaluated"])
        self.assertEqual(result["live_model_calls"], 0)
        self.assertEqual(result["external_http_requests"], 0)
        self.assertFalse(result["gpu_used"])
        self.assertEqual(result["fixture_sha256"], hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    unittest.main()
