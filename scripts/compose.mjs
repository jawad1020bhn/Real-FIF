import path from 'node:path';
import { ROOT, pythonBin, run, parseArgs } from './lib/paths.mjs';

const args = parseArgs(process.argv.slice(2));
const argv = [path.join(ROOT, 'scripts/compose.py')];
for (const [key, value] of Object.entries(args)) {
  if (key === '_') continue;
  argv.push(`--${key}`);
  if (value !== true) argv.push(String(value));
}
process.exit(run(pythonBin(), argv).status ?? 1);
