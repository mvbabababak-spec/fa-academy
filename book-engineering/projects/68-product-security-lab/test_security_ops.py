"""Offline tests for the synthetic Chapter 68 security-operations lab."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import security_ops

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "synthetic_security_events.json"


class FixtureValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_declares_synthetic_nonpersonal_inputs(self) -> None:
        security_ops.validate_fixture(self.fixture)
        self.assertIs(self.fixture["synthetic"], True)
        self.assertIs(self.fixture["contains_personal_data"], False)
        self.assertIs(self.fixture["contains_real_credentials"], False)

    def test_duplicate_event_id_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["events"][1]["event_id"] = fixture["events"][0]["event_id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            security_ops.validate_fixture(fixture)

    def test_nonmonotonic_time_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["events"][1]["timestamp_ms"] = -1
        with self.assertRaisesRegex(ValueError, "monotonic"):
            security_ops.validate_fixture(fixture)

    def test_unsafe_request_id_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["events"][0]["request_id"] = "trace-1\ncredential=secret"
        with self.assertRaisesRegex(ValueError, "safe fixture identifier"):
            security_ops.validate_fixture(fixture)

    def test_cost_cannot_exceed_server_capacity(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["events"][0]["estimated_cost_units"] = 3
        with self.assertRaisesRegex(ValueError, "server-side bucket capacity"):
            security_ops.validate_fixture(fixture)

    def test_real_data_claim_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["contains_personal_data"] = True
        with self.assertRaisesRegex(ValueError, "no personal data"):
            security_ops.validate_fixture(fixture)


class TokenBucketTests(unittest.TestCase):
    def test_capacity_refill_and_retry_after_are_exact(self) -> None:
        bucket = security_ops.TokenBucket(capacity=2, refill_units_per_second=1)
        self.assertEqual(bucket.consume(0, 2), (True, 0))
        self.assertEqual(bucket.consume(0, 1), (False, 1000))
        self.assertEqual(bucket.consume(1000, 1), (True, 0))

    def test_bucket_rejects_out_of_order_time(self) -> None:
        bucket = security_ops.TokenBucket(capacity=2, refill_units_per_second=1)
        bucket.consume(100, 1)
        with self.assertRaisesRegex(ValueError, "monotonic"):
            bucket.consume(99, 1)

    def test_buckets_are_independent(self) -> None:
        tenant_a = security_ops.TokenBucket(capacity=2, refill_units_per_second=1)
        tenant_b = security_ops.TokenBucket(capacity=2, refill_units_per_second=1)
        self.assertEqual(tenant_a.consume(0, 2), (True, 0))
        self.assertEqual(tenant_a.consume(0, 1), (False, 1000))
        self.assertEqual(tenant_b.consume(0, 1), (True, 0))

    def test_invalid_bucket_parameters_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            security_ops.TokenBucket(capacity=0, refill_units_per_second=1)
        with self.assertRaises(ValueError):
            security_ops.TokenBucket(capacity=1, refill_units_per_second=0)


class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture_bytes = FIXTURE.read_bytes()
        cls.result = security_ops.run_file(FIXTURE)
        cls.serialized = json.dumps(cls.result, ensure_ascii=False, sort_keys=True)

    def test_fixture_hash_and_decision_totals(self) -> None:
        self.assertEqual(self.result["fixture_sha256"], hashlib.sha256(self.fixture_bytes).hexdigest())
        self.assertEqual(self.result["request_count"], 14)
        self.assertEqual(self.result["decision_counts"], {"allowed": 6, "denied": 6, "rate_limited": 2})
        self.assertEqual(self.result["auth_failure_count"], 3)
        self.assertEqual(self.result["authorization_denial_count"], 3)
        self.assertEqual(self.result["rate_limited_count"], 2)

    def test_claimed_tenant_never_overrides_registry(self) -> None:
        decisions = {item["request_id"]: item for item in self.result["audit_events"]}
        self.assertEqual(decisions["trace-001"]["tenant_ref"], "tenant-a")
        self.assertEqual(decisions["trace-001"]["outcome"], "allowed")

    def test_cross_tenant_and_role_denials_are_distinct(self) -> None:
        decisions = {item["request_id"]: item for item in self.result["audit_events"]}
        self.assertEqual(decisions["trace-007"]["reason_code"], "tenant_boundary")
        self.assertEqual(decisions["trace-008"]["reason_code"], "role_required")
        self.assertEqual(decisions["trace-014"]["reason_code"], "tenant_boundary")

    def test_missing_unknown_and_disabled_credentials_are_denied(self) -> None:
        decisions = {item["event_id"]: item for item in self.result["decisions"]}
        self.assertEqual(decisions["req-009"]["reason_code"], "missing_credential")
        self.assertEqual(decisions["req-010"]["reason_code"], "invalid_credential")
        self.assertEqual(decisions["req-011"]["reason_code"], "invalid_credential")
        self.assertTrue(all(decisions[key]["status_code"] == 401 for key in ("req-009", "req-010", "req-011")))

    def test_rate_limit_emits_retry_after_milliseconds(self) -> None:
        decisions = {item["event_id"]: item for item in self.result["decisions"]}
        self.assertEqual(decisions["req-003"]["status_code"], 429)
        self.assertEqual(decisions["req-003"]["retry_after_ms"], 800)
        self.assertEqual(decisions["req-005"]["retry_after_ms"], 100)

    def test_privileged_action_requires_role_then_allows_admin(self) -> None:
        decisions = {item["event_id"]: item for item in self.result["decisions"]}
        self.assertEqual(decisions["req-008"]["status_code"], 403)
        self.assertEqual(decisions["req-012"]["status_code"], 200)
        self.assertEqual(decisions["req-012"]["reason_code"], "policy_allow")

    def test_audit_schema_is_allowlisted(self) -> None:
        expected = {
            "timestamp_ms", "request_id", "actor_ref", "tenant_ref", "action",
            "resource_type", "outcome", "status_code", "reason_code", "policy_version",
        }
        self.assertEqual(len(self.result["audit_events"]), 14)
        for item in self.result["audit_events"]:
            self.assertEqual(set(item), expected)

    def test_private_canaries_and_source_addresses_are_not_logged(self) -> None:
        for forbidden in (
            "SYNTHETIC-CREDENTIAL-CANARY-DO-NOT-LOG",
            "SYNTHETIC-PRIVATE-PROMPT-DO-NOT-LOG",
            "synthetic-person@example.invalid",
            "198.51.100.",
            "claimed_tenant_ref",
        ):
            self.assertNotIn(forbidden, self.serialized)
        self.assertEqual(self.result["metrics"]["private_fields_logged"], 0)

    def test_aggregate_dimensions_stay_low_cardinality(self) -> None:
        self.assertEqual(self.result["metrics"]["dimension_fields"], ["outcome", "reason_code"])
        self.assertNotIn("tenant_ref", self.result["metrics"])
        self.assertNotIn("actor_ref", self.result["metrics"])

    def test_authentication_burst_creates_privacy_minimized_alert(self) -> None:
        self.assertEqual(len(self.result["alerts"]), 1)
        alert = self.result["alerts"][0]
        self.assertEqual(alert["alert_code"], "AUTH_FAILURE_BURST")
        self.assertEqual(alert["count"], 3)
        self.assertEqual(alert["evidence_request_ids"], ["trace-009", "trace-010", "trace-011"])
        self.assertIs(alert["source_ip_logged"], False)
        self.assertIs(alert["credential_value_logged"], False)

    def test_incident_progresses_through_evidence_gated_states(self) -> None:
        self.assertEqual(self.result["incident_count"], 1)
        incident = self.result["incidents"][0]
        self.assertEqual(incident["state"], "closed")
        self.assertEqual([step["phase"] for step in incident["timeline"]], ["contain", "recover", "close"])
        self.assertEqual([step["state"] for step in incident["timeline"]], ["contained", "recovered", "closed"])

    def test_response_state_machine_rejects_out_of_order_evidence(self) -> None:
        incident = {"incident_id": "incident-x", "state": "open", "timeline": []}
        wrong_step = {
            "incident_id": "incident-x", "phase": "recover",
            "evidence_type": "rotation_verified", "evidence_ref": "evidence-x",
        }
        with self.assertRaisesRegex(ValueError, "expected incident phase contain"):
            security_ops._advance_incident(incident, wrong_step)
        self.assertEqual(incident["state"], "open")
        self.assertEqual(incident["timeline"], [])

    def test_simulation_is_repeatable(self) -> None:
        again = security_ops.run_file(FIXTURE)
        self.assertEqual(self.result, again)

    def test_cli_writes_deterministic_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.json"
            second = Path(temp_dir) / "second.json"
            for destination in (first, second):
                exit_code = security_ops.main(["--fixture", str(FIXTURE), "--output", str(destination)])
                self.assertEqual(exit_code, 0)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertTrue(first.read_bytes().endswith(b"\n"))

    def test_scope_disclaims_production_and_compliance_claims(self) -> None:
        self.assertIn("not an authentication implementation", self.result["scope"])
        self.assertEqual(self.result["external_http_requests"], 0)
        self.assertEqual(self.result["live_auth_provider_calls"], 0)
        self.assertEqual(self.result["live_model_calls"], 0)
        self.assertFalse(self.result["gpu_used"])
        self.assertEqual(self.result["personal_records"], 0)
        self.assertFalse(self.result["real_credentials_used"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
