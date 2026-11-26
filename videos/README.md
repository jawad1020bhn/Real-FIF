# Videos — harness projects

This folder contains generated reel projects, a reusable scaffold, and one retained reference example. The generic harness creates and renders projects from the repository root; see the root `README.md`.

## Projects

| Path | Role |
|---|---|
| `videos/_template/` | Scaffold for new projects. `input/` is for user audio; generated `*-smoke/` projects are ignored. |
| `videos/quran-reel-ash-sharh/` | Reference example for Arabic RTL typography, full tashkeel, deterministic GSAP timelines, offline assets, and mastered recitation audio. Do not edit it for new reels. |

Old binary/database/promo assets were removed during the generic cleanup. Rendered MP4s and generated per-project QA/audio/frames are build artifacts and are excluded from Git.

## Create a reel

From the repository root:

```bash
npm run reel -- --lang ar --project videos/my-ar-reel --demo --offline
npm run reel -- --lang en --project videos/my-en-reel --demo --offline
npm run check -- --project videos/my-ar-reel
```

Replace `--demo` with `--input /path/to/voice.wav` for real audio. `--offline` uses reviewed `config/words.<lang>.example.json` timings because Hugging Face model weights are not cached in this sandbox. Once weights are available, use `--align-backend whisperx` or `faster-whisper`.

## Project anatomy

```text
<project>/
  input/                user audio (or generated demo WAV)
  audio/clean.wav       silence-cut, loudness-normalised audio
  audio/edits.json      cut ranges + remap contract
  words.json            reviewed word timings
  captions.srt          subtitles
  index.html            generated HyperFrames composition
  hyperframes.json      composition manifest
  assets/               vendored GSAP, fonts, font licences, local audio.wav
  render.json           renderer backend + output metadata
  qa/report.md          human QA report
  qa/contact-sheet.jpg  sampled frames from the actual MP4
  reel-state.json       stage, paths, approvals, QA, cost
```

The renderer is HyperFrames `0.9.100` with headless Chromium supplied by `@sparticuz/chromium`; local FFmpeg/ffprobe come from pinned npm installers. A Pillow frame renderer is available as a Chrome-less fallback. All assets are local, so renders are deterministic and keyless.

## Reference example

`videos/quran-reel-ash-sharh/` keeps its original rendered MP4s, eight scene illustrations, recitation audio, Scheherazade New / Amiri fonts, and SIL OFL licence files. It is documentation, not an input to the generic pipeline. Qur'anic recitation should use reviewed text and manual boundaries; generic forced alignment is unreliable for full tashkeel and tajwid.

## Verification

```bash
npm run doctor
npm run check -- --project videos/my-ar-reel
npm run qa -- --project videos/my-ar-reel --out out/reel-ar.mp4 --lang ar
```

No API keys, no paid calls, no publishing. Outputs are drafts only.
