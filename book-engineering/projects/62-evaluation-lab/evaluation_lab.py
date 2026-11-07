"""Small, deterministic audit helpers for an explicitly synthetic benchmark fixture.

This module is teaching code, not a production evaluator. It uses only the Python
standard library and deliberately labels overlap results as review flags, not proof
of training-data contamination.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import re
import sys
import unicodedata
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parent
VALID_SPLITS = {"train", "validation", "test"}
LABELS = (0, 1)
REQUIRED_FIELDS = {"case_id", "group_id", "split", "prompt", "reference", "baseline", "candidate"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number} must be a JSON object")
            rows.append(value)
    return rows


def validate_rows(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    """Validate schema, unique cases, labels, and group-disjoint data splits."""
    if not rows:
        raise ValueError("benchmark fixture must contain at least one case")
    seen: set[str] = set()
    group_split: dict[str, str] = {}
    counts = {split: 0 for split in sorted(VALID_SPLITS)}
    for index, row in enumerate(rows):
        missing = REQUIRED_FIELDS - row.keys()
        if missing:
            raise ValueError(f"row {index} is missing fields: {sorted(missing)}")
        case_id = row["case_id"]
        group_id = row["group_id"]
        split = row["split"]
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"row {index} has an empty or non-string case_id")
        if not isinstance(group_id, str) or not group_id.strip():
            raise ValueError(f"row {index} has an empty or non-string group_id")
        if case_id in seen:
            raise ValueError(f"duplicate case_id: {case_id}")
        seen.add(case_id)
        if split not in VALID_SPLITS:
            raise ValueError(f"unknown split {split!r} for case {case_id}")
        previous = group_split.setdefault(group_id, split)
        if previous != split:
            raise ValueError(f"group {group_id!r} crosses splits {previous!r} and {split!r}")
        counts[split] += 1
        if not isinstance(row["prompt"], str) or not row["prompt"].strip():
            raise ValueError(f"case {case_id} has an empty prompt")
        for field in ("reference", "baseline", "candidate"):
            value = row[field]
            if isinstance(value, bool) or value not in LABELS:
                raise ValueError(f"case {case_id} has invalid binary label in {field}: {value!r}")
    return counts


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion; not cluster-adjusted."""
    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("require 0 <= successes <= total and total > 0")
    p = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    margin = z * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total))) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def classification_metrics(truth: Sequence[int], predictions: Sequence[int]) -> dict[str, Any]:
    """Return accuracy, macro-F1, per-class scores, and a Wilson interval."""
    if len(truth) != len(predictions) or not truth:
        raise ValueError("truth and predictions must have equal, nonzero length")
    if any(isinstance(value, bool) or not isinstance(value, int) or value not in LABELS for value in (*truth, *predictions)):
        raise ValueError("labels must be integer 0 or 1")
    per_class: dict[str, dict[str, float | int]] = {}
    f1_values: list[float] = []
    for label in LABELS:
        tp = sum(actual == label and predicted == label for actual, predicted in zip(truth, predictions))
        fp = sum(actual != label and predicted == label for actual, predicted in zip(truth, predictions))
        fn = sum(actual == label and predicted != label for actual, predicted in zip(truth, predictions))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        support = sum(actual == label for actual in truth)
        per_class[str(label)] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
        f1_values.append(f1)
    correct = sum(actual == predicted for actual, predicted in zip(truth, predictions))
    low, high = wilson_interval(correct, len(truth))
    return {
        "n": len(truth),
        "correct": correct,
        "accuracy": correct / len(truth),
        "accuracy_wilson_95": [low, high],
        "macro_f1": sum(f1_values) / len(f1_values),
        "per_class": per_class,
    }


def paired_group_bootstrap(
    rows: Sequence[dict[str, Any]], *, repetitions: int = 2000, seed: int = 62
) -> dict[str, Any]:
    """Bootstrap paired accuracy difference by resampling whole group clusters."""
    if repetitions < 100:
        raise ValueError("use at least 100 bootstrap repetitions")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["group_id"]].append(row)
    group_ids = sorted(groups)
    if len(group_ids) < 2:
        raise ValueError("group bootstrap requires at least two groups")
    observed = sum(r["candidate"] == r["reference"] for r in rows) / len(rows) - sum(
        r["baseline"] == r["reference"] for r in rows
    ) / len(rows)
    rng = random.Random(seed)
    deltas: list[float] = []
    for _ in range(repetitions):
        sampled_ids = [rng.choice(group_ids) for _ in group_ids]
        sample = [row for group_id in sampled_ids for row in groups[group_id]]
        base = sum(r["baseline"] == r["reference"] for r in sample) / len(sample)
        candidate = sum(r["candidate"] == r["reference"] for r in sample) / len(sample)
        deltas.append(candidate - base)
    deltas.sort()

    def percentile(q: float) -> float:
        position = (len(deltas) - 1) * q
        lo = math.floor(position)
        hi = math.ceil(position)
        if lo == hi:
            return deltas[lo]
        return deltas[lo] * (hi - position) + deltas[hi] * (position - lo)

    return {
        "groups": len(group_ids),
        "repetitions": repetitions,
        "seed": seed,
        "observed_candidate_minus_baseline_accuracy": observed,
        "percentile_95_interval": [percentile(0.025), percentile(0.975)],
        "bootstrap_fraction_delta_positive": sum(value > 0 for value in deltas) / repetitions,
        "warning": "Fixture-sized descriptive bootstrap; not a significance claim or a substitute for a prespecified study.",
    }


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def _token_jaccard(left: str, right: str) -> float:
    a = set(_normalize_text(left).split())
    b = set(_normalize_text(right).split())
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def screen_for_overlap(
    evaluation_texts: Sequence[str], training_texts: Sequence[str], *, threshold: float = 0.8
) -> list[dict[str, Any]]:
    """Flag exact/near overlaps for manual review; never infer training provenance."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    normalized_training: dict[str, list[int]] = defaultdict(list)
    for index, text in enumerate(training_texts):
        normalized_training[_normalize_text(text)].append(index)
    output: list[dict[str, Any]] = []
    for eval_index, text in enumerate(evaluation_texts):
        normalized = _normalize_text(text)
        exact = normalized_training.get(normalized, []) if normalized else []
        best_score = 0.0
        best_training_index: int | None = None
        for train_index, train_text in enumerate(training_texts):
            score = _token_jaccard(text, train_text)
            if score > best_score:
                best_score, best_training_index = score, train_index
        flagged = bool(exact) or best_score >= threshold
        reason = "normalized_exact_match" if exact else ("high_token_jaccard_review" if flagged else "no_flag")
        output.append({
            "evaluation_index": eval_index,
            "flagged_for_review": flagged,
            "reason": reason,
            "exact_training_indices": exact,
            "best_token_jaccard": best_score,
            "best_training_index": best_training_index,
            "interpretation": "Overlap is a review lead only; it does not establish whether a model trained on this text.",
        })
    return output


def pairwise_percent_agreement(votes_by_case: dict[str, Sequence[int]]) -> dict[str, Any]:
    """Uncorrected pairwise agreement; report counts and disagreements, not only a score."""
    agreements = 0
    comparisons = 0
    items_with_votes = 0
    for votes in votes_by_case.values():
        if len(votes) < 2:
            continue
        items_with_votes += 1
        for left, right in combinations(votes, 2):
            comparisons += 1
            agreements += left == right
    return {
        "items_with_at_least_two_votes": items_with_votes,
        "pair_comparisons": comparisons,
        "pair_agreements": agreements,
        "percent_agreement": agreements / comparisons if comparisons else None,
        "warning": "Raw pairwise agreement is not chance-corrected and is not a measure of label validity.",
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_fixture() -> dict[str, Any]:
    data_path = ROOT / "sample_evaluation.jsonl"
    rows = load_jsonl(data_path)
    split_counts = validate_rows(rows)
    test_rows = [row for row in rows if row["split"] == "test"]
    corpus_path = ROOT / "training_corpus_fixture.txt"
    training_texts = [line.strip() for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    vote_path = ROOT / "human_votes_fixture.json"
    votes = json.loads(vote_path.read_text(encoding="utf-8"))
    return {
        "scope": "Synthetic, hand-authored teaching fixture only; no external benchmark or model was used.",
        "fixture_sha256": {
            data_path.name: sha256_file(data_path),
            corpus_path.name: sha256_file(corpus_path),
            vote_path.name: sha256_file(vote_path),
        },
        "split_counts": split_counts,
        "test_case_count": len(test_rows),
        "baseline": classification_metrics(
            [row["reference"] for row in test_rows], [row["baseline"] for row in test_rows]
        ),
        "candidate": classification_metrics(
            [row["reference"] for row in test_rows], [row["candidate"] for row in test_rows]
        ),
        "paired_group_bootstrap": paired_group_bootstrap(test_rows),
        "human_vote_fixture": pairwise_percent_agreement(votes),
        "overlap_screen": screen_for_overlap([row["prompt"] for row in test_rows], training_texts),
        "limitations": [
            "The labels, predictions, annotator votes, and corpus lines are fabricated for teaching.",
            "The test contains six cases in three groups; intervals and bootstrap output are unstable and illustrative.",
            "Wilson intervals assume independent Bernoulli trials; this code does not make that assumption valid for clustered or distribution-shifted data.",
            "Overlap flags are heuristics and cannot prove contamination or prove its absence.",
            "No human annotators, language model, benchmark, deployment workload, or sensitive data were used.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results.json")
    args = parser.parse_args()
    result = run_fixture()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "test_cases": result["test_case_count"],
        "baseline_accuracy": result["baseline"]["accuracy"],
        "candidate_accuracy": result["candidate"]["accuracy"],
        "limitations": "synthetic fixture only; see results.json",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
