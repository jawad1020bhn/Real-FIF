# Local model cache (git-ignored)

This harness uses **no API keys**. WhisperX / faster-whisper need model weights only when you run real ASR. Those weights are several GiB and are not committed.

## What happened in this sandbox (2026-11-25/26)

- `npm install` succeeded after correcting two pinned npm versions.
- `.venv/bin/python -m pip install -r requirements.txt` succeeded: `whisperx 3.8.6`, `faster-whisper 1.2.1`, `ctranslate2 4.9.1`, `torch 2.8.0` with CUDA wheels, `torchaudio 2.8.0`, `transformers 4.57.6`, `huggingface-hub 0.36.2`, `auto-editor 29.3.1`, `Pillow`, `numpy`, `soundfile`, `imageio-ffmpeg`, `arabic-reshaper`, and `python-bidi`. The venv is about 7.7 GiB and is excluded from Git.
- **Model prefetch failed.** `npm run models:ar` / `python3 scripts/install-models.py --lang ar` failed with `SSLError: HTTPSConnectionPool(host='huggingface.co' ...) TLS/SSL connection has been closed (EOF)`. `npm run models:en` / `--lang en` failed with `URLError: <urlopen error TLS/SSL connection has been closed (EOF)>` while reaching `download.pytorch.org`. Hugging Face and PyTorch model hosts are outside this sandbox's outbound allowlist. No weights were cached; `models/` contains only this README.
- `auto-editor`'s first-run CLI also tried to download its release binary from GitHub and hit a TLS EOF. The harness therefore uses deterministic FFmpeg `silencedetect` by default; the Python package is installed and imports correctly.
- HyperFrames' own `browser ensure` did **not** need a CDN: `@sparticuz/chromium` plus extracted NSS/NSPR libraries supplied `/tmp/chromium`, and `hyperframes doctor` reported `Chrome env: /tmp/chromium`.

## On a machine with Hugging Face access

```bash
npm install
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm run models:ar   # Arabic wav2vec2 alignment + faster-whisper large-v3
npm run models:en   # torchaudio English alignment + faster-whisper large-v3
```

Then copy `models/` (or the Hugging Face cache) into this repo, or set `HF_HOME=/path/to/cache`. Set `HF_HUB_OFFLINE=0` and `TRANSFORMERS_OFFLINE=0` only for that prefetch. One speaker requires **no diarization and no HF token**.

## Offline path (works here)

```bash
npm run reel -- --lang ar --project videos/ar-reel --demo --offline
npm run reel -- --lang en --project videos/en-reel --demo --offline
```

`--offline` uses `config/words.<lang>.example.json` as deterministic word timings. For real audio, supply a reviewed `words.json` already aligned to `audio/clean.wav`; see `docs/INSTALL.md` and `docs/ARCHITECTURE.md`.
