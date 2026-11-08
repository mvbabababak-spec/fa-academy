import math
import tempfile
import unittest
from pathlib import Path

from scaling_lab import (
    _atomic_write_json,
    _data_sha256,
    build_report,
    run_fingerprint,
)


class ScalingLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run the two-process Gloo probe once for the whole suite.
        cls.report = build_report(seed=46)

    def test_activation_checkpoint_preserves_outputs_and_gradients(self):
        probe = self.report["activation_checkpoint_probe"]
        self.assertEqual(probe["max_abs_output_delta"], 0.0)
        self.assertEqual(probe["max_abs_input_gradient_delta"], 0.0)
        self.assertEqual(probe["max_abs_parameter_gradient_delta"], 0.0)

    def test_activation_checkpoint_saves_fewer_autograd_bytes(self):
        probe = self.report["activation_checkpoint_probe"]
        self.assertGreater(probe["saved_tensor_bytes_baseline"], 0)
        self.assertLess(
            probe["saved_tensor_bytes_rematerialized"],
            probe["saved_tensor_bytes_baseline"],
        )
        self.assertLess(probe["saved_tensor_ratio"], 1.0)

    def test_checkpoint_mode_is_explicitly_non_reentrant(self):
        self.assertFalse(self.report["activation_checkpoint_probe"]["use_reentrant"])
        self.assertFalse(self.report["config"]["activation_checkpoint"]["use_reentrant"])

    def test_ddp_gradient_matches_single_process_global_mean(self):
        probe = self.report["distributed_probe"]
        self.assertEqual(probe["backend"], "gloo")
        self.assertEqual(probe["world_size"], 2)
        self.assertEqual(probe["max_abs_gradient_delta"], 0.0)
        self.assertTrue(math.isfinite(probe["ddp_gradient"]))

    def test_uneven_shards_are_weighted_by_sample_count(self):
        probe = self.report["distributed_probe"]
        self.assertEqual(probe["local_sample_counts"], [3, 2])
        self.assertEqual(sum(probe["local_sample_counts"]), probe["global_sample_count"])
        self.assertAlmostEqual(probe["ddp_gradient"], -33.0, places=6)

    def test_data_hash_is_stable(self):
        self.assertEqual(_data_sha256(), _data_sha256())
        self.assertEqual(self.report["data_sha256"], _data_sha256())

    def test_fingerprint_is_stable_and_sensitive_to_config(self):
        config = self.report["config"]
        runtime = self.report["runtime"]
        code_hash = self.report["code_sha256"]
        data_hash = self.report["data_sha256"]
        first = run_fingerprint(config, code_hash, data_hash, runtime)
        second = run_fingerprint(config, code_hash, data_hash, runtime)
        changed = dict(config, seed=config["seed"] + 1)
        self.assertEqual(first, second)
        self.assertNotEqual(first, run_fingerprint(changed, code_hash, data_hash, runtime))

    def test_report_records_limitations_and_runtime(self):
        self.assertEqual(self.report["schema_version"], 1)
        self.assertIn("torch_version", self.report["runtime"])
        self.assertIn("not training", self.report["scope_note"])
        self.assertIn("not peak process/device memory", self.report["activation_checkpoint_probe"]["measurement_note"])
        self.assertIn("no GPU", self.report["distributed_probe"]["measurement_note"])

    def test_atomic_json_write_round_trip(self):
        with tempfile.TemporaryDirectory(prefix="ch46-json-") as temporary:
            destination = Path(temporary) / "nested" / "run.json"
            _atomic_write_json(destination, self.report)
            self.assertEqual(destination.read_text(encoding="utf-8").endswith("\n"), True)
            import json
            self.assertEqual(json.loads(destination.read_text(encoding="utf-8")), self.report)
            self.assertEqual(list(destination.parent.glob(".*.tmp")), [])

    def test_negative_seed_is_rejected(self):
        from scaling_lab import activation_checkpoint_probe
        with self.assertRaises(ValueError):
            activation_checkpoint_probe(seed=-1)


if __name__ == "__main__":
    unittest.main()
