#!/usr/bin/env node
// Stills from a NOOR film in one browser session: node films/noor/n05-iqra/tools/stills.cjs <film dir> --t 4,10.5,22 [--w 640 --h 360] [--out /tmp/x] [--shots]
// --shots: one still in the middle of every shot (and one 0.6 s after each shot starts). Writes JPEGs named by time.
const path = require('path'); const fs = require('fs');
const ROOTH = path.resolve(__dirname, '../../../../harness');
const { chromium } = require(path.join(ROOTH, 'node_modules/playwright'));
const { start } = require(path.join(ROOTH, 'server.cjs'));
const a = process.argv.slice(2); const film = a[0]; const opt = { w: 640, h: 360, out: '/tmp/stills', t: [], shots: false, params: [] };
for (let i = 1; i < a.length; i++) { const k = a[i]; if (k === '--w') opt.w = +a[++i]; else if (k === '--h') opt.h = +a[++i]; else if (k === '--out') opt.out = a[++i]; else if (k === '--t') opt.t = a[++i].split(',').map(Number); else if (k === '--shots') opt.shots = true; else if (k === '--param') opt.params.push(a[++i]); }
fs.mkdirSync(opt.out, { recursive: true });
(async () => {
  const { server, port } = await start(0);
  const browser = await chromium.launch({ headless: true, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--font-render-hinting=none', '--js-flags=--max-old-space-size=4096'] });
  const page = await browser.newPage({ viewport: { width: opt.w, height: opt.h } });
  page.on('console', (m) => console.log('[page]', m.text())); page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  const q = new URLSearchParams({ w: opt.w, h: opt.h, fps: 24 }); for (const p of opt.params) { const [k, v] = p.split('='); q.set(k, v); }
  await page.goto(`http://127.0.0.1:${port}/${film.replace(/\/$/, '')}/index.html?${q}`, { waitUntil: 'load', timeout: 120000 });
  await page.waitForFunction(() => window.KF_READY === true || window.KF_ERROR, null, { timeout: 180000 });
  let ts = opt.t;
  if (opt.shots) { const sh = await page.evaluate(() => window.__kf.SHOTS.map((s) => [s.id, s.t0, s.t1])); ts = []; for (const [id, t0, t1] of sh) { ts.push(+(t0 + 0.6).toFixed(2), +((t0 + t1) / 2).toFixed(2)); console.log(id, t0.toFixed(2), t1.toFixed(2)); } }
  for (const t of ts) { const t0 = Date.now(); const data = await page.evaluate(async (t) => { await KF.render(Math.round(t * 24), Math.round(t * 24) / 24); return KF.canvas.toDataURL('image/jpeg', 0.9); }, t);
    const f = path.join(opt.out, `t${String(t.toFixed(2)).padStart(7, '0')}.jpg`); fs.writeFileSync(f, Buffer.from(data.slice(data.indexOf(',') + 1), 'base64')); console.log(f, ((Date.now() - t0) / 1000).toFixed(1) + 's'); }
  await browser.close(); server.close();
})().catch((e) => { console.error(e); process.exit(1); });
