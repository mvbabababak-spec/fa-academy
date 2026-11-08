"""First-order, configuration-driven estimates for model memory and FLOPs.

The module performs arithmetic on an explicitly synthetic fixture. It does not
load a model, inspect a GPU, train, benchmark, or predict real-world quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_FIXTURE = Path(__file__).with_name("sample_profiles.json")
BYTES_PER_GB = 1_000_000_000
BYTES_PER_GIB = 1024**3
SCHEMA_VERSION = 1


class EstimationInputError(ValueError):
    """Raised when a workload profile is malformed or outside the model."""


def _integer(name: str, value: Any, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise EstimationInputError(f"{name} must be an integer >= {minimum}")
    return value


def _number(name: str, value: Any, *, minimum: float = 0.0) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EstimationInputError(f"{name} must be a finite number >= {minimum}")
    if isinstance(value, float) and not math.isfinite(value):
        raise EstimationInputError(f"{name} must be a finite number >= {minimum}")
    if value < minimum:
        raise EstimationInputError(f"{name} must be a finite number >= {minimum}")
    return value


def _normalize(value: int | float) -> int | float:
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return int(value)
    return value


def _scaled(count: int, bytes_per_item: int | float) -> int | float:
    return _normalize(count * bytes_per_item)


def _divided(value: int | float, divisor: int) -> int | float:
    return _normalize(value / divisor)


def byte_units(byte_count: int | float) -> dict[str, int | float]:
    """Return bytes plus decimal GB and binary GiB; GB and GiB are not equal."""
    count = _number("byte_count", byte_count)
    return {
        "bytes": _normalize(count),
        "decimal_GB": round(count / BYTES_PER_GB, 6),
        "binary_GiB": round(count / BYTES_PER_GIB, 6),
    }


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EstimationInputError(f"{name} must be an object")
    return value


def estimate_kv_cache(
    *,
    layers: int,
    active_sequences: int,
    context_tokens: int,
    kv_heads: int,
    head_dim: int,
    bytes_per_element: int | float,
) -> int | float:
    """Estimate uncompressed K and V storage for a decoder KV cache.

    The estimate is 2 * layers * batch * tokens * KV-heads * head-dimension
    * bytes-per-element. It is not applicable unchanged to every architecture.
    """
    layer_count = _integer("layers", layers, minimum=1)
    batch = _integer("active_sequences", active_sequences)
    tokens = _integer("context_tokens", context_tokens)
    key_value_heads = _integer("kv_heads", kv_heads, minimum=1)
    dimension = _integer("head_dim", head_dim, minimum=1)
    element_bytes = _number("bytes_per_element", bytes_per_element, minimum=0.000001)
    return _normalize(
        2 * layer_count * batch * tokens * key_value_heads * dimension * element_bytes
    )


def estimate_activation_reference(
    *,
    microbatch: int,
    sequence_tokens: int,
    hidden_size: int,
    layers: int,
    saved_tensors_per_layer: int,
    bytes_per_element: int | float,
) -> int | float:
    """Count a declared number of hidden-state-sized activation equivalents.

    This deliberately transparent scenario is not a framework-level prediction
    of actual activation memory. Attention, MLP intermediates, rematerialization,
    fusion, tensor layouts, and implementation details can change the peak.
    """
    batch = _integer("microbatch", microbatch, minimum=1)
    tokens = _integer("sequence_tokens", sequence_tokens, minimum=1)
    width = _integer("hidden_size", hidden_size, minimum=1)
    layer_count = _integer("layers", layers, minimum=1)
    saved_count = _integer("saved_tensors_per_layer", saved_tensors_per_layer)
    element_bytes = _number("bytes_per_element", bytes_per_element, minimum=0.000001)
    return _normalize(batch * tokens * width * layer_count * saved_count * element_bytes)


def estimate_inference(
    *,
    model_parameters: int,
    weight_bytes_per_parameter: int | float,
    kv_cache_bytes: int | float = 0,
    runtime_and_temporary_bytes: int | float = 0,
    safety_bytes: int | float = 0,
) -> dict[str, Any]:
    """Add explicitly supplied inference memory components for one device."""
    parameters = _integer("model_parameters", model_parameters, minimum=1)
    weight_size = _number("weight_bytes_per_parameter", weight_bytes_per_parameter)
    kv_size = _number("kv_cache_bytes", kv_cache_bytes)
    runtime_size = _number("runtime_and_temporary_bytes", runtime_and_temporary_bytes)
    margin = _number("safety_bytes", safety_bytes)

    weights = _scaled(parameters, weight_size)
    total = weights + kv_size + runtime_size + margin
    return {
        "kind": "inference_memory",
        "model_weights": byte_units(weights),
        "kv_cache": byte_units(kv_size),
        "runtime_and_temporary": byte_units(runtime_size),
        "safety_reserve": byte_units(margin),
        "total_estimate": byte_units(total),
        "scope": "configured arithmetic; not a device-fit guarantee",
    }


def estimate_training(
    *,
    model_parameters: int,
    trainable_parameters: int,
    weight_bytes_per_parameter: int | float,
    gradient_bytes_per_trainable_parameter: int | float,
    master_weight_bytes_per_trainable_parameter: int | float,
    optimizer_state_bytes_per_trainable_parameter: int | float,
    world_size: int = 1,
    zero_stage: int = 0,
    activation_model: dict[str, Any] | None = None,
    activation_bytes_override: int | float | None = None,
    temporary_bytes: int | float = 0,
    safety_bytes: int | float = 0,
) -> dict[str, Any]:
    """Estimate per-rank model-state and declared non-state memory.

    ``zero_stage`` uses idealized ZeRO divisors: stage 1 partitions optimizer
    state/master copies, stage 2 additionally partitions gradients, and stage 3
    additionally partitions parameters. Communication/all-gather buffers,
    padding, fragmentation, and framework-specific behavior are not modelled.
    """
    parameters = _integer("model_parameters", model_parameters, minimum=1)
    trainable = _integer("trainable_parameters", trainable_parameters)
    if trainable > parameters:
        raise EstimationInputError("trainable_parameters cannot exceed model_parameters")
    ranks = _integer("world_size", world_size, minimum=1)
    stage = _integer("zero_stage", zero_stage)
    if stage > 3:
        raise EstimationInputError("zero_stage must be an integer in [0, 3]")

    weight_b = _number("weight_bytes_per_parameter", weight_bytes_per_parameter)
    gradient_b = _number(
        "gradient_bytes_per_trainable_parameter", gradient_bytes_per_trainable_parameter
    )
    master_b = _number(
        "master_weight_bytes_per_trainable_parameter",
        master_weight_bytes_per_trainable_parameter,
    )
    optimizer_b = _number(
        "optimizer_state_bytes_per_trainable_parameter",
        optimizer_state_bytes_per_trainable_parameter,
    )
    temporary = _number("temporary_bytes", temporary_bytes)
    margin = _number("safety_bytes", safety_bytes)

    if activation_model is not None and activation_bytes_override is not None:
        raise EstimationInputError(
            "supply activation_model or activation_bytes_override, not both"
        )
    if activation_model is not None:
        activation_inputs = _require_mapping("activation_model", activation_model)
        activation_bytes = estimate_activation_reference(**activation_inputs)
        activation_basis = {
            "kind": "hidden_state_equivalents",
            "inputs": activation_inputs,
            "interpretation": "user-configured reference scenario, not a measured peak",
        }
    elif activation_bytes_override is not None:
        activation_bytes = _number("activation_bytes_override", activation_bytes_override)
        activation_basis = {
            "kind": "externally_supplied_bytes",
            "interpretation": "user-supplied value; no measurement performed by this program",
        }
    else:
        activation_bytes = 0
        activation_basis = {
            "kind": "not_estimated",
            "interpretation": "zero is a placeholder; actual activations must be measured or supplied",
        }

    parameter_divisor = ranks if stage == 3 else 1
    gradient_divisor = ranks if stage >= 2 else 1
    optimizer_divisor = ranks if stage >= 1 else 1

    weights = _divided(_scaled(parameters, weight_b), parameter_divisor)
    gradients = _divided(_scaled(trainable, gradient_b), gradient_divisor)
    master_weights = _divided(_scaled(trainable, master_b), optimizer_divisor)
    optimizer_states = _divided(_scaled(trainable, optimizer_b), optimizer_divisor)
    state_total = weights + gradients + master_weights + optimizer_states
    total = state_total + activation_bytes + temporary + margin

    return {
        "kind": "training_memory_per_rank",
        "assumptions": {
            "model_parameters": parameters,
            "trainable_parameters": trainable,
            "world_size": ranks,
            "zero_stage": stage,
            "weight_bytes_per_parameter": weight_b,
            "gradient_bytes_per_trainable_parameter": gradient_b,
            "master_weight_bytes_per_trainable_parameter": master_b,
            "optimizer_state_bytes_per_trainable_parameter": optimizer_b,
        },
        "idealized_sharding_divisors": {
            "parameters": parameter_divisor,
            "gradients": gradient_divisor,
            "master_and_optimizer_states": optimizer_divisor,
        },
        "model_states_per_rank": {
            "model_weights": byte_units(weights),
            "trainable_gradients": byte_units(gradients),
            "trainable_master_weights": byte_units(master_weights),
            "trainable_optimizer_states": byte_units(optimizer_states),
            "subtotal": byte_units(state_total),
        },
        "non_state_memory_per_rank": {
            "activation_reference": byte_units(activation_bytes),
            "activation_basis": activation_basis,
            "temporary_workspaces": byte_units(temporary),
            "safety_reserve": byte_units(margin),
        },
        "total_estimate_per_rank": byte_units(total),
        "scope": (
            "first-order per-rank accounting; excludes unmodelled communication buffers, "
            "allocator effects, offload copies, and other implementation-specific memory"
        ),
    }


def estimate_training_flops(
    *, model_parameters: int, training_tokens: int, flops_per_parameter_token: int = 6
) -> int:
    """Return C ≈ k*N*D; k=6 is a dense-transformer first-order convention."""
    parameters = _integer("model_parameters", model_parameters, minimum=1)
    tokens = _integer("training_tokens", training_tokens)
    factor = _integer("flops_per_parameter_token", flops_per_parameter_token, minimum=1)
    return factor * parameters * tokens


def estimate_inference_flops(
    *,
    model_parameters: int,
    prompt_tokens: int,
    generated_tokens: int,
    batch_size: int = 1,
    flops_per_parameter_token: int = 2,
) -> int:
    """Approximate dense linear-layer FLOPs over prompt and generated tokens.

    This omits the sequence-quadratic attention term in prefill and many
    architecture/runtime costs; it is not a latency prediction.
    """
    parameters = _integer("model_parameters", model_parameters, minimum=1)
    prompt = _integer("prompt_tokens", prompt_tokens)
    generated = _integer("generated_tokens", generated_tokens)
    batch = _integer("batch_size", batch_size, minimum=1)
    factor = _integer("flops_per_parameter_token", flops_per_parameter_token, minimum=1)
    return factor * parameters * batch * (prompt + generated)


def roofline_lower_bound_seconds(
    *,
    floating_point_operations: int,
    bytes_moved: int,
    effective_flops_per_second: int | float,
    effective_bytes_per_second: int | float,
) -> dict[str, float]:
    """Compute a roofline-style lower bound from user-supplied effective rates."""
    operations = _integer("floating_point_operations", floating_point_operations)
    traffic = _integer("bytes_moved", bytes_moved)
    compute_rate = _number("effective_flops_per_second", effective_flops_per_second, minimum=0.000001)
    bandwidth = _number("effective_bytes_per_second", effective_bytes_per_second, minimum=0.000001)
    compute_bound = operations / compute_rate
    bandwidth_bound = traffic / bandwidth
    return {
        "compute_bound_seconds": compute_bound,
        "bandwidth_bound_seconds": bandwidth_bound,
        "lower_bound_seconds": max(compute_bound, bandwidth_bound),
        "warning": "a lower bound only; rates are user inputs, not measured by this project",
    }


def validate_fixture(fixture: Any) -> None:
    """Validate the synthetic fixture and every profile before calculating."""
    if not isinstance(fixture, dict):
        raise EstimationInputError("fixture must be a JSON object")
    if fixture.get("schema_version") != SCHEMA_VERSION:
        raise EstimationInputError("unsupported fixture schema_version")
    if fixture.get("label_source") != "synthetic_fixture":
        raise EstimationInputError("fixture label_source must be synthetic_fixture")
    metadata = _require_mapping("metadata", fixture.get("metadata"))
    for field in (
        "real_model_weights_included",
        "real_hardware_measurements_performed",
        "training_performed",
        "benchmark_performed",
    ):
        if metadata.get(field) is not False:
            raise EstimationInputError(f"fixture metadata must explicitly set {field}=false")

    profiles = fixture.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise EstimationInputError("fixture profiles must be a non-empty array")
    identifiers: set[str] = set()
    for profile in profiles:
        profile = _require_mapping("profile", profile)
        identifier = profile.get("profile_id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise EstimationInputError("each profile needs a non-empty profile_id")
        if identifier in identifiers:
            raise EstimationInputError("profile_id values must be unique")
        identifiers.add(identifier)
        kind = profile.get("kind")
        if kind == "inference":
            _integer("model_parameters", profile.get("model_parameters"), minimum=1)
            _number("weight_bytes_per_parameter", profile.get("weight_bytes_per_parameter"))
            cache = _require_mapping("kv_cache", profile.get("kv_cache"))
            required = ("layers", "active_sequences", "context_tokens", "kv_heads", "head_dim", "bytes_per_element")
            if any(field not in cache for field in required):
                raise EstimationInputError(f"{identifier}: kv_cache is missing a required field")
            estimate_kv_cache(**{field: cache[field] for field in required})
            _number("runtime_and_temporary_bytes", profile.get("runtime_and_temporary_bytes", 0))
            _number("safety_bytes", profile.get("safety_bytes", 0))
        elif kind == "training":
            parameters = _integer("model_parameters", profile.get("model_parameters"), minimum=1)
            trainable = _integer("trainable_parameters", profile.get("trainable_parameters"))
            if trainable > parameters:
                raise EstimationInputError("trainable_parameters cannot exceed model_parameters")
            for field in (
                "weight_bytes_per_parameter",
                "gradient_bytes_per_trainable_parameter",
                "master_weight_bytes_per_trainable_parameter",
                "optimizer_state_bytes_per_trainable_parameter",
            ):
                _number(field, profile.get(field))
            _integer("world_size", profile.get("world_size", 1), minimum=1)
            stage = _integer("zero_stage", profile.get("zero_stage", 0))
            if stage > 3:
                raise EstimationInputError("zero_stage must be an integer in [0, 3]")
            if "activation_model" in profile:
                activation_model = _require_mapping("activation_model", profile["activation_model"])
                estimate_activation_reference(**activation_model)
            _number("temporary_bytes", profile.get("temporary_bytes", 0))
            _number("safety_bytes", profile.get("safety_bytes", 0))
            if "training_tokens" in profile:
                _integer("training_tokens", profile["training_tokens"])
        else:
            raise EstimationInputError(f"{identifier}: kind must be inference or training")


def load_fixture(path: str | Path = DEFAULT_FIXTURE) -> tuple[dict[str, Any], str]:
    fixture_path = Path(path)
    raw = fixture_path.read_bytes()
    try:
        fixture = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EstimationInputError(f"fixture is not valid UTF-8 JSON: {fixture_path.name}") from exc
    validate_fixture(fixture)
    return fixture, hashlib.sha256(raw).hexdigest()


def analyze_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one validated profile, preserving its declared assumptions."""
    common = {"profile_id": profile["profile_id"], "label": profile.get("label", "")}
    if profile["kind"] == "inference":
        cache_inputs = profile["kv_cache"]
        cache_bytes = estimate_kv_cache(**cache_inputs)
        estimate = estimate_inference(
            model_parameters=profile["model_parameters"],
            weight_bytes_per_parameter=profile["weight_bytes_per_parameter"],
            kv_cache_bytes=cache_bytes,
            runtime_and_temporary_bytes=profile.get("runtime_and_temporary_bytes", 0),
            safety_bytes=profile.get("safety_bytes", 0),
        )
        output = {**common, "kind": "inference", "kv_cache_inputs": cache_inputs, "estimate": estimate}
        if "prompt_tokens" in profile or "generated_tokens" in profile:
            output["linear_layer_flops"] = estimate_inference_flops(
                model_parameters=profile["model_parameters"],
                prompt_tokens=profile.get("prompt_tokens", 0),
                generated_tokens=profile.get("generated_tokens", 0),
                batch_size=cache_inputs["active_sequences"],
            )
        return output

    activation_model = profile.get("activation_model")
    estimate = estimate_training(
        model_parameters=profile["model_parameters"],
        trainable_parameters=profile["trainable_parameters"],
        weight_bytes_per_parameter=profile["weight_bytes_per_parameter"],
        gradient_bytes_per_trainable_parameter=profile["gradient_bytes_per_trainable_parameter"],
        master_weight_bytes_per_trainable_parameter=profile["master_weight_bytes_per_trainable_parameter"],
        optimizer_state_bytes_per_trainable_parameter=profile["optimizer_state_bytes_per_trainable_parameter"],
        world_size=profile.get("world_size", 1),
        zero_stage=profile.get("zero_stage", 0),
        activation_model=activation_model,
        temporary_bytes=profile.get("temporary_bytes", 0),
        safety_bytes=profile.get("safety_bytes", 0),
    )
    output = {**common, "kind": "training", "estimate": estimate}
    if "training_tokens" in profile:
        output["training_flops_approximation"] = estimate_training_flops(
            model_parameters=profile["model_parameters"],
            training_tokens=profile["training_tokens"],
        )
    return output


def run_demo(fixture_path: str | Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    """Return deterministic arithmetic results for all fixture profiles."""
    fixture, digest = load_fixture(fixture_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture": {
            "fixture_id": fixture.get("fixture_id", "unnamed"),
            "sha256": digest,
            "label_source": fixture["label_source"],
        },
        "scope": {
            "real_model_loaded": False,
            "real_hardware_measured": False,
            "training_performed": False,
            "benchmark_performed": False,
            "claim": "configured arithmetic and synthetic profiles only",
        },
        "scenarios": [analyze_profile(profile) for profile in fixture["profiles"]],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="First-order model memory/FLOPs estimator")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write JSON to this path (default: stdout)")
    args = parser.parse_args(argv)
    result = run_demo(args.fixture)
    serialized = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(f"Wrote arithmetic-only report: {args.output}")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
