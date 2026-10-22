// Hattin: icons drawn in code, registered with the Battle Map engine (100x100 box, origin bottom-centre, o.t = seconds since the icon popped in).
// No religious symbols: teams are colours and plain banners.
import { registerIcon, drawIcon } from '/films/lib/battlemap/icons.js';
const INK = '#2a190e';
const outline = (g, fill, lw = 3.2) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; if (fill) { g.fillStyle = fill; g.fill(); } g.stroke(); };
const stroke2 = (g, w, col) => { g.lineCap = 'round'; g.lineJoin = 'round'; g.lineWidth = w + 3; g.strokeStyle = INK; g.stroke(); g.lineWidth = w; g.strokeStyle = col; g.stroke(); };
const rgb = (c, k = 1) => c ? `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})` : '#c42626';
const drop = (g, x, y, s, fill = '#8fc4ee') => { g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + 9 * s, y + 15 * s, x, y + 20 * s); g.quadraticCurveTo(x - 9 * s, y + 15 * s, x, y); outline(g, fill, 2.4); };

registerIcon('sun', (g, o) => { // a sun in sunglasses: the heat is the villain
  const t = o.t || 0; g.save(); g.translate(50, 54); g.rotate(t * 0.45);
  for (let i = 0; i < 12; i++) { g.save(); g.rotate(i / 12 * Math.PI * 2); const L = i % 2 ? 40 : 47; g.beginPath(); g.moveTo(-6, -30); g.lineTo(0, -L); g.lineTo(6, -30); g.closePath(); outline(g, '#ffb21f', 2.6); g.restore(); }
  g.restore();
  g.beginPath(); g.arc(50, 54, 29, 0, 7); outline(g, '#ffd93a', 3.6);
  g.beginPath(); g.roundRect(26, 44, 21, 13, 5); outline(g, '#1b1410', 2.2); g.beginPath(); g.roundRect(53, 44, 21, 13, 5); outline(g, '#1b1410', 2.2);
  g.beginPath(); g.moveTo(47, 49); g.lineTo(53, 49); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.moveTo(33, 49); g.lineTo(38, 47); g.moveTo(60, 49); g.lineTo(65, 47); g.lineWidth = 1.8; g.strokeStyle = 'rgba(255,255,255,0.7)'; g.stroke();
  g.beginPath(); g.moveTo(36, 68); g.quadraticCurveTo(50, 78, 64, 68); g.lineWidth = 3.6; g.strokeStyle = INK; g.stroke();
});
registerIcon('flask', (g, o) => { // an empty water flask tipped over, one last drop, a sad face
  const t = o.t || 0; g.save(); g.translate(40, 54); g.rotate(1.75 + Math.sin(t * 3.2) * 0.08);
  g.beginPath(); g.roundRect(-8, -48, 16, 20, 3); outline(g, '#8b8f97', 2.8); g.beginPath(); g.roundRect(-11, -54, 22, 8, 3); outline(g, '#6e4a2a', 2.4);
  g.beginPath(); g.arc(0, 0, 33, 0, 7); outline(g, '#c79a5c', 3.4); g.beginPath(); g.arc(0, 0, 25, 0, 7); g.lineWidth = 2; g.strokeStyle = 'rgba(70,40,10,0.55)'; g.stroke();
  g.restore();
  g.beginPath(); g.arc(31, 50, 3.4, 0, 7); g.fillStyle = INK; g.fill(); g.beginPath(); g.arc(49, 50, 3.4, 0, 7); g.fill();
  g.beginPath(); g.moveTo(23, 46); g.lineTo(34, 40); g.moveTo(57, 46); g.lineTo(46, 40); g.lineWidth = 2.6; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.moveTo(31, 70); g.quadraticCurveTo(40, 61, 49, 70); g.lineWidth = 3.4; g.strokeStyle = INK; g.stroke();
  const u = (t * 0.9) % 1; if (u < 0.85) drop(g, 90, 66 + u * 20, 0.7 - u * 0.2);
  g.font = '800 15px Cinzel, serif'; g.textAlign = 'center'; g.lineJoin = 'round'; g.lineWidth = 5; g.strokeStyle = INK; g.strokeText('EMPTY', 50, 100); g.fillStyle = '#fff1c6'; g.fillText('EMPTY', 50, 100);
});
registerIcon('hook', (g, o) => { // a fishing hook with a wriggling worm (the bait)
  const t = o.t || 0; g.beginPath(); g.moveTo(50, -40); g.lineTo(50, 24); g.lineWidth = 3.2; g.strokeStyle = INK; g.stroke(); g.lineWidth = 1.4; g.strokeStyle = '#f6ecd0'; g.stroke();
  g.beginPath(); g.arc(50, 24, 4, 0, 7); outline(g, '#9a9ea6', 2.2);
  g.beginPath(); g.moveTo(50, 27); g.lineTo(50, 66); g.bezierCurveTo(50, 98, 84, 98, 84, 66); g.lineTo(84, 56); stroke2(g, 7, '#cfd2d8');
  g.beginPath(); g.moveTo(84, 58); g.lineTo(74, 70); g.lineTo(82, 70); g.closePath(); outline(g, '#cfd2d8', 2.2);
  const w = Math.sin(t * 7) * 3; g.beginPath(); g.moveTo(40, 62); g.bezierCurveTo(26 + w, 50, 30, 76 - w, 48, 74); g.bezierCurveTo(60, 72 + w, 66, 56, 58, 52); stroke2(g, 7, '#f08a9c');
  g.beginPath(); g.arc(41, 62, 1.7, 0, 7); g.fillStyle = INK; g.fill();
});
registerIcon('castle', (g, o) => {
  const col = rgb(o.team); g.beginPath(); g.rect(14, 54, 72, 40); outline(g, '#e6d3a4', 3.2);
  for (const x of [14, 30, 46, 62, 78]) { g.beginPath(); g.rect(x, 46, 8, 10); outline(g, '#e6d3a4', 2.2); }
  for (const x of [8, 66]) { g.beginPath(); g.rect(x, 28, 26, 66); outline(g, '#d9c08a', 3); for (const y of [28, 36]) for (const dx of [0, 9, 18]) { g.beginPath(); g.rect(x + dx, y - 8, 8, 8); outline(g, '#d9c08a', 2); } }
  g.beginPath(); g.moveTo(42, 94); g.lineTo(42, 72); g.quadraticCurveTo(50, 60, 58, 72); g.lineTo(58, 94); g.closePath(); outline(g, '#5a3d22', 2.4);
  g.beginPath(); g.moveTo(21, 18); g.lineTo(21, 2); g.lineWidth = 3; g.strokeStyle = INK; g.stroke(); g.beginPath(); g.moveTo(21, 2); g.lineTo(38, 8 + Math.sin((o.t || 0) * 6) * 1.6); g.lineTo(21, 14); g.closePath(); outline(g, col, 2);
});
registerIcon('thermo', (g, o) => { // the mercury climbs while the icon is on screen, then shivers at the top
  const t = o.t || 0; const lvl = Math.min(0.97, 0.16 + 0.84 * (1 - Math.exp(-t * 0.95))); const sh = lvl > 0.9 ? Math.sin(t * 40) * 1.2 : 0;
  g.save(); g.translate(sh, 0); g.beginPath(); g.roundRect(40, 4, 20, 68, 10); outline(g, '#f6efd8', 3.4);
  g.beginPath(); g.arc(50, 80, 17, 0, Math.PI * 2); outline(g, '#e23a3a', 3.4);
  g.beginPath(); g.roundRect(46, 74 - 62 * lvl, 8, 62 * lvl + 6, 3); g.fillStyle = '#e23a3a'; g.fill();
  for (let k = 0; k < 5; k++) { g.beginPath(); g.moveTo(60, 14 + k * 11); g.lineTo(k % 2 ? 66 : 70, 14 + k * 11); g.lineWidth = 2.4; g.strokeStyle = INK; g.stroke(); }
  g.restore();
});
registerIcon('flame', (g, o) => {
  const t = o.t || 0; const w = Math.sin(t * 9) * 3, w2 = Math.sin(t * 11 + 1) * 3;
  g.beginPath(); g.moveTo(50, 98); g.bezierCurveTo(10, 94, 10, 56, 36, 38 + w); g.bezierCurveTo(34, 52, 42, 52, 44, 44); g.bezierCurveTo(40, 22, 58, 12 + w2, 56, 0); g.bezierCurveTo(84, 22, 94, 46, 88, 68); g.bezierCurveTo(84, 90, 68, 98, 50, 98); g.closePath(); outline(g, '#ff7a1f', 3.4);
  g.beginPath(); g.moveTo(50, 96); g.bezierCurveTo(30, 94, 30, 70, 46, 58 + w2); g.bezierCurveTo(48, 68, 56, 66, 58, 58); g.bezierCurveTo(72, 70, 74, 92, 50, 96); g.closePath(); g.fillStyle = '#ffd23f'; g.fill();
});
registerIcon('cough', (g, o) => { // a coughing face with smoke puffs
  const t = o.t || 0; const sh = Math.sin(t * 18) * 1.6; g.save(); g.translate(sh, 0);
  g.beginPath(); g.arc(46, 58, 34, 0, 7); outline(g, '#c9d4a0', 3.6);
  g.beginPath(); g.moveTo(26, 46); g.lineTo(40, 52); g.lineTo(26, 58); g.moveTo(66, 46); g.lineTo(52, 52); g.lineTo(66, 58); g.lineWidth = 3.6; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.ellipse(46, 74, 9, 7 + Math.abs(Math.sin(t * 9)) * 3, 0, 0, 7); outline(g, '#5a2a22', 2.8);
  g.restore();
  for (let i = 0; i < 3; i++) { const u = ((t * 1.1 + i / 3) % 1); const x = 84 + u * 14, y = 66 - u * 30 - i * 3, r = 7 + u * 9; g.globalAlpha = 1 - u * 0.8; g.beginPath(); g.arc(x, y, r, 0, 7); outline(g, '#b7aca0', 2.6); }
  g.globalAlpha = 1;
});
registerIcon('eye', (g, o) => {
  const t = o.t || 0; const lx = Math.sin(t * 2.2) * 2.5;
  g.beginPath(); g.moveTo(6, 58); g.quadraticCurveTo(50, 8, 94, 58); g.quadraticCurveTo(50, 108, 6, 58); g.closePath(); outline(g, '#fbf6e8', 3.6);
  g.beginPath(); g.arc(60 + lx, 58, 20, 0, 7); outline(g, '#3a7be2', 3); g.beginPath(); g.arc(61 + lx, 58, 9, 0, 7); g.fillStyle = INK; g.fill();
  g.beginPath(); g.arc(66 + lx, 51, 4, 0, 7); g.fillStyle = '#fff'; g.fill();
});
registerIcon('cup', (g, o) => { // a goblet of iced water
  const t = o.t || 0;
  g.beginPath(); g.moveTo(22, 20); g.lineTo(78, 20); g.quadraticCurveTo(78, 62, 50, 66); g.quadraticCurveTo(22, 62, 22, 20); g.closePath(); outline(g, '#e9f6ff', 3.4);
  g.beginPath(); g.moveTo(25, 30); g.lineTo(75, 30); g.quadraticCurveTo(74, 60, 50, 63); g.quadraticCurveTo(26, 60, 25, 30); g.closePath(); g.fillStyle = 'rgba(120,190,240,0.85)'; g.fill();
  for (const [x, y, r] of [[38, 26, 0.3], [58, 24, -0.25], [48, 36, 0.1]]) { g.save(); g.translate(x, y + Math.sin(t * 2 + x) * 1.4); g.rotate(r); g.beginPath(); g.roundRect(-9, -9, 18, 18, 3); outline(g, 'rgba(235,250,255,0.95)', 2.2); g.beginPath(); g.moveTo(-5, -4); g.lineTo(0, -6); g.lineWidth = 2; g.strokeStyle = '#fff'; g.stroke(); g.restore(); }
  g.beginPath(); g.moveTo(50, 66); g.lineTo(50, 86); g.lineWidth = 7; g.strokeStyle = INK; g.stroke(); g.lineWidth = 3.6; g.strokeStyle = '#e9f6ff'; g.stroke();
  g.beginPath(); g.ellipse(50, 90, 22, 6, 0, 0, 7); outline(g, '#e9f6ff', 3);
  for (const [x, y, ph] of [[12, 16, 0], [88, 30, 1.7], [82, 8, 3.1]]) { const s = 0.5 + 0.5 * Math.sin(t * 5 + ph); g.save(); g.translate(x, y); g.scale(0.4 + s * 0.6, 0.4 + s * 0.6); g.beginPath(); for (let k = 0; k < 8; k++) { const r = k % 2 ? 3 : 10; const a = k / 8 * Math.PI * 2; g.lineTo(Math.cos(a) * r, Math.sin(a) * r); } g.closePath(); g.fillStyle = '#fff'; g.fill(); g.restore(); }
});
registerIcon('hothelmet', (g, o) => { // a metal helmet with heat lines and sweat (the final gag)
  const t = o.t || 0; const gl = 0.5 + 0.5 * Math.sin(t * 6);
  g.beginPath(); g.arc(50, 64, 42, 0, 7); g.fillStyle = `rgba(255,120,30,${0.22 + gl * 0.18})`; g.fill();
  g.save(); g.translate(0, 8); drawIcon(g, 'helmet', 50, 100, 100, { team: o.team, t }); g.restore();
  for (const [x, ph] of [[26, 0], [50, 1.3], [74, 2.4]]) { g.beginPath(); for (let k = 0; k <= 10; k++) { const y = 12 - k * 3.2 - ((t * 20 + ph * 9) % 14); const xx = x + Math.sin(k * 0.9 + t * 7 + ph) * 4; k ? g.lineTo(xx, y) : g.moveTo(xx, y); } stroke2(g, 3.2, '#ff6a2a'); }
  const u = (t * 1.3) % 1; for (const [x, y] of [[92, 56], [8, 62]]) drop(g, x, y + u * 12, 0.7);
});
registerIcon('hourglass', (g, o) => {
  const t = o.t || 0; const u = (t * 0.45) % 1;
  g.beginPath(); g.moveTo(24, 8); g.lineTo(76, 8); g.lineTo(54, 50); g.lineTo(76, 92); g.lineTo(24, 92); g.lineTo(46, 50); g.closePath(); outline(g, 'rgba(235,245,250,0.9)', 3.4);
  g.beginPath(); g.moveTo(30, 14); g.lineTo(70, 14); g.lineTo(50 + (1 - (1 - u) * 0.9) * 0, 48 - 0); g.closePath(); g.fillStyle = `rgba(230,180,70,${1 - u * 0.8})`; g.fill();
  g.beginPath(); g.moveTo(50, 50); g.lineTo(50, 86); g.lineWidth = 2; g.strokeStyle = '#e6b446'; g.stroke();
  g.beginPath(); g.moveTo(50 - 8 - u * 14, 90); g.lineTo(50 + 8 + u * 14, 90); g.lineTo(50, 90 - 8 - u * 22); g.closePath(); g.fillStyle = '#e6b446'; g.fill();
  for (const y of [4, 96]) { g.beginPath(); g.roundRect(18, y - 4, 64, 8, 3); outline(g, '#8a5a30', 2.6); }
});
registerIcon('twinpeaks', (g, o) => { // two hills side by side: the Horns
  g.beginPath(); g.moveTo(2, 94); g.lineTo(28, 30); g.lineTo(52, 94); g.closePath(); outline(g, '#b49360', 3.4);
  g.beginPath(); g.moveTo(48, 94); g.lineTo(74, 30); g.lineTo(98, 94); g.closePath(); outline(g, '#a58652', 3.4);
  g.beginPath(); g.moveTo(28, 30); g.lineTo(21, 50); g.lineTo(28, 46); g.lineTo(34, 52); g.closePath(); outline(g, '#efe0b8', 2.2);
  g.beginPath(); g.moveTo(74, 30); g.lineTo(67, 50); g.lineTo(74, 46); g.lineTo(80, 52); g.closePath(); outline(g, '#efe0b8', 2.2);
});
registerIcon('drop', (g, o) => { const k = 1 + 0.06 * Math.sin((o.t || 0) * 5); g.save(); g.translate(50, 60); g.scale(k, k); g.translate(-50, -60);
  g.beginPath(); g.moveTo(50, 6); g.bezierCurveTo(86, 48, 84, 90, 50, 92); g.bezierCurveTo(16, 90, 14, 48, 50, 6); g.closePath(); outline(g, '#6cb4ee', 3.6);
  g.beginPath(); g.moveTo(32, 62); g.quadraticCurveTo(32, 76, 42, 80); g.lineWidth = 4; g.strokeStyle = 'rgba(255,255,255,0.75)'; g.stroke(); g.restore(); });
registerIcon('sweat', (g, o) => {
  g.beginPath(); g.arc(50, 56, 38, 0, 7); outline(g, '#ffd98a', 3.6);
  for (const s of [-1, 1]) { g.beginPath(); g.arc(50 + s * 14, 48, 4, 0, 7); g.fillStyle = INK; g.fill(); }
  g.beginPath(); g.moveTo(34, 76); g.quadraticCurveTo(50, 66, 66, 76); g.lineWidth = 4; g.strokeStyle = INK; g.stroke();
  const u = ((o.t || 0) * 1.4) % 1; for (const [x, y] of [[84, 30], [14, 34]]) { g.beginPath(); g.moveTo(x, y + u * 12); g.quadraticCurveTo(x + 8, y + 14 + u * 12, x, y + 18 + u * 12); g.quadraticCurveTo(x - 8, y + 14 + u * 12, x, y + u * 12); outline(g, '#8fc4ee', 2.4); }
});
registerIcon('tent2', (g, o) => { // King Guy's red tent: bigger, striped, a pennant
  const col = rgb(o.team || [0.8, 0.12, 0.12]); g.beginPath(); g.moveTo(2, 94); g.lineTo(50, 22); g.lineTo(98, 94); g.closePath(); outline(g, col, 3.6);
  for (const x of [20, 36, 64, 80]) { g.beginPath(); g.moveTo(50, 22); g.lineTo(x, 94); g.lineWidth = 2; g.strokeStyle = 'rgba(255,230,200,0.55)'; g.stroke(); }
  g.beginPath(); g.moveTo(40, 94); g.lineTo(50, 52); g.lineTo(60, 94); g.closePath(); outline(g, '#3a0f0c', 2.6);
  g.beginPath(); g.moveTo(50, 22); g.lineTo(50, 4); g.lineWidth = 3; g.strokeStyle = INK; g.stroke(); g.beginPath(); g.moveTo(50, 4); g.lineTo(72, 10 + Math.sin((o.t || 0) * 6) * 1.6); g.lineTo(50, 17); g.closePath(); outline(g, '#ffd23f', 2);
});
