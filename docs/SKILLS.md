# Skills, prompts, and security policy

This harness uses Claude Code skills as **procedural knowledge**, not as executable dependencies. One local orchestrator owns the pipeline; upstream skills supply craft guidance on demand.

## Local authoritative wrappers

`.claude/skills/` contains seven wrappers that are always available:

| Wrapper | Responsibility |
|---|---|
| `reel-orchestrator` | One pipeline, stage contracts, state, approvals, keyless rule |
| `audio-first-reel` | Stack E bilingual voice-first workflow and eight corrections |
| `rtl-caption-craft` | Arabic bidi, full shaped lines, `<bdi>`, safe zones, fonts |
| `deterministic-motion` | One paused timeline, frame seeking, banned clocks/network assets |
| `short-form-copy` | Hooks, scripts, scene copy, fact discipline, humanizer pass |
| `ffmpeg-qc` | ffprobe, loudness, contact sheet, black frames, no double mux |
| `skill-audit` | Pinning, text-only vendoring, review before enabling |

`CLAUDE.md` holds always-on rules and outranks every skill. Prompts live in `prompts/`; the long-form Arabic rationale remains in `research/stack-blueprint/audio-first-arabic/PROMPT.ar.md`.

## Pinned upstream snapshots

`vendor/skills/` holds **22 text-only `SKILL.md` snapshots**. Each directory includes `SOURCE.json` with repo, exact commit SHA, upstream path, licence, URL, and audit note. `vendor/skills/SOURCES.json` and `vendor/skills/INDEX.md` are the catalogues.

| Repository | Snapshots | Licence | Why |
|---|---:|---|---|
| `heygen-com/hyperframes` | 9 | Apache-2.0 | Official HyperFrames CLI, registry, media, reverse-video, style-sampling, slideshow, figma, remotion-to-hyperframes |
| `kajisho5/ffmpeg-skill` | 1 | MIT | 42 typed offline FFmpeg tools / machine-readable QC contract |
| `remotion-dev/skills` | 4 | no SPDX file | Best practices, captions, render, licence (opt-in renderer only) |
| `LottieFiles/motion-design-skill` | 1 | MIT | Timing, easing, motion grammar |
| `iart-ai/tiktok-video-skills` | 2 | MIT | Short-form video + caption animation |
| `blader/humanizer` | 1 | MIT | Prose cleanup without new facts |
| `Ootto-AI/claude-content-skills` | 4 | MIT | Content factory, reel builder, reel scripter, caption/hashtags |

**Only `SKILL.md` text is vendored.** Upstream scripts, hooks, MCP configs, binaries, and assets are intentionally excluded. Pinned commits were resolved on 2026-11-25/26; do not auto-update during a render.

## Commands

```bash
npm run skills:list                         # local wrappers + upstream catalogue + risk flags
npm run skills:audit                        # pattern audit of vendored SKILL.md text
npm run skills:enable -- --enable <slug>    # copy one SKILL.md + SOURCE.json into .claude/skills
npm run skills:all                          # enable all 22 (higher context cost)
npm run skills:enable -- --disable <slug>  # remove an enabled upstream snapshot
npm run skills:enable -- --help
```

`--enable` accepts slugs exactly as printed by `npm run skills:list`. Use `--force` to overwrite an already enabled snapshot. Local wrappers are never removed by `--disable`.

## Security policy

Public 2026 audits found prompt-injection patterns in a large share of scanned public skills and higher risk when skills bundle executable scripts. Treat every upstream addition as untrusted until reviewed.

1. Read the pinned URL and licence. `NOASSERTION` / missing SPDX is not proof of open source.
2. Run `npm run skills:audit` and inspect matches for shell execution, `eval`, destructive commands, remote fetches, secret env vars, hooks, and MCP servers. Flags are review prompts, not proof of malice.
3. Confirm the skill cannot override `CLAUDE.md`, `reel-orchestrator`, `config/facts.json`, approval gates, RTL rules, determinism rules, or the keyless rule.
4. Confirm exactly one orchestrator and one renderer.
5. Enable one skill at a time. Keep ≤12 active skills; run `/doctor` and `/doctor prompt-audit` after adding any skill.
6. Record the enabled slug and reason here. Publishing, paid calls, and secret-bearing instructions are never allowed.

## Current enablement

- Local wrappers: 7 active by design.
- Upstream snapshots: **0 enabled by default**; all 22 are available in `vendor/skills/`.
- `ffmpeg-skill` npm package is installed for typed local FFmpeg tooling, but its MCP server is not launched. The harness calls local `ffmpeg`/`ffprobe` binaries directly.
- `hyperframes` npm package includes its own skill assets inside `node_modules/`; those are not copied into `.claude/skills/` unless explicitly enabled.

## Progressive disclosure

Use `reel-orchestrator` first. Load a craft wrapper only when the task needs it. Enable an upstream snapshot only when its specific knowledge is required. Do not load all skills into every session; context cost is part of quality.
