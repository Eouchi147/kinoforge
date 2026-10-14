// Offline camera planner (Node): ray-marches the heightfield to a small PNG so framing can be designed without the browser.
// Usage: node view.mjs out.png --cam x,y,z --look x,y,z [--mm 35] [--w 480] [--h 270] [--res 1] [--prog 1] [--anchors]
import fs from 'node:fs'; import zlib from 'node:zlib';
import { makeTerrain, makeRoute, makeRiver, WORLD } from '../terrain.js';
import { bakeLighting } from '../bake.js';

const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const out = process.argv[2] || 'view.png';
const cam = arg('--cam', '0,100,0').split(',').map(Number), look = arg('--look', '0,0,-100').split(',').map(Number);
const mm = +arg('--mm', 35), W = +arg('--w', 480), H = +arg('--h', 270), RES = +arg('--res', 1.0), prog = +arg('--prog', 1);
const T = makeTerrain({ res: RES }); const route = makeRoute(T); const river = makeRiver(T); const B = bakeLighting(T);
const nx = T.nx, nz = T.nz;
const bil = (c, wx, wz) => { const fi = Math.min(nx - 1.001, Math.max(0, (wx - WORLD.x0) / T.res)), fj = Math.min(nz - 1.001, Math.max(0, (wz - WORLD.z0) / T.res)); const i = Math.floor(fi), j = Math.floor(fj), tx = fi - i, tz = fj - j; const g = (a, b) => B[((j + b) * nx + i + a) * 4 + c]; return (g(0, 0) * (1 - tx) + g(1, 0) * tx) * (1 - tz) + (g(0, 1) * (1 - tx) + g(1, 1) * tx) * tz; };
const inW = (x, z) => x > WORLD.x0 && x < WORLD.x1 && z > WORLD.z0 && z < WORLD.z1;
// camera basis (three's lookAt with up = +y)
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; const nrm = (a) => { const l = Math.hypot(...a); return a.map((v) => v / l); }; const crs = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const zc = nrm(sub(cam, look)); const xc = nrm(crs([0, 1, 0], zc)); const yc = crs(zc, xc);
const vfov = 2 * Math.atan(12 / mm), th = Math.tan(vfov / 2), tw = th * W / H;
const dirAt = (u, v) => nrm([-zc[0] + xc[0] * u * tw + yc[0] * v * th, -zc[1] + xc[1] * u * tw + yc[1] * v * th, -zc[2] + xc[2] * u * tw + yc[2] * v * th]);
function march(o, d, tmax = 1600) { // returns t of first hit or -1
  let t = 0.5, prev = 0.5; for (; t < tmax;) { const x = o[0] + d[0] * t, y = o[1] + d[1] * t, z = o[2] + d[2] * t; if (!inW(x, z)) { if (d[1] >= 0 || y > 160) return -1; t += 2; continue; } const h = T.sample(x, z); if (y < h) { let lo = prev, hi = t; for (let k = 0; k < 7; k++) { const m = (lo + hi) / 2; if (o[1] + d[1] * m < T.sample(o[0] + d[0] * m, o[2] + d[2] * m)) hi = m; else lo = m; } return (lo + hi) / 2; } prev = t; t += Math.max(0.35, t * 0.004 + Math.max(0, y - h) * 0.03); }
  return -1;
}
// route / river hit test via coarse hash
const hashR = new Map(); const addPts = (P, map, step) => { for (let i = 0; i < P.n; i += step) { const k = Math.round(P.x[i] / 2) + ',' + Math.round(P.z[i] / 2); (map.get(k) || map.set(k, []).get(k)).push(i); } };
addPts(route, hashR, 2); const hashV = new Map(); addPts(river, hashV, 2);
const nearP = (P, map, x, z, r, maxI) => { for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) { const l = map.get((Math.round(x / 2) + a) + ',' + (Math.round(z / 2) + b)); if (!l) continue; for (const i of l) { if (i > maxI) continue; if (Math.hypot(P.x[i] - x, P.z[i] - z) < r) return true; } } return false; };
const ramp = [[0, [150, 168, 112]], [10, [172, 176, 116]], [22, [200, 178, 112]], [38, [196, 150, 92]], [56, [168, 150, 128]], [74, [170, 168, 160]], [92, [226, 224, 216]]];
const col = (h) => { for (let i = 0; i < ramp.length - 1; i++) if (h <= ramp[i + 1][0]) { const t = (h - ramp[i][0]) / (ramp[i + 1][0] - ramp[i][0]); return ramp[i][1].map((c, k) => c + (ramp[i + 1][1][k] - c) * Math.max(0, Math.min(1, t))); } return ramp[ramp.length - 1][1]; };
const sun = [1.0, 0.86, 0.66], sky = [0.62, 0.70, 0.86], fogC = [0.86, 0.80, 0.68];
const img = new Uint8Array(W * H * 3); const maxI = Math.floor(prog * route.n);
for (let py = 0; py < H; py++) for (let px = 0; px < W; px++) {
  const u = (px + 0.5) / W * 2 - 1, v = 1 - (py + 0.5) / H * 2; const d = dirAt(u, v); const t = march(cam, d); let r, g, b;
  if (t < 0) { const hh = Math.max(0, d[1]); const k = Math.pow(Math.min(1, hh / 0.5), 0.75); r = fogC[0] + (0.72 - fogC[0]) * k; g = fogC[1] + (0.78 - fogC[1]) * k; b = fogC[2] + (0.86 - fogC[2]) * k; }
  else {
    const x = cam[0] + d[0] * t, y = cam[1] + d[1] * t, z = cam[2] + d[2] * t; const c = col(y); const s = bil(1, x, z), k = bil(2, x, z); const L = [sun[0] * s * 1.25 + sky[0] * k * 0.55, sun[1] * s * 1.25 + sky[1] * k * 0.55, sun[2] * s * 1.25 + sky[2] * k * 0.55];
    r = c[0] / 255 * L[0]; g = c[1] / 255 * L[1]; b = c[2] / 255 * L[2];
    const iv = 4, hv = y / iv; const fr = Math.abs(hv - Math.round(hv)); if (fr < 0.07) { r *= 0.6; g *= 0.6; b *= 0.6; }
    if (T.lakeRho(x, z) < 1) { r = 0.04; g = 0.06; b = 0.09; }
    if (nearP(river, hashV, x, z, 0.8 + t * 0.003, 1e9)) { r = 0.15; g = 0.3; b = 0.5; }
    if (nearP(route, hashR, x, z, 0.7 + t * 0.004, maxI)) { r = 0.48; g = 0.1; b = 0.1; }
    const fa = 1 - Math.exp(-t * 0.0022); r += (fogC[0] - r) * fa; g += (fogC[1] - g) * fa; b += (fogC[2] - b) * fa;
  }
  const o = (py * W + px) * 3; img[o] = Math.min(255, r * 255); img[o + 1] = Math.min(255, g * 255); img[o + 2] = Math.min(255, b * 255);
}
// anchors
const proj = (p) => { const q = sub(p, cam); const z = -(q[0] * zc[0] + q[1] * zc[1] + q[2] * zc[2]); const x = q[0] * xc[0] + q[1] * xc[1] + q[2] * xc[2], y = q[0] * yc[0] + q[1] * yc[1] + q[2] * yc[2]; return [(x / (z * tw) * 0.5 + 0.5) * W, (0.5 - y / (z * th) * 0.5) * H, z]; };
const anchors = { camp: [T.camp[0], T.sample(...T.camp), T.camp[1]], saddle: [T.saddle[0], T.sample(...T.saddle), T.saddle[1]], tarn: [T.lake.cx, T.lake.level, T.lake.cz], routeEnd: route.at(route.L), s85: route.at(85), s150: route.at(150), s190: route.at(190) };
for (const [i, p] of T.layout.peaks.entries()) anchors['peak' + i] = [p[0], T.sample(p[0], p[1]), p[1]];
const dot = (x, y, c) => { for (let a = -2; a <= 2; a++) for (let b = -2; b <= 2; b++) { const X = Math.round(x + a), Y = Math.round(y + b); if (X < 0 || Y < 0 || X >= W || Y >= H) continue; const o = (Y * W + X) * 3; img[o] = c[0]; img[o + 1] = c[1]; img[o + 2] = c[2]; } };
if (process.argv.includes('--anchors')) for (const [name, p] of Object.entries(anchors)) { const [x, y, z] = proj(p); const o = [cam[0], cam[1], cam[2]]; const dd = nrm(sub(p, cam)); const tt = march(o, dd); const dist = Math.hypot(...sub(p, cam)); const vis = tt < 0 || tt > dist - 1.5; console.log(name.padEnd(9), 'px', x.toFixed(0).padStart(5), y.toFixed(0).padStart(5), 'depth', z.toFixed(0).padStart(4), vis ? 'visible' : 'HIDDEN', ' world', p.map((v) => v.toFixed(1)).join(',')); if (x > 0 && x < W && y > 0 && y < H) dot(x, y, vis ? [255, 255, 255] : [255, 0, 255]); }
// writePNG
const crc = (() => { const tbl = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; tbl[n] = c >>> 0; } return (buf) => { let c = 0xffffffff; for (const b of buf) c = tbl[(c ^ b) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }; })();
const chunk = (type, data) => { const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(type), data]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([len, td, c]); };
const raw = Buffer.alloc((W * 3 + 1) * H); for (let y = 0; y < H; y++) { raw[y * (W * 3 + 1)] = 0; Buffer.from(img.buffer, y * W * 3, W * 3).copy(raw, y * (W * 3 + 1) + 1); }
const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(W, 0); ihdr.writeUInt32BE(H, 4); ihdr[8] = 8; ihdr[9] = 2;
fs.writeFileSync(out, Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw, { level: 3 })), chunk('IEND', Buffer.alloc(0))]));
console.log('wrote', out, W + 'x' + H, 'cam', cam.join(','), 'look', look.join(','), mm + 'mm');
