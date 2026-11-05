"""Train and evaluate a tiny next-token model on chapter 40's prepared splits.

The model is a fixed-context feed-forward baseline, not a Transformer or a
production language model. It uses PyTorch on CPU and never downloads data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
from typing import Iterable, Sequence

import torch
from torch import nn
from torch.nn import functional as F

SPECIAL_TOKENS = ("<pad>", "<unk>", "<bos>", "<eos>")
SPLIT_NAMES = ("train", "validation", "test")
TOKEN_PATTERN = re.compile(r"[\w\u200c]+|[^\w\s]", flags=re.UNICODE)
MODEL_TYPE = "tiny-fixed-context-feedforward-lm"


def normalize_text(text: str) -> str:
    """Match the conservative NFC/whitespace contract used in chapter 40."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(unicodedata.normalize("NFC", text).split())


def tokenize_words(text: str) -> list[str]:
    """Word/punctuation tokenization compatible with the chapter 40 baseline."""
    return TOKEN_PATTERN.findall(normalize_text(text))


def validate_vocabulary(vocabulary: Sequence[str]) -> list[str]:
    vocab = list(vocabulary)
    if len(vocab) < len(SPECIAL_TOKENS) or tuple(vocab[:4]) != SPECIAL_TOKENS:
        raise ValueError("vocabulary must start with <pad>, <unk>, <bos>, <eos>")
    if any(not isinstance(token, str) or not token for token in vocab):
        raise ValueError("vocabulary entries must be non-empty strings")
    if len(vocab) != len(set(vocab)):
        raise ValueError("vocabulary entries must be unique")
    return vocab


def encode_text(text: str, vocabulary: Sequence[str]) -> list[int]:
    """Encode one record with BOS/EOS; unknown words map to the fixed <unk> id."""
    vocab = validate_vocabulary(vocabulary)
    token_to_id = {token: index for index, token in enumerate(vocab)}
    unknown_id = token_to_id["<unk>"]
    ids = [token_to_id["<bos>"]]
    ids.extend(token_to_id.get(token, unknown_id) for token in tokenize_words(text))
    ids.append(token_to_id["<eos>"])
    return ids


def decode_ids(token_ids: Iterable[int], vocabulary: Sequence[str], skip_special: bool = True) -> str:
    vocab = validate_vocabulary(vocabulary)
    result = []
    skip = {"<pad>", "<bos>", "<eos>"}
    for token_id in token_ids:
        if not isinstance(token_id, int) or token_id < 0 or token_id >= len(vocab):
            raise ValueError(f"token id {token_id!r} is outside this vocabulary")
        token = vocab[token_id]
        if skip_special and token in skip:
            continue
        result.append(token)
    return " ".join(result)


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON from {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON in {path.name} line {line_number}: {exc.msg}") from exc
                if not isinstance(row, dict):
                    raise ValueError(f"{path.name} line {line_number} must be an object")
                for key in ("id", "group_id", "text"):
                    if not isinstance(row.get(key), str) or not row[key].strip():
                        raise ValueError(f"{path.name} line {line_number}: {key} must be a non-empty string")
                rows.append(row)
    except OSError as exc:
        raise ValueError(f"cannot read {path.name}: {exc}") from exc
    if not rows:
        raise ValueError(f"{path.name} contains no records")
    return rows


def load_dataset(data_dir: str | Path) -> dict:
    """Load chapter 40 artifacts and verify split/tokenizer provenance."""
    root = Path(data_dir)
    summary = _read_json(root / "summary.json")
    expected_normalization = "Unicode NFC and whitespace collapse; Persian ZWNJ retained"
    if summary.get("tokenizer_fit_split") != "train":
        raise ValueError("chapter 40 summary must confirm tokenizer_fit_split=train")
    if summary.get("normalization") != expected_normalization:
        raise ValueError("chapter 40 summary has an unsupported normalization contract")
    vocab_payload = _read_json(root / "vocab.json")
    if vocab_payload.get("format_version") != 1 or vocab_payload.get("kind") != "educational-word-level-tokenizer":
        raise ValueError("unsupported chapter 40 vocabulary format")
    if vocab_payload.get("special_tokens") != list(SPECIAL_TOKENS):
        raise ValueError("chapter 40 special-token contract does not match")
    if vocab_payload.get("normalization") != expected_normalization:
        raise ValueError("chapter 40 vocabulary has an unsupported normalization contract")
    vocabulary = validate_vocabulary(vocab_payload.get("vocabulary", []))
    if summary.get("tokenizer_vocabulary_size") != len(vocabulary):
        raise ValueError("chapter 40 summary and vocabulary size disagree")

    splits = {name: _read_jsonl(root / f"{name}.jsonl") for name in SPLIT_NAMES}
    seen_ids: set[str] = set()
    seen_text_hashes: dict[str, str] = {}
    group_sets: dict[str, set[str]] = {}
    for name, rows in splits.items():
        ids = [row["id"] for row in rows]
        overlap_ids = seen_ids.intersection(ids)
        if overlap_ids:
            raise ValueError(f"record id appears in more than one split: {sorted(overlap_ids)}")
        seen_ids.update(ids)
        group_sets[name] = {row["group_id"] for row in rows}
        for row in rows:
            normalized = normalize_text(row["text"])
            digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            if normalized != row["text"] or row.get("normalized_text_sha256") != digest:
                raise ValueError(f"normalized text hash or form does not match in {name}.jsonl for {row['id']}")
            previous_split = seen_text_hashes.get(digest)
            if previous_split is not None and previous_split != name:
                raise ValueError(f"exact normalized text appears in more than one split: {row['id']}")
            seen_text_hashes[digest] = name
    if group_sets["train"] & group_sets["validation"] or group_sets["train"] & group_sets["test"] or group_sets["validation"] & group_sets["test"]:
        raise ValueError("group leakage: a group_id appears in more than one split")

    declared_groups = summary.get("split_groups")
    if not isinstance(declared_groups, dict):
        raise ValueError("chapter 40 summary must include split_groups")
    for name in SPLIT_NAMES:
        declared = declared_groups.get(name)
        if not isinstance(declared, list) or set(declared) != group_sets[name]:
            raise ValueError(f"split_groups in summary do not match {name}.jsonl")

    training_tokens = {
        token
        for row in splits["train"]
        for token in tokenize_words(row["text"])
    }
    holdout_only_tokens = set(vocabulary[len(SPECIAL_TOKENS):]) - training_tokens
    if holdout_only_tokens:
        raise ValueError(f"vocabulary contains tokens absent from train: {sorted(holdout_only_tokens)}")

    vocab_bytes = json.dumps(vocabulary, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    split_hashes = {
        name: hashlib.sha256((root / f"{name}.jsonl").read_bytes()).hexdigest()
        for name in SPLIT_NAMES
    }
    return {
        "root": root,
        "summary": summary,
        "vocabulary": vocabulary,
        "splits": splits,
        "vocabulary_sha256": hashlib.sha256(vocab_bytes).hexdigest(),
        "summary_sha256": hashlib.sha256((root / "summary.json").read_bytes()).hexdigest(),
        "split_sha256": split_hashes,
    }


def build_examples(records: Sequence[dict], vocabulary: Sequence[str], block_size: int) -> list[tuple[list[int], int]]:
    """Make fixed-width left-padded context/next-token pairs per record only."""
    vocab = validate_vocabulary(vocabulary)
    if not isinstance(block_size, int) or block_size < 1 or block_size > 256:
        raise ValueError("block_size must be an integer between 1 and 256")
    pad_id = vocab.index("<pad>")
    examples: list[tuple[list[int], int]] = []
    for row in records:
        text = row.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("every record needs non-empty text")
        sequence = encode_text(text, vocab)
        for target_index in range(1, len(sequence)):
            context = sequence[max(0, target_index - block_size):target_index]
            context = [pad_id] * (block_size - len(context)) + context
            examples.append((context, sequence[target_index]))
    if not examples:
        raise ValueError("no next-token examples could be built")
    return examples


class TinyFeedForwardLM(nn.Module):
    """A small fixed-context baseline; no recurrent state or self-attention."""

    def __init__(self, vocab_size: int, block_size: int = 4, embedding_dim: int = 16,
                 hidden_dim: int = 32, pad_id: int = 0):
        super().__init__()
        if vocab_size < len(SPECIAL_TOKENS):
            raise ValueError("vocab_size is too small for the special-token contract")
        if not all(isinstance(x, int) and x > 0 for x in (block_size, embedding_dim, hidden_dim)):
            raise ValueError("block_size, embedding_dim, and hidden_dim must be positive integers")
        if not 0 <= pad_id < vocab_size:
            raise ValueError("pad_id must be inside the vocabulary")
        self.vocab_size = vocab_size
        self.block_size = block_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.pad_id = pad_id
        self.token_embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=pad_id)
        self.position_embedding = nn.Embedding(block_size, embedding_dim)
        self.hidden = nn.Linear(block_size * embedding_dim, hidden_dim)
        self.output = nn.Linear(hidden_dim, vocab_size)

    def forward(self, context_ids: torch.Tensor) -> torch.Tensor:
        if not isinstance(context_ids, torch.Tensor) or context_ids.dtype != torch.long:
            raise TypeError("context_ids must be a torch.long tensor")
        if context_ids.ndim != 2 or context_ids.shape[1] != self.block_size:
            raise ValueError(f"context_ids must have shape (batch, {self.block_size})")
        if context_ids.numel() and (context_ids.min().item() < 0 or context_ids.max().item() >= self.vocab_size):
            raise ValueError("context token id is outside the vocabulary")
        positions = torch.arange(self.block_size, device=context_ids.device)
        embedded = self.token_embedding(context_ids) + self.position_embedding(positions).unsqueeze(0)
        hidden = torch.tanh(self.hidden(embedded.reshape(context_ids.shape[0], -1)))
        return self.output(hidden)  # raw logits; CrossEntropyLoss applies log-softmax


def _example_tensors(examples: Sequence[tuple[list[int], int]]) -> tuple[torch.Tensor, torch.Tensor]:
    if not examples:
        raise ValueError("examples must not be empty")
    contexts, targets = zip(*examples)
    return torch.tensor(contexts, dtype=torch.long), torch.tensor(targets, dtype=torch.long)


def evaluate(model: TinyFeedForwardLM, examples: Sequence[tuple[list[int], int]], batch_size: int = 64) -> dict:
    """Return token-mean negative log-likelihood and derived perplexity."""
    if not isinstance(batch_size, int) or batch_size < 1:
        raise ValueError("batch_size must be a positive integer")
    inputs, targets = _example_tensors(examples)
    was_training = model.training
    model.eval()
    loss_sum = 0.0
    count = 0
    with torch.inference_mode():
        for start in range(0, len(targets), batch_size):
            x = inputs[start:start + batch_size]
            y = targets[start:start + batch_size]
            logits = model(x)
            loss_sum += float(F.cross_entropy(logits, y, reduction="sum").item())
            count += len(y)
    model.train(was_training)
    mean_nll = loss_sum / count
    perplexity = math.exp(mean_nll) if mean_nll < 80 else None
    return {"mean_nll_nats_per_token": mean_nll, "perplexity": perplexity, "target_tokens": count}


def train_model(train_examples: Sequence[tuple[list[int], int]],
                validation_examples: Sequence[tuple[list[int], int]],
                vocabulary: Sequence[str], *, seed: int = 41, epochs: int = 30,
                batch_size: int = 16, block_size: int = 4, embedding_dim: int = 16,
                hidden_dim: int = 32, learning_rate: float = 0.01) -> tuple[TinyFeedForwardLM, list[dict]]:
    if not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if not isinstance(epochs, int) or epochs < 1 or epochs > 1000:
        raise ValueError("epochs must be an integer from 1 to 1000")
    if not isinstance(batch_size, int) or batch_size < 1:
        raise ValueError("batch_size must be a positive integer")
    if not math.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("learning_rate must be finite and positive")
    vocab = validate_vocabulary(vocabulary)
    train_x, train_y = _example_tensors(train_examples)
    _example_tensors(validation_examples)
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    model = TinyFeedForwardLM(
        len(vocab), block_size=block_size, embedding_dim=embedding_dim,
        hidden_dim=hidden_dim, pad_id=vocab.index("<pad>"),
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.0)
    generator = torch.Generator(device="cpu").manual_seed(seed + 1)
    history: list[dict] = []
    for epoch in range(1, epochs + 1):
        model.train()
        order = torch.randperm(len(train_y), generator=generator)
        for start in range(0, len(order), batch_size):
            indices = order[start:start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            logits = model(train_x.index_select(0, indices))
            loss = F.cross_entropy(logits, train_y.index_select(0, indices))
            if not torch.isfinite(loss):
                raise FloatingPointError("training loss became non-finite")
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
        train_metrics = evaluate(model, train_examples, batch_size=batch_size)
        validation_metrics = evaluate(model, validation_examples, batch_size=batch_size)
        history.append({"epoch": epoch, "train": train_metrics, "validation": validation_metrics})
    return model, history


def generate(model: TinyFeedForwardLM, vocabulary: Sequence[str], prompt: str = "", *,
             max_new_tokens: int = 20, temperature: float = 1.0, seed: int = 41) -> dict:
    """Generate word-level tokens autoregressively from the fixed-context model."""
    vocab = validate_vocabulary(vocabulary)
    if not isinstance(max_new_tokens, int) or max_new_tokens < 0 or max_new_tokens > 512:
        raise ValueError("max_new_tokens must be an integer from 0 to 512")
    if not math.isfinite(temperature) or temperature < 0:
        raise ValueError("temperature must be finite and non-negative")
    token_to_id = {token: index for index, token in enumerate(vocab)}
    pad_id, unk_id = token_to_id["<pad>"], token_to_id["<unk>"]
    bos_id, eos_id = token_to_id["<bos>"], token_to_id["<eos>"]
    ids = [bos_id] + [token_to_id.get(token, unk_id) for token in tokenize_words(prompt)]
    generator = torch.Generator(device="cpu").manual_seed(seed)
    was_training = model.training
    model.eval()
    with torch.inference_mode():
        for _ in range(max_new_tokens):
            context = ids[-model.block_size:]
            context = [pad_id] * (model.block_size - len(context)) + context
            logits = model(torch.tensor([context], dtype=torch.long))[0].clone()
            logits[pad_id] = float("-inf")
            logits[bos_id] = float("-inf")
            if temperature == 0:
                next_id = int(torch.argmax(logits).item())
            else:
                probabilities = torch.softmax(logits / temperature, dim=-1)
                next_id = int(torch.multinomial(probabilities, 1, generator=generator).item())
            ids.append(next_id)
            if next_id == eos_id:
                break
    model.train(was_training)
    return {"token_ids": ids, "text": decode_ids(ids, vocab), "new_tokens": max(0, len(ids) - 1 - len(tokenize_words(prompt)))}


def model_config(vocabulary: Sequence[str], *, block_size: int, embedding_dim: int, hidden_dim: int) -> dict:
    return {
        "vocab_size": len(vocabulary),
        "block_size": block_size,
        "embedding_dim": embedding_dim,
        "hidden_dim": hidden_dim,
        "pad_id": list(vocabulary).index("<pad>"),
    }


def save_checkpoint(path: str | Path, model: TinyFeedForwardLM, vocabulary: Sequence[str],
                    config: dict, metadata: dict) -> None:
    """Save primitive metadata plus state_dict; do not pickle a model object."""
    vocab = validate_vocabulary(vocabulary)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format_version": 1,
        "model_type": MODEL_TYPE,
        "config": dict(config),
        "vocabulary": vocab,
        "metadata": dict(metadata),
        "state_dict": model.state_dict(),
    }
    torch.save(payload, path)


def load_checkpoint(path: str | Path) -> tuple[TinyFeedForwardLM, dict]:
    """Load a trusted educational checkpoint with weights_only=True on CPU."""
    payload = torch.load(Path(path), map_location="cpu", weights_only=True)
    if not isinstance(payload, dict) or payload.get("format_version") != 1 or payload.get("model_type") != MODEL_TYPE:
        raise ValueError("unsupported checkpoint format")
    vocabulary = validate_vocabulary(payload.get("vocabulary", []))
    config = payload.get("config")
    if not isinstance(config, dict) or config.get("vocab_size") != len(vocabulary):
        raise ValueError("checkpoint config and vocabulary disagree")
    model = TinyFeedForwardLM(**config)
    model.load_state_dict(payload["state_dict"], strict=True)
    model.eval()
    return model, payload


def run_experiment(data_dir: str | Path, output_dir: str | Path, *, seed: int = 41,
                   epochs: int = 30, batch_size: int = 16, block_size: int = 4,
                   embedding_dim: int = 16, hidden_dim: int = 32,
                   learning_rate: float = 0.01, prompt: str = "هوش مصنوعی",
                   max_new_tokens: int = 12, temperature: float = 0.8,
                   evaluate_test_split: bool = True) -> dict:
    """Train on train, monitor validation, and optionally evaluate test once."""
    if not isinstance(evaluate_test_split, bool):
        raise ValueError("evaluate_test_split must be a boolean")
    bundle = load_dataset(data_dir)
    vocab = bundle["vocabulary"]
    examples = {
        name: build_examples(bundle["splits"][name], vocab, block_size)
        for name in SPLIT_NAMES
    }
    model, history = train_model(
        examples["train"], examples["validation"], vocab, seed=seed, epochs=epochs,
        batch_size=batch_size, block_size=block_size, embedding_dim=embedding_dim,
        hidden_dim=hidden_dim, learning_rate=learning_rate,
    )
    # The held-out test split is evaluated once, after choices are fixed.
    metrics = {
        "format_version": 1,
        "model_type": MODEL_TYPE,
        "seed": seed,
        "device": "cpu",
        "torch_version": torch.__version__,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "config": model_config(vocab, block_size=block_size, embedding_dim=embedding_dim, hidden_dim=hidden_dim),
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "vocabulary_sha256": bundle["vocabulary_sha256"],
        "chapter40_summary_sha256": bundle["summary_sha256"],
        "split_sha256": bundle["split_sha256"],
        "token_targets": {name: len(examples[name]) for name in SPLIT_NAMES},
        "train": evaluate(model, examples["train"], batch_size=batch_size),
        "validation_last_epoch": history[-1]["validation"],
        "test_once_after_training": (
            evaluate(model, examples["test"], batch_size=batch_size)
            if evaluate_test_split else None
        ),
        "test_policy": (
            "evaluated once after configuration was fixed"
            if evaluate_test_split else "not evaluated; validation-only run (--skip-test)"
        ),
        "generation": generate(model, vocab, prompt, max_new_tokens=max_new_tokens,
                                temperature=temperature, seed=seed + 2),
        "limits": [
            "sixteen self-authored sample records only; not a representative Persian corpus",
            "word-level vocabulary; punctuation and spacing are simplified",
            "fixed-context feed-forward baseline; no Transformer, self-attention, or production decoding",
            "validation and test are tiny grouped holdouts; metrics are unstable and not evidence of generalization",
        ],
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "history.json").write_text(json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    config = metrics["config"]
    save_checkpoint(output / "checkpoint.pt", model, vocab, config, {
        "seed": seed,
        "training_summary_sha256": bundle["summary_sha256"],
        "vocabulary_sha256": bundle["vocabulary_sha256"],
        "split_sha256": bundle["split_sha256"],
        "optimizer": "AdamW, weight_decay=0",
    })
    return metrics


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Train a tiny CPU next-token baseline on chapter 40 splits")
    parser.add_argument("--data-dir", type=Path, default=project_dir.parent / "40-small-data-project" / "build")
    parser.add_argument("--output-dir", type=Path, default=project_dir / "build")
    parser.add_argument("--seed", type=int, default=41)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--block-size", type=int, default=4)
    parser.add_argument("--embedding-dim", type=int, default=16)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--prompt", default="هوش مصنوعی")
    parser.add_argument("--max-new-tokens", type=int, default=12)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--skip-test", action="store_true", help="do not evaluate held-out test data during validation-only model selection")
    args = parser.parse_args()
    metrics = run_experiment(
        args.data_dir, args.output_dir, seed=args.seed, epochs=args.epochs,
        batch_size=args.batch_size, block_size=args.block_size,
        embedding_dim=args.embedding_dim, hidden_dim=args.hidden_dim,
        learning_rate=args.learning_rate, prompt=args.prompt,
        max_new_tokens=args.max_new_tokens, temperature=args.temperature,
        evaluate_test_split=not args.skip_test,
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
