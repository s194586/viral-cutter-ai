import argparse
import json
import re
from bisect import bisect_left
from pathlib import Path

SENTENCE_BREAK_RE = re.compile(r'(?<=[\.!?…])\s+')


def parse_time(time_str):
    parts = [p for p in time_str.split(':') if p != '']
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    raise ValueError(f'Niepoprawny format czasu: {time_str}')


def load_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        transcript = json.load(f)
    if isinstance(transcript, dict) and 'segments' in transcript:
        transcript = transcript['segments']
    return transcript


def load_heatmap(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def split_sentences(text):
    parts = SENTENCE_BREAK_RE.split(text.strip())
    sentences = [part.strip() for part in parts if part.strip()]
    return sentences or [text.strip()]


def build_sentence_boundaries(transcript):
    sentences = []
    for segment in transcript:
        start = parse_time(segment['start'])
        end = parse_time(segment['end'])
        text = segment.get('text', '').replace('\n', ' ').strip()
        if not text:
            continue

        pieces = split_sentences(text)
        if len(pieces) == 1:
            sentences.append({'start': start, 'end': end, 'text': pieces[0]})
            continue

        total_chars = sum(len(piece) for piece in pieces)
        if total_chars == 0:
            sentences.append({'start': start, 'end': end, 'text': text})
            continue

        cursor = start
        consumed = 0
        for piece in pieces[:-1]:
            consumed += len(piece)
            portion = consumed / total_chars
            boundary = start + (end - start) * portion
            sentences.append({'start': cursor, 'end': boundary, 'text': piece})
            cursor = boundary
        sentences.append({'start': cursor, 'end': end, 'text': pieces[-1]})
    return sentences


def build_heatmap_index(heatmap):
    heatmap_sorted = sorted(heatmap, key=lambda entry: entry['start_time'])
    starts = [entry['start_time'] for entry in heatmap_sorted]
    return heatmap_sorted, starts


def average_heatmap_value(heatmap, starts, window_start, window_end):
    idx = bisect_left(starts, window_start)
    if idx > 0:
        idx -= 1

    total_weight = 0.0
    weighted_sum = 0.0
    for entry in heatmap[idx:]:
        entry_start = entry['start_time']
        entry_end = entry['end_time']
        if entry_start >= window_end:
            break
        overlap_start = max(window_start, entry_start)
        overlap_end = min(window_end, entry_end)
        overlap = overlap_end - overlap_start
        if overlap <= 0:
            continue
        total_weight += overlap
        weighted_sum += overlap * entry['value']
    if total_weight == 0:
        return 0.0
    return weighted_sum / total_weight


def collect_text_for_window(sentences, window_start, window_end):
    parts = []
    for sentence in sentences:
        if sentence['end'] <= window_start:
            continue
        if sentence['start'] >= window_end:
            break
        parts.append(sentence['text'])
    return ' '.join(parts).strip()


def summarize_text(text, max_chars=220):
    summary = ' '.join(text.split())
    if len(summary) <= max_chars:
        return summary
    truncated = summary[:max_chars].rstrip()
    if '.' in truncated:
        truncated = truncated[: truncated.rfind('.') + 1]
    if len(truncated) < 40:
        truncated = summary[:max_chars].rstrip()
    return truncated + '…'


def build_candidates(sentences, heatmap, starts, min_duration, max_duration):
    sentence_boundaries = sorted({boundary for s in sentences for boundary in (s['start'], s['end'])})
    candidates = []

    for window_start in sentence_boundaries:
        min_end = window_start + min_duration
        max_end = window_start + max_duration
        valid_ends = [boundary for boundary in sentence_boundaries if boundary >= min_end and boundary <= max_end]
        if not valid_ends:
            continue

        for window_end in valid_ends:
            avg_value = average_heatmap_value(heatmap, starts, window_start, window_end)
            if avg_value <= 0:
                continue
            text_snippet = collect_text_for_window(sentences, window_start, window_end)
            candidates.append({
                'start': window_start,
                'end': window_end,
                'duration': window_end - window_start,
                'avg_value': avg_value,
                'summary': summarize_text(text_snippet),
                'text': text_snippet,
            })
    return candidates


def select_non_overlapping(candidates, count=3):
    selected = []
    for candidate in sorted(candidates, key=lambda x: x['avg_value'], reverse=True):
        if any(not (candidate['end'] <= chosen['start'] or candidate['start'] >= chosen['end']) for chosen in selected):
            continue
        selected.append(candidate)
        if len(selected) == count:
            break
    return selected


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    if hours > 0:
        return f'{hours:d}:{minutes:02d}:{secs:05.2f}'
    return f'{minutes:02d}:{secs:05.2f}'


def save_top_windows(windows, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(windows, f, ensure_ascii=False, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description='Analiza viralowych fragmentów z heatmapy i transkrypcji')
    parser.add_argument('--transcript', default='transcripts/Naruciak_Final.json', help='Ścieżka do transkrypcji JSON')
    parser.add_argument('--heatmap', default='metadata/heatmap.json', help='Ścieżka do heatmapy JSON')
    parser.add_argument('--min-duration', type=float, default=30.0, help='Minimalna długość okna w sekundach')
    parser.add_argument('--max-duration', type=float, default=60.0, help='Maksymalna długość okna w sekundach')
    parser.add_argument('--top', type=int, default=3, help='Liczba najlepszych momentów do wypisania')
    parser.add_argument('--save-json', default=None, help='Zapisz wybrane okna do pliku JSON')
    return parser.parse_args()


def main():
    args = parse_args()

    transcript = load_transcript(args.transcript)
    heatmap = load_heatmap(args.heatmap)
    sentences = build_sentence_boundaries(transcript)
    heatmap_index, heatmap_starts = build_heatmap_index(heatmap)

    candidates = build_candidates(sentences, heatmap_index, heatmap_starts, args.min_duration, args.max_duration)
    if not candidates:
        raise SystemExit('Nie znaleziono żadnych okien spełniających kryteria 30-60 sekund.')

    top_windows = select_non_overlapping(candidates, count=args.top)
    if not top_windows:
        raise SystemExit('Nie udało się wybrać niepokrywających się okien. Spróbuj zmniejszyć liczbę top lub dopasować parametry.')

    print('\nTop {} momentów do Shortsów:'.format(len(top_windows)))
    for index, window in enumerate(top_windows, start=1):
        print(f'Nr {index}:')
        print(f'  Zakres: {format_time(window["start"])} - {format_time(window["end"])}')
        print(f'  Średni wynik heatmapy: {window["avg_value"]:.4f}')
        print(f'  Długość: {window["duration"]:.1f}s')
        print(f'  Opis: {window["summary"]}')
        print()

    if args.save_json:
        out_path = Path(args.save_json)
        save_top_windows(top_windows, out_path)
        print(f'Zapisano wybrane okna do: {out_path}')


if __name__ == '__main__':
    main()
