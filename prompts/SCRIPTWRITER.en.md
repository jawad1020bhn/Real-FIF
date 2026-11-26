# Short-form scriptwriter (English)

```text
Draft a 20–35 second vertical reel script for one speaker, using only config/brand.json and config/facts.json.

Constraints:
- Hook within the first 1.5 seconds: one concrete promise or sharp question. No hype, no "secret", no false urgency.
- 3–5 short beats; each beat is one sentence that fits one caption line. No compound clauses, no jargon without a plain-language gloss.
- Every number, date, name, and claim must already exist verbatim in config/facts.json. If absent, write [placeholder] and tell me what is missing. Never infer from a README, model output, or earlier video.
- LTR, DejaVu Sans, plain sentence case. Isolate non-Latin tokens with <bdi>.
- One CTA at the end. No hashtags, links, or sales promises.
- Offer three hook alternatives and explain why one was chosen, then write the chosen copy to config/copy.en.json (hook, subtitle, outro, cta, scenes). Do not edit code.
- Everything is a draft. Do not use "best", "fastest", or superlatives unless config/facts.json supports them.

After approval, run the humanizer pass on style only: remove filler and generic AI cadence, add no new facts.
```
