#!/usr/bin/env node
// check.cjs: the director's checks in code. Loads a film in headless Chromium (harness/server.cjs + harness/node_modules/playwright),
// lints the spec against the cues, renders stills at every narration line and a few word times, and writes:
//   <out>/report.json  { ok, hard: [...], soft: [...], lint: {errors, warnings}, stills: [...], ready_s, still_s }
//   <out>/sheet.jpg    contact sheet, the narration line under each still (for the eyes seat)
//   <out>/stills/*.jpg
// Hard problems (the candidate cannot ship): spec syntax error, page errors, console errors, lint errors, a still that fails to render,
// blank frames, load timeout. Soft problems (sent to the coder, never block): text off screen, overlapping text, lint warnings.
//
//   node films/director/check.cjs films/studio/<id> [--spec ./spec.js] [--out dir] [--line battle-map] [--max 28] [--times 3,17.5]
// The spec path is relative to the film folder (the film's index.html reads ?spec=). Exit 0 with a report; 2 if the checker itself broke.
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const { chromium } = require(path.join(ROOT, 'harness', 'node_modules', 'playwright'));
const { start } = require(path.join(ROOT, 'harness', 'server.cjs'));

const a = process.argv.slice(2); const film = a[0].replace(/\/+$/, ''); const o = { spec: './spec.js', out: null, line: null, max: 28, times: null, timeout: 240 };
for (let i = 1; i < a.length; i++) { const k = a[i]; const v = a[++i]; if (k === '--spec') o.spec = v; else if (k === '--out') o.out = v; else if (k === '--line') o.line = v; else if (k === '--max') o.max = +v; else if (k === '--times') o.times = v.split(',').map(Number); else if (k === '--timeout') o.timeout = +v; }
const filmAbs = path.resolve(ROOT, film); const filmRel = path.relative(ROOT, filmAbs);
const out = path.resolve(o.out || path.join(filmAbs, 'check', path.basename(o.spec).replace(/\.m?js$/, '')));
fs.mkdirSync(path.join(out, 'stills'), { recursive: true });
const lines = JSON.parse(fs.readFileSync(path.join(__dirname, 'lines.json'), 'utf8'));
const filmJson = JSON.parse(fs.readFileSync(path.join(filmAbs, 'film.json'), 'utf8'));
let lineName = o.line || filmJson.line; if (!lineName) { try { lineName = JSON.parse(fs.readFileSync(path.join(filmAbs, 'brief.json'), 'utf8')).line; } catch {} } lineName = lineName || 'battle-map';
const L = lines[lineName] || {}; const W = filmJson.render_w || (L.render || [1280])[0], H = filmJson.render_h || (L.render || [0, 720])[1];
const cues = JSON.parse(fs.readFileSync(path.join(filmAbs, 'cues.json'), 'utf8'));
const report = { film: filmRel, spec: o.spec, line: lineName, ok: false, hard: [], soft: [], lint: { errors: [], warnings: [] }, stills: [], page_errors: [], console_errors: [], ready_s: null, still_s: null, sheet: null };
const save = () => fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 1));
const uniq = (arr) => [...new Set(arr)];

// 1. syntax: node --check on a copy with an .mjs name (ES module)
const specAbs = path.resolve(filmAbs, o.spec);
if (!fs.existsSync(specAbs)) { report.hard.push(`spec file ${o.spec} does not exist`); save(); process.exit(0); }
try { const tmp = path.join(out, 'syntax.mjs'); fs.copyFileSync(specAbs, tmp); execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' }); fs.unlinkSync(tmp); }
catch (e) { const msg = String(e.stderr || e.message).split('\n').filter((l) => l.trim() && !/^\s+at /.test(l) && !/^Node\.js/.test(l)).slice(0, 6).join(' | ').replace(/\S*syntax\.mjs/g, o.spec);
  report.hard.push('syntax error: ' + msg); save(); console.log(JSON.stringify({ ok: false, hard: report.hard.length })); process.exit(0); }
const src = fs.readFileSync(specAbs, 'utf8');
if (/^\s*import\s/m.test(src)) report.hard.push('the spec must not import anything (it is data: export default { ... })');
if (/Math\.random|Date\.now|performance\.now/.test(src)) report.hard.push('the spec must be deterministic: no Math.random, Date.now or performance.now');

// the times to look at: each narration line, the title card, the end card, plus a few word times the spec uses
function stillTimes() {
  if (o.times) return o.times.map((t) => ({ t, why: 'asked' }));
  const T = []; const dur = cues.duration;
  for (const l of cues.lines) T.push({ t: Math.min(l.end, l.start + Math.min(1.2, (l.end - l.start) * 0.5)), why: l.id, line: l.id });
  const tl = cues.lines.find((l) => l.id === cues.title_line); if (tl) T.push({ t: tl.end + 0.6, why: 'title card', line: tl.id });
  T.push({ t: Math.max(0, dur - 1.0), why: 'end card' });
  const refs = uniq([...src.matchAll(/['"](l\d\d\.[^'"#>+]+)/g)].map((m) => m[1]));
  const words = []; for (const r of refs) { const [lid, w] = r.split('.'); const ln = cues.lines.find((x) => x.id === lid); if (!ln) continue; const n = w.toLowerCase().replace(/[^a-z0-9]/g, '');
    const hit = (ln.words || []).find((x) => x[0].toLowerCase().replace(/[^a-z0-9]/g, '') === n); if (hit) words.push({ t: hit[1] + 0.7, why: r, line: lid }); }
  T.sort((p, q) => p.t - q.t); const extra = Math.max(0, o.max - T.length);
  for (let k = 0; k < Math.min(extra, words.length); k++) T.push(words[Math.floor(k * words.length / Math.min(extra, words.length))]);
  T.sort((p, q) => p.t - q.t); const outT = []; for (const x of T) if (!outT.length || x.t - outT[outT.length - 1].t > 0.45) outT.push(x);
  return outT.slice(0, Math.max(o.max, cues.lines.length + 2));
}
const lineAt = (t) => { let cur = null; for (const l of cues.lines) if (t >= l.start - 0.05) cur = l; return cur; };

(async () => {
  const { server, port } = await start(0);
  const browser = await chromium.launch({ headless: true, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--font-render-hinting=none', '--js-flags=--max-old-space-size=4096'] });
  try {
    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    // record every fillText on a full-size canvas (the overlay): text, its box on screen, its alpha
    await page.addInitScript(({ W, H }) => { window.__kfText = []; window.__kfRec = false; const P = CanvasRenderingContext2D.prototype; const orig = P.fillText;
      P.fillText = function (text, x, y, ...rest) { try { if (window.__kfRec && this.canvas && this.canvas.width === W && this.canvas.height === H && String(text).trim().length >= 2) {
        const m = this.measureText(text); const tr = this.getTransform(); const xs = [x - m.actualBoundingBoxLeft, x + m.actualBoundingBoxRight], ys = [y - m.actualBoundingBoxAscent, y + m.actualBoundingBoxDescent];
        const pts = []; for (const px of xs) for (const py of ys) pts.push([tr.a * px + tr.c * py + tr.e, tr.b * px + tr.d * py + tr.f]);
        const bx = pts.map((p) => p[0]), by = pts.map((p) => p[1]); window.__kfText.push({ text: String(text), x0: Math.min(...bx), x1: Math.max(...bx), y0: Math.min(...by), y1: Math.max(...by), a: this.globalAlpha }); } } catch (e) {}
        return orig.call(this, text, x, y, ...rest); }; }, { W, H });
    page.on('pageerror', (e) => report.page_errors.push(String(e.message || e).slice(0, 400)));
    page.on('console', (m) => { if (m.type() === 'error' && !/favicon/.test(m.text())) report.console_errors.push(m.text().slice(0, 300)); });
    page.on('requestfailed', (r) => report.console_errors.push(`request failed: ${r.url().replace(/^https?:\/\/[^/]+/, '')}`));
    page.on('response', (r) => { if (r.status() >= 400 && !/favicon/.test(r.url())) report.console_errors.push(`HTTP ${r.status()}: ${r.url().replace(/^https?:\/\/[^/]+/, '')}`); });
    const qs = new URLSearchParams({ w: W, h: H, fps: filmJson.fps || 24, spec: o.spec });
    const t0 = Date.now(); await page.goto(`http://127.0.0.1:${port}/${filmRel}/index.html?${qs}`, { waitUntil: 'load', timeout: 120000 });
    // wait for KF_READY, but stop at the first page error (a spec that throws never gets ready)
    // engines that catch their own spec errors expose window.KF_ERROR (and window.KF_WARNINGS); both are read here
    let ready = false, kfErr = null; while ((Date.now() - t0) / 1000 < o.timeout) { [ready, kfErr] = await page.evaluate(() => [window.KF_READY === true, window.KF_ERROR ? String(window.KF_ERROR.message || window.KF_ERROR) : null]).catch(() => [false, null]);
      if (ready || kfErr || report.page_errors.length) break; await page.waitForTimeout(250); }
    if (kfErr) report.hard.push('spec error: ' + kfErr.slice(0, 400));
    if (!ready && !kfErr && !report.page_errors.length) report.hard.push(`the film did not get ready in ${o.timeout} s`);
    const kfWarn = await page.evaluate(() => (window.KF_WARNINGS || []).map(String)).catch(() => []); for (const w of kfWarn) report.soft.push('engine warning: ' + w.slice(0, 300));
    report.ready_s = +((Date.now() - t0) / 1000).toFixed(1);
    // 2. lint (in the page: the engine's own modules resolve the time refs)
    if (L.lint) {
      const lr = await page.evaluate(async ({ lint, spec, film }) => { try { const m = await import('/' + lint); const s = (await import(new URL(spec, location.origin + '/' + film + '/').href + '?lint')).default;
        const c = await (await fetch('/' + film + '/cues.json')).json(); return m.lint(s, c); } catch (e) { return { errors: ['lint could not load the spec: ' + (e.message || e)], warnings: [] }; } }, { lint: L.lint, spec: o.spec, film: filmRel });
      report.lint = { errors: uniq(lr.errors), warnings: uniq(lr.warnings) };
    }
    // 3. stills
    if (ready) {
      const times = stillTimes(); const fps = filmJson.fps || 24; let tot = 0;
      for (const st of times) { const i = Math.round(st.t * fps), t = i / fps; const s0 = Date.now(); const rec = { t: +t.toFixed(2), why: st.why, line: (lineAt(t) || {}).id || null };
        try {
          const r = await page.evaluate(async ({ i, t }) => { window.__kfText = []; window.__kfRec = true; try { await KF.render(i, t); } finally { window.__kfRec = false; }
            const c = document.createElement('canvas'); c.width = 64; c.height = 36; const g = c.getContext('2d'); g.drawImage(KF.canvas, 0, 0, 64, 36); const d = g.getImageData(0, 0, 64, 36).data;
            let s = 0, s2 = 0; const n = d.length / 4; for (let k = 0; k < d.length; k += 4) { const y = 0.2126 * d[k] + 0.7152 * d[k + 1] + 0.0722 * d[k + 2]; s += y; s2 += y * y; }
            const mean = s / n; return { url: KF.canvas.toDataURL('image/jpeg', 0.85), mean, std: Math.sqrt(Math.max(0, s2 / n - mean * mean)), text: window.__kfText }; }, { i, t });
          const file = path.join(out, 'stills', `t${String(Math.round(t * 100)).padStart(6, '0')}.jpg`); fs.writeFileSync(file, Buffer.from(r.url.slice(r.url.indexOf(',') + 1), 'base64'));
          Object.assign(rec, { file: path.relative(out, file), mean: +r.mean.toFixed(1), std: +r.std.toFixed(1) });
          if (r.std < 3.5) report.hard.push(`blank frame at ${t.toFixed(2)} s (${st.why}): flat ${r.mean < 40 ? 'dark' : 'colour'} image, nothing drawn`);
          // text checks: visible text only, the same string drawn twice (outline + fill) counts once
          const vis = []; for (const x of r.text) if (x.a > 0.6 && !vis.some((v) => v.text === x.text && Math.abs(v.x0 - x.x0) < 3 && Math.abs(v.y0 - x.y0) < 3)) vis.push(x);
          rec.texts = vis.map((x) => x.text);
          for (const x of vis) { const m = 0.01 * W; if (x.x0 < -m || x.x1 > W + m || x.y0 < -m || x.y1 > H + m) report.soft.push(`text off screen at ${t.toFixed(2)} s (${rec.line || st.why}): "${x.text}"`); }
          for (let p = 0; p < vis.length; p++) for (let q = p + 1; q < vis.length; q++) { const A = vis[p], B = vis[q]; if (A.text === B.text) continue;
            const ix = Math.max(0, Math.min(A.x1, B.x1) - Math.max(A.x0, B.x0)), iy = Math.max(0, Math.min(A.y1, B.y1) - Math.max(A.y0, B.y0));
            const small = Math.min((A.x1 - A.x0) * (A.y1 - A.y0), (B.x1 - B.x0) * (B.y1 - B.y0)); if (small > 0 && ix * iy > 0.25 * small) report.soft.push(`overlapping text at ${t.toFixed(2)} s (${rec.line || st.why}): "${A.text}" and "${B.text}"`); }
        } catch (e) { rec.error = String(e.message || e).split('\n')[0].slice(0, 300); report.hard.push(`render error at ${t.toFixed(2)} s (${st.why}): ${rec.error}`); }
        const dt = (Date.now() - s0) / 1000; tot += dt; rec.s = +dt.toFixed(2); report.stills.push(rec); }
      report.still_s = report.stills.length ? +(tot / report.stills.length).toFixed(2) : null;
    }
    // 4. contact sheet: still + time + narration line
    const shown = report.stills.filter((s) => s.file);
    if (shown.length) {
      const cols = 4, tw = 330, th = Math.round(tw * H / W); const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
      const cells = shown.map((s) => { const ln = cues.lines.find((l) => l.id === s.line); const img = fs.readFileSync(path.join(out, s.file)).toString('base64');
        return `<div class="c"><img src="data:image/jpeg;base64,${img}"><div class="t"><b>${s.t.toFixed(1)} s ${esc(s.line || '')}</b> ${esc(s.why && s.why !== s.line ? '[' + s.why + '] ' : '')}${esc(ln ? ln.text : '(no narration)')}</div></div>`; }).join('');
      const html = `<html><head><style>body{margin:0;background:#15110d;font:12px/1.3 Arial,sans-serif;color:#eee}.g{display:grid;grid-template-columns:repeat(${cols},${tw}px);gap:8px;padding:8px}
        .c img{width:${tw}px;height:${th}px;display:block}.t{padding:3px 2px 0;height:${Math.round(13 * 1.3 * 4)}px;overflow:hidden}h1{font-size:14px;margin:8px 8px 0}</style></head>
        <body><h1>${esc(filmJson.title || filmRel)}: ${esc(o.spec)}</h1><div class="g">${cells}</div></body></html>`;
      const sp = await browser.newPage({ viewport: { width: cols * (tw + 8) + 8, height: 400 }, deviceScaleFactor: 1 }); await sp.setContent(html, { waitUntil: 'load' });
      await sp.screenshot({ path: path.join(out, 'sheet.jpg'), fullPage: true, type: 'jpeg', quality: 78 }); await sp.close(); report.sheet = 'sheet.jpg';
    }
  } finally { await browser.close(); server.close(); }
  for (const e of uniq(report.page_errors)) report.hard.push('page error: ' + e);
  for (const e of uniq(report.console_errors)) report.hard.push('console error: ' + e);
  for (const e of report.lint.errors) report.hard.push('lint: ' + e);
  for (const w of report.lint.warnings) report.soft.push('lint warning: ' + w);
  report.hard = uniq(report.hard); report.soft = uniq(report.soft).slice(0, 40); report.ok = report.hard.length === 0; save();
  console.log(JSON.stringify({ ok: report.ok, hard: report.hard.length, soft: report.soft.length, stills: report.stills.length, ready_s: report.ready_s, still_s: report.still_s, out: path.relative(ROOT, out) }));
})().catch((e) => { console.error(e); report.hard.push('checker crashed: ' + String(e.message || e).slice(0, 300)); save(); process.exit(2); });
