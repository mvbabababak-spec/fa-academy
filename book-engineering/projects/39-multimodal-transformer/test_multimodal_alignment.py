"""Shape, mask, loss and gradient tests for the multimodal alignment demo."""
from __future__ import annotations

import unittest

import torch

from multimodal_alignment import (
    AudioFrameEncoder,
    TextTokenEncoder,
    TinyMultimodalAligner,
    VisionPatchEncoder,
    symmetric_info_nce,
    three_way_contrastive_loss,
)


class VisionPatchEncoderTests(unittest.TestCase):
    def test_non_square_image_becomes_expected_patch_sequence(self) -> None:
        encoder = VisionPatchEncoder(32, 4, patch_size=8, max_patches=24)
        tokens = encoder(torch.rand(2, 3, 32, 48))
        self.assertEqual(tuple(tokens.shape), (2, 24, 32))
        self.assertTrue(torch.isfinite(tokens).all())

    def test_rejects_non_divisible_image_size(self) -> None:
        encoder = VisionPatchEncoder(32, 4, patch_size=8)
        with self.assertRaises(ValueError):
            encoder(torch.rand(2, 3, 31, 32))

    def test_rejects_patch_count_above_position_table(self) -> None:
        encoder = VisionPatchEncoder(32, 4, patch_size=8, max_patches=3)
        with self.assertRaises(ValueError):
            encoder(torch.rand(1, 3, 16, 16))


class TextTokenEncoderTests(unittest.TestCase):
    def test_padding_mask_is_true_for_padding_and_padded_outputs_are_zero(self) -> None:
        encoder = TextTokenEncoder(32, 32, 4, pad_id=0, max_length=8)
        ids = torch.tensor([[1, 5, 6, 0], [1, 7, 0, 0]], dtype=torch.long)
        tokens, mask = encoder(ids)
        self.assertEqual(tuple(tokens.shape), (2, 4, 32))
        self.assertEqual(mask.tolist(), [[False, False, False, True], [False, False, True, True]])
        self.assertTrue(torch.equal(tokens[mask], torch.zeros_like(tokens[mask])))

    def test_rejects_all_padding_row_and_wrong_mask_dtype(self) -> None:
        encoder = TextTokenEncoder(16, 16, 4, max_length=8)
        with self.assertRaises(ValueError):
            encoder(torch.zeros(1, 3, dtype=torch.long))
        with self.assertRaises(ValueError):
            encoder(torch.tensor([[1, 2]]), torch.zeros(1, 2, dtype=torch.long))

    def test_rejects_token_outside_vocabulary(self) -> None:
        encoder = TextTokenEncoder(8, 16, 4)
        with self.assertRaises(ValueError):
            encoder(torch.tensor([[1, 8]], dtype=torch.long))


class AudioFrameEncoderTests(unittest.TestCase):
    def test_length_mask_counts_valid_patches(self) -> None:
        encoder = AudioFrameEncoder(16, 32, 4, frame_stride=4, max_audio_tokens=16)
        features = torch.randn(3, 16, 32)
        tokens, mask = encoder(features, torch.tensor([32, 24, 12], dtype=torch.long))
        self.assertEqual(tuple(tokens.shape), (3, 8, 32))
        self.assertEqual((~mask).sum(dim=1).tolist(), [8, 6, 3])
        self.assertTrue(torch.equal(tokens[mask], torch.zeros_like(tokens[mask])))

    def test_rejects_invalid_lengths(self) -> None:
        encoder = AudioFrameEncoder(16, 32, 4, frame_stride=4)
        with self.assertRaises(ValueError):
            encoder(torch.randn(2, 16, 16), torch.tensor([16, 0], dtype=torch.long))


class ContrastiveLossTests(unittest.TestCase):
    def test_aligned_pairs_outscore_a_permutation(self) -> None:
        vectors = torch.eye(4)
        aligned = symmetric_info_nce(vectors, vectors, logit_scale=8.0)
        permuted = symmetric_info_nce(vectors, vectors.roll(1, dims=0), logit_scale=8.0)
        self.assertLess(aligned.item(), permuted.item())

    def test_rejects_single_example_and_mismatched_shapes(self) -> None:
        with self.assertRaises(ValueError):
            symmetric_info_nce(torch.ones(1, 4), torch.ones(1, 4))
        with self.assertRaises(ValueError):
            symmetric_info_nce(torch.ones(2, 4), torch.ones(2, 5))
        with self.assertRaises(ValueError):
            symmetric_info_nce(torch.ones(2, 4), torch.ones(2, 4), logit_scale=True)

    def test_three_way_loss_is_scalar_and_finite(self) -> None:
        a, b, c = torch.randn(3, 8), torch.randn(3, 8), torch.randn(3, 8)
        loss = three_way_contrastive_loss(a, b, c)
        self.assertEqual(loss.ndim, 0)
        self.assertTrue(torch.isfinite(loss))


class TinyMultimodalAlignerTests(unittest.TestCase):
    def _inputs(self):
        images = torch.rand(3, 3, 32, 32)
        ids = torch.tensor([[1, 5, 6, 0], [1, 7, 0, 0], [1, 8, 9, 10]], dtype=torch.long)
        audio = torch.randn(3, 16, 32)
        lengths = torch.tensor([32, 24, 16], dtype=torch.long)
        return images, ids, audio, lengths

    def test_three_encoders_shared_embeddings_and_cross_attention_shapes(self) -> None:
        model = TinyMultimodalAligner(d_model=32, embed_dim=12, num_heads=4)
        images, ids, audio, lengths = self._inputs()
        out = model(images, ids, audio, audio_lengths=lengths)
        for name in ("image_embedding", "text_embedding", "audio_embedding", "fused_embedding"):
            embedding = out[name]
            self.assertEqual(tuple(embedding.shape), (3, 12))
            self.assertTrue(torch.allclose(embedding.norm(dim=-1), torch.ones(3), atol=1e-5))
        self.assertEqual(tuple(out["fused_text_tokens"].shape), (3, 4, 32))
        self.assertTrue(torch.equal(out["fused_text_tokens"][out["text_padding_mask"]], torch.zeros_like(out["fused_text_tokens"][out["text_padding_mask"]])))

    def test_all_three_encoder_branches_receive_finite_gradients(self) -> None:
        torch.manual_seed(19)
        model = TinyMultimodalAligner(d_model=32, embed_dim=12, num_heads=4)
        images, ids, audio, lengths = self._inputs()
        out = model(images, ids, audio, audio_lengths=lengths)
        loss = three_way_contrastive_loss(
            out["image_embedding"], out["text_embedding"], out["audio_embedding"]
        ) + symmetric_info_nce(out["fused_embedding"], out["text_embedding"])
        loss.backward()
        parameters = (
            model.vision.patch_projection.weight,
            model.text.embedding.weight,
            model.audio.frame_projection.weight,
            model.fusion.image_attention.in_proj_weight,
            model.fusion.audio_attention.in_proj_weight,
        )
        for parameter in parameters:
            self.assertIsNotNone(parameter.grad)
            self.assertTrue(torch.isfinite(parameter.grad).all())

    def test_rejects_mismatched_modality_batch_sizes(self) -> None:
        model = TinyMultimodalAligner(d_model=32, embed_dim=12, num_heads=4)
        images, ids, audio, _ = self._inputs()
        with self.assertRaises(ValueError):
            model(images, ids[:2], audio)
        with self.assertRaises(ValueError):
            model(None, ids, audio)

    def test_rejects_invalid_hidden_width_configuration(self) -> None:
        with self.assertRaises(ValueError):
            TinyMultimodalAligner(d_model=30, embed_dim=12, num_heads=4)


if __name__ == "__main__":
    unittest.main()
