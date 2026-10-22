// Figures for the detail layer: walkers (planted-foot gait), hooded leaders with lanterns, riders and horses, banners, torches, sparks.
// All drawn in design px (720x1280) on a Canvas2D context; shapes are built in "h units" (figure height = 1) under a local transform.
import { clamp, lerp, smoothstep, ease, noise1 } from '/harness/kit/film.js';
import { rgba, mixc, mul, hex } from './paint.js';

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
//   crown:true, cape:colour, helm:true (+ plume colour), shield:colour, spear:true, seat:true (rider: near leg bent over the saddle), shadow:false, seed }
// returns anchors in px: { shoulder, hand, lantern, head }
// The gait is planted-foot: the stance foot slides back at exactly the body speed (ph = distance / (STRIDE * stride * h)), the swing foot arcs forward,
// the hips bob twice per cycle, the torso counter-rotates (shoulders dip, robe hem trails), the head stays level, arms swing against the legs.
export const STRIDE = 0.6;   // body travel per foot cycle, in figure heights
export function person(g, o) {
  const h = o.h, face = o.face || 1, ph = o.ph || 0, walk = o.walk ?? 1; const L = STRIDE * (o.stride ?? 1);
  if (o.view === 'back' || o.view === 'front') return personFB(g, o);
  const A = {}; const M0 = g.getTransform(); g.save(); g.translate(o.x, o.y); g.scale(face * h, -h);
  const lw = (w) => Math.max(w, 1.1 / h);
  const w2 = 2 * Math.PI * ph;
  if (o.shadow !== false && h > 12) { g.fillStyle = 'rgba(5,4,12,0.4)'; g.beginPath(); g.ellipse(0.03, 0.004, 0.22 + 0.04 * walk, 0.028, 0, 0, 7); g.fill(); }
  const f0 = footAt(ph, 0, L * walk), f1 = footAt(ph, 1, L * walk);
  const bob = 0.014 * walk * Math.cos(4 * Math.PI * ph + 0.6) + (walk < 0.2 ? 0.003 * Math.sin((o.t ?? 0) * 1.6) : 0); const hip = [0.0, 0.5 + bob];
  const lean = 0.05 * walk; const lc = (p) => { const c = Math.cos(-lean), s = Math.sin(-lean); const dx = p[0] - hip[0], dy = p[1] - hip[1]; return [hip[0] + dx * c - dy * s, hip[1] + dx * s + dy * c]; };
  const col = o.col || PAL.cloak, col2 = o.col2 || PAL.cloak2, dark = o.dark || PAL.dark;
  g.lineCap = 'round'; g.lineJoin = 'round';
  const leg = (f, c, w) => { const ank = [f[0] + 0.02, f[1] + 0.05]; const kn = ik(hip, ank, 0.26, 0.26, 1); g.strokeStyle = rgba(c); g.lineWidth = lw(w); g.beginPath(); g.moveTo(hip[0], hip[1]); g.lineTo(kn[0], kn[1]); g.lineTo(ank[0], ank[1]); g.stroke();
    // boot: heel to toe, the toe drops while the leg swings through
    const sw = clamp(f[1] / 0.05); g.save(); g.translate(ank[0], ank[1] - 0.018); g.rotate(-0.28 * sw * (f[0] > 0 ? 0.4 : 1.2) + (f[1] < 0.004 ? 0.04 : 0)); g.fillStyle = rgba(mixc(c, dark, 0.35)); g.beginPath(); g.moveTo(-0.035, 0.03); g.lineTo(-0.03, -0.02); g.quadraticCurveTo(0.02, -0.03, 0.085, -0.032); g.quadraticCurveTo(0.1, -0.028, 0.1, -0.05); g.lineTo(0.1, -0.052); g.lineTo(-0.035, -0.052); g.closePath(); g.fill(); g.restore(); };
  if (!o.noLegs) leg(f1, mixc(dark, col, 0.4), 0.062);
  // spear (carried upright in the far hand)
  const shF = lc([0.0, 0.795]);
  if (o.spear) { const px = 0.12 + 0.01 * Math.sin(w2), top = 1.78; g.strokeStyle = rgba(PAL.staff); g.lineWidth = lw(0.022); g.beginPath(); g.moveTo(px - 0.012, 0.32); g.lineTo(px, top); g.stroke(); g.fillStyle = rgba([150, 156, 190], 0.95); g.beginPath(); g.moveTo(px - 0.018, top - 0.01); g.lineTo(px, top + 0.11); g.lineTo(px + 0.018, top - 0.01); g.closePath(); g.fill(); }
  // staff (far hand), planted with the far foot
  if (o.staff) { const tipx = f1[0] + 0.2; g.strokeStyle = rgba(PAL.staff); g.lineWidth = lw(0.026); g.beginPath(); g.moveTo(tipx - 0.02 * walk, 0.0); g.lineTo(0.13, 0.8); g.stroke(); }
  // far arm (swings against the near leg, hangs, or grips the staff / spear)
  { const hd = o.staff ? [0.13, 0.62] : o.spear ? [0.121, 0.64] : [0.01 - 0.085 * walk * Math.sin(w2 + 0.3), 0.5 + 0.012 * Math.cos(w2)]; const el = ik(shF, hd, 0.17, 0.16, -1); g.strokeStyle = rgba(mixc(dark, col, 0.5)); g.lineWidth = lw(0.05); g.beginPath(); g.moveTo(shF[0], shF[1]); g.lineTo(el[0], el[1]); g.lineTo(hd[0], hd[1]); g.stroke(); }
  if (!o.noLegs) leg(f0, dark, 0.07);
  if (o.seat) { const kn = [0.2, 0.37], an = [0.14, 0.15]; g.strokeStyle = rgba(mixc(dark, col, 0.2)); g.lineWidth = lw(0.075); g.beginPath(); g.moveTo(hip[0] + 0.01, hip[1] - 0.01); g.lineTo(kn[0], kn[1]); g.lineTo(an[0], an[1]); g.stroke(); g.fillStyle = rgba(dark); g.beginPath(); g.ellipse(an[0] + 0.035, an[1] - 0.02, 0.05, 0.026, -0.2, 0, 7); g.fill(); }
  // robe / cloak: shoulders, a cinch at the waist, a skirt that swings with the stride and trails behind the walker
  const hem = o.hem ?? 0.2, sway = 0.022 * Math.sin(w2) * walk, tr = -0.04 * walk;
  const body = [lc([0.045, 0.83]), lc([0.088, 0.69]), lc([0.09, 0.56]), lc([0.1, 0.44]), lc([0.118 + (f0[0] > f1[0] ? f0[0] : f1[0]) * 0.2, hem + 0.015]), lc([0.05, hem - 0.015 + sway * 0.4]), lc([-0.05, hem - 0.005]),
    lc([-0.13 + tr, hem + 0.02 + sway]), lc([-0.112 + tr * 0.5, 0.4]), lc([-0.085, 0.56]), lc([-0.088, 0.68]), lc([-0.06, 0.82])];
  const bp = smoothPath(body); g.fillStyle = rgba(col); g.fill(bp);
  if (h > 60) { g.save(); g.clip(bp); const gr = g.createLinearGradient(-0.15, 0.85, 0.15, 0.2); gr.addColorStop(0, rgba(col2, 0.6)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.fillRect(-0.3, 0, 0.6, 1);
    g.fillStyle = rgba(dark, 0.55); g.fillRect(-0.2, lc([0, 0.56])[1] - 0.012, 0.4, 0.024); // belt
    if (h > 90) { g.lineWidth = 0.011; for (let k = 0; k < 3; k++) { const x0 = -0.04 + k * 0.05; g.strokeStyle = rgba(dark, 0.5); g.beginPath(); g.moveTo(x0, 0.54); g.quadraticCurveTo(x0 - 0.012 + tr, 0.4, x0 - 0.03 + tr * 1.5 + 0.01 * k, hem + 0.02); g.stroke(); g.strokeStyle = rgba(col2, 0.5); g.beginPath(); g.moveTo(x0 + 0.014, 0.54); g.quadraticCurveTo(x0 + 0.002 + tr, 0.4, x0 - 0.016 + tr * 1.5 + 0.01 * k, hem + 0.02); g.stroke(); } }
    g.restore(); }
  if (o.cape) { const cp = smoothPath([lc([-0.04, 0.84]), lc([-0.17 + tr, 0.7]), lc([-0.22 + tr * 2 - 0.02 * Math.sin(w2 - 0.8) * walk, 0.3]), lc([-0.16 + tr * 2, hem - 0.03]), lc([-0.05, 0.4]), lc([0.02, 0.7])]); g.fillStyle = rgba(o.cape); g.fill(cp); }
  // head + hood / helm (the head stays level: it cancels the bob)
  const nk = lc([0.012, 0.86]); const hr = 0.064; const tilt = (o.head ?? -0.1 * walk) - lean * 0.3; const hc = [nk[0] + 0.012, nk[1] + 0.075];
  g.save(); g.translate(nk[0], nk[1]); g.rotate(-tilt); g.translate(-nk[0], -nk[1]);
  let hoodPath = null;
  if (o.hood !== false) { const hp = hoodPath = smoothPath([[nk[0] - 0.06, nk[1] - 0.012], [nk[0] - 0.085, nk[1] + 0.05], [nk[0] - 0.13 + tr * 0.8, nk[1] + 0.13], [nk[0] - 0.115 + tr, nk[1] + 0.17], [nk[0] - 0.02, nk[1] + 0.185], [nk[0] + 0.05, nk[1] + 0.15], [nk[0] + 0.08, nk[1] + 0.085], [nk[0] + 0.065, nk[1] + 0.02], [nk[0] + 0.035, nk[1] - 0.02]]); g.fillStyle = rgba(col); g.fill(hp);
    if (h > 120) { g.fillStyle = rgba(dark, 0.9); g.beginPath(); g.ellipse(nk[0] + 0.045, nk[1] + 0.085, 0.034, 0.05, 0.1, 0, 7); g.fill(); } }
  else { g.fillStyle = rgba(o.skinCol || PAL.skin); g.beginPath(); g.ellipse(nk[0] + 0.01, nk[1] + 0.085, hr, hr * 1.12, 0, 0, 7); g.fill(); }
  if (o.helm) { const hx = hc[0], hy = hc[1] + 0.025; g.fillStyle = rgba(o.helmCol || [58, 54, 78]); g.beginPath(); g.moveTo(hx - 0.075, hy - 0.02); g.quadraticCurveTo(hx - 0.08, hy + 0.1, hx + 0.005, hy + 0.17); g.quadraticCurveTo(hx + 0.07, hy + 0.1, hx + 0.078, hy - 0.02); g.closePath(); g.fill();
    g.fillStyle = rgba([170, 160, 190], 0.5); g.beginPath(); g.moveTo(hx - 0.07, hy - 0.01); g.quadraticCurveTo(hx - 0.07, hy + 0.09, hx - 0.01, hy + 0.15); g.lineTo(hx - 0.03, hy + 0.04); g.closePath(); g.fill();
    g.strokeStyle = rgba([40, 36, 54]); g.lineWidth = lw(0.012); g.beginPath(); g.moveTo(hx + 0.05, hy + 0.03); g.lineTo(hx + 0.06, hy - 0.04); g.stroke();
    if (o.plume) { g.strokeStyle = rgba(o.plume); g.lineWidth = lw(0.022); g.beginPath(); g.moveTo(hx + 0.005, hy + 0.17); g.quadraticCurveTo(hx - 0.04, hy + 0.23 + 0.01 * Math.sin(w2), hx - 0.1 - 0.03 * walk, hy + 0.2 - 0.02 * Math.cos(w2)); g.stroke(); } }
  if (o.crown) { g.fillStyle = rgba(PAL.gold); g.fillRect(nk[0] - 0.05, nk[1] + 0.14, 0.11, 0.028); for (let k = 0; k < 3; k++) { g.beginPath(); g.moveTo(nk[0] - 0.05 + k * 0.045, nk[1] + 0.168); g.lineTo(nk[0] - 0.03 + k * 0.045, nk[1] + 0.2); g.lineTo(nk[0] - 0.015 + k * 0.045, nk[1] + 0.168); g.fill(); } }
  g.restore();
  A.head = [nk[0], nk[1] + 0.09];
  // near arm: reaches for the shoulder ahead, carries the lantern, or swings
  const shN = lc([0.035, 0.79]); let hand;
  if (o.reach) hand = [o.reach[0], o.reach[1]]; else hand = [0.035 + 0.09 * walk * Math.sin(w2 + Math.PI + 0.3), 0.5 + 0.014 * Math.cos(w2 + 0.6) + (o.lantern ? 0.04 : 0)];
  if (o.lantern) hand = [0.19 + 0.02 * walk * Math.sin(w2), 0.6];
  const elN = ik(shN, hand, 0.17, 0.165, -1); g.strokeStyle = rgba(col); g.lineWidth = lw(0.062); g.beginPath(); g.moveTo(shN[0], shN[1]); g.lineTo(elN[0], elN[1]); g.lineTo(hand[0], hand[1]); g.stroke();
  g.fillStyle = rgba(mixc(dark, col, 0.3)); g.beginPath(); g.arc(hand[0], hand[1], 0.03, 0, 7); g.fill();
  if (o.shield) { g.fillStyle = rgba(o.shield); g.beginPath(); g.ellipse(0.08, 0.6, 0.075, 0.17, 0, 0, 7); g.fill(); g.strokeStyle = rgba(PAL.gold, 0.7); g.lineWidth = lw(0.012); g.stroke(); g.fillStyle = rgba([200, 180, 120], 0.8); g.beginPath(); g.arc(0.08, 0.6, 0.022, 0, 7); g.fill(); }
  A.shoulder = [shN[0], shN[1]];
  let lant = null;
  if (o.lantern) { const sw = 0.12 * Math.sin(w2 + 0.4) * walk * 0.6 + (o.lanternSway || 0); const px = hand[0] + Math.sin(sw) * 0.09, py = hand[1] - Math.cos(sw) * 0.09; g.strokeStyle = rgba(PAL.frame); g.lineWidth = lw(0.008);
    g.beginPath(); g.moveTo(hand[0], hand[1] - 0.01); g.lineTo(px, py + 0.02); g.stroke(); const on = o.lantern.on ?? 1; g.save(); g.translate(px, py - 0.025); g.rotate(-sw * 0.8);
    g.fillStyle = rgba(mixc(PAL.paperOff, PAL.paperLit, on)); g.beginPath(); g.ellipse(0, 0, 0.034, 0.047, 0, 0, 7); g.fill(); g.fillStyle = rgba(PAL.frame); g.fillRect(-0.03, 0.04, 0.06, 0.01); g.fillRect(-0.03, -0.05, 0.06, 0.01); g.restore(); lant = [px, py - 0.025]; }
  if (o.warm && h > 60) { const all = new Path2D(); all.addPath(bp); if (hoodPath) all.addPath(hoodPath); g.save(); g.clip(all); g.setTransform(M0); const w = o.warm; const rg = g.createRadialGradient(w.x, w.y, 0, w.x, w.y, w.r); rg.addColorStop(0, rgba([255, 175, 95], w.a)); rg.addColorStop(1, rgba([255, 150, 80], 0)); g.fillStyle = rg; g.fillRect(w.x - w.r, w.y - w.r, w.r * 2, w.r * 2); g.restore(); }
  g.restore();
  const T = (p) => [o.x + face * p[0] * h, o.y - p[1] * h];
  return { shoulder: T(A.shoulder), head: T(A.head), lantern: lant ? T(lant) : null, hand: T(hand) };
}


// the same people seen from behind or from the front (symmetric, for crowds walking away from or toward the camera): legs alternate, arms swing, the robe sways
function personFB(g, o) {
  const h = o.h, ph = o.ph || 0, walk = o.walk ?? 1, w2 = 2 * Math.PI * ph; const front = o.view === 'front'; const col = o.col || PAL.cloak, col2 = o.col2 || PAL.cloak2, dark = o.dark || PAL.dark;
  g.save(); g.translate(o.x, o.y); g.scale(h * (o.sx ?? 1), -h); g.lineCap = 'round'; g.lineJoin = 'round'; const lw = (w) => Math.max(w, 1.1 / h);
  if (o.shadow !== false && h > 12) { g.fillStyle = 'rgba(5,4,12,0.4)'; g.beginPath(); g.ellipse(0, 0.004, 0.2, 0.03, 0, 0, 7); g.fill(); }
  const sL = Math.sin(w2) * walk, sR = -sL; const bob = 0.012 * walk * Math.abs(Math.sin(w2)); const hem = o.hem ?? 0.2; const hipY = 0.5 + bob;
  for (const [sd, sw] of [[-1, sL], [1, sR]]) { const lift = Math.max(0, sw) * 0.06, ahead = sw * 0.05 * (front ? -1 : 1); g.strokeStyle = rgba(mixc(dark, col, 0.35)); g.lineWidth = lw(0.065); g.beginPath(); g.moveTo(sd * 0.045, hipY); g.lineTo(sd * 0.05, 0.25 + lift * 0.5); g.lineTo(sd * 0.052, lift + 0.03 + ahead * 0.3); g.stroke(); g.fillStyle = rgba(dark); g.beginPath(); g.ellipse(sd * 0.055, lift + 0.018, 0.04, 0.022, 0, 0, 7); g.fill(); }
  if (o.spear) { g.strokeStyle = rgba(PAL.staff); g.lineWidth = lw(0.022); g.beginPath(); g.moveTo(0.17, 0.22); g.lineTo(0.17, 1.78); g.stroke(); g.fillStyle = rgba([150, 156, 190], 0.95); g.beginPath(); g.moveTo(0.152, 1.77); g.lineTo(0.17, 1.89); g.lineTo(0.188, 1.77); g.closePath(); g.fill(); }
  // arms (behind the robe's edge): swing against the legs
  for (const [sd, sw] of [[-1, sR], [1, sL]]) { if (o.spear && sd === 1) continue; g.strokeStyle = rgba(mixc(dark, col, 0.55)); g.lineWidth = lw(0.055); g.beginPath(); g.moveTo(sd * 0.135, 0.79); g.lineTo(sd * 0.165, 0.62); g.lineTo(sd * 0.16, 0.5 + 0.03 * sw); g.stroke(); }
  const sway = 0.02 * Math.sin(w2) * walk;
  const bp = smoothPath([[-0.07, 0.86], [-0.14, 0.8], [-0.12, 0.6], [-0.15, 0.4], [-0.18 + sway, hem], [0, hem - 0.015], [0.18 + sway, hem], [0.15, 0.4], [0.12, 0.6], [0.14, 0.8], [0.07, 0.86]]); g.fillStyle = rgba(col); g.fill(bp);
  g.save(); g.clip(bp); const gr = g.createLinearGradient(-0.15, 0.85, 0.15, 0.2); gr.addColorStop(0, rgba(col2, 0.55)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.fillRect(-0.3, 0, 0.6, 1); g.fillStyle = rgba(dark, 0.55); g.fillRect(-0.16, 0.55, 0.32, 0.022);
  if (!front && !o.cape) { g.strokeStyle = rgba(dark, 0.4); g.lineWidth = lw(0.01); for (let k = -2; k <= 2; k++) { g.beginPath(); g.moveTo(k * 0.03, 0.78); g.lineTo(k * 0.05 + sway, hem + 0.02); g.stroke(); } }
  g.restore();
  if (o.cape) { g.fillStyle = rgba(o.cape); const cp = smoothPath([[-0.09, 0.86], [-0.2, 0.7], [-0.23 + sway, 0.3], [-0.19, hem - 0.03], [0.19, hem - 0.03], [0.23 + sway, 0.3], [0.2, 0.7], [0.09, 0.86]]); g.fill(cp); }
  // head
  const hy = 0.93 + bob; if (o.hood !== false && !o.helm) { g.fillStyle = rgba(col); g.beginPath(); g.moveTo(-0.095, 0.82); g.quadraticCurveTo(-0.115, 0.95, -0.03, 1.03); g.quadraticCurveTo(0.03, 1.06, 0.07, 1.0); g.quadraticCurveTo(0.12, 0.93, 0.095, 0.82); g.closePath(); g.fill(); if (front) { g.fillStyle = rgba(dark, 0.9); g.beginPath(); g.ellipse(0, 0.92, 0.04, 0.052, 0, 0, 7); g.fill(); } }
  else { g.fillStyle = rgba(o.skinCol || PAL.skin); g.beginPath(); g.ellipse(0, hy, 0.062, 0.07, 0, 0, 7); g.fill(); }
  if (o.helm) { g.fillStyle = rgba(o.helmCol || [58, 54, 78]); g.beginPath(); g.moveTo(-0.075, hy - 0.02); g.quadraticCurveTo(-0.08, hy + 0.09, 0, hy + 0.17); g.quadraticCurveTo(0.08, hy + 0.09, 0.075, hy - 0.02); g.closePath(); g.fill(); g.fillStyle = rgba([170, 160, 190], 0.4); g.beginPath(); g.moveTo(-0.07, hy - 0.01); g.quadraticCurveTo(-0.07, hy + 0.09, -0.005, hy + 0.15); g.lineTo(-0.03, hy + 0.03); g.closePath(); g.fill(); if (o.plume) { g.strokeStyle = rgba(o.plume); g.lineWidth = lw(0.026); g.beginPath(); g.moveTo(0, hy + 0.17); g.quadraticCurveTo(0.02, hy + 0.24, -0.02 + 0.02 * Math.sin(w2), hy + 0.27); g.stroke(); } }
  if (o.crown) { g.fillStyle = rgba(PAL.gold); g.fillRect(-0.055, hy + 0.05, 0.11, 0.028); for (let k = 0; k < 3; k++) { g.beginPath(); g.moveTo(-0.055 + k * 0.045, hy + 0.078); g.lineTo(-0.035 + k * 0.045, hy + 0.11); g.lineTo(-0.02 + k * 0.045, hy + 0.078); g.fill(); } }
  if (o.shield) { g.fillStyle = rgba(o.shield); g.beginPath(); g.ellipse(-0.17, 0.6, 0.1, 0.17, 0, 0, 7); g.fill(); g.strokeStyle = rgba(PAL.gold, 0.7); g.lineWidth = lw(0.012); g.stroke(); g.fillStyle = rgba([200, 180, 120], 0.8); g.beginPath(); g.arc(-0.17, 0.6, 0.024, 0, 7); g.fill(); }
  let lant = null; if (o.lantern) { const lx = 0.2, ly = 0.58; g.strokeStyle = rgba(PAL.frame); g.lineWidth = lw(0.008); g.beginPath(); g.moveTo(lx, 0.62); g.lineTo(lx, ly + 0.05); g.stroke(); const on = o.lantern.on ?? 1; g.fillStyle = rgba(mixc(PAL.paperOff, PAL.paperLit, on)); g.beginPath(); g.ellipse(lx, ly, 0.034, 0.047, 0, 0, 7); g.fill(); lant = [lx, ly]; }
  if (o.torch) { g.strokeStyle = rgba(PAL.staff); g.lineWidth = lw(0.022); g.beginPath(); g.moveTo(0.19, 0.5); g.lineTo(0.2, 0.98); g.stroke(); lant = [0.2, 1.0]; }
  g.restore(); const T = (p) => [o.x + p[0] * h * (o.sx ?? 1), o.y - p[1] * h];
  return { shoulder: T([0.13, 0.79]), head: T([0, hy + 0.07]), lantern: lant ? T(lant) : null, hand: T([0.16, 0.52]) };
}

// ------------------------------------------------------------------ horse (side view, facing +x; withers height = 1 unit)
// A real quadruped: barrel, rounded chest and croup, arched neck, wedge head with ear, mane and tail that follow the wind of its own motion, and
// four legs of three bones each with planted-foot gaits. o: { x, y (ground under the body), h (withers height px), face, ph (gait cycle 0..1, drive it from
// distance / (cycle * h) so no hoof skates), gallop (0 walk .. 1 gallop), stand (true: standing, breathing), col, t, headDip }
export function horse(g, o) {
  const h = o.h, face = o.face || 1, ph = o.ph || 0, gal = clamp(o.gallop ?? 1), stand = !!o.stand; const tt = o.t ?? ph * 3;
  g.save(); g.translate(o.x, o.y); g.scale(face * h, -h); g.lineCap = 'round'; g.lineJoin = 'round';
  const col = o.col || hex('#141320'), col2 = mixc(col, hex('#3a3550'), 0.4), far = mixc(col, hex('#24203a'), 0.45);
  const duty = lerp(0.68, 0.36, gal), cyc = lerp(1.45, 2.25, gal), E = cyc * duty;
  const w2 = 2 * Math.PI * ph;
  const bob = stand ? 0.004 * Math.sin(tt * 1.5) : lerp(0.012, 0.036, gal) * Math.sin(2 * w2 + 0.7);
  const pitch = stand ? 0.0 : lerp(0.012, 0.075, gal) * Math.sin(w2 - 0.5);
  const body = [0.0, 0.66 + bob]; const rot = (p) => { const c = Math.cos(pitch), s = Math.sin(pitch); return [body[0] + p[0] * c - p[1] * s, body[1] + p[0] * s + p[1] * c]; };
  // legs: shoulder / hip attach points (body frame) and their gait phase offsets (walk: hind, fore, hind, fore around; gallop: the two pairs nearly together)
  const offs = gal < 0.5 ? { hf: 0.0, ff: 0.5, hn: 0.5 - 0.25, fn: 0.25 } : { hf: 0.0, ff: 0.5, hn: 0.12, fn: 0.62 };
  const legs = [{ ax: 0.33, ay: -0.1, off: offs.ff, hind: false, near: false }, { ax: -0.4, ay: -0.04, off: offs.hf, hind: true, near: false }, { ax: 0.31, ay: -0.1, off: offs.fn, hind: false, near: true }, { ax: -0.38, ay: -0.04, off: offs.hn, hind: true, near: true }];
  const drawLeg = (L) => {
    const a = rot([L.ax, L.ay]); const p = (((ph + L.off) % 1) + 1) % 1; let fx, fy;
    if (stand) { fx = a[0] + (L.hind ? -0.03 : 0.03) + (L.near ? 0.03 : -0.02); fy = 0; }
    else if (p < duty) { const u = p / duty; fx = a[0] + E * (0.5 - u) * 0.9 + (L.hind ? -0.02 : 0.05); fy = 0; }
    else { const u = (p - duty) / (1 - duty); fx = a[0] + (L.hind ? -0.02 : 0.05) + E * 0.9 * (-0.5 + ease.inOutSine(u)); fy = lerp(0.11, 0.2, gal) * Math.sin(Math.PI * Math.pow(u, 0.8)); }
    const fet = [fx - (L.hind ? 0.01 : 0), fy + 0.075]; const ul = L.hind ? 0.31 : 0.3, ll = L.hind ? 0.3 : 0.31;
    const kn = ik(a, fet, ul, ll, L.hind ? -1 : 1); const c = L.near ? col : far;
    g.strokeStyle = rgba(c); g.lineWidth = L.hind ? 0.15 : 0.12; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(kn[0], kn[1]); g.stroke();   // thigh / forearm
    g.lineWidth = L.hind ? 0.07 : 0.064; g.beginPath(); g.moveTo(kn[0], kn[1]); g.lineTo(fet[0], fet[1]); g.stroke();                       // cannon
    g.lineWidth = 0.056; g.beginPath(); g.moveTo(fet[0], fet[1]); g.lineTo(fet[0] + 0.028, fy + 0.02); g.stroke();                              // pastern
    g.fillStyle = rgba(mul(c, 0.8)); g.beginPath(); g.moveTo(fet[0] + 0.012, fy + 0.04); g.lineTo(fet[0] + 0.07, fy + 0.0); g.lineTo(fet[0] - 0.005, fy + 0.0); g.closePath(); g.fill();   // hoof
    if (fy < 0.004 && !stand) { g.fillStyle = 'rgba(4,3,10,0.28)'; g.beginPath(); g.ellipse(fet[0] + 0.03, 0.0, 0.07, 0.014, 0, 0, 7); g.fill(); }
  };
  if (o.shadow !== false) { g.fillStyle = 'rgba(4,3,10,0.36)'; g.beginPath(); g.ellipse(0.0, 0.004, 0.62, 0.05, 0, 0, 7); g.fill(); }
  drawLeg(legs[0]); drawLeg(legs[1]);
  // tail (behind the body), swinging with the stride and streaming back with speed
  { const tb = rot([-0.52, 0.12]); const stream = 0.14 + 0.2 * gal; const sw = 0.05 * Math.sin(w2 * 1.0 + 1.0) + 0.03 * Math.sin(tt * 2.1);
    g.strokeStyle = rgba(col); g.lineWidth = 0.055; g.beginPath(); g.moveTo(tb[0], tb[1]); g.bezierCurveTo(tb[0] - 0.12, tb[1] + 0.04 - 0.03 * gal, tb[0] - stream - 0.06, tb[1] - 0.1 + sw, tb[0] - stream - 0.14, tb[1] - 0.36 + 0.1 * gal + sw); g.stroke();
    g.strokeStyle = rgba(col2, 0.7); g.lineWidth = 0.02; g.beginPath(); g.moveTo(tb[0], tb[1] + 0.01); g.bezierCurveTo(tb[0] - 0.12, tb[1] + 0.05 - 0.03 * gal, tb[0] - stream - 0.04, tb[1] - 0.08 + sw, tb[0] - stream - 0.1, tb[1] - 0.33 + 0.1 * gal + sw); g.stroke(); }
  g.save(); g.translate(body[0], body[1]); g.rotate(pitch);
  // barrel with chest, croup and hind quarter
  const bp = smoothPath([[-0.5, 0.2], [-0.6, 0.06], [-0.58, -0.1], [-0.44, -0.24], [-0.15, -0.26], [0.2, -0.27], [0.42, -0.2], [0.52, -0.04], [0.48, 0.14], [0.34, 0.25], [0.1, 0.22], [-0.2, 0.22]]); g.fillStyle = rgba(col); g.fill(bp);
  g.save(); g.clip(bp); const lg = g.createLinearGradient(0, 0.25, 0, -0.26); lg.addColorStop(0, rgba(col2, 0.55)); lg.addColorStop(0.5, rgba(col, 0)); lg.addColorStop(1, rgba([0, 0, 0], 0.25)); g.fillStyle = lg; g.fillRect(-0.7, -0.3, 1.4, 0.6); g.restore();
  // neck and head (a head that nods with the stride)
  const nod = (stand ? 0.012 * Math.sin(tt * 0.9) : 0.03 * Math.sin(w2 * 1.0 - 1.2) * (1 - 0.5 * gal)) + (o.headDip ?? 0); const hdx = Math.sin(nod) * 0.2;
  const np = smoothPath([[0.22, 0.18], [0.38, 0.34], [0.5, 0.52], [0.56, 0.66], [0.64, 0.66 + nod], [0.72 + hdx, 0.61 + nod], [0.83 + hdx, 0.44 + nod], [0.91 + hdx, 0.33 + nod], [0.9 + hdx, 0.25 + nod], [0.82 + hdx, 0.27 + nod], [0.73, 0.37], [0.67, 0.33], [0.66, 0.16], [0.5, -0.02], [0.4, -0.16]]); g.fillStyle = rgba(col); g.fill(np);
  g.beginPath(); g.moveTo(0.57, 0.66 + nod); g.lineTo(0.55, 0.8 + nod); g.lineTo(0.62, 0.68 + nod); g.closePath(); g.fill();                  // ear
  g.fillStyle = rgba([6, 5, 12], 0.9); g.beginPath(); g.ellipse(0.74 + hdx, 0.5 + nod, 0.014, 0.01, -0.5, 0, 7); g.fill();                              // eye
  // mane along the crest, lifting in the wind of the motion
  g.strokeStyle = rgba(col2, 0.95); g.lineWidth = 0.03; for (let k = 0; k < 6; k++) { const u = k / 5; const bx = lerp(0.26, 0.58, u), by = lerp(0.24, 0.68, u) + (u > 0.8 ? nod : 0); const wv = 0.03 * Math.sin(tt * 4 + k * 1.3 + w2) * (0.5 + gal) + gal * 0.07;
    g.beginPath(); g.moveTo(bx, by); g.quadraticCurveTo(bx - 0.04 - wv * 0.5, by + 0.05, bx - 0.09 - wv, by + 0.03 - wv * 0.4); g.stroke(); }
  g.restore();
  drawLeg(legs[2]); drawLeg(legs[3]);
  g.restore();
  const T = (p) => [o.x + face * p[0] * h, o.y - p[1] * h]; return { saddle: T([0.08, 0.66 + bob + 0.16]), head: T([0.9, 1.0]) };
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
