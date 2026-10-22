#!/usr/bin/env node
// Render many stills in ONE browser session: node films/lib/kinetic/tools/stills.cjs films/studio/kinetic-demo --t 3,17.6,40 --out /tmp/x [--w 720 --h 1280] [--f 100,200] [--range a,b,step] [--param k=v] [--sheet]
// Prints the engine's warnings and any spec error (unknown cue word, em dash...). With --cards, renders one still per card (at its first landing) and
// with --sheet also writes a contact sheet (sheet.jpg) using ffmpeg if available.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { spawnSync } = require('child_process'); const { start, ROOT } = require('../../../../harness/server.cjs');
const a = process.argv.slice(2); const scene = a[0]; const o = { w: 720, h: 1280, t: [], f: [], out: '/tmp/kinetic-stills', params: [], cards: false, sheet: false };
for (let i = 1; i < a.length; i++) { const k = a[i]; if (k === '--t') o.t = a[++i].split(',').map(Number); else if (k === '--f') o.f = a[++i].split(',').map(Number); else if (k === '--w') o.w = +a[++i]; else if (k === '--h') o.h = +a[++i]; else if (k === '--out') o.out = a[++i]; else if (k === '--param') o.params.push(a[++i]); else if (k === '--cards') o.cards = true; else if (k === '--sheet') o.sheet = true; else if (k === '--range') { const [s, e, st] = a[++i].split(',').map(Number); for (let x = s; x < e; x += st || 1) o.f.push(x); } }
(async () => {
  fs.mkdirSync(o.out, { recursive: true }); const { server, port } = await start(0);
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none', '--disable-web-security'] });
  const page = await browser.newPage({ viewport: { width: o.w, height: o.h }, deviceScaleFactor: 1 });
  page.on('console', (m) => { const t = m.text(); if (!/favicon/.test(t)) console.log('[page]', t); }); page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  const qs = new URLSearchParams({ w: o.w, h: o.h, fps: 24 }); for (const p of o.params) { const [k, v] = p.split('='); qs.set(k, v); }
  const t0 = Date.now(); await page.goto(`http://127.0.0.1:${port}/${scene.replace(/^\/+/, '').replace(/\/$/, '')}/index.html?${qs}`, { waitUntil: 'load', timeout: 180000 });
  try { await page.waitForFunction(() => window.KF_READY === true || window.KF_ERROR, null, { timeout: 120000 }); } catch (e) { console.error('timeout waiting for KF_READY'); }
  const err = await page.evaluate(() => window.KF_ERROR); if (err) { console.error('SPEC ERROR:', err); await browser.close(); server.close(); process.exit(2); }
  console.log('ready in', ((Date.now() - t0) / 1000).toFixed(1), 's'); const warn = await page.evaluate(() => window.KF_WARNINGS || []); for (const w of warn) console.log('WARNING:', w);
  const fps = await page.evaluate(() => KF.fps); const list = [...o.t.map((t) => [Math.round(t * fps), t]), ...o.f.map((f) => [f, f / fps])];
  if (o.cards) { const cs = await page.evaluate(() => KF.cards); for (const c of cs) { if (c.over) continue; const t = Math.min(c.t1 - 0.05, Math.max(c.t0 + 0.1, c.lastT + 0.35)); list.push([Math.round(t * fps), t]); } }
  const files = []; let tot = 0;
  for (const [i, t] of list) { const s = Date.now(); const d = await page.evaluate(async ({ i, t }) => { await KF.render(i, t); return KF.canvas.toDataURL('image/jpeg', 0.92); }, { i, t });
    const file = path.join(o.out, `f${String(i).padStart(5, '0')}.jpg`); fs.writeFileSync(file, Buffer.from(d.slice(d.indexOf(',') + 1), 'base64')); files.push(file); const dt = (Date.now() - s) / 1000; tot += dt; console.log(file, 't=' + t.toFixed(2), dt.toFixed(2) + 's'); }
  if (list.length) console.log('mean s/frame', (tot / list.length).toFixed(2));
  if (o.sheet && files.length) { const cols = Math.min(8, files.length), rows = Math.ceil(files.length / cols); const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-pattern_type', 'glob', '-i', path.join(o.out, 'f*.jpg'), '-vf', `scale=180:-1,tile=${cols}x${rows}`, '-frames:v', '1', path.join(o.out, 'sheet.jpg')]); if (r.status === 0) console.log('sheet', path.join(o.out, 'sheet.jpg')); else console.log('sheet failed', String(r.stderr)); }
  await browser.close(); server.close();
})().catch((e) => { console.error(e); process.exit(1); });
