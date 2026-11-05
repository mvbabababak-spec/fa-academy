"""Small CPU-friendly examples of encoder-only, decoder-only and seq2seq Transformers.

The module is instructional, not a pretrained language model. Boolean attention
masks follow PyTorch nn.MultiheadAttention 2.6 semantics: True means blocked.
"""
from __future__ import annotations

import torch
from torch import Tensor, nn


def _check_config(vocab_size: int, d_model: int, num_heads: int, ff_dim: int,
                  num_layers: int, max_len: int, pad_id: int) -> None:
    if vocab_size < 2:
        raise ValueError("vocab_size must be at least 2")
    if d_model < 1 or num_heads < 1 or d_model % num_heads:
        raise ValueError("d_model must be positive and divisible by num_heads")
    if ff_dim < 1 or num_layers < 1 or max_len < 1:
        raise ValueError("ff_dim, num_layers and max_len must be positive")
    if not 0 <= pad_id < vocab_size:
        raise ValueError("pad_id must be a valid vocabulary id")


def _check_tokens(token_ids: Tensor, vocab_size: int, name: str) -> None:
    if not isinstance(token_ids, Tensor) or token_ids.ndim != 2:
        raise ValueError(f"{name} must have shape [batch, length]")
    if token_ids.dtype != torch.long:
        raise ValueError(f"{name} must use torch.long token ids")
    if token_ids.shape[0] < 1 or token_ids.shape[1] < 1:
        raise ValueError(f"{name} must contain a non-empty batch and sequence")
    if token_ids.min().item() < 0 or token_ids.max().item() >= vocab_size:
        raise ValueError(f"{name} contains an id outside the vocabulary")


def _check_padding_mask(mask: Tensor | None, token_ids: Tensor, name: str) -> Tensor | None:
    if mask is None:
        return None
    if mask.dtype != torch.bool or tuple(mask.shape) != tuple(token_ids.shape):
        raise ValueError(f"{name} must be a boolean tensor with the same [batch, length] shape")
    return mask


def make_padding_mask(token_ids: Tensor, pad_id: int = 0) -> Tensor:
    """Return True at padding tokens, the key_padding_mask convention in PyTorch."""
    if token_ids.ndim != 2 or token_ids.dtype != torch.long:
        raise ValueError("token_ids must be a rank-2 torch.long tensor")
    if pad_id < 0:
        raise ValueError("pad_id must be non-negative")
    return token_ids.eq(pad_id)


def causal_mask(length: int, device: torch.device | None = None) -> Tensor:
    """Boolean [T,T] mask: True blocks keys strictly to the right of each query."""
    if length < 1:
        raise ValueError("length must be positive")
    return torch.ones((length, length), dtype=torch.bool, device=device).triu(1)


def shift_right(target_ids: Tensor, bos_id: int) -> Tensor:
    """Teacher-forcing input: [BOS, y0, ..., y_(T-2)] for target [y0, ..., y_(T-1)]."""
    if target_ids.ndim != 2 or target_ids.dtype != torch.long:
        raise ValueError("target_ids must be a rank-2 torch.long tensor")
    if target_ids.shape[0] < 1 or target_ids.shape[1] < 1 or bos_id < 0:
        raise ValueError("target_ids and bos_id must be non-empty/non-negative")
    bos = torch.full((target_ids.shape[0], 1), bos_id,
                     dtype=torch.long, device=target_ids.device)
    return torch.cat((bos, target_ids[:, :-1]), dim=1)


class TokenPositionEmbedding(nn.Module):
    """Learned token plus absolute position embeddings for a teaching example."""
    def __init__(self, vocab_size: int, d_model: int, max_len: int, pad_id: int) -> None:
        super().__init__()
        self.max_len = max_len
        self.token = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.position = nn.Embedding(max_len, d_model)

    def forward(self, token_ids: Tensor) -> Tensor:
        length = token_ids.shape[1]
        if length > self.max_len:
            raise ValueError(f"sequence length {length} exceeds max_len={self.max_len}")
        positions = torch.arange(length, device=token_ids.device).unsqueeze(0)
        return self.token(token_ids) + self.position(positions)


class BidirectionalEncoderBlock(nn.Module):
    """Pre-LN encoder block: unmasked self-attention, then a position-wise FFN."""
    def __init__(self, d_model: int, num_heads: int, ff_dim: int) -> None:
        super().__init__()
        self.norm_attn = nn.LayerNorm(d_model)
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(nn.Linear(d_model, ff_dim), nn.GELU(), nn.Linear(ff_dim, d_model))

    def forward(self, x: Tensor, key_padding_mask: Tensor | None = None) -> Tensor:
        qkv = self.norm_attn(x)
        attended, _ = self.self_attn(
            qkv, qkv, qkv, key_padding_mask=key_padding_mask, need_weights=False
        )
        x = x + attended
        return x + self.ff(self.norm_ff(x))


class CausalDecoderBlock(nn.Module):
    """Pre-LN decoder-only block: causal self-attention and a position-wise FFN."""
    def __init__(self, d_model: int, num_heads: int, ff_dim: int) -> None:
        super().__init__()
        self.norm_attn = nn.LayerNorm(d_model)
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(nn.Linear(d_model, ff_dim), nn.GELU(), nn.Linear(ff_dim, d_model))

    def forward(self, x: Tensor, key_padding_mask: Tensor | None = None) -> Tensor:
        qkv = self.norm_attn(x)
        attended, _ = self.self_attn(
            qkv, qkv, qkv,
            attn_mask=causal_mask(x.shape[1], device=x.device),
            key_padding_mask=key_padding_mask,
            need_weights=False,
        )
        x = x + attended
        return x + self.ff(self.norm_ff(x))


class EncoderDecoderBlock(nn.Module):
    """Decoder block with causal self-attention, source cross-attention and an FFN."""
    def __init__(self, d_model: int, num_heads: int, ff_dim: int) -> None:
        super().__init__()
        self.norm_self = nn.LayerNorm(d_model)
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm_cross = nn.LayerNorm(d_model)
        self.cross_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(nn.Linear(d_model, ff_dim), nn.GELU(), nn.Linear(ff_dim, d_model))

    def forward(self, target: Tensor, memory: Tensor,
                target_padding_mask: Tensor | None = None,
                memory_padding_mask: Tensor | None = None) -> Tensor:
        q = self.norm_self(target)
        attended, _ = self.self_attn(
            q, q, q,
            attn_mask=causal_mask(target.shape[1], device=target.device),
            key_padding_mask=target_padding_mask,
            need_weights=False,
        )
        target = target + attended

        # Queries come from the decoder; keys and values are the encoder memory.
        cross_query = self.norm_cross(target)
        cross, _ = self.cross_attn(
            cross_query, memory, memory,
            key_padding_mask=memory_padding_mask,
            need_weights=False,
        )
        target = target + cross
        return target + self.ff(self.norm_ff(target))


class BidirectionalEncoder(nn.Module):
    """Encoder backbone returning one contextual vector per source token."""
    def __init__(self, vocab_size: int, d_model: int = 32, num_heads: int = 4,
                 ff_dim: int = 64, num_layers: int = 1, max_len: int = 128,
                 pad_id: int = 0) -> None:
        super().__init__()
        _check_config(vocab_size, d_model, num_heads, ff_dim, num_layers, max_len, pad_id)
        self.vocab_size, self.pad_id = vocab_size, pad_id
        self.embedding = TokenPositionEmbedding(vocab_size, d_model, max_len, pad_id)
        self.layers = nn.ModuleList(
            BidirectionalEncoderBlock(d_model, num_heads, ff_dim) for _ in range(num_layers)
        )
        self.final_norm = nn.LayerNorm(d_model)

    def forward(self, source_ids: Tensor,
                source_padding_mask: Tensor | None = None) -> Tensor:
        _check_tokens(source_ids, self.vocab_size, "source_ids")
        source_padding_mask = _check_padding_mask(
            source_padding_mask, source_ids, "source_padding_mask"
        )
        if source_ids.shape[1] > self.embedding.max_len:
            raise ValueError("source sequence exceeds max_len")
        if source_padding_mask is None:
            source_padding_mask = make_padding_mask(source_ids, self.pad_id)
        x = self.embedding(source_ids)
        for layer in self.layers:
            x = layer(x, key_padding_mask=source_padding_mask)
        return self.final_norm(x)


class EncoderOnlyClassifier(nn.Module):
    """Bidirectional encoder plus a masked-mean classification head."""
    def __init__(self, vocab_size: int, num_classes: int, d_model: int = 32,
                 num_heads: int = 4, ff_dim: int = 64, num_layers: int = 1,
                 max_len: int = 128, pad_id: int = 0) -> None:
        super().__init__()
        if num_classes < 2:
            raise ValueError("num_classes must be at least 2")
        self.pad_id = pad_id
        self.encoder = BidirectionalEncoder(
            vocab_size, d_model, num_heads, ff_dim, num_layers, max_len, pad_id
        )
        self.classifier = nn.Linear(d_model, num_classes)

    def forward(self, source_ids: Tensor,
                source_padding_mask: Tensor | None = None) -> Tensor:
        if source_padding_mask is None:
            source_padding_mask = make_padding_mask(source_ids, self.pad_id)
        hidden = self.encoder(source_ids, source_padding_mask)
        valid = (~source_padding_mask).unsqueeze(-1).to(hidden.dtype)
        pooled = (hidden * valid).sum(dim=1) / valid.sum(dim=1).clamp_min(1.0)
        return self.classifier(pooled)


class DecoderOnlyLanguageModel(nn.Module):
    """Causal decoder-only model; logits at t predict the next target token."""
    def __init__(self, vocab_size: int, d_model: int = 32, num_heads: int = 4,
                 ff_dim: int = 64, num_layers: int = 1, max_len: int = 128,
                 pad_id: int = 0) -> None:
        super().__init__()
        _check_config(vocab_size, d_model, num_heads, ff_dim, num_layers, max_len, pad_id)
        self.vocab_size, self.pad_id = vocab_size, pad_id
        self.embedding = TokenPositionEmbedding(vocab_size, d_model, max_len, pad_id)
        self.layers = nn.ModuleList(
            CausalDecoderBlock(d_model, num_heads, ff_dim) for _ in range(num_layers)
        )
        self.final_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

    def forward(self, token_ids: Tensor,
                padding_mask: Tensor | None = None) -> Tensor:
        _check_tokens(token_ids, self.vocab_size, "token_ids")
        padding_mask = _check_padding_mask(padding_mask, token_ids, "padding_mask")
        if token_ids.shape[1] > self.embedding.max_len:
            raise ValueError("token sequence exceeds max_len")
        if padding_mask is None:
            padding_mask = make_padding_mask(token_ids, self.pad_id)
        x = self.embedding(token_ids)
        for layer in self.layers:
            x = layer(x, key_padding_mask=padding_mask)
        return self.lm_head(self.final_norm(x))


class EncoderDecoderTransformer(nn.Module):
    """Conditional autoregressive Transformer with separate source and target streams."""
    def __init__(self, vocab_size: int, d_model: int = 32, num_heads: int = 4,
                 ff_dim: int = 64, num_layers: int = 1, max_len: int = 128,
                 pad_id: int = 0) -> None:
        super().__init__()
        _check_config(vocab_size, d_model, num_heads, ff_dim, num_layers, max_len, pad_id)
        self.vocab_size, self.pad_id = vocab_size, pad_id
        self.source_embedding = TokenPositionEmbedding(vocab_size, d_model, max_len, pad_id)
        self.target_embedding = TokenPositionEmbedding(vocab_size, d_model, max_len, pad_id)
        self.encoder_layers = nn.ModuleList(
            BidirectionalEncoderBlock(d_model, num_heads, ff_dim) for _ in range(num_layers)
        )
        self.encoder_norm = nn.LayerNorm(d_model)
        self.decoder_layers = nn.ModuleList(
            EncoderDecoderBlock(d_model, num_heads, ff_dim) for _ in range(num_layers)
        )
        self.decoder_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

    def encode(self, source_ids: Tensor,
               source_padding_mask: Tensor | None = None) -> Tensor:
        _check_tokens(source_ids, self.vocab_size, "source_ids")
        source_padding_mask = _check_padding_mask(
            source_padding_mask, source_ids, "source_padding_mask"
        )
        if source_ids.shape[1] > self.source_embedding.max_len:
            raise ValueError("source sequence exceeds max_len")
        if source_padding_mask is None:
            source_padding_mask = make_padding_mask(source_ids, self.pad_id)
        memory = self.source_embedding(source_ids)
        for layer in self.encoder_layers:
            memory = layer(memory, key_padding_mask=source_padding_mask)
        return self.encoder_norm(memory)

    def decode(self, target_input_ids: Tensor, memory: Tensor,
               target_padding_mask: Tensor | None = None,
               memory_padding_mask: Tensor | None = None) -> Tensor:
        _check_tokens(target_input_ids, self.vocab_size, "target_input_ids")
        if target_input_ids.shape[1] > self.target_embedding.max_len:
            raise ValueError("target sequence exceeds max_len")
        target_padding_mask = _check_padding_mask(
            target_padding_mask, target_input_ids, "target_padding_mask"
        )
        if memory.ndim != 3 or memory.shape[0] != target_input_ids.shape[0]:
            raise ValueError("memory must be [same batch, source length, d_model]")
        if memory.shape[1] < 1 or memory.shape[2] != self.lm_head.in_features:
            raise ValueError("memory has an invalid source length or feature dimension")
        if memory_padding_mask is not None:
            if (memory_padding_mask.dtype != torch.bool
                    or tuple(memory_padding_mask.shape) != tuple(memory.shape[:2])):
                raise ValueError("memory_padding_mask must be boolean [batch, source length]")
        x = self.target_embedding(target_input_ids)
        for layer in self.decoder_layers:
            x = layer(
                x, memory,
                target_padding_mask=target_padding_mask,
                memory_padding_mask=memory_padding_mask,
            )
        return self.lm_head(self.decoder_norm(x))

    def forward(self, source_ids: Tensor, target_input_ids: Tensor,
                source_padding_mask: Tensor | None = None,
                target_padding_mask: Tensor | None = None) -> Tensor:
        if source_padding_mask is None:
            source_padding_mask = make_padding_mask(source_ids, self.pad_id)
        if target_padding_mask is None:
            target_padding_mask = make_padding_mask(target_input_ids, self.pad_id)
        memory = self.encode(source_ids, source_padding_mask)
        return self.decode(
            target_input_ids, memory, target_padding_mask, source_padding_mask
        )


def demo() -> None:
    torch.manual_seed(7)
    source = torch.tensor([[1, 4, 5, 0], [1, 6, 7, 0]], dtype=torch.long)
    target = torch.tensor([[8, 9, 2], [10, 11, 2]], dtype=torch.long)
    decoder_input = shift_right(target, bos_id=1)
    source_padding = make_padding_mask(source, pad_id=0)
    target_padding = make_padding_mask(decoder_input, pad_id=0)

    encoder = EncoderOnlyClassifier(vocab_size=16, num_classes=3)
    decoder = DecoderOnlyLanguageModel(vocab_size=16)
    seq2seq = EncoderDecoderTransformer(vocab_size=16)
    print("encoder-only logits:", tuple(encoder(source, source_padding).shape))
    print("decoder-only next-token logits:", tuple(decoder(source, source_padding).shape))
    print("encoder-decoder logits:", tuple(
        seq2seq(source, decoder_input, source_padding, target_padding).shape
    ))
    print("decoder input:", decoder_input.tolist())
    print("all outputs finite:", all(torch.isfinite(x).all().item() for x in (
        encoder(source, source_padding), decoder(source, source_padding),
        seq2seq(source, decoder_input, source_padding, target_padding),
    )))


if __name__ == "__main__":
    demo()
