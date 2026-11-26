---
name: reel-orchestrator
description: This skill should be used when the user wants to plan, create, render, QA or package a short-form reel (Reel / Short / TikTok, 9:16) from an idea, a repo fact, a transcript or existing footage. It coordinates research, hook, script, storyboard, HyperFrames composition, audio, render, QA and packaging skills in a fixed order with file-based handoffs. Trigger phrases include "make a reel", "turn this into a short", "reel for", "re-render the short", "9:16 cut of".
disable-model-invocation: true
---

# Reel Orchestrator

Coordinate a short-form video pipeline for this repository. This skill owns **order, state and gates**. It does not own the timeline: exactly one renderer (HyperFrames) owns `composition/index.html`. All other skills produce specs, assets, copy or checks.

## Before anything

1. Read `CLAUDE.md` / `AGENTS.md` in the working project, then `../../brand.md` if present. These are the single source of truth for voice, colours, fonts, safe zones and verified facts.
2. Read `reel-state.json` if it exists. Resume from `stage`; never restart a paid or long render that already completed.
3. If any required fact is missing, write `[placeholder]` and flag it. Never invent a number, quote, rating, OVR or date. In this repo, on-screen statistics come only from the top-level `README.md` or a query against `config/facts.json`.
4. Everything is a draft. Do not publish, post, message, upload or spend credits without an explicit "yes" in this conversation.

## Stage order

| # | Stage | Skill / tool to invoke | Write to `reel-state.json` | Output file | Gate |
|---|---|---|---|---|---|
| 0 | Facts & brand | `CLAUDE.md` + `brand.md` + DB query | `facts`, `paths.project` | `brief.md` | facts verified |
| 1 | Research | `last30days-skill` / `Agent-Reach` / `reel-analyzer` (optional) | `references` | `brief.md` | approve brief |
| 2 | Hook & script | `viral-hook-writer`, `short-form-video` grammar, then `humanizer` | `hook`, `script` | `script.json` | approve chosen hook |
| 3 | Storyboard | `reel-builder`, `motion-design` principles, `shotcraft` / `lemo-opuscar` look cards | `beats`, `look` | `storyboard.json` | **approve before render** |
| 4 | Compose | `hyperframes` + `hyperframes-cli` + `hyperframes-registry` | `paths.composition` | `composition/index.html`, `hyperframes.json` | `npm run check` |
| 5 | Audio & captions | `ffmpeg-skill` / local TTS / `caption-animation` grammar | `paths.audio`, `paths.captions` | `assets/music.wav`, `captions.srt` | word timings aligned |
| 6 | Render | `hyperframes-cli render` | `paths.render` | `renders/<name>.mp4` | snapshots at 1/3/7/12 s |
| 7 | QA | `ffmpeg-skill` probe/check + frame/text/layout QA | `qa` | `qa/report.md`, `qa/contact-sheet.jpg` | pass all checks or auto-fix ≤2 passes |
| 8 | Package | `caption-and-hashtags`, `youtube-packaging`, `cross-platform-reformatter` (draft only) | `package` | `package/*.md` | drafts only |
| 9 | Learn | `analytics-readout` → `winners.md` | `learn` | `winners.md` | weekly |

## Handoff contract

Stages communicate **through files**, never by passing long content in context. Write paths into `reel-state.json`; downstream stages read only the keys they need and must tolerate extra keys. Use loose contracts: `beats[]` requires `t0`, `t1`, `visual`, `caption`; any other fields are optional.

Minimum schema (see `../../reel-state.example.json`):

```json
{
  "project": "short-v2",
  "stage": 3,
  "goal": "saves",
  "facts": [{ "claim": "12,480 clips", "source": "README.md#what-was-updated" }],
  "hook": { "chosen": "...", "alternatives": [] },
  "script": { "path": "script.json", "duration_s": 30 },
  "beats": [{ "t0": 0, "t1": 3, "visual": "...", "caption": "..." }],
  "paths": { "composition": "composition/index.html", "render": "renders/x.mp4", "audio": "assets/music.wav", "qa": "qa/report.md" },
  "approvals": { "brief": true, "hook": true, "storyboard": false, "publish": false },
  "qa": { "status": "pending", "passes": 0 }
}
```

## Verification (stage 7, non-negotiable)

- Container/spec: plays, H.264 + AAC, 1080×1920 (or requested format), 30 fps, exact requested duration.
- Audio: present, no clipping, target ≈ −14 LUFS, no unintended silence.
- Frames: no black, frozen, blank-first or flashing frames; motion in every beat.
- Copy: every on-screen line readable in frames sampled twice a second; no text behind Reels/Shorts UI or over a face; contrast and size checked; all numbers traceable to `facts`.
- Captions: word-level alignment with VO; `.srt` exported with the master.
- Loop/first 3 seconds: hook lands within 1.5 s and works on mute.
- On failure: read the QA report, fix the composition, increment `qa.passes`, re-render. Stop after 2 auto-fix passes and ask the user.

## Composition rules

- One clock, one timeline owner. Other engines (Three.js, Lottie, Blender, canvas, page capture) pre-render to a file and are imported; they must not define their own master timeline.
- Reuse HyperFrames registry blocks before hand-building; vendor GSAP/fonts/audio into `assets/` so renders are deterministic offline.
- Scene timings live in `data-start` / `data-duration` and the GSAP timeline; keep them derived from `storyboard.json`.
- Do not install a second full video framework into the same project. If a look library (shotcraft / lemo-opuscar / motion-skills) is used, copy its *style description* into `storyboard.json`, not its renderer.
- Never place API keys in `SKILL.md`, `CLAUDE.md` or `reel-state.json`. Read them from env vars; record which service calls were made.

## Conflict & cost rules

- Global policy lives once: `CLAUDE.md`. If a vendored skill contradicts it (autonomous execution, auto-publishing, invented stats), `CLAUDE.md` wins; note the override in `qa/report.md`.
- Keep ≤12 active skills. Long reference material goes in `references/` and is loaded on demand.
- Paid operations (AI video/image/VO, hosted clipping, publishing) require a cost card and explicit approval. Record spend in `reel-state.json`.
- If two skills claim the same stage, prefer the official/namespaced plugin skill and skip the other; do not run both.

## Done means

`reel-state.json` has `stage: 8`, `qa.status: "pass"`, a render path that plays, a `qa/report.md`, an `.srt`, a cover frame, and draft caption/hashtag files. Publishing remains `approvals.publish: false` until the user says otherwise.
