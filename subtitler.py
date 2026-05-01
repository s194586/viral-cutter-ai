#!/usr/bin/env python3
"""Podstawowy moduł do generowania napisów z transkrypcji.

Na razie tworzy pliki SRT/VTT z segmentów z `Naruciak_Final.json`.
W przyszłości można go rozwinąć o bezpośrednie nałożenie napisów na wycięte klipy.
"""

import argparse
import json
import re
from pathlib import Path

TIME_RE = re.compile(r'^(?:(\d+):)?(\d{1,2}):(\d{2}(?:\.\d+)?)$')


def parse_time(time_str):
    if isinstance(time_str, (int, float)):
        return float(time_str)
    value = TIME_RE.match(time_str.strip())
    if not value:
        raise ValueError(f'Niepoprawny format czasu: {time_str}')
    hours = int(value.group(1) or 0)
    minutes = int(value.group(2))
    seconds = float(value.group(3))
    return hours * 3600 + minutes * 60 + seconds


def format_srt_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    ms = int((secs - int(secs)) * 1000)
    return f'{hours:02d}:{minutes:02d}:{int(secs):02d},{ms:03d}'


def format_vtt_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    ms = int((secs - int(secs)) * 1000)
    return f'{hours:02d}:{minutes:02d}:{int(secs):02d}.{ms:03d}'


def load_transcript(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'segments' in data:
        return data['segments']
    return data


def build_subtitles(transcript):
    subtitles = []
    for idx, segment in enumerate(transcript, start=1):
        start = parse_time(segment['start'])
        end = parse_time(segment['end'])
        text = segment.get('text', '').replace('\n', ' ').strip()
        if not text:
            continue
        subtitles.append({
            'index': idx,
            'start': start,
            'end': end,
            'text': text,
        })
    return subtitles


def save_srt(subtitles, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in subtitles:
            f.write(f"{item['index']}\n")
            f.write(f"{format_srt_timestamp(item['start'])} --> {format_srt_timestamp(item['end'])}\n")
            f.write(f"{item['text']}\n\n")


def save_vtt(subtitles, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('WEBVTT\n\n')
        for item in subtitles:
            start = format_vtt_timestamp(item['start'])
            end = format_vtt_timestamp(item['end'])
            f.write(f"{start} --> {end}\n")
            f.write(f"{item['text']}\n\n")


def parse_args():
    parser = argparse.ArgumentParser(description='Generuj plik napisów z transkrypcji JSON')
    parser.add_argument('--transcript', default='transcripts/Naruciak_Final.json', help='Ścieżka do transkrypcji JSON')
    parser.add_argument('--output-dir', default='subtitles', help='Katalog wyjściowy dla napisów')
    parser.add_argument('--format', choices=['srt', 'vtt'], default='srt', help='Format napisów')
    return parser.parse_args()


def main():
    args = parse_args()
    transcript = load_transcript(args.transcript)
    subtitles = build_subtitles(transcript)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{Path(args.transcript).stem}.{args.format}"

    if args.format == 'srt':
        save_srt(subtitles, output_file)
    else:
        save_vtt(subtitles, output_file)

    print(f'Zapisano napisy: {output_file}')
    print('To jest podstawowy fundament. W przyszłości można dodać funkcję burn-in lub podpinania napisów do wyciętych klipów.')


if __name__ == '__main__':
    main()
