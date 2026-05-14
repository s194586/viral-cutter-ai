from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np

from transcription.base import TranscriptSegment, normalize_speaker_label

from .base import DiarizationBackend, DiarizationConfig, DiarizationResult


FRAME_SIZE = 400
HOP_SIZE = 160
EPSILON = 1e-8


@dataclass
class _Cluster:
    centroid: np.ndarray
    indices: list[int]


@dataclass
class _ClusterSummary:
    label: int
    indices: list[int]
    duration_seconds: float
    segment_count: int
    share: float
    centroid: np.ndarray


class HeuristicDiarizationBackend(DiarizationBackend):
    name = "heuristic_cluster"

    def __init__(self, config: DiarizationConfig):
        self.config = config

    def assign_speakers(self, audio_path: Path, segments: list[TranscriptSegment]) -> DiarizationResult:
        started_at = time.perf_counter()
        if not self.config.enabled:
            self._apply_fallback(segments)
            return DiarizationResult(
                backend=self.name,
                enabled=False,
                status="disabled",
                speaker_count=1 if segments else 0,
                diarization_seconds=0.0,
                used_fallback=True,
                extra_metadata=self._build_diagnostics(segments, eligible_segments=0, assigned_segments=0),
            )

        try:
            waveform = self._load_audio(audio_path, sample_rate=self.config.sample_rate)
            feature_rows, feature_indices = self._extract_features(waveform, segments, self.config.sample_rate)
            if len(feature_rows) < 2:
                self._apply_fallback(segments)
                return DiarizationResult(
                    backend=self.name,
                    enabled=True,
                    status="fallback_single_speaker",
                    speaker_count=1 if segments else 0,
                    diarization_seconds=time.perf_counter() - started_at,
                    used_fallback=True,
                    extra_metadata=self._build_diagnostics(
                        segments,
                        eligible_segments=len(feature_rows),
                        assigned_segments=0,
                        raw_cluster_count=1 if len(feature_rows) else 0,
                        final_speaker_count=1 if segments else 0,
                        single_speaker_likelihood=1.0 if segments else 0.0,
                        multi_speaker_evidence=0.0,
                        clusters_merged=0,
                        tiny_clusters_removed=0,
                        decision_reason="insufficient_feature_segments",
                    ),
                )

            raw_labels = self._cluster_features(feature_rows)
            labels, decision_metadata = self._refine_labels(
                feature_rows,
                raw_labels,
                feature_indices,
                segments,
            )
            label_map = self._normalize_labels(labels, feature_indices)

            for segment_index, cluster_label in zip(feature_indices, labels):
                segments[segment_index].speaker = label_map[cluster_label]

            self._fill_unassigned_segments(segments)
            speaker_count = len({segment.speaker for segment in segments if segment.speaker})
            return DiarizationResult(
                backend=self.name,
                enabled=True,
                status="applied",
                speaker_count=speaker_count,
                diarization_seconds=time.perf_counter() - started_at,
                used_fallback=False,
                extra_metadata=self._build_diagnostics(
                    segments,
                    eligible_segments=len(feature_rows),
                    assigned_segments=len(feature_indices),
                    cluster_label_distribution=dict(sorted(Counter(labels).items())),
                    **decision_metadata,
                ),
            )
        except Exception as exc:
            self._apply_fallback(segments)
            return DiarizationResult(
                backend=self.name,
                enabled=True,
                status="fallback_error",
                speaker_count=1 if segments else 0,
                diarization_seconds=time.perf_counter() - started_at,
                used_fallback=True,
                extra_metadata=self._build_diagnostics(
                    segments,
                    eligible_segments=0,
                    assigned_segments=0,
                    error=str(exc),
                ),
            )

    def _apply_fallback(self, segments: list[TranscriptSegment]) -> None:
        for segment in segments:
            segment.speaker = "Speaker 0"

    def _load_audio(self, audio_path: Path, sample_rate: int) -> np.ndarray:
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(audio_path),
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-f",
            "s16le",
            "-",
        ]
        result = subprocess.run(cmd, capture_output=True, check=True)
        waveform = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
        return waveform

    def _extract_features(
        self,
        waveform: np.ndarray,
        segments: list[TranscriptSegment],
        sample_rate: int,
    ) -> tuple[np.ndarray, list[int]]:
        features: list[np.ndarray] = []
        indices: list[int] = []
        for index, segment in enumerate(segments):
            duration = segment.end - segment.start
            if duration < self.config.min_segment_seconds:
                continue
            feature_row = self._segment_features(
                waveform,
                sample_rate,
                start=segment.start,
                end=segment.end,
            )
            if feature_row is None:
                continue
            features.append(feature_row)
            indices.append(index)
        if not features:
            return np.zeros((0, 0), dtype=np.float32), indices
        matrix = np.vstack(features)
        normalized = matrix / np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), EPSILON)
        return normalized.astype(np.float32), indices

    def _segment_features(
        self,
        waveform: np.ndarray,
        sample_rate: int,
        *,
        start: float,
        end: float,
    ) -> np.ndarray | None:
        start_index = max(0, int(start * sample_rate))
        end_index = min(len(waveform), int(end * sample_rate))
        chunk = waveform[start_index:end_index]
        if len(chunk) < FRAME_SIZE:
            return None

        chunk = chunk - np.mean(chunk)
        rms = math.sqrt(float(np.mean(chunk**2)) + EPSILON)
        zcr = float(np.mean(np.abs(np.diff(np.signbit(chunk)).astype(np.float32))))

        frames = self._frame_audio(chunk)
        window = np.hanning(FRAME_SIZE).astype(np.float32)
        spectra = np.abs(np.fft.rfft(frames * window, axis=1)) + EPSILON
        power = spectra**2
        freqs = np.fft.rfftfreq(FRAME_SIZE, d=1.0 / sample_rate)

        spectral_sum = power.sum(axis=1) + EPSILON
        centroids = (power * freqs).sum(axis=1) / spectral_sum
        bandwidths = np.sqrt(((freqs - centroids[:, None]) ** 2 * power).sum(axis=1) / spectral_sum)

        cumulative = np.cumsum(power, axis=1)
        rolloff_threshold = spectral_sum[:, None] * 0.85
        rolloff_indices = (cumulative >= rolloff_threshold).argmax(axis=1)
        rolloffs = freqs[rolloff_indices]

        pitch_mask = (freqs >= 70) & (freqs <= 350)
        if np.any(pitch_mask):
            dominant_pitch = freqs[pitch_mask][power[:, pitch_mask].mean(axis=0).argmax()]
        else:
            dominant_pitch = 0.0

        band_edges = np.geomspace(80, sample_rate / 2, num=9)
        band_energies: list[float] = []
        for left, right in zip(band_edges[:-1], band_edges[1:]):
            mask = (freqs >= left) & (freqs < right)
            if not np.any(mask):
                band_energies.append(0.0)
                continue
            band_energies.append(float(np.log(power[:, mask].mean() + EPSILON)))

        feature_vector = np.array(
            [
                np.log(rms + EPSILON),
                zcr,
                float(np.mean(centroids) / max(sample_rate, 1)),
                float(np.std(centroids) / max(sample_rate, 1)),
                float(np.mean(bandwidths) / max(sample_rate, 1)),
                float(np.mean(rolloffs) / max(sample_rate, 1)),
                float(dominant_pitch / max(sample_rate, 1)),
                *band_energies,
            ],
            dtype=np.float32,
        )
        return feature_vector

    def _frame_audio(self, chunk: np.ndarray) -> np.ndarray:
        if len(chunk) < FRAME_SIZE:
            return np.zeros((0, FRAME_SIZE), dtype=np.float32)
        frame_count = 1 + max(0, (len(chunk) - FRAME_SIZE) // HOP_SIZE)
        frames = np.zeros((frame_count, FRAME_SIZE), dtype=np.float32)
        for frame_index in range(frame_count):
            start = frame_index * HOP_SIZE
            frames[frame_index] = chunk[start : start + FRAME_SIZE]
        return frames

    def _cluster_features(self, feature_rows: np.ndarray) -> list[int]:
        clusters: list[_Cluster] = []
        labels: list[int] = []

        for row_index, row in enumerate(feature_rows):
            if not clusters:
                clusters.append(_Cluster(centroid=row.copy(), indices=[row_index]))
                labels.append(0)
                continue

            similarities = [self._cosine_similarity(row, cluster.centroid) for cluster in clusters]
            best_index = int(np.argmax(similarities))
            best_similarity = similarities[best_index]

            if (
                best_similarity < self.config.similarity_threshold
                and len(clusters) < self.config.max_speakers
            ):
                new_label = len(clusters)
                clusters.append(_Cluster(centroid=row.copy(), indices=[row_index]))
                labels.append(new_label)
                continue

            labels.append(best_index)
            clusters[best_index].indices.append(row_index)
            clusters[best_index].centroid = feature_rows[clusters[best_index].indices].mean(axis=0)

        for _ in range(2):
            for cluster_index, cluster in enumerate(clusters):
                cluster.indices = [row_index for row_index, label in enumerate(labels) if label == cluster_index]
                if cluster.indices:
                    cluster.centroid = feature_rows[cluster.indices].mean(axis=0)

            for row_index, row in enumerate(feature_rows):
                similarities = [self._cosine_similarity(row, cluster.centroid) for cluster in clusters]
                labels[row_index] = int(np.argmax(similarities))

        return labels

    def _refine_labels(
        self,
        feature_rows: np.ndarray,
        raw_labels: list[int],
        feature_indices: list[int],
        segments: list[TranscriptSegment],
    ) -> tuple[list[int], dict[str, Any]]:
        if not raw_labels:
            return [], {
                "raw_cluster_count": 0,
                "final_speaker_count": 0,
                "single_speaker_likelihood": 1.0 if segments else 0.0,
                "multi_speaker_evidence": 0.0,
                "clusters_merged": 0,
                "tiny_clusters_removed": 0,
                "decision_reason": "no_clusters",
            }

        durations = [max(0.0, segments[index].end - segments[index].start) for index in feature_indices]
        raw_cluster_count = len(set(raw_labels))
        labels = list(raw_labels)
        clusters_merged = 0
        tiny_clusters_removed = 0

        labels, merged_now, removed_now = self._merge_small_or_similar_clusters(
            feature_rows,
            labels,
            durations,
        )
        clusters_merged += merged_now
        tiny_clusters_removed += removed_now

        raw_summaries = self._summarize_clusters(feature_rows, raw_labels, durations)
        final_summaries = self._summarize_clusters(feature_rows, labels, durations)
        adjacent_similarity_mean = self._adjacent_similarity_mean(feature_rows)
        top_cluster_similarity = self._top_cluster_similarity(final_summaries)
        stable_cluster_count = sum(
            1
            for summary in final_summaries
            if summary.share >= self.config.multi_speaker_min_share
        )
        alternating_blocks = self._count_alternating_blocks(labels)
        dominant_share = final_summaries[0].share if final_summaries else 1.0

        single_speaker_likelihood = self._estimate_single_speaker_likelihood(
            adjacent_similarity_mean=adjacent_similarity_mean,
            top_cluster_similarity=top_cluster_similarity,
            dominant_share=dominant_share,
            stable_cluster_count=stable_cluster_count,
            raw_cluster_count=raw_cluster_count,
            final_summaries=final_summaries,
            alternating_blocks=alternating_blocks,
        )
        multi_speaker_evidence = self._estimate_multi_speaker_evidence(
            adjacent_similarity_mean=adjacent_similarity_mean,
            top_cluster_similarity=top_cluster_similarity,
            stable_cluster_count=stable_cluster_count,
            final_summaries=final_summaries,
            alternating_blocks=alternating_blocks,
        )

        decision_reason = "kept_multi_speaker_clusters"
        if self._should_collapse_to_single(
            single_speaker_likelihood=single_speaker_likelihood,
            multi_speaker_evidence=multi_speaker_evidence,
            top_cluster_similarity=top_cluster_similarity,
            stable_cluster_count=stable_cluster_count,
            final_summaries=final_summaries,
        ):
            labels = [0 for _ in labels]
            final_summaries = self._summarize_clusters(feature_rows, labels, durations)
            decision_reason = "collapsed_to_single_speaker_due_to_weak_multi_evidence"
        else:
            labels, merged_now = self._merge_residual_small_clusters(
                feature_rows,
                labels,
                durations,
            )
            clusters_merged += merged_now
            final_summaries = self._summarize_clusters(feature_rows, labels, durations)

        diagnostics = {
            "raw_cluster_count": raw_cluster_count,
            "final_speaker_count": len(final_summaries),
            "raw_cluster_distribution": {
                f"Cluster {summary.label}": summary.segment_count for summary in raw_summaries
            },
            "raw_cluster_duration_share": {
                f"Cluster {summary.label}": round(float(summary.share), 4) for summary in raw_summaries
            },
            "single_speaker_likelihood": round(float(single_speaker_likelihood), 4),
            "multi_speaker_evidence": round(float(multi_speaker_evidence), 4),
            "clusters_merged": int(clusters_merged),
            "tiny_clusters_removed": int(tiny_clusters_removed),
            "decision_reason": decision_reason,
            "adjacent_similarity_mean": round(float(adjacent_similarity_mean), 4),
            "top_cluster_similarity": round(float(top_cluster_similarity), 4),
            "stable_cluster_count": int(stable_cluster_count),
            "alternating_blocks": int(alternating_blocks),
        }
        return labels, diagnostics

    def _merge_small_or_similar_clusters(
        self,
        feature_rows: np.ndarray,
        labels: list[int],
        durations: list[float],
    ) -> tuple[list[int], int, int]:
        if not labels:
            return labels, 0, 0

        merged = 0
        removed = 0
        working = list(labels)

        while True:
            summaries = self._summarize_clusters(feature_rows, working, durations)
            if len(summaries) <= 1:
                break

            candidate = None
            target = None
            best_similarity = -1.0
            for summary in reversed(summaries):
                if not self._is_small_cluster(summary):
                    continue
                for other in summaries:
                    if other.label == summary.label:
                        continue
                    similarity = self._cosine_similarity(summary.centroid, other.centroid)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        candidate = summary.label
                        target = other.label
            if candidate is None or target is None:
                break

            for index, label in enumerate(working):
                if label == candidate:
                    working[index] = target
            merged += 1
            if best_similarity >= self.config.merge_similarity_threshold:
                removed += 1

        return working, merged, removed

    def _merge_residual_small_clusters(
        self,
        feature_rows: np.ndarray,
        labels: list[int],
        durations: list[float],
    ) -> tuple[list[int], int]:
        if not labels:
            return labels, 0

        working = list(labels)
        merged = 0
        while True:
            summaries = self._summarize_clusters(feature_rows, working, durations)
            dominant = summaries[0] if summaries else None
            candidate = next(
                (
                    summary
                    for summary in reversed(summaries)
                    if dominant is not None
                    and summary.label != dominant.label
                    and summary.share < self.config.min_cluster_share
                ),
                None,
            )
            if candidate is None or dominant is None:
                break
            for index, label in enumerate(working):
                if label == candidate.label:
                    working[index] = dominant.label
            merged += 1
        return working, merged

    def _summarize_clusters(
        self,
        feature_rows: np.ndarray,
        labels: list[int],
        durations: list[float],
    ) -> list[_ClusterSummary]:
        grouped: dict[int, list[int]] = {}
        for row_index, label in enumerate(labels):
            grouped.setdefault(int(label), []).append(row_index)
        total_duration = sum(durations[index] for index in range(len(labels))) or float(len(labels)) or 1.0
        summaries: list[_ClusterSummary] = []
        for label, indices in grouped.items():
            duration_seconds = sum(durations[index] for index in indices)
            summaries.append(
                _ClusterSummary(
                    label=label,
                    indices=indices,
                    duration_seconds=duration_seconds,
                    segment_count=len(indices),
                    share=duration_seconds / total_duration,
                    centroid=feature_rows[indices].mean(axis=0),
                )
            )
        return sorted(
            summaries,
            key=lambda summary: (summary.share, summary.duration_seconds, summary.segment_count),
            reverse=True,
        )

    def _is_small_cluster(self, summary: _ClusterSummary) -> bool:
        return (
            summary.share < self.config.min_cluster_share
            or summary.duration_seconds < self.config.min_cluster_seconds
            or summary.segment_count < self.config.min_cluster_segments
        )

    def _adjacent_similarity_mean(self, feature_rows: np.ndarray) -> float:
        if len(feature_rows) < 2:
            return 1.0
        similarities = [
            self._cosine_similarity(feature_rows[index], feature_rows[index + 1])
            for index in range(len(feature_rows) - 1)
        ]
        return float(sum(similarities) / max(len(similarities), 1))

    def _top_cluster_similarity(self, summaries: list[_ClusterSummary]) -> float:
        if len(summaries) < 2:
            return 1.0
        top = summaries[:2]
        return self._cosine_similarity(top[0].centroid, top[1].centroid)

    def _count_alternating_blocks(self, labels: list[int]) -> int:
        if not labels:
            return 0
        run_labels: list[int] = []
        for label in labels:
            if not run_labels or run_labels[-1] != label:
                run_labels.append(label)
        return max(0, len(run_labels) - 1)

    def _estimate_single_speaker_likelihood(
        self,
        *,
        adjacent_similarity_mean: float,
        top_cluster_similarity: float,
        dominant_share: float,
        stable_cluster_count: int,
        raw_cluster_count: int,
        final_summaries: list[_ClusterSummary],
        alternating_blocks: int,
    ) -> float:
        likelihood = 0.0
        if adjacent_similarity_mean >= self.config.single_speaker_similarity_floor:
            likelihood += 0.3
        elif adjacent_similarity_mean >= self.config.single_speaker_similarity_floor - 0.02:
            likelihood += 0.18

        if top_cluster_similarity >= self.config.merge_similarity_threshold:
            likelihood += 0.32
        elif top_cluster_similarity >= self.config.merge_similarity_threshold - 0.03:
            likelihood += 0.16

        if dominant_share >= 0.7:
            likelihood += 0.18
        elif dominant_share >= 0.55:
            likelihood += 0.08

        if stable_cluster_count <= 1:
            likelihood += 0.14
        elif stable_cluster_count == 2 and top_cluster_similarity >= self.config.merge_similarity_threshold:
            likelihood += 0.08

        if raw_cluster_count > len(final_summaries):
            likelihood += 0.08

        if alternating_blocks >= 16:
            likelihood -= 0.08
        if stable_cluster_count >= 3:
            likelihood -= 0.12

        return max(0.0, min(1.0, likelihood))

    def _estimate_multi_speaker_evidence(
        self,
        *,
        adjacent_similarity_mean: float,
        top_cluster_similarity: float,
        stable_cluster_count: int,
        final_summaries: list[_ClusterSummary],
        alternating_blocks: int,
    ) -> float:
        evidence = 0.0
        stable_shares = [summary.share for summary in final_summaries if summary.share >= self.config.multi_speaker_min_share]
        if len(stable_shares) >= 2:
            evidence += 0.34
        if len(stable_shares) >= 3:
            evidence += 0.18
        if len(stable_shares) >= 2 and top_cluster_similarity < self.config.merge_similarity_threshold - 0.03:
            evidence += 0.28
        elif len(stable_shares) >= 2 and top_cluster_similarity < self.config.merge_similarity_threshold:
            evidence += 0.18
        if alternating_blocks >= 24:
            evidence += 0.12
        elif alternating_blocks >= 12:
            evidence += 0.06
        if adjacent_similarity_mean < self.config.single_speaker_similarity_floor - 0.025:
            evidence += 0.12
        if stable_cluster_count == 1:
            evidence -= 0.18
        return max(0.0, min(1.0, evidence))

    def _should_collapse_to_single(
        self,
        *,
        single_speaker_likelihood: float,
        multi_speaker_evidence: float,
        top_cluster_similarity: float,
        stable_cluster_count: int,
        final_summaries: list[_ClusterSummary],
    ) -> bool:
        if len(final_summaries) <= 1:
            return True
        if stable_cluster_count <= 1 and single_speaker_likelihood >= 0.45:
            return True
        if (
            single_speaker_likelihood >= self.config.single_speaker_likelihood_threshold
            and multi_speaker_evidence < 0.55
        ):
            return True
        if (
            stable_cluster_count == 2
            and top_cluster_similarity >= self.config.merge_similarity_threshold
            and multi_speaker_evidence < 0.6
        ):
            return True
        if (
            single_speaker_likelihood >= 0.4
            and top_cluster_similarity >= self.config.merge_similarity_threshold + 0.02
            and multi_speaker_evidence < 0.75
        ):
            return True
        return False

    def _normalize_labels(self, labels: list[int], feature_indices: list[int]) -> dict[int, str]:
        ordered_labels: list[int] = []
        for segment_index, label in sorted(zip(feature_indices, labels), key=lambda item: item[0]):
            if label not in ordered_labels:
                ordered_labels.append(label)
        return {label: normalize_speaker_label(f"Speaker {index}") for index, label in enumerate(ordered_labels)}

    def _fill_unassigned_segments(self, segments: list[TranscriptSegment]) -> None:
        last_speaker = "Speaker 0"
        for segment in segments:
            if segment.speaker:
                last_speaker = segment.speaker
            else:
                segment.speaker = last_speaker

        next_speaker = "Speaker 0"
        for segment in reversed(segments):
            if segment.speaker:
                next_speaker = segment.speaker
            else:
                segment.speaker = next_speaker

        counts = Counter(segment.speaker for segment in segments if segment.speaker)
        fallback_speaker = counts.most_common(1)[0][0] if counts else "Speaker 0"
        for segment in segments:
            if not segment.speaker:
                segment.speaker = fallback_speaker

    def _build_diagnostics(
        self,
        segments: list[TranscriptSegment],
        *,
        eligible_segments: int,
        assigned_segments: int,
        **extra: Any,
    ) -> dict[str, Any]:
        speakers = [normalize_speaker_label(segment.speaker) for segment in segments if segment.speaker]
        speaker_counts = Counter(speakers)
        switches = sum(1 for left, right in zip(speakers, speakers[1:]) if left != right)
        dominant_ratio = speaker_counts.most_common(1)[0][1] / len(speakers) if speakers else 0.0
        diagnostics = {
            "eligible_segments": int(eligible_segments),
            "assigned_segments": int(assigned_segments),
            "max_speakers": self.config.max_speakers,
            "speaker_distribution": dict(sorted(speaker_counts.items())),
            "speaker_switches": switches,
            "dominant_speaker_ratio": round(float(dominant_ratio), 4),
        }
        diagnostics.update(extra)
        return diagnostics

    def _cosine_similarity(self, left: np.ndarray, right: np.ndarray) -> float:
        denominator = (np.linalg.norm(left) * np.linalg.norm(right)) + EPSILON
        return float(np.dot(left, right) / denominator)
