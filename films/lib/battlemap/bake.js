// Battle Map engine: lighting bake from a heightfield (pure JS). Low-sun diffuse term with soft cast shadows, and a sky-visibility term.
export function sunVector(azimuthDeg, elevationDeg) { // unit vector TOWARD the sun; azimuth clockwise from north; x east, z south
  const az = azimuthDeg * Math.PI / 180, el = elevationDeg * Math.PI / 180;
  return [Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)];
}
function sampler(T) {
  const { nx, nz, H } = T;
  return (fi, fj) => {
    if (fi < 0) fi = 0; else if (fi > nx - 1.001) fi = nx - 1.001; if (fj < 0) fj = 0; else if (fj > nz - 1.001) fj = nz - 1.001;
    const i = fi | 0, j = fj | 0, tx = fi - i, tz = fj - j, a = j * nx + i;
    const a0 = H[a] + (H[a + 1] - H[a]) * tx, a1 = H[a + nx] + (H[a + nx + 1] - H[a + nx]) * tx; return a0 + (a1 - a0) * tz;
  };
}
// sun term: diffuse (normalised so level ground = 1) times soft cast shadow
export function bakeSun(T, azimuthDeg, elevationDeg, { penumbra = 0.075, maxLen = 300 } = {}) {
  const { nx, nz, res, H } = T; const S = sunVector(azimuthDeg, elevationDeg); const at = sampler(T);
  const tanEl = S[1] / Math.hypot(S[0], S[2]); const hl = Math.hypot(S[0], S[2]); const hx = S[0] / hl, hz = S[2] / hl;
  let hmax = -1e9; for (let k = 0; k < H.length; k++) if (H[k] > hmax) hmax = H[k];
  const out = new Float32Array(nx * nz);
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    const p = j * nx + i; const h0 = H[p];
    const im = i > 0 ? i - 1 : i, ip = i < nx - 1 ? i + 1 : i, jm = j > 0 ? j - 1 : j, jp = j < nz - 1 ? j + 1 : j;
    const dhx = (H[j * nx + ip] - H[j * nx + im]) / ((ip - im) * res), dhz = (H[jp * nx + i] - H[jm * nx + i]) / ((jp - jm) * res);
    const il = 1 / Math.sqrt(dhx * dhx + 1 + dhz * dhz); const ndl = Math.max(0, (-dhx * il) * S[0] + il * S[1] + (-dhz * il) * S[2]) / S[1];
    let maxSlope = -1; let t = res * 1.5; const hBias = h0 + 0.25;
    while (t < maxLen) { const hh = at(i + hx * t / res, j + hz * t / res); if (hh > hBias) { const sl = (hh - hBias) / t; if (sl > maxSlope) maxSlope = sl; } if (hBias + t * tanEl > hmax + 2) break; t *= 1.075; t += res * 0.6; }
    const vis = Math.min(1, Math.max(0, (tanEl - maxSlope) / penumbra + 0.5));
    out[p] = Math.min(2.2, ndl) * vis;
  }
  return out;
}
export function bakeSky(T, { aoStrength = 1.15 } = {}) {
  const { nx, nz, res, H } = T; const at = sampler(T); const out = new Float32Array(nx * nz);
  const dirs = []; for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2 + 0.3; dirs.push([Math.cos(a), Math.sin(a)]); }
  const aoSteps = []; { let d = 1.2; for (let k = 0; k < 13; k++) { aoSteps.push(d); d *= 1.34; } }
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    const p = j * nx + i; const h0 = H[p];
    const im = i > 0 ? i - 1 : i, ip = i < nx - 1 ? i + 1 : i, jm = j > 0 ? j - 1 : j, jp = j < nz - 1 ? j + 1 : j;
    const dhx = (H[j * nx + ip] - H[j * nx + im]) / ((ip - im) * res), dhz = (H[jp * nx + i] - H[jm * nx + i]) / ((jp - jm) * res);
    const nY = 1 / Math.sqrt(dhx * dhx + 1 + dhz * dhz); let occ = 0;
    for (let k = 0; k < 8; k++) { const dx = dirs[k][0], dz = dirs[k][1]; let ms = -1; for (let q = 0; q < aoSteps.length; q++) { const d = aoSteps[q]; const sl = (at(i + dx * d / res, j + dz * d / res) - h0) / d; if (sl > ms) ms = sl; }
      const tang = dhx * dx + dhz * dz; const a = Math.atan(Math.max(0, ms)), tt = Math.atan(Math.max(0, tang)); occ += Math.max(0, Math.sin(a) - Math.sin(tt)); }
    occ /= 8; out[p] = Math.min(1, Math.max(0, (0.5 + 0.5 * nY) * (1 - aoStrength * occ)));
  }
  return out;
}
