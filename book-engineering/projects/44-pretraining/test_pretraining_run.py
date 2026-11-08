import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import torch

from pretraining_run import (
    BatchCursor,
    make_config,
    train_pretraining,
    warmup_cosine_learning_rate,
)


VOCAB = ["<pad>", "<unk>", "<bos>", "<eos>", "alef", "be", "pe", "te"]
IDENTITY = {
    "summary_sha256": "a" * 64,
    "vocabulary_sha256": "b" * 64,
    "split_sha256": {"train": "c" * 64, "validation": "d" * 64, "test": "e" * 64},
}
TRAIN = [
    ([0, 0, 2, 4], 5),
    ([0, 2, 4, 5], 6),
    ([2, 4, 5, 6], 7),
    ([0, 0, 2, 5], 4),
    ([0, 2, 5, 4], 6),
]
VALIDATION = [([0, 0, 2, 4], 6), ([0, 2, 4, 6], 7)]
TEST = [([0, 0, 2, 5], 6), ([0, 2, 5, 6], 4)]


def small_config(**overrides):
    values = {
        "total_updates": 6,
        "microbatch_size": 2,
        "gradient_accumulation_steps": 2,
        "peak_lr": 0.01,
        "warmup_updates": 2,
        "min_lr_ratio": 0.1,
        "evaluation_every": 2,
        "checkpoint_every": 2,
        "seed": 7,
        "block_size": 4,
        "embedding_dim": 4,
        "hidden_dim": 8,
    }
    values.update(overrides)
    return make_config(VOCAB, **values)


class PretrainingScheduleTests(unittest.TestCase):
    def test_warmup_cosine_boundaries_and_no_warmup(self):
        self.assertAlmostEqual(warmup_cosine_learning_rate(1, peak_lr=0.1, total_updates=10, warmup_updates=2), 0.05)
        self.assertAlmostEqual(warmup_cosine_learning_rate(2, peak_lr=0.1, total_updates=10, warmup_updates=2), 0.1)
        self.assertAlmostEqual(warmup_cosine_learning_rate(10, peak_lr=0.1, total_updates=10, warmup_updates=2), 0.01)
        self.assertAlmostEqual(warmup_cosine_learning_rate(1, peak_lr=0.1, total_updates=10, warmup_updates=0), 0.1)
        self.assertAlmostEqual(warmup_cosine_learning_rate(10, peak_lr=0.1, total_updates=10, warmup_updates=0), 0.01)
        self.assertAlmostEqual(warmup_cosine_learning_rate(1, peak_lr=0.1, total_updates=1, warmup_updates=0), 0.1)

    def test_schedule_rejects_invalid_update_and_warmup(self):
        with self.assertRaises(ValueError):
            warmup_cosine_learning_rate(0, peak_lr=0.1, total_updates=10, warmup_updates=2)
        with self.assertRaises(ValueError):
            warmup_cosine_learning_rate(1, peak_lr=0.1, total_updates=4, warmup_updates=4)
        with self.assertRaises(ValueError):
            warmup_cosine_learning_rate(1, peak_lr=float("nan"), total_updates=4, warmup_updates=1)
        with self.assertRaises(ValueError):
            warmup_cosine_learning_rate(1, peak_lr=0.1, total_updates=4, warmup_updates=1, min_lr_ratio=1.2)

    def test_cursor_saves_permutation_position_and_rng(self):
        first = BatchCursor(5, microbatch_size=2, accumulation_steps=2, seed=9)
        first_window = first.next_window()
        self.assertEqual([len(batch) for batch in first_window], [2, 2])
        state = first.state_dict()
        expected_next = first.next_window()
        restored = BatchCursor(5, microbatch_size=2, accumulation_steps=2, seed=1000)
        restored.load_state_dict(state)
        self.assertEqual(restored.next_window(), expected_next)

    def test_cursor_covers_partial_batch_without_dropping_examples(self):
        cursor = BatchCursor(5, microbatch_size=2, accumulation_steps=3, seed=11)
        window = cursor.next_window()
        self.assertEqual(sorted(index for batch in window for index in batch), list(range(5)))
        self.assertEqual([len(batch) for batch in window], [2, 2, 1])

    def test_gradient_accumulation_matches_one_combined_batch(self):
        config_full = small_config(total_updates=1, warmup_updates=0, microbatch_size=4, gradient_accumulation_steps=1,
                                   evaluation_every=1, checkpoint_every=1)
        config_accum = small_config(total_updates=1, warmup_updates=0, microbatch_size=2, gradient_accumulation_steps=2,
                                    evaluation_every=1, checkpoint_every=1)
        with tempfile.TemporaryDirectory() as folder:
            full = train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config_full, identity=IDENTITY,
                                     output_dir=Path(folder) / "full")
            accumulated = train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config_accum, identity=IDENTITY,
                                            output_dir=Path(folder) / "accum")
            full_state = torch.load(Path(folder) / "full/checkpoint-final.pt", map_location="cpu", weights_only=True)
            accum_state = torch.load(Path(folder) / "accum/checkpoint-final.pt", map_location="cpu", weights_only=True)
            for name, tensor in full_state["model_state_dict"].items():
                self.assertTrue(torch.allclose(tensor, accum_state["model_state_dict"][name], atol=1e-7, rtol=1e-6), name)
            self.assertEqual(full["test_once_after_training"], 1)
            self.assertEqual(accumulated["test_once_after_training"], 1)

    def test_interrupted_resume_matches_uninterrupted_run_and_test_is_once(self):
        config = small_config()
        with tempfile.TemporaryDirectory() as folder:
            full_dir = Path(folder) / "full"
            split_dir = Path(folder) / "split"
            resumed_dir = Path(folder) / "resumed"
            full = train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY, output_dir=full_dir)
            partial = train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY,
                                        output_dir=split_dir, stop_after=3)
            self.assertFalse(partial["completed"])
            self.assertEqual(partial["test_once_after_training"], 0)
            self.assertIsNone(partial["test_metrics"])
            resumed = train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY,
                                        output_dir=resumed_dir, resume_from=split_dir / "checkpoint-latest.pt")
            self.assertEqual(full, resumed)
            self.assertEqual((full_dir / "history.json").read_bytes(), (resumed_dir / "history.json").read_bytes())
            state_a = torch.load(full_dir / "checkpoint-final.pt", map_location="cpu", weights_only=True)
            state_b = torch.load(resumed_dir / "checkpoint-final.pt", map_location="cpu", weights_only=True)
            for name, tensor in state_a["model_state_dict"].items():
                self.assertTrue(torch.equal(tensor, state_b["model_state_dict"][name]), name)
            again = train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY,
                                     output_dir=Path(folder) / "again", resume_from=resumed_dir / "checkpoint-final.pt")
            self.assertEqual(again, full)
            self.assertEqual(again["test_once_after_training"], 1)

    def test_resume_refuses_changed_training_configuration(self):
        config = small_config()
        changed = small_config(peak_lr=0.02)
        with tempfile.TemporaryDirectory() as folder:
            partial_dir = Path(folder) / "partial"
            train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY,
                              output_dir=partial_dir, stop_after=2)
            with self.assertRaisesRegex(ValueError, "config or data hashes differ"):
                train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=changed, identity=IDENTITY,
                                  output_dir=Path(folder) / "changed", resume_from=partial_dir / "checkpoint-latest.pt")

    def test_resume_refuses_changed_data_identity(self):
        config = small_config()
        changed_identity = dict(IDENTITY, summary_sha256="f" * 64)
        with tempfile.TemporaryDirectory() as folder:
            partial_dir = Path(folder) / "partial"
            train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY,
                              output_dir=partial_dir, stop_after=2)
            with self.assertRaisesRegex(ValueError, "config or data hashes differ"):
                train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=changed_identity,
                                  output_dir=Path(folder) / "changed", resume_from=partial_dir / "checkpoint-latest.pt")

    def test_outputs_are_json_and_partial_run_does_not_evaluate_test(self):
        config = small_config()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "run"
            metrics = train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY,
                                        output_dir=output, stop_after=2)
            stored = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics, stored)
            self.assertEqual(stored["status"], "partial")
            self.assertEqual(stored["target_tokens_seen"], sum(row["target_tokens_in_update"] for row in json.loads((output / "history.json").read_text(encoding="utf-8"))))
            self.assertTrue((output / "run_card.md").is_file())
            self.assertFalse(list(output.glob("*.tmp")))
            chart_path = output / "loss_curve.svg"
            chart = ET.parse(chart_path).getroot()
            svg_ns = "{http://www.w3.org/2000/svg}"
            self.assertEqual(chart.tag, svg_ns + "svg")
            polylines = chart.findall(".//" + svg_ns + "polyline")
            circles = chart.findall(".//" + svg_ns + "circle")
            self.assertEqual(len(polylines), 2)
            self.assertEqual(len(circles), 2)
            self.assertIn("history.json", chart.find(svg_ns + "desc").text)
            history = json.loads((output / "history.json").read_text(encoding="utf-8"))
            validation_count = sum(row["validation"] is not None for row in history)
            self.assertEqual(len(polylines[0].attrib["points"].split()), len(history))
            self.assertEqual(len(polylines[1].attrib["points"].split()), validation_count)
            self.assertEqual(len(circles), validation_count + 1)

    def test_checkpoint_rejects_unsupported_version(self):
        config = small_config()
        with tempfile.TemporaryDirectory() as folder:
            partial_dir = Path(folder) / "partial"
            train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY,
                              output_dir=partial_dir, stop_after=2)
            checkpoint = torch.load(partial_dir / "checkpoint-latest.pt", map_location="cpu", weights_only=True)
            checkpoint["checkpoint_version"] = 999
            bad = Path(folder) / "bad.pt"
            torch.save(checkpoint, bad)
            with self.assertRaisesRegex(ValueError, "unsupported or malformed"):
                train_pretraining(TRAIN, VALIDATION, TEST, VOCAB, config=config, identity=IDENTITY,
                                  output_dir=Path(folder) / "resume", resume_from=bad)


if __name__ == "__main__":
    unittest.main()
