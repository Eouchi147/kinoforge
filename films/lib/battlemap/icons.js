// Battle Map engine: simple icons drawn in code (no images). Each icon is drawn in a 100x100 box, bottom-centre origin, facing right.
// drawIcon(ctx, name, x, y, sizePx, { flip, team:[r,g,b], t, alpha })   (x,y = bottom-centre of the icon on screen)
const INK = '#2a190e';
const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const TEAM = { rome: [0.80, 0.12, 0.12], carthage: [0.16, 0.38, 0.88], gold: [0.96, 0.74, 0.22], neutral: [0.86, 0.80, 0.64] };
function outline(g, fill, lw = 3.2) { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; if (fill) { g.fillStyle = fill; g.fill(); } g.stroke(); }
const P = {
  elephant(g, o) {
    const team = o.team || TEAM.carthage; const skin = '#8d7e70', skin2 = '#a89886', dark = '#6e6054';
    const leg = (x, y0, w, h, c) => { g.beginPath(); g.roundRect(x, y0, w, h, 5); outline(g, c); };
    const sw = Math.sin((o.t || 0) * 7) * 3; // walking sway of the legs
    leg(20 + sw, 66, 12, 31, dark); leg(60 - sw, 66, 12, 31, dark);
    // tail
    g.beginPath(); g.moveTo(14, 46); g.quadraticCurveTo(4, 56, 8 + sw * 0.5, 74); g.lineWidth = 3.6; g.strokeStyle = INK; g.stroke();
    // body
    g.beginPath(); g.ellipse(44, 54, 33, 25, 0, 0, Math.PI * 2); outline(g, skin);
    leg(32 - sw, 66, 13, 31, skin); leg(50 + sw, 66, 13, 31, skin);
    g.beginPath(); g.ellipse(44, 54, 33, 25, 0, 0, Math.PI * 2); g.fillStyle = skin; g.fill();
    g.beginPath(); g.ellipse(44, 54, 33, 25, 0, 0, Math.PI * 2); g.lineWidth = 3.2; g.strokeStyle = INK; g.stroke();
    // blanket + trim
    g.beginPath(); g.moveTo(22, 34); g.quadraticCurveTo(44, 24, 64, 36); g.lineTo(62, 62); g.lineTo(24, 62); g.closePath(); outline(g, rgb(team), 2.6);
    g.beginPath(); g.moveTo(24, 60); g.lineTo(62, 60); g.lineWidth = 3; g.strokeStyle = '#f4cf63'; g.stroke();
    g.beginPath(); g.roundRect(32, 20, 22, 14, 4); outline(g, '#c9a15a', 2.6); // little howdah
    // head, ear, trunk, tusk
    g.beginPath(); g.moveTo(88, 52); g.quadraticCurveTo(104, 58, 98, 80); g.quadraticCurveTo(95, 90, 88, 88); g.lineWidth = 11; g.strokeStyle = INK; g.stroke();
    g.beginPath(); g.moveTo(88, 52); g.quadraticCurveTo(104, 58, 98, 80); g.quadraticCurveTo(95, 90, 88, 88); g.lineWidth = 6.2; g.strokeStyle = skin; g.stroke();
    g.beginPath(); g.arc(76, 46, 19, 0, Math.PI * 2); outline(g, skin);
    g.beginPath(); g.ellipse(66, 46, 11, 16, 0.15, 0, Math.PI * 2); outline(g, skin2, 2.8);
    g.beginPath(); g.moveTo(84, 62); g.quadraticCurveTo(100, 62, 104, 74); g.lineWidth = 4.4; g.strokeStyle = INK; g.stroke(); g.lineWidth = 2.2; g.strokeStyle = '#f6efd8'; g.stroke();
    g.beginPath(); g.arc(82, 41, 2.3, 0, Math.PI * 2); g.fillStyle = INK; g.fill();
  },
  ship(g, o) {
    const team = o.team || TEAM.rome; const bob = Math.sin((o.t || 0) * 3) * 1.5; g.save(); g.translate(0, bob);
    g.beginPath(); g.moveTo(14, 12); g.lineTo(14, 74); g.lineWidth = 0.01; g.restore(); g.save(); g.translate(0, bob);
    g.beginPath(); g.roundRect(48, 14, 4, 50, 1.5); outline(g, '#6b4a2a', 2.4);
    g.beginPath(); g.moveTo(52, 18); g.quadraticCurveTo(84, 36, 80, 58); g.lineTo(52, 58); g.closePath(); outline(g, '#f4ead0', 2.8);
    g.beginPath(); g.moveTo(52, 34); g.quadraticCurveTo(70, 42, 68, 46); g.lineTo(52, 46); g.closePath(); g.fillStyle = rgb(team); g.fill();
    g.beginPath(); g.moveTo(8, 58); g.lineTo(94, 58); g.quadraticCurveTo(100, 50, 100, 42); g.quadraticCurveTo(98, 78, 66, 88); g.lineTo(32, 88); g.quadraticCurveTo(12, 82, 8, 58); g.closePath(); outline(g, '#8a5a30', 3.4);
    g.beginPath(); g.moveTo(14, 66); g.lineTo(92, 66); g.lineWidth = 3; g.strokeStyle = '#f4cf63'; g.stroke();
    for (const x of [28, 44, 60]) { g.beginPath(); g.moveTo(x, 74); g.lineTo(x - 9, 94); g.lineWidth = 3; g.strokeStyle = INK; g.stroke(); }
    g.restore(); g.beginPath(); g.moveTo(6, 96); g.quadraticCurveTo(20, 90, 34, 96); g.quadraticCurveTo(48, 102, 62, 96); g.quadraticCurveTo(76, 90, 94, 96); g.lineWidth = 3; g.strokeStyle = 'rgba(60,110,160,0.85)'; g.stroke();
  },
  crown(g, o) {
    g.beginPath(); g.moveTo(14, 84); g.lineTo(10, 34); g.lineTo(32, 56); g.lineTo(50, 24); g.lineTo(68, 56); g.lineTo(90, 34); g.lineTo(86, 84); g.closePath(); outline(g, '#f2c230', 3.4);
    g.beginPath(); g.rect(14, 72, 72, 12); outline(g, '#d99a14', 2.6);
    for (const [x, y, c] of [[10, 34, '#e23a3a'], [50, 24, '#3a7be2'], [90, 34, '#e23a3a']]) { g.beginPath(); g.arc(x, y, 6, 0, Math.PI * 2); outline(g, c, 2.4); }
    g.beginPath(); g.moveTo(26, 62); g.lineTo(28, 78); g.lineWidth = 3.2; g.strokeStyle = 'rgba(255,255,255,0.55)'; g.stroke();
  },
  helmet(g, o) {
    const team = o.team || TEAM.rome; const steel = '#c3c0b6', steel2 = '#9b988f';
    g.beginPath(); g.moveTo(30, 40); g.quadraticCurveTo(50, -4, 82, 38); g.quadraticCurveTo(70, 26, 52, 24); g.quadraticCurveTo(38, 26, 30, 40); g.closePath(); outline(g, rgb(team), 3); // plume
    for (let k = 0; k < 6; k++) { g.beginPath(); g.moveTo(36 + k * 7.4, 30 - Math.sin(k / 5 * Math.PI) * 5); g.lineTo(38 + k * 7.4, 41); g.lineWidth = 1.8; g.strokeStyle = 'rgba(30,5,5,0.7)'; g.stroke(); }
    g.beginPath(); g.moveTo(18, 70); g.quadraticCurveTo(18, 34, 52, 34); g.quadraticCurveTo(84, 34, 84, 70); g.lineTo(84, 76); g.lineTo(18, 76); g.closePath(); outline(g, steel, 3.4);
    g.beginPath(); g.moveTo(20, 70); g.quadraticCurveTo(12, 78, 14, 94); g.lineTo(32, 92); g.lineTo(30, 76); g.closePath(); outline(g, steel2, 3); // neck guard
    g.beginPath(); g.moveTo(66, 76); g.lineTo(84, 76); g.lineTo(80, 98); g.quadraticCurveTo(72, 100, 66, 92); g.closePath(); outline(g, steel2, 3); // cheek piece
    g.beginPath(); g.moveTo(26, 56); g.quadraticCurveTo(34, 42, 52, 40); g.lineWidth = 4; g.strokeStyle = 'rgba(255,255,255,0.55)'; g.stroke();
    g.beginPath(); g.moveTo(18, 70); g.lineTo(84, 70); g.lineWidth = 3; g.strokeStyle = '#d8aa3c'; g.stroke();
  },
  heart(g, o) {
    g.beginPath(); g.moveTo(50, 90); g.bezierCurveTo(6, 58, 6, 24, 30, 20); g.bezierCurveTo(42, 18, 48, 28, 50, 34); g.bezierCurveTo(52, 28, 58, 18, 70, 20); g.bezierCurveTo(94, 24, 94, 58, 50, 90); g.closePath(); outline(g, o.fill || '#e8394f', 3.6);
    g.beginPath(); g.moveTo(24, 40); g.quadraticCurveTo(26, 30, 36, 30); g.lineWidth = 4; g.strokeStyle = 'rgba(255,255,255,0.6)'; g.stroke();
  },
  tent(g, o) {
    const team = o.team || TEAM.rome; g.beginPath(); g.moveTo(6, 92); g.lineTo(50, 20); g.lineTo(94, 92); g.closePath(); outline(g, '#efe3c2', 3.4);
    g.beginPath(); g.moveTo(50, 20); g.lineTo(38, 92); g.lineTo(62, 92); g.closePath(); outline(g, rgb(team, 0.8), 3);
    g.beginPath(); g.moveTo(50, 20); g.lineTo(50, 4); g.lineWidth = 3; g.strokeStyle = INK; g.stroke(); g.beginPath(); g.moveTo(50, 4); g.lineTo(68, 10); g.lineTo(50, 16); g.closePath(); outline(g, rgb(team), 2);
  },
  bow(g, o) {
    g.beginPath(); g.arc(30, 50, 44, -1.15, 1.15); g.lineWidth = 6; g.strokeStyle = INK; g.stroke(); g.lineWidth = 3.4; g.strokeStyle = '#9a6a35'; g.stroke();
    const a = 1.15; const x = 30 + 44 * Math.cos(a), y1 = 50 - 44 * Math.sin(a), y2 = 50 + 44 * Math.sin(a); g.beginPath(); g.moveTo(x, y1); g.lineTo(x, y2); g.lineWidth = 1.8; g.strokeStyle = INK; g.stroke();
  },
  burst(g, o) {
    g.beginPath(); const n = 12; for (let k = 0; k < n * 2; k++) { const r = k % 2 ? 26 : 46; const a = k / (n * 2) * Math.PI * 2; const px = 50 + Math.cos(a) * r, py = 56 + Math.sin(a) * r * 0.9; k ? g.lineTo(px, py) : g.moveTo(px, py); } g.closePath(); outline(g, '#ffd23f', 3.6);
    g.beginPath(); for (let k = 0; k < n * 2; k++) { const r = k % 2 ? 14 : 28; const a = k / (n * 2) * Math.PI * 2 + 0.1; const px = 50 + Math.cos(a) * r, py = 56 + Math.sin(a) * r * 0.9; k ? g.lineTo(px, py) : g.moveTo(px, py); } g.closePath(); g.fillStyle = '#fff3b0'; g.fill();
  },
  city(g, o) {
    const team = o.team || TEAM.carthage; g.beginPath(); g.rect(12, 46, 76, 46); outline(g, '#e6d3a4', 3.2); for (const x of [12, 30, 48, 66, 80]) { g.beginPath(); g.rect(x, 38, 8, 10); outline(g, '#e6d3a4', 2.4); }
    g.beginPath(); g.rect(40, 22, 20, 70); outline(g, '#d9c08a', 3); g.beginPath(); g.moveTo(40, 22); g.lineTo(50, 8); g.lineTo(60, 22); g.closePath(); outline(g, rgb(team), 3);
    g.beginPath(); g.moveTo(44, 92); g.lineTo(44, 74); g.quadraticCurveTo(50, 64, 56, 74); g.lineTo(56, 92); g.closePath(); outline(g, '#5a3d22', 2.4);
  },
  book(g, o) {
    g.beginPath(); g.moveTo(8, 36); g.quadraticCurveTo(30, 28, 50, 40); g.lineTo(50, 90); g.quadraticCurveTo(30, 78, 8, 86); g.closePath(); outline(g, '#f6efd8', 3.2);
    g.beginPath(); g.moveTo(92, 36); g.quadraticCurveTo(70, 28, 50, 40); g.lineTo(50, 90); g.quadraticCurveTo(70, 78, 92, 86); g.closePath(); outline(g, '#efe5c6', 3.2);
    for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(16, 46 + k * 9); g.quadraticCurveTo(30, 42 + k * 9, 42, 50 + k * 9); g.lineWidth = 1.8; g.strokeStyle = 'rgba(60,40,20,0.6)'; g.stroke(); g.beginPath(); g.moveTo(84, 46 + k * 9); g.quadraticCurveTo(70, 42 + k * 9, 58, 50 + k * 9); g.stroke(); }
  },
  door(g, o) {
    g.beginPath(); g.moveTo(14, 96); g.lineTo(14, 40); g.quadraticCurveTo(14, 8, 50, 8); g.quadraticCurveTo(86, 8, 86, 40); g.lineTo(86, 96); g.closePath(); outline(g, '#9a6a35', 3.6);
    for (const x of [38, 62]) { g.beginPath(); g.moveTo(x, 12); g.lineTo(x, 96); g.lineWidth = 2; g.strokeStyle = 'rgba(40,20,5,0.8)'; g.stroke(); }
    for (const y of [38, 70]) { g.beginPath(); g.moveTo(14, y); g.lineTo(86, y); g.lineWidth = 4; g.strokeStyle = '#3a2a1a'; g.stroke(); }
    g.beginPath(); g.arc(72, 60, 4, 0, 7); outline(g, '#f2c230', 2);
  },
  flag(g, o) {
    const team = o.team || TEAM.rome; g.beginPath(); g.moveTo(26, 96); g.lineTo(26, 6); g.lineWidth = 5; g.strokeStyle = INK; g.stroke(); g.lineWidth = 2.4; g.strokeStyle = '#d8b26a'; g.stroke();
    g.beginPath(); g.moveTo(26, 10); g.quadraticCurveTo(52, 2, 70, 14); g.quadraticCurveTo(84, 22, 94, 18); g.lineTo(94, 52); g.quadraticCurveTo(80, 56, 68, 48); g.quadraticCurveTo(50, 38, 26, 50); g.closePath(); outline(g, rgb(team), 3);
  },
  question(g, o) { g.font = '800 120px Cinzel, serif'; g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.lineJoin = 'round'; g.lineWidth = 10; g.strokeStyle = INK; g.strokeText('?', 50, 96); g.fillStyle = '#f6e9c6'; g.fillText('?', 50, 96); },
  star(g, o) { g.beginPath(); for (let k = 0; k < 10; k++) { const r = k % 2 ? 20 : 46; const a = -Math.PI / 2 + k / 10 * Math.PI * 2; const px = 50 + Math.cos(a) * r, py = 54 + Math.sin(a) * r; k ? g.lineTo(px, py) : g.moveTo(px, py); } g.closePath(); outline(g, '#ffd23f', 3.4); },
  laurel(g, o) { for (const s of [-1, 1]) for (let k = 0; k < 6; k++) { g.save(); g.translate(50 + s * (8 + k * 5), 88 - k * 11); g.rotate(s * (0.5 + k * 0.12)); g.beginPath(); g.ellipse(0, 0, 11, 5, 0, 0, 7); outline(g, '#5f8f3c', 2.2); g.restore(); } },
  sword(g, o) { g.save(); g.translate(50, 50); g.rotate(-0.78); g.beginPath(); g.moveTo(-5, 44); g.lineTo(-5, -34); g.lineTo(0, -46); g.lineTo(5, -34); g.lineTo(5, 44); g.closePath(); outline(g, '#d4d6da', 2.8); g.beginPath(); g.rect(-16, 44, 32, 6); outline(g, '#c99a2e', 2.6); g.beginPath(); g.rect(-3, 50, 6, 14); outline(g, '#6b4a2a', 2.4); g.restore(); },
};
P.no = (g, o) => { g.beginPath(); g.arc(50, 56, 38, 0, 7); g.lineWidth = 11; g.strokeStyle = INK; g.stroke(); g.lineWidth = 6; g.strokeStyle = '#e0302a'; g.stroke(); g.beginPath(); g.moveTo(24, 82); g.lineTo(76, 30); g.lineWidth = 11; g.strokeStyle = INK; g.stroke(); g.lineWidth = 6; g.strokeStyle = '#e0302a'; g.stroke(); };
P.hug = (g, o) => { const outer = rgb(o.team || TEAM.carthage), inner = rgb(o.inner || TEAM.rome); g.beginPath(); g.roundRect(8, 22, 84, 66, 14); g.lineWidth = 15; g.strokeStyle = INK; g.stroke(); g.lineWidth = 9; g.strokeStyle = outer; g.stroke();
  g.beginPath(); g.roundRect(30, 40, 40, 30, 4); outline(g, inner, 3); for (const [x, y, a] of [[4, 55, 0], [96, 55, Math.PI], [50, 14, Math.PI / 2], [50, 96, -Math.PI / 2]]) { g.save(); g.translate(x, y); g.rotate(a); g.beginPath(); g.moveTo(-2, -9); g.lineTo(14, 0); g.lineTo(-2, 9); g.closePath(); outline(g, outer, 2.6); g.restore(); } };
P.check = (g, o) => { g.beginPath(); g.moveTo(14, 56); g.lineTo(40, 84); g.lineTo(88, 22); g.lineWidth = 20; g.strokeStyle = INK; g.stroke(); g.lineWidth = 11; g.strokeStyle = '#3fae5a'; g.stroke(); };
P.swords = (g, o) => { g.save(); P.sword(g, o); g.translate(100, 0); g.scale(-1, 1); P.sword(g, o); g.restore(); };
export const ICON_NAMES = Object.keys(P);
export function drawIcon(ctx, name, x, y, size, o = {}) {
  const fn = P[name]; if (!fn) throw new Error('unknown icon ' + name); const s = size / 100;
  ctx.save(); ctx.globalAlpha *= o.alpha ?? 1; ctx.translate(x, y); if (o.rot) ctx.rotate(o.rot); ctx.scale(o.flip ? -s : s, s); ctx.translate(-50, -100);
  ctx.shadowColor = 'rgba(30,15,5,0.35)'; ctx.shadowBlur = 6; ctx.shadowOffsetY = 3; if (typeof o.team === 'string') o = { ...o, team: TEAM[o.team] };
  fn(ctx, o); ctx.restore();
}
