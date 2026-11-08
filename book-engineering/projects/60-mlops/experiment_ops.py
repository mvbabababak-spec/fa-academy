#!/usr/bin/env python3
"""Small, offline-first experiment-tracking example for Volume 4, Chapter 14.

The fixture and model are synthetic and intentionally tiny. No network tracking,
model-quality claim, GPU training, or production deployment is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_FIXTURE = PROJECT_DIR / "sample_experiment.json"
DEFAULT_FIXTURE_MANIFEST = PROJECT_DIR / "fixture_manifest.json"
LOCKFILE = PROJECT_DIR / "requirements-lock-linux-py313.txt"
EXPERIMENT_NAME = "fa-academy-v4-ch14-synthetic-ops"


class ContractError(ValueError):
    """Raised when the fixture or run configuration violates the project contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    """Stable UTF-8 encoding used only for deterministic run fingerprints."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def validate_fixture(data: dict[str, Any]) -> None:
    if data.get("schema_version") != 1:
        raise ContractError("fixture schema_version must be 1")
    if data.get("label_source") != "synthetic_fixture":
        raise ContractError("only the explicitly synthetic fixture is accepted")
    if not isinstance(data.get("fixture_id"), str) or not data["fixture_id"]:
        raise ContractError("fixture_id must be a non-empty string")

    records = data.get("records")
    if not isinstance(records, list) or len(records) < 2:
        raise ContractError("records must contain at least two synthetic rows")
    sample_ids: set[str] = set()
    for row in records:
        if not isinstance(row, dict):
            raise ContractError("every record must be an object")
        sample_id = row.get("sample_id")
        if not isinstance(sample_id, str) or not sample_id or sample_id in sample_ids:
            raise ContractError("sample_id values must be non-empty and unique")
        sample_ids.add(sample_id)
        for key in ("x", "y"):
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ContractError(f"record field {key!r} must be a finite number")

    scope = data.get("scope")
    if not isinstance(scope, dict):
        raise ContractError("fixture scope must be an object")
    required_false = (
        "real_data_used",
        "pretrained_model_used",
        "gpu_used",
        "benchmark_claim",
        "model_quality_claim",
        "production_claim",
    )
    if scope.get("synthetic_only") is not True:
        raise ContractError("scope.synthetic_only must be true")
    if any(scope.get(key) is not False for key in required_false):
        raise ContractError("the project fixture must make no real-data or production claims")


def load_fixture(
    fixture_path: Path = DEFAULT_FIXTURE,
    manifest_path: Path = DEFAULT_FIXTURE_MANIFEST,
) -> tuple[dict[str, Any], str]:
    raw = fixture_path.read_bytes()
    digest = sha256_bytes(raw)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"fixture manifest is missing: {manifest_path}") from exc
    if manifest.get("fixture_id") is None:
        raise ContractError("fixture manifest must identify the fixture")
    if manifest.get("fixture_file") != fixture_path.name:
        raise ContractError("fixture manifest filename does not match the selected fixture")
    if manifest.get("sha256") != digest:
        raise ContractError("fixture SHA-256 does not match fixture_manifest.json")
    if manifest.get("record_count") is not None:
        data = json.loads(raw)
        if manifest["record_count"] != len(data.get("records", [])):
            raise ContractError("fixture record count does not match fixture_manifest.json")
    else:
        data = json.loads(raw)
    validate_fixture(data)
    if manifest["fixture_id"] != data["fixture_id"]:
        raise ContractError("fixture ID does not match fixture_manifest.json")
    return data, digest


def fit_toy_linear(
    records: list[dict[str, Any]],
    *,
    steps: int,
    learning_rate: float,
) -> dict[str, Any]:
    """Full-batch gradient descent on a four-row synthetic linear fixture."""
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 100:
        raise ContractError("steps must be an integer from 1 through 100")
    if isinstance(learning_rate, bool) or not isinstance(learning_rate, (int, float)):
        raise ContractError("learning_rate must be numeric")
    learning_rate = float(learning_rate)
    if not math.isfinite(learning_rate) or not 0.0 < learning_rate <= 0.1:
        raise ContractError("learning_rate must be finite and in (0, 0.1]")

    xs = [float(row["x"]) for row in records]
    ys = [float(row["y"]) for row in records]
    count = len(records)
    weight = 0.0
    bias = 0.0

    def mse() -> float:
        return sum((weight * x + bias - y) ** 2 for x, y in zip(xs, ys)) / count

    history: list[dict[str, float | int]] = [{"step": 0, "mse": mse()}]
    for step in range(1, steps + 1):
        residuals = [weight * x + bias - y for x, y in zip(xs, ys)]
        grad_weight = (2.0 / count) * sum(error * x for error, x in zip(residuals, xs))
        grad_bias = (2.0 / count) * sum(residuals)
        weight -= learning_rate * grad_weight
        bias -= learning_rate * grad_bias
        loss = mse()
        if not math.isfinite(loss):
            raise ContractError("toy optimizer produced a non-finite metric")
        history.append({"step": step, "mse": loss})

    return {
        "weight": weight,
        "bias": bias,
        "initial_mse": history[0]["mse"],
        "final_mse": history[-1]["mse"],
        "history": history,
    }


def capture_git_provenance(start: Path = PROJECT_DIR) -> dict[str, Any]:
    """Capture commit and cleanliness digests without exporting diffs or file contents."""
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=top,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=top,
            check=True,
            capture_output=True,
        ).stdout
        diff = subprocess.run(
            ["git", "diff", "--binary", "HEAD"],
            cwd=top,
            check=True,
            capture_output=True,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        declared_commit = os.environ.get("SOURCE_COMMIT")
        if declared_commit in (None, "", "unknown") or not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", declared_commit):
            declared_commit = None
        clean_text = os.environ.get("SOURCE_WORKTREE_CLEAN", "unknown").lower()
        declared_clean = True if clean_text == "true" else False if clean_text == "false" else None
        status_hash = os.environ.get("SOURCE_STATUS_SHA256")
        diff_hash = os.environ.get("SOURCE_TRACKED_DIFF_SHA256")
        if status_hash is not None and not re.fullmatch(r"[0-9a-f]{64}", status_hash):
            status_hash = None
        if diff_hash is not None and not re.fullmatch(r"[0-9a-f]{64}", diff_hash):
            diff_hash = None
        untracked_text = os.environ.get("SOURCE_UNTRACKED_PATH_COUNT")
        try:
            untracked_count = int(untracked_text) if untracked_text is not None else None
            if untracked_count is not None and untracked_count < 0:
                untracked_count = None
        except ValueError:
            untracked_count = None
        declared = any((declared_commit, declared_clean is not None, status_hash, diff_hash, untracked_count is not None))
        return {
            "available": False,
            "capture_method": "environment" if declared else "unavailable",
            "commit": declared_commit,
            "worktree_clean": declared_clean,
            "status_sha256": status_hash,
            "tracked_diff_sha256": diff_hash,
            "untracked_path_count": untracked_count,
        }

    return {
        "available": True,
        "capture_method": "git",
        "commit": commit,
        "worktree_clean": len(status) == 0,
        "status_sha256": sha256_bytes(status),
        "tracked_diff_sha256": sha256_bytes(diff),
        "untracked_path_count": sum(line.startswith(b"??") for line in status.splitlines()),
    }


def package_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def environment_snapshot() -> dict[str, Any]:
    lock_hash = sha256_file(LOCKFILE) if LOCKFILE.exists() else None
    digest = os.environ.get("CONTAINER_IMAGE_DIGEST")
    if digest is not None and not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        digest = None
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.system(),
        "machine": platform.machine(),
        "mlflow": package_version("mlflow"),
        "wandb": package_version("wandb"),
        "pyyaml": package_version("PyYAML"),
        "dependency_lock_sha256": lock_hash,
        "container_image_digest": digest,
        "accelerator": "none; pure-Python CPU arithmetic",
    }


def run_fingerprint(
    *,
    fixture_sha256: str,
    config: dict[str, Any],
    environment: dict[str, Any],
    source: dict[str, Any],
) -> str:
    stable_git = {
        key: source.get(key)
        for key in (
            "available",
            "capture_method",
            "commit",
            "worktree_clean",
            "status_sha256",
            "tracked_diff_sha256",
            "untracked_path_count",
        )
    }
    identity = {
        "schema_version": 1,
        "fixture_sha256": fixture_sha256,
        "config": config,
        "environment": environment,
        "source": stable_git,
    }
    return sha256_bytes(canonical_json_bytes(identity))


def create_run(
    *,
    fixture_path: Path,
    fixture_manifest_path: Path,
    output_dir: Path,
    steps: int | None = None,
    learning_rate: float | None = None,
    capture_git: bool = True,
) -> tuple[dict[str, Any], Path, Path]:
    fixture, fixture_hash = load_fixture(fixture_path, fixture_manifest_path)
    config = dict(fixture["config"])
    if steps is not None:
        config["steps"] = steps
    if learning_rate is not None:
        config["learning_rate"] = learning_rate
    result = fit_toy_linear(
        fixture["records"],
        steps=config["steps"],
        learning_rate=config["learning_rate"],
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.json"
    run_path = output_dir / "run.json"
    model_record = {
        "schema_version": 1,
        "artifact_type": "synthetic-toy-linear-output",
        "fixture_id": fixture["fixture_id"],
        "fixture_sha256": fixture_hash,
        "weights": {"weight": result["weight"], "bias": result["bias"]},
        "training_points": len(fixture["records"]),
        "history": result["history"],
        "scope": {
            "synthetic_only": True,
            "model_quality_claim": False,
            "benchmark_claim": False,
            "production_claim": False,
        },
    }
    write_json(model_path, model_record)

    source = capture_git_provenance(PROJECT_DIR) if capture_git else {
        "available": False,
        "commit": None,
        "worktree_clean": None,
        "status_sha256": None,
        "tracked_diff_sha256": None,
        "untracked_path_count": None,
        "capture_requested": False,
    }
    environment = environment_snapshot()
    fingerprint = run_fingerprint(
        fixture_sha256=fixture_hash,
        config=config,
        environment=environment,
        source=source,
    )
    record: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": fixture["fixture_id"],
        "run_fingerprint_sha256": fingerprint,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixture": {
            "fixture_id": fixture["fixture_id"],
            "fixture_file": fixture_path.name,
            "sha256": fixture_hash,
            "record_count": len(fixture["records"]),
            "label_source": fixture["label_source"],
        },
        "config": config,
        "source": source,
        "environment": environment,
        "metrics": {
            "initial_mse": result["initial_mse"],
            "final_mse": result["final_mse"],
            "history": result["history"],
            "training_points": len(fixture["records"]),
        },
        "artifact": {
            "file": model_path.name,
            "sha256": sha256_file(model_path),
            "bytes": model_path.stat().st_size,
        },
        "scope": fixture["scope"],
        "tracking": {
            "backend": "manifest",
            "status": "manifest-only",
            "external_sync_requested": False,
            "api_key_required": False,
        },
    }
    write_json(run_path, record)
    return record, model_path, run_path


@contextmanager
def temporary_environment(values: dict[str, str | None]) -> Iterator[None]:
    old = {key: os.environ.get(key) for key in values}
    try:
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def track_with_mlflow(
    record: dict[str, Any], model_path: Path, run_path: Path, output_dir: Path
) -> dict[str, Any]:
    import mlflow

    tracking_dir = output_dir / "mlflow"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    database = tracking_dir / "tracking.db"
    tracking_uri = f"sqlite:///{database.resolve()}"
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name=f"ch60-{record['run_fingerprint_sha256'][:12]}") as run:
        mlflow.log_params(
            {
                "fixture_id": record["fixture"]["fixture_id"],
                "fixture_sha256": record["fixture"]["sha256"],
                "learning_rate": record["config"]["learning_rate"],
                "steps": record["config"]["steps"],
                "run_fingerprint_sha256": record["run_fingerprint_sha256"],
            }
        )
        mlflow.set_tags(
            {
                "git_commit": record["source"].get("commit") or "unavailable",
                "git_worktree_clean": str(record["source"].get("worktree_clean")),
                "synthetic_only": "true",
                "external_sync_requested": "false",
            }
        )
        for point in record["metrics"]["history"]:
            mlflow.log_metric("toy/mse", point["mse"], step=point["step"])
        run_id = run.info.run_id
        record["tracking"] = {
            "backend": "mlflow",
            "status": "logged-local-sqlite",
            "experiment_name": EXPERIMENT_NAME,
            "run_id": run_id,
            "storage": "local SQLite plus local artifact directory",
            "external_sync_requested": False,
            "api_key_required": False,
        }
        write_json(run_path, record)
        mlflow.log_artifact(str(model_path), artifact_path="outputs")
        mlflow.log_artifact(str(run_path), artifact_path="provenance")

    return record["tracking"]


def track_with_wandb_offline(
    record: dict[str, Any], model_path: Path, run_path: Path, output_dir: Path
) -> dict[str, Any]:
    # Force local-only mode and remove any inherited API key for this call.
    # No `wandb sync` or login operation is performed by this project.
    env = {
        "WANDB_MODE": "offline",
        "WANDB_CONSOLE": "off",
        "WANDB_DISABLE_GIT": "true",
        "WANDB_SILENT": "true",
        "WANDB_API_KEY": None,
    }
    with temporary_environment(env):
        import wandb

        output_dir.mkdir(parents=True, exist_ok=True)
        settings = wandb.Settings(
            mode="offline",
            save_code=False,
            disable_git=True,
            console="off",
            x_disable_stats=True,
            x_disable_meta=True,
            x_disable_machine_info=True,
        )
        with wandb.init(
            project="fa-academy-v4-ch14-synthetic-ops",
            name=f"ch60-{record['run_fingerprint_sha256'][:12]}",
            mode="offline",
            dir=str(output_dir),
            config={
                "fixture_id": record["fixture"]["fixture_id"],
                "fixture_sha256": record["fixture"]["sha256"],
                "learning_rate": record["config"]["learning_rate"],
                "steps": record["config"]["steps"],
                "run_fingerprint_sha256": record["run_fingerprint_sha256"],
                "synthetic_only": True,
            },
            settings=settings,
        ) as run:
            run.define_metric("step")
            run.define_metric("toy/mse", step_metric="step")
            for point in record["metrics"]["history"]:
                run.log({"step": point["step"], "toy/mse": point["mse"]})
            run.summary["fixture_sha256"] = record["fixture"]["sha256"]
            run.summary["synthetic_only"] = True
            run_id = run.id
            offline_run_dir = Path(run.dir).resolve().parent
            relative_run_dir = offline_run_dir.relative_to(output_dir.resolve()).as_posix()
            record["tracking"] = {
                "backend": "wandb",
                "mode": "offline",
                "status": "saved-locally-not-synced",
                "project": "fa-academy-v4-ch14-synthetic-ops",
                "run_id": run_id,
                "offline_run_directory": relative_run_dir,
                "external_sync_requested": False,
                "api_key_required": False,
                "automatic_code_capture": False,
                "automatic_git_capture": False,
                "system_metrics_capture": False,
            }
            write_json(run_path, record)
            artifact = wandb.Artifact(
                name=f"ch60-output-{record['run_fingerprint_sha256'][:12]}",
                type="synthetic-run-output",
                metadata={
                    "fixture_id": record["fixture"]["fixture_id"],
                    "fixture_sha256": record["fixture"]["sha256"],
                    "run_fingerprint_sha256": record["run_fingerprint_sha256"],
                    "synthetic_only": True,
                },
            )
            artifact.add_file(str(model_path), name="model.json")
            artifact.add_file(str(run_path), name="run.json")
            run.log_artifact(artifact)

    return record["tracking"]


def run_experiment(
    *,
    backend: str,
    output_dir: Path,
    fixture_path: Path = DEFAULT_FIXTURE,
    fixture_manifest_path: Path = DEFAULT_FIXTURE_MANIFEST,
    steps: int | None = None,
    learning_rate: float | None = None,
    capture_git: bool = True,
) -> dict[str, Any]:
    if backend not in {"manifest", "mlflow", "wandb-offline"}:
        raise ContractError(f"unsupported backend: {backend}")
    record, model_path, run_path = create_run(
        fixture_path=fixture_path,
        fixture_manifest_path=fixture_manifest_path,
        output_dir=output_dir,
        steps=steps,
        learning_rate=learning_rate,
        capture_git=capture_git,
    )
    if backend == "mlflow":
        track_with_mlflow(record, model_path, run_path, output_dir)
    elif backend == "wandb-offline":
        track_with_wandb_offline(record, model_path, run_path, output_dir)
    write_json(run_path, record)
    return record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        choices=("manifest", "mlflow", "wandb-offline"),
        default="manifest",
        help="manifest-only, local SQLite MLflow, or explicitly offline W&B",
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--fixture-manifest", type=Path, default=DEFAULT_FIXTURE_MANIFEST)
    parser.add_argument("--output", type=Path, default=Path("/tmp/fa-academy-ch60-run"))
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--learning-rate", type=float, default=None)
    parser.add_argument(
        "--no-git-provenance",
        action="store_true",
        help="omit local Git state from this demo run; not recommended for real experiments",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        record = run_experiment(
            backend=args.backend,
            output_dir=args.output,
            fixture_path=args.fixture,
            fixture_manifest_path=args.fixture_manifest,
            steps=args.steps,
            learning_rate=args.learning_rate,
            capture_git=not args.no_git_provenance,
        )
    except (ContractError, OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    summary = {
        "run_fingerprint_sha256": record["run_fingerprint_sha256"],
        "fixture_sha256": record["fixture"]["sha256"],
        "initial_mse": record["metrics"]["initial_mse"],
        "final_mse": record["metrics"]["final_mse"],
        "git_worktree_clean": record["source"].get("worktree_clean"),
        "tracking": record["tracking"],
        "output": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
