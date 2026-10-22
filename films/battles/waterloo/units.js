// Waterloo: film-side additions to the Battle Map v2 engine (no engine file changed). Registered from index.html before the film starts.
// - FIG_KINDS.artillery: a field gun on its carriage with two gunners (instanced like every other figure: one gun per tray cell).
// - glyphs: `tricolore` (the French standard with an eagle finial) and `brig` (a flat two-masted sailing ship), drawn in the v2 style:
//   one ink weight, flat fills, a paper halo from drawIcon, no faces, no shine.
import * as THREE from 'three';
import { FIG_KINDS } from '/films/lib/battlemap/figures.js';
import { registerIcon, INK, PAPER, GOLD, GOLD_D, TEAM_RGB } from '/films/lib/battlemap/icons.js';

// ------------------------------------------------------------------ the gun figure (local: x right, y up, z forward, fits a 1 x 1 cell)
// roles as in the engine's figures.js: 0 team cloth, 1 metal, 3 wood, 5 dark, 6 gold (here: the bronze of the barrel)
function gunGeo() {
  const P = [], N = [], R = [];
  const tri = (a, b, c, role) => { const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2], vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2]; let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; const l = Math.hypot(nx, ny, nz) || 1;
    for (const p of [a, b, c]) { P.push(p[0], p[1], p[2]); N.push(nx / l, ny / l, nz / l); R.push(role); } };
  const quad = (a, b, c, d, role) => { tri(a, b, c, role); tri(a, c, d, role); };
  const box = (cx, cz, hx, hz, y0, y1, role, tx = hx, tz = hz) => { const b = [[cx - hx, y0, cz - hz], [cx + hx, y0, cz - hz], [cx + hx, y0, cz + hz], [cx - hx, y0, cz + hz]], t = [[cx - tx, y1, cz - tz], [cx + tx, y1, cz - tz], [cx + tx, y1, cz + tz], [cx - tx, y1, cz + tz]];
    quad(t[3], t[2], t[1], t[0], role); for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; quad(b[k], b[k2], t[k2], t[k], role); } };
  const beam = (a, b, hw, role) => { const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]; const L = Math.hypot(...d); const u = d.map((v) => v / L); const s = Math.abs(u[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0];
    let r = [u[1] * s[2] - u[2] * s[1], u[2] * s[0] - u[0] * s[2], u[0] * s[1] - u[1] * s[0]]; const rl = Math.hypot(...r); r = r.map((v) => v / rl * hw); let q = [u[1] * r[2] - u[2] * r[1], u[2] * r[0] - u[0] * r[2], u[0] * r[1] - u[1] * r[0]]; const ql = Math.hypot(...q); q = q.map((v) => v / ql * hw);
    const c = (p, sr, sq) => [p[0] + r[0] * sr + q[0] * sq, p[1] + r[1] * sr + q[1] * sq, p[2] + r[2] * sr + q[2] * sq];
    const A = [c(a, -1, -1), c(a, 1, -1), c(a, 1, 1), c(a, -1, 1)], B = [c(b, -1, -1), c(b, 1, -1), c(b, 1, 1), c(b, -1, 1)];
    for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; quad(A[k], A[k2], B[k2], B[k], role); } quad(B[0], B[1], B[2], B[3], role); quad(A[3], A[2], A[1], A[0], role); };
  // two spoked wheels (rim of 10 segments, 5 spokes, hub)
  const wr = 0.21, wy = 0.21, wz = 0.04;
  for (const x of [-0.25, 0.25]) {
    for (let k = 0; k < 10; k++) { const a0 = k / 10 * Math.PI * 2, a1 = (k + 1) / 10 * Math.PI * 2; beam([x, wy + Math.cos(a0) * wr, wz + Math.sin(a0) * wr], [x, wy + Math.cos(a1) * wr, wz + Math.sin(a1) * wr], 0.024, 3); }
    for (let k = 0; k < 5; k++) { const a = k / 5 * Math.PI * 2 + 0.3; beam([x, wy, wz], [x, wy + Math.cos(a) * wr, wz + Math.sin(a) * wr], 0.012, 3); }
    box(x, wz, 0.035, 0.035, wy - 0.035, wy + 0.035, 5);
  }
  beam([-0.25, wy, wz], [0.25, wy, wz], 0.025, 5);                        // axle
  for (const x of [-0.075, 0.075]) beam([x, 0.27, 0.12], [x * 0.6, 0.03, -0.56], 0.035, 3); // the carriage cheeks running down to the trail
  box(0, -0.56, 0.07, 0.04, 0, 0.06, 3);                                   // trail end on the ground
  beam([0, 0.31, -0.16], [0, 0.35, 0.58], 0.056, 6);                       // bronze barrel
  beam([0, 0.35, 0.55], [0, 0.355, 0.62], 0.068, 6);                       // muzzle swell
  box(0, -0.18, 0.06, 0.05, 0.27, 0.37, 6);                                // breech and cascabel
  // two gunners: one at the trail with a handspike, one by the muzzle with a rammer
  const gunner = (x, z, tool) => { box(x, z, 0.075, 0.05, 0.0, 0.3, 5, 0.065, 0.045); box(x, z, 0.085, 0.055, 0.3, 0.58, 0, 0.075, 0.05); box(x, z, 0.045, 0.045, 0.58, 0.68, 1); box(x, z, 0.05, 0.05, 0.68, 0.8, 5, 0.055, 0.055); tool(); };
  gunner(0.36, -0.36, () => beam([0.30, 0.05, -0.30], [0.42, 0.62, -0.42], 0.014, 3));
  gunner(-0.38, 0.40, () => beam([-0.30, 0.10, 0.60], [-0.44, 0.78, 0.22], 0.014, 3));
  const g = new THREE.InstancedBufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('aN', new THREE.Float32BufferAttribute(N, 3)); g.setAttribute('aRole', new THREE.Float32BufferAttribute(R, 1)); return g;
}

// ------------------------------------------------------------------ glyphs
const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const ink = (g, lw = 2.6) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; g.stroke(); };
const fillInk = (g, fill, lw = 2.6) => { g.fillStyle = fill; g.fill(); ink(g, lw); };
function tricolore(g, o) { // staff, gold eagle finial, a square flag in three vertical bands that moves with the wind
  const wave = Math.sin((o.t || 0) * 2.2) * 1.6;
  g.beginPath(); g.moveTo(30, 99); g.lineTo(30, 16); ink(g, 5.2); g.beginPath(); g.moveTo(30, 99); g.lineTo(30, 16); g.lineWidth = 2.2; g.strokeStyle = GOLD; g.stroke();
  g.beginPath(); g.moveTo(22, 12); g.quadraticCurveTo(26, 4, 30, 9); g.quadraticCurveTo(34, 4, 38, 12); g.lineTo(30, 17); g.closePath(); fillInk(g, GOLD, 1.8); // the eagle, as a flat wing shape
  const band = (x0, x1, col) => { g.beginPath(); g.moveTo(x0, 20 + wave * (x0 - 31) / 60); g.lineTo(x1, 20 + wave * (x1 - 31) / 60); g.lineTo(x1, 58 + wave * (x1 - 31) / 60); g.lineTo(x0, 58 + wave * (x0 - 31) / 60); g.closePath(); g.fillStyle = col; g.fill(); };
  band(31, 51, rgb(TEAM_RGB.carthage)); band(51, 71, PAPER); band(71, 91, '#b8302a');
  g.beginPath(); g.moveTo(31, 20); g.lineTo(91, 20 + wave); g.lineTo(91, 58 + wave); g.lineTo(31, 58); g.closePath(); ink(g, 2.4);
  for (let x = 34; x <= 90; x += 5) { g.beginPath(); g.moveTo(x, 58 + wave * (x - 31) / 60); g.lineTo(x, 63 + wave * (x - 31) / 60); g.lineWidth = 1.5; g.strokeStyle = GOLD_D; g.stroke(); }
}
function brig(g, o) { // hull, two masts with square sails, a pennant in the team colour; it rocks gently
  const team = o.team || TEAM_RGB.carthage; const bob = Math.sin((o.t || 0) * 2) * 1.2; g.save(); g.translate(0, bob);
  for (const [x, h] of [[38, 18], [64, 24]]) { g.beginPath(); g.moveTo(x, 70); g.lineTo(x, h); ink(g, 3);
    for (const [y0, w] of [[h + 6, 13], [h + 24, 16]]) { g.beginPath(); g.moveTo(x - w, y0); g.lineTo(x + w, y0); g.quadraticCurveTo(x + w + 2, y0 + 9, x + w - 1, y0 + 16); g.lineTo(x - w + 1, y0 + 16); g.quadraticCurveTo(x - w - 2, y0 + 9, x - w, y0); g.closePath(); fillInk(g, PAPER, 2.2); } }
  g.beginPath(); g.moveTo(64, 24); g.lineTo(80, 21); g.lineTo(64, 18); g.closePath(); fillInk(g, rgb(team), 1.6);
  g.beginPath(); g.moveTo(84, 66); g.lineTo(96, 56); ink(g, 2.4); // bowsprit
  g.beginPath(); g.moveTo(8, 64); g.lineTo(88, 64); g.quadraticCurveTo(84, 80, 72, 84); g.lineTo(24, 84); g.quadraticCurveTo(12, 80, 8, 64); g.closePath(); fillInk(g, '#7a5232', 2.6);
  g.beginPath(); g.moveTo(14, 70); g.lineTo(86, 70); g.lineWidth = 3; g.strokeStyle = rgb(team); g.stroke();
  g.restore();
}

let done = false;
export function registerWaterloo() {
  if (done) return; done = true;
  FIG_KINDS.artillery = { geo: gunGeo, sp: [3.4, 4.2], sc: 0.6 };
  registerIcon('tricolore', tricolore); registerIcon('brig', brig);
}
