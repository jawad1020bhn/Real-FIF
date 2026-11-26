import path from 'node:path';
import { ROOT, ffmpegBin, ffprobeBin, chromeBin, hfBin, run, parseArgs } from './lib/paths.mjs';

const args = parseArgs(process.argv.slice(2));
const project = path.resolve(ROOT, String(args.project || 'videos/ar-reel'));
const hf = hfBin();
const ff = ffmpegBin();
const fp = ffprobeBin();
const chrome = await chromeBin();
if (!hf || !ff || !fp) {
  console.error('ERROR: hyperframes / ffmpeg / ffprobe not found. Run `npm install` and `npm run doctor`.');
  process.exit(2);
}
if (!chrome) console.warn('WARN: headless Chrome not found; HyperFrames check may fail.');

const argv = ['check', project, '--no-cache', '--no-browser-gpu'];
if (!args['no-strict']) argv.push('--strict');
if (args.samples) argv.push(`--samples=${args.samples}`);
if (args.at) argv.push(`--at=${args.at}`);
if (args['safe-zone']) argv.push(`--safe-zone=${args['safe-zone']}`);

const env = {
  HYPERFRAMES_FFMPEG_PATH: ff,
  HYPERFRAMES_FFPROBE_PATH: fp,
  HYPERFRAMES_BROWSER_PATH: chrome || '',
  CHROME_PATH: chrome || '',
  PUPPETEER_EXECUTABLE_PATH: chrome || '',
  HYPERFRAMES_TELEMETRY: 'off',
  HYPERFRAMES_NO_UPDATE_CHECK: '1',
  DO_NOT_TRACK: '1',
  LD_LIBRARY_PATH: process.env.LD_LIBRARY_PATH || '',
};
console.log(`[check] ${project} (strict=${!args['no-strict']})`);
process.exit(run(hf, argv, { env }).status ?? 1);
