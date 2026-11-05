from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from small_corpus import (
    SPECIAL_TOKENS,
    SimpleWordTokenizer,
    deduplicate_records,
    load_manifest,
    normalize_text,
    prepare_dataset,
    sensitive_pattern_matches,
    split_by_group,
    train_word_vocabulary,
    validate_record,
)


ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "sample_corpus.jsonl"


def record(record_id: str, group_id: str, text: str, **changes) -> dict:
    value = {
        "id": record_id,
        "group_id": group_id,
        "text": text,
        "source": "self-authored-demo",
        "license": "SELF-CREATED",
        "attribution": "Babak & Ai — test fixture",
        "language": "fa",
        "acquired_at": "2026-11-05",
        "rights_note": "original test fixture",
    }
    value.update(changes)
    return value


class ManifestTests(unittest.TestCase):
    def test_sample_manifest_has_sixteen_documented_records(self):
        rows = load_manifest(SAMPLE)
        self.assertEqual(len(rows), 16)
        self.assertEqual(len({row["id"] for row in rows}), 16)
        self.assertTrue(all(row["license"] == "SELF-CREATED" for row in rows))
        self.assertTrue(all(row["normalized_text_sha256"] for row in rows))

    def test_normalization_is_conservative_and_keeps_persian_zwnj(self):
        self.assertEqual(normalize_text("  café\r\n  تازه‌کار  "), "café تازه‌کار")
        self.assertEqual(normalize_text("e\u0301  "), "é")

    def test_unapproved_license_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside this demo's allowlist"):
            validate_record(record("x", "g1", "متن", license="CC-BY-NC-4.0"))

    def test_cc_by_requires_source_url_and_attribution(self):
        with self.assertRaisesRegex(ValueError, "CC-BY-4.0 rows require"):
            validate_record(record("x", "g1", "متن", license="CC-BY-4.0", source="unknown"))
        accepted = record(
            "x", "g1", "متن", license="CC-BY-4.0", source="https://example.org/work",
            attribution="Author, title, CC BY 4.0",
        )
        self.assertEqual(validate_record(accepted)["license"], "CC-BY-4.0")

    def test_missing_provenance_field_is_rejected(self):
        bad = record("x", "g1", "متن")
        del bad["rights_note"]
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            validate_record(bad)

    def test_invalid_acquired_at_date_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "acquired_at must begin with an ISO date"):
            validate_record(record("x", "g1", "متن", acquired_at="not-a-date"))

    def test_possible_email_and_phone_patterns_are_flagged(self):
        self.assertIn("email-like", sensitive_pattern_matches("contact a.person@example.org"))
        self.assertIn("phone-like", sensitive_pattern_matches("call +1 (214) 555-0182"))
        with self.assertRaisesRegex(ValueError, "possible sensitive pattern"):
            validate_record(record("x", "g1", "email me at a.person@example.org"))

    def test_manifest_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.jsonl"
            row = record("same", "g1", "اول")
            path.write_text(json.dumps(row, ensure_ascii=False) + "\n" + json.dumps(row, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate record id"):
                load_manifest(path)

    def test_manifest_rejects_malformed_json_with_line_number(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.jsonl"
            path.write_text("{broken\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 1"):
                load_manifest(path)


class CurationTests(unittest.TestCase):
    def test_exact_dedup_uses_normalized_text_and_keeps_audit_trail(self):
        first = record("one", "g1", "سلام   دنیا")
        second = record("two", "g2", "سلام\nدنیا", source="different-source", license="CC0-1.0", attribution="Other creator")
        unique, duplicates = deduplicate_records([first, second])
        self.assertEqual([row["id"] for row in unique], ["one"])
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["duplicate_id"], "two")
        self.assertEqual(duplicates[0]["kept_id"], "one")
        self.assertEqual(duplicates[0]["reason"], "exact normalized text hash matched")
        self.assertEqual(duplicates[0]["duplicate_source"], "different-source")
        self.assertEqual(duplicates[0]["duplicate_license"], "CC0-1.0")
        self.assertEqual(duplicates[0]["duplicate_record_metadata"]["attribution"], "Other creator")

    def test_group_split_covers_rows_without_group_leakage(self):
        rows = [record(f"{group}-{i}", group, f"متن {group} {i}") for group in "abcd" for i in range(2)]
        splits, membership = split_by_group(rows, seed=7)
        self.assertEqual({row["id"] for split in splits.values() for row in split}, {row["id"] for row in rows})
        self.assertEqual(sum(len(part) for part in splits.values()), len(rows))
        self.assertEqual(sum(len(groups) for groups in membership.values()), 4)
        for left in membership:
            for right in membership:
                if left < right:
                    self.assertFalse(set(membership[left]) & set(membership[right]))
        for name, split in splits.items():
            self.assertTrue({row["group_id"] for row in split} <= set(membership[name]))

    def test_group_split_is_reproducible_for_the_same_seed(self):
        rows = [record(f"{group}-{i}", group, f"نمونه {group} {i}") for group in "abcdef" for i in range(2)]
        first, groups_first = split_by_group(rows, seed=91)
        second, groups_second = split_by_group(rows, seed=91)
        self.assertEqual(groups_first, groups_second)
        self.assertEqual({key: [r["id"] for r in value] for key, value in first.items()},
                         {key: [r["id"] for r in value] for key, value in second.items()})

    def test_group_split_requires_three_groups(self):
        rows = [record("a", "only-1", "الف"), record("b", "only-2", "ب")]
        with self.assertRaisesRegex(ValueError, "at least three distinct groups"):
            split_by_group(rows)

    def test_group_split_rejects_bad_fractions(self):
        rows = [record(str(i), str(i), f"متن {i}") for i in range(4)]
        with self.assertRaisesRegex(ValueError, "sum to 1"):
            split_by_group(rows, fractions=(0.7, 0.2, 0.2))

    def test_vocabulary_is_built_only_from_given_training_texts(self):
        vocab = train_word_vocabulary(["داده آموزش تکرار تکرار"], max_vocab_size=20)
        self.assertEqual(vocab[:4], list(SPECIAL_TOKENS))
        self.assertIn("آموزش", vocab)
        self.assertNotIn("آزمون‌ویژه", vocab)

    def test_vocabulary_frequency_limit_and_tie_break_are_deterministic(self):
        vocab = train_word_vocabulary(["زرد آبی زرد", "آبی سبز"], min_frequency=2, max_vocab_size=8)
        self.assertEqual(vocab, list(SPECIAL_TOKENS) + ["آبی", "زرد"])

    def test_tokenizer_unknown_and_special_token_contract(self):
        tokenizer = SimpleWordTokenizer.train(["سلام دنیا"], max_vocab_size=20)
        ids = tokenizer.encode("سلام ناشناخته", add_bos=True, add_eos=True)
        self.assertEqual(ids[0], tokenizer.token_to_id["<bos>"])
        self.assertEqual(ids[-1], tokenizer.token_to_id["<eos>"])
        self.assertEqual(ids[2], tokenizer.token_to_id["<unk>"])
        self.assertEqual(tokenizer.decode(ids), "سلام <unk>")

    def test_tokenizer_round_trip_vocabulary_save_and_load(self):
        tokenizer = SimpleWordTokenizer.train(["کتاب تازه کتاب"], max_vocab_size=30)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "nested" / "vocab.json"
            tokenizer.save(path)
            loaded = SimpleWordTokenizer.load(path)
            self.assertEqual(loaded.vocabulary, tokenizer.vocabulary)
            self.assertEqual(loaded.encode("کتاب تازه"), tokenizer.encode("کتاب تازه"))


class PipelineTests(unittest.TestCase):
    def test_pipeline_writes_splits_vocab_card_and_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "prepared"
            summary = prepare_dataset(SAMPLE, output, seed=40)
            self.assertEqual(summary["input_records"], 16)
            self.assertEqual(summary["retained_records"], 16)
            self.assertEqual(summary["exact_duplicates_removed"], 0)
            self.assertEqual(summary["tokenizer_fit_split"], "train")
            for name in ("train", "validation", "test"):
                self.assertTrue((output / f"{name}.jsonl").is_file())
            self.assertTrue((output / "vocab.json").is_file())
            self.assertTrue((output / "duplicates.json").is_file())
            self.assertTrue((output / "summary.json").is_file())
            self.assertTrue((output / "data_card.md").is_file())
            groups = [set(summary["split_groups"][name]) for name in ("train", "validation", "test")]
            self.assertFalse(groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
            self.assertEqual(sum(summary["split_counts"].values()), 16)
            card = (output / "data_card.md").read_text(encoding="utf-8")
            self.assertIn("فقط از متن train", card)
            self.assertIn("بررسی انسانی", card)

    def test_train_vocab_does_not_absorb_holdout_only_word(self):
        tokenizer = SimpleWordTokenizer.train(["واژهٔ آموزش"], max_vocab_size=20)
        self.assertNotIn("ویژه‌فقط‌آزمون", tokenizer.token_to_id)
        self.assertEqual(tokenizer.encode("ویژه‌فقط‌آزمون", add_bos=False, add_eos=False),
                         [tokenizer.token_to_id["<unk>"]])


if __name__ == "__main__":
    unittest.main()
