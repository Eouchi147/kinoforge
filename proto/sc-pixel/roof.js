// P13 roof: wet roof slab, parapet lip, props with neon rim strips, puddles with jittering reflection dashes.
import * as THREE from 'three';
import { rng } from '/harness/kit/film.js';
import { P, K, flat, vcMat, colorBox } from './palette.js';

const strip = (g, x, y, z, w, h, hex) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), flat(hex)); m.position.set(x, y, z); g.add(m); return m; };

export function buildRoof(g, beacons) {
  const R = rng(77);
  // floor with a glow gradient toward the street edge (z=0): reflects the neon off wet tar
  const fg = new THREE.PlaneGeometry(140, 40, 1, 8); fg.rotateX(-Math.PI / 2); const pos = fg.attributes.position, col = new Float32Array(pos.count * 3), c = new THREE.Color(), a = new THREE.Color(P.skyMid), b = new THREE.Color(K(0, 1, 2)), hi = new THREE.Color(K(0, 2, 3));
  for (let i = 0; i < pos.count; i++) { const z = pos.getZ(i) + 20; const t = Math.min(1, z / 14); c.copy(hi).lerp(b, Math.pow(t, 0.7)); col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b; }
  fg.setAttribute('color', new THREE.BufferAttribute(col, 3)); const floor = new THREE.Mesh(fg, vcMat); floor.position.set(0, 0, 20 - 0.4); g.add(floor);
  // parapet lip along the street edge
  const lip = colorBox(140, 0.55, 0.5, { pz: K(0, 1, 2), py: K(1, 3, 4), px: K(0, 1, 2), nx: K(0, 1, 2), nz: K(0, 0, 1) }); lip.position.set(0, 0.275, -0.15); g.add(lip);
  strip(g, 0, 0.5, 0.11, 140, 0.05, P.cyanDim); // wet highlight on the lip edge
  // AC unit, tank on legs, stair hut: mid-ground silhouettes
  const ac = colorBox(2.6, 1.2, 1.7, { pz: P.inkFace, px: P.inkSide, nx: P.inkSide, py: K(0, 2, 3) }); ac.position.set(6.2, 0.6, 3.6); g.add(ac); strip(g, 4.93, 0.6, 4.46, 0.06, 1.2, P.cyanDim);
  const hut = colorBox(3.4, 2.9, 2.6, { pz: P.inkFace, px: P.inkSide, nx: P.inkSide, py: K(0, 2, 3) }); hut.position.set(13, 1.45, 7.4); g.add(hut); strip(g, 13, 1.1, 8.72, 0.9, 1.7, K(0, 0, 0));
  // antenna mast with a magenta beacon
  const mast = colorBox(0.16, 3.3, 0.16, { def: P.inkFace, px: K(0, 1, 2) }); mast.position.set(-6.2, 1.65, 1.4); g.add(mast); const bar = colorBox(1.0, 0.12, 0.12, { def: P.inkFace }); bar.position.set(-6.2, 2.6, 1.4); g.add(bar); strip(g, -6.12, 1.65, 1.49, 0.04, 3.3, P.cyanDim);
  beacons.add(g, -6.2, 3.45, 1.5, 0.2, { hex: P.mag, period: 1.0, phase: 0.2, duty: 0.2, off: P.inkFace });
  for (let k = 0; k < 9; k++) { const z0 = 1.2 + k * 1.15 + k * k * 0.07; const st = new THREE.Mesh(new THREE.PlaneGeometry(140, 0.09 + k * 0.012), flat(K(0, 1, 2))); st.rotation.x = -Math.PI / 2; st.position.set(0, 0.006, z0); g.add(st); }
  // puddles + reflection dashes (animated in update on 2s)
  const pud = [[-0.2, 1.1, 2.2, 0.55], [2.3, 2.6, 1.6, 0.5], [-3.6, 3.4, 2.8, 0.7], [5.0, 1.4, 1.9, 0.45], [0.9, 4.6, 2.4, 0.7], [-7.0, 2.2, 2.0, 0.5], [8.8, 5.2, 2.6, 0.8]];
  const dashes = [];
  for (const [x, z, rx, rz] of pud) {
    const m = new THREE.Mesh(new THREE.CircleGeometry(1, 20), flat(K(0, 2, 3))); m.rotation.x = -Math.PI / 2; m.scale.set(rx, rz, 1); m.position.set(x, 0.012, z); g.add(m);
    for (let k = 0; k < 3; k++) { const hex = R() < 0.5 ? P.cyan : P.mag; const w = 0.35 + R() * 0.55; const d = new THREE.Mesh(new THREE.PlaneGeometry(w, 0.06), flat(hex)); d.rotation.x = -Math.PI / 2; d.position.set(x, 0.02, z); g.add(d); dashes.push({ d, x, z, rx, rz, k, seed: R() * 10, on: R() }); }
  }
  return { update(frame) { const n = Math.floor(frame / 2); for (const q of dashes) {
    const h = Math.sin(n * 12.9898 + q.seed * 78.233 + q.k * 3.1) * 43758.5453; const r1 = h - Math.floor(h), r2 = (h * 7.13) - Math.floor(h * 7.13);
    q.d.position.x = q.x + (r1 - 0.5) * q.rx * 1.2; q.d.position.z = q.z + (r2 - 0.5) * q.rz * 1.0; q.d.visible = ((n + q.k * 3) % 5) < 4 || q.on < 0.3; } } };
}
