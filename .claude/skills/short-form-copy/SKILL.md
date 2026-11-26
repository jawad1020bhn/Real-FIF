---
name: short-form-copy
description: Use when writing hooks, scripts, on-screen copy, scene text, captions, CTAs, or hashtags for Reels, TikTok, and Shorts. Enforces fact discipline, bilingual copy files, short-form grammar, and draft-only output.
---

# Short-form copy

## Structure

1. **Hook (0–1.5 s):** one concrete promise or tension. Put it on screen immediately; sound-off viewers must understand it.
2. **Body (1.5 s → end−1.5 s):** 3–5 beats, each tied to a sentence boundary or `words.json` line. No walls of text.
3. **Outro / CTA (last 1.5 s):** one action. No stacked links, hashtags, or disclaimers.

For 30–45 s scripts, keep spoken sentences short and let each line become one caption state. Scene boundaries come from `words.json` or reviewed sentence boundaries, never guessed timestamps.

## Files, not chat memory

- `config/copy.ar.json` and `config/copy.en.json`: hook, subtitle, outro, CTA, scenes.
- `config/facts.json`: **only** source of truth for numbers, dates, names, and claims. If empty, use `[placeholder]` and ask a human. Never infer a statistic from a README, model output, or prior video.
- `config/brand.json`: voice, palette, safe zones, format, platforms.
- `words.json`: reviewed display text and timings. ASR never rewrites it.
- `reel-state.json`: chosen hook, alternatives, goal, approvals, QA.

## Language rules

- `ar`: strict RTL; full tashkeel is allowed in `display` but stripped in `align`; no isolated Arabic word reshaping.
- `en`: LTR; plain sentence case; `<bdi>` is still used for embedded numbers/Latin inside an Arabic line.
- Do not mix Arabic and English in the same caption line unless the user asked for it; isolate mixed tokens explicitly.

## Human, not hype

Use the `humanizer` upstream skill only as a prose pass after the facts are locked: remove filler, inflated claims, and generic AI cadence. Do not add new facts. Do not optimize for engagement by inventing urgency. Every output is a draft; brief, storyboard, and publish are separate approvals.
