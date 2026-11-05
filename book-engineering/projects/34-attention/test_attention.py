"""Tests for the explicit attention implementation in attention.py."""
import unittest

import torch
import torch.nn.functional as F

from attention import scaled_dot_product_attention


class ScaledDotProductAttentionTests(unittest.TestCase):
    def test_hand_computed_example(self):
        q = torch.tensor([[[1.0, 0.0]]], dtype=torch.float64)
        k = torch.tensor([[[1.0, 0.0], [0.0, 1.0]]], dtype=torch.float64)
        v = torch.tensor([[[10.0, 0.0], [0.0, 10.0]]], dtype=torch.float64)

        output, weights = scaled_dot_product_attention(q, k, v)
        expected_weights = torch.tensor([[[0.6697615493, 0.3302384507]]], dtype=torch.float64)
        expected_output = torch.tensor([[[6.697615493, 3.302384507]]], dtype=torch.float64)
        torch.testing.assert_close(weights, expected_weights, atol=1e-9, rtol=1e-9)
        torch.testing.assert_close(output, expected_output, atol=1e-8, rtol=1e-9)

    def test_batch_and_different_query_key_lengths(self):
        torch.manual_seed(3401)
        q = torch.randn(2, 3, 4, dtype=torch.float64)
        k = torch.randn(2, 5, 4, dtype=torch.float64)
        v = torch.randn(2, 5, 7, dtype=torch.float64)

        output, weights = scaled_dot_product_attention(q, k, v)
        self.assertEqual(tuple(weights.shape), (2, 3, 5))
        self.assertEqual(tuple(output.shape), (2, 3, 7))
        torch.testing.assert_close(
            weights.sum(dim=-1), torch.ones(2, 3, dtype=torch.float64)
        )
        torch.testing.assert_close(output, weights @ v)

    def test_matches_pytorch_scaled_dot_product_attention(self):
        torch.manual_seed(34)
        q = torch.randn(2, 4, 6, dtype=torch.float64)
        k = torch.randn(2, 7, 6, dtype=torch.float64)
        v = torch.randn(2, 7, 5, dtype=torch.float64)

        actual, _ = scaled_dot_product_attention(q, k, v)
        reference = F.scaled_dot_product_attention(
            q, k, v, dropout_p=0.0, is_causal=False
        )
        torch.testing.assert_close(actual, reference, atol=1e-12, rtol=1e-12)

    def test_gradients_are_finite(self):
        torch.manual_seed(35)
        q = torch.randn(2, 3, 4, dtype=torch.float64, requires_grad=True)
        k = torch.randn(2, 5, 4, dtype=torch.float64, requires_grad=True)
        v = torch.randn(2, 5, 6, dtype=torch.float64, requires_grad=True)

        output, _ = scaled_dot_product_attention(q, k, v)
        output.square().mean().backward()
        for tensor in (q, k, v):
            self.assertIsNotNone(tensor.grad)
            self.assertTrue(torch.isfinite(tensor.grad).all().item())

    def test_softmax_remains_finite_for_large_finite_scores(self):
        q = torch.tensor([[[1000.0, 0.0]]], dtype=torch.float64)
        k = torch.tensor([[[1000.0, 0.0], [0.0, 1000.0]]], dtype=torch.float64)
        v = torch.tensor([[[1.0], [3.0]]], dtype=torch.float64)

        output, weights = scaled_dot_product_attention(q, k, v)
        self.assertTrue(torch.isfinite(weights).all().item())
        self.assertTrue(torch.isfinite(output).all().item())
        torch.testing.assert_close(weights.sum(dim=-1), torch.ones(1, 1, dtype=torch.float64))

    def test_rejects_rank_other_than_three(self):
        with self.assertRaisesRegex(ValueError, "rank-3"):
            scaled_dot_product_attention(torch.ones(2, 4), torch.ones(2, 4), torch.ones(2, 5))

    def test_rejects_incompatible_shapes(self):
        q = torch.ones(1, 2, 3)
        with self.assertRaisesRegex(ValueError, "feature dimensions"):
            scaled_dot_product_attention(q, torch.ones(1, 4, 2), torch.ones(1, 4, 5))
        with self.assertRaisesRegex(ValueError, "sequence lengths"):
            scaled_dot_product_attention(q, torch.ones(1, 4, 3), torch.ones(1, 5, 6))
        with self.assertRaisesRegex(ValueError, "batch dimensions"):
            scaled_dot_product_attention(q, torch.ones(2, 4, 3), torch.ones(2, 4, 6))

    def test_rejects_non_floating_input(self):
        with self.assertRaisesRegex(TypeError, "floating-point"):
            scaled_dot_product_attention(
                torch.ones(1, 1, 2, dtype=torch.long),
                torch.ones(1, 2, 2, dtype=torch.long),
                torch.ones(1, 2, 3, dtype=torch.long),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
