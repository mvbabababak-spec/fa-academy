import json
import tempfile
import unittest
from pathlib import Path

import torch
from torch.nn import functional as F

from peft_lab import (
    BottleneckAdapter,
    LoRALinear,
    audit_fixture,
    lora_parameter_count,
    quantized_payload_lower_bound,
    run_toy_demo,
    validate_fixture,
)

ROOT = Path(__file__).resolve().parent


class ParameterAccountingTests(unittest.TestCase):
    def test_lora_formula_for_rectangular_projection(self):
        self.assertEqual(lora_parameter_count(32, 64, 4), 384)

    def test_lora_rejects_invalid_dimensions_or_rank(self):
        for args in ((0, 4, 1), (4, 4, 0), (3, 5, 4)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                lora_parameter_count(*args)

    def test_four_bit_payload_is_only_packed_weight_lower_bound(self):
        self.assertEqual(quantized_payload_lower_bound(7_000_000_000, 4), 3_500_000_000)
        self.assertEqual(quantized_payload_lower_bound(3, 4), 2)
        with self.assertRaises(ValueError):
            quantized_payload_lower_bound(-1, 4)

    def test_fixture_audit_is_validation_only(self):
        result = audit_fixture(ROOT / "sample_layers.json")
        self.assertEqual(result["status"], "validated_only")
        self.assertFalse(result["training_performed"])
        self.assertFalse(result["model_loaded"])
        self.assertFalse(result["model_downloaded"])
        self.assertEqual(len(result["layers"]), 3)
        self.assertIn("lower bound only", result["memory_note"])

    def test_duplicate_or_inconsistent_fixture_is_rejected(self):
        rows = json.loads((ROOT / "sample_layers.json").read_text(encoding="utf-8"))
        rows[1]["name"] = rows[0]["name"]
        with self.assertRaises(ValueError):
            validate_fixture(rows)
        rows[1]["name"] = "new"
        rows[1]["weight_bits"] = 3
        with self.assertRaises(ValueError):
            validate_fixture(rows)


class LoRALinearTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(4801)

    def test_zero_initialized_update_preserves_frozen_base(self):
        layer = LoRALinear(8, 6, rank=2, alpha=4, bias=True)
        x = torch.randn(5, 8)
        self.assertTrue(torch.equal(layer(x), layer.base(x)))
        self.assertFalse(layer.base.weight.requires_grad)
        self.assertFalse(layer.base.bias.requires_grad)
        self.assertTrue(layer.lora_A.requires_grad)
        self.assertTrue(layer.lora_B.requires_grad)

    def test_trainable_parameter_count_matches_formula(self):
        layer = LoRALinear(32, 64, rank=4, alpha=8, bias=True)
        self.assertEqual(layer.trainable_parameter_count(), 4 * (32 + 64))

    def test_initial_gradient_reaches_zero_initialized_b_factor(self):
        layer = LoRALinear(4, 3, rank=2, alpha=2, bias=False)
        x = torch.randn(7, 4)
        layer(x).sum().backward()
        self.assertIsNotNone(layer.lora_B.grad)
        self.assertGreater(float(layer.lora_B.grad.abs().sum()), 0.0)
        self.assertIsNotNone(layer.lora_A.grad)
        self.assertEqual(float(layer.lora_A.grad.abs().sum()), 0.0)

    def test_merge_matches_unmerged_eval(self):
        layer = LoRALinear(7, 5, rank=2, alpha=3, bias=True, dropout=0.2)
        with torch.no_grad():
            layer.lora_B.normal_(0, 0.1)
        layer.eval()
        x = torch.randn(9, 7)
        self.assertTrue(torch.allclose(layer(x), layer.merged_layer()(x), atol=1e-6, rtol=1e-6))

    def test_rank_stabilized_scaling_is_explicit_option(self):
        standard = LoRALinear(8, 6, rank=4, alpha=8)
        stabilized = LoRALinear(8, 6, rank=4, alpha=8, rank_stabilized=True)
        self.assertEqual(standard.scaling, 2.0)
        self.assertEqual(stabilized.scaling, 4.0)

    def test_invalid_hyperparameters_are_rejected(self):
        for kwargs in (
            {"in_features": 8, "out_features": 6, "rank": 2, "alpha": 0},
            {"in_features": 8, "out_features": 6, "rank": 2, "alpha": 2, "dropout": 1.0},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                LoRALinear(**kwargs)


class BottleneckAdapterTests(unittest.TestCase):
    def test_zero_up_projection_starts_as_residual_identity(self):
        adapter = BottleneckAdapter(hidden_size=12, bottleneck_size=3)
        x = torch.randn(4, 12)
        self.assertTrue(torch.equal(adapter(x), x))

    def test_adapter_shape_and_gradient(self):
        adapter = BottleneckAdapter(hidden_size=12, bottleneck_size=3)
        x = torch.randn(4, 12, requires_grad=True)
        loss = adapter(x).square().mean()
        loss.backward()
        self.assertEqual(tuple(adapter(x.detach()).shape), (4, 12))
        self.assertIsNotNone(adapter.up.weight.grad)

    def test_toy_demo_improves_only_its_synthetic_objective(self):
        result = run_toy_demo(steps=500, seed=48)
        self.assertEqual(result["status"], "synthetic_demo_completed")
        self.assertFalse(result["model_loaded"])
        self.assertFalse(result["model_downloaded"])
        self.assertFalse(result["base_parameters_trainable"])
        self.assertEqual(result["lora_trainable_parameters"], 2 * (16 + 12))
        self.assertLess(result["final_mse"], result["initial_mse"])
        self.assertLess(result["merge_max_abs_error"], 1e-5)


if __name__ == "__main__":
    unittest.main()
