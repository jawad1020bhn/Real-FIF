import path from 'node:path';
import { ROOT, pythonBin, run, parseArgs } from './lib/paths.mjs';
const args = parseArgs(process.argv.slice(2));
const py = pythonBin();
const argv = [path.join(ROOT,'scripts/align.py')];
for (const [k,v] of Object.entries(args)) {
  if (k === '_') continue;
  argv.push(`--${k}`);
  if (v !== true) argv.push(String(v));
}
const r = run(py, argv);
process.exit(r.status ?? 1);
