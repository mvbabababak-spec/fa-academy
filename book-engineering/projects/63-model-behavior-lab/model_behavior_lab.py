"""Audit a deliberately synthetic model-behavior fixture.

This teaching utility computes descriptive claim-evidence, group-slice,
calibration, paired-perturbation, and toy-linear-explanation summaries. It does
not load a model, retrieve real evidence, infer social fairness, or certify safety.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = ROOT / "synthetic_behavior_fixture.json"
CLAIM_STATUSES = {"supported", "contradicted", "unverified"}


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _binary(value: Any, name: str) -> int:
    if type(value) is not int or value not in (0, 1):
        raise ValueError(f"{name} must be integer 0 or 1")
    return value


def _unique_ids(rows: list[dict[str, Any]], name: str) -> None:
    ids = [row.get("id") for row in rows]
    if any(not isinstance(item, str) or not item.strip() for item in ids):
        raise ValueError(f"{name} rows need non-empty string IDs")
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name} IDs must be unique")


def validate_fixture(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict) or data.get("synthetic") is not True:
        raise ValueError("fixture must explicitly identify itself as synthetic")
    if data.get("fixture_id") != "v5-ch02-synthetic-behavior-v1":
        raise ValueError("unexpected fixture_id")
    required = ("claims", "classification_cases", "robustness_pairs", "explanation_cases")
    for key in required:
        if not isinstance(data.get(key), list) or not data[key]:
            raise ValueError(f"{key} must be a non-empty list")
        _unique_ids(data[key], key)

    for row in data["claims"]:
        if row.get("status") not in CLAIM_STATUSES:
            raise ValueError(f"claim {row.get('id')} has an unsupported evidence status")
        if not isinstance(row.get("evidence_id"), str) or not row["evidence_id"].strip():
            raise ValueError(f"claim {row.get('id')} needs a fixture evidence_id")

    for row in data["classification_cases"]:
        _binary(row.get("label"), f"{row.get('id')}.label")
        probability = _finite_number(row.get("probability_positive"), f"{row.get('id')}.probability_positive")
        if not 0.0 <= probability <= 1.0:
            raise ValueError(f"{row.get('id')}.probability_positive must be in [0, 1]")
        group = row.get("group")
        if not isinstance(group, str) or not group.strip():
            raise ValueError(f"{row.get('id')} needs a non-empty synthetic group label")

    for row in data["robustness_pairs"]:
        _binary(row.get("true_label"), f"{row.get('id')}.true_label")
        _binary(row.get("baseline_prediction"), f"{row.get('id')}.baseline_prediction")
        _binary(row.get("variant_prediction"), f"{row.get('id')}.variant_prediction")
        if row.get("label_preserving") is not True:
            raise ValueError(f"{row.get('id')} is not declared label-preserving in the synthetic fixture")
        if not isinstance(row.get("transformation"), str) or not row["transformation"].strip():
            raise ValueError(f"{row.get('id')} needs a transformation label")

    for row in data["explanation_cases"]:
        _finite_number(row.get("intercept"), f"{row.get('id')}.intercept")
        weights, features = row.get("weights"), row.get("features")
        if not isinstance(weights, dict) or not isinstance(features, dict) or not weights:
            raise ValueError(f"{row.get('id')} needs non-empty weights and features")
        if set(weights) != set(features):
            raise ValueError(f"{row.get('id')} weight and feature names must match")
        for name in weights:
            _finite_number(weights[name], f"{row.get('id')}.weights.{name}")
            _finite_number(features[name], f"{row.get('id')}.features.{name}")
    return data


def audit_claim_evidence(claims: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {status: 0 for status in sorted(CLAIM_STATUSES)}
    for row in claims:
        counts[row["status"]] += 1
    resolved = counts["supported"] + counts["contradicted"]
    return {
        "claim_count": len(claims),
        "counts_by_fixture_status": counts,
        "resolved_count": resolved,
        "support_fraction_among_resolved": counts["supported"] / resolved if resolved else None,
        "unverified_count_excluded_from_denominator": counts["unverified"],
        "interpretation": "fixture evidence labels only; not a measured hallucination rate or a truth oracle",
    }


def _classification_metrics(rows: list[dict[str, Any]], bins: int = 5) -> dict[str, Any]:
    tp = tn = fp = fn = 0
    brier_total = 0.0
    confidence_rows: list[tuple[float, int]] = []
    for row in rows:
        label = row["label"]
        probability = float(row["probability_positive"])
        prediction = int(probability >= 0.5)
        if prediction == 1 and label == 1:
            tp += 1
        elif prediction == 0 and label == 0:
            tn += 1
        elif prediction == 1 and label == 0:
            fp += 1
        else:
            fn += 1
        brier_total += (probability - label) ** 2
        confidence = probability if prediction == 1 else 1.0 - probability
        confidence_rows.append((confidence, int(prediction == label)))

    total = len(rows)
    accuracy = (tp + tn) / total if total else None
    calibration_bins: list[dict[str, Any]] = []
    ece = 0.0
    for index in range(bins):
        lower = 0.5 + 0.5 * index / bins
        upper = 0.5 + 0.5 * (index + 1) / bins
        members = [
            (confidence, correct)
            for confidence, correct in confidence_rows
            if (
                lower <= confidence <= upper
                if index == bins - 1
                else lower <= confidence < upper
            )
        ]
        mean_confidence = sum(item[0] for item in members) / len(members) if members else None
        bin_accuracy = sum(item[1] for item in members) / len(members) if members else None
        gap = abs(mean_confidence - bin_accuracy) if members else None
        if members:
            ece += len(members) / total * float(gap)
        calibration_bins.append({
            "lower_inclusive": round(lower, 6),
            "upper_inclusive": index == bins - 1,
            "upper": round(upper, 6),
            "count": len(members),
            "mean_confidence": mean_confidence,
            "accuracy": bin_accuracy,
            "absolute_gap": gap,
        })

    return {
        "count": total,
        "threshold": 0.5,
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "accuracy": accuracy,
        "true_positive_rate": tp / (tp + fn) if tp + fn else None,
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "brier_score": brier_total / total if total else None,
        "top_label_ece_equal_width_5_bins": ece if total else None,
        "calibration_bins": calibration_bins,
        "calibration_note": "top-label ECE depends on binning and sample size; it is not a complete calibration certificate",
    }


def audit_classification(cases: list[dict[str, Any]]) -> dict[str, Any]:
    overall = _classification_metrics(cases)
    groups = sorted({row["group"] for row in cases})
    by_group = {
        group: _classification_metrics([row for row in cases if row["group"] == group])
        for group in groups
    }

    def gap(metric: str) -> float | None:
        values = [item[metric] for item in by_group.values() if item[metric] is not None]
        return max(values) - min(values) if len(values) >= 2 else None

    return {
        "overall": overall,
        "synthetic_group_slices": by_group,
        "max_absolute_group_gap": {
            "accuracy": gap("accuracy"),
            "true_positive_rate": gap("true_positive_rate"),
            "false_positive_rate": gap("false_positive_rate"),
        },
        "scope": "descriptive fixture slices; no real population, protected group, or fairness criterion is represented",
    }


def audit_robustness_pairs(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(pairs)
    unchanged = sum(row["baseline_prediction"] == row["variant_prediction"] for row in pairs)
    baseline_correct = sum(row["baseline_prediction"] == row["true_label"] for row in pairs)
    variant_correct = sum(row["variant_prediction"] == row["true_label"] for row in pairs)
    return {
        "label_preserving_pair_count": count,
        "prediction_consistency": unchanged / count if count else None,
        "prediction_changed_count": count - unchanged,
        "baseline_accuracy_on_pairs": baseline_correct / count if count else None,
        "variant_accuracy_on_pairs": variant_correct / count if count else None,
        "accuracy_difference_variant_minus_baseline": (variant_correct - baseline_correct) / count if count else None,
        "interpretation": "synthetic paired stress cases only; transformations are not human-validated and this is not an adversarial-security test",
    }


def audit_toy_explanations(rows: list[dict[str, Any]]) -> dict[str, Any]:
    case_results = []
    max_additivity_error = 0.0
    max_ablation_error = 0.0
    for row in rows:
        contributions = {
            name: float(row["weights"][name]) * float(row["features"][name])
            for name in sorted(row["weights"])
        }
        score = float(row["intercept"]) + sum(contributions.values())
        reconstructed = float(row["intercept"]) + sum(contributions.values())
        additivity_error = abs(score - reconstructed)
        max_additivity_error = max(max_additivity_error, additivity_error)
        ablation_errors = {}
        for name in contributions:
            ablated_score = float(row["intercept"]) + sum(
                contribution for other, contribution in contributions.items() if other != name
            )
            ablation_delta = score - ablated_score
            ablation_errors[name] = abs(ablation_delta - contributions[name])
            max_ablation_error = max(max_ablation_error, ablation_errors[name])
        top_feature = max(contributions, key=lambda name: abs(contributions[name]))
        case_results.append({
            "id": row["id"],
            "toy_score": score,
            "contributions": contributions,
            "largest_absolute_contribution": top_feature,
            "additivity_error": additivity_error,
            "ablation_errors": ablation_errors,
        })
    return {
        "case_count": len(rows),
        "max_additivity_error": max_additivity_error,
        "max_ablation_error": max_ablation_error,
        "cases": case_results,
        "interpretation": "arithmetic checks for a known toy linear function only; not evidence of causal or human-faithful explanations for a black-box model",
    }


def analyze(data: dict[str, Any], fixture_bytes: bytes) -> dict[str, Any]:
    validate_fixture(data)
    return {
        "fixture_id": data["fixture_id"],
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "claim_evidence_audit": audit_claim_evidence(data["claims"]),
        "classification_audit": audit_classification(data["classification_cases"]),
        "paired_robustness_audit": audit_robustness_pairs(data["robustness_pairs"]),
        "toy_explanation_audit": audit_toy_explanations(data["explanation_cases"]),
        "limitations": [
            "All records, labels, evidence statuses, groups, probabilities, transformations, and model scores are synthetic.",
            "No real language model, external source, human annotation, or deployment was queried.",
            "Small group slices and calibration bins are descriptive; no confidence interval or significance test is estimated.",
            "Fixture evidence support is not a truth oracle; unresolved claims are excluded from the support fraction.",
            "The perturbation pairs are not human-validated, and robustness to these pairs does not imply robustness to distribution shift or attack.",
            "Toy linear additivity does not establish the faithfulness, causality, or usefulness of post-hoc explanations for a black-box model.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    args = parser.parse_args()
    raw = args.fixture.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    result = analyze(data, raw)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote synthetic behavior audit: {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
