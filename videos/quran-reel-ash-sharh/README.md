# Surah Ash-Sharh (94) — Qur'an Reel

A pro-studio vertical reel modelled on `sample.mp4` (Surah At-Takwir) in the repo
root — same visual language, a different surah: **Ash-Sharh, "The Relief"**,
home of *"Indeed, with hardship comes ease."*

## Deliverables

| File | Spec |
|---|---|
| `renders/surah-ash-sharh-reel.mp4` | Master — 1080×1920, 30 fps, 28.0 s, H.264 + AAC, 27.7 MB |
| `renders/surah-ash-sharh-reel-optimised.mp4` | Upload copy — CRF 20, max 8 Mb/s, faststart, 12 MB |

## How it was made

- **Framework:** HyperFrames 0.9.94 (HTML/CSS/GSAP → headless Chrome → FFmpeg),
  project checks pass with `ok: true`.
- **Structure:** 2.7 s title card → one illustrated scene per ayah (8) →
  black-and-gold closing card (94:5–6), mirroring the sample's pacing.
- **Artwork:** eight bespoke cinematic illustrations, one per verse — dawn
  breaking (v1), the burden dissolving (v2), the weighed-down ridge (v3),
  repute raised to the heavens (v4), the hardship canyon (v5) answered by the
  same canyon in sunrise (v6), the quiet courtyard of worship (v7), and the
  path of light (v8). Slow Ken Burns drift, crossfades, film grain, vignette,
  gold progress bar.
- **Typography:** Scheherazade New for the Arabic (full tashkeel), gold
  letter-spaced surah/verse header and Eastern-Arabic numeral medallion —
  same system as the sample. English: Saheeh International.
- **Audio:** Qur'an recitation of Surah 94 (source MP3:
  `abderahmanrahmoun/quran-audio-apii` on GitHub, kept as
  `assets/recitation-source.mp3`). Verse boundaries were located by waveform
  envelope analysis (dips at 2.55 / 5.30 / 7.95 / 10.35 / 13.20 / 16.30 /
  19.10 s), padded behind the title card (+2.4 s), then mastered with
  `loudnorm` to **−14 LUFS / −1.5 dBTP** (measured −13.8 LUFS on the master).

## Re-render

```bash
cd videos/quran-reel-ash-sharh
npm run check     # HyperFrames checks
npm run render    # -> renders/surah-ash-sharh-reel.mp4
```

Edit timings/text in `index.html`; scene artwork lives in `assets/scene*.jpg`.
