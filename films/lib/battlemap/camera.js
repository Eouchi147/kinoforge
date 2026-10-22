// Battle Map engine: camera keyframes. Orbit parametrisation: a target on the ground, a distance (or ground width), pitch (90 = looking straight down),
// yaw (compass bearing the camera looks toward: 0 = north/up the map, 90 = east), lens in mm. Keys are time-ordered; each key says HOW we arrive at it.
import { clamp, lerp } from './noise.js';
import { easeFn } from './timeline.js';

const PROPS = ['x', 'z', 'ty', 'dist', 'pitch', 'yaw', 'mm'];
export function normaliseKey(k, clock, aspect) {
  const t = clock.at(k.at); const mm = k.mm ?? 35; const o = { t, x: k.target?.[0] ?? k.x ?? 0, z: k.target?.[1] ?? k.z ?? 0, ty: k.ty ?? 0, pitch: k.pitch ?? 55, yaw: k.yaw ?? 0, mm, ease: k.ease || 'inOut', cut: !!k.cut };
  if (k.dist !== undefined) o.dist = k.dist; else { // fit a ground width: horizontal field of view from the lens
    const vf = 2 * Math.atan(12 / mm), hf = 2 * Math.atan(Math.tan(vf / 2) * aspect); o.dist = (k.width ?? 300) / (2 * Math.tan(hf / 2)); }
  o.shake = k.shake ?? 0; return o;
}
export class CameraTrack {
  constructor(keys) { this.k = keys.slice().sort((a, b) => a.t - b.t); }
  at(t) {
    const K = this.k; if (!K.length) return null; if (t <= K[0].t) return { ...K[0] }; if (t >= K[K.length - 1].t) return { ...K[K.length - 1] };
    let i = 0; while (i < K.length - 2 && t >= K[i + 1].t) i++; const a = K[i], b = K[i + 1];
    if (b.cut) return { ...a };
    const u = clamp((t - a.t) / (b.t - a.t)); const out = {};
    if (b.ease === 'spline') { // C1 Hermite through the keys: no stops at the keys
      const p0 = K[i - 1], p3 = K[i + 2]; const dt = b.t - a.t;
      for (const p of PROPS) { const m1 = p0 && !a.cut ? (b[p] - p0[p]) / (b.t - p0.t) : (b[p] - a[p]) / dt, m2 = p3 && !K[i + 2].cut ? (p3[p] - a[p]) / (p3.t - a.t) : (b[p] - a[p]) / dt;
        const u2 = u * u, u3 = u2 * u; out[p] = (2 * u3 - 3 * u2 + 1) * a[p] + (u3 - 2 * u2 + u) * dt * m1 + (-2 * u3 + 3 * u2) * b[p] + (u3 - u2) * dt * m2; }
      out.shake = lerp(a.shake, b.shake, u);
    } else { const e = easeFn(b.ease)(u); for (const p of PROPS) out[p] = lerp(a[p], b[p], e); out.shake = lerp(a.shake, b.shake, e); }
    out.t = t; return out;
  }
}
// pose -> THREE camera placement
export function poseToCamera(p, groundY, cam, drift = null) {
  const pitch = clamp(p.pitch, 3, 89.9) * Math.PI / 180, yaw = p.yaw * Math.PI / 180; const dx = Math.sin(yaw), dz = -Math.cos(yaw);
  const ty = groundY + p.ty; const ch = Math.cos(pitch);
  let px = p.x - dx * p.dist * ch, pz = p.z - dz * p.dist * ch, py = ty + Math.sin(pitch) * p.dist; let lx = p.x, ly = ty, lz = p.z;
  if (drift) { px += drift[0]; py += drift[1]; pz += drift[2]; }
  return { pos: [px, py, pz], look: [lx, ly, lz], mm: p.mm };
}
