"""Tiny CPU-friendly encoders for image, text, and audio alignment.

This pedagogical model demonstrates patch/token encoders, a shared embedding
space, symmetric contrastive learning, and text-query cross-attention to visual
and audio context. It uses random weights and synthetic features: it is not a
pretrained model, dataset, benchmark, or production multimodal assistant.
"""
from __future__ import annotations

import math

import torch
import torch.nn.functional as F
from torch import Tensor, nn


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def _masked_mean(tokens: Tensor, padding_mask: Tensor | None = None) -> Tensor:
    """Mean-pool [B,T,D], ignoring positions where a bool mask is True."""
    if padding_mask is None:
        return tokens.mean(dim=1)
    weights = (~padding_mask).unsqueeze(-1).to(tokens.dtype)
    return (tokens * weights).sum(dim=1) / weights.sum(dim=1).clamp_min(1.0)


def _transformer(d_model: int, num_heads: int, depth: int) -> nn.TransformerEncoder:
    layer = nn.TransformerEncoderLayer(
        d_model=d_model,
        nhead=num_heads,
        dim_feedforward=4 * d_model,
        dropout=0.0,
        activation="gelu",
        batch_first=True,
        norm_first=True,
    )
    return nn.TransformerEncoder(layer, num_layers=depth, enable_nested_tensor=False)


class VisionPatchEncoder(nn.Module):
    """Patchify a fixed-size batch of images and encode the patch sequence."""

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        *,
        patch_size: int = 8,
        image_channels: int = 3,
        max_patches: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(patch_size, "patch_size")
        _positive_int(image_channels, "image_channels")
        _positive_int(max_patches, "max_patches")
        _positive_int(depth, "depth")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.image_channels = image_channels
        self.patch_size = patch_size
        self.max_patches = max_patches
        self.patch_projection = nn.Conv2d(
            image_channels, d_model, kernel_size=patch_size, stride=patch_size
        )
        self.position = nn.Parameter(torch.zeros(1, max_patches, d_model))
        nn.init.normal_(self.position, std=0.02)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, images: Tensor) -> Tensor:
        if not isinstance(images, Tensor) or images.ndim != 4:
            raise ValueError("images must have shape [B,C,H,W]")
        if not images.is_floating_point():
            raise ValueError("images must be floating-point tensors")
        batch, channels, height, width = images.shape
        p = self.patch_size
        if batch < 1 or channels != self.image_channels or height < p or width < p:
            raise ValueError("images need a non-empty batch, configured channels, and at least one patch")
        if height % p or width % p:
            raise ValueError("image height and width must be divisible by patch_size")
        patches = self.patch_projection(images).flatten(2).transpose(1, 2)
        if patches.shape[1] > self.max_patches:
            raise ValueError("image produces more patches than max_patches")
        patches = self.encoder(patches + self.position[:, : patches.shape[1]])
        return self.norm(patches)


class TextTokenEncoder(nn.Module):
    """Encode token IDs with a padding-aware bidirectional Transformer."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        num_heads: int,
        *,
        pad_id: int = 0,
        max_length: int = 64,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(vocab_size, "vocab_size")
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(max_length, "max_length")
        _positive_int(depth, "depth")
        if isinstance(pad_id, bool) or not isinstance(pad_id, int) or not 0 <= pad_id < vocab_size:
            raise ValueError("pad_id must be a token ID in the vocabulary")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.vocab_size = vocab_size
        self.pad_id = pad_id
        self.max_length = max_length
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.position = nn.Embedding(max_length, d_model)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        token_ids: Tensor,
        padding_mask: Tensor | None = None,
    ) -> tuple[Tensor, Tensor]:
        if not isinstance(token_ids, Tensor) or token_ids.ndim != 2:
            raise ValueError("token_ids must have shape [B,L]")
        if token_ids.dtype != torch.long:
            raise ValueError("token_ids must use torch.long")
        batch, length = token_ids.shape
        if batch < 1 or length < 1 or length > self.max_length:
            raise ValueError("token batch must be non-empty and no longer than max_length")
        if bool(((token_ids < 0) | (token_ids >= self.vocab_size)).any()):
            raise ValueError("token_ids contain an ID outside the vocabulary")
        if padding_mask is None:
            padding_mask = token_ids.eq(self.pad_id)
        elif (
            not isinstance(padding_mask, Tensor)
            or padding_mask.dtype != torch.bool
            or tuple(padding_mask.shape) != tuple(token_ids.shape)
            or padding_mask.device != token_ids.device
        ):
            raise ValueError("padding_mask must be bool [B,L] on the token device; True means padding")
        if bool(padding_mask.all(dim=1).any()):
            raise ValueError("each text row must contain at least one unmasked token")
        positions = torch.arange(length, device=token_ids.device).unsqueeze(0)
        x = self.embedding(token_ids) + self.position(positions)
        x = self.encoder(x, src_key_padding_mask=padding_mask)
        x = self.norm(x).masked_fill(padding_mask.unsqueeze(-1), 0.0)
        return x, padding_mask


class AudioFrameEncoder(nn.Module):
    """Encode log-Mel-like [B,n_mels,T] features in fixed-size frame groups."""

    def __init__(
        self,
        n_mels: int,
        d_model: int,
        num_heads: int,
        *,
        frame_stride: int = 4,
        max_audio_tokens: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(n_mels, "n_mels")
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(frame_stride, "frame_stride")
        _positive_int(max_audio_tokens, "max_audio_tokens")
        _positive_int(depth, "depth")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.n_mels = n_mels
        self.frame_stride = frame_stride
        self.max_audio_tokens = max_audio_tokens
        self.frame_projection = nn.Conv1d(
            n_mels, d_model, kernel_size=frame_stride, stride=frame_stride
        )
        self.position = nn.Embedding(max_audio_tokens, d_model)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        features: Tensor,
        lengths: Tensor | None = None,
    ) -> tuple[Tensor, Tensor]:
        if not isinstance(features, Tensor) or features.ndim != 3:
            raise ValueError("audio features must have shape [B,n_mels,T]")
        if not features.is_floating_point():
            raise ValueError("audio features must be floating-point tensors")
        batch, n_mels, frames = features.shape
        stride = self.frame_stride
        if batch < 1 or n_mels != self.n_mels or frames < stride:
            raise ValueError("audio features need a non-empty batch, configured n_mels, and enough frames")
        if lengths is None:
            lengths = torch.full((batch,), frames, dtype=torch.long, device=features.device)
        elif (
            not isinstance(lengths, Tensor)
            or lengths.dtype != torch.long
            or tuple(lengths.shape) != (batch,)
            or lengths.device != features.device
        ):
            raise ValueError("lengths must be torch.long [B] on the feature device")
        if bool(((lengths < stride) | (lengths > frames)).any()):
            raise ValueError("each valid audio length must be between frame_stride and T")
        x = self.frame_projection(features).transpose(1, 2)
        if x.shape[1] > self.max_audio_tokens:
            raise ValueError("audio produces more tokens than max_audio_tokens")
        valid_tokens = torch.div(lengths, stride, rounding_mode="floor")
        padding_mask = (
            torch.arange(x.shape[1], device=features.device).unsqueeze(0)
            >= valid_tokens.unsqueeze(1)
        )
        positions = torch.arange(x.shape[1], device=features.device).unsqueeze(0)
        x = self.encoder(x + self.position(positions), src_key_padding_mask=padding_mask)
        x = self.norm(x).masked_fill(padding_mask.unsqueeze(-1), 0.0)
        return x, padding_mask


class TextCrossModalFusion(nn.Module):
    """Let text queries read image and audio token sequences via cross-attention."""

    def __init__(self, d_model: int, num_heads: int) -> None:
        super().__init__()
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.image_attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.audio_attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Linear(4 * d_model, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(
        self,
        text_tokens: Tensor,
        image_tokens: Tensor,
        audio_tokens: Tensor,
        text_padding_mask: Tensor,
        audio_padding_mask: Tensor,
    ) -> Tensor:
        image_context, _ = self.image_attention(
            text_tokens, image_tokens, image_tokens, need_weights=False
        )
        audio_context, _ = self.audio_attention(
            text_tokens,
            audio_tokens,
            audio_tokens,
            key_padding_mask=audio_padding_mask,
            need_weights=False,
        )
        fused = self.norm1(text_tokens + image_context + audio_context)
        fused = self.norm2(fused + self.feed_forward(fused))
        return fused.masked_fill(text_padding_mask.unsqueeze(-1), 0.0)


class TinyMultimodalAligner(nn.Module):
    """Three encoders with a shared space plus text-to-image/audio fusion.

    Inputs are normalized image tensors, text token IDs and log-Mel-like audio
    features. The returned shared embeddings suit contrastive retrieval demos;
    ``fused_text_tokens`` illustrates cross-attention but is not a generator.
    """

    def __init__(
        self,
        vocab_size: int = 64,
        *,
        pad_id: int = 0,
        n_mels: int = 16,
        d_model: int = 32,
        embed_dim: int = 16,
        num_heads: int = 4,
        patch_size: int = 8,
        max_image_patches: int = 256,
        max_text_length: int = 64,
        audio_frame_stride: int = 4,
        max_audio_tokens: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        for name, value in (
            ("vocab_size", vocab_size), ("n_mels", n_mels), ("d_model", d_model),
            ("embed_dim", embed_dim), ("num_heads", num_heads), ("depth", depth),
        ):
            _positive_int(value, name)
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.vision = VisionPatchEncoder(
            d_model, num_heads, patch_size=patch_size,
            max_patches=max_image_patches, depth=depth,
        )
        self.text = TextTokenEncoder(
            vocab_size, d_model, num_heads, pad_id=pad_id,
            max_length=max_text_length, depth=depth,
        )
        self.audio = AudioFrameEncoder(
            n_mels, d_model, num_heads, frame_stride=audio_frame_stride,
            max_audio_tokens=max_audio_tokens, depth=depth,
        )
        self.fusion = TextCrossModalFusion(d_model, num_heads)
        self.image_projection = nn.Linear(d_model, embed_dim)
        self.text_projection = nn.Linear(d_model, embed_dim)
        self.audio_projection = nn.Linear(d_model, embed_dim)
        self.fused_projection = nn.Linear(d_model, embed_dim)

    def forward(
        self,
        images: Tensor,
        token_ids: Tensor,
        audio_features: Tensor,
        *,
        text_padding_mask: Tensor | None = None,
        audio_lengths: Tensor | None = None,
    ) -> dict[str, Tensor]:
        if not all(isinstance(value, Tensor) for value in (images, token_ids, audio_features)):
            raise ValueError("all modality inputs must be tensors")
        if images.ndim != 4 or token_ids.ndim != 2 or audio_features.ndim != 3:
            raise ValueError("inputs must be images [B,C,H,W], tokens [B,L], and audio [B,F,T]")
        batch = images.shape[0]
        if token_ids.shape[0] != batch or audio_features.shape[0] != batch or batch < 1:
            raise ValueError("image, text, and audio batches must have the same non-zero size")
        if images.device != token_ids.device or images.device != audio_features.device:
            raise ValueError("all modalities must be on the same device")

        image_tokens = self.vision(images)
        text_tokens, text_mask = self.text(token_ids, text_padding_mask)
        audio_tokens, audio_mask = self.audio(audio_features, audio_lengths)
        image_pooled = image_tokens.mean(dim=1)
        text_pooled = _masked_mean(text_tokens, text_mask)
        audio_pooled = _masked_mean(audio_tokens, audio_mask)
        fused_text_tokens = self.fusion(
            text_tokens, image_tokens, audio_tokens, text_mask, audio_mask
        )
        fused_text_pooled = _masked_mean(fused_text_tokens, text_mask)

        return {
            "image_tokens": image_tokens,
            "text_tokens": text_tokens,
            "audio_tokens": audio_tokens,
            "audio_padding_mask": audio_mask,
            "text_padding_mask": text_mask,
            "fused_text_tokens": fused_text_tokens,
            "image_embedding": F.normalize(self.image_projection(image_pooled), dim=-1),
            "text_embedding": F.normalize(self.text_projection(text_pooled), dim=-1),
            "audio_embedding": F.normalize(self.audio_projection(audio_pooled), dim=-1),
            "fused_embedding": F.normalize(self.fused_projection(fused_text_pooled), dim=-1),
        }


def symmetric_info_nce(
    first: Tensor,
    second: Tensor,
    *,
    logit_scale: float = 10.0,
) -> Tensor:
    """Symmetric in-batch InfoNCE for aligned [B,D] pairs, with B >= 2.

    The diagonal entries are the positive pairs; other entries are negatives
    for this batch. ``logit_scale`` is a positive multiplier, not log(scale).
    """
    if not isinstance(first, Tensor) or not isinstance(second, Tensor):
        raise ValueError("first and second must be tensors")
    if first.ndim != 2 or second.ndim != 2 or first.shape != second.shape:
        raise ValueError("embeddings must share the same [B,D] shape")
    if first.shape[0] < 2 or first.shape[1] < 1:
        raise ValueError("InfoNCE needs at least two paired examples and one feature")
    if not first.is_floating_point() or not second.is_floating_point():
        raise ValueError("embeddings must be floating point")
    if first.device != second.device or first.dtype != second.dtype:
        raise ValueError("embeddings must share device and dtype")
    if (
        isinstance(logit_scale, bool)
        or not isinstance(logit_scale, (int, float))
        or not math.isfinite(logit_scale)
        or logit_scale <= 0
    ):
        raise ValueError("logit_scale must be a finite positive number")
    a = F.normalize(first, dim=-1)
    b = F.normalize(second, dim=-1)
    logits = logit_scale * (a @ b.transpose(0, 1))
    labels = torch.arange(first.shape[0], device=first.device)
    return (F.cross_entropy(logits, labels) + F.cross_entropy(logits.T, labels)) / 2


def three_way_contrastive_loss(
    image_embeddings: Tensor,
    text_embeddings: Tensor,
    audio_embeddings: Tensor,
    *,
    logit_scale: float = 10.0,
) -> Tensor:
    """Average symmetric image-text, image-audio and text-audio objectives."""
    return (
        symmetric_info_nce(image_embeddings, text_embeddings, logit_scale=logit_scale)
        + symmetric_info_nce(image_embeddings, audio_embeddings, logit_scale=logit_scale)
        + symmetric_info_nce(text_embeddings, audio_embeddings, logit_scale=logit_scale)
    ) / 3.0


def demo() -> None:
    torch.manual_seed(39)
    model = TinyMultimodalAligner(d_model=32, embed_dim=16, num_heads=4)
    images = torch.rand(4, 3, 32, 32)
    token_ids = torch.tensor([
        [1, 7, 8, 0, 0, 0],
        [1, 9, 10, 11, 0, 0],
        [1, 12, 13, 0, 0, 0],
        [1, 14, 15, 16, 17, 0],
    ], dtype=torch.long)
    audio = torch.randn(4, 16, 64)  # synthetic log-Mel-like features, not waveforms
    audio_lengths = torch.tensor([64, 56, 48, 40], dtype=torch.long)
    output = model(images, token_ids, audio, audio_lengths=audio_lengths)
    loss = three_way_contrastive_loss(
        output["image_embedding"], output["text_embedding"], output["audio_embedding"]
    )
    loss.backward()
    print(f"shared embeddings: {tuple(output['image_embedding'].shape)} per modality")
    print(f"fused text tokens: {tuple(output['fused_text_tokens'].shape)}")
    print(f"synthetic three-way InfoNCE: {loss.item():.4f}")
    print(f"finite loss and gradients: {bool(torch.isfinite(loss)) and model.vision.patch_projection.weight.grad is not None}")


if __name__ == "__main__":
    demo()
