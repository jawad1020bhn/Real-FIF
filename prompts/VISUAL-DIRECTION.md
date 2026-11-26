# Visual direction prompt

```text
Art-direct the reel from config/brand.json. Canvas 1080x1920, 30 fps, dark editorial look: near-black background, soft accent glow at the top, gold accent, warm muted secondary text, generous negative space.

Rules:
- Platform-safe band: y 288–1248, x 120–888; below y 840 the right edge narrows to 780. Arabic captions sit 20 px higher. No text under platform controls.
- Headline >= 92 px, captions >= 84 px Arabic / 72 px English. High contrast, dark caption plate, soft text shadow.
- One paused GSAP timeline: hook rises/fades in, subtitle follows, each scene crossfades at words.json boundaries, progress bar runs across the full duration, outro + CTA in the last 1.5 seconds.
- Caption states show a FULL shaped line. Highlight only the active word inside it. Arabic is RTL with <bdi> around Latin/numbers; English is LTR.
- Fonts, GSAP, and audio are local files under assets/. No CDN, no remote images, no generated imagery calls.
- Motion is slow, purposeful, and frame-locked: no free-running loops, no unseeded randomness, no overlapping tweens on the same property. Reset every scene with tl.set before animating.
- Every frame must be reproducible from the same inputs. Prefer fewer, cleaner beats over decorative motion.

Deliver index.html + hyperframes.json via npm run compose, then a contact sheet via npm run qa. Describe the look in one sentence in qa/report.md.
```
