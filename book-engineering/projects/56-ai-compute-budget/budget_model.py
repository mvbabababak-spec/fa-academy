"""Transparent lifecycle-cost arithmetic for an explicitly synthetic fixture.

This module does not fetch prices, inspect hardware, offer tax/accounting advice,
or establish that different compute services deliver equivalent work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CENT = Decimal("0.01")
ZERO = Decimal("0")


class BudgetInputError(ValueError):
    """Raised when the fixture is incomplete, inconsistent, or non-finite."""


def decimal_value(value: Any, field: str) -> Decimal:
    if isinstance(value, bool):
        raise BudgetInputError(f"{field} must be a finite decimal, not a boolean")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise BudgetInputError(f"{field} must be a finite decimal") from error
    if not result.is_finite():
        raise BudgetInputError(f"{field} must be finite")
    return result


def nonnegative(value: Any, field: str) -> Decimal:
    result = decimal_value(value, field)
    if result < ZERO:
        raise BudgetInputError(f"{field} must be nonnegative")
    return result


def integer(value: Any, field: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise BudgetInputError(f"{field} must be an integer >= {minimum}")
    return value


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def energy_cost_usd(site_input_kw: Any, powered_hours: Any, rate_usd_per_kwh: Any) -> Decimal:
    """Compute meter-boundary kWh times a user-supplied USD/kWh rate."""
    kw = nonnegative(site_input_kw, "site_input_kw")
    hours = nonnegative(powered_hours, "powered_hours")
    rate = nonnegative(rate_usd_per_kwh, "rate_usd_per_kwh")
    return kw * hours * rate


def cloud_compute_cost_usd(hourly_rate_usd: Any, billed_hours: Any) -> Decimal:
    rate = nonnegative(hourly_rate_usd, "hourly_rate_usd")
    hours = nonnegative(billed_hours, "billed_hours")
    return rate * hours


def net_present_value(cashflows: list[Decimal], annual_discount_rate: Any) -> Decimal:
    """Discount costs at year-end; index 0 is the initial cash flow."""
    if not isinstance(cashflows, list) or not cashflows:
        raise BudgetInputError("cashflows must be a non-empty list")
    rate = nonnegative(annual_discount_rate, "annual_discount_rate")
    if rate >= Decimal("1"):
        raise BudgetInputError("annual_discount_rate must be less than 1 for this teaching model")
    total = ZERO
    factor = Decimal("1") + rate
    for year, amount in enumerate(cashflows):
        cash = decimal_value(amount, f"cashflows[{year}]")
        total += cash / (factor ** year)
    return total


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BudgetInputError(f"{field} must be an object")
    return value


def validate_fixture(fixture: Any) -> dict[str, Any]:
    data = _require_mapping(fixture, "fixture")
    if data.get("schema_version") != 1:
        raise BudgetInputError("unsupported schema_version")
    if data.get("fixture_id") != "v4-ch10-synthetic-budget-v1":
        raise BudgetInputError("fixture_id does not match this chapter")
    if data.get("label_source") != "synthetic_fixture":
        raise BudgetInputError("the worked case must stay labeled synthetic_fixture")

    market = _require_mapping(data.get("market_snapshot"), "market_snapshot")
    cloud = _require_mapping(market.get("cloud_compute"), "market_snapshot.cloud_compute")
    energy = _require_mapping(market.get("electricity"), "market_snapshot.electricity")
    for record, field in ((cloud, "cloud_compute"), (energy, "electricity")):
        for required in ("as_of", "market", "currency", "source_url"):
            if not isinstance(record.get(required), str) or not record[required].strip():
                raise BudgetInputError(f"market_snapshot.{field}.{required} is required")
        if not record["source_url"].startswith("https://"):
            raise BudgetInputError(f"market_snapshot.{field}.source_url must use HTTPS")
    if cloud.get("currency") != "USD" or energy.get("currency") != "USD":
        raise BudgetInputError("the chapter fixture uses USD throughout")
    nonnegative(cloud.get("price_usd_per_instance_hour"), "cloud price")
    nonnegative(energy.get("price_usd_per_kwh"), "electricity price")
    if cloud.get("region") != "us-central1 (Iowa, US)":
        raise BudgetInputError("cloud snapshot region must remain explicit")
    if energy.get("market") != "Texas, US statewide commercial average":
        raise BudgetInputError("electricity snapshot must not be presented as a Dallas tariff")

    assumptions = _require_mapping(data.get("assumptions"), "assumptions")
    horizon = integer(assumptions.get("horizon_years"), "horizon_years", minimum=1)
    discount = nonnegative(assumptions.get("annual_discount_rate"), "annual_discount_rate")
    if discount >= Decimal("1"):
        raise BudgetInputError("annual_discount_rate must be less than 1")
    if assumptions.get("price_escalation_mode") != "held_constant_for_synthetic_demo":
        raise BudgetInputError("price_escalation_mode must disclose the fixture assumption")
    if assumptions.get("performance_parity_measured") is not False:
        raise BudgetInputError("the fixture must not claim measured performance parity")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 3:
        raise BudgetInputError("exactly three teaching scenarios are required")
    seen: set[str] = set()
    for index, raw in enumerate(scenarios):
        scenario = _require_mapping(raw, f"scenarios[{index}]")
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id or scenario_id in seen:
            raise BudgetInputError(f"scenarios[{index}].id must be unique and non-empty")
        seen.add(scenario_id)
        if scenario.get("quote_status") != "synthetic_not_a_vendor_quote":
            raise BudgetInputError(f"{scenario_id} must disclose synthetic quote status")
        if scenario.get("strategy") not in {"buy", "lease", "cloud"}:
            raise BudgetInputError(f"{scenario_id}.strategy must be buy, lease, or cloud")
        integer(scenario.get("annual_deliverables"), f"{scenario_id}.annual_deliverables", minimum=1)
        nonnegative(scenario.get("annual_other_cost_usd"), f"{scenario_id}.annual_other_cost_usd")
        nonnegative(scenario.get("upfront_cost_usd"), f"{scenario_id}.upfront_cost_usd")
        if scenario["strategy"] in {"buy", "lease"}:
            nonnegative(scenario.get("site_input_kw"), f"{scenario_id}.site_input_kw")
            integer(scenario.get("annual_powered_hours"), f"{scenario_id}.annual_powered_hours")
            nonnegative(scenario.get("annual_maintenance_usd"), f"{scenario_id}.annual_maintenance_usd")
            if scenario.get("energy_price_source") != "market_snapshot.electricity":
                raise BudgetInputError(f"{scenario_id} must identify its electricity input source")
        if scenario["strategy"] == "buy":
            for key in ("acquisition_cost_usd", "residual_value_usd"):
                nonnegative(scenario.get(key), f"{scenario_id}.{key}")
        elif scenario["strategy"] == "lease":
            for key in ("monthly_lease_payment_usd", "end_of_term_buyout_usd", "residual_value_usd"):
                nonnegative(scenario.get(key), f"{scenario_id}.{key}")
        else:
            if scenario.get("price_source") != "market_snapshot.cloud_compute":
                raise BudgetInputError(f"{scenario_id} must identify the dated cloud price source")
            if decimal_value(scenario.get("instance_hourly_price_usd"), f"{scenario_id}.instance_hourly_price_usd") != decimal_value(
                cloud["price_usd_per_instance_hour"], "market cloud price"
            ):
                raise BudgetInputError("cloud scenario price differs from its dated market snapshot")
            integer(scenario.get("annual_billed_instance_hours"), f"{scenario_id}.annual_billed_instance_hours")
    return data


def _scenario_cashflows(scenario: dict[str, Any], years: int, energy_rate: Decimal, cloud_rate: Decimal) -> tuple[list[Decimal], dict[str, Any]]:
    strategy = scenario["strategy"]
    annual_deliverables = int(scenario["annual_deliverables"])
    annual_other = nonnegative(scenario["annual_other_cost_usd"], "annual_other_cost_usd")
    upfront = nonnegative(scenario["upfront_cost_usd"], "upfront_cost_usd")
    rows: list[dict[str, str]] = []

    if strategy == "buy":
        acquisition = nonnegative(scenario["acquisition_cost_usd"], "acquisition_cost_usd")
        annual_maintenance = nonnegative(scenario["annual_maintenance_usd"], "annual_maintenance_usd")
        annual_energy = energy_cost_usd(
            scenario["site_input_kw"], scenario["annual_powered_hours"], energy_rate
        )
        initial = cents(acquisition + upfront)
        recurring = cents(annual_maintenance + annual_other + annual_energy)
        residual = nonnegative(scenario["residual_value_usd"], "residual_value_usd")
        components = {
            "acquisition_usd": str(cents(acquisition)),
            "upfront_usd": str(cents(upfront)),
            "annual_energy_kwh": str(nonnegative(scenario["site_input_kw"], "site_input_kw") * Decimal(int(scenario["annual_powered_hours"]))),
            "annual_energy_cost_usd": str(cents(annual_energy)),
            "annual_maintenance_usd": str(cents(annual_maintenance)),
            "annual_other_cost_usd": str(cents(annual_other)),
            "terminal_residual_credit_usd": str(cents(residual)),
        }
        cashflows = [initial] + [recurring for _ in range(years)]
        cashflows[-1] -= cents(residual)
    elif strategy == "lease":
        monthly = nonnegative(scenario["monthly_lease_payment_usd"], "monthly_lease_payment_usd")
        annual_lease = cents(monthly * Decimal(12))
        annual_maintenance = nonnegative(scenario["annual_maintenance_usd"], "annual_maintenance_usd")
        annual_energy = energy_cost_usd(
            scenario["site_input_kw"], scenario["annual_powered_hours"], energy_rate
        )
        initial = cents(upfront)
        recurring = cents(annual_lease + annual_maintenance + annual_other + annual_energy)
        buyout = nonnegative(scenario["end_of_term_buyout_usd"], "end_of_term_buyout_usd")
        residual = nonnegative(scenario["residual_value_usd"], "residual_value_usd")
        components = {
            "upfront_usd": str(cents(upfront)),
            "annual_lease_payment_usd": str(annual_lease),
            "annual_energy_kwh": str(nonnegative(scenario["site_input_kw"], "site_input_kw") * Decimal(int(scenario["annual_powered_hours"]))),
            "annual_energy_cost_usd": str(cents(annual_energy)),
            "annual_maintenance_usd": str(cents(annual_maintenance)),
            "annual_other_cost_usd": str(cents(annual_other)),
            "terminal_buyout_usd": str(cents(buyout)),
            "terminal_residual_credit_usd": str(cents(residual)),
        }
        cashflows = [initial] + [recurring for _ in range(years)]
        cashflows[-1] += cents(buyout) - cents(residual)
    else:
        billed_hours = integer(scenario["annual_billed_instance_hours"], "annual_billed_instance_hours")
        compute = cloud_compute_cost_usd(cloud_rate, billed_hours)
        initial = cents(upfront)
        recurring = cents(compute + annual_other)
        components = {
            "upfront_usd": str(cents(upfront)),
            "annual_billed_instance_hours": billed_hours,
            "market_instance_price_usd_per_hour": str(cloud_rate),
            "annual_compute_cost_usd": str(cents(compute)),
            "annual_other_cost_usd": str(cents(annual_other)),
            "annual_energy_cost_usd": None,
            "terminal_residual_credit_usd": "0.00",
        }
        cashflows = [initial] + [recurring for _ in range(years)]

    return cashflows, {
        "id": scenario["id"],
        "strategy": strategy,
        "market": scenario.get("market", "synthetic classroom case"),
        "quote_status": scenario["quote_status"],
        "annual_deliverables_assumed": annual_deliverables,
        "total_deliverables_assumed": annual_deliverables * years,
        "components": components,
        "cashflows_year_0_to_horizon_usd": [str(cents(value)) for value in cashflows],
    }


def build_results(fixture: Any, fixture_bytes: bytes) -> dict[str, Any]:
    data = validate_fixture(fixture)
    assumptions = data["assumptions"]
    horizon = int(assumptions["horizon_years"])
    discount = nonnegative(assumptions["annual_discount_rate"], "annual_discount_rate")
    energy_rate = nonnegative(data["market_snapshot"]["electricity"]["price_usd_per_kwh"], "electricity price")
    cloud_rate = nonnegative(data["market_snapshot"]["cloud_compute"]["price_usd_per_instance_hour"], "cloud price")
    scenarios_out = []
    for scenario in data["scenarios"]:
        flows, details = _scenario_cashflows(scenario, horizon, energy_rate, cloud_rate)
        nominal = sum(flows, ZERO)
        npv_value = net_present_value(flows, discount)
        outputs = details["total_deliverables_assumed"]
        details.update({
            "nominal_tco_usd": str(cents(nominal)),
            "npv_tco_usd": str(cents(npv_value)),
            "npv_cost_per_synthetic_deliverable_usd": str(cents(npv_value / Decimal(outputs))),
        })
        scenarios_out.append(details)
    return {
        "result_schema_version": 1,
        "fixture_id": data["fixture_id"],
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "currency": "USD",
        "horizon_years": horizon,
        "annual_discount_rate": str(discount),
        "cashflow_timing": "initial cost at year 0; recurring costs at year end; residual/buyout at horizon; yearly cashflows rounded to cents",
        "market_snapshot": data["market_snapshot"],
        "scenarios": scenarios_out,
        "comparison_status": {
            "performance_parity_measured": False,
            "synthetic_deliverables_are_not_benchmarks": True,
            "purchase_and_lease_amounts_are_vendor_quotes": False,
            "prices_escalated": False,
            "taxes_and_financing_costs_included": False,
            "complete_invoice_or_cost_estimate": False,
        },
        "limitations": [
            "Purchase and lease amounts and annual usage are synthetic assumptions, not offers or market quotes.",
            "The dated cloud list price is one US region snapshot; it is not an all-in invoice or future price guarantee.",
            "The Texas commercial electricity value is a statewide average, not a Dallas customer tariff or marginal bill rate.",
            "Equal synthetic deliverables do not demonstrate equal throughput, quality, availability, or workload suitability.",
            "Taxes, financing, inflation, escalation, demand charges, depreciation rules, downtime, labor, replacement, and all charges not explicit in the fixture are excluded.",
        ],
    }


def load_and_run(fixture_path: Path) -> dict[str, Any]:
    raw = fixture_path.read_bytes()
    try:
        fixture = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BudgetInputError(f"cannot parse fixture: {error}") from error
    return build_results(fixture, raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate a synthetic three-way compute TCO illustration")
    parser.add_argument("--fixture", type=Path, default=ROOT / "sample_budget.json")
    parser.add_argument("--output", type=Path, help="write deterministic JSON results instead of stdout")
    args = parser.parse_args()
    try:
        result = load_and_run(args.fixture)
    except (OSError, BudgetInputError) as error:
        parser.error(str(error))
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
