"""Tests for causal multi-head self-attention in causal_multihead.py."""
import unittest

import torch
import torch.nn.functional as F

from causal_multihead import CausalMultiHeadSelfAttention


class CausalMultiHeadSelfAttentionTests(unittest.TestCase):
    def test_batch_shapes_and_normalized_causal_weights(self):
        torch.manual_seed(3501)
        model = CausalMultiHeadSelfAttention(d_model=8, num_heads=2)
        x = torch.randn(3, 5, 8)

        output, weights = model(x)
        self.assertEqual(tuple(output.shape), (3, 5, 8))
        self.assertEqual(tuple(weights.shape), (3, 2, 5, 5))
        torch.testing.assert_close(weights.sum(dim=-1), torch.ones_like(weights.sum(dim=-1)))
        self.assertEqual(weights.triu(diagonal=1).abs().max().item(), 0.0)

    def test_future_input_change_cannot_change_earlier_outputs(self):
        torch.manual_seed(3502)
        model = CausalMultiHeadSelfAttention(d_model=8, num_heads=2).double().eval()
        x = torch.randn(2, 6, 8, dtype=torch.float64)
        changed = x.clone()
        cut = 3
        changed[:, cut:, :] += 1000.0

        with torch.no_grad():
            original_output, _ = model(x)
            changed_output, _ = model(changed)
        torch.testing.assert_close(original_output[:, :cut], changed_output[:, :cut], atol=1e-12, rtol=1e-12)

    def test_future_input_change_cannot_change_earlier_weights(self):
        torch.manual_seed(3503)
        model = CausalMultiHeadSelfAttention(d_model=8, num_heads=4).double().eval()
        x = torch.randn(1, 6, 8, dtype=torch.float64)
        changed = x.clone()
        cut = 4
        changed[:, cut:, :] -= 500.0

        with torch.no_grad():
            _, original_weights = model(x)
            _, changed_weights = model(changed)
        torch.testing.assert_close(
            original_weights[:, :, :cut, :], changed_weights[:, :, :cut, :],
            atol=1e-12, rtol=1e-12,
        )

    def test_current_position_can_affect_its_output(self):
        torch.manual_seed(3504)
        model = CausalMultiHeadSelfAttention(d_model=8, num_heads=2).double().eval()
        x = torch.randn(1, 5, 8, dtype=torch.float64)
        changed = x.clone()
        changed[:, 2, :] += 0.75

        with torch.no_grad():
            original_output, _ = model(x)
            changed_output, _ = model(changed)
        self.assertFalse(torch.allclose(original_output[:, 2], changed_output[:, 2]))

    def test_manual_causal_mask_matches_pytorch_is_causal(self):
        torch.manual_seed(3505)
        q = torch.randn(2, 3, 5, 4, dtype=torch.float64)
        k = torch.randn(2, 3, 5, 4, dtype=torch.float64)
        v = torch.randn(2, 3, 5, 6, dtype=torch.float64)
        allowed = torch.ones(5, 5, dtype=torch.bool).tril()
        scores = q @ k.transpose(-2, -1) / (4 ** 0.5)
        weights = torch.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
        manual = weights @ v

        reference = F.scaled_dot_product_attention(
            q, k, v, dropout_p=0.0, is_causal=True
        )
        torch.testing.assert_close(manual, reference, atol=1e-12, rtol=1e-12)

    def test_functional_boolean_mask_true_means_allowed(self):
        torch.manual_seed(3506)
        q = torch.randn(1, 2, 4, 3, dtype=torch.float64)
        k = torch.randn(1, 2, 4, 3, dtype=torch.float64)
        v = torch.randn(1, 2, 4, 5, dtype=torch.float64)
        allowed = torch.ones(4, 4, dtype=torch.bool).tril()

        with_bool_mask = F.scaled_dot_product_attention(
            q, k, v, attn_mask=allowed, dropout_p=0.0, is_causal=False
        )
        with_causal_flag = F.scaled_dot_product_attention(
            q, k, v, dropout_p=0.0, is_causal=True
        )
        torch.testing.assert_close(with_bool_mask, with_causal_flag, atol=1e-12, rtol=1e-12)

    def test_rejects_invalid_model_dimensions(self):
        with self.assertRaisesRegex(ValueError, "divisible"):
            CausalMultiHeadSelfAttention(d_model=7, num_heads=2)
        with self.assertRaisesRegex(ValueError, "positive"):
            CausalMultiHeadSelfAttention(d_model=0, num_heads=1)
        with self.assertRaisesRegex(TypeError, "integer"):
            CausalMultiHeadSelfAttention(d_model=8.0, num_heads=2)

    def test_rejects_invalid_inputs(self):
        model = CausalMultiHeadSelfAttention(d_model=8, num_heads=2)
        with self.assertRaisesRegex(ValueError, "batch, sequence"):
            model(torch.ones(2, 8))
        with self.assertRaisesRegex(ValueError, "feature dimension"):
            model(torch.ones(1, 4, 6))
        with self.assertRaisesRegex(TypeError, "floating-point"):
            model(torch.ones(1, 4, 8, dtype=torch.long))
        with self.assertRaisesRegex(ValueError, "sequence length"):
            model(torch.ones(1, 0, 8))

    def test_gradients_are_finite(self):
        torch.manual_seed(3507)
        model = CausalMultiHeadSelfAttention(d_model=8, num_heads=2).double()
        x = torch.randn(2, 5, 8, dtype=torch.float64, requires_grad=True)
        output, _ = model(x)
        output.square().mean().backward()
        self.assertIsNotNone(x.grad)
        self.assertTrue(torch.isfinite(x.grad).all().item())
        for parameter in model.parameters():
            self.assertIsNotNone(parameter.grad)
            self.assertTrue(torch.isfinite(parameter.grad).all().item())

    def test_single_token_sequence(self):
        model = CausalMultiHeadSelfAttention(d_model=4, num_heads=2)
        output, weights = model(torch.randn(1, 1, 4))
        self.assertEqual(tuple(output.shape), (1, 1, 4))
        self.assertEqual(tuple(weights.shape), (1, 2, 1, 1))
        torch.testing.assert_close(weights, torch.ones_like(weights))


if __name__ == "__main__":
    unittest.main(verbosity=2)
