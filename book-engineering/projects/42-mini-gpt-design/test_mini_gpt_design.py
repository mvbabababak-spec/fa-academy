import unittest
from dataclasses import replace

import torch

from mini_gpt_design import (
    ModelConfig,
    build_model,
    context_sweep,
    count_parameters,
    estimate_budget,
    parameter_breakdown,
)


class MiniGPTDesignTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(42)
        self.config = ModelConfig()

    def test_parameter_formula_matches_reused_chapter_37_model(self):
        model = build_model(self.config)
        breakdown = parameter_breakdown(self.config)
        self.assertEqual(breakdown["total"], 117350)
        self.assertEqual(count_parameters(model), breakdown["total"])

    def test_forward_has_batch_sequence_vocabulary_shape(self):
        model = build_model(self.config).eval()
        token_ids = torch.randint(0, self.config.vocab_size, (2, 17), dtype=torch.long)
        token_ids[:, 0] = (self.config.pad_id + 1) % self.config.vocab_size
        with torch.no_grad():
            logits = model(token_ids)
        self.assertEqual(tuple(logits.shape), (2, 17, self.config.vocab_size))
        self.assertTrue(torch.isfinite(logits).all())

    def test_prefix_guard_rejects_left_and_all_padding_but_allows_right_padding(self):
        model = build_model(self.config).eval()
        with self.assertRaisesRegex(ValueError, "non-padding prefix"):
            model(torch.tensor([[self.config.pad_id, 7, 8]], dtype=torch.long))
        with self.assertRaisesRegex(ValueError, "non-padding prefix"):
            model(torch.full((1, 4), self.config.pad_id, dtype=torch.long))
        valid_ids = torch.tensor([[1, 7, 8]], dtype=torch.long)
        masked_prefix = torch.tensor([[True, False, False]], dtype=torch.bool)
        with self.assertRaisesRegex(ValueError, "first prefix token"):
            model(valid_ids, padding_mask=masked_prefix)
        right_padded_ids = torch.tensor([[1, 7, self.config.pad_id, self.config.pad_id]], dtype=torch.long)
        with torch.no_grad():
            logits = model(right_padded_ids)
        self.assertEqual(tuple(logits.shape), (1, 4, self.config.vocab_size))
        self.assertTrue(torch.isfinite(logits).all())

    def test_future_change_cannot_change_earlier_logits(self):
        model = build_model(self.config).eval()
        tokens_a = torch.tensor([[1, 7, 8, 9, 10, 11]], dtype=torch.long)
        tokens_b = tokens_a.clone()
        tokens_b[0, 5] = 31
        with torch.no_grad():
            logits_a = model(tokens_a)
            logits_b = model(tokens_b)
        self.assertTrue(torch.allclose(logits_a[:, :5], logits_b[:, :5], atol=1e-6, rtol=1e-6))

    def test_doubling_context_adds_only_the_expected_position_rows_to_params(self):
        short = replace(self.config, block_size=32)
        long = replace(self.config, block_size=64)
        self.assertEqual(
            parameter_breakdown(long)["total"] - parameter_breakdown(short)["total"],
            (64 - 32) * self.config.d_model,
        )

    def test_attention_score_equivalent_size_is_quadratic_in_sequence_length(self):
        config = replace(self.config, block_size=128)
        at_64 = estimate_budget(config, batch_size=16, sequence_length=64)
        at_128 = estimate_budget(config, batch_size=16, sequence_length=128)
        self.assertEqual(at_128["attention_score_equivalent_bytes"], 4 * at_64["attention_score_equivalent_bytes"])
        self.assertEqual(at_128["ffn_hidden_bytes"], 2 * at_64["ffn_hidden_bytes"])
        self.assertEqual(at_128["logits_bytes"], 2 * at_64["logits_bytes"])

    def test_fp32_adamw_persistent_estimate_counts_parameters_gradients_and_two_moments(self):
        result = estimate_budget(self.config, batch_size=16, sequence_length=64)
        params = result["parameter_count"]
        self.assertEqual(result["parameter_bytes"], params * 4)
        self.assertEqual(result["gradient_bytes"], params * 4)
        self.assertEqual(result["adamw_state_bytes"], params * 8)
        self.assertEqual(result["persistent_bytes"], params * 16)

    def test_context_sweep_reports_exactly_three_contexts_and_budget_directions(self):
        rows = context_sweep(self.config)
        self.assertEqual([row["context_length"] for row in rows], [32, 64, 128])
        self.assertEqual([row["parameter_count"] for row in rows], [115302, 117350, 121446])
        self.assertLess(rows[0]["attention_score_equivalent_bytes"], rows[1]["attention_score_equivalent_bytes"])
        self.assertLess(rows[1]["attention_score_equivalent_bytes"], rows[2]["attention_score_equivalent_bytes"])
        self.assertTrue(all("not peak memory" in row["assumptions"]["activation_note"] for row in rows))

    def test_invalid_model_dimensions_are_rejected(self):
        with self.assertRaises(ValueError):
            replace(self.config, d_model=63).validate()
        with self.assertRaises(ValueError):
            replace(self.config, block_size=0).validate()
        with self.assertRaises(ValueError):
            replace(self.config, pad_id=self.config.vocab_size).validate()

    def test_invalid_budget_shape_or_byte_width_is_rejected(self):
        with self.assertRaises(ValueError):
            estimate_budget(self.config, batch_size=0, sequence_length=64)
        with self.assertRaises(ValueError):
            estimate_budget(self.config, batch_size=1, sequence_length=65)
        with self.assertRaises(ValueError):
            estimate_budget(self.config, batch_size=1, sequence_length=16, activation_bytes=0)

    def test_context_sweep_rejects_empty_and_duplicate_lengths(self):
        with self.assertRaises(ValueError):
            context_sweep(self.config, ())
        with self.assertRaises(ValueError):
            context_sweep(self.config, (32, 32))


if __name__ == "__main__":
    unittest.main()
