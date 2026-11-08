"""Tests for sinusoidal positions, RoPE, residuals and LayerNorm variants."""
import unittest

import torch

from transformer_block import (
    PositionAwareTransformerBlock,
    apply_rope,
    sinusoidal_encoding,
)


class PositionAndBlockTests(unittest.TestCase):
    def test_sinusoidal_encoding_even_odd_and_position_zero(self):
        even = sinusoidal_encoding(4, 6)
        odd = sinusoidal_encoding(4, 5)
        self.assertEqual(tuple(even.shape), (4, 6))
        self.assertEqual(tuple(odd.shape), (4, 5))
        torch.testing.assert_close(even[0, 0::2], torch.zeros(3))
        torch.testing.assert_close(even[0, 1::2], torch.ones(3))
        torch.testing.assert_close(odd[0, 0::2], torch.zeros(3))
        torch.testing.assert_close(odd[0, 1::2], torch.ones(2))
        self.assertFalse(torch.equal(even[0], even[1]))

    def test_sinusoidal_encoding_respects_explicit_absolute_offsets(self):
        positions = torch.arange(10, 14)
        shifted = sinusoidal_encoding(4, 8, positions=positions)
        ordinary = sinusoidal_encoding(4, 8)
        self.assertFalse(torch.allclose(shifted, ordinary))
        self.assertTrue(torch.isfinite(shifted).all().item())

    def test_rope_preserves_query_and_key_norms(self):
        torch.manual_seed(3602)
        values = torch.randn(2, 3, 7, 8, dtype=torch.float64)
        rotated = apply_rope(values)
        self.assertEqual(tuple(rotated.shape), tuple(values.shape))
        torch.testing.assert_close(
            torch.linalg.vector_norm(rotated, dim=-1),
            torch.linalg.vector_norm(values, dim=-1),
            atol=1e-12,
            rtol=1e-12,
        )

    def test_rope_dot_product_depends_on_relative_not_absolute_offset(self):
        base_q = torch.tensor([0.4, -1.1, 0.7, 0.2], dtype=torch.float64)
        base_k = torch.tensor([-0.3, 0.8, 1.2, -0.5], dtype=torch.float64)
        q = base_q.view(1, 1, 1, 4).expand(1, 1, 6, 4).clone()
        k = base_k.view(1, 1, 1, 4).expand(1, 1, 6, 4).clone()
        q_rot = apply_rope(q)
        k_rot = apply_rope(k)
        offset_two_a = (q_rot[:, :, 0] * k_rot[:, :, 2]).sum(dim=-1)
        offset_two_b = (q_rot[:, :, 3] * k_rot[:, :, 5]).sum(dim=-1)
        torch.testing.assert_close(offset_two_a, offset_two_b, atol=1e-12, rtol=1e-12)

    def test_block_shapes_for_sinusoidal_and_rope_modes(self):
        torch.manual_seed(3603)
        x = torch.randn(2, 5, 12)
        positions = torch.arange(5)
        for mode in ("sinusoidal", "rope"):
            block = PositionAwareTransformerBlock(
                d_model=12, num_heads=3, d_ff=24, position_mode=mode
            ).eval()
            with torch.no_grad():
                output = block(x, positions)
            self.assertEqual(tuple(output.shape), tuple(x.shape))
            self.assertTrue(torch.isfinite(output).all().item())

    def test_pre_and_post_layernorm_layouts_preserve_shape(self):
        torch.manual_seed(3604)
        x = torch.randn(2, 4, 8)
        for order in ("pre", "post"):
            block = PositionAwareTransformerBlock(
                d_model=8, num_heads=2, position_mode="sinusoidal", norm_order=order
            )
            output = block(x)
            self.assertEqual(tuple(output.shape), tuple(x.shape))
            self.assertTrue(torch.isfinite(output).all().item())

    def test_residual_block_has_finite_input_and_parameter_gradients(self):
        torch.manual_seed(3605)
        block = PositionAwareTransformerBlock(
            d_model=8, num_heads=2, d_ff=16, position_mode="rope"
        ).double()
        x = torch.randn(2, 5, 8, dtype=torch.float64, requires_grad=True)
        block(x).square().mean().backward()
        self.assertIsNotNone(x.grad)
        self.assertTrue(torch.isfinite(x.grad).all().item())
        for parameter in block.parameters():
            self.assertIsNotNone(parameter.grad)
            self.assertTrue(torch.isfinite(parameter.grad).all().item())

    def test_rope_requires_even_head_dimension(self):
        with self.assertRaisesRegex(ValueError, "even head_dim"):
            PositionAwareTransformerBlock(d_model=6, num_heads=2, position_mode="rope")
        values = torch.randn(1, 2, 4, 3)
        with self.assertRaisesRegex(ValueError, "even"):
            apply_rope(values)

    def test_rejects_invalid_inputs_and_positions(self):
        block = PositionAwareTransformerBlock(d_model=8, num_heads=2)
        with self.assertRaisesRegex(ValueError, "batch, sequence"):
            block(torch.ones(2, 8))
        with self.assertRaisesRegex(ValueError, "feature dimension"):
            block(torch.ones(1, 4, 6))
        with self.assertRaisesRegex(TypeError, "floating-point"):
            block(torch.ones(1, 4, 8, dtype=torch.long))
        with self.assertRaisesRegex(ValueError, "sequence length"):
            block(torch.ones(1, 0, 8))
        with self.assertRaisesRegex(ValueError, "one value per token"):
            sinusoidal_encoding(4, 8, positions=torch.arange(3))
        with self.assertRaisesRegex(ValueError, "non-negative"):
            apply_rope(torch.randn(1, 2, 3, 4), positions=torch.tensor([0, -1, 2]))

    def test_rejects_invalid_configuration(self):
        with self.assertRaisesRegex(ValueError, "divisible"):
            PositionAwareTransformerBlock(d_model=7, num_heads=2)
        with self.assertRaisesRegex(ValueError, "positive"):
            PositionAwareTransformerBlock(d_model=8, num_heads=2, d_ff=0)
        with self.assertRaisesRegex(ValueError, "position_mode"):
            PositionAwareTransformerBlock(d_model=8, num_heads=2, position_mode="learned")
        with self.assertRaisesRegex(ValueError, "norm_order"):
            PositionAwareTransformerBlock(d_model=8, num_heads=2, norm_order="middle")
        with self.assertRaisesRegex(TypeError, "integer"):
            sinusoidal_encoding(4, 8.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
