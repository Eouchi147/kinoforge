// SET march: medium shots of a group walking home at dusk: hooded lantern leader, followers with a hand on the shoulder ahead.
// The camera tracks beside them (lateral dolly); the ground plane slides at exactly the speed the planted feet need.
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, igniteEnv, flick, tintAll, lightsOn } from './common.js';
import { paintSky, paintRange, paintPineRidge, pineTree, paintFog, paintRocks, paintTufts } from '../paint.js';
import { person, glowAt, hash1, PAL } from '../figs.js';

export default function march(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, peaks: 2400, mid: 900, fog: 300, pines: 150, slope: 60, ground: 9, fg: 4 }; const planes = {};
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 411 });
    paintSky(C, { stops: [[-500, hex('#0b0e30')], [0, hex('#141944')], [250, hex('#262c5d')], [420, hex('#444580')], [540, hex('#6a5f90')], [640, hex('#8f7a9c')]], glow: { x: 40, y: 640, rx: 800, ry: 320, col: hex('#e0a58e'), a: 0.7 },
      clouds: [{ y: 150, h: 13, x0: -300, x1: 1000, col: hex('#1f2454'), lit: hex('#5d5789'), litA: 0.6, sy: 0.03 }, { y: 330, h: 11, x0: -200, x1: 1100, col: hex('#2e3366'), lit: hex('#8f7c9f'), litA: 0.7, thr: 0.5, sy: 0.034 }, { y: 480, h: 9, x0: 100, x1: 1100, col: hex('#3a3d72'), lit: hex('#a18aa6'), litA: 0.7, thr: 0.5, sy: 0.04 }] });
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.peaks); r[3] = Math.min(r[3], 800); const C = new Canvas(r, { seed: 421 });
    const ridge = (x) => 640 - bump(x, 120, 190, 250) - bump(x, 420, 140, 190) - bump(x, 650, 120, 130) - 30 * ridged(x * 0.0065, 4, 1) - 9 * ridged(x * 0.03, 3, 2);
    paintRange(C, { ridge, top: hex('#323866'), mid: hex('#383d6c'), base: hex('#474a79'), fall: 190, light: { dir: -1, col: hex('#5a5f93'), amt: 0.45 }, shade: 0.18, haze: { col: hex('#4f4d7e'), y0: 560, y1: 700, a: 0.5 }, snow: { y: 470, col: hex('#8a8bb6'), amt: 0.85 }, rim: hex('#9c8fb0') });
    C.mottle({ amt: 0.05 }); planes.peaks = S.plane('peaks', D.peaks, r, C.c); }
  { const r = cover(D.mid); r[1] = Math.max(r[1], 480); r[3] = Math.min(r[3], 860); const C = new Canvas(r, { seed: 431 });
    const ridge = (x) => 690 - bump(x, 560, 200, 60) - bump(x, 60, 150, 40) - 14 * ridged(x * 0.01, 3, 3);
    paintRange(C, { ridge, top: hex('#262a55'), mid: hex('#2e325f'), base: hex('#45477a'), fall: 120, light: { dir: -1, col: hex('#3e4377'), amt: 0.4 }, shade: 0.12, haze: { col: hex('#5a5788'), y0: 720, y1: 820, a: 0.8 }, rim: hex('#5a5f92'), sizes: 0.9 });
    C.mottle({ amt: 0.05 }); planes.mid = S.plane('mid', D.mid, r, C.c); }
  { const r0 = cover(D.fog, 90); const r = [r0[0], 640, r0[2], 880]; const C = new Canvas(r, { seed: 451 });
    paintFog(C, { y: (x) => 770 + 10 * Math.sin(x * 0.004), h: 44, col: hex('#5d5a88'), top: hex('#7b77a3'), a: 0.95, density: 1.5, wisp: 0.8, blur: 3 }); planes.fog = S.plane('fog', D.fog, r, C.c); planes.fog.userData.drift = 4; }
  { const r = cover(D.pines); r[1] = Math.max(r[1], 640); r[3] = Math.min(r[3], 960); const C = new Canvas(r, { seed: 461 });
    paintPineRidge(C, { base: (x) => 820 + 14 * Math.sin(x * 0.01) + det(x, 8, 3), hMin: 60, hMax: 150, spacing: 26, col: hex('#12152a'), ground: hex('#14172f'), groundLit: hex('#1c2040'), rim: hex('#2f3660'), gaps: [[120, 560]], gapKeep: 0.12, tierPx: 8 });
    C.mottle({ amt: 0.05 }); planes.pines = S.plane('pines', D.pines, r, C.c); }
  { const r = cover(D.slope); r[1] = Math.max(r[1], 760); r[3] = Math.min(r[3], 1160); const C = new Canvas(r, { seed: 471 });
    paintRange(C, { ridge: (x) => 900 + 20 * Math.sin(x * 0.006) + det(x, 12, 4, 5), top: hex('#1d2146'), mid: hex('#171a38'), base: hex('#101228'), fall: 220, light: { dir: -1, col: hex('#2d3262'), amt: 0.3 }, shade: 0.1, rim: hex('#3d4378'), sizes: 1.0 });
    C.mottle({ amt: 0.05 }); planes.slope = S.plane('slope', D.slope, r, C.c); }
  { const r = cover(D.ground, 120); r[1] = Math.max(r[1], 930); const C = new Canvas(r, { seed: 481 }); const R = rng(4811);
    const top = (x) => 984 + 6 * Math.sin(x * 0.01) + det(x, 5, 3, 14); const path = new Path2D(); path.moveTo(r[0] - 20, r[3] + 20); for (let x = r[0] - 20; x <= r[2] + 20; x += 4) path.lineTo(x, top(x)); path.lineTo(r[2] + 20, r[3] + 20); path.closePath();
    const onPath = (x, y) => 1 - smoothstep(0.3, 0.9, (y - 1020) / 200) * 0.0 - (y < 1010 ? 0.6 : 0);
    const gc = (x, y) => mixc(mixc(hex('#2a2940'), hex('#3b3853'), smoothstep(990, 1100, y)), mixc(hex('#1b1b31'), hex('#13142a'), smoothstep(1100, 1300, y)), smoothstep(1090, 1260, y));
    underpaint(C, gc, path, 6); const m = C.mask((q) => q.fill(path));
    C.strokes({ n: C.area / 700, mask: m, color: gc, angle: () => 0.02 + (C.R() - 0.5) * 0.25, len: [16, 54], wid: [5, 11], alpha: [0.5, 0.85], jv: 0.06 });
    for (let i = 0; i < 360; i++) { const x = lerp(r[0], r[2], C.R()), y = lerp(992, 1240, Math.sqrt(C.R())); const s = lerp(2, 6, smoothstep(990, 1240, y)); C.dab(x, y, (C.R() - 0.5) * 0.4, s * 1.8, s, C.R() < 0.55 ? hex('#2e2b44') : hex('#58536f'), 0.5, 0.15); }
    for (const yy of [1068, 1150]) for (let x = r[0]; x < r[2]; x += 9 + C.R() * 30) C.dab(x, yy + Math.sin(x * 0.03) * 3 + C.R() * 4, 0, 20 + C.R() * 40, 2 + C.R() * 2, hex('#201f35'), 0.3, 0.02);
    paintTufts(C, { x0: r[0], x1: r[2], base: (x) => top(x) + 3, step: 11, h0: 8, h1: 22, col: hex('#14162c'), blades: 5 });
    paintTufts(C, { x0: r[0], x1: r[2], base: (x) => 1262 + 10 * Math.sin(x * 0.02), step: 24, h0: 14, h1: 34, col: hex('#0e1022'), blades: 6, jitter: 8 });
    if (new URLSearchParams(location.search).get('prof')) console.log('ground rect ' + r); C.mottle({ amt: 0.06 }); planes.ground = S.plane('ground', D.ground, r, C.c); }
  tintAll(S, 1);
  return {
    planes,
    update(F) {
      const t = F.t, lt = F.lt, sh = F.shot, g = F.g, K = F.K(D.ground);
      planes.fog.position.x = planes.fog.userData.base.x - planes.fog.userData.drift * t * planes.fog.userData.D / S.f;
      const dark = sh.dark ?? 0.8; tintAll(S, dark, [0.97, 0.98, 1.06]);
      const h = sh.h || 430, T = sh.T || 1.3, n = sh.n || 6, gapK = 0.31; const footY = sh.footY || 1030; const lx0 = sh.lead ?? 480;
      const lit = igniteEnv(t, sh.lampOn ?? -1, 3) || 0 + 0; const on = sh.lampOn == null ? 1 : lit;
      // people on screen: fixed place (the camera walks with them), gait phase from time
      const items = []; for (let k = n - 1; k >= 0; k--) { const lead = k === 0; items.push(k); }
      const lights = [];
      const bobs = []; let leadA = null; const lampS = sh.lampXY || null;
      const warm0 = { x: lx0 + 0.19 * h * 0.9 + 0.1 * h, y: footY - 0.58 * h, r: 0.62 * h, a: 0.16 * clamp(on, 0, 1) };
      g.save(); g.filter = 'blur(10px)'; g.fillStyle = 'rgba(4,4,12,0.55)'; g.beginPath(); g.ellipse(lx0 - (n - 1) * gapK * h * 0.5 + 0.1 * h, footY + 6, (n * gapK + 0.3) * h * 0.5, 0.05 * h, 0, 0, 7); g.fill(); g.restore();
      for (let k = n - 1; k >= 0; k--) {
        const lead = k === 0; const x = lx0 - k * gapK * h; const y = footY + (k % 2 ? 3 : 0) * 0 + k * 0; const hh = h * (1 - 0.012 * (k % 3));
        const a = person(g, { x, y: y, h: hh, face: 1, ph: t / T + k * 0.29, walk: 0.9, stride: 0.8, col: lead ? PAL.cloak : mixc(PAL.cloak, PAL.cloak2, 0.5 + 0.3 * hash1(k)), col2: PAL.cloak2, head: lead ? -0.02 : 0.1 + 0.03 * Math.sin(t * 0.9 + k), staff: lead, lantern: lead ? { on: clamp(on, 0, 1) } : null,
          reach: lead ? null : [gapK + 0.03, 0.8], hem: 0.2 + 0.015 * (k % 3), warm: on > 0.01 && !F.q.nowarm ? { ...warm0, a: warm0.a * Math.max(0, 1 - k * 0.45) } : null });
        if (lead) leadA = a;
      }
      if (leadA && leadA.lantern && on > 0.01) { const [lx, ly] = leadA.lantern; const gl = F.glow(); glowAt(gl, lx, ly, 70, 0.9 * on); glowAt(gl, lx, ly, 380, 0.3 * on, [255, 140, 70]);
        F.lights.push({ x: lx, y: ly, r: 330, c: WARM, k: 0.8 * on }); const w = F.W(D.ground, lx, ly + 220); const ws = F.W(D.slope, lx, ly);
        lightsOn(planes.ground, [{ p: w, r: 1.9 * D.ground / 9, c: WARM, k: 3.6 * on }]); lightsOn(planes.slope, [{ p: ws, r: 7, c: WARM, k: 1.4 * on }]); }
      F.amb = [0.9 * dark + 0.1, 0.9 * dark + 0.1, dark + 0.1];
    },
  };
}
