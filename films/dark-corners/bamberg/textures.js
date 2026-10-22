// Bamberg (Kinetic): baked surfaces. Dark card (copied from proto/p11-kinetic), cream parchment (the letter), cold paper (the court),
// printed-ink dropout mask, vignette and grain tiles (the finish pass done in Canvas 2D: no WebGL in the render path).
import { rng, mk, lerp, clamp, smoothstep, fbmCanvas, valueNoise2D } from './lib.js';

export const PAD = 24;                                              // paper canvases are PAD px larger on every side so impact shakes never show an edge

export function bakeDark(w, h, U) {
  const cv = mk(w, h), g = cv.getContext('2d'), r = rng(11);
  g.fillStyle = '#070606'; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'lighter'; g.drawImage(fbmCanvas(w >> 1, h >> 1, { seed: 7, scale: 4.5, oct: 5, gain: 0.55, lo: 0, hi: 9, fn: (v) => 0.5 + (v - 0.5) * 2.2 }), 0, 0, w, h);
  const gr = g.createRadialGradient(w * 0.40, h * 0.40, 10, w * 0.40, h * 0.40, h * 0.62); gr.addColorStop(0, 'rgba(64,52,36,0.10)'); gr.addColorStop(1, 'rgba(64,52,36,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'source-over';
  for (let k = 0; k < 70; k++) { g.fillStyle = `rgba(239,230,210,${0.03 + 0.08 * r()})`; const d = (0.6 + 1.6 * r()) * U; g.fillRect(r() * w, r() * h, d, d); }
  g.lineCap = 'round'; for (let k = 0; k < 26; k++) { const x = r() * w, y = r() * h, a = r() * 6.28, L = (8 + 26 * r()) * U; g.strokeStyle = `rgba(239,230,210,${0.025 + 0.05 * r()})`; g.lineWidth = 0.6 * U; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * L * 0.5 + 3, y + Math.sin(a) * L * 0.5, x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke(); }
  return cv;
}

// the letter: warm parchment (p11 cream, with the finish tint pre-applied because there is no finish shader here)
export function bakeCream(w, h, U) {
  const cv = mk(w, h), g = cv.getContext('2d'), r = rng(77);
  g.fillStyle = '#f2e9d6'; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'multiply';
  g.drawImage(fbmCanvas(w >> 1, h >> 1, { seed: 31, scale: 2.4, oct: 4, gain: 0.5, lo: 238, hi: 255, fn: (v) => 0.5 + (v - 0.5) * 2.2 }), 0, 0, w, h);
  g.drawImage(fbmCanvas(w, h, { seed: 32, scale: 330, oct: 2, gain: 0.55, lo: 245, hi: 255, fn: (v) => 0.5 + (v - 0.5) * 2.0 }), 0, 0);
  g.globalCompositeOperation = 'source-over';
  for (let k = 0; k < 5; k++) { const x = r() * w, y = r() * h, R = (110 + 170 * r()) * U; const gr = g.createRadialGradient(x, y, 2, x, y, R); gr.addColorStop(0, 'rgba(150,108,56,0.07)'); gr.addColorStop(1, 'rgba(150,108,56,0)'); g.fillStyle = gr; g.fillRect(x - R, y - R, R * 2, R * 2); }
  g.lineCap = 'round';
  for (let k = 0; k < 900; k++) { const x = r() * w, y = r() * h, a = r() * 6.28, L = (4 + 20 * r()) * U, bend = (r() - 0.5) * 0.9; g.strokeStyle = r() < 0.6 ? `rgba(120,94,62,${0.04 + 0.08 * r()})` : `rgba(255,252,240,${0.12 + 0.22 * r()})`; g.lineWidth = (0.5 + 0.8 * r()) * U; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a + bend) * L * 0.5, y + Math.sin(a + bend) * L * 0.5, x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke(); }
  for (let k = 0; k < 60; k++) { g.fillStyle = `rgba(104,70,36,${0.10 + 0.22 * r()})`; g.beginPath(); g.arc(r() * w, r() * h, (0.5 + 1.6 * r()) * U, 0, 6.2832); g.fill(); }
  for (const yy of [h * 0.333, h * 0.667]) {                                      // trifold creases: a soft shadow line + a catch-light below it
    g.strokeStyle = 'rgba(96,66,30,0.20)'; g.lineWidth = 3 * U; g.beginPath(); g.moveTo(0, yy); g.lineTo(w, yy + 1.5 * U); g.stroke();
    g.strokeStyle = 'rgba(255,250,236,0.50)'; g.lineWidth = 2 * U; g.beginPath(); g.moveTo(0, yy + 3 * U); g.lineTo(w, yy + 4.5 * U); g.stroke();
    const gr = g.createLinearGradient(0, yy - 28 * U, 0, yy + 28 * U); gr.addColorStop(0, 'rgba(110,78,40,0)'); gr.addColorStop(0.5, 'rgba(110,78,40,0.06)'); gr.addColorStop(1, 'rgba(110,78,40,0)'); g.fillStyle = gr; g.fillRect(0, yy - 28 * U, w, 56 * U);
  }
  const eg = (x0, y0, x1, y1, ax, ay, bx, by) => { const gr = g.createLinearGradient(x0, y0, x1, y1); gr.addColorStop(0, 'rgba(120,86,44,0.13)'); gr.addColorStop(1, 'rgba(120,86,44,0)'); g.fillStyle = gr; g.fillRect(ax, ay, bx, by); };
  const e = 80 * U; eg(0, 0, e, 0, 0, 0, e, h); eg(w, 0, w - e, 0, w - e, 0, e, h); eg(0, 0, 0, e, 0, 0, w, e); eg(0, h, 0, h - e, 0, h - e, w, e);
  return cv;
}

// the court: cold, even, bureaucratic paper (blue-grey, no age, no warmth)
export function bakeCold(w, h, U) {
  const cv = mk(w, h), g = cv.getContext('2d'), r = rng(404);
  g.fillStyle = '#eceeee'; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'multiply';
  g.drawImage(fbmCanvas(w >> 1, h >> 1, { seed: 51, scale: 3, oct: 3, gain: 0.5, lo: 242, hi: 255, fn: (v) => 0.5 + (v - 0.5) * 2.0 }), 0, 0, w, h);
  g.drawImage(fbmCanvas(w, h, { seed: 52, scale: 300, oct: 2, gain: 0.55, lo: 244, hi: 255, fn: (v) => 0.5 + (v - 0.5) * 2.0 }), 0, 0);
  g.globalCompositeOperation = 'source-over';
  g.lineCap = 'round';
  for (let k = 0; k < 520; k++) { const x = r() * w, y = r() * h, a = r() * 6.28, L = (3 + 14 * r()) * U; g.strokeStyle = r() < 0.5 ? `rgba(90,104,112,${0.04 + 0.07 * r()})` : `rgba(255,255,255,${0.2 + 0.25 * r()})`; g.lineWidth = (0.5 + 0.7 * r()) * U; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke(); }
  for (let k = 0; k < 40; k++) { g.fillStyle = `rgba(40,50,56,${0.08 + 0.2 * r()})`; g.beginPath(); g.arc(r() * w, r() * h, (0.4 + 1.0 * r()) * U, 0, 6.2832); g.fill(); }
  const eg = (x0, y0, x1, y1, ax, ay, bx, by) => { const gr = g.createLinearGradient(x0, y0, x1, y1); gr.addColorStop(0, 'rgba(60,76,86,0.10)'); gr.addColorStop(1, 'rgba(60,76,86,0)'); g.fillStyle = gr; g.fillRect(ax, ay, bx, by); };
  const e = 60 * U; eg(0, 0, e, 0, 0, 0, e, h); eg(w, 0, w - e, 0, w - e, 0, e, h); eg(0, 0, 0, e, 0, 0, w, e); eg(0, h, 0, h - e, 0, h - e, w, e);
  return cv;
}

// printed-ink dropout: tiny speckles that eat up to ~20 % of the ink
export function bakeInkNoise(w, h, U) {
  const cv = mk(w, h), g = cv.getContext('2d'), img = g.createImageData(w, h), d = img.data, n = valueNoise2D(91);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const v = n.fbm(x / (2.2 * U), y / (2.2 * U), 2) * 0.7 + n(x / (0.9 * U) + 40, y / (0.9 * U) + 7) * 0.3; const a = smoothstep(0.60, 0.80, v) * 0.20; const k = (y * w + x) * 4; d[k] = d[k + 1] = d[k + 2] = 0; d[k + 3] = Math.round(a * 255); }
  g.putImageData(img, 0, 0); return cv;
}

// vignette = black overlay, same falloff as the kit's finish shader (vignette 0.30)
export function bakeVignette(w, h, amt = 0.30) {
  const cv = mk(w, h), g = cv.getContext('2d'), img = g.createImageData(w, h), d = img.data, ar = w / h;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const cx = (x / w - 0.5) * ar, cy = y / h - 0.5, r2 = cx * cx + cy * cy, k = (y * w + x) * 4; d[k] = d[k + 1] = d[k + 2] = 0; d[k + 3] = Math.round(255 * amt * smoothstep(0.25, 1.6, r2 * 2.2)); }
  g.putImageData(img, 0, 0); return cv;
}

// film grain tile: black/white speckle, a few % opacity; drawn at a per-frame deterministic offset
export function bakeGrain(w, h, amt = 0.045) {
  const cv = mk(w, h), g = cv.getContext('2d'), img = g.createImageData(w, h), d = img.data, r = rng(2718);
  for (let i = 0; i < w * h; i++) { const v = r(), k = i * 4, white = v > 0.5, m = Math.abs(v - 0.5) * 2; d[k] = d[k + 1] = d[k + 2] = white ? 255 : 0; d[k + 3] = Math.round(255 * amt * (0.35 + 0.65 * m)); }
  g.putImageData(img, 0, 0); return cv;
}
