// SET pass: Kleidion. Looking up the gorge toward the Bulgarian side: Samuel's great wall of stone and timber across the narrows,
// a gold afterglow beyond it, black cliffs either side, the mountain on the right with the path the flank march takes.
// Modes: day (build / attack / held) and night (the torch column crossing the mountain, coming down behind the wall, the rout).
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, igniteEnv, flick, fireFlick, tintAll, lightsOn, paintCliff, spline, nn } from './common.js';
import { paintSky, paintRange, pineTree, paintFog, paintTufts, paintRocks } from '../paint.js';
import { person, horse, banner, glowAt, torch, embers, hash1, PAL, STRIDE } from '../figs.js';
import { birds, smoke, motes, hazeBand, shaft, shaftAB, paintGrassStrip } from '../ambient.js';
import { floorLight, rubble, ruts, ledgeTrees, horizonGlow } from './light.js';

export const WALL = { x0: 140, x1: 584, top: 548, base: 704 };
const floorHalf = (y) => 215 + (y - 704) * 0.62;           // half width of the gorge floor at row y
const hgt = (y) => 1.75 * (9 + (y - 700) * 0.04);           // person height at row y of the floor
export const TRAIL = [[560, 318], [430, 352], [510, 398], [390, 438], [480, 486], [372, 520], [430, 566], [390, 596], [378, 612]].map(([x, y]) => ({ x, y }));

const W_ = WALL;
export default function pass(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, far: 2500, slope: 800, valley: 420, wall: 220, floor: 150, cliffL: 110, cliffR: 100, fg: 55 }; const planes = {};
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 711 });
    paintSky(C, { stops: [[-600, hex('#17163a')], [0, hex('#2a2a56')], [250, hex('#5a4a74')], [430, hex('#b07a78')], [540, hex('#e8a468')], [640, hex('#f6c277')]], glow: { x: 380, y: 560, rx: 520, ry: 120, col: hex('#ffd28a'), a: 0.75 },
      clouds: [{ y: 200, h: 14, x0: -300, x1: 1000, col: hex('#3a345e'), lit: hex('#c98a78'), litA: 0.7, sy: 0.03 }, { y: 360, h: 11, x0: -200, x1: 1000, col: hex('#6a4a70'), lit: hex('#f2b070'), litA: 0.85, thr: 0.5, sy: 0.036 }] });
    horizonGlow(C, { y: 548, x0: r[0], x1: r[2], h: 150, col: [255, 196, 128], a: 0.42, seed: 7 });
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.far); r[1] = Math.max(r[1], 150); r[3] = Math.min(r[3], 520); const C = new Canvas(r, { seed: 721 });
    paintRange(C, { ridge: (x) => 330 - bump(x, 330, 150, 130) - bump(x, 560, 110, 60) - bump(x, 120, 120, 60) - 24 * ridged(x * 0.007, 4, 3), top: hex('#8a6a7a'), mid: hex('#755a72'), base: hex('#5e4a68'), fall: 120, light: { dir: -1, col: hex('#c08a80'), amt: 0.4 }, shade: 0.12, haze: { col: hex('#c9906f'), y0: 300, y1: 420, a: 0.8 }, snow: { y: 240, col: hex('#d9b0a0'), amt: 0.6 } });
    C.mottle({ amt: 0.05 }); planes.far = S.plane('far', D.far, r, C.c); }
  { const r = cover(D.slope, 30); r[3] = Math.min(r[3], 720); const C = new Canvas(r, { seed: 731 }); const R = rng(7311);
    // the mountain that closes the far end of the gorge: dark face, pines, and the path the flank march takes across it
    const ridge = (x) => 330 - bump(x, 520, 140, 40) + bump(x, 150, 120, 20) + 14 * Math.sin(x * 0.011) + det(x, 14, 6, 2);
    paintRange(C, { ridge, top: hex('#3a2f4a'), mid: hex('#2a2238'), base: hex('#1d1729'), fall: 360, light: { dir: -1, col: hex('#5a4458'), amt: 0.4 }, shade: 0.14, rim: hex('#e0a078'), sizes: 1.1 });
    for (let i = 0; i < 120; i++) { const x = lerp(r[0], r[2], R()), y = lerp(340, 640, R()); if (y < ridge(x) + 8) continue; pineTree(C, x, y, 16 + R() * 28, hex('#171326'), { tierPx: 4, rim: hex('#8a5a60') }); }
    const tr = spline(TRAIL, 10); g_path(C, tr);
    C.mottle({ amt: 0.05 }); planes.slope = S.plane('slope', D.slope, r, C.c); planes.slope.userData.trail = tr; }
  { const r = cover(D.valley, 30); r[1] = Math.max(r[1], 540); r[3] = Math.min(r[3], 760); const C = new Canvas(r, { seed: 741 }); const R = rng(7411);
    paintRange(C, { ridge: (x) => 600 + 10 * Math.sin(x * 0.01) + det(x, 6, 3), top: hex('#3a2c3c'), mid: hex('#2a2030'), base: hex('#201826'), fall: 90, light: { dir: -1, col: hex('#7a5a60'), amt: 0.3 }, rim: hex('#d49a78') });
    for (let i = 0; i < 40; i++) { const x = lerp(r[0], r[2], R()); pineTree(C, x, 610 + R() * 40, 22 + R() * 26, hex('#181220'), { tierPx: 4, rim: hex('#a8705c') }); }
    C.mottle({ amt: 0.05 }); planes.valley = S.plane('valley', D.valley, r, C.c); }
  { const r = cover(D.wall, 30); r[1] = Math.max(r[1], 380); r[3] = Math.min(r[3], 780); const C = new Canvas(r, { seed: 751 }); const g = C.g; const R = rng(7511);
    const W = WALL; const stone = hex('#40343e'), timber = hex('#4e382c'), lit = hex('#d49a68'); const hFoot = 52;
    // earth bank and stone footing with courses
    g.fillStyle = rgba(hex('#2c2228')); g.beginPath(); g.moveTo(W.x0 - 30, W.base + 8); g.quadraticCurveTo(W.x0, W.base - hFoot - 6, W.x0 + 30, W.base - hFoot); g.lineTo(W.x1 - 30, W.base - hFoot); g.quadraticCurveTo(W.x1, W.base - hFoot - 6, W.x1 + 30, W.base + 8); g.closePath(); g.fill();
    g.fillStyle = rgba(stone); g.fillRect(W.x0, W.base - hFoot, W.x1 - W.x0, hFoot + 6);
    C.strokes({ n: (W.x1 - W.x0) * hFoot / 110, box: [W.x0, W.base - hFoot, W.x1, W.base + 4], color: () => mixc(stone, lit, 0.16 * R()), angle: () => (R() - 0.5) * 0.06, len: [8, 22], wid: [3, 6], alpha: [0.5, 0.85], jv: 0.1 });
    for (let y = W.base - hFoot + 12; y < W.base; y += 13) { g.strokeStyle = 'rgba(14,10,16,0.5)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(W.x0, y); g.lineTo(W.x1, y); g.stroke(); }
    // timber palisade: great logs side by side, uneven tops, cross-ties, a fighting platform behind
    for (let x = W.x0; x < W.x1; x += 8) { const top = W.top + (R() - 0.5) * 10 + 2 * Math.sin(x * 0.05); g.fillStyle = rgba(mul(timber, 0.75 + R() * 0.5)); g.beginPath(); g.moveTo(x, W.base - hFoot + 2); g.lineTo(x, top + 7); g.lineTo(x + 4, top - 2); g.lineTo(x + 8, top + 7); g.lineTo(x + 8, W.base - hFoot + 2); g.closePath(); g.fill(); g.fillStyle = rgba(lit, 0.3); g.fillRect(x, top + 5, 2, W.base - hFoot - top - 2); g.fillStyle = rgba([0, 0, 0], 0.25); g.fillRect(x + 6.4, top + 5, 1.6, W.base - hFoot - top - 2); }
    for (const yy of [W.top + 30, W.top + 62]) { g.fillStyle = rgba(hex('#2a1e22')); g.fillRect(W.x0, yy, W.x1 - W.x0, 5); }
    // square watchtowers with flat roofs and parapets (no pointed roofs)
    for (const tx of [W.x0 - 10, 349, W.x1 - 36]) { const tw = 54, th = 92; const ty = W.top - th + 28; g.fillStyle = rgba(mul(timber, 0.9)); g.fillRect(tx, ty, tw, W.base - hFoot - ty); for (let x = tx; x < tx + tw; x += 6) { g.fillStyle = rgba(lit, 0.18 * R()); g.fillRect(x, ty, 2, W.base - hFoot - ty); }
      g.fillStyle = rgba(hex('#2a1e22')); g.fillRect(tx - 7, ty - 8, tw + 14, 10); for (let x = tx - 7; x < tx + tw + 7; x += 13) g.fillRect(x, ty - 18, 8, 12); g.fillStyle = rgba(hex('#18101a')); g.fillRect(tx + 18, ty + 26, 18, 26); }
    // the gate: stone arch and dark doors, iron straps
    g.fillStyle = rgba(hex('#171018')); g.beginPath(); g.moveTo(322, W.base + 6); g.lineTo(322, W.base - 40); g.quadraticCurveTo(362, W.base - 72, 402, W.base - 40); g.lineTo(402, W.base + 6); g.closePath(); g.fill();
    g.strokeStyle = rgba(mixc(stone, lit, 0.3), 0.85); g.lineWidth = 3.5; g.beginPath(); g.moveTo(319, W.base + 6); g.lineTo(319, W.base - 40); g.quadraticCurveTo(362, W.base - 76, 405, W.base - 40); g.lineTo(405, W.base + 6); g.stroke();
    // rubble and stakes at the foot
    for (let i = 0; i < 90; i++) { const x = lerp(W.x0 - 30, W.x1 + 30, R()), y = W.base + 2 + R() * 10; const sz = 2 + R() * 5; C.dab(x, y, -0.2 + (R() - 0.5), sz * 2, sz, mul(stone, 0.6 + R() * 0.5), 0.9, 0.2); }
    C.mottle({ amt: 0.05 }); planes.wall = S.plane('wall', D.wall, r, C.c); }
  { const r = cover(D.floor, 40); r[1] = Math.max(r[1], 690); const C = new Canvas(r, { seed: 761 }); const R = rng(7611); const g = C.g;
    const path = new Path2D(); path.moveTo(360 - floorHalf(704), 704); path.lineTo(360 + floorHalf(704), 704); for (let y = 704; y <= r[3] + 30; y += 20) path.lineTo(360 + floorHalf(y), y); for (let y = r[3] + 30; y >= 704; y -= 20) path.lineTo(360 - floorHalf(y), y); path.closePath();
    const fc = (x, y) => mixc(mixc(hex('#53424a'), hex('#34282e'), smoothstep(704, 1100, y)), hex('#a07858'), 0.4 * smoothstep(780, 704, y) * Math.exp(-(((x - 360) / 200) ** 2)));
    underpaint(C, fc, path, 6); const m = C.mask((gg) => gg.fill(path));
    C.strokes({ n: C.area / 700, mask: m, color: fc, angle: () => (R() - 0.5) * 0.3, len: [14, 46], wid: [4, 10], alpha: [0.45, 0.8], jv: 0.08 });
    for (let i = 0; i < 260; i++) { const y = lerp(710, 1300, Math.pow(R(), 0.9)), x = 360 + (R() - 0.5) * 2 * floorHalf(y); const s = 2 + (y - 700) * 0.012 * (0.5 + R()); C.dab(x, y, (R() - 0.5) * 0.4, s * 2.2, s, mixc(hex('#3a2c34'), hex('#9a7a68'), R()), 0.7, 0.2); }
    paintTufts(C, { x0: 40, x1: 680, base: (x) => 712 + (R() - 0.5) * 4, step: 9, h0: 3, h1: 9, col: hex('#3a2c34'), blades: 3 });
    // light and shade: the low sun behind the wall throws wedges of gold down the floor between the cliffs' cast shadows; ruts lead to the gate; rubble casts shadows
    g.save(); g.clip(path); ruts(C, { gx: 362, yFar: 706, yNear: r[3], spread: (y) => 60 + (y - 704) * 0.4 });
    floorLight(C, { yFar: 704, yNear: r[3], cx: 360, n: 8, farSpread: 90, nearSpread: 560, col: [255, 196, 124], a: 0.26, shadeA: 0.34, half: floorHalf, seed: 14 });
    rubble(C, { x0: 360 - 260, x1: 360 + 260, y0: 720, y1: r[3] - 20, n: 70, seed: 15, base: hex('#4a3a44'), lit: hex('#e0a870'), size: (y) => 2 + (y - 700) * 0.022, mask: (x, y) => Math.abs(x - 360) < floorHalf(y) * 0.95 });
    g.restore();
    C.mottle({ amt: 0.06 }); planes.floor = S.plane('floor', D.floor, r, C.c); }
  // a wisp of dust hanging above the floor in the afterglow
  { const r0 = cover(D.floor + 25, 150); const r = [r0[0], 640, r0[2], 860]; const C = new Canvas(r, { seed: 799 });
    paintFog(C, { y: (x) => 730 + 10 * Math.sin(x * 0.005), h: 50, col: hex('#a07a70'), top: hex('#e2b684'), a: 0.75, density: 1.3, wisp: 0.85, blur: 3 }); planes.dust = S.plane('dust', D.floor + 25, r, C.c); planes.dust.userData.drift = 4; }
  { const r = cover(D.cliffL, 40); const C = new Canvas(r, { seed: 771 });
    const cliffLe = (y) => 132 - 170 * smoothstep(650, 1350, y) + 24 * smoothstep(520, -300, y) + det(y, 14, 6, 1);
    paintCliff(C, { edge: cliffLe, side: 'L', base: hex('#1a141f'), mid: hex('#2f2330'), rim: hex('#e0a070'), lit: hex('#5a4048') });
    ledgeTrees(C, { edge: cliffLe, side: 'L', y0: -200, y1: 1100, n: 46, seed: 31, col: hex('#150f1c'), rim: hex('#d89868'), h0: 24, h1: 90, inset: [4, 60] });
    C.mottle({ amt: 0.05 }); planes.cliffL = S.plane('cliffL', D.cliffL, r, C.c); }
  { const r = cover(D.cliffR, 40); const C = new Canvas(r, { seed: 781 });
    const cliffRe = (y) => 592 + 170 * smoothstep(650, 1350, y) - 24 * smoothstep(520, -300, y) + det(y, 14, 6, 2);
    paintCliff(C, { edge: cliffRe, side: 'R', base: hex('#161119'), mid: hex('#2a1f2c'), rim: hex('#d89868'), lit: hex('#4a3640') });
    ledgeTrees(C, { edge: cliffRe, side: 'R', y0: -200, y1: 1100, n: 46, seed: 32, col: hex('#130e1a'), rim: hex('#d89868'), h0: 24, h1: 90, inset: [4, 60] });
    C.mottle({ amt: 0.05 }); planes.cliffR = S.plane('cliffR', D.cliffR, r, C.c); }
  { const r = cover(D.fg, 50); r[1] = Math.max(r[1], 1000); const C = new Canvas(r, { seed: 791 });
    paintRocks(C, { rocks: [{ x: 10, y: 1290, rx: 200, ry: 120 }, { x: 720, y: 1300, rx: 220, ry: 130 }, { x: 380, y: 1370, rx: 240, ry: 80 }], col: hex('#0c0810'), lit: hex('#3a2c3a'), litA: 0.4, blur: 3 }); planes.fg = S.plane('fg', D.fg, r, C.c); }
  { const r = cover(D.fg, 50); planes.grass = paintGrassStrip(S, 'grass', D.fg - 1, [r[0], 1220, r[2], 1385], { seed: 97, col: hex('#0b0710'), lit: hex('#5a3c40'), h0: 26, h1: 66, step: 11, amp: 0.005, freq: 16 }); }
  tintAll(S, 1);
  function g_path(C, tr) { const g = C.g; g.strokeStyle = 'rgba(190,150,130,0.22)'; g.lineWidth = 2.2; g.lineCap = 'round'; g.beginPath(); tr.forEach((p, i) => i ? g.lineTo(p.x, p.y) : g.moveTo(p.x, p.y)); g.stroke(); }
  const trail = planes.slope.userData.trail;
  const PPM = (y) => 9 + (y - 700) * 0.04;      // floor-plane px per metre at row y (a person is 1.75 m tall: hgt = 1.75 * PPM)
  const onFloor = (F, x, y, o = {}) => { const hd = hgt(y) * (o.scale ?? 1); const q = F.P(D.floor, x, y), K = F.K(D.floor, x, y); return { q, h: hd * K, hd, K }; };
  const WORK = [hex('#3a2a2e'), hex('#33283a'), hex('#2e2a36'), hex('#3c3026'), hex('#2c2634')];
  // a man on the floor at plane (x, y): side view (face +-1), or from behind / in front (o.view); tiny ones are blobs
  function man(F, g, x, y, o = {}) {
    const a = onFloor(F, x, y, o); if (a.h < 2) return null; const face = o.face ?? 1;
    if (a.h < 7) { g.fillStyle = rgba(o.col || hex('#1c1424')); g.beginPath(); g.ellipse(a.q[0], a.q[1] - a.h * 0.42, a.h * 0.17, a.h * 0.42, 0, 0, 7); g.fill(); g.beginPath(); g.arc(a.q[0], a.q[1] - a.h * 0.92, a.h * 0.1, 0, 7); g.fill(); if (o.spear) { g.strokeStyle = rgba(PAL.staff); g.lineWidth = 1; g.beginPath(); g.moveTo(a.q[0] + a.h * 0.2, a.q[1]); g.lineTo(a.q[0] + a.h * 0.15, a.q[1] - a.h * 1.4); g.stroke(); } return a; }
    const r = person(g, { x: a.q[0], y: a.q[1], h: a.h, face, view: o.view, ph: o.ph ?? 0, walk: o.walk ?? 1, col: o.col || hex('#20162a'), col2: o.col2 || hex('#2e2238'), dark: o.dark || hex('#150e1c'), hood: o.hood ?? false, skinCol: hex('#150e1c'), helm: o.helm, plume: o.plume, shield: o.shield, spear: o.spear, staff: o.staff,
      head: o.head ?? -0.05, hem: o.hem ?? 0.28, stride: o.stride ?? 0.9, reach: o.reach, lantern: o.lantern, torch: o.torch, cape: o.cape, t: F.t });
    a.r = r; return a;
  }
  const work = (k, i) => { const c = WORK[(k + i) % 5]; return { col: c, col2: mixc(c, hex('#4a3a4a'), 0.4), dark: hex('#150e1c'), hood: k % 3 === 0, hem: 0.3 }; };
  function wheel(g, x, y, r, a) { g.save(); g.translate(x, y); g.strokeStyle = rgba(hex('#2a1c18')); g.lineWidth = Math.max(1.2, r * 0.16); g.beginPath(); g.arc(0, 0, r, 0, 7); g.stroke(); g.lineWidth = Math.max(0.8, r * 0.07); for (let k = 0; k < 6; k++) { const an = a + k * Math.PI / 3; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(an) * r, Math.sin(an) * r); g.stroke(); } g.restore(); }
  return {
    planes, D, trail, man, onFloor, hgt, floorHalf, PPM,

    dyn(F, { gg }) {
      const t = F.t, lt = F.lt, sh = F.shot, g = F.g, S_ = F.S; const mode = sh.mode; const arr = [];
      const draw = () => { arr.sort((a, b) => a.y - b.y); for (const o of arr) o.fn(); };
      if (mode === 'build') {
        // the working gorge: hauling teams, beam carriers, an ox cart, masons at the wall, all at a walking pace (metres per second, not screen speed)
        const teams = [{ y: 965, x0: 640, v: -0.9, n: 4, seed: 1 }, { y: 1100, x0: 60, v: 0.8, n: 4, seed: 2 }, { y: 845, x0: 650, v: -0.8, n: 3, seed: 3 }, { y: 1190, x0: 700, v: -0.7, n: 3, seed: 4 }];
        for (const tm of teams) { const pm = PPM(tm.y), sg = Math.sign(tm.v), dist = Math.abs(tm.v) * lt; const ph0 = dist / (STRIDE * 1.75 * 0.9);
          for (let k = 0; k < tm.n; k++) { const x = tm.x0 + tm.v * pm * lt - sg * k * 1.1 * pm; arr.push({ y: tm.y + k * 0.1, fn: () => man(F, g, x, tm.y, { face: sg, ph: ph0 + k * 0.27, walk: 0.8, ...work(tm.seed, k), head: 0.12, reach: [0.3, 0.62], stride: 0.8 }) }); }
          const sx = tm.x0 + tm.v * pm * lt - sg * (tm.n * 1.1 + 1.0) * pm; arr.push({ y: tm.y - 0.2, fn: () => { const a = onFloor(F, sx, tm.y); const lh = a.h * 0.16; g.fillStyle = 'rgba(6,4,12,0.4)'; g.beginPath(); g.ellipse(a.q[0], a.q[1] + 1, a.h * 0.7, a.h * 0.05, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#5a4030')); g.fillRect(a.q[0] - a.h * 0.6, a.q[1] - lh * 1.9, a.h * 1.2, lh * 1.1); g.fillStyle = rgba(hex('#8a6a4a'), 0.5); g.fillRect(a.q[0] - a.h * 0.6, a.q[1] - lh * 1.9, a.h * 1.2, lh * 0.2); g.fillStyle = rgba(hex('#2a1c18')); g.fillRect(a.q[0] - a.h * 0.7, a.q[1] - lh * 0.8, a.h * 1.4, lh * 0.25);
              const lead = onFloor(F, tm.x0 + tm.v * pm * lt - sg * (tm.n - 1) * 1.1 * pm, tm.y); g.strokeStyle = rgba(hex('#6a5a4a'), 0.8); g.lineWidth = Math.max(0.8, a.h * 0.012); g.beginPath(); g.moveTo(a.q[0] + sg * a.h * 0.6, a.q[1] - lh); g.lineTo(lead.q[0] - sg * lead.h * 0.1, lead.q[1] - lead.h * 0.6); g.stroke(); } }); }
        for (const [y, x0, v, sd] of [[1040, 140, 0.9, 5], [900, 580, -0.9, 6], [1235, 90, 0.8, 7]]) { const pm = PPM(y), sg = Math.sign(v), ph0 = Math.abs(v) * lt / (STRIDE * 1.75 * 0.9);
          const xa = x0 + v * pm * lt; for (let k = 0; k < 2; k++) arr.push({ y: y + k * 0.1, fn: () => man(F, g, xa - sg * k * 2.6 * pm, y, { face: sg, ph: ph0 + k * 0.5, walk: 0.85, ...work(sd, k), head: 0.08, reach: [0.12, 0.84], stride: 0.8 }) });
          arr.push({ y: y + 0.5, fn: () => { const a = onFloor(F, xa, y), b = onFloor(F, xa - sg * 2.6 * pm, y); g.strokeStyle = rgba(hex('#5a4030')); g.lineWidth = Math.max(2, a.h * 0.07); g.lineCap = 'round'; g.beginPath(); g.moveTo(a.q[0] - sg * a.h * 0.15, a.q[1] - a.h * 0.88); g.lineTo(b.q[0] + sg * b.h * 0.15, b.q[1] - b.h * 0.88); g.stroke(); } }); }
        { const y = 880, pm = PPM(y), v = 0.7, x = 80 + v * pm * lt; arr.push({ y, fn: () => { const a = onFloor(F, x, y); const hh = a.h * 0.72; const hs = horse(g, { x: a.q[0] + a.h * 0.7, y: a.q[1], h: hh, face: 1, ph: v * lt / (1.45 * 1.3), gallop: 0, col: hex('#241a28'), t }); const cx = a.q[0] - a.h * 0.5, cb = a.q[1] - a.h * 0.4;
            g.fillStyle = 'rgba(6,4,12,0.4)'; g.beginPath(); g.ellipse(cx, a.q[1] + 1, a.h * 0.9, a.h * 0.05, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#4a3426')); g.beginPath(); g.moveTo(cx - a.h * 0.85, cb - a.h * 0.42); g.lineTo(cx + a.h * 0.75, cb - a.h * 0.42); g.lineTo(cx + a.h * 0.62, cb - a.h * 0.02); g.lineTo(cx - a.h * 0.72, cb - a.h * 0.02); g.closePath(); g.fill();
            g.fillStyle = rgba(hex('#8a8a96'), 0.9); for (let k = 0; k < 4; k++) { g.beginPath(); g.ellipse(cx - a.h * 0.55 + k * a.h * 0.38, cb - a.h * 0.5, a.h * 0.17, a.h * 0.1, 0.1 * k, 0, 7); g.fill(); }
            wheel(g, cx - a.h * 0.35, a.q[1] - a.h * 0.2, a.h * 0.2, (v * lt) / 0.4); wheel(g, cx + a.h * 0.4, a.q[1] - a.h * 0.2, a.h * 0.2, (v * lt) / 0.4);
            g.strokeStyle = rgba(hex('#3a2a20')); g.lineWidth = Math.max(1.5, a.h * 0.03); g.beginPath(); g.moveTo(cx + a.h * 0.7, cb - a.h * 0.2); g.lineTo(a.q[0] + a.h * 0.55, a.q[1] - a.h * 0.55); g.stroke(); } }); }
        // masons at the foot of the wall: they hammer and chisel
        for (const [x, y] of [[215, 742], [300, 738], [430, 744], [520, 740]]) arr.push({ y, fn: () => { const sg = x < 360 ? 1 : -1; const hm = 0.5 + 0.5 * Math.sin(t * 4.5 + x); const a = man(F, g, x, y, { face: sg, walk: 0, ...work(x, 1), head: 0.18, reach: [0.3, 0.55 + 0.35 * hm], stride: 0.8 }); if (a && a.r) { g.strokeStyle = rgba(PAL.staff); g.lineWidth = Math.max(1, a.h * 0.03); g.beginPath(); g.moveTo(a.r.hand[0], a.r.hand[1]); g.lineTo(a.r.hand[0] + sg * a.h * 0.2, a.r.hand[1] - a.h * 0.22); g.stroke(); } } });
        // foreground: a brazier with two men warming their hands at the dusk (depth and a warm key)
        { const bx = 590, by = 1262; const a = onFloor(F, bx, by); const fl = fireFlick(t, 4); const hf = a.h * 0.5 * (0.9 + 0.2 * fl); const bp = a.q; arr.push({ y: by + 5, fn: () => { g.fillStyle = 'rgba(6,4,12,0.45)'; g.beginPath(); g.ellipse(bp[0], bp[1] + 3, a.h * 0.45, a.h * 0.05, 0, 0, 7); g.fill(); g.strokeStyle = rgba(hex('#1c1416')); g.lineWidth = Math.max(1.4, a.h * 0.02); g.beginPath(); g.moveTo(bp[0] - a.h * 0.2, bp[1]); g.lineTo(bp[0] - a.h * 0.07, bp[1] - a.h * 0.3); g.moveTo(bp[0] + a.h * 0.2, bp[1]); g.lineTo(bp[0] + a.h * 0.07, bp[1] - a.h * 0.3); g.stroke(); g.fillStyle = rgba(hex('#1c1416')); g.beginPath(); g.ellipse(bp[0], bp[1] - a.h * 0.32, a.h * 0.16, a.h * 0.05, 0, 0, 7); g.fill();
              g.fillStyle = rgba([255, 150, 60], 0.9); g.beginPath(); g.moveTo(bp[0] - a.h * 0.1, bp[1] - a.h * 0.33); g.quadraticCurveTo(bp[0] - a.h * 0.08, bp[1] - a.h * 0.33 - hf * 0.6, bp[0] + 3 * Math.sin(t * 7), bp[1] - a.h * 0.33 - hf); g.quadraticCurveTo(bp[0] + a.h * 0.1, bp[1] - a.h * 0.33 - hf * 0.5, bp[0] + a.h * 0.1, bp[1] - a.h * 0.33); g.fill(); g.fillStyle = rgba([255, 230, 160], 0.95); g.beginPath(); g.ellipse(bp[0], bp[1] - a.h * 0.42, a.h * 0.045, a.h * 0.11 * fl, 0, 0, 7); g.fill(); } });
          for (const [dx, sg] of [[-0.6, 1], [0.62, -1]]) arr.push({ y: by + 6, fn: () => man(F, g, bx + dx * a.h / PPM(by) * 0.0 + (dx * 36), by + 2, { face: sg, walk: 0, ...work(9, dx > 0 ? 1 : 2), head: 0.05, reach: [0.3, 0.55], hood: true }) });
          glowAt(gg, bp[0], bp[1] - a.h * 0.4, a.h * 1.3, 0.55 * fl, [255, 150, 70]); glowAt(gg, bp[0], bp[1] - a.h * 0.4, a.h * 4.2, 0.18 * fl, [255, 130, 60]); if (F.lights.length < 8) F.lights.push({ x: bp[0], y: bp[1] - a.h * 0.4, r: a.h * 3.5, c: WARM, k: 0.9 * fl }); }
        draw();
      } else if (mode === 'attack') {
        // a shield wall advances at a jog (2 m/s), halts under the volleys, then falls back; three waves, each a block of men seen from behind, then from the front as they retreat
        for (const w of sh.waves || []) { const u = t - w.t0; if (u < 0) continue; const N = w.n || 36, cols = 12, rows = Math.ceil(N / cols); const run = w.run, hold = w.hold, back = w.back; const cx = 360 + (hash1(w.seed * 7) - 0.5) * 200; const a0 = PPM(w.yStart ?? (w.yStop + 150)); const v = 2.0;
          const aOf = (uu) => { if (uu < run) return a0 * Math.exp(-0.012 * v * uu); const aS = a0 * Math.exp(-0.012 * v * run); if (uu < run + hold) return aS; return aS * Math.exp(0.012 * 1.8 * (uu - run - hold)); };
          const advancing = u < run + hold * 0.9; const dist = u < run ? v * u : u < run + hold ? v * run : v * run + 1.8 * (u - run - hold);
          for (let k = 0; k < N; k++) { const col = k % cols, row = Math.floor(k / cols); const aa = aOf(u) * (1 + row * 0.085); const y = 700 + (aa - 9) / 0.04; if (y > 1360) continue; const x = cx + (col - (cols - 1) / 2) * 1.05 * PPM(y) + (hash1(k * 3.3 + w.seed) - 0.5) * 0.35 * PPM(y); const bearer = k === 5 || k === 18; const walking = u < run || u > run + hold; const ph = dist / (STRIDE * 1.75 * 0.9) + hash1(k * 1.7) * 0.5;
            arr.push({ y, fn: () => { const a = man(F, g, x, y, { view: advancing ? 'back' : 'front', ph, walk: walking ? 0.85 : 0.12, spear: !bearer, shield: !bearer ? PAL.purple : null, helm: true, plume: k % 5 === 0 ? [118, 38, 56] : null, col: hex('#2a1a38'), col2: hex('#3a2848'), hem: 0.3 }); if (bearer && a) banner(g, { x: a.q[0] + a.h * 0.18, y: a.q[1] - a.h * 0.1, h: a.h * 2.6, w: a.h * 1.0, t, dir: -1, seed: k, amp: 0.13 }); } }); } }
        draw();
      } else if (mode === 'column') {
        // the general's torches cross the mountain: a long column strung along the path, creeping at a walking pace; its head reaches the ridge above the wall and goes over
        const tr = trail; const total = tr[tr.length - 1].s; const lt0 = t - sh.t0; const sHead = total * 0.97 + lt0 * 4.6; const N = 42, gap = 17;
        for (let k = 0; k < N; k++) { const s = sHead - k * gap; if (s < 0 || s > total) continue; const p = tr.at(s / total); const q = F.P(D.slope, p.x, p.y); const K = F.K(D.slope, p.x, p.y); const fk = fireFlick(t, k);
          g.fillStyle = rgba(hex('#0c0814')); g.beginPath(); g.ellipse(q[0], q[1] - 3 * K, 1.4 * K + 0.5, 3.4 * K + 0.8, 0, 0, 7); g.fill();
          glowAt(gg, q[0], q[1] - 5 * K, 6 * K + 3, 0.8 * fk, [255, 175, 85]); glowAt(gg, q[0], q[1] - 5 * K, 18 * K + 5, 0.16 * fk, [255, 140, 70]); if (k % 5 === 0 && F.lights.length < 6) F.lights.push({ x: q[0], y: q[1], r: 50 * K, c: WARM, k: 0.6 }); }
        const behind = clamp((lt0 - 3.2) / 3.0); if (behind > 0) { const p = F.P(D.valley, 380, 640); glowAt(gg, p[0], p[1], 260 * F.K(D.valley), 0.5 * behind, [255, 150, 70]); }
      } else if (mode === 'rout') {
        // the rout: flares behind the wall, smoke and sparks, the defenders run for the ends of the wall; then the captives are led out across the floor
        const W = W_; const hitsAll = sh.hits || [];
        for (const h0 of hitsAll) { const u = t - h0; if (u < 0 || u > 3.6) continue; const a = Math.exp(-u * 0.7) * smoothstep(0, 0.1, u); const x = lerp(W.x0 + 40, W.x1 - 40, hash1(h0 * 5.1)); const p = F.P(D.wall, x, W.top + 20); const kw = F.K(D.wall);
          glowAt(gg, p[0], p[1], 150 * kw * (0.8 + u * 0.3), 0.7 * a, [255, 120, 50]); if (F.lights.length < 7) F.lights.push({ x: p[0], y: p[1], r: 200 * kw, c: WARM, k: 1.2 * a });
          for (let k = 0; k < 4; k++) { const f = torch(g, p[0] + (k - 1.5) * 14 * kw, F.P(D.wall, x, W.top + 36)[1], 22 * kw * (0.8 + 0.4 * hash1(h0 + k)) * a, t, k + h0, a); glowAt(gg, f[0], f[1], 30 * kw, 0.5 * a * fireFlick(t, k), [255, 160, 80]); }
          smoke(g, t - h0 * 0.0, p[0], p[1] - 20 * kw, { n: 8, rise: 150 * kw, wind: -18 * kw, r0: 6 * kw, r1: 26 * kw, a: 0.34 * Math.min(1, u * 1.2), col: [58, 46, 62], life: 4, seed: Math.round(h0) }); }
        embers(gg, t, { x0: 100, y0: 380, x1: 620, y1: 640 }, 44, { size: 1.8, col: [255, 170, 80], a: 0.8, wind: -20, rise: 1.3, seed: 5 });
        const rt = smoothstep(sh.rout, sh.rout + 0.5, t); const Kw = F.K(D.wall, 360, 650);
        for (let k = 0; k < 16; k++) { const x0 = W.x0 + 24 + (W.x1 - W.x0 - 48) * ((k + 0.5) / 16); const d = x0 < 360 ? -1 : 1; const delay = hash1(k * 2.1) * 1.4; const ur = Math.max(0, t - sh.rout - delay); const x = x0 + d * Math.min(ur, 4) * 3.0 * 17 * (0.7 + 0.6 * hash1(k)); if (x < W.x0 - 6 || x > W.x1 + 6) continue; const p = F.P(D.wall, x, W.top + 40); const hh = 31 * Kw; const ph = ur * 2.4 + k * 0.3;
          arr.push({ y: p[1], fn: () => { if (ur > 0) person(g, { x: p[0], y: p[1], h: hh, face: d, ph, walk: 1, col: hex('#1e1626'), col2: hex('#2e2238'), dark: hex('#150e1c'), hood: false, skinCol: hex('#150e1c'), helm: hh > 16, hem: 0.3, stride: 1.2, head: 0.1, t });
              else person(g, { x: p[0], y: p[1], h: hh, view: 'front', walk: 0.02, ph: k * 0.37, col: hex('#1e1626'), col2: hex('#2e2238'), dark: hex('#150e1c'), hood: false, skinCol: hex('#150e1c'), helm: hh > 16, spear: k % 3 === 1, hem: 0.3, t }); } }); }
        // the captives: a file led across the floor from the left, guards with torches
        if (sh.captivesFrom != null) { const u = t - sh.captivesFrom; if (u > -1) { const y = 1010, pm = PPM(y); const x0 = 80 + 1.0 * pm * u; const n = 11; const ph0 = u / (STRIDE * 1.75 * 0.85);
            for (let k = 0; k < n; k++) arr.push({ y: y + k * 0.05, fn: () => { const x = x0 - k * 0.95 * pm; man(F, g, x, y, { face: 1, ph: ph0 + k * 0.31, walk: 0.8, col: mixc(hex('#241a2c'), hex('#2e2238'), hash1(k)), hood: false, head: 0.24, reach: k ? [0.34, 0.8] : null, hem: 0.3, stride: 0.85 }); } });
            for (const [gk, off] of [[0, 1.6], [n - 1, -1.6]]) arr.push({ y: y + 1, fn: () => { const x = x0 - gk * 0.95 * pm + off * pm * 1.2; const a = man(F, g, x, y + 6, { face: 1, ph: ph0 + gk * 0.31 + 0.2, walk: 0.9, helm: true, torch: null, col: hex('#2a1a38'), col2: hex('#3a2848'), reach: [0.2, 0.9], stride: 0.9 }); if (a && a.r) { const f = torch(g, a.r.hand[0] + a.h * 0.02, a.r.hand[1] - a.h * 0.08, a.h * 0.17, t, gk + 30, 1); glowAt(gg, f[0], f[1], a.h * 1.4, 0.55 * fireFlick(t, gk), [255, 170, 90]); if (F.lights.length < 8) F.lights.push({ x: f[0], y: f[1], r: a.h * 1.8, c: WARM, k: 0.5 }); } } }); } }
        draw();
      }
      if (sh.embers) embers(gg, t, { x0: 0, y0: 300, x1: 720, y1: 1100 }, 30, { size: 1.3, col: [255, 200, 130], a: 0.5, wind: 14, rise: 0.4, seed: 8 });
    },
    update(F) {
      const t = F.t, lt = F.lt, sh = F.shot, g = F.g, S_ = F.S; const night = typeof sh.night === 'function' ? sh.night(t) : (sh.night ?? 0); const day = 1 - 0.72 * night; const W = WALL;
      tintAll(S_, day, [1 - 0.5 * night * 0.7, 1 - 0.25 * night * 0.5, 1 + 0.08 * night]);
      const gg = F.glow(); const hits = sh.hits || [];
      const Pw = (x, y) => F.P(D.wall, x, y), Kw = F.K(D.wall, 360, 650);
      // the afterglow at the gorge end, shafts through the dust, birds over the gap, smoke from the camp behind the wall
      const sunp = F.P(D.sky, 380, 540); glowAt(gg, sunp[0], sunp[1], 380 * Math.max(1, F.K(D.sky)), 0.1 * (1 - night), [255, 190, 110]);
      { const bp = Pw(362, W.base + 6); const kk = F.K(D.wall, 362, W.base); glowAt(gg, bp[0], bp[1], 330 * kk, 0.07 * (1 - night), [230, 170, 110]); }
      if (night < 0.5) { const a = F.P(D.wall, 370, W.top - 50); for (const [x, w1, al, sd] of [[250, 140, 0.12, 1], [380, 210, 0.15, 2], [500, 150, 0.1, 3]]) shaftAB(gg, t, a, F.P(D.floor, x, 1180), 30, w1 * F.K(D.floor), al * (1 - night), [255, 200, 130], sd);
        motes(gg, t, { x0: 60, y0: 600, x1: 660, y1: 1200 }, { n: 30, col: [255, 214, 150], a: 0.4, size: 1.2, seed: 6, drift: [4, -2] });
        for (const [x, sd] of [[210, 1], [345, 2], [525, 3]]) { const p = Pw(x, W.top - 10); smoke(g, t, p[0], p[1], { n: 8, rise: 110 * Kw, wind: 10 * Kw, r0: 3 * Kw, r1: 13 * Kw, a: 0.26, life: 8, seed: sd, col: [190, 150, 130] }); }
        birds(g, t, { x0: 120, x1: 620, y0: 190, y1: 330, n: 6, seed: 5, size: 6, speed: 20, dir: 1, hz: 2.0, col: [40, 26, 44], a: 0.8 }); }
      // defenders on the wall: they stand along the walkway (spears up, one leaning on the parapet, one shifting his weight)
      const rout = sh.rout ? smoothstep(sh.rout, sh.rout + 0.6, t) : 0; const items = [];
      if (sh.defenders !== false && !(sh.mode === 'rout')) { const R = rng(91); for (let k = 0; k < 18; k++) { const x = W.x0 + 20 + (W.x1 - W.x0 - 40) * ((k + 0.5) / 18) + (R() - 0.5) * 8; const p = Pw(x, W.top + 40); const hh = 31 * Kw;
          person(g, { x: p[0], y: p[1], h: hh, view: 'front', walk: 0.02, ph: k * 0.37, col: hex('#1e1626'), col2: hex('#2e2238'), dark: hex('#150e1c'), hood: false, skinCol: hex('#150e1c'), helm: hh > 16, spear: k % 3 === 1, hem: 0.3, t }); } }
      // wall banners (Bulgarian: dark red, a pale disc)
      if (sh.banners !== false) for (const [bx, by, h, dir, seed] of [[W.x0 + 16, W.top - 70, 70, 1, 3], [376, W.top - 70, 84, 1, 5], [W.x1 - 22, W.top - 70, 70, -1, 7]]) { const p = Pw(bx, by); banner(g, { x: p[0], y: p[1], h: h * Kw * 1.3, w: 46 * Kw, t, dir, col: PAL.red, colLit: PAL.redLit, trim: hex('#d8b868'), emblem: 'none', seed, amp: 0.1 * (1 + 2 * rout) }); }
      // torches and braziers on the wall: lit at night, and flickering at dusk
      const torchOn = night > 0.3 ? 1 : 0.55; for (let k = 0; k < 7; k++) { const x = W.x0 + 40 + k * 62; const p = Pw(x, W.top + 34); const s = 14 * Kw; const f = torch(g, p[0], p[1], s, t, k, torchOn); glowAt(gg, f[0], f[1], 70 * Kw, 0.5 * torchOn * fireFlick(t, k)); }
      // dust puffs and arrow volleys on the beats
      for (const h0 of hits) { const u = (t - h0); if (u < 0 || u > 2.2) continue; if (sh.mode === 'rout') continue; const a = Math.exp(-u * 1.3) * smoothstep(0, 0.08, u);
        for (let k = 0; k < 4; k++) { const x = lerp(W.x0 + 40, W.x1 - 40, hash1(h0 * 7 + k)); const p = Pw(x + u * 10 * (k - 1.5), W.base - 6 - u * 34); glowAt(gg, p[0], p[1], (46 + u * 70) * Kw, 0.30 * a, [255, 190, 110]); }
        if (u < 0.7) { for (let k = 0; k < 14; k++) { const x0 = lerp(120, 600, hash1(h0 * 3 + k)); const s = u / 0.7; const a0 = F.P(D.floor, x0, 1000), a1 = F.P(D.wall, lerp(W.x0 + 30, W.x1 - 30, hash1(h0 + k * 1.7)), W.top + 30); const px_ = lerp(a0[0], a1[0], s), py_ = lerp(a0[1], a1[1], s) - 140 * Math.sin(Math.PI * s); const pxb = lerp(a0[0], a1[0], s - 0.06), pyb = lerp(a0[1], a1[1], s - 0.06) - 140 * Math.sin(Math.PI * Math.max(0, s - 0.06));
            gg.strokeStyle = `rgba(255,230,180,${0.55 * (1 - s * 0.4)})`; gg.lineWidth = 1.3; gg.beginPath(); gg.moveTo(pxb, pyb); gg.lineTo(px_, py_); gg.stroke(); } } }
      this.dyn(F, { gg, items, day, night, rout });
      F.amb = [0.9 * day + 0.1, 0.88 * day + 0.1, 0.95 * day + 0.1]; F.bloom = 0.5;
    },
  };
}
