import unittest

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
        events = subtitler.build_subtitle_events(
            transcript,
            0.0,
            5.0,
            speaker_smoothing_window=1.0,
        )

        self.assertEqual(len(events), 3)
        self.assertEqual(events[1]["speaker"], "Speaker 0")


if __name__ == "__main__":
    unittest.main()
