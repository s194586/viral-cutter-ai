#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_RESULTS_PATH = PROJECT_ROOT / "benchmarks" / "results.json"
DEFAULT_TEMPLATE_PATH = PROJECT_ROOT / "benchmarks" / "human_review_template.csv"
DEFAULT_REVIEWS_PATH = PROJECT_ROOT / "benchmarks" / "human_reviews.jsonl"
DEFAULT_HTML_PATH = PROJECT_ROOT / "benchmarks" / "review_dashboard.html"
CLIP_ID_RE = re.compile(r"[^a-zA-Z0-9_.-]+")
REVIEW_FIELDS = (
    "rating",
    "good_clip",
    "boundary_issue",
    "boring_setup",
    "no_payoff",
    "too_context_dependent",
    "notes",
)


@dataclass
class ReviewClip:
    clip_id: str
    case_id: str
    scenario_id: str
    content_type: str = ""
    expected_content_type: str = ""
    clip_index: int | str = ""
    start: float | None = None
    end: float | None = None
    start_label: str = ""
    end_label: str = ""
    duration: float | None = None
    local_score: float | str | None = None
    final_score: float | str | None = None
    selection_reasons: list[str] = field(default_factory=list)
    local_features: dict[str, Any] = field(default_factory=dict)
    transcript_excerpt: str = ""
    video_path: str = ""
    human_template: dict[str, str] = field(default_factory=dict)
    latest_review: dict[str, Any] | None = None
    review_count: int = 0


def load_json(path: Path, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except Exception:
        return default


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value or "").strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off", ""}:
        return False
    raise argparse.ArgumentTypeError(f"Expected true/false, got: {value}")


def format_time_value(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, str) and ":" in value:
        return value.strip()
    try:
        seconds = max(0.0, float(value))
    except Exception:
        return str(value)
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


def normalize_project_path(path_text: str) -> str:
    return str(path_text or "").replace("\\", "/")


def stable_clip_id(case_id: str, scenario_id: str, start: Any, end: Any) -> str:
    start_label = format_time_value(start)
    end_label = format_time_value(end)
    base = f"{case_id}|{scenario_id}|{start_label}|{end_label}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    prefix = CLIP_ID_RE.sub("-", f"{case_id}-{scenario_id}").strip("-").lower()
    return f"{prefix}-{digest}" if prefix else digest


def review_key_from_row(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("case_id", "") or "").strip(),
        str(row.get("scenario_id", "") or "").strip(),
        str(row.get("clip_start", "") or "").strip(),
        str(row.get("clip_end", "") or "").strip(),
    )


def load_human_review_template(path: Path = DEFAULT_TEMPLATE_PATH) -> dict[tuple[str, str, str, str], dict[str, str]]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8", newline="") as file_handle:
        rows = list(csv.DictReader(file_handle))
    return {review_key_from_row(row): row for row in rows}


def load_jsonl_reviews(path: Path = DEFAULT_REVIEWS_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    reviews = []
    with open(path, "r", encoding="utf-8") as file_handle:
        for line in file_handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                reviews.append(payload)
    return reviews


def summarize_reviews_by_clip(reviews: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for review in reviews:
        clip_id = str(review.get("clip_id", "") or "").strip()
        if not clip_id:
            continue
        current = grouped.setdefault(clip_id, {"count": 0, "latest": None})
        current["count"] += 1
        current["latest"] = review
    return grouped


def _clip_video_path(
    clip: dict[str, Any],
    scenario: dict[str, Any],
    template_row: dict[str, str] | None,
) -> str:
    if template_row and template_row.get("clip_file"):
        return normalize_project_path(str(template_row.get("clip_file") or ""))
    subtitle_dir = normalize_project_path(((scenario.get("artifacts") or {}).get("subtitle_dir") or "").strip())
    clip_index = int(clip.get("index") or 0)
    if not subtitle_dir or not clip_index:
        return ""
    pattern = f"segment_{clip_index}_*.mp4"
    matches = sorted((PROJECT_ROOT / subtitle_dir).glob(pattern))
    if matches:
        try:
            return str(matches[0].relative_to(PROJECT_ROOT))
        except ValueError:
            return str(matches[0])
    return ""


def _extract_clip_text(clip: dict[str, Any]) -> str:
    for key in ("summary", "text", "transcript_excerpt"):
        value = str(clip.get(key, "") or "").strip()
        if value:
            return value
    return ""


def collect_clips(
    results_path: Path = DEFAULT_RESULTS_PATH,
    template_path: Path = DEFAULT_TEMPLATE_PATH,
    reviews_path: Path = DEFAULT_REVIEWS_PATH,
) -> list[ReviewClip]:
    results = load_json(results_path, default={}) or {}
    template_lookup = load_human_review_template(template_path)
    reviews_by_clip = summarize_reviews_by_clip(load_jsonl_reviews(reviews_path))
    clips: list[ReviewClip] = []

    case_payloads = results.get("cases", []) if isinstance(results, dict) else []
    for case in case_payloads:
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("case_id", "") or "").strip()
        expected_type = str(case.get("expected_content_type", "") or "").strip()
        for scenario in case.get("scenarios", []) or []:
            if not isinstance(scenario, dict) or scenario.get("status") != "completed":
                continue
            scenario_id = str(scenario.get("scenario_id", "") or "").strip()
            classification = scenario.get("classification") or {}
            content_type = str(
                classification.get("detected_content_type")
                or scenario.get("content_type_arg")
                or expected_type
                or ""
            )
            for clip in (scenario.get("selection") or {}).get("clips", []) or []:
                if not isinstance(clip, dict):
                    continue
                start_label = str(clip.get("start_label") or format_time_value(clip.get("start")))
                end_label = str(clip.get("end_label") or format_time_value(clip.get("end")))
                clip_id = stable_clip_id(case_id, scenario_id, start_label, end_label)
                template_row = template_lookup.get((case_id, scenario_id, start_label, end_label))
                review_summary = reviews_by_clip.get(clip_id) or {"count": 0, "latest": None}
                clips.append(
                    ReviewClip(
                        clip_id=clip_id,
                        case_id=case_id,
                        scenario_id=scenario_id,
                        content_type=content_type,
                        expected_content_type=expected_type,
                        clip_index=clip.get("index", ""),
                        start=clip.get("start"),
                        end=clip.get("end"),
                        start_label=start_label,
                        end_label=end_label,
                        duration=clip.get("duration"),
                        local_score=clip.get("local_score"),
                        final_score=clip.get("final_score") or clip.get("local_score"),
                        selection_reasons=[str(item) for item in clip.get("selection_reasons", [])],
                        local_features=clip.get("local_features") or {},
                        transcript_excerpt=_extract_clip_text(clip),
                        video_path=_clip_video_path(clip, scenario, template_row),
                        human_template=template_row or {},
                        latest_review=review_summary.get("latest"),
                        review_count=int(review_summary.get("count") or 0),
                    )
                )
    return clips


def append_review(path: Path, review: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(review, ensure_ascii=False, sort_keys=True) + "\n")


def build_review_payload(args: argparse.Namespace) -> dict[str, Any]:
    if not 1 <= int(args.rating) <= 5:
        raise ValueError("rating must be between 1 and 5")
    payload = {
        "clip_id": args.clip_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rating": int(args.rating),
        "good_clip": bool(args.good_clip),
        "boundary_issue": bool(args.boundary_issue),
        "boring_setup": bool(args.boring_setup),
        "no_payoff": bool(args.no_payoff),
        "too_context_dependent": bool(args.too_context_dependent),
        "notes": str(args.notes or ""),
    }
    return payload


def _penalty_summary(features: dict[str, Any]) -> dict[str, Any]:
    wanted = (
        "ad_like_penalty",
        "gameplay_setup_penalty",
        "low_payoff_penalty",
        "contextless_penalty",
        "preamble_penalty",
        "repetition_penalty",
        "payoff_score",
        "gameplay_action_score",
        "tutorial_instruction_score",
        "commentary_complete_thought_score",
        "podcast_dialogue_payoff_score",
    )
    return {key: features[key] for key in wanted if key in features}


def print_clip_list(clips: list[ReviewClip], *, limit: int | None = None) -> None:
    shown = clips[:limit] if limit else clips
    for clip in shown:
        status = "reviewed" if clip.latest_review else "unreviewed"
        score = clip.final_score if clip.final_score is not None else ""
        print(
            f"{clip.clip_id}\t{status}\t{clip.case_id}/{clip.scenario_id}\t"
            f"{clip.start_label}-{clip.end_label}\tscore={score}\tvideo={clip.video_path or '-'}"
        )
    print(f"clips_shown={len(shown)} total_clips={len(clips)}")


def _html_path(path_text: str, output_path: Path) -> str:
    if not path_text:
        return ""
    path = Path(normalize_project_path(path_text))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    try:
        return html.escape(str(path.relative_to(output_path.parent)))
    except ValueError:
        return html.escape(str(path))


def render_html(clips: list[ReviewClip], output_path: Path) -> str:
    rows = []
    for clip in clips:
        latest = clip.latest_review or {}
        penalties = _penalty_summary(clip.local_features)
        video_src = _html_path(clip.video_path, output_path)
        video_html = (
            f'<video controls preload="metadata" src="{video_src}"></video>'
            if video_src
            else '<div class="missing">No video file path</div>'
        )
        rows.append(
            f"""
            <article class="clip">
              <div class="meta">
                <code>{html.escape(clip.clip_id)}</code>
                <span>{html.escape(clip.case_id)} / {html.escape(clip.scenario_id)}</span>
                <span>{html.escape(clip.start_label)} - {html.escape(clip.end_label)}</span>
                <span>score: {html.escape(str(clip.final_score or ""))}</span>
                <span class="status">{'reviewed' if clip.latest_review else 'unreviewed'}</span>
              </div>
              {video_html}
              <p>{html.escape(clip.transcript_excerpt or '')}</p>
              <dl>
                <dt>Reasons</dt><dd>{html.escape(', '.join(clip.selection_reasons) or '-')}</dd>
                <dt>Features</dt><dd><pre>{html.escape(json.dumps(penalties, ensure_ascii=False, indent=2))}</pre></dd>
                <dt>Video path</dt><dd>{html.escape(clip.video_path or '-')}</dd>
                <dt>Latest review</dt><dd><pre>{html.escape(json.dumps(latest, ensure_ascii=False, indent=2))}</pre></dd>
              </dl>
            </article>
            """
        )
    body = "\n".join(rows)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Virtual Cutter Review Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; background: #f6f7f9; color: #1f2933; }}
    header {{ max-width: 1100px; margin: 0 auto 20px; }}
    .clip {{ max-width: 1100px; margin: 0 auto 16px; padding: 16px; background: white; border: 1px solid #d8dee8; border-radius: 8px; }}
    .meta {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 12px; }}
    .meta span, code {{ background: #eef2f7; padding: 3px 6px; border-radius: 4px; }}
    .status {{ font-weight: 700; }}
    video {{ width: min(260px, 100%); max-height: 460px; display: block; margin: 8px 0 12px; background: #111827; }}
    dt {{ font-weight: 700; margin-top: 8px; }}
    dd {{ margin-left: 0; }}
    pre {{ white-space: pre-wrap; background: #f3f4f6; padding: 8px; border-radius: 6px; overflow-x: auto; }}
    .missing {{ color: #7b8794; margin: 8px 0 12px; }}
  </style>
</head>
<body>
  <header>
    <h1>AI Virtual Cutter Review Dashboard</h1>
    <p>Use <code>python review_dashboard.py add-review --clip-id CLIP_ID --rating 4 --good-clip true --notes "..."</code> to append feedback to <code>benchmarks/human_reviews.jsonl</code>.</p>
  </header>
  {body}
</body>
</html>
"""


def export_html(args: argparse.Namespace) -> None:
    clips = collect_clips(Path(args.results), Path(args.template), Path(args.reviews))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(clips, output_path), encoding="utf-8")
    print(f"exported_html={output_path} clips={len(clips)}")


def list_clips(args: argparse.Namespace) -> None:
    clips = collect_clips(Path(args.results), Path(args.template), Path(args.reviews))
    print_clip_list(clips, limit=args.limit)


def add_review(args: argparse.Namespace) -> None:
    payload = build_review_payload(args)
    append_review(Path(args.reviews), payload)
    print(f"review_saved clip_id={payload['clip_id']} path={args.reviews}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local human-review dashboard for AI Virtual Cutter clips.")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List clips discovered from benchmark results.")
    list_parser.add_argument("--results", default=str(DEFAULT_RESULTS_PATH))
    list_parser.add_argument("--template", default=str(DEFAULT_TEMPLATE_PATH))
    list_parser.add_argument("--reviews", default=str(DEFAULT_REVIEWS_PATH))
    list_parser.add_argument("--limit", type=int, default=50)
    list_parser.set_defaults(func=list_clips)

    export_parser = subparsers.add_parser("export-html", help="Export a standalone HTML review dashboard.")
    export_parser.add_argument("--results", default=str(DEFAULT_RESULTS_PATH))
    export_parser.add_argument("--template", default=str(DEFAULT_TEMPLATE_PATH))
    export_parser.add_argument("--reviews", default=str(DEFAULT_REVIEWS_PATH))
    export_parser.add_argument("--output", default=str(DEFAULT_HTML_PATH))
    export_parser.set_defaults(func=export_html)

    review_parser = subparsers.add_parser("add-review", help="Append one human review row to JSONL.")
    review_parser.add_argument("--clip-id", required=True)
    review_parser.add_argument("--reviews", default=str(DEFAULT_REVIEWS_PATH))
    review_parser.add_argument("--rating", required=True, type=int, choices=range(1, 6))
    review_parser.add_argument("--good-clip", type=parse_bool, default=False)
    review_parser.add_argument("--boundary-issue", type=parse_bool, default=False)
    review_parser.add_argument("--boring-setup", type=parse_bool, default=False)
    review_parser.add_argument("--no-payoff", type=parse_bool, default=False)
    review_parser.add_argument("--too-context-dependent", type=parse_bool, default=False)
    review_parser.add_argument("--notes", default="")
    review_parser.set_defaults(func=add_review)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
