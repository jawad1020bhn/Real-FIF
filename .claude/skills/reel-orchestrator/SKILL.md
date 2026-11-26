---
name: reel-orchestrator
description: Use when the user asks to create, render, re-render, or QA a short-form reel in this repository. Owns the whole keyless pipeline and enforces one renderer, file contracts, bilingual language switching, approval gates, and QA.
---

# Reel orchestrator

You are the single top-level orchestrator for the keyless reel harness. Do not run multiple renderers or improvise a second pipeline. Every stage communicates through files, not chat memory.

## Non-negotiable rules

1. **Keyless:** no API keys, no tokens, no paid calls, no diarization token, no external model calls at render time. Do not publish, upload, or spend credits.
2. **One renderer:** HyperFrames is the quality path. The offline Pillow renderer is a fallback only. Remotion is opt-in and must never run in the same project as HyperFrames.
3. **One timeline owner:** a single paused GSAP timeline seeked to film time. See `deterministic-motion`.
4. **Language switch:** `--lang ar` means strict RTL, Scheherazade New and Arabic wav2vec2 alignment; `--lang en` means LTR, DejaVu Sans and the English alignment model. See `rtl-caption-craft`.
5. **Facts:** `config/facts.json` is the only source of truth for numbers and claims. Never invent statistics, dates, or names. Use `[placeholder]` and ask for a human value.
6. **Approvals:** installs, briefs, storyboards, and publishing are explicit human gates. This harness produces drafts only.
7. **ASR is not an editor:** reviewed text in `words.json` / `copy.<lang>.json` wins. Never let transcription rewrite copy, especially Qur'anic recitation, numbers, or names.

## Stage contract

| Stage | Command / file | Required output |
|---|---|---|
| 0 doctor | `npm run doctor` | `reports/doctor.json` |
| 1 clean | `npm run clean` | `audio/clean.wav`, `audio/edits.json` |
| 2 align | `npm run align` | `words.json`, `captions.srt` |
| 3 compose | `npm run compose` | `index.html`, `hyperframes.json`, `assets/` |
| 4 render | `npm run render` | `out/reel-<lang>.mp4`, `render.json` |
| 5 qa | `npm run qa` | `qa/report.md`, `qa/report.json`, `qa/contact-sheet.jpg` |
| state | `reel-state.json` | updated after every stage |

Run the complete chain with `npm run reel -- --lang ar --project videos/my-reel --demo --offline` or supply `--input /path/to/voice.wav`. Use `--help` for all flags. No model cache means the orchestrator defaults to deterministic `--from-json` word timings.

## Working order

1. Read `reel-state.json` first; resume from its `stage` rather than restarting blindly.
2. Run `npm run doctor` and stop on missing core binaries. Record warnings, especially heavy ASR/model-cache notes.
3. Clean silence **before** alignment. If anything is cut later, remap every word with the `edits.json` rule.
4. Align with the language-specific model, or use `config/words.<lang>.example.json` offline. Mark unalignable words `score: 0` and list them in QA.
5. Compose from `config/copy.<lang>.json`, `config/brand.json`, and `words.json`. All assets must be local.
6. Render once. HyperFrames already muxes the `<audio>` tag; the Pillow fallback muxes once in its final FFmpeg command. Never add a second naive mux.
7. Run QA. If a critical check fails, fix the earliest failing stage and re-run from there, at most twice, then ask the user.
8. Update `reel-state.json` with stage status, paths, QA, and cost. Cost must remain `{api_calls: [], credits_spent: 0}`.

## Progressive disclosure

- Architecture and file contracts: `docs/ARCHITECTURE.md`
- Install/model reality: `docs/INSTALL.md`
- Skill catalogue and security policy: `docs/SKILLS.md`
- Highest-quality prompts: `prompts/README.md`
- Pinned upstream skill snapshots: `vendor/skills/SOURCES.json` and `npm run skills:list`

If the user asks for a specific craft layer, invoke the matching local wrapper (`audio-first-reel`, `rtl-caption-craft`, `deterministic-motion`, `short-form-copy`, `ffmpeg-qc`, `skill-audit`). Keep this skill as the only orchestrator.
