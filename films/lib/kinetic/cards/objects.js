// Kinetic cards made of objects: stamp (a stamped word over a document) and drawer (an archive drawer and file reveal).
import { clamp, lerp, ease, rgba, keys, withScale, smoothstep, rng, measure, fitSize, FONTS, mk } from '../lib.js';
import { parseItems, buildBlock } from '../blocks.js';
import { SLAM } from '../engine.js';

const DOCINK = '#14171a';

// ---------------------------------------------------------------- stamp
// card: { word, on?, doc?: { header, date, lines[] } , angle?, accent?, at?: [fx, fy], frame?: true }
export function stamp(E, c, ctx) {
  const { W, H, U } = E, th = ctx.theme, doc = c.doc, onDark = th.dark;
  const items = [];
  if (doc) {
    if (doc.header) items.push({ kind: 'typed', txt: String(doc.header).toUpperCase(), cap: 0.0165, ls: 0.22, on: ctx.t0 + 0.2 }, { kind: 'rule' });
    if (doc.date) items.push({ kind: 'gap', h: 0.02 }, { kind: 'stamp', txt: String(doc.date).toUpperCase(), maxCap: 0.06, on: doc.dateOn });
    const lines = (Array.isArray(doc.lines) ? doc.lines : doc.lines ? [doc.lines] : []).map((l) => (/^(!!|!|\+|\^|~|#|==|_)/.test(l) ? l : '~' + l));
    if (lines.length) items.push({ kind: 'gap', h: 0.02 });
    for (const it of parseItems(lines, { emph: 'none' })) items.push(it.kind === 'typed' ? { ...it, txt: String(it.txt).toUpperCase(), cap: 0.0185 } : it);
  }
  const docCtx = { ...ctx, theme: { ...th, ink: c.sheet === false ? th.ink : DOCINK, dark: c.sheet === false ? th.dark : false } };
  const B = items.length ? buildBlock(E, docCtx, items, { pos: 0.205, gap: 0.02, color: c.sheet === false ? undefined : DOCINK, emph: 'none' }) : null;
  const sx0 = E.AX - 0.035 * W, sx1 = E.AX + E.MEAS + 0.035 * W, sy0 = 0.165 * H, sy1 = Math.max(0.58, B ? B.bottom + 0.2 : 0.58) * H;
  const tin = ctx.t0;
  const word = String(c.word).toUpperCase(), wl = word.split(' ');
  const auto = ctx.clock.match(wl, ctx.t0);
  const tStamp = ctx.snap(c.on != null ? ctx.at(c.on) : (auto ? auto[0] : ctx.t0 + 0.9));
  const angle = (c.angle ?? -6) * Math.PI / 180;
  const col = c.accent ? th.accent : (c.color || (c.sheet === false ? th.ink : DOCINK));
  const size = fitSize(FONTS.B, word, 0.05, (c.fit ?? 0.8) * E.MEAS), capPx = measure(FONTS.B(size), 'H', 0).asc;
  const szc = Math.min(size, 0.11 * H * size / capPx), cap2 = measure(FONTS.B(szc), 'H', 0).asc;
  const at = c.place || [0.445, B ? B.bottom + 0.085 : sy1 / H - 0.115];
  const R = rng(55 + word.length);
  const bars = Array.from({ length: 9 }, () => 0.45 + 0.55 * R());
  const draw = (E) => {
    const t = E.t, g = E.g, ink = E.ink, p = ease.outCubic(clamp((t - tin) / 0.3)), dy = (1 - p) * 0.05 * H;
    g.save(); g.translate(0, dy); g.globalAlpha = p;
    g.save(); g.translate((sx0 + sx1) / 2, (sy0 + sy1) / 2); g.rotate(-0.012); g.translate(-(sx0 + sx1) / 2, -(sy0 + sy1) / 2);
    if (c.sheet !== false) {
    g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = onDark ? 26 * U : 8 * U; g.shadowOffsetY = 8 * U; g.fillStyle = '#e4e7e6'; g.fillRect(sx0, sy0, sx1 - sx0, sy1 - sy0); g.shadowColor = 'rgba(0,0,0,0)';
    g.fillStyle = 'rgba(60,76,86,0.07)'; g.fillRect(sx0, sy0, sx1 - sx0, 3 * U); }
    if (c.sheet !== false && (!B || !doc.lines)) {                                       // placeholder rules where the real text would be
      g.fillStyle = 'rgba(20,23,26,0.13)'; const y0 = (B ? B.bottom + 0.02 : 0.25) * H;
      for (let k = 0; y0 + k * 0.034 * H < sy1 - 0.04 * H; k++) g.fillRect(E.AX, y0 + k * 0.034 * H, E.MEAS * bars[k % bars.length], 0.0085 * H);
    }
    g.restore(); g.restore();
    ink.save(); ink.translate(0, dy); ink.globalAlpha = p; ink.translate((sx0 + sx1) / 2, (sy0 + sy1) / 2); ink.rotate(-0.012); ink.translate(-(sx0 + sx1) / 2, -(sy0 + sy1) / 2);
    if (B) B.draw(E); ink.restore();
    if (t >= tStamp) {
      const f = E.f - Math.ceil(tStamp * 24 - 1e-6); if (f < 0) return;
      const cx = at[0] * W, cy = at[1] * H, pad = 0.02 * H;
      const wd = measure(FONTS.B(szc), word, 0.05 * szc).adv, bw = wd + 2 * pad + 0.02 * H, bh = cap2 + 2 * pad;
      const sc = keys(f, [[0, 1.4], [1, 1.14], [2, 1.0], [3, 0.97], [4, 1.0]]);
      const a = Math.min(1, 0.35 + 0.35 * f), settled = f >= 3;
      ink.save(); ink.translate(cx, cy); ink.rotate(angle); ink.scale(sc, sc);
      ink.globalAlpha = a * 0.92; ink.strokeStyle = col; ink.fillStyle = col; ink.lineJoin = 'miter';
      if (c.frame !== false) { ink.lineWidth = 0.008 * H; ink.strokeRect(-bw / 2, -bh / 2, bw, bh); ink.lineWidth = 0.0028 * H; ink.strokeRect(-bw / 2 - 0.011 * H, -bh / 2 - 0.011 * H, bw + 0.022 * H, bh + 0.022 * H); }
      ink.font = FONTS.B(szc); ink.letterSpacing = 0.05 * szc + 'px'; ink.textBaseline = 'alphabetic'; ink.textAlign = 'center'; ink.fillText(word, 0.025 * szc, cap2 / 2);
      ink.restore();
    }
  };
  return { draw, hits: [[tStamp, 12, 7, 0.06]], lastT: tStamp };
}

// ---------------------------------------------------------------- drawer
// card: { label, folder?, strip?: [typed lines], text?, start?: 'closed'|'open', openAt?, dropAt?, closeAt?, push?, dust? }
export function drawer(E, c, ctx) {
  const { W, H, U } = E, th = ctx.theme;
  const DR = { x0: 0.07 * W, x1: 0.93 * W, y0: 0.44 * H, y1: 0.82 * H }, FO = { x0: 0.13 * W, x1: 0.87 * W, y0: 0.485 * H, y1: 0.775 * H };
  const motes = (() => { const r = rng(606), a = []; for (let k = 0; k < 46; k++) a.push({ x: r(), y: r(), s: 0.004 + 0.01 * r(), z: 0.6 + 1.8 * r(), p: r() * 6.28 }); return a; })();
  const label = String(c.label || '').toUpperCase(), folder = String(c.folder || c.label || '').toUpperCase();
  const events = [];
  const startOpen = c.start === 'open' || (!c.openAt && c.start == null && !!c.dropAt);
  if (c.openAt != null) events.push({ t: ctx.at(c.openAt), to: 1, dur: c.openDur ?? 0.5, e: ease.outCubic });
  if (c.closeAt != null) events.push({ t: ctx.at(c.closeAt), to: 0, dur: c.closeDur ?? 0.5, e: ease.inQuad });
  events.sort((a, b) => a.t - b.t);
  const tDrop = c.dropAt != null ? ctx.at(c.dropAt) : null, tOpen = c.openAt != null ? ctx.at(c.openAt) : null;
  const openOf = (t) => { let cur = startOpen ? 1 : 0; for (const ev of events) { if (t >= ev.t + ev.dur) cur = ev.to; else if (t >= ev.t) return lerp(cur, ev.to, ev.e(clamp((t - ev.t) / ev.dur))); else break; } return cur; };
  const B = c.text ? buildBlock(E, ctx, c.text, { pos: c.pos ?? 'top', emph: c.emph, accent: c.accent, align: c.align }) : null;
  const strip = c.strip === false ? null : (c.strip || []);
  const dur = Math.max(1, ctx.t1 - ctx.t0);
  function drawStrip(g, cx, cy, w, rot, alpha) {
    const h = w * 0.36; g.save(); g.translate(cx, cy); g.rotate(rot); g.globalAlpha = alpha; g.shadowColor = 'rgba(0,0,0,0.65)'; g.shadowBlur = 20 * U; g.shadowOffsetY = 7 * U; g.fillStyle = '#e9e1cb'; g.fillRect(-w / 2, -h / 2, w, h); g.shadowColor = 'rgba(0,0,0,0)';
    g.fillStyle = 'rgba(70,48,24,0.22)'; g.fillRect(-w / 2, -h / 2, w, 2 * U); g.fillRect(-w / 2, h / 2 - 2 * U, w, 2 * U); g.fillRect(-w / 2, -h / 2, 2 * U, h); g.fillRect(w / 2 - 2 * U, -h / 2, 2 * U, h);
    g.fillStyle = '#2a241c'; g.font = `400 ${0.0175 * H}px "Special Elite"`; g.letterSpacing = (0.06 * 0.0175 * H) + 'px'; g.textBaseline = 'alphabetic';
    if (strip.length) strip.slice(0, 5).forEach((s, i) => g.fillText(String(s).toUpperCase(), -w / 2 + 0.05 * w, -h / 2 + 0.17 * h + i * 0.045 * H)); else { g.fillStyle = 'rgba(42,36,28,0.2)'; for (let k = 0; k < 4; k++) g.fillRect(-w / 2 + 0.07 * w, -h / 2 + 0.2 * h + k * 0.2 * h, w * (0.8 - 0.1 * (k % 2)), 0.006 * H); }
    g.restore();
  }
  const draw = (E) => {
    const t = E.t, g = E.g, open = openOf(t), cx = W / 2, cyy = 0.63 * H, push = (c.push ?? 0.05) * clamp((t - ctx.t0) / dur);
    if (B) { const gr = g.createLinearGradient(0, 0, 0, 0.42 * H); gr.addColorStop(0, 'rgba(14,13,11,0.8)'); gr.addColorStop(0.8, 'rgba(14,13,11,0.65)'); gr.addColorStop(1, 'rgba(14,13,11,0)'); }
    g.save(); g.translate(cx, cyy); g.scale(1 + push, 1 + push); g.translate(-cx, -cyy);
    const rim = 15 * U;
    let gr = g.createLinearGradient(0, DR.y0 - rim, 0, DR.y1 + rim); gr.addColorStop(0, '#34373a'); gr.addColorStop(1, '#17181a'); g.fillStyle = gr; g.fillRect(DR.x0 - rim, DR.y0 - rim, DR.x1 - DR.x0 + 2 * rim, DR.y1 - DR.y0 + 2 * rim);
    g.fillStyle = 'rgba(255,255,255,0.10)'; g.fillRect(DR.x0 - rim, DR.y0 - rim, DR.x1 - DR.x0 + 2 * rim, 2 * U);
    g.fillStyle = '#080707'; g.fillRect(DR.x0, DR.y0, DR.x1 - DR.x0, DR.y1 - DR.y0);
    gr = g.createLinearGradient(0, DR.y0, 0, DR.y0 + 40 * U); gr.addColorStop(0, 'rgba(0,0,0,0.8)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(DR.x0, DR.y0, DR.x1 - DR.x0, 40 * U);
    const ly0 = DR.y1 + rim, ly1 = ly0 + 0.10 * H;
    gr = g.createLinearGradient(0, ly0, 0, ly1); gr.addColorStop(0, '#2b2d30'); gr.addColorStop(1, '#141516'); g.fillStyle = gr; g.fillRect(DR.x0 - rim, ly0, DR.x1 - DR.x0 + 2 * rim, ly1 - ly0);
    g.fillStyle = 'rgba(255,255,255,0.08)'; g.fillRect(DR.x0 - rim, ly0, DR.x1 - DR.x0 + 2 * rim, 2 * U);
    const pw = 0.30 * W, ph = 0.034 * H; g.fillStyle = '#c9ced0'; g.fillRect(cx - pw / 2, ly0 + 0.022 * H, pw, ph);
    g.fillStyle = '#14171a'; g.font = `400 ${0.0145 * H}px "Special Elite"`; g.letterSpacing = (0.12 * 0.0145 * H) + 'px'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(label, cx, ly0 + 0.022 * H + ph / 2 + 1 * U); g.textAlign = 'left'; g.letterSpacing = '0px';
    g.fillStyle = '#0c0d0e'; g.fillRect(cx - 0.10 * W, ly0 + 0.066 * H, 0.20 * W, 0.012 * H); g.fillStyle = 'rgba(255,255,255,0.14)'; g.fillRect(cx - 0.10 * W, ly0 + 0.066 * H, 0.20 * W, 1.5 * U);
    g.save(); g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = 16 * U; g.shadowOffsetY = 5 * U; g.fillStyle = '#b9bfc1'; g.fillRect(FO.x0, FO.y0, FO.x1 - FO.x0, FO.y1 - FO.y0); g.restore();
    g.fillStyle = '#bcc2c4'; g.fillRect(FO.x0 - 1 * U, FO.y0 - 0.014 * H, 0.22 * W, 0.016 * H);
    const cyS = (FO.y0 + FO.y1) / 2, stripShown = startOpen || tOpen != null || tDrop != null;
    if (strip && stripShown) {
      let y = cyS, a = 1;
      if (tDrop != null) { const pD = ease.inOutCubic(clamp((t - tDrop) / 0.7)); y = lerp(0.745 * H, cyS, pD); a = clamp((t - ctx.t0) / 0.2); }
      drawStrip(g, (FO.x0 + FO.x1) / 2, y, 0.64 * W, -0.012, a);
    }
    const glow = smoothstep(0, 1, open) * (0.9 + 0.1 * Math.sin(t * 2.1));
    if (glow > 0) { const gg = g.createRadialGradient(cx, cyS, 10, cx, cyS, 0.55 * W); gg.addColorStop(0, `rgba(255,214,150,${0.28 * glow})`); gg.addColorStop(1, 'rgba(255,214,150,0)'); g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = gg; g.fillRect(DR.x0, DR.y0 - 60 * U, DR.x1 - DR.x0, DR.y1 - DR.y0 + 120 * U); g.restore(); }
    const th2 = Math.PI * (1 - clamp(open)), cc = Math.cos(th2), cw = FO.x1 - FO.x0;
    if (open < 0.999) {
      g.save(); g.translate(FO.x0, 0); g.scale(Math.abs(cc) < 1e-3 ? 1e-3 : cc, 1);
      g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 14 * U; g.fillStyle = cc >= 0 ? '#cdd2d3' : '#a9b0b2'; g.fillRect(0, FO.y0, cw, FO.y1 - FO.y0); g.shadowColor = 'rgba(0,0,0,0)';
      g.fillStyle = `rgba(0,0,0,${0.35 * (1 - Math.abs(cc))})`; g.fillRect(0, FO.y0, cw, FO.y1 - FO.y0);
      g.fillStyle = '#2a2f33'; g.font = `400 ${0.0175 * H}px "Special Elite"`; g.letterSpacing = (0.12 * 0.0175 * H) + 'px'; g.textBaseline = 'alphabetic'; g.fillText(folder, 0.05 * cw, FO.y0 + 0.04 * H); g.fillRect(0.05 * cw, FO.y0 + 0.05 * H, 0.5 * cw, 2 * U); g.letterSpacing = '0px';
      g.restore();
    }
    if ((c.dust ?? 1) > 0) { g.save(); for (const m of motes) { const yy = DR.y0 + ((m.y + t * m.s) % 1) * (DR.y1 - DR.y0), xx = DR.x0 + m.x * (DR.x1 - DR.x0) + 14 * U * Math.sin(t * 0.5 + m.p); g.fillStyle = `rgba(255,236,200,${0.30 * (c.dust ?? 1) * (0.5 + 0.5 * Math.sin(t * 1.3 + m.p))})`; g.beginPath(); g.arc(xx, yy, m.z * U, 0, 6.2832); g.fill(); } g.restore(); }
    g.restore();
    if (B) B.draw(E);
  };
  const hits = [];
  if (tOpen != null) hits.push([tOpen + 0.1, 6, 5, 0.04]);
  for (const ev of events) if (ev.to === 0) hits.push([ev.t + ev.dur, 10, 7, 0.06]);
  return { draw, hits: [...hits, ...(B ? B.hits : [])], lastT: Math.max(ctx.t0, B ? B.lastT : 0, ...events.map((e) => e.t)) };
}
