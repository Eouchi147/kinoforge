#!/usr/bin/env node
// social/lib/safecheck.mjs: step through a social video, every frame, and check that nothing that must stay safe (text:
// words, numbers, URLs; elements tagged data-safe: logo marks) enters the platform zones. The zone is SAFE in brief.mjs
// (rule R-2-08: left 11%, right 22%, top 15%, bottom 35%). No screenshots, so it is quick (seconds per video).
//
//   node social/lib/safecheck.mjs social/templates/card-motion                                  (the template's sample)
//   node social/lib/safecheck.mjs social/templates/card-motion --brief /social/batches/smartmount/2026-12/batch.json --id v01-tip-height
//   options: --step 0.1 (seconds between checks; default: every frame)   --json out.json (write the report)
// Exit code 1 when anything is outside the safe box by more than 2 px (a defect: the platform would draw over it).
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { safeBox } from './brief.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('../../harness/node_modules/playwright');
const { start } = require('../../harness/server.cjs');

const args = process.argv.slice(2), scene = args[0].replace(/^\/+|\/$/g, '');
const opt = { step: null, brief: null, id: null, json: null };
for (let i = 1; i < args.length; i++) { const k = args[i].replace(/^--/, ''); opt[k] = args[++i]; }
const SAFE = safeBox(), TOL = 2;

const { server, port } = await start(0);
const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none', '--force-color-profile=srgb'] });
let code = 0;
try {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => { console.error('[pageerror]', e.message); code = 2; });
  const q = new URLSearchParams({ w: 1080, h: 1920 }); if (opt.brief) q.set('brief', opt.brief); if (opt.id) q.set('id', opt.id);
  await page.goto(`http://127.0.0.1:${port}/${scene}/index.html?${q}`, { waitUntil: 'load', timeout: 120000 });
  await page.waitForFunction(() => window.KF_READY === true || window.KF_ERROR, null, { timeout: 120000 });
  const err = await page.evaluate(() => window.KF_ERROR || null); if (err) throw new Error(err);
  const dur = await page.evaluate(() => KF.duration), fps = (await page.evaluate(() => KF.fps)) || 30;
  const bad = new Map(); let frames = 0;
  const every = opt.step ? Math.max(1, Math.round(+opt.step * fps)) : 1, last = Math.round(dur * fps);   // frame indices: no drift
  for (let i = 0; i <= last; i += every) {
    const t = i / fps;
    const boxes = await page.evaluate(async ({ i, t }) => { await KF.render(i, t); return window.KF_TEXT(); }, { i, t });
    frames++;
    for (const b of boxes) {
      const over = { left: SAFE.x0 - b.x0, right: b.x1 - SAFE.x1, top: SAFE.y0 - b.y0, bottom: b.y1 - SAFE.y1 };
      const worst = Object.entries(over).filter(([, v]) => v > TOL);
      if (!worst.length) continue;
      const key = b.text + ' | ' + worst.map(([s]) => s).join(',');
      const prev = bad.get(key); const px = Math.max(...worst.map(([, v]) => v));
      if (!prev) bad.set(key, { text: b.text, sides: worst.map(([s]) => s), from: +t.toFixed(2), to: +t.toFixed(2), px: Math.round(px), op: b.op });
      else { prev.to = +t.toFixed(2); prev.px = Math.max(prev.px, Math.round(px)); prev.op = Math.max(prev.op, b.op); }
    }
  }
  const report = { scene, brief: opt.brief, id: opt.id, safe: SAFE, frames, duration: dur, violations: [...bad.values()] };
  if (opt.json) { fs.mkdirSync(path.dirname(path.resolve(opt.json)), { recursive: true }); fs.writeFileSync(opt.json, JSON.stringify(report, null, 1)); }
  if (report.violations.length) {
    code = code || 1;
    console.log(`SAFE ZONE: ${report.violations.length} problem(s) in ${scene}${opt.id ? ' ' + opt.id : ''}`);
    for (const v of report.violations) console.log(`  "${v.text}" crosses ${v.sides.join(' and ')} by up to ${v.px}px, ${v.from}s to ${v.to}s (opacity up to ${v.op})`);
  } else console.log(`safe zone ok: ${scene}${opt.id ? ' ' + opt.id : ''}, ${frames} frames checked over ${dur}s (R-2-08 box x ${SAFE.x0} to ${SAFE.x1}, y ${SAFE.y0} to ${SAFE.y1})`);
} catch (e) { console.error(e.message || e); code = 2; }
await browser.close(); server.close();
process.exit(code);
