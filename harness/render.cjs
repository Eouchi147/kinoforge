#!/usr/bin/env node
// KINOFORGE frame renderer: loads a scene page in headless Chromium (SwiftShader, no GPU needed), steps it
// frame by frame with a deterministic clock, saves PNGs, then assembles an MP4 (+ optional audio) with ffmpeg.
//
//   node render.cjs <scene path under ROOT, e.g. proto/p05-relic> [options]
//     --out DIR        frames + mp4 go here (default: out/<scene name>)
//     --w 1280 --h 720 --fps 24
//     --start 0 --end N   frame range [start, end) for chunked renders (end defaults to total)
//     --mp4            assemble out/<name>.mp4 after rendering (needs the full range)
//     --audio FILE     wav/mp3 to mux into the mp4
//     --contact        also write a 6x2 contact sheet jpg
//     --skip-existing  don't re-render frames already on disk
//     --jpg            capture JPEG 95 instead of PNG (faster, smaller)
//     --param k=v      extra query params passed to the page (repeatable)
//
// Scene contract (window.KF, set by the page before signalling ready):
//   KF.width, KF.height (read from ?w=&h= query), KF.fps, KF.duration (seconds)
//   KF.canvas            the canvas to capture
//   await KF.render(frameIndex, timeSeconds)   draws that exact frame (deterministic)
//   window.KF_READY = true   when assets/fonts are loaded (or KF.ready promise)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const { start, ROOT } = require('./server.cjs');

const args = process.argv.slice(2);
const scene = args[0];
if (!scene || scene.startsWith('--')) { console.error('usage: node render.cjs <scene-dir> [--out DIR] [--w 1280 --h 720 --fps 24] [--mp4] [--audio f.wav]'); process.exit(2); }
const opt = { w: 1280, h: 720, fps: 24, start: 0, end: -1, mp4: false, audio: null, contact: false, skip: false, jpg: false, params: [] };
for (let i = 1; i < args.length; i++) {
  const a = args[i];
  const next = () => args[++i];
  if (a === '--out') opt.out = next();
  else if (a === '--w') opt.w = +next();
  else if (a === '--h') opt.h = +next();
  else if (a === '--fps') opt.fps = +next();
  else if (a === '--start') opt.start = +next();
  else if (a === '--end') opt.end = +next();
  else if (a === '--mp4') opt.mp4 = true;
  else if (a === '--audio') opt.audio = next();
  else if (a === '--contact') opt.contact = true;
  else if (a === '--skip-existing') opt.skip = true;
  else if (a === '--jpg') opt.jpg = true;
  else if (a === '--param') opt.params.push(next());
  else { console.error('unknown option', a); process.exit(2); }
}
const name = path.basename(scene.replace(/\/$/, ''));
const outDir = path.resolve(opt.out || path.join(ROOT, 'out', name));
const framesDir = path.join(outDir, 'frames');
fs.mkdirSync(framesDir, { recursive: true });

(async () => {
  const t0 = Date.now();
  const { server, port } = await start(0);
  const browser = await chromium.launch({
    headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
      '--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--disable-web-security', '--font-render-hinting=none',
      '--js-flags=--max-old-space-size=4096'],
  });
  const page = await browser.newPage({ viewport: { width: opt.w, height: opt.h }, deviceScaleFactor: 1 });
  page.on('console', (m) => { const t = m.text(); if (!/favicon/.test(t)) console.log('[page]', t); });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  const q = new URLSearchParams({ w: opt.w, h: opt.h, fps: opt.fps });
  for (const p of opt.params) { const [k, v] = p.split('='); q.set(k, v); }
  const url = `http://127.0.0.1:${port}/${scene.replace(/^\/+/, '').replace(/\/$/, '')}/index.html?${q}`;
  console.log('scene', url);
  await page.goto(url, { waitUntil: 'load', timeout: 120000 });
  await page.waitForFunction(() => window.KF_READY === true, null, { timeout: 180000 });
  const info = await page.evaluate(() => ({ fps: KF.fps, duration: KF.duration, w: KF.width, h: KF.height, shots: (KF.shots || []).map(s => s.name + ':' + s.dur) }));
  const fps = info.fps || opt.fps;
  const total = Math.round(info.duration * fps);
  const end = opt.end < 0 ? total : Math.min(opt.end, total);
  console.log(`ready in ${((Date.now() - t0) / 1000).toFixed(1)}s — ${info.w}x${info.h} @${fps} fps, ${info.duration}s = ${total} frames; rendering [${opt.start}, ${end})`, info.shots.length ? '\nshots: ' + info.shots.join(' | ') : '');
  const ext = opt.jpg ? 'jpg' : 'png';
  let tStart = Date.now();
  for (let i = opt.start; i < end; i++) {
    const file = path.join(framesDir, String(i).padStart(5, '0') + '.' + ext);
    if (opt.skip && fs.existsSync(file)) continue;
    const t = i / fps;
    const data = await page.evaluate(async ({ i, t, jpg }) => {
      await KF.render(i, t);
      return KF.canvas.toDataURL(jpg ? 'image/jpeg' : 'image/png', 0.95);
    }, { i, t, jpg: opt.jpg });
    fs.writeFileSync(file, Buffer.from(data.slice(data.indexOf(',') + 1), 'base64'));
    if ((i - opt.start + 1) % 24 === 0 || i === end - 1) {
      const done = i - opt.start + 1, el = (Date.now() - tStart) / 1000;
      console.log(`frame ${i + 1}/${end}  ${(el / done).toFixed(2)} s/frame  eta ${((end - i - 1) * el / done / 60).toFixed(1)} min`);
    }
  }
  await browser.close();
  server.close();
  if (opt.mp4) {
    const mp4 = path.join(outDir, name + '.mp4');
    const ff = ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(framesDir, '%05d.' + ext)];
    if (opt.audio) ff.push('-i', path.resolve(opt.audio));
    ff.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart');
    if (opt.audio) ff.push('-c:a', 'aac', '-b:a', '256k', '-shortest');
    ff.push(mp4);
    const r = spawnSync('ffmpeg', ff, { stdio: 'inherit' });
    if (r.status !== 0) { console.error('ffmpeg failed'); process.exit(1); }
    console.log('wrote', mp4);
    if (opt.contact) {
      const n = end - opt.start, step = Math.max(1, Math.floor(n / 12));
      const sheet = path.join(outDir, name + '.contact.jpg');
      spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', mp4, '-vf', `select='not(mod(n\\,${step}))',scale=320:-2,tile=6x2`, '-frames:v', '1', '-q:v', '3', sheet], { stdio: 'inherit' });
      console.log('wrote', sheet);
    }
  }
  console.log(`done in ${((Date.now() - t0) / 60000).toFixed(1)} min`);
})().catch((e) => { console.error(e); process.exit(1); });
