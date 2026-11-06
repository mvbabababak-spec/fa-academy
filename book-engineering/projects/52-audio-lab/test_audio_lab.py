"""Unit tests for the chapter 52 synthetic audio and transcript fixtures."""
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

from audio_lab import (
    audit_fixture,
    character_error_stats,
    corpus_word_error_stats,
    edit_counts,
    frame_signal,
    load_fixture,
    make_synthetic_tone,
    root_mean_square,
    sentence_macro_word_error_rate,
    single_sided_power_spectrum,
    word_error_stats,
)

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "sample_transcripts.json"


class FixtureTests(unittest.TestCase):
    def test_fixture_has_three_synthetic_text_pairs_and_no_audio(self):
        result = audit_fixture(FIXTURE)
        self.assertEqual(result["fixture"]["records"], 3)
        self.assertFalse(result["fixture"]["audio_recordings_included"])
        self.assertFalse(result["fixture"]["model_outputs_included"])
        self.assertFalse(result["training_performed"])
        self.assertFalse(result["speech_model_loaded"])

    def test_fixture_sha256_is_stable(self):
        result = audit_fixture(FIXTURE)
        self.assertEqual(result["fixture"]["sha256"], hashlib.sha256(FIXTURE.read_bytes()).hexdigest())

    def test_duplicate_ids_are_rejected(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload["records"][1]["id"] = payload["records"][0]["id"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unique"):
                load_fixture(path)

    def test_non_synthetic_record_is_rejected(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload["records"][0]["label_source"] = "model_output"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad-source.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "synthetic fixture"):
                load_fixture(path)

    def test_fixture_must_explicitly_exclude_recordings(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload["metadata"]["audio_recordings_included"] = True
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "audio-present.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no audio recordings"):
                load_fixture(path)

    def test_empty_record_list_is_rejected(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload["records"] = []
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "empty.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "at least one"):
                load_fixture(path)


class SignalTests(unittest.TestCase):
    def test_generated_tone_has_expected_sample_count_and_peak(self):
        tone = make_synthetic_tone(sample_rate=16_000, duration_ms=100, frequency_hz=440.0)
        self.assertEqual(len(tone), 1_600)
        self.assertLessEqual(max(abs(sample) for sample in tone), 0.5)

    def test_tone_frequency_must_be_below_nyquist(self):
        with self.assertRaisesRegex(ValueError, "Nyquist"):
            make_synthetic_tone(sample_rate=16_000, duration_ms=100, frequency_hz=8_000.0)

    def test_tone_amplitude_must_be_in_range(self):
        with self.assertRaisesRegex(ValueError, "amplitude"):
            make_synthetic_tone(amplitude=1.1)

    def test_frame_count_for_one_hundred_milliseconds(self):
        tone = make_synthetic_tone()
        frames = frame_signal(tone, 16_000, frame_ms=25, hop_ms=10)
        self.assertEqual(len(frames), 8)

    def test_frame_and_hop_sample_counts(self):
        tone = make_synthetic_tone()
        frames = frame_signal(tone, 16_000, frame_ms=25, hop_ms=10)
        self.assertEqual(len(frames[0]), 400)
        self.assertEqual(frames[1][0], tone[160])

    def test_non_padded_short_signal_has_no_complete_frame(self):
        self.assertEqual(frame_signal([0.0] * 100, 16_000), [])

    def test_padded_short_signal_returns_one_complete_frame(self):
        frames = frame_signal([0.25] * 100, 16_000, pad_end=True)
        self.assertEqual(len(frames), 1)
        self.assertEqual(len(frames[0]), 400)
        self.assertEqual(frames[0][-1], 0.0)

    def test_padded_tail_adds_partial_final_frame(self):
        tone = make_synthetic_tone()
        frames = frame_signal(tone, 16_000, frame_ms=25, hop_ms=10, pad_end=True)
        self.assertEqual(len(frames), 10)
        self.assertEqual(len(frames[-1]), 400)
        self.assertEqual(frames[-1][-1], 0.0)

    def test_empty_signal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            frame_signal([], 16_000)

    def test_invalid_sample_rate_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "sample_rate"):
            frame_signal([0.0], 0)

    def test_non_finite_sample_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            frame_signal([0.0, math.inf], 16_000)

    def test_invalid_frame_duration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "frame_ms"):
            frame_signal([0.0] * 500, 16_000, frame_ms=0)

    def test_invalid_hop_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "hop_ms"):
            frame_signal([0.0] * 500, 16_000, hop_ms=float("nan"))

    def test_rms_of_zeros_is_zero(self):
        self.assertEqual(root_mean_square([0.0, 0.0]), 0.0)

    def test_rms_of_sine_is_finite_and_below_peak(self):
        frames = frame_signal(make_synthetic_tone(), 16_000)
        rms = root_mean_square(frames[0])
        self.assertTrue(math.isfinite(rms))
        self.assertAlmostEqual(rms, 0.5 / math.sqrt(2), places=3)

    def test_spectrum_has_expected_number_of_nonnegative_bins(self):
        frames = frame_signal(make_synthetic_tone(), 16_000)
        spectrum = single_sided_power_spectrum(frames[0], 16_000)
        self.assertEqual(len(spectrum), 201)
        self.assertTrue(all(value >= 0 for value in spectrum))

    def test_spectrum_peak_matches_analytic_tone(self):
        frames = frame_signal(make_synthetic_tone(), 16_000)
        spectrum = single_sided_power_spectrum(frames[0], 16_000)
        peak_bin = max(range(len(spectrum)), key=spectrum.__getitem__)
        self.assertEqual(peak_bin, 11)
        self.assertEqual(peak_bin * 16_000 / len(frames[0]), 440.0)

    def test_fft_cannot_be_shorter_than_frame(self):
        frames = frame_signal(make_synthetic_tone(), 16_000)
        with self.assertRaisesRegex(ValueError, "shorter"):
            single_sided_power_spectrum(frames[0], 16_000, n_fft=100)


class MetricTests(unittest.TestCase):
    def test_equal_transcripts_have_zero_wer(self):
        self.assertEqual(word_error_stats("turn left", "turn left")["error_rate"], 0.0)

    def test_substitution_and_deletion_counts(self):
        result = word_error_stats("turn left at the bridge", "turn right at bridge")
        self.assertEqual((result["substitutions"], result["deletions"], result["insertions"]), (1, 1, 0))
        self.assertEqual(result["error_rate"], 2 / 5)

    def test_insertion_count(self):
        result = word_error_stats("call Mina at noon", "call Mina tomorrow at noon")
        self.assertEqual(result["insertions"], 1)
        self.assertEqual(result["error_rate"], 1 / 4)

    def test_wer_has_no_upper_bound(self):
        self.assertEqual(word_error_stats("yes", "no now")["error_rate"], 2.0)

    def test_word_normalization_case_and_whitespace(self):
        self.assertEqual(word_error_stats("  Call  MINA ", "call mina")["error_rate"], 0.0)

    def test_word_edit_counts_can_be_used_independently(self):
        counts = edit_counts(["a", "b"], ["a", "c", "d"])
        self.assertEqual(counts["edit_distance"], 2)
        self.assertEqual(counts["insertions"], 1)

    def test_wer_empty_reference_is_undefined(self):
        with self.assertRaisesRegex(ValueError, "empty reference"):
            word_error_stats("   ", "something")

    def test_cer_counts_character_substitution(self):
        result = character_error_stats("cat", "cut")
        self.assertEqual(result["substitutions"], 1)
        self.assertEqual(result["reference_units"], 3)
        self.assertEqual(result["error_rate"], 1 / 3)

    def test_cer_normalizes_canonical_unicode(self):
        self.assertEqual(character_error_stats("é", "e\u0301")["error_rate"], 0.0)

    def test_cer_ignores_whitespace_by_documented_policy(self):
        self.assertEqual(character_error_stats("a b", "ab")["error_rate"], 0.0)

    def test_cer_keeps_punctuation(self):
        result = character_error_stats("a!", "a")
        self.assertEqual(result["deletions"], 1)
        self.assertEqual(result["error_rate"], 0.5)

    def test_cer_empty_reference_is_undefined(self):
        with self.assertRaisesRegex(ValueError, "empty reference"):
            character_error_stats("   ", "x")

    def test_corpus_wer_pools_error_counts_before_division(self):
        records = load_fixture(FIXTURE)["records"]
        result = corpus_word_error_stats(records)
        self.assertEqual(result["reference_units"], 11)
        self.assertEqual(result["edit_distance"], 3)
        self.assertEqual(result["error_rate"], 3 / 11)

    def test_sentence_macro_wer_is_a_different_aggregation(self):
        records = load_fixture(FIXTURE)["records"]
        macro = sentence_macro_word_error_rate(records)
        pooled = corpus_word_error_stats(records)["error_rate"]
        self.assertAlmostEqual(macro, (0.4 + 0.25 + 0.0) / 3)
        self.assertNotEqual(macro, pooled)

    def test_empty_corpus_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            corpus_word_error_stats([])


if __name__ == "__main__":
    unittest.main()
