// A London lane at night: Equiano walks with a lamp, Granville Sharp meets him, a letter passes; a lit window where Sharp writes.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, rng, noise1 } from '/harness/kit/film.js';
import { Setup, setLights, DW, DH } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, paintSky, underpaint } from './paint.js';
import { WARM, GLOW, coverCams, flick, drawLantern, line, paintPerson } from './common.js';

const SD = { sky: 9000, far: 420, mid: 150, wall: 70, win: 69, ground: 46, fig: 42, lamp: 52 };
const GROUND = 960, VP = [360, 640];
const WINW = [34, 470, 196, 690]; // the lit window (design px on the left wall)
const LAMP = { x: 468, y: 470, px: 560, py: 410 };

function facade(C, x0, x1, yTop, yBot, side, seed, lit) {
  const g = C.g, R = C.R, n = C.n; const brick = (x, y) => mixc(mixc(hex('#241a22'), hex('#160f19'), smoothstep(yTop, yBot, y)), hex('#2b2028'), n.fbm(x * 0.03, y * 0.03, 3) * 0.5);
  const path = new Path2D(); path.rect(x0, yTop, x1 - x0, yBot - yTop); underpaint(C, brick, path, 6); const m = C.mask((gg) => gg.fill(path));
  C.strokes({ n: (x1 - x0) * (yBot - yTop) / 420, mask: m, color: brick, angle: () => (R() - 0.5) * 0.3, len: [12, 40], wid: [3, 6], alpha: [0.35, 0.6], jv: 0.1 });
  for (let y = yTop; y < yBot; y += 14) for (let x = x0; x < x1; x += 22 + R() * 16) C.dab(x + R() * 6, y + R() * 3, (R() - 0.5) * 0.05, 14 + R() * 14, 1.4, hex('#0a0710'), 0.4, 0, 0.5);
  // timber beams (jetty floors) and windows
  const floors = []; for (let y = yTop + 120; y < yBot - 60; y += 150 + R() * 20) floors.push(y);
  for (const y of floors) { g.fillStyle = rgba(hex('#120c10')); g.fillRect(x0, y - 8, x1 - x0, 16); for (let x = x0; x < x1; x += 6 + R() * 6) C.dab(x, y - 7, 0, 12 + R() * 10, 2, hex('#6a5a66'), 0.28, 0, 0.4); }
  const wins = []; const cols = Math.max(1, Math.floor((x1 - x0) / 80));
  floors.concat([yBot - 140]).forEach((fy, fi) => { for (let c = 0; c < cols; c++) { const cx = x0 + (c + 0.5) * (x1 - x0) / cols + (R() - 0.5) * 6, wy = fy - 118, ww = 38, wh = 60; if (wy < yTop + 10) continue;
    const on = R() < lit; g.fillStyle = rgba(hex('#07050c')); g.fillRect(cx - ww / 2 - 4, wy - 4, ww + 8, wh + 8); g.fillStyle = rgba(on ? hex('#6b3d22') : hex('#0e1222')); g.fillRect(cx - ww / 2, wy, ww, wh);
    g.strokeStyle = rgba(hex('#07050c')); g.lineWidth = 3; g.beginPath(); g.moveTo(cx, wy); g.lineTo(cx, wy + wh); g.moveTo(cx - ww / 2, wy + wh / 2); g.lineTo(cx + ww / 2, wy + wh / 2); g.stroke(); C.dab(cx - ww / 2 - 3, wy + wh / 2, Math.PI / 2, wh + 6, 1.8, hex('#8fa6dc'), 0.3, 0, 0.2); if (on) wins.push([cx, wy + wh / 2, ww, wh]); } });
  for (let x = x0; x < x1; x += 4 + R() * 5) C.dab(x, yTop + 1, 0, 12 + R() * 12, 2.4, hex('#8fa6dc'), 0.25 + R() * 0.2, 0, 0.5);
  return wins;
}

export function buildStreet(shots) {
  const S = new Setup('street', { pos: [0, 0, 0], mm: 35 }); const f = S.f; const cams = coverCams(shots, 'street'); const cover = (D, m) => S.cover(D, cams, m); const planes = {}; const wglow = [];
  { const r = cover(SD.sky, 40); const C = new Canvas(r, { seed: 1801 }); paintSky(C, { stops: [[-300, hex('#04060e')], [150, hex('#0a1022')], [420, hex('#1a1f3a')], [640, hex('#3a3040')], [800, hex('#5a4448')]], glow: { x: 360, y: 760, rx: 520, ry: 260, col: hex('#9a6a52'), a: 0.5 },
      clouds: [{ y: 200, h: 26, x0: -300, x1: 1100, col: hex('#0a0f20'), lit: hex('#2a3052'), litA: 0.5, sy: 0.02 }, { y: 420, h: 22, x0: -300, x1: 1100, col: hex('#1a1f3a'), lit: hex('#6a4a4a'), litA: 0.6, sy: 0.028, thr: 0.5 }], n: 0.9 }); C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', SD.sky, r, C.c); }
  // far skyline with a spire
  { const r = cover(SD.far, 60); const C = new Canvas(r, { seed: 1811 }); const g = C.g, R = C.R; const base = 700;
    for (let x = r[0]; x < r[2]; x += 36 + R() * 40) { const w = 40 + R() * 70, h = 60 + R() * 130; g.fillStyle = rgba(mixc(hex('#171322'), hex('#0e0b17'), R())); g.fillRect(x, base - h, w, h + 60); g.beginPath(); g.moveTo(x - 3, base - h); g.lineTo(x + w / 2, base - h - 22 - R() * 22); g.lineTo(x + w + 3, base - h); g.fill();
      for (let k = 0; k < 4; k++) if (R() < 0.35) { g.fillStyle = rgba(hex('#7a4a2a'), 0.9); g.fillRect(x + 6 + R() * (w - 18), base - h + 14 + R() * (h - 30), 5, 8); } if (R() < 0.3) g.fillRect(x + w * 0.7, base - h - 38, 8, 20); }
    g.fillStyle = rgba(hex('#0e0b17')); g.beginPath(); g.moveTo(560, base - 40); g.lineTo(572, base - 330); g.lineTo(584, base - 40); g.fill(); g.fillRect(552, base - 160, 40, 130);
    C.mottle({ amt: 0.05 }); C.blur(0.9); planes.far = S.plane('far', SD.far, r, C.c); }
  // mid pair of facades further down the lane
  { const r = cover(SD.mid, 40); const C = new Canvas(r, { seed: 1821 }); facade(C, 150, 330, 300, 760, -1, 1, 0.45); facade(C, 400, 570, 340, 760, 1, 2, 0.45); C.mottle({ amt: 0.05 }); planes.mid = S.plane('mid', SD.mid, r, C.c); }
  // near walls, left and right (the left one carries the study window)
  let wins = [];
  { const r = cover(SD.wall, 60); const C = new Canvas(r, { seed: 1831 }); const a = facade(C, r[0] - 40, 214, -100, 1100, -1, 3, 0.3); const b = facade(C, 506, r[2] + 40, -100, 1100, 1, 4, 0.3); wins = [...a, ...b];
    const g = C.g; const [wx0, wy0, wx1, wy1] = WINW; g.fillStyle = rgba(hex('#07050c')); g.fillRect(wx0 - 8, wy0 - 8, wx1 - wx0 + 16, wy1 - wy0 + 16); g.fillStyle = rgba(hex('#201208')); g.fillRect(wx0, wy0, wx1 - wx0, wy1 - wy0);
    C.mottle({ amt: 0.05 }); planes.wall = S.plane('wall', SD.wall, r, C.c); }
  // the study inside the window: warm room, a desk, a seated figure writing, a candle (painted at 2x so it survives the push-in)
  { const [wx0, wy0, wx1, wy1] = WINW; const r = [wx0, wy0, wx1, wy1]; const C = new Canvas(r, { seed: 1841, q: 2.4 }); const g = C.g, R = C.R;
    const gr = g.createLinearGradient(0, wy0, 0, wy1); gr.addColorStop(0, rgba(hex('#7a4a28'))); gr.addColorStop(1, rgba(hex('#3a200f'))); g.fillStyle = gr; g.fillRect(wx0, wy0, wx1 - wx0, wy1 - wy0);
    C.strokes({ n: 140, color: () => mixc(hex('#8a5a30'), hex('#4a2a14'), R()), angle: () => (R() - 0.5) * 0.4, len: [10, 30], wid: [3, 6], alpha: [0.3, 0.55] });
    g.fillStyle = rgba(hex('#1a0e08')); g.fillRect(wx0, wy1 - 70, wx1 - wx0, 70); for (let x = wx0; x < wx1; x += 4 + R() * 4) C.dab(x, wy1 - 69, 0, 8 + R() * 8, 1.6, hex('#c08850'), 0.5, 0, 0.4);
    // Sharp seen from the side at his desk: head bent, wig, a coat; the quill arm is drawn live
    const sx = 100, sy = wy1 - 62; g.fillStyle = rgba(hex('#0b0810')); g.beginPath(); g.moveTo(sx - 42, wy1); g.quadraticCurveTo(sx - 46, sy - 42, sx - 16, sy - 56); g.lineTo(sx + 10, sy - 58); g.quadraticCurveTo(sx + 34, sy - 40, sx + 36, wy1); g.closePath(); g.fill();
    g.beginPath(); g.ellipse(sx + 6, sy - 76, 13, 15, 0.2, 0, 6.3); g.fill(); g.beginPath(); g.ellipse(sx + 2, sy - 82, 17, 17, 0, 0, 6.3); g.fill(); g.beginPath(); g.ellipse(sx - 14, sy - 66, 8, 11, 0, 0, 6.3); g.fill();
    for (let k = 0; k < 9; k++) C.dab(sx + 20, sy - 84 + k * 3, Math.PI / 2, 12, 1.4, hex('#e8a868'), 0.55, 0.03);
    g.fillStyle = rgba(hex('#2a1810')); g.fillRect(wx0, wy1 - 48, wx1 - wx0, 8); for (let x = wx0; x < wx1; x += 5) C.dab(x, wy1 - 49, 0, 10, 1.4, hex('#d09860'), 0.5, 0, 0.4);
    g.fillStyle = rgba(hex('#dcc89a')); g.beginPath(); g.moveTo(sx + 34, wy1 - 49); g.lineTo(sx + 78, wy1 - 49); g.lineTo(sx + 84, wy1 - 42); g.lineTo(sx + 30, wy1 - 42); g.closePath(); g.fill();
    g.fillStyle = rgba(hex('#dcc89a')); g.fillRect(wx1 - 44, wy1 - 62, 8, 14); g.fillStyle = rgba(hex('#171008')); g.fillRect(wx1 - 41, wy1 - 68, 2, 6);
    g.strokeStyle = rgba(hex('#0b0810')); g.lineWidth = 6; g.beginPath(); g.moveTo(wx0 + (wx1 - wx0) / 2, wy0); g.lineTo(wx0 + (wx1 - wx0) / 2, wy1); g.moveTo(wx0, wy0 + (wy1 - wy0) * 0.35); g.lineTo(wx1, wy0 + (wy1 - wy0) * 0.35); g.stroke(); g.lineWidth = 9; g.strokeRect(wx0 + 1, wy0 + 1, wx1 - wx0 - 2, wy1 - wy0 - 2);
    planes.study = S.plane('study', SD.win, r, C.c); }
  // ground: wet cobbles
  { const r = cover(SD.ground, 60); const C = new Canvas(r, { seed: 1851 }); const R = C.R, n = C.n; const [x0, y0, x1, y1] = r; const gp = new Path2D(); gp.rect(x0 - 10, 730, x1 - x0 + 20, y1 - 730 + 10); const gm = C.mask((gg) => gg.fill(gp));
    underpaint(C, (x, y) => mixc(hex('#1c1a2a'), hex('#0a0910'), smoothstep(730, y1, y)), gp, 10); C.strokes({ n: C.area / 700, mask: gm, color: (x, y) => mixc(hex('#2a2638'), hex('#0c0b14'), R()), angle: () => (R() - 0.5) * 0.4, len: [10, 40], wid: [4, 9], alpha: [0.35, 0.6], jv: 0.1 });
    for (let k = -8; k <= 8; k++) { const xb = 360 + k * 150; for (let s = 0; s < 1; s += 0.025) { const y = lerp(740, y1, s); const x = lerp(VP[0] + (xb - VP[0]) * (740 - VP[1]) / (y1 - VP[1]), xb, s); C.dab(x, y, Math.atan2(y1 - VP[1], xb - VP[0]), 12 + s * 36, 1.2 + s * 2, hex('#050409'), 0.6, 0.02, 0.4); } }
    for (let y = 750; y < y1; y += 22) for (let x = x0; x < x1; x += 20 + R() * 20) C.dab(x + R() * 8, y + R() * 5, (R() - 0.5) * 0.1, 8 + (y - 740) * 0.05, 2 + (y - 740) * 0.004, mixc(hex('#3a3450'), hex('#141220'), R()), 0.5, 0, 0.5);
    C.mottle({ amt: 0.05 }); planes.ground = S.plane('ground', SD.ground, r, C.c); }
  // figures: Equiano (bare head, coat, a letter in one hand, a hand lamp in the other) and Sharp (tricorn, cane)
  const EQ = { x: 330, yb: GROUND, h: 340 }, SH = { x: 506, yb: GROUND, h: 350 }; const uE = EQ.h / 100, uS = SH.h / 100;
  const hand = (F, u, hx, hy) => [F.x + hx * u, F.yb - 79 * u + hy * u];
  { const r = [EQ.x - 150, EQ.yb - 400, EQ.x + 190, EQ.yb + 12]; const C = new Canvas(r, { seed: 1861, q: 1.6 });
    paintPerson(C, { x: EQ.x, yb: EQ.yb, h: EQ.h, face: 1, hat: 'none', coat: 0.92, flare: 1.15, shoulder: 17, stride: 3, col: hex('#0d0b16'), arms: [{ s: [13, 3], e: [24, 20], h: [38, 17] }, { s: [-13, 3], e: [-22, 20], h: [-24, 40] }] });
    planes.eq = S.plane('eq', SD.fig, r, C.c); planes.eq.userData.F = EQ; }
  { const r = [SH.x - 190, SH.yb - 410, SH.x + 150, SH.yb + 12]; const C = new Canvas(r, { seed: 1871, q: 1.6 }); const g = C.g;
    paintPerson(C, { x: SH.x, yb: SH.yb, h: SH.h, face: -1, hat: 'tricorn', coat: 0.95, flare: 1.3, shoulder: 18, col: hex('#0e0c17'), arms: [{ s: [-13, 3], e: [-26, 17], h: [-40, 14] }, { s: [13, 3], e: [18, 26], h: [22, 50] }] });
    g.strokeStyle = rgba(hex('#0e0c17')); g.lineWidth = 6; g.lineCap = 'round'; const hp = hand(SH, uS, 22, 50); g.beginPath(); g.moveTo(hp[0] + 2, hp[1] - 36); g.lineTo(hp[0] + 8, SH.yb); g.stroke(); C.dab(hp[0] - 1, hp[1] + 60, Math.PI / 2, 120, 1.6, hex('#ffb870'), 0.45, 0);
    planes.sh = S.plane('sh', SD.fig, r, C.c); planes.sh.userData.F = SH; }
  for (const k of ['far', 'mid', 'wall', 'ground', 'eq', 'sh']) planes[k].material.uniforms.uTint.value.set(1, 1, 1);
  // lights: the street lamp on the right wall, Equiano's hand lamp, window glows, the study candle
  const lampG = S.glow(LAMP.x, LAMP.y, SD.lamp, 170, { color: GLOW, core: 40 }); lampG.renderOrder = 1e6 - SD.lamp * 10 + 5; const lampA = S.glow(LAMP.x, LAMP.y + 30, SD.lamp, 1000, { color: [1, 0.55, 0.22], core: 5000 }); lampA.renderOrder = 1e6 - SD.lamp * 10 - 0.5;
  const handG = S.glow(0, 0, SD.fig - 0.5, 120, { color: GLOW, core: 40 }); const handA = S.glow(0, 0, SD.fig - 0.5, 700, { color: [1, 0.55, 0.22], core: 5000 }); handG.renderOrder = 1e6 - SD.fig * 10 + 5; handA.renderOrder = 1e6 - SD.fig * 10 - 0.4;
  const studyG = S.glow(WINW[0] + 96, WINW[1] + 130, SD.win - 0.3, 300, { color: [1, 0.62, 0.3], core: 5000 }, planes.study); const candleG = S.glow(WINW[2] - 40, WINW[3] - 60, SD.win - 0.2, 50, { color: GLOW, core: 30 }, planes.study);
  const winGl = wins.slice(0, 14).map(([x, y, w, h]) => { const g = S.glow(x, y, SD.wall - 0.2, Math.max(w, h) * 3.2, { color: [1.0, 0.55, 0.24], shape: 1, rect: [w / (Math.max(w, h) * 3.2), h / (Math.max(w, h) * 3.2)] }, planes.wall); return g; });
  const api = {
    key: 'street', S, planes, cams, show(v) { S.group.visible = v; },
    update(t, sh) {
      const fl = flick(t, 7); const lw = S.world(LAMP.x, LAMP.y, SD.lamp); lampG.position.copy(lw); lampA.position.copy(lw); lampG.material.uniforms.uI.value = 1.2 * fl; lampA.material.uniforms.uI.value = 0.06 * fl;
      const ex = sh.eqX ? sh.eqX(t) : 0, shx = sh.shX ? sh.shX(t) : 0; planes.eq.visible = sh.eq !== false; planes.sh.visible = sh.sh !== false;
      planes.eq.position.x = planes.eq.userData.base.x + ex * SD.fig / f; planes.sh.position.x = planes.sh.userData.base.x + shx * SD.fig / f; planes.eq.position.y = planes.eq.userData.base.y + Math.sin(t * 2.2) * 1.6 * SD.fig / f; 
      const hp = hand(EQ, uE, -24, 40); const hw = S.world(hp[0] + ex, hp[1], SD.fig); handG.position.copy(hw); handA.position.copy(hw); const hl = sh.handLamp === false ? 0 : 1; handG.visible = handA.visible = hl > 0; handG.material.uniforms.uI.value = 1.0 * fl * hl; handA.material.uniforms.uI.value = 0.055 * fl * hl;
      studyG.material.uniforms.uI.value = 0.07 * fl; candleG.material.uniforms.uI.value = 1.0 * fl; winGl.forEach((g, i) => { g.material.uniforms.uI.value = 0.9 * flick(t, 40 + i); });
      const L = (D) => [{ p: new THREE.Vector3(lw.x, lw.y, -D + 3.2), r: 3.6, c: WARM, k: 3.0 * fl }, { p: new THREE.Vector3(hw.x, hw.y, -D + 2.0), r: 2.0, c: WARM, k: (sh.handLamp === false ? 0 : 3.2) * fl }];
      for (const k of ['far', 'mid', 'wall', 'ground', 'eq', 'sh']) setLights(planes[k].material, L({ far: SD.far, mid: SD.mid, wall: SD.wall, ground: SD.ground, eq: SD.fig, sh: SD.fig }[k]));
    },
    draw(g, e) {
      const { t, sh, project } = e; const P = (x, y, D) => project(...S.world(x, y, D).toArray()); const sc = Math.abs(P(100, 0, SD.fig)[0] - P(0, 0, SD.fig)[0]) / 100; const fl = flick(t, 7);
      const ex = sh.eqX ? sh.eqX(t) : 0, shx = sh.shX ? sh.shX(t) : 0;
      // street lamp on its bracket
      const lb = P(LAMP.px, LAMP.py, SD.lamp), lp = P(LAMP.x, LAMP.y - 28, SD.lamp); const sc2 = Math.abs(P(100, 0, SD.lamp)[0] - P(0, 0, SD.lamp)[0]) / 100; line(g, lb, P(LAMP.x + 28, LAMP.y - 62, SD.lamp), 5 * sc2, hex('#0a0810')); line(g, P(LAMP.x + 28, LAMP.y - 62, SD.lamp), lp, 2.2 * sc2, hex('#0a0810')); const sw = Math.sin(t * 0.9) * 0.05; drawLantern(g, P(LAMP.x, LAMP.y, SD.lamp)[0], P(LAMP.x, LAMP.y, SD.lamp)[1], 62 * sc2, 1.0 * fl, sw);
      // hand lamp
      if (sh.handLamp !== false && sh.eq !== false) { const hp = hand(EQ, uE, -24, 40); const q = P(hp[0] + ex, hp[1] + 28, SD.fig); const swing = Math.sin(t * 2.0) * 0.1; line(g, P(hp[0] + ex, hp[1], SD.fig), q, 2 * sc, hex('#0a0810')); drawLantern(g, q[0], q[1] + 28 * sc, 50 * sc, 1.0 * fl, swing); }
      // the letter: in Equiano's hand, then across to Sharp's
      if (sh.letter) { const k = sh.letter(t); const a = hand(EQ, uE, 38, 17), b = hand(SH, uS, -40, 14); const ax = a[0] + ex, bx = b[0] + shx; const x = lerp(ax, bx, ease.inOutSine(k.k)) , y = lerp(a[1], b[1], ease.inOutSine(k.k)) - Math.sin(Math.PI * k.k) * 10; const q = P(x, y, SD.fig); const w = 30 * sc, h2 = 20 * sc;
        g.save(); g.translate(q[0], q[1]); g.rotate(-0.25 + k.k * 0.3); g.fillStyle = 'rgba(232,214,170,0.96)'; g.fillRect(-w / 2, -h2 / 2, w, h2); g.strokeStyle = 'rgba(80,60,36,0.7)'; g.lineWidth = 1.2 * sc; g.beginPath(); g.moveTo(-w / 2, -h2 / 2); g.lineTo(0, 1 * sc); g.lineTo(w / 2, -h2 / 2); g.stroke(); g.fillStyle = 'rgba(150,36,28,0.9)'; g.beginPath(); g.arc(0, 1 * sc, 2.2 * sc, 0, 6.3); g.fill(); g.restore(); }
      // Sharp's quill arm in the window: a small live stroke across the page
      if (sh.writing) { const [wx0, wy0, wx1, wy1] = WINW; const sx = 100, sy = wy1 - 62; const wob = Math.sin(t * 5.2) * 3 + Math.sin(t * 2.3) * 3; const hnd = P(sx + 46 + wob, wy1 - 56 + Math.sin(t * 7) * 0.8, SD.win); const tip = P(sx + 58 + wob * 1.4, wy1 - 47, SD.win); const sw2 = Math.abs(P(100, 0, SD.win)[0] - P(0, 0, SD.win)[0]) / 100;
        g.strokeStyle = rgba(hex('#0b0810')); g.lineWidth = 7 * sw2; g.lineCap = 'round'; g.beginPath(); g.moveTo(P(sx + 18, sy - 40, SD.win)[0], P(sx + 18, sy - 40, SD.win)[1]); g.lineTo(hnd[0], hnd[1]); g.stroke(); g.strokeStyle = 'rgba(236,222,190,0.95)'; g.lineWidth = 2.2 * sw2; g.beginPath(); g.moveTo(hnd[0], hnd[1]); g.lineTo(hnd[0] + 22 * sw2, hnd[1] - 40 * sw2); g.stroke(); g.strokeStyle = 'rgba(30,20,12,0.9)'; g.lineWidth = 1.4 * sw2; g.beginPath(); g.moveTo(hnd[0], hnd[1]); g.lineTo(tip[0], tip[1]); g.stroke(); }
    },
  };
  S.group.visible = false; return api;
}
