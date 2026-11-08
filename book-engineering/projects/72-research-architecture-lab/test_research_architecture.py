"""Unit tests for structural checks on the fictional chapter-72 packet."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from research_architecture import PROJECT_ID, analyze_files, validate_packet

HERE = Path(__file__).resolve().parent


class ResearchArchitecturePacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads((HERE / "research_packet.json").read_text(encoding="utf-8"))

    def mutated(self, change, message: str) -> None:
        packet = copy.deepcopy(self.fixture)
        change(packet)
        with self.assertRaisesRegex(ValueError, message):
            validate_packet(packet)

    def test_fixture_is_valid_and_synthetic(self) -> None:
        result = validate_packet(copy.deepcopy(self.fixture))
        self.assertEqual(result["validation_status"], "structural_consistency_passed")
        self.assertTrue(result["synthetic"])
        self.assertFalse(result["scientific_conclusions"]["novelty_confirmed"])

    def test_counts_match_the_planning_packet(self) -> None:
        counts = validate_packet(copy.deepcopy(self.fixture))["counts"]
        self.assertEqual(counts["architecture_components"], 1)
        self.assertEqual(counts["architecture_alternatives"], 2)
        self.assertEqual(counts["quality_scenarios"], 3)
        self.assertEqual(counts["planned_evaluations"], 2)
        self.assertEqual(counts["paper_sections"], 11)
        self.assertEqual(counts["contributors"], 3)
        self.assertEqual(counts["roadmap_milestones"], 4)

    def test_result_never_claims_empirical_or_publication_validation(self) -> None:
        conclusions = validate_packet(copy.deepcopy(self.fixture))["scientific_conclusions"]
        self.assertTrue(all(value is False for value in conclusions.values()))

    def test_rejects_wrong_project_id(self) -> None:
        self.mutated(lambda p: p.update(project_id="other"), "unexpected project_id")

    def test_rejects_non_synthetic_fixture(self) -> None:
        self.mutated(lambda p: p.update(synthetic=False), "explicitly synthetic")

    def test_rejects_real_data_flag(self) -> None:
        self.mutated(lambda p: p.update(real_data_used=True), "real_data_used must be false")

    def test_rejects_real_model_output_flag(self) -> None:
        self.mutated(lambda p: p.update(real_model_outputs=True), "real_model_outputs must be false")

    def test_rejects_network_use_flag(self) -> None:
        self.mutated(lambda p: p.update(network_used=True), "network_used must be false")

    def test_rejects_a_production_scope(self) -> None:
        self.mutated(lambda p: p["problem"].update(boundary="production service"),
                     "must exclude production use")

    def test_rejects_missing_falsification_condition(self) -> None:
        self.mutated(lambda p: p["contribution"].update(falsification_condition=""),
                     "falsification_condition is required")

    def test_rejects_component_without_interface_contract(self) -> None:
        self.mutated(lambda p: p["architecture"]["components"][0].update(output_contract=""),
                     "needs output_contract")

    def test_rejects_duplicate_component_ids(self) -> None:
        def change(p):
            p["architecture"]["components"].append(copy.deepcopy(p["architecture"]["components"][0]))
        self.mutated(change, "architecture components contains duplicate ids")

    def test_requires_at_least_two_alternatives(self) -> None:
        self.mutated(lambda p: p["architecture"].update(alternatives=p["architecture"]["alternatives"][:1]),
                     "at least two architecture alternatives")

    def test_rejects_unknown_evaluation_reference_in_quality_scenario(self) -> None:
        self.mutated(lambda p: p["quality_scenarios"][0].update(evaluation_ref="E-unknown"),
                     "references an unknown evaluation")

    def test_rejects_duplicate_evaluation_ids(self) -> None:
        def change(p):
            p["evaluation_plan"].append(copy.deepcopy(p["evaluation_plan"][0]))
        self.mutated(change, "evaluation plan contains duplicate ids")

    def test_rejects_unregistered_source_reference(self) -> None:
        self.mutated(lambda p: p["related_work"].update(source_refs=["S-unknown"]),
                     "cites an unknown source")

    def test_rejects_unknown_evaluation_in_claim(self) -> None:
        self.mutated(lambda p: p["claims"][0].update(evaluation_refs=["E-unknown"]),
                     "references an unknown evaluation")

    def test_rejects_claim_presented_as_supported(self) -> None:
        self.mutated(lambda p: p["claims"][0].update(status="supported"),
                     "must remain a hypothesis")

    def test_rejects_incomplete_paper_outline(self) -> None:
        self.mutated(lambda p: p["paper_outline"].__setitem__(
            slice(None), [item for item in p["paper_outline"] if item["id"] != "limitations"]),
            "omits a required section")

    def test_rejects_unknown_credit_role(self) -> None:
        self.mutated(lambda p: p["contributors"][0].update(credit_roles=["Guaranteed authorship"]),
                     "unsupported CRediT role")

    def test_rejects_authorship_decision_inferred_from_roles(self) -> None:
        self.mutated(lambda p: p["contributors"][0].update(authorship_status="decided_by_roles"),
                     "must not be treated as an authorship decision")

    def test_rejects_roadmap_without_decision_gate(self) -> None:
        self.mutated(lambda p: p["roadmap"][0].update(decision_gate=""),
                     "needs decision_gate")

    def test_rejects_milestone_marked_complete(self) -> None:
        self.mutated(lambda p: p["roadmap"][0].update(status="complete"),
                     "must not be marked complete")

    def test_rejects_premature_license_approval(self) -> None:
        self.mutated(lambda p: p["release_plan"].update(license_review="approved"),
                     "license review must remain pending")

    def test_rejects_fixture_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet_path = root / "packet.json"
            manifest_path = root / "manifest.json"
            packet_path.write_bytes((HERE / "research_packet.json").read_bytes())
            manifest_path.write_text(json.dumps({
                "project_id": PROJECT_ID,
                "fixture_sha256": "0" * 64,
                "synthetic": True,
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fixture SHA-256 mismatch"):
                analyze_files(packet_path, manifest_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
