from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import torch

from preference_lab import (
    audit_fixture,
    dpo_loss,
    grpo_group_advantages,
    pairwise_reward_loss,
    ppo_clipped_policy_loss,
    run_toy_dpo,
    split_by_group,
    validate_preferences,
)

FIXTURE = Path(__file__).with_name("sample_preferences.jsonl")


def read_fixture() -> list[dict[str, object]]:
    return [json.loads(line) for line in FIXTURE.read_text(encoding="utf-8").splitlines()]


class DatasetAuditTests(unittest.TestCase):
    def test_fixture_audit_records_limits_and_hash(self) -> None:
        report = audit_fixture(FIXTURE)
        self.assertEqual(report["records"], 12)
        self.assertEqual(report["group_count"], 6)
        self.assertEqual(report["label_source_counts"], {"synthetic_fixture": 12})
        self.assertEqual(sum(part["records"] for part in report["split_counts"].values()), 12)
        self.assertFalse(report["training_performed"])
        self.assertFalse(report["model_downloaded"])
        self.assertEqual(len(report["sha256"]), 64)
        self.assertIn("not human", report["fixture_kind"])

    def test_duplicate_ids_are_rejected(self) -> None:
        rows = read_fixture()[:2]
        rows[1]["id"] = rows[0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate id"):
            validate_preferences(rows)

    def test_identical_choice_pair_is_rejected(self) -> None:
        rows = read_fixture()[:1]
        rows[0]["rejected"] = rows[0]["chosen"]
        with self.assertRaisesRegex(ValueError, "must differ"):
            validate_preferences(rows)

    def test_empty_field_is_rejected(self) -> None:
        rows = read_fixture()[:1]
        rows[0]["prompt"] = "  "
        with self.assertRaisesRegex(ValueError, "non-empty string"):
            validate_preferences(rows)

    def test_unknown_label_source_is_rejected(self) -> None:
        rows = read_fixture()[:1]
        rows[0]["label_source"] = "invented"
        with self.assertRaisesRegex(ValueError, "unsupported label_source"):
            validate_preferences(rows)

    def test_group_split_is_deterministic_and_disjoint(self) -> None:
        rows = validate_preferences(read_fixture())
        first = split_by_group(rows, seed=49)
        second = split_by_group(rows, seed=49)
        self.assertEqual(first, second)
        group_sets = [{row["group_id"] for row in first[name]} for name in ("train", "validation", "test")]
        self.assertEqual(len(group_sets[0] & group_sets[1]), 0)
        self.assertEqual(len(group_sets[0] & group_sets[2]), 0)
        self.assertEqual(len(group_sets[1] & group_sets[2]), 0)

    def test_group_split_rejects_too_few_groups(self) -> None:
        rows = validate_preferences(read_fixture()[:2])
        with self.assertRaisesRegex(ValueError, "at least three"):
            split_by_group(rows)

    def test_malformed_jsonl_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.jsonl"
            path.write_text("{not json}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid JSON on line 1"):
                audit_fixture(path)


class PreferenceObjectiveTests(unittest.TestCase):
    def test_pairwise_reward_loss_matches_bradley_terry_nll(self) -> None:
        chosen = torch.tensor([1.0])
        rejected = torch.tensor([0.0])
        actual = pairwise_reward_loss(chosen, rejected)
        expected = torch.nn.functional.softplus(torch.tensor(-1.0))
        self.assertTrue(torch.allclose(actual, expected))

    def test_pairwise_reward_gradient_pushes_scores_in_order(self) -> None:
        chosen = torch.tensor([0.2], requires_grad=True)
        rejected = torch.tensor([-0.1], requires_grad=True)
        pairwise_reward_loss(chosen, rejected).backward()
        self.assertLess(chosen.grad.item(), 0.0)
        self.assertGreater(rejected.grad.item(), 0.0)

    def test_pairwise_reward_rejects_shape_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "same shape"):
            pairwise_reward_loss(torch.tensor([1.0]), torch.tensor([0.0, -1.0]))

    def test_dpo_loss_matches_manual_reference_adjusted_margin(self) -> None:
        chosen_pi = torch.tensor([torch.log(torch.tensor(0.8)).item()])
        rejected_pi = torch.tensor([torch.log(torch.tensor(0.2)).item()])
        chosen_ref = torch.tensor([torch.log(torch.tensor(0.5)).item()])
        rejected_ref = torch.tensor([torch.log(torch.tensor(0.5)).item()])
        actual = dpo_loss(chosen_pi, rejected_pi, chosen_ref, rejected_ref, beta=1.0)
        self.assertAlmostEqual(actual.item(), -torch.log(torch.tensor(0.8)).item(), places=6)

    def test_dpo_gradient_increases_preferred_relative_log_probability(self) -> None:
        chosen = torch.tensor([-0.7], requires_grad=True)
        rejected = torch.tensor([-0.7], requires_grad=True)
        ref_chosen = torch.tensor([-0.7])
        ref_rejected = torch.tensor([-0.7])
        dpo_loss(chosen, rejected, ref_chosen, ref_rejected, beta=0.2).backward()
        self.assertLess(chosen.grad.item(), 0.0)
        self.assertGreater(rejected.grad.item(), 0.0)

    def test_dpo_rejects_nonpositive_beta(self) -> None:
        values = torch.tensor([-0.5])
        with self.assertRaisesRegex(ValueError, "beta must be finite and positive"):
            dpo_loss(values, values, values, values, beta=0.0)

    def test_dpo_rejects_shape_mismatch(self) -> None:
        values = torch.tensor([-0.5])
        with self.assertRaisesRegex(ValueError, "same shape"):
            dpo_loss(values, values, torch.tensor([-0.5, -0.4]), torch.tensor([-0.5, -0.4]), beta=0.1)


class GroupAndClippingTests(unittest.TestCase):
    def test_grpo_advantages_normalize_per_prompt_group(self) -> None:
        rewards = torch.tensor([1.0, 3.0, 10.0, 10.0])
        advantages = grpo_group_advantages(rewards, ["a", "a", "b", "b"])
        self.assertAlmostEqual(advantages[0].item(), -1.0, places=5)
        self.assertAlmostEqual(advantages[1].item(), 1.0, places=5)
        self.assertTrue(torch.equal(advantages[2:], torch.zeros(2)))

    def test_grpo_singleton_and_constant_groups_are_zero(self) -> None:
        rewards = torch.tensor([4.0, 2.0, 2.0])
        advantages = grpo_group_advantages(rewards, ["single", "same", "same"])
        self.assertTrue(torch.equal(advantages, torch.zeros(3)))

    def test_grpo_rejects_group_count_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "length must match"):
            grpo_group_advantages(torch.tensor([1.0, 2.0]), ["only-one"])

    def test_ppo_positive_advantage_uses_upper_clip(self) -> None:
        loss = ppo_clipped_policy_loss(
            torch.tensor([torch.log(torch.tensor(1.5)).item()]),
            torch.tensor([0.0]), torch.tensor([1.0]), clip_range=0.2,
        )
        self.assertAlmostEqual(loss.item(), -1.2, places=5)

    def test_ppo_negative_advantage_uses_lower_clip(self) -> None:
        loss = ppo_clipped_policy_loss(
            torch.tensor([torch.log(torch.tensor(0.5)).item()]),
            torch.tensor([0.0]), torch.tensor([-1.0]), clip_range=0.2,
        )
        self.assertAlmostEqual(loss.item(), 0.8, places=5)

    def test_ppo_rejects_invalid_clip_range(self) -> None:
        values = torch.tensor([0.0])
        with self.assertRaisesRegex(ValueError, "clip_range"):
            ppo_clipped_policy_loss(values, values, values, clip_range=1.0)


class ToyRunTests(unittest.TestCase):
    def test_toy_dpo_smoke_run_reduces_loss_without_loading_model(self) -> None:
        report = run_toy_dpo(steps=80, seed=49)
        self.assertLess(report["final_dpo_loss"], report["initial_dpo_loss"])
        self.assertGreater(report["policy_chosen_probability"], 0.5)
        self.assertFalse(report["model_loaded"])
        self.assertFalse(report["model_downloaded"])
        self.assertEqual(report["device"], "cpu")


if __name__ == "__main__":
    unittest.main(verbosity=2)
