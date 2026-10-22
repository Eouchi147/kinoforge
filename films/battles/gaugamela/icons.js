// Gaugamela: icons drawn in code, registered with the Battle Map engine (100x100 box, origin bottom-centre, o.t = seconds since the icon popped in).
// o.fill picks a variant: chariot 'fast' | 'royal' | 'royalfast' | 'broken'; wheel: none; strike: the text to cross out.
import { registerIcon } from '/films/lib/battlemap/icons.js';
const INK = '#2a190e';
const outline = (g, fill, lw = 3.2) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; if (fill) { g.fillStyle = fill; g.fill(); } g.stroke(); };
const col = (c, k = 1) => c ? `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})` : '#2a5cc8';

// a wheel with curved blades sticking out; spins with time
function wheel(g, cx, cy, r, ang, blades = 6) {
  g.save(); g.translate(cx, cy); g.rotate(ang);
  for (let i = 0; i < blades; i++) { // the blades (grey, with a bright edge)
    g.save(); g.rotate(i / blades * Math.PI * 2);
    g.beginPath(); g.moveTo(r * 0.82, -r * 0.16); g.quadraticCurveTo(r * 1.5, -r * 0.1, r * 1.75, r * 0.46); g.quadraticCurveTo(r * 1.2, r * 0.18, r * 0.82, r * 0.2); g.closePath(); outline(g, '#cfd4dc', 2.6);
    g.beginPath(); g.moveTo(r * 0.96, -r * 0.08); g.quadraticCurveTo(r * 1.4, -r * 0.04, r * 1.55, r * 0.34); g.lineWidth = 1.4; g.strokeStyle = '#ffffff'; g.stroke();
    g.restore();
  }
  g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.fillStyle = '#e1c283'; g.fill(); g.lineWidth = r * 0.2; g.strokeStyle = '#8a5a2a'; g.stroke(); g.lineWidth = 2.6; g.strokeStyle = INK; g.beginPath(); g.arc(0, 0, r * 1.1, 0, Math.PI * 2); g.stroke();
  g.lineWidth = r * 0.1; g.strokeStyle = '#8a5a2a'; for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 + Math.PI / 6; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(a) * r * 0.92, Math.sin(a) * r * 0.92); g.stroke(); }
  g.beginPath(); g.arc(0, 0, r * 0.2, 0, Math.PI * 2); outline(g, '#5a3a1a', 2.4);
  g.restore();
}
function speedLines(g, x0, y0, t, n = 4) { g.lineCap = 'round'; for (let i = 0; i < n; i++) { const y = y0 + i * 9; const u = (((t || 0) * 3.2 + i * 0.37) % 1 + 1) % 1; const L = 20 + (i % 2) * 12; g.beginPath(); g.moveTo(x0 - u * 14, y); g.lineTo(x0 - u * 14 - L, y); g.lineWidth = 4.4; g.strokeStyle = INK; g.stroke(); g.lineWidth = 2.2; g.strokeStyle = '#fff6dc'; g.stroke(); } }

registerIcon('chariot', (g, o) => {
  const v = o.fill || ''; const royal = v.startsWith('royal'); const fast = v.endsWith('fast') || v === 'fast'; const broken = v === 'broken'; const t = o.t || 0;
  const team = royal ? [0.95, 0.74, 0.22] : (o.team || [0.16, 0.38, 0.88]); const tc = col(team);
  g.save(); g.translate(-8, 0);
  if (broken) { g.translate(34, 92); g.rotate(-0.28); g.translate(-34, -92); }
  const gallop = Math.sin(t * (fast ? 22 : 9));
  // horse (facing right)
  g.save(); g.translate(0, -Math.abs(gallop) * (fast ? 3 : 1.5));
  for (const [lx, ph] of [[74, 0], [84, Math.PI], [64, Math.PI * 0.5], [90, Math.PI * 1.5]]) { const sw = broken ? 0 : Math.sin(t * (fast ? 22 : 9) + ph) * 7; g.beginPath(); g.moveTo(lx, 62); g.lineTo(lx + sw, 90); g.lineWidth = 5; g.lineCap = 'round'; g.strokeStyle = INK; g.stroke(); g.lineWidth = 2.6; g.strokeStyle = '#7a5230'; g.stroke(); }
  g.beginPath(); g.moveTo(56, 52); g.quadraticCurveTo(46, 58, 50, 72); g.lineWidth = 5; g.lineCap = 'round'; g.strokeStyle = INK; g.stroke(); g.lineWidth = 2.6; g.strokeStyle = '#4a2a10'; g.stroke();
  g.beginPath(); g.ellipse(76, 56, 22, 11, -0.05, 0, Math.PI * 2); outline(g, '#9a6a3a', 3);
  g.beginPath(); g.moveTo(88, 52); g.quadraticCurveTo(95, 38, 95, 24); g.lineTo(108, 27); g.quadraticCurveTo(104, 44, 97, 62); g.closePath(); outline(g, '#9a6a3a', 3);
  g.save(); g.translate(104, 26); g.rotate(0.6); g.beginPath(); g.ellipse(2, 0, 12, 6, 0, 0, Math.PI * 2); outline(g, '#9a6a3a', 3); g.beginPath(); g.arc(-1, -1.5, 1.8, 0, 7); g.fillStyle = INK; g.fill(); g.restore();
  g.beginPath(); g.moveTo(94, 22); g.lineTo(96, 12); g.lineTo(101, 21); g.closePath(); outline(g, '#9a6a3a', 2.4);
  g.beginPath(); g.moveTo(90, 48); g.quadraticCurveTo(94, 36, 94, 22); g.lineWidth = 4.5; g.strokeStyle = '#4a2a10'; g.stroke();
  g.restore();
  // pole and cart
  g.beginPath(); g.moveTo(44, 62); g.lineTo(64, 60); g.lineWidth = 4; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.moveTo(10, 40); g.lineTo(52, 40); g.lineTo(54, 66); g.lineTo(12, 68); g.closePath(); outline(g, tc, 3.2);
  g.beginPath(); g.moveTo(12, 52); g.lineTo(53, 52); g.lineWidth = 2.4; g.strokeStyle = 'rgba(255,255,255,0.7)'; g.stroke();
  // driver
  g.beginPath(); g.arc(32, 28, 8, 0, 7); outline(g, '#e9c79a', 2.6); g.beginPath(); g.arc(32, 25, 8.6, Math.PI, 0); g.closePath(); outline(g, royal ? '#f4cf63' : '#cfd4dc', 2.6);
  if (royal) { g.beginPath(); g.moveTo(22, 17); g.lineTo(24, 6); g.lineTo(28, 13); g.lineTo(32, 3); g.lineTo(36, 13); g.lineTo(40, 6); g.lineTo(42, 17); g.closePath(); outline(g, '#ffd23f', 2.6); }
  // the scythed wheel
  if (broken) { wheel(g, 78, 90, 15, t * 5 + 1, 6); } else wheel(g, 30, 74, 17, t * (fast ? 14 : 5), 6);
  g.restore();
  if (fast) speedLines(g, 8, 44, t);
  if (broken) { for (const [x, y, r] of [[20, 20, 6], [52, 14, 5], [88, 40, 6]]) { g.save(); g.translate(x, y); g.rotate(t * 3); g.beginPath(); for (let k = 0; k < 8; k++) { const rr = k % 2 ? r * 0.45 : r; const a = k / 8 * Math.PI * 2; g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); } g.closePath(); outline(g, '#ffd23f', 1.8); g.restore(); } }
});
registerIcon('wheel', (g, o) => { const t = o.t || 0; g.save(); g.translate(0, -2); wheel(g, 50, 58, 30, t * 1.4, 8);
  for (let i = 0; i < 4; i++) { const a = t * 2 + i * 1.6; const x = 50 + Math.cos(a) * 52, y = 58 + Math.sin(a) * 52; g.save(); g.translate(x, y); g.rotate(a); g.beginPath(); for (let k = 0; k < 8; k++) { const r = k % 2 ? 2 : 7; const b = k / 8 * Math.PI * 2; g.lineTo(Math.cos(b) * r, Math.sin(b) * r); } g.closePath(); g.fillStyle = '#fffbe0'; g.fill(); g.restore(); }
  g.restore(); });
registerIcon('roller', (g, o) => { const t = o.t || 0; const rot = t * 5;
  g.beginPath(); g.moveTo(30, 36); g.lineTo(84, 34); g.lineWidth = 6; g.lineCap = 'round'; g.strokeStyle = INK; g.stroke(); g.lineWidth = 3; g.strokeStyle = '#a8743a'; g.stroke();
  g.beginPath(); g.moveTo(84, 34); g.lineTo(98, 12); g.lineWidth = 6; g.strokeStyle = INK; g.stroke(); g.lineWidth = 3; g.strokeStyle = '#a8743a'; g.stroke();
  g.beginPath(); g.roundRect(10, 40, 46, 44, 12); outline(g, '#b9b4a6', 3.4);
  g.save(); g.beginPath(); g.roundRect(10, 40, 46, 44, 12); g.clip(); g.strokeStyle = 'rgba(70,60,45,0.55)'; g.lineWidth = 3; for (let k = 0; k < 4; k++) { const y = 40 + ((k * 14 + rot * 9) % 56); g.beginPath(); g.moveTo(10, y); g.lineTo(56, y); g.stroke(); } g.restore();
  g.beginPath(); g.ellipse(33, 62, 8, 22, 0, 0, 7); g.fillStyle = 'rgba(255,255,255,0.35)'; g.fill();
  g.beginPath(); g.ellipse(33, 90, 30, 6, 0, 0, 7); g.fillStyle = 'rgba(255,250,230,0.7)'; g.fill(); });
registerIcon('strike', (g, o) => { // a parchment tag with a silly number, crossed out
  const txt = o.fill || '1,000,000?'; const t = o.t || 0; g.save(); g.translate(50, 56); g.rotate(-0.05 + Math.sin(t * 3) * 0.02); g.translate(-50, -56);
  g.beginPath(); g.moveTo(-38, 24); g.quadraticCurveTo(50, 16, 138, 24); g.lineTo(138, 88); g.quadraticCurveTo(50, 96, -38, 88); g.closePath(); outline(g, '#f3e3b8', 4);
  g.font = '800 27px Cinzel, serif'; g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.fillStyle = '#3a2412'; g.fillText(txt, 50, 69);
  const u = Math.min(1, Math.max(0, (t - 0.45) / 0.3)); g.beginPath(); g.moveTo(-30, 66); g.lineTo(-30 + 160 * u, 54 + 12 * (1 - u) ); g.lineCap = 'round'; g.lineWidth = 13; g.strokeStyle = INK; g.stroke(); g.lineWidth = 8; g.strokeStyle = '#e0302a'; g.stroke();
  g.restore(); });
registerIcon('spiral', (g, o) => { const t = o.t || 0; g.beginPath(); g.arc(50, 56, 40, 0, 7); outline(g, '#fff0b8', 3.4); g.save(); g.translate(50, 56); g.rotate(t * 3); g.beginPath(); for (let k = 0; k < 90; k++) { const a = k / 90 * Math.PI * 6; const r = 3 + k * 0.38; g.lineTo(Math.cos(a) * r, Math.sin(a) * r); } g.lineWidth = 4.5; g.lineCap = 'round'; g.strokeStyle = INK; g.stroke(); g.restore(); });
registerIcon('bulb', (g, o) => { const t = o.t || 0; for (let i = 0; i < 8; i++) { const a = -Math.PI / 2 + (i - 3.5) * 0.42; const r0 = 40 + Math.sin(t * 9 + i) * 2; g.beginPath(); g.moveTo(50 + Math.cos(a) * r0, 44 + Math.sin(a) * r0); g.lineTo(50 + Math.cos(a) * (r0 + 11), 44 + Math.sin(a) * (r0 + 11)); g.lineWidth = 4; g.lineCap = 'round'; g.strokeStyle = INK; g.stroke(); g.lineWidth = 2; g.strokeStyle = '#ffd23f'; g.stroke(); }
  g.beginPath(); g.arc(50, 44, 25, 0, 7); outline(g, '#ffe680', 3.4); g.beginPath(); g.roundRect(38, 66, 24, 16, 4); outline(g, '#b9b4a6', 3); g.beginPath(); g.moveTo(40, 82); g.lineTo(50, 94); g.lineTo(60, 82); g.closePath(); outline(g, '#8a8f98', 2.6);
  g.beginPath(); g.moveTo(42, 50); g.lineTo(47, 40); g.lineTo(53, 50); g.lineTo(58, 40); g.lineWidth = 3; g.strokeStyle = '#c98a1a'; g.stroke(); });
registerIcon('sweat', (g, o) => { const t = o.t || 0;
  g.beginPath(); g.arc(50, 56, 38, 0, 7); outline(g, '#ffd98a', 3.6);
  for (const s of [-1, 1]) { g.beginPath(); g.arc(50 + s * 14, 48, 4, 0, 7); g.fillStyle = INK; g.fill(); }
  g.beginPath(); g.moveTo(34, 76); g.quadraticCurveTo(50, 66, 66, 76); g.lineWidth = 4; g.strokeStyle = INK; g.stroke();
  const u = (t * 1.4) % 1; for (const [x, y] of [[84, 30], [14, 34]]) { g.beginPath(); g.moveTo(x, y + u * 12); g.quadraticCurveTo(x + 8, y + 14 + u * 12, x, y + 18 + u * 12); g.quadraticCurveTo(x - 8, y + 14 + u * 12, x, y + u * 12); outline(g, '#8fc4ee', 2.4); } });
registerIcon('calendar', (g, o) => { const t = o.t || 0; g.beginPath(); g.roundRect(14, 20, 72, 70, 8); outline(g, '#f6efd8', 3.6); g.beginPath(); g.roundRect(14, 20, 72, 20, [8, 8, 0, 0]); outline(g, '#d93a3a', 3.6);
  for (const x of [32, 68]) { g.beginPath(); g.moveTo(x, 12); g.lineTo(x, 28); g.lineWidth = 6; g.lineCap = 'round'; g.strokeStyle = INK; g.stroke(); }
  const flip = (t * 3) % 1; for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) { g.beginPath(); g.roundRect(20 + c * 16, 46 + r * 13, 11, 8, 2); g.fillStyle = (r * 4 + c) < Math.floor(t * 3 % 12) ? '#c8b98a' : '#8a7a5a'; g.fill(); }
  g.save(); g.translate(86, 90); g.rotate(-0.4 - flip * 0.2); g.beginPath(); g.moveTo(0, 0); g.lineTo(-24, 0); g.lineTo(-24, -24); g.closePath(); outline(g, '#fffbea', 2.4); g.restore(); });
registerIcon('clock', (g, o) => { g.beginPath(); g.arc(50, 56, 38, 0, 7); outline(g, '#f6efd8', 3.6);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; g.beginPath(); g.moveTo(50 + Math.cos(a) * 31, 56 + Math.sin(a) * 31); g.lineTo(50 + Math.cos(a) * 36, 56 + Math.sin(a) * 36); g.lineWidth = 2.4; g.strokeStyle = INK; g.stroke(); }
  const t = o.t || 0; const ha = -Math.PI / 2 + t * 0.8, ma = -Math.PI / 2 + t * 9.6;
  g.beginPath(); g.moveTo(50, 56); g.lineTo(50 + Math.cos(ha) * 17, 56 + Math.sin(ha) * 17); g.lineWidth = 5; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.moveTo(50, 56); g.lineTo(50 + Math.cos(ma) * 27, 56 + Math.sin(ma) * 27); g.lineWidth = 3.2; g.stroke(); });
registerIcon('exclaim', (g, o) => { const k = 1 + 0.06 * Math.sin((o.t || 0) * 14); g.save(); g.translate(50, 60); g.scale(k, k); g.translate(-50, -60); g.font = '800 120px Cinzel, serif'; g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.lineJoin = 'round'; g.lineWidth = 11; g.strokeStyle = INK; g.strokeText('!', 50, 96); g.fillStyle = '#ffd23f'; g.fillText('!', 50, 96); g.restore(); });
registerIcon('puff', (g, o) => { const t = o.t || 0; for (let i = 0; i < 5; i++) { const u = Math.min(1, t * 1.1 + i * 0.12); const x = 20 + i * 16 + u * 4, y = 80 - u * 14 - (i % 2) * 8; g.beginPath(); g.arc(x, y, 9 + u * 8 + (i % 2) * 3, 0, 7); g.fillStyle = `rgba(250,244,226,${0.95 - u * 0.5})`; g.fill(); g.lineWidth = 2.4; g.strokeStyle = `rgba(42,25,14,${0.8 - u * 0.4})`; g.stroke(); } });
