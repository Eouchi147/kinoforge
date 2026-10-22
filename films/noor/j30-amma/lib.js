// NOOR Juz 30: shared helpers for the sets and the overlay graphics (Lantern Road style, 1280x720 design frame).
// Every function is a pure function of its inputs and time: no clocks, seeded randomness only.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, noise1, rng, valueNoise2D } from '/harness/kit/film.js';
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, paintSky, paintRange, paintFog, paintRocks, paintTufts, pineTree, dabOn } from './paint.js';
export { Canvas, hex, mixc, mul, rgba, underpaint, ridged, paintSky, paintRange, paintFog, paintRocks, paintTufts, pineTree, dabOn, clamp, lerp, smoothstep, ease, noise1, rng, valueNoise2D, THREE };

export const WARM = [1.0, 0.5, 0.18];      // oil-lamp light on paint (linear)
export const GOLDL = [1.0, 0.66, 0.26];
export const MOON = [0.55, 0.62, 1.0];
export const PAL = { night: hex('#04060F'), gold: hex('#C9A227'), goldLit: hex('#f2d27a'), parch: hex('#FFFEF7'), ink: hex('#2C2416'), sage: hex('#8BA888'), brass: hex('#6e5426'), brassDark: hex('#2a1e10') };
export const hash1 = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
export const nn = valueNoise2D(77);

export const flick = (t, seed) => 1 + 0.06 * noise1(t * 7.3 + seed * 3.7, seed) + 0.03 * noise1(t * 19 + seed, seed + 2);
export function igniteEnv(t, t0, seed = 0, rise = 0.5) {
  if (t0 == null || t < t0) return 0; const u = t - t0; const a = ease.outCubic(clamp(u / rise)); const f = 1 + 0.25 * Math.exp(-Math.max(0, u - rise) / 0.3);
  return a * f * flick(t, seed);
}
export function tintAll(S, k, c = [1, 1, 1], skip = null) { for (const p of S.planes) { if (skip && skip(p)) continue; p.material.uniforms.uTint.value.set(k * c[0], k * c[1], k * c[2]); } }
export function lightsOn(plane, list) {
  const u = plane.material.uniforms; let n = 0;
  for (const l of [...list].sort((a, b) => b.k - a.k)) { if (!(l.k > 0.0005)) continue; if (n >= 8) break; u.uLP.value[n].set(l.p.x, l.p.y, l.p.z, l.r); u.uLC.value[n].set(l.c[0] * l.k, l.c[1] * l.k, l.c[2] * l.k); n++; }
  u.uNL.value = n;
}
export function glowAt(gg, x, y, r, a = 1, col = [255, 170, 90]) {
  if (r <= 0.5 || a <= 0.002) return; const g = gg.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${a})`); g.addColorStop(0.18, `rgba(${col[0]},${col[1]},${col[2]},${a * 0.45})`); g.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
  gg.fillStyle = g; gg.fillRect(x - r, y - r, r * 2, r * 2);
}
// drifting dust in a lamp beam or pollen in a garden (additive, design px box)
export function motes(gg, t, f, o = {}) {
  const { n = 24, col = [255, 215, 160], a = 0.35, size = 1.3, seed = 1, drift = [5, -3] } = o;
  for (let i = 0; i < n; i++) {
    const r1 = hash1(i * 3.7 + seed), r2 = hash1(i * 6.1 + seed), r3 = hash1(i * 1.3 + seed); const w = f.x1 - f.x0, h = f.y1 - f.y0;
    const px = f.x0 + (((r1 * w + drift[0] * t * (0.5 + r3) + 14 * Math.sin(t * 0.4 + i)) % w) + w) % w;
    const py = f.y0 + (((r2 * h + drift[1] * t * (0.5 + r3) + 9 * Math.sin(t * 0.33 + i * 2.1)) % h) + h) % h;
    const tw = 0.55 + 0.45 * Math.sin(t * (0.7 + r3 * 1.6) + i * 3.3);
    gg.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${a * tw})`; gg.beginPath(); gg.arc(px, py, size * (0.6 + r3), 0, 7); gg.fill();
  }
}
export function smoke(g, t, x, y, o = {}) {
  const { n = 7, rise = 80, wind = 6, r0 = 1.5, r1 = 10, a = 0.16, col = [190, 180, 200], life = 6, seed = 1 } = o;
  for (let i = 0; i < n; i++) {
    const u = (((t / life) + i / n + hash1(seed * 3.1)) % 1);
    const px = x + wind * u * life * 0.5 + 3 * Math.sin(t * 0.8 + i * 1.7) * u; const py = y - rise * u; const r = lerp(r0, r1, Math.sqrt(u)); const al = a * Math.sin(Math.PI * Math.min(1, u * 1.05)) * (1 - u * 0.55);
    const gr = g.createRadialGradient(px, py, 0, px, py, r); gr.addColorStop(0, rgba(col, al)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.fillRect(px - r, py - r, r * 2, r * 2);
  }
}
// twinkling stars over a painted sky, projected from a plane at depth D (so they ride with the parallax); stars[] = [x,y,mag]
export function makeStars(seed, box, n, magPow = 2.2) { const R = rng(seed); const out = []; for (let i = 0; i < n; i++) out.push([lerp(box[0], box[2], R()), lerp(box[1], box[3], Math.pow(R(), 1.25)), Math.pow(R(), magPow)]); return out; }
export function drawStars(F, D, stars, a = 1, yFade = null) {
  const gg = F.glow(); const K = F.K(D);
  for (let i = 0; i < stars.length; i++) { const [x, y, m] = stars[i]; let al = a * (0.35 + 0.65 * m) * (0.75 + 0.25 * Math.sin(F.t * (1.3 + hash1(i) * 2.2) + i)); if (yFade) al *= yFade(y); if (al < 0.02) continue;
    const p = F.P(D, x, y); if (p[0] < -20 || p[0] > 1300 || p[1] < -20 || p[1] > 740) continue; if (F.starClip) { const c = F.starClip; if (p[0] < c[0] || p[0] > c[2] || p[1] < c[1] || p[1] > c[3]) continue; }
    const r = (1.4 + 2.2 * m) * Math.max(0.8, Math.min(1.6, K)); gg.fillStyle = `rgba(235,236,255,${Math.min(1, al)})`; gg.beginPath(); gg.arc(p[0], p[1], r * 0.55, 0, 7); gg.fill(); if (m > 0.6) glowAt(gg, p[0], p[1], r * 4, al * 0.35, [190, 200, 255]); }
}
// a painted night sky for windows and wide skies
export function nightSky(C, o = {}) {
  const stops = (o.stops || [[-300, '#03040c'], [0, '#060a1d'], [260, '#0c1434'], [480, '#18214a'], [640, '#26305e'], [760, '#30385f']]).map(([y, c]) => [y, hex(c)]);
  return paintSky(C, { stops, glow: o.glow || { x: 900, y: 520, rx: 900, ry: 260, col: hex('#3a3f72'), a: 0.35 }, clouds: o.clouds || [], n: 0.8 });
}
// crescent moon (glow canvas + detail), lit side facing `dir`
export function crescent(F, x, y, r, a = 1, tilt = -0.5) {
  const gg = F.glow(); glowAt(gg, x, y, r * 7, 0.18 * a, [150, 165, 255]); glowAt(gg, x, y, r * 2.4, 0.25 * a, [220, 225, 255]);
  const g = F.g; g.save(); g.translate(x, y); g.rotate(tilt); g.fillStyle = `rgba(246,240,214,${a})`; g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.arc(r * 0.42, -r * 0.12, r * 0.86, 0, Math.PI * 2, true); g.fill('evenodd'); g.restore();
}

// ------------------------------------------------------------------ the Ramadan lantern (fanous): brass frame, glass panels, a cap and a ring
// drawn on the detail layer `g`; returns the glass centre. lit 0..1 (warm glass + glow drawn by the caller with glowLantern)
export function fanous(g, x, y, s, lit, t, seed = 0, o = {}) {
  const fl = lit > 0 ? flick(t, seed) : 1; const sw = o.sway ? o.sway * Math.sin(t * 0.9 + seed * 1.7) : 0;
  g.save(); g.translate(x, y); g.rotate(sw);
  const brass = o.brass || [92, 68, 34], dark = [30, 22, 14];
  const glassOff = o.glassOff || [58, 42, 30]; const glassOn = [255, 196, 108]; const gc = mixc(glassOff, mixc(glassOn, [255, 236, 180], 0.25 * fl), clamp(lit));
  // ring + chain
  g.strokeStyle = rgba(dark); g.lineWidth = Math.max(0.8, s * 0.05); g.beginPath(); g.arc(0, -s * 1.02, s * 0.1, 0, 7); g.stroke();
  if (o.chain) { g.beginPath(); g.moveTo(0, -s * 1.12); g.lineTo(0, -s * 1.12 - o.chain); g.stroke(); }
  // cap (dome) and finial
  g.fillStyle = rgba(brass); g.beginPath(); g.moveTo(-s * 0.42, -s * 0.6); g.quadraticCurveTo(0, -s * 1.05, s * 0.42, -s * 0.6); g.closePath(); g.fill();
  g.fillRect(-s * 0.48, -s * 0.62, s * 0.96, s * 0.07);
  // glass body: a tapering hexagonal lantern seen front-on: three panels
  const top = -s * 0.55, bot = s * 0.45, wt = s * 0.36, wb = s * 0.26;
  const body = new Path2D(); body.moveTo(-wt, top); body.lineTo(wt, top); body.lineTo(wb, bot); body.lineTo(-wb, bot); body.closePath();
  const gr = g.createLinearGradient(0, top, 0, bot); gr.addColorStop(0, rgba(mul(gc, 0.85))); gr.addColorStop(0.55, rgba(gc)); gr.addColorStop(1, rgba(mul(gc, 0.8))); g.fillStyle = gr; g.fill(body);
  // pierced brass pattern over the glass: little arches
  g.strokeStyle = rgba(mixc(dark, brass, 0.4), 0.95); g.lineWidth = Math.max(0.7, s * 0.045);
  for (const xx of [-1 / 3, 1 / 3]) { g.beginPath(); g.moveTo(lerp(-wt, wt, 0.5 + xx / 2 * 2 / 1), top); g.lineTo(lerp(-wb, wb, 0.5 + xx / 2 * 2 / 1), bot); g.stroke(); }
  g.stroke(body);
  if (s > 9) { g.lineWidth = Math.max(0.6, s * 0.03); for (let k = -1; k <= 1; k++) { const cx = k * s * 0.21, cy = (top + bot) * 0.5 - s * 0.05; g.beginPath(); g.moveTo(cx - s * 0.07, cy + s * 0.12); g.lineTo(cx - s * 0.07, cy - s * 0.02); g.quadraticCurveTo(cx, cy - s * 0.15, cx + s * 0.07, cy - s * 0.02); g.lineTo(cx + s * 0.07, cy + s * 0.12); g.stroke(); } }
  // base
  g.fillStyle = rgba(brass); g.beginPath(); g.moveTo(-wb * 1.15, bot); g.lineTo(wb * 1.15, bot); g.lineTo(wb * 0.6, bot + s * 0.16); g.lineTo(-wb * 0.6, bot + s * 0.16); g.closePath(); g.fill();
  g.fillRect(-s * 0.06, bot + s * 0.16, s * 0.12, s * 0.12);
  // flame inside
  if (lit > 0.05) { g.fillStyle = `rgba(255,246,214,${0.9 * clamp(lit)})`; const fh = s * 0.22 * (0.9 + 0.15 * fl); g.beginPath(); g.ellipse(0, (top + bot) * 0.5 + s * 0.08 - fh * 0.3, s * 0.05, fh * 0.5, 0, 0, 7); g.fill(); }
  g.restore();
  return [x, y + (-s * 0.05)];
}
export function glowLantern(gg, x, y, s, lit, t, seed = 0, k = 1) {
  if (lit <= 0.01) return; const fl = flick(t, seed);
  glowAt(gg, x, y, s * 9 * k, 0.16 * lit * fl, [255, 150, 70]); glowAt(gg, x, y, s * 2.6 * k, 0.5 * lit * fl, [255, 200, 120]); glowAt(gg, x, y, s * 0.7, 0.8 * lit, [255, 236, 190]);
}
// an oil lamp (clay, open spout), flame + glow; returns the flame tip
export function oilLamp(g, gg, x, y, s, t, k = 1, seed = 3) {
  const fl = flick(t, seed); const clay = [96, 62, 40];
  g.fillStyle = rgba(mul(clay, 0.75)); g.beginPath(); g.ellipse(x, y, s * 1.0, s * 0.42, 0, 0, 7); g.fill();
  g.fillStyle = rgba(clay); g.beginPath(); g.ellipse(x, y - s * 0.12, s * 0.95, s * 0.34, 0, 0, 7); g.fill();
  g.beginPath(); g.moveTo(x + s * 0.6, y - s * 0.25); g.quadraticCurveTo(x + s * 1.45, y - s * 0.3, x + s * 1.5, y - s * 0.12); g.quadraticCurveTo(x + s * 1.3, y + s * 0.05, x + s * 0.6, y + s * 0.05); g.fill();
  g.fillStyle = rgba(mul(clay, 0.4)); g.beginPath(); g.ellipse(x - s * 0.1, y - s * 0.2, s * 0.28, s * 0.1, 0, 0, 7); g.fill();
  const fx = x + s * 1.42, fy = y - s * 0.2; const fh = s * 0.95 * k * (0.9 + 0.2 * fl);
  if (k > 0.02) { g.fillStyle = `rgba(255,214,140,${0.95})`; g.beginPath(); g.moveTo(fx - s * 0.13, fy); g.quadraticCurveTo(fx - s * 0.16, fy - fh * 0.6, fx + s * 0.03 * Math.sin(t * 6 + seed), fy - fh); g.quadraticCurveTo(fx + s * 0.18, fy - fh * 0.5, fx + s * 0.13, fy); g.fill();
    g.fillStyle = 'rgba(255,250,228,0.9)'; g.beginPath(); g.ellipse(fx, fy - fh * 0.28, s * 0.05, fh * 0.2, 0, 0, 7); g.fill();
    glowAt(gg, fx, fy - fh * 0.4, s * 16 * k, 0.17 * fl * k, [255, 150, 70]); glowAt(gg, fx, fy - fh * 0.4, s * 3 * k, 0.55 * fl * k, [255, 205, 130]); }
  return [fx, fy - fh * 0.4];
}

// ------------------------------------------------------------------ text (crisp overlay, after the grade)
// The King Fahd Complex Uthmani text (quranenc) writes the staggered (open) tanween of idgham and ikhfa with its own font's code points:
// U+065E for open dammatan and U+0656 for open kasratan. Amiri Quran draws these marks at the standard Unicode points U+08F1 and U+08F2
// (U+065E is missing from it and U+0656 would draw a subscript alef). Same marks, mapped for display only; the source text is unchanged.
export const forAmiri = (s) => s.replace(/\u065E/g, '\u08F1').replace(/\u0656/g, '\u08F2');
export function drawArabic(og, text, x, y, size, o = {}) {
  const { color = '#f2d27a', alpha = 1, reveal = 1, shadow = 16, glow = 0 } = o; if (alpha <= 0.003 || reveal <= 0) return;
  text = forAmiri(text); og.save(); og.font = `400 ${size}px "Amiri Quran"`; og.direction = 'rtl'; og.textAlign = 'center'; og.textBaseline = 'middle';
  const w = og.measureText(text).width; const pad = size * 0.6;
  if (reveal < 1) { og.beginPath(); og.rect(x + w / 2 + pad - (w + 2 * pad) * reveal, y - size * 1.6, (w + 2 * pad) * reveal, size * 3.2); og.clip(); }
  og.globalAlpha = alpha; if (shadow) { og.shadowColor = 'rgba(4,4,12,0.9)'; og.shadowBlur = shadow; }
  if (glow) { og.shadowColor = `rgba(255,200,110,${glow})`; og.shadowBlur = size * 0.5; og.fillStyle = color; og.fillText(text, x, y); og.shadowColor = 'rgba(4,4,12,0.9)'; og.shadowBlur = shadow; }
  og.fillStyle = color; og.fillText(text, x, y); og.restore(); return w;
}
export function textW(og, text, font) { og.save(); og.font = font; const w = og.measureText(text).width; og.restore(); return w; }
