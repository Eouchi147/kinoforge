// SET gorge: a narrow canyon in the Balkans, seen along its floor. Used for the ambush that nearly caught Basil and for the governor
// trapped and killed (shown only as dust, falling stones and a banner that lies still).
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, igniteEnv, flick, fireFlick, tintAll, lightsOn, paintCliff } from './common.js';
import { paintSky, paintRange, pineTree, paintTufts, paintRocks } from '../paint.js';
import { person, horse, banner, glowAt, embers, hash1, PAL } from '../figs.js';

const fh = (y) => 120 + (y - 560) * 0.46;               // half width of the floor at row y
const hg = (y) => 3.3 * (7 + (y - 560) * 0.03);        // person height at row y

export default function gorge(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, far: 700, cliffB: 300, floor: 160, cliffA: 100, fg: 45 }; const planes = {};
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 911 });
    paintSky(C, { stops: [[-500, hex('#1c1a42')], [0, hex('#2e2a58')], [200, hex('#6a4e72')], [350, hex('#d29070')], [450, hex('#f5c47a')], [560, hex('#ffd88c')]], glow: { x: 360, y: 430, rx: 380, ry: 300, col: hex('#ffdf9a'), a: 0.95 },
      clouds: [{ y: 150, h: 12, x0: -200, x1: 900, col: hex('#4a3a66'), lit: hex('#e29a78'), litA: 0.8, sy: 0.034, thr: 0.5 }] });
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.far); r[1] = Math.max(r[1], 200); r[3] = Math.min(r[3], 640); const C = new Canvas(r, { seed: 921 });
    paintRange(C, { ridge: (x) => 470 - bump(x, 360, 130, 90) - 18 * ridged(x * 0.01, 3, 4), top: hex('#9a7080'), mid: hex('#7a5a70'), base: hex('#5a4464'), fall: 150, light: { dir: -1, col: hex('#d09a80'), amt: 0.4 }, haze: { col: hex('#d8a080'), y0: 470, y1: 600, a: 0.8 }, rim: hex('#f0c090') });
    C.mottle({ amt: 0.05 }); planes.far = S.plane('far', D.far, r, C.c); }
  { const r = cover(D.cliffB, 30); const C = new Canvas(r, { seed: 931 }); const eL = (y) => 228 - 30 * smoothstep(560, 1100, y) + 20 * smoothstep(300, -300, y) + det(y, 10, 4, 3), eR = (y) => 492 + 30 * smoothstep(560, 1100, y) - 20 * smoothstep(300, -300, y) + det(y, 10, 4, 4);
    paintCliff(C, { edge: eL, side: 'L', base: hex('#2a2030'), mid: hex('#4a3a48'), rim: hex('#f0b080'), lit: hex('#7a5a60') }); paintCliff(C, { edge: eR, side: 'R', base: hex('#241c2c'), mid: hex('#413443'), rim: hex('#f0b080'), lit: hex('#6a5058') });
    C.mottle({ amt: 0.05 }); planes.cliffB = S.plane('cliffB', D.cliffB, r, C.c); }
  { const r = cover(D.floor, 40); r[1] = Math.max(r[1], 540); const C = new Canvas(r, { seed: 941 }); const R = rng(9411);
    const path = new Path2D(); path.moveTo(360 - fh(560), 560); path.lineTo(360 + fh(560), 560); for (let y = 560; y <= r[3] + 30; y += 20) path.lineTo(360 + fh(y), y); for (let y = r[3] + 30; y >= 560; y -= 20) path.lineTo(360 - fh(y), y); path.closePath();
    const fc = (x, y) => mixc(mixc(hex('#6a5248'), hex('#3e3038'), smoothstep(560, 1100, y)), hex('#d0a070'), 0.5 * smoothstep(700, 560, y) * Math.exp(-(((x - 360) / 120) ** 2)));
    underpaint(C, fc, path, 6); C.strokes({ n: C.area / 800, mask: C.mask((g) => g.fill(path)), color: fc, angle: () => (R() - 0.5) * 0.3, len: [14, 46], wid: [4, 10], alpha: [0.45, 0.8], jv: 0.08 });
    for (let i = 0; i < 200; i++) { const y = lerp(566, 1300, Math.pow(R(), 0.9)), x = 360 + (R() - 0.5) * 2 * fh(y); const s = 2 + (y - 560) * 0.012 * (0.5 + R()); C.dab(x, y, (R() - 0.5) * 0.4, s * 2.2, s, mixc(hex('#2e222a'), hex('#8a6a58'), R()), 0.7, 0.2); }
    { const g = C.g; g.save(); g.clip(path); const gr = g.createLinearGradient(0, 556, 0, 720); gr.addColorStop(0, 'rgba(236,190,130,0.95)'); gr.addColorStop(1, 'rgba(236,190,130,0)'); g.fillStyle = gr; g.fillRect(0, 556, 720, 170); g.restore(); g.save(); g.globalCompositeOperation = 'destination-out'; const g2 = g.createLinearGradient(0, 550, 0, 650); g2.addColorStop(0, 'rgba(0,0,0,1)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = g2; g.fillRect(0, 540, 720, 112); g.restore(); }
    C.mottle({ amt: 0.06 }); planes.floor = S.plane('floor', D.floor, r, C.c); }
  { const r = cover(D.cliffA, 40); const C = new Canvas(r, { seed: 951 });
    paintCliff(C, { edge: (y) => 150 - 190 * smoothstep(560, 1350, y) + 40 * smoothstep(420, -300, y) + det(y, 14, 6, 5), side: 'L', base: hex('#17111c'), mid: hex('#2a2030'), rim: hex('#f0a870'), lit: hex('#5a4048') });
    paintCliff(C, { edge: (y) => 570 + 190 * smoothstep(560, 1350, y) - 40 * smoothstep(420, -300, y) + det(y, 14, 6, 6), side: 'R', base: hex('#140f19'), mid: hex('#261c2c'), rim: hex('#f0a870'), lit: hex('#4a343e') });
    C.mottle({ amt: 0.05 }); planes.cliffA = S.plane('cliffA', D.cliffA, r, C.c); }
  { const r = cover(D.fg, 40); r[1] = Math.max(r[1], 1050); const C = new Canvas(r, { seed: 961 });
    paintRocks(C, { rocks: [{ x: 0, y: 1300, rx: 220, ry: 100 }, { x: 740, y: 1310, rx: 240, ry: 110 }], col: hex('#08060c'), lit: hex('#2c2030'), litA: 0.4, blur: 3 }); planes.fg = S.plane('fg', D.fg, r, C.c); }
  tintAll(S, 1);
  const rock = (g, x, y, s, a, col) => { g.save(); g.translate(x, y); g.rotate(a); g.fillStyle = rgba(col); g.beginPath(); for (let i = 0; i < 8; i++) { const an = i / 8 * Math.PI * 2; const r = s * (0.75 + 0.35 * hash1(i * 3.1 + x)); i ? g.lineTo(Math.cos(an) * r, Math.sin(an) * r) : g.moveTo(Math.cos(an) * r, Math.sin(an) * r); } g.closePath(); g.fill(); g.fillStyle = rgba([255, 190, 130], 0.25); g.beginPath(); g.arc(-s * 0.3, -s * 0.3, s * 0.35, 0, 7); g.fill(); g.restore(); };
  return {
    planes, D,
    update(F) {
      const t = F.t, sh = F.shot, g = F.g, S_ = F.S; const gg = F.glow(); const day = sh.day ?? 1; tintAll(S_, day, [1, 0.97, 1]);
      const pf = (x, y) => F.P(D.floor, x, y), kf = (x, y) => F.K(D.floor, x, y);
      const hit = (arr, t0, t1) => arr.filter((h) => t >= h && t < h + 3);
      const mode = sh.mode; const items = [];
      // dust under the beat
      const hits = sh.hits || [];
      if (mode === 'ride') {
        // Byzantine riders ride up the gorge; stones come off the rim; a purple cloak turns back
        const n = sh.riders ?? 7; const u0 = t - sh.t0; for (let k = n - 1; k >= 0; k--) { const back = sh.flee ? 1 : 0; let y, x, face = 1, gait;
          if (!sh.flee) { y = 1140 - k * 70 - u0 * 34; x = 360 + ((k % 2) - 0.5) * 80 * (1 + (y - 560) / 400); face = -1; gait = u0 * 1.2 + k * 0.3; }
          else { const lead = k === 0; const s = u0 * 1.0; y = lead ? lerp(640, 1250, ease.inQuad(clamp(s / (sh.dur * 0.95)))) : lerp(560, 760, clamp(s * 0.2)) + k * 14; x = lead ? 360 + 20 * Math.sin(s * 3) : 360 + (k % 2 ? 1 : -1) * (40 + k * 20); face = lead ? 1 : -1; gait = u0 * 2.6 + k * 0.2; if (!lead) { x += 0; } }
          items.push({ y, fn: () => { const p = pf(x, y), K = kf(x, y); const hh = hg(y) * 0.88 * K; if (hh < 3) return; const hs = horse(g, { x: p[0], y: p[1], h: hh, face: sh.flee && k === 0 ? 1 : (face > 0 ? 1 : -1), ph: gait, gallop: sh.flee && k === 0 ? 1 : 0.35, col: hex(k % 2 ? '#1c1626' : '#20182a') });
            person(g, { x: hs.saddle[0], y: hs.saddle[1] + 0.5 * hh * 1.15, h: hh * 1.15, face: sh.flee && k === 0 ? 1 : (face > 0 ? 1 : -1), walk: 0, noLegs: true, col: k === 0 && sh.flee ? hex('#4b2468') : hex('#241a30'), col2: hex('#3a2848'), dark: hex('#140e1c'), hood: false, skinCol: hex('#140e1c'), hem: 0.25, cape: k === 0 && sh.flee ? hex('#6a3a8a') : null, head: 0, reach: [0.22, 0.62] }); } }); }
        items.sort((a, b) => a.y - b.y); items.forEach((o) => o.fn());
      }
      // falling stones with dust
      for (const h0 of hits) { const u = t - h0; if (u < -0.2 || u > 3) continue; const side = (Math.round(h0 * 10) % 2) ? 1 : -1; const nR = 4;
        for (let k = 0; k < nR; k++) { const sx = 360 + side * (170 + 30 * hash1(h0 + k)) + (hash1(h0 * 3 + k) - 0.5) * 60; const ty = 560 + 280 * hash1(h0 * 7 + k) + 60; const fall = clamp((u - k * 0.06) / (0.5 + 0.2 * k * 0.3)); if (fall <= 0) continue;
          const a = F.P(D.cliffA, sx + side * 40, 120 - 100 * hash1(k)), b = F.P(D.floor, sx - side * 30, ty); const px_ = lerp(a[0], b[0], fall), py_ = lerp(a[1], b[1], fall * fall); if (fall < 1) rock(g, px_, py_, (10 + 8 * hash1(k * 2 + h0)) * F.K(D.floor, 360, 800), u * 9 + k, hex('#2a2028')); }
        const d = Math.exp(-u * 0.8) * smoothstep(0, 0.25, u); const c = F.P(D.floor, 360 + side * 70, 700 + 100 * hash1(h0)); const kk = F.K(D.floor, 360, 700); glowAt(gg, c[0], c[1], (130 + 90 * Math.min(u, 2)) * kk * 1.5, 0.42 * d, [240, 190, 130]); }
      if (mode === 'column') {
        // the governor's men, a purple banner, as the stones come down: dust covers them; the banner leans and lies still
        const n = sh.men ?? 9; const items2 = []; const fall = sh.fallAt ? smoothstep(sh.fallAt, sh.fallAt + 1.4, t) : 0; const u0 = t - sh.t0;
        for (let k = 0; k < n; k++) { const y = 1000 - k * 52 - Math.min(u0, 2.5) * 20 * (1 - fall); const x = 360 + ((k * 37) % 5 - 2) * 26; items2.push({ y, fn: () => { const p = pf(x, y), K = kf(x, y); const hh = hg(y) * K; person(g, { x: p[0], y: p[1], h: hh, face: -1, ph: u0 * 1.1 + k * 0.4, walk: (1 - fall) * 0.9, col: hex('#241a30'), col2: hex('#3a2848'), hood: false, skinCol: hex('#140e1c'), staff: true, hem: 0.3, stride: 0.9 });
          if (k === 2) { const rot = fall * 1.35; g.save(); g.translate(p[0], p[1] - hh * 0.05); g.rotate(rot); banner(g, { x: 0, y: 0, h: hh * 2.5, w: hh * 0.9, t: t * (1 - fall), dir: -1, seed: 4, amp: 0.12 * (1 - fall) }); g.restore(); } } }); }
        items2.sort((a, b) => a.y - b.y).forEach((o) => o.fn());
      }
      // dust veil at the floor, always a little
      const vp = F.P(D.floor, 360, 640); glowAt(gg, vp[0], vp[1], 320 * F.K(D.floor, 360, 640), 0.12 * day, [250, 200, 130]);
      if (sh.embers !== false) embers(gg, t, { x0: 100, y0: 300, x1: 620, y1: 1000 }, 22, { size: 1.2, col: [255, 220, 160], a: 0.4, wind: 6, rise: 0.3, seed: 12 });
      F.amb = [0.95 * day + 0.05, 0.9 * day + 0.05, 0.95 * day + 0.08]; F.bloom = 0.5;
    },
  };
}
