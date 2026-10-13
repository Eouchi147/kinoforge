// P02 "INK & EMBER" — motion-comic noir, 10 s @ 24 fps (240 f), 1280x720.
// Everything is drawn procedurally with Canvas 2D into the kit overlay (over a black three.js scene), so the kit's finish
// pass gives the scene ONE grade: halftone dots in shadows (mode 3), grain, vignette, halation on highlights only.
// Deterministic: seeded rng, all animation keyed to the frame index. Authoring space is 1280x720 (scaled for other sizes).
import * as THREE from 'three';
import { boot, makeComposer, ease, rng, clamp, lerp, smoothstep, noise1, valueNoise2D } from '/harness/kit/film.js';

// ================================================================ timing (integer frames — cuts and audio cues share exact times)
const FPS = 24, SF = [62, 68, 57, 12, 41];                                   // 240 f = 10.000 s
const S0 = SF.map((_, k) => SF.slice(0, k).reduce((a, b) => a + b, 0));     // first frame of each shot: 0, 62, 130, 187, 199
const SHOTS = [
  { name: 'S1 city EWS 24mm truck + lightning', dur: SF[0] / FPS },
  { name: 'S2 courier MCU 85mm locked', dur: SF[1] / FPS },
  { name: 'S3 hand + seal ECU 40mm push', dur: SF[2] / FPS },
  { name: 'S4 ink-blot wipe (silence)', dur: SF[3] / FPS },
  { name: 'S5 chapter card', dur: SF[4] / FPS },
];
const KEY = { flash: 26, dart: 101, blink: 108, breath: [72, 110], drop: 168 };  // global frames
const shotOf = (i) => { let n = 0; while (n < 4 && i >= S0[n + 1]) n++; const f = i - S0[n]; return { n, f, u: f / (SF[n] - 1) }; };

// ================================================================ palette (Ink & Ember style sheet)
const C = { ink: '#0B0B0D', navy: '#141A26', slate: '#3B4654', bone: '#D9CFBC', teal: '#1F4E5A', amber: '#C98A2E', ember: '#9E1B1B' };
const RGB = (h) => [1, 3, 5].map((k) => parseInt(h.slice(k, k + 2), 16));
const col = (h, a = 1) => `rgba(${RGB(h).join(',')},${a})`;
const mixc = (h1, h2, k, a = 1) => { const A = RGB(h1), B = RGB(h2); return `rgba(${A.map((v, j) => Math.round(lerp(v, B[j], k))).join(',')},${a})`; };
const AMBER_D = mixc(C.amber, C.ink, 0.58);       // warm half-shadow band (gets halftone dots)
const BONE_HOT = mixc(C.bone, C.amber, 0.22);     // hot edge of the lantern key
const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };

// ================================================================ path + brush-ink helpers
// parse absolute SVG-ish paths (M L C Z) into a Path2D (fills/clips) and sampled polylines (for ink ribbons)
function parse(d) {
  const tk = d.match(/[MLCZ]|-?\d*\.?\d+/g); const subs = []; let cur = null, i = 0, cmd = '', x = 0, y = 0;
  const n = () => +tk[i++];
  while (i < tk.length) {
    if (/[MLCZ]/.test(tk[i])) cmd = tk[i++];
    if (cmd === 'M') { x = n(); y = n(); cur = [[x, y]]; subs.push({ pts: cur, closed: false }); cmd = 'L'; }
    else if (cmd === 'L') { x = n(); y = n(); cur.push([x, y]); }
    else if (cmd === 'C') {
      const a = n(), b = n(), c2 = n(), d2 = n(), e = n(), f = n();
      const L = Math.hypot(a - x, b - y) + Math.hypot(c2 - a, d2 - b) + Math.hypot(e - c2, f - d2); const k = Math.max(6, Math.ceil(L / 5));
      for (let j = 1; j <= k; j++) { const t = j / k, m = 1 - t; cur.push([m * m * m * x + 3 * m * m * t * a + 3 * m * t * t * c2 + t * t * t * e, m * m * m * y + 3 * m * m * t * b + 3 * m * t * t * d2 + t * t * t * f]); }
      x = e; y = f;
    } else if (cmd === 'Z') { const s = subs[subs.length - 1]; s.closed = true; cur.push([...s.pts[0]]); cmd = ''; }
    else i++;
  }
  return { p2d: new Path2D(d), subs };
}
// smooth curve through points (Catmull-Rom), returns a dense polyline
function spline(P, per = 8) {
  const out = [];
  for (let k = 0; k < P.length - 1; k++) {
    const p0 = P[Math.max(0, k - 1)], p1 = P[k], p2 = P[k + 1], p3 = P[Math.min(P.length - 1, k + 2)];
    for (let j = 0; j < per; j++) {
      const t = j / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map((q) => 0.5 * (2 * p1[q] + (-p0[q] + p2[q]) * t + (2 * p0[q] - 5 * p1[q] + 4 * p2[q] - p3[q]) * t2 + (-p0[q] + 3 * p1[q] - 3 * p2[q] + p3[q]) * t3)));
    }
  }
  out.push([...P[P.length - 1]]); return out;
}
const densify = (P, step = 8) => { const out = []; for (let k = 0; k < P.length - 1; k++) { const [a, b] = [P[k], P[k + 1]]; const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / step)); for (let j = 0; j < n; j++) out.push([lerp(a[0], b[0], j / n), lerp(a[1], b[1], j / n)]); } out.push([...P[P.length - 1]]); return out; };
// brush-ink ribbon: a filled stroke whose width is modulated by seeded noise along its length, tapered at open ends.
// returns the centre point of the last drawn sample (the brush head) so draw-on strokes can add a wet blob there.
function ribbon(g, pts, w, seed = 1, { taper = 0.15, vary = 0.7, freq = 0.035, closed = false, upto = 1 } = {}) {
  const N = pts.length; if (N < 2 || upto <= 0) return null;
  const s = new Float32Array(N); for (let k = 1; k < N; k++) s[k] = s[k - 1] + Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
  const L = s[N - 1] || 1, Lmax = L * upto; const A = [], B = []; let head = pts[0];
  for (let k = 0; k < N; k++) {
    if (s[k] > Lmax + 1e-6) break;
    const a = pts[Math.max(0, k - 1)], b = pts[Math.min(N - 1, k + 1)]; let tx = b[0] - a[0], ty = b[1] - a[1]; const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
    const u = s[k] / L, tp = closed ? 1 : 0.18 + 0.82 * Math.min(smoothstep(0, taper, u), smoothstep(0, taper, 1 - u));
    const nz = clamp(0.5 + 0.55 * noise1(s[k] * freq, seed)), hw = 0.5 * w * (1 - vary * 0.5 + vary * nz) * tp;
    A.push([pts[k][0] - ty * hw, pts[k][1] + tx * hw]); B.push([pts[k][0] + ty * hw, pts[k][1] - tx * hw]); head = pts[k];
  }
  if (A.length < 2) return null;
  g.beginPath(); g.moveTo(A[0][0], A[0][1]); for (const p of A) g.lineTo(p[0], p[1]); for (let k = B.length - 1; k >= 0; k--) g.lineTo(B[k][0], B[k][1]); g.closePath(); g.fill();
  return head;
}
const inkShape = (g, shape, w, seed, opts = {}) => shape.subs.forEach((sp, k) => ribbon(g, sp.pts, w, seed + k * 7, { closed: sp.closed, ...opts }));
// crescent = shape minus the shape shifted by (dx,dy): the rim of the side facing AWAY from the shift (i.e. toward the light)
function crescent(g, p2d, dx, dy, style) {
  g.save(); g.clip(p2d); const inv = new Path2D(); inv.rect(-4000, -4000, 9000, 9000); inv.addPath(p2d, new DOMMatrix([1, 0, 0, 1, dx, dy]));
  g.clip(inv, 'evenodd'); g.fillStyle = style; g.fillRect(-4000, -4000, 9000, 9000); g.restore();
}
// cel light bands from a hard key: dir points from the light toward the shadow side; bands widest (darkest) first
const lightBands = (g, p2d, dir, bands) => { for (const [w, st] of bands) crescent(g, p2d, dir[0] * w, dir[1] * w, st); };
// baked-canvas rim: crescent of src's alpha on the side opposite to (dx,dy), filled with colour
function rimOf(src, dx, dy, color) {
  const cv = mk(src.width, src.height), g = cv.getContext('2d');
  g.drawImage(src, 0, 0); g.globalCompositeOperation = 'source-in'; g.fillStyle = color; g.fillRect(0, 0, cv.width, cv.height);
  g.globalCompositeOperation = 'destination-out'; g.drawImage(src, dx, dy); return cv;
}
function blurred(src, r) { const cv = mk(src.width, src.height), g = cv.getContext('2d'); g.filter = `blur(${r}px)`; g.drawImage(src, 0, 0); return cv; }
const quadPath = (q) => { const p = new Path2D(); p.moveTo(...q[0]); for (const v of q.slice(1)) p.lineTo(...v); p.closePath(); return p; };
// periodic angular noise (integer harmonics -> no seam at 2π)
function angNoise(seed, harm = [2, 3, 5, 8, 13, 21]) { const r = rng(seed); const ph = harm.map(() => r() * 6.2832); return (a) => harm.reduce((s, m, k) => s + Math.sin(m * a + ph[k]) / Math.sqrt(m), 0) * 0.45; }

// ================================================================ paper
function bakePaper(w, h, { seed = 3, base = [22, 23, 27], mott = 5, tooth = 5, fibers = 900, fiber = [70, 72, 76], fiberA = 0.09 } = {}) {
  const cv = mk(w, h), g = cv.getContext('2d'), img = g.createImageData(w, h), d = img.data, n = valueNoise2D(seed);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const m = n.fbm(x / 210, y / 210, 3) - 0.5, t1 = n(x / 1.7 + 50.3, y / 1.7 + 11.9) - 0.5, t2 = n(x / 5.3 + 7.1, y / 5.3 + 3.3) - 0.5;
    const v = m * mott * 2 + t1 * tooth + t2 * tooth * 0.8, k = (y * w + x) * 4;
    d[k] = base[0] + v; d[k + 1] = base[1] + v; d[k + 2] = base[2] + v * 1.05; d[k + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const r = rng(seed + 11); g.lineCap = 'round';
  for (let k = 0; k < fibers; k++) {
    const x = r() * w, y = r() * h, a = r() * 6.2832, L = 4 + r() * 22, bend = (r() - 0.5) * 0.8;
    g.strokeStyle = `rgba(${fiber.join(',')},${fiberA * (0.4 + r())})`; g.lineWidth = 0.5 + r() * 0.8; g.beginPath(); g.moveTo(x, y);
    g.quadraticCurveTo(x + Math.cos(a + bend) * L * 0.5, y + Math.sin(a + bend) * L * 0.5, x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke();
  }
  return cv;
}

// ================================================================ rain (deterministic streaks; length ∝ nearness = 180° shutter of the fall speed)
function rain(g, L, t, ox = 0, oy = 0, tint = null, lit = null) {
  const r = rng(L.seed), [ax, ay, aw, ah] = L.area; const P = [new Path2D(), new Path2D()];
  for (let k = 0; k < L.n; k++) {
    const x0 = r() * aw, ph = r(), sp = L.speed * (0.82 + 0.36 * r()), len = L.len * (0.7 + 0.6 * r());
    const span = ah + len * 2, yy = ((ph * span + t * sp) % span) - len;
    const y = ay + yy + oy, x = ax + ((((x0 + ox + yy * L.slant) % aw) + aw) % aw);
    const p = lit && Math.hypot(x - lit[0], y - lit[1]) < lit[2] ? P[1] : P[0];
    p.moveTo(x, y); p.lineTo(x + len * L.slant, y + len);
  }
  g.save(); g.lineCap = 'round'; g.lineWidth = L.wid; g.strokeStyle = tint || L.col; g.stroke(P[0]);
  if (lit) { g.strokeStyle = lit[3]; g.lineWidth = L.wid * 1.15; g.stroke(P[1]); }
  g.restore();
}

// ================================================================ page layout (frame coords). Panels are hand-ruled quads.
const LAY = {
  P1: [[40, 34], [1240, 36], [1239, 686], [41, 684]],
  P1s: [[40, 34], [348, 34], [314, 686], [40, 686]],      // S2: city strip (dimmed)
  P2: [[368, 34], [1240, 36], [1239, 686], [334, 684]],   // S2: courier
  P2s: [[40, 34], [296, 34], [266, 686], [40, 686]],      // S3: courier strip (dimmed)
  P3: [[316, 40], [1240, 34], [1236, 686], [286, 680]],   // S3: hand + letter (slightly skewed = tension)
};
function panel(g, q, content, { ox = 0, oy = 0, dim = 0, border = 1, seed = 1, bw = 6 } = {}) {
  const p = quadPath(q);
  g.save(); g.clip(p); g.translate(ox, oy); content(g); g.restore();
  if (dim) { g.fillStyle = col(C.ink, dim); g.fill(p); }
  g.fillStyle = C.ink; const head = ribbon(g, densify([...q, q[0]], 6), bw, seed, { closed: border >= 1, upto: border, vary: 0.55, freq: 0.02, taper: 0.02 });
  if (border < 1 && head) { g.beginPath(); g.arc(head[0], head[1], bw * 0.75, 0, 6.2832); g.fill(); }  // wet brush head while drawing on
}
function caption(g, text, x, y, alpha, seed) {
  if (alpha <= 0) return;
  g.save(); g.globalAlpha = alpha; g.font = 'italic 400 27px "IM Fell English"';
  const tw = g.measureText(text).width, bw = tw + 30, bh = 42;
  g.fillStyle = C.bone; g.beginPath(); g.moveTo(x - 1, y + 1); g.lineTo(x + bw + 1, y - 1); g.lineTo(x + bw, y + bh + 1); g.lineTo(x, y + bh); g.closePath(); g.fill();
  g.globalCompositeOperation = 'multiply'; g.drawImage(TOOTH, x, y, bw, bh, x, y, bw, bh); g.globalCompositeOperation = 'source-over';
  g.fillStyle = C.ink; ribbon(g, densify([[x, y], [x + bw, y - 1], [x + bw, y + bh], [x, y + bh], [x, y]], 6), 2.6, seed, { closed: true, vary: 0.6, freq: 0.05 });
  g.textBaseline = 'middle'; g.fillText(text, x + 15, y + bh / 2 + 2);
  g.restore();
}

// ================================================================ S1 — the city (content space 1200x652; origin = P1 top-left)
const CW = 1500, CH = 660, COX = 150, CITY_F = 853;          // canvases are wider than the panel for the truck; 24 mm ≈ 853 px focal
const DEP = { far: 800, mid: 90, street: 30, near: 18, rf: 40, rm: 12, rn: 4 };
const SPIRE = [392, 236], LANTERN1 = [800, 546], COURIER1 = [786, 616];
const FLASH = { 26: 1.0, 27: 0.3, 28: 0.78, 29: 0.26, 30: 0.15, 31: 0.08, 32: 0.045, 33: 0.02 };
const BOLT_A = { 26: 1, 27: 0.3, 28: 0.85, 29: 0.18 };
let SKY, SKY_LIT, FAR, FAR_RIM, FAR_FL, MID, MID_RIM, MID_FL, STREET, NEAR, NEAR_RIM, NEAR_FL, BOLT;
const R1 = {
  far: { seed: 501, n: 700, len: 11, wid: 0.9, speed: 520, slant: 0.16, area: [-60, -20, 1340, 700], col: 'rgba(120,134,146,0.20)' },
  mid: { seed: 502, n: 260, len: 25, wid: 1.25, speed: 1100, slant: 0.17, area: [-60, -30, 1340, 720], col: 'rgba(150,160,168,0.26)' },
  near: { seed: 503, n: 56, len: 66, wid: 2.6, speed: 2600, slant: 0.18, area: [-80, -80, 1380, 820], col: 'rgba(175,180,182,0.15)' },
};
function bakeSky(lit) {
  const cv = mk(CW, CH), g = cv.getContext('2d'), img = g.createImageData(CW, CH), d = img.data, n = valueNoise2D(41), m = valueNoise2D(43);
  const stops = [[0, [17, 22, 33]], [0.3, [22, 30, 44]], [0.44, [28, 40, 55]], [0.53, [34, 58, 69]], [0.6, [46, 84, 92]], [0.66, [40, 74, 82]], [0.76, [26, 44, 52]], [1, [15, 22, 28]]];
  const grad = (v) => { for (let k = 1; k < stops.length; k++) if (v <= stops[k][0]) { const [a0, c0] = stops[k - 1], [a1, c1] = stops[k]; const u = (v - a0) / (a1 - a0); return c0.map((x, j) => lerp(x, c1[j], u)); } return stops[stops.length - 1][1]; };
  const bx = SPIRE[0] + COX - 60, by = 40;
  for (let y = 0; y < CH; y++) {
    const v = y / CH, base = grad(v), under = smoothstep(0.12, 0.55, v);
    for (let x = 0; x < CW; x++) {
      const cl = n.fbm(x / 430, y / 112, 5), dens = smoothstep(0.36, 0.7, cl), edge = smoothstep(0.44, 0.6, cl) - smoothstep(0.62, 0.8, cl);
      const st = m(x / 1.6, y / 30) - 0.5, k = (y * CW + x) * 4; let r, gg, b;
      if (!lit) { const s = 1 - 0.42 * dens; r = base[0] * s + 10 * edge * under + 6 * edge + st * 3; gg = base[1] * s + 20 * edge * under + 7 * edge + st * 3; b = base[2] * s + 22 * edge * under + 9 * edge + st * 4; }
      else {
        const fall = Math.exp(-Math.hypot(x - bx, (y - by) * 1.25) / 520), lum = (0.22 + 0.78 * fall) * (0.5 + 0.6 * dens + 0.4 * edge);
        r = lerp(58, 236, lum) + st * 8; gg = lerp(66, 231, lum) + st * 8; b = lerp(80, 220, lum) + st * 8;
      }
      d[k] = r; d[k + 1] = gg; d[k + 2] = b; d[k + 3] = 255;
    }
  }
  g.putImageData(img, 0, 0); return cv;
}
function bakeFar() {
  const cv = mk(CW, CH), g = cv.getContext('2d'), r = rng(77), tops = []; g.fillStyle = '#18202c';
  for (let x = 0; x < CW;) {
    const w = r.range(16, 52), top = 378 - r.range(0, 30) - (r() < 0.18 ? r.range(12, 34) : 0);
    g.fillRect(x, top, w + 1, CH - top); tops.push([x, w, top]);
    if (r() < 0.3) g.fillRect(x + w * r.range(0.2, 0.7), top - r.range(6, 16), 4, 20);
    x += w;
  }
  const sx = SPIRE[0] + COX;   // gothic spire (the lightning rod)
  g.beginPath(); g.moveTo(sx - 15, 390); g.lineTo(sx - 15, 300); g.lineTo(sx - 10, 294); g.lineTo(sx, SPIRE[1]); g.lineTo(sx + 10, 294); g.lineTo(sx + 15, 300); g.lineTo(sx + 15, 390); g.fill();
  for (const o of [-24, 24]) { g.beginPath(); g.moveTo(sx + o - 4, 334); g.lineTo(sx + o, 314); g.lineTo(sx + o + 4, 334); g.fill(); g.fillRect(sx + o - 4, 334, 8, 60); }
  g.beginPath(); g.moveTo(sx + 15, 338); g.lineTo(sx + 128, 338); g.lineTo(sx + 140, 356); g.lineTo(sx + 15, 356); g.fill();
  const dx = 760 + COX; g.fillRect(dx - 34, 330, 68, 60); g.beginPath(); g.ellipse(dx, 331, 34, 30, 0, Math.PI, 0); g.fill(); g.fillRect(dx - 2, 292, 4, 14);
  g.fillRect(1092 + COX, 292, 11, 100);
  g.globalCompositeOperation = 'source-atop'; const hz = g.createLinearGradient(0, 380, 0, 480); hz.addColorStop(0, 'rgba(36,64,74,0)'); hz.addColorStop(1, 'rgba(36,64,74,0.85)'); g.fillStyle = hz; g.fillRect(0, 280, CW, CH);
  g.globalCompositeOperation = 'source-over';
  for (let k = 0; k < 110; k++) { const t = tops[Math.floor(r() * tops.length)]; const wx = t[0] + 3 + r() * (t[1] - 6), wy = t[2] + 6 + r() * 70; if (wy > 446) continue; g.fillStyle = col(C.amber, 0.3 + 0.5 * r()); g.fillRect(Math.round(wx), Math.round(wy), 2, 2); }
  return cv;
}
function bakeMid() {
  const cv = mk(CW, CH), g = cv.getContext('2d'), r = rng(91), FILL = '#0e1219', bld = [];
  for (let x = -20; x < CW;) {
    const w = r.range(60, 150), top = r.range(424, 470), type = r.int(0, 3); bld.push({ x, w, top });
    g.fillStyle = FILL; g.fillRect(x, top, w + 1, CH - top);
    const roofH = type === 1 ? r.range(18, 34) : type === 2 ? 16 : 0;
    if (type === 1) { g.beginPath(); g.moveTo(x - 2, top); g.lineTo(x + w / 2, top - roofH); g.lineTo(x + w + 2, top); g.fill(); }
    else if (type === 2) { g.beginPath(); g.moveTo(x, top); g.lineTo(x + 10, top - 16); g.lineTo(x + w - 10, top - 16); g.lineTo(x + w, top); g.fill(); }
    else if (type === 3) { g.fillRect(x, top - 6, w, 6); g.fillRect(x + 3, top - 9, w - 6, 3); }
    for (let k = r.int(0, 2); k > 0; k--) { const cx = x + r.range(0.15, 0.8) * w, ch = r.range(16, 30), cw = r.range(8, 14), cy = top - ch - roofH * 0.5; g.fillRect(cx, cy, cw, ch + 20); g.fillRect(cx + 1, cy - 5, cw / 2 - 1.5, 6); g.fillRect(cx + cw / 2 + 0.5, cy - 4, cw / 2 - 1.5, 5); }
    if (r() < 0.14) { const tx = x + r.range(0.2, 0.6) * w; g.fillRect(tx, top - 34, 26, 20); g.beginPath(); g.moveTo(tx - 2, top - 34); g.lineTo(tx + 13, top - 46); g.lineTo(tx + 28, top - 34); g.fill(); g.fillRect(tx + 2, top - 14, 2, 14); g.fillRect(tx + 22, top - 14, 2, 14); }
    if (r() < 0.2) { const ax = x + r.range(0.1, 0.9) * w; g.fillRect(ax, top - 42, 1.5, 42); g.fillRect(ax - 7, top - 36, 15, 1.5); }
    x += w;
  }
  for (const b of bld) for (let wy = b.top + 14; wy < CH - 10; wy += 22) for (let wx = b.x + 8; wx < b.x + b.w - 10; wx += 17) {
    const p = r(); if (p < 0.15) { g.fillStyle = col(C.amber, 0.4 + 0.55 * r()); g.fillRect(wx, wy, 5, 8); } else if (p < 0.22) { g.fillStyle = 'rgba(40,52,64,0.7)'; g.fillRect(wx, wy, 5, 8); }
  }
  return cv;
}
function tinyCourier(g, cx, fy, s = 1.25) {   // the courier seen from a rooftop: hooded silhouette, lantern rim on her right
  g.save(); g.translate(cx, fy); g.scale(s, s);
  const P = new Path2D('M -11 0 L -8 -24 C -9 -33 -11 -40 -7 -45 C -3 -49 5 -48 7 -42 L 5 -36 L 6 -27 L 12 0 Z');
  g.fillStyle = C.ink; g.fill(P); crescent(g, P, -2.2, 1.4, col(C.amber, 1)); crescent(g, P, -0.8, 0.5, BONE_HOT);
  g.restore();
  const rf = g.createLinearGradient(0, fy, 0, fy + 34); rf.addColorStop(0, 'rgba(8,8,10,0.9)'); rf.addColorStop(1, 'rgba(8,8,10,0)'); g.fillStyle = rf; g.fillRect(cx - 11, fy, 22, 34);
}
function bakeStreet() {
  const cv = mk(CW, CH), g = cv.getContext('2d'), X = (x) => x + COX, r = rng(66);
  // facade across the street: stone courses, pilasters, cornice, a doorway; lit only near the lantern
  g.fillStyle = '#151c27'; g.fillRect(X(520), 454, 580, 170);
  g.fillStyle = '#0d1118'; g.fillRect(X(514), 444, 592, 10); g.fillRect(X(514), 500, 592, 4);
  for (let k = 0; k < 7; k++) { g.fillStyle = '#10151e'; g.fillRect(X(540 + k * 84), 454, 9, 160); }
  for (let k = 0; k < 9; k++) { const wx = X(556 + k * 58), lit = r() < 0.32; g.fillStyle = lit ? col(C.amber, 0.6) : '#0b0e14'; g.fillRect(wx, 470, 14, 22); g.fillStyle = r() < 0.15 ? col(C.amber, 0.35) : '#0b0e14'; g.fillRect(wx, 524, 14, 22); }
  g.fillStyle = '#07090c'; g.fillRect(X(690), 522, 34, 92); g.fillStyle = '#0d1118'; g.fillRect(X(686), 516, 42, 6);
  g.fillStyle = '#0c1118'; g.fillRect(X(520), 614, 580, CH - 614);
  const LX = X(LANTERN1[0]), LY = LANTERN1[1];
  let gr = g.createRadialGradient(LX, LY, 2, LX, LY, 150); gr.addColorStop(0, col(C.amber, 0.78)); gr.addColorStop(0.28, col(C.amber, 0.3)); gr.addColorStop(1, col(C.amber, 0)); g.fillStyle = gr; g.fillRect(LX - 160, LY - 160, 320, 320);
  gr = g.createLinearGradient(0, 614, 0, CH); gr.addColorStop(0, col(C.amber, 0.7)); gr.addColorStop(1, col(C.amber, 0.05)); g.fillStyle = gr; g.fillRect(LX - 8, 614, 16, CH - 614);
  for (let k = 0; k < 34; k++) { g.fillStyle = col(C.amber, 0.25 + 0.5 * r()); g.fillRect(LX - 70 + r() * 140, 618 + r() * 40, 3 + r() * 7, 1.3); }
  g.fillStyle = C.ink; g.fillRect(LX, LY - 16, 18, 3); g.fillRect(LX - 6, LY - 12, 12, 3.5);
  g.fillStyle = '#F6E6BE'; g.fillRect(LX - 4.5, LY - 9, 9, 12); g.fillStyle = C.ink; g.fillRect(LX - 6, LY + 3, 12, 3); g.fillRect(LX - 0.8, LY - 9, 1.6, 12);
  tinyCourier(g, X(COURIER1[0]), COURIER1[1]);
  return cv;
}
function bakeNear() {
  const cv = mk(CW, CH), g = cv.getContext('2d'), X = (x) => x + COX; g.fillStyle = C.ink;
  const roofL = [[X(-160), 376], [X(130), 304], [X(318), 316], [X(660), CH + 10]];
  g.beginPath(); g.moveTo(...roofL[0]); for (const p of roofL.slice(1)) g.lineTo(...p); g.lineTo(X(-160), CH + 10); g.fill();
  const box = (x, y, w, h) => g.fillRect(X(x), y, w, h);
  box(58, 228, 58, 110); box(54, 220, 66, 10); box(64, 204, 13, 18); box(84, 208, 12, 14); box(100, 202, 11, 20);
  box(372, 372, 42, 70); box(368, 366, 50, 8); box(378, 354, 12, 14); box(396, 356, 11, 12);
  box(735, 478, 60, 200); box(728, 470, 74, 9); box(740, 450, 14, 22); box(760, 454, 13, 18); box(779, 446, 12, 26);
  g.beginPath(); g.moveTo(X(1004), CH + 10); g.lineTo(X(1004), 336); g.lineTo(X(990), 332); g.lineTo(X(990), 320); g.lineTo(X(1034), 320); g.lineTo(X(1058), 270); g.lineTo(X(1420), 262); g.lineTo(X(1420), CH + 10); g.fill();
  g.beginPath(); g.moveTo(X(1112), 300); g.lineTo(X(1112), 262); g.lineTo(X(1138), 238); g.lineTo(X(1164), 262); g.lineTo(X(1164), 300); g.fill();
  box(1238, 214, 3, 50); box(1229, 222, 21, 2);  // lightning rod
  // wet roof tiles: faint slate courses parallel to the eaves (rain catches the sky)
  g.save(); g.globalCompositeOperation = 'source-atop'; g.strokeStyle = 'rgba(59,70,84,0.30)'; g.lineWidth = 1.2;
  for (let k = 1; k < 18; k++) { const o = k * 19; g.beginPath(); g.moveTo(X(318 - 340), 316 + o * 0.15 + o); g.lineTo(X(318 + o * 0.55), 316 + o); g.stroke(); }
  g.restore();
  // lit dormer window (a practical)
  g.fillStyle = C.amber; g.fillRect(X(1126), 268, 24, 28); g.fillStyle = col('#F0D9A6', 0.85); g.fillRect(X(1129), 272, 8, 10);
  g.fillStyle = C.ink; g.fillRect(X(1137), 268, 2.5, 28); g.fillRect(X(1126), 281, 24, 2.5);
  // brushy ink edges along the silhouettes facing the sky
  ribbon(g, densify(roofL.slice(0, 3).map(([x, y]) => [x, y]), 6), 5, 61, { vary: 0.8, freq: 0.03 });
  ribbon(g, densify([[X(1004), 420], [X(1004), 336], [X(990), 332], [X(990), 320], [X(1034), 320], [X(1058), 270], [X(1420), 262]], 6), 5, 62, { vary: 0.8, freq: 0.03 });
  return cv;
}
function bakeBolt() {
  const r = rng(2026);
  const mid = (a, b, depth, disp) => { if (!depth) return [a, b]; const m = [(a[0] + b[0]) / 2 + (r() - 0.5) * disp, (a[1] + b[1]) / 2 + (r() - 0.5) * disp * 0.35]; return [...mid(a, m, depth - 1, disp * 0.55).slice(0, -1), ...mid(m, b, depth - 1, disp * 0.55)]; };
  const main = mid([262, -8], [SPIRE[0], SPIRE[1] - 2], 6, 120);
  const branches = [0.22, 0.4, 0.58].map((q, k) => { const p = main[Math.floor(q * main.length)]; const end = [p[0] + (k === 1 ? 70 : -60 - 30 * k), p[1] + 70 + 30 * k]; return mid(p, end, 4, 40); });
  return { main, branches };
}
function drawBolt(g, a) {
  g.save(); g.lineJoin = 'round'; g.lineCap = 'round';
  for (const [w, al, c] of [[18, 0.10, C.bone], [7, 0.28, C.bone], [3.2, 0.9, '#F4EFE6'], [1.5, 1, '#FFFFFF']]) {
    g.strokeStyle = c; g.globalAlpha = al * a;
    g.lineWidth = w; g.beginPath(); BOLT.main.forEach((p, k) => (k ? g.lineTo(...p) : g.moveTo(...p))); g.stroke();
    g.lineWidth = w * 0.55; for (const b of BOLT.branches) { g.beginPath(); b.forEach((p, k) => (k ? g.lineTo(...p) : g.moveTo(...p))); g.stroke(); }
  }
  g.restore();
}
function drawCity(g, i, camX) {
  const t = i / FPS, fl = FLASH[i] || 0, off = (D) => -camX * CITY_F / D;
  g.drawImage(SKY, -COX, 0);
  if (fl) { g.globalAlpha = fl; g.drawImage(SKY_LIT, -COX, 0); g.globalAlpha = 1; }
  if (BOLT_A[i]) drawBolt(g, BOLT_A[i]);
  const layer = (img, rim, flr, D) => { const x = -COX + off(D); g.drawImage(img, x, 0); if (rim) g.drawImage(rim, x, 0); if (fl && flr) { g.globalAlpha = fl; g.drawImage(flr, x, 0); g.globalAlpha = 1; } };
  const rt = fl ? mixc('#8896a2', C.bone, fl, 0.25 + 0.45 * fl) : null;
  layer(FAR, FAR_RIM, FAR_FL, DEP.far);
  rain(g, R1.far, t, off(DEP.rf), 0, rt);
  layer(MID, MID_RIM, MID_FL, DEP.mid);
  layer(STREET, null, null, DEP.street);
  const lx = LANTERN1[0] + off(DEP.street);
  rain(g, R1.mid, t, off(DEP.rm), 0, rt, [lx, LANTERN1[1] + 10, 85, col(C.amber, 0.55)]);
  layer(NEAR, NEAR_RIM, NEAR_FL, DEP.near);
  rain(g, R1.near, t, off(DEP.rn), 0, rt);
}

// ================================================================ S2 — the courier under the lantern (content 906x652, origin = P2 bbox top-left)
// The figure is authored in a "sheet" frame and drawn scaled 1.3x about (560,280) -> (600,286) so the face fills an MCU.
const CS = { s: 1.3, ax: 560, ay: 280, bx: 600, by: 286 };
const toS2 = ([x, y]) => [CS.bx + (x - CS.ax) * CS.s, CS.by + (y - CS.ay) * CS.s];
const L2 = [-0.72, 0.70];                 // light direction: from the lantern (upper right) toward lower left
const LANT = { px: 792, py: 50 };         // lantern pivot (hook) in S2 content coords
const lanternAng = (t) => 0.05 * Math.cos(2 * Math.PI * (t - 2.9) / 2.4);   // swing extremes at 2.9 s and 4.1 s = the two creaks
const CO = {
  coat: parse('M 40 700 C 70 610 140 548 236 510 C 320 478 420 464 500 466 C 590 470 660 510 700 580 C 716 612 726 660 730 700 Z'),
  hood: parse('M 240 520 C 248 470 256 420 262 380 C 268 330 274 280 278 236 C 280 214 276 194 264 172 C 290 146 330 120 386 110 C 440 102 494 106 536 122 C 568 136 592 152 606 176 C 616 194 616 208 604 216 C 594 222 580 216 566 208 L 520 210 L 488 300 L 470 420 L 340 530 Z'),
  neck: parse('M 430 330 L 532 362 C 556 372 580 396 596 428 C 608 452 616 486 622 530 L 330 572 Z'),
  hoodEdge: parse('M 248 500 C 252 450 258 410 262 380 C 268 330 274 280 278 236 C 280 214 276 194 264 172 C 290 146 330 120 386 110 C 440 102 494 106 536 122 C 568 136 592 152 606 176 C 616 194 616 208 604 216'),
  hem: parse('M 598 206 C 604 192 596 174 582 160 C 562 142 536 130 508 124'),
  fold1: parse('M 590 186 C 566 178 534 176 504 184 C 480 190 460 200 446 212'),
  fold2: parse('M 486 396 C 440 356 392 306 344 236 C 330 214 322 196 318 182'),
  fold3: parse('M 474 202 C 450 190 420 186 392 190'),
  face: parse('M 498 196 C 524 189 548 191 562 199 C 566 209 570 220 568 230 C 566 236 562 240 563 246 C 568 260 582 276 591 287 C 593 292 586 296 576 295 C 572 298 575 304 578 308 C 575 313 569 314 571 317 C 575 321 575 328 569 332 C 563 336 563 343 559 350 C 554 360 542 364 528 366 L 500 380 L 468 300 Z'),
  profile: parse('M 562 199 C 566 209 570 220 568 230 C 566 236 562 240 563 246 C 568 260 582 276 591 287 C 593 292 586 296 576 295 C 572 298 575 304 578 308 C 575 313 569 314 571 317 C 575 321 575 328 569 332 C 563 336 563 343 559 350 C 554 360 542 364 528 366'),
  flap: parse('M 604 216 C 594 222 580 216 566 208 C 548 198 522 198 504 208 C 484 222 474 252 476 292 C 478 330 492 360 516 386 L 470 420 L 400 330 L 430 210 C 470 180 560 176 604 216 Z'),
  flapEdge: parse('M 612 206 C 606 218 590 220 566 208 C 548 198 522 198 504 208 C 484 222 474 252 476 292 C 478 330 492 360 516 386'),
  patch: parse('M 440 368 L 494 380 L 508 448 L 436 456 Z'),   // plain ink under the jaw: hides the hood's inner-edge key band where the flap ends
  nose: parse('M 561 250 C 566 264 570 276 568 287 C 566 291 570 293 574 293'),
  mouth: parse('M 571 317 C 563 318 556 318 550 316'),
};
const SHADOW_UP = (() => { const p = new Path2D(); p.moveTo(660, 156); p.lineTo(300, 516); p.lineTo(300, 0); p.lineTo(660, 0); p.closePath(); return p; })();
const LIT_DOWN = (() => { const p = new Path2D(); p.moveTo(660, 156); p.lineTo(300, 516); p.lineTo(300, 700); p.lineTo(660, 700); p.closePath(); return p; })();
let BG2, PIL2, BEADS;
const R2 = {
  far: { seed: 601, n: 260, len: 16, wid: 1.0, speed: 700, slant: 0.17, area: [-40, -20, 990, 700], col: 'rgba(110,122,134,0.18)' },
  mid: { seed: 602, n: 120, len: 34, wid: 1.4, speed: 1500, slant: 0.18, area: [-40, -40, 990, 740], col: 'rgba(150,158,164,0.24)' },
  near: { seed: 603, n: 22, len: 120, wid: 4.5, speed: 3600, slant: 0.19, area: [-60, -120, 1030, 900], col: 'rgba(160,166,170,0.10)' },
};
function bakeBG2() {   // the street behind her through an 85 mm lens: compressed, defocused, darker
  const cv = mk(980, 720), g = cv.getContext('2d'), X = (x) => x + 30, r = rng(212);
  let gr = g.createLinearGradient(0, 0, 0, 720); gr.addColorStop(0, '#182031'); gr.addColorStop(0.55, '#202a3c'); gr.addColorStop(1, '#1a2431'); g.fillStyle = gr; g.fillRect(0, 0, 980, 720);
  gr = g.createRadialGradient(X(60), 720, 10, X(60), 720, 300); gr.addColorStop(0, col(C.teal, 0.85)); gr.addColorStop(1, col(C.teal, 0)); g.fillStyle = gr; g.fillRect(0, 0, 980, 720);
  gr = g.createRadialGradient(X(200), 230, 10, X(200), 230, 300); gr.addColorStop(0, 'rgba(48,70,82,0.5)'); gr.addColorStop(1, 'rgba(48,70,82,0)'); g.fillStyle = gr; g.fillRect(0, 0, 980, 720);
  // defocused facades: soft darker masses, so the window lights sit on something
  for (const [x, y, rx, ry] of [[60, 260, 160, 420], [420, 520, 220, 160]]) { const m = g.createRadialGradient(X(x), y, 10, X(x), y, Math.max(rx, ry)); m.addColorStop(0, 'rgba(12,15,22,0.5)'); m.addColorStop(1, 'rgba(12,15,22,0)'); g.fillStyle = m; g.fillRect(0, 0, 980, 720); }
  const spots = [[96, 150, 34, 46, 1], [168, 60, 24, 36, 1], [236, 300, 40, 26, 0.8], [40, 360, 26, 40, 0.9], [330, 40, 22, 28, 0.7], [690, 470, 30, 42, 0.8], [790, 330, 20, 30, 0.6], [400, 590, 46, 24, 0.7], [130, 480, 24, 30, 0.9], [640, 560, 36, 26, 0.7], [250, 180, 18, 18, 0.6], [60, 60, 30, 20, 0.6], [470, 40, 26, 34, 0.5]];
  for (const [x, y, w, h, a] of spots) { g.fillStyle = col(r() < 0.8 ? C.amber : C.bone, a * (0.45 + 0.35 * r())); g.beginPath(); g.roundRect(X(x), y, w, h, 7); g.fill(); }
  gr = g.createRadialGradient(X(170), 110, 4, X(170), 110, 60); gr.addColorStop(0, 'rgba(240,214,160,0.9)'); gr.addColorStop(1, 'rgba(201,138,46,0)'); g.fillStyle = gr; g.fillRect(X(100), 40, 140, 140);
  g.strokeStyle = 'rgba(130,140,150,0.10)'; g.lineWidth = 1.5; for (let k = 0; k < 260; k++) { const x = r() * 980, y = r() * 720; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 4, y + 26); g.stroke(); }
  return blurred(cv, 10);
}
function bakePilaster() {   // the wall corner the lantern bracket is fixed to (right edge of P2), lit by the lantern
  const cv = mk(80, 720), g = cv.getContext('2d');
  g.fillStyle = '#10141b'; g.fillRect(0, 0, 80, 720);
  const gr = g.createRadialGradient(0, 80, 4, 0, 80, 330); gr.addColorStop(0, col(C.amber, 0.7)); gr.addColorStop(0.4, col(C.amber, 0.2)); gr.addColorStop(1, col(C.amber, 0)); g.fillStyle = gr; g.fillRect(0, 0, 80, 720);
  g.fillStyle = 'rgba(8,8,10,0.9)'; for (let y = 22, k = 0; y < 720; y += 46, k++) { g.fillRect(0, y, 80, 3); g.fillRect(k % 2 ? 30 : 56, y - 43, 3, 43); }
  g.fillStyle = C.ink; ribbon(g, densify([[2, 0], [3, 720]], 8), 5, 71, { vary: 0.7 });
  return cv;
}
function drawLantern(g, t, flick) {
  const ang = lanternAng(t);
  g.save(); g.translate(LANT.px, LANT.py); g.rotate(ang);
  g.fillStyle = C.ink;
  g.beginPath(); g.moveTo(-5, 10); g.lineTo(5, 10); g.lineTo(34, 30); g.lineTo(-34, 30); g.closePath(); g.fill(); g.fillRect(-37, 29, 74, 7); g.fillRect(-3, 2, 6, 10);
  const gl = g.createLinearGradient(0, 36, 0, 96); gl.addColorStop(0, '#E2B86C'); gl.addColorStop(0.45, '#F4E2B6'); gl.addColorStop(1, '#C98A2E');
  g.fillStyle = gl; g.beginPath(); g.moveTo(-27, 36); g.lineTo(27, 36); g.lineTo(21, 96); g.lineTo(-21, 96); g.closePath(); g.fill();
  const fc = g.createRadialGradient(0, 64, 1, 0, 64, 15); fc.addColorStop(0, `rgba(255,250,236,${0.95 * flick})`); fc.addColorStop(1, 'rgba(255,240,205,0)'); g.fillStyle = fc; g.fillRect(-20, 44, 40, 40);
  g.fillStyle = C.ink;
  ribbon(g, [[-27, 34], [-21, 98]], 4.5, 81, { taper: 0.01, vary: 0.3 }); ribbon(g, [[27, 34], [21, 98]], 4.5, 82, { taper: 0.01, vary: 0.3 });
  ribbon(g, [[-9, 36], [-7, 96]], 2, 83, { taper: 0.01 }); ribbon(g, [[9, 36], [7, 96]], 2, 84, { taper: 0.01 });
  g.beginPath(); g.moveTo(-24, 95); g.lineTo(24, 95); g.lineTo(14, 108); g.lineTo(-14, 108); g.closePath(); g.fill(); g.beginPath(); g.arc(0, 112, 4.5, 0, 6.3); g.fill();
  g.fillStyle = col(C.amber, 0.9); g.fillRect(-35, 36, 70, 2); g.fillStyle = col(C.amber, 0.6); g.fillRect(-22, 97, 44, 2);
  g.restore();
}
function drawBracket(g) {
  g.fillStyle = C.ink;
  ribbon(g, densify([[906, 44], [784, 46]], 6), 6.5, 91, { taper: 0.05, vary: 0.4 });
  ribbon(g, densify([[906, 112], [834, 48]], 6), 4.5, 92, { taper: 0.05, vary: 0.4 });
  const sc = []; for (let k = 0; k <= 36; k++) { const a = k / 36 * 9, rr = 3 + k * 0.4; sc.push([846 + Math.cos(a + 2) * rr, 68 + Math.sin(a + 2) * rr * 0.8]); } ribbon(g, sc, 3.2, 93, { taper: 0.2 });
  g.beginPath(); g.arc(LANT.px, LANT.py - 1, 4, 0, 6.3); g.fill();
}
function breathLift(t) { let b = 0; for (const e of [3.0, 4.583]) { const x = t - e; b += x < 0 ? smoothstep(-0.9, 0, x) : 1 - smoothstep(0, 0.8, x); } return b; }
function gazeAt(i, mode) {
  if (mode === 'down') return [2.6, 2.4];
  const G0 = [2.8, 1.0], G1 = [-3.6, -0.3], k = i - KEY.dart;
  const w = k < -1 ? 0 : k === -1 ? -0.15 : k === 0 ? 0.5 : k === 1 ? 0.88 : 1;
  return [lerp(G0[0], G1[0], w), lerp(G0[1], G1[1], w)];
}
const openAt = (i) => { const k = i - KEY.blink; return k < 0 || k > 5 ? 1 : [0.5, 0.12, 0, 0.35, 0.72, 0.95][k]; };   // 2 / 1 / 3 frames
function eye(g, cx, cy, hw, hh, open, gx, gy, seed) {
  g.save(); g.translate(cx, cy); g.rotate(-0.06);
  const h = hh * open;
  if (open > 0.05) {
    const al = new Path2D(); al.moveTo(-hw, 0); al.quadraticCurveTo(-hw * 0.1, -h * 2.1, hw, -0.5); al.quadraticCurveTo(0, h * 1.5, -hw, 0); al.closePath();
    g.fillStyle = '#2a3240'; g.fill(al);
    g.save(); g.clip(al); g.fillStyle = '#0c0e13'; g.beginPath(); g.arc(gx, gy, hh * 1.05, 0, 6.3); g.fill();
    if (open > 0.45) { g.fillStyle = C.bone; g.beginPath(); g.ellipse(gx + 0.8, gy - 0.8, 1.9, 1.6, 0, 0, 6.3); g.fill(); }
    g.restore();
  }
  g.fillStyle = C.ink; ribbon(g, spline([[-hw - 2.5, 0.8], [-hw * 0.3, -h * 1.12 - 0.8], [hw * 0.5, -h * 0.95 - 0.8], [hw + 1.5, 0]], 6), 2.8, seed, { taper: 0.3, vary: 0.4 });
  if (open < 0.4) { g.fillStyle = '#414b5a'; ribbon(g, spline([[-hw - 1, 0.6], [0, 1.9], [hw, 0.3]], 6), 1.6, seed + 1, { taper: 0.3 }); }
  g.restore();
}
function breathPuff(g, i, f0, mx, my) {
  const k = (i - f0) / FPS; if (k < 0 || k > 1.5) return;
  const r = rng(f0 * 13 + 1);
  for (let j = 0; j < 8; j++) {
    const d = r(), ang = -0.32 + (r() - 0.5) * 0.55, dist = (16 + 96 * d) * ease.outCubic(clamp(k / 1.25));
    const x = mx + 8 + Math.cos(ang) * dist, y = my + Math.sin(ang) * dist - 16 * k, rad = 6 + (26 + 36 * d) * ease.outQuad(clamp(k / 1.15));
    const a = 0.26 * smoothstep(0, 0.1, k) * (1 - smoothstep(0.3, 1.4, k)) * (0.6 + 0.4 * r());
    const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, `rgba(226,200,156,${a})`); gr.addColorStop(1, 'rgba(226,200,156,0)');
    g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
}
function drip(g, i, fForm, fFall, x0, y0) {
  if (i < fForm) return;
  if (i < fFall) { const k = (i - fForm) / (fFall - fForm), rr = 1.2 + 2.6 * k; g.fillStyle = BONE_HOT; g.beginPath(); g.ellipse(x0, y0 + rr, rr * 0.8, rr * 1.2, 0, 0, 6.3); g.fill(); return; }
  const s = (i - fFall) / FPS, y = y0 + 0.5 * 5200 * s * s, yp = y0 + 0.5 * 5200 * Math.max(0, s - 1 / 48) ** 2; if (yp > 700) return;
  g.strokeStyle = col(C.bone, 0.85 * (1 - smoothstep(260, 620, y))); g.lineWidth = 2.8; g.lineCap = 'round'; g.beginPath(); g.moveTo(x0 + (yp - y0) * 0.18, yp); g.lineTo(x0 + (y - y0) * 0.18, Math.max(y, yp + 5)); g.stroke();
}
function hoodFold(g, shape, seed, lit, hue = C.amber, dir = L2) {   // fabric fold: ink crease + a catch-light on the side facing its light
  g.fillStyle = C.ink; inkShape(g, shape, 3.0, seed, { taper: 0.35 });
  if (lit) { g.fillStyle = col(hue, lit); inkShape(g, { subs: shape.subs.map((s) => ({ ...s, pts: s.pts.map(([x, y]) => [x - dir[0] * 2.6, y - dir[1] * 2.6]) })) }, 1.6, seed + 3, { taper: 0.45 }); }
}
function drawCourier(g, i, mode) {
  const t = i / FPS, t2 = Math.floor(i / 2) * 2 / FPS;          // character animation on 2s
  const dy = -1.6 * breathLift(t2) - 0.4 * Math.sin(t2 * 2.4);
  g.save(); g.translate(CS.bx, CS.by + dy); g.scale(CS.s, CS.s); g.translate(-CS.ax, -CS.ay);
  // coat + neck in shadow
  g.fillStyle = C.ink; g.fill(CO.coat.p2d);
  crescent(g, CO.coat.p2d, 5, 1, C.teal); lightBands(g, CO.coat.p2d, L2, [[13, AMBER_D], [6, C.amber], [2, BONE_HOT]]);
  g.fillStyle = C.ink; g.fill(CO.neck.p2d); lightBands(g, CO.neck.p2d, L2, [[9, AMBER_D], [4, C.amber], [1.6, BONE_HOT]]);
  // hood: cowl with a drooping peak, teal rim behind, lantern key in front, seam + drape folds
  g.fillStyle = C.ink; g.fill(CO.hood.p2d);
  crescent(g, CO.hood.p2d, 5, 2, C.teal); lightBands(g, CO.hood.p2d, L2, [[17, AMBER_D], [8, C.amber], [2.6, BONE_HOT]]);
  hoodFold(g, CO.fold1, 201, 0.45); hoodFold(g, CO.fold2, 203, 0.9, '#2b6676', [0.8, 0.6]); hoodFold(g, CO.fold3, 205, 0);
  g.fillStyle = C.ink; g.fill(CO.patch.p2d);
  // face: soft cheek light under the brim shadow, cel bands on the profile, brim shadow over the eyes
  g.fillStyle = C.ink; g.fill(CO.face.p2d);
  g.save(); g.clip(CO.face.p2d); g.clip(LIT_DOWN); const cg = g.createRadialGradient(552, 306, 2, 552, 306, 50); cg.addColorStop(0, col(C.amber, 0.46)); cg.addColorStop(1, col(C.amber, 0)); g.fillStyle = cg; g.fillRect(480, 240, 130, 140); g.restore();
  lightBands(g, CO.face.p2d, L2, [[10, AMBER_D], [5.2, C.amber], [2.1, BONE_HOT]]);
  g.save(); g.clip(CO.face.p2d); g.fillStyle = C.ink; g.fill(SHADOW_UP); g.restore();
  // eyes (in the brim shadow): glints, dart, blink
  const [gx, gy] = gazeAt(i, mode), op = mode === 'down' ? 0.8 : openAt(i);
  eye(g, 522, 247, 10, 4.0, op, gx, gy, 101); eye(g, 557, 244, 5.0, 3.5, op, gx * 0.55 + 0.6, gy, 103);
  g.fillStyle = C.ink; inkShape(g, CO.nose, 2.0, 111, { taper: 0.3 }); inkShape(g, CO.mouth, 1.8, 113, { taper: 0.4 });
  // hood side flap (frames the face), hem seam, outer ink
  g.fillStyle = C.ink; g.fill(CO.flap.p2d);
  inkShape(g, CO.flapEdge, 3.4, 121, { taper: 0.12 }); inkShape(g, CO.hoodEdge, 4.4, 123, { taper: 0.08 }); inkShape(g, CO.profile, 2.2, 125, { taper: 0.1 });
  g.fillStyle = C.ink; inkShape(g, CO.hem, 2.2, 127, { taper: 0.3 });
  // a strand of hair escaping the hood, blown forward, catching the lantern
  const sw = 2.0 * Math.sin(t2 * 2.3) + 1.0 * Math.sin(t2 * 5.1 + 1);
  const hp = spline([[588, 214], [594 + sw * 0.3, 228], [600 + sw * 0.7, 244], [598 + sw, 262]], 8);
  g.fillStyle = C.ink; ribbon(g, hp, 2.8, 131, { taper: 0.35 }); g.fillStyle = BONE_HOT; ribbon(g, hp.map(([x, y]) => [x + 0.8, y - 0.4]), 1.1, 133, { taper: 0.45 });
  // rain beads on the lit top of the hood
  for (const [x, y, rr] of BEADS) { g.fillStyle = 'rgba(8,8,10,0.8)'; g.beginPath(); g.arc(x - 0.5, y + 0.7, rr, 0, 6.3); g.fill(); g.fillStyle = BONE_HOT; g.beginPath(); g.arc(x, y, rr * 0.75, 0, 6.3); g.fill(); }
  g.restore();
  return dy;
}
function drawCourierPanel(g, i, mode) {
  const t = i / FPS, flick = 1 + 0.04 * noise1(t * 9, 4);
  g.drawImage(BG2, -30, -34);
  rain(g, R2.far, t);
  g.drawImage(PIL2, 868, -10);
  const gx = LANT.px - 64 * Math.sin(lanternAng(t)), gy = LANT.py + 64;
  g.save(); g.globalCompositeOperation = 'lighter'; const hl = g.createRadialGradient(gx, gy, 6, gx, gy, 240); hl.addColorStop(0, col(C.amber, 0.30 * flick)); hl.addColorStop(1, col(C.amber, 0)); g.fillStyle = hl; g.fillRect(gx - 250, gy - 250, 500, 500); g.restore();
  const dy = drawCourier(g, i, mode);
  drawBracket(g); drawLantern(g, t, flick);
  rain(g, R2.mid, t, 0, 0, null, [gx, gy + 20, 170, col(C.amber, 0.5)]);
  if (mode !== 'down') {
    const [bx, by] = toS2([607, 216]), [mx, my] = toS2([577, 318]);
    drip(g, i, 80, 93, bx, by + dy); drip(g, i, 112, 123, bx, by + dy);
    for (const f0 of KEY.breath) breathPuff(g, i, f0, mx, my + dy);
  }
  rain(g, R2.near, t);
}

// ================================================================ S3 — the letter (content 950x652, origin = P3 bbox top-left)
const ENV = { w: 512, h: 308, pad: 24, cx: 616, cy: 290, rot: -0.1 };
const envPt = (lx, ly) => [ENV.cx + lx * Math.cos(ENV.rot) - ly * Math.sin(ENV.rot), ENV.cy + lx * Math.sin(ENV.rot) + ly * Math.cos(ENV.rot)];
const SEAL_POS = envPt(-7, 30);                       // the flap tip; also the push-in centre and the blot origin
const THUMB = { x: 392, y: 470, ang: Math.atan2(SEAL_POS[1] - 470, SEAL_POS[0] - 392) };
const HD = {
  mass: parse('M 130 700 C 160 640 204 590 252 552 C 270 538 284 528 296 520 C 290 486 292 446 304 414 C 312 394 326 386 342 388 C 362 390 384 396 404 404 L 424 520 C 386 580 352 640 336 700 Z'),
  massEdge: parse('M 150 680 C 176 630 214 586 252 552 C 270 538 284 528 296 520 C 290 486 292 446 304 414 C 312 394 326 386 342 388'),
  fingerGap: parse('M 297 518 C 306 500 320 486 344 474'),
  thumb: parse('M -56 -34 C 0 -38 60 -36 110 -30 C 140 -27 162 -24 172 -12 C 180 -1 178 14 164 21 C 150 27 120 28 90 29 C 40 32 0 36 -56 42 Z'),
  thumbTop: parse('M -30 -36 C 20 -37 70 -35 110 -30 C 140 -27 162 -24 172 -12 C 180 -1 178 14 164 21'),
  thumbBot: parse('M 164 21 C 150 27 120 28 90 29 C 40 32 0 36 -40 41'),
  crease: parse('M 104 -30 C 99 -18 98 -6 101 6'),
  sleeve: parse('M -80 540 C 60 530 180 580 270 652 L 330 720 L -80 720 Z'),
  cuff: parse('M 196 590 C 236 604 270 628 296 660 L 276 690 C 250 660 214 636 176 622 Z'),
};
const GLOVE = '#1b1d22';
let BG3, ENVC, SEALC, SEAL_SMALL;
const R3 = {
  mid: { seed: 701, n: 150, len: 30, wid: 1.4, speed: 1300, slant: 0.18, area: [-60, -40, 1080, 740], col: 'rgba(160,162,160,0.22)' },
  near: { seed: 702, n: 24, len: 110, wid: 4.2, speed: 3400, slant: 0.19, area: [-80, -120, 1120, 900], col: 'rgba(170,170,166,0.10)' },
};
function bakeBG3() {   // wet cobbles far below the letter (her POV), defocused; the lantern's reflection lies in a puddle
  const cv = mk(1060, 780), g = cv.getContext('2d'), r = rng(333);
  g.fillStyle = '#0a0b0d'; g.fillRect(0, 0, 1060, 780);
  for (let y = -10; y < 790;) {
    const h = 30 + y * 0.035; let x = -r() * 40;
    while (x < 1080) { const w = h * r.range(1.1, 1.7); g.fillStyle = mixc('#1d2024', '#30343a', r()); g.beginPath(); g.roundRect(x + 3, y + 3, w - 6, h - 6, 8); g.fill(); g.fillStyle = 'rgba(160,164,170,0.38)'; g.beginPath(); g.roundRect(x + 7, y + 4, w - 14, 3, 2); g.fill(); x += w; }
    y += h;
  }
  const pud = new Path2D(); const an = angNoise(17); for (let k = 0; k <= 72; k++) { const a = k / 72 * 6.2832, rr = 1 + 0.18 * an(a); const x = 800 + Math.cos(a) * 240 * rr, y = 150 + Math.sin(a) * 110 * rr; k ? pud.lineTo(x, y) : pud.moveTo(x, y); } pud.closePath();
  g.fillStyle = '#0d0e10'; g.fill(pud);
  g.save(); g.clip(pud); const gr = g.createRadialGradient(860, 120, 4, 860, 120, 105); gr.addColorStop(0, 'rgba(226,218,202,0.75)'); gr.addColorStop(0.35, 'rgba(217,207,188,0.25)'); gr.addColorStop(1, 'rgba(217,207,188,0)'); g.fillStyle = gr; g.fillRect(700, 0, 360, 300);
  g.fillStyle = 'rgba(10,10,12,0.9)'; g.fillRect(842, 40, 6, 56); g.restore();
  return blurred(cv, 7);
}
function bakeEnvelope() {
  const { w, h, pad } = ENV, cv = mk(w + pad * 2, h + pad * 2), g = cv.getContext('2d'), hw = w / 2, hh = h / 2, r = rng(444);
  g.translate(pad + hw, pad + hh);
  const gr = g.createLinearGradient(hw * 0.8, -hh, -hw, hh); gr.addColorStop(0, '#D4CAB7'); gr.addColorStop(0.35, '#BAB09D'); gr.addColorStop(0.65, '#888175'); gr.addColorStop(1, '#64605A'); g.fillStyle = gr; g.fillRect(-hw, -hh, w, h);
  g.globalCompositeOperation = 'multiply'; g.drawImage(TOOTH, 0, 0, w, h, -hw, -hh, w, h); g.globalCompositeOperation = 'source-over';
  g.strokeStyle = 'rgba(50,46,40,0.28)'; g.lineWidth = 2; g.beginPath(); g.moveTo(-hw, hh); g.lineTo(-62, 14); g.moveTo(hw, hh); g.lineTo(62, 14); g.stroke();
  // hatching on the shadow side (lower left), comic-ink style
  g.save(); const hz = new Path2D(); hz.moveTo(-hw, -10); hz.lineTo(-hw, hh); hz.lineTo(-30, hh); hz.closePath(); g.clip(hz);
  g.strokeStyle = 'rgba(20,18,16,0.32)'; g.lineWidth = 1.3; for (let k = -40; k < 40; k++) { const o = k * 7; g.beginPath(); g.moveTo(-hw + o, hh + 10); g.lineTo(-hw + o + 200, hh - 190); g.stroke(); }
  g.restore();
  const flap = new Path2D(); flap.moveTo(-hw, -hh); flap.lineTo(-7, 30); flap.lineTo(hw, -hh); flap.closePath();
  g.save(); g.translate(0, 8); g.fillStyle = 'rgba(30,26,22,0.38)'; g.fill(flap); g.restore();
  const fg = g.createLinearGradient(hw, -hh, -hw, 0); fg.addColorStop(0, '#D9D0BE'); fg.addColorStop(1, '#98907E'); g.fillStyle = fg; g.fill(flap);
  g.globalCompositeOperation = 'multiply'; g.save(); g.clip(flap); g.drawImage(TOOTH, 300, 200, w, h, -hw, -hh, w, h); g.restore(); g.globalCompositeOperation = 'source-over';
  g.fillStyle = C.ink;
  ribbon(g, densify([[-hw, -hh], [-7, 30], [hw, -hh]], 6), 2.6, 451, { vary: 0.75, freq: 0.04 });
  // outline heavier on the shadow side (bottom/left), lighter toward the lantern (top/right)
  ribbon(g, densify([[-hw, -hh], [hw, -hh]], 6), 2.2, 452, { vary: 0.7, taper: 0.03 });
  ribbon(g, densify([[hw, -hh], [hw, hh]], 6), 2.8, 453, { vary: 0.7, taper: 0.03 });
  ribbon(g, densify([[hw, hh], [-hw, hh]], 6), 4.8, 454, { vary: 0.7, taper: 0.03 });
  ribbon(g, densify([[-hw, hh], [-hw, -hh]], 6), 4.4, 455, { vary: 0.7, taper: 0.03 });
  for (let k = 0; k < 8; k++) { const x = r.range(-hw + 30, hw - 30), y = r.range(-hh + 40, hh - 20), rr = r.range(5, 15); g.fillStyle = 'rgba(60,54,46,0.24)'; g.beginPath(); g.ellipse(x, y, rr, rr * 0.85, 0, 0, 6.3); g.fill(); g.strokeStyle = 'rgba(236,230,218,0.5)'; g.lineWidth = 1.2; g.beginPath(); g.arc(x, y, rr * 0.92, -2.4, -1.0); g.stroke(); }
  for (let k = 0; k < 12; k++) { const x = r.range(-hw + 20, hw - 20), y = r.range(-hh + 20, hh - 20); g.fillStyle = 'rgba(30,28,26,0.5)'; g.beginPath(); g.arc(x + 0.8, y + 1, 1.8, 0, 6.3); g.fill(); g.fillStyle = 'rgba(246,242,234,0.95)'; g.beginPath(); g.arc(x, y, 1.3, 0, 6.3); g.fill(); }
  return cv;
}
function sealBlob(R) { const an = angNoise(909), P = []; for (let k = 0; k <= 90; k++) { const a = k / 90 * 6.2832; let rr = R * (1 + 0.09 * an(a)); for (const [ca, cl] of [[0.7, 0.22], [2.6, 0.16], [4.4, 0.12]]) rr += R * cl * Math.exp(-((((a - ca + 9.42) % 6.2832 - 3.14) / 0.16) ** 2)); P.push([Math.cos(a) * rr, Math.sin(a) * rr]); } return P; }
function bakeSeal(R) {   // Ember Red wax seal pressed with an eye (the only colour in the film)
  const S = Math.ceil(R * 3.2), cv = mk(S, S), g = cv.getContext('2d'), P = sealBlob(R);
  g.translate(S / 2, S / 2);
  const blob = new Path2D(); P.forEach(([x, y], k) => (k ? blob.lineTo(x, y) : blob.moveTo(x, y))); blob.closePath();
  g.save(); g.translate(2, 4); g.fillStyle = 'rgba(20,10,8,0.45)'; g.fill(blob); g.restore();
  const gr = g.createRadialGradient(-R * 0.3, -R * 0.35, R * 0.1, 0, 0, R * 1.2); gr.addColorStop(0, '#B42626'); gr.addColorStop(0.6, C.ember); gr.addColorStop(1, '#5E0E0E'); g.fillStyle = gr; g.fill(blob);
  g.save(); g.clip(blob);
  g.lineWidth = R * 0.12; g.strokeStyle = 'rgba(60,8,8,0.55)'; g.beginPath(); g.arc(0.8, 1.2, R * 0.7, 0, 6.3); g.stroke();
  g.strokeStyle = 'rgba(214,92,80,0.55)'; g.lineWidth = R * 0.05; g.beginPath(); g.arc(-0.6, -0.8, R * 0.76, 3.6, 5.9); g.stroke();
  const eyeP = (ox, oy) => { const p = new Path2D(); p.moveTo(-R * 0.42 + ox, oy); p.quadraticCurveTo(ox, -R * 0.34 + oy, R * 0.42 + ox, oy); p.quadraticCurveTo(ox, R * 0.34 + oy, -R * 0.42 + ox, oy); p.closePath(); return p; };
  g.lineWidth = R * 0.07; g.strokeStyle = 'rgba(214,92,80,0.6)'; g.stroke(eyeP(0.6, 1.2)); g.strokeStyle = 'rgba(55,6,6,0.85)'; g.stroke(eyeP(0, 0));
  g.fillStyle = 'rgba(55,6,6,0.85)'; g.beginPath(); g.arc(0, 0, R * 0.13, 0, 6.3); g.fill();
  g.fillStyle = 'rgba(236,190,176,0.55)'; g.beginPath(); g.ellipse(R * 0.36, -R * 0.52, R * 0.2, R * 0.08, -0.5, 0, 6.3); g.fill();
  g.restore();
  g.fillStyle = 'rgba(40,6,6,0.9)'; ribbon(g, densify(P, 4), Math.max(1.4, R * 0.05), 911, { closed: true, vary: 0.5 });
  return cv;
}
const GLOVE_BANDS = [[9, '#2a2e35'], [4.5, C.slate], [1.7, mixc(C.bone, C.slate, 0.3)]];
function drawHandMass(g) {
  g.fillStyle = GLOVE; g.fill(HD.mass.p2d);
  lightBands(g, HD.mass.p2d, [0.3, 0.95], GLOVE_BANDS);
  g.save(); g.setLineDash([4, 4]); g.strokeStyle = 'rgba(80,92,106,0.9)'; g.lineWidth = 1.4;   // three stitch lines on the back of the glove
  for (const [a, b] of [[[262, 548], [210, 612]], [[276, 560], [228, 624]], [[290, 572], [246, 636]]]) { g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.stroke(); }
  g.restore();
  g.strokeStyle = 'rgba(120,132,144,0.75)'; g.lineWidth = 1.8; g.beginPath(); g.arc(312, 424, 16, -2.6, -1.4); g.stroke(); g.beginPath(); g.arc(306, 484, 14, -2.8, -1.6); g.stroke();
  g.fillStyle = C.ink; inkShape(g, HD.massEdge, 3.6, 141, { taper: 0.1 }); inkShape(g, HD.fingerGap, 2.6, 143, { taper: 0.3 });
}
function drawThumb(g, f3) {
  const fq = Math.floor(f3 / 2) * 2, kf = f3 - (KEY.drop - S0[2]);   // reach on 2s, flinch on 1s
  const reach = -6 * ease.inOutSine(clamp((fq - 6) / 6)) + 32 * ease.inOutSine(clamp((fq - 12) / 22));
  const flinch = kf < 2 ? 0 : kf < 5 ? -16 * ease.outCubic((kf - 2) / 3) : -16 + 6 * ease.inOutSine(clamp((kf - 5) / 10));
  const d = reach + flinch, t = (S0[2] + f3) / FPS, tr = 0.5 * noise1(t * 6, 3);
  g.save(); g.translate(THUMB.x + Math.cos(THUMB.ang) * d, THUMB.y + Math.sin(THUMB.ang) * d + tr); g.rotate(THUMB.ang + (kf >= 2 && kf < 8 ? 0.025 : 0));
  g.save(); g.translate(4, 7); g.fillStyle = 'rgba(26,22,18,0.42)'; g.fill(HD.thumb.p2d); g.restore();   // contact shadow on the paper
  g.fillStyle = GLOVE; g.fill(HD.thumb.p2d);
  const la = -THUMB.ang - Math.PI / 2;   // world "down" expressed in the thumb's rotated frame
  lightBands(g, HD.thumb.p2d, [Math.cos(la) * -1 + 0.2, Math.sin(la) * -1], GLOVE_BANDS);
  g.save(); g.setLineDash([3.5, 3.5]); g.strokeStyle = 'rgba(80,92,106,0.95)'; g.lineWidth = 1.3; g.beginPath(); g.moveTo(-30, 14); g.quadraticCurveTo(70, 18, 150, 14); g.stroke(); g.restore();
  g.fillStyle = C.ink; inkShape(g, HD.thumbTop, 3.0, 151, { taper: 0.1 }); inkShape(g, HD.thumbBot, 4.2, 152, { taper: 0.1 }); inkShape(g, HD.crease, 2.0, 153, { taper: 0.4 });
  g.strokeStyle = 'rgba(150,156,160,0.6)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(108, -30); g.quadraticCurveTo(104, -20, 105, -12); g.stroke();
  g.restore();
}
function drawSleeve(g) {
  g.fillStyle = GLOVE; g.fill(HD.cuff.p2d); lightBands(g, HD.cuff.p2d, [0.3, 0.95], [[4, '#2a2e35'], [1.6, C.slate]]);
  g.fillStyle = C.ink; g.fill(HD.sleeve.p2d);
  lightBands(g, HD.sleeve.p2d, [0.25, 0.97], [[10, '#16181d'], [4, '#2c333d'], [1.6, C.slate]]);
  g.strokeStyle = 'rgba(44,51,61,0.9)'; g.lineWidth = 2; g.beginPath(); g.moveTo(20, 600); g.quadraticCurveTo(110, 610, 190, 680); g.stroke();
  g.fillStyle = C.ink; ribbon(g, HD.sleeve.subs[0].pts.slice(0, 30), 5, 161, { taper: 0.1 });
}
function dropFx(g, f3) {
  const kf = f3 - (KEY.drop - S0[2]), [sx, sy] = SEAL_POS;
  if (kf >= -3 && kf < 0) { const yy = sy - 6 - [230, 140, 58][kf + 3]; g.strokeStyle = 'rgba(240,236,226,0.9)'; g.lineWidth = 2.6; g.lineCap = 'round'; g.beginPath(); g.moveTo(sx - 9 - 6, yy - 34); g.lineTo(sx - 9, yy); g.stroke(); }
  if (kf < 0) return;
  if (kf <= 1) { const k = kf === 0 ? 1 : 0.45; g.fillStyle = `rgba(244,240,232,${0.95 * k})`; g.beginPath(); g.ellipse(sx - 4, sy - 2, 13 * (kf + 1), 5 * (kf + 1), 0, 0, 6.3); g.fill();
    const cr = rng(177); for (let j = 0; j < 11; j++) { const a = -Math.PI * (0.02 + 0.96 * cr()), rr = (10 + 12 * cr()) * (1 + 0.8 * kf), w = 1.4 + 2.2 * cr(); g.beginPath(); g.ellipse(sx - 4 + Math.cos(a) * rr, sy - 2 + Math.sin(a) * rr * 0.75, w, w * 1.7, a + 1.57, 0, 6.3); g.fill(); } }
  for (const [d0, maxR, w0] of [[1, 92, 4.4], [4, 62, 3.0]]) {
    const k = kf - d0; if (k < 0 || k > 13) continue;
    const rr = 12 + maxR * ease.outCubic(k / 13), a = 1 - smoothstep(5, 13, k), P = [];
    for (let j = 0; j <= 64; j++) { const an = j / 64 * 6.2832; P.push([sx - 4 + Math.cos(an) * rr, sy + Math.sin(an) * rr * 0.92]); }
    g.fillStyle = col(C.ink, 0.92 * a); ribbon(g, P, w0 * (1 - k / 16), 171 + d0, { closed: true, vary: 0.9, freq: 0.08 });
  }
  const r = rng(173);
  for (let j = 0; j < 9; j++) {
    const a = -Math.PI * (0.12 + 0.76 * r()), v = 150 + 170 * r(), s = (kf + 0.5) / FPS; if (kf > 11) break;
    const x = sx - 4 + Math.cos(a) * v * s, y = sy + Math.sin(a) * v * s + 0.5 * 2600 * s * s, rr = 1.4 + 1.6 * r();
    g.fillStyle = col(C.ink, 0.8); g.beginPath(); g.arc(x, y, rr + 0.9, 0, 6.3); g.fill(); g.fillStyle = 'rgba(244,240,232,0.95)'; g.beginPath(); g.arc(x - 0.3, y - 0.3, rr, 0, 6.3); g.fill();
  }
  g.fillStyle = 'rgba(250,240,236,0.85)'; g.beginPath(); g.ellipse(sx + 6, sy - 10, 4.5, 3.2, -0.5, 0, 6.3); g.fill(); g.fillStyle = 'rgba(60,8,8,0.6)'; g.beginPath(); g.arc(sx + 7.5, sy - 7.5, 1.5, 0, 6.3); g.fill();
}
function drawLetterPanel(g, f3) {
  const t = (S0[2] + f3) / FPS, u = Math.max(0, f3) / (SF[2] - 1), dz = 0.054 * Math.pow(u, 1.6);
  const push = (D, fn) => { const s = D / (D - dz); g.save(); g.translate(SEAL_POS[0], SEAL_POS[1]); g.scale(s, s); g.translate(-SEAL_POS[0], -SEAL_POS[1]); fn(); g.restore(); };
  push(1.6, () => {
    g.drawImage(BG3, -40, -60);
    for (let k = 0; k < 5; k++) { const r = rng(800 + k), ph = (t * 1.3 + r()) % 1, x = 690 + r() * 220, y = 70 + r() * 110; g.strokeStyle = `rgba(190,190,186,${0.22 * (1 - ph)})`; g.lineWidth = 1.6; g.beginPath(); g.ellipse(x, y, 4 + ph * 36, (4 + ph * 36) * 0.45, 0, 0, 6.3); g.stroke(); }
  });
  push(1.0, () => rain(g, R3.mid, t));
  push(0.52, () => drawHandMass(g));
  push(0.5, () => {
    g.save(); g.translate(ENV.cx, ENV.cy); g.rotate(ENV.rot); g.drawImage(ENVC, -ENV.w / 2 - ENV.pad, -ENV.h / 2 - ENV.pad); g.restore();
    g.save(); g.translate(SEAL_POS[0], SEAL_POS[1]); g.rotate(ENV.rot); g.drawImage(SEALC, -SEALC.width / 2, -SEALC.height / 2); g.restore();
  });
  push(0.48, () => { drawThumb(g, f3); drawSleeve(g); });
  push(0.5, () => dropFx(g, f3));
  push(0.3, () => rain(g, R3.near, t));
}

// ================================================================ S4 — ink-blot wipe from the seal (on 1s)
const BLOT_R = [26, 66, 124, 200, 296, 410, 545, 705, 895, 1120, 1480, 2400];
const BLOT_N = [angNoise(1201), angNoise(1202, [5, 7, 11, 17, 23, 29])];
const TENDRILS = (() => { const r = rng(1203); return Array.from({ length: 11 }, () => ({ a: r() * 6.2832, len: 0.14 + 0.3 * r(), w: 0.05 + 0.07 * r() })); })();
const SPATTER = (() => { const r = rng(1204); return Array.from({ length: 46 }, () => { const dist = 40 + Math.pow(r(), 1.4) * 720; return { a: r() * 6.2832, dist, rad: 1.5 + r() * (dist < 250 ? 9 : 5), k: Math.min(3, Math.floor(dist / 220)) }; }); })();
function drawBlot(g, k, cx, cy) {
  const R = BLOT_R[Math.min(k, 11)], p = new Path2D();
  for (let j = 0; j <= 200; j++) {
    const a = j / 200 * 6.2832; let rr = R * (1 + 0.16 * BLOT_N[0](a) + 0.06 * BLOT_N[1](a));
    for (const td of TENDRILS) { const da = Math.atan2(Math.sin(a - td.a), Math.cos(a - td.a)); rr += R * td.len * Math.exp(-((da / td.w) ** 2)); }
    const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr; j ? p.lineTo(x, y) : p.moveTo(x, y);
  }
  p.closePath(); g.fillStyle = '#060607'; g.fill(p);
  for (const s of SPATTER) {
    if (k < s.k) continue; const x = cx + Math.cos(s.a) * s.dist, y = cy + Math.sin(s.a) * s.dist;
    g.beginPath(); g.arc(x, y, s.rad, 0, 6.3); g.fill();
    if (k === s.k) { g.lineWidth = s.rad * 1.2; g.strokeStyle = '#060607'; g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y); g.lineTo(x - Math.cos(s.a) * s.dist * 0.25, y - Math.sin(s.a) * s.dist * 0.25); g.stroke(); }
  }
}

// ================================================================ S5 — chapter card
function drawCard(g, f) {
  g.drawImage(PAGE, 0, 0);
  const x0 = 178;
  g.save(); g.textBaseline = 'alphabetic';
  g.font = '400 30px "Oswald"'; g.letterSpacing = '15px'; g.fillStyle = col(C.bone, 0.8); g.fillText('CHAPTER ONE', x0 + 6, 292);
  g.font = '600 158px "Oswald"'; g.letterSpacing = '7px'; g.fillStyle = C.bone; g.fillText('THE SEAL', x0, 462); const tw = g.measureText('THE SEAL').width;
  g.restore();
  g.fillStyle = col(C.bone, 0.55); ribbon(g, densify([[x0 + 6, 318], [x0 + 236, 316]], 6), 3, 1301, { vary: 0.8 });
  g.globalCompositeOperation = 'multiply'; g.drawImage(TOOTH, 0, 0); g.globalCompositeOperation = 'source-over';
  g.save(); g.translate(x0 + tw + 34, 440); g.rotate(-0.18); g.drawImage(SEAL_SMALL, -SEAL_SMALL.width / 2, -SEAL_SMALL.height / 2); g.restore();
}

// ================================================================ boot
let post, PAGE, TOOTH, W, H;
await boot({
  fps: FPS, shots: SHOTS, fonts: [['IM Fell English', 400], ['Oswald', 400], ['Oswald', 600]],
  init: async (ctx) => {
    W = ctx.W; H = ctx.H;
    try { await document.fonts.load('italic 400 27px "IM Fell English"'); } catch (e) { console.log('italic font failed', e); }
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x000000);
    const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 10);
    post = makeComposer(ctx.renderer, scene, camera, { grade: 'halftone', finish: {
      saturation: 1.0, contrast: 1.04, gamma: 1.3, shadowTint: [0, 0, 0], highlightTint: [0, 0, 0],   // no split-tone (teal-orange is forbidden); colour comes from motivated sources
      halation: 0.35, halationThreshold: 0.86, grain: 0.05, grainSize: 1.5, vignette: 0.3, mode: 3, modeAmount: 0.6, modeParams: [0.6, 5, 0] } });
    // KIT BUG workaround: the overlay CanvasTexture is tagged sRGB, so the GPU linearises it and nothing re-encodes it
    // (2D colours come out ~2.2 gamma too dark: mid-grey 128 -> 55). Treat the canvas bytes as already display-referred.
    post.overlay.tex.colorSpace = THREE.NoColorSpace; post.overlay.tex.needsUpdate = true;
    PAGE = bakePaper(1280, 720, { seed: 3, base: [38, 37, 35], mott: 6, tooth: 6, fibers: 1300, fiber: [96, 94, 88], fiberA: 0.12 });
    TOOTH = bakePaper(1280, 720, { seed: 5, base: [244, 242, 238], mott: 4, tooth: 9, fibers: 700, fiber: [200, 196, 188], fiberA: 0.25 });
    SKY = bakeSky(false); SKY_LIT = bakeSky(true); BOLT = bakeBolt();
    FAR = bakeFar(); FAR_RIM = rimOf(FAR, 0, 2, '#2b3b46'); FAR_FL = rimOf(FAR, 2, 3, C.bone);
    MID = bakeMid(); MID_RIM = rimOf(MID, 0, 2, '#273843'); MID_FL = rimOf(MID, 2, 3, C.bone);
    STREET = bakeStreet();
    NEAR = bakeNear(); NEAR_RIM = rimOf(NEAR, 1, 3, '#22323c'); NEAR_FL = rimOf(NEAR, 3, 4, C.bone);
    BG2 = bakeBG2(); PIL2 = bakePilaster();
    BEADS = (() => { const r = rng(141), pts = CO.hoodEdge.subs[0].pts.filter(([x, y]) => x > 420 && y < 200), out = []; for (let k = 0; k < pts.length; k += 3) { const [x, y] = pts[k], d = 5 + r() * 12; if (r() < 0.75) out.push([x + L2[0] * d, y + L2[1] * d, 1.1 + r() * 1.1]); } return out; })();
    BG3 = bakeBG3(); ENVC = bakeEnvelope(); SEALC = bakeSeal(42); SEAL_SMALL = bakeSeal(24);
  },
  render: async (ctx, i, t) => {
    const g = post.overlay.ctx; g.setTransform(W / 1280, 0, 0, H / 720, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
    g.fillStyle = '#000'; g.fillRect(0, 0, 1280, 720);
    const { n, f } = shotOf(i);
    if (n === 0) {
      g.drawImage(PAGE, 0, 0);
      const camX = 1.6 * ease.inOutSine(f / (SF[0] - 1)), develop = smoothstep(8, 20, f);
      panel(g, LAY.P1, (c) => { drawCity(c, i, camX); if (develop < 1) { c.globalAlpha = 1 - develop; c.drawImage(PAGE, -40, -34); c.globalAlpha = 1; } },
        { ox: 40, oy: 34, border: smoothstep(1, 10, f), seed: 11, bw: 6.5 });
      caption(g, 'The letter weighed nothing.', 62, 620, clamp((f - 15) / 2), 21);
      if (f < 6) { g.fillStyle = `rgba(0,0,0,${1 - f / 6})`; g.fillRect(0, 0, 1280, 720); }   // the page itself rises out of black
    } else if (n === 1) {
      g.drawImage(PAGE, 0, 0);
      panel(g, LAY.P1s, (c) => drawCity(c, S0[1] - 1, 1.6), { ox: -190, oy: 34, dim: 0.3, seed: 12, bw: 6 });
      panel(g, LAY.P2, (c) => drawCourierPanel(c, i, 'S2'), { ox: 334, oy: 34, seed: 13, bw: 6.5 });
      caption(g, 'She had been told not to look.', 392, 54, clamp((f - 5) / 2), 22);
    } else if (n === 2 || n === 3) {
      g.drawImage(PAGE, 0, 0);
      const f3 = i - S0[2];
      // the previous panel is dimmed AND drained to grey, so the Ember Red seal is the only hue in the frame
      panel(g, LAY.P2s, (c) => { drawCourierPanel(c, i, 'down'); c.globalCompositeOperation = 'saturation'; c.fillStyle = '#808080'; c.fillRect(-2000, -100, 4000, 900); c.globalCompositeOperation = 'source-over'; }, { ox: -432, oy: 34, dim: 0.42, seed: 14, bw: 6 });
      panel(g, LAY.P3, (c) => drawLetterPanel(c, f3), { ox: 286, oy: 34, seed: 15, bw: 6.5 });
      if (n === 3) drawBlot(g, f, 286 + SEAL_POS[0], 34 + SEAL_POS[1]);
    } else {
      drawCard(g, f);
    }
    g.globalCompositeOperation = 'multiply'; g.drawImage(TOOTH, 0, 0); g.globalCompositeOperation = 'source-over';
    post.render(t);
  },
});
