// Figures for the detail layer: walkers (planted-foot gait), hooded leaders with lanterns, riders and horses, banners, torches, sparks.
// All drawn in design px (720x1280) on a Canvas2D context; shapes are built in "h units" (figure height = 1) under a local transform.
import { clamp, lerp, smoothstep, ease, noise1 } from '/harness/kit/film.js';
import { rgba, mixc, hex } from './paint.js';

export const hash1 = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
export const PAL = { cloak: hex('#1c1a2c'), cloak2: hex('#26233a'), dark: hex('#14131f'), skin: hex('#0e0d16'), staff: hex('#2b2531'), frame: hex('#1c1414'),
  paperLit: hex('#ffe0a6'), paperOff: hex('#5f586c'), purple: hex('#4b2468'), purpleLit: hex('#76409a'), gold: hex('#d9a845'), goldLit: hex('#ffd983'), red: hex('#6b2420'), redLit: hex('#a8423a'), wood: hex('#3a2c26') };

function ik(hip, end, a, b, bendSign = 1) {
  const dx = end[0] - hip[0], dy = end[1] - hip[1]; const d = Math.min(Math.hypot(dx, dy), a + b - 1e-4);
  const c = clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1); const base = Math.atan2(dy, dx); const ang = base + bendSign * Math.acos(c);
  return [hip[0] + a * Math.cos(ang), hip[1] + a * Math.sin(ang)];
}
const smoothPath = (pts) => { const p = new Path2D(); const n = pts.length; p.moveTo((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2);
  for (let i = 1; i <= n; i++) { const a = pts[i % n], b = pts[(i + 1) % n]; p.quadraticCurveTo(a[0], a[1], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2); } p.closePath(); return p; };

// planted-foot gait: stance foot slides back at exactly the body speed (no skating); swing foot arcs forward. ph in cycles.
export function footAt(ph, side, L, lift = 0.05) {
  const p = ((ph + side * 0.5) % 1 + 1) % 1; const ST = 0.58;
  if (p < ST) { const u = p / ST; return [L * 0.29 * (1 - 2 * u), 0, 0]; }
  const u = (p - ST) / (1 - ST); const e = ease.inOutSine(u); return [lerp(-L * 0.29, L * 0.29, e), lift * Math.sin(Math.PI * Math.pow(u, 0.85)), 0.5 * Math.sin(Math.PI * u) * 0.0];
}

// A walker in local h units. o: { x, y (feet on the ground, px), h (px), face (+1 right, -1 left), ph (gait cycle 0..1), walk (0..1),
//   col, col2 (robe), hood, head (tilt, rad, + looks up), reach:[dx,dy] (hand target in h units, relative to own feet), lantern:{on}, staff,
//   carry:'none', cape:colour, crown:true, seed }
// returns anchors in px: { shoulder, hand, lantern, head }
export const STRIDE = 0.6;   // body travel per foot cycle, in figure heights (ph = distance / (STRIDE * h))
export function person(g, o) {
  const h = o.h, face = o.face || 1, ph = o.ph || 0, walk = o.walk ?? 1; const L = STRIDE * (o.stride ?? 1);
  const A = {}; g.save(); g.translate(o.x, o.y); g.scale(face * h, -h);
  const lw = (w) => Math.max(w, 1.1 / h);
  const f0 = footAt(ph, 0, L * walk), f1 = footAt(ph, 1, L * walk);
  const bob = 0.012 * walk * Math.cos(4 * Math.PI * ph + 0.6); const hip = [0.0, 0.5 + bob];
  const lean = 0.05 * walk; const lc = (p) => { const c = Math.cos(-lean), s = Math.sin(-lean); const dx = p[0] - hip[0], dy = p[1] - hip[1]; return [hip[0] + dx * c - dy * s, hip[1] + dx * s + dy * c]; };
  const col = o.col || PAL.cloak, col2 = o.col2 || PAL.cloak2, dark = o.dark || PAL.dark;
  g.lineCap = 'round'; g.lineJoin = 'round';
  const leg = (f, c, w) => { const ank = [f[0] + 0.02, f[1] + 0.04]; const kn = ik(hip, ank, 0.26, 0.26, 1); g.strokeStyle = rgba(c); g.lineWidth = lw(w); g.beginPath(); g.moveTo(hip[0], hip[1]); g.lineTo(kn[0], kn[1]); g.lineTo(ank[0], ank[1]); g.stroke();
    g.fillStyle = rgba(c); g.beginPath(); g.ellipse(f[0] + 0.045, f[1] + 0.022, 0.058, 0.028, 0, 0, 7); g.fill(); };
  leg(f1, mixc(dark, col, 0.4), 0.062);
  // staff (far hand), planted with the far foot
  if (o.staff) { const tipx = f1[0] + 0.17 * 0 + 0.2; g.strokeStyle = rgba(PAL.staff); g.lineWidth = lw(0.026); g.beginPath(); g.moveTo(tipx - 0.02 * walk, 0.0); g.lineTo(0.13, 0.8); g.stroke(); }
  // far arm (hangs / grips staff)
  const shF = lc([0.0, 0.795]); { const hd = o.staff ? [0.13, 0.62] : [0.02 - 0.03 * walk * Math.sin(2 * Math.PI * ph), 0.52]; const el = ik(shF, hd, 0.17, 0.16, -1); g.strokeStyle = rgba(mixc(dark, col, 0.5)); g.lineWidth = lw(0.05); g.beginPath(); g.moveTo(shF[0], shF[1]); g.lineTo(el[0], el[1]); g.lineTo(hd[0], hd[1]); g.stroke(); }
  leg(f0, dark, 0.07);
  // robe / cloak
  const hem = o.hem ?? 0.2, sway = 0.02 * Math.sin(2 * Math.PI * ph) * walk, tr = -0.04 * walk;
  const body = [lc([0.05, 0.83]), lc([0.095, 0.68]), lc([0.115, 0.42]), lc([0.135 + (f0[0] > f1[0] ? f0[0] : f1[0]) * 0.18, hem + 0.015]), lc([0.05, hem - 0.015 + sway * 0.4]), lc([-0.05, hem - 0.005]),
    lc([-0.15 + tr, hem + 0.02 + sway]), lc([-0.13 + tr * 0.5, 0.4]), lc([-0.1, 0.68]), lc([-0.065, 0.82])];
  const bp = smoothPath(body); g.fillStyle = rgba(col); g.fill(bp);
  if (h > 90) { g.save(); g.clip(bp); const gr = g.createLinearGradient(-0.15, 0.85, 0.15, 0.2); gr.addColorStop(0, rgba(col2, 0.55)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.fillRect(-0.3, 0, 0.6, 1); g.strokeStyle = rgba(dark, 0.45); g.lineWidth = 0.008;
    for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(lc([-0.07 + k * 0.05, 0.74])[0], 0.74); g.quadraticCurveTo(-0.08 + k * 0.05 + tr, 0.45, -0.1 + k * 0.06 + tr * 1.5, hem + 0.02); g.stroke(); } g.restore(); }
  if (o.cape) { const cp = smoothPath([lc([-0.04, 0.84]), lc([-0.17 + tr, 0.7]), lc([-0.22 + tr * 2, 0.3]), lc([-0.16 + tr * 2, hem - 0.03]), lc([-0.05, 0.4]), lc([0.02, 0.7])]); g.fillStyle = rgba(o.cape); g.fill(cp); }
  // head + hood
  const nk = lc([0.012, 0.86]); const hr = 0.064; const tilt = (o.head ?? -0.1 * walk) - lean * 0.3; const hc = [nk[0] + Math.sin(-tilt) * 0.0 + 0.012, nk[1] + 0.075];
  g.save(); g.translate(nk[0], nk[1]); g.rotate(-tilt); g.translate(-nk[0], -nk[1]);
  if (o.hood !== false) { const hp = smoothPath([[nk[0] - 0.075, nk[1] - 0.01], [nk[0] - 0.1, nk[1] + 0.07], [nk[0] - 0.12 + tr * 0.5, nk[1] + 0.17], [nk[0] - 0.03, nk[1] + 0.2], [nk[0] + 0.05, nk[1] + 0.17], [nk[0] + 0.085, nk[1] + 0.1], [nk[0] + 0.07, nk[1] + 0.02], [nk[0] + 0.04, nk[1] - 0.02]]); g.fillStyle = rgba(col); g.fill(hp); }
  else { g.fillStyle = rgba(o.skinCol || PAL.skin); g.beginPath(); g.ellipse(nk[0] + 0.01, nk[1] + 0.085, hr, hr * 1.12, 0, 0, 7); g.fill(); }
  if (o.crown) { g.fillStyle = rgba(PAL.gold); g.fillRect(nk[0] - 0.05, nk[1] + 0.14, 0.11, 0.028); for (let k = 0; k < 3; k++) { g.beginPath(); g.moveTo(nk[0] - 0.05 + k * 0.045, nk[1] + 0.168); g.lineTo(nk[0] - 0.03 + k * 0.045, nk[1] + 0.2); g.lineTo(nk[0] - 0.015 + k * 0.045, nk[1] + 0.168); g.fill(); } }
  g.restore();
  A.head = [nk[0], nk[1] + 0.09];
  // near arm: reaches for the shoulder ahead, or carries the lantern
  const shN = lc([0.035, 0.79]); let hand;
  if (o.reach) { hand = [o.reach[0] / (face === 0 ? 1 : 1), o.reach[1]]; } else hand = [0.16 + 0.025 * walk * Math.sin(2 * Math.PI * ph + 0.8), 0.56 + (o.lantern ? 0.02 : 0)];
  if (o.lantern) hand = [0.19 + 0.02 * walk * Math.sin(2 * Math.PI * ph), 0.6];
  const elN = ik(shN, hand, 0.17, 0.165, -1); g.strokeStyle = rgba(col); g.lineWidth = lw(0.062); g.beginPath(); g.moveTo(shN[0], shN[1]); g.lineTo(elN[0], elN[1]); g.lineTo(hand[0], hand[1]); g.stroke();
  g.fillStyle = rgba(mixc(dark, col, 0.3)); g.beginPath(); g.arc(hand[0], hand[1], 0.03, 0, 7); g.fill();
  A.shoulder = [shN[0], shN[1]];
  let lant = null;
  if (o.lantern) { const sw = 0.12 * Math.sin(2 * Math.PI * ph * 1 + 0.4) * walk * 0.6 + (o.lanternSway || 0); const px = hand[0] + Math.sin(sw) * 0.09, py = hand[1] - Math.cos(sw) * 0.09; g.strokeStyle = rgba(PAL.frame); g.lineWidth = lw(0.008);
    g.beginPath(); g.moveTo(hand[0], hand[1] - 0.01); g.lineTo(px, py + 0.02); g.stroke(); const on = o.lantern.on ?? 1; g.save(); g.translate(px, py - 0.025); g.rotate(-sw * 0.8);
    g.fillStyle = rgba(mixc(PAL.paperOff, PAL.paperLit, on)); g.beginPath(); g.ellipse(0, 0, 0.034, 0.047, 0, 0, 7); g.fill(); g.fillStyle = rgba(PAL.frame); g.fillRect(-0.03, 0.04, 0.06, 0.01); g.fillRect(-0.03, -0.05, 0.06, 0.01); g.restore(); lant = [px, py - 0.025]; }
  g.restore();
  const T = (p) => [o.x + face * p[0] * h, o.y - p[1] * h];
  return { shoulder: T(A.shoulder), head: T(A.head), lantern: lant ? T(lant) : null, hand: T(hand) };
}

// ------------------------------------------------------------------ horse (side view, facing +x; withers height = 1 unit)
export function horse(g, o) {
  const h = o.h, face = o.face || 1, ph = o.ph || 0, gallop = o.gallop ?? 1; g.save(); g.translate(o.x, o.y); g.scale(face * h, -h); g.lineCap = 'round'; g.lineJoin = 'round';
  const col = o.col || hex('#141320'), col2 = mixc(col, hex('#3a3550'), 0.35); const bob = 0.05 * gallop * Math.sin(2 * Math.PI * ph * 2 + 0.5); const pitch = 0.06 * gallop * Math.sin(2 * Math.PI * ph * 2 - 0.4);
  const body = [0.0, 0.62 + bob];
  const legs = [[0.42, 0.0], [0.34, 0.12], [-0.38, 0.0], [-0.3, 0.1]]; // fore far, fore near, hind far, hind near (shoulder/hip x offset, phase offset)
  const lg = (sx, off, near, hind) => { const p = ph + off * 0.5 + (hind ? 0.5 : 0); const a = Math.sin(2 * Math.PI * p) * (gallop ? 0.95 : 0.35) * (gallop ? 1 : 0.8); const k = Math.cos(2 * Math.PI * p);
    const top = [body[0] + sx, body[1] - 0.08]; const knee = [top[0] + 0.22 * Math.sin(a) * 0.55 + (hind ? -0.04 : 0.04), top[1] - 0.26 + Math.max(0, k) * 0.07];
    const foot = [knee[0] + (hind ? -1 : 1) * 0.04 + 0.2 * Math.sin(a - 0.5 * k) * 0.5, Math.max(0.03, knee[1] - 0.28 + Math.max(0, -Math.cos(2 * Math.PI * p + 1)) * 0.1 * gallop)];
    if (!gallop) { foot[1] = Math.max(0.02, foot[1] - 0.02); }
    g.strokeStyle = rgba(near ? col : mixc(col, hex('#222034'), 0.5)); g.lineWidth = hind ? 0.075 : 0.062; g.beginPath(); g.moveTo(top[0], top[1]); g.lineTo(knee[0], knee[1]); g.lineWidth = 0.05; g.lineTo(foot[0], foot[1]); g.stroke();
    g.beginPath(); g.ellipse(foot[0] + 0.03, foot[1], 0.042, 0.022, 0, 0, 7); g.fillStyle = rgba(col); g.fill(); };
  lg(legs[0][0], 0.0, false, false); lg(legs[2][0], 0.0, false, true);
  g.save(); g.translate(body[0], body[1]); g.rotate(pitch);
  const bp = smoothPath([[-0.5, 0.1], [-0.52, -0.1], [-0.3, -0.22], [0.1, -0.2], [0.42, -0.16], [0.56, 0.06], [0.52, 0.2], [0.2, 0.17], [-0.2, 0.2]]); g.fillStyle = rgba(col); g.fill(bp);
  // neck + head
  const np = smoothPath([[0.38, 0.1], [0.62, 0.2], [0.76, 0.46], [0.84, 0.5], [0.95, 0.4], [1.0, 0.32], [0.92, 0.35], [0.82, 0.38], [0.74, 0.28], [0.58, 0.06]]); g.fill(np);
  g.beginPath(); g.moveTo(0.78, 0.5); g.lineTo(0.8, 0.58); g.lineTo(0.83, 0.5); g.fill();
  // mane + tail
  g.strokeStyle = rgba(col2, 0.9); g.lineWidth = 0.035; g.beginPath(); g.moveTo(0.5, 0.2); g.quadraticCurveTo(0.58, 0.42 + 0.03 * Math.sin(ph * 12), 0.72, 0.52); g.stroke();
  g.lineWidth = 0.05; g.strokeStyle = rgba(col); g.beginPath(); g.moveTo(-0.5, 0.1); g.quadraticCurveTo(-0.68, 0.05 + 0.05 * Math.sin(ph * 12), -0.82, -0.1 + 0.08 * Math.sin(ph * 12 + 1)); g.stroke();
  g.restore();
  lg(legs[1][0], 0.12, true, false); lg(legs[3][0], 0.12, true, true);
  g.restore();
  const T = (p) => [o.x + face * p[0] * h, o.y - p[1] * h]; return { saddle: T([0.05, 0.78 + bob]), head: T([0.9, 1.0]) };
}

// ------------------------------------------------------------------ banners and torches
// cloth that waves: pole at (x,y) rising h px, flag w px wide hanging from the top; wind blows toward +x (dir=1) or -x
export function banner(g, o) {
  const { x, y, h, w, t = 0, dir = 1, col = PAL.purple, colLit = PAL.purpleLit, trim = PAL.gold, emblem = 'cross', amp = 0.12, seed = 0, flagH = 0.6 } = o; const fh = w * flagH;
  g.save(); g.strokeStyle = rgba(PAL.staff); g.lineWidth = Math.max(1.6, h * 0.012); g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y); g.lineTo(x, y - h); g.stroke();
  g.fillStyle = rgba(trim); g.beginPath(); g.arc(x, y - h - 1.5, Math.max(1.4, h * 0.012), 0, 7); g.fill();
  const N = 10; const top = y - h * 0.97; const P = []; const Q = [];
  for (let i = 0; i <= N; i++) { const u = i / N; const wv = Math.sin(u * 5.2 - t * 5.5 + seed) * amp * w * u + Math.sin(u * 9.1 - t * 8.3 + seed * 2) * amp * 0.3 * w * u; P.push([x + dir * u * w * (1 - 0.05 * Math.abs(wv) / (w * amp + 0.001)), top + wv]); Q.push([P[i][0], P[i][1] + fh * (1 - 0.12 * u)]); }
  const path = new Path2D(); path.moveTo(P[0][0], P[0][1]); for (let i = 1; i <= N; i++) path.lineTo(P[i][0], P[i][1]); for (let i = N; i >= 0; i--) path.lineTo(Q[i][0], Q[i][1]); path.closePath();
  g.fillStyle = rgba(col); g.fill(path);
  g.save(); g.clip(path); // folds: lit and shadow bands follow the wave
  for (let i = 0; i < N; i++) { const s = Math.cos(i / N * 5.2 - t * 5.5 + seed); g.fillStyle = s > 0 ? rgba(colLit, 0.45 * s) : rgba([0, 0, 0], -0.3 * s); g.beginPath(); g.moveTo(P[i][0], P[i][1]); g.lineTo(P[i + 1][0], P[i + 1][1]); g.lineTo(Q[i + 1][0], Q[i + 1][1]); g.lineTo(Q[i][0], Q[i][1]); g.closePath(); g.fill(); }
  // trim
  g.strokeStyle = rgba(trim, 0.9); g.lineWidth = Math.max(1, w * 0.04); g.beginPath(); for (let i = 0; i <= N; i++) { const y1 = lerp(P[i][1], Q[i][1], 0.93); i ? g.lineTo(P[i][0], y1) : g.moveTo(P[i][0], y1); } g.stroke();
  const mid = (u, v) => { const i = Math.min(N - 1, Math.floor(u * N)), f = u * N - i; const a = [lerp(P[i][0], P[i + 1][0], f), lerp(P[i][1], P[i + 1][1], f)], b = [lerp(Q[i][0], Q[i + 1][0], f), lerp(Q[i][1], Q[i + 1][1], f)]; return [lerp(a[0], b[0], v), lerp(a[1], b[1], v)]; };
  if (emblem === 'cross') { const c = mid(0.5, 0.5); const s = Math.min(w, fh) * 0.2; g.fillStyle = rgba(trim); g.fillRect(c[0] - s * 0.14, c[1] - s, s * 0.28, s * 2); g.fillRect(c[0] - s * 0.7, c[1] - s * 0.45, s * 1.4, s * 0.26); }
  else if (emblem === 'disc') { const c = mid(0.5, 0.5); g.fillStyle = rgba(trim, 0.9); g.beginPath(); g.arc(c[0], c[1], Math.min(w, fh) * 0.2, 0, 7); g.fill(); g.fillStyle = rgba(col); g.beginPath(); g.arc(c[0] + Math.min(w, fh) * 0.06, c[1], Math.min(w, fh) * 0.15, 0, 7); g.fill(); }
  g.restore(); g.restore();
  return { tip: [x, y - h] };
}
// a warm glow (additive) at design px; r in px
export function glowAt(gg, x, y, r, a = 1, col = [255, 160, 80]) {
  const g = gg.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${a})`); g.addColorStop(0.18, `rgba(${col[0]},${col[1]},${col[2]},${a * 0.45})`); g.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
  gg.fillStyle = g; gg.fillRect(x - r, y - r, r * 2, r * 2);
}
// torch: stick + flame teardrop (detail layer) with flicker; returns flame centre. Glow is drawn separately on the glow canvas.
export function torch(g, x, y, s, t, seed = 0, lit = 1) {
  g.save(); g.translate(x, y); g.strokeStyle = rgba(PAL.staff); g.lineWidth = Math.max(0.9, s * 0.09); g.lineCap = 'round'; g.beginPath(); g.moveTo(0, s * 1.2); g.lineTo(0, 0); g.stroke();
  const fl = 1 + 0.18 * noise1(t * 9 + seed * 2.3, seed) + 0.1 * noise1(t * 23 + seed, seed + 3); const sw = 0.25 * noise1(t * 6 + seed, seed + 1);
  if (lit > 0.01) { g.fillStyle = rgba([255, 200, 110], 0.95 * lit); g.beginPath(); g.moveTo(-s * 0.17, 0); g.quadraticCurveTo(-s * 0.2 + sw * s * 0.3, -s * 0.5 * fl, sw * s * 0.6, -s * 0.95 * fl); g.quadraticCurveTo(s * 0.22 + sw * s * 0.3, -s * 0.45 * fl, s * 0.17, 0); g.closePath(); g.fill();
    g.fillStyle = rgba([255, 245, 200], 0.9 * lit); g.beginPath(); g.ellipse(0, -s * 0.18, s * 0.08, s * 0.2 * fl, 0, 0, 7); g.fill(); }
  g.restore(); return [x + 0, y - s * 0.4];
}
// drifting embers / dust motes: deterministic; field = {x0,y0,x1,y1}; returns nothing (draws additive dots on the glow context if given)
export function embers(g, t, f, n, { speed = 30, size = 1.6, col = [255, 160, 70], a = 0.8, rise = 1, wind = 10, seed = 1 } = {}) {
  for (let i = 0; i < n; i++) { const r1 = hash1(i * 3.1 + seed), r2 = hash1(i * 7.7 + seed), r3 = hash1(i * 1.9 + seed), life = 2 + 3 * r3; const u = ((t / life + r1) % 1);
    const x = f.x0 + (f.x1 - f.x0) * r2 + Math.sin(t * 1.3 + i) * 8 + wind * u * life * 0.6, y = f.y1 - (f.y1 - f.y0) * u * rise + 0; const al = a * Math.sin(Math.PI * u) * (0.5 + 0.5 * hash1(i + Math.floor(t * 6)));
    g.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${al})`; g.beginPath(); g.arc(x, y, size * (0.5 + r3), 0, 7); g.fill(); }
}
