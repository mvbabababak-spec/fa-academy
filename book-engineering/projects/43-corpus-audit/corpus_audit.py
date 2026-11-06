"""Offline corpus release-screen demo for chapter 43.

This program writes a review ledger only. It does not decide whether data may
legally or ethically be used, does not delete records, and does not train a model.
It uses only Python's standard library and never fetches source URLs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
from typing import Sequence


REPORT_VERSION = 1
RIGHTS_STATUSES = frozenset({"demo-only", "pending", "reviewed", "excluded"})
REQUIRED_STRING_FIELDS = (
    "id", "source_id", "source_version", "captured_at", "license_expression",
    "rights_review_status", "intended_use", "language",
)
OPTIONAL_STRING_FIELDS = ("source_uri", "license_url", "rights_evidence_ref")
TOKEN_PATTERN = re.compile(r"[\w\u200c]+", flags=re.UNICODE)


def normalize_text(text: str) -> str:
    """Conservative comparison cleanup: NFC and whitespace collapse only."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(unicodedata.normalize("NFC", text).split())


def comparison_key(text: str) -> str:
    """Case-insensitive exact-match key; punctuation and Persian letter forms stay."""
    return normalize_text(text).casefold()


def word_tokens(text: str) -> list[str]:
    """A tiny Unicode word splitter for audit examples, not a Persian tokenizer."""
    return TOKEN_PATTERN.findall(normalize_text(text).casefold())


def _require_string(row: dict, key: str, line_number: int, allow_empty: bool = False) -> str:
    value = row.get(key)
    if not isinstance(value, str):
        raise ValueError(f"line {line_number}: field {key!r} must be a string")
    value = value.strip()
    if not value and not allow_empty:
        raise ValueError(f"line {line_number}: field {key!r} must be non-empty")
    return value


def validate_corpus_record(value: object, line_number: int) -> dict:
    """Check the sample schema while retaining unresolved rights as review flags."""
    if not isinstance(value, dict):
        raise ValueError(f"line {line_number}: each corpus JSONL row must be an object")
    row = dict(value)
    for key in REQUIRED_STRING_FIELDS:
        row[key] = _require_string(row, key, line_number)
    for key in OPTIONAL_STRING_FIELDS:
        row[key] = _require_string(row, key, line_number, allow_empty=True)
    row["text"] = _require_string(row, "text", line_number, allow_empty=True)
    if row["rights_review_status"] not in RIGHTS_STATUSES:
        allowed = ", ".join(sorted(RIGHTS_STATUSES))
        raise ValueError(f"line {line_number}: rights_review_status must be one of: {allowed}")
    try:
        date.fromisoformat(row["captured_at"][:10])
    except (TypeError, ValueError):
        raise ValueError(f"line {line_number}: captured_at must begin with an ISO date, e.g. 2026-11-06") from None
    return row


def validate_evaluation_record(value: object, line_number: int) -> dict:
    """Read a separate evaluation fixture; it is never merged into the corpus."""
    if not isinstance(value, dict):
        raise ValueError(f"evaluation line {line_number}: each JSONL row must be an object")
    row = dict(value)
    row["id"] = _require_string(row, "id", line_number)
    row["text"] = _require_string(row, "text", line_number)
    return row


def _load_jsonl(path: str | Path, validator) -> list[dict]:
    path = Path(path)
    records: list[dict] = []
    seen_ids: set[str] = set()
    try:
        stream = path.open("r", encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot open {path}: {exc}") from exc
    with stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON in {path.name} line {line_number}: {exc.msg}") from exc
            record = validator(value, line_number)
            if record["id"] in seen_ids:
                raise ValueError(f"duplicate id {record['id']!r} in {path.name} line {line_number}")
            seen_ids.add(record["id"])
            records.append(record)
    if not records:
        raise ValueError(f"{path.name} contains no records")
    return records


def load_corpus(path: str | Path) -> list[dict]:
    return _load_jsonl(path, validate_corpus_record)


def load_evaluation(path: str | Path) -> list[dict]:
    return _load_jsonl(path, validate_evaluation_record)


def _validate_integer(name: str, value: object, *, minimum: int = 1) -> int:
    """Reject booleans and fractional values before they reach range/slicing."""
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        qualifier = "non-negative" if minimum == 0 else "positive"
        raise ValueError(f"{name} must be a {qualifier} integer")
    return value


def quality_flags(text: str, min_characters: int = 64) -> list[str]:
    """Return review signals only; no flag automatically removes a record."""
    _validate_integer("min_characters", min_characters, minimum=0)
    flags: list[str] = []
    cleaned = normalize_text(text)
    if not cleaned:
        flags.append("empty_after_normalization")
    if len(cleaned) < min_characters:
        flags.append("below_min_characters")
    if "\ufffd" in text:
        flags.append("replacement_character_present")

    controls = [
        character for character in text
        if unicodedata.category(character) == "Cc" and character not in "\r\n\t"
    ]
    if controls and len(controls) / max(len(text), 1) > 0.01:
        flags.append("control_character_ratio_over_1pct")

    lines = [comparison_key(line) for line in text.splitlines() if line.strip()]
    if len(lines) >= 3:
        duplicate_count = len(lines) - len(set(lines))
        if duplicate_count / len(lines) >= 0.5:
            flags.append("repeated_lines_candidate")
    return flags


def _shingles(tokens: Sequence[str], size: int = 3) -> set[tuple[str, ...]]:
    _validate_integer("shingle size", size)
    return {tuple(tokens[index:index + size]) for index in range(max(0, len(tokens) - size + 1))}


def jaccard_similarity(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _validate_threshold(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0.0 < value <= 1.0:
        raise ValueError(f"{name} must be finite and in (0, 1]")
    return float(value)


def exact_duplicate_pairs(records: Sequence[dict]) -> list[dict]:
    by_key: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        key = comparison_key(record["text"])
        if key:
            by_key[key].append(record)
    pairs = []
    for key, group in by_key.items():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=lambda item: item["id"])
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        for left_index in range(len(ordered)):
            for right_index in range(left_index + 1, len(ordered)):
                pairs.append({
                    "left_id": ordered[left_index]["id"],
                    "right_id": ordered[right_index]["id"],
                    "match_type": "exact_normalized_candidate",
                    "content_sha256": digest,
                })
    return sorted(pairs, key=lambda item: (item["left_id"], item["right_id"]))


def near_duplicate_pairs(
    records: Sequence[dict], threshold: float = 0.70, min_tokens: int = 6, shingle_size: int = 3
) -> list[dict]:
    """Pairwise shingle-Jaccard candidate search for small offline examples only."""
    threshold = _validate_threshold("near-duplicate threshold", threshold)
    _validate_integer("shingle_size", shingle_size)
    _validate_integer("min_tokens", min_tokens)
    if min_tokens < shingle_size:
        raise ValueError("min_tokens must be at least shingle_size")
    cached = []
    for record in records:
        text_key = comparison_key(record["text"])
        tokens = word_tokens(record["text"])
        cached.append((record["id"], text_key, tokens, _shingles(tokens, shingle_size)))
    pairs = []
    for index, (left_id, left_key, left_tokens, left_shingles) in enumerate(cached):
        if len(left_tokens) < min_tokens or not left_shingles:
            continue
        for right_id, right_key, right_tokens, right_shingles in cached[index + 1:]:
            if left_key == right_key or len(right_tokens) < min_tokens or not right_shingles:
                continue
            score = jaccard_similarity(left_shingles, right_shingles)
            if score >= threshold:
                first, second = sorted((left_id, right_id))
                pairs.append({
                    "left_id": first,
                    "right_id": second,
                    "match_type": "near_duplicate_review_candidate",
                    "shingle_size": shingle_size,
                    "jaccard": round(score, 6),
                })
    return sorted(pairs, key=lambda item: (item["left_id"], item["right_id"]))


def _has_common_contiguous_window(left: Sequence[str], right: Sequence[str], window_size: int) -> bool:
    if window_size < 1 or min(len(left), len(right)) < window_size:
        return False
    right_windows = {tuple(right[index:index + window_size]) for index in range(len(right) - window_size + 1)}
    return any(
        tuple(left[index:index + window_size]) in right_windows
        for index in range(len(left) - window_size + 1)
    )


def evaluation_overlap_candidates(
    corpus: Sequence[dict],
    evaluation: Sequence[dict],
    near_threshold: float = 0.65,
    min_contiguous_tokens: int = 8,
    shingle_size: int = 3,
    min_tokens: int = 6,
) -> list[dict]:
    """Find exact, long-substring, or shingle-similarity candidates, not proof of exposure."""
    near_threshold = _validate_threshold("evaluation near-overlap threshold", near_threshold)
    _validate_integer("min_contiguous_tokens", min_contiguous_tokens)
    _validate_integer("shingle_size", shingle_size)
    _validate_integer("min_tokens", min_tokens)
    if min_tokens < shingle_size:
        raise ValueError("min_tokens must be at least shingle_size")
    matches = []
    for benchmark in evaluation:
        benchmark_key = comparison_key(benchmark["text"])
        benchmark_tokens = word_tokens(benchmark["text"])
        benchmark_shingles = _shingles(benchmark_tokens, shingle_size)
        for document in corpus:
            document_key = comparison_key(document["text"])
            document_tokens = word_tokens(document["text"])
            match_type = None
            score = None
            if benchmark_key and benchmark_key == document_key:
                match_type = "exact_surface_overlap_candidate"
                score = 1.0
            elif _has_common_contiguous_window(benchmark_tokens, document_tokens, min_contiguous_tokens):
                match_type = "long_contiguous_overlap_candidate"
            elif (
                len(benchmark_tokens) >= min_tokens
                and len(document_tokens) >= min_tokens
                and benchmark_shingles
            ):
                similarity = jaccard_similarity(benchmark_shingles, _shingles(document_tokens, shingle_size))
                if similarity >= near_threshold:
                    match_type = "near_overlap_review_candidate"
                    score = round(similarity, 6)
            if match_type:
                matches.append({
                    "evaluation_id": benchmark["id"],
                    "corpus_id": document["id"],
                    "match_type": match_type,
                    **({"jaccard": score} if score is not None else {}),
                })
    return sorted(matches, key=lambda item: (item["evaluation_id"], item["corpus_id"], item["match_type"]))


def _rights_review(record: dict, target_use: str) -> tuple[str, list[str]]:
    status = record["rights_review_status"]
    flags: list[str] = []
    if status == "demo-only":
        flags.append("synthetic_demo_not_a_permission")
    elif status == "pending":
        flags.append("human_rights_review_pending")
    elif status == "excluded":
        flags.append("excluded_by_declared_policy")
    else:
        flags.append("human_review_claim_not_machine_verified")

    if record["license_expression"].casefold() in {"noassertion", "none", "unknown"}:
        flags.append("license_expression_unresolved")
    if not record["source_uri"]:
        flags.append("source_uri_missing")
    if not record["license_url"]:
        flags.append("license_url_missing")
    if not record["rights_evidence_ref"]:
        flags.append("rights_evidence_reference_missing")
    if record["intended_use"] != target_use:
        flags.append("intended_use_mismatch")

    if status == "excluded":
        disposition = "excluded_by_declared_policy"
    elif status == "reviewed" and len(flags) == 1:
        disposition = "review_claim_complete_but_unverified"
    elif status == "demo-only":
        disposition = "fixture_only_not_cleared"
    else:
        disposition = "hold_for_human_review"
    return disposition, sorted(flags)


def audit_records(
    corpus: Sequence[dict],
    evaluation: Sequence[dict],
    *,
    target_use: str = "pretraining",
    min_characters: int = 64,
    near_threshold: float = 0.70,
    evaluation_threshold: float = 0.65,
    min_contiguous_tokens: int = 8,
) -> tuple[dict, dict]:
    if not isinstance(target_use, str) or not target_use.strip():
        raise ValueError("target_use must be a non-empty string")
    _validate_threshold("near-duplicate threshold", near_threshold)
    _validate_threshold("evaluation near-overlap threshold", evaluation_threshold)
    if min_characters < 0 or min_contiguous_tokens < 1:
        raise ValueError("minimum lengths must be non-negative (contiguous token count must be positive)")

    rows = sorted(corpus, key=lambda record: record["id"])
    eval_rows = sorted(evaluation, key=lambda record: record["id"])
    exact_pairs = exact_duplicate_pairs(rows)
    near_pairs = near_duplicate_pairs(rows, threshold=near_threshold)
    overlap_pairs = evaluation_overlap_candidates(
        rows,
        eval_rows,
        near_threshold=evaluation_threshold,
        min_contiguous_tokens=min_contiguous_tokens,
    )

    record_rows = []
    statuses: Counter[str] = Counter()
    languages: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    quality_counts: Counter[str] = Counter()
    review_required = 0
    excluded_count = 0
    for record in rows:
        disposition, rights_flags = _rights_review(record, target_use)
        flags = quality_flags(record["text"], min_characters=min_characters)
        quality_counts.update(flags)
        statuses[record["rights_review_status"]] += 1
        languages[record["language"]] += 1
        sources[record["source_id"]] += 1
        if disposition == "hold_for_human_review" or disposition == "fixture_only_not_cleared":
            review_required += 1
        if disposition == "excluded_by_declared_policy":
            excluded_count += 1
        canonical = normalize_text(record["text"])
        record_rows.append({
            "id": record["id"],
            "source_id": record["source_id"],
            "content_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "character_count": len(canonical),
            "word_count_proxy": len(word_tokens(record["text"])),
            "rights_review_status": record["rights_review_status"],
            "rights_disposition": disposition,
            "rights_flags": rights_flags,
            "quality_flags": flags,
        })

    summary = {
        "report_version": REPORT_VERSION,
        "corpus_documents": len(rows),
        "evaluation_items": len(eval_rows),
        "rights_status_counts": dict(sorted(statuses.items())),
        "manual_rights_review_required": review_required,
        "explicitly_excluded_records": excluded_count,
        "quality_flagged_records": sum(bool(row["quality_flags"]) for row in record_rows),
        "quality_flag_counts": dict(sorted(quality_counts.items())),
        "source_counts": dict(sorted(sources.items())),
        "language_counts": dict(sorted(languages.items())),
        "exact_duplicate_pairs": len(exact_pairs),
        "near_duplicate_review_candidates": len(near_pairs),
        "evaluation_overlap_candidates": len(overlap_pairs),
        "training_rows_exported": 0,
        "automatic_training_approval": False,
        "raw_text_in_report": False,
        "thresholds": {
            "min_characters_review_flag": min_characters,
            "near_duplicate_shingle_jaccard": near_threshold,
            "evaluation_shingle_jaccard": evaluation_threshold,
            "minimum_contiguous_evaluation_tokens": min_contiguous_tokens,
        },
    }
    report = {
        "report_version": REPORT_VERSION,
        "purpose": "offline review ledger; not legal approval, not a training export",
        "comparison_normalization": "Unicode NFC and whitespace collapse; exact key casefolds; punctuation retained",
        "target_use_claimed_by_policy": target_use,
        "automatic_training_approval": False,
        "raw_text_in_report": False,
        "records": record_rows,
        "exact_duplicate_candidates": exact_pairs,
        "near_duplicate_candidates": near_pairs,
        "evaluation_overlap_candidates": overlap_pairs,
        "summary": summary,
    }
    return report, summary


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def build_data_card(summary: dict) -> str:
    thresholds = summary["thresholds"]
    status_lines = [f"- `{name}`: {count}" for name, count in summary["rights_status_counts"].items()]
    quality_lines = [f"- `{name}`: {count}" for name, count in summary["quality_flag_counts"].items()] or ["- هیچ پرچم کیفیتی در این اجرای نمونه ثبت نشد."]
    return "\n".join([
        "# کارت ممیزی نمونهٔ فصل ۴۳",
        "",
        "> این سند فقط گزارش یک fixture آموزشی است؛ مجوز واقعی، رضایت، ناشناس‌سازی، کیفیت زبانی یا آماده‌بودن برای آموزش را تأیید نمی‌کند.",
        "",
        "## هدف و دامنه",
        "",
        f"- ردیف‌های پیکره: {summary['corpus_documents']}؛ موارد ارزیابی جدا: {summary['evaluation_items']}",
        "- دامنهٔ ادعاشده در سیاست نمونه: پیش‌آموزش؛ هیچ ردیفی از این fixture به مدل صادر نمی‌شود.",
        "- همهٔ جمله‌ها برای نمایش کد ساخته شده‌اند؛ `demo-only` مجوز نشر یا آموزش نیست.",
        "",
        "## منشأ و بررسی حقوق",
        "",
        *status_lines,
        f"- نیازمند بررسی انسانی طبق status/metadata نمونه: {summary['manual_rights_review_required']}",
        f"- صریحاً کنارگذاشته‌شده در نمونه: {summary['explicitly_excluded_records']}",
        "- برنامه متن مجوز را تفسیر یا URL را دریافت نمی‌کند و هیچ حق استفاده‌ای اعطا نمی‌کند.",
        "",
        "## کیفیت و تکرار",
        "",
        f"- ردیف‌های دارای دست‌کم یک heuristic flag: {summary['quality_flagged_records']}",
        *quality_lines,
        f"- پرچم کوتاهی متن از {thresholds['min_characters_review_flag']} نویسه کمتر؛ این فقط آستانهٔ تمرین است.",
        f"- exact duplicate candidate pairs: {summary['exact_duplicate_pairs']}",
        f"- near-duplicate review candidates (Jaccard روی {3}-gramها، threshold={thresholds['near_duplicate_shingle_jaccard']:.2f}): {summary['near_duplicate_review_candidates']}",
        "- هیچ رکوردی خودکار حذف یا ادغام نشده است.",
        "",
        "## آلودگی ارزیابی",
        "",
        f"- هم‌پوشانی‌های سطحیِ candidate: {summary['evaluation_overlap_candidates']}",
        f"- هم‌پوشانی پیوسته: حداقل {thresholds['minimum_contiguous_evaluation_tokens']} واژه؛ بررسی نزدیک: Jaccard روی 3-gramها.",
        "- candidate نه اثبات ورود به آموزش است و نه برآورد سوگیری نمره؛ شباهت معنایی/پارافریزها پوشش داده نمی‌شوند.",
        "",
        "## پردازش، نسخه و محدودیت",
        "",
        "- مقایسه: Unicode NFC و فشرده‌سازی فاصله‌ها؛ متن اصلی بازنویسی یا صادر نمی‌شود.",
        "- گزارش فقط شناسه، شمارش، پرچم و hash دارد؛ hash ناشناس‌سازی نیست و ممکن است امکان تطبیق متن را بدهد.",
        "- جست‌وجوی near-duplicate زوج‌به‌زوج و مناسب fixture کوچک است؛ برای وب‌مقیاس طراحی نشده.",
        "- زبان از فیلد manifest خوانده می‌شود؛ کد زبان را تشخیص یا کیفیت را رتبه‌بندی نمی‌کند.",
        "- وضعیت حقوقی، مجوز پلتفرم، حریم خصوصی، bias، پوشش، کیفیت موضوعی و حذف تکرار معنایی باید جداگانه و انسانی بررسی شوند.",
        "",
    ])


def audit_files(
    manifest_path: str | Path,
    evaluation_path: str | Path,
    output_dir: str | Path,
    *,
    target_use: str = "pretraining",
    min_characters: int = 64,
    near_threshold: float = 0.70,
    evaluation_threshold: float = 0.65,
    min_contiguous_tokens: int = 8,
) -> tuple[dict, dict]:
    corpus = load_corpus(manifest_path)
    evaluation = load_evaluation(evaluation_path)
    report, summary = audit_records(
        corpus,
        evaluation,
        target_use=target_use,
        min_characters=min_characters,
        near_threshold=near_threshold,
        evaluation_threshold=evaluation_threshold,
        min_contiguous_tokens=min_contiguous_tokens,
    )
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "audit.json", report)
    _write_json(output / "summary.json", summary)
    (output / "data_card.md").write_text(build_data_card(summary), encoding="utf-8")
    return report, summary


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Create an offline corpus audit ledger; no training export")
    parser.add_argument("--manifest", type=Path, default=root / "sample_corpus.jsonl")
    parser.add_argument("--evaluation", type=Path, default=root / "sample_evaluation.jsonl")
    parser.add_argument("--output", type=Path, default=root / "build")
    parser.add_argument("--target-use", default="pretraining")
    parser.add_argument("--min-characters", type=int, default=64)
    parser.add_argument("--near-threshold", type=float, default=0.70)
    parser.add_argument("--evaluation-threshold", type=float, default=0.65)
    parser.add_argument("--min-contiguous-tokens", type=int, default=8)
    args = parser.parse_args(argv)
    _, summary = audit_files(
        args.manifest,
        args.evaluation,
        args.output,
        target_use=args.target_use,
        min_characters=args.min_characters,
        near_threshold=args.near_threshold,
        evaluation_threshold=args.evaluation_threshold,
        min_contiguous_tokens=args.min_contiguous_tokens,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
    print("Audit only: no data was approved, deleted, downloaded, or exported for training.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
