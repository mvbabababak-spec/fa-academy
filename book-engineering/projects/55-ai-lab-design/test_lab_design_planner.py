"""Unit tests for synthetic lab-planning arithmetic and input validation."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import lab_design_planner as planner

FIXTURE = Path(__file__).with_name("sample_labs.json")
SCRIPT = Path(__file__).with_name("lab_design_planner.py")


class FixtureValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture, _ = planner.load_fixture(FIXTURE)

    def test_reference_fixture_is_valid(self) -> None:
        self.assertIsNone(planner.validate_fixture(self.fixture))

    def test_schema_version_must_match(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["schema_version"] = "future"
        with self.assertRaisesRegex(planner.DesignInputError, "schema_version"):
            planner.validate_fixture(value)

    def test_fixture_id_is_required(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["fixture_id"] = " "
        with self.assertRaisesRegex(planner.DesignInputError, "fixture_id"):
            planner.validate_fixture(value)

    def test_fixture_must_be_labeled_synthetic(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["label_source"] = "measured"
        with self.assertRaisesRegex(planner.DesignInputError, "synthetic_fixture"):
            planner.validate_fixture(value)

    def test_metadata_fields_must_be_explicitly_false(self) -> None:
        for field in planner.REQUIRED_FALSE_METADATA:
            with self.subTest(field=field):
                value = copy.deepcopy(self.fixture)
                value["metadata"][field] = True
                with self.assertRaisesRegex(planner.DesignInputError, field):
                    planner.validate_fixture(value)

    def test_missing_metadata_is_not_silently_assumed(self) -> None:
        value = copy.deepcopy(self.fixture)
        del value["metadata"]["prices_included"]
        with self.assertRaisesRegex(planner.DesignInputError, "prices_included"):
            planner.validate_fixture(value)

    def test_profiles_must_be_nonempty(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"] = []
        with self.assertRaisesRegex(planner.DesignInputError, "non-empty"):
            planner.validate_fixture(value)

    def test_profile_ids_must_be_unique(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][1]["profile_id"] = value["profiles"][0]["profile_id"]
        with self.assertRaisesRegex(planner.DesignInputError, "duplicate profile_id"):
            planner.validate_fixture(value)

    def test_tier_must_be_known(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["tier"] = "enterprise-premium"
        with self.assertRaisesRegex(planner.DesignInputError, "tier"):
            planner.validate_fixture(value)

    def test_workload_must_be_an_object(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["workload"] = None
        with self.assertRaisesRegex(planner.DesignInputError, "workload"):
            planner.validate_fixture(value)

    def test_zero_minimum_node_count_is_rejected(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["workload"]["minimum_nodes"] = 0
        with self.assertRaisesRegex(planner.DesignInputError, "minimum_nodes"):
            planner.validate_fixture(value)

    def test_boolean_is_not_an_integer(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["workload"]["minimum_nodes"] = True
        with self.assertRaisesRegex(planner.DesignInputError, "minimum_nodes"):
            planner.validate_fixture(value)

    def test_negative_memory_is_rejected(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["workload"]["minimum_vram_gib_per_accelerator"] = -1
        with self.assertRaisesRegex(planner.DesignInputError, "minimum_vram"):
            planner.validate_fixture(value)

    def test_nonfinite_memory_is_rejected(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["design"]["vram_gib_per_accelerator"] = float("inf")
        with self.assertRaisesRegex(planner.DesignInputError, "finite"):
            planner.validate_fixture(value)

    def test_vram_fraction_must_be_greater_than_zero(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["policy"]["usable_vram_fraction"] = 0
        with self.assertRaisesRegex(planner.DesignInputError, "usable_vram_fraction"):
            planner.validate_fixture(value)

    def test_vram_fraction_cannot_exceed_one(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["policy"]["usable_vram_fraction"] = 1.01
        with self.assertRaisesRegex(planner.DesignInputError, "usable_vram_fraction"):
            planner.validate_fixture(value)

    def test_cooling_factor_below_one_is_rejected(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["policy"]["cooling_design_factor"] = 0.99
        with self.assertRaisesRegex(planner.DesignInputError, "cooling_design_factor"):
            planner.validate_fixture(value)

    def test_storage_schema_requires_every_component(self) -> None:
        value = copy.deepcopy(self.fixture)
        del value["profiles"][0]["workload"]["storage"]["backup_tb"]
        with self.assertRaisesRegex(planner.DesignInputError, "backup_tb"):
            planner.validate_fixture(value)

    def test_negative_storage_is_rejected(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["workload"]["storage"]["scratch_tb"] = -0.5
        with self.assertRaisesRegex(planner.DesignInputError, "scratch_tb"):
            planner.validate_fixture(value)

    def test_storage_copy_count_must_be_integer(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["workload"]["storage"]["working_copies"] = 1.5
        with self.assertRaisesRegex(planner.DesignInputError, "working_copies"):
            planner.validate_fixture(value)

    def test_runtime_stack_entries_must_be_unique(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["design"]["declared_runtime_stack"] = ["linux", "linux"]
        with self.assertRaisesRegex(planner.DesignInputError, "duplicates"):
            planner.validate_fixture(value)

    def test_runtime_stack_entries_must_be_nonempty_strings(self) -> None:
        value = copy.deepcopy(self.fixture)
        value["profiles"][0]["workload"]["required_runtime_stack"] = [""]
        with self.assertRaisesRegex(planner.DesignInputError, "required_runtime_stack"):
            planner.validate_fixture(value)


class ArithmeticAndCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture, self.digest = planner.load_fixture(FIXTURE)
        self.profiles = {item["profile_id"]: item for item in self.fixture["profiles"]}
        self.policy = self.fixture["policy"]

    def _evaluate(self, profile_id: str, **changes):
        profile = copy.deepcopy(self.profiles[profile_id])
        for group, fields in changes.items():
            profile[group].update(fields)
        return planner.evaluate_profile(profile, self.policy)

    def test_storage_formula_counts_all_user_declared_parts(self) -> None:
        storage = self.profiles["synthetic-personal-lab"]["workload"]["storage"]
        self.assertAlmostEqual(planner.required_storage_tb(storage), 5.1)

    def test_personal_design_passes_screen(self) -> None:
        result = self._evaluate("synthetic-personal-lab")
        self.assertEqual(result["status"], "paper_feasible")
        self.assertTrue(all(check["passed"] for check in result["checks"]))

    def test_independent_workstation_passes_screen(self) -> None:
        self.assertEqual(self._evaluate("synthetic-independent-workstation")["status"], "paper_feasible")

    def test_organizational_cluster_passes_screen(self) -> None:
        self.assertEqual(self._evaluate("synthetic-organizational-cluster")["status"], "paper_feasible")

    def test_underprovisioned_profile_is_flagged(self) -> None:
        result = self._evaluate("synthetic-underprovisioned-cluster")
        self.assertEqual(result["status"], "needs_revision")
        failed = {item["check"] for item in result["checks"] if not item["passed"]}
        self.assertEqual(failed, {
            "per_accelerator_memory", "host_ram", "usable_storage",
            "declared_psu_output_capacity", "site_input_power_allocation",
            "cooling_capacity_screen", "nominal_interconnect_rate", "declared_runtime_stack",
        })

    def test_memory_is_checked_per_accelerator_not_pooled(self) -> None:
        result = self._evaluate("synthetic-personal-lab", workload={"minimum_vram_gib_per_accelerator": 22})
        check = next(item for item in result["checks"] if item["check"] == "per_accelerator_memory")
        self.assertFalse(check["passed"])
        self.assertEqual(check["usable_capacity_gib"], 21.6)

    def test_node_count_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-personal-lab", workload={"minimum_nodes": 2})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "minimum_nodes")["passed"])

    def test_accelerator_count_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-personal-lab", workload={"accelerators_per_node": 2})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "accelerators_per_node")["passed"])

    def test_host_ram_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-personal-lab", design={"host_ram_gib": 32})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "host_ram")["passed"])

    def test_physical_position_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-personal-lab", design={"documented_accelerator_positions_per_node": 0})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "documented_accelerator_positions")["passed"])

    def test_storage_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-personal-lab", design={"usable_storage_tb": 5})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "usable_storage")["passed"])

    def test_psu_declared_output_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-personal-lab", design={"psu_dc_capacity_w_per_node": 400})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "declared_psu_output_capacity")["passed"])

    def test_site_power_allocation_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-personal-lab", design={"site_approved_input_capacity_w": 500})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "site_input_power_allocation")["passed"])

    def test_cooling_capacity_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-personal-lab", design={"cooling_capacity_btu_per_hour": 100})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "cooling_capacity_screen")["passed"])

    def test_network_line_rate_shortfall_is_flagged(self) -> None:
        result = self._evaluate("synthetic-independent-workstation", design={"nominal_interconnect_gbps": 10})
        self.assertFalse(next(c for c in result["checks"] if c["check"] == "nominal_interconnect_rate")["passed"])

    def test_runtime_stack_gap_is_flagged(self) -> None:
        result = self._evaluate("synthetic-independent-workstation", design={"declared_runtime_stack": ["linux"]})
        check = next(c for c in result["checks"] if c["check"] == "declared_runtime_stack")
        self.assertFalse(check["passed"])
        self.assertEqual(check["missing"], ["accelerator-runtime", "distributed-runtime"])

    def test_network_and_other_it_loads_are_in_site_sum(self) -> None:
        result = self._evaluate("synthetic-personal-lab")
        self.assertEqual(result["derived"]["total_site_input_power_w"], 545)

    def test_heat_conversion_uses_nist_derived_factor(self) -> None:
        result = self._evaluate("synthetic-personal-lab")
        self.assertAlmostEqual(
            result["derived"]["estimated_it_heat_btu_per_hour"],
            545 * planner.BTU_PER_HOUR_PER_WATT,
        )

    def test_cooling_factor_is_applied_after_heat_conversion(self) -> None:
        result = self._evaluate("synthetic-personal-lab")
        self.assertAlmostEqual(
            result["derived"]["screened_cooling_requirement_btu_per_hour"],
            545 * planner.BTU_PER_HOUR_PER_WATT * self.policy["cooling_design_factor"],
        )

    def test_dc_load_headroom_is_reported(self) -> None:
        result = self._evaluate("synthetic-personal-lab")
        check = next(c for c in result["checks"] if c["check"] == "declared_psu_output_capacity")
        self.assertEqual(check["arithmetic_headroom_w_per_node"], 280)

    def test_storage_screen_reports_exact_fixture_requirement(self) -> None:
        result = self._evaluate("synthetic-organizational-cluster")
        self.assertEqual(result["derived"]["required_storage_tb"], 236)

    def test_fixture_summary_counts_three_paper_feasible_profiles(self) -> None:
        result = planner.run_demo(FIXTURE)
        self.assertEqual(result["summary"], {"profiles": 4, "paper_feasible": 3, "needs_revision": 1})

    def test_profile_results_are_deterministic(self) -> None:
        self.assertEqual(planner.run_demo(FIXTURE), planner.run_demo(FIXTURE))

    def test_output_scope_disclaims_real_deployment_claims(self) -> None:
        result = planner.run_demo(FIXTURE)
        for key in ("real_hardware_measured", "real_workload_run", "vendor_skus_included", "prices_included", "benchmark_performed", "electrical_code_checked", "installation_performed", "training_performed"):
            self.assertIs(result["scope"][key], False)

    def test_hash_matches_raw_fixture_bytes(self) -> None:
        _, digest = planner.load_fixture(FIXTURE)
        self.assertEqual(digest, hashlib.sha256(FIXTURE.read_bytes()).hexdigest())

    def test_usable_vram_fraction_is_explicit_in_check(self) -> None:
        result = self._evaluate("synthetic-personal-lab")
        check = next(c for c in result["checks"] if c["check"] == "per_accelerator_memory")
        self.assertEqual(check["usable_fraction"], 0.9)


class CliAndFileTests(unittest.TestCase):
    def test_chapter_appendix_is_byte_for_byte_project_source(self) -> None:
        chapter = SCRIPT.parents[2] / "chapters" / "55-ai-lab-design.md"
        source = SCRIPT.read_bytes()
        marker = b"\n```python\n"
        _, found, tail = chapter.read_bytes().rpartition(marker)
        self.assertTrue(found, "Python appendix fence is missing")
        closing = tail.rfind(b"```")
        self.assertGreaterEqual(closing, 0, "Python appendix is not closed")
        self.assertEqual(tail[:closing], source)

    def test_cli_stdout_is_json(self) -> None:
        completed = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
        result = json.loads(completed.stdout)
        self.assertEqual(result["summary"]["profiles"], 4)

    def test_cli_writes_output_file_and_creates_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "report.json"
            completed = subprocess.run([sys.executable, str(SCRIPT), "--output", str(target)], capture_output=True, text=True, check=True)
            self.assertIn("Wrote synthetic design screen", completed.stdout)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["summary"]["paper_feasible"], 3)

    def test_cli_accepts_custom_fixture_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.json"
            subprocess.run([sys.executable, str(SCRIPT), "--fixture", str(FIXTURE), "--output", str(output)], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["fixture"]["fixture_id"], "v4-ch09-synthetic-lab-design-v1")

    def test_loader_rejects_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(planner.DesignInputError, "valid UTF-8 JSON"):
                planner.load_fixture(path)

    def test_loader_rejects_invalid_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_bytes(b"\xff\xfe")
            with self.assertRaisesRegex(planner.DesignInputError, "valid UTF-8 JSON"):
                planner.load_fixture(path)

    def test_loader_reports_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            with self.assertRaisesRegex(planner.DesignInputError, "not found"):
                planner.load_fixture(path)

    def test_cli_returns_two_for_malformed_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text("{}", encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), "--fixture", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("input error", result.stderr)

    def test_cli_never_includes_prices_in_output(self) -> None:
        completed = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
        result = json.loads(completed.stdout)
        self.assertIs(result["scope"]["prices_included"], False)
        self.assertFalse(any("price" in key.lower() for profile in result["profiles"] for key in profile))


if __name__ == "__main__":
    unittest.main()
