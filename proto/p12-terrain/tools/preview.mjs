// Offline terrain design preview (Node). Usage: node preview.mjs out.png [scale] [res]
import fs from 'node:fs'; import zlib from 'node:zlib';
import { makeTerrain, makeRoute, makeRiver, WORLD } from '../terrain.js';
import { bakeLighting } from '../bake.js';

const out = process.argv[2] || 'preview.png'; const SC = +(process.argv[3] || 1.6); const RES = +(process.argv[4] || 1.0);
const t0 = Date.now(); const lap = (m) => console.log(m.padEnd(22), ((Date.now() - t0) / 1000).toFixed(2) + 's');
const ER = process.env.ER ? JSON.parse(process.env.ER) : undefined; const T = makeTerrain({ res: RES, layout: ER ? { erosion: ER } : {} }); lap('terrain');
const route = makeRoute(T); lap('route L=' + route.L.toFixed(1));
const river = makeRiver(T); lap('river');
const B = bakeLighting(T); lap('bake');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const crop = (arg('--crop', '') ? arg('--crop').split(',').map(Number) : [WORLD.x0, WORLD.z0, WORLD.x1, WORLD.z1]); const CX0 = crop[0], CZ0 = crop[1], CX1 = crop[2], CZ1 = crop[3];
const W = Math.round((CX1 - CX0) * SC), Hh = Math.round((CZ1 - CZ0) * SC);
const img = new Uint8Array(W * Hh * 3);
const ramp = [[0, [150, 168, 112]], [10, [172, 176, 116]], [22, [200, 178, 112]], [38, [196, 150, 92]], [56, [168, 150, 128]], [74, [170, 168, 160]], [92, [226, 224, 216]]];
const col = (h) => { for (let i = 0; i < ramp.length - 1; i++) if (h <= ramp[i + 1][0]) { const t = (h - ramp[i][0]) / (ramp[i + 1][0] - ramp[i][0]); return ramp[i][1].map((c, k) => c + (ramp[i + 1][1][k] - c) * Math.max(0, Math.min(1, t))); } return ramp[ramp.length - 1][1]; };
const sun = [1.0, 0.86, 0.66], sky = [0.62, 0.70, 0.86];
const bil = (c, wx, wz) => { const fi = Math.min(T.nx - 1.001, Math.max(0, (wx - WORLD.x0) / T.res)), fj = Math.min(T.nz - 1.001, Math.max(0, (wz - WORLD.z0) / T.res)); const i = Math.floor(fi), j = Math.floor(fj), tx = fi - i, tz = fj - j; const g = (a, b) => B[((j + b) * T.nx + i + a) * 4 + c]; return (g(0, 0) * (1 - tx) + g(1, 0) * tx) * (1 - tz) + (g(0, 1) * (1 - tx) + g(1, 1) * tx) * tz; };
for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) {
  const wx = CX0 + x / SC, wz = CZ0 + y / SC; const h = bil(0, wx, wz), s = bil(1, wx, wz), k = bil(2, wx, wz); const c = col(h); const slope = bil(3, wx, wz);
  const L = [sun[0] * s * 1.25 + sky[0] * k * 0.55, sun[1] * s * 1.25 + sky[1] * k * 0.55, sun[2] * s * 1.25 + sky[2] * k * 0.55];
  let r = c[0] / 255 * L[0], g = c[1] / 255 * L[1], b = c[2] / 255 * L[2];
  const iv = 4, hv = h / iv; const fr = Math.abs(hv - Math.round(hv)); const gw = 1.0 / (SC * Math.max(0.15, slope)) / iv; // ~1px line
  const lw = Math.min(0.45, 0.9 * gw); if (fr < lw) { const idx = Math.round(hv) % 5 === 0; const a = (idx ? 0.62 : 0.34) * (1 - fr / lw); r *= 1 - a; g *= 1 - a; b *= 1 - a * 0.9; }
  const o = (y * W + x) * 3; img[o] = Math.min(255, r * 255); img[o + 1] = Math.min(255, g * 255); img[o + 2] = Math.min(255, b * 255);
}
const px = (wx) => (wx - CX0) * SC, pz = (wz) => (wz - CZ0) * SC;
const dot = (x, y, r, c) => { for (let a = -r; a <= r; a++) for (let b = -r; b <= r; b++) { if (a * a + b * b > r * r) continue; const X = Math.round(x + a), Y = Math.round(y + b); if (X < 0 || Y < 0 || X >= W || Y >= Hh) continue; const o = (Y * W + X) * 3; img[o] = c[0]; img[o + 1] = c[1]; img[o + 2] = c[2]; } };
for (let i = 0; i < river.n; i++) dot(px(river.x[i]), pz(river.z[i]), 1.1, [40, 80, 150]);
for (let i = 0; i < route.n; i += 2) dot(px(route.x[i]), pz(route.z[i]), 1.4, [150, 20, 20]);
for (const [x, z] of T.lakePoly) dot(px(x), pz(z), 1, [10, 20, 40]);
dot(px(T.camp[0]), pz(T.camp[1]), 4, [255, 255, 255]); dot(px(T.saddle[0]), pz(T.saddle[1]), 4, [255, 255, 0]);
// S1 frame rectangle (+-120 x +-67.5) at the origin
const rect = (x0, z0, x1, z1, c) => { for (let t = 0; t <= 1; t += 1 / 800) { dot(px(x0 + (x1 - x0) * t), pz(z0), 0.6, c); dot(px(x0 + (x1 - x0) * t), pz(z1), 0.6, c); dot(px(x0), pz(z0 + (z1 - z0) * t), 0.6, c); dot(px(x1), pz(z0 + (z1 - z0) * t), 0.6, c); } };
rect(-120, -67.5, 120, 67.5, [255, 255, 255]);
// writePNG
const crc = (() => { const tbl = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; tbl[n] = c >>> 0; } return (buf) => { let c = 0xffffffff; for (const b of buf) c = tbl[(c ^ b) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }; })();
const chunk = (type, data) => { const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(type), data]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([len, td, c]); };
const raw = Buffer.alloc((W * 3 + 1) * Hh); for (let y = 0; y < Hh; y++) { raw[y * (W * 3 + 1)] = 0; Buffer.from(img.buffer, y * W * 3, W * 3).copy(raw, y * (W * 3 + 1) + 1); }
const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(W, 0); ihdr.writeUInt32BE(Hh, 4); ihdr[8] = 8; ihdr[9] = 2;
fs.writeFileSync(out, Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw, { level: 3 })), chunk('IEND', Buffer.alloc(0))]));
let hmin = 1e9, hmax = -1e9; for (const v of T.H) { if (v < hmin) hmin = v; if (v > hmax) hmax = v; }
console.log('wrote', out, W + 'x' + Hh, 'height range', hmin.toFixed(1), hmax.toFixed(1), 'route L', route.L.toFixed(1), 'camp y', T.sample(...T.camp).toFixed(1), 'tarn level', T.lake.level);
