// SET study: a quiet room at night where tonight's juz is read. Plaster walls warmed by one oil lamp, an arched window with a
// wooden lattice and the crescent beyond, a niche with three small lanterns on its shelf, a rug, and in front a wooden stand (rehal)
// holding an open mushaf whose pages show only their illuminated borders and soft ruled lines (never imitation script). No person.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, ease, rng, WARM, PAL, tintAll, lightsOn, glowAt, motes, smoke, flick, igniteEnv, fanous, glowLantern, oilLamp, nightSky, makeStars, drawStars, crescent } from '../lib.js';

export const archPath = (x0, y0, x1, y1, k = 0.55) => { const p = new Path2D(); const w = x1 - x0, cx = (x0 + x1) / 2, ys = y0 + w * k; p.moveTo(x0, y1); p.lineTo(x0, ys); p.quadraticCurveTo(x0, y0 + w * 0.12, cx, y0); p.quadraticCurveTo(x1, y0 + w * 0.12, x1, ys); p.lineTo(x1, y1); p.closePath(); return p; };
export function plasterWall(C, base, opt = {}) {
  const [x0, y0, x1, y1] = C.rect; const n = C.n, R = C.R;
  const col = (x, y) => mul(mixc(base, mixc(base, [255, 236, 200], 0.18), n.fbm(x * 0.004, y * 0.004, 4)), 0.82 + 0.3 * n.fbm(x * 0.012 + 5, y * 0.012, 3) - (opt.floorShade ? 0.25 * smoothstep(opt.floorShade - 120, opt.floorShade, y) : 0));
  underpaint(C, col, null, 8);
  C.strokes({ n: C.area / 700, color: col, angle: () => (R() - 0.5) * 2.4, len: [20, 60], wid: [8, 18], alpha: [0.25, 0.5], jv: 0.06, bend: 0.25 });
  C.strokes({ n: C.area / 1600, color: (x, y) => mul(col(x, y), 0.88), angle: () => (R() - 0.5) * 0.4, len: [40, 120], wid: [3, 6], alpha: [0.15, 0.3], jv: 0.06, bend: 0.1 });
  C.mottle({ amt: 0.14, cell: 26 });
}

export default function study(S, cams) {
  const cover = (D, m = 40) => S.cover(D, cams, m); const D = { sky: 220, wall: 14, floor: 9.5, stand: 6 };
  const planes = {}; const WIN = [770, 96, 960, 420], NICHE = [200, 150, 420, 430];
  // the sky beyond the window
  { const r = cover(D.sky, 60); const C = new Canvas(r, { seed: 701 }); nightSky(C, { stops: [[-200, '#02030a'], [100, '#050818'], [300, '#0a1030'], [500, '#141c44']], glow: { x: 900, y: 340, rx: 700, ry: 300, col: hex('#232a5a'), a: 0.35 } }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  // the back wall with the window cut out and the niche painted in
  { const r = cover(D.wall, 60); const C = new Canvas(r, { seed: 702 }); const g = C.g; plasterWall(C, hex('#7a5a3c'), { floorShade: 560 });
    // niche: a deep arched recess with a shelf
    const np = archPath(...NICHE); underpaint(C, (x, y) => mul(hex('#3a2818'), 0.7 + 0.5 * smoothstep(NICHE[1] + 30, NICHE[3], y) * (0.6 + 0.4 * C.n.fbm(x * 0.02, y * 0.02, 3))), np, 6);
    C.strokes({ n: 260, mask: C.mask((gg) => gg.fill(np)), color: (x, y) => mul(hex('#4a3420'), 0.7 + 0.4 * C.n.fbm(x * 0.03, y * 0.03, 2)), angle: () => Math.PI / 2 + (C.R() - 0.5) * 0.5, len: [10, 30], wid: [4, 8], alpha: [0.3, 0.6], jv: 0.06, bend: 0.2 });
    g.strokeStyle = rgba(hex('#a9875e'), 0.8); g.lineWidth = 5; g.stroke(np); g.strokeStyle = rgba(hex('#2a1c10'), 0.6); g.lineWidth = 2; g.stroke(archPath(NICHE[0] + 6, NICHE[1] + 6, NICHE[2] - 6, NICHE[3]));
    g.fillStyle = rgba(hex('#5a3c22')); g.fillRect(NICHE[0] - 10, NICHE[3] - 70, NICHE[2] - NICHE[0] + 20, 12); g.fillStyle = rgba(hex('#2a1a0e')); g.fillRect(NICHE[0] - 10, NICHE[3] - 58, NICHE[2] - NICHE[0] + 20, 5);
    // a folded cloth and a small bowl on the shelf, left, so the niche is lived in
    g.fillStyle = rgba(hex('#4f5a46')); g.fillRect(NICHE[0] + 18, NICHE[3] - 92, 40, 22); g.fillStyle = rgba(hex('#6b3f2a')); g.beginPath(); g.ellipse(NICHE[2] - 34, NICHE[3] - 78, 16, 8, 0, 0, 7); g.fill();
    // window: carved frame, then the opening cut out, then the lattice over its lower half
    const wp = archPath(...WIN); g.strokeStyle = rgba(hex('#3a2616')); g.lineWidth = 26; g.stroke(wp); g.strokeStyle = rgba(hex('#9c7a50'), 0.7); g.lineWidth = 4; g.stroke(archPath(WIN[0] - 16, WIN[1] - 16, WIN[2] + 16, WIN[3] + 16));
    g.fillStyle = rgba(hex('#2a1c10')); g.fillRect(WIN[0] - 34, WIN[3], WIN[2] - WIN[0] + 68, 18);
    g.save(); g.globalCompositeOperation = 'destination-out'; g.fill(wp); g.restore();
    g.save(); g.clip(wp); g.strokeStyle = rgba(hex('#24170d')); g.lineWidth = 4; const ly = WIN[1] + 170; for (let x = WIN[0] - 40; x < WIN[2] + 40; x += 26) { g.beginPath(); g.moveTo(x, ly); g.lineTo(x + 130, WIN[3]); g.moveTo(x + 130, ly); g.lineTo(x, WIN[3]); g.stroke(); } g.fillStyle = rgba(hex('#24170d')); g.fillRect(WIN[0], ly - 4, WIN[2] - WIN[0], 7); g.restore();
    // a bookcase on the right: three shelves of bound books, spines with gold bands, catching the lamp
    g.fillStyle = rgba(hex('#2e1d10')); g.fillRect(1030, 170, 210, 360); g.fillStyle = rgba(hex('#1a0f07')); g.fillRect(1042, 182, 186, 336);
    { const R2 = rng(77); for (let sh = 0; sh < 3; sh++) { const yb = 290 + sh * 116; g.fillStyle = rgba(hex('#4a3018')); g.fillRect(1036, yb, 198, 10); let x = 1046;
      while (x < 1222) { const w = 10 + R2() * 14, h = 70 + R2() * 26; if (x + w > 1224) break; const lean = R2() < 0.12 ? 0.12 : 0; const col = [hex('#5e2a1e'), hex('#2f4a3e'), hex('#6a4a22'), hex('#3a2a4a'), hex('#7a5a30')][Math.floor(R2() * 5)];
        g.save(); g.translate(x + w / 2, yb); g.rotate(lean); g.fillStyle = rgba(mul(col, 0.8 + R2() * 0.4)); g.fillRect(-w / 2, -h, w, h); g.fillStyle = rgba(hex('#c9a227'), 0.55); g.fillRect(-w / 2, -h + 10, w, 2); g.fillRect(-w / 2, -16, w, 2); g.restore(); x += w + 1.5 + (lean ? 6 : 0); } } }
    g.fillStyle = rgba(hex('#4a3018')); g.fillRect(1030, 160, 210, 14);
    // skirting where the wall meets the floor
    g.fillStyle = rgba(hex('#2a1a0e')); g.fillRect(-2000, 548, 6000, 14);
    planes.wall = S.plane('wall', D.wall, r, C.c); }
  // the floor and rug, seen in perspective
  { const r = cover(D.floor, 60); r[1] = Math.max(r[1], 420); const C = new Canvas(r, { seed: 703 }); const g = C.g; const [x0, y0, x1, y1] = r;
    underpaint(C, (x, y) => mul(hex('#3c2a1c'), 0.7 + 0.5 * C.n.fbm(x * 0.01, y * 0.03, 3)), null, 8);
    C.strokes({ n: C.area / 500, color: (x, y) => mul(hex('#4a3422'), 0.7 + 0.5 * C.n.fbm(x * 0.006, y * 0.04, 3)), angle: () => (C.R() - 0.5) * 0.08, len: [60, 160], wid: [4, 8], alpha: [0.3, 0.6], jv: 0.06, bend: 0.02 });
    const rug = new Path2D(); rug.moveTo(330, 500); rug.lineTo(1080, 500); rug.lineTo(1320, 760); rug.lineTo(90, 760); rug.closePath();
    underpaint(C, (x, y) => mixc(hex('#6a2420'), hex('#8a3a26'), C.n.fbm(x * 0.01, y * 0.02, 3)), rug, 6);
    g.save(); g.clip(rug); g.strokeStyle = rgba(hex('#c9a227'), 0.55); g.lineWidth = 3; const inner = (k) => { const p = new Path2D(); p.moveTo(330 + k * 1.1, 500 + k * 0.4); p.lineTo(1080 - k * 1.1, 500 + k * 0.4); p.lineTo(1320 - k * 1.6, 760); p.lineTo(90 + k * 1.6, 760); p.closePath(); return p; }; g.stroke(inner(24)); g.strokeStyle = rgba(hex('#1e3a3a'), 0.7); g.lineWidth = 9; g.stroke(inner(44));
    for (let i = 0; i < 9; i++) { const u = (i + 0.5) / 9; const yy = 560 + u * 120; const xc = 705; const ww = 160 + u * 80; g.strokeStyle = rgba(hex('#d6b06a'), 0.32); g.lineWidth = 2; g.beginPath(); g.moveTo(xc - ww, yy); g.lineTo(xc, yy - 18); g.lineTo(xc + ww, yy); g.lineTo(xc, yy + 18); g.closePath(); g.stroke(); }
    g.restore(); C.strokes({ n: 900, mask: C.mask((gg) => gg.fill(rug)), color: (x, y) => mul(hex('#7a3022'), 0.8 + 0.4 * C.R()), angle: () => (C.R() - 0.5) * 0.3, len: [6, 16], wid: [2, 4], alpha: [0.2, 0.4], jv: 0.1, bend: 0.2 });
    planes.floor = S.plane('floor', D.floor, r, C.c); }
  // the stand and the open mushaf (foreground)
  { const r = [440, 300, 980, 760]; const C = new Canvas(r, { seed: 704, q: 1.5 }); const g = C.g;
    const wood = hex('#5a3a20'), woodL = hex('#8a5e34');
    // the rehal: two interlocking boards; above the crossing they open into a V that holds the book, below it two legs
    const board = (pts, col) => { const p = new Path2D(); p.moveTo(...pts[0]); for (const q of pts.slice(1)) p.lineTo(...q); p.closePath(); underpaint(C, (x, y) => mul(col, 0.75 + 0.45 * C.n.fbm(x * 0.03, y * 0.01, 3)), p, 3); g.strokeStyle = rgba(mul(col, 0.45), 0.9); g.lineWidth = 2; g.stroke(p); };
    board([[628, 404], [654, 398], [806, 650], [778, 656]], wood); board([[792, 404], [766, 398], [614, 650], [642, 656]], woodL);
    g.strokeStyle = rgba(hex('#d1aa50'), 0.5); g.lineWidth = 1.5; for (const [p0, p1] of [[[642, 408], [790, 650]], [[778, 408], [630, 650]]]) { g.beginPath(); g.moveTo(...p0); g.lineTo(...p1); g.stroke(); }
    g.fillStyle = rgba(hex('#c9a227'), 0.6); g.beginPath(); g.arc(710, 528, 6, 0, 7); g.fill();
    // the open book: two pages bowing from the spine, a gilded frame on each, soft ruled lines (no letters)
    const page = (side) => { const sx = side < 0 ? -1 : 1; const p = new Path2D(); p.moveTo(710, 462); p.quadraticCurveTo(710 + sx * 70, 420, 710 + sx * 168, 436); p.lineTo(710 + sx * 160, 372); p.quadraticCurveTo(710 + sx * 70, 356, 710, 396); p.closePath(); return p; };
    for (const s of [-1, 1]) { const p = page(s); underpaint(C, (x, y) => mixc(hex('#f3e7c6'), hex('#d9c393'), smoothstep(0, 230, Math.abs(x - 710)) * 0.5 + C.n.fbm(x * 0.02, y * 0.02, 2) * 0.2), p, 3);
      g.save(); g.clip(p); g.strokeStyle = rgba(hex('#b38a2e'), 0.85); g.lineWidth = 3; g.stroke(page(s)); g.lineWidth = 1.2; g.strokeStyle = rgba(hex('#2e6f6a'), 0.55);
      g.strokeStyle = rgba(hex('#b38a2e'), 0.7); g.lineWidth = 1.5; const fr = new Path2D(); fr.moveTo(710 + s * 18, 448); fr.quadraticCurveTo(710 + s * 72, 414, 710 + s * 150, 426); fr.lineTo(710 + s * 145, 382); fr.quadraticCurveTo(710 + s * 72, 370, 710 + s * 18, 404); fr.closePath(); g.stroke(fr); g.lineWidth = 1; g.strokeStyle = rgba(hex('#5a5a5a'), 0.35);
      for (let k = 0; k < 5; k++) { const yy = 404 + k * 8.5; g.beginPath(); g.moveTo(710 + s * 26, yy + 2); g.quadraticCurveTo(710 + s * 74, yy - 26 + k * 0.6, 710 + s * 138, yy - 16); g.stroke(); }
      g.fillStyle = rgba(hex('#c9a227'), 0.85); g.beginPath(); g.arc(710 + s * 84, 392, 4, 0, 7); g.fill(); g.restore(); }
    g.fillStyle = rgba(hex('#8a6a3a'), 0.6); g.fillRect(708, 396, 4, 66);
    C.mottle({ amt: 0.08, cell: 12 }); planes.stand = S.plane('stand', D.stand, r, C.c); }
  const stars = makeStars(705, [700, -100, 1000, 420], 90, 1.6);
  const LAMP = { x: 930, y: 610, D: D.stand }; const NL = [{ x: 255, y: 340 }, { x: 310, y: 340 }, { x: 365, y: 340 }];
  return {
    update(F) {
      const t = F.t, g = F.g, sh = F.shot; const gg = F.glow(); const fl = flick(t, 3);
      // the lamp's light on everything (one warm key), the cool moon fill from the window
      const lampP = F.P(D.stand, LAMP.x, LAMP.y); const Kl = F.K(D.stand, LAMP.x, LAMP.y);
      const Lw = (DD, k) => ({ p: S.world(LAMP.x + 30, LAMP.y - 30, DD), r: 0.62 * DD, c: WARM, k: k * fl });
      tintAll(S, 0.34); planes.sky.material.uniforms.uTint.value.set(0.5, 0.52, 0.62);
      lightsOn(planes.wall, [Lw(D.wall, 2.0), ...(sh.mode === 'niche' ? NL.map((n, i) => ({ p: S.world(n.x, n.y, D.wall - 0.2), r: 1.3, c: WARM, k: 1.4 * igniteEnv(t, sh.niche[i], i) })) : [])]);
      lightsOn(planes.floor, [Lw(D.floor, 1.6)]); lightsOn(planes.stand, [{ ...Lw(D.stand, 0.9), r: 0.5 * D.stand }]);
      // window: stars and the crescent, a faint moonbeam across the wall
      { const a = F.P(D.wall, WIN[0] + 6, WIN[1] + 30), b = F.P(D.wall, WIN[2] - 6, WIN[1] + 160); F.starClip = [a[0], a[1], b[0], b[1]]; } drawStars(F, D.sky, stars, 0.9); const mp = F.P(D.sky, 905, 175); crescent(F, mp[0], mp[1], 14 * F.K(D.sky) / F.K(D.sky), 0.95);
      // niche lanterns (three treasures): unlit by default, they light on the narration in "niche"
      for (let i = 0; i < 3; i++) { const p = F.P(D.wall, NL[i].x, NL[i].y); const K = F.K(D.wall, NL[i].x, NL[i].y); const on = sh.mode === 'niche' ? igniteEnv(t, sh.niche[i], i + 5) : (sh.mode === 'lamp' || sh.mode === 'room' ? 0.0 : 0);
        fanous(g, p[0], p[1], 34 * K, on, t, i + 5); glowLantern(gg, p[0], p[1], 34 * K, on, t, i + 5); if (on > 0) F.lights.push({ x: p[0], y: p[1], r: 120 * K, c: WARM, k: 0.6 * on }); }
      // the oil lamp on its low stool
      const K = Kl; g.fillStyle = rgba(hex('#3a2616')); g.fillRect(lampP[0] - 40 * K, lampP[1] + 10 * K, 80 * K, 10 * K); g.fillRect(lampP[0] - 34 * K, lampP[1] + 20 * K, 8 * K, 60 * K); g.fillRect(lampP[0] + 26 * K, lampP[1] + 20 * K, 8 * K, 60 * K);
      const tip = oilLamp(g, gg, lampP[0] - 10 * K, lampP[1], 34 * K, t, 1, 3);
      smoke(g, t, tip[0], tip[1] - 22 * K, { n: 5, rise: 90 * K, wind: 4, r0: 1 * K + 0.5, r1: 7 * K + 1, a: 0.1, life: 5, seed: 2 });
      F.lights.push({ x: tip[0], y: tip[1], r: 520 * K, c: WARM, k: 0.75 * fl });
      // dust in the lamp light and the moonbeam
      motes(gg, t, { x0: lampP[0] - 420 * K, y0: lampP[1] - 380 * K, x1: lampP[0] + 220 * K, y1: lampP[1] + 60 * K }, { n: 26, col: [255, 214, 160], a: 0.35, size: 1.2, seed: 11, drift: [3, -2] });
      const wp = F.P(D.wall, 865, 300); glowAt(gg, wp[0], wp[1] + 80, 260 * F.K(D.wall), 0.05, [140, 160, 255]);
      F.amb = [0.92, 0.9, 0.95]; F.bloom = 0.42; F.hal = 0.22;
    },
  };
}
