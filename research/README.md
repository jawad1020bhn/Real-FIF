# Research — Claude Code reels & content-creation stack

A research deliverable for this repo (2026-11-25, addendum same date). The repo retains one Arabic HyperFrames reference example under `videos/`; this work surveys the current open-source ecosystem and studies how to combine several tools for better results.

| File | What it is |
|---|---|
| [`claude-code-reels-research.md`](claude-code-reels-research.md) | **Main report**: verified shortlist by layer, benchmark analysis, merging study (9 case studies → 10 patterns → failure modes → security), 5 recommended stacks (A–E), a 9-stage pipeline for this repo, evaluation plan, sources. **Section 9 is the addendum** for the 12-tool Arabic audio-first prompt. |
| [`tool-matrix.csv`](tool-matrix.csv) | 36 Claude Code repos: stars / forks / SPDX licence / last push / install command / dependencies / assessment, verified 2026-11-25 |
| [`audio-factory-matrix.csv`](audio-factory-matrix.csv) | 28 entries for the 12-tool Arabic reel factory + their Claude Code skill wrappers: versions (npm/PyPI), licences, stars, adoption verdict |
| [`stack-blueprint/`](stack-blueprint/) | Copy-ready merge design: orchestrator `SKILL.md`, shared `reel-state.json` contract, always-on `CLAUDE.md` rules, adoption/pinning instructions |
| [`stack-blueprint/audio-first-arabic/`](stack-blueprint/audio-first-arabic/) | Hardened Arabic Claude Code prompt, `words.json` schema + example, deterministic RTL karaoke caption example, stage contract |

**Bottom line:** keep HyperFrames as the single renderer, add HyperFrames' own 9-skill plugin plus `ffmpeg-skill` and a short-form craft layer, put them behind one orchestrator with file-based handoffs and frame QA, and add the content-factory skills (hooks/scripts/calendar/memory) only if you're producing reels regularly. The 12-tool Arabic list adds a useful **voice-first Stack E** (Auto-Editor → WhisperX → RTL word captions → render → FFmpeg QC), but only after fixing three blockers: frame-locking external animation libraries, the Arabic wav2vec2 alignment model + tashkeel, and `dir="rtl"` bidi for word spans. Vet and pin every third-party skill first.

> All figures were verified against `api.github.com`, `registry.npmjs.org` and `pypi.org` on 2026-11-25; sources are linked in the report rather than vendored into this repo.

## Implementation status

The recommended Stack A + Stack E design is now implemented at the repository root: see `README.md`, `CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/INSTALL.md`, `docs/SKILLS.md`, `scripts/`, `config/`, `templates/hyperframes/`, `prompts/`, `.claude/skills/`, and `vendor/skills/`. Bilingual `ar`/`en` smoke tests render with HyperFrames and pass both the harness QA and `hyperframes check`. This research folder remains the evidence and design record; the root harness is the runnable deliverable.
