import fs from 'node:fs'; import path from 'node:path';
import { ROOT, pythonBin, ffmpegBin, ffprobeBin, chromeBin, run, ensure, writeJson } from './lib/paths.mjs';

const report = { timestamp: new Date().toISOString(), root: ROOT, node: process.version, checks: [], python: {}, binaries: {}, modules: {}, models: {}, packages: {} };
const add = (name, ok, detail) => { report.checks.push({name, ok, detail}); console.log(`${ok?'  OK ':'WARN'}  ${name.padEnd(30)} ${detail}`); };

console.log('\n=== keyless reel harness / doctor ===\n');
add('Node.js >=22', Number(process.versions.node.split('.')[0])>=22, process.version);
const npm = run('npm',['-v'],{quiet:true}); add('npm', npm.status===0, (npm.stdout||'').trim());

const py = pythonBin();
const pv = run(py,['-c','import sys;print(".".join(map(str,sys.version_info[:3])))'],{quiet:true});
const ver = (pv.stdout||'').trim(); report.python = {bin:py, version:ver};
add('Python 3.10–3.13', pv.status===0 && /^3\.(10|11|12|13)\./.test(ver), `${ver} (${py})`);

const mods = ['PIL','numpy','imageio_ffmpeg','soundfile','auto_editor','whisperx','faster_whisper','ctranslate2','torch','arabic_reshaper','bidi','huggingface_hub','transformers','torchaudio'];
const mr = run(py,['-c',`import importlib.util as u,json;print(json.dumps({m: bool(u.find_spec(m)) for m in ${JSON.stringify(mods)}}))`],{quiet:true});
try { report.modules = JSON.parse(mr.stdout.trim()); } catch { report.modules = {}; }
for (const m of ['PIL','numpy','imageio_ffmpeg','auto_editor','whisperx','faster_whisper','arabic_reshaper','bidi']) add(`python: ${m}`, !!report.modules[m], report.modules[m]?'installed':'missing (optional)');
add('python: torch', !!report.modules.torch, report.modules.torch?'installed (heavy ASR available)':'missing');

const ff = ffmpegBin(), fp = ffprobeBin(), ch = await chromeBin();
report.binaries = {ffmpeg:ff, ffprobe:fp, chrome:ch};
add('ffmpeg', !!ff, ff || 'not found — npm install @ffmpeg-installer/ffmpeg');
add('ffprobe', !!fp, fp || 'not found — npm install @ffprobe-installer/ffprobe');
add('headless Chrome', !!ch, ch || 'not found — will use offline Pillow frame renderer');
if (ff) { const v=run(ff,['-version'],{quiet:true}); const line=(v.stdout||v.stderr||'').split('\n')[0]; add('ffmpeg version', v.status===0, line); const e=run(ff,['-hide_banner','-encoders'],{quiet:true}); add('H.264 encoder', /libx264/.test(e.stdout||''), /libx264/.test(e.stdout||'')?'libx264':'fallback mpeg4 will be used'); }

for (const p of ['hyperframes','gsap','animejs','@mojs/core','roughjs','three','ffmpeg-skill','remotion','@remotion/gsap']) {
  const ok = fs.existsSync(path.join(ROOT,'node_modules',p)); report.packages[p]=ok; add(`npm: ${p}`, ok, ok?'installed':'missing');
}
const modelDir = ensure(path.join(ROOT,'models'));
report.models = { dir: modelDir, entries: fs.readdirSync(modelDir).filter(f=>f!=='README.md') };
add('cached ASR models', report.models.entries.length>0, report.models.entries.length?report.models.entries.join(', '):'none — use --from-json (offline) or install-models.py');
add('no API keys in env', !Object.keys(process.env).some(k=>/OPENAI|ELEVEN|REPLICATE|HF_TOKEN|ANTHROPIC_API_KEY/.test(k)), 'keyless');

report.core_ok = !!ff && !!fp && Number(process.versions.node.split('.')[0])>=22 && Object.values(report.packages).filter(Boolean).length>=5;
writeJson(path.join(ROOT,'reports/doctor.json'), report);
console.log(`\ncore_ok = ${report.core_ok}   (ffmpeg + ffprobe + node + npm packages)`);
console.log(`report  -> reports/doctor.json\n`);
process.exit(report.core_ok?0:1);
