// The lantern: the film's motif. One large ship's lantern over a blurred sea; the flame, the glass and the halo are drawn live
// so the light can swell, gutter and go out. Moods: night (o3), dusk (care), dawn (the last shot).
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, noise1 } from '/harness/kit/film.js';
import { Setup, setLights, DW, DH } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, paintSky, underpaint } from './paint.js';
import { WARM, GLOW, coverCams, flick } from './common.js';
import { MOODS, paintWater } from './sea.js';

const LD = { bg: 6000, lan: 10 };
const CX = 360, FLAME = [360, 650];
const PANES = [[[292, 442], [428, 442], [428, 760], [292, 760]], [[254, 440], [290, 442], [290, 760], [258, 758]], [[430, 442], [466, 440], [462, 758], [430, 760]]];

export function buildLantern(mood, shots) {
  const M = MOODS[{ night: 'moon', dusk: 'dusk', dawn: 'dawn' }[mood]]; const S = new Setup('lantern-' + mood, { pos: [0, 0, 0], mm: 35 }); const f = S.f; const cams = coverCams(shots, 'lantern:' + mood); const cover = (D, m) => S.cover(D, cams, m);
  const planes = {}; const horizon = 820;
  { const r = cover(LD.bg, 50); const C = new Canvas(r, { seed: 1501 + mood.length });
    const dy = horizon - 740; paintSky(C, { stops: M.sky.map(([y, c]) => [y + dy, hex(c)]), glow: { ...M.glow, y: M.glow.y + dy, col: hex(M.glow.col) }, clouds: M.clouds.map((c) => ({ ...c, y: c.y + dy * 0.5, col: hex(c.col), lit: hex(c.lit) })), n: 0.9 });
    const top0 = horizon; const rr = [r[0], top0 - 20, r[2], r[3]]; const W = new Canvas(rr, { seed: 1511 + mood.length }); paintWater(W, { top0, amp: 3, k: 1.6, fall: 380, c: M.water.mid, seed: 3, glit: { ...M.glit, w: 40, widen: 0.2 }, lit: M.glit.col, contrast: 0.7 });
    C.g.drawImage(W.c, (rr[0] - r[0]), (rr[1] - r[1])); C.blur(7); planes.bg = S.plane('bg', LD.bg, r, C.c); }
  { const r = [-60, -20, 780, 900]; const C = new Canvas(r, { seed: 1521 }); const g = C.g, R = C.R; const iron = hex('#0d0b10'), rim = hex(M.rim);
    // bracket arm and the chain to the handle ring
    g.strokeStyle = rgba(iron); g.lineCap = 'round'; g.lineWidth = 16; g.beginPath(); g.moveTo(-60, 40); g.bezierCurveTo(180, 20, 330, 60, 360, 250); g.stroke(); g.lineWidth = 10; g.beginPath(); g.moveTo(-60, 160); g.bezierCurveTo(120, 140, 260, 170, 330, 230); g.stroke();
    for (let k = 0; k < 6; k++) { g.lineWidth = 5; g.beginPath(); g.ellipse(360, 250 + k * 8, 7, 10, 0, 0, 6.3); g.stroke(); }
    for (let t = 0; t < 1; t += 0.03) { const x = lerp(-60, 330, t), y = 40 + 80 * Math.sin(t * 2.4) * (1 - t); C.dab(x, y - 8, 0.2, 22, 2, rim, 0.45, 0.05); }
    // cap (conical), handle ring, base plate
    const cap = new Path2D(); cap.moveTo(232, 440); cap.lineTo(360, 322); cap.lineTo(488, 440); cap.closePath(); underpaint(C, (x, y) => mixc(hex('#1a1520'), iron, smoothstep(250, 480, x)), cap, 5); const mc = C.mask((gg) => gg.fill(cap));
    C.strokes({ n: 140, mask: mc, color: () => mixc(hex('#1a1520'), iron, R()), angle: (x, y) => (x < 360 ? -0.8 : 0.8), len: [20, 60], wid: [4, 8], alpha: [0.4, 0.7], bend: 0.05 });
    for (let t = 0; t < 1; t += 0.04) C.dab(lerp(236, 356, t), lerp(438, 326, t), -0.84, 14, 2.2, rim, 0.55, 0.0);
    g.strokeStyle = rgba(iron); g.lineWidth = 11; g.beginPath(); g.arc(360, 304, 24, 0, Math.PI * 2); g.stroke(); C.dab(342, 290, -0.9, 20, 2.2, rim, 0.55, 0.05);
    g.fillStyle = rgba(iron); g.fillRect(238, 436, 244, 16); g.fillRect(244, 758, 232, 36); g.fillRect(262, 792, 196, 16);
    for (let x = 240; x < 480; x += 6) C.dab(x, 438, 0, 10, 2, rim, 0.45, 0, 0.3); for (let x = 246; x < 474; x += 6) C.dab(x, 760, 0, 10, 2, rim, 0.35, 0, 0.3);
    // glass panes (dark, reflecting a little sky) and the iron posts
    for (const P of PANES) { const p = new Path2D(); P.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y))); p.closePath(); g.fillStyle = rgba(mixc(hex('#10131e'), hex('#26304a'), 0.5)); g.fill(p); }
    g.strokeStyle = rgba(iron); g.lineWidth = 11; for (const x of [252, 291, 429, 468]) { g.beginPath(); g.moveTo(x + (x < 360 ? 4 : -4), 440); g.lineTo(x + (x < 360 ? 7 : -7), 760); g.stroke(); }
    for (const x of [250, 289, 427, 466]) C.dab(x + (x < 360 ? 1 : 6), 600, Math.PI / 2, 300, 2.4, rim, 0.4, 0, 0.2);
    // candle stub on the base, a cool reflection streak on the glass
    g.fillStyle = rgba(hex('#cdbd98')); g.fillRect(346, 700, 28, 62); C.dab(352, 730, Math.PI / 2, 50, 4, hex('#fff0cc'), 0.5, 0); g.fillStyle = rgba(hex('#171210')); g.fillRect(358, 684, 3, 18);
    C.mottle({ amt: 0.04, cell: 10 }); planes.lan = S.plane('lan', LD.lan, r, C.c); }
  const halo = S.glow(FLAME[0], FLAME[1], LD.lan + 0.5, 760, { color: [1.0, 0.55, 0.22], core: 5000 }, planes.lan); const g2 = S.glow(FLAME[0], FLAME[1], LD.lan + 0.4, 190, { color: GLOW, core: 30 }, planes.lan); const g3 = S.glow(FLAME[0], FLAME[1], LD.lan - 0.2, 70, { color: [1, 0.92, 0.7], core: 20 }, planes.lan);
  const api = {
    key: 'lantern:' + mood, S, planes, cams, mood,
    show(v) { S.group.visible = v; },
    update(t, sh) {
      const on = (sh.flame ? sh.flame(t) : 1); const fl = flick(t, 4) * on; const wp = S.world(FLAME[0], FLAME[1], LD.lan);
      for (const gm of [halo, g2, g3]) gm.position.copy(wp); halo.material.uniforms.uI.value = 0.2 * fl * (sh.haloK ?? 1); g2.material.uniforms.uI.value = 1.2 * fl; g3.material.uniforms.uI.value = 0.8 * on * flick(t, 6);
      planes.lan.material.uniforms.uTint.value.setScalar(1);
      setLights(planes.lan.material, [{ p: new THREE.Vector3(wp.x, wp.y, wp.z + 0.5), r: 1.2, c: WARM, k: 2.4 * fl }]);
      planes.bg.material.uniforms.uTint.value.setScalar(sh.bgK ? sh.bgK(t) : 1);
      planes.bg.userData.sx = 0; // the sea drifts slowly behind the glass
      planes.bg.position.x = planes.bg.userData.base.x + Math.sin(t * 0.25) * 2 * LD.bg / f;
    },
    draw(g, e) {
      const { t, sh, project } = e; const on = (sh.flame ? sh.flame(t) : 1); if (on < 0.01 && !(sh.smoke && sh.smoke(t) > 0)) return;
      const P = (x, y) => project(...S.world(x, y, LD.lan).toArray()); const fl = flick(t, 4) * on; const fc = P(FLAME[0], FLAME[1]); const sc = Math.abs(P(100, 0)[0] - P(0, 0)[0]) / 100;
      // glass lit from within
      for (const pane of PANES) { g.save(); g.beginPath(); pane.forEach(([x, y], i) => { const q = P(x, y); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); g.clip();
        const gr = g.createRadialGradient(fc[0], fc[1], 8 * sc, fc[0], fc[1], 230 * sc); gr.addColorStop(0, `rgba(255,236,190,${(0.95 * Math.min(1, fl)).toFixed(3)})`); gr.addColorStop(0.45, `rgba(255,178,92,${(0.78 * Math.min(1, fl)).toFixed(3)})`); gr.addColorStop(1, `rgba(236,120,52,${(0.55 * Math.min(1, fl)).toFixed(3)})`); g.fillStyle = gr; g.fillRect(0, 0, 1000, 1400); g.restore(); }
      // the flame: a teardrop that leans and breathes
      if (on > 0.01) { const sway = noise1(t * 2.2, 3) * 5 * sc + noise1(t * 5.1, 9) * 2 * sc; const h = (34 + 52 * Math.min(1.1, on) * (0.92 + 0.08 * Math.sin(t * 9))) * sc, w = (11 + 6 * Math.min(1, on)) * sc; const bx = fc[0] + 0, by = fc[1] + 44 * sc;
        const flame = (hh, ww, col, a) => { g.fillStyle = col; g.globalAlpha = a; g.beginPath(); g.moveTo(bx, by); g.bezierCurveTo(bx - ww * 1.2, by - hh * 0.35, bx - ww * 0.5 + sway * 0.3, by - hh * 0.8, bx + sway, by - hh); g.bezierCurveTo(bx + ww * 0.5 + sway * 0.3, by - hh * 0.8, bx + ww * 1.2, by - hh * 0.35, bx, by); g.fill(); g.globalAlpha = 1; };
        flame(h, w, 'rgb(255,168,64)', 0.95); flame(h * 0.78, w * 0.66, 'rgb(255,214,120)', 1); flame(h * 0.5, w * 0.36, 'rgb(255,248,226)', 1); }
      if (sh.smoke) { const k = sh.smoke(t); if (k > 0) { for (let i = 0; i < 9; i++) { const u = i / 9; const y = fc[1] + 10 * sc - k * 260 * sc * (0.3 + u * 0.7); const x = fc[0] + Math.sin(u * 5 + t * 1.4) * (10 + 40 * u) * sc; const a = 0.22 * (1 - u) * Math.min(1, k * 4) * (1 - smoothstep(0.7, 1, k)); g.fillStyle = `rgba(200,190,200,${a.toFixed(3)})`; g.beginPath(); g.ellipse(x, y, (9 + 22 * u) * sc, (8 + 14 * u) * sc, 0, 0, 6.3); g.fill(); } } }
    },
  };
  S.group.visible = false; return api;
}
