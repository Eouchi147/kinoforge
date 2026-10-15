#!/usr/bin/env node
// KINOFORGE DOM renderer for motion design: a page laid out with HTML/CSS (real type, variable fonts, blur, 3D transforms),
// stepped frame by frame with a deterministic clock and captured as screenshots, then assembled into an MP4. No AI, no fees.
//
//   node harness/dom-render.cjs <scene dir under ROOT> [--w 1920 --h 1080 --fps 30] [--out DIR] [--stills 1.2,3.5] [--param k=v]
//
// Scene contract: window.KF = { duration, fps?, render(i, t) }   render sets every style from t (no CSS transitions)
//                 window.KF_READY = true once fonts and images are loaded.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const { start, ROOT } = require('./server.cjs');

const args = process.argv.slice(2);
const scene = args[0];
const opt = { w: 1920, h: 1080, fps: 30, stills: [], params: [], out: null, only: false };
for (let i = 1; i < args.length; i++) {
  const a = args[i], next = () => args[++i];
  if (a === '--w') opt.w = +next(); else if (a === '--h') opt.h = +next(); else if (a === '--fps') opt.fps = +next();
  else if (a === '--out') opt.out = next(); else if (a === '--stills') opt.stills = next().split(',').map(Number);
  else if (a === '--stills-only') opt.only = true; else if (a === '--param') opt.params.push(next());
  else { console.error('unknown option', a); process.exit(2); }
}
const name = path.basename(scene.replace(/\/$/, ''));
const outDir = path.resolve(opt.out || path.join(ROOT, 'out', name));
const framesDir = path.join(outDir, 'frames');
fs.rmSync(framesDir, { recursive: true, force: true }); fs.mkdirSync(framesDir, { recursive: true });

(async () => {
  const t0 = Date.now();
  const { server, port } = await start(0);
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none', '--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: opt.w, height: opt.h }, deviceScaleFactor: 1 });
  page.on('console', (m) => console.log('[page]', m.text()));
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  const q = new URLSearchParams({ w: opt.w, h: opt.h });
  for (const p of opt.params) { const [k, v] = p.split('='); q.set(k, v); }
  await page.goto(`http://127.0.0.1:${port}/${scene.replace(/^\/+|\/$/g, '')}/index.html?${q}`, { waitUntil: 'load', timeout: 120000 });
  await page.waitForFunction(() => window.KF_READY === true, null, { timeout: 120000 });
  const fps = (await page.evaluate(() => KF.fps)) || opt.fps;
  const dur = await page.evaluate(() => KF.duration);
  const shot = async (t, file, type) => { await page.evaluate(async ({ i, t }) => { await KF.render(i, t); }, { i: Math.round(t * fps), t }); await page.screenshot({ path: file, type, ...(type === 'jpeg' ? { quality: 94 } : {}) }); };
  for (const t of opt.stills) await shot(t, path.join(outDir, `${name}-${t.toFixed(2)}.png`), 'png');
  if (!opt.only) {
    const total = Math.round(dur * fps);
    for (let i = 0; i < total; i++) await shot(i / fps, path.join(framesDir, String(i).padStart(5, '0') + '.jpg'), 'jpeg');
    const mp4 = path.join(outDir, name + '.mp4');
    const r = spawnSync('ffmpeg', ['-nostdin', '-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(framesDir, '%05d.jpg'),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4], { stdio: 'inherit' });
    if (r.status !== 0) { console.error('ffmpeg failed'); process.exit(1); }
    console.log('wrote', mp4, `${total} frames`);
  }
  await browser.close(); server.close();
  console.log(`done in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
})().catch((e) => { console.error(e); process.exit(1); });
