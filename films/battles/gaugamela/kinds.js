// Gaugamela: the one army kind the engine does not have, built film-side (no engine change).
//  - FIG_KINDS.chariot: a scythed chariot as a miniature (two horses, a car with a team-coloured breastwork, two spoked wheels
//    with a blade out of each hub, a driver). Blocks use it with `figures: 'chariot'` (kind stays 'cavalry' for the tray).
//  - glyph 'u-chariot': the unit symbol for the legend key, drawn like the engine's unit frames (flat, one ink weight, team tint).
// Import this before startBattleMap (index.html).
import * as THREE from 'three';
import { FIG_KINDS } from '/films/lib/battlemap/figures.js';
import { registerIcon, TEAM_RGB, INK } from '/films/lib/battlemap/icons.js';

// the same geometry builder as the engine's figures (local x right, y up, z forward; one figure fits a 1 x 1 cell)
function builder() {
  const P = [], N = [], R = [];
  const tri = (a, b, c, role) => { const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2], vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2]; let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; const l = Math.hypot(nx, ny, nz) || 1;
    for (const p of [a, b, c]) { P.push(p[0], p[1], p[2]); N.push(nx / l, ny / l, nz / l); R.push(role); } };
  const quad = (a, b, c, d, role) => { tri(a, b, c, role); tri(a, c, d, role); };
  const box = (cx, cz, hx, hz, y0, y1, role, tx = hx, tz = hz) => {
    const b = [[cx - hx, y0, cz - hz], [cx + hx, y0, cz - hz], [cx + hx, y0, cz + hz], [cx - hx, y0, cz + hz]], t = [[cx - tx, y1, cz - tz], [cx + tx, y1, cz - tz], [cx + tx, y1, cz + tz], [cx - tx, y1, cz + tz]];
    quad(t[3], t[2], t[1], t[0], role); for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; quad(b[k], b[k2], t[k2], t[k], role); } };
  const beam = (a, b, hw, role) => { const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]; const L = Math.hypot(...d); const u = d.map((v) => v / L); const s = Math.abs(u[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0];
    let r = [u[1] * s[2] - u[2] * s[1], u[2] * s[0] - u[0] * s[2], u[0] * s[1] - u[1] * s[0]]; const rl = Math.hypot(...r); r = r.map((v) => v / rl * hw); let q = [u[1] * r[2] - u[2] * r[1], u[2] * r[0] - u[0] * r[2], u[0] * r[1] - u[1] * r[0]]; const ql = Math.hypot(...q); q = q.map((v) => v / ql * hw);
    const c = (p, sr, sq) => [p[0] + r[0] * sr + q[0] * sq, p[1] + r[1] * sr + q[1] * sq, p[2] + r[2] * sr + q[2] * sq];
    const A = [c(a, -1, -1), c(a, 1, -1), c(a, 1, 1), c(a, -1, 1)], B = [c(b, -1, -1), c(b, 1, -1), c(b, 1, 1), c(b, -1, 1)];
    for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; quad(A[k], A[k2], B[k2], B[k], role); } quad(B[0], B[1], B[2], B[3], role); };
  const cap = (cx, cy, cz, r, h, role) => { const b = [[cx - r, cy, cz - r], [cx + r, cy, cz - r], [cx + r, cy, cz + r], [cx - r, cy, cz + r]]; for (let k = 0; k < 4; k++) tri(b[k], b[(k + 1) % 4], [cx, cy + h, cz], role); };
  const done = () => { const g = new THREE.InstancedBufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('aN', new THREE.Float32BufferAttribute(N, 3)); g.setAttribute('aRole', new THREE.Float32BufferAttribute(R, 1)); return g; };
  return { box, beam, cap, done };
}
// roles: 0 team cloth, 1 metal, 3 wood, 4 horse coat, 5 leather
function chariotGeo() {
  const B = builder();
  for (const x of [-0.12, 0.12]) { // the team: two horses abreast
    for (const [lx, lz] of [[-0.035, 0.36], [0.035, 0.36], [-0.035, 0.14], [0.035, 0.14]]) B.box(x + lx, lz, 0.022, 0.026, 0.0, 0.25, 4);
    B.box(x, 0.25, 0.055, 0.16, 0.23, 0.38, 4, 0.05, 0.15);
    B.beam([x, 0.35, 0.38], [x, 0.50, 0.47], 0.035, 4); B.beam([x, 0.50, 0.46], [x, 0.44, 0.58], 0.03, 4);
    B.beam([x, 0.33, 0.10], [x, 0.22, 0.05], 0.015, 5);
  }
  B.beam([0, 0.30, -0.12], [0, 0.33, 0.36], 0.014, 3); B.beam([-0.16, 0.36, 0.34], [0.16, 0.36, 0.34], 0.012, 3); // pole and yoke
  B.box(0, -0.22, 0.15, 0.10, 0.15, 0.19, 3);                                   // floor
  B.box(0, -0.13, 0.15, 0.018, 0.19, 0.38, 0, 0.13, 0.016);                      // breastwork (team)
  for (const s of [-1, 1]) B.box(s * 0.145, -0.22, 0.012, 0.09, 0.19, 0.31, 0);  // side screens
  B.beam([-0.27, 0.15, -0.24], [0.27, 0.15, -0.24], 0.013, 3);                   // axle
  for (const s of [-1, 1]) { const wx = s * 0.23, cy = 0.15, cz = -0.24, r = 0.145; // spoked wheel, a blade out of the hub
    for (let k = 0; k < 8; k++) { const a0 = k / 8 * Math.PI * 2, a1 = (k + 1) / 8 * Math.PI * 2; B.beam([wx, cy + Math.sin(a0) * r, cz + Math.cos(a0) * r], [wx, cy + Math.sin(a1) * r, cz + Math.cos(a1) * r], 0.011, 3); }
    for (let k = 0; k < 4; k++) { const a = k / 4 * Math.PI + 0.39; B.beam([wx, cy - Math.sin(a) * r, cz - Math.cos(a) * r], [wx, cy + Math.sin(a) * r, cz + Math.cos(a) * r], 0.006, 3); }
    B.beam([s * 0.27, cy, cz], [s * 0.47, cy - 0.01, cz + 0.03], 0.01, 1); B.beam([s * 0.47, cy - 0.01, cz + 0.03], [s * 0.52, cy - 0.04, cz - 0.08], 0.008, 1);
  }
  B.box(0, -0.25, 0.055, 0.045, 0.19, 0.50, 0, 0.05, 0.04); B.box(0, -0.25, 0.04, 0.04, 0.50, 0.58, 1); B.cap(0, 0.58, -0.25, 0.05, 0.05, 1); // driver
  return B.done();
}
FIG_KINDS.chariot = { geo: chariotGeo, sp: [4.2, 5.0], sc: 1.15 };

// the legend's unit symbol: a frame in the team tint with a spoked wheel and its blade
const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const pale = (c, k) => [c[0] + (1 - c[0]) * k, c[1] + (1 - c[1]) * k, c[2] + (1 - c[2]) * k];
registerIcon('u-chariot', (g, o) => {
  const team = o.team || TEAM_RGB.carthage; g.lineJoin = 'round'; g.lineCap = 'round';
  g.beginPath(); g.rect(12, 34, 76, 50); g.fillStyle = rgb(pale(team, 0.62)); g.fill();
  g.save(); g.clip(); g.beginPath(); g.rect(12, 34, 76, 6); g.fillStyle = rgb(team); g.fill(); g.restore();
  g.beginPath(); g.rect(12, 34, 76, 50); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
  g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.arc(44, 63, 13, 0, 7); g.stroke();
  g.lineWidth = 2; g.beginPath(); for (let k = 0; k < 3; k++) { const a = k / 3 * Math.PI; g.moveTo(44 - Math.cos(a) * 13, 63 - Math.sin(a) * 13); g.lineTo(44 + Math.cos(a) * 13, 63 + Math.sin(a) * 13); } g.stroke();
  g.lineWidth = 3; g.beginPath(); g.moveTo(57, 63); g.lineTo(80, 63); g.lineTo(74, 57); g.stroke();
});
