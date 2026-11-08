#!/usr/bin/env python3
"""Deterministic release-gate simulator for synthetic AI deployment evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
REQUIRED_COMPONENTS = ("service", "model", "tokenizer", "preprocessing", "runtime")
DEFAULT_FIXTURE = Path(__file__).with_name("synthetic_release_scenarios.json")


def canonical_bytes(value: Any) -> bytes:
    """Return stable JSON bytes for this exercise's synthetic manifest."""
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_digest(value: Any) -> str:
    """Hash a JSON value using the exercise's canonical serialization."""
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def is_digest(value: Any) -> bool:
    return isinstance(value, str) and DIGEST_PATTERN.fullmatch(value) is not None


def _current_release_errors(current: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(current, dict):
        return ["current_release_missing"]
    if not isinstance(current.get("release_id"), str) or not current["release_id"].strip():
        errors.append("current_release_id_missing")
    components = current.get("components")
    if not isinstance(components, dict) or not all(key in components for key in REQUIRED_COMPONENTS):
        errors.append("current_release_components_incomplete")
    elif current.get("bundle_digest") != sha256_digest(components):
        errors.append("current_release_digest_mismatch")
    if not is_digest(current.get("bundle_digest")):
        errors.append("current_release_digest_invalid")
    return errors


def _preflight_errors(
    scenario: Any, current: Any, policy: Any
) -> list[str]:
    errors: list[str] = []
    if not isinstance(scenario, dict):
        return ["scenario_not_object"]
    if not isinstance(policy, dict):
        return ["policy_not_object"]
    errors.extend(_current_release_errors(current))

    name = scenario.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("scenario_name_missing")
    if scenario.get("target") not in {"staging", "production"}:
        errors.append("target_not_supported")

    candidate = scenario.get("candidate")
    if not isinstance(candidate, dict):
        return errors + ["candidate_not_object"]
    release_id = candidate.get("release_id")
    if not isinstance(release_id, str) or not release_id.strip():
        errors.append("candidate_release_id_missing")
    elif isinstance(current, dict) and release_id == current.get("release_id"):
        errors.append("candidate_release_id_not_new")

    components = candidate.get("components")
    if not isinstance(components, dict) or not all(key in components for key in REQUIRED_COMPONENTS):
        errors.append("candidate_components_incomplete")
    else:
        computed_digest = sha256_digest(components)
        if not is_digest(candidate.get("bundle_digest")):
            errors.append("candidate_digest_invalid")
        elif candidate.get("bundle_digest") != computed_digest:
            errors.append("candidate_digest_mismatch")

    provenance = candidate.get("provenance")
    if not isinstance(provenance, dict) or provenance.get("verified") is not True:
        errors.append("provenance_not_verified")
    elif candidate.get("bundle_digest") != provenance.get("subject_digest"):
        errors.append("provenance_subject_mismatch")

    required_gates = policy.get("required_gates")
    gates = candidate.get("gates")
    if not isinstance(required_gates, list) or not required_gates:
        errors.append("required_gates_policy_missing")
    elif not isinstance(gates, dict):
        errors.append("candidate_gates_missing")
    else:
        errors.extend(
            f"gate_not_passed:{gate}"
            for gate in required_gates
            if gates.get(gate) != "passed"
        )

    if policy.get("require_backward_compatibility", True) and candidate.get("backward_compatible") is not True:
        errors.append("rollback_compatibility_not_confirmed")
    if scenario.get("target") == "production" and policy.get("require_production_approval", True):
        if scenario.get("approval_status") != "approved":
            errors.append("production_approval_missing")

    stages = policy.get("rollout_stages_percent")
    if (
        not isinstance(stages, list)
        or not stages
        or any(not isinstance(value, int) or isinstance(value, bool) for value in stages)
        or stages != sorted(set(stages))
        or stages[-1] != 100
        or stages[0] <= 0
    ):
        errors.append("rollout_policy_invalid")

    if isinstance(current, dict) and candidate.get("bundle_digest") == current.get("bundle_digest"):
        errors.append("candidate_matches_current_release")
    return errors


def _observation_error(observation: Any) -> str | None:
    if not isinstance(observation, dict):
        return "observation_not_object"
    requests = observation.get("requests")
    errors = observation.get("errors")
    p95_ms = observation.get("p95_ms")
    traffic_percent = observation.get("traffic_percent")
    if not isinstance(traffic_percent, int) or isinstance(traffic_percent, bool):
        return "traffic_percent_invalid"
    if not isinstance(requests, int) or isinstance(requests, bool) or requests <= 0:
        return "request_count_invalid"
    if not isinstance(errors, int) or isinstance(errors, bool) or errors < 0 or errors > requests:
        return "error_count_invalid"
    if not isinstance(p95_ms, (int, float)) or isinstance(p95_ms, bool) or not math.isfinite(p95_ms) or p95_ms < 0:
        return "p95_latency_invalid"
    return None


def evaluate_scenario(scenario: dict[str, Any], current: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a fixture scenario without making any external deployment call."""
    errors = _preflight_errors(scenario, current, policy)
    current_id = current.get("release_id") if isinstance(current, dict) else None
    if errors:
        return {
            "scenario": scenario.get("name") if isinstance(scenario, dict) else None,
            "decision": "blocked",
            "preflight_passed": False,
            "blocked_reasons": errors,
            "active_release_id": current_id,
            "promoted_stages_percent": [],
            "rollback_performed": False,
            "simulated_only": True,
        }

    candidate = scenario["candidate"]
    expected_stages = policy["rollout_stages_percent"]
    observations = scenario.get("observations")
    if not isinstance(observations, list):
        observations = []
    observed_stages = [item.get("traffic_percent") if isinstance(item, dict) else None for item in observations]
    if observed_stages != expected_stages:
        return {
            "scenario": scenario["name"],
            "decision": "blocked",
            "preflight_passed": True,
            "blocked_reasons": ["rollout_observations_do_not_match_policy"],
            "active_release_id": current_id,
            "promoted_stages_percent": [],
            "rollback_performed": False,
            "simulated_only": True,
        }

    promoted: list[int] = []
    minimum_requests = policy.get("minimum_requests_per_stage")
    max_error_rate = policy.get("max_error_rate")
    max_p95_ms = policy.get("max_p95_ms")
    if (
        not isinstance(minimum_requests, int) or isinstance(minimum_requests, bool) or minimum_requests <= 0
        or not isinstance(max_error_rate, (int, float)) or isinstance(max_error_rate, bool)
        or not 0 <= max_error_rate <= 1
        or not isinstance(max_p95_ms, (int, float)) or isinstance(max_p95_ms, bool) or max_p95_ms <= 0
    ):
        return {
            "scenario": scenario["name"],
            "decision": "blocked",
            "preflight_passed": True,
            "blocked_reasons": ["health_policy_invalid"],
            "active_release_id": current_id,
            "promoted_stages_percent": [],
            "rollback_performed": False,
            "simulated_only": True,
        }

    for observation in observations:
        invalid = _observation_error(observation)
        if invalid:
            return {
                "scenario": scenario["name"],
                "decision": "blocked",
                "preflight_passed": True,
                "blocked_reasons": [invalid],
                "active_release_id": current_id,
                "promoted_stages_percent": promoted,
                "rollback_performed": False,
                "simulated_only": True,
            }
        stage = observation["traffic_percent"]
        if observation["requests"] < minimum_requests:
            return {
                "scenario": scenario["name"],
                "decision": "hold",
                "preflight_passed": True,
                "blocked_reasons": ["insufficient_canary_sample"],
                "active_release_id": current_id,
                "promoted_stages_percent": promoted,
                "held_at_percent": stage,
                "rollback_performed": False,
                "simulated_only": True,
            }
        error_rate = observation["errors"] / observation["requests"]
        if error_rate > max_error_rate:
            return {
                "scenario": scenario["name"],
                "decision": "rolled_back",
                "preflight_passed": True,
                "blocked_reasons": ["canary_error_rate_over_limit"],
                "active_release_id": current_id,
                "candidate_release_id": candidate["release_id"],
                "promoted_stages_percent": promoted,
                "failed_at_percent": stage,
                "observed_error_rate": round(error_rate, 6),
                "rollback_performed": True,
                "simulated_only": True,
            }
        if observation["p95_ms"] > max_p95_ms:
            return {
                "scenario": scenario["name"],
                "decision": "rolled_back",
                "preflight_passed": True,
                "blocked_reasons": ["canary_p95_over_limit"],
                "active_release_id": current_id,
                "candidate_release_id": candidate["release_id"],
                "promoted_stages_percent": promoted,
                "failed_at_percent": stage,
                "observed_p95_ms": observation["p95_ms"],
                "rollback_performed": True,
                "simulated_only": True,
            }
        promoted.append(stage)

    return {
        "scenario": scenario["name"],
        "decision": "promoted",
        "preflight_passed": True,
        "blocked_reasons": [],
        "active_release_id": candidate["release_id"],
        "candidate_release_id": candidate["release_id"],
        "previous_release_id": current_id,
        "promoted_stages_percent": promoted,
        "rollback_performed": False,
        "simulated_only": True,
    }


def run_fixture(payload: dict[str, Any], fixture_sha256: str) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("synthetic") is not True:
        raise ValueError("fixture must be a synthetic JSON object")
    fixture_id = payload.get("fixture_id")
    if not isinstance(fixture_id, str) or not fixture_id.strip():
        raise ValueError("fixture_id is required")
    current = payload.get("current_release")
    policy = payload.get("policy")
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("fixture must contain at least one scenario")
    names = [item.get("name") if isinstance(item, dict) else None for item in scenarios]
    if any(not isinstance(name, str) or not name.strip() for name in names) or len(names) != len(set(names)):
        raise ValueError("scenario names must be non-empty and unique")
    results = [evaluate_scenario(scenario, current, policy) for scenario in scenarios]
    decision_counts = {name: sum(result["decision"] == name for result in results) for name in ("blocked", "hold", "rolled_back", "promoted")}
    return {
        "project_id": fixture_id,
        "fixture_id": fixture_id,
        "fixture_sha256": fixture_sha256,
        "synthetic": True,
        "scenario_count": len(results),
        "decision_counts": decision_counts,
        "results": results,
        "external_network_requests": 0,
        "cloud_deployments": 0,
        "production_writes": 0,
        "model_inference_calls": 0,
        "gpu_used": False,
        "personal_records": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    args = parser.parse_args()
    try:
        raw = args.fixture.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        result = run_fixture(payload, hashlib.sha256(raw).hexdigest())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
