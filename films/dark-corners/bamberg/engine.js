// Bamberg (Kinetic): the typographic engine. Lines of words that LAND on the narration's word times (slam / pop / type),
// a handwriting writer (Junius's hand: glyph by glyph, wipe + wet ink + tremor), strokes. Pure functions of the frame.
import { clamp, lerp, ease, rng, keys, mixc, rgba, withStretch, withScale, measure, fitSize, mkLine, run, prefixAdv, FONTS, ribbon, densify, smoothstep, noise1 } from './lib.js';

export const FPS = 24;
// A word lands with weight and then rests: a short vertical stretch that settles (no rebound for plain words, one soft rebound for the line's key word).
export const LAND = [[0, 1.10], [1, 1.04], [2, 1.008], [3, 1.0]];
export const HEAVY = [[0, 1.15], [1, 1.065], [2, 1.0], [3, 0.985], [4, 1.0]];
export const PAYOFF = [[0, 1.20], [1, 1.08], [2, 0.994], [3, 0.972], [4, 0.99], [5, 1.0]];
export const SLAM = [[0, 1.22], [1, 1.09], [2, 1.0], [3, 0.972], [4, 0.99], [5, 1.0]];                  // uniform scale (year / date stamps)
const hexLum = (h) => { const v = [1, 3, 5].map((k) => parseInt(h.slice(k, k + 2), 16)); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
export const landFrame = (t) => Math.ceil(t * FPS - 1e-6);

export function createEngine(W, H, g, ink, cues) {
  const U = H / 1280, AX = 0.11 * W, MEAS = 0.67 * W;
  const E = { W, H, U, AX, MEAS, g, ink, f: 0, t: 0, cues };
  const font = (key) => FONTS[key];

  E.emFit = (fk, txt, frac, ls = 0) => fitSize(font(fk), txt, ls, 0.97 * frac * MEAS) / H;                // font size (H units) that makes `txt` span frac of the measure
  // ---- cue lookup: tw('o1','witch.') = start time of that word on the film's timeline; nth picks a repeated word
  E.tw = (id, word, nth = 0) => { const L = cues.lines.find((l) => l.id === id); if (!L) throw new Error('no line ' + id); let n = 0; for (const w of L.words) if (w[0].toLowerCase() === word.toLowerCase()) { if (n++ === nth) return w[1]; } throw new Error('no word ' + word + ' in ' + id); };
  E.te = (id, word, nth = 0) => { const L = cues.lines.find((l) => l.id === id); let n = 0; for (const w of L.words) if (w[0].toLowerCase() === word.toLowerCase()) { if (n++ === nth) return w[2]; } throw new Error('no word ' + word + ' in ' + id); };

  // ---- resolve a line spec to geometry (font size, ink box, word origins). Cheap: text metrics are cached.
  E.geo = (s) => {
    const fk = font(s.font || 'B'), ls = s.ls || 0;
    let size;
    if (s.fit) { size = fitSize(fk, s.txt, ls, s.fit * 0.985 * MEAS); if (s.maxCap) size = Math.min(size, s.maxCap * H / (measure(fk(100), 'H', 0).asc / 100)); }
    else if (s.cap) size = s.cap * H / (measure(fk(100), 'H', 0).asc / 100);
    else size = s.em * H;
    const ln = mkLine(s.txt, fk, size, ls);
    let ox, inkL;
    const al = s.align || 'left';
    if (al === 'center') { inkL = (s.cx ?? 0.5) * W - ln.inkW / 2; ox = inkL + ln.l; } else if (al === 'right') { inkL = (s.x ?? 0.89 * W) - ln.inkW; ox = inkL + ln.l; } else { inkL = s.x ?? AX; ox = inkL + ln.l; }
    const words = []; let idx = 0;
    for (const w of s.txt.split(' ')) { words.push({ text: w, idx, ox: ox + prefixAdv(ln, idx), m: measure(ln.font, w, ln.ls) }); idx += w.length + 1; }
    return { ln, ox, inkL, inkW: ln.inkW, cap: ln.cap, base: s.base * H, words, size };
  };

  // stack lines top to bottom (top, gap in H units): sets .base on each spec copy and returns [{...spec, base}] plus the bottom
  E.stack = (specs, top, gap) => {
    let y = top * H; const out = [];
    for (const s of specs) { const q = { ...s, base: 0 }; const cap = E.geo({ ...q, base: 0 }).cap; y += cap; q.base = y / H; out.push(q); y += gap * H; }
    return { lines: out, bottom: (y - gap * H) / H };
  };

  // optical stack: the gap between two lines follows the type size (k x the cap height of the lower line, clamped), so a small kicker sits close to its
  // payoff and two big lines are not left floating. gaps can still be forced with spec.gapAfter (H units).
  E.stk = (specs, top, k = 0.36, lo = 0.012, hi = 0.03) => {
    let y = top * H; const out = []; let prev = null;
    for (const s of specs) { const q = { ...s, base: 0 }, cap = E.geo({ ...q, base: 0 }).cap; if (prev) y += (prev.gapAfter != null ? prev.gapAfter * H : Math.min(hi * H, Math.max(lo * H, k * cap))); y += cap; q.base = y / H; out.push(q); prev = s; }
    return { lines: out, bottom: y / H };
  };

  // ---- draw a line whose words land at s.times (seconds). mode: slam | pop | type | stamp
  E.line = (s, f = E.f, t = E.t) => {
    const G = E.geo(s), words = G.words, ink = s.to || E.ink;
    const times = Array.isArray(s.times) ? s.times : words.map(() => s.times);
    const col = s.color, FL = (hexLum(col) < 120 ? col : '#fffaf0'), mode = s.mode || 'slam', curveOf = (i) => (s.curves && s.curves[i]) || s.curve || LAND;
    let outA = 1;
    if (s.out != null) { const k = (t - s.out) / (s.outDur || 0); if (t >= s.out) { if (!s.outDur) return G; outA = 1 - clamp(k); if (outA <= 0) return G; } }
    const a0 = (s.alpha ?? 1) * outA;
    for (let i = 0; i < words.length; i++) {
      const w = words[i], tl = times[i]; if (tl == null || t < tl - 1e-9) continue;
      const fl = landFrame(tl), k = f - fl; if (k < 0) continue;
      const ay = G.base - G.cap / 2, dy = (s.rise || 0) * (1 - ease.outCubic(clamp((t - tl) / 0.25))) * E.H;
      if (mode === 'slam') {
        const sx = s.sx ? keys(k, s.sx) : 1;
        withStretch(ink, ay, keys(k, curveOf(i)), () => { ink.save(); if (sx !== 1) { ink.translate(w.ox, 0); ink.scale(sx, 1); ink.translate(-w.ox, 0); } run(ink, G.ln, w.text, w.ox, G.base + dy, { fill: mixc(col, FL, k === 0 ? 0.7 : k === 1 ? 0.28 : 0), alpha: a0 }); ink.restore(); });
      } else if (mode === 'stamp') {
        if (k < 3 && s.smear) for (const [dt, al] of [[0.7, 0.10], [0.35, 0.20]]) withScale(ink, G.inkL, ay, keys(k - dt, SLAM), () => run(ink, G.ln, w.text, w.ox, G.base, { fill: rgba(col, al * a0) }));
        withScale(ink, s.pivotX ?? G.inkL, ay, keys(k, SLAM), () => run(ink, G.ln, w.text, w.ox, G.base + dy, { fill: mixc(col, FL, k === 0 ? 0.8 : k === 1 ? 0.35 : 0), alpha: a0 }));
      } else if (mode === 'pop') {
        const p = ease.outCubic(clamp((t - tl) / (s.popDur || 0.3)));
        withScale(ink, w.ox - w.m.l, ay, lerp(1.03, 1, p), () => run(ink, G.ln, w.text, w.ox, G.base + dy, { fill: col, alpha: a0 * p }));
      } else if (mode === 'type') {
        const nxt = times[i + 1] != null ? times[i + 1] : tl + 0.5, dur = Math.min(0.6, Math.max(0.1, nxt - tl)), n = w.text.length, per = Math.min(s.perChar || 0.05, dur / n);
        const nc = clamp(Math.floor((t - tl) / per + 1), 0, n);
        if (nc > 0) run(ink, G.ln, w.text.slice(0, nc), w.ox, G.base + dy, { fill: col, alpha: a0 });
      }
    }
    return G;
  };

  // ---- Junius's hand: handwriting written glyph by glyph. spec: {txt, em, x, base, times:[per word], color, trem(t)->0..1, glyph (s per glyph, optional), wipe, dry}
  const JC = new Map();
  const jitFor = (s, n) => { const key = (s.seed || 1) + '|' + n; if (JC.has(key)) return JC.get(key); const r = rng(1000 + (s.seed || 1) * 17), a = []; for (let i = 0; i < n; i++) a.push({ dx: r() - 0.5, dy: r() - 0.5, rot: r() - 0.5, sc: r() - 0.5, lag: r() }); JC.set(key, a); return a; };
  E.hand = (s, f = E.f, t = E.t) => {
    const fk = font(s.font || 'C'), size = s.em * H, ln = mkLine(s.txt, fk, size, 0), jit = jitFor(s, s.txt.length);
    const x0 = s.align === 'center' ? (s.cx ?? 0.5) * W - ln.inkW / 2 + ln.l : (s.x ?? AX) + ln.l, base = s.base * H;
    const words = s.txt.split(' '), widx = []; let p = 0; for (const w of words) { widx.push(p); p += w.length + 1; }
    const wipe = s.wipe ?? 0.07, dry = s.dry ?? 0.22, trem = s.trem || (() => 0.35);
    if (s.out != null && t >= s.out) { const k = 1 - clamp((t - s.out) / (s.outDur || 0.25)); if (k <= 0) return { ln, x0, base, inkW: ln.inkW, any: false }; s = { ...s, alpha: (s.alpha ?? 1) * k }; }
    let any = false, tFirst = 1e9;
    const times = s.times;
    // slot times
    for (let wi = 0; wi < words.length; wi++) {
      const w = words[wi], tw0 = times[wi]; if (tw0 == null || t < tw0) continue;
      const nxt = times[wi + 1] != null ? times[wi + 1] : tw0 + (s.lastDur ?? 0.5), dur = Math.min(s.maxWord ?? 0.75, Math.max(0.12, nxt - tw0)), n = w.length;
      for (let j = 0; j < n; j++) {
        const gi = widx[wi] + j, tk = s.glyph ? tw0 + j * s.glyph : tw0 + (j / n) * dur * 0.9, pr = (t - tk) / wipe; if (pr <= 0) continue;
        any = true; const age = t - tk, wet = 1 - smoothstep(0.02, dry, age), jt = jit[gi], T = trem(tk) * U;
        let adv = measure(ln.font, w[j], 0).adv, gx = x0 + prefixAdv(ln, gi), cx = gx + adv / 2, sqx = 1;
        if (s.squash && s.squash.w === wi) { const wa = x0 + prefixAdv(ln, widx[wi]), wb = wa + measure(ln.font, w, 0).adv, wc = (wa + wb) / 2; sqx = s.squash.k(t); cx = wc + (cx - wc) * sqx; }
        const dyy = jt.dy * 3.0 * T + (s.drift ? s.drift * (gi / s.txt.length) * U * 14 : 0) + (s.sag ? s.sag(gi / s.txt.length) * U : 0);
        E.ink.save(); E.ink.translate(cx + jt.dx * 2.4 * T, base + dyy); E.ink.rotate(jt.rot * 0.05 * (0.4 + T / U) + (s.tilt || 0)); E.ink.scale(sqx * (1 + jt.sc * 0.03 * (0.4 + T / U)), 1 + jt.sc * 0.03 * (0.4 + T / U));
        if (pr < 1) { E.ink.beginPath(); E.ink.rect(-adv / 2 - 3 * U, -ln.asc * 1.3, (adv + 6 * U) * clamp(pr), (ln.asc + ln.desc) * 1.8); E.ink.clip(); }
        E.ink.font = ln.font; E.ink.letterSpacing = '0px'; E.ink.textAlign = 'left'; E.ink.textBaseline = 'alphabetic';
        const ca = (s.alpha ?? 1);
        if (wet > 0.01) { E.ink.shadowColor = rgba(s.color, 0.5 * wet * ca); E.ink.shadowBlur = (1.2 + 3.2 * wet) * U; }
        E.ink.fillStyle = rgba(s.color, ca); E.ink.fillText(w[j], -adv / 2, 0); E.ink.restore();
      }
    }
    return { ln, x0, base, inkW: ln.inkW, any };
  };

  // word box of the k-th word of a hand line (for effects that clamp onto a word)
  E.handWord = (s, wi) => { const ln = mkLine(s.txt, font(s.font || 'C'), s.em * H, 0), x0 = (s.align === 'center' ? (s.cx ?? 0.5) * W - ln.inkW / 2 : (s.x ?? AX)) + ln.l, ws = s.txt.split(' '); let idx = 0; for (let i = 0; i < wi; i++) idx += ws[i].length + 1; const a = x0 + prefixAdv(ln, idx), adv = measure(ln.font, ws[wi], 0).adv; return { x0: a, x1: a + adv, base: s.base * H, cap: ln.cap, asc: ln.asc }; };
  // ---- strokes
  const ulPts = (x0, x1, y, amp = 1.6) => densify([[x0, y], [x0 + (x1 - x0) * 0.33, y + amp * U * 0.6], [x0 + (x1 - x0) * 0.7, y - amp * U * 0.4], [x1, y - amp * U]], 6);
  E.stroke = (x0, x1, y, t0, dur, w, color, { seed = 5, amp = 1.6, to = E.ink } = {}) => {
    const p = ease.outCubic(clamp((E.t - t0) / dur)); if (E.t < t0) return;
    to.save(); to.fillStyle = color; const head = ribbon(to, ulPts(x0, x1, y, amp), w, seed, { upto: p, taper: 0.06 });
    if (p < 1 && head) { to.beginPath(); to.arc(head[0], head[1], w * 0.62, 0, 6.2832); to.fill(); } to.restore();
  };
  E.rule = (x0, x1, y, t0, dur, th, color, to = E.g) => { const p = ease.outCubic(clamp((E.t - t0) / dur)); if (E.t < t0) return; to.fillStyle = color; to.fillRect(x0, y, (x1 - x0) * p, th); };
  E.HEAVY = HEAVY; E.PAYOFF = PAYOFF; E.LAND = LAND;
  // the series card (also the end card): DARK CORNERS + episode title. t0 = slam time, out = start of the fade (optional)
  E.titleCard = (t0, out = null, outDur = 0.2, alpha = 1) => {
    const C = E.C, base = { color: C.cream, out: out ?? undefined, outDur, alpha };
    const T1 = E.line({ ...base, txt: 'DARK CORNERS', font: 'B', fit: 1.0, ls: 0.06, base: 0.40, times: t0, mode: 'stamp', smear: true });
    const a = out != null ? 1 - clamp((E.t - out) / outDur) : 1;
    E.rule(E.AX, E.AX + T1.inkW, 0.43 * H, t0 + 0.3, 0.3, Math.max(2, 0.0021 * H), rgba(C.cream, 0.5 * a * alpha));
    const sub = 'A Hundred Thousand Good Nights', ws = sub.split(' ');
    E.line({ ...base, txt: sub, font: 'C', fit: 1.0, ls: 0, base: 0.485, times: ws.map((_, i) => t0 + 0.6 + i * 0.13), mode: 'pop', popDur: 0.4 });
  };
  return E;
}
