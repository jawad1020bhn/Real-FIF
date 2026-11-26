#!/usr/bin/env python3
"""Stage 3 — deterministic HyperFrames HTML from words.json + copy/brand/facts.

The generated project uses ONE paused GSAP timeline seeked to film time. Arabic
captions remain full shaped lines; the active word is highlighted inside that
line, with <bdi> around Latin/number tokens. No network assets or free clocks.
"""
import argparse
import html
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def esc(value):
    return html.escape(str(value), quote=True)


def line_markup(doc, active_index, lang):
    """Build one full shaped line; never render isolated Arabic words."""
    words = [w for w in doc["words"] if w.get("line") == doc["words"][active_index]["line"]]
    line_id = doc["words"][active_index]["line"]
    parts = []
    for w in words:
        cls = "w active" if w is doc["words"][active_index] else "w"
        tag = "bdi" if w.get("bdi") else "span"
        parts.append(f'<{tag} class="{cls}">{esc(w["display"])}</{tag}>')
    return " ".join(parts), line_id


def caption_states(doc, lang, direction):
    states = []
    for i, w in enumerate(doc["words"]):
        markup, line_id = line_markup(doc, i, lang)
        # No data-start/data-end here: HyperFrames timed clips would own visibility and
        # conflict with the single paused GSAP timeline. The timeline sets opacity by time.
        states.append(
            f'    <div id="cap-{i}" class="caption-state" dir="{direction}" lang="{lang}" '
            f'data-line="{line_id}">{markup}</div>'
        )
    return "\n".join(states) if states else "    <!-- captions disabled -->"


def caption_gsap(doc, enabled=True):
    if not enabled or not doc["words"]:
        return "/* captions disabled */"
    lines = ["const capStates = gsap.utils.toArray('.caption-state');",
             "tl.set(capStates,{opacity:0},0);"]
    for i, w in enumerate(doc["words"]):
        s = f'{w["start"]:.3f}'
        lines.append(f"tl.set(capStates,{{opacity:0}},{s});")
        lines.append(f"tl.set('#cap-{i}',{{opacity:1}},{s});")
    last = doc["words"][-1]["end"]
    lines.append(f"tl.set(capStates,{{opacity:0}},{last + 0.01:.3f});")
    return "\n".join(lines)


def scene_blocks(doc, copy, lang, direction, duration):
    html_parts, gsap_lines = [], []
    gsap_lines.append("tl.set('.scene',{opacity:0,y:26},0);")
    for i, line in enumerate(doc["lines"]):
        src = copy.get("scenes", [])[i] if i < len(copy.get("scenes", [])) else {}
        title = src.get("title", f"Scene {i + 1}")
        body = src.get("body", line.get("text", ""))
        start = float(line.get("start", 0))
        end = float(line.get("end", start + 2.0))
        html_parts.append(
            f'  <div id="scene-{i}" class="scene" dir="{direction}" lang="{lang}">'
            f'<h2>{esc(title)}</h2><p>{esc(body)}</p></div>'
        )
        # Give the scene a readable hold, but clear it before the closing card appears.
        # Short scene bodies in copy.<lang>.json keep the craft hold requirement satisfied.
        out_at = min(max(start + 0.5, end - 0.35), max(start + 0.5, duration - 2.65))
        gsap_lines.append(
            f"tl.to('#scene-{i}',{{opacity:1,y:0,duration:0.45,ease:'power2.out'}},{start:.3f});"
        )
        gsap_lines.append(
            f"tl.to('#scene-{i}',{{opacity:0,y:-24,duration:0.35,ease:'power2.in'}},{out_at:.3f});"
        )
    return "\n".join(html_parts), "\n".join(gsap_lines)


def outro_gsap(duration):
    clear_at = max(0.0, duration - 2.70)
    start = max(0.0, duration - 2.25)
    cta_start = max(0.0, duration - 2.10)
    return "\n".join([
        "tl.set('#outro',{opacity:0,y:26},0);",
        "tl.set('#cta',{opacity:0,y:18},0);",
        f"tl.to('#hook',{{opacity:0,y:-24,duration:0.35,ease:'power2.in'}},{clear_at:.3f});",
        f"tl.to('#subtitle',{{opacity:0,y:-18,duration:0.35,ease:'power2.in'}},{clear_at:.3f});",
        f"tl.to('#outro',{{opacity:1,y:0,duration:0.50,ease:'power2.out'}},{start:.3f});",
        f"tl.to('#cta',{{opacity:1,y:0,duration:0.45,ease:'power2.out'}},{cta_start:.3f});",
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["ar", "en"], default="ar")
    ap.add_argument("--project", required=True)
    ap.add_argument("--template", default="hyperframes")
    ap.add_argument("--headline", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--no-captions", action="store_true")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    words_path = project / "words.json"
    if not words_path.exists():
        raise SystemExit(f"ERROR: {words_path} missing. Run `npm run align` first.")
    doc = load(words_path)
    langs = load(ROOT / "config" / "languages.json")
    lang = langs[args.lang]
    brand = load(ROOT / "config" / "brand.json")
    copy = load(ROOT / "config" / f"copy.{args.lang}.json")
    facts = load(ROOT / "config" / "facts.json")

    template = (ROOT / "templates" / args.template) if not Path(args.template).is_absolute() else Path(args.template)
    template = template.resolve()
    if not template.is_dir():
        raise SystemExit(f"ERROR: template not found: {template}")

    project.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template / "assets", project / "assets", dirs_exist_ok=True)
    for name in ("caption.component.html",):
        shutil.copy2(template / name, project / name)

    # The renderer's audio tag is local; HyperFrames must not fetch anything.
    audio_rel = doc.get("audio", "audio/clean.wav")
    audio_src = project / audio_rel
    if not audio_src.exists():
        raise SystemExit(f"ERROR: clean audio missing: {audio_src}. Run `npm run clean` first.")
    shutil.copy2(audio_src, project / "assets" / "audio.wav")

    fps = int(doc.get("fps", brand.get("format", {}).get("fps", 30)))
    duration = max(float(doc.get("duration", 10.4)),
                   (doc["words"][-1]["end"] + 1.2) if doc.get("words") else 10.4)
    direction = lang["dir"]
    palette = brand.get("palette", {})
    safe = brand.get("safe_zones", {})
    typ = brand.get("type", {})
    hook = args.headline or copy.get("hook", brand.get("name", "Reel"))
    subtitle = args.subtitle or copy.get("subtitle", "")
    # Only font families declared with a local @font-face in the template. HyperFrames'
    # linter rejects unmapped families such as "Amiri" or "DejaVu Sans" without a face.
    font_stack = ('"ReelArabic", "ReelArabicRegular", serif' if args.lang == "ar"
                  else '"ReelLatin", sans-serif')
    font_px = int(lang.get("caption_px", typ.get("caption_min_px", 40)))
    # Arabic Scheherazade needs a larger optical size; long English hooks wrap at 92px.
    headline_px = 92 if args.lang == "ar" else max(int(typ.get("headline_min_px", 72)), 72)
    # Platform-safe band from HyperFrames' vertical guide: y 288-1248, x 120-888;
    # below y 840 TikTok narrows the right edge to 780.
    side = int(safe.get("sides", 200))
    top = int(safe.get("top", 300))
    # Scheherazade New's taller Arabic glyphs need a slightly higher caption band.
    bottom = int(safe.get("bottom_ar", 700) if args.lang == "ar" else safe.get("bottom", 680))
    band = safe.get("platform_band", {})
    caption_left = int(band.get("x0", 120))
    caption_right = 1080 - int(band.get("narrow_right", 780))
    progress_origin = "right center" if direction == "rtl" else "left center"
    brand_html = (f'  <div id="brand-rtl">{esc(brand["name"])}</div>' if direction == "rtl"
                  else f'  <div id="brand">{esc(brand["name"])}</div>')

    scenes_html, scenes_gsap = scene_blocks(doc, copy, args.lang, direction, duration)
    caption_enabled = not args.no_captions
    states = caption_states(doc, args.lang, direction) if caption_enabled else "    <!-- captions disabled -->"
    gsap_lines = "\n".join([
        scenes_gsap,
        caption_gsap(doc, caption_enabled),
        outro_gsap(duration),
    ])

    tokens = {
        "LANG": args.lang,
        "DIR": direction,
        "TITLE": esc(hook),
        "BG": palette.get("bg", "#07070A"),
        "INK": palette.get("ink", "#F5F5F7"),
        "ACCENT": palette.get("accent", "#D9A84E"),
        "ACCENT_SOFT": palette.get("accent_soft", "rgba(217,168,78,.16)"),
        "MUTED": palette.get("muted", "#8F887A"),
        "FONT_STACK": font_stack,
        "SIDE": str(side),
        "TOP": str(top),
        "BOTTOM": str(bottom),
        "CAPTION_LEFT": str(caption_left),
        "CAPTION_RIGHT": str(caption_right),
        "HEADLINE_PX": str(headline_px),
        "CAPTION_PX": str(font_px),
        "PROGRESS_ORIGIN": progress_origin,
        "DURATION": f"{duration:.3f}",
        "FPS": str(fps),
        "BRAND_HTML": brand_html,
        "HOOK": esc(hook),
        "SUBTITLE": esc(subtitle),
        "OUTRO": esc(copy.get("outro", "")),
        "CTA": esc(copy.get("cta", "")),
        "SCENES_HTML": scenes_html,
        "CAPTION_STATES": states,
        "GSAP_LINES": gsap_lines,
    }
    index = (template / "index.html").read_text(encoding="utf-8")
    for key, value in tokens.items():
        index = index.replace(f"@@{key}@@", value)
    leftovers = sorted(set(re.findall(r"@@[A-Z_]+@@", index)))
    if leftovers:
        raise SystemExit(f"ERROR: unresolved template tokens: {', '.join(leftovers)}")
    (project / "index.html").write_text(index, encoding="utf-8")

    hp_path = project / "hyperframes.json"
    hp = load(template / "hyperframes.json") if (template / "hyperframes.json").exists() else {}
    hp.update({
        "name": project.name,
        "width": 1080,
        "height": 1920,
        "fps": fps,
        "duration": duration,
        "audio": "assets/audio.wav",
        "language": args.lang,
        "direction": direction,
        "renderer": "hyperframes",
        "entry": "index.html",
        "offline": True,
        "facts_source": "config/facts.json",
        "facts": facts,
        "caption_policy": "full shaped line; active word highlighted inside it; <bdi> for Latin/numbers",
    })
    hp_path.write_text(json.dumps(hp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[compose] {len(doc['lines'])} scenes / {len(doc['words'])} words / {duration:.2f}s -> {project}/index.html")
    print(f"[compose] direction={direction} font={lang['font']} timeline=paused+seeked; captions={'off' if args.no_captions else 'on'}")
    print(f"[compose] audio -> {project}/assets/audio.wav (muxed once by the renderer)")


if __name__ == "__main__":
    main()
