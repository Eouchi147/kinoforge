#!/usr/bin/env node
// Render many stills in ONE browser session (the sheet is baked once): node films/lib/battlemap/tools/stills.cjs films/battles/cannae --t 3,17.6,40 --out /tmp/x [--w 1280 --h 720] [--f 100,200] [--param k=v]
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { start, ROOT } = require('../../../../harness/server.cjs');
const a = process.argv.slice(2); const scene = a[0]; const o = { w: 1280, h: 720, t: [], f: [], out: '/tmp/claude-0/kf-stills', params: [], q: 90 };
for (let i = 1; i < a.length; i++) { const k = a[i]; if (k === '--t') o.t = a[++i].split(',').map(Number); else if (k === '--f') o.f = a[++i].split(',').map(Number); else if (k === '--w') o.w = +a[++i]; else if (k === '--h') o.h = +a[++i]; else if (k === '--out') o.out = a[++i]; else if (k === '--param') o.params.push(a[++i]); else if (k === '--range') { const [s, e, st] = a[++i].split(',').map(Number); for (let x = s; x < e; x += st || 1) o.f.push(x); } }
(async () => {
  fs.mkdirSync(o.out, { recursive: true }); const { server, port } = await start(0);
  const browser = await chromium.launch({ headless: true, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--disable-web-security', '--font-render-hinting=none', '--js-flags=--max-old-space-size=4096'] });
  const page = await browser.newPage({ viewport: { width: o.w, height: o.h }, deviceScaleFactor: 1 });
  page.on('console', (m) => { const t = m.text(); if (!/favicon/.test(t)) console.log('[page]', t); }); page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  const qs = new URLSearchParams({ w: o.w, h: o.h, fps: 24 }); for (const p of o.params) { const [k, v] = p.split('='); qs.set(k, v); }
  const t0 = Date.now(); await page.goto(`http://127.0.0.1:${port}/${scene.replace(/^\/+/, '').replace(/\/$/, '')}/index.html?${qs}`, { waitUntil: 'load', timeout: 180000 });
  await page.waitForFunction(() => window.KF_READY === true, null, { timeout: 300000 }); console.log('ready in', ((Date.now() - t0) / 1000).toFixed(1), 's');
  const fps = await page.evaluate(() => KF.fps); const list = [...o.t.map((t) => [Math.round(t * fps), t]), ...o.f.map((f) => [f, f / fps])];
  for (const [i, t] of list) { const s = Date.now(); const d = await page.evaluate(async ({ i, t }) => { await KF.render(i, t); return KF.canvas.toDataURL('image/jpeg', 0.92); }, { i, t });
    const file = path.join(o.out, `f${String(i).padStart(5, '0')}.jpg`); fs.writeFileSync(file, Buffer.from(d.slice(d.indexOf(',') + 1), 'base64')); console.log(file, ((Date.now() - s) / 1000).toFixed(2) + 's'); }
  await browser.close(); server.close();
})().catch((e) => { console.error(e); process.exit(1); });
