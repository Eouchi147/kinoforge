// node shot.cjs <path under repo root> <out.png> [w h]  -> screenshot of any page served by the harness server (waits for window.READY)
const { chromium } = require('playwright'); const { start } = require('../../../../harness/server.cjs');
(async () => { const { server, port } = await start(0); const b = await chromium.launch({ args: ['--no-sandbox'] }); const p = await b.newPage({ viewport: { width: +(process.argv[4] || 1280), height: +(process.argv[5] || 520) } });
  p.on('console', (m) => console.log('[page]', m.text())); p.on('pageerror', (e) => console.log('[err]', e.message));
  await p.goto(`http://127.0.0.1:${port}/${process.argv[2]}`); await p.waitForFunction(() => window.READY === true, null, { timeout: 20000 }); await p.screenshot({ path: process.argv[3] }); await b.close(); server.close(); })();
