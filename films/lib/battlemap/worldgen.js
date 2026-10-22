// Battle Map engine: a terrain world from DATA (pure JS, runs in Node and the browser).
// Units are map units; x east, z south, y up. The map is centred on the origin: x in [-W/2, W/2], z in [-D/2, D/2].
// world = { seed, size:[W,D], res:1, base:0, features:[...] }; feature types: see SPEC.md.
import { clamp, lerp, smoothstep, gradNoise, fbm, ridged, catmull, resample, distToPath, sdPoly, ellipsePoly, rng, TAU } from './noise.js';
import { bakeSun, bakeSky } from './bake.js';

class PathIndex { // bucketed nearest-segment queries so rivers cost O(local) per texel
  constructor(P, R, cell = 16) {
    this.P = P; this.R = R; this.cell = cell; this.map = new Map();
    for (let k = 0; k < P.n - 1; k++) {
      const x0 = Math.min(P.x[k], P.x[k + 1]) - R, x1 = Math.max(P.x[k], P.x[k + 1]) + R, z0 = Math.min(P.z[k], P.z[k + 1]) - R, z1 = Math.max(P.z[k], P.z[k + 1]) + R;
      for (let cz = Math.floor(z0 / cell); cz <= Math.floor(z1 / cell); cz++) for (let cx = Math.floor(x0 / cell); cx <= Math.floor(x1 / cell); cx++) { const key = cx + ',' + cz; let a = this.map.get(key); if (!a) this.map.set(key, a = []); a.push(k); }
    }
  }
  query(px, pz) {
    const a = this.map.get(Math.floor(px / this.cell) + ',' + Math.floor(pz / this.cell)); if (!a) return [1e9, 0, 1];
    const P = this.P; let best = 1e18, bs = 0, side = 1;
    for (const k of a) { const ax = P.x[k], az = P.z[k], vx = P.x[k + 1] - ax, vz = P.z[k + 1] - az; const l2 = vx * vx + vz * vz || 1e-9; const t = clamp(((px - ax) * vx + (pz - az) * vz) / l2);
      const dx = px - (ax + vx * t), dz = pz - (az + vz * t); const d2 = dx * dx + dz * dz; if (d2 < best) { best = d2; bs = P.s[k] + t * Math.sqrt(l2); side = (vx * (pz - az) - vz * (px - ax)) >= 0 ? 1 : -1; } }
    return [Math.sqrt(best), bs, side];
  }
}
export function smoothPath(pts, { meander = 0, seed = 1, ds = 1.0, wl = 30 } = {}) { // spec points -> smooth dense path with optional meander
  const N = gradNoise(seed + 5); let P = resample(catmull(pts, 12), ds);
  if (meander) { const x = new Float32Array(P.n), z = new Float32Array(P.n); for (let i = 0; i < P.n; i++) { const i0 = Math.max(0, i - 1), i1 = Math.min(P.n - 1, i + 1); const tx = P.x[i1] - P.x[i0], tz = P.z[i1] - P.z[i0]; const l = Math.hypot(tx, tz) || 1; const m = N(P.s[i] / wl, 0.37) * meander * Math.min(1, P.s[i] / 20, (P.L - P.s[i]) / 20); x[i] = P.x[i] - tz / l * m; z[i] = P.z[i] + tx / l * m; }
    const poly = []; for (let i = 0; i < P.n; i++) poly.push([x[i], z[i]]); P = resample(poly, ds); }
  return P;
}
const toDeg = (d) => (d || 0) * Math.PI / 180;

export function up2(src, nx, nz) { // Catmull-Rom midpoint upsample (even samples are the source samples)
  const mx = 2 * nx - 1, mz = 2 * nz - 1; const a = new Float32Array(mx * nz), o = new Float32Array(mx * mz);
  for (let j = 0; j < nz; j++) { const r = j * nx, q = j * mx; for (let i = 0; i < nx; i++) { a[q + 2 * i] = src[r + i]; if (i < nx - 1) { const p0 = src[r + (i > 0 ? i - 1 : i)], p1 = src[r + i], p2 = src[r + i + 1], p3 = src[r + (i + 2 < nx ? i + 2 : i + 1)]; a[q + 2 * i + 1] = (-p0 + 9 * p1 + 9 * p2 - p3) / 16; } } }
  for (let i = 0; i < mx; i++) for (let j = 0; j < nz; j++) { o[2 * j * mx + i] = a[j * mx + i]; if (j < nz - 1) { const p0 = a[(j > 0 ? j - 1 : j) * mx + i], p1 = a[j * mx + i], p2 = a[(j + 1) * mx + i], p3 = a[(j + 2 < nz ? j + 2 : j + 1) * mx + i]; o[(2 * j + 1) * mx + i] = (-p0 + 9 * p1 + 9 * p2 - p3) / 16; } }
  return { data: o, nx: mx, nz: mz };
}

export function buildWorldData(spec, { sunAz = null } = {}) {
  const W = spec.size[0], D = spec.size[1]; const res = spec.res || 1.0; const x0 = -W / 2, z0 = -D / 2, x1 = W / 2, z1 = D / 2;
  const nx = Math.round(W / res) + 1, nz = Math.round(D / res) + 1; const seed = spec.seed || 1;
  const N = [gradNoise(seed), gradNoise(seed + 17), gradNoise(seed + 41), gradNoise(seed + 83)];
  const H = new Float32Array(nx * nz); H.fill(spec.base || 0);
  const F = new Float32Array(nx * nz * 4); for (let k = 0; k < nx * nz; k++) { F[k * 4] = -60; F[k * 4 + 1] = -60; F[k * 4 + 2] = -60; F[k * 4 + 3] = -60; } // water, woods, farms, road SDF (positive inside)
  const FID = new Float32Array(nx * nz * 4); // field id map (nearest): type, angle01, tone, 0
  const feats = spec.features || [];
  const loop = (bx0, bz0, bx1, bz1, fn) => { // texel loop over a world-space bbox
    const i0 = Math.max(0, Math.floor((bx0 - x0) / res)), i1 = Math.min(nx - 1, Math.ceil((bx1 - x0) / res)), j0 = Math.max(0, Math.floor((bz0 - z0) / res)), j1 = Math.min(nz - 1, Math.ceil((bz1 - z0) / res));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) fn(i, j, x0 + i * res, z0 + j * res, j * nx + i);
  };
  const polyBox = (poly, m) => { let a = 1e9, b = 1e9, c = -1e9, d = -1e9; for (const [x, z] of poly) { a = Math.min(a, x); b = Math.min(b, z); c = Math.max(c, x); d = Math.max(d, z); } return [a - m, b - m, c + m, d + m]; };
  const pathBox = (P, m) => { let a = 1e9, b = 1e9, c = -1e9, d = -1e9; for (let k = 0; k < P.n; k++) { a = Math.min(a, P.x[k]); b = Math.min(b, P.z[k]); c = Math.max(c, P.x[k]); d = Math.max(d, P.z[k]); } return [a - m, b - m, c + m, d + m]; };
  const setF = (p, ch, v) => { if (v > F[p * 4 + ch]) F[p * 4 + ch] = v; };
  const polyOf = (f, sd) => f.poly ? f.poly : ellipsePoly(f.at[0], f.at[1], Array.isArray(f.r) ? f.r[0] : f.r, Array.isArray(f.r) ? f.r[1] : f.r, toDeg(f.rot), 48, f.wob ?? 0.12, sd);
  const info = { rivers: [], seas: [], lakes: [], woods: [], farms: [], roads: [] };
  let fi = 0;
  // pass 1: additive relief
  for (const f of feats) {
    fi++; const sd = seed * 7 + fi * 13;
    if (f.type === 'undulate') { const amp = f.amp ?? 3, sc = f.scale ?? 90, oct = f.oct ?? 4; const Nn = N[(fi + 1) % 4]; loop(x0, z0, x1, z1, (i, j, x, z, p) => { H[p] += amp * fbm(Nn, x / sc + fi * 3.1, z / sc + fi * 1.7, oct); }); }
    else if (f.type === 'hill') {
      const [px, pz] = f.at; const rx = Array.isArray(f.r) ? f.r[0] : f.r, rz = Array.isArray(f.r) ? f.r[1] : f.r; const rot = toDeg(f.rot), c = Math.cos(rot), s = Math.sin(rot); const hh = f.h ?? 10, rough = f.rough ?? 0.12, crag = f.crag ?? 0, pw = f.power ?? 1.2; const Nn = N[(fi + 2) % 4];
      loop(px - rx * 1.4, pz - rz * 1.4, px + rx * 1.4, pz + rz * 1.4, (i, j, x, z, p) => { const dx = x - px, dz = z - pz; const u = (dx * c + dz * s) / rx, v = (-dx * s + dz * c) / rz; const d = Math.hypot(u, v); if (d >= 1.4) return;
        const w = Math.pow(1 - smoothstep(0, 1.0, d), pw); H[p] += hh * w * (1 + rough * fbm(Nn, x / 24 + px, z / 24, 3)) + (crag ? crag * hh * w * (ridged(Nn, x / 20 + 3, z / 20, 3) - 0.4) : 0); });
    }
    else if (f.type === 'ridge') {
      const P = smoothPath(f.path, { meander: f.meander || 0, seed: sd, ds: 2 }); const w = f.w ?? 30, hh = f.h ?? 20, rough = f.rough ?? 0.2, crest = f.crest ?? 1.3; const idx = new PathIndex(P, w, 16); const Nn = N[(fi + 3) % 4];
      const b = pathBox(P, w); loop(b[0], b[1], b[2], b[3], (i, j, x, z, p) => { const [d, s] = idx.query(x, z); if (d >= w) return; const prof = Math.pow(1 - d / w, crest); const vary = 0.78 + 0.22 * Nn(s / 55 + 3, 1.1);
        H[p] += hh * vary * prof * (1 + rough * (ridged(Nn, x / 26, z / 26, 3) - 0.35)); });
    }
    else if (f.type === 'mountains') {
      const hh = f.h ?? 40, sc = f.scale ?? 60, rid = f.ridged ?? 0.7, edge = f.edge ?? 25; const Nn = N[(fi + 1) % 4]; let sdf, box;
      if (f.path) { const P = smoothPath(f.path, { ds: 3 }); const w = f.w ?? 60; const idx = new PathIndex(P, w + 4, 24); sdf = (x, z) => w - idx.query(x, z)[0]; box = pathBox(P, w + 4); }
      else { const poly = polyOf(f, sd); sdf = (x, z) => sdPoly(x, z, poly); box = polyBox(poly, 4); }
      loop(box[0], box[1], box[2], box[3], (i, j, x, z, p) => { const m = smoothstep(0, edge, sdf(x, z)); if (m <= 0) return; const r = ridged(Nn, x / sc, z / sc, 5), b = 0.5 + 0.5 * fbm(Nn, x / (sc * 2.5) + 9, z / (sc * 2.5), 3);
        H[p] += hh * m * ((1 - rid) * b + rid * r * (0.6 + 0.6 * b)); });
    }
  }
  // pass 2: water (carving + SDF)
  fi = 0;
  for (const f of feats) {
    fi++; const sd = seed * 7 + fi * 13;
    if (f.type === 'river') {
      const w = f.w ?? 6, depth = f.depth ?? 2.2, bank = f.bank ?? 6; const P = smoothPath(f.path, { meander: f.meander ?? 0, seed: sd, ds: 1.0, wl: f.wl ?? 30 }); const idx = new PathIndex(P, w + bank + 8, 16); const Nn = N[(fi + 1) % 4];
      info.rivers.push({ path: P, w, name: f.name }); const b = pathBox(P, w + bank + 6);
      loop(b[0], b[1], b[2], b[3], (i, j, x, z, p) => { const [d, s] = idx.query(x, z); if (d > w / 2 + bank + 4) return; const wob = 1 + 0.18 * Nn(s / 11, 5.5); const hw = w * 0.5 * wob * (f.taper ? lerp(1 - f.taper, 1, s / P.L) : 1);
        setF(p, 0, hw - d); const prof = 1 - smoothstep(hw * 0.5, hw + bank, d); H[p] -= depth * prof * (1 + 0.15 * Nn(x / 9, z / 9)); });
    }
    else if (f.type === 'sea' || f.type === 'lake') {
      const poly = f.type === 'lake' ? polyOf(f, sd) : f.poly; const shelf = f.shelf ?? 18, beach = f.beach ?? 7, deep = f.depth ?? 6; const Nn = N[(fi + 2) % 4]; const b = polyBox(poly, shelf + beach + 8); info[f.type === 'lake' ? 'lakes' : 'seas'].push({ poly });
      loop(b[0], b[1], b[2], b[3], (i, j, x, z, p) => { let sdv = sdPoly(x, z, poly); sdv += 0.9 * Nn(x / 17 + 3, z / 17); setF(p, 0, sdv);
        if (sdv > 0) H[p] = lerp(Math.min(H[p], 0.6), -deep, smoothstep(0, shelf, sdv)); else if (sdv > -beach) { const t = smoothstep(0, beach, -sdv); H[p] = lerp(0.6 + 0.4 * Math.max(0, H[p]), H[p], t); } });
    }
  }
  // pass 3: woods, farms, roads (feature SDFs)
  fi = 0;
  for (const f of feats) {
    fi++; const sd = seed * 7 + fi * 13;
    if (f.type === 'woods') {
      const poly = polyOf(f, sd); const b = polyBox(poly, 8); info.woods.push({ poly, f }); const Nn = N[(fi + 1) % 4];
      loop(b[0], b[1], b[2], b[3], (i, j, x, z, p) => { setF(p, 1, sdPoly(x, z, poly) + 1.6 * Nn(x / 13 + 2, z / 13 + 1)); });
    }
    else if (f.type === 'road') {
      const P = smoothPath(f.path, { meander: f.meander ?? 0, seed: sd, ds: 1.0 }); const w = f.w ?? 2; const idx = new PathIndex(P, w + 4, 16); const b = pathBox(P, w + 4); info.roads.push({ path: P });
      loop(b[0], b[1], b[2], b[3], (i, j, x, z, p) => { const [d] = idx.query(x, z); if (d < w + 3) setF(p, 3, w / 2 - d); });
    }
    else if (f.type === 'farms') {
      const [cx, cz, fw, fd] = f.rect; const ang = toDeg(f.rot ?? f.rect[4] ?? 0), c = Math.cos(ang), s = Math.sin(ang); const gap = f.gap ?? 0.9; const R = rng(sd); const cw = f.cell?.[0] ?? 14, cd = f.cell?.[1] ?? 10; const skip = f.skip ?? 0.12; const kinds = f.kinds ?? 4;
      const cols = []; { let u = -fw / 2; while (u < fw / 2 - 0.5) { const w1 = Math.min(fw / 2 - u, cw * (0.65 + 0.8 * R())); const rows = []; let v = -fd / 2; while (v < fd / 2 - 0.5) { const d1 = Math.min(fd / 2 - v, cd * (0.65 + 0.8 * R())); rows.push({ v0: v, v1: v + d1, type: R() < skip ? 0 : 1 + Math.floor(R() * kinds), turn: R() < 0.5 ? 0 : 1, tone: R() }); v += d1; } cols.push({ u0: u, u1: u + w1, rows }); u += w1; } }
      info.farms.push({ rect: f.rect });
      const bb = Math.hypot(fw, fd) / 2 + 3; loop(cx - bb, cz - bb, cx + bb, cz + bb, (i, j, x, z, p) => { const dx = x - cx, dz = z - cz; const u = dx * c + dz * s, v = -dx * s + dz * c; if (Math.abs(u) > fw / 2 + 1 || Math.abs(v) > fd / 2 + 1) return;
        const uc = clamp(u, -fw / 2, fw / 2 - 1e-3), vc = clamp(v, -fd / 2, fd / 2 - 1e-3); let col = cols[cols.length - 1]; for (const cc of cols) if (uc < cc.u1) { col = cc; break; } let row = col.rows[col.rows.length - 1]; for (const rr of col.rows) if (vc < rr.v1) { row = rr; break; }
        if (!row.type) return; const dIn = Math.min(u - col.u0 - gap / 2, col.u1 - gap / 2 - u, v - row.v0 - gap / 2, row.v1 - gap / 2 - v); setF(p, 2, dIn);
        if (dIn > -1.2) { const q = p * 4; FID[q] = row.type; FID[q + 1] = ((ang + row.turn * Math.PI / 2) % Math.PI + Math.PI) % Math.PI / Math.PI; FID[q + 2] = row.tone; } });
    }
  }
  // pass 4: finishing: flatten (camps, battlefields) and a global height scale
  for (const f of feats) if (f.type === 'flat') { const [px, pz] = f.at; const r = f.r ?? 20, lvl = f.level, soft = f.soft ?? 12; loop(px - r - soft, pz - r - soft, px + r + soft, pz + r + soft, (i, j, x, z, p) => { const d = Math.hypot(x - px, z - pz); const w = 1 - smoothstep(r, r + soft, d); if (w > 0) H[p] = lerp(H[p], lvl ?? H[p], w * (f.amount ?? 0.9)); }); }
  // lighting
  const T = { nx, nz, res, H, x0, z0, x1, z1, W, D };
  const sun = spec.sun || { azimuth: 300, elevation: 24 }; const eve = spec.sunEve || { azimuth: 262, elevation: 7 };
  const sunA = bakeSun(T, sun.azimuth, sun.elevation), sunB = bakeSun(T, eve.azimuth, eve.elevation, { penumbra: 0.06 }), sky = bakeSky(T);
  const H2 = up2(H, nx, nz), A2 = up2(sunA, nx, nz), B2 = up2(sunB, nx, nz), K2 = up2(sky, nx, nz);
  const mx = H2.nx, mz = H2.nz, r2 = res / 2; const map = new Float32Array(mx * mz * 4);
  for (let k = 0; k < mx * mz; k++) { map[k * 4] = H2.data[k]; map[k * 4 + 1] = Math.max(0, A2.data[k]); map[k * 4 + 2] = clamp(K2.data[k]); map[k * 4 + 3] = Math.max(0, B2.data[k]); }
  const hAt = (x, z) => { const fx = clamp((x - x0) / r2, 0, mx - 1.001), fz = clamp((z - z0) / r2, 0, mz - 1.001); const i = Math.floor(fx), j = Math.floor(fz), tx = fx - i, tz = fz - j, a = j * mx + i; const d = H2.data;
    return (d[a] * (1 - tx) + d[a + 1] * tx) * (1 - tz) + (d[a + mx] * (1 - tx) + d[a + mx + 1] * tx) * tz; };
  const waterAt = (x, z) => { const fx = clamp((x - x0) / res, 0, nx - 1.001), fz = clamp((z - z0) / res, 0, nz - 1.001); const i = Math.floor(fx), j = Math.floor(fz); return F[(j * nx + i) * 4]; };
  return { spec, W, D, x0, z0, x1, z1, res, nx, nz, H, F, FID, map: { data: map, nx: mx, nz: mz, res: r2 }, hAt, waterAt, info,
    sunVec: spec.sun || { azimuth: 300, elevation: 24 } };
}
