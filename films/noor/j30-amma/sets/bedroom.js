// SET bedroom: a child's room at night, nobody in it. A low bed with a folded patterned blanket and a pillow, a small lamp turned
// low on a stool, an arched window with the crescent and stars, a little shelf with a closed mushaf in its cloth, a rug.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, rng, WARM, tintAll, lightsOn, glowAt, motes, smoke, flick, oilLamp, nightSky, makeStars, drawStars, crescent } from '../lib.js';
import { archPath, plasterWall } from './study.js';

export default function bedroom(S, cams) {
  const cover = (D, m = 50) => S.cover(D, cams, m); const D = { sky: 220, wall: 13, floor: 9, bed: 7 }; const planes = {};
  const WIN = [300, 110, 470, 400];
  { const r = cover(D.sky, 60); const C = new Canvas(r, { seed: 1201 }); nightSky(C, { stops: [[-200, '#02030a'], [100, '#060a1e'], [300, '#0c1236'], [500, '#161d48']], glow: { x: 380, y: 300, rx: 600, ry: 300, col: hex('#232a5a'), a: 0.35 } }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.wall, 60); const C = new Canvas(r, { seed: 1202 }); const g = C.g; plasterWall(C, hex('#4e5a78'), { floorShade: 560 });
    const wp = archPath(...WIN); g.strokeStyle = rgba(hex('#2a2a3a')); g.lineWidth = 22; g.stroke(wp); g.strokeStyle = rgba(hex('#8a8aa8'), 0.5); g.lineWidth = 3; g.stroke(archPath(WIN[0] - 14, WIN[1] - 14, WIN[2] + 14, WIN[3] + 14));
    g.fillStyle = rgba(hex('#2a2a3a')); g.fillRect(WIN[0] - 30, WIN[3], WIN[2] - WIN[0] + 60, 16);
    g.save(); g.globalCompositeOperation = 'destination-out'; g.fill(wp); g.restore();
    // a thin curtain tied to one side
    const cu = new Path2D(); cu.moveTo(WIN[2] - 10, WIN[1] + 20); cu.quadraticCurveTo(WIN[2] + 40, 260, WIN[2] + 18, WIN[3] + 10); cu.lineTo(WIN[2] + 46, WIN[3] + 10); cu.quadraticCurveTo(WIN[2] + 70, 250, WIN[2] + 26, WIN[1] + 10); cu.closePath(); underpaint(C, (x, y) => mixc(hex('#9a8aa0'), hex('#6a5a78'), C.n.fbm(x * 0.05, y * 0.01, 2)), cu, 3);
    // a little shelf with a closed mushaf wrapped in cloth, and a framed calligraphy roundel (pattern only)
    g.fillStyle = rgba(hex('#3a2a1e')); g.fillRect(620, 300, 170, 10); g.fillStyle = rgba(hex('#2f5a52')); g.fillRect(650, 268, 70, 32); g.fillStyle = rgba(hex('#c9a227'), 0.6); g.fillRect(650, 282, 70, 3);
    g.fillStyle = rgba(hex('#6a4a2a')); g.beginPath(); g.ellipse(752, 288, 18, 12, 0, 0, 7); g.fill();
    g.strokeStyle = rgba(hex('#b89a5a'), 0.7); g.lineWidth = 3; g.beginPath(); g.arc(705, 180, 52, 0, 7); g.stroke(); g.lineWidth = 1.2; for (let k = 0; k < 16; k++) { const a = k * Math.PI / 8; g.beginPath(); g.moveTo(705 + Math.cos(a) * 20, 180 + Math.sin(a) * 20); g.lineTo(705 + Math.cos(a + 0.4) * 44, 180 + Math.sin(a + 0.4) * 44); g.stroke(); }
    g.fillStyle = rgba(hex('#24243a')); g.fillRect(-2000, 548, 6000, 12);
    planes.wall = S.plane('wall', D.wall, r, C.c); }
  { const r = cover(D.floor, 60); r[1] = Math.max(r[1], 420); const C = new Canvas(r, { seed: 1203 }); const g = C.g;
    underpaint(C, (x, y) => mul(hex('#2a2430'), 0.7 + 0.5 * C.n.fbm(x * 0.01, y * 0.03, 3)), null, 8);
    const rug = new Path2D(); rug.moveTo(200, 520); rug.lineTo(760, 520); rug.lineTo(820, 720); rug.lineTo(80, 720); rug.closePath(); underpaint(C, (x, y) => mixc(hex('#24384a'), hex('#1c2e3e'), C.n.fbm(x * 0.01, y * 0.02, 3)), rug, 6);
    g.save(); g.clip(rug); g.strokeStyle = rgba(hex('#c9a227'), 0.45); g.lineWidth = 3; g.strokeRect(150, 540, 620, 300); for (let i = 0; i < 6; i++) { g.beginPath(); g.arc(470, 640, 30 + i * 22, Math.PI, 2 * Math.PI); g.stroke(); } g.restore();
    planes.floor = S.plane('floor', D.floor, r, C.c); }
  // the bed: low wooden frame, mattress, pillow, the folded blanket
  { const r = [760, 330, 1320, 720]; const C = new Canvas(r, { seed: 1204, q: 1.4 }); const g = C.g;
    const box = (pts, col, k = 0.4) => { const p = new Path2D(); p.moveTo(...pts[0]); for (const q of pts.slice(1)) p.lineTo(...q); p.closePath(); underpaint(C, (x, y) => mul(col, 0.8 + k * C.n.fbm(x * 0.02, y * 0.02, 3)), p, 3); return p; };
    box([[800, 560], [1300, 560], [1300, 640], [800, 640]], hex('#4a3020')); g.fillStyle = rgba(hex('#2a1a10')); g.fillRect(800, 636, 500, 6); g.fillRect(812, 640, 14, 40); g.fillRect(1280, 640, 14, 40);
    box([[790, 500], [1300, 500], [1300, 566], [790, 566]], hex('#d8d0c0'), 0.25);
    const pil = new Path2D(); pil.ellipse(1210, 488, 70, 28, -0.05, 0, 7); underpaint(C, (x, y) => mixc(hex('#e8e0d0'), hex('#b8b0c0'), smoothstep(470, 510, y)), pil, 3);
    // the folded blanket: three layered folds with a woven border
    for (let k = 0; k < 3; k++) { const y = 470 + k * 10, x0 = 860 + k * 4, x1 = 1060 - k * 4; const p = box([[x0, y], [x1, y], [x1 + 6, y + 34], [x0 - 6, y + 34]], mixc(hex('#7a2a24'), hex('#9a3a2a'), k * 0.3), 0.3); g.strokeStyle = rgba(hex('#e0b860'), 0.65); g.lineWidth = 2; g.beginPath(); g.moveTo(x0, y + 6); g.lineTo(x1, y + 6); g.stroke();
      g.fillStyle = rgba(hex('#2a4a5a'), 0.8); for (let x = x0 + 12; x < x1 - 8; x += 18) { g.beginPath(); g.moveTo(x, y + 18); g.lineTo(x + 5, y + 23); g.lineTo(x, y + 28); g.lineTo(x - 5, y + 23); g.closePath(); g.fill(); } }
    C.mottle({ amt: 0.07, cell: 12 }); planes.bed = S.plane('bed', D.bed, r, C.c); }
  const stars = makeStars(1205, [250, -100, 520, 420], 70, 1.6); const LAMP = [720, 520];
  return {
    update(F) {
      const t = F.t, g = F.g, sh = F.shot; const gg = F.glow(); const dim = sh.dim ? lerp(1, 0.55, smoothstep(sh.dim[0], sh.dim[1], t)) : 1; const fl = flick(t, 9) * dim;
      tintAll(S, 0.4); planes.sky.material.uniforms.uTint.value.set(0.55, 0.56, 0.68);
      { const a = F.P(D.wall, WIN[0] + 6, WIN[1] + 30), b = F.P(D.wall, WIN[2] - 6, WIN[3] - 4); F.starClip = [a[0], a[1], b[0], b[1]]; } drawStars(F, D.sky, stars, 0.9); F.starClip = null;
      { const mp = F.P(D.sky, 410, 180); const a = F.P(D.wall, WIN[0] + 14, WIN[1] + 40), b = F.P(D.wall, WIN[2] - 14, WIN[3]); if (mp[0] > a[0] && mp[0] < b[0] && mp[1] > a[1] && mp[1] < b[1]) crescent(F, mp[0], mp[1], 13, 0.95); }
      const lp = F.P(D.floor, LAMP[0], LAMP[1]); const K = F.K(D.floor, LAMP[0], LAMP[1]);
      g.fillStyle = rgba(hex('#2a1c12')); g.fillRect(lp[0] - 38 * K, lp[1] + 6 * K, 76 * K, 9 * K); g.fillRect(lp[0] - 32 * K, lp[1] + 15 * K, 8 * K, 54 * K); g.fillRect(lp[0] + 24 * K, lp[1] + 15 * K, 8 * K, 54 * K);
      const tip = oilLamp(g, gg, lp[0] - 12 * K, lp[1], 30 * K, t, 0.75 * dim, 9); smoke(g, t, tip[0], tip[1] - 14 * K, { n: 4, rise: 70 * K, a: 0.08, life: 5, seed: 6 });
      const Lw = (DD, k) => ({ p: S.world(LAMP[0], LAMP[1] - 40, DD), r: 0.5 * DD, c: WARM, k: k * fl });
      lightsOn(planes.wall, [Lw(D.wall, 1.4)]); lightsOn(planes.floor, [Lw(D.floor, 1.4)]); lightsOn(planes.bed, [{ ...Lw(D.bed, 1.0), r: 0.55 * D.bed }]);
      F.lights.push({ x: tip[0], y: tip[1], r: 380 * K, c: WARM, k: 0.55 * fl });
      // moonlight falling through the window onto the floor, with dust turning in it
      const w0 = F.P(D.wall, 385, 300); glowAt(gg, w0[0] + 40, w0[1] + 260, 230 * F.K(D.wall), 0.06, [140, 160, 255]);
      motes(gg, t, { x0: w0[0] - 80, y0: w0[1] - 80, x1: w0[0] + 220, y1: w0[1] + 300 }, { n: 18, col: [190, 205, 255], a: 0.3, size: 1.0, seed: 71, drift: [2, 1] });
      F.amb = [0.9, 0.92, 1.0]; F.bloom = 0.42; F.hal = 0.2;
    },
  };
}
