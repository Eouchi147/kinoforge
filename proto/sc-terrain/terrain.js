// P12 TERRAIN — pure data module (no THREE): deterministic heightfield, valley/cirque model, lake, camp terrace,
// A* route + river polyline. Runs unchanged in Node (tools/preview.mjs) and in the browser (scene.js).
// Units: 1 unit = 1 metre of map; heights already include the 2x vertical exaggeration. x east, z SOUTH, y up.

export const WORLD = { x0: -230, x1: 230, z0: -330, z1: 90 };
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };

// ---------------------------------------------------------------- deterministic randomness (kit's mulberry32)
export function rng(seed = 1) {
  let a = seed >>> 0;
  const f = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  f.range = (lo, hi) => lo + (hi - lo) * f();
  return f;
}
// gradient (Perlin) noise, ~[-1,1]
export function gradNoise(seed = 1) {
  const r = rng(seed); const P = new Uint8Array(512); const G = new Float32Array(512);
  const perm = Array.from({ length: 256 }, (_, i) => i);
  for (let i = 255; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; }
  for (let i = 0; i < 512; i++) P[i] = perm[i & 255];
  for (let i = 0; i < 256; i++) { const a = r() * Math.PI * 2; G[i * 2] = Math.cos(a); G[i * 2 + 1] = Math.sin(a); }
  const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  return (x, y) => {
    const xf0 = Math.floor(x), yf0 = Math.floor(y); const X = xf0 & 255, Y = yf0 & 255; const xf = x - xf0, yf = y - yf0;
    const h00 = P[P[X] + Y] * 2, h10 = P[P[X + 1] + Y] * 2, h01 = P[P[X] + Y + 1] * 2, h11 = P[P[X + 1] + Y + 1] * 2;
    const g00 = G[h00] * xf + G[h00 + 1] * yf, g10 = G[h10] * (xf - 1) + G[h10 + 1] * yf, g01 = G[h01] * xf + G[h01 + 1] * (yf - 1), g11 = G[h11] * (xf - 1) + G[h11 + 1] * (yf - 1);
    const u = fade(xf), v = fade(yf);
    return (g00 + (g10 - g00) * u + ((g01 + (g11 - g01) * u) - (g00 + (g10 - g00) * u)) * v) * 1.41;
  };
}
function fbmOf(N, x, y, oct = 4, lac = 2.03, gain = 0.5) { // rotated octaves so the lattice never lines up
  let s = 0, a = 1, f = 1, norm = 0, cx = x, cy = y;
  for (let i = 0; i < oct; i++) { s += a * N(cx * f, cy * f); norm += a; a *= gain; f *= lac; const nx = cx * 0.8 - cy * 0.6 + 17.3, ny = cx * 0.6 + cy * 0.8 - 9.1; cx = nx; cy = ny; }
  return s / norm;
}
function ridgedOf(N, x, y, oct = 5) { // 0..1, sharp crest lines
  let s = 0, a = 0.5, f = 1, w = 1, norm = 0, cx = x, cy = y;
  for (let i = 0; i < oct; i++) { let v = 1 - Math.abs(N(cx * f, cy * f)); v *= v; v *= w; w = clamp(v * 1.7, 0.15, 1); s += v * a; norm += a; f *= 2.07; a *= 0.5; const nx = cx * 0.8 - cy * 0.6 + 5.7, ny = cx * 0.6 + cy * 0.8 + 3.3; cx = nx; cy = ny; }
  return s / norm;
}
function interpK(K, s) { // smooth piecewise interpolation through knots [[s,val],...]
  if (s <= K[0][0]) return K[0][1]; const n = K.length; if (s >= K[n - 1][0]) return K[n - 1][1];
  let i = 0; while (i < n - 2 && s > K[i + 1][0]) i++;
  const t = (s - K[i][0]) / (K[i + 1][0] - K[i][0]); const e = t * t * (3 - 2 * t); return lerp(K[i][1], K[i + 1][1], lerp(t, e, 0.65));
}
function catmull(pts, n = 24) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let k = 0; k < n; k++) {
      const t = k / n, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map((c) => 0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3)));
    }
  }
  out.push(pts[pts.length - 1].slice()); return out;
}
export function resample(poly, ds) { // equal arclength resampling -> {x,z,s}
  const xs = [poly[0][0]], zs = [poly[0][1]], ss = [0]; let acc = 0, carry = 0;
  for (let i = 1; i < poly.length; i++) {
    let ax = poly[i - 1][0], az = poly[i - 1][1]; const bx = poly[i][0], bz = poly[i][1]; let seg = Math.hypot(bx - ax, bz - az);
    while (carry + seg >= ds) { const t = (ds - carry) / seg; ax = lerp(ax, bx, t); az = lerp(az, bz, t); seg = Math.hypot(bx - ax, bz - az); acc += ds; xs.push(ax); zs.push(az); ss.push(acc); carry = 0; }
    carry += seg;
  }
  return { x: Float32Array.from(xs), z: Float32Array.from(zs), s: Float32Array.from(ss), n: xs.length };
}

// ---------------------------------------------------------------- authored layout (all the design numbers live here)
export const LAYOUT = {
  seed: 1214,
  // valley axis, tarn (north) -> south-west exit
  thalweg: [[22, -160], [21, -146], [16, -132], [10, -118], [3, -104], [-6, -90], [-16, -74], [-26, -56], [-36, -38], [-46, -20], [-56, -3], [-64, 13], [-72, 28], [-80, 41], [-90, 56], [-100, 72], [-112, 90], [-126, 112]],
  floorK: [[0, 38], [14, 37.6], [28, 34], [44, 26], [62, 19], [92, 15], [140, 10.5], [190, 6.5], [240, 2.8], [330, 0.3]],
  halfWidthK: [[0, 25], [28, 9], [70, 6], [120, 7], [200, 9], [330, 13]],
  wallK: [[0, 60], [30, 46], [70, 52], [120, 60], [200, 62], [330, 70]],
  highlandK: [[-340, 34], [-300, 38], [-240, 58], [-170, 68], [-80, 56], [0, 42], [40, 34], [100, 26]],
  lake: { cx: 22, cz: -160, a: 21, b: 12.5, rot: 0.14, level: 38.0 },
  camp: [-60, 36],
  saddle: [14, -226],
  // extra summit height on top of the highland (x, z, height, radius)
  peaks: [[-32, -214, 46, 30], [66, -226, 54, 34], [-92, -192, 30, 34], [124, -198, 36, 36], [-150, -255, 24, 44], [32, -300, 44, 60], [-8, -262, 20, 30]],
  saddleNotch: { depth: 0, r: 15 },
  // the pass: a trench cut through the rim, floor descending away to the north (z decreasing): the skyline V seen from the tarn
  pass: { x: 14, sway: 3.5, halfW: 21, wall: 38, pow: 1.7, z0: -226, floorK: [[226, 64], [256, 58], [292, 47], [340, 36]] }, // floorK keyed by -z (distance north)
  sun: { azimuthDeg: 315, elevationDeg: 30 },
};

export function makeTerrain(opts = {}) {
  const L = { ...LAYOUT, ...opts.layout }; const res = opts.res || 0.5; const { x0, x1, z0, z1 } = WORLD;
  const nx = Math.round((x1 - x0) / res) + 1, nz = Math.round((z1 - z0) / res) + 1;
  const N1 = gradNoise(L.seed), N2 = gradNoise(L.seed + 17), N3 = gradNoise(L.seed + 41), N4 = gradNoise(L.seed + 83);

  // ---- thalweg polyline + signed-free distance field on a 1-unit coarse grid
  const tw = resample(catmull(L.thalweg, 28), 1.0);
  const CG = 1.0, cnx = Math.round((x1 - x0) / CG) + 1, cnz = Math.round((z1 - z0) / CG) + 1;
  const cDist = new Float32Array(cnx * cnz), cS = new Float32Array(cnx * cnz);
  for (let j = 0; j < cnz; j++) for (let i = 0; i < cnx; i++) {
    const px = x0 + i * CG, pz = z0 + j * CG; let best = 1e9, bi = 0;
    for (let k = 0; k < tw.n; k++) { const dx = px - tw.x[k], dz = pz - tw.z[k]; const d2 = dx * dx + dz * dz; if (d2 < best) { best = d2; bi = k; } }
    // refine against the two adjacent segments
    let bd = Math.sqrt(best), bs = tw.s[bi];
    for (const k of [bi - 1, bi]) { if (k < 0 || k >= tw.n - 1) continue; const ax = tw.x[k], az = tw.z[k], bx = tw.x[k + 1], bz = tw.z[k + 1]; const vx = bx - ax, vz = bz - az; const t = clamp(((px - ax) * vx + (pz - az) * vz) / (vx * vx + vz * vz)); const dd = Math.hypot(px - (ax + vx * t), pz - (az + vz * t)); if (dd < bd) { bd = dd; bs = tw.s[k] + t; } }
    cDist[j * cnx + i] = bd; cS[j * cnx + i] = bs;
  }
  const valleyQ = (x, z) => { // bilinear distance, nearest s
    const fx = clamp((x - x0) / CG, 0, cnx - 1.001), fz = clamp((z - z0) / CG, 0, cnz - 1.001); const i = Math.floor(fx), j = Math.floor(fz), tx = fx - i, tz = fz - j;
    const a = j * cnx + i; const d = lerp(lerp(cDist[a], cDist[a + 1], tx), lerp(cDist[a + cnx], cDist[a + cnx + 1], tx), tz);
    const s = cS[(tx < 0.5 ? a : a + 1) + (tz < 0.5 ? 0 : cnx)]; return [d, s];
  };

  const highland = (z) => interpK(L.highlandK, z);
  const cx = L.lake.cx, cz = L.lake.cz;
  const lakeRho = (x, z) => { const dx = x - cx, dz = z - cz; const c = Math.cos(L.lake.rot), s = Math.sin(L.lake.rot); const u = dx * c + dz * s, v = -dx * s + dz * c; const wob = 1 + 0.16 * fbmOf(N3, x / 8.5 + 3, z / 8.5, 3); return Math.hypot(u / L.lake.a, v / L.lake.b) / wob; };

  // ---- the height function
  let lastT = 0;
  const AX = 0.38, ca = Math.cos(AX), sa = Math.sin(AX); // valley bearing (radians off north) — noise is stretched along it
  function heightRaw(x, z) {
    const wx = x + 30 * fbmOf(N1, x / 140 + 5.2, z / 140 + 1.3, 3), wz = z + 30 * fbmOf(N1, x / 140 + 9.7, z / 140 + 8.1, 3);
    const hl = highland(wz);
    const ua = (wx * ca - wz * sa), va = (wx * sa + wz * ca); // along / across the valley axis (u across, v along)
    const rM = ridgedOf(N2, ua / 105, va / 175, 3), rm = ridgedOf(N3, ua / 52, va / 80, 2), roll = 0.5 + 0.5 * fbmOf(N1, wx / 72, wz / 72, 3);
    const m = 0.52 * rM + 0.16 * rm + 0.32 * roll;
    const B = hl * (0.36 + 0.78 * m) + 2.4 * ridgedOf(N4, wx / 34, wz / 34, 2) * smoothstep(10, 50, hl);
    const [d0, s] = valleyQ(x, z);
    const d = d0 + 7 * fbmOf(N2, x / 30 + 11, z / 30, 3) + 2.0 * fbmOf(N4, x / 12, z / 12, 2);
    const hw = interpK(L.halfWidthK, s), W = interpK(L.wallK, s), F = interpK(L.floorK, s);
    const t = smoothstep(hw, hw + W, d); lastT = t;
    let h = F + Math.max(B - F, 0) * Math.pow(t, 1.12) + (1 - t) * 0.5 * fbmOf(N4, x / 14, z / 14, 3);
    // spurs and gullies running down the valley walls (ridged noise stretched across the valley axis): the engraver's crenellated contours
    { const ga = -0.47 * wx + 0.88 * wz, gc = 0.88 * wx + 0.47 * wz; const wallW = smoothstep(0.05, 0.42, t) * (1 - 0.55 * smoothstep(0.82, 1.0, t));
      if (wallW > 0) { const g1 = ridgedOf(N3, ga / (L.gully?.along ?? 26) + 3.1, gc / (L.gully?.across ?? 95), 3), g2 = ridgedOf(N2, ga / 11 + 8.3, gc / 60 + 1.7, 2); h += wallW * ((L.gully?.amp ?? 15) * (g1 - 0.40) + (L.gully?.amp2 ?? 4) * (g2 - 0.40)); } }
    // rim summits, then the saddle notch cut into the crest
    for (const [px, pz, ph, pr] of L.peaks) {
      const dx = x - px, dz = z - pz; const r2 = (dx * dx + dz * dz) / (pr * pr); if (r2 > 9) continue;
      const crag = 0.7 + 0.3 * ridgedOf(N3, wx / 34 + px, wz / 34 + pz, 3);
      h += ph * Math.exp(-r2) * crag * 1.1;
    }
    { const dx = x - L.saddle[0], dz = z - L.saddle[1]; const r2 = (dx * dx + dz * dz) / (L.saddleNotch.r * L.saddleNotch.r); if (r2 < 9) h -= L.saddleNotch.depth * Math.exp(-r2); }
    { const P = L.pass; if (P && z < P.z0 + 16) { const xc = P.x + P.sway * Math.sin(z / 29 + 1.3), dxp = Math.abs(Math.abs(x - xc) + 3.0 * fbmOf(N4, x / 17 + 2, z / 17, 2)); const prof = interpK(P.floorK, -z) + P.wall * Math.pow(dxp / P.halfW, P.pow);
        const zin = smoothstep(P.z0 + 16, P.z0 - 14, z); const k = 7, hh = Math.max(k - Math.abs(h - prof), 0) / k, sm = Math.min(h, prof) - hh * hh * k * 0.25; h = lerp(h, sm, zin); } }
    return h;
  }
  // ---- coarse grid (1 unit): raw heights, then stream-power erosion; the fine grid = raw + upsampled erosion delta
  const ER = L.erosion || {}; const ec = 1.0, enx = Math.round((x1 - x0) / ec) + 1, enz = Math.round((z1 - z0) / ec) + 1;
  const eRaw = new Float32Array(enx * enz), eT = new Float32Array(enx * enz);
  for (let j = 0; j < enz; j++) for (let i = 0; i < enx; i++) { eRaw[j * enx + i] = heightRaw(x0 + i * ec, z0 + j * ec); eT[j * enx + i] = lastT; }
  const eh = Float32Array.from(eRaw);
  if ((ER.iters ?? 7) > 0) erodeGrid(eh, enx, enz, eT, { iters: ER.iters ?? 8, K: ER.K ?? 0.022, m: ER.m ?? 0.5, D: ER.D ?? 0.22, J: ER.J ?? 1.1 });
  const eDelta = new Float32Array(enx * enz); for (let k = 0; k < eDelta.length; k++) eDelta[k] = (eh[k] - eRaw[k]) * smoothstep(0.04, 0.4, eT[k]);
  const deltaAt = (x, z) => { const fx = clamp((x - x0) / ec, 0, enx - 1.001), fz = clamp((z - z0) / ec, 0, enz - 1.001); const i = Math.floor(fx), j = Math.floor(fz), tx = fx - i, tz = fz - j, a = j * enx + i; return lerp(lerp(eDelta[a], eDelta[a + 1], tx), lerp(eDelta[a + enx], eDelta[a + enx + 1], tx), tz); };
  const H = new Float32Array(nx * nz);
  if (Math.abs(res - ec) < 1e-9) { for (let k = 0; k < H.length; k++) H[k] = eRaw[k] + eDelta[k]; } // same grid: reuse the raw heights
  else for (let j = 0; j < nz; j++) { const z = z0 + j * res; for (let i = 0; i < nx; i++) { const x = x0 + i * res; H[j * nx + i] = heightRaw(x, z) + deltaAt(x, z); } }

  const T = { world: WORLD, res, nx, nz, H, layout: L, thalweg: tw };
  const idx = (x, z) => { const fx = clamp((x - x0) / res, 0, nx - 1.001), fz = clamp((z - z0) / res, 0, nz - 1.001); return [Math.floor(fx), Math.floor(fz), fx - Math.floor(fx), fz - Math.floor(fz)]; };
  T.sample = (x, z) => { const [i, j, tx, tz] = idx(x, z); const a = j * nx + i; return lerp(lerp(H[a], H[a + 1], tx), lerp(H[a + nx], H[a + nx + 1], tx), tz); };
  T.slopeAt = (x, z) => { const e = 1.0; const gx = (T.sample(x + e, z) - T.sample(x - e, z)) / (2 * e), gz = (T.sample(x, z + e) - T.sample(x, z - e)) / (2 * e); return Math.hypot(gx, gz); };

  // ---- camp terrace (flat-ish ground for the tents)
  { const [px, pz] = L.camp; let sum = 0, cnt = 0; for (let a = -4; a <= 4; a += 2) for (let b = -4; b <= 4; b += 2) { sum += T.sample(px + a, pz + b); cnt++; }
    const lvl = sum / cnt; T.campLevel = lvl;
    for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) { const x = x0 + i * res, z = z0 + j * res; const d = Math.hypot(x - px, z - pz); if (d > 13) continue; const w = smoothstep(13, 4.5, d); H[j * nx + i] = lerp(H[j * nx + i], lvl, w * 0.92); }
  }
  // ---- the tarn: flat bed below the water level, soft shore
  const lk = L.lake;
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) { const x = x0 + i * res, z = z0 + j * res; if (Math.abs(x - cx) > 60 || Math.abs(z - cz) > 60) continue; const rho = lakeRho(x, z); const w = smoothstep(1.45, 0.92, rho); if (w <= 0) continue; H[j * nx + i] = lerp(H[j * nx + i], lk.level - 1.3 - 1.2 * smoothstep(1.0, 0.3, rho), w); }
  // water outline polygon (rho = 1)
  { const poly = []; for (let k = 0; k < 120; k++) { const th = k / 120 * Math.PI * 2; const dx = Math.cos(th), dz = Math.sin(th); let lo = 0, hi = 60; for (let it = 0; it < 22; it++) { const mid = (lo + hi) / 2; if (lakeRho(cx + dx * mid, cz + dz * mid) < 1) lo = mid; else hi = mid; } poly.push([cx + dx * lo, cz + dz * lo]); } T.lakePoly = poly; T.lakeRho = lakeRho; }

  // ---- slope grid (for routing + the shader's rock mask)
  T.camp = L.camp; T.saddle = L.saddle; T.lake = lk;
  return T;
}

// ---------------------------------------------------------------- stream-power erosion (priority-flood routing, implicit scheme)
function erodeGrid(h, nx, nz, tMask, { iters = 7, K = 0.006, m = 0.5, D = 0.18, J = 0.9 } = {}) {
  const N = nx * nz, hf = new Float32Array(N), rec = new Int32Array(N), order = new Int32Array(N), A = new Float32Array(N), closed = new Uint8Array(N);
  const hk = new Float32Array(N), hid = new Int32Array(N); let hs = 0; // binary min-heap
  const push = (id, key) => { let i = hs++; while (i > 0) { const p = (i - 1) >> 1; if (hk[p] <= key) break; hk[i] = hk[p]; hid[i] = hid[p]; i = p; } hk[i] = key; hid[i] = id; };
  const pop = () => { const top = hid[0]; hs--; if (hs > 0) { const key = hk[hs], id = hid[hs]; let i = 0; for (;;) { let c = 2 * i + 1; if (c >= hs) break; if (c + 1 < hs && hk[c + 1] < hk[c]) c++; if (hk[c] >= key) break; hk[i] = hk[c]; hid[i] = hid[c]; i = c; } hk[i] = key; hid[i] = id; } return top; };
  const tmp = new Float32Array(N), jit = new Float32Array(N);
  for (let it = 0; it < iters; it++) {
    closed.fill(0); hs = 0; const jr = rng(1000 + it * 77);
    for (let c = 0; c < N; c++) jit[c] = (jr() - 0.5) * J; // jittered routing surface breaks the D8 grid bias
    for (let i = 0; i < nx; i++) for (const j of [0, nz - 1]) { const c = j * nx + i; closed[c] = 1; rec[c] = -1; hf[c] = h[c]; push(c, h[c]); }
    for (let j = 1; j < nz - 1; j++) for (const i of [0, nx - 1]) { const c = j * nx + i; closed[c] = 1; rec[c] = -1; hf[c] = h[c]; push(c, h[c]); }
    let k = 0;
    while (hs > 0) { const c = pop(); order[k++] = c; const ci = c % nx, cj = (c / nx) | 0;
      for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) { if (!di && !dj) continue; const ni = ci + di, nj = cj + dj; if (ni < 0 || nj < 0 || ni >= nx || nj >= nz) continue; const n = nj * nx + ni; if (closed[n]) continue; closed[n] = 1; hf[n] = Math.max(h[n] + jit[n], hf[c] + 1e-3); rec[n] = c; push(n, hf[n]); } }
    A.fill(1); for (let q = k - 1; q >= 0; q--) { const c = order[q], r = rec[c]; if (r >= 0) A[r] += A[c]; }
    for (let q = 0; q < k; q++) { const c = order[q], r = rec[c]; if (r < 0 || h[c] <= h[r]) continue; const dd = (Math.abs((c % nx) - (r % nx)) + Math.abs(((c / nx) | 0) - ((r / nx) | 0))) === 2 ? 1.414 : 1; const f = K * Math.pow(A[c], m) / dd * smoothstep(0.03, 0.3, tMask[c]); h[c] = (h[c] + f * h[r]) / (1 + f); }
    // hillslope diffusion
    tmp.set(h); for (let j = 1; j < nz - 1; j++) for (let i = 1; i < nx - 1; i++) { const c = j * nx + i; const avg = (tmp[c - 1] + tmp[c + 1] + tmp[c - nx] + tmp[c + nx]) * 0.25; h[c] += D * smoothstep(0.03, 0.3, tMask[c]) * (avg - tmp[c]); }
  }
  // fill closed pits (they read as craters on a contour map): priority-flood to the spill height, then keep a faint drainage slope
  closed.fill(0); hs = 0;
  for (let i = 0; i < nx; i++) for (const j of [0, nz - 1]) { const c = j * nx + i; closed[c] = 1; hf[c] = h[c]; push(c, h[c]); }
  for (let j = 1; j < nz - 1; j++) for (const i of [0, nx - 1]) { const c = j * nx + i; closed[c] = 1; hf[c] = h[c]; push(c, h[c]); }
  while (hs > 0) { const c = pop(); const ci = c % nx, cj = (c / nx) | 0;
    for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) { if (!di && !dj) continue; const ni = ci + di, nj = cj + dj; if (ni < 0 || nj < 0 || ni >= nx || nj >= nz) continue; const n = nj * nx + ni; if (closed[n]) continue; closed[n] = 1; hf[n] = Math.max(h[n], hf[c] + 0.02); push(n, hf[n]); } }
  for (let c = 0; c < N; c++) if (hf[c] > h[c]) h[c] = hf[c] * smoothstep(0.03, 0.3, tMask[c]) + h[c] * (1 - smoothstep(0.03, 0.3, tMask[c]));
}

// ---------------------------------------------------------------- the route: A* over slope cost, then smoothed to a pen line
export function makeRoute(T, opts = {}) {
  const L = T.layout; const { x0, x1, z0, z1 } = WORLD; const G = 2.0; const gx = Math.round((x1 - x0) / G) + 1, gz = Math.round((z1 - z0) / G) + 1;
  const tw = T.thalweg; const rd = new Float32Array(gx * gz).fill(1e9);
  // distance to thalweg on the route grid (cheap splat)
  for (let k = 0; k < tw.n; k++) { const ci = Math.round((tw.x[k] - x0) / G), cj = Math.round((tw.z[k] - z0) / G); for (let a = -5; a <= 5; a++) for (let b = -5; b <= 5; b++) { const i = ci + a, j = cj + b; if (i < 0 || j < 0 || i >= gx || j >= gz) continue; const d = Math.hypot(x0 + i * G - tw.x[k], z0 + j * G - tw.z[k]); if (d < rd[j * gx + i]) rd[j * gx + i] = d; } }
  const hs = new Float32Array(gx * gz); for (let j = 0; j < gz; j++) for (let i = 0; i < gx; i++) hs[j * gx + i] = T.sample(x0 + i * G, z0 + j * G);
  const start = [Math.round((L.camp[0] - x0) / G), Math.round((L.camp[1] - z0) / G)];
  const endW = opts.end || [L.lake.cx - 17, L.lake.cz + 14]; const end = [Math.round((endW[0] - x0) / G), Math.round((endW[1] - z0) / G)];
  const inLake = (i, j) => T.lakeRho(x0 + i * G, z0 + j * G) < 1.18;
  const cost = (a, b, ai, aj, bi, bj) => {
    const d = Math.hypot(bi - ai, bj - aj) * G; const sl = Math.abs(hs[b] - hs[a]) / d; let c = d * (1 + 4.2 * Math.pow(sl / 0.3, 2));
    const r = rd[b]; if (r < 2.6) c *= 5; else if (r < 8) c *= 1.0 + 0.55 * (8 - r) / 5.4; // keep off the river bed except to cross it
    return c;
  };
  const open = [], g = new Float32Array(gx * gz).fill(1e18), came = new Int32Array(gx * gz).fill(-1), closed = new Uint8Array(gx * gz);
  const heap = []; const push = (n, f) => { heap.push([f, n]); let i = heap.length - 1; while (i > 0) { const p = (i - 1) >> 1; if (heap[p][0] <= heap[i][0]) break; [heap[p], heap[i]] = [heap[i], heap[p]]; i = p; } };
  const pop = () => { const top = heap[0]; const last = heap.pop(); if (heap.length) { heap[0] = last; let i = 0; for (;;) { let l = 2 * i + 1, r = l + 1, m = i; if (l < heap.length && heap[l][0] < heap[m][0]) m = l; if (r < heap.length && heap[r][0] < heap[m][0]) m = r; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; i = m; } } return top[1]; };
  const s0 = start[1] * gx + start[0], e0 = end[1] * gx + end[0]; g[s0] = 0; push(s0, 0);
  while (heap.length) {
    const n = pop(); if (closed[n]) continue; closed[n] = 1; if (n === e0) break; const ni = n % gx, nj = (n / gx) | 0;
    for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) { if (!di && !dj) continue; const mi = ni + di, mj = nj + dj; if (mi < 0 || mj < 0 || mi >= gx || mj >= gz) continue; const m = mj * gx + mi; if (closed[m]) continue; if (inLake(mi, mj) && m !== e0) continue;
      const ng = g[n] + cost(n, m, ni, nj, mi, mj); if (ng < g[m]) { g[m] = ng; came[m] = n; push(m, ng + Math.hypot(end[0] - mi, end[1] - mj) * G * 1.02); } }
  }
  const pts = []; for (let n = e0; n >= 0; n = came[n]) { pts.push([x0 + (n % gx) * G, z0 + ((n / gx) | 0) * G]); if (n === s0) break; } pts.reverse();
  pts[0] = [L.camp[0], L.camp[1]]; pts[pts.length - 1] = [endW[0], endW[1]];
  // smooth: repeated neighbour averaging with pinned ends, then Catmull-Rom, then a hand-drawn wobble
  let cur = pts.map((p) => p.slice());
  for (let it = 0; it < (opts.smooth || 14); it++) { const nxt = cur.map((p) => p.slice()); for (let i = 1; i < cur.length - 1; i++) { nxt[i][0] = 0.25 * cur[i - 1][0] + 0.5 * cur[i][0] + 0.25 * cur[i + 1][0]; nxt[i][1] = 0.25 * cur[i - 1][1] + 0.5 * cur[i][1] + 0.25 * cur[i + 1][1]; } cur = nxt; }
  const dense = resample(catmull(cur, 10), 0.4); const Nw = gradNoise(L.seed + 5);
  const out = { x: new Float32Array(dense.n), z: new Float32Array(dense.n), y: new Float32Array(dense.n), s: new Float32Array(dense.n), n: dense.n };
  for (let i = 0; i < dense.n; i++) { const w = Math.min(1, dense.s[i] / 6, (dense.s[dense.n - 1] - dense.s[i]) / 6); const nx_ = Nw(dense.s[i] / 7, 0.3) * 0.32 * w, nz_ = Nw(dense.s[i] / 7, 5.1) * 0.32 * w; out.x[i] = dense.x[i] + nx_; out.z[i] = dense.z[i] + nz_; }
  // re-measure arclength after the wobble
  let acc = 0; for (let i = 0; i < out.n; i++) { if (i) acc += Math.hypot(out.x[i] - out.x[i - 1], out.z[i] - out.z[i - 1]); out.s[i] = acc; out.y[i] = T.sample(out.x[i], out.z[i]); }
  out.L = acc; out.at = (s) => { s = clamp(s, 0, acc); let lo = 0, hi = out.n - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (out.s[m] <= s) lo = m; else hi = m; } const t = (s - out.s[lo]) / Math.max(1e-6, out.s[hi] - out.s[lo]); return [lerp(out.x[lo], out.x[hi], t), lerp(out.y[lo], out.y[hi], t), lerp(out.z[lo], out.z[hi], t)]; };
  return out;
}

// the river: thalweg from the tarn outlet, with gentle meanders; width tapers 0.5 -> 1.0
export function makeRiver(T) {
  const L = T.layout; const tw = T.thalweg; const Nw = gradNoise(L.seed + 9); const pts = []; const start = 15;
  for (let k = 0; k < tw.n; k++) { if (tw.s[k] < start) continue; const k0 = Math.max(0, k - 1), k1 = Math.min(tw.n - 1, k + 1); const tx = tw.x[k1] - tw.x[k0], tz = tw.z[k1] - tw.z[k0]; const tl = Math.hypot(tx, tz) || 1; const nxv = -tz / tl, nzv = tx / tl; const m = Nw(tw.s[k] / 22, 1.7) * 3.2 * Math.min(1, (tw.s[k] - start) / 14); pts.push([tw.x[k] + nxv * m, tw.z[k] + nzv * m]); }
  const r = resample(pts, 0.5); const out = { x: r.x, z: r.z, y: new Float32Array(r.n), s: r.s, n: r.n, L: r.s[r.n - 1] }; for (let i = 0; i < r.n; i++) out.y[i] = T.sample(r.x[i], r.z[i]); return out;
}
