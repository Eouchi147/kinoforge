// P01 "STATIC" — analog horror, 10 s. A 1990s security tape of an empty school corridor at 2:14 AM; between frames, something is closer.
// One continuous CCTV take (S1 clock stutter → S2 a tracking error hides the far door opening → S3 digital zoom, 2-frame dropout,
// a figure is standing in the doorway) → S4 black → S5 card. The scare is a continuity change, never a jump (R-8-07).
// Post: kit 'vhs' finish + three scene-owned passes (kit untouched): ZOOM (digital crop of the sensor image, before the OSD),
// PLAYBACK (tape faults that also hit the burned-in OSD), BEZEL (4:3 CRT window inside 16:9). Event frames are mirrored in audio.py.
import * as THREE from 'three';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { boot, CameraRig, makeComposer, ease, rng, fbmCanvas, valueNoise2D, canvasTexture, smoothstep, clamp, lerp, noise1 } from '/harness/kit/film.js';

// ------------------------------------------------------------------ timing (frames @ 24 fps) — keep in sync with audio.py
const FPS = 24;
const CUT = [0, 77, 139, 209, 223, 240];           // first frame of S1..S5, then the end
const SHOTS = [
  { name: 'S1 CCTV wide, door closed, clock stutters', dur: 77 / FPS },
  { name: 'S2 same take, tracking error, door opens', dur: 62 / FPS },
  { name: 'S3 digital zoom, dropout, figure', dur: 70 / FPS },
  { name: 'S4 black', dur: 14 / FPS },
  { name: 'S5 card TAPE 3 OF 11', dur: 17 / FPS },
];
const EV = { stutter: [31, 34], band: [87, 104], door: 94, zoom: [139, 173], drop: [173, 175], figure: 175 };
// P5 (the failing tube by the far door): [first frame, end frame, level]
const FLICKER = [[14, 16, 0.06], [17, 18, 0.4], [54, 58, 0.04], [60, 61, 0.45], [120, 123, 0.05], [146, 148, 0.3], [183, 187, 0.03], [199, 200, 0.25]];
const ZOOM_K = 45 / 20;                               // 20 mm → 45 mm equivalent

// ------------------------------------------------------------------ the set (metres)
const CW = 3.2, CH = 3.0, ZN = 1.0, ZF = -14.4, LEN = ZN - ZF, ZMID = (ZN + ZF) / 2;
const XW = CW / 2, LD = 0.38, LH = 1.83, LB = 0.1, LWD = 0.305, XF = XW - LD; // lockers: depth, height, base, width; front plane |x|
const DW = 0.95, DH = 2.12, DOOR_OPEN = 1.5;
const PANELS = [{ z: -1.3, s: 0 }, { z: -4.35, s: 1 }, { z: -7.4, s: 1 }, { z: -10.45, s: 1 }, { z: -13.5, s: 2 }]; // 1 on, 0 dead, 2 failing
const BANKS = [{ side: -1, z0: 0.8, n: 10 }, { side: -1, z0: -4.8, n: 10 }, { side: -1, z0: -9.2, n: 14 }, { side: 1, z0: -1.7, n: 12 }, { side: 1, z0: -6.85, n: 22 }];
const SIDE_DOORS = [{ side: -1, z: -4.1 }, { side: -1, z: -8.55 }, { side: 1, z: -6.1 }, { side: 1, z: -0.95 }];
const CAM = { pos: [0.92, 2.6, 0.85], yaw: -8.0, pitch: 14.0, roll: 0.6, mm: 20 }; // high right corner, aimed across and 14° down
const PANEL_RGB = [0.93, 1.0, 0.92], PANEL_I = 3.2, RECT_I = 13;
const WIN = { x0: 171, y0: 8, x1: 1109, y1: 712, r: 26 }; // 4:3 CRT window (px @1280x720)

let scene, camera, rig, post, W, H, world, figure, neck, doorPivot, zoomPass, playPass, bezelPass, zoomTarget;
const panelMats = [], panelLights = [];
const BG = new THREE.Color(0x0b0f0d), BLACK = new THREE.Color(0x000000);

// ------------------------------------------------------------------ helpers
const cv = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
const col = (r, g, b, a = 1) => `rgba(${r | 0},${g | 0},${b | 0},${a})`;
// the kit's overlay texture is sRGB-tagged, so it is decoded to linear when sampled and mixed into display-referred pixels:
// pre-encode overlay greys so the drawn value is the displayed value.
const osd = (v) => Math.round(255 * clamp(v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055));
// low-res alpha layer evaluated per pixel (cheap at low res, drawn scaled up = soft grime)
function alphaLayer(w, h, rgb, fn) {
  const c = cv(w, h), g = c.getContext('2d'), img = g.createImageData(w, h), d = img.data;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const i = (y * w + x) * 4; d[i] = rgb[0]; d[i + 1] = rgb[1]; d[i + 2] = rgb[2]; d[i + 3] = 255 * clamp(fn((x + 0.5) / w, (y + 0.5) / h)); }
  g.putImageData(img, 0, 0); return c;
}
const std = (o) => new THREE.MeshStandardMaterial(o);
function box(w, h, d, mat, x, y, z, parent) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.position.set(x, y, z); (parent || world).add(m); return m; }
function flickerLevel(f) { for (const [a, b, l] of FLICKER) if (f >= a && f < b) return l; return 1; }

// ------------------------------------------------------------------ textures
function floorMaps() { // vinyl composition tile, 3.2 x 15.4 m; canvas top = far end, left = -x
  const w = 504, h = 2424, T = 48, cx = 252, r = rng(31);
  const c = cv(w, h), g = c.getContext('2d'), rc = cv(w, h), rg = rc.getContext('2d');
  g.fillStyle = col(60, 62, 56); g.fillRect(0, 0, w, h); rg.fillStyle = col(0, 150, 0); rg.fillRect(0, 0, w, h);
  for (let ty = 0; ty * T < h; ty++) for (let tx = -6; tx < 6; tx++) {
    const x0 = cx + tx * T, y0 = ty * T; if (x0 + T < 0 || x0 > w) continue;
    const border = tx === -4 || tx === 3, repair = !border && r() < 0.04;
    const b = border ? [58, 74, 70] : repair ? [142, 144, 124] : [160, 157, 140]; const v = (r() - 0.5) * 9;
    g.fillStyle = col(b[0] + v, b[1] + v, b[2] + v * 0.8); g.fillRect(x0, y0, T, T);
    for (let k = 0; k < 34; k++) { const dk = r() < 0.55, a = 16 + r() * 30; g.fillStyle = dk ? col(b[0] - a, b[1] - a, b[2] - a * 0.9, 0.55) : col(b[0] + a * 0.5, b[1] + a * 0.5, b[2] + a * 0.4, 0.5); g.fillRect(x0 + r() * T, y0 + r() * T, 1 + r() * 2.2, 1 + r() * 1.5); }
    rg.fillStyle = col(0, (border ? 0.36 : 0.17 + r() * 0.07) * 255, 0); rg.fillRect(x0, y0, T, T);
  }
  g.fillStyle = col(64, 66, 56, 0.6); rg.fillStyle = col(0, 215, 0);
  for (let tx = -6; tx <= 6; tx++) { const x = cx + tx * T; g.fillRect(x - 0.75, 0, 1.5, h); rg.fillRect(x - 1.2, 0, 2.4, h); }
  for (let ty = 0; ty * T <= h; ty++) { const y = ty * T; g.fillRect(0, y - 0.75, w, 1.5); rg.fillRect(0, y - 1.2, w, 2.4); }
  // grime: fbm darkening that gathers along the locker line (brief: dirt at the floor edges), plus general mottling
  const nz = valueNoise2D(41);
  const grime = (u, v) => { const xm = Math.abs(u * CW - XW); const f = nz.fbm(u * 7, v * 34, 4); return smoothstep(0.62, 1.2, xm) * (0.35 + 0.95 * f) * 0.9 + 0.22 * smoothstep(0.55, 0.78, f); };
  g.drawImage(alphaLayer(126, 606, [40, 42, 30], grime), 0, 0, w, h);
  rg.drawImage(alphaLayer(126, 606, [0, 175, 0], grime), 0, 0, w, h);
  // traffic lane: buffed lighter and smoother down the middle
  const lane = g.createLinearGradient(0, 0, w, 0); lane.addColorStop(0.28, 'rgba(255,255,240,0)'); lane.addColorStop(0.5, 'rgba(255,255,240,0.07)'); lane.addColorStop(0.72, 'rgba(255,255,240,0)'); g.fillStyle = lane; g.fillRect(0, 0, w, h);
  const lr = rg.createLinearGradient(0, 0, w, 0); lr.addColorStop(0.3, 'rgba(0,40,0,0)'); lr.addColorStop(0.5, 'rgba(0,40,0,0.45)'); lr.addColorStop(0.7, 'rgba(0,40,0,0)'); rg.fillStyle = lr; rg.fillRect(0, 0, w, h);
  // heel scuffs
  g.lineCap = 'round';
  for (let k = 0; k < 110; k++) { g.strokeStyle = col(28, 28, 24, 0.1 + r() * 0.2); g.lineWidth = 0.8 + r() * 2.2; const x = 80 + r() * 344, y = r() * h; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + (r() - .5) * 30, y + (r() - .5) * 24, x + (r() - .5) * 46, y + (r() - .5) * 30); g.stroke(); }
  return { map: c, rough: rc };
}
function wallMap(seed, w, h, mw, extra) { // painted concrete block, 0.4 x 0.2 m courses; mw = wall width in metres
  const c = cv(w, h), g = c.getContext('2d'), r = rng(seed); const bw = w / mw * 0.4, bh = h / CH * 0.2;
  g.fillStyle = col(118, 122, 104); g.fillRect(0, 0, w, h);
  g.fillStyle = col(136, 140, 120); g.fillRect(0, 0, w, h); // mortar
  for (let row = 0; row * bh < h; row++) { const y = h - (row + 1) * bh, off = (row % 2) * bw / 2; for (let x = -off; x < w; x += bw) { const v = (r() - 0.5) * 8; g.fillStyle = col(176 + v, 180 + v, 158 + v * 0.8); g.fillRect(x + 0.6, y + 0.6, bw - 1.2, bh - 1.2); } }
  for (let k = 0; k < w * h / 60; k++) { g.fillStyle = r() < 0.5 ? 'rgba(90,92,80,0.18)' : 'rgba(230,230,210,0.12)'; g.fillRect(r() * w, r() * h, 1, 1); }
  const nz = valueNoise2D(seed + 7);
  g.drawImage(alphaLayer(Math.ceil(w / 8), Math.ceil(h / 8), [58, 60, 46], (u, v) => smoothstep(0.84, 1.0, v) * 0.55 + smoothstep(0.08, 0.0, v) * 0.3 + 0.32 * smoothstep(0.52, 0.86, nz.fbm(u * 26, v * 5, 4))), 0, 0, w, h);
  if (extra) extra(g, w, h, r);
  return c;
}
function lockerMaps(n, seed) { // one bank: n doors, 64 px per door, 384 px tall (1.83 m)
  const PW = 64, w = n * PW, h = 384, r = rng(seed);
  const c = cv(w, h), g = c.getContext('2d'), b = cv(w, h), bg = b.getContext('2d');
  bg.fillStyle = '#7a7a7a'; bg.fillRect(0, 0, w, h);
  for (let i = 0; i < n; i++) {
    const x = i * PW, v = (r() - 0.5) * 10, re = r() < 0.12 ? 1 : 0;
    const base = re ? [118 + v, 140 + v, 124 + v] : [96 + v, 130 + v, 128 + v];
    g.fillStyle = col(...base); g.fillRect(x, 0, PW, h);
    g.fillStyle = col(base[0] + 18, base[1] + 18, base[2] + 16, 0.45); g.fillRect(x + 3, 3, 2, h - 6); g.fillRect(x + 3, 3, PW - 7, 2);
    g.fillStyle = col(14, 20, 20, 0.75); g.fillRect(x, 0, 2.5, h); g.fillRect(x + PW - 1.5, 0, 1.5, h); bg.fillStyle = '#202020'; bg.fillRect(x, 0, 2.5, h);
    for (const top of [18, 326]) for (let s = 0; s < 6; s++) { const yy = top + s * 7; g.fillStyle = col(10, 14, 14, 0.9); g.fillRect(x + 15, yy, PW - 30, 3); g.fillStyle = col(base[0] + 24, base[1] + 24, base[2] + 20, 0.5); g.fillRect(x + 15, yy + 3, PW - 30, 1); bg.fillStyle = '#181818'; bg.fillRect(x + 15, yy, PW - 30, 3); }
    g.fillStyle = col(24, 30, 30, 0.9); g.fillRect(x + PW - 17, 166, 7, 48); g.fillStyle = col(160, 166, 158, 0.75); g.fillRect(x + PW - 16, 170, 5, 9); bg.fillStyle = '#303030'; bg.fillRect(x + PW - 17, 166, 7, 48);
    g.fillStyle = col(160, 158, 140, 0.6); g.fillRect(x + 22, 70, 20, 9); // blank number plate
    for (let k = 0; k < 3; k++) { if (r() < 0.45) continue; const dx = x + 8 + r() * 48, dy = 90 + r() * 220, rr = 6 + r() * 14; const gr = g.createRadialGradient(dx, dy, 0, dx, dy, rr); gr.addColorStop(0, 'rgba(0,0,0,0.22)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(dx - rr, dy - rr, rr * 2, rr * 2); }
    for (let k = 0; k < 6; k++) { g.fillStyle = col(30, 26, 20, 0.15 + r() * 0.25); g.fillRect(x + 4 + r() * 54, 300 + r() * 80, 2 + r() * 7, 1 + r() * 3); } // kicks
    if (r() < 0.3) { g.fillStyle = 'rgba(110,70,40,0.35)'; for (let k = 0; k < 10; k++) g.fillRect(x + 3 + r() * 58, 360 + r() * 22, 1 + r() * 2, 1 + r() * 2); } // rust
  }
  const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(0,0,0,0.05)'); gr.addColorStop(0.75, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(10,8,4,0.3)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  return { map: c, bump: b };
}
function ceilingMap() { // 2x2 ft acoustic tiles on a white grid; canvas top = near end (z = +1), left = -x
  const w = 384, h = 1848, r = rng(77), nz = valueNoise2D(78);
  const px = (x) => (x + XW) / CW * w, pz = (z) => (ZN - z) / LEN * h;
  const c = cv(w, h), g = c.getContext('2d');
  g.fillStyle = col(188, 186, 174); g.fillRect(0, 0, w, h);
  for (let k = 0; k < 9000; k++) { g.fillStyle = r() < 0.7 ? 'rgba(90,88,80,0.35)' : 'rgba(250,250,240,0.25)'; g.fillRect(r() * w, r() * h, 1 + r(), 1 + r() * 2); } // fissures
  g.drawImage(alphaLayer(48, 231, [120, 104, 70], (u, v) => 0.35 * smoothstep(0.6, 0.9, nz.fbm(u * 6, v * 28, 4))), 0, 0, w, h);
  const stain = (x, z, rr) => { const X = px(x), Z = pz(z); for (let k = 0; k < 3; k++) { const s = rr * (1 - k * 0.25); const gr = g.createRadialGradient(X, Z, s * 0.6, X, Z, s); gr.addColorStop(0, 'rgba(130,100,55,0.10)'); gr.addColorStop(0.85, 'rgba(110,80,40,0.35)'); gr.addColorStop(1, 'rgba(110,80,40,0)'); g.fillStyle = gr; g.beginPath(); g.ellipse(X, Z, s, s * 0.8, 0.4, 0, 6.3); g.fill(); } };
  stain(-0.55, -5.9, 22); stain(0.62, -9.1, 16); stain(-1.2, -11.6, 26); stain(0.9, -2.6, 12);
  // black plenum above the dead fixture that hangs crooked (P1), and the recesses of the others
  g.fillStyle = '#040404'; g.fillRect(px(-0.305), pz(PANELS[0].z + 0.61), px(0.305) - px(-0.305), pz(PANELS[0].z - 0.61) - pz(PANELS[0].z + 0.61)); // plenum above the hanging fixture
  g.fillStyle = col(70, 70, 66); for (const p of PANELS.slice(1)) g.fillRect(px(-0.305), pz(p.z + 0.61), px(0.305) - px(-0.305), pz(p.z - 0.61) - pz(p.z + 0.61));
  g.fillStyle = col(150, 150, 140); for (let k = 0; k < 7; k++) g.fillRect(px(0.305) + 6, pz(-8.9) + 6 + k * 9, px(0.915) - px(0.305) - 12, 3); // return-air grille slots
  g.fillStyle = col(222, 222, 214); // T-bar grid
  for (let k = -3; k <= 3; k++) { const x = px(0.305 + 0.61 * k); g.fillRect(x - 1.5, 0, 3, h); }
  for (let m = -24; m <= 4; m++) { const z = pz(-1.3 + 0.61 * m); g.fillRect(0, z - 1.5, w, 3); }
  return c;
}
function diffuserMap() { // prismatic lens over two tubes
  const w = 64, h = 128, c = cv(w, h), g = c.getContext('2d');
  g.fillStyle = col(200, 204, 200); g.fillRect(0, 0, w, h);
  for (const tx of [20, 44]) { const gr = g.createLinearGradient(tx - 14, 0, tx + 14, 0); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(tx - 14, 4, 28, h - 8); }
  g.strokeStyle = 'rgba(150,156,150,0.35)'; g.lineWidth = 1; for (let k = -h; k < w + h; k += 5) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k + h, h); g.stroke(); g.beginPath(); g.moveTo(k + h, 0); g.lineTo(k, h); g.stroke(); }
  const e = g.createLinearGradient(0, 0, w, 0); e.addColorStop(0, 'rgba(60,60,60,0.5)'); e.addColorStop(0.1, 'rgba(0,0,0,0)'); e.addColorStop(0.9, 'rgba(0,0,0,0)'); e.addColorStop(1, 'rgba(60,60,60,0.5)'); g.fillStyle = e; g.fillRect(0, 0, w, h);
  return c;
}
function exitFace() { // red glow, abstract (no letters): a brighter field with two dark bars and a chevron
  const c = cv(128, 64), g = c.getContext('2d');
  g.fillStyle = '#2a0806'; g.fillRect(0, 0, 128, 64); g.fillStyle = '#e8321e'; g.fillRect(6, 6, 116, 52);
  g.fillStyle = '#ff6a4a'; g.fillRect(14, 14, 100, 36); g.fillStyle = '#8a160c'; g.fillRect(24, 24, 30, 16); g.fillRect(62, 24, 18, 16);
  g.beginPath(); g.moveTo(88, 22); g.lineTo(104, 32); g.lineTo(88, 42); g.closePath(); g.fill();
  return c;
}
function clockFace() { // white dial, 12 ticks, hands at 2:14 (matches the OSD)
  const S = 128, c = cv(S, S), g = c.getContext('2d'), m = S / 2;
  g.fillStyle = '#1c1c1a'; g.fillRect(0, 0, S, S); g.fillStyle = '#e8e6dc'; g.beginPath(); g.arc(m, m, 58, 0, 6.3); g.fill();
  g.translate(m, m); g.rotate(-Math.PI / 2); g.translate(-m, -m); // the cylinder cap's UVs turn the dial 90° clockwise; pre-rotate
  g.strokeStyle = '#1a1a18'; g.lineCap = 'butt';
  for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2; g.lineWidth = k % 3 ? 2 : 4; g.beginPath(); g.moveTo(m + Math.sin(a) * 46, m - Math.cos(a) * 46); g.lineTo(m + Math.sin(a) * 55, m - Math.cos(a) * 55); g.stroke(); }
  const hand = (deg, len, wd) => { const a = deg * Math.PI / 180; g.lineWidth = wd; g.lineCap = 'round'; g.beginPath(); g.moveTo(m - Math.sin(a) * 6, m + Math.cos(a) * 6); g.lineTo(m + Math.sin(a) * len, m - Math.cos(a) * len); g.stroke(); };
  hand((2 + 14 / 60) * 30, 30, 6); hand(14 * 6, 46, 4);
  return c;
}
function posterMap() { // a sun-washed notice: dark printed border, blank faded centre, torn corner, tape (no text)
  const w = 128, h = 76, c = cv(w, h), g = c.getContext('2d'), r = rng(5);
  g.fillStyle = col(46, 58, 86); g.fillRect(0, 0, w, h);
  g.fillStyle = col(176, 172, 150); g.fillRect(9, 9, w - 18, h - 18);
  g.fillStyle = 'rgba(70,84,110,0.22)'; g.beginPath(); g.arc(34, 38, 15, 0, 6.3); g.fill(); g.fillRect(58, 26, 52, 6); g.fillRect(58, 40, 40, 5);
  for (let k = 0; k < 500; k++) { g.fillStyle = 'rgba(100,90,60,0.1)'; g.fillRect(r() * w, r() * h, 2, 2); }
  g.fillStyle = 'rgba(232,224,180,0.65)'; g.fillRect(-4, -2, 16, 7); g.fillRect(w - 12, -2, 16, 7); g.fillRect(w - 12, h - 5, 16, 7);
  g.globalCompositeOperation = 'destination-out'; g.beginPath(); g.moveTo(0, h - 30); g.lineTo(9, h - 19); g.lineTo(15, h - 10); g.lineTo(26, h); g.lineTo(0, h); g.closePath(); g.fill(); g.globalCompositeOperation = 'source-over';
  return c;
}
function wetMask() { // irregular puddle; alphaMap reads G, so composite the mask onto opaque black
  const w = 128, h = 96, nz = valueNoise2D(91), c = cv(w, h), g = c.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
  g.drawImage(alphaLayer(w, h, [255, 255, 255], (u, v) => { const dx = (u - 0.5) * 2, dy = (v - 0.5) * 2; const d = Math.sqrt(dx * dx * 0.9 + dy * dy * 1.3); return smoothstep(0.95, 0.55, d + 0.45 * (nz.fbm(u * 5, v * 5, 4) - 0.5)); }), 0, 0);
  return c;
}
function beyondWall() { // the stairwell's back wall: a wired-glass window of cold night light behind where the figure will stand
  // (BoxGeometry's -z face runs u toward -x, so the canvas is mirrored in x)
  const w = 256, h = 240, c = cv(w, h), g = c.getContext('2d');
  const U = (x) => (XW - x) / CW * w, V = (y) => (CH - y) / CH * h;
  g.fillStyle = col(52, 64, 74); g.fillRect(0, 0, w, h);
  const glow = g.createRadialGradient(U(-0.15), V(1.45), 6, U(-0.15), V(1.2), 150); glow.addColorStop(0, 'rgba(140,164,178,0.75)'); glow.addColorStop(0.55, 'rgba(104,128,142,0.4)'); glow.addColorStop(1, 'rgba(120,146,160,0)'); g.fillStyle = glow; g.fillRect(0, 0, w, h);
  const x0 = U(0.32), x1 = U(-0.62), y0 = V(2.05), y1 = V(0.85);
  g.fillStyle = col(150, 170, 182); g.fillRect(x0, y0, x1 - x0, y1 - y0);
  g.strokeStyle = 'rgba(90,110,122,0.55)'; g.lineWidth = 1; for (let x = x0; x < x1; x += 5) { g.beginPath(); g.moveTo(x, y0); g.lineTo(x, y1); g.stroke(); } for (let y = y0; y < y1; y += 5) { g.beginPath(); g.moveTo(x0, y); g.lineTo(x1, y); g.stroke(); }
  g.fillStyle = col(40, 48, 54); g.fillRect((x0 + x1) / 2 - 2, y0, 4, y1 - y0); g.fillRect(x0, (y0 + y1) / 2 - 2, x1 - x0, 4);
  g.strokeStyle = col(34, 40, 46); g.lineWidth = 5; g.strokeRect(x0, y0, x1 - x0, y1 - y0);
  const sill = g.createLinearGradient(0, y1, 0, h); sill.addColorStop(0, 'rgba(150,172,186,0.35)'); sill.addColorStop(1, 'rgba(150,172,186,0.12)'); g.fillStyle = sill; g.fillRect(x0 - 20, y1 + 3, x1 - x0 + 40, h - y1);
  return c;
}
function beyondFloor() { // landing floor: window light pooled toward the back wall (canvas top = doorway side)
  const w = 128, h = 128, c = cv(w, h), g = c.getContext('2d');
  g.fillStyle = col(30, 38, 44); g.fillRect(0, 0, w, h);
  const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(120,140,152,0.15)'); gr.addColorStop(1, 'rgba(150,172,186,0.6)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  return c;
}

// ------------------------------------------------------------------ the corridor
function buildCorridor(renderer) {
  const aniso = renderer.capabilities.getMaxAnisotropy();
  const fm = floorMaps();
  const floorMat = std({ map: canvasTexture(fm.map, { wrap: false }), roughnessMap: canvasTexture(fm.rough, { srgb: false, wrap: false }), roughness: 1.0, metalness: 0.0 });
  floorMat.map.anisotropy = floorMat.roughnessMap.anisotropy = aniso;
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(CW, LEN), floorMat); floor.rotation.x = -Math.PI / 2; floor.position.set(0, 0, ZMID); world.add(floor);
  // wet patch: a glossy film that mirrors P5 (and so flickers with it)
  const wet = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 0.95), std({ color: 0x55584e, roughness: 0.06, metalness: 0.0, transparent: true, opacity: 0.92, alphaMap: canvasTexture(wetMask(), { srgb: false, wrap: false }), depthWrite: false }));
  wet.rotation.x = -Math.PI / 2; wet.rotation.z = 0.3; wet.position.set(0.48, 0.004, -5.8); world.add(wet);
  // walls (painted block) — left: canvas left = near end; right: canvas left = far end
  const wl = wallMap(11, 1848, 360, LEN, (g, w, h, r) => { // a water stain running down from the ceiling
    const u = (ZN - (-5.25)) / LEN * w; const gr = g.createLinearGradient(0, 0, 0, h * 0.5); gr.addColorStop(0, 'rgba(110,84,46,0.55)'); gr.addColorStop(1, 'rgba(110,84,46,0)'); g.fillStyle = gr; g.fillRect(u - 10, 0, 20, h * 0.5); g.fillRect(u + 4, 0, 6, h * 0.62);
  });
  const wr = wallMap(12, 1848, 360, LEN);
  for (const [cnv, side] of [[wl, -1], [wr, 1]]) {
    const m = std({ map: canvasTexture(cnv, { wrap: false }), roughness: 0.92 }); m.map.anisotropy = aniso;
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(LEN, CH), m); wall.rotation.y = -side * Math.PI / 2; wall.position.set(side * XW, CH / 2, ZMID); world.add(wall);
  }
  // ceiling
  const cm = std({ map: canvasTexture(ceilingMap(), { wrap: false }), roughness: 0.95 }); cm.map.anisotropy = aniso;
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(CW, LEN), cm); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, CH, ZMID); world.add(ceil);
  // end wall behind the camera (rarely seen, but closes the box)
  box(CW, CH, 0.1, std({ color: 0x8c8e7c, roughness: 0.95 }), 0, CH / 2, ZN + 0.05);
  // far wall with the door opening (U-shaped polygon, UVs in metres)
  const s = new THREE.Shape([[-XW, 0], [-DW / 2, 0], [-DW / 2, DH], [DW / 2, DH], [DW / 2, 0], [XW, 0], [XW, CH], [-XW, CH]].map(([x, y]) => new THREE.Vector2(x, y)));
  const fwTex = canvasTexture(wallMap(13, 384, 360, CW), { wrap: false }); fwTex.repeat.set(1 / CW, 1 / CH); fwTex.offset.set(0.5, 0);
  const farWall = new THREE.Mesh(new THREE.ShapeGeometry(s), std({ map: fwTex, roughness: 0.92 })); farWall.position.z = ZF; world.add(farWall);
  const frameMat = std({ color: 0x2b3230, roughness: 0.55, metalness: 0.3 });
  box(0.06, DH + 0.06, 0.26, frameMat, -DW / 2 - 0.03, (DH + 0.06) / 2, ZF - 0.11); box(0.06, DH + 0.06, 0.26, frameMat, DW / 2 + 0.03, (DH + 0.06) / 2, ZF - 0.11); box(DW + 0.12, 0.06, 0.26, frameMat, 0, DH + 0.03, ZF - 0.11);
  box(0.075, 0.12, 0.012, std({ color: 0xb8b6a8, roughness: 0.6 }), 0.68, 1.22, ZF + 0.006); // light switch plate
  // the far door: swings away into the stairwell (push bar on the corridor side)
  doorPivot = new THREE.Group(); doorPivot.position.set(-DW / 2 + 0.01, 0, ZF - 0.03); world.add(doorPivot);
  const doorC = cv(64, 128); { const g = doorC.getContext('2d'), r = rng(3); g.fillStyle = col(62, 74, 70); g.fillRect(0, 0, 64, 128); for (let k = 0; k < 40; k++) { g.fillStyle = col(20, 24, 22, 0.15 + r() * 0.2); g.fillRect(r() * 64, 50 + r() * 70, 1 + r() * 4, 1 + r() * 2); } g.fillStyle = col(120, 124, 118); g.fillRect(0, 112, 64, 16); }
  const leafMat = std({ map: canvasTexture(doorC, { wrap: false }), roughness: 0.5, metalness: 0.15 });
  box(DW - 0.02, DH - 0.02, 0.045, leafMat, (DW - 0.02) / 2, (DH - 0.02) / 2, 0, doorPivot);
  box(0.78, 0.055, 0.06, std({ color: 0xa8aca4, roughness: 0.35, metalness: 0.6 }), DW / 2, 1.0, 0.05, doorPivot);
  // fire-exit sign over the door (abstract red, no letters) + its red spill
  const exitMats = [0, 0, 0, 0, 1, 0].map((k) => k ? new THREE.MeshBasicMaterial({ map: canvasTexture(exitFace(), { wrap: false }), color: new THREE.Color(2.2, 2.2, 2.2) }) : std({ color: 0x1a1a18, roughness: 0.6 }));
  const exit = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.18, 0.07), exitMats); exit.position.set(0, DH + 0.3, ZF + 0.04); world.add(exit);
  const red = new THREE.PointLight(0xff2a18, 0.35, 3.5, 2); red.position.set(0, DH + 0.18, ZF + 0.25); world.add(red);
  // lockers
  const topMat = std({ color: 0x55605a, roughness: 0.9 }), capMat = std({ color: 0x4e6662, roughness: 0.6, metalness: 0.2, side: THREE.DoubleSide }), hoodMat = std({ color: 0x3e4c46, map: canvasTexture(fbmCanvas(256, 64, { seed: 61, scale: 6, oct: 4, lo: 120, hi: 255 })), roughness: 0.62, metalness: 0.2 }), baseMat = std({ color: 0x1c1f1d, roughness: 0.8 });
  BANKS.forEach((b, i) => {
    const lm = lockerMaps(b.n, 100 + i); const len = b.n * LWD, zc = b.z0 - len / 2;
    const front = std({ map: canvasTexture(lm.map, { wrap: false }), bumpMap: canvasTexture(lm.bump, { srgb: false, wrap: false }), bumpScale: 1.2, roughness: 0.4, metalness: 0.3 }); front.map.anisotropy = aniso;
    const side = std({ color: 0x5e7c78, roughness: 0.6, metalness: 0.2 });
    const mats = b.side < 0 ? [front, side, topMat, baseMat, side, side] : [side, front, topMat, baseMat, side, side];
    const m = new THREE.Mesh(new THREE.BoxGeometry(LD, LH, len), mats); m.position.set(b.side * (XW - LD / 2), LB + LH / 2, zc); world.add(m);
    box(LD - 0.04, LB, len, baseMat, b.side * (XW - LD / 2 + 0.02), LB / 2, zc);
    // sloped hood (institutional lockers: nothing can sit on top) — reads as a lit strip from the high camera
    const hood = new THREE.Mesh(new THREE.PlaneGeometry(len, Math.hypot(LD, 0.37)), hoodMat);
    hood.position.set(b.side * (XW - LD / 2), LB + LH + 0.185, zc); hood.lookAt(hood.position.x - b.side * 0.698, hood.position.y + 0.716, zc); world.add(hood);
    const yT = LB + LH, cap = new THREE.BufferGeometry(), P = [];   // triangular end caps so the hood reads as a solid wedge
    for (const z of [b.z0, b.z0 - len]) P.push(b.side * XF, yT, z, b.side * XW, yT, z, b.side * XW, yT + 0.37, z);
    cap.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); cap.computeVertexNormals(); world.add(new THREE.Mesh(cap, capMat));
  });
  // classroom doors (dark, closed, narrow black windows)
  const woodC = cv(64, 128); { const g = woodC.getContext('2d'), r = rng(8); g.fillStyle = col(96, 72, 50); g.fillRect(0, 0, 64, 128); for (let k = 0; k < 60; k++) { g.fillStyle = col(60, 42, 28, 0.25); g.fillRect(r() * 64, 0, 1, 128); } }
  const woodMat = std({ map: canvasTexture(woodC, { wrap: false }), roughness: 0.6 }), glassMat = std({ color: 0x050707, roughness: 0.08, metalness: 0.0 });
  for (const d of SIDE_DOORS) {
    const x = d.side * (XW - 0.03);
    box(0.06, 2.16, 0.08, frameMat, x, 1.08, d.z - 0.5); box(0.06, 2.16, 0.08, frameMat, x, 1.08, d.z + 0.5); box(0.06, 0.08, 1.08, frameMat, x, 2.16, d.z);
    box(0.04, 2.1, 0.92, woodMat, d.side * (XW - 0.02), 1.05, d.z);
    box(0.012, 0.72, 0.13, glassMat, d.side * (XW - 0.045), 1.55, d.z + 0.2);
    box(0.06, 0.03, 0.13, std({ color: 0x9a9c94, roughness: 0.4, metalness: 0.6 }), d.side * (XW - 0.07), 1.0, d.z - 0.33);
  }
  // poster-shaped blank sheet high on the left wall; a bin in the gap after the first locker bank
  const poster = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 0.59), std({ map: canvasTexture(posterMap(), { wrap: false }), roughness: 0.85, alphaTest: 0.5 }));
  poster.rotation.set(0, Math.PI / 2, -0.025); poster.position.set(-XW + 0.006, 2.6, -4.2); world.add(poster); // above the first classroom door, on the lit wall
  const bin = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.18, 0.64, 20, 1, true), std({ color: 0x343a36, roughness: 0.65, side: THREE.DoubleSide })); bin.position.set(-XW + 0.26, 0.32, -2.8); world.add(bin);
  const binIn = new THREE.Mesh(new THREE.CircleGeometry(0.2, 20), std({ color: 0x0c0d0c, roughness: 1 })); binIn.rotation.x = -Math.PI / 2; binIn.position.set(-XW + 0.26, 0.5, -2.8); world.add(binIn);
  // double-faced corridor clock on a bracket from the left wall
  const clock = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.07, 32), [std({ color: 0x1a1a18, roughness: 0.5 }), std({ map: canvasTexture(clockFace(), { wrap: false }), roughness: 0.3 }), std({ color: 0x1a1a18 })]);
  clock.rotation.x = Math.PI / 2; clock.position.set(-XW + 0.3, 2.42, -7.6); world.add(clock);
  box(0.3, 0.025, 0.025, frameMat, -XW + 0.15, 2.62, -7.6); box(0.02, 0.05, 0.02, frameMat, -XW + 0.3, 2.6, -7.6);
  // fluorescent troffers: emissive diffuser + frame + a RectAreaLight each (dead panel has no light)
  const diff = canvasTexture(diffuserMap(), { wrap: false }), trofFrame = std({ color: 0xcfd0c8, roughness: 0.5, metalness: 0.2 });
  PANELS.forEach((p, i) => {
    // each fixture hangs from a pivot at its near end; the dead one (P1) has dropped its far end: the crooked panel
    const piv = new THREE.Group(); piv.position.set(0, CH, p.z + 0.615); world.add(piv);
    if (p.s === 0) piv.rotation.set(-0.21, 0.05, 0.07);
    box(0.62, 0.03, 1.23, trofFrame, 0, -0.015, -0.615, piv);
    const m = new THREE.MeshBasicMaterial({ map: diff, color: new THREE.Color(0.11, 0.11, 0.105) });
    const d = new THREE.Mesh(new THREE.PlaneGeometry(0.56, 1.17), m); d.rotation.x = Math.PI / 2; d.position.set(0, -0.032, -0.615); piv.add(d); panelMats[i] = m;
    if (p.s) { const L = new THREE.RectAreaLight(new THREE.Color(...PANEL_RGB), RECT_I, 0.56, 1.17); L.position.set(0, CH - 0.035, p.z); L.rotation.x = -Math.PI / 2; world.add(L); panelLights[i] = L; }
  });
  world.add(new THREE.HemisphereLight(0xb8c6b8, 0x8a8470, 0.7));
  const bounce = new THREE.DirectionalLight(0xb4ae98, 0.35); bounce.position.set(0.3, -10, -4); bounce.target.position.set(0, 0, -6); world.add(bounce, bounce.target); // lit floor → ceiling
  // the stairwell beyond the far door (unlit: what we see is its own cold window light)
  const bm = (cnv, c) => new THREE.MeshBasicMaterial({ map: cnv ? canvasTexture(cnv, { wrap: false }) : null, color: c ?? 0xffffff, side: THREE.BackSide });
  const sideG = cv(8, 64); { const g = sideG.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 64); gr.addColorStop(0, '#0e1215'); gr.addColorStop(1, '#1a2024'); g.fillStyle = gr; g.fillRect(0, 0, 8, 64); }
  const beyond = new THREE.Mesh(new THREE.BoxGeometry(CW, CH, 3.0), [bm(sideG), bm(sideG), bm(null, 0x0b0e10), bm(beyondFloor()), bm(null, 0x000000), bm(beyondWall())]);
  beyond.position.set(0, CH / 2, ZF - 0.2 - 1.5); world.add(beyond);
}

// ------------------------------------------------------------------ the figure: primitives, near-black, slightly too tall; two states only
function buildFigure() {
  const m = std({ color: 0x050505, roughness: 0.95 }), g = new THREE.Group();
  const cap = (r, len, x, y, z, rz = 0) => { const me = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 4, 10), m); me.position.set(x, y, z); me.rotation.z = rz; g.add(me); return me; };
  cap(0.068, 0.93, -0.095, 0.53, 0, 0.035); cap(0.066, 0.93, 0.1, 0.53, 0.02, -0.02);           // legs (weight on the left)
  cap(0.15, 0.64, 0.0, 1.4, 0, 0.03);                                                             // long narrow torso
  const sh = cap(0.07, 0.36, 0.0, 1.8, 0); sh.rotation.z = Math.PI / 2 + 0.05;                   // shoulders (one lower)
  cap(0.046, 0.98, -0.25, 1.27, 0.03, -0.075); cap(0.046, 0.98, 0.255, 1.27, 0.03, 0.06);         // arms hang clear of the body, to the knee
  cap(0.03, 0.17, -0.29, 0.66, 0.05, -0.12); cap(0.03, 0.17, 0.285, 0.66, 0.05, 0.1);             // long hands
  neck = new THREE.Group(); neck.position.set(0.0, 1.86, 0.0); g.add(neck);
  const nk = new THREE.Mesh(new THREE.CapsuleGeometry(0.045, 0.13, 4, 8), m); nk.position.y = 0.07; neck.add(nk);
  const hd = new THREE.Mesh(new THREE.SphereGeometry(0.105, 18, 14), m); hd.scale.set(0.9, 1.3, 1.0); hd.position.y = 0.2; neck.add(hd);
  g.position.set(0.03, 0, ZF - 0.08); g.rotation.y = 0.07; g.visible = false;
  return g;
}

// ------------------------------------------------------------------ scene-owned post passes
const VS = `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`;
const ZoomShader = { // digital zoom: crop + bilinear upscale of the sensor image (resolution really is lost), slight CCD softness
  uniforms: { tDiffuse: { value: null }, k: { value: 1 }, center: { value: new THREE.Vector2(0.5, 0.5) }, px: { value: new THREE.Vector2(1 / 1280, 1 / 720) } },
  vertexShader: VS,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float k; uniform vec2 center; uniform vec2 px; varying vec2 vUv;
  void main(){ vec2 uv=center+(vUv-0.5)/k; vec3 c=0.5*(texture2D(tDiffuse,uv+0.5*px).rgb+texture2D(tDiffuse,uv-0.5*px).rgb); gl_FragColor=vec4(c,1.0); }`,
};
const PlaybackShader = { // tape faults: tracking band, line tearing, head-switching skew, hum bar, signal loss
  uniforms: { tDiffuse: { value: null }, resolution: { value: new THREE.Vector2(1280, 720) }, frame: { value: 0 }, time: { value: 0 }, band: { value: 0 }, bandY: { value: 0.5 }, bandH: { value: 0.11 },
    jitter: { value: 0.6 }, vshift: { value: 0 }, hsw: { value: 1 }, blackout: { value: 0 }, humbar: { value: 0.035 } },
  vertexShader: VS,
  fragmentShader: `uniform sampler2D tDiffuse; uniform vec2 resolution; uniform float frame, time, band, bandY, bandH, jitter, vshift, hsw, blackout, humbar; varying vec2 vUv;
  float hash(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
  void main(){
    if(blackout>0.5){ gl_FragColor=vec4(0.0,0.0,0.0,1.0); return; }
    vec2 uv=vUv; uv.y=clamp(uv.y+vshift,0.0,1.0);
    float line=floor(uv.y*resolution.y);
    float dx=(hash(vec2(line,frame))-0.5)*jitter;
    float d=abs(uv.y-bandY);
    float inB=band*(1.0-smoothstep(bandH*0.5,bandH,d));
    float nearB=band*(1.0-smoothstep(bandH,bandH*2.8,d));
    dx+=(hash(vec2(floor(uv.y*resolution.y/3.0),frame*1.37))-0.3)*75.0*inB;
    dx+=sin(uv.y*55.0+frame*2.1)*8.0*nearB;
    float hs=hsw*(1.0-smoothstep(0.0,18.0/resolution.y,uv.y));
    dx+=hs*(18.0+26.0*hash(vec2(line,floor(frame*0.5))));
    uv.x+=dx/resolution.x;
    vec3 col=texture2D(tDiffuse,uv).rgb;
    float segW=4.0+34.0*hash(vec2(line,frame+3.0));
    float seg=floor(uv.x*resolution.x/segW);
    float sn=hash(vec2(seg,line*1.31+frame*17.0));
    col=mix(col,vec3(0.5+0.5*hash(vec2(seg+7.0,line))),step(0.86-0.3*inB,sn)*inB);
    col=mix(col,col*0.65+vec3(0.10),inB*0.6);
    col=mix(col,vec3(0.8*hash(vec2(floor(uv.x*resolution.x*0.5),line+frame))),hs*0.45);
    float hy=fract(time*0.09); float hb=exp(-pow((fract(uv.y-hy+0.5)-0.5)/0.09,2.0)); col*=1.0-humbar*hb;
    gl_FragColor=vec4(col,1.0);
  }`,
};
const BezelShader = { // 4:3 picture with rounded CRT corners, clean black pillars
  uniforms: { tDiffuse: { value: null }, resolution: { value: new THREE.Vector2(1280, 720) }, rect: { value: new THREE.Vector4(171, 8, 1109, 712) }, radius: { value: 26 } },
  vertexShader: VS,
  fragmentShader: `uniform sampler2D tDiffuse; uniform vec2 resolution; uniform vec4 rect; uniform float radius; varying vec2 vUv;
  void main(){ vec3 c=texture2D(tDiffuse,vUv).rgb; vec2 p=vUv*resolution; vec2 ctr=0.5*(rect.xy+rect.zw); vec2 hs=0.5*(rect.zw-rect.xy);
    vec2 q=abs(p-ctr)-(hs-radius); float d=length(max(q,0.0))+min(max(q.x,q.y),0.0)-radius;
    float m=1.0-smoothstep(-1.0,1.0,d); float glass=smoothstep(-26.0,0.0,d);
    gl_FragColor=vec4(c*m*(1.0-0.2*glass),1.0); }`,
};

// ------------------------------------------------------------------ overlay (burned-in OSD and the card)
function drawOSD(c, f) {
  const s = W / 1280, sy = H / 720, k = f - EV.stutter[0], glitch = k >= 0 && k < 3;
  const sec = f < EV.stutter[1] ? 7 : 9 + Math.floor((f - EV.stutter[1]) / FPS); // frozen on :07, then :09 — a second is missing
  const ss = glitch && k === 1 ? '  ' : String(sec).padStart(2, '0');
  const x = (187 + (glitch ? [9, -5, 3][k] : 0)) * s, y = (20 + (glitch ? [3, -2, 1][k] : 0)) * sy, a = glitch ? [0.75, 1, 0.85][k] : 1;
  c.save(); c.font = `400 ${Math.round(42 * sy)}px "VT323"`; c.textBaseline = 'top'; c.lineJoin = 'round'; c.lineWidth = 4 * sy;
  const put = (txt, px, al = 'left') => { c.textAlign = al; c.strokeStyle = `rgba(0,0,0,${0.8 * a})`; c.strokeText(txt, px, y); c.fillStyle = `rgba(240,242,232,${a})`; c.fillText(txt, px, y); };
  put(`CAM 03   02:14:${ss}`, x);
  if (glitch && k === 0) { c.globalAlpha = 0.3; c.fillText(`CAM 03   02:14:${ss}`, x + 16 * s, y + 7 * sy); c.globalAlpha = 1; } // a torn ghost of the line
  if (f % 24 < 15) { // REC blinks on the recorder's own clock
    const rx = (1093 + (glitch ? [9, -5, 3][k] : 0)) * s, dx = rx - 11 * s; put('REC', rx - 32 * s, 'right'); // "REC ●"
    c.fillStyle = `rgba(0,0,0,${0.8 * a})`; c.beginPath(); c.arc(dx, y + 21 * sy, 11 * sy, 0, 6.3); c.fill();
    c.fillStyle = `rgba(235,40,28,${a})`; c.beginPath(); c.arc(dx, y + 21 * sy, 8.5 * sy, 0, 6.3); c.fill();
  }
  c.restore();
}
function drawCard(c, f) {
  const k = f - CUT[4], n = CUT[5] - CUT[4];
  const env = Math.min(1, (k + 1) / 4) * Math.min(1, (n - k) / 5);
  const fl = (k === 6 || k === 11 ? 0.55 : 1) * (0.9 + 0.1 * noise1(k * 1.9, 4));
  const v = 0.58 * env * fl;
  c.save(); c.font = `400 ${Math.round(34 * H / 720)}px "VT323"`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.letterSpacing = `${Math.round(3 * W / 1280)}px`;
  c.fillStyle = `rgb(${osd(v)},${osd(v)},${osd(v * 0.96)})`; c.fillText('TAPE 3 OF 11', W / 2, H / 2); c.restore();
}

// ------------------------------------------------------------------ boot
await boot({
  fps: FPS, shots: SHOTS, fonts: [['VT323', 400]], exposure: 1.15,
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; const { renderer } = ctx;
    RectAreaLightUniformsLib.init();
    scene = new THREE.Scene(); scene.background = BG; scene.fog = new THREE.FogExp2(0x1a2420, 0.018);
    world = new THREE.Group(); scene.add(world);
    const qc = ctx.q.get('cam'); if (qc) { const v = qc.split(',').map(Number); CAM.pos = v.slice(0, 3); CAM.yaw = v[3]; CAM.pitch = v[4]; } // tuning override only
    camera = new THREE.PerspectiveCamera(30, W / H, 0.05, 60); rig = new CameraRig(camera);
    buildCorridor(renderer);
    figure = buildFigure(); world.add(figure);
    // CCTV mount: position + yaw/pitch → look target; small installer's roll
    const yw = CAM.yaw * Math.PI / 180, pt = CAM.pitch * Math.PI / 180, P = CAM.pos;
    const look = [P[0] + 10 * Math.sin(yw) * Math.cos(pt), P[1] - 10 * Math.sin(pt), P[2] - 10 * Math.cos(yw) * Math.cos(pt)];
    rig.set({ pos: P, look, mm: CAM.mm }); rig.roll = CAM.roll * Math.PI / 180; rig.apply(); camera.updateMatrixWorld();
    const uvOf = (x, y, z) => { const p = new THREE.Vector3(x, y, z).project(camera); return new THREE.Vector2((p.x + 1) / 2, (p.y + 1) / 2); };
    zoomTarget = uvOf(0.0, 1.02, ZF);
    const dTop = uvOf(0, DH, ZF), dBot = uvOf(0, 0, ZF);
    console.log(`door centre uv ${zoomTarget.x.toFixed(3)},${zoomTarget.y.toFixed(3)}  door y ${dBot.y.toFixed(3)}..${dTop.y.toFixed(3)}`);
    post = makeComposer(renderer, scene, camera, { bloom: { strength: 0.3, radius: 0.45, threshold: 0.92 }, grade: 'vhs',
      finish: { saturation: 0.7, contrast: 1.06, grain: 0.12, grainSize: 2, vignette: 0.4, halation: 0.12, lift: [0.02, 0.028, 0.026], shadowTint: [-0.012, 0.022, 0.014], highlightTint: [0.0, 0.012, 0.0] } });
    // insert the scene-owned passes around the kit's overlay and finish
    const P_ = post.composer.passes;
    zoomPass = new ShaderPass(ZoomShader); zoomPass.uniforms.px.value.set(1 / W, 1 / H);
    post.composer.insertPass(zoomPass, P_.findIndex((p) => p.uniforms && p.uniforms.tOverlay));
    playPass = new ShaderPass(PlaybackShader); playPass.uniforms.resolution.value.set(W, H);
    post.composer.insertPass(playPass, P_.findIndex((p) => p.uniforms === post.finish));
    bezelPass = new ShaderPass(BezelShader); bezelPass.uniforms.resolution.value.set(W, H);
    bezelPass.uniforms.rect.value.set(WIN.x0 * W / 1280, WIN.y0 * H / 720, WIN.x1 * W / 1280, WIN.y1 * H / 720); bezelPass.uniforms.radius.value = WIN.r * H / 720;
    post.composer.addPass(bezelPass);
  },
  render: async (ctx, i, t) => {
    const f = Math.round(t * FPS);
    const n = f < CUT[1] ? 0 : f < CUT[2] ? 1 : f < CUT[3] ? 2 : f < CUT[4] ? 3 : 4;
    const tape = n <= 2;
    world.visible = tape; scene.background = tape ? BG : BLACK;
    // practicals: P2/P3/P4 steady (tiny mains wobble), P1 dead and hanging crooked, P5 failing by the far door
    const fl = flickerLevel(f);
    PANELS.forEach((p, k) => {
      const lv = p.s === 0 ? 0 : (p.s === 2 ? fl : 1) * (0.985 + 0.015 * noise1(t * 3.1, k));
      const I = p.s === 0 ? 0.11 : Math.max(0.1, PANEL_I * lv);
      panelMats[k].color.setRGB(PANEL_RGB[0] * I, PANEL_RGB[1] * I, PANEL_RGB[2] * I);
      if (panelLights[k]) panelLights[k].intensity = RECT_I * lv;
    });
    // continuity: the door (closed → open under the band) and the figure (absent → standing)
    doorPivot.rotation.y = f >= EV.door ? DOOR_OPEN : 0;
    figure.visible = n === 2 && f >= EV.figure;
    if (figure.visible) { const k = f - EV.figure; neck.rotation.z = 0.46 - 0.15 * Math.exp(-k / 3.5) * Math.cos(k * 0.5); } // only the tilt settles (R-5-04)
    // camera never moves; S3 is a digital zoom of the sensor image toward the doorway (noticing)
    rig.apply();
    const zs = n === 2 ? ease.inOutSine(clamp((f - EV.zoom[0]) / (EV.zoom[1] - EV.zoom[0]))) : 0;
    const k = lerp(1, ZOOM_K, zs), hk = 0.5 / k;
    zoomPass.uniforms.k.value = k;
    zoomPass.uniforms.center.value.set(clamp(lerp(0.5, zoomTarget.x, zs), hk, 1 - hk), clamp(lerp(0.5, zoomTarget.y, zs), hk, 1 - hk));
    // playback faults
    const pu = playPass.uniforms; pu.frame.value = f; pu.time.value = t;
    const inBand = f >= EV.band[0] && f < EV.band[1];
    const band = inBand ? Math.min(1, (f - EV.band[0] + 1) / 2.5, (EV.band[1] - f) / 2.5) : 0;
    pu.band.value = band; pu.bandY.value = lerp(1.18, -0.18, clamp((f - EV.band[0]) / (EV.band[1] - 1 - EV.band[0])));
    pu.jitter.value = 0.6 + 4.0 * band; pu.vshift.value = (f === 88 || f === 89) ? 0.012 : (f === 101) ? -0.006 : 0;
    pu.hsw.value = n === 3 ? 0 : 1; pu.blackout.value = (f >= EV.drop[0] && f < EV.drop[1]) ? 1 : 0;
    // overlay: OSD on tape, card at the end
    const { ctx: c, clear } = post.overlay; clear();
    if (tape) drawOSD(c, f);
    if (n === 4) drawCard(c, f);
    // finish: one grade; the tracking error spikes the CRT/VHS mode and weave; S4 is true black
    const fz = post.finish; fz.fade.value = n === 3 ? 0 : 1; fz.modeAmount.value = 1 + 0.25 * band; fz.weave.value = 3.0 * band;
    post.render(t);
  },
});
