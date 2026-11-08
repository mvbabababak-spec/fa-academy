import json
import tempfile
import unittest
from pathlib import Path

import torch

from vision_lab import (
    SOURCE,
    audit_fixture,
    image_text_logits,
    load_fixture,
    normalize_embeddings,
    patch_grid,
    patchify,
    retrieval_metrics,
    symmetric_contrastive_loss,
    unpatchify,
    validate_fixture,
    vit_token_budget,
)

FIXTURE = Path(__file__).with_name("sample_embeddings.json")


class PatchContractTests(unittest.TestCase):
    def test_patch_grid_for_224_patch16(self):
        self.assertEqual(patch_grid(224, 224, 16), (14, 14))

    def test_patch_token_budget_includes_class_token(self):
        result = vit_token_budget(224, 224, 16)
        self.assertEqual(result["patch_tokens"], 196)
        self.assertEqual(result["sequence_tokens"], 197)
        self.assertEqual(result["attention_pairs_per_head"], 197**2)

    def test_doubling_both_image_dimensions_scales_patch_pairs_approximately_sixteenfold(self):
        small = vit_token_budget(224, 224, 16, include_class_token=False)
        large = vit_token_budget(448, 448, 16, include_class_token=False)
        self.assertEqual(large["patch_tokens"], 4 * small["patch_tokens"])
        self.assertEqual(large["attention_pairs_per_head"], 16 * small["attention_pairs_per_head"])

    def test_grid_rejects_implicit_padding(self):
        with self.assertRaisesRegex(ValueError, "divisible"):
            patch_grid(225, 224, 16)

    def test_grid_rejects_zero_boolean_and_wrong_types(self):
        for args in ((0, 16, 16), (16, 16, 0), (True, 16, 16), (16.0, 16, 16)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                patch_grid(*args)

    def test_patchify_has_row_major_patches(self):
        image = torch.arange(1 * 4 * 4, dtype=torch.float32).reshape(1, 4, 4)
        patches = patchify(image, 2)
        self.assertEqual(tuple(patches.shape), (4, 4))
        self.assertTrue(torch.equal(patches[0], torch.tensor([0.0, 1.0, 4.0, 5.0])))
        self.assertTrue(torch.equal(patches[-1], torch.tensor([10.0, 11.0, 14.0, 15.0])))

    def test_unpatchify_reconstructs_tiny_input_exactly(self):
        image = torch.arange(3 * 8 * 8, dtype=torch.float32).reshape(3, 8, 8)
        patches = patchify(image, 4)
        self.assertTrue(torch.equal(unpatchify(patches, (2, 2), 3, 4), image))

    def test_patchify_rejects_bad_shape_and_patch_size(self):
        with self.assertRaisesRegex(ValueError, "shape"):
            patchify(torch.zeros(8, 8), 4)
        with self.assertRaisesRegex(ValueError, "divisible"):
            patchify(torch.zeros(1, 5, 8), 4)

    def test_unpatchify_rejects_incompatible_shape(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            unpatchify(torch.zeros(3, 16), (2, 2), 1, 4)


class AlignmentObjectiveTests(unittest.TestCase):
    def setUp(self):
        self.images = torch.tensor([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]], dtype=torch.float32)
        self.texts = torch.tensor([[0.9, 0.1], [0.1, 0.9], [-0.9, 0.1]], dtype=torch.float32)

    def test_normalize_returns_unit_vectors(self):
        result = normalize_embeddings(torch.tensor([[3.0, 4.0]]))
        self.assertTrue(torch.allclose(torch.linalg.vector_norm(result, dim=-1), torch.ones(1)))

    def test_normalize_rejects_zero_vectors_and_nonfinite_values(self):
        for bad in (torch.zeros(1, 2), torch.tensor([[float("nan"), 1.0]])):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                normalize_embeddings(bad)

    def test_logits_put_matching_synthetic_pairs_on_the_diagonal(self):
        logits = image_text_logits(self.images, self.texts, temperature=0.1)
        self.assertEqual(tuple(logits.shape), (3, 3))
        self.assertTrue(torch.all(logits.diagonal() > logits[0, 1:].max()))

    def test_logits_reject_bad_temperature_or_dimensions(self):
        with self.assertRaisesRegex(ValueError, "temperature"):
            image_text_logits(self.images, self.texts, temperature=0)
        with self.assertRaisesRegex(ValueError, "same dimension"):
            image_text_logits(self.images, torch.ones(3, 4))

    def test_symmetric_loss_has_finite_gradient(self):
        images = self.images.clone().requires_grad_(True)
        loss = symmetric_contrastive_loss(images, self.texts, temperature=0.1)
        loss.backward()
        self.assertTrue(torch.isfinite(loss))
        self.assertTrue(torch.isfinite(images.grad).all())

    def test_correct_pair_order_has_lower_loss_than_a_permuted_order(self):
        correct = symmetric_contrastive_loss(self.images, self.texts, temperature=0.1)
        wrong = symmetric_contrastive_loss(self.images, self.texts[[1, 2, 0]], temperature=0.1)
        self.assertLess(correct.item(), wrong.item())

    def test_diagonal_loss_rejects_single_pair_without_in_batch_negatives(self):
        with self.assertRaisesRegex(ValueError, "at least two pairs"):
            symmetric_contrastive_loss(self.images[:1], self.texts[:1])

    def test_diagonal_loss_rejects_unequal_batch_sizes(self):
        with self.assertRaisesRegex(ValueError, "equal"):
            symmetric_contrastive_loss(self.images, self.texts[:2])


class RetrievalMetricTests(unittest.TestCase):
    def test_fixture_retrieval_is_exact_in_both_directions(self):
        payload, _ = load_fixture(FIXTURE)
        images = torch.tensor([row["embedding"] for row in payload["images"]], dtype=torch.float32)
        texts = torch.tensor([row["embedding"] for row in payload["texts"]], dtype=torch.float32)
        image_groups = [row["group_id"] for row in payload["images"]]
        text_groups = [row["group_id"] for row in payload["texts"]]
        i2t = retrieval_metrics(images, texts, image_groups, text_groups)
        t2i = retrieval_metrics(texts, images, text_groups, image_groups)
        self.assertEqual(i2t["recall_at_k"]["1"], 1.0)
        self.assertEqual(t2i["recall_at_k"]["1"], 1.0)
        self.assertEqual(i2t["mean_reciprocal_rank"], 1.0)

    def test_retrieval_metrics_allow_multiple_relevant_candidates_per_group(self):
        queries = torch.tensor([[0.0, 1.0]])
        candidates = torch.tensor([[0.0, 1.0], [0.9, 0.1], [0.8, 0.2]])
        metrics = retrieval_metrics(queries, candidates, ["positive"], ["negative", "positive", "positive"], ks=(1, 2))
        self.assertEqual(metrics["ranks"], [2])
        self.assertEqual(metrics["recall_at_k"], {"1": 0.0, "2": 1.0})

    def test_retrieval_rejects_query_without_matching_candidate(self):
        with self.assertRaisesRegex(ValueError, "no matching candidate"):
            retrieval_metrics(torch.tensor([[1.0, 0.0]]), torch.tensor([[0.0, 1.0]]), ["missing"], ["other"])

    def test_retrieval_rejects_mismatched_id_counts_and_invalid_k(self):
        q, c = torch.tensor([[1.0, 0.0]]), torch.tensor([[1.0, 0.0]])
        with self.assertRaisesRegex(ValueError, "counts"):
            retrieval_metrics(q, c, [], ["g"])
        with self.assertRaisesRegex(ValueError, "positive integers"):
            retrieval_metrics(q, c, ["g"], ["g"], ks=(0,))


class FixtureContractTests(unittest.TestCase):
    def test_fixture_has_four_synthetic_pairs_and_four_groups(self):
        payload, source = load_fixture(FIXTURE)
        self.assertEqual(validate_fixture(payload), (4, 4, 8))
        self.assertEqual(len(source) > 0, True)

    def test_audit_records_exact_hash_and_no_model_or_training(self):
        payload, source = load_fixture(FIXTURE)
        report = audit_fixture(payload, source)
        self.assertEqual(report["status"], "synthetic_image_text_fixture_audit_complete")
        self.assertEqual(report["label_source"], SOURCE)
        self.assertFalse(report["training_performed"])
        self.assertFalse(report["pretrained_model_loaded"])
        self.assertFalse(report["image_files_loaded"])
        self.assertEqual(report["sha256"], "aba309bb1b3e69443802190b988a21e0432109c01b777f4f58fe11f992936522")

    def test_loader_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "valid UTF-8 JSON"):
                load_fixture(path)

    def test_fixture_rejects_duplicate_ids_wrong_source_and_group_mismatch(self):
        payload, _ = load_fixture(FIXTURE)
        duplicate = json.loads(json.dumps(payload))
        duplicate["images"][1]["id"] = duplicate["images"][0]["id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_fixture(duplicate)
        wrong_source = json.loads(json.dumps(payload))
        wrong_source["texts"][0]["label_source"] = "human"
        with self.assertRaisesRegex(ValueError, "synthetic fixture"):
            validate_fixture(wrong_source)
        mismatched = json.loads(json.dumps(payload))
        mismatched["texts"][0]["group_id"] = "unknown"
        with self.assertRaisesRegex(ValueError, "match exactly"):
            validate_fixture(mismatched)

    def test_demo_reports_only_fixture_results(self):
        payload, _ = load_fixture(FIXTURE)
        from vision_lab import run_demo
        report = run_demo(payload)
        self.assertEqual(report["status"], "synthetic_patch_and_embedding_smoke_test")
        self.assertFalse(report["training_performed"])
        self.assertFalse(report["pretrained_model_loaded"])
        self.assertTrue(report["patch_fixture"]["reconstruction_exact"])
        self.assertEqual(report["image_to_text_retrieval"]["recall_at_k"]["1"], 1.0)
        self.assertIn("not a ViT forward pass", report["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
