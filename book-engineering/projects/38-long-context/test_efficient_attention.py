import math
import unittest

import torch

from efficient_attention import (
    KVCache,
    SwitchTop1MoE,
    causal_allowed_mask,
    estimate_kv_cache_bytes,
    grouped_query_attention,
    local_causal_allowed_mask,
    switch_top1_load_balance_loss,
)


class AttentionMaskTests(unittest.TestCase):
    def test_causal_mask_uses_true_for_allowed_and_blocks_future(self):
        mask = causal_allowed_mask(4, 4)
        expected = torch.tensor([
            [True, False, False, False],
            [True, True, False, False],
            [True, True, True, False],
            [True, True, True, True],
        ])
        self.assertTrue(torch.equal(mask, expected))

    def test_cached_query_defaults_to_the_last_key_position(self):
        mask = causal_allowed_mask(1, 5)
        self.assertTrue(torch.equal(mask, torch.ones((1, 5), dtype=torch.bool)))

    def test_local_causal_window_keeps_only_recent_keys(self):
        mask = local_causal_allowed_mask(4, 4, window_size=2)
        expected = torch.tensor([
            [True, False, False, False],
            [True, True, False, False],
            [False, True, True, False],
            [False, False, True, True],
        ])
        self.assertTrue(torch.equal(mask, expected))

    def test_local_mask_can_address_a_cached_suffix(self):
        mask = local_causal_allowed_mask(2, 5, window_size=2)
        expected = torch.tensor([
            [False, False, True, True, False],
            [False, False, False, True, True],
        ])
        self.assertTrue(torch.equal(mask, expected))

    def test_invalid_offsets_lengths_and_window_are_rejected(self):
        for call in (
            lambda: causal_allowed_mask(0, 4),
            lambda: causal_allowed_mask(2, 4, query_offset=3),
            lambda: causal_allowed_mask(2, 4, query_offset=-1),
            lambda: local_causal_allowed_mask(2, 4, window_size=0),
        ):
            with self.subTest(call=call), self.assertRaises(ValueError):
                call()


class GroupedQueryAttentionTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(38)
        self.query = torch.randn(2, 8, 5, 16)
        self.key = torch.randn(2, 2, 5, 16)
        self.value = torch.randn(2, 2, 5, 16)

    def test_gqa_matches_explicit_kv_head_repetition(self):
        output, probabilities = grouped_query_attention(
            self.query, self.key, self.value, causal=False
        )
        repeat = self.query.shape[1] // self.key.shape[1]
        expanded_key = self.key.repeat_interleave(repeat, dim=1)
        expanded_value = self.value.repeat_interleave(repeat, dim=1)
        scores = self.query @ expanded_key.transpose(-2, -1) / math.sqrt(self.query.shape[-1])
        expected_probabilities = torch.softmax(scores, dim=-1)
        expected_output = expected_probabilities @ expanded_value
        torch.testing.assert_close(output, expected_output)
        torch.testing.assert_close(probabilities, expected_probabilities)

    def test_gqa_shape_and_probability_rows(self):
        output, probabilities = grouped_query_attention(
            self.query, self.key, self.value, causal=True
        )
        self.assertEqual(tuple(output.shape), (2, 8, 5, 16))
        self.assertEqual(tuple(probabilities.shape), (2, 8, 5, 5))
        torch.testing.assert_close(
            probabilities.sum(dim=-1), torch.ones((2, 8, 5)), atol=1e-6, rtol=1e-6
        )
        self.assertTrue(torch.isfinite(output).all())

    def test_one_kv_head_is_valid_mqa(self):
        key = self.key[:, :1]
        value = self.value[:, :1]
        output, _ = grouped_query_attention(self.query, key, value, causal=True)
        self.assertEqual(tuple(output.shape), tuple(self.query.shape))
        self.assertTrue(torch.isfinite(output).all())

    def test_equal_query_and_kv_heads_cover_mha_case(self):
        q = torch.randn(1, 4, 3, 8)
        k = torch.randn(1, 4, 3, 8)
        v = torch.randn(1, 4, 3, 8)
        output, _ = grouped_query_attention(q, k, v, causal=True)
        scores = q @ k.transpose(-2, -1) / math.sqrt(8)
        allowed = causal_allowed_mask(3, 3)
        probabilities = torch.softmax(scores.masked_fill(~allowed, torch.finfo(scores.dtype).min), dim=-1)
        torch.testing.assert_close(output, probabilities @ v)

    def test_causal_attention_does_not_read_future_values(self):
        q = torch.randn(1, 4, 4, 8)
        k = torch.randn(1, 2, 4, 8)
        v1 = torch.randn(1, 2, 4, 8)
        v2 = v1.clone()
        v2[:, :, 3] += 100
        out1, _ = grouped_query_attention(q, k, v1, causal=True)
        out2, _ = grouped_query_attention(q, k, v2, causal=True)
        torch.testing.assert_close(out1[:, :, :3], out2[:, :, :3])

    def test_local_attention_respects_window(self):
        q = torch.randn(1, 4, 4, 8)
        k = torch.randn(1, 2, 4, 8)
        v = torch.randn(1, 2, 4, 8)
        out, probs = grouped_query_attention(q, k, v, causal=True, local_window=2)
        self.assertTrue(torch.equal(probs[:, :, 3, :2], torch.zeros_like(probs[:, :, 3, :2])))
        self.assertTrue(torch.isfinite(out).all())

    def test_batch_specific_allowed_mask_is_supported(self):
        mask = torch.ones((2, 5, 5), dtype=torch.bool)
        mask[0, :, 4] = False
        output, probabilities = grouped_query_attention(
            self.query, self.key, self.value, allowed_mask=mask
        )
        self.assertTrue(torch.equal(probabilities[0, :, :, 4], torch.zeros_like(probabilities[0, :, :, 4])))
        self.assertTrue(torch.isfinite(output).all())

    def test_every_query_must_have_an_allowed_key(self):
        mask = torch.zeros((5, 5), dtype=torch.bool)
        with self.assertRaises(ValueError):
            grouped_query_attention(self.query, self.key, self.value, allowed_mask=mask)

    def test_invalid_shapes_head_ratio_and_mask_are_rejected(self):
        with self.assertRaises(ValueError):
            grouped_query_attention(self.query, self.key[:, :, :, :8], self.value)
        with self.assertRaises(ValueError):
            grouped_query_attention(self.query[:, :7], self.key, self.value)
        with self.assertRaises(ValueError):
            grouped_query_attention(self.query, self.key, self.value, allowed_mask=torch.ones(4, 5, dtype=torch.bool))
        with self.assertRaises(ValueError):
            grouped_query_attention(self.query, self.key, self.value, local_window=2)


class KVCacheTests(unittest.TestCase):
    def test_appends_new_tokens_in_order(self):
        cache = KVCache()
        key = torch.arange(12, dtype=torch.float32).reshape(1, 2, 3, 2)
        value = -key
        key_1, value_1 = cache.append(key[:, :, :2], value[:, :, :2])
        key_2, value_2 = cache.append(key[:, :, 2:], value[:, :, 2:])
        self.assertEqual(cache.num_tokens, 3)
        torch.testing.assert_close(key_1, key[:, :, :2])
        torch.testing.assert_close(value_1, value[:, :, :2])
        torch.testing.assert_close(key_2, key)
        torch.testing.assert_close(value_2, value)

    def test_empty_cache_get_is_rejected(self):
        with self.assertRaises(ValueError):
            KVCache().get()

    def test_incremental_cached_decode_matches_full_causal_attention(self):
        torch.manual_seed(39)
        q = torch.randn(1, 8, 6, 8)
        k = torch.randn(1, 2, 6, 8)
        v = torch.randn(1, 2, 6, 8)
        full, _ = grouped_query_attention(q, k, v, causal=True)
        cache = KVCache()
        steps = []
        for position in range(q.shape[2]):
            cached_k, cached_v = cache.append(
                k[:, :, position:position + 1], v[:, :, position:position + 1]
            )
            step, _ = grouped_query_attention(
                q[:, :, position:position + 1], cached_k, cached_v, causal=True
            )
            steps.append(step)
        incremental = torch.cat(steps, dim=2)
        torch.testing.assert_close(incremental, full, atol=1e-6, rtol=1e-6)

    def test_incompatible_cache_chunk_is_rejected(self):
        cache = KVCache()
        cache.append(torch.zeros(1, 2, 1, 4), torch.zeros(1, 2, 1, 4))
        with self.assertRaises(ValueError):
            cache.append(torch.zeros(1, 3, 1, 4), torch.zeros(1, 3, 1, 4))
        with self.assertRaises(ValueError):
            KVCache().append(torch.zeros(1, 2, 1, 4), torch.zeros(1, 2, 0, 4))


class CacheBudgetTests(unittest.TestCase):
    def test_bf16_32k_example_is_four_gib_for_eight_kv_heads(self):
        result = estimate_kv_cache_bytes(
            num_layers=32, batch_size=1, sequence_length=32768,
            num_kv_heads=8, head_dim=128, bytes_per_element=2,
        )
        self.assertEqual(result, 4 * 1024**3)

    def test_kv_cache_size_scales_with_head_count_and_batch(self):
        common = dict(
            num_layers=32, batch_size=1, sequence_length=32768,
            head_dim=128, bytes_per_element=2,
        )
        mha = estimate_kv_cache_bytes(num_kv_heads=32, **common)
        gqa = estimate_kv_cache_bytes(num_kv_heads=8, **common)
        mqa = estimate_kv_cache_bytes(num_kv_heads=1, **common)
        doubled = estimate_kv_cache_bytes(num_kv_heads=8, **{**common, "batch_size": 2})
        self.assertEqual(mha, 4 * gqa)
        self.assertEqual(gqa, 8 * mqa)
        self.assertEqual(doubled, 2 * gqa)

    def test_invalid_cache_budget_dimensions_are_rejected(self):
        with self.assertRaises(ValueError):
            estimate_kv_cache_bytes(
                num_layers=32, batch_size=0, sequence_length=10,
                num_kv_heads=2, head_dim=8,
            )
        with self.assertRaises(ValueError):
            estimate_kv_cache_bytes(
                num_layers=True, batch_size=1, sequence_length=10,
                num_kv_heads=2, head_dim=8,
            )


class SwitchTop1MoETests(unittest.TestCase):
    def test_balanced_and_collapsed_router_losses(self):
        balanced_probabilities = torch.full((4, 2), 0.5)
        balanced_choices = torch.tensor([0, 0, 1, 1], dtype=torch.long)
        balanced_loss = switch_top1_load_balance_loss(
            balanced_probabilities, balanced_choices, alpha=1.0
        )
        self.assertAlmostEqual(float(balanced_loss), 1.0, places=6)

        collapsed_probabilities = torch.tensor([[0.9, 0.1]] * 4)
        collapsed_choices = torch.zeros(4, dtype=torch.long)
        collapsed_loss = switch_top1_load_balance_loss(
            collapsed_probabilities, collapsed_choices, alpha=1.0
        )
        self.assertAlmostEqual(float(collapsed_loss), 1.8, places=6)

    def test_moe_shapes_finiteness_and_gradients(self):
        torch.manual_seed(40)
        model = SwitchTop1MoE(d_model=8, hidden_dim=16, num_experts=4)
        x = torch.randn(2, 3, 8, requires_grad=True)
        output, aux_loss, selected = model(x)
        self.assertEqual(tuple(output.shape), (2, 3, 8))
        self.assertEqual(tuple(selected.shape), (2, 3))
        self.assertTrue(torch.isfinite(output).all())
        self.assertTrue(torch.isfinite(aux_loss))
        (output.square().mean() + aux_loss).backward()
        self.assertIsNotNone(x.grad)
        self.assertIsNotNone(model.router.weight.grad)

    def test_only_selected_expert_processes_tokens(self):
        torch.manual_seed(41)
        model = SwitchTop1MoE(d_model=4, hidden_dim=8, num_experts=3)
        with torch.no_grad():
            model.router.weight.zero_()
            model.router.bias.copy_(torch.tensor([8.0, -8.0, -8.0]))
        output, _, selected = model(torch.randn(2, 3, 4))
        self.assertTrue(torch.equal(selected, torch.zeros_like(selected)))
        output.sum().backward()
        self.assertIsNotNone(model.experts[0][0].weight.grad)
        self.assertIsNone(model.experts[1][0].weight.grad)
        self.assertIsNone(model.experts[2][0].weight.grad)

    def test_invalid_router_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            switch_top1_load_balance_loss(torch.ones(2, 2), torch.tensor([0, 2]))
        with self.assertRaises(ValueError):
            switch_top1_load_balance_loss(torch.tensor([[0.2, 0.2]]), torch.tensor([0]))
        model = SwitchTop1MoE(d_model=4, hidden_dim=8, num_experts=2)
        with self.assertRaises(ValueError):
            model(torch.ones(2, 4, dtype=torch.long))
        with self.assertRaises(ValueError):
            model(torch.ones(2, 5))


if __name__ == "__main__":
    unittest.main()
