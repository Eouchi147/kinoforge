// SET page: the chroniclers' manuscripts on a dark desk by candlelight. Two parchment sheets (Skylitzes above, Kekaumenos below),
// ink written in the detail layer (revealed by time), candle flames that relight the paper, dust motes in the beam.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, igniteEnv, fireFlick, tintAll, lightsOn, nn, nn2 } from './common.js';
import { glowAt, embers, hash1 } from '../figs.js';
import { smoke, motes } from '../ambient.js';

export function paintDesk(C, { dark = 1, planks = 7, y0 = null } = {}) {
  const [x0, y0_, x1, y1] = C.rect; const g = C.g; const R = C.R;
  g.fillStyle = rgba(hex('#1a120f')); g.fillRect(x0, y0_, x1 - x0, y1 - y0_);
  const ph = 190; // plank height, running horizontally
  for (let y = Math.floor(y0_ / ph) * ph; y < y1; y += ph) { const k = Math.round(y / ph); const sh = mixc(hex('#3a2a20'), hex('#2a1d16'), (nn2(k * 3.1, 2.2)));
    underpaint(C, (x, yy) => mul(sh, 0.8 + 0.5 * (nn.fbm(x * 0.004, yy * 0.02 + k * 7, 3) - 0.3)), (() => { const p = new Path2D(); p.rect(x0, y + 3, x1 - x0, ph - 6); return p; })(), 10);
    C.strokes({ n: (x1 - x0) * ph / 320, box: [x0, y, x1, y + ph], color: (x, yy) => mul(sh, 0.7 + 0.55 * nn.fbm(x * 0.003, yy * 0.03 + k * 5, 3)), angle: () => (R() - 0.5) * 0.02, len: [60, 220], wid: [2, 5], alpha: [0.4, 0.8], jv: 0.1, bend: 0.01, taper: 0.5 });
    g.fillStyle = rgba(hex('#0a0605'), 0.9); g.fillRect(x0, y - 1.5, x1 - x0, 3.5); // plank gap
    for (let i = 0; i < 3; i++) { const kx = lerp(x0, x1, R()), ky = y + ph * (0.2 + 0.6 * R()); g.strokeStyle = rgba(hex('#120b08'), 0.6); g.lineWidth = 1.5; g.beginPath(); g.ellipse(kx, ky, 12 + R() * 14, 4 + R() * 3, 0, 0, 7); g.stroke(); }
  }
  C.mottle({ amt: 0.12, cell: 30 });
}
// a parchment sheet painted in local coordinates (0..w, 0..h); returns the canvas
export function paintSheet(w, h, seed, q = 1.4) {
  const C = new Canvas([0, 0, w, h], { q, seed }); const g = C.g, R = C.R; const n = C.n;
  const edge = (x, y) => { const m = Math.min(x, w - x, y, h - y); return m; };
  const path = new Path2D(); const pts = []; const N = 120; const wob = (t) => (n.fbm(t * 5 + seed, 1.7, 3) - 0.5) * 7;
  for (let i = 0; i <= N; i++) { const u = i / N; pts.push([u * w, wob(u) + 3]); } for (let i = 1; i <= N; i++) { const u = i / N; pts.push([w - 3 - wob(u + 3), u * h]); } for (let i = 1; i <= N; i++) { const u = i / N; pts.push([w - u * w, h - 3 - wob(u + 5)]); } for (let i = 1; i < N; i++) { const u = i / N; pts.push([3 + wob(u + 7), h - u * h]); }
  pts.forEach(([x, y], i) => i ? path.lineTo(x, y) : path.moveTo(x, y)); path.closePath();
  const base = (x, y) => { const e = smoothstep(0, 70, edge(x, y)); const stain = smoothstep(0.55, 0.8, n.fbm(x * 0.006, y * 0.006, 4)); return mixc(mixc(hex('#a98d5c'), hex('#cdb482'), 0.5 + 0.5 * n.fbm(x * 0.004 + 3, y * 0.004, 3)), mixc(hex('#7b5f3a'), hex('#5e472c'), e), (1 - e) * 0.75 + stain * 0.25); };
  underpaint(C, base, path, 6); const m = C.mask((gg) => gg.fill(path));
  C.strokes({ n: w * h / 420, mask: m, color: base, angle: () => (R() - 0.5) * 3, len: [8, 36], wid: [3, 8], alpha: [0.2, 0.45], jv: 0.07, bend: 0.3 });
  C.strokes({ n: w * h / 3000, mask: m, color: () => hex('#6c5230'), angle: () => R() * 6.28, len: [4, 14], wid: [0.8, 1.6], alpha: [0.25, 0.5], jv: 0.1, bend: 0.4 }); // fibres
  // ruling lines, very faint
  g.strokeStyle = 'rgba(70,50,28,0.16)'; g.lineWidth = 1; for (let y = 70; y < h - 40; y += 34) { g.beginPath(); g.moveTo(42, y); g.lineTo(w - 42, y); g.stroke(); }
  g.strokeStyle = 'rgba(70,50,28,0.2)'; g.beginPath(); g.moveTo(40, 40); g.lineTo(40, h - 40); g.moveTo(w - 40, 40); g.lineTo(w - 40, h - 40); g.stroke();
  C.mottle({ amt: 0.1, cell: 16 }); return C.c;
}

const SHEETS = { sky: { cx: 360, cy: 640, w: 560, h: 760, rot: -0.03, seed: 5101 }, kek: { cx: 372, cy: 1560, w: 560, h: 720, rot: 0.028, seed: 5102 } };
const PAGE_TEXT = {
  sky: { head: ['John Skylitzes, Synopsis of Histories', '(written decades after 1014):'], body: ['The emperor blinded the captives,', 'about fifteen thousand, as they say,', 'and sent them to Samuel.'], at: [93.7, 95.9, 96.8, 100.2, 100.5, 101.9], headAt: [93.5, 95.0], scrib: [10.95, 15.3], num: 'fifteen thousand', numLine: 1, underline: 98.2, strike: [140.388, 141.2] },
  kek: { head: ['Kekaumenos, Advice and Stories (1070s):'], body: ['the emperor Basil captured', 'fourteen thousand Bulgarians', 'at the barrier.'], at: [133.0, 134.9, 134.9, 137.0, 137.0, 138.0], headAt: [130.9, 132.4], scrib: [129.5, 132.2], num: 'fourteen thousand', numLine: 1, underline: 135.7, strike: [141.526, 142.4] },
};
const rev = (t, a, b) => clamp((t - a) / (b - a));

export default function page(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { desk: 10, sheet: 9.8 }; const planes = {};
  { const r = cover(D.desk, 60); const C = new Canvas(r, { seed: 5001 }); paintDesk(C); planes.desk = S.plane('desk', D.desk, r, C.c); }
  const sheetPl = {};
  for (const [k, s] of Object.entries(SHEETS)) { const c = paintSheet(s.w, s.h, s.seed); const pl = S.plane('sheet_' + k, D.sheet, [s.cx - s.w / 2, s.cy - s.h / 2, s.cx + s.w / 2, s.cy + s.h / 2], c); pl.rotation.z = -s.rot; sheetPl[k] = pl; planes['sheet_' + k] = pl; }
  tintAll(S, 0.3);
  const candles = [{ x: 690, y: 300 }, { x: 70, y: 1150 }, { x: 650, y: 1250 }];
  // script: pseudo-handwriting strokes along a line, revealed from the left
  const script = (g, x0, y, w, seed, prog, size = 14, a = 0.8) => {
    const R = rng(seed); g.save(); g.beginPath(); g.rect(x0 - 4, y - size * 2, w * prog + 4, size * 4); g.clip(); g.strokeStyle = `rgba(38,24,14,${a})`; g.lineWidth = 1.5; g.lineCap = 'round'; g.beginPath();
    let x = x0; while (x < x0 + w) { const wl = 18 + R() * 40; const gap = 6 + R() * 5; for (let k = 0; k < wl; k += 4 + R() * 3) { const hgt = size * (0.35 + R() * 0.65) * (R() < 0.2 ? 1.6 : 1); g.moveTo(x + k, y); g.quadraticCurveTo(x + k + 2, y - hgt, x + k + 4, y - hgt * 0.2); g.quadraticCurveTo(x + k + 5, y + hgt * 0.25, x + k + 6, y); } x += wl + gap; } g.stroke(); g.restore();
  };
  return {
    planes,
    update(F) {
      const t = F.t, g = F.g; const sh = F.shot; const dim = sh.dimTo ? lerp(1, sh.dimTo, smoothstep(sh.dimAt[0], sh.dimAt[1], t)) : 1; const fl = candles.map((c, i) => fireFlick(t, i * 3.3 + 1) * dim);
      tintAll(S, 0.3 * dim);
      // candle lights on the desk + sheets
      const Ls = candles.map((c, i) => ({ p: S.world(c.x, c.y, D.desk), r: 3.2 * D.desk / 10 * (S.f / 1866), c: WARM, k: 1.5 * fl[i] }));
      const sheetL = candles.map((c, i) => ({ p: S.world(c.x, c.y, D.sheet), r: 3.0 * D.sheet / 10, c: WARM, k: 0.75 * fl[i] }));
      lightsOn(planes.desk, Ls); for (const k of Object.keys(SHEETS)) lightsOn(sheetPl[k], sheetL);
      const gl = F.glow();
      for (let i = 0; i < candles.length; i++) { const c = candles[i]; const p = F.P(D.desk, c.x, c.y); const K = F.K(D.desk, c.x, c.y);
        glowAt(gl, p[0], p[1], 240 * K * fl[i], 0.16, [255, 150, 70]); glowAt(gl, p[0], p[1], 26 * K, 0.9 * fl[i]);
        // candle stub + flame (only when roughly on screen)
        if (p[0] > -80 && p[0] < DWc + 80 && p[1] > -80 && p[1] < DHc + 80) { g.fillStyle = rgba(hex('#cfc3a0')); g.fillRect(p[0] - 9 * K, p[1], 18 * K, 70 * K); g.fillStyle = rgba(hex('#3a2c20')); g.fillRect(p[0] - 14 * K, p[1] + 70 * K, 28 * K, 6 * K);
          const hf = 26 * K * (0.9 + 0.2 * fl[i]); g.fillStyle = rgba([255, 205, 120], 0.95); g.beginPath(); g.moveTo(p[0] - 5 * K, p[1]); g.quadraticCurveTo(p[0] - 6 * K, p[1] - hf * 0.6, p[0] + 1.5 * K * Math.sin(t * 7 + i), p[1] - hf); g.quadraticCurveTo(p[0] + 7 * K, p[1] - hf * 0.5, p[0] + 5 * K, p[1]); g.fill(); }
        if (p[0] > -80 && p[0] < DWc + 80 && p[1] > -120 && p[1] < DHc + 80) { smoke(g, t, p[0], p[1] - 26 * K, { n: 5, rise: 150 * K, wind: 10, r0: 1.2 * K + 0.5, r1: 7 * K + 1, a: 0.14 * dim, col: [200, 190, 210], life: 4, seed: i + 3 });
          const ma = t * 2.3 + i * 2, mr = (34 + 10 * Math.sin(t * 0.7 + i)) * K; const mx = p[0] + Math.cos(ma) * mr, my = p[1] - 28 * K + Math.sin(ma * 1.3) * mr * 0.55; const fl2 = Math.sin(t * 38 + i) * 0.7; g.fillStyle = 'rgba(30,22,26,0.9)'; g.beginPath(); g.ellipse(mx, my, 1.6 * K, 4 * K, 0.3, 0, 7); g.fill(); g.fillStyle = 'rgba(210,190,160,0.75)'; for (const sd of [-1, 1]) { g.beginPath(); g.ellipse(mx + sd * 4 * K, my - 1 * K, 4.6 * K * Math.abs(0.4 + fl2), 2.4 * K, sd * 0.5, 0, 7); g.fill(); } }
        F.lights.push({ x: p[0], y: p[1], r: 300 * K, c: WARM, k: 0.5 * fl[i] }); }
      // sheets
      for (const [key, s] of Object.entries(SHEETS)) {
        const cp = F.P(D.sheet, s.cx, s.cy), K = F.K(D.sheet, s.cx, s.cy); const tx = PAGE_TEXT[key];
        if (cp[1] < -700 * K || cp[1] > 1280 + 700 * K) continue; g.save(); g.translate(cp[0], cp[1]); g.rotate(s.rot); g.scale(K, K);
        const lx = -s.w / 2 + 56, tw = s.w - 112;
        // pseudo script lines: above and below the passage; written down over time
        const scribLines = []; for (let i = 0; i < 6; i++) scribLines.push(-s.h / 2 + 64 + i * 34); for (let i = 0; i < 7; i++) scribLines.push(32 + 118 + i * 34 - (key === 'kek' ? 10 : 0));
        scribLines.forEach((yy, i) => { const sc = key === 'sky' && sh.scribe ? sh.scribe : tx.scrib; const per = (sc[1] - sc[0]) / scribLines.length; const pr = rev(t, sc[0] + i * per, sc[0] + (i + 1) * per * 1.3); if (pr > 0) script(g, lx, yy, tw * (0.78 + 0.2 * hash1(i * 5 + (key === 'sky' ? 1 : 9))), 100 + i * 7 + (key === 'sky' ? 0 : 50), pr, 13, 0.62); });
        // the passage: header (small), body (large), real type
        g.font = 'italic 400 22px "Cormorant Garamond"'; g.textBaseline = 'alphabetic'; g.fillStyle = 'rgba(40,24,14,0.92)';
        const textLine = (str, x, y, p, font, col) => { if (p <= 0) return; g.save(); g.font = font; g.beginPath(); g.rect(x - 6, y - 40, (g.measureText(str).width + 12) * p, 60); g.clip(); g.fillStyle = col; g.fillText(str, x, y); g.restore(); };
        const y0 = -s.h / 2 + 64 + 6 * 34 + 26;
        tx.head.forEach((h, i) => textLine(h, lx, y0 + i * 28, rev(t, tx.headAt[0] + (i * (tx.headAt[1] - tx.headAt[0])) / tx.head.length, tx.headAt[0] + ((i + 1) * (tx.headAt[1] - tx.headAt[0])) / tx.head.length), 'italic 400 22px "Cormorant Garamond"', 'rgba(52,32,18,0.9)'));
        const by = y0 + tx.head.length * 28 + 44; const bodyFont = 'italic 500 33px "Cormorant Garamond"';
        tx.body.forEach((b, i) => { const p = rev(t, tx.at[i * 2], tx.at[i * 2 + 1]); textLine(b, lx, by + i * 46, p, bodyFont, 'rgba(34,20,12,0.95)');
          if (i === tx.numLine && p > 0) { g.font = bodyFont; const a = b.indexOf(tx.num); const xs = lx + g.measureText(b.slice(0, a)).width, xe = xs + g.measureText(tx.num).width;
            const up = rev(t, tx.underline, tx.underline + 0.6); if (up > 0) { g.strokeStyle = 'rgba(122,36,24,0.85)'; g.lineWidth = 2.2; g.beginPath(); g.moveTo(xs, by + i * 46 + 8); g.quadraticCurveTo((xs + xe) / 2, by + i * 46 + 12, xs + (xe - xs) * up, by + i * 46 + 7); g.stroke(); }
            const sp = rev(t, tx.strike[0], tx.strike[1]); if (sp > 0) { g.strokeStyle = 'rgba(30,14,10,0.92)'; g.lineWidth = 4; g.lineCap = 'round'; g.beginPath(); const ym = by + i * 46 - 10; for (let k = 0; k <= 24 * sp; k++) { const u = k / 24; const xx = xs - 10 + (xe - xs + 20) * u; const yy = ym + (k % 2 ? 4 : -4) * 0.8 + Math.sin(u * 9) * 2; k ? g.lineTo(xx, yy) : g.moveTo(xx, yy); } g.stroke(); } } });
        g.restore();
      }
      motes(F.glow(), t, { x0: 60, y0: 200, x1: 660, y1: 1200 }, { n: 18, col: [255, 214, 160], a: 0.4 * dim, size: 1.1, seed: 22, drift: [3, -3] });
      embers(F.glow(), t, { x0: 0, y0: 100, x1: 720, y1: 1250 }, 26, { size: 1.4, col: [255, 200, 120], a: 0.45, wind: 4, speed: 8, rise: 0.4, seed: 7 });
      F.amb = [0.85, 0.85, 0.85]; F.bloom = 0.35;
    },
  };
}
const DWc = 720, DHc = 1280;
