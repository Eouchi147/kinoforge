// The sea set: sky, a stack of painted swell bands, the ship (hull, masts, sails), the stern lantern. Moods: dusk, moon, dawn.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, noise1, rng, valueNoise2D } from '/harness/kit/film.js';
import { Setup, setLights, DW, DH } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, paintSky, underpaint } from './paint.js';
import { WARM, GLOW, coverCams, flick, wob } from './common.js';
import { buildExtras } from './seaextra.js';

export const YH = 740; // horizon (design px)
const nz = valueNoise2D(311);

export const MOODS = {
  dusk: {
    sky: [[-300, '#241f55'], [60, '#3b3270'], [260, '#7b5a8c'], [430, '#c8808a'], [590, '#f0a06a'], [690, '#ffc078'], [YH, '#ffd9a0']],
    glow: { x: 150, y: 718, rx: 440, ry: 240, col: '#ffd39a', a: 0.85 }, sun: { x: 150, y: 712, col: [1.0, 0.7, 0.36], size: 230, I: 1.0 },
    clouds: [{ y: 150, h: 30, x0: -300, x1: 1100, col: '#4a3d7c', lit: '#c58796', litA: 0.55, sy: 0.02 }, { y: 330, h: 26, x0: -100, x1: 1100, col: '#8a5f8c', lit: '#f4a674', litA: 0.8, sy: 0.026, thr: 0.5 },
      { y: 470, h: 20, x0: -300, x1: 1100, col: '#b6738b', lit: '#ffc784', litA: 0.85, sy: 0.034, thr: 0.5 }, { y: 600, h: 14, x0: 200, x1: 1100, col: '#d58a7c', lit: '#ffd496', litA: 0.8, sy: 0.04, thr: 0.52 }],
    water: { far: ['#f6c58c', '#c8908e'], mid: ['#a67a96', '#5a4573'], near: ['#47395e', '#251d3f'], fg: ['#1c1633', '#120f26'] }, glit: { col: '#ffd9a4', a: 0.9, x: 150 },
    hull: '#150f1c', hullLit: '#5a3d52', rim: '#ffb870', sailLit: '#eaa87c', sailMid: '#b87388', sailShade: '#6e4a80', mast: '#120c1a', lantern: 0.8,
    lights: false },
  moon: {
    sky: [[-300, '#050819'], [120, '#0a1230'], [420, '#162452'], [640, '#26376a'], [YH, '#3e5086']],
    glow: { x: 520, y: 360, rx: 360, ry: 330, col: '#7d93c4', a: 0.6 }, moonD: { x: 520, y: 360 }, sun: { x: 520, y: 360, col: [0.62, 0.74, 1.0], size: 170, I: 1.1 },
    clouds: [{ y: 250, h: 24, x0: -300, x1: 1000, col: '#0c1536', lit: '#4a5f96', litA: 0.65, sy: 0.022, thr: 0.5 }, { y: 470, h: 20, x0: 200, x1: 1100, col: '#16224a', lit: '#6b80b8', litA: 0.7, sy: 0.03, thr: 0.5 }, { y: 120, h: 28, x0: -300, x1: 700, col: '#080d26', lit: '#27386c', litA: 0.5, sy: 0.02 }],
    water: { far: ['#4c608f', '#26335e'], mid: ['#1c2a55', '#0f1938'], near: ['#0e1735', '#080e22'], fg: ['#070b1c', '#050816'] }, glit: { col: '#cfdcff', a: 0.85, x: 520 },
    hull: '#0a0c1c', hullLit: '#2e3d70', rim: '#8fa6dc', sailLit: '#7d92c6', sailMid: '#4f629c', sailShade: '#2a3868', mast: '#080a18', lantern: 1.0, lights: true },
  dawn: {
    sky: [[-300, '#34436a'], [100, '#5a6a92'], [330, '#9a97b4'], [520, '#d8b3a2'], [680, '#f3cba0'], [YH, '#ffe0b4']],
    glow: { x: 520, y: 725, rx: 480, ry: 200, col: '#ffdcae', a: 0.75 }, sun: { x: 520, y: 722, col: [1.0, 0.82, 0.6], size: 300, I: 1.6 },
    clouds: [{ y: 190, h: 26, x0: -300, x1: 1100, col: '#56658c', lit: '#c3a7ae', litA: 0.55, sy: 0.02 }, { y: 400, h: 20, x0: -200, x1: 1100, col: '#8e8fb0', lit: '#f0c3a6', litA: 0.7, sy: 0.028, thr: 0.5 }, { y: 580, h: 14, x0: 0, x1: 1100, col: '#c9a6b0', lit: '#ffdcb0', litA: 0.8, sy: 0.04, thr: 0.52 }],
    water: { far: ['#f1cfa8', '#b8a1b0'], mid: ['#8c93b0', '#566285'], near: ['#46547a', '#2c3860'], fg: ['#232d52', '#161d3a'] }, glit: { col: '#fff0cf', a: 0.8, x: 520 },
    hull: '#1b1826', hullLit: '#55506a', rim: '#ffd8a8', sailLit: '#f6dcc0', sailMid: '#c9b0b4', sailShade: '#8a83a2', mast: '#171523', lantern: 0.7, lights: false },
};

// ---- water band: wavy top edge, long horizontal strokes banded by swell, crest lights, sun/moon glitter
export function paintWater(C, P) {
  const [x0, y0, x1, y1] = C.rect; const g = C.g, n = C.n, R = C.R; const k = P.k || 1;
  const top = (x) => P.top0 + P.amp * ((n.fbm(x * 0.0035 + P.seed, 3.7, 4) - 0.5) * 2 + 0.35 * Math.sin(x * 0.011 + P.seed * 3));
  const path = new Path2D(); path.moveTo(x0 - 20, y1 + 20); for (let x = x0 - 20; x <= x1 + 20; x += 4) path.lineTo(x, top(x)); path.lineTo(x1 + 20, y1 + 20); path.closePath();
  const cTop = hex(P.c[0]), cBot = hex(P.c[1]);
  const band = (x, y) => 0.5 + 0.5 * Math.sin((y - P.top0) * 0.11 / k + (n.fbm(x * 0.006, y * 0.01 / k, 3) - 0.5) * 7);
  const col = (x, y) => { const d = smoothstep(top(x), top(x) + P.fall, y); let c = mixc(cTop, cBot, d); if (P.skyc) c = mixc(c, hex(P.skyc), 0.25 * (1 - d)); return mixc(c, mul(c, 0.78), 0.5 * band(x, y) * (P.contrast ?? 1)); };
  underpaint(C, col, path, 8); const m = C.mask((gg) => gg.fill(path));
  const A = C.area;
  C.strokes({ n: A / (1000 * k), mask: m, color: col, angle: (x, y) => (n.fbm(x * 0.01, y * 0.02, 3) - 0.5) * 0.22 + (R() - 0.5) * 0.06, len: [50 * k, 140 * k], wid: [4 * k, 9 * k], alpha: [0.4, 0.7], jv: 0.045, bend: 0.06, taper: 0.5 });
  C.strokes({ n: A / (520 * k), mask: m, minMask: 0.5, color: col, angle: (x, y) => (n.fbm(x * 0.01, y * 0.02, 3) - 0.5) * 0.25 + (R() - 0.5) * 0.1, len: [16 * k, 56 * k], wid: [2.4 * k, 5 * k], alpha: [0.4, 0.75], jv: 0.06, bend: 0.1 });
  // crest lights: pale thin dabs along the top edge and along swell crests
  const lit = hex(P.lit || P.c[0]);
  for (let x = x0; x < x1; x += (6 + R() * 12) / Math.max(0.6, k * 0.8)) { const y = top(x) + 2 + R() * 7 * k; if (R() < 0.45) continue; C.dab(x, y, (R() - 0.5) * 0.12, (10 + R() * 26) * k, (1.4 + R() * 1.6) * k, lit, 0.18 + R() * 0.3, 0.04, 0.8); }
  for (let i = 0; i < A / (3500 * k * k); i++) { const x = lerp(x0, x1, R()), y = lerp(top(x) + 6, y1, Math.pow(R(), 0.8)); if (band(x, y) < 0.55) continue; C.dab(x, y, (R() - 0.5) * 0.15, (12 + R() * 34) * k, (1.4 + R() * 1.6) * k, lit, 0.18 + R() * 0.3, 0.05, 0.8); }
  if (P.glit) { const G = P.glit; const gc = hex(G.col); const cnt = A / (140 * k); for (let i = 0; i < cnt; i++) { const y = lerp(top(G.x) + 3, y1, Math.pow(R(), 0.65)); const spread = (G.w || 26) * k + (y - P.top0) * (G.widen ?? 0.12); const x = G.x + R.gauss() * spread * 0.5; if (!m(x, y)) continue; const bb = band(x, y); if (R() > 0.35 + 0.65 * bb) continue; C.dab(x, y, (R() - 0.5) * 0.1, (6 + R() * 22) * k, (1.2 + R() * 1.8) * k, gc, (0.35 + R() * 0.5) * G.a, 0.04, 0.8); } }
  if (P.blur) C.blur(P.blur);
}

// ---- the ship: local canvas 720 x 900, waterline y = 806, bow to the right, stern lantern at the left
export const SHIP = { W: 720, H: 900, wl: 806, lantern: [74, 626], pivot: [330, 806] };
const sheer = [[64, 688], [196, 698], [240, 716], [330, 725], [430, 723], [500, 708], [606, 690]];
const sheerY = (x) => { for (let i = 1; i < sheer.length; i++) if (x <= sheer[i][0]) { const [a, b] = [sheer[i - 1], sheer[i]]; return lerp(a[1], b[1], (x - a[0]) / (b[0] - a[0])); } return 690; };
function paintShip(C, M) {
  const g = C.g, R = C.R, n = C.n; const hull = hex(M.hull), hl = hex(M.hullLit), rim = hex(M.rim), mastC = hex(M.mast);
  // sails first (behind masts), then the hull in front of the lower sails
  const sail = (xl, xr, yT, yB, bulge, tag) => {
    const bl = bulge, p = new Path2D(); p.moveTo(xl, yT); p.lineTo(xr, yT); p.quadraticCurveTo(xr + bl * 0.6, (yT + yB) / 2, xr - bl * 0.2, yB); p.quadraticCurveTo((xl + xr) / 2, yB + (yB - yT) * 0.09, xl + bl * 0.2, yB); p.quadraticCurveTo(xl - bl * 0.6, (yT + yB) / 2, xl, yT); p.closePath();
    const sL = hex(M.sailLit), sM = hex(M.sailMid), sS = hex(M.sailShade);
    const colAt = (x, y) => { const u = (x - xl) / (xr - xl), v = (y - yT) / (yB - yT); const c = mixc(mixc(sL, sM, smoothstep(0.1, 0.75, u + 0.25 * v)), sS, smoothstep(0.55, 1.1, u + 0.35 * v)); return mixc(c, mul(c, 0.82), 0.5 * (0.5 + 0.5 * Math.sin(v * 9 + n.fbm(x * 0.02, y * 0.02, 2) * 5))); };
    underpaint(C, colAt, p, 5); const m = C.mask((gg) => gg.fill(p));
    C.strokes({ n: (xr - xl) * (yB - yT) / 70, box: [xl - 8, yT - 4, xr + 8, yB + 14], mask: m, minMask: 0.6, color: colAt, angle: () => Math.PI / 2 + (R() - 0.5) * 0.35, len: [18, 44], wid: [5, 11], alpha: [0.4, 0.7], jv: 0.05, bend: 0.1 });
    // seams + the sail's lit leading edge + shadow under the yard
    for (let s = 1; s < 4; s++) { const x = lerp(xl, xr, s / 4); C.dab(x, (yT + yB) / 2 + 4, Math.PI / 2, (yB - yT) * 0.86, 1.4, mul(sS, 0.78), 0.34, 0.04, 0.2); }
    g.save(); g.clip(p); const gr = g.createLinearGradient(0, yT, 0, yT + (yB - yT) * 0.22); gr.addColorStop(0, rgba(mul(sS, 0.5), 0.55)); gr.addColorStop(1, rgba(sS, 0)); g.fillStyle = gr; g.fillRect(xl - 10, yT, xr - xl + 20, (yB - yT) * 0.25); g.restore();
    for (let y = yT + 4; y < yB; y += 5 + R() * 6) C.dab(xl + 2 + R() * 5, y, Math.PI / 2, 8 + R() * 14, 2 + R() * 2, mixc(sL, [255, 238, 205], 0.35), 0.4 + R() * 0.3, 0.05);
  };
  const tri = (pts, bulge) => { const p = new Path2D(); p.moveTo(...pts[0]); p.quadraticCurveTo(...[(pts[0][0] + pts[1][0]) / 2 + bulge[0], (pts[0][1] + pts[1][1]) / 2 + bulge[1]], ...pts[1]); p.lineTo(...pts[2]); p.closePath();
    const sL = hex(M.sailLit), sM = hex(M.sailMid), sS = hex(M.sailShade); const xs = pts.map((q) => q[0]), ys = pts.map((q) => q[1]); const xl = Math.min(...xs), xr = Math.max(...xs), yT = Math.min(...ys), yB = Math.max(...ys);
    const colAt = (x, y) => mixc(mixc(sL, sM, smoothstep(0, 0.7, (x - xl) / (xr - xl))), sS, smoothstep(0.5, 1.1, (x - xl) / (xr - xl) + (y - yT) / (yB - yT) * 0.3)); underpaint(C, colAt, p, 5); const m = C.mask((gg) => gg.fill(p));
    C.strokes({ n: (xr - xl) * (yB - yT) / 160, box: [xl, yT, xr, yB], mask: m, minMask: 0.6, color: colAt, angle: () => Math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0]) + (R() - 0.5) * 0.3, len: [14, 36], wid: [4, 9], alpha: [0.4, 0.7], jv: 0.05 }); };
  // mizzen: spanker + topsail; main: three square sails; fore: three square sails; two jibs
  const MX = { miz: 140, main: 300, fore: 470 };
  tri([[470, 352], [706, 648], [482, 650]], [-6, 14]); tri([[478, 420], [650, 664], [486, 664]], [-4, 10]);
  sail(414, 526, 520, 650, 22, 'fc'); sail(426, 514, 442, 514, 16, 'ft'); sail(444, 496, 382, 436, 10, 'fg');
  sail(236, 366, 476, 618, 24, 'mc'); sail(252, 350, 392, 466, 18, 'mt'); sail(270, 332, 318, 384, 12, 'mg');
  { const p = new Path2D(); p.moveTo(144, 504); p.quadraticCurveTo(100, 520, 64, 552); p.lineTo(70, 696); p.lineTo(144, 700); p.closePath(); const sL = hex(M.sailLit), sM = hex(M.sailMid), sS = hex(M.sailShade);
    const colAt = (x, y) => mixc(mixc(sL, sM, smoothstep(60, 150, x)), sS, smoothstep(0.55, 1.0, (y - 504) / 196)); underpaint(C, colAt, p, 5); const m = C.mask((gg) => gg.fill(p));
    C.strokes({ n: 90 * 190 / 70, box: [60, 500, 148, 704], mask: m, minMask: 0.6, color: colAt, angle: () => Math.PI / 2 + (R() - 0.5) * 0.3, len: [16, 40], wid: [5, 10], alpha: [0.4, 0.7], jv: 0.05 }); }
  sail(112, 170, 458, 508, 8, 'zt');
  // hull
  const H = new Path2D(); H.moveTo(64, 688); H.lineTo(196, 698); H.quadraticCurveTo(222, 700, 240, 716); H.quadraticCurveTo(330, 728, 430, 724); H.quadraticCurveTo(500, 708, 606, 690); H.lineTo(612, 688); H.quadraticCurveTo(598, 760, 574, 830); H.lineTo(92, 830); H.quadraticCurveTo(76, 760, 64, 688); H.closePath();
  const hullCol = (x, y) => { const u = (x - 64) / 540, d = clamp((y - sheerY(x)) / 120); return mixc(mixc(hex(M.hullLit), hull, smoothstep(0, 0.5, d) * 0.85 + 0.15), hull, smoothstep(0.1, 0.9, u) * 0.3 + 0.1 * u); };
  underpaint(C, hullCol, H, 5); const mh = C.mask((gg) => gg.fill(H));
  for (let d = 4; d < 132; d += 6 + R() * 2) for (let x = 64; x < 612; x += 20 + R() * 20) { const y = sheerY(x) + d; if (y > 830) continue; C.dab(x + R() * 8, y, Math.atan((sheerY(x + 10) - sheerY(x - 10)) / 20) + (R() - 0.5) * 0.04, 22 + R() * 26, 2.8 + R() * 2.4, mixc(hullCol(x, y), d % 24 < 8 ? rim : hl, d % 24 < 8 ? 0.1 : 0.2 * R()), 0.4 + R() * 0.4, 0.02, 0.6); }
  // wale stripe + rail + deck line
  for (let x = 66; x < 600; x += 7 + R() * 5) { const y = sheerY(x) + 26 + (x - 64) * 0.004; C.dab(x, y, Math.atan((sheerY(x + 8) - sheerY(x - 8)) / 16), 16 + R() * 10, 3.2, mixc(hex('#7a5a4a'), rim, 0.15), 0.5, 0.02, 0.6); }
  for (let x = 62; x < 614; x += 3 + R() * 3) { C.dab(x, sheerY(x) - 1.5, Math.atan((sheerY(x + 6) - sheerY(x - 6)) / 12), 10 + R() * 8, 2.4, mixc(hex('#2a1f26'), rim, 0.1), 0.9, 0.0, 0.6); }
  // stern: quarter-gallery windows (dark, a hint of lantern warmth) and the poop cabin
  g.fillStyle = rgba(hex('#0d0a12')); g.fillRect(70, 664, 130, 30);
  for (let i = 0; i < 4; i++) { g.fillStyle = rgba(mixc(hex('#12100e'), hex('#d89a4e'), M.lantern * 0.75)); g.fillRect(84 + i * 20, 714, 11, 17); C.dab(89.5 + i * 20, 722, 0, 14, 8, hex('#ffc780'), 0.3 * M.lantern, 0.0); }
  g.fillStyle = rgba(mul(hull, 1.1)); g.fillRect(96, 658, 96, 8); for (let x = 98; x < 190; x += 14) { g.fillStyle = rgba(hex('#07060c')); g.fillRect(x, 670, 7, 13); }
  // masts, yards, rigging (soft: the Kuwahara pass turns thin lines into brushwork)
  const mastLine = (x, yT, yB, w) => { g.fillStyle = rgba(mastC); g.fillRect(x - w / 2, yT, w, yB - yT); C.dab(x - w * 0.35, (yT + yB) / 2, Math.PI / 2, yB - yT, w * 0.28, rim, 0.38, 0.0, 0.2); };
  mastLine(MX.miz, 440, 716, 6); mastLine(MX.main, 262, 726, 7.5); mastLine(MX.fore, 338, 718, 7);
  const yard = (x0, x1, y, w = 4.2) => { g.fillStyle = rgba(mastC); g.fillRect(x0, y - w / 2, x1 - x0, w); C.dab((x0 + x1) / 2, y - w * 0.4, 0, x1 - x0, w * 0.3, rim, 0.3, 0, 0.2); };
  yard(402, 538, 519); yard(422, 518, 441); yard(440, 500, 381); yard(224, 378, 475); yard(246, 354, 391); yard(266, 336, 317); yard(104, 176, 457); yard(112, 146, 500);
  const stay = (a, b, w = 1.5, al = 0.85) => { g.strokeStyle = rgba(mastC, al); g.lineWidth = w; g.lineCap = 'round'; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); };
  stay([MX.fore, 342], [706, 648]); stay([MX.main, 268], [MX.fore, 342]); stay([MX.miz, 444], [MX.main, 272]); stay([MX.main, 270], [MX.fore + 4, 340], 1.2, 0.6); stay([MX.miz, 442], [64, 640], 1.3, 0.8); stay([MX.main, 264], [64, 688], 1.2, 0.55);
  for (const mx of [MX.miz, MX.main, MX.fore]) { const top = mx === MX.main ? 300 : mx === MX.fore ? 380 : 470; for (const sd of [-1, 1]) { stay([mx, top], [mx + sd * 54, sheerY(mx) + 4], 1.4, 0.8); for (let r = 0; r < 9; r++) { const t = (r + 1) / 10; stay([mx + sd * 54 * t * 0.6, top + (sheerY(mx) - top) * t * 0.9 - 4], [mx + sd * 54 * t * 0.6 + 2, top + (sheerY(mx) - top) * t * 0.9 + 4], 1.0, 0.45); } } }
  stay([MX.fore, 520], [612, 698], 1.2, 0.7);
  // bowsprit + figurehead stub
  g.strokeStyle = rgba(mastC); g.lineWidth = 6; g.lineCap = 'round'; g.beginPath(); g.moveTo(590, 694); g.lineTo(712, 646); g.stroke();
  // stern lantern post + lantern body (painted dark; the light is a glow sprite + relight)
  const [lx, ly] = SHIP.lantern; g.fillStyle = rgba(mastC); g.fillRect(lx - 2, ly + 14, 4, 690 - ly - 14); g.fillStyle = rgba(hex('#0d0a12')); g.beginPath(); g.moveTo(lx - 9, ly - 14); g.lineTo(lx + 9, ly - 14); g.lineTo(lx + 7, ly + 15); g.lineTo(lx - 7, ly + 15); g.closePath(); g.fill();
  g.fillStyle = rgba(mixc(hex('#34261c'), hex('#ffd9a0'), M.lantern)); g.fillRect(lx - 5.5, ly - 10, 11, 21); g.fillStyle = rgba(hex('#0d0a12')); g.beginPath(); g.moveTo(lx - 11, ly - 14); g.lineTo(lx, ly - 26); g.lineTo(lx + 11, ly - 14); g.closePath(); g.fill();
  // waterline: the hull melts into the water, with a soft reflection beneath
  { const wl = SHIP.wl; g.save(); g.globalCompositeOperation = 'destination-out'; const gr = g.createLinearGradient(0, wl - 7, 0, wl + 9); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,1)'); g.fillStyle = gr; g.fillRect(0, wl - 7, SHIP.W, SHIP.H - wl + 7); g.restore();
    g.save(); g.translate(0, wl); g.scale(1, -1); g.globalAlpha = 0.5; g.filter = 'blur(1.6px)'; g.drawImage(C.c, 0, wl - 84, SHIP.W, 84, 0, -84, SHIP.W, 84); g.restore();
    g.save(); g.globalCompositeOperation = 'destination-out'; const g2 = g.createLinearGradient(0, wl + 4, 0, wl + 84); g2.addColorStop(0, 'rgba(0,0,0,0.15)'); g2.addColorStop(1, 'rgba(0,0,0,1)'); g.fillStyle = g2; g.fillRect(0, wl + 4, SHIP.W, 90); g.restore();
    for (let x = 70; x < 590; x += 4 + R() * 5) C.dab(x, wl + 1 + R() * 3, 0, 8 + R() * 18, 1.6 + R() * 1.4, mixc(hex(M.rim), [255, 255, 255], 0.3), 0.16 + R() * 0.2, 0.03, 0.7); }
  C.mottle({ amt: 0.04, cell: 12 });
}

export function buildSea(mood, shots) {
  const M = MOODS[mood]; const S = new Setup('sea-' + mood, { pos: [0, 0, 0], mm: 35 }); const f = S.f; const cams = coverCams(shots, 'sea:' + mood);
  const cover = (D, m) => S.cover(D, cams, m);
  const planes = {}; const seed = mood === 'dusk' ? 1 : mood === 'moon' ? 2 : 3;
  const D = { sky: 8000, b0: 3600, b1: 1500, b2: 620, b3: 300, ship: 170, b4: 85, b5: 42, b6: 21 };
  { const r = cover(D.sky, 40); const C = new Canvas(r, { seed: 400 + seed });
    paintSky(C, { stops: M.sky.map(([y, c]) => [y, hex(c)]), glow: { ...M.glow, col: hex(M.glow.col) }, clouds: M.clouds.map((c) => ({ ...c, col: hex(c.col), lit: hex(c.lit) })), n: 0.9 });
    if (M.moonD) { /* moon disc is a glow sprite; stars are painted dabs */ for (let i = 0; i < 160; i++) { const x = lerp(r[0], r[2], C.R()), y = lerp(r[1], 560, Math.pow(C.R(), 1.4)); C.dab(x, y, 0, 2 + C.R() * 2, 1.4 + C.R(), [210, 222, 255], 0.35 + C.R() * 0.5, 0, 0.5); } }
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  const bands = [
    ['b0', D.b0, 0, 1.5, 0.5, 70, M.water.far, 0.55], ['b1', D.b1, 6, 3, 0.6, 90, M.water.far, 0.7], ['b2', D.b2, 34, 6, 0.8, 140, [M.water.far[1], M.water.mid[0]], 0.8],
    ['b3', D.b3, 100, 9, 1.0, 170, M.water.mid, 0.9], ['b4', D.b4, 172, 12, 1.4, 190, [M.water.mid[1], M.water.near[0]], 1.0], ['b5', D.b5, 282, 18, 2.0, 220, M.water.near, 1.0], ['b6', D.b6, 440, 26, 3.2, 260, M.water.fg, 1.0],
  ];
  for (const [key, Dd, dy, amp, k, fall, c, gA] of bands) {
    const r0 = cover(Dd, 50); const top0 = YH + dy; const r = [r0[0], Math.max(r0[1], top0 - amp - 30), r0[2], Math.max(r0[3], top0 + 200)]; const C = new Canvas(r, { seed: 410 + seed * 10 + bands.findIndex((b) => b[0] === key), q: key === 'b6' ? 0.7 : key === 'b0' || key === 'b1' ? 1 : 1 });
    const gl = { ...M.glit, x: M.glit.x, w: 18 + k * 10, widen: 0.16 * (k > 1 ? 1 : 0.5), a: M.glit.a * gA };
    paintWater(C, { top0, amp, k, fall, c, seed: seed * 7 + dy * 0.01, glit: key === 'b0' ? null : gl, lit: M.glit.col, blur: key === 'b6' ? 2.5 : key === 'b5' ? 1.2 : 0, contrast: key === 'b0' || key === 'b1' ? 0.4 : 1, skyc: M.sky[M.sky.length - 2][1] });
    C.mottle({ amt: 0.04 }); const pl = S.plane(key, Dd, r, C.c); pl.userData.amp = k; planes[key] = pl;
  }
  // the ship: plane in a pivot group so it can roll about the waterline
  const shipG = new THREE.Group(); S.group.add(shipG);
  const shipPlane = (() => { const r = [0, 0, SHIP.W, SHIP.H]; const C = new Canvas(r, { seed: 450 + seed }); paintShip(C, M); return C; })();
  const ship = S.plane('ship', D.ship, [0, 0, SHIP.W, SHIP.H], shipPlane.c); S.group.remove(ship); shipG.add(ship); ship.userData.pivotPx = SHIP.pivot;
  const sun = S.glow(M.sun.x, M.sun.y, D.sky * 0.9, M.sun.size * 0.9, { color: M.sun.col, core: 30 }, planes.sky); sun.material.uniforms.uI.value = M.sun.I;
  const lanternGlow = S.glow(0, 0, D.ship, 60, { color: GLOW, core: 40 }, ship); const lanternGlow2 = S.glow(0, 0, D.ship, 24, { color: [1.0, 0.8, 0.5], core: 30 }, ship);
  const api = {
    key: 'sea:' + mood, S, M, planes, shipG, ship, D, cams, lanternGlow,
    // place the ship at depth Dship, screen-px offset (sx, sy) of its pivot from design position, uniform scale
    placeShip(Dd, px, py, rot = 0, sc = 1) {
      const s = Dd / f; const pw = S.world(px, py, Dd); shipG.position.copy(pw); shipG.rotation.z = rot; shipG.scale.setScalar(sc);
      const cx = (SHIP.W / 2 - SHIP.pivot[0]) * s, cy = -(SHIP.H / 2 - SHIP.pivot[1]) * s; ship.position.set(cx, cy, 0);
      const order = (d) => 1e6 - d * 10; ship.renderOrder = order(Dd); lanternGlow.renderOrder = ship.renderOrder + 0.5; lanternGlow2.renderOrder = ship.renderOrder + 0.6;
      api.shipD = Dd; api.shipS = s * sc; api.shipS0 = s;
    },
    lanternWorld() { const s = api.shipS0; const v = new THREE.Vector3((SHIP.lantern[0] - SHIP.pivot[0]) * s, -(SHIP.lantern[1] - SHIP.pivot[1]) * s, 0); shipG.updateMatrixWorld(true); return shipG.localToWorld(v); },
    show(v) { S.group.visible = v; },
    update(t, sh, tl, u) {
      // swell: each band drifts and bobs a little (phase per band), ship rolls and heaves on the slowest swell
      for (const k of ['b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6']) { const p = planes[k]; const ph = k.charCodeAt(1) * 1.7; const a = (k === 'b0' ? 0 : p.userData.amp) * 0.9; const sc = p.userData.D / f;
        p.position.x = p.userData.base.x + (Math.sin(t * 0.33 + ph) * 5 * a + t * (0.4 + 0.5 * a) * (sh.drift ?? 1)) * sc; p.position.y = p.userData.base.y + Math.sin(t * 0.55 + ph * 1.3) * 2.6 * a * sc; }
      const roll = 0.016 * Math.sin(t * 0.62 + seed) + 0.006 * Math.sin(t * 1.4 + 2 * seed); const heave = 3.2 * Math.sin(t * 0.62 + seed + 0.8);
      const shipSpec = typeof sh.ship === 'function' ? sh.ship(tl, u, t) : sh.ship; const sp = { D: 170, x: 360, y: 872, sc: 1, ...(shipSpec || {}) }; api.placeShip(sp.D, sp.x, sp.y + heave * sp.sc, roll * (sh.roll ?? 1), sp.sc);
      const shipOn = shipSpec !== null; shipG.visible = shipOn; lanternGlow.visible = lanternGlow2.visible = shipOn; const lw = api.lanternWorld(); const fl = flick(t, 3) * M.lantern;
      lanternGlow.position.copy(lw); lanternGlow2.position.copy(lw); lanternGlow.material.uniforms.uI.value = 1.05 * fl * (sh.lanternK ?? 1); lanternGlow2.material.uniforms.uI.value = 0.9 * fl * (sh.lanternK ?? 1);
      const lk = (sh.lanternK ?? 1) * fl; const lightList = [{ p: lw, r: 1.0 * api.shipS * 60, c: WARM, k: 2.0 * M.lantern * lk }];
      setLights(ship.material, lightList); for (const k of ['b4', 'b5']) setLights(planes[k].material, [{ p: lw, r: 1.6 * api.shipS * 90, c: WARM, k: 1.1 * M.lantern * lk * (mood === 'moon' ? 1.2 : 0.6) }]);
    },
  };
  const X = buildExtras({ S, mood, M, cover, planes, shipG, api, f, D, seed });
  const upd = api.update; api.update = (t, sh, tl, u) => { upd(t, sh, tl, u); X.update(t, sh); }; api.draw = (g, e) => X.draw(g, e); api.X = X;
  S.group.visible = false; return api;
}
