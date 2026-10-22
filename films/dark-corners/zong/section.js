// The ship in section, seen from astern: a hull, three decks, one lantern on a boom. Each small light is one person aboard:
// crew in cool white on the weather deck, captives in amber below. Only numbers, never bodies.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, rng, noise1 } from '/harness/kit/film.js';
import { Setup, setLights, DW, DH } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, paintSky, underpaint } from './paint.js';
import { WARM, GLOW, coverCams, flick, drawLantern, line } from './common.js';
import { MOODS, paintWater } from './sea.js';

const Y = { rail: 560, deck: 590, d1: 724, d2: 862, keel: 1012 };
const halfOuter = (y) => { const u = clamp((y - Y.rail) / (Y.keel - Y.rail)); return 232 * Math.sqrt(Math.max(0, 1 - Math.pow(u, 2.5))) + 6; };
const halfInner = (y) => Math.max(2, halfOuter(y) - 24);

export function buildSection(shots) {
  const M = MOODS.moon; const S = new Setup('section', { pos: [0, 0, 0], mm: 35 }); const f = S.f; const cams = coverCams(shots, 'section'); const cover = (D, m) => S.cover(D, cams, m); const planes = {};
  const DD = { hull: 50, mast: 40 };
  { const r = cover(9000, 40); const C = new Canvas(r, { seed: 1701 }); paintSky(C, { stops: M.sky.map(([y, c]) => [y + 200, hex(c)]), glow: { ...M.glow, x: 560, y: 260, col: hex(M.glow.col), a: 0.4 }, clouds: M.clouds.map((c) => ({ ...c, y: c.y + 100, col: hex(c.col), lit: hex(c.lit) })), n: 0.9 });
    for (let i = 0; i < 180; i++) C.dab(lerp(r[0], r[2], C.R()), lerp(r[1], 800, Math.pow(C.R(), 1.2)), 0, 2 + C.R() * 2, 1.4 + C.R(), [210, 222, 255], 0.3 + C.R() * 0.5, 0, 0.5);
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', 9000, r, C.c); }
  { const r0 = cover(900, 40); const top0 = 930; const r = [r0[0], top0 - 40, r0[2], r0[3]]; const C = new Canvas(r, { seed: 1711 }); paintWater(C, { top0, amp: 4, k: 1.2, fall: 380, c: M.water.mid, seed: 4, glit: { ...M.glit, x: 560, w: 20, widen: 0.1, a: 0.5 }, lit: M.glit.col, contrast: 0.7 }); planes.sea = S.plane('sea', 900, r, C.c); }
  // hull in section
  { const r = [60, 80, 660, 1060]; const C = new Canvas(r, { seed: 1721 }); const g = C.g, R = C.R, n = C.n; const iron = hex('#0b0d1a');
    const outer = new Path2D(), inner = new Path2D(); outer.moveTo(360 - halfOuter(Y.rail), Y.rail); inner.moveTo(360 - halfInner(Y.rail), Y.rail + 6);
    for (let y = Y.rail; y <= Y.keel; y += 4) { outer.lineTo(360 - halfOuter(y), y); inner.lineTo(360 - halfInner(y), Math.min(y + 6, Y.keel - 4)); }
    for (let y = Y.keel; y >= Y.rail; y -= 4) { outer.lineTo(360 + halfOuter(y), y); inner.lineTo(360 + halfInner(y), Math.min(y + 6, Y.keel - 4)); } outer.closePath(); inner.closePath();
    const colO = (x, y) => mixc(mixc(hex('#2b2c4a'), hex('#171a30'), smoothstep(150, 560, x)), hex('#0c0e1c'), smoothstep(Y.rail, Y.keel, y) * 0.5); underpaint(C, colO, outer, 6); const mo = C.mask((gg) => gg.fill(outer));
    C.strokes({ n: 700, mask: mo, color: colO, angle: (x, y) => { const dy = 6, dx = (halfOuter(y + dy) - halfOuter(y - dy)) / 12; return Math.atan2(1, (x < 360 ? -1 : 1) * dx * -1) + (R() - 0.5) * 0.1; }, len: [30, 90], wid: [5, 10], alpha: [0.4, 0.7], jv: 0.08, bend: 0.05 });
    for (let k = 0; k < 11; k++) { const off = 4 + k * 2.2; g.strokeStyle = rgba(hex('#07080f'), 0.5); g.lineWidth = 1.6; g.beginPath(); for (let y = Y.rail; y <= Y.keel; y += 6) { const x = 360 - (halfOuter(y) - off - k * 1.6); y === Y.rail ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke(); g.beginPath(); for (let y = Y.rail; y <= Y.keel; y += 6) { const x = 360 + (halfOuter(y) - off - k * 1.6); y === Y.rail ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke(); }
    // interior: dark volume, ribs, deck beams
    g.fillStyle = rgba(hex('#04050c')); g.fill(inner); g.save(); g.clip(inner);
    for (let y = Y.rail + 20; y < Y.keel; y += 22) { g.strokeStyle = rgba(hex('#0f1124'), 0.8); g.lineWidth = 2; g.beginPath(); g.moveTo(0, y); g.lineTo(720, y); g.stroke(); }
    g.restore();
    for (const y of [Y.deck, Y.d1, Y.d2]) { const hw = halfInner(y) + 8; g.fillStyle = rgba(hex('#262a48')); g.fillRect(360 - hw, y - 4, hw * 2, 9); for (let x = 360 - hw; x < 360 + hw; x += 5 + R() * 4) C.dab(x, y - 3.5, 0, 12 + R() * 10, 2.2, hex('#8fa6dc'), 0.4 + R() * 0.3, 0, 0.4); }
    // rails and the top edge: moon rim
    for (const sd of [-1, 1]) { g.fillStyle = rgba(hex('#1a1d36')); g.fillRect(360 + sd * 232 - 7, Y.rail - 22, 14, 46); for (let k = 0; k < 8; k++) C.dab(360 + sd * 232 - 5 + k * 1.2 * sd, Y.rail - 20 + k * 6, Math.PI / 2, 8, 1.6, hex('#8fa6dc'), 0.5, 0); }
    for (let y = Y.rail; y < Y.keel; y += 4 + R() * 4) { for (const sd of [-1, 1]) C.dab(360 + sd * (halfOuter(y) - 1.5), y, Math.PI / 2 - sd * 0.25, 8 + R() * 10, 1.8, hex('#8fa6dc'), sd < 0 ? 0.5 : 0.25, 0.04); }
    C.mottle({ amt: 0.05 }); planes.hull = S.plane('hull', DD.hull, r, C.c); }
  // mast, yards, shrouds, boom (thin, in front)
  { const r = [60, 100, 660, 640]; const C = new Canvas(r, { seed: 1731 }); const g = C.g, R = C.R; const iron = hex('#0b0d1a');
    g.fillStyle = rgba(iron); g.fillRect(352, 150, 16, 440); for (const [y, w] of [[212, 300], [330, 360], [452, 420]]) { g.fillRect(360 - w / 2, y - 4, w, 8); for (let x = 360 - w / 2; x < 360 + w / 2; x += 6 + R() * 5) C.dab(x, y - 3.5, 0, 12, 2, hex('#8fa6dc'), 0.4, 0, 0.3); }
    for (const sd of [-1, 1]) for (let k = 0; k < 4; k++) { g.strokeStyle = rgba(iron, 0.85); g.lineWidth = 2; g.beginPath(); g.moveTo(360 + sd * 6, 260 + k * 10); g.lineTo(360 + sd * (232 - 8 + k * 0), 560 - k * 2); g.stroke(); }
    C.dab(354, 360, Math.PI / 2, 420, 2.6, hex('#8fa6dc'), 0.45, 0, 0.1);
    g.strokeStyle = rgba(iron); g.lineWidth = 8; g.lineCap = 'round'; g.beginPath(); g.moveTo(366, 470); g.lineTo(486, 470); g.stroke(); g.lineWidth = 5; g.beginPath(); g.moveTo(366, 520); g.lineTo(470, 474); g.stroke();
    C.blur(0.6); planes.mast = S.plane('mast', DD.mast, r, C.c); }
  // dots: capacity by level, shuffled reveal order
  const R = rng(1741); const cells = []; const levels = [[Y.deck + 22, Y.d1 - 12], [Y.d1 + 16, Y.d2 - 12], [Y.d2 + 16, Y.keel - 22]];
  levels.forEach(([ya, yb], li) => { for (let y = ya; y <= yb; y += 13) { const hw = halfInner(y) - 14; if (hw < 12) continue; for (let x = 360 - hw; x <= 360 + hw; x += 11) cells.push([x + (R() - 0.5) * 2.5, y + (R() - 0.5) * 2.5]); } });
  const order = cells.map((c, i) => [R(), i]).sort((a, b) => a[0] - b[0]).map((a) => a[1]).slice(0, 440); const dots = order.map((ci, i) => ({ x: cells[ci][0], y: cells[ci][1], ph: R() * 6.3, i }));
  const crew = Array.from({ length: 17 }, (_, i) => ({ x: 360 - 200 + i * 25 + (R() - 0.5) * 6, y: Y.deck - 12, i, ph: R() * 6.3 }));
  for (const k of ['hull', 'mast']) planes[k].material.uniforms.uTint.value.set(1, 1, 1);
  const moon = S.glow(560, 260, 8500, 190, { color: [0.62, 0.74, 1.0], core: 40 }, planes.sky); moon.material.uniforms.uI.value = 0.9;
  const lg = S.glow(486, 508, DD.mast, 150, { color: GLOW, core: 40 }, planes.mast); const lg2 = S.glow(486, 508, DD.mast, 54, { color: [1, 0.86, 0.6], core: 30 }, planes.mast); const aura = S.glow(486, 520, DD.mast, 900, { color: [1, 0.55, 0.22], core: 5000 }, planes.mast);
  const api = {
    key: 'section', S, planes, cams, show(v) { S.group.visible = v; },
    update(t, sh) { const p = planes.sea; p.position.x = p.userData.base.x + (Math.sin(t * 0.3) * 4 + t * 0.4) * 900 / f; const fl = flick(t, 5); const lw = S.world(486, 508, DD.mast); lg.position.copy(lw); lg2.position.copy(lw); aura.position.copy(lw); lg.material.uniforms.uI.value = 1.0 * fl; lg2.material.uniforms.uI.value = 0.85 * fl; aura.material.uniforms.uI.value = 0.06 * fl;
      for (const k of ['hull']) setLights(planes[k].material, [{ p: new THREE.Vector3(lw.x, lw.y, lw.z + 1.4), r: 2.4, c: WARM, k: 2.2 * fl }]); setLights(planes.mast.material, [{ p: new THREE.Vector3(lw.x, lw.y, lw.z + 1.0), r: 1.6, c: WARM, k: 2.2 * fl }]); },
    draw(g, e) {
      const { t, sh, project } = e; const P = (x, y) => project(...S.world(x, y, DD.hull).toArray()); const sc = Math.abs(P(100, 0)[0] - P(0, 0)[0]) / 100;
      const sw = Math.sin(t * 1.1) * 0.12; const lq = P(486 + Math.sin(sw) * 30, 482 + 36 * Math.cos(sw)); const hk = P(486, 478); line(g, hk, [lq[0], lq[1] - 18 * sc], 2 * sc, hex('#0a0a12'), 0.95); drawLantern(g, lq[0], lq[1] + 8 * sc, 40 * sc, 1.0 * flick(t, 5), sw * 0.5);
      const d = sh.dots ? sh.dots(t) : { crew: 0, cap: 0, dim: 0, keep: 440, fade: 0 };
      for (const c of crew) { const a = clamp(d.crew - c.i); if (a <= 0.01) continue; const q = P(c.x, c.y); const tw = 0.85 + 0.15 * Math.sin(t * 1.7 + c.ph); g.fillStyle = `rgba(220,232,255,${(0.2 * a * tw).toFixed(3)})`; g.beginPath(); g.arc(q[0], q[1], 7 * sc, 0, 6.3); g.fill(); g.fillStyle = `rgba(236,244,255,${(0.95 * a * tw).toFixed(3)})`; g.beginPath(); g.arc(q[0], q[1], 3.2 * sc, 0, 6.3); g.fill(); }
      for (const dt of dots) { let a = clamp((d.cap - dt.i) / 5); if (a <= 0.01) continue; if (dt.i >= d.keep) a *= 1 - d.fade; if (a <= 0.01) continue; if (dt.i % 2 === 1) a *= 1 - 0.72 * d.dim; const q = P(dt.x, dt.y); const tw = 0.8 + 0.2 * Math.sin(t * (1.1 + (dt.i % 5) * 0.2) + dt.ph);
        g.fillStyle = `rgba(255,150,60,${(0.17 * a * tw).toFixed(3)})`; g.beginPath(); g.arc(q[0], q[1], 6.2 * sc, 0, 6.3); g.fill(); g.fillStyle = `rgba(255,206,128,${(0.95 * a * tw).toFixed(3)})`; g.beginPath(); g.arc(q[0], q[1], 2.7 * sc, 0, 6.3); g.fill(); }
    },
  };
  S.group.visible = false; return api;
}
