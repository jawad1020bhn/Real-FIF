#!/usr/bin/env python3
"""Build the 45 s keyless harness promo reel.

Code-driven motion graphics only: no generated photographic backgrounds.
Every installed creative library gets a visible, deterministic scene.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from paths import ffmpeg_bin  # noqa: E402

PROJECT = ROOT / "videos" / "harness-promo-45s"
TEMPLATE_ASSETS = ROOT / "templates" / "hyperframes" / "assets"
REF_FONTS = ROOT / "videos" / "quran-reel-ash-sharh" / "assets" / "fonts"
DURATION = 45.0
FPS = 30

SCENES = [
    ("hook", 0.0, 5.0, "HYPERFRAMES + GSAP", "THE REEL HARNESS"),
    ("audio", 5.0, 6.0, "FFMPEG + FFMPEG-SKILL", "AUDIO FIRST"),
    ("anime", 11.0, 6.0, "ANIME.JS", "STAGGERED CARDS"),
    ("mo", 17.0, 6.0, "MO.JS", "SHAPE BURSTS"),
    ("rough", 23.0, 8.0, "ROUGH.JS + THREE.JS", "PIPELINE / WIREFRAME"),
    ("remotion", 31.0, 6.0, "REMOTION", "FRAME-LOCKED CLIP"),
    ("pillow", 37.0, 8.0, "PILLOW + QA + SKILLS", "FALLBACK / VERIFY / OUTRO"),
]

NARRATION_LINES = [
    "Meet the reel harness. Audio first: silence trimmed, loudness tamed, reviewed words timed offline. Auto-Editor and WhisperX are installed, but model fetches stay off.",
    "Composition is code. HyperFrames mounts scenes; GSAP drives paused timelines. anime.js, mo.js, Rough.js, and Three.js animate cards, bursts, sketches, and wireframes.",
    "Remotion renders a clip; FFmpeg stitches it. Strict checks, QA, Pillow, Arabic shaping, soundfile, numpy, and skills audit stay local. Keyless. Offline. Run it again.",
]

LINE_TIMES = [(0.4, 10.1), (10.3, 27.3), (27.5, 39.2)]

FONT_FACES_ROOT = '''@font-face{font-family:"ReelLatin";src:url("assets/fonts/DejaVuSans-Bold.ttf") format("truetype");font-weight:700;font-display:block;}
@font-face{font-family:"ReelArabic";src:url("assets/fonts/ScheherazadeNew-Bold.ttf") format("truetype");font-weight:700;font-display:block;}
@font-face{font-family:"ReelAmiri";src:url("assets/fonts/Amiri-Regular.ttf") format("truetype");font-weight:400;font-display:block;}'''

FONT_FACES_SUB = '''@font-face{font-family:"ReelLatin";src:url("assets/fonts/DejaVuSans-Bold.ttf") format("truetype");font-weight:700;font-display:block;}
@font-face{font-family:"ReelArabic";src:url("assets/fonts/ScheherazadeNew-Bold.ttf") format("truetype");font-weight:700;font-display:block;}
@font-face{font-family:"ReelAmiri";src:url("assets/fonts/Amiri-Regular.ttf") format("truetype");font-weight:400;font-display:block;}'''

COMMON_CSS = '''
#root{position:absolute;inset:0;overflow:hidden;background:#07070A;color:#F5F5F7;font-family:"ReelLatin",sans-serif;direction:ltr;opacity:0;}
[data-hf-inner-root="true"]{opacity:1 !important;}
.grid{position:absolute;inset:0;opacity:.25;background-image:linear-gradient(rgba(217,168,78,.10) 1px,transparent 1px),linear-gradient(90deg,rgba(217,168,78,.10) 1px,transparent 1px);background-size:72px 72px;mask-image:linear-gradient(180deg,rgba(0,0,0,.9),rgba(0,0,0,.15));}
.tag,.headline,.subhead,.node,.card,.clip{opacity:0;}
.vignette{position:absolute;inset:0;box-shadow:inset 0 0 260px rgba(0,0,0,.88);pointer-events:none;}
.kicker{position:absolute;left:120px;right:120px;top:330px;font-size:30px;line-height:1.2;letter-spacing:.20em;color:#F3D489;text-transform:uppercase;text-align:center;}
.headline{position:absolute;left:120px;right:120px;top:360px;font-size:86px;line-height:1.03;font-weight:700;color:#fff;text-align:center;text-wrap:balance;text-shadow:0 8px 44px rgba(0,0,0,.95);}
.subhead{position:absolute;left:120px;right:120px;top:610px;font-size:34px;line-height:1.35;color:#D1CBC0;text-align:center;text-shadow:0 5px 28px rgba(0,0,0,.95);}
.tag{position:absolute;left:120px;right:120px;top:260px;font-size:28px;letter-spacing:.18em;color:#D9A84E;text-align:center;text-transform:uppercase;}
.card{position:absolute;background:rgba(16,18,24,.88);border:1px solid rgba(217,168,78,.52);border-radius:26px;padding:24px 26px;font-size:30px;color:#F1E8D5;box-shadow:0 18px 60px rgba(0,0,0,.45);}
.node{position:absolute;width:220px;padding:18px;border:2px solid #D9A84E;border-radius:22px;background:rgba(9,11,16,.9);font-size:28px;text-align:center;color:#F3D489;}
.bar{position:absolute;left:120px;right:120px;top:920px;height:8px;background:rgba(255,255,255,.14);overflow:hidden;}
.bar-fill{height:100%;width:100%;background:linear-gradient(90deg,#D9A84E,#F3D489);transform:scaleX(0);transform-origin:left center;}
.motion-line{position:absolute;left:120px;right:120px;top:820px;height:2px;background:rgba(217,168,78,.35);}
'''

ROOT_TMPL = Template(r'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>$TITLE</title>
<script src="assets/gsap.min.js"></script>
<style>
$FONT_FACES_ROOT
:root{--bg:#07070A;--gold:#D9A84E;--gold2:#F3D489;--muted:#D1CBC0;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000;color:#F5F5F7;font-family:"ReelLatin",sans-serif;direction:ltr;}
#root{position:relative;width:100%;height:100%;overflow:hidden;background:var(--bg);direction:ltr;}
.comp-layer{position:absolute;inset:0;pointer-events:none;}
.beat-layer{z-index:1;opacity:0;}
.caption-layer{z-index:4;}
#brand{position:absolute;left:120px;top:190px;width:360px;font-size:28px;letter-spacing:.20em;color:var(--gold);text-transform:uppercase;z-index:5;}
#mode{position:absolute;right:120px;top:190px;width:360px;font-size:28px;letter-spacing:.16em;color:#D1CBC0;text-transform:uppercase;text-align:right;z-index:5;}
#grain{position:absolute;inset:0;opacity:.045;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");z-index:6;pointer-events:none;}
#progress-track{position:absolute;left:0;right:0;bottom:0;height:8px;background:rgba(255,255,255,.12);z-index:8;pointer-events:none;}
#progress{height:100%;width:100%;background:linear-gradient(90deg,var(--gold),var(--gold2));transform:scaleX(0);transform-origin:left center;}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="$DURATION" data-width="1080" data-height="1920" data-fps="$FPS" data-background="#07070A">
$HOSTS
  <div id="captions-host" class="comp-layer caption-layer" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="$DURATION" data-width="1080" data-height="1920" data-track-index="3" data-track-kind="captions" data-layout-allow-safe-zone></div>
  <div id="brand" data-layout-allow-overlap data-layout-allow-safe-zone>REEL STUDIO</div>
  <div id="mode" data-layout-allow-overlap data-layout-allow-safe-zone>KEYLESS · OFFLINE</div>
  <div id="grain"></div>
  <div id="progress-track"><div id="progress"></div></div>
  <audio id="narration" data-start="0" data-duration="$DURATION" data-track-index="2" data-volume="1" preload="auto" src="assets/audio.wav"></audio>
</div>
<script>
const mainTl = gsap.timeline({paused:true});
mainTl.fromTo('#progress',{scaleX:0},{scaleX:1,duration:$DURATION,ease:'none'},0);
mainTl.set('#brand',{opacity:1},0);
mainTl.set('#mode',{opacity:1},0);
mainTl.set({}, {}, $DURATION);
window.__timelines = window.__timelines || {};
window.__timelines['main'] = mainTl;
window.__duration = $DURATION;
window.__fps = $FPS;
</script>
</body>
</html>
''')


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def copy_assets() -> None:
    assets = PROJECT / "assets"
    (assets / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE_ASSETS / "gsap.min.js", assets / "gsap.min.js")
    shutil.copy2(TEMPLATE_ASSETS / "fonts" / "DejaVuSans-Bold.ttf", assets / "fonts" / "DejaVuSans-Bold.ttf")
    shutil.copy2(TEMPLATE_ASSETS / "fonts" / "LICENSE-DejaVu.txt", assets / "fonts" / "LICENSE-DejaVu.txt")
    for name in ("ScheherazadeNew-Bold.ttf", "Amiri-Regular.ttf", "OFL-ScheherazadeNew.txt", "OFL-Amiri.txt"):
        shutil.copy2(REF_FONTS / name, assets / "fonts" / name)
    copies = [
        ("node_modules/animejs/dist/bundles/anime.umd.min.js", "anime.umd.min.js"),
        ("node_modules/@mojs/core/dist/mo.umd.js", "mo.umd.js"),
        ("node_modules/roughjs/bundled/rough.js", "rough.js"),
        ("node_modules/three/build/three.module.js", "three.module.js"),
        ("node_modules/three/build/three.core.js", "three.core.js"),
    ]
    for src, dst in copies:
        shutil.copy2(ROOT / src, assets / dst)
    # Deterministic browser subset of @mojs/core 1.7.1: the upstream UMD bundle
    # contains wall-clock/rAF/template-selector code that HyperFrames rejects.
    (assets / "mo.umd.js").write_text("""window.__hfRafNoop = window.__hfRafNoop || function(){return 0;};
window.mojs = (function(){
  var NS = 'http://www.w3.org/2000/svg';
  function make(parent, tag, attrs){
    var el = document.createElementNS(NS, tag);
    for (var k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  }
  function canvas(parent, w, h){
    var c = document.createElementNS(NS, 'svg');
    c.setAttribute('width', w); c.setAttribute('height', h);
    c.style.position='absolute'; c.style.inset='0'; c.style.width='100%'; c.style.height='100%';
    parent.appendChild(c); return c;
  }
  function Shape(opts){
    opts = opts || {}; this.parent = opts.parent || document.body;
    this.canvas = canvas(this.parent, 840, 520);
    this.el = make(this.canvas, 'circle', {cx:420, cy:260, r:10, fill:'transparent', stroke:'#F3D489', 'stroke-width':3});
    this.canvas.appendChild(this.el); this.setProgress(0);
  }
  Shape.prototype.setProgress = function(p){
    var r = 24 + 120 * p, a = 1 - 0.35 * p;
    this.el.setAttribute('r', r);
    this.el.setAttribute('stroke', p > 0.5 ? '#D9A84E' : '#F3D489');
    this.el.setAttribute('opacity', a);
  };
  function Burst(opts){
    opts = opts || {}; this.parent = opts.parent || document.body;
    var count = opts.count || 8; this.dots = [];
    this.canvas = canvas(this.parent, 840, 520);
    for (var i=0;i<count;i++){
      var el = make(this.canvas, 'circle', {cx:420, cy:260, r:12, fill:'#D9A84E', opacity:0.9});
      this.canvas.appendChild(el); this.dots.push(el);
    }
    this.setProgress(0);
  }
  Burst.prototype.setProgress = function(p){
    for (var i=0;i<this.dots.length;i++){
      var ang = 2 * Math.PI * i / this.dots.length;
      var rad = 20 + 170 * p;
      var el = this.dots[i];
      el.setAttribute('cx', 420 + Math.cos(ang) * rad);
      el.setAttribute('cy', 260 + Math.sin(ang) * rad);
      el.setAttribute('r', 6 + 10 * (1 - p));
      el.setAttribute('opacity', 0.35 + 0.65 * Math.sin(Math.PI * p));
      el.setAttribute('fill', i % 2 ? '#F3D489' : '#F5F5F7');
    }
  };
  return {Shape:Shape, Burst:Burst};
})();
""", encoding="utf-8")
    # Rough.js uses Math.random for hachure jitter; a fixed value keeps the sketch deterministic.
    rp = assets / "rough.js"
    rt = rp.read_text(encoding="utf-8").replace("Math.random()", "0.5")
    rp.write_text(rt, encoding="utf-8")
    # compose.py copies clean.wav to assets/audio.wav; pad it to the exact film duration.
    audio_out = assets / "audio.wav"
    if not audio_out.exists():
        shutil.copy2(PROJECT / "audio" / "clean.wav", audio_out)
    ff = ffmpeg_bin()
    if ff:
        padded = assets / "audio.padded.wav"
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(audio_out),
                        "-af", f"apad,atrim=0:{DURATION:.3f}", "-ac", "2", "-ar", "48000",
                        "-c:a", "pcm_s16le", str(padded)], check=True)
        padded.replace(audio_out)


def words_source() -> dict:
    words, lines = [], []
    for li, (text, (start, end)) in enumerate(zip(NARRATION_LINES, LINE_TIMES)):
        tokens = re.findall(r"\S+", text)
        span = end - start
        for i, tok in enumerate(tokens):
            words.append({
                "display": tok,
                "align": tok,
                "start": round(start + span * i / len(tokens), 3),
                "end": round(start + span * (i + 1) / len(tokens), 3),
                "score": 1.0,
                "line": li,
            })
        lines.append({"index": li, "text": text, "start": start, "end": end})
    return {
        "language": "en", "direction": "ltr", "duration": DURATION, "fps": FPS,
        "audio": "audio/clean.wav", "lines": lines, "words": words,
        "backend": "from-json (offline, deterministic)",
        "source_text": "videos/harness-promo-45s/config/words.source.json",
    }


def write_words_source() -> None:
    cfg = PROJECT / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "words.source.json").write_text(
        json.dumps(words_source(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def caption_states(doc: dict, sep: str = " ") -> str:
    out = []
    for i, word in enumerate(doc["words"]):
        parts = []
        for j, w in enumerate(doc["words"]):
            if w["line"] != word["line"]:
                continue
            cls = "w active" if j == i else "w"
            parts.append(f'<span class="{cls}">{esc(w["display"])}</span>')
        out.append(
            f'<div id="cap-{i}" class="caption-state" dir="ltr" lang="en" data-line="{word["line"]}">{" ".join(parts)}</div>'
        )
    return sep.join(out)


def caption_gsap(doc: dict) -> str:
    lines = ["const capStates = gsap.utils.toArray('.caption-state');", "const tl = gsap.timeline({paused:true});", "tl.set(capStates,{opacity:0},0);"]
    for i, word in enumerate(doc["words"]):
        s = word["start"]
        lines.append(f"tl.set(capStates,{{opacity:0}},{s:.3f}); tl.set('#cap-{i}',{{opacity:1}},{s:.3f});")
    for line in doc["lines"]:
        lines.append(f"tl.set(capStates,{{opacity:0}},{line['end'] + 0.01:.3f});")
    lines += [f"tl.set(capStates,{{opacity:0}},{DURATION:.3f});", f"tl.set({{}}, {{}}, {DURATION:.3f});",
              "window.__timelines = window.__timelines || {};", "window.__timelines['captions'] = tl;"]
    return " ".join(lines)


def base_gsap(cid: str, duration: float, first: bool) -> str:
    scope = f'[data-composition-id="{cid}"]'
    lines = [
        "const tl = gsap.timeline({paused:true});",
        f"tl.fromTo('{scope}',{{opacity:0}},{{opacity:1,duration:.35,ease:'power2.out'}},0);",
        "tl.fromTo('.grid',{opacity:.25,scale:1.02},{opacity:.88,scale:1,duration:1.1,ease:'power2.out'},0);",
        "tl.fromTo('.tag',{opacity:0,y:-18},{opacity:1,y:0,duration:.55,ease:'power3.out'},0.12);",
        "tl.fromTo('.headline',{opacity:0,y:42},{opacity:1,y:0,duration:.75,ease:'power3.out'},0.22);",
        "tl.fromTo('.subhead',{opacity:0,y:24},{opacity:1,y:0,duration:.6,ease:'power3.out'},0.48);",
        f"tl.to('{scope}',{{opacity:0,duration:.30,ease:'power1.in'}},{max(0, duration - .30):.3f});",
        f"tl.set({{}}, {{}}, {duration:.3f});",
        "window.__timelines = window.__timelines || {};",
        f"window.__timelines['{cid}'] = tl;",
    ]
    return "\n".join(lines)


def allow_safe_zone(markup: str) -> str:
    return re.sub(
        r"(<[^>]*\bdata-layout-allow-overlap\b(?![^>]*\bdata-layout-allow-safe-zone\b)[^>]*)(>)",
        r"\1 data-layout-allow-safe-zone\2",
        markup,
    )


def scene_html(cid: str, start: float, duration: float, kicker: str, headline: str, extra_html: str, extra_js: str, css_extra: str = "") -> str:
    subhead = "PAUSED TIMELINES · LOCAL ASSETS · NO CLOUD"
    return allow_safe_zone(f'''<template id="{cid}-template">
<div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920" data-duration="{duration:.3f}">
  <div class="grid" data-layout-allow-overflow></div><div class="vignette" data-layout-allow-overflow></div>
  <div class="tag" data-layout-allow-overlap>{esc(kicker)}</div>
  <h1 class="headline" data-layout-allow-overlap>{esc(headline)}</h1>
  <p class="subhead" data-layout-allow-overlap>{esc(subhead)}</p>
{extra_html}
  <style>
{FONT_FACES_SUB}
{COMMON_CSS}
{css_extra}
  </style>
  <script>
  (function(){{
{base_gsap(cid, duration, start == 0.0)}
{extra_js}
  }})();
  </script>
</div>
</template>
''')


def hook_scene(cid: str, start: float, duration: float, kicker: str, headline: str) -> str:
    extra = ''.join([
        '  <div class="node" data-layout-allow-overlap id="n1" style="left:120px;top:780px">AUDIO</div>',
        '  <div class="node" data-layout-allow-overlap id="n2" style="left:430px;top:780px">WORDS</div>',
        '  <div class="node" data-layout-allow-overlap id="n3" style="left:740px;top:780px">RENDER</div>',
        '  <div class="motion-line" data-layout-ignore></div>',
        '  <div class="bar" data-layout-ignore><div class="bar-fill" data-layout-ignore id="hook-bar"></div></div>',
    ])
    js = "\n".join([
        "tl.fromTo('#n1',{opacity:0,y:30},{opacity:1,y:0,duration:.5,ease:'power3.out'},.7);",
        "tl.fromTo('#n2',{opacity:0,y:30},{opacity:1,y:0,duration:.5,ease:'power3.out'},.9);",
        "tl.fromTo('#n3',{opacity:0,y:30},{opacity:1,y:0,duration:.5,ease:'power3.out'},1.1);",
        "tl.fromTo('#hook-bar',{scaleX:0},{scaleX:1,duration:3.6,ease:'none'},.8);",
        "tl.to('#n1',{y:-12,duration:.45,ease:'power1.inOut'},2.0).to('#n1',{y:0,duration:.45,ease:'power1.inOut'},2.45);",
        "tl.to('#n2',{y:-18,duration:.5,ease:'power1.inOut'},2.4).to('#n2',{y:0,duration:.5,ease:'power1.inOut'},2.9);",
        "tl.to('#n3',{y:-14,duration:.5,ease:'power1.inOut'},2.8).to('#n3',{y:0,duration:.5,ease:'power1.inOut'},3.3);",
    ])
    return scene_html(cid, start, duration, kicker, headline, extra, js)


def audio_scene(cid: str, start: float, duration: float, kicker: str, headline: str) -> str:
    bars = []
    for i in range(18):
        h = 60 + (i * 47) % 210
        bars.append(f'  <div class="wave" data-layout-ignore id="w{i}" style="left:{120 + i * 48}px;bottom:1000px;height:{h}px"></div>')
    extra = "\n".join(bars + [
        '  <div class="card" data-layout-allow-overlap id="ae" style="left:120px;top:1460px;width:300px" data-layout-allow-safe-zone>AUTO-EDITOR · gated</div>',
        '  <div class="card" data-layout-allow-overlap id="wx" style="left:460px;top:1460px;width:350px" data-layout-allow-safe-zone>WHISPERX · no weights</div>',
        '  <div class="card" data-layout-allow-overlap id="fs" style="left:120px;top:1600px;width:690px" data-layout-allow-safe-zone>FFMPEG-SKILL · doctor + contract</div>',
    ])
    css = ".wave{position:absolute;width:24px;background:linear-gradient(180deg,#F3D489,#D9A84E);border-radius:14px;transform-origin:bottom center;opacity:.85;}"
    js_lines = ["tl.set('.wave',{scaleY:.25},0);"]
    for i in range(18):
        js_lines.append(f"tl.to('#w{i}',{{scaleY:{0.45 + (i % 5) * 0.13:.2f},duration:.45,ease:'power1.inOut'}},{0.7 + i * 0.09:.2f}).to('#w{i}',{{scaleY:.28,duration:.45,ease:'power1.inOut'}},{1.15 + i * 0.09:.2f});")
    js_lines += [
        "tl.fromTo('#ae',{opacity:0,x:-30},{opacity:1,x:0,duration:.5,ease:'power3.out'},1.2);",
        "tl.fromTo('#wx',{opacity:0,x:30},{opacity:1,x:0,duration:.5,ease:'power3.out'},1.5);",
        "tl.fromTo('#fs',{opacity:0,y:24},{opacity:1,y:0,duration:.55,ease:'power3.out'},1.9);",
    ]
    return scene_html(cid, start, duration, kicker, headline, extra, "\n".join(js_lines), css)


def anime_scene(cid: str, start: float, duration: float, kicker: str, headline: str) -> str:
    extra = "\n".join([
        '<script src="assets/anime.umd.min.js"></script>',
        '  <div class="card acard" data-layout-allow-overlap id="a1" style="left:120px;top:780px;width:260px">GSAP</div>',
        '  <div class="card acard" data-layout-allow-overlap id="a2" style="left:410px;top:780px;width:260px">ANIME.JS</div>',
        '  <div class="card acard" data-layout-allow-overlap id="a3" style="left:700px;top:780px;width:260px">STAGGER</div>',
        '  <div class="card acard" data-layout-allow-overlap id="a4" style="left:120px;top:910px;width:840px">seek() driven by a paused GSAP timeline</div>',
    ])
    css = ".acard{opacity:0;}"
    js = "\n".join([
        "const animeTl = anime.createTimeline({autoplay:false});",
        "anime.set('.acard',{opacity:0,translateY:40,scale:.94});",
        "animeTl.add('.acard',{opacity:1,translateY:0,scale:1,duration:650,delay:anime.stagger(110),ease:'outExpo'},0);",
        "animeTl.init();",
        "const driver={p:0};",
        f"tl.to(driver,{{p:1,duration:{duration:.3f},ease:'none',onUpdate:()=>animeTl.seek(driver.p * 1000)}},0);",
    ])
    return scene_html(cid, start, duration, kicker, headline, extra, js, css)


def mo_scene(cid: str, start: float, duration: float, kicker: str, headline: str) -> str:
    extra = "\n".join([
        '<script src="assets/mo.umd.js"></script>',
        '  <div id="mo-stage" data-layout-ignore style="position:absolute;left:0;right:0;top:1450px;bottom:120px"></div>',
        '  <div class="card" data-layout-allow-overlap id="mo-label" style="left:120px;top:800px;width:840px;text-align:center">mo.js shapes · setProgress()</div>',
    ])
    css = "#mo-stage{pointer-events:none;}"
    js = "\n".join([
        "const burst = new mojs.Burst({parent: document.getElementById('mo-stage'), radius:{0:180}, count:8, children:{shape:'circle', radius:14, fill:['#D9A84E','#F3D489','#F5F5F7'], strokeWidth:2, duration:1200, easing:'quad.out'}});",
        "const ring = new mojs.Shape({parent: document.getElementById('mo-stage'), shape:'circle', radius:90, stroke:'#F3D489', strokeWidth:3, fill:'transparent', duration:1200});",
        "const moDriver={p:0};",
        f"tl.to(moDriver,{{p:1,duration:{duration:.3f},ease:'none',onUpdate:()=>{{burst.setProgress(moDriver.p);ring.setProgress(moDriver.p);}}}},0);",
        "tl.fromTo('#mo-label',{opacity:0,y:20},{opacity:1,y:0,duration:.55,ease:'power3.out'},.8);",
    ])
    return scene_html(cid, start, duration, kicker, headline, extra, js, css)


def rough_scene(cid: str, start: float, duration: float, kicker: str, headline: str) -> str:
    extra = "\n".join([
        '<script src="assets/rough.js"></script>',
        '  <canvas id="sketch" data-layout-ignore width="840" height="260" style="position:absolute;left:120px;top:720px"></canvas>',
        '  <canvas id="three-canvas" data-layout-ignore width="840" height="420" style="position:absolute;left:120px;top:1450px"></canvas>',
        '  <div class="card" data-layout-allow-overlap id="rt" style="left:120px;top:800px;width:840px;text-align:center;display:none">Rough.js pipeline + Three.js wireframe</div>',
    ])
    css = "#sketch,#three-canvas{background:rgba(9,11,16,.55);border:1px solid rgba(217,168,78,.35);border-radius:26px;}"
    js = "\n".join([
        "const rc = rough.canvas(document.getElementById('sketch'),{seed:7});",
        "rc.rectangle(40,30,210,85,{stroke:'#D9A84E',strokeWidth:3,roughness:1.6});",
        "rc.rectangle(310,30,210,85,{stroke:'#F3D489',strokeWidth:3,roughness:1.6});",
        "rc.rectangle(580,30,210,85,{stroke:'#F5F5F7',strokeWidth:3,roughness:1.6});",
        "rc.line(250,72,310,72,{stroke:'#F3D489',strokeWidth:4,roughness:2});",
        "rc.line(520,72,580,72,{stroke:'#F3D489',strokeWidth:4,roughness:2});",
        "rc.circle(420,190,48,{stroke:'#D9A84E',strokeWidth:3,roughness:2});",
        "tl.fromTo('#sketch',{opacity:0,y:24},{opacity:1,y:0,duration:.6,ease:'power3.out'},.8);",
        "tl.fromTo('#rt',{opacity:0,y:-16},{opacity:1,y:0,duration:.5,ease:'power3.out'},.6);",
    ])
    # Three.js module script; registered after import.
    js += "\n"
    return scene_html(cid, start, duration, kicker, headline, extra, js, css).replace(
        "</script>\n</div>\n</template>",
        "</script>\n<script type=\"module\">\n" + """
import * as THREE from './assets/three.module.js';
const canvas = document.getElementById('three-canvas');
const renderer = new THREE.WebGLRenderer({canvas, alpha:true, antialias:true});
renderer.setSize(840,420,false);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45,840/420,0.1,100);
camera.position.z=5;
const mesh = new THREE.Mesh(new THREE.IcosahedronGeometry(1.25,1), new THREE.MeshBasicMaterial({color:0xD9A84E,wireframe:true}));
scene.add(mesh);
const edges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.TorusGeometry(1.7,.04,8,80)), new THREE.LineBasicMaterial({color:0xF3D489}));
scene.add(edges);
const state={a:0};
const tl3 = gsap.timeline({paused:true});
tl3.to(state,{a:Math.PI*2,duration:DURATION,ease:'none',onUpdate:()=>{mesh.rotation.set(state.a*.6,state.a,state.a*.2);edges.rotation.set(-state.a*.3,state.a*.7,0);renderer.render(scene,camera);}},0);
renderer.render(scene,camera);
const hostTl=window.__timelines['ROUGH_TIMELINE_KEY']; if(hostTl) hostTl.add(tl3,0);
""" .replace("DURATION", f"{duration:.3f}").replace("ROUGH_TIMELINE_KEY", cid) + "\n</script>\n</div>\n</template>"
    )


def remotion_scene(cid: str, start: float, duration: float, kicker: str, headline: str) -> str:
    extra = "\n".join([
        '  <video id="remotion-clip" data-layout-allow-overlap class="clip" src="assets/remotion-clip.mp4" muted playsinline preload="auto" data-start="0" data-duration="4.000" data-track-index="1" data-track-kind="video" data-has-audio="false" data-layout-allow-occlusion style="position:absolute;left:390px;top:1450px;width:300px;height:420px;object-fit:cover;border:2px solid rgba(217,168,78,.55);border-radius:30px" data-layout-allow-safe-zone></video>',
        '  <div class="card" data-layout-allow-overlap id="rlabel" style="left:120px;top:800px;width:840px;text-align:center">@remotion/three · @remotion/gsap · useCurrentFrame</div>',
    ])
    js = "\n".join([
        "tl.fromTo('#remotion-clip',{opacity:0,scale:.94},{opacity:1,scale:1,duration:.6,ease:'power3.out'},.4);",
        "tl.fromTo('#rlabel',{opacity:0,y:20},{opacity:1,y:0,duration:.55,ease:'power3.out'},1.0);",
        "tl.to('#remotion-clip',{scale:1.04,duration:3.2,ease:'none'},1.0);",
    ])
    return scene_html(cid, start, duration, kicker, headline, extra, js)


def pillow_scene(cid: str, start: float, duration: float, kicker: str, headline: str) -> str:
    extra = "\n".join([
        '  <img id="pillow-card" data-layout-allow-overlap class="clip" src="assets/pillow-fallback-card.jpg" alt="" data-start="0" data-duration="8.000" data-track-index="1" data-layout-allow-overflow style="position:absolute;left:120px;top:1420px;width:300px;height:480px;object-fit:cover;border:2px solid rgba(217,168,78,.55);border-radius:30px" data-layout-allow-safe-zone />',
        '  <div class="card" data-layout-allow-overlap id="qa1" style="left:500px;top:1450px;width:460px" data-layout-allow-safe-zone>STRICT CHECK</div>',
        '  <div class="card" data-layout-allow-overlap id="qa2" style="left:500px;top:1580px;width:460px" data-layout-allow-safe-zone>FFMPEG QC</div>',
        '  <div class="card" data-layout-allow-overlap id="qa3" style="left:500px;top:1710px;width:460px" data-layout-allow-safe-zone>SKILLS AUDIT</div>',
        '  <div class="headline" id="cta" data-layout-allow-overlap style="left:500px;top:1840px;width:460px;font-size:54px;color:#F3D489" data-layout-allow-safe-zone>RUN IT AGAIN</div>',
    ])
    js = "\n".join([
        "tl.fromTo('#pillow-card',{opacity:0,y:30},{opacity:1,y:0,duration:.65,ease:'power3.out'},.4);",
        "tl.fromTo('#qa1',{opacity:0,y:20},{opacity:1,y:0,duration:.5,ease:'power3.out'},1.0);",
        "tl.fromTo('#qa2',{opacity:0,y:20},{opacity:1,y:0,duration:.5,ease:'power3.out'},1.3);",
        "tl.fromTo('#qa3',{opacity:0,y:20},{opacity:1,y:0,duration:.5,ease:'power3.out'},1.6);",
        "tl.fromTo('#cta',{opacity:0,scale:.9},{opacity:1,scale:1,duration:.7,ease:'back.out(1.4)'},3.0);",
        "tl.to('#pillow-card',{scale:1.03,duration:4.5,ease:'none'},1.0);",
    ])
    return scene_html(cid, start, duration, kicker, headline, extra, js)


SCENE_BUILDERS = {
    "hook": hook_scene,
    "audio": audio_scene,
    "anime": anime_scene,
    "mo": mo_scene,
    "rough": rough_scene,
    "remotion": remotion_scene,
    "pillow": pillow_scene,
}

CAPTIONS_TMPL = Template(r'''<template id="captions-template">
<div id="root" data-composition-id="captions" data-track-kind="captions" data-width="1080" data-height="1920" data-duration="$DURATION">
$CAPTION_STATES
  <style>
$FONT_FACES_SUB
#root{position:absolute;inset:0;pointer-events:none;direction:ltr;}
.caption-state{position:absolute;left:100px;right:100px;bottom:520px;height:360px;font-family:"ReelLatin",sans-serif;font-size:44px;font-weight:700;line-height:1.14;text-align:center;white-space:normal;text-wrap:balance;color:#F7F4EC;opacity:0;text-shadow:0 6px 28px rgba(0,0,0,.98);}
.caption-state .w{color:#F7F4EC;}
.caption-state .w.active{color:#F3D489;text-shadow:0 0 28px rgba(217,168,78,.6),0 6px 28px rgba(0,0,0,.98);}
  </style>
  <script>
  (function(){
$CAPTION_GSAP
  })();
  </script>
</div>
</template>
''')


def host(scene: tuple) -> str:
    kind, start, duration, kicker, headline = scene
    cid = f"s-{kind}"
    return (
        f'  <div id="{cid}-host" class="comp-layer beat-layer" data-composition-id="{cid}" '
        f'data-composition-src="compositions/{cid}.html" data-start="{start:.3f}" '
        f'data-duration="{duration:.3f}" data-width="1080" data-height="1920" data-track-index="1"></div>'
    )


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if "--words-source-only" in sys.argv:
        write_words_source()
        print(f"[build] words source -> {PROJECT / 'config' / 'words.source.json'}")
        return
    copy_assets()
    write_words_source()
    comp_dir = PROJECT / "compositions"
    comp_dir.mkdir(parents=True, exist_ok=True)
    for stale in comp_dir.glob("*.html"):
        stale.unlink()
    for scene in SCENES:
        kind, start, duration, kicker, headline = scene
        cid = f"s-{kind}"
        (comp_dir / f"{cid}.html").write_text(
            SCENE_BUILDERS[kind](cid, start, duration, kicker, headline), encoding="utf-8"
        )

    # words.json is produced by scripts/align.py from the deterministic source.
    doc = json.loads((PROJECT / "words.json").read_text(encoding="utf-8"))
    (comp_dir / "captions.html").write_text(
        CAPTIONS_TMPL.substitute({
            "DURATION": f"{DURATION:.3f}",
            "CAPTION_STATES": caption_states(doc),
            "FONT_FACES_SUB": FONT_FACES_SUB,
            "CAPTION_GSAP": caption_gsap(doc),
        }), encoding="utf-8"
    )

    index = ROOT_TMPL.substitute({
        "TITLE": "Keyless Reel Harness — 45s promo",
        "DURATION": f"{DURATION:.3f}",
        "FPS": str(FPS),
        "FONT_FACES_ROOT": FONT_FACES_ROOT,
        "HOSTS": "\n".join(host(s) for s in SCENES),
    })
    (PROJECT / "index.html").write_text(index, encoding="utf-8")

    hp = {
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True},
        "name": PROJECT.name,
        "width": 1080, "height": 1920, "fps": FPS, "duration": DURATION,
        "audio": "assets/audio.wav", "language": "en", "direction": "ltr",
        "renderer": "hyperframes", "entry": "index.html", "offline": True,
        "facts_source": "config/facts.json", "facts": {"facts": []},
        "caption_policy": "Reviewed narration only; no ASR rewrite; no invented numbers on screen.",
        "drafts_only": True, "no_invented_numbers": True,
    }
    write_json(PROJECT / "hyperframes.json", hp)
    (PROJECT / "README.md").write_text(f'''# Keyless Reel Harness — promo reel

A {DURATION:.0f} s code-driven showcase of the installed harness. No generated photographic backgrounds: motion, cards, diagrams, waveform, 3D wireframe, Remotion clip, Pillow fallback card and QA cards are all deterministic.

## Rebuild

```bash
npm run harness:build
npm run harness:check
npm run harness:render
npm run harness:qa
```

Or `npm run harness:all`.

The builder uses `scripts/reel.mjs` for doctor/clean/align, `scripts/compose.py` for the baseline assets, then replaces the composition with modular HyperFrames sub-compositions. Audio is a local generated voiceover plus a synthetic numpy/soundfile bed, mixed and loudness-normalised with FFmpeg. No API keys, paid calls, publishing or model-weight fetches.
''', encoding="utf-8")
    print(f"[build] {len(SCENES)} scenes / {len(doc['words'])} reviewed words / {len(doc['lines'])} caption lines")
    print(f"[build] index -> {PROJECT / 'index.html'}")
    print(f"[build] compositions -> {comp_dir}")


if __name__ == "__main__":
    main()
