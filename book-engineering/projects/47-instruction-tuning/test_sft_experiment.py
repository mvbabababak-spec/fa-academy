"""Pure-Python tests for the chapter 47 data contract and loss mask."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from sft_experiment import (
    audit_dataset,
    collate_features,
    encode_prompt_completion,
    load_jsonl,
    split_by_group,
)

ROOT = Path(__file__).resolve().parent


class FakeTokenizer:
    bos_token_id = 1
    eos_token_id = 2
    pad_token_id = 0

    def encode(self, text: str, *, add_special_tokens: bool = False) -> list[int]:
        if add_special_tokens:
            raise AssertionError("the SFT example encodes prompt and completion separately")
        return [10 + len(word) for word in text.split()]


class SFTDataContractTests(unittest.TestCase):
    def test_sample_fixture_is_group_split_and_counts_are_audit_only(self):
        rows = load_jsonl(ROOT / "sample_sft.jsonl")
        first = split_by_group(rows, seed=47)
        second = split_by_group(rows, seed=47)
        self.assertEqual(
            {name: [row["id"] for row in first[name]] for name in first},
            {name: [row["id"] for row in second[name]] for name in second},
        )
        self.assertTrue(all(first[name] for name in ("train", "validation", "test")))
        assignment = {
            row["group_id"]: name
            for name, split in first.items()
            for row in split
        }
        self.assertEqual(len(assignment), len({row["group_id"] for row in rows}))
        for name, split in first.items():
            self.assertTrue(all(assignment[row["group_id"]] == name for row in split))

    def test_split_changes_when_seed_changes_without_group_leakage(self):
        rows = load_jsonl(ROOT / "sample_sft.jsonl")
        split_a = split_by_group(rows, seed=47)
        split_b = split_by_group(rows, seed=48)
        owners_a = {row["group_id"]: name for name, group in split_a.items() for row in group}
        owners_b = {row["group_id"]: name for name, group in split_b.items() for row in group}
        self.assertNotEqual(owners_a, owners_b)
        for owner_map in (owners_a, owners_b):
            for name, group in (split_a if owner_map is owners_a else split_b).items():
                self.assertTrue(all(owner_map[row["group_id"]] == name for row in group))

    def test_group_split_requires_three_independent_groups(self):
        rows = [
            {"id": f"r{i}", "source_id": "demo", "group_id": f"g{i}", "prompt": "p", "completion": "c"}
            for i in range(2)
        ]
        with self.assertRaisesRegex(ValueError, "at least three"):
            split_by_group(rows)

    def test_prompt_is_masked_and_completion_plus_eos_is_supervised(self):
        encoded = encode_prompt_completion("ask now", "ok", FakeTokenizer(), max_length=16)
        self.assertEqual(encoded["input_ids"], [1, 13, 13, 12, 2])
        self.assertEqual(encoded["labels"], [-100, -100, -100, 12, 2])
        self.assertEqual(sum(value != -100 for value in encoded["labels"][1:]), 2)

    def test_left_truncation_keeps_target_and_never_exceeds_length(self):
        encoded = encode_prompt_completion("one two three four", "ok", FakeTokenizer(), max_length=5)
        self.assertEqual(len(encoded["input_ids"]), 5)
        self.assertEqual(encoded["input_ids"][-2:], [12, 2])
        self.assertEqual(encoded["labels"][-2:], [12, 2])
        self.assertEqual(encoded["labels"][:3], [-100, -100, -100])

    def test_too_long_target_is_rejected_not_silently_cut(self):
        with self.assertRaisesRegex(ValueError, "no room"):
            encode_prompt_completion("ask", "one two three", FakeTokenizer(), max_length=4)

    def test_collation_masks_padding(self):
        batch = collate_features(
            [
                {"input_ids": [1, 10, 12], "labels": [-100, -100, 12]},
                {"input_ids": [1, 11], "labels": [-100, 11]},
            ],
            pad_token_id=0,
        )
        self.assertEqual(batch["input_ids"], [[1, 10, 12], [1, 11, 0]])
        self.assertEqual(batch["attention_mask"], [[1, 1, 1], [1, 1, 0]])
        self.assertEqual(batch["labels"], [[-100, -100, 12], [-100, 11, -100]])

    def test_loader_rejects_duplicate_ids_and_missing_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rows.jsonl"
            row = {"id": "same", "source_id": "demo", "group_id": "g1", "prompt": "p", "completion": "c"}
            path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate id"):
                load_jsonl(path)
            path.write_text(json.dumps({"id": "missing", "prompt": "p"}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source_id"):
                load_jsonl(path)

    def test_audit_writes_counts_without_loading_or_training_a_model(self):
        with tempfile.TemporaryDirectory() as directory:
            report = audit_dataset(ROOT / "sample_sft.jsonl", directory, seed=47)
            saved = json.loads((Path(directory) / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(report, saved)
        self.assertFalse(saved["training_performed"])
        self.assertFalse(saved["model_downloaded_or_loaded"])
        self.assertEqual(saved["test_evaluations"], 0)
        self.assertEqual(saved["data"]["records"], 15)
        self.assertEqual(saved["data"]["groups"], 14)


if __name__ == "__main__":
    unittest.main()
