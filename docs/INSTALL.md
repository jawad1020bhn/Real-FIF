# Install reality — what worked in this sandbox

Date: 2026-11-25/26 UTC. Outbound access was limited to GitHub, npm, and PyPI hosts. Hugging Face, PyTorch model hosts, Chrome download CDNs, and apt were not available. **No API keys were used.**

## Environment

| Item | Value |
|---|---|
| Node.js | `v22.22.3` |
| npm | `10.9.8` |
| Python | `3.11.2` (system), `.venv` used for installs |
| System `ffmpeg` / `ffprobe` / Chrome | missing from PATH |
| Shared NSS/NSPR/GBM/ALSA/ATK libs | missing initially |
| Disk | ~20 GiB available at audit; `.venv` grew to ~7.7 GiB |

## 1. npm dependencies — worked after one pin fix

First `npm install` failed:

```text
npm error code ETARGET
npm error notarget No matching version found for @ffmpeg-installer/ffmpeg@4.1.0
```

`4.1.0` is the version of the platform binary package `@ffmpeg-installer/linux-x64`, not the wrapper. The wrapper was corrected to `@ffmpeg-installer/ffmpeg@1.1.0`; `@ffprobe-installer/ffprobe` was corrected to `2.1.2`. The retry succeeded: **348 packages added in 25 s**.

Installed npm layers:

- `hyperframes@0.9.100` (Apache-2.0)
- `gsap@3.15.1`, `animejs@4.5.0`, `@mojs/core@1.7.1`, `roughjs@4.6.6`, `three@0.187.0`
- `remotion@4.0.547`, `@remotion/cli`, `@remotion/gsap`, `@remotion/three` (opt-in only)
- `ffmpeg-skill@4.12.0`, `@ffmpeg-installer/ffmpeg@1.1.0`, `@ffmpeg-installer/linux-x64@4.1.0`
- `@ffprobe-installer/ffprobe@2.1.2`, `@ffprobe-installer/linux-x64@5.2.0`
- `@sparticuz/chromium@158.0.0`, `skills@1.9.0` (dev)

Local binaries now resolve to:

```text
node_modules/@ffmpeg-installer/linux-x64/ffmpeg    # libx264 + aac available
node_modules/@ffprobe-installer/linux-x64/ffprobe
node_modules/.bin/hyperframes
```

`npm run doctor` reports `core_ok = true`.

## 2. Python dependencies — venv required

System-wide `python3 -m pip install -r requirements.txt` failed with:

```text
error: externally-managed-environment
```

The working install was:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install arabic-reshaper==3.1.0 python-bidi==0.6.12
```

The last two packages are now pinned in `requirements.txt`. They exist because this Pillow build has no `libraqm`, so the Chrome-less fallback reshapes full Arabic lines with `arabic-reshaper` and reorders them with `python-bidi`.

Confirmed imports: `PIL`, `numpy`, `imageio_ffmpeg`, `soundfile`, `auto_editor`, `whisperx`, `faster_whisper`, `ctranslate2`, `torch`, `torchaudio`, `transformers`, `huggingface_hub`, `arabic_reshaper`, `bidi`.

Selected resolved versions: `whisperx 3.8.6`, `faster-whisper 1.2.1`, `ctranslate2 4.9.1`, `torch 2.8.0` + CUDA wheels, `torchaudio 2.8.0`, `transformers 4.57.6`, `huggingface-hub 0.36.2`, `auto-editor 29.3.1`, `Pillow 11.3.0`, `numpy 2.3.3`, `soundfile 0.13.1`, `imageio-ffmpeg 0.8.1`.

`.venv/` is git-ignored and not part of the saved workspace snapshot. Reproduce it from `requirements.txt`.

## 3. Auto-Editor — package worked, release binary did not

`auto_editor` imports correctly, but its first CLI invocation tried to download a release binary:

```text
Error downloading binary: <urlopen error TLS/SSL connection has been closed (EOF)>
Please download manually from: https://github.com/WyattBlue/auto-editor/releases/download/29.3.1/auto-editor-linux-x86_64
```

The harness therefore defaults to deterministic FFmpeg `silencedetect` + `loudnorm`. `--clean-backend auto-editor` is still available on a machine where that release is reachable; the script falls back to FFmpeg if the download fails.

## 4. Heavy ASR / model fetch — libraries worked, weights did not

WhisperX and faster-whisper Python packages installed successfully. Weight prefetch was attempted for both languages:

```bash
npm run models:ar   # scripts/install-models.py --lang ar
npm run models:en   # scripts/install-models.py --lang en
```

Arabic failed:

```text
ERROR: SSLError: HTTPSConnectionPool(host='huggingface.co', port=443):
Max retries exceeded with url: /api/models/jonatasgrosman/wav2vec2-large-xlsr-53-arabic/revision/main
(Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF)')))
```

English failed:

```text
ERROR: URLError: <urlopen error TLS/SSL connection has been closed (EOF)>
Downloading: "https://download.pytorch.org/torchaudio/models/wav2vec2_fairseq_base_ls960_asr_ls960.pth"
```

No weights were cached; `models/` contains only `README.md`. `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` are set in `.env.example`. The harness defaults to `--offline` / `--from-json` when `models/` is empty. One speaker requires no diarization and no HF token.

To prefetch on a normal machine, run the two commands above with Hugging Face reachable, then copy `models/` here or set `HF_HOME`. Do not set `HF_HUB_OFFLINE=1` during that prefetch.

## 5. Chromium / HyperFrames — worked offline

System Chrome and NSS/NSPR libraries were absent. `@sparticuz/chromium` ships `bin/al2023.tar.br` containing `libnss3.so`, `libnspr4.so`, and friends. `scripts/lib/paths.mjs` and `scripts/lib/paths.py` decompress that tarball into `vendor/bin/lib/lib/` (git-ignored) and set `LD_LIBRARY_PATH`. `@sparticuz/chromium.executablePath()` resolves to `/tmp/chromium`:

```text
Chromium 158.0.8127.0
ldd /tmp/chromium  →  no missing libraries
```

With `HYPERFRAMES_BROWSER_PATH=/tmp/chromium`, `HYPERFRAMES_FFMPEG_PATH`, `HYPERFRAMES_FFPROBE_PATH`, and `LD_LIBRARY_PATH` set, `hyperframes doctor` reports `✓ Chrome env: /tmp/chromium`. `hyperframes browser ensure` reports `Browser found / Source: env / Ready to render` and downloads nothing.

`hyperframes doctor` still marks `whisper-cpp`, Kokoro TTS, MusicGen BGM, and Docker as missing; those are optional and are not used by this harness. No API keys are needed.

## 6. End-to-end verification

Both languages were rendered with HyperFrames, not the Pillow fallback:

```bash
npm run reel -- --lang ar --project videos/_template/ar-smoke --demo --offline --fps 12 --out out/ar-smoke.mp4
npm run reel -- --lang en --project videos/_template/en-smoke --demo --offline --fps 12 --out out/en-smoke.mp4
npm run check -- --project videos/_template/ar-smoke
npm run check -- --project videos/_template/en-smoke
```

| Result | Arabic | English |
|---|---|---|
| Align backend | `from-json` (11 words) | `from-json` (18 words) |
| Renderer | HyperFrames | HyperFrames |
| Output | 10.42 s, 1080×1920, H.264 + AAC, 12 fps, ~0.72 MiB | 10.42 s, 1080×1920, H.264 + AAC, 12 fps, ~0.80 MiB |
| `npm run qa` | **PASS 24/24, 0 warnings** | **PASS 23/23, 0 warnings** |
| `hyperframes lint` | 0 errors / 0 warnings | 0 errors / 0 warnings |
| `hyperframes check --strict` | 0 issues, 38/38 WCAG AA | 0 issues, 47/47 WCAG AA |

`--fps 12` was used only to keep the smoke tests fast. Omit it for the default 30 fps. The full pipeline also verified FFmpeg `silencedetect`, `loudnorm`, `captions.srt`, `reel-state.json`, contact sheets, black-frame detection, and integrated-loudness checks.

## 7. Reinstall from a clean checkout

```bash
npm install
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
npm run doctor
npm run reel -- --lang ar --project videos/ar-reel --demo --offline
```

`node_modules/`, `.venv/`, `vendor/bin/lib/`, `models/*`, `out/`, and `reports/` are generated. Keep `package-lock.json`, `requirements.txt`, `config/`, `templates/`, `scripts/`, `prompts/`, `.claude/skills/`, and `vendor/skills/` in Git.

## 8. Licence / provenance notes

- `ffmpeg-skill` is installed as an npm package; its SKILL.md text is also pinned in `vendor/skills/`. Its MCP server and scripts are not launched here.
- HyperFrames is Apache-2.0. FFmpeg binaries are LGPL/GPL by build. GSAP is free under a Standard no-charge licence but is not OSI open source. Remotion is source-available and needs a company licence for larger teams.
- Vendored fonts include SIL OFL files for Scheherazade New and Amiri, and the DejaVu licence.
- Upstream Claude Code skills are stored as **text-only** `SKILL.md` snapshots pinned to commit SHAs; no upstream executable code, hooks, or MCP configs are vendored. See `docs/SKILLS.md`.
