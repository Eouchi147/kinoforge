// P08 "TWO CHAIRS" — 2D rigged dialogue with real lip-sync (Kokoro TTS + Rhubarb visemes) and deadpan comic timing. 12 s @ 24 fps.
// Lane: characters & comedy. Everything is drawn with Canvas 2D (paths, fills, 2–3 px outlines darker than their fill) into
// post.overlay.ctx over a black Three.js scene, so the kit's finish pass supplies the one grade, the grain and the vignette.
// Picture and sound read ONE cue file, lines/cues.json (written by build_lines.py): line starts, per-frame mouth tracks
// (Rhubarb visemes, >=2-frame holds, p/b/m closures kept), word times and the frame-exact shot cuts. audio.py reads the same file.
import * as THREE from 'three';
import { boot, makeComposer, ease, clamp, lerp, rng } from '/harness/kit/film.js';

const CUES = await (await fetch('./lines/cues.json')).json();
const FPS = CUES.fps;                                            // animation is authored in 24 fps frames
const SHOTS = CUES.shots.map((s) => ({ name: s.name, dur: s.frames / FPS }));
const CUT = CUES.shots.map((s) => s.start_frame);
const LN = Object.fromEntries(CUES.lines.map((l) => [l.id, l]));
const EV = CUES.events;
const fr = (sec) => sec * FPS;

// ------------------------------------------------------------------ cameras: which region of the stage each shot shows
// One locked camera position, a different "lens" per shot (pure crop): world point P (stage px, 1 unit = 1 px of the wide)
// is placed at screen point S (1280x720 basis) at zoom z; lw = outline width in screen px (held at 2–3 px at every zoom).
// Singles are framed on the character's real eye-line at the shot's first frame (then locked: the camera never follows).
const CAM = [
  { P: [648, 382], S: [640, 360], z: 1.1, lw: 2.0 },   // S1 WS two-shot  (≈38 mm eq.)
  { who: 'bo', S: [846, 268], z: 3.0, lw: 2.6 },       // S2 MCU Bo       (≈105 mm eq.) — Bo on the right third, lead room left
  { who: 'remi', S: [420, 250], z: 2.55, lw: 2.6 },    // S3 MCU Rémi     (≈90 mm eq.) — left third, lead room right for the gesture
  { who: 'bo', S: [834, 262], z: 4.1, lw: 2.8 },       // S4 MCU-tight Bo (one size step in from S2)
  { P: [650, 392], S: [640, 360], z: 1.42, lw: 2.2 },  // S5 MS two-shot  (≈50 mm eq.)
  { who: 'bo', S: [834, 262], z: 4.1, lw: 2.8 },       // S6 = S4 framing (reaction hold)
  { who: 'remi', S: [500, 252], z: 3.25, lw: 3.0 },    // S7 CU Rémi      (tightest size on Rémi: the emotional peak)
];

// ------------------------------------------------------------------ palette (one colour script: cool stage, warm pool; Rémi warm, Bo cool)
const COL = {
  wallTop: '#0a090f', wall: '#1b1925', fold: '#0f0d15',
  floorFar: '#0e0a09', floorNear: '#191210',
  wood: '#8a5934', woodFar: '#6b4428',
  rSkin: '#f0c29b', rHair: '#4b2c20', rCard: '#c7942f', rRib: '#a97a24', rShirt: '#eee7d6', rTrou: '#4a3b4d', rShoe: '#3b2a24', rFrame: '#2a1f1d', rBtn: '#5a3a20',
  bSkin: '#a76b47', bHat: '#2f7570', bRib: '#245c58', bHood: '#4c5f80', bPocket: '#465979', bTrou: '#2e3039', bShoe: '#ddd5c6', bSole: '#9a9388',
  mouth: '#3c1219', tongue: '#c8545c', teeth: '#f7f2e8', white: '#fbf8f1', pupil: '#23170f', lash: '#1c1113',
};
const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a, b, t) => '#' + hex(a).map((v, i) => Math.round(lerp(v, hex(b)[i], t)).toString(16).padStart(2, '0')).join('');
const ink = (c) => mix(c, '#140b16', 0.58);                      // outline = the fill, ~40% darker and cooler
const shadeOf = (c) => mix(c, '#3b2446', 0.30);                  // cel shadow: hue-shifted toward violet
const rimOf = (c) => mix(c, '#fff0d4', 0.34);                    // warm rim from the overhead spot

// ------------------------------------------------------------------ drawing core
let g = null, LW = 1, LIGHT = [0.36, -0.93];
function strokePath(build, col, w) { g.beginPath(); build(); g.strokeStyle = col; g.lineWidth = w * LW; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(); }
function fillPath(build, col) { g.beginPath(); build(); g.fillStyle = col; g.fill(); }
// a cel-shaded part: base fill; shadow crescent on the side away from the key (the shape minus itself shifted toward the
// light); thin warm rim on the lit edge; optional inner details drawn inside the clip; ink outline last.
function part(build, base, o = {}) {
  const sh = o.sh ?? shadeOf(base), hi = o.hi ?? rimOf(base), so = o.so ?? 7, ho = o.ho ?? 2.2, lw = o.lw ?? 2.4;
  const [lx, ly] = LIGHT;
  g.save(); g.beginPath(); build(); g.fillStyle = base; g.fill(); g.clip();
  if (so > 0) { g.beginPath(); g.rect(-6000, -6000, 12000, 12000); g.translate(lx * so, ly * so); build(); g.translate(-lx * so, -ly * so); g.fillStyle = sh; g.fill('evenodd'); }
  if (ho > 0) { g.beginPath(); g.rect(-6000, -6000, 12000, 12000); g.translate(-lx * ho, -ly * ho); build(); g.translate(lx * ho, ly * ho); g.fillStyle = hi; g.fill('evenodd'); }
  if (o.inner) o.inner();
  g.restore();
  if (lw > 0) strokePath(build, o.ink ?? ink(base), lw);
}
const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const len = (a) => Math.hypot(a[0], a[1]);
const nrm = (a) => { const l = len(a) || 1; return [a[0] / l, a[1] / l]; };
const rot = (p, deg) => { const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a); return [p[0] * c - p[1] * s, p[0] * s + p[1] * c]; };
function isect(p1, p2, p3, p4) {
  const d = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0]); if (Math.abs(d) < 1e-6) return null;
  const t = ((p1[0] - p3[0]) * (p3[1] - p4[1]) - (p1[1] - p3[1]) * (p3[0] - p4[0])) / d; return [p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])];
}
// one closed outline around a bent polyline (thigh→shin, upper arm→forearm, fingers): rounded joints, round caps, no seams
function limb(pts, ws) {
  const n = pts.length, N = [];
  for (let i = 0; i < n - 1; i++) { const d = nrm(sub(pts[i + 1], pts[i])); N.push([-d[1], d[0]]); }
  const off = (i, k, s) => [pts[i][0] + s * N[k][0] * ws[i], pts[i][1] + s * N[k][1] * ws[i]];
  const joint = (i, s) => {
    const a0 = off(i - 1, i - 1, s), a1 = off(i, i - 1, s), b0 = off(i, i, s), b1 = off(i + 1, i, s);
    let c = isect(a0, a1, b0, b1) || a1; const cj = sub(c, pts[i]); const cl = len(cj);
    if (cl > ws[i] * 2.2) c = [pts[i][0] + cj[0] / cl * ws[i] * 2.2, pts[i][1] + cj[1] / cl * ws[i] * 2.2];
    const r = Math.min(ws[i] * 0.9, len(sub(a1, a0)) * 0.4, len(sub(b1, b0)) * 0.4);
    const da = nrm(sub(a1, a0)), db = nrm(sub(b1, b0));
    return [[c[0] - da[0] * r, c[1] - da[1] * r], c, [c[0] + db[0] * r, c[1] + db[1] * r]];
  };
  const th = (v) => Math.atan2(v[1], v[0]);
  const p0 = off(0, 0, 1); g.moveTo(p0[0], p0[1]);
  for (let i = 1; i < n - 1; i++) { const [pa, c, pb] = joint(i, 1); g.lineTo(pa[0], pa[1]); g.quadraticCurveTo(c[0], c[1], pb[0], pb[1]); }
  const pe = off(n - 1, n - 2, 1); g.lineTo(pe[0], pe[1]);
  g.arc(pts[n - 1][0], pts[n - 1][1], ws[n - 1], th(N[n - 2]), th(N[n - 2]) - Math.PI, true);
  for (let i = n - 2; i >= 1; i--) { const [pa, c, pb] = joint(i, -1); g.lineTo(pb[0], pb[1]); g.quadraticCurveTo(c[0], c[1], pa[0], pa[1]); }
  const ps = off(0, 0, -1); g.lineTo(ps[0], ps[1]);
  g.arc(pts[0][0], pts[0][1], ws[0], th(N[0]) + Math.PI, th(N[0]), true);
  g.closePath();
}
// two-bone IK (bend = +1 puts the elbow below/behind the shoulder→wrist line for a figure facing +x)
function ik(S, T, a, b, bend = 1) {
  const d = sub(T, S); const dl = len(d) || 1; const dc = clamp(dl, Math.abs(a - b) + 0.5, a + b - 0.5);
  const base = Math.atan2(d[1], d[0]); const ang = Math.acos(clamp((a * a + dc * dc - b * b) / (2 * a * dc), -1, 1));
  const E = [S[0] + a * Math.cos(base + bend * ang), S[1] + a * Math.sin(base + bend * ang)];
  return { E, W: [S[0] + d[0] / dl * dc, S[1] + d[1] / dl * dc] };
}
// a five-digit cartoon hand at wrist W pointing along `ang`; open 0 = relaxed/curled, 1 = spread presenting hand.
// Drawn as an ink underlay + fill so the union of palm and fingers reads as one silhouette.
function hand(W, ang, s, open, skin, thumbSide = -1) {
  g.save(); g.translate(W[0], W[1]); g.rotate(ang); g.scale(1, thumbSide < 0 ? 1 : -1);
  const sp = lerp(0.18, 0.62, open), curl = lerp(1.05, 0.04, open);
  const shapes = [() => g.ellipse(s * 0.42, s * 0.02, s * 0.5, s * 0.38, 0, 0, Math.PI * 2)];
  [[-1.5, 0.92], [-0.5, 1.06], [0.5, 1.0], [1.5, 0.82]].forEach(([k, lf]) => {
    const a0 = k * sp * 0.42, L = s * 0.62 * lf, bx = s * 0.8, by = k * s * 0.16;
    const m = [bx + Math.cos(a0) * L * 0.55, by + Math.sin(a0) * L * 0.55]; const a1 = a0 + curl * 1.15;
    const tp = [m[0] + Math.cos(a1) * L * 0.5, m[1] + Math.sin(a1) * L * 0.5];
    shapes.push(() => limb([[bx, by], m, tp], [s * 0.115, s * 0.105, s * 0.09]));
  });
  const ta = lerp(-1.0, -1.45, open), t0 = [s * 0.32, -s * 0.24], t1 = [t0[0] + Math.cos(ta) * s * 0.34, t0[1] + Math.sin(ta) * s * 0.34];
  const t2 = [t1[0] + Math.cos(ta + 0.55 * (1 - open) + 0.15) * s * 0.3, t1[1] + Math.sin(ta + 0.55 * (1 - open) + 0.15) * s * 0.3];
  shapes.push(() => limb([t0, t1, t2], [s * 0.14, s * 0.12, s * 0.1]));
  g.lineJoin = 'round'; g.strokeStyle = ink(skin); g.lineWidth = 2 * 2.2 * LW;
  for (const f of shapes) { g.beginPath(); f(); g.stroke(); }
  g.fillStyle = skin; for (const f of shapes) { g.beginPath(); f(); g.fill(); }
  g.restore();
}

// ------------------------------------------------------------------ face kit (eyes, lids, brows, 9 Rhubarb mouths)
function eye(e) { // { x, y, rx, ry, gx, gy, pr, cover 0..1, lid (lid colour), skin, lash (px), heavy }
  if (e.cover >= 0.97) { strokePath(() => { g.moveTo(e.x - e.rx * 1.05, e.y + e.ry * 0.1); g.quadraticCurveTo(e.x, e.y + e.ry * 0.62, e.x + e.rx * 1.05, e.y + e.ry * 0.1); }, COL.lash, e.lash); return; }
  const white = () => g.ellipse(e.x, e.y, e.rx, e.ry, 0, 0, Math.PI * 2);
  const yl = e.y - e.ry + 2 * e.ry * e.cover, bul = e.ry * 0.42;
  g.save(); g.beginPath(); white(); g.fillStyle = COL.white; g.fill(); g.clip();
  const px = e.x + e.gx, py = e.y + e.gy;
  g.beginPath(); g.arc(px, py, e.pr, 0, Math.PI * 2); g.fillStyle = COL.pupil; g.fill();
  g.beginPath(); g.arc(px + e.pr * 0.36, py - e.pr * 0.4, e.pr * 0.33, 0, Math.PI * 2); g.fillStyle = '#ffffff'; g.fill();   // catchlight, key side
  g.beginPath(); g.moveTo(e.x - e.rx - 3, e.y - e.ry - 6); g.lineTo(e.x + e.rx + 3, e.y - e.ry - 6); g.lineTo(e.x + e.rx + 3, yl);
  g.quadraticCurveTo(e.x, yl + bul, e.x - e.rx - 3, yl); g.closePath(); g.fillStyle = e.lid; g.fill();
  g.restore();
  strokePath(white, ink(e.skin), 1.3);
  g.save(); g.beginPath(); g.ellipse(e.x, e.y, e.rx + 1.2, e.ry + 1.2, 0, 0, Math.PI * 2); g.clip();
  strokePath(() => { g.moveTo(e.x - e.rx - 3, yl); g.quadraticCurveTo(e.x, yl + bul, e.x + e.rx + 3, yl); }, COL.lash, e.lash);
  g.restore();
}
function brow(p0, p1, arch, th, col) { // p0 = inner end (toward the nose), p1 = outer end
  const m = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - arch];
  part(() => limb([p0, m, p1], [th, th * 0.92, th * 0.5]), col, { so: 0, ho: 0, lw: 1.4 });
}
const VIS = {   // Rhubarb mouth chart. w = width factor, o = opening (fraction of max height), rnd = corner rounding
  X: { w: 1.0, o: 0 }, A: { w: 0.9, o: 0, press: true }, B: { w: 1.0, o: 0.24, both: true },
  C: { w: 1.0, o: 0.52, tongue: 0.45 }, D: { w: 1.1, o: 1.0, tongue: 0.6 }, E: { w: 0.74, o: 0.6, rnd: 0.65, tongue: 0.35 },
  F: { w: 0.46, o: 0.32, rnd: 1.0, pucker: true }, G: { w: 0.9, o: 0.36, bite: true }, H: { w: 0.96, o: 0.52, tongueUp: true },
};
function mouthShape(v, m) { // m: { x, y, w, h, smile (-1..1), skin } in head-local units; the far corner (+x) is foreshortened
  const S = VIS[v] || VIS.X, w = m.w * S.w, o = S.o * m.h;
  const xl = m.x - w * 0.56, xr = m.x + w * 0.44, cy = m.y - m.smile * m.h * 0.2, yr = cy - m.h * 0.05;
  const lc = ink(m.skin);
  if (o === 0) {
    if (S.press) { // A — lips pressed: straight compressed seam, lower-lip bulge, tucked corners
      strokePath(() => { g.moveTo(xl, cy + 0.3); g.quadraticCurveTo(m.x, m.y + 0.4, xr, yr); }, lc, 2.7);
      strokePath(() => { g.moveTo(m.x - w * 0.24, m.y + m.h * 0.3); g.quadraticCurveTo(m.x, m.y + m.h * 0.46, m.x + w * 0.2, m.y + m.h * 0.28); }, mix(m.skin, '#6a2b2e', 0.42), 1.5);
      strokePath(() => { g.moveTo(xl - 0.5, cy - m.h * 0.12); g.lineTo(xl + 0.6, cy + m.h * 0.1); }, lc, 1.5);
    } else { // X — relaxed rest: a soft curve that follows the expression
      strokePath(() => { g.moveTo(xl + w * 0.06, cy); g.quadraticCurveTo(m.x, m.y + m.h * (0.06 + m.smile * 0.3), xr - w * 0.05, yr); }, lc, 2.0);
    }
    return;
  }
  const rnd = S.rnd || 0, a = lerp(0.24, 0.03, rnd), top = m.y - o * 0.3, bot = m.y + o * 0.7;
  const cTop = (8 * top - 2 * cy) / 6, cBot = (8 * bot - 2 * cy) / 6;
  const contour = () => { g.moveTo(xl, cy); g.bezierCurveTo(xl + w * a, cTop, xr - w * a, cTop, xr, yr); g.bezierCurveTo(xr - w * a, cBot, xl + w * a, cBot, xl, cy); g.closePath(); };
  if (S.pucker) strokePath(contour, mix(m.skin, '#b0534f', 0.4), 4.2);                       // pushed-out lip ring
  g.save(); g.beginPath(); contour(); g.fillStyle = COL.mouth; g.fill(); g.clip();
  if (!S.pucker) { g.fillStyle = COL.teeth; g.fillRect(xl - 2, top - m.h, w + 4, m.h * (S.both ? 1.0 : 0.8) + (S.bite ? m.h * 0.12 : 0)); }
  if (S.both) { g.fillStyle = COL.teeth; g.fillRect(xl - 2, m.y + o * 0.12, w + 4, m.h); strokePath(() => { g.moveTo(xl, m.y + o * 0.08); g.lineTo(xr, m.y + o * 0.06); }, mix(COL.teeth, '#7a6a68', 0.5), 1.0); }
  if (S.tongue) fillPath(() => g.ellipse(m.x - w * 0.04, bot + o * 0.05, w * 0.34, o * S.tongue * 0.75, 0, 0, Math.PI * 2), COL.tongue);
  if (S.tongueUp) fillPath(() => g.ellipse(m.x + w * 0.06, top + o * 0.42, w * 0.2, o * 0.34, 0, 0, Math.PI * 2), COL.tongue);
  const lipTop = () => { g.moveTo(xl - 1, m.y + o * 0.2); g.quadraticCurveTo(m.x, m.y - o * 0.12, xr + 1, m.y + o * 0.16); };
  if (S.bite) { fillPath(() => { lipTop(); g.lineTo(xr + 2, bot + 8); g.lineTo(xl - 2, bot + 8); g.closePath(); }, mix(m.skin, '#b04f55', 0.5)); strokePath(lipTop, lc, 1.5); }   // lower lip tucked under the upper teeth
  g.restore();
  strokePath(contour, lc, 2.1);
}

// ------------------------------------------------------------------ the stage
function drawStage(cam) {
  // faint back wall: a dark stage curtain with soft vertical folds, warmed by the spill of the overhead spot
  let gr = g.createLinearGradient(-900, 0, 2200, 0);
  for (let k = 0; k <= 96; k++) { const u = k / 96; const ph = 0.5 + 0.5 * Math.sin(u * Math.PI * 2 * 24 + 1.7 * Math.sin(u * 31)); gr.addColorStop(u, mix(COL.fold, COL.wall, 0.35 + 0.65 * ph)); }
  g.fillStyle = gr; g.fillRect(-900, -800, 3100, 1202);
  gr = g.createRadialGradient(650, 330, 30, 650, 330, 620); gr.addColorStop(0, 'rgba(255,196,140,0.17)'); gr.addColorStop(0.5, 'rgba(255,180,130,0.07)'); gr.addColorStop(1, 'rgba(255,180,130,0)');
  g.fillStyle = gr; g.fillRect(-900, -800, 3100, 1202);
  gr = g.createLinearGradient(0, -120, 0, 250); gr.addColorStop(0, 'rgba(6,5,9,0.92)'); gr.addColorStop(1, 'rgba(6,5,9,0)');
  g.fillStyle = gr; g.fillRect(-900, -800, 3100, 1050);
  // floor (dark stage boards) + the warm pool of the overhead spot (perspective ellipse)
  gr = g.createLinearGradient(0, 400, 0, 740); gr.addColorStop(0, COL.floorFar); gr.addColorStop(1, COL.floorNear);
  g.fillStyle = gr; g.fillRect(-900, 400, 3100, 700);
  g.save(); g.translate(648, 566); g.scale(1, 0.235);
  gr = g.createRadialGradient(0, 0, 0, 0, 0, 520); gr.addColorStop(0, 'rgba(198,140,86,0.86)'); gr.addColorStop(0.42, 'rgba(158,103,62,0.56)'); gr.addColorStop(0.78, 'rgba(110,70,42,0.17)'); gr.addColorStop(1, 'rgba(110,70,42,0)');
  g.fillStyle = gr; g.beginPath(); g.arc(0, 0, 520, 0, Math.PI * 2); g.fill(); g.restore();
  g.strokeStyle = 'rgba(14,8,6,0.38)'; g.lineWidth = 1.1 * LW;
  for (let k = 1; k < 18; k++) { const y = 401 + 340 * Math.pow(k / 18, 1.45); g.beginPath(); g.moveTo(-900, y); g.lineTo(2200, y); g.stroke(); }
  // curtain hem meets the floor: contact shadow band
  gr = g.createLinearGradient(0, 396, 0, 418); gr.addColorStop(0, 'rgba(0,0,0,0.75)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(-900, 396, 3100, 22);
  // soft shadow ellipses under the chairs (spot is overhead, so they sit under the chairs, pushed a little off-centre)
  const sh = (x, y, rx, ry, a) => { g.save(); g.translate(x, y); g.scale(1, ry / rx); const r = g.createRadialGradient(0, 0, 0, 0, 0, rx); r.addColorStop(0, `rgba(8,4,3,${a})`); r.addColorStop(0.6, `rgba(8,4,3,${a * 0.55})`); r.addColorStop(1, 'rgba(8,4,3,0)'); g.fillStyle = r; g.beginPath(); g.arc(0, 0, rx, 0, Math.PI * 2); g.fill(); g.restore(); };
  sh(412, 603, 104, 17, 0.62); sh(898, 603, 98, 16, 0.62);
  sh(526, 601, 30, 5, 0.5); sh(546, 595, 28, 4.5, 0.42);        // Rémi's shoes (contact)
  sh(814, 606, 34, 6, 0.28);                                     // under Bo's dangling feet (no contact)
}
const MOTES = (() => { const r = rng(808); return Array.from({ length: 64 }, () => ({ x: 380 + r() * 540, y: -20 + r() * 560, s: 0.8 + r() * 1.4, a: 0.5 + r() * 0.5, p: r() * 6.28, v: 0.4 + r() * 0.8 })); })();
function spotHaze(f, z) { // the overhead spot's cone through stage haze — the visible source of the key; motes drift slowly in it
  const t = f / FPS;
  g.save(); g.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 6; k++) {    // six nested cones = a soft-edged volume, densest in the core
    const w = 0.55 + k * 0.11, gr = g.createLinearGradient(0, -260, 0, 566);
    gr.addColorStop(0, 'rgba(255,214,160,0.016)'); gr.addColorStop(0.55, 'rgba(255,200,150,0.008)'); gr.addColorStop(1, 'rgba(255,190,140,0)');
    g.fillStyle = gr; g.beginPath(); g.moveTo(648 - 88 * w, -260); g.lineTo(648 + 88 * w, -260); g.lineTo(648 + 492 * w, 566); g.lineTo(648 - 492 * w, 566); g.closePath(); g.fill();
  }
  for (const m of MOTES) {
    const x = m.x + 9 * Math.sin(t * 0.23 * m.v + m.p), y = m.y + ((t * 3.2 * m.v + m.p * 40) % 560) * 0.08 + 6 * Math.sin(t * 0.31 + m.p * 2);
    const edge = Math.max(0, 1 - Math.abs(x - 648) / (88 + (y + 260) * 0.49));          // inside the cone only
    const a = 0.22 * m.a * edge * Math.max(0, 1 - y / 560);
    if (a < 0.01) continue;
    g.fillStyle = `rgba(255,226,186,${a.toFixed(3)})`; g.beginPath(); g.arc(x, y, m.s * 1.2 / z, 0, Math.PI * 2); g.fill();
  }
  g.restore();
}
function spotFalloff() { // the overhead spot falls off toward the wings: outer sides of both figures sink a little
  const gr = g.createRadialGradient(648, 420, 240, 648, 420, 900); gr.addColorStop(0, 'rgba(4,2,6,0)'); gr.addColorStop(1, 'rgba(4,2,6,0.55)');
  g.fillStyle = gr; g.fillRect(-900, -800, 3100, 1700);
}
function drawStageLip() { // foreground plane in the wide: the front edge of the stage, lit along its lip
  const gr = g.createLinearGradient(0, 694, 0, 740); gr.addColorStop(0, '#2a1d15'); gr.addColorStop(0.08, '#120c0a'); gr.addColorStop(1, '#050304');
  g.fillStyle = gr; g.fillRect(-900, 694, 3100, 200);
}

// ------------------------------------------------------------------ chair (in the sitter's local frame: facing +x, seat top y=8, floor y=138)
const FAR = [17, -8];   // the far side of anything, in this 3/4 view
function chair(ox) {
  const leg = (x, y0, y1, far) => part(() => { g.moveTo(x - 4.2, y0); g.lineTo(x + 4.2, y0); g.lineTo(x + 3.3, y1); g.lineTo(x - 3.3, y1); g.closePath(); }, far ? COL.woodFar : COL.wood, { so: 3, ho: 1.2, lw: 2.0 });
  const post = (x, y0, y1, far) => part(() => { g.moveTo(x - 4.4, y0); g.lineTo(x + 4.4, y0); g.lineTo(x + 4.0, y1); g.quadraticCurveTo(x, y1 - 4, x - 4.0, y1); g.closePath(); }, far ? COL.woodFar : COL.wood, { so: 3, ho: 1.4, lw: 2.0 });
  const bx = ox - 38, fx = ox + 30;
  leg(fx + FAR[0], 14 + FAR[1], 138 + FAR[1], true); post(bx + FAR[0], 138 + FAR[1], -150 + FAR[1], true);
  const slat = (y0, h) => part(() => { g.moveTo(bx, y0); g.lineTo(bx + FAR[0], y0 + FAR[1]); g.lineTo(bx + FAR[0], y0 + FAR[1] + h); g.lineTo(bx, y0 + h); g.closePath(); }, COL.wood, { so: 2, ho: 1.2, lw: 1.8 });
  slat(-146, 16); slat(-96, 10);
  part(() => { g.moveTo(ox + 34, 8); g.lineTo(ox - 42, 8); g.lineTo(ox - 42 + FAR[0], 8 + FAR[1]); g.lineTo(ox + 34 + FAR[0], 8 + FAR[1]); g.closePath(); }, mix(COL.wood, '#ffe0b0', 0.12), { so: 0, ho: 0, lw: 1.8 });
  part(() => { g.moveTo(ox + 34, 8); g.lineTo(ox + 34 + FAR[0], 8 + FAR[1]); g.lineTo(ox + 34 + FAR[0], 15 + FAR[1]); g.lineTo(ox + 34, 15); g.closePath(); }, mix(COL.wood, '#000000', 0.18), { so: 0, ho: 0, lw: 1.6 });
  part(() => { g.moveTo(ox - 42, 8); g.lineTo(ox + 34, 8); g.lineTo(ox + 34, 15); g.lineTo(ox - 42, 15); g.closePath(); }, COL.wood, { so: 0, ho: 1.2, lw: 1.8 });
  leg(fx, 15, 138, false); post(bx, 138, -150, false);
}

// ------------------------------------------------------------------ animation helpers (everything is a pure function of the frame)
const ramp = (f, f0, d, e = ease.inOutSine) => e(clamp((f - f0) / d));
const bump = (f, fc, w) => Math.exp(-(((f - fc) / w) ** 2));
// anticipation (counter-move over dA frames) → action with overshoot and settle (outBack over dB frames)
const act = (f, f0, dA, dB, counter, amount) => f < f0 - dA ? 0 : f < f0 ? -counter * ease.inOutSine((f - (f0 - dA)) / dA) : lerp(-counter, amount, ease.outBack(clamp((f - f0) / dB)));
const BLINK = { reg: [0.45, 0.85, 1, 0.72, 0.42, 0.15], fast: [0.5, 0.95, 0.7, 0.4, 0.15], slow: [0.3, 0.6, 0.86, 1, 1, 0.8, 0.55, 0.3, 0.1] }; // 2/1/3, 2/0/3, 3/2/4
const blinkAt = (f, list) => list.reduce((c, [f0, k]) => { const i = Math.floor(f + 1e-6) - f0; return i >= 0 && i < BLINK[k].length ? Math.max(c, BLINK[k][i]) : c; }, 0);
const mouthAt = (who, f) => CUES.mouth[who][clamp(Math.floor(f + 1e-6), 0, CUES.total_frames - 1)] || 'X';
const wordF = (id, w, k = 0, off = 0) => { const L = LN[id]; const h = L.words.filter((x) => x[2] === w); return h[k] ? fr(L.start + h[k][0] + off) : null; };

// stressed syllables → small head dips + brow pops (Rémi only; Bo never moves)
const ACC = [['L1', 'rehearsed', 0.12], ['L1', 'speech', 0.05], ['L1', 'weeks', 0.05], ['L3', 'three', 0.04], ['L3', 'mirror', 0.05], ['L3', 'hand', 0.04], ['L5', 'mirror', 0.05], ['L5', 'no', 0.05]]
  .map(([id, w, o]) => wordF(id, w, 0, o)).filter((x) => x !== null);
const F_HAND = Math.round(fr(EV.hand)), F_C1 = Math.round(fr(EV.creak1)), F_REL = CUT[3] + 6;
const R_BLINKS = [[8, 'reg'], [F_C1 - 1, 'reg'], [Math.round(fr(LN.L3.off)) + 2, 'reg'], [Math.ceil(fr(LN.L5.off)) + 2, 'fast'], [CUT[6] + 4, 'slow']];   // breath-in, head move, pride beat, after "no.", the deflation
const R_DARTS = [[64, 4, -2.6, 0.4], [Math.round(fr(LN.L3.start + LN.L3.gaps[0][0])) + 1, 4, -2.4, -3.2], [Math.round(fr(LN.L3.start + LN.L3.gaps[1][0])) + 1, 3, 0.4, -3.6], [Math.round(wordF('L5', 'said')) - 1, 4, -1.4, 3.0]];
const B_BLINKS = [[CUT[5] + 1, 'slow']];   // Bo's one blink, in the reaction hold

function remiPose(f) {
  const t = f / FPS, defl = ramp(f, CUT[6] + 1, 10, ease.outCubic);
  const breath = Math.sin(2 * Math.PI * t / 3.5 + 0.9);
  const gestA = f < F_HAND - 5 ? 0 : f < F_HAND ? ease.inOutSine((f - F_HAND + 5) / 5) : 1;          // anticipation weight
  const gestG = f < F_HAND ? 0 : ease.outBack(clamp((f - F_HAND) / 14));                              // action (overshoot) + 8-frame settle
  const rel = ramp(f, F_REL, 12);                                                                     // hands back to the knees off-screen (S4)
  let lean = 5 + act(f, 62, 3, 10, 0.6, 1.5) + act(f, F_C1, 3, 10, 1.2, 2.5) + act(f, F_HAND, 5, 14, -1.4, -4.6) * (1 - rel)
    + act(f, CUT[4], 3, 9, 0.8, 2.0) + 1.5 * defl;
  const hipX = 1.5 * ramp(f, 60, 10) + 2 * ramp(f, F_C1, 10);
  let nod = 0; for (const fa of ACC) nod += bump(f, fa, 2.3);
  let nodLag = 0; for (const fa of ACC) nodLag += bump(f - 3, fa, 2.6);
  const pride = gestG * (1 - rel);
  return {
    breath, lean, hipX, defl, nod, nodLag, gestA: gestA * (1 - rel), gestG: gestG * (1 - rel), pride,
    tilt: -1.5 + 2.5 * act(f, F_C1, 3, 10, 0.5, 1) - 3 * pride + 1.5 * defl,
    blink: blinkAt(f, R_BLINKS), gaze: (() => { for (const [f0, d, dx, dy] of R_DARTS) if (f >= f0 && f < f0 + d) return [dx, dy]; return defl > 0.5 && f > CUT[6] + 9 ? [1.4, 2.8] : [2.3, 1.5]; })(),
    raise: 0.5 + 0.28 * Math.min(1, nod) + 0.35 * pride + 0.4 * defl, knit: 0.45 + (f >= CUT[4] ? 0.25 : 0) + 0.35 * defl - 0.2 * pride,
    smile: f < CUT[4] ? 0.35 + 0.45 * pride : lerp(0.05, -0.75, defl),
    mouth: mouthAt('remi', f), slip: 1.6 * defl,
  };
}
function boPose(f) {
  const t = f / FPS;
  return { breath: Math.sin(2 * Math.PI * t / 3.5 + 2.4), tilt: 3.0 * ramp(f, CUT[3], 6), blink: blinkAt(f, B_BLINKS), mouth: mouthAt('bo', f) };
}

// ------------------------------------------------------------------ RÉMI — tall, thin, nervous (local frame: facing +x, origin = hip on the seat)
const R = { upper: 58, fore: 54 };
const remiTorso = () => {
  g.moveTo(-27, 9); g.bezierCurveTo(-31, -30, -29, -92, -22, -128); g.bezierCurveTo(-18, -150, -6, -164, 8, -165);
  g.bezierCurveTo(18, -166, 28, -161, 33, -150); g.bezierCurveTo(38, -128, 35, -100, 31, -72); g.bezierCurveTo(28, -44, 33, -12, 40, 7); g.closePath();
};
const remiHead = () => {
  g.moveTo(-20, 30); g.bezierCurveTo(-34, 18, -40, -6, -36, -24); g.bezierCurveTo(-32, -44, -12, -52, 6, -50);
  g.bezierCurveTo(24, -48, 34, -36, 35, -20); g.bezierCurveTo(36, -10, 34, -2, 35, 4); g.bezierCurveTo(37, 12, 36, 20, 33, 28);
  g.bezierCurveTo(31, 36, 31, 42, 26, 47); g.bezierCurveTo(20, 52, 8, 50, -2, 44); g.bezierCurveTo(-10, 40, -16, 36, -20, 30); g.closePath();
};
const remiHair = () => {
  g.moveTo(-22, 27); g.bezierCurveTo(-37, 14, -43, -8, -39, -27); g.bezierCurveTo(-35, -49, -12, -59, 8, -56); g.bezierCurveTo(26, -53, 37, -43, 34, -31);
  g.bezierCurveTo(29, -39, 20, -44, 10, -42); g.bezierCurveTo(2, -40, -6, -41, -11, -34); g.bezierCurveTo(-16, -23, -18, -6, -17, 8); g.bezierCurveTo(-17, 16, -19, 22, -22, 27); g.closePath();
};
function remiLeg(o, far) {
  const hip = far ? [12, -4] : [4, 0], knee = far ? [88, -27] : [76, -22], ank = far ? [106, 117] : [90, 122], k = far ? [0, -6] : [0, 0];
  part(() => limb([hip, knee, ank], far ? [11.5, 10, 7.8] : [11.5, 9.5, 7.2]), far ? mix(COL.rTrou, '#140c16', 0.16) : COL.rTrou, { so: 6, ho: 1.8, lw: 2.2 });
  const fy = 138 + k[1], hx = ank[0] - 9;
  part(() => { g.moveTo(hx, fy); g.lineTo(hx + 34, fy); g.quadraticCurveTo(hx + 45, fy, hx + 44, fy - 7); g.quadraticCurveTo(hx + 40, fy - 15, hx + 22, fy - 15); g.quadraticCurveTo(hx + 2, fy - 18, hx, fy - 9); g.closePath(); },
    far ? mix(COL.rShoe, '#000', 0.2) : COL.rShoe, { so: 3, ho: 1.5, lw: 2.0 });
}
function remiArm(S, T, far, open, P) {
  const { E, W } = ik(S, T, R.upper, R.fore, 1);
  const sleeve = far ? mix(COL.rCard, '#4a2e1a', 0.22) : COL.rCard;
  const wr = [lerp(E[0], W[0], 0.88), lerp(E[1], W[1], 0.88)];
  const fa = Math.atan2(W[1] - E[1], W[0] - E[0]);
  // hand first (sleeve cuff overlaps the wrist)
  const handAng = fa + lerp(0.55, -0.35, P.gestG) + (far ? 0.12 : 0);
  hand(W, handAng, 17, lerp(0.15, 1.0, P.gestG) - 0.12 * P.gestA, far ? mix(COL.rSkin, '#7a4a3a', 0.16) : COL.rSkin, far ? 1 : -1);
  part(() => limb([S, E, wr], [9.5, 8, 7.4]), sleeve, { so: 5, ho: 1.8, lw: 2.2 });
  part(() => limb([wr, [lerp(E[0], W[0], 0.99), lerp(E[1], W[1], 0.99)]], [7.8, 7.8]), far ? mix(COL.rRib, '#4a2e1a', 0.22) : COL.rRib, { so: 0, ho: 0, lw: 2.0 });
}
function remiFace(P) {
  part(remiHead, COL.rSkin, { so: 9, ho: 2.4, sh: mix(COL.rSkin, '#9a4f56', 0.28) });
  // hair + cowlick (the cowlick lags the head by 3 frames: overlapping action)
  part(remiHair, COL.rHair, { so: 6, ho: 2.6, hi: mix(COL.rHair, '#ffcf96', 0.32) });
  g.save(); g.translate(-15, -53); g.rotate((-8 + 9 * (P.nodLag - P.nod) - 0.6 * P.tilt) * Math.PI / 180);
  part(() => { g.moveTo(-6, 3); g.bezierCurveTo(-11, -10, -6, -24, 6, -27); g.bezierCurveTo(12, -28, 15, -22, 11, -18); g.bezierCurveTo(4, -20, 1, -12, 5, 3); g.closePath(); }, COL.rHair, { so: 3, ho: 1.8, hi: mix(COL.rHair, '#ffcf96', 0.32), lw: 2.0 });
  g.restore();
  part(() => { g.ellipse(-16, 6, 8, 12, -0.15, 0, Math.PI * 2); }, COL.rSkin, { so: 3, ho: 1.2, sh: mix(COL.rSkin, '#9a4f56', 0.28), lw: 2.0,
    inner: () => strokePath(() => { g.moveTo(-14, -1); g.quadraticCurveTo(-20, 4, -15, 12); }, mix(COL.rSkin, '#7a3a3a', 0.4), 1.4) });
  // eyes (big, anxious, slightly covered when calm)
  const cover = Math.max(P.blink, 0.06 + 0.06 * P.defl), lid = mix(COL.rSkin, '#b77a64', 0.25);
  fillPath(() => g.ellipse(7, 15, 7.5, 4.6, 0, 0, Math.PI * 2), 'rgba(226,116,104,0.16)');                                     // cheek warmth
  eye({ x: 3, y: -6, rx: 9, ry: 10.5, gx: P.gaze[0], gy: P.gaze[1], pr: 4.4, cover, lid, skin: COL.rSkin, lash: 2.6 });
  eye({ x: 24.5, y: -6, rx: 5.8, ry: 9.6, gx: P.gaze[0] * 0.7, gy: P.gaze[1], pr: 3.7, cover, lid, skin: COL.rSkin, lash: 2.4 });
  // long nose breaking the far contour
  part(() => { g.moveTo(15, -4); g.bezierCurveTo(19, 4, 33, 4, 40, 10); g.bezierCurveTo(44, 14, 40, 19, 33, 18); g.bezierCurveTo(28, 21, 22, 19, 20, 15); g.bezierCurveTo(17, 9, 16, 3, 15, -4); g.closePath(); },
    COL.rSkin, { so: 4, ho: 1.6, sh: mix(COL.rSkin, '#9a4f56', 0.28), lw: 2.1 });
  strokePath(() => { g.moveTo(25, 15.5); g.quadraticCurveTo(28, 17.5, 30.5, 15.8); }, mix(COL.rSkin, '#7a3a3a', 0.45), 1.3);
  mouthShape(P.mouth, { x: 20, y: 31, w: 22, h: 15, smile: P.smile, skin: COL.rSkin });
  // round glasses (they slip a hair down the nose in the deflation)
  const gy = -6 + P.slip, fcol = COL.rFrame;
  const lens = [() => g.arc(3, gy, 13.5, 0, Math.PI * 2), () => g.ellipse(25, gy, 8.4, 12.6, 0, 0, Math.PI * 2)];
  for (const L of lens) { g.save(); g.beginPath(); L(); g.fillStyle = 'rgba(205,225,255,0.10)'; g.fill(); g.clip();
    strokePath(() => { g.moveTo(-2, gy - 18); g.lineTo(40, gy + 24); }, 'rgba(255,255,255,0.0)', 1); g.restore(); }
  g.save(); g.beginPath(); lens[0](); g.clip(); strokePath(() => { g.moveTo(5, gy - 13); g.lineTo(14, gy - 4); }, 'rgba(255,250,240,0.55)', 2.4); g.restore();
  g.save(); g.beginPath(); lens[1](); g.clip(); strokePath(() => { g.moveTo(25.5, gy - 12); g.lineTo(31.5, gy - 5); }, 'rgba(255,250,240,0.5)', 1.9); g.restore();
  strokePath(lens[0], fcol, 2.5); strokePath(lens[1], fcol, 2.2);
  strokePath(() => { g.moveTo(15.8, gy - 3); g.quadraticCurveTo(16.4, gy - 7.5, 17.2, gy - 4); }, fcol, 2.2);
  strokePath(() => { g.moveTo(-10.4, gy - 2); g.lineTo(-15, gy + 1 - P.slip * 0.5); }, fcol, 2.3);
  // big expressive brows above the frames: up/in = anxious (inner ends rise toward the nose)
  const by = -24 - 6 * P.raise, kn = 6 * P.knit, bcol = mix(COL.rHair, '#120806', 0.25);
  brow([13, by - kn], [-9, by + 3], 2.6 - kn * 0.25, 4.1, bcol);
  brow([19.5, by - kn * 0.85], [33, by + 3.2], 1.6 - kn * 0.2, 3.3, bcol);
}
function drawRemi(P) {
  g.save(); g.translate(420 + P.hipX, 462); LIGHT = [0.36, -0.93];
  chair(0);
  const ts = 1 + 0.010 * P.breath - 0.024 * P.defl;                  // breathing torso; deflation drops the shoulders 4 px
  const tor = (p) => rot([p[0], p[1] * ts], P.lean);                // torso-local → hip-local
  // arm targets: rest (hands on knees) → anticipation (gather in) → gesture (presenting toward Bo)
  const pose = (k) => ({ n: [[66, -34], [40, -86], [116, -188]][k], f: [[80, -44], [50, -98], [106, -142]][k] });   // rest / gather / present
  const lerpP = (a, b, u) => [lerp(a[0], b[0], u), lerp(a[1], b[1], u)];
  const hold = Math.sin(f_now * 0.21) * 1.2 * P.pride;
  const tgt = (key) => { const r = pose(0)[key], a = pose(1)[key], gg = pose(2)[key]; const p = lerpP(r, a, P.gestA * (1 - P.gestG)); return lerpP(p, [gg[0], gg[1] - hold], P.gestG); };
  const shN = tor([6, -150]), shF = tor([6 + FAR[0] * 0.55, -150 + FAR[1] * 0.5]);
  remiLeg(P, true);
  remiArm(shF, tgt('f'), true, 0, P);
  remiLeg(P, false);
  // torso (rotated by the lean around the hip; breathing scale)
  g.save(); g.rotate(P.lean * Math.PI / 180); g.scale(1, ts);
  part(remiTorso, COL.rCard, { so: 8, ho: 2.4, inner: () => {
    fillPath(() => { g.moveTo(-40, -3); g.lineTo(60, -3); g.lineTo(60, 20); g.lineTo(-40, 20); g.closePath(); }, COL.rRib);   // ribbed hem
    strokePath(() => { g.moveTo(25, -123); g.bezierCurveTo(27, -80, 30, -30, 38, 6); }, ink(COL.rCard), 1.6);                   // placket
    for (const u of [0.18, 0.42, 0.66]) { const y = lerp(-118, 0, u), x = 25.5 + 12 * u * u; fillPath(() => g.arc(x + 2.5, y, 2.7, 0, Math.PI * 2), COL.rBtn); }
  } });
  part(() => { g.moveTo(9, -164); g.lineTo(28, -159); g.lineTo(25, -122); g.closePath(); }, COL.rShirt, { so: 2, ho: 0, lw: 1.8 });       // shirt in the V
  g.restore();
  // neck + head (head pivots at the neck top: nods on stressed syllables, tilt for attitude)
  const nb = tor([16, -160]);
  g.save(); g.translate(nb[0], nb[1]); g.rotate(P.lean * 0.6 * Math.PI / 180);
  part(() => { g.moveTo(-8, 4); g.bezierCurveTo(-6, -14, -5, -30, -4, -44); g.lineTo(10, -44); g.bezierCurveTo(10, -30, 9, -14, 10, 4); g.closePath(); }, COL.rSkin, { so: 4, ho: 1.4, sh: mix(COL.rSkin, '#9a4f56', 0.3), lw: 2.1 });
  part(() => { g.moveTo(-9, 0); g.lineTo(2, 12); g.lineTo(4, -2); g.closePath(); g.moveTo(4, -2); g.lineTo(7, 11); g.lineTo(12, 0); g.closePath(); }, COL.rShirt, { so: 0, ho: 0, lw: 1.6 });  // collar points
  g.translate(2, -40 + 1.2 * P.nod); g.rotate((P.tilt + 2.2 * P.nod) * Math.PI / 180);
  g.translate(4, -36);
  remiFace(P);
  g.restore();
  remiArm(shN, tgt('n'), false, 0, P);
  g.restore();
}

// ------------------------------------------------------------------ BO — short, round, unflappable (drawn mirrored: local +x faces Rémi)
const boBody = () => {
  g.moveTo(-40, 11); g.bezierCurveTo(-63, 0, -67, -54, -46, -81); g.bezierCurveTo(-32, -100, -2, -106, 18, -96);
  g.bezierCurveTo(38, -84, 55, -52, 53, -22); g.bezierCurveTo(51, -2, 38, 11, 18, 13); g.closePath();
};
function boLeg(far) {
  const k = far ? [22, -10] : [0, 0], q = (p) => [p[0] + k[0] * 0.55, p[1] + k[1] * 0.5];
  part(() => limb([q([12, 4]), q([52, 6]), q([56, 60])], [13, 11, 9]), far ? mix(COL.bTrou, '#000', 0.25) : COL.bTrou, { so: 5, ho: 1.6, lw: 2.2 });
  const a = q([44, 74]);
  part(() => { g.moveTo(a[0], a[1]); g.lineTo(a[0] + 28, a[1]); g.quadraticCurveTo(a[0] + 38, a[1], a[0] + 36, a[1] - 8); g.quadraticCurveTo(a[0] + 31, a[1] - 18, a[0] + 14, a[1] - 18); g.quadraticCurveTo(a[0] - 3, a[1] - 19, a[0] - 2, a[1] - 8); g.closePath(); },
    far ? mix(COL.bShoe, '#000', 0.28) : COL.bShoe, { so: 4, ho: 1.4, lw: 2.1, inner: () => fillPath(() => g.rect(a[0] - 6, a[1] - 4.5, 48, 6), far ? mix(COL.bSole, '#000', 0.28) : COL.bSole) });
}
function boFace(P) {
  const skinSh = mix(COL.bSkin, '#4a2a44', 0.3);
  part(() => g.ellipse(-24, 6, 7, 10, -0.1, 0, Math.PI * 2), COL.bSkin, { so: 3, ho: 1, sh: skinSh, lw: 2.0 });
  part(() => g.ellipse(0, 0, 40, 37, 0, 0, Math.PI * 2), COL.bSkin, { so: 8, ho: 2.2, sh: skinSh });
  // beanie: dome + rolled cuff with ribbing
  part(() => { g.moveTo(-43, -12); g.bezierCurveTo(-47, -48, -20, -61, 2, -61); g.bezierCurveTo(25, -61, 45, -47, 42, -14); g.closePath(); }, COL.bHat, { so: 7, ho: 2.4 });
  const cuff = () => { g.moveTo(-45, -26); g.quadraticCurveTo(0, -32, 44, -28); g.quadraticCurveTo(47.5, -20, 43.5, -11); g.quadraticCurveTo(0, -16, -44, -10); g.quadraticCurveTo(-48.5, -18, -45, -26); g.closePath(); };
  part(cuff, COL.bHat, { so: 3, ho: 1.6, inner: () => { for (let x = -42; x <= 42; x += 5.5) strokePath(() => { g.moveTo(x, -30); g.lineTo(x + 0.6, -10); }, COL.bRib, 1.2); } });
  // half-lidded eyes (the lids never lift; the one slow blink lives in S6)
  const cover = 0.5 + 0.5 * P.blink, lid = mix(COL.bSkin, '#000000', 0.12);   // the slow blink spans his half-lidded range
  fillPath(() => g.ellipse(4, 17, 8, 5, 0, 0, Math.PI * 2), 'rgba(196,92,78,0.14)');
  eye({ x: 2, y: 4, rx: 7.6, ry: 7, gx: 2.2, gy: -0.6, pr: 3.3, cover, lid, skin: COL.bSkin, lash: 3.0 });
  eye({ x: 22.5, y: 3, rx: 5.2, ry: 6.6, gx: 1.6, gy: -0.6, pr: 2.9, cover, lid, skin: COL.bSkin, lash: 2.7 });
  brow([9.5, -5.2], [-6, -5.2], 0, 2.7, mix(COL.bSkin, '#1a0f0c', 0.72));
  brow([17.5, -5.6], [28, -5.6], 0, 2.3, mix(COL.bSkin, '#1a0f0c', 0.72));
  part(() => g.ellipse(27.5, 13, 7.0, 6.2, 0, 0, Math.PI * 2), COL.bSkin, { so: 3.5, ho: 1.6, sh: skinSh, lw: 0 });
  strokePath(() => g.ellipse(27.5, 13, 7.0, 6.2, 0, -0.35, Math.PI * 0.95), ink(COL.bSkin), 2.0);
  fillPath(() => g.ellipse(25.5, 16.2, 1.7, 1.1, 0.2, 0, Math.PI * 2), mix(COL.bSkin, '#2a120e', 0.55));
  mouthShape(P.mouth, { x: 17, y: 24.5, w: 13, h: 9.5, smile: 0, skin: COL.bSkin });
}
function drawBo(P) {
  g.save(); g.translate(868, 462); g.scale(-1, 1); LIGHT = [0.34, -0.94];
  chair(-24);
  const bs = 1 + 0.012 * P.breath;
  boLeg(true); boLeg(false);
  g.save(); g.scale(1, bs);
  part(boBody, COL.bHood, { so: 10, ho: 2.6 });
  part(() => g.ellipse(-8, -97, 33, 12, -0.08, 0, Math.PI * 2), mix(COL.bHood, '#000', 0.16), { so: 0, ho: 1.5, lw: 2.0 });    // bunched hood behind the head
  part(() => limb([[-20, -84], [-36, -48], [6, -27]], [12.5, 11, 10]), COL.bHood, { so: 5, ho: 1.8, lw: 2.2 });                     // sleeve, elbow back
  part(() => limb([[-3, -31], [8, -26]], [9.6, 9.6]), mix(COL.bHood, '#000', 0.12), { so: 0, ho: 0, lw: 2.0 });                       // ribbed cuff at the pocket mouth
  fillPath(() => { g.moveTo(5, -47); g.quadraticCurveTo(-1, -28, 5, -9); g.lineTo(11, -10); g.quadraticCurveTo(6, -28, 11, -47); g.closePath(); }, mix(COL.bHood, '#05060c', 0.62)); // pocket mouth (shadow)
  part(() => { g.moveTo(12, -53); g.quadraticCurveTo(28, -57, 41, -54); g.quadraticCurveTo(53, -33, 46, -10); g.quadraticCurveTo(28, -3, 10, -7); g.quadraticCurveTo(3, -29, 12, -53); g.closePath(); }, COL.bPocket,
    { so: 4, ho: 1.2, lw: 2.0, inner: () => strokePath(() => { g.moveTo(13, -48); g.quadraticCurveTo(28, -52, 41, -49); }, mix(COL.bPocket, '#0c1020', 0.35), 1.1) });
  g.restore();
  g.save(); g.translate(6, -128 * bs); g.rotate(-P.tilt * Math.PI / 180);
  boFace(P);
  g.restore();
  g.restore();
}

// eye-line of each character in stage coordinates (same transform chain as the drawing), for framing the singles
function remiEyeWorld(P) {
  const ts = 1 + 0.010 * P.breath - 0.024 * P.defl, nb = rot([16, -160 * ts], P.lean);
  let p = rot([17.5, -42], P.tilt + 2.2 * P.nod); p = rot([p[0] + 2, p[1] - 40 + 1.2 * P.nod], P.lean * 0.6);
  return [420 + P.hipX + nb[0] + p[0], 462 + nb[1] + p[1]];
}
function boEyeWorld(P) { const bs = 1 + 0.012 * P.breath; const p = rot([12, 4], -P.tilt); return [868 - (6 + p[0]), 462 - 128 * bs + p[1]]; }
const CAM_P = CAM.map((c, k) => c.P || (c.who === 'remi' ? remiEyeWorld(remiPose(CUT[k])) : boEyeWorld(boPose(CUT[k]))));

// ------------------------------------------------------------------ boot
let post, f_now = 0;
await boot({
  fps: FPS, shots: SHOTS,
  init: async (ctx) => {
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x000000);
    const camera = new THREE.PerspectiveCamera(30, ctx.W / ctx.H, 0.1, 10);
    // one grade for every shot: a soft "cel" finish — gentle contrast, warm highlights / cool shadows, fine grain, mild vignette
    post = makeComposer(ctx.renderer, scene, camera, { grade: 'cel', finish: { saturation: 1.06, contrast: 1.05, grain: 0.035, grainSize: 1.4, vignette: 0.3, halation: 0.06, halationThreshold: 0.82,
      shadowTint: [0.0, 0.004, 0.018], highlightTint: [0.025, 0.012, -0.012] } });
    // KIT WORKAROUND: the overlay CanvasTexture is tagged sRGB, so it is linearised on sampling and never re-encoded
    // (rgb 128 → 55 on screen). Treat it as raw display-referred data so the canvas colours land exactly.
    post.overlay.tex.colorSpace = THREE.NoColorSpace; post.overlay.tex.needsUpdate = true;
  },
  render: async (ctx, i, t) => {
    const f = t * FPS; f_now = f;
    if (ctx.q.get('chart')) { // QC only (never in the film): the 9 Rhubarb mouths on both rigs, X A B C D E F G H left→right
      g = post.overlay.ctx; g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#1b1925'; g.fillRect(0, 0, ctx.W, ctx.H);
      const u = ctx.W / 1280, sc = 1.55 * u; LW = 1.6 / 1.55;
      'XABCDEFGH'.split('').forEach((v, n) => {
        const x = (78 + n * 138) * u;
        g.setTransform(sc, 0, 0, sc, x, 200 * u); LIGHT = [0.36, -0.93]; remiFace({ ...remiPose(150), mouth: v, blink: 0, smile: 0, gaze: [2.3, 1.5] });
        g.setTransform(sc, 0, 0, sc, x + 6 * u, 530 * u); LIGHT = [0.34, -0.94]; boFace({ blink: 0, mouth: v, tilt: 0, breath: 0 });
      });
      post.render(t); return;
    }
    let k = 0; for (let s = 0; s < CUT.length; s++) if (f >= CUT[s] - 1e-6) k = s;
    let cam = CAM[k];
    g = post.overlay.ctx; g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#000'; g.fillRect(0, 0, ctx.W, ctx.H);
    let P0 = CAM_P[k];
    const qc = ctx.q.get('cu');   // QC only (never in the film): a tracking close-up on one face to inspect visemes/blinks at any frame
    if (qc) { cam = { S: [640, 330], z: 5.0, lw: 3.0 }; P0 = qc === 'bo' ? boEyeWorld(boPose(f)) : remiEyeWorld(remiPose(f)); }
    const sc = cam.z * ctx.W / 1280, cx = P0[0] - (cam.S[0] - 640) / cam.z, cy = P0[1] - (cam.S[1] - 360) / cam.z;
    g.setTransform(sc, 0, 0, sc, ctx.W / 2 - cx * sc, ctx.H / 2 - cy * sc); LW = cam.lw / cam.z;
    drawStage(cam);
    spotHaze(f, cam.z);
    drawRemi(remiPose(f));
    drawBo(boPose(f));
    spotFalloff();
    if (cam.z < 1.2) drawStageLip();
    post.render(t);
  },
});
