// stage.js — the paper theatre's fixed scenery, authored in S1 screen coordinates per layer (multiplane cards).
import { cut, torn, circle, poly, piece, rgb, screenTex } from './paper.js';
import { PAL, ST, INK } from './puppets.js';
import { rng } from '/harness/kit/film.js';

export const DEPTH = { screen: 2.2, far: 1.9, near: 1.65, mid: 1.4, dragon: 1.15, bird: 1.05, army: 1.0, front: 0.9, grass: 0.75 };
const L = {};
let SCREEN = null;
export const HOT = [872, 236];                                   // the lamp's hotspot on the screen (screen-layer coords)
const STOPS = [[0, [255, 242, 200]], [0.08, [255, 224, 152]], [0.22, [255, 184, 82]], [0.4, [246, 130, 34]], [0.62, [206, 80, 16]], [0.84, [130, 40, 10]], [1.1, [56, 16, 5]]];

const ridge = (x0, x1, yFn, step, bottom = 1150) => { const pts = []; for (let x = x0; x <= x1 + 0.1; x += step) pts.push([x, yFn(x)]); pts.push([x1, bottom], [x0, bottom]); return poly(pts); };
function merlons(xa, xb, y, h, n) { const pw = (xb - xa) / (2 * n - 1), out = []; for (let i = 0; i < 2 * n - 1; i++) { const yy = i % 2 ? y : y - h; out.push([xa + i * pw, yy], [xa + (i + 1) * pw, yy]); } return out; }
function castlePath() {
  const P = [[40, 562], [48, 232], [40, 232], [81, 148], [122, 232], [114, 232], [114, 330], ...merlons(114, 150, 330, 10, 2), [150, 330], [150, 198],
    ...merlons(150, 268, 198, 16, 5), [268, 198], [268, 352], ...merlons(268, 298, 352, 10, 2), [298, 352], [298, 264], [290, 264], [326, 194], [362, 264], [354, 264], [354, 562]];
  const holes = 'M 76 286 L 76 268 Q 81 259 86 268 L 86 286 Z M 77 396 L 77 380 Q 81 373 85 380 L 85 396 Z '
    + 'M 184 262 L 184 242 Q 190 232 196 242 L 196 262 Z M 222 262 L 222 242 Q 228 232 234 242 L 234 262 Z ' + circle(209, 302, 8, 18)
    + 'M 189 556 L 189 502 Q 209 474 229 502 L 229 556 Z M 322 314 L 322 296 Q 326 289 330 296 L 330 314 Z M 126 362 L 126 378 L 131 378 L 131 362 Z M 278 380 L 278 396 L 283 396 L 283 380 Z';
  return poly(P) + holes;
}
const flag = (x, y, w, v) => `M ${x - 1.3} ${y + 36} L ${x - 1.3} ${y} L ${x + w} ${y + 5 + v} L ${x + w - 7} ${y + 9 + v * 0.5} L ${x + w + 1} ${y + 14 + v} L ${x + 1.3} ${y + 15} L ${x + 1.3} ${y + 36} Z`;
function tuft(x, y, h, n, seed, lean = 0) {
  const r = rng(seed); let s = '';
  for (let j = 0; j < n; j++) { const bx = x + (j - n / 2) * 3.2 + (r() - 0.5) * 2, hh = h * (0.55 + 0.45 * r()), tx = bx + lean * hh + (r() - 0.5) * hh * 0.5, w = 1.6 + r() * 1.4; s += `M ${bx - w} ${y + 4} Q ${bx - w * 0.3 + (tx - bx) * 0.4} ${y - hh * 0.5} ${tx} ${y - hh} Q ${bx + w * 0.3 + (tx - bx) * 0.5} ${y - hh * 0.45} ${bx + w} ${y + 4} Z `; }
  return s;
}
function fern(x, y, h, lean, n) {           // a cut-paper frond: curved stem with alternating leaflets
  let s = `M ${x - 1.2} ${y + 3} Q ${x + lean * 0.4 - 1.2} ${y - h * 0.55} ${x + lean - 0.6} ${y - h} L ${x + lean + 0.6} ${y - h} Q ${x + lean * 0.4 + 1.2} ${y - h * 0.55} ${x + 1.2} ${y + 3} Z `;
  for (let k = 1; k < n; k++) { const u = k / n, px = x + lean * u * u, py = y - h * u, L = 20 * (1 - u * 0.75), side = k % 2 ? 1 : -1; s += `M ${px} ${py - 1.2} L ${px + side * L} ${py - 5 - L * 0.4} L ${px + side * L * 0.4} ${py + 1.5} Z `; }
  return s;
}
function daisy(x, y, h) {
  const cx = x + 3, cy = y - h; let s = `M ${x - 1.1} ${y + 3} Q ${x + 2} ${y - h * 0.5} ${cx - 0.9} ${cy} L ${cx + 0.9} ${cy} Q ${x + 3} ${y - h * 0.5} ${x + 1.1} ${y + 3} Z `;
  const pts = []; for (let k = 0; k < 24; k++) { const a = k / 24 * Math.PI * 2, r = k % 2 ? 5.5 : 11.5; pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); }
  return s + poly(pts) + circle(cx, cy, 2.1, 8) + `M ${x + 1} ${y - h * 0.45} Q ${x + 9} ${y - h * 0.55} ${x + 13} ${y - h * 0.48} Q ${x + 8} ${y - h * 0.4} ${x + 1} ${y - h * 0.35} Z `;
}
export function buildStage() {
  SCREEN = screenTex(1760, 1260, 21);
  L.far = torn(ridge(-500, 2300, (x) => 468 + 15 * Math.sin(x / 160 + 0.5) + 9 * Math.sin(x / 61 + 2) + 5 * Math.sin(x / 23), 18), { seed: 701 });
  L.farTrees = cut([566, 588, 604, 1360, 1384].map((x, k) => `M ${x - 6} ${462 + k % 2 * 3} L ${x} ${444 + k % 2 * 3} L ${x + 6} ${462 + k % 2 * 3} Z `).join(''), { seed: 708, amp: 0.3 });
  const pk = [[-500, 522], [-300, 508], [-100, 514], [100, 500], [300, 510], [520, 503], [700, 494], [820, 474], [900, 424], [948, 378], [992, 404], [1060, 302], [1112, 352], [1150, 336], [1226, 264], [1292, 332], [1340, 308], [1420, 362], [1500, 320], [1590, 374], [1700, 346], [1820, 402], [2000, 382], [2300, 424]];
  L.near = cut(poly([...pk, [2300, 1150], [-500, 1150]]), { seed: 702, amp: 1.3, freq: 0.05, hf: 0.7, fib: 0.9, step: 3 });
  L.hill = torn('M -500 1150 L -500 566 C -300 556 -100 550 80 553 C 240 556 380 560 520 586 C 600 600 660 620 700 1150 Z', { seed: 703 });
  L.castle = cut(castlePath(), { seed: 704, rule: 'evenodd', amp: 0.55 });
  L.flags = [0, 1].map((v) => cut(flag(81, 114, 26, v * 3 - 1.5) + flag(326, 160, 22, 1.5 - v * 3), { seed: 709 + v, amp: 0.3 }));
  L.trees = cut('M 924 600 L 924 560 Q 896 562 892 536 Q 884 512 904 500 Q 908 478 932 478 Q 954 474 962 496 Q 982 506 974 530 Q 970 556 940 558 L 940 600 Z', { seed: 711, amp: 0.6 });
  L.ground = torn(ridge(-500, 2300, (x) => 577 + 3 * Math.sin(x / 90) + 2 * Math.sin(x / 37 + 1), 14), { seed: 705, amp: 1.0, hf: 0.6 });
  L.mound = torn('M -500 1150 L -500 690 C -300 684 -100 682 60 686 C 160 690 220 696 262 704 L 300 1150 Z', { seed: 706 });
  L.rock = cut('M 256 1150 L 262 640 L 274 566 L 288 526 L 300 506 L 326 494 L 344 491 L 372 490 L 392 497 L 404 512 L 416 540 L 426 580 L 440 640 L 452 1150 Z', { seed: 714, amp: 0.9, hf: 0.5, fib: 0.6 });
  L.hillock = torn('M 1000 1150 L 1004 640 C 1020 616 1050 604 1090 600 C 1120 590 1150 594 1176 588 C 1220 580 1270 586 1320 578 C 1380 570 1440 574 1500 566 C 1600 556 1700 560 1800 552 L 2300 548 L 2300 1150 Z', { seed: 707 });
  L.frontTufts = cut(tuft(70, 690, 18, 7, 1, -0.2) + tuft(206, 697, 15, 6, 2, 0.2) + tuft(1040, 612, 22, 8, 3, -0.15) + tuft(1236, 586, 18, 7, 4, 0.1) + tuft(1470, 572, 20, 8, 5, 0) + tuft(1760, 556, 18, 7, 6, -0.1), { seed: 712, amp: 0.25 });
  L.plants = [cut(fern(1074, 604, 104, -34, 11), { seed: 715, amp: 0.25 }), cut(fern(1118, 598, 70, 22, 9), { seed: 716, amp: 0.25 }), cut(daisy(1204, 590, 64), { seed: 717, amp: 0.25, rule: 'evenodd' })];
  L.grass = cut([-260, -60, 170, 420, 640, 880, 1120, 1340, 1580, 1820, 2060].map((x, k) => tuft(x, 742, 46 + (k * 37) % 30, 9 + k % 4, 20 + k, ((k % 3) - 1) * 0.18)).join(''), { seed: 713, amp: 0.3 });
}

// ------------------------------------------------------------------ the lamp-lit screen (screen-layer coords; B = lamp brightness)
export function drawScreen(g, B = 1) {
  g.save(); g.translate(HOT[0], HOT[1]); g.scale(1.35, 1); const R = 760, grd = g.createRadialGradient(0, 0, 0, 0, 0, R);
  for (const [s, c] of STOPS) grd.addColorStop(s / 1.1, rgb(c.map((v) => Math.min(255, v * B))));
  g.fillStyle = grd; g.fillRect(-R * 2, -R * 2, R * 4, R * 4); g.restore();
  g.globalCompositeOperation = 'multiply'; g.drawImage(SCREEN, -80, -330); g.globalCompositeOperation = 'source-over';
}
// CU background: the same screen seen closer (texture magnified, hotspot behind the puppet)
export function drawScreenCU(g, B = 1) {
  g.save(); g.translate(470, 210); g.scale(1.3, 1); const R = 900, grd = g.createRadialGradient(0, 0, 0, 0, 0, R);
  for (const [s, c] of STOPS) grd.addColorStop(s / 1.1, rgb(c.map((v) => Math.min(255, v * B))));
  g.fillStyle = grd; g.fillRect(-R * 2, -R * 2, R * 4, R * 4); g.restore();
  g.globalCompositeOperation = 'multiply'; g.drawImage(SCREEN, 380, 360, 760, 430, -20, -20, 1320, 760); g.globalCompositeOperation = 'source-over';
}
// translucent layers (drawn into the compositor's layer canvas, then multiplied over everything behind)
export const drawFar = (g) => { piece(g, L.far, { fill: ST.far }); piece(g, L.farTrees, { fill: ST.near }); };
export const drawNear = (g) => piece(g, L.near, { fill: ST.near });
export const drawMid = (g, i) => { piece(g, L.hill, { fill: ST.mid }); g.save(); g.translate(-80, 0); piece(g, L.castle, { fill: ST.mid }); piece(g, L.flags[Math.floor(i / 6) % 2], { fill: ST.mid }); g.restore(); };
export const drawGround = (g) => piece(g, L.ground, { fill: ST.ground });
// opaque near-black layers
export const drawFrontLeft = (g) => { piece(g, L.mound, INK(1.4)); piece(g, L.rock, INK(1.4)); };
export const drawFrontRight = (g) => { for (const p of L.plants) piece(g, p, INK(0.9)); piece(g, L.hillock, INK(1.4)); piece(g, L.frontTufts, INK(1.0)); };
export const drawGrass = (g) => piece(g, L.grass, INK(1.2));
