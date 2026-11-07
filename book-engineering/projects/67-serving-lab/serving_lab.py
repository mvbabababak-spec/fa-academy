"""Synthetic service-level queue, microbatch, and exact-response-cache simulator.

This module is a deterministic discrete-event teaching model. It does not load
an inference runtime, model, GPU, or network client.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
import hashlib
import json
import math
from pathlib import Path
from typing import Any

FIXTURE_ID = "v5-ch06-serving-synthetic-v1"
DEFAULT_FIXTURE = Path(__file__).with_name("synthetic_serving_trace.json")

SERVICE_MODEL = {
    "launch_overhead_ms": 5.0,
    "prefill_ms_per_prompt_token": 0.4,
    "decode_step_base_ms": 4.0,
    "decode_step_ms_per_extra_sequence": 0.75,
    "cache_lookup_ms": 1.5,
}

CONFIGURATIONS = [
    {
        "name": "baseline_one_at_a_time",
        "batch_size": 1,
        "batch_wait_ms": 0.0,
        "max_queue_size": 8,
        "cache_enabled": False,
        "max_cache_entries": 0,
        "max_cache_bytes": 0,
    },
    {
        "name": "microbatch_only",
        "batch_size": 4,
        "batch_wait_ms": 12.0,
        "max_queue_size": 8,
        "cache_enabled": False,
        "max_cache_entries": 0,
        "max_cache_bytes": 0,
    },
    {
        "name": "exact_response_cache_only",
        "batch_size": 1,
        "batch_wait_ms": 0.0,
        "max_queue_size": 8,
        "cache_enabled": True,
        "max_cache_entries": 16,
        "max_cache_bytes": 4096,
    },
    {
        "name": "microbatch_plus_exact_cache",
        "batch_size": 4,
        "batch_wait_ms": 12.0,
        "max_queue_size": 8,
        "cache_enabled": True,
        "max_cache_entries": 16,
        "max_cache_bytes": 4096,
    },
]


class FixtureError(ValueError):
    """Raised when the synthetic request trace violates its schema."""


def _finite_number(value: Any, name: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise ValueError(f"{name} must be finite and >= {minimum}")
    return result


def _positive_integer(value: Any, name: str, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def response_cache_key(request: dict[str, Any]) -> str:
    """Build an exact fixture key from all response-affecting dimensions.

    ``prompt_id`` stands for the exact, versioned tokenized request in this
    synthetic trace. A real product must define its own safe scope and key.
    """
    required = (
        "model_revision", "prompt_id", "decoding", "locale", "context_revision"
    )
    missing = [field for field in required if field not in request]
    if missing:
        raise ValueError(f"request is missing cache-key fields: {', '.join(missing)}")
    payload = {field: request[field] for field in required}
    try:
        return json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ValueError("cache-key values must be finite JSON data") from error


def little_average_in_system(arrival_rate_per_second: float, mean_time_seconds: float) -> float:
    """Return L = lambda * W for stable long-run averages."""
    rate = _finite_number(arrival_rate_per_second, "arrival_rate_per_second")
    duration = _finite_number(mean_time_seconds, "mean_time_seconds")
    return rate * duration


def nearest_rank_percentile(values: list[float], percentile: float) -> float | None:
    """Nearest-rank percentile; returns None for an empty sample."""
    if not values:
        return None
    p = _finite_number(percentile, "percentile", 0.0)
    if p > 100.0:
        raise ValueError("percentile must be <= 100")
    ordered = sorted(float(value) for value in values)
    rank = max(1, math.ceil((p / 100.0) * len(ordered)))
    return ordered[rank - 1]


def validate_fixture(fixture: dict[str, Any]) -> None:
    if not isinstance(fixture, dict) or fixture.get("fixture_id") != FIXTURE_ID:
        raise FixtureError(f"fixture_id must equal {FIXTURE_ID!r}")
    if fixture.get("synthetic") is not True:
        raise FixtureError("fixture must be explicitly marked synthetic")
    requests = fixture.get("requests")
    if not isinstance(requests, list) or not requests:
        raise FixtureError("requests must be a nonempty list")
    ids: set[str] = set()
    for index, request in enumerate(requests):
        label = f"requests[{index}]"
        if not isinstance(request, dict):
            raise FixtureError(f"{label} must be an object")
        request_id = request.get("request_id")
        if not isinstance(request_id, str) or not request_id:
            raise FixtureError(f"{label}.request_id must be a nonempty string")
        if request_id in ids:
            raise FixtureError(f"duplicate request_id: {request_id}")
        ids.add(request_id)
        try:
            _finite_number(request.get("arrival_ms"), f"{label}.arrival_ms")
            _positive_integer(request.get("prompt_tokens"), f"{label}.prompt_tokens")
            _positive_integer(request.get("output_tokens"), f"{label}.output_tokens")
            _positive_integer(request.get("deadline_ms"), f"{label}.deadline_ms")
        except ValueError as error:
            raise FixtureError(str(error)) from error
        for field in ("model_revision", "prompt_id", "locale", "context_revision"):
            if not isinstance(request.get(field), str) or not request[field]:
                raise FixtureError(f"{label}.{field} must be a nonempty string")
        if not isinstance(request.get("decoding"), dict):
            raise FixtureError(f"{label}.decoding must be an object")
        if not isinstance(request.get("expected_output"), str) or not request["expected_output"]:
            raise FixtureError(f"{label}.expected_output must be a nonempty string")
        try:
            response_cache_key(request)
        except ValueError as error:
            raise FixtureError(f"{label}: {error}") from error


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    checked = dict(config)
    if not isinstance(checked.get("name"), str) or not checked["name"]:
        raise ValueError("config.name must be a nonempty string")
    checked["batch_size"] = _positive_integer(checked.get("batch_size"), "batch_size")
    checked["max_queue_size"] = _positive_integer(checked.get("max_queue_size"), "max_queue_size")
    checked["batch_wait_ms"] = _finite_number(checked.get("batch_wait_ms"), "batch_wait_ms")
    cache_enabled = checked.get("cache_enabled")
    if not isinstance(cache_enabled, bool):
        raise ValueError("cache_enabled must be a boolean")
    checked["cache_enabled"] = cache_enabled
    checked["max_cache_entries"] = _positive_integer(
        checked.get("max_cache_entries"), "max_cache_entries", minimum=0
    )
    checked["max_cache_bytes"] = _positive_integer(
        checked.get("max_cache_bytes"), "max_cache_bytes", minimum=0
    )
    service_overrides = checked.get("service_model", {})
    if not isinstance(service_overrides, dict):
        raise ValueError("service_model must be an object")
    service = dict(SERVICE_MODEL)
    service.update(service_overrides)
    for field in (
        "launch_overhead_ms", "prefill_ms_per_prompt_token",
        "decode_step_base_ms", "decode_step_ms_per_extra_sequence", "cache_lookup_ms",
    ):
        service[field] = _finite_number(service[field], f"service_model.{field}")
    checked["service_model"] = service
    if not checked["cache_enabled"]:
        checked["max_cache_entries"] = 0
        checked["max_cache_bytes"] = 0
    return checked


class ResponseCache:
    """Small LRU response cache with explicit entry and UTF-8 payload limits."""

    def __init__(self, max_entries: int, max_bytes: int) -> None:
        self.max_entries = max_entries
        self.max_bytes = max_bytes
        self.entries: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.payload_bytes = 0
        self.peak_payload_bytes = 0

    def get(self, key: str, now_ms: float) -> str | None:
        entry = self.entries.get(key)
        if entry is None or entry["ready_at_ms"] > now_ms:
            return None
        self.entries.move_to_end(key)
        return entry["response"]

    def store(self, key: str, response: str, ready_at_ms: float) -> bool:
        size = len(key.encode("utf-8")) + len(response.encode("utf-8"))
        if self.max_entries == 0 or self.max_bytes == 0 or size > self.max_bytes:
            return False
        old = self.entries.pop(key, None)
        if old is not None:
            self.payload_bytes -= old["payload_bytes"]
        self.entries[key] = {
            "response": response,
            "ready_at_ms": ready_at_ms,
            "payload_bytes": size,
        }
        self.payload_bytes += size
        self.entries.move_to_end(key)
        while len(self.entries) > self.max_entries or self.payload_bytes > self.max_bytes:
            _, evicted = self.entries.popitem(last=False)
            self.payload_bytes -= evicted["payload_bytes"]
        self.peak_payload_bytes = max(self.peak_payload_bytes, self.payload_bytes)
        return key in self.entries


def _round_ms(value: float | None) -> float | None:
    return None if value is None else round(float(value), 3)


def simulate(fixture: dict[str, Any], raw_config: dict[str, Any]) -> dict[str, Any]:
    """Simulate one FIFO service worker, microbatch wait, and optional exact cache."""
    validate_fixture(fixture)
    config = validate_config(raw_config)
    requests = sorted(
        fixture["requests"], key=lambda request: (request["arrival_ms"], request["request_id"])
    )
    waiting: list[dict[str, Any]] = []
    records: dict[str, dict[str, Any]] = {}
    cache = ResponseCache(config["max_cache_entries"], config["max_cache_bytes"])
    queue_peak = 0
    batch_summaries: list[dict[str, Any]] = []
    next_batch_number = 1
    index = 0
    now_ms = 0.0
    active: dict[str, Any] | None = None
    service = config["service_model"]

    def admit(request: dict[str, Any], arrival_ms: float) -> None:
        nonlocal queue_peak
        key = response_cache_key(request)
        if config["cache_enabled"]:
            cached_response = cache.get(key, arrival_ms)
            if cached_response is not None:
                completion_ms = arrival_ms + service["cache_lookup_ms"]
                latency_ms = completion_ms - arrival_ms
                matches = cached_response == request["expected_output"]
                records[request["request_id"]] = {
                    "request_id": request["request_id"],
                    "arrival_ms": _round_ms(arrival_ms),
                    "status": "cache_hit",
                    "cache_hit": True,
                    "model_compute": False,
                    "batch_id": None,
                    "batch_size": 0,
                    "queue_wait_ms": 0.0,
                    "ttft_ms": _round_ms(latency_ms),
                    "response_latency_ms": _round_ms(latency_ms),
                    "completed_at_ms": _round_ms(completion_ms),
                    "deadline_ms": request["deadline_ms"],
                    "deadline_missed": latency_ms > request["deadline_ms"],
                    "output_matches_reference": matches,
                }
                return

        if len(waiting) >= config["max_queue_size"]:
            records[request["request_id"]] = {
                "request_id": request["request_id"],
                "arrival_ms": _round_ms(arrival_ms),
                "status": "rejected_queue_full",
                "cache_hit": False,
                "model_compute": False,
                "batch_id": None,
                "batch_size": 0,
                "queue_wait_ms": None,
                "ttft_ms": None,
                "response_latency_ms": None,
                "completed_at_ms": None,
                "deadline_ms": request["deadline_ms"],
                "deadline_missed": None,
                "output_matches_reference": None,
            }
            return

        waiting.append(request)
        queue_peak = max(queue_peak, len(waiting))

    def start_batch(batch: list[dict[str, Any]], start_ms: float) -> dict[str, Any]:
        nonlocal next_batch_number
        batch_id = f"batch-{next_batch_number:03d}"
        next_batch_number += 1
        batch_size = len(batch)
        max_prompt_tokens = max(request["prompt_tokens"] for request in batch)
        prefill_ms = (
            service["launch_overhead_ms"]
            + max_prompt_tokens * service["prefill_ms_per_prompt_token"]
        )
        decode_step_ms = (
            service["decode_step_base_ms"]
            + max(0, batch_size - 1) * service["decode_step_ms_per_extra_sequence"]
        )
        events = []
        for request in batch:
            first_token_ms = start_ms + prefill_ms
            completion_ms = first_token_ms + request["output_tokens"] * decode_step_ms
            response_latency_ms = completion_ms - request["arrival_ms"]
            queue_wait_ms = start_ms - request["arrival_ms"]
            records[request["request_id"]] = {
                "request_id": request["request_id"],
                "arrival_ms": _round_ms(request["arrival_ms"]),
                "status": "model_response",
                "cache_hit": False,
                "model_compute": True,
                "batch_id": batch_id,
                "batch_size": batch_size,
                "queue_wait_ms": _round_ms(queue_wait_ms),
                "ttft_ms": _round_ms(first_token_ms - request["arrival_ms"]),
                "response_latency_ms": _round_ms(response_latency_ms),
                "completed_at_ms": _round_ms(completion_ms),
                "deadline_ms": request["deadline_ms"],
                "deadline_missed": response_latency_ms > request["deadline_ms"],
                # The mock computation returns the fixed reference string. This
                # is a transport/integrity check, not a model-quality score.
                "output_matches_reference": True,
            }
            events.append((completion_ms, request["request_id"], request, response_cache_key(request)))
        events.sort(key=lambda event: (event[0], event[1]))
        batch_end = max(event[0] for event in events)
        batch_summaries.append({
            "batch_id": batch_id,
            "batch_size": batch_size,
            "start_ms": _round_ms(start_ms),
            "prefill_assumption_ms": _round_ms(prefill_ms),
            "decode_step_assumption_ms": _round_ms(decode_step_ms),
            "engine_release_ms": _round_ms(batch_end),
        })
        return {"events": events, "next_event": 0, "end_ms": batch_end}

    while index < len(requests) or waiting or active is not None:
        if active is None:
            if not waiting:
                if index >= len(requests):
                    break
                now_ms = max(now_ms, float(requests[index]["arrival_ms"]))
                admit(requests[index], now_ms)
                index += 1
                continue

            first_waiter = waiting[0]
            dispatch_deadline = max(
                now_ms, float(first_waiter["arrival_ms"]) + config["batch_wait_ms"]
            )
            while (
                len(waiting) < config["batch_size"]
                and index < len(requests)
                and float(requests[index]["arrival_ms"]) <= dispatch_deadline
            ):
                now_ms = float(requests[index]["arrival_ms"])
                admit(requests[index], now_ms)
                index += 1

            if len(waiting) >= config["batch_size"]:
                start_ms = now_ms
            else:
                start_ms = dispatch_deadline
                now_ms = start_ms
            take = min(config["batch_size"], len(waiting))
            batch = waiting[:take]
            del waiting[:take]
            active = start_batch(batch, start_ms)
            continue

        completion_index = active["next_event"]
        next_completion_ms = active["events"][completion_index][0]
        next_arrival_ms = (
            float(requests[index]["arrival_ms"]) if index < len(requests) else math.inf
        )
        if next_completion_ms <= next_arrival_ms:
            now_ms = next_completion_ms
            _, request_id, request, key = active["events"][completion_index]
            if config["cache_enabled"]:
                cache.store(key, request["expected_output"], now_ms)
            active["next_event"] += 1
            if active["next_event"] >= len(active["events"]):
                active = None
        else:
            now_ms = next_arrival_ms
            admit(requests[index], now_ms)
            index += 1

    if len(records) != len(requests):
        raise RuntimeError("simulation ended before every request received a terminal status")

    successful = [record for record in records.values() if record["status"] in {"model_response", "cache_hit"}]
    model_responses = [record for record in successful if record["model_compute"]]
    correct = [record for record in successful if record["output_matches_reference"] is True]
    rejected = [record for record in records.values() if record["status"] == "rejected_queue_full"]
    latency_values = [record["response_latency_ms"] for record in successful]
    ttft_values = [record["ttft_ms"] for record in model_responses]
    queue_wait_values = [record["queue_wait_ms"] for record in model_responses]
    first_arrival = min(float(request["arrival_ms"]) for request in requests)
    last_completion = max(float(record["completed_at_ms"]) for record in successful)
    elapsed_ms = max(0.0, last_completion - first_arrival)
    elapsed_seconds = elapsed_ms / 1000.0
    successful_tokens = sum(
        request["output_tokens"]
        for request in requests
        if records[request["request_id"]]["status"] in {"model_response", "cache_hit"}
    )
    fixture_match_rate = len(correct) / elapsed_seconds if elapsed_seconds > 0 else None
    response_rate = len(successful) / elapsed_seconds if elapsed_seconds > 0 else None
    token_rate = successful_tokens / elapsed_seconds if elapsed_seconds > 0 else None

    return {
        "name": config["name"],
        "batch_size_limit": config["batch_size"],
        "batch_wait_ms_limit": _round_ms(config["batch_wait_ms"]),
        "max_queue_size": config["max_queue_size"],
        "response_cache_enabled": config["cache_enabled"],
        "max_cache_entries": config["max_cache_entries"],
        "max_cache_payload_bytes": config["max_cache_bytes"],
        "request_count": len(requests),
        "successful_responses": len(successful),
        "queue_rejections": len(rejected),
        "model_compute_requests": len(model_responses),
        "response_cache_hits": sum(record["cache_hit"] for record in successful),
        "output_integrity_matches": len(correct),
        "output_integrity_rate": _round_ms(len(correct) / len(successful) if successful else 0.0),
        "deadline_misses": sum(record["deadline_missed"] is True for record in successful),
        "max_waiting_queue_depth": queue_peak,
        "model_batches": len(batch_summaries),
        "max_batch_observed": max((batch["batch_size"] for batch in batch_summaries), default=0),
        "response_latency_p50_ms": _round_ms(nearest_rank_percentile(latency_values, 50)),
        "response_latency_p95_ms": _round_ms(nearest_rank_percentile(latency_values, 95)),
        "model_ttft_p95_ms": _round_ms(nearest_rank_percentile(ttft_values, 95)),
        "queue_wait_p95_ms": _round_ms(nearest_rank_percentile(queue_wait_values, 95)),
        "trace_elapsed_ms": _round_ms(elapsed_ms),
        "completed_responses_per_second": _round_ms(response_rate),
        "fixture_correct_responses_per_second": _round_ms(fixture_match_rate),
        "fixture_output_tokens_per_second": _round_ms(token_rate),
        "response_cache_payload_bytes_final": cache.payload_bytes,
        "response_cache_payload_bytes_peak": cache.peak_payload_bytes,
        "batch_schedule": batch_summaries,
        "per_request": [records[request["request_id"]] for request in requests],
    }


def analyze_fixture(fixture: dict[str, Any], fixture_sha256: str) -> dict[str, Any]:
    validate_fixture(fixture)
    keys = {response_cache_key(request) for request in fixture["requests"]}
    runs = [simulate(fixture, config) for config in CONFIGURATIONS]
    return {
        "project_id": FIXTURE_ID,
        "fixture_id": FIXTURE_ID,
        "fixture_sha256": fixture_sha256,
        "synthetic": True,
        "request_count": len(fixture["requests"]),
        "unique_exact_cache_keys": len(keys),
        "run_count": len(runs),
        "runs": runs,
        "external_http_requests": 0,
        "live_model_calls": 0,
        "gpu_used": False,
        "production_trace_used": False,
        "personal_records": 0,
        "model_quality_evaluated": False,
        "scope": (
            "Deterministic discrete-event illustration of one synthetic service worker, "
            "bounded FIFO waiting queue, optional microbatching, and bounded exact-response cache. "
            "The model response is a fixed fixture string; no inference runtime is executed."
        ),
        "limitations": [
            "All arrivals, token counts, reference strings, capacities, and service-time coefficients are invented; no production trace is represented.",
            "The single-worker service-time formula is a teaching assumption, not a GPU, model, vLLM, or hardware benchmark.",
            "The mock returns fixture reference strings, so output-integrity equality is not model quality, factuality, safety, or human evaluation.",
            "The response-cache payload estimate counts UTF-8 key and body bytes only; it omits Python object, allocator, index, and process overhead.",
            "Cache freshness, personalized or tenant isolation, authorization, rate limiting, telemetry, cancellation, retry policy, deployment, and autoscaling are not implemented.",
            "The simulator has one worker, FIFO queueing, no in-flight duplicate coalescing, and no stochastic variation or confidence interval."
        ],
    }


def analyze_file(fixture_path: Path) -> dict[str, Any]:
    raw = fixture_path.read_bytes()
    fixture = json.loads(raw.decode("utf-8"))
    return analyze_fixture(fixture, hashlib.sha256(raw).hexdigest())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate a synthetic service queue, microbatch policy, and exact response cache"
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, default=Path("-"))
    args = parser.parse_args()
    result = analyze_file(args.fixture)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if str(args.output) == "-":
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
