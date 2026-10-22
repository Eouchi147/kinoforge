// Thermopylae: film-side glyphs for the Battle Map v2 engine (no engine file changed). Registered from index.html before the film starts.
// Drawn in the v2 style: a 100x100 box, bottom-centre origin, one ink weight, flat fills, the paper halo comes from drawIcon; no faces.
//   pass   the place glyph of Thermopylae: a cliff, a narrow road and the sea
//   trail  the hidden mountain path: a mountain with a dashed path over its shoulder
//   stele  the stone with the epitaph
//   lambda a Spartan hoplite shield (the Greek side's banner in the legend)
import { registerIcon, INK, PAPER, GOLD, TEAM_RGB } from '/films/lib/battlemap/icons.js';

const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const ink = (g, lw = 2.6) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; g.stroke(); };
const fillInk = (g, fill, lw = 2.6) => { g.fillStyle = fill; g.fill(); ink(g, lw); };

function pass(g) {
  g.beginPath(); g.moveTo(6, 94); g.lineTo(6, 26); g.lineTo(18, 18); g.lineTo(28, 30); g.lineTo(36, 46); g.lineTo(40, 94); g.closePath(); fillInk(g, '#c7b49a', 2.8); // the cliff
  for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(14 + k * 6, 92); g.lineTo(16 + k * 5, 50 + k * 6); ink(g, 1.6); }
  g.beginPath(); g.moveTo(42, 94); g.lineTo(46, 52); g.lineTo(54, 52); g.lineTo(60, 94); g.closePath(); fillInk(g, '#e8d6a8', 2.2);                      // the road
  g.beginPath(); g.moveTo(50, 90); g.lineTo(50, 58); g.setLineDash([5, 5]); ink(g, 1.6); g.setLineDash([]);
  for (let k = 0; k < 3; k++) { const y = 62 + k * 12, x0 = 64; g.beginPath(); for (let i = 0; i < 2; i++) { const x = x0 + i * 14; g.moveTo(x, y); g.quadraticCurveTo(x + 3.5, y - 6, x + 7, y); g.quadraticCurveTo(x + 10.5, y + 6, x + 14, y); }
    g.lineWidth = 3; g.strokeStyle = '#3f74a0'; g.lineCap = 'round'; g.stroke(); }                                                                   // the sea
}
function trail(g) {
  g.beginPath(); g.moveTo(4, 92); g.lineTo(40, 22); g.lineTo(56, 46); g.lineTo(68, 34); g.lineTo(96, 92); g.closePath(); fillInk(g, '#c7b49a', 2.8);
  g.beginPath(); g.moveTo(32, 38); g.lineTo(40, 22); g.lineTo(48, 36); g.lineTo(42, 32); g.closePath(); g.fillStyle = PAPER; g.fill();
  g.beginPath(); g.moveTo(12, 90); g.bezierCurveTo(30, 70, 34, 52, 52, 50); g.bezierCurveTo(70, 48, 76, 66, 90, 88); g.setLineDash([6, 5]); g.lineWidth = 3.4; g.strokeStyle = rgb(TEAM_RGB.rome, 0.9); g.lineCap = 'round'; g.stroke(); g.setLineDash([]);
}
function stele(g) {
  g.beginPath(); g.moveTo(32, 94); g.lineTo(34, 30); g.quadraticCurveTo(50, 18, 66, 30); g.lineTo(68, 94); g.closePath(); fillInk(g, '#d8d0bf', 2.8);
  g.beginPath(); g.rect(24, 90, 52, 6); fillInk(g, '#b9ae98', 2.2);
  for (let k = 0; k < 5; k++) { g.beginPath(); g.moveTo(40, 42 + k * 9); g.lineTo(60, 42 + k * 9); g.lineWidth = 1.6; g.strokeStyle = 'rgba(43,32,24,0.6)'; g.stroke(); }
}
function lambda(g, o) {
  const team = o.team || TEAM_RGB.carthage;
  g.beginPath(); g.arc(50, 56, 38, 0, 7); fillInk(g, rgb(team), 3);
  g.beginPath(); g.arc(50, 56, 31, 0, 7); g.lineWidth = 2.2; g.strokeStyle = GOLD; g.stroke();
  g.beginPath(); g.moveTo(32, 78); g.lineTo(50, 32); g.lineTo(68, 78); g.lineWidth = 7; g.strokeStyle = GOLD; g.lineJoin = 'miter'; g.lineCap = 'butt'; g.stroke();
}

let done = false;
export function registerThermopylae() {
  if (done) return; done = true;
  registerIcon('pass', pass); registerIcon('trail', trail); registerIcon('stele', stele); registerIcon('lambda', lambda);
}
