// Ain Jalut: icons drawn in code, registered with the Battle Map engine (100x100 box, origin bottom-centre, o.t = seconds since the icon popped in).
import { registerIcon } from '/films/lib/battlemap/icons.js';
const INK = '#2a190e';
const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const outline = (g, fill, lw = 3.2) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = lw; g.strokeStyle = INK; if (fill) { g.fillStyle = fill; g.fill(); } g.stroke(); };

// a rolled letter with a wax seal in the sender's colour (o.team); fill:'censor' = the reply, with a black bar scribbled over the writing
const scroll = (g, o) => {
  const seal = o.team ? rgb(o.team) : '#c0392b'; const bob = Math.sin((o.t || 0) * 4) * 1.2; g.save(); g.translate(0, bob);
  g.beginPath(); g.moveTo(14, 20); g.lineTo(86, 20); g.lineTo(86, 76); g.lineTo(14, 76); g.closePath(); outline(g, '#f3e6c0', 3.4);
  for (const y of [20, 76]) { g.beginPath(); g.roundRect(8, y - 8, 84, 16, 8); outline(g, '#e3cd96', 3.2); g.beginPath(); g.ellipse(10, y, 4, 7, 0, 0, 7); outline(g, '#c9ad6a', 2); g.beginPath(); g.ellipse(90, y, 4, 7, 0, 0, 7); outline(g, '#c9ad6a', 2); }
  if (o.fill === 'censor') {
    for (const [y, w] of [[34, 56], [44, 46], [54, 60]]) { g.beginPath(); g.moveTo(22, y); g.lineTo(22 + w * 0.5, y); g.lineWidth = 3; g.strokeStyle = 'rgba(60,40,20,0.55)'; g.stroke(); }
    g.beginPath(); g.roundRect(18, 38, 64, 17, 3); g.fillStyle = '#16100c'; g.fill();
    g.beginPath(); g.moveTo(24, 46); for (let k = 0; k < 6; k++) g.lineTo(24 + k * 10 + 5, 42 + (k % 2) * 8); g.lineWidth = 2.4; g.strokeStyle = '#f3e6c0'; g.stroke();
    g.font = '800 14px Cinzel, serif'; g.textAlign = 'center'; g.fillStyle = '#16100c'; g.fillText('#$%&!', 50, 68);
  } else {
    for (const [y, w] of [[34, 56], [44, 44], [54, 56], [64, 34]]) { g.beginPath(); g.moveTo(22, y); g.lineTo(22 + w, y); g.lineWidth = 3.4; g.strokeStyle = 'rgba(60,40,20,0.7)'; g.stroke(); }
    g.beginPath(); g.arc(70, 64, 10, 0, 7); outline(g, seal, 2.8); g.beginPath(); g.arc(70, 64, 4.4, 0, 7); g.lineWidth = 2; g.strokeStyle = 'rgba(255,255,255,0.55)'; g.stroke();
  }
  g.restore();
};
registerIcon('scroll', scroll);

registerIcon('spring', (g, o) => { // a spring: rocks, bubbling water, ripples
  const t = o.t || 0;
  g.beginPath(); g.ellipse(50, 80, 42, 15, 0, 0, 7); outline(g, '#8d8478', 3.4);
  g.beginPath(); g.ellipse(50, 79, 33, 10, 0, 0, 7); outline(g, '#58b6e8', 3);
  for (let k = 0; k < 2; k++) { const u = ((t * 0.9 + k * 0.5) % 1); g.beginPath(); g.ellipse(50, 79, 8 + u * 22, 2.5 + u * 6, 0, 0, 7); g.lineWidth = 2; g.strokeStyle = `rgba(255,255,255,${0.9 - u * 0.9})`; g.stroke(); }
  const h = 8 + 4 * Math.sin(t * 6); g.beginPath(); g.moveTo(50, 20 - h * 0.2); g.bezierCurveTo(68, 44, 72, 62, 50, 76 - 0); g.bezierCurveTo(28, 62, 32, 44, 50, 20 - h * 0.2); g.closePath(); outline(g, '#6cc4f2', 3.4);
  g.beginPath(); g.moveTo(40, 50); g.quadraticCurveTo(42, 40, 48, 36); g.lineWidth = 3.4; g.strokeStyle = 'rgba(255,255,255,0.75)'; g.stroke();
  for (const [x, y, r] of [[30, 66, 6], [74, 70, 5], [22, 82, 7], [80, 84, 6]]) { g.beginPath(); g.arc(x, y, r, 0, 7); outline(g, '#a39a8b', 2.6); }
});

registerIcon('hat', (g, o) => { // a conjuror's hat with a star: "a trick"
  const t = o.t || 0; g.beginPath(); g.ellipse(50, 84, 42, 11, 0, 0, 7); outline(g, '#2d2540', 3.4);
  g.beginPath(); g.moveTo(26, 80); g.lineTo(30, 30); g.quadraticCurveTo(50, 22, 70, 30); g.lineTo(74, 80); g.quadraticCurveTo(50, 90, 26, 80); g.closePath(); outline(g, '#40345c', 3.4);
  g.beginPath(); g.moveTo(27, 70); g.quadraticCurveTo(50, 80, 73, 70); g.lineTo(73, 62); g.quadraticCurveTo(50, 72, 27, 62); g.closePath(); outline(g, '#c0392b', 2.6);
  for (const [x, y, s, ph] of [[22, 28, 1, 0], [80, 22, 1.2, 1.4], [62, 8, 0.9, 2.6]]) { const k = 0.75 + 0.25 * Math.sin(t * 6 + ph); g.save(); g.translate(x, y); g.scale(s * k, s * k); g.beginPath(); for (let i = 0; i < 8; i++) { const r = i % 2 ? 3 : 9; const a = -Math.PI / 2 + i / 8 * Math.PI * 2; i ? g.lineTo(Math.cos(a) * r, Math.sin(a) * r) : g.moveTo(Math.cos(a) * r, Math.sin(a) * r); } g.closePath(); outline(g, '#ffd23f', 2.4); g.restore(); }
});

registerIcon('mirror', (g, o) => { // a hand mirror that shows the same trick back
  const t = o.t || 0; g.beginPath(); g.moveTo(44, 62); g.lineTo(34, 96); g.lineTo(46, 98); g.lineTo(56, 64); g.closePath(); outline(g, '#9a6a35', 3);
  g.beginPath(); g.ellipse(50, 38, 32, 34, 0, 0, 7); outline(g, '#d8aa3c', 4); g.beginPath(); g.ellipse(50, 38, 25, 27, 0, 0, 7); outline(g, '#bfe6f6', 2.6);
  const sh = (((t * 0.7) % 1.6) - 0.3) * 70; g.save(); g.beginPath(); g.ellipse(50, 38, 25, 27, 0, 0, 7); g.clip(); g.beginPath(); g.moveTo(14 + sh, 70); g.lineTo(26 + sh, 70); g.lineTo(52 + sh, 6); g.lineTo(40 + sh, 6); g.closePath(); g.fillStyle = 'rgba(255,255,255,0.7)'; g.fill(); g.restore();
  g.beginPath(); g.arc(42, 38, 3.2, 0, 7); g.arc(58, 38, 3.2, 0, 7); g.fillStyle = INK; g.fill(); g.beginPath(); g.moveTo(40, 50); g.quadraticCurveTo(50, 58, 60, 50); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
});

registerIcon('copy', (g, o) => { // two sheets, the second one a copy (the "copied" mark)
  g.beginPath(); g.roundRect(14, 10, 50, 66, 5); outline(g, '#efe3c2', 3.2); for (const y of [26, 38, 50]) { g.beginPath(); g.moveTo(22, y); g.lineTo(56, y); g.lineWidth = 3; g.strokeStyle = 'rgba(60,40,20,0.5)'; g.stroke(); }
  g.beginPath(); g.roundRect(36, 28, 50, 66, 5); outline(g, '#fffaf0', 3.2); for (const y of [44, 56, 68]) { g.beginPath(); g.moveTo(44, y); g.lineTo(78, y); g.lineWidth = 3; g.strokeStyle = 'rgba(60,40,20,0.5)'; g.stroke(); }
});

registerIcon('smirk', (g, o) => { // a face with a very pleased, slightly crooked smile (the fake retreat)
  const t = o.t || 0; const w = Math.sin(t * 5) * 1.2; g.beginPath(); g.arc(50, 56, 38, 0, 7); outline(g, '#ffd98a', 3.6);
  for (const s of [-1, 1]) { g.beginPath(); g.ellipse(50 + s * 14, 50, 6, 7, 0, 0, 7); g.fillStyle = '#fffaf0'; g.fill(); g.lineWidth = 2.4; g.strokeStyle = INK; g.stroke(); g.beginPath(); g.arc(50 + s * 14 + 2.4, 51 + w * 0.3, 3, 0, 7); g.fillStyle = INK; g.fill(); }
  g.beginPath(); g.moveTo(30, 41); g.lineTo(44, 38 + w); g.moveTo(56, 38); g.lineTo(70, 44); g.lineWidth = 3.4; g.strokeStyle = INK; g.stroke();
  g.beginPath(); g.moveTo(32, 72); g.quadraticCurveTo(54, 78, 72, 64); g.lineWidth = 4; g.strokeStyle = INK; g.stroke();
});

registerIcon('puff', (g, o) => { // a cartoon puff of smoke (something is simply gone)
  const t = o.t || 0; const k = 1 + 0.05 * Math.sin(t * 6);
  for (const [x, y, r, c] of [[34, 70, 22, '#e8e2d6'], [66, 70, 22, '#e8e2d6'], [50, 52, 26, '#f4efe6'], [50, 78, 20, '#ddd6c8']]) { g.beginPath(); g.arc(x, y, r * k, 0, 7); outline(g, c, 3); }
  for (const [x, y, r] of [[40, 56, 5], [64, 66, 4]]) { g.beginPath(); g.arc(x, y, r, 0, 7); g.fillStyle = 'rgba(255,255,255,0.8)'; g.fill(); }
});

registerIcon('horn', (g, o) => { // a rally horn with sound waves
  const t = o.t || 0; g.beginPath(); g.moveTo(14, 58); g.lineTo(46, 50); g.lineTo(84, 26); g.lineTo(84, 82); g.lineTo(46, 66); g.lineTo(14, 62); g.closePath(); outline(g, '#e2b04a', 3.4);
  g.beginPath(); g.ellipse(84, 54, 8, 28, 0, 0, 7); outline(g, '#c98f2e', 3);
  for (let k = 0; k < 3; k++) { const u = ((t * 1.4 + k / 3) % 1); g.beginPath(); g.arc(88, 54, 12 + u * 14, -0.9, 0.9); g.lineWidth = 3.4; g.strokeStyle = `rgba(42,25,14,${0.9 - u * 0.9})`; g.stroke(); }
});


registerIcon('bush', (g, o) => { // a bush: somewhere to hide
  for (const [x, y, r, c] of [[30, 72, 22, '#4c8a3a'], [68, 72, 24, '#4c8a3a'], [50, 56, 28, '#5fa04a']]) { g.beginPath(); g.arc(x, y, r, 0, 7); outline(g, c, 3.2); }
  g.beginPath(); g.moveTo(44, 90); g.lineTo(44, 98); g.moveTo(58, 90); g.lineTo(58, 98); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
  for (const [x, y] of [[40, 52], [60, 64], [28, 74]]) { g.beginPath(); g.arc(x, y, 3, 0, 7); g.fillStyle = '#e23a3a'; g.fill(); }
});
