// Battle Map engine: deterministic maths, noise and geometry helpers (pure JS, no THREE; runs in Node and the browser).
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const TAU = Math.PI * 2;

export function rng(seed = 1) { // mulberry32
  let a = seed >>> 0;
  const f = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  f.range = (lo, hi) => lo + (hi - lo) * f();
  return f;
}
export function hash01(a, b = 0, c = 0) { // stateless hash -> [0,1)
  let h = (Math.imul(a | 0, 374761393) + Math.imul(b | 0, 668265263) + Math.imul(c | 0, 2147483647)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177); h ^= h >>> 16; return (h >>> 0) / 4294967296;
}
export function gradNoise(seed = 1) { // Perlin gradient noise, ~[-1,1]
  const r = rng(seed); const P = new Uint8Array(512); const G = new Float32Array(512);
  const perm = Array.from({ length: 256 }, (_, i) => i);
  for (let i = 255; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; }
  for (let i = 0; i < 512; i++) P[i] = perm[i & 255];
  for (let i = 0; i < 256; i++) { const a = r() * TAU; G[i * 2] = Math.cos(a); G[i * 2 + 1] = Math.sin(a); }
  const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  return (x, y) => {
    const xf0 = Math.floor(x), yf0 = Math.floor(y); const X = xf0 & 255, Y = yf0 & 255; const xf = x - xf0, yf = y - yf0;
    const h00 = P[P[X] + Y] * 2, h10 = P[P[X + 1] + Y] * 2, h01 = P[P[X] + Y + 1] * 2, h11 = P[P[X + 1] + Y + 1] * 2;
    const g00 = G[h00] * xf + G[h00 + 1] * yf, g10 = G[h10] * (xf - 1) + G[h10 + 1] * yf, g01 = G[h01] * xf + G[h01 + 1] * (yf - 1), g11 = G[h11] * (xf - 1) + G[h11 + 1] * (yf - 1);
    const u = fade(xf), v = fade(yf); const a = g00 + (g10 - g00) * u, b = g01 + (g11 - g01) * u; return (a + (b - a) * v) * 1.41;
  };
}
export function fbm(N, x, y, oct = 4, lac = 2.03, gain = 0.5) { // rotated octaves so the lattice never lines up
  let s = 0, a = 1, f = 1, norm = 0, cx = x, cy = y;
  for (let i = 0; i < oct; i++) { s += a * N(cx * f, cy * f); norm += a; a *= gain; f *= lac; const nx = cx * 0.8 - cy * 0.6 + 17.3, ny = cx * 0.6 + cy * 0.8 - 9.1; cx = nx; cy = ny; }
  return s / norm;
}
export function ridged(N, x, y, oct = 5) { // 0..1, sharp crest lines
  let s = 0, a = 0.5, f = 1, w = 1, norm = 0, cx = x, cy = y;
  for (let i = 0; i < oct; i++) { let v = 1 - Math.abs(N(cx * f, cy * f)); v *= v; v *= w; w = clamp(v * 1.7, 0.15, 1); s += v * a; norm += a; f *= 2.07; a *= 0.5; const nx = cx * 0.8 - cy * 0.6 + 5.7, ny = cx * 0.6 + cy * 0.8 + 3.3; cx = nx; cy = ny; }
  return s / norm;
}
export function catmull(pts, n = 16) { // Catmull-Rom through points -> dense polyline
  if (pts.length < 3) { if (pts.length === 2) { const out = []; for (let k = 0; k <= n; k++) out.push([lerp(pts[0][0], pts[1][0], k / n), lerp(pts[0][1], pts[1][1], k / n)]); return out; } return pts.map((p) => p.slice()); }
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let k = 0; k < n; k++) { const t = k / n, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map((c) => 0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3))); }
  }
  out.push(pts[pts.length - 1].slice()); return out;
}
export function resample(poly, ds) { // equal arclength resampling -> {x, z, s, n, L}
  const xs = [poly[0][0]], zs = [poly[0][1]], ss = [0]; let acc = 0, carry = 0;
  for (let i = 1; i < poly.length; i++) {
    let ax = poly[i - 1][0], az = poly[i - 1][1]; const bx = poly[i][0], bz = poly[i][1]; let seg = Math.hypot(bx - ax, bz - az);
    while (carry + seg >= ds) { const t = (ds - carry) / seg; ax = lerp(ax, bx, t); az = lerp(az, bz, t); seg = Math.hypot(bx - ax, bz - az); acc += ds; xs.push(ax); zs.push(az); ss.push(acc); carry = 0; }
    carry += seg;
  }
  const lx = poly[poly.length - 1][0], lz = poly[poly.length - 1][1];
  if (Math.hypot(lx - xs[xs.length - 1], lz - zs[zs.length - 1]) > ds * 0.25) { acc += Math.hypot(lx - xs[xs.length - 1], lz - zs[zs.length - 1]); xs.push(lx); zs.push(lz); ss.push(acc); }
  return { x: Float32Array.from(xs), z: Float32Array.from(zs), s: Float32Array.from(ss), n: xs.length, L: ss[ss.length - 1] };
}
// distance from p to polyline (arrays x,z of n points) -> [dist, arclength s, signed side (+1 left of travel direction in x-east z-south coords)]
export function distToPath(px, pz, P) {
  let best = 1e18, bs = 0, side = 1;
  for (let k = 0; k < P.n - 1; k++) {
    const ax = P.x[k], az = P.z[k], vx = P.x[k + 1] - ax, vz = P.z[k + 1] - az; const l2 = vx * vx + vz * vz || 1e-9;
    const t = clamp(((px - ax) * vx + (pz - az) * vz) / l2); const dx = px - (ax + vx * t), dz = pz - (az + vz * t); const d2 = dx * dx + dz * dz;
    if (d2 < best) { best = d2; bs = P.s[k] + t * Math.sqrt(l2); side = (vx * (pz - az) - vz * (px - ax)) >= 0 ? 1 : -1; }
  }
  return [Math.sqrt(best), bs, side];
}
// signed distance to a polygon (positive inside)
export function sdPoly(px, pz, poly) {
  let d2 = 1e18, inside = false; const n = poly.length;
  for (let i = 0, j = n - 1; i < n; j = i++) {
    const ax = poly[j][0], az = poly[j][1], bx = poly[i][0], bz = poly[i][1]; const vx = bx - ax, vz = bz - az; const l2 = vx * vx + vz * vz || 1e-9;
    const t = clamp(((px - ax) * vx + (pz - az) * vz) / l2); const dx = px - (ax + vx * t), dz = pz - (az + vz * t); const q = dx * dx + dz * dz; if (q < d2) d2 = q;
    if ((az > pz) !== (bz > pz) && px < (bx - ax) * (pz - az) / (bz - az) + ax) inside = !inside;
  }
  return inside ? Math.sqrt(d2) : -Math.sqrt(d2);
}
export function ellipsePoly(cx, cz, rx, rz, rot = 0, n = 40, wob = 0, seed = 1) {
  const N = gradNoise(seed); const c = Math.cos(rot), s = Math.sin(rot); const out = [];
  for (let k = 0; k < n; k++) { const a = k / n * TAU; const w = 1 + wob * N(Math.cos(a) * 1.7 + 4, Math.sin(a) * 1.7 + 9); const ux = Math.cos(a) * rx * w, uz = Math.sin(a) * rz * w; out.push([cx + ux * c - uz * s, cz + ux * s + uz * c]); }
  return out;
}
export function interpK(K, s) { // smooth piecewise interpolation through knots [[s,val],...]
  if (s <= K[0][0]) return K[0][1]; const n = K.length; if (s >= K[n - 1][0]) return K[n - 1][1];
  let i = 0; while (i < n - 2 && s > K[i + 1][0]) i++; const t = (s - K[i][0]) / (K[i + 1][0] - K[i][0]); return lerp(K[i][1], K[i + 1][1], t * t * (3 - 2 * t));
}

export function chaikin(poly, n = 2) { let P = poly; for (let k = 0; k < n; k++) { const Q = []; for (let i = 0; i < P.length; i++) { const a = P[i], b = P[(i + 1) % P.length]; Q.push([a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25], [a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75]); } P = Q; } return P; }
