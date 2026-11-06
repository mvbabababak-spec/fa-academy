"""A tiny DDPM sampler using the exact score of a synthetic 2-D mixture.

This is an analytic teaching fixture, not a trained neural image/video model.
It uses only Python's standard library and writes a JSON audit/demo record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


DEFAULT_FIXTURE = Path(__file__).with_name("sample_mixture.json")
BETA_START = 0.0005
BETA_END = 0.06
DEFAULT_STEPS = 200
DEFAULT_SAMPLES = 64
DEFAULT_SEED = 53


@dataclass(frozen=True)
class DiffusionSchedule:
    betas: tuple[float, ...]
    alphas: tuple[float, ...]
    alpha_bars: tuple[float, ...]


def _time_index(t: int, steps: int) -> int:
    if isinstance(t, bool) or not isinstance(t, int) or not 0 <= t < steps:
        raise ValueError(f"t must be an integer in [0, {steps - 1}]")
    return t


def _finite_vector(values: Sequence[float], name: str) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a numeric sequence")
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric sequence") from exc
    if not result or not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must contain finite values")
    return result


def validate_fixture(fixture: Any) -> None:
    """Validate the deliberately narrow, synthetic 2-D fixture schema."""
    if not isinstance(fixture, dict):
        raise ValueError("fixture must be a JSON object")
    if fixture.get("schema_version") != 1:
        raise ValueError("unsupported fixture schema_version")
    if fixture.get("label_source") != "synthetic_fixture":
        raise ValueError("fixture label_source must be synthetic_fixture")
    if fixture.get("dimension") != 2:
        raise ValueError("this teaching sampler accepts only dimension=2")

    variance = fixture.get("component_variance")
    if isinstance(variance, bool) or not isinstance(variance, (int, float)):
        raise ValueError("component_variance must be numeric")
    if not math.isfinite(float(variance)) or float(variance) <= 0:
        raise ValueError("component_variance must be finite and positive")

    components = fixture.get("components")
    if not isinstance(components, list) or len(components) < 2:
        raise ValueError("fixture must contain at least two components")
    identifiers: list[str] = []
    weights: list[float] = []
    for component in components:
        if not isinstance(component, dict):
            raise ValueError("each component must be an object")
        identifier = component.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("each component needs a non-empty id")
        if identifier in identifiers:
            raise ValueError("component ids must be unique")
        identifiers.append(identifier)
        mean = _finite_vector(component.get("mean", ()), "component mean")
        if len(mean) != 2:
            raise ValueError("each component mean must have two coordinates")
        weight = component.get("weight")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError("component weight must be numeric")
        weight = float(weight)
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("component weights must be finite and non-negative")
        weights.append(weight)
    if not math.isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("component weights must sum to 1")
    if not any(weight > 0 for weight in weights):
        raise ValueError("at least one component weight must be positive")

    metadata = fixture.get("metadata")
    required_false = (
        "image_files_included",
        "video_files_included",
        "real_world_observations_included",
        "trained_weights_included",
    )
    if not isinstance(metadata, dict):
        raise ValueError("fixture metadata is required")
    if any(metadata.get(field) is not False for field in required_false):
        raise ValueError("fixture must explicitly exclude images, videos, observations, and trained weights")


def load_fixture(path: str | Path) -> tuple[dict[str, Any], str]:
    fixture_path = Path(path)
    raw = fixture_path.read_bytes()
    try:
        fixture = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"fixture is not valid UTF-8 JSON: {fixture_path.name}") from exc
    validate_fixture(fixture)
    return fixture, hashlib.sha256(raw).hexdigest()


def linear_beta_schedule(
    steps: int = DEFAULT_STEPS,
    beta_start: float = BETA_START,
    beta_end: float = BETA_END,
) -> DiffusionSchedule:
    """Create a linear beta schedule and its alpha / cumulative-alpha values."""
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 2:
        raise ValueError("steps must be an integer of at least 2")
    if not math.isfinite(beta_start) or not math.isfinite(beta_end):
        raise ValueError("beta endpoints must be finite")
    if not 0 < beta_start <= beta_end < 1:
        raise ValueError("beta endpoints must satisfy 0 < start <= end < 1")
    betas = tuple(
        beta_start + (beta_end - beta_start) * index / (steps - 1)
        for index in range(steps)
    )
    alphas = tuple(1.0 - beta for beta in betas)
    cumulative = 1.0
    alpha_bars: list[float] = []
    for alpha in alphas:
        cumulative *= alpha
        alpha_bars.append(cumulative)
    return DiffusionSchedule(betas, alphas, tuple(alpha_bars))


def q_sample(
    x0: Sequence[float],
    noise: Sequence[float],
    t: int,
    schedule: DiffusionSchedule,
) -> tuple[float, ...]:
    """Draw x_t from the closed-form forward marginal, given explicit noise."""
    t = _time_index(t, len(schedule.betas))
    clean = _finite_vector(x0, "x0")
    epsilon = _finite_vector(noise, "noise")
    if len(clean) != len(epsilon):
        raise ValueError("x0 and noise must have the same dimension")
    alpha_bar = schedule.alpha_bars[t]
    signal_scale = math.sqrt(alpha_bar)
    noise_scale = math.sqrt(1.0 - alpha_bar)
    return tuple(signal_scale * value + noise_scale * eps for value, eps in zip(clean, epsilon))


def predict_x0_from_epsilon(
    x_t: Sequence[float],
    epsilon_prediction: Sequence[float],
    t: int,
    schedule: DiffusionSchedule,
) -> tuple[float, ...]:
    """Invert the forward marginal when the noise value is known exactly."""
    t = _time_index(t, len(schedule.betas))
    noisy = _finite_vector(x_t, "x_t")
    epsilon = _finite_vector(epsilon_prediction, "epsilon_prediction")
    if len(noisy) != len(epsilon):
        raise ValueError("x_t and epsilon_prediction must have the same dimension")
    alpha_bar = schedule.alpha_bars[t]
    return tuple(
        (value - math.sqrt(1.0 - alpha_bar) * eps) / math.sqrt(alpha_bar)
        for value, eps in zip(noisy, epsilon)
    )


def ddpm_posterior_variance(t: int, schedule: DiffusionSchedule) -> float:
    """Return beta-tilde for q(x_(t-1) | x_t, x_0); it is zero at t=0."""
    t = _time_index(t, len(schedule.betas))
    previous_alpha_bar = 1.0 if t == 0 else schedule.alpha_bars[t - 1]
    current_alpha_bar = schedule.alpha_bars[t]
    denominator = 1.0 - current_alpha_bar
    variance = schedule.betas[t] * (1.0 - previous_alpha_bar) / denominator
    return max(0.0, variance)


def gaussian_mixture_score(
    x_t: Sequence[float],
    t: int,
    fixture: dict[str, Any],
    schedule: DiffusionSchedule,
) -> tuple[float, float]:
    """Compute the exact score of the noised fixture mixture, not a learned score."""
    validate_fixture(fixture)
    t = _time_index(t, len(schedule.betas))
    point = _finite_vector(x_t, "x_t")
    if len(point) != 2:
        raise ValueError("the fixture score is defined for two-dimensional points")

    alpha_bar = schedule.alpha_bars[t]
    mean_scale = math.sqrt(alpha_bar)
    variance_t = alpha_bar * float(fixture["component_variance"]) + (1.0 - alpha_bar)
    log_constant = -0.5 * 2 * math.log(2.0 * math.pi * variance_t)

    log_probabilities: list[float] = []
    scaled_means: list[tuple[float, float]] = []
    for component in fixture["components"]:
        mean = tuple(mean_scale * value for value in component["mean"])
        scaled_means.append((mean[0], mean[1]))
        weight = float(component["weight"])
        if weight == 0:
            log_probabilities.append(-math.inf)
            continue
        squared_distance = sum((value - center) ** 2 for value, center in zip(point, mean))
        log_probabilities.append(
            math.log(weight) + log_constant - squared_distance / (2.0 * variance_t)
        )

    maximum = max(log_probabilities)
    unnormalized = [math.exp(value - maximum) for value in log_probabilities]
    normalizer = sum(unnormalized)
    posterior_weights = [value / normalizer for value in unnormalized]
    score = tuple(
        sum(
            posterior_weight * (component_mean[axis] - point[axis]) / variance_t
            for posterior_weight, component_mean in zip(posterior_weights, scaled_means)
        )
        for axis in range(2)
    )
    return score[0], score[1]


def epsilon_from_score(
    score: Sequence[float],
    t: int,
    schedule: DiffusionSchedule,
) -> tuple[float, ...]:
    """Use score(x_t) = -E[epsilon | x_t] / sqrt(1-alpha_bar_t)."""
    t = _time_index(t, len(schedule.betas))
    gradient = _finite_vector(score, "score")
    scale = -math.sqrt(1.0 - schedule.alpha_bars[t])
    return tuple(scale * value for value in gradient)


def ddpm_reverse_step(
    x_t: Sequence[float],
    epsilon_prediction: Sequence[float],
    t: int,
    schedule: DiffusionSchedule,
    noise: Sequence[float] | None = None,
) -> tuple[float, ...]:
    """Apply one epsilon-parameterized DDPM reverse step."""
    t = _time_index(t, len(schedule.betas))
    noisy = _finite_vector(x_t, "x_t")
    epsilon = _finite_vector(epsilon_prediction, "epsilon_prediction")
    if len(noisy) != len(epsilon):
        raise ValueError("x_t and epsilon_prediction must have the same dimension")
    alpha_bar = schedule.alpha_bars[t]
    beta = schedule.betas[t]
    alpha = schedule.alphas[t]
    mean = tuple(
        (value - beta * eps / math.sqrt(1.0 - alpha_bar)) / math.sqrt(alpha)
        for value, eps in zip(noisy, epsilon)
    )
    variance = ddpm_posterior_variance(t, schedule)
    if t == 0:
        if noise is not None:
            raise ValueError("the final t=0 reverse step has zero posterior variance")
        return mean
    if noise is None:
        raise ValueError("noise is required when t > 0")
    random_noise = _finite_vector(noise, "noise")
    if len(random_noise) != len(mean):
        raise ValueError("reverse-step noise must match the point dimension")
    noise_scale = math.sqrt(variance)
    return tuple(value + noise_scale * eps for value, eps in zip(mean, random_noise))


def sample_mixture(
    fixture: dict[str, Any],
    schedule: DiffusionSchedule,
    count: int = DEFAULT_SAMPLES,
    seed: int = DEFAULT_SEED,
) -> tuple[tuple[float, float], ...]:
    """Sample from the toy mixture with an analytic-score DDPM reverse chain."""
    validate_fixture(fixture)
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("count must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    rng = random.Random(seed)
    points: list[tuple[float, float]] = [
        (rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)) for _ in range(count)
    ]
    for t in reversed(range(len(schedule.betas))):
        updated: list[tuple[float, float]] = []
        for point in points:
            score = gaussian_mixture_score(point, t, fixture, schedule)
            epsilon = epsilon_from_score(score, t, schedule)
            step_noise = None if t == 0 else (rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0))
            result = ddpm_reverse_step(point, epsilon, t, schedule, step_noise)
            updated.append((result[0], result[1]))
        points = updated
    return tuple(points)


def nearest_component_counts(
    samples: Sequence[Sequence[float]],
    fixture: dict[str, Any],
) -> dict[str, int]:
    """Count nearest synthetic centers; this is a demo summary, not an evaluator."""
    validate_fixture(fixture)
    counts = {component["id"]: 0 for component in fixture["components"]}
    for sample in samples:
        point = _finite_vector(sample, "sample")
        if len(point) != 2:
            raise ValueError("samples must be two-dimensional")
        nearest = min(
            fixture["components"],
            key=lambda component: sum(
                (point[axis] - float(component["mean"][axis])) ** 2 for axis in range(2)
            ),
        )
        counts[nearest["id"]] += 1
    return counts


def _fixture_record(fixture: dict[str, Any], fixture_hash: str, path: Path) -> dict[str, Any]:
    return {
        "path": path.name,
        "sha256": fixture_hash,
        "fixture_id": fixture["fixture_id"],
        "label_source": fixture["label_source"],
        "dimension": fixture["dimension"],
        "components": len(fixture["components"]),
        "image_files_included": fixture["metadata"]["image_files_included"],
        "video_files_included": fixture["metadata"]["video_files_included"],
        "real_world_observations_included": fixture["metadata"]["real_world_observations_included"],
        "trained_weights_included": fixture["metadata"]["trained_weights_included"],
    }


def run_audit(fixture: dict[str, Any], fixture_hash: str, fixture_path: Path) -> dict[str, Any]:
    return {
        "status": "synthetic_diffusion_fixture_audit_complete",
        "mode": "audit",
        "training_performed": False,
        "neural_model_loaded": False,
        "model_downloaded": False,
        "image_files_loaded": False,
        "video_files_loaded": False,
        "device": "CPU; Python standard library only",
        "fixture": _fixture_record(fixture, fixture_hash, fixture_path),
        "claims_not_supported": [
            "quality of a trained image or video model",
            "Persian-language output quality",
            "hardware performance or benchmark results",
            "copyright clearance, privacy compliance, or legal conclusions",
        ],
    }


def run_demo(
    fixture: dict[str, Any],
    fixture_hash: str,
    fixture_path: Path,
    steps: int = DEFAULT_STEPS,
    sample_count: int = DEFAULT_SAMPLES,
    seed: int = DEFAULT_SEED,
    beta_start: float = BETA_START,
    beta_end: float = BETA_END,
) -> dict[str, Any]:
    schedule = linear_beta_schedule(steps, beta_start, beta_end)
    samples = sample_mixture(fixture, schedule, sample_count, seed)
    means = [sum(sample[axis] for sample in samples) / len(samples) for axis in range(2)]
    return {
        "status": "analytic_synthetic_mixture_ddpm_demo_complete",
        "mode": "demo",
        "training_performed": False,
        "neural_model_loaded": False,
        "model_downloaded": False,
        "image_files_loaded": False,
        "video_files_loaded": False,
        "analytic_score_used": True,
        "score_source": "closed_form_density_of_known_synthetic_gaussian_mixture",
        "device": "CPU; Python standard library only",
        "fixture": _fixture_record(fixture, fixture_hash, fixture_path),
        "sampling": {
            "method": "epsilon-parameterized DDPM reverse updates",
            "initial_prior": "standard-normal approximation at the terminal timestep",
            "timesteps": steps,
            "beta_start": beta_start,
            "beta_end": beta_end,
            "terminal_alpha_bar": schedule.alpha_bars[-1],
            "sample_count": sample_count,
            "seed": seed,
            "posterior_noise_added_at_t0": False,
        },
        "nearest_synthetic_center_counts": nearest_component_counts(samples, fixture),
        "sample_mean": means,
        "samples": [list(sample) for sample in samples],
        "interpretation_limit": "Toy 2-D distribution only; not image/video generation or model evaluation.",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a synthetic diffusion fixture or run its analytic toy sampler")
    parser.add_argument("--mode", choices=("audit", "demo"), required=True)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, required=True, help="directory for run.json")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--beta-start", type=float, default=BETA_START)
    parser.add_argument("--beta-end", type=float, default=BETA_END)
    args = parser.parse_args(argv)

    fixture, fixture_hash = load_fixture(args.fixture)
    if args.mode == "audit":
        result = run_audit(fixture, fixture_hash, args.fixture)
    else:
        result = run_demo(
            fixture,
            fixture_hash,
            args.fixture,
            steps=args.steps,
            sample_count=args.samples,
            seed=args.seed,
            beta_start=args.beta_start,
            beta_end=args.beta_end,
        )
    result["python"] = ".".join(map(str, sys.version_info[:3]))
    output_file = args.output / "run.json"
    _write_json(output_file, result)
    print(json.dumps({"status": result["status"], "output": str(output_file), "fixture_sha256": fixture_hash}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
