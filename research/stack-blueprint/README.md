# Stack blueprint — a worked "merge" design

This directory is **research output, not an installed plugin**. It is a copy-ready starting point for the recommended Stack A in [`../claude-code-reels-research.md`](../claude-code-reels-research.md): one orchestrator skill, one renderer, file-based handoffs, explicit approval gates and verification at every stage.

```
stack-blueprint/
├── README.md                              # this file
├── CLAUDE.md.snippet                      # always-on rules; import from each project
├── reel-state.example.json                # the single handoff contract
├── skills/reel-orchestrator/SKILL.md      # the meta-skill that owns stage order
└── audio-first-arabic/                    # Stack E: voice-first Arabic reels
    ├── README.md                          #   stage contract, traps, first test
    ├── PROMPT.ar.md                       #   hardened Arabic Claude Code prompt
    ├── words.schema.json                  #   WhisperX -> caption/scene handoff
    ├── words.example.json                 #   RTL + tashkeel + <bdi> example
    └── rtl-caption.example.html           #   deterministic RTL karaoke block
```

## Why this shape

It distils the nine case studies in Section 5 of the report:

| Borrowed from | Applied here |
|---|---|
| `Ootto-AI/claude-content-skills` | One orchestrator (`/reel`) with an explicit numbered pipeline and a compounding learn stage |
| `tripathiadityap/claude-skills` | One short `CLAUDE.md` of global guardrails; profile/brand read first by every stage |
| `kajisho5/ffmpeg-skill` ecosystem | Brain/hands split, typed tools, machine-readable `contract --json`, one-way dependencies |
| `murathany7/reel-studio` | Exactly one clock/timeline owner; engines are imported assets, not rival timelines; frame/text/layout QA |
| `artemnovitckii/claude-animation-skills` | A shared JSON spec → template → MP4 → contact sheet with safe areas |
| `itpartypattaya/reels-montage` | Approve the plan before any render; paid/network add-ons are opt-in |
| `DojoCodingLabs/remotion-superpowers` | Layering on official skills, hooks for hard guards, subagents for research |
| `iart-ai/motion-skills` | Install few, focused skills; each with a deliver-and-verify loop |
| `hyperframes` marketplace | Ship skills as one versioned bundle; reuse registry blocks before hand-building |

## How to adopt (Stack A, keyless)

```bash
# 1. Core renderer already used by videos/ — add its official skills
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes

# 2. Craft layers (markdown only, no renderer of their own)
npx skills add LottieFiles/motion-design-skill
npx skills add iart-ai/tiktok-video-skills
npx skills add blader/humanizer

# 3. Local editing/QC "hands"
npx ffmpeg-skill setup
npx ffmpeg-skill doctor
npx ffmpeg-skill contract --json | head -40

# 4. The orchestrator (copy, don't symlink into a live .claude dir without review)
mkdir -p .claude/skills/reel-orchestrator
cp research/stack-blueprint/skills/reel-orchestrator/SKILL.md .claude/skills/reel-orchestrator/
```

Then, per video project (`videos/<project>/`):

```bash
cp research/stack-blueprint/reel-state.example.json videos/<project>/reel-state.json
# append/import CLAUDE.md.snippet into videos/<project>/CLAUDE.md and AGENTS.md
```

Edit `reel-state.json` (`project`, `facts`, `goal`, `format`), then in Claude Code:

```
/reel-orchestrator make a 30s 9:16 data-story reel about the a product launch
```

## Pinning third-party skills (recommended for a team)

Community marketplaces move fast. For a reproducible stack, mirror the repos you choose into a private marketplace with pinned commits, following the `strict: false` skill-bundle entry shape documented in [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official):

```json
{
  "name": "reel-stack",
  "plugins": [
    {
      "name": "reel-craft",
      "description": "Pinned, reviewed craft skills for short-form reels",
      "source": { "source": "git-subdir", "url": "https://github.com/<your-org>/<mirror>.git", "path": "skills", "ref": "main", "sha": "<40-char-commit>" },
      "strict": false,
      "skills": ["./motion-design", "./short-form-video", "./humanizer"]
    }
  ]
}
```

Review every `SKILL.md`, script, `hooks.json` and `.mcp.json` at that SHA; bump the SHA deliberately. Never point at a moving `main` branch for anything with shell access.

## Stack E (audio-first Arabic reels)

[`audio-first-arabic/`](audio-first-arabic/) applies the same patterns to a different input — a voice recording instead of a topic. It reuses `CLAUDE.md.snippet`, `reel-state.example.json` and the orchestrator's stage/gate discipline, and adds a `words.json` contract, an RTL karaoke caption component and a determinism guard for GSAP/anime.js/mo.js/Three.js. Keep **one** orchestrator: if you adopt Stack E, extend `reel-orchestrator` with its stages rather than running a second meta-skill.

## Do / don't

- ✅ Keep `SKILL.md` lean, references on demand, ≤12 active skills, `/doctor prompt-audit` after changes.
- ✅ A/B against a no-skill baseline — a plain Claude Code session can already make a valid 15-second promo.
- ❌ Don't add both HyperFrames and Remotion as timeline owners in one project.
- ❌ Don't run `/content-factory` and `/reel-orchestrator` at once — two orchestrators means two stage orders.
- ❌ Don't auto-publish, auto-spend, or paste web/transcript text into an instruction position.
