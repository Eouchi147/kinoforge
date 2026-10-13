// Dev helper (not part of the scene): render a list of frames in ONE browser session via the same page/contract as harness/render.cjs.
//   PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node proto/p13-pixel-vigil/tools/frames.cjs 0,43,87 [--w 1280 --h 720] [--out out/p13-pixel-vigil/dev]  (never the harness frames dir)
const path = require('path'), fs = require('fs');
const ROOT = path.resolve(__dirname, '..', '..', '..');
const { chromium } = require(path.join(ROOT, 'harness', 'node_modules', 'playwright'));
const { start } = require(path.join(ROOT, 'harness', 'server.cjs'));
const args = process.argv.slice(2); const list = args[0].split(',').map(Number);
let w = 1280, h = 720, out = path.join(ROOT, 'out', 'p13-pixel-vigil', 'dev');
for (let i = 1; i < args.length; i++) { if (args[i] === '--w') w = +args[++i]; else if (args[i] === '--h') h = +args[++i]; else if (args[i] === '--out') out = path.resolve(args[++i]); }
fs.mkdirSync(out, { recursive: true });
(async () => {
  const { server, port } = await start(0);
  const browser = await chromium.launch({ headless: true, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--disable-web-security', '--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  page.on('console', (m) => console.log('[page]', m.text())); page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${port}/proto/p13-pixel-vigil/index.html?w=${w}&h=${h}&fps=24`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.KF_READY === true, null, { timeout: 180000 });
  const t0 = Date.now();
  for (const i of list) {
    const data = await page.evaluate(async ({ i }) => { await KF.render(i, i / 24); return KF.canvas.toDataURL('image/png'); }, { i });
    fs.writeFileSync(path.join(out, String(i).padStart(5, '0') + '.png'), Buffer.from(data.slice(data.indexOf(',') + 1), 'base64'));
  }
  console.log(`rendered ${list.length} frames in ${((Date.now() - t0) / 1000).toFixed(1)} s (${((Date.now() - t0) / 1000 / list.length).toFixed(2)} s/frame) at ${w}x${h}`);
  await browser.close(); server.close();
})().catch((e) => { console.error(e); process.exit(1); });
