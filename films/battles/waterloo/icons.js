// Waterloo: extra Battle Map icons drawn in code (100x100 box, bottom-centre origin). Registered from index.html with registerIcons().
const INK = '#2a190e';
const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
function outline(g, fill, lw = 3.2) { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; if (fill) { g.fillStyle = fill; g.fill(); } g.stroke(); }

export const WATERLOO_ICONS = {
  // Napoleon's bicorne hat, side on, with a tricolour cockade
  hat(g, o) {
    g.beginPath(); g.moveTo(4, 74); g.quadraticCurveTo(10, 52, 30, 46); g.quadraticCurveTo(50, 8, 70, 46); g.quadraticCurveTo(90, 52, 96, 74);
    g.quadraticCurveTo(70, 86, 50, 84); g.quadraticCurveTo(30, 86, 4, 74); g.closePath(); outline(g, '#2b2f4a', 3.6);
    g.beginPath(); g.moveTo(10, 66); g.quadraticCurveTo(50, 78, 90, 66); g.lineWidth = 4; g.strokeStyle = '#e8b93a'; g.stroke();
    g.beginPath(); g.moveTo(26, 36); g.quadraticCurveTo(40, 22, 50, 20); g.lineWidth = 3.4; g.strokeStyle = 'rgba(255,255,255,0.38)'; g.stroke();
    g.beginPath(); g.arc(50, 58, 11, 0, 7); outline(g, '#e23a3a', 2.6); g.beginPath(); g.arc(50, 58, 7, 0, 7); g.fillStyle = '#f6f2e6'; g.fill(); g.beginPath(); g.arc(50, 58, 3.2, 0, 7); g.fillStyle = '#2f5fd0'; g.fill();
  },
  // a farmhouse: stone walls, red roof, chimney, a gate
  farm(g, o) {
    g.beginPath(); g.rect(12, 52, 76, 42); outline(g, '#e9dcb4', 3.4);
    g.beginPath(); g.moveTo(5, 56); g.lineTo(50, 16); g.lineTo(95, 56); g.closePath(); outline(g, '#b8442f', 3.6);
    g.beginPath(); g.rect(68, 22, 9, 22); outline(g, '#a39577', 2.6);
    g.beginPath(); g.moveTo(40, 94); g.lineTo(40, 70); g.quadraticCurveTo(50, 60, 60, 70); g.lineTo(60, 94); g.closePath(); outline(g, '#6b4a2a', 2.6);
    g.beginPath(); g.rect(18, 62, 12, 12); outline(g, '#6f98b8', 2.2); g.beginPath(); g.rect(70, 62, 12, 12); outline(g, '#6f98b8', 2.2);
  },
  // a clock; the hands turn with the icon's age (o.t), o.rate = turns per second of the minute hand
  clock(g, o) {
    const t = o.t || 0, rate = o.rate ?? 0.5; g.beginPath(); g.arc(50, 56, 40, 0, 7); outline(g, '#f6efd8', 4); g.beginPath(); g.arc(50, 56, 40, 0, 7); g.lineWidth = 3; g.strokeStyle = '#e8b93a'; g.stroke();
    for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2; g.beginPath(); g.moveTo(50 + Math.sin(a) * 33, 56 - Math.cos(a) * 33); g.lineTo(50 + Math.sin(a) * 38, 56 - Math.cos(a) * 38); g.lineWidth = 2.6; g.strokeStyle = INK; g.stroke(); }
    const hand = (a, l, w) => { g.beginPath(); g.moveTo(50, 56); g.lineTo(50 + Math.sin(a) * l, 56 - Math.cos(a) * l); g.lineWidth = w; g.strokeStyle = INK; g.lineCap = 'round'; g.stroke(); };
    hand(t * rate * Math.PI * 2, 30, 3.2); hand(t * rate * Math.PI * 2 / 12 + (o.start ?? 4.6), 20, 4.6); g.beginPath(); g.arc(50, 56, 3.6, 0, 7); g.fillStyle = INK; g.fill();
    g.beginPath(); g.arc(22, 14, 8, 0, 7); outline(g, '#e8b93a', 2.4); g.beginPath(); g.arc(78, 14, 8, 0, 7); outline(g, '#e8b93a', 2.4);
  },
  // a little bed with a sleeper (for the very expensive lie in)
  bed(g, o) {
    const z = Math.sin((o.t || 0) * 2.4) * 3;
    g.beginPath(); g.roundRect(6, 52, 88, 26, 4); outline(g, '#f6efd8', 3.2);
    g.beginPath(); g.roundRect(6, 66, 88, 16, 4); outline(g, '#5a82c8', 3.2);
    g.beginPath(); g.roundRect(8, 44, 28, 16, 8); outline(g, '#fff8e6', 3);
    g.beginPath(); g.rect(4, 40, 6, 52); outline(g, '#8a5a30', 3); g.beginPath(); g.rect(90, 52, 6, 40); outline(g, '#8a5a30', 3);
    g.font = '800 26px Cinzel, serif'; g.textAlign = 'center'; g.lineJoin = 'round'; g.lineWidth = 6; g.strokeStyle = INK; g.fillStyle = '#fff3d2';
    g.strokeText('Z', 62, 38 + z); g.fillText('Z', 62, 38 + z); g.font = '800 18px Cinzel, serif'; g.strokeText('z', 78, 24 - z); g.fillText('z', 78, 24 - z);
  },
  sun(g, o) {
    const t = o.t || 0; g.save(); g.translate(50, 54); g.rotate(t * 0.5); for (let k = 0; k < 12; k++) { g.rotate(Math.PI / 6); g.beginPath(); g.moveTo(-5, -30); g.lineTo(0, -46); g.lineTo(5, -30); g.closePath(); outline(g, '#ffcf3f', 2.6); } g.restore();
    g.beginPath(); g.arc(50, 54, 28, 0, 7); outline(g, '#ffd84d', 3.6); g.beginPath(); g.arc(42, 46, 8, 0, 7); g.fillStyle = 'rgba(255,255,255,0.5)'; g.fill();
  },
  // a rain cloud with falling drops (animated by o.t)
  rain(g, o) {
    const t = o.t || 0; g.beginPath(); g.moveTo(22, 52); g.bezierCurveTo(4, 52, 6, 30, 26, 30); g.bezierCurveTo(28, 12, 58, 8, 64, 28); g.bezierCurveTo(88, 22, 96, 50, 78, 52); g.closePath(); outline(g, '#b9c3d0', 3.6);
    g.beginPath(); g.moveTo(24, 44); g.quadraticCurveTo(40, 38, 56, 42); g.lineWidth = 3; g.strokeStyle = 'rgba(255,255,255,0.55)'; g.stroke();
    for (let k = 0; k < 6; k++) { const u = (t * 1.6 + k * 0.37) % 1; const x = 20 + k * 12 + (k % 2) * 3, y = 58 + u * 36; g.beginPath(); g.moveTo(x, y); g.lineTo(x - 3, y + 11); g.lineWidth = 3.6; g.strokeStyle = '#3a78c8'; g.lineCap = 'round'; g.globalAlpha *= 1; g.stroke(); }
  },
  // a French cannon on its wheel
  cannon(g, o) {
    g.save(); g.translate(46, 56); g.rotate(-0.2); g.beginPath(); g.roundRect(-30, -12, 66, 22, 9); outline(g, '#4a4d56', 3.4); g.beginPath(); g.roundRect(30, -15, 14, 28, 4); outline(g, '#3a3c44', 3); g.beginPath(); g.moveTo(-26, -6); g.lineTo(18, -6); g.lineWidth = 3; g.strokeStyle = 'rgba(255,255,255,0.3)'; g.stroke(); g.restore();
    g.beginPath(); g.arc(34, 74, 20, 0, 7); outline(g, '#9a6a35', 3.6); g.beginPath(); g.arc(34, 74, 6, 0, 7); outline(g, '#6b4a2a', 2.4);
    for (let k = 0; k < 4; k++) { const a = k * Math.PI / 4; g.beginPath(); g.moveTo(34 + Math.cos(a) * 18, 74 + Math.sin(a) * 18); g.lineTo(34 - Math.cos(a) * 18, 74 - Math.sin(a) * 18); g.lineWidth = 2.4; g.strokeStyle = INK; g.stroke(); }
  },
  // a hedgehog with a back of bayonets (kids will like it)
  hedgehog(g, o) {
    const team = o.team || [0.8, 0.12, 0.12]; const col = rgb(team);
    for (let k = 0; k < 11; k++) { const a = Math.PI + (k / 10) * Math.PI; const bx = 48 + Math.cos(a) * 30, by = 74 + Math.sin(a) * 34; const ex = 48 + Math.cos(a) * 52, ey = 74 + Math.sin(a) * 60; g.beginPath(); g.moveTo(bx, by); g.lineTo(ex, ey); g.lineWidth = 4.2; g.strokeStyle = INK; g.lineCap = 'round'; g.stroke(); g.lineWidth = 2; g.strokeStyle = '#e6e6e0'; g.stroke(); }
    g.beginPath(); g.ellipse(48, 76, 34, 24, 0, Math.PI, 0); g.lineTo(82, 76); g.closePath(); outline(g, col, 3.4);
    g.beginPath(); g.ellipse(86, 78, 13, 10, 0, 0, 7); outline(g, '#d8b98c', 3); g.beginPath(); g.arc(94, 78, 3, 0, 7); g.fillStyle = INK; g.fill(); g.beginPath(); g.arc(88, 74, 2.2, 0, 7); g.fillStyle = INK; g.fill();
    for (const x of [30, 58]) { g.beginPath(); g.roundRect(x, 84, 10, 10, 3); outline(g, '#d8b98c', 2.4); }
  },
  // a small palm island with a flag
  island(g, o) {
    g.beginPath(); g.ellipse(50, 84, 44, 12, 0, 0, 7); outline(g, '#e8d398', 3); g.beginPath(); g.moveTo(52, 80); g.quadraticCurveTo(46, 50, 56, 28); g.lineWidth = 6; g.strokeStyle = INK; g.stroke(); g.lineWidth = 3.2; g.strokeStyle = '#9a6a35'; g.stroke();
    for (const [dx, dy] of [[-26, 6], [-14, -8], [18, -8], [28, 8], [2, -14]]) { g.beginPath(); g.moveTo(56, 28); g.quadraticCurveTo(56 + dx * 0.6, 28 + dy - 10, 56 + dx, 28 + dy + 6); g.lineWidth = 7; g.strokeStyle = INK; g.stroke(); g.lineWidth = 3.6; g.strokeStyle = '#3fae5a'; g.stroke(); }
  },
  // a pair of crossed muskets not needed; a plain exclamation mark for "oops"
  oops(g, o) { g.font = '800 120px Cinzel, serif'; g.textAlign = 'center'; g.lineJoin = 'round'; g.lineWidth = 11; g.strokeStyle = INK; g.strokeText('!', 50, 96); g.fillStyle = '#ffd23f'; g.fillText('!', 50, 96); },
};
