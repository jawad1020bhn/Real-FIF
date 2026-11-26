# Keyless Reel Harness

A bilingual (`ar` / `en`), offline-first short-form video factory. Start from voice audio, cut silence, align words, render word-timed RTL/LTR captions with one paused GSAP timeline, and finish with a deterministic MP4, SRT, contact sheet, QA report, and state file. **No API keys, no paid calls, no publishing.**

This repository is now a generic harness. Research and one Arabic RTL reference example are retained; the old database, binaries, and promo assets were removed.

## What is installed

| Layer | Tools |
|---|---|
| Renderer | HyperFrames `0.9.100` (Apache-2.0), GSAP `3.15.1`, local fonts, local audio |
| Optional motion / React | anime.js, mo.js, Rough.js, Three.js, Remotion + `@remotion/gsap` + `@remotion/three` (Remotion is opt-in and never mixed with HyperFrames in one project) |
| Local FFmpeg | `@ffmpeg-installer/ffmpeg`, `@ffprobe-installer/ffprobe`, `ffmpeg-skill`, `imageio-ffmpeg` |
| Audio / ASR | Auto-Editor `29.3.1`, WhisperX `3.8.6`, faster-whisper `1.2.1`, CTranslate2, Torch/Torchaudio, soundfile |
| Offline rendering | Pillow + `arabic-reshaper` + `python-bidi` fallback |
| Claude Code layer | 7 local orchestration wrappers + 22 pinned, text-only upstream `SKILL.md` snapshots |
| Prompts | `prompts/` — bilingual Stack E, scriptwriting, visual direction, quality gate |

Pinned versions live in [`package.json`](package.json), [`package-lock.json`](package-lock.json), and [`requirements.txt`](requirements.txt). Generated `node_modules/`, `.venv/`, model weights, and output MP4s are excluded from Git.

## Quick start

```bash
# 1. Node dependencies (also installs local ffmpeg / ffprobe / Chromium)
npm install

# 2. Python dependencies in a venv (system pip is externally managed here)
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

# 3. Verify the keyless toolchain
npm run doctor

# 4. Deterministic bilingual smoke tests — no input file and no model downloads
npm run reel -- --lang ar --project videos/ar-reel --demo --offline
npm run reel -- --lang en --project videos/en-reel --demo --offline

# 5. HyperFrames lint + runtime + layout + contrast + craft gate
npm run check -- --project videos/ar-reel
npm run check -- --project videos/en-reel

# 6. Live test dashboard (opens /test/ in the preview)
npm run test:serve
```

For real audio:

```bash
npm run reel -- --lang ar --project videos/my-reel \
  --input /path/to/voice.wav --offline
```

`--offline` uses reviewed `config/words.<lang>.example.json` timings. Once model weights are cached in `models/`, drop `--offline` and use `--align-backend whisperx` (or `faster-whisper`). See [`models/README.md`](models/README.md) and [`docs/INSTALL.md`](docs/INSTALL.md) for exactly what worked and failed in this sandbox.

## Language switch

| Flag | Direction | Font | Alignment | Caption policy |
|---|---|---|---|---|
| `--lang ar` | RTL (strict) | Scheherazade New / Amiri | `jonatasgrosman/wav2vec2-large-xlsr-53-arabic` | full shaped line, active word highlighted inside it, `<bdi>` for Latin/numbers |
| `--lang en` | LTR | DejaVu Sans | `WAV2VEC2_ASR_BASE_960H` | standard word-timed karaoke line |

Arabic keeps tashkeel in `display` and strips it in `align`. One speaker uses no diarization and no HF token. Reviewed text always wins over ASR output.

## Pipeline — Stack E

```text
input audio
  → clean (FFmpeg silencedetect + loudnorm, edits.json)
  → align (WhisperX / faster-whisper / offline words.json)
  → compose (one paused GSAP timeline, local assets, RTL/LTR)
  → render (HyperFrames, or Pillow fallback without Chrome)
  → qa (ffprobe, loudness, blackdetect, contact sheet, report)
  → out/reel-<lang>.mp4 + captions.srt + reel-state.json
```

`npm run reel` is the single orchestrator. It writes `reel-state.json` after every stage and stops on failure. Stage scripts can also be run individually: `clean`, `align`, `compose`, `render`, `qa`. Use `npm run reel -- --help` for all flags.

## Outputs

| File | Meaning |
|---|---|
| `out/reel-ar.mp4`, `out/reel-en.mp4` | Draft H.264/AAC vertical MP4s (ignored by Git) |
| `<project>/captions.srt` | Subtitles; Arabic lines carry RLE/PDF isolation |
| `<project>/words.json` | Reviewed display/align text, timings, scores, lines |
| `<project>/audio/edits.json` | Silence cuts and loudness metadata; remap contract |
| `<project>/index.html`, `hyperframes.json` | Generated HyperFrames composition and manifest |
| `<project>/render.json` | Renderer backend, output size, duration, binaries |
| `<project>/qa/report.md`, `report.json`, `contact-sheet.jpg` | Machine + human QA |
| `<project>/reel-state.json` | Stage, paths, approvals, QA, cost |

## Commands

| Command | Purpose |
|---|---|
| `npm run doctor` | Node/Python/binaries/module/package/model/key checks → `reports/doctor.json` |
| `npm run reel -- --lang ar|en ...` | Full pipeline with file-based stage handoffs |
| `npm run check -- --project <dir>` | HyperFrames lint/runtime/layout/motion/contrast/craft/audio gate |
| `npm run test:serve` | Static live preview; open `/test/` for videos, contact sheets, QA reports |
| `npm run clean/align/compose/render/qa` | Individual stage |
| `npm run models:ar`, `npm run models:en` | One-time weight prefetch on a machine with Hugging Face access |
| `npm run skills:list` | Local wrappers + pinned upstream skill catalogue |
| `npm run skills:audit` | Pattern audit of vendored `SKILL.md` text |
| `npm run skills:enable -- --enable <slug>` | Enable one pinned upstream skill |
| `npm run skills:all` | Enable all 22 upstream snapshots (higher context cost) |

## Repository map

```text
.claude/skills/        local authoritative wrappers
config/                brand, languages, copy, facts, example words, state contract
docs/                  architecture, install reality, skill/security guide
models/                weight cache (empty here; git-ignored)
out/                   rendered MP4s (git-ignored)
prompts/               highest-quality bilingual prompts
research/              original 2026-11-25 tool research + Stack E blueprint
scripts/               doctor, orchestrator, stage scripts, QA, skill enable
templates/hyperframes/ offline HTML/CSS/GSAP template + fonts + licences
test/                   live test dashboard (static HTML)
vendor/skills/          22 pinned text-only upstream SKILL.md snapshots
videos/_template/       scaffold + ignored smoke-test projects
videos/quran-reel-ash-sharh/  retained RTL reference example
```

## Quality and safety rules

- One orchestrator, one renderer, one paused timeline. No independent clocks, unseeded randomness, or network assets.
- Silence cuts happen before alignment; any later cut must be remapped through `edits.json`.
- Audio is muxed once. FFmpeg after render is for probe, loudness, snapshots, and QA only.
- `config/facts.json` is the only source of truth. Missing values become `[placeholder]`.
- Platform-safe band: y 288–1248, x 120–888; below y 840 TikTok narrows the right edge to 780. Arabic captions sit 20 px higher.
- HyperFrames `lint` and `check` pass with 0 errors/0 warnings on both smoke tests; harness QA passes 24/24 (`ar`) and 23/23 (`en`).
- All outputs are drafts. Publishing, posting, and paid calls require separate explicit human approval.

## Licence notes

HyperFrames is Apache-2.0. FFmpeg binaries are LGPL/GPL by build. GSAP is free under its Standard no-charge licence but is **not OSI open source**. Remotion is source-available and requires a company licence for larger teams. Scheherazade New and Amiri are SIL OFL; DejaVu has its own permissive licence. Licence files sit beside the vendored fonts.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — pipeline, contracts, bilingual logic
- [`docs/INSTALL.md`](docs/INSTALL.md) — exact sandbox install/model-fetch results
- [`docs/SKILLS.md`](docs/SKILLS.md) — skill catalogue, pinning, security policy
- [`docs/TESTING.md`](docs/TESTING.md) — post-merge acceptance checklist
- [`test/index.html`](test/index.html) — live test dashboard (`npm run test:serve`, open `/test/`)
- [`prompts/README.md`](prompts/README.md) — copy-ready high-quality prompts
- [`research/claude-code-reels-research.md`](research/claude-code-reels-research.md) — source research
- [`CLAUDE.md`](CLAUDE.md) — always-on rules for Claude Code
