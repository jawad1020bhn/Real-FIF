# Final quality gate prompt

```text
Before declaring the reel finished, act as a skeptical reviewer. Do not fix anything yet: produce a pass/fail list with exact evidence.

Check:
1) Files: out/reel-<lang>.mp4, captions.srt, words.json, render.json, qa/report.md, qa/contact-sheet.jpg, reel-state.json.
2) ffprobe: 1080x1920, expected fps, H.264, exactly one AAC audio stream, duration within 0.75 s of hyperframes.json, file >100 KiB.
3) Visual: open the contact sheet. Hook readable by 1.5 s; no black/frozen/empty frames; captions inside safe zones; no text under platform buttons; motion is present.
4) Language: ar => dir="rtl", direction:rtl, RLE/PDF in SRT, highlight right-to-left inside a full shaped Arabic line. en => LTR and left-to-right highlight.
5) Timing: clean happened before align; edits.json exists; word times are on clean.wav; score:0 words are listed for human review.
6) Facts: every number/date/name on screen comes from config/facts.json. Flag any invented value as a hard failure.
7) Determinism: no independent clocks, unseeded randomness, free-running loops, remote src, or second audio mux.
8) Keyless: no API keys, no tokens, no paid calls, no diarization token, no publishing. reel-state.json cost is api_calls=[] and credits_spent=0.
9) Renderer: report whether HyperFrames or pillow-fallback was used. If fallback, note that per-word highlight is simplified.

Only after I approve the report, fix the earliest failing stage, re-run from there, and regenerate QA. Maximum two repair loops, then stop and ask. Publishing is a separate explicit human action and is never part of this harness.
```
