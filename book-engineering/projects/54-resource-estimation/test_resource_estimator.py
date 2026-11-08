"""Unit tests for the arithmetic-only synthetic resource estimator."""
from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from resource_estimator import (
    DEFAULT_FIXTURE,
    EstimationInputError,
    byte_units,
    estimate_activation_reference,
    estimate_inference,
    estimate_inference_flops,
    estimate_kv_cache,
    estimate_training,
    estimate_training_flops,
    load_fixture,
    roofline_lower_bound_seconds,
    run_demo,
    validate_fixture,
)


ROOT = Path(__file__).resolve().parent
FIXTURE, FIXTURE_HASH = load_fixture(DEFAULT_FIXTURE)


def training_args(**overrides):
    values = {
        "model_parameters": 100,
        "trainable_parameters": 100,
        "weight_bytes_per_parameter": 2,
        "gradient_bytes_per_trainable_parameter": 4,
        "master_weight_bytes_per_trainable_parameter": 4,
        "optimizer_state_bytes_per_trainable_parameter": 8,
        "world_size": 1,
        "zero_stage": 0,
    }
    values.update(overrides)
    return values


class FixtureTests(unittest.TestCase):
    def test_fixture_loads_and_hash_is_sha256(self):
        fixture, digest = load_fixture(DEFAULT_FIXTURE)
        self.assertEqual(fixture["fixture_id"], "v4-ch08-synthetic-resource-profiles-v1")
        self.assertEqual(len(digest), 64)
        self.assertTrue(all(char in "0123456789abcdef" for char in digest))

    def test_fixture_is_explicitly_synthetic_and_unmeasured(self):
        validate_fixture(FIXTURE)
        self.assertEqual(FIXTURE["label_source"], "synthetic_fixture")
        self.assertFalse(FIXTURE["metadata"]["real_hardware_measurements_performed"])
        self.assertFalse(FIXTURE["metadata"]["training_performed"])
        self.assertEqual(len(FIXTURE["profiles"]), 4)

    def test_fixture_rejects_real_world_label(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["label_source"] = "measured_benchmark"
        with self.assertRaisesRegex(EstimationInputError, "synthetic_fixture"):
            validate_fixture(fixture)

    def test_fixture_requires_false_for_each_claim_boundary(self):
        for field in (
            "real_model_weights_included",
            "real_hardware_measurements_performed",
            "training_performed",
            "benchmark_performed",
        ):
            with self.subTest(field=field):
                fixture = copy.deepcopy(FIXTURE)
                fixture["metadata"][field] = True
                with self.assertRaisesRegex(EstimationInputError, field):
                    validate_fixture(fixture)

    def test_fixture_rejects_duplicate_profile_ids(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["profiles"][1]["profile_id"] = fixture["profiles"][0]["profile_id"]
        with self.assertRaisesRegex(EstimationInputError, "unique"):
            validate_fixture(fixture)

    def test_fixture_rejects_unknown_profile_kind(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["profiles"][0]["kind"] = "benchmark"
        with self.assertRaisesRegex(EstimationInputError, "inference or training"):
            validate_fixture(fixture)

    def test_fixture_rejects_trainable_count_larger_than_model(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["profiles"][1]["trainable_parameters"] += 1
        with self.assertRaisesRegex(EstimationInputError, "cannot exceed"):
            validate_fixture(fixture)

    def test_fixture_rejects_incomplete_cache_shape(self):
        fixture = copy.deepcopy(FIXTURE)
        del fixture["profiles"][0]["kv_cache"]["kv_heads"]
        with self.assertRaisesRegex(EstimationInputError, "missing a required field"):
            validate_fixture(fixture)

    def test_fixture_rejects_non_finite_activation_element_size(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["profiles"][1]["activation_model"]["bytes_per_element"] = math.nan
        with self.assertRaisesRegex(EstimationInputError, "finite number"):
            validate_fixture(fixture)


class UnitAndKVCacheTests(unittest.TestCase):
    def test_gib_and_decimal_gb_are_reported_separately(self):
        values = byte_units(1024**3)
        self.assertEqual(values["bytes"], 1024**3)
        self.assertEqual(values["binary_GiB"], 1.0)
        self.assertEqual(values["decimal_GB"], 1.073742)

    def test_kv_cache_formula_matches_hand_calculation(self):
        size = estimate_kv_cache(
            layers=32,
            active_sequences=4,
            context_tokens=8192,
            kv_heads=8,
            head_dim=128,
            bytes_per_element=2,
        )
        self.assertEqual(size, 4 * 1024**3)

    def test_kv_cache_scales_linearly_with_batch(self):
        one = estimate_kv_cache(layers=2, active_sequences=1, context_tokens=10, kv_heads=4, head_dim=8, bytes_per_element=2)
        three = estimate_kv_cache(layers=2, active_sequences=3, context_tokens=10, kv_heads=4, head_dim=8, bytes_per_element=2)
        self.assertEqual(three, 3 * one)

    def test_kv_cache_scales_linearly_with_context(self):
        short = estimate_kv_cache(layers=2, active_sequences=1, context_tokens=10, kv_heads=4, head_dim=8, bytes_per_element=2)
        long = estimate_kv_cache(layers=2, active_sequences=1, context_tokens=20, kv_heads=4, head_dim=8, bytes_per_element=2)
        self.assertEqual(long, 2 * short)

    def test_zero_active_sequences_produce_zero_cache(self):
        size = estimate_kv_cache(layers=2, active_sequences=0, context_tokens=512, kv_heads=4, head_dim=8, bytes_per_element=2)
        self.assertEqual(size, 0)

    def test_kv_cache_rejects_zero_layers(self):
        with self.assertRaisesRegex(EstimationInputError, "layers"):
            estimate_kv_cache(layers=0, active_sequences=1, context_tokens=1, kv_heads=1, head_dim=1, bytes_per_element=2)

    def test_kv_cache_rejects_boolean_dimension(self):
        with self.assertRaisesRegex(EstimationInputError, "kv_heads"):
            estimate_kv_cache(layers=1, active_sequences=1, context_tokens=1, kv_heads=True, head_dim=1, bytes_per_element=2)

    def test_kv_cache_rejects_non_positive_element_size(self):
        with self.assertRaisesRegex(EstimationInputError, "bytes_per_element"):
            estimate_kv_cache(layers=1, active_sequences=1, context_tokens=1, kv_heads=1, head_dim=1, bytes_per_element=0)


class ActivationTests(unittest.TestCase):
    def test_activation_reference_matches_declared_equivalents(self):
        size = estimate_activation_reference(
            microbatch=2,
            sequence_tokens=3,
            hidden_size=4,
            layers=5,
            saved_tensors_per_layer=6,
            bytes_per_element=2,
        )
        self.assertEqual(size, 1440)

    def test_activation_reference_can_be_zero_if_multiplier_is_zero(self):
        size = estimate_activation_reference(
            microbatch=1,
            sequence_tokens=1,
            hidden_size=1,
            layers=1,
            saved_tensors_per_layer=0,
            bytes_per_element=2,
        )
        self.assertEqual(size, 0)

    def test_activation_reference_rejects_zero_microbatch(self):
        with self.assertRaisesRegex(EstimationInputError, "microbatch"):
            estimate_activation_reference(microbatch=0, sequence_tokens=1, hidden_size=1, layers=1, saved_tensors_per_layer=1, bytes_per_element=2)

    def test_training_rejects_two_activation_sources(self):
        with self.assertRaisesRegex(EstimationInputError, "not both"):
            estimate_training(
                **training_args(),
                activation_model={"microbatch": 1, "sequence_tokens": 1, "hidden_size": 1, "layers": 1, "saved_tensors_per_layer": 1, "bytes_per_element": 2},
                activation_bytes_override=10,
            )


class InferenceTests(unittest.TestCase):
    def test_inference_components_sum(self):
        result = estimate_inference(
            model_parameters=7_000_000_000,
            weight_bytes_per_parameter=2,
            kv_cache_bytes=4 * 1024**3,
            runtime_and_temporary_bytes=100,
            safety_bytes=200,
        )
        self.assertEqual(result["model_weights"]["bytes"], 14_000_000_000)
        self.assertEqual(result["total_estimate"]["bytes"], 14_000_000_000 + 4 * 1024**3 + 300)

    def test_inference_rejects_boolean_parameter_count(self):
        with self.assertRaisesRegex(EstimationInputError, "model_parameters"):
            estimate_inference(model_parameters=True, weight_bytes_per_parameter=2)

    def test_inference_flops_include_batch_prompt_and_generation(self):
        value = estimate_inference_flops(
            model_parameters=2,
            prompt_tokens=4,
            generated_tokens=1,
            batch_size=2,
        )
        self.assertEqual(value, 40)

    def test_inference_flops_reject_negative_tokens(self):
        with self.assertRaisesRegex(EstimationInputError, "generated_tokens"):
            estimate_inference_flops(model_parameters=10, prompt_tokens=4, generated_tokens=-1)


class TrainingStateTests(unittest.TestCase):
    def test_explicit_full_training_states_sum_to_18_bytes_per_parameter(self):
        result = estimate_training(**training_args())
        states = result["model_states_per_rank"]
        self.assertEqual(states["subtotal"]["bytes"], 100 * (2 + 4 + 4 + 8))
        self.assertEqual(states["model_weights"]["bytes"], 200)
        self.assertEqual(states["trainable_gradients"]["bytes"], 400)
        self.assertEqual(states["trainable_master_weights"]["bytes"], 400)
        self.assertEqual(states["trainable_optimizer_states"]["bytes"], 800)

    def test_adapter_style_profile_keeps_all_base_weights_but_limits_trainable_states(self):
        result = estimate_training(
            **training_args(model_parameters=7_035_000_000, trainable_parameters=35_000_000)
        )
        states = result["model_states_per_rank"]
        self.assertEqual(states["model_weights"]["bytes"], 14_070_000_000)
        self.assertEqual(states["trainable_gradients"]["bytes"], 140_000_000)
        self.assertEqual(states["trainable_master_weights"]["bytes"], 140_000_000)
        self.assertEqual(states["trainable_optimizer_states"]["bytes"], 280_000_000)
        self.assertEqual(states["subtotal"]["bytes"], 14_630_000_000)

    def test_zero_stage_zero_replicates_all_states(self):
        result = estimate_training(**training_args(world_size=4, zero_stage=0))
        self.assertEqual(result["model_states_per_rank"]["subtotal"]["bytes"], 1800)
        self.assertEqual(result["idealized_sharding_divisors"], {"parameters": 1, "gradients": 1, "master_and_optimizer_states": 1})

    def test_zero_stage_one_partitions_master_and_optimizer(self):
        result = estimate_training(**training_args(world_size=4, zero_stage=1))
        self.assertEqual(result["model_states_per_rank"]["subtotal"]["bytes"], 900)
        self.assertEqual(result["idealized_sharding_divisors"], {"parameters": 1, "gradients": 1, "master_and_optimizer_states": 4})

    def test_zero_stage_two_also_partitions_gradients(self):
        result = estimate_training(**training_args(world_size=4, zero_stage=2))
        self.assertEqual(result["model_states_per_rank"]["subtotal"]["bytes"], 600)
        self.assertEqual(result["idealized_sharding_divisors"], {"parameters": 1, "gradients": 4, "master_and_optimizer_states": 4})

    def test_zero_stage_three_also_partitions_parameters(self):
        result = estimate_training(**training_args(world_size=4, zero_stage=3))
        self.assertEqual(result["model_states_per_rank"]["subtotal"]["bytes"], 450)
        self.assertEqual(result["idealized_sharding_divisors"], {"parameters": 4, "gradients": 4, "master_and_optimizer_states": 4})

    def test_world_size_one_does_not_change_ideal_state_bytes(self):
        baseline = estimate_training(**training_args(world_size=1, zero_stage=0))
        stage_three = estimate_training(**training_args(world_size=1, zero_stage=3))
        self.assertEqual(
            baseline["model_states_per_rank"]["subtotal"]["bytes"],
            stage_three["model_states_per_rank"]["subtotal"]["bytes"],
        )

    def test_activation_temporary_and_safety_are_separate_addends(self):
        model = {"microbatch": 1, "sequence_tokens": 2, "hidden_size": 3, "layers": 4, "saved_tensors_per_layer": 5, "bytes_per_element": 2}
        result = estimate_training(
            **training_args(model_parameters=1, trainable_parameters=1),
            activation_model=model,
            temporary_bytes=7,
            safety_bytes=11,
        )
        self.assertEqual(result["non_state_memory_per_rank"]["activation_reference"]["bytes"], 240)
        self.assertEqual(result["total_estimate_per_rank"]["bytes"], 18 + 240 + 7 + 11)

    def test_activation_zero_is_explicitly_a_placeholder_when_not_supplied(self):
        result = estimate_training(**training_args())
        self.assertEqual(result["non_state_memory_per_rank"]["activation_reference"]["bytes"], 0)
        self.assertEqual(result["non_state_memory_per_rank"]["activation_basis"]["kind"], "not_estimated")

    def test_training_rejects_trainable_count_larger_than_model(self):
        with self.assertRaisesRegex(EstimationInputError, "cannot exceed"):
            estimate_training(**training_args(model_parameters=10, trainable_parameters=11))

    def test_training_rejects_boolean_world_size(self):
        with self.assertRaisesRegex(EstimationInputError, "world_size"):
            estimate_training(**training_args(world_size=True))

    def test_training_rejects_invalid_stage(self):
        with self.assertRaisesRegex(EstimationInputError, "zero_stage"):
            estimate_training(**training_args(zero_stage=4))
        with self.assertRaisesRegex(EstimationInputError, "zero_stage"):
            estimate_training(**training_args(zero_stage=True))

    def test_training_rejects_infinite_byte_assumption(self):
        with self.assertRaisesRegex(EstimationInputError, "optimizer_state"):
            estimate_training(**training_args(optimizer_state_bytes_per_trainable_parameter=math.inf))


class ComputeAndDemoTests(unittest.TestCase):
    def test_training_flops_is_configured_k_times_n_times_d(self):
        self.assertEqual(estimate_training_flops(model_parameters=7, training_tokens=140, flops_per_parameter_token=6), 5880)

    def test_training_flops_reject_boolean_factor(self):
        with self.assertRaisesRegex(EstimationInputError, "flops_per_parameter_token"):
            estimate_training_flops(model_parameters=7, training_tokens=140, flops_per_parameter_token=True)

    def test_roofline_lower_bound_uses_larger_bottleneck_time(self):
        compute_bound = roofline_lower_bound_seconds(
            floating_point_operations=100,
            bytes_moved=100,
            effective_flops_per_second=10,
            effective_bytes_per_second=100,
        )
        self.assertEqual(compute_bound["lower_bound_seconds"], 10)
        memory_bound = roofline_lower_bound_seconds(
            floating_point_operations=100,
            bytes_moved=200,
            effective_flops_per_second=100,
            effective_bytes_per_second=10,
        )
        self.assertEqual(memory_bound["lower_bound_seconds"], 20)
        self.assertIn("lower bound only", memory_bound["warning"])

    def test_roofline_rejects_zero_rate(self):
        with self.assertRaisesRegex(EstimationInputError, "effective_bytes_per_second"):
            roofline_lower_bound_seconds(floating_point_operations=10, bytes_moved=10, effective_flops_per_second=1, effective_bytes_per_second=0)

    def test_demo_is_deterministic_and_preserves_fixture_hash(self):
        first = run_demo(DEFAULT_FIXTURE)
        second = run_demo(DEFAULT_FIXTURE)
        self.assertEqual(first, second)
        self.assertEqual(first["fixture"]["sha256"], FIXTURE_HASH)
        self.assertEqual(len(first["scenarios"]), 4)
        self.assertFalse(first["scope"]["real_hardware_measured"])

    def test_demo_contains_expected_inference_and_training_totals(self):
        result = run_demo(DEFAULT_FIXTURE)
        scenarios = {item["profile_id"]: item for item in result["scenarios"]}
        inference = scenarios["synthetic-gqa-inference"]["estimate"]["total_estimate"]["bytes"]
        self.assertEqual(inference, 14_070_000_000 + 4 * 1024**3)
        full = scenarios["synthetic-full-training"]["estimate"]
        self.assertEqual(full["model_states_per_rank"]["subtotal"]["bytes"], 126_630_000_000)
        self.assertEqual(full["non_state_memory_per_rank"]["activation_reference"]["bytes"], 4 * 1024**3)
        adapter = scenarios["synthetic-adapter-training"]["estimate"]
        self.assertEqual(adapter["model_states_per_rank"]["subtotal"]["bytes"], 14_630_000_000)

    def test_cli_writes_valid_json_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "nested" / "results.json"
            completed = subprocess.run(
                [sys.executable, str(ROOT / "resource_estimator.py"), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("arithmetic-only", completed.stdout)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["fixture"]["sha256"], FIXTURE_HASH)
            self.assertEqual(len(report["scenarios"]), 4)


if __name__ == "__main__":
    unittest.main()
