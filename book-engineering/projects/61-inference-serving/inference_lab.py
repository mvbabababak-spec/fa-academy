"""Analyze normalized, per-request inference traces and estimate dense KV-cache bytes.

This tool performs deterministic arithmetic on its input trace. It does not load
or serve a model, connect to an inference engine, or benchmark hardware.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
VALID_STATUSES = {"ok", "error", "timeout"}


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _nonnegative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def estimate_kv_cache_bytes(
    *,
    layers: int,
    kv_heads: int,
    head_dim: int,
    bytes_per_element: int,
    tokens: int,
    sequences: int = 1,
) -> int:
    """Estimate dense full-attention K/V payload bytes, excluding runtime overhead."""
    values = {
        "layers": layers,
        "kv_heads": kv_heads,
        "head_dim": head_dim,
        "bytes_per_element": bytes_per_element,
        "tokens": tokens,
        "sequences": sequences,
    }
    for name, value in values.items():
        _positive_int(value, name)
    return 2 * layers * kv_heads * head_dim * bytes_per_element * tokens * sequences


def nearest_rank_percentile(values: list[float], percentile: float) -> float:
    """Return the nearest-rank percentile; this is descriptive, not an interval."""
    if not values:
        raise ValueError("percentile requires at least one value")
    percentile = _finite_number(percentile, "percentile")
    if not 0 <= percentile <= 100:
        raise ValueError("percentile must be between 0 and 100")
    ordered = sorted(_finite_number(value, "sample value") for value in values)
    rank = max(1, math.ceil(percentile * len(ordered) / 100))
    return ordered[rank - 1]


def validate_fixture(fixture: dict[str, Any]) -> None:
    """Validate the small, normalized trace schema used by the project."""
    if not isinstance(fixture, dict):
        raise ValueError("fixture root must be an object")
    if fixture.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if not isinstance(fixture.get("fixture_id"), str) or not fixture["fixture_id"].strip():
        raise ValueError("fixture_id must be a non-empty string")
    if not isinstance(fixture.get("label_source"), str) or not fixture["label_source"].strip():
        raise ValueError("label_source must be a non-empty string")

    profile = fixture.get("kv_profile")
    if not isinstance(profile, dict):
        raise ValueError("kv_profile must be an object")
    for key in ("layers", "kv_heads", "head_dim", "bytes_per_element", "context_tokens", "concurrent_sequences"):
        _positive_int(profile.get(key), f"kv_profile.{key}")

    runs = fixture.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("runs must be a non-empty list")
    run_ids: set[str] = set()
    for run_index, run in enumerate(runs, 1):
        prefix = f"runs[{run_index}]"
        if not isinstance(run, dict):
            raise ValueError(f"{prefix} must be an object")
        run_id = run.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip() or run_id in run_ids:
            raise ValueError(f"{prefix}.run_id must be unique and non-empty")
        run_ids.add(run_id)
        if not isinstance(run.get("runtime"), str) or not run["runtime"].strip():
            raise ValueError(f"{prefix}.runtime must be a non-empty string")
        if not isinstance(run.get("configuration"), dict):
            raise ValueError(f"{prefix}.configuration must be an object")
        window_ms = _finite_number(run.get("window_ms"), f"{prefix}.window_ms")
        if window_ms <= 0:
            raise ValueError(f"{prefix}.window_ms must be positive")
        requests = run.get("requests")
        if not isinstance(requests, list) or not requests:
            raise ValueError(f"{prefix}.requests must be a non-empty list")

        request_ids: set[str] = set()
        for request_index, request in enumerate(requests, 1):
            request_prefix = f"{prefix}.requests[{request_index}]"
            if not isinstance(request, dict):
                raise ValueError(f"{request_prefix} must be an object")
            request_id = request.get("request_id")
            if not isinstance(request_id, str) or not request_id.strip() or request_id in request_ids:
                raise ValueError(f"{request_prefix}.request_id must be unique and non-empty")
            request_ids.add(request_id)
            status = request.get("status")
            if not isinstance(status, str) or status not in VALID_STATUSES:
                raise ValueError(f"{request_prefix}.status must be one of {sorted(VALID_STATUSES)}")
            arrival_ms = _finite_number(request.get("arrival_ms"), f"{request_prefix}.arrival_ms")
            finish_ms = _finite_number(request.get("finish_ms"), f"{request_prefix}.finish_ms")
            prompt_tokens = _nonnegative_int(request.get("prompt_tokens"), f"{request_prefix}.prompt_tokens")
            if not 0 <= arrival_ms <= finish_ms <= window_ms:
                raise ValueError(f"{request_prefix} timestamps must satisfy 0 <= arrival <= finish <= window")

            first_output_ms = request.get("first_output_ms")
            completion_tokens = request.get("completion_tokens")
            if status == "ok":
                first_output_ms = _finite_number(first_output_ms, f"{request_prefix}.first_output_ms")
                completion_tokens = _positive_int(completion_tokens, f"{request_prefix}.completion_tokens")
                if not arrival_ms <= first_output_ms <= finish_ms:
                    raise ValueError(f"{request_prefix} timestamps must satisfy arrival <= first output <= finish")
            else:
                if first_output_ms is not None:
                    first_output_ms = _finite_number(first_output_ms, f"{request_prefix}.first_output_ms")
                    if not arrival_ms <= first_output_ms <= finish_ms:
                        raise ValueError(f"{request_prefix}.first_output_ms must be null or within the request")
                if completion_tokens is not None:
                    _nonnegative_int(completion_tokens, f"{request_prefix}.completion_tokens")


def _metric_summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "p50_ms": None, "p95_ms": None}
    return {
        "count": len(values),
        "p50_ms": nearest_rank_percentile(values, 50),
        "p95_ms": nearest_rank_percentile(values, 95),
    }


def summarize_run(run: dict[str, Any]) -> dict[str, Any]:
    """Summarize one validated run; latency percentiles include successful requests only."""
    requests = run["requests"]
    successful = [request for request in requests if request["status"] == "ok"]
    failed = len(requests) - len(successful)
    ttft_ms = [request["first_output_ms"] - request["arrival_ms"] for request in successful]
    e2e_ms = [request["finish_ms"] - request["arrival_ms"] for request in successful]
    tpot_ms = [
        (request["finish_ms"] - request["first_output_ms"]) / (request["completion_tokens"] - 1)
        for request in successful
        if request["completion_tokens"] > 1
    ]
    window_s = run["window_ms"] / 1000
    completion_tokens = sum(request["completion_tokens"] for request in successful)
    prompt_tokens = sum(request["prompt_tokens"] for request in successful)
    return {
        "run_id": run["run_id"],
        "runtime": run["runtime"],
        "configuration": run["configuration"],
        "measurement_window_ms": run["window_ms"],
        "requests": {
            "attempted": len(requests),
            "successful": len(successful),
            "failed_or_timed_out": failed,
            "error_rate": failed / len(requests),
            "successful_requests_per_s": len(successful) / window_s,
        },
        "tokens_per_s": {
            "prompt": prompt_tokens / window_s,
            "completion": completion_tokens / window_s,
        },
        "latency": {
            "ttft": _metric_summary(ttft_ms),
            "end_to_end": _metric_summary(e2e_ms),
            "estimated_tpot": _metric_summary(tpot_ms),
        },
        "tpot_definition": "(finish_ms - first_output_ms) / (completion_tokens - 1); client/trace estimate",
        "percentile_method": "nearest rank; descriptive only, not a confidence interval",
    }


def analyze_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    validate_fixture(fixture)
    profile = fixture["kv_profile"]
    per_sequence_bytes = estimate_kv_cache_bytes(
        layers=profile["layers"],
        kv_heads=profile["kv_heads"],
        head_dim=profile["head_dim"],
        bytes_per_element=profile["bytes_per_element"],
        tokens=profile["context_tokens"],
    )
    total_cache_bytes = estimate_kv_cache_bytes(
        layers=profile["layers"],
        kv_heads=profile["kv_heads"],
        head_dim=profile["head_dim"],
        bytes_per_element=profile["bytes_per_element"],
        tokens=profile["context_tokens"],
        sequences=profile["concurrent_sequences"],
    )
    return {
        "schema_version": 1,
        "fixture_id": fixture["fixture_id"],
        "label_source": fixture["label_source"],
        "scope": fixture.get("scope", {}),
        "kv_cache_estimate": {
            "bytes_per_token": estimate_kv_cache_bytes(
                layers=profile["layers"],
                kv_heads=profile["kv_heads"],
                head_dim=profile["head_dim"],
                bytes_per_element=profile["bytes_per_element"],
                tokens=1,
            ),
            "tokens_per_sequence": profile["context_tokens"],
            "concurrent_sequences": profile["concurrent_sequences"],
            "bytes_per_sequence": per_sequence_bytes,
            "bytes_for_concurrency": total_cache_bytes,
            "GiB_for_concurrency": total_cache_bytes / (1024**3),
            "excludes": [
                "model weights and non-KV activations",
                "allocator fragmentation and block metadata",
                "runtime workspaces, graph capture and temporary buffers",
                "sliding-window or architecture-specific cache savings",
            ],
        },
        "runs": [summarize_run(run) for run in fixture["runs"]],
    }


def run(fixture_path: Path) -> dict[str, Any]:
    raw = fixture_path.read_bytes()
    fixture = json.loads(raw)
    result = analyze_fixture(fixture)
    result["fixture_sha256"] = hashlib.sha256(raw).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a normalized inference trace and dense KV-cache estimate")
    parser.add_argument("--fixture", type=Path, default=ROOT / "sample_trace.json")
    parser.add_argument("--output", type=Path, default=Path("-"), help="JSON output path, or - for stdout")
    args = parser.parse_args()
    try:
        result = run(args.fixture)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if str(args.output) == "-":
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote deterministic analysis to {args.output}")


if __name__ == "__main__":
    main()
