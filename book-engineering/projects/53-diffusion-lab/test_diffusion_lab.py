"""Unit tests for the analytic synthetic-mixture diffusion lab."""
from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from diffusion_lab import (
    DEFAULT_FIXTURE,
    DEFAULT_SAMPLES,
    DEFAULT_SEED,
    DEFAULT_STEPS,
    BETA_END,
    BETA_START,
    ddpm_posterior_variance,
    ddpm_reverse_step,
    epsilon_from_score,
    gaussian_mixture_score,
    linear_beta_schedule,
    load_fixture,
    nearest_component_counts,
    predict_x0_from_epsilon,
    q_sample,
    run_demo,
    sample_mixture,
    validate_fixture,
)


ROOT = Path(__file__).resolve().parent
FIXTURE, FIXTURE_HASH = load_fixture(DEFAULT_FIXTURE)


class FixtureTests(unittest.TestCase):
    def test_fixture_loads_with_sha256(self):
        fixture, digest = load_fixture(DEFAULT_FIXTURE)
        self.assertEqual(fixture["fixture_id"], "v4-ch07-2d-gaussian-mixture-v1")
        self.assertEqual(len(digest), 64)
        self.assertEqual(fixture["label_source"], "synthetic_fixture")

    def test_fixture_has_four_balanced_components(self):
        validate_fixture(FIXTURE)
        self.assertEqual(len(FIXTURE["components"]), 4)
        self.assertEqual(sum(row["weight"] for row in FIXTURE["components"]), 1.0)

    def test_fixture_excludes_real_media_and_weights(self):
        metadata = FIXTURE["metadata"]
        self.assertIs(metadata["image_files_included"], False)
        self.assertIs(metadata["video_files_included"], False)
        self.assertIs(metadata["real_world_observations_included"], False)
        self.assertIs(metadata["trained_weights_included"], False)

    def test_fixture_rejects_non_synthetic_label(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["label_source"] = "collected_data"
        with self.assertRaises(ValueError):
            validate_fixture(fixture)

    def test_fixture_rejects_weights_that_do_not_sum_to_one(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["components"][0]["weight"] = 0.5
        with self.assertRaisesRegex(ValueError, "sum to 1"):
            validate_fixture(fixture)

    def test_fixture_rejects_wrong_mean_dimension(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["components"][0]["mean"] = [1.0]
        with self.assertRaisesRegex(ValueError, "two coordinates"):
            validate_fixture(fixture)

    def test_fixture_rejects_included_image_files(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["metadata"]["image_files_included"] = True
        with self.assertRaisesRegex(ValueError, "explicitly exclude"):
            validate_fixture(fixture)

    def test_fixture_rejects_non_finite_component_mean(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["components"][0]["mean"][0] = math.inf
        with self.assertRaisesRegex(ValueError, "finite"):
            validate_fixture(fixture)


class ScheduleTests(unittest.TestCase):
    def test_linear_schedule_length_and_endpoints(self):
        schedule = linear_beta_schedule(steps=7, beta_start=0.01, beta_end=0.07)
        self.assertEqual(len(schedule.betas), 7)
        self.assertAlmostEqual(schedule.betas[0], 0.01)
        self.assertAlmostEqual(schedule.betas[-1], 0.07)

    def test_alpha_bars_are_positive_and_strictly_decreasing(self):
        schedule = linear_beta_schedule(steps=20)
        self.assertTrue(all(0 < value <= 1 for value in schedule.alpha_bars))
        self.assertTrue(all(a > b for a, b in zip(schedule.alpha_bars, schedule.alpha_bars[1:])))

    def test_schedule_rejects_too_few_steps(self):
        with self.assertRaises(ValueError):
            linear_beta_schedule(steps=1)

    def test_schedule_rejects_boolean_step_count(self):
        with self.assertRaises(ValueError):
            linear_beta_schedule(steps=True)

    def test_schedule_rejects_beta_outside_open_unit_interval(self):
        with self.assertRaises(ValueError):
            linear_beta_schedule(beta_start=0.0, beta_end=0.02)
        with self.assertRaises(ValueError):
            linear_beta_schedule(beta_start=0.01, beta_end=1.0)

    def test_schedule_rejects_reversed_beta_endpoints(self):
        with self.assertRaises(ValueError):
            linear_beta_schedule(beta_start=0.1, beta_end=0.01)

    def test_schedule_rejects_non_finite_beta(self):
        with self.assertRaises(ValueError):
            linear_beta_schedule(beta_start=float("nan"), beta_end=0.1)


class ForwardAndPosteriorTests(unittest.TestCase):
    def setUp(self):
        self.schedule = linear_beta_schedule(steps=12)
        self.clean = (1.25, -0.75)
        self.noise = (-0.5, 0.8)

    def test_forward_sample_matches_closed_form(self):
        t = 4
        alpha_bar = self.schedule.alpha_bars[t]
        expected = tuple(
            math.sqrt(alpha_bar) * clean + math.sqrt(1.0 - alpha_bar) * noise
            for clean, noise in zip(self.clean, self.noise)
        )
        self.assertEqual(q_sample(self.clean, self.noise, t, self.schedule), expected)

    def test_zero_noise_forward_sample_only_scales_signal(self):
        t = 0
        result = q_sample(self.clean, (0.0, 0.0), t, self.schedule)
        expected = tuple(math.sqrt(self.schedule.alpha_bars[t]) * value for value in self.clean)
        self.assertEqual(result, expected)

    def test_known_noise_inverts_forward_sample(self):
        for t in (0, 3, 7, 11):
            noisy = q_sample(self.clean, self.noise, t, self.schedule)
            recovered = predict_x0_from_epsilon(noisy, self.noise, t, self.schedule)
            for actual, expected in zip(recovered, self.clean):
                self.assertAlmostEqual(actual, expected, places=12)

    def test_forward_sample_rejects_dimension_mismatch(self):
        with self.assertRaisesRegex(ValueError, "same dimension"):
            q_sample((1.0, 2.0), (0.0,), 1, self.schedule)

    def test_inverse_rejects_dimension_mismatch(self):
        with self.assertRaisesRegex(ValueError, "same dimension"):
            predict_x0_from_epsilon((1.0, 2.0), (0.0,), 1, self.schedule)

    def test_forward_sample_rejects_out_of_range_timestep(self):
        with self.assertRaises(ValueError):
            q_sample(self.clean, self.noise, len(self.schedule.betas), self.schedule)

    def test_posterior_variance_is_zero_at_final_reverse_step(self):
        self.assertEqual(ddpm_posterior_variance(0, self.schedule), 0.0)

    def test_posterior_variance_is_bounded_by_beta(self):
        for t, beta in enumerate(self.schedule.betas):
            variance = ddpm_posterior_variance(t, self.schedule)
            self.assertGreaterEqual(variance, 0.0)
            self.assertLessEqual(variance, beta + 1e-15)

    def test_posterior_variance_rejects_invalid_timestep(self):
        with self.assertRaises(ValueError):
            ddpm_posterior_variance(-1, self.schedule)


class ScoreAndReverseTests(unittest.TestCase):
    def setUp(self):
        self.schedule = linear_beta_schedule(steps=20)

    def test_symmetric_mixture_has_zero_score_at_origin(self):
        score = gaussian_mixture_score((0.0, 0.0), 5, FIXTURE, self.schedule)
        self.assertAlmostEqual(score[0], 0.0, places=14)
        self.assertAlmostEqual(score[1], 0.0, places=14)

    def test_score_is_finite_and_points_toward_a_nearby_mode(self):
        score = gaussian_mixture_score((0.8, 0.2), 2, FIXTURE, self.schedule)
        self.assertTrue(all(math.isfinite(value) for value in score))
        self.assertGreater(score[0], 0.0)

    def test_score_rejects_non_two_dimensional_input(self):
        with self.assertRaisesRegex(ValueError, "two-dimensional"):
            gaussian_mixture_score((1.0,), 2, FIXTURE, self.schedule)

    def test_score_rejects_invalid_timestep(self):
        with self.assertRaises(ValueError):
            gaussian_mixture_score((0.0, 0.0), 20, FIXTURE, self.schedule)

    def test_epsilon_score_relation_is_applied(self):
        score = (0.4, -0.2)
        t = 5
        epsilon = epsilon_from_score(score, t, self.schedule)
        scale = -math.sqrt(1.0 - self.schedule.alpha_bars[t])
        self.assertEqual(epsilon, (scale * score[0], scale * score[1]))

    def test_reverse_step_at_t0_is_deterministic(self):
        noisy = (0.2, -0.3)
        epsilon = (0.1, -0.2)
        t = 0
        result = ddpm_reverse_step(noisy, epsilon, t, self.schedule)
        alpha_bar = self.schedule.alpha_bars[t]
        beta = self.schedule.betas[t]
        alpha = self.schedule.alphas[t]
        expected = tuple(
            (value - beta * eps / math.sqrt(1.0 - alpha_bar)) / math.sqrt(alpha)
            for value, eps in zip(noisy, epsilon)
        )
        self.assertEqual(result, expected)

    def test_reverse_step_rejects_noise_at_t0(self):
        with self.assertRaisesRegex(ValueError, "zero posterior variance"):
            ddpm_reverse_step((0.0, 0.0), (0.0, 0.0), 0, self.schedule, (1.0, 1.0))

    def test_reverse_step_requires_noise_when_t_is_positive(self):
        with self.assertRaisesRegex(ValueError, "noise is required"):
            ddpm_reverse_step((0.0, 0.0), (0.0, 0.0), 2, self.schedule)

    def test_reverse_step_rejects_noise_dimension_mismatch(self):
        with self.assertRaisesRegex(ValueError, "match the point dimension"):
            ddpm_reverse_step((0.0, 0.0), (0.0, 0.0), 2, self.schedule, (1.0,))


class SamplerAndCliTests(unittest.TestCase):
    def test_sampler_is_deterministic_for_fixed_seed(self):
        schedule = linear_beta_schedule(steps=16)
        first = sample_mixture(FIXTURE, schedule, count=5, seed=17)
        second = sample_mixture(FIXTURE, schedule, count=5, seed=17)
        self.assertEqual(first, second)

    def test_sampler_returns_requested_finite_points(self):
        schedule = linear_beta_schedule(steps=16)
        samples = sample_mixture(FIXTURE, schedule, count=7, seed=53)
        self.assertEqual(len(samples), 7)
        self.assertTrue(all(len(point) == 2 for point in samples))
        self.assertTrue(all(math.isfinite(value) for point in samples for value in point))

    def test_sampler_rejects_non_positive_count(self):
        with self.assertRaises(ValueError):
            sample_mixture(FIXTURE, linear_beta_schedule(steps=8), count=0)

    def test_nearest_center_counts_cover_each_sample(self):
        samples = ((-2.0, -2.0), (-2.0, 2.0), (2.0, -2.0), (2.0, 2.0))
        counts = nearest_component_counts(samples, FIXTURE)
        self.assertEqual(sum(counts.values()), 4)
        self.assertEqual(set(counts), {"southwest", "northwest", "southeast", "northeast"})
        self.assertEqual(set(counts.values()), {1})

    def test_demo_result_states_toy_boundaries(self):
        fixture, digest = load_fixture(DEFAULT_FIXTURE)
        result = run_demo(fixture, digest, DEFAULT_FIXTURE, steps=10, sample_count=4, seed=1)
        self.assertFalse(result["training_performed"])
        self.assertFalse(result["neural_model_loaded"])
        self.assertFalse(result["image_files_loaded"])
        self.assertTrue(result["analytic_score_used"])
        self.assertEqual(result["sampling"]["sample_count"], 4)

    def test_cli_audit_writes_fixture_hash_and_no_model_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "diffusion_lab.py"),
                    "--mode", "audit",
                    "--fixture", str(DEFAULT_FIXTURE),
                    "--output", directory,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            record = json.loads((Path(directory) / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(record["fixture"]["sha256"], FIXTURE_HASH)
        self.assertFalse(record["training_performed"])
        self.assertFalse(record["neural_model_loaded"])
        self.assertFalse(record["image_files_loaded"])

    def test_cli_demo_writes_reproducible_points(self):
        records = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as directory:
                subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "diffusion_lab.py"),
                        "--mode", "demo",
                        "--fixture", str(DEFAULT_FIXTURE),
                        "--output", directory,
                        "--steps", "12",
                        "--samples", "4",
                        "--seed", "53",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                records.append(json.loads((Path(directory) / "run.json").read_text(encoding="utf-8")))
        self.assertEqual(records[0]["samples"], records[1]["samples"])
        self.assertEqual(records[0]["status"], "analytic_synthetic_mixture_ddpm_demo_complete")
        self.assertFalse(records[0]["training_performed"])
        self.assertFalse(records[0]["model_downloaded"])


if __name__ == "__main__":
    unittest.main()
