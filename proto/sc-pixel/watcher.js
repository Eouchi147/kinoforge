// P13 watcher: blocky figure in a long coat, hat, seen from behind. Everything animates on 2s (pose frame = floor(f/2)*2).
// Timeline (absolute frames): weight shift 120-132 | window lights 130 | head: anticipation 134-137, turn 138-140, settle 141-146 | S3 step: foot1 plants 186, foot2 plants 194.
import * as THREE from 'three';
import { P, K, flat, colorBox } from './palette.js';

const sm = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
function kf(keys, f) { // piecewise smooth interpolation through [[frame, value], ...]
  if (f <= keys[0][0]) return keys[0][1]; if (f >= keys[keys.length - 1][0]) return keys[keys.length - 1][1];
  for (let i = 0; i < keys.length - 1; i++) { const [a, va] = keys[i], [b, vb] = keys[i + 1]; if (f >= a && f <= b) return va + (vb - va) * sm(a, b, f); }
}
export const HEAD_KEYS = [[133, 0], [136, -0.11], [137.5, -0.08], [138, 0.02], [139, 0.42], [140, 0.74], [143, 0.58], [146, 0.64], [150, 0.6]];

export function buildWatcher() {
  const root = new THREE.Group(); const hips = new THREE.Group(); hips.position.y = 0.95; root.add(hips);
  const box = (w, h, d, c, x, y, z, par) => { const m = colorBox(w, h, d, c); m.position.set(x, y, z); par.add(m); return m; };
  const INK = { pz: P.inkFace, px: P.inkSide, nx: P.inkSide, py: K(0, 1, 2), ny: P.inkSide, nz: P.inkSide };
  const SLV = { pz: K(0, 1, 2), px: P.inkSide, nx: P.inkSide, py: K(0, 2, 3), ny: P.inkSide };
  const rimL = new THREE.MeshBasicMaterial({ color: P.cyan }), rimA = new THREE.MeshBasicMaterial({ color: P.cyan }), rimR = new THREE.MeshBasicMaterial({ color: P.mag });
  const rim = (par, x, y, z, h, mat, w = 0.035) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); m.position.set(x, y, z); par.add(m); return m; };
  // legs (pivot at hip)
  const legs = [-1, 1].map((s) => { const g = new THREE.Group(); g.position.set(s * 0.1, 0, 0); hips.add(g); box(0.14, 0.82, 0.17, INK, 0, -0.41, 0, g); box(0.16, 0.1, 0.28, { def: P.black, py: K(0, 1, 2) }, 0, -0.9, -0.05, g); return g; });
  // spine: torso, shoulder yoke, collar, arms, belt, seam
  const spine = new THREE.Group(); hips.add(spine);
  { // torso = one extruded back-view outline: sloped shoulders, tapered waist (reads as a coat, not stacked boxes); flat colour, silhouette first
    const sh = new THREE.Shape(); const pts = [[-0.22, 0], [-0.25, 0.3], [-0.265, 0.5], [-0.365, 0.595], [-0.11, 0.7], [0.11, 0.7], [0.365, 0.595], [0.265, 0.5], [0.25, 0.3], [0.22, 0]];
    sh.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) sh.lineTo(pts[i][0], pts[i][1]); sh.closePath();
    const tg = new THREE.ExtrudeGeometry(sh, { depth: 0.28, bevelEnabled: false }); tg.translate(0, 0, -0.14); spine.add(new THREE.Mesh(tg, flat(K(0, 0, 1)))); }
  box(0.1, 0.13, 0.3, { def: P.inkFace, py: K(0, 2, 3), px: K(0, 1, 2) }, -0.14, 0.7, 0.0, spine); box(0.1, 0.13, 0.3, { def: P.inkFace, py: K(0, 2, 3), nx: K(0, 1, 2) }, 0.14, 0.7, 0.0, spine); // collar points
  const arms = [-1, 1].map((s) => { const g = new THREE.Group(); g.position.set(s * 0.305, 0.6, 0.0); spine.add(g); box(0.12, 0.62, 0.16, SLV, 0, -0.31, 0, g); return g; });
  box(0.46, 0.05, 0.29, { pz: K(0, 1, 2), px: K(0, 1, 2), nx: K(0, 1, 2) }, 0, 0.05, 0, spine);
  { const a = rim(spine, -0.2885, 0.6265, 0.142, 0.032, rimA, 0.17); a.rotation.z = 0.39; const b = rim(spine, 0.2885, 0.6265, 0.142, 0.032, rimR, 0.17); b.rotation.z = -0.39; } // shoulder-line highlights follow the slope
  rim(arms[0], -0.05, -0.31, 0.083, 0.62, rimL, 0.03); rim(arms[1], 0.05, -0.31, 0.083, 0.62, rimR, 0.03);
  // head pivot at the neck
  const head = new THREE.Group(); head.position.set(0, 0.74, 0); spine.add(head);
  box(0.22, 0.23, 0.22, { pz: P.inkFace, px: K(0, 1, 2), nx: P.inkSide, py: P.inkFace, ny: P.inkSide }, 0, 0.09, 0, head);
  box(0.47, 0.045, 0.47, { def: P.inkFace, py: K(0, 1, 2), ny: K(0, 1, 2) }, 0, 0.2, 0, head); box(0.25, 0.08, 0.25, { def: P.inkFace, py: K(0, 2, 3), px: K(0, 1, 2) }, 0, 0.26, 0, head); box(0.18, 0.06, 0.18, { def: P.inkFace, py: K(0, 2, 3), px: K(0, 1, 2) }, 0, 0.33, 0, head);
  rim(head, -0.095, 0.09, 0.115, 0.2, rimA, 0.03); rim(head, 0.095, 0.09, 0.115, 0.2, rimR, 0.03); rim(head, -0.215, 0.2, 0.235, 0.035, rimA, 0.05); rim(head, 0.215, 0.2, 0.235, 0.035, rimR, 0.05);
  // coat hem: 3 panels, each lags the one above by 3 frames; a core block closes the gaps
  box(0.58, 0.3, 0.27, INK, 0, -0.15, 0, hips);
  const hem = [-1, 0, 1].map((s, k) => { const g = new THREE.Group(); g.position.set(s * 0.2, -0.28, 0.11); hips.add(g); g.userData.flare = s * 0.05; box(0.21, 0.5, 0.05, INK, 0, -0.25, 0, g); box(0.21, 0.04, 0.052, { def: K(0, 1, 2) }, 0, -0.5, 0, g); g.userData.k = k; return g; });
  rim(hem[0], -0.1, -0.25, 0.03, 0.5, rimL, 0.025); rim(hem[2], 0.1, -0.25, 0.03, 0.5, rimR, 0.025);
  root.traverse((o) => { o.frustumCulled = false; });
  return { root, hips, spine, head, legs, arms, hem, rimL, rimA, rimR, base: { x: 0, z: 0 } };
}

// pose the figure for absolute frame f (call every frame; poses only change on even frames)
export function poseWatcher(w, f, { x0, z0, windowOn = 130 }) {
  const fp = Math.floor(f / 2) * 2; const t = fp / 24;
  const wind = 0.4 + 0.14 * Math.sin(t * 1.9) + 0.9 * sm(212, 239, fp);
  // weight shift (frame 120): hips slide +4.5 cm to the screen right, torso counter-leans, head tilts back over the new stance
  const ws = (g) => sm(120, 131, g); const w0 = ws(fp);
  // S3 step: body travel (two stages), foot plants at 186 and 194, bob on each plant
  const body = 0.22 * sm(180, 190, fp) + 0.22 * sm(188, 197, fp);
  const bob = -0.046 * Math.exp(-Math.pow((fp - 187) / 2.4, 2)) - 0.04 * Math.exp(-Math.pow((fp - 195) / 2.4, 2));
  const headLag = -0.022 * Math.exp(-Math.pow((fp - 189) / 2.4, 2)) - 0.018 * Math.exp(-Math.pow((fp - 197) / 2.4, 2)); // head settles 2 f after the body (overlap)
  const lean = 0.05 * Math.sin(Math.PI * sm(176, 180, fp)) * (fp < 181 ? 1 : 0) - 0.045 * sm(180, 186, fp) * (1 - sm(190, 198, fp));
  const breathe = Math.sin(t * Math.PI * 2 / 4);
  w.root.position.set(x0 + 0.045 * w0, bob, z0 - body);
  w.spine.rotation.z = -0.035 * w0; w.spine.rotation.x = lean; w.spine.rotation.y = 0.08 * sm(140, 154, fp); w.spine.scale.y = 1 + 0.012 * breathe; // shoulders follow the head a beat later
  // head: look at window
  const yaw = kf(HEAD_KEYS, fp); const nod = fp >= 133 && fp <= 140 ? -0.05 * Math.sin(Math.PI * (fp - 133) / 7) : 0;
  w.head.rotation.set(nod + 0.02 * w0 + (fp > 150 ? -0.02 : 0), yaw, 0.03 * w0 * 0 + 0.025 * w0);
  w.head.position.y = 0.74 + 0.012 * sm(133, 138, fp) * (1 - sm(150, 160, fp)) + headLag;
  // legs: planted-foot solver in z. foot targets: L swings 178->186, R swings 188->194
  const L = 0.9; const footL = z0 - 0.44 * sm(178, 186, fp), footR = z0 - 0.44 * sm(188, 194, fp);
  const rz = z0 - body; const ang = (fz) => Math.asin(Math.max(-0.9, Math.min(0.9, (rz - fz) / L)));
  w.legs[0].rotation.x = ang(footL); w.legs[1].rotation.x = ang(footR);
  w.arms[0].rotation.x = -0.5 * (ang(footL) - ang(footR)) * 0.5; w.arms[1].rotation.x = 0.5 * (ang(footL) - ang(footR)) * 0.5;
  // coat hem: lag 3 f per segment; sways with wind + inertia of the body travel
  w.hem.forEach((g, k) => { const lag = 3 * (k + 1); const fl = fp - lag; const tl = fl / 24; const vel = (0.22 * (sm(180, 190, fl + 1) - sm(180, 190, fl)) + 0.22 * (sm(188, 197, fl + 1) - sm(188, 197, fl)));
    const flutter = Math.sin(tl * 9.0 + k * 1.3) * 0.5 + Math.sin(tl * 14.3 + k * 2.1) * 0.25;
    g.rotation.z = g.userData.flare - (0.06 + 0.2 * wind) - 0.07 * wind * flutter; g.rotation.x = -14 * vel + 0.05 * wind * flutter - 0.1 * (sm(120, 126, fl) - sm(126, 134, fl)) * 0; });
  // rim colour: left rim turns amber the frame the window lights (motivated by the window)
  w.rimA.color.setHex(f >= windowOn ? (f < windowOn + 3 ? P.amberHot : P.amber) : P.cyan);
}
