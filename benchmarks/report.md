# AI-Virtual-Cutter Benchmark Report

- Generated at: `2026-05-11T02:16:18.683251+00:00`
- Run id: `20260511_005600`
- AI mode: `local_only`
- Subtitle checker mode: `local_only`
- Legacy media assets in `input/`: `4`
- Benchmark corpus assets in `benchmarks/assets/`: `10`
- Auxiliary smoke assets: `2`

## Scope

- Legacy input asset: `input\EMERITOS BANDITOS BEZ MVP MAJORA W ESEA INTERMEDIATE!.f251.mp3`
- Legacy input asset: `input\EMERITOS BANDITOS BEZ MVP MAJORA W ESEA INTERMEDIATE!.f251.webm`
- Legacy input asset: `input\EMERITOS BANDITOS BEZ MVP MAJORA W ESEA INTERMEDIATE!.f399.mp4`
- Legacy input asset: `input\EMERITOS BANDITOS BEZ MVP MAJORA W ESEA INTERMEDIATE!.mp4`
- Benchmark corpus asset: `benchmarks\assets\canva_presentation_tutorial\input\source.mp3`
- Benchmark corpus asset: `benchmarks\assets\canva_presentation_tutorial\input\source.mp4`
- Benchmark corpus asset: `benchmarks\assets\magenta_team_podcast\input\source.mp3`
- Benchmark corpus asset: `benchmarks\assets\magenta_team_podcast\input\source.mp4`
- Benchmark corpus asset: `benchmarks\assets\putin_parade_commentary\input\source.mp3`
- Benchmark corpus asset: `benchmarks\assets\putin_parade_commentary\input\source.mp4`
- Benchmark corpus asset: `benchmarks\assets\roman_giertych_commentary\input\source.mp3`
- Benchmark corpus asset: `benchmarks\assets\roman_giertych_commentary\input\source.mp4`
- Benchmark corpus asset: `benchmarks\assets\ukraine_war_report\input\source.mp3`
- Benchmark corpus asset: `benchmarks\assets\ukraine_war_report\input\source.mp4`
- Auxiliary smoke asset (not used to claim universality): `tmp\smoke_120s.mp3`
- Auxiliary smoke asset (not used to claim universality): `tmp\smoke_5s.mp3`
- Configured benchmark cases: `6`
- Distinct expected content types tested: `gameplay, generic, podcast, tutorial`
- This iteration expands the real benchmark corpus to `6` configured materials.

## Classifier Results

| Material | Expected | Auto detected | Confidence | Correct | Reasons |
| --- | --- | --- | ---: | --- | --- |
| EMERITOS BANDITOS gameplay | `gameplay` | `gameplay` | 0.97 | yes | Visual motion is high across sampled frames.; Scene changes are frequent.; Speech contains many emotionally elevated segments. |
| Ukraine war report commentary | `generic` | `podcast` | 0.76 | no | High speech coverage across the material.; Multiple recurring speakers are present.; No single speaker dominates the full transcript. |
| Roman Giertych commentary essay | `generic` | `generic` | 0.53 | yes | Keyword evidence is weak, so a generic fallback stays safer. |
| Putin parade commentary | `generic` | `podcast` | 0.83 | no | High speech coverage across the material.; Utterances are relatively long and conversational.; The transcript contains many longer turns. |
| Magenta Team two-person podcast | `podcast` | `generic` | 0.50 | no | Signals for gameplay were not strong enough to avoid a safe generic strategy. |
| Canva presentation tutorial | `tutorial` | `generic` | 0.51 | no | Signals for podcast were not strong enough to avoid a safe generic strategy. |

## Key Observations

- Commentary / generic cases routed to `podcast` in `2/3` cases.
- True podcast cases classified correctly as `podcast`: `0/1`.
- True tutorial cases classified correctly as `tutorial`: `0/1`.
- Expected single-speaker materials flagged as over-segmented by diarization: `4`.

## EMERITOS BANDITOS gameplay

- Expected content type: `gameplay`
- Expected speaker mode: `multi`
- Status: `completed`
- Description: Repository gameplay benchmark with facecam, team voice chat and fast game-state changes.
- Notes: Current gameplay material available in the repository. It is the only full long-form benchmark case at the moment.
- Transcript preparation: `reused_local_transcript`
- Heatmap source: `existing_heatmap`

### Transcript / Diarization

- Segments: `701`
- Speakers: `4`
- Speaker switches: `467`
- Dominant speaker ratio: `0.2825`
- Diarization status: `applied`
- Fallback used: `False`

### Subtitle Checker

- Mode: `local_only`
- Status: `warning`
- Score: `70.0`
- Issues: `0` errors, `38` warnings
- Top issue codes: `TOO_MANY_WORDS_FOR_DURATION` x35, `REPEATED_WORDS` x2, `DUPLICATED_ADJACENT_TEXT` x1

### Strategy Scenarios

| Scenario | Arg | Detected | Confidence | Override ok | Render success | Top-5 overlap note |
| --- | --- | --- | ---: | --- | --- | --- |
| auto | `auto` | `gameplay` | 0.97 | False | True | - |
| manual_gameplay | `gameplay` | `gameplay` | 1.00 | True | True | 5/5 overlap vs auto |
| compare_podcast | `podcast` | `podcast` | 1.00 | True | True | 3/5 overlap vs auto |
| compare_generic | `generic` | `generic` | 1.00 | True | True | 4/5 overlap vs auto |

### Pairwise Overlap

- `auto` vs `manual_gameplay`: `5/5` overlapping clips (`1.00`)
- `auto` vs `compare_podcast`: `3/5` overlapping clips (`0.60`)
- `auto` vs `compare_generic`: `4/5` overlapping clips (`0.80`)
- `manual_gameplay` vs `compare_podcast`: `3/5` overlapping clips (`0.60`)
- `manual_gameplay` vs `compare_generic`: `4/5` overlapping clips (`0.80`)
- `compare_podcast` vs `compare_generic`: `3/5` overlapping clips (`0.60`)

### Top Clips

#### auto

- `17:47.41 - 18:35.79` | score `94.23` | reasons: strong heatmap support, contains punchy or emotional language, has several short punchy lines
- `05:25.33 - 05:58.35` | score `92.97` | reasons: strong heatmap support, contains punchy or emotional language, has several short punchy lines
- `16:38.20 - 17:19.73` | score `92.73` | reasons: strong heatmap support, contains punchy or emotional language, contains high-importance transcript moments
- `02:17.46 - 02:52.19` | score `92.62` | reasons: strong heatmap support, contains punchy or emotional language, has several short punchy lines
- `04:14.05 - 04:59.95` | score `92.07` | reasons: strong heatmap support, contains punchy or emotional language, has several short punchy lines

#### manual_gameplay

- `17:47.41 - 18:35.79` | score `94.23` | reasons: strong heatmap support, contains punchy or emotional language, has several short punchy lines
- `05:25.33 - 05:58.35` | score `92.97` | reasons: strong heatmap support, contains punchy or emotional language, has several short punchy lines
- `16:38.20 - 17:19.73` | score `92.73` | reasons: strong heatmap support, contains punchy or emotional language, contains high-importance transcript moments
- `02:17.46 - 02:52.19` | score `92.62` | reasons: strong heatmap support, contains punchy or emotional language, has several short punchy lines
- `04:14.05 - 04:59.95` | score `92.07` | reasons: strong heatmap support, contains punchy or emotional language, has several short punchy lines

#### compare_podcast

- `17:47.41 - 18:35.79` | score `89.18` | reasons: strong heatmap support, good speech density for a short clip, has speaker dynamics or conversational turns
- `16:38.20 - 17:28.11` | score `88.26` | reasons: strong heatmap support, has speaker dynamics or conversational turns, good speech density for a short clip
- `04:58.65 - 05:58.35` | score `87.52` | reasons: strong heatmap support, good speech density for a short clip, has speaker dynamics or conversational turns
- `00:06.56 - 00:45.74` | score `85.53` | reasons: strong heatmap support, good speech density for a short clip, has speaker dynamics or conversational turns
- `07:54.74 - 08:25.84` | score `85.53` | reasons: strong heatmap support, good speech density for a short clip, has speaker dynamics or conversational turns

#### compare_generic

- `17:47.41 - 18:35.79` | score `89.45` | reasons: strong heatmap support, contains punchy or emotional language, good speech density for a short clip
- `16:38.20 - 17:19.73` | score `88.83` | reasons: strong heatmap support, contains punchy or emotional language, contains high-importance transcript moments
- `05:37.91 - 06:14.94` | score `88.78` | reasons: strong heatmap support, contains punchy or emotional language, good speech density for a short clip
- `04:14.05 - 04:59.95` | score `87.6` | reasons: strong heatmap support, contains punchy or emotional language, contains high-importance transcript moments
- `00:06.56 - 00:40.74` | score `86.68` | reasons: strong heatmap support, contains punchy or emotional language, good speech density for a short clip

### Rendering

- `auto`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`5`
- `manual_gameplay`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`5`
- `compare_podcast`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`7`
- `compare_generic`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`4`

### Findings

- Auto classification matched the expected type (gameplay) with confidence 0.97.
- Subtitle checker reported warnings (38), but no hard failure.
- Face-aware rendering completed, but actual face detections were sparse (93/2442 sampled checks), so this benchmark does not strongly validate facecam tracking quality.
- All rendered benchmark scenarios produced the requested subtitled clips.

## Ukraine war report commentary

- Expected content type: `generic`
- Expected speaker mode: `single`
- Status: `completed`
- Source URL: https://www.youtube.com/watch?v=5hC0yPPFOYA
- Description: Single-host war report with map-based commentary and headline-driven analysis. Treated as generic/commentary-like for the current classifier taxonomy.
- Notes: Added as a generic/commentary benchmark. It is speech-heavy, but it is not a true podcast or tutorial.
- Transcript preparation: `reused_local_transcript`
- Heatmap source: `existing_heatmap`

### Transcript / Diarization

- Segments: `1053`
- Speakers: `4`
- Speaker switches: `684`
- Dominant speaker ratio: `0.3514`
- Diarization status: `applied`
- Fallback used: `False`
- Diagnostic flags: `expected_single_speaker_but_detected_many`

### Subtitle Checker

- Mode: `local_only`
- Status: `warning`
- Score: `70.0`
- Issues: `0` errors, `10` warnings
- Top issue codes: `TOO_MANY_WORDS_FOR_DURATION` x8, `MODEL_ARTIFACT` x1, `EARLY_TRANSCRIPT_END` x1

### Strategy Scenarios

| Scenario | Arg | Detected | Confidence | Override ok | Render success | Top-5 overlap note |
| --- | --- | --- | ---: | --- | --- | --- |
| auto | `auto` | `podcast` | 0.76 | False | True | - |
| manual_generic | `generic` | `generic` | 1.00 | True | True | 4/5 overlap vs auto |
| compare_podcast | `podcast` | `podcast` | 1.00 | True | True | 5/5 overlap vs auto |

### Pairwise Overlap

- `auto` vs `manual_generic`: `4/5` overlapping clips (`0.80`)
- `auto` vs `compare_podcast`: `5/5` overlapping clips (`1.00`)
- `manual_generic` vs `compare_podcast`: `4/5` overlapping clips (`0.80`)

### Top Clips

#### auto

- `17:40.72 - 18:16.46` | score `84.96` | reasons: good speech density for a short clip, has speaker dynamics or conversational turns, starts with a stronger hook signal
- `11:56.88 - 12:27.68` | score `82.58` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `22:37.76 - 23:08.12` | score `80.8` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `10:12.83 - 10:48.78` | score `80.66` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, ends with a clearer payoff signal
- `13:06.56 - 13:44.74` | score `80.18` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal

#### manual_generic

- `17:40.72 - 18:16.46` | score `82.33` | reasons: contains punchy or emotional language, good speech density for a short clip, starts with a stronger hook signal
- `11:56.88 - 12:27.68` | score `79.86` | reasons: contains punchy or emotional language, contains high-importance transcript moments, good speech density for a short clip
- `20:43.05 - 21:13.50` | score `78.0` | reasons: contains punchy or emotional language, starts with a stronger hook signal, contains high-importance transcript moments
- `10:12.83 - 10:48.78` | score `77.46` | reasons: contains punchy or emotional language, good speech density for a short clip, ends with a clearer payoff signal
- `22:39.10 - 23:23.72` | score `76.91` | reasons: contains punchy or emotional language, good speech density for a short clip, contains high-importance transcript moments

#### compare_podcast

- `17:40.72 - 18:16.46` | score `84.96` | reasons: good speech density for a short clip, has speaker dynamics or conversational turns, starts with a stronger hook signal
- `11:56.88 - 12:27.68` | score `82.58` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `22:37.76 - 23:08.12` | score `80.8` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `10:12.83 - 10:48.78` | score `80.66` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, ends with a clearer payoff signal
- `13:06.56 - 13:44.74` | score `80.18` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal

### Rendering

- `auto`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`82`
- `manual_generic`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`69`
- `compare_podcast`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`82`

### Findings

- Auto classification missed the expected type: podcast vs generic.
- Subtitle checker reported warnings (10), but no hard failure.
- Transcript/diarization diagnostics raised flags: expected_single_speaker_but_detected_many
- All rendered benchmark scenarios produced the requested subtitled clips.

## Roman Giertych commentary essay

- Expected content type: `generic`
- Expected speaker mode: `single`
- Status: `completed`
- Source URL: https://www.youtube.com/watch?v=FheyKl2x73A
- Description: Single-narrator political commentary / explainer essay with archival visuals. Treated as generic/commentary-like for the current taxonomy.
- Notes: Added as a generic/commentary benchmark. It resembles a narrated commentary video more than a dialogue-driven podcast.
- Transcript preparation: `reused_local_transcript`
- Heatmap source: `existing_heatmap`

### Transcript / Diarization

- Segments: `439`
- Speakers: `4`
- Speaker switches: `288`
- Dominant speaker ratio: `0.2825`
- Diarization status: `applied`
- Fallback used: `False`
- Diagnostic flags: `expected_single_speaker_but_detected_many`

### Subtitle Checker

- Mode: `local_only`
- Status: `warning`
- Score: `100.0`
- Issues: `0` errors, `0` warnings

### Strategy Scenarios

| Scenario | Arg | Detected | Confidence | Override ok | Render success | Top-5 overlap note |
| --- | --- | --- | ---: | --- | --- | --- |
| auto | `auto` | `generic` | 0.53 | False | True | - |
| manual_generic | `generic` | `generic` | 1.00 | True | True | 5/5 overlap vs auto |
| compare_podcast | `podcast` | `podcast` | 1.00 | True | True | 3/5 overlap vs auto |

### Pairwise Overlap

- `auto` vs `manual_generic`: `5/5` overlapping clips (`1.00`)
- `auto` vs `compare_podcast`: `3/5` overlapping clips (`0.60`)
- `manual_generic` vs `compare_podcast`: `3/5` overlapping clips (`0.60`)

### Top Clips

#### auto

- `19:54.36 - 20:31.18` | score `78.74` | reasons: contains punchy or emotional language, good speech density for a short clip, starts with a stronger hook signal
- `19:09.66 - 19:41.82` | score `78.04` | reasons: contains punchy or emotional language, good speech density for a short clip, starts with a stronger hook signal
- `00:53.90 - 01:26.86` | score `72.99` | reasons: contains punchy or emotional language, starts with a stronger hook signal, good speech density for a short clip
- `11:14.48 - 11:53.92` | score `72.06` | reasons: contains punchy or emotional language, good speech density for a short clip, contains high-importance transcript moments
- `12:20.16 - 12:56.24` | score `71.5` | reasons: contains punchy or emotional language, good speech density for a short clip, contains high-importance transcript moments

#### manual_generic

- `19:54.36 - 20:31.18` | score `78.74` | reasons: contains punchy or emotional language, good speech density for a short clip, starts with a stronger hook signal
- `19:09.66 - 19:41.82` | score `78.04` | reasons: contains punchy or emotional language, good speech density for a short clip, starts with a stronger hook signal
- `00:53.90 - 01:26.86` | score `72.99` | reasons: contains punchy or emotional language, starts with a stronger hook signal, good speech density for a short clip
- `11:14.48 - 11:53.92` | score `72.06` | reasons: contains punchy or emotional language, good speech density for a short clip, contains high-importance transcript moments
- `12:20.16 - 12:56.24` | score `71.5` | reasons: contains punchy or emotional language, good speech density for a short clip, contains high-importance transcript moments

#### compare_podcast

- `19:09.66 - 20:01.48` | score `82.71` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `00:53.90 - 01:26.86` | score `77.1` | reasons: has speaker dynamics or conversational turns, starts with a stronger hook signal, good speech density for a short clip
- `11:14.48 - 11:53.92` | score `74.25` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk
- `04:13.30 - 04:54.70` | score `74.23` | reasons: good speech density for a short clip, has speaker dynamics or conversational turns, stays relatively clear despite overlap risk
- `13:39.04 - 14:30.56` | score `72.62` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk

### Rendering

- `auto`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`0`
- `manual_generic`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`0`
- `compare_podcast`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`0`

### Findings

- Auto classification matched the expected type (generic) with confidence 0.527.
- Subtitle checker reported warnings (0), but no hard failure.
- Transcript/diarization diagnostics raised flags: expected_single_speaker_but_detected_many
- All rendered benchmark scenarios produced the requested subtitled clips.

## Putin parade commentary

- Expected content type: `generic`
- Expected speaker mode: `single`
- Status: `completed`
- Source URL: https://www.youtube.com/watch?v=7t9yv4d318U
- Description: Single-host current-events commentary about Russia's parade and Ukraine. Treated as generic/commentary-like for the current taxonomy.
- Notes: Added as a generic/commentary benchmark. Useful for testing news-like monologue material without introducing a new taxonomy class yet.
- Transcript preparation: `reused_local_transcript`
- Heatmap source: `existing_heatmap`

### Transcript / Diarization

- Segments: `229`
- Speakers: `4`
- Speaker switches: `148`
- Dominant speaker ratio: `0.31`
- Diarization status: `applied`
- Fallback used: `False`
- Diagnostic flags: `expected_single_speaker_but_detected_many`

### Subtitle Checker

- Mode: `local_only`
- Status: `warning`
- Score: `100.0`
- Issues: `0` errors, `0` warnings

### Strategy Scenarios

| Scenario | Arg | Detected | Confidence | Override ok | Render success | Top-5 overlap note |
| --- | --- | --- | ---: | --- | --- | --- |
| auto | `auto` | `podcast` | 0.83 | False | True | - |
| manual_generic | `generic` | `generic` | 1.00 | True | True | 4/5 overlap vs auto |
| compare_podcast | `podcast` | `podcast` | 1.00 | True | True | 5/5 overlap vs auto |

### Pairwise Overlap

- `auto` vs `manual_generic`: `4/5` overlapping clips (`0.80`)
- `auto` vs `compare_podcast`: `5/5` overlapping clips (`1.00`)
- `manual_generic` vs `compare_podcast`: `4/5` overlapping clips (`0.80`)

### Top Clips

#### auto

- `06:57.53 - 07:47.13` | score `78.98` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `10:08.63 - 10:39.61` | score `74.61` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk
- `00:55.26 - 01:34.25` | score `74.36` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk
- `12:31.65 - 13:06.09` | score `73.46` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk
- `14:34.63 - 15:19.99` | score `70.39` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk

#### manual_generic

- `06:57.53 - 07:47.13` | score `74.92` | reasons: contains punchy or emotional language, good speech density for a short clip, starts with a stronger hook signal
- `00:55.26 - 01:34.25` | score `73.73` | reasons: contains punchy or emotional language, contains high-importance transcript moments, good speech density for a short clip
- `10:08.63 - 10:39.61` | score `73.31` | reasons: contains punchy or emotional language, good speech density for a short clip, contains high-importance transcript moments
- `12:31.65 - 13:06.09` | score `71.15` | reasons: contains punchy or emotional language, good speech density for a short clip, contains high-importance transcript moments
- `03:28.09 - 04:02.47` | score `68.88` | reasons: contains punchy or emotional language, good speech density for a short clip, contains high-importance transcript moments

#### compare_podcast

- `06:57.53 - 07:47.13` | score `78.98` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `10:08.63 - 10:39.61` | score `74.61` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk
- `00:55.26 - 01:34.25` | score `74.36` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk
- `12:31.65 - 13:06.09` | score `73.46` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk
- `14:34.63 - 15:19.99` | score `70.39` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, stays relatively clear despite overlap risk

### Rendering

- `auto`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`11`
- `manual_generic`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`11`
- `compare_podcast`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`11`

### Findings

- Auto classification missed the expected type: podcast vs generic.
- Subtitle checker reported warnings (0), but no hard failure.
- Transcript/diarization diagnostics raised flags: expected_single_speaker_but_detected_many
- All rendered benchmark scenarios produced the requested subtitled clips.

## Magenta Team two-person podcast

- Expected content type: `podcast`
- Expected speaker mode: `multi`
- Status: `completed`
- Source URL: https://www.youtube.com/watch?v=9Qa-szUnNaY
- Description: Short branded two-person conversation episode from Magenta Team. Suitable as a real multi-speaker podcast benchmark within the current taxonomy.
- Notes: Added to validate whether the classifier and diarization behave better on a true conversation than on commentary-like monologues.
- Transcript preparation: `reused_local_transcript`
- Heatmap source: `existing_heatmap`

### Transcript / Diarization

- Segments: `388`
- Speakers: `4`
- Speaker switches: `191`
- Dominant speaker ratio: `0.3557`
- Diarization status: `applied`
- Fallback used: `False`

### Subtitle Checker

- Mode: `local_only`
- Status: `warning`
- Score: `88.0`
- Issues: `0` errors, `3` warnings
- Top issue codes: `TOO_MANY_WORDS_FOR_DURATION` x2, `DUPLICATED_ADJACENT_TEXT` x1

### Strategy Scenarios

| Scenario | Arg | Detected | Confidence | Override ok | Render success | Top-5 overlap note |
| --- | --- | --- | ---: | --- | --- | --- |
| auto | `auto` | `generic` | 0.50 | False | True | - |
| manual_podcast | `podcast` | `podcast` | 1.00 | True | True | 5/5 overlap vs auto |
| compare_generic | `generic` | `generic` | 1.00 | True | True | 5/5 overlap vs auto |

### Pairwise Overlap

- `auto` vs `manual_podcast`: `5/5` overlapping clips (`1.00`)
- `auto` vs `compare_generic`: `5/5` overlapping clips (`1.00`)
- `manual_podcast` vs `compare_generic`: `5/5` overlapping clips (`1.00`)

### Top Clips

#### auto

- `00:42.70 - 01:27.20` | score `81.0` | reasons: contains punchy or emotional language, starts with a stronger hook signal, ends with a clearer payoff signal
- `02:10.86 - 02:46.86` | score `80.25` | reasons: contains punchy or emotional language, good speech density for a short clip, starts with a stronger hook signal
- `07:49.37 - 08:26.37` | score `79.34` | reasons: contains punchy or emotional language, contains high-importance transcript moments, starts with a stronger hook signal
- `04:44.78 - 05:16.86` | score `78.38` | reasons: contains punchy or emotional language, contains high-importance transcript moments, starts with a stronger hook signal
- `06:32.44 - 07:05.17` | score `77.65` | reasons: contains punchy or emotional language, contains high-importance transcript moments, starts with a stronger hook signal

#### manual_podcast

- `02:10.86 - 02:46.86` | score `85.18` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `00:48.36 - 01:27.20` | score `84.89` | reasons: has speaker dynamics or conversational turns, good speech density for a short clip, starts with a stronger hook signal
- `07:49.37 - 08:26.37` | score `81.07` | reasons: has speaker dynamics or conversational turns, starts with a stronger hook signal, good speech density for a short clip
- `04:44.78 - 05:16.86` | score `79.5` | reasons: has speaker dynamics or conversational turns, starts with a stronger hook signal, good speech density for a short clip
- `06:32.44 - 07:05.17` | score `79.05` | reasons: has speaker dynamics or conversational turns, starts with a stronger hook signal, good speech density for a short clip

#### compare_generic

- `00:42.70 - 01:27.20` | score `81.0` | reasons: contains punchy or emotional language, starts with a stronger hook signal, ends with a clearer payoff signal
- `02:10.86 - 02:46.86` | score `80.25` | reasons: contains punchy or emotional language, good speech density for a short clip, starts with a stronger hook signal
- `07:49.37 - 08:26.37` | score `79.34` | reasons: contains punchy or emotional language, contains high-importance transcript moments, starts with a stronger hook signal
- `04:44.78 - 05:16.86` | score `78.38` | reasons: contains punchy or emotional language, contains high-importance transcript moments, starts with a stronger hook signal
- `06:32.44 - 07:05.17` | score `77.65` | reasons: contains punchy or emotional language, contains high-importance transcript moments, starts with a stronger hook signal

### Rendering

- `auto`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`14`
- `manual_podcast`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`14`
- `compare_generic`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`14`

### Findings

- Auto classification missed the expected type: generic vs podcast.
- Subtitle checker reported warnings (3), but no hard failure.
- All rendered benchmark scenarios produced the requested subtitled clips.

## Canva presentation tutorial

- Expected content type: `tutorial`
- Expected speaker mode: `single`
- Status: `completed`
- Source URL: https://www.youtube.com/watch?v=t9ge2mWHoxU
- Description: Single-presenter Canva screencast on making engaging presentations. Suitable as a tutorial benchmark with screen-focused visuals and instructional speech.
- Notes: Added to test the tutorial path before tuning classifier or strategy weights.
- Transcript preparation: `reused_local_transcript`
- Heatmap source: `existing_heatmap`

### Transcript / Diarization

- Segments: `826`
- Speakers: `4`
- Speaker switches: `524`
- Dominant speaker ratio: `0.2724`
- Diarization status: `applied`
- Fallback used: `False`
- Diagnostic flags: `expected_single_speaker_but_detected_many`

### Subtitle Checker

- Mode: `local_only`
- Status: `warning`
- Score: `96.0`
- Issues: `0` errors, `1` warnings
- Top issue codes: `MODEL_ARTIFACT` x1

### Strategy Scenarios

| Scenario | Arg | Detected | Confidence | Override ok | Render success | Top-5 overlap note |
| --- | --- | --- | ---: | --- | --- | --- |
| auto | `auto` | `generic` | 0.51 | False | True | - |
| manual_tutorial | `tutorial` | `tutorial` | 1.00 | True | True | 3/5 overlap vs auto |
| compare_generic | `generic` | `generic` | 1.00 | True | True | 5/5 overlap vs auto |

### Pairwise Overlap

- `auto` vs `manual_tutorial`: `3/5` overlapping clips (`0.60`)
- `auto` vs `compare_generic`: `5/5` overlapping clips (`1.00`)
- `manual_tutorial` vs `compare_generic`: `3/5` overlapping clips (`0.60`)

### Top Clips

#### auto

- `07:31.31 - 08:07.91` | score `73.31` | reasons: strong heatmap support, contains high-importance transcript moments, contains punchy or emotional language
- `09:05.65 - 09:42.82` | score `72.88` | reasons: strong heatmap support, contains high-importance transcript moments, good speech density for a short clip
- `09:56.17 - 10:31.10` | score `71.49` | reasons: strong heatmap support, contains punchy or emotional language, contains high-importance transcript moments
- `25:46.46 - 26:22.20` | score `71.36` | reasons: strong heatmap support, contains high-importance transcript moments, good speech density for a short clip
- `24:58.92 - 25:33.52` | score `66.0` | reasons: strong heatmap support, contains punchy or emotional language, contains high-importance transcript moments

#### manual_tutorial

- `07:31.31 - 08:07.91` | score `67.14` | reasons: strong heatmap support, stays relatively clear despite overlap risk, good speech density for a short clip
- `25:46.46 - 26:22.20` | score `66.87` | reasons: strong heatmap support, stays relatively clear despite overlap risk, good speech density for a short clip
- `09:56.17 - 10:31.10` | score `66.6` | reasons: strong heatmap support, stays relatively clear despite overlap risk, good speech density for a short clip
- `17:25.96 - 18:01.94` | score `66.07` | reasons: good speech density for a short clip, stays relatively clear despite overlap risk, fits a strong short-form duration window
- `26:55.86 - 27:31.62` | score `64.9` | reasons: strong heatmap support, good speech density for a short clip, stays relatively clear despite overlap risk

#### compare_generic

- `07:31.31 - 08:07.91` | score `73.31` | reasons: strong heatmap support, contains high-importance transcript moments, contains punchy or emotional language
- `09:05.65 - 09:42.82` | score `72.88` | reasons: strong heatmap support, contains high-importance transcript moments, good speech density for a short clip
- `09:56.17 - 10:31.10` | score `71.49` | reasons: strong heatmap support, contains punchy or emotional language, contains high-importance transcript moments
- `25:46.46 - 26:22.20` | score `71.36` | reasons: strong heatmap support, contains high-importance transcript moments, good speech density for a short clip
- `24:58.92 - 25:33.52` | score `66.0` | reasons: strong heatmap support, contains punchy or emotional language, contains high-importance transcript moments

### Rendering

- `auto`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`0`
- `manual_tutorial`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`0`
- `compare_generic`: render_success=`True`, face_tracking_success=`5`, center_fallback=`0`, zoom_samples=`0`

### Findings

- Auto classification missed the expected type: generic vs tutorial.
- Subtitle checker reported warnings (1), but no hard failure.
- Transcript/diarization diagnostics raised flags: expected_single_speaker_but_detected_many
- Face-aware rendering completed, but actual face detections were sparse (1/1076 sampled checks), so this benchmark does not strongly validate facecam tracking quality.
- All rendered benchmark scenarios produced the requested subtitled clips.

## Human Review

- Fill in `benchmarks\human_review_template.csv` with `human_relevance_score`, `human_boundary_score`, `human_crop_score` and notes for each rendered clip.

## Recommendation

- Next step: `improve_classifier`
- Title: Improve the heuristic content classifier
- Why: Auto classification accuracy is only 33% across the tested materials, so routing errors are likely to dominate downstream quality.
