"""Validate the structure of a synthetic AI-governance evidence pack."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = ROOT / "governance_pack.json"
SCHEMA_VERSION = "1.0"
SEVERITY_LEVELS = {"low", "moderate", "high", "critical"}
LIKELIHOOD_LEVELS = {"rare", "possible", "likely"}
TREATMENTS = {"avoid", "mitigate", "transfer", "accept"}
EVIDENCE_STATES = {"planned", "fixture_only", "reviewed"}
RISK_STATES = {"planned", "in_progress", "mitigated", "accepted"}


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_text_items(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_has_text(item) for item in value)


def _is_allowed(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def _require_fields(value: Any, fields: tuple[str, ...], path: str,
                    errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return
    for field in fields:
        if not _has_text(value.get(field)):
            errors.append(f"{path}.{field} must be a non-empty string")


def validate_pack(pack: Any) -> list[str]:
    """Return schema/completeness errors; this function is not a compliance audit."""
    errors: list[str] = []
    if not isinstance(pack, dict):
        return ["pack must be a JSON object"]

    if pack.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION!r}")
    if not _has_text(pack.get("pack_id")):
        errors.append("pack_id must be a non-empty string")
    if not _has_text(pack.get("fixture_id")):
        errors.append("fixture_id must be a non-empty string")

    system = pack.get("system")
    _require_fields(
        system,
        ("system_id", "name", "provider", "deployer", "version", "intended_use", "review_by"),
        "system",
        errors,
    )
    if isinstance(system, dict):
        if not _has_text_items(system.get("out_of_scope_uses")):
            errors.append("system.out_of_scope_uses must be a non-empty list of non-empty strings")
        try:
            date.fromisoformat(system.get("review_by", ""))
        except (TypeError, ValueError):
            errors.append("system.review_by must be an ISO date")

    model_card = pack.get("model_card")
    _require_fields(
        model_card,
        ("model_id", "provider", "revision", "intended_use", "evaluation_status"),
        "model_card",
        errors,
    )
    if isinstance(model_card, dict) and not _has_text_items(model_card.get("limitations")):
        errors.append("model_card.limitations must be a non-empty list of non-empty strings")

    evidence = pack.get("evidence")
    evidence_ids: set[str] = set()
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
        evidence = []
    for index, item in enumerate(evidence):
        path = f"evidence[{index}]"
        _require_fields(item, ("id", "kind", "scope"), path, errors)
        if not isinstance(item, dict):
            continue
        evidence_id = item.get("id")
        if _has_text(evidence_id):
            if evidence_id in evidence_ids:
                errors.append(f"{path}.id is duplicated: {evidence_id}")
            evidence_ids.add(evidence_id)
        if not _is_allowed(item.get("status"), EVIDENCE_STATES):
            errors.append(f"{path}.status must be one of {sorted(EVIDENCE_STATES)}")

    data_cards = pack.get("dataset_cards")
    if not isinstance(data_cards, list) or not data_cards:
        errors.append("dataset_cards must be a non-empty list")
        data_cards = []
    dataset_ids: set[str] = set()
    for index, card in enumerate(data_cards):
        path = f"dataset_cards[{index}]"
        _require_fields(
            card,
            ("dataset_id", "name", "source", "collection_method", "license_status", "intended_use", "review_by"),
            path,
            errors,
        )
        if not isinstance(card, dict):
            continue
        dataset_id = card.get("dataset_id")
        if _has_text(dataset_id):
            if dataset_id in dataset_ids:
                errors.append(f"{path}.dataset_id is duplicated: {dataset_id}")
            dataset_ids.add(dataset_id)
        if not _has_text_items(card.get("known_gaps")):
            errors.append(f"{path}.known_gaps must be a non-empty list of non-empty strings, including known unknowns")
        if not isinstance(card.get("personal_data"), bool):
            errors.append(f"{path}.personal_data must be an explicit boolean")
        try:
            date.fromisoformat(card.get("review_by", ""))
        except (TypeError, ValueError):
            errors.append(f"{path}.review_by must be an ISO date")

    risks = pack.get("risk_register")
    if not isinstance(risks, list) or not risks:
        errors.append("risk_register must be a non-empty list")
        risks = []
    risk_ids: set[str] = set()
    high_residual_open = []
    for index, risk in enumerate(risks):
        path = f"risk_register[{index}]"
        if not isinstance(risk, dict):
            errors.append(f"{path} must be an object")
            continue
        for field in ("id", "scenario", "control_owner"):
            if not _has_text(risk.get(field)):
                errors.append(f"{path}.{field} must be a non-empty string")
        risk_id = risk.get("id")
        if _has_text(risk_id):
            if risk_id in risk_ids:
                errors.append(f"{path}.id is duplicated: {risk_id}")
            risk_ids.add(risk_id)
        if not _has_text_items(risk.get("affected_parties")):
            errors.append(f"{path}.affected_parties must be a non-empty list of non-empty strings")
        if not _is_allowed(risk.get("inherent_severity"), SEVERITY_LEVELS):
            errors.append(f"{path}.inherent_severity is not a defined qualitative level")
        if not _is_allowed(risk.get("residual_severity"), SEVERITY_LEVELS):
            errors.append(f"{path}.residual_severity is not a defined qualitative level")
        if not _is_allowed(risk.get("inherent_likelihood"), LIKELIHOOD_LEVELS):
            errors.append(f"{path}.inherent_likelihood is not a defined qualitative level")
        if not _is_allowed(risk.get("treatment"), TREATMENTS):
            errors.append(f"{path}.treatment must be one of {sorted(TREATMENTS)}")
        if not _is_allowed(risk.get("status"), RISK_STATES):
            errors.append(f"{path}.status must be one of {sorted(RISK_STATES)}")
        if not _has_text_items(risk.get("controls")):
            errors.append(f"{path}.controls must be a non-empty list of non-empty strings")
        refs = risk.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{path}.evidence_refs must be a non-empty list")
        elif any(not _has_text(ref) for ref in refs):
            errors.append(f"{path}.evidence_refs must contain non-empty string ids")
        elif any(ref not in evidence_ids for ref in refs):
            errors.append(f"{path}.evidence_refs contains an unknown evidence id")
        if _is_allowed(risk.get("residual_severity"), {"high", "critical"}) and risk.get("status") != "accepted":
            high_residual_open.append(risk_id or f"risk-{index}")

    decision = pack.get("decision")
    if not isinstance(decision, dict):
        errors.append("decision must be an object")
        decision = {}
    if not _is_allowed(decision.get("gate_status"), {"hold", "approved", "rejected"}):
        errors.append("decision.gate_status must be hold, approved, or rejected")
    if not _has_text(decision.get("rationale")):
        errors.append("decision.rationale must be a non-empty string")
    if decision.get("gate_status") == "approved":
        if not _has_text(decision.get("approved_by")) or not _has_text(decision.get("approved_at")):
            errors.append("an approved gate needs a named human approver and approval date")
        if high_residual_open:
            errors.append("an approved gate cannot leave high or critical residual risks without explicit acceptance")

    return errors


def analyze(pack: Any, fixture_bytes: bytes) -> dict[str, Any]:
    """Produce a deterministic schema-check report without authorizing deployment."""
    errors = validate_pack(pack)
    risks = pack.get("risk_register", []) if isinstance(pack, dict) else []
    evidence = pack.get("evidence", []) if isinstance(pack, dict) else []
    decision = pack.get("decision", {}) if isinstance(pack, dict) else {}
    if not isinstance(risks, list):
        risks = []
    if not isinstance(evidence, list):
        evidence = []
    if not isinstance(decision, dict):
        decision = {}
    return {
        "fixture_id": pack.get("fixture_id") if isinstance(pack, dict) else None,
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "risk_count": len(risks),
        "evidence_count": len(evidence),
        "structurally_valid": not errors,
        "validation_errors": errors,
        "gate_status": decision.get("gate_status"),
        "release_authorized": False,
        "scope": (
            "Structural validation of one synthetic governance pack only; "
            "not a compliance audit, certification, legal opinion, or release authorization."
        ),
        "limitations": [
            "The fixture is synthetic and contains no personal data, actual model, or production evidence.",
            "The validator checks field presence and internal references, not the truth, quality, or sufficiency of evidence.",
            "Qualitative severity and likelihood labels are not probabilities and are not aggregated into a numeric score.",
            "A valid schema does not establish legal applicability, conformity, safety, fairness, privacy, or fitness for use.",
            "The release_authorized field is always false; approval belongs to an accountable human process.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    args = parser.parse_args()
    fixture_bytes = args.fixture.read_bytes()
    pack = json.loads(fixture_bytes.decode("utf-8"))
    result = analyze(pack, fixture_bytes)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote synthetic governance-pack validation: {args.output}")
    else:
        print(rendered, end="")
    return 0 if result["structurally_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
