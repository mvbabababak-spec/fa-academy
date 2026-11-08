from __future__ import annotations

import json
import unittest
from decimal import Decimal
from pathlib import Path

from budget_model import (
    BudgetInputError,
    build_results,
    cloud_compute_cost_usd,
    energy_cost_usd,
    load_and_run,
    net_present_value,
    validate_fixture,
)

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "sample_budget.json"


class ArithmeticTests(unittest.TestCase):
    def test_energy_uses_site_kw_hours_and_rate(self):
        self.assertEqual(energy_cost_usd("0.45", 1200, "0.0896"), Decimal("48.384000"))

    def test_cloud_cost_uses_instance_hours_and_snapshot_rate(self):
        self.assertEqual(cloud_compute_cost_usd("4.49993", 800), Decimal("3599.94400"))

    def test_npv_discounts_year_end_costs(self):
        result = net_present_value([Decimal("100"), Decimal("110")], "0.10")
        self.assertEqual(result, Decimal("200"))

    def test_npv_rejects_empty_flows_and_invalid_rate(self):
        with self.assertRaises(BudgetInputError):
            net_present_value([], "0.05")
        with self.assertRaises(BudgetInputError):
            net_present_value([Decimal("1")], "1.0")

    def test_energy_rejects_negative_inputs(self):
        with self.assertRaises(BudgetInputError):
            energy_cost_usd("-0.2", 10, "0.1")

    def test_non_finite_values_are_rejected(self):
        with self.assertRaises(BudgetInputError):
            cloud_compute_cost_usd("NaN", 10)


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.raw = FIXTURE.read_bytes()
        self.fixture = json.loads(self.raw.decode("utf-8"))

    def test_fixture_is_explicitly_synthetic_and_market_tagged(self):
        self.assertEqual(validate_fixture(self.fixture)["label_source"], "synthetic_fixture")
        self.assertEqual(self.fixture["market_snapshot"]["cloud_compute"]["region"], "us-central1 (Iowa, US)")
        self.assertIn("not Dallas", self.fixture["market_snapshot"]["electricity"]["region"])

    def test_results_have_three_scenarios_and_disclaim_performance_parity(self):
        result = build_results(self.fixture, self.raw)
        self.assertEqual(len(result["scenarios"]), 3)
        self.assertFalse(result["comparison_status"]["performance_parity_measured"])
        self.assertFalse(result["comparison_status"]["complete_invoice_or_cost_estimate"])
        self.assertEqual(result["fixture_sha256"], __import__("hashlib").sha256(self.raw).hexdigest())

    def test_cloud_scenario_carries_dated_rate_and_separate_costs_warning(self):
        result = load_and_run(FIXTURE)
        cloud = next(row for row in result["scenarios"] if row["strategy"] == "cloud")
        self.assertEqual(cloud["components"]["market_instance_price_usd_per_hour"], "4.49993")
        self.assertEqual(cloud["components"]["annual_compute_cost_usd"], "3599.94")
        self.assertIsNone(cloud["components"]["annual_energy_cost_usd"])
        self.assertTrue(any("not an all-in invoice" in note for note in result["limitations"]))

    def test_market_regions_cannot_be_silently_changed(self):
        altered = json.loads(json.dumps(self.fixture))
        altered["market_snapshot"]["cloud_compute"]["region"] = "Dallas, US"
        with self.assertRaises(BudgetInputError):
            validate_fixture(altered)

    def test_fixture_rejects_vendor_quote_mislabelling(self):
        altered = json.loads(json.dumps(self.fixture))
        altered["scenarios"][0]["quote_status"] = "vendor_quote"
        with self.assertRaises(BudgetInputError):
            validate_fixture(altered)

    def test_fixture_rejects_performance_parity_claim(self):
        altered = json.loads(json.dumps(self.fixture))
        altered["assumptions"]["performance_parity_measured"] = True
        with self.assertRaises(BudgetInputError):
            validate_fixture(altered)

    def test_fixture_rejects_a_cloud_price_mismatch(self):
        altered = json.loads(json.dumps(self.fixture))
        altered["scenarios"][2]["instance_hourly_price_usd"] = "4.00"
        with self.assertRaises(BudgetInputError):
            validate_fixture(altered)


if __name__ == "__main__":
    unittest.main()
