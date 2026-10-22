// SET road: the long switchback road over a Balkan hillside at dusk (the Lantern Road). Wide shots of the captives, the lantern groups,
// the title card and the last image. Planes at depth: sky 6000, peaks 2400, mid 1000, fog 420, hill (with the road painted on it) 170, foreground 70.
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, igniteEnv, flick, spline, ribbonPath, tintAll, lightsOn } from './common.js';
import { paintSky, paintRange, pineTree, paintFog, paintRocks, paintTufts, paintHouse } from '../paint.js';
import { person, banner, glowAt, torch, embers, hash1, PAL, STRIDE } from '../figs.js';
import { birds, smoke, motes, hazeBand, paintGrassStrip } from '../ambient.js';

export const ROAD_PTS = [[-70, 1330], [250, 1250], [620, 1175], [700, 1130], [560, 1085], [190, 1030], [60, 990], [110, 955], [430, 915], [640, 880], [670, 850], [560, 828], [300, 795], [215, 770], [260, 745], [430, 722], [520, 704], [500, 690], [440, 676], [412, 664]].map(([x, y]) => ({ x, y }));
export const hwAt = (y) => 3 + (y - 650) * 0.2;           // half road width (design px) at hill row y
export const hgt = (y) => 0.9 * hwAt(y);                  // a 1.75 m person (road = 4 m): figure height in design px

export default function road(S, cams, env) {
  const cover = (D, m) => S.cover(D, cams, m);
  const D = { sky: 6000, peaks: 2400, mid: 1000, fog: 420, hill: 170, fg: 70 };
  const planes = {}; const HAM = { win: [], chim: [] };
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 11 });
    paintSky(C, { stops: [[-500, hex('#0b0e30')], [0, hex('#141944')], [250, hex('#262c5d')], [420, hex('#444580')], [540, hex('#6a5f90')], [640, hex('#8f7a9c')]], glow: { x: 30, y: 600, rx: 820, ry: 300, col: hex('#e0a58e'), a: 0.75 },
      clouds: [{ y: 120, h: 13, x0: -300, x1: 1000, col: hex('#1f2454'), lit: hex('#5d5789'), litA: 0.6, sy: 0.03 }, { y: 280, h: 11, x0: -200, x1: 1100, col: hex('#2e3366'), lit: hex('#8f7c9f'), litA: 0.7, thr: 0.5, sy: 0.034 },
        { y: 430, h: 9, x0: 120, x1: 1100, col: hex('#3a3d72'), lit: hex('#a18aa6'), litA: 0.7, thr: 0.5, sy: 0.04 }, { y: -140, h: 16, x0: -300, x1: 1000, col: hex('#10143c'), lit: hex('#272c5c'), litA: 0.5, sy: 0.026, thr: 0.48 }] });
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.peaks); r[3] = Math.min(r[3], 760); const C = new Canvas(r, { seed: 21 });
    const ridge = (x) => 585 - bump(x, 150, 190, 270) - bump(x, 430, 130, 210) - bump(x, 640, 120, 120) - bump(x, 20, 120, 120) - 34 * ridged(x * 0.0065, 4, 1) - 9 * ridged(x * 0.03, 3, 2);
    paintRange(C, { ridge, top: hex('#323866'), mid: hex('#383d6c'), base: hex('#474a79'), fall: 190, light: { dir: -1, col: hex('#5a5f93'), amt: 0.45 }, shade: 0.18, haze: { col: hex('#4f4d7e'), y0: 520, y1: 640, a: 0.5 }, snow: { y: 400, col: hex('#8a8bb6'), amt: 0.85 }, rim: hex('#9c8fb0') });
    C.mottle({ amt: 0.05 }); planes.peaks = S.plane('peaks', D.peaks, r, C.c); }
  { const r = cover(D.mid); r[3] = Math.min(r[3], 760); r[1] = Math.max(r[1], 440); const C = new Canvas(r, { seed: 31 });
    const ridge = (x) => 612 - bump(x, 560, 200, 60) - bump(x, 90, 150, 48) - bump(x, 340, 90, -14) - 14 * ridged(x * 0.01, 3, 3);
    paintRange(C, { ridge, top: hex('#262a55'), mid: hex('#2e325f'), base: hex('#45477a'), fall: 120, light: { dir: -1, col: hex('#3e4377'), amt: 0.4 }, shade: 0.12, haze: { col: hex('#5a5788'), y0: 640, y1: 740, a: 0.8 }, rim: hex('#5a5f92'), sizes: 0.9 });
    // a far hamlet under the ridge: little houses, chimneys that smoke, windows that warm up at dusk
    { const R = rng(3701); for (let k = 0; k < 10; k++) { const x = 486 + k * 12 + (R() - 0.5) * 6, yg = 606 + (k % 3) * 4 + R() * 3; const hh = paintHouse(C, x, yg, 8 + R() * 5, 5 + R() * 3, { wall: hex('#3c3f70'), roof: hex('#1f2250'), crest: hex('#6a6aa0'), win: hex('#15183a'), roofK: 0.5, gable: R() < 0.4, sideShade: 1, litLeft: 0.3 });
        for (const w of hh.windows) HAM.win.push([w[0] + w[2] / 2, w[1] + w[3] / 2]); if (k === 2 || k === 6) HAM.chim.push([x + 1, hh.roofTop]); } }
    C.mottle({ amt: 0.05 }); planes.mid = S.plane('mid', D.mid, r, C.c); }
  { const r0 = cover(D.fog, 150); const r = [r0[0], 600, r0[2], 760]; const C = new Canvas(r, { seed: 51 });
    paintFog(C, { y: (x) => 668 + 10 * Math.sin(x * 0.004), h: 30, col: hex('#5d5a88'), top: hex('#7b77a3'), a: 0.95, density: 1.5, wisp: 0.8, blur: 3 }); planes.fog = S.plane('fog', D.fog, r, C.c); planes.fog.userData.drift = 5; }
  // ---- the hillside with the road
  const dense = spline(ROAD_PTS, 12); const rb = ribbonPath(dense, hwAt, 0.3);
  const crest = (x) => 664 + 24 * Math.sin(x * 0.006 + 0.8) + det(x, 10, 4, 3) + bump(x, 420, 70, 16) - bump(x, 760, 160, 20);
  { const r = cover(D.hill, 40); r[3] = Math.max(r[3], 1360); const C = new Canvas(r, { seed: 71 }); const g = C.g; const R = rng(7101);
    const hill = paintRange(C, { ridge: crest, top: hex('#2b2f5e'), mid: hex('#1f2347'), base: hex('#101229'), fall: 640, light: { dir: -1, col: hex('#3a3f74'), amt: 0.32 }, shade: 0.14, rim: hex('#5a5f92'), sizes: 1.15, n: 1.0 });
    // road bed: edge shadow below, banked edge above, packed earth, ruts
    const rbE = ribbonPath(dense, hwAt, 0.3, 4);
    g.fillStyle = rgba(hex('#0c0e1f'), 0.55); g.save(); g.translate(0, 4); g.fill(rbE.path); g.restore();
    const roadCol = (x, y) => mixc(mixc(hex('#4a4663'), hex('#34314d'), smoothstep(700, 1150, y)), hex('#625d80'), 0.5 * smoothstep(760, 660, y));
    underpaint(C, roadCol, rb.path, 4); const mb = C.mask((gg) => gg.fill(rb.path));
    // strokes along the road direction
    for (let i = 0; i < dense.length - 1; i += 1) { const a = dense[i], b = dense[i + 1]; const ang = Math.atan2(b.y - a.y, b.x - a.x); const w = hwAt(a.y); const n = Math.max(2, Math.round(w / 5));
      for (let k = 0; k < n; k++) { const o = (R() - 0.5) * 2 * w * 0.85; C.dab(a.x + o * Math.sin(ang) * 0.3 * 0 + (R() - 0.5) * 4, a.y + (R() - 0.5) * w * 0.12, ang + (R() - 0.5) * 0.2, Math.hypot(b.x - a.x, b.y - a.y) * 2.4 + 6, Math.max(1.5, w * 0.09), mixc(hex('#3a3752'), hex('#6c6788'), R() * 0.8), 0.55, 0.05); } }
    // ruts and pale verge stones
    for (let i = 0; i < dense.length - 1; i += 2) { const a = dense[i], b = dense[i + 1]; const ang = Math.atan2(b.y - a.y, b.x - a.x); const w = hwAt(a.y);
      for (const s of [-0.38, 0.38]) C.dab(a.x - Math.sin(ang) * w * s * 0.9 * 0.3 * 0, a.y + s * w * 0.3, ang, 26, Math.max(1.2, w * 0.05), hex('#2c2a44'), 0.5, 0.02); }
    paintTufts(C, { x0: r[0], x1: r[2], base: (x) => crest(x) + 1, step: 8, h0: 3, h1: 9, col: hex('#14162c'), blades: 4 });
    // tufts along the road edges
    for (let i = 0; i < dense.length; i += 2) { const p = dense[i]; const w = hwAt(p.y); for (const sd of [-1, 1]) { const x = p.x + sd * (w * 0.95 + R() * 4); const y = p.y + sd * w * 0.3 + (R() - 0.5) * 4; const hh = 4 + w * 0.12 * (0.5 + R()); for (let k = 0; k < 4; k++) { const a = -Math.PI / 2 + (R() - 0.5) * 1.0; C.dab(x + (R() - 0.5) * hh, y, a, hh * (0.6 + R() * 0.5), Math.max(1.3, hh * 0.12), mul(hex('#14162c'), 0.8 + R() * 0.5), 0.8, 0.1, 0.9); } } }
    // pines on the slope (kept off the road bed)
    const dist = (x, y) => { let b = 1e9; for (const p of dense) { const dx = (x - p.x), dy = (y - p.y) / 0.3; b = Math.min(b, Math.hypot(dx, dy) - hwAt(p.y)); } return b; };
    const trees = []; for (let k = 0; k < 900 && trees.length < 46; k++) { const y = lerp(690, 1330, Math.pow(R(), 0.85)), x = lerp(r[0] + 10, r[2] - 10, R()); if (y < crest(x) + 12) continue; if (dist(x, y) < 20 + hwAt(y) * 0.3) continue; trees.push([x, y, hwAt(y)]); }
    trees.sort((a, b) => a[1] - b[1]); for (const [x, y, w] of trees) pineTree(C, x, y, Math.min(190, 1.9 * w * (0.6 + R() * 0.6)), mul(hex('#10122a'), 0.8 + R() * 0.45), { rim: hex('#2f3660'), tierPx: Math.max(3.5, w * 0.16), wr: 0.34 });
    for (let i = 0; i < 40; i++) { const x = lerp(r[0], r[2], R()), y = lerp(720, 1320, R()); if (dist(x, y) < 10 || y < crest(x) + 18) continue; const s = 3 + hwAt(y) * 0.12 * R() * 2; C.dab(x, y, -0.3 + (R() - 0.5) * 0.4, s * 2, s, hex('#0d0f21'), 0.9, 0.2, 1.0); C.dab(x - s * 0.3, y - s * 0.35, -0.4, s * 1.2, s * 0.3, hex('#2c2f4e'), 0.5, 0.1); }
    C.mottle({ amt: 0.06 }); planes.hill = S.plane('hill', D.hill, r, C.c); }
  { const r = cover(D.fg, 60); r[1] = Math.max(r[1], 940); const C = new Canvas(r, { seed: 91 });
    paintRocks(C, { rocks: [{ x: -20, y: 1290, rx: 260, ry: 110 }, { x: 420, y: 1360, rx: 220, ry: 80 }, { x: 800, y: 1300, rx: 260, ry: 110 }], col: hex('#080914'), lit: hex('#2f3458'), litA: 0.42, blur: 3.5 });
    planes.fg = S.plane('fg', D.fg, r, C.c); }
  { const r = cover(D.fg, 60); planes.grass = paintGrassStrip(S, 'grass', D.fg - 1, [r[0], 1250, r[2], 1385], { seed: 93, col: hex('#07081a'), lit: hex('#2c3158'), h0: 26, h1: 70, step: 10, amp: 0.0045, freq: 18 }); }
  // far hamlet windows: small warm lights
  const hamGlows = HAM.win.map(([x, y]) => S.glow(x, y, D.mid, 9, { color: [1.0, 0.62, 0.28], core: 140 }, planes.mid));
  tintAll(S, 1);

  const total = dense.total;
  // metres from the bottom of the road: the road is 4 m wide (2 * hwAt px) and its ground is tilted by k = 0.3, so every step in px becomes a real step in metres.
  // Everything that walks is driven in metres and metres per second, so a far walker is as slow as a near one (not a screen-speed slide).
  const MB = new Float32Array(dense.length); for (let i = 1; i < dense.length; i++) { const a = dense[i - 1], b = dense[i]; MB[i] = MB[i - 1] + Math.hypot(b.x - a.x, (b.y - a.y) / 0.3) / (hwAt((a.y + b.y) / 2) / 2); }
  const Mtot = MB[dense.length - 1];
  const sOfM = (m) => { m = clamp(m, 0, Mtot); let a = 0, b = dense.length - 1; while (b - a > 1) { const k = (a + b) >> 1; if (MB[k] <= m) a = k; else b = k; } return lerp(dense[a].s, dense[b].s, (m - MB[a]) / Math.max(1e-6, MB[b] - MB[a])); };
  const ptM = (m) => dense.at(sOfM(m) / total);
  const mAtU = (u) => { const s = clamp(u, 0, 1) * total; let a = 0, b = dense.length - 1; while (b - a > 1) { const k = (a + b) >> 1; if (dense[k].s <= s) a = k; else b = k; } return lerp(MB[a], MB[b], (s - dense[a].s) / Math.max(1e-6, dense[b].s - dense[a].s)); };
  // draw a walker (or a few-pixel stand-in when it is tiny) at road metre m. dir +1 walks up the road (m grows), -1 down. The figure turns through the hairpins.
  function walker(F, m, o) {
    const p = ptM(m); const hd = hgt(p.y) * (o.scale ?? 1); const off = (o.off ?? 0) * hwAt(p.y); const px = p.x + off * 0.9, py = p.y + off * 0.25;
    const q = F.P(D.hill, px, py), K = F.K(D.hill, px, py); const h = hd * K; if (h < 1.2) return null;
    const dir = o.dir ?? 1; const ddx = p.dx * dir, ddy = (p.dy * dir) / 0.3; const turn = ddx / (Math.hypot(ddx, ddy) || 1); const face = (turn < 0 ? -1 : 1) * Math.max(0.3, Math.pow(Math.abs(turn), 0.5));
    return { sy: q[1], draw(g) {
      if (h < 9) { g.fillStyle = rgba(o.col || hex('#1a1828')); g.beginPath(); g.ellipse(q[0], q[1] - h * 0.42, h * 0.16, h * 0.42, 0, 0, 7); g.fill(); g.beginPath(); g.arc(q[0], q[1] - h * 0.9, h * 0.1, 0, 7); g.fill();
        if (o.staff || o.spear) { g.strokeStyle = rgba(PAL.staff); g.lineWidth = 1; g.beginPath(); g.moveTo(q[0] + h * 0.2, q[1]); g.lineTo(q[0] + h * 0.16, q[1] - h * 1.25); g.stroke(); } return {}; }
      const ph = (dir > 0 ? m : -m) / (STRIDE * 1.75 * (o.scale ?? 1)) + (o.ph0 || 0);
      return person(g, { x: q[0], y: q[1], h, face, ph, walk: o.walk ?? 1, col: o.col || PAL.cloak, col2: o.col2 || PAL.cloak2, head: o.head ?? -0.05, staff: o.staff, spear: o.spear, helm: o.helm, plume: o.plume, shield: o.shield, hood: o.hood, skinCol: o.skinCol, dark: o.dark, lantern: o.lantern, reach: o.reach, hem: o.hem ?? 0.2, stride: o.stride, t: F.t });
    }, h, q, face, p, hd, plane: [px, py] };
  }
  const PURPLE = { col: PAL.purple, colLit: PAL.purpleLit };
  const COL = [hex('#191726'), hex('#1b1a2c'), hex('#161425'), hex('#1e1b2e')];
  // a file of people: leader at metre mL, followers behind (hand on the shoulder ahead), at walking pace
  function file(F, mL, dir, n, o = {}) {
    const out = []; const gap = o.gap ?? 0.82;
    for (let k = 0; k < n; k++) { const m = mL - dir * k * gap; if (m < 0 || m > Mtot) continue; const lead = k === 0; const hv = hash1(k * 3.3 + (o.seed || 0)); const c = o.col || COL[(k + (o.seed || 0)) % 4];
      const w = walker(F, m, { dir, col: c, col2: mixc(c, hex('#2b2842'), 0.6), staff: lead && !o.bare, lantern: lead && o.lantern ? { on: o.on ?? 1 } : null, reach: !lead ? [0.34, 0.8] : null, head: lead ? -0.02 : -0.16 - 0.08 * hv, ph0: k * 0.37 + hv, scale: 0.95 + 0.09 * hv, walk: o.walk ?? 0.85 });
      if (w) { w.lead = lead; out.push(w); } }
    return out;
  }
  return {
    planes, hillPx: (s) => dense.at(s / total), dense, total, D, walker, file, Mtot, mAtU,
    update(F) {
      const t = F.t, sh = F.shot, S_ = F.S, g = F.g; const mode = sh.mode;
      let dark = 1; const items = []; const lamps = [];
      if (mode === 'army') {
        dark = 0.94; const G = 9, gap = 0.82, P = G * gap + 3.0, span = Mtot + 2 * P + 20, v = 1.0;
        const m0 = (j, tt) => (((j * P - v * tt) % span) + span) % span; const NG = Math.ceil(span / P);
        // the nearest groups light first (on the hits), the rest follow up the road
        const vis = []; for (let j = 0; j < NG; j++) { const m = m0(j, sh.lit[0]); if (m > 0 && m < Mtot) vis.push({ j, m }); } vis.sort((a, b) => a.m - b.m);
        const onT = new Map(); vis.forEach((e, r) => onT.set(e.j, r < sh.lit.length ? sh.lit[r] : lerp(sh.litRest[0], sh.litRest[1], clamp((r - sh.lit.length) / Math.max(1, vis.length - sh.lit.length)))));
        for (let j = 0; j < NG; j++) { const on = igniteEnv(t, onT.get(j) ?? sh.litRest[1] + 0.4, j + 1); const its = file(F, m0(j, t), -1, G, { lantern: true, on: clamp(on, 0, 1), gap, seed: j * 5 }); for (const w of its) if (w.lead && w.h > 3.5) lamps.push({ w, on }); items.push(...its); }
        // the escort: spearmen on both verges, a purple banner now and then; they march with the column, then halt at the roadside and let it go on alone
        for (let i = 0; Mtot - 14 - i * 21 > 0; i++) { const halt = lerp(sh.halt[0], sh.halt[1], (i * 0.618) % 1); const m = Mtot - 8 - i * 21 - v * Math.min(t, halt); const side = i % 2 ? 1.32 : -1.32; const wk = 1 - smoothstep(halt - 0.5, halt, t);
          const w = walker(F, m, { dir: -1, off: side, spear: true, helm: true, plume: i % 3 === 0 ? [96, 36, 56] : null, shield: i % 2 ? PAL.purple : null, hood: false, skinCol: hex('#150e1c'), col: hex('#241f33'), col2: hex('#30294a'), dark: hex('#150e1c'), head: -0.02, ph0: i * 0.23, walk: wk * 0.95, hem: 0.28, stride: 0.9 });
          if (w) { items.push(w); if (i % 3 === 1 && w.h > 8) items.push({ sy: w.q[1] - 0.1, draw: (gg) => banner(gg, { x: w.q[0] + w.face * w.h * 0.28, y: w.q[1] - w.h * 0.05, h: w.h * 2.7, w: w.h * 1.15, t, dir: -Math.sign(w.face), ...PURPLE, seed: i }) }); } }
      } else if (mode === 'groups') {
        dark = sh.dark ?? 0.74;
        for (const gr of sh.groups || []) { const on = gr.on != null ? igniteEnv(t, gr.on, gr.seed || 1) * (1 - smoothstep(gr.off ?? 1e9, (gr.off ?? 1e9) + 1.0, t)) : 1; const dir = gr.dir || -1;
          const mL = mAtU(gr.u) + dir * (gr.v ?? 1.1) * (t - (gr.t ?? 0)); const its = file(F, mL, dir, gr.n ?? 9, { lantern: true, on: clamp(on, 0, 1), gap: 0.8, seed: Math.round((gr.seed || 1) * 7), walk: 0.9 }); for (const w of its) if (w.lead && w.h > 3.5) lamps.push({ w, on }); items.push(...its); }
      }
      tintAll(S_, dark, [0.97, 0.98, 1.06]);
      // ---- ambient life: the hamlet (chimney smoke, windows warming), a flock of birds, drifting dust and haze
      const kM = F.K(D.mid, 540, 600); const dusk = clamp(0.35 + 0.65 * smoothstep(0, 6, t) + (t > 90 ? 0.4 : 0), 0, 1.2) * 1.0;
      hamGlows.forEach((gm, i) => { const on = smoothstep(2 + (i * 0.37) % 3, 4 + (i * 0.37) % 3, t < 20 ? t : 9) * 0.9; gm.visible = on > 0.01; gm.material.uniforms.uI.value = on * (0.8 + 0.2 * Math.sin(t * 1.3 + i)); });
      HAM.chim.forEach(([x, y], i) => { const p = F.P(D.mid, x, y); smoke(g, t, p[0], p[1], { n: 7, rise: 70 * kM, wind: 9 * kM, r0: 1.6 * kM, r1: 7 * kM, a: 0.32, life: 8, seed: i + 3, col: [128, 120, 170] }); });
      birds(g, t, { x0: -40, x1: 760, y0: 330, y1: 470, n: 7, seed: 3, size: 6.5, speed: 17, dir: 1, hz: 2.1, col: [18, 16, 40], a: 0.8 });
      birds(g, t, { x0: -40, x1: 760, y0: 560, y1: 640, n: 3, seed: 8, size: 4.2, speed: -11, dir: 1, hz: 2.6, col: [16, 15, 36], a: 0.7 });
      const gb = F.glow(); motes(gb, t, { x0: 0, y0: 560, x1: 720, y1: 1260 }, { n: 18, col: [190, 180, 240], a: 0.28, size: 1.1, seed: 4, drift: [6, -2] });
      // ---- lanterns: glow canvas (parallax-exact) + relight the hillside + the figures near them
      items.sort((a, b) => a.sy - b.sy); const res = new Map(); for (const it of items) { const r = it.draw(g); if (r) res.set(it, r); }
      const gl = lamps.length ? F.glow() : null; const hillLights = [];
      lamps.sort((a, b) => b.w.h - a.w.h);
      for (const { w, on } of lamps) { const r = res.get(w); if (!r || !r.lantern || on < 0.01) continue; const [lx, ly] = r.lantern; const k = clamp(on, 0, 1.6); const fk = 1 + 0.06 * Math.sin(t * 9 + lx);
        glowAt(gl, lx, ly, Math.max(5, w.h * 0.9), 0.95 * k * fk); glowAt(gl, lx, ly, Math.max(12, w.h * 3.2), 0.28 * k, [255, 140, 70]);
        if (F.lights.length < 8) F.lights.push({ x: lx, y: ly, r: Math.max(14, w.h * 1.6), c: WARM, k: 2.8 * k });
        if (hillLights.length < 8) hillLights.push({ p: S_.world(w.plane[0] + w.face * 0.19 * w.hd, w.plane[1] - 0.6 * w.hd, D.hill), r: Math.max(5, w.hd * 1.5) * D.hill / S_.f, c: WARM, k: 2.4 * k }); }
      lightsOn(planes.hill, hillLights);
      F.amb = [0.9 * dark + 0.1, 0.9 * dark + 0.1, 1.0 * dark + 0.1];
    },
  };
}
