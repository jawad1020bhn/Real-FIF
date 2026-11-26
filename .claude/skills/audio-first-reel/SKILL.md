---
name: audio-first-reel
description: Use when a reel starts from a voice recording, recitation, podcast clip, or MP3/WAV and needs silence cuts, word-level timings, word-timed captions, and a deterministic MP4. This is Stack E, now bilingual ar/en.
---

# Audio-first reel — Stack E

Pipeline: `input` → silence cuts → word timings → word-timed captions → one paused-timeline composition → one MP4 + SRT + QA.

## Language switch

| | `ar` (strict default for Arabic) | `en` |
|---|---|---|
| Direction | RTL | LTR |
| Font | Scheherazade New / Amiri | DejaVu Sans |
| Alignment | `jonatasgrosman/wav2vec2-large-xlsr-53-arabic` | `WAV2VEC2_ASR_BASE_960H` |
| Caption line | full shaped Arabic line, highlight inside it | standard word-timed line |
| SRT | RLE/PDF isolation marks | normal |

## Hardened corrections

1. **Cut first, align second.** `audio/edits.json` records every removed range. All later times are on `audio/clean.wav`. If a cut happens after alignment, remap `start_new = start_old − sum(removed_before_start)`.
2. **Arabic alignment:** pass `--language ar` and the Arabic wav2vec2 model explicitly. Keep tashkeel in `display`, strip it in `align`. Mark out-of-vocabulary numbers / Latin tokens `score: 0` and use nearest interpolation. One speaker means **no diarization and no HF token**.
3. **No model rewriting:** the reviewed text is the source of truth. Generic forced alignment is unreliable for full tashkeel and tajwid; use manual boundaries for Qur'anic recitation.
4. **RTL captions:** `dir="rtl"`, `direction:rtl`, `unicode-bidi:isolate`, one full shaped line, active word highlighted inside that line, `<bdi>` for Latin/numbers. Never render isolated Arabic words as independent shaped spans.
5. **Frame-locked motion:** one paused GSAP timeline seeked to `frame/fps`. `useCurrentFrame()` alone is not enough for GSAP, anime.js, mo.js, or Three.js. No independent clocks, randomness, or network assets.
6. **Mux once:** HyperFrames uses the local `<audio>` tag; the Pillow fallback muxes in its final FFmpeg command. Use FFmpeg afterwards only for probe, loudness, contact sheet, and QA.
7. **Model cache:** WhisperX/faster-whisper weights are several GiB. If Hugging Face is blocked, use `--offline`/`--from-json config/words.<lang>.example.json`. See `docs/INSTALL.md`.
8. **QA gate:** duration, 1080×1920, fps, single audio stream, RTL/LTR flags, caption states, black frames, loudness, contact sheet, unverified words. Publishing is never automatic.

## Commands

```bash
npm run doctor
npm run reel -- --lang ar --project videos/ar-reel --demo --offline
npm run reel -- --lang en --project videos/en-reel --demo --offline
npm run reel -- --lang ar --project videos/ar-reel --input path/to/voice.wav --align-backend whisperx
python3 scripts/install-models.py --lang ar   # only on a machine with Hugging Face access
```

Read `research/stack-blueprint/audio-first-arabic/PROMPT.ar.md` for the full Arabic rationale and `prompts/STACK-E.en.md` for the English equivalent.
