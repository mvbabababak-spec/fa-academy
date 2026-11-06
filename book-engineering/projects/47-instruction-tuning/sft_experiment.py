"""Small, offline-first SFT data-contract and CPU fine-tuning demonstration.

The default audit mode never imports Transformers, loads a model, or accesses the
network. The optional training mode is a research smoke test on synthetic English
data and a revision-pinned Pythia checkpoint; it is not a quality benchmark.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
from typing import Any, Mapping, Sequence

MODEL_ID = "EleutherAI/pythia-14m"
MODEL_REVISION = "cf967c0a9a04383db6f7b1108d86b2962634b4ac"
MODEL_CARD_LICENSE = "apache-2.0"
MODEL_CARD_URL = "https://huggingface.co/EleutherAI/pythia-14m"
MODEL_CARD_REVIEWED = "2026-11-06"
REQUIRED_FIELDS = ("id", "source_id", "group_id", "prompt", "completion")
SPLIT_NAMES = ("train", "validation", "test")


def _require_positive_int(name: str, value: object, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _require_fraction(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number in (0, 1)")
    result = float(value)
    if not math.isfinite(result) or not 0.0 < result < 1.0:
        raise ValueError(f"{name} must be a finite number in (0, 1)")
    return result


def load_jsonl(path: str | Path) -> list[dict[str, str]]:
    """Load the minimal prompt/completion schema; never infer rights or quality."""
    path = Path(path)
    rows: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    try:
        stream = path.open("r", encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot open dataset {path}: {exc}") from exc
    with stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number}: each row must be a JSON object")
            row = dict(value)
            for field in REQUIRED_FIELDS:
                item = row.get(field)
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"line {line_number}: {field!r} must be a non-empty string")
                row[field] = item.strip()
            if row["id"] in seen_ids:
                raise ValueError(f"line {line_number}: duplicate id {row['id']!r}")
            seen_ids.add(row["id"])
            rows.append(row)
    if not rows:
        raise ValueError(f"dataset {path} contains no records")
    return rows


def split_by_group(
    records: Sequence[Mapping[str, str]],
    *,
    seed: int = 47,
    train_fraction: float = 0.8,
    validation_fraction: float = 0.1,
) -> dict[str, list[Mapping[str, str]]]:
    """Deterministically split group IDs so related records cannot cross splits."""
    _require_positive_int("seed", seed, minimum=0)
    train_fraction = _require_fraction("train_fraction", train_fraction)
    validation_fraction = _require_fraction("validation_fraction", validation_fraction)
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("train_fraction + validation_fraction must be less than 1")
    if not records:
        raise ValueError("records must not be empty")
    group_ids = sorted({str(record["group_id"]) for record in records})
    if len(group_ids) < 3:
        raise ValueError("at least three independent group_id values are required for train/validation/test")

    ordered_groups = sorted(
        group_ids,
        key=lambda group: (
            hashlib.sha256(f"{seed}\0{group}".encode("utf-8")).hexdigest(),
            group,
        ),
    )
    train_count = min(max(1, round(len(ordered_groups) * train_fraction)), len(ordered_groups) - 2)
    validation_count = min(
        max(1, round(len(ordered_groups) * validation_fraction)),
        len(ordered_groups) - train_count - 1,
    )
    train_groups = set(ordered_groups[:train_count])
    validation_groups = set(ordered_groups[train_count:train_count + validation_count])
    test_groups = set(ordered_groups[train_count + validation_count:])
    group_to_split = {
        **{group: "train" for group in train_groups},
        **{group: "validation" for group in validation_groups},
        **{group: "test" for group in test_groups},
    }
    result: dict[str, list[Mapping[str, str]]] = {name: [] for name in SPLIT_NAMES}
    for record in records:
        result[group_to_split[str(record["group_id"])]].append(record)
    if any(not result[name] for name in SPLIT_NAMES):
        raise ValueError("each split must contain at least one record")
    return result


def encode_prompt_completion(
    prompt: str,
    completion: str,
    tokenizer: Any,
    *,
    max_length: int = 128,
) -> dict[str, list[int]]:
    """Tokenize separately and mask prompt labels; never silently cut a target."""
    max_length = _require_positive_int("max_length", max_length, minimum=2)
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    if not isinstance(completion, str) or not completion.strip():
        raise ValueError("completion must be a non-empty string")
    eos_token_id = getattr(tokenizer, "eos_token_id", None)
    if eos_token_id is None:
        raise ValueError("tokenizer must define eos_token_id")

    prompt_ids = list(tokenizer.encode(prompt, add_special_tokens=False))
    completion_ids = list(tokenizer.encode(completion, add_special_tokens=False))
    bos_token_id = getattr(tokenizer, "bos_token_id", None)
    if bos_token_id is not None:
        prompt_ids.insert(0, int(bos_token_id))
    if not prompt_ids:
        raise ValueError("prompt produced no tokens")
    if not completion_ids:
        raise ValueError("completion produced no tokens")
    if completion_ids[-1] != int(eos_token_id):
        completion_ids.append(int(eos_token_id))

    prompt_budget = max_length - len(completion_ids)
    if prompt_budget < 1:
        raise ValueError("completion plus EOS leaves no room for a prompt token; increase max_length")
    if len(prompt_ids) > prompt_budget:
        # Keep the most recent context tokens; the completion is never truncated.
        prompt_ids = prompt_ids[-prompt_budget:]
    input_ids = [int(token) for token in prompt_ids + completion_ids]
    labels = [-100] * len(prompt_ids) + [int(token) for token in completion_ids]
    if len(input_ids) > max_length or not any(label != -100 for label in labels[1:]):
        raise ValueError("encoded example has no valid shifted completion targets")
    return {"input_ids": input_ids, "labels": labels}


def collate_features(features: Sequence[Mapping[str, Sequence[int]]], *, pad_token_id: int) -> dict[str, list[list[int]]]:
    """Right-pad IDs/masks; pad labels with -100 so padding adds no loss."""
    _require_positive_int("batch size", len(features))
    if isinstance(pad_token_id, bool) or not isinstance(pad_token_id, int):
        raise ValueError("pad_token_id must be an integer")
    max_length = max(len(feature["input_ids"]) for feature in features)
    batch_ids: list[list[int]] = []
    batch_masks: list[list[int]] = []
    batch_labels: list[list[int]] = []
    for feature in features:
        input_ids = [int(value) for value in feature["input_ids"]]
        labels = [int(value) for value in feature["labels"]]
        if not input_ids or len(input_ids) != len(labels):
            raise ValueError("each feature must have equally sized, non-empty input_ids and labels")
        padding = max_length - len(input_ids)
        batch_ids.append(input_ids + [pad_token_id] * padding)
        batch_masks.append([1] * len(input_ids) + [0] * padding)
        batch_labels.append(labels + [-100] * padding)
    return {"input_ids": batch_ids, "attention_mask": batch_masks, "labels": batch_labels}


def _dataset_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _split_counts(splits: Mapping[str, Sequence[Mapping[str, str]]]) -> dict[str, dict[str, int]]:
    return {
        name: {
            "records": len(splits[name]),
            "groups": len({str(record["group_id"]) for record in splits[name]}),
        }
        for name in SPLIT_NAMES
    }


def audit_dataset(dataset_path: str | Path, output_dir: str | Path, *, seed: int = 47) -> dict[str, Any]:
    """Validate JSONL and save counts only. Does not tokenize or train."""
    dataset_path = Path(dataset_path)
    rows = load_jsonl(dataset_path)
    splits = split_by_group(rows, seed=seed)
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "validated_only",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data": {
            "file_name": dataset_path.name,
            "sha256": _dataset_digest(dataset_path),
            "records": len(rows),
            "groups": len({row["group_id"] for row in rows}),
            "split_counts": _split_counts(splits),
            "contains_only_synthetic_demo_data": True,
        },
        "training_performed": False,
        "model_downloaded_or_loaded": False,
        "test_evaluations": 0,
        "interpretation": "Counts validate this public synthetic fixture only; they are not a model or data-quality result.",
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _encode_split(
    records: Sequence[Mapping[str, str]], tokenizer: Any, *, max_length: int
) -> list[dict[str, list[int]]]:
    return [
        encode_prompt_completion(record["prompt"], record["completion"], tokenizer, max_length=max_length)
        for record in records
    ]


def _torch_batch(features: Sequence[Mapping[str, Sequence[int]]], *, pad_token_id: int, torch: Any) -> dict[str, Any]:
    padded = collate_features(features, pad_token_id=pad_token_id)
    return {
        name: torch.tensor(values, dtype=torch.long, device="cpu")
        for name, values in padded.items()
    }


def _evaluate_nll(model: Any, features: Sequence[Mapping[str, Sequence[int]]], *, batch_size: int, pad_token_id: int, torch: Any) -> float:
    model.eval()
    weighted_loss = 0.0
    target_count = 0
    with torch.no_grad():
        for start in range(0, len(features), batch_size):
            batch = _torch_batch(features[start:start + batch_size], pad_token_id=pad_token_id, torch=torch)
            valid_targets = int((batch["labels"][:, 1:] != -100).sum().item())
            if valid_targets < 1:
                raise ValueError("evaluation batch has no shifted completion targets")
            output = model(**batch)
            loss = float(output.loss.detach().cpu().item())
            if not math.isfinite(loss):
                raise ValueError("non-finite evaluation loss")
            weighted_loss += loss * valid_targets
            target_count += valid_targets
    if target_count == 0:
        raise ValueError("evaluation split is empty")
    return weighted_loss / target_count


def train_pythia_demo(
    dataset_path: str | Path,
    output_dir: str | Path,
    *,
    seed: int = 47,
    epochs: int = 1,
    batch_size: int = 2,
    max_length: int = 128,
    learning_rate: float = 5e-5,
    cpu_threads: int = 1,
    allow_download: bool = False,
) -> dict[str, Any]:
    """Full-parameter CPU SFT smoke run; test is evaluated once, after training."""
    _require_positive_int("seed", seed, minimum=0)
    epochs = _require_positive_int("epochs", epochs)
    batch_size = _require_positive_int("batch_size", batch_size)
    max_length = _require_positive_int("max_length", max_length, minimum=2)
    cpu_threads = _require_positive_int("cpu_threads", cpu_threads)
    if isinstance(learning_rate, bool) or not isinstance(learning_rate, (int, float)) or not math.isfinite(float(learning_rate)) or learning_rate <= 0:
        raise ValueError("learning_rate must be finite and positive")

    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    try:
        import torch
        import transformers
        import huggingface_hub
        import tokenizers
        import safetensors
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "training requires the pinned model-demo dependencies; install requirements.txt "
            "and this folder's requirements-model-demo.txt"
        ) from exc

    dataset_path = Path(dataset_path)
    rows = load_jsonl(dataset_path)
    splits = split_by_group(rows, seed=seed)
    torch.manual_seed(seed)
    torch.set_num_threads(cpu_threads)
    local_files_only = not allow_download
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_files_only=local_files_only,
        trust_remote_code=False,
        use_fast=True,
    )
    if tokenizer.eos_token_id is None:
        raise RuntimeError("the pinned tokenizer has no EOS token")
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_files_only=local_files_only,
        trust_remote_code=False,
        use_safetensors=True,
        dtype=torch.float32,
    )
    model.config.pad_token_id = tokenizer.pad_token_id
    model.to("cpu")

    encoded = {name: _encode_split(splits[name], tokenizer, max_length=max_length) for name in SPLIT_NAMES}
    validation_before = _evaluate_nll(
        model, encoded["validation"], batch_size=batch_size,
        pad_token_id=int(tokenizer.pad_token_id), torch=torch,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(learning_rate), weight_decay=0.0)
    update_count = 0
    for epoch in range(epochs):
        order = list(range(len(encoded["train"])))
        random.Random(seed + epoch).shuffle(order)
        model.train()
        for start in range(0, len(order), batch_size):
            selected = [encoded["train"][index] for index in order[start:start + batch_size]]
            batch = _torch_batch(selected, pad_token_id=int(tokenizer.pad_token_id), torch=torch)
            optimizer.zero_grad(set_to_none=True)
            output = model(**batch)
            loss = output.loss
            if not bool(torch.isfinite(loss).item()):
                raise ValueError(f"non-finite training loss at update {update_count + 1}")
            loss.backward()
            optimizer.step()
            update_count += 1

    validation_after = _evaluate_nll(
        model, encoded["validation"], batch_size=batch_size,
        pad_token_id=int(tokenizer.pad_token_id), torch=torch,
    )
    # The held-out public fixture split is inspected once, after all training choices.
    test_after = _evaluate_nll(
        model, encoded["test"], batch_size=batch_size,
        pad_token_id=int(tokenizer.pad_token_id), torch=torch,
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_dir = output_dir / "model"
    tokenizer_dir = output_dir / "tokenizer"
    model.save_pretrained(model_dir, safe_serialization=True)
    tokenizer.save_pretrained(tokenizer_dir)

    split_counts = _split_counts(splits)
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "completed_smoke_run",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": {
            "id": MODEL_ID,
            "revision": MODEL_REVISION,
            "card_license_metadata": MODEL_CARD_LICENSE,
            "model_card": MODEL_CARD_URL,
            "card_reviewed": MODEL_CARD_REVIEWED,
            "license_and_training_data_terms_independently_verified": False,
            "human_facing_or_product_deployment_claim": False,
        },
        "runtime": {
            "python": sys.version.split()[0],
            "torch": str(torch.__version__),
            "transformers": str(transformers.__version__),
            "huggingface_hub": str(huggingface_hub.__version__),
            "tokenizers": str(tokenizers.__version__),
            "safetensors": str(safetensors.__version__),
            "device": "cpu",
            "cpu_threads": cpu_threads,
            "dtype": "float32",
        },
        "data": {
            "file_name": dataset_path.name,
            "sha256": _dataset_digest(dataset_path),
            "records": len(rows),
            "groups": len({row["group_id"] for row in rows}),
            "split_counts": split_counts,
            "contains_only_synthetic_demo_data": True,
            "dataset_upload_implemented_by_this_script": False,
        },
        "method": {
            "objective": "causal next-token loss on completion tokens only",
            "prompt_labels": -100,
            "padding_labels": -100,
            "training": "full-parameter supervised fine-tuning",
            "chat_template_used": False,
            "evaluation_policy": "validation before and after; public test split once after training",
        },
        "config": {
            "seed": seed,
            "epochs": epochs,
            "batch_size": batch_size,
            "max_length": max_length,
            "learning_rate": float(learning_rate),
            "optimizer": "AdamW",
            "weight_decay": 0.0,
            "network_download_allowed_for_this_run": bool(allow_download),
        },
        "metrics": {
            "optimizer_updates": update_count,
            "validation_nll_before": validation_before,
            "validation_nll_after": validation_after,
            "test_nll_after": test_after,
            "test_evaluations": 1,
        },
        "interpretation": (
            "A CPU pipeline smoke test on a tiny public synthetic English fixture. "
            "Loss values are not a benchmark, quality claim, Persian result, or deployment recommendation."
        ),
    }
    (output_dir / "run.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit a prompt/completion fixture or run a small pinned SFT demo")
    parser.add_argument("--mode", choices=("audit", "train"), default="audit")
    parser.add_argument("--data", type=Path, default=Path(__file__).with_name("sample_sft.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/ch47-sft-demo"))
    parser.add_argument("--seed", type=int, default=47)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    parser.add_argument("--cpu-threads", type=int, default=1)
    parser.add_argument(
        "--allow-download", action="store_true",
        help="explicitly allow downloading the revision-pinned model/tokenizer; default mode is cache-only",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.mode == "audit":
        report = audit_dataset(args.data, args.output, seed=args.seed)
    else:
        report = train_pythia_demo(
            args.data,
            args.output,
            seed=args.seed,
            epochs=args.epochs,
            batch_size=args.batch_size,
            max_length=args.max_length,
            learning_rate=args.learning_rate,
            cpu_threads=args.cpu_threads,
            allow_download=args.allow_download,
        )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
