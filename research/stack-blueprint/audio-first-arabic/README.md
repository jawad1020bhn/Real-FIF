# Audio-first Arabic reel factory — blueprint

Research output complementing [Section 9 of the report](../../claude-code-reels-research.md) and [`audio-factory-matrix.csv`](../../audio-factory-matrix.csv). **Nothing here is installed**; these are copy-ready specs for Stack E (`input.mp3` → silence cuts → Arabic word timings → RTL karaoke captions → `out/reel.mp4`).

| File | Purpose |
|---|---|
| [`PROMPT.ar.md`](PROMPT.ar.md) | Hardened Arabic Claude Code prompt (keeps the original's 5 stages, approvals, `npm run reel`, Arabic README; adds 8 corrections) + a diff table explaining every change |
| [`words.schema.json`](words.schema.json) | The single handoff contract between WhisperX, the caption component and the scenes |
| [`words.example.json`](words.example.json) | Neutral Arabic example with `display` (tashkeel) vs `align` (stripped), a `<bdi>` number, and an interpolated `score: 0` word |
| [`rtl-caption.example.html`](rtl-caption.example.html) | Minimal deterministic RTL karaoke block: `dir="rtl"` wrapper, whole-line highlighting, `<bdi>`, `renderFrame(t)` with no wall clock |

## What is actually added to the stack

The 12-tool list contributes a **sixth stack, not a replacement**: the earlier stacks start from a topic/script; this one starts from a voice recording. Adopt:

- **Auto-Editor** 29.3.1 (Unlicense) or `ffmpeg-skill`'s `silence.py` — but cut **before** alignment, keep `edits.json`, and remap times if anything is cut later.
- **WhisperX** 3.8.6 (BSD-2-Clause) with `--language ar` and `align_model=jonatasgrosman/wav2vec2-large-xlsr-53-arabic`. Python 3.10–3.13. One speaker → no diarization → no HF token. Strip tashkeel for alignment, keep it for display; mark unalignable words `score: 0`.
- **HyperFrames** 0.9.99 (Apache-2.0, already in `videos/`) as the default timeline owner: it pauses and seeks GSAP / anime.js / Lottie / Three.js / WAAPI timelines per frame. **Remotion** 4.0.547 is opt-in only (source-available; free ≤3 employees) and then `@remotion/gsap` is mandatory.
- **GSAP** 3.15.1 (free no-charge, *not* OSI), plus at most one or two of anime.js 4.5.0 / mo.js 1.7.1 / Rough.js 4.6.6 / Three.js 0.187.0 — all driven by frame, never by their own tickers.
- **FFmpeg / `ffmpeg-skill`** for loudness, `ffprobe`, `.srt` and re-frames only — the renderer already muxes audio.
- **Skill wrappers** from the earlier research so the raw tools aren't hand-wired: `kajisho5/{ffmpeg,transcription,subtitle,qc,media-analysis,remotion-ffmpeg}-skill`, `remotion-dev/skills`, `LottieFiles/motion-design-skill`, `iart-ai/tiktok-video-skills` (`caption-animation`), `iart-ai/webgl-animation-skills`.

**Skip for reels:** Manim (+ `adithya-s-k/manim_skill`, `iart-ai/manim-skills`) — math explainers only, exactly as the original prompt says. **Motion Canvas** 3.17.2 (MIT) is optional for step-by-step teaching scenes, not karaoke captions.

## Stage contract (mirrors `reel-orchestrator`)

| # | Stage | Input → output | Gate |
|---:|---|---|---|
| 0 | `doctor` | machine → `doctor.json` (Node, Python 3.10–3.13, ffmpeg/ffprobe, Chrome, pinned versions) | approve installs |
| 1 | clean | `input.mp3` → `audio/clean.wav` + `edits.json` | approve cut plan |
| 2 | align | `clean.wav` + reviewed `copy.json` → `words.json` | approve word list incl. `unverified[]` |
| 3 | compose | `words.json` + `copy.json` → `composition/index.html` + `storyboard.json` | approve storyboard before render |
| 4 | animate | paused timelines seeked to `frame/fps`; `npm run check` determinism guard | no `rAF`/`Date.now`/`performance.now`/`Math.random`/network assets |
| 5 | captions | full shaped RTL lines, active word highlighted inside the line | `dir="rtl"`, `<bdi>` for numbers, safe zones, full tashkeel font |
| 6 | render + QA | → `out/reel.mp4`, `captions.srt`, `qa/report.md`, `qa/contact-sheet.jpg` | ffprobe specs, −14 LUFS, no black/frozen frames, every word readable, RTL highlight direction, no invented numbers (≤2 auto-fix passes) |
| 7 | learn | `reel-state.json`, `winners.md` | drafts only; publish on explicit yes |

`npm run reel` chains 0→6 and stops on the first non-zero exit. `reel-state.json` follows [`../reel-state.example.json`](../reel-state.example.json) so the pipeline survives a session restart.

## Known traps (why the original prompt would fail)

1. `useCurrentFrame()` alone does not frame-lock GSAP/anime.js/mo.js/Three.js — a GSAP timeline can finish during the first captured second and leave black frames ([comparison](https://hyperframes.heygen.com/blog/hyperframes-vs-remotion), [`@remotion/gsap`](https://www.remotion.dev/docs/gsap)).
2. Word spans without `dir="rtl"` reverse the sentence and the karaoke highlight ([OpenMontage #819](https://github.com/calesthio/OpenMontage/issues/819)); isolated Arabic words reshape incorrectly.
3. Forced alignment is language-specific; Arabic uses `jonatasgrosman/wav2vec2-large-xlsr-53-arabic` ([source](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py)). Diacritics, numbers and Latin tokens may not align → `score: 0` + manual review.
4. Cutting silence after timing shifts every caption and scene boundary; keep `edits.json` and remap (`start − Σ removed_before_start`).
5. Remotion/HyperFrames already mux audio — a second FFmpeg mux causes A/V drift.
6. Licensing: Remotion source-available (≤3 employees free), GSAP free but not open source, FFmpeg LGPL/GPL by build, Arabic fonts SIL OFL (add licence files next to vendored `.ttf`).
7. In this sandbox `ffmpeg`/`ffprobe` are **not on PATH** and apt / Chrome CDN / Hugging Face downloads are blocked; use the `HYPERFRAMES_*_PATH` shims documented in `videos/README.md` and pre-seed `models/`.
8. Never let ASR rewrite reviewed text — especially Qur'anic text. No invented statistics: for this repo, on-screen numbers come from the top-level `README.md` or a `config/facts.json` query.

## First test in this repo

`videos/quran-reel-ash-sharh/assets/recitation.wav` is 28.0 s / 48 kHz stereo and already has eight verse boundaries (waveform analysis, documented in that project's README), eight scene images and vendored Scheherazade New / Amiri fonts. It is the ideal `input.mp3` — but Qur'anic recitation with full tashkeel/tajwid is the hardest case for generic forced alignment. Use the fixed reviewed verse text as the alignment target (or keep the existing manual boundaries), never let the model correct it, and verify word times by eye. For a first smoke test use the neutral line in `words.example.json`.

Copy the fonts into the new project's `assets/fonts/` **with their SIL OFL licence files**, keep existing `videos/*/renders/` untouched, and write the new reel to its own `videos/<new-project>/` folder.
