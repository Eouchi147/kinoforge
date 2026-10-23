// Cutaway look board: flat-vector. The meadow example (films/cutaway/meadow) drawn as a pure 2D flat vector cross-section
// on a canvas, as a pure function of time t (harness/render.cjs contract: window.KF, KF.render(i, t), KF.canvas).
// Words come from spec.json (labels, counter, title, end card); times from cues.json, resolved like the Cutaway engine.
// Design space is 1920x1080; the canvas is ?w=&h= and everything is scaled. Deterministic: seeded RNG, no clock reads.

const Q = new URLSearchParams(location.search);
const W = +(Q.get('w') || 1920), H = +(Q.get('h') || 1080), FPS = +(Q.get('fps') || 24), DUR = 40;
const S = W / 1920;
const canvas = document.createElement('canvas');
canvas.width = W; canvas.height = H;
canvas.style.width = '100vw'; canvas.style.height = 'auto'; canvas.style.display = 'block';
document.body.appendChild(canvas);
const g = canvas.getContext('2d', { willReadFrequently: true });   // CPU raster (Skia): far faster than SwiftShader GL for many small paths

// ------------------------------------------------------------------ helpers
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const sstep = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const ease = (k) => { k = clamp(k); return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; };
const easeOut = (k) => 1 - Math.pow(1 - clamp(k), 3);
const TAU = Math.PI * 2;
function rng(seed) { let s = seed | 0; return () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function hex(c) { const n = parseInt(c.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function mix(a, b, k) { const A = hex(a), B = hex(b); return 'rgb(' + A.map((v, i) => Math.round(lerp(v, B[i], k))).join(',') + ')'; }
function rgba(c, a) { const A = hex(c); return `rgba(${A[0]},${A[1]},${A[2]},${a})`; }
function poly(pts, close = true) { g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); if (close) g.closePath(); }
function ell(x, y, rx, ry, rot = 0) { g.beginPath(); g.ellipse(x, y, Math.max(0.1, rx), Math.max(0.1, ry), rot, 0, TAU); }
function circ(x, y, r) { g.beginPath(); g.arc(x, y, Math.max(0.1, r), 0, TAU); }
function vgrad(y0, y1, c0, c1) { const gr = g.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, c0); gr.addColorStop(1, c1); return gr; }
function rrect(x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }

// ------------------------------------------------------------------ palette (limited: dusk sky, meadow greens, earth, one gold, one violet)
const P = {
  ink: '#1c1a2e', ink2: '#2b2843', cream: '#fff4e2', paper: '#f6ead3',
  skyTop: '#47508a', skyMid: '#c88a98', skyLow: '#f6c08c', sun: '#fff1cc',
  hill1: '#e3a58e', hill2: '#c48a8c', hill3: '#94708c', under0: '#6e5a7e', under1: '#2a2541',
  grassLight: '#b3cf6e', grass: '#79ad55', grassDark: '#3f7a46', turf: '#355f3a',
  leaf0: '#2d5f49', leaf1: '#3f8556', leaf2: '#7dbb64', trunk: '#5b3b2c',
  water0: '#9fd1df', water1: '#4f93ba', water2: '#2b5f8a',
  gold: '#f4c247', goldDark: '#c48b2a', terracotta: '#cd6a40', violet: '#9b6bd6',
  bone: '#fbf3df', boneShadow: '#a8977a',
};
const STR = [ // name, bottom of the layer (m below the turf, as presets.STRATA_TIME), colour top, colour bottom, mark colour
  ['topsoil', 0.07, '#6b442a', '#4f311f', '#3a2416'],
  ['sand', 0.17, '#f0d092', '#e3b977', '#c99a5c'],
  ['clay', 0.31, '#d27a4f', '#bb633f', '#9f4f31'],
  ['loam', 0.47, '#98653f', '#7f5234', '#664127'],
  ['gravel', 0.57, '#aca396', '#918a80', '#6f685f'],
  ['ochre', 0.62, '#e2a24b', '#d08b3b', '#b2722b'],
  ['limestone', 1.30, '#e9dec3', '#d2c4a2', '#b8a882'],
  ['bedrock', 1.60, '#4b4c64', '#33344b', '#25263a'],
];

// ------------------------------------------------------------------ the world (design px; 300 px = 1 m; the block is 4 m wide, 1.6 m deep)
const PX = 300, BX0 = 330, BX1 = 1530, CX = 930, TOP0 = 455, BOT = TOP0 + 1.6 * PX;
const OX = 86, OY = -50;                     // the top of the block seen a little from above (and its right face)
const RL = 948, RR = 1152, WY = TOP0 + 16;   // the river where it leaves through the front cut, its level
const ux = (u) => CX + u * PX;
function rawTop(x) { return TOP0 - 9 * Math.sin((x - BX0) * 0.0049 + 0.5) - 6 * Math.sin((x - BX0) * 0.0127 + 1.3) - 16 * Math.exp(-(((x - 470) / 150) ** 2)); }
function bank(x) { const d = x < RL ? RL - x : x > RR ? x - RR : 0; return 1 - sstep(0, 70, d); }
function top(x) { return lerp(rawTop(x), WY - 4, bank(x)); }
function bed(x) { const u = clamp((x - RL) / (RR - RL)); return WY + 98 * Math.pow(Math.sin(Math.PI * u), 0.7); }
function faceTop(x) { return (x > RL && x < RR) ? bed(x) : top(x); }
function wav(i, x) { const a = i >= 6 ? 7 : 3.2; return a * Math.sin(x * 0.0105 * (1 + i * 0.13) + i * 1.7) + 1.8 * Math.sin(x * 0.031 + i * 2.3); }
function bnd(i, x) { const c = STR[i][1]; const f = Math.max(0, 1 - c / 0.55); return TOP0 + c * PX + f * (rawTop(x) - TOP0) + (i === STR.length - 1 ? 0 : wav(i, x)); }
function depthY(d, x) { return TOP0 + d * PX + Math.max(0, 1 - d / 0.55) * (rawTop(x) - TOP0); }
const onTop = (x, d) => [x + d * OX, top(x) + d * OY];
const rivC = (d) => (RL + RR) / 2 + d * OX - 55 * Math.sin(d * Math.PI);
const rivW = (d) => (RR - RL) / 2 * (1 - 0.12 * d);
const onRiver = (d, k = 0) => [rivC(d) + k * rivW(d), WY + d * OY];

// finds (easter eggs) in the front cut: kind, x, y. Hedgehog, geode and well sit on the +X face in the Blender line; here the
// front face is the only full face, so they move to it, at their own depths, where nothing else is.
const EGG = {
  mole: { x: ux(-1.30), y: depthY(0.115, ux(-1.30)) },
  chest: { x: ux(-1.18), y: depthY(0.31, ux(-1.18)) },
  amphora: { x: ux(-0.42), y: depthY(0.46, ux(-0.42)) },
  ammonite: { x: ux(0.20), y: depthY(0.84, ux(0.20)) },
  dino: { x: ux(-0.78) - 0.12 * PX, y: depthY(0.98, ux(-0.78)) - 0.06 * PX },
  trilobite: { x: ux(-1.48), y: depthY(1.235, ux(-1.48)) },
  gold: { x: ux(-0.33), y: depthY(1.42, ux(-0.33)) },
  hedgehog: { x: 1262, y: depthY(0.17, 1262) },
  geode: { x: 1196, y: depthY(1.10, 1196) },
  well: { x: 1432, y: depthY(0.78, 1432) },
};
EGG.dino.skull = { x: EGG.dino.x - 170, y: EGG.dino.y - 18 };   // the skull leads; the skeleton runs right from it (scale DS)
const DS = 0.62;

// ------------------------------------------------------------------ static scatter (seeded, built once)
const R = rng(4);
const MARKS = [];   // texture marks in the cut face: [layer, type, x, y, a, b, rot]
for (let i = 0; i < STR.length; i++) {
  const n = [90, 160, 70, 90, 150, 30, 160, 70][i];
  for (let k = 0; k < n; k++) {
    const x = BX0 + 6 + R() * (BX1 - BX0 - 12);
    const y0 = i === 0 ? faceTop(x) + 8 : bnd(i - 1, x), y1 = bnd(i, x);
    if (y1 - y0 < 6) continue;
    const y = lerp(y0 + 3, y1 - 3, R());
    if (y < faceTop(x) + 6) continue;
    MARKS.push([i, x, y, R(), R(), R()]);
  }
}
const GRASS = [];   // tufts along the front edge of the turf
for (let x = BX0 + 3; x < BX1 - 2; x += 5.5 + R() * 3) { if (x > RL - 6 && x < RR + 6) continue; GRASS.push([x, 7 + R() * 9, R(), R()]); }
const FLOWERS = [];
for (let k = 0; k < 150; k++) {
  const x = BX0 + 10 + R() * (BX1 - BX0 - 20), d = 0.08 + R() * 0.85;
  const [X, Y] = onTop(x, d);
  if (Math.abs(X - rivC(d)) < rivW(d) + 16) continue;
  if (x > 1240 && d < 0.95 && R() < 0.6) continue;
  FLOWERS.push([X, Y, d, Math.floor(R() * 4), R()]);
}
const PETALS = Array.from({ length: 36 }, () => [R(), R(), R(), R()]);
const STONES = Array.from({ length: 40 }, () => [R(), R(), R()]);

// ------------------------------------------------------------------ background (parallax layers)
function background(t) {
  g.fillStyle = vgrad(-200, 470, P.skyTop, P.skyLow);
  g.fillRect(-2000, -1500, 6000, 1980);
  const gr = g.createLinearGradient(0, -200, 0, 470); gr.addColorStop(0, rgba(P.skyTop, 0)); gr.addColorStop(0.62, rgba(P.skyMid, 0.55)); gr.addColorStop(1, rgba(P.skyLow, 0));
  g.fillStyle = gr; g.fillRect(-2000, -200, 6000, 670);
  // the sun, low behind the block, and its rings
  const sx = 520, sy = 300;
  for (let k = 5; k >= 1; k--) { circ(sx, sy, 60 + k * 46); g.fillStyle = rgba(P.sun, 0.05 + (5 - k) * 0.012); g.fill(); }
  g.save(); g.translate(sx, sy); g.rotate(t * 0.012);
  for (let k = 0; k < 12; k++) { g.rotate(TAU / 12); poly([[0, -4], [1400, -60 - 30 * (k % 3)], [1400, 60 + 30 * (k % 2)], [0, 4]]); g.fillStyle = rgba(P.sun, 0.035); g.fill(); }
  g.restore();
  circ(sx, sy, 62); g.fillStyle = P.sun; g.fill();
  // clouds: flat lozenges with a lit top edge
  const clouds = [[150, 120, 1.0], [760, 70, 0.8], [1260, 150, 1.15], [1760, 95, 0.9], [-300, 200, 0.7], [2200, 210, 0.8]];
  for (const [x0, y, s] of clouds) {
    const x = x0 + ((t * 6 * s) % 2600);
    for (const dx of [0, -2600]) {
      const X = x + dx; if (X < -900 || X > 2900) continue;
      g.save(); g.translate(X, y); g.scale(s, s);
      rrect(-150, -16, 300, 32, 16); g.fillStyle = rgba('#ffe7cf', 0.55); g.fill();
      rrect(-90, -36, 150, 40, 20); g.fill();
      rrect(-60, -10, 260, 24, 12); g.fillStyle = rgba('#f4c3a6', 0.45); g.fill();
      g.restore();
    }
  }
}
function hills() {
  const layers = [[P.hill1, 395, 26, 0.004, 0.2], [P.hill2, 425, 22, 0.006, 1.7], [P.hill3, 452, 18, 0.009, 3.1]];
  for (const [c, y, a, f, ph] of layers) {
    const pts = [[-1500, 1300]];
    for (let x = -1500; x <= 3500; x += 40) pts.push([x, y - a * Math.sin(x * f + ph) - a * 0.5 * Math.sin(x * f * 2.7 + ph * 2)]);
    pts.push([3500, 1300]); poly(pts); g.fillStyle = c; g.fill();
  }
  g.fillStyle = vgrad(470, 1150, P.under0, P.under1); g.fillRect(-1500, 470, 5000, 1500);
  const glow = g.createRadialGradient(960, 470, 40, 960, 470, 1000); glow.addColorStop(0, rgba('#f6c08c', 0.28)); glow.addColorStop(1, rgba('#f6c08c', 0));
  g.fillStyle = glow; g.fillRect(-1500, 470, 5000, 1500);
  // a faint far meadow line at the horizon
  g.fillStyle = rgba('#f2b48f', 0.25); g.fillRect(-1500, 466, 5000, 4);
}

// ------------------------------------------------------------------ the block
function facePath() {
  const pts = [];
  for (let x = BX0; x <= BX1; x += 4) pts.push([x, faceTop(x)]);
  pts.push([BX1, faceTop(BX1)], [BX1, BOT], [BX0, BOT]);
  poly(pts);
}
function strata(t, reveal) {
  g.save(); facePath(); g.clip();
  for (let i = 0; i < STR.length; i++) {
    const [, c, c0, c1] = STR[i];
    const pts = [];
    if (i === 0) { for (let x = BX0; x <= BX1; x += 6) pts.push([x, faceTop(x) - 2]); pts.push([BX1, faceTop(BX1) - 2]); }
    else { for (let x = BX0; x <= BX1; x += 6) pts.push([x, bnd(i - 1, x)]); pts.push([BX1, bnd(i - 1, BX1)]); }
    pts.push([BX1 + 2, BOT + 2], [BX0 - 2, BOT + 2]); poly(pts);
    const ya = TOP0 + (i ? STR[i - 1][1] : 0) * PX, yb = TOP0 + c * PX;
    g.fillStyle = vgrad(ya - 10, yb + 10, c0, c1); g.fill();
    // a thin light line on top of each layer: the cut catches the light
    if (i > 0) { g.beginPath(); for (let x = BX0; x <= BX1; x += 6) { const y = bnd(i - 1, x); x === BX0 ? g.moveTo(x, y) : g.lineTo(x, y); } g.strokeStyle = rgba('#ffffff', i >= 6 ? 0.10 : 0.16); g.lineWidth = 1.2; g.stroke(); }
  }
  // texture marks, one vocabulary per layer
  for (const [i, x, y, a, b, r] of MARKS) {
    const mc = STR[i][4];
    g.fillStyle = mc; g.strokeStyle = mc;
    switch (STR[i][0]) {
      case 'topsoil': g.globalAlpha = 0.55; g.lineWidth = 1; g.beginPath(); g.moveTo(x, y - 6); g.quadraticCurveTo(x + (a - 0.5) * 10, y, x + (b - 0.5) * 8, y + 5); g.stroke(); break;
      case 'sand': g.globalAlpha = 0.45; circ(x, y, 1 + a * 1.2); g.fill(); break;
      case 'clay': g.globalAlpha = 0.35; g.lineWidth = 1.4; g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 10 + a * 22, y + (b - 0.5) * 2); g.stroke(); break;
      case 'loam': g.globalAlpha = 0.5; ell(x, y, 2 + a * 2.5, 1.5 + b * 1.5, r * 3); g.fill(); break;
      case 'gravel': g.globalAlpha = 1; ell(x, y, 2.5 + a * 4, 2 + b * 2.6, r * 3); g.fillStyle = mix('#c9c0b2', '#6f685f', r); g.fill(); break;
      case 'ochre': g.globalAlpha = 0.4; g.fillRect(x, y, 6 + a * 8, 1.2); break;
      case 'limestone':
        g.globalAlpha = 0.5;
        if (a < 0.3) { g.lineWidth = 1; g.beginPath(); g.arc(x, y, 3 + b * 3, Math.PI, TAU); g.stroke(); g.beginPath(); g.moveTo(x - 3 - b * 3, y); g.lineTo(x + 3 + b * 3, y); g.stroke(); }
        else if (a < 0.75) { g.fillRect(x, y, 12 + b * 26, 1); }
        else { circ(x, y, 1.2 + b); g.fill(); }
        break;
      case 'bedrock': g.globalAlpha = 0.55; g.lineWidth = 1.2; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 8 + a * 10, y + (b - 0.5) * 12); g.lineTo(x + 14 + a * 18, y + (r - 0.5) * 16); g.stroke(); break;
    }
  }
  g.globalAlpha = 1;
  // bedding bands inside the thick limestone
  for (const [d0, d1, a] of [[0.74, 0.79, 0.22], [0.96, 1.04, 0.16], [1.16, 1.2, 0.24]]) {
    const pts = []; for (let x = BX0; x <= BX1; x += 8) pts.push([x, TOP0 + d0 * PX + wav(6, x) * 0.6 + 2 * Math.sin(x * 0.02 + d0 * 9)]);
    for (let x = BX1; x >= BX0; x -= 8) pts.push([x, TOP0 + d1 * PX + wav(6, x) * 0.6 + 2 * Math.sin(x * 0.017 + d1 * 7)]);
    poly(pts); g.fillStyle = rgba(STR[6][4], a); g.fill();
  }
  // turf band with roots, right under the grass
  const tp = []; for (let x = BX0; x <= BX1; x += 4) { if (x > RL - 2 && x < RR + 2) continue; tp.push([x, faceTop(x)]); }
  g.lineWidth = 9; g.strokeStyle = P.turf; g.lineJoin = 'round';
  g.beginPath(); let pen = false;
  for (let x = BX0; x <= BX1; x += 4) { const inR = x > RL - 2 && x < RR + 2; if (inR) { pen = false; continue; } const y = faceTop(x) + 3.5; pen ? g.lineTo(x, y) : g.moveTo(x, y); pen = true; }
  g.stroke();
  g.restore();
}
function rightFace() {
  const x = BX1;
  const ys = [top(x)]; for (let i = 0; i < STR.length; i++) ys.push(i === STR.length - 1 ? BOT : bnd(i, x));
  for (let i = 0; i < STR.length; i++) {
    poly([[x, ys[i]], [x + OX, ys[i] + OY], [x + OX, ys[i + 1] + OY], [x, ys[i + 1]]]);
    g.fillStyle = mix(STR[i][3], P.ink, 0.38); g.fill();
  }
  poly([[x, top(x) - 1], [x + OX, top(x) + OY - 1], [x + OX, top(x) + OY + 8], [x, top(x) + 8]]); g.fillStyle = mix(P.turf, P.ink, 0.3); g.fill();
  // the edge where the two cut faces meet
  g.strokeStyle = rgba('#ffffff', 0.18); g.lineWidth = 1.5; g.beginPath(); g.moveTo(x, top(x)); g.lineTo(x, BOT); g.stroke();
}
function topStrip() {
  const front = [], back = [];
  for (let x = BX0; x <= BX1; x += 4) { front.push([x, top(x)]); back.push([x + OX, top(x) + OY]); }
  front.push([BX1, top(BX1)]); back.push([BX1 + OX, top(BX1) + OY]);
  poly(front.concat(back.reverse()));
  const gr = g.createLinearGradient(0, TOP0 + OY - 30, 0, TOP0 + 18); gr.addColorStop(0, P.grassLight); gr.addColorStop(0.55, P.grass); gr.addColorStop(1, mix(P.grass, P.grassDark, 0.5));
  g.fillStyle = gr; g.fill();
  // the back edge of the block catches the low sun
  g.beginPath(); for (let x = BX0; x <= BX1 + 1; x += 4) { const X = x + OX, Y = top(Math.min(x, BX1)) + OY; x === BX0 ? g.moveTo(X, Y) : g.lineTo(X, Y); }
  g.strokeStyle = rgba('#ffe9b0', 0.85); g.lineWidth = 2.2; g.stroke();
  // left end of the strip (the block's left edge seen from above)
  g.beginPath(); g.moveTo(BX0, top(BX0)); g.lineTo(BX0 + OX, top(BX0) + OY); g.strokeStyle = rgba('#ffe9b0', 0.5); g.lineWidth = 1.5; g.stroke();
}
function riverTop(t) {
  const L = [], Rr = [];
  for (let d = 0; d <= 1.0001; d += 0.05) { L.push(onRiver(d, -1)); Rr.push(onRiver(d, 1)); }
  poly(L.concat(Rr.reverse()));
  g.fillStyle = vgrad(WY + OY, WY, P.water0, P.water1); g.fill();
  g.save(); g.clip();
  // flow: short light dashes travelling toward the cut
  g.strokeStyle = rgba('#ffffff', 0.55); g.lineWidth = 1.3; g.lineCap = 'round';
  for (let k = 0; k < 26; k++) {
    const d = 1 - (((k * 0.618 + t * 0.06) % 1));
    const side = ((k * 0.381) % 1) * 1.6 - 0.8;
    const [x, y] = onRiver(d, side);
    g.globalAlpha = 0.25 + 0.5 * Math.sin(Math.PI * d);
    g.beginPath(); g.moveTo(x - 7, y); g.lineTo(x + 7, y); g.stroke();
  }
  g.globalAlpha = 1; g.restore();
  // banks: a darker lip
  g.lineWidth = 2; g.strokeStyle = rgba(P.grassDark, 0.8);
  for (const k of [-1, 1]) { g.beginPath(); for (let d = 0; d <= 1.0001; d += 0.05) { const [x, y] = onRiver(d, k); d === 0 ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke(); }
}
function riverSection(t) {
  // water as glass in the cut, from its level down to the bed
  const pts = [];
  for (let x = RL; x <= RR; x += 3) pts.push([x, WY + 1.4 * Math.sin(x * 0.06 - t * 2.2)]);
  for (let x = RR; x >= RL; x -= 3) pts.push([x, bed(x)]);
  poly(pts);
  g.fillStyle = vgrad(WY, WY + 100, rgba(P.water0, 0.92), rgba(P.water2, 0.95)); g.fill();
  g.save(); g.clip();
  // light bands moving in the water
  for (let k = 0; k < 5; k++) {
    const x = RL + ((k * 47 + t * 9) % (RR - RL + 60)) - 30;
    poly([[x, WY], [x + 16, WY], [x - 18, WY + 110], [x - 30, WY + 110]]); g.fillStyle = rgba('#ffffff', 0.07); g.fill();
  }
  // weed on the bed, swaying
  g.strokeStyle = rgba('#3f7a46', 0.85); g.lineWidth = 2.2; g.lineCap = 'round';
  for (let k = 0; k < 9; k++) {
    const x = RL + 22 + k * 20 + (k % 2) * 6, y = bed(x);
    const h = 18 + (k * 7) % 22, sw = Math.sin(t * 1.3 + k) * 6;
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + sw * 0.4, y - h * 0.5, x + sw, y - h); g.stroke();
  }
  // fish
  const fishC = ['#d9e6ee', '#e88f4f', '#d9e6ee', '#b9c9d6', '#e88f4f'];
  for (let k = 0; k < 5; k++) {
    const span = (RR - RL) - 50, ph = k * 1.9, sp = 0.17 + k * 0.03;
    const s = Math.sin(t * sp * TAU / 2 + ph);
    const x = RL + 25 + (s * 0.5 + 0.5) * span, dir = Math.cos(t * sp * TAU / 2 + ph) >= 0 ? 1 : -1;
    const y = WY + 22 + k * 12 + Math.sin(t * 1.1 + k) * 4;
    if (y > bed(x) - 8) continue;
    g.save(); g.translate(x, y); g.scale(dir, 1);
    const sz = 0.8 + (k % 3) * 0.2; g.scale(sz, sz);
    ell(0, 0, 11, 4.6); g.fillStyle = fishC[k]; g.fill();
    const wag = Math.sin(t * 9 + k) * 2;
    poly([[-9, 0], [-17, -5 + wag], [-17, 5 + wag]]); g.fill();
    circ(6, -1, 1.1); g.fillStyle = P.ink; g.fill();
    g.restore();
  }
  // bubbles
  g.strokeStyle = rgba('#ffffff', 0.6); g.lineWidth = 1;
  for (let k = 0; k < 7; k++) {
    const x0 = RL + 30 + k * 24, ph = ((t * 0.35 + k * 0.37) % 1);
    const y = lerp(bed(x0) - 6, WY + 4, ph); circ(x0 + Math.sin(t * 2 + k) * 3, y, 1.5 + k % 2); g.stroke();
  }
  g.restore();
  // the bed: sand and pebbles
  g.beginPath(); for (let x = RL; x <= RR; x += 3) { const y = bed(x); x === RL ? g.moveTo(x, y) : g.lineTo(x, y); }
  g.strokeStyle = '#c9b38a'; g.lineWidth = 5; g.stroke();
  // the surface line: the glass catches the light
  g.beginPath(); for (let x = RL; x <= RR; x += 3) { const y = WY + 1.4 * Math.sin(x * 0.06 - t * 2.2); x === RL ? g.moveTo(x, y) : g.lineTo(x, y); }
  g.strokeStyle = rgba('#ffffff', 0.85); g.lineWidth = 2; g.stroke();
}

// ------------------------------------------------------------------ the finds in the cut
function sparkle(x, y, s, a) { if (a <= 0.01) return; g.save(); g.translate(x, y); g.globalAlpha = a; g.fillStyle = '#fffbe6'; poly([[0, -s], [s * 0.22, -s * 0.22], [s, 0], [s * 0.22, s * 0.22], [0, s], [-s * 0.22, s * 0.22], [-s, 0], [-s * 0.22, -s * 0.22]]); g.fill(); g.restore(); }
function mole(t) {
  const { x, y } = EGG.mole;
  // the tunnel: a hollow in the soil from the digging face to the nest, 0.6 m to the right
  const path = () => { g.beginPath(); g.moveTo(x - 6, y); g.bezierCurveTo(x + 40, y + 10, x + 80, y - 8, x + 120, y + 4); g.quadraticCurveTo(x + 145, y + 10, x + 160, y + 8); };
  g.lineCap = 'round'; g.lineJoin = 'round';
  path(); g.strokeStyle = rgba('#3a2416', 0.35); g.lineWidth = 22; g.stroke();
  path(); g.strokeStyle = '#3d2718'; g.lineWidth = 17; g.stroke();
  g.save(); g.translate(0, 5); path(); g.strokeStyle = '#5a3b25'; g.lineWidth = 6; g.stroke(); g.restore();   // the floor, packed earth
  // a side shaft up to the molehill
  g.beginPath(); g.moveTo(x + 58, y - 2); g.quadraticCurveTo(x + 66, y - 16, x + 62, faceTop(x + 62) + 2); g.strokeStyle = '#3d2718'; g.lineWidth = 11; g.stroke();
  // nest chamber lined with dry grass
  ell(x + 180, y + 7, 30, 19); g.fillStyle = rgba('#3a2416', 0.35); g.fill();
  ell(x + 180, y + 7, 27, 16.5); g.fillStyle = '#3d2718'; g.fill();
  g.beginPath(); g.ellipse(x + 180, y + 9, 25, 13, 0, 0.05, Math.PI - 0.05); g.closePath(); g.fillStyle = '#d4ad62'; g.fill();
  g.strokeStyle = '#efcf86'; g.lineWidth = 1.1;
  for (let k = 0; k < 9; k++) { g.beginPath(); g.moveTo(x + 160 + k * 5, y + 12 + (k % 2) * 3); g.lineTo(x + 167 + k * 4.5, y + 17 - (k % 3) * 1.5); g.stroke(); }
  // the mole, facing left, digging at the end of its tunnel
  const dig = Math.sin(t * 7), bob = Math.sin(t * 3.5) * 0.8;
  g.save(); g.translate(x + 8, y + 1 + bob); g.scale(1.25, 1.25);
  ell(14, 3, 4, 1.6, 0.4); g.fillStyle = '#e79a8f'; g.fill();          // tail
  ell(9, 5, 5, 2.4, 0.2); g.fill();                                     // hind foot
  ell(2, 0, 14, 7.5); g.fillStyle = vgrad(-8, 8, '#6a6170', '#3a333f'); g.fill();
  ell(-9, 0.5, 6.5, 5); g.fill();
  poly([[-13, -1.5], [-21, 1], [-13, 3.5]]); g.fillStyle = '#ef9f92'; g.fill();  // snout
  circ(-21, 1, 1.2); g.fill();
  g.save(); g.translate(-8, 5); g.rotate(-0.4 + dig * 0.55); ell(-5, 0, 6, 3.4); g.fillStyle = '#f2ab9e'; g.fill();
  g.strokeStyle = '#d07e72'; g.lineWidth = 0.8; for (let k = 0; k < 3; k++) { g.beginPath(); g.moveTo(-8, -2 + k * 2); g.lineTo(-11.5, -2.5 + k * 2.4); g.stroke(); } g.restore();
  ell(0, -4, 9, 2.2); g.fillStyle = rgba('#ffffff', 0.16); g.fill();
  g.restore();
  // soil flicked back over its shoulder
  for (let k = 0; k < 3; k++) { const ph = (t * 1.5 + k / 3) % 1; circ(x - 18 + ph * 26, y - 4 + ph * ph * 12 - ph * 9, 1.8); g.fillStyle = rgba('#9a6d45', 1 - ph); g.fill(); }
}
function chest(t) {
  const { x, y } = EGG.chest;
  // coins leaking out of a split board and down into the soil
  for (let k = 0; k < 15; k++) {
    const u = k / 14, cx = x + 24 + u * 40 + Math.sin(k * 2.1) * 5, cy = y + 18 + u * u * 56 + (k % 3) * 2;
    ell(cx, cy, 5.5, 2.6, (k % 4) * 0.4); g.fillStyle = P.goldDark; g.fill();
    ell(cx, cy - 0.8, 5, 2.1, (k % 4) * 0.4); g.fillStyle = P.gold; g.fill();
  }
  g.save(); g.translate(x, y); g.rotate(-0.1);
  // the lid, hinged at the back right, thrown open
  g.save(); g.translate(30, -6); g.rotate(0.62 + Math.sin(t * 0.8) * 0.015);
  g.beginPath(); g.moveTo(-60, 0); g.lineTo(-60, -6); g.bezierCurveTo(-58, -24, -2, -24, 0, -6); g.lineTo(0, 0); g.closePath();
  g.fillStyle = vgrad(-22, 0, '#a86c3c', '#7a4a28'); g.fill();
  g.fillStyle = '#e0ad48'; g.fillRect(-52, -19, 5, 19); g.fillRect(-13, -19, 5, 19);
  g.restore();
  // the open mouth, heaped with gold
  ell(0, -6, 29, 6); g.fillStyle = '#2a170b'; g.fill();
  g.beginPath(); g.moveTo(-26, -6); g.quadraticCurveTo(-10, -20, 4, -13); g.quadraticCurveTo(16, -19, 27, -6); g.closePath(); g.fillStyle = P.gold; g.fill();
  for (let k = 0; k < 7; k++) { ell(-18 + k * 6, -10 - Math.sin(k * 1.3) * 3 - (k > 1 && k < 5 ? 3 : 0), 3.6, 2, 0.3 * (k % 3 - 1)); g.fillStyle = k % 2 ? '#f8d775' : P.goldDark; g.fill(); }
  // body
  rrect(-30, -6, 60, 31, 3); g.fillStyle = vgrad(-6, 25, '#9e663a', '#6a3f22'); g.fill();
  g.fillStyle = '#58331b'; for (const yy of [4, 14]) g.fillRect(-30, yy, 60, 1.6);
  g.fillStyle = '#e0ad48'; g.fillRect(-22, -6, 5, 31); g.fillRect(17, -6, 5, 31);
  rrect(-5, -3, 10, 11, 2); g.fillStyle = '#f1c35a'; g.fill(); circ(0, 3, 1.6); g.fillStyle = '#4a2a14'; g.fill();
  poly([[22, 16], [30, 13], [30, 25], [24, 25]]); g.fillStyle = '#2a170b'; g.fill();          // the split it leaks through
  g.restore();
  // glints
  for (let k = 0; k < 4; k++) { const a = Math.max(0, Math.sin(t * 2.4 + k * 1.7)); sparkle(x - 16 + k * 11, y - 20 - (k % 2) * 5, 5.5, a * 0.9); }
}
function amphora(t) {
  const { x, y } = EGG.amphora;
  // shards and bronze coins around it
  const shards = [[-60, 16, 0.3], [56, 20, -0.6]];
  for (const [dx, dy, r] of shards) { g.save(); g.translate(x + dx, y + dy); g.rotate(r); poly([[-7, -3], [6, -5], [8, 3], [-4, 5]]); g.fillStyle = '#9a4a2a'; g.fill(); g.restore(); }
  for (const [dx, dy] of [[-30, 22], [-18, 25], [24, 24]]) { ell(x + dx, y + dy, 5, 2.4); g.fillStyle = '#8c5a2b'; g.fill(); ell(x + dx, y + dy - 0.6, 4.4, 1.8); g.fillStyle = '#b8803e'; g.fill(); }
  g.save(); g.translate(x, y); g.rotate(-0.18);
  const body = () => { g.beginPath(); g.moveTo(-26, -7); g.bezierCurveTo(-18, -22, 26, -22, 40, -4); g.lineTo(52, 0); g.lineTo(40, 4); g.bezierCurveTo(26, 22, -18, 22, -26, 7); g.closePath(); };
  body(); g.fillStyle = vgrad(-20, 20, '#e08a57', '#a9532f'); g.fill();
  g.fillRect(-46, -5, 22, 10);                                                  // neck
  rrect(-52, -8, 8, 16, 2); g.fillStyle = '#c4683d'; g.fill();                  // rim
  g.strokeStyle = '#b85e36'; g.lineWidth = 3.4; g.lineCap = 'round';
  g.beginPath(); g.moveTo(-40, -5); g.quadraticCurveTo(-32, -22, -20, -14); g.stroke();   // handles
  g.beginPath(); g.moveTo(-40, 5); g.quadraticCurveTo(-32, 22, -20, 14); g.stroke();
  g.beginPath(); g.moveTo(0, -18); g.quadraticCurveTo(4, 0, 0, 18); g.strokeStyle = '#6b3420'; g.lineWidth = 2.5; g.stroke();
  g.beginPath(); g.moveTo(10, -18); g.quadraticCurveTo(14, 0, 10, 18); g.lineWidth = 1.2; g.stroke();
  g.beginPath(); g.moveTo(-14, -13); g.bezierCurveTo(-4, -18, 16, -18, 28, -10); g.strokeStyle = rgba('#ffffff', 0.3); g.lineWidth = 2; g.stroke();
  g.restore();
}
function ammonite(t) {
  const { x, y } = EGG.ammonite;
  const R0 = 24;
  circ(x, y, R0 + 3); g.fillStyle = mix(STR[6][3], P.ink, 0.15); g.fill();
  const gr = g.createRadialGradient(x - 6, y - 8, 2, x, y, R0); gr.addColorStop(0, '#f7e6e2'); gr.addColorStop(0.5, '#e2cba6'); gr.addColorStop(1, '#b99c72');
  circ(x, y, R0); g.fillStyle = gr; g.fill();
  // spiral and ribs
  g.strokeStyle = '#8c6f4b'; g.lineWidth = 1.6; g.beginPath();
  for (let a = 0; a < TAU * 3.2; a += 0.12) { const r = R0 * Math.exp(-0.17 * a) * 0.95; const px = x + Math.cos(a + 0.5) * r, py = y + Math.sin(a + 0.5) * r; a === 0 ? g.moveTo(px, py) : g.lineTo(px, py); }
  g.stroke();
  g.lineWidth = 1; g.strokeStyle = rgba('#8c6f4b', 0.7);
  for (let a = 0; a < TAU * 1.6; a += 0.32) { const r1 = R0 * Math.exp(-0.17 * a) * 0.95, r0 = R0 * Math.exp(-0.17 * (a + TAU)) * 0.95; g.beginPath(); g.moveTo(x + Math.cos(a + 0.5) * r0, y + Math.sin(a + 0.5) * r0); g.lineTo(x + Math.cos(a + 0.5) * r1, y + Math.sin(a + 0.5) * r1); g.stroke(); }
  // nacre sheen sliding over it
  const k = (Math.sin(t * 0.7) * 0.5 + 0.5);
  ell(x - 10 + k * 18, y - 8, 12, 5, -0.6); g.fillStyle = rgba('#bfe6dc', 0.35); g.fill();
}
function trilobite(t) {
  // seen from above, lying in the stone: head shield with eyes, segmented body in three lobes, tail shield
  const { x, y } = EGG.trilobite;
  g.save(); g.translate(x, y); g.rotate(-0.18);
  ell(2, 0, 34, 21); g.fillStyle = mix(STR[6][3], P.ink, 0.16); g.fill();
  g.beginPath(); g.moveTo(-14, -17); g.bezierCurveTo(-34, -18, -36, 18, -14, 17); g.lineTo(18, 13); g.quadraticCurveTo(34, 0, 18, -13); g.closePath();
  g.fillStyle = '#8a7862'; g.fill();
  g.strokeStyle = '#5d4f40'; g.lineWidth = 1.4;
  for (let k = 0; k < 9; k++) { const sx = -10 + k * 3.6, hh = lerp(16.5, 12, k / 8); g.beginPath(); g.moveTo(sx, -hh); g.quadraticCurveTo(sx + 2.2, 0, sx, hh); g.stroke(); }
  g.beginPath(); g.moveTo(-14, -17); g.quadraticCurveTo(-12, 0, -14, 17); g.lineWidth = 2; g.stroke();          // head shield edge
  ell(8, 0, 20, 5.5); g.fillStyle = '#a6937a'; g.fill();                                                      // the raised middle lobe
  g.strokeStyle = '#7a6a58'; g.lineWidth = 1; for (let k = 0; k < 8; k++) { g.beginPath(); g.moveTo(-6 + k * 4, -5); g.lineTo(-6 + k * 4, 5); g.stroke(); }
  ell(-22, 0, 7, 7.5); g.fillStyle = '#a6937a'; g.fill();                                                     // glabella
  g.fillStyle = '#3f352b'; ell(-18, -10, 2.6, 2); g.fill(); ell(-18, 10, 2.6, 2); g.fill();                               // eyes
  g.restore();
}
function dino(t) {
  // a T. rex laid flat in the limestone, facing left: big skull, S-neck, ribcage, tiny arm, heavy hind legs, long tail
  const { x: sx, y: sy } = EGG.dino.skull;
  const hollow = mix(STR[6][3], '#6e5f45', 0.42), far = mix(P.bone, '#b9a986', 0.45);
  g.save(); g.translate(sx, sy); g.scale(DS, DS);
  g.lineCap = 'round'; g.lineJoin = 'round';
  const L = (pts, w) => { g.lineWidth = w; g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.stroke(); };
  const C = (x0, y0, a, b, c, d, e, f, w) => { g.lineWidth = w; g.beginPath(); g.moveTo(x0, y0); g.bezierCurveTo(a, b, c, d, e, f); g.stroke(); };
  const skull = () => { g.beginPath(); g.moveTo(-64, -4); g.bezierCurveTo(-60, -20, -30, -30, 4, -42); g.bezierCurveTo(30, -50, 52, -42, 60, -22); g.lineTo(62, 4); g.lineTo(48, 6); g.lineTo(-60, 8); g.closePath(); };
  const jaw = () => { g.beginPath(); g.moveTo(-58, 13); g.lineTo(50, 10); g.lineTo(60, 26); g.bezierCurveTo(44, 40, -10, 36, -52, 22); g.closePath(); };
  const legs = (col, w, dx, da) => {
    g.strokeStyle = col; g.fillStyle = col;
    const p = [[286 + dx, -16], [244 + dx + da, 40], [292 + dx + da, 98], [282 + dx + da * 0.5, 140]];
    L(p.slice(0, 2), 17 + w); L(p.slice(1, 3), 12 + w); L(p.slice(2, 4), 9 + w);           // femur, shin, foot bones
    const [fx, fy] = p[3];
    L([[fx, fy], [fx - 30, fy + 4]], 6 + w); L([[fx, fy], [fx - 22, fy + 10]], 6 + w); L([[fx, fy], [fx + 10, fy + 4]], 5 + w);
  };
  const body = (col, w) => {
    g.strokeStyle = col; g.fillStyle = col;
    C(46, -6, 74, 4, 98, -12, 128, -16, 19 + w);                         // neck, short and thick
    C(124, -14, 170, -28, 236, -30, 286, -22, 13 + w);                    // back
    C(286, -22, 360, -20, 450, -20, 570, -2, 10 + w);                     // tail, tapering below
    C(420, -18, 470, -14, 520, -8, 570, -2, 6 + w);
    for (let k = 0; k < 10; k++) { const rx = 136 + k * 13, ry = -22 - Math.sin(k / 9 * Math.PI) * 6; C(rx, ry, rx - 12, ry + 24, rx - 6, ry + 52, rx + 4 - k * 0.6, ry + 66 - Math.abs(k - 4.5) * 4.5, 4.6 + w); }
    g.beginPath(); g.ellipse(286, -20, 36 + w / 2, 14 + w / 2, -0.08, 0, TAU); g.fill();         // hip blade
    L([[278, -10], [270, 36], [254, 44]], 8 + w);                                                      // pubis and its boot
    L([[140, 30], [148, 42]], 4.5 + w); L([[148, 42], [143, 49]], 3 + w); L([[148, 42], [153, 48]], 3 + w);   // the tiny arm
    skull(); g.fill(); if (w) { g.lineWidth = w * 1.6; g.stroke(); }
    jaw(); g.fill(); if (w) { g.lineWidth = w * 1.6; g.stroke(); }
  };
  legs(hollow, 8, -24, -6); body(hollow, 8); legs(hollow, 8, 0, 0);
  legs(far, 0, -24, -6); body(P.bone, 0); legs(P.bone, 0, 0, 0);
  // vertebrae: the spine and tail read as a chain of bones
  g.strokeStyle = hollow; g.lineWidth = 1.6;
  for (let k = 0; k < 6; k++) { const u = (k + 0.5) / 6, x = lerp(60, 124, u), y = -6 + Math.sin(u * Math.PI) * 2 - u * 10; g.beginPath(); g.moveTo(x, y - 8); g.lineTo(x - 1, y + 8); g.stroke(); }
  for (let k = 0; k < 30; k++) {
    const u = k / 29, x = lerp(132, 556, u), y = u < 0.36 ? lerp(-18, -27, Math.sin(u / 0.36 * Math.PI / 2)) : lerp(-25, -3, ((u - 0.36) / 0.64) ** 1.6);
    const h = lerp(6, 2.5, u); g.beginPath(); g.moveTo(x, y - h); g.lineTo(x - 1, y + h); g.stroke();
  }
  // skull openings and teeth
  g.fillStyle = hollow;
  ell(-16, -14, 18, 9, -0.25); g.fill();       // the big opening in front of the eye
  ell(22, -20, 8, 9); g.fill();                 // eye socket
  ell(44, -10, 6, 10, 0.2); g.fill();           // the opening behind it
  ell(-50, -6, 3.5, 2.5); g.fill();             // nostril
  g.fillRect(-56, 8, 106, 4);                   // the mouth line
  g.fillStyle = P.bone;
  for (let k = 0; k < 10; k++) { const tx = -54 + k * 9.5; poly([[tx, 8], [tx + 3, 18 - (k % 2) * 3], [tx + 6.5, 8]]); g.fill(); }
  for (let k = 0; k < 9; k++) { const tx = -50 + k * 9.5; poly([[tx, 13], [tx + 3, 6 + (k % 2) * 2], [tx + 6, 13]]); g.fill(); }
  g.strokeStyle = rgba('#ffffff', 0.75); g.lineWidth = 2.5; g.beginPath(); g.moveTo(-40, -18); g.bezierCurveTo(-20, -32, 10, -40, 40, -32); g.stroke();
  g.restore();
}
function goldSeam(t) {
  const { x, y } = EGG.gold, half = 1.5 * PX;
  const yv = (u) => y + 8 * Math.sin(u * 0.012 + 1) + 4 * Math.sin(u * 0.037);
  const thick = (u) => (5 + 4 * Math.sin(u * 0.02 + 2) ** 2) * Math.pow(Math.sin(Math.PI * clamp((u + half) / (2 * half))), 0.45);
  const pts = [], pb = [];
  for (let u = -half; u <= half; u += 6) { const X = x + u; pts.push([X, yv(u) - thick(u)]); pb.push([X, yv(u) + thick(u)]); }
  poly(pts.concat(pb.reverse())); g.fillStyle = '#e7e4ef'; g.fill();
  g.strokeStyle = rgba('#ffffff', 0.5); g.lineWidth = 1; g.stroke();
  const RG = rng(11);
  for (let k = 0; k < 16; k++) {
    const u = -half + 20 + RG() * (2 * half - 40), X = x + u, Y = yv(u) + (RG() - 0.5) * 6, s = 4 + RG() * 5;
    g.save(); g.translate(X, Y); g.rotate(RG() * 3);
    poly([[-s, -s * 0.4], [-s * 0.2, -s * 0.9], [s * 0.9, -s * 0.3], [s * 0.6, s * 0.7], [-s * 0.6, s * 0.6]]); g.fillStyle = P.goldDark; g.fill();
    poly([[-s * 0.7, -s * 0.4], [-s * 0.2, -s * 0.7], [s * 0.6, -s * 0.25], [s * 0.2, s * 0.2]]); g.fillStyle = P.gold; g.fill();
    g.restore();
    const a = Math.max(0, Math.sin(t * 1.6 + k * 2.3)) ** 6; sparkle(X + 2, Y - 3, 7, a);
  }
}
function hedgehog(t) {
  const { x, y } = EGG.hedgehog;
  ell(x, y + 2, 34, 19); g.fillStyle = '#2f2014'; g.fill();
  const lv = ['#d9792e', '#b9472e', '#e0b040', '#c25e2a'];
  for (let k = 0; k < 11; k++) { ell(x - 26 + k * 5.2, y + 14 - Math.abs(k - 5) * 0.8, 6, 2.6, (k % 3 - 1) * 0.5); g.fillStyle = lv[k % 4]; g.fill(); }
  const b = 1 + Math.sin(t * 2.2) * 0.035;
  g.save(); g.translate(x, y + 4); g.scale(b, b);
  g.fillStyle = '#5f4128';
  for (let k = 0; k < 22; k++) { const a = Math.PI * 0.95 + k / 21 * Math.PI * 1.1; const r0 = 13, r1 = 21 + (k % 2) * 3; poly([[Math.cos(a - 0.12) * r0, Math.sin(a - 0.12) * r0 * 0.8], [Math.cos(a) * r1, Math.sin(a) * r1 * 0.8], [Math.cos(a + 0.12) * r0, Math.sin(a + 0.12) * r0 * 0.8]]); g.fill(); }
  ell(0, 0, 17, 12.5); g.fillStyle = vgrad(-12, 12, '#8a6440', '#5f4128'); g.fill();
  ell(10, 5, 8, 6); g.fillStyle = '#e4c7a2'; g.fill();          // tucked face
  circ(16, 6, 1.8); g.fillStyle = P.ink; g.fill();
  g.beginPath(); g.arc(9, 4, 2.2, 0.2, Math.PI - 0.2); g.strokeStyle = P.ink; g.lineWidth = 1; g.stroke();   // closed eye
  g.restore();
}
function geode(t) {
  const { x, y } = EGG.geode;
  const glow = 0.5 + 0.2 * Math.sin(t * 1.3);
  const gr = g.createRadialGradient(x, y, 4, x, y, 70); gr.addColorStop(0, rgba(P.violet, 0.45 * glow)); gr.addColorStop(1, rgba(P.violet, 0));
  circ(x, y, 70); g.fillStyle = gr; g.fill();
  const shell = [];
  for (let k = 0; k < 18; k++) { const a = k / 18 * TAU, r = 1 + ((k * 7) % 5) * 0.03; shell.push([x + Math.cos(a) * 34 * r, y + Math.sin(a) * 26 * r]); }
  poly(shell); g.fillStyle = '#6a6678'; g.fill();
  ell(x, y, 26, 19); g.fillStyle = '#3a2357'; g.fill();
  ell(x, y, 27.5, 20.5); g.strokeStyle = '#d9d3e6'; g.lineWidth = 2.4; g.stroke();
  const cc = ['#9b6bd6', '#c9a2f2', '#7a4bb8', '#e3cdfa'];
  for (let k = 0; k < 18; k++) {
    const a = k / 18 * TAU + 0.1, bx = x + Math.cos(a) * 25, by = y + Math.sin(a) * 18.5, L = 9 + (k % 3) * 4;
    const tx = x + Math.cos(a) * (25 - L), ty = y + Math.sin(a) * (18.5 - L * 0.75);
    const nx = -Math.sin(a) * 3.2, ny = Math.cos(a) * 3.2;
    poly([[bx + nx, by + ny], [tx, ty], [bx - nx, by - ny]]); g.fillStyle = cc[k % 4]; g.fill();
  }
  sparkle(x - 6, y - 5, 5, (Math.sin(t * 1.9) * 0.5 + 0.5) * 0.8);
}
function well(t) {
  const x = EGG.well.x, yTop = faceTop(x) + 2, yBot = EGG.well.y;
  // the shaft, cut in half: the far half of the stone ring shows inside
  g.fillStyle = '#2a2224'; g.fillRect(x - 24, yTop, 48, yBot - yTop);
  for (let row = 0, yy = yTop + 2; yy < yBot - 4; row++, yy += 11) for (let k = 0; k < 4; k++) { rrect(x - 21 + k * 10.5 + (row % 2) * 5 - 2, yy, 9, 8, 2); g.fillStyle = row % 3 === 1 ? '#4b4446' : '#433c3e'; g.fill(); }
  g.fillStyle = vgrad(yBot - 26, yBot, '#4a8cc0', '#2b5f8a'); g.fillRect(x - 22, yBot - 24, 44, 24);
  g.fillStyle = rgba('#ffffff', 0.6); g.fillRect(x - 22, yBot - 24, 44, 1.5);
  for (const sx of [-1, 1]) for (let row = 0, yy = yTop; yy < yBot; row++, yy += 11) { rrect(x + sx * 28 - 6 + (row % 2) * 2 * sx, yy, 12, 10, 2.5); g.fillStyle = row % 2 ? '#a19b95' : '#8d8781'; g.fill(); }
  rrect(x - 34, yBot, 68, 9, 3); g.fillStyle = '#8d8781'; g.fill();
  // rope and bucket, swaying
  const sw = Math.sin(t * 1.2) * 0.04, ropeTop = top(x) - 44, L = (yBot - 70) - ropeTop;
  const bx = x + Math.sin(sw) * L, by = ropeTop + Math.cos(sw) * L;
  g.strokeStyle = '#d8c19a'; g.lineWidth = 1.4; g.beginPath(); g.moveTo(x, ropeTop); g.lineTo(bx, by); g.stroke();
  g.save(); g.translate(bx, by); g.rotate(sw);
  g.beginPath(); g.arc(0, 4, 8, Math.PI, TAU); g.strokeStyle = '#3b3550'; g.lineWidth = 1.4; g.stroke();
  poly([[-9, 4], [9, 4], [7, 20], [-7, 20]]); g.fillStyle = '#8a5a3a'; g.fill();
  g.fillStyle = '#5b3a24'; g.fillRect(-9, 8, 18, 2); g.fillRect(-8, 15, 16, 2);
  g.restore();
}
function eggs(t) { mole(t); chest(t); amphora(t); ammonite(t); trilobite(t); dino(t); goldSeam(t); hedgehog(t); geode(t); well(t); }

// ------------------------------------------------------------------ on top: trees, buildings, animals
function treeRound(x, y, s, t, ph, big) {
  const sw = Math.sin(t * 0.9 + ph) * 2 * s;
  g.fillStyle = P.trunk;
  poly([[x - 5 * s, y + 2], [x - 3 * s, y - 70 * s], [x + 3 * s, y - 70 * s], [x + 6 * s, y + 2]]); g.fill();
  if (big) { g.lineWidth = 5 * s; g.strokeStyle = P.trunk; g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y - 50 * s); g.quadraticCurveTo(x - 18 * s, y - 70 * s, x - 34 * s + sw, y - 92 * s); g.moveTo(x + 1, y - 58 * s); g.quadraticCurveTo(x + 18 * s, y - 76 * s, x + 32 * s + sw, y - 96 * s); g.stroke(); }
  const blobs = big ? [[-50, -110, 42], [0, -140, 52], [48, -112, 44], [-20, -96, 40], [24, -92, 38], [-4, -172, 34], [62, -144, 28], [-62, -140, 30]]
    : [[-14, -86, 22], [10, -96, 26], [16, -76, 20], [-6, -112, 20]];
  for (const [bx, by, r] of blobs) { circ(x + bx * s + sw, y + by * s, r * s); g.fillStyle = P.leaf0; g.fill(); }
  for (const [bx, by, r] of blobs) { circ(x + bx * s + sw + 3 * s, y + by * s + 4 * s, r * s * 0.82); g.fillStyle = P.leaf1; g.fill(); }
  // light from the low sun behind, upper left: a lit crescent on each blob
  g.save(); for (const [bx, by, r] of blobs) { circ(x + bx * s + sw, y + by * s, r * s); } g.clip();
  for (const [bx, by, r] of blobs) { circ(x + bx * s + sw - r * s * 0.35, y + by * s - r * s * 0.4, r * s * 0.6); g.fillStyle = rgba(P.leaf2, 0.85); g.fill(); }
  g.restore();
}
function treePoplar(x, y, s, t, ph) {
  const sw = Math.sin(t * 1.1 + ph) * 2.4 * s;
  g.fillStyle = P.trunk; g.fillRect(x - 2.5 * s, y - 24 * s, 5 * s, 26 * s);
  g.beginPath(); g.moveTo(x, y - 18 * s); g.bezierCurveTo(x - 22 * s, y - 40 * s, x - 14 * s + sw, y - 110 * s, x + sw, y - 128 * s); g.bezierCurveTo(x + 14 * s + sw, y - 110 * s, x + 22 * s, y - 40 * s, x, y - 18 * s); g.fillStyle = P.leaf0; g.fill();
  g.beginPath(); g.moveTo(x - 2 * s, y - 24 * s); g.bezierCurveTo(x - 18 * s, y - 50 * s, x - 10 * s + sw, y - 106 * s, x + sw, y - 124 * s); g.quadraticCurveTo(x - 2 * s + sw, y - 70 * s, x - 2 * s, y - 24 * s); g.fillStyle = P.leaf2; g.fill();
}
function treePine(x, y, s, t, ph) {
  const sw = Math.sin(t * 1.0 + ph) * 1.6 * s;
  g.fillStyle = P.trunk; g.fillRect(x - 3 * s, y - 16 * s, 6 * s, 18 * s);
  for (let k = 0; k < 3; k++) { const yb = y - 12 * s - k * 26 * s, w = (30 - k * 7) * s; poly([[x - w, yb], [x + sw * (k + 1) / 3, yb - 44 * s], [x + w, yb]]); g.fillStyle = P.leaf0; g.fill(); poly([[x - w, yb], [x + sw * (k + 1) / 3, yb - 44 * s], [x - w * 0.15, yb]]); g.fillStyle = P.leaf1; g.fill(); }
}
function house(x, y, s, roof, t, lit) {
  const w = 34 * s, h = 26 * s, rh = 22 * s, dx = OX * 0.3 * s, dy = OY * 0.3 * s;
  poly([[x + w / 2, y], [x + w / 2 + dx, y + dy], [x + w / 2 + dx, y + dy - h], [x + w / 2, y - h]]); g.fillStyle = '#d9c3a2'; g.fill();          // side wall
  poly([[x, y - h - rh], [x + dx, y + dy - h - rh], [x + w / 2 + dx + 4 * s, y + dy - h + 2 * s], [x + w / 2 + 4 * s, y - h + 2 * s]]); g.fillStyle = mix(roof, P.ink, 0.22); g.fill(); // roof side
  poly([[x - w / 2, y], [x + w / 2, y], [x + w / 2, y - h], [x, y - h - rh], [x - w / 2, y - h]]); g.fillStyle = vgrad(y - h - rh, y, '#fff3df', '#ecdcc0'); g.fill(); // gable
  poly([[x - w / 2 - 4 * s, y - h + 2 * s], [x, y - h - rh - 2 * s], [x + w / 2 + 4 * s, y - h + 2 * s], [x + w / 2, y - h + 2 * s], [x, y - h - rh + 3 * s], [x - w / 2, y - h + 2 * s]]); g.fillStyle = roof; g.fill();
  g.fillStyle = mix(roof, P.ink, 0.35); g.fillRect(x + w / 2 + dx * 0.5 - 2 * s, y + dy * 0.5 - h - rh - 6 * s, 5 * s, 12 * s);   // chimney
  g.fillStyle = '#7a4a32'; g.fillRect(x - 4 * s, y - 13 * s, 8 * s, 13 * s);
  g.fillStyle = lit; g.fillRect(x - 13 * s, y - 20 * s, 6 * s, 7 * s); g.fillRect(x + 7 * s, y - 20 * s, 6 * s, 7 * s);
  g.fillRect(x - 3 * s, y - h - 10 * s, 6 * s, 7 * s);
}
function mill(t) {
  const [x, y] = onTop(1196, 0.1);
  house(x + 4, y, 1.45, '#5d5470', t, '#ffd37a');
  // waterwheel turning in the river
  const cx = RR - 6 + 0.1 * OX, cy = WY + 0.1 * OY - 12, r = 30, a = t * 0.9;
  g.save(); g.translate(cx, cy);
  circ(0, 0, r); g.strokeStyle = '#6e4a30'; g.lineWidth = 4; g.stroke();
  circ(0, 0, r * 0.45); g.lineWidth = 2.5; g.stroke();
  for (let k = 0; k < 8; k++) { const q = a + k / 8 * TAU; g.beginPath(); g.moveTo(Math.cos(q) * 4, Math.sin(q) * 4); g.lineTo(Math.cos(q) * r, Math.sin(q) * r); g.lineWidth = 2.2; g.stroke(); g.save(); g.rotate(q); g.fillStyle = '#8a5a3a'; g.fillRect(r - 4, -5, 10, 10); g.restore(); }
  circ(0, 0, 4.5); g.fillStyle = '#3b2a20'; g.fill();
  g.restore();
  for (let k = 0; k < 4; k++) { const ph = (t * 1.4 + k / 4) % 1; circ(cx - r - 2 - ph * 12, cy + 18 + ph * 10, 2.2 * (1 - ph)); g.fillStyle = rgba('#ffffff', 0.8 * (1 - ph)); g.fill(); }
}
function bridge() {
  const d = 0.74, [l] = onRiver(d, -1), [r] = onRiver(d, 1), y = WY + d * OY;
  const x0 = l - 24, x1 = r + 24;
  g.beginPath(); g.moveTo(x0, y + 2); g.lineTo(x0 + 10, y - 16); g.lineTo(x1 - 10, y - 16); g.lineTo(x1, y + 2);
  g.lineTo(r - 4, y + 2); g.quadraticCurveTo((l + r) / 2, y - 26, l + 4, y + 2); g.closePath();
  g.fillStyle = '#d4c3a3'; g.fill();
  g.fillStyle = '#b3a183'; g.fillRect(x0 + 8, y - 20, x1 - x0 - 16, 5);
}
function lamp(x, y, t, k) {
  g.fillStyle = '#3b3550'; g.fillRect(x - 1.2, y - 30, 2.4, 30);
  const gr = g.createRadialGradient(x, y - 32, 1, x, y - 32, 16); gr.addColorStop(0, rgba('#ffd37a', 0.9)); gr.addColorStop(1, rgba('#ffd37a', 0));
  circ(x, y - 32, 16); g.fillStyle = gr; g.fill();
  circ(x, y - 32, 3.4); g.fillStyle = '#fff1c2'; g.fill();
}
function wellHead(t) {
  const x = EGG.well.x, y = top(x) + 2;
  rrect(x - 30, y - 22, 60, 22, 3); g.fillStyle = '#9c968f'; g.fill();
  g.fillStyle = '#7f7973'; for (let k = 0; k < 4; k++) g.fillRect(x - 30 + k * 15 + 2, y - 12, 1.2, 12);
  g.fillRect(x - 30, y - 12, 60, 1.2);
  g.fillStyle = '#5b3a24'; g.fillRect(x - 26, y - 52, 3.5, 30); g.fillRect(x + 22.5, y - 52, 3.5, 30);
  g.fillRect(x - 26, y - 46, 52, 3);
  poly([[x - 34, y - 50], [x, y - 70], [x + 34, y - 50]]); g.fillStyle = '#a8553a'; g.fill();
}
function deer(x, y, s, t, fawn) {
  const lift = fawn ? 0.5 + 0.5 * Math.sin(t * 0.6 + 2) : sstep(0.1, 0.5, (Math.sin(t * 0.45) * 0.5 + 0.5));
  const body = fawn ? '#c4844e' : '#b5703c';
  g.save(); g.translate(x, y); g.scale(s, s);
  g.fillStyle = mix(body, P.ink, 0.25);
  g.fillRect(-15, -16, 3, 16); g.fillRect(10, -16, 3, 16);          // far legs
  g.fillStyle = body;
  g.fillRect(-11, -16, 3.2, 16); g.fillRect(14, -16, 3.2, 16);       // near legs
  ell(0, -22, 20, 9); g.fill();
  ell(0, -17, 14, 3.5); g.fillStyle = '#ecd2ae'; g.fill();
  ell(20, -26, 3, 2.5); g.fillStyle = '#f6efe3'; g.fill();          // tail
  // neck and head: grazing (down) or looking around (up)
  const na = lerp(2.4, 4.3, lift);
  const nx = -16 + Math.cos(na) * 16, ny = -26 + Math.sin(na) * 16;
  g.strokeStyle = body; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath(); g.moveTo(-14, -24); g.lineTo(nx, ny); g.stroke();
  g.save(); g.translate(nx, ny); g.rotate(lerp(1.2, -0.25, lift));
  ell(-5, 0, 8, 4.4); g.fillStyle = body; g.fill();
  circ(-12, 0.5, 1.6); g.fillStyle = P.ink; g.fill();
  ell(1, -5, 2, 4.2, 0.4); g.fillStyle = mix(body, P.ink, 0.15); g.fill();
  if (!fawn) { g.strokeStyle = '#ecdcc0'; g.lineWidth = 1.4; g.beginPath(); g.moveTo(0, -4); g.lineTo(3, -14); g.lineTo(6, -18); g.moveTo(3, -14); g.lineTo(-1, -18); g.stroke(); }
  g.restore();
  if (fawn) { g.fillStyle = '#f3e3c8'; for (const [a, b] of [[-6, -25], [0, -26], [6, -25], [-3, -21], [4, -21]]) { circ(a, b, 1.3); g.fill(); } }
  g.restore();
}
function rabbit(x, y, t) {
  const cyc = (t * 0.55) % 1, hopping = cyc < 0.35, k = hopping ? cyc / 0.35 : 0;
  const hopN = Math.floor(t * 0.55);
  const X = x + ((hopN % 6) < 3 ? hopN % 6 : 6 - (hopN % 6)) * 14 + (hopping ? (((hopN % 6) < 3) ? 14 : -14) * k : 0);
  const dir = (hopN % 6) < 3 ? -1 : 1;
  const Y = y - Math.sin(Math.PI * k) * 10;
  g.save(); g.translate(X, Y); g.scale(dir * 0.9, 0.9);
  ell(0, -8, 10, 7.5); g.fillStyle = '#a7907a'; g.fill();
  circ(-9, -14, 5.2); g.fill();
  ell(-8, -24, 2.2, 7, -0.15); g.fill(); ell(-11, -23, 2.2, 7, -0.4); g.fillStyle = '#8f7966'; g.fill();
  circ(9, -9, 3.4); g.fillStyle = '#f6efe3'; g.fill();
  circ(-12, -15, 1.1); g.fillStyle = P.ink; g.fill();
  g.restore();
}
function fox(t) {
  const L = 380, sp = 22, u = (t * sp) % (2 * L), fwd = u < L, p = fwd ? u : 2 * L - u;
  const x = 900 - p, d = 0.22, [X, Y] = onTop(x, d);
  const tr = Math.sin(t * 9);
  g.save(); g.translate(X, Y); g.scale(fwd ? 1 : -1, 1);
  g.strokeStyle = '#3a2a24'; g.lineWidth = 2.6; g.lineCap = 'round';
  for (const [lx, ph] of [[-10, 0], [-6, Math.PI], [10, Math.PI], [14, 0]]) { g.beginPath(); g.moveTo(lx, -12); g.lineTo(lx + Math.sin(t * 9 + ph) * 4, 0); g.stroke(); }
  ell(2, -15 + tr * 0.6, 17, 6.5); g.fillStyle = '#d9692b'; g.fill();
  g.beginPath(); g.moveTo(18, -16); g.quadraticCurveTo(34, -22, 40, -12); g.quadraticCurveTo(32, -10, 18, -12); g.closePath(); g.fill();
  ell(38, -13, 4, 2.6, 0.4); g.fillStyle = '#f6efe3'; g.fill();
  g.save(); g.translate(-16, -19 + tr * 0.6);
  poly([[0, -6], [-12, 1], [0, 4]]); g.fillStyle = '#d9692b'; g.fill(); ell(0, -1, 5.5, 5); g.fill();
  poly([[-1, -5], [1, -12], [4, -4]]); g.fillStyle = '#3a2a24'; g.fill();
  poly([[-10, 1], [-1, 1], [-1, 4]]); g.fillStyle = '#f6efe3'; g.fill();
  circ(-5, -2, 1.1); g.fillStyle = P.ink; g.fill();
  g.restore();
  g.restore();
}
function heron(t) {
  const [x, y] = onRiver(0.5, 0.62);
  const st = sstep(0, 0.25, Math.abs((t % 14) - 9) < 0.6 ? 1 - Math.abs((t % 14) - 9) / 0.6 : 0);
  g.save(); g.translate(x, y);
  g.strokeStyle = '#c9a368'; g.lineWidth = 1.6; g.beginPath(); g.moveTo(-2, -26); g.lineTo(-3, 2); g.moveTo(3, -26); g.lineTo(4, 2); g.stroke();
  ell(0, -34, 9, 12, 0.35); g.fillStyle = '#8fa3b8'; g.fill();
  ell(3, -30, 6, 9, 0.35); g.fillStyle = '#6f8399'; g.fill();
  const hx = lerp(-10, -20, st), hy = lerp(-62, -30, st);
  g.strokeStyle = '#c9d3dd'; g.lineWidth = 3.4; g.beginPath(); g.moveTo(-4, -42); g.bezierCurveTo(-14, -48, 0, -56, hx, hy); g.stroke();
  ell(hx, hy, 4, 3); g.fillStyle = '#c9d3dd'; g.fill();
  g.strokeStyle = P.ink; g.lineWidth = 1.2; g.beginPath(); g.moveTo(hx + 2, hy - 2); g.lineTo(hx + 9, hy - 4); g.stroke();
  poly([[hx - 3, hy - 1], [hx - 16, hy + 1 + st * 6], [hx - 3, hy + 2]]); g.fillStyle = '#e0a43a'; g.fill();
  g.restore();
  ell(x, y + 1, 10, 2); g.strokeStyle = rgba('#ffffff', 0.5); g.lineWidth = 1; g.stroke();
}
function duck(d, k, t, male) {
  const [x0, y] = onRiver(d, k);
  const x = x0 + Math.sin(t * 0.3 + d * 9) * 10, bob = Math.sin(t * 2 + d * 7) * 0.8;
  const r = ((t * 0.8 + d * 3) % 1); ell(x, y + 2, 9 + r * 14, 2 + r * 3); g.strokeStyle = rgba('#ffffff', 0.5 * (1 - r)); g.lineWidth = 1; g.stroke();
  g.save(); g.translate(x, y + bob);
  g.beginPath(); g.moveTo(-10, 0); g.quadraticCurveTo(-10, -9, 2, -8); g.quadraticCurveTo(10, -8, 11, -3); g.lineTo(9, 0); g.closePath(); g.fillStyle = male ? '#8d7d6c' : '#7d6650'; g.fill();
  circ(-8, -11, 4.2); g.fillStyle = male ? '#2f7a4f' : '#7d6650'; g.fill();
  if (male) { g.fillStyle = '#f6efe3'; g.fillRect(-10, -7.5, 5, 1.2); }
  poly([[-12, -12], [-17, -10.5], [-12, -9.5]]); g.fillStyle = '#e8a03a'; g.fill();
  g.restore();
}
function butterflies(t) {
  const cols = ['#f2b84b', '#c6a8f0', '#f08a7a'];
  for (let k = 0; k < 3; k++) {
    const cx = 610 + k * 70, cy = 380 - k * 10;
    const x = cx + Math.sin(t * 0.7 + k * 2) * 40 + Math.sin(t * 1.9 + k) * 10, y = cy + Math.sin(t * 1.3 + k * 1.3) * 16;
    const f = Math.abs(Math.cos(t * 13 + k * 2));
    g.save(); g.translate(x, y);
    g.fillStyle = cols[k];
    g.scale(f * 0.9 + 0.1, 1);
    ell(-4, -3, 4.5, 3.4, -0.6); g.fill(); ell(4, -3, 4.5, 3.4, 0.6); g.fill();
    g.fillStyle = mix(cols[k], P.ink, 0.25); ell(-3, 2.5, 3, 2.2, 0.5); g.fill(); ell(3, 2.5, 3, 2.2, -0.5); g.fill();
    g.fillStyle = P.ink; g.fillRect(-0.7, -4, 1.4, 8);
    g.restore();
  }
}
function birds(t) {
  for (let k = 0; k < 4; k++) {
    const a = t * (0.16 + k * 0.025) + k * 1.6;
    const x = 980 + Math.cos(a) * (260 + k * 50) + k * 30, y = 150 + Math.sin(a) * (40 + k * 8) - k * 18;
    const f = Math.sin(t * (7 + k) + k), s = 1 - k * 0.12;
    g.save(); g.translate(x, y); g.scale(s, s);
    g.beginPath(); g.moveTo(-14, -4 * f); g.quadraticCurveTo(-6, -6 - 6 * f, 0, 0); g.quadraticCurveTo(6, -6 - 6 * f, 14, -4 * f);
    g.quadraticCurveTo(6, -3 - 3 * f, 0, 2.5); g.quadraticCurveTo(-6, -3 - 3 * f, -14, -4 * f); g.fillStyle = rgba(P.ink2, 0.85); g.fill();
    g.restore();
  }
}
function petals(t) {
  for (const [a, b, c, d] of PETALS) {
    const p = ((a + t * (0.025 + c * 0.02)) % 1);
    const x = BX0 - 120 + p * (BX1 - BX0 + 300), y = 250 + b * 200 + Math.sin(t * (0.8 + d) + a * 9) * 16 + p * 50;
    g.save(); g.translate(x, y); g.rotate(t * (1 + d * 2) + a * 6);
    ell(0, 0, 2.6, 1.3 * Math.abs(Math.cos(t * 2 + b * 7)) + 0.35); g.fillStyle = d < 0.6 ? rgba('#f7c6d6', 0.9) : rgba('#fff1e0', 0.75); g.fill();
    g.restore();
  }
}
function grassFront(t) {
  for (const [x, h, a, b] of GRASS) {
    const y = top(x) + 1.5, sw = Math.sin(t * 1.6 + x * 0.025) * 3 + (a - 0.5) * 3;
    g.fillStyle = b < 0.5 ? P.grassDark : P.grass;
    poly([[x - 3, y], [x + sw, y - h], [x + 1.2, y]]); g.fill();
    poly([[x - 1, y], [x + sw * 0.8 - 4, y - h * 0.7], [x + 2, y]]); g.fill();
    if (b > 0.85) { circ(x + sw, y - h - 1, 2); g.fillStyle = a > 0.5 ? '#fff4d6' : '#f2b84b'; g.fill(); }
  }
}
function flowers(t) {
  const fc = ['#fff4d6', '#f2b84b', '#f08aa4', '#c6a8f0'];
  for (const [x, y, d, c, r] of FLOWERS) {
    const sw = Math.sin(t * 1.4 + x * 0.03) * 1.2;
    g.strokeStyle = P.grassDark; g.lineWidth = 1; g.beginPath(); g.moveTo(x, y); g.lineTo(x + sw, y - 6 - r * 4); g.stroke();
    circ(x + sw, y - 6 - r * 4, 1.8 + r * 0.8); g.fillStyle = fc[c]; g.fill();
  }
}
function reeds(t) {
  const spots = [[-1.08, 0.05], [-1.12, 0.2], [-1.05, 0.35], [1.06, 0.06], [1.1, 0.75], [-1.1, 0.85]];
  for (const [k, d] of spots) {
    const [x, y] = onRiver(d, k);
    for (let j = 0; j < 5; j++) {
      const xx = x + (j - 2) * 3.2, h = 26 + (j * 7) % 14, sw = Math.sin(t * 1.5 + xx * 0.1) * 3;
      g.strokeStyle = '#4f7d43'; g.lineWidth = 1.6; g.beginPath(); g.moveTo(xx, y + 2); g.quadraticCurveTo(xx, y - h * 0.6, xx + sw, y - h); g.stroke();
      if (j % 2 === 0) { ell(xx + sw * 0.9, y - h + 4, 2.2, 5.5, sw * 0.05); g.fillStyle = '#7a4f2e'; g.fill(); }
    }
  }
}
function lilies(t) {
  for (let k = 0; k < 12; k++) {
    const d = 0.08 + (k * 0.37 % 1) * 0.84, s = ((k * 0.61) % 1) * 1.4 - 0.7;
    const [x, y] = onRiver(d, s);
    ell(x, y, 7, 2.6); g.fillStyle = '#4f8c46'; g.fill();
    if (k % 3 === 0) { circ(x + 1, y - 1.5, 2); g.fillStyle = '#f7c6d6'; g.fill(); }
  }
}
function boulder(x, d, s) { const [X, Y] = onTop(x, d); ell(X, Y - 5 * s, 12 * s, 7 * s); g.fillStyle = '#9a96a3'; g.fill(); ell(X - 3 * s, Y - 8 * s, 7 * s, 3.5 * s); g.fillStyle = '#b8b4bf'; g.fill(); }
function molehill() { const x = EGG.mole.x + 62, y = top(x) + 2; g.beginPath(); g.moveTo(x - 18, y); g.quadraticCurveTo(x, y - 18, x + 18, y); g.closePath(); g.fillStyle = '#7a5536'; g.fill(); g.beginPath(); g.moveTo(x - 9, y - 6); g.quadraticCurveTo(x, y - 12, x + 7, y - 7); g.strokeStyle = rgba('#ffffff', 0.2); g.lineWidth = 1.5; g.stroke(); }

const PROPS = [];   // things on the block's top, drawn back to front
function prop(d, fn) { PROPS.push({ d, fn }); }
const TREES = [[470, 0.45, 'big', 1.0], [380, 0.82, 'poplar', 0.8], [415, 0.12, 'round', 0.5], [600, 0.88, 'round', 0.62], [660, 0.66, 'pine', 0.55],
  [840, 0.85, 'poplar', 0.72], [880, 0.28, 'round', 0.48], [905, 0.92, 'round', 0.55], [1225, 0.9, 'poplar', 0.75], [1520, 0.95, 'pine', 0.6],
  [770, 0.98, 'pine', 0.5], [545, 0.97, 'poplar', 0.62], [1300, 0.97, 'poplar', 0.6], [1395, 0.95, 'round', 0.5], [1500, 0.08, 'round', 0.42]];
TREES.forEach(([x, d, kind, s], i) => prop(d, (t) => { const [X, Y] = onTop(x, d); if (kind === 'poplar') treePoplar(X, Y, s, t, i); else if (kind === 'pine') treePine(X, Y, s, t, i); else treeRound(X, Y, s, t, i, kind === 'big'); }));
const HOUSES = [[1268, 0.55, '#c0573a', 1], [1335, 0.8, '#4f5d7a', 0.9], [1385, 0.3, '#c0573a', 1.05], [1468, 0.68, '#4f5d7a', 0.95], [1495, 0.25, '#b8553a', 0.9]];
HOUSES.forEach(([x, d, roof, s]) => prop(d, (t) => { const [X, Y] = onTop(x, d); house(X, Y, s, roof, t, '#ffd37a'); }));
prop(0.1, mill);
prop(0.74, bridge);
prop(0.05, wellHead);
[[1240, 0.3], [1445, 0.45], [1180, 0.72]].forEach(([x, d], k) => prop(d, (t) => { const [X, Y] = onTop(x, d); lamp(X, Y, t, k); }));
[[400, 0.4, 1], [575, 0.1, 0.8], [960, 0.6, 0.0], [1010, 0.15, 0.0], [700, 0.9, 0.9], [1180, 0.45, 0.8]].forEach(([x, d, s]) => { if (s) prop(d, () => boulder(x, d, s)); });
prop(0.45, (t) => { const [X, Y] = onTop(790, 0.45); deer(X, Y, 1.25, t, false); });
prop(0.62, (t) => { const [X, Y] = onTop(728, 0.62); deer(X, Y, 0.85, t, true); });
prop(0.2, (t) => { const [X, Y] = onTop(600, 0.2); rabbit(X, Y, t); });
prop(0.22, fox);
prop(0.5, heron);
prop(0.62, (t) => duck(0.62, -0.35, t, true));
prop(0.42, (t) => duck(0.42, 0.25, t, false));
prop(0.26, (t) => duck(0.26, -0.15, t, false));
PROPS.sort((a, b) => b.d - a.d);

// ------------------------------------------------------------------ the whole world at time t
function world(t, reveal) {
  // shadow under the floating block and a few crumbs falling away
  const gr = g.createRadialGradient(960, BOT + 60, 10, 960, BOT + 60, 700);
  gr.addColorStop(0, rgba('#0d0b18', 0.45)); gr.addColorStop(1, rgba('#0d0b18', 0));
  g.save(); g.translate(0, BOT + 60); g.scale(1, 0.06); g.translate(0, -(BOT + 60)); circ(960, BOT + 60, 700); g.fillStyle = gr; g.fill(); g.restore();
  for (const [a, b, c] of STONES.slice(0, 7)) {
    const x = BX0 + 60 + a * (BX1 - BX0 - 120), y = BOT + 22 + b * 50 + Math.sin(t * 0.8 + a * 9) * 4, s = 3 + c * 7;
    g.save(); g.translate(x, y); g.rotate(t * 0.1 + c * 5); poly([[-s, -s * 0.5], [s * 0.2, -s], [s, -s * 0.1], [s * 0.4, s * 0.8], [-s * 0.7, s * 0.6]]); g.fillStyle = mix(STR[7][2], '#8a8aa6', 0.35); g.fill(); g.restore();
  }
  rightFace();
  strata(t);
  g.strokeStyle = rgba('#fff4d6', 0.22); g.lineWidth = 2; g.beginPath(); g.moveTo(BX0, top(BX0)); g.lineTo(BX0, BOT); g.lineTo(BX1, BOT); g.stroke();
  g.save(); facePath(); g.clip(); eggs(t); g.restore();
  riverSection(t);
  // the reveal: the cut face draws in from the top down (only in the opening)
  if (reveal < 1) {
    const yr = lerp(TOP0 - 40, BOT + 4, easeOut(reveal));
    g.save(); facePath(); g.clip();
    g.fillStyle = mix(P.under1, P.ink, 0.3); g.fillRect(BX0 - 4, yr, BX1 - BX0 + 8, BOT - yr + 8);
    g.fillStyle = rgba('#fff4d6', 0.9); g.fillRect(BX0 - 4, yr - 1.5, BX1 - BX0 + 8, 3);
    g.restore();
  }
  topStrip();
  riverTop(t);
  lilies(t);
  flowers(t);
  molehill();
  for (const p of PROPS) p.fn(t);
  reeds(t);
  grassFront(t);
  butterflies(t);
  petals(t);
  birds(t);
}

// ------------------------------------------------------------------ cues and spec: times resolved like the Cutaway engine
let CUES = null, SPEC = null;
const norm = (w) => w.toLowerCase().replace(/[^a-z0-9]/g, '');
function T(ref) {
  if (typeof ref === 'number') return ref;
  let s = String(ref).trim(), off = 0;
  const m = s.match(/^(.+?)([+-]\d*\.?\d+)$/); if (m && !/^[+-]?\d*\.?\d+$/.test(s)) { s = m[1]; off = parseFloat(m[2]); }
  if (/^[+-]?\d*\.?\d+$/.test(s)) return parseFloat(s) + off;
  if (s === 'start') return off; if (s === 'end') return DUR + off; if (s === 'outro') return CUES.duration - CUES.outro_s + off;
  const endq = s.endsWith('>'); if (endq) s = s.slice(0, -1);
  const [lid, word] = s.split('.');
  const line = CUES.lines.find((l) => l.id === lid); if (!line) throw new Error('no cue line ' + lid);
  if (!word) return (endq ? line.end : line.start) + off;
  let [wd, nth] = word.split('#'); nth = +(nth || 0); wd = norm(wd);
  let hits = line.words.filter((w) => norm(w[0]) === wd); if (!hits.length) hits = line.words.filter((w) => norm(w[0]).startsWith(wd));
  const w = hits[nth]; if (!w) throw new Error(`no word ${word} in ${lid}`);
  return (endq ? w[2] : w[1]) + off;
}

// ------------------------------------------------------------------ the shots: the meadow spec's shot list, in 2D
// map -> opening wide (the cut draws in), ground -> close on the grass at the corner of the cut into the sun,
// crane -> down the cut face, crane -> into deep time, macro -> the skull, hero -> the whole section, wide.
// Shot ends are the spec's own, so frame numbers match the Blender meadow (768 = the skull, 830 = the whole section).
let SHOTS = [], LABELS = [], COUNTER = null;
const CAM = {
  map: [{ x: 975, y: 560, z: 0.96 }, { x: 960, y: 548, z: 1.04 }],
  ground: [{ x: 690, y: 392, z: 2.45 }, { x: 726, y: 386, z: 2.58 }],
  crane: [{ x: 640, y: 320, z: 2.1 }, { x: 700, y: 556, z: 2.16 }],
  crane2: [{ x: 700, y: 556, z: 2.16 }, { x: 660, y: 770, z: 2.1 }],
  macro: [{ x: EGG.dino.skull.x + 104, y: EGG.dino.skull.y + 20, z: 3.4 }, { x: EGG.dino.skull.x + 96, y: EGG.dino.skull.y + 18, z: 3.7 }],
  hero: [{ x: 990, y: 572, z: 1.1 }, { x: 960, y: 560, z: 1.0 }],
};
function buildShots() {
  const list = [];
  let t0 = 0, craneN = 0;
  for (const sc of SPEC.scenes) for (const sh of sc.shots) {
    let kind = sh.camera; if (kind === 'crane') kind = craneN++ ? 'crane2' : 'crane';
    let t1 = sh.until !== undefined ? T(sh.until) : DUR;
    list.push({ name: kind, t0, t1, labels: sh.labels || [], counter: sh.counter || null });
    for (const lb of sh.labels || []) LABELS.push({ text: lb.text.toUpperCase(), at: T(lb.at), until: Math.min(t1, T(lb.until)), point: lb.point, slot: lb.slot, shotEnd: t1 });
    if (sh.counter) COUNTER = { ...sh.counter, at: T(sh.counter.at), done: T(sh.counter.done), until: t1 };
    t0 = t1;
  }
  list[list.length - 1].t1 = DUR;
  return list;
}
function camAt(t) {
  const sh = SHOTS.find((s) => t >= s.t0 && t < s.t1) || SHOTS[SHOTS.length - 1];
  const [a, b] = CAM[sh.name]; const k = ease((t - sh.t0) / (sh.t1 - sh.t0));
  return { sh, x: lerp(a.x, b.x, k), y: lerp(a.y, b.y, k), z: lerp(a.z, b.z, k) };
}
function setCam(c, par) {
  const z = 1 + (c.z - 1) * par, x = lerp(960, c.x, par), y = lerp(540, c.y, par);
  g.setTransform(S * z, 0, 0, S * z, S * (960 - x * z), S * (540 - y * z));
}
const toScreen = (c, x, y) => [(x - c.x) * c.z + 960, (y - c.y) * c.z + 540];

// ------------------------------------------------------------------ words on screen (set in code)
function track(text, ls) { g.letterSpacing = ls + 'px'; return text; }
function label(c, lb, t) {
  // labels arrive on their word and stay until the end of their shot (an explainer builds its diagram up)
  const a = t - lb.at; if (a < 0 || t >= lb.shotEnd) return;
  const out = clamp((lb.shotEnd - t) / 0.3);
  const p = EGG[lb.point] ? (lb.point === 'dino' ? EGG.dino.skull : EGG[lb.point]) : null; if (!p) return;
  const [tx, ty] = toScreen(c, p.x, p.y);
  const sl = { 'upper-left': [-300, -170], 'lower-left': [-300, 170], 'upper-right': [300, -170], 'lower-right': [300, 170], left: [-360, 0], right: [360, 0], top: [0, -220], bottom: [0, 220] }[lb.slot] || [300, -170];
  g.font = '600 24px Inter'; track('', 4.5);
  const tw = g.measureText(lb.text).width, pw = tw + 46, ph = 46;
  let px = clamp(tx + sl[0], 70 + (sl[0] < 0 ? pw / 2 : 0), 1850 - (sl[0] > 0 ? pw / 2 : pw / 2)), py = clamp(ty + sl[1], 90, 990);
  const left = sl[0] < 0;
  const ex = left ? px + pw / 2 : px - pw / 2;   // where the leader meets the pill
  const k1 = easeOut(a / 0.35), k2 = easeOut((a - 0.2) / 0.35);
  g.globalAlpha = out;
  // target ring
  circ(tx, ty, 9 * k1); g.strokeStyle = P.cream; g.lineWidth = 2; g.stroke();
  circ(tx, ty, 3.2 * k1); g.fillStyle = P.cream; g.fill();
  // leader: from the ring, a straight run, then a short horizontal into the pill
  const elx = ex + (left ? 26 : -26);
  const pts = [[tx, ty], [elx, py], [ex, py]];
  const segL = [Math.hypot(elx - tx, py - ty), Math.abs(ex - elx)], tot = segL[0] + segL[1];
  let rem = tot * k1;
  g.beginPath(); g.moveTo(tx, ty);
  for (let i = 1; i < 3; i++) { const L = segL[i - 1], q = clamp(rem / L); g.lineTo(lerp(pts[i - 1][0], pts[i][0], q), lerp(pts[i - 1][1], pts[i][1], q)); rem -= L; if (rem <= 0) break; }
  g.strokeStyle = P.cream; g.lineWidth = 2; g.stroke();
  if (k2 > 0) {
    g.globalAlpha = out * k2;
    const cx = px + (1 - k2) * (left ? -10 : 10);
    rrect(cx - pw / 2, py - ph / 2, pw, ph, ph / 2); g.fillStyle = rgba(P.ink, 0.9); g.fill();
    g.strokeStyle = rgba(P.cream, 0.35); g.lineWidth = 1.2; g.stroke();
    circ(cx - pw / 2 + 20, py, 4); g.fillStyle = P.gold; g.fill();
    g.fillStyle = P.cream; g.textBaseline = 'middle'; g.textAlign = 'left';
    g.fillText(lb.text, cx - pw / 2 + 32, py + 1);
  }
  g.globalAlpha = 1; track('', 0);
}
function counter(t) {
  const C = COUNTER; if (!C || t < C.at || t >= C.until) return;
  const a = t - C.at, k = ease((t - C.at) / (C.done - C.at));
  const v = Math.round(lerp(C.from, C.to, k));
  const txt = v.toLocaleString('en-US');
  const alpha = clamp(a / 0.3) * clamp((C.until - t) / 0.3);
  g.globalAlpha = alpha;
  const x = 1790, y = 150;
  g.font = '800 84px Inter'; track('', -1); g.textAlign = 'right'; g.textBaseline = 'alphabetic';
  const w = Math.max(g.measureText('66,000,000').width, g.measureText(txt).width);
  rrect(x - w - 44, y - 86, w + 80, 150, 22); g.fillStyle = rgba(P.ink, 0.88); g.fill();
  g.fillStyle = P.cream; g.fillText(txt, x, y);
  g.font = '600 22px Inter'; track('', 6); g.fillStyle = P.gold; g.fillText(C.caption, x, y + 40);
  g.globalAlpha = 1; track('', 0); g.textAlign = 'left';
}
function titleCard(t) {
  const tt = SPEC.title; const a = t - T(tt.at), until = T(tt.until); if (a < 0 || t >= until) return;
  const k = easeOut(a / 0.5), out = clamp((until - t) / 0.4);
  g.globalAlpha = k * out;
  g.font = '800 80px Inter'; track('', -2);
  const w = g.measureText(tt.text).width, x = 1790 - w, y = 330;
  rrect(x - 50, y - 160 + (1 - k) * 14, w + 100, 230, 26); g.fillStyle = rgba(P.ink, 0.88); g.fill();
  g.fillStyle = P.gold; g.fillRect(x, y - 108 + (1 - k) * 10, 46, 4);
  g.font = '600 24px Inter'; track('', 9); g.fillStyle = P.gold; g.textBaseline = 'middle'; g.fillText(tt.kicker, x + 62, y - 105 + (1 - k) * 10);
  g.font = '800 80px Inter'; track('', -2); g.fillStyle = P.cream; g.textBaseline = 'alphabetic'; g.fillText(tt.text, x, y + 10 + (1 - k) * 8);
  // the strata as a small colour bar under the title: the series mark
  STR.forEach((s, i) => { g.fillStyle = s[2]; g.fillRect(x + i * 30, y + 36 + (1 - k) * 8, 26, 6); });
  g.globalAlpha = 1; track('', 0);
}
function endCard(t) {
  const t0 = T('outro'); if (t < t0) return;
  const k = easeOut((t - t0) / 0.8);
  g.fillStyle = rgba(P.ink, 0.82 * k); g.fillRect(0, 0, 1920, 1080);
  g.globalAlpha = clamp((t - t0 - 0.25) / 0.6);
  g.textAlign = 'center'; g.textBaseline = 'alphabetic';
  g.font = '800 120px Inter'; track('', 26); g.fillStyle = P.cream; g.fillText(SPEC.end.text, 960 + 13, 540);
  STR.forEach((s, i) => { g.fillStyle = s[2]; g.fillRect(960 - 4 * 34 + i * 34, 578, 30, 7); });
  g.font = '500 36px Inter'; track('', 1); g.fillStyle = rgba(P.cream, 0.85); g.fillText(SPEC.end.sub, 960, 650);
  g.globalAlpha = 1; g.textAlign = 'left'; track('', 0);
}

// ------------------------------------------------------------------ finish: vignette and film grain
let GRAIN = null;
function makeGrain() {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const x = c.getContext('2d'), im = x.createImageData(256, 256), r = rng(99);
  for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() - 0.5) * 120; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
  x.putImageData(im, 0, 0); return c;
}
function finish(i) {
  g.setTransform(S, 0, 0, S, 0, 0);
  const v = g.createRadialGradient(960, 540, 380, 960, 540, 1150); v.addColorStop(0, 'rgba(14,12,28,0)'); v.addColorStop(1, 'rgba(14,12,28,0.42)');
  g.fillStyle = v; g.fillRect(0, 0, 1920, 1080);
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.globalCompositeOperation = 'overlay'; g.globalAlpha = 0.16;
  const pat = g.createPattern(GRAIN, 'repeat'); const ox = (i * 73) % 256, oy = (i * 151) % 256;
  g.translate(-ox, -oy); g.fillStyle = pat; g.fillRect(0, 0, W + 256, H + 256);
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1;
}

// ------------------------------------------------------------------ frame
async function render(i, t) {
  const c = camAt(t);
  g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = P.ink; g.fillRect(0, 0, W, H);
  setCam(c, 0.22); background(t);
  setCam(c, 0.5); hills();
  setCam(c, 1);
  const reveal = c.sh.name === 'map' ? clamp((t - 0.6) / 3.0) : 1;
  world(t, reveal);
  g.setTransform(S, 0, 0, S, 0, 0);
  for (const lb of LABELS) if (t >= c.sh.t0 && lb.shotEnd <= c.sh.t1 + 1e-6 && lb.shotEnd > c.sh.t0) label(c, lb, t);
  counter(t);
  titleCard(t);
  endCard(t);
  finish(i);
}

(async () => {
  [SPEC, CUES] = await Promise.all([fetch('./spec.json').then((r) => r.json()), fetch('./cues.json').then((r) => r.json())]);
  SHOTS = buildShots();
  GRAIN = makeGrain();
  for (const w of ['400', '500', '600', '800']) await document.fonts.load(`${w} 40px Inter`);
  await document.fonts.ready;
  window.KF = { width: W, height: H, fps: FPS, duration: DUR, canvas, shots: SHOTS.map((s) => ({ name: s.name, dur: +(s.t1 - s.t0).toFixed(3) })), render };
  window.KF_READY = true;
})();
