#!/usr/bin/env python3
"""Stage 2 — word-level timings -> words.json (+ captions.srt).

Backends (keyless, no tokens):
  whisperx         forced alignment with a per-language wav2vec2 model (highest quality)
  faster-whisper   native word_timestamps=True (lighter fallback)
  from-json        deterministic offline mode using a supplied words.json

Arabic: tashkeel is KEPT in `display` and STRIPPED in `align` because wav2vec2
dictionaries do not contain combining marks. Numbers / Latin tokens are marked
bdi=True and score=0 when their timing was interpolated.
"""
import argparse, json, os, re, sys, unicodedata

ARABIC_DIACRITICS = re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
LATIN_OR_DIGIT = re.compile(r'[A-Za-z0-9]')

def strip_tashkeel(s):
    return ARABIC_DIACRITICS.sub('', s).replace('\u0640', '')

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def normalize(doc, lang_cfg, audio_rel, project):
    words = []
    for i, w in enumerate(doc.get('words', [])):
        display = w.get('display') or w.get('word') or ''
        align = w.get('align') or (strip_tashkeel(display) if lang_cfg.get('strip_tashkeel_for_alignment') else display)
        score = float(w.get('score', w.get('probability', 1.0) or 0.0))
        words.append({
            'display': display, 'align': align,
            'start': round(float(w.get('start', 0)), 3), 'end': round(float(w.get('end', 0)), 3),
            'score': round(score, 3), 'line': int(w.get('line', 0)),
            'bdi': bool(LATIN_OR_DIGIT.search(display)) and lang_cfg['dir'] == 'rtl',
            **({'note': w['note']} if w.get('note') else {}),
        })
    words.sort(key=lambda x: (x['start'], x['line']))
    lines = doc.get('lines') or []
    if not lines:
        # group into lines of up to 6 words
        for start in range(0, len(words), 6):
            chunk = words[start:start+6]
            chunk and lines.append({'index': len(lines), 'text': ' '.join(w['display'] for w in chunk),
                                    'start': chunk[0]['start'], 'end': chunk[-1]['end']})
        for w in words:
            w['line'] = min(w['line'], len(lines)-1) if lines else 0
    unverified = [i for i,w in enumerate(words) if w['score'] == 0]
    out = {
        'language': lang_cfg['lang_tag'], 'direction': lang_cfg['dir'],
        'audio': audio_rel, 'duration': round(float(doc.get('duration') or (words[-1]['end'] + 1.2 if words else 10)), 3),
        'fps': 30, 'align_model': lang_cfg['align_model'], 'asr_model': lang_cfg['asr_model'],
        'source_text': f'config/copy.{lang_cfg["lang_tag"]}.json',
        'lines': lines, 'words': words, 'unverified': unverified,
        'backend': doc.get('backend', 'from-json'),
    }
    return out

def write_srt(doc, project, rtl):
    lines = []
    for idx, line in enumerate(doc['lines'], 1):
        def ts(t):
            h = int(t//3600); m = int((t%3600)//60); s = t%60
            return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')
        text = line['text']
        if rtl: text = '\u202b' + text + '\u202c'
        lines.append(f"{idx}\n{ts(line['start'])} --> {ts(line['end'])}\n{text}\n")
    open(os.path.join(project,'captions.srt'),'w',encoding='utf-8').write('\n'.join(lines))

def from_json(path, lang_cfg, audio_rel, project):
    doc = json.load(open(path, encoding='utf-8'))
    doc['backend'] = 'from-json (offline, deterministic)'
    return normalize(doc, lang_cfg, audio_rel, project)

def whisperx_backend(a, lang_cfg, audio_rel, project):
    import whisperx
    device = a.device
    compute = a.compute_type
    model = whisperx.load_model(a.model, device, compute_type=compute)
    audio = whisperx.load_audio(a.audio)
    result = model.transcribe(audio, batch_size=a.batch_size, language=lang_cfg['lang_tag'])
    align_name = a.align_model or lang_cfg['align_model']
    align_model, meta = whisperx.load_align_model(language_code=lang_cfg['lang_tag'], device=device, model_name=align_name)
    result = whisperx.align(result['segments'], align_model, meta, audio, device,
                            return_char_alignments=False, interpolate_method='nearest')
    flat = []
    for seg in result['segments']:
        for w in seg.get('words', []):
            flat.append({'word': w.get('word',''), 'start': w.get('start'), 'end': w.get('end'), 'score': w.get('score', 1.0)})
    doc = {'words': flat, 'backend': 'whisperx', 'duration': max((w['end'] or 0) for w in flat) if flat else 10}
    return normalize(doc, lang_cfg, audio_rel, project)

def faster_whisper_backend(a, lang_cfg, audio_rel, project):
    from faster_whisper import WhisperModel
    model = WhisperModel(a.model, device=a.device, compute_type=a.compute_type)
    segments, info = model.transcribe(a.audio, language=lang_cfg['lang_tag'], word_timestamps=True, vad_filter=True)
    flat = []
    for seg in segments:
        for w in seg.words or []:
            flat.append({'word': w.word, 'start': w.start, 'end': w.end, 'score': w.probability})
    doc = {'words': flat, 'backend': 'faster-whisper', 'duration': max((w['end'] or 0) for w in flat) if flat else 10}
    return normalize(doc, lang_cfg, audio_rel, project)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', default='ar', choices=['ar','en'])
    ap.add_argument('--project', required=True)
    ap.add_argument('--audio', default='audio/clean.wav')
    ap.add_argument('--backend', default='whisperx', choices=['whisperx','faster-whisper','from-json'])
    ap.add_argument('--from-json', dest='from_json', default='')
    ap.add_argument('--model', default='large-v3')
    ap.add_argument('--align-model', default='')
    ap.add_argument('--device', default=os.environ.get('ASR_DEVICE','cpu'))
    ap.add_argument('--compute-type', default=os.environ.get('ASR_COMPUTE_TYPE','int8'))
    ap.add_argument('--batch-size', type=int, default=4)
    a = ap.parse_args()

    langs = json.load(open(os.path.join(os.path.dirname(__file__),'..','config','languages.json'), encoding='utf-8'))
    lang_cfg = langs[a.lang]
    project = os.path.abspath(a.project)
    os.makedirs(project, exist_ok=True)
    audio_rel = a.audio

    if a.backend == 'from-json' or a.from_json:
        src = a.from_json or os.path.join(os.path.dirname(__file__),'..','config',f'words.{a.lang}.example.json')
        doc = from_json(src, lang_cfg, audio_rel, project)
        print(f'[align] from-json : {src}')
    elif a.backend == 'whisperx':
        print(f'[align] whisperx  : {a.model} / {a.align_model or lang_cfg["align_model"]} on {a.device}')
        doc = whisperx_backend(a, lang_cfg, audio_rel, project)
    else:
        print(f'[align] faster-whisper : {a.model} on {a.device}')
        doc = faster_whisper_backend(a, lang_cfg, audio_rel, project)

    json.dump(doc, open(os.path.join(project,'words.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    open(os.path.join(project,'words.json'),'a',encoding='utf-8').write('\n')
    write_srt(doc, project, lang_cfg['dir']=='rtl')
    print(f'[align] {len(doc["words"])} words / {len(doc["lines"])} lines -> {os.path.join(project,"words.json")}')
    if doc['unverified']:
        print(f'[align] WARNING: {len(doc["unverified"])} word(s) have interpolated timings (score=0). Verify in qa/report.md.')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'[align] ERROR ({type(e).__name__}): {e}', file=sys.stderr)
        print('[align] Fall back to: ALIGN_BACKEND=from-json npm run reel -- --from-json config/words.<lang>.example.json', file=sys.stderr)
        sys.exit(3)
