---
name: ffmpeg-qc
description: Use when probing, validating, loudness-checking, contact-sheeting, captioning, re-framing, or diagnosing a rendered MP4. Wraps the local FFmpeg/ffprobe binaries and the ffmpeg-skill approach with no API keys.
---

# FFmpeg QC

`ffmpeg` and `ffprobe` come from pinned npm installers; `scripts/lib/paths.mjs` and `scripts/lib/paths.py` resolve them. There is no PATH dependency and no network call.

## What the harness already does

- `npm run clean` uses FFmpeg `silencedetect` to cut silence before alignment and writes `audio/edits.json`.
- `npm run align` writes `captions.srt`.
- HyperFrames muxes the local `<audio>` tag once; the Pillow fallback muxes once in the final FFmpeg command.
- `npm run qa` runs `ffprobe`, `loudnorm`, `blackdetect`, and a `tile` contact sheet, then writes `qa/report.md` and `qa/report.json`.

## Rules

1. **Do not mux twice.** Use FFmpeg after render only for probe, loudness, platform re-frames, snapshots, and verification.
2. **Target loudness:** −14 LUFS / −1.5 dBTP for social video. `qa.py` reports `input_i`; large deviations are warnings.
3. **Verify:** 1080×1920, expected fps, H.264, one AAC audio stream, duration within ±0.75 s, file >100 KiB.
4. **Visual QA:** sample `qa/contact-sheet.jpg` from the actual MP4, not from source HTML. Check black frames, frozen frames, safe zones, caption readability, and RTL/LTR highlight direction.
5. **Caption QC:** SRT must exist; Arabic lines need RLE/PDF isolation. Unverified word timings (`score: 0`) must be reviewed by a human.
6. **No invented values:** if a number is not in `config/facts.json`, do not put it in a caption, filename, or QA claim.

## Useful manual commands

```bash
npm run qa -- --project videos/ar-reel --out out/reel-ar.mp4 --lang ar
node -e "console.log(require('@ffmpeg-installer/ffmpeg').path)"
node -e "console.log(require('@ffprobe-installer/ffprobe').path)"
```

The pinned upstream `ffmpeg-skill` description is available via `npm run skills:enable -- --enable ffmpeg-skill-ffmpeg-skill`. Only its SKILL.md text is vendored; its MCP server and scripts are not installed here.
