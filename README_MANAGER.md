# 🎬 Viral Cutter AI - Workflow Manager

Kompletny system automatyzacji: od pobrania wideo z YouTube, przez transkrypcję, analizę viralowych momentów, wycinanie, do dodawania dynamicznych napisów.

---

## 📋 Komponenty

### 1. `manager.py` — Główny Orkestrator
**Główny skrypt** - automatyzuje cały workflow w jednym poleceniu.

```bash
# Pełny workflow z pobieraniem
python manager.py --url "https://www.youtube.com/watch?v=..."

# Cleanup: usuń ciężkie pliki z input/ po sukcesie
python manager.py --url "..." --cleanup

# Test/Debug: pomiń pobieranie i transkrypcję
python manager.py --url "..." --skip-download

# Debug: pomiń albo wymuś AI Subtitler Checker
python manager.py --url "..." --skip-subtitle-checker
python manager.py --url "..." --force-subtitle-checker
```

**Workflow Manager:**
1. ✅ Sprawdza i tworzy niezbędne foldery (input/, metadata/, transcripts/, cuts/raw/, cuts/subtitles/)
2. 📥 **Pobieranie** - `download_content.py` (wideo z YouTube max 1080p, audio, metadane)
3. 🎙️ **Transkrypcja** - `transcribe_podcast.py` (dzielenie po ciszy, Google Gemini API)
4. 🔎 **AI Subtitler Checker** - `subtitler_checker.py` (timing, sens językowy, próbki audio pod halucynacje)
5. 📊 **Analiza** - `analyze_virals.py` (heatmapa + transkrypcja → top momenty)
6. ✂️ **Wycinanie** - `cutter.py` (shoty 9:16 zapisywane od razu do `cuts/raw/`)
7. 📝 **Napisy** - `subtitler.py` (małe białe napisy z czarnym obrysem, nisko na dole)
8. 🧹 **Cleanup** (opcjonalnie) - usuwa wideo z input/ po sukcesie

**Obsługa błędów:**
- Retry logic dla transkrypcji (2 próby)
- Raport jakości transkrypcji: `metadata/subtitle_check_report.json`
- Jasne komunikaty o błędach
- Graceful shutdown na Ctrl+C

---

### 2. `subtitler_checker.py` — AI Subtitler Checker
Weryfikuje transkrypcję przed analizą i generowaniem napisów.

```bash
python subtitler_checker.py \
  --audio input/audio.mp3 \
  --transcript transcripts/final_transcript.json \
  --report metadata/subtitle_check_report.json
```

**Funkcjonalność:**
- ✅ Lokalna kontrola timestampów, pustych segmentów, overlapów i tempa słów
- ✅ Heurystyki sensowności tekstu: artefakty modelu, powtórzenia, podejrzane znaki
- ✅ Krótkie próbki audio porównywane przez Gemini z tekstem transkrypcji
- ✅ Wykrywanie podejrzanych halucynacji: słowa w transkrypcji, których nie słychać w próbce
- ✅ Raport JSON ze statusem `pass`, `warning` albo `fail`

**Output:**
- `metadata/subtitle_check_report.json` - score, lista problemów i wyniki próbek AI

---

### 3. `subtitler.py` — Dynamiczne Napisy
Dodaje napisy na wycięte wideo z transkrypcji.

```bash
python subtitler.py \
  --transcript transcripts/Naruciak_Final.json \
  --input-dir cuts/raw \
  --output-raw cuts/raw \
  --output-subs cuts/subtitles
```

**Funkcjonalność:**
- ✅ 1-2 słowa na ekranie (dynamiczny rozsplit transkrypcji)
- ✅ Mała, czytelna czcionka dopasowana do shotów
- ✅ Białe napisy z cienkim czarnym obrysem
- ✅ Umieszczone nisko przy dole (Alignment=2, MarginV=65)
- ✅ Bezpieczne strefy (nie zasłaniają UI TikToka/Shortsów)

**Output:**
- `cuts/raw/` - surowe wideo (bez napisów)
- `cuts/subtitles/` - wideo z wbijanymi napisami (burnt-in)

---

### 4. Pozostałe Komponenty

#### `download_content.py`
```bash
python download_content.py "https://www.youtube.com/watch?v=..."
```
- Pobiera wideo (max 1080p) i audio
- Tworzy metadane (.info.json) i heatmapę (placeholde jeśli nie ma)

#### `transcribe_podcast.py`
```bash
python transcribe_podcast.py --file input/audio.mp3 --out transcripts/output.json
```
- Transkrybuje audio dzieląc po ciszy
- Używa Google Gemini API
- Retry logic

#### `analyze_virals.py`
```bash
python analyze_virals.py \
  --transcript transcripts/Naruciak_Final.json \
  --heatmap metadata/heatmap.json \
  --save-json top_windows.json
```
- Analizuje transkrypcję i heatmapę
- Znajduje 3 najlepsze momenty (30-60s)

#### `cutter.py`
```bash
python cutter.py --windows top_windows.json --output-dir cuts/raw
```
- Wycina surowe shoty z wideo do `cuts/raw/`
- Format: `segment_1_MM-SS_ms_MM-SS_ms.mp4`

---

## 📁 Struktura Katalogów

```
project/
├── input/                          # Pobrane wideo/audio
├── metadata/                       # Metadane, heatmapy i raport checkera
│   └── subtitle_check_report.json  # Raport AI Subtitler Checkera
├── transcripts/                    # Transkrypcje (JSON)
│   ├── Naruciak_Final.json        # Główna transkrypcja
│   └── cache/                      # Temp cache dla transkrypcji
├── cuts/                           # Wycięte segmenty
│   ├── raw/                        # Surowe wycinki (bez napisów)
│   └── subtitles/                 # Wycinki z napisami (FINAL)
├── top_windows.json                # Wybrane momenty
├── manager.py                      # 🎬 GŁÓWNY ORKESTRATOR
├── subtitler_checker.py            # 🔎 Kontrola transkrypcji i halucynacji
├── subtitler.py                    # 📝 Dodawanie napisów
├── download_content.py             # 📥 Pobieranie
├── transcribe_podcast.py           # 🎙️ Transkrypcja
├── analyze_virals.py               # 📊 Analiza
├── cutter.py                       # ✂️ Wycinanie
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Instalacja
```bash
pip install -r requirements.txt
```

### 2. Konfiguracja
```bash
# .env (jeśli potrzebny Google API)
export GOOGLE_API_KEY="your-key-here"
```

### 3. Uruchomienie
```bash
python manager.py --url "https://www.youtube.com/watch?v=..." --cleanup
```

### 4. Wyniki
- Gotowe wycinki z napisami: `cuts/subtitles/`
- Każdy plik to 30-60s Shorts-ready video

---

## 🧪 Testowanie

Przetestowano na:
- ✅ 3 wycięte segmenty
- ✅ 5 surowych wideo (raw) + 5 z napisami
- ✅ Dynamiczne napisy (1-3 słowa)
- ✅ Workflow complete (pobieranie → subtitles)
- ✅ Error handling i retry logic
- ✅ Folder auto-creation

---

## 📊 Wyniki Testu

```
✓ WORKFLOW UKOŃCZONY

📊 Wygenerowane pliki:

  📂 Surowe wycinki (3 plików):
    - segment_1_08-57_53_09-31_26.mp4
    - segment_2_19-03_10_19-33_66.mp4
    - segment_3_00-15_04_00-51_00.mp4

  📂 Wycinki z napisami (3 plików):
    - segment_1_08-57_53_09-31_26.mp4
    - segment_2_19-03_10_19-33_66.mp4
    - segment_3_00-15_04_00-51_00.mp4

  📁 Katalog output: cuts/subtitles/
```

---

## 🔧 Troubleshooting

### Błąd: `ffmpeg not found`
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Błąd: `GOOGLE_API_KEY not set`
```bash
# Ustaw zmienną środowiska
export GOOGLE_API_KEY="your-key"
```

### Błąd transkrypcji
- Manager automatycznie spróbuje 2 razy
- Sprawdź limit API w Google Cloud

### Wideo bez napisów
- Sprawdź czy transkrypcja istnieje: `transcripts/Naruciak_Final.json`
- Sprawdź czy heatmapa istnieje: `metadata/heatmap.json`

---

## 📝 Notatki

- Napisy są **wbijane bezpośrednio** (burnt-in) za pomocą filtru ffmpeg `subtitles`
- Tekst: dynamiczny (1-2 słowa), mała czytelna czcionka
- Safe zones: nisko przy dole, MarginV=65
- AI Subtitler Checker działa po transkrypcji i przed wyborem viralowych momentów
- Jeśli raport checkera jest aktualny i ma status `pass` albo `warning`, manager nie odpala go ponownie
- Wszystkie procesy logują output dla debugowania
- Workflow jest modularny - każdy krok można uruchomić niezależnie

---

## 🎬 Przyszłe Ulepszenia

- [ ] **Face Tracking** - zastąpienie sztywnego center crop inteligentnym kadrowaniem, które podąża za mówiącą osobą.
- [ ] **Background Music & SFX** - automatyczne nakładanie cichego podkładu muzycznego oraz efektów dźwiękowych podkreślających kluczowe słowa.
- [ ] **AI Content Checker** - system oceny wiralowości, który analizuje wycięte fragmenty pod kątem dynamiki i potencjału zasięgowego.
- [ ] **Pełny Frontend** - graficzny interfejs użytkownika do zarządzania projektami i podglądu wideo przed eksportem.
- [ ] **Batch Processing** - obsługa wielu filmów naraz w jednym przebiegu workflow.
- [ ] **Personalizacja napisów** - konfiguracja fontów, kolorów, rozmiaru i pozycji napisów.
- [ ] **Eksport do platform** - automatyczne publikowanie lub przygotowanie eksportu pod TikTok i YouTube Shorts API.
- [ ] **Automatyczne testy** - testy regresji dla pobierania, transkrypcji, cięcia i generowania napisów.
- [ ] **Obsługa wielu języków** - rozszerzenie workflow o inne języki, OCR i TTS.
