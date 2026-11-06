"""Run a tiny, offline Hugging Face data-to-CPU-training smoke test.

The project reads only its checked-in synthetic JSONL fixture. It trains a
byte-pair tokenizer on the train split, maps both splits to token IDs, pads
batches, initializes a small random BERT from config, and takes fixed CPU steps
through Accelerate. It never contacts the Hub or loads pretrained weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_DATASETS_DISABLE_PROGRESS_BARS"] = "1"

import accelerate
import datasets
import tokenizers
import torch
import transformers
from accelerate import Accelerator
from datasets import Dataset, DatasetDict, Features, Value, disable_progress_bar
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from tokenizers.trainers import BpeTrainer
from torch.utils.data import DataLoader
from transformers import (
    BertConfig,
    BertForSequenceClassification,
    DataCollatorWithPadding,
    PreTrainedTokenizerFast,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = ROOT / "sample_data.jsonl"
DEFAULT_MANIFEST = ROOT / "fixture_manifest.json"
DEFAULT_OUTPUT = ROOT / "results.json"
FIXTURE_ID = "v4-ch12-synthetic-text-pipeline-v1"
MAX_LENGTH = 24
BATCH_SIZE = 2
VOCAB_SIZE = 96
SPECIAL_TOKENS = ("[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]")
FEATURES = Features(
    {
        "example_id": Value("string"),
        "group_id": Value("string"),
        "split": Value("string"),
        "text": Value("string"),
        "label": Value("int64"),
    }
)


class PipelineInputError(ValueError):
    """Raised when the synthetic fixture or its manifest is invalid."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PipelineInputError(f"cannot read fixture manifest: {error}") from error
    if not isinstance(manifest, dict):
        raise PipelineInputError("fixture manifest must be a JSON object")
    if manifest.get("schema_version") != 1 or manifest.get("fixture_id") != FIXTURE_ID:
        raise PipelineInputError("unsupported fixture manifest identity")
    if manifest.get("label_source") != "synthetic_fixture":
        raise PipelineInputError("fixture manifest must identify labels as synthetic_fixture")
    digest = manifest.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise PipelineInputError("fixture manifest sha256 must be 64 lowercase hexadecimal characters")
    return manifest


def _validate_records(records: Any, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(records, list) or not records:
        raise PipelineInputError("fixture must contain at least one JSONL record")
    required = {"example_id", "group_id", "split", "text", "label"}
    seen_ids: set[str] = set()
    groups_to_splits: dict[str, set[str]] = defaultdict(set)
    split_counts: Counter[str] = Counter()
    split_groups: dict[str, set[str]] = defaultdict(set)
    label_counts: dict[str, Counter[str]] = defaultdict(Counter)
    cleaned: list[dict[str, Any]] = []
    for row_no, row in enumerate(records, start=1):
        if not isinstance(row, dict) or set(row) != required:
            raise PipelineInputError(f"record {row_no} must contain exactly {sorted(required)}")
        for field in ("example_id", "group_id", "split", "text"):
            if not isinstance(row[field], str) or not row[field].strip():
                raise PipelineInputError(f"record {row_no} field {field} must be a non-empty string")
        if row["split"] not in {"train", "validation"}:
            raise PipelineInputError(f"record {row_no} has unsupported split {row['split']!r}")
        label = row["label"]
        if isinstance(label, bool) or not isinstance(label, int) or label not in (0, 1):
            raise PipelineInputError(f"record {row_no} label must be integer 0 or 1")
        if row["example_id"] in seen_ids:
            raise PipelineInputError(f"duplicate example_id {row['example_id']!r}")
        seen_ids.add(row["example_id"])
        groups_to_splits[row["group_id"]].add(row["split"])
        split_counts[row["split"]] += 1
        split_groups[row["split"]].add(row["group_id"])
        label_counts[row["split"]][str(label)] += 1
        cleaned.append(dict(row))
    leaking_groups = sorted(group for group, splits in groups_to_splits.items() if len(splits) != 1)
    if leaking_groups:
        raise PipelineInputError(f"group_id values cross splits: {leaking_groups}")

    expected_rows = manifest.get("record_count")
    expected_splits = manifest.get("split_record_counts")
    expected_groups = manifest.get("split_group_counts")
    expected_labels = manifest.get("label_counts")
    if len(cleaned) != expected_rows:
        raise PipelineInputError(f"record count {len(cleaned)} does not match manifest {expected_rows}")
    actual_splits = {name: split_counts[name] for name in ("train", "validation")}
    actual_groups = {name: len(split_groups[name]) for name in ("train", "validation")}
    actual_labels = {
        name: {label: label_counts[name][label] for label in ("0", "1")}
        for name in ("train", "validation")
    }
    if actual_splits != expected_splits:
        raise PipelineInputError("split record counts do not match fixture manifest")
    if actual_groups != expected_groups:
        raise PipelineInputError("split group counts do not match fixture manifest")
    if actual_labels != expected_labels:
        raise PipelineInputError("split label counts do not match fixture manifest")
    return cleaned


def load_fixture(
    fixture_path: Path = DEFAULT_FIXTURE,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    try:
        raw_bytes = fixture_path.read_bytes()
    except OSError as error:
        raise PipelineInputError(f"cannot read fixture: {error}") from error
    manifest = _read_manifest(manifest_path)
    digest = _sha256(raw_bytes)
    if digest != manifest["sha256"]:
        raise PipelineInputError("fixture sha256 does not match fixture manifest")
    records: list[dict[str, Any]] = []
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PipelineInputError("fixture must be UTF-8 encoded") from error
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise PipelineInputError(f"blank JSONL line at {line_no}; keep one record per line")
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise PipelineInputError(f"invalid JSON on line {line_no}: {error.msg}") from error
    return _validate_records(records, manifest), manifest, digest


def split_records(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        name: [row for row in records if row["split"] == name]
        for name in ("train", "validation")
    }


def build_datasets(records: list[dict[str, Any]]) -> DatasetDict:
    splits = split_records(records)
    if not splits["train"] or not splits["validation"]:
        raise PipelineInputError("both train and validation splits must be non-empty")
    return DatasetDict(
        {
            name: Dataset.from_list(rows, features=FEATURES)
            for name, rows in splits.items()
        }
    )


def train_fast_tokenizer(train_rows: list[dict[str, Any]]) -> PreTrainedTokenizerFast:
    if not train_rows:
        raise PipelineInputError("tokenizer training requires at least one train row")
    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()
    trainer = BpeTrainer(
        vocab_size=VOCAB_SIZE,
        min_frequency=1,
        special_tokens=list(SPECIAL_TOKENS),
    )
    tokenizer.train_from_iterator((row["text"] for row in train_rows), trainer=trainer)
    cls_id = tokenizer.token_to_id("[CLS]")
    sep_id = tokenizer.token_to_id("[SEP]")
    if cls_id is None or sep_id is None:
        raise RuntimeError("tokenizer training did not retain the required special tokens")
    tokenizer.post_processor = TemplateProcessing(
        single="[CLS] $A [SEP]",
        pair="[CLS] $A [SEP] $B:1 [SEP]:1",
        special_tokens=[("[CLS]", cls_id), ("[SEP]", sep_id)],
    )
    fast = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer,
        unk_token="[UNK]",
        pad_token="[PAD]",
        cls_token="[CLS]",
        sep_token="[SEP]",
        mask_token="[MASK]",
    )
    fast.model_max_length = MAX_LENGTH
    return fast


def tokenize_splits(
    raw_datasets: DatasetDict,
    tokenizer: PreTrainedTokenizerFast,
) -> DatasetDict:
    disable_progress_bar()

    def encode_batch(batch: dict[str, list[Any]]) -> dict[str, Any]:
        return tokenizer(batch["text"], truncation=True, max_length=MAX_LENGTH)

    remove_columns = ["example_id", "group_id", "split", "text"]
    return raw_datasets.map(
        encode_batch,
        batched=True,
        remove_columns=remove_columns,
        load_from_cache_file=False,
        desc="Tokenize the fixed synthetic fixture",
    )


def _split_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = Counter(str(row["label"]) for row in rows)
    return {
        "records": len(rows),
        "groups": len({row["group_id"] for row in rows}),
        "group_ids": sorted({row["group_id"] for row in rows}),
        "label_counts": {label: labels[label] for label in ("0", "1")},
    }


def _package_versions() -> dict[str, str]:
    return {
        "torch": str(torch.__version__),
        "transformers": str(transformers.__version__),
        "datasets": str(datasets.__version__),
        "tokenizers": str(tokenizers.__version__),
        "accelerate": str(accelerate.__version__),
    }


def run_pipeline(
    fixture_path: Path = DEFAULT_FIXTURE,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    seed: int = 58,
    max_steps: int = 2,
) -> dict[str, Any]:
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise PipelineInputError("seed must be a non-negative integer")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 1:
        raise PipelineInputError("max_steps must be a positive integer")

    records, manifest, fixture_sha256 = load_fixture(fixture_path, manifest_path)
    splits = split_records(records)
    if max_steps > (len(splits["train"]) + BATCH_SIZE - 1) // BATCH_SIZE:
        raise PipelineInputError("max_steps exceeds the number of train batches in this one-epoch smoke test")
    raw_datasets = build_datasets(records)
    tokenizer = train_fast_tokenizer(splits["train"])
    tokenized = tokenize_splits(raw_datasets, tokenizer)
    collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")

    torch.manual_seed(seed)
    torch.set_num_threads(1)
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(
        tokenized["train"],
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=generator,
        collate_fn=collator,
    )
    validation_loader = DataLoader(
        tokenized["validation"],
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collator,
    )

    config = BertConfig(
        vocab_size=len(tokenizer),
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=32,
        max_position_embeddings=MAX_LENGTH + 8,
        num_labels=2,
        pad_token_id=tokenizer.pad_token_id,
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
        classifier_dropout=0.0,
    )
    model = BertForSequenceClassification(config)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    accelerator = Accelerator(cpu=True)
    if accelerator.device.type != "cpu":
        raise RuntimeError(f"CPU-only smoke test received unexpected device {accelerator.device}")
    model, optimizer, train_loader = accelerator.prepare(model, optimizer, train_loader)

    training_losses: list[float] = []
    finite_gradients = True
    model.train()
    for step, batch in enumerate(train_loader):
        if step >= max_steps:
            break
        optimizer.zero_grad(set_to_none=True)
        output = model(**batch)
        loss = output.loss
        if loss is None or not torch.isfinite(loss).item():
            raise RuntimeError("training returned a non-finite loss")
        accelerator.backward(loss)
        finite_gradients = finite_gradients and all(
            parameter.grad is None or torch.isfinite(parameter.grad).all().item()
            for parameter in model.parameters()
        )
        if not finite_gradients:
            raise RuntimeError("training returned a non-finite gradient")
        training_losses.append(float(loss.detach().cpu().item()))
        optimizer.step()
    if len(training_losses) != max_steps:
        raise RuntimeError(f"completed {len(training_losses)} training steps, expected {max_steps}")

    model.eval()
    evaluation_losses: list[float] = []
    validation_loader = accelerator.prepare(validation_loader)
    with torch.no_grad():
        for batch in validation_loader:
            output = model(**batch)
            if output.loss is None or not torch.isfinite(output.loss).item():
                raise RuntimeError("validation smoke loss is non-finite")
            evaluation_losses.append(float(output.loss.detach().cpu().item()))

    return {
        "schema_version": 1,
        "fixture_id": manifest["fixture_id"],
        "fixture_sha256": fixture_sha256,
        "label_source": manifest["label_source"],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": _package_versions(),
            "accelerator_device": str(accelerator.device),
            "distributed_type": str(accelerator.distributed_type),
        },
        "data": {
            "splits": {
                name: _split_summary(rows)
                for name, rows in splits.items()
            },
            "group_overlap": sorted(
                set(row["group_id"] for row in splits["train"])
                & set(row["group_id"] for row in splits["validation"])
            ),
            "dataset_columns_after_tokenization": {
                name: list(tokenized[name].column_names)
                for name in ("train", "validation")
            },
        },
        "tokenizer": {
            "implementation": "tokenizers BPE wrapped by PreTrainedTokenizerFast",
            "trained_on_split": "train",
            "training_example_ids": [row["example_id"] for row in splits["train"]],
            "training_text_sha256": _sha256(
                "\n".join(row["text"] for row in splits["train"]).encode("utf-8")
            ),
            "vocab_size": len(tokenizer),
            "special_token_ids": {
                name: tokenizer.convert_tokens_to_ids(name)
                for name in SPECIAL_TOKENS
            },
            "max_length": MAX_LENGTH,
        },
        "model": {
            "class": "BertForSequenceClassification",
            "weights": "randomly_initialized_from_config",
            "pretrained_weights_loaded": False,
            "trainable_parameters": sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad),
            "hidden_size": config.hidden_size,
            "layers": config.num_hidden_layers,
            "num_labels": config.num_labels,
        },
        "training": {
            "performed": True,
            "seed": seed,
            "optimizer": "torch.optim.AdamW",
            "learning_rate": 1e-3,
            "batch_size": BATCH_SIZE,
            "steps": len(training_losses),
            "training_losses": training_losses,
            "all_gradients_finite": finite_gradients,
            "validation_loss_smoke_only": evaluation_losses,
            "validation_used_for_optimization": False,
            "device": str(accelerator.device),
        },
        "scope": {
            "real_user_or_public_data_used": False,
            "hub_access_or_download": False,
            "pretrained_weights_used": False,
            "validation_used_for_optimization": False,
            "gpu_used": False,
            "benchmark_performed": False,
            "model_quality_claim": False,
            "generalization_established": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the offline synthetic Hugging Face CPU pipeline")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=58)
    parser.add_argument("--max-steps", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        result = run_pipeline(
            args.fixture,
            args.manifest,
            seed=args.seed,
            max_steps=args.max_steps,
        )
    except (PipelineInputError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
