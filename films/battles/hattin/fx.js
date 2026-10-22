// Hattin: film-side effects, installed over the Battle Map engine without changing it. Pure functions of t (hash based).
// In the world (patches Ambient.update, uses the kinds from kinds.js):
//  - ambient.fires = [{ path: [[x, z], ...], at, spread, until, n, sc, smoke }]  the brush fire: flames light one after another along the
//    path over `spread` seconds, flicker, and send up dark smoke columns; glows are added in the overlay so they read at night.
//  - ambient.pavilions = [{ pos, team, sc, at, fallAt, fallDur }]  King Guy's red tent; it collapses at `fallAt`.
// In the overlay (patches StageOverlay.draw):
//  - spec.heat   = [{ at, until, strength }]   a warm haze veil, heavier near the ground (the July heat), no moving graphics
//  - spec.smoke  = [{ at, until, from: [x0, z0, x1, z1], wind: [dx, dz], n, size, rise, speed, alpha }]  smoke born along the fire line
//    that drifts on the wind (world anchored): the smoke blowing into the crusader camp
//  - spec.dim    = [{ at, until, alpha, color }]  the night veil
//  - spec.regions = [{ at, until, poly: [[x, z], ...], team, alpha }]  a territory on the map (fine hatching, inked edge): the Levant stage
import { StageOverlay } from '/films/lib/battlemap/overlay.js';
import { Ambient } from '/films/lib/battlemap/ambient.js';
import { TEAMS } from '/films/lib/battlemap/blocks.js';
import { clamp, hash01, lerp } from '/films/lib/battlemap/noise.js';

const win = (self, key, specs) => { const k = '_' + key; if (!self[k]) self[k] = specs.map((r) => ({ ...r, t0: self.clock.at(r.at), t1: r.until !== undefined ? self.clock.at(r.until) : 1e9 })); return self[k]; };
const env = (r, t) => clamp((t - r.t0) / (r.fadeIn ?? 0.8)) * (1 - clamp((t - r.t1) / (r.fadeOut ?? 0.8)));

// the flames of every fire line at time t: [{ x, z, k (0..1 size), i }]
function samplePath(P, f) { const seg = []; let L = 0; for (let i = 1; i < P.length; i++) { const d = Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); seg.push(d); L += d; } let s = f * L, i = 0; while (i < seg.length - 1 && s > seg[i]) { s -= seg[i]; i++; } const u = clamp(s / seg[i]); return [lerp(P[i][0], P[i + 1][0], u), lerp(P[i][1], P[i + 1][1], u)]; }
function flames(fire, clock, t) {
  if (!fire._t) { fire._t = [clock.at(fire.at), fire.until !== undefined ? clock.at(fire.until) : 1e9]; }
  const [t0, t1] = fire._t; if (t < t0 || t > t1 + 3) return []; const n = fire.n ?? 40; const out = []; const spread = fire.spread ?? 3;
  for (let i = 0; i < n; i++) { const f = (i + 0.5) / n; const lit = t0 + spread * f + hash01(i, 3) * 0.4; if (t < lit) continue; const [x, z] = samplePath(fire.path, f);
    const jx = (hash01(i, 5) - 0.5) * (fire.width ?? 6), jz = (hash01(i, 6) - 0.5) * (fire.width ?? 6); const grow = clamp((t - lit) / 0.9) * (1 - clamp((t - t1) / 2.5));
    const flick = 0.78 + 0.16 * Math.sin(t * 9.1 + i * 2.3) + 0.08 * Math.sin(t * 15.7 + i * 5.1); out.push({ x: x + jx, z: z + jz, k: grow * flick, i }); }
  return out;
}

export function installFx() {
  const up0 = Ambient.prototype.update;
  Ambient.prototype.update = function (t) {
    up0.call(this, t); const F = this.stage.blocks.figs; if (!F) return; const sp = this.spec || {}; const mh = this.stage.mh;
    for (const fire of (sp.fires || [])) { for (const fl of flames(fire, this.clock, t)) { if (fl.k <= 0.02) continue;
      F.extra.push({ kind: 'flame', x: fl.x, z: fl.z, fx: Math.sin(fl.i), fz: Math.cos(fl.i), sc: (fire.sc ?? 2.4) * fl.k, col: [0.3, 0.2, 0.1] });
      if (fl.i % (fire.smokeEvery ?? 3) === 0) this.smokeAt(F.extraPuffs, fl.x, fl.z, t, 6, (fire.smoke ?? 0.3) * Math.min(1, fl.k), mh, this.wind, fire.smokeH ?? 12, [0.36, 0.33, 0.30]); } }
    for (const pv of (sp.pavilions || [])) { if (!pv._t) pv._t = [pv.at !== undefined ? this.clock.at(pv.at) : -1e9, pv.fallAt !== undefined ? this.clock.at(pv.fallAt) : 1e9];
      if (t < pv._t[0]) continue; const fall = clamp((t - pv._t[1]) / (pv.fallDur ?? 0.9)); const k = clamp((t - pv._t[0]) / 0.6) * (1 - 0.82 * fall * fall);
      const col = (TEAMS[pv.team || 'rome'] || TEAMS.rome).top; F.extra.push({ kind: 'pavilion', x: pv.pos[0], z: pv.pos[1], fx: 0, fz: -1, sc: (pv.sc ?? 6) * k, col }); }
  };
  const draw0 = StageOverlay.prototype.draw;
  StageOverlay.prototype.draw = function (g, t, view) {
    const sp = this.stage.spec;
    if (sp.regions && sp.regions.length) for (const r of win(this, 'regions', sp.regions)) { const a = env(r, t); if (a > 0.01) drawRegion(g, view, r, a); }
    if (sp.heat && sp.heat.length) for (const s of win(this, 'heat', sp.heat)) { const a = env(s, t); if (a > 0.01) drawHeat(g, view.rect, a * (s.strength ?? 1)); }
    if (sp.smoke && sp.smoke.length) for (const s of win(this, 'smoke', sp.smoke)) { const a = env(s, t); if (a > 0.01) drawSmoke(g, t, view, this.stage, a, s); }
    if (sp.dim && sp.dim.length) for (const d of win(this, 'dim', sp.dim)) { const a = env(d, t); if (a > 0.005) { const r = view.rect; g.save(); g.globalAlpha = a * d.alpha; g.fillStyle = d.color || 'rgb(14,7,3)'; g.fillRect(r.x, r.y, r.w, r.h); g.restore(); } }
    const fires = sp.ambient?.fires || []; if (fires.length) drawGlows(g, t, view, this.stage, fires, this.clock);
    draw0.call(this, g, t, view);
  };
}

function drawRegion(g, view, e, a) {
  const pts = e.poly.map(([x, z]) => view.project(x, e.y ?? 2, z)); if (pts.some((q) => !(q.depth > 1))) return;
  const r = view.rect; const c = (TEAMS[e.team] || TEAMS.neutral).top.map((v) => Math.round(v * 255)); const al = (e.alpha ?? 0.24) * a;
  const path = () => { g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q.x, q.y) : g.moveTo(q.x, q.y))); g.closePath(); };
  g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip();
  path(); g.fillStyle = `rgba(${c[0]},${c[1]},${c[2]},${al})`; g.fill();
  g.save(); path(); g.clip(); g.strokeStyle = `rgba(${c[0]},${c[1]},${c[2]},${al * 0.9})`; g.lineWidth = Math.max(1, r.h * 0.0016); const s = r.h * 0.016; g.beginPath(); for (let x = -r.h; x < r.w + r.h; x += s) { g.moveTo(r.x + x, r.y + r.h); g.lineTo(r.x + x + r.h * 0.6, r.y); } g.stroke(); g.restore();
  path(); g.lineJoin = 'round'; g.lineWidth = Math.max(3, r.h * 0.0055); g.strokeStyle = `rgba(244,234,210,${0.8 * a})`; g.stroke(); g.lineWidth = Math.max(1.4, r.h * 0.0024); g.strokeStyle = `rgba(${Math.round(c[0] * 0.7)},${Math.round(c[1] * 0.7)},${Math.round(c[2] * 0.7)},${Math.min(1, al * 3.4)})`; g.stroke();
  g.restore();
}
function drawHeat(g, r, a) {
  g.save(); const gr = g.createLinearGradient(0, r.y, 0, r.y + r.h); gr.addColorStop(0, 'rgba(255,214,150,0.10)'); gr.addColorStop(0.5, 'rgba(255,196,120,0.06)'); gr.addColorStop(1, 'rgba(255,170,80,0.16)');
  g.globalAlpha = a; g.fillStyle = gr; g.fillRect(r.x, r.y, r.w, r.h); g.restore();
}
function drawSmoke(g, t, view, stage, a, s) {
  const [x0, z0, x1, z1] = s.from; const [wx, wz] = s.wind; const n = s.n ?? 40; const speed = s.speed ?? 0.11; const size = s.size ?? 7; const rise = s.rise ?? 9;
  g.save(); g.beginPath(); g.rect(view.rect.x, view.rect.y, view.rect.w, view.rect.h); g.clip();
  for (let i = 0; i < n; i++) {
    const u = (((hash01(i, 11) + (t - s.t0) * speed * (0.8 + 0.5 * hash01(i, 12))) % 1) + 1) % 1; const f = hash01(i, 13);
    const x = x0 + (x1 - x0) * f + wx * u + Math.sin(t * 0.9 + i) * 3, z = z0 + (z1 - z0) * f + wz * u + Math.cos(t * 0.7 + i * 1.3) * 3; const y = stage.mh(x, z) + 2 + rise * u;
    const p = view.project(x, y, z); if (!p.ok) continue; const r = size * view.pxPerUnit(p.depth) * (0.5 + 1.5 * u) * (0.8 + 0.5 * hash01(i, 14)); const al = a * (s.alpha ?? 0.55) * Math.sin(Math.PI * Math.min(1, u * 1.15)) * (0.6 + 0.4 * hash01(i, 15));
    if (al < 0.01 || r < 1) continue; const gr = g.createRadialGradient(p.x, p.y, r * 0.1, p.x, p.y, r); gr.addColorStop(0, `rgba(88,80,74,${al})`); gr.addColorStop(0.6, `rgba(120,112,104,${al * 0.7})`); gr.addColorStop(1, 'rgba(140,132,124,0)');
    g.fillStyle = gr; g.beginPath(); g.arc(p.x, p.y, r, 0, 7); g.fill(); }
  g.restore();
}
function drawGlows(g, t, view, stage, fires, clock) { // the light of the flames, added over the night veil
  const r = view.rect; g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip(); g.globalCompositeOperation = 'lighter';
  for (const fire of fires) for (const fl of flames(fire, clock, t)) { if (fl.k <= 0.05) continue; const p = view.project(fl.x, stage.mh(fl.x, fl.z) + 1.2, fl.z); if (!p.ok) continue;
    const R = Math.max(3, (fire.glow ?? 9) * view.pxPerUnit(p.depth) * fl.k); const al = 0.30 * Math.min(1, fl.k) * (fire.glowA ?? 1);
    const gr = g.createRadialGradient(p.x, p.y, 0, p.x, p.y, R); gr.addColorStop(0, `rgba(255,170,70,${al})`); gr.addColorStop(0.4, `rgba(230,110,40,${al * 0.45})`); gr.addColorStop(1, 'rgba(200,80,30,0)'); g.fillStyle = gr; g.fillRect(p.x - R, p.y - R, R * 2, R * 2); }
  g.restore();
}
