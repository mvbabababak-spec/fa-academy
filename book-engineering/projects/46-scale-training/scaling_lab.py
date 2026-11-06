"""CPU probes for activation rematerialization, DDP gradient reduction, and run identity.

This is a deterministic correctness fixture, not a speed or model-quality benchmark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.checkpoint import checkpoint


SEED = 46
WORLD_SIZE = 2
INPUT_DIM = 8
HIDDEN_DIM = 16
OUTPUT_DIM = 4
BLOCKS = 2
_TIMEOUT = timedelta(seconds=45)


class ResidualBlock(nn.Module):
    """Small block whose intermediate tensors participate in backward."""

    def __init__(self) -> None:
        super().__init__()
        self.up = nn.Linear(INPUT_DIM, HIDDEN_DIM)
        self.down = nn.Linear(HIDDEN_DIM, INPUT_DIM)
        self.activation = nn.GELU()

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        return value + self.down(self.activation(self.up(value))) * 0.5


class ProbeNetwork(nn.Module):
    """A tiny network to compare ordinary and checkpointed autograd graphs."""

    def __init__(self) -> None:
        super().__init__()
        self.blocks = nn.ModuleList(ResidualBlock() for _ in range(BLOCKS))
        self.head = nn.Linear(INPUT_DIM, OUTPUT_DIM)

    def forward(self, value: torch.Tensor, *, rematerialize: bool = False) -> torch.Tensor:
        for block in self.blocks:
            if rematerialize:
                value = checkpoint(block, value, use_reentrant=False)
            else:
                value = block(value)
        return self.head(value)


def _max_abs(left: torch.Tensor, right: torch.Tensor) -> float:
    return float((left - right).abs().max().item())


def activation_checkpoint_probe(seed: int = SEED) -> dict[str, Any]:
    """Compare output/gradients and count tensors saved for backward hooks."""
    if seed < 0:
        raise ValueError("seed must be non-negative")
    torch.manual_seed(seed)
    reference = ProbeNetwork()
    rematerialized = ProbeNetwork()
    rematerialized.load_state_dict(reference.state_dict())
    inputs = torch.linspace(-1.0, 1.0, 5 * INPUT_DIM, dtype=torch.float32).reshape(5, INPUT_DIM)

    def run(model: ProbeNetwork, use_rematerialization: bool) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
        model.zero_grad(set_to_none=True)
        value = inputs.clone().requires_grad_(True)
        saved_bytes = 0

        def pack(tensor: torch.Tensor) -> torch.Tensor:
            nonlocal saved_bytes
            saved_bytes += tensor.numel() * tensor.element_size()
            return tensor

        with torch.autograd.graph.saved_tensors_hooks(pack, lambda tensor: tensor):
            output = model(value, rematerialize=use_rematerialization)
            output.square().mean().backward()
        parameter_gradients = torch.cat([
            parameter.grad.detach().reshape(-1)
            for parameter in model.parameters()
            if parameter.grad is not None
        ])
        return output.detach(), value.grad.detach(), parameter_gradients, saved_bytes

    base_out, base_input_grad, base_parameter_grad, base_saved = run(reference, False)
    check_out, check_input_grad, check_parameter_grad, check_saved = run(rematerialized, True)
    return {
        "seed": seed,
        "blocks": BLOCKS,
        "use_reentrant": False,
        "saved_tensor_bytes_baseline": base_saved,
        "saved_tensor_bytes_rematerialized": check_saved,
        "saved_tensor_ratio": check_saved / base_saved if base_saved else None,
        "max_abs_output_delta": _max_abs(base_out, check_out),
        "max_abs_input_gradient_delta": _max_abs(base_input_grad, check_input_grad),
        "max_abs_parameter_gradient_delta": _max_abs(base_parameter_grad, check_parameter_grad),
        "measurement_note": "autograd saved-tensor bytes only; not peak process/device memory or runtime",
    }


def _synthetic_data() -> tuple[torch.Tensor, torch.Tensor, tuple[tuple[int, ...], ...]]:
    features = torch.arange(1.0, 6.0, dtype=torch.float32).reshape(-1, 1)
    targets = 2.0 * features
    # Deliberately uneven shards exercise sample-count weighting: 3 + 2 = 5.
    shards = ((0, 1, 2), (3, 4))
    return features, targets, shards


def _ddp_worker(rank: int, world_size: int, rendezvous_file: str, result_file: str) -> None:
    """One Gloo CPU rank; called by multiprocessing spawn."""
    torch.set_num_threads(1)
    dist.init_process_group(
        backend="gloo",
        init_method=f"file://{rendezvous_file}",
        rank=rank,
        world_size=world_size,
        timeout=_TIMEOUT,
    )
    try:
        model = nn.Linear(1, 1, bias=False)
        with torch.no_grad():
            model.weight.fill_(0.5)
        distributed_model = DDP(model)

        features, targets, shards = _synthetic_data()
        indices = list(shards[rank])
        local_features = features[indices]
        local_targets = targets[indices]
        local_loss_sum = F.mse_loss(distributed_model(local_features), local_targets, reduction="sum")
        # DDP averages rank gradients. Scale local sums so the result is the
        # sample-weighted mean gradient, even though shard lengths differ.
        (local_loss_sum * world_size / len(features)).backward()

        if rank == 0:
            single_model = nn.Linear(1, 1, bias=False)
            with torch.no_grad():
                single_model.weight.fill_(0.5)
            global_loss = F.mse_loss(single_model(features), targets, reduction="mean")
            global_loss.backward()
            payload = {
                "backend": "gloo",
                "device": "cpu",
                "world_size": world_size,
                "global_sample_count": len(features),
                "local_sample_counts": [len(shard) for shard in shards],
                "ddp_gradient": float(distributed_model.module.weight.grad.item()),
                "single_process_reference_gradient": float(single_model.weight.grad.item()),
            }
            Path(result_file).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        dist.barrier()
    finally:
        if dist.is_initialized():
            dist.destroy_process_group()


def distributed_gradient_probe() -> dict[str, Any]:
    """Run a real two-process CPU DDP all-reduce with the Gloo backend."""
    if dist.is_initialized():
        raise RuntimeError("the probe must run before another process group is initialized")
    if not dist.is_available() or not dist.is_gloo_available():
        raise RuntimeError("this PyTorch build does not include the Gloo backend")
    with tempfile.TemporaryDirectory(prefix="ch46-ddp-") as temporary:
        rendezvous_file = str(Path(temporary) / "rendezvous")
        result_file = str(Path(temporary) / "result.json")
        mp.spawn(
            _ddp_worker,
            args=(WORLD_SIZE, rendezvous_file, result_file),
            nprocs=WORLD_SIZE,
            join=True,
        )
        payload = json.loads(Path(result_file).read_text(encoding="utf-8"))
    payload["max_abs_gradient_delta"] = abs(
        payload["ddp_gradient"] - payload["single_process_reference_gradient"]
    )
    payload["measurement_note"] = "one synthetic gradient step; no GPU, network cluster, speed, or quality benchmark"
    return payload


def _data_sha256() -> str:
    features, targets, shards = _synthetic_data()
    content = {
        "features": features.reshape(-1).tolist(),
        "targets": targets.reshape(-1).tolist(),
        "shards": [list(shard) for shard in shards],
    }
    return hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_fingerprint(config: dict[str, Any], code_sha256: str, data_sha256: str, runtime: dict[str, str]) -> str:
    """Content identity for this fixture; it is not a security signature."""
    payload = {
        "config": config,
        "code_sha256": code_sha256,
        "data_sha256": data_sha256,
        "runtime": runtime,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_report(seed: int = SEED) -> dict[str, Any]:
    if seed < 0:
        raise ValueError("seed must be non-negative")
    config = {
        "seed": seed,
        "network": {"input_dim": INPUT_DIM, "hidden_dim": HIDDEN_DIM, "output_dim": OUTPUT_DIM, "blocks": BLOCKS},
        "activation_checkpoint": {"enabled_for_probe": True, "use_reentrant": False},
        "distributed": {"backend": "gloo", "world_size": WORLD_SIZE, "device": "cpu"},
    }
    runtime = {
        "python_version": platform.python_version(),
        "torch_version": str(torch.__version__),
        "device": "cpu",
        "distributed_backend": "gloo",
    }
    code_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    data_sha256 = _data_sha256()
    return {
        "schema_version": 1,
        "config_fingerprint": run_fingerprint(config, code_sha256, data_sha256, runtime),
        "code_sha256": code_sha256,
        "data_sha256": data_sha256,
        "config": config,
        "runtime": runtime,
        "activation_checkpoint_probe": activation_checkpoint_probe(seed),
        "distributed_probe": distributed_gradient_probe(),
        "scope_note": "correctness and provenance fixture only; not training, a benchmark, or a production recovery system",
    }


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            temporary_name = handle.name
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary_name, path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--output", type=Path, help="optional JSON report path; no file is written by default")
    args = parser.parse_args(argv)
    report = build_report(args.seed)
    if args.output is not None:
        _atomic_write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
