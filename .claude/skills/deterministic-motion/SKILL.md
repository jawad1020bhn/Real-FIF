---
name: deterministic-motion
description: Use when authoring or reviewing GSAP, anime.js, mo.js, Rough.js, Three.js, HyperFrames, or Remotion motion. Enforces one paused timeline, frame seeking, local assets, and reproducible renders.
---

# Deterministic motion

Libraries such as GSAP, anime.js, mo.js, and Three.js own their own clocks. `useCurrentFrame()` alone does **not** frame-lock them.

## One-clock rule

- One timeline per project, owned by one renderer.
- HyperFrames: `const tl = gsap.timeline({paused:true})`; register `window.__timelines['main'] = tl`; HyperFrames seeks it to film time before each capture.
- Remotion (opt-in only): use `@remotion/gsap` and `tl.time(frame / fps, false)`. Never run HyperFrames and Remotion in the same project.
- At most one or two optional motion libraries per scene. Prefer GSAP for the reel's main motion.

## Banned in captured code

- Free-running animation loops and independent clocks.
- `Date.now`, `performance.now`, `THREE.Clock`, unseeded randomness.
- `requestAnimationFrame`, `setTimeout`-driven visual state.
- Network fonts, images, audio, scripts, or `fetch()` at render time.
- Overlapping tweens on the same property without a reset to a known state.

Use a fixed-seed PRNG if variation is essential. Every tween must start from an explicit `tl.set(...)` state so seeking backwards is stable.

## HyperFrames project rules

- `index.html` carries `data-composition-id`, `data-start`, `data-duration`, `data-width`, `data-height`, `data-fps`.
- All assets live under `assets/`; `gsap.min.js`, fonts, and `audio.wav` are vendored locally.
- The final `tl.set({}, {}, duration)` keeps the timeline at the exact composition length.
- `scripts/qa.py` rejects independent clocks and remote `src` URLs.

## Verification

Run `npm run render -- --project ... --out ... --lang ar`, then `npm run qa`. Compare `qa/contact-sheet.jpg` across two renders; identical inputs must produce identical frames.
