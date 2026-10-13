// Dev helper: render frame N, then evaluate a JS expression (page context; window.__p13 = {world,camera,post}) and print the result.
//   node proto/p13-pixel-vigil/tools/probe.cjs 173 "<js expression returning JSON-able>"
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..', '..');
const { chromium } = require(path.join(ROOT, 'harness', 'node_modules', 'playwright'));
const { start } = require(path.join(ROOT, 'harness', 'server.cjs'));
const frame = +process.argv[2], expr = process.argv[3];
(async () => {
  const { server, port } = await start(0);
  const browser = await chromium.launch({ headless: true, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--disable-web-security'] });
  const page = await browser.newPage({ viewport: { width: 640, height: 360 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${port}/proto/p13-pixel-vigil/index.html?w=640&h=360&fps=24`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.KF_READY === true, null, { timeout: 180000 });
  const r = await page.evaluate(async ({ frame, expr }) => { await KF.render(frame, frame / 24); return (0, eval)(expr); }, { frame, expr });
  console.log(typeof r === 'string' ? r : JSON.stringify(r, null, 1));
  await browser.close(); server.close();
})().catch((e) => { console.error(e); process.exit(1); });
