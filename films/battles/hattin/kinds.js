// Hattin: the army and world kinds the engine does not have, built film-side (no engine change). Import before startBattleMap.
//  - FIG_KINDS.flame: a burning tuft of dry grass (three flame tongues on a charred patch), placed by the fire line in fx.js.
//  - FIG_KINDS.pavilion: King Guy's red tent (walls and a cone roof in the team colour, a pole), placed and felled by fx.js.
//  - glyph 'u-horse-archers': the legend's unit symbol (cavalry sign with a bow), drawn like the engine's unit frames.
import * as THREE from 'three';
import { FIG_KINDS } from '/films/lib/battlemap/figures.js';
import { registerIcon, TEAM_RGB, INK } from '/films/lib/battlemap/icons.js';

function builder() { // the engine's figure builder (local x right, y up, z forward; roles: 0 team cloth, 3 wood, 5 dark, 10 flame)
  const P = [], N = [], R = [];
  const tri = (a, b, c, role) => { const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2], vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2]; let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; const l = Math.hypot(nx, ny, nz) || 1;
    for (const p of [a, b, c]) { P.push(p[0], p[1], p[2]); N.push(nx / l, ny / l, nz / l); R.push(role); } };
  const quad = (a, b, c, d, role) => { tri(a, b, c, role); tri(a, c, d, role); };
  const box = (cx, cz, hx, hz, y0, y1, role, tx = hx, tz = hz) => {
    const b = [[cx - hx, y0, cz - hz], [cx + hx, y0, cz - hz], [cx + hx, y0, cz + hz], [cx - hx, y0, cz + hz]], t = [[cx - tx, y1, cz - tz], [cx + tx, y1, cz - tz], [cx + tx, y1, cz + tz], [cx - tx, y1, cz + tz]];
    quad(t[3], t[2], t[1], t[0], role); for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; quad(b[k], b[k2], t[k2], t[k], role); } };
  const cone = (cx, cy, cz, r, h, role, n = 6) => { for (let k = 0; k < n; k++) { const a0 = k / n * Math.PI * 2, a1 = (k + 1) / n * Math.PI * 2; tri([cx + Math.cos(a1) * r, cy, cz + Math.sin(a1) * r], [cx + Math.cos(a0) * r, cy, cz + Math.sin(a0) * r], [cx, cy + h, cz], role); } };
  const prism = (r, y0, y1, role, n = 8) => { for (let k = 0; k < n; k++) { const a0 = k / n * Math.PI * 2, a1 = (k + 1) / n * Math.PI * 2; const p0 = [Math.cos(a0) * r, Math.sin(a0) * r], p1 = [Math.cos(a1) * r, Math.sin(a1) * r]; quad([p1[0], y0, p1[1]], [p0[0], y0, p0[1]], [p0[0], y1, p0[1]], [p1[0], y1, p1[1]], role); } };
  const done = () => { const g = new THREE.InstancedBufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('aN', new THREE.Float32BufferAttribute(N, 3)); g.setAttribute('aRole', new THREE.Float32BufferAttribute(R, 1)); return g; };
  return { box, cone, prism, done };
}
function flameGeo() {
  const B = builder();
  B.box(0, 0, 0.42, 0.30, 0.0, 0.02, 5);                       // charred patch
  B.cone(0, 0.02, 0, 0.20, 0.95, 10); B.cone(0.17, 0.02, 0.08, 0.13, 0.62, 10); B.cone(-0.16, 0.02, -0.07, 0.14, 0.52, 10); B.cone(0.04, 0.02, -0.16, 0.10, 0.40, 10);
  return B.done();
}
function pavilionGeo() {
  const B = builder();
  B.prism(0.42, 0.0, 0.42, 0, 8);                               // walls
  B.cone(0, 0.42, 0, 0.50, 0.42, 0, 8);                         // roof
  B.box(0, 0, 0.018, 0.018, 0.80, 1.12, 3);                     // pole above the roof
  B.box(0.09, 0, 0.09, 0.008, 1.0, 1.1, 0);                     // pennant
  return B.done();
}
FIG_KINDS.flame = { geo: flameGeo, sp: [1, 1], sc: 1 };
FIG_KINDS.pavilion = { geo: pavilionGeo, sp: [1, 1], sc: 1 };

const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const pale = (c, k) => [c[0] + (1 - c[0]) * k, c[1] + (1 - c[1]) * k, c[2] + (1 - c[2]) * k];
registerIcon('u-horse-archers', (g, o) => {
  const team = o.team || TEAM_RGB.carthage; g.lineJoin = 'round'; g.lineCap = 'round';
  g.beginPath(); g.rect(12, 34, 76, 50); g.fillStyle = rgb(pale(team, 0.62)); g.fill();
  g.save(); g.clip(); g.beginPath(); g.rect(12, 34, 76, 6); g.fillStyle = rgb(team); g.fill(); g.restore();
  g.beginPath(); g.rect(12, 34, 76, 50); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
  g.strokeStyle = INK; g.fillStyle = INK; g.lineWidth = 3; g.beginPath(); g.moveTo(12, 84); g.lineTo(88, 40); g.stroke();
  g.lineWidth = 2.6; g.beginPath(); g.arc(42, 66, 11, -1.25, 1.25); g.stroke(); g.beginPath(); g.moveTo(46, 66); g.lineTo(64, 66); g.stroke();
  g.beginPath(); g.moveTo(66, 66); g.lineTo(60, 62); g.lineTo(60, 70); g.closePath(); g.fill();
});
