from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import torch

from tiny_lm import (
    SPECIAL_TOKENS,
    TinyFeedForwardLM,
    build_examples,
    decode_ids,
    encode_text,
    evaluate,
    generate,
    load_checkpoint,
    load_dataset,
    model_config,
    normalize_text,
    save_checkpoint,
    tokenize_words,
    train_model,
    validate_vocabulary,
)

ROOT = Path(__file__).resolve().parent
VOCAB = list(SPECIAL_TOKENS) + ["سلام", "دنیا", "جهان", "یک", "واژه", "مدل", "کوچک", "."]


def record(record_id: str, group_id: str, text: str) -> dict:
    digest = hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()
    return {"id": record_id, "group_id": group_id, "text": normalize_text(text), "normalized_text_sha256": digest}


def write_dataset(root: Path, *, fit_split: str = "train", leak_group: bool = False,
                  duplicate_id: bool = False, declared_groups_wrong: bool = False,
                  holdout_only_vocab: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    vocabulary = VOCAB + (["فقط‌آزمون"] if holdout_only_vocab else [])
    (root / "vocab.json").write_text(json.dumps({
        "format_version": 1,
        "kind": "educational-word-level-tokenizer",
        "normalization": "Unicode NFC and whitespace collapse; Persian ZWNJ retained",
        "special_tokens": list(SPECIAL_TOKENS),
        "vocabulary": vocabulary,
    }, ensure_ascii=False), encoding="utf-8")
    splits = {
        "train": [
            record("tr-1", "g1", "سلام دنیا جهان یک واژه مدل کوچک ."),
            record("tr-2", "g2", "سلام جهان مدل کوچک")
        ],
        "validation": [record("va-1", "g1" if leak_group else "g3", "یک واژه")],
        "test": [record("tr-1" if duplicate_id else "te-1", "g4", "مدل کوچک")],
    }
    for name, rows in splits.items():
        (root / f"{name}.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )
    declared = {name: sorted({row["group_id"] for row in rows}) for name, rows in splits.items()}
    if declared_groups_wrong:
        declared["train"] = ["not-a-real-group"]
    summary = {
        "tokenizer_fit_split": fit_split,
        "normalization": "Unicode NFC and whitespace collapse; Persian ZWNJ retained",
        "tokenizer_vocabulary_size": len(vocabulary),
        "split_groups": declared,
    }
    (root / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    return root


def examples(text: str, block_size: int = 2):
    return build_examples([record("r", "g", text)], VOCAB, block_size)


class TokenAndWindowTests(unittest.TestCase):
    def test_normalization_is_nfc_and_preserves_persian_zwnj(self):
        self.assertEqual(normalize_text("  e\u0301\r\n تازه‌کار  "), "é تازه‌کار")
        self.assertEqual(tokenize_words("تازه‌کار!"), ["تازه‌کار", "!"])

    def test_vocabulary_contract_and_duplicates_are_rejected(self):
        self.assertEqual(validate_vocabulary(VOCAB), VOCAB)
        with self.assertRaisesRegex(ValueError, "start with"):
            validate_vocabulary(["<unk>", "<pad>", "<bos>", "<eos>"])
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_vocabulary(list(SPECIAL_TOKENS) + ["سلام", "سلام"])

    def test_encode_adds_boundaries_and_maps_unseen_tokens_to_unk(self):
        ids = encode_text("سلام دیده‌نشده", VOCAB)
        self.assertEqual(ids[0], VOCAB.index("<bos>"))
        self.assertEqual(ids[-1], VOCAB.index("<eos>"))
        self.assertEqual(ids[2], VOCAB.index("<unk>"))

    def test_decode_skips_boundaries_and_rejects_invalid_ids(self):
        ids = [VOCAB.index("<bos>"), VOCAB.index("سلام"), VOCAB.index("<eos>")]
        self.assertEqual(decode_ids(ids, VOCAB), "سلام")
        self.assertIn("<eos>", decode_ids(ids, VOCAB, skip_special=False))
        with self.assertRaisesRegex(ValueError, "outside this vocabulary"):
            decode_ids([len(VOCAB)], VOCAB)

    def test_next_token_targets_are_shifted_by_one(self):
        rows = examples("سلام دنیا")
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][1], VOCAB.index("سلام"))
        self.assertEqual(rows[1][1], VOCAB.index("دنیا"))
        self.assertEqual(rows[2][1], VOCAB.index("<eos>"))
        self.assertEqual(rows[1][0], [VOCAB.index("<bos>"), VOCAB.index("سلام")])

    def test_context_is_left_padded_and_keeps_only_recent_tokens(self):
        rows = examples("سلام دنیا جهان", block_size=2)
        self.assertEqual(rows[0][0], [VOCAB.index("<pad>"), VOCAB.index("<bos>")])
        self.assertEqual(rows[-1][0], [VOCAB.index("دنیا"), VOCAB.index("جهان")])
        with self.assertRaisesRegex(ValueError, "block_size"):
            build_examples([record("r", "g", "سلام")], VOCAB, 0)

    def test_context_windows_never_cross_record_boundaries(self):
        rows = build_examples([record("a", "g1", "سلام"), record("b", "g2", "دنیا")], VOCAB, 2)
        bos_contexts = [context for context, _ in rows if context[-1] == VOCAB.index("<bos>")]
        self.assertEqual(bos_contexts, [[VOCAB.index("<pad>"), VOCAB.index("<bos>")]] * 2)
        self.assertNotIn([VOCAB.index("سلام"), VOCAB.index("<eos>")], [context for context, _ in rows])


class DataIntegrityTests(unittest.TestCase):
    def test_load_dataset_checks_files_hashes_groups_and_fit_split(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = load_dataset(write_dataset(Path(temp)))
            self.assertEqual(bundle["summary"]["tokenizer_fit_split"], "train")
            self.assertEqual(set(bundle["splits"]), {"train", "validation", "test"})
            self.assertEqual(len(bundle["vocabulary_sha256"]), 64)
            self.assertEqual(len(bundle["summary_sha256"]), 64)
            self.assertEqual(set(bundle["split_sha256"]), {"train", "validation", "test"})
            self.assertTrue(all(len(value) == 64 for value in bundle["split_sha256"].values()))

    def test_loader_rejects_tokenizer_fit_on_holdout(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "fit_split=train"):
                load_dataset(write_dataset(Path(temp), fit_split="validation"))

    def test_loader_rejects_group_leakage(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "group leakage"):
                load_dataset(write_dataset(Path(temp), leak_group=True))

    def test_loader_rejects_record_ids_repeated_across_splits(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "record id appears"):
                load_dataset(write_dataset(Path(temp), duplicate_id=True))

    def test_loader_rejects_summary_group_membership_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "split_groups in summary"):
                load_dataset(write_dataset(Path(temp), declared_groups_wrong=True))

    def test_loader_rejects_vocabulary_token_absent_from_train(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "tokens absent from train"):
                load_dataset(write_dataset(Path(temp), holdout_only_vocab=True))

    def test_loader_rejects_changed_text_with_stale_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = write_dataset(Path(temp))
            train_path = root / "train.jsonl"
            rows = [json.loads(line) for line in train_path.read_text(encoding="utf-8").splitlines()]
            rows[0]["text"] = "سلام ویرایش‌شده"
            train_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "normalized text hash or form"):
                load_dataset(root)


class ModelAndTrainingTests(unittest.TestCase):
    def setUp(self):
        self.train = examples("سلام دنیا سلام", block_size=2)
        self.validation = examples("سلام جهان", block_size=2)
        self.model = TinyFeedForwardLM(len(VOCAB), block_size=2, embedding_dim=4, hidden_dim=8)

    def test_model_returns_one_logit_per_vocabulary_item(self):
        logits = self.model(torch.tensor([[VOCAB.index("<bos>"), VOCAB.index("سلام")]], dtype=torch.long))
        self.assertEqual(tuple(logits.shape), (1, len(VOCAB)))
        self.assertTrue(torch.isfinite(logits).all())

    def test_model_rejects_wrong_rank_width_and_dtype(self):
        with self.assertRaisesRegex(ValueError, "shape"):
            self.model(torch.zeros((2, 3), dtype=torch.long))
        with self.assertRaisesRegex(ValueError, "shape"):
            self.model(torch.zeros((2,), dtype=torch.long))
        with self.assertRaisesRegex(TypeError, "torch.long"):
            self.model(torch.zeros((1, 2), dtype=torch.float32))

    def test_evaluation_is_finite_token_mean_and_does_not_create_gradients(self):
        metrics = evaluate(self.model, self.validation, batch_size=2)
        self.assertGreater(metrics["mean_nll_nats_per_token"], 0)
        self.assertGreater(metrics["perplexity"], 1)
        self.assertEqual(metrics["target_tokens"], len(self.validation))
        self.assertTrue(all(parameter.grad is None for parameter in self.model.parameters()))

    def test_training_updates_parameters_and_records_validation(self):
        before = {key: value.detach().clone() for key, value in self.model.state_dict().items()}
        model, history = train_model(self.train, self.validation, VOCAB, seed=8, epochs=2,
                                     batch_size=2, block_size=2, embedding_dim=4, hidden_dim=8)
        self.assertEqual(len(history), 2)
        self.assertIn("validation", history[-1])
        self.assertTrue(any(not torch.equal(before[key], value) for key, value in model.state_dict().items()))
        self.assertTrue(torch.isfinite(torch.tensor(history[-1]["train"]["mean_nll_nats_per_token"])))

    def test_training_is_repeatable_on_cpu_for_fixed_inputs_and_seed(self):
        kwargs = dict(seed=19, epochs=2, batch_size=2, block_size=2, embedding_dim=4, hidden_dim=8)
        first, first_history = train_model(self.train, self.validation, VOCAB, **kwargs)
        second, second_history = train_model(self.train, self.validation, VOCAB, **kwargs)
        for key in first.state_dict():
            self.assertTrue(torch.equal(first.state_dict()[key], second.state_dict()[key]), key)
        self.assertEqual(first_history, second_history)

    def test_checkpoint_round_trip_preserves_logits_and_safe_metadata(self):
        config = model_config(VOCAB, block_size=2, embedding_dim=4, hidden_dim=8)
        sample = torch.tensor([[VOCAB.index("<bos>"), VOCAB.index("سلام")]], dtype=torch.long)
        expected = self.model(sample).detach()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "nested" / "checkpoint.pt"
            save_checkpoint(path, self.model, VOCAB, config, {"seed": 4, "optimizer": "AdamW"})
            restored, payload = load_checkpoint(path)
            torch.testing.assert_close(restored(sample), expected)
            self.assertEqual(payload["metadata"]["seed"], 4)
            self.assertEqual(payload["model_type"], "tiny-fixed-context-feedforward-lm")

    def test_generation_stops_at_eos_is_seeded_and_checks_temperature(self):
        model = TinyFeedForwardLM(len(VOCAB), block_size=2, embedding_dim=4, hidden_dim=8)
        eos = VOCAB.index("<eos>")
        with torch.no_grad():
            model.output.weight.zero_()
            model.output.bias.zero_()
            model.output.bias[eos] = 10
        generated = generate(model, VOCAB, "سلام", max_new_tokens=5, temperature=0)
        self.assertEqual(generated["new_tokens"], 1)
        self.assertEqual(generated["text"], "سلام")
        with torch.no_grad():
            model.output.bias[eos] = -10
        first = generate(model, VOCAB, "سلام", max_new_tokens=5, temperature=1, seed=7)
        second = generate(model, VOCAB, "سلام", max_new_tokens=5, temperature=1, seed=7)
        self.assertEqual(first, second)
        self.assertLessEqual(first["new_tokens"], 5)
        with self.assertRaisesRegex(ValueError, "temperature"):
            generate(model, VOCAB, "", temperature=-1)


class CommandLineTests(unittest.TestCase):
    def test_cli_trains_and_respects_validation_only_test_policy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data_dir = write_dataset(root / "corpus")
            for skip_test in (False, True):
                output = root / ("validation-only" if skip_test else "final-run")
                command = [
                    sys.executable, str(ROOT / "tiny_lm.py"),
                    "--data-dir", str(data_dir), "--output-dir", str(output),
                    "--epochs", "1", "--batch-size", "2", "--block-size", "2",
                    "--embedding-dim", "4", "--hidden-dim", "8", "--seed", "23",
                    "--prompt", "سلام", "--max-new-tokens", "2", "--temperature", "0",
                ]
                if skip_test:
                    command.append("--skip-test")
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stderr[-2000:])
                self.assertTrue((output / "metrics.json").is_file())
                self.assertTrue((output / "history.json").is_file())
                self.assertTrue((output / "checkpoint.pt").is_file())
                metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
                self.assertEqual(metrics["device"], "cpu")
                if skip_test:
                    self.assertIsNone(metrics["test_once_after_training"])
                    self.assertIn("--skip-test", metrics["test_policy"])
                else:
                    self.assertIsInstance(metrics["test_once_after_training"], dict)
                    self.assertIn("once", metrics["test_policy"])


if __name__ == "__main__":
    unittest.main()
