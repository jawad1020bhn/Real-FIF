# Review copy — 45s harness promo

Watch this file before any merge decision:

- `renders/harness-promo-45s.mp4` — 45.00s, 1080×1920, 30fps, H.264/AAC, local narration + synthetic bed.
- `qa/contact-sheet-full.jpg` — eight frames sampled from the encoded MP4.
- `reports/harness-promo-contact-sheet.jpg` — same full-reel sheet at the repository report path.
- `qa/report.md` — machine/human QA report.

## What is on screen

Seven deterministic, code-driven HyperFrames scenes, each with a visible library/skill label and real motion:

1. **HyperFrames + GSAP** — paused timeline, grid reveal, three animated pipeline nodes and progress bar.
2. **Audio first** — FFmpeg/ffmpeg-skill waveform, Auto-Editor/WhisperX gating labels, deterministic silence-cut workflow.
3. **anime.js** — staggered cards driven by a paused GSAP timeline and `animeTl.seek()`.
4. **mo.js** — deterministic SVG shape burst and ring via a local frame-locked shim.
5. **Rough.js + Three.js** — hand-drawn pipeline sketch and a rotating WebGL wireframe icosahedron/torus.
6. **Remotion** — a locally rendered 4s `@remotion/three` + `@remotion/gsap` clip embedded in the HyperFrames timeline.
7. **Pillow + QA + skills** — local Arabic-shaped fallback card, strict-check / FFmpeg-QC / skills-audit chips, and the CTA.

Caption states are word-timed from reviewed JSON (70 words, 3 caption lines). Brand, progress, grain and safe-zone chrome are local. No generated photographic backgrounds, no AI stills as primary visuals, no network assets, no independent clocks.

## Stack actually exercised

HyperFrames, GSAP, anime.js, mo.js shim, Rough.js, Three.js, Remotion 4 (`useCurrentFrame`, `useGsapTimeline`, `ThreeCanvas`), FFmpeg/FFprobe, ffmpeg-skill contract/doctor, Pillow, numpy/soundfile, arabic_reshaper/bidi, local fonts, word-timed captions, strict HyperFrames checks, FFmpeg QA, and a skills audit with 22 pinned upstream skill snapshots. Auto-Editor and WhisperX are installed and referenced as gated/offline; no model weights were fetched.

## Verification

- `npm run harness:check`: Lint/Runtime/Layout/Motion/Craft/Audio 0 errors; 128/128 WCAG AA contrast checks.
- `npm run harness:qa`: PASS, 23/23 checks, 1 non-critical warning about silence cuts before alignment (word times come from the reviewed JSON source).
- Strict check report: `.hyperframes/artifacts/checks/6b127f3d-a6aa-402a-84e9-c0bbb884ef9f.json`.
- Final render: `out/harness-promo-45s.mp4`; committed review copy: `renders/harness-promo-45s.mp4`.

## Constraints

No API keys, paid calls, publishing, or invented statistics. `config/facts.json` is empty and is the only facts source. The rejected Surah Ash-Sharh test reel has been removed; this promo does not reuse its scripts, assets, captions, or backgrounds. Merge requires explicit human review and approval.
