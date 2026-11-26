import fs from 'node:fs';
import path from 'node:path';
import { ROOT, ensure, readJson, parseArgs } from './lib/paths.mjs';

const args = parseArgs(process.argv.slice(2));
const vendorDir = path.join(ROOT, 'vendor/skills');
const claudeDir = path.join(ROOT, '.claude/skills');
ensure(vendorDir); ensure(claudeDir);

const RISK_PATTERNS = [
  ['shell-exec', /\b(?:execSync|spawnSync|child_process|subprocess|shell=True)\b/gi],
  ['eval', /\b(?:eval|Function)\s*\(/g],
  ['curl-pipe', /curl[^\n]{0,120}\|\s*(?:ba)?sh/gi],
  ['destructive', /rm\s+-rf|sudo\s+/g],
  ['remote-fetch', /\bfetch\s*\(|https?:\/\//gi],
  ['secret-env', /(?:TOKEN|API_KEY|SECRET|PASSWORD)/g],
];

function risk(text) {
  return RISK_PATTERNS.map(([name, re]) => [name, (text.match(re) || []).length]).filter(([, n]) => n > 0);
}

function upstream() {
  return fs.readdirSync(vendorDir, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => {
      const dir = path.join(vendorDir, d.name);
      const meta = readJson(path.join(dir, 'SOURCE.json'), {}) || {};
      const skill = path.join(dir, 'SKILL.md');
      const text = fs.existsSync(skill) ? fs.readFileSync(skill, 'utf8') : '';
      return {
        slug: d.name, ...meta,
        enabled: fs.existsSync(path.join(claudeDir, d.name, 'SKILL.md')),
        risk: risk(text),
      };
    })
    .sort((a, b) => a.slug.localeCompare(b.slug));
}

function localWrappers() {
  return fs.readdirSync(claudeDir, { withFileTypes: true })
    .filter(d => d.isDirectory() && fs.existsSync(path.join(claudeDir, d.name, 'SKILL.md')))
    .map(d => d.name)
    .filter(name => !fs.existsSync(path.join(vendorDir, name)))
    .sort();
}

function printList() {
  console.log('\n=== local orchestration wrappers (always on) ===\n');
  for (const name of localWrappers()) console.log(`  ${name}`);
  console.log('\n=== pinned upstream SKILL.md snapshots (enable on demand) ===\n');
  console.log('  enabled  risk  slug                                   repo@commit');
  for (const s of upstream()) {
    const r = s.risk.map(([k, n]) => `${k}:${n}`).join(',') || '-';
    const repo = `${s.repo || '?'}@${(s.commit || '').slice(0, 7)}`;
    console.log(`  ${s.enabled ? 'YES     ' : 'no      '} ${r.padEnd(18).slice(0, 18)} ${s.slug.padEnd(38)} ${repo}`);
  }
  console.log('\nCopy rule: SKILL.md text only. Upstream scripts, hooks, MCP configs and assets are NOT vendored.');
  console.log('Enable: npm run skills:enable -- --enable <slug>');
  console.log('Audit : npm run skills:enable -- --audit');
  console.log('All   : npm run skills:enable -- --all   (higher context cost)\n');
}

function copySkill(slug, force) {
  const src = path.join(vendorDir, slug);
  const dst = path.join(claudeDir, slug);
  if (!fs.existsSync(path.join(src, 'SKILL.md'))) {
    console.error(`ERROR: unknown upstream skill slug: ${slug}`);
    process.exit(2);
  }
  if (fs.existsSync(path.join(dst, 'SKILL.md')) && !force) {
    console.log(`already enabled: ${slug} (use --force to overwrite)`);
    return;
  }
  if (force && fs.existsSync(dst)) fs.rmSync(dst, { recursive: true, force: true });
  ensure(dst);
  for (const name of ['SKILL.md', 'SOURCE.json']) {
    if (fs.existsSync(path.join(src, name))) fs.copyFileSync(path.join(src, name), path.join(dst, name));
  }
  const text = fs.readFileSync(path.join(src, 'SKILL.md'), 'utf8');
  const r = risk(text);
  console.log(`enabled: ${slug}`);
  console.log(`  source : ${(readJson(path.join(src, 'SOURCE.json'), {}) || {}).url || 'unknown'}`);
  console.log(`  audit  : ${r.length ? r.map(([k, n]) => `${k}:${n}`).join(', ') : 'no flagged patterns'}`);
}

function audit() {
  console.log('\n=== text-only skill audit ===\n');
  for (const s of upstream()) {
    const rows = s.risk.length ? s.risk.map(([k, n]) => `${k}:${n}`).join(', ') : 'clean';
    console.log(`${s.slug.padEnd(40)} ${rows}`);
  }
  console.log('\nFlags are prompts for human review, not proof of malicious code. No upstream executable code is vendored.');
  console.log('Review before enabling: npm run skills:enable -- --enable <slug>\n');
}

if (args.help) {
  console.log(`Usage:
  npm run skills:list
  npm run skills:enable -- --list
  npm run skills:enable -- --audit
  npm run skills:enable -- --enable <slug>
  npm run skills:enable -- --all [--force]
  npm run skills:enable -- --disable <slug>
`);
} else if (args.audit) {
  audit();
} else if (args.all) {
  for (const s of upstream()) copySkill(s.slug, Boolean(args.force));
  console.log(`\nEnabled ${upstream().length} pinned SKILL.md snapshots. Run /doctor to review context cost.`);
} else if (args.enable) {
  copySkill(String(args.enable), Boolean(args.force));
} else if (args.disable) {
  const dst = path.join(claudeDir, String(args.disable));
  if (fs.existsSync(path.join(dst, 'SOURCE.json'))) {
    fs.rmSync(dst, { recursive: true, force: true });
    console.log(`disabled: ${args.disable}`);
  } else {
    console.log(`not an enabled upstream snapshot (local wrappers are not removed): ${args.disable}`);
  }
} else {
  printList();
}
