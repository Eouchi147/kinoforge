// SET page: a large illuminated page in the manner of the indigo-dyed manuscripts (gold on deep blue), on a dark wooden desk by
// lamplight. The page itself carries only illumination: double gold rules, corner rosettes, a marginal medallion, a headband.
// The Qur'anic Arabic is never painted here: it is set crisp in the overlay (gfx.js) from the King Fahd Complex Uthmani text.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, rng, WARM, tintAll, lightsOn, glowAt, motes, flick } from '../lib.js';

export function rosette(g, x, y, r, col, a = 1) {
  g.save(); g.globalAlpha = a; g.strokeStyle = rgba(col); g.fillStyle = rgba(col); g.lineWidth = Math.max(1, r * 0.06);
  g.beginPath(); g.arc(x, y, r, 0, 7); g.stroke(); g.beginPath(); g.arc(x, y, r * 0.78, 0, 7); g.stroke();
  for (let k = 0; k < 12; k++) { const a0 = k * Math.PI / 6; g.beginPath(); g.ellipse(x + Math.cos(a0) * r * 0.45, y + Math.sin(a0) * r * 0.45, r * 0.28, r * 0.1, a0, 0, 7); g.fill(); }
  g.beginPath(); g.arc(x, y, r * 0.16, 0, 7); g.fillStyle = rgba(mixc(col, [120, 30, 30], 0.6)); g.fill(); g.restore();
}

export default function page(S, cams) {
  const cover = (D, m = 50) => S.cover(D, cams, m); const D = { desk: 11, page: 10 }; const planes = {};
  const PG = [110, 40, 1170, 690];
  { const r = cover(D.desk, 60); const C = new Canvas(r, { seed: 901 }); const [x0, y0, x1, y1] = r;
    underpaint(C, (x, y) => mul(hex('#2c1d14'), 0.7 + 0.5 * C.n.fbm(x * 0.002, y * 0.02, 3)), null, 10);
    C.strokes({ n: C.area / 300, color: (x, y) => mul(hex('#3a271a'), 0.6 + 0.6 * C.n.fbm(x * 0.002, y * 0.03, 3)), angle: () => (C.R() - 0.5) * 0.04, len: [80, 240], wid: [3, 7], alpha: [0.35, 0.7], jv: 0.08, bend: 0.01, taper: 0.5 });
    C.mottle({ amt: 0.12, cell: 30 }); planes.desk = S.plane('desk', D.desk, r, C.c); }
  { const C = new Canvas(PG, { seed: 902, q: 1.25 }); const g = C.g; const [x0, y0, x1, y1] = PG; const n = C.n;
    const edge = new Path2D(); const N = 90; const w = (u, s) => (n.fbm(u * 6 + s, 2.2, 3) - 0.5) * 8;
    edge.moveTo(x0 + 4, y0 + 4); for (let i = 0; i <= N; i++) edge.lineTo(lerp(x0, x1, i / N), y0 + 4 + w(i / N, 1)); for (let i = 0; i <= N; i++) edge.lineTo(x1 - 4 + w(i / N, 2), lerp(y0, y1, i / N)); for (let i = N; i >= 0; i--) edge.lineTo(lerp(x0, x1, i / N), y1 - 4 + w(i / N, 3)); for (let i = N; i >= 0; i--) edge.lineTo(x0 + 4 + w(i / N, 4), lerp(y0, y1, i / N)); edge.closePath();
    const base = (x, y) => { const e = Math.min(x - x0, x1 - x, y - y0, y1 - y); return mixc(mixc(hex('#0f1534'), hex('#18204a'), n.fbm(x * 0.004, y * 0.004, 4)), hex('#0a0e24'), (1 - smoothstep(0, 60, e)) * 0.6 + smoothstep(0.6, 0.85, n.fbm(x * 0.008 + 3, y * 0.008, 4)) * 0.3); };
    underpaint(C, base, edge, 5); const m = C.mask((gg) => gg.fill(edge));
    C.strokes({ n: C.area / 380, mask: m, color: base, angle: () => (C.R() - 0.5) * 3, len: [10, 40], wid: [4, 10], alpha: [0.25, 0.5], jv: 0.06, bend: 0.3 });
    C.strokes({ n: C.area / 2600, mask: m, color: () => hex('#2e3a74'), angle: () => C.R() * 6.28, len: [4, 14], wid: [0.8, 1.6], alpha: [0.25, 0.45], jv: 0.1, bend: 0.4 });
    const GOLD = hex('#c9a227'), GOLDL = hex('#e8c86a');
    // frame: double rule with a band of small lozenges between, corner rosettes
    const fr = (k, col, lw) => { g.strokeStyle = rgba(col, 0.92); g.lineWidth = lw; g.strokeRect(x0 + k, y0 + k, x1 - x0 - 2 * k, y1 - y0 - 2 * k); };
    fr(34, GOLD, 3); fr(52, GOLD, 1.5); fr(60, GOLDL, 0.8);
    g.fillStyle = rgba(GOLD, 0.85); for (const [ax, ay, bx, by] of [[x0 + 43, y0 + 43, x1 - 43, y0 + 43], [x0 + 43, y1 - 43, x1 - 43, y1 - 43]]) for (let x = ax + 20; x < bx - 10; x += 22) { g.beginPath(); g.moveTo(x, ay - 5); g.lineTo(x + 5, ay); g.lineTo(x, ay + 5); g.lineTo(x - 5, ay); g.closePath(); g.fill(); }
    for (const [ax, ay, by] of [[x0 + 43, y0 + 43, y1 - 43], [x1 - 43, y0 + 43, y1 - 43]]) for (let y = ay + 20; y < by - 10; y += 22) { g.beginPath(); g.moveTo(ax, y - 5); g.lineTo(ax + 5, y); g.lineTo(ax, y + 5); g.lineTo(ax - 5, y); g.closePath(); g.fill(); }
    for (const [x, y] of [[x0 + 43, y0 + 43], [x1 - 43, y0 + 43], [x0 + 43, y1 - 43], [x1 - 43, y1 - 43]]) { g.fillStyle = rgba(hex('#121a42')); g.beginPath(); g.arc(x, y, 18, 0, 7); g.fill(); rosette(g, x, y, 16, GOLD); }
    // marginal medallion on the right edge
    { const x = x1 - 10, y = (y0 + y1) / 2; g.fillStyle = rgba(hex('#121a42')); g.beginPath(); g.ellipse(x, y, 30, 46, 0, 0, 7); g.fill(); rosette(g, x, y, 26, GOLD); g.strokeStyle = rgba(GOLD); g.lineWidth = 1.5; g.beginPath(); g.moveTo(x, y - 46); g.lineTo(x, y - 76); g.moveTo(x, y + 46); g.lineTo(x, y + 76); g.stroke(); }
    // gold flecks, rubbed gilding
    for (let i = 0; i < 260; i++) { const x = lerp(x0 + 70, x1 - 70, C.R()), y = lerp(y0 + 70, y1 - 70, C.R()); g.fillStyle = rgba(GOLDL, 0.08 + C.R() * 0.12); g.beginPath(); g.arc(x, y, 0.6 + C.R() * 1.4, 0, 7); g.fill(); }
    C.mottle({ amt: 0.1, cell: 14, light: [200, 190, 255] }); planes.page = S.plane('page', D.page, PG, C.c); }
  const LAMP = [1240, 120];
  return {
    update(F) {
      const t = F.t; const gg = F.glow(); const fl = flick(t, 7); const sh = F.shot;
      tintAll(S, 0.44);
      const L = [{ p: S.world(LAMP[0], LAMP[1], D.page), r: 9, c: WARM, k: 1.2 * fl }, { p: S.world(300, 650, D.page), r: 6, c: [0.5, 0.55, 1.0], k: 0.25 }];
      lightsOn(planes.page, L); lightsOn(planes.desk, L.map((l) => ({ ...l, p: S.world(LAMP[0], LAMP[1], D.desk) })));
      // the lamp is just out of frame top right: its warm spill, and a moving glint along the gold rule
      const p = F.P(D.page, LAMP[0], LAMP[1]); glowAt(gg, p[0], p[1], 420, 0.09 * fl, [255, 160, 80]);
      const gx = F.P(D.page, 160 + ((t * 9) % 960), 74); glowAt(gg, gx[0], gx[1], 26, 0.18, [255, 220, 140]);
      motes(gg, t, { x0: 700, y0: 40, x1: 1280, y1: 600 }, { n: 22, col: [255, 214, 160], a: 0.35, size: 1.1, seed: 41, drift: [-3, 2] });
      // the text sits on a quiet page: a soft vignette dims the gilding under the overlay
      F.amb = [0.95, 0.95, 1.0]; F.bloom = 0.42; F.hal = 0.2;
    },
  };
}
