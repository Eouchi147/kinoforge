// Bamberg (Kinetic): shared helpers. Self-contained (no three.js): math, canvas helpers, text metrics, brush ribbons.
// Everything is a pure function of its inputs; randomness is always a seeded rng.

// ---------------------------------------------------------------- math
export function rng(seed = 1) {
  let a = seed >>> 0;
  const f = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  return f;
}
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const ease = {
  linear: (t) => t, outQuad: (t) => t * (2 - t), inQuad: (t) => t * t, inOutQuad: (t) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t),
  outCubic: (t) => 1 - Math.pow(1 - t, 3), inCubic: (t) => t * t * t, inOutCubic: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  outQuart: (t) => 1 - Math.pow(1 - t, 4), inOutSine: (t) => -(Math.cos(Math.PI * t) - 1) / 2,
  outBack: (t) => { const c = 1.70158; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); },
};
export function noise1(t, seed = 0) {
  return 0.5 * Math.sin(t + seed) + 0.25 * Math.sin(t * 2.3 + seed * 1.7 + 1.1) + 0.125 * Math.sin(t * 5.1 + seed * 0.3 + 2.2) + 0.0625 * Math.sin(t * 11.7 + 3.3 + seed);
}
export function valueNoise2D(seed = 1) {
  const r = rng(seed), P = new Uint8Array(512), g = new Float32Array(256);
  for (let i = 0; i < 256; i++) { P[i] = i; g[i] = r(); }
  for (let i = 255; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [P[i], P[j]] = [P[j], P[i]]; }
  for (let i = 0; i < 256; i++) P[i + 256] = P[i];
  const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  const n = (x, y) => {
    const X = Math.floor(x) & 255, Y = Math.floor(y) & 255, xf = x - Math.floor(x), yf = y - Math.floor(y);
    const a = g[P[P[X] + Y]], b = g[P[P[X + 1] + Y]], c = g[P[P[X] + Y + 1]], d = g[P[P[X + 1] + Y + 1]], u = fade(xf), v = fade(yf);
    return lerp(lerp(a, b, u), lerp(c, d, u), v);
  };
  n.fbm = (x, y, oct = 5, lac = 2, gain = 0.5) => { let s = 0, a = 1, f = 1, norm = 0; for (let i = 0; i < oct; i++) { s += a * n(x * f, y * f); norm += a; a *= gain; f *= lac; } return s / norm; };
  return n;
}
export function fbmCanvas(w, h, { seed = 1, scale = 4, oct = 5, gain = 0.5, lo = 0, hi = 255, fn = null } = {}) {
  const n = valueNoise2D(seed), c = document.createElement('canvas'); c.width = w; c.height = h;
  const ctx = c.getContext('2d'), img = ctx.createImageData(w, h), d = img.data;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let v = n.fbm(x / w * scale, y / h * scale, oct, 2, gain); if (fn) v = fn(v, x / w, y / h);
    const g = lo + (hi - lo) * clamp(v), i = (y * w + x) * 4; d[i] = d[i + 1] = d[i + 2] = g; d[i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0); return c;
}

// ---------------------------------------------------------------- canvas / colour helpers
export const mk = (w, h) => { const c = document.createElement('canvas'); c.width = Math.round(w); c.height = Math.round(h); return c; };
export const hex = (h) => [1, 3, 5].map((k) => parseInt(h.slice(k, k + 2), 16));
export const rgba = (h, a = 1) => `rgba(${hex(h).join(',')},${a})`;
export const mixc = (a, b, k, al = 1) => { const A = hex(a), B = hex(b); return `rgba(${A.map((v, j) => Math.round(lerp(v, B[j], k))).join(',')},${al})`; };
export const keys = (f, K) => { if (f <= K[0][0]) return K[0][1]; for (let j = 1; j < K.length; j++) if (f <= K[j][0]) { const [a, va] = K[j - 1], [b, vb] = K[j]; return lerp(va, vb, (f - a) / (b - a)); } return K[K.length - 1][1]; };
export const densify = (P, step = 6) => { const out = []; for (let k = 0; k < P.length - 1; k++) { const [a, b] = [P[k], P[k + 1]]; const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / step)); for (let j = 0; j < n; j++) out.push([lerp(a[0], b[0], j / n), lerp(a[1], b[1], j / n)]); } out.push([...P[P.length - 1]]); return out; };
export const catmull = (P, n = 6) => { const out = []; for (let i = 0; i < P.length - 1; i++) { const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)]; for (let s = 0; s < n; s++) { const u = s / n, u2 = u * u, u3 = u2 * u; out.push([0, 1].map((a) => 0.5 * (2 * p1[a] + (p2[a] - p0[a]) * u + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * u2 + (3 * p1[a] - p0[a] - 3 * p2[a] + p3[a]) * u3))); } } out.push(P[P.length - 1]); return out; };
export const withScale = (g, ax, ay, s, fn) => { g.save(); g.translate(ax, ay); g.scale(s, s); g.translate(-ax, -ay); fn(); g.restore(); };
export const withStretch = (g, ay, sy, fn) => { g.save(); g.translate(0, ay); g.scale(1, sy); g.translate(0, -ay); fn(); g.restore(); };

// ---------------------------------------------------------------- text metrics
const MG = mk(8, 8).getContext('2d');
const MC = new Map();
export function measure(font, text, ls = 0) {
  const key = font + '|' + ls + '|' + text; if (MC.has(key)) return MC.get(key);
  MG.font = font; MG.letterSpacing = ls + 'px'; const m = MG.measureText(text);
  const o = { adv: m.width, l: m.actualBoundingBoxLeft, r: m.actualBoundingBoxRight, asc: m.actualBoundingBoxAscent, desc: m.actualBoundingBoxDescent }; MC.set(key, o); return o;
}
export const FONTS = {
  B: (px) => `400 ${px}px "Bebas Neue"`,                       // display, slams
  C: (px) => `italic 600 ${px}px "Cormorant Garamond"`,        // Junius's hand
  C5: (px) => `italic 500 ${px}px "Cormorant Garamond"`,
  T: (px) => `400 ${px}px "Special Elite"`,                    // the court: cold typed print
  F: (px) => `400 ${px}px "IM Fell English"`,                  // the executioner's hand
  FI: (px) => `italic 400 ${px}px "IM Fell English"`,
};
export const fitSize = (fontFn, text, lsEm, target) => { const m = measure(fontFn(100), text, lsEm * 100); return 100 * target / (m.r + m.l); };
export function mkLine(text, fontFn, F, lsEm = 0) {
  const font = fontFn(F), ls = lsEm * F, m = measure(font, text, ls);
  return { text, font, F, ls, adv: m.adv, l: m.l, r: m.r, inkW: m.r + m.l, asc: m.asc, desc: m.desc, cap: measure(font, 'H', 0).asc };
}
export function run(g, ln, text, ox, oy, { fill, alpha = 1 } = {}) {
  g.save(); g.font = ln.font; g.letterSpacing = ln.ls + 'px'; g.textAlign = 'left'; g.textBaseline = 'alphabetic'; g.fillStyle = fill; g.globalAlpha = alpha; g.fillText(text, ox, oy); g.restore();
}
export const prefixAdv = (ln, idx) => measure(ln.font, ln.text.slice(0, idx), ln.ls).adv;

// ---------------------------------------------------------------- brush ribbon (width-modulated filled stroke)
export function ribbon(g, pts, w, seed, { taper = 0.12, vary = 0.55, freq = 0.03, upto = 1 } = {}) {
  const N = pts.length; if (N < 2 || upto <= 0) return null;
  const s = new Float32Array(N); for (let k = 1; k < N; k++) s[k] = s[k - 1] + Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
  const L = s[N - 1] || 1, Lmax = L * upto; const A = [], B = []; let head = pts[0];
  for (let k = 0; k < N; k++) {
    if (s[k] > Lmax + 1e-6) break;
    const a = pts[Math.max(0, k - 1)], b = pts[Math.min(N - 1, k + 1)]; let tx = b[0] - a[0], ty = b[1] - a[1]; const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
    const u = s[k] / L, tp = 0.2 + 0.8 * Math.min(smoothstep(0, taper, u), smoothstep(0, taper, 1 - u));
    const nz = clamp(0.5 + 0.55 * noise1(s[k] * freq, seed)), hw = 0.5 * w * (1 - vary * 0.5 + vary * nz) * tp;
    A.push([pts[k][0] - ty * hw, pts[k][1] + tx * hw]); B.push([pts[k][0] + ty * hw, pts[k][1] - tx * hw]); head = pts[k];
  }
  if (A.length < 2) return null;
  g.beginPath(); g.moveTo(A[0][0], A[0][1]); for (const p of A) g.lineTo(p[0], p[1]); for (let k = B.length - 1; k >= 0; k--) g.lineTo(B[k][0], B[k][1]); g.closePath(); g.fill();
  return head;
}
