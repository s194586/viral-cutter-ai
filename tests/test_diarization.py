import unittest
from pathlib import Path

import numpy as np

from diarization import DiarizationConfig, HeuristicDiarizationBackend
from transcription.base import TranscriptSegment


def _normalize_rows(rows):
    matrix = np.asarray(rows, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, 1e-8)


def _make_segments(count: int, *, duration: float = 2.0) -> list[TranscriptSegment]:
    segments = []
    cursor = 0.0
    for index in range(count):
        segments.append(
            TranscriptSegment(
                start=cursor,
                end=cursor + duration,
                text=f"Segment {index}",
            )
        )
        cursor += duration
    return segments


class HeuristicDiarizationBackendTests(unittest.TestCase):
    def setUp(self):
        self.backend = HeuristicDiarizationBackend(DiarizationConfig(enabled=True))

    def test_single_speaker_like_profile_collapses_to_one_speaker(self):
        feature_rows = _normalize_rows(
            [
                [1.0, 0.02, 0.0, 0.0],
                [0.99, 0.03, 0.0, 0.0],
                [1.01, 0.01, 0.0, 0.0],
                [1.0, 0.04, 0.0, 0.0],
                [0.98, 0.02, 0.0, 0.0],
                [1.02, 0.01, 0.0, 0.0],
                [0.99, 0.01, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [0.98, 0.06, 0.0, 0.0],
                [1.01, 0.05, 0.0, 0.0],
                [0.99, 0.04, 0.0, 0.0],
                [1.0, 0.05, 0.0, 0.0],
            ]
        )
        raw_labels = [0, 0, 1, 1, 0, 0, 1, 1, 2, 2, 1, 0]
        feature_indices = list(range(len(raw_labels)))
        segments = _make_segments(len(raw_labels), duration=4.0)

        labels, diagnostics = self.backend._refine_labels(
            feature_rows,
            raw_labels,
            feature_indices,
            segments,
        )

        self.assertEqual(len(set(labels)), 1)
        self.assertEqual(diagnostics["final_speaker_count"], 1)
        self.assertGreaterEqual(diagnostics["single_speaker_likelihood"], 0.58)
        self.assertIn("single_speaker", diagnostics["decision_reason"])

    def test_multi_speaker_like_profile_stays_multi_speaker(self):
        feature_rows = _normalize_rows(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.98, 0.02, 0.0, 0.0],
                [1.01, 0.01, 0.0, 0.0],
                [0.99, 0.03, 0.0, 0.0],
                [1.02, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.02, 0.99, 0.0, 0.0],
                [0.01, 1.01, 0.0, 0.0],
                [0.03, 0.98, 0.0, 0.0],
                [0.0, 1.02, 0.0, 0.0],
                [1.01, 0.0, 0.0, 0.0],
                [0.99, 0.01, 0.0, 0.0],
                [1.02, 0.02, 0.0, 0.0],
                [0.98, 0.02, 0.0, 0.0],
                [1.0, 0.01, 0.0, 0.0],
                [0.15, 0.93, 0.0, 0.0],
                [0.14, 0.92, 0.0, 0.0],
                [0.01, 1.0, 0.0, 0.0],
                [0.0, 0.99, 0.0, 0.0],
                [0.02, 1.01, 0.0, 0.0],
                [0.03, 0.98, 0.0, 0.0],
                [0.0, 1.02, 0.0, 0.0],
            ]
        )
        raw_labels = [0] * 5 + [1] * 5 + [0] * 5 + [2] * 2 + [1] * 5
        feature_indices = list(range(len(raw_labels)))
        segments = _make_segments(len(raw_labels), duration=4.0)

        labels, diagnostics = self.backend._refine_labels(
            feature_rows,
            raw_labels,
            feature_indices,
            segments,
        )

        self.assertGreater(len(set(labels)), 1)
        self.assertEqual(diagnostics["final_speaker_count"], 2)
        self.assertGreater(diagnostics["multi_speaker_evidence"], 0.55)
        self.assertEqual(diagnostics["decision_reason"], "kept_multi_speaker_clusters")

    def test_tiny_clusters_are_merged_into_dominant_speaker(self):
        feature_rows = _normalize_rows(
            [
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.01, 0.0, 0.0],
                [1.01, 0.0, 0.0, 0.0],
                [0.99, 0.02, 0.0, 0.0],
                [1.0, 0.03, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.02, 0.99, 0.0, 0.0],
                [0.0, 1.01, 0.0, 0.0],
                [0.01, 1.0, 0.0, 0.0],
                [0.08, 0.96, 0.0, 0.0],
                [1.02, 0.01, 0.0, 0.0],
                [1.0, 0.02, 0.0, 0.0],
                [0.01, 0.99, 0.0, 0.0],
                [0.02, 1.01, 0.0, 0.0],
            ]
        )
        raw_labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 0, 0, 1, 1]
        feature_indices = list(range(len(raw_labels)))
        segments = _make_segments(len(raw_labels), duration=4.0)

        labels, diagnostics = self.backend._refine_labels(
            feature_rows,
            raw_labels,
            feature_indices,
            segments,
        )

        self.assertEqual(len(set(labels)), 2)
        self.assertGreaterEqual(diagnostics["clusters_merged"], 1)
        self.assertGreaterEqual(diagnostics["tiny_clusters_removed"], 1)

    def test_disabled_backend_uses_safe_fallback(self):
        backend = HeuristicDiarizationBackend(DiarizationConfig(enabled=False))
        segments = _make_segments(3)

        result = backend.assign_speakers(Path("missing.wav"), segments)

        self.assertTrue(result.used_fallback)
        self.assertEqual(result.status, "disabled")
        self.assertEqual(result.speaker_count, 1)
        self.assertTrue(all(segment.speaker == "Speaker 0" for segment in segments))


if __name__ == "__main__":
    unittest.main()
