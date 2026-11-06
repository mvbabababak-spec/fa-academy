"""Tiny pretraining loop with update-based warmup/cosine and resumable checkpoints.

Reuses chapter 41's tested model, tokenizer and data loader. The focus here is
training state: optimizer updates, token-mean gradient accumulation, schedule,
metrics and exact CPU resume within one fixed software/data configuration.
No model or dataset is downloaded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Sequence

import torch
from torch import nn
from torch.nn import functional as F


ROOT = Path(__file__).resolve().parents[3]
CHAPTER41_PROJECT = ROOT / "book-engineering/projects/41-first-language-model"
if str(CHAPTER41_PROJECT) not in sys.path:
    sys.path.insert(0, str(CHAPTER41_PROJECT))

from tiny_lm import TinyFeedForwardLM, build_examples, evaluate, load_dataset  # noqa: E402

CHECKPOINT_VERSION = 1
SCHEDULE_NAME = "linear_warmup_cosine"


def _finite_positive(name: str, value: float) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def warmup_cosine_learning_rate(
    update: int,
    *,
    peak_lr: float,
    total_updates: int,
    warmup_updates: int,
    min_lr_ratio: float = 0.1,
) -> float:
    """Return the LR for one-based optimizer update `update`.

    With warmup, update W reaches peak_lr and update U reaches the minimum.
    With no warmup, update 1 starts at peak_lr and the final update reaches
    min_lr_ratio * peak_lr. For a one-update run, the only update uses peak_lr.
    """
    peak_lr = _finite_positive("peak_lr", peak_lr)
    if not isinstance(total_updates, int) or total_updates < 1:
        raise ValueError("total_updates must be a positive integer")
    if not isinstance(update, int) or not 1 <= update <= total_updates:
        raise ValueError("update must be in [1, total_updates]")
    if not isinstance(warmup_updates, int) or not 0 <= warmup_updates < total_updates:
        raise ValueError("warmup_updates must be an integer in [0, total_updates)")
    if not isinstance(min_lr_ratio, (int, float)) or not math.isfinite(min_lr_ratio) or not 0 <= min_lr_ratio <= 1:
        raise ValueError("min_lr_ratio must be finite and in [0, 1]")

    if warmup_updates and update <= warmup_updates:
        return peak_lr * update / warmup_updates
    if warmup_updates:
        progress = (update - warmup_updates) / (total_updates - warmup_updates)
    elif total_updates == 1:
        progress = 0.0
    else:
        progress = (update - 1) / (total_updates - 1)
    progress = min(max(progress, 0.0), 1.0)
    minimum = peak_lr * float(min_lr_ratio)
    return minimum + 0.5 * (peak_lr - minimum) * (1.0 + math.cos(math.pi * progress))


def make_config(
    vocabulary: Sequence[str],
    *,
    total_updates: int = 12,
    microbatch_size: int = 8,
    gradient_accumulation_steps: int = 2,
    peak_lr: float = 0.01,
    warmup_updates: int = 3,
    min_lr_ratio: float = 0.1,
    evaluation_every: int = 3,
    checkpoint_every: int = 4,
    seed: int = 44,
    block_size: int = 4,
    embedding_dim: int = 16,
    hidden_dim: int = 32,
    max_grad_norm: float = 1.0,
) -> dict:
    """Build the serializable, resume-locked run configuration."""
    if not isinstance(vocabulary, Sequence) or len(vocabulary) < 4:
        raise ValueError("vocabulary must contain at least the four chapter-41 special tokens")
    integer_fields = {
        "total_updates": total_updates,
        "microbatch_size": microbatch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "evaluation_every": evaluation_every,
        "checkpoint_every": checkpoint_every,
        "seed": seed,
        "block_size": block_size,
        "embedding_dim": embedding_dim,
        "hidden_dim": hidden_dim,
    }
    for name, value in integer_fields.items():
        minimum = 0 if name == "seed" else 1
        if not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if not isinstance(warmup_updates, int) or not 0 <= warmup_updates < total_updates:
        raise ValueError("warmup_updates must be in [0, total_updates)")
    peak_lr = _finite_positive("peak_lr", peak_lr)
    max_grad_norm = _finite_positive("max_grad_norm", max_grad_norm)
    if not isinstance(min_lr_ratio, (int, float)) or not math.isfinite(min_lr_ratio) or not 0 <= min_lr_ratio <= 1:
        raise ValueError("min_lr_ratio must be finite and in [0, 1]")
    return {
        "model": {
            "type": "chapter41.TinyFeedForwardLM",
            "vocab_size": len(vocabulary),
            "block_size": block_size,
            "embedding_dim": embedding_dim,
            "hidden_dim": hidden_dim,
            "pad_id": list(vocabulary).index("<pad>"),
        },
        "optimizer": {"type": "AdamW", "weight_decay": 0.0},
        "schedule": {
            "type": SCHEDULE_NAME,
            "peak_lr": peak_lr,
            "warmup_updates": warmup_updates,
            "min_lr_ratio": float(min_lr_ratio),
        },
        "total_updates": total_updates,
        "microbatch_size": microbatch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "evaluation_every": evaluation_every,
        "checkpoint_every": checkpoint_every,
        "seed": seed,
        "max_grad_norm": max_grad_norm,
        "device": "cpu",
    }


def data_identity(dataset: dict) -> dict:
    """Use chapter-41 hashes to bind a run/checkpoint to exact prepared inputs."""
    identity = {
        "summary_sha256": dataset["summary_sha256"],
        "vocabulary_sha256": dataset["vocabulary_sha256"],
        "split_sha256": dict(sorted(dataset["split_sha256"].items())),
    }
    for digest in (identity["summary_sha256"], identity["vocabulary_sha256"], *identity["split_sha256"].values()):
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError("dataset identity must contain SHA-256 hex digests")
    return identity


def run_fingerprint(config: dict, identity: dict) -> str:
    payload = json.dumps({"config": config, "data_identity": identity}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class BatchCursor:
    """Deterministic shuffled example cursor; state is saved at update boundaries."""

    def __init__(self, example_count: int, microbatch_size: int, accumulation_steps: int, seed: int):
        if not isinstance(example_count, int) or example_count < 1:
            raise ValueError("example_count must be a positive integer")
        if not isinstance(microbatch_size, int) or microbatch_size < 1:
            raise ValueError("microbatch_size must be a positive integer")
        if not isinstance(accumulation_steps, int) or accumulation_steps < 1:
            raise ValueError("accumulation_steps must be a positive integer")
        self.example_count = example_count
        self.microbatch_size = microbatch_size
        self.accumulation_steps = accumulation_steps
        self.epoch = 0
        self.order: list[int] = []
        self.position = 0
        self.generator = torch.Generator(device="cpu").manual_seed(seed)

    def _begin_epoch(self) -> None:
        self.epoch += 1
        self.order = torch.randperm(self.example_count, generator=self.generator).tolist()
        self.position = 0

    def next_microbatch(self) -> list[int]:
        if not self.order or self.position >= self.example_count:
            self._begin_epoch()
        end = min(self.position + self.microbatch_size, self.example_count)
        indices = self.order[self.position:end]
        self.position = end
        return indices

    def next_window(self) -> list[list[int]]:
        return [self.next_microbatch() for _ in range(self.accumulation_steps)]

    def state_dict(self) -> dict:
        return {
            "example_count": self.example_count,
            "microbatch_size": self.microbatch_size,
            "accumulation_steps": self.accumulation_steps,
            "epoch": self.epoch,
            "order": list(self.order),
            "position": self.position,
            "generator_state": self.generator.get_state(),
        }

    def load_state_dict(self, state: dict) -> None:
        expected = (self.example_count, self.microbatch_size, self.accumulation_steps)
        actual = (state.get("example_count"), state.get("microbatch_size"), state.get("accumulation_steps"))
        if actual != expected:
            raise ValueError("sampler checkpoint does not match dataset/batch configuration")
        order = state.get("order")
        position = state.get("position")
        epoch = state.get("epoch")
        generator_state = state.get("generator_state")
        if not isinstance(order, list) or not isinstance(position, int) or not isinstance(epoch, int):
            raise ValueError("invalid sampler checkpoint fields")
        if order and sorted(order) != list(range(self.example_count)):
            raise ValueError("sampler order must be a permutation of all training examples")
        if not order and (position != 0 or epoch != 0):
            raise ValueError("empty sampler order is valid only before the first batch")
        if not 0 <= position <= self.example_count or epoch < 0:
            raise ValueError("sampler position or epoch is outside its valid range")
        if order and epoch < 1:
            raise ValueError("a non-empty sampler order must have a positive epoch")
        if not isinstance(generator_state, torch.Tensor):
            raise ValueError("sampler checkpoint is missing its random generator state")
        self.epoch = epoch
        self.order = list(order)
        self.position = position
        self.generator.set_state(generator_state)


def _atomic_torch_save(value: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False)
    temporary = Path(handle.name)
    handle.close()
    try:
        torch.save(value, temporary)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json_write(value: dict | list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False)
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _loss_curve_svg(history: list[dict]) -> str:
    """Render recorded training/validation NLL as a dependency-free SVG."""
    training = [(int(row["update"]), float(row["batch_mean_nll"])) for row in history]
    validation = [
        (int(row["update"]), float(row["validation"]["mean_nll_nats_per_token"]))
        for row in history if row.get("validation") is not None
    ]
    values = [value for _, value in (*training, *validation)]
    if not training or not values or not all(math.isfinite(value) for value in values):
        raise ValueError("loss curve requires finite training history and at least one optimizer update")

    width, height = 960, 560
    left, right, top, bottom = 96, 34, 76, 90
    plot_width, plot_height = width - left - right, height - top - bottom
    max_update = max(update for update, _ in training)
    x = lambda update: left + (update - 1) / max(1, max_update - 1) * plot_width
    low, high = min(values), max(values)
    if high - low < 1e-12:
        low -= 0.5
        high += 0.5
    padding = (high - low) * 0.12
    low, high = low - padding, high + padding
    y = lambda value: top + (high - value) / (high - low) * plot_height
    esc = lambda value: f"{value:.5g}"
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 560" role="img" aria-labelledby="chart-title chart-desc">',
        '<title id="chart-title">Training and validation loss by optimizer update</title>',
        '<desc id="chart-desc">Mean negative log likelihood in nats per target, plotted from the recorded history.json. Training is a blue solid line; periodic validation is an orange line with circles.</desc>',
        '<rect width="960" height="560" fill="#ffffff"/>',
        '<text x="480" y="34" text-anchor="middle" font-family="sans-serif" font-size="21" font-weight="700" fill="#172554">Loss curve from history.json</text>',
    ]
    for tick in range(5):
        value = high - (high - low) * tick / 4
        yy = y(value)
        pieces.append(f'<line x1="{left}" y1="{yy:.2f}" x2="{left + plot_width}" y2="{yy:.2f}" stroke="#e2e8f0"/>')
        pieces.append(f'<text x="{left - 12}" y="{yy + 5:.2f}" text-anchor="end" font-family="sans-serif" font-size="13" fill="#475569">{esc(value)}</text>')
    pieces.extend([
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#334155" stroke-width="1.5"/>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#334155" stroke-width="1.5"/>',
        f'<text x="{left + plot_width / 2:.1f}" y="{height - 22}" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#0f172a">Optimizer update</text>',
        f'<text x="24" y="{top + plot_height / 2:.1f}" transform="rotate(-90 24 {top + plot_height / 2:.1f})" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#0f172a">NLL (nat / target)</text>',
    ])
    tick_updates = sorted(set((1, max_update))) if max_update == 1 else sorted(set((1, (max_update + 1) // 2, max_update)))
    for update in tick_updates:
        xx = x(update)
        pieces.append(f'<line x1="{xx:.2f}" y1="{top + plot_height}" x2="{xx:.2f}" y2="{top + plot_height + 5}" stroke="#334155"/>')
        pieces.append(f'<text x="{xx:.2f}" y="{top + plot_height + 23}" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#475569">{update}</text>')

    def add_series(points: list[tuple[int, float]], color: str, marker: bool) -> None:
        if not points:
            return
        coords = " ".join(f"{x(update):.2f},{y(value):.2f}" for update, value in points)
        pieces.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
        if marker:
            for update, value in points:
                pieces.append(f'<circle cx="{x(update):.2f}" cy="{y(value):.2f}" r="5" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>')

    add_series(training, "#2563eb", False)
    add_series(validation, "#ea580c", True)
    pieces.extend([
        f'<line x1="{left + 18}" y1="{height - 53}" x2="{left + 52}" y2="{height - 53}" stroke="#2563eb" stroke-width="3"/>',
        f'<text x="{left + 61}" y="{height - 48}" font-family="sans-serif" font-size="13" fill="#334155">Training batch mean</text>',
        f'<line x1="{left + 246}" y1="{height - 53}" x2="{left + 280}" y2="{height - 53}" stroke="#ea580c" stroke-width="3"/>',
        f'<circle cx="{left + 263}" cy="{height - 53}" r="4" fill="#ea580c"/>',
        f'<text x="{left + 289}" y="{height - 48}" font-family="sans-serif" font-size="13" fill="#334155">Validation</text>',
        '<text x="480" y="552" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#64748b">Validation points appear only at scheduled evaluation updates; this curve is descriptive, not a quality claim.</text>',
        '</svg>',
    ])
    return "\n".join(pieces) + "\n"


def _atomic_text_write(value: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False)
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _checkpoint_payload(
    *, model: TinyFeedForwardLM, optimizer: torch.optim.Optimizer, cursor: BatchCursor,
    config: dict, identity: dict, fingerprint: str, step: int, history: list[dict],
    phase: str = "training", final_metrics: dict | None = None,
) -> dict:
    return {
        "checkpoint_version": CHECKPOINT_VERSION,
        "phase": phase,
        "run_fingerprint": fingerprint,
        "config": config,
        "data_identity": identity,
        "step": step,
        "scheduler_state": {"type": SCHEDULE_NAME, "last_completed_update": step},
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "sampler_state_dict": cursor.state_dict(),
        "torch_rng_state": torch.get_rng_state(),
        "history": history,
        "final_metrics": final_metrics,
    }


def _load_checkpoint(
    path: str | Path, *, config: dict, identity: dict, fingerprint: str,
    model: TinyFeedForwardLM, optimizer: torch.optim.Optimizer, cursor: BatchCursor,
) -> dict:
    try:
        state = torch.load(Path(path), map_location="cpu", weights_only=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(f"cannot load a safe checkpoint from {path}: {exc}") from exc
    if not isinstance(state, dict) or state.get("checkpoint_version") != CHECKPOINT_VERSION:
        raise ValueError("unsupported or malformed checkpoint version")
    if state.get("config") != config or state.get("data_identity") != identity:
        raise ValueError("resume refused: checkpoint config or data hashes differ from this run")
    if state.get("run_fingerprint") != fingerprint:
        raise ValueError("resume refused: run fingerprint does not match")
    step = state.get("step")
    if not isinstance(step, int) or not 0 <= step <= config["total_updates"]:
        raise ValueError("checkpoint update is outside the configured training plan")
    scheduler_state = state.get("scheduler_state")
    if scheduler_state != {"type": SCHEDULE_NAME, "last_completed_update": step}:
        raise ValueError("checkpoint schedule position is inconsistent with optimizer update")
    if state.get("phase") not in {"training", "complete"} or not isinstance(state.get("history"), list):
        raise ValueError("checkpoint phase or history is invalid")
    if not isinstance(state.get("torch_rng_state"), torch.Tensor):
        raise ValueError("checkpoint is missing the CPU torch RNG state")
    model.load_state_dict(state["model_state_dict"])
    optimizer.load_state_dict(state["optimizer_state_dict"])
    cursor.load_state_dict(state["sampler_state_dict"])
    torch.set_rng_state(state["torch_rng_state"])
    return state


def _examples_to_tensors(examples: Sequence[tuple[list[int], int]]) -> tuple[torch.Tensor, torch.Tensor]:
    if not examples:
        raise ValueError("training examples must not be empty")
    contexts, targets = zip(*examples)
    inputs = torch.tensor(contexts, dtype=torch.long, device="cpu")
    labels = torch.tensor(targets, dtype=torch.long, device="cpu")
    if inputs.ndim != 2 or labels.ndim != 1 or len(inputs) != len(labels):
        raise ValueError("examples must be context/next-token pairs")
    return inputs, labels


def _last_validation(history: list[dict]) -> dict | None:
    for item in reversed(history):
        if item.get("validation") is not None:
            return item["validation"]
    return None


def _write_run_outputs(output_dir: Path, history: list[dict], metrics: dict, config: dict, identity: dict) -> None:
    _atomic_json_write(history, output_dir / "history.json")
    _atomic_json_write(metrics, output_dir / "metrics.json")
    _atomic_text_write(_loss_curve_svg(history), output_dir / "loss_curve.svg")
    card = "\n".join([
        "# Chapter 44 pretraining run card",
        "",
        f"- Status: `{metrics['status']}`; optimizer update {metrics['global_update']} / {metrics['total_updates']}.",
        f"- Training examples: {metrics['training_examples']}; valid target tokens seen: {metrics['target_tokens_seen']}.",
        f"- Effective batch cap: microbatch {config['microbatch_size']} × accumulation {config['gradient_accumulation_steps']} (final batches may be smaller).",
        f"- Schedule: linear warmup + cosine; peak LR {config['schedule']['peak_lr']}; warmup {config['schedule']['warmup_updates']} updates; final ratio {config['schedule']['min_lr_ratio']}.",
        f"- Data identity: summary `{identity['summary_sha256']}`; vocabulary `{identity['vocabulary_sha256']}`.",
        "- Validation guides monitoring only; the held-out test split is evaluated once after a completed run and is never used to step the schedule.",
        "- This CPU fixture is an engineering demonstration, not a quality, scaling or production-pretraining result.",
        "",
    ])
    card_path = output_dir / "run_card.md"
    temporary = output_dir / ".run_card.md.tmp"
    output_dir.mkdir(parents=True, exist_ok=True)
    temporary.write_text(card, encoding="utf-8")
    os.replace(temporary, card_path)


def train_pretraining(
    train_examples: Sequence[tuple[list[int], int]],
    validation_examples: Sequence[tuple[list[int], int]],
    test_examples: Sequence[tuple[list[int], int]],
    vocabulary: Sequence[str],
    *,
    config: dict,
    identity: dict,
    output_dir: str | Path,
    resume_from: str | Path | None = None,
    stop_after: int | None = None,
) -> dict:
    """Run or resume a CPU training plan; only a completed run evaluates the test split."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if config["model"]["vocab_size"] != len(vocabulary):
        raise ValueError("configured vocabulary size does not match tokenizer")
    fingerprint = run_fingerprint(config, identity)
    torch.set_num_threads(1)
    torch.manual_seed(config["seed"])
    model = TinyFeedForwardLM(
        vocab_size=config["model"]["vocab_size"],
        block_size=config["model"]["block_size"],
        embedding_dim=config["model"]["embedding_dim"],
        hidden_dim=config["model"]["hidden_dim"],
        pad_id=config["model"]["pad_id"],
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["schedule"]["peak_lr"], weight_decay=config["optimizer"]["weight_decay"])
    cursor = BatchCursor(
        len(train_examples), config["microbatch_size"], config["gradient_accumulation_steps"], config["seed"] + 1,
    )
    inputs, targets = _examples_to_tensors(train_examples)
    history: list[dict] = []
    step = 0
    loaded_state = None
    if resume_from is not None:
        loaded_state = _load_checkpoint(
            resume_from, config=config, identity=identity, fingerprint=fingerprint,
            model=model, optimizer=optimizer, cursor=cursor,
        )
        step = loaded_state["step"]
        history = list(loaded_state["history"])
        if loaded_state["phase"] == "complete":
            metrics = loaded_state.get("final_metrics")
            if not isinstance(metrics, dict) or not metrics.get("completed"):
                raise ValueError("completed checkpoint is missing final metrics")
            _write_run_outputs(output, history, metrics, config, identity)
            return metrics
    if stop_after is not None:
        if not isinstance(stop_after, int) or not 1 <= stop_after <= config["total_updates"]:
            raise ValueError("stop_after must be in [1, total_updates]")
        if stop_after <= step and step < config["total_updates"]:
            raise ValueError("stop_after must be greater than the checkpoint update")

    while step < config["total_updates"]:
        update = step + 1
        lr = warmup_cosine_learning_rate(
            update,
            peak_lr=config["schedule"]["peak_lr"],
            total_updates=config["total_updates"],
            warmup_updates=config["schedule"]["warmup_updates"],
            min_lr_ratio=config["schedule"]["min_lr_ratio"],
        )
        for group in optimizer.param_groups:
            group["lr"] = lr
        batches = cursor.next_window()
        target_count = sum(len(batch) for batch in batches)
        if target_count == 0:
            raise RuntimeError("sampler produced an empty optimizer update")
        optimizer.zero_grad(set_to_none=True)
        loss_sum_for_update = 0.0
        for indices in batches:
            index_tensor = torch.tensor(indices, dtype=torch.long)
            batch_x = inputs.index_select(0, index_tensor)
            batch_y = targets.index_select(0, index_tensor)
            logits = model(batch_x)
            loss_sum = F.cross_entropy(logits, batch_y, reduction="sum")
            if not torch.isfinite(loss_sum):
                raise FloatingPointError(f"non-finite loss at optimizer update {update}")
            (loss_sum / target_count).backward()
            loss_sum_for_update += float(loss_sum.detach().item())
        grad_norm = nn.utils.clip_grad_norm_(model.parameters(), config["max_grad_norm"], error_if_nonfinite=True)
        optimizer.step()
        step = update
        entry = {
            "update": step,
            "learning_rate": lr,
            "batch_mean_nll": loss_sum_for_update / target_count,
            "target_tokens_in_update": target_count,
            "sampler_epoch": cursor.epoch,
            "gradient_norm_before_clip": float(grad_norm.detach().item()),
            "validation": None,
        }
        if step % config["evaluation_every"] == 0 or step == config["total_updates"]:
            entry["validation"] = evaluate(model, validation_examples, batch_size=config["microbatch_size"])
        history.append(entry)

        stop_here = stop_after is not None and step >= stop_after and step < config["total_updates"]
        if step % config["checkpoint_every"] == 0 or step == config["total_updates"] or stop_here:
            state = _checkpoint_payload(
                model=model, optimizer=optimizer, cursor=cursor, config=config, identity=identity,
                fingerprint=fingerprint, step=step, history=history,
            )
            _atomic_torch_save(state, output / "checkpoint-latest.pt")
            _atomic_json_write(history, output / "history.json")
        if stop_here:
            break

    completed = step == config["total_updates"]
    latest_validation = _last_validation(history)
    metrics = {
        "status": "complete" if completed else "partial",
        "completed": completed,
        "global_update": step,
        "total_updates": config["total_updates"],
        "training_examples": len(train_examples),
        "target_tokens_seen": sum(item["target_tokens_in_update"] for item in history),
        "run_fingerprint": fingerprint,
        "data_identity": identity,
        "final_validation": latest_validation if completed else None,
        "latest_validation": latest_validation,
        "test_once_after_training": 0,
        "test_metrics": None,
    }
    if completed:
        metrics["test_metrics"] = evaluate(model, test_examples, batch_size=config["microbatch_size"])
        metrics["test_once_after_training"] = 1
        final_state = _checkpoint_payload(
            model=model, optimizer=optimizer, cursor=cursor, config=config, identity=identity,
            fingerprint=fingerprint, step=step, history=history, phase="complete", final_metrics=metrics,
        )
        _atomic_torch_save(final_state, output / "checkpoint-latest.pt")
        _atomic_torch_save(final_state, output / "checkpoint-final.pt")
    _write_run_outputs(output, history, metrics, config, identity)
    return metrics


def run_from_data_dir(
    data_dir: str | Path,
    *,
    config: dict,
    output_dir: str | Path,
    resume_from: str | Path | None = None,
    stop_after: int | None = None,
) -> dict:
    dataset = load_dataset(data_dir)
    vocabulary = dataset["vocabulary"]
    block_size = config["model"]["block_size"]
    examples = {
        name: build_examples(dataset["splits"][name], vocabulary, block_size)
        for name in ("train", "validation", "test")
    }
    return train_pretraining(
        examples["train"], examples["validation"], examples["test"], vocabulary,
        config=config, identity=data_identity(dataset), output_dir=output_dir,
        resume_from=resume_from, stop_after=stop_after,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a tiny resumable pretraining schedule on chapter-40 sample data")
    parser.add_argument("--data-dir", type=Path, required=True, help="chapter-40 prepared output with train/validation/test and vocab")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "build")
    parser.add_argument("--total-updates", type=int, default=12)
    parser.add_argument("--microbatch-size", type=int, default=8)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=2)
    parser.add_argument("--peak-lr", type=float, default=0.01)
    parser.add_argument("--warmup-updates", type=int, default=3)
    parser.add_argument("--min-lr-ratio", type=float, default=0.1)
    parser.add_argument("--evaluation-every", type=int, default=3)
    parser.add_argument("--checkpoint-every", type=int, default=4)
    parser.add_argument("--seed", type=int, default=44)
    parser.add_argument("--resume", type=Path, help="safe checkpoint to resume or inspect without reevaluating a completed test")
    parser.add_argument("--stop-after", type=int, help="save a partial run at this optimizer update for interruption/resume practice")
    args = parser.parse_args(argv)
    dataset = load_dataset(args.data_dir)
    vocabulary = dataset["vocabulary"]
    config = make_config(
        vocabulary,
        total_updates=args.total_updates,
        microbatch_size=args.microbatch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        peak_lr=args.peak_lr,
        warmup_updates=args.warmup_updates,
        min_lr_ratio=args.min_lr_ratio,
        evaluation_every=args.evaluation_every,
        checkpoint_every=args.checkpoint_every,
        seed=args.seed,
    )
    examples = {
        name: build_examples(dataset["splits"][name], vocabulary, config["model"]["block_size"])
        for name in ("train", "validation", "test")
    }
    metrics = train_pretraining(
        examples["train"], examples["validation"], examples["test"], vocabulary,
        config=config, identity=data_identity(dataset), output_dir=args.output_dir,
        resume_from=args.resume, stop_after=args.stop_after,
    )
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True, indent=2))
    print("This CPU run is a schedule/checkpoint exercise, not a language-model quality claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
