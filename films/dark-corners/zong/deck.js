// The night deck: moonlit sea beyond a bulwark with one open gap, a lantern swinging from a davit, casks, chain. Absence and light.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, rng, valueNoise2D } from '/harness/kit/film.js';
import { Setup, setLights, DW, DH } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, paintSky, underpaint } from './paint.js';
import { WARM, GLOW, coverCams, flick, drawLantern, line } from './common.js';
import { MOODS, paintWater } from './sea.js';

export const DK = { yh: 600, rail: 790, floor: 1010, gap: [380, 530], pivot: [292, 300], L: 230, moon: [560, 230] };
const DE = { wall: 24, deck: 20, mast: 8, casksB: 18, casksF: 15, lant: 14 };

function paintCask(C, cx, yb, w, h, P) {
  const g = C.g, R = C.R; const ry = w * 0.17, topY = yb - h; const col = hex(P.col || '#2b2320');
  const body = new Path2D(); body.moveTo(cx - w * 0.41, topY); body.bezierCurveTo(cx - w * 0.56, topY + h * 0.3, cx - w * 0.56, yb - h * 0.3, cx - w * 0.42, yb); body.lineTo(cx + w * 0.42, yb); body.bezierCurveTo(cx + w * 0.56, yb - h * 0.3, cx + w * 0.56, topY + h * 0.3, cx + w * 0.41, topY); body.closePath();
  const colAt = (x, y) => { const u = (x - cx) / (w * 0.56); return mixc(mixc(hex(P.lit || '#5a4a40'), col, smoothstep(-0.9, 0.2, u)), mul(col, 0.55), smoothstep(0.2, 1, u)); };
  underpaint(C, colAt, body, 4); const m = C.mask((gg) => gg.fill(body));
  C.strokes({ n: w * h / 38, box: [cx - w * 0.6, topY, cx + w * 0.6, yb], mask: m, minMask: 0.6, color: colAt, angle: () => Math.PI / 2 + (R() - 0.5) * 0.1, len: [h * 0.18, h * 0.5], wid: [3, 6], alpha: [0.35, 0.6], jv: 0.1, bend: 0.03 });
  for (let k = 1; k < 9; k++) { const x = cx - w * 0.5 + k * w / 9; C.dab(x, (topY + yb) / 2, Math.PI / 2, h * 0.92, 1.4, mul(col, 0.45), 0.5, 0.06, 0.2); }
  for (const hy of [0.14, 0.34, 0.66, 0.86]) { const y = topY + h * hy; const half = w * (0.4 + 0.15 * Math.sin(Math.PI * hy)); g.strokeStyle = rgba(hex('#0b0b14')); g.lineWidth = Math.max(3, h * 0.04); g.beginPath(); g.ellipse(cx, y, half, ry * 0.8, 0, 0.05, Math.PI - 0.05); g.stroke(); C.dab(cx - half * 0.35, y + ry * 0.7, 0, half * 0.7, 1.6, hex('#6d7aa5'), 0.4, 0.0, 0.4); }
  // open lid: dark interior ellipse with a thin rim
  g.fillStyle = rgba(hex('#04060d')); g.beginPath(); g.ellipse(cx, topY, w * 0.41, ry, 0, 0, Math.PI * 2); g.fill(); g.strokeStyle = rgba(hex(P.rim || '#8fa1d4'), 0.55); g.lineWidth = 2.2; g.beginPath(); g.ellipse(cx, topY, w * 0.41, ry, 0, Math.PI, Math.PI * 2); g.stroke();
  for (let k = 0; k < 7; k++) C.dab(cx - w * 0.38 + R() * w * 0.4, topY - ry * 0.9 + R() * 2, 0, 8 + R() * 14, 1.6, hex('#9fb0e0'), 0.45, 0.04);
  return { cx, topY, rx: w * 0.41, ry, yb, w, h };
}


// ---- chain: oval links alternating face-on / edge-on along a path, steel in shadow, warm glints toward the lantern
function links(g, pts, size, lantern, fl) {
  g.lineCap = 'round';
  for (let i = 0; i + 1 < pts.length; i++) { const a = pts[i], b = pts[i + 1]; const ang = Math.atan2(b[1] - a[1], b[0] - a[0]); const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
    const d = Math.hypot(mx - lantern[0], my - lantern[1]); const lit = clamp(1.3 - d / (size * 70), 0, 1) * fl; const face = i % 2 === 0;
    g.save(); g.translate(mx, my); g.rotate(ang);
    const rx = size * (face ? 0.95 : 0.7), ry = size * (face ? 0.58 : 0.24);
    g.strokeStyle = rgba(mixc([20, 24, 40], [92, 70, 52], lit * 0.6)); g.lineWidth = size * 0.3; g.beginPath(); g.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2); g.stroke();
    g.strokeStyle = rgba(mixc([96, 116, 170], [255, 196, 120], lit), 0.35 + 0.55 * lit); g.lineWidth = Math.max(1, size * 0.08); g.beginPath(); g.ellipse(0, -size * 0.04, rx * 0.95, ry * 0.9, 0, Math.PI * 1.1, Math.PI * 1.9); g.stroke();
    g.restore(); }
}
function cuff(g, x, y, r, rot, open, lit) {
  g.save(); g.translate(x, y); g.rotate(rot); g.lineCap = 'round';
  g.strokeStyle = rgba(mixc([22, 26, 44], [96, 74, 54], lit * 0.6)); g.lineWidth = r * 0.34; g.beginPath(); g.arc(0, 0, r, open, Math.PI * 2 - open); g.stroke();
  g.strokeStyle = rgba(mixc([100, 120, 176], [255, 200, 130], lit), 0.35 + 0.5 * lit); g.lineWidth = Math.max(1, r * 0.08); g.beginPath(); g.arc(0, -r * 0.04, r * 0.96, Math.PI * 1.15, Math.PI * 1.85); g.stroke();
  g.fillStyle = rgba(mixc([18, 21, 36], [80, 62, 48], lit * 0.6)); g.fillRect(r * 0.9, -r * 0.34, r * 0.5, r * 0.68); g.restore();
}
function drawChain(g, e, P, sh, lp, sc) {
  const { t } = e; const lantern = P(lp.x, lp.y + 20); const fl = flick(t, 2) * (sh.lanternK ?? 1);
  if (sh.chainMode === 'coil') { // chain coiled on the deck, a pair of open cuffs at its end
    const pts = []; for (let a = 0; a < 3.4 * Math.PI; a += 0.19) { const r = (46 + 15 * a) * sh.chainScale; pts.push(P(sh.chainAt[0] + r * Math.cos(a), sh.chainAt[1] + r * Math.sin(a) * 0.26, 13)); }
    const tail = []; const last = pts[pts.length - 1]; for (let k = 1; k <= 12; k++) tail.push([last[0] + k * 28 * sc * 0.9, last[1] + Math.sin(k * 0.7) * 5 * sc + k * 3 * sc]);
    const size = 13 * sc * sh.chainScale; links(g, [...pts, ...tail], size, lantern, fl);
    const c0 = tail[tail.length - 1]; cuff(g, c0[0] + 20 * sc, c0[1] + 4 * sc, 22 * sc * sh.chainScale, 0.2, 0.5, clamp(1.1 - Math.hypot(c0[0] - lantern[0], c0[1] - lantern[1]) / 600, 0, 1) * fl); cuff(g, c0[0] + 62 * sc, c0[1] + 10 * sc, 20 * sc * sh.chainScale, -0.1, 0.45, 0.2);
  } else if (sh.chainMode === 'hang') { // chain hanging from the post at the open gap, swaying, an open cuff on its end
    const [x0, y0] = [DK.gap[1] + 8, 718]; const n = 17; const pts = []; const sway = (s) => (Math.sin(t * 1.15 + 0.5) * 22 + Math.sin(t * 2.3) * 4) * s * s;
    for (let k = 0; k <= n; k++) { const s = k / n; pts.push(P(x0 - 18 * s + sway(s), y0 + s * 190, 22)); }
    const size = 12 * sc * 0.9; links(g, pts, size, lantern, fl); const end = pts[pts.length - 1]; cuff(g, end[0] + 4 * sc, end[1] + 20 * sc, 22 * sc * 0.9, Math.sin(t * 1.15 + 0.5) * 0.18, 0.55, 0.5 * fl);
  }
}

export function buildDeck(shots) {
  const S = new Setup('deck', { pos: [0, 0, 0], mm: 35 }); const f = S.f; const cams = coverCams(shots, 'deck'); const cover = (D, m) => S.cover(D, cams, m);
  const M = MOODS.moon; const planes = {}; const dy = DK.yh - 740; const [GX0, GX1] = DK.gap;
  { const r = cover(9000, 40); const C = new Canvas(r, { seed: 1101 });
    paintSky(C, { stops: M.sky.map(([y, c]) => [y + dy, hex(c)]), glow: { ...M.glow, y: DK.moon[1], x: DK.moon[0], col: hex(M.glow.col) }, clouds: M.clouds.map((c) => ({ ...c, y: c.y + dy * 0.4, col: hex(c.col), lit: hex(c.lit) })), n: 0.9 });
    for (let i = 0; i < 200; i++) { const x = lerp(r[0], r[2], C.R()), y = lerp(r[1], 520, Math.pow(C.R(), 1.3)); C.dab(x, y, 0, 2 + C.R() * 2, 1.4 + C.R(), [210, 222, 255], 0.35 + C.R() * 0.5, 0, 0.5); }
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', 9000, r, C.c); }
  const water = [['w0', 3600, 0, 1.5, 0.5, 70, M.water.far, 0.5], ['w1', 900, 18, 4, 0.7, 110, [M.water.far[1], M.water.mid[0]], 0.8], ['w2', 320, 70, 8, 1.0, 190, M.water.mid, 1.0]];
  water.forEach(([key, Dd, d0, amp, k, fall, c, gA], i) => { const r0 = cover(Dd, 40); const top0 = DK.yh + d0; const r = [r0[0], Math.max(r0[1], top0 - amp - 30), r0[2], Math.max(r0[3], top0 + (key === 'w2' ? 700 : 260))];
    const C = new Canvas(r, { seed: 1110 + i }); paintWater(C, { top0, amp, k, fall: key === 'w2' ? 420 : fall, c, seed: 5 + i, glit: key === 'w0' ? null : { ...M.glit, x: DK.moon[0] - 10, w: 16 + k * 10, widen: 0.1, a: M.glit.a * gA }, lit: M.glit.col, contrast: 0.7, skyc: M.sky[M.sky.length - 2][1] });
    C.mottle({ amt: 0.04 }); const pl = S.plane(key, Dd, r, C.c); pl.userData.amp = k; planes[key] = pl; });
  // bulwark wall with an open gap; top rail; posts
  { const r = cover(DE.wall, 60); const C = new Canvas(r, { seed: 1120 }); const g = C.g, R = C.R, n = C.n; const [x0, , x1] = r;
    const top = (x) => DK.rail + 8 * Math.sin(x * 0.004 + 1) + (n.fbm(x * 0.01, 2, 3) - 0.5) * 6;
    const path = new Path2D(); path.moveTo(x0 - 10, DK.floor + 30); path.lineTo(x0 - 10, top(x0 - 10)); for (let x = x0 - 10; x <= GX0; x += 6) path.lineTo(x, top(x)); path.lineTo(GX0, DK.floor + 30); path.lineTo(GX1, DK.floor + 30); path.lineTo(GX1, top(GX1)); for (let x = GX1; x <= x1 + 10; x += 6) path.lineTo(x, top(x)); path.lineTo(x1 + 10, DK.floor + 30); path.closePath();
    const col = (x, y) => mixc(hex('#1d2140'), hex('#0b0d1c'), smoothstep(top(x), DK.floor, y));
    underpaint(C, col, path, 6); const m = C.mask((gg) => gg.fill(path));
    C.strokes({ n: C.area / 700, mask: m, color: col, angle: () => Math.PI / 2 + (R() - 0.5) * 0.08, len: [30, 120], wid: [4, 9], alpha: [0.4, 0.7], jv: 0.08, bend: 0.02 });
    for (let x = x0; x < x1; x += 46 + R() * 10) { if (x > GX0 - 6 && x < GX1 + 6) continue; C.dab(x, (top(x) + DK.floor) / 2, Math.PI / 2, DK.floor - top(x), 2.2, hex('#06070f'), 0.7, 0.01, 0.1); }
    // the rail beam (lit on its upper face by the moon) and edge of the gap
    for (const [a, b] of [[x0 - 10, GX0], [GX1, x1 + 10]]) { g.fillStyle = rgba(hex('#171b34')); g.beginPath(); g.moveTo(a, top(a) - 18); for (let x = a; x <= b; x += 6) g.lineTo(x, top(x) - 18); for (let x = b; x >= a; x -= 6) g.lineTo(x, top(x) + 6); g.closePath(); g.fill();
      for (let x = a; x < b; x += 5 + R() * 5) C.dab(x, top(x) - 17, 0, 14 + R() * 14, 2.4, hex('#8fa6dc'), 0.45 + R() * 0.3, 0.02, 0.5); }
    for (const x of [GX0 - 8, GX1 + 8]) { g.fillStyle = rgba(hex('#0f1226')); g.fillRect(x - 11, top(x) - 70, 22, 80); C.dab(x - 8, top(x) - 34, Math.PI / 2, 60, 2.2, hex('#8fa6dc'), 0.45, 0, 0.2); }
    for (const x of [90, 640, 700]) { if (x < GX0 - 20 || x > GX1 + 20) { g.fillStyle = rgba(hex('#0f1226')); g.fillRect(x - 9, top(x) - 56, 18, 64); C.dab(x - 6, top(x) - 28, Math.PI / 2, 48, 2, hex('#8fa6dc'), 0.4, 0, 0.2); } }
    C.mottle({ amt: 0.05 }); planes.wall = S.plane('wall', DE.wall, r, C.c); }
  // deck floor in perspective
  { const r = cover(DE.deck, 60); const C = new Canvas(r, { seed: 1130 }); const g = C.g, R = C.R, n = C.n; const [x0, y0, x1, y1] = r; const VP = [DW / 2 + 40, 520];
    const topE = (x) => DK.floor - 4 + (n.fbm(x * 0.02, 5, 3) - 0.5) * 5;
    const path = new Path2D(); path.moveTo(x0 - 10, y1 + 10); for (let x = x0 - 10; x <= x1 + 10; x += 6) path.lineTo(x, topE(x)); path.lineTo(x1 + 10, y1 + 10); path.closePath();
    const col = (x, y) => mixc(hex('#262a48'), hex('#10131f'), smoothstep(DK.floor, y1, y)); underpaint(C, col, path, 8); const m = C.mask((gg) => gg.fill(path));
    C.strokes({ n: C.area / 900, mask: m, color: col, angle: (x, y) => Math.atan2(y - VP[1], x - VP[0]) * 0.0 + (R() - 0.5) * 0.05, len: [40, 140], wid: [4, 8], alpha: [0.35, 0.6], jv: 0.08, bend: 0.02 });
    for (let k = -8; k <= 8; k++) { const xb = DW / 2 + k * 118; for (let s = 0; s < 1; s += 0.015) { const y = lerp(DK.floor, y1, s); const x = lerp(VP[0] + (xb - VP[0]) * (DK.floor - VP[1]) / (y1 - VP[1]), xb, s); C.dab(x, y, Math.atan2(y1 - VP[1], xb - VP[0]), 14 + s * 40, 1.8 + s * 2.6, hex('#04050a'), 0.85, 0.02, 0.4); C.dab(x + 2.4, y, Math.atan2(y1 - VP[1], xb - VP[0]), 12 + s * 36, 1.0 + s * 1.1, hex('#5c6a98'), 0.3, 0.02, 0.4); } }
    for (let y = DK.floor + 24; y < y1; y += 70 + R() * 40) for (let x = x0; x < x1; x += 90 + R() * 80) C.dab(x, y, (R() - 0.5) * 0.1, 8 + R() * 18, 2.2, hex('#07080f'), 0.4, 0, 0.5);
    for (let x = x0; x < x1; x += 5 + R() * 6) C.dab(x, topE(x) + 1, 0, 12 + R() * 14, 2.0, hex('#6b7cae'), 0.35 + R() * 0.3, 0.02, 0.5);
    C.mottle({ amt: 0.05 }); planes.deck = S.plane('deck', DE.deck, r, C.c); }
  // casks: back row and front row
  const casks = { back: [], front: [] };
  { const r = cover(DE.casksB, 60); const C = new Canvas(r, { seed: 1140 }); for (const [cx, yb, w, h] of [[430, 1062, 120, 128], [560, 1060, 124, 132], [690, 1064, 118, 126]]) casks.back.push(paintCask(C, cx, yb, w, h, { col: '#2a2224', lit: '#4d4452' })); C.mottle({ amt: 0.05 }); planes.casksB = S.plane('casksB', DE.casksB, r, C.c); }
  { const r = cover(DE.casksF, 60); const C = new Canvas(r, { seed: 1141 }); for (const [cx, yb, w, h] of [[206, 1196, 150, 160], [378, 1204, 156, 164], [552, 1198, 150, 160]]) casks.front.push(paintCask(C, cx, yb, w, h, { col: '#2e2523', lit: '#56495a' }));
    // spigot on the middle front cask + a tin cup on the deck
    const c1 = casks.front[1]; const g = C.g; g.fillStyle = rgba(hex('#0e0c10')); g.fillRect(c1.cx + 6, c1.yb - 52, 34, 9); g.fillRect(c1.cx + 36, c1.yb - 52, 8, 20); C.dab(c1.cx + 22, c1.yb - 52, 0, 28, 1.6, hex('#a8b4d8'), 0.6, 0, 0.3);
    g.fillStyle = rgba(hex('#10111c')); g.beginPath(); g.moveTo(c1.cx + 14, c1.yb + 16); g.lineTo(c1.cx + 62, c1.yb + 16); g.lineTo(c1.cx + 58, c1.yb + 44); g.lineTo(c1.cx + 18, c1.yb + 44); g.closePath(); g.fill(); C.dab(c1.cx + 38, c1.yb + 16, 0, 46, 2, hex('#9fb0e0'), 0.55, 0, 0.3); casks.cup = [c1.cx + 38, c1.yb + 18]; casks.spigot = [c1.cx + 40, c1.yb - 31];
    C.mottle({ amt: 0.05 }); planes.casksF = S.plane('casksF', DE.casksF, r, C.c); }
  // the mast (left), shrouds, and the davit that carries the lantern
  { const r = cover(DE.mast, 60); const C = new Canvas(r, { seed: 1150 }); const g = C.g, R = C.R; const [x0, y0, x1, y1] = r;
    const tr = new Path2D(); tr.moveTo(-12, y1 + 10); tr.lineTo(-6, y0 - 10); tr.lineTo(88, y0 - 10); tr.lineTo(96, y1 + 10); tr.closePath(); const col = (x, y) => mixc(hex('#141830'), hex('#06070f'), smoothstep(-10, 96, x));
    underpaint(C, col, tr, 6); const mk = C.mask((gg) => gg.fill(tr)); C.strokes({ n: 260, mask: mk, color: col, angle: () => Math.PI / 2 + (R() - 0.5) * 0.05, len: [80, 260], wid: [5, 11], alpha: [0.4, 0.7], bend: 0.02 });
    for (let y = y0; y < y1; y += 60 + R() * 30) { g.fillStyle = rgba(hex('#0a0b16')); g.fillRect(-10, y, 106, 8); C.dab(-4, y + 1, 0, 70, 1.8, hex('#8fa6dc'), 0.4, 0, 0.3); }
    for (let y = y0; y < y1; y += 5 + R() * 6) C.dab(2 + R() * 4, y, Math.PI / 2, 14 + R() * 20, 2.4, hex('#7f94cc'), 0.35 + R() * 0.3, 0.02, 0.4);
    // davit arm
    g.strokeStyle = rgba(hex('#0a0b16')); g.lineWidth = 11; g.lineCap = 'round'; g.beginPath(); g.moveTo(80, DK.pivot[1] + 30); g.lineTo(DK.pivot[0], DK.pivot[1]); g.stroke(); g.lineWidth = 6; g.beginPath(); g.moveTo(80, DK.pivot[1] + 120); g.lineTo(DK.pivot[0] - 30, DK.pivot[1] + 8); g.stroke();
    C.dab(150, DK.pivot[1] + 8, -0.12, 120, 2.2, hex('#8fa6dc'), 0.4, 0, 0.3);
    // shrouds fanning out to the rail (soft lines)
    for (let k = 0; k < 6; k++) { g.strokeStyle = rgba(hex('#0a0b16'), 0.85); g.lineWidth = 2.4; g.beginPath(); g.moveTo(84, 120 + k * 22); g.lineTo(190 + k * 46, DK.rail - 4); g.stroke(); }
    for (let k = 0; k < 12; k++) { const t = 0.06 + k * 0.075; const ya = lerp(120, DK.rail, t), yb2 = lerp(142 + 5 * 22, DK.rail, t); const xa = lerp(84, 190, t), xb = lerp(84 + 0, 190 + 5 * 46, t); g.strokeStyle = rgba(hex('#0a0b16'), 0.6); g.lineWidth = 1.8; g.beginPath(); g.moveTo(xa + 2, lerp(120, DK.rail - 4, t)); g.lineTo(lerp(84, 190 + 5 * 46, t) - 2, lerp(120 + 5 * 22, DK.rail - 4, t)); g.stroke(); }
    C.blur(1.2); planes.mast = S.plane('mast', DE.mast, r, C.c); }
  // tints: everything is moonlit blue; the lantern warms it
  for (const k of ['wall', 'deck', 'casksB', 'casksF', 'mast']) planes[k].material.uniforms.uTint.value.set(1, 1, 1);
  const moon = S.glow(DK.moon[0], DK.moon[1], 8500, 200, { color: [0.62, 0.74, 1.0], core: 40 }, planes.sky); moon.material.uniforms.uI.value = 0.95;
  const aura = S.glow(0, 0, DE.lant, 950, { color: [1.0, 0.55, 0.22], core: 5000 }); aura.renderOrder = 1e6 - DE.lant * 10 - 0.6; const lg1 = S.glow(0, 0, DE.lant, 160, { color: GLOW, core: 40 }); const lg2 = S.glow(0, 0, DE.lant, 56, { color: [1, 0.86, 0.6], core: 30 }); lg1.renderOrder = 1e6 - DE.lant * 10 + 0.5; lg2.renderOrder = lg1.renderOrder + 0.1;
  const rainR = rng(1190); const drops = Array.from({ length: 420 }, () => ({ x: rainR() * 900 - 90, y: rainR() * 1500, s: 0.7 + rainR() * 0.8, l: 40 + rainR() * 70 }));
  const lanternPx = (t, sh) => { const A = sh.swing ?? 0.25, w = 2 * Math.PI / (sh.period ?? 3.4); const th = A * Math.sin(w * t) * Math.exp(-0.0 * t) + 0.04 * Math.sin(w * 2.3 * t + 1); const [px, py] = DK.pivot; return { th, x: px + Math.sin(th) * DK.L, y: py + Math.cos(th) * DK.L }; };
  const api = {
    key: 'deck', S, planes, casks, cams,
    show(v) { S.group.visible = v; },
    update(t, sh) {
      for (const k of ['w0', 'w1', 'w2']) { const p = planes[k]; const ph = k.charCodeAt(1) * 1.7; const a = p.userData.amp; const sc = p.userData.D / f; p.position.x = p.userData.base.x + (Math.sin(t * 0.3 + ph) * 4 * a + t * 0.4 * a) * sc; p.position.y = p.userData.base.y + Math.sin(t * 0.5 + ph) * 2 * a * sc; }
      const lp = lanternPx(t, sh); const lw = S.world(lp.x, lp.y, DE.lant); lg1.position.copy(lw); lg2.position.copy(lw); aura.position.copy(lw); aura.material.uniforms.uI.value = 0.07 * flick(t, 2) * (sh.lanternK ?? 1); const fl = flick(t, 2) * (sh.lanternK ?? 1); lg1.material.uniforms.uI.value = 1.0 * fl; lg2.material.uniforms.uI.value = 0.85 * fl;
      moon.material.uniforms.uI.value = 0.8 * (sh.moonK ?? 1);
      const L = (D, d, r, k) => [{ p: new THREE.Vector3(lw.x, lw.y, -D + d), r, c: WARM, k: k * fl }];
      setLights(planes.wall.material, L(DE.wall, 2.6, 4.4, 4.2)); setLights(planes.deck.material, L(DE.deck, 2.2, 4.6, 4.8)); setLights(planes.casksB.material, L(DE.casksB, 1.8, 3.6, 4.0)); setLights(planes.casksF.material, L(DE.casksF, 1.6, 3.2, 4.4)); setLights(planes.mast.material, L(DE.mast, 1.8, 3.2, 3.6));
      planes.casksB.visible = planes.casksF.visible = sh.casksOn !== false;
    },
    draw(g, e) {
      const { t, sh, project } = e; const lp = lanternPx(t, sh); const fl = flick(t, 2) * (sh.lanternK ?? 1);
      const P = (x, y, D = DE.lant) => project(...S.world(x, y, D).toArray());
      // chain + lantern (crisp, swinging)
      const [px, py] = DK.pivot; const a = P(px, py), b = P(lp.x, lp.y - 24); line(g, a, b, 2.2, hex('#0a0a12'), 0.95);
      const scale = (P(0, 0)[0] - P(100, 0)[0]) / -100; const sc = Math.abs(scale);
      const c = P(lp.x, lp.y + 20); drawLantern(g, c[0], c[1], 62 * sc, 1.0 * fl, lp.th * 0.5);
      // casks: water surface + drops
      const cw = sh.casks; if (cw) { const all = [...casks.back.map((c, i) => ({ ...c, D: DE.casksB, i: 3 + i })), ...casks.front.map((c, i) => ({ ...c, D: DE.casksF, i }))];
        for (const ck of all) { const lvl = cw.level(t, ck.i); if (lvl < 0) continue; const q = P(ck.cx, ck.topY + ck.ry * 0.15, ck.D); const q2 = P(ck.cx + ck.rx, ck.topY, ck.D); const rx = Math.abs(q2[0] - q[0]) * 0.92, ry = rx * (ck.ry / ck.rx);
          // the water surface sits below the lid: ellipse shrinks into the barrel as it empties; brighter as it fills
          const dep = (1 - lvl) * 0.8; g.save(); g.beginPath(); g.ellipse(q[0], q[1], rx * 0.99, ry * 0.99, 0, 0, Math.PI * 2); g.clip();
          g.fillStyle = rgba(mixc([6, 9, 20], [58, 78, 128], lvl), 0.95); g.beginPath(); g.ellipse(q[0], q[1] + ry * dep * 0.9, rx * (1 - dep * 0.18), ry * (1 - dep * 0.18), 0, 0, Math.PI * 2); g.fill();
          if (lvl > 0.05) { const glint = lvl * lvl * 1.2; g.fillStyle = `rgba(190,205,255,${(glint * 0.55).toFixed(3)})`; g.beginPath(); g.ellipse(q[0] + rx * 0.2, q[1] + ry * dep * 0.9 - ry * 0.1, rx * 0.34, ry * 0.2, 0, 0, Math.PI * 2); g.fill();
            if (cw.ripples) for (let k = 0; k < 3; k++) { const ph = ((t * 1.7 + ck.i * 0.37 + k / 3) % 1); g.strokeStyle = `rgba(200,215,255,${(0.35 * (1 - ph)).toFixed(3)})`; g.lineWidth = 1.4; g.beginPath(); g.ellipse(q[0] + (k - 1) * rx * 0.4, q[1] + ry * dep * 0.9, rx * 0.5 * ph, ry * 0.5 * ph, 0, 0, Math.PI * 2); g.stroke(); } }
          g.restore(); } }
      // a slow drip from the spigot into the tin cup: the bead takes longer to swell each time
      if (sh.drips) { const sp = P(...casks.spigot, DE.casksF), cp = P(...casks.cup, DE.casksF); const sz = Math.abs(P(10, 0, DE.casksF)[0] - P(0, 0, DE.casksF)[0]) / 10;
        sh.drips.forEach(([ts, gw]) => { const age = t - ts;
          if (age > -gw && age < 0) { const k = (age + gw) / gw; const r = 1.2 + 3.2 * Math.pow(k, 1.6); g.fillStyle = 'rgba(180,200,250,0.92)'; g.beginPath(); g.ellipse(sp[0], sp[1] + r * sz * 0.9, r * sz * 0.8, r * sz * (1.0 + 0.45 * k), 0, 0, 6.3); g.fill(); g.fillStyle = 'rgba(255,236,200,0.8)'; g.beginPath(); g.arc(sp[0] - r * sz * 0.2, sp[1] + r * sz * 0.5, r * sz * 0.22, 0, 6.3); g.fill(); }
          else if (age >= 0 && age < 0.34) { const fall = Math.pow(age / 0.34, 2); const yy = sp[1] + 6 * sz + (cp[1] - sp[1] - 8 * sz) * fall; g.fillStyle = 'rgba(190,210,255,0.9)'; g.beginPath(); g.ellipse(sp[0], yy, 2.2 * sz, 3.6 * sz, 0, 0, 6.3); g.fill(); }
          else if (age >= 0.34 && age < 1.1) { const k = (age - 0.34) / 0.76; g.strokeStyle = `rgba(200,215,255,${(0.75 * (1 - k)).toFixed(3)})`; g.lineWidth = 1.6; g.beginPath(); g.ellipse(cp[0], cp[1] + 1 * sz, 4 * sz + 9 * sz * k, 1.4 * sz + 3 * sz * k, 0, 0, 6.3); g.stroke(); } }); }
      if (sh.chainMode) drawChain(g, e, P, sh, lp, sc);
      // rain
      if (sh.rain) { const k = sh.rain(t); if (k > 0) { g.lineCap = 'round'; for (const d of drops) { const y = ((d.y + t * 1500 * d.s) % 1500) - 150, x = d.x - (y * 0.18); if (!(x > -20 && x < 740)) continue; g.strokeStyle = `rgba(190,205,240,${(0.22 * k * d.s).toFixed(3)})`; g.lineWidth = 1.1 * d.s; g.beginPath(); g.moveTo(x, y); g.lineTo(x - d.l * 0.18, y + d.l); g.stroke(); } } }
    },
  };
  S.group.visible = false; return api;
}
