"""A rights-aware, deterministic tiny-text corpus pipeline for chapter 40.

Standard-library only. The sample pipeline is educational, not a legal review,
privacy guarantee, or production-quality near-duplicate detector.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import random
import re
import unicodedata
from typing import Iterable, Sequence


ALLOWED_LICENSES = frozenset({"CC0-1.0", "CC-BY-4.0", "PUBLIC-DOMAIN", "SELF-CREATED"})
REQUIRED_FIELDS = frozenset({
    "id", "group_id", "text", "source", "license", "attribution",
    "language", "acquired_at", "rights_note",
})
SPECIAL_TOKENS = ("<pad>", "<unk>", "<bos>", "<eos>")
TOKEN_PATTERN = re.compile(r"[\w\u200c]+|[^\w\s]", flags=re.UNICODE)
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\w)\+?\d[\d ().-]{7,}\d(?!\w)")
SPLIT_NAMES = ("train", "validation", "test")
NORMALIZATION_NOTE = "Unicode NFC and whitespace collapse; Persian ZWNJ retained"


def normalize_text(text: str) -> str:
    """Normalize canonical Unicode composition and whitespace conservatively."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(unicodedata.normalize("NFC", text).split())


def sensitive_pattern_matches(text: str) -> list[str]:
    """Return heuristic flags only; absence of flags does not prove text is safe."""
    matches = []
    if EMAIL_PATTERN.search(text):
        matches.append("email-like")
    if PHONE_PATTERN.search(text):
        matches.append("phone-like")
    return matches


def _nonempty_string(record: dict, key: str, line_number: int | None) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        where = f" on line {line_number}" if line_number is not None else ""
        raise ValueError(f"field {key!r} must be a non-empty string{where}")
    return value.strip()


def validate_record(record: object, line_number: int | None = None) -> dict:
    """Validate required provenance fields and return a normalized copy."""
    where = f"line {line_number}: " if line_number is not None else ""
    if not isinstance(record, dict):
        raise ValueError(f"{where}each JSONL row must be an object")
    missing = sorted(REQUIRED_FIELDS - record.keys())
    if missing:
        raise ValueError(f"{where}missing required fields: {', '.join(missing)}")

    checked = dict(record)
    for key in REQUIRED_FIELDS - {"text"}:
        checked[key] = _nonempty_string(checked, key, line_number)

    if checked["license"] not in ALLOWED_LICENSES:
        raise ValueError(
            f"{where}license {checked['license']!r} is outside this demo's allowlist; "
            "review rights and update policy deliberately"
        )
    if checked["license"] == "CC-BY-4.0":
        if not checked["attribution"] or not checked["source"].startswith(("https://", "http://")):
            raise ValueError(f"{where}CC-BY-4.0 rows require an attribution and source URL")
    if checked["license"] == "SELF-CREATED" and not checked["rights_note"]:
        raise ValueError(f"{where}self-created rows need a rights_note")

    try:
        date.fromisoformat(checked["acquired_at"][:10])
    except (TypeError, ValueError):
        raise ValueError(f"{where}acquired_at must begin with an ISO date such as 2026-11-05") from None

    normalized = normalize_text(checked["text"])
    if not normalized:
        raise ValueError(f"{where}text is empty after normalization")
    matches = sensitive_pattern_matches(normalized)
    if matches:
        raise ValueError(
            f"{where}possible sensitive pattern {', '.join(matches)}; review and redact "
            "before adding text (the heuristic is not exhaustive)"
        )
    checked["text"] = normalized
    checked["normalized_text_sha256"] = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return checked


def load_manifest(path: str | Path) -> list[dict]:
    """Read UTF-8 JSONL and validate it without fetching external resources."""
    path = Path(path)
    rows: list[dict] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            row = validate_record(raw, line_number)
            if row["id"] in seen_ids:
                raise ValueError(f"duplicate record id {row['id']!r} on line {line_number}")
            seen_ids.add(row["id"])
            rows.append(row)
    if not rows:
        raise ValueError(f"manifest {path} contains no records")
    return rows


def deduplicate_records(records: Sequence[dict]) -> tuple[list[dict], list[dict]]:
    """Remove exact normalized-text duplicates while preserving an audit trail."""
    unique: list[dict] = []
    first_by_hash: dict[str, dict] = {}
    duplicates: list[dict] = []
    for record in records:
        normalized = normalize_text(record["text"])
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        first = first_by_hash.get(digest)
        if first is None:
            copy = dict(record)
            copy["text"] = normalized
            copy["normalized_text_sha256"] = digest
            first_by_hash[digest] = copy
            unique.append(copy)
        else:
            duplicates.append({
                "duplicate_id": record["id"],
                "kept_id": first["id"],
                "reason": "exact normalized text hash matched",
                "duplicate_source": record["source"],
                "kept_source": first["source"],
                "duplicate_group_id": record["group_id"],
                "kept_group_id": first["group_id"],
                "duplicate_license": record["license"],
                "kept_license": first["license"],
                "duplicate_attribution": record["attribution"],
                "kept_attribution": first["attribution"],
                "duplicate_record_metadata": {key: value for key, value in record.items() if key != "text"},
                "kept_record_metadata": {key: value for key, value in first.items() if key != "text"},
                "normalized_text_sha256": digest,
            })
    return unique, duplicates


def _group_counts(group_count: int, fractions: Sequence[float]) -> list[int]:
    if len(fractions) != 3 or any(not isinstance(x, (int, float)) for x in fractions):
        raise ValueError("fractions must contain train, validation, test values")
    values = [float(x) for x in fractions]
    if any(not math.isfinite(x) or x <= 0 for x in values) or not math.isclose(sum(values), 1.0, abs_tol=1e-9):
        raise ValueError("split fractions must be positive and sum to 1")
    raw = [group_count * x for x in values]
    counts = [math.floor(x) for x in raw]
    remainder_order = sorted(range(3), key=lambda i: (raw[i] - counts[i], -i), reverse=True)
    for i in remainder_order[: group_count - sum(counts)]:
        counts[i] += 1
    # A tiny corpus must still reserve at least one independent group per split.
    for i in range(3):
        if counts[i] == 0:
            donors = [j for j in range(3) if counts[j] > 1]
            if not donors:
                raise ValueError("at least three distinct groups are required for train/validation/test")
            donor = max(donors, key=lambda j: counts[j])
            counts[donor] -= 1
            counts[i] += 1
    return counts


def split_by_group(
    records: Sequence[dict],
    fractions: Sequence[float] = (0.8, 0.1, 0.1),
    seed: int = 40,
) -> tuple[dict[str, list[dict]], dict[str, list[str]]]:
    """Split by source/story group so related records never cross partitions."""
    groups = sorted({record["group_id"] for record in records})
    if len(groups) < 3:
        raise ValueError("at least three distinct groups are required for train/validation/test")
    counts = _group_counts(len(groups), fractions)
    shuffled = list(groups)
    random.Random(seed).shuffle(shuffled)
    assignment: dict[str, str] = {}
    offset = 0
    group_membership: dict[str, list[str]] = {}
    for name, count in zip(SPLIT_NAMES, counts):
        current = shuffled[offset: offset + count]
        offset += count
        group_membership[name] = sorted(current)
        assignment.update({group_id: name for group_id in current})
    splits = {name: [] for name in SPLIT_NAMES}
    for record in records:
        splits[assignment[record["group_id"]]].append(record)
    return splits, group_membership


def tokenize_words(text: str) -> list[str]:
    """A deliberately simple Unicode word/punctuation tokenizer; keeps ZWNJ."""
    return TOKEN_PATTERN.findall(normalize_text(text))


def train_word_vocabulary(
    training_texts: Iterable[str],
    min_frequency: int = 1,
    max_vocab_size: int = 10_000,
) -> list[str]:
    """Learn a deterministic word-level vocabulary from training texts only."""
    if min_frequency < 1:
        raise ValueError("min_frequency must be at least 1")
    if max_vocab_size < len(SPECIAL_TOKENS):
        raise ValueError(f"max_vocab_size must be at least {len(SPECIAL_TOKENS)}")
    counts: Counter[str] = Counter()
    for text in training_texts:
        counts.update(tokenize_words(text))
    candidates = [
        (token, frequency)
        for token, frequency in counts.items()
        if token not in SPECIAL_TOKENS and frequency >= min_frequency
    ]
    candidates.sort(key=lambda item: (-item[1], item[0]))
    room = max_vocab_size - len(SPECIAL_TOKENS)
    return list(SPECIAL_TOKENS) + [token for token, _ in candidates[:room]]


class SimpleWordTokenizer:
    """Small educational tokenizer; decoding joins tokens, not original spacing."""

    def __init__(self, vocabulary: Sequence[str]):
        self.vocabulary = list(vocabulary)
        if self.vocabulary[:len(SPECIAL_TOKENS)] != list(SPECIAL_TOKENS):
            raise ValueError("vocabulary must start with the four declared special tokens")
        if len(self.vocabulary) != len(set(self.vocabulary)):
            raise ValueError("vocabulary tokens must be unique")
        self.token_to_id = {token: index for index, token in enumerate(self.vocabulary)}

    @classmethod
    def train(
        cls,
        training_texts: Iterable[str],
        min_frequency: int = 1,
        max_vocab_size: int = 10_000,
    ) -> "SimpleWordTokenizer":
        return cls(train_word_vocabulary(training_texts, min_frequency, max_vocab_size))

    def encode(self, text: str, add_bos: bool = True, add_eos: bool = True) -> list[int]:
        ids = [self.token_to_id["<bos>"]] if add_bos else []
        ids.extend(self.token_to_id.get(token, self.token_to_id["<unk>"]) for token in tokenize_words(text))
        if add_eos:
            ids.append(self.token_to_id["<eos>"])
        return ids

    def decode(self, ids: Iterable[int], skip_special: bool = True) -> str:
        tokens = []
        for token_id in ids:
            if not isinstance(token_id, int) or token_id < 0 or token_id >= len(self.vocabulary):
                raise ValueError(f"token id {token_id!r} is outside this vocabulary")
            token = self.vocabulary[token_id]
            if skip_special and token in {"<pad>", "<bos>", "<eos>"}:
                continue
            tokens.append(token)
        return " ".join(tokens)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format_version": 1,
            "kind": "educational-word-level-tokenizer",
            "normalization": NORMALIZATION_NOTE,
            "special_tokens": list(SPECIAL_TOKENS),
            "vocabulary": self.vocabulary,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "SimpleWordTokenizer":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("format_version") != 1 or payload.get("kind") != "educational-word-level-tokenizer":
            raise ValueError("unsupported tokenizer file format")
        if payload.get("special_tokens") != list(SPECIAL_TOKENS):
            raise ValueError("special token contract does not match this implementation")
        return cls(payload["vocabulary"])


def _write_jsonl(path: Path, rows: Sequence[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _write_data_card(path: Path, summary: dict) -> None:
    licenses = ", ".join(f"`{name}`: {count}" for name, count in sorted(summary["license_counts"].items()))
    lines = [
        "# کارت دادهٔ نمونهٔ فصل ۴۰",
        "",
        "- **هدف:** ساخت ورودی کوچک و قابل‌بازتولید برای آموزش آزمایشی فصل ۴۱؛ نه benchmark و نه دادهٔ مناسب محصول.",
        "- **ترکیب:** متن‌های فارسی خودنگاشتهٔ نمونه؛ هیچ فایل یا صفحهٔ وبی در اجرای پیش‌فرض دریافت نمی‌شود.",
        f"- **نسخهٔ pipeline:** 1؛ تعداد رکوردهای پذیرفته‌شده پس از حذف تکرار: {summary['retained_records']}.",
        f"- **مجوزهای ثبت‌شده در manifest:** {licenses or 'هیچ'}.",
        "- **پاک‌سازی:** Unicode NFC و فشرده‌سازی whitespace؛ نیم‌فاصله حفظ می‌شود؛ متن خام این نمونه در `sample_corpus.jsonl` می‌ماند.",
        f"- **تقسیم:** گروه منبعی با seed={summary['seed']}؛ نسبت‌ها برای نمونهٔ کوچک تقریبی‌اند؛ گروه‌ها بین splitها مشترک نیستند.",
        "- **واژگان:** فقط از متن train ساخته شده؛ validation/test برای fit کردن tokenizer استفاده نشده‌اند.",
        "- **حریم خصوصی:** آشکارساز ایمیل/تلفن چند الگوی ساده را رد می‌کند، اما جامع نیست؛ بررسی انسانی پیش از هر استفاده لازم است.",
        "- **محدودیت‌ها:** نمونه کوچک و خودساخته است؛ اندازه/پوشش زبان را نمایندگی نمی‌کند؛ حذف تکرار نزدیک و بررسی مجوز خودکار نیست.",
        "- **کاربرد مجاز پروژه:** تمرین pipeline محلی. برای توزیع یا استفادهٔ دیگر، حقوق، attribution، حریم خصوصی و شرایط منبع را جداگانه بررسی کنید.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def prepare_dataset(
    manifest_path: str | Path,
    output_dir: str | Path,
    seed: int = 40,
    fractions: Sequence[float] = (0.8, 0.1, 0.1),
    min_frequency: int = 1,
    max_vocab_size: int = 10_000,
) -> dict:
    """Run validation, exact deduplication, group splitting, and train-only vocab fit."""
    records = load_manifest(manifest_path)
    unique, duplicates = deduplicate_records(records)
    splits, group_membership = split_by_group(unique, fractions=fractions, seed=seed)
    tokenizer = SimpleWordTokenizer.train(
        (record["text"] for record in splits["train"]),
        min_frequency=min_frequency,
        max_vocab_size=max_vocab_size,
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in splits.items():
        _write_jsonl(output_dir / f"{name}.jsonl", rows)
    tokenizer.save(output_dir / "vocab.json")
    (output_dir / "duplicates.json").write_text(
        json.dumps(duplicates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    license_counts = dict(sorted(Counter(row["license"] for row in unique).items()))
    summary = {
        "pipeline_version": 1,
        "seed": seed,
        "normalization": NORMALIZATION_NOTE,
        "input_records": len(records),
        "retained_records": len(unique),
        "exact_duplicates_removed": len(duplicates),
        "split_counts": {name: len(rows) for name, rows in splits.items()},
        "split_group_counts": {name: len(group_membership[name]) for name in SPLIT_NAMES},
        "split_groups": group_membership,
        "license_counts": license_counts,
        "tokenizer_vocabulary_size": len(tokenizer.vocabulary),
        "tokenizer_fit_split": "train",
        "sensitive_pattern_scan": "heuristic email/phone patterns only; manual review still required",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_data_card(output_dir / "data_card.md", summary)
    return summary


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Prepare a tiny rights-documented text corpus")
    parser.add_argument("--manifest", type=Path, default=root / "sample_corpus.jsonl")
    parser.add_argument("--output", type=Path, default=root / "build")
    parser.add_argument("--seed", type=int, default=40)
    args = parser.parse_args()
    summary = prepare_dataset(args.manifest, args.output, seed=args.seed)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
