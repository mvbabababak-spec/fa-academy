import unittest

import torch

from transformer_architectures import (
    BidirectionalEncoder,
    DecoderOnlyLanguageModel,
    EncoderDecoderTransformer,
    EncoderOnlyClassifier,
    causal_mask,
    make_padding_mask,
    shift_right,
)


class TransformerArchitectureTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(17)
        self.small = dict(
            vocab_size=24, d_model=16, num_heads=4, ff_dim=32,
            num_layers=1, max_len=12, pad_id=0,
        )

    def test_padding_mask_marks_only_padding_ids(self):
        ids = torch.tensor([[4, 5, 0], [0, 7, 8]], dtype=torch.long)
        expected = torch.tensor([[False, False, True], [True, False, False]])
        self.assertTrue(torch.equal(make_padding_mask(ids, pad_id=0), expected))

    def test_causal_mask_blocks_future_and_keeps_present(self):
        mask = causal_mask(4)
        expected = torch.tensor([
            [False, True, True, True],
            [False, False, True, True],
            [False, False, False, True],
            [False, False, False, False],
        ])
        self.assertTrue(torch.equal(mask, expected))

    def test_shift_right_aligns_bos_and_previous_target(self):
        target = torch.tensor([[8, 9, 2], [4, 5, 2]], dtype=torch.long)
        expected = torch.tensor([[1, 8, 9], [1, 4, 5]], dtype=torch.long)
        self.assertTrue(torch.equal(shift_right(target, bos_id=1), expected))

    def test_encoder_returns_context_for_every_source_position(self):
        model = BidirectionalEncoder(**self.small).eval()
        source = torch.tensor([[1, 3, 4, 0]], dtype=torch.long)
        hidden = model(source)
        self.assertEqual(tuple(hidden.shape), (1, 4, 16))
        self.assertTrue(torch.isfinite(hidden).all())

    def test_encoder_can_use_right_context(self):
        model = BidirectionalEncoder(**self.small).eval()
        source_a = torch.tensor([[1, 3, 4, 5]], dtype=torch.long)
        source_b = source_a.clone()
        source_b[0, 3] = 9
        hidden_a = model(source_a)
        hidden_b = model(source_b)
        self.assertFalse(torch.allclose(hidden_a[:, 0], hidden_b[:, 0], atol=1e-7, rtol=1e-7))

    def test_encoder_classifier_emits_class_logits(self):
        model = EncoderOnlyClassifier(num_classes=3, **self.small)
        ids = torch.tensor([[1, 4, 5, 0], [1, 7, 0, 0]], dtype=torch.long)
        logits = model(ids)
        self.assertEqual(tuple(logits.shape), (2, 3))
        self.assertTrue(torch.isfinite(logits).all())

    def test_decoder_only_predicts_one_vocabulary_distribution_per_position(self):
        model = DecoderOnlyLanguageModel(**self.small)
        ids = torch.tensor([[1, 4, 5, 0], [1, 6, 0, 0]], dtype=torch.long)
        logits = model(ids)
        self.assertEqual(tuple(logits.shape), (2, 4, self.small["vocab_size"]))
        self.assertTrue(torch.isfinite(logits).all())

    def test_decoder_cannot_leak_changed_future_token_to_earlier_logits(self):
        model = DecoderOnlyLanguageModel(**self.small).eval()
        tokens_a = torch.tensor([[1, 4, 5, 6, 7]], dtype=torch.long)
        tokens_b = tokens_a.clone()
        tokens_b[0, 4] = 11
        logits_a = model(tokens_a)
        logits_b = model(tokens_b)
        self.assertTrue(torch.allclose(logits_a[:, :4], logits_b[:, :4], atol=1e-6, rtol=1e-6))

    def test_encoder_decoder_handles_different_source_and_target_lengths(self):
        model = EncoderDecoderTransformer(**self.small)
        source = torch.tensor([[1, 3, 4, 0], [1, 5, 0, 0]], dtype=torch.long)
        target_input = torch.tensor([[1, 7, 8], [1, 9, 0]], dtype=torch.long)
        logits = model(source, target_input)
        self.assertEqual(tuple(logits.shape), (2, 3, self.small["vocab_size"]))
        self.assertTrue(torch.isfinite(logits).all())

    def test_seq2seq_loss_has_gradient_path_to_source_memory(self):
        model = EncoderDecoderTransformer(**self.small)
        source = torch.tensor([[3, 4, 5]], dtype=torch.long)
        target_input = torch.tensor([[1, 7]], dtype=torch.long)
        logits = model(source, target_input)
        logits[0, -1, 8].backward()
        grad = model.source_embedding.token.weight.grad[3]
        self.assertGreater(float(grad.norm()), 0.0)

    def test_invalid_token_shape_and_out_of_range_id_are_rejected(self):
        model = DecoderOnlyLanguageModel(**self.small)
        with self.assertRaises(ValueError):
            model(torch.tensor([1, 2, 3], dtype=torch.long))
        with self.assertRaises(ValueError):
            model(torch.tensor([[1, 24]], dtype=torch.long))

    def test_invalid_padding_mask_is_rejected(self):
        model = BidirectionalEncoder(**self.small)
        source = torch.tensor([[1, 2, 3]], dtype=torch.long)
        bad_mask = torch.tensor([[0, 0, 1]], dtype=torch.long)
        with self.assertRaises(ValueError):
            model(source, bad_mask)

    def test_invalid_dimensions_and_position_length_are_rejected(self):
        with self.assertRaises(ValueError):
            DecoderOnlyLanguageModel(vocab_size=24, d_model=15, num_heads=4)
        model = DecoderOnlyLanguageModel(**self.small)
        with self.assertRaises(ValueError):
            model(torch.ones((1, 13), dtype=torch.long))


if __name__ == "__main__":
    unittest.main()
