// SET field: a cold night field after a battle (shields, spears, the fallen in mist, a moon) and the flight of Samuel across it:
// pursuers with torches, a son who puts his father on a horse, the gallop away. No gore: the fallen are dark shapes in the mist.
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, fireFlick, tintAll } from './common.js';
import { paintSky, paintRange, paintFog, paintRocks, paintTufts } from '../paint.js';
import { person, horse, banner, glowAt, torch, embers, hash1, PAL } from '../figs.js';
import { birds, smoke, motes, hazeBand, paintGrassStrip } from '../ambient.js';

const STRIDE = 0.6;
const gh = (y) => 0.36 * (y - 560) + 20;           // person height (plane px) at ground row y

export default function field(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, far: 1800, mist: 500, ground: 160, fg: 50 }; const planes = {};
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 1111 });
    paintSky(C, { stops: [[-500, hex('#05071c')], [0, hex('#0a0e32')], [300, hex('#161c50')], [500, hex('#2a2f68')], [600, hex('#4a4a84')]], glow: { x: 520, y: 330, rx: 300, ry: 240, col: hex('#7a82c0'), a: 0.35 },
      clouds: [{ y: 200, h: 12, x0: -300, x1: 1000, col: hex('#10143c'), lit: hex('#3a4088'), litA: 0.6, sy: 0.03 }, { y: 420, h: 9, x0: -100, x1: 1000, col: hex('#222862'), lit: hex('#6a64a0'), litA: 0.5, thr: 0.5, sy: 0.04 }] });
    const R = rng(11111); for (let i = 0; i < 120; i++) { const x = lerp(r[0], r[2], R()), y = lerp(r[1], 560, R() * R()); C.g.fillStyle = rgba([220, 225, 255], 0.25 + R() * 0.6); C.g.beginPath(); C.g.arc(x, y, 0.5 + R() * 1.0, 0, 7); C.g.fill(); }
    { const g = C.g; const gr = g.createRadialGradient(520, 330, 4, 520, 330, 46); gr.addColorStop(0, 'rgba(240,240,255,1)'); gr.addColorStop(0.35, 'rgba(225,230,255,0.95)'); gr.addColorStop(1, 'rgba(160,170,230,0)'); g.fillStyle = gr; g.beginPath(); g.arc(520, 330, 46, 0, 7); g.fill(); }
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.far); r[1] = Math.max(r[1], 300); r[3] = Math.min(r[3], 700); const C = new Canvas(r, { seed: 1121 });
    paintRange(C, { ridge: (x) => 590 - bump(x, 120, 160, 70) - bump(x, 520, 200, 60) - 20 * ridged(x * 0.008, 3, 5), top: hex('#232a58'), mid: hex('#1c2250'), base: hex('#1a1f48'), fall: 160, light: { dir: -1, col: hex('#4a5088'), amt: 0.3 }, haze: { col: hex('#3a3f78'), y0: 570, y1: 680, a: 0.7 }, rim: hex('#7a78aa') });
    C.mottle({ amt: 0.05 }); planes.far = S.plane('far', D.far, r, C.c); }
  { const r = cover(D.ground, 60); r[1] = Math.max(r[1], 560); const C = new Canvas(r, { seed: 1131 }); const R = rng(11311); const g = C.g;
    const fc = (x, y) => mixc(mixc(hex('#2c3248'), hex('#171a28'), smoothstep(560, 1200, y)), hex('#3c4066'), 0.3 * smoothstep(740, 560, y));
    const path = new Path2D(); path.rect(r[0], 556, r[2] - r[0], r[3] - 556); underpaint(C, fc, path, 6);
    C.strokes({ n: C.area / 700, mask: C.mask((gg) => gg.fill(path)), color: fc, angle: () => (R() - 0.5) * 0.25, len: [16, 52], wid: [4, 10], alpha: [0.4, 0.75], jv: 0.08 });
    // moonlit sheen along the far ground, patches of short grass, churned earth where the armies fought
    for (let i = 0; i < 160; i++) { const y = lerp(600, 1280, Math.pow(R(), 0.9)), x = lerp(r[0], r[2], R()); const h = 5 + (y - 560) * 0.05; for (let k = 0; k < 4; k++) C.dab(x + (R() - 0.5) * h, y, -Math.PI / 2 + (R() - 0.5) * 0.9, h * (0.7 + R() * 0.6), Math.max(1.2, h * 0.1), mixc(hex('#141728'), hex('#4a5084'), R() * 0.6), 0.8, 0.1, 0.9); }
    for (let i = 0; i < 26; i++) { const y = lerp(640, 1250, Math.pow(R(), 0.8)), x = lerp(r[0], r[2], R()); const s = 14 + (y - 560) * 0.12; C.dab(x, y, (R() - 0.5) * 0.2, s * 3, s * 0.5, mixc(hex('#12141f'), hex('#262a40'), R()), 0.5, 0.05); }
    // the fallen, drawn as people: a prone figure with a head, shoulders, legs and a cloak; shields seen at a low angle with boss and rim; broken spears; arrows
    const gh2 = (y) => gh(y); const items = []; for (let i = 0; i < 42; i++) items.push({ y: lerp(600, 1290, Math.pow(R(), 0.85)), x: lerp(r[0] + 20, r[2] - 20, R()), k: R(), d: R() < 0.5 ? 1 : -1 });
    items.sort((a, b) => a.y - b.y);
    const prone = (x, y, h, d, tone) => { g.save(); g.translate(x, y); g.scale(d, 1); const L = h * 0.95, T = h * 0.13;
      g.fillStyle = 'rgba(4,5,12,0.45)'; g.beginPath(); g.ellipse(L * 0.05, T * 0.35, L * 0.62, T * 0.55, 0, 0, 7); g.fill();
      g.fillStyle = rgba(mixc(hex('#10121e'), tone, 0.5)); g.beginPath(); g.moveTo(-L * 0.42, -T * 0.05); g.quadraticCurveTo(-L * 0.46, -T * 0.7, -L * 0.2, -T * 0.78); g.quadraticCurveTo(L * 0.1, -T * 1.0, L * 0.22, -T * 0.72); g.quadraticCurveTo(L * 0.32, -T * 0.3, L * 0.2, T * 0.12); g.lineTo(-L * 0.4, T * 0.1); g.closePath(); g.fill();      // torso and cloak
      g.beginPath(); g.moveTo(-L * 0.4, -T * 0.4); g.lineTo(-L * 0.62, -T * 0.55); g.lineTo(-L * 0.74, -T * 0.2); g.lineTo(-L * 0.4, T * 0.08); g.closePath(); g.fill(); g.beginPath(); g.moveTo(-L * 0.38, -T * 0.15); g.lineTo(-L * 0.7, T * 0.06); g.lineTo(-L * 0.66, T * 0.2); g.lineTo(-L * 0.38, T * 0.12); g.closePath(); g.fill();   // legs
      g.fillStyle = rgba(hex('#0b0c16')); g.beginPath(); g.ellipse(L * 0.32, -T * 0.4, T * 0.62, T * 0.55, 0, 0, 7); g.fill();                                 // head
      g.strokeStyle = 'rgba(140,150,220,0.34)'; g.lineWidth = Math.max(0.8, T * 0.08); g.beginPath(); g.moveTo(-L * 0.38, -T * 0.7); g.quadraticCurveTo(L * 0.1, -T * 1.0, L * 0.22, -T * 0.72); g.stroke();      // moon rim
      g.strokeStyle = rgba(mixc(hex('#10121e'), tone, 0.5)); g.lineWidth = T * 0.42; g.lineCap = 'round'; g.beginPath(); g.moveTo(L * 0.1, -T * 0.4); g.lineTo(L * 0.34 + h * 0.06, T * 0.0 - (R() - 0.5) * T); g.stroke(); g.restore(); };
    for (const it of items) { const h = gh2(it.y) * 0.5; const { x, y } = it; if (h < 4) continue;
      if (it.k < 0.4) prone(x, y, h * 1.5, it.d, R() < 0.3 ? hex('#4a2430') : hex('#2a3052'));
      else if (it.k < 0.58) { g.save(); g.translate(x, y); g.rotate((R() - 0.5) * 0.4); const rx = h * 0.3, ry = rx * (0.14 + 0.1 * R()); g.fillStyle = 'rgba(4,5,12,0.45)'; g.beginPath(); g.ellipse(3, ry * 0.9, rx * 1.05, ry * 0.7, 0, 0, 7); g.fill();
        const tone = R() < 0.35 ? hex('#3a2230') : hex('#252a44'); g.fillStyle = rgba(tone); g.beginPath(); g.moveTo(-rx, 0); g.quadraticCurveTo(0, -ry * 2.6, rx, 0); g.quadraticCurveTo(0, ry * 1.4, -rx, 0); g.fill();
        g.strokeStyle = 'rgba(160,170,235,0.55)'; g.lineWidth = Math.max(1, h * 0.014); g.beginPath(); g.moveTo(-rx, 0); g.quadraticCurveTo(0, -ry * 2.6, rx, 0); g.stroke(); g.fillStyle = rgba([170, 175, 215], 0.6); g.beginPath(); g.ellipse(rx * 0.05, -ry * 0.9, rx * 0.13, ry * 0.28, 0, 0, 7); g.fill(); g.restore(); }
      else if (it.k < 0.78) { const a = (R() - 0.5) * 0.7; const L2 = h * (1.2 + R() * 0.9); g.strokeStyle = rgba(hex('#2a2030')); g.lineWidth = Math.max(1.2, h * 0.02); g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.sin(a) * L2, y - Math.cos(a) * L2); g.stroke(); if (R() < 0.5) { g.fillStyle = rgba(hex('#3a1c28'), 0.8); g.beginPath(); g.moveTo(x + Math.sin(a) * L2, y - Math.cos(a) * L2); g.lineTo(x + Math.sin(a) * L2 * 0.9 + h * 0.18, y - Math.cos(a) * L2 * 0.93); g.lineTo(x + Math.sin(a) * L2 * 0.88 + h * 0.1, y - Math.cos(a) * L2 * 0.84); g.fill(); } else { g.fillStyle = rgba([150, 160, 210], 0.5); g.beginPath(); g.moveTo(x + Math.sin(a) * L2, y - Math.cos(a) * L2); g.lineTo(x + Math.sin(a) * L2 * 1.07 + 0.4, y - Math.cos(a) * L2 * 1.07); g.lineTo(x + Math.sin(a) * L2 + h * 0.03, y - Math.cos(a) * L2 + h * 0.08); g.fill(); } }
      else { for (let k = 0; k < 3; k++) { const a = -Math.PI / 2 + 0.4 + (R() - 0.5) * 0.9; const L3 = h * (0.5 + 0.2 * R()); g.strokeStyle = rgba(hex('#1c1a2a')); g.lineWidth = Math.max(1, h * 0.012); g.beginPath(); g.moveTo(x + k * h * 0.07, y); g.lineTo(x + k * h * 0.07 + Math.cos(a) * L3, y + Math.sin(a) * L3 * 0.6); g.stroke(); } } }
    { const gr = g.createLinearGradient(0, 556, 0, 720); gr.addColorStop(0, 'rgba(70,76,130,0.9)'); gr.addColorStop(1, 'rgba(70,76,130,0)'); g.fillStyle = gr; g.fillRect(r[0], 556, r[2] - r[0], 170); g.save(); g.globalCompositeOperation = 'destination-out'; const g2 = g.createLinearGradient(0, 556, 0, 600); g2.addColorStop(0, 'rgba(0,0,0,1)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = g2; g.fillRect(r[0], 540, r[2] - r[0], 70); g.restore(); }
    C.mottle({ amt: 0.06 }); planes.ground = S.plane('ground', D.ground, r, C.c); }
  { const r = cover(D.mist, 150); r[1] = Math.max(r[1], 560); r[3] = Math.min(r[3], 900); const C = new Canvas(r, { seed: 1141 });
    paintFog(C, { y: (x) => 690 + 14 * Math.sin(x * 0.004), h: 60, col: hex('#5a5e94'), top: hex('#7a7eb4'), a: 0.8, density: 1.4, wisp: 0.8, blur: 3 }); planes.mist = S.plane('mist', D.mist, r, C.c); planes.mist.userData.drift = 3; }
  { const r = cover(D.fg, 40); planes.grass = paintGrassStrip(S, 'grass', D.fg - 1, [r[0], 1230, r[2], 1385], { seed: 99, col: hex('#05060f'), lit: hex('#2a3060'), h0: 30, h1: 78, step: 12, amp: 0.005, freq: 15 }); }
  tintAll(S, 1);
  const flame = (g, x, y, s, t, seed) => torch(g, x, y, s, t, seed, 1);
  return {
    planes, D,
    update(F) {
      const t = F.t, sh = F.shot, g = F.g, lt = F.lt; const gg = F.glow(); const mode = sh.mode || 'dead';
      const pf = (x, y) => F.P(D.ground, x, y), kf = (x, y) => F.K(D.ground, x, y);
      const mp = F.P(D.sky, 520, 330); glowAt(gg, mp[0], mp[1], 220, 0.18, [150, 160, 230]);
      // far torches searching the field: they drift along the horizon, flicker, and one group sweeps back and forth
      if (sh.search !== false) for (let k = 0; k < 7; k++) { const x = 40 + k * 104 + 36 * Math.sin(t * 0.21 + k * 2); const y = 596 + (k % 3) * 9; const p = pf(x, y), K = kf(x, y); glowAt(gg, p[0], p[1] - 6 * K, 14 * K + 6, 0.4 * fireFlick(t, k + 10), [255, 170, 90]); }
      const solid = (x, y) => { const p = pf(x, y), K = kf(x, y); return { p, K, h: gh(y) * K }; };
      const arr = []; const draw = () => { arr.sort((a, b) => a.y - b.y); for (const o of arr) o.fn(); };
      const MPX = (y) => gh(y) / 1.75;                         // ground-plane px per metre at row y
      const P_ = { crimson: hex('#4b1a24'), crimson2: hex('#5a2430') };
      if (mode === 'dead') {
        // one figure lying among the fallen: breath (and, in the cold, its vapour), a hand; at `rise` he lifts his head
        const x = sh.fx ?? 360, y = sh.fy ?? 960; const { p, K, h } = solid(x, y); const br = 0.008 * Math.sin(t * 1.4); const rise = sh.rise ? smoothstep(sh.rise, sh.rise + 0.9, t) : 0;
        g.save(); g.translate(p[0], p[1]); g.fillStyle = 'rgba(4,5,12,0.32)'; g.beginPath(); g.ellipse(-h * 0.04, h * 0.015, h * 0.58, h * 0.045, 0, 0, 7); g.fill();
        g.fillStyle = rgba(hex('#241a32')); g.beginPath(); g.moveTo(-h * 0.5, -h * 0.01); g.quadraticCurveTo(-h * 0.54, -h * 0.14, -h * 0.25, -h * (0.17 + br)); g.quadraticCurveTo(h * 0.15, -h * (0.22 + br + rise * 0.03), h * 0.32, -h * (0.15 + rise * 0.04)); g.quadraticCurveTo(h * 0.44, -h * 0.06, h * 0.34, h * 0.0); g.closePath(); g.fill();
        g.fillStyle = rgba(P_.crimson, 0.85); g.beginPath(); g.moveTo(-h * 0.3, -h * 0.12); g.quadraticCurveTo(-h * 0.05, -h * 0.2, h * 0.28, -h * 0.13); g.lineTo(h * 0.22, -h * 0.02); g.lineTo(-h * 0.3, -h * 0.02); g.closePath(); g.fill();   // his cloak
        g.beginPath(); g.moveTo(-h * 0.48, -h * 0.06); g.lineTo(-h * 0.7, -h * 0.1); g.lineTo(-h * 0.76, h * 0.0); g.lineTo(-h * 0.48, h * 0.0); g.closePath(); g.fillStyle = rgba(hex('#1a1426')); g.fill();
        g.fillStyle = rgba(hex('#0c0a14')); g.beginPath(); g.ellipse(h * 0.42, -h * (0.1 + rise * 0.07), h * 0.082, h * 0.09, 0, 0, 7); g.fill();
        g.strokeStyle = 'rgba(150,160,230,0.4)'; g.lineWidth = Math.max(1, h * 0.012); g.beginPath(); g.moveTo(-h * 0.45, -h * 0.12); g.quadraticCurveTo(0, -h * (0.22 + br), h * 0.3, -h * (0.16 + rise * 0.04)); g.stroke(); g.restore();
        const u = (t % 2.8) / 2.8; const va = Math.sin(Math.PI * Math.min(1, u * 1.2)) * (u < 0.85 ? 1 : 0); smoke(g, t, p[0] + h * 0.5, p[1] - h * 0.12, { n: 4, rise: h * 0.25, wind: 8, r0: h * 0.025, r1: h * 0.09, a: 0.2 * va, life: 2.8, col: [170, 180, 230], seed: 2 });
        glowAt(gg, p[0], p[1] - h * 0.1, h * 1.3, 0.07, [150, 160, 230]);
      }
      if (mode === 'escape') {
        // 76.74 to 82.69: the pursuers' torches run in from the left, the son helps his father to the horse and lifts him up, the son mounts, both ride off to the right into the dark
        const u = lt; const xA = 540, yA = 1005, xB = 640, yB = 1012; const vA = clamp((u - 4.0) / 1.0); const gv = (u) => (u < 4.0 ? 0 : Math.min(1, (u - 4.0) / 0.9));
        const dist = (u0) => { const e = Math.max(0, u - u0); return e < 0.9 ? 3.5 * e * e / 1.8 : 3.5 * 0.9 / 2 + 3.5 * (e - 0.9); };   // metres: accelerates to a canter, then a steady 3.5 m/s...
        const dA = (u < 4.0 ? 0 : (7.0 * (u - 4.0) * Math.min(1, (u - 4.0) / 0.8) * 0.5 + 7.0 * Math.max(0, u - 4.8) * 0.5)), dB = (u < 4.15 ? 0 : (7.0 * (u - 4.15) * Math.min(1, (u - 4.15) / 0.8) * 0.5 + 7.0 * Math.max(0, u - 4.95) * 0.5));
        // pursuers: a jog (2.6 m/s) from the left edge, torches high; they slow to a walk as they see the riders leave
        for (let k = 0; k < 8; k++) { const y = 700 + (k * 53) % 190; const m = MPX(y); const e = clamp(u - 3.4, 0, 1.2); const dx = 2.3 * Math.min(u, 3.4) + 2.3 * e - (2.3 - 0.3) * e * e / 2.4 + 0.3 * Math.max(0, u - 4.6);
          const x = -430 + k * 34 + (k % 2) * 26 + dx * m; const ph = dx / (STRIDE * 1.75 * 1.2) + k * 0.37; const wk = u < 4.6 ? 1 : lerp(1, 0.3, clamp((u - 4.6) / 0.8));
          arr.push({ y, fn: () => { const { p, K, h } = solid(x, y); if (h < 4 || p[0] < -90 || p[0] > 820) return; const a = person(g, { x: p[0], y: p[1], h, face: 1, ph, walk: wk, col: hex('#241a30'), col2: hex('#3a2848'), hood: false, skinCol: hex('#140e1c'), helm: true, hem: 0.3, stride: 1.2, reach: [0.3, 0.8], t });
              const f = flame(g, a.hand[0] + h * 0.04, a.hand[1] - h * 0.08, h * 0.17, t, k); glowAt(gg, f[0], f[1], h * 1.4, 0.55 * fireFlick(t, k), [255, 170, 90]); if (F.lights.length < 6) F.lights.push({ x: f[0], y: f[1], r: h * 1.6, c: WARM, k: 0.45 }); } }); }
        // the horses (a plain standing horse until the ride begins)
        const horseAt = (x, y, d, o) => { const { p, K, h } = solid(x + d * MPX(y), y); const hw = h * 0.8; return { p, hw, h, K }; };
        const walkLen = 1.4, hwM = 1.4;
        const rec = (u0) => 75 * ease.inOutSine(clamp((u - u0) / 2.4)); const yAr = yA - rec(4.0), yBr = yB - rec(4.15);
        const hA = (() => { const x = xA + dA * MPX(yA); const { p, h } = solid(x, yAr); return { p, h, hw: h * 0.8 }; })(); const hB = (() => { const x = xB + dB * MPX(yB); const { p, h } = solid(x, yBr); return { p, h, hw: h * 0.8 }; })();
        const phA = dA / (2.25 * 1.4) + 0.0, phB = dB / (2.25 * 1.4) + 0.15; const gA = u < 4.0 ? 0 : 1, gBb = u < 4.15 ? 0 : 1;
        arr.push({ y: yA, fn: () => { const hs = horse(g, { x: hA.p[0], y: hA.p[1], h: hA.hw, face: 1, ph: phA, gallop: gA, stand: u < 4.0, col: hex('#161224'), t }); const lift = smoothstep(2.0, 3.4, u);
            // the father: helped along, then lifted up
            const fx = lerp(hs.saddle[0] - hA.h * 0.95, hs.saddle[0], ease.inOutSine(lift)), fy = lerp(hA.p[1], hs.saddle[1] + 0.5 * hA.h * 0.98, ease.inOutQuad(lift)) - 0.22 * hA.h * Math.sin(Math.PI * lift);
            const seated = lift >= 0.999; person(g, { x: fx, y: fy, h: hA.h * 0.98, face: 1, view: undefined, walk: seated ? 0 : 0.35 * (u < 2.0 ? 1 : 0), ph: u * 0.5, noLegs: lift > 0.55, seat: seated, col: P_.crimson, col2: P_.crimson2, cape: hex('#5a1a2a'), crown: true, hood: false, skinCol: hex('#140e1c'), reach: seated ? [0.22, 0.62] : [0.3, 0.7], head: seated ? 0.02 : 0.14, hem: 0.1, t, stride: 0.5 }); } });
        arr.push({ y: yB, fn: () => { const hs = horse(g, { x: hB.p[0], y: hB.p[1], h: hB.hw, face: 1, ph: phB, gallop: gBb, stand: u < 4.15, col: hex('#1c1628'), t });
            const m = smoothstep(3.55, 4.1, u); const sx = lerp(hB.p[0] - hB.h * 1.4, hs.saddle[0], m);
            // the son: steadies his father at the horse, then walks to his own and swings up
            const sy = lerp(hB.p[1], hs.saddle[1] + 0.5 * hB.h * 0.98, ease.inOutQuad(m)) - 0.2 * hB.h * Math.sin(Math.PI * m); const walkSon = u < 3.55 ? 0.15 : (m < 1 ? 0.7 : 0); const sonX = u < 2.0 ? hA.p[0] - hA.h * 1.35 : (u < 3.55 ? hA.p[0] - hA.h * 1.3 : sx);
            const sonY = u < 3.55 ? hA.p[1] + 3 : sy;
            person(g, { x: sonX, y: sonY, h: hB.h * 0.98, face: 1, walk: m >= 1 ? 0 : walkSon, ph: u * 0.7, noLegs: m > 0.55, seat: m >= 1, col: hex('#23283c'), col2: hex('#343c58'), hood: false, skinCol: hex('#140e1c'), helm: true, reach: m >= 1 ? [0.22, 0.62] : [0.34, 0.85], head: -0.02, hem: 0.1, t, stride: 0.6 }); } });
        draw();
        F.lights.length < 7 && F.lights.push({ x: -40, y: 560, r: 900, c: WARM, k: 0.5 * fireFlick(t, 3) });
      }
      if (sh.fire) { const p = F.P(D.far, 40, 600); glowAt(gg, p[0], p[1], 300 * F.K(D.far), 0.09 * fireFlick(t, 1), [255, 120, 60]); F.lights.length < 8 && F.lights.push({ x: p[0], y: p[1], r: 520, c: WARM, k: 0.5 }); }
      // life of the night field: crows crossing the moon, a hanging mist, vapour of far fires, motes of cold light, grass in the wind
      birds(g, t, { x0: -40, x1: 760, y0: 260, y1: 380, n: 4, seed: 11, size: 7, speed: 14, dir: -1, hz: 1.7, col: [8, 8, 24], a: 0.85 });
      hazeBand(gg, t, { y: 760, n: 5, h: 50, w: 340, a: 0.05, col: [120, 130, 210], speed: 6, seed: 2 });
      motes(gg, t, { x0: 0, y0: 500, x1: 720, y1: 1100 }, { n: 16, col: [190, 200, 255], a: 0.25, size: 1.0, seed: 13, drift: [4, -1] });
      F.amb = [0.9, 0.95, 1.15]; F.bloom = 0.5;
    },
  };
}
