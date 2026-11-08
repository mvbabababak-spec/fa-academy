#!/usr/bin/env python3
"""Summarize a synthetic paired experiment at its independent group level."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

PROJECT_ID = "v5-ch10-experiment-design-synthetic-v1"
DEFAULT_DIR = Path(__file__).resolve().parent


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _finite_score(value: Any, label: str) -> float:
    _require(not isinstance(value, bool) and isinstance(value, (int, float)), f"{label} must be numeric")
    score = float(value)
    _require(math.isfinite(score) and 0.0 <= score <= 1.0, f"{label} must be finite and in [0, 1]")
    return score


def validate_plan(plan: dict[str, Any]) -> None:
    _require(isinstance(plan, dict), "analysis plan must be a JSON object")
    _require(plan.get("project_id") == PROJECT_ID, "analysis plan project_id mismatch")
    _require(plan.get("status") == "illustrative_only_not_a_preregistration", "plan must not claim real preregistration")
    design = plan.get("design")
    analysis = plan.get("analysis")
    _require(isinstance(design, dict) and isinstance(analysis, dict), "design and analysis objects are required")
    _require(plan.get("synthetic_only") is True, "plan must be explicitly synthetic-only")
    _require(plan.get("analysis_unit") == "task_group", "analysis unit must be the independent task_group")
    _require(plan.get("resampling_unit") == "task_group", "resampling unit must be the independent task_group")
    group_count = design.get("group_count")
    tasks_per_group = design.get("tasks_per_group")
    repetitions_per_task = design.get("repetitions_per_task")
    _require(isinstance(group_count, int) and not isinstance(group_count, bool) and group_count >= 4,
             "at least four independent groups are required in this teaching fixture")
    _require(isinstance(tasks_per_group, int) and not isinstance(tasks_per_group, bool) and tasks_per_group >= 1
             and isinstance(repetitions_per_task, int) and not isinstance(repetitions_per_task, bool)
             and repetitions_per_task >= 1, "task and repetition counts must be positive integers")
    _require(analysis.get("primary_metric") == "mean_candidate_minus_baseline",
             "the primary metric must be the prespecified paired difference")
    _require(analysis.get("interval_method") == "stratified_percentile_bootstrap_resampling_task_groups_within_topic",
             "the bootstrap must resample task groups within the prespecified topic blocks, not rows")
    _require(analysis.get("report_p_value") is False, "this fixture must not report a p-value")
    _require(isinstance(analysis.get("bootstrap_replicates"), int)
             and analysis["bootstrap_replicates"] >= 100,
             "bootstrap_replicates must be an integer of at least 100")
    _require(isinstance(analysis.get("bootstrap_seed"), int) and analysis["bootstrap_seed"] >= 0,
             "bootstrap_seed must be a non-negative integer")
    confidence = analysis.get("confidence_level")
    _require(isinstance(confidence, (int, float)) and 0.5 < confidence < 1.0,
             "confidence_level must be between 0.5 and 1")


def validate_fixture(payload: dict[str, Any], plan: dict[str, Any]) -> list[dict[str, Any]]:
    _require(isinstance(payload, dict), "fixture must be a JSON object")
    _require(payload.get("synthetic") is True, "fixture must be explicitly synthetic")
    _require(payload.get("fixture_id") == PROJECT_ID, "fixture_id mismatch")
    _require(payload.get("external_data_used") is False, "fixture must not claim external data")
    observations = payload.get("observations")
    _require(isinstance(observations, list) and observations, "observations must be a non-empty list")
    design = plan["design"]
    seen: set[tuple[str, str, int]] = set()
    group_topics: dict[str, str] = {}
    tasks_by_group: dict[str, set[str]] = {}
    task_owners: dict[str, str] = {}
    repeats_by_task: dict[tuple[str, str], set[int]] = {}
    clean: list[dict[str, Any]] = []

    for index, row in enumerate(observations):
        label = f"observation {index + 1}"
        _require(isinstance(row, dict), f"{label} must be an object")
        group_id, topic, task_id, repetition = (
            row.get("group_id"), row.get("topic"), row.get("task_id"), row.get("repetition")
        )
        _require(all(isinstance(value, str) and value.strip() for value in (group_id, topic, task_id)),
                 f"{label} needs non-empty group_id, topic, and task_id")
        _require(isinstance(repetition, int) and not isinstance(repetition, bool) and repetition >= 1,
                 f"{label} repetition must be a positive integer")
        key = (group_id, task_id, repetition)
        _require(key not in seen, f"duplicate paired observation: {key}")
        seen.add(key)
        previous_topic = group_topics.setdefault(group_id, topic)
        _require(previous_topic == topic, f"task group {group_id} has multiple topics")
        previous_group = task_owners.setdefault(task_id, group_id)
        _require(previous_group == group_id, f"task_id {task_id} appears in multiple groups")
        tasks_by_group.setdefault(group_id, set()).add(task_id)
        repeats_by_task.setdefault((group_id, task_id), set()).add(repetition)
        baseline = _finite_score(row.get("baseline_score"), f"{label} baseline_score")
        candidate = _finite_score(row.get("candidate_score"), f"{label} candidate_score")
        clean.append({
            "group_id": group_id,
            "topic": topic,
            "task_id": task_id,
            "repetition": repetition,
            "baseline_score": baseline,
            "candidate_score": candidate,
        })

    expected_groups = design["group_count"]
    expected_tasks = design["tasks_per_group"]
    expected_repetitions = design["repetitions_per_task"]
    _require(len(group_topics) == expected_groups, "fixture group count does not match the locked design")
    _require(set(tasks_by_group) == set(group_topics), "group metadata is incomplete")
    topic_group_counts: dict[str, int] = {}
    for topic in group_topics.values():
        topic_group_counts[topic] = topic_group_counts.get(topic, 0) + 1
    minimum_groups_per_topic = plan["design"].get("minimum_groups_per_topic", 1)
    _require(isinstance(minimum_groups_per_topic, int) and minimum_groups_per_topic >= 1,
             "minimum_groups_per_topic must be a positive integer")
    _require(all(count >= minimum_groups_per_topic for count in topic_group_counts.values()),
             "each topic block has too few independent groups for the locked design")
    expected_task_count = expected_groups * expected_tasks
    for group_id, task_ids in tasks_by_group.items():
        _require(len(task_ids) == expected_tasks, f"task count is unbalanced in group {group_id}")
    _require(len(repeats_by_task) == expected_task_count, "fixture task count does not match the locked design")
    expected_repetitions_set = set(range(1, expected_repetitions + 1))
    for key, repetitions in repeats_by_task.items():
        _require(repetitions == expected_repetitions_set, f"repetitions are incomplete for task {key}")
    _require(len(clean) == expected_groups * expected_tasks * expected_repetitions,
             "observation count does not match the locked design")
    return clean


def _percentile(sorted_values: list[float], probability: float) -> float:
    """Linear interpolation between adjacent order statistics (type 7)."""
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    fraction = position - lower
    return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction


def analyze(payload: dict[str, Any], plan: dict[str, Any], fixture_sha256: str,
            plan_sha256: str) -> dict[str, Any]:
    validate_plan(plan)
    observations = validate_fixture(payload, plan)
    group_rows: dict[str, list[dict[str, Any]]] = {}
    for row in observations:
        group_rows.setdefault(row["group_id"], []).append(row)

    group_results = []
    differences = []
    topic_differences: dict[str, list[float]] = {}
    for group_id in sorted(group_rows):
        rows = group_rows[group_id]
        baseline = statistics.fmean(row["baseline_score"] for row in rows)
        candidate = statistics.fmean(row["candidate_score"] for row in rows)
        difference = candidate - baseline
        differences.append(difference)
        topic_differences.setdefault(rows[0]["topic"], []).append(difference)
        group_results.append({
            "group_id": group_id,
            "topic": rows[0]["topic"],
            "baseline_mean": round(baseline, 6),
            "candidate_mean": round(candidate, 6),
            "paired_difference": round(difference, 6),
        })

    mean_difference = statistics.fmean(differences)
    confidence = float(plan["analysis"]["confidence_level"])
    tail = (1.0 - confidence) / 2.0
    replicates = int(plan["analysis"]["bootstrap_replicates"])
    rng = random.Random(int(plan["analysis"]["bootstrap_seed"]))
    bootstrap_means = []
    for _ in range(replicates):
        sample = []
        for topic in sorted(topic_differences):
            values = topic_differences[topic]
            sample.extend(rng.choice(values) for _ in values)
        bootstrap_means.append(statistics.fmean(sample))
    bootstrap_means.sort()

    return {
        "project_id": PROJECT_ID,
        "fixture_id": payload["fixture_id"],
        "synthetic": True,
        "analysis_plan_sha256": plan_sha256,
        "fixture_sha256": fixture_sha256,
        "design": {
            "independent_groups": len(group_results),
            "tasks_per_group": int(plan["design"]["tasks_per_group"]),
            "repetitions_per_task": int(plan["design"]["repetitions_per_task"]),
            "paired_observation_rows": len(observations),
            "resampling_unit": "task_group",
        },
        "primary_result": {
            "estimand": plan["estimand"],
            "metric": "mean_candidate_minus_baseline",
            "mean_paired_difference": round(mean_difference, 7),
            "median_group_difference": round(statistics.median(differences), 6),
            "bootstrap_percentile_interval": {
                "confidence_level": confidence,
                "lower": round(_percentile(bootstrap_means, tail), 6),
                "upper": round(_percentile(bootstrap_means, 1.0 - tail), 6),
                "replicates": replicates,
                "seed": int(plan["analysis"]["bootstrap_seed"]),
                "unit_resampled": "task_group_within_topic",
                "stratification_factor": "topic",
                "strata_count": len(topic_differences),
            },
            "p_value": None,
        },
        "group_results": group_results,
        "interpretation": (
            "محاسبهٔ قطعی روی fixture آموزشی ساختگی است؛ نه نتیجهٔ مدل واقعی، نه آزمون فرضیهٔ جمعیتی، "
            "و نه مجوز تعمیم یا استقرار."
        ),
        "external_network_requests": 0,
        "model_inference_calls": 0,
        "gpu_used": False,
        "personal_records": 0,
        "inference_authorized": False,
    }


def run(plan_path: Path, fixture_path: Path, manifest_path: Path, output_path: Path) -> dict[str, Any]:
    plan_bytes = plan_path.read_bytes()
    fixture_bytes = fixture_path.read_bytes()
    plan = json.loads(plan_bytes.decode("utf-8"))
    payload = json.loads(fixture_bytes.decode("utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    plan_hash = hashlib.sha256(plan_bytes).hexdigest()
    fixture_hash = hashlib.sha256(fixture_bytes).hexdigest()
    _require(manifest.get("project_id") == PROJECT_ID, "fixture manifest project_id mismatch")
    _require(manifest.get("analysis_plan_sha256") == plan_hash, "analysis plan bytes do not match manifest")
    _require(manifest.get("fixture_sha256") == fixture_hash, "fixture bytes do not match manifest")
    _require(manifest.get("observation_count") == len(payload.get("observations", [])),
             "fixture observation count does not match manifest")
    _require(manifest.get("group_count") == plan["design"]["group_count"],
             "fixture group count does not match manifest")
    result = analyze(payload, plan, fixture_hash, plan_hash)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_DIR / "analysis_plan.json")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_DIR / "synthetic_paired_scores.json")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_DIR / "fixture_manifest.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_DIR / "results.json")
    args = parser.parse_args()
    try:
        result = run(args.plan, args.fixture, args.manifest, args.output)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        parser.error(str(exc))
    interval = result["primary_result"]["bootstrap_percentile_interval"]
    print(
        f"synthetic fixture only: groups={result['design']['independent_groups']}; "
        f"mean paired difference={result['primary_result']['mean_paired_difference']}; "
        f"interval=[{interval['lower']}, {interval['upper']}]; inference_authorized=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
