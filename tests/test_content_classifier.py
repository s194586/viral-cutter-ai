import unittest

from content_classifier import classify_from_features


REAL_CASE_FIXTURES = {
    "ukraine_commentary": {
        "speech_coverage_ratio": 0.8538,
        "avg_segment_duration": 1.6975,
        "short_segment_ratio": 0.2716,
        "long_segment_ratio": 0.0275,
        "question_ratio": 0.0190,
        "qa_turn_ratio": 0.0038,
        "avg_words_per_second": 2.7682,
        "speaker_count": 4,
        "speaker_switch_rate_per_minute": 19.6047,
        "dominant_speaker_ratio": 0.3514,
        "emotion_segment_ratio": 0.0,
        "gameplay_keyword_ratio": 0.0,
        "tutorial_keyword_ratio": 0.0020,
        "podcast_keyword_ratio": 0.0006,
        "commentary_keyword_ratio": 0.0053,
        "instruction_segment_ratio": 0.0199,
        "direct_address_ratio": 0.0104,
        "commentary_segment_ratio": 0.0237,
        "motion_score": 0.4797,
        "scene_change_rate": 0.2059,
        "face_presence_ratio": 0.75,
        "face_stability": 0.9542,
        "face_overlay_ratio": 0.0,
        "face_large_ratio": 0.0,
        "heatmap_volatility": 0.0,
        "heatmap_high_energy_ratio": 0.0,
    },
    "roman_commentary": {
        "speech_coverage_ratio": 0.9213,
        "avg_segment_duration": 2.8151,
        "short_segment_ratio": 0.0228,
        "long_segment_ratio": 0.2255,
        "question_ratio": 0.0114,
        "qa_turn_ratio": 0.0068,
        "avg_words_per_second": 2.7811,
        "speaker_count": 4,
        "speaker_switch_rate_per_minute": 12.8822,
        "dominant_speaker_ratio": 0.2825,
        "emotion_segment_ratio": 0.0,
        "gameplay_keyword_ratio": 0.0,
        "tutorial_keyword_ratio": 0.0023,
        "podcast_keyword_ratio": 0.0015,
        "commentary_keyword_ratio": 0.0052,
        "instruction_segment_ratio": 0.0182,
        "direct_address_ratio": 0.0023,
        "commentary_segment_ratio": 0.0387,
        "motion_score": 1.0,
        "scene_change_rate": 0.9118,
        "face_presence_ratio": 0.4167,
        "face_stability": 0.7745,
        "face_overlay_ratio": 0.6,
        "face_large_ratio": 0.0,
        "heatmap_volatility": 0.0,
        "heatmap_high_energy_ratio": 0.0,
    },
    "podcast": {
        "speech_coverage_ratio": 0.8471,
        "avg_segment_duration": 1.8537,
        "short_segment_ratio": 0.25,
        "long_segment_ratio": 0.0412,
        "question_ratio": 0.0593,
        "qa_turn_ratio": 0.0206,
        "avg_words_per_second": 2.8127,
        "speaker_count": 4,
        "speaker_switch_rate_per_minute": 13.4968,
        "dominant_speaker_ratio": 0.3557,
        "emotion_segment_ratio": 0.0,
        "gameplay_keyword_ratio": 0.0005,
        "tutorial_keyword_ratio": 0.0020,
        "podcast_keyword_ratio": 0.0054,
        "commentary_keyword_ratio": 0.0,
        "instruction_segment_ratio": 0.0284,
        "direct_address_ratio": 0.0284,
        "commentary_segment_ratio": 0.0,
        "motion_score": 0.6193,
        "scene_change_rate": 0.4118,
        "face_presence_ratio": 0.25,
        "face_stability": 0.9703,
        "face_overlay_ratio": 1.0,
        "face_large_ratio": 0.0,
        "heatmap_volatility": 0.0,
        "heatmap_high_energy_ratio": 0.0,
    },
    "tutorial": {
        "speech_coverage_ratio": 0.9380,
        "avg_segment_duration": 1.9865,
        "short_segment_ratio": 0.1186,
        "long_segment_ratio": 0.0424,
        "question_ratio": 0.0048,
        "qa_turn_ratio": 0.0,
        "avg_words_per_second": 2.3359,
        "speaker_count": 4,
        "speaker_switch_rate_per_minute": 17.9724,
        "dominant_speaker_ratio": 0.2724,
        "emotion_segment_ratio": 0.0,
        "gameplay_keyword_ratio": 0.0,
        "tutorial_keyword_ratio": 0.0310,
        "podcast_keyword_ratio": 0.0003,
        "commentary_keyword_ratio": 0.0003,
        "instruction_segment_ratio": 0.1937,
        "direct_address_ratio": 0.0460,
        "commentary_segment_ratio": 0.0012,
        "motion_score": 0.7937,
        "scene_change_rate": 0.3824,
        "face_presence_ratio": 0.0833,
        "face_stability": 0.0,
        "face_overlay_ratio": 0.0,
        "face_large_ratio": 1.0,
        "heatmap_volatility": 0.1077,
        "heatmap_high_energy_ratio": 0.05,
    },
}


class ContentClassifierTests(unittest.TestCase):
    def test_podcast_like_features_route_to_podcast(self):
        result = classify_from_features(
            {
                "speech_coverage_ratio": 0.88,
                "avg_segment_duration": 2.8,
                "long_segment_ratio": 0.36,
                "speaker_count": 2,
                "speaker_switch_rate_per_minute": 4.2,
                "dominant_speaker_ratio": 0.58,
                "motion_score": 0.08,
                "scene_change_rate": 0.03,
                "face_presence_ratio": 0.82,
                "face_stability": 0.78,
                "gameplay_keyword_ratio": 0.0,
                "tutorial_keyword_ratio": 0.0,
                "podcast_keyword_ratio": 0.01,
                "commentary_keyword_ratio": 0.0,
                "instruction_segment_ratio": 0.0,
                "direct_address_ratio": 0.03,
                "commentary_segment_ratio": 0.0,
                "qa_turn_ratio": 0.06,
                "question_ratio": 0.08,
                "emotion_segment_ratio": 0.11,
                "short_segment_ratio": 0.08,
                "heatmap_volatility": 0.04,
                "heatmap_high_energy_ratio": 0.05,
                "avg_words_per_second": 2.9,
            }
        )
        self.assertEqual(result.content_type, "podcast")

    def test_gameplay_like_features_route_to_gameplay(self):
        result = classify_from_features(
            {
                "speech_coverage_ratio": 0.73,
                "avg_segment_duration": 1.1,
                "speaker_count": 4,
                "speaker_switch_rate_per_minute": 10.5,
                "dominant_speaker_ratio": 0.34,
                "motion_score": 0.74,
                "scene_change_rate": 0.31,
                "face_presence_ratio": 0.28,
                "face_stability": 0.24,
                "face_overlay_ratio": 0.55,
                "gameplay_keyword_ratio": 0.026,
                "tutorial_keyword_ratio": 0.001,
                "commentary_keyword_ratio": 0.0,
                "instruction_segment_ratio": 0.01,
                "direct_address_ratio": 0.01,
                "commentary_segment_ratio": 0.0,
                "qa_turn_ratio": 0.01,
                "question_ratio": 0.02,
                "emotion_segment_ratio": 0.39,
                "short_segment_ratio": 0.48,
                "chaos_ratio": 0.22,
                "heatmap_volatility": 0.16,
                "heatmap_high_energy_ratio": 0.22,
            }
        )
        self.assertEqual(result.content_type, "gameplay")

    def test_tutorial_like_features_route_to_tutorial(self):
        result = classify_from_features(
            {
                "speech_coverage_ratio": 0.91,
                "avg_segment_duration": 2.4,
                "speaker_count": 1,
                "speaker_switch_rate_per_minute": 0.0,
                "dominant_speaker_ratio": 1.0,
                "motion_score": 0.14,
                "scene_change_rate": 0.05,
                "face_presence_ratio": 0.12,
                "face_large_ratio": 0.08,
                "gameplay_keyword_ratio": 0.001,
                "tutorial_keyword_ratio": 0.024,
                "podcast_keyword_ratio": 0.0,
                "commentary_keyword_ratio": 0.0,
                "instruction_segment_ratio": 0.14,
                "direct_address_ratio": 0.05,
                "commentary_segment_ratio": 0.0,
                "qa_turn_ratio": 0.0,
                "question_ratio": 0.01,
                "emotion_segment_ratio": 0.07,
                "short_segment_ratio": 0.10,
                "avg_words_per_second": 2.5,
                "heatmap_volatility": 0.05,
                "heatmap_high_energy_ratio": 0.04,
            }
        )
        self.assertEqual(result.content_type, "tutorial")

    def test_commentary_like_features_route_to_commentary(self):
        result = classify_from_features(
            {
                "speech_coverage_ratio": 0.93,
                "avg_segment_duration": 2.9,
                "speaker_count": 1,
                "speaker_switch_rate_per_minute": 0.2,
                "dominant_speaker_ratio": 0.96,
                "motion_score": 0.46,
                "scene_change_rate": 0.18,
                "face_presence_ratio": 0.62,
                "face_stability": 0.88,
                "gameplay_keyword_ratio": 0.0,
                "tutorial_keyword_ratio": 0.002,
                "podcast_keyword_ratio": 0.001,
                "commentary_keyword_ratio": 0.006,
                "instruction_segment_ratio": 0.02,
                "direct_address_ratio": 0.005,
                "commentary_segment_ratio": 0.06,
                "qa_turn_ratio": 0.0,
                "question_ratio": 0.01,
                "emotion_segment_ratio": 0.08,
                "short_segment_ratio": 0.05,
                "long_segment_ratio": 0.28,
                "avg_words_per_second": 2.8,
                "heatmap_volatility": 0.03,
                "heatmap_high_energy_ratio": 0.04,
            }
        )
        self.assertEqual(result.content_type, "commentary")

    def test_real_commentary_profiles_do_not_regress_to_podcast(self):
        for key in ("ukraine_commentary", "roman_commentary"):
            with self.subTest(case=key):
                result = classify_from_features(REAL_CASE_FIXTURES[key])
                self.assertEqual(result.content_type, "commentary")
                self.assertGreater(result.scores["commentary"], result.scores["podcast"])

    def test_real_podcast_profile_routes_to_podcast(self):
        result = classify_from_features(REAL_CASE_FIXTURES["podcast"])
        self.assertEqual(result.content_type, "podcast")
        self.assertGreater(result.scores["podcast"], result.scores["commentary"])

    def test_real_tutorial_profile_routes_to_tutorial(self):
        result = classify_from_features(REAL_CASE_FIXTURES["tutorial"])
        self.assertEqual(result.content_type, "tutorial")
        self.assertGreater(result.scores["tutorial"], result.scores["generic"])

    def test_ambiguous_features_fall_back_to_generic(self):
        result = classify_from_features(
            {
                "speech_coverage_ratio": 0.48,
                "avg_segment_duration": 1.5,
                "speaker_count": 1,
                "speaker_switch_rate_per_minute": 0.6,
                "dominant_speaker_ratio": 0.96,
                "motion_score": 0.24,
                "scene_change_rate": 0.08,
                "face_presence_ratio": 0.18,
                "gameplay_keyword_ratio": 0.002,
                "tutorial_keyword_ratio": 0.002,
                "podcast_keyword_ratio": 0.0,
                "commentary_keyword_ratio": 0.0,
                "instruction_segment_ratio": 0.01,
                "direct_address_ratio": 0.01,
                "commentary_segment_ratio": 0.0,
                "qa_turn_ratio": 0.0,
                "question_ratio": 0.0,
                "emotion_segment_ratio": 0.14,
                "short_segment_ratio": 0.2,
                "heatmap_volatility": 0.06,
                "heatmap_high_energy_ratio": 0.07,
            }
        )
        self.assertEqual(result.content_type, "generic")


if __name__ == "__main__":
    unittest.main()
