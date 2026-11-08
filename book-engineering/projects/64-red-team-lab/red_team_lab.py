"""Run a deterministic, synthetic check of selected AI security controls.

This program does not load or attack a language model, service, tool, or dataset.
It checks only the policy branches explicitly represented in its local fixture.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_FIXTURE = BASE_DIR / "synthetic_security_fixture.json"
DEFAULT_POLICY: dict[str, Any] = {
    "deny_synthetic_canary": True,
    "treat_retrieved_instructions_as_untrusted": True,
    "enforce_tool_scopes": True,
    "require_verified_data_provenance": True,
    "deny_membership_confirmation": True,
    "enforce_query_budget": True,
    "query_budget": 2,
}
CATEGORIES = {
    "direct_prompt_injection",
    "indirect_prompt_injection",
    "tool_scope",
    "data_poisoning",
    "membership_probe",
    "excessive_querying",
    "benign_public_read",
}
POLICY_KEYS = set(DEFAULT_POLICY)


def validate_fixture(data: dict[str, Any]) -> None:
    """Reject malformed or ambiguous fixture records before calculating results."""
    if not isinstance(data, dict) or not isinstance(data.get("fixture_id"), str):
        raise ValueError("fixture must contain a string fixture_id")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("fixture cases must be a non-empty list")
    ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each fixture case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("each fixture case needs a non-empty id")
        if case_id in ids:
            raise ValueError(f"duplicate case id: {case_id}")
        ids.add(case_id)
        if case.get("category") not in CATEGORIES:
            raise ValueError(f"unknown category in {case_id}: {case.get('category')!r}")
        if not isinstance(case.get("is_attack"), bool):
            raise ValueError(f"is_attack must be boolean in {case_id}")
        if not isinstance(case.get("expected_outcome"), str):
            raise ValueError(f"expected_outcome must be a string in {case_id}")
        if case.get("is_attack") and not isinstance(case.get("success_outcome"), str):
            raise ValueError(f"attack case needs a fixture-specific success_outcome in {case_id}")
        if not case.get("is_attack") and case.get("success_outcome") is not None:
            raise ValueError(f"benign case success_outcome must be null in {case_id}")
        if case["category"] == "excessive_querying":
            count = case.get("queries_in_window")
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise ValueError(f"queries_in_window must be a non-negative integer in {case_id}")
        if case["category"] == "tool_scope" and not isinstance(case.get("principal_scopes"), list):
            raise ValueError(f"principal_scopes must be a list in {case_id}")


def _effective_policy(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = DEFAULT_POLICY.copy()
    if overrides:
        unknown = set(overrides) - POLICY_KEYS
        if unknown:
            raise ValueError(f"unknown policy keys: {sorted(unknown)}")
        policy.update(overrides)
    for key in POLICY_KEYS - {"query_budget"}:
        if not isinstance(policy[key], bool):
            raise ValueError(f"policy {key} must be boolean")
    budget = policy["query_budget"]
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 0:
        raise ValueError("query_budget must be a non-negative integer")
    return policy


def decide(case: dict[str, Any], policy: dict[str, Any] | None = None) -> str:
    """Return the toy policy outcome for a fixture case; this is not model inference."""
    controls = _effective_policy(policy)
    category = case["category"]
    if category == "direct_prompt_injection":
        if case.get("asks_for_synthetic_canary") and controls["deny_synthetic_canary"]:
            return "blocked"
        return "canary_disclosed"
    if category == "indirect_prompt_injection":
        is_untrusted = case.get("instruction_origin") == "untrusted_retrieved_content"
        if is_untrusted and controls["treat_retrieved_instructions_as_untrusted"]:
            return "blocked"
        return "action_executed" if case.get("requests_tool_action") else "allowed"
    if category == "tool_scope":
        requested = case.get("requested_action")
        scopes = case.get("principal_scopes", [])
        if requested not in scopes and controls["enforce_tool_scopes"]:
            return "blocked"
        return "action_executed" if requested not in scopes else "allowed"
    if category == "data_poisoning":
        if not case.get("provenance_verified") and controls["require_verified_data_provenance"]:
            return "quarantined"
        return "sample_accepted"
    if category == "membership_probe":
        if case.get("requests_membership_confirmation") and controls["deny_membership_confirmation"]:
            return "blocked"
        return "membership_confirmed"
    if category == "excessive_querying":
        if (case.get("queries_in_window", 0) > controls["query_budget"]
                and controls["enforce_query_budget"]):
            return "rate_limited"
        return "query_served"
    if category == "benign_public_read":
        return "allowed"
    raise ValueError(f"unsupported category: {category!r}")


def analyze(data: dict[str, Any], fixture_bytes: bytes,
            policy: dict[str, Any] | None = None) -> dict[str, Any]:
    validate_fixture(data)
    controls = _effective_policy(policy)
    case_results = []
    for case in data["cases"]:
        observed = decide(case, controls)
        case_results.append({
            "id": case["id"],
            "category": case["category"],
            "is_attack": case["is_attack"],
            "expected_outcome": case["expected_outcome"],
            "observed_outcome": observed,
            "control_check_passed": observed == case["expected_outcome"],
            "simulated_goal_reached": bool(
                case["is_attack"] and observed == case.get("success_outcome")
            ),
        })
    attack_cases = [result for result in case_results if result["is_attack"]]
    goal_count = sum(result["simulated_goal_reached"] for result in attack_cases)
    passed = sum(result["control_check_passed"] for result in case_results)
    attempts = len(attack_cases)
    return {
        "fixture_id": data["fixture_id"],
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "policy_id": "synthetic-control-policy-v1",
        "case_count": len(case_results),
        "attack_case_count": attempts,
        "benign_control_count": len(case_results) - attempts,
        "control_checks_passed": passed,
        "control_checks_failed": len(case_results) - passed,
        "simulated_attack_goals_reached": goal_count,
        "simulated_attack_goal_rate": goal_count / attempts if attempts else None,
        "rate_limited_cases": sum(
            result["observed_outcome"] == "rate_limited" for result in case_results
        ),
        "cases": case_results,
        "scope": (
            "Deterministic decisions against seven synthetic policy cases only; "
            "not a red-team test of an AI model or deployed system."
        ),
        "limitations": [
            "No language model, classifier, API, network, external tool, model weight, training pipeline, or real dataset is executed.",
            "The fixture contains synthetic labels and no personal data, credentials, or production secrets.",
            "The simulated goal rate is computed from six hand-authored cases and is not an empirical attack-success rate.",
            "The query-budget case checks a local threshold branch only; it does not test model extraction, distributed accounts, or privacy leakage.",
            "A provenance flag is not a cryptographic signature or proof that data is safe, lawful, accurate, or unbiased.",
            "Passing these unit tests does not establish prompt-injection resistance, privacy, security, safety, or deployment readiness.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    args = parser.parse_args()
    fixture_bytes = args.fixture.read_bytes()
    data = json.loads(fixture_bytes.decode("utf-8"))
    result = analyze(data, fixture_bytes)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote synthetic security-control results: {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
