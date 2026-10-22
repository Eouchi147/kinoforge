// SET field: a cold night field after a battle (shields, spears, the fallen in mist, a moon) and the flight of Samuel across it:
// pursuers with torches, a son who puts his father on a horse, the gallop away. No gore: the fallen are dark shapes in the mist.
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, fireFlick, tintAll } from './common.js';
import { paintSky, paintRange, paintFog, paintRocks, paintTufts } from '../paint.js';
import { person, horse, banner, glowAt, torch, embers, hash1, PAL } from '../figs.js';

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
    // the fallen, shields, spears: far to near
    const items = []; for (let i = 0; i < 70; i++) items.push({ y: lerp(580, 1280, Math.pow(R(), 0.8)), x: lerp(r[0] + 10, r[2] - 10, R()), k: R() });
    items.sort((a, b) => a.y - b.y);
    for (const it of items) { const h = gh(it.y); const { x, y } = it;
      if (it.k < 0.38) { // a body: a dark lump with a head, a cloak
        g.fillStyle = rgba(mixc(hex('#0e0f1c'), hex('#2a2a46'), R() * 0.4)); g.beginPath(); g.ellipse(x, y, h * (0.45 + R() * 0.2), h * 0.1, (R() - 0.5) * 0.2, 0, 7); g.fill(); g.beginPath(); g.arc(x + h * 0.46 * (R() < 0.5 ? 1 : -1), y - h * 0.02, h * 0.07, 0, 7); g.fill(); g.fillStyle = rgba([120, 130, 190], 0.14); g.beginPath(); g.ellipse(x - h * 0.1, y - h * 0.06, h * 0.3, h * 0.03, 0, 0, 7); g.fill(); }
      else if (it.k < 0.55) { // a shield on the ground
        g.fillStyle = rgba(mixc(hex('#1a1a30'), hex('#2c2c4c'), R())); g.beginPath(); g.ellipse(x, y, h * 0.2, h * 0.055, 0, 0, 7); g.fill(); g.strokeStyle = rgba([120, 130, 190], 0.3); g.lineWidth = Math.max(1, h * 0.012); g.beginPath(); g.ellipse(x, y - h * 0.01, h * 0.2, h * 0.055, 0, Math.PI * 1.05, Math.PI * 1.95); g.stroke(); }
      else { // a spear planted, leaning
        const a = (R() - 0.5) * 0.5; g.strokeStyle = rgba(hex('#2a2030')); g.lineWidth = Math.max(1.2, h * 0.018); g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.sin(a) * h * 1.7, y - Math.cos(a) * h * 1.7); g.stroke(); g.fillStyle = rgba([150, 160, 210], 0.5); g.beginPath(); g.moveTo(x + Math.sin(a) * h * 1.7, y - Math.cos(a) * h * 1.7); g.lineTo(x + Math.sin(a) * h * 1.82 + 0.4, y - Math.cos(a) * h * 1.82); g.lineTo(x + Math.sin(a) * h * 1.7 + h * 0.03, y - Math.cos(a) * h * 1.7 + h * 0.08); g.fill(); } }
    { const gr = g.createLinearGradient(0, 556, 0, 720); gr.addColorStop(0, 'rgba(70,76,130,0.9)'); gr.addColorStop(1, 'rgba(70,76,130,0)'); g.fillStyle = gr; g.fillRect(r[0], 556, r[2] - r[0], 170); g.save(); g.globalCompositeOperation = 'destination-out'; const g2 = g.createLinearGradient(0, 556, 0, 600); g2.addColorStop(0, 'rgba(0,0,0,1)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = g2; g.fillRect(r[0], 540, r[2] - r[0], 70); g.restore(); }
    C.mottle({ amt: 0.06 }); planes.ground = S.plane('ground', D.ground, r, C.c); }
  { const r = cover(D.mist, 40); r[1] = Math.max(r[1], 560); r[3] = Math.min(r[3], 900); const C = new Canvas(r, { seed: 1141 });
    paintFog(C, { y: (x) => 690 + 14 * Math.sin(x * 0.004), h: 60, col: hex('#5a5e94'), top: hex('#7a7eb4'), a: 0.8, density: 1.4, wisp: 0.8, blur: 3 }); planes.mist = S.plane('mist', D.mist, r, C.c); planes.mist.userData.drift = 3; }
  { const r = cover(D.fg, 40); r[1] = Math.max(r[1], 1100); const C = new Canvas(r, { seed: 1151 });
    paintRocks(C, { rocks: [{ x: 30, y: 1320, rx: 200, ry: 90 }, { x: 720, y: 1330, rx: 260, ry: 100 }], col: hex('#05050c'), lit: hex('#1c2040'), litA: 0.4, blur: 3 }); planes.fg = S.plane('fg', D.fg, r, C.c); }
  tintAll(S, 1);
  const flame = (g, x, y, s, t, seed) => torch(g, x, y, s, t, seed, 1);
  return {
    planes, D,
    update(F) {
      const t = F.t, sh = F.shot, g = F.g, lt = F.lt; const gg = F.glow(); const mode = sh.mode || 'dead';
      const pf = (x, y) => F.P(D.ground, x, y), kf = (x, y) => F.K(D.ground, x, y);
      const mp = F.P(D.sky, 520, 330); glowAt(gg, mp[0], mp[1], 220, 0.18, [150, 160, 230]);
      // far torches searching the field
      if (sh.search !== false) for (let k = 0; k < 6; k++) { const x = 60 + k * 110 + 30 * Math.sin(t * 0.3 + k * 2); const y = 596 + (k % 3) * 9; const p = pf(x, y), K = kf(x, y); glowAt(gg, p[0], p[1] - 6 * K, 14 * K + 6, 0.4 * fireFlick(t, k + 10), [255, 170, 90]); }
      const solid = (x, y) => { const p = pf(x, y), K = kf(x, y); return { p, K, h: gh(y) * K }; };
      if (mode === 'dead') {
        // one figure lying among the fallen: breath, a hand; at `rise` he lifts his head
        const x = sh.fx ?? 360, y = sh.fy ?? 960; const { p, K, h } = solid(x, y); const br = 0.008 * Math.sin(t * 1.4); const rise = sh.rise ? smoothstep(sh.rise, sh.rise + 0.9, t) : 0;
        g.save(); g.translate(p[0], p[1]); g.fillStyle = rgba(hex('#1a1426')); g.beginPath(); g.ellipse(0, -h * 0.05, h * 0.5, h * (0.1 + br + rise * 0.04), -0.04, 0, 7); g.fill(); g.fillStyle = rgba(hex('#2c2038')); g.beginPath(); g.ellipse(-h * 0.1, -h * 0.07, h * 0.36, h * 0.07, -0.05, 0, 7); g.fill();
        g.fillStyle = rgba(hex('#0c0a14')); g.beginPath(); g.arc(h * 0.5, -h * 0.08 - rise * h * 0.1, h * 0.085, 0, 7); g.fill(); g.fillStyle = rgba([150, 160, 220], 0.18); g.beginPath(); g.ellipse(-h * 0.1, -h * 0.12, h * 0.3, h * 0.025, 0, 0, 7); g.fill(); g.restore();
        glowAt(gg, p[0], p[1] - h * 0.1, h * 1.3, 0.07, [150, 160, 230]);
      }
      if (mode === 'chase') {
        // pursuers with torches run in from the left; the father and son at the right look back
        const u = lt; const arr = [];
        for (let k = 0; k < 8; k++) { const x = -80 + u * 120 + k * 52 + (k % 2) * 25; const y = 700 + (k * 53) % 180; arr.push({ y, x, k }); }
        arr.sort((a, b) => a.y - b.y); for (const o of arr) { const { p, K, h } = solid(o.x, o.y); if (h < 4) continue; const a = person(g, { x: p[0], y: p[1], h, face: 1, ph: u * 1.7 + o.k * 0.37, walk: 1, col: hex('#241a30'), col2: hex('#3a2848'), hood: false, skinCol: hex('#140e1c'), hem: 0.3, stride: 1.2, reach: [0.3, 0.75] });
          const f = flame(g, a.hand[0] + h * 0.04, a.hand[1] - h * 0.08, h * 0.17, t, o.k); glowAt(gg, f[0], f[1], h * 1.4, 0.55 * fireFlick(t, o.k), [255, 170, 90]); F.lights.push({ x: f[0], y: f[1], r: h * 1.6, c: WARM, k: 0.45 }); }
        const s = solid(560, 1000); person(g, { x: s.p[0], y: s.p[1], h: s.h * 1.02, face: -1, walk: 0.0, col: hex('#4b1a24'), col2: hex('#5a2430'), cape: hex('#5a1a2a'), crown: true, hood: false, skinCol: hex('#140e1c'), head: -0.1 });
        const so = solid(630, 1010); person(g, { x: so.p[0], y: so.p[1], h: so.h * 0.98, face: -1, walk: 0, col: hex('#23283c'), col2: hex('#343c58'), hood: false, skinCol: hex('#140e1c'), reach: [0.35, 0.8] });
      }
      if (mode === 'mount') {
        // the son lifts his father into the saddle
        const lift = smoothstep(sh.liftAt ?? 0.3, sh.liftAt ?? 0.3 + 1.2, lt); const hx = 420, hy = 980; const h0 = solid(hx, hy); const hh = h0.h * 1.0;
        const hs = horse(g, { x: h0.p[0], y: h0.p[1], h: hh, face: -1, ph: 0.3 + t * 0.2, gallop: 0, col: hex('#161224') });
        const rx = lerp(h0.p[0] + hh * 0.55, hs.saddle[0], lift), ry = lerp(h0.p[1], hs.saddle[1] + 0.5 * hh * 1.1, lift * lift * (3 - 2 * lift));
        person(g, { x: rx, y: ry, h: hh * 1.1, face: -1, walk: 0, noLegs: lift > 0.5, col: hex('#4b1a24'), col2: hex('#5a2430'), cape: hex('#5a1a2a'), crown: true, hood: false, skinCol: hex('#140e1c'), reach: [0.3, 0.7], head: 0.08 });
        const sx = lerp(h0.p[0] + hh * 0.9, h0.p[0] + hh * 0.52, lift * 0.0 + 0.6 * smoothstep(0, 1, lift)); person(g, { x: sx, y: h0.p[1] + 3, h: hh * 1.02, face: -1, walk: 0.15, ph: t * 0.9, col: hex('#23283c'), col2: hex('#343c58'), hood: false, skinCol: hex('#140e1c'), reach: [0.3, 0.85] });
        F.lights.push({ x: -40, y: 560, r: 900, c: WARM, k: 0.5 * fireFlick(t, 3) });
      }
      if (mode === 'gallop') {
        // two horses gallop off into the dark, pursuers' torches far behind
        const u = clamp(lt / sh.dur); const arr = [];
        for (let k = 0; k < 2; k++) { const e = ease.inQuad(clamp(u * 0.9 + k * -0.04)); const x = lerp(520 - k * 70, 80 - k * 20, e), y = lerp(960 - k * 20, 760 - k * 6, e); arr.push({ x, y, k }); }
        arr.sort((a, b) => a.y - b.y); for (const o of arr) { const { p, K, h } = solid(o.x, o.y); const hh = h * 1.0; const hs = horse(g, { x: p[0], y: p[1], h: hh, face: -1, ph: lt * 2.6 + o.k * 0.2, gallop: 1, col: hex('#161224') });
          person(g, { x: hs.saddle[0], y: hs.saddle[1] + 0.5 * hh * 1.1, h: hh * 1.1, face: -1, noLegs: true, walk: 0, col: o.k ? hex('#23283c') : hex('#4b1a24'), col2: hex('#5a2430'), cape: o.k ? null : hex('#5a1a2a'), crown: !o.k, hood: false, skinCol: hex('#140e1c'), reach: [0.3, 0.7] });
          glowAt(gg, p[0], p[1] - hh * 0.2, hh * 2.2, 0.12, [210, 160, 140]); }
        for (let k = 0; k < 6; k++) { const x = 640 - k * 18 - lt * 26 + (k % 2) * 30, y = 760 + k * 24; const { p, K, h } = solid(x, y); const f = flame(g, p[0], p[1] - h * 0.9, h * 0.17, t, k + 20); glowAt(gg, f[0], f[1], h * 1.6, 0.5, [255, 170, 90]); }
      }
      if (sh.fire) { const p = F.P(D.far, 40, 600); glowAt(gg, p[0], p[1], 300 * F.K(D.far), 0.09 * fireFlick(t, 1), [255, 120, 60]); F.lights.push({ x: p[0], y: p[1], r: 520, c: WARM, k: 0.5 }); }
      embers(gg, t, { x0: 0, y0: 500, x1: 720, y1: 1000 }, 14, { size: 1.0, col: [200, 210, 255], a: 0.25, wind: 6, rise: 0.2, seed: 13 });
      F.amb = [0.9, 0.95, 1.15]; F.bloom = 0.5;
    },
  };
}
