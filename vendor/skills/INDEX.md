# Pinned upstream skill snapshots

Pinned on **2026-11-25**. Text-only skill snapshots; no upstream executable code, hooks or MCP servers. Enable one at a time via npm run skills:enable.

No upstream scripts, hooks, MCP servers, binaries, or assets are vendored. Each directory contains `SKILL.md` text plus `SOURCE.json` provenance.

| Slug | Repository | Commit | Licence | Upstream path |
|---|---|---|---|---|
| `hyperframes-figma` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/figma/SKILL.md` |
| `hyperframes-hyperframes-cli` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/hyperframes-cli/SKILL.md` |
| `hyperframes-hyperframes-registry` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/hyperframes-registry/SKILL.md` |
| `hyperframes-hyperframes` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/hyperframes/SKILL.md` |
| `hyperframes-media-use` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/media-use/SKILL.md` |
| `hyperframes-remotion-to-hyperframes` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/remotion-to-hyperframes/SKILL.md` |
| `hyperframes-reverse-any-video` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/reverse-any-video/SKILL.md` |
| `hyperframes-slideshow` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/slideshow/SKILL.md` |
| `hyperframes-style-sampling` | `heygen-com/hyperframes` | `707fe93ab813` | Apache-2.0 | `skills/style-sampling/SKILL.md` |
| `ffmpeg-skill-ffmpeg-skill` | `kajisho5/ffmpeg-skill` | `6b07d9fb69ca` | MIT | `skills/ffmpeg-skill/SKILL.md` |
| `skills-remotion-best-practices` | `remotion-dev/skills` | `a3f4098a2afd` | NONE | `skills/remotion-best-practices/SKILL.md` |
| `skills-remotion-captions` | `remotion-dev/skills` | `a3f4098a2afd` | NONE | `skills/remotion-captions/SKILL.md` |
| `skills-remotion-render` | `remotion-dev/skills` | `a3f4098a2afd` | NONE | `skills/remotion-render/SKILL.md` |
| `skills-remotion-license` | `remotion-dev/skills` | `a3f4098a2afd` | NONE | `skills/remotion-license/SKILL.md` |
| `motion-design-skill-motion-design` | `LottieFiles/motion-design-skill` | `d77a9fc8cb37` | MIT | `skills/motion-design/SKILL.md` |
| `tiktok-video-skills-short-form-video` | `iart-ai/tiktok-video-skills` | `88e7152fc271` | MIT | `skills/short-form-video/SKILL.md` |
| `tiktok-video-skills-caption-animation` | `iart-ai/tiktok-video-skills` | `88e7152fc271` | MIT | `skills/caption-animation/SKILL.md` |
| `humanizer` | `blader/humanizer` | `a32f24407364` | MIT | `SKILL.md` |
| `claude-content-skills-content-factory` | `Ootto-AI/claude-content-skills` | `691875ac3eaf` | MIT | `skills/content-factory/SKILL.md` |
| `claude-content-skills-reel-builder` | `Ootto-AI/claude-content-skills` | `691875ac3eaf` | MIT | `skills/reel-builder/SKILL.md` |
| `claude-content-skills-reel-scripter` | `Ootto-AI/claude-content-skills` | `691875ac3eaf` | MIT | `skills/reel-scripter/SKILL.md` |
| `claude-content-skills-caption-and-hashtags` | `Ootto-AI/claude-content-skills` | `691875ac3eaf` | MIT | `skills/caption-and-hashtags/SKILL.md` |

Enable one at a time:

```bash
npm run skills:list
npm run skills:enable -- --audit
npm run skills:enable -- --enable <slug>
```

Local wrappers under `.claude/skills/` are authoritative; see `docs/SKILLS.md`.
