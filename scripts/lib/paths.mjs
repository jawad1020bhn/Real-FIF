import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
export const ROOT = path.resolve(import.meta.dirname, '../..');

export function pythonBin() {
  const local = path.join(ROOT, '.venv/bin/python');
  if (process.env.PYTHON) return process.env.PYTHON;
  if (fs.existsSync(local)) return local;
  return 'python3';
}

function tryRequire(mod) {
  try { const m = require(mod); return m.path || m.default?.path || null; } catch { return null; }
}

export function ffmpegBin() {
  for (const v of ['FFMPEG_PATH','HYPERFRAMES_FFMPEG_PATH']) if (process.env[v] && fs.existsSync(process.env[v])) return process.env[v];
  const npm = tryRequire('@ffmpeg-installer/ffmpeg');
  if (npm && fs.existsSync(npm)) return npm;
  const linux = path.join(ROOT,'node_modules/@ffmpeg-installer/linux-x64/ffmpeg');
  if (fs.existsSync(linux)) return linux;
  const r = spawnSync(pythonBin(), ['-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'], {encoding:'utf8'});
  if (r.status === 0 && r.stdout.trim() && fs.existsSync(r.stdout.trim())) return r.stdout.trim();
  const w = spawnSync('which',['ffmpeg'],{encoding:'utf8'});
  if (w.status === 0 && w.stdout.trim()) return w.stdout.trim();
  return null;
}

export function ffprobeBin() {
  for (const v of ['FFPROBE_PATH','HYPERFRAMES_FFPROBE_PATH']) if (process.env[v] && fs.existsSync(process.env[v])) return process.env[v];
  const npm = tryRequire('@ffprobe-installer/ffprobe');
  if (npm && fs.existsSync(npm)) return npm;
  const linux = path.join(ROOT,'node_modules/@ffprobe-installer/linux-x64/ffprobe');
  if (fs.existsSync(linux)) return linux;
  const w = spawnSync('which',['ffprobe'],{encoding:'utf8'});
  if (w.status === 0 && w.stdout.trim()) return w.stdout.trim();
  return null;
}

export function hfBin() {
  for (const p of [path.join(ROOT,'node_modules/.bin/hyperframes'), path.join(ROOT,'node_modules/hyperframes/bin/hyperframes.mjs')]) {
    if (fs.existsSync(p)) return p;
  }
  const w = spawnSync('which',['hyperframes'],{encoding:'utf8'});
  return w.status === 0 && w.stdout.trim() ? w.stdout.trim() : null;
}

export async function chromeBin() {
  for (const v of ['HYPERFRAMES_BROWSER_PATH','CHROME_PATH']) if (process.env[v] && fs.existsSync(process.env[v])) return process.env[v];
  try {
    const mod = await import('@sparticuz/chromium');
    const chromium = mod.default || mod;
    const p = await chromium.executablePath();
    if (p && fs.existsSync(p)) {
      // @sparticuz/chromium ships NSS/NSPR libs in al2023.tar.br. Extract them locally
      // so Chromium can start on a minimal image without apt. 100% offline.
      const libDir = path.join(ROOT,'vendor/bin/lib/lib');
      if (!fs.existsSync(path.join(libDir,'libnss3.so'))) {
        const zlib = await import('node:zlib');
        const br = path.join(ROOT,'node_modules/@sparticuz/chromium/bin/al2023.tar.br');
        if (fs.existsSync(br)) {
          const tarPath = path.join(ROOT,'vendor/bin/al2023.tar');
          const extractDir = path.join(ROOT,'vendor/bin/lib');
          ensure(path.dirname(tarPath));
          ensure(extractDir);
          fs.writeFileSync(tarPath, zlib.brotliDecompressSync(fs.readFileSync(br)));
          spawnSync('tar',['-xf',tarPath,'-C',extractDir]);
        }
      }
      if (fs.existsSync(path.join(libDir,'libnss3.so'))) {
        process.env.LD_LIBRARY_PATH = `${libDir}:${process.env.LD_LIBRARY_PATH||''}`;
      }
      return p;
    }
  } catch {}
  for (const c of ['chromium','chromium-browser','google-chrome','chrome']) {
    const w = spawnSync('which',[c],{encoding:'utf8'});
    if (w.status === 0 && w.stdout.trim()) return w.stdout.trim();
  }
  return null;
}

export function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, { stdio: opts.quiet ? 'pipe' : 'inherit', encoding: opts.quiet ? 'utf8' : undefined, cwd: opts.cwd || ROOT, env: {...process.env, ...(opts.env||{})} });
  return r;
}
export function ensure(p) { fs.mkdirSync(p, {recursive:true}); return p; }
export function readJson(p, fallback=null) { try { return JSON.parse(fs.readFileSync(p,'utf8')); } catch { return fallback; } }
export function writeJson(p, v) { ensure(path.dirname(p)); fs.writeFileSync(p, JSON.stringify(v,null,2)+'\n'); }
export function parseArgs(argv) {
  const out = { _: [] };
  for (let i=0;i<argv.length;i++) {
    const a=argv[i];
    if (a.startsWith('--')) { const k=a.slice(2); const v=argv[i+1] && !argv[i+1].startsWith('--') ? argv[++i] : true; out[k]=v; }
    else out._.push(a);
  }
  return out;
}
