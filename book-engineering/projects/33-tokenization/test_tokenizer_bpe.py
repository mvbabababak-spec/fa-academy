"""Deterministic and round-trip tests for the toy byte-BPE project."""
import tempfile
import unittest
from pathlib import Path

from tokenizer_bpe import BYTE_OFFSET, ByteBPE, EVAL_TEXTS, TRAIN_CORPUS


class ByteBPETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokenizer = ByteBPE.train(TRAIN_CORPUS, num_merges=24)

    def test_hand_count_and_expected_ids(self):
        tokenizer = ByteBPE.train(["abab", "abac"], num_merges=1)
        self.assertEqual(tokenizer.merges, ((BYTE_OFFSET + ord("a"), BYTE_OFFSET + ord("b")),))
        self.assertEqual(tokenizer.encode("abab"), [260, 260])
        self.assertEqual(tokenizer.encode("abac"), [260, 101, 103])
        self.assertEqual(tokenizer.vocab_size, 261)

    def test_round_trip_ascii_persian_emoji_and_whitespace(self):
        samples = ["", "Hello, AI!", "مدل زبانی", "می‌آموزد 🤖\n", "A\u030a / Å"]
        for text in samples:
            with self.subTest(text=text):
                self.assertEqual(self.tokenizer.decode(self.tokenizer.encode(text)), text)

    def test_special_tokens_are_explicit_and_skippable(self):
        ids = self.tokenizer.encode("AI", add_bos=True, add_eos=True)
        self.assertEqual(ids[0], 1)
        self.assertEqual(ids[-1], 2)
        self.assertEqual(self.tokenizer.decode(ids), "AI")
        self.assertEqual(self.tokenizer.decode(ids, skip_special_tokens=False), "<|bos|>AI<|eos|>")

    def test_visible_special_spelling_is_ordinary_text(self):
        text = "<|bos|> is a visible spelling, not a control token here"
        ids = self.tokenizer.encode(text)
        self.assertNotIn(1, ids)
        self.assertEqual(self.tokenizer.decode(ids), text)

    def test_no_unknown_token_is_needed_for_valid_utf8(self):
        for text in EVAL_TEXTS:
            ids = self.tokenizer.encode(text)
            self.assertNotIn(3, ids)
            self.assertEqual(self.tokenizer.decode(ids), text)

    def test_merge_training_is_deterministic_and_order_independent_for_ties(self):
        one = ByteBPE.train(TRAIN_CORPUS, num_merges=24)
        two = ByteBPE.train(reversed(TRAIN_CORPUS), num_merges=24)
        self.assertEqual(one.merges, two.merges)
        self.assertEqual(one.vocab_size, two.vocab_size)

    def test_save_load_preserves_vocabulary_and_encoding(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tokenizer.json"
            self.tokenizer.save(path)
            restored = ByteBPE.load(path)
            self.assertEqual(restored.merges, self.tokenizer.merges)
            for text in EVAL_TEXTS:
                self.assertEqual(restored.encode(text), self.tokenizer.encode(text))
                self.assertEqual(restored.decode(restored.encode(text)), text)

    def test_invalid_training_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            ByteBPE.train([], num_merges=1)
        with self.assertRaises(TypeError):
            ByteBPE.train("not a corpus", num_merges=1)
        with self.assertRaises(TypeError):
            ByteBPE.train(["valid", 4], num_merges=1)
        with self.assertRaises(ValueError):
            ByteBPE.train(["valid"], num_merges=-1)

    def test_invalid_encode_and_decode_values_are_rejected(self):
        with self.assertRaises(TypeError):
            self.tokenizer.encode(123)
        with self.assertRaises(ValueError):
            self.tokenizer.decode([self.tokenizer.vocab_size])
        with self.assertRaises(TypeError):
            self.tokenizer.decode([True])
        with self.assertRaises(TypeError):
            self.tokenizer.encode("text", add_bos=1)

    def test_normalization_is_not_silently_applied(self):
        composed = "Å"
        decomposed = "A\u030a"
        self.assertNotEqual(self.tokenizer.encode(composed), self.tokenizer.encode(decomposed))
        self.assertEqual(self.tokenizer.decode(self.tokenizer.encode(composed)), composed)
        self.assertEqual(self.tokenizer.decode(self.tokenizer.encode(decomposed)), decomposed)

    def test_merge_count_never_increases_byte_baseline_count(self):
        baseline = ByteBPE.train(TRAIN_CORPUS, num_merges=0)
        for text in EVAL_TEXTS:
            self.assertLessEqual(len(self.tokenizer.encode(text)), len(baseline.encode(text)))


if __name__ == "__main__":
    unittest.main()
