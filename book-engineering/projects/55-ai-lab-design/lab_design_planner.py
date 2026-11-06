"""Arithmetic-only lab design checks using synthetic, user-declared profiles.

This tool is not a hardware selector, benchmark, electrical-code checker, or
engineering approval. It compares supplied requirements with supplied design
limits and reports the assumptions it used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v4-ch09-lab-design-v1"
BTU_PER_HOUR_PER_WATT = 3.412141633
DEFAULT_FIXTURE = Path(__file__).with_name("sample_labs.json")
REQUIRED_FALSE_METADATA = (
    "real_hardware_measured",
    "real_workload_run",
    "vendor_skus_included",
    "prices_included",
    "benchmark_performed",
    "electrical_code_checked",
    "installation_performed",
    "training_performed",
)
ALLOWED_TIERS = {
    "personal-low-cost",
    "independent-professional",
    "organizational-cluster",
    "synthetic-underprovisioned",
}


class DesignInputError(ValueError):
    """Raised when a lab-design fixture is malformed or unsafe to interpret."""


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignInputError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DesignInputError(f"{path} must be a non-empty string")
    return value.strip()


def _number(value: Any, path: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DesignInputError(f"{path} must be a number")
    number = float(value)
    if not math.isfinite(number) or number < minimum:
        raise DesignInputError(f"{path} must be finite and at least {minimum}")
    return number


def _integer(value: Any, path: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise DesignInputError(f"{path} must be an integer at least {minimum}")
    return value


def _string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise DesignInputError(f"{path} must be a list")
    result = [_string(item, f"{path}[{index}]") for index, item in enumerate(value)]
    if len(set(result)) != len(result):
        raise DesignInputError(f"{path} must not contain duplicates")
    return result


def _validate_storage(storage: Any, path: str) -> None:
    storage = _mapping(storage, path)
    for field in ("dataset_tb", "checkpoint_size_tb", "scratch_tb", "backup_tb"):
        _number(storage.get(field), f"{path}.{field}")
    _integer(storage.get("working_copies"), f"{path}.working_copies", minimum=1)
    _integer(storage.get("checkpoint_versions"), f"{path}.checkpoint_versions", minimum=0)


def validate_fixture(fixture: Any) -> None:
    """Validate schema and explicit boundaries; this never verifies real equipment."""
    fixture = _mapping(fixture, "fixture")
    if fixture.get("schema_version") != SCHEMA_VERSION:
        raise DesignInputError(f"fixture.schema_version must equal {SCHEMA_VERSION}")
    _string(fixture.get("fixture_id"), "fixture.fixture_id")
    if fixture.get("label_source") != "synthetic_fixture":
        raise DesignInputError("fixture.label_source must be synthetic_fixture")

    metadata = _mapping(fixture.get("metadata"), "fixture.metadata")
    for field in REQUIRED_FALSE_METADATA:
        if metadata.get(field) is not False:
            raise DesignInputError(f"fixture.metadata.{field} must be false")

    policy = _mapping(fixture.get("policy"), "fixture.policy")
    usable_fraction = _number(policy.get("usable_vram_fraction"), "fixture.policy.usable_vram_fraction")
    if not 0 < usable_fraction <= 1:
        raise DesignInputError("fixture.policy.usable_vram_fraction must be in (0, 1]")
    _number(policy.get("cooling_design_factor"), "fixture.policy.cooling_design_factor", minimum=1.0)
    _string(policy.get("policy_note"), "fixture.policy.policy_note")

    profiles = fixture.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise DesignInputError("fixture.profiles must be a non-empty list")
    identifiers: set[str] = set()
    for index, raw_profile in enumerate(profiles):
        path = f"fixture.profiles[{index}]"
        profile = _mapping(raw_profile, path)
        identifier = _string(profile.get("profile_id"), f"{path}.profile_id")
        if identifier in identifiers:
            raise DesignInputError(f"duplicate profile_id: {identifier}")
        identifiers.add(identifier)
        tier = _string(profile.get("tier"), f"{path}.tier")
        if tier not in ALLOWED_TIERS:
            raise DesignInputError(f"{path}.tier is not an allowed synthetic tier")
        _string(profile.get("topology"), f"{path}.topology")

        workload = _mapping(profile.get("workload"), f"{path}.workload")
        _integer(workload.get("minimum_nodes"), f"{path}.workload.minimum_nodes", minimum=1)
        _integer(workload.get("accelerators_per_node"), f"{path}.workload.accelerators_per_node", minimum=1)
        _number(workload.get("minimum_vram_gib_per_accelerator"), f"{path}.workload.minimum_vram_gib_per_accelerator", minimum=0.000001)
        _number(workload.get("minimum_host_ram_gib"), f"{path}.workload.minimum_host_ram_gib", minimum=0.000001)
        _validate_storage(workload.get("storage"), f"{path}.workload.storage")
        _number(workload.get("minimum_nominal_interconnect_gbps"), f"{path}.workload.minimum_nominal_interconnect_gbps")
        _string_list(workload.get("required_runtime_stack"), f"{path}.workload.required_runtime_stack")

        design = _mapping(profile.get("design"), f"{path}.design")
        _integer(design.get("node_count"), f"{path}.design.node_count", minimum=1)
        _integer(design.get("accelerators_per_node"), f"{path}.design.accelerators_per_node", minimum=1)
        _number(design.get("vram_gib_per_accelerator"), f"{path}.design.vram_gib_per_accelerator", minimum=0.000001)
        _number(design.get("host_ram_gib"), f"{path}.design.host_ram_gib", minimum=0.000001)
        _integer(design.get("documented_accelerator_positions_per_node"), f"{path}.design.documented_accelerator_positions_per_node", minimum=0)
        _number(design.get("usable_storage_tb"), f"{path}.design.usable_storage_tb")
        _number(design.get("estimated_component_dc_load_w_per_node"), f"{path}.design.estimated_component_dc_load_w_per_node")
        _number(design.get("psu_dc_capacity_w_per_node"), f"{path}.design.psu_dc_capacity_w_per_node", minimum=0.000001)
        _number(design.get("system_peak_input_w_per_node"), f"{path}.design.system_peak_input_w_per_node")
        _number(design.get("network_gear_input_w_total"), f"{path}.design.network_gear_input_w_total")
        _number(design.get("other_it_input_w_total"), f"{path}.design.other_it_input_w_total")
        _number(design.get("site_approved_input_capacity_w"), f"{path}.design.site_approved_input_capacity_w", minimum=0.000001)
        _number(design.get("cooling_capacity_btu_per_hour"), f"{path}.design.cooling_capacity_btu_per_hour", minimum=0.000001)
        _number(design.get("nominal_interconnect_gbps"), f"{path}.design.nominal_interconnect_gbps")
        _string_list(design.get("declared_runtime_stack"), f"{path}.design.declared_runtime_stack")
        _string(design.get("basis_note"), f"{path}.design.basis_note")


def load_fixture(path: str | Path = DEFAULT_FIXTURE) -> tuple[dict[str, Any], str]:
    """Load, hash and validate a UTF-8 JSON fixture."""
    fixture_path = Path(path)
    try:
        raw = fixture_path.read_bytes()
        fixture = json.loads(raw.decode("utf-8"))
    except FileNotFoundError as exc:
        raise DesignInputError(f"fixture not found: {fixture_path}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DesignInputError(f"fixture is not valid UTF-8 JSON: {fixture_path}") from exc
    validate_fixture(fixture)
    return fixture, hashlib.sha256(raw).hexdigest()


def required_storage_tb(storage: dict[str, Any]) -> float:
    """Sum user-declared active data, working copies, checkpoints, scratch and backups."""
    _validate_storage(storage, "storage")
    return (
        float(storage["dataset_tb"]) * int(storage["working_copies"])
        + float(storage["checkpoint_size_tb"]) * int(storage["checkpoint_versions"])
        + float(storage["scratch_tb"])
        + float(storage["backup_tb"])
    )


def _check(name: str, passed: bool, **details: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), **details}


def evaluate_profile(profile: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Compare the profile's declared arithmetic inputs; never probe a device."""
    workload = profile["workload"]
    design = profile["design"]
    node_count = int(design["node_count"])
    usable_vram = float(design["vram_gib_per_accelerator"]) * float(policy["usable_vram_fraction"])
    required_storage = required_storage_tb(workload["storage"])
    total_site_input = (
        node_count * float(design["system_peak_input_w_per_node"])
        + float(design["network_gear_input_w_total"])
        + float(design["other_it_input_w_total"])
    )
    heat_load = total_site_input * BTU_PER_HOUR_PER_WATT
    cooling_required = heat_load * float(policy["cooling_design_factor"])
    required_stack = set(workload["required_runtime_stack"])
    declared_stack = set(design["declared_runtime_stack"])

    checks = [
        _check(
            "minimum_nodes",
            node_count >= int(workload["minimum_nodes"]),
            required=int(workload["minimum_nodes"]), available=node_count,
        ),
        _check(
            "accelerators_per_node",
            int(design["accelerators_per_node"]) >= int(workload["accelerators_per_node"]),
            required=int(workload["accelerators_per_node"]), available=int(design["accelerators_per_node"]),
        ),
        _check(
            "per_accelerator_memory",
            usable_vram >= float(workload["minimum_vram_gib_per_accelerator"]),
            required_gib=round(float(workload["minimum_vram_gib_per_accelerator"]), 6),
            declared_capacity_gib=round(float(design["vram_gib_per_accelerator"]), 6),
            usable_capacity_gib=round(usable_vram, 6),
            usable_fraction=float(policy["usable_vram_fraction"]),
        ),
        _check(
            "host_ram",
            float(design["host_ram_gib"]) >= float(workload["minimum_host_ram_gib"]),
            required_gib=round(float(workload["minimum_host_ram_gib"]), 6),
            available_gib=round(float(design["host_ram_gib"]), 6),
        ),
        _check(
            "documented_accelerator_positions",
            int(design["documented_accelerator_positions_per_node"]) >= int(design["accelerators_per_node"]),
            required=int(design["accelerators_per_node"]),
            declared_available=int(design["documented_accelerator_positions_per_node"]),
        ),
        _check(
            "usable_storage",
            float(design["usable_storage_tb"]) >= required_storage,
            required_tb=round(required_storage, 6),
            available_tb=round(float(design["usable_storage_tb"]), 6),
        ),
        _check(
            "declared_psu_output_capacity",
            float(design["psu_dc_capacity_w_per_node"]) >= float(design["estimated_component_dc_load_w_per_node"]),
            estimated_component_load_w_per_node=round(float(design["estimated_component_dc_load_w_per_node"]), 6),
            declared_psu_output_w_per_node=round(float(design["psu_dc_capacity_w_per_node"]), 6),
            arithmetic_headroom_w_per_node=round(
                float(design["psu_dc_capacity_w_per_node"]) - float(design["estimated_component_dc_load_w_per_node"]), 6
            ),
        ),
        _check(
            "site_input_power_allocation",
            total_site_input <= float(design["site_approved_input_capacity_w"]),
            planned_input_w=round(total_site_input, 6),
            user_declared_approved_capacity_w=round(float(design["site_approved_input_capacity_w"]), 6),
            arithmetic_margin_w=round(float(design["site_approved_input_capacity_w"]) - total_site_input, 6),
        ),
        _check(
            "cooling_capacity_screen",
            float(design["cooling_capacity_btu_per_hour"]) >= cooling_required,
            estimated_it_heat_btu_per_hour=round(heat_load, 6),
            fixture_policy_factor=float(policy["cooling_design_factor"]),
            screened_requirement_btu_per_hour=round(cooling_required, 6),
            user_declared_capacity_btu_per_hour=round(float(design["cooling_capacity_btu_per_hour"]), 6),
        ),
        _check(
            "nominal_interconnect_rate",
            float(design["nominal_interconnect_gbps"]) >= float(workload["minimum_nominal_interconnect_gbps"]),
            minimum_nominal_gbps=round(float(workload["minimum_nominal_interconnect_gbps"]), 6),
            declared_nominal_gbps=round(float(design["nominal_interconnect_gbps"]), 6),
        ),
        _check(
            "declared_runtime_stack",
            required_stack.issubset(declared_stack),
            required=sorted(required_stack),
            declared=sorted(declared_stack),
            missing=sorted(required_stack - declared_stack),
        ),
    ]
    passed = all(item["passed"] for item in checks)
    return {
        "profile_id": profile["profile_id"],
        "tier": profile["tier"],
        "topology": profile["topology"],
        "status": "paper_feasible" if passed else "needs_revision",
        "inputs_are_synthetic": True,
        "derived": {
            "required_storage_tb": round(required_storage, 6),
            "total_site_input_power_w": round(total_site_input, 6),
            "estimated_it_heat_btu_per_hour": round(heat_load, 6),
            "screened_cooling_requirement_btu_per_hour": round(cooling_required, 6),
            "per_accelerator_usable_vram_gib": round(usable_vram, 6),
        },
        "checks": checks,
        "limitations": [
            "Declared capacities and compatibility notes were not checked against physical devices.",
            "Nominal network rate is not measured throughput or application performance.",
            "Power, cooling and storage calculations are first-order screens, not code or engineering approval.",
        ],
    }


def run_demo(fixture_path: str | Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    """Return deterministic results for all synthetic lab profiles."""
    fixture, digest = load_fixture(fixture_path)
    policy = fixture["policy"]
    profiles = [evaluate_profile(profile, policy) for profile in fixture["profiles"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture": {
            "fixture_id": fixture["fixture_id"],
            "sha256": digest,
            "label_source": fixture["label_source"],
        },
        "scope": {
            "real_hardware_measured": False,
            "real_workload_run": False,
            "vendor_skus_included": False,
            "prices_included": False,
            "benchmark_performed": False,
            "electrical_code_checked": False,
            "installation_performed": False,
            "training_performed": False,
            "claim": "synthetic declared-capacity arithmetic only; not a bill of materials or deployment approval",
        },
        "policy": {
            "usable_vram_fraction": float(policy["usable_vram_fraction"]),
            "cooling_design_factor": float(policy["cooling_design_factor"]),
            "policy_note": policy["policy_note"],
        },
        "summary": {
            "profiles": len(profiles),
            "paper_feasible": sum(profile["status"] == "paper_feasible" for profile in profiles),
            "needs_revision": sum(profile["status"] == "needs_revision" for profile in profiles),
        },
        "profiles": profiles,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check declared lab-design capacity arithmetic")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write JSON report to a file (default: stdout)")
    args = parser.parse_args(argv)
    try:
        result = run_demo(args.fixture)
    except DesignInputError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    serialized = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(f"Wrote synthetic design screen: {args.output}")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
