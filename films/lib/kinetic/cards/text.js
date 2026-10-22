// Kinetic cards made of type: statement, slam, record, strike, list, count, title, end.
// Each build(E, card, ctx) returns { draw(E, lt), hits: [[t, amp, len, kick]], lastT }.
import { clamp, lerp, ease, rgba, keys, withScale, measure, FONTS, fitSize, wrapMeasure } from '../lib.js';
import { parseItems, buildBlock } from '../blocks.js';
import { SLAM } from '../engine.js';

const opts = (c) => ({ pos: c.pos, align: c.align, emph: c.emph, gap: c.gap, accent: c.accent, wrap: c.wrap, color: c.color, x: c.x, cx: c.cx });
const merge = (...bs) => ({ hits: bs.flatMap((b) => b.hits), lastT: Math.max(...bs.map((b) => b.lastT)), firstT: Math.min(...bs.map((b) => b.firstT ?? 1e9)) });

// ---------------------------------------------------------------- statement: lines landing word by word
export function statement(E, c, ctx) {
  const B = buildBlock(E, ctx, c.lines ?? c.text, opts(c));
  const decos = (c.deco ? (Array.isArray(c.deco) ? c.deco : [c.deco]) : []).map((d) => ({ ...d, t: d.on != null ? ctx.at(d.on) : ctx.t0 + 0.2 }));
  const draw = (E) => { for (const d of decos) drawDeco(E, d, ctx); B.draw(E); };
  return { draw, hits: B.hits, lastT: B.lastT, block: B };
}
// small decorations (objects, never pictures of people): rope | bars
function drawDeco(E, d, ctx) {
  const { W, H, U } = E, t = E.t; if (t < d.t) return; const I = E.ink, col = d.color || ctx.theme.ink;
  if (d.kind === 'rope') {                                       // a twisted rope that draws down from the top edge; optional knot at the end
    const x = (d.x ?? 0.84) * W, len = (d.len ?? 0.42) * H, p = ease.outCubic(clamp((t - d.t) / (d.dur ?? 0.6))), yEnd = -0.02 * H + (len + 0.02 * H) * p;
    I.save(); I.strokeStyle = col; I.lineCap = 'round'; I.lineWidth = 7 * U; I.beginPath(); I.moveTo(x, -0.02 * H); I.lineTo(x, yEnd); I.stroke();
    I.globalCompositeOperation = 'destination-out'; I.lineWidth = 2.2 * U; for (let y = -0.02 * H; y < yEnd; y += 9 * U) { I.beginPath(); I.moveTo(x - 4 * U, y + 4 * U); I.lineTo(x + 4 * U, y - 2 * U); I.stroke(); }
    I.globalCompositeOperation = 'source-over'; I.fillStyle = col; I.beginPath(); I.arc(x, yEnd + 3 * U, 6 * U, 0, 6.2832); I.fill(); I.restore();
  } else if (d.kind === 'bars') {                                // seven hairlines that draw down from the top edge
    for (let k = 0; k < 7; k++) { const x = (0.13 + k * 0.12) * W, p = ease.outCubic(clamp((t - d.t - k * 0.04) / 0.25)); if (p > 0) { I.fillStyle = rgba(col, 0.16); I.fillRect(x, 0, Math.max(2, 3 * U), H * p); } }
  }
}

// ---------------------------------------------------------------- slam: a big date or number that slams on a word, with a dateline
export function slam(E, c, ctx) {
  const ticks = Array.isArray(c.text) ? c.text : [{ text: c.text, on: c.on }];
  const mk = (tk, first) => {
    const items = [];
    if (c.kicker) items.push({ kind: 'kicker', txt: String(c.kicker).toUpperCase() });
    items.push({ kind: 'stamp', txt: String(tk.text), on: tk.on ?? c.on, maxCap: c.cap, accent: !!c.accent && c.accent !== 'dateline' });
    if (c.rule !== false) items.push({ kind: 'rule' });
    if (c.dateline) items.push({ kind: 'typed', txt: String(c.dateline).toUpperCase(), cap: 0.02, ls: 0.1, nowrap: true, on: c.datelineOn });
    if (c.lines || c.sub) { items.push({ kind: 'gap', h: 0.035 }); for (const it of parseItems(c.lines ?? c.sub, { emph: c.emph, wrap: c.wrap })) items.push(it); }
    return buildBlock(E, ctx, items, { pos: c.pos ?? 'upper', align: c.align, gap: c.gap, color: c.color, x: c.x, cx: c.cx });
  };
  const Bs = ticks.map((tk, i) => ({ B: mk(tk, i === 0), t: ctx.at(tk.on ?? c.on ?? ctx.t0) }));
  // for date ticks the earlier stamps are replaced; only the active one draws, the rest (kicker, dateline, lines) are identical
  const draw = (E) => {                                                  // date ticks: only the latest stamp that has landed draws
    let best = 0; for (let i = 0; i < Bs.length; i++) if (E.t >= Bs[i].B.lines.find((s) => s.kind === 'stamp').times[0] - 1e-6) best = i;
    Bs[best].B.draw(E);
  };
  return { draw, hits: Bs.flatMap((x) => x.B.hits), lastT: Math.max(...Bs.map((x) => x.B.lastT)) };
}

// ---------------------------------------------------------------- record: a cold typed document
export function record(E, c, ctx) {
  const items = [];
  if (c.header) items.push({ kind: 'typed', txt: String(c.header).toUpperCase(), cap: 0.0185, ls: 0.22, on: ctx.t0 + 0.05 }, { kind: 'rule' });
  if (c.date) items.push({ kind: 'gap', h: 0.03 }, { kind: 'stamp', txt: String(c.date).toUpperCase(), on: c.dateOn, maxCap: 0.085, align: 'left', accent: c.accent === 'date' });
  const lines = (Array.isArray(c.lines) ? c.lines : c.lines ? [c.lines] : (c.text ? [c.text] : [])).map((l) => (typeof l === 'string' && !/^(!!|!|\+|\^|~|#|==|_)/.test(l) ? '~' + l : l));
  if (lines.length) items.push({ kind: 'gap', h: 0.03 });
  for (const it of parseItems(lines, { emph: 'none' })) items.push(it.kind === 'typed' ? { ...it, txt: String(it.txt).toUpperCase() } : it);
  const B = buildBlock(E, ctx, items, { pos: c.pos ?? 'top', gap: c.gap ?? 0.02, color: c.color, accent: c.accent === true ? true : undefined, emph: 'none' });
  return { draw: (E) => B.draw(E), hits: B.hits, lastT: B.lastT, block: B };
}

// ---------------------------------------------------------------- strike: text that is struck through, then contradicted
export function strike(E, c, ctx) {
  const A = buildBlock(E, ctx, c.text, { ...opts(c), emph: c.emph ?? 'none', pos: c.pos ?? 'upper', accent: undefined });
  const tStrike = ctx.at(c.strikeOn ?? c.on ?? (A.lastT + 0.9));
  const thenSrc = c.then ?? c.lines;
  const B = thenSrc ? buildBlock(E, { ...ctx, from: tStrike - 0.1 }, thenSrc, { pos: Math.min(0.55, A.bottom + 0.06), align: c.align, emph: c.emph, accent: c.accent, color: c.color2 }) : null;
  const dark = ctx.theme.dark, barCol = c.bar === 'accent' ? ctx.theme.accent : (dark ? ctx.theme.ink : ctx.theme.ink);
  const draw = (E) => {
    const t = E.t, k = clamp((t - tStrike) / 0.25);
    A.draw(E, { alpha: 1 - 0.55 * ease.outCubic(k) });
    if (t >= tStrike) {
      let n = 0;
      for (const s of A.lines) {
        if (s.rule || s.kind === 'kicker' || s.txt == null) continue;
        const G = E.geo(s), p = ease.outCubic(clamp((t - tStrike - n * 0.07) / 0.22)); n++;
        const y = G.base - G.cap * 0.5, th = dark ? Math.max(2, 0.0035 * E.H) : 0.022 * E.H;
        E.ink.fillStyle = barCol; E.ink.fillRect(G.inkL - 6 * E.U, y - th / 2, (G.inkW + 12 * E.U) * p, th);
      }
    }
    if (B) B.draw(E);
  };
  const hits = [[tStrike + 0.05, 7, 5, 0.03], ...(B ? B.hits : [])];
  return { draw, hits, lastT: Math.max(tStrike, B ? B.lastT : 0) };
}

// ---------------------------------------------------------------- list: items appearing in turn
export function list(E, c, ctx) {
  const items = [];
  if (c.title) items.push({ kind: c.titleKind || 'kicker', txt: String(c.title).toUpperCase(), on: ctx.t0 + 0.1 }, { kind: 'gap', h: 0.03 });
  const mark = c.marker || 'num';
  const srcItems = (c.items || []).map((it) => (typeof it === 'string' ? { txt: it } : it));
  const ind = srcItems.every((it) => (it.mark || mark) === 'none') ? 0 : 0.085 * E.W;
  const ons = Array.isArray(c.on) ? c.on : [];
  let n = 0;
  srcItems.forEach((it, i) => {
    const txt = String(it.txt ?? it.text).toUpperCase();
    // wrap long items into several lines (each its own spec, the first carries the marker)
    const parts = txt.length > 20 ? txt.split(/\s+/).reduce((a, w) => { const cur = a[a.length - 1]; if (cur && (cur + ' ' + w).length <= 20) a[a.length - 1] = cur + ' ' + w; else a.push(w); return a; }, []) : [txt];
    parts.forEach((p, j) => items.push({ kind: 'body', txt: p, x: (E.AX + ind) / E.W, fit: (E.MEAS - ind) / E.MEAS, maxCap: c.cap ?? 0.048, ls: 0.04, item: i, first: j === 0, mark: it.mark || mark, on: j === 0 ? (it.on ?? ons[i]) : undefined, accent: !!it.accent }));
    n++;
  });
  // x passed as fraction: blocks multiplies by W only for o.x; here the spec carries pixels via geo, so convert below
  const B = buildBlock(E, ctx, items.map((it) => (it.item != null ? { ...it, x: E.AX + ind } : it)), { pos: c.pos ?? 'upper', gap: c.gap ?? 0.026, emph: 'none', color: c.color });
  const draw = (E) => {
    B.draw(E);
    const th = ctx.theme;
    for (const s of B.lines) {
      if (s.rule || s.item == null || !s.first || s.mark === 'none') continue;
      const t0 = s.times[0], p = ease.outCubic(clamp((E.t - t0) / 0.25)); if (p <= 0) continue;
      const G = E.geo(s), cy = G.base - G.cap / 2, x = E.AX + 0.018 * E.W, g = E.ink, col = s.accent ? th.accent : th.ink;
      g.save(); g.globalAlpha = p; g.strokeStyle = col; g.fillStyle = col; g.lineWidth = Math.max(2, 0.0026 * E.H); g.lineCap = 'round'; g.lineJoin = 'round';
      const r = 0.012 * E.H;
      if (s.mark === 'dot') { g.beginPath(); g.arc(x, cy, r * 0.55, 0, 6.2832); g.fill(); }
      else if (s.mark === 'tick') { g.beginPath(); g.moveTo(x - r, cy); g.lineTo(x - r * 0.25, cy + r * 0.8); g.lineTo(x + r * 1.1, cy - r * 0.9); g.stroke(); }
      else if (s.mark === 'cross') { const q = r * 0.85; g.beginPath(); g.moveTo(x - q, cy - q); g.lineTo(x + q, cy + q); g.moveTo(x + q, cy - q); g.lineTo(x - q, cy + q); g.stroke(); }
      else { g.font = `400 ${0.021 * E.H}px "Bebas Neue"`; g.letterSpacing = (0.12 * 0.021 * E.H) + 'px'; g.textBaseline = 'middle'; g.fillText(String(s.item + 1).padStart(2, '0'), E.AX, cy + 1 * E.U); }
      g.restore();
    }
  };
  return { draw, hits: B.hits, lastT: B.lastT };
}

// ---------------------------------------------------------------- count: a number counting up, with a label
export function count(E, c, ctx) {
  const from = c.from ?? 0, to = +c.to, dec = c.decimals ?? 0, W = E.W, H = E.H, U = E.U;
  const tStart = ctx.at(c.on ?? (ctx.t0 + 0.15));
  const tEnd = c.settle != null ? ctx.at(c.settle) : tStart + (c.dur ?? 1.5);
  const fmt = (v) => { const s = (dec ? v.toFixed(dec) : String(Math.round(v))); const [a, b] = s.split('.'); const w = c.commas === false ? a : a.replace(/\B(?=(\d{3})+(?!\d))/g, ','); return (c.prefix || '') + w + (b ? '.' + b : '') + (c.suffix || ''); };
  const final = fmt(to), fk = FONTS.B;
  const size = fitSize(fk, final.replace(/\d/g, '0'), 0.01, 0.985 * E.MEAS * (c.fit ?? 1)), cap = measure(fk(size), 'H', 0).asc;
  const capMax = (c.cap ?? 0.15) * H, sz = Math.min(size, capMax * size / cap), capPx = measure(fk(sz), 'H', 0).asc;
  const ls = 0.01 * sz, font = fk(sz), dw = measure(font, '0', ls).adv;
  const widthOf = (s) => [...s].reduce((a, ch) => a + (/\d/.test(ch) ? dw : measure(font, ch, ls).adv), 0), fw = widthOf(final);
  const base = (c.base ?? 0.37) * H;
  const x0 = (c.align === 'center' ? E.cx - fw / 2 : E.AX);
  const kick = c.kicker ? buildBlock(E, ctx, [{ kind: 'kicker', txt: String(c.kicker).toUpperCase() }], { pos: base / H - capPx / H - 0.05, emph: 'none', align: c.align }) : null;
  const lab = c.label ? buildBlock(E, { ...ctx, from: tEnd - 0.4 }, c.label, { pos: base / H + 0.035, emph: c.emph ?? 'none', align: c.align, accent: c.accent }) : null;
  const tl = Math.min(tEnd + 0.04, ctx.t1);
  const draw = (E) => {
    const t = E.t, k = clamp((t - tStart) / Math.max(0.1, tEnd - tStart)); if (t < tStart) return;
    const v = lerp(from, to, ease.outCubic(k)), s = fmt(v), ink = E.ink; let x = x0 + fw - widthOf(s);
    const f = E.f - Math.ceil(tEnd * 24 - 1e-6), sc = f >= 0 ? keys(f, SLAM) : 1;
    const a = clamp((t - tStart) / 0.12);
    withScale(ink, x0, base - capPx / 2, sc, () => {
      ink.save(); ink.font = font; ink.letterSpacing = ls + 'px'; ink.textAlign = 'left'; ink.textBaseline = 'alphabetic'; ink.fillStyle = c.accent === 'number' ? ctx.theme.accent : (c.color || ctx.theme.ink); ink.globalAlpha = a;
      for (const ch of s) { const w = /\d/.test(ch) ? dw : measure(font, ch, ls).adv; const off = /\d/.test(ch) ? (dw - measure(font, ch, ls).adv) / 2 : 0; ink.fillText(ch, x + off, base); x += w; }
      ink.restore();
    });
    if (kick) kick.draw(E); if (lab) lab.draw(E);
  };
  return { draw, hits: [[tEnd, 8, 6, 0.05], ...(lab ? lab.hits : [])], lastT: Math.max(tEnd, lab ? lab.lastT : 0) };
}

// ---------------------------------------------------------------- title and end: the series card
export function title(E, c, ctx) {
  const sp = ctx.spec, series = String(c.series ?? sp.series ?? '').toUpperCase(), ttl = c.title ?? sp.title ?? '';
  const t0 = ctx.snap(ctx.at(c.on ?? (ctx.t0 + 0.2)));
  const ink = ctx.theme.ink, items = [];
  const lines = Array.isArray(ttl) ? ttl : String(ttl).split(/\s+\/\s+/);
  const draw = (E) => {
    const t = E.t, a = c.fadeOut ? 1 - clamp((t - (ctx.t1 - c.fadeOut)) / c.fadeOut) : 1;
    let base = 0.40;
    let w = 0;
    if (series) {
      const T1 = E.line({ txt: series, font: 'B', fit: 1.0, ls: 0.06, base, times: t0, mode: 'stamp', smear: true, color: ink, alpha: a, maxCap: 0.13 });
      E.rule(E.AX, E.AX + T1.inkW, (base + 0.03) * E.H, t0 + 0.3, 0.3, Math.max(2, 0.0021 * E.H), rgba(ink, 0.5 * a), E.ink); w = T1.inkW; base += 0.105;
    }
    const ws = lines.join(' ').split(' '); let i = 0;
    lines.forEach((ln, li) => {
      const n = ln.split(' ').length, times = ln.split(' ').map((_, k) => t0 + 0.6 + (i + k) * 0.13); i += n;
      E.line({ txt: ln, font: 'C', fit: w ? w / E.MEAS : 1.0, maxCap: 0.05, ls: 0, base: base + li * 0.078, times, mode: 'pop', popDur: 0.4, color: ink, alpha: a });
    });
  };
  return { draw, hits: [[t0, 6, 5, 0.05]], lastT: t0 };
}
export const end = (E, c, ctx) => {
  const T = title(E, { ...c, fadeOut: c.fadeOut ?? 0.4 }, ctx);
  if (!c.line) return T;
  const B = buildBlock(E, ctx, c.line, { pos: 0.20, emph: c.emph ?? 'none', color: ctx.theme.ink, align: 'left' });
  return { draw: (E) => { B.draw(E); T.draw(E); }, hits: [...T.hits, ...B.hits], lastT: Math.max(T.lastT, B.lastT) };
};
