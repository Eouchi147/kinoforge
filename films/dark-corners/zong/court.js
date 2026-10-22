// The London court by candlelight: chandelier, a raised bench with a faceless judge, a jury box, the dock, windows with rain.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, rng, valueNoise2D } from '/harness/kit/film.js';
import { Setup, setLights, DW, DH } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, underpaint } from './paint.js';
import { WARM, GLOW, coverCams, flick, line, paintPerson } from './common.js';

const CD = { wall: 40, floor: 30, bench: 28, judge: 27.5, jury: 24, dock: 20, chand: 14, table: 18, lawyer: 16, pew: 6 };
const CAND = { // candle groups: flames in design px at their plane depth
  chand: { D: CD.chand, pts: Array.from({ length: 8 }, (_, i) => [360 + 150 * Math.cos(i * Math.PI / 4), 262 + 26 * Math.sin(i * Math.PI / 4)]) },
  bench: { D: CD.bench, pts: [[196, 622], [524, 622]] }, table: { D: CD.table, pts: [[130, 944], [596, 944]] }, dock: { D: CD.dock, pts: [[112, 826]] },
};
export const WIN = [[34, 150, 186, 640], [534, 150, 686, 640]];

function bust(C, x, yb, w, h, P) { // head and shoulders, faceless
  const g = C.g, R = C.R; const col = P.col || [14, 12, 22]; g.fillStyle = rgba(col);
  g.beginPath(); g.moveTo(x - w / 2, yb); g.quadraticCurveTo(x - w / 2, yb - h * 0.55, x - w * 0.22, yb - h * 0.6); g.lineTo(x + w * 0.22, yb - h * 0.6); g.quadraticCurveTo(x + w / 2, yb - h * 0.55, x + w / 2, yb); g.closePath(); g.fill();
  g.fillRect(x - w * 0.09, yb - h * 0.72, w * 0.18, h * 0.16); const hr = w * 0.17; const hy = yb - h * 0.8; g.beginPath(); g.ellipse(x, hy, hr * 0.86, hr * 1.06, 0, 0, Math.PI * 2); g.fill();
  if (P.wig) { g.beginPath(); g.ellipse(x, hy - hr * 0.25, hr * 1.2, hr * 1.2, 0, 0, Math.PI * 2); g.fill(); g.beginPath(); g.ellipse(x - hr * 1.0, hy + hr * 0.9, hr * 0.62, hr * 1.0, 0, 0, Math.PI * 2); g.ellipse(x + hr * 1.0, hy + hr * 0.9, hr * 0.62, hr * 1.0, 0, 0, Math.PI * 2); g.fill();
    if (P.wigLit) for (let k = 0; k < 14; k++) C.dab(x + (R() - 0.5) * hr * 2, hy - hr * 0.6 + R() * hr * 0.9, (R() - 0.5), hr * 0.5, 1.4, P.wigLit, 0.3 + R() * 0.3, 0.1); }
  else if (P.hat) { g.beginPath(); g.ellipse(x, hy - hr * 0.7, hr * 1.5, hr * 0.5, 0, 0, Math.PI * 2); g.fill(); g.fillRect(x - hr * 0.9, hy - hr * 1.5, hr * 1.8, hr * 0.9); }
  if (P.rim) { for (let k = 0; k < 8; k++) C.dab(x - w * 0.46 + R() * w * 0.2, yb - h * (0.1 + R() * 0.45), Math.PI / 2, 8 + R() * 14, 1.6, P.rim, 0.4, 0.05); C.dab(x - hr * 0.8, hy - hr * 0.2, Math.PI / 2, hr * 1.2, 1.6, P.rim, 0.55, 0); }
}
function candleStand(C, x, y, h, flameUp = true) { const g = C.g; g.fillStyle = rgba(hex('#2a1d14')); g.fillRect(x - 9, y - h, 18, h); g.fillStyle = rgba(hex('#d8c59a')); g.fillRect(x - 5, y - h - 22, 10, 22); C.dab(x - 2, y - h - 11, Math.PI / 2, 18, 2.6, hex('#fff0c8'), 0.7, 0); g.fillStyle = rgba(hex('#1b120c')); g.fillRect(x - 1, y - h - 28, 2, 7); }

export function buildCourt(shots) {
  const S = new Setup('court', { pos: [0, 0, 0], mm: 35 }); const f = S.f; const cams = coverCams(shots, 'court'); const cover = (D, m) => S.cover(D, cams, m);
  const planes = {}; const wood = (a, b) => mixc(hex(a), hex(b), 0.5);
  // back wall: panelling, two tall windows, a pediment over the bench
  { const r = cover(CD.wall, 60); const C = new Canvas(r, { seed: 1301 }); const g = C.g, R = C.R, n = C.n;
    underpaint(C, (x, y) => mixc(hex('#2a1c16'), hex('#120c0c'), smoothstep(100, 1000, y)), null, 12);
    C.strokes({ n: C.area / 900, color: (x, y) => mixc(hex('#3a271c'), hex('#150e0d'), n.fbm(x * 0.01, y * 0.004, 3)), angle: () => Math.PI / 2 + (R() - 0.5) * 0.05, len: [40, 140], wid: [4, 9], alpha: [0.3, 0.55], jv: 0.1 });
    for (let y = 700; y < 1000; y += 140) for (let x = -60; x < 800; x += 190) { g.strokeStyle = rgba(hex('#0b0706'), 0.8); g.lineWidth = 3; g.strokeRect(x + 14, y + 12, 160, 116); C.dab(x + 14, y + 12, 0, 160, 2, hex('#6a4a34'), 0.3, 0, 0.3); }
    for (const [x0, y0, x1, y1] of WIN) { const arch = new Path2D(); arch.moveTo(x0, y1); arch.lineTo(x0, y0 + 90); arch.quadraticCurveTo(x0, y0, (x0 + x1) / 2, y0 - 20); arch.quadraticCurveTo(x1, y0, x1, y0 + 90); arch.lineTo(x1, y1); arch.closePath();
      g.save(); g.clip(arch); const gr = g.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, rgba(hex('#1d2c5a'))); gr.addColorStop(1, rgba(hex('#0a1028'))); g.fillStyle = gr; g.fillRect(x0, y0 - 30, x1 - x0, y1 - y0 + 40);
      C.strokes({ n: 90, box: [x0, y0 - 20, x1, y1], mask: (x, y) => 1, color: () => mixc(hex('#31468a'), hex('#16204a'), R()), angle: () => (R() - 0.5) * 0.3, len: [20, 70], wid: [5, 9], alpha: [0.25, 0.5] }); g.restore();
      g.strokeStyle = rgba(hex('#0b0706')); g.lineWidth = 7; g.stroke(arch); g.lineWidth = 3.6; g.beginPath(); g.moveTo((x0 + x1) / 2, y0 - 20); g.lineTo((x0 + x1) / 2, y1); for (let k = 1; k < 5; k++) { g.moveTo(x0, y0 + 90 + k * 90); g.lineTo(x1, y0 + 90 + k * 90); } g.stroke();
      C.dab(x0 + 3, (y0 + y1) / 2, Math.PI / 2, (y1 - y0) * 0.8, 2.4, hex('#8fa6dc'), 0.45, 0, 0.2); }
    // pediment + royal-arms plaque over the bench (abstract carved shape)
    g.fillStyle = rgba(hex('#171009')); g.beginPath(); g.moveTo(150, 430); g.lineTo(360, 330); g.lineTo(570, 430); g.closePath(); g.fill(); for (let x = 160; x < 560; x += 6) C.dab(x, 430 - Math.abs(x - 360) * 0.47, 0, 12, 2, hex('#7a5a30'), 0.5, 0, 0.3);
    g.fillStyle = rgba(hex('#3a2a14')); g.beginPath(); g.moveTo(330, 460); g.lineTo(390, 460); g.lineTo(380, 500); g.lineTo(360, 516); g.lineTo(340, 500); g.closePath(); g.fill(); C.dab(360, 478, Math.PI / 2, 30, 3, hex('#b08a4a'), 0.5, 0);
    C.mottle({ amt: 0.05 }); planes.wall = S.plane('wall', CD.wall, r, C.c); }
  // floor
  { const r = cover(CD.floor, 60); const C = new Canvas(r, { seed: 1311 }); const R = C.R; const [x0, y0, x1, y1] = r; const VP = [360, 690];
    const fp = new Path2D(); fp.rect(x0 - 10, 930, x1 - x0 + 20, y1 - 930 + 10); const fm = C.mask((gg) => gg.fill(fp));
    underpaint(C, (x, y) => mixc(hex('#1e1612'), hex('#0a0707'), smoothstep(930, y1, y)), fp, 12); C.strokes({ n: C.area / 1100, mask: fm, color: (x, y) => mixc(hex('#2c1f18'), hex('#0c0808'), R()), angle: () => (R() - 0.5) * 0.06, len: [40, 120], wid: [4, 9], alpha: [0.3, 0.55], jv: 0.1 });
    for (let k = -9; k <= 9; k++) { const xb = 360 + k * 130; for (let s = 0; s < 1; s += 0.02) { const y = lerp(930, y1, s); const x = lerp(VP[0] + (xb - VP[0]) * (930 - VP[1]) / (y1 - VP[1]), xb, s); C.dab(x, y, Math.atan2(y1 - VP[1], xb - VP[0]), 16 + s * 40, 1.6 + s * 2, hex('#050303'), 0.7, 0.02, 0.4); } }
    C.mottle({ amt: 0.05 }); planes.floor = S.plane('floor', CD.floor, r, C.c); planes.floor.userData.top = 930; }
  // bench (the judge's raised box) + steps
  { const r = [60, 560, 660, 960]; const C = new Canvas(r, { seed: 1321 }); const g = C.g, R = C.R;
    const body = new Path2D(); body.moveTo(150, 645); body.lineTo(570, 645); body.lineTo(590, 940); body.lineTo(130, 940); body.closePath(); const col = (x, y) => mixc(hex('#33211a'), hex('#150d0c'), smoothstep(645, 940, y));
    underpaint(C, col, body, 6); const m = C.mask((gg) => gg.fill(body)); C.strokes({ n: 260, mask: m, color: col, angle: () => Math.PI / 2 + (R() - 0.5) * 0.04, len: [30, 100], wid: [4, 8], alpha: [0.35, 0.6], jv: 0.1 });
    for (const [a, b, c2, d] of [[170, 680, 330, 900], [390, 680, 550, 900]]) { g.strokeStyle = rgba(hex('#0a0605'), 0.85); g.lineWidth = 4; g.strokeRect(a, b, c2 - a, d - b); C.dab(a, b, 0, c2 - a, 2, hex('#7a5a3e'), 0.35, 0, 0.3); C.dab(a, b, Math.PI / 2, d - b, 2, hex('#7a5a3e'), 0.25, 0, 0.3); }
    g.fillStyle = rgba(hex('#1d130f')); g.fillRect(138, 628, 444, 24); for (let x = 140; x < 580; x += 5 + R() * 5) C.dab(x, 630, 0, 12 + R() * 12, 2.4, hex('#a8784a'), 0.4 + R() * 0.3, 0, 0.4);
    g.fillStyle = rgba(hex('#241711')); g.fillRect(110, 940, 500, 20); for (let x = 112; x < 600; x += 6 + R() * 6) C.dab(x, 942, 0, 12, 2.2, hex('#9a6c44'), 0.35, 0, 0.4);
    for (const x of [196, 524]) candleStand(C, x, 628, 24);
    C.mottle({ amt: 0.05 }); planes.bench = S.plane('bench', CD.bench, r, C.c); }
  // the judge: scarlet robe, full-bottomed wig, faceless
  { const r = [200, 400, 520, 660]; const C = new Canvas(r, { seed: 1331 }); const g = C.g;
    bust(C, 360, 662, 190, 150, { col: hex('#3a0f14'), wig: true, wigLit: hex('#c9b79a'), rim: hex('#c98a5a') });
    g.fillStyle = rgba(hex('#8a7c66'), 0.75); g.fillRect(352, 598, 6, 44); g.fillRect(364, 598, 6, 44);
    C.mottle({ amt: 0.04 }); planes.judge = S.plane('judge', CD.judge, r, C.c); planes.judge.userData.flame = true; }
  // jury box: a railed box, two rows of faceless jurors
  { const r = [440, 640, 740, 980]; const C = new Canvas(r, { seed: 1341 }); const g = C.g, R = C.R;
    g.fillStyle = rgba(hex('#1b120e')); g.fillRect(450, 760, 280, 220);
    for (let row = 0; row < 2; row++) for (let k = 0; k < 6; k++) { const x = 492 + k * 46 + (row ? 20 : 0) + (R() - 0.5) * 4, yb = row ? 902 : 836; bust(C, x, yb, 46, 66 - row * 4, { col: mixc(hex('#0e0c18'), hex('#1b1620'), R() * 0.5), hat: R() < 0.25, wig: R() < 0.3, rim: hex('#c98a5a') }); }
    g.fillStyle = rgba(hex('#2a1b14')); g.fillRect(444, 900, 296, 80); for (let x = 446; x < 738; x += 20) { g.fillStyle = rgba(hex('#120b08')); g.fillRect(x, 908, 6, 64); } for (let x = 446; x < 738; x += 5 + R() * 5) C.dab(x, 902, 0, 12 + R() * 10, 2.4, hex('#a8784a'), 0.4 + R() * 0.3, 0, 0.4);
    C.mottle({ amt: 0.05 }); planes.jury = S.plane('jury', CD.jury, r, C.c); }
  // the dock: a waist-high wooden pen at the left (empty), one candle on its rail
  { const r = [-60, 780, 330, 1040]; const C = new Canvas(r, { seed: 1351 }); const g = C.g, R = C.R;
    g.fillStyle = rgba(hex('#241810')); g.fillRect(-40, 830, 330, 14); g.fillRect(-40, 950, 330, 18); for (let x = -30; x < 290; x += 34) { g.fillStyle = rgba(hex('#170f0a')); g.fillRect(x, 842, 10, 112); C.dab(x - 1, 898, Math.PI / 2, 100, 1.6, hex('#8a5e3a'), 0.35, 0, 0.2); }
    for (let x = -40; x < 290; x += 5 + R() * 5) C.dab(x, 832, 0, 12 + R() * 10, 2.4, hex('#a8784a'), 0.4 + R() * 0.3, 0, 0.4);
    candleStand(C, 112, 830, 16); g.fillStyle = rgba(hex('#0f0a07')); for (const x of [-30, 262]) { g.fillRect(x, 800, 16, 190); } C.mottle({ amt: 0.05 }); planes.dock = S.plane('dock', CD.dock, r, C.c); }
  // the lawyers' table with open ledgers and two candles
  { const r = [-40, 880, 760, 1180]; const C = new Canvas(r, { seed: 1361 }); const g = C.g, R = C.R;
    const top = new Path2D(); top.moveTo(-30, 960); top.lineTo(750, 960); top.lineTo(780, 1010); top.lineTo(-60, 1010); top.closePath(); g.fillStyle = rgba(hex('#2a1b14')); g.fill(top); for (let x = -40; x < 780; x += 5 + R() * 5) C.dab(x, 962, 0, 14 + R() * 12, 2.4, hex('#b08050'), 0.4 + R() * 0.3, 0, 0.4);
    g.fillStyle = rgba(hex('#130c0a')); g.fillRect(-60, 1010, 840, 160); for (let x = -40; x < 780; x += 8 + R() * 10) C.dab(x, 1080 + R() * 60, Math.PI / 2, 40 + R() * 60, 3, hex('#2a1b14'), 0.4, 0.02);
    for (const [cx, w] of [[300, 150], [470, 130]]) { g.fillStyle = rgba(hex('#8f7d58')); g.beginPath(); g.moveTo(cx - w / 2, 985); g.lineTo(cx + w / 2, 985); g.lineTo(cx + w / 2 + 14, 1006); g.lineTo(cx - w / 2 - 14, 1006); g.closePath(); g.fill(); g.strokeStyle = rgba(hex('#5a4630'), 0.7); g.lineWidth = 1.4; for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(cx - w / 2 + 8, 991 + k * 4.5); g.lineTo(cx + w / 2 - 8, 991 + k * 4.5); g.stroke(); } }
    for (const x of [130, 596]) candleStand(C, x, 960, 18); C.mottle({ amt: 0.05 }); planes.table = S.plane('table', CD.table, r, C.c); }
  // the owners' lawyer: standing at the table, wig and gown, one arm raised
  { const r = [20, 520, 360, 1030]; const C = new Canvas(r, { seed: 1371 });
    paintPerson(C, { x: 150, yb: 1022, h: 430, face: 1, hat: 'wig', coat: 1.0, flare: 1.5, shoulder: 18, col: hex('#0c0a13'), rim: null, arms: [{ s: [14, 4], e: [38, -14], h: [44, -52] }, { s: [-14, 4], e: [-24, 22], h: [-14, 36] }] });
    C.mottle({ amt: 0.04 }); planes.lawyer = S.plane('lawyer', CD.lawyer, r, C.c); }
  // chandelier (hangs from above): iron ring, chain, eight candle stubs
  { const r = [180, -200, 540, 330]; const C = new Canvas(r, { seed: 1381 }); const g = C.g;
    g.strokeStyle = rgba(hex('#0b0807')); g.lineWidth = 4; g.beginPath(); g.moveTo(360, -200); g.lineTo(360, 244); g.stroke(); for (let y = -200; y < 240; y += 16) { g.lineWidth = 3; g.beginPath(); g.ellipse(360, y + 8, 4.5, 8, 0, 0, 6.3); g.stroke(); }
    g.lineWidth = 7; g.beginPath(); g.ellipse(360, 262, 150, 26, 0, 0, Math.PI * 2); g.stroke(); C.dab(300, 238, 0, 130, 2.2, hex('#c98a5a'), 0.5, 0, 0.3);
    for (const [fx, fy] of CAND.chand.pts) { g.fillStyle = rgba(hex('#d8c59a')); g.fillRect(fx - 4, fy - 4, 8, 18); g.fillStyle = rgba(hex('#0b0807')); g.fillRect(fx - 7, fy + 12, 14, 5); }
    C.mottle({ amt: 0.04 }); planes.chand = S.plane('chand', CD.chand, r, C.c); }
  // foreground pew: two heads from behind at the bottom (spectators), out of focus
  { const r = [-60, 1040, 780, 1400]; const C = new Canvas(r, { seed: 1391 }); const g = C.g, R = C.R;
    g.fillStyle = rgba(hex('#07050a')); g.fillRect(-60, 1180, 840, 240); for (let x = -50; x < 780; x += 7 + R() * 8) C.dab(x, 1182, 0, 12, 2.4, hex('#7a5a3e'), 0.3 + R() * 0.2, 0, 0.4);
    bust(C, 96, 1200, 200, 200, { col: hex('#07050a'), hat: true }); bust(C, 604, 1210, 180, 190, { col: hex('#07050a'), wig: true }); C.blur(3); planes.pew = S.plane('pew', CD.pew, r, C.c); }
  for (const k in planes) planes[k].material.uniforms.uTint.value.set(0.55, 0.5, 0.52);
  // flames
  const flames = []; for (const [gk, G] of Object.entries(CAND)) G.pts.forEach(([x, y], i) => { const gm = S.glow(x, y, G.D, gk === 'chand' ? 46 : 44, { color: GLOW, core: 40 }, null); gm.renderOrder = 1e6 - G.D * 10 + 5; flames.push({ g: gm, grp: gk, i }); });
  const aura = S.glow(360, 300, CD.chand + 4, 1300, { color: [1.0, 0.55, 0.22], core: 5000 }); aura.renderOrder = 1e6 - CD.chand * 10 - 5;
  const rainR = rng(1399); const drops = WIN.map(([x0, y0, x1, y1]) => Array.from({ length: 22 }, () => ({ x: lerp(x0 + 6, x1 - 6, rainR()), y0: rainR() * 600, sp: 40 + rainR() * 90, w: 0.8 + rainR() })));
  const out = (sh) => (sh.candleOff || {}); const cOn = (t, off, grp, i) => { const t0 = off[grp + (grp === 'chand' ? i : '')]; if (t0 === undefined) return 1; if (t < t0) return 1; const u = (t - t0) / 0.4; return u >= 1 ? 0 : (1 - u) * (1 - u) * (1 + 0.3 * Math.sin(u * 14)); };
  const api = {
    key: 'court', S, planes, cams,
    show(v) { S.group.visible = v; },
    update(t, sh) {
      const off = out(sh); planes.judge.visible = sh.judge !== false; planes.jury.visible = sh.jury !== false; planes.lawyer.visible = sh.lawyer === true;
      const grpK = { chand: 0, bench: 0, table: 0, dock: 0 }, grpN = { chand: 0, bench: 0, table: 0, dock: 0 };
      for (const fl of flames) { const on = cOn(t, off, fl.grp, fl.i) * flick(t, fl.i + fl.grp.length * 3); fl.g.material.uniforms.uI.value = 1.1 * on; fl.g.visible = on > 0.01; grpK[fl.grp] += on; grpN[fl.grp]++; }
      for (const k in grpK) grpK[k] /= grpN[k];
      const wp = (gk) => { const G = CAND[gk]; const ps = G.pts; const x = ps.reduce((a, p) => a + p[0], 0) / ps.length, y = ps.reduce((a, p) => a + p[1], 0) / ps.length; return S.world(x, y, G.D); };
      const L = (D, d) => [{ p: wp('chand').setZ(-D + d), r: 5.5, c: WARM, k: 3.4 * grpK.chand }, { p: wp('bench').setZ(-D + d), r: 2.8, c: WARM, k: 2.6 * grpK.bench }, { p: wp('table').setZ(-D + d), r: 2.8, c: WARM, k: 2.6 * grpK.table }, { p: wp('dock').setZ(-D + d), r: 2.2, c: WARM, k: 2.8 * grpK.dock }];
      for (const [k, D] of [['wall', CD.wall], ['floor', CD.floor], ['bench', CD.bench], ['judge', CD.judge], ['jury', CD.jury], ['dock', CD.dock], ['table', CD.table], ['lawyer', CD.lawyer], ['chand', CD.chand], ['pew', CD.pew]]) setLights(planes[k].material, L(D, 3.5));
      aura.material.uniforms.uI.value = 0.06 * (0.4 + 0.6 * grpK.chand) * flick(t, 8);
      // window glow cools when it rains (the rain draws in draw())
    },
    draw(g, e) {
      const { t, sh, project } = e; if (!sh.rain) return; const k = sh.rain(t); if (k <= 0) return;
      WIN.forEach(([x0, y0, x1, y1], wi) => { const P = (x, y) => project(...S.world(x, y, CD.wall - 0.4).toArray()); g.save(); const a = P(x0, y0), b = P(x1, y1); g.beginPath(); g.rect(a[0], a[1] - 30, b[0] - a[0], b[1] - a[1] + 30); g.clip();
        for (const d of drops[wi]) { const y = y0 + ((d.y0 + t * d.sp) % (y1 - y0 + 20)); const q = P(d.x + Math.sin(y * 0.05 + d.y0) * 2, y); g.strokeStyle = `rgba(190,210,255,${(0.5 * k).toFixed(3)})`; g.lineWidth = d.w; g.lineCap = 'round'; g.beginPath(); g.moveTo(q[0], q[1] - 14); g.lineTo(q[0], q[1]); g.stroke(); g.fillStyle = `rgba(210,225,255,${(0.35 * k).toFixed(3)})`; g.beginPath(); g.arc(q[0], q[1], d.w * 1.4, 0, 6.3); g.fill(); }
        g.restore(); });
    },
  };
  S.group.visible = false; return api;
}
