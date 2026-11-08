from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from gpu_systems_demo import (
    ContractError,
    classify_backend,
    load_fixture,
    runtime_snapshot,
    validate_dense_layout,
    worker_identity,
)

PROJECT = Path(__file__).resolve().parent


class LayoutContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.layout, self.fixture_hash = load_fixture()

    def test_checked_in_fixture_matches_its_sha256_manifest(self) -> None:
        self.assertEqual(len(self.fixture_hash), 64)
        manifest = json.loads((PROJECT / "fixture_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["sha256"], self.fixture_hash)
        self.assertEqual(manifest["label_source"], "synthetic_fixture")

    def test_dense_layout_dimensions_multiply_to_world_size(self) -> None:
        result = validate_dense_layout(self.layout)
        self.assertEqual(result["dimension_product"], 16)
        self.assertEqual(result["world_size"], 16)
        self.assertEqual(result["dense_parallelism"], {"dp": 2, "tp": 2, "pp": 2, "cp": 2})
        self.assertTrue(result["valid"])

    def test_expert_parallelism_is_explicitly_out_of_scope(self) -> None:
        result = validate_dense_layout(self.layout)
        self.assertFalse(result["scope"]["expert_parallelism_included"])

    def test_unsupported_schema_is_rejected(self) -> None:
        layout = copy.deepcopy(self.layout)
        layout["schema_version"] = "v0"
        with self.assertRaisesRegex(ContractError, "schema_version"):
            validate_dense_layout(layout)

    def test_non_synthetic_label_is_rejected(self) -> None:
        layout = copy.deepcopy(self.layout)
        layout["label_source"] = "measured_hardware"
        with self.assertRaisesRegex(ContractError, "synthetic_fixture"):
            validate_dense_layout(layout)

    def test_real_hardware_claim_is_rejected(self) -> None:
        layout = copy.deepcopy(self.layout)
        layout["metadata"]["real_hardware_observed"] = True
        with self.assertRaisesRegex(ContractError, "metadata"):
            validate_dense_layout(layout)

    def test_training_or_benchmark_claim_is_rejected(self) -> None:
        for key in ("training_run_performed", "benchmark_performed"):
            with self.subTest(key=key):
                layout = copy.deepcopy(self.layout)
                layout["metadata"][key] = True
                with self.assertRaisesRegex(ContractError, "metadata"):
                    validate_dense_layout(layout)

    def test_world_size_must_be_positive_non_boolean_integer(self) -> None:
        for value in (0, -1, 1.5, "16", True):
            with self.subTest(value=value):
                layout = copy.deepcopy(self.layout)
                layout["world_size"] = value
                with self.assertRaisesRegex(ContractError, "world_size"):
                    validate_dense_layout(layout)

    def test_parallel_dimensions_must_be_positive_non_boolean_integers(self) -> None:
        for key in ("dp", "tp", "pp", "cp"):
            for value in (0, -1, 1.5, "2", True):
                with self.subTest(key=key, value=value):
                    layout = copy.deepcopy(self.layout)
                    layout["dense_parallelism"][key] = value
                    with self.assertRaisesRegex(ContractError, key):
                        validate_dense_layout(layout)

    def test_dimension_product_must_equal_world_size(self) -> None:
        layout = copy.deepcopy(self.layout)
        layout["world_size"] = 8
        with self.assertRaisesRegex(ContractError, "does not equal"):
            validate_dense_layout(layout)

    def test_every_dense_dimension_is_required(self) -> None:
        layout = copy.deepcopy(self.layout)
        del layout["dense_parallelism"]["cp"]
        with self.assertRaisesRegex(ContractError, "cp"):
            validate_dense_layout(layout)

    def test_expert_parallelism_claim_cannot_be_enabled(self) -> None:
        layout = copy.deepcopy(self.layout)
        layout["metadata"]["expert_parallelism_modeled"] = True
        with self.assertRaisesRegex(ContractError, "metadata"):
            validate_dense_layout(layout)

    def test_fixture_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            altered_fixture = Path(directory) / "sample.json"
            altered_fixture.write_bytes((PROJECT / "sample_layout.json").read_bytes() + b" ")
            with self.assertRaisesRegex(ContractError, "SHA-256"):
                load_fixture(altered_fixture, PROJECT / "fixture_manifest.json")


class BackendAndRankTests(unittest.TestCase):
    def test_backend_classification_for_rocm(self) -> None:
        self.assertEqual(classify_backend(None, "10.1", True), "rocm-hip")
        self.assertEqual(classify_backend(None, "10.1", False), "rocm-build-no-visible-device")

    def test_backend_classification_for_cuda(self) -> None:
        self.assertEqual(classify_backend("13.0", None, True), "cuda")
        self.assertEqual(classify_backend("13.0", None, False), "cuda-build-no-visible-device")

    def test_backend_classification_for_cpu(self) -> None:
        self.assertEqual(classify_backend(None, None, False), "cpu-or-no-accelerator-build")

    def test_worker_identity_accepts_two_local_ranks(self) -> None:
        identity = worker_identity({"RANK": "1", "LOCAL_RANK": "1", "WORLD_SIZE": "2"})
        self.assertEqual(identity, {"rank": 1, "local_rank": 1, "world_size": 2})

    def test_worker_identity_requires_torchrun_environment(self) -> None:
        with self.assertRaisesRegex(ContractError, "torchrun"):
            worker_identity({})

    def test_worker_identity_rejects_non_integer_environment(self) -> None:
        with self.assertRaisesRegex(ContractError, "must be integers"):
            worker_identity({"RANK": "x", "LOCAL_RANK": "0", "WORLD_SIZE": "2"})

    def test_worker_identity_checks_global_rank_range(self) -> None:
        with self.assertRaisesRegex(ContractError, "RANK"):
            worker_identity({"RANK": "2", "LOCAL_RANK": "0", "WORLD_SIZE": "2"})

    def test_worker_identity_requires_multiple_workers(self) -> None:
        with self.assertRaisesRegex(ContractError, "at least two"):
            worker_identity({"RANK": "0", "LOCAL_RANK": "0", "WORLD_SIZE": "1"})

    def test_worker_identity_rejects_negative_local_rank(self) -> None:
        with self.assertRaisesRegex(ContractError, "LOCAL_RANK"):
            worker_identity({"RANK": "0", "LOCAL_RANK": "-1", "WORLD_SIZE": "2"})

    def test_runtime_snapshot_is_explicit_and_non_benchmarking(self) -> None:
        snapshot = runtime_snapshot()
        for key in (
            "python", "platform", "torch", "torch_cuda_build", "torch_hip_build",
            "torch_cuda_api_available", "accelerator_backend_classification",
            "visible_device_count", "visible_device_names", "distributed_available",
            "gloo_available", "nccl_available",
        ):
            with self.subTest(key=key):
                self.assertIn(key, snapshot)
        self.assertIsInstance(snapshot["torch_cuda_api_available"], bool)
        self.assertIsInstance(snapshot["visible_device_count"], int)
        self.assertIsInstance(snapshot["gloo_available"], bool)
        self.assertIsInstance(snapshot["nccl_available"], bool)
        if not snapshot["torch_cuda_api_available"]:
            self.assertEqual(snapshot["visible_device_count"], 0)
            self.assertEqual(snapshot["visible_device_names"], [])


if __name__ == "__main__":
    unittest.main()
