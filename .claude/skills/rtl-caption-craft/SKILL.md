---
name: rtl-caption-craft
description: Use when composing, styling, or QA'ing Arabic word-timed captions. Prevents reversed bidi order, isolated-word reshaping, Latin/number breakage, and unreadable safe zones.
---

# RTL caption craft

Arabic captions are a full-line typography problem, not a list of independent word spans.

## Required markup

- Container: `dir="rtl" lang="ar" style="direction:rtl;unicode-bidi:isolate"`.
- Show the **complete shaped line** at all times. Change only the active word's colour/background inside that line.
- Isolate Latin names and numbers with `<bdi>`; set `unicode-bidi:isolate`.
- Use Scheherazade New for full tashkeel, Amiri as fallback. Their SIL OFL licences sit next to the fonts in `templates/hyperframes/assets/fonts/`.
- Load fonts before the first captured frame; never reference a CDN.

## Why

Inline-block word spans are bidi-neutral. Without `dir="rtl"` the sentence order and karaoke highlight reverse. An isolated Arabic word reshapes incorrectly because Arabic glyph joining depends on surrounding letters. The full-line highlight avoids both failures.

## Safe-zone and readability rules

- 1080×1920 canvas. Platform-safe band: y 288–1248, x 120–888; below y 840 TikTok narrows the right edge to 780. Arabic captions sit 20 px higher.
- Caption text at least 40 px, headline at least 72 px. This harness uses 84 px Arabic / 72 px English captions and a 92 px headline.
- First caption must appear within 1.5 s. The reel must make sense with sound off.
- High contrast, dark caption plate, no text beneath platform buttons.
- Arabic SRT lines carry RLE `\u202b` and PDF `\u202c` marks; `scripts/qa.py` checks them.

## QA checklist

- Highlight travels right-to-left for `ar`, left-to-right for `en`.
- One caption state per word in `index.html`, with `w active` inside a full line.
- `words.json` has `direction: "rtl"` for `ar`; `score: 0` words appear in `qa/report.md`.
- `captions.srt` exists and is isolated for Arabic.
- Contact sheet sampled from the actual MP4 is readable.
