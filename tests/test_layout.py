import unittest

from layout import get_layout_profile, is_vertical_9_16
from strategies import get_strategy


class LayoutProfileTests(unittest.TestCase):
    def test_tutorial_uses_full_frame_blur_background(self):
        profile = get_layout_profile("tutorial")
        self.assertEqual(profile.layout_mode, "full_frame_blur_background")
        self.assertEqual(profile.layout_policy, "screen_preserve_blur_bg")
        self.assertTrue(profile.preserve_full_frame)
        self.assertTrue(profile.blur_background)
        self.assertFalse(profile.allow_face_tracking)
        self.assertEqual((profile.output_width, profile.output_height), (1080, 1920))
        self.assertEqual(profile.output_aspect_ratio, "9:16")

    def test_gameplay_uses_gameplay_priority_crop(self):
        profile = get_layout_profile("gameplay")
        self.assertEqual(profile.layout_mode, "gameplay_priority_crop")
        self.assertEqual(profile.layout_policy, "gameplay_safe_vertical")
        self.assertEqual(profile.crop_priority, "gameplay")
        self.assertTrue(profile.allow_face_tracking)
        self.assertTrue(profile.ignore_edge_faces)
        self.assertGreaterEqual(profile.min_face_area_for_tracking, 0.06)

    def test_podcast_uses_speaker_face_crop(self):
        profile = get_layout_profile("podcast")
        self.assertEqual(profile.layout_mode, "speaker_face_crop")
        self.assertEqual(profile.layout_policy, "face_active_speaker")
        self.assertEqual(profile.crop_priority, "speaker_face")
        self.assertTrue(profile.allow_face_tracking)
        self.assertGreater(profile.face_tracking_weight, 0.9)

    def test_commentary_uses_stable_subject_crop(self):
        profile = get_layout_profile("commentary")
        self.assertEqual(profile.layout_mode, "stable_subject_crop")
        self.assertEqual(profile.layout_policy, "stable_subject_or_center")
        self.assertEqual(profile.crop_priority, "subject")
        self.assertTrue(profile.allow_face_tracking)
        self.assertTrue(profile.safe_center_crop)

    def test_generic_uses_safe_center_crop(self):
        profile = get_layout_profile("generic")
        self.assertEqual(profile.layout_mode, "safe_center_crop")
        self.assertEqual(profile.layout_policy, "safe_center_crop")
        self.assertFalse(profile.allow_face_tracking)
        self.assertTrue(profile.safe_center_crop)

    def test_override_mode_wins_over_content_type(self):
        profile = get_layout_profile("tutorial", "safe_center_crop")
        self.assertEqual(profile.layout_mode, "safe_center_crop")
        self.assertEqual(profile.content_type, "tutorial")

    def test_strategy_payload_includes_layout_and_vertical_output(self):
        strategy = get_strategy("tutorial")
        payload = strategy.to_dict()
        self.assertEqual(payload["layout"]["layout_mode"], "full_frame_blur_background")
        self.assertEqual(payload["render_hints"]["output_aspect_ratio"], "9:16")
        self.assertTrue(payload["render_hints"]["preserve_full_frame"])

    def test_is_vertical_9_16(self):
        self.assertTrue(is_vertical_9_16(1080, 1920))
        self.assertFalse(is_vertical_9_16(1920, 1080))


if __name__ == "__main__":
    unittest.main()
