"""Compare automatic gradients on one tiny, explicitly synthetic CPU fixture.

Only the selected optional framework is imported. No model, dataset, GPU, network,
training loop, or performance benchmark is used by this teaching smoke test.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = ROOT / "sample_problem.json"
BACKENDS = ("torch", "jax", "tensorflow")
METADATA_KEYS = (
    "real_dataset_loaded",
    "pretrained_model_loaded",
    "training_performed",
    "gpu_used",
    "benchmark_performed",
)


class ComparisonInputError(ValueError):
    """Raised when the synthetic comparison fixture is invalid."""


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ComparisonInputError(f"{field} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ComparisonInputError(f"{field} must be a finite number")
    return result


def validate_fixture(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ComparisonInputError("fixture must be a JSON object")
    if raw.get("schema_version") != 1:
        raise ComparisonInputError("unsupported schema_version")
    if raw.get("fixture_id") != "v4-ch11-synthetic-gradient-v1":
        raise ComparisonInputError("fixture_id does not match this chapter")
    if raw.get("label_source") != "synthetic_fixture":
        raise ComparisonInputError("fixture must remain labeled synthetic_fixture")

    x = raw.get("x")
    y = raw.get("y")
    if not isinstance(x, list) or not isinstance(y, list) or len(x) != len(y) or len(x) < 2:
        raise ComparisonInputError("x and y must be equal-length lists with at least two values")
    for index, value in enumerate(x):
        _finite_number(value, f"x[{index}]")
    for index, value in enumerate(y):
        _finite_number(value, f"y[{index}]")

    parameters = raw.get("initial_parameters")
    if not isinstance(parameters, dict):
        raise ComparisonInputError("initial_parameters must be an object")
    for name in ("weight", "bias"):
        _finite_number(parameters.get(name), f"initial_parameters.{name}")

    tolerance = _finite_number(raw.get("absolute_tolerance"), "absolute_tolerance")
    if not 0 < tolerance <= 0.01:
        raise ComparisonInputError("absolute_tolerance must be greater than 0 and at most 0.01")

    metadata = raw.get("metadata")
    if not isinstance(metadata, dict) or any(metadata.get(key) is not False for key in METADATA_KEYS):
        raise ComparisonInputError("fixture metadata must explicitly disclaim real data, models, training, GPU and benchmarks")
    return raw


def load_fixture(path: Path = DEFAULT_FIXTURE) -> tuple[dict[str, Any], bytes]:
    try:
        fixture_bytes = path.read_bytes()
    except OSError as error:
        raise ComparisonInputError(f"cannot read fixture: {error}") from error
    try:
        fixture = json.loads(fixture_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ComparisonInputError(f"cannot parse fixture JSON: {error}") from error
    return validate_fixture(fixture), fixture_bytes


def reference_result(fixture: dict[str, Any]) -> dict[str, float]:
    """Evaluate MSE and its closed-form gradients without a tensor library."""
    validate_fixture(fixture)
    x = [float(value) for value in fixture["x"]]
    y = [float(value) for value in fixture["y"]]
    weight = float(fixture["initial_parameters"]["weight"])
    bias = float(fixture["initial_parameters"]["bias"])
    residuals = [weight * xv + bias - yv for xv, yv in zip(x, y)]
    count = len(x)
    loss = sum(error * error for error in residuals) / count
    gradient_weight = 2.0 * sum(error * xv for error, xv in zip(residuals, x)) / count
    gradient_bias = 2.0 * sum(residuals) / count
    return {
        "loss": loss,
        "gradient_weight": gradient_weight,
        "gradient_bias": gradient_bias,
    }


def _as_float(value: Any) -> float:
    if hasattr(value, "item"):
        value = value.item()
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError("framework returned a non-finite scalar")
    return result


def _torch_result(fixture: dict[str, Any]) -> tuple[dict[str, float], str]:
    torch = importlib.import_module("torch")
    device = torch.device("cpu")
    x = torch.tensor(fixture["x"], dtype=torch.float32, device=device)
    y = torch.tensor(fixture["y"], dtype=torch.float32, device=device)
    weight = torch.tensor(float(fixture["initial_parameters"]["weight"]), dtype=torch.float32, device=device, requires_grad=True)
    bias = torch.tensor(float(fixture["initial_parameters"]["bias"]), dtype=torch.float32, device=device, requires_grad=True)
    loss = torch.mean((weight * x + bias - y) ** 2)
    loss.backward()
    return (
        {
            "loss": _as_float(loss),
            "gradient_weight": _as_float(weight.grad),
            "gradient_bias": _as_float(bias.grad),
        },
        str(getattr(torch, "__version__", "unknown")),
    )


def _jax_result(fixture: dict[str, Any]) -> tuple[dict[str, float], str]:
    jax = importlib.import_module("jax")
    jnp = importlib.import_module("jax.numpy")
    cpu_devices = jax.devices("cpu")
    if not cpu_devices:
        raise RuntimeError("JAX reports no CPU device")
    device = cpu_devices[0]
    x = jax.device_put(jnp.asarray(fixture["x"], dtype=jnp.float32), device)
    y = jax.device_put(jnp.asarray(fixture["y"], dtype=jnp.float32), device)
    initial = fixture["initial_parameters"]

    def objective(parameters: tuple[Any, Any]) -> Any:
        weight, bias = parameters
        return jnp.mean((weight * x + bias - y) ** 2)

    parameters = (
        jax.device_put(jnp.asarray(float(initial["weight"]), dtype=jnp.float32), device),
        jax.device_put(jnp.asarray(float(initial["bias"]), dtype=jnp.float32), device),
    )
    loss, gradients = jax.value_and_grad(objective)(parameters)
    return (
        {
            "loss": _as_float(loss),
            "gradient_weight": _as_float(gradients[0]),
            "gradient_bias": _as_float(gradients[1]),
        },
        str(getattr(jax, "__version__", "unknown")),
    )


def _tensorflow_result(fixture: dict[str, Any]) -> tuple[dict[str, float], str]:
    tf = importlib.import_module("tensorflow")
    initial = fixture["initial_parameters"]
    with tf.device("/CPU:0"):
        x = tf.constant(fixture["x"], dtype=tf.float32)
        y = tf.constant(fixture["y"], dtype=tf.float32)
        weight = tf.Variable(float(initial["weight"]), dtype=tf.float32)
        bias = tf.Variable(float(initial["bias"]), dtype=tf.float32)
        with tf.GradientTape() as tape:
            loss = tf.reduce_mean(tf.square(weight * x + bias - y))
        gradient_weight, gradient_bias = tape.gradient(loss, [weight, bias])
    if gradient_weight is None or gradient_bias is None:
        raise RuntimeError("GradientTape did not return both gradients")
    return (
        {
            "loss": _as_float(loss),
            "gradient_weight": _as_float(gradient_weight),
            "gradient_bias": _as_float(gradient_bias),
        },
        str(getattr(tf, "__version__", "unknown")),
    )


_RUNNERS = {
    "torch": _torch_result,
    "jax": _jax_result,
    "tensorflow": _tensorflow_result,
}


def run_backend(name: str, fixture: dict[str, Any]) -> dict[str, Any]:
    if name not in _RUNNERS:
        raise ComparisonInputError(f"unknown backend: {name}")
    try:
        observed, version = _RUNNERS[name](fixture)
    except ModuleNotFoundError as error:
        missing_root = (error.name or "").split(".", maxsplit=1)[0]
        if missing_root == name:
            return {"backend": name, "status": "not_installed"}
        return {"backend": name, "status": "import_error", "error_type": type(error).__name__}
    except Exception as error:
        return {"backend": name, "status": "import_error", "error_type": type(error).__name__}

    expected = reference_result(fixture)
    tolerance = float(fixture["absolute_tolerance"])
    differences = {
        key: abs(observed[key] - expected[key])
        for key in expected
    }
    passed = all(math.isfinite(observed[key]) and differences[key] <= tolerance for key in expected)
    return {
        "backend": name,
        "status": "passed" if passed else "mismatch",
        "version": version,
        "device": "cpu",
        "observed": observed,
        "absolute_difference_from_reference": differences,
        "tolerance": tolerance,
    }


def build_report(fixture: dict[str, Any], fixture_bytes: bytes, requested_backend: str = "all") -> dict[str, Any]:
    validate_fixture(fixture)
    if requested_backend not in ("reference", "all", *BACKENDS):
        raise ComparisonInputError(f"unknown backend: {requested_backend}")
    expected = reference_result(fixture)
    selected = BACKENDS if requested_backend == "all" else (() if requested_backend == "reference" else (requested_backend,))
    backend_results = {name: run_backend(name, fixture) for name in selected}
    passed = [name for name, row in backend_results.items() if row["status"] == "passed"]
    skipped = [name for name, row in backend_results.items() if row["status"] == "not_installed"]
    failed = [name for name, row in backend_results.items() if row["status"] not in {"passed", "not_installed"}]
    if failed:
        status = "failed"
    elif skipped and passed:
        status = "passed_with_skips"
    elif skipped or requested_backend == "reference":
        status = "reference_only"
    else:
        status = "passed"
    return {
        "schema_version": 1,
        "fixture_id": fixture["fixture_id"],
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "requested_backend": requested_backend,
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "platform": f"{platform.system()} {platform.machine()}",
        "reference": expected,
        "framework_results": backend_results,
        "summary": {
            "status": status,
            "passed": passed,
            "skipped_not_installed": skipped,
            "failed": failed,
        },
        "scope": {
            "real_dataset_loaded": False,
            "pretrained_model_loaded": False,
            "training_performed": False,
            "gpu_used": False,
            "benchmark_performed": False,
            "network_access_performed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare MSE gradients using optional CPU framework adapters")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--backend", choices=("reference", "all", *BACKENDS), default="all")
    parser.add_argument("--output", type=Path, help="write JSON to a file instead of stdout")
    args = parser.parse_args(argv)
    try:
        fixture, fixture_bytes = load_fixture(args.fixture)
        report = build_report(fixture, fixture_bytes, args.backend)
    except ComparisonInputError as error:
        print(f"input error: {error}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote comparison report: {args.output}")
    else:
        sys.stdout.write(rendered)

    if report["summary"]["failed"]:
        return 1
    if args.backend not in {"all", "reference"} and report["framework_results"][args.backend]["status"] == "not_installed":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
