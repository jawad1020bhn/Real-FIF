#!/usr/bin/env python3
"""Stage 6 — machine-readable QA, contact sheet and human-readable report."""
import argparse
import json
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from paths import ffmpeg_bin, ffprobe_bin, probe_json  # noqa: E402


def load(path, fallback=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return fallback if fallback is not None else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", choices=["ar", "en"], default="ar")
    ap.add_argument("--fps", type=float, default=0)
    args = ap.parse_args()

    project = Path(args.project).resolve()
    out = Path(args.out).resolve()
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    hp = load(project / "hyperframes.json")
    words = load(project / "words.json")
    render = load(project / "render.json")
    edits = load(project / "audio" / "edits.json")
    # QA reads the root plus every mounted sub-composition, so modular projects
    # still get caption, RTL, clock and network-asset checks.
    html_paths = [project / "index.html"]
    comp_dir = project / "compositions"
    if comp_dir.exists():
        html_paths.extend(sorted(comp_dir.rglob("*.html")))
    index = "\n".join(p.read_text(encoding="utf-8") for p in html_paths if p.exists())
    srt = (project / "captions.srt").read_text(encoding="utf-8") if (project / "captions.srt").exists() else ""

    checks, warnings = [], []

    def add(name, ok, detail, critical=True):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail), "critical": critical})
        if not ok and not critical:
            warnings.append(f"{name}: {detail}")

    ff, fp = ffmpeg_bin(), ffprobe_bin()
    add("ffmpeg + ffprobe", bool(ff and fp), f"{ff or 'missing'} / {fp or 'missing'}")
    add("output exists", out.exists(), str(out))
    size = out.stat().st_size if out.exists() else 0
    add("output > 100 KiB", size > 100_000, f"{size / 1024:.0f} KiB")

    info = probe_json(fp, out) if out.exists() else {}
    streams = info.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    fmt = info.get("format", {})
    duration = float(fmt.get("duration", 0) or 0)
    expected = float(hp.get("duration", words.get("duration", 0)) or 0)
    width = int(video.get("width", 0) or 0)
    height = int(video.get("height", 0) or 0)
    codec = video.get("codec_name", "")
    fps_raw = video.get("avg_frame_rate", "0/1")
    try:
        fps = float(Fraction(fps_raw))
    except Exception:
        fps = 0.0
    add("video stream", bool(video), f"{width}x{height} {codec} @ {fps:.2f} fps")
    add("1080x1920 vertical", width == 1080 and height == 1920, f"{width}x{height}")
    add("H.264 video", codec == "h264", codec or "missing")
    expected_fps = args.fps or float(hp.get("fps", 30))
    add("fps matches composition", abs(fps - expected_fps) <= 0.6, f"{fps:.2f} fps / expected {expected_fps:.0f}")
    add("duration matches composition", abs(duration - expected) <= 0.75, f"actual {duration:.2f}s / expected {expected:.2f}s")
    add("audio stream present", bool(audio), audio.get("codec_name", "missing"))
    add("audio muxed once", len([s for s in streams if s.get("codec_type") == "audio"]) == 1,
        f"{len([s for s in streams if s.get('codec_type') == 'audio'])} audio stream(s)")

    direction = "rtl" if args.lang == "ar" else "ltr"
    add("words.json direction", words.get("direction") == direction, words.get("direction", "missing"))
    add("language tag", words.get("language") == args.lang, words.get("language", "missing"))
    add("words + lines", bool(words.get("words")) and bool(words.get("lines")),
        f"{len(words.get('words', []))} words / {len(words.get('lines', []))} lines")
    unverified = words.get("unverified", [])
    add("word scores reviewed", not unverified, f"{len(unverified)} interpolated/unverified word(s)", critical=False)
    if unverified:
        warnings.append(f"Unverified word indices: {unverified}")
    if edits.get("removed"):
        warnings.append("Silence cuts happened before alignment; verify all word times are on audio/clean.wav (edits.json).")
    add("captions.srt", bool(srt.strip()), f"{len(srt.splitlines())} lines")
    if args.lang == "ar":
        add("RTL subtitle isolation marks", "\u202b" in srt and "\u202c" in srt,
            "RLE/PDF around Arabic subtitle lines")
    add("RTL composition flags", direction in index and f'dir="{direction}"' in index,
        f'dir="{direction}" + direction:{direction}')
    caption_states = index.count('class="caption-state"')
    add("one caption state per word", caption_states == len(words.get("words", [])),
        f"{caption_states} states / {len(words.get('words', []))} words", critical=False)
    add("full-line highlight", '.w active' in index or 'w active' in index,
        "active word highlighted inside the full shaped line")
    banned = re.findall(r"(?:requestAnimationFrame|Date\.now|performance\.now|Math\.random|THREE\.Clock|fetch)\s*\(|src=[\"']https?://", index)
    add("no independent clocks / network assets", not banned, ", ".join(sorted(set(banned))) or "clean")
    add("no API keys in env", not any(k in os.environ for k in ("OPENAI_API_KEY", "ELEVENLABS_API_KEY", "REPLICATE_API_TOKEN", "HF_TOKEN", "ANTHROPIC_API_KEY")), "keyless")

    # Visual sampling: one contact sheet from the actual MP4.
    sheet = qa_dir / "contact-sheet.jpg"
    if ff and out.exists():
        cmd = [ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(out),
               "-vf", "fps=1/2,scale=270:480,tile=3x2", "-frames:v", "1", "-q:v", "3", str(sheet)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        add("contact sheet", r.returncode == 0 and sheet.exists() and sheet.stat().st_size > 1000,
            f"{sheet.name} ({sheet.stat().st_size if sheet.exists() else 0} bytes)")
        if r.returncode:
            warnings.append(f"contact sheet: {r.stderr[-300:]}")

        # Black-frame detection; long black spans are a warning, not a hard fail.
        black = subprocess.run([ff, "-hide_banner", "-i", str(out), "-vf",
                                "blackdetect=d=0.50:pix_th=0.10", "-an", "-f", "null", "-"],
                               capture_output=True, text=True)
        spans = re.findall(r"black_start:([0-9.]+) black_end:([0-9.]+)", black.stderr or "")
        long_spans = [(float(a), float(b)) for a, b in spans if float(b) - float(a) >= 1.0]
        add("no long black frames", not long_spans, f"{len(long_spans)} black span(s) >= 1s", critical=False)
        if long_spans:
            warnings.append(f"Black spans: {long_spans[:4]}")

        # Integrated loudness target from the brief: -14 LUFS.
        loud = subprocess.run([ff, "-hide_banner", "-i", str(out), "-af",
                               "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                              capture_output=True, text=True)
        matches = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", loud.stderr or "", re.S)
        measured = None
        if matches:
            try:
                measured = float(json.loads(matches[-1]).get("input_i", "nan"))
            except Exception:
                measured = None
        if measured is None or measured != measured:  # nan
            warnings.append("Could not parse loudnorm input_i; loudness not verified.")
        else:
            add("loudness near -14 LUFS", -17.0 <= measured <= -11.0, f"input_i={measured:.1f} LUFS", critical=False)
    else:
        add("contact sheet", False, "ffmpeg unavailable")

    if render.get("backend") == "pillow-fallback":
        warnings.append("Pillow fallback was used: full-line captions are present but per-word highlight is simplified. HyperFrames is the quality path.")

    critical_failures = [c for c in checks if c["critical"] and not c["ok"]]
    status = "pass" if not critical_failures else "fail"
    report = {
        "status": status,
        "project": str(project),
        "output": str(out),
        "lang": args.lang,
        "direction": direction,
        "render_backend": render.get("backend", "unknown"),
        "checks": checks,
        "warnings": warnings,
        "contact_sheet": str(sheet) if sheet.exists() else None,
    }
    (qa_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"# QA — {project.name}", "", f"**Status:** {status.upper()}  ",
             f"**Language:** `{args.lang}` / `{direction}`  ",
             f"**Renderer:** `{render.get('backend', 'unknown')}`  ",
             f"**Output:** `{out}`", "", "## Checks", "",
             "| | Check | Detail |", "|---|---|---|"]
    for c in checks:
        mark = "PASS" if c["ok"] else ("WARN" if not c["critical"] else "FAIL")
        lines.append(f"| {mark} | {c['name']} | {c['detail']} |")
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in warnings] or ["- none"]
    lines += ["", "## Review gates", "",
              "- Watch the MP4 with sound off: the hook and captions must still be readable.",
              "- For Arabic, verify the highlight travels right-to-left inside a full shaped line.",
              "- Verify no invented numbers: `config/facts.json` is the only source of truth.",
              "- Publishing is a separate, explicit human approval. Never auto-publish.", ""]
    (qa_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"[qa] {status.upper()} — {sum(1 for c in checks if c['ok'])}/{len(checks)} checks, {len(warnings)} warning(s)")
    print(f"[qa] report -> {qa_dir / 'report.md'}")
    if critical_failures:
        for c in critical_failures:
            print(f"[qa] FAIL {c['name']}: {c['detail']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
