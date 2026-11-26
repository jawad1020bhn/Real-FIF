import fs from 'node:fs';
import path from 'node:path';
import { ROOT, pythonBin, run, ensure, readJson, writeJson, parseArgs } from './lib/paths.mjs';

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  console.log(`Keyless bilingual reel harness — one orchestrator, one renderer.

Usage:
  npm run reel -- --lang ar|en [--project videos/my-reel] [--input path/to/audio]
               [--demo] [--offline] [--from-json config/words.ar.example.json]
               [--align-backend whisperx|faster-whisper|from-json]
               [--render-backend auto|hyperframes|pillow] [--fps 30]
               [--out out/reel.mp4] [--headline "…"] [--subtitle "…"]

Flags:
  --demo                generate a deterministic offline WAV so no input is needed
  --offline             force from-json word timings + offline HF env (default when no models are cached)
  --skip-doctor         skip the dependency/keyless doctor
  --skip-clean          reuse <project>/audio/clean.wav
  --skip-align          reuse <project>/words.json
  --skip-compose        reuse <project>/index.html + hyperframes.json
  --skip-render         reuse the existing MP4 at --out
  --skip-qa             stop after render
  --clean-backend ffmpeg|auto-editor
  --no-captions         compose without word-timed caption states
  --no-hyperframes      force the Chrome-less Pillow renderer

All values use space-separated arguments (--lang ar), not --lang=ar.
No API keys, no paid calls, no publishing. Stages: doctor → clean → align → compose → render → qa.
`);
  process.exit(0);
}

const lang = String(args.lang || 'ar').toLowerCase();
if (!['ar', 'en'].includes(lang)) {
  console.error('ERROR: --lang must be ar or en');
  process.exit(2);
}
const project = path.resolve(ROOT, String(args.project || `videos/${lang}-reel`));
ensure(project);
ensure(path.join(project, 'input'));
const statePath = path.join(project, 'reel-state.json');
const inputRel = args.input || (args.demo ? 'input/input.wav' : 'input/input.mp3');

function resolveMaybeRootOrProject(value) {
  const abs = path.isAbsolute(value) ? value : path.resolve(ROOT, value);
  if (fs.existsSync(abs)) return abs;
  return path.resolve(project, value);
}

const input = resolveMaybeRootOrProject(inputRel);
if (args.demo) {
  ensure(path.dirname(input));
  console.log(`\n=== reel stage 0a: deterministic demo audio ===`);
  const r = run(pythonBin(), [path.join(ROOT, 'scripts/make-test-audio.py'),
    '--out', input, '--duration', String(args.duration || 10.4)]);
  if (r.status !== 0) {
    console.error('ERROR: demo audio generation failed');
    process.exit(r.status ?? 1);
  }
}
if (!args['skip-clean'] && !fs.existsSync(input)) {
  console.error(`ERROR: input not found: ${input}`);
  console.error('Provide --input /path/to/audio, or use --demo for a deterministic offline test.');
  process.exit(2);
}
if (args['skip-clean'] && !fs.existsSync(path.join(project, 'audio/clean.wav'))) {
  console.error(`ERROR: --skip-clean requires ${path.join(project, 'audio/clean.wav')}`);
  process.exit(2);
}

const modelsDir = path.join(ROOT, 'models');
const cachedModels = fs.existsSync(modelsDir)
  ? fs.readdirSync(modelsDir).filter(n => n !== 'README.md' && !n.startsWith('.')).length > 0
  : false;
let alignBackend = String(args['align-backend'] || process.env.ALIGN_BACKEND || (cachedModels ? 'whisperx' : 'from-json'));
if (args['from-json']) alignBackend = 'from-json';
if (args.offline && !args['align-backend']) alignBackend = 'from-json';
if (!['whisperx', 'faster-whisper', 'from-json'].includes(alignBackend)) {
  console.error(`ERROR: unsupported --align-backend ${alignBackend}`);
  process.exit(2);
}
let fromJson = args['from-json']
  ? resolveMaybeRootOrProject(String(args['from-json']))
  : (alignBackend === 'from-json' ? path.join(ROOT, 'config', `words.${lang}.example.json`) : '');
if (fromJson && !fs.existsSync(fromJson)) {
  console.error(`ERROR: --from-json file not found: ${fromJson}`);
  process.exit(2);
}
const offline = Boolean(args.offline || alignBackend === 'from-json');
let renderBackend = String(args['render-backend'] || process.env.RENDERER || 'auto');
if (renderBackend === 'frames') renderBackend = 'pillow';
if (args['no-hyperframes']) renderBackend = 'pillow';
if (!['auto', 'hyperframes', 'pillow'].includes(renderBackend)) {
  console.error(`ERROR: unsupported --render-backend ${renderBackend}`);
  process.exit(2);
}
const out = path.resolve(ROOT, String(args.out || `out/reel-${lang}.mp4`));
ensure(path.dirname(out));

const templateState = readJson(path.join(ROOT, 'config/reel-state.example.json'), {}) || {};
const state = {
  ...templateState,
  project: path.basename(project),
  lang,
  stage: 0,
  completed: false,
  goal: String(args.goal || 'saves'),
  facts: [],
  mode: { offline, alignBackend, renderBackend, cachedModels, keyless: true },
  paths: {
    input: path.relative(ROOT, input),
    audio: 'audio/clean.wav',
    words: 'words.json',
    composition: 'index.html',
    render: path.relative(ROOT, out),
    qa: 'qa/report.md',
    state: 'reel-state.json',
  },
  approvals: {
    install: true,          // user explicitly approved the full install attempt
    brief: false,
    storyboard: false,
    publish: false,
    paid_calls: false,
  },
  cost: { api_calls: [], credits_spent: 0 },
  qa: { status: 'pending', passes: 0 },
  stages: [],
};
writeJson(statePath, state);

function stage(name, number, cmd, argv, env = {}) {
  console.log(`\n=== reel stage ${number}: ${name} ===`);
  const r = run(cmd, argv, { env });
  const ok = r.status === 0;
  state.stage = number;
  state.stages.push({ name, number, ok, command: [path.basename(cmd), ...argv.map(String)].join(' ') });
  writeJson(statePath, state);
  if (!ok) {
    if (r.error) console.error(r.error.message);
    console.error(`ERROR: stage "${name}" failed with exit code ${r.status ?? 'unknown'}`);
    process.exit(r.status ?? 1);
  }
}

function pushArg(argv, flag, value) {
  if (value === true) {
    argv.push(flag);
    return;
  }
  if (value !== undefined && value !== null && value !== '' && value !== false) {
    argv.push(flag, String(value));
  }
}

if (!args['skip-doctor']) stage('doctor', 0, process.execPath, [path.join(ROOT, 'scripts/doctor.mjs')]);

if (!args['skip-clean']) {
  const a = [path.join(ROOT, 'scripts/clean.mjs'), '--project', project, '--input', input,
    '--backend', String(args['clean-backend'] || 'ffmpeg')];
  pushArg(a, '--threshold', args.threshold);
  pushArg(a, '--min-silence', args['min-silence']);
  pushArg(a, '--margin', args.margin);
  stage('clean', 1, process.execPath, a);
}

if (!args['skip-align']) {
  const a = [path.join(ROOT, 'scripts/align.mjs'), '--lang', lang, '--project', project,
    '--backend', alignBackend];
  pushArg(a, '--from-json', fromJson);
  pushArg(a, '--model', args.model);
  pushArg(a, '--align-model', args['align-model']);
  pushArg(a, '--device', args.device);
  pushArg(a, '--compute-type', args['compute-type']);
  pushArg(a, '--batch-size', args['batch-size']);
  stage('align', 2, process.execPath, a, {
    ALIGN_BACKEND: alignBackend,
    HF_HUB_OFFLINE: offline ? '1' : '0',
    TRANSFORMERS_OFFLINE: offline ? '1' : '0',
  });
} else if (!fs.existsSync(path.join(project, 'words.json'))) {
  console.error(`ERROR: --skip-align requires ${path.join(project, 'words.json')}`);
  process.exit(2);
}

if (!args['skip-compose']) {
  const a = [path.join(ROOT, 'scripts/compose.mjs'), '--lang', lang, '--project', project];
  pushArg(a, '--template', args.template);
  pushArg(a, '--headline', args.headline);
  pushArg(a, '--subtitle', args.subtitle);
  pushArg(a, '--no-captions', args['no-captions']);
  stage('compose', 3, process.execPath, a);
}

if (!args['skip-render']) {
  const a = [path.join(ROOT, 'scripts/render.mjs'), '--project', project, '--out', out,
    '--lang', lang, '--backend', renderBackend];
  pushArg(a, '--quality', args.quality);
  pushArg(a, '--fps', args.fps);
  stage('render', 4, process.execPath, a, {
    HYPERFRAMES_TELEMETRY: 'off',
    HYPERFRAMES_NO_UPDATE_CHECK: '1',
    DO_NOT_TRACK: '1',
  });
} else if (!fs.existsSync(out)) {
  console.error(`ERROR: --skip-render requires an existing output: ${out}`);
  process.exit(2);
}

if (!args['skip-qa']) {
  const a = [path.join(ROOT, 'scripts/qa.mjs'), '--project', project, '--out', out, '--lang', lang];
  pushArg(a, '--fps', args.fps);
  stage('qa', 5, process.execPath, a);
  const report = readJson(path.join(project, 'qa/report.json'), {}) || {};
  state.qa = {
    status: report.status || 'unknown',
    passes: (report.checks || []).filter(c => c.ok).length,
    warnings: (report.warnings || []).length,
  };
}
state.stage = 6;
state.completed = true;
writeJson(statePath, state);

const renderInfo = readJson(path.join(project, 'render.json'), {}) || {};
console.log(`\n=== reel complete ===`);
console.log(`language : ${lang} (${lang === 'ar' ? 'RTL' : 'LTR'})`);
console.log(`align    : ${alignBackend}${fromJson ? ` <- ${path.relative(ROOT, fromJson)}` : ''}`);
console.log(`renderer : ${renderInfo.backend || renderBackend}`);
console.log(`video    : ${out}`);
console.log(`qa       : ${path.join(project, 'qa/report.md')}`);
console.log(`state    : ${statePath}`);
console.log(`No API keys used. No publishing performed. Draft only.\n`);
