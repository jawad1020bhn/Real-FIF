# Highest-quality prompts

These are copy-ready prompts for Claude Code. They are **keyless**, bilingual, and tied to the file contracts in this repository. Use `reel-orchestrator` as the only top-level skill; these prompts supply intent and quality gates.

| Prompt | Use when |
|---|---|
| [`STACK-E.ar.md`](STACK-E.ar.md) | Arabic voice-first reel, full hardened brief |
| [`STACK-E.en.md`](STACK-E.en.md) | English voice-first reel, same stack and corrections |
| [`SCRIPTWRITER.ar.md`](SCRIPTWRITER.ar.md) | Arabic hook / script / scene copy |
| [`SCRIPTWRITER.en.md`](SCRIPTWRITER.en.md) | English hook / script / scene copy |
| [`VISUAL-DIRECTION.md`](VISUAL-DIRECTION.md) | Look, motion, typography, safe zones |
| [`QUALITY-GATE.md`](QUALITY-GATE.md) | Final review, QA, and human approval gates |
| [`../research/stack-blueprint/audio-first-arabic/PROMPT.ar.md`](../research/stack-blueprint/audio-first-arabic/PROMPT.ar.md) | Long-form Arabic rationale and the original 12-tool correction table |

## Shared rules

- No API keys, tokens, diarization tokens, paid calls, or publishing.
- `config/facts.json` is the only source of truth. Missing values become `[placeholder]`; never invent numbers.
- One orchestrator, one renderer, one paused timeline.
- `--lang ar` is strict RTL; `--lang en` is LTR.
- Silence cuts happen before alignment; `edits.json` is the remap contract.
- The reviewed text wins over ASR output.
- Audio is muxed once; FFmpeg after render is for probe / loudness / snapshots / QA only.
- Stop after each stage, show the produced files, and wait for approval.
