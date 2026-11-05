"""Position schemes and a compact Transformer block for volume 3 chapter 36."""
from __future__ import annotations

import math

import torch
from torch import nn


def _positive_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def sinusoidal_encoding(
    length: int,
    d_model: int,
    *,
    positions: torch.Tensor | None = None,
    device: torch.device | str | None = None,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Return [length, d_model] sinusoidal absolute position encodings.

    Odd model dimensions are supported; the last even coordinate simply has no
    paired odd coordinate. Positions are shared by all examples in the batch.
    """
    _positive_int("length", length)
    _positive_int("d_model", d_model)
    if not isinstance(dtype, torch.dtype) or not dtype.is_floating_point:
        raise TypeError("dtype must be a floating-point torch.dtype")

    if positions is None:
        pos = torch.arange(length, device=device, dtype=torch.int64)
    else:
        pos = torch.as_tensor(positions, device=device)
        if pos.ndim != 1 or pos.numel() != length:
            raise ValueError("positions must be a rank-1 vector with one value per token")
        if pos.dtype == torch.bool or pos.is_floating_point() or pos.is_complex():
            raise TypeError("positions must use an integer dtype")
        if torch.any(pos < 0).item():
            raise ValueError("positions must be non-negative")

    work_dtype = torch.float64 if dtype == torch.float64 else torch.float32
    pos = pos.to(dtype=work_dtype).unsqueeze(1)
    pair_indices = torch.arange(0, d_model, 2, device=pos.device, dtype=work_dtype)
    frequencies = torch.exp(pair_indices * (-math.log(10000.0) / d_model))
    angles = pos * frequencies.unsqueeze(0)

    encoding = torch.zeros(length, d_model, device=pos.device, dtype=work_dtype)
    encoding[:, 0::2] = torch.sin(angles)
    odd_count = encoding[:, 1::2].shape[1]
    if odd_count:
        encoding[:, 1::2] = torch.cos(angles[:, :odd_count])
    return encoding.to(dtype=dtype)


def apply_rope(
    x: torch.Tensor,
    positions: torch.Tensor | None = None,
    *,
    base: float = 10000.0,
) -> torch.Tensor:
    """Apply RoPE to [batch, heads, length, head_dim] query/key vectors.

    Coordinates are paired as (0,1), (2,3), ... . RoPE rotates queries and
    keys, not values. The teaching implementation uses one shared position
    vector for the batch and requires an even head dimension.
    """
    if not isinstance(x, torch.Tensor):
        raise TypeError("x must be a torch.Tensor")
    if x.ndim != 4:
        raise ValueError("expected [batch, heads, length, head_dim] input")
    if not x.is_floating_point():
        raise TypeError("x must have floating-point dtype")
    if x.size(-1) == 0 or x.size(-1) % 2:
        raise ValueError("head_dim must be a positive even integer for RoPE")
    if isinstance(base, bool) or not isinstance(base, (int, float)):
        raise TypeError("base must be a positive finite number")
    if not math.isfinite(base) or base <= 0:
        raise ValueError("base must be a positive finite number")

    length, head_dim = x.size(-2), x.size(-1)
    if length == 0:
        raise ValueError("sequence length must be positive")
    if positions is None:
        pos = torch.arange(length, device=x.device, dtype=torch.int64)
    else:
        pos = torch.as_tensor(positions, device=x.device)
        if pos.ndim != 1 or pos.numel() != length:
            raise ValueError("positions must be a rank-1 vector with one value per token")
        if pos.dtype == torch.bool or pos.is_floating_point() or pos.is_complex():
            raise TypeError("positions must use an integer dtype")
        if torch.any(pos < 0).item():
            raise ValueError("positions must be non-negative")

    work_dtype = torch.float64 if x.dtype == torch.float64 else torch.float32
    pair_indices = torch.arange(0, head_dim, 2, device=x.device, dtype=work_dtype)
    inv_freq = torch.exp(pair_indices * (-math.log(float(base)) / head_dim))
    angles = pos.to(dtype=work_dtype).unsqueeze(1) * inv_freq.unsqueeze(0)
    cos = angles.cos().to(dtype=x.dtype)[None, None, :, :]
    sin = angles.sin().to(dtype=x.dtype)[None, None, :, :]

    even, odd = x[..., 0::2], x[..., 1::2]
    rotated = torch.empty_like(x)
    rotated[..., 0::2] = even * cos - odd * sin
    rotated[..., 1::2] = even * sin + odd * cos
    return rotated


class PositionAwareTransformerBlock(nn.Module):
    """Single batch-first, full self-attention block with visible sublayers.

    `position_mode` is either `sinusoidal` (add to the residual stream) or
    `rope` (rotate Q and K). `norm_order` is `pre` or `post`. This block has no
    causal/padding mask or dropout; it is an encoder-style teaching example.
    """

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int | None = None,
        *,
        position_mode: str = "sinusoidal",
        norm_order: str = "pre",
        rope_base: float = 10000.0,
    ) -> None:
        super().__init__()
        _positive_int("d_model", d_model)
        _positive_int("num_heads", num_heads)
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        if position_mode not in {"sinusoidal", "rope"}:
            raise ValueError("position_mode must be 'sinusoidal' or 'rope'")
        if norm_order not in {"pre", "post"}:
            raise ValueError("norm_order must be 'pre' or 'post'")
        if position_mode == "rope" and (d_model // num_heads) % 2:
            raise ValueError("RoPE requires an even head_dim")
        if isinstance(rope_base, bool) or not isinstance(rope_base, (int, float)):
            raise TypeError("rope_base must be a positive finite number")
        if not math.isfinite(rope_base) or rope_base <= 0:
            raise ValueError("rope_base must be a positive finite number")

        if d_ff is None:
            d_ff = 4 * d_model
        _positive_int("d_ff", d_ff)
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.position_mode = position_mode
        self.norm_order = norm_order
        self.rope_base = float(rope_base)

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )

    def _self_attention(self, x: torch.Tensor, positions: torch.Tensor | None) -> torch.Tensor:
        batch, length, _ = x.shape
        qkv = self.qkv(x).view(batch, length, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        query, key, value = qkv.unbind(dim=0)
        if self.position_mode == "rope":
            query = apply_rope(query, positions, base=self.rope_base)
            key = apply_rope(key, positions, base=self.rope_base)

        scores = query @ key.transpose(-2, -1) / math.sqrt(self.head_dim)
        weights = torch.softmax(scores, dim=-1)
        per_head = weights @ value
        combined = per_head.transpose(1, 2).contiguous().view(batch, length, self.d_model)
        return self.out_proj(combined)

    def forward(self, x: torch.Tensor, positions: torch.Tensor | None = None) -> torch.Tensor:
        if not isinstance(x, torch.Tensor):
            raise TypeError("x must be a torch.Tensor")
        if x.ndim != 3:
            raise ValueError("expected [batch, sequence, d_model] input")
        if not x.is_floating_point():
            raise TypeError("x must have floating-point dtype")
        if x.size(1) == 0:
            raise ValueError("sequence length must be positive")
        if x.size(-1) != self.d_model:
            raise ValueError("input feature dimension must equal d_model")
        if x.device != self.qkv.weight.device:
            raise ValueError("input and module must be on the same device")
        if x.dtype != self.qkv.weight.dtype:
            raise TypeError("input and module must use the same dtype")

        if self.position_mode == "sinusoidal":
            encoding = sinusoidal_encoding(
                x.size(1), self.d_model, positions=positions,
                device=x.device, dtype=x.dtype,
            )
            x = x + encoding.unsqueeze(0)

        if self.norm_order == "pre":
            x = x + self._self_attention(self.norm1(x), positions)
            x = x + self.ffn(self.norm2(x))
        else:
            x = self.norm1(x + self._self_attention(x, positions))
            x = self.norm2(x + self.ffn(x))
        return x


def main() -> None:
    torch.manual_seed(3601)
    x = torch.randn(2, 6, 16)
    model = PositionAwareTransformerBlock(
        d_model=16, num_heads=4, position_mode="rope", norm_order="pre"
    ).eval()
    positions = torch.arange(10, 16)
    with torch.no_grad():
        output = model(x, positions)
    encoding = sinusoidal_encoding(6, 16)
    print("device=cpu")
    print("mode=rope, norm_order=pre")
    print("input_shape=", tuple(x.shape))
    print("output_shape=", tuple(output.shape))
    print("sinusoidal_shape=", tuple(encoding.shape))
    print("output_finite=", torch.isfinite(output).all().item())


if __name__ == "__main__":
    main()
