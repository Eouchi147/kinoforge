// p03 — the three painted multiplane setups. Each builder paints its planes once (init) and returns camera() + update().
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, noise1, rng, valueNoise2D } from '/harness/kit/film.js';
import { Setup, setLights } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, paintSky, paintRange, paintPineRidge, pineTree, paintFog, paintHouse, paintRocks, paintBough, paintTufts, ridged, underpaint } from './paint.js';

export const WARM = [1.0, 0.47, 0.15];               // lantern light on paint (linear)
export const GLOW = [1.0, 0.6, 0.27];               // glow sprite colour (linear; HDR via intensity)
const nn = valueNoise2D(77), nn2 = valueNoise2D(91);
const det = (x, a = 22, b = 8, s = 0) => a * (nn.fbm(x * 0.008 + s, 3.1, 5) - 0.5) + b * (nn2.fbm(x * 0.04 + s, 7.3, 3) - 0.5);
const bump = (x, c, w, h) => h * Math.exp(-(((x - c) / w) ** 2));
export const fovV = (mm) => 2 * Math.atan(12 / mm) * 180 / Math.PI;
export function camAt(mm, pos, look) { const c = new THREE.PerspectiveCamera(fovV(mm), 16 / 9, 0.1, 1e5); c.position.set(...pos); c.lookAt(new THREE.Vector3(...look)); c.updateMatrixWorld(); c.updateProjectionMatrix(); return c; }
// lantern ignition: quick catch, flare, settle, living flicker (deterministic)
export function igniteEnv(t, t0, seed = 0, flare = 1.45, rise = 0.07) {
  if (t < t0) return 0; const u = t - t0; const a = ease.outCubic(clamp(u / rise)); const f = 1 + (flare - 1) * Math.exp(-Math.max(0, u - rise) / 0.18);
  return a * f * (1 + 0.05 * noise1(t * 8.3 + seed * 3.7, seed) + 0.025 * noise1(t * 21 + seed, seed + 2));
}
export const flick = (t, seed) => 1 + 0.05 * noise1(t * 8.3 + seed * 3.7, seed) + 0.025 * noise1(t * 21 + seed, seed + 2);

// houses in irregular clusters along a terrace (overlapping, mixed gable/eave, staggered)
function clusters(R, x0, x1, wA, wB, hA, hB, { gap = [14, 50], tag = null, gableP = 0.3 } = {}) {
  const a = []; let x = x0 + R() * 16;
  while (x < x1) { const n = 1 + Math.floor(R() * 4);
    for (let k = 0; k < n && x < x1; k++) { const w = lerp(wA, wB, R()); a.push({ x: x + w / 2, w, h: lerp(hA, hB, R()), roofK: 0.46 + R() * 0.18, z: R(), dy: (R() - 0.5) * hA * 0.35, gable: R() < gableP, lantern: typeof tag === 'function' ? tag(x) : tag }); x += w * (0.86 + R() * 0.3); }
    x += lerp(gap[0], gap[1], R()); }
  return a;
}
// a terrace row: slope + retaining wall below `base`, trees, houses standing on `base`, steps, lantern posts
function paintTerrace(C, P) {
  const { base } = P; const [x0, y0, x1, y1] = C.rect; const g = C.g, R = C.R; const wallH = P.wallH || 0;
  const path = new Path2D(); path.moveTo(x0 - 20, y1 + 20); for (let x = x0 - 20; x <= x1 + 20; x += 3) path.lineTo(x, base(x) - 1); path.lineTo(x1 + 20, y1 + 20); path.closePath();
  underpaint(C, (x, y) => mixc(P.slopeTop, P.slopeBot, smoothstep(base(x), base(x) + (P.slopeFall || 160), y)), path, 8);
  const m = C.mask((gg) => gg.fill(path));
  C.strokes({ n: C.area / (P.slopeDensity || 1300), mask: m, color: (x, y) => mixc(P.slopeTop, P.slopeBot, smoothstep(base(x) + wallH, base(x) + (P.slopeFall || 160), y)), angle: (x, y) => (nn.fbm(x * 0.01, y * 0.01, 3) > 0.5 ? -0.7 : 0.7) + (C.R() - 0.5) * 0.5, len: [12, 30], wid: [5, 10], alpha: [0.45, 0.75], jv: 0.07 });
  if (P.shrubs) for (let x = x0; x < x1; x += 10 + R() * 22) { const yb = base(x) + wallH + 6 + R() * (P.slopeFall || 160) * 0.6; if (yb > y1) continue; const s = 4 + R() * 9; C.dab(x, yb, -0.2 + (R() - 0.5) * 0.6, s * 2, s, mul(P.slopeBot, 0.7 + R() * 0.25), 0.85, 0.2, 1.0); }
  if (wallH) { // dry-stone retaining wall: courses of stone dabs, lit top edge
    for (let x = x0 - 10; x < x1 + 10; x += 5 + R() * 6) { const yb = base(x); for (let yy = yb + 2; yy < yb + wallH; yy += 3 + R() * 3) C.dab(x + R() * 4, yy, (R() - 0.5) * 0.25, 5 + R() * 7, 2.5 + R() * 2.5, mul(P.wall, 0.72 + R() * 0.45), 0.85, 0.05); C.dab(x + 2, yb + 1.2, (R() - 0.5) * 0.15, 7 + R() * 6, 1.6, P.wallTop || mul(P.wall, 1.35), 0.6, 0.03); }
  }
  for (const tr of P.trees || []) pineTree(C, tr[0], base(tr[0]) + 2 + (tr[3] || 0), tr[1], mul(P.tree || hex('#12152a'), 0.88 + R() * 0.24), { rim: P.treeRim, rimSide: -1, tierPx: Math.max(3, tr[1] / 8), wr: tr[2] || 0.32 });
  const houses = []; for (const h of (P.houses || []).slice().sort((a, b) => (a.z || 0) - (b.z || 0))) {
    const r = paintHouse(C, h.x, base(h.x) + (h.dy || 0), h.w, h.h, { wall: P.houseWall, roof: P.houseRoof, crest: P.crest, win: hex('#100e18'), roofK: h.roofK ?? 0.5, gable: h.gable, sideShade: R() < 0.5 ? 1 : -1, litLeft: 0.12 });
    houses.push({ ...h, ...r }); }
  for (const seg of P.steps || []) { const [ax, ay, bx, by] = seg; const n = Math.max(3, Math.round(Math.hypot(bx - ax, by - ay) / 4)); for (let i = 0; i <= n; i++) { const u = i / n; C.dab(lerp(ax, bx, u) + (R() - 0.5), lerp(ay, by, u), (R() - 0.5) * 0.2, P.stepW || 7, 1.7, mul(P.step || hex('#5c5878'), 0.8 + R() * 0.35), 0.8, 0.02); } }
  const posts = []; for (const p of P.posts || []) { const yb = base(p.x) + (p.dy || 0); const ph = p.h; g.fillStyle = rgba(hex('#100e17')); g.fillRect(p.x - Math.max(0.8, ph * 0.05), yb - ph, Math.max(1.6, ph * 0.1), ph);
    const lw = Math.max(2.2, ph * 0.22), lh = Math.max(2.8, ph * 0.3); g.fillStyle = rgba(hex('#16121b')); g.fillRect(p.x - lw * 0.65, yb - ph - lh - 1.2, lw * 1.3, 1.4); g.fillStyle = rgba(hex('#4f4860')); g.fillRect(p.x - lw / 2, yb - ph - lh, lw, lh);
    posts.push({ x: p.x, y: yb - ph - lh / 2, id: p.id }); }
  C.mottle({ amt: 0.07, cell: 14 });
  return { houses, posts };
}

// ================================================================== S1 — EWS, lateral dolly along the ridge road
export function buildS1(TM) {
  const S = new Setup('S1', { pos: [0, 0, 0], mm: 32 }); const f = S.f;
  const vM = TM.walk.step / TM.walk.T * TM.walk.heightM; // m/s
  const camX = (t) => { const a = 2.4, u = clamp(t / a); return vM * 1.25 * (t < a ? a * (u ** 3 - 0.5 * u ** 4) : a * 0.5 + (t - a)); };
  const cams = [0, 1.2, 2.4, 3.5, 4.6].map((t) => camAt(32, [camX(t), 0, 0], [camX(t), 0, -100]));
  const cover = (D, m) => S.cover(D, cams, m);
  const D = { sky: 6000, peaks: 1600, mid: 620, village: 330, fog: 260, fog2: 190, pines: 125, road: 95, brush: 45, fg: 12 };
  const yFar = (x) => 512 - 0.05 * (x - 425) + 3 * Math.sin(x * 0.009 + 0.5), yNear = (x) => yFar(x) + 21 + 3 * Math.sin(x * 0.021 + 1), yWalk = (x) => yFar(x) + 9.5;
  const planes = {};
  // --- sky: indigo overhead, afterglow low at the left (the light he walks away from)
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 11 });
    paintSky(C, { stops: [[-80, hex('#0e1235')], [50, hex('#171d4a')], [160, hex('#2a3064')], [250, hex('#444580')], [320, hex('#635e8f')], [380, hex('#847599')], [460, hex('#937f9f')]],
      glow: { x: 60, y: 385, rx: 720, ry: 170, col: hex('#c49fa6'), a: 0.55 },
      clouds: [{ y: 128, h: 13, x0: -150, x1: 760, col: hex('#1f2454'), lit: hex('#5d5789'), litA: 0.6, sy: 0.03 }, { y: 236, h: 10, x0: 420, x1: 1500, col: hex('#3a3d72'), lit: hex('#8f7c9f'), litA: 0.7, thr: 0.5, sy: 0.034 },
        { y: 62, h: 15, x0: 700, x1: 1650, col: hex('#141943'), lit: hex('#2f3366'), litA: 0.5, sy: 0.03 }, { y: 30, h: 18, x0: -200, x1: 640, col: hex('#121640'), lit: hex('#272c5c'), litA: 0.5, sy: 0.026, thr: 0.48 },
        { y: 178, h: 9, x0: 860, x1: 1600, col: hex('#2a2f63'), lit: hex('#6a6292'), litA: 0.6, sy: 0.04, thr: 0.5 }] });
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  // --- far peaks: a massif left of centre stepping down to the right (leads the eye toward the village)
  { const r = cover(D.peaks); const C = new Canvas(r, { seed: 21 });
    const ridge = (x) => 318 - bump(x, 430, 170, 140) - bump(x, 640, 120, 95) - bump(x, 190, 110, 62) - bump(x, 960, 140, 64) - bump(x, 1240, 120, 38) - 34 * ridged(x * 0.0065, 4, 1) - 9 * ridged(x * 0.03, 3, 2);
    paintRange(C, { ridge, top: hex('#323866'), mid: hex('#383d6c'), base: hex('#474a79'), fall: 150, light: { dir: -1, col: hex('#5a5f93'), amt: 0.45 }, shade: 0.18, haze: { col: hex('#4f4d7e'), y0: 280, y1: 350, a: 0.45 }, snow: { y: 232, col: hex('#8a8bb6'), amt: 0.85 }, rim: hex('#9c8fb0') });
    C.mottle({ amt: 0.05 }); planes.peaks = S.plane('peaks', D.peaks, r, C.c); }
  // --- mid mountains: dark ridge from the left down into the valley, then the village spur rising at the right
  { const r = cover(D.mid); const C = new Canvas(r, { seed: 31 });
    const ridge = (x) => 370 - bump(x, 150, 200, 26) + 28 * smoothstep(450, 760, x) - 74 * smoothstep(820, 1090, x) - bump(x, 1240, 160, 24) - 12 * ridged(x * 0.01, 3, 3);
    paintRange(C, { ridge, top: hex('#262a55'), mid: hex('#2e325f'), base: hex('#45477a'), fall: 110, light: { dir: -1, col: hex('#3e4377'), amt: 0.4 }, shade: 0.12, haze: { col: hex('#5a5788'), y0: 390, y1: 452, a: 0.85 }, rim: hex('#5a5f92'), sizes: 0.9 });
    C.mottle({ amt: 0.05 }); planes.mid = S.plane('mid', D.mid, r, C.c); }
  // --- the distant village on its spur (right): dark and unlit — it wakes in S2
  { const r = cover(D.village); const C = new Canvas(r, { seed: 41 }); const RR = rng(4401);
    const spur = (x) => 458 - 128 * smoothstep(800, 1070, x) + det(x, 8, 4, 9) - bump(x, 1210, 100, 12);
    const base = (x) => spur(x) + 2, base2 = (x) => spur(x) + 24 + 3 * Math.sin(x * 0.03);
    const trees = []; for (let x = 790; x < 1540; x += 8 + RR() * 16) trees.push([x, 10 + RR() * 16, 0.3]);
    paintTerrace(C, { base, slopeTop: hex('#23264c'), slopeBot: hex('#363a68'), slopeFall: 90, trees, houses: clusters(RR, 960, 1520, 12, 19, 7, 11, { gap: [8, 30] }), houseWall: hex('#34324f'), houseRoof: hex('#15172d'), crest: hex('#3f4270'), slopeDensity: 900 });
    paintTerrace(C, { base: base2, wallH: 5, wall: hex('#34324f'), slopeTop: hex('#202347'), slopeBot: hex('#3a3d6c'), slopeFall: 90, houses: clusters(RR, 910, 1500, 13, 20, 8, 12, { gap: [10, 34] }), houseWall: hex('#383552'), houseRoof: hex('#14162b'), crest: hex('#3d406c'), slopeDensity: 900 });
    const road = [[730, 478], [905, 442], [840, 420], [990, 395], [930, 377], [1010, 360]];
    for (let i = 0; i < road.length - 1; i++) for (let k = 0; k < 7; k++) { const u = k / 7; C.dab(lerp(road[i][0], road[i + 1][0], u), lerp(road[i][1], road[i + 1][1], u), Math.atan2(road[i + 1][1] - road[i][1], road[i + 1][0] - road[i][0]), 16, 3.2, hex('#5a5578'), 0.8, 0.02); }
    planes.village = S.plane('village', D.village, r, C.c); }
  // --- valley fog (two bands, drifting with the wind toward -x); the lower band sits right behind the traveler
  { const r = cover(D.fog, 90); const C = new Canvas(r, { seed: 51 });
    paintFog(C, { y: (x) => 432 + 12 * Math.sin(x * 0.004), h: 34, col: hex('#5d5a88'), top: hex('#7b77a3'), a: 0.95, density: 1.5, wisp: 0.8, blur: 3 });
    planes.fog = S.plane('fog', D.fog, r, C.c); planes.fog.userData.drift = 7; }
  { const r = cover(D.fog2, 120); const C = new Canvas(r, { seed: 52 });
    paintFog(C, { y: (x) => 494 + 6 * Math.sin(x * 0.006 + 1), h: 15, col: hex('#64608e'), top: hex('#807ba6'), a: 0.9, density: 1.5, wisp: 0.7, blur: 2 });
    planes.fog2 = S.plane('fog2', D.fog2, r, C.c); planes.fog2.userData.drift = 11; }
  // --- ridge pines beyond the road; a gap behind the traveler so he reads against the fog
  { const r = cover(D.pines); const C = new Canvas(r, { seed: 61 });
    paintPineRidge(C, { base: (x) => yFar(x) - 1, hMin: 16, hMax: 60, spacing: 12, col: hex('#12152a'), rim: hex('#2f3660'), gaps: [[262, 770]], gapKeep: 0.05, heightEnv: (x) => 0.55 + 0.45 * smoothstep(200, 0, x) + 0.45 * smoothstep(780, 1020, x), tierPx: 6 });
    C.mottle({ amt: 0.05 }); planes.pines = S.plane('pines', D.pines, r, C.c); }
  // --- the road on the ridge crest + the dark near slope below it
  { const r = cover(D.road); const C = new Canvas(r, { seed: 71 }); const g = C.g; const [x0, , x1, y1] = r;
    const slope = new Path2D(); slope.moveTo(x0 - 10, y1 + 10); for (let x = x0 - 10; x <= x1 + 10; x += 3) slope.lineTo(x, yNear(x)); slope.lineTo(x1 + 10, y1 + 10); slope.closePath();
    underpaint(C, (x, y) => mixc(hex('#2a2c48'), hex('#0e1022'), smoothstep(yNear(x), yNear(x) + 190, y)), slope, 8); const ms = C.mask((gg) => gg.fill(slope));
    C.strokes({ n: C.area / 1100, mask: ms, color: (x, y) => mixc(hex('#272a46'), hex('#0e1023'), smoothstep(yNear(x), yNear(x) + 160, y)), angle: (x, y) => (nn.fbm(x * 0.012, y * 0.01, 3) > 0.5 ? -0.75 : 0.75) + (C.R() - 0.5) * 0.4, len: [14, 38], wid: [5, 11], alpha: [0.45, 0.8], jv: 0.08 });
    const band = new Path2D(); band.moveTo(x0 - 10, yFar(x0 - 10)); for (let x = x0 - 10; x <= x1 + 10; x += 3) band.lineTo(x, yFar(x)); for (let x = x1 + 10; x >= x0 - 10; x -= 3) band.lineTo(x, yNear(x) + 1); band.closePath();
    const roadCol = (x, y) => { const u = clamp((y - yFar(x)) / (yNear(x) - yFar(x))); return mixc(mixc(hex('#46425f'), hex('#2f2c46'), smoothstep(0.4, 1.0, u)), hex('#5a557a'), 0.6 * smoothstep(0.25, 0.0, u)); };
    underpaint(C, roadCol, band, 4); const mb = C.mask((gg) => gg.fill(band));
    C.strokes({ n: C.area / 750, box: [x0, 440, x1, 580], mask: mb, color: roadCol, angle: () => Math.atan(-0.05) + (C.R() - 0.5) * 0.16, len: [14, 34], wid: [4, 8], alpha: [0.5, 0.85], jv: 0.06, bend: 0.05 });
    for (let x = x0; x < x1; x += 3 + C.R() * 6) { const y = lerp(yFar(x) + 4, yNear(x) - 3, C.R()); C.dab(x, y, (C.R() - 0.5) * 0.6, 3 + C.R() * 3, 2 + C.R() * 1.5, C.R() < 0.5 ? hex('#34314a') : hex('#6c6788'), 0.4, 0.1); }
    for (const k of [0.42, 0.74]) for (let x = x0; x < x1; x += 6) { const y = lerp(yFar(x), yNear(x), k) + Math.sin(x * 0.05) * 0.6; C.dab(x, y, Math.atan(-0.05), 9, 1.6, hex('#36334c'), 0.4, 0.02); }
    paintTufts(C, { x0, x1, base: (x) => yFar(x) + 1, step: 7, h0: 3, h1: 8, col: hex('#191b31'), blades: 4 });
    paintTufts(C, { x0, x1, base: (x) => yNear(x) + 2, step: 9, h0: 4, h1: 11, col: hex('#15172c'), blades: 5 });
    for (let i = 0; i < 26; i++) { const x = lerp(x0, x1, C.R()); const y = yNear(x) + 22 + C.R() * 140; const rr = 4 + C.R() * 12; C.dab(x, y, -0.3 + (C.R() - 0.5) * 0.4, rr * 2, rr, hex('#121427'), 0.9, 0.2, 1.0); C.dab(x - rr * 0.3, y - rr * 0.35, -0.4, rr * 1.2, rr * 0.3, hex('#2c2f4e'), 0.55, 0.1); }
    C.mottle({ amt: 0.07 }); planes.road = S.plane('road', D.road, r, C.c); }
  // --- near brush on the slope (mid-fast parallax)
  { const r = cover(D.brush); const C = new Canvas(r, { seed: 81 });
    const base = (x) => 640 + 25 * Math.sin(x * 0.006) + det(x, 18, 6, 3);
    for (let x = r[0]; x < r[2]; x += 26 + C.R() * 40) { const h = 30 + C.R() * 60; const yb = base(x) + 30; for (let k = 0; k < 14; k++) { const a = -Math.PI / 2 + (C.R() - 0.5) * 1.6; C.dab(x + Math.cos(a) * h * 0.4, yb + Math.sin(a) * h * 0.4, a, h * (0.5 + C.R() * 0.5), 4 + C.R() * 5, mul(hex('#0f1122'), 0.8 + C.R() * 0.4), 0.9, 0.15, 0.9); }
      if (C.R() < 0.6) C.dab(x - h * 0.15, yb - h * 0.55, -2.2, h * 0.35, 3, hex('#262a4a'), 0.5, 0.1); }
    const path = new Path2D(); path.moveTo(r[0], r[3]); for (let x = r[0]; x <= r[2]; x += 4) path.lineTo(x, base(x) + 34); path.lineTo(r[2], r[3]); path.closePath(); C.g.fillStyle = rgba(hex('#0d0f1f')); C.g.fill(path);
    C.blur(1.2); planes.brush = S.plane('brush', D.brush, r, C.c); }
  // --- foreground: out-of-focus rocks along the bottom + a pine bough from the top-left
  { const r = cover(D.fg); const C = new Canvas(r, { seed: 91 });
    const rocks = []; for (let x = r[0] - 40; x < r[2] + 40; x += 150 + C.R() * 200) rocks.push({ x, y: 744 + C.R() * 30, rx: 70 + C.R() * 110, ry: 34 + C.R() * 30 });
    paintRocks(C, { rocks, col: hex('#090a15'), lit: hex('#20233f') });
    // out-of-focus grass clumps (repoussoir): one at the bottom-left, one that slides in from the right during the dolly
    // out-of-focus boulders (repoussoir): bottom-left at the start, one sliding in from the right during the dolly
    paintRocks(C, { rocks: [{ x: 40, y: 690, rx: 250, ry: 95 }, { x: 330, y: 770, rx: 170, ry: 70 }, { x: 1500, y: 690, rx: 260, ry: 100 }, { x: 1760, y: 740, rx: 200, ry: 80 }], col: hex('#080914'), lit: hex('#2f3458'), litA: 0.42 });
    C.blur(3.5); planes.fg = S.plane('fg', D.fg, r, C.c); }

  const ropeGlows = TM.s1.ropeLanterns.map(() => S.glow(0, 0, D.road, 40, { color: GLOW, core: 90 }, planes.road));
  const handGlow = S.glow(0, 0, D.road, 30, { color: GLOW, core: 110 }, planes.road);
  return {
    setup: S, D, planes, yWalk, camX, vM,
    camera(cam, t) { const x = camX(t); cam.position.set(x, 0, 0); cam.lookAt(x, 0, -100); },
    update(t, { lanternWorld, ropeWorld, ropeOn }) {
      for (const k of ['fog', 'fog2']) { const p = planes[k]; p.position.x = p.userData.base.x - p.userData.drift * t * p.userData.D / f; }
      ropeGlows.forEach((gm, i) => { gm.position.copy(ropeWorld[i]); gm.material.uniforms.uI.value = 1.5 * ropeOn[i]; });
      handGlow.position.copy(lanternWorld); handGlow.material.uniforms.uI.value = 1.1 * flick(t, 9);
      setLights(planes.road.material, [{ p: lanternWorld, r: 1.1, c: WARM, k: 2.4 * flick(t, 9) }, ...ropeWorld.map((p, i) => ({ p, r: 2.0, c: WARM, k: 3.0 * ropeOn[i] }))]);
    },
  };
}

// ================================================================== S2 — low angle, crane up + tilt: the village wakes
export function buildS2(TM) {
  const S = new Setup('S2', { pos: [0, 0, 0], mm: 26 }); const f = S.f; const CRANE = 17, TILT = 12 * Math.PI / 180;
  const pose2 = (k) => { const y = CRANE * k, th = TILT * k; return { pos: [0, y, 0], look: [0, y + Math.tan(th) * 100, -100] }; };
  const cams = [0, 0.25, 0.5, 0.75, 1].map((k) => { const p = pose2(k); return camAt(26, p.pos, p.look); });
  const cover = (D, m) => S.cover(D, cams, m);
  const D = { sky: 6000, peaks: 1500, flank: 400, upper: 210, fogA: 185, middle: 160, fogB: 140, lower: 125, road: 100, fg: 30 };
  const shift = (Dd) => f * Math.tan(TILT) + CRANE * f / Dd; const E = (Dd) => (y) => y - shift(Dd); // end-pose y -> reference y at depth Dd
  const planes = {}; const lights = { lower: [], middle: [], upper: [] }; const windows = [];
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 211 }); const e = E(D.sky);
    paintSky(C, { stops: [[e(-60), hex('#0c1030')], [e(80), hex('#151a42')], [e(200), hex('#262c5d')], [e(330), hex('#3e4074')], [e(470), hex('#5d5888')]],
      glow: { x: -100, y: e(330), rx: 520, ry: 150, col: hex('#93809f'), a: 0.35 },
      clouds: [{ y: e(95), h: 13, x0: 520, x1: 1600, col: hex('#181d4b'), lit: hex('#43427a'), litA: 0.6, sy: 0.03 }, { y: e(30), h: 12, x0: -200, x1: 700, col: hex('#121640'), lit: hex('#30336a'), litA: 0.5, sy: 0.03 }] });
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.peaks); const C = new Canvas(r, { seed: 221 }); const e = E(D.peaks);
    const ridge = (x) => e(300) - bump(x, 330, 150, 170) - bump(x, 640, 160, 240) - bump(x, 1000, 140, 175) - bump(x, 1320, 120, 115) - 36 * ridged(x * 0.006, 4, 4) - 10 * ridged(x * 0.03, 3, 5);
    paintRange(C, { ridge, top: hex('#353b6b'), mid: hex('#3e4373'), base: hex('#4c4f7f'), fall: 190, light: { dir: -1, col: hex('#646a9c'), amt: 0.5 }, shade: 0.16, haze: { col: hex('#4b4c7c'), y0: e(210), y1: e(300), a: 0.8 }, snow: { y: e(150), col: hex('#8e8fb9'), amt: 0.85 }, rim: hex('#b9a2b8') });
    C.mottle({ amt: 0.05 }); planes.peaks = S.plane('peaks', D.peaks, r, C.c); }
  { const r = cover(D.flank); const C = new Canvas(r, { seed: 231 }); const e = E(D.flank);
    const ridge = (x) => e(192) - bump(x, 1150, 260, 60) - bump(x, 160, 200, 25) - 14 * ridged(x * 0.008, 3, 6);
    paintRange(C, { ridge, top: hex('#23264f'), mid: hex('#2a2e59'), base: hex('#3b3e6c'), fall: 260, light: { dir: -1, col: hex('#3c4176'), amt: 0.35 }, shade: 0.12, rim: hex('#4e5488') });
    const RR = rng(2311); for (let i = 0; i < 70; i++) { const x = lerp(r[0], r[2], RR()); if (nn.fbm(x * 0.006, 1.3, 3) < 0.5) continue; pineTree(C, x, ridge(x) + 4 + RR() * 10, 10 + RR() * 14, hex('#191c36'), { tierPx: 3, rim: hex('#3b4072') }); }
    C.mottle({ amt: 0.05 }); planes.flank = S.plane('flank', D.flank, r, C.c); }
  const terrace = (key, Dd, seed, P) => { const r = cover(Dd); const C = new Canvas(r, { seed }); const e = E(Dd);
    const base = (x) => e(P.baseE(x)); const steps = (P.stepsE || []).map(([ax, ay, bx, by]) => [ax, e(ay), bx, e(by)]);
    const out = paintTerrace(C, { base, wallH: P.wallH, wall: hex('#3c3a58'), wallTop: hex('#5d5a7e'), slopeTop: P.slopeTop || hex('#1f2242'), slopeBot: P.slopeBot || hex('#15172f'), slopeFall: P.fall || 120, shrubs: false,
      trees: P.trees, houses: P.houses, houseWall: P.wallC || hex('#2d2b47'), houseRoof: hex('#151629'), crest: hex('#4b4e7c'), treeRim: hex('#2e3460'), steps, step: hex('#5c5878'), stepW: P.stepW, posts: P.posts });
    const pl = S.plane(key, Dd, r, C.c); planes[key] = pl;
    for (const h of out.houses) for (const w of h.windows) windows.push({ plane: pl, D: Dd, x: w[0] + w[2] / 2, y: w[1] + w[3] / 2, w: w[2], h: w[3], lantern: h.lantern });
    for (const p of out.posts) lights[key].push({ id: p.id, x: p.x, y: p.y, D: Dd, plane: pl });
    return pl; };
  const RR = rng(2401); const trees = (x0, x1, hA, hB, n) => Array.from({ length: n }, () => [lerp(x0, x1, RR()), lerp(hA, hB, RR()), 0.28 + RR() * 0.1, (RR() - 0.5) * 6]);
  terrace('upper', D.upper, 241, { baseE: (x) => 312 + 0.00026 * (x - 770) ** 2 + det(x, 5, 2, 11), wallH: 9, fall: 90,
    houses: [...clusters(RR, 440, 735, 18, 25, 10, 13, { tag: 'V5' }), { x: 772, w: 40, h: 20, roofK: 0.62, z: 2, gable: true, lantern: 'V6' }, ...clusters(RR, 812, 1100, 18, 25, 10, 13, { tag: 'V5' })],
    trees: trees(420, 1120, 14, 28, 24), posts: [{ id: 'V5', x: 640, h: 9 }, { id: 'V6', x: 800, h: 12, dy: -2 }], stepsE: [[700, 324, 760, 306], [640, 336, 700, 324]], stepW: 4 });
  { const r = cover(D.fogA, 330); const e = E(D.fogA); const L = new Canvas(r, { seed: 251 }), Rr = new Canvas(r, { seed: 252 });
    paintFog(L, { y: (x) => e(352) + 6 * Math.sin(x * 0.01), h: 20, col: hex('#57558a'), top: hex('#77739f'), a: 1, density: 1.6, wisp: 0.8, xEnv: (x) => 1 - smoothstep(560, 760, x) });
    paintFog(Rr, { y: (x) => e(348) + 6 * Math.sin(x * 0.012 + 2), h: 20, col: hex('#57558a'), top: hex('#77739f'), a: 1, density: 1.6, wisp: 0.8, xEnv: (x) => smoothstep(560, 760, x) });
    planes.fogAL = S.plane('fogAL', D.fogA, r, L.c); planes.fogAR = S.plane('fogAR', D.fogA, r, Rr.c); }
  terrace('middle', D.middle, 261, { baseE: (x) => 412 + 0.00016 * (x - 760) ** 2 + det(x, 6, 2, 13), wallH: 13, fall: 110,
    houses: clusters(RR, 330, 1220, 22, 30, 13, 17, { tag: (x) => (x < 690 ? 'V3' : 'V4') }), trees: trees(300, 1250, 16, 36, 22),
    posts: [{ id: 'V3', x: 470, h: 12 }, { id: 'V4', x: 905, h: 12 }], stepsE: [[600, 446, 640, 425], [560, 432, 600, 446], [520, 420, 560, 432]], stepW: 5 });
  { const r = cover(D.fogB, 330); const e = E(D.fogB); const L = new Canvas(r, { seed: 271 }), Rr = new Canvas(r, { seed: 272 });
    paintFog(L, { y: (x) => e(458) + 5 * Math.sin(x * 0.011), h: 18, col: hex('#5b5889'), top: hex('#7a76a2'), a: 1, density: 1.5, wisp: 0.8, xEnv: (x) => 1 - smoothstep(540, 740, x) });
    paintFog(Rr, { y: (x) => e(455) + 5 * Math.sin(x * 0.013 + 1), h: 18, col: hex('#5b5889'), top: hex('#7a76a2'), a: 1, density: 1.5, wisp: 0.8, xEnv: (x) => smoothstep(540, 740, x) });
    planes.fogBL = S.plane('fogBL', D.fogB, r, L.c); planes.fogBR = S.plane('fogBR', D.fogB, r, Rr.c); }
  terrace('lower', D.lower, 281, { baseE: (x) => 515 + 0.0001 * (x - 760) ** 2 + det(x, 6, 2, 17), wallH: 20, fall: 150, slopeTop: hex('#1e2141'), slopeBot: hex('#13152c'),
    houses: clusters(RR, 230, 1300, 28, 38, 16, 21, { tag: (x) => (x < 820 ? 'V2' : 'V1') }), trees: trees(220, 1300, 20, 44, 18),
    posts: [{ id: 'V1', x: 1010, h: 15 }, { id: 'V2', x: 640, h: 15 }], stepsE: [[880, 676, 960, 610], [960, 610, 1010, 548], [1010, 548, 1040, 520]], stepW: 7 });
  // --- road: crest band + slope; posts R1..R3 and the gate are drawn crisp in the detail layer
  const eR = E(D.road); const yWalk = (x) => eR(688) - 0.02 * (x - 360) + 1.2 * Math.sin(x * 0.02);
  { const r = cover(D.road); const C = new Canvas(r, { seed: 291 }); const g = C.g; const [x0, , x1, y1] = r;
    const yF = (x) => yWalk(x) - 11, yN = (x) => yWalk(x) + 13;
    const slope = new Path2D(); slope.moveTo(x0 - 10, y1 + 10); for (let x = x0 - 10; x <= x1 + 10; x += 3) slope.lineTo(x, yN(x)); slope.lineTo(x1 + 10, y1 + 10); slope.closePath();
    underpaint(C, (x, y) => mixc(hex('#2b2e4e'), hex('#15172e'), smoothstep(yN(x), yN(x) + 220, y)), slope, 8); const ms = C.mask((gg) => gg.fill(slope));
    C.strokes({ n: C.area / 1200, mask: ms, color: (x, y) => mixc(hex('#2d3050'), hex('#15172e'), smoothstep(yN(x), yN(x) + 220, y)), angle: (x, y) => (nn.fbm(x * 0.012, y * 0.01, 3) > 0.5 ? -0.7 : 0.7) + (C.R() - 0.5) * 0.4, len: [14, 38], wid: [5, 11], alpha: [0.45, 0.8], jv: 0.08 });
    const band = new Path2D(); band.moveTo(x0 - 10, yF(x0 - 10)); for (let x = x0 - 10; x <= x1 + 10; x += 3) band.lineTo(x, yF(x)); for (let x = x1 + 10; x >= x0 - 10; x -= 3) band.lineTo(x, yN(x) + 1); band.closePath();
    const rc = (x, y) => mixc(mixc(hex('#423e5c'), hex('#2c2a43'), smoothstep(yF(x) + 6, yN(x), y)), hex('#565275'), 0.5 * smoothstep(yF(x) + 5, yF(x), y));
    underpaint(C, rc, band, 4); const mb = C.mask((gg) => gg.fill(band));
    C.strokes({ n: C.area / 900, mask: mb, color: rc, angle: () => Math.atan(-0.02) + (C.R() - 0.5) * 0.16, len: [12, 30], wid: [4, 7], alpha: [0.5, 0.85], jv: 0.06 });
    paintTufts(C, { x0, x1, base: (x) => yF(x) + 1, step: 7, h0: 3, h1: 8, col: hex('#191b31'), blades: 4 });
    paintTufts(C, { x0, x1, base: (x) => yN(x) + 2, step: 9, h0: 5, h1: 12, col: hex('#13152a'), blades: 5 });
    for (let i = 0; i < 70; i++) { const x = lerp(x0, x1, C.R()), y = yN(x) + 18 + Math.pow(C.R(), 0.7) * 230; const s = 5 + C.R() * 13; if (C.R() < 0.55) { for (let k = 0; k < 7; k++) { const a = -Math.PI / 2 + (C.R() - 0.5) * 1.5; C.dab(x + Math.cos(a) * s * 0.5, y + Math.sin(a) * s * 0.5, a, s * (0.8 + C.R() * 0.6), Math.max(2, s * 0.22), mul(hex('#14162c'), 0.8 + C.R() * 0.4), 0.85, 0.15, 0.9); } }
      else { C.dab(x, y, -0.25, s * 2.2, s, hex('#191b33'), 0.9, 0.2, 1.0); C.dab(x - s * 0.3, y - s * 0.35, -0.3, s * 1.3, s * 0.3, hex('#34385c'), 0.55, 0.1); } }
    C.mottle({ amt: 0.07 }); planes.road = S.plane('road', D.road, r, C.c); }
  { const r = cover(D.fg); const C = new Canvas(r, { seed: 301 }); const base = (x) => 548 + 30 * Math.sin(x * 0.005 + 1) + det(x, 30, 10, 21);
    const path = new Path2D(); path.moveTo(r[0], r[3] + 10); for (let x = r[0]; x <= r[2]; x += 4) path.lineTo(x, base(x)); path.lineTo(r[2], r[3] + 10); path.closePath(); C.g.fillStyle = rgba(hex('#0b0c1a')); C.g.fill(path);
    const rocks = []; for (let x = r[0] - 60; x < r[2] + 60; x += 170 + C.R() * 170) rocks.push({ x, y: base(x) + 70 + C.R() * 30, rx: 100 + C.R() * 110, ry: 55 + C.R() * 35 });
    paintRocks(C, { rocks, col: hex('#0b0c19'), lit: hex('#2a2f52'), litA: 0.45 });
    paintTufts(C, { x0: r[0], x1: r[2], base: (x) => base(x) + 30, step: 60, h0: 18, h1: 40, col: hex('#0c0d1b'), blades: 6, jitter: 30 });
    C.blur(4); planes.fg = S.plane('fg', D.fg, r, C.c); }

  const chain = TM.s2.chain; const ids = ['R1', 'R2', 'R3', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'];
  const allPosts = [...lights.lower, ...lights.middle, ...lights.upper];
  const vGlows = allPosts.map((p) => { const gm = S.glow(p.x, p.y, p.D, 30 + 1500 / p.D, { color: GLOW, core: 90 }, p.plane); gm.userData.t0 = chain[ids.indexOf(p.id)]; p.world = gm.position.clone(); return gm; });
  const winGlows = windows.map((w, i) => { const RW = rng(500 + i); const m = Math.max(w.w, w.h) * 3.6; const gm = S.glow(w.x, w.y, w.D, m, { color: [1.0, 0.55, 0.24], shape: 1, rect: [w.w / m, w.h / m] }, w.plane);
    gm.userData.t0 = (chain[ids.indexOf(w.lantern)] ?? 99) + 0.12 + RW() * 0.6; gm.userData.lit = RW() < 0.93; return gm; });
  const rGlows = [0, 1, 2].map(() => S.glow(0, 0, D.road, 30, { color: GLOW, core: 100 }, planes.road));
  const handGlow = S.glow(0, 0, D.road, 28, { color: GLOW, core: 110 }, planes.road);
  // light scattered in the evening mist over each terrace: grows as that terrace's lanterns catch (motivated by them)
  const aura = [['lower', D.lower, 760, 470, 1100], ['middle', D.middle, 770, 372, 820], ['upper', D.upper, 770, 282, 560]].map(([k, Dd, x, yE, sz]) => {
    const gm = S.glow(x, E(Dd)(yE), Dd, sz, { color: GLOW, core: 4000 }, planes[k]); gm.userData.key = k; return gm; });
  return {
    setup: S, D, planes, yWalk, chain, ids,
    camera(cam, t) { const [a, b] = TM.s2.crane; const k = ease.inOutSine(clamp((t - a) / (b - a))); const p = pose2(k); cam.position.set(...p.pos); cam.lookAt(...p.look); },
    update(t, { lanternWorld, roadPosts }) {
      const part = ease.inOutSine(clamp((t - 5.0) / 3.7));
      const mv = (pl, dx) => { pl.position.x = pl.userData.base.x + dx * pl.userData.D / f; };
      mv(planes.fogAL, -260 * part - 6 * (t - 4.6)); mv(planes.fogAR, 240 * part - 6 * (t - 4.6)); mv(planes.fogBL, -300 * part - 9 * (t - 4.6)); mv(planes.fogBR, 280 * part - 9 * (t - 4.6));
      for (const p of [planes.fogAL, planes.fogAR, planes.fogBL, planes.fogBR]) p.material.uniforms.uOpacity.value = 1 - 0.35 * part;
      for (const gm of vGlows) gm.material.uniforms.uI.value = 1.75 * igniteEnv(t, gm.userData.t0, gm.userData.t0 * 7);
      for (const gm of winGlows) gm.material.uniforms.uI.value = gm.userData.lit ? 1.2 * smoothstep(gm.userData.t0, gm.userData.t0 + 0.25, t) * flick(t, gm.userData.t0 * 3) : 0;
      roadPosts.forEach((p, i) => { rGlows[i].position.copy(p.world); rGlows[i].material.uniforms.uI.value = 1.4 * igniteEnv(t, chain[i], i + 1); });
      handGlow.position.copy(lanternWorld); handGlow.material.uniforms.uI.value = 1.05 * flick(t, 9);
      const L = (arr) => arr.map((p) => ({ p: p.world, r: 12 * p.D / 125, c: WARM, k: 3.4 * igniteEnv(t, chain[ids.indexOf(p.id)], 3) }));
      setLights(planes.lower.material, L(lights.lower)); setLights(planes.middle.material, L(lights.middle)); setLights(planes.upper.material, L(lights.upper));
      const fogL = (arr) => arr.map((p) => ({ p: p.world, r: 22 * p.D / 125, c: WARM, k: 1.6 * igniteEnv(t, chain[ids.indexOf(p.id)], 3) }));
      for (const k of ['fogAL', 'fogAR']) setLights(planes[k].material, fogL([...lights.middle, ...lights.upper]));
      for (const k of ['fogBL', 'fogBR']) setLights(planes[k].material, fogL([...lights.lower, ...lights.middle]));
      for (const gm of aura) { const ls = lights[gm.userData.key]; const on = ls.reduce((s, p) => s + clamp(igniteEnv(t, chain[ids.indexOf(p.id)], 3), 0, 1), 0) / ls.length; gm.material.uniforms.uI.value = (gm.userData.key === 'upper' ? 0.045 : 0.06) * on; }
      setLights(planes.road.material, [{ p: lanternWorld, r: 1.0, c: WARM, k: 2.2 * flick(t, 9) }, ...roadPosts.map((p, i) => ({ p: p.world, r: 2.2, c: WARM, k: 3.0 * igniteEnv(t, chain[i], i + 1) }))]);
    },
  };
}

// ================================================================== S3 — locked-off MWS at the gate
export function buildS3(TM) {
  const S = new Setup('S3', { pos: [0, 0, 0], mm: 35 }); const f = S.f; const full = (m = 40) => [-m, -m, 1280 + m, 720 + m];
  const D = { sky: 4000, peaks: 1500, village: 300, fog1: 200, near: 60, fog2: 40, ground: 8.6, gate: 8.5, lanternLit: 8.45, fig: 7, tree: 4, fg: 2.5 };
  const planes = {}; const glows = []; const winLights = [];
  { const r = full(); const C = new Canvas(r, { seed: 311 });
    paintSky(C, { stops: [[-40, hex('#0c1030')], [140, hex('#161b44')], [300, hex('#282e5f')], [430, hex('#3f4175')]], glow: { x: -120, y: 420, rx: 520, ry: 160, col: hex('#8a7a9e'), a: 0.35 },
      clouds: [{ y: 96, h: 12, x0: -100, x1: 760, col: hex('#151a43'), lit: hex('#393a70'), litA: 0.55, sy: 0.03 }, { y: 205, h: 10, x0: 200, x1: 1100, col: hex('#242a5a'), lit: hex('#524f82'), litA: 0.6, sy: 0.034 }] });
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = full(); const C = new Canvas(r, { seed: 321 });
    const ridge = (x) => 305 - bump(x, 170, 130, 95) - bump(x, 470, 150, 132) - bump(x, 740, 120, 62) - 26 * ridged(x * 0.007, 4, 8) - 7 * ridged(x * 0.03, 3, 9);
    paintRange(C, { ridge, top: hex('#31365f'), mid: hex('#383d6b'), base: hex('#41447a'), fall: 150, light: { dir: -1, col: hex('#4f5486'), amt: 0.4 }, shade: 0.14, haze: { col: hex('#3f4274'), y0: 270, y1: 350, a: 0.7 }, snow: { y: 222, col: hex('#676893'), amt: 0.6 }, rim: hex('#8b84ad') });
    C.mottle({ amt: 0.05 }); planes.peaks = S.plane('peaks', D.peaks, r, C.c); }
  // upper village climbing to the right (all lit now: the chain has passed)
  { const r = full(); const C = new Canvas(r, { seed: 331 }); const RR = rng(3311);
    paintRange(C, { ridge: (x) => 232 - 150 * smoothstep(350, 1300, x) + det(x, 14, 5, 9), top: hex('#20234a'), mid: hex('#252955'), base: hex('#30335f'), fall: 300, light: { dir: -1, col: hex('#373c70'), amt: 0.3 }, shade: 0.1 });
    for (const [base, x0, x1, w0, w1, h0, h1] of [[(x) => 250 - 120 * smoothstep(560, 1280, x) + det(x, 8, 3, 8), 640, 1300, 22, 30, 12, 16], [(x) => 332 - 120 * smoothstep(380, 1280, x) + det(x, 8, 3, 6), 470, 1300, 28, 40, 15, 21]]) {
      const trees = Array.from({ length: 16 }, () => [lerp(x0 - 30, x1, RR()), 14 + RR() * 30, 0.3, 0]);
      const out = paintTerrace(C, { base, wallH: 9, wall: hex('#353352'), wallTop: hex('#4f4c70'), slopeTop: hex('#1e2146'), slopeBot: hex('#1b1e40'), slopeFall: 80, houses: clusters(RR, x0, x1, w0, w1, h0, h1, { gap: [10, 40] }), trees, houseWall: hex('#353352'), houseRoof: hex('#15162c'), crest: hex('#46497a') });
      for (const h of out.houses) for (const w of h.windows) if (RR() < 0.85) winLights.push([w[0] + w[2] / 2, w[1] + w[3] / 2, w[2], w[3], D.village]);
    }
    C.blur(0.8); planes.village = S.plane('village', D.village, r, C.c); }
  { const r = [-200, 200, 1480, 470]; const C = new Canvas(r, { seed: 341 }); paintFog(C, { y: (x) => 338 - 42 * smoothstep(300, 1280, x), h: 18, col: hex('#4f4d7d'), top: hex('#6c689a'), a: 0.95, density: 1.6, wisp: 0.8 });
    planes.fog1 = S.plane('fog1', D.fog1, r, C.c); planes.fog1.userData.drift = 9; }
  // the lower terrace right behind the gate: houses, stone stair rising from the gate, four stair lanterns (lit)
  const nearLanterns = [];
  { const r = full(); const C = new Canvas(r, { seed: 351 }); const g = C.g; const RR = rng(3511);
    const base = (x) => 470 - 40 * smoothstep(700, 1280, x) + det(x, 5, 2, 12);
    const out = paintTerrace(C, { base, wallH: 46, wall: hex('#3c3956'), wallTop: hex('#5f5b80'), slopeTop: hex('#1f2245'), slopeBot: hex('#181a36'), slopeDensity: 1400, slopeFall: 140,
      houses: [{ x: 640, w: 112, h: 62, roofK: 0.5, z: 0, gable: false }, { x: 772, w: 92, h: 56, roofK: 0.56, z: 1, gable: true }, { x: 1176, w: 128, h: 70, roofK: 0.48, z: 0, gable: false }, { x: 1318, w: 96, h: 60, roofK: 0.56, z: 1, gable: true }],
      trees: [[560, 120, 0.3, 0], [705, 92, 0.3, 0], [1062, 140, 0.32, 0], [1252, 82, 0.3, 0]], houseWall: hex('#3d3a5a'), houseRoof: hex('#17182f'), crest: hex('#4f5180') });
    for (let i = 0; i < 16; i++) { const u = i / 15; const y = lerp(600, base(960) + 4, u), w = lerp(150, 70, u), x = lerp(950, 965, u);
      g.fillStyle = rgba(mul(hex('#37334e'), 0.85 + 0.15 * (i % 2))); g.fillRect(x - w / 2, y - 7, w, 8); C.dab(x, y - 7.5, 0, w * 0.95, 2.2, hex('#4e4a6b'), 0.7, 0.0, 0.2); }
    for (const h of out.houses) for (const w of h.windows) winLights.push([w[0] + w[2] / 2, w[1] + w[3] / 2, w[2], w[3], D.near]);
    for (const [x, ph] of [[870, 52], [1046, 52], [905, 34], [1012, 34]]) { const yb = x < 900 || x > 1040 ? 598 : base(960) + 40; g.fillStyle = rgba(hex('#14111a')); g.fillRect(x - 2.5, yb - ph, 5, ph); g.fillStyle = rgba(hex('#4e4760')); g.fillRect(x - 7, yb - ph - 15, 14, 15); g.fillStyle = rgba(hex('#17131d')); g.fillRect(x - 9, yb - ph - 17, 18, 3); nearLanterns.push([x, yb - ph - 7.5]); }
    C.mottle({ amt: 0.06 }); planes.near = S.plane('near', D.near, r, C.c); }
  // low mist right behind the traveler (separation), thinning toward the gate so the stair stays clear
  { const r = [-200, 330, 1480, 640]; const C = new Canvas(r, { seed: 361 }); paintFog(C, { y: () => 478, h: 52, col: hex('#6a6795'), top: hex('#8a85b2'), a: 0.95, density: 1.8, wisp: 0.55, xEnv: (x) => 1 - smoothstep(720, 900, x) });
    planes.fog2 = S.plane('fog2', D.fog2, r, C.c); planes.fog2.userData.drift = 12; }
  // ground: the road arriving from the left, packed earth before the gate, dark verges
  const groundY = 628;
  { const r = full(); const C = new Canvas(r, { seed: 371 });
    const top = (x) => 596 + 6 * Math.sin(x * 0.01) + det(x, 6, 3, 14);
    const path = new Path2D(); path.moveTo(-60, 780); for (let x = -60; x <= 1340; x += 4) path.lineTo(x, top(x)); path.lineTo(1340, 780); path.closePath();
    const onPath = (x, y) => { const c = lerp(470, 950, smoothstep(720, 600, y)); const w = lerp(560, 190, smoothstep(720, 600, y)); return 1 - smoothstep(w * 0.4, w * 0.56, Math.abs(x - c)); };
    const gc = (x, y) => mixc(mixc(hex('#1b1b31'), hex('#272640'), smoothstep(720, 600, y)), mixc(hex('#3b3853'), hex('#2f2c45'), smoothstep(600, 720, y)), onPath(x, y));
    underpaint(C, gc, path, 6); const m = C.mask((q) => q.fill(path));
    C.strokes({ n: C.area / 900, mask: m, color: gc, angle: (x, y) => (onPath(x, y) > 0.5 ? 0.02 : -0.3) + (C.R() - 0.5) * 0.3, len: [16, 44], wid: [5, 10], alpha: [0.5, 0.85], jv: 0.06 });
    for (let i = 0; i < 220; i++) { const x = lerp(-20, 1300, C.R()), y = lerp(604, 720, Math.sqrt(C.R())); if (onPath(x, y) < 0.6) continue; const s = lerp(2, 5, smoothstep(600, 720, y)); C.dab(x, y, (C.R() - 0.5) * 0.4, s * 1.7, s, C.R() < 0.6 ? hex('#2e2b44') : hex('#56516e'), 0.5, 0.15); }
    paintTufts(C, { x0: -40, x1: 1320, base: (x) => top(x) + 2, step: 10, h0: 6, h1: 16, col: hex('#17182d'), blades: 5 });
    C.mottle({ amt: 0.06 }); planes.ground = S.plane('ground', D.ground, r, C.c); }
  // the gate: timber posts on stone plinths, lintel, small roof; the great lantern hangs from the lintel
  const LAN = { x: 946, y0: 186, y1: 292, w: 80 };
  { const r = full(); const C = new Canvas(r, { seed: 381 }); const g = C.g;
    const post = (xb, xt, yb, yt, w) => { // posts lean in toward the top (low camera looking up)
      g.fillStyle = rgba(hex('#241f2d')); g.beginPath(); g.moveTo(xb - w / 2, yb); g.lineTo(xt - w * 0.44, yt); g.lineTo(xt + w * 0.44, yt); g.lineTo(xb + w / 2, yb); g.closePath(); g.fill();
      C.strokes({ n: 150, box: [Math.min(xb, xt) - w, yt, Math.max(xb, xt) + w, yb], mask: (x, y) => { const u = (y - yt) / (yb - yt); const c = lerp(xt, xb, u), hw = lerp(w * 0.44, w / 2, u); return Math.abs(x - c) < hw - 1 ? 1 : 0; },
        color: (x, y) => { const u = (y - yt) / (yb - yt); const c = lerp(xt, xb, u); return mixc(hex('#272231'), hex('#3d3549'), smoothstep(c + w * 0.1, c - w * 0.5, x) * 0.7); }, angle: () => Math.PI / 2 + (C.R() - 0.5) * 0.06, len: [30, 90], wid: [3, 6], alpha: [0.5, 0.85], jv: 0.08, bend: 0.02 }); };
    post(784, 792, 560, 140, 46); post(1112, 1102, 560, 140, 46);
    for (const [x, w] of [[784, 70], [1112, 70]]) { g.fillStyle = rgba(hex('#37334b')); g.fillRect(x - w / 2, 552, w, 56); C.strokes({ n: 60, box: [x - w / 2, 552, x + w / 2, 608], color: (px, py) => mixc(hex('#3a364f'), hex('#55507a'), smoothstep(608, 552, py) * 0.6), angle: () => (C.R() - 0.5) * 0.3, len: [10, 24], wid: [5, 9], alpha: [0.6, 0.9], jv: 0.1 });
      C.dab(x, 553, 0, w * 0.95, 3, hex('#625d82'), 0.7, 0, 0.2); }
    g.fillStyle = rgba(hex('#241f2d')); g.fillRect(722, 120, 452, 30); C.strokes({ n: 120, box: [722, 120, 1174, 150], color: (x, y) => mixc(hex('#262130'), hex('#3a3249'), smoothstep(150, 120, y) * 0.7), angle: () => (C.R() - 0.5) * 0.05, len: [40, 120], wid: [3, 6], alpha: [0.5, 0.85], jv: 0.07 });
    g.fillStyle = rgba(hex('#19182a')); g.beginPath(); g.moveTo(690, 124); g.lineTo(760, 66); g.lineTo(1136, 66); g.lineTo(1206, 124); g.lineTo(1180, 132); g.lineTo(716, 132); g.closePath(); g.fill();
    C.strokes({ n: 260, box: [690, 64, 1206, 132], mask: (x, y) => { if (y < 66 || y > 131) return 0; const l = 760 - (y - 66) / 58 * 70, rr = 1136 + (y - 66) / 58 * 70; return x > l && x < rr ? 1 : 0; },
      color: (x, y) => mixc(hex('#1b1a2d'), hex('#33345a'), smoothstep(124, 66, y) * 0.6), angle: (x) => (x < 760 ? -0.7 : x > 1136 ? 0.7 : 0.0) + (C.R() - 0.5) * 0.2, len: [10, 26], wid: [4, 8], alpha: [0.6, 0.9], jv: 0.08 });
    C.dab(948, 66, 0, 390, 3.5, hex('#5b5d88'), 0.8, 0.0, 0.2); C.dab(724, 96, -0.69, 86, 3, hex('#4f517c'), 0.6, 0.02, 0.3);
    g.fillStyle = rgba(hex('#16121a')); g.fillRect(LAN.x - 1.5, 150, 3, LAN.y0 - 150 + 4);
    const body = (gg, paper, rib, ribA) => { gg.fillStyle = rgba(hex('#1a1416')); gg.fillRect(LAN.x - LAN.w * 0.42, LAN.y0 - 4, LAN.w * 0.84, 9); gg.fillRect(LAN.x - LAN.w * 0.4, LAN.y1 - 5, LAN.w * 0.8, 9);
      gg.fillStyle = rgba(paper); gg.beginPath(); gg.ellipse(LAN.x, (LAN.y0 + LAN.y1) / 2, LAN.w / 2, (LAN.y1 - LAN.y0) / 2 - 4, 0, 0, Math.PI * 2); gg.fill();
      gg.strokeStyle = rgba(rib, ribA); gg.lineWidth = 2.4; for (let k = -2; k <= 2; k++) { gg.beginPath(); gg.ellipse(LAN.x, (LAN.y0 + LAN.y1) / 2, Math.abs(k) / 2.5 * LAN.w / 2 + 0.5, (LAN.y1 - LAN.y0) / 2 - 4, 0, k < 0 ? Math.PI / 2 : -Math.PI / 2, k < 0 ? Math.PI * 1.5 : Math.PI / 2); gg.stroke(); }
      for (let k = 1; k < 6; k++) { const y = lerp(LAN.y0 + 6, LAN.y1 - 6, k / 6); const hw = LAN.w / 2 * Math.sqrt(Math.max(0, 1 - ((y - (LAN.y0 + LAN.y1) / 2) / ((LAN.y1 - LAN.y0) / 2 - 3)) ** 2)); gg.beginPath(); gg.moveTo(LAN.x - hw, y); gg.lineTo(LAN.x + hw, y); gg.stroke(); } };
    body(g, hex('#4a4356'), hex('#221c28'), 0.7);
    C.mottle({ amt: 0.05 }); planes.gate = S.plane('gate', D.gate, r, C.c);
    const L2 = new Canvas(r, { seed: 382 }); body(L2.g, hex('#f2b56e'), hex('#8a4428'), 0.75);
    const rg = L2.g.createRadialGradient(LAN.x, (LAN.y0 + LAN.y1) / 2 + 6, 3, LAN.x, (LAN.y0 + LAN.y1) / 2, LAN.w * 0.55); rg.addColorStop(0, 'rgba(255,232,190,0.35)'); rg.addColorStop(1, 'rgba(255,170,90,0)');
    L2.g.globalCompositeOperation = 'source-atop'; L2.g.fillStyle = rg; L2.g.fillRect(LAN.x - LAN.w, LAN.y0, LAN.w * 2, LAN.y1 - LAN.y0); planes.lanternLit = S.plane('lanternLit', D.lanternLit, r, L2.c); planes.lanternLit.material.uniforms.uOpacity.value = 0; }
  // the traveler card (per-frame canvas, full frame at his depth)
  const FIG = [300, 270, 820, 720]; // design-px region the traveler, his staff and his long shadow can occupy in S3
  const figCanvas = document.createElement('canvas'); figCanvas.width = FIG[2] - FIG[0]; figCanvas.height = FIG[3] - FIG[1]; const figG = figCanvas.getContext('2d', { willReadFrequently: true });
  planes.fig = S.plane('fig', D.fig, FIG, figCanvas); { const tx = planes.fig.material.uniforms.map.value; tx.generateMipmaps = false; tx.minFilter = THREE.LinearFilter; }
  // a dark pine at the left edge (frames the empty left), out of focus
  { const r = full(120); const C = new Canvas(r, { seed: 386 }); const g = C.g;
    g.fillStyle = rgba(hex('#0b0c18')); g.beginPath(); g.moveTo(-40, 800); g.lineTo(-10, -100); g.lineTo(52, -100); g.lineTo(78, 800); g.closePath(); g.fill();
    for (let k = 0; k < 9; k++) { const y = 40 + k * 70 + C.R() * 30; const len = 60 + C.R() * 90; for (let j = 0; j < 14; j++) { const s = j / 13; C.dab(40 + s * len, y + s * s * 30 + (C.R() - 0.5) * 10, 0.35 + (C.R() - 0.5) * 0.8, 26 + C.R() * 20, 5 + C.R() * 4, mul(hex('#0c0d1a'), 0.85 + C.R() * 0.3), 0.9, 0.2); } }
    C.blur(4); planes.tree = S.plane('tree', D.tree, r, C.c); }
  // foreground: rock at the bottom-left (the title sits on it), bough top-left
  { const r = full(120); const C = new Canvas(r, { seed: 391 });
    paintRocks(C, { rocks: [{ x: 210, y: 772, rx: 300, ry: 70 }, { x: -40, y: 700, rx: 140, ry: 90 }], col: hex('#090a15'), lit: hex('#22264a') });
    C.blur(5); planes.fg = S.plane('fg', D.fg, r, C.c); }
  for (const [x, y, w, h, Dd] of winLights) { const m = Math.max(w, h) * 2.2; const gm = S.glow(x, y, Dd, m, { color: [1.0, 0.55, 0.24], shape: 1, rect: [w / m, h / m] }, Dd === D.village ? planes.village : planes.near); gm.userData.base = 0.65; glows.push(gm); }
  for (const [x, y] of nearLanterns) { const gm = S.glow(x, y, D.near, 60, { color: GLOW, core: 80 }, planes.near); gm.userData.base = 1.2; glows.push(gm); }
  const nearL = nearLanterns.map(([x, y]) => S.world(x, y, D.near));
  const bigGlow = S.glow(LAN.x, (LAN.y0 + LAN.y1) / 2, D.lanternLit, 460, { color: GLOW, core: 4000 }, planes.lanternLit); // halo only: the paper is the source
  const handGlow = S.glow(0, 0, D.fig, 64, { color: GLOW, core: 100 }, planes.fig);
  const lanW = S.world(LAN.x, (LAN.y0 + LAN.y1) / 2, D.lanternLit);
  return {
    setup: S, D, planes, figCanvas, figG, FIG, groundY, LAN, lanW,
    camera(cam) { cam.position.set(0, 0, 0); cam.lookAt(0, 0, -100); },
    update(t, { lanternPx, ign }) {
      for (const k of ['fog1', 'fog2']) { const p = planes[k]; p.position.x = p.userData.base.x - p.userData.drift * (t - 8.8) * p.userData.D / f; }
      glows.forEach((gm, i) => { gm.material.uniforms.uI.value = gm.userData.base * flick(t, i * 1.3); });
      planes.lanternLit.material.uniforms.uOpacity.value = clamp(ign, 0, 1); bigGlow.material.uniforms.uI.value = 0.4 * ign;
      const hw = S.world(lanternPx[0], lanternPx[1], D.fig); handGlow.position.copy(hw); handGlow.material.uniforms.uI.value = 0.55 * flick(t, 9);
      setLights(planes.ground.material, [{ p: lanW, r: 3.8, c: WARM, k: 5.5 * ign }, { p: hw, r: 0.55, c: WARM, k: 2.2 * flick(t, 9) }]);
      setLights(planes.gate.material, [{ p: lanW, r: 2.4, c: WARM, k: 4.0 * ign }]);
      setLights(planes.near.material, nearL.map((p, i) => ({ p, r: 2.6, c: WARM, k: 2.2 * flick(t, i + 20) })));
      planes.fig.material.uniforms.map.value.needsUpdate = true;
    },
  };
}
