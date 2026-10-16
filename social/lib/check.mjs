#!/usr/bin/env node
// social/lib/check.mjs: check a batch before anything is rendered (no browser, no fees): templates exist, photos are in the
// client's media.json and on disk, every word passes the house style and the card limits, captions fit every platform,
// ids are unique, the music cap is sane. Writes the render matrix for the workflow.
//
//   node social/lib/check.mjs social/batches/smartmount/2026-12 [--only v01-tip-height,v02-teach-arc] [--matrix matrix.json]
// Exit code 1 on any problem. The safe-zone check needs a browser and runs per video (safecheck.mjs).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolveVideo, briefProblems } from './brief.mjs';
import { captions, PLATFORMS } from './captions.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const args = process.argv.slice(2), opt = { only: '', matrix: null };
const dir = args.shift();
for (let i = 0; i < args.length; i++) { const k = args[i].replace(/^--/, ''); opt[k] = args[++i] ?? ''; }
if (!dir) { console.error('usage: check.mjs <batch dir> [--only ids] [--matrix file]'); process.exit(2); }

const problems = [], read = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const batch = read(path.join(dir, 'batch.json'));
const brand = read(path.join(ROOT, 'social', 'clients', batch.client, 'brand.json'));
const media = read(path.join(ROOT, 'social', 'clients', batch.client, 'media', 'media.json'));
const photos = media.photos.map((p) => p.file);
const templates = fs.readdirSync(path.join(ROOT, 'social', 'templates')).filter((t) => fs.existsSync(path.join(ROOT, 'social', 'templates', t, 'index.html')));
for (const p of photos) if (!fs.existsSync(path.join(ROOT, 'social', 'clients', batch.client, 'media', p))) problems.push(`media.json lists ${p} but the file is missing`);
if (!batch.batch || !/^[A-Za-z0-9_.]+(?:[A-Za-z0-9_.]|-(?=[A-Za-z0-9]))*$/.test(batch.batch)) problems.push(`batch name "${batch.batch}" must be letters, digits, dots, underscores or single hyphens`);
if (path.basename(path.resolve(dir)) !== batch.batch || path.basename(path.dirname(path.resolve(dir))) !== batch.client) problems.push(`folder should be social/batches/${batch.client}/${batch.batch}`);
const m = batch.music;
if (m && m.enabled !== false) {
  if (!m.prompt) problems.push('music is enabled but has no prompt');
  if (!(m.cap_usd > 0) || m.cap_usd > 0.5) problems.push(`music cap_usd ${m.cap_usd} must be above 0 and at most 0.5 (one Lyria clip costs about $0.04 to $0.08)`);
}
const only = String(opt.only || '').split(',').map((s) => s.trim()).filter(Boolean), ids = new Set(), matrix = [];
for (const v of batch.videos || []) {
  if (!v.id || !/^[a-z0-9][a-z0-9-]*$/.test(v.id)) problems.push(`video id "${v.id}" must be lower case letters, digits and hyphens`);
  if (ids.has(v.id)) problems.push(`video id "${v.id}" is used twice`); ids.add(v.id);
  const brief = resolveVideo(batch, v.id);
  const where = `${v.id}: `;
  for (const p of briefProblems(brief, brand, { templates, photos })) problems.push(where + p);
  for (const p of brief.platforms || []) if (!PLATFORMS.includes(p)) problems.push(where + `unknown platform "${p}"`);
  const cap = captions(brief, brand, { music: m && m.enabled !== false ? 'ai' : 'none' });
  for (const p of cap.checks.problems) problems.push(where + p);
  if (!only.length || only.includes(v.id)) matrix.push({ id: v.id, template: brief.template, name: `${batch.client}-${batch.batch}-${v.id}` });
}
for (const o of only) if (!ids.has(o)) problems.push(`--only names "${o}", which is not in the batch`);
if (!matrix.length) problems.push('nothing to render');
const used = (batch.videos || []).map((v) => v.photo); const dup = used.filter((p, i) => used.indexOf(p) !== i);
if (dup.length) console.log(`note: photos used more than once: ${[...new Set(dup)].join(', ')}`);
console.log(`batch ${batch.client}/${batch.batch}: ${(batch.videos || []).length} videos, ${matrix.length} to render, templates ${[...new Set(matrix.map((x) => x.template))].join(', ')}, music ${m && m.enabled !== false ? 'yes (cap $' + m.cap_usd + ')' : 'no'}`);
if (opt.matrix) fs.writeFileSync(opt.matrix, JSON.stringify(matrix));
if (problems.length) { console.error('PROBLEMS:\n  ' + problems.join('\n  ')); process.exit(1); }
console.log('batch ok');
