# Test plan — post-merge readiness

This is the acceptance checklist for the merged keyless bilingual reel harness. All commands run from the repository root on the current branch; after merging, the same tree is on `main`.

## 0. Preconditions

```bash
npm install
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
npm run doctor
```

Expected: `core_ok = true`, local `ffmpeg`/`ffprobe`, `/tmp/chromium`, all npm packages, all Python modules. `cached ASR models` is a warning here because Hugging Face is blocked. No API keys in env.

## 1. Bilingual offline smoke tests

```bash
npm run reel -- --lang ar --project videos/_template/ar-smoke --demo --offline --fps 12 --out out/ar-smoke.mp4
npm run reel -- --lang en --project videos/_template/en-smoke --demo --offline --fps 12 --out out/en-smoke.mp4
```

Expected:

| Check | Arabic | English |
|---|---|---|
| Align | `from-json`, 11 words | `from-json`, 18 words |
| Renderer | `hyperframes` | `hyperframes` |
| Output | 10.42 s, 1080×1920, H.264/AAC, 12 fps | 10.42 s, 1080×1920, H.264/AAC, 12 fps |
| Harness QA | `pass`, 24/24, 0 warnings | `pass`, 23/23, 0 warnings |

Omit `--fps 12` for the production default of 30 fps.

## 2. HyperFrames quality gate

```bash
npm run check -- --project videos/_template/ar-smoke
npm run check -- --project videos/_template/en-smoke
```

Expected: `Check passed`, `0 issues across 9 sample(s)`, 0 lint/runtime/motion/contrast/craft/audio errors, 38/38 and 47/47 WCAG AA text checks.

## 3. Visual / bilingual review

Open the live test dashboard at `/test/` (see §7) or open these files directly:

- `videos/_template/ar-smoke/qa/contact-sheet.jpg`
- `videos/_template/en-smoke/qa/contact-sheet.jpg`
- `out/ar-smoke.mp4`
- `out/en-smoke.mp4`
- `videos/_template/{ar,en}-smoke/qa/report.md`

Verify:

- Arabic is `dir="rtl"`, full shaped line, active word highlighted inside the line, highlight travels right-to-left.
- English is LTR, active word highlighted inside the line, highlight travels left-to-right.
- Latin/number tokens are isolated with `<bdi>`.
- Hook readable by 1.5 s; reel makes sense with sound off.
- No text under platform UI, no black/frozen/empty frames, no invented numbers.
- One audio stream, no double mux, loudness near −14 LUFS.

## 4. Real audio path

```bash
npm run reel -- --lang ar --project videos/my-ar-reel \
  --input /path/to/voice.wav --offline --out out/my-ar-reel.mp4
npm run reel -- --lang en --project videos/my-en-reel \
  --input /path/to/voice.wav --offline --out out/my-en-reel.mp4
```

`--offline` requires a reviewed `words.json` / `config/words.<lang>.example.json` whose timings already match `audio/clean.wav`. If silence was cut, remap through `audio/edits.json`. ASR must never rewrite reviewed text, especially Qur'anic recitation, numbers, or names.

## 5. Heavy ASR path (on a machine with Hugging Face access)

```bash
npm run models:ar
npm run models:en
npm run reel -- --lang ar --project videos/asr-ar --input /path/to/voice.wav --align-backend whisperx
npm run reel -- --lang en --project videos/asr-en --input /path/to/voice.wav --align-backend whisperx
```

Expected: Arabic uses `jonatasgrosman/wav2vec2-large-xlsr-53-arabic`; English uses `WAV2VEC2_ASR_BASE_960H`; tashkeel stays in `display` and is stripped in `align`; `score:0` words appear in QA. One speaker uses no diarization and no HF token.

In this sandbox these prefetches fail with TLS EOF to `huggingface.co` / `download.pytorch.org`; use the offline path here. See `docs/INSTALL.md`.

## 6. Fallback and determinism tests

```bash
# Chrome-less Pillow fallback
npm run reel -- --lang ar --project videos/_template/ar-fallback \
  --demo --offline --no-hyperframes --fps 12 --out out/ar-fallback.mp4

# auto-editor backend (falls back to FFmpeg silencedetect if its binary is blocked)
npm run clean -- --project videos/_template/ae-test --input videos/_template/ar-smoke/input/input.wav --backend auto-editor
```

Expected: fallback MP4 still has one audio stream and full-line Arabic captions; QA adds a warning that per-word highlight is simplified. Re-running the same command with the same inputs produces the same frames.

Also verify:

```bash
npm run skills:list
npm run skills:audit
npm run skills:enable -- --enable humanizer
npm run skills:enable -- --disable humanizer
```

No API keys, no paid calls, no publishing. `reel-state.json` cost stays `{api_calls: [], credits_spent: 0}`.

## 7. Live test dashboard

```bash
npm run test:serve
```

Then open `/test/` in the preview. The dashboard links the README, install/architecture/skills/testing docs, both MP4 drafts, both contact sheets, and both QA reports. Generated outputs are git-ignored; run §1 first if a link is missing. No external assets or services are used.

## 8. Exit criteria

- `npm run doctor` → `core_ok = true`.
- `npm run reel` → exit 0 for `ar` and `en`.
- `npm run qa` → `pass`, 0 warnings for both smoke tests.
- `npm run check` → `Check passed`, 0 issues for both projects.
- `hyperframes lint` → 0 errors / 0 warnings.
- No old database/promo content in tracked files.
- No API keys, tokens, paid calls, or publishing.
- `git status` contains no generated `node_modules/`, `.venv/`, `models/*`, `out/`, `reports/`, or `*-smoke/` artifacts.
