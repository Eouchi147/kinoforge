// P12 TERRAIN — the world as data for the page (pure JS, also runs in Node): heightfield (1 unit grid) -> baked low-sun lighting ->
// bicubic 2x upsample into one RGBA float map [height, sun, sky, lake rho] at 0.5 unit texels, plus the ink route and the river.
import { makeTerrain, makeRoute, makeRiver, WORLD } from './terrain.js';
import { bakeLighting } from './bake.js';

// Catmull-Rom midpoint upsample (exact half-way weights -1,9,9,-1 / 16); even samples are the source samples
function up2(src, nx, nz) {
  const mx = 2 * nx - 1, mz = 2 * nz - 1; const a = new Float32Array(mx * nz), o = new Float32Array(mx * mz);
  for (let j = 0; j < nz; j++) { const r = j * nx, q = j * mx; for (let i = 0; i < nx; i++) { a[q + 2 * i] = src[r + i]; if (i < nx - 1) { const p0 = src[r + (i > 0 ? i - 1 : i)], p1 = src[r + i], p2 = src[r + i + 1], p3 = src[r + (i + 2 < nx ? i + 2 : i + 1)]; a[q + 2 * i + 1] = (-p0 + 9 * p1 + 9 * p2 - p3) / 16; } } }
  for (let i = 0; i < mx; i++) for (let j = 0; j < nz; j++) { o[2 * j * mx + i] = a[j * mx + i]; if (j < nz - 1) { const p0 = a[(j > 0 ? j - 1 : j) * mx + i], p1 = a[j * mx + i], p2 = a[(j + 1) * mx + i], p3 = a[(j + 2 < nz ? j + 2 : j + 1) * mx + i]; o[(2 * j + 1) * mx + i] = (-p0 + 9 * p1 + 9 * p2 - p3) / 16; } }
  return { data: o, nx: mx, nz: mz };
}

export function buildWorld({ res = 1.0 } = {}) {
  const t0 = Date.now(); const lap = {};
  const T = makeTerrain({ res }); lap.terrain = Date.now() - t0;
  const route = makeRoute(T); const river = makeRiver(T); lap.route = Date.now() - t0;
  const B = bakeLighting(T); lap.bake = Date.now() - t0;
  const n = T.nx * T.nz; const ch = [0, 1, 2].map((c) => { const a = new Float32Array(n); for (let k = 0; k < n; k++) a[k] = B[k * 4 + c]; return a; });
  const H2 = up2(ch[0], T.nx, T.nz), S2 = up2(ch[1], T.nx, T.nz), K2 = up2(ch[2], T.nx, T.nz); lap.up = Date.now() - t0;
  const nx = H2.nx, nz = H2.nz, r2 = res / 2, { x0, z0 } = WORLD; const data = new Float32Array(nx * nz * 4); const lk = T.lake;
  for (let j = 0; j < nz; j++) { const z = z0 + j * r2; for (let i = 0; i < nx; i++) { const x = x0 + i * r2, p = j * nx + i;
    data[p * 4] = H2.data[p]; data[p * 4 + 1] = Math.min(1, Math.max(0, S2.data[p])); data[p * 4 + 2] = Math.min(1, Math.max(0, K2.data[p]));
    data[p * 4 + 3] = (Math.abs(x - lk.cx) < 62 && Math.abs(z - lk.cz) < 62) ? T.lakeRho(x, z) : 9; } }
  lap.tex = Date.now() - t0;
  const hAt = (x, z) => { const fx = Math.min(nx - 1.001, Math.max(0, (x - x0) / r2)), fz = Math.min(nz - 1.001, Math.max(0, (z - z0) / r2)); const i = Math.floor(fx), j = Math.floor(fz), tx = fx - i, tz = fz - j, a = j * nx + i;
    const H = H2.data; return (H[a] * (1 - tx) + H[a + 1] * tx) * (1 - tz) + (H[a + nx] * (1 - tx) + H[a + nx + 1] * tx) * tz; };
  return { T, route, river, map: { data, nx, nz, res: r2, x0, z0 }, hAt, lap };
}
