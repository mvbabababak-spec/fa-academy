"""Contract, provenance, local-tracking, and static-manifest tests for chapter 60."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

import experiment_ops as ops

ROOT = Path(__file__).resolve().parent


class FixtureAndTrainingTests(unittest.TestCase):
    def test_fixture_manifest_matches_exact_fixture_bytes(self) -> None:
        fixture, digest = ops.load_fixture()
        manifest = json.loads((ROOT / "fixture_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(digest, hashlib.sha256((ROOT / "sample_experiment.json").read_bytes()).hexdigest())
        self.assertEqual(manifest["sha256"], digest)
        self.assertEqual(manifest["record_count"], len(fixture["records"]))
        self.assertFalse(fixture["scope"]["real_data_used"])

    def test_fixture_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            fixture_path = temp_path / "sample_experiment.json"
            manifest_path = temp_path / "fixture_manifest.json"
            fixture_path.write_bytes((ROOT / "sample_experiment.json").read_bytes() + b" ")
            manifest_path.write_bytes((ROOT / "fixture_manifest.json").read_bytes())
            with self.assertRaisesRegex(ops.ContractError, "SHA-256"):
                ops.load_fixture(fixture_path, manifest_path)

    def test_real_data_claim_is_rejected(self) -> None:
        fixture, _ = ops.load_fixture()
        fixture["scope"]["real_data_used"] = True
        with self.assertRaisesRegex(ops.ContractError, "no real-data"):
            ops.validate_fixture(fixture)

    def test_duplicate_sample_ids_are_rejected(self) -> None:
        fixture, _ = ops.load_fixture()
        fixture["records"][1]["sample_id"] = fixture["records"][0]["sample_id"]
        with self.assertRaisesRegex(ops.ContractError, "unique"):
            ops.validate_fixture(fixture)

    def test_toy_fit_is_finite_and_decreases_on_synthetic_fixture(self) -> None:
        fixture, _ = ops.load_fixture()
        result = ops.fit_toy_linear(
            fixture["records"],
            steps=fixture["config"]["steps"],
            learning_rate=fixture["config"]["learning_rate"],
        )
        self.assertEqual(len(result["history"]), 6)
        self.assertAlmostEqual(result["initial_mse"], 21.0)
        self.assertLess(result["final_mse"], result["initial_mse"])
        self.assertTrue(all(float(point["mse"]) >= 0 for point in result["history"]))

    def test_unsafe_learning_rate_and_step_count_are_rejected(self) -> None:
        fixture, _ = ops.load_fixture()
        with self.assertRaisesRegex(ops.ContractError, "learning_rate"):
            ops.fit_toy_linear(fixture["records"], steps=5, learning_rate=1.0)
        with self.assertRaisesRegex(ops.ContractError, "steps"):
            ops.fit_toy_linear(fixture["records"], steps=0, learning_rate=0.05)

    def test_canonical_fingerprint_is_order_independent_and_config_sensitive(self) -> None:
        source = {
            "available": True,
            "commit": "a" * 40,
            "worktree_clean": True,
            "status_sha256": "b" * 64,
            "tracked_diff_sha256": "c" * 64,
            "untracked_path_count": 0,
        }
        first = ops.run_fingerprint(
            fixture_sha256="d" * 64,
            config={"steps": 5, "learning_rate": 0.05},
            environment={"python": "3.13.16", "platform": "Linux"},
            source=source,
        )
        reordered = ops.run_fingerprint(
            fixture_sha256="d" * 64,
            config={"learning_rate": 0.05, "steps": 5},
            environment={"platform": "Linux", "python": "3.13.16"},
            source=source,
        )
        changed = ops.run_fingerprint(
            fixture_sha256="d" * 64,
            config={"steps": 6, "learning_rate": 0.05},
            environment={"python": "3.13.16", "platform": "Linux"},
            source=source,
        )
        self.assertEqual(first, reordered)
        self.assertNotEqual(first, changed)

    def test_manifest_run_writes_hash_linked_artifacts_and_scoped_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "run"
            record = ops.run_experiment(backend="manifest", output_dir=output, capture_git=False)
            model = json.loads((output / "model.json").read_text(encoding="utf-8"))
            disk_run = json.loads((output / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(record["artifact"]["sha256"], ops.sha256_file(output / "model.json"))
            self.assertEqual(disk_run["fixture"]["sha256"], record["fixture"]["sha256"])
            self.assertTrue(model["scope"]["synthetic_only"])
            self.assertFalse(model["scope"]["model_quality_claim"])
            self.assertFalse(record["tracking"]["external_sync_requested"])
            self.assertIsNone(record["source"]["worktree_clean"])

    def test_run_fingerprint_changes_when_configuration_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = ops.run_experiment(
                backend="manifest", output_dir=Path(temp) / "first", capture_git=False
            )
            second = ops.run_experiment(
                backend="manifest",
                output_dir=Path(temp) / "second",
                steps=6,
                capture_git=False,
            )
        self.assertNotEqual(first["run_fingerprint_sha256"], second["run_fingerprint_sha256"])


class GitProvenanceTests(unittest.TestCase):
    def _git(self, cwd: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

    def test_clean_and_dirty_worktrees_are_distinguished(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            self._git(repo, "init", "-q")
            self._git(repo, "config", "user.name", "Chapter 60 test")
            self._git(repo, "config", "user.email", "ch60-test@example.invalid")
            code = repo / "code.py"
            code.write_text("value = 1\n", encoding="utf-8")
            self._git(repo, "add", "code.py")
            self._git(repo, "commit", "-m", "initial", "-q")

            clean = ops.capture_git_provenance(repo)
            self.assertTrue(clean["available"])
            self.assertTrue(clean["worktree_clean"])
            self.assertEqual(clean["untracked_path_count"], 0)

            code.write_text("value = 2\n", encoding="utf-8")
            (repo / "untracked.txt").write_text("not committed\n", encoding="utf-8")
            dirty = ops.capture_git_provenance(repo)
            self.assertFalse(dirty["worktree_clean"])
            self.assertEqual(dirty["commit"], clean["commit"])
            self.assertEqual(dirty["untracked_path_count"], 1)
            self.assertNotEqual(dirty["status_sha256"], clean["status_sha256"])

    def test_container_environment_can_supply_commit_without_copying_dot_git(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.dict(
                os.environ,
                {
                    "SOURCE_COMMIT": "a" * 40,
                    "SOURCE_WORKTREE_CLEAN": "true",
                    "SOURCE_STATUS_SHA256": "b" * 64,
                    "SOURCE_TRACKED_DIFF_SHA256": "c" * 64,
                    "SOURCE_UNTRACKED_PATH_COUNT": "0",
                },
                clear=False,
            ):
                source = ops.capture_git_provenance(Path(temp))
        self.assertFalse(source["available"])
        self.assertEqual(source["capture_method"], "environment")
        self.assertEqual(source["commit"], "a" * 40)
        self.assertTrue(source["worktree_clean"])
        self.assertEqual(source["untracked_path_count"], 0)


class TrackingIntegrationTests(unittest.TestCase):
    def test_mlflow_logs_params_metrics_and_artifacts_to_local_sqlite(self) -> None:
        import mlflow
        from mlflow import MlflowClient

        self.assertEqual(mlflow.__version__, "3.18.0")
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "mlflow-run"
            record = ops.run_experiment(backend="mlflow", output_dir=output, capture_git=False)
            run_id = record["tracking"]["run_id"]
            client = MlflowClient()
            stored = client.get_run(run_id)
            self.assertEqual(stored.data.params["fixture_sha256"], record["fixture"]["sha256"])
            self.assertEqual(stored.data.params["steps"], "5")
            self.assertAlmostEqual(stored.data.metrics["toy/mse"], record["metrics"]["final_mse"])
            artifacts = {item.path for item in client.list_artifacts(run_id)}
            self.assertEqual(artifacts, {"outputs", "provenance"})
            model_file = Path(client.download_artifacts(run_id, "outputs/model.json"))
            model = json.loads(model_file.read_text(encoding="utf-8"))
            self.assertEqual(model["fixture_sha256"], record["fixture"]["sha256"])
            self.assertFalse(record["tracking"]["external_sync_requested"])

    def test_wandb_backend_forces_offline_and_uses_no_api_key(self) -> None:
        import wandb

        self.assertEqual(wandb.__version__, "0.31.0")
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "wandb-run"
            with mock.patch.dict(
                os.environ,
                {"WANDB_MODE": "online", "WANDB_API_KEY": "test-only-not-a-secret"},
                clear=False,
            ):
                record = ops.run_experiment(
                    backend="wandb-offline", output_dir=output, capture_git=False
                )
                self.assertEqual(os.environ["WANDB_MODE"], "online")
                self.assertEqual(os.environ["WANDB_API_KEY"], "test-only-not-a-secret")

            tracking = record["tracking"]
            offline_dir = output / tracking["offline_run_directory"]
            self.assertEqual(tracking["mode"], "offline")
            self.assertEqual(tracking["status"], "saved-locally-not-synced")
            self.assertTrue(offline_dir.is_dir())
            self.assertTrue(list(offline_dir.glob("*.wandb")))
            self.assertFalse(tracking["external_sync_requested"])
            self.assertFalse(tracking["automatic_code_capture"])
            self.assertFalse(tracking["system_metrics_capture"])


class DeploymentExampleTests(unittest.TestCase):
    def test_dockerfile_pins_base_digest_and_runs_non_root(self) -> None:
        text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        digests = re.findall(r"python:3\.13\.16-slim@sha256:([0-9a-f]{64})", text)
        self.assertEqual(len(digests), 2)
        self.assertEqual(digests[0], digests[1])
        self.assertIn("USER 10001:10001", text)
        self.assertIn("COPY --from=builder", text)
        self.assertNotRegex(text, r"(?i)\b(?:ARG|ENV)\s+\w*(?:TOKEN|SECRET|API_KEY)")

    def test_kubernetes_job_is_ephemeral_hardened_and_resource_bounded(self) -> None:
        job = yaml.safe_load((ROOT / "job.yaml").read_text(encoding="utf-8"))
        self.assertEqual(job["apiVersion"], "batch/v1")
        self.assertEqual(job["kind"], "Job")
        self.assertEqual(job["spec"]["backoffLimit"], 1)
        self.assertGreater(job["spec"]["activeDeadlineSeconds"], 0)
        pod = job["spec"]["template"]["spec"]
        container = pod["containers"][0]
        self.assertEqual(pod["restartPolicy"], "Never")
        self.assertTrue(pod["securityContext"]["runAsNonRoot"])
        self.assertTrue(container["securityContext"]["readOnlyRootFilesystem"])
        self.assertEqual(container["resources"]["requests"]["cpu"], "1")
        self.assertEqual(container["resources"]["limits"]["memory"], "2Gi")
        self.assertIn("emptyDir", pod["volumes"][0])
        self.assertRegex(container["image"], r"@sha256:[0-9a-f]{64}$")
        self.assertIn(".invalid", container["image"])
        self.assertEqual(job["spec"]["ttlSecondsAfterFinished"], 3600)

    def test_direct_and_locked_requirements_match_documented_versions(self) -> None:
        direct = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        lock = (ROOT / "requirements-lock-linux-py313.txt").read_text(encoding="utf-8")
        for line in ("mlflow==3.18.0", "wandb==0.31.0", "PyYAML==6.0.3"):
            self.assertIn(line, direct)
            self.assertIn(line, lock)


if __name__ == "__main__":
    unittest.main(verbosity=2)
