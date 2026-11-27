# Keyless Reel Harness — promo reel

A 45 s code-driven showcase of the installed harness. No generated photographic backgrounds: motion, cards, diagrams, waveform, 3D wireframe, Remotion clip, Pillow fallback card and QA cards are all deterministic.

## Rebuild

```bash
npm run harness:build
npm run harness:check
npm run harness:render
npm run harness:qa
```

Or `npm run harness:all`.

The builder uses `scripts/reel.mjs` for doctor/clean/align, `scripts/compose.py` for the baseline assets, then replaces the composition with modular HyperFrames sub-compositions. Audio is a local generated voiceover plus a synthetic numpy/soundfile bed, mixed and loudness-normalised with FFmpeg. No API keys, paid calls, publishing or model-weight fetches.

## Deliverables

- `renders/harness-promo-45s.mp4` — final 45s review copy.
- `renders/REVIEW.md` — review gates and the full stack list.
- `qa/report.md`, `qa/contact-sheet.jpg`, `qa/contact-sheet-full.jpg` — QA and encoded-video contact sheets.
- `reports/harness-promo-contact-sheet.jpg` — repository-level full-reel sheet.

The seven scenes visibly exercise HyperFrames/GSAP, FFmpeg/ffmpeg-skill, anime.js, mo.js, Rough.js/Three.js, Remotion, and Pillow/QA/skills. Pinned skill snapshots live in `.claude/skills/`. Strict HyperFrames checks and `npm run harness:qa` pass; see `renders/REVIEW.md` for exact results.
