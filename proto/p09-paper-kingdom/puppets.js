// puppets.js — jointed cut-out puppets for P09. Every piece is built once (fixed cut wobble); poses only move pivots.
import { cut, torn, circle, poly, piece, rgb, transTex, surfTex, rimTex } from './paper.js';
import { lerp, clamp } from '/harness/kit/film.js';

export const PAL = {
  ink: [24, 13, 7], inkB: [52, 26, 13], rim: [205, 122, 58],
  far: [226, 168, 126], near: [184, 116, 76], mid: [118, 68, 42], ground: [124, 70, 43],
  creamL: [255, 244, 218], creamM: [240, 212, 164], creamD: [206, 160, 106], crease: [138, 86, 46],
  fireO: [255, 112, 18], fireY: [255, 206, 70],
};
export const ST = {};
export function initStyles(g) {
  ST.ink = rgb(PAL.ink); ST.inkB = rgb(PAL.inkB);
  ST.inkTex = g.createPattern(surfTex(256, [150, 86, 44], 31, 0.09), 'repeat');
  ST.rim = g.createPattern(rimTex(128, PAL.rim, 41), 'repeat');
  ST.far = g.createPattern(transTex(512, PAL.far, 51, { mott: 0.26 }), 'repeat');
  ST.near = g.createPattern(transTex(512, PAL.near, 61, { mott: 0.3 }), 'repeat');
  ST.mid = g.createPattern(transTex(512, PAL.mid, 71, { mott: 0.34 }), 'repeat');
  ST.ground = g.createPattern(transTex(512, PAL.ground, 81, { mott: 0.3 }), 'repeat');
  ST.cream = g.createPattern(transTex(256, [255, 255, 255], 91, { mott: 0.12, fib: 120 }), 'repeat');
}
export const INK = (rimW = 1.3) => ({ fill: ST.ink, tex: ST.inkTex, rimStyle: ST.rim, rimW });

// ================================================================== the KING (feet at 0,0; faces right)
const K = {};
function buildKing() {
  const hem = []; for (let k = 1, x = -64; x < -16; x += 4, k++) hem.push([x, k % 2 ? -4 : 0]);
  K.cape = cut('M -12 -132 C -28 -126 -38 -100 -44 -64 C -50 -30 -58 -12 -68 0 ' + hem.map((p) => `L ${p[0]} ${p[1]}`).join(' ') + ' L -16 0 L -14 -60 Z', { seed: 214 });
  K.robe = cut('M -18 -128 L 12 -130 C 18 -112 22 -84 24 -54 C 26 -30 28 -12 30 0 L -22 0 C -22 -40 -22 -90 -18 -128 Z M -15 -73 L 20 -75 L 20 -72.4 L -15 -70.4 Z '
    + [-13, -1, 11, 22].map((cx) => poly([[cx, -15], [cx + 2.4, -10.5], [cx, -6], [cx - 2.4, -10.5]])).join(' '), { seed: 201, rule: 'evenodd' });
  K.collar = cut('M -27 -134 Q -14 -143 -2 -138 Q 10 -144 23 -136 L 25 -122 Q 14 -116 4 -120 Q -8 -114 -20 -120 Q -27 -122 -29 -128 Z '
    + [[-14, -129], [0, -128], [13, -129]].map(([cx, cy]) => poly([[cx, cy - 3.6], [cx + 2, cy], [cx, cy + 3.6], [cx - 2, cy]])).join(' '), { seed: 215, rule: 'evenodd' });
  K.head = cut('M -6 -136 C -14 -142 -15 -160 -7 -168 C 0 -175 14 -175 20 -167 L 22 -160 L 33 -152 L 23 -148 L 25 -143 L 31 -136 L 29 -126 L 26 -108 L 18 -122 L 8 -134 Z '
    + 'M 10 -158 Q 13.5 -162 17.5 -158.5 Q 13.5 -155.5 10 -158 Z', { seed: 202, rule: 'evenodd' });
  K.crown = cut('M -10 -168 L 21 -171 L 22 -178 L 25 -195 L 17 -182 L 11 -201 L 5 -183 L -1 -198 L -5 -182 L -12 -193 L -11 -178 Z ' + circle(6, -175, 1.9, 8), { seed: 203, rule: 'evenodd' });
  K.balls = [[25, -196.5], [11, -202.8], [-1, -199.6], [-12, -194.6]].map(([x, y], k) => cut(circle(x, y, 2.6, 12), { seed: 204 + k * 31 }));
  K.shoe = cut('M 22 -1 L 30 -5 C 38 -7 44 -8 47 -14 C 48 -6 42 -1 31 1 Z', { seed: 207 });
  K.sleeve = cut('M -9 -4 C -10 14 -12 30 -16 46 L 14 52 C 12 32 10 14 8 -4 Q 0 -9 -9 -4 Z', { seed: 208 });
  K.fist = cut(circle(-0.5, 58, 7.5, 18), { seed: 209 });
  K.rod = cut('M -2.6 40 L 1.6 40 L 1.6 92 L -2.6 92 Z', { seed: 210 });
  K.orb = cut(circle(-0.5, 97, 6.6, 16), { seed: 211 });
  K.fin = cut('M -0.5 101.5 L 3.6 107.5 L -0.5 114.5 L -4.6 107.5 Z', { seed: 212 });
  K.pin = cut(circle(0, 0, 2.6, 10), { seed: 213 });
}
// k: { x, y, s, arm (rad: 0 = hanging, + = swings forward/up), lean (rad) }
export function drawKing(g, k) {
  const st = INK(1.25);
  g.save(); g.translate(k.x, k.y); g.scale(k.s, k.s); g.rotate(k.lean || 0);
  piece(g, K.cape, st); piece(g, K.robe, st); piece(g, K.shoe, st); piece(g, K.collar, st); piece(g, K.head, st); piece(g, K.crown, st); for (const b of K.balls) piece(g, b, st);
  g.translate(6, -124); g.rotate(-k.arm);
  piece(g, K.rod, st); piece(g, K.orb, st); piece(g, K.fin, st); piece(g, K.sleeve, st); piece(g, K.fist, st); piece(g, K.pin, st);
  g.restore();
}

// ================================================================== SOLDIER (feet at 0,0; faces right; hip at y -35)
const S = {};
function buildSoldier() {
  S.torso = cut('M -9 -67 L 8 -67 L 11 -48 L 15 -33 L -13 -33 L -10 -48 Z M -7 -47.6 L 8 -47.6 L 8.2 -45.4 L -7.2 -45.4 Z', { seed: 101, rule: 'evenodd' });
  S.head = cut('M -8 -80 L 9 -80 L 9 -76 L 13.5 -73 L 9 -71 L 9 -66.5 L -8 -66.5 Z', { seed: 102 });
  S.helmet = cut('M -10 -84 C -10 -95 -4 -101 0 -108 C 5 -101 11 -95 11 -86 L 14 -83 L 14 -79.5 L -12 -79.5 L -12 -83 Z', { seed: 103 });
  S.plume = cut('M 0 -106 C -5 -114 -13 -116 -20 -110 C -14 -111 -8 -108 -3 -102 Z', { seed: 104 });
  S.shield = cut(circle(10, -51, 14, 26) + circle(10, -51, 3.3, 10), { seed: 105, rule: 'evenodd' });
  S.legA = [cut('M -5 -38 L 1 -38 L -9 -5 L -6 -4 L -5 0 L -18 0 L -17 -3 L -15 -5 Z', { seed: 106 }), cut('M 0 -38 L 6 -38 L 15 -5 L 19 -4 L 21 0 L 9 0 L 9 -4 Z', { seed: 107 })];
  S.legB = [cut('M -4 -38 L 2 -38 L 1.5 -5 L 6 -4 L 8 0 L -5 0 L -5 -4 Z', { seed: 108 }), cut('M 0 -38 L 6 -38 L 11 -21 L 6 -11 L 12 -9 L 12 -6 L 1 -7 L 4 -21 Z', { seed: 109 })];
  S.legH = [cut('M -5 -38 L 5 -38 L 6 -5 L 11 -4 L 12 0 L -6 0 L -6 -4 Z', { seed: 110 })];
  S.shaft = cut('M -1.3 40 L 1.3 40 L 1.3 -95 L -1.3 -95 Z', { seed: 111, amp: 0.3 });
  S.blade = cut('M 0 -115 C 4.5 -108 5 -100 1.4 -95 L -1.4 -95 C -5 -100 -4.5 -108 0 -115 Z', { seed: 112 });
  S.fist = cut(circle(0, 0, 4.2, 12), { seed: 113 });
}
// s: { x, y, s, pose 'A' contact | 'B' passing | 'H' halt, bob (px, body only), lean, spear (rad, + = tip forward) }
export function drawSoldier(g, s) {
  const st = INK(1.1);
  g.save(); g.translate(s.x, s.y); g.scale(s.s, s.s);
  for (const l of (s.pose === 'A' ? S.legA : s.pose === 'B' ? S.legB : S.legH)) piece(g, l, st);
  g.translate(0, s.bob || 0); g.rotate(s.lean || 0);
  piece(g, S.torso, st); piece(g, S.head, st); piece(g, S.helmet, st); piece(g, S.plume, st); piece(g, S.shield, st);
  g.translate(-1, -50); g.rotate(s.spear || 0); piece(g, S.shaft, st); piece(g, S.blade, st); piece(g, S.fist, st);
  g.restore();
}

// ================================================================== DRAGON (base at 0,0; faces left). chain of 5 hinged segments + head + jaw, two-part wings
export const DRG = { segs: [[120, 88, 74, 3, 22], [105, 74, 60, 3, 20], [92, 60, 48, 3, 16], [80, 48, 40, 2, 14], [70, 40, 34, 2, 12]] }; // [L, w0, w1, spines, spine h]
const D = {};
function segPath(L, w0, w1, nS, h) {
  const W = (x) => lerp(w0, w1, clamp(x / L)) / 2, pts = [[0, W(0)]];
  for (let j = 0; j < nS; j++) { const xc = L * (j + 0.55) / nS, bw = L / nS * 0.3; pts.push([xc - bw, W(xc - bw)], [xc - bw * 1.6, W(xc) + h], [xc + bw, W(xc + bw)]); }
  pts.push([L, W(L)]);
  for (let k = 1; k < 8; k++) { const a = Math.PI / 2 - k / 8 * Math.PI; pts.push([L + Math.cos(a) * W(L), Math.sin(a) * W(L)]); }
  pts.push([L, -W(L)]);
  const nP = Math.max(3, Math.round(L / 13));
  for (let j = 1; j < nP; j++) { const x = L * (1 - j / nP); pts.push([x + 2.6, -W(x + 2.6)], [x, -W(x) + 2.6], [x - 2.6, -W(x - 2.6)]); }
  pts.push([0, -W(0)]);
  for (let k = 1; k < 8; k++) { const a = -Math.PI / 2 - k / 8 * Math.PI; pts.push([Math.cos(a) * W(0), Math.sin(a) * W(0)]); }
  return poly(pts);
}
function buildDragon() {
  D.segs = DRG.segs.map((s, k) => cut(segPath(...s), { seed: 300 + k, amp: 0.4 }));
  const up = []; for (let x = 97; x > 44; x -= 6) up.push(`L ${x} -4 L ${x - 3} ${x % 12 < 6 ? -13 : -10}`);
  D.head = cut('M -10 20 L -52 46 L -6 30 L 10 31 L -26 66 L 22 35 L 44 31 L 52 25 L 78 19 L 95 18 L 104 9 L 105 1 L 99 -3 ' + up.join(' ')
    + ' L 40 -8 L 28 -15 L 8 -19 L -8 -13 Q -14 0 -10 20 Z M 51 15 Q 58 21.5 66 16 Q 58 11.5 51 15 Z ' + circle(97, 10, 1.9, 8), { seed: 310, rule: 'evenodd', amp: 0.35 });
  const lo = []; for (let x = 12; x < 66; x += 6) lo.push(`L ${x} 4 L ${x + 3} ${x % 12 < 6 ? 12 : 9.5}`);
  D.jaw = cut('M -6 3 ' + lo.join(' ') + ' L 70 5 L 73 -2 L 64 -10 L 20 -14 L -4 -8 Z', { seed: 311, amp: 0.35 });
  D.wingIn = cut('M -8 2 L 150 -2 L 150 8 C 122 30 102 58 84 84 C 62 70 32 64 -4 66 Z', { seed: 320, amp: 0.5 });
  D.boneIn = cut('M -10 -6 L 148 -7 L 158 0 L 148 7 L -10 6 Z', { seed: 321, amp: 0.3 });
  D.wingOut = cut('M -4 -2 L 140 -16 L 132 -4 Q 100 20 112 58 L 104 63 Q 72 52 54 106 L 46 108 Q 28 70 -2 82 Q -8 40 -4 -2 Z', { seed: 322, amp: 0.5 });
  D.fingers = [cut('M -3 -5 L 146 -20 L 140 -12 L -3 4 Z', { seed: 323, amp: 0.25 }), cut('M -3 -3 L 110 58 L 104 63 L 3 4 Z', { seed: 324, amp: 0.25 }), cut('M -2 -3 L 52 108 L 45 109 L 3 3 Z', { seed: 325, amp: 0.25 })];
  D.claw = cut('M 0 -6 L 34 -10 L 52 -2 L 60 -8 L 58 0 L 64 2 L 56 6 L 60 12 L 50 8 L 30 8 L 0 6 Z', { seed: 326, amp: 0.3 });
  D.pin = cut(circle(0, 0, 3.4, 12), { seed: 327 });
}
// pose: { ang:[6] world angles (seg0..4, head), jaw, wN:[a,b], wF:[a,b], claw }
export function dragonJoints(pose) {
  const P = [[0, 0]]; let x = 0, y = 0;
  for (let k = 0; k < 5; k++) { const a = pose.ang[k], L = DRG.segs[k][0]; x += Math.cos(a) * L; y += Math.sin(a) * L; P.push([x, y]); }
  return P;
}
function creamPiece(g, sh, col) { g.fillStyle = rgb(col); g.fill(sh.p, sh.rule); g.globalCompositeOperation = 'multiply'; g.fillStyle = ST.cream; g.fill(sh.p, sh.rule); g.globalCompositeOperation = 'source-over'; g.strokeStyle = rgb(PAL.crease, 0.85); g.lineWidth = 0.9; g.stroke(sh.p); }
function drawWing(g, root, w, s, membraneA, far, cream = false, squash = 1) {
  const ink = (sh, a = 1, rimmed = true) => cream ? creamPiece(g, sh, far ? PAL.creamD : PAL.creamL) : piece(g, sh, { fill: far ? ST.inkB : ST.ink, tex: ST.inkTex, alpha: a, rimStyle: rimmed && !far ? ST.rim : null, rimW: 1.1 });
  g.save(); g.translate(root[0], root[1]); g.rotate(w[0]); g.scale(s, s * squash);
  ink(D.wingIn, membraneA);
  g.save(); g.translate(150, 0); g.rotate(w[1]); if (cream) creamPiece(g, D.wingOut, far ? PAL.creamD : PAL.creamM); else ink(D.wingOut, membraneA);
  if (!cream) for (const f of D.fingers) ink(f, 1);
  g.restore();
  if (!cream) ink(D.boneIn, 1);
  g.restore();
}
// opts: wings (bool), wingCream, wingSquash, neckCream (seg3, seg4, head shown as the flipped cream back), neckSquash
export function drawDragon(g, pose, { wings = true, wingCream = false, wingSquash = 1, neckCream = false, neckSquash = 1, segs = 5 } = {}) {
  const P = dragonJoints(pose), st = INK(1.3);
  const a1 = pose.ang[1], root = [P[2][0] - Math.sin(a1) * 18, P[2][1] + Math.cos(a1) * 18];   // shoulder on the dorsal side of seg1's end
  if (wings) drawWing(g, [root[0] + 14, root[1] - 18], pose.wF, 0.86, 0.96, true, wingCream, wingSquash);
  const seg = (k) => { g.save(); g.translate(P[k][0], P[k][1]); g.rotate(pose.ang[k]); if (neckCream && k >= 3) { g.scale(1, neckSquash); creamPiece(g, D.segs[k], PAL.creamM); } else piece(g, D.segs[k], st); g.restore(); };
  for (let k = 0; k < segs; k++) seg(k);
  if (segs < 5) { if (wings) drawWing(g, root, pose.wN, 1, 0.97, false, wingCream, wingSquash); return P; }
  g.save(); g.translate(P[5][0], P[5][1]); g.rotate(pose.ang[5]);
  if (neckCream) { g.scale(1, neckSquash); creamPiece(g, D.head, PAL.creamD); }
  else { g.save(); g.translate(30, -12); g.rotate(-pose.jaw); piece(g, D.jaw, st); g.restore(); piece(g, D.head, st); }
  g.restore();
  if (pose.claw !== undefined && !neckCream) { const a0 = pose.ang[1]; g.save(); g.translate(P[1][0] + Math.sin(a0) * 30, P[1][1] - Math.cos(a0) * 30); g.rotate(pose.claw); piece(g, D.claw, st); g.restore(); }
  for (let k = 1; k < (neckCream ? 3 : 6); k++) { g.save(); g.translate(P[k][0], P[k][1]); piece(g, D.pin, st); g.restore(); }
  if (wings) drawWing(g, root, pose.wN, 1, 0.97, false, wingCream, wingSquash);
  return P;
}
// mouth position (local) for fire
export function dragonMouth(pose) { const P = dragonJoints(pose), a = pose.ang[5], hx = 100, hy = -12; return [P[5][0] + Math.cos(a) * hx - Math.sin(a) * hy, P[5][1] + Math.sin(a) * hx + Math.cos(a) * hy]; }

// ================================================================== tissue-paper FIRE (additive, alpha 0.6)
const F = {};
function buildFire() {
  F.v = ['M 0 0 C 10 -14 28 -20 46 -15 C 56 -24 68 -22 76 -31 C 79 -20 74 -14 84 -11 C 94 -13 103 -20 112 -28 C 110 -13 104 -3 96 3 C 105 7 113 10 120 17 C 105 21 91 16 80 18 C 64 26 40 23 24 15 C 12 11 4 7 0 0 Z',
    'M 0 0 C 12 -12 30 -16 44 -12 C 54 -26 66 -26 72 -36 C 76 -24 72 -16 82 -12 C 92 -10 104 -14 116 -10 C 106 -2 100 2 92 6 C 100 12 106 16 110 24 C 96 22 86 18 74 20 C 58 24 36 22 22 14 C 10 10 3 6 0 0 Z',
    'M 0 0 C 8 -15 24 -22 40 -18 C 52 -20 62 -14 70 -22 C 74 -14 72 -8 80 -6 C 92 -10 100 -18 106 -30 C 108 -16 106 -6 100 0 C 108 4 114 6 122 6 C 112 14 98 14 88 14 C 74 24 52 26 30 18 C 14 14 5 8 0 0 Z'].map((d, k) => torn(d, { seed: 400 + k, amp: 0.9, hf: 0.6, fib: 0.8 }));
}
// jet along +x from the origin (local +y = upward on screen for a left-down jet); amt 0..1, k = flicker drawing index (on 2s)
export function drawFire(g, amt, k) {
  if (amt <= 0) return;
  g.save(); g.globalCompositeOperation = 'lighter';
  const N = 12;
  for (let j = 0; j < N; j++) {
    const u = j / (N - 1); if (u > amt * 1.04) break;
    const d = 6 + 228 * u * amt, s = (0.32 + 0.82 * u) * (0.78 + 0.22 * amt), lift = 0.0009 * d * d, sp = ((j % 3) - 1) * 0.2 * u + 0.08 * Math.sin(k * 2.1 + j * 1.7);
    g.save(); g.translate(d, -lift * 0.0 + lift); g.rotate(sp + 0.002 * d); g.scale(s, s * (0.9 + 0.18 * Math.sin(k * 1.3 + j)));
    g.globalAlpha = 0.6; g.fillStyle = rgb(j % 4 === 3 ? [235, 70, 12] : PAL.fireO); g.fill(F.v[(j + k) % 3].p);
    g.scale(0.66, 0.58); g.translate(14, 0); g.fillStyle = rgb(PAL.fireY); g.fill(F.v[(j + k + 1) % 3].p);
    g.restore();
  }
  g.restore();
}

// ================================================================== the child's HANDS (right hand; wrist at 0,0, fingers toward -y, thumb on -x; mirror for left)
const H = { fingers: [[-26, -66, -0.22, 30, 24, 17], [-9, -73, -0.07, 34, 26, 18], [9, -72, 0.07, 31, 24, 17], [25, -63, 0.24, 24, 19, 14.5]], thumb: [-35, -24, -0.9, 27, 23, 19] };
function capsule(w, L, tipR = 1) { const r = w / 2; return `M ${-r} 3 L ${-r} ${-L + r} Q ${-r} ${-L - r * 0.15 * tipR} 0 ${-L - r * 0.1} Q ${r} ${-L - r * 0.15 * tipR} ${r} ${-L + r} L ${r} 3 Z`; }
function buildHands() {
  H.palm = cut('M -40 8 C -45 -18 -44 -48 -36 -68 C -18 -79 16 -79 36 -67 C 44 -46 44 -18 39 8 Z', { seed: 500, amp: 0.6 });
  H.cuff = cut('M -46 26 Q -34 21 -23 26 Q -11 21 0 26 Q 11 21 23 26 Q 34 21 46 26 L 49 76 L -49 76 Z', { seed: 501, amp: 0.6 });
  H.arm = cut('M -36 4 L 36 4 L 44 70 L 56 430 L -58 430 L -44 70 Z', { seed: 502, amp: 0.8 });
  H.seg = H.fingers.map((f, k) => [cut(capsule(f[5], f[3]), { seed: 510 + k, amp: 0.4 }), cut(capsule(f[5] * 0.94, f[4], 2), { seed: 520 + k, amp: 0.4 })]);
  H.tseg = [cut(capsule(H.thumb[5], H.thumb[3]), { seed: 530, amp: 0.4 }), cut(capsule(H.thumb[5] * 0.95, H.thumb[4], 2), { seed: 531, amp: 0.4 })];
}
// h: { x, y, rot, s, mirror, curl (0..1 fingers), pinch (0..1 thumb), spread }
export function drawHand(g, h) {
  const st = INK(1.5), c = h.curl || 0;
  g.save(); g.translate(h.x, h.y); g.rotate(h.rot); g.scale(h.mirror ? -h.s : h.s, h.s);
  piece(g, H.arm, st); piece(g, H.cuff, st);
  const T = H.thumb; g.save(); g.translate(T[0], T[1]); g.rotate(T[2] + 0.5 * (h.pinch || 0)); piece(g, H.tseg[0], st); g.translate(0, -T[3] + 6); g.rotate(0.45 * (h.pinch || 0)); piece(g, H.tseg[1], st); g.restore();
  piece(g, H.palm, st);
  H.fingers.forEach((f, k) => {
    g.save(); g.translate(f[0], f[1]); g.rotate(f[2] * (1 + (h.spread || 0)) - 0.18 * c);
    g.scale(1, 1 - 0.18 * c); piece(g, H.seg[k][0], st);
    g.translate(0, -f[3] + f[5] * 0.3); g.rotate(-0.5 * c); g.scale(1, 1 - 0.22 * c); piece(g, H.seg[k][1], st); g.restore();
  });
  g.restore();
}

// ================================================================== ORIGAMI BIRD (lighter paper; body centre 0,0; faces right). wing: 'up' | 'mid' | 'down' | 'rest'
const B = {};
const WT = { up: [[-26, -122], [6, -118]], rest: [[-30, -118], [4, -112]], mid: [[-98, -42], [-76, -54]], down: [[-44, 70], [-22, 64]] };
function buildBird() {
  B.tail = [[-40, 2], [-114, -40], [-24, -6]];
  B.bodyU = [[-40, 2], [-4, -14], [48, -4], [0, 4]];
  B.bodyL = [[-40, 2], [0, 4], [48, -4], [2, 19]];
  B.neck = [[30, -9], [50, -4], [94, -60], [84, -64]];
  B.head = [[84, -64], [94, -60], [111, -51], [97, -49]];
}
function facet(g, pts, col, seed) { const sh = cut(poly(pts), { seed, amp: 0.25, hf: 0.1, fib: 0.15 }); g.fillStyle = rgb(col); g.fill(sh.p); g.fillStyle = ST.cream; g.globalCompositeOperation = 'multiply'; g.fill(sh.p); g.globalCompositeOperation = 'source-over'; return sh; }
// b: { x, y, s, rot, wing, stage: undefined (cream bird) | 'd2' (dark body, cream neck/wings) | 'ib3' (body half flipped) }
export function drawBird(g, b) {
  g.save(); g.translate(b.x, b.y); g.rotate(b.rot || 0); g.scale(b.s, b.s);
  const [tn, tf] = WT[b.wing || 'rest'], ln = [], st = b.stage; g.lineJoin = 'round';
  const dark = (pts, seed, alt) => { const sh = cut(poly(pts), { seed, amp: 0.25, hf: 0.1, fib: 0.15 }); piece(g, sh, { fill: alt ? ST.inkB : ST.ink, tex: ST.inkTex, rimStyle: ST.rim, rimW: 1.3 }); };
  ln.push(facet(g, [[4, -12], [34, -8], tf], PAL.creamD, 601));
  if (st === 'd2') { dark(B.tail, 602); dark(B.bodyL, 603, true); dark(B.bodyU, 604); ln.push(facet(g, [[30, -9], [50, -4], [104, -74], [92, -78]], PAL.creamM, 605)); }
  else if (st === 'ib3') { ln.push(facet(g, B.tail, PAL.creamM, 602)); dark(B.bodyL, 603, true); dark(B.bodyU, 604); ln.push(facet(g, [[0, -4], [48, -4], [-4, -14]], PAL.creamL, 609)); ln.push(facet(g, B.neck, PAL.creamM, 605)); ln.push(facet(g, [[84, -64], [94, -60], [101, -57], [91, -56]], PAL.creamD, 606)); }
  else { ln.push(facet(g, B.tail, PAL.creamM, 602)); ln.push(facet(g, B.bodyL, PAL.creamD, 603)); ln.push(facet(g, B.bodyU, PAL.creamL, 604)); ln.push(facet(g, B.neck, PAL.creamM, 605)); ln.push(facet(g, B.head, PAL.creamD, 606)); }
  const wn1 = [[-12, -11], [8, -9], tn], wn2 = [[8, -9], [30, -8], tn];
  const down = b.wing === 'down'; ln.push(facet(g, wn1, down ? PAL.creamM : PAL.creamL, 607)); ln.push(facet(g, wn2, down ? PAL.creamD : PAL.creamM, 608));
  g.strokeStyle = rgb(PAL.crease, 0.8); g.lineWidth = 1.1 / Math.max(0.6, b.s); for (const sh of ln) g.stroke(sh.p);
  g.restore();
}

// ================================================================== the FOLD (S3): shape swaps. 0 dragon | 0.5 wings flipping | 1 wings folded (cream backs) | 1.5 neck flipping
export const WFOLD = { n: [-2.25, 2.75], f: [-2.05, 2.6] };
export function drawFolded(g, pose, stage) {
  if (stage === 0) { drawDragon(g, pose); return; }
  const half = (a, b) => [lerp(a[0], b[0], 0.5), lerp(a[1], b[1], 0.5)];
  if (stage === 0.5) { drawDragon(g, { ...pose, wN: half(pose.wN, WFOLD.n), wF: half(pose.wF, WFOLD.f) }, { wingCream: true, wingSquash: 0.3 }); return; }
  const p1 = { ...pose, jaw: 0.04, wN: WFOLD.n, wF: WFOLD.f };
  if (stage === 1) { drawDragon(g, p1, { wingCream: true, wingSquash: 0.62 }); return; }
  // neck folding toward us: foreshortened to a short cream flap on its hinge (joint 3), the rest of the body still dark
  const P = drawDragon(g, p1, { wingCream: true, wingSquash: 0.62, segs: 3 }), a = P[3], b = P[5], dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy), nx = -dy / L * 27, ny = dx / L * 27;
  const sh = cut(poly([[a[0] + nx, a[1] + ny], [a[0] + dx * 0.36 + nx * 0.5, a[1] + dy * 0.36 + ny * 0.5], [a[0] + dx * 0.42, a[1] + dy * 0.42], [a[0] + dx * 0.36 - nx * 0.5, a[1] + dy * 0.36 - ny * 0.5], [a[0] - nx, a[1] - ny]]), { seed: 731, amp: 0.3 });
  creamPiece(g, sh, PAL.creamM);
}

export function buildPuppets() { buildKing(); buildSoldier(); buildDragon(); buildFire(); buildHands(); buildBird(); }
