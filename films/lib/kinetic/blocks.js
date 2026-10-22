// Kinetic engine: text blocks. Parses the spec's text mini-language into lines, lays them out in the 9:16 safe zone, gives every
// word its landing time (explicit, or matched to the cue words, or spread), and returns a draw function + shake hits.
//
// Text mini-language (one string, parts separated by " / " or a newline; or an array of parts; or objects):
//   "PLAIN"        body line, auto-sized to the measure       "^SMALL"   kicker (small, tracked)
//   "+HEAVY"       heavier landing                             "!PAYOFF"  big payoff       "!!HUGE"   biggest
//   "#STAMP"       big smeared stamp (dates, numbers)          "~typed"   typed document line (wraps by itself)
//   "=="           a rule that draws across                    "_"        extra gap
// A single plain string with no " / " is wrapped into balanced lines automatically; the last short line becomes the payoff.
import { clamp, measure, wrapBalanced, wrapMeasure, FONTS, rgba, fitSize } from './lib.js';
import { fillGaps } from './timeline.js';
import { LAND, HEAVY, PAYOFF } from './engine.js';

const KIND = {
  kicker: { font: 'B', maxCap: 0.034, ls: 0.16, fit: 1.0 },
  body: { font: 'B', maxCap: 0.065, ls: 0.03, fit: 1.0 },
  heavy: { font: 'B', maxCap: 0.085, ls: 0.03, fit: 1.0, curve: HEAVY, amp: 4 },
  big: { font: 'B', maxCap: 0.115, ls: 0.035, fit: 1.0, curve: PAYOFF, amp: 6 },
  huge: { font: 'B', maxCap: 0.15, ls: 0.03, fit: 1.0, curve: PAYOFF, amp: 8 },
  stamp: { font: 'B', maxCap: 0.125, ls: 0.01, fit: 1.0, mode: 'stamp', smear: true, amp: 7 },
  typed: { font: 'T', mode: 'type', cap: 0.0225, ls: 0.06, perChar: 0.045 },
};
const MARK = [['!!', 'huge'], ['!', 'big'], ['+', 'heavy'], ['^', 'kicker'], ['~', 'typed'], ['#', 'stamp']];
const SAFE_Y0 = 0.15, SAFE_Y1 = 0.66;

// ---- parse: string | array | object -> items [{kind, txt, ...opts}]
export function parseItems(src, o = {}) {
  const arr = Array.isArray(src) ? src : (src == null ? [] : [src]); const items = []; let explicit = false;
  for (const a of arr) {
    if (a && typeof a === 'object') {
      if (a.rule || a.gap != null) { items.push({ kind: a.rule ? 'rule' : 'gap', h: a.gap, ...a }); continue; }
      const kind = a.kind || 'body', txt = a.txt ?? a.text; if (a.kind) explicit = true; items.push({ ...a, kind, txt }); continue;
    }
    const parts = String(a).split(/\s+\/\s+|\n/).map((s) => s.trim()).filter(Boolean);
    const manual = parts.length > 1;
    for (const p of parts) {
      if (p === '==') { items.push({ kind: 'rule' }); continue; }
      if (p === '_') { items.push({ kind: 'gap' }); continue; }
      let kind = 'body', txt = p, marked = false;
      for (const [m, k] of MARK) if (p.startsWith(m)) { kind = k; txt = p.slice(m.length).trim(); marked = true; break; }
      if (marked) explicit = true;
      if (!marked && !manual) { for (const w of wrapBalanced(txt, o.wrap || 17)) items.push({ kind, txt: w, auto: true }); }
      else items.push({ kind, txt, auto: false });
    }
  }
  // automatic emphasis: a lone short body line is a payoff; the last short line of a block becomes the payoff
  if (o.emph !== 'none' && !explicit) {
    const body = items.filter((i) => i.kind === 'body');
    if (body.length === 1 && body[0].txt.length <= 16) body[0].kind = 'big';
    else if (body.length >= 2 && items[items.length - 1].kind === 'body' && items[items.length - 1].txt.length <= 14) items[items.length - 1].kind = 'big';
  }
  return items;
}

const words = (txt) => String(txt).split(' ').filter((w) => w.length);

// ---- build a block
// ctx: { clock, t0, t1, theme:{ink, dim, accent}, snap(t), from }
export function buildBlock(E, ctx, srcItems, o = {}) {
  const { W, H, U, MEAS } = E, theme = ctx.theme, color = o.color || theme.ink;
  let items = parseItems(srcItems, o);
  const align = o.align || 'left', gap = o.gap ?? 0.022;
  if (o.accent) {                                                           // the card's one accent: its last (or first, or n-th) text line
    const ti = items.filter((i) => i.txt != null && i.kind !== 'rule' && i.kind !== 'gap' && i.kind !== 'kicker' && i.kind !== 'typed');
    const pick = o.accent === 'first' ? ti[0] : typeof o.accent === 'number' ? ti[o.accent] : ti[ti.length - 1]; if (pick) pick.accent = true;
  }
  // 1. expand typed items by measure, flatten to line specs
  const L = [];
  for (const it of items) {
    if (it.kind === 'rule') { L.push({ rule: true, ...it }); continue; }
    if (it.kind === 'gap') { L.push({ gapOnly: true, h: it.h ?? 0.02 }); continue; }
    const K = KIND[it.kind] || KIND.body, base = { ...K, ...it };
    const fontKey = base.font || K.font;
    if (it.kind === 'typed') {
      const capH = base.cap, size = capH * H / (measure(FONTS.T(100), 'H', 0).asc / 100);
      const t0s = String(base.txt);
      if (base.nowrap) { const need = fitSize(FONTS.T, t0s, base.ls, 0.99 * MEAS), k = Math.min(1, need / size); L.push({ ...base, txt: t0s, font: 'T', cap: capH * k, ls: base.ls, typed: true }); }
      else for (const w of wrapMeasure(t0s, FONTS.T, size, 0.99 * MEAS, base.ls)) L.push({ ...base, txt: w, font: 'T', cap: capH, ls: base.ls, typed: true });
    } else L.push({ ...base, txt: base.txt, font: fontKey });
  }
  // 2. timing: every word of every text line
  const tl = L.filter((l) => l.txt != null && !l.rule && !l.gapOnly);
  const flat = []; tl.forEach((l, li) => { if (l.on == null) words(l.txt).forEach((w, wi) => flat.push({ w, li, wi })); });   // lines with an explicit "on" are not matched
  const auto = ctx.clock.match(flat.map((x) => x.w), ctx.from ?? ctx.t0, { to: ctx.t1 + 0.8 });
  const t0 = ctx.t0 + 0.12, t1 = Math.max(t0 + 0.2, ctx.t1 - 0.5);
  const filled = fillGaps(auto || flat.map(() => null), t0, t1);
  tl.forEach((l) => { l.times = words(l.txt).map(() => t0); });
  flat.forEach((x, k) => { tl[x.li].times[x.wi] = filled[k]; });
  for (const l of tl) {
    if (l.on != null) { const on = Array.isArray(l.on) ? l.on.map((r) => ctx.at(r)) : words(l.txt).map(() => ctx.at(l.on)); l.times = on; }
    if (l.after != null) { const d = +l.after; l.times = l.times.map((t) => t + d); }
    // landing of a heavy / big line snaps to a nearby strong hit
    if (l.amp && l.times.length) { const k = l.times.length - 1; l.times[k] = ctx.snap(l.times[k]); if (l.times.length === 1) l.times[0] = l.times[k]; }
    // a line cannot land before the card starts
    l.times = l.times.map((t) => Math.max(t, ctx.t0));
  }
  // 3. geometry: sizes -> heights -> position in the safe zone
  const heights = L.map((l) => {
    if (l.rule) return 0.004; if (l.gapOnly) return l.h - gap;
    return E.geo({ ...l, base: 0 }).cap / H;
  });
  const total = heights.reduce((s, h, i) => s + h + (i ? gap : 0), 0);
  let top;
  const pos = o.pos ?? 'middle';
  if (typeof pos === 'number') top = pos;
  else if (pos === 'top') top = SAFE_Y0 + 0.01; else if (pos === 'upper') top = 0.21; else if (pos === 'lower') top = 0.63 - total; else top = 0.385 - total / 2;
  top = clamp(top, SAFE_Y0, Math.max(SAFE_Y0, SAFE_Y1 - total));
  if (o.top != null) top = o.top;
  const out = []; let y = top, prev = null;
  L.forEach((l, i) => {
    if (i) y += gap;
    if (l.rule) { out.push({ rule: true, y, prev }); y += heights[i]; return; }
    if (l.gapOnly) { y += heights[i]; return; }
    const cap = heights[i]; y += cap;
    const spec = { ...l, base: y, color: l.accent ? theme.accent : (l.color || color), align: l.align || align };
    if (spec.align === 'center') spec.cx = o.cx ?? 0.445; if (o.x != null && spec.align === 'left') spec.x = o.x * W;
    if (spec.alpha == null && o.alpha != null) spec.alpha = o.alpha;
    spec.mode = spec.mode || o.mode || 'slam';
    if (l.typed) spec.mode = 'type';
    out.push(spec); prev = spec; y += 0;
  });
  const bottom = y;
  // 4. hits
  const hits = [];
  for (const s of out) if (!s.rule && s.amp) hits.push([s.times[s.times.length - 1], s.amp, 5, s.kind === 'stamp' ? 0.05 : 0.04]);
  const lastT = Math.max(ctx.t0, ...out.filter((s) => !s.rule).map((s) => s.times[s.times.length - 1] ?? 0));
  const firstT = Math.min(...out.filter((s) => !s.rule).map((s) => s.times[0] ?? 1e9));
  let lowest = 0.0; for (const s of out) if (!s.rule && s.base > lowest) lowest = s.base;
  if (total > SAFE_Y1 - SAFE_Y0 + 0.03 && ctx.warn) ctx.warn(`text block is ${(total * 100).toFixed(0)}% of the frame high (safe zone is 51%): split the card`);
  const geos = [];
  function draw(E, extra = {}) {
    let lastGeo = null;
    for (const s of out) {
      if (s.rule) {
        if (!lastGeo) continue; const tr = (lastGeo.landT ?? 0) + 0.14; const x0 = lastGeo.G.inkL, wd = Math.min(MEAS, lastGeo.G.inkW);
        E.rule(x0, x0 + wd, s.y * H, tr, 0.22, Math.max(2, 0.0021 * H), rgba(color, 0.5 * (extra.alpha ?? 1)), E.ink); continue;
      }
      const G = E.line({ ...s, ...(extra.alpha != null ? { alpha: (s.alpha ?? 1) * extra.alpha } : {}) });
      lastGeo = { G, landT: s.times[s.times.length - 1] };
    }
  }
  return { draw, hits, lines: out, top, bottom, lastT, firstT, total };
}
