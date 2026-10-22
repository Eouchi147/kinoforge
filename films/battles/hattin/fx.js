// Hattin: film-side overlay effects, installed on top of the Battle Map engine without changing it.
//  - spec.shimmer = [{ at, until, strength, fadeIn, fadeOut }]  heat haze: a warm veil and rising wavy light bands over the whole frame
//  - spec.smoke   = [{ at, until, from: [x0, z0, x1, z1], wind: [dx, dz], n, size, rise, speed, alpha }]  puffs born along a line that drift on the wind (world anchored)
//  - spec.dim     = [{ at, until, alpha, color, stars, fadeIn, fadeOut }]  a veil over the map (night), optional twinkling stars
// Pure functions of t (hash based), so every frame is reproducible.
import { StageOverlay } from '/films/lib/battlemap/overlay.js';
import { clamp, hash01 } from '/films/lib/battlemap/noise.js';

const win = (self, key, specs) => { const k = '_' + key; if (!self[k]) self[k] = specs.map((r) => ({ ...r, t0: self.clock.at(r.at), t1: self.clock.at(r.until) })); return self[k]; };
const env = (r, t) => clamp((t - r.t0) / (r.fadeIn ?? 0.8)) * (1 - clamp((t - r.t1) / (r.fadeOut ?? 0.8)));

export function installFx() {
  const draw0 = StageOverlay.prototype.draw;
  StageOverlay.prototype.draw = function (g, t, view) {
    const sp = this.stage.spec;
    if (sp.dim && sp.dim.length) for (const d of win(this, 'dim', sp.dim)) { const a = env(d, t); if (a > 0.005) drawDim(g, t, view.rect, a, d); }
    if (sp.shimmer && sp.shimmer.length) for (const s of win(this, 'shimmer', sp.shimmer)) { const a = env(s, t); if (a > 0.01) drawShimmer(g, t, view.rect, a * (s.strength ?? 1)); }
    if (sp.smoke && sp.smoke.length) for (const s of win(this, 'smoke', sp.smoke)) { const a = env(s, t); if (a > 0.01) drawSmoke(g, t, view, this.stage, a, s); }
    draw0.call(this, g, t, view);
  };
}

function drawDim(g, t, r, a, d) {
  g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip(); g.globalAlpha = a * d.alpha; g.fillStyle = d.color || 'rgb(14,7,3)'; g.fillRect(r.x, r.y, r.w, r.h); g.globalAlpha = a;
  if (d.stars) {
    for (let i = 0; i < 46; i++) { const x = r.x + hash01(i, 1) * r.w, y = r.y + hash01(i, 2) * r.h * 0.42; const tw = 0.5 + 0.5 * Math.sin(t * (1.5 + hash01(i, 3) * 2.5) + i * 1.7); const s = r.h * (0.0025 + 0.004 * hash01(i, 4)) * (0.6 + 0.8 * tw);
      g.globalAlpha = a * (0.35 + 0.6 * tw); g.fillStyle = '#fff6d8'; g.beginPath(); g.moveTo(x, y - s * 2); g.lineTo(x + s * 0.5, y - s * 0.5); g.lineTo(x + s * 2, y); g.lineTo(x + s * 0.5, y + s * 0.5); g.lineTo(x, y + s * 2); g.lineTo(x - s * 0.5, y + s * 0.5); g.lineTo(x - s * 2, y); g.lineTo(x - s * 0.5, y - s * 0.5); g.closePath(); g.fill(); }
  }
  g.restore();
}

function drawShimmer(g, t, r, a) {
  g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip();
  const gr = g.createLinearGradient(0, r.y, 0, r.y + r.h); gr.addColorStop(0, 'rgba(255,190,90,0)'); gr.addColorStop(0.55, 'rgba(255,200,110,0.10)'); gr.addColorStop(1, 'rgba(255,170,70,0.22)');
  g.globalAlpha = a; g.fillStyle = gr; g.fillRect(r.x, r.y, r.w, r.h); g.lineCap = 'round';
  for (let i = 0; i < 16; i++) { // rising wavy bands
    const ph = hash01(i, 5); const u = ((ph + t * (0.05 + 0.04 * hash01(i, 6))) % 1); const y0 = r.y + r.h * (1.02 - u * 0.95); const x0 = r.x + hash01(i, 7) * r.w * 1.1 - r.w * 0.05; const w = r.w * (0.16 + 0.22 * hash01(i, 8));
    g.beginPath(); for (let k = 0; k <= 14; k++) { const x = x0 + w * k / 14, y = y0 + Math.sin(k * 0.9 + t * 4 + i * 2.1) * r.h * 0.006; k ? g.lineTo(x, y) : g.moveTo(x, y); }
    g.globalAlpha = a * 0.22 * Math.sin(Math.PI * u); g.lineWidth = Math.max(2, r.h * 0.005); g.strokeStyle = 'rgba(255,248,224,1)'; g.stroke(); }
  g.restore();
}

function drawSmoke(g, t, view, stage, a, s) {
  const [x0, z0, x1, z1] = s.from; const [wx, wz] = s.wind; const n = s.n ?? 40; const speed = s.speed ?? 0.11; const size = s.size ?? 7; const rise = s.rise ?? 9; const H = view.rect.h;
  g.save(); g.beginPath(); g.rect(view.rect.x, view.rect.y, view.rect.w, view.rect.h); g.clip();
  for (let i = 0; i < n; i++) {
    const u = (((hash01(i, 11) + (t - s.t0) * speed * (0.8 + 0.5 * hash01(i, 12))) % 1) + 1) % 1; const f = hash01(i, 13);
    const x = x0 + (x1 - x0) * f + wx * u + Math.sin(t * 0.9 + i) * 3, z = z0 + (z1 - z0) * f + wz * u + Math.cos(t * 0.7 + i * 1.3) * 3; const y = stage.mh(x, z) + 2 + rise * u;
    const p = view.project(x, y, z); if (!p.ok) continue; const r = size * view.pxPerUnit(p.depth) * (0.5 + 1.5 * u) * (0.8 + 0.5 * hash01(i, 14)); const al = a * (s.alpha ?? 0.55) * Math.sin(Math.PI * Math.min(1, u * 1.15)) * (0.6 + 0.4 * hash01(i, 15));
    if (al < 0.01 || r < 1) continue; const gr = g.createRadialGradient(p.x, p.y, r * 0.1, p.x, p.y, r); gr.addColorStop(0, `rgba(88,80,74,${al})`); gr.addColorStop(0.6, `rgba(120,112,104,${al * 0.7})`); gr.addColorStop(1, 'rgba(140,132,124,0)');
    g.fillStyle = gr; g.beginPath(); g.arc(p.x, p.y, r, 0, 7); g.fill(); }
  g.restore(); void H;
}
