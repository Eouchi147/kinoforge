// P13 world: five depth layers (each a Group so S1 can slide them by whole art pixels), signs, the amber window W, the roof + watcher.
// World: +x right, +y up (0 = roof surface), -z away from camera. Roof edge z=0. Layers: far z-170, B3 z-85, B2 z-50 (holds W), B1 z-24 (flanks the slot), roof.
// Slot between the two B1 towers: x -8.8 .. -1.8; W sits behind it on B2 so S2 (cam x .9) and S3 (cam x 2.6) both see it through the slot.
import * as THREE from 'three';
import { rng } from '/harness/kit/film.js';
import { P, K, flat, halo } from './palette.js';
import { building, windowGrid, roofClutter } from './city.js';
import { Neon, Beacons, blimp } from './neon.js';
import { buildRoof } from './roof.js';
import { buildWatcher } from './watcher.js';

export const W_POS = [-12, 9.5, -49.9]; // the amber window (centre)
export const WATCHER = { x: 1.8, z: 0.74 };
export const BL_X0 = -30; // blimp start x (drifts 1 art px / 7 frames)
export const FLICK = { // [startFrame, length, level] level 0 = off, .5 = dim; the buzz in audio.py drops out on the same frames
  ring: [[22, 1, 0], [61, 2, 0], [80, 1, 0.5], [104, 1, 0], [145, 2, 0], [190, 2, 0.5]],
  zig: [[9, 2, 0], [31, 1, 0], [33, 2, 0], [52, 1, 0.5], [71, 3, 0], [98, 2, 0], [111, 1, 0.5], [150, 1, 0], [205, 2, 0.5]],
  eq: [[14, 3, 0.5], [44, 1, 0], [76, 1, 0], [99, 1, 0.5], [165, 1, 0]],
  stack: [[40, 1, 0.5], [88, 2, 0], [172, 1, 0.5]],
};
const pickWith = (dark, rates) => (i, j, R) => { const r = R(); let a = 0; for (const [p, hex] of rates) { a += p; if (r < a) return hex; } return dark; };

export function buildWorld(scene) {
  const neon = new Neon(), beacons = new Beacons(); const layers = [];
  const mk = (name, depth) => { const g = new THREE.Group(); g.name = name; scene.add(g); layers.push({ g, depth, name }); return g; };
  const far = mk('far', 178), b3 = mk('b3', 93), b2 = mk('b2', 58), b1 = mk('b1', 32), roofG = mk('roof', 7.3);
  // ---- far skyline: hazy lavender slabs, a few tall landmarks
  { const R = rng(11); let x = -340, n = 0; while (x < 340) { const w = 14 + R() * 18, h = R() < 0.18 ? 52 + R() * 34 : 16 + R() * 30, gap = R() < 0.4 ? 3 + R() * 9 : 0;
      building(far, { x0: x, x1: x + w, top: h, z: -170, d: 20, face: [P.farFace, K(2, 2, 4)], side: P.farSide, roof: P.farTop, gy0: 0, gy1: 60 });
      windowGrid(far, { x0: x + 1.5, x1: x + w - 1.5, yBot: 3, yTop: h - 2, z: -169.9, ww: 2.6, wh: 3.4, px: 5.8, py: 8, seed: 100 + n, pick: pickWith(K(1, 1, 2), [[0.1, K(2, 4, 5)], [0.16, K(1, 3, 4)]]) });
      if (R() < 0.45) roofClutter(far, { x0: x, x1: x + w, top: h, z: -170, d: 20, seed: 300 + n, face: P.farFace, roof: P.farTop, beacons: n % 2 ? beacons : null }); x += w + gap; n++; } }
  const bl = blimp(beacons); bl.position.set(BL_X0, 72, -160); far.add(bl);
  // ---- B3 mid skyline
  { const R = rng(23); let x = -170, n = 0; while (x < 170) { const w = 12 + R() * 14, h = 10 + R() * 22 + (R() < 0.2 ? 12 : 0), gap = R() < 0.2 ? 2 + R() * 4 : 0;
      building(b3, { x0: x, x1: x + w, top: h, z: -85, d: 22, face: [K(1, 2, 3), K(1, 3, 4)], side: K(0, 2, 3), roof: K(1, 3, 4), gy0: 0, gy1: 40 });
      windowGrid(b3, { x0: x + 1.2, x1: x + w - 1.2, yBot: 2, yTop: h - 1.5, z: -84.9, ww: 1.8, wh: 2.4, px: 3.6, py: 5, seed: 200 + n, pick: pickWith(K(0, 1, 3), [[0.12, P.winTeal], [0.08, P.winCyan], [0.02, P.winMag]]) });
      if (R() < 0.6) roofClutter(b3, { x0: x, x1: x + w, top: h, z: -85, d: 22, seed: 400 + n, face: K(0, 1, 3), roof: K(1, 3, 4), beacons: n % 3 ? beacons : null }); x += w + gap; n++; } }
  // ---- B2: the W building (+ neighbours kept low so the sky shows behind the watcher's head)
  const faceB2 = [K(0, 2, 3), K(1, 3, 3)], sideB2 = K(0, 1, 2);
  const b2s = [[-46, 10, 17, 500], [-120, -46, 26, 501], [10, 80, 7.5, 502]];
  for (const [x0, x1, top, sd] of b2s) {
    building(b2, { x0, x1, top, z: -50, d: 24, face: faceB2, side: sideB2, roof: K(1, 3, 4), gy0: -4, gy1: top });
    windowGrid(b2, { x0: x0 + 1.5, x1: x1 - 1.5, yBot: -4, yTop: top - 1.4, z: -49.9, ww: 1.8, wh: 2.4, px: 3.8, py: 4.6, seed: sd, skip: (x, y) => Math.abs(x - W_POS[0]) < 2.2 && Math.abs(y - W_POS[1]) < 3.0, pick: (i, j, R, x, y) => { const r = R(); if (Math.abs(x - W_POS[0]) < 7 && Math.abs(y - W_POS[1]) < 8) return K(0, 0, 1); return r < 0.07 ? P.winDim : r < 0.12 ? P.winTeal : r < 0.13 ? P.winCyan : K(0, 0, 1); } }); }
  roofClutter(b2, { x0: -46, x1: 10, top: 17, z: -50, d: 24, seed: 510, face: K(0, 1, 2), roof: K(1, 3, 4), beacons, avoid: [[-22, -6]] });
  // ---- B1: the two low towers flanking the slot
  const faceB1 = [K(0, 1, 2), K(0, 1, 3)], sideB1 = K(0, 0, 1);
  building(b1, { x0: -95, x1: -8.8, top: 10, z: -24, d: 6, face: faceB1, side: sideB1, roof: K(1, 3, 4), gy0: -3, gy1: 10 });
  building(b1, { x0: -1.8, x1: 75, top: 4.5, z: -24, d: 6, face: faceB1, side: sideB1, roof: K(0, 2, 3), gy0: -3, gy1: 4.5 });
  const winB1 = pickWith(K(0, 0, 1), [[0.14, P.winDim], [0.09, P.winTeal], [0.05, P.winCyan], [0.025, P.winMag]]);
  windowGrid(b1, { x0: -93, x1: -10.5, yBot: -3, yTop: 8.6, z: -23.9, ww: 1.3, wh: 1.8, px: 2.7, py: 3.6, seed: 600, pick: winB1, skip: (x, y) => (Math.abs(x + 14.5) < 3.2 && Math.abs(y - 4.2) < 3.2) || (Math.abs(x + 27) < 2.6 && Math.abs(y - 4.5) < 4) });
  windowGrid(b1, { x0: -0.5, x1: 73, yBot: -3, yTop: 3.4, z: -23.9, ww: 1.3, wh: 1.8, px: 2.7, py: 3.6, seed: 601, pick: winB1, skip: (x, y) => (Math.abs(x - 5.4) < 1.9 && Math.abs(y - 1.4) < 2.6) || (Math.abs(x - 14.2) < 2.8 && Math.abs(y - 1.7) < 2.6) });
  roofClutter(b1, { x0: -95, x1: -8.8, top: 10, z: -24, d: 6, seed: 610, face: K(0, 0, 1), roof: K(0, 2, 3), beacons });
  roofClutter(b1, { x0: -1.8, x1: 75, top: 4.5, z: -24, d: 6, seed: 611, face: K(0, 0, 1), roof: K(0, 2, 3), beacons, avoid: [[1.5, 9.5]] });
  { const e = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 13), flat(K(0, 3, 4))); e.position.set(-8.88, 3.5, -23.85); b1.add(e); }
  // neon: cyan ring left of the slot, magenta zigzag right of it, equalizer + stack farther out
  neon.sign(b1, 'ring', -14.5, 4.2, -23.8, 1.15, { on: P.cyan, dim: P.cyanDim, off: K(0, 1, 3), flick: FLICK.ring, haloI: 0.32, reach: 1.6 });
  neon.sign(b1, 'zig', 5.4, 1.4, -23.8, 0.5, { on: P.mag, dim: P.magDim, off: K(1, 0, 2), flick: FLICK.zig, haloI: 0.55, reach: 1.9 });
  neon.sign(b1, 'eq', -27, 4.5, -23.8, 0.9, { on: P.mag, on2: P.cyan, dim: P.magDim, off: K(1, 1, 2), flick: FLICK.eq, haloI: 0.4, reach: 1.8 });
  neon.sign(b1, 'stack', 14.2, 1.7, -23.8, 0.62, { on: P.cyan, on2: P.mag, dim: P.cyanDim, off: K(0, 1, 3), flick: FLICK.stack, haloI: 0.5, reach: 2.4, back: K(0, 2, 3) });
  neon.sign(b3, 'eq', -38, 22, -84.8, 2.2, { on: P.mag, on2: P.mag, dim: P.magDim, off: K(1, 1, 3), flick: [[27, 2, 0], [65, 1, 0]], haloI: 0.35, reach: 4 });
  neon.sign(b3, 'ring', 62, 20, -84.8, 2.8, { on: P.cyan, dim: P.cyanDim, off: K(0, 1, 3), flick: [[48, 2, 0.5]], haloI: 0.35, reach: 4 });
  // ---- W: the amber window (dark until frame 130); children: [0] glass, [1][2] mullions, [3] sill, [4] halo
  const wg = new THREE.Group(); wg.position.set(...W_POS); b2.add(wg);
  const wMat = new THREE.MeshBasicMaterial({ color: K(0, 0, 1) }); wg.add(new THREE.Mesh(new THREE.PlaneGeometry(2.6, 3.4), wMat));
  const mull = new THREE.MeshBasicMaterial({ color: K(0, 1, 2) }); const m1 = new THREE.Mesh(new THREE.PlaneGeometry(0.32, 3.4), mull), m2 = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 0.32), mull); m1.position.z = m2.position.z = 0.03; m2.position.y = 0.5; wg.add(m1, m2);
  const sill = new THREE.Mesh(new THREE.PlaneGeometry(3.2, 0.36), flat(K(0, 1, 2))); sill.position.set(0, -1.88, 0.02); wg.add(sill);
  const wHalo = halo(2.6, 3.4, K(6, 3, 0), { reach: 2.6, power: 1.5, intensity: 0, mix: true }); wHalo.position.z = -0.03; wg.add(wHalo);
  // ---- roof + watcher
  const roof = buildRoof(roofG, beacons); const watcher = buildWatcher(); roofG.add(watcher.root);
  return { layers, neon, beacons, roof, watcher, bl, W: { wMat, mull, wHalo, group: wg } };
}
