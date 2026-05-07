#!/usr/bin/env python3
"""
subtitler.py — Inteligentny system stylizacji napisów z Speaker Diarization.

Funkcje:
- Ładuje transkrypcję z JSON z metadanymi speaker/importance/chaos
- Generuje plik ASS z kolorami speakerów i ważnymi słowami
- Filtrowanie chaosu: ukrywa nieistotne napisy przy chaosie
- Emphasis: podkreśla ważne słowa kolorem i pogrubieniem
"""

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import shutil

SPEAKER_COLORS: Dict[str, str] = {
    "Speaker A": "&H00FFFFFF",
    "Speaker B": "&H0000A5FF",  # Neon orange for better contrast
    "Speaker C": "&H00FFFF00",
    "Speaker D": "&H00FF00FF",
    "Speaker E": "&H0000FF00",
}
DEFAULT_STYLE_NAME = "Default"
CHAOS_EMPHASIS_STYLE = "ChaosEmphasis"
EMPHASIS_COLOR = "&H0000FF00"  # Neon green
KEYWORD_PATTERNS = [
    r"\d+\s*(?:zł|pln|euro|usd|dollar)",
    r"\b[A-ZŚĆĘŁŃÓŹŻ][a-zśćęłńóźż]+\b",
    r"(?:wow|wow!|super|fantastycz|niesamowit|genialn|straszn|okropn)",
]
KEYWORD_REGEX = re.compile("|".join(KEYWORD_PATTERNS), re.IGNORECASE | re.UNICODE)


def parse_time(time_str: str) -> float:
    if isinstance(time_str, (int, float)):
        return float(time_str)
    time_str = str(time_str).strip()
    pattern = r'^(?:(\d+):)?(\d{1,2}):(\d{2}(?:\.\d+)?)$'
    match = re.match(pattern, time_str)
    if not match:
        raise ValueError(f"Niepoprawny format czasu: {time_str}")
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    return hours * 3600 + minutes * 60 + seconds


def load_transcript(path: Path) -> List[Dict]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'segments' in data:
        return data['segments']
    return data


def apply_emphasis(text: str, speaker_color: str = "&H00FFFFFF") -> str:
    def repl(match):
        word = match.group(0)
        return f'{{\\b1\\c{EMPHASIS_COLOR}}}{word}{{\\b0\\c{speaker_color}}}'
    return KEYWORD_REGEX.sub(repl, text)


def calculate_words_per_second(text: str, duration: float) -> float:
    if duration <= 0 or not text.strip():
        return 0.0
    return len(text.split()) / duration


def should_display_subtitle(segment: Dict, duration: float) -> bool:
    chaos = bool(segment.get('chaos', False))
    importance = int(segment.get('importance', 3))
    text = str(segment.get('text', '')).strip()
    # "Cisza w chaosie": napisy znikają, CHYBA ŻE importance >= 5
    if chaos and importance < 5:
        return False
    # Filtrowanie zbyt szybkich napisów o niskiej ważności
    if calculate_words_per_second(text, duration) > 4.0 and importance < 4:
        return False
    return True


def build_subtitle_events(transcript: List[Dict], segment_start: float, segment_duration: float) -> List[Dict]:
    events: List[Dict] = []
    for item in transcript:
        seg_start = parse_time(item.get('start', '00:00'))
        seg_end = parse_time(item.get('end', '00:00'))
        text = str(item.get('text', '')).strip()
        speaker = str(item.get('speaker', DEFAULT_STYLE_NAME))
        importance = int(item.get('importance', 3))
        chaos = bool(item.get('chaos', False))
        
        if not text or seg_end <= segment_start or seg_start >= segment_start + segment_duration:
            continue
            
        overlap_start = max(seg_start, segment_start)
        overlap_end = min(seg_end, segment_start + segment_duration)
        rel_start = overlap_start - segment_start
        rel_end = overlap_end - segment_start
        
        if rel_end <= rel_start:
            continue
            
        if not should_display_subtitle(item, rel_end - rel_start):
            continue
        
        speaker_color = SPEAKER_COLORS.get(speaker, "&H00FFFFFF")
        
        # Dla importance 5 w chaosie nie stosujemy apply_emphasis, bo tekst będzie wyświetlany specjalnym stylem
        if chaos and importance == 5:
            display_text = text
        else:
            display_text = apply_emphasis(text, speaker_color) if importance >= 4 else text

        events.append({
            'start': rel_start,
            'end': rel_end,
            'text': display_text,
            'speaker': speaker if speaker in SPEAKER_COLORS else DEFAULT_STYLE_NAME,
            'importance': importance,
            'chaos': chaos,
        })
    return events


def format_ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"


def create_ass_file(events: List[Dict]) -> str:
    # MarginV: 285 aby być bezpiecznie nad UI YouTube/TikTok
    MARGIN_V = 285

    lines: List[str] = [
        "[Script Info]",
        "Title: Viral Cutter AI Subtitles",
        "ScriptType: v4.00+",
        "Collisions: Normal",
        "PlayResX: 1920",
        "PlayResY: 1080",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: {DEFAULT_STYLE_NAME},Montserrat,22,&H00FFFFFF,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1.2,0,2,70,70,{MARGIN_V},1",
    ]
    for speaker, color in SPEAKER_COLORS.items():
        lines.append(f"Style: {speaker},Montserrat,22,{color},&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1.2,0,2,70,70,{MARGIN_V},1")
    
    # ChaosEmphasis: +30% font (22 * 1.3 ≈ 29), Alignment 5 (center-center), Neon Green
    lines.append(f"Style: {CHAOS_EMPHASIS_STYLE},Montserrat,29,{EMPHASIS_COLOR},&H00000000,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,1.2,0,5,70,70,{MARGIN_V},1")
    
    lines.extend(["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"])
    for event in events:
        start_time = format_ass_time(event['start'])
        end_time = format_ass_time(event['end'])
        text = str(event['text']).replace(',', '\\,')
        
        # Wybór stylu: ChaosEmphasis dla ważnych słów w chaosie
        style = CHAOS_EMPHASIS_STYLE if event.get('chaos') and event.get('importance') == 5 else event['speaker']
        
        lines.append(f"Dialogue: 0,{start_time},{end_time},{style},,0,0,0,,{text}")
    return "\n".join(lines)


def extract_segment_time_from_filename(filename: str) -> Tuple[float, float]:
    name = Path(filename).stem
    pattern = r'segment_\d+_(\d{2})-(\d{2}_\d+)_(\d{2})-(\d{2}_\d+)'
    match = re.search(pattern, name)
    if not match:
        raise ValueError(f"Nie można sparsować czasu z nazwy pliku: {filename}")
    start_minutes = int(match.group(1))
    start_secs = float(match.group(2).replace('_', '.'))
    end_minutes = int(match.group(3))
    end_secs = float(match.group(4).replace('_', '.'))
    return start_minutes * 60 + start_secs, end_minutes * 60 + end_secs


def add_subtitles_to_video(input_video: Path, output_video: Path, ass_file: Path) -> None:
    output_video.parent.mkdir(parents=True, exist_ok=True)
    escaped_path = str(ass_file).replace('\\', '\\\\').replace(':', '\\:')
    filter_str = f"ass='{escaped_path}'"
    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(input_video),
        '-vf', filter_str,
        '-c:a', 'aac',
        '-b:a', '192k',
        str(output_video),
    ]
    print(f'  Dodaję napisy (ASS): {output_video.name}')
    subprocess.run(cmd, check=True)


def process_cut_file(cut_file: Path, transcript: List[Dict], output_raw: Path, output_subs: Path) -> None:
    output_raw.mkdir(parents=True, exist_ok=True)
    output_subs.mkdir(parents=True, exist_ok=True)
    segment_start, segment_end = extract_segment_time_from_filename(cut_file.name)
    segment_duration = segment_end - segment_start
    events = build_subtitle_events(transcript, segment_start, segment_duration)
    if not events:
        print(f'  ⚠ Brak napisów dla {cut_file.name}')
    raw_output = output_raw / cut_file.name
    if cut_file.resolve() != raw_output.resolve():
        shutil.copy2(cut_file, raw_output)
        print(f'✓ Skopiowano surowe wideo: {raw_output.name}')
    else:
        print(f'✓ Surowe wideo jest już w cuts/raw: {raw_output.name}')
    ass_file = cut_file.parent / f'{cut_file.stem}.ass'
    with open(ass_file, 'w', encoding='utf-8') as f:
        f.write(create_ass_file(events))
    subs_output = output_subs / cut_file.name
    try:
        add_subtitles_to_video(raw_output, subs_output, ass_file)
        print(f'✓ Dodano napisy (ASS): {subs_output.name}')
    except subprocess.CalledProcessError as e:
        print(f'  ✗ Błąd przy dodawaniu napisów: {e}')
    finally:
        if ass_file.exists():
            ass_file.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Inteligentne dodawanie napisów z Speaker Diarization')
    parser.add_argument('--transcript', default='transcripts/final_transcript.json', help='Ścieżka do transkrypcji JSON z metadanymi')
    parser.add_argument('--input-dir', default='cuts', help='Katalog z wyciętymi wideo')
    parser.add_argument('--output-raw', default='cuts/raw', help='Katalog wyjściowy dla surowych wideo (bez napisów)')
    parser.add_argument('--output-subs', default='cuts/subtitles', help='Katalog wyjściowy dla wideo z napisami')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    transcript_path = Path(args.transcript)
    input_dir = Path(args.input_dir)
    output_raw = Path(args.output_raw)
    output_subs = Path(args.output_subs)
    if not transcript_path.exists():
        print(f'✗ Plik transkrypcji nie istnieje: {transcript_path}')
        return
    if not input_dir.exists():
        print(f'✗ Katalog wejściowy nie istnieje: {input_dir}')
        return
    print(f'📖 Ładuję transkrypcję: {transcript_path}')
    transcript = load_transcript(transcript_path)
    cut_files = sorted(input_dir.glob('segment_*.mp4'))
    if not cut_files:
        print(f'⚠ Nie znaleziono plików segment_*.mp4 w {input_dir}')
        return
    print(f'🎬 Znaleziono {len(cut_files)} wyciętych wideo')
    print()
    for cut_file in cut_files:
        print(f'Przetwarzam: {cut_file.name}')
        process_cut_file(cut_file, transcript, output_raw, output_subs)
        print()
    print('✓ Gotowe!')
    print(f'  Surowe wideo: {output_raw.resolve()}')
    print(f'  Z napisami (ASS): {output_subs.resolve()}')


if __name__ == '__main__':
    main()
