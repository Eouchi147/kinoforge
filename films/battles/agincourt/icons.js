// Agincourt: icons drawn in code, registered with the Battle Map engine (100x100 box, origin bottom-centre, o.t = seconds since the icon popped in).
import { registerIcon } from '/films/lib/battlemap/icons.js';
const INK = '#2a190e';
const outline = (g, fill, lw = 3.2) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; if (fill) { g.fillStyle = fill; g.fill(); } g.stroke(); };
const cloud = (g, fill, x = 0, y = 0, k = 1) => { g.save(); g.translate(x, y); g.scale(k, k); g.beginPath(); g.moveTo(18, 56); g.bezierCurveTo(2, 56, 2, 34, 22, 34); g.bezierCurveTo(24, 16, 52, 12, 58, 30); g.bezierCurveTo(78, 22, 94, 38, 84, 52); g.bezierCurveTo(92, 58, 86, 66, 76, 66); g.lineTo(24, 66); g.bezierCurveTo(14, 66, 10, 60, 18, 56); g.closePath(); outline(g, fill, 3.2); g.restore(); };
const drops = (g, o, n, x0, x1, y0, y1, speed = 2.2) => { for (let i = 0; i < n; i++) { const u = (((o.t || 0) * speed + i / n * 1.7) % 1 + 1) % 1; const x = x0 + (x1 - x0) * ((i * 0.618) % 1) - u * 5; const y = y0 + (y1 - y0) * u; g.beginPath(); g.moveTo(x, y); g.lineTo(x - 3.4, y + 9); g.lineWidth = 3.4; g.lineCap = 'round'; g.strokeStyle = INK; g.stroke(); g.lineWidth = 1.7; g.strokeStyle = '#8fc4ee'; g.stroke(); } };

registerIcon('rain', (g, o) => { drops(g, o, 9, 14, 90, 66, 100); cloud(g, '#9aa6b4', 0, 0, 1); });
registerIcon('thermo', (g, o) => {
  g.beginPath(); g.roundRect(40, 6, 20, 66, 10); outline(g, '#f6efd8', 3.4);
  g.beginPath(); g.arc(50, 80, 17, 0, Math.PI * 2); outline(g, '#e23a3a', 3.4);
  const lvl = 0.55 + 0.35 * (0.5 + 0.5 * Math.sin((o.t || 0) * 5)); g.beginPath(); g.roundRect(46, 74 - 62 * lvl, 8, 62 * lvl + 6, 3); g.fillStyle = '#e23a3a'; g.fill();
  for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(60, 16 + k * 12); g.lineTo(68, 16 + k * 12); g.lineWidth = 2.6; g.strokeStyle = INK; g.stroke(); }
});
registerIcon('sick', (g, o) => {
  const w = Math.sin((o.t || 0) * 6) * 2.2;
  g.beginPath(); g.arc(50, 56, 38, 0, Math.PI * 2); outline(g, '#a6cf6a', 3.6);
  g.beginPath(); g.arc(50, 60, 28, 0.15, Math.PI - 0.15); g.fillStyle = 'rgba(80,120,40,0.25)'; g.fill();
  for (const s of [-1, 1]) { g.beginPath(); g.moveTo(50 + s * 22, 44 + w * s); g.lineTo(50 + s * 10, 52); g.lineWidth = 3.6; g.strokeStyle = INK; g.stroke(); g.beginPath(); g.arc(50 + s * 15, 53, 4, 0, 7); g.fillStyle = INK; g.fill(); }
  g.beginPath(); g.moveTo(32, 76); g.quadraticCurveTo(40, 68 + w, 50, 76); g.quadraticCurveTo(60, 84 - w, 68, 76); g.lineWidth = 4; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.moveTo(84, 58); g.quadraticCurveTo(94, 70, 86, 78); g.quadraticCurveTo(80, 70, 84, 58); outline(g, '#8fc4ee', 2.2);
});
registerIcon('mud', (g, o) => {
  const k = 1 + 0.04 * Math.sin((o.t || 0) * 5);
  g.save(); g.translate(50, 70); g.scale(k, k); g.translate(-50, -70);
  g.beginPath(); const n = 14; for (let i = 0; i <= n; i++) { const a = i / n * Math.PI * 2; const r = (i % 2 ? 26 : 42) + (i % 3) * 3; const x = 50 + Math.cos(a) * r, y = 70 + Math.sin(a) * r * 0.52; if (i === 0) g.moveTo(x, y); else g.quadraticCurveTo(50 + Math.cos(a - 0.2) * (r + 8), 70 + Math.sin(a - 0.2) * (r + 8) * 0.52, x, y); }
  g.closePath(); outline(g, '#6b4a2a', 3.6);
  g.beginPath(); g.ellipse(40, 66, 12, 5, -0.2, 0, 7); g.fillStyle = '#8a6540'; g.fill();
  for (const [x, y, r] of [[30, 28, 6], [52, 14, 8], [74, 30, 5], [86, 52, 4]]) { g.beginPath(); g.arc(x, y, r, 0, 7); outline(g, '#6b4a2a', 2.6); }
  g.restore();
});
registerIcon('bush', (g, o) => {
  for (const [x, y, r, c] of [[30, 72, 22, '#4c8a3a'], [68, 72, 24, '#4c8a3a'], [50, 56, 28, '#5fa04a']]) { g.beginPath(); g.arc(x, y, r, 0, 7); outline(g, c, 3.2); }
  g.beginPath(); g.moveTo(44, 90); g.lineTo(44, 98); g.moveTo(58, 90); g.lineTo(58, 98); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
  for (const [x, y] of [[40, 52], [60, 64], [28, 74]]) { g.beginPath(); g.arc(x, y, 3, 0, 7); g.fillStyle = '#e23a3a'; g.fill(); }
});
registerIcon('quill', (g, o) => {
  g.beginPath(); g.roundRect(6, 74, 30, 24, 7); outline(g, '#2d2a3a', 3.2); g.beginPath(); g.ellipse(21, 74, 11, 4, 0, 0, 7); outline(g, '#0b0a12', 2.4);
  g.save(); g.translate(56, 50); g.rotate(0.55);
  g.beginPath(); g.moveTo(-8, 44); g.quadraticCurveTo(-34, -6, 6, -46); g.quadraticCurveTo(34, -14, 12, 34); g.quadraticCurveTo(2, 40, -8, 44); g.closePath(); outline(g, '#f3e2b8', 3.4);
  g.beginPath(); g.moveTo(-8, 44); g.quadraticCurveTo(-6, 0, 6, -44); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
  for (let k = 0; k < 5; k++) { g.beginPath(); g.moveTo(-3 + k * 0.2, 30 - k * 14); g.lineTo(-18 + k * 4, 22 - k * 13); g.lineWidth = 1.8; g.strokeStyle = 'rgba(60,40,20,0.6)'; g.stroke(); }
  g.beginPath(); g.moveTo(-8, 44); g.lineTo(-12, 58); g.lineTo(-3, 49); g.closePath(); outline(g, '#2a190e', 2);
  g.restore();
});
registerIcon('weather', (g, o) => {
  const t = o.t || 0;
  g.save(); g.translate(30, 34); g.rotate(t * 0.5); g.beginPath(); for (let i = 0; i < 16; i++) { const r = i % 2 ? 26 : 38; const a = i / 16 * Math.PI * 2; g.lineTo(Math.cos(a) * r, Math.sin(a) * r); } g.closePath(); outline(g, '#ffd23f', 3); g.restore();
  g.beginPath(); g.arc(30, 34, 17, 0, 7); outline(g, '#ffe58a', 3);
  drops(g, o, 8, 30, 92, 62, 100); cloud(g, '#a9b3bf', 8, 4, 0.96);
});
registerIcon('axe', (g, o) => {
  g.save(); g.translate(50, 54); g.rotate(-0.6);
  g.beginPath(); g.roundRect(-4, -46, 8, 96, 3); outline(g, '#9a6a35', 3);
  g.beginPath(); g.moveTo(4, -42); g.quadraticCurveTo(34, -52, 30, -18); g.quadraticCurveTo(26, -6, 4, -10); g.closePath(); outline(g, '#c9ccd2', 3.2);
  g.restore();
});
registerIcon('hammer', (g, o) => {
  const sw = Math.sin((o.t || 0) * 9) * 0.25;
  g.save(); g.translate(50, 94); g.rotate(-0.5 + sw);
  g.beginPath(); g.roundRect(-4, -70, 8, 72, 3); outline(g, '#9a6a35', 3);
  g.beginPath(); g.roundRect(-22, -92, 44, 24, 5); outline(g, '#9b9ea6', 3.4);
  g.restore();
});
registerIcon('clock', (g, o) => {
  g.beginPath(); g.arc(50, 56, 38, 0, 7); outline(g, '#f6efd8', 3.6);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; g.beginPath(); g.moveTo(50 + Math.cos(a) * 31, 56 + Math.sin(a) * 31); g.lineTo(50 + Math.cos(a) * 36, 56 + Math.sin(a) * 36); g.lineWidth = 2.4; g.strokeStyle = INK; g.stroke(); }
  const t = o.t || 0; const ha = -Math.PI / 2 + t * 0.8, ma = -Math.PI / 2 + t * 9.6;
  g.beginPath(); g.moveTo(50, 56); g.lineTo(50 + Math.cos(ha) * 17, 56 + Math.sin(ha) * 17); g.lineWidth = 5; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.moveTo(50, 56); g.lineTo(50 + Math.cos(ma) * 27, 56 + Math.sin(ma) * 27); g.lineWidth = 3.2; g.stroke();
});
registerIcon('sweat', (g, o) => {
  g.beginPath(); g.arc(50, 56, 38, 0, 7); outline(g, '#ffd98a', 3.6);
  for (const s of [-1, 1]) { g.beginPath(); g.arc(50 + s * 14, 48, 4, 0, 7); g.fillStyle = INK; g.fill(); }
  g.beginPath(); g.moveTo(34, 76); g.quadraticCurveTo(50, 66, 66, 76); g.lineWidth = 4; g.strokeStyle = INK; g.stroke();
  const u = ((o.t || 0) * 1.4) % 1; for (const [x, y] of [[84, 30], [14, 34]]) { g.beginPath(); g.moveTo(x, y + u * 12); g.quadraticCurveTo(x + 8, y + 14 + u * 12, x, y + 18 + u * 12); g.quadraticCurveTo(x - 8, y + 14 + u * 12, x, y + u * 12); outline(g, '#8fc4ee', 2.4); }
});
registerIcon('fall', (g, o) => { // a bow tumbling down (dropped)
  const u = Math.min(1, (o.t || 0) / 0.8); g.save(); g.translate(50, 30 + u * u * 60); g.rotate(u * 2.4); g.translate(-30, -50);
  g.beginPath(); g.arc(30, 50, 44, -1.15, 1.15); g.lineWidth = 6; g.strokeStyle = INK; g.stroke(); g.lineWidth = 3.4; g.strokeStyle = '#9a6a35'; g.stroke();
  const a = 1.15; const x = 30 + 44 * Math.cos(a), y1 = 50 - 44 * Math.sin(a), y2 = 50 + 44 * Math.sin(a); g.beginPath(); g.moveTo(x, y1); g.lineTo(x, y2); g.lineWidth = 1.8; g.strokeStyle = INK; g.stroke(); g.restore();
});
