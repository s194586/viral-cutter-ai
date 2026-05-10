import argparse
import json
import re
import subprocess
from pathlib import Path

MAX_SHORT_DURATION = 60.0
WORD_RE = re.compile(
    r"[0-9A-Za-zÀ-žąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+(?:['’-][0-9A-Za-zÀ-žąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+)*",
    re.UNICODE,
)


def parse_time(value):
    if isinstance(value, (int, float)):
        return float(value)
    parts = [part for part in str(value).strip().replace(",", ".").split(":") if part]
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    raise ValueError(f"Invalid timestamp format: {value}")


def file_has_audio(path):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a",
        "-show_entries",
        "stream=index",
        "-of",
        "csv=p=0",
        str(path),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    return bool(completed.stdout.strip())


def file_has_video(path):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v",
        "-show_entries",
        "stream=index",
        "-of",
        "csv=p=0",
        str(path),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    return bool(completed.stdout.strip())


def load_windows(windows_file):
    with open(windows_file, "r", encoding="utf-8") as file_handle:
        windows = json.load(file_handle)
    if not isinstance(windows, list):
        raise ValueError("Windows file must contain a JSON list.")
    return windows


def extract_word_timestamps(segment):
    words = []
    raw_words = segment.get("words")
    if isinstance(raw_words, list):
        for item in raw_words:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or item.get("word") or "").strip()
            if not text:
                continue
            try:
                start = parse_time(item["start"])
                end = parse_time(item["end"])
            except Exception:
                continue
            if end <= start:
                continue
            words.append({"text": text, "start": start, "end": end, "source": "transcript"})
    return words


def approximate_word_timestamps(segment):
    text = str(segment.get("text", "")).strip()
    if not text:
        return []

    start = parse_time(segment["start"])
    end = parse_time(segment["end"])
    duration = end - start
    if duration <= 0:
        return []

    matches = list(WORD_RE.finditer(text))
    if not matches:
        return []

    total_units = sum(max(1, len(match.group(0))) for match in matches)
    cursor = start
    words = []
    consumed_units = 0

    for index, match in enumerate(matches):
        token = match.group(0)
        token_units = max(1, len(token))
        if index == len(matches) - 1:
            word_end = end
        else:
            consumed_units += token_units
            portion = consumed_units / total_units
            word_end = start + duration * portion
        words.append({"text": token, "start": cursor, "end": word_end, "source": "estimated"})
        cursor = word_end

    return words


def load_transcript(transcript_file):
    path = Path(transcript_file)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    if isinstance(data, dict) and "segments" in data:
        data = data["segments"]
    if not isinstance(data, list):
        return []

    segments = []
    for item in data:
        try:
            start = parse_time(item["start"])
            end = parse_time(item["end"])
        except Exception:
            continue
        if end <= start:
            continue

        text = str(item.get("text", "")).strip()
        words = extract_word_timestamps(item)
        if not words:
            words = approximate_word_timestamps(item)

        segments.append({"start": start, "end": end, "text": text, "words": words})

    return sorted(segments, key=lambda item: item["start"])


def load_cutting_log(log_path):
    path = Path(log_path)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def save_cutting_log(log_path, log):
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(log, file_handle, ensure_ascii=False, indent=2)


def upsert_cutter_adjustment(log, entry):
    adjustments = log.setdefault("cutter_adjustments", [])
    adjustments = [item for item in adjustments if item.get("segment_index") != entry.get("segment_index")]
    adjustments.append(entry)
    adjustments.sort(key=lambda item: item.get("segment_index", 0))
    log["cutter_adjustments"] = adjustments


def flatten_words(segments):
    words = []
    for segment in segments:
        for word in segment.get("words", []):
            if word["end"] <= word["start"]:
                continue
            words.append(word)
    return sorted(words, key=lambda item: item["start"])


def snap_start_to_word_boundary(timestamp, words):
    for word in words:
        if word["start"] < timestamp < word["end"]:
            return word["start"], f"Moved start to word boundary before '{word['text']}'."
    return timestamp, None


def snap_end_to_word_boundary(timestamp, words):
    for word in words:
        if word["start"] < timestamp < word["end"]:
            return word["end"], f"Extended end to complete word '{word['text']}'."
    return timestamp, None


def latest_word_end_before(words, limit):
    candidates = [word["end"] for word in words if word["end"] <= limit]
    return max(candidates) if candidates else None


def earliest_word_end_after(words, limit):
    candidates = [word["end"] for word in words if word["end"] > limit]
    return min(candidates) if candidates else None


def first_word_start_after(words, timestamp):
    candidates = [word["start"] for word in words if word["start"] >= timestamp]
    return min(candidates) if candidates else None


def enforce_no_mid_word(start, end, segments, *, max_duration=MAX_SHORT_DURATION):
    all_words = flatten_words(segments)
    if not all_words:
        safe_end = min(end, start + max_duration)
        return start, safe_end, ["No word timestamps available, kept raw boundaries with duration cap."], "none"

    decisions = []
    source = "transcript" if any(word.get("source") == "transcript" for word in all_words) else "estimated"

    original_start = start
    original_end = end

    start, start_decision = snap_start_to_word_boundary(start, all_words)
    if start_decision:
        decisions.append(start_decision)

    end, end_decision = snap_end_to_word_boundary(end, all_words)
    if end_decision:
        decisions.append(end_decision)

    if end - start > max_duration:
        strict_limit = start + max_duration
        snapped_end = latest_word_end_before(all_words, strict_limit)
        if snapped_end is None:
            snapped_end = strict_limit
        if snapped_end != end:
            decisions.append(
                f"Shortened end from {original_end:.2f}s to {snapped_end:.2f}s to keep the clip under {max_duration:.0f}s."
            )
        end = snapped_end

    if end <= start:
        next_word_end = earliest_word_end_after(all_words, start)
        if next_word_end is not None:
            end = min(next_word_end, start + max_duration)
            decisions.append("Recovered invalid cut bounds by extending to the next completed word.")
        else:
            end = min(original_end, start + max_duration)
            decisions.append("Recovered invalid cut bounds using the original end timestamp.")

    next_word_start = first_word_start_after(all_words, start)
    if next_word_start is not None and next_word_start > start and not decisions:
        decisions.append("Cut already landed between words, no boundary correction was needed.")

    return start, end, decisions, source


def find_input_video(input_path):
    path = Path(input_path)
    if path.is_file():
        return path

    if path.is_dir():
        candidates = list(path.glob("*.mp4")) + list(path.glob("*.mkv")) + list(path.glob("*.mov")) + list(path.glob("*.webm"))
    else:
        input_dir = Path("input")
        candidates = list(input_dir.glob("*.mp4")) + list(input_dir.glob("*.mkv")) + list(input_dir.glob("*.mov")) + list(input_dir.glob("*.webm"))

    if not candidates:
        raise FileNotFoundError("No input video was found. Pass --video explicitly.")

    scored = []
    for candidate in candidates:
        has_audio = file_has_audio(candidate)
        has_video = file_has_video(candidate)
        scored.append((has_video and has_audio, has_video, has_audio, candidate.stat().st_mtime, candidate))

    scored.sort(key=lambda item: (item[0], item[1], item[2], item[3]), reverse=True)
    best = scored[0][4]
    if not scored[0][0]:
        print(f"Warning: selected file without full AV streams: {best} (video={scored[0][1]}, audio={scored[0][2]})")
    return best


def cut_segment(video_path, output_path, start, duration):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-ss",
        f"{start:.3f}",
        "-t",
        f"{duration:.3f}",
        "-map",
        "0",
        "-vf",
        "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920",
        "-c:v",
        "libx264",
        "-preset",
        "superfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def format_filename_time(seconds):
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}-{secs:05.2f}".replace(".", "_")


def parse_args():
    parser = argparse.ArgumentParser(description="Cut raw short clips using ffmpeg.")
    parser.add_argument("--video", default=None, help="Path to source video")
    parser.add_argument("--windows", default="top_windows.json", help="JSON file with start/end windows")
    parser.add_argument("--transcript", default="transcripts/final_transcript.json", help="Transcript JSON for boundary protection")
    parser.add_argument("--output-dir", default="cuts/raw", help="Output directory for raw cuts")
    parser.add_argument("--cutting-log", default="metadata/cutting_logic.json", help="Log file for Smart Context Cutter decisions")
    return parser.parse_args()


def main():
    args = parse_args()
    video_path = find_input_video(args.video) if args.video else find_input_video("input")
    windows = load_windows(args.windows)
    transcript = load_transcript(args.transcript)
    cutting_log = load_cutting_log(args.cutting_log)

    for idx, window in enumerate(windows, start=1):
        start = float(window["start"])
        end = float(window["end"])
        start, end, decisions, word_source = enforce_no_mid_word(start, end, transcript)
        duration = end - start

        output_path = Path(args.output_dir) / f"segment_{idx}_{format_filename_time(start)}_{format_filename_time(end)}.mp4"
        upsert_cutter_adjustment(
            cutting_log,
            {
                "segment_index": idx,
                "source_window": {
                    "start": window.get("start"),
                    "end": window.get("end"),
                    "heatmap_start": window.get("heatmap_start"),
                    "heatmap_end": window.get("heatmap_end"),
                    "summary": window.get("summary"),
                    "ai_reason": window.get("ai_reason"),
                    "hook_reason": window.get("hook_reason"),
                    "ending_reason": window.get("ending_reason"),
                },
                "final_start": start,
                "final_end": end,
                "final_duration": duration,
                "word_boundary_source": word_source,
                "decisions": decisions,
            },
        )

        print(f"Cutting segment {idx}: {start:.2f}s - {end:.2f}s -> {output_path}")
        cut_segment(video_path, output_path, start, duration)

    save_cutting_log(args.cutting_log, cutting_log)
    print(f"Done. Files saved in {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
