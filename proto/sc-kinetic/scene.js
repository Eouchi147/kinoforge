// P11 "KINETIC" — vertical (9:16) typographic hook, 8 s @ 24 fps (192 f). Canvas 2D drawn through boot() + the kit overlay (a black
// three.js scene sits behind it), so the kit's finish pass supplies the one grade: grain, vignette, a slight warm highlight tint.
// Deterministic: seeded rng, every animation is a function of the frame index. All sizes are H-relative (720x1280 and 1080x1920 are identical).
// Picture and sound share timing.js. Query params: ?safe=1 draws the platform-UI mask, ?audit=all logs every text box that leaves the safe rect.
import * as THREE from 'three';
import { boot, makeComposer, ease, rng, clamp, lerp, smoothstep, noise1, fbmCanvas, valueNoise2D } from '/harness/kit/film.js';
import T from './timing.js';

const FPS = T.fps;
const Q = new URLSearchParams(location.search);
const DBG_SAFE = Q.get('safe') === '1', AUDIT = Q.get('audit');
const C = { dark: '#0e0d0b', cream: '#efe6d2', ink: '#1a1612', red: '#9e1b1b' };
const SAFE = { x0: 0.11, x1: 0.78, y0: 0.15, y1: 0.65 };                 // R-2-08: left 11 %, right 22 %, top 15 %, bottom 35 %
const SHOTS = T.beats.map((b) => ({ name: b.name, dur: (b.f1 - b.f0) / FPS }));
const BEBAS = (px) => `400 ${px}px "Bebas Neue"`;
const CORM = (px) => `italic 600 ${px}px "Cormorant Garamond"`;
const CORM5 = (px) => `italic 500 ${px}px "Cormorant Garamond"`;
const PAD = 24;                                                           // paper canvases are PAD px larger on every side so the impact shake never shows an edge

let W, H, U, post, MG, LAY, PAPER_D, PAPER_C, INK, INKG, INKNOISE, TMP, TMPG, LAYER, LAYERG, LETTER, AUDIT_ON = false, BOXES = [], CUR_SHAKE = [0, 0];

// ---------------------------------------------------------------- small helpers
const mk = (w, h) => { const c = document.createElement('canvas'); c.width = Math.round(w); c.height = Math.round(h); return c; };
const hex = (h) => [1, 3, 5].map((k) => parseInt(h.slice(k, k + 2), 16));
const rgba = (h, a = 1) => `rgba(${hex(h).join(',')},${a})`;
const mixc = (a, b, k, al = 1) => { const A = hex(a), B = hex(b); return `rgba(${A.map((v, j) => Math.round(lerp(v, B[j], k))).join(',')},${al})`; };
const keys = (f, K) => { if (f <= K[0][0]) return K[0][1]; for (let j = 1; j < K.length; j++) if (f <= K[j][0]) { const [a, va] = K[j - 1], [b, vb] = K[j]; return lerp(va, vb, (f - a) / (b - a)); } return K[K.length - 1][1]; };
const densify = (P, step = 6) => { const out = []; for (let k = 0; k < P.length - 1; k++) { const [a, b] = [P[k], P[k + 1]]; const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / step)); for (let j = 0; j < n; j++) out.push([lerp(a[0], b[0], j / n), lerp(a[1], b[1], j / n)]); } out.push([...P[P.length - 1]]); return out; };
const withScale = (g, ax, ay, s, fn) => { g.save(); g.translate(ax, ay); g.scale(s, s); g.translate(-ax, -ay); fn(); g.restore(); };
const withStretch = (g, ay, sy, fn) => { g.save(); g.translate(0, ay); g.scale(1, sy); g.translate(0, -ay); fn(); g.restore(); };       // vertical-only landing: the word never grows sideways, so it can never leave the safe rectangle

// landing / slam curves, as (frames since landing -> scale). Piecewise linear on purpose: crisp, no float.
const SLAM = [[0, 1.30], [1, 1.12], [2, 1.0], [3, 0.962], [4, 0.978], [5, 0.995], [6, 1.0]];      // "1628": 2-frame undershoot then settle
const LAND = [[0, 1.20], [1, 1.08], [2, 1.016], [3, 1.0]];                                          // ordinary word on a tick: a vertical stretch that snaps back (height only)
const HEAVY = [[0, 1.24], [1, 1.09], [2, 1.0], [3, 0.972], [4, 0.99], [5, 1.0]];                   // EXECUTED
const PAYOFF = [[0, 1.24], [1, 1.09], [2, 0.99], [3, 0.965], [4, 0.99], [5, 1.0]];                 // FOR WITCHCRAFT
const SHAKES = [[T.b1.slam, 7, 5], [T.b2.witch, 4, 4], [T.b3.cut, 11, 6]];                         // [frame, amplitude px @1280, length]

function shakeAt(f) {
  let dx = 0, dy = 0;
  for (const [f0, amp, len] of SHAKES) { const k = f - f0; if (k >= 0 && k < len) { const d = Math.pow(1 - k / len, 1.5); dx += amp * d * Math.cos(k * 2.6 + f0); dy += amp * d * Math.sin(k * 3.3 + f0 * 0.7); } }
  return [dx * U, dy * U];
}

// ---------------------------------------------------------------- text metrics, lines, tracking
const MC = new Map();
function measure(font, text, ls = 0) {
  const key = font + '|' + ls + '|' + text; if (MC.has(key)) return MC.get(key);
  MG.font = font; MG.letterSpacing = ls + 'px'; const m = MG.measureText(text);
  const o = { adv: m.width, l: m.actualBoundingBoxLeft, r: m.actualBoundingBoxRight, asc: m.actualBoundingBoxAscent, desc: m.actualBoundingBoxDescent }; MC.set(key, o); return o;
}
const fitSize = (fontFn, text, lsEm, target) => { const m = measure(fontFn(100), text, lsEm * 100); return 100 * target / (m.r + m.l); };
function mkLine(text, fontFn, F, lsEm) {
  const font = fontFn(F), ls = lsEm * F, m = measure(font, text, ls);
  return { text, font, F, ls, adv: m.adv, l: m.l, r: m.r, inkW: m.r + m.l, asc: m.asc, desc: m.desc, cap: measure(font, 'H', 0).asc };
}
function track(g, label, x0, y0, x1, y1) {                                  // audit: record a box in frame coordinates (shake removed)
  if (!AUDIT_ON) return; const M = g.getTransform(), sh = g === post.overlay.ctx ? CUR_SHAKE : [0, 0]; const P = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]].map(([x, y]) => [M.a * x + M.c * y + M.e - sh[0], M.b * x + M.d * y + M.f - sh[1]]);
  BOXES.push({ label, x0: Math.min(...P.map((p) => p[0])), x1: Math.max(...P.map((p) => p[0])), y0: Math.min(...P.map((p) => p[1])), y1: Math.max(...P.map((p) => p[1])) });
}
// draw `text` (a whole line or a run of it) with its origin at (ox, oy)
function run(g, ln, text, ox, oy, { fill, alpha = 1, label = 'text' } = {}) {
  g.save(); g.font = ln.font; g.letterSpacing = ln.ls + 'px'; g.textAlign = 'left'; g.textBaseline = 'alphabetic'; g.fillStyle = fill; g.globalAlpha = alpha; g.fillText(text, ox, oy); g.restore();
  const m = measure(ln.font, text, ln.ls); track(g, label, ox - m.l, oy - m.asc, ox + m.r, oy + m.desc);
}
// word k of a line: origin from the continuous layout (prefix advance), so it sits exactly where the full line would put it
function wordAt(ln, ox, text, idx) { return { text, ox: ox + measure(ln.font, ln.text.slice(0, idx), ln.ls).adv, m: measure(ln.font, text, ln.ls) }; }

// ---------------------------------------------------------------- brush ribbon (width-modulated filled stroke), ported from the p02 pattern
function ribbon(g, pts, w, seed, { taper = 0.12, vary = 0.55, freq = 0.03, upto = 1 } = {}) {
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
// a hand-laid underline: nearly straight, with a slow wave and a slight rise so it does not look ruled
const underlinePts = (x0, x1, y, amp = 1.6) => densify([[x0, y], [x0 + (x1 - x0) * 0.33, y + amp * U * 0.6], [x0 + (x1 - x0) * 0.7, y - amp * U * 0.4], [x1, y - amp * U]], 6);

// ---------------------------------------------------------------- baked textures
function bakeDark(w, h) {
  const cv = mk(w, h), g = cv.getContext('2d'), r = rng(11);
  g.fillStyle = '#070606'; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'lighter'; g.drawImage(fbmCanvas(w, h, { seed: 7, scale: 4.5, oct: 5, gain: 0.55, lo: 0, hi: 9, fn: (v) => 0.5 + (v - 0.5) * 2.2 }), 0, 0);
  const gr = g.createRadialGradient(w * 0.40, h * 0.40, 10, w * 0.40, h * 0.40, h * 0.62); gr.addColorStop(0, 'rgba(64,52,36,0.10)'); gr.addColorStop(1, 'rgba(64,52,36,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'source-over';
  for (let k = 0; k < 70; k++) { g.fillStyle = `rgba(239,230,210,${0.03 + 0.08 * r()})`; const d = (0.6 + 1.6 * r()) * U; g.fillRect(r() * w, r() * h, d, d); }          // dust
  g.lineCap = 'round'; for (let k = 0; k < 26; k++) { const x = r() * w, y = r() * h, a = r() * 6.28, L = (8 + 26 * r()) * U; g.strokeStyle = `rgba(239,230,210,${0.025 + 0.05 * r()})`; g.lineWidth = 0.6 * U; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * L * 0.5 + 3, y + Math.sin(a) * L * 0.5, x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke(); }
  return cv;
}
function bakeCream(w, h) {
  const cv = mk(w, h), g = cv.getContext('2d'), r = rng(77);
  g.fillStyle = '#f1ebdb'; g.fillRect(0, 0, w, h);        // pre-finish cream; the multiplies below and the finish pass's warm highlight tint land it on #efe6d2
  g.globalCompositeOperation = 'multiply';
  g.drawImage(fbmCanvas(w, h, { seed: 31, scale: 2.4, oct: 4, gain: 0.5, lo: 243, hi: 255, fn: (v) => 0.5 + (v - 0.5) * 2.2 }), 0, 0);       // slow parchment mottling (a few %)
  g.drawImage(fbmCanvas(w, h, { seed: 32, scale: 330, oct: 2, gain: 0.55, lo: 245, hi: 255, fn: (v) => 0.5 + (v - 0.5) * 2.0 }), 0, 0);      // fine tooth, 2-3 px cells (no mid-scale blobs)
  g.globalCompositeOperation = 'source-over';
  for (let k = 0; k < 5; k++) { const x = r() * w, y = r() * h, R = (110 + 170 * r()) * U; const gr = g.createRadialGradient(x, y, 2, x, y, R); gr.addColorStop(0, 'rgba(150,108,56,0.05)'); gr.addColorStop(1, 'rgba(150,108,56,0)'); g.fillStyle = gr; g.fillRect(x - R, y - R, R * 2, R * 2); }   // age stains
  g.lineCap = 'round';
  for (let k = 0; k < 1100; k++) { const x = r() * w, y = r() * h, a = r() * 6.28, L = (4 + 20 * r()) * U, bend = (r() - 0.5) * 0.9; g.strokeStyle = r() < 0.6 ? `rgba(120,94,62,${0.04 + 0.08 * r()})` : `rgba(255,252,240,${0.12 + 0.22 * r()})`; g.lineWidth = (0.5 + 0.8 * r()) * U; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a + bend) * L * 0.5, y + Math.sin(a + bend) * L * 0.5, x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke(); }
  for (let k = 0; k < 70; k++) { g.fillStyle = `rgba(104,70,36,${0.10 + 0.22 * r()})`; g.beginPath(); g.arc(r() * w, r() * h, (0.5 + 1.6 * r()) * U, 0, 6.2832); g.fill(); }                // foxing
  const eg = (x0, y0, x1, y1, ax, ay, bx, by) => { const gr = g.createLinearGradient(x0, y0, x1, y1); gr.addColorStop(0, 'rgba(120,86,44,0.09)'); gr.addColorStop(1, 'rgba(120,86,44,0)'); g.fillStyle = gr; g.fillRect(ax, ay, bx, by); };
  const e = 70 * U; eg(0, 0, e, 0, 0, 0, e, h); eg(w, 0, w - e, 0, w - e, 0, e, h); eg(0, 0, 0, e, 0, 0, w, e); eg(0, h, 0, h - e, 0, h - e, w, e);
  return cv;
}
function bakeInkNoise(w, h) {                                                  // printed-ink dropout: tiny speckles that eat up to ~20 % of the ink
  const cv = mk(w, h), g = cv.getContext('2d'), img = g.createImageData(w, h), d = img.data, n = valueNoise2D(91);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const v = n.fbm(x / (2.2 * U), y / (2.2 * U), 2) * 0.7 + n(x / (0.9 * U) + 40, y / (0.9 * U) + 7) * 0.3; const a = smoothstep(0.60, 0.80, v) * 0.20; const k = (y * w + x) * 4; d[k] = d[k + 1] = d[k + 2] = 0; d[k + 3] = Math.round(a * 255); }
  g.putImageData(img, 0, 0); return cv;
}

// The letter: a torn, folded sheet in the card's own dark. Sprite is baked once; its top-left sheet corner is at (M, M).
function bakeLetter() {
  const Lw = Math.round(0.764 * W), Lh = Math.round(0.64 * H), M = Math.round(0.05 * H), r = rng(2024);
  const cv = mk(Lw + 2 * M, Lh + 2 * M), g = cv.getContext('2d'); g.translate(M, M);
  const N = 110, ph = Array.from({ length: 6 }, () => r() * 6.283), edge = [];
  for (let k = 0; k <= N; k++) {                                            // torn top edge: sines of rising frequency + jitter + one two-stroke step
    const u = k / N; let y = 0; [[3, 5], [7, 3.4], [13, 2.4], [29, 1.6], [57, 1.1]].forEach(([fq, a], j) => { y += a * U * Math.sin(u * fq * 6.283 + ph[j]); });
    y += (r() - 0.5) * 3.2 * U + smoothstep(0.55, 0.60, u) * -15 * U; edge.push([Lw * u, y]);
  }
  const ey = (x) => { const k = clamp(x / Lw) * N, a = Math.floor(k), b = Math.min(N, a + 1); return lerp(edge[a][1], edge[b][1], k - a); };
  const d = 86 * U;                                                           // dog-ear leg
  const A = [Lw - d, ey(Lw - d)], B = [Lw, ey(Lw) + d];
  const path = new Path2D(); path.moveTo(edge[0][0], edge[0][1]);
  for (const [x, y] of edge) { if (x <= A[0]) path.lineTo(x, y); }
  path.lineTo(A[0], A[1]); path.lineTo(B[0], B[1]); path.lineTo(Lw + 1.5 * U, Lh * 0.55); path.lineTo(Lw, Lh + 40); path.lineTo(0, Lh + 40); path.lineTo(-3 * U, Lh * 0.62); path.lineTo(2 * U, Lh * 0.3); path.closePath();
  // soft contact shadow on the cream (the sheet lies flat: small offset, wide blur)
  g.save(); g.shadowColor = 'rgba(40,26,10,0.60)'; g.shadowBlur = 34 * U; g.shadowOffsetX = 6 * U; g.shadowOffsetY = 12 * U; g.fillStyle = '#1c1610'; g.fill(path); g.restore();
  g.save(); g.clip(path);
  g.globalCompositeOperation = 'lighter'; g.drawImage(fbmCanvas(Lw, Lh, { seed: 61, scale: 14, oct: 4, gain: 0.5, lo: 0, hi: 9, fn: (v) => 0.5 + (v - 0.5) * 2.0 }), 0, 0);   // aged mottling, fine enough not to read as clouds
  g.globalCompositeOperation = 'source-over';
  let gr = g.createLinearGradient(0, 0, 0, Lh * 0.55); gr.addColorStop(0, 'rgba(176,146,104,0.24)'); gr.addColorStop(0.5, 'rgba(176,146,104,0.07)'); gr.addColorStop(1, 'rgba(176,146,104,0)'); g.fillStyle = gr; g.fillRect(0, 0, Lw, Lh);   // the torn end catches the light
  gr = g.createLinearGradient(0, Lh * 0.45, 0, Lh); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = gr; g.fillRect(0, 0, Lw, Lh + 40);                   // and falls off toward the bottom
  g.strokeStyle = 'rgba(214,196,160,0.16)'; g.lineWidth = 1.6 * U; g.beginPath(); g.moveTo(1 * U, 8 * U); g.lineTo(-1 * U, Lh); g.moveTo(Lw - 1 * U, 8 * U); g.lineTo(Lw, Lh); g.stroke();      // paper thickness on the side edges
  for (let k = 0; k < 900; k++) { const x = r() * Lw, y = r() * Lh, a = r() * 6.28, L = (3 + 12 * r()) * U; g.strokeStyle = `rgba(214,196,160,${0.03 + 0.07 * r()})`; g.lineWidth = 0.7 * U; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke(); }
  // abstract handwriting: wavy strokes with word-like gaps and a ragged right margin. Deliberately NOT glyphs (R-9-07); very faint, lower body only.
  { const rs = rng(515), xh = 8.5 * U, asc = 21 * U, desc = 13 * U;
    const cr = (P, n) => { const out = []; for (let i = 0; i < P.length - 1; i++) { const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)]; for (let s = 0; s < n; s++) { const u = s / n, u2 = u * u, u3 = u2 * u; out.push([0, 1].map((a) => 0.5 * (2 * p1[a] + (p2[a] - p0[a]) * u + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * u2 + (3 * p1[a] - p0[a] - 3 * p2[a] + p3[a]) * u3))); } } out.push(P[P.length - 1]); return out; };
    const pen = (pts, w) => {                                                                       // pointed-pen ribbon: thicker on the downstroke, thinner on the upstroke and at the ends
      const N = pts.length, A = [], B = []; for (let k = 0; k < N; k++) { const a = pts[Math.max(0, k - 1)], b = pts[Math.min(N - 1, k + 1)]; let tx = b[0] - a[0], ty = b[1] - a[1]; const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
        const hw = 0.5 * w * (0.4 + 0.95 * clamp(0.25 + 0.75 * ty)) * (k < 3 || k > N - 4 ? 0.55 : 1); A.push([pts[k][0] - ty * hw, pts[k][1] + tx * hw]); B.push([pts[k][0] + ty * hw, pts[k][1] - tx * hw]); }
      g.beginPath(); g.moveTo(A[0][0], A[0][1]); for (const p of A) g.lineTo(p[0], p[1]); for (let k = N - 1; k >= 0; k--) g.lineTo(B[k][0], B[k][1]); g.closePath(); g.fill();
    };
    const E = -0.18 * xh;                                                                           // every cell starts and ends at this height, so the pen never lifts inside a word
    const shapes = [                                                                                 // abstract cells (humps, waves, ascender loops, descenders) -- they imitate a hand, they do not spell
      (c) => [[0.22 * c, -xh], [0.5 * c, -0.2 * xh], [0.78 * c, -xh], [c, E]],                                                          // n / m / u
      (c) => [[0.3 * c, -0.95 * xh], [0.55 * c, -0.05 * xh], [0.8 * c, -0.75 * xh], [c, E]],                                            // e / a / c
      (c) => [[0.24 * c, -0.7 * asc], [0.4 * c, -asc], [0.52 * c, -0.65 * asc], [0.34 * c, -0.2 * asc], [0.58 * c, 0], [c, E]],         // l / h / b: an ascender loop
      (c) => [[0.3 * c, -xh], [0.42 * c, 0.25 * desc], [0.4 * c, desc], [0.12 * c, 0.85 * desc], [0.3 * c, -0.1 * xh], [c, E]],         // g / y / p: a descender loop
    ];
    let li = 0;
    for (let ly = Lh * 0.37; ly < Lh - 20 * U; ly += 37 * U, li++) {
      const slope = (rs() - 0.5) * 0.012; let x = (44 + 6 * rs() + (li % 5 === 0 ? 26 : 0)) * U; const xe = Lw - (46 + rs() * Lw * 0.30) * U, x0 = x;
      while (x < xe) {
        const wl = (22 + 84 * rs()) * U, P = [[x, ly + slope * (x - x0) + E]]; let cx = x;
        while (cx < x + wl - 3 * U) { const c = (4.8 + 5.2 * rs()) * U, q = rs(), kd = q < 0.34 ? 0 : q < 0.64 ? 1 : q < 0.84 ? 2 : 3; for (const [px, py] of shapes[kd](c)) P.push([cx + px, ly + slope * (cx + px - x0) + py + (rs() - 0.5) * 0.8 * U]); cx += c; }
        g.fillStyle = `rgba(206,188,150,${0.09 + 0.06 * rs()})`; pen(cr(P, 4), (1.5 + 0.9 * rs()) * U);
        x = cx + (8 + 13 * rs()) * U;
      }
    } }
  for (const yy of [Lh * 0.31, Lh * 0.63]) {                                                     // trifold creases: shadow line + catch-light
    const pts = []; for (let x = -4; x <= Lw + 4; x += 14 * U) pts.push([x, yy + 1.4 * U * noise1(x * 0.02, yy)]);
    g.lineJoin = 'round'; g.strokeStyle = 'rgba(0,0,0,0.55)'; g.lineWidth = 3.2 * U; g.beginPath(); pts.forEach((p, i) => (i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1]))); g.stroke();
    g.strokeStyle = 'rgba(214,196,160,0.13)'; g.lineWidth = 1.6 * U; g.beginPath(); pts.forEach((p, i) => (i ? g.lineTo(p[0], p[1] + 3 * U) : g.moveTo(p[0], p[1] + 3 * U))); g.stroke();
  }
  g.restore();
  // torn rim: the white inner fibre of the paper shows along the tear
  const tear = edge.filter(([x]) => x <= A[0]);
  g.lineJoin = 'round'; g.lineCap = 'round';
  g.strokeStyle = 'rgba(206,190,156,0.30)'; g.lineWidth = 5.5 * U; g.beginPath(); tear.forEach((p, i) => (i ? g.lineTo(p[0], p[1] + 2.2 * U) : g.moveTo(p[0], p[1] + 2.2 * U))); g.stroke();
  g.strokeStyle = 'rgba(232,218,186,0.62)'; g.lineWidth = 1.7 * U; g.beginPath(); tear.forEach((p, i) => (i ? g.lineTo(p[0], p[1] + 0.8 * U) : g.moveTo(p[0], p[1] + 0.8 * U))); g.stroke();
  for (let k = 0; k < 110; k++) { const p = tear[Math.floor(r() * tear.length)], a = -Math.PI / 2 + (r() - 0.5) * 1.3, L = (2.5 + 8 * r()) * U; g.strokeStyle = `rgba(226,210,176,${0.25 + 0.4 * r()})`; g.lineWidth = (0.6 + 0.6 * r()) * U; g.beginPath(); g.moveTo(p[0], p[1] + 1.5 * U); g.lineTo(p[0] + Math.cos(a) * L, p[1] + 1.5 * U + Math.sin(a) * L); g.stroke(); }
  // dog-ear: the corner folded over; its back is a lighter tone, with a shadow where it lies on the sheet
  const P = [Lw, ey(Lw)], dx = B[0] - A[0], dy = B[1] - A[1], dl = Math.hypot(dx, dy), nx = -dy / dl, ny = dx / dl, t2 = ((P[0] - A[0]) * nx + (P[1] - A[1]) * ny) * 2;
  const P2 = [P[0] - nx * t2, P[1] - ny * t2];
  g.save(); g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 9 * U; g.shadowOffsetX = -2 * U; g.shadowOffsetY = 3 * U;
  g.fillStyle = '#3a3126'; g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.lineTo(P2[0], P2[1]); g.closePath(); g.fill(); g.restore();
  gr = g.createLinearGradient(A[0], A[1], P2[0], P2[1]); gr.addColorStop(0, 'rgba(214,196,160,0.30)'); gr.addColorStop(1, 'rgba(214,196,160,0.04)'); g.fillStyle = gr; g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.lineTo(P2[0], P2[1]); g.closePath(); g.fill();
  g.strokeStyle = 'rgba(232,218,186,0.45)'; g.lineWidth = 1.4 * U; g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.stroke();
  return { cv, Lw, Lh, M };
}

// ---------------------------------------------------------------- layout (everything from H; x from W). Built once in init().
function buildLayout() {
  const ax = SAFE.x0 * W, meas = (SAFE.x1 - SAFE.x0) * W, L = { ax, meas };
  { // B1
    const ln = mkLine('1628', BEBAS, 0.229 * H, 0.01), base = 0.430 * H;
    L.year = { ln, ox: ax + ln.l, base, anchorY: base - ln.cap / 2 };
    const dl = mkLine('Bamberg, Germany', CORM, fitSize(CORM, 'Bamberg, Germany', 0.02, ln.inkW), 0.02);   // dateline fitted to the year's width: one lockup, one measure
    L.date = { ln: dl, ox: ax + dl.l, base: 0.515 * H };
    L.rule = { y: 0.455 * H, w: ln.inkW, th: Math.max(2, 0.0021 * H) };
  }
  { // B2: three lines fitted to one measure -> hard left and right axes
    const gap = 0.024 * H, mk3 = (text, ls) => mkLine(text, BEBAS, fitSize(BEBAS, text, ls, meas), ls);
    const l1 = mk3('A MAYOR WAS', 0.02), l2 = mk3('EXECUTED', 0), l3 = mk3('FOR WITCHCRAFT', 0.04);
    const top = 0.265 * H, b1 = top + l1.cap, b2 = b1 + gap + l2.cap, b3 = b2 + gap + l3.cap;
    L.b2 = { l1: { ln: l1, ox: ax + l1.l, base: b1 }, l2: { ln: l2, ox: ax + l2.l, base: b2 }, l3: { ln: l3, ox: ax + l3.l, base: b3 }, ulY: b3 + 0.019 * H, ulW: 0.0095 * H };
    L.b2.words = [['A', 0], ['MAYOR', 2], ['WAS', 8]].map(([w, idx]) => ({ ...wordAt(l1, L.b2.l1.ox, w, idx), base: b1, ln: l1 }));
  }
  { // B3-B6 written lines (Cormorant italic, ink)
    const FT1 = fitSize(CORM, 'His last letter', 0, 0.93 * meas), F23 = fitSize(CORM, 'With a broken hand.', 0, 0.975 * meas), gapP = 0.040 * H;
    const b1 = 0.168 * H + 0.73 * FT1, b1b = b1 + 0.95 * FT1, b2 = b1b + gapP + 0.73 * F23, b3 = b2 + 1.2 * F23;
    const a = mkLine('His last letter', CORM, FT1, 0), b = mkLine('survived.', CORM, FT1, 0), jr = rng(88);
    const glyphs = (ln, slot0) => { ln.slot0 = slot0; ln.ox = ax + ln.l; ln.gx = []; ln.gadv = []; ln.jit = []; for (let j = 0; j < ln.text.length; j++) { const ch = ln.text[j]; ln.gx.push(measure(ln.font, ln.text.slice(0, j + 1), 0).adv - measure(ln.font, ch, 0).adv); ln.gadv.push(measure(ln.font, ch, 0).adv); ln.jit.push({ dy: (jr() - 0.5) * 2.4 * U, rot: (jr() - 0.5) * 0.026, sc: 1 + (jr() - 0.5) * 0.024 }); } };
    glyphs(a, 0); glyphs(b, a.text.length + 1);                              // slot 15 = the wrap space (the quill lifts for one beat)
    a.base = b1; b.base = b1b;
    const t2 = mkLine('Written in secret.', CORM, F23, 0), t3 = mkLine('With a broken hand.', CORM, F23, 0);
    L.t1 = { lines: [a, b], slots: a.text.length + 1 + b.text.length };
    L.t2 = { ln: t2, ox: ax + t2.l, base: b2 };
    L.t3 = { ln: t3, ox: ax + t3.l, base: b3, ulY: b3 + 0.0135 * H, ulW: 0.0085 * H };
    L.t3.words = [['With', 0], ['a', 5], ['broken', 7], ['hand.', 14]].map(([w, idx]) => ({ ...wordAt(t3, L.t3.ox, w, idx), base: b3, ln: t3 }));
  }
  { // B6 label + arrow + letter pose
    const lb = mkLine('PART 1 OF 3', BEBAS, 0.042 * H, 0.20);
    L.label = { ln: lb, ox: ax + lb.l, base: 0.590 * H };
    L.arrow = { x: ax + 17 * U, y0: 0.608 * H, y1: 0.643 * H, head: 15 * U, w: Math.max(2, 0.0052 * H) };
    L.letter = { x: 0.07 * W, rest: 0.515 * H, peek: 0.930 * H, dip: 0.025 * H, tilt: -0.05 };
  }
  return L;
}

// ---------------------------------------------------------------- the dark cards
function flashFill(k, a) { return mixc(C.cream, '#fffaf0', k === 0 ? 0.8 : k === 1 ? 0.35 : 0, a); }
function drawB1(g, f) {
  const Y = LAY.year, s = keys(f, SLAM);
  if (f < 3) for (const [dt, al] of [[0.7, 0.10], [0.35, 0.20]]) withScale(g, LAY.ax, Y.anchorY, keys(f - dt, SLAM), () => run(g, Y.ln, '1628', Y.ox, Y.base, { fill: rgba(C.cream, al), label: 'smear' }));      // R-5-03 smear
  withScale(g, LAY.ax, Y.anchorY, s, () => run(g, Y.ln, '1628', Y.ox, Y.base, { fill: flashFill(f, 1), label: 'year' }));
  const kr = clamp((f - T.b1.rule + 1) / 5);
  if (kr > 0) { g.fillStyle = rgba(C.cream, 0.5); const rw = LAY.rule.w * ease.outCubic(kr); g.fillRect(LAY.ax, LAY.rule.y, rw, LAY.rule.th); track(g, 'gfx:rule', LAY.ax, LAY.rule.y, LAY.ax + rw, LAY.rule.y + LAY.rule.th); }
  const kd = (f - T.b1.dateline + 1) / 3;
  if (kd > 0) { const e = ease.outCubic(clamp(kd)); run(g, LAY.date.ln, 'Bamberg, Germany', LAY.date.ox, LAY.date.base + (1 - e) * 0.012 * H, { fill: C.cream, alpha: 0.92 * e, label: 'dateline' }); }
}
function drawWordsLine(g, f, line, wordsFrames, curve, color, alpha, label) {
  for (const w of line) {
    const k = f - wordsFrames[w.text]; if (k < 0) continue;
    const m = w.m, ax = w.ox - m.l, ay = w.base - w.ln.cap / 2;
    withStretch(g, ay, keys(k, curve), () => run(g, w.ln, w.text, w.ox, w.base, { fill: mixc(color, '#fffaf0', k === 0 ? 0.7 : k === 1 ? 0.28 : 0, alpha), label: label + w.text }));
  }
}
function drawB2(g, f) {
  const B = LAY.b2;
  drawWordsLine(g, f, B.words, T.b2.words, LAND, C.cream, 0.88, 'b2:');
  const kE = f - T.b2.words.EXECUTED;
  if (kE >= 0) { const m = B.l2.ln, ax = LAY.ax, ay = B.l2.base - m.cap / 2; withStretch(g, ay, keys(kE, HEAVY), () => run(g, m, 'EXECUTED', B.l2.ox, B.l2.base, { fill: mixc(C.cream, '#fffaf0', kE === 0 ? 0.7 : kE === 1 ? 0.28 : 0), label: 'b2:EXECUTED' })); }
  const kW = f - T.b2.witch;
  if (kW >= 0) {
    const m = B.l3.ln, ax = LAY.ax, ay = B.l3.base - m.cap / 2; withStretch(g, ay, keys(kW, PAYOFF), () => run(g, m, m.text, B.l3.ox, B.l3.base, { fill: mixc(C.cream, '#fffaf0', kW === 0 ? 0.8 : kW === 1 ? 0.3 : 0), label: 'b2:FOR WITCHCRAFT' }));
    const p = ease.outCubic(clamp((f + 0.5 - T.b2.ulStart) / (T.b2.ulEnd - T.b2.ulStart)));                       // red-ink underline drawn left -> right
    if (f >= T.b2.ulStart) {
      const x0 = LAY.ax, x1 = LAY.ax + m.inkW; g.fillStyle = C.red; const head = ribbon(g, underlinePts(x0, x1, B.ulY), B.ulW, 41, { upto: p, taper: 0.06 });
      if (p < 1 && head) { g.beginPath(); g.arc(head[0], head[1], B.ulW * 0.62, 0, 6.2832); g.fill(); }
      track(g, 'gfx:underline-b2', x0, B.ulY - B.ulW, x0 + (x1 - x0) * p, B.ulY + B.ulW);
    }
  }
}

// ---------------------------------------------------------------- the cream card
function drawT1(g, f, t) {                                                       // written, glyph by glyph: 40 ms each, 70 ms left->right wipe, wet ink that dries in 220 ms
  const t0 = T.b4.typeStart / FPS, gm = T.b4.glyphMs / 1000, wipe = T.b4.wipeMs / 1000, dry = T.b4.dryMs / 1000;
  for (const ln of LAY.t1.lines) {
    let any = false;
    for (let j = 0; j < ln.text.length; j++) {
      const ch = ln.text[j]; if (ch === ' ') continue;
      const tk = t0 + (ln.slot0 + j) * gm, p = (t - tk) / wipe; if (p <= 0) continue; any = true;
      const age = t - tk, wet = 1 - smoothstep(0.02, dry, age), jt = ln.jit[j], adv = ln.gadv[j], cx = ln.ox + ln.gx[j] + adv / 2;
      g.save(); g.translate(cx, ln.base + jt.dy); g.rotate(jt.rot); g.scale(jt.sc, jt.sc);
      g.beginPath(); g.rect(-adv / 2 - 3 * U, -ln.asc * 1.3, (adv + 6 * U) * clamp(p), (ln.asc + ln.desc) * 1.8); g.clip();
      g.font = ln.font; g.letterSpacing = '0px'; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
      g.shadowColor = rgba(C.ink, 0.55 * wet); g.shadowBlur = (1.2 + 3.4 * wet) * U; g.fillStyle = mixc('#0a0806', C.ink, 1 - wet); g.fillText(ch, -adv / 2, 0); g.restore();
    }
    if (any) track(g, 'T1:' + ln.text, ln.ox - ln.l, ln.base - ln.asc, ln.ox + ln.r, ln.base + ln.desc);
  }
}
function drawT2(g, f) {                                                          // whole line, 5-frame ink wipe with a soft leading edge, then a 0.58 s hold
  const k = f - T.b5.t2; if (k < 0) return; const B = LAY.t2, p = clamp((k + 1) / T.b5.t2Wipe);
  if (p >= 1) { run(g, B.ln, B.ln.text, B.ox, B.base, { fill: C.ink, label: 'T2' }); return; }
  TMPG.setTransform(1, 0, 0, 1, 0, 0); TMPG.clearRect(0, 0, W, H); TMPG.globalCompositeOperation = 'source-over';
  run(TMPG, B.ln, B.ln.text, B.ox, B.base, { fill: C.ink, label: 'T2' });
  const x0 = LAY.ax, w = B.ln.inkW + 12 * U, edge = 26 * U, xe = x0 + p * (w + edge), gr = TMPG.createLinearGradient(xe - edge, 0, xe, 0); gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  TMPG.globalCompositeOperation = 'destination-in'; TMPG.fillStyle = gr; TMPG.fillRect(0, 0, W, H); TMPG.globalCompositeOperation = 'source-over';
  g.drawImage(TMP, 0, 0);
}
function drawT3(g, f) {                                                          // word by word, 4-frame holds, then the red underline that bleeds
  const B = LAY.t3;
  for (const w of B.words) {
    const k = f - T.b5.t3[w.text]; if (k < 0) continue; const s = keys(k, [[0, 1.04], [1, 1.015], [2, 1.0]]), ax = w.ox - w.m.l, ay = B.base - B.ln.cap / 2;
    withScale(g, ax, ay, s, () => run(g, B.ln, w.text, w.ox, B.base, { fill: C.ink, alpha: k === 0 ? 0.6 : 1, label: 'T3:' + w.text }));
  }
  if (f >= T.b5.ulStart) {
    const p = ease.outCubic(clamp((f + 0.5 - T.b5.ulStart) / (T.b5.ulEnd - T.b5.ulStart))), b = clamp((f - T.b5.ulEnd) / 16), x0 = LAY.ax, x1 = LAY.ax + B.ln.inkW + 2 * U, pts = underlinePts(x0, x1, B.ulY, 1.4);
    if (b > 0) { g.save(); g.filter = `blur(${(1.0 + 2.2 * b) * U}px)`; g.globalAlpha = 0.5 * b; g.fillStyle = C.red; ribbon(g, pts, B.ulW * (1.7 + 0.5 * b), 52, { upto: 1, taper: 0.06 }); g.restore(); }
    g.fillStyle = C.red; const head = ribbon(g, pts, B.ulW * (1 + 0.25 * b), 52, { upto: p, taper: 0.06 });
    if (p < 1 && head) { g.beginPath(); g.arc(head[0], head[1], B.ulW * 0.62, 0, 6.2832); g.fill(); }
    if (b > 0) { const r2 = rng(53); g.fillStyle = rgba(C.red, 0.34 * b); for (let k = 0; k < 16; k++) { const x = lerp(x0, x1, r2()), y = B.ulY + (r2() - 0.35) * B.ulW * 1.5, rad = (0.9 + 1.7 * r2()) * U * (0.5 + 0.5 * b); g.beginPath(); g.arc(x, y, rad, 0, 6.2832); g.fill(); } }   // capillary spots
    track(g, 'gfx:underline-b5', x0, B.ulY - B.ulW, x0 + (x1 - x0) * p, B.ulY + B.ulW);
  }
}
const letterY = (f) => {                                                         // f may be fractional. 3-frame anticipation dip, then 11 frames of outBack
  const P = LAY.letter, k = f - T.b3.cut; if (k < 0) return P.peek;                  // before the cut the sheet is not drawn; sampling the shutter across the cut must not see an off-screen pose (it would ghost the first frame)
  if (f < T.b3.launch) return lerp(P.peek, P.peek + P.dip, ease.outQuad(clamp(k / T.b3.dipFrames)));
  return lerp(P.peek + P.dip, P.rest, ease.outBack(clamp((f - T.b3.launch) / (T.b3.rest - T.b3.launch))));
};
let ACC = null, OUTIMG = null;
function drawLetter(g, f) {                                                      // 180-degree shutter: while the sheet moves, average sub-frame poses in FLOAT (an 8-bit 'lighter' stack tints a dark, textured sheet); N follows the smear length so the torn edge never stair-steps
  const P = LAY.letter, S = LETTER, cx = P.x + S.Lw / 2;
  const put = (gg, y) => { gg.save(); gg.translate(cx, y); gg.rotate(P.tilt); gg.drawImage(S.cv, -S.Lw / 2 - S.M, -S.M); gg.restore(); };
  const y = letterY(f), span = Math.abs(y - letterY(f - 0.5));
  if (span <= 1.2) { put(g, y); return; }
  const N = clamp(Math.ceil(span / 3), 3, 32), ys = []; for (let s = 0; s < N; s++) ys.push(letterY(f - 0.5 * s / (N - 1)));
  const ytop = Math.max(0, Math.floor(Math.min(...ys) - S.M - 70 * U)), bh = H - ytop, bw = W, n4 = bw * bh * 4;
  if (!ACC || ACC.length !== n4) { ACC = new Float32Array(n4); OUTIMG = LAYERG.createImageData(bw, bh); } else ACC.fill(0);
  for (const yy of ys) {
    LAYERG.setTransform(1, 0, 0, 1, 0, -ytop); LAYERG.clearRect(0, ytop, W, bh); put(LAYERG, yy);   // sprite drawn in a window that starts at ytop LAYERG.setTransform(1, 0, 0, 1, 0, 0);
    const d = LAYERG.getImageData(0, 0, bw, bh).data;
    for (let i = 0; i < n4; i += 4) { const a = d[i + 3]; if (a) { const k = a / 255; ACC[i] += d[i] * k; ACC[i + 1] += d[i + 1] * k; ACC[i + 2] += d[i + 2] * k; ACC[i + 3] += a; } }
  }
  const od = OUTIMG.data;
  for (let i = 0; i < n4; i += 4) { const A = ACC[i + 3]; if (A > 0) { const k = 255 / A; od[i] = ACC[i] * k; od[i + 1] = ACC[i + 1] * k; od[i + 2] = ACC[i + 2] * k; od[i + 3] = A / N; } else od[i] = od[i + 1] = od[i + 2] = od[i + 3] = 0; }
  LAYERG.setTransform(1, 0, 0, 1, 0, 0); LAYERG.clearRect(0, 0, W, H); LAYERG.putImageData(OUTIMG, 0, ytop); g.drawImage(LAYER, 0, 0);
}
function drawLabel(g, f) {
  const B = LAY.label, k = f - T.b6.label; if (k < 0) return;
  const ax = LAY.ax, ay = B.base - B.ln.cap / 2, fl = k === 0 ? 0.7 : k === 1 ? 0.25 : 0;
  withScale(g, ax, ay, keys(k, [[0, 1.15], [1, 1.06], [2, 1.0]]), () => run(g, B.ln, B.ln.text, B.ox, B.base, { fill: mixc(C.cream, '#fffaf0', fl), label: 'label' }));
  const A = LAY.arrow, ps = clamp((f - T.b6.arrowStart + 1) / (T.b6.arrowShaftEnd - T.b6.arrowStart)), ph = clamp((f - T.b6.arrowShaftEnd + 1) / (T.b6.arrowEnd - T.b6.arrowShaftEnd + 1));
  if (ps > 0) {
    g.save(); g.strokeStyle = C.cream; g.lineWidth = A.w; g.lineCap = 'round'; g.lineJoin = 'round';
    const ys = lerp(A.y0, A.y1, ease.outCubic(ps)); g.beginPath(); g.moveTo(A.x, A.y0); g.lineTo(A.x, ys); g.stroke();
    if (ph > 0) { const e = ease.outCubic(ph), hx = A.head * e, hy = A.head * e; g.beginPath(); g.moveTo(A.x - hx, A.y1 - hy); g.lineTo(A.x, A.y1); g.lineTo(A.x + hx, A.y1 - hy); g.stroke(); }
    g.restore(); track(g, 'gfx:arrow', A.x - A.head, A.y0, A.x + A.head, A.y1);
  }
}

// ---------------------------------------------------------------- frame
function renderFrame(f, t) {
  const g = post.overlay.ctx; g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none'; g.shadowBlur = 0; g.shadowColor = 'rgba(0,0,0,0)';
  g.textRendering = 'geometricPrecision'; g.fontKerning = 'normal';
  const [sx, sy] = shakeAt(f); CUR_SHAKE = [sx, sy]; const dark = f < T.b3.cut;
  g.drawImage(dark ? PAPER_D : PAPER_C, -PAD + sx, -PAD + sy);
  if (dark) { const hit = f === T.b1.slam ? 0.05 : f === T.b1.slam + 1 ? 0.02 : f === T.b2.witch ? 0.035 : 0; if (hit) { g.fillStyle = rgba(C.cream, hit); g.fillRect(0, 0, W, H); } }   // 1-2 frame exposure kick on the paper hits
  g.save(); g.translate(sx, sy);
  if (!dark) drawLetter(g, f);
  // everything that is printed or written goes through one ink layer, so both cards share one material (speckled dropout, no vector-clean type)
  INKG.setTransform(1, 0, 0, 1, 0, 0); INKG.clearRect(0, 0, W, H); INKG.globalAlpha = 1; INKG.globalCompositeOperation = 'source-over'; INKG.filter = 'none'; INKG.shadowBlur = 0; INKG.shadowColor = 'rgba(0,0,0,0)'; INKG.textRendering = 'geometricPrecision'; INKG.fontKerning = 'normal';
  if (dark) { if (f < T.beats[1].f0) drawB1(INKG, f); else drawB2(INKG, f); }
  else { drawT1(INKG, f, t); drawT2(INKG, f); drawT3(INKG, f); }
  INKG.globalCompositeOperation = 'destination-out'; INKG.drawImage(INKNOISE, 0, 0); INKG.globalCompositeOperation = 'source-over';
  g.drawImage(INK, 0, 0);
  if (!dark) drawLabel(g, f);
  g.restore();
  if (DBG_SAFE) {
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = 'rgba(255,0,200,0.30)';
    const x0 = SAFE.x0 * W, x1 = SAFE.x1 * W, y0 = SAFE.y0 * H, y1 = SAFE.y1 * H;
    g.fillRect(0, 0, W, y0); g.fillRect(0, y1, W, H - y1); g.fillRect(0, y0, x0, y1 - y0); g.fillRect(x1, y0, W - x1, y1 - y0);
    g.strokeStyle = 'rgba(0,255,255,0.95)'; g.lineWidth = 2; g.strokeRect(x0, y0, x1 - x0, y1 - y0); g.restore();
  }
}

await boot({
  fps: FPS, shots: SHOTS, fonts: [['Bebas Neue', 400]],
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; U = H / 1280;
    for (const spec of ['italic 500 40px "Cormorant Garamond"', 'italic 600 40px "Cormorant Garamond"']) await document.fonts.load(spec, 'Hisa,.');
    await document.fonts.ready;
    MG = mk(8, 8).getContext('2d');
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x000000);
    const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 10);
    post = makeComposer(ctx.renderer, scene, camera, { grade: 'none', finish: { grain: 0.04, vignette: 0.3, halation: 0, highlightTint: [0.03, 0.015, 0.0] } });
    LAY = buildLayout();
    PAPER_D = bakeDark(W + 2 * PAD, H + 2 * PAD); PAPER_C = bakeCream(W + 2 * PAD, H + 2 * PAD); INKNOISE = bakeInkNoise(W, H);
    INK = mk(W, H); INKG = INK.getContext('2d'); TMP = mk(W, H); TMPG = TMP.getContext('2d'); LAYER = mk(W, H); LAYERG = LAYER.getContext('2d', { willReadFrequently: true });
    LETTER = bakeLetter();
    if (AUDIT === 'all') {                                                         // text-box audit over the whole timeline, no compositing
      AUDIT_ON = true; const viol = {}, x0 = SAFE.x0 * W - 1, x1 = SAFE.x1 * W + 1, y0 = SAFE.y0 * H - 1, y1 = SAFE.y1 * H + 1, seen = {};
      for (let f = 0; f < T.total; f++) {
        BOXES = []; renderFrame(f, f / FPS);
        for (const b of BOXES) { seen[b.label] = (seen[b.label] || 0) + 1; if (b.x0 < x0 || b.x1 > x1 || b.y0 < y0 || b.y1 > y1) (viol[b.label] = viol[b.label] || []).push(f); }
      }
      AUDIT_ON = false;
      console.log('[audit] safe rect px: x ' + x0.toFixed(0) + '..' + x1.toFixed(0) + ' y ' + y0.toFixed(0) + '..' + y1.toFixed(0) + '; labels tracked: ' + Object.keys(seen).length);
      for (const [lab, fr] of Object.entries(viol)) console.log('[audit] OUTSIDE ' + lab + ' frames ' + fr.join(','));
      if (!Object.keys(viol).length) console.log('[audit] no box leaves the safe rect on any frame');
    }
  },
  render: async (ctx, i, t) => { renderFrame(i, t); post.render(t); },
});
