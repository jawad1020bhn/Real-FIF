# Videos — made with HyperFrames

[HyperFrames](https://github.com/heygen-com/hyperframes) (HeyGen, Apache 2.0) —
write HTML/CSS/GSAP, render deterministic MP4 with headless Chrome + FFmpeg.

## Install

Requirements: Node.js 22+ and FFmpeg (`ffmpeg` + `ffprobe` on PATH), plus Chrome/Chromium.

```bash
# CLI (no global install needed — npx fetches hyperframes@0.9.94, verified here)
npx hyperframes --version

# Agent skills / plugin (Claude Code, Codex, Cursor, …)
npx skills add heygen-com/hyperframes
# …or, inside a project:
npx hyperframes skills update
npx hyperframes browser ensure   # downloads chrome-headless-shell
npx hyperframes doctor           # checks Node / FFmpeg / Chrome
```

> Sandbox note (this environment): apt and Chrome's download CDN are blocked, so the
> toolchain was assembled from allowed registries only — CLI via npm, FFmpeg via the
> PyPI `imageio-ffmpeg` wheel, `ffprobe` built from the FFmpeg git mirror, Chromium via
> the npm `@sparticuz/chromium` package with NSS/NSPR libraries built from the
> mozilla/nss + mozilla/nspr git mirrors, wired in through
> `HYPERFRAMES_BROWSER_PATH`, `HYPERFRAMES_FFMPEG_PATH`, `HYPERFRAMES_FFPROBE_PATH`
> and `LD_LIBRARY_PATH`. On a normal machine the four commands above are all you need.

## Projects here

| Project | Output | Spec |
|---|---|---|
| `real-fif-promo/` | `renders/real-fif-promo.mp4` | 1920×1080, 30 fps, 20 s, H.264 + AAC |
| `real-fif-short/` | `renders/real-fif-short.mp4` | 1080×1920 (9:16), 30 fps, 12 s, H.264 + AAC |

Both are promos for this repo's FC 27 roster update for FIFA 14. All numbers on
screen come from the top-level `README.md` (25,305 players, 922 teams, 55 leagues,
43,066 names; spot-checked OVRs Mbappé 91, Messi 89, Ronaldo 84). Background audio
is a deterministic FFmpeg-synthesised pad/beat (`assets/music.wav`), GSAP is
vendored in `assets/` so compositions render offline.

## Edit / re-render

```bash
cd real-fif-promo            # or real-fif-short
npm run dev                  # live Studio preview in the browser
npm run check                # lint / runtime / layout / audio checks (ok: true)
npx hyperframes snapshot --at 1,7,12,17   # frame grabs for review
npm run render               # -> renders/*.mp4
```

Edit `index.html` (scene timings are the `data-start`/`data-duration` attributes
and the GSAP timeline at the bottom) and re-render — output is deterministic.
