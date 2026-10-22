// Shared helpers for the Zong film: portrait cameras, light envelopes, the crisp detail-layer lantern, silhouettes.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, noise1 } from '/harness/kit/film.js';
import { rgba, mixc, hex, mul } from './paint.js';

export const WARM = [1.0, 0.47, 0.15];     // lantern light on paint (linear)
export const GLOW = [1.0, 0.6, 0.27];      // glow sprite colour (HDR via intensity)
export const fovV = (mm) => 2 * Math.atan(12 / mm) * 180 / Math.PI;
export const ASPECT = 9 / 16;

// camera pose {x,y,z,mm,yaw,pitch,roll}: planes sit at world z = -D, camera starts at z = 0 looking down -z
export function poseCamera(cam, p) {
  const x = p.x || 0, y = p.y || 0, z = p.z || 0, yaw = p.yaw || 0, pitch = p.pitch || 0;
  cam.fov = fovV(p.mm || 35); cam.aspect = ASPECT; cam.near = 0.05; cam.far = 40000; cam.position.set(x, y, z);
  cam.up.set(0, 1, 0); cam.lookAt(x + Math.sin(yaw) * Math.cos(pitch) * 100, y + Math.sin(pitch) * 100, z - Math.cos(yaw) * Math.cos(pitch) * 100);
  if (p.roll) cam.rotateZ(p.roll);
  cam.updateProjectionMatrix(); cam.updateMatrixWorld(); return cam;
}
// cameras sampled along a list of shots (for plane coverage)
export function coverCams(shots, key) {
  const out = [];
  for (const s of shots) { if (key && s.set !== key) continue; for (let i = 0; i <= 4; i++) { const u = i / 4; const c = new THREE.PerspectiveCamera(); poseCamera(c, s.cam(u * (s.t1 - s.t0), u)); out.push(c); } }
  if (!out.length) { const c = new THREE.PerspectiveCamera(); poseCamera(c, { mm: 35 }); out.push(c); }
  return out;
}
// lantern ignition: quick catch, flare, settle, living flicker (deterministic)
export function igniteEnv(t, t0, seed = 0, flare = 1.45, rise = 0.07) {
  if (t < t0) return 0; const u = t - t0; const a = ease.outCubic(clamp(u / rise)); const f = 1 + (flare - 1) * Math.exp(-Math.max(0, u - rise) / 0.18);
  return a * f * (1 + 0.05 * noise1(t * 8.3 + seed * 3.7, seed) + 0.025 * noise1(t * 21 + seed, seed + 2));
}
export const flick = (t, seed = 0) => 1 + 0.06 * noise1(t * 8.3 + seed * 3.7, seed) + 0.03 * noise1(t * 21 + seed, seed + 2);
export const wob = (t, seed = 0) => noise1(t * 0.35 + seed * 1.3, seed);

export function line(g, a, b, w, col, al = 1) { g.strokeStyle = rgba(col, al); g.lineWidth = w; g.lineCap = 'round'; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }

// crisp ship's lantern for the detail layer: cx,cy = centre of the glass; s = scale (px per unit, lantern ~ 1 wide x 1.5 tall); on 0..1.3
export function drawLantern(g, cx, cy, s, on, ang = 0) {
  g.save(); g.translate(cx, cy); g.rotate(ang);
  const w = 0.62 * s, h = 1.0 * s;
  g.fillStyle = rgba(mixc([46, 34, 28], [255, 214, 140], clamp(on, 0, 1)));
  g.beginPath(); g.moveTo(-w / 2, -h / 2); g.lineTo(w / 2, -h / 2); g.lineTo(w * 0.42, h / 2); g.lineTo(-w * 0.42, h / 2); g.closePath(); g.fill();
  g.fillStyle = rgba(mixc([255, 236, 190], [255, 252, 232], clamp(on, 0, 1)), clamp(on, 0, 1) * 0.9); g.beginPath(); g.ellipse(0, h * 0.08, w * 0.16, h * 0.26, 0, 0, Math.PI * 2); g.fill();
  g.strokeStyle = rgba([14, 11, 14]); g.lineWidth = Math.max(1, 0.06 * s); g.lineJoin = 'round';
  g.beginPath(); g.moveTo(-w / 2, -h / 2); g.lineTo(-w * 0.42, h / 2); g.moveTo(w / 2, -h / 2); g.lineTo(w * 0.42, h / 2); g.moveTo(0, -h / 2); g.lineTo(0, h / 2); g.stroke();
  g.fillStyle = rgba([14, 11, 14]); g.beginPath(); g.moveTo(-w * 0.62, -h / 2); g.lineTo(0, -h * 0.82); g.lineTo(w * 0.62, -h / 2); g.closePath(); g.fill(); g.fillRect(-w * 0.5, h / 2 - 0.02 * s, w, 0.12 * s);
  g.lineWidth = Math.max(1, 0.05 * s); g.beginPath(); g.arc(0, -h * 0.82, w * 0.12, 0, Math.PI * 2); g.stroke();
  g.restore();
}

// ------------------------------------------------------------------ silhouettes (faceless, dignified): standing figures from simple volumes
// P { x, yb (feet), h, face: -1|1, hat: 'tricorn'|'wig'|'none'|'cap', coat: 0..1 (length), col, rim, rimSide, arm: {...} }
function capsule(g, x0, y0, x1, y1, w0, w1) {
  const a = Math.atan2(y1 - y0, x1 - x0) + Math.PI / 2, c = Math.cos(a), s = Math.sin(a);
  g.beginPath(); g.moveTo(x0 + c * w0 / 2, y0 + s * w0 / 2); g.lineTo(x1 + c * w1 / 2, y1 + s * w1 / 2); g.lineTo(x1 - c * w1 / 2, y1 - s * w1 / 2); g.lineTo(x0 - c * w0 / 2, y0 - s * w0 / 2); g.closePath(); g.fill();
  g.beginPath(); g.arc(x0, y0, w0 / 2, 0, Math.PI * 2); g.arc(x1, y1, w1 / 2, 0, Math.PI * 2); g.fill();
}
export function paintPerson(C, P) {
  const g = C.g, R = C.R; const { x, yb, h } = P; const f = P.face || 1; const col = P.col || [12, 11, 20]; const u = h / 100;
  g.fillStyle = rgba(col); g.strokeStyle = rgba(col);
  const hipY = yb - 47 * u, shY = yb - 79 * u, headY = yb - 91 * u, sw = (P.shoulder || 17) * u;
  // legs
  const stride = (P.stride || 0) * u;
  capsule(g, x - 3.2 * u + stride * 0.5, hipY, x - 3.5 * u - stride * 0.5, yb - 4 * u, 8 * u, 5.5 * u);
  capsule(g, x + 3.2 * u - stride * 0.5, hipY, x + 3.5 * u + stride * 0.5, yb - 4 * u, 8 * u, 5.5 * u);
  g.beginPath(); g.ellipse(x - 3.5 * u - stride * 0.5 + f * 3 * u, yb - 1.5 * u, 6 * u, 2.6 * u, 0, 0, Math.PI * 2); g.ellipse(x + 3.5 * u + stride * 0.5 + f * 3 * u, yb - 1.5 * u, 6 * u, 2.6 * u, 0, 0, Math.PI * 2); g.fill();
  // coat: shoulders to knee, flaring
  const cl = P.coat ?? 0.7, hemY = lerp(hipY, yb - 12 * u, cl); const fl = (P.flare ?? 1) * u;
  g.beginPath(); g.moveTo(x - sw, shY + 3 * u); g.quadraticCurveTo(x - sw - 1 * u, shY - 3 * u, x - 5 * u, shY - 3 * u); g.lineTo(x + 5 * u, shY - 3 * u); g.quadraticCurveTo(x + sw + 1 * u, shY - 3 * u, x + sw, shY + 3 * u);
  g.lineTo(x + sw - 1.5 * u + (P.lean || 0) * u, hipY); g.quadraticCurveTo(x + 11 * fl + f * 2 * u, hemY - 8 * u, x + 14 * fl, hemY); g.lineTo(x - 14 * fl, hemY); g.quadraticCurveTo(x - 11 * fl + f * 2 * u, hemY - 8 * u, x - sw + 1.5 * u + (P.lean || 0) * u, hipY); g.closePath(); g.fill();
  // neck + head
  g.fillRect(x - 2.6 * u, shY - 6 * u, 5.2 * u, 7 * u);
  const hx = x + f * 1.2 * u + (P.lean || 0) * u * 0.6, hr = 6.4 * u;
  g.beginPath(); g.ellipse(hx, headY, hr * 0.86, hr * 1.06, 0, 0, Math.PI * 2); g.fill();
  if (P.hat === 'tricorn') { // brim a flattened triangle, crown low
    g.beginPath(); g.moveTo(hx - hr * 1.9, headY - hr * 0.55); g.lineTo(hx - hr * 0.2, headY - hr * 1.95); g.lineTo(hx + hr * 1.9, headY - hr * 0.55); g.quadraticCurveTo(hx, headY - hr * 0.2, hx - hr * 1.9, headY - hr * 0.55); g.closePath(); g.fill();
    g.beginPath(); g.ellipse(hx, headY - hr * 0.95, hr * 0.95, hr * 0.7, 0, 0, Math.PI * 2); g.fill();
  } else if (P.hat === 'wig') { // curled side rolls and a queue
    g.beginPath(); g.ellipse(hx, headY - hr * 0.35, hr * 1.18, hr * 1.1, 0, 0, Math.PI * 2); g.fill(); g.beginPath(); g.ellipse(hx - f * hr * 0.9, headY + hr * 0.8, hr * 0.62, hr * 0.8, 0, 0, Math.PI * 2); g.ellipse(hx + f * hr * 0.9, headY + hr * 0.8, hr * 0.62, hr * 0.8, 0, 0, Math.PI * 2); g.fill();
  } else if (P.hat === 'cap') { g.beginPath(); g.ellipse(hx, headY - hr * 0.55, hr * 1.0, hr * 0.62, 0, Math.PI, Math.PI * 2); g.fill(); g.fillRect(hx - hr * 1.0, headY - hr * 0.6, hr * 2.0, hr * 0.28); }
  // arms: each {a:[sx,sy] shoulder offset, e:[x,y] elbow, h:[x,y] hand} in units of u relative to (x, shY)
  for (const A of P.arms || []) { capsule(g, x + A.s[0] * u, shY + A.s[1] * u, x + A.e[0] * u, shY + A.e[1] * u, 6 * u, 5 * u); capsule(g, x + A.e[0] * u, shY + A.e[1] * u, x + A.h[0] * u, shY + A.h[1] * u, 5 * u, 4 * u); g.beginPath(); g.arc(x + A.h[0] * u, shY + A.h[1] * u, 2.6 * u, 0, Math.PI * 2); g.fill(); }
  // rim light dabs on the lit side (sparse, so it stays a painted silhouette)
  if (P.rim) { const sd = P.rimSide || -1; for (let k = 0; k < 26; k++) { const yy = lerp(shY - 4 * u, hemY, R()); const side = sd * (sw + (yy - shY) / (hemY - shY) * 6 * u) * 0.96; C.dab(x + side, yy, Math.PI / 2 + (R() - 0.5) * 0.2, 6 * u + R() * 9 * u, 1.4 * u + R() * 1.2 * u, P.rim, 0.55 + R() * 0.3, 0.03); }
    for (let k = 0; k < 6; k++) C.dab(hx + sd * hr * 0.8, headY - hr * 0.2 + R() * hr, Math.PI / 2, hr * 0.8, 1.3 * u, P.rim, 0.6, 0.0); }
  return { head: [hx, headY], shoulder: [x, shY], hip: [x, hipY], top: yb - h };
}
