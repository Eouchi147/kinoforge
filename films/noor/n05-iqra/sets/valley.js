// SET valley: Makkah at dusk, seen from a hillside above. Bare mountains ring the valley; flat-roofed houses of mud brick; in
// the middle the Kaaba (a simple dark cube) with small stone statues set around it (idols, kept small and wide); cook fires and
// their smoke; tiny specks of people moving far below (no one recognisable, nobody named). Loud life, seen from far away.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, ease, rng, det, bump, lightsOn } from './common.js';
import { paintSky, paintRange, paintRocks, paintTufts, ridged } from '../paint.js';
import { birds, smoke, motes, hazeBand } from '../ambient.js';
import { glowAt, flick, hash1 } from '../fx.js';

const KAABA = [700, 470];

function flatHouse(C, x, yb, w, h, k = 1) {
  const g = C.g, R = C.R; const wall = mul(mixc(hex('#463a40'), hex('#5e4c4a'), R()), 0.75 + R() * 0.3); const top = mul(wall, 1.25);
  g.fillStyle = rgba(wall); g.fillRect(x - w / 2, yb - h, w, h); g.fillStyle = rgba(top); g.beginPath(); g.moveTo(x - w / 2, yb - h); g.lineTo(x - w / 2 + w * 0.18, yb - h - h * 0.28); g.lineTo(x + w / 2 + w * 0.18, yb - h - h * 0.28); g.lineTo(x + w / 2, yb - h); g.closePath(); g.fill();
  g.fillStyle = rgba(mul(wall, 0.6)); g.beginPath(); g.moveTo(x + w / 2, yb - h); g.lineTo(x + w / 2 + w * 0.18, yb - h - h * 0.28); g.lineTo(x + w / 2 + w * 0.18, yb - h * 0.28); g.lineTo(x + w / 2, yb); g.closePath(); g.fill();
  const out = []; if (w > 10 * k) { const dw = Math.max(2, w * 0.16), dh = h * 0.5; const dx = x + (R() - 0.5) * w * 0.5; g.fillStyle = rgba(hex('#120c14')); g.fillRect(dx - dw / 2, yb - dh, dw, dh); out.push([dx, yb - dh * 0.5, dw, dh]); }
  return out;
}

export default function valley(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, ring: 3000, side: 1700, floor: 900, near: 340, fg: 100 }; const P = {}; const doors = [], fires = [], nearDoors = [];
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 8101 });
    paintSky(C, { stops: [[-600, hex('#0a0c2a')], [0, hex('#161a46')], [120, hex('#2e2c5e')], [200, hex('#6a5070')], [260, hex('#b07a6a')], [300, hex('#d49a72')]], glow: { x: 300, y: 290, rx: 700, ry: 120, col: hex('#e0a070'), a: 0.6 },
      clouds: [{ y: 150, h: 10, x0: -400, x1: 1600, col: hex('#3a3060'), lit: hex('#b07a7a'), litA: 0.7, thr: 0.5, sy: 0.04 }] });
    P.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.ring); r[1] = Math.max(r[1], 120); const C = new Canvas(r, { seed: 8102 });
    paintRange(C, { ridge: (x) => 290 - bump(x, 100, 160, 70) - bump(x, 980, 200, 90) - bump(x, 1300, 160, 60) - 30 * ridged(x * 0.006, 4, 6), top: hex('#4a3a5a'), mid: hex('#3a3050'), base: hex('#2e2846'), fall: 140, light: { dir: -1, col: hex('#9a6a6a'), amt: 0.45 }, rim: hex('#d09a80'), haze: { col: hex('#5a4a6a'), y0: 280, y1: 360, a: 0.7 } });
    C.mottle({ amt: 0.05 }); P.ring = S.plane('ring', D.ring, r, C.c); }
  { const r = cover(D.side); r[1] = Math.max(r[1], 160); const C = new Canvas(r, { seed: 8103 });
    paintRange(C, { ridge: (x) => 380 - bump(x, -60, 260, 190) - bump(x, 1380, 300, 210) - bump(x, 220, 120, 60) + det(x, 14, 5, 3), top: hex('#33283e'), mid: hex('#2a2236'), base: hex('#221c2e'), fall: 220, light: { dir: -1, col: hex('#7a5458'), amt: 0.4 }, rim: hex('#b07a70'), sizes: 1.1 });
    C.mottle({ amt: 0.05 }); P.side = S.plane('side', D.side, r, C.c); }
  // the valley floor: sand, houses, the Kaaba and its idols
  { const r = cover(D.floor); r[1] = Math.max(r[1], 330); const C = new Canvas(r, { seed: 8104 }); const g = C.g; const n = C.n; const R = rng(81041);
    const colAt = (x, y) => mul(mixc(hex('#2e2630'), hex('#463840'), n.fbm(x * 0.005, y * 0.02, 4)), 0.8 + 0.3 * smoothstep(340, 560, y));
    underpaint(C, colAt, null, 8); C.strokes({ n: C.area / 900, color: colAt, angle: () => (R() - 0.5) * 0.15, len: [30, 90], wid: [6, 12], alpha: [0.4, 0.7], jv: 0.06, bend: 0.05 });
    // houses packed along the valley, away from the open court around the Kaaba
    const hs = []; for (let i = 0; i < 520; i++) { const x = lerp(r[0], r[2], R()); const y = lerp(350, 590, Math.pow(R(), 0.9)); if (Math.hypot((x - KAABA[0]) / 1.8, y - KAABA[1]) < 70) continue; hs.push([x, y]); }
    hs.sort((a, b) => a[1] - b[1]); for (const [x, y] of hs) { const s = lerp(0.6, 1.4, (y - 350) / 240); for (const d of flatHouse(C, x, y, (12 + R() * 16) * s, (7 + R() * 7) * s)) if (R() < 0.5) doors.push(d); if (R() < 0.08) fires.push([x + 10 * s, y + 4]); }
    // the open court and the Kaaba: a dark cube under a dark cloth, a pale line of the courtyard ground
    g.fillStyle = rgba(hex('#6a5a52'), 0.8); g.beginPath(); g.ellipse(KAABA[0], KAABA[1] + 4, 66, 18, 0, 0, 7); g.fill();
    const k = 16; g.fillStyle = rgba(hex('#141016')); g.fillRect(KAABA[0] - k, KAABA[1] - 2 * k, 2 * k, 2 * k); g.fillStyle = rgba(hex('#241e24')); g.beginPath(); g.moveTo(KAABA[0] - k, KAABA[1] - 2 * k); g.lineTo(KAABA[0] - k + 7, KAABA[1] - 2 * k - 6); g.lineTo(KAABA[0] + k + 7, KAABA[1] - 2 * k - 6); g.lineTo(KAABA[0] + k, KAABA[1] - 2 * k); g.closePath(); g.fill();
    g.fillStyle = rgba(hex('#0c080c')); g.beginPath(); g.moveTo(KAABA[0] + k, KAABA[1] - 2 * k); g.lineTo(KAABA[0] + k + 7, KAABA[1] - 2 * k - 6); g.lineTo(KAABA[0] + k + 7, KAABA[1] - 6); g.lineTo(KAABA[0] + k, KAABA[1]); g.closePath(); g.fill();
    // the idols: many small upright stones and figures in a ring (kept tiny, no detail)
    for (let i = 0; i < 46; i++) { const a = i / 46 * 6.283; const x = KAABA[0] + Math.cos(a) * 58 + (R() - 0.5) * 6, y = KAABA[1] + 2 + Math.sin(a) * 15; const h = 5 + R() * 6; g.fillStyle = rgba(mixc(hex('#3a2e2e'), hex('#7a6a5a'), R())); g.fillRect(x - 1.2, y - h, 2.4, h); g.beginPath(); g.arc(x, y - h, 1.5, 0, 7); g.fill(); }
    C.mottle({ amt: 0.05 }); P.floor = S.plane('floor', D.floor, r, C.c); }
  // near rooftops under the hillside, larger, with lit doorways
  { const r = cover(D.near, 40); r[1] = Math.max(r[1], 480); const C = new Canvas(r, { seed: 8105 }); const R = rng(81051);
    const top = (x) => 560 + 20 * Math.sin(x * 0.004) + det(x, 6, 2, 2); underpaint(C, (x, y) => mul(hex('#3a2c34'), 0.8 + 0.3 * C.n.fbm(x * 0.01, y * 0.01, 3)), (() => { const p = new Path2D(); p.moveTo(r[0], r[3]); for (let x = r[0]; x <= r[2]; x += 4) p.lineTo(x, top(x)); p.lineTo(r[2], r[3]); p.closePath(); return p; })(), 8);
    const hs = []; for (let i = 0; i < 70; i++) { const x = lerp(r[0], r[2], R()); hs.push([x, top(x) + 30 + R() * 140]); } hs.sort((a, b) => a[1] - b[1]);
    for (const [x, y] of hs) for (const d of flatHouse(C, x, y, 40 + R() * 50, 26 + R() * 20, 1)) if (R() < 0.6) nearDoors.push(d);
    C.mottle({ amt: 0.05 }); P.near = S.plane('near', D.near, r, C.c); }
  { const r = cover(D.fg, 40); r[1] = Math.max(r[1], 560); const C = new Canvas(r, { seed: 8106 });
    paintRocks(C, { rocks: [{ x: 120, y: 760, rx: 330, ry: 90 }, { x: 1220, y: 750, rx: 260, ry: 80 }], col: hex('#0a080e'), lit: hex('#3a2a30'), litA: 0.45, blur: 3 });
    paintTufts(C, { x0: r[0], x1: 520, base: () => 690, step: 18, h0: 10, h1: 24, col: hex('#0e0c12'), blades: 5, jitter: 24 }); P.fg = S.plane('fg', D.fg, r, C.c); }
  const doorGlow = doors.slice(0, 70).map(([x, y, w, h], i) => S.glow(x, y, D.floor, 6 + hash1(i) * 5, { color: [1.0, 0.62, 0.3], core: 200 }, P.floor));
  const nearGlow = nearDoors.slice(0, 26).map(([x, y, w, h]) => S.glow(x, y, D.near, Math.max(w, h) * 1.4, { color: [1.0, 0.6, 0.28], shape: 1, rect: [0.42, 0.62] }, P.near));
  const fireGlow = fires.slice(0, 20).map(([x, y]) => S.glow(x, y, D.floor, 16, { color: [1.0, 0.55, 0.22], core: 120 }, P.floor));
  return {
    planes: P, D,
    update(F) {
      const t = F.t, g = F.g, gg = F.glow();
      for (const pl of Object.values(P)) pl.material.uniforms.uTint.value.set(0.86, 0.84, 0.94);
      doorGlow.forEach((gm, i) => { gm.visible = true; gm.material.uniforms.uI.value = 0.5 * flick(t, i); });
      nearGlow.forEach((gm, i) => { gm.visible = true; gm.material.uniforms.uI.value = 0.55 * flick(t, i + 40); });
      fireGlow.forEach((gm, i) => { gm.visible = true; gm.material.uniforms.uI.value = 0.9 * flick(t * 1.4, i + 80); });
      for (let i = 0; i < fires.length && i < 20; i++) { const p = F.P(D.floor, fires[i][0], fires[i][1]); smoke(g, t, p[0], p[1], { n: 6, rise: 70, wind: 10, r0: 2, r1: 14, a: 0.13, col: [110, 96, 110], life: 8, seed: i + 3 }); }
      // tiny specks of people moving around the court and along the lanes (no one recognisable)
      for (let i = 0; i < 70; i++) { const r1 = hash1(i * 1.3), r2 = hash1(i * 2.7), r3 = hash1(i * 4.1); let x, y;
        if (i < 30) { const a = r1 * 6.283 - t * (0.05 + r2 * 0.03); x = KAABA[0] + Math.cos(a) * (36 + r3 * 18); y = KAABA[1] + 1 + Math.sin(a) * (10 + r3 * 4); }
        else { x = lerp(-200, 1500, (r1 + t * (0.004 + r2 * 0.006) * (i % 2 ? 1 : -1) + 10) % 1); y = lerp(380, 580, r3); }
        const p = F.P(D.floor, x, y); const K = F.K(D.floor); g.fillStyle = `rgba(${30 + 40 * r2 | 0},${22 + 30 * r2 | 0},${30 + 20 * r3 | 0},0.85)`; g.fillRect(p[0] - 0.7 * K, p[1] - 3.2 * K, 1.5 * K, 3.2 * K); }
      // the warm low sun: a sunset bloom on the left horizon; birds crossing; dust haze over the valley
      { const c = F.P(D.ring, 300, 300); glowAt(gg, c[0], c[1], 520, 0.32, [255, 170, 110]); }
      birds(g, t, { x0: -80, x1: 1360, y0: 120, y1: 260, n: 7, seed: 12, size: 6, speed: 20, dir: -1, hz: 2.0, col: [40, 26, 40], a: 0.8 });
      hazeBand(gg, t, { y: F.P(D.floor, 600, 420)[1], x0: -200, x1: 1480, n: 7, h: 40, w: 520, a: 0.06, col: [220, 160, 140], speed: 7, seed: 5 });
      motes(gg, t, { x0: 0, y0: 300, x1: 1280, y1: 720 }, { n: 16, col: [255, 200, 150], a: 0.2, size: 1.1, seed: 17, drift: [5, -2] });
      F.amb = [0.95, 0.9, 0.95];
    },
  };
}
