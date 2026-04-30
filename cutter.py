import argparse
import json
import subprocess
from pathlib import Path


def load_windows(windows_file):
    with open(windows_file, 'r', encoding='utf-8') as f:
        windows = json.load(f)
    if not isinstance(windows, list):
        raise ValueError('Plik segmentów musi zawierać listę obiektów JSON.')
    return windows


def find_input_video(input_path):
    path = Path(input_path)
    if path.exists():
        return path
    candidates = list(Path('input').glob('*.mp4')) + list(Path('input').glob('*.mkv')) + list(Path('input').glob('*.mov')) + list(Path('input').glob('*.webm'))
    if not candidates:
        raise FileNotFoundError('Nie znaleziono pliku wideo w katalogu input/. Podaj --video.')
    return candidates[0]


def cut_segment(video_path, output_path, start, duration):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        'ffmpeg',
        '-y',
        '-ss', f'{start:.3f}',
        '-i', str(video_path),
        '-t', f'{duration:.3f}',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', '+faststart',
        str(output_path)
    ]
    subprocess.run(cmd, check=True)


def format_time(seconds):
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f'{minutes:02d}-{secs:05.2f}'.replace('.', '_')


def parse_args():
    parser = argparse.ArgumentParser(description='Wycinanie segmentów Shorts z wideo przy pomocy ffmpeg')
    parser.add_argument('--video', default=None, help='Ścieżka do pliku wideo w input/')
    parser.add_argument('--windows', default='top_windows.json', help='Plik JSON z listą wybranych okien (start/end)')
    parser.add_argument('--output-dir', default='cuts', help='Katalog wyjściowy dla wyciętych plików')
    return parser.parse_args()


def main():
    args = parse_args()
    video_path = find_input_video(args.video) if args.video else find_input_video('input')
    windows = load_windows(args.windows)

    for idx, window in enumerate(windows, start=1):
        start = float(window['start'])
        end = float(window['end'])
        duration = end - start
        safe_label = window.get('summary', f'segment_{idx}')[:40].replace(' ', '_').replace('/', '_')
        output_path = Path(args.output_dir) / f'segment_{idx}_{format_time(start)}_{format_time(end)}.mp4'
        print(f'Wycinam segment {idx}: {start:.2f}s - {end:.2f}s -> {output_path}')
        cut_segment(video_path, output_path, start, duration)

    print(f'Gotowe. Pliki zapisano w {Path(args.output_dir).resolve()}')


if __name__ == '__main__':
    main()
