// Ambient life for the wide shots: birds, smoke, drifting dust and haze, light shafts, distant folk, grass strips that sway in the wind.
// Everything is a pure function of time (no clocks), drawn in design px (720x1280) on the detail layer `g` or the additive glow canvas `gg`.
import { clamp, lerp, smoothstep } from '/harness/kit/film.js';
import { rgba, hex, mixc, mul, Canvas } from './paint.js';
import { hash1 } from './figs.js';

// a flock crossing the sky: small V silhouettes with a wing beat; o = { x0, x1, y0, y1, n, seed, size, speed (px/s), dir, col, a, hz }
export function birds(g, t, o) {
  const { x0 = -40, x1 = 760, y0 = 200, y1 = 420, n = 7, seed = 1, size = 7, speed = 22, dir = 1, col = [14, 12, 28], a = 0.85, hz = 2.2, wob = 14 } = o;
  const span = x1 - x0 + 160;
  for (let i = 0; i < n; i++) {
    const r1 = hash1(i * 5.1 + seed), r2 = hash1(i * 9.7 + seed), r3 = hash1(i * 2.3 + seed);
    const lead = (i % 2 ? 1 : -1) * Math.ceil(i / 2) * size * 2.4; // loose V formation
    const px = x0 - 80 + (((r1 * span + speed * dir * t - lead * dir * 1.4) % span) + span) % span;
    const py = lerp(y0, y1, r2 * 0.3) + Math.abs(lead) * 0.35 + wob * Math.sin(t * 0.5 + r3 * 6) + (y1 - y0) * 0.25 * Math.sin(t * 0.07 + seed);
    const s = size * (0.8 + 0.4 * r3); const f = Math.sin(2 * Math.PI * hz * t * (0.9 + 0.2 * r2) + r1 * 6.28);
    const up = f * 0.55; // wing angle
    g.strokeStyle = rgba(col, a); g.lineWidth = Math.max(1, s * 0.22); g.lineCap = 'round'; g.lineJoin = 'round';
    g.beginPath(); g.moveTo(px - s, py - s * up * 0.9); g.quadraticCurveTo(px - s * 0.45, py - s * 0.35 - s * up * 0.5, px, py);
    g.quadraticCurveTo(px + s * 0.45, py - s * 0.35 - s * up * 0.5, px + s, py - s * up * 0.9); g.stroke();
  }
}

// soft smoke rising from (x,y): drifting, widening puffs; o = { n, rise, wind, r0, r1, a, col, life, seed }
export function smoke(g, t, x, y, o = {}) {
  const { n = 9, rise = 90, wind = 14, r0 = 2.5, r1 = 15, a = 0.28, col = [120, 112, 150], life = 7, seed = 1 } = o;
  for (let i = 0; i < n; i++) {
    const u = (((t / life) + i / n + hash1(seed * 3.1)) % 1);
    const px = x + wind * u * life * 0.5 + 4 * Math.sin(t * 0.8 + i * 1.7) * u + 6 * (hash1(i + seed) - 0.5) * u;
    const py = y - rise * u; const r = lerp(r0, r1, Math.sqrt(u)); const al = a * Math.sin(Math.PI * Math.min(1, u * 1.05)) * (1 - u * 0.55);
    const gr = g.createRadialGradient(px, py, 0, px, py, r); gr.addColorStop(0, rgba(col, al)); gr.addColorStop(0.6, rgba(col, al * 0.5)); gr.addColorStop(1, rgba(col, 0));
    g.fillStyle = gr; g.fillRect(px - r, py - r, r * 2, r * 2);
  }
}

// warm / cold drifting dust or pollen in a box (additive); o = { n, col, a, size, speed, seed }
export function motes(gg, t, f, o = {}) {
  const { n = 24, col = [255, 215, 160], a = 0.35, size = 1.3, speed = 6, seed = 1, drift = [5, -3] } = o;
  for (let i = 0; i < n; i++) {
    const r1 = hash1(i * 3.7 + seed), r2 = hash1(i * 6.1 + seed), r3 = hash1(i * 1.3 + seed); const w = f.x1 - f.x0, h = f.y1 - f.y0;
    const px = f.x0 + (((r1 * w + drift[0] * t * (0.5 + r3) + 14 * Math.sin(t * 0.4 + i)) % w) + w) % w;
    const py = f.y0 + (((r2 * h + drift[1] * t * (0.5 + r3) + 9 * Math.sin(t * 0.33 + i * 2.1)) % h) + h) % h;
    const tw = 0.55 + 0.45 * Math.sin(t * (0.7 + r3 * 1.6) + i * 3.3);
    gg.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${a * tw})`; gg.beginPath(); gg.arc(px, py, size * (0.6 + r3), 0, 7); gg.fill();
  }
}

// a soft slanting shaft of light (additive): from a source rect at the top to a wider base, breathing slowly
export function shaft(gg, t, o) {
  const { x = 360, y0 = 300, y1 = 900, w0 = 20, w1 = 160, ang = 0.18, a = 0.12, col = [255, 200, 130], seed = 0 } = o;
  const k = a * (0.85 + 0.15 * Math.sin(t * 0.4 + seed * 2.3)); const dx = Math.tan(ang) * (y1 - y0);
  const gr = gg.createLinearGradient(x, y0, x + dx, y1); gr.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${k})`); gr.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
  gg.fillStyle = gr; gg.beginPath(); gg.moveTo(x - w0 / 2, y0); gg.lineTo(x + w0 / 2, y0); gg.lineTo(x + dx + w1 / 2, y1); gg.lineTo(x + dx - w1 / 2, y1); gg.closePath(); gg.fill();
}

// low ground haze: wide soft blobs sliding along the ground (additive)
export function hazeBand(gg, t, o) {
  const { y = 800, x0 = -100, x1 = 820, n = 6, h = 40, w = 300, a = 0.07, col = [150, 150, 210], speed = 8, seed = 1 } = o;
  const span = x1 - x0 + w;
  for (let i = 0; i < n; i++) {
    const r1 = hash1(i * 4.1 + seed), r2 = hash1(i * 8.3 + seed); const px = x0 - w / 2 + (((r1 * span + speed * t) % span) + span) % span; const py = y + (r2 - 0.5) * h * 1.4 + 3 * Math.sin(t * 0.3 + i);
    const gr = gg.createRadialGradient(px, py, 0, px, py, w * 0.5); gr.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${a})`); gr.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
    gg.save(); gg.translate(px, py); gg.scale(1, h / w); gg.translate(-px, -py); gg.fillStyle = gr; gg.fillRect(px - w * 0.5, py - w * 0.5, w, w); gg.restore();
  }
}

// a painted grass strip (own plane): blades along the bottom, to be swayed by the wind uniform. rect in design px.
export function paintGrassStrip(S, name, D, rect, { seed = 1, col = hex('#0d0f20'), lit = hex('#3a3f70'), h0 = 18, h1 = 46, step = 8, amp = 0.006, freq = 22 } = {}) {
  const C = new Canvas(rect, { seed, q: 1 }); const R = C.R; const [x0, y0, x1, y1] = rect;
  for (let x = x0 - 6; x < x1 + 6; x += step * (0.4 + R())) {
    const h = lerp(h0, h1, Math.pow(R(), 1.4)); const yb = y1 + 4 + R() * 6; const k = 3 + Math.floor(R() * 3);
    for (let i = 0; i < k; i++) { const a = -Math.PI / 2 + (R() - 0.5) * 0.7; const c = mixc(mul(col, 0.7 + R() * 0.6), lit, R() < 0.18 ? 0.5 : 0);
      C.dab(x + (R() - 0.5) * h * 0.3, yb - h * 0.45, a, h * (0.8 + R() * 0.4), Math.max(1.4, h * 0.075), c, 0.92, 0.1 * (R() - 0.5) * 2, 0.9); }
  }
  const pl = S.plane(name, D, rect, C.c); pl.material.uniforms.uSway.value.set(amp, 0.0, freq); return pl;
}

// a light shaft between two screen points (e.g. a gap in the cliffs and a patch of floor), widening toward b; follows the camera because both ends are projected plane points
export function shaftAB(gg, t, a, b, w0, w1, alpha = 0.1, col = [255, 200, 130], seed = 0) {
  const k = alpha * (0.82 + 0.18 * Math.sin(t * 0.37 + seed * 2.1)); const dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; const nx = -dy / l, ny = dx / l;
  const gr = gg.createLinearGradient(a[0], a[1], b[0], b[1]); gr.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${k})`); gr.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
  gg.fillStyle = gr; gg.beginPath(); gg.moveTo(a[0] + nx * w0 / 2, a[1] + ny * w0 / 2); gg.lineTo(a[0] - nx * w0 / 2, a[1] - ny * w0 / 2); gg.lineTo(b[0] - nx * w1 / 2, b[1] - ny * w1 / 2); gg.lineTo(b[0] + nx * w1 / 2, b[1] + ny * w1 / 2); gg.closePath(); gg.fill();
}
