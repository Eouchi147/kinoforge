// Label retiming + camera-path analysis (Node): when does each anchor enter the frame (unoccluded, inside a safe margin)?
// Also prints per-frame camera speed/pitch so the single eased S2 move can be verified numerically.
import { buildWorld } from '../world.js';
import * as TM from '../timing.js';
import { POSE, kS2 } from '../camera.js';
const W = buildWorld({ res: 1.0 }); const { T, route } = W;
const lerp = (a, b, t) => a + (b - a) * t;
function pose(t) {
  const n = t < TM.CUT_S2 ? 0 : t < TM.CUT_S3 ? 1 : 2;
  if (n === 0) return POSE.s1; if (n === 2) return POSE.s3;
  const u = (t - TM.CUT_S2) / (TM.CUT_S3 - TM.CUT_S2), k = kS2(u), a = POSE.s2a, b = POSE.s2b;
  return { pos: a.pos.map((v, i) => lerp(v, b.pos[i], k)), look: a.look.map((v, i) => lerp(v, b.look[i], k)), mm: lerp(a.mm, b.mm, k) };
}
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; const nrm = (a) => { const l = Math.hypot(...a); return a.map((v) => v / l); }; const crs = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
function proj(p, P) {
  const zc = nrm(sub(P.pos, P.look)), xc = nrm(crs([0, 1, 0], zc)), yc = crs(zc, xc); const th = Math.tan(Math.atan(12 / P.mm)), tw = th * 16 / 9;
  const q = sub(p, P.pos); const z = -(q[0] * zc[0] + q[1] * zc[1] + q[2] * zc[2]); const x = q[0] * xc[0] + q[1] * xc[1] + q[2] * xc[2], y = q[0] * yc[0] + q[1] * yc[1] + q[2] * yc[2];
  return [x / (z * tw), y / (z * th), z];
}
function occl(p, P) { let worst = 0; const N = 36; for (let k = 1; k < N - 2; k++) { const f = k / N; const x = P.pos[0] + (p[0] - P.pos[0]) * f, y = P.pos[1] + (p[1] - P.pos[1]) * f, z = P.pos[2] + (p[2] - P.pos[2]) * f; const ex = W.hAt(x, z) - y; if (ex > worst) worst = ex; } return worst; }
const end = route.at(route.L);
const A = { camp: [T.camp[0], T.sample(...T.camp), T.camp[1]], tarn: [T.lake.cx, T.sample(T.lake.cx, T.lake.cz), T.lake.cz], saddle: [T.saddle[0], T.sample(...T.saddle) + 3, T.saddle[1]], end };
const first = {}, last = {};
for (let f = 0; f < 240; f++) { const t = f / 24, P = pose(t); for (const [k, a] of Object.entries(A)) { const [x, y, z] = proj(a, P); const inside = z > 0 && Math.abs(x) < 0.90 && Math.abs(y) < 0.88 && occl(a, P) < 1.0; if (inside) { if (first[k] === undefined) first[k] = t; last[k] = t; } } }
console.log('anchor in-frame (safe margin, unoccluded) first/last s:'); for (const k of Object.keys(A)) console.log(' ', k.padEnd(7), first[k]?.toFixed(3), last[k]?.toFixed(3));
if (process.argv.includes('--path')) {
  let prevD = null, prevPos = null, prevPitch = null;
  console.log('frame  t     k      pos                      pitch  dPos/f  dPitch/f');
  for (let f = TM.CUT_S2 * 24 - 1; f <= TM.CUT_S3 * 24 + 1; f++) { const t = f / 24, P = pose(t); const d = nrm(sub(P.look, P.pos)); const pitch = Math.asin(-d[1]) * 180 / Math.PI; const dp = prevPos ? Math.hypot(...sub(P.pos, prevPos)) : 0, dpi = prevPitch !== null ? pitch - prevPitch : 0;
    if (f % 4 === 0 || f > TM.CUT_S3 * 24 - 4) console.log(String(f).padStart(4), t.toFixed(3), P.pos.map((v) => v.toFixed(1).padStart(6)).join(' '), pitch.toFixed(2).padStart(7), dp.toFixed(2).padStart(7), dpi.toFixed(2).padStart(8)); prevPos = P.pos; prevPitch = pitch; }
}
