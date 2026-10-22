// SET road: the long switchback road over a Balkan hillside at dusk (the Lantern Road). Wide shots of the captives, the lantern groups,
// the title card and the last image. Planes at depth: sky 6000, peaks 2400, mid 1000, fog 420, hill (with the road painted on it) 170, foreground 70.
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, igniteEnv, flick, spline, ribbonPath, tintAll, lightsOn } from './common.js';
import { paintSky, paintRange, pineTree, paintFog, paintRocks, paintTufts } from '../paint.js';
import { person, banner, glowAt, torch, embers, hash1, PAL, STRIDE } from '../figs.js';

export const ROAD_PTS = [[-70, 1330], [250, 1250], [620, 1175], [700, 1130], [560, 1085], [190, 1030], [60, 990], [110, 955], [430, 915], [640, 880], [670, 850], [560, 828], [300, 795], [215, 770], [260, 745], [430, 722], [520, 704], [500, 690], [440, 676], [412, 664]].map(([x, y]) => ({ x, y }));
export const hwAt = (y) => 3 + (y - 650) * 0.2;           // half road width (design px) at hill row y
export const hgt = (y) => 0.9 * hwAt(y);                  // a 1.75 m person (road = 4 m): figure height in design px

export default function road(S, cams, env) {
  const cover = (D, m) => S.cover(D, cams, m);
  const D = { sky: 6000, peaks: 2400, mid: 1000, fog: 420, hill: 170, fg: 70 };
  const planes = {};
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
    C.mottle({ amt: 0.05 }); planes.mid = S.plane('mid', D.mid, r, C.c); }
  { const r0 = cover(D.fog, 90); const r = [r0[0], 600, r0[2], 760]; const C = new Canvas(r, { seed: 51 });
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
  tintAll(S, 1);

  const P0 = dense[0], total = dense.total;
  const hillPx = (s) => dense.at(s / total);          // point on the road (design px of the hill plane) at arclength s
  const SKIP = [];
  // draw a walker (or a tiny stand-in when it is only a few pixels tall) at road arclength s
  function walker(F, s, o) {
    const p = hillPx(s); const hd = hgt(p.y) * (o.scale ?? 1); const off = (o.off ?? 0) * hwAt(p.y); const px = p.x + off * 0.9, py = p.y + off * 0.25;
    const q = F.P(D.hill, px, py), K = F.K(D.hill, px, py); const h = hd * K; if (h < 1.2) return null;
    const dir = o.dir ?? 1; const face = (p.dx * dir) >= 0 ? 1 : -1;
    return { sy: q[1], draw(g) {
      if (h < 9) { g.fillStyle = rgba(o.col || hex('#1a1828')); g.beginPath(); g.ellipse(q[0], q[1] - h * 0.42, h * 0.16, h * 0.42, 0, 0, 7); g.fill(); g.beginPath(); g.arc(q[0], q[1] - h * 0.9, h * 0.1, 0, 7); g.fill();
        if (o.staff) { g.strokeStyle = rgba(PAL.staff); g.lineWidth = 1; g.beginPath(); g.moveTo(q[0] + face * h * 0.2, q[1]); g.lineTo(q[0] + face * h * 0.16, q[1] - h * 1.25); g.stroke(); } return {}; }
      const ph = Math.abs(s) / (STRIDE * hd) + (o.ph0 || 0);
      return person(g, { x: q[0], y: q[1], h, face, ph, walk: o.walk ?? 1, col: o.col || PAL.cloak, col2: o.col2 || PAL.cloak2, head: o.head ?? -0.05, staff: o.staff, lantern: o.lantern, reach: o.reach, hem: 0.2 });
    }, h, q, face, p, hd, plane: [px, py] };
  }
  // a file of people: leader at arclength s0 moving dir (+1 up the road, -1 down), followers behind (hand on the shoulder ahead)
  function fileOf(F, s0, dir, n, o = {}) {
    const items = []; let s = s0;
    for (let k = 0; k < n; k++) { const lead = k === 0; const p = hillPx(s); if (s < 0 || s > total) { s -= dir * 0.5 * hgt(p.y); continue; }
      const w = walker(F, s, { dir, col: o.col, col2: o.col2, staff: lead && o.staff !== false && !o.bare, lantern: lead && o.lantern ? { on: o.on ?? 1 } : null, reach: !lead ? [0.3 + 0.04, 0.8] : null, head: o.head ?? -0.05, ph0: k * 0.37, off: o.off, scale: o.scale, walk: o.walk });
      if (w) { w.lead = lead; items.push(w); } s -= dir * (o.gap ?? 0.5) * hgt(p.y) * (o.scale ?? 1); }
    return items;
  }
  const PURPLE = { col: PAL.purple, colLit: PAL.purpleLit };
  return {
    planes, hillPx, dense, total, D, walker, fileOf,
    update(F) {
      const t = F.t, lt = F.lt, sh = F.shot, S_ = F.S, g = F.g; const mode = sh.mode;
      planes.fog.position.x = planes.fog.userData.base.x - planes.fog.userData.drift * t * planes.fog.userData.D / S_.f;
      let dark = 1, items = [], lamps = [];
      if (mode === 'captives') {
        dark = 0.94; const spd = 17;
        // the column comes down the road from the notch: spearmen along the flank, banners at intervals
        let s = total * 0.985 - spd * t * 0 - (t * spd) % 1e9; s = total * 1.02 - spd * t; let k = 0;
        while (s > -40 && k < 400) { const p = hillPx(clamp(s, 0, total)); const hd = hgt(p.y); const bannerK = k % 34 === 0 && k > 0; const guard = k % 7 === 3;
          const w = walker(F, clamp(s, 0, total), { dir: -1, col: guard ? hex('#241f33') : hex('#191726'), col2: hex('#242238'), head: guard ? -0.02 : -0.22, staff: guard, off: guard ? (k % 14 === 3 ? 1.12 : -1.12) : ((k * 0.37) % 1 - 0.5) * 0.6, ph0: k * 0.37, walk: guard ? 1 : 0.8 });
          if (w) { items.push(w); if (bannerK) { const dpx = w; items.push({ sy: w.q[1] - 0.1, draw: (gg) => banner(gg, { x: w.q[0], y: w.q[1] - w.h * 0.05, h: w.h * 2.7, w: w.h * 1.15, t, dir: -w.face, ...PURPLE, seed: k }) }); } }
          s -= (0.55 + 0.25 * ((k * 0.618) % 1)) * hd; k++; }
      } else if (mode === 'lanterns' || mode === 'title' || mode === 'end') {
        const G = sh.groups || []; dark = sh.dark ?? 0.74;
        for (const gr of G) { const on = gr.on != null ? igniteEnv(t, gr.on, gr.seed || 1) * (1 - smoothstep(gr.off ?? 1e9, (gr.off ?? 1e9) + 1.0, t)) : 1; const s0 = gr.u * total + (gr.dir || -1) * (gr.v ?? 9) * (t - (gr.t ?? 0));
          const its = fileOf(F, s0, gr.dir || -1, gr.n ?? 9, { lantern: true, on: clamp(on, 0, 1), gap: 0.44, head: -0.02 }); for (const w of its) if (w.lead && w.h > 4) lamps.push({ w, on }); items.push(...its); }
      }
      tintAll(S_, dark, [0.97, 0.98, 1.06]);
      items.sort((a, b) => a.sy - b.sy); const res = new Map(); for (const it of items) { const r = it.draw(g); if (r) res.set(it, r); }
      // lanterns: glow canvas (parallax-exact) + relight the hillside + the figures near them
      const gl = lamps.length ? F.glow() : null; const hillLights = [];
      for (const { w, on } of lamps) { const r = res.get(w); if (!r || !r.lantern || on < 0.01) continue; const [lx, ly] = r.lantern; const k = clamp(on, 0, 1.6);
        glowAt(gl, lx, ly, Math.max(6, w.h * 0.9), 0.95 * k); glowAt(gl, lx, ly, Math.max(14, w.h * 3.2), 0.28 * k, [255, 140, 70]);
        F.lights.push({ x: lx, y: ly, r: Math.max(14, w.h * 1.6), c: WARM, k: 2.8 * k });
        hillLights.push({ p: S_.world(w.plane[0] + w.face * 0.19 * w.hd, w.plane[1] - 0.6 * w.hd, D.hill), r: Math.max(5, w.hd * 1.5) * D.hill / S_.f, c: WARM, k: 2.4 * k }); }
      lightsOn(planes.hill, hillLights.slice(0, 8));
      F.amb = [0.9 * dark + 0.1, 0.9 * dark + 0.1, 1.0 * dark + 0.1];
    },
  };
}
