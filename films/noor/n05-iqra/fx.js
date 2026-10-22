// small shared effects for NOOR films: hash, additive glows, embers, the hand lantern, stars. Pure functions of time.
import { clamp, lerp, smoothstep, noise1 } from '/harness/kit/film.js';
export const hash1 = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
export function glowAt(gg, x, y, r, a = 1, col = [255, 160, 80]) {
  if (!(r > 0.5) || !(a > 0.002)) return;
  const g = gg.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${a})`); g.addColorStop(0.18, `rgba(${col[0]},${col[1]},${col[2]},${a * 0.45})`); g.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
  gg.fillStyle = g; gg.fillRect(x - r, y - r, r * 2, r * 2);
}
export function embers(g, t, f, n, { size = 1.6, col = [255, 160, 70], a = 0.8, rise = 1, wind = 10, seed = 1 } = {}) {
  for (let i = 0; i < n; i++) { const r1 = hash1(i * 3.1 + seed), r2 = hash1(i * 7.7 + seed), r3 = hash1(i * 1.9 + seed), life = 2 + 3 * r3; const u = ((t / life + r1) % 1);
    const x = f.x0 + (f.x1 - f.x0) * r2 + Math.sin(t * 1.3 + i) * 8 + wind * u * life * 0.6, y = f.y1 - (f.y1 - f.y0) * u * rise; const al = a * Math.sin(Math.PI * u) * (0.5 + 0.5 * hash1(i + Math.floor(t * 6)));
    g.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${al})`; g.beginPath(); g.arc(x, y, size * (0.5 + r3), 0, 7); g.fill(); }
}
export const flick = (t, seed) => 1 + 0.06 * noise1(t * 8.3 + seed * 3.7, seed) + 0.03 * noise1(t * 21 + seed, seed + 2);
// a hand lantern with nobody carrying it on screen: a small brass frame, a flame, swinging gently. s = size in px (frame height)
export function handLantern(g, gg, x, y, s, t, { swing = 0.12, lit = 1, seed = 0 } = {}) {
  const a = swing * Math.sin(t * 2.6 + seed) ; const fl = flick(t, seed);
  g.save(); g.translate(x, y); g.rotate(a);
  if (s > 5) {
    g.strokeStyle = 'rgba(60,44,26,0.9)'; g.lineWidth = Math.max(0.8, s * 0.06); g.beginPath(); g.moveTo(-s * 0.18, -s * 0.55); g.quadraticCurveTo(0, -s * 0.85, s * 0.18, -s * 0.55); g.stroke();
    g.fillStyle = 'rgba(70,52,30,0.95)'; g.fillRect(-s * 0.26, -s * 0.55, s * 0.52, s * 0.1); g.fillRect(-s * 0.3, s * 0.38, s * 0.6, s * 0.1);
    g.fillStyle = `rgba(255,${190 + 30 * fl | 0},110,${0.55 * lit})`; g.fillRect(-s * 0.22, -s * 0.45, s * 0.44, s * 0.83);
    g.strokeStyle = 'rgba(60,44,26,0.9)'; g.lineWidth = Math.max(0.6, s * 0.035); for (const xx of [-0.22, 0, 0.22]) { g.beginPath(); g.moveTo(xx * s, -s * 0.45); g.lineTo(xx * s, s * 0.38); g.stroke(); }
  }
  g.fillStyle = `rgba(255,240,190,${0.95 * lit})`; g.beginPath(); g.ellipse(0, 0, Math.max(0.8, s * 0.07), Math.max(1.2, s * 0.16 * fl), 0, 0, 7); g.fill();
  g.restore();
  glowAt(gg, x, y, Math.max(10, s * 2.2), 0.85 * lit * fl, [255, 190, 110]); glowAt(gg, x, y, Math.max(26, s * 7), 0.22 * lit * fl, [255, 150, 70]);
}
// a star field drawn per frame (twinkle, optional rotation about a pole): box in design px, n stars, rot (radians)
export function stars(gg, t, box, { n = 220, seed = 3, a = 1, rot = 0, pole = [640, -400], big = 0.08 } = {}) {
  const [x0, y0, x1, y1] = box; const c = Math.cos(rot), s = Math.sin(rot);
  for (let i = 0; i < n; i++) {
    const r1 = hash1(i * 1.71 + seed), r2 = hash1(i * 3.33 + seed), r3 = hash1(i * 5.9 + seed);
    let x = lerp(x0, x1, r1), y = lerp(y0, y1, Math.pow(r2, 1.4));
    if (rot) { const dx = x - pole[0], dy = y - pole[1]; x = pole[0] + dx * c - dy * s; y = pole[1] + dx * s + dy * c; }
    const tw = 0.6 + 0.4 * Math.sin(t * (1.1 + r3 * 2.7) + i * 2.1) * Math.sin(t * (0.37 + r1) + i);
    const b = r3 > 1 - big ? 1.8 : 0.9 + r3 * 0.6; const al = a * (0.35 + 0.65 * r3) * tw;
    gg.fillStyle = `rgba(${200 + 55 * r1 | 0},${215 + 30 * r2 | 0},255,${al})`; gg.beginPath(); gg.arc(x, y, b * 0.75, 0, 7); gg.fill();
    if (b > 1.5) { gg.fillStyle = `rgba(220,230,255,${al * 0.25})`; gg.beginPath(); gg.arc(x, y, b * 2.6, 0, 7); gg.fill(); }
  }
}
// a Ramadan lantern (fanous): brass frame, domed cap, warm glass panes, a ring to hang it by. Drawn at (x, y) = centre of the glass, s = height in px.
export function fanous(g, gg, x, y, s, t, { lit = 1, sway = 0.04, seed = 0 } = {}) {
  const fl = flick(t, seed + 5); const a = sway * Math.sin(t * 0.9 + seed);
  g.save(); g.translate(x, y); g.rotate(a);
  const w = s * 0.42, h = s * 0.5; const brass = 'rgba(120,88,40,0.98)', dark = 'rgba(60,40,18,0.98)';
  // glass body (hexagon seen from the side: three panes)
  g.fillStyle = `rgba(255,${200 + 25 * fl | 0},120,${0.88 * lit + 0.1})`; g.beginPath(); g.moveTo(-w * 0.5, -h * 0.5); g.lineTo(w * 0.5, -h * 0.5); g.lineTo(w * 0.42, h * 0.5); g.lineTo(-w * 0.42, h * 0.5); g.closePath(); g.fill();
  g.fillStyle = `rgba(255,140,60,${0.35 * lit})`; g.fillRect(-w * 0.5, -h * 0.5, w * 0.16, h); g.fillRect(w * 0.34, -h * 0.5, w * 0.16, h);
  g.strokeStyle = dark; g.lineWidth = Math.max(0.8, s * 0.018); for (const k of [-0.17, 0.17]) { g.beginPath(); g.moveTo(k * w, -h * 0.5); g.lineTo(k * w * 0.85, h * 0.5); g.stroke(); }
  // pierced brass bands
  g.fillStyle = brass; g.fillRect(-w * 0.56, -h * 0.58, w * 1.12, h * 0.1); g.fillRect(-w * 0.48, h * 0.48, w * 0.96, h * 0.1);
  g.fillStyle = `rgba(255,220,150,${0.8 * lit})`; for (let i = -2; i <= 2; i++) { g.beginPath(); g.arc(i * w * 0.18, -h * 0.53, s * 0.012, 0, 7); g.fill(); }
  // domed cap, finial and ring
  g.fillStyle = brass; g.beginPath(); g.moveTo(-w * 0.56, -h * 0.58); g.quadraticCurveTo(-w * 0.5, -h * 1.05, 0, -h * 1.12); g.quadraticCurveTo(w * 0.5, -h * 1.05, w * 0.56, -h * 0.58); g.closePath(); g.fill();
  g.fillStyle = 'rgba(200,160,80,0.7)'; g.beginPath(); g.moveTo(-w * 0.4, -h * 0.66); g.quadraticCurveTo(-w * 0.3, -h * 0.95, 0, -h * 1.02); g.lineTo(0, -h * 0.9); g.quadraticCurveTo(-w * 0.2, -h * 0.85, -w * 0.3, -h * 0.66); g.closePath(); g.fill();
  g.fillStyle = brass; g.fillRect(-s * 0.012, -h * 1.3, s * 0.024, h * 0.2); g.strokeStyle = brass; g.lineWidth = Math.max(0.8, s * 0.02); g.beginPath(); g.arc(0, -h * 1.38, s * 0.045, 0, 7); g.stroke();
  // base drop
  g.fillStyle = brass; g.beginPath(); g.moveTo(-w * 0.4, h * 0.58); g.quadraticCurveTo(0, h * 0.86, w * 0.4, h * 0.58); g.closePath(); g.fill();
  // flame
  g.fillStyle = `rgba(255,248,210,${0.95 * lit})`; g.beginPath(); g.ellipse(0, h * 0.08, s * 0.03, s * 0.08 * fl, 0, 0, 7); g.fill();
  g.restore();
  glowAt(gg, x, y, s * 0.9, 0.75 * lit * fl, [255, 196, 110]); glowAt(gg, x, y, s * 2.6, 0.24 * lit * fl, [255, 150, 70]);
}
