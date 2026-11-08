"""Synthetic policy audit for identity, tenant checks, quotas, safe logs, and response."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

PROJECT_ID = "v5-ch07-security-ops-synthetic-v1"
ALLOWED_ACTIONS = {
    "record.read": {"reader", "security-admin"},
    "audit.export": {"security-admin"},
}
ALLOWED_RESOURCE_TYPES = {"record", "audit-log"}
SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
REASON_CODES = {
    "policy_allow",
    "missing_credential",
    "invalid_credential",
    "rate_limit_exceeded",
    "tenant_boundary",
    "role_required",
    "action_not_permitted",
}
RESPONSE_TRANSITIONS = {
    "open": ("contain", "contained", "credential_revocation_record"),
    "contained": ("recover", "recovered", "rotation_verified"),
    "recovered": ("close", "closed", "postmortem_reviewed"),
}


class TokenBucket:
    """A deterministic per-key token bucket; this is not distributed state."""

    def __init__(self, capacity: int, refill_units_per_second: int):
        if type(capacity) is not int or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if type(refill_units_per_second) is not int or refill_units_per_second <= 0:
            raise ValueError("refill rate must be a positive integer")
        self.capacity = capacity
        self.refill_rate = refill_units_per_second
        self.tokens = float(capacity)
        self.updated_ms: int | None = None

    def consume(self, timestamp_ms: int, cost: int) -> tuple[bool, int]:
        if type(timestamp_ms) is not int or timestamp_ms < 0:
            raise ValueError("timestamp_ms must be a non-negative integer")
        if type(cost) is not int or cost <= 0 or cost > self.capacity:
            raise ValueError("cost must be a positive integer no greater than capacity")
        if self.updated_ms is None:
            self.updated_ms = timestamp_ms
        else:
            if timestamp_ms < self.updated_ms:
                raise ValueError("timestamps for one bucket must be monotonic")
            elapsed_ms = timestamp_ms - self.updated_ms
            self.tokens = min(
                float(self.capacity),
                self.tokens + (elapsed_ms * self.refill_rate / 1000.0),
            )
            self.updated_ms = timestamp_ms
        if self.tokens + 1e-12 >= cost:
            self.tokens = max(0.0, self.tokens - cost)
            return True, 0
        seconds_to_refill = (cost - self.tokens) / self.refill_rate
        retry_after_ms = max(1, math.ceil(seconds_to_refill * 1000.0 - 1e-9))
        return False, retry_after_ms


def validate_fixture(fixture: dict[str, Any]) -> None:
    """Validate the fixed schema and synthetic-only scope before evaluation."""
    if not isinstance(fixture, dict) or fixture.get("fixture_id") != PROJECT_ID:
        raise ValueError("unexpected fixture id")
    if fixture.get("synthetic") is not True:
        raise ValueError("fixture must be explicitly marked synthetic")
    if fixture.get("contains_personal_data") is not False:
        raise ValueError("fixture must declare no personal data")
    if fixture.get("contains_real_credentials") is not False:
        raise ValueError("fixture must declare no real credentials")
    policy = fixture.get("policy")
    if not isinstance(policy, dict) or not isinstance(policy.get("version"), str) or not SAFE_REQUEST_ID.fullmatch(policy["version"]):
        raise ValueError("policy version must be a safe non-empty identifier")
    if type(policy.get("bucket_capacity")) is not int or policy["bucket_capacity"] <= 0:
        raise ValueError("bucket_capacity must be a positive integer")
    if type(policy.get("refill_units_per_second")) is not int or policy["refill_units_per_second"] <= 0:
        raise ValueError("refill rate must be a positive integer")
    if type(policy.get("auth_failure_threshold")) is not int or policy["auth_failure_threshold"] < 2:
        raise ValueError("auth failure threshold must be at least two")
    if type(policy.get("auth_failure_window_ms")) is not int or policy["auth_failure_window_ms"] <= 0:
        raise ValueError("auth failure window must be a positive integer")

    credentials = fixture.get("credential_registry")
    if not isinstance(credentials, dict) or not credentials:
        raise ValueError("credential_registry must be a non-empty object")
    for credential_ref, identity in credentials.items():
        if not isinstance(credential_ref, str) or not SAFE_REQUEST_ID.fullmatch(credential_ref):
            raise ValueError("credential references must be safe non-empty identifiers")
        if not isinstance(identity, dict):
            raise ValueError("credential entry must be an object")
        for key in ("principal_ref", "tenant_ref"):
            if not isinstance(identity.get(key), str) or not SAFE_REQUEST_ID.fullmatch(identity[key]):
                raise ValueError(f"credential entry needs a safe {key}")
        if not isinstance(identity.get("roles"), list) or not all(isinstance(role, str) and SAFE_REQUEST_ID.fullmatch(role) for role in identity["roles"]):
            raise ValueError("credential roles must be a safe string list")
        if not isinstance(identity.get("active"), bool):
            raise ValueError("credential active flag must be boolean")

    events = fixture.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("events must be a non-empty list")
    event_ids: set[str] = set()
    prior_timestamp = -1
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        event_id = event.get("event_id")
        request_id = event.get("request_id")
        timestamp_ms = event.get("timestamp_ms")
        if not isinstance(event_id, str) or not SAFE_REQUEST_ID.fullmatch(event_id) or event_id in event_ids:
            raise ValueError("event ids must be safe and unique")
        if not isinstance(request_id, str) or not SAFE_REQUEST_ID.fullmatch(request_id):
            raise ValueError("request_id must use the safe fixture identifier alphabet")
        if type(timestamp_ms) is not int or timestamp_ms < 0 or timestamp_ms < prior_timestamp:
            raise ValueError("event timestamps must be non-negative and monotonic")
        if not isinstance(event.get("action"), str) or not event["action"]:
            raise ValueError("action is required")
        if event.get("resource_type") not in ALLOWED_RESOURCE_TYPES:
            raise ValueError("resource_type is outside the fixed example schema")
        if type(event.get("estimated_cost_units")) is not int or not 1 <= event["estimated_cost_units"] <= policy["bucket_capacity"]:
            raise ValueError("estimated_cost_units must be within the server-side bucket capacity")
        event_ids.add(event_id)
        prior_timestamp = timestamp_ms

    steps = fixture.get("response_steps")
    if not isinstance(steps, list):
        raise ValueError("response_steps must be a list")
    for step in steps:
        if not isinstance(step, dict) or not all(isinstance(step.get(key), str) and SAFE_REQUEST_ID.fullmatch(step[key]) for key in ("incident_id", "phase", "evidence_type", "evidence_ref")):
            raise ValueError("response steps require safe incident, phase, evidence type, and evidence reference identifiers")


def _audit_event(
    event: dict[str, Any],
    identity: dict[str, Any] | None,
    outcome: str,
    status_code: int,
    reason_code: str,
    policy_version: str,
) -> dict[str, Any]:
    """Construct an event from an allowlist; never copy arbitrary request fields."""
    if reason_code not in REASON_CODES:
        raise ValueError("reason code is not in the fixed low-cardinality set")
    action = event.get("action")
    safe_action = action if action in ALLOWED_ACTIONS else "unknown_action"
    resource_type = event.get("resource_type")
    safe_resource_type = resource_type if resource_type in ALLOWED_RESOURCE_TYPES else "other"
    return {
        "timestamp_ms": event["timestamp_ms"],
        "request_id": event["request_id"],
        "actor_ref": identity["principal_ref"] if identity else "unknown",
        "tenant_ref": identity["tenant_ref"] if identity else "unknown",
        "action": safe_action,
        "resource_type": safe_resource_type,
        "outcome": outcome,
        "status_code": status_code,
        "reason_code": reason_code,
        "policy_version": policy_version,
    }


def _advance_incident(incident: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(incident)
    current_state = updated["state"]
    transition = RESPONSE_TRANSITIONS.get(current_state)
    if transition is None:
        raise ValueError("incident is already closed or in an unknown state")
    expected_phase, next_state, expected_evidence = transition
    if step.get("incident_id") != updated["incident_id"]:
        raise ValueError("response step references a different incident")
    if step.get("phase") != expected_phase:
        raise ValueError(f"expected incident phase {expected_phase}")
    if step.get("evidence_type") != expected_evidence or not step.get("evidence_ref"):
        raise ValueError(f"phase {expected_phase} requires evidence type {expected_evidence}")
    updated["state"] = next_state
    updated["timeline"].append({
        "phase": expected_phase,
        "state": next_state,
        "evidence_ref": step["evidence_ref"],
    })
    return updated


def simulate(fixture: dict[str, Any], fixture_sha256: str) -> dict[str, Any]:
    validate_fixture(fixture)
    policy = fixture["policy"]
    credentials = fixture["credential_registry"]
    buckets: dict[str, TokenBucket] = {}
    decisions: list[dict[str, Any]] = []
    audit_events: list[dict[str, Any]] = []
    auth_failure_times: list[tuple[int, str]] = []
    alerts: list[dict[str, Any]] = []
    alert_emitted = False

    for event in fixture["events"]:
        credential_ref = event.get("credential_ref")
        identity = credentials.get(credential_ref) if isinstance(credential_ref, str) else None
        if identity is None or not identity.get("active"):
            reason_code = "missing_credential" if credential_ref is None else "invalid_credential"
            decision = {
                "event_id": event["event_id"],
                "request_id": event["request_id"],
                "outcome": "denied",
                "status_code": 401,
                "reason_code": reason_code,
                "retry_after_ms": 0,
            }
            auth_failure_times.append((event["timestamp_ms"], event["request_id"]))
            cutoff = event["timestamp_ms"] - policy["auth_failure_window_ms"]
            auth_failure_times = [(ts, rid) for ts, rid in auth_failure_times if ts >= cutoff]
            if not alert_emitted and len(auth_failure_times) >= policy["auth_failure_threshold"]:
                window_events = auth_failure_times[-policy["auth_failure_threshold"]:]
                alerts.append({
                    "alert_code": "AUTH_FAILURE_BURST",
                    "severity": "review",
                    "count": len(window_events),
                    "window_ms": policy["auth_failure_window_ms"],
                    "evidence_request_ids": [request_id for _, request_id in window_events],
                    "source_ip_logged": False,
                    "credential_value_logged": False,
                })
                alert_emitted = True
            audit_events.append(_audit_event(event, None, "denied", 401, reason_code, policy["version"]))
            decisions.append(decision)
            continue

        tenant_ref = identity["tenant_ref"]
        bucket = buckets.setdefault(
            tenant_ref,
            TokenBucket(policy["bucket_capacity"], policy["refill_units_per_second"]),
        )
        admitted, retry_after_ms = bucket.consume(event["timestamp_ms"], event["estimated_cost_units"])
        if not admitted:
            decision = {
                "event_id": event["event_id"],
                "request_id": event["request_id"],
                "outcome": "rate_limited",
                "status_code": 429,
                "reason_code": "rate_limit_exceeded",
                "retry_after_ms": retry_after_ms,
            }
            audit_events.append(_audit_event(event, identity, "rate_limited", 429, "rate_limit_exceeded", policy["version"]))
            decisions.append(decision)
            continue

        roles = set(identity["roles"])
        allowed_roles = ALLOWED_ACTIONS.get(event["action"])
        if allowed_roles is None:
            outcome, status_code, reason_code = "denied", 403, "action_not_permitted"
        elif event.get("resource_tenant_ref") != tenant_ref:
            outcome, status_code, reason_code = "denied", 403, "tenant_boundary"
        elif roles.isdisjoint(allowed_roles):
            outcome, status_code, reason_code = "denied", 403, "role_required"
        else:
            outcome, status_code, reason_code = "allowed", 200, "policy_allow"
        decision = {
            "event_id": event["event_id"],
            "request_id": event["request_id"],
            "outcome": outcome,
            "status_code": status_code,
            "reason_code": reason_code,
            "retry_after_ms": 0,
        }
        audit_events.append(_audit_event(event, identity, outcome, status_code, reason_code, policy["version"]))
        decisions.append(decision)

    incidents: list[dict[str, Any]] = []
    if alert_emitted:
        incident = {
            "incident_id": "incident-001",
            "alert_code": "AUTH_FAILURE_BURST",
            "state": "open",
            "timeline": [],
        }
        for step in fixture["response_steps"]:
            if step["incident_id"] == incident["incident_id"]:
                incident = _advance_incident(incident, step)
        incidents.append(incident)
    elif fixture["response_steps"]:
        raise ValueError("fixture contains response steps but did not trigger a matching alert")

    reason_counts: dict[str, int] = {}
    for event in audit_events:
        reason_counts[event["reason_code"]] = reason_counts.get(event["reason_code"], 0) + 1
    outcome_counts = {
        "allowed": sum(item["outcome"] == "allowed" for item in decisions),
        "denied": sum(item["outcome"] == "denied" for item in decisions),
        "rate_limited": sum(item["outcome"] == "rate_limited" for item in decisions),
    }
    return {
        "project_id": PROJECT_ID,
        "fixture_id": fixture["fixture_id"],
        "fixture_sha256": fixture_sha256,
        "synthetic": True,
        "request_count": len(fixture["events"]),
        "decision_counts": outcome_counts,
        "reason_counts": dict(sorted(reason_counts.items())),
        "decisions": decisions,
        "auth_failure_count": sum(item["status_code"] == 401 for item in decisions),
        "authorization_denial_count": sum(item["status_code"] == 403 for item in decisions),
        "rate_limited_count": sum(item["status_code"] == 429 for item in decisions),
        "audit_event_count": len(audit_events),
        "audit_events": audit_events,
        "alerts": alerts,
        "incident_count": len(incidents),
        "incidents": incidents,
        "metrics": {
            "request_count": len(decisions),
            "allowed": outcome_counts["allowed"],
            "denied": outcome_counts["denied"],
            "rate_limited": outcome_counts["rate_limited"],
            "alert_count": len(alerts),
            "private_fields_logged": 0,
            "dimension_fields": ["outcome", "reason_code"],
        },
        "external_http_requests": 0,
        "live_auth_provider_calls": 0,
        "live_model_calls": 0,
        "gpu_used": False,
        "personal_records": 0,
        "real_credentials_used": False,
        "scope": "Synthetic deterministic policy simulation; not an authentication implementation, production limiter, security audit, or incident-response service.",
        "limitations": [
            "All identities, tenants, credentials, request times, resource references, and canary strings are invented; no user or production trace is represented.",
            "Credential references select synthetic registry entries; no OAuth, OIDC, JWT signature validation, password verifier, identity provider, or cryptographic key is implemented.",
            "The token bucket is single-process deterministic state; it does not model distributed consistency, real network latency, concurrent races, or provider quotas.",
            "Audit events are assembled by a fixed allowlist for this fixture; this does not prove that another logger, proxy, provider, or storage system is privacy-safe.",
            "The alert threshold and response evidence are synthetic policy choices; they are not an attack probability, compliance finding, or proof of actual credential revocation/recovery.",
            "No legal review, human incident response, notification decision, model-quality evaluation, penetration test, or production security control was performed."
        ],
    }


def run_file(fixture_path: Path) -> dict[str, Any]:
    raw = fixture_path.read_bytes()
    fixture = json.loads(raw.decode("utf-8"))
    return simulate(fixture, hashlib.sha256(raw).hexdigest())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_fixture = Path(__file__).with_name("synthetic_security_events.json")
    default_output = Path(__file__).with_name("results.json")
    parser.add_argument("--fixture", type=Path, default=default_fixture)
    parser.add_argument("--output", type=Path, default=default_output)
    args = parser.parse_args(argv)
    result = run_file(args.fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
