"""A deterministic CPU lab for floating-point formats, AMP and affine quantization.

The program measures storage dtypes and tensor-level quantization error. It does
not benchmark accelerators or claim that a dtype has a fast hardware kernel.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import torch
from torch import nn


FORMAT_SPECS = (
    ("FP32", "float32", 32, "1/8/23"),
    ("FP16", "float16", 16, "1/5/10"),
    ("BF16", "bfloat16", 16, "1/8/7"),
    ("FP8 E4M3FN", "float8_e4m3fn", 8, "1/4/3"),
    ("FP8 E5M2", "float8_e5m2", 8, "1/5/2"),
)


def _json_scalar(value: float) -> float | str:
    """Return a JSON-safe scalar while preserving NaN and infinity labels."""
    number = float(value)
    if math.isnan(number):
        return "nan"
    if math.isinf(number):
        return "inf" if number > 0 else "-inf"
    return number


def format_table() -> list[dict[str, Any]]:
    """Inspect the available PyTorch dtypes instead of assuming their limits."""
    rows: list[dict[str, Any]] = []
    for name, attr, bits, fields in FORMAT_SPECS:
        dtype = getattr(torch, attr, None)
        if dtype is None:
            rows.append({"name": name, "dtype": f"torch.{attr}", "available": False})
            continue
        info = torch.finfo(dtype)
        bytes_per_element = torch.empty((), dtype=dtype).element_size()
        bytes_for_million = bytes_per_element * 1_000_000
        rows.append({
            "name": name,
            "dtype": str(dtype),
            "available": True,
            "bits": bits,
            "sign_exponent_fraction_bits": fields,
            "bytes_per_element": bytes_per_element,
            "max_finite": float(info.max),
            "smallest_normal": float(info.tiny),
            "epsilon_at_one": float(info.eps),
            "million_values_decimal_MB": bytes_for_million / 1_000_000,
            "million_values_MiB": bytes_for_million / (1024 * 1024),
        })
    return rows


def precision_probe(values: list[float] | None = None) -> dict[str, Any]:
    """Cast a fixed FP32 vector down and back, counting under/overflow outcomes."""
    if values is None:
        values = [1e-8, 0.1, 1.001, 1e5, -1e5]
    source = torch.tensor(values, dtype=torch.float32)
    rows: list[dict[str, Any]] = []
    for name, attr, _bits, _fields in FORMAT_SPECS:
        dtype = getattr(torch, attr, None)
        if dtype is None:
            rows.append({"name": name, "available": False})
            continue
        rounded = source.to(dtype).to(torch.float32)
        finite = torch.isfinite(rounded)
        error = (rounded[finite] - source[finite]).abs()
        rows.append({
            "name": name,
            "available": True,
            "roundtrip_values": [_json_scalar(x) for x in rounded.tolist()],
            "nonzero_to_zero_count": int(((source != 0) & (rounded == 0)).sum().item()),
            "infinity_count": int(torch.isinf(rounded).sum().item()),
            "nan_count": int(torch.isnan(rounded).sum().item()),
            "max_abs_error_on_finite_values": float(error.max().item()) if error.numel() else None,
        })
    return {"source_fp32": values, "casts": rows}


def cpu_autocast_probe() -> dict[str, Any]:
    """Compare FP32 Linear with CPU BF16 autocast; this is not a speed benchmark."""
    torch.manual_seed(451)
    model = nn.Linear(8, 4, bias=True).eval()
    inputs = torch.linspace(-1.25, 1.25, 64, dtype=torch.float32).reshape(8, 8)
    with torch.inference_mode():
        reference = model(inputs)
        with torch.amp.autocast(device_type="cpu", dtype=torch.bfloat16):
            mixed = model(inputs)
    difference = (mixed.float() - reference).abs()
    return {
        "device": "cpu",
        "autocast_dtype": "torch.bfloat16",
        "parameter_dtype_after_autocast": str(next(model.parameters()).dtype),
        "input_dtype": str(inputs.dtype),
        "output_dtype": str(mixed.dtype),
        "finite_output": bool(torch.isfinite(mixed).all().item()),
        "max_abs_difference_from_fp32": float(difference.max().item()),
        "benchmark_performed": False,
    }


def _as_cpu_float(values: Any) -> torch.Tensor:
    tensor = torch.as_tensor(values, dtype=torch.float32, device="cpu")
    if tensor.numel() == 0:
        raise ValueError("values must not be empty")
    if not bool(torch.isfinite(tensor).all().item()):
        raise ValueError("values must all be finite")
    return tensor


def _chunks(flat: torch.Tensor, granularity: str, group_size: int | None) -> list[torch.Tensor]:
    if granularity == "tensor":
        if group_size is not None:
            raise ValueError("group_size is only valid for granularity='group'")
        return [flat]
    if granularity != "group":
        raise ValueError("granularity must be 'tensor' or 'group'")
    if not isinstance(group_size, int) or isinstance(group_size, bool) or group_size <= 0:
        raise ValueError("group granularity requires a positive integer group_size")
    return [flat[start : start + group_size] for start in range(0, flat.numel(), group_size)]


def calculate_qparams(
    calibration_values: Any,
    *,
    bits: int = 8,
    symmetric: bool = True,
    granularity: str = "tensor",
    group_size: int | None = None,
) -> dict[str, Any]:
    """Derive signed integer quantization parameters from calibration values.

    For a symmetric signed range the negative endpoint is restricted to -qmax
    (for int8: -127..127), making zero exactly representable. Group mode flattens
    the input and gives each consecutive group its own scale/zero point.
    """
    if not isinstance(bits, int) or isinstance(bits, bool) or not 2 <= bits <= 8:
        raise ValueError("bits must be an integer from 2 through 8")
    if not isinstance(symmetric, bool):
        raise ValueError("symmetric must be a bool")
    values = _as_cpu_float(calibration_values)
    flat = values.reshape(-1)
    qmax = 2 ** (bits - 1) - 1
    qmin = -qmax if symmetric else -(2 ** (bits - 1))
    pieces = _chunks(flat, granularity, group_size)
    scales: list[float] = []
    zero_points: list[int] = []

    for piece in pieces:
        low = float(piece.min().item())
        high = float(piece.max().item())
        if symmetric:
            scale = max(abs(low), abs(high)) / qmax
            zero_point = 0
        elif high == low:
            # A constant range needs a non-zero step. This choice preserves a
            # non-zero constant when possible and maps an all-zero group to 0.
            magnitude = abs(low)
            scale = magnitude / qmax if magnitude else 1.0
            zero_point = 0
        else:
            scale = (high - low) / (qmax - qmin)
            zero_point = int(torch.round(torch.tensor(qmin - low / scale)).item())
            zero_point = max(qmin, min(qmax, zero_point))
        if not math.isfinite(scale) or scale <= 0:
            scale = 1.0
        scales.append(float(scale))
        zero_points.append(int(zero_point))

    return {
        "bits": bits,
        "symmetric": symmetric,
        "granularity": granularity,
        "group_size": group_size,
        "qmin": qmin,
        "qmax": qmax,
        "scales": scales,
        "zero_points": zero_points,
        "calibration_numel": flat.numel(),
    }


def quantize_with_qparams(values: Any, qparams: dict[str, Any]) -> dict[str, Any]:
    """Round, clamp and dequantize with precomputed qparams; report saturation."""
    tensor = _as_cpu_float(values)
    flat = tensor.reshape(-1)
    granularity = qparams.get("granularity")
    group_size = qparams.get("group_size")
    pieces = _chunks(flat, granularity, group_size)
    scales = qparams.get("scales")
    zero_points = qparams.get("zero_points")
    if not isinstance(scales, list) or not isinstance(zero_points, list):
        raise ValueError("qparams must contain scale and zero_point lists")
    if len(pieces) != len(scales) or len(pieces) != len(zero_points):
        raise ValueError("qparams count does not match the tensor groups")
    if granularity == "group" and flat.numel() != qparams.get("calibration_numel"):
        raise ValueError("group qparams require the same flattened length as calibration")
    qmin = int(qparams["qmin"])
    qmax = int(qparams["qmax"])

    code_pieces: list[torch.Tensor] = []
    dequant_pieces: list[torch.Tensor] = []
    saturation_count = 0
    for piece, scale, zero_point in zip(pieces, scales, zero_points):
        scale = float(scale)
        zero_point = int(zero_point)
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("all scales must be positive and finite")
        rounded = torch.round(piece / scale + zero_point)
        saturation_count += int(((rounded < qmin) | (rounded > qmax)).sum().item())
        codes = rounded.clamp(qmin, qmax).to(torch.int8)
        reconstructed = (codes.to(torch.float32) - zero_point) * scale
        code_pieces.append(codes)
        dequant_pieces.append(reconstructed)

    codes_flat = torch.cat(code_pieces)
    dequant_flat = torch.cat(dequant_pieces)
    dequantized = dequant_flat.reshape(tensor.shape)
    error = (dequantized - tensor).abs()
    return {
        "codes": codes_flat.reshape(tensor.shape),
        "dequantized": dequantized,
        "scales": [float(x) for x in scales],
        "zero_points": [int(x) for x in zero_points],
        "qmin": qmin,
        "qmax": qmax,
        "saturation_count": saturation_count,
        "saturation_fraction": saturation_count / flat.numel(),
        "mae": float(error.mean().item()),
        "rmse": float(torch.sqrt(torch.mean((dequantized - tensor) ** 2)).item()),
        "max_abs_error": float(error.max().item()),
    }


def _result_for_json(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (value.tolist() if isinstance(value, torch.Tensor) else value)
        for key, value in result.items()
    }


def quantization_demo() -> dict[str, Any]:
    """Compare per-tensor/group int8 and a calibration-distribution shift."""
    values = torch.tensor([0.04, -0.05, 0.03, 10.0, 0.10, 0.12, -0.08, 0.11])
    per_tensor_qparams = calculate_qparams(values, symmetric=True, granularity="tensor")
    per_group_qparams = calculate_qparams(
        values, symmetric=True, granularity="group", group_size=4
    )
    per_tensor = quantize_with_qparams(values, per_tensor_qparams)
    per_group = quantize_with_qparams(values, per_group_qparams)

    calibration = torch.tensor([-1.0, -0.5, 0.0, 0.5, 1.0])
    evaluation = torch.tensor([-1.5, -0.2, 1.4])
    calibrated_qparams = calculate_qparams(calibration, symmetric=True, granularity="tensor")
    shifted = quantize_with_qparams(evaluation, calibrated_qparams)
    return {
        "int8_per_tensor": {
            "source": values.tolist(),
            "qparams": per_tensor_qparams,
            "result": _result_for_json(per_tensor),
        },
        "int8_per_group": {
            "source": values.tolist(),
            "qparams": per_group_qparams,
            "result": _result_for_json(per_group),
        },
        "calibration_shift": {
            "calibration_values": calibration.tolist(),
            "evaluation_values": evaluation.tolist(),
            "qparams": calibrated_qparams,
            "result": _result_for_json(shifted),
        },
        "storage_note": (
            "The code tensor uses torch.int8 for clarity. This demonstration does not pack sub-8-bit codes or include scale metadata in a model-size estimate."
        ),
    }


def run_lab() -> dict[str, Any]:
    """Return the complete deterministic report used by the CLI and tests."""
    return {
        "runtime": {
            "torch_version": torch.__version__,
            "device": "cpu",
            "purpose": "numeric behavior demonstration; not a performance benchmark",
        },
        "formats": format_table(),
        "cast_probe": precision_probe(),
        "cpu_bf16_autocast": cpu_autocast_probe(),
        "quantization": quantization_demo(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional path for the JSON report")
    args = parser.parse_args()
    report = json.dumps(run_lab(), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
