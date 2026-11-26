# Architecture — keyless bilingual reel harness

## Goal

Turn one audio file into a deterministic 1080×1920 draft reel, with word-timed captions, one paused-timeline composition, one audio mux, and a machine-readable QA report. The same pipeline supports Arabic (`ar`, strict RTL) and English (`en`, LTR). No API keys, no paid calls, no publishing.

## One orchestrator

`scripts/reel.mjs` is the only top-level command. It writes `reel-state.json` after every stage and stops on failure. Stages communicate through files, not chat memory.

```text
doctor  →  clean  →  align  →  compose  →  render  →  qa
  │         │         │          │           │         └─ qa/report.md, report.json, contact-sheet.jpg
  │         │         │          │           └─ out/reel-<lang>.mp4, render.json
  │         │         │          └─ index.html, hyperframes.json, assets/
  │         │         └─ words.json, captions.srt
  │         └─ audio/clean.wav, audio/edits.json
  └─ reports/doctor.json
```

Run all stages with:

```bash
npm run reel -- --lang ar --project videos/ar-reel --demo --offline
npm run reel -- --lang en --project videos/en-reel --demo --offline
```

`--demo` synthesises a deterministic 10.4 s WAV. `--offline` selects `config/words.<lang>.example.json` because Hugging Face weights are not cached here. For real audio, pass `--input /path/to/voice.wav`; for cached weights, use `--align-backend whisperx` or `faster-whisper`.

## Stage contracts

| Stage | Script | Inputs | Outputs | Rules |
|---|---|---|---|---|
| doctor | `scripts/doctor.mjs` | env, manifests | `reports/doctor.json` | core = Node ≥22, ffmpeg, ffprobe, npm packages, Python modules; warns on missing model cache |
| clean | `scripts/clean.mjs` | input audio | `audio/clean.wav`, `audio/edits.json` | FFmpeg `silencedetect` before alignment; single-pass `loudnorm` toward −14 LUFS; auto-editor is an optional backend |
| align | `scripts/align.mjs` → `align.py` | clean audio / example JSON | `words.json`, `captions.srt` | language-specific model, tashkeel split, `score:0` for unalignable words, reviewed text wins |
| compose | `scripts/compose.mjs` → `compose.py` | `words.json`, `copy.<lang>.json`, `brand.json`, `facts.json`, template | `index.html`, `hyperframes.json`, `assets/` | one paused GSAP timeline, local assets, full-line RTL captions, `<bdi>` isolation |
| render | `scripts/render.mjs` → `render.py` | HyperFrames project | MP4, `render.json` | HyperFrames first; Pillow fallback only if Chrome/render fails; audio muxed once |
| qa | `scripts/qa.mjs` → `qa.py` | MP4 + project files | `qa/report.md`, `report.json`, `contact-sheet.jpg` | ffprobe, loudness, blackdetect, contact sheet, RTL/LTR, determinism, keyless checks |

`npm run check -- --project <dir>` adds HyperFrames' own lint/runtime/layout/motion/contrast/craft/audio gate on the generated HTML.

## Language switching

`config/languages.json` is the switchboard.

| | `ar` | `en` |
|---|---|---|
| Direction | `rtl` | `ltr` |
| Font | Scheherazade New / Amiri (SIL OFL) | DejaVu Sans |
| ASR | `large-v3` | `large-v3` |
| Alignment | `jonatasgrosman/wav2vec2-large-xlsr-53-arabic` | `WAV2VEC2_ASR_BASE_960H` |
| Tashkeel | kept in `display`, stripped in `align` | n/a |
| SRT | RLE `\u202b` + PDF `\u202c` isolation | normal |
| Caption | full shaped line, active word highlighted inside it | full line, active word highlighted inside it |
| Safe band | same platform band, 20 px higher caption | same platform band |

`config/copy.ar.json` and `config/copy.en.json` hold hook, subtitle, outro, CTA, and scene copy. `config/facts.json` is the only source of truth for numbers and claims; it is empty by default. `config/brand.json` holds palette, format, voice, and platform-safe zones.

## Deterministic composition

`templates/hyperframes/index.html` is filled by `compose.py`. It contains one paused GSAP timeline registered as `window.__timelines['main']`; HyperFrames seeks it to film time before each captured frame. No independent clocks, unseeded randomness, free-running loops, or remote assets. The template embeds:

- local `assets/gsap.min.js`, fonts, font licences, and `assets/audio.wav`;
- `data-composition-id`, `data-start`, `data-duration`, `data-width`, `data-height`, `data-fps`;
- caption states that show a **full shaped line** and highlight the active word inside it;
- `<bdi>` for Latin/number tokens;
- platform-safe layout: y 288–1248, x 120–888; below y 840 the right edge narrows to 780;
- progress bar, hook, subtitle, scenes, outro, and CTA on the same timeline.

Caption and scene elements deliberately have **no** `data-start`/`data-end` timing attributes: HyperFrames timed clips would own visibility and conflict with the single GSAP timeline. This also keeps `hyperframes lint` at 0 errors / 0 warnings.

## Stack E corrections implemented

1. Clean silence **before** alignment; `edits.json` records cuts and the remap formula.
2. Arabic alignment model is explicit; tashkeel is display-only; unalignable tokens are `score:0`.
3. One speaker needs no diarization and no HF token.
4. RTL uses `dir="rtl"`, `direction:rtl`, `unicode-bidi:isolate`, full shaped lines, and `<bdi>`.
5. All external animation libraries are optional; one paused timeline is seeked to `frame/fps`.
6. HyperFrames muxes the local `<audio>` tag once; Pillow fallback muxes in its final FFmpeg command. No second mux.
7. Model weights are a separate, explicit prefetch. Offline `--from-json` is the default when `models/` is empty.
8. QA, contact sheet, approval gates, `reel-state.json`, and draft-only publishing are built in.

## Rendering and fallback

`render.py` sets `HYPERFRAMES_FFMPEG_PATH`, `HYPERFRAMES_FFPROBE_PATH`, `HYPERFRAMES_BROWSER_PATH`, and `LD_LIBRARY_PATH` from the pinned npm binaries and locally extracted NSS/NSPR libraries. HyperFrames renders with `--workers 1 --no-browser-gpu --no-best-effort`. If it fails, Pillow renders deterministic PNG frames with `arabic-reshaper` + `python-bidi` and muxes audio once. Both paths produce H.264/AAC MP4.

## QA

`qa.py` checks file size, resolution, fps, H.264, one audio stream, duration, words/lines, direction, unverified word scores, SRT isolation, RTL flags, caption states, full-line highlight, independent clocks, network assets, API keys, contact sheet, black frames, and integrated loudness. `report.md` adds human review gates. Publishing is never automatic.

## Skills and prompts

- `.claude/skills/` — 7 authoritative local wrappers (orchestrator, audio-first, RTL craft, deterministic motion, short-form copy, FFmpeg QC, skill audit).
- `vendor/skills/` — 22 pinned, text-only upstream `SKILL.md` snapshots with `SOURCE.json` provenance. Enable one at a time with `npm run skills:enable -- --enable <slug>`.
- `prompts/` — bilingual Stack E, scriptwriting, visual direction, and quality-gate prompts.
- `CLAUDE.md` — always-on rules; outranks any vendored skill.

## Generated artifacts

`node_modules/`, `.venv/`, `models/*`, `out/`, `reports/`, `videos/_template/*-smoke/`, and per-project `audio/`, `qa/`, `frames/`, `renders/` are ignored. Reproducibility comes from `package.json`, `package-lock.json`, `requirements.txt`, `config/`, `templates/`, and `scripts/`.

## Verified smoke tests in this sandbox

| Language | Align | Renderer | Harness QA | HyperFrames check |
|---|---|---|---|---|
| `ar` | `from-json` (11 words) | HyperFrames | 24/24, 0 warnings | 0 errors / 0 warnings, 38/38 WCAG AA |
| `en` | `from-json` (18 words) | HyperFrames | 23/23, 0 warnings | 0 errors / 0 warnings, 47/47 WCAG AA |

Both renders were 10.42 s, 1080×1920, H.264 + AAC, 12 fps for the smoke test (use 30 fps by omitting `--fps 12`). No API keys or model downloads were used.
