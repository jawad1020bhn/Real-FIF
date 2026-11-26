# Voice-first reel — Stack E (English)

> Paste the block below into Claude Code inside this repo. Language `en` means LTR, DejaVu Sans, and the English alignment model. No API keys, credits, or publishing.

```text
Build a 1080x1920 / 30 fps vertical reel from an English voice recording, with word-timed captions and frame-locked motion, using only the keyless harness in this repository.

Work stage by stage. After each stage, show the files produced and wait for my approval:

0) Run npm run doctor, then read reel-state.json and resume from its last stage. Use the pinned versions in package.json and requirements.txt. Do not install anything new or download model weights without approval. No API keys, no HF token, no diarization for a single speaker.

1) Clean audio FIRST: npm run clean -- --project videos/en-reel --input <audio file>. Outputs audio/clean.wav and audio/edits.json. Every later timestamp is on the clean audio. Any cut after alignment must be remapped with edits.json.

2) Word timings: if weights are cached in models/, run npm run align -- --lang en --project videos/en-reel --align-backend whisperx with --language en and the English wav2vec2/torchaudio alignment model. If Hugging Face is blocked, use --offline or --from-json config/words.en.example.json. Mark out-of-vocabulary tokens score:0 with nearest interpolation and list them in QA. ASR never rewrites the reviewed copy, names, or numbers.

3) Scenes: read config/copy.en.json, config/brand.json, and config/facts.json. Never invent a number, date, name, or claim; missing values become [placeholder] and are escalated. Scene boundaries come from words.json or reviewed sentence boundaries, never guessed timestamps. All assets are local under assets/.

4) Motion: run npm run compose and npm run render. One paused GSAP timeline seeked to film time; no independent clocks, unseeded randomness, free-running animation loops, or network assets. HyperFrames is the quality path; the Pillow renderer is a Chrome-less fallback only. Never combine HyperFrames and Remotion in one project.

5) Captions: LTR word-timed karaoke, full line with the active word highlighted inside it. Use <bdi> for isolated numbers or non-Latin tokens. First caption within 1.5 s; the reel must make sense with sound off. Safe zones: platform band y 288–1248, x 120–888; below y 840 the right edge narrows to 780. Captions sit at the bottom of the band.

6) Export and QA: the renderer muxes audio once. Use FFmpeg afterwards only for probe, loudness near -14 LUFS, and review snapshots — never a second naive mux. Run npm run qa, open qa/contact-sheet.jpg and qa/report.md. Verify duration, resolution, fps, one audio stream, caption direction, unverified words, black frames, and no invented facts. On a critical failure: snapshot → read → fix → re-render, at most twice, then ask me.

7) Update reel-state.json after every stage. Cost must remain api_calls=[] and credits_spent=0. Deliver a draft only: out/reel-en.mp4 + captions.srt + qa/report.md. Do not publish, upload, buy credits, or modify reference projects in videos/ without explicit approval.

Run the chain with npm run reel -- --lang en --project videos/en-reel --input <audio file>, or --demo --offline for a deterministic no-model smoke test.
```

The eight underlying corrections and licence/model notes are in `research/claude-code-reels-research.md` Section 9 and `docs/INSTALL.md`.
