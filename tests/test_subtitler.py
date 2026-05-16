import unittest
from unittest.mock import patch

import subtitler


class SubtitlerSpeakerTests(unittest.TestCase):
    def test_speaker_style_is_deterministic_for_same_label(self):
        first = subtitler.speaker_style("Speaker 3")
        second = subtitler.speaker_style("Speaker 3")
        self.assertEqual(first, second)

    def test_speaker_smoothing_merges_short_flip_between_same_speakers(self):
        transcript = [
            {"start": "00:00.00", "end": "00:02.00", "text": "first part", "speaker": "Speaker 0"},
            {"start": "00:02.00", "end": "00:02.70", "text": "short flip", "speaker": "Speaker 1"},
            {"start": "00:02.70", "end": "00:05.00", "text": "same speaker returns", "speaker": "Speaker 0"},
        ]
        events, metadata = subtitler.build_subtitle_events_with_metadata(
            transcript,
            0.0,
            5.0,
            speaker_smoothing_window=1.0,
        )

        self.assertEqual(len(events), 3)
        self.assertEqual(events[1]["speaker"], "Speaker 0")
        self.assertEqual(metadata["speaker_flips_smoothed"], 1)
        self.assertTrue(metadata["speaker_smoothing_enabled"])
        self.assertEqual(metadata["speaker_color_map"]["Speaker 0"], subtitler.speaker_color_map(["Speaker 0"])["Speaker 0"])

    def test_long_real_speaker_change_is_not_merged(self):
        transcript = [
            {"start": "00:00.00", "end": "00:02.00", "text": "part one", "speaker": "Speaker 0"},
            {"start": "00:02.00", "end": "00:04.50", "text": "different speaker long turn", "speaker": "Speaker 1"},
            {"start": "00:04.50", "end": "00:06.00", "text": "speaker zero again", "speaker": "Speaker 0"},
        ]
        events, metadata = subtitler.build_subtitle_events_with_metadata(
            transcript,
            0.0,
            6.0,
            speaker_smoothing_window=1.0,
        )

        self.assertEqual(events[1]["speaker"], "Speaker 1")
        self.assertEqual(metadata["speaker_flips_smoothed"], 0)

    def test_missing_speaker_labels_still_render_with_default_style(self):
        transcript = [
            {"start": "00:00.00", "end": "00:02.00", "text": "no speaker label here"},
        ]
        events, metadata = subtitler.build_subtitle_events_with_metadata(
            transcript,
            0.0,
            2.0,
        )

        self.assertEqual(events[0]["speaker"], subtitler.DEFAULT_STYLE_NAME)
        self.assertTrue(metadata["speaker_smoothing_enabled"])
        self.assertEqual(metadata["detected_speaker_count"], 0)

    def test_single_speaker_commentary_merges_unstable_short_speakers(self):
        transcript = [
            {"start": "00:00.00", "end": "00:01.00", "text": "one", "speaker": "Speaker 0"},
            {"start": "00:01.00", "end": "00:01.50", "text": "two", "speaker": "Speaker 1"},
            {"start": "00:01.50", "end": "00:02.00", "text": "three", "speaker": "Speaker 2"},
            {"start": "00:02.00", "end": "00:02.50", "text": "four", "speaker": "Speaker 3"},
            {"start": "00:02.50", "end": "00:03.00", "text": "five", "speaker": "Speaker 4"},
            {"start": "00:03.00", "end": "00:03.50", "text": "six", "speaker": "Speaker 5"},
            {"start": "00:03.50", "end": "00:06.00", "text": "dominant", "speaker": "Speaker 0"},
        ]
        events, metadata = subtitler.build_subtitle_events_with_metadata(
            transcript,
            0.0,
            6.0,
            content_type_hint="commentary",
            expected_speaker_mode="single",
        )

        effective_speakers = {event["speaker"] for event in events if event["speaker"] != subtitler.DEFAULT_STYLE_NAME}
        self.assertLessEqual(len(effective_speakers), 2)
        self.assertTrue(metadata["merged_low_duration_speakers"])
        self.assertIn(metadata["speaker_stability_reason"], {"merged_low_duration_speakers", "within_effective_cap"})

    def test_podcast_keeps_real_alternating_speakers(self):
        transcript = [
            {"start": "00:00.00", "end": "00:02.00", "text": "host one", "speaker": "Speaker 0"},
            {"start": "00:02.00", "end": "00:04.00", "text": "host two", "speaker": "Speaker 1"},
            {"start": "00:04.00", "end": "00:06.00", "text": "host one again", "speaker": "Speaker 0"},
            {"start": "00:06.00", "end": "00:08.00", "text": "host two again", "speaker": "Speaker 1"},
        ]
        events, metadata = subtitler.build_subtitle_events_with_metadata(
            transcript,
            0.0,
            8.0,
            content_type_hint="podcast",
            expected_speaker_mode="multi",
        )

        effective_speakers = {event["speaker"] for event in events if event["speaker"] != subtitler.DEFAULT_STYLE_NAME}
        self.assertEqual(effective_speakers, {"Speaker 0", "Speaker 1"})
        self.assertEqual(metadata["merged_low_duration_speakers"], [])

    def test_local_subtitle_correction_preserves_timestamps_and_segment_count(self):
        transcript = [
            {"start": "00:00.00", "end": "00:02.00", "text": "to  jest test ,napisow", "speaker": "Speaker 0"},
            {"start": "00:02.00", "end": "00:04.00", "text": "druga linia", "speaker": "Speaker 0"},
        ]
        events, metadata = subtitler.build_subtitle_events_with_metadata(
            transcript,
            0.0,
            4.0,
            subtitle_correction_mode="local_only",
        )

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["start"], 0.0)
        self.assertEqual(events[0]["end"], 2.0)
        self.assertEqual(events[0]["text"], "To jest test, napisow")
        self.assertTrue(metadata["subtitles_corrected"])
        self.assertEqual(metadata["corrected_segments_count"], 2)

    def test_subtitle_correction_off_leaves_text_unchanged(self):
        transcript = [
            {"start": "00:00.00", "end": "00:02.00", "text": "to  jest test ,napisow", "speaker": "Speaker 0"},
        ]
        events, metadata = subtitler.build_subtitle_events_with_metadata(
            transcript,
            0.0,
            2.0,
            subtitle_correction_mode="off",
        )

        self.assertEqual(events[0]["text"], "to  jest test ,napisow")
        self.assertFalse(metadata["subtitles_corrected"])

    @patch("semantic_clip_director.generate_text_with_transport", return_value="not-json")
    def test_invalid_api_subtitle_correction_falls_back(self, _mock_generate):
        transcript = [
            {"start": "00:00.00", "end": "00:02.00", "text": "to  jest test ,napisow", "speaker": "Speaker 0"},
        ]
        events, metadata = subtitler.build_subtitle_events_with_metadata(
            transcript,
            0.0,
            2.0,
            subtitle_correction_mode="gemini_optional",
            semantic_model="models/gemini-2.5-flash",
            api_key="test-key",
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["text"], "To jest test, napisow")
        self.assertIn("expecting value", metadata["correction_fallback_reason"].lower())


if __name__ == "__main__":
    unittest.main()
