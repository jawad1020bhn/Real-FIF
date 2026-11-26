#!/usr/bin/env python3
"""Stage 5 — HyperFrames render with an offline Pillow fallback.

Both paths produce a 1080x1920 H.264/AAC MP4 through the pinned local FFmpeg
binary. Audio is muxed exactly once: either by HyperFrames' <audio> tag or, for
the Pillow fallback, by the final FFmpeg command.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from paths import ffmpeg_bin, ffprobe_bin, chrome_bin, hf_bin, probe_json  # noqa: E402


def shape_text(text, lang):
    """Full-line Arabic shaping/reordering for the Chrome-less fallback."""
    if lang != "ar":
        return text
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text), base_dir="R")
    except Exception as exc:  # pragma: no cover - optional dependency
        print(f"[render] WARNING: Arabic shaping unavailable ({exc}); using unshaped text.", file=sys.stderr)
        return text


def wrap_text(draw, text, font, max_width, lang):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(shape_text(candidate, lang), font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return [shape_text(line, lang) for line in lines]


def hyperframes_render(project, out, fps, duration, quality):
    hf, chrome, ff, fp = hf_bin(), chrome_bin(), ffmpeg_bin(), ffprobe_bin()
    if not hf or not ff or not fp:
        return False
    env = os.environ.copy()
    env.update({
        "HYPERFRAMES_FFMPEG_PATH": ff,
        "HYPERFRAMES_FFPROBE_PATH": fp,
        "HYPERFRAMES_BROWSER_PATH": chrome or "",
        "CHROME_PATH": chrome or "",
        "PUPPETEER_EXECUTABLE_PATH": chrome or "",
        "HYPERFRAMES_TELEMETRY": "off",
        "HYPERFRAMES_NO_UPDATE_CHECK": "1",
        "DO_NOT_TRACK": "1",
        "LD_LIBRARY_PATH": f"{ROOT / 'vendor' / 'bin' / 'lib' / 'lib'}:{env.get('LD_LIBRARY_PATH','')}",
    })
    cmd = [hf, "render", str(project), "-o", str(out), "-f", str(fps), "-q", quality,
           "--format", "mp4", "--workers", "1", "--no-wait", "--no-browser-gpu",
           "--no-best-effort"]
    print("[render] HyperFrames:", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, env=env, cwd=ROOT)
    ok = r.returncode == 0 and out.exists() and out.stat().st_size > 1000
    if not ok and out.exists():
        out.unlink(missing_ok=True)
        print("[render] HyperFrames produced an incomplete file; discarded it.", file=sys.stderr)
    return ok


def pillow_render(project, out, fps, duration, lang):
    """Deterministic PNG frames without Chrome. Full shaped line, no isolated words."""
    from PIL import Image, ImageDraw, ImageFont

    words = json.loads((project / "words.json").read_text(encoding="utf-8"))
    langs = json.loads((ROOT / "config" / "languages.json").read_text(encoding="utf-8"))
    brand = json.loads((ROOT / "config" / "brand.json").read_text(encoding="utf-8"))
    copy = json.loads((ROOT / "config" / f"copy.{lang}.json").read_text(encoding="utf-8"))
    font_name = "ScheherazadeNew-Bold.ttf" if lang == "ar" else "DejaVuSans-Bold.ttf"
    font_path = project / "assets" / "fonts" / font_name
    if not font_path.exists():
        font_path = project / "assets" / "fonts" / "Amiri-Regular.ttf"
    big = ImageFont.truetype(str(font_path), 78) if font_path.exists() else ImageFont.load_default()
    head = ImageFont.truetype(str(font_path), 104) if font_path.exists() else big
    small = ImageFont.truetype(str(font_path), 42) if font_path.exists() else big
    palette = brand.get("palette", {})
    accent = palette.get("accent", "#D9A84E")
    bg = palette.get("background", palette.get("bg", "#07070A"))

    def rgb(value):
        value = value.lstrip("#")
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

    accent_rgb, bg_rgb = rgb(accent), rgb(bg)
    W, H = 1080, 1920
    frames = project / "frames"
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir(parents=True)
    n = max(1, int(duration * fps))
    headline = copy.get("hook", brand.get("name", "Reel"))
    subtitle = copy.get("subtitle", "")
    for i in range(n):
        t = i / fps
        im = Image.new("RGB", (W, H), bg_rgb)
        d = ImageDraw.Draw(im)
        for y in range(0, H, 12):
            k = max(0.0, 1.0 - abs(y - 520) / 1100)
            d.rectangle((0, y, W, y + 12),
                        fill=(int(bg_rgb[0] + 18 * k), int(bg_rgb[1] + 38 * k), int(bg_rgb[2] + 30 * k)))
        brand_text = shape_text(brand["name"], lang)
        d.text((W // 2, 115), brand_text, font=small, fill=accent_rgb, anchor="mm")
        for j, line in enumerate(wrap_text(d, headline, head, W - 150, lang)):
            d.text((W // 2, 350 + j * 120), line, font=head, fill="white", anchor="mm")
        for j, line in enumerate(wrap_text(d, subtitle, small, W - 180, lang)):
            d.text((W // 2, 560 + j * 58), line, font=small, fill=(215, 215, 210), anchor="mm")
        current = next((line for line in words["lines"] if line["start"] <= t <= line["end"] + 0.20), None)
        if current:
            d.rounded_rectangle((55, 1070, W - 55, 1410), radius=38, fill=(12, 12, 14))
            caption_lines = wrap_text(d, current["text"], big, W - 130, lang)
            y0 = 1235 - (len(caption_lines) - 1) * 52
            for j, line in enumerate(caption_lines):
                d.text((W // 2, y0 + j * 104), line, font=big, fill="white", anchor="mm")
            active = sum(1 for w in words["words"] if w["line"] == current["index"] and w["start"] <= t <= w["end"])
            radius = 8 + min(active, 8) * 5
            d.ellipse((W // 2 - radius, 1480, W // 2 + radius, 1496), fill=accent_rgb)
        d.rectangle((70, 1822, 1010, 1832), fill=(42, 42, 46))
        d.rectangle((70, 1822, 70 + int(940 * min(t / duration, 1)), 1832), fill=accent_rgb)
        im.save(frames / f"{i:05d}.png")
    silent = project / "video-only.mp4"
    cmd = [ffmpeg_bin(), "-y", "-hide_banner", "-framerate", str(fps),
           "-i", str(frames / "%05d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "20", "-preset", "veryfast", "-r", str(fps), str(silent)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:], file=sys.stderr)
        raise SystemExit("FFmpeg encode failed")
    shutil.rmtree(frames, ignore_errors=True)
    return silent


def mux_audio(silent, audio, out):
    cmd = [ffmpeg_bin(), "-y", "-hide_banner", "-i", str(silent), "-i", str(audio),
           "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
           "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:], file=sys.stderr)
        raise SystemExit("FFmpeg mux failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", choices=["ar", "en"], default="ar")
    ap.add_argument("--backend", choices=["auto", "hyperframes", "pillow"], default="auto")
    ap.add_argument("--quality", default="standard")
    ap.add_argument("--fps", type=int, default=0)
    args = ap.parse_args()

    project = Path(args.project).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    words = json.loads((project / "words.json").read_text(encoding="utf-8"))
    hp = json.loads((project / "hyperframes.json").read_text(encoding="utf-8"))
    fps = args.fps or int(hp.get("fps", 30))
    duration = float(hp.get("duration", words.get("duration", 10.4)))
    audio = project / hp.get("audio", "assets/audio.wav")
    if not audio.exists():
        raise SystemExit(f"ERROR: audio missing: {audio}")

    print(f"[render] ffmpeg={ffmpeg_bin()}  ffprobe={ffprobe_bin()}  chrome={chrome_bin() or 'unavailable'}", flush=True)
    used, ok = "hyperframes", False
    if args.backend in ("auto", "hyperframes"):
        try:
            ok = hyperframes_render(project, out, fps, duration, args.quality)
        except Exception as exc:
            print(f"[render] HyperFrames unavailable ({type(exc).__name__}: {exc})", file=sys.stderr)
    if not ok:
        if args.backend == "hyperframes":
            raise SystemExit("HyperFrames render failed and --backend=hyperframes was forced")
        used = "pillow-fallback"
        print("[render] Falling back to the offline Pillow frame renderer (no Chrome).", flush=True)
        silent = pillow_render(project, out, fps, duration, args.lang)
        mux_audio(silent, audio, out)
        silent.unlink(missing_ok=True)
    else:
        info = probe_json(ffprobe_bin(), out)
        streams = [s.get("codec_type") for s in info.get("streams", [])]
        if "audio" not in streams:
            silent = project / "hf-video-only.mp4"
            out.replace(silent)
            mux_audio(silent, audio, out)
            silent.unlink(missing_ok=True)

    info = probe_json(ffprobe_bin(), out)
    fmt = info.get("format", {})
    dur = float(fmt.get("duration", 0) or 0)
    size = out.stat().st_size
    print(f"[render] backend={used}  {out}  {size / 1024 / 1024:.2f} MiB  {dur:.2f}s")
    (project / "render.json").write_text(json.dumps({
        "backend": used, "output": str(out), "bytes": size, "duration": dur,
        "fps": fps, "audio": str(audio), "hyperframes_version": "0.9.100",
        "ffmpeg": ffmpeg_bin(), "chrome": chrome_bin(),
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
