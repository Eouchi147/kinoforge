// SET house: a doorway in Makkah at night. A mud-brick wall, the door open on a warm room: a lamp in a wall niche, a folded
// cloak on a low bench, a water jar. The hand lantern that came down the mountain has been set down on the step. No people.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, ease, rng, det, bump, lightsOn } from './common.js';
import { paintSky, paintRange, ridged } from '../paint.js';
import { motes, hazeBand } from '../ambient.js';
import { glowAt, handLantern, stars, flick, hash1 } from '../fx.js';

const DOOR = [520, 210, 770, 640];       // x0, y0, x1, y1 on the wall plane
const NICHE = [700, 330], LANT = [810, 628];

export default function house(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, ridge: 2400, room: 330, wall: 260, street: 150 }; const P = {};
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 9101 });
    paintSky(C, { stops: [[-600, hex('#04060f')], [0, hex('#0a0e2a')], [140, hex('#141a44')], [200, hex('#22244e')]] });
    const R = rng(91011); for (let i = 0; i < 300; i++) { const x = lerp(r[0], r[2], R()), y = lerp(r[1], 160, R()); C.g.fillStyle = rgba([215, 222, 255], 0.2 + R() * 0.5); C.g.beginPath(); C.g.arc(x, y, 0.4 + R() * 0.8, 0, 7); C.g.fill(); }
    P.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.ridge); r[1] = Math.max(r[1], 40); const C = new Canvas(r, { seed: 9102 });
    paintRange(C, { ridge: (x) => 170 - bump(x, 300, 160, 70) - bump(x, 1000, 200, 50) - 18 * ridged(x * 0.008, 4, 7), top: hex('#16183a'), mid: hex('#121430'), base: hex('#0e1028'), fall: 80, rim: hex('#4a4672'), light: { dir: -1, col: hex('#2a2a58'), amt: 0.3 } });
    P.ridge = S.plane('ridge', D.ridge, r, C.c); }
  // the room behind the door: a plastered back wall with a niche lamp, a bench with a folded cloak, a jar
  { const r = cover(D.room, 30); const C = new Canvas(r, { seed: 9103 }); const g = C.g; const n = C.n; const R = rng(91031);
    const colAt = (x, y) => mul(mixc(hex('#6a5040'), hex('#8a6a50'), n.fbm(x * 0.01, y * 0.01, 4)), 0.7 + 0.4 * smoothstep(700, 300, Math.hypot(x - NICHE[0], y - NICHE[1])));
    underpaint(C, colAt, null, 6); C.strokes({ n: C.area / 500, color: colAt, angle: () => Math.PI / 2 + (R() - 0.5) * 0.4, len: [14, 40], wid: [6, 12], alpha: [0.35, 0.65], jv: 0.06 });
    g.fillStyle = rgba(hex('#3a2a22')); g.fillRect(r[0], 560, r[2] - r[0], r[3] - 560); // floor
    g.fillStyle = rgba(hex('#2a1c16')); g.beginPath(); g.moveTo(NICHE[0] - 30, NICHE[1] + 26); g.lineTo(NICHE[0] - 30, NICHE[1] - 14); g.quadraticCurveTo(NICHE[0], NICHE[1] - 46, NICHE[0] + 30, NICHE[1] - 14); g.lineTo(NICHE[0] + 30, NICHE[1] + 26); g.closePath(); g.fill();
    g.fillStyle = rgba(hex('#6a4430')); g.beginPath(); g.ellipse(NICHE[0], NICHE[1] + 18, 18, 7, 0, 0, 7); g.fill();
    // bench and folded cloak
    g.fillStyle = rgba(hex('#3a2618')); g.fillRect(540, 500, 200, 22); g.fillRect(552, 522, 12, 50); g.fillRect(716, 522, 12, 50);
    g.fillStyle = rgba(hex('#5a2a24')); g.beginPath(); g.moveTo(570, 500); g.lineTo(574, 474); g.quadraticCurveTo(640, 462, 700, 472); g.lineTo(704, 500); g.closePath(); g.fill();
    g.fillStyle = rgba(hex('#7a3a30'), 0.7); g.fillRect(578, 480, 120, 5); g.fillStyle = rgba(hex('#3a1a16'), 0.8); g.fillRect(576, 492, 126, 4);
    // a water jar
    g.fillStyle = rgba(hex('#7a5038')); g.beginPath(); g.ellipse(560, 600, 26, 34, 0, 0, 7); g.fill(); g.fillRect(550, 556, 20, 14); g.fillStyle = rgba(hex('#9a6a48'), 0.6); g.beginPath(); g.ellipse(552, 590, 8, 20, 0, 0, 7); g.fill();
    C.mottle({ amt: 0.07 }); P.room = S.plane('room', D.room, r, C.c); }
  // the wall with its doorway (cut out), mud brick, a wooden door leaf standing open
  { const r = cover(D.wall, 40); r[1] = Math.max(r[1], 90); const C = new Canvas(r, { seed: 9104 }); const g = C.g; const n = C.n; const R = rng(91041);
    const top = (x) => 120 + 6 * Math.sin(x * 0.02) + det(x, 4, 2, 6);
    const wp = new Path2D(); wp.moveTo(r[0] - 10, r[3] + 10); for (let x = r[0] - 10; x <= r[2] + 10; x += 4) wp.lineTo(x, top(x)); wp.lineTo(r[2] + 10, r[3] + 10); wp.closePath();
    const colAt = (x, y) => mul(mixc(hex('#3a3040'), hex('#4e4250'), n.fbm(x * 0.006, y * 0.008, 4)), 0.75 + 0.35 * smoothstep(520, 150, Math.hypot(x - 645, y - 470)));
    underpaint(C, colAt, wp, 6); const m = C.mask((gg) => gg.fill(wp));
    C.strokes({ n: C.area / 700, mask: m, color: colAt, angle: () => (R() - 0.5) * 0.2, len: [24, 60], wid: [8, 14], alpha: [0.4, 0.7], jv: 0.06 });
    g.strokeStyle = 'rgba(20,14,22,0.35)'; g.lineWidth = 1.2; for (let y = 140; y < r[3]; y += 22) { g.beginPath(); g.moveTo(r[0], y + (n.fbm(y, 1, 2) - 0.5) * 4); g.lineTo(r[2], y); g.stroke(); for (let x = r[0] + ((y / 22) % 2) * 30; x < r[2]; x += 60) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 22); g.stroke(); } }
    // lintel beam and door frame
    g.fillStyle = rgba(hex('#2a1c14')); g.fillRect(DOOR[0] - 26, DOOR[1] - 26, DOOR[2] - DOOR[0] + 52, 26); g.fillRect(DOOR[0] - 14, DOOR[1], 14, DOOR[3] - DOOR[1]); g.fillRect(DOOR[2], DOOR[1], 14, DOOR[3] - DOOR[1]);
    g.save(); g.globalCompositeOperation = 'destination-out'; g.fillRect(DOOR[0], DOOR[1], DOOR[2] - DOOR[0], DOOR[3] - DOOR[1]); g.restore();
    // the open door leaf, seen edge-on against the inner left jamb
    g.fillStyle = rgba(hex('#3a2416')); g.beginPath(); g.moveTo(DOOR[0], DOOR[1]); g.lineTo(DOOR[0] + 44, DOOR[1] + 16); g.lineTo(DOOR[0] + 44, DOOR[3] - 4); g.lineTo(DOOR[0], DOOR[3]); g.closePath(); g.fill();
    for (let k = 1; k < 4; k++) { g.strokeStyle = 'rgba(14,8,6,0.6)'; g.beginPath(); g.moveTo(DOOR[0] + 11 * k, DOOR[1] + 4 * k); g.lineTo(DOOR[0] + 11 * k, DOOR[3] - k); g.stroke(); }
    C.mottle({ amt: 0.06 }); P.wall = S.plane('wall', D.wall, r, C.c); }
  { const r = cover(D.street, 40); r[1] = Math.max(r[1], 560); const C = new Canvas(r, { seed: 9105 }); const n = C.n; const R = rng(91051);
    const colAt = (x, y) => mul(mixc(hex('#241e28'), hex('#3a3036'), n.fbm(x * 0.008, y * 0.03, 4)), 0.8 + 0.2 * smoothstep(720, 600, y));
    const sp = new Path2D(); sp.rect(r[0], 600, r[2] - r[0], r[3] - 600); underpaint(C, colAt, sp, 6); const m = C.mask((gg) => gg.fill(sp));
    C.strokes({ n: C.area / 700, mask: m, color: colAt, angle: () => (R() - 0.5) * 0.3, len: [20, 60], wid: [5, 10], alpha: [0.4, 0.7], jv: 0.08 });
    C.g.fillStyle = rgba(hex('#4a3a34')); C.g.fillRect(480, 600, 330, 14); // the step
    P.street = S.plane('street', D.street, r, C.c); }
  const nicheGlow = S.glow(NICHE[0], NICHE[1] + 4, D.room, 40, { color: [1.0, 0.7, 0.35], core: 90 }, P.room);
  return {
    planes: P, D,
    update(F) {
      const t = F.t, g = F.g, gg = F.glow(); const fl = flick(t, 4);
      for (const pl of [P.sky, P.ridge]) pl.material.uniforms.uTint.value.set(0.85, 0.85, 0.95);
      P.wall.material.uniforms.uTint.value.set(0.45, 0.44, 0.52); P.street.material.uniforms.uTint.value.set(0.5, 0.48, 0.55); P.room.material.uniforms.uTint.value.set(0.55, 0.5, 0.5);
      nicheGlow.visible = true; nicheGlow.material.uniforms.uI.value = 1.1 * fl;
      const lp = S.world(NICHE[0], NICHE[1], D.room); lightsOn(P.room, [{ p: lp, r: 70, c: [1.0, 0.6, 0.28], k: 2.6 * fl }]);
      const spill = S.world(645, 560, D.wall + 40); lightsOn(P.street, [{ p: spill, r: 70, c: [1.0, 0.58, 0.26], k: 1.6 * fl }]); lightsOn(P.wall, [{ p: spill, r: 60, c: [1.0, 0.58, 0.26], k: 0.9 * fl }]);
      { const p = F.P(D.room, NICHE[0], NICHE[1] + 10); const K = F.K(D.room); g.fillStyle = 'rgba(255,190,90,0.95)'; g.beginPath(); g.ellipse(p[0] + 6 * K, p[1], 2.4 * K, 7 * K * fl, 0, 0, 7); g.fill(); glowAt(gg, p[0], p[1], 90 * K, 0.6 * fl, [255, 170, 80]); }
      // the lantern set down on the step: he is home
      { const p = F.P(D.street, LANT[0], LANT[1] - 14); const K = F.K(D.street); handLantern(g, gg, p[0], p[1], 34 * K, t, { swing: 0.0, seed: 6 }); }
      const a = F.P(D.sky, -300, -500), b = F.P(D.sky, 1600, 120); stars(gg, t, [a[0], a[1], b[0], b[1]], { n: 70, seed: 51, a: 0.7 });
      hazeBand(gg, t, { y: 640, x0: -200, x1: 1480, n: 4, h: 30, w: 400, a: 0.04, col: [150, 140, 210], speed: 4, seed: 6 });
      motes(gg, t, { x0: 520, y0: 220, x1: 770, y1: 620 }, { n: 16, col: [255, 200, 140], a: 0.3, size: 1.2, seed: 23, drift: [2, -3] });
      F.amb = [0.9, 0.88, 0.96];
    },
  };
}
