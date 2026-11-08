"""Design and budget a tiny GPT-like decoder using chapter 37's tested model.

This script does not train a language model. It checks a configuration, verifies
its exact parameter count against the existing decoder-only implementation,
performs one random-token shape smoke test, and estimates clearly labeled memory
proxies. No data is downloaded.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import sys

import torch

# Reuse, rather than fork, the decoder-only architecture tested in chapter 37.
CHAPTER_37_PROJECT = Path(__file__).resolve().parents[1] / "37-encoder-decoder"
if str(CHAPTER_37_PROJECT) not in sys.path:
    sys.path.insert(0, str(CHAPTER_37_PROJECT))

from transformer_architectures import DecoderOnlyLanguageModel  # noqa: E402


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for the chapter-37 decoder-only teaching model."""

    vocab_size: int = 102
    block_size: int = 64
    d_model: int = 64
    num_heads: int = 4
    ff_dim: int = 256
    num_layers: int = 2
    pad_id: int = 0

    def validate(self) -> None:
        positive = {
            "vocab_size": self.vocab_size,
            "block_size": self.block_size,
            "d_model": self.d_model,
            "num_heads": self.num_heads,
            "ff_dim": self.ff_dim,
            "num_layers": self.num_layers,
        }
        for name, value in positive.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.vocab_size < 2:
            raise ValueError("vocab_size must be at least 2")
        if self.d_model % self.num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        if isinstance(self.pad_id, bool) or not isinstance(self.pad_id, int):
            raise ValueError("pad_id must be an integer")
        if not 0 <= self.pad_id < self.vocab_size:
            raise ValueError("pad_id must be a valid vocabulary id")


def parameter_breakdown(config: ModelConfig) -> dict[str, int]:
    """Return exact parameter counts for chapter 37's untied, biased model."""
    config.validate()
    vocab, width, context = config.vocab_size, config.d_model, config.block_size
    attention_per_block = 4 * width * width + 4 * width
    norms_per_block = 4 * width  # two LayerNorms, each with scale and bias
    ffn_per_block = 2 * width * config.ff_dim + config.ff_dim + width
    block_per_layer = attention_per_block + norms_per_block + ffn_per_block
    parts = {
        "token_embedding": vocab * width,
        "position_embedding": context * width,
        "attention_per_block": attention_per_block,
        "norms_per_block": norms_per_block,
        "ffn_per_block": ffn_per_block,
        "all_transformer_blocks": config.num_layers * block_per_layer,
        "final_layer_norm": 2 * width,
        "untied_lm_head": width * vocab + vocab,
    }
    parts["total"] = (
        parts["token_embedding"]
        + parts["position_embedding"]
        + parts["all_transformer_blocks"]
        + parts["final_layer_norm"]
        + parts["untied_lm_head"]
    )
    return parts


class NonPaddingPrefixDecoder(DecoderOnlyLanguageModel):
    """Chapter-37 decoder plus a guard against rows starting with a masked key."""

    def forward(
        self,
        token_ids: torch.Tensor,
        padding_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        if isinstance(token_ids, torch.Tensor) and token_ids.ndim == 2:
            if token_ids.shape[0] > 0 and token_ids.shape[1] > 0:
                if bool(token_ids[:, 0].eq(self.pad_id).any().item()):
                    raise ValueError(
                        "each causal sequence must start with a non-padding prefix token (for example BOS)"
                    )
                if (
                    isinstance(padding_mask, torch.Tensor)
                    and padding_mask.dtype == torch.bool
                    and tuple(padding_mask.shape) == tuple(token_ids.shape)
                    and bool(padding_mask[:, 0].any().item())
                ):
                    raise ValueError("the first prefix token cannot be masked as padding")
        return super().forward(token_ids, padding_mask=padding_mask)


def build_model(config: ModelConfig) -> DecoderOnlyLanguageModel:
    """Reuse chapter 37's model with an explicit non-padding-prefix guard."""
    config.validate()
    return NonPaddingPrefixDecoder(
        vocab_size=config.vocab_size,
        d_model=config.d_model,
        num_heads=config.num_heads,
        ff_dim=config.ff_dim,
        num_layers=config.num_layers,
        max_len=config.block_size,
        pad_id=config.pad_id,
    )


def count_parameters(model: torch.nn.Module) -> int:
    """Count trainable and non-trainable model parameters once each."""
    return sum(parameter.numel() for parameter in model.parameters())


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 ** 2), 6)


def estimate_budget(
    config: ModelConfig,
    *,
    batch_size: int,
    sequence_length: int,
    parameter_bytes: int = 4,
    gradient_bytes: int = 4,
    optimizer_state_bytes_per_parameter: int = 8,
    activation_bytes: int = 4,
) -> dict:
    """Estimate persistent bytes and named tensor-size proxies, not peak VRAM.

    The default persistent estimate assumes FP32 parameters and gradients plus
    two FP32 AdamW moments. The score-equivalent, FFN-hidden, and logits sizes
    describe one tensor of each named shape per layer (or one logits tensor);
    they are not a peak-memory measurement or a prediction of kernel allocation.
    """
    config.validate()
    integer_values = {
        "batch_size": batch_size,
        "sequence_length": sequence_length,
        "parameter_bytes": parameter_bytes,
        "gradient_bytes": gradient_bytes,
        "optimizer_state_bytes_per_parameter": optimizer_state_bytes_per_parameter,
        "activation_bytes": activation_bytes,
    }
    for name, value in integer_values.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    if sequence_length > config.block_size:
        raise ValueError("sequence_length exceeds configured block_size")

    parameters = parameter_breakdown(config)["total"]
    parameter_storage = parameters * parameter_bytes
    gradient_storage = parameters * gradient_bytes
    optimizer_storage = parameters * optimizer_state_bytes_per_parameter
    persistent = parameter_storage + gradient_storage + optimizer_storage

    # Shape-based reference sizes for dense score-equivalent, FFN, and logits tensors.
    score_equivalent = (
        config.num_layers * batch_size * config.num_heads
        * sequence_length * sequence_length * activation_bytes
    )
    ffn_hidden = (
        config.num_layers * batch_size * sequence_length
        * config.ff_dim * activation_bytes
    )
    logits = batch_size * sequence_length * config.vocab_size * activation_bytes
    reference_activations = score_equivalent + ffn_hidden + logits
    return {
        "parameter_count": parameters,
        "parameter_bytes": parameter_storage,
        "gradient_bytes": gradient_storage,
        "adamw_state_bytes": optimizer_storage,
        "persistent_bytes": persistent,
        "persistent_mib": _mib(persistent),
        "attention_score_equivalent_bytes": score_equivalent,
        "ffn_hidden_bytes": ffn_hidden,
        "logits_bytes": logits,
        "reference_activation_bytes": reference_activations,
        "reference_activation_mib": _mib(reference_activations),
        "assumptions": {
            "parameter_bytes_per_value": parameter_bytes,
            "gradient_bytes_per_value": gradient_bytes,
            "adamw_state_bytes_per_parameter": optimizer_state_bytes_per_parameter,
            "activation_bytes_per_value": activation_bytes,
            "adamw_states": "two moment tensors; assumes both are allocated",
            "activation_note": (
                "shape-equivalent tensor sizes only; not peak memory, not an allocation "
                "trace, and not necessarily materialized by an optimized attention kernel"
            ),
            "excluded": [
                "optimizer metadata and allocator overhead",
                "input/target IDs, masks, residuals, Q/K/V, gradients of activations",
                "temporary workspaces, fragmentation, and device/runtime reservations",
            ],
        },
    }


def context_sweep(
    config: ModelConfig,
    context_lengths: tuple[int, ...] = (32, 64, 128),
    *,
    batch_size: int = 16,
    parameter_bytes: int = 4,
    gradient_bytes: int = 4,
    optimizer_state_bytes_per_parameter: int = 8,
    activation_bytes: int = 4,
) -> list[dict]:
    """Compare configurations whose maximum and actual sequence lengths match."""
    if not context_lengths:
        raise ValueError("context_lengths must not be empty")
    if any(isinstance(length, bool) or not isinstance(length, int) or length < 1 for length in context_lengths):
        raise ValueError("context_lengths must contain positive integers")
    if len(set(context_lengths)) != len(context_lengths):
        raise ValueError("context_lengths must be unique")
    rows = []
    for length in context_lengths:
        trial = replace(config, block_size=length)
        report = estimate_budget(
            trial,
            batch_size=batch_size,
            sequence_length=length,
            parameter_bytes=parameter_bytes,
            gradient_bytes=gradient_bytes,
            optimizer_state_bytes_per_parameter=optimizer_state_bytes_per_parameter,
            activation_bytes=activation_bytes,
        )
        rows.append({"context_length": length, **report})
    return rows


def design_report(
    config: ModelConfig,
    *,
    batch_size: int = 16,
    sequence_length: int | None = None,
    parameter_bytes: int = 4,
    gradient_bytes: int = 4,
    optimizer_state_bytes_per_parameter: int = 8,
    activation_bytes: int = 4,
) -> dict:
    """Check the formula against the module and return a random-token smoke report."""
    config.validate()
    sequence_length = config.block_size if sequence_length is None else sequence_length
    budget = estimate_budget(
        config,
        batch_size=batch_size,
        sequence_length=sequence_length,
        parameter_bytes=parameter_bytes,
        gradient_bytes=gradient_bytes,
        optimizer_state_bytes_per_parameter=optimizer_state_bytes_per_parameter,
        activation_bytes=activation_bytes,
    )
    model = build_model(config).eval()
    actual = count_parameters(model)
    formula = parameter_breakdown(config)["total"]
    if actual != formula:
        raise RuntimeError(f"parameter formula {formula} != model parameter count {actual}")
    torch.manual_seed(42)
    token_ids = torch.randint(0, config.vocab_size, (batch_size, sequence_length), dtype=torch.long)
    # A causal attention row with no visible non-padding key is undefined. The
    # real next-token sequence starts with a non-padding BOS/prefix token.
    token_ids[:, 0] = (config.pad_id + 1) % config.vocab_size
    with torch.no_grad():
        logits = model(token_ids)
    return {
        "config": asdict(config),
        "input_shape": list(token_ids.shape),
        "logits_shape": list(logits.shape),
        "all_logits_finite": bool(torch.isfinite(logits).all().item()),
        "parameter_breakdown": parameter_breakdown(config),
        "parameter_count_actual": actual,
        "budget": budget,
        "scope": "one random-token forward smoke test; no corpus, training, or quality evaluation",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Design and budget a tiny GPT-like decoder")
    parser.add_argument("--vocab-size", type=int, default=102)
    parser.add_argument("--block-size", type=int, default=64)
    parser.add_argument("--d-model", type=int, default=64)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--ff-dim", type=int, default=256)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--pad-id", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--sequence-length", type=int, default=None)
    parser.add_argument("--parameter-bytes", type=int, default=4)
    parser.add_argument("--gradient-bytes", type=int, default=4)
    parser.add_argument("--optimizer-state-bytes", type=int, default=8)
    parser.add_argument("--activation-bytes", type=int, default=4)
    parser.add_argument("--context-sweep", action="store_true", help="also compare contexts 32, 64, 128")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = ModelConfig(
        vocab_size=args.vocab_size,
        block_size=args.block_size,
        d_model=args.d_model,
        num_heads=args.heads,
        ff_dim=args.ff_dim,
        num_layers=args.layers,
        pad_id=args.pad_id,
    )
    report = design_report(
        config,
        batch_size=args.batch_size,
        sequence_length=args.sequence_length,
        parameter_bytes=args.parameter_bytes,
        gradient_bytes=args.gradient_bytes,
        optimizer_state_bytes_per_parameter=args.optimizer_state_bytes,
        activation_bytes=args.activation_bytes,
    )
    if args.context_sweep:
        report["context_sweep"] = context_sweep(
            config,
            batch_size=args.batch_size,
            parameter_bytes=args.parameter_bytes,
            gradient_bytes=args.gradient_bytes,
            optimizer_state_bytes_per_parameter=args.optimizer_state_bytes,
            activation_bytes=args.activation_bytes,
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
