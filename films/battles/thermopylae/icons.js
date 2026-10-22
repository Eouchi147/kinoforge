// Thermopylae: icons drawn in code, registered with the Battle Map engine (100x100 box, origin bottom-centre, o.t = seconds since the icon popped in).
import { registerIcon, drawIcon } from '/films/lib/battlemap/icons.js';
const INK = '#2a190e';
const outline = (g, fill, lw = 3.2) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; if (fill) { g.fillStyle = fill; g.fill(); } g.stroke(); };
const text = (g, s, x, y, px, fill = '#fff3d2', lw = 0.2) => { g.font = `800 ${px}px Cinzel, serif`; g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.lineJoin = 'round'; g.lineWidth = px * lw; g.strokeStyle = INK; g.strokeText(s, x, y); g.fillStyle = fill; g.fillText(s, x, y); };

// the Great King's throne, which hops three times (fill = nothing)
registerIcon('throne', (g, o) => {
  const t = o.t || 0; let hop = 0, count = 0; for (let k = 0; k < 3; k++) { const s = 0.35 + 0.66 * k; const u = (t - s) / 0.5; if (u > 0) count = k + 1; if (u > 0 && u < 1) hop = Math.sin(Math.PI * u) * 36; }
  g.save(); g.translate(0, -hop);
  g.beginPath(); g.moveTo(24, 96); g.lineTo(24, 40); g.lineTo(76, 40); g.lineTo(76, 96); g.closePath(); outline(g, '#7a1f2a', 3.4);                // back cushion
  g.beginPath(); g.moveTo(20, 40); g.quadraticCurveTo(50, 2, 80, 40); g.lineTo(76, 44); g.lineTo(24, 44); g.closePath(); outline(g, '#f2c230', 3.4);   // arched gold back
  g.beginPath(); g.roundRect(14, 62, 72, 16, 5); outline(g, '#d99a14', 3);                                                                            // seat
  g.beginPath(); g.roundRect(30, 46, 40, 16, 4); outline(g, '#a8323f', 2.6);                                                                          // cushion
  for (const x of [14, 78]) { g.beginPath(); g.roundRect(x, 52, 8, 44, 3); outline(g, '#f2c230', 3); }                                                // arms
  g.beginPath(); g.moveTo(40, 36); g.lineTo(38, 18); g.lineTo(46, 26); g.lineTo(50, 12); g.lineTo(54, 26); g.lineTo(62, 18); g.lineTo(60, 36); g.closePath(); outline(g, '#ffd23f', 2.6); // little crown
  g.restore();
  if (count > 0) { const sc = 1 + 0.25 * Math.max(0, 1 - ((t - (0.35 + 0.66 * (count - 1))) / 0.3)); g.save(); g.translate(86, 18); g.scale(sc, sc); g.beginPath(); g.arc(0, 0, 14, 0, 7); outline(g, '#fff3d2', 3); text(g, String(count), 0, 7, 20, INK, 0); g.restore(); }
});

// a calendar page: fill = "start,stepSeconds,HEADER" (step 0 = a still page)
registerIcon('calendar', (g, o) => {
  const [s0, st, head, mx] = String(o.fill || '1,0,DAY').split(','); const t = o.t || 0; const step = parseFloat(st) || 0; const n = Math.min(mx ? parseInt(mx, 10) : 99, parseInt(s0, 10) + (step > 0 ? Math.floor(t / step) : 0));
  const sinceFlip = step > 0 ? (t % step) : 1; const live = step > 0 && parseInt(s0, 10) + Math.floor(t / step) <= (mx ? parseInt(mx, 10) : 99); const sq = live && sinceFlip < 0.14 && t >= step ? sinceFlip / 0.14 : 1;
  g.save(); g.translate(50, 100); g.scale(1, Math.max(0.15, sq)); g.translate(-50, -100);
  g.beginPath(); g.roundRect(8, 8, 84, 88, 10); outline(g, '#f6efd8', 3.6);
  g.beginPath(); g.roundRect(8, 8, 84, 28, [10, 10, 0, 0]); outline(g, '#c42a2a', 3.6);
  for (const x of [28, 72]) { g.beginPath(); g.roundRect(x - 4, 0, 8, 16, 3); outline(g, '#9b9ea6', 2.6); }
  text(g, head || 'DAY', 50, 30, 20, '#fff3d2', 0.12); text(g, String(n), 50, 82, n > 9 ? 44 : 52, INK, 0);
  g.restore();
});

// the sun, then a swarm of arrows swallows it (t = seconds since it popped in)
registerIcon('sundim', (g, o) => {
  const t = o.t || 0; const u = Math.max(0, Math.min(1, (t - 0.1) / 1.2));
  g.save(); g.translate(50, 54); g.rotate(t * 0.4); g.beginPath(); for (let i = 0; i < 20; i++) { const r = i % 2 ? 30 : 48; const a = i / 20 * Math.PI * 2; g.lineTo(Math.cos(a) * r, Math.sin(a) * r); } g.closePath(); outline(g, '#ffd23f', 3.2); g.restore();
  g.beginPath(); g.arc(50, 54, 25, 0, 7); outline(g, '#ffe58a', 3);
  if (u > 0) { g.save(); g.globalAlpha = 0.92 * u; g.beginPath(); g.arc(50, 54, 52, 0, 7); g.fillStyle = '#2a2236'; g.fill(); g.restore();
    g.lineCap = 'round'; for (let i = 0; i < 26; i++) { const ang = i * 2.399; const rr = 8 + (i * 7.3 % 40); const x = 50 + Math.cos(ang) * rr * u, y = 54 + Math.sin(ang) * rr * u; g.beginPath(); g.moveTo(x - 7, y + 12); g.lineTo(x + 3, y - 8); g.lineWidth = 2.6; g.strokeStyle = '#d93a2a'; g.stroke(); g.beginPath(); g.moveTo(x + 3, y - 8); g.lineTo(x + 7, y - 2); g.moveTo(x + 3, y - 8); g.lineTo(x - 2, y - 6); g.lineWidth = 2.2; g.strokeStyle = '#f6e9c6'; g.stroke(); } }
});

// a Spartan helmet in sunglasses (fighting in the shade)
registerIcon('cool', (g, o) => {
  drawIcon(g, 'helmet', 50, 100, 100, { team: o.team });
  g.beginPath(); g.roundRect(30, 52, 22, 15, 5); outline(g, '#18141c', 2.6); g.beginPath(); g.roundRect(55, 52, 22, 15, 5); outline(g, '#18141c', 2.6);
  g.beginPath(); g.moveTo(52, 56); g.lineTo(55, 56); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.moveTo(34, 55); g.lineTo(40, 55); g.moveTo(59, 55); g.lineTo(65, 55); g.lineWidth = 2; g.strokeStyle = 'rgba(255,255,255,0.7)'; g.stroke();
});

registerIcon('moon', (g, o) => {
  const t = o.t || 0; g.beginPath(); g.arc(50, 52, 36, 0, Math.PI * 2); g.arc(64, 44, 30, 0, Math.PI * 2, true); outline(g, '#f6ecc0', 3.4);
  for (const [x, y, r, p] of [[84, 24, 6, 0], [88, 62, 4, 1.7], [18, 14, 5, 3.1]]) { const k = 0.7 + 0.3 * Math.sin(t * 3 + p); g.beginPath(); for (let i = 0; i < 8; i++) { const rr = (i % 2 ? r * 0.35 : r) * k; const a = i / 8 * Math.PI * 2; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); outline(g, '#fff6c8', 1.8); }
});

registerIcon('burn', (g, o) => { // flames and rising smoke
  const t = o.t || 0;
  for (let i = 0; i < 4; i++) { const u = ((t * 0.55 + i / 4) % 1); const y = 58 - u * 52, x = 44 + Math.sin(u * 5 + i * 2) * 10 + i * 4 - 6; g.globalAlpha = 0.9 * (1 - u); g.beginPath(); g.arc(x, y, 9 + u * 14, 0, 7); outline(g, '#6d6a70', 2.4); } g.globalAlpha = 1;
  const f = 1 + 0.08 * Math.sin(t * 11);
  g.save(); g.translate(50, 96); g.scale(f, 1 + (f - 1) * 1.6); g.translate(-50, -96);
  g.beginPath(); g.moveTo(14, 96); g.quadraticCurveTo(6, 64, 30, 40); g.quadraticCurveTo(30, 62, 40, 66); g.quadraticCurveTo(42, 34, 52, 16); g.quadraticCurveTo(66, 40, 66, 60); g.quadraticCurveTo(74, 56, 76, 46); g.quadraticCurveTo(94, 70, 86, 96); g.closePath(); outline(g, '#f2602a', 3.4);
  g.beginPath(); g.moveTo(32, 96); g.quadraticCurveTo(28, 76, 46, 58); g.quadraticCurveTo(62, 74, 68, 96); g.closePath(); outline(g, '#ffd23f', 2.6); g.restore();
});

registerIcon('bag', (g, o) => { // a bag of coins
  g.beginPath(); g.moveTo(34, 38); g.quadraticCurveTo(10, 60, 14, 82); g.quadraticCurveTo(18, 98, 50, 98); g.quadraticCurveTo(82, 98, 86, 82); g.quadraticCurveTo(90, 60, 66, 38); g.closePath(); outline(g, '#b58a4a', 3.4);
  g.beginPath(); g.moveTo(32, 40); g.quadraticCurveTo(50, 50, 68, 40); g.lineTo(72, 28); g.quadraticCurveTo(50, 36, 28, 28); g.closePath(); outline(g, '#8d6a38', 3);
  g.beginPath(); g.moveTo(36, 30); g.lineTo(64, 30); g.lineWidth = 4; g.strokeStyle = '#d33'; g.stroke();
  text(g, '$', 50, 84, 40, '#ffd23f', 0.18);
  for (const [x, y] of [[84, 90], [92, 80], [78, 98]]) { g.beginPath(); g.ellipse(x, y, 9, 4, 0, 0, 7); outline(g, '#ffd23f', 2.2); }
});

registerIcon('stone', (g, o) => { // the memorial stone
  g.beginPath(); g.moveTo(14, 98); g.lineTo(14, 40); g.quadraticCurveTo(14, 4, 50, 4); g.quadraticCurveTo(86, 4, 86, 40); g.lineTo(86, 98); g.closePath(); outline(g, '#b9b5ab', 3.8);
  g.beginPath(); g.moveTo(24, 98); g.lineTo(24, 42); g.quadraticCurveTo(24, 14, 50, 14); g.quadraticCurveTo(76, 14, 76, 42); g.lineTo(76, 98); g.closePath(); g.lineWidth = 1.6; g.strokeStyle = 'rgba(60,50,40,0.55)'; g.stroke();
  for (const y of [38, 50, 62, 74]) { g.beginPath(); g.moveTo(32, y); g.lineTo(68 - (y % 3) * 4, y); g.lineWidth = 3.2; g.strokeStyle = 'rgba(50,42,34,0.7)'; g.stroke(); }
  g.beginPath(); g.moveTo(34, 98); g.quadraticCurveTo(50, 90, 66, 98); g.lineWidth = 3; g.strokeStyle = '#5f8f3c'; g.stroke();
});

registerIcon('peak', (g, o) => { // a steep mountain
  g.beginPath(); g.moveTo(2, 96); g.lineTo(34, 30); g.lineTo(46, 46); g.lineTo(66, 8); g.lineTo(98, 96); g.closePath(); outline(g, '#9a8f82', 3.6);
  g.beginPath(); g.moveTo(66, 8); g.lineTo(98, 96); g.lineTo(76, 96); g.lineTo(70, 60); g.lineTo(62, 44); g.closePath(); g.fillStyle = 'rgba(40,30,24,0.4)'; g.fill();
  g.beginPath(); g.moveTo(66, 8); g.lineTo(56, 30); g.lineTo(62, 26); g.lineTo(68, 34); g.lineTo(74, 24); g.lineTo(78, 30); g.closePath(); outline(g, '#fffaf0', 2.4);
});

registerIcon('wave', (g, o) => { // the sea
  const t = o.t || 0; for (let r = 0; r < 3; r++) { const y = 40 + r * 22; const sw = Math.sin(t * 2.4 + r) * 4; g.beginPath(); g.moveTo(4, y); for (let k = 0; k < 4; k++) g.quadraticCurveTo(16 + k * 24 + sw, y - 16, 28 + k * 24, y); g.lineWidth = 9; g.strokeStyle = INK; g.stroke(); g.lineWidth = 5; g.strokeStyle = r % 2 ? '#8fc4ee' : '#5fa0dc'; g.stroke(); }
});

registerIcon('hourglass', (g, o) => {
  const t = o.t || 0; const u = (t * 0.5) % 1;
  g.beginPath(); g.moveTo(22, 8); g.lineTo(78, 8); g.quadraticCurveTo(78, 44, 54, 52); g.quadraticCurveTo(78, 60, 78, 94); g.lineTo(22, 94); g.quadraticCurveTo(22, 60, 46, 52); g.quadraticCurveTo(22, 44, 22, 8); g.closePath(); outline(g, 'rgba(235,245,250,0.9)', 3.6);
  g.beginPath(); g.moveTo(30, 14 + u * 20); g.lineTo(70, 14 + u * 20); g.lineTo(52, 48); g.closePath(); g.fillStyle = '#f2c230'; g.fill();
  g.beginPath(); g.moveTo(50, 52); g.lineTo(50, 92 - u * 20); g.lineWidth = 2.4; g.strokeStyle = '#f2c230'; g.stroke();
  g.beginPath(); g.moveTo(26, 94); g.quadraticCurveTo(50, 62 + (1 - u) * 14, 74, 94); g.closePath(); g.fillStyle = '#f2c230'; g.fill();
  for (const y of [4, 98]) { g.beginPath(); g.roundRect(16, y - 4, 68, 9, 3); outline(g, '#8a5a30', 3); }
});

registerIcon('shout', (g, o) => { // an exclamation mark in a burst
  const k = 1 + 0.06 * Math.sin((o.t || 0) * 12); g.save(); g.translate(50, 56); g.scale(k, k); g.translate(-50, -56);
  g.beginPath(); const n = 10; for (let i = 0; i < n * 2; i++) { const r = i % 2 ? 32 : 48; const a = i / (n * 2) * Math.PI * 2; i ? g.lineTo(50 + Math.cos(a) * r, 52 + Math.sin(a) * r) : g.moveTo(50 + Math.cos(a) * r, 52 + Math.sin(a) * r); } g.closePath(); outline(g, '#ffd23f', 3.4);
  text(g, '!', 50, 76, 70, '#c42a2a', 0.16); g.restore();
});
