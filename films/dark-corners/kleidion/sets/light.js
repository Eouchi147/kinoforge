// Shared painting helpers that make the gorge floors and cliffs read as lit places instead of flat tone: shafts of low sun between cast shadows, rubble with cast shadows,
// cart ruts that lead the eye to the gate, trees on the cliff ledges, a horizon band instead of a cloud-like glow.
import { Canvas, hex, mixc, mul, rgba, clamp, lerp, smoothstep, rng, underpaint } from './common.js';
import { pineTree } from '../paint.js';

// low sun from the far gap: bright wedges fanning toward the camera, soft dark wedges between them, the floor darkening toward the cliff feet
export function floorLight(C, o) {
  const R = rng(o.seed || 5); const { yFar = 704, yNear = 1300, cx = 360, n = 5, farSpread = 40, nearSpread = 520, col = [255, 200, 130], a = 0.2, shadeA = 0.3, edgeW = 170, half = (y) => 300, blur = 16 } = o;
  // draw the wedges on their own layer, blur them hard (shafts of light are soft), then lay the layer on the painting
  const lay = document.createElement('canvas'); lay.width = C.c.width; lay.height = C.c.height; const g = lay.getContext('2d'); g.setTransform(C.q, 0, 0, C.q, -C.rect[0] * C.q, -C.rect[1] * C.q);
  const lg = (alpha) => { const gr = g.createLinearGradient(0, yFar, 0, yNear); gr.addColorStop(0, rgba(col, alpha)); gr.addColorStop(0.45, rgba(col, alpha * 0.4)); gr.addColorStop(1, rgba(col, 0)); return gr; };
  const sg = (alpha) => { const gr = g.createLinearGradient(0, yFar, 0, yNear); gr.addColorStop(0, rgba([8, 5, 18], alpha * 0.1)); gr.addColorStop(0.5, rgba([8, 5, 18], alpha)); gr.addColorStop(1, rgba([8, 5, 18], alpha * 0.8)); return gr; };
  for (let k = 0; k < n; k++) {
    const u = (k + 0.5) / n - 0.5; const jit = R() - 0.5; const xf = cx + u * farSpread * 2, xn = cx + (u + jit * 0.1) * nearSpread * 2; const wf = 18 + R() * 24, wn = 150 + R() * 140;
    g.fillStyle = lg(a * (0.55 + R() * 0.8)); g.beginPath(); g.moveTo(xf - wf / 2, yFar); g.lineTo(xf + wf / 2, yFar); g.lineTo(xn + wn / 2, yNear); g.lineTo(xn - wn / 2, yNear); g.closePath(); g.fill();
    const xf2 = xf + (farSpread * 2 / n) * 0.5, xn2 = xn + (nearSpread * 2 / n) * 0.5; const sw = 120 + R() * 140;
    g.fillStyle = sg(shadeA * (0.5 + R() * 0.7)); g.beginPath(); g.moveTo(xf2 - 8, yFar); g.lineTo(xf2 + 8, yFar); g.lineTo(xn2 + sw / 2, yNear); g.lineTo(xn2 - sw / 2, yNear); g.closePath(); g.fill();
  }
  // cliff feet: the floor darkens under the walls
  for (const sd of [-1, 1]) { const x0 = cx + sd * (half(yNear) - edgeW), x1 = cx + sd * (half(yNear) + 30); const gr = g.createLinearGradient(x0, 0, x1, 0); gr.addColorStop(0, 'rgba(6,4,14,0)'); gr.addColorStop(1, 'rgba(6,4,14,0.5)'); g.fillStyle = gr; g.fillRect(Math.min(x0, x1), yFar, Math.abs(edgeW + 30), yNear - yFar); }
  const out = document.createElement('canvas'); out.width = lay.width; out.height = lay.height; const og = out.getContext('2d'); og.filter = `blur(${blur * C.q}px)`; og.drawImage(lay, 0, 0);
  const t = C.g; t.save(); t.setTransform(1, 0, 0, 1, 0, 0); t.drawImage(out, 0, 0); t.restore();
}

// rubble: rocks with a lit side toward the far gap and a cast shadow lying toward the camera; size grows with y
export function rubble(C, { x0, x1, y0, y1, n, seed = 3, base = hex('#4a3a44'), lit = hex('#d49a68'), size = (y) => 4 + (y - 700) * 0.03, mask = null }) {
  const g = C.g, R = rng(seed); const arr = []; for (let i = 0; i < n; i++) { const y = lerp(y0, y1, Math.pow(R(), 0.8)); const x = lerp(x0, x1, R()); if (mask && !mask(x, y)) continue; arr.push([x, y, size(y) * (0.5 + R() * 1.3), R()]); }
  arr.sort((a, b) => a[1] - b[1]);
  for (const [x, y, s, r] of arr) {
    g.fillStyle = 'rgba(6,4,14,0.4)'; g.beginPath(); g.ellipse(x - s * 0.5, y + s * 0.34, s * 1.7, s * 0.3, -0.05, 0, 7); g.fill();
    g.fillStyle = rgba(mul(base, 0.7 + r * 0.5)); g.beginPath(); for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2; const rr = s * (0.8 + 0.3 * Math.sin(k * 2.3 + r * 9)); const px = x + Math.cos(a) * rr, py = y - s * 0.45 + Math.sin(a) * rr * 0.62; k ? g.lineTo(px, py) : g.moveTo(px, py); } g.closePath(); g.fill();
    g.fillStyle = rgba(lit, 0.32); g.beginPath(); g.ellipse(x + s * 0.15, y - s * 0.78, s * 0.7, s * 0.2, 0.05, 0, 7); g.fill();
  }
}

// cart ruts: two pairs of dark lines converging on (gx, yFar) as the road leads to the gate
export function ruts(C, { gx = 362, yFar = 706, yNear = 1300, spread = (y) => 40 + (y - 704) * 0.32, seed = 4, a = 0.35 }) {
  const g = C.g, R = rng(seed); g.save(); g.lineCap = 'round';
  for (const off of [-1.6, -1, 1, 1.6]) { g.strokeStyle = `rgba(10,6,16,${a * (0.6 + R() * 0.5)})`; g.lineWidth = 3; g.beginPath(); for (let y = yFar; y <= yNear; y += 14) { const x = gx + off * spread(y) * 0.5 + 10 * Math.sin(y * 0.01 + off * 3); y === yFar ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke();
    g.strokeStyle = 'rgba(255,200,140,0.12)'; g.lineWidth = 1.2; g.beginPath(); for (let y = yFar; y <= yNear; y += 14) { const x = gx + off * spread(y) * 0.5 + 10 * Math.sin(y * 0.01 + off * 3) + 2.5; y === yFar ? g.moveTo(x, y - 1) : g.lineTo(x, y - 1); } g.stroke(); }
  g.restore();
}

// trees and brush on cliff ledges: small dark pines hanging on the edge with a warm rim on the side facing the low sun
export function ledgeTrees(C, { edge, side = 'L', y0, y1, n, seed = 8, col = hex('#150f1c'), rim = hex('#c88a5e'), h0 = 22, h1 = 62, inset = [10, 70] }) {
  const R = rng(seed); const sg = side === 'L' ? -1 : 1; const ts = [];
  for (let i = 0; i < n; i++) { const y = lerp(y0, y1, R()); const e = edge(y); const x = e + (side === 'L' ? -1 : 1) * lerp(inset[0], inset[1], R()) * (0.4 + R()); ts.push([x, y + 6, lerp(h0, h1, Math.pow(R(), 1.3)) * (0.7 + 0.5 * smoothstep(y0, y1, y)), R()]); }
  ts.sort((a, b) => a[1] - b[1]);
  for (const [x, y, h, r] of ts) pineTree(C, x, y, h, mul(col, 0.8 + r * 0.5), { rim, rimSide: side === 'L' ? 1 : -1, tierPx: Math.max(3.5, h / 9), wr: 0.34 });
}

// a thin warm horizon band (a real afterglow: wide and flat, brightest at the skyline) instead of a round cloud-like blob
export function horizonGlow(C, { y, x0, x1, h = 90, col = [255, 190, 120], a = 0.5, core = 0.9, streaks = 5, seed = 2 }) {
  const g = C.g, R = rng(seed); g.save();
  const gr = g.createLinearGradient(0, y - h, 0, y + h * 0.5); gr.addColorStop(0, rgba(col, 0)); gr.addColorStop(0.7, rgba(col, a * 0.7)); gr.addColorStop(0.9, rgba(mixc(col, [255, 240, 200], core * 0.6), a)); gr.addColorStop(1, rgba(col, a * 0.5)); g.fillStyle = gr; g.fillRect(x0, y - h, x1 - x0, h * 1.5);
  for (let i = 0; i < streaks; i++) { const yy = y - h * (0.08 + 0.7 * R()); const w = 120 + R() * 380; const x = lerp(x0, x1, R()); const sg = g.createLinearGradient(x - w, 0, x + w, 0); sg.addColorStop(0, rgba(col, 0)); sg.addColorStop(0.5, rgba(col, 0.2 + 0.2 * R())); sg.addColorStop(1, rgba(col, 0)); g.fillStyle = sg; g.fillRect(x - w, yy - 1.2 - R() * 1.8, w * 2, 2.4 + R() * 2.4); }
  g.restore();
}
