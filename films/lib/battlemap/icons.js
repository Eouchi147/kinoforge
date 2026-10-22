// Battle Map engine v2: the glyph set. Refined, flat, consistent vector symbols drawn in code (no images, no emoji, no faces):
// heraldic banners in each side's colours, simplified military unit symbols, place glyphs (town, fort, camp, river, ford, hill...),
// and a few map annotations (clash, ring, gate, laurel...). One ink weight, flat fills, a thin paper halo so they read on any ground.
// Every glyph draws in a 100x100 box, origin bottom-centre (50, 100) on screen = (x, y) passed to drawIcon.
// drawIcon(ctx, name, x, y, sizePx, { flip, team: 'rome' | [r,g,b], t, rot, alpha, fill })
// v1 names (elephant ship crown helmet heart tent bow burst city book door flag question star laurel sword swords no hug check shield
// tapestry cross) still work and now draw their refined counterparts. Films add glyphs with registerIcon(name, fn).
export const INK = '#2b2018', PAPER = '#f4ead2', GOLD = '#d9a441', GOLD_D = '#a8741f';
const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
export const TEAM_RGB = { rome: [0.74, 0.12, 0.12], carthage: [0.15, 0.33, 0.74], gold: [0.90, 0.68, 0.22], neutral: [0.80, 0.74, 0.60], green: [0.20, 0.52, 0.30], cream: [0.95, 0.90, 0.78], ink: [0.36, 0.20, 0.12] };
const LW = 2.6;
const ink = (g, lw = LW) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; g.stroke(); };
const fillInk = (g, fill, lw = LW) => { if (fill) { g.fillStyle = fill; g.fill(); } ink(g, lw); };
const teamOf = (o, def = 'rome') => o.team || TEAM_RGB[def];
const pale = (c, k = 0.55) => [c[0] + (1 - c[0]) * k, c[1] + (1 - c[1]) * k, c[2] + (1 - c[2]) * k];

// ------------------------------------------------------------------ heraldry
function pennant(g, o, swallow = true) { // a staff with a swallowtail pennant
  const team = teamOf(o); const wave = Math.sin((o.t || 0) * 2.4) * 2.2;
  g.beginPath(); g.moveTo(30, 98); g.lineTo(30, 8); ink(g, 5.2); g.beginPath(); g.moveTo(30, 98); g.lineTo(30, 8); g.lineWidth = 2.2; g.strokeStyle = GOLD; g.stroke();
  g.beginPath(); g.arc(30, 7, 3.6, 0, 7); fillInk(g, GOLD, 1.8);
  g.beginPath(); g.moveTo(31, 13); g.bezierCurveTo(50, 10 + wave, 66, 16 - wave, 90, 14 + wave * 0.6); if (swallow) { g.lineTo(78, 31); g.lineTo(90, 48 + wave * 0.6); } else g.lineTo(90, 48 + wave * 0.6);
  g.bezierCurveTo(66, 50 - wave, 50, 44 + wave, 31, 47); g.closePath(); fillInk(g, rgb(team), 2.4);
  g.beginPath(); g.moveTo(35, 18); g.bezierCurveTo(50, 15 + wave, 64, 21 - wave, 80, 19 + wave * 0.6); g.lineWidth = 1.6; g.strokeStyle = GOLD; g.stroke();
  g.beginPath(); g.arc(50, 30 + wave * 0.1, 6.5, 0, 7); g.fillStyle = GOLD; g.fill(); g.lineWidth = 1.4; g.strokeStyle = INK; g.stroke();
}
function vexillum(g, o) { // a Roman-style square standard hanging from a crossbar, with a fringe
  const team = teamOf(o); const sw = Math.sin((o.t || 0) * 1.8) * 1.2;
  g.beginPath(); g.moveTo(50, 99); g.lineTo(50, 6); ink(g, 5.2); g.beginPath(); g.moveTo(50, 99); g.lineTo(50, 6); g.lineWidth = 2.2; g.strokeStyle = GOLD; g.stroke();
  g.beginPath(); g.moveTo(24, 16); g.lineTo(76, 16); ink(g, 4.6); g.beginPath(); g.moveTo(24, 16); g.lineTo(76, 16); g.lineWidth = 2; g.strokeStyle = GOLD; g.stroke();
  g.beginPath(); g.moveTo(50, 2); g.lineTo(55, 9); g.lineTo(50, 13); g.lineTo(45, 9); g.closePath(); fillInk(g, GOLD, 1.6);
  g.beginPath(); g.moveTo(27, 18); g.lineTo(73, 18); g.lineTo(73 + sw, 58); g.lineTo(27 + sw, 58); g.closePath(); fillInk(g, rgb(team), 2.4);
  g.beginPath(); g.rect(31 + sw * 0.3, 22, 38, 32); g.lineWidth = 1.5; g.strokeStyle = GOLD; g.stroke();
  for (let x = 30; x <= 70; x += 5) { g.beginPath(); g.moveTo(x + sw, 58); g.lineTo(x + sw, 64); g.lineWidth = 1.6; g.strokeStyle = GOLD_D; g.stroke(); }
  g.beginPath(); g.moveTo(50 + sw * 0.5, 28); g.lineTo(58 + sw * 0.5, 38); g.lineTo(50 + sw * 0.5, 48); g.lineTo(42 + sw * 0.5, 38); g.closePath(); g.fillStyle = GOLD; g.fill();
}
function shieldH(g, o) { const team = teamOf(o, 'carthage');
  g.beginPath(); g.moveTo(18, 14); g.lineTo(82, 14); g.lineTo(82, 50); g.bezierCurveTo(82, 74, 66, 88, 50, 96); g.bezierCurveTo(34, 88, 18, 74, 18, 50); g.closePath(); fillInk(g, rgb(team), 2.8);
  g.beginPath(); g.moveTo(24, 20); g.lineTo(76, 20); g.lineTo(76, 50); g.bezierCurveTo(76, 70, 63, 82, 50, 89); g.bezierCurveTo(37, 82, 24, 70, 24, 50); g.closePath(); g.lineWidth = 1.6; g.strokeStyle = GOLD; g.stroke();
  g.beginPath(); g.arc(50, 46, 9, 0, 7); g.fillStyle = GOLD; g.fill(); }

// ------------------------------------------------------------------ unit symbols (a frame with the arm's sign, team tint)
function unitFrame(g, o, sign) {
  const team = teamOf(o); g.beginPath(); g.rect(12, 34, 76, 50); fillInk(g, rgb(pale(team, 0.62)), 3);
  g.beginPath(); g.rect(12, 34, 76, 50); g.lineWidth = 3; g.strokeStyle = rgb(team, 0.85); g.save(); g.clip(); g.beginPath(); g.rect(12, 34, 76, 6); g.fillStyle = rgb(team); g.fill(); g.restore();
  g.beginPath(); g.rect(12, 34, 76, 50); ink(g, 3);
  g.save(); g.strokeStyle = INK; g.fillStyle = INK; g.lineWidth = 3; g.lineCap = 'round'; sign(g); g.restore();
}
const SIGNS = {
  infantry: (g) => { g.beginPath(); g.moveTo(12, 40); g.lineTo(88, 84); g.moveTo(88, 40); g.lineTo(12, 84); g.stroke(); },
  heavy: (g) => { SIGNS.infantry(g); g.beginPath(); g.rect(40, 50, 20, 18); g.fillStyle = PAPER; g.fill(); g.stroke(); g.beginPath(); g.moveTo(44, 59); g.lineTo(56, 59); g.stroke(); },
  cavalry: (g) => { g.beginPath(); g.moveTo(12, 84); g.lineTo(88, 40); g.stroke(); },
  light: (g) => { g.beginPath(); g.moveTo(12, 84); g.lineTo(88, 40); g.stroke(); g.beginPath(); g.arc(50, 62, 7, 0, 7); g.stroke(); },
  archers: (g) => { g.beginPath(); g.arc(36, 59, 18, -1.2, 1.2); g.stroke(); g.beginPath(); g.moveTo(42, 59); g.lineTo(78, 59); g.stroke(); g.beginPath(); g.moveTo(78, 59); g.lineTo(70, 53); g.lineTo(70, 65); g.closePath(); g.fill(); },
  elephant: (g) => { g.beginPath(); g.moveTo(28, 52); g.bezierCurveTo(34, 42, 58, 42, 64, 54); g.bezierCurveTo(70, 62, 72, 72, 66, 78); g.stroke(); g.beginPath(); g.moveTo(30, 52); g.lineTo(30, 76); g.moveTo(46, 50); g.lineTo(46, 76); g.stroke(); },
  ships: (g) => { g.beginPath(); g.moveTo(22, 66); g.lineTo(78, 66); g.lineTo(70, 76); g.lineTo(30, 76); g.closePath(); g.stroke(); g.beginPath(); g.moveTo(50, 66); g.lineTo(50, 44); g.lineTo(66, 60); g.lineTo(50, 60); g.stroke(); },
  artillery: (g) => { g.beginPath(); g.arc(50, 59, 8, 0, 7); g.fill(); },
  commander: (g) => { star(g, 50, 60, 15, 6.5, true); },
};
function star(g, cx, cy, R, r, fill = false) { g.beginPath(); for (let k = 0; k < 10; k++) { const rr = k % 2 ? r : R; const a = -Math.PI / 2 + k / 10 * Math.PI * 2; const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr; k ? g.lineTo(x, y) : g.moveTo(x, y); } g.closePath(); if (fill) g.fill(); else g.stroke(); }

// ------------------------------------------------------------------ places
const town = (g, o) => { const team = o.team ? rgb(o.team) : '#b8452c';
  g.beginPath(); g.moveTo(8, 92); g.lineTo(92, 92); ink(g, 3);
  const house = (x, w, h, roof) => { g.beginPath(); g.rect(x, 92 - h, w, h); fillInk(g, PAPER, 2.4); g.beginPath(); g.moveTo(x - 2, 92 - h); g.lineTo(x + w / 2, 92 - h - roof); g.lineTo(x + w + 2, 92 - h); g.closePath(); fillInk(g, team, 2.4); };
  house(14, 18, 22, 12); house(62, 22, 18, 12); g.beginPath(); g.rect(38, 36, 20, 56); fillInk(g, PAPER, 2.4); g.beginPath(); g.moveTo(36, 36); g.lineTo(48, 18); g.lineTo(60, 36); g.closePath(); fillInk(g, team, 2.4);
  for (const [x, y] of [[44, 50], [44, 66], [20, 80], [69, 82]]) { g.beginPath(); g.rect(x, y, 6, 7); g.fillStyle = INK; g.fill(); } };
const fort = (g, o) => { const team = o.team ? rgb(pale(o.team, 0.5)) : PAPER;
  g.beginPath(); g.rect(22, 36, 56, 52); fillInk(g, team, 3); for (const [x, y] of [[22, 36], [78, 36], [22, 88], [78, 88]]) { g.beginPath(); g.rect(x - 8, y - 8, 16, 16); fillInk(g, PAPER, 2.6); }
  g.beginPath(); g.moveTo(44, 88); g.lineTo(44, 74); g.arc(50, 74, 6, Math.PI, 0); g.lineTo(56, 88); fillInk(g, INK, 2); };
const camp = (g, o) => { const team = o.team ? rgb(o.team) : '#9a6a35';
  g.beginPath(); g.roundRect(8, 44, 84, 50, 8); g.fillStyle = 'rgba(244,234,210,0.85)'; g.fill(); g.setLineDash([6, 4]); ink(g, 2.6); g.setLineDash([]);
  const tent = (x, y, s) => { g.beginPath(); g.moveTo(x - 12 * s, y); g.lineTo(x, y - 18 * s); g.lineTo(x + 12 * s, y); g.closePath(); fillInk(g, PAPER, 2.2); g.beginPath(); g.moveTo(x, y - 18 * s); g.lineTo(x - 3 * s, y); g.lineTo(x + 3 * s, y); g.closePath(); g.fillStyle = team; g.fill(); };
  tent(32, 84, 1); tent(62, 84, 1); tent(47, 70, 0.8); };
const river = (g, o) => { for (let k = 0; k < 3; k++) { const y = 52 + k * 14; g.beginPath(); g.moveTo(10, y); g.bezierCurveTo(26, y - 9, 40, y + 9, 56, y); g.bezierCurveTo(70, y - 9, 80, y + 6, 92, y - 2); g.lineCap = 'round'; g.lineWidth = 6.4; g.strokeStyle = INK; g.stroke(); g.lineWidth = 3.2; g.strokeStyle = '#4f86b0'; g.stroke(); } };
const ford = (g, o) => { river(g, o); g.beginPath(); g.moveTo(36, 36); g.lineTo(36, 98); g.moveTo(62, 36); g.lineTo(62, 98); g.setLineDash([7, 6]); ink(g, 3.2); g.setLineDash([]); };
const hill = (g, o) => { g.beginPath(); g.moveTo(6, 92); g.bezierCurveTo(26, 40, 74, 40, 94, 92); g.closePath(); fillInk(g, '#d9c38e', 2.8); for (let k = 0; k < 7; k++) { const x = 22 + k * 9.5; g.beginPath(); g.moveTo(x, 92); g.lineTo(x + (k - 3) * 1.6, 74 - Math.sin(k / 6 * Math.PI) * 14); ink(g, 1.8); } };
const mountain = (g, o) => { g.beginPath(); g.moveTo(4, 92); g.lineTo(38, 26); g.lineTo(54, 52); g.lineTo(66, 38); g.lineTo(96, 92); g.closePath(); fillInk(g, '#c7b49a', 2.8); g.beginPath(); g.moveTo(30, 42); g.lineTo(38, 26); g.lineTo(46, 40); g.lineTo(40, 36); g.closePath(); g.fillStyle = PAPER; g.fill(); for (let k = 0; k < 5; k++) { g.beginPath(); g.moveTo(40 + k * 6, 92); g.lineTo(44 + k * 5, 60 + k * 4); ink(g, 1.6); } };
const woods = (g, o) => { for (const [x, y, r] of [[30, 66, 18], [66, 62, 20], [48, 50, 16]]) { g.beginPath(); g.moveTo(x, y + r); g.lineTo(x, y + r + 12); ink(g, 3); g.beginPath(); g.arc(x, y, r, 0, 7); fillInk(g, '#8aa25a', 2.6); } };
const bridge = (g, o) => { river(g, o); g.beginPath(); g.moveTo(8, 50); g.quadraticCurveTo(50, 30, 92, 50); g.lineTo(92, 58); g.quadraticCurveTo(50, 38, 8, 58); g.closePath(); fillInk(g, '#c9a46a', 2.6); };
const sea = (g, o) => { for (let k = 0; k < 3; k++) { const y = 56 + k * 14, x0 = 12 + (k % 2) * 10; g.beginPath(); for (let i = 0; i < 3; i++) { const x = x0 + i * 26; g.moveTo(x, y); g.quadraticCurveTo(x + 6.5, y - 8, x + 13, y); g.quadraticCurveTo(x + 19.5, y + 8, x + 26, y); } g.lineWidth = 3.2; g.strokeStyle = '#3f74a0'; g.lineCap = 'round'; g.stroke(); } };
const plain = (g, o) => { for (let k = 0; k < 4; k++) { const y = 56 + k * 11; g.beginPath(); g.moveTo(14 + k * 4, y); g.lineTo(86 - k * 4, y); g.setLineDash([10, 6]); ink(g, 2); g.setLineDash([]); } };

// ------------------------------------------------------------------ annotations
const crown = (g, o) => { g.beginPath(); g.moveTo(16, 82); g.lineTo(12, 40); g.lineTo(32, 58); g.lineTo(50, 30); g.lineTo(68, 58); g.lineTo(88, 40); g.lineTo(84, 82); g.closePath(); fillInk(g, GOLD, 2.8); g.beginPath(); g.rect(16, 74, 68, 8); fillInk(g, GOLD_D, 2.2); for (const x of [12, 50, 88]) { g.beginPath(); g.arc(x, x === 50 ? 28 : 38, 4.6, 0, 7); fillInk(g, PAPER, 1.8); } };
const helmet = (g, o) => { const team = teamOf(o); // a flat crested helmet in profile (no face, no shine)
  g.beginPath(); g.moveTo(26, 46); g.bezierCurveTo(30, 22, 64, 18, 78, 40); g.bezierCurveTo(70, 30, 46, 28, 26, 46); g.closePath(); fillInk(g, rgb(team), 2.4);
  g.beginPath(); g.moveTo(22, 82); g.lineTo(22, 60); g.bezierCurveTo(22, 40, 40, 34, 54, 34); g.bezierCurveTo(70, 34, 80, 46, 80, 62); g.lineTo(80, 70); g.lineTo(62, 70); g.lineTo(62, 88); g.lineTo(46, 88); g.lineTo(46, 74); g.lineTo(34, 82); g.closePath(); fillInk(g, '#b9b3a3', 2.6);
  g.beginPath(); g.moveTo(22, 60); g.lineTo(80, 60); ink(g, 1.8); };
const laurel = (g, o) => { g.save(); g.translate(50, 56); for (const s of [-1, 1]) { g.beginPath(); g.arc(0, 0, 32, s < 0 ? Math.PI * 0.55 : Math.PI * 0.45, s < 0 ? Math.PI * 1.35 : -Math.PI * 0.35, s > 0); ink(g, 2.2);
    for (let k = 0; k < 7; k++) { const a = s < 0 ? Math.PI * (0.62 + k * 0.1) : Math.PI * (0.38 - k * 0.1); const x = Math.cos(a) * 32, y = Math.sin(a) * 32; g.save(); g.translate(x, y); g.rotate(a + (s < 0 ? -0.6 : 0.6) + Math.PI / 2); g.beginPath(); g.ellipse(0, -6, 3.6, 8, 0, 0, 7); fillInk(g, '#8aa25a', 1.6); g.restore(); } } g.restore(); };
const book = (g, o) => { g.beginPath(); g.moveTo(50, 40); g.bezierCurveTo(38, 32, 22, 32, 10, 38); g.lineTo(10, 86); g.bezierCurveTo(22, 80, 38, 80, 50, 88); g.bezierCurveTo(62, 80, 78, 80, 90, 86); g.lineTo(90, 38); g.bezierCurveTo(78, 32, 62, 32, 50, 40); g.closePath(); fillInk(g, PAPER, 2.6); g.beginPath(); g.moveTo(50, 40); g.lineTo(50, 88); ink(g, 2);
  for (let k = 0; k < 4; k++) { for (const s of [-1, 1]) { g.beginPath(); g.moveTo(50 + s * 8, 50 + k * 8); g.lineTo(50 + s * 32, 48 + k * 8); g.lineWidth = 1.4; g.strokeStyle = 'rgba(43,32,24,0.55)'; g.stroke(); } } };
const scroll = (g, o) => { g.beginPath(); g.roundRect(18, 30, 64, 56, 4); fillInk(g, PAPER, 2.6); for (const y of [30, 86]) { g.beginPath(); g.ellipse(50, y, 36, 5, 0, 0, 7); fillInk(g, '#e2cf9e', 2.2); } for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(28, 44 + k * 9); g.lineTo(72, 44 + k * 9); g.lineWidth = 1.4; g.strokeStyle = 'rgba(43,32,24,0.5)'; g.stroke(); } };
const sword = (g, o) => { g.save(); g.translate(50, 56); g.rotate(-0.785); g.beginPath(); g.moveTo(-3.6, 30); g.lineTo(-3.6, -32); g.lineTo(0, -42); g.lineTo(3.6, -32); g.lineTo(3.6, 30); g.closePath(); fillInk(g, '#d8d4c8', 2.2); g.beginPath(); g.rect(-13, 30, 26, 5); fillInk(g, GOLD, 2); g.beginPath(); g.rect(-3, 35, 6, 12); fillInk(g, '#6b4a2a', 2); g.beginPath(); g.arc(0, 50, 4, 0, 7); fillInk(g, GOLD, 1.8); g.restore(); };
const swords = (g, o) => { g.save(); sword(g, o); g.translate(100, 0); g.scale(-1, 1); sword(g, o); g.restore(); };
const clash = (g, o) => { g.save(); g.translate(50, 60); for (const s of [-1, 1]) { g.save(); g.rotate(s * 0.785); g.beginPath(); g.moveTo(0, -30); g.lineTo(0, 30); g.moveTo(-8, 18); g.lineTo(8, 18); g.lineWidth = 7; g.strokeStyle = PAPER; g.lineCap = 'round'; g.stroke(); g.lineWidth = 3.2; g.strokeStyle = INK; g.stroke(); g.restore(); } g.restore(); };
const no = (g, o) => { g.beginPath(); g.arc(50, 58, 34, 0, 7); g.lineWidth = 9; g.strokeStyle = PAPER; g.stroke(); g.lineWidth = 4.4; g.strokeStyle = '#a3241c'; g.stroke(); g.beginPath(); g.moveTo(26, 82); g.lineTo(74, 34); g.lineWidth = 9; g.strokeStyle = PAPER; g.stroke(); g.lineWidth = 4.4; g.strokeStyle = '#a3241c'; g.stroke(); };
const check = (g, o) => { g.beginPath(); g.moveTo(20, 60); g.lineTo(42, 82); g.lineTo(84, 30); g.lineWidth = 11; g.strokeStyle = PAPER; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(); g.lineWidth = 5; g.strokeStyle = '#2f6b3a'; g.stroke(); };
const question = (g, o) => { g.beginPath(); g.arc(50, 58, 34, 0, 7); fillInk(g, PAPER, 2.6); g.font = '600 52px "Cinzel", serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = INK; g.fillText('?', 51, 61); };
const gate = (g, o) => { g.beginPath(); g.rect(16, 30, 12, 64); fillInk(g, '#c9a46a', 2.4); g.beginPath(); g.rect(72, 30, 12, 64); fillInk(g, '#c9a46a', 2.4); g.beginPath(); g.rect(28, 52, 44, 10); fillInk(g, rgb(teamOf(o, 'carthage')), 2.4); g.beginPath(); g.rect(28, 70, 44, 10); fillInk(g, rgb(teamOf(o, 'carthage')), 2.4); };
const ring = (g, o) => { const team = rgb(teamOf(o, 'carthage')); g.beginPath(); g.arc(50, 58, 32, 0, 7); g.lineWidth = 9; g.strokeStyle = INK; g.stroke(); g.lineWidth = 5; g.strokeStyle = team; g.stroke();
  for (let k = 0; k < 4; k++) { const a = k * Math.PI / 2 + 0.6; const x = 50 + Math.cos(a) * 32, y = 58 + Math.sin(a) * 32; g.save(); g.translate(x, y); g.rotate(a + Math.PI / 2); g.beginPath(); g.moveTo(6, 0); g.lineTo(-5, -6); g.lineTo(-5, 6); g.closePath(); fillInk(g, team, 1.6); g.restore(); } };
const envelop = (g, o) => { const outer = rgb(teamOf(o, 'carthage')), inner = rgb(o.inner || TEAM_RGB.rome); // the double envelopment as a textbook diagram
  g.beginPath(); g.rect(36, 46, 28, 22); fillInk(g, inner, 2.4);
  for (const s of [-1, 1]) { g.beginPath(); g.moveTo(80, 57 + s * 8); g.bezierCurveTo(84, 57 + s * 34, 30, 57 + s * 36, 20, 57 + s * 12); g.lineWidth = 9; g.strokeStyle = INK; g.lineCap = 'round'; g.stroke(); g.lineWidth = 5; g.strokeStyle = outer; g.stroke();
    g.save(); g.translate(20, 57 + s * 12); g.rotate(s > 0 ? -2.1 : 2.1); g.beginPath(); g.moveTo(9, 0); g.lineTo(-6, -8); g.lineTo(-6, 8); g.closePath(); fillInk(g, outer, 2); g.restore(); }
  g.beginPath(); g.rect(76, 44, 8, 26); fillInk(g, outer, 2.2); };
const elephantS = (g, o) => { const team = teamOf(o, 'carthage'); // a flat side silhouette, no eye, no face
  g.beginPath(); g.moveTo(14, 90); g.lineTo(16, 62); g.bezierCurveTo(10, 44, 26, 30, 46, 32); g.bezierCurveTo(62, 26, 78, 32, 82, 46); g.bezierCurveTo(88, 56, 92, 70, 90, 86); g.lineTo(84, 86); g.bezierCurveTo(84, 74, 82, 64, 78, 60); g.lineTo(76, 90); g.lineTo(66, 90); g.lineTo(64, 70); g.lineTo(34, 70); g.lineTo(32, 90); g.lineTo(22, 90); g.lineTo(22, 72); g.closePath(); fillInk(g, '#9b9488', 2.6);
  g.beginPath(); g.moveTo(80, 56); g.quadraticCurveTo(92, 58, 96, 50); ink(g, 4.4); g.beginPath(); g.moveTo(80, 56); g.quadraticCurveTo(92, 58, 96, 50); g.lineWidth = 2; g.strokeStyle = PAPER; g.stroke();
  g.beginPath(); g.moveTo(30, 38); g.lineTo(60, 34); g.lineTo(62, 56); g.lineTo(30, 58); g.closePath(); fillInk(g, rgb(team), 2.2); g.beginPath(); g.moveTo(30, 54); g.lineTo(62, 52); g.lineWidth = 2; g.strokeStyle = GOLD; g.stroke(); };
const galley = (g, o) => { const team = teamOf(o, 'rome'); const bob = Math.sin((o.t || 0) * 2) * 1.2; g.save(); g.translate(0, bob);
  g.beginPath(); g.moveTo(48, 64); g.lineTo(48, 14); ink(g, 3.2); g.beginPath(); g.moveTo(30, 20); g.lineTo(68, 20); g.lineTo(64, 56); g.lineTo(32, 56); g.closePath(); fillInk(g, PAPER, 2.4); g.beginPath(); g.rect(34, 30, 28, 8); g.fillStyle = rgb(team); g.fill();
  for (let k = 0; k < 5; k++) { g.beginPath(); g.moveTo(26 + k * 11, 72); g.lineTo(18 + k * 11, 90); ink(g, 2); }
  g.beginPath(); g.moveTo(8, 62); g.lineTo(88, 62); g.quadraticCurveTo(96, 60, 96, 50); g.lineTo(90, 50); g.quadraticCurveTo(92, 72, 70, 76); g.lineTo(24, 76); g.quadraticCurveTo(10, 72, 8, 62); g.closePath(); fillInk(g, '#8a5a30', 2.6);
  g.beginPath(); g.moveTo(14, 67); g.lineTo(86, 67); g.lineWidth = 2; g.strokeStyle = GOLD; g.stroke(); g.restore(); };
const tapestry = (g, o) => { g.beginPath(); g.moveTo(6, 30); g.lineTo(94, 30); g.lineTo(94, 80); g.lineTo(6, 80); g.closePath(); fillInk(g, PAPER, 2.6); for (const y of [37, 73]) { g.beginPath(); g.moveTo(10, y); g.lineTo(90, y); g.lineWidth = 2.6; g.strokeStyle = '#a3402e'; g.stroke(); } if (o.fill !== 'plain') { g.font = '600 34px "Cinzel", serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = INK; g.fillText('?', 50, 57); } };
const cross = (g, o) => { g.beginPath(); g.moveTo(24, 32); g.lineTo(76, 84); g.moveTo(76, 32); g.lineTo(24, 84); g.lineWidth = 10; g.strokeStyle = PAPER; g.lineCap = 'round'; g.stroke(); g.lineWidth = 4.6; g.strokeStyle = '#a3241c'; g.stroke(); };
const tent = (g, o) => { const team = teamOf(o); g.beginPath(); g.moveTo(10, 90); g.lineTo(50, 26); g.lineTo(90, 90); g.closePath(); fillInk(g, PAPER, 2.6); g.beginPath(); g.moveTo(50, 26); g.lineTo(42, 90); g.lineTo(58, 90); g.closePath(); g.fillStyle = rgb(team); g.fill(); ink(g, 2); };

const P = {
  // heraldry and units
  banner: (g, o) => pennant(g, o, true), pennant: (g, o) => pennant(g, o, true), vexillum, flag: (g, o) => pennant(g, o, true), shield: shieldH,
  'u-infantry': (g, o) => unitFrame(g, o, SIGNS.infantry), 'u-heavy': (g, o) => unitFrame(g, o, SIGNS.heavy), 'u-elite': (g, o) => unitFrame(g, o, SIGNS.heavy), 'u-cavalry': (g, o) => unitFrame(g, o, SIGNS.cavalry),
  'u-light': (g, o) => unitFrame(g, o, SIGNS.light), 'u-archers': (g, o) => unitFrame(g, o, SIGNS.archers), 'u-elephant': (g, o) => unitFrame(g, o, SIGNS.elephant), 'u-ships': (g, o) => unitFrame(g, o, SIGNS.ships),
  'u-artillery': (g, o) => unitFrame(g, o, SIGNS.artillery), 'u-commander': (g, o) => unitFrame(g, o, SIGNS.commander),
  // places
  town, city: town, village: town, fort, camp, river, ford, hill, mountain, alps: mountain, woods, bridge, sea, plain,
  // annotations (v1 names map to refined glyphs)
  crown, helmet, commander: (g, o) => { g.beginPath(); g.arc(50, 58, 30, 0, 7); fillInk(g, PAPER, 2.6); g.fillStyle = rgb(teamOf(o)); star(g, 50, 59, 20, 8.4, true); ink(g, 1.8); },
  star: (g, o) => { g.fillStyle = GOLD; star(g, 50, 56, 40, 17, true); ink(g, 2.6); }, laurel, book, scroll, sword, swords, clash, burst: clash, no, check, question, gate, door: gate, ring, heart: ring,
  envelop, hug: envelop, elephant: elephantS, ship: galley, galley, bow: (g, o) => unitFrame(g, o, SIGNS.archers), tent, tapestry, cross,
};
export const ICON_NAMES = Object.keys(P);
export const UNIT_GLYPH = { infantry: 'u-infantry', elite: 'u-heavy', heavy: 'u-heavy', cavalry: 'u-cavalry', light: 'u-light', archers: 'u-archers', elephant: 'u-elephant', ships: 'u-ships', artillery: 'u-artillery', commander: 'u-commander' };
export function registerIcon(name, fn) { P[name] = fn; ICON_NAMES.push(name); } // films add their own glyphs: fn(g, o) draws in a 100x100 box, bottom-centre origin
export function hasIcon(name) { return !!P[name]; }
export function drawIcon(ctx, name, x, y, size, o = {}) {
  const fn = P[name]; if (!fn) throw new Error('unknown icon ' + name); const s = size / 100;
  ctx.save(); ctx.globalAlpha *= o.alpha ?? 1; ctx.translate(x, y); if (o.rot) ctx.rotate(o.rot); ctx.scale(o.flip ? -s : s, s); ctx.translate(-50, -100);
  ctx.shadowColor = o.halo === false ? 'transparent' : 'rgba(244,234,210,0.85)'; ctx.shadowBlur = Math.max(1.5, 3.5 / Math.max(s, 0.2) * s); ctx.shadowOffsetY = 0;
  if (typeof o.team === 'string') o = { ...o, team: TEAM_RGB[o.team] || TEAM_RGB.neutral }; if (typeof o.inner === 'string') o = { ...o, inner: TEAM_RGB[o.inner] };
  fn(ctx, o); ctx.restore();
}
