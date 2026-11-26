# Research: open-source Claude Code plugins, skills & tools for reels and content creation

**Date:** 2026-11-25 · **Branch:** `current working branch` · **Scope:** recent, popular, open-source Claude Code extensions for short-form video (Reels / TikTok / Shorts) and the surrounding content workflow, with a study of how to **merge** several of them into one stack.

> Companion files: [`tool-matrix.csv`](tool-matrix.csv) (36 Claude Code repos), [`audio-factory-matrix.csv`](audio-factory-matrix.csv) (28 entries for the 12-tool Arabic audio-first pipeline + skill wrappers), all metadata verified live via the GitHub/npm/PyPI APIs on 2026-11-25, and [`stack-blueprint/`](stack-blueprint/) (copy-ready orchestrator design, including [`audio-first-arabic/`](stack-blueprint/audio-first-arabic/) with a hardened Arabic prompt).

---

## 0. Executive summary

1. **There is no single "best plugin".** The ecosystem has settled into five layers — (1) research/strategy, (2) hook + script, (3) a deterministic renderer, (4) editing / captions / QA / audio, (5) publishing + analytics. Every strong open-source project occupies one or two of these. Best results come from composing one tool per layer behind a single orchestrator skill.
2. **Popularity is a poor quality signal here.** The most-starred repos are catalogues/frameworks (`anthropics/skills` 200.4k, `obra/superpowers` 326.5k, `ComposioHQ/awesome-claude-skills` 80.3k). Several excellent, actively maintained reel tools have <50 stars (`murathany7/reel-studio` 5, `itpartypattaya/reels-montage` 11, `High56/short-video-skills` 1) because they shipped in the last 4–8 weeks. Tier recommendations below are based on pipeline fit, licence, activity, dependencies and evidence — not stars alone.
3. **A controlled benchmark exists and it is humbling.** `zhuyansen/awesome-claude-video-skills` ran 16 video skills on the same 15-second promo brief with Claude Opus 5.5, no API keys. **All 16 produced a valid film — and so did Claude Code with no skill at all (4.4 min).** What differed was time (2.0–23.5 min), sound (9/16 added it), and having a distinct look (10/16). Conclusion: a skill earns its place by giving you a *look*, a *workflow*, *footage editing*, *verification*, or *speed* — not by making video possible. HyperFrames (the renderer already used in this repo) was the slowest at 23.5 min but produced a distinctive look; `vincentsch/explainroo` was fastest at 2.0 min; `remotion-dev/skills` rendered reliably in 4.5 min.
4. **This repo already has the right foundation.** `videos/` ships one reference HyperFrames project (`quran-reel-ash-sharh`) with vendored GSAP, Arabic fonts, deterministic audio and rendered MP4s; the two earlier promo projects were removed during the generic cleanup. The cheapest high-impact upgrade is *not* a new renderer: it is installing HyperFrames' own 9-skill plugin, adding `ffmpeg-skill` for local edits/QC, adding a short-form craft layer, and writing one orchestrator skill with a file-based stage contract.
5. **Merging is where quality comes from** — but merges fail in predictable ways: two renderers fighting over one timeline, duplicate skill names, contradictory instructions, context bloat, API-key sprawl, licence clashes and unpinned upstream scripts. Section 5 turns the best real-world projects into 10 reusable composition patterns and a failure-mode table.
6. **Treat third-party skills as code dependencies, not config.** Snyk's ToxicSkills audit (Feb 2026) scanned 3,984 public skills: 13.4% critical issues, 36% with prompt-injection patterns, 76 confirmed malicious payloads. A second study of 31,132 skills found 26.1% with at least one vulnerability and skills bundling executable scripts 2.12× more likely to be vulnerable. Vet, pin and sandbox (Section 5.5).
7. **Voice-first addendum (Section 9).** A 12-tool Arabic "reels factory" prompt adds one genuinely new mode: `input.mp3` → silence cuts → Arabic word timings → word-by-word RTL captions → `out/reel.mp4` via `npm run reel`. It is worth adding as **Stack E**, but three claims in the original prompt are unsafe as written: `useCurrentFrame()` alone does not frame-lock GSAP/anime.js/mo.js/Three.js, WhisperX needs an explicit Arabic wav2vec2 alignment model (and tashkeel handling), and RTL word spans reverse without `dir="rtl"`. GSAP is free-but-not-OSI and Remotion is source-available, not open source. Section 9 gives the eight corrections, the tool-by-tool verdict and a hardened Arabic prompt.

### The short list (verified 2026-11-25)

| Layer | Pick | Stars | Licence | Why |
|---|---|---:|---|---|
| Renderer (already here) | `heygen-com/hyperframes` | 90.1k | Apache-2.0 | HTML→deterministic MP4; 9 official skills, ~450 registry blocks, `reverse-any-video`, `style-sampling` |
| Local edit / QC | `kajisho5/ffmpeg-skill` | 11.0k | MIT | 42 typed FFmpeg tools + MCP + machine-readable contract; offline, self-verifying |
| Full pipeline (free) | `digitalsamba/claude-code-video-toolkit` | 2.8k | MIT | Script → voice/music/images → Remotion → QC → publish on open models |
| Alternative renderer | `remotion-dev/skills` | 8.0k | no licence file | Official React skills; captions, maps, render, docs, licence checks |
| Fast explainer | `vincentsch/explainroo` | 1.45k | MIT | Fastest benchmarked (2.0 min), own look + sound |
| Look libraries | `Vincentwei1021/video-shotcraft` / `lemomo-ai/lemo-opuscar` | 22.6k / 21.1k | Apache-2.0 / NOASSERTION ⚠ | 124 shot recipes; 99 film styles |
| Craft / short-form grammar | `iart-ai/motion-skills` (56 skills, 19 packs) + `LottieFiles/motion-design-skill` | 2.2k / 3.7k | MIT / MIT | Renderer-agnostic timing, hooks, captions, easing |
| No-footage reels | `artemnovitckii/claude-animation-skills` | 1.26k | MIT (README) | 11 styles; best worked example of merging 6 OSS tools |
| Content factory | `Ootto-AI/claude-content-skills` | 577 | MIT | Orchestrator + hooks/scripts/calendar + Obsidian memory, from 262 real posts |
| Creator suite | `tripathiadityap/claude-skills` | 0 | MIT | 25 skills, 6 bundles, one shared `PROFILE.md`, strict guardrails |
| Research / de-slopping | `mvanhorn/last30days-skill`, `Panniantong/Agent-Reach`, `blader/humanizer` | 75.0k / 114.7k / 73.5k | MIT | Trends, reference reels, human-sounding copy |
| Merge reference | `DojoCodingLabs/remotion-superpowers` | 188 | MIT | Skills + MCP + subagents + hooks in one plugin |
| Meta / discovery | `anthropics/claude-plugins-official`, `zhuyansen/awesome-claude-video-skills` | 48.2k / 2.7k | Apache-2.0 / mixed | Manifest spec; 554 graded repos + 16-skill benchmark |

---

## 1. Method, scope and caveats

- **Metadata**: every star count, licence and last-push date in this document and in `tool-matrix.csv` was read from `api.github.com/repos/<owner>/<repo>` on 2026-11-25 (via `gh api`), not copied from blog posts. Star numbers move quickly in this ecosystem; treat them as a snapshot.
- **Primary sources**: the repositories' own READMEs and SKILL.md files (fetched via the GitHub API), the [official Claude Code docs](https://code.claude.com/docs/en/skills) ([extension overview](https://code.claude.com/docs/en/features-overview)), [anthropics/skills](https://github.com/anthropics/skills), [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official), and the [Awesome Claude Video Skills](https://github.com/zhuyansen/awesome-claude-video-skills) catalogue (554 repos, security-graded, refreshed every 8h).
- **Secondary sources**: the [HeyGen "best Claude Code skills for video" review](https://hyperframes.heygen.com/blog/best-claude-code-skills-for-video), [7 open-source repos that turn Claude into a video studio](https://medium.com/@adarsh.subham55/7-open-source-repos-that-turn-claude-into-a-video-studio-and-the-best-trick-inside-each-one-04fa0fdf0dda), [6 animation skills for reels](https://novitckii.com/resources/animation-skills/), [7 open-source tools (Nov 2026)](https://ajseven.medium.com/7-open-source-tools-that-let-claude-code-create-videos-automatically-32c0a0c04329), [Composio skill best practices](https://composio.dev/content/top-claude-skills), [skill-chaining patterns](https://www.mindstudio.ai/blog/how-to-build-skill-system-claude-code-chaining-pipelines), and security research from [Snyk ToxicSkills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) / [Cybedefend](https://www.cybedefend.com/en/blog/are-claude-code-skills-safe) / [NeuralTrust](https://neuraltrust.ai/blog/claude-code-skills).
- **"Open source"** here means a public repo with an explicit licence. Several popular projects are **NOT** cleanly licensed: `hypit-ai/hypit` (31.5k stars), `lemomo-ai/lemo-opuscar` (21.1k), `artemnovitckii/claude-animation-skills`, `tuzhechen2005/opus-video-skills`, `RahmanBuildsAI/ravyn-reel-kit`, `fahmid-juboraj/reelforge` return `NOASSERTION`/no SPDX licence from GitHub even when the README says MIT; `anthropics/skills` has mixed licensing (most Apache-2.0, document skills historically source-available); `remotion-dev/skills` has no licence file. `OpenMontage` is AGPL-3.0 and `0xsline/OpenChatCut` AGPL-3.0; `op7418/guizang-product-video-skill` AGPL-3.0. Remotion itself requires a company licence for teams >3 people — relevant to `it-reelsmaker`, `remotion-superpowers`, `video-shotcraft`.
- **Sandbox reality**: this repo's `videos/README.md` documents that apt and Chrome's CDN were blocked and the toolchain was assembled from npm/PyPI only. Recommendations therefore prioritise offline/keyless tools and note every API key explicitly.

---

## 2. Landscape: the five layers

| # | Layer | Job | Output artifact | Representative open-source tools |
|---|---|---|---|---|
| 1 | **Research & strategy** | Find a proven format, trend, audience question, reference reel | `brief.md`, trend notes, teardown | `mvanhorn/last30days-skill`, `Panniantong/Agent-Reach`, `Ootto-AI` `reel-analyzer` / `trend-spotter` / `going-viral`, `beatra-ai/viral-video-remake-skill`, `hypit-ai/hypit` |
| 2 | **Hook & script** | 1–3s hook, 30–45s script, on-screen text, shot list, caption/hashtags | `script.json`, `storyboard.json` | `Ootto-AI` `viral-hook-writer`/`reel-scripter`/`reel-builder`, `tripathiadityap/claude-skills` creator-video, `sergebulaev/tiktok-skills`, `Melvynx/video-agent-skills`, `blader/humanizer` |
| 3 | **Renderer** | Deterministic frames from code | `index.html` / React composition → MP4 | `heygen-com/hyperframes`, `remotion-dev/skills`, `OpenMontage`, `OpenChatCut`, `vincentsch/explainroo`, `murathany7/reel-studio`, `digitalsamba/claude-code-video-toolkit` |
| 4 | **Edit / captions / audio / QA** | Cut footage, word-timed captions, loudness, safe areas, frame checks | `master.mp4`, `.srt`, QA report | `kajisho5/ffmpeg-skill`, `kurbaitaev/ghost-editor`, `itpartypattaya/reels-montage`, `browser-use/video-use`, `iart-ai/tiktok-video-skills`, `artemnovitckii/claude-animation-skills` |
| 5 | **Publish / learn** | Schedule, post, reply, read analytics, feed winners back into memory | posts, metrics, updated brand memory | `sergebulaev/tiktok-skills` (Publora/Apify), `opus-pro/opus-skills`, `mutonby/openshorts-plugin` (MCP), `dan2756/ReelForge`, `Ootto-AI` `ai-brain` / `content-calendar` |

**Look/style libraries cut across layers 2–3**: `Vincentwei1021/video-shotcraft` (124 shot recipe cards), `lemomo-ai/lemo-opuscar` (99 film styles), `LottieFiles/motion-design-skill` (timing/easing), `iart-ai/motion-skills` (56 skills in 19 packs), `alchaincyf/huashu-art-motion` (35 artistic styles, Chinese), `diffusionstudio/lottie`.

**Packaging/standards layer**: `anthropics/claude-plugins-official` (plugin manifest, marketplace schema, `plugin.json`, `.mcp.json`, `commands/`, `agents/`, `skills/`), `anthropics/skills` (the Agent Skills format + `template/` + `spec/`), `vercel-labs/skills` (`npx skills add <repo>` / `npx skills update`), `gh skill install`, and `High56/short-video-skills` (a meta-plugin that chooses and installs 8 packs from their original creators).

---

## 3. Verified shortlist, by layer

### 3.1 Foundations / renderers / frameworks

| Repo | ★ | Licence | Last push | Install | Distinctive value |
|---|---:|---|---|---|---|
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 90,070 | Apache-2.0 | 2026-11-25 | `/plugin marketplace add heygen-com/hyperframes` → `/plugin install hyperframes@hyperframes`; or `npx skills add heygen-com/hyperframes` | HTML/CSS/GSAP → deterministic MP4. Ships **9 skills** (`hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `remotion-to-hyperframes`, `reverse-any-video`, `style-sampling`, `slideshow`, `figma`) and a ~450-block registry. `reverse-any-video` rebuilds a reference clip as an editable project; `style-sampling` makes a new episode in a proven style. Used by this repo already. |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | 8,000 | no licence file | 2026-11-24 | `npx remotion skills add` / `npx skills add remotion-dev/skills` / `gh skill install remotion-dev/skills` | 14 official skills: best-practices, create, markup, studio, render, maps, elements, captions, saas, interactivity, docs, license, upgrade, multimedia. Best React-native path. |
| [OpenMontageInc/OpenMontage](https://github.com/OpenMontageInc/OpenMontage) | 83,301 | AGPL-3.0 | 2026-11-16 | see repo | 12 production pipelines, 100+ tools, 700+ skill/knowledge files. Graded **CAUTION** in the awesome list; 8.6 min in benchmark (no sound). |
| [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) | 2,763 | MIT | 2026-11-25 | `git clone … && uv sync && claude` → `/setup`, `/video` | The most complete free end-to-end toolkit: templates, brands, skills per craft, Qwen3-TTS/FLUX.2/ACE-Step on your own GPU, QC, vertical cut-downs, YouTube publish, MCP `video_job.py`. ~$0.33 measured for a 90s video. |
| [vincentsch/explainroo](https://github.com/vincentsch/explainroo) | 1,451 | MIT | 2026-11-23 | see repo | Benchmark #1: 2.0 min, sound, own look. |
| [murathany7/reel-studio](https://github.com/murathany7/reel-studio) | 5 | MIT | 2026-11-17 | `/plugin marketplace add murathany7/reel-studio` → `/plugin install reel-studio@reel-studio` | Brand folder (facts/colours/fonts/voice) separated from `looks/` (7 art directions); engine adapters (GSAP, Lottie/Rive, Pixi, Three.js, Blender, page capture) all on **one clock**; frame/text/layout QA; one composition → 9:16, 4:5, 1:1, 16:9. Tiny today, best architecture. |
| [DojoCodingLabs/remotion-superpowers](https://github.com/DojoCodingLabs/remotion-superpowers) | 188 | MIT | 2026-10-29 | `/plugin marketplace add DojoCodingLabs/remotion-superpowers` → `/plugin install remotion-superpowers@remotion-superpowers` then `/setup` | Layers official Remotion + ElevenLabs + Replicate skills with MCP servers (Pexels, TwelveLabs, KIE), 3 subagents, hooks and a `/review-video` self-fix loop. Best "merge" exemplar. |
| [0xsline/OpenChatCut](https://github.com/0xsline/OpenChatCut) | 3,331 | AGPL-3.0 | 2026-11-12 | see repo | Local-first conversational editor with multi-track timeline, Agent Skills, MCP, Remotion rendering. |

### 3.2 Craft, styles and short-form specialization

| Repo | ★ | Licence | Last push | What it uniquely gives |
|---|---:|---|---|---|
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 22,580 | Apache-2.0 | 2026-11-25 | 124 shot recipe cards, 209 style variants, tuned Remotion implementations, 149 SFX, a validated 10-shot template, music/VO/captions/B-roll. |
| [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 21,057 | NOASSERTION ⚠ | 2026-11-23 | 99 film styles in code (blueprint, risograph, ukiyo-e, newsreel, whiteboard…), each a written style guide + demo film, zero video model. |
| [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills) | 2,169 | MIT | 2026-11-18 | 56 skills in 19 packs; install only what you need (`npx skills add iart-ai/<pack>`). Every skill uses a *render a frame → screenshot → check* loop. |
| [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) | 3,682 | MIT | 2026-11-23 | Renderer-agnostic motion principles: timing, easing, choreography, animation quality. Zero deps. |
| [artemnovitckii/claude-animation-skills](https://github.com/artemnovitckii/claude-animation-skills) | 1,255 | MIT (README) | 2026-11-17 | 11 no-footage reel styles (`/graph`, `/map-route`, `/stick-figure`, `/kurzgesagt`, `/low-poly`, `/minecraft`…). JSON spec → template.html → HyperFrames → 1080×1920 MP4 + safe-area contact sheet. VO = Kokoro, word timings = Parakeet, all local. |
| [kaomei/stickman-video-director](https://github.com/kaomei/stickman-video-director) | 8,311 | MIT | 2026-11-24 | Script → faceless stickman reel, 20+ styles, VO/captions/SFX. |
| [iart-ai/tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills) | 34 | MIT | 2026-11-11 | 4 focused skills: hook→retention→loop grammar, karaoke captions, drift-free countdown, lower thirds. Ideal composable grammar layer. |
| [social-media-skills/remotion-shorts-skill](https://github.com/social-media-skills/remotion-shorts-skill) | 26 | MIT | 2026-11-11 | Topic / data / changelog → kinetic-text shorts (great for DB statistics). |
| [hypit-ai/hypit](https://github.com/hypit-ai/hypit) | 31,499 | NOASSERTION ⚠ | 2026-11-25 | Clone a reference video as a reusable *workflow* (SVML), then swap host/hook/product/language → 100 variants. 6.5 min in benchmark. Verify licence before adopting. |
| [nexu-io/openmotion](https://github.com/nexu-io/openmotion) | 16,309 | Apache-2.0 | 2026-11-25 | Reference video → editable motion graphics with brand kit, open CapCut/Motion alternative. |
| [feitangyuan/onetake](https://github.com/feitangyuan/onetake) | 4,477 | NOASSERTION ⚠ | 2026-11-19 | Films that never cut — one idea running through all beats (benchmark #2 by eye, 8.5 min). |

### 3.3 Footage-first editing (talking head, long-form → shorts)

| Repo | ★ | Licence | Notes |
|---|---:|---|---|
| [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | 11,040 | MIT | `npx ffmpeg-skill setup`. 42 typed tools exposed as CLI **and** MCP (`contract --json`); probe → edit losslessly → check → verify; refuses overwriting declared inputs; local review page with platform safe areas. No cloud, no keys, no Python deps. |
| [browser-use/video-use](https://github.com/browser-use/video-use) | 31,573 | MIT | Raw takes folder → edited video; FFmpeg + optional HyperFrames/Remotion/Manim/PIL overlays; ElevenLabs key per review. Last push 2026-10-08. |
| [kurbaitaev/ghost-editor](https://github.com/kurbaitaev/ghost-editor) | 749 | MIT | 19 named styles ("Clean OS", "Caption News", "Telestrator", "Data Story"…), can learn a style from a reference reel. Mac Apple silicon; ffmpeg/Whisper/OpenCV; optional Gemini + ElevenLabs keys; 15–25 min per 60s reel. |
| [itpartypattaya/reels-montage](https://github.com/itpartypattaya/reels-montage) | 11 | MIT | Marketplace with core `it-reelsmaker` + optional `it-reelsmaker-online`. Word-level transcript → cut plan (**your yes**) → visual plan (**your yes**) → Remotion virtual camera → −14 LUFS master + cover + SRT + numeric report. Claims 16k+ installs in Anthropic's official directory (Nov 2026) despite low GitHub stars. |
| [hassancs91/claude-youtube-editor](https://github.com/hassancs91/claude-youtube-editor) | 392 | MIT | Talking head → cut, visuals, voice, SFX, thumbnail, upload. |
| [AgriciDaniel/claude-shorts](https://github.com/AgriciDaniel/claude-shorts) | 520 | MIT | Interactive long-form → short-form, Remotion animated captions, AI segment scoring (last push 2026-07-11). |
| [ghost1412/shortsflow](https://github.com/ghost1412/shortsflow) | 18 | MIT | Self-hosted OpusClip/Klap alternative: local Whisper, face tracking, active-speaker cuts, 9:16 captions. |
| [yerinsabraham/video-edit-skill](https://github.com/yerinsabraham/video-edit-skill) | 9 | Apache-2.0 | `/video-edit`: best takes, kinetic captions, words behind subject, logos, zooms, sound. |
| [beatra-ai/viral-video-remake-skill](https://github.com/beatra-ai/viral-video-remake-skill) | 10 | MIT-0 | Teardown a winning short into hook/beats/CTA, rebuild on your subject as beat frames + shot list + 9:16 clip. Paid Beatra credits only on explicit approval. |

### 3.4 Content creation (research, hooks, scripts, captions, carousels, calendars)

| Repo | ★ | Licence | Notes |
|---|---:|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 200,437 | mixed | Canonical format; `brand-guidelines`, `canvas-design`, `slack-gif-creator`, `frontend-design`, `theme-factory`, docx/pdf/pptx/xlsx, `skill-creator`. Install: `/plugin marketplace add anthropics/skills` → `document-skills` / `example-skills`. |
| [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | 114,690 | MIT | Read/search Reddit/X/YouTube, download reels → transcripts. Bundled into Ootto as the FIND step. |
| [blader/humanizer](https://github.com/blader/humanizer) | 73,538 | MIT | Strips AI tells from any script/caption; bundled into Ootto and tripathiadityap. |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 74,994 | MIT | Research any topic over the last 30 days across Reddit, X, YouTube, HN, Polymarket, web. |
| [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | 80,179 | MIT | Native PPTX decks from a topic — useful for carousels/slides. |
| [Ootto-AI/claude-content-skills](https://github.com/Ootto-AI/claude-content-skills) | 577 | MIT | 14 core + 30 Instagram skills. `/content-factory` runs FIND → STUDY → HOOK → SCRIPT → BUILD → CAPTION → POST → LEADS → COMPOUND; `ai-brain` stores winners in an Obsidian vault. Built from 262 real posts / 3.5M views. Install: `/plugin marketplace add Ootto-AI/claude-content-skills` → `/plugin install claude-content-skills@ootto-content-skills`. |
| [tripathiadityap/claude-skills](https://github.com/tripathiadityap/claude-skills) | 0 | MIT | 25 skills in 6 plugin bundles (`creator-core`, `creator-writing`, `creator-video`, `creator-podcast`, `creator-notion-ops`, `data-analytics`). A shared `PROFILE.md` is read by every skill first; global rules: no invented numbers, drafts only, prompt-injection safe, humanizer scrub. Video skills define style/pipeline/QC but bring **no renderer** (ffmpeg/faster-whisper/yt-dlp). |
| [sergebulaev/tiktok-skills](https://github.com/sergebulaev/tiktok-skills) | 146 | MIT | 3-second hooks, captions, trend mapping, profile optimiser, real Apify audience data, optional Publora scheduling; explicit publishing approval. |
| [Melvynx/video-agent-skills](https://github.com/Melvynx/video-agent-skills) | 214 | MIT | Markdown-only scripting/research/editing skills — zero dependency risk. |
| [ricocc/rico-skills](https://github.com/ricocc/rico-skills) | 278 | MIT | Content creation, design optimisation, resource curation. |
| [claude-world/notebooklm-skill](https://github.com/claude-world/notebooklm-skill) | 505 | MIT | Research → synthesis → content creation → packaging via NotebookLM. |
| [TheNoumanDev/zero-dollar-studio](https://github.com/TheNoumanDev/zero-dollar-studio) | 21 | MIT | Free guides + `make-video`, `snipshorts`, `cartoonsmith` skills for $0 YouTube production. |

### 3.5 Distribution, analytics and meta tools

| Repo | ★ | Licence | Notes |
|---|---:|---|---|
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 48,209 | Apache-2.0 | Reference plugin layout + immutable plugin slugs + `strict:false` skill-bundle marketplace entries. Third-party submissions now go through `claude.ai/directory/manage`. |
| [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) | 2,733 | mixed | 554 repos, security-graded, categorised (98 frameworks, 101 promo, 96 explainers, 68 editing, 73 shorts, …), plus the 16-skill end-to-end benchmark. |
| [obra/superpowers](https://github.com/obra/superpowers) | 326,496 | MIT | Skills framework/methodology (TDD, brainstorming, planning) — not video, but the canonical composable-skill discipline. |
| [mutonby/openshorts-plugin](https://github.com/mutonby/openshorts-plugin) | 136 | MIT | Skill + hosted MCP server: long video → captioned 9:16 clips → publish; OAuth, no local credentials, but footage leaves the machine. |
| [opus-pro/opus-skills](https://github.com/opus-pro/opus-skills) | 40 | MIT | Official OpusClip skill: clip long videos and post to social. |
| [dan2756/ReelForge](https://github.com/dan2756/ReelForge) | 8 | MIT | Faceless channel factory with 2D (Kokoro VO, code-drawn scenes) or 3D Blender modes, plus per-platform analytics dashboard — the only stack here that closes the analytics loop in-app. |
| [intelligent-iterations/ii-content-engine](https://github.com/intelligent-iterations/ii-content-engine) | 17 | MIT | Generate viral videos/carousels/reels and auto-post to TikTok/Instagram. |
| [High56/short-video-skills](https://github.com/High56/short-video-skills) | 1 | MIT | Meta-plugin that explains/installs 8 packs (HyperFrames, Shotcraft, Lemo Opuscar, Remotion Skills, Huashu Art Motion, LottieFiles, Video Toolkit, Video Agent Skills) from their original creators — an installer-by-guide pattern. |
| [scenario-labs/skills](https://github.com/scenario-labs/skills) | 4,024 | MIT | Model-routing skills for production-ready image/video/audio/3D assets (useful if adding generative B-roll). |
| [Cassette-Editor/oh-my-cassette](https://github.com/Cassette-Editor/oh-my-cassette) | 218 | MIT | AI co-editor plugin + MCP server for montage. |

---

## 4. What the benchmark actually says about "best"

Source: the [tested end-to-end table](https://github.com/zhuyansen/awesome-claude-video-skills#tested) (2026-10-11). Same brief: 15-second promo, five fixed lines of on-screen copy, 1920×1080 @ 30 fps, **no video/image/voice API keys**. Checks: plays, correct length/size, all five lines readable in frames sampled twice a second, picture moves.

| # | Skill | Time | Sound | Look |
|---:|---|---:|---|---|
| 1 | `vincentsch/explainroo` | **2.0 min** | Yes | own |
| 2 | `wshuyi/remotion-video-skill` | 3.4 min | No | default-ish |
| 3 | `vibe-motion/skills` | 4.4 min | Yes | own |
| — | **Claude Code, no skill** | **4.4 min** | — | baseline |
| 4 | `remotion-dev/skills` | 4.5 min | No | default-ish |
| 5 | `Barty-Bart/motion-graphics` | 4.7 min | No | own |
| 6 | `digitalsamba/claude-code-video-toolkit` | 5.5 min | Yes | default-ish |
| 7 | `diffusionstudio/lottie` | 5.6 min | No | default-ish |
| 8 | `hypit-ai/hypit` | 6.5 min | Yes | default-ish |
| 9 | `iart-ai/motion-skills` | 6.5 min | Yes | own |
| 10 | `charlie947/motion-graphics-skills` | 7.0 min | Yes | default-ish |
| 11 | `howseen-ai/claude-motion-design` | 7.9 min | Yes | own |
| 12 | `feitangyuan/onetake` | 8.5 min | Yes | own |
| 13 | `OpenMontage` | 8.6 min | No | own |
| 14 | `op7418/guizang-product-video-skill` | 8.6 min | Yes | own |
| 15 | `echris6/motion-video-kit` | 21.8 min | No | own |
| 16 | `heygen-com/hyperframes` | **23.5 min** | No | own |

**Interpretation for this repo:** for a simple promo the marginal value of a skill is low; for repeatable branded reels the value is (a) a recognisable look, (b) word-timed captions and sound, (c) automated frame/QA checks, (d) a re-runnable composition rather than a one-off render. HyperFrames is slow but scored "a look of its own" and its 9-skill plugin adds capabilities no other renderer has (`reverse-any-video`, `style-sampling`, `remotion-to-hyperframes`, 450-block registry). Keeping it is rational; the fix is to put it behind an orchestrator that does the writing/research before rendering, so the expensive render only happens once per approved storyboard.

---

## 5. The merging study — how the best projects combine tools

### 5.1 Nine real-world case studies

| Project | What it merges | The transferable trick |
|---|---|---|
| **HyperFrames** (9 skills, Apache-2.0) | One versioned plugin bundling core/CLI/registry/media/reverse/style/figma/slideshow/Remotion-port skills + ~450 reusable blocks | Ship skills as **one versioned bundle**; keep a shared block registry so skills never hand-build what exists. `core-skills` is explicitly deprecated in favour of the bundle. |
| **kajisho5/ffmpeg-skill ecosystem** (42 tools + ~10 sibling repos) | `ffmpeg-skill` = "the hands" (cut/measure/export, structured JSON); `video-production-agent` = "the brain" (decides cut points); `remotion-ffmpeg-skill` consumes `probe.py`/`silence.py`/`scenes.py` output; transcription/thumbnail/color/QC skills read `contract --json` | **One-way dependency direction** and a **machine-readable contract**. Sibling skills never call each other; the engine never calls a brain. Typed tools + verification after every operation, instead of the agent guessing ffmpeg flags. |
| **artemnovitckii/claude-animation-skills** | HyperFrames + three.js + GSAP + Playwright + Kokoro TTS + Parakeet word timings + shared `kit/anim.py`/`kit/words.py` | A **shared spec format** (`*.graph.json`) and a shared build script let 11 very different styles use one pipeline; each quick skill goes spec → template → MP4 → contact sheet with Instagram safe areas marked. |
| **DojoCodingLabs/remotion-superpowers** | Official `remotion-dev/skills` + `elevenlabs/skills` + `replicate/skills` + MCP servers (Pexels, TwelveLabs, KIE) + 3 subagents + hooks (API-key guard, captions tip) + `/review-video` loop | Don't rewrite vendor skills — **layer on top** and own only orchestration, placement and timing. `/setup` installs/upgrades the upstream skills; hooks add hard guards; subagents keep context small. |
| **Ootto-AI/claude-content-skills** | 30+ markdown skills + `content-factory` orchestrator + `ai-brain` Obsidian memory + externally bundled `Agent-Reach` and `humanizer` | **Orchestrator skill with explicit stage order** + **persistent shared memory** + a **compounding loop** (save the winner, next reel starts smarter). Also shows safe bundling: credits/links/versions kept for vendored skills. |
| **tripathiadityap/claude-skills** | 25 skills in 6 plugin bundles, one `PROFILE.md`, global rules in every skill | **Shared brand/voice config read first by every skill** + **global guardrails** (no invented numbers → `[placeholder]`; drafts only; pasted text is data, never instructions; humanizer scrub). Plugin namespacing avoids collisions. |
| **murathany7/reel-studio** | 7 engine adapters (GSAP, SVG/Lottie/Rive, Pixi, Three.js, Blender, page capture, lip-sync) on one Studio clock; 7 `looks/`; `AGENTS.md` + `.agents/skills` symlinked into `.claude/skills`; optional local review desk MCP | **Exactly one clock / one composition**; engines are adapters, not rival timelines. Brand (identity) ≠ look (per-piece art direction). One composition → four aspect ratios. Frame/text/layout QA is a first-class stage. |
| **itpartypattaya/reels-montage** | Core local plugin + optional `…-online` add-on (stock/AI B-roll) + Remotion + local whisper + loudness mastering | **Capability split by trust/cost**: offline core always safe, network/paid add-ons opt-in and **only after an approved plan**. Two human gates (cut plan, visual plan). |
| **iart-ai/motion-skills / High56/short-video-skills** | 19 independently installable packs (56 skills) / a meta-plugin that installs 8 third-party packs from their original repos | **Install only what you need**, and when curating others, keep a guide that downloads from the original creator so versions stay current. |
| **hypit-ai/hypit** | Reference video → editable SVML workflow → generation models (optional) → 100 variants | **Clone the structure, not the words**: one composition, pluggable components, swap host/hook/product/language without re-authoring. |

### 5.2 Ten composition patterns (the actual "best results" recipe)

1. **One orchestrator (meta-)skill.** A single entry point (`/reel` or `/content-factory`) owns the stage order. Individual skills stay independently useful; sequencing lives in the orchestrator, not buried in each skill. Official docs and community practice agree: build your setup over time, keep `CLAUDE.md` for always-true rules, skills for repeatable procedures.
2. **File-based state with a stable schema.** Stages hand off JSON/Markdown files (`brief.json` → `script.json` → `storyboard.json` → `composition/index.html` → `qa/report.md`), not in-context blobs. Pass **references/paths**, not full transcripts; one source of truth; loose contracts (downstream reads only the fields it needs, extra fields allowed). This is the single most reliable fix for context loss across a long render.
3. **Exactly one renderer on one clock.** Choose HyperFrames **or** Remotion **or** Blender as the timeline owner. Other skills may produce specs, assets, captions, audio or stills, but must not define a competing timeline. If you must mix (e.g. Blender plates in a HyperFrames reel), pre-render the plate to a video file and import it, like `reel-studio`'s engine adapters.
4. **Brain / hands separation.** Decision skills (what to cut, what to say) upstream; execution skills (ffmpeg, renderer, ffmpeg-skill tools) downstream; dependencies one-way. Expose typed tools and a machine-readable contract so the agent composes operations instead of guessing shell flags.
5. **Namespacing + progressive disclosure.** Plugin skills are namespaced (`/plugin:skill`) so several plugins with a `captions` skill coexist; personal > project > bundled for identical *unnamespaced* names. Only `name` + `description` load at session start (~100 tokens each, with a documented ~2% description budget / 16,000-char fallback); bodies load on trigger; `references/` and scripts load on demand. Keep `SKILL.md` <500 lines, write trigger-rich descriptions, use `disable-model-invocation: true` for side-effecting skills and `context: fork` for heavy research.
6. **Layer all extension types deliberately.** `CLAUDE.md` = brand/legal/format rules; **skills** = workflows; **MCP** = external data/actions (stock, transcription, publishing); **hooks** = deterministic gates that must run every time (`PostToolUse` frame check, key guard); **subagents** = parallel research / teardown / QA without polluting main context. `remotion-superpowers` and `reel-studio` are working examples.
7. **Verify, then iterate — always.** Render → snapshot/contact sheet → Claude *looks* at frames → fix → re-render. Add automated checks: duration, fps, resolution, codec/audio present, loudness (−14 LUFS), no black/frozen/blank-first frame, safe zones (no text under Reels UI or on a face), text size/contrast, no invented numbers, word-level caption alignment. `ffmpeg-skill`, `reel-studio`, `artemnovitckii`, `it-reelsmaker` and `digitalsamba` all implement versions of this.
8. **Explicit approval and spend gates.** Approve the brief, storyboard and cut plan before rendering; paid model calls only after an explicit "yes" with a cost card (`beatra-ai` does this well). Publishing, DMs and comments are always draft-only unless the user says otherwise.
9. **Close the loop.** Post → collect metrics → classify winners → write back to brand memory (`ai-brain` / `PROFILE.md` / a `winners.md`) → next brief starts from proven hooks. This is what turns a pile of skills into a compounding system.
10. **Version and pin everything.** Pin marketplace repos to commits in a private marketplace, record Node/Python/ffmpeg versions in `CLAUDE.md`, and re-run `/doctor prompt-audit` after any skill change. Prefer official skills over forks; every fork is a maintenance liability.

### 5.3 How merges break (and the fix)

| Failure mode | Symptom | Fix |
|---|---|---|
| **Two renderers** | Two timelines, double-renders, contradictory `data-start` vs React `Sequence` values | One clock owner; adapters pre-render to files; a single `composition/` dir |
| **Duplicate skill names** | `/captions` from three packs silently overrides (enterprise > personal > project; plugin skills namespaced) | Install as plugins (namespaced) or rename directories; audit with `/context` and `/doctor` |
| **Contradictory instructions** | one skill "always ask", another "execute autonomously"; inconsistent output | Put global policy once in `CLAUDE.md`/`PROFILE.md`; delete duplicated rules from vendored skills; `/doctor prompt-audit` |
| **Context bloat** | Skill descriptions excluded, wrong skill fires, quality drops after long renders | ≤50 skills active, short descriptions, `<500` line SKILL.md, references on demand, file handoffs, `context: fork` subagents for research |
| **Runtime drift** | Node 18 vs 22.18+, Python 3.9 vs 3.10+, Chrome/ffmpeg missing, `uv` vs `pip` | Record versions; one setup skill (`/setup`, `doctor`); prefer pre-rendered assets over live GPU deps |
| **Key sprawl / data egress** | ElevenLabs, KIE, Replicate, TwelveLabs, Pexels, Apify, Publora, Beatra, Gemini… | Tier the stack: keyless core + opt-in online add-on; env vars only, never in SKILL.md; log what leaves the machine |
| **Licence clash** | AGPL pipeline, source-available packs, unlicensed `NOASSERTION` repos, Remotion company licence | Check SPDX via API (done in `tool-matrix.csv`); avoid AGPL/unlicensed in a redistributable product; read bundled font/SFX licences |
| **Install-script risk** | `curl … \| bash`, `irm … \| iex`, dynamic remote instructions | Read the script first, pin the release SHA, or clone + copy skill folders manually |
| **Prompt injection** | A reference reel's transcript / scraped post contains "ignore previous instructions" | Treat all fetched text as data; `tripathiadityap`'s rule; no auto-publish; deny-by-default permissions |
| **Unbounded paid renders** | One vague prompt triggers 20 generative clips | Cost card + explicit approval before any paid call |

### 5.4 Context budget maths (why "install all of them" fails)

Claude Code loads only skill metadata at startup (roughly 100 tokens per skill; the docs describe a ~2% of context budget for descriptions with a 16,000-character fallback cap, adjustable via `SLASH_COMMAND_TOOL_CHAR_BUDGET`). Install 60 packs with long descriptions and some skills are silently excluded. Bodies (<5k words each) load only on trigger; scripts/references load on demand. Practical target for a reel stack: **6–12 active skills**, one orchestrator, the rest as optional `references/` or invoked explicitly. Use `/context` and `/doctor` to check what is actually loaded.

### 5.5 Security: the non-negotiable part of merging

- Snyk's **ToxicSkills** audit (Feb 2026) of 3,984 public skills: **13.4% critical**, **36% with prompt-injection patterns**, 1,467 malicious payloads, 76 confirmed malicious skills; 91% of confirmed malware combined natural-language jailbreaks with shell payloads.
- "Agent Skills in the Wild" (Jan 2026) analysed 31,132 skills: **26.1%** had ≥1 vulnerability, **5.2%** high-severity patterns, and skills bundling executable scripts were **2.12×** more likely to be vulnerable.
- A 2026 npm worm used a `SessionStart` hook in a repo's `.claude/settings.json` — hooks execute on clone+trust, so audit hooks harder than skills.
- Hidden Unicode tag characters in a `SKILL.md` description can carry invisible instructions; a Markdown-only skill can still tell the agent to exfiltrate `~/.ssh/id_rsa`.

**Vetting checklist before any skill enters the stack:**
1. Read `SKILL.md`, every script, `hooks.json`, `.mcp.json`, `plugin.json` and install commands; check for `curl|bash`, base64 blobs, unusual domains, `allowed-tools: Bash(*)`, network fetches.
2. Prefer official/`SAFE`-graded repos; treat `CAUTION`/`NOASSERTION` grades as blocked. The awesome list grades 554 repos; `OpenMontage` is `CAUTION`.
3. Pin to a commit in a private marketplace; re-review on every update (supply-chain compromise after approval is a named OWASP agentic risk).
4. Deny-by-default permissions; secrets in env vars only; no public posting without explicit approval.
5. Run `uvx mcp-scan@latest --skills`, `/doctor` and `/doctor prompt-audit` periodically.
6. For this repo specifically: never let a content skill read `.git/`, the DB or tokens; give it an explicit `videos/<project>/` working directory.

---

## 6. Recommended stacks for **this** repository

The repo already has a working offline HyperFrames toolchain (see `videos/README.md`) and three finished reels. All stacks below keep that renderer and add layers around it.

### Stack A — "Minimum viable, zero keys" (recommended starting point)

```
CLAUDE.md (brand + facts + guardrails)
  └── /reel  (custom orchestrator — see stack-blueprint/)
        ├── research:  mvanhorn/last30days-skill        (optional, ideas/trends)
        ├── craft:     LottieFiles/motion-design-skill  (timing/easing)
        │              iart-ai/tiktok-video-skills      (hook/retention/loop + karaoke captions)
        ├── copy:      blader/humanizer                 (final pass on all on-screen text)
        ├── render:    /plugin install hyperframes@hyperframes   (9 skills, 450 blocks)
        └── edit/QA:   npx ffmpeg-skill setup          (42 tools, probe→edit→verify, review page)
```

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
npx skills add LottieFiles/motion-design-skill
npx skills add iart-ai/tiktok-video-skills
npx skills add blader/humanizer
npx ffmpeg-skill setup && npx ffmpeg-skill doctor
```
Cost: €0 / no keys. Fits the sandbox (npm + PyPI only). Adds a look library, short-form grammar, word-timed captions and real QC to existing MP4s. **This is the best value-per-risk stack.**

### Stack B — "Content factory" (ideas → hooks → calendar → reels)

Stack A **+** `Ootto-AI/claude-content-skills` (orchestration/hooks/scripts/calendar/Obsidian memory) **+** `tripathiadityap/claude-skills` (25 creator skills, shared `PROFILE.md`, carousels, YouTube packaging, transcript moments) **+** `sergebulaev/tiktok-skills` (platform captions/trends, optional scheduling). All markdown-only, no renderer of their own — they feed `reel-state.json` into HyperFrames. Pick **one** orchestrator: either `/content-factory` or your own `/reel`; do not run both (duplicate stage order = conflict).

### Stack C — "Studio with AI media" (best ceiling, real costs)

Stack A/B **+** one of: `DojoCodingLabs/remotion-superpowers` (if you switch to Remotion: ElevenLabs VO/music/SFX, Pexels stock, KIE/Replicate image+video, TwelveLabs review) or `digitalsamba/claude-code-video-toolkit` (Remotion + open models on your own GPU, ~$0.33/90s) **+** `scenario-labs/skills` for model routing. Requires Node 22.18+, API keys, and a decision on Remotion's company licence. Use when a reel needs a voice, generated B-roll or 100 variants.

### Stack D — "Footage-first" (editing local footage / talking heads)

Stack A **+** one editor: `kurbaitaev/ghost-editor` (19 styles, style-from-reference, Mac only) or `itpartypattaya/reels-montage` (approval gates, −14 LUFS, brand profile, cross-platform) or `0xsline/OpenChatCut` (timeline + MCP). All three ultimately use ffmpeg/Remotion — `ffmpeg-skill` remains the shared "hands" layer, and no second timeline owner is introduced.

### Stack E — "Audio-first Arabic factory" (from the 12-tool prompt, Section 9)

Stack A **+** Auto-Editor/`ffmpeg-skill` silence cuts **+** WhisperX Arabic word timings **+** an RTL karaoke caption component **+** `npm run reel`. Starts from `input.mp3` instead of a topic. Default renderer stays HyperFrames (native seek adapters for GSAP/anime.js/Three.js); Remotion is the opt-in variant when editable React props are essential (`@remotion/gsap` mandatory). Full corrections, verdicts and the hardened prompt are in Section 9 and [`stack-blueprint/audio-first-arabic/`](stack-blueprint/audio-first-arabic/).

### Trade-off table

| Stack | Keys | Setup | Time/reel | Look control | Risk |
|---|---|---|---|---|---|
| A | none | ~15 min | render-bound (HyperFrames ~10–25 min) | high | low |
| B | none | ~30 min | + research/writing | high | medium (instruction conflicts) |
| C | 5–8 keys | 1–2 h | + generation time | very high | high (cost, licences, egress) |
| D | optional Gemini/ElevenLabs | ~45 min | 15–25 min edit | medium-high | medium (OS/hardware limits) |
| E | none after model cache | 1–2 h (models ~5 GB) | ASR + render | high | medium (Arabic alignment, RTL bidi, determinism) |

---

## 7. Concrete blueprint: a nine-stage pipeline for the reel harness reels

Implemented as copy-ready files in [`stack-blueprint/`](stack-blueprint/). Design rules: one orchestrator, one renderer, file-based handoffs, explicit gates, verification every stage, no invented numbers — every statistic on screen must come from the top-level `README.md` or be queried from `config/facts.json` (12,480 clips · 36 templates · 9 formats · 12,480 captions · Alpha 91 / Beta 89 / Gamma 84).

| # | Stage | Owner skill / tool | Input → output | Gate |
|---|---|---|---|---|
| 0 | Brand & facts | `CLAUDE.md` + `brand.md` | repo README/DB → verified fact list | facts signed off, `[placeholder]` for gaps |
| 1 | Research | `last30days-skill` / `Agent-Reach` / `reel-analyzer` | topic → `brief.json` (goal, audience, 3 reference reels, teardown) | approve brief |
| 2 | Hook & script | `viral-hook-writer` / `iart-ai:short-form-video` / `humanizer` | brief → `script.json` (10 hooks ranked, 30–45s script, on-screen text) | approve chosen hook |
| 3 | Storyboard | `reel-builder` / `LottieFiles:motion-design` / `shotcraft` look cards | script → `storyboard.json` (beats with `t0`, `t1`, visual, SFX, caption, source) | **approve before any render** |
| 4 | Compose | `hyperframes` skill + `hyperframes-registry` blocks | storyboard → `composition/index.html` + `hyperframes.json` + vendored assets | `npm run check` |
| 5 | Audio | ffmpeg-skill / deterministic pad or local TTS | → `assets/music.wav`, `.srt`, word timings | waveform + loudness check |
| 6 | Render | `hyperframes-cli` `render` | → `renders/*.mp4` (9:16 1080×1920, 30fps, H.264+AAC) | snapshot at 1/3/7/12s |
| 7 | QA | ffmpeg-skill `probe`/`check` + frame QA + text/layout QA | → `qa/report.md` (duration, fps, LUFS, safe zones, contrast, no black/frozen frames, all copy readable, no invented numbers) | **auto-fix loop max 2 passes** |
| 8 | Package | `creator-video` / `tiktok-skills` / `openshorts-plugin` (opt-in) | caption, hashtags, cover frame, `.srt`, 1:1/16:9 cut-downs, calendar entry | drafts only; publish on explicit yes |
| 9 | Learn | `ai-brain` / `winners.md` | analytics → next brief's hook bank | weekly |

**Stage-state contract** (one file, `reel-state.json`, written by the orchestrator; see `stack-blueprint/reel-state.example.json`): stable keys (`project`, `stage`, `facts`, `hook`, `script`, `beats`, `paths`, `qa`, `approvals`), loose downstream reads, paths not blobs.

**Directory layout** (fits the existing `videos/` convention):
```
videos/<reel-name>/
├── CLAUDE.md, AGENTS.md        # always-on rules, import ../../research/stack-blueprint/CLAUDE.md.snippet
├── reel-state.json             # single source of truth
├── brief.md, script.json, storyboard.json
├── assets/                     # gsap.min.js, fonts, music.wav, stills (vendored for offline)
├── composition/index.html      # the ONLY timeline owner
├── hyperframes.json, meta.json, package.json
├── renders/<name>.mp4
└── qa/report.md + contact-sheet.jpg
```

**First three experiments** (each isolates one variable, per `Ootto`'s A/B hook rule):
1. Re-render the reference reel with only the first 3 seconds changed (3 hook variants), same body — measure which hook survives a mute first play.
2. A data-story reel from `config/facts.json` (verified product numbers) using `iart-ai/data-animation-skills` or `social-media-skills/remotion-shorts-skill` grammar, rendered via HyperFrames.
3. Feed a local footage clip through `ffmpeg-skill` probe/cut + `hyperframes:reverse-any-video` to rebuild a short as an editable project — tests the "reference → editable composition" merge with zero new keys.

---

## 8. How to evaluate whether the merged stack is actually better

| Metric | Baseline (no skill) | Target with stack A | How to measure |
|---|---|---|---|
| Time to first approved storyboard | ad hoc | <10 min | timestamps in `reel-state.json` |
| Render passes needed | 2–4 | 1 (+≤2 auto-fix) | count `qa/report.md` revisions |
| QA pass rate | manual eyeball | 100% automated checks | `ffmpeg-skill` probe + frame/text/layout QA |
| Copy accuracy | occasional hallucinated stat | zero unverified numbers | lint `script.json` against `facts` list |
| Visual consistency | varies per session | shared `brand.md` + `looks/` | side-by-side contact sheets |
| Context efficiency | n/a | ≤12 active skills, `/context` clean | `/doctor` + `/context` |
| Cost per reel | Claude plan only | €0 keys | ledger in `reel-state.json` |
| Content outcome | n/a | hook retention / saves / shares | platform analytics → `winners.md` |

Always A/B against the **no-skill baseline** — the 16-skill benchmark showed a plain agent already produces a valid 15-second film, so any added skill must demonstrably improve look, speed, sound, accuracy or reuse.

---

## 9. Addendum — the 12-tool Arabic "reels factory" list & prompt

A reader-supplied Arabic post describes a code-built reel factory: one prompt in Claude Code builds a local, vertical (1080×1920 / 30 fps) video pipeline from a voice file — **Auto-Editor** (cut silence) → **WhisperX** (word timings, Arabic) → **Remotion** (React scenes, all copy in props) → **GSAP / anime.js / mo.js / Rough.js / Three.js** (motion) → **FFmpeg** (`out/reel.mp4`), with `npm run reel`, stage-by-stage approvals and an Arabic README. It lists 12 tools and offers HyperFrames / Motion Canvas / Manim as fallbacks. This section records **what is worth adding** to the research above, what needs correcting, and how the two toolsets merge. Full verified data: [`audio-factory-matrix.csv`](audio-factory-matrix.csv). Hardened prompt and caption contract: [`stack-blueprint/audio-first-arabic/`](stack-blueprint/audio-first-arabic/).

### 9.1 Verified status of the 12 tools (2026-11-25)

Metadata from `api.github.com`, `registry.npmjs.org` and `pypi.org`. The post says "12 tools" and lists exactly 12 libraries/frameworks, then adds Claude Code as a 13th link — all 13 are checked below. "OSI" matters here because the brief asked for *open-source* tools — two of the 12 are not OSI open source.

| # | Tool | Repo / package | ★ | Licence | Current version | In the pipeline |
|---:|---|---|---:|---|---|---|
| 1 | Claude Code | `anthropics/claude-code` | — | proprietary | — | agent / orchestrator |
| 2 | Remotion | `remotion-dev/remotion` | 75,919 | **source-available**, `NOASSERTION` | 4.0.547 | React scenes; free only for individuals / ≤3 employees, else [Company Licence](https://www.remotion.dev/docs/license/pricing) |
| 3 | HyperFrames | `heygen-com/hyperframes` | 90,706 | **Apache-2.0** | 0.9.99 (repo pins 0.9.94) | HTML→MP4; already used by this repo |
| 4 | Motion Canvas | `motion-canvas/motion-canvas` | 20,270 | **MIT** | 3.17.2 | step-by-step explainers (not karaoke captions) |
| 5 | GSAP | `greensock/GSAP` | 31,305 | **Standard "no-charge" (free, NOT OSI)** | 3.15.1 | timelines / stagger / SplitText — all plugins free since 2025 ([overview](https://www.smashingapps.com/best-free-javascript-animation-libraries-in-2026/)) |
| 6 | anime.js | `juliangarnier/anime` | 75,105 | MIT | 4.5.0 | lightweight tweens (v4 API differs from v3) |
| 7 | mo.js | `mojs/mojs` | 18,950 | MIT | `@mojs/core` 1.7.1 | stamps / bursts |
| 8 | Rough.js | `rough-stuff/rough` | 21,482 | MIT | 4.6.6 | hand-drawn style; last push 2024-07-28 |
| 9 | Three.js | `mrdoob/three.js` | 119,467 | MIT | 0.187.0 | 3D via `@remotion/three` 4.0.547 |
| 10 | Manim | `ManimCommunity/manim` | 42,942 | MIT | Python | math explainers only |
| 11 | Auto-Editor | `WyattBlue/auto-editor` | 6,163 | **Unlicense** | 29.3.1 (Python ≥3.9) | silence cuts |
| 12 | WhisperX | `m-bain/whisperX` | 25,703 | **BSD-2-Clause** | 3.8.6 (Python ≥3.10, <3.14) | Arabic word timings |
| 13 | FFmpeg | `FFmpeg/FFmpeg` | 68,268 | LGPL/GPL **by build** | — | mux / QC |

**Skill wrappers that already exist** (so these raw tools don't have to be wired by hand): `kajisho5/ffmpeg-skill` (11.0k, MIT, 42 typed FFmpeg tools + MCP), `kajisho5/transcription-skill` / `subtitle-skill` / `qc-skill` / `media-analysis-skill` / `remotion-ffmpeg-skill` (MIT, small, active), `remotion-dev/skills` (8.1k, 14 official skills incl. `/remotion-captions`), `LottieFiles/motion-design-skill` (3.7k, MIT), `iart-ai/tiktok-video-skills` (`caption-animation`, `short-form-video`), `iart-ai/webgl-animation-skills`, `adithya-s-k/manim_skill` (1.4k, MIT), `abhiemj/manim-mcp-server` (664). `artemnovitckii/claude-animation-skills` is a working local voice+word-timing pipeline that uses **Kokoro TTS + Parakeet** instead of WhisperX — a useful reference implementation.

### 9.2 Adoption verdict

| Verdict | Tools | Reason |
|---|---|---|
| **Adopt as-is** | HyperFrames, FFmpeg (via `ffmpeg-skill`), Claude Code orchestrator, Arabic fonts | Already in this repo; offline; deterministic; Apache-2.0 / MIT / OFL |
| **Adopt with fixes** | Auto-Editor, WhisperX, GSAP, Remotion, Three.js | Each has a hidden integration trap (§9.3) |
| **Optional / one-per-reel** | anime.js, mo.js, Rough.js, Motion Canvas, `@remotion/gsap` | Add one flavour at a time; each adds a clock or dependency burden |
| **Skip for reels** | Manim (+ `manim_skill`, `manim-mcp-server`) | Only for math explainers, exactly as the original prompt says |
| **Don't call it open source** | GSAP (no-charge licence), Remotion (source-available) | Both are free to use here, but neither is OSI open source |

**Genuinely new capability** brought by the list (not covered by Sections 2–3): a **voice-first input** (`input.mp3` → the reel follows the user's own recording), **word-level timing from real audio**, **Arabic RTL captions**, and a **single `npm run reel` repeat loop**. The prior stacks started from a topic/script; this one starts from sound. That's worth adding as a sixth stack.

### 9.3 Eight corrections that decide whether the factory actually renders

1. **`useCurrentFrame()` is necessary but not sufficient.** GSAP, anime.js, mo.js and Three.js advance on `performance.now()` / their own tickers. In Remotion a 4-second GSAP timeline can finish during the first captured second, leaving black frames; the fix is a **paused timeline seeked to `frame/fps`** — `@remotion/gsap` 4.0.547 does exactly this ([docs](https://www.remotion.dev/docs/gsap)), and HyperFrames ships native seek adapters for GSAP, anime.js, Lottie, Three.js and WAAPI ([HeyGen comparison](https://hyperframes.heygen.com/blog/hyperframes-vs-remotion), [independent comparison](https://docs.varg.ai/comparisons/varg-vs-remotion-vs-hyperframes)). Add a **determinism guard**: no `requestAnimationFrame`, `Date.now`, `performance.now`, `Clock`, `Math.random` (use a seeded RNG) or network-loaded assets; seek overlapping tweens from a reset state so a frame doesn't depend on the previously rendered one ([worked fix](https://github.com/ContentFries/visualfries/pull/66), [render contract](https://roo.beehiiv.com/p/claude-video-prompts)).
2. **Arabic word-by-word captions reverse without an explicit base direction.** Inline-block word spans are bidi-neutral, so the line defaults to LTR and the karaoke highlight walks the wrong way (documented in [OpenMontage issue #819](https://github.com/calesthio/OpenMontage/issues/819) / [fix #820](https://github.com/calesthio/OpenMontage/pull/820)). Set `dir="rtl" lang="ar"` + `direction: rtl` on the caption wrapper, detect direction from the words, isolate mixed Latin/numbers with `<bdi>`/`unicode-bidi: isolate`, and **highlight a word inside the full shaped line** rather than rendering an isolated word (Arabic letters reshape). Keep tashkeel in the display string. A font with full diacritics is required — this repo already vendors **Scheherazade New** and **Amiri** in `videos/quran-reel-ash-sharh/assets/fonts/`; add their SIL OFL licence files next to them if redistributed.
3. **WhisperX Arabic needs an explicit alignment model and clean audio.** Forced alignment is per-language: the HF defaults in `whisperx/alignment.py` include `"ar": "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"` ([source](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py)), but some 2026 guides still claim only en/fr/de/es/it have defaults ([WhisperX guide](https://vloggingpro.com/ai/tools/whisperx/)). Pass `--language ar --align_model jonatasgrosman/wav2vec2-large-xlsr-53-arabic` explicitly. **Strip tashkeel for alignment, keep it for display**; words whose characters aren't in the align dictionary (numbers, Latin brands) get interpolated timings — flag them with `score: 0` and verify. For one speaker, **skip diarization** so no Hugging Face token is needed. Export a 16 kHz mono WAV for alignment; cache models locally (first run downloads several GB).
4. **Silence cuts must precede alignment — and stay consistent.** The original order (Auto-Editor → WhisperX) is correct. Never cut after timing without remapping: keep Auto-Editor's edit-decision list and apply `clean_start = raw_start − Σ(removed_before_start)` to every word/scene boundary. Alternatively skip Auto-Editor and use `ffmpeg-skill`'s `silence.py` transcription-aware cuts, which already returns structured JSON.
5. **Don't mux twice.** Remotion's render (and HyperFrames') already combines video + audio. Use FFmpeg/`ffmpeg-skill` afterwards for loudness (≈ −14 LUFS), transcription to `.srt`, platform re-frames and `ffprobe` verification — not a second naive `-c:v copy` mux, which is where A/V drift appears.
6. **Licensing and reproducibility.** Remotion is free for individuals and companies ≤3 people, otherwise $25/seat or $0.01/render ([official pricing](https://www.remotion.dev/docs/license/pricing)); GSAP is 100% free but not open source; FFmpeg's licence depends on the build (LGPL vs GPL); fonts/models have their own licences. Pin every version, ask before installing, record Node/Python versions in a `doctor` script, and never run unpinned `curl … | bash`.
7. **Sandbox reality for this repo.** `videos/README.md` documents that apt and Chrome's CDN are blocked and the toolchain came from npm + the `imageio-ffmpeg` PyPI wheel via `HYPERFRAMES_BROWSER_PATH` / `HYPERFRAMES_FFMPEG_PATH` / `HYPERFRAMES_FFPROBE_PATH`. On this machine `ffmpeg`/`ffprobe` are **not on PATH** (verified), Node/npm/Python are. WhisperX's model downloads from Hugging Face would be blocked here — plan a pre-seeded `models/` cache or run the ASR step on a normal machine and commit only `words.json`.
8. **Gates and verification.** Keep the prompt's "stop after each stage" behaviour, add `reel-state.json` + `qa/report.md` from `stack-blueprint/`, require a frame contact sheet, caption-readability check, safe zones, and "no invented numbers" rule; publishing and paid calls remain explicit-approval only.

### 9.4 How the 12 tools merge into the five-layer model

| Layer | From the Arabic list | From the researched skill ecosystem | Merged choice |
|---|---|---|---|
| 1 Research | (none — audio is the input) | `last30days-skill`, `Ootto` `reel-analyzer`, `Agent-Reach` | Optional: only when choosing a topic before recording |
| 2 Hook/script | the recording itself, all copy in one props file | `viral-hook-writer`, `humanizer`, `tripathiadityap` `PROFILE.md`, no invented numbers | `script.json` / props file with verified facts; humanizer pass |
| 3 Renderer | Remotion (props) or HyperFrames fallback | HyperFrames' 9-skill plugin + registry, `remotion-dev/skills`, `reel-studio`'s one-clock rule | **One owner**: HyperFrames for this repo; Remotion only if React props are essential |
| 4 Edit / captions / QA | Auto-Editor, WhisperX, FFmpeg, GSAP/anime/mo/Rough/Three | `ffmpeg-skill` (+ transcription/subtitle/QC siblings), `iart-ai` caption grammar, `LottieFiles` motion principles | Typed tools + file contracts + paused/seeked animation adapters + `qa/report.md` |
| 5 Publish / learn | Arabic README, `npm run reel` | `content-calendar`, `ai-brain`, analytics skills | `winners.md` hook bank, drafts-only publishing |

### 9.5 Stack E — audio-first Arabic reel factory

**E-HF (recommended here):** `input.mp3` → Auto-Editor/`ffmpeg-skill` silence cuts → WhisperX Arabic word timings (`words.json`) → HyperFrames `composition/index.html` (GSAP paused+seeked, vendored Arabic fonts, RTL caption component) → `hyperframes render` → `ffmpeg-skill` probe/loudness/QC → `out/reel.mp4` + `.srt` + Arabic README. `npm run reel` chains all stages. No API keys after models are cached.

**E-Remotion (if editable React props matter):** same stages, with `remotion-dev/skills`, `@remotion/gsap` (paused timelines), `@remotion/three` (frame-driven), `delayRender()` for font loading, and no `rAF`/`Date.now`/`Math.random`; check the Company Licence before distributing.

**Ready-made test data in this repo:** `videos/quran-reel-ash-sharh/assets/recitation.wav` (28.0 s, 48 kHz stereo), eight verse boundaries already found by waveform envelope analysis, eight scene images, and vendored Arabic fonts. That is an ideal first `input.mp3`. ⚠️ **Caveat:** Qur'anic recitation with full tashkeel/tajwid is the hardest case for generic ASR alignment — don't let a model "correct" the verse text; use the fixed, reviewed text as the alignment target (or keep the existing manual verse boundaries) and verify word times by eye. The `words.example.json` in the blueprint uses a neutral Arabic line for this reason.

See [`stack-blueprint/audio-first-arabic/PROMPT.ar.md`](stack-blueprint/audio-first-arabic/PROMPT.ar.md) for the **hardened Arabic prompt** (keeps the original's 5 stages, `input.mp3`, approvals, `npm run reel` and Arabic README, and adds the eight corrections above), plus `words.schema.json`, `words.example.json` and `README.md`.

---

## 10. Sources

**Official / primary**
- [Claude Code — Extend Claude Code (feature layering)](https://code.claude.com/docs/en/features-overview) · [Skills docs](https://code.claude.com/docs/en/skills) · [Plugin docs](https://code.claude.com/docs/en/plugins)
- [anthropics/skills](https://github.com/anthropics/skills) · [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) · [Agent Skills spec](https://agentskills.io/specification)
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) (README, `skills/*/SKILL.md`, `.claude-plugin/marketplace.json`) · [remotion-dev/skills](https://github.com/remotion-dev/skills)
- Project READMEs for every repo in [`tool-matrix.csv`](tool-matrix.csv) · GitHub REST API metadata (2026-11-25)

**Rankings / benchmarks / surveys**
- [Awesome Claude Video Skills — 554 graded repos + tested end-to-end benchmark](https://github.com/zhuyansen/awesome-claude-video-skills) · [live graded page](https://agentskillshub.top/best/claude-video-skills/)
- [The Best Claude Code Skills for Making Videos in 2026 (HeyGen/HyperFrames blog)](https://hyperframes.heygen.com/blog/best-claude-code-skills-for-video)
- [7 Open-Source Repos That Turn Claude Into a Video Studio](https://medium.com/@adarsh.subham55/7-open-source-repos-that-turn-claude-into-a-video-studio-and-the-best-trick-inside-each-one-04fa0fdf0dda) · [7 Open-Source Tools That Let Claude Code Create Videos Automatically](https://ajseven.medium.com/7-open-source-tools-that-let-claude-code-create-videos-automatically-32c0a0c04329) · [6 Claude Code Extension Skills](https://lucaberton.com/blog/claude-code-extension-skills-2026/) · [6 animation skills for reels](https://novitckii.com/resources/animation-skills/) · [Best Claude Code GitHub Repos 2026](https://www.ayautomate.com/blog/best-claude-code-github-repos)

**Composition / best practices**
- [Composio: Top 10 Claude Code Skills — combining multiple skills](https://composio.dev/content/top-claude-skills) · [Mindstudio: chaining skills into pipelines](https://www.mindstudio.ai/blog/how-to-build-skill-system-claude-code-chaining-pipelines) · [Mindstudio: skill collaboration patterns](https://www.mindstudio.ai/blog/claude-code-skill-collaboration-chaining-workflows) · [ClaudeCodeGuides: combine multiple skills](https://claudecodeguides.com/how-to-combine-multiple-claude-skills-in-one-project/) · [Multi-agent workflows: skills + subagents](https://getknack.ai/blog/claude-code-multi-agent-workflows) · [Shareuhack: skills content pipeline + context budget](https://www.shareuhack.com/en/posts/claude-code-skills-guide)

**Security**
- [Snyk ToxicSkills (Feb 2026)](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) · [Cybedefend: vetting skills & plugins](https://www.cybedefend.com/en/blog/are-claude-code-skills-safe) · [NeuralTrust: Claude Code Skills complete guide / OWASP mapping](https://neuraltrust.ai/blog/claude-code-skills) · [DEV: 7-check audit frame](https://dev.to/ventureio/are-claude-skills-safe-in-2026-what-the-snyk-toxicskills-audit-actually-found-1315)

**Addendum (Section 9): 12 tools, Arabic/RTL, determinism**
- Tool repos: [Remotion](https://github.com/remotion-dev/remotion) · [HyperFrames](https://github.com/heygen-com/hyperframes) · [Motion Canvas](https://github.com/motion-canvas/motion-canvas) · [GSAP](https://github.com/greensock/GSAP) · [anime.js](https://github.com/juliangarnier/anime) · [mo.js](https://github.com/mojs/mojs) · [Rough.js](https://github.com/rough-stuff/rough) · [Three.js](https://github.com/mrdoob/three.js) · [Manim](https://github.com/ManimCommunity/manim) · [Auto-Editor](https://github.com/WyattBlue/auto-editor) · [WhisperX](https://github.com/m-bain/whisperX) · [FFmpeg](https://github.com/FFmpeg/FFmpeg) · [Claude Code](https://claude.com/product/claude-code). Versions from `registry.npmjs.org` / `pypi.org`, metadata from `api.github.com`, all 2026-11-25.
- Licensing: [Remotion licence & pricing](https://www.remotion.dev/docs/license/pricing) · [GSAP pricing / free plugins](https://gsap.com/pricing/) · [GSAP 2026 overview](https://www.smashingapps.com/best-free-javascript-animation-libraries-in-2026/)
- WhisperX Arabic: [alignment.py default models (`"ar": "jonatasgrosman/wav2vec2-large-xlsr-53-arabic")`](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py) · [WhisperX limits & per-language alignment](https://vloggingpro.com/ai/tools/whisperx/) · [WhisperX 2026 guide](https://whipscribe.com/tools/whisperx)
- Determinism / animation clocks: [`@remotion/gsap` docs](https://www.remotion.dev/docs/gsap) · [HyperFrames vs Remotion (HeyGen)](https://hyperframes.heygen.com/blog/hyperframes-vs-remotion) · [independent comparison](https://docs.varg.ai/comparisons/varg-vs-remotion-vs-hyperframes) · [render-contract article](https://roo.beehiiv.com/p/claude-video-prompts) · [seek-order determinism fix](https://github.com/ContentFries/visualfries/pull/66) · [3D/GSAP determinism guard](https://github.com/FasalZein/motion-studio/issues/37)
- Arabic RTL captions: [OpenMontage issue #819](https://github.com/calesthio/OpenMontage/issues/819) · [fix PR #820](https://github.com/calesthio/OpenMontage/pull/820) · [RTL karaoke line-highlighting fix](https://github.com/twangyal/projects-monorepo/issues/355) · [Arabic RTL subtitle rendering notes](https://capzai.com/en/blog/how-to-add-arabic-subtitles-rtl-2026)

---

## Appendix A — Verified metadata notes

- Star counts are a live snapshot; the awesome list's own table (refreshed every 8h) already disagrees with some blog figures (e.g. `hyperframes` 60.3k in the Oct benchmark vs 90.1k now). Where a number is quoted from a blog, it is labelled as such.
- `NOASSERTION` from the GitHub API means GitHub could not map the licence to SPDX — **not** necessarily "no licence". `hypit-ai/hypit`, `lemomo-ai/lemo-opuscar`, `artemnovitckii/claude-animation-skills`, `tuzhechen2005/opus-video-skills`, `fahmid-juboraj/reelforge`, `RahmanBuildsAI/ravyn-reel-kit`, `feitangyuan/onetake`, `ww-w-ai/super-video-agent`, `Barty-Bart/motion-graphics`, `zhuyansen/awesome-claude-video-skills` fall in this bucket; read their LICENSE files before redistribution.
- Two repos redirect: `calesthio/OpenMontage` → `OpenMontageInc/OpenMontage`; `ghost1412/shorts-generator` → `ghost1412/shortsflow`; `vincentventalon/claude-code-video-editing-skill` → `vincentventalon/my-claude-skills`. Matrix uses canonical names.
- `itpartypattaya/reels-montage` has 11 GitHub stars but claims 16,000+ installs / 5,000+ active accounts in Anthropic's official plugin directory — a good reminder that GitHub stars under-count plugin-directory adoption.
