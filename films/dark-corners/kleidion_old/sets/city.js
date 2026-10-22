// SET city: Constantinople at dusk, Byzantine purple and gold. A terrace in the foreground (Basil, banners), the sea walls with
// lanterns, the domed skyline, a gold afterglow. Used for the emperor, the city wide, the nickname and the time-lapse.
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, igniteEnv, flick, tintAll, lightsOn, nn } from './common.js';
import { paintSky, paintRange, pineTree, paintFog, paintHouse, paintTufts } from '../paint.js';
import { person, banner, glowAt, embers, hash1, PAL } from '../figs.js';

const DOMES = { cx: 410, base: 905 };
function dome(C, cx, yb, rx, ry, col, lit, ribs = 10) {
  const g = C.g; const p = new Path2D(); p.ellipse(cx, yb, rx, ry, 0, Math.PI, 2 * Math.PI); p.closePath();
  const gr = g.createLinearGradient(cx - rx, yb - ry, cx + rx * 0.7, yb); gr.addColorStop(0, rgba(lit)); gr.addColorStop(0.35, rgba(mixc(lit, col, 0.6))); gr.addColorStop(1, rgba(col)); g.fillStyle = gr; g.fill(p);
  g.save(); g.clip(p); g.strokeStyle = rgba(mul(col, 0.7), 0.5); g.lineWidth = Math.max(1, rx * 0.012); for (let i = 1; i < ribs; i++) { const a = Math.PI + (i / ribs) * Math.PI; g.beginPath(); g.moveTo(cx, yb - ry * 1.1); g.quadraticCurveTo(cx + Math.cos(a) * rx * 0.9, yb - ry * 0.7 + Math.sin(a) * ry * 0.2, cx + Math.cos(a) * rx, yb); g.stroke(); } g.restore();
  g.strokeStyle = rgba(lit, 0.9); g.lineWidth = Math.max(1.2, rx * 0.02); g.beginPath(); g.ellipse(cx, yb, rx, ry, 0, Math.PI * 1.02, Math.PI * 1.42); g.stroke();
}
function hagiaSophia(C, cx, yb, s, col, lit, win) {
  const g = C.g, R = C.R; const body = mul(col, 1.0);
  // buttress masses and walls
  const W = 240 * s, Hh = 80 * s; g.fillStyle = rgba(body); g.fillRect(cx - W / 2, yb - Hh, W, Hh + 2);
  const wallGr = g.createLinearGradient(cx - W / 2, 0, cx + W / 2, 0); wallGr.addColorStop(0, rgba(mixc(body, lit, 0.35), 0.8)); wallGr.addColorStop(1, rgba(body, 0)); g.fillStyle = wallGr; g.fillRect(cx - W / 2, yb - Hh, W, Hh);
  for (const sx of [-1, 1]) { g.fillStyle = rgba(mul(body, 0.92)); g.fillRect(cx + sx * W * 0.5 - 14 * s * (sx > 0 ? 0 : 1) - (sx > 0 ? 0 : 0), yb - Hh * 1.25, 30 * s, Hh * 1.25); }
  // semi-domes and main dome
  dome(C, cx - 78 * s, yb - Hh, 86 * s, 54 * s, body, lit, 7); dome(C, cx + 78 * s, yb - Hh, 86 * s, 54 * s, body, mixc(lit, body, 0.5), 7);
  g.fillStyle = rgba(body); g.fillRect(cx - 62 * s, yb - Hh - 34 * s, 124 * s, 36 * s);
  dome(C, cx, yb - Hh - 30 * s, 66 * s, 62 * s, body, lit, 14);
  // drum windows (lit later by glows)
  const wins = []; for (let i = 0; i < 9; i++) { const x = cx - 54 * s + i * 13.5 * s; g.fillStyle = rgba(hex('#2a1a30')); g.fillRect(x, yb - Hh - 28 * s, 5 * s, 14 * s); wins.push([x, yb - Hh - 28 * s, 5 * s, 14 * s]); }
  for (let i = 0; i < 5; i++) { const x = cx - 95 * s + i * 45 * s; g.fillStyle = rgba(hex('#2a1a30')); g.fillRect(x, yb - Hh * 0.8, 6 * s, 20 * s); wins.push([x, yb - Hh * 0.8, 6 * s, 20 * s]); }
  // cross on the summit
  const ty = yb - Hh - 30 * s - 62 * s; g.fillStyle = rgba(PAL.gold); g.fillRect(cx - 1.3 * s, ty - 18 * s, 2.6 * s, 20 * s); g.fillRect(cx - 7 * s, ty - 12 * s, 14 * s, 2.6 * s);
  // corner turrets (stepped, conical caps)
  for (const sx of [-1, 1]) { const x = cx + sx * (W / 2 + 12 * s); g.fillStyle = rgba(mul(body, 0.95)); g.fillRect(x - 11 * s, yb - Hh * 1.6, 22 * s, Hh * 1.6); g.beginPath(); g.moveTo(x - 14 * s, yb - Hh * 1.6); g.lineTo(x, yb - Hh * 1.6 - 26 * s); g.lineTo(x + 14 * s, yb - Hh * 1.6); g.closePath(); g.fill(); }
  return wins;
}
function seaWall(C, x0, x1, yTop, yBase, col, lit, towers) {
  const g = C.g, R = C.R; g.fillStyle = rgba(col); g.fillRect(x0, yTop, x1 - x0, yBase - yTop);
  C.strokes({ n: (x1 - x0) * (yBase - yTop) / 140, box: [x0, yTop, x1, yBase], color: (x, y) => mixc(col, lit, 0.25 * smoothstep(yBase, yTop, y) * R()), angle: () => (R() - 0.5) * 0.1, len: [10, 26], wid: [3, 6], alpha: [0.4, 0.8], jv: 0.08, bend: 0.03 });
  for (let x = x0; x < x1; x += 14) { g.fillStyle = rgba(mul(col, 0.9)); g.fillRect(x, yTop - 9, 8, 10); } // crenellations
  for (let y = yTop + 14; y < yBase; y += 10) { g.fillStyle = rgba(mul(col, 0.82), 0.4); for (let x = x0 + (y % 20); x < x1; x += 22) g.fillRect(x, y, 14, 2); }
  const tw = [];
  for (const t of towers) { const w = t.w, h = t.h; g.fillStyle = rgba(mul(col, 0.95)); g.fillRect(t.x - w / 2, yTop - h, w, h + (yBase - yTop)); g.fillStyle = rgba(mixc(col, lit, 0.4), 0.7); g.fillRect(t.x - w / 2, yTop - h, 4, h + (yBase - yTop));
    for (let x = t.x - w / 2; x < t.x + w / 2; x += 11) { g.fillStyle = rgba(mul(col, 0.9)); g.fillRect(x, yTop - h - 10, 7, 11); }
    g.fillStyle = rgba(hex('#1d1230')); g.fillRect(t.x - 3, yTop - h * 0.7, 6, 16); tw.push({ x: t.x, y: yTop - h * 0.62 }); }
  return tw;
}

export default function city(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, hills: 3000, city: 500, wall: 250, water: 140, terrace: 30 }; const planes = {}; const gl = { lamps: [], wins: [] };
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 611 });
    paintSky(C, { stops: [[-600, hex('#140c30')], [0, hex('#24143f')], [260, hex('#4c2a66')], [480, hex('#8a4a78')], [650, hex('#d1785f')], [760, hex('#f2b062')], [820, hex('#f7c97a')]], glow: { x: 400, y: 800, rx: 520, ry: 300, col: hex('#ffd58a'), a: 0.85 },
      clouds: [{ y: 360, h: 14, x0: -300, x1: 1100, col: hex('#3a2058'), lit: hex('#d98d7a'), litA: 0.75, sy: 0.03 }, { y: 520, h: 12, x0: -200, x1: 1100, col: hex('#5a3068'), lit: hex('#f2a468'), litA: 0.85, thr: 0.5, sy: 0.034 }, { y: 660, h: 10, x0: -100, x1: 900, col: hex('#7a3e70'), lit: hex('#ffc47a'), litA: 0.9, thr: 0.5, sy: 0.04 }, { y: 150, h: 16, x0: -300, x1: 1000, col: hex('#1b0f38'), lit: hex('#4a2a66'), litA: 0.6, sy: 0.026 }] });
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.hills); r[1] = Math.max(r[1], 640); r[3] = Math.min(r[3], 900); const C = new Canvas(r, { seed: 621 });
    paintRange(C, { ridge: (x) => 800 - bump(x, 100, 200, 22) - bump(x, 700, 180, 28) - 8 * ridged(x * 0.01, 3, 2), top: hex('#6b4778'), mid: hex('#5a3c6c'), base: hex('#4c3260'), fall: 80, light: { dir: -1, col: hex('#9a6a80'), amt: 0.3 }, shade: 0.1, haze: { col: hex('#a86a78'), y0: 800, y1: 880, a: 0.7 } });
    C.mottle({ amt: 0.05 }); planes.hills = S.plane('hills', D.hills, r, C.c); }
  { const r = cover(D.city, 30); r[1] = Math.max(r[1], 480); r[3] = Math.min(r[3], 1010); const C = new Canvas(r, { seed: 631 }); const R = rng(6311); const g = C.g;
    // the hill the city climbs: a mass behind the roofs
    const ground = (x) => 905 - 60 * smoothstep(-100, 500, x) * (1 - smoothstep(500, 900, x)) - 14 * smoothstep(560, 900, x) + det(x, 8, 3, 4);
    paintRange(C, { ridge: (x) => ground(x) - 24, top: hex('#46305e'), mid: hex('#3a2850'), base: hex('#2c1e42'), fall: 120, light: { dir: -1, col: hex('#7a5478'), amt: 0.4 }, shade: 0.12, rim: hex('#c98a78') });
    const wins = [];
    // houses in clusters on the hillside, tiers of roofs
    for (const [yb, x0, x1, w0, w1, h0, h1] of [[ground(0) - 4, -60, 800, 16, 28, 10, 18], [ground(0) + 22, -60, 800, 20, 34, 12, 20], [ground(0) + 46, -60, 800, 24, 38, 14, 22]]) {
      let x = x0; while (x < x1) { const w = lerp(w0, w1, R()); const base = yb + (ground(x) - ground(0)) * 1.0 + (R() - 0.5) * 4; if (Math.abs(x - DOMES.cx) > 170 || yb > ground(0) + 10) { const hh = paintHouse(C, x + w / 2, base, w, lerp(h0, h1, R()), { wall: hex('#4a3860'), roof: hex('#2a1c3e'), crest: hex('#8a5a74'), win: hex('#1c1230'), roofK: 0.4 + R() * 0.2, gable: R() < 0.3, sideShade: R() < 0.5 ? 1 : -1, litLeft: 0.2 }); for (const w2 of hh.windows) wins.push(w2); } x += w * (0.8 + R() * 0.5); } }
    // the great church, centre
    const gw = hagiaSophia(C, DOMES.cx, ground(DOMES.cx) + 6, 1.18, hex('#3b2a56'), hex('#d49a82'), null); gw.forEach((w) => wins.push(w));
    // lesser domes and a column
    dome(C, 150, ground(150) + 4, 30, 26, hex('#3b2a56'), hex('#c98a78'), 8); g.fillStyle = rgba(hex('#3b2a56')); g.fillRect(120, ground(150) - 18, 60, 22);
    dome(C, 660, ground(660) + 2, 34, 28, hex('#3b2a56'), hex('#c98a78'), 8); g.fillRect(626, ground(660) - 18, 68, 22);
    g.fillStyle = rgba(hex('#3b2a56')); g.fillRect(574, ground(574) - 74, 8, 78); g.fillRect(569, ground(574) - 82, 18, 10);
    // cypresses
    for (let i = 0; i < 26; i++) { const x = lerp(-40, 780, R()); if (Math.abs(x - DOMES.cx) < 130) continue; const yb = ground(x) + 10 + R() * 40; const h = 24 + R() * 34; g.fillStyle = rgba(hex('#1d1530')); g.beginPath(); g.moveTo(x - 3, yb); g.quadraticCurveTo(x - 5.5, yb - h * 0.6, x, yb - h); g.quadraticCurveTo(x + 5.5, yb - h * 0.6, x + 3, yb); g.fill(); }
    C.mottle({ amt: 0.05 }); planes.city = S.plane('city', D.city, r, C.c);
    gl.wins = wins.filter(() => R() < 0.8).map((w) => [w[0] + w[2] / 2, w[1] + w[3] / 2, w[2], w[3], R()]); gl.cityPlane = planes.city; }
  { const r = cover(D.wall, 40); r[1] = Math.max(r[1], 780); r[3] = Math.min(r[3], 1060); const C = new Canvas(r, { seed: 641 });
    const towers = [{ x: 60, w: 50, h: 54 }, { x: 250, w: 54, h: 62 }, { x: 440, w: 52, h: 58 }, { x: 640, w: 56, h: 66 }, { x: 820, w: 50, h: 54 }, { x: -130, w: 50, h: 56 }];
    const tw = seaWall(C, r[0] - 10, r[2] + 10, 950, 1002, hex('#4a3662'), hex('#d49a82'), towers); gl.towers = tw; C.mottle({ amt: 0.05 }); planes.wall = S.plane('wall', D.wall, r, C.c); }
  { const r = cover(D.water, 40); r[1] = Math.max(r[1], 960); const C = new Canvas(r, { seed: 651 }); const g = C.g; const R = rng(6511);
    const wc = (x, y) => mixc(mixc(hex('#241a44'), hex('#18102e'), smoothstep(1000, 1300, y)), hex('#e0a070'), 0.42 * Math.exp(-(((x - 400) / 140) ** 2)) * smoothstep(1100, 990, y));
    underpaint(C, wc, null, 6);
    C.strokes({ n: C.area / 380, color: wc, angle: () => (C.R() - 0.5) * 0.06, len: [24, 90], wid: [2, 5], alpha: [0.4, 0.8], jv: 0.08, bend: 0.02 });
    for (let i = 0; i < 260; i++) { const x = lerp(r[0], r[2], R()), y = lerp(1000, 1300, Math.pow(R(), 0.8)); const gold = Math.exp(-(((x - 400) / 150) ** 2)); if (R() > 0.15 + gold) continue; C.dab(x, y, (R() - 0.5) * 0.05, 14 + R() * 40, 1.6 + R() * 2.2, mixc(hex('#c88a78'), hex('#ffd08a'), R() * gold), 0.5 + 0.3 * gold, 0.02); }
    C.mottle({ amt: 0.05 }); planes.water = S.plane('water', D.water, r, C.c); }
  { const r = cover(D.terrace, 40); r[1] = Math.max(r[1], 960); const C = new Canvas(r, { seed: 661 }); const g = C.g; const R = rng(6611);
    // paved terrace in front, dark edge, a low balustrade run across the far lip
    const top = 1018; g.fillStyle = rgba(hex('#1a1230')); g.fillRect(r[0], top, r[2] - r[0], r[3] - top);
    underpaint(C, (x, y) => mixc(hex('#3a2a52'), hex('#171028'), smoothstep(top, top + 260, y)), (() => { const p = new Path2D(); p.rect(r[0], top + 24, r[2] - r[0], r[3] - top); return p; })(), 8);
    C.strokes({ n: C.area / 900, box: [r[0], top + 24, r[2], r[3]], color: (x, y) => mixc(hex('#3a2a52'), hex('#171028'), smoothstep(top, top + 260, y)), angle: () => (R() - 0.5) * 0.06, len: [20, 80], wid: [4, 9], alpha: [0.4, 0.8], jv: 0.08 });
    for (let y = top + 50; y < r[3]; y += 46 + (y - top) * 0.08) { g.strokeStyle = rgba(hex('#0f0a1c'), 0.6); g.lineWidth = 1.4; g.beginPath(); g.moveTo(r[0], y); g.lineTo(r[2], y); g.stroke(); }
    // balustrade: coping, balusters
    g.fillStyle = rgba(hex('#241838')); g.fillRect(r[0], top - 6, r[2] - r[0], 10); g.fillStyle = rgba(mixc(hex('#4a3662'), hex('#d49a82'), 0.5)); g.fillRect(r[0], top - 7, r[2] - r[0], 2.2);
    for (let x = r[0]; x < r[2]; x += 18) { g.fillStyle = rgba(hex('#1c1230')); g.beginPath(); g.moveTo(x, top + 24); g.quadraticCurveTo(x + 4, top + 12, x + 1.5, top + 4); g.lineTo(x + 7, top + 4); g.quadraticCurveTo(x + 4.5, top + 12, x + 9, top + 24); g.fill(); }
    g.fillStyle = rgba(hex('#241838')); g.fillRect(r[0], top + 24, r[2] - r[0], 8);
    // pedestals with lanterns at both ends
    for (const x of [90, 650]) { g.fillStyle = rgba(hex('#241838')); g.fillRect(x - 18, top - 62, 36, 90); g.fillStyle = rgba(hex('#4a3662'), 0.7); g.fillRect(x - 18, top - 62, 4, 90); g.fillRect(x - 22, top - 68, 44, 10); }
    C.mottle({ amt: 0.05 }); planes.terrace = S.plane('terrace', D.terrace, r, C.c); }
  // glows: towers, windows
  const S_ = S; const towerGlows = gl.towers.map((t) => S_.glow(t.x, t.y, D.wall, 34, { color: [1.0, 0.6, 0.27], core: 90 }, planes.wall));
  const winGlows = gl.wins.map((w) => { const m = Math.max(w[2], w[3]) * 3; return S_.glow(w[0], w[1], D.city, m, { color: [1.0, 0.62, 0.3], shape: 1, rect: [w[2] / m, w[3] / m] }, planes.city); });
  tintAll(S, 1);
  const BASIL = { x: 520, y: 1112, h: 330 };
  return {
    planes, D,
    update(F) {
      const t = F.t, lt = F.lt, sh = F.shot, g = F.g, S_ = F.S;
      // time of day: dusk by default; 'cycle' drives a time-lapse (light swings from gold to blue night and back)
      let day = sh.day ?? 1; let nightK = 0;
      if (sh.cycle) { const c = sh.cycle; const ph = (t - c.t0) / (c.t1 - c.t0); nightK = 0.5 - 0.5 * Math.cos(ph * Math.PI * 2 * c.n); day = 1 - 0.72 * nightK; }
      tintAll(S_, day, [1 - 0.55 * nightK * 0.8, 1 - 0.3 * nightK * 0.5, 1 + 0.1 * nightK]);
      const lampT = sh.lamps || []; const lampOn = (i) => (sh.lampsAll ? 1 : igniteEnv(t, lampT[i] ?? 1e9, i + 1)) * (1 + 0.0);
      towerGlows.forEach((gm, i) => { const on = clamp(lampOn(i % Math.max(1, lampT.length || 6)), 0, 1.5) * (sh.lampsAll ? 1 : 1); gm.visible = on > 0.01; gm.material.uniforms.uI.value = 1.5 * on * (1 + 0.2 * nightK); });
      const winAmt = sh.windows ?? 0.5 + nightK * 0.6; winGlows.forEach((gm, i) => { const w = gl.wins[i]; const on = smoothstep(w[4] * 0.9, w[4] * 0.9 + 0.15, winAmt + (sh.lampsAll ? 0.5 : 0)); gm.visible = on > 0.01; gm.material.uniforms.uI.value = 0.9 * on * flick(t, i * 1.7); });
      // lamp light on the wall and the water
      const lights = []; gl.towers.forEach((tw, i) => { const on = towerGlows[i].visible ? towerGlows[i].material.uniforms.uI.value / 1.5 : 0; lights.push({ p: S_.world(tw.x, tw.y, D.wall), r: 20 * D.wall / S_.f * 9, c: WARM, k: 2.2 * on }); });
      lightsOn(planes.wall, lights.filter((l) => l.k > 0.01).slice(0, 8));
      // Basil on the terrace, banners at the posts
      if (sh.basil !== false) {
        const bs = BASIL; const q = F.P(D.terrace, bs.x, bs.y), K = F.K(D.terrace, bs.x, bs.y); const h = bs.h * K;
        const sun = F.P(D.sky, 400, 800);
        // the banners (two poles on the terrace)
        for (const [bx, by, bh, dirb, seed] of [[150, 1100, 560, 1, 1], [660, 1096, 520, -1, 2]]) { const p = F.P(D.terrace, bx, by); banner(g, { x: p[0], y: p[1], h: bh * K, w: 190 * K, t, dir: dirb, seed, amp: 0.1 }); }
        if (!sh.noBasil) person(g, { x: q[0], y: q[1], h, face: -1, ph: 0, walk: 0, col: hex('#3a1e56'), col2: hex('#5a2f82'), dark: hex('#1c1030'), hood: false, crown: true, cape: hex('#4b2468'), head: 0.04 + 0.01 * Math.sin(t * 0.8), hem: 0.06, skinCol: hex('#241633'), lantern: null, reach: [0.02, 0.5], warm: { x: sun[0], y: sun[1] - 50 * K, r: 520 * K, a: 0.22 } });
      }
      if (sh.cloth) this.cloth && this.cloth(F);
      const gg = F.glow(); const sunp = F.P(D.sky, 400, 800); glowAt(gg, sunp[0], sunp[1] - 40, 420 * Math.max(1, F.K(D.sky)), 0.10 + 0.08 * (1 - nightK), [255, 190, 110]);
      for (let i = 0; i < towerGlows.length; i++) { const tw = gl.towers[i]; const on = towerGlows[i].visible ? 1 : 0; if (!on) continue; const p = F.P(D.wall, tw.x, tw.y + 120); const k = F.K(D.wall, tw.x, tw.y); glowAt(gg, p[0], p[1], 8 * k + 6, 0.35 * Math.min(1, towerGlows[i].material.uniforms.uI.value / 1.5), [255, 170, 90]); }
      embers(gg, t, { x0: 0, y0: 500, x1: 720, y1: 1200 }, 18, { size: 1.2, col: [255, 210, 150], a: 0.35, wind: 6, rise: 0.3, seed: 3 });
      F.amb = [0.95 * day + 0.05, 0.9 * day + 0.08, 1.0 * day + 0.1]; F.bloom = 0.55;
    },
  };
}
