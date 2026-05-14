import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import review_dashboard


class ReviewDashboardTests(unittest.TestCase):
    def _sample_results(self, path: Path) -> None:
        payload = {
            "cases": [
                {
                    "case_id": "case_a",
                    "expected_content_type": "gameplay",
                    "scenarios": [
                        {
                            "scenario_id": "auto",
                            "status": "completed",
                            "content_type_arg": "auto",
                            "classification": {"detected_content_type": "gameplay"},
                            "artifacts": {"subtitle_dir": "benchmarks/runs/test/case_a/auto/cuts_subtitles"},
                            "selection": {
                                "clips": [
                                    {
                                        "index": 1,
                                        "start": 10.0,
                                        "end": 40.0,
                                        "start_label": "00:10.00",
                                        "end_label": "00:40.00",
                                        "duration": 30.0,
                                        "local_score": 91.2,
                                        "selection_reasons": ["strong heatmap support"],
                                        "local_features": {"low_payoff_penalty": 0.2},
                                        "summary": "short transcript excerpt",
                                    }
                                ]
                            },
                        }
                    ],
                }
            ]
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    def _sample_template(self, path: Path) -> None:
        path.write_text(
            "\n".join(
                [
                    "case_id,scenario_id,clip_start,clip_end,clip_file,human_relevance_score,human_boundary_score,human_crop_score,notes",
                    r"case_a,auto,00:10.00,00:40.00,benchmarks\runs\test\case_a\auto\cuts_subtitles\segment_1.mp4,,,,",
                ]
            ),
            encoding="utf-8",
        )

    def test_stable_clip_id_is_deterministic(self):
        left = review_dashboard.stable_clip_id("case_a", "auto", "00:10.00", "00:40.00")
        right = review_dashboard.stable_clip_id("case_a", "auto", 10.0, 40.0)
        self.assertEqual(left, right)
        self.assertIn("case_a-auto", left)

    def test_collect_clips_handles_missing_optional_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            results = base / "results.json"
            template = base / "template.csv"
            reviews = base / "reviews.jsonl"
            self._sample_results(results)
            self._sample_template(template)

            clips = review_dashboard.collect_clips(results, template, reviews)

        self.assertEqual(len(clips), 1)
        self.assertEqual(clips[0].case_id, "case_a")
        self.assertEqual(clips[0].video_path, "benchmarks/runs/test/case_a/auto/cuts_subtitles/segment_1.mp4")
        self.assertEqual(clips[0].local_features["low_payoff_penalty"], 0.2)

    def test_write_and_read_jsonl_reviews(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "reviews.jsonl"
            review_dashboard.append_review(
                path,
                {
                    "clip_id": "clip_a",
                    "rating": 4,
                    "good_clip": True,
                    "boundary_issue": False,
                    "boring_setup": False,
                    "no_payoff": False,
                    "too_context_dependent": False,
                    "notes": "good",
                },
            )
            reviews = review_dashboard.load_jsonl_reviews(path)

        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]["clip_id"], "clip_a")
        self.assertEqual(reviews[0]["rating"], 4)

    def test_export_html_without_crash(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            results = base / "results.json"
            template = base / "template.csv"
            reviews = base / "reviews.jsonl"
            output = base / "dashboard.html"
            self._sample_results(results)
            self._sample_template(template)

            clips = review_dashboard.collect_clips(results, template, reviews)
            output.write_text(review_dashboard.render_html(clips, output), encoding="utf-8")

            html = output.read_text(encoding="utf-8")
        self.assertIn("AI Virtual Cutter Review Dashboard", html)
        self.assertIn("case_a / auto", html)

    def test_cli_help(self):
        completed = subprocess.run(
            [sys.executable, "review_dashboard.py", "--help"],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("Local human-review dashboard", completed.stdout)


if __name__ == "__main__":
    unittest.main()
