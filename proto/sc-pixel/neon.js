// P13 neon: abstract emissive signs (bars, ring, zigzag, stack — no letters), blinking beacons, a drifting blimp.
import * as THREE from 'three';
import { P, K, flat, halo } from './palette.js';

const plane = (w, h, mat, x = 0, y = 0, z = 0, rot = 0) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); m.position.set(x, y, z); m.rotation.z = rot; return m; };

export class Neon {
  constructor() { this.signs = []; }
  // kind: eq | ring | zig | stack. flick: [[startFrame, len, level], ...] (level 0 off, .5 dim); everything else is fully on.
  sign(group, kind, x, y, z, s, { on, dim, on2 = null, off = P.skyLow, flick = [], haloI = 0.5, reach = 1.8, back = P.inkFace } = {}) {
    const g = new THREE.Group(); g.position.set(x, y, z); const mat = new THREE.MeshBasicMaterial({ color: on }); const mat2 = on2 ? new THREE.MeshBasicMaterial({ color: on2 }) : mat;
    let bw = 3 * s, bh = 3 * s;
    if (kind === 'eq') { bw = 4.4 * s; bh = 7 * s; g.add(plane(bw, bh, flat(back), 0, 0, 0.02)); const hs = [0.5, 0.88, 0.66, 1.0, 0.38];
      hs.forEach((v, k) => { const h = (bh - 0.8 * s) * v; g.add(plane(0.52 * s, h, k % 2 ? mat2 : mat, (k - 2) * 0.82 * s, -bh / 2 + 0.4 * s + h / 2, 0.05)); }); }
    else if (kind === 'ring') { const r = 1.6 * s; bw = bh = 2 * r + 0.8 * s; const bk = new THREE.Mesh(new THREE.CircleGeometry(r + 0.4 * s, 28), flat(back)); bk.position.z = 0.02; g.add(bk);
      const ring = new THREE.Mesh(new THREE.RingGeometry(r - 0.36 * s, r, 28), mat); ring.position.z = 0.05; g.add(ring); const dot = new THREE.Mesh(new THREE.CircleGeometry(0.46 * s, 14), mat2); dot.position.z = 0.05; g.add(dot); }
    else if (kind === 'zig') { bw = 3.4 * s; bh = 6.4 * s; g.add(plane(bw, bh, flat(back), 0, 0, 0.02)); const pts = [[-1, 2.3], [1, 1.1], [-1, -0.1], [1, -1.3], [-1, -2.5]];
      for (let k = 0; k < pts.length - 1; k++) { const [ax, ay] = pts[k], [bx, by] = pts[k + 1]; const dx = (bx - ax) * 0.55 * s, dy = (by - ay) * s * 1.0; const len = Math.hypot(dx, dy) + 0.3 * s; g.add(plane(0.4 * s, len, mat, (ax + bx) * 0.275 * s, (ay + by) * 0.5 * s, 0.05, Math.atan2(-dx, dy))); } }
    else if (kind === 'stack') { bw = 4.2 * s; bh = 4.6 * s; g.add(plane(bw, bh, flat(back), 0, 0, 0.02));
      for (let k = 0; k < 4; k++) g.add(plane(bw - 0.8 * s, 0.62 * s, k % 2 ? mat2 : mat, 0, bh / 2 - 0.7 * s - k * 1.05 * s, 0.05)); }
    const hl = halo(bw, bh, on, { reach, power: 1.5, intensity: haloI, circle: kind === 'ring' }); hl.position.z = 0.01; g.add(hl); group.add(g);
    const rec = { g, mat, mat2, on, on2: on2 ?? on, dim, off, flick, hl, haloI, level: 1, kind, hexNow: on, hex2Now: on2 ?? on, h: bh };
    this.signs.push(rec); return rec;
  }
  levelAt(rec, frame) { for (const [a, n, lv] of rec.flick) if (frame >= a && frame < a + n) return lv; return 1; }
  update(frame) {
    for (const r of this.signs) {
      const lv = this.levelAt(r, frame); if (lv === r.level) continue; r.level = lv;
      const c = lv >= 1 ? [r.on, r.on2] : lv > 0 ? [r.dim, r.dim] : [r.off, r.off];
      r.mat.color.setHex(c[0]); r.mat2.color.setHex(c[1]); r.hexNow = c[0]; r.hex2Now = c[1]; r.hl.userData.mat.uniforms.uI.value = r.haloI * (lv >= 1 ? 1 : lv > 0 ? 0.3 : 0);
    }
  }
}

export class Beacons {
  constructor() { this.list = []; }
  add(group, x, y, z, size = 1, { hex = P.mag, period = 1.0, phase = 0, duty = 0.22, off = null } = {}) {
    const mat = new THREE.MeshBasicMaterial({ color: hex }); const m = plane(size, size, mat, x, y, z); m.renderOrder = 4; group.add(m); this.list.push({ mat, hex, off: off ?? P.skyMid, period, phase, duty }); return m;
  }
  update(t) { for (const b of this.list) { const u = (((t / b.period) + b.phase) % 1 + 1) % 1; b.mat.color.setHex(u < b.duty ? b.hex : b.off); } }
}

export function blimp(beacons) {
  const g = new THREE.Group(); const E = (rx, ry, hex, x, y, z) => { const m = new THREE.Mesh(new THREE.CircleGeometry(1, 30), flat(hex)); m.scale.set(rx, ry, 1); m.position.set(x, y, z); return m; };
  g.add(E(23, 7.5, K(2, 2, 4), 0, 0, 0)); g.add(E(21.6, 4.1, K(1, 1, 3), 0, -3.2, 0.02)); g.add(E(15, 1.3, K(3, 3, 5), 3, 5.0, 0.04));
  const fin = (sx, sy, hex) => { const s = new THREE.Shape(); s.moveTo(0, 0); s.lineTo(-7 * sx, 8 * sy); s.lineTo(-1.5 * sx, 0); const m = new THREE.Mesh(new THREE.ShapeGeometry(s), flat(hex)); m.position.set(-19, sy > 0 ? 3 : -3, -0.02); return m; };
  g.add(fin(1, 1, K(2, 2, 4))); g.add(fin(1, -1, K(1, 1, 3)));
  g.add(plane(7, 2.2, flat(K(0, 1, 2)), 3, -8.2, 0.02)); for (let k = 0; k < 3; k++) g.add(plane(0.9, 0.9, flat(P.winCyan), 0.6 + k * 2.4, -8.2, 0.05));
  for (let k = 0; k < 3; k++) g.add(plane(14, 1.1, flat(k === 1 ? P.mag : P.magDim), 3, 3.0 - k * 2.3, 0.06));
  beacons.add(g, 22.8, 0.8, 0.1, 2.2, { hex: P.cyanHot, period: 1.5, phase: 0.1, duty: 0.3 }); beacons.add(g, -20.5, 0.4, 0.1, 2.2, { hex: P.mag, period: 1.5, phase: 0.6, duty: 0.3 });
  return g;
}
