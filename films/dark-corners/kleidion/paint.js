// p03 painting engine, deterministic procedural brushwork on Canvas2D, drawn in *design px* (1280x720 frame space).
// Every surface is built the way a matte painter works: flat underpainting, then big dabs, then smaller dabs, colour
// sampled from a value/temperature field with jitter, direction from a flow field, edges broken by spill and fbm.
import { rng, valueNoise2D, clamp, lerp, smoothstep } from '/harness/kit/film.js';

export const hex = (h) => { const n = parseInt(h.replace('#', ''), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
export const mixc = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
export const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
export const rgba = (c, a = 1) => `rgba(${Math.round(clamp(c[0], 0, 255))},${Math.round(clamp(c[1], 0, 255))},${Math.round(clamp(c[2], 0, 255))},${clamp(a, 0, 1).toFixed(3)})`;
export function ramp(stops, t) {
  if (t <= stops[0][0]) return stops[0][1];
  for (let i = 1; i < stops.length; i++) if (t <= stops[i][0]) { const [t0, c0] = stops[i - 1], [t1, c1] = stops[i]; return mixc(c0, c1, (t - t0) / (t1 - t0)); }
  return stops[stops.length - 1][1];
}

// a single tapered dab on any 2D context (used by the figure painter too)
export function dabOn(g, x, y, ang, len, wid, col, a, bend = 0, taper = 0.6) { Canvas.prototype.dab.call({ g }, x, y, ang, len, wid, col, a, bend, taper); }

const CPU_RASTER = true; // software Skia raster: faster than SwiftShader-backed canvases for ~500k dabs (measured 15.6 s vs 18.1 s)
export class Canvas {
  constructor(rect, { q = 1, seed = 1 } = {}) {
    this.rect = rect; this.q = q; const [x0, y0, x1, y1] = rect;
    this.c = document.createElement('canvas'); this.c.width = Math.max(4, Math.ceil((x1 - x0) * q)); this.c.height = Math.max(4, Math.ceil((y1 - y0) * q));
    this.g = this.c.getContext('2d', CPU_RASTER ? { willReadFrequently: true } : undefined); this.g.setTransform(q, 0, 0, q, -x0 * q, -y0 * q);
    this.R = rng(seed); this.n = valueNoise2D(seed * 7 + 3); this.seed = seed;
  }
  get area() { const [x0, y0, x1, y1] = this.rect; return (x1 - x0) * (y1 - y0); }
  // tapered brush dab along a gently bent centreline (blunt start, tapered tail, like a loaded brush lifting off)
  dab(x, y, ang, len, wid, col, a, bend = 0, taper = 0.6) {
    const g = this.g, ca = Math.cos(ang), sa = Math.sin(ang), hx = ca * len * 0.5, hy = sa * len * 0.5;
    const p0x = x - hx, p0y = y - hy, p2x = x + hx, p2y = y + hy, cx = x - sa * bend * len, cy = y + ca * bend * len; const N = 7;
    const Lx = new Float32Array(N + 1), Ly = new Float32Array(N + 1), Rx = new Float32Array(N + 1), Ry = new Float32Array(N + 1);
    for (let i = 0; i <= N; i++) {
      const s = i / N, m = 1 - s; const px = m * m * p0x + 2 * m * s * cx + s * s * p2x, py = m * m * p0y + 2 * m * s * cy + s * s * p2y;
      const tx = 2 * m * (cx - p0x) + 2 * s * (p2x - cx), ty = 2 * m * (cy - p0y) + 2 * s * (p2y - cy); const tl = Math.hypot(tx, ty) || 1;
      const prof = Math.pow(Math.min(1, (s + 0.08) / 0.3), 0.5) * Math.pow(1 - s * 0.97, taper); const w = wid * 0.5 * prof;
      Lx[i] = px - ty / tl * w; Ly[i] = py + tx / tl * w; Rx[i] = px + ty / tl * w; Ry[i] = py - tx / tl * w;
    }
    g.fillStyle = rgba(col, a); g.beginPath(); g.moveTo(Lx[0], Ly[0]); for (let i = 1; i <= N; i++) g.lineTo(Lx[i], Ly[i]); for (let i = N; i >= 0; i--) g.lineTo(Rx[i], Ry[i]); g.closePath(); g.fill();
  }
  // stratified, shuffled stroke field. color(x,y,m) -> rgb|null, angle(x,y) -> rad, mask(x,y) -> 0..1
  strokes({ n, box = null, mask = null, minMask = 0.5, color, angle, len, wid, alpha, jv = 0.05, bend = 0.15, taper = 0.6, aMul = null, sizeMul = null }) {
    const [bx0, by0, bx1, by1] = box || this.rect; const w = bx1 - bx0, h = by1 - by0; if (w <= 0 || h <= 0 || n < 1) return;
    const cols = Math.max(1, Math.round(Math.sqrt(n * w / h))), rows = Math.max(1, Math.round(n / cols)), cw = w / cols, rh = h / rows, R = this.R;
    const idx = new Uint32Array(cols * rows); for (let i = 0; i < idx.length; i++) idx[i] = i;
    for (let i = idx.length - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); const t = idx[i]; idx[i] = idx[j]; idx[j] = t; }
    for (let k = 0; k < idx.length; k++) {
      const i = idx[k] % cols, j = (idx[k] / cols) | 0; const x = bx0 + (i + R()) * cw, y = by0 + (j + R()) * rh;
      const r1 = R(), r2 = R(), r3 = R(), r4 = R(), r5 = R(), gg = R.gauss();
      const mv = mask ? mask(x, y) : 1; if (mv < minMask) continue;
      const c0 = color(x, y, mv); if (!c0) continue; const v = 1 + jv * gg;
      const sm = sizeMul ? sizeMul(x, y) : 1; const am = aMul ? aMul(x, y, mv) : 1; if (am <= 0.003) continue;
      this.dab(x, y, angle(x, y), lerp(len[0], len[1], r1) * sm, lerp(wid[0], wid[1], r2) * sm, [c0[0] * v, c0[1] * v, c0[2] * v], lerp(alpha[0], alpha[1], r3) * am, (r4 - 0.5) * 2 * bend, taper + (r5 - 0.5) * 0.3);
    }
  }
  // rasterised mask from a draw callback (fill white); returns lookup in design px -> 0..1
  mask(draw) {
    const c = document.createElement('canvas'); c.width = this.c.width; c.height = this.c.height; const g = c.getContext('2d', { willReadFrequently: true });
    g.setTransform(this.q, 0, 0, this.q, -this.rect[0] * this.q, -this.rect[1] * this.q); g.fillStyle = '#fff'; g.strokeStyle = '#fff'; draw(g);
    const d = g.getImageData(0, 0, c.width, c.height).data; const W = c.width, H = c.height, q = this.q, x0 = this.rect[0], y0 = this.rect[1];
    const a = new Uint8Array(W * H); for (let i = 0; i < a.length; i++) a[i] = d[i * 4 + 3];
    const f = (x, y) => { const X = ((x - x0) * q) | 0, Y = ((y - y0) * q) | 0; return (X < 0 || Y < 0 || X >= W || Y >= H) ? 0 : a[Y * W + X] / 255; };
    f.canvas = c; return f;
  }
  blur(px) { const c = document.createElement('canvas'); c.width = this.c.width; c.height = this.c.height; const g = c.getContext('2d'); g.filter = `blur(${px * this.q}px)`; g.drawImage(this.c, 0, 0);
    const o = this.g; o.save(); o.setTransform(1, 0, 0, 1, 0, 0); o.clearRect(0, 0, c.width, c.height); o.drawImage(c, 0, 0); o.restore(); }
  // coarse paper/pigment mottling (only where paint exists)
  mottle({ cell = 18, amt = 0.08, seed = 5, light = [255, 244, 230], dark = [8, 6, 20] } = {}) {
    const w = Math.ceil(this.c.width / cell) + 2, h = Math.ceil(this.c.height / cell) + 2; const n = valueNoise2D(seed + this.seed * 13);
    for (const [col, sign] of [[dark, -1], [light, 1]]) {
      const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); const img = g.createImageData(w, h); const d = img.data;
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const v = (n.fbm(x * 0.21 + sign * 9.3, y * 0.21, 4) - 0.5) * 2 * sign; const i = (y * w + x) * 4; d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = Math.round(clamp(v * 1.6) * amt * 255); }
      g.putImageData(img, 0, 0); const o = this.g; o.save(); o.setTransform(1, 0, 0, 1, 0, 0); o.globalCompositeOperation = 'source-atop'; o.imageSmoothingEnabled = true; o.drawImage(c, -cell, -cell, w * cell, h * cell); o.restore();
    }
  }
}

// smooth underpainting: colour field sampled on a coarse grid, upscaled with smoothing, optionally clipped to a path
export function underpaint(C, colAt, clip = null, cell = 6, box = null) {
  const [x0, y0, x1, y1] = box || C.rect; const w = Math.ceil((x1 - x0) / cell) + 3, h = Math.ceil((y1 - y0) / cell) + 3;
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); const img = g.createImageData(w, h); const d = img.data;
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const col = colAt(x0 + (i - 1.5) * cell, y0 + (j - 1.5) * cell); const k = (j * w + i) * 4; d[k] = clamp(col[0], 0, 255); d[k + 1] = clamp(col[1], 0, 255); d[k + 2] = clamp(col[2], 0, 255); d[k + 3] = 255; }
  g.putImageData(img, 0, 0); const o = C.g; o.save(); if (clip) o.clip(clip); o.imageSmoothingEnabled = true; o.imageSmoothingQuality = 'high'; o.drawImage(c, x0 - 2 * cell, y0 - 2 * cell, w * cell, h * cell); o.restore();
}
// ridged 1D noise (sharp crests) for mountain silhouettes: returns 0..1
const _rn = valueNoise2D(4242);
export const ridged = (x, oct = 4, seed = 0) => { let s = 0, a = 0.5, f = 1, n = 0; for (let i = 0; i < oct; i++) { const v = 1 - Math.abs(2 * _rn(x * f + seed * 13.7, 5.5 + i * 3.1 + seed) - 1); s += a * v * v; n += a; a *= 0.5; f *= 2.03; } return s / n; };

// ------------------------------------------------------------------ sky
// P: { stops:[[y,rgb]...], glow:{x,y,rx,ry,col,a}, clouds:[{y,h,x0,x1,col,lit,thr,sx,sy}] , n:density }
export function paintSky(C, P) {
  const [x0, y0, x1, y1] = C.rect; const g = C.g;
  const colAt = (x, y) => { let c = ramp(P.stops, y); if (P.glow) { const gl = P.glow; const d2 = ((x - gl.x) / gl.rx) ** 2 + ((y - gl.y) / gl.ry) ** 2; c = mixc(c, gl.col, gl.a * Math.exp(-d2)); } return c; };
  underpaint(C, colAt, null, 8);
  const A = C.area * (P.n || 1); const wave = (x, y) => 0.05 * Math.sin(x * 0.0045 + y * 0.012) + 0.03 * Math.sin(x * 0.011 - y * 0.02);
  C.strokes({ n: A / 2600, color: colAt, angle: (x, y) => wave(x, y) + (C.R() - 0.5) * 0.1, len: [90, 190], wid: [16, 28], alpha: [0.35, 0.6], jv: 0.03, bend: 0.05, taper: 0.45 });
  C.strokes({ n: A / 1500, color: colAt, angle: (x, y) => wave(x, y) + (C.R() - 0.5) * 0.16, len: [36, 90], wid: [9, 16], alpha: [0.3, 0.55], jv: 0.04, bend: 0.1 });
  for (const cl of P.clouds || []) {
    const n = C.n; const thr = cl.thr ?? 0.52;
    const m = (x, y) => { const e = Math.exp(-(((y - cl.y) / cl.h) ** 2)) * smoothstep(cl.x0, cl.x0 + 160, x) * (1 - smoothstep(cl.x1 - 160, cl.x1, x));
      return e * smoothstep(thr, thr + 0.16, n.fbm(x * (cl.sx || 0.0032), y * (cl.sy || 0.016) + cl.y * 0.01, 4)); };
    const cc = (x, y, mv) => { const t = clamp((y - (cl.y - cl.h)) / (2 * cl.h)); return mixc(mixc(colAt(x, y), cl.col, 0.55 + 0.35 * mv), cl.lit, smoothstep(0.5, 1.0, t) * (cl.litA ?? 0.7)); };
    C.strokes({ n: (cl.x1 - cl.x0) * cl.h * 2 / 420, box: [cl.x0, cl.y - cl.h * 1.6, cl.x1, cl.y + cl.h * 1.6], mask: m, minMask: 0.08, color: cc, angle: (x, y) => wave(x, y) * 0.6 + (C.R() - 0.5) * 0.08 + (cl.tilt || 0),
      len: [50, 140], wid: [8, 16], alpha: [0.4, 0.75], aMul: (x, y, mv) => smoothstep(0.05, 0.5, mv), jv: 0.05, bend: 0.06, taper: 0.5 });
    C.strokes({ n: (cl.x1 - cl.x0) * cl.h * 2 / 650, box: [cl.x0, cl.y - cl.h * 1.4, cl.x1, cl.y + cl.h * 1.4], mask: m, minMask: 0.3, color: cc, angle: (x, y) => wave(x, y) * 0.6 + (C.R() - 0.5) * 0.12 + (cl.tilt || 0),
      len: [20, 50], wid: [5, 9], alpha: [0.45, 0.8], jv: 0.06, bend: 0.1 });
  }
  return colAt;
}

// ------------------------------------------------------------------ mountain range
// P: { ridge:x=>y, top, mid, base, fall, light:{dir,col,amt}, shade, haze:{col,y0,y1,a}, snow:{y,col,amt}, sizes:k, n }
export function paintRange(C, P) {
  const [x0, y0, x1, y1] = C.rect; const g = C.g, n = C.n, k = P.sizes || 1;
  const path = new Path2D(); path.moveTo(x0 - 20, y1 + 20); for (let x = x0 - 20; x <= x1 + 20; x += 2) path.lineTo(x, P.ridge(x)); path.lineTo(x1 + 20, y1 + 20); path.closePath();
  const m = C.mask((gg) => gg.fill(path));
  const slope = (x) => (P.ridge(x + 4) - P.ridge(x - 4)) / 8; const dir = P.light ? P.light.dir : -1;
  const R0 = x0 - 120, STP = 4, NS = Math.ceil((x1 - x0 + 240) / STP); const tab = new Float32Array(NS + 2);
  for (let i = 0; i <= NS + 1; i++) { let s = 0; for (let k = -16; k <= 16; k++) s += P.ridge(R0 + (i + k) * STP); tab[i] = s / 33; }
  const ridgeS = (x) => { const u = clamp((x - R0) / STP, 0, NS); const i = Math.floor(u), f = u - i; return tab[i] * (1 - f) + tab[i + 1] * f; };
  const facet = (x, y) => clamp(slope(x) * dir * 1.6 * (1 - smoothstep(0, 70, y - P.ridge(x))) + (n.fbm(x * 0.0085 + y * 0.0055 * dir, y * 0.0085 - x * 0.0035, 4) - 0.5) * 1.9 + 0.08, -1, 1);
  const colAt = (x, y) => {
    const d = clamp((y - ridgeS(x)) / (P.fall || 240)); let c = ramp([[0, P.top], [0.45, P.mid], [1, P.base]], d);
    if (P.light) { const f = facet(x, y); const lit = smoothstep(0.05, 0.55, f); c = mixc(c, P.light.col, lit * P.light.amt * (1 - 0.55 * d)); c = mul(c, 1 - (P.shade || 0.12) * smoothstep(0.1, -0.5, f)); }
    if (P.snow) { const sn = smoothstep(P.snow.y + 25, P.snow.y - 25, y + (n.fbm(x * 0.02, y * 0.02, 3) - 0.5) * 60) * smoothstep(0.48, 0.62, n.fbm(x * 0.017 - y * 0.011 * dir, y * 0.02 + x * 0.006 + 40, 4)) * (0.55 + 0.45 * smoothstep(-0.2, 0.4, facet(x, y)));
      c = mixc(c, P.snow.col, sn * (P.snow.amt ?? 0.85)); }
    if (P.haze) c = mixc(c, P.haze.col, smoothstep(P.haze.y0, P.haze.y1, y) * (P.haze.a ?? 1));
    return c;
  };
  underpaint(C, colAt, path, 5);
  // strokes follow the slope planes: along the crest near the top, then diagonals down each facet (lit facets one way,
  // shadowed the other), never vertical, so the Kuwahara pass reads them as planes rather than slats
  const ang = (x, y) => { const d = clamp((y - P.ridge(x)) / 50); const along = Math.atan(slope(x)); const f = facet(x, y); const diag = 0.75 * dir * Math.sign(f || 1) + (nn3(x, y) - 0.5) * 0.5; return lerp(along, diag, smoothstep(0.15, 0.85, d)) + (C.R() - 0.5) * 0.3; };
  const nn3 = (x, y) => n.fbm(x * 0.02 + 7, y * 0.02, 2);
  const A = C.area * (P.n || 1);
  C.strokes({ n: A / 1500, mask: m, color: colAt, angle: ang, len: [22 * k, 56 * k], wid: [9 * k, 17 * k], alpha: [0.4, 0.7], jv: 0.045, bend: 0.14 });
  C.strokes({ n: A / 1100, mask: m, minMask: 0.6, color: colAt, angle: ang, len: [10 * k, 28 * k], wid: [5 * k, 10 * k], alpha: [0.45, 0.8], jv: 0.06, bend: 0.18 });
  // ridge rim on light-facing slopes (afterglow catching the crest)
  if (P.rim) for (let x = x0; x < x1; x += 3 + C.R() * 5) { const s = slope(x) * dir; if (s < 0.06 + C.R() * 0.2) continue; C.dab(x, P.ridge(x) + 2.5 + C.R() * 3, Math.atan(slope(x)), (8 + C.R() * 18) * k, (2.5 + C.R() * 3) * k, P.rim, 0.5 + C.R() * 0.35, 0.05); }
  return { colAt, mask: m };
}

// ------------------------------------------------------------------ pines (fbm-broken painted silhouettes)
export function pineTree(C, x, yb, h, col, { rim = null, rimSide = -1, wr = 0.36, tierPx = 8, lean = 0 } = {}) {
  const g = C.g, R = C.R; const w = h * wr * (0.85 + R() * 0.3); const tiers = Math.max(3, Math.round(h / tierPx));
  g.fillStyle = rgba(mul(col, 0.85)); g.fillRect(x - Math.max(0.6, h * 0.012), yb - h * 0.3, Math.max(1.2, h * 0.024), h * 0.3);
  const topX = x + lean * h;
  for (let k = 0; k < tiers; k++) {
    const u0 = k / tiers, u1 = Math.min(1, (k + 1.7) / tiers); const yA = yb - h + u0 * h * 0.9, yB = yb - h + u1 * h * 0.9 - h * 0.02; const cxk = lerp(topX, x, u0);
    const ww = w * (0.12 + 0.88 * Math.pow(u1, 0.85)) * (0.8 + R() * 0.35) * 0.5; const droop = (yB - yA) * (0.18 + R() * 0.15);
    const c = mul(col, 0.9 + R() * 0.2); g.fillStyle = rgba(c); g.beginPath(); g.moveTo(cxk + (R() - 0.5), yA - 1);
    const zz = 4; for (let i = 1; i <= zz; i++) { const u = i / zz; g.lineTo(cxk - ww * u + (i % 2 ? -1 : 1) * ww * 0.12 * R(), yA + (yB - yA) * u * 0.85 + (i % 2 ? droop * 0.4 : -droop * 0.2)); }
    g.lineTo(cxk - ww * (1.05 + R() * 0.1), yB + droop); const bz = 6; for (let i = 1; i < bz; i++) { const u = i / bz; g.lineTo(cxk - ww + 2 * ww * u, yB + (i % 2 ? -1 : 0.4) * (yB - yA) * 0.18 * (0.5 + R())); }
    g.lineTo(cxk + ww * (1.05 + R() * 0.1), yB + droop); for (let i = zz - 1; i >= 1; i--) { const u = i / zz; g.lineTo(cxk + ww * u + (i % 2 ? 1 : -1) * ww * 0.12 * R(), yA + (yB - yA) * u * 0.85 + (i % 2 ? droop * 0.4 : -droop * 0.2)); }
    g.closePath(); g.fill();
    if (rim && R() < 0.85) { const side = rimSide; C.dab(cxk + side * ww * (0.45 + R() * 0.3), yA + (yB - yA) * (0.45 + R() * 0.3), side < 0 ? -2.3 + R() * 0.3 : -0.8 + R() * 0.3, Math.max(2.5, ww * 0.9), Math.max(1.2, h * 0.025), rim, 0.35 + R() * 0.35, 0.1); }
  }
}
// a ridge band of pines: P { base:x=>y, hMin,hMax, spacing, col, ground, rim, gaps:[[a,b]], fill:true }
export function paintPineRidge(C, P) {
  const [x0, y0, x1, y1] = C.rect; const g = C.g, R = C.R, n = C.n;
  if (P.ground) { const path = new Path2D(); path.moveTo(x0 - 10, y1 + 10); for (let x = x0 - 10; x <= x1 + 10; x += 3) path.lineTo(x, P.base(x) + (n.fbm(x * 0.05, 3.3, 3) - 0.5) * 6); path.lineTo(x1 + 10, y1 + 10); path.closePath();
    g.fillStyle = rgba(P.ground); g.fill(path); const m = C.mask((gg) => gg.fill(path));
    C.strokes({ n: C.area / 900, mask: m, color: (x, y) => mixc(P.ground, P.groundLit || P.ground, smoothstep(P.base(x) + 30, P.base(x), y) * 0.6), angle: () => (C.R() - 0.5) * 0.5, len: [10, 30], wid: [4, 9], alpha: [0.4, 0.75], jv: 0.08 }); }
  const inGap = (x) => (P.gaps || []).some(([a, b]) => x > a && x < b);
  const trees = []; for (let x = x0 - 20; x < x1 + 20; x += P.spacing * (0.45 + R() * 0.9)) { if (inGap(x) && R() > (P.gapKeep || 0.08)) continue; const env = P.heightEnv ? P.heightEnv(x) : 1; if (env <= 0.02) continue; trees.push([x + (R() - 0.5) * 4, lerp(P.hMin, P.hMax, Math.pow(R(), 1.3)) * env, R()]); }
  trees.sort((a, b) => a[2] - b[2]);
  for (const [x, h, r] of trees) pineTree(C, x, P.base(x) + 2 + r * 6, h, mul(P.col, 0.85 + r * 0.3), { rim: P.rim, rimSide: P.rimSide ?? -1, tierPx: P.tierPx || Math.max(4, h / 9), lean: (R() - 0.5) * 0.04 });
}

// ------------------------------------------------------------------ fog band (soft, brushy, fbm alpha)
// P { y:x=>y (centre), h, col, top (lit upper colour), a, density, wisp }
export function paintFog(C, P) {
  const [x0, y0, x1, y1] = C.rect; const n = C.n;
  const yc = (x) => P.y(x) + (n.fbm(x * 0.0022, 9.1, 3) - 0.5) * P.h * 1.3; // the band meanders
  const dens = (x, y) => { const e = Math.exp(-(((y - yc(x)) / P.h) ** 2) * 1.5); const w = smoothstep(0.36, 0.74, n.fbm(x * (P.sx || 0.0034), y * (P.sy || 0.024), 5)); const edge = P.xEnv ? P.xEnv(x) : 1; return e * lerp(1, w, P.wisp ?? 0.85) * edge; };
  const col = (x, y) => mixc(P.col, P.top || P.col, smoothstep(yc(x) + P.h * 0.4, yc(x) - P.h, y));
  let ymin = 1e9, ymax = -1e9; for (let x = x0; x <= x1; x += 8) { const yy = P.y(x); ymin = Math.min(ymin, yy); ymax = Math.max(ymax, yy); }
  const box = [x0, ymin - P.h * 2.4, x1, ymax + P.h * 2.4]; const BA = (x1 - x0) * (box[3] - box[1]);
  C.strokes({ n: BA * (P.density || 1) / 240, box, mask: dens, minMask: 0.04, color: col, angle: (x, y) => (n.fbm(x * 0.004, y * 0.01, 2) - 0.5) * 0.35 + (C.R() - 0.5) * 0.08, len: [70, 180], wid: [9, 20], alpha: [0.05, 0.11], aMul: (x, y, m) => m * (P.a ?? 1), jv: 0.03, bend: 0.06, taper: 0.4 });
  C.strokes({ n: BA * (P.density || 1) / 380, box, mask: dens, minMask: 0.3, color: col, angle: (x, y) => (n.fbm(x * 0.004, y * 0.01, 2) - 0.5) * 0.35 + (C.R() - 0.5) * 0.12, len: [26, 80], wid: [6, 12], alpha: [0.06, 0.13], aMul: (x, y, m) => m * (P.a ?? 1), jv: 0.04, bend: 0.1 });
  if (P.blur !== 0) C.blur(P.blur ?? 2.5);
}

// ------------------------------------------------------------------ village house (gable roof, plaster walls, timber)
// returns { windows:[[x,y,w,h]], door:[x,y,w,h], roofTop:y }
export function paintHouse(C, x, yg, w, hW, P) {
  const g = C.g, R = C.R; const gable = P.gable ?? (R() < 0.3); const ov = w * (gable ? 0.17 : 0.09); const xl = x - w / 2, xr = x + w / 2, yt = yg - hW;
  const wall = mul(P.wall, 0.88 + R() * 0.2), roof = mul(P.roof, 0.88 + R() * 0.24); const sw = Math.max(1.6, w / 12); const lit = P.litLeft ?? 0.14;
  const wallStrokes = (box, mask) => C.strokes({ n: Math.max(4, (box[2] - box[0]) * (box[3] - box[1]) / 55), box, mask, color: (px, py) => mul(wall, 0.84 + 0.2 * smoothstep(box[1], box[1] + hW * 0.5, py) - 0.14 * smoothstep(yg - hW * 0.25, yg, py) + (px < x ? lit * 0.5 : -0.04)),
    angle: () => Math.PI / 2 + (C.R() - 0.5) * 0.3, len: [hW * 0.25, hW * 0.55], wid: [sw, sw * 1.8], alpha: [0.4, 0.75], jv: 0.06, bend: 0.06 });
  let roofTop;
  if (gable) { // gable end faces us: pentagon wall, dark roof plane peeking behind, barge boards along the rake
    const gh = w * (P.roofK ?? 0.55) * (0.8 + R() * 0.3), apy = yt - gh; roofTop = apy - ov * 0.6;
    g.fillStyle = rgba(roof); g.beginPath(); g.moveTo(xl - ov, yt + 1.5); g.lineTo(x, apy - ov * 0.7); g.lineTo(xr + ov, yt + 1.5); g.closePath(); g.fill();
    const wp = new Path2D(); wp.moveTo(xl, yg + 1); wp.lineTo(xl, yt); wp.lineTo(x, apy + ov * 0.25); wp.lineTo(xr, yt); wp.lineTo(xr, yg + 1); wp.closePath(); g.fillStyle = rgba(wall); g.fill(wp);
    wallStrokes([xl, apy, xr, yg], (px, py) => (py > apy + ov * 0.3 + Math.abs(px - x) * (gh / (w / 2)) && px > xl + 0.5 && px < xr - 0.5 ? 1 : 0));
    const rk = Math.atan2(gh, w / 2); const bw = Math.max(1.4, w / 15);
    C.dab((xl - ov + x) / 2, (yt + apy) / 2 - ov * 0.15, -rk, Math.hypot(w / 2 + ov, gh) * 1.02, bw, mul(roof, 0.8), 0.95, 0.0, 0.15); C.dab((xr + ov + x) / 2, (yt + apy) / 2 - ov * 0.15, rk, Math.hypot(w / 2 + ov, gh) * 1.02, bw, mul(roof, 0.75), 0.95, 0.0, 0.15);
    if (P.crest) C.dab((xl - ov + x) / 2, (yt + apy) / 2 - ov * 0.35 - bw * 0.4, -rk, Math.hypot(w / 2 + ov, gh) * 0.9, Math.max(1.1, bw * 0.5), P.crest, 0.55, 0.0, 0.3);
  } else { // eave faces us: wall rectangle under a hipped/gabled roof seen from the long side
    const roofH = w * (P.roofK ?? 0.5) * 0.62 * (0.85 + R() * 0.3), apx = x + (R() - 0.5) * w * 0.05, apy = yt - roofH; roofTop = apy;
    g.fillStyle = rgba(wall); g.fillRect(xl, yt, w, hW + 1); wallStrokes([xl + 0.5, yt, xr - 0.5, yg], null);
    const hip = w * (0.18 + R() * 0.2); g.fillStyle = rgba(roof); g.beginPath(); g.moveTo(xl - ov, yt + roofH * 0.12); g.lineTo(xl + hip, apy); g.lineTo(xr - hip, apy); g.lineTo(xr + ov, yt + roofH * 0.12); g.lineTo(xr + ov * 0.6, yt + roofH * 0.26); g.lineTo(xl - ov * 0.6, yt + roofH * 0.26); g.closePath(); g.fill();
    const rs = Math.max(1.5, w / 15);
    C.strokes({ n: Math.max(5, w * roofH / 40), box: [xl - ov, apy, xr + ov, yt + roofH * 0.2], mask: (px, py) => (py > apy && py < yt + roofH * 0.2 && px > xl - ov + (yt - py) / roofH * (hip + ov) && px < xr + ov - (yt - py) / roofH * (hip + ov)) ? 1 : 0,
      color: (px, py) => mul(roof, 0.85 + 0.35 * smoothstep(yt + roofH * 0.1, apy, py) + (px < xl + hip ? lit : 0)), angle: () => (C.R() - 0.5) * 0.25, len: [w * 0.15, w * 0.4], wid: [rs, rs * 1.6], alpha: [0.5, 0.85], jv: 0.06, bend: 0.04 });
    if (P.crest) C.dab(x, apy + 0.6, 0, (w - 2 * hip) * 1.02, Math.max(1.1, w / 30), P.crest, 0.6, 0.0, 0.25);
  }
  if (P.sideShade) { g.fillStyle = rgba(mul(wall, 0.6), 0.5); g.fillRect(P.sideShade > 0 ? x + w * 0.2 : xl, yt, w * 0.3, hW); }
  g.fillStyle = rgba(mul(P.roof, 0.85)); const pw = Math.max(1.2, w / 20); g.fillRect(xl - 0.4, yt, pw, hW); g.fillRect(xr - pw + 0.4, yt, pw, hW); // timber corner posts
  if (R() < 0.45 && w > 14) { const cx = x + (R() - 0.5) * w * 0.5, cw = Math.max(1.6, w * 0.08); g.fillStyle = rgba(mul(roof, 0.9)); g.fillRect(cx - cw / 2, roofTop - w * 0.1, cw, w * 0.16); }
  // windows (dark, 0 to 2) + door
  const wins = []; const nw = w > 60 ? 2 : (R() < 0.8 ? 1 : 0); const ww = Math.max(3, w * 0.19), wh = Math.max(3.5, hW * 0.34);
  for (let i = 0; i < nw; i++) { const wx = nw === 1 ? x + (R() - 0.5) * w * 0.3 - ww / 2 : xl + w * (0.18 + 0.48 * i) + (R() - 0.5) * 2; const wy = yt + hW * (0.2 + R() * 0.1); g.fillStyle = rgba(P.win || [20, 18, 30]); g.fillRect(wx, wy, ww, wh); wins.push([wx, wy, ww, wh]); }
  let door = null; if (w > 16 && R() < 0.75) { const dw = Math.max(2.4, w * 0.15), dh = hW * 0.6; const dx = x + (R() < 0.5 ? -1 : 1) * w * 0.24 - dw / 2; g.fillStyle = rgba(mul(P.win || [20, 18, 30], 1.1)); g.fillRect(dx, yg - dh, dw, dh); door = [dx, yg - dh, dw, dh]; }
  return { windows: wins, door, roofTop, eave: yt };
}

// ------------------------------------------------------------------ out-of-focus foreground rock mass
export function paintRocks(C, P) {
  const g = C.g, R = C.R, n = C.n; const [x0, y0, x1, y1] = C.rect;
  for (const r of P.rocks) {
    const path = new Path2D(); const N = 28; for (let i = 0; i <= N; i++) { const a = Math.PI * 2 * i / N; const rr = 1 + (n.fbm(Math.cos(a) * 1.3 + r.x * 0.01, Math.sin(a) * 1.3, 3) - 0.5) * 0.7; const px = r.x + Math.cos(a) * r.rx * rr, py = r.y + Math.sin(a) * r.ry * rr * (Math.sin(a) > 0 ? 1.6 : 1); i ? path.lineTo(px, py) : path.moveTo(px, py); }
    path.closePath(); g.fillStyle = rgba(P.col); g.fill(path); const m = C.mask((gg) => gg.fill(path));
    // soft sky-lit top edge (gradient inside the silhouette), then short low-contrast dabs for surface, no long streaks
    g.save(); g.clip(path); const lg = g.createLinearGradient(r.x - r.rx * 0.4, r.y - r.ry * 1.05, r.x + r.rx * 0.2, r.y - r.ry * 0.35); lg.addColorStop(0, rgba(P.lit, P.litA ?? 0.5)); lg.addColorStop(1, rgba(P.lit, 0)); g.fillStyle = lg; g.fillRect(r.x - r.rx * 1.5, r.y - r.ry * 1.5, r.rx * 3, r.ry * 3); g.restore();
    C.strokes({ n: r.rx * r.ry / 160, box: [r.x - r.rx * 1.3, r.y - r.ry * 1.3, r.x + r.rx * 1.3, r.y + r.ry * 1.8], mask: m, minMask: 0.7, color: (x, y) => mixc(P.col, P.lit, smoothstep(r.y - r.ry * 0.2, r.y - r.ry, y) * 0.22),
      angle: () => -0.4 + (C.R() - 0.5) * 1.2, len: [r.rx * 0.08, r.rx * 0.2], wid: [r.rx * 0.05, r.rx * 0.1], alpha: [0.35, 0.6], jv: 0.06, bend: 0.2 });
  }
  if (P.blur) C.blur(P.blur);
}

// ------------------------------------------------------------------ pine bough (out of focus foreground)
export function paintBough(C, P) {
  const g = C.g, R = C.R; const pts = P.pts; g.strokeStyle = rgba(P.col); g.lineCap = 'round';
  for (let i = 0; i < pts.length - 1; i++) { g.lineWidth = lerp(P.w0, P.w1, i / (pts.length - 1)); g.beginPath(); g.moveTo(pts[i][0], pts[i][1]); g.lineTo(pts[i + 1][0], pts[i + 1][1]); g.stroke(); }
  // needle clusters along the bough: fans of dark strokes drooping, a few cool-lit tips
  for (let i = 0; i < pts.length - 1; i++) for (let s = 0; s < 1; s += 0.08 + R() * 0.06) {
    const x = lerp(pts[i][0], pts[i + 1][0], s), y = lerp(pts[i][1], pts[i + 1][1], s); const sz = lerp(P.n0, P.n1, (i + s) / (pts.length - 1));
    for (let k = 0; k < 9; k++) { const a = Math.PI / 2 + (R() - 0.5) * 2.6; C.dab(x + Math.cos(a) * sz * 0.4, y + Math.sin(a) * sz * 0.4 + sz * 0.15, a, sz * (0.6 + R() * 0.6), sz * 0.16, mul(P.col, 0.8 + R() * 0.4), 0.85, 0.15); }
    if (P.lit && R() < 0.5) C.dab(x - sz * 0.2, y - sz * 0.25, -2.4 + R() * 0.6, sz * 0.5, sz * 0.12, P.lit, 0.4, 0.1);
  }
  if (P.blur) C.blur(P.blur);
}

// ------------------------------------------------------------------ grass / brush tufts along a line
export function paintTufts(C, P) {
  const R = C.R; for (let x = P.x0; x < P.x1; x += P.step * (0.4 + R())) { const yb = P.base(x) + R() * (P.jitter || 3); const h = lerp(P.h0, P.h1, R());
    for (let k = 0; k < (P.blades || 5); k++) { const a = -Math.PI / 2 + (R() - 0.5) * 0.9 + (P.lean || 0); C.dab(x + (R() - 0.5) * h * 0.3 + Math.cos(a) * h * 0.45, yb + Math.sin(a) * h * 0.45, a, h * (0.6 + R() * 0.5), Math.max(1.2, h * 0.09), mul(P.col, 0.8 + R() * 0.4), 0.7 + R() * 0.3, 0.12, 0.9); } }
}
