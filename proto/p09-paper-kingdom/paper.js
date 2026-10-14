// paper.js — cut-paper toolkit for P09 PAPER KINGDOM (deterministic: seeded rng only, no Math.random / Date).
// Shapes are authored as absolute SVG-ish paths (M L Q C Z), sampled to polylines and given a FIXED hand-cut wobble
// (scissor) or a fibrous tear, once at init — so edges never boil. Textures are built once; patterns are filled in the
// part's own transform, so fibres travel with the puppet (no texture swim).
import { rng, lerp, clamp, noise1, valueNoise2D } from '/harness/kit/film.js';

export const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
// CPU-raster 2D contexts: on SwiftShader the GPU 2D path executes clips/blurs very slowly; Skia's CPU raster is far faster
export const ctx2d = (c) => c.getContext('2d', { willReadFrequently: true });
export const VIEW = { dpr: 1, light: [-0.72, 0.69] }; // device px per authoring px; screen-space direction AWAY from the lamp (down-left)
export const rgb = (c, a = 1) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
export const mixc = (A, B, k) => A.map((v, j) => lerp(v, B[j], k));

// ------------------------------------------------------------------ path language → closed polylines
export function parse(d) {
  const tk = d.match(/[MLQCZ]|-?\d*\.?\d+/g); const subs = []; let cur = null, i = 0, cmd = '', x = 0, y = 0;
  const n = () => +tk[i++];
  while (i < tk.length) {
    if (/[MLQCZ]/.test(tk[i])) cmd = tk[i++];
    if (cmd === 'M') { x = n(); y = n(); cur = [[x, y]]; subs.push(cur); cmd = 'L'; }
    else if (cmd === 'L') { x = n(); y = n(); cur.push([x, y]); }
    else if (cmd === 'Q') {
      const a = n(), b = n(), e = n(), f = n(); const k = Math.max(4, Math.ceil((Math.hypot(a - x, b - y) + Math.hypot(e - a, f - b)) / 5));
      for (let j = 1; j <= k; j++) { const t = j / k, m = 1 - t; cur.push([m * m * x + 2 * m * t * a + t * t * e, m * m * y + 2 * m * t * b + t * t * f]); }
      x = e; y = f;
    } else if (cmd === 'C') {
      const a = n(), b = n(), c = n(), dd = n(), e = n(), f = n();
      const L = Math.hypot(a - x, b - y) + Math.hypot(c - a, dd - b) + Math.hypot(e - c, f - dd); const k = Math.max(5, Math.ceil(L / 5));
      for (let j = 1; j <= k; j++) { const t = j / k, m = 1 - t; cur.push([m * m * m * x + 3 * m * m * t * a + 3 * m * t * t * c + t * t * t * e, m * m * m * y + 3 * m * m * t * b + 3 * m * t * t * dd + t * t * t * f]); }
      x = e; y = f;
    } else if (cmd === 'Z') { cmd = ''; }
    else i++;
  }
  return subs;
}
export const circle = (cx, cy, r, n = 0) => {
  n = n || Math.max(14, Math.ceil(r * 1.1)); let s = '';
  for (let k = 0; k < n; k++) { const a = k / n * 2 * Math.PI; s += (k ? 'L ' : 'M ') + (cx + r * Math.cos(a)).toFixed(2) + ' ' + (cy + r * Math.sin(a)).toFixed(2) + ' '; }
  return s + 'Z ';
};
export const ellipse = (cx, cy, rx, ry, rot = 0, n = 28) => {
  let s = ''; const c = Math.cos(rot), si = Math.sin(rot);
  for (let k = 0; k < n; k++) { const a = k / n * 2 * Math.PI, x = rx * Math.cos(a), y = ry * Math.sin(a); s += (k ? 'L ' : 'M ') + (cx + x * c - y * si).toFixed(2) + ' ' + (cy + x * si + y * c).toFixed(2) + ' '; }
  return s + 'Z ';
};
export const poly = (pts) => 'M ' + pts.map((p) => p[0].toFixed(2) + ' ' + p[1].toFixed(2)).join(' L ') + ' Z ';

function densify(P, step) {
  const Q = P.length > 2 && Math.hypot(P[0][0] - P[P.length - 1][0], P[0][1] - P[P.length - 1][1]) < 1e-6 ? P.slice(0, -1) : P;
  const out = []; const N = Q.length;
  for (let k = 0; k < N; k++) {
    const a = Q[k], b = Q[(k + 1) % N]; const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / step));
    for (let j = 0; j < n; j++) out.push([lerp(a[0], b[0], j / n), lerp(a[1], b[1], j / n)]);
  }
  return out;
}
// a cut paper piece. amp/freq = slow scissor wobble, hf = small waver, fib = per-vertex fibre noise. rule 'evenodd' for holes.
export function cut(d, o = {}) {
  const { seed = 1, step = 3.5, amp = 0.5, freq = 0.045, hf = 0.22, fib = 0.3, rule = 'nonzero' } = o;
  const r = rng(seed * 7919 + 13); const subs = [];
  parse(d).forEach((P, si) => {
    const D = densify(P, step); const N = D.length; const out = []; let s = 0;
    for (let k = 0; k < N; k++) {
      const a = D[(k - 1 + N) % N], b = D[(k + 1) % N]; let tx = b[0] - a[0], ty = b[1] - a[1]; const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
      if (k) s += Math.hypot(D[k][0] - D[k - 1][0], D[k][1] - D[k - 1][1]);
      const off = amp * noise1(s * freq, seed * 1.37 + si) + hf * noise1(s * freq * 5.7, seed * 0.71 + 3 + si) + fib * (r() - 0.5);
      out.push([D[k][0] - ty * off, D[k][1] + tx * off]);
    }
    subs.push(out);
  });
  const p = new Path2D(); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (const P of subs) { p.moveTo(P[0][0], P[0][1]); for (let k = 1; k < P.length; k++) p.lineTo(P[k][0], P[k][1]); p.closePath(); for (const q of P) { x0 = Math.min(x0, q[0]); y0 = Math.min(y0, q[1]); x1 = Math.max(x1, q[0]); y1 = Math.max(y1, q[1]); } }
  return { p, rule, subs, bb: [x0, y0, x1, y1] };
}
export const torn = (d, o = {}) => cut(d, { amp: 2.0, freq: 0.06, hf: 1.1, fib: 1.3, step: 2.2, ...o });

// ------------------------------------------------------------------ drawing a piece: fill, fibre pattern (local space), lit edge
export function rim(g, sh, style, w = 1.4) {
  const m = g.getTransform(), det = m.a * m.d - m.b * m.c; if (Math.abs(det) < 1e-12) return;
  const sx = VIEW.light[0] * w * VIEW.dpr, sy = VIEW.light[1] * w * VIEW.dpr;              // device-space shift toward the shadow side
  const lx = (m.d * sx - m.c * sy) / det, ly = (-m.b * sx + m.a * sy) / det;                // the same shift in the piece's local space
  const [x0, y0, x1, y1] = sh.bb, mg = Math.abs(lx) + Math.abs(ly) + 4;
  g.save(); g.clip(sh.p, sh.rule);
  const inv = new Path2D(); inv.rect(x0 - mg, y0 - mg, x1 - x0 + 2 * mg, y1 - y0 + 2 * mg); inv.addPath(sh.p, new DOMMatrix([1, 0, 0, 1, lx, ly]));
  g.clip(inv, 'evenodd'); g.fillStyle = style; g.fillRect(x0 - mg, y0 - mg, x1 - x0 + 2 * mg, y1 - y0 + 2 * mg); g.restore();
}
export function piece(g, sh, { fill, tex = null, rimStyle = null, rimW = 1.4, alpha = 1 } = {}) {
  if (alpha !== 1) g.globalAlpha = alpha;
  g.fillStyle = fill; g.fill(sh.p, sh.rule);
  if (tex) { g.fillStyle = tex; g.fill(sh.p, sh.rule); }
  if (alpha !== 1) g.globalAlpha = 1;
  if (rimStyle) rim(g, sh, rimStyle, rimW);
}

// ------------------------------------------------------------------ textures (built once)
function tileValue(N, cells, seed) {
  const r = rng(seed); const G = new Float32Array(cells * cells); for (let k = 0; k < G.length; k++) G[k] = r();
  const out = new Float32Array(N * N); const fade = (t) => t * t * (3 - 2 * t);
  for (let y = 0; y < N; y++) {
    const fy = y / N * cells, Y = Math.floor(fy), v = fade(fy - Y), y0 = (Y % cells) * cells, y1 = ((Y + 1) % cells) * cells;
    for (let x = 0; x < N; x++) {
      const fx = x / N * cells, X = Math.floor(fx), u = fade(fx - X), x0 = X % cells, x1 = (X + 1) % cells;
      out[y * N + x] = lerp(lerp(G[y0 + x0], G[y0 + x1], u), lerp(G[y1 + x0], G[y1 + x1], u), v);
    }
  }
  return out;
}
export function tileFbm(N, base, oct, seed, gain = 0.55) {
  const out = new Float32Array(N * N); let norm = 0, a = 1;
  for (let o = 0; o < oct; o++) { const v = tileValue(N, base << o, seed + o * 101); for (let k = 0; k < out.length; k++) out[k] += v[k] * a; norm += a; a *= gain; }
  for (let k = 0; k < out.length; k++) out[k] /= norm; return out;
}
// curly fibres drawn with wrap-around (tileable)
function fibres(g, N, count, seed, colorFn, wMin = 0.4, wMax = 1.1, lMin = 8, lMax = 40) {
  const r = rng(seed); g.lineCap = 'round';
  for (let k = 0; k < count; k++) {
    const x = r() * N, y = r() * N, a = r() * Math.PI * 2, L = lMin + r() * (lMax - lMin), b1 = (r() - 0.5) * 1.6, b2 = (r() - 0.5) * 1.6;
    g.strokeStyle = colorFn(r); g.lineWidth = wMin + r() * (wMax - wMin);
    for (const ox of [-N, 0, N]) for (const oy of [-N, 0, N]) {
      const x0 = x + ox, y0 = y + oy; if (x0 < -lMax || x0 > N + lMax || y0 < -lMax || y0 > N + lMax) continue;
      g.beginPath(); g.moveTo(x0, y0);
      g.bezierCurveTo(x0 + Math.cos(a + b1) * L * 0.35, y0 + Math.sin(a + b1) * L * 0.35, x0 + Math.cos(a + b2) * L * 0.7, y0 + Math.sin(a + b2) * L * 0.7, x0 + Math.cos(a) * L, y0 + Math.sin(a) * L);
      g.stroke();
    }
  }
}
// opaque transmission texture for translucent (multiply) paper: colour T, cloudy density + darker fibres
export function transTex(N, T, seed, { mott = 0.3, fib = 260 } = {}) {
  const c = mk(N, N), g = ctx2d(c), img = g.createImageData(N, N), d = img.data;
  const m = tileFbm(N, 4, 4, seed), t = tileFbm(N, 64, 2, seed + 7);
  for (let k = 0; k < N * N; k++) { const v = 1 - mott * 0.5 + mott * m[k] + (t[k] - 0.5) * 0.08; d[k * 4] = T[0] * v; d[k * 4 + 1] = T[1] * v; d[k * 4 + 2] = T[2] * v; d[k * 4 + 3] = 255; }
  g.putImageData(img, 0, 0);
  fibres(g, N, fib, seed + 3, (r) => `rgba(${T[0] * 0.55 | 0},${T[1] * 0.5 | 0},${T[2] * 0.45 | 0},${0.12 + 0.22 * r()})`, 0.5, 1.3, 10, 46);
  fibres(g, N, fib * 0.4, seed + 5, (r) => `rgba(${Math.min(255, T[0] * 1.25) | 0},${Math.min(255, T[1] * 1.22) | 0},${Math.min(255, T[2] * 1.2) | 0},${0.10 + 0.15 * r()})`, 0.5, 1.0, 8, 30);
  return c;
}
// alpha texture laid OVER opaque near-black pieces: faint warm fibres and mottling (the paper's own surface)
export function surfTex(N, C, seed, a0 = 0.05) {
  const c = mk(N, N), g = ctx2d(c), img = g.createImageData(N, N), d = img.data; const m = tileFbm(N, 4, 4, seed);
  for (let k = 0; k < N * N; k++) { d[k * 4] = C[0]; d[k * 4 + 1] = C[1]; d[k * 4 + 2] = C[2]; d[k * 4 + 3] = 255 * a0 * clamp(m[k] * 1.6 - 0.3); }
  g.putImageData(img, 0, 0);
  fibres(g, N, 120, seed + 1, (r) => `rgba(${C[0]},${C[1]},${C[2]},${0.05 + 0.08 * r()})`, 0.4, 0.9, 8, 34);
  return c;
}
// lit-edge texture: the rim colour with a broken, fibrous alpha
export function rimTex(N, C, seed) {
  const c = mk(N, N), g = ctx2d(c), img = g.createImageData(N, N), d = img.data; const m = tileFbm(N, 16, 3, seed), f = tileFbm(N, 64, 1, seed + 9);
  for (let k = 0; k < N * N; k++) { const a = clamp(0.35 + 0.9 * m[k] + 0.5 * (f[k] - 0.5)); d[k * 4] = C[0]; d[k * 4 + 1] = C[1]; d[k * 4 + 2] = C[2]; d[k * 4 + 3] = 255 * a; }
  g.putImageData(img, 0, 0); return c;
}
// the backlit screen paper (non-tiling, big): white = clear; clouds of density + long dark fibres; multiplied over the lamp gradient
export function screenTex(w, h, seed = 21) {
  const c = mk(w, h), g = ctx2d(c), img = g.createImageData(w, h), d = img.data; const n = valueNoise2D(seed), q = valueNoise2D(seed + 1), o = valueNoise2D(seed + 2);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const m1 = n.fbm(x / 300, y / 240, 3, 2, 0.5), m2 = o.fbm(x / 60, y / 52, 3, 2, 0.5), t = q(x / 2.1, y / 2.1) - 0.5, k = (y * w + x) * 4;
    const v = Math.min(1, 0.79 + 0.16 * m1 + 0.09 * m2 + t * 0.035); d[k] = 255 * v; d[k + 1] = 251 * v; d[k + 2] = 242 * v; d[k + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const r = rng(seed + 5); g.lineCap = 'round';
  for (let k = 0; k < 1500; k++) {      // fibres: most faint and dark (denser paper), a few thin bright ones
    const x = r() * w, y = r() * h, a = r() * Math.PI * 2, L = 8 + r() * r() * 60, b1 = (r() - 0.5) * 2, b2 = (r() - 0.5) * 2, dark = r() < 0.78;
    g.strokeStyle = dark ? `rgba(110,62,30,${0.025 + 0.05 * r()})` : `rgba(255,250,232,${0.05 + 0.09 * r()})`; g.lineWidth = 0.4 + r() * 0.9;
    g.beginPath(); g.moveTo(x, y); g.bezierCurveTo(x + Math.cos(a + b1) * L * 0.33, y + Math.sin(a + b1) * L * 0.33, x + Math.cos(a + b2) * L * 0.66, y + Math.sin(a + b2) * L * 0.66, x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke();
  }
  return c;
}

// ------------------------------------------------------------------ layer compositor: each paper layer casts a soft offset shadow on what is behind
export class Compositor {
  constructor(W, H) { this.W = W; this.H = H; this.L = mk(W, H); this.S = mk(W, H); this.lg = ctx2d(this.L); this.sg = ctx2d(this.S); }
  begin() { const { lg, W, H } = this; lg.setTransform(1, 0, 0, 1, 0, 0); lg.globalAlpha = 1; lg.globalCompositeOperation = 'source-over'; lg.filter = 'none'; lg.clearRect(0, 0, W, H); return lg; }
  // draw(lg) paints the layer (it sets its own transforms). off = shadow offset in authoring px (down-left), blur in authoring px.
  layer(g, draw, { mode = 'source-over', off = [-4, 3.5], blur = 4, shadow = 'rgba(30,10,2,0.5)', defocus = 0 } = {}) {
    const lg = this.begin(); draw(lg); lg.setTransform(1, 0, 0, 1, 0, 0);
    const { W, H, sg } = this, s = VIEW.dpr;
    if (shadow) {
      sg.setTransform(1, 0, 0, 1, 0, 0); sg.globalCompositeOperation = 'source-over'; sg.clearRect(0, 0, W, H);
      sg.filter = `blur(${((blur + defocus) * s).toFixed(2)}px)`; sg.drawImage(this.L, off[0] * s, off[1] * s); sg.filter = 'none';
      sg.globalCompositeOperation = 'source-in'; sg.fillStyle = shadow; sg.fillRect(0, 0, W, H);
      if (!defocus) { sg.globalCompositeOperation = 'destination-out'; sg.drawImage(this.L, 0, 0); }
      sg.globalCompositeOperation = 'source-over';
      g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(this.S, 0, 0); g.restore();
    }
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = mode; if (defocus) g.filter = `blur(${(defocus * s).toFixed(2)}px)`;
    g.drawImage(this.L, 0, 0); g.restore();
  }
}
