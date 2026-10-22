// SET pass: Kleidion. Looking up the gorge toward the Bulgarian side: Samuel's great wall of stone and timber across the narrows,
// a gold afterglow beyond it, black cliffs either side, the mountain on the right with the path the flank march takes.
// Modes: day (build / attack / held) and night (the torch column crossing the mountain, coming down behind the wall, the rout).
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, igniteEnv, flick, fireFlick, tintAll, lightsOn, paintCliff, spline, nn } from './common.js';
import { paintSky, paintRange, pineTree, paintFog, paintTufts, paintRocks } from '../paint.js';
import { person, banner, glowAt, torch, embers, hash1, PAL, STRIDE } from '../figs.js';

export const WALL = { x0: 140, x1: 584, top: 548, base: 704 };
const floorHalf = (y) => 215 + (y - 704) * 0.62;           // half width of the gorge floor at row y
const hgt = (y) => 1.75 * (9 + (y - 700) * 0.04);           // person height at row y of the floor
export const TRAIL = [[560, 318], [430, 352], [510, 398], [390, 438], [480, 486], [372, 520], [430, 566], [390, 596], [378, 612]].map(([x, y]) => ({ x, y }));

const W_ = WALL;
export default function pass(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, far: 2500, slope: 800, valley: 420, wall: 220, floor: 150, cliffL: 110, cliffR: 100, fg: 55 }; const planes = {};
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 711 });
    paintSky(C, { stops: [[-600, hex('#17163a')], [0, hex('#2a2a56')], [250, hex('#5a4a74')], [430, hex('#b07a78')], [540, hex('#e8a468')], [640, hex('#f6c277')]], glow: { x: 380, y: 520, rx: 420, ry: 260, col: hex('#ffd28a'), a: 0.9 },
      clouds: [{ y: 200, h: 14, x0: -300, x1: 1000, col: hex('#3a345e'), lit: hex('#c98a78'), litA: 0.7, sy: 0.03 }, { y: 360, h: 11, x0: -200, x1: 1000, col: hex('#6a4a70'), lit: hex('#f2b070'), litA: 0.85, thr: 0.5, sy: 0.036 }] });
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
    C.mottle({ amt: 0.06 }); planes.floor = S.plane('floor', D.floor, r, C.c); }
  { const r = cover(D.cliffL, 40); const C = new Canvas(r, { seed: 771 });
    paintCliff(C, { edge: (y) => 132 - 170 * smoothstep(650, 1350, y) + 24 * smoothstep(520, -300, y) + det(y, 14, 6, 1), side: 'L', base: hex('#1a141f'), mid: hex('#2f2330'), rim: hex('#e0a070'), lit: hex('#5a4048') });
    C.mottle({ amt: 0.05 }); planes.cliffL = S.plane('cliffL', D.cliffL, r, C.c); }
  { const r = cover(D.cliffR, 40); const C = new Canvas(r, { seed: 781 });
    paintCliff(C, { edge: (y) => 592 + 170 * smoothstep(650, 1350, y) - 24 * smoothstep(520, -300, y) + det(y, 14, 6, 2), side: 'R', base: hex('#161119'), mid: hex('#2a1f2c'), rim: hex('#d89868'), lit: hex('#4a3640') });
    C.mottle({ amt: 0.05 }); planes.cliffR = S.plane('cliffR', D.cliffR, r, C.c); }
  { const r = cover(D.fg, 50); r[1] = Math.max(r[1], 1000); const C = new Canvas(r, { seed: 791 });
    paintRocks(C, { rocks: [{ x: 10, y: 1290, rx: 200, ry: 120 }, { x: 720, y: 1300, rx: 220, ry: 130 }, { x: 380, y: 1370, rx: 240, ry: 80 }], col: hex('#0c0810'), lit: hex('#3a2c3a'), litA: 0.4, blur: 3 }); planes.fg = S.plane('fg', D.fg, r, C.c); }
  tintAll(S, 1);
  function g_path(C, tr) { const g = C.g; g.strokeStyle = 'rgba(190,150,130,0.22)'; g.lineWidth = 2.2; g.lineCap = 'round'; g.beginPath(); tr.forEach((p, i) => i ? g.lineTo(p.x, p.y) : g.moveTo(p.x, p.y)); g.stroke(); }
  const trail = planes.slope.userData.trail;
  // people on the gorge floor (plane D.floor coordinates)
  const onFloor = (F, x, y, o = {}) => { const hd = hgt(y) * (o.scale ?? 1); const q = F.P(D.floor, x, y), K = F.K(D.floor, x, y); return { q, h: hd * K, hd, K }; };
  function soldier(F, g, x, y, o) { const a = onFloor(F, x, y, o); if (a.h < 2) return null; const face = o.face ?? 1;
    if (a.h < 9) { g.fillStyle = rgba(o.col || hex('#1c1424')); g.beginPath(); g.ellipse(a.q[0], a.q[1] - a.h * 0.42, a.h * 0.17, a.h * 0.42, 0, 0, 7); g.fill(); g.beginPath(); g.arc(a.q[0], a.q[1] - a.h * 0.92, a.h * 0.1, 0, 7); g.fill(); if (o.spear) { g.strokeStyle = rgba(PAL.staff); g.lineWidth = 1; g.beginPath(); g.moveTo(a.q[0] + face * a.h * 0.2, a.q[1]); g.lineTo(a.q[0] + face * a.h * 0.15, a.q[1] - a.h * 1.4); g.stroke(); } return a; }
    person(g, { x: a.q[0], y: a.q[1], h: a.h, face, ph: o.ph ?? 0, walk: o.walk ?? 1, col: o.col || hex('#20162a'), col2: o.col2 || hex('#2e2238'), dark: hex('#150e1c'), hood: false, skinCol: hex('#150e1c'), staff: o.spear, head: o.head ?? -0.05, hem: o.hem ?? 0.28, stride: 0.9, reach: o.reach });
    if (o.shield && a.h > 8) { g.fillStyle = rgba(o.shieldCol || PAL.purple); g.beginPath(); g.arc(a.q[0] + face * a.h * 0.17, a.q[1] - a.h * 0.55, a.h * 0.15, 0, 7); g.fill(); g.strokeStyle = rgba(PAL.gold, 0.8); g.lineWidth = Math.max(0.8, a.h * 0.02); g.stroke(); }
    return a; }
  return {
    planes, D, trail, soldier, onFloor, hgt, floorHalf,

    dyn(F, { gg, items, day, night, rout }) {
      const t = F.t, sh = F.shot, g = F.g, S_ = F.S; const mode = sh.mode; const R = rng(4242);
      const draw = (arr) => { arr.sort((a, b) => a.y - b.y); for (const o of arr) o.fn(); };
      if (mode === 'attack') {
        const arr = []; const waves = sh.waves || [];
        for (const w of waves) { const u = t - w.t0; if (u < -0.1) continue; const N = w.n || 34; const run = w.run || 1.7, hold = w.hold || 0.5, back = w.back || 1.5;
          for (let k = 0; k < N; k++) { const fx = (hash1(k * 3.3 + w.seed) - 0.5) * 2, jy = hash1(k * 5.7 + w.seed) * 70; let y; let face = 1;
            if (u < run) y = lerp(1330, w.yStop + jy, ease.outQuad(clamp(u / run))); else if (u < run + hold) y = w.yStop + jy; else { y = lerp(w.yStop + jy, 1400, ease.inQuad(clamp((u - run - hold) / back))); face = -1; }
            if (y > 1380) continue; const x = 360 + fx * floorHalf(y) * 0.92; const bearer = k % 11 === 0; const spd = u < run ? 1 : (u < run + hold ? 0.15 : 1); const ph = (u * 1.6 * spd + hash1(k) * 3);
            arr.push({ y, fn: () => { soldier(F, g, x, y, { face: face === 1 ? 1 : -1, ph, walk: spd, spear: !bearer, shield: !bearer, col: hex('#2a1a38'), col2: hex('#3a2848'), hem: 0.3 });
              if (bearer) { const a = onFloor(F, x, y); banner(g, { x: a.q[0] + face * a.h * 0.25, y: a.q[1] - a.h * 0.1, h: a.h * 2.6, w: a.h * 1.0, t, dir: -face, seed: k, amp: 0.13 }); } } }); } }
        draw(arr);
      } else if (mode === 'build') {
        const arr = []; for (let k = 0; k < 7; k++) { const pair = k; const x0 = 360 + (hash1(k * 9.1) - 0.5) * 360; const y0 = 1180 - k * 62; const u = ((t * 0.04 + k * 0.17) % 1);
          const y = y0 - u * 40, x = x0 + (360 - x0) * u * 0.12; arr.push({ y, fn: () => { const a1 = soldier(F, g, x - 26, y, { face: 1, ph: t * 0.8 + k, walk: 0.7, head: 0.1 }); const a2 = soldier(F, g, x + 26, y + 2, { face: 1, ph: t * 0.8 + k + 0.4, walk: 0.7, head: 0.1 });
            if (a1 && a2) { g.strokeStyle = rgba(hex('#5a4030')); g.lineWidth = Math.max(3, a1.h * 0.13); g.lineCap = 'round'; g.beginPath(); g.moveTo(a1.q[0] - a1.h * 0.1, a1.q[1] - a1.h * 0.8); g.lineTo(a2.q[0] + a2.h * 0.1, a2.q[1] - a2.h * 0.8); g.stroke(); } } }); }
        draw(arr);
      } else if (mode === 'column') {
        // torches crossing the mountain: the head runs along the path, the rest follow; the path lights as they pass
        const tr = trail; const total = tr[tr.length - 1].s; const sp = sh.speed ?? 130; const s0 = (sh.s0 ?? 0) + (t - sh.t0) * sp; const N = 46, gap = 26;
        for (let k = 0; k < N; k++) { const s = s0 - k * gap; if (s < 0 || s > total) continue; const p = tr.at(s / total); const q = F.P(D.slope, p.x, p.y); const K = F.K(D.slope, p.x, p.y); const fk = fireFlick(t, k);
          g.fillStyle = rgba(hex('#0c0814')); g.beginPath(); g.ellipse(q[0], q[1] - 3 * K, 1.4 * K + 0.5, 3.4 * K + 0.8, 0, 0, 7); g.fill();
          glowAt(gg, q[0], q[1] - 5 * K, 10 * K + 4, 0.85 * fk, [255, 175, 85]); glowAt(gg, q[0], q[1] - 5 * K, 34 * K + 8, 0.2 * fk, [255, 140, 70]); if (k % 4 === 0) F.lights.push({ x: q[0], y: q[1], r: 50 * K, c: WARM, k: 0.6 }); }
        // light spilling over the wall once they are behind it
        const behind = clamp((s0 - total * 0.92) / (total * 0.2)); if (behind > 0) { const p = F.P(D.valley, 380, 640); glowAt(gg, p[0], p[1], 260 * F.K(D.valley), 0.5 * behind, [255, 150, 70]); }
      } else if (mode === 'captives') {
        const arr = []; const sp = 26; for (let k = 0; k < 26; k++) { const u = (t - sh.t0) * sp * 0.5 + k * 34; const y = 760 + u * 0.55 + 0; const yy = y; if (yy > 1350 || yy < 740) continue; const x = 360 + (k % 2 ? 1 : -1) * floorHalf(yy) * (0.12 + 0.1 * (k % 3));
          arr.push({ y: yy, fn: () => { soldier(F, g, x, yy, { face: 1, ph: (t - sh.t0) * 1.1 + k * 0.4, walk: 0.8, head: 0.22, col: hex('#241a2c'), col2: hex('#30243a'), hem: 0.3, reach: k % 2 ? [0.3, 0.8] : null }); } });
          if (k % 5 === 2) { const gx = 360 + (k % 2 ? -1 : 1) * floorHalf(yy) * 0.75; arr.push({ y: yy + 1, fn: () => { const a = soldier(F, g, gx, yy, { face: 1, ph: (t - sh.t0) * 1.2 + k, walk: 1, spear: false, col: hex('#20162a') }); if (a) { const f = torch(g, a.q[0] + a.h * 0.22, a.q[1] - a.h * 0.8, a.h * 0.16, t, k, 1); glowAt(gg, f[0], f[1], a.h * 0.9, 0.5 * fireFlick(t, k)); F.lights.push({ x: f[0], y: f[1], r: a.h * 1.4, c: WARM, k: 0.5 }); } } }); } }
        draw(arr);
      } else if (mode === 'flare') {
        // the rout: fire flares behind the wall, smoke and sparks
        for (const h0 of sh.hits || []) { const u = t - h0; if (u < 0 || u > 2.6) continue; const a = Math.exp(-u * 0.9) * smoothstep(0, 0.1, u); const x = lerp(W_.x0 + 40, W_.x1 - 40, hash1(h0 * 5.1)); const p = F.P(D.wall, x, W_.top + 20); glowAt(gg, p[0], p[1], 150 * F.K(D.wall) * (0.8 + u * 0.3), 0.7 * a, [255, 120, 50]); F.lights.push({ x: p[0], y: p[1], r: 200 * F.K(D.wall), c: WARM, k: 1.2 * a }); }
        embers(gg, t, { x0: 100, y0: 380, x1: 620, y1: 640 }, 40, { size: 1.8, col: [255, 170, 80], a: 0.8, wind: -20, rise: 1.3, seed: 5 });
      }
      if (sh.embers) embers(gg, t, { x0: 0, y0: 300, x1: 720, y1: 1100 }, 30, { size: 1.3, col: [255, 200, 130], a: 0.5, wind: 14, rise: 0.4, seed: 8 });
    },
    update(F) {
      const t = F.t, lt = F.lt, sh = F.shot, g = F.g, S_ = F.S; const night = typeof sh.night === 'function' ? sh.night(t) : (sh.night ?? 0); const day = 1 - 0.72 * night; const W = WALL;
      tintAll(S_, day, [1 - 0.5 * night * 0.7, 1 - 0.25 * night * 0.5, 1 + 0.08 * night]);
      const gg = F.glow(); const hits = sh.hits || [];
      // the glow at the gorge end (sun low) and dust that the fighting kicks up
      const sunp = F.P(D.sky, 380, 520); glowAt(gg, sunp[0], sunp[1], 380 * Math.max(1, F.K(D.sky)), 0.1 * (1 - night), [255, 190, 110]);
      { const bp = F.P(D.wall, 362, W.base + 6); const kk = F.K(D.wall, 362, W.base); glowAt(gg, bp[0], bp[1], 330 * kk, 0.07 * (1 - night), [230, 170, 110]); }
      const Pw = (x, y) => F.P(D.wall, x, y), Kw = F.K(D.wall, 360, 650);
      // defenders on the wall: stand along the walkway; they run when the rout begins
      const rout = sh.rout ? smoothstep(sh.rout, sh.rout + 0.6, t) : 0; const items = [];
      if (sh.defenders !== false) { const R = rng(91); for (let k = 0; k < 18; k++) { const x = W.x0 + 20 + (W.x1 - W.x0 - 40) * ((k + 0.5) / 18) + (R() - 0.5) * 8; const sway = rout * Math.sin(t * 5 + k * 1.7) * 18 * (R() + 0.3); const p = Pw(x + sway, W.top + 40); const hh = 30 * Kw * (D.wall / 220) ;
          const drop = rout * (k % 3 === 0 ? 1 : 0) * 18 * Kw; g.fillStyle = rgba(hex('#1a1220')); const px_ = p[0], py_ = p[1] + drop; g.beginPath(); g.ellipse(px_, py_ - hh * 0.4, hh * 0.15, hh * 0.4, 0, 0, 7); g.fill(); g.beginPath(); g.arc(px_, py_ - hh * 0.9, hh * 0.1, 0, 7); g.fill();
          if (k % 3 === 1) { g.strokeStyle = rgba(PAL.staff); g.lineWidth = Math.max(1, Kw * 1.1); g.beginPath(); g.moveTo(px_ + hh * 0.2, py_); g.lineTo(px_ + hh * 0.17, py_ - hh * 1.5); g.stroke(); } } }
      // wall banners (Bulgarian: dark red, a pale disc)
      if (sh.banners !== false) for (const [bx, by, h, dir, seed] of [[W.x0 + 16, W.top - 70, 70, 1, 3], [376, W.top - 70, 84, 1, 5], [W.x1 - 22, W.top - 70, 70, -1, 7]]) { const p = Pw(bx, by); banner(g, { x: p[0], y: p[1], h: h * Kw * 1.3, w: 46 * Kw, t, dir, col: PAL.red, colLit: PAL.redLit, trim: hex('#d8b868'), emblem: 'none', seed, amp: 0.1 * (1 + 2 * rout) }); }
      // torches on the wall at night
      const torchOn = night > 0.3 ? 1 : 0; if (torchOn) for (let k = 0; k < 7; k++) { const x = W.x0 + 40 + k * 62; const p = Pw(x, W.top + 34); const s = 14 * Kw; const f = torch(g, p[0], p[1], s, t, k, 1); glowAt(gg, f[0], f[1], 70 * Kw, 0.5 * fireFlick(t, k)); }
      // dust puffs and arrow volleys on the beats
      for (const h0 of hits) { const u = (t - h0); if (u < 0 || u > 2.2) continue; const a = Math.exp(-u * 1.3) * smoothstep(0, 0.08, u);
        for (let k = 0; k < 4; k++) { const x = lerp(W.x0 + 40, W.x1 - 40, hash1(h0 * 7 + k)); const p = Pw(x + u * 10 * (k - 1.5), W.base - 6 - u * 34); glowAt(gg, p[0], p[1], (46 + u * 70) * Kw, 0.30 * a, [255, 190, 110]); }
        if (u < 0.7) { for (let k = 0; k < 14; k++) { const x0 = lerp(120, 600, hash1(h0 * 3 + k)); const s = u / 0.7; const a0 = F.P(D.floor, x0, 1180), a1 = F.P(D.wall, lerp(W.x0 + 30, W.x1 - 30, hash1(h0 + k * 1.7)), W.top + 30); const px_ = lerp(a0[0], a1[0], s), py_ = lerp(a0[1], a1[1], s) - 140 * Math.sin(Math.PI * s); const pxb = lerp(a0[0], a1[0], s - 0.06), pyb = lerp(a0[1], a1[1], s - 0.06) - 140 * Math.sin(Math.PI * Math.max(0, s - 0.06));
            gg.strokeStyle = `rgba(255,230,180,${0.55 * (1 - s * 0.4)})`; gg.lineWidth = 1.3; gg.beginPath(); gg.moveTo(pxb, pyb); gg.lineTo(px_, py_); gg.stroke(); } } }
      this.dyn(F, { gg, items, day, night, rout });
      F.amb = [0.9 * day + 0.1, 0.88 * day + 0.1, 0.95 * day + 0.1]; F.bloom = 0.5;
    },
  };
}
