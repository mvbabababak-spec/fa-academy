#!/usr/bin/env python3
"""Offline-safe GPU-stack preflight and a CPU/Gloo torchrun smoke test.

The project deliberately does not install vendor drivers or run GPU kernels.
It validates a synthetic dense-parallel layout, reports the active PyTorch
build, and tests process/rank/collective wiring on CPU with Gloo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any, Mapping

import torch
import torch.distributed as dist

PROJECT_DIR = Path(__file__).resolve().parent
FIXTURE_PATH = PROJECT_DIR / "sample_layout.json"
MANIFEST_PATH = PROJECT_DIR / "fixture_manifest.json"


class ContractError(ValueError):
    """Raised when a fixture or worker environment violates its contract."""


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ContractError(f"{name} must be a positive integer")
    return value


def validate_dense_layout(layout: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a simplified dense TP×PP×CP×DP layout; EP is out of scope."""
    if layout.get("schema_version") != "v4-ch13-layout-v1":
        raise ContractError("unsupported layout schema_version")
    if layout.get("label_source") != "synthetic_fixture":
        raise ContractError("layout must be labeled synthetic_fixture")
    metadata = layout.get("metadata")
    required_false = (
        "real_hardware_observed",
        "training_run_performed",
        "benchmark_performed",
        "expert_parallelism_modeled",
    )
    if not isinstance(metadata, dict) or any(metadata.get(key) is not False for key in required_false):
        raise ContractError("fixture metadata must explicitly exclude hardware, training, benchmark, and EP claims")

    world_size = _positive_int(layout.get("world_size"), "world_size")
    dense = layout.get("dense_parallelism")
    if not isinstance(dense, dict):
        raise ContractError("dense_parallelism must be an object")
    dimensions = {name: _positive_int(dense.get(name), name) for name in ("dp", "tp", "pp", "cp")}
    product = dimensions["dp"] * dimensions["tp"] * dimensions["pp"] * dimensions["cp"]
    if product != world_size:
        raise ContractError(
            f"dense parallelism product {product} does not equal world_size {world_size}"
        )
    return {
        "fixture_id": layout.get("fixture_id"),
        "label_source": "synthetic_fixture",
        "world_size": world_size,
        "dense_parallelism": dimensions,
        "dimension_product": product,
        "valid": True,
        "scope": {
            "expert_parallelism_included": False,
            "real_hardware_observed": False,
            "training_run_performed": False,
            "benchmark_performed": False,
        },
    }


def load_fixture(path: Path = FIXTURE_PATH, manifest_path: Path = MANIFEST_PATH) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("fixture_id") != "v4-ch13-synthetic-dense-layout-v1":
        raise ContractError("fixture manifest id mismatch")
    if manifest.get("sha256") != digest:
        raise ContractError("fixture SHA-256 does not match the manifest")
    if manifest.get("label_source") != "synthetic_fixture":
        raise ContractError("fixture manifest must identify synthetic data")
    layout = json.loads(raw.decode("utf-8"))
    validated = validate_dense_layout(layout)
    if validated["fixture_id"] != manifest["fixture_id"]:
        raise ContractError("fixture and manifest ids differ")
    return layout, digest


def classify_backend(cuda_build: str | None, hip_build: str | None, available: bool) -> str:
    """Distinguish builds using metadata; torch.cuda is also PyTorch's HIP API."""
    if hip_build:
        return "rocm-hip" if available else "rocm-build-no-visible-device"
    if cuda_build:
        return "cuda" if available else "cuda-build-no-visible-device"
    return "cpu-or-no-accelerator-build"


def runtime_snapshot() -> dict[str, Any]:
    available = bool(torch.cuda.is_available())
    backend = classify_backend(torch.version.cuda, torch.version.hip, available)
    count = int(torch.cuda.device_count()) if available else 0
    devices = [torch.cuda.get_device_name(index) for index in range(count)] if available else []
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": str(torch.__version__),
        "torch_cuda_build": torch.version.cuda,
        "torch_hip_build": torch.version.hip,
        "torch_cuda_api_available": available,
        "accelerator_backend_classification": backend,
        "visible_device_count": count,
        "visible_device_names": devices,
        "distributed_available": bool(dist.is_available()),
        "gloo_available": bool(dist.is_available() and dist.is_gloo_available()),
        "nccl_available": bool(dist.is_available() and dist.is_nccl_available()),
    }


def worker_identity(env: Mapping[str, str] | None = None) -> dict[str, int]:
    values = os.environ if env is None else env
    required = ("RANK", "LOCAL_RANK", "WORLD_SIZE")
    missing = [key for key in required if key not in values]
    if missing:
        raise ContractError(f"launch with torchrun; missing environment variables: {', '.join(missing)}")
    try:
        rank, local_rank, world_size = (int(values[key]) for key in required)
    except (TypeError, ValueError) as exc:
        raise ContractError("RANK, LOCAL_RANK, and WORLD_SIZE must be integers") from exc
    if world_size < 2:
        raise ContractError("the Gloo smoke test requires at least two workers")
    if rank < 0 or rank >= world_size:
        raise ContractError("RANK must be in [0, WORLD_SIZE)")
    if local_rank < 0:
        raise ContractError("LOCAL_RANK must be non-negative")
    return {"rank": rank, "local_rank": local_rank, "world_size": world_size}


def _scope_limits() -> dict[str, bool]:
    return {
        "cuda_runtime_tested": False,
        "rocm_runtime_tested": False,
        "triton_kernel_executed": False,
        "deepspeed_training_executed": False,
        "fsdp_training_executed": False,
        "megatron_training_executed": False,
        "gpu_benchmark_performed": False,
        "model_quality_claim": False,
    }


def run_gloo_smoke(output_path: Path) -> dict[str, Any]:
    identity = worker_identity()
    if not dist.is_available() or not dist.is_gloo_available():
        raise RuntimeError("this CPU smoke test requires PyTorch distributed with Gloo support")
    fixture, fixture_hash = load_fixture()
    dist.init_process_group(backend="gloo", timeout=timedelta(seconds=60))
    try:
        if dist.get_rank() != identity["rank"] or dist.get_world_size() != identity["world_size"]:
            raise RuntimeError("torchrun environment and initialized process group disagree")
        rank = dist.get_rank()
        world_size = dist.get_world_size()
        value = torch.tensor([rank + 1], dtype=torch.int64, device="cpu")
        dist.all_reduce(value, op=dist.ReduceOp.SUM)
        observed = int(value.item())
        expected = world_size * (world_size + 1) // 2
        if observed != expected:
            raise RuntimeError(f"all_reduce returned {observed}; expected {expected}")
        result = {
            "schema_version": "v4-ch13-gloo-smoke-v1",
            "fixture_id": fixture["fixture_id"],
            "fixture_sha256": fixture_hash,
            "validated_synthetic_layout": validate_dense_layout(fixture),
            "environment": runtime_snapshot(),
            "process_group": {
                "backend": "gloo",
                "rank": rank,
                "local_rank": identity["local_rank"],
                "world_size": world_size,
                "rank_inputs": list(range(1, world_size + 1)),
            },
            "collective": {
                "operation": "all_reduce_sum",
                "observed": observed,
                "expected": expected,
                "passed": observed == expected,
            },
            "scope": _scope_limits(),
        }
        if rank == 0:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = output_path.with_name(output_path.name + f".{os.getpid()}.tmp")
            temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(output_path)
        dist.barrier()
        return result
    finally:
        if dist.is_initialized():
            dist.destroy_process_group()


def _json_stdout(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "layout", "gloo-smoke"), default="preflight")
    parser.add_argument("--fixture", type=Path, default=FIXTURE_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=Path("/tmp/ch59-gloo-smoke.json"))
    parser.add_argument("--local-rank", "--local_rank", type=int, default=None,
                        help="accepted for compatibility; torchrun environment variables are authoritative")
    args = parser.parse_args(argv)
    try:
        if args.mode == "preflight":
            _json_stdout(runtime_snapshot())
        elif args.mode == "layout":
            fixture, digest = load_fixture(args.fixture, args.manifest)
            _json_stdout({"fixture_sha256": digest, "layout": validate_dense_layout(fixture)})
        else:
            _json_stdout(run_gloo_smoke(args.output))
    except (ContractError, OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
