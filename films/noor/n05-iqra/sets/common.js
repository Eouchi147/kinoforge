// shared painting / lighting helpers for the sets (from Kleidion, unchanged except this line)
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, noise1, rng, valueNoise2D } from '/harness/kit/film.js';
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged } from '../paint.js';

export const WARM = [1.0, 0.47, 0.15];          // lantern light on paint (linear)
export const GOLD = [1.0, 0.62, 0.2];
export const nn = valueNoise2D(77), nn2 = valueNoise2D(91);
export const det = (x, a = 22, b = 8, s = 0) => a * (nn.fbm(x * 0.008 + s, 3.1, 5) - 0.5) + b * (nn2.fbm(x * 0.04 + s, 7.3, 3) - 0.5);
export const bump = (x, c, w, h) => h * Math.exp(-(((x - c) / w) ** 2));
export function igniteEnv(t, t0, seed = 0, flare = 1.45, rise = 0.07) {
  if (t < t0) return 0; const u = t - t0; const a = ease.outCubic(clamp(u / rise)); const f = 1 + (flare - 1) * Math.exp(-Math.max(0, u - rise) / 0.18);
  return a * f * (1 + 0.05 * noise1(t * 8.3 + seed * 3.7, seed) + 0.025 * noise1(t * 21 + seed, seed + 2));
}
export const flick = (t, seed) => 1 + 0.05 * noise1(t * 8.3 + seed * 3.7, seed) + 0.025 * noise1(t * 21 + seed, seed + 2);
export const fireFlick = (t, seed) => 1 + 0.16 * noise1(t * 9 + seed * 2.1, seed) + 0.08 * noise1(t * 23 + seed, seed + 4);

// Catmull-Rom through points -> dense polyline [{x,y,...extra}] (extra numeric fields interpolated)
export function spline(pts, seg = 14, keys = []) {
  const out = []; const n = pts.length; const g = (i) => pts[clamp(i, 0, n - 1)];
  for (let i = 0; i < n - 1; i++) for (let k = 0; k < seg; k++) {
    const t = k / seg, t2 = t * t, t3 = t2 * t; const p0 = g(i - 1), p1 = g(i), p2 = g(i + 1), p3 = g(i + 2); const o = {};
    for (const key of ['x', 'y', ...keys]) o[key] = 0.5 * ((2 * p1[key]) + (-p0[key] + p2[key]) * t + (2 * p0[key] - 5 * p1[key] + 4 * p2[key] - p3[key]) * t2 + (-p0[key] + 3 * p1[key] - 3 * p2[key] + p3[key]) * t3);
    out.push(o);
  }
  const l = pts[n - 1]; const o = {}; for (const key of ['x', 'y', ...keys]) o[key] = l[key]; out.push(o);
  let s = 0; out[0].s = 0; for (let i = 1; i < out.length; i++) { s += Math.hypot(out[i].x - out[i - 1].x, out[i].y - out[i - 1].y); out[i].s = s; }
  const total = s; out.total = total; out.at = (u) => { const d = clamp(u, 0, 1) * total; let a = 0, b = out.length - 1; while (b - a > 1) { const m = (a + b) >> 1; if (out[m].s <= d) a = m; else b = m; }
    const f = (d - out[a].s) / Math.max(1e-6, out[b].s - out[a].s); const r = {}; for (const key of Object.keys(out[a])) r[key] = lerp(out[a][key], out[b][key], f); r.dx = out[b].x - out[a].x; r.dy = out[b].y - out[a].y; return r; };
  return out;
}
// a ground road as a ribbon with perspective foreshortening: half-width hw(y) measured across the road; k = ground tilt (vertical squash)
export function ribbonPath(dense, hw, k = 0.3, extra = 0) {
  const L = [], R = [];
  for (let i = 0; i < dense.length; i++) { const a = dense[Math.max(0, i - 1)], b = dense[Math.min(dense.length - 1, i + 1)]; let tx = b.x - a.x, ty = (b.y - a.y) / k; const l = Math.hypot(tx, ty) || 1; tx /= l; ty /= l;
    const nx = -ty, ny = tx; const w = hw(dense[i].y) + extra; L.push([dense[i].x + nx * w, dense[i].y + ny * w * k]); R.push([dense[i].x - nx * w, dense[i].y - ny * w * k]); }
  const p = new Path2D(); p.moveTo(L[0][0], L[0][1]); for (let i = 1; i < L.length; i++) p.lineTo(L[i][0], L[i][1]); for (let i = R.length - 1; i >= 0; i--) p.lineTo(R[i][0], R[i][1]); p.closePath(); return { path: p, L, R };
}
// scale tint over every plane of a set (night falling etc.): k brightness, c colour multipliers
export function tintAll(S, k, c = [1, 1, 1], skip = null) { for (const p of S.planes) { if (skip && skip(p)) continue; p.material.uniforms.uTint.value.set(k * c[0], k * c[1], k * c[2]); } }
export function lightsOn(plane, list) { // list of {p: Vector3, r, c, k}
  const u = plane.material.uniforms; let n = 0; for (const l of list) { if (!(l.k > 0.0005)) continue; if (n >= 8) break; u.uLP.value[n].set(l.p.x, l.p.y, l.p.z, l.r); u.uLC.value[n].set(l.c[0] * l.k, l.c[1] * l.k, l.c[2] * l.k); n++; } u.uNL.value = n;
}
// reusable painted night/dusk skies
export function skyDusk(S, D, cover, seed, opt = {}) {
  const r = cover(D); const C = new Canvas(r, { seed });
  const o = Object.assign({ stops: [[-500, '#0b0e30'], [0, '#141944'], [250, '#262c5d'], [420, '#444580'], [540, '#6a5f90'], [640, '#8f7a9c']], glow: { x: 60, y: 600, rx: 760, ry: 230, col: '#c49fa6', a: 0.55 }, clouds: null }, opt);
  const stops = o.stops.map(([y, c]) => [y, hex(c)]);
  const clouds = (o.clouds || [{ y: 140, h: 13, x0: -300, x1: 1100, col: '#1f2454', lit: '#5d5789', litA: 0.6, sy: 0.03 }, { y: 300, h: 12, x0: -200, x1: 1200, col: '#2e3366', lit: '#8f7c9f', litA: 0.7, thr: 0.5, sy: 0.034 }, { y: 440, h: 10, x0: 200, x1: 1300, col: '#3a3d72', lit: '#a18aa6', litA: 0.7, thr: 0.5, sy: 0.04 }]).map((c) => ({ ...c, col: hex(c.col), lit: hex(c.lit) }));
  return { r, C, stops, clouds, glow: o.glow && { ...o.glow, col: hex(o.glow.col) } };
}
export { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, THREE };

// a vertical rock face: fills the side of the canvas beyond edge(y) (side 'L' = x < edge, 'R' = x > edge); lit rim along the edge, strata ledges
export function paintCliff(C, { edge, side = 'L', base, mid, rim, lit = null, strata = 46, bushes = 0.5 }) {
  const [x0, y0, x1, y1] = C.rect; const g = C.g, R = C.R, n = C.n;
  const path = new Path2D(); if (side === 'L') { path.moveTo(x0 - 20, y0 - 20); for (let y = y0 - 20; y <= y1 + 20; y += 6) path.lineTo(edge(y), y); path.lineTo(x0 - 20, y1 + 20); } else { path.moveTo(x1 + 20, y0 - 20); for (let y = y0 - 20; y <= y1 + 20; y += 6) path.lineTo(edge(y), y); path.lineTo(x1 + 20, y1 + 20); }
  path.closePath(); const m = C.mask((gg) => gg.fill(path)); const sgn = side === 'L' ? 1 : -1;
  const colAt = (x, y) => { const d = clamp(Math.abs(x - edge(y)) / 260); const f = n.fbm(x * 0.012, y * 0.006, 4); const facet = n.fbm(x * 0.02 + 5, y * 0.01, 3); let c = mixc(mid, base, smoothstep(0, 1, d) * 0.9); c = mixc(c, mul(mid, 0.6), smoothstep(0.55, 0.75, f) * 0.5); if (lit) c = mixc(c, lit, smoothstep(0.55, 0.7, facet) * 0.35 * (1 - d)); return c; };
  underpaint(C, colAt, path, 8);
  C.strokes({ n: C.area / 900, mask: m, color: colAt, angle: (x, y) => Math.PI / 2 + (n.fbm(x * 0.01, y * 0.004, 3) - 0.5) * 0.9 + (R() - 0.5) * 0.25, len: [26, 80], wid: [6, 14], alpha: [0.4, 0.75], jv: 0.07, bend: 0.1 });
  C.strokes({ n: C.area / 1800, mask: m, color: (x, y) => mul(colAt(x, y), 0.75), angle: (x, y) => (R() - 0.5) * 0.12, len: [20, 60], wid: [3, 6], alpha: [0.35, 0.6], jv: 0.08, bend: 0.05 });
  for (let y = y0; y < y1; y += strata * (0.6 + R() * 0.9)) { const e = edge(y); for (let k = 0; k < 6; k++) { const x = e + sgn * -1 * (R() * 200) * (side === 'L' ? -1 : 1) * 0 + (side === 'L' ? -R() * 220 : R() * 220); C.dab(x, y + (R() - 0.5) * 8, (R() - 0.5) * 0.1, 30 + R() * 70, 2 + R() * 3, mul(base, 0.55), 0.55, 0.03); } }
  for (let y = y0; y < y1; y += 3 + R() * 6) { const e = edge(y), e2 = edge(y + 6); const slope = (e2 - e) / 6; const lightFacing = side === 'L' ? slope < 0.05 : slope > -0.05; if (!lightFacing && R() < 0.7) continue; C.dab(e - sgn * (2 + R() * 3) * -1 * -1 + (side === 'L' ? -3 : 3), y, Math.PI / 2 + slope * 0.6, 8 + R() * 22, 2.4 + R() * 3.6, rim, 0.55 + R() * 0.4, 0.05); }
  return m;
}
