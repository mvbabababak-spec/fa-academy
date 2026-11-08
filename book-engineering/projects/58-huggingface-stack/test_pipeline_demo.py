"""Unit and integration tests for the offline chapter 58 pipeline."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import torch
from transformers import DataCollatorWithPadding

import pipeline_demo as demo


class FixtureTests(unittest.TestCase):
    def test_checked_in_fixture_matches_manifest_and_grouped_splits(self):
        rows, manifest, digest = demo.load_fixture()
        self.assertEqual(digest, "eb21fe6a41dcd4dc828c00a7dc0293370087bb77fc6df022078fc16a20d750a2")
        self.assertEqual(manifest["fixture_id"], "v4-ch12-synthetic-text-pipeline-v1")
        splits = demo.split_records(rows)
        self.assertEqual([len(splits[name]) for name in ("train", "validation")], [8, 4])
        train_groups = {row["group_id"] for row in splits["train"]}
        validation_groups = {row["group_id"] for row in splits["validation"]}
        self.assertFalse(train_groups & validation_groups)

    def test_hash_mismatch_is_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / "changed.jsonl"
            fixture.write_bytes(demo.DEFAULT_FIXTURE.read_bytes() + b" ")
            with self.assertRaisesRegex(demo.PipelineInputError, "sha256"):
                demo.load_fixture(fixture, demo.DEFAULT_MANIFEST)

    def test_group_leakage_is_rejected_even_when_record_count_is_unchanged(self):
        rows, manifest, _ = demo.load_fixture()
        changed = copy.deepcopy(rows)
        changed[0]["split"] = "validation"
        fixture_bytes = ("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in changed)).encode("utf-8")
        changed_manifest = copy.deepcopy(manifest)
        changed_manifest["sha256"] = hashlib.sha256(fixture_bytes).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / "leaky.jsonl"
            manifest_path = root / "manifest.json"
            fixture.write_bytes(fixture_bytes)
            manifest_path.write_text(json.dumps(changed_manifest, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(demo.PipelineInputError, "cross splits"):
                demo.load_fixture(fixture, manifest_path)

    def test_boolean_is_not_accepted_as_an_integer_label(self):
        rows, manifest, _ = demo.load_fixture()
        changed = copy.deepcopy(rows)
        changed[0]["label"] = True
        fixture_bytes = ("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in changed)).encode("utf-8")
        changed_manifest = copy.deepcopy(manifest)
        changed_manifest["sha256"] = hashlib.sha256(fixture_bytes).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / "bad-label.jsonl"
            manifest_path = root / "manifest.json"
            fixture.write_bytes(fixture_bytes)
            manifest_path.write_text(json.dumps(changed_manifest, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(demo.PipelineInputError, "integer 0 or 1"):
                demo.load_fixture(fixture, manifest_path)


class HuggingFaceComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.manifest, _ = demo.load_fixture()
        cls.splits = demo.split_records(cls.rows)
        cls.tokenizer = demo.train_fast_tokenizer(cls.splits["train"])

    def test_datasets_features_and_split_sizes(self):
        dataset_dict = demo.build_datasets(self.rows)
        self.assertEqual(set(dataset_dict.keys()), {"train", "validation"})
        self.assertEqual([len(dataset_dict[name]) for name in ("train", "validation")], [8, 4])
        self.assertEqual(dataset_dict["train"].features["label"].dtype, "int64")
        self.assertEqual(dataset_dict["validation"].features["text"].dtype, "string")

    def test_tokenizer_special_ids_and_training_split_boundary(self):
        result = self.tokenizer("نمونهٔ ساختگی الف", truncation=True, max_length=demo.MAX_LENGTH)
        self.assertEqual(result["input_ids"][0], self.tokenizer.cls_token_id)
        self.assertEqual(result["input_ids"][-1], self.tokenizer.sep_token_id)
        self.assertEqual(self.tokenizer.pad_token_id, 0)
        train_ids = {row["example_id"] for row in self.splits["train"]}
        validation_ids = {row["example_id"] for row in self.splits["validation"]}
        self.assertFalse(train_ids & validation_ids)
        self.assertEqual(set(demo.SPECIAL_TOKENS), set(self.tokenizer.all_special_tokens))

    def test_map_drops_raw_text_and_metadata_columns(self):
        raw = demo.build_datasets(self.rows)
        encoded = demo.tokenize_splits(raw, self.tokenizer)
        self.assertEqual(set(encoded["train"].column_names), {"label", "input_ids", "attention_mask"})
        self.assertEqual(set(encoded["validation"].column_names), {"label", "input_ids", "attention_mask"})

    def test_collator_pads_and_masks_a_shorter_sequence(self):
        examples = [
            self.tokenizer("الف روشن", truncation=True, max_length=demo.MAX_LENGTH),
            self.tokenizer("یک متن ساختگی طولانی‌تر برای آزمون padding", truncation=True, max_length=demo.MAX_LENGTH),
        ]
        collator = DataCollatorWithPadding(tokenizer=self.tokenizer, return_tensors="pt")
        batch = collator(examples)
        self.assertEqual(batch["input_ids"].ndim, 2)
        self.assertEqual(batch["attention_mask"].shape, batch["input_ids"].shape)
        self.assertTrue(torch.all(batch["input_ids"][:, 0] == self.tokenizer.cls_token_id).item())
        self.assertTrue(torch.any(batch["attention_mask"] == 0).item())
        self.assertTrue(torch.all(batch["input_ids"][batch["attention_mask"] == 0] == self.tokenizer.pad_token_id).item())


class EndToEndTests(unittest.TestCase):
    def test_cpu_smoke_records_limits_and_finite_losses(self):
        result = demo.run_pipeline(seed=58, max_steps=2)
        self.assertEqual(result["fixture_sha256"], "eb21fe6a41dcd4dc828c00a7dc0293370087bb77fc6df022078fc16a20d750a2")
        self.assertEqual(result["environment"]["accelerator_device"], "cpu")
        self.assertEqual(result["environment"]["packages"]["torch"], str(torch.__version__))
        self.assertEqual(result["data"]["group_overlap"], [])
        self.assertEqual(result["tokenizer"]["trained_on_split"], "train")
        self.assertEqual(result["training"]["steps"], 2)
        self.assertTrue(result["training"]["all_gradients_finite"])
        self.assertTrue(all(torch.isfinite(torch.tensor(loss)).item() for loss in result["training"]["training_losses"]))
        self.assertEqual(result["scope"]["gpu_used"], False)
        self.assertEqual(result["scope"]["pretrained_weights_used"], False)
        self.assertEqual(result["scope"]["hub_access_or_download"], False)
        self.assertEqual(result["scope"]["benchmark_performed"], False)
        self.assertEqual(result["scope"]["model_quality_claim"], False)

    def test_fixed_seed_repeats_training_losses(self):
        first = demo.run_pipeline(seed=58, max_steps=2)
        second = demo.run_pipeline(seed=58, max_steps=2)
        self.assertEqual(first["training"]["training_losses"], second["training"]["training_losses"])
        self.assertEqual(first["tokenizer"]["training_text_sha256"], second["tokenizer"]["training_text_sha256"])

    def test_invalid_step_count_is_rejected(self):
        with self.assertRaisesRegex(demo.PipelineInputError, "positive integer"):
            demo.run_pipeline(max_steps=0)
        with self.assertRaisesRegex(demo.PipelineInputError, "exceeds"):
            demo.run_pipeline(max_steps=5)

    def test_cli_writes_json_and_honors_offline_mode(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            environment = os.environ.copy()
            environment["HF_HUB_OFFLINE"] = "1"
            environment["HF_DATASETS_OFFLINE"] = "1"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(demo.ROOT / "pipeline_demo.py"),
                    "--output",
                    str(output),
                    "--max-steps",
                    "1",
                ],
                cwd=demo.ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["fixture_id"], demo.FIXTURE_ID)
            self.assertEqual(result["training"]["steps"], 1)
            self.assertFalse(result["scope"]["hub_access_or_download"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
