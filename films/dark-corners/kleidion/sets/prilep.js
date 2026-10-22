// SET prilep: Samuel's fortress at Prilep. From the rampart (dusk): the plain below, the long road, a line of lanterns coming slowly.
// From the plain (dawn): the keep and a single window that is lit, then dark. Samuel is a crowned silhouette on the parapet.
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, fireFlick, tintAll, spline, ribbonPath, paintCliff } from './common.js';
import { paintSky, paintRange, pineTree, paintFog, paintTufts, paintRocks } from '../paint.js';
import { person, glowAt, embers, hash1, PAL } from '../figs.js';
import { birds, smoke, motes, hazeBand } from '../ambient.js';
import { horizonGlow } from './light.js';

const ROAD = spline([{ x: 440, y: 612 }, { x: 400, y: 640 }, { x: 330, y: 690 }, { x: 290, y: 760 }, { x: 350, y: 850 }, { x: 420, y: 960 }, { x: 330, y: 1100 }, { x: 250, y: 1300 }], 12);
export default function prilep(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, far: 2200, plain: 700, keep: 380, ramp: 95, fg: 48 }; const planes = {};
  const skies = { dusk: { stops: [[-500, '#0d0f30'], [0, '#1a1c4c'], [300, '#3a2f66'], [480, '#7a4a6e'], [580, '#d88a6a'], [640, '#f3b27a']], glow: { x: 250, y: 630, rx: 560, ry: 120, col: '#ffc08a', a: 0.55 } },
    dawn: { stops: [[-500, '#243060'], [0, '#3a4880'], [300, '#7a78a8'], [480, '#d8a0a0'], [580, '#f6c8a0'], [640, '#fde0b0']], glow: { x: 360, y: 640, rx: 620, ry: 130, col: '#ffe0b0', a: 0.6 } } };
  for (const k of Object.keys(skies)) { const o = skies[k]; const r = cover(D.sky); const C = new Canvas(r, { seed: k === 'dusk' ? 1311 : 1312 });
    paintSky(C, { stops: o.stops.map(([y, c]) => [y, hex(c)]), glow: { ...o.glow, col: hex(o.glow.col) }, clouds: [{ y: 220, h: 12, x0: -300, x1: 1000, col: hex(k === 'dusk' ? '#2a2058' : '#6a6a9a'), lit: hex(k === 'dusk' ? '#c87a7a' : '#f4b890'), litA: 0.7, sy: 0.03 }, { y: 430, h: 10, x0: -100, x1: 1000, col: hex(k === 'dusk' ? '#4a3066' : '#9a8aa8'), lit: hex(k === 'dusk' ? '#f0a478' : '#ffd8a8'), litA: 0.8, thr: 0.5, sy: 0.04 }] });
    if (k === 'dusk') { const R = rng(13111); for (let i = 0; i < 70; i++) { const x = lerp(r[0], r[2], R()), y = lerp(r[1], 380, R()); C.g.fillStyle = rgba([220, 225, 255], 0.2 + R() * 0.5); C.g.beginPath(); C.g.arc(x, y, 0.5 + R(), 0, 7); C.g.fill(); } }
    horizonGlow(C, { y: 636, x0: r[0], x1: r[2], h: 150, col: k === 'dusk' ? [255, 170, 120] : [255, 215, 160], a: 0.55, streaks: 6, seed: 5 });
    C.mottle({ amt: 0.05 }); planes['sky_' + k] = S.plane('sky_' + k, D.sky, r, C.c); }
  { const r = cover(D.far); r[1] = Math.max(r[1], 300); r[3] = Math.min(r[3], 700); const C = new Canvas(r, { seed: 1321 });
    paintRange(C, { ridge: (x) => 610 - bump(x, 120, 200, 130) - bump(x, 600, 160, 90) - 24 * ridged(x * 0.007, 4, 5), top: hex('#4a3a66'), mid: hex('#3a2f5c'), base: hex('#30284e'), fall: 180, light: { dir: 1, col: hex('#c07a7a'), amt: 0.35 }, haze: { col: hex('#c08a8a'), y0: 560, y1: 690, a: 0.8 }, rim: hex('#f0a478') });
    C.mottle({ amt: 0.05 }); planes.far = S.plane('far', D.far, r, C.c); }
  { const r = cover(D.plain, 40); r[1] = Math.max(r[1], 596); const C = new Canvas(r, { seed: 1331 }); const R = rng(13311); const g = C.g;
    const fc = (x, y) => mixc(mixc(hex('#4a3a5a'), hex('#1c1828'), smoothstep(600, 1300, y)), hex('#8a5a6a'), 0.35 * smoothstep(720, 600, y) + 0.0);
    const path = new Path2D(); path.rect(r[0], 596, r[2] - r[0], r[3] - 596); underpaint(C, fc, path, 6);
    C.strokes({ n: C.area / 700, mask: C.mask((gg) => gg.fill(path)), color: fc, angle: () => (R() - 0.5) * 0.2, len: [18, 60], wid: [4, 10], alpha: [0.4, 0.75], jv: 0.08 });
    // fields in long strips and the road
    for (let i = 0; i < 40; i++) { const y = lerp(610, 1290, Math.pow(R(), 0.8)), x = lerp(r[0], r[2], R()); const s = 6 + (y - 600) * 0.05; C.dab(x, y, (R() - 0.5) * 0.15, s * 8 * (0.6 + R()), s * 0.9, mixc(hex('#3a3a48'), hex('#5a4a50'), R()), 0.45, 0.08); }
    const rb = ribbonPath(ROAD, (y) => 6 + (y - 600) * 0.1, 0.3); const rc = (x, y) => mixc(hex('#7a6a74'), hex('#3a3040'), smoothstep(620, 1200, y)); underpaint(C, rc, rb.path, 5);
    C.strokes({ n: 500, mask: C.mask((gg) => gg.fill(rb.path)), color: rc, angle: () => (R() - 0.5) * 0.3, len: [10, 28], wid: [3, 6], alpha: [0.4, 0.7], jv: 0.08 });
    { const gr = g.createLinearGradient(0, 596, 0, 700); gr.addColorStop(0, 'rgba(200,140,130,0.9)'); gr.addColorStop(1, 'rgba(200,140,130,0)'); g.fillStyle = gr; g.fillRect(r[0], 596, r[2] - r[0], 110); g.save(); g.globalCompositeOperation = 'destination-out'; const g2 = g.createLinearGradient(0, 596, 0, 640); g2.addColorStop(0, 'rgba(0,0,0,1)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = g2; g.fillRect(r[0], 580, r[2] - r[0], 66); g.restore(); }
    C.mottle({ amt: 0.06 }); planes.plain = S.plane('plain', D.plain, r, C.c); }
  // the fortress on its hill, to the right: walls, towers, a keep with one window
  let KEEP = { wx: 536, wy: 540 };
  { const r = cover(D.keep, 60); r[1] = Math.max(r[1], 330); r[3] = Math.min(r[3], 900); const C = new Canvas(r, { seed: 1341 }); const R = rng(13411); const g = C.g;
    const hill = (x) => 760 - bump(x, 560, 230, 190) - 14 * Math.sin(x * 0.012) + det(x, 8, 3, 2);
    const hp = new Path2D(); hp.moveTo(r[0], r[3]); for (let x = r[0]; x <= r[2]; x += 6) hp.lineTo(x, hill(x)); hp.lineTo(r[2], r[3]); hp.closePath();
    const hc = (x, y) => mixc(hex('#3a2c4a'), hex('#1a1424'), smoothstep(560, 820, y)); underpaint(C, hc, hp, 7); C.strokes({ n: C.area / 1100, mask: C.mask((gg) => gg.fill(hp)), color: hc, angle: () => (R() - 0.5) * 0.4, len: [14, 40], wid: [4, 9], alpha: [0.4, 0.75], jv: 0.08 });
    for (let i = 0; i < 26; i++) { const x = lerp(r[0], r[2], R()); pineTree(C, x, hill(x) + 22 + R() * 50, 34 + R() * 30, hex('#120e1e'), { rim: hex('#8a5a6a'), rimSide: 1 }); }
    // walls and towers (dark masonry, lit rim from the sky glow behind)
    const wallY = (x) => hill(x) - 6; const blk = hex('#241a30'), lit = hex('#7a5a70'), rim = hex('#f0b090');
    const wallPath = new Path2D(); wallPath.moveTo(380, wallY(380) + 40); wallPath.lineTo(380, wallY(380) - 50); wallPath.lineTo(700, wallY(700) - 46); wallPath.lineTo(700, wallY(700) + 40); wallPath.closePath(); g.fillStyle = rgba(blk); g.fill(wallPath);
    g.strokeStyle = rgba(rim, 0.5); g.lineWidth = 1.5; g.beginPath(); g.moveTo(380, wallY(380) - 50); g.lineTo(700, wallY(700) - 46); g.stroke();
    for (let x = 384; x < 700; x += 22) { const yy = wallY(x) - 50 + (x - 380) * 4 / 320; g.fillStyle = rgba(blk); g.fillRect(x, yy - 12, 12, 12); g.fillStyle = rgba(rim, 0.45); g.fillRect(x, yy - 12, 12, 1.4); }
    const tower = (x, w, h, roof) => { const yb = wallY(x) + 30; g.fillStyle = rgba(blk); g.fillRect(x - w / 2, yb - h, w, h); g.fillStyle = rgba(lit, 0.35); g.fillRect(x - w / 2, yb - h, w * 0.18, h); for (let k = 0; k < 4; k++) { g.fillStyle = rgba(blk); g.fillRect(x - w / 2 + k * w / 3.6, yb - h - 12, w / 5, 12); } g.fillStyle = rgba(rim, 0.5); g.fillRect(x - w / 2, yb - h - 12, w, 1.5);
      if (roof) { g.fillStyle = rgba(hex('#1a1220')); g.beginPath(); g.moveTo(x - w / 2 - 5, yb - h - 12); g.lineTo(x, yb - h - 12 - w * 0.8); g.lineTo(x + w / 2 + 5, yb - h - 12); g.fill(); g.fillStyle = rgba(rim, 0.4); g.beginPath(); g.moveTo(x - w / 2 - 5, yb - h - 12); g.lineTo(x, yb - h - 12 - w * 0.8); g.lineTo(x - w / 2 + 2, yb - h - 12); g.fill(); } return yb - h; };
    tower(392, 48, 120, false); tower(690, 46, 110, false);
    const ky = tower(540, 100, 190, true); KEEP = { wx: 548, wy: ky + 70, w: 14, h: 26 }; g.fillStyle = rgba(hex('#0a0710')); g.fillRect(KEEP.wx - 7, KEEP.wy - 13, 14, 26);
    for (let k = 0; k < 5; k++) { const wx = 505 + (k % 3) * 33, wy2 = ky + 110 + Math.floor(k / 3) * 40; g.fillStyle = rgba(hex('#0a0710')); g.fillRect(wx, wy2, 9, 18); }
    C.mottle({ amt: 0.05 }); planes.keep = S.plane('keep', D.keep, r, C.c); }
  { const r = cover(D.ramp, 40); r[1] = Math.max(r[1], 880); const C = new Canvas(r, { seed: 1351 }); const R = rng(13511); const g = C.g;
    // the parapet: a stone walkway edge with merlons, a tower base at the left
    const top = 1010; const path = new Path2D(); path.rect(r[0], top, r[2] - r[0], r[3] - top); const sc = (x, y) => mixc(mixc(hex('#3a2e44'), hex('#171220'), smoothstep(top, top + 270, y)), hex('#6a5068'), 0.25 * smoothstep(top + 40, top, y));
    underpaint(C, sc, path, 7); C.strokes({ n: C.area / 900, mask: C.mask((gg) => gg.fill(path)), color: sc, angle: () => (R() - 0.5) * 0.15, len: [20, 70], wid: [5, 11], alpha: [0.4, 0.75], jv: 0.07 });
    for (let x = -40; x < 780; x += 150) { const mp = new Path2D(); mp.rect(x, top - 78, 96, 80); underpaint(C, (xx, yy) => mixc(hex('#2e2438'), hex('#4a3a56'), smoothstep(top - 78, top, yy) * 0.3 + 0.1 * R()), mp, 6); g.fillStyle = rgba(hex('#f0b090'), 0.5); g.fillRect(x, top - 78, 96, 2.5); g.fillStyle = rgba(hex('#0e0a16'), 0.5); g.fillRect(x + 90, top - 76, 6, 78); }
    g.strokeStyle = rgba(hex('#0e0a16'), 0.6); g.lineWidth = 2; for (let y = top + 30; y < r[3]; y += 38) { g.beginPath(); g.moveTo(r[0], y); g.lineTo(r[2], y); g.stroke(); for (let x = (y % 76 ? 0 : 40) + r[0]; x < r[2]; x += 80) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 38); g.stroke(); } }
    C.mottle({ amt: 0.05 }); planes.ramp = S.plane('ramp', D.ramp, r, C.c); }
  tintAll(S, 1);
  return {
    planes, D,
    update(F) {
      const t = F.t, sh = F.shot, g = F.g, lt = F.lt; const gl = F.glow(); const dawn = sh.dawn ? 1 : 0;
      planes.sky_dusk.visible = !dawn; planes.sky_dawn.visible = !!dawn; const k = dawn ? 0.85 : 0.7; tintAll(S, k, dawn ? [1.1, 1.0, 0.95] : [1, 1, 1.05]);
      // the lantern line on the plain: each leader a warm point, a dark huddle behind it; they appear as the shot goes, nearer ones drift closer
      if (sh.lanterns) { const [n0, t0, t1] = sh.lanterns; const NG = 8; const n = Math.floor(NG * smoothstep(t0, t1, t) + 0.5);
        // groups of men, each led by one with a lantern; the others walk behind with a hand on the shoulder in front; every group a little nearer as the shot goes
        for (let i = 0; i < n; i++) { const u0 = 0.05 + i * 0.112; const u = clamp(u0 + 0.004 * (t - t0), 0, 0.99); const age = clamp((t - (t0 + (t1 - t0) * i / NG)) / 0.8); const f = fireFlick(t, i);
          const men = 6; const pts = []; for (let j = 0; j < men; j++) { const uj = clamp(u - j * 0.0095, 0, 1); const pj = ROAD.at(1 - uj); const q = F.P(D.plain, pj.x + (j % 2 ? 2 : -2), pj.y), K = F.K(D.plain, pj.x, pj.y); pts.push({ q, h: (5 + (pj.y - 600) * 0.045) * K * 2.0, j }); }
          for (let j = men - 1; j >= 0; j--) { const { q, h } = pts[j]; const bob = Math.sin(t * 5.2 + j * 1.7 + i) * h * 0.012; g.fillStyle = rgba(hex(j === 0 ? '#15101c' : '#0c0814'), 0.94 * age);
            g.beginPath(); g.moveTo(q[0] - h * 0.13, q[1]); g.lineTo(q[0] - h * 0.09, q[1] - h * 0.66 + bob); g.lineTo(q[0] + h * 0.09, q[1] - h * 0.66 + bob); g.lineTo(q[0] + h * 0.14, q[1]); g.closePath(); g.fill(); g.beginPath(); g.arc(q[0], q[1] - h * 0.8 + bob, h * 0.1, 0, 7); g.fill();
            if (j > 0) { const fr = pts[j - 1]; g.strokeStyle = rgba(hex('#0c0814'), 0.9 * age); g.lineWidth = Math.max(0.8, h * 0.05); g.lineCap = 'round'; g.beginPath(); g.moveTo(q[0], q[1] - h * 0.6 + bob); g.lineTo(fr.q[0] + h * 0.03, fr.q[1] - h * 0.62); g.stroke(); } }
          const L = pts[0]; const lx = L.q[0] + L.h * 0.24, ly = L.q[1] - L.h * 0.52; g.strokeStyle = rgba(hex('#15101c'), 0.9 * age); g.lineWidth = Math.max(0.8, L.h * 0.04); g.beginPath(); g.moveTo(L.q[0], L.q[1] - L.h * 0.6); g.lineTo(lx, ly - L.h * 0.08); g.stroke();
          glowAt(gl, lx, ly, 3 + L.h * 0.34, 0.95 * f * age, [255, 190, 110]); glowAt(gl, lx, ly, 6 + L.h * 1.5, 0.34 * f * age, [255, 150, 80]); glowAt(gl, lx, ly, 10 + L.h * 4, 0.1 * f * age, [255, 130, 60]); } }
      // the keep window: lit, then out at `windowOut`
      if (sh.window) { const kp = F.P(D.keep, KEEP.wx, KEEP.wy), K = F.K(D.keep, KEEP.wx, KEEP.wy); const on = 1 - smoothstep(sh.window, sh.window + 0.5, t); const f = fireFlick(t, 7) * on; g.fillStyle = rgba([255, 190, 110], 0.92 * on); g.fillRect(kp[0] - 6 * K, kp[1] - 12 * K, 12 * K, 24 * K); glowAt(gl, kp[0], kp[1], 120 * K, 0.5 * f, [255, 160, 80]); F.lights.push({ x: kp[0], y: kp[1], r: 150 * K, c: WARM, k: 0.6 * on }); }
      // Samuel on the parapet
      if (sh.samuel) { const o = sh.samuel; const sp = F.P(D.ramp, o.x ?? 300, 1010 + 6), K = F.K(D.ramp, 300, 1010); const hh = (o.h ?? 330) * K; const col = clamp((t - (sh.collapse ?? 1e9)) / 1.1); const e = ease.inQuad(col);
        g.save(); g.translate(sp[0], sp[1]); if (col > 0) { g.translate(-hh * 0.1 * e, hh * 0.02 * e); g.rotate(-1.35 * e); } person(g, { x: 0, y: 0, h: hh, face: o.face ?? 1, walk: 0, col: hex('#4b1a24'), col2: hex('#5a2430'), cape: hex('#5a1a2a'), crown: true, hood: false, skinCol: hex('#140e1c'), head: 0.06 - 0.18 * e, warm: undefined, reach: [0.2, 0.5 + 0.2 * e] }); g.restore();
        if (sh.guard && t > sh.collapse + 0.4) { const gu = clamp((t - sh.collapse - 0.4) / 0.7); const gp = F.P(D.ramp, 520 - 120 * ease.outQuad(gu), 1016); person(g, { x: gp[0], y: gp[1], h: 300 * K, face: -1, ph: t * 1.6, walk: 1 - gu, col: hex('#2a2038'), col2: hex('#3a2c4a'), hood: false, skinCol: hex('#140e1c'), reach: [-0.3, 0.7] }); } }
      // life: swifts over the plain, hearth smoke under the fortress, a mist sliding over the fields, drifting motes
      { const kp = F.P(D.keep, 420, 760), KK = F.K(D.keep); for (const [dx, sd] of [[0, 1], [150, 2], [260, 3]]) smoke(g, t, kp[0] + dx * KK, kp[1], { n: 5, rise: 90 * KK, wind: 8, r0: 1.5 * KK + 0.5, r1: 9 * KK + 2, a: dawn ? 0.2 : 0.16, col: dawn ? [200, 170, 180] : [130, 100, 140], life: 8, seed: sd }); }
      birds(g, t, { x0: -60, x1: 780, y0: 320, y1: 520, n: dawn ? 8 : 5, seed: dawn ? 5 : 6, size: 5.5, speed: 15, dir: dawn ? 1 : -1, hz: 2.2, col: dawn ? [60, 44, 80] : [26, 16, 44], a: 0.8 });
      hazeBand(gl, t, { y: 720, n: 6, h: 55, w: 340, a: dawn ? 0.06 : 0.04, col: dawn ? [255, 210, 190] : [200, 150, 190], speed: 5, seed: 8 });
      motes(gl, t, { x0: 0, y0: 600, x1: 720, y1: 1100 }, { n: 14, col: dawn ? [255, 230, 190] : [255, 190, 140], a: 0.25, size: 1.0, seed: 12, drift: [4, -2] });
      if (!dawn && sh.glowSky !== false) { const sp = F.P(D.sky, 250, 620); glowAt(gl, sp[0], sp[1], 520, 0.12, [255, 170, 110]); }
      if (dawn) { const sp = F.P(D.sky, 360, 640); glowAt(gl, sp[0], sp[1], 600, 0.07 + 0.05 * smoothstep(0, 3, lt), [255, 200, 140]); }
      if (!dawn) embers(gl, t, { x0: 0, y0: 600, x1: 720, y1: 1000 }, 10, { size: 1.0, col: [255, 190, 130], a: 0.25, wind: 6, rise: 0.2, seed: 21 });
      F.amb = [0.95, 0.92, 1.0]; F.bloom = dawn ? 0.6 : 0.5; F.lights = F.lights;
    },
  };
}
