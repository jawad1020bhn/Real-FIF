import fs from 'node:fs'; import path from 'node:path';
import { ROOT, ffmpegBin, ffprobeBin, run, ensure, writeJson, parseArgs } from './lib/paths.mjs';

// Stage 1 — silence removal. Cuts BEFORE alignment; every later timing is on clean.wav.
// Backends: ffmpeg-silencedetect (default, deterministic) or auto-editor (optional).
const args = parseArgs(process.argv.slice(2));
const proj = path.resolve(ROOT, args.project || 'videos/my-first-reel');
const input = path.resolve(ROOT, args.input || path.join(proj, 'input/input.mp3'));
const audioDir = ensure(path.join(proj, 'audio'));
const clean = path.join(audioDir, 'clean.wav');
const editsPath = path.join(audioDir, 'edits.json');
const backend = args.backend || 'ffmpeg';
const threshold = Number(args.threshold || -35);
const minSilence = Number(args['min-silence'] || 0.30);
const margin = Number(args.margin || 0.12);
const ff = ffmpegBin(), fp = ffprobeBin();
if (!ff) { console.error('ERROR: ffmpeg not found. Run `npm install` first.'); process.exit(2); }
if (!fs.existsSync(input)) { console.error(`ERROR: input not found: ${input}`); process.exit(2); }

const probe = fp ? run(fp, ['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',input], {quiet:true}) : null;
const duration = probe && probe.status === 0 ? parseFloat((probe.stdout||'0').trim()) : 0;
console.log(`[clean] input   : ${input}`);
console.log(`[clean] backend : ${backend}  (noise ${threshold}dB / min ${minSilence}s / margin ${margin}s)`);

let removed = [], kept = [], usedBackend = 'ffmpeg-silencedetect';

if (backend === 'auto-editor') {
  // auto-editor's CLI downloads a release binary on first run; that host is blocked in
  // some sandboxes. Try it, then fall back to the deterministic FFmpeg backend.
  const ae = path.join(ROOT, '.venv/bin/auto-editor');
  if (fs.existsSync(ae)) {
    const r = run(ae, [input, '--output', clean, '--no-open'], {quiet:true});
    if (r.status === 0 && fs.existsSync(clean)) {
      usedBackend = 'auto-editor';
      writeJson(editsPath, {input, output:clean, backend:usedBackend, removed:[], kept:[{start:0,end:duration}],
        source_duration:duration, note:'auto-editor EDL not parsed here — re-run align on clean.wav; all times are clean-audio times.'});
      console.log(`[clean] auto-editor wrote ${clean}`);
      process.exit(0);
    }
    console.warn('[clean] auto-editor binary download failed here; falling back to FFmpeg silencedetect.');
  } else {
    console.warn('[clean] auto-editor not installed; falling back to FFmpeg silencedetect.');
  }
}

const sd = run(ff, ['-hide_banner','-i',input,'-af',`silencedetect=noise=${threshold}dB:d=${minSilence}`,'-f','null','-'], {quiet:true});
const log = `${sd.stderr||''}\n${sd.stdout||''}`;
const starts = [...log.matchAll(/silence_start:\s*([\d.]+)/g)].map(m=>parseFloat(m[1]));
const ends   = [...log.matchAll(/silence_end:\s*([\d.]+)/g)].map(m=>parseFloat(m[1]));
const total = duration || (ends.length ? ends[ends.length-1] + 1 : 0);

let cursor = 0;
for (let i=0;i<starts.length;i++) {
  const s = starts[i] + margin, e = (ends[i] ?? starts[i]) - margin;
  if (e <= s) continue;
  if (s > cursor) kept.push([cursor, s]);
  removed.push([starts[i], ends[i] ?? starts[i]]);
  cursor = Math.max(cursor, e);
}
if (total > cursor) kept.push([cursor, total]);
if (!kept.length) kept = [[0, total]];
kept = kept.filter(([a,b]) => b - a > 0.05).slice(0, 60);
if (!kept.length) kept = [[0, total]];

const parts = kept.map(([a,b],i)=>`[0:a]atrim=start=${a.toFixed(3)}:end=${b.toFixed(3)},asetpts=PTS-STARTPTS[a${i}]`).join(';');
const labels = kept.map((_,i)=>`[a${i}]`).join('');
const filter = `${parts};${labels}concat=n=${kept.length}:v=0:a=1[out]`;
const r = run(ff, ['-y','-hide_banner','-i',input,'-filter_complex',filter,'-map','[out]','-ac','1','-ar','16000','-c:a','pcm_s16le',clean], {quiet:true});
if (r.status !== 0) { console.error((r.stderr||'').slice(-2000)); process.exit(3); }

// Single-pass loudness normalisation toward the social-video target. This is an
// audio-only filter; it does not shift word timings or touch the video stream.
const normalized = path.join(audioDir, 'clean.normalized.wav');
const nr = run(ff, ['-y','-hide_banner','-i',clean,'-af','loudnorm=I=-14:TP=-1.5:LRA=11',
  '-ac','1','-ar','16000','-c:a','pcm_s16le',normalized], {quiet:true});
const normalizedOk = nr.status === 0 && fs.existsSync(normalized) && fs.statSync(normalized).size > 1000;
if (normalizedOk) {
  fs.renameSync(normalized, clean);
  usedBackend += '+loudnorm';
} else {
  fs.rmSync(normalized, {force:true});
  console.warn('[clean] loudnorm unavailable; keeping the un-normalised clean.wav. QA will warn about loudness.');
}

const probeDuration = p => fp ? parseFloat((run(fp,['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',p],{quiet:true}).stdout||'0').trim()) : 0;
let cleanDuration = probeDuration(clean);
writeJson(editsPath, {input, output:clean, backend:usedBackend, threshold_db:threshold, min_silence_s:minSilence, margin_s:margin,
  loudnorm_target_lufs:-14, loudnorm_applied:normalizedOk,
  removed, kept: kept.map(([a,b])=>({start:a,end:b})), source_duration:total, clean_duration:cleanDuration,
  note:'All downstream word/scene times are on the CLEAN audio. If anything is cut later, remap: start - sum(removed_before_start).'});
console.log(`[clean] removed ${removed.length} silence ranges -> ${clean} (${cleanDuration.toFixed(2)}s, loudnorm=${normalizedOk ? 'on' : 'off'})`);
console.log(`[clean] edits   -> ${editsPath}`);
