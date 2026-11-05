"""Small CPU-friendly demos for KV cache, GQA, local masks, and Switch top-1 MoE.

This is instructional PyTorch code, not a fused or benchmarked GPU kernel.
The attention routine intentionally materializes dense score tensors; a boolean
local mask demonstrates semantics but does not itself skip dense computation.
"""
from __future__ import annotations

import math
from typing import Final

import torch
from torch import Tensor, nn


_INT_FIELDS: Final = (
    "query_length", "key_length", "window_size", "num_layers", "batch_size",
    "sequence_length", "num_kv_heads", "head_dim", "bytes_per_element",
)


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def causal_allowed_mask(
    query_length: int,
    key_length: int,
    *,
    query_offset: int | None = None,
    device: torch.device | str | None = None,
) -> Tensor:
    """Return [Tq,Tk] bool mask where True means that a query may read a key.

    With cached decoding, the default places the query block at the end of the
    key sequence. For example, Tq=1,Tk=5 lets the query read all five keys.
    """
    _positive_int(query_length, "query_length")
    _positive_int(key_length, "key_length")
    offset = key_length - query_length if query_offset is None else query_offset
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("query_offset must be a non-negative integer")
    if offset + query_length > key_length:
        raise ValueError("query positions must lie within the key sequence")
    q_positions = torch.arange(query_length, device=device) + offset
    k_positions = torch.arange(key_length, device=device)
    return k_positions.unsqueeze(0) <= q_positions.unsqueeze(1)


def local_causal_allowed_mask(
    query_length: int,
    key_length: int,
    window_size: int,
    *,
    query_offset: int | None = None,
    device: torch.device | str | None = None,
) -> Tensor:
    """Causal window: each query reads itself and at most window_size-1 past keys."""
    _positive_int(window_size, "window_size")
    allowed = causal_allowed_mask(
        query_length, key_length, query_offset=query_offset, device=device
    )
    offset = key_length - query_length if query_offset is None else query_offset
    q_positions = torch.arange(query_length, device=device) + offset
    k_positions = torch.arange(key_length, device=device)
    recent_enough = k_positions.unsqueeze(0) >= (
        q_positions.unsqueeze(1) - window_size + 1
    )
    return allowed & recent_enough


def grouped_query_attention(
    query: Tensor,
    key: Tensor,
    value: Tensor,
    *,
    causal: bool = False,
    local_window: int | None = None,
    query_offset: int | None = None,
    allowed_mask: Tensor | None = None,
) -> tuple[Tensor, Tensor]:
    """Compute a transparent GQA reference attention.

    Shapes: query [B,Hq,Tq,D], key/value [B,Hkv,Tk,D], with Hq divisible by
    Hkv. Query heads are arranged in contiguous groups that share one KV head.
    ``allowed_mask`` is bool [Tq,Tk] or [B,Tq,Tk], and True means allowed.
    Returns output [B,Hq,Tq,D] and probabilities [B,Hq,Tq,Tk].

    This reference expands work into a dense score tensor. It checks behavior;
    it does not provide sparse or production-kernel speedups.
    """
    tensors = (query, key, value)
    if any(not isinstance(tensor, Tensor) or tensor.ndim != 4 for tensor in tensors):
        raise ValueError("query, key, and value must be rank-4 tensors")
    if any(not tensor.is_floating_point() for tensor in tensors):
        raise ValueError("query, key, and value must use floating-point dtypes")
    if query.device != key.device or key.device != value.device:
        raise ValueError("query, key, and value must be on the same device")
    if query.dtype != key.dtype or key.dtype != value.dtype:
        raise ValueError("query, key, and value must have the same dtype")
    batch, query_heads, query_length, head_dim = query.shape
    key_batch, kv_heads, key_length, key_dim = key.shape
    if batch < 1 or query_heads < 1 or query_length < 1 or key_length < 1 or head_dim < 1:
        raise ValueError("batch, head counts, sequence lengths, and head_dim must be positive")
    if key_batch != batch or value.shape != key.shape:
        raise ValueError("key and value must have matching [B,Hkv,Tk,D] shapes")
    if key_dim != head_dim:
        raise ValueError("query, key, and value head dimensions must match")
    if kv_heads < 1 or query_heads % kv_heads != 0:
        raise ValueError("the positive number of query heads must be divisible by KV heads")
    if not isinstance(causal, bool):
        raise ValueError("causal must be a bool")
    if local_window is not None:
        _positive_int(local_window, "local_window")
        if not causal:
            raise ValueError("local_window is supported only with causal=True")
    if query_offset is not None and not causal:
        raise ValueError("query_offset is meaningful only with causal=True")

    mask: Tensor | None = None
    if causal:
        if local_window is None:
            mask = causal_allowed_mask(
                query_length, key_length, query_offset=query_offset, device=query.device
            )
        else:
            mask = local_causal_allowed_mask(
                query_length, key_length, local_window,
                query_offset=query_offset, device=query.device,
            )
    if allowed_mask is not None:
        if allowed_mask.dtype != torch.bool or allowed_mask.device != query.device:
            raise ValueError("allowed_mask must be a bool tensor on the query device")
        valid_shapes = ((query_length, key_length), (batch, query_length, key_length))
        if tuple(allowed_mask.shape) not in valid_shapes:
            raise ValueError("allowed_mask must have shape [Tq,Tk] or [B,Tq,Tk]")
        mask = allowed_mask if mask is None else (mask & allowed_mask)
    if mask is not None and not bool(mask.any(dim=-1).all()):
        raise ValueError("every query must have at least one allowed key")

    groups = query_heads // kv_heads
    grouped_query = query.reshape(batch, kv_heads, groups, query_length, head_dim)
    scores = torch.einsum("bhgqd,bhkd->bhgqk", grouped_query, key)
    scores = scores / math.sqrt(head_dim)
    if mask is not None:
        expanded_mask = mask if mask.ndim == 2 else mask[:, None, None, :, :]
        scores = scores.masked_fill(~expanded_mask, torch.finfo(scores.dtype).min)
    work_dtype = torch.float32 if scores.dtype in (torch.float16, torch.bfloat16) else scores.dtype
    probabilities = torch.softmax(scores.to(work_dtype), dim=-1).to(query.dtype)
    grouped_output = torch.einsum("bhgqk,bhkd->bhgqd", probabilities, value)
    output = grouped_output.reshape(batch, query_heads, query_length, head_dim)
    return output, probabilities.reshape(batch, query_heads, query_length, key_length)


class KVCache:
    """Minimal append-only self-attention KV cache for a decoding demonstration.

    ``torch.cat`` copies existing data on append; real serving systems commonly
    preallocate or page KV blocks instead. This class is deliberately simple.
    """
    def __init__(self) -> None:
        self.key: Tensor | None = None
        self.value: Tensor | None = None

    @property
    def num_tokens(self) -> int:
        return 0 if self.key is None else int(self.key.shape[2])

    def append(self, key: Tensor, value: Tensor) -> tuple[Tensor, Tensor]:
        if (not isinstance(key, Tensor) or not isinstance(value, Tensor)
                or key.ndim != 4 or value.ndim != 4):
            raise ValueError("new key and value must be rank-4 [B,Hkv,T,D] tensors")
        if key.shape != value.shape or any(size < 1 for size in key.shape):
            raise ValueError("new key and value must have matching, non-empty shapes")
        if key.device != value.device or key.dtype != value.dtype:
            raise ValueError("new key and value must share device and dtype")
        if not key.is_floating_point():
            raise ValueError("new key and value must be floating point")
        if self.key is None:
            self.key, self.value = key, value
        else:
            assert self.value is not None
            if key.shape[:2] != self.key.shape[:2] or key.shape[3] != self.key.shape[3]:
                raise ValueError("new cache chunk has incompatible batch, head, or feature size")
            if key.device != self.key.device or key.dtype != self.key.dtype:
                raise ValueError("new cache chunk must share the existing device and dtype")
            self.key = torch.cat((self.key, key), dim=2)
            self.value = torch.cat((self.value, value), dim=2)
        return self.key, self.value

    def get(self) -> tuple[Tensor, Tensor]:
        if self.key is None or self.value is None:
            raise ValueError("the KV cache is empty")
        return self.key, self.value



def estimate_kv_cache_bytes(
    *,
    num_layers: int,
    batch_size: int,
    sequence_length: int,
    num_kv_heads: int,
    head_dim: int,
    bytes_per_element: int = 2,
) -> int:
    """Estimate self-attention K+V bytes; excludes weights, workspaces, and metadata."""
    values = {
        "num_layers": num_layers,
        "batch_size": batch_size,
        "sequence_length": sequence_length,
        "num_kv_heads": num_kv_heads,
        "head_dim": head_dim,
        "bytes_per_element": bytes_per_element,
    }
    for name, value in values.items():
        _positive_int(value, name)
    return (
        2 * num_layers * batch_size * sequence_length * num_kv_heads
        * head_dim * bytes_per_element
    )


def switch_top1_load_balance_loss(
    probabilities: Tensor,
    selected_experts: Tensor,
    *,
    alpha: float = 1.0,
) -> Tensor:
    """Switch-style top-1 auxiliary loss: alpha * E * sum_i(f_i * P_i).

    ``probabilities`` is [N,E], ``selected_experts`` is [N]. This formula is
    the simple top-1 case; it is not a universal loss for top-k MoE routers.
    """
    if probabilities.ndim != 2 or selected_experts.ndim != 1:
        raise ValueError("probabilities must be [N,E] and selected_experts [N]")
    token_count, expert_count = probabilities.shape
    if token_count < 1 or expert_count < 2 or selected_experts.shape[0] != token_count:
        raise ValueError("load-balancing inputs must contain tokens and at least two experts")
    if not probabilities.is_floating_point() or selected_experts.dtype != torch.long:
        raise ValueError("probabilities must be floating point and selections torch.long")
    if probabilities.device != selected_experts.device:
        raise ValueError("probabilities and selections must be on the same device")
    if not math.isfinite(alpha) or alpha < 0:
        raise ValueError("alpha must be finite and non-negative")
    if not bool(torch.isfinite(probabilities).all()) or bool((probabilities < 0).any()):
        raise ValueError("router probabilities must be finite and non-negative")
    row_sums = probabilities.sum(dim=-1)
    if not torch.allclose(row_sums, torch.ones_like(row_sums), atol=1e-5, rtol=1e-5):
        raise ValueError("each router probability row must sum to one")
    if bool((selected_experts < 0).any()) or bool((selected_experts >= expert_count).any()):
        raise ValueError("selected expert index is outside the expert range")

    fractions = torch.nn.functional.one_hot(
        selected_experts, num_classes=expert_count
    ).to(probabilities.dtype).mean(dim=0).detach()
    mean_probability = probabilities.mean(dim=0)
    return alpha * expert_count * torch.sum(fractions * mean_probability)


class SwitchTop1MoE(nn.Module):
    """Small token-routed top-1 MoE; no capacity limit or distributed dispatch."""
    def __init__(
        self,
        d_model: int,
        hidden_dim: int,
        num_experts: int = 4,
        *,
        aux_loss_weight: float = 0.01,
    ) -> None:
        super().__init__()
        _positive_int(d_model, "d_model")
        _positive_int(hidden_dim, "hidden_dim")
        if isinstance(num_experts, bool) or not isinstance(num_experts, int) or num_experts < 2:
            raise ValueError("num_experts must be an integer of at least two")
        if not math.isfinite(aux_loss_weight) or aux_loss_weight < 0:
            raise ValueError("aux_loss_weight must be finite and non-negative")
        self.d_model = d_model
        self.num_experts = num_experts
        self.aux_loss_weight = float(aux_loss_weight)
        self.router = nn.Linear(d_model, num_experts, bias=True)
        self.experts = nn.ModuleList(
            nn.Sequential(
                nn.Linear(d_model, hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, d_model),
            )
            for _ in range(num_experts)
        )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        if not isinstance(x, Tensor) or x.ndim not in (2, 3):
            raise ValueError("x must have shape [N,D] or [B,T,D]")
        if x.shape[-1] != self.d_model or any(size < 1 for size in x.shape):
            raise ValueError("x must be non-empty and end with d_model features")
        if not x.is_floating_point():
            raise ValueError("x must be a floating-point tensor")
        original_shape = x.shape
        flat = x.reshape(-1, self.d_model)
        probabilities = torch.softmax(self.router(flat), dim=-1)
        selected = probabilities.argmax(dim=-1)
        selected_probability = probabilities.gather(1, selected[:, None]).squeeze(1)

        output = torch.zeros_like(flat)
        for expert_index, expert in enumerate(self.experts):
            token_indices = torch.nonzero(selected == expert_index, as_tuple=True)[0]
            if token_indices.numel() == 0:
                continue
            expert_input = flat.index_select(0, token_indices)
            expert_output = expert(expert_input)
            gate_weight = selected_probability.index_select(0, token_indices).unsqueeze(-1)
            output = output.index_add(0, token_indices, expert_output * gate_weight)

        aux_loss = switch_top1_load_balance_loss(
            probabilities, selected, alpha=self.aux_loss_weight
        )
        return output.reshape(original_shape), aux_loss, selected.reshape(original_shape[:-1])


def demo() -> None:
    torch.manual_seed(38)
    batch, query_heads, kv_heads, length, head_dim = 1, 8, 2, 5, 16
    query = torch.randn(batch, query_heads, length, head_dim)
    key = torch.randn(batch, kv_heads, length, head_dim)
    value = torch.randn_like(key)
    output, _ = grouped_query_attention(query, key, value, causal=True)
    print(f"causal GQA output: {tuple(output.shape)}")

    cache = KVCache()
    cached_key, cached_value = cache.append(key[:, :, :2], value[:, :, :2])
    cached_key, cached_value = cache.append(key[:, :, 2:3], value[:, :, 2:3])
    print(f"KV cache tokens after two appends: {cache.num_tokens}")
    print(f"cached shapes: {tuple(cached_key.shape)}, {tuple(cached_value.shape)}")

    gqa_bytes = estimate_kv_cache_bytes(
        num_layers=32, batch_size=1, sequence_length=32768,
        num_kv_heads=8, head_dim=128, bytes_per_element=2,
    )
    mha_bytes = estimate_kv_cache_bytes(
        num_layers=32, batch_size=1, sequence_length=32768,
        num_kv_heads=32, head_dim=128, bytes_per_element=2,
    )
    print(f"illustrative 32K BF16 cache: GQA-8={gqa_bytes / 2**30:.1f} GiB; MHA={mha_bytes / 2**30:.1f} GiB")

    moe = SwitchTop1MoE(d_model=16, hidden_dim=32, num_experts=4)
    hidden = torch.randn(2, 3, 16)
    moe_output, aux_loss, expert_ids = moe(hidden)
    print(f"top-1 MoE output: {tuple(moe_output.shape)}; aux_loss={aux_loss.item():.4f}")
    print(f"selected expert IDs: {expert_ids.tolist()}")


if __name__ == "__main__":
    demo()
