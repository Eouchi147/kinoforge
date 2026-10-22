// SET path: a garden hill at night, a stone path winding up to the top, thirty lanterns on posts along it (thirty parts,
// thirty nights). Cypresses and palms in the middle ground sway a little, fireflies drift, low haze slides along the hollows.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, rng, WARM, tintAll, lightsOn, glowAt, motes, flick, igniteEnv, fanous, glowLantern, nightSky, makeStars, drawStars, crescent, paintRange, paintFog, pineTree, paintTufts, ridged } from '../lib.js';

// the path as a list of design-px points on the hill plane, bottom to top
const PATH = [[470, 760], [540, 690], [640, 640], [720, 600], [700, 545], [600, 505], [560, 460], [640, 420], [760, 392], [800, 350], [740, 315], [670, 285], [690, 250], [760, 228], [800, 205]];
function dense(pts, n) { const out = []; let L = 0; const seg = []; for (let i = 0; i < pts.length - 1; i++) { const d = Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]); seg.push(d); L += d; }
  for (let k = 0; k < n; k++) { let s = (k / (n - 1)) * L; let i = 0; while (i < seg.length - 1 && s > seg[i]) { s -= seg[i]; i++; } const u = clamp(s / seg[i]); out.push([lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u), Math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])]); } return out; }
export const hillRidge = (x) => 200 + 0.00042 * (x - 800) ** 2 + 26 * (ridged(x * 0.004, 3, 2) - 0.5);

export default function path(S, cams) {
  const cover = (D, m = 50) => S.cover(D, cams, m); const D = { sky: 3000, far: 900, hill: 80, mid: 40, fg: 14 }; const planes = {};
  { const r = cover(D.sky, 80); const C = new Canvas(r, { seed: 801 }); nightSky(C, { stops: [[-1200, '#02030a'], [-200, '#050818'], [200, '#0b1234'], [420, '#1a2250'], [560, '#2b3263']], glow: { x: 640, y: 470, rx: 900, ry: 200, col: hex('#3d3c70'), a: 0.4 } }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.far, 60); r[1] = Math.max(r[1], 250); const C = new Canvas(r, { seed: 802 });
    paintRange(C, { ridge: (x) => 395 + 40 * (ridged(x * 0.0022, 4, 5) - 0.5) + 18 * Math.sin(x * 0.004), top: hex('#1b2046'), mid: hex('#151a3a'), base: hex('#0d1128'), fall: 200, light: { dir: -1, col: hex('#3a3f72'), amt: 0.3 }, haze: { col: hex('#2a2f5a'), y0: 380, y1: 520, a: 0.5 } });
    planes.far = S.plane('far', D.far, r, C.c); }
  // the hill with the path
  const lamps = dense(PATH, 30).map(([x, y, a], i) => { const side = i % 2 ? 1 : -1; const k = lerp(1, 0.42, clamp((760 - y) / 560)); return { x: x + side * 26 * k * Math.cos(a + Math.PI / 2) * 1.2, y: y + side * 10 * k, s: 15 * k, k, i }; });
  { const r = cover(D.hill, 60); r[1] = Math.max(r[1], 120); const C = new Canvas(r, { seed: 803 }); const g = C.g; const [x0, y0, x1, y1] = r;
    const hp = new Path2D(); hp.moveTo(x0 - 10, y1 + 10); for (let x = x0 - 10; x <= x1 + 10; x += 4) hp.lineTo(x, hillRidge(x)); hp.lineTo(x1 + 10, y1 + 10); hp.closePath();
    const col = (x, y) => mixc(mixc(hex('#141d1c'), hex('#26332a'), C.n.fbm(x * 0.006, y * 0.006, 4)), hex('#1a2036'), smoothstep(hillRidge(x) + 80, hillRidge(x), y) * 0.7);
    underpaint(C, col, hp, 6); const m = C.mask((gg) => gg.fill(hp));
    C.strokes({ n: C.area / 380, mask: m, color: col, angle: () => -0.2 + (C.R() - 0.5) * 0.8, len: [10, 34], wid: [5, 11], alpha: [0.4, 0.75], jv: 0.08, bend: 0.2 });
    // scattered shrubs and stones over the hill, smaller toward the top
    for (let i = 0; i < 520; i++) { const x = lerp(x0, x1, C.R()), y = lerp(hillRidge(x) + 6, y1, Math.pow(C.R(), 0.8)); const k = lerp(1, 0.4, clamp((760 - y) / 560)); const rr = (5 + C.R() * 12) * k;
      if (C.R() < 0.8) { C.dab(x, y, -1.3 + C.R() * 0.5, rr * 1.8, rr * 1.2, mixc(hex('#0e1614'), hex('#2c3e30'), C.R() * 0.7), 0.85, 0.3); C.dab(x - rr * 0.3, y - rr * 0.4, -2.2, rr, rr * 0.4, hex('#3a4a52'), 0.35, 0.2); }
      else { g.fillStyle = rgba(mixc(hex('#3a3a44'), hex('#55505a'), C.R()), 0.8); g.beginPath(); g.ellipse(x, y, rr * 0.8, rr * 0.4, 0, 0, 7); g.fill(); } }
    // the stone path: a ribbon, wider at the bottom
    for (let pass = 0; pass < 2; pass++) { const pts = dense(PATH, 220); for (const [x, y] of pts) { const k = lerp(1, 0.4, clamp((760 - y) / 560)); const w = (pass ? 22 : 30) * k;
      if (pass === 0) { g.fillStyle = rgba(hex('#2a2a30'), 0.9); g.beginPath(); g.ellipse(x, y, w, w * 0.32, 0, 0, 7); g.fill(); }
      else { for (let j = 0; j < 2; j++) C.dab(x + (C.R() - 0.5) * w, y + (C.R() - 0.5) * w * 0.25, (C.R() - 0.5) * 0.4, w * 0.5, w * 0.2, mixc(hex('#5a5560'), hex('#7a7068'), C.R()), 0.7, 0.1); } } }
    // flowering shrubs along the path edges (sage, with pale blossoms)
    for (let i = 0; i < 140; i++) { const p = dense(PATH, 140)[i]; const k = lerp(1, 0.4, clamp((760 - p[1]) / 560)); for (const sd of [-1, 1]) { const x = p[0] + sd * (42 + C.R() * 30) * k, y = p[1] + (C.R() - 0.3) * 8 * k; const r0 = (6 + C.R() * 8) * k;
      C.dab(x, y, -1.4 + C.R() * 0.6, r0 * 2, r0 * 1.3, mixc(hex('#3c5a44'), hex('#8BA888'), C.R() * 0.5), 0.8, 0.3); if (C.R() < 0.4) { g.fillStyle = rgba(hex('#e8dcc0'), 0.7); g.beginPath(); g.arc(x + (C.R() - 0.5) * r0, y - r0 * 0.5, 1.4 * k + 0.6, 0, 7); g.fill(); } } }
    planes.hill = S.plane('hill', D.hill, r, C.c); }
  // middle ground: cypresses and palms on both flanks (sway in the wind)
  { const r = cover(D.mid, 60); r[1] = Math.max(r[1], -200); const C = new Canvas(r, { seed: 804 }); const g = C.g;
    const cyp = (x, yb, h) => { const w = h * 0.16; const p = new Path2D(); p.moveTo(x, yb - h); p.quadraticCurveTo(x + w * 1.3, yb - h * 0.55, x + w * 0.7, yb); p.lineTo(x - w * 0.7, yb); p.quadraticCurveTo(x - w * 1.3, yb - h * 0.55, x, yb - h); p.closePath(); underpaint(C, (xx, yy) => mixc(hex('#0e1a16'), hex('#1e3026'), C.n.fbm(xx * 0.05, yy * 0.02, 3)), p, 3);
      C.strokes({ n: h * w / 40, box: [x - w * 1.3, yb - h, x + w * 1.3, yb], mask: C.mask((gg) => gg.fill(p)), color: () => mixc(hex('#132420'), hex('#2a4234'), C.R()), angle: () => -Math.PI / 2 + (C.R() - 0.5) * 0.8, len: [6, 16], wid: [3, 6], alpha: [0.5, 0.8], jv: 0.08, bend: 0.3 }); };
    const palm = (x, yb, h, lean) => { g.strokeStyle = rgba(hex('#1a1612')); g.lineWidth = h * 0.035; g.lineCap = 'round'; g.beginPath(); g.moveTo(x, yb); g.quadraticCurveTo(x + lean * h * 0.3, yb - h * 0.6, x + lean * h * 0.45, yb - h); g.stroke(); const tx = x + lean * h * 0.45, ty = yb - h;
      for (let k = 0; k < 9; k++) { const a = -Math.PI / 2 + (k - 4) * 0.42 + (C.R() - 0.5) * 0.2; const L = h * (0.32 + C.R() * 0.12); g.strokeStyle = rgba(hex('#132018')); g.lineWidth = h * 0.012; g.beginPath(); g.moveTo(tx, ty); g.quadraticCurveTo(tx + Math.cos(a) * L * 0.6, ty + Math.sin(a) * L * 0.5 - L * 0.1, tx + Math.cos(a) * L, ty + Math.sin(a) * L * 0.7 + L * 0.35); g.stroke();
        for (let j = 1; j < 10; j++) { const u = j / 10; const px = tx + Math.cos(a) * L * u, py = ty + Math.sin(a) * L * 0.7 * u + L * 0.35 * u * u; C.dab(px, py + 4, a + Math.PI / 2 * 0.6, L * 0.14, L * 0.035, hex('#17261c'), 0.9, 0.2); } } };
    cyp(150, 640, 420); cyp(240, 660, 330); cyp(1090, 600, 380); cyp(1180, 640, 460); palm(330, 690, 440, -0.25); palm(980, 680, 400, 0.3); cyp(60, 700, 360);
    paintTufts(C, { x0: r[0], x1: r[2], base: (x) => 690 + 20 * Math.sin(x * 0.01), step: 9, h0: 14, h1: 34, col: hex('#14211a'), blades: 5 });
    planes.mid = S.plane('mid', D.mid, r, C.c); planes.mid.material.uniforms.uSway.value.set(0.0018, 0.35, 9); }
  // foreground: dark blossoming bushes at the bottom corners, soft
  { const r = cover(D.fg, 60); r[1] = Math.max(r[1], 380); const C = new Canvas(r, { seed: 805 }); const g = C.g;
    for (const [cx, cy, rx, ry] of [[40, 760, 260, 170], [1260, 760, 300, 180], [640, 900, 900, 120]]) { const p = new Path2D(); p.ellipse(cx, cy, rx, ry, 0, 0, 7); underpaint(C, (x, y) => mixc(hex('#070c0b'), hex('#14211c'), C.n.fbm(x * 0.01, y * 0.01, 3)), p, 5);
      C.strokes({ n: rx * ry / 140, box: [cx - rx, cy - ry, cx + rx, cy + ry], mask: C.mask((gg) => gg.fill(p)), color: () => mixc(hex('#0b1512'), hex('#22382a'), C.R()), angle: () => -1.2 + (C.R() - 0.5) * 1.6, len: [14, 36], wid: [6, 12], alpha: [0.5, 0.85], jv: 0.06, bend: 0.3 });
      for (let k = 0; k < rx / 6; k++) { const a = C.R() * Math.PI * 2; const rr = Math.sqrt(C.R()); const x = cx + Math.cos(a) * rx * rr * 0.9, y = cy + Math.sin(a) * ry * rr * 0.9; if (y > cy - ry * 0.9) { g.fillStyle = rgba(hex('#d9cfb8'), 0.5); g.beginPath(); g.arc(x, y, 2 + C.R() * 2, 0, 7); g.fill(); } } }
    C.blur(2.2); planes.fg = S.plane('fg', D.fg, r, C.c); }
  // a low haze band in the hollow, drifting
  { const r = cover(D.mid + 5, 60); r[1] = Math.max(r[1], 200); const C = new Canvas(r, { seed: 806 }); paintFog(C, { y: (x) => 560 + 30 * Math.sin(x * 0.004), h: 40, col: hex('#3a4170'), top: hex('#5a5f90'), a: 0.6, density: 0.8 }); planes.fog = S.plane('fog', D.mid + 5, r, C.c); planes.fog.userData.drift = 1.4; }
  const stars = makeStars(807, [-800, -1400, 2100, 420], 260, 2.0);
  return {
    update(F) {
      const t = F.t, g = F.g, sh = F.shot; const gg = F.glow();
      tintAll(S, 0.42); planes.sky.material.uniforms.uTint.value.set(0.75, 0.78, 0.92); planes.fog.material.uniforms.uTint.value.set(0.5, 0.5, 0.6);
      drawStars(F, D.sky, stars, 0.95); { const p = F.P(D.sky, 1180, 80); crescent(F, p[0], p[1], 15, 0.95); }
      const lit = (i) => (sh.lamps ? igniteEnv(t, sh.lamps[i], i, 0.45) : 1);
      const Lh = []; const order = [...lamps].sort((a, b) => b.y - a.y);
      for (const l of lamps) { const on = lit(l.i); const p = F.P(D.hill, l.x, l.y); const K = F.K(D.hill, l.x, l.y); const s = l.s * K;
        // post
        g.fillStyle = 'rgba(26,20,16,0.95)'; g.fillRect(p[0] - s * 0.09, p[1] - s * 0.2, s * 0.18, s * 2.4); g.fillRect(p[0] - s * 0.4, p[1] - s * 1.25, s * 0.8, s * 0.12);
        fanous(g, p[0], p[1] - s * 0.6, s, on, t, l.i); glowLantern(gg, p[0], p[1] - s * 0.6, s, on, t, l.i, 1.1);
        if (on > 0.02) { Lh.push({ p: S.world(l.x, l.y - 10, D.hill), r: 2.6 * l.k, c: WARM, k: 1.6 * on }); if (l.k > 0.6) F.lights.push({ x: p[0], y: p[1], r: 160 * s / 15, c: WARM, k: 0.45 * on }); } }
      lightsOn(planes.hill, Lh.filter((_, i) => i % 1 === 0).slice(-8).concat(Lh.slice(0, 0)));
      lightsOn(planes.mid, Lh.slice(0, 6).map((l) => ({ ...l, p: l.p.clone().multiplyScalar(D.mid / D.hill), r: 3, k: l.k * 0.5 })));
      // fireflies over the garden (life), a faint cool sheen on the haze
      motes(gg, t, { x0: 0, y0: 380, x1: 1280, y1: 700 }, { n: 34, col: [214, 236, 150], a: 0.55, size: 1.5, seed: 31, drift: [4, -1.5] });
      F.amb = [0.95, 0.95, 1.0]; F.bloom = 0.5; F.hal = 0.25;
    },
  };
}
