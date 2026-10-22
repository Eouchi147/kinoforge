// Kinetic cards made of handwriting: letter (warm parchment, ink writing itself) and quote (a third hand, double-struck).
import { clamp, lerp, ease, rgba, smoothstep, measure, FONTS, wrapMeasure, fitSize } from '../lib.js';
import { buildBlock } from '../blocks.js';
import { fillGaps } from '../timeline.js';

const wordsOf = (s) => String(s).split(' ').filter(Boolean);

// timing for a list of wrapped lines: match every word to the cues, fill gaps, split back per line
function lineTimes(ctx, lines, from, to) {
  const flat = lines.flatMap((l) => wordsOf(l));
  const auto = ctx.clock.match(flat, from, { to: to + 0.8 });
  const ts = fillGaps(auto || flat.map(() => null), ctx.t0 + 0.15, Math.max(ctx.t0 + 0.4, ctx.t1 - 0.6));
  let k = 0; return lines.map((l) => wordsOf(l).map(() => ts[k++]));
}

// ---------------------------------------------------------------- letter: ink writes itself, glyph by glyph, on the cue words
// card: { text, kicker?, size: 'normal'|'big', fail?: true (the hand weakens), tremble?, underline?, color?, sign? }
export function letter(E, c, ctx) {
  const { W, H, U } = E, th = ctx.theme;
  const em = (c.em ?? (c.size === 'big' ? 0.075 : c.size === 'small' ? 0.042 : 0.054));
  const px = em * H, pitch = em * (c.pitch ?? 1.42);
  const src = Array.isArray(c.lines) ? c.lines : null;
  const lines = src ? src.map(String) : wrapMeasure(String(c.text), FONTS.C, px, E.MEAS * 0.97, 0);
  const sign = c.sign ? String(c.sign) : null;
  const all = sign ? [...lines, sign] : lines;
  const times = lineTimes(ctx, all, ctx.from ?? ctx.t0, ctx.t1);
  const total = (all.length - 1) * pitch + em * 0.6, kick = c.kicker ? 0.075 : 0;
  const pos = c.pos ?? 'upper';
  const top = typeof pos === 'number' ? pos : pos === 'top' ? 0.19 : pos === 'lower' ? 0.62 - total : pos === 'middle' ? 0.385 - total / 2 : 0.23;
  const first = top + kick + em * 0.7;
  const tremb = c.tremble ?? 0.5, tEnd = ctx.t1;
  const trem = c.fail ? (tk) => tremb * 0.6 + (c.failTo ?? 1.4) * smoothstep(ctx.t0, tEnd - 1, tk) : () => tremb;
  const kickB = c.kicker ? buildBlock(E, ctx, [{ kind: 'kicker', txt: String(c.kicker).toUpperCase(), color: th.ink }], { pos: top, emph: 'none' }) : null;
  const specs = all.map((txt, i) => ({
    txt, em, base: first + i * pitch + (i === all.length - 1 && sign ? pitch * 0.25 : 0), times: times[i], color: c.accent && i === all.length - 1 ? th.accent : (c.color || th.ink), trem, seed: (c.seed ?? 3) + i,
    sag: c.fail ? (u) => (c.sag ?? 4) * (i / all.length) + 6 * u * (i / all.length) : null, maxWord: 0.7, lastDur: 0.6, x: i === all.length - 1 && sign ? E.AX + 0.22 * W : undefined,
  }));
  const lastT = Math.max(...times.map((t) => t[t.length - 1]));
  const draw = (E) => {
    if (kickB) kickB.draw(E);
    const res = specs.map((s) => E.hand(s));
    if (c.underline) {
      const last = res[(sign ? all.length - 2 : all.length - 1)], tU = lastT + 0.55;
      if (last && last.inkW) E.stroke(E.AX, E.AX + last.inkW * 0.98, specs[sign ? all.length - 2 : all.length - 1].base * H + 0.018 * H, tU, 0.4, 0.007 * H, c.color || th.ink, { seed: 9 });
    }
    if (c.blot) {                                                 // the pen gives out: a blot spreads where the last word ends
      const tb = lastT + 0.55, p = ease.outCubic(clamp((E.t - tb) / 0.5)); if (E.t >= tb) {
        const r = res[res.length - 1], s = specs[specs.length - 1], x = (s.x ?? E.AX) + (r.inkW || 0) + 0.02 * W, y = s.base * H + 0.006 * H, I = E.ink;
        I.save(); I.fillStyle = rgba(th.ink, 0.9); I.beginPath(); I.ellipse(x, y, 5 * U * p, 4 * U * p, 0.3, 0, 6.2832); I.fill(); I.fillRect(x - 1.1 * U, y, 2.2 * U, 18 * U * p); I.restore();
      }
    }
  };
  return { draw, hits: c.hit === false ? [] : [[ctx.t0, 9, 6, 0]], lastT };
}

// ---------------------------------------------------------------- quote: a third hand. Serif, double-struck, tilted a little.
// card: { text, by?, size?, tilt? (radians), mark?: true }
export function quote(E, c, ctx) {
  const { W, H, U } = E, th = ctx.theme;
  const em = c.em ?? (c.size === 'big' ? 0.062 : 0.05), px = em * H, pitch = em * 1.32;
  const fontKey = c.italic ? 'FI' : 'F';
  const lines = wrapMeasure(String(c.text), FONTS[fontKey], px, E.MEAS * 0.96, 0);
  const times = lineTimes(ctx, lines, ctx.from ?? ctx.t0, ctx.t1);
  const total = (lines.length - 1) * pitch + em * 0.7 + (c.by ? 0.07 : 0);
  const pos = c.pos ?? 'middle', top = typeof pos === 'number' ? pos : pos === 'top' ? 0.2 : pos === 'lower' ? 0.62 - total : pos === 'upper' ? 0.24 : 0.385 - total / 2;
  const first = top + em * 0.75 + (c.mark !== false ? 0.05 : 0), tilt = c.tilt ?? -0.028;
  const specs = lines.map((txt, i) => ({ txt, font: fontKey, em, base: first + i * pitch, times: times[i], color: c.color || th.ink }));
  const lastT = Math.max(...times.map((t) => t[t.length - 1]));
  const cx = E.AX + E.MEAS / 2, cy = (first + (lines.length - 1) * pitch / 2) * H;
  const by = c.by ? buildBlock(E, { ...ctx, from: lastT }, [{ kind: 'kicker', txt: String(c.by).toUpperCase(), on: lastT + 0.35 }], { pos: first + (lines.length - 1) * pitch + 0.045, emph: 'none', color: rgba(th.ink, 0.65) }) : null;
  const draw = (E) => {
    const ink = E.ink; ink.save(); ink.translate(cx, cy); ink.rotate(tilt); ink.translate(-cx, -cy);
    if (c.mark !== false) { const a = clamp((E.t - ctx.t0) / 0.3) * 0.5; ink.save(); ink.globalAlpha = a; ink.fillStyle = th.ink; ink.font = `400 ${0.2 * H}px "IM Fell English"`; ink.textBaseline = 'alphabetic'; ink.fillText('“', E.AX - 0.015 * W, (top + 0.03) * H + 0.07 * H); ink.restore(); }
    for (const s of specs) {                                       // struck twice, the second blow a hair off register
      E.line({ ...s, mode: 'pop', popDur: 0.25, x: E.AX + 2.2 * U, base: s.base + 1.4 * U / H, alpha: 0.42, color: s.color });
      E.line({ ...s, mode: 'pop', popDur: 0.25 });
    }
    ink.restore();
    if (by) by.draw(E);
  };
  return { draw, hits: [[times[0][0], 4, 4, 0.03]], lastT };
}
