#!/usr/bin/env python3
"""Audit a deliberately synthetic teaching packet; never contacts a network."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

FIXTURE_ID = "v5-ch09-paper-reproduction-synthetic-v1"
REQUIRED_CLAIMS = {"C1", "C2", "C3"}
ROW_FIELDS = ("row_id", "target", "baseline_prediction", "reported_prediction", "rerun_prediction")


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def validate_packet(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict) or packet.get("schema_version") != 1:
        raise ValueError("packet must be a version-1 JSON object")
    if packet.get("fixture_id") != FIXTURE_ID or packet.get("synthetic") is not True:
        raise ValueError("only the declared synthetic teaching fixture is accepted")
    paper = packet.get("paper")
    if not isinstance(paper, dict) or not paper.get("title") or not paper.get("paper_version"):
        raise ValueError("paper title and version are required")
    if paper.get("status") != "fictional teaching packet; not a published study":
        raise ValueError("the teaching packet must remain explicitly fictional")

    protocol = packet.get("protocol")
    if not isinstance(protocol, dict) or protocol.get("metric") != "mae":
        raise ValueError("this lab supports only the declared MAE protocol")
    rows = protocol.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("at least one fixed synthetic observation is required")
    seen_rows: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or any(field not in row for field in ROW_FIELDS):
            raise ValueError(f"row {index} is missing a required field")
        row_id = row["row_id"]
        if not isinstance(row_id, str) or not row_id or row_id in seen_rows:
            raise ValueError(f"row {index} has an empty or duplicate row_id")
        seen_rows.add(row_id)
        for field in ROW_FIELDS[1:]:
            _finite_number(row[field], f"row {row_id} {field}")

    published = protocol.get("published")
    if not isinstance(published, dict):
        raise ValueError("published metric values are required")
    for field in ("baseline_mae", "candidate_mae", "minimum_relative_improvement", "max_absolute_metric_difference"):
        value = _finite_number(published.get(field), f"published.{field}")
        if value < 0:
            raise ValueError(f"published.{field} cannot be negative")

    claims = packet.get("claims")
    if not isinstance(claims, list):
        raise ValueError("claims must be a list")
    claim_ids = [claim.get("id") for claim in claims if isinstance(claim, dict)]
    if len(claim_ids) != len(claims) or set(claim_ids) != REQUIRED_CLAIMS or len(claim_ids) != len(REQUIRED_CLAIMS):
        raise ValueError("the fixture must contain exactly the distinct claims C1, C2, and C3")
    by_id = {claim["id"]: claim for claim in claims}

    c1 = by_id["C1"]
    artifacts = c1.get("artifacts_available")
    required_artifacts = c1.get("required_artifacts")
    if not isinstance(required_artifacts, list) or not required_artifacts or not isinstance(artifacts, dict):
        raise ValueError("C1 must declare required artifacts and their availability")
    if any(not isinstance(name, str) or not name for name in required_artifacts):
        raise ValueError("C1 artifact names must be non-empty strings")
    if any(not isinstance(artifacts.get(name), bool) for name in required_artifacts):
        raise ValueError("C1 artifact availability must be explicit booleans")

    c2 = by_id["C2"]
    c2_required = c2.get("required_artifacts")
    c2_available = c2.get("artifacts_available")
    if not isinstance(c2_required, list) or not c2_required or not isinstance(c2_available, dict):
        raise ValueError("C2 must declare required artifacts and their availability")
    if any(not isinstance(name, str) or not name for name in c2_required):
        raise ValueError("C2 artifact names must be non-empty strings")
    if any(not isinstance(c2_available.get(name), bool) for name in c2_required):
        raise ValueError("C2 artifact availability must be explicit booleans")

    c3 = by_id["C3"]
    required_groups = c3.get("required_groups")
    observed_groups = c3.get("observed_groups")
    if (not isinstance(required_groups, list) or not required_groups
            or not isinstance(observed_groups, list)
            or any(not isinstance(group, str) or not group for group in required_groups + observed_groups)):
        raise ValueError("C3 must declare non-empty group names for required and observed coverage")


def _mae(rows: list[dict[str, Any]], prediction_field: str) -> float:
    return sum(abs(float(row["target"]) - float(row[prediction_field])) for row in rows) / len(rows)


def evaluate(packet: dict[str, Any]) -> dict[str, Any]:
    """Return claim-level results without treating missing evidence as a negative result."""
    validate_packet(packet)
    protocol = packet["protocol"]
    rows = protocol["rows"]
    published = protocol["published"]
    claims = {claim["id"]: claim for claim in packet["claims"]}

    missing_c1 = [name for name in claims["C1"]["required_artifacts"]
                  if not claims["C1"]["artifacts_available"][name]]
    c1_result: dict[str, Any] = {"claim_id": "C1", "scope": claims["C1"]["scope"]}
    if missing_c1:
        c1_result.update({"status": "blocked", "missing_artifacts": missing_c1,
                          "interpretation": "اجرای ادعای محدود C1 به‌علت artifact ناقص آغاز نشد."})
    else:
        baseline_mae = _mae(rows, "baseline_prediction")
        reported_candidate_mae = _mae(rows, "reported_prediction")
        rerun_candidate_mae = _mae(rows, "rerun_prediction")
        candidate_gap = abs(rerun_candidate_mae - float(published["candidate_mae"]))
        reported_gap = abs(reported_candidate_mae - float(published["candidate_mae"]))
        baseline_gap = abs(baseline_mae - float(published["baseline_mae"]))
        relative_improvement = (baseline_mae - rerun_candidate_mae) / baseline_mae if baseline_mae > 0 else None
        within_tolerance = (
            candidate_gap <= float(published["max_absolute_metric_difference"])
            and reported_gap <= float(published["max_absolute_metric_difference"])
            and baseline_gap <= float(published["max_absolute_metric_difference"])
            and relative_improvement is not None
            and relative_improvement >= float(published["minimum_relative_improvement"])
        )
        c1_result.update({
            "status": "reproduced_within_tolerance" if within_tolerance else "not_reproduced",
            "metrics": {
                "baseline_mae": round(baseline_mae, 6),
                "reported_candidate_mae_from_rows": round(reported_candidate_mae, 6),
                "published_candidate_mae": round(float(published["candidate_mae"]), 6),
                "rerun_candidate_mae": round(rerun_candidate_mae, 6),
                "absolute_difference_from_published_candidate": round(candidate_gap, 6),
                "reported_rows_difference_from_published_candidate": round(reported_gap, 6),
                "baseline_difference_from_published": round(baseline_gap, 6),
                "relative_improvement_vs_baseline": (round(relative_improvement, 6)
                                                       if relative_improvement is not None else None),
                "max_absolute_metric_difference": float(published["max_absolute_metric_difference"]),
                "minimum_relative_improvement": float(published["minimum_relative_improvement"]),
            },
            "interpretation": (
                "روی داده و پروتکل ساختگیِ ثابت، نتیجه در تلورانس اعلام‌شده به‌دست آمد؛ این فقط یک بازتولید آموزشی است."
                if within_tolerance else
                "با artifactهای موجود، معیار پذیرش عددی برآورده نشد؛ اختلاف به‌تنهایی علت علمی یا خطای مقاله را تعیین نمی‌کند."
            ),
        })

    missing_c2 = [name for name in claims["C2"]["required_artifacts"]
                  if not claims["C2"]["artifacts_available"][name]]
    c2_result = {
        "claim_id": "C2",
        "scope": claims["C2"]["scope"],
        "status": "blocked" if missing_c2 else "not_assessed",
        "missing_artifacts": missing_c2,
        "interpretation": (
            "ادعای وابسته به checkpoint اجرا نشد؛ نبود artifact شاهدی علیه درستی ادعا نیست."
            if missing_c2 else
            "وجود artifact به‌تنهایی بازتولید ادعا را انجام نمی‌دهد؛ اجرای مستقل هنوز ارزیابی نشده است."
        ),
    }

    c3 = claims["C3"]
    missing_groups = sorted(set(c3["required_groups"]) - set(c3["observed_groups"]))
    c3_result = {
        "claim_id": "C3",
        "scope": c3["scope"],
        "status": "not_assessed",
        "missing_required_groups": missing_groups,
        "interpretation": (
            "برای تعمیم به دامنهٔ جدید، گروه/دادهٔ مستقلِ لازم در این بسته نیست؛ ادعا آزموده نشده است."
            if missing_groups else
            "دادهٔ گروه‌های لازم فهرست شده، اما تحلیل تعمیم در این پروژه پیاده‌سازی نشده است."
        ),
    }

    claim_results = [c1_result, c2_result, c3_result]
    counts: dict[str, int] = {}
    for result in claim_results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    overall = "complete_for_declared_claims" if all(
        result["status"] == "reproduced_within_tolerance" for result in claim_results
    ) else "partial_or_unassessed"
    return {
        "project_id": FIXTURE_ID,
        "paper_id": packet["paper"]["paper_id"],
        "paper_status": packet["paper"]["status"],
        "synthetic": True,
        "claim_results": claim_results,
        "status_counts": counts,
        "overall_status": overall,
        "scope_note": "این خروجی فقط کنترل fixture ساختگی را گزارش می‌کند؛ داوری دربارهٔ مقاله یا مدل واقعی نیست.",
    }


def run(packet_path: Path, output_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    packet_bytes = packet_path.read_bytes()
    packet = json.loads(packet_bytes.decode("utf-8"))
    validate_packet(packet)
    fixture_hash = hashlib.sha256(packet_bytes).hexdigest()
    manifest_path = manifest_path or packet_path.with_name("fixture_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("fixture_id") != FIXTURE_ID
            or manifest.get("sha256") != fixture_hash
            or manifest.get("synthetic") is not True
            or manifest.get("observation_count") != len(packet["protocol"]["rows"])):
        raise ValueError("fixture bytes do not match the declared manifest")
    if manifest.get("claim_ids") != ["C1", "C2", "C3"]:
        raise ValueError("fixture claim IDs do not match the declared manifest")
    result = evaluate(packet)
    result["fixture_sha256"] = fixture_hash
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=here / "synthetic_paper_packet.json")
    parser.add_argument("--manifest", type=Path, default=here / "fixture_manifest.json")
    parser.add_argument("--output", type=Path, default=here / "results.json")
    args = parser.parse_args()
    result = run(args.packet, args.output, args.manifest)
    counts = ", ".join(f"{key}={value}" for key, value in sorted(result["status_counts"].items()))
    print(f"{result['overall_status']}: {counts}; synthetic={result['synthetic']}; sha256={result['fixture_sha256']}")


if __name__ == "__main__":
    main()
