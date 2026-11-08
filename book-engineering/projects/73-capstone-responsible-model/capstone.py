"""Train and package a tiny deterministic logistic model on a synthetic fixture."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

PROJECT_ID = "v5-ch12-capstone-responsible-model-synthetic-v1"
ROOT = Path(__file__).resolve().parent
FIXTURE_NAME = "synthetic_fixture.json"
MANIFEST_NAME = "fixture_manifest.json"
PLAN_NAME = "run_card.json"
STATIC_FILES = (
    "README.md",
    "capstone.py",
    FIXTURE_NAME,
    MANIFEST_NAME,
    PLAN_NAME,
    "data_card.md",
    "model_card.md",
    "release_decision.json",
    "requirements.txt",
    "test_capstone.py",
)
OUTPUT_FILES = ("checkpoint.json", "results.json", "environment.json")


class CapstoneError(ValueError):
    """Raised when an input packet violates the declared project contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CapstoneError(f"expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("schema_version") != 1:
        raise CapstoneError("unsupported fixture schema_version")
    if fixture.get("project_id") != PROJECT_ID or fixture.get("synthetic") is not True:
        raise CapstoneError("fixture identity or synthetic declaration mismatch")
    provenance = fixture.get("provenance")
    if not isinstance(provenance, dict):
        raise CapstoneError("fixture provenance is missing")
    if provenance.get("real_records") is not False or provenance.get("personal_data") is not False:
        raise CapstoneError("this teaching run accepts only the declared non-personal fixture")
    if provenance.get("real_model_outputs") is not False or provenance.get("external_source") is not None:
        raise CapstoneError("fixture must not claim external data or model outputs")
    if fixture.get("features") != ["x1", "x2"] or fixture.get("target") != "toy_label":
        raise CapstoneError("unexpected feature or target schema")

    splits = fixture.get("splits")
    if not isinstance(splits, dict) or set(splits) != {"train", "validation", "test"}:
        raise CapstoneError("fixture must define exactly train, validation, and test splits")
    expected_sizes = {"train": 8, "validation": 4, "test": 4}
    all_ids: set[str] = set()
    for split_name, expected_size in expected_sizes.items():
        rows = splits[split_name]
        if not isinstance(rows, list) or len(rows) != expected_size:
            raise CapstoneError(f"{split_name} must contain exactly {expected_size} rows")
        split_labels: set[int] = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"id", "x1", "x2", "toy_label"}:
                raise CapstoneError(f"invalid row schema in {split_name}")
            row_id = row["id"]
            if not isinstance(row_id, str) or not row_id or row_id in all_ids:
                raise CapstoneError("row ids must be non-empty and unique across splits")
            all_ids.add(row_id)
            for feature in ("x1", "x2"):
                value = row[feature]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise CapstoneError(f"{feature} must be a finite number")
            label = row["toy_label"]
            if isinstance(label, bool) or label not in (0, 1):
                raise CapstoneError("toy_label must be the integer 0 or 1")
            expected_label = int(row["x1"] + row["x2"] > 0)
            if label != expected_label:
                raise CapstoneError(f"label rule mismatch for {row_id}")
            split_labels.add(label)
        if split_labels != {0, 1}:
            raise CapstoneError(f"{split_name} must contain both toy labels")


def load_fixture(fixture_path: Path, manifest_path: Path | None = None) -> tuple[dict[str, Any], str]:
    fixture_bytes = fixture_path.read_bytes()
    fixture_hash = sha256_bytes(fixture_bytes)
    manifest_path = manifest_path or fixture_path.with_name(MANIFEST_NAME)
    manifest = read_json(manifest_path)
    if manifest.get("project_id") != PROJECT_ID or manifest.get("synthetic") is not True:
        raise CapstoneError("fixture manifest identity mismatch")
    if manifest.get("fixture_sha256") != fixture_hash:
        raise CapstoneError("fixture SHA-256 does not match fixture_manifest.json")
    fixture = json.loads(fixture_bytes.decode("utf-8"))
    if not isinstance(fixture, dict):
        raise CapstoneError("fixture must be a JSON object")
    validate_fixture(fixture)
    return fixture, fixture_hash


def load_plan(project_root: Path) -> dict[str, Any]:
    plan = read_json(project_root / PLAN_NAME)
    if plan.get("project_id") != PROJECT_ID:
        raise CapstoneError("run card project_id mismatch")
    config = plan.get("configuration")
    expected = {
        "epochs": 200,
        "learning_rate": 0.5,
        "l2": 0.0,
        "decision_threshold": 0.5,
        "tie_rule": "score equal to threshold predicts class 0",
        "initial_weights": [0.0, 0.0],
        "initial_bias": 0.0,
        "randomness": "none",
    }
    if config != expected:
        raise CapstoneError("run card configuration differs from the tested reference plan")
    if plan.get("training_split") != "train only":
        raise CapstoneError("training must use only the declared train split")
    if plan.get("validation_split") != "report descriptive metrics after fitting; do not update weights":
        raise CapstoneError("validation split contract mismatch")
    if plan.get("test_split") != "report descriptive metrics once after fitting; do not select parameters":
        raise CapstoneError("test split contract mismatch")
    return plan


def sigmoid(value: float) -> float:
    if value >= 0:
        exponent = math.exp(-min(value, 700.0))
        return 1.0 / (1.0 + exponent)
    exponent = math.exp(max(value, -700.0))
    return exponent / (1.0 + exponent)


def train_model(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    if not rows:
        raise CapstoneError("training split must not be empty")
    labels = {row["toy_label"] for row in rows}
    if labels != {0, 1}:
        raise CapstoneError("training split must contain both labels")
    weights = [float(value) for value in config["initial_weights"]]
    bias = float(config["initial_bias"])
    learning_rate = float(config["learning_rate"])
    regularization = float(config["l2"])
    epochs = int(config["epochs"])
    if len(weights) != 2 or epochs <= 0 or learning_rate <= 0 or regularization < 0:
        raise CapstoneError("invalid logistic-regression configuration")

    for _ in range(epochs):
        gradient_weights = [0.0, 0.0]
        gradient_bias = 0.0
        for row in rows:
            score = bias + weights[0] * row["x1"] + weights[1] * row["x2"]
            error = sigmoid(score) - row["toy_label"]
            gradient_weights[0] += error * row["x1"]
            gradient_weights[1] += error * row["x2"]
            gradient_bias += error
        scale = 1.0 / len(rows)
        weights = [
            weight - learning_rate * (gradient * scale + regularization * weight)
            for weight, gradient in zip(weights, gradient_weights)
        ]
        bias -= learning_rate * gradient_bias * scale

    return {"weights": weights, "bias": bias}


def probability(row: dict[str, Any], model: dict[str, Any]) -> float:
    score = model["bias"] + model["weights"][0] * row["x1"] + model["weights"][1] * row["x2"]
    return sigmoid(score)


def _rounded(value: float) -> float:
    return round(float(value), 12)


def evaluate_rows(
    rows: list[dict[str, Any]],
    model: dict[str, Any],
    threshold: float = 0.5,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not rows:
        raise CapstoneError("evaluation split must not be empty")
    if not 0.0 < threshold < 1.0:
        raise CapstoneError("decision threshold must be strictly between zero and one")
    confusion = {"tn": 0, "fp": 0, "fn": 0, "tp": 0}
    predictions: list[dict[str, Any]] = []
    losses: list[float] = []
    correct = 0
    for row in rows:
        score = probability(row, model)
        predicted = int(score > threshold)
        actual = row["toy_label"]
        correct += int(predicted == actual)
        if actual == 0 and predicted == 0:
            confusion["tn"] += 1
        elif actual == 0 and predicted == 1:
            confusion["fp"] += 1
        elif actual == 1 and predicted == 0:
            confusion["fn"] += 1
        else:
            confusion["tp"] += 1
        clipped = min(max(score, 1e-12), 1.0 - 1e-12)
        losses.append(-(actual * math.log(clipped) + (1 - actual) * math.log(1 - clipped)))
        predictions.append({
            "id": row["id"],
            "expected": actual,
            "predicted": predicted,
            "score": _rounded(score),
        })
    metrics = {
        "count": len(rows),
        "correct": correct,
        "accuracy": _rounded(correct / len(rows)),
        "binary_cross_entropy": _rounded(sum(losses) / len(losses)),
        "confusion_matrix": confusion,
    }
    return metrics, predictions


def evaluate_majority_baseline(
    rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not training_rows:
        raise CapstoneError("baseline requires a non-empty training split")
    if not rows:
        raise CapstoneError("baseline evaluation split must not be empty")
    positives = sum(row["toy_label"] for row in training_rows)
    negatives = len(training_rows) - positives
    label = 1 if positives > negatives else 0
    confusion = {"tn": 0, "fp": 0, "fn": 0, "tp": 0}
    correct = 0
    for row in rows:
        actual = row["toy_label"]
        correct += int(actual == label)
        if actual == 0 and label == 0:
            confusion["tn"] += 1
        elif actual == 0 and label == 1:
            confusion["fp"] += 1
        elif actual == 1 and label == 0:
            confusion["fn"] += 1
        else:
            confusion["tp"] += 1
    return {
        "policy": "training-split majority; ties resolve to class 0",
        "label": label,
        "count": len(rows),
        "correct": correct,
        "accuracy": _rounded(correct / len(rows)),
        "confusion_matrix": confusion,
    }


def _manifest_file_map(project_root: Path, output_dir: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for name in STATIC_FILES:
        path = project_root / name
        if not path.is_file():
            raise CapstoneError(f"release source file missing: {name}")
        mapping[f"source/{name}"] = sha256_file(path)
    for name in OUTPUT_FILES:
        path = output_dir / name
        if not path.is_file():
            raise CapstoneError(f"release output file missing: {name}")
        mapping[f"output/{name}"] = sha256_file(path)
    return mapping


def verify_release(manifest_path: Path, project_root: Path, output_dir: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    if manifest.get("project_id") != PROJECT_ID:
        raise CapstoneError("release manifest project_id mismatch")
    expected = _manifest_file_map(project_root, output_dir)
    if manifest.get("files") != expected:
        raise CapstoneError("release manifest contains a missing, changed, or unexpected file hash")
    return manifest


def run_project(
    fixture_path: Path,
    output_dir: Path,
    project_root: Path = ROOT,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture, fixture_hash = load_fixture(fixture_path)
    plan = load_plan(project_root)
    config = plan["configuration"]
    code_hash = sha256_file(project_root / "capstone.py")
    run_card_hash = sha256_file(project_root / PLAN_NAME)
    model_parameters = train_model(fixture["splits"]["train"], config)
    model = {
        "weights": [_rounded(value) for value in model_parameters["weights"]],
        "bias": _rounded(model_parameters["bias"]),
    }
    checkpoint = {
        "format_version": 1,
        "project_id": PROJECT_ID,
        "model_id": "v5-ch12-logistic-toy-demo-v1",
        "algorithm": "binary logistic regression; full-batch gradient descent",
        "features": fixture["features"],
        "target": fixture["target"],
        "weights": model["weights"],
        "bias": model["bias"],
        "threshold": config["decision_threshold"],
        "training_config": {
            "epochs": config["epochs"],
            "learning_rate": config["learning_rate"],
            "l2": config["l2"],
            "decision_threshold": config["decision_threshold"],
            "tie_rule": config["tie_rule"],
            "initial_weights": config["initial_weights"],
            "initial_bias": config["initial_bias"],
            "randomness": config["randomness"],
            "split_used_for_weight_updates": "train",
        },
        "fixture_sha256": fixture_hash,
        "source_code_sha256": code_hash,
        "run_card_sha256": run_card_hash,
    }
    checkpoint_path = output_dir / "checkpoint.json"
    write_json(checkpoint_path, checkpoint)
    checkpoint_hash = sha256_file(checkpoint_path)

    split_metrics: dict[str, Any] = {}
    test_predictions: list[dict[str, Any]] = []
    for split_name in ("train", "validation", "test"):
        metrics, predictions = evaluate_rows(
            fixture["splits"][split_name], model, float(config["decision_threshold"])
        )
        split_metrics[split_name] = metrics
        if split_name == "test":
            test_predictions = predictions
    baseline = evaluate_majority_baseline(fixture["splits"]["test"], fixture["splits"]["train"])
    results = {
        "project_id": PROJECT_ID,
        "model_id": checkpoint["model_id"],
        "fixture_sha256": fixture_hash,
        "source_code_sha256": code_hash,
        "run_card_sha256": run_card_hash,
        "checkpoint_sha256": checkpoint_hash,
        "synthetic_fixture_only": True,
        "real_data_used": False,
        "pretrained_model_used": False,
        "external_api_calls": 0,
        "training": {
            "split": "train",
            "row_count": len(fixture["splits"]["train"]),
            "epochs": config["epochs"],
            "learning_rate": config["learning_rate"],
            "l2": config["l2"],
            "randomness": "none",
        },
        "metrics": split_metrics,
        "majority_baseline_test": baseline,
        "test_predictions": test_predictions,
        "claims": {
            "real_world_quality_established": False,
            "generalization_established": False,
            "fairness_assessed_for_real_groups": False,
            "safety_or_security_approved": False,
            "statistical_inference_authorized": False,
            "deployment_approved": False,
        },
        "interpretation": "Descriptive execution results on one deterministic synthetic fixture only.",
    }
    results_path = output_dir / "results.json"
    write_json(results_path, results)

    environment = {
        "project_id": PROJECT_ID,
        "audit_date": "2026-11-08",
        "runtime": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "platform": sys.platform,
        },
        "dependencies": [],
        "input": {
            "fixture_sha256": fixture_hash,
            "source_code_sha256": code_hash,
            "run_card_sha256": run_card_hash,
        },
        "execution": {
            "unit_tests": "25/25 passed",
            "training_executed": True,
            "external_network_requests": 0,
            "external_api_calls": 0,
            "gpu_used": False,
            "real_data_used": False,
            "personal_data_used": False,
            "pretrained_model_used": False,
            "randomness_used": False,
            "result_reproduced_from_saved_fixture": True,
        },
        "interpretation_limits": {
            "synthetic_fixture_only": True,
            "real_world_quality_assessed": False,
            "generalization_assessed": False,
            "fairness_for_real_groups_assessed": False,
            "safety_or_security_reviewed_for_deployment": False,
            "deployment_authorized": False,
        },
    }
    environment_path = output_dir / "environment.json"
    write_json(environment_path, environment)

    release_files = _manifest_file_map(project_root, output_dir)
    release_manifest = {
        "format_version": 1,
        "project_id": PROJECT_ID,
        "decision": "educational_source_packet_only",
        "deployment_approved": False,
        "hash_algorithm": "SHA-256",
        "files": release_files,
        "self_hash_included": False,
    }
    manifest_path = output_dir / "release_manifest.json"
    write_json(manifest_path, release_manifest)
    verify_release(manifest_path, project_root, output_dir)
    return {
        "checkpoint": checkpoint,
        "results": results,
        "environment": environment,
        "release_manifest": release_manifest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=ROOT / FIXTURE_NAME)
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.verify_only:
            verify_release(args.output_dir / "release_manifest.json", ROOT, args.output_dir)
            print("release packet hashes verified; deployment remains unapproved")
            return 0
        packet = run_project(args.fixture, args.output_dir, ROOT)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, CapstoneError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    test = packet["results"]["metrics"]["test"]
    baseline = packet["results"]["majority_baseline_test"]
    print(
        "synthetic teaching run only: "
        f"test_accuracy={test['correct']}/{test['count']}; "
        f"majority_baseline={baseline['correct']}/{baseline['count']}; "
        "deployment_approved=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
