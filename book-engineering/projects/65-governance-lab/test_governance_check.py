from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

import governance_check as checker

ROOT = Path(__file__).resolve().parent
FIXTURE_BYTES = (ROOT / "governance_pack.json").read_bytes()
FIXTURE = json.loads(FIXTURE_BYTES.decode("utf-8"))


class GovernancePackTests(unittest.TestCase):
    def test_synthetic_pack_is_structurally_valid_but_not_release_authorized(self):
        report = checker.analyze(FIXTURE, FIXTURE_BYTES)
        self.assertTrue(report["structurally_valid"], report["validation_errors"])
        self.assertFalse(report["release_authorized"])
        self.assertEqual(report["gate_status"], "hold")
        self.assertEqual(report["risk_count"], 4)
        self.assertEqual(report["evidence_count"], 5)

    def test_missing_system_owner_field_is_reported(self):
        pack = deepcopy(FIXTURE)
        del pack["system"]["deployer"]
        errors = checker.validate_pack(pack)
        self.assertIn("system.deployer must be a non-empty string", errors)

    def test_duplicate_risk_id_is_reported(self):
        pack = deepcopy(FIXTURE)
        pack["risk_register"][1]["id"] = pack["risk_register"][0]["id"]
        self.assertTrue(any("risk_register[1].id is duplicated" in e for e in checker.validate_pack(pack)))

    def test_unknown_qualitative_severity_is_reported(self):
        pack = deepcopy(FIXTURE)
        pack["risk_register"][0]["inherent_severity"] = "4"
        self.assertTrue(any("inherent_severity is not a defined qualitative level" in e for e in checker.validate_pack(pack)))

    def test_unhashable_enum_and_evidence_reference_values_are_reported(self):
        pack = deepcopy(FIXTURE)
        pack["evidence"][0]["status"] = []
        pack["risk_register"][0]["inherent_severity"] = {}
        pack["risk_register"][0]["evidence_refs"] = [{}]
        pack["decision"]["gate_status"] = []
        errors = checker.validate_pack(pack)
        self.assertTrue(any("evidence[0].status must be one of" in error for error in errors))
        self.assertTrue(any("inherent_severity is not a defined qualitative level" in error for error in errors))
        self.assertIn("risk_register[0].evidence_refs must contain non-empty string ids", errors)
        self.assertIn("decision.gate_status must be hold, approved, or rejected", errors)

    def test_list_fields_require_non_empty_text_items(self):
        pack = deepcopy(FIXTURE)
        pack["system"]["out_of_scope_uses"] = [""]
        pack["model_card"]["limitations"] = [""]
        pack["dataset_cards"][0]["known_gaps"] = [None]
        pack["risk_register"][0]["affected_parties"] = [""]
        pack["risk_register"][0]["controls"] = [""]
        errors = checker.validate_pack(pack)
        self.assertTrue(any("system.out_of_scope_uses must be" in error for error in errors))
        self.assertTrue(any("model_card.limitations must be" in error for error in errors))
        self.assertTrue(any("dataset_cards[0].known_gaps must be" in error for error in errors))
        self.assertTrue(any("risk_register[0].affected_parties must be" in error for error in errors))
        self.assertTrue(any("risk_register[0].controls must be" in error for error in errors))

    def test_unlinked_evidence_reference_is_reported(self):
        pack = deepcopy(FIXTURE)
        pack["risk_register"][0]["evidence_refs"] = ["EV-NOT-IN-CATALOG"]
        self.assertTrue(any("unknown evidence id" in e for e in checker.validate_pack(pack)))

    def test_model_card_must_expose_limitations(self):
        pack = deepcopy(FIXTURE)
        pack["model_card"]["limitations"] = []
        self.assertIn(
            "model_card.limitations must be a non-empty list of non-empty strings",
            checker.validate_pack(pack),
        )

    def test_dataset_card_must_record_known_gaps(self):
        pack = deepcopy(FIXTURE)
        pack["dataset_cards"][0]["known_gaps"] = []
        self.assertIn(
            "dataset_cards[0].known_gaps must be a non-empty list of non-empty strings, including known unknowns",
            checker.validate_pack(pack),
        )

    def test_approved_gate_requires_human_approval_and_closed_high_risk(self):
        pack = deepcopy(FIXTURE)
        pack["decision"]["gate_status"] = "approved"
        pack["decision"]["approved_by"] = ""
        pack["decision"]["approved_at"] = ""
        errors = checker.validate_pack(pack)
        self.assertTrue(any("named human approver" in e for e in errors))
        self.assertTrue(any("high or critical residual risks" in e for e in errors))

    def test_risk_register_requires_evidence_refs(self):
        pack = deepcopy(FIXTURE)
        pack["risk_register"][0]["evidence_refs"] = []
        self.assertTrue(any("evidence_refs must be a non-empty list" in e for e in checker.validate_pack(pack)))

    def test_report_is_deterministic_for_identical_bytes(self):
        first = checker.analyze(FIXTURE, FIXTURE_BYTES)
        second = checker.analyze(FIXTURE, FIXTURE_BYTES)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
