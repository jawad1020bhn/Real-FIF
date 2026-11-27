# QA — harness-promo-45s

**Status:** PASS  
**Language:** `en` / `ltr`  
**Renderer:** `hyperframes`  
**Output:** `/home/user/Real-FIF/out/harness-promo-45s.mp4`

## Checks

| | Check | Detail |
|---|---|---|
| PASS | ffmpeg + ffprobe | /home/user/Real-FIF/node_modules/@ffmpeg-installer/linux-x64/ffmpeg / /home/user/Real-FIF/node_modules/@ffprobe-installer/linux-x64/ffprobe |
| PASS | output exists | /home/user/Real-FIF/out/harness-promo-45s.mp4 |
| PASS | output > 100 KiB | 11377 KiB |
| PASS | video stream | 1080x1920 h264 @ 30.00 fps |
| PASS | 1080x1920 vertical | 1080x1920 |
| PASS | H.264 video | h264 |
| PASS | fps matches composition | 30.00 fps / expected 30 |
| PASS | duration matches composition | actual 45.00s / expected 45.00s |
| PASS | audio stream present | aac |
| PASS | audio muxed once | 1 audio stream(s) |
| PASS | words.json direction | ltr |
| PASS | language tag | en |
| PASS | words + lines | 70 words / 3 lines |
| PASS | word scores reviewed | 0 interpolated/unverified word(s) |
| PASS | captions.srt | 11 lines |
| PASS | RTL composition flags | dir="ltr" + direction:ltr |
| PASS | one caption state per word | 70 states / 70 words |
| PASS | full-line highlight | active word highlighted inside the full shaped line |
| PASS | no independent clocks / network assets | clean |
| PASS | no API keys in env | keyless |
| PASS | contact sheet | contact-sheet.jpg (110009 bytes) |
| PASS | no long black frames | 0 black span(s) >= 1s |
| PASS | loudness near -14 LUFS | input_i=-15.2 LUFS |

## Warnings

- Silence cuts happened before alignment; verify all word times are on audio/clean.wav (edits.json).

## Review gates

- Watch the MP4 with sound off: the hook and captions must still be readable.
- For Arabic, verify the highlight travels right-to-left inside a full shaped line.
- Verify no invented numbers: `config/facts.json` is the only source of truth.
- Publishing is a separate, explicit human approval. Never auto-publish.
