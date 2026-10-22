// Gaugamela: film-side overlay effects, installed on top of the Battle Map engine without changing it.
//  - spec.sheen: [{ at, until, center:[x,z], rx, rz, y, alpha }]  a glossy "smoothed flat" shimmer laid on an ellipse of ground
//  - spec.zones: [{ y, rgb, alpha, p, keys:[{ t, c:[x,z], rx, rz }] }]  a territory (rounded blob) laid on the map that grows between keys (the empire)
//  - spec.glows: [{ at, until, pos:[x,z], y, r, rgb:[r,g,b] }]     a pulsing golden glow (the gap), r in map units
// Pure functions of t, so every frame is reproducible.
import { StageOverlay } from '/films/lib/battlemap/overlay.js';
import { clamp } from '/films/lib/battlemap/noise.js';

export function installFx() {
  const draw0 = StageOverlay.prototype.draw;
  StageOverlay.prototype.draw = function (g, t, view) {
    const sp = this.stage.spec;
    if (sp.sheen && sp.sheen.length) {
      if (!this._sheen) this._sheen = sp.sheen.map((e) => ({ ...e, t0: this.clock.at(e.at), t1: this.clock.at(e.until) }));
      for (const e of this._sheen) { const a = clamp((t - e.t0) / (e.fadeIn ?? 0.6)) * (1 - clamp((t - e.t1) / (e.fadeOut ?? 0.8))); if (a > 0.01) drawSheen(g, t, view, e, a); }
    }
    if (sp.zones && sp.zones.length) {
      if (!this._zones) this._zones = sp.zones.map((e) => ({ ...e, keys: e.keys.map((k) => ({ ...k, tt: this.clock.at(k.t) })) }));
      for (const e of this._zones) drawZone(g, t, view, e);
    }
    if (sp.glows && sp.glows.length) {
      if (!this._glows) this._glows = sp.glows.map((e) => ({ ...e, t0: this.clock.at(e.at), t1: this.clock.at(e.until) }));
      for (const e of this._glows) { const a = clamp((t - e.t0) / (e.fadeIn ?? 0.4)) * (1 - clamp((t - e.t1) / (e.fadeOut ?? 0.6))); if (a > 0.01) drawGlow(g, t, view, e, a); }
    }
    draw0.call(this, g, t, view);
  };
}

function drawSheen(g, t, view, e, a) {
  const N = 48; const pts = []; for (let i = 0; i < N; i++) { const th = i / N * Math.PI * 2; pts.push(view.project(e.center[0] + Math.cos(th) * e.rx, e.y ?? 11, e.center[1] + Math.sin(th) * e.rz)); }
  if (pts.some((p) => !(p.depth > 1))) return;
  let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; for (const p of pts) { x0 = Math.min(x0, p.x); x1 = Math.max(x1, p.x); y0 = Math.min(y0, p.y); y1 = Math.max(y1, p.y); }
  const r = view.rect; g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip();
  g.beginPath(); pts.forEach((p, i) => (i ? g.lineTo(p.x, p.y) : g.moveTo(p.x, p.y))); g.closePath();
  g.save(); g.clip(); g.globalAlpha = a * (e.alpha ?? 1);
  g.fillStyle = 'rgba(255,248,214,0.20)'; g.fillRect(x0, y0, x1 - x0, y1 - y0);
  const W = x1 - x0, H = y1 - y0; const cyc = ((t * 0.42) % 1.6) - 0.3; // a bright diagonal glint sweeping across, again and again
  for (let k = 0; k < 2; k++) { const u = cyc - k * 0.8; const cx = x0 + W * u; const gr = g.createLinearGradient(cx - W * 0.14, y0, cx + W * 0.14 + H * 0.3, y1);
    gr.addColorStop(0, 'rgba(255,255,240,0)'); gr.addColorStop(0.5, 'rgba(255,255,244,0.62)'); gr.addColorStop(1, 'rgba(255,255,240,0)'); g.fillStyle = gr; g.fillRect(x0, y0, W, H); }
  g.restore();
  g.globalAlpha = a * (e.alpha ?? 1); g.setLineDash([Math.max(8, view.rect.h * 0.016), Math.max(6, view.rect.h * 0.012)]); g.lineWidth = Math.max(2.5, view.rect.h * 0.0046); g.strokeStyle = 'rgba(255,250,226,0.92)';
  g.beginPath(); pts.forEach((p, i) => (i ? g.lineTo(p.x, p.y) : g.moveTo(p.x, p.y))); g.closePath(); g.stroke();
  g.restore();
}

function drawGlow(g, t, view, e, a) {
  const p = view.project(e.pos[0], e.y ?? 4, e.pos[1]); if (!(p.depth > 1)) return; const ppu = view.pxPerUnit(p.depth);
  const pulse = 0.82 + 0.18 * Math.sin(t * 7); const R = e.r * ppu * pulse; const c = e.rgb || [255, 214, 80]; const r = view.rect;
  g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip(); g.globalCompositeOperation = 'lighter';
  const gr = g.createRadialGradient(p.x, p.y, 0, p.x, p.y, R); gr.addColorStop(0, `rgba(${c[0]},${c[1]},${c[2]},${0.95 * a})`); gr.addColorStop(0.45, `rgba(${c[0]},${c[1]},${c[2]},${0.45 * a})`); gr.addColorStop(1, `rgba(${c[0]},${c[1]},${c[2]},0)`);
  g.fillStyle = gr; g.beginPath(); g.ellipse(p.x, p.y, R, R * (e.squash ?? 0.62), 0, 0, Math.PI * 2); g.fill();
  g.globalCompositeOperation = 'source-over'; g.globalAlpha = a; g.lineWidth = Math.max(3, r.h * 0.006); g.strokeStyle = 'rgba(255,236,150,0.95)'; g.setLineDash([r.h * 0.012, r.h * 0.01]); g.lineDashOffset = -t * 40; g.beginPath(); g.ellipse(p.x, p.y, R * 0.72, R * 0.72 * (e.squash ?? 0.62), 0, 0, Math.PI * 2); g.stroke();
  g.restore();
}

const ease = (u) => u * u * (3 - 2 * u);
function drawZone(g, t, view, e) {
  const K = e.keys; if (t < K[0].tt) return; let a = K[0], b = K[0], u = 0;
  for (let i = 0; i < K.length - 1; i++) { if (t >= K[i].tt) { a = K[i]; b = K[i + 1]; u = clamp((t - a.tt) / Math.max(1e-3, b.tt - a.tt)); } }
  if (t >= K[K.length - 1].tt) { a = b = K[K.length - 1]; u = 1; }
  const w = ease(u); const c = [a.c[0] + (b.c[0] - a.c[0]) * w, a.c[1] + (b.c[1] - a.c[1]) * w]; const rx = a.rx + (b.rx - a.rx) * w, rz = a.rz + (b.rz - a.rz) * w; if (rx < 1) return;
  const p = e.p ?? 3, N = 64; const pts = []; for (let i = 0; i < N; i++) { const th = i / N * Math.PI * 2; const cs = Math.cos(th), sn = Math.sin(th); pts.push(view.project(c[0] + rx * Math.sign(cs) * Math.pow(Math.abs(cs), 2 / p), e.y ?? 3, c[1] + rz * Math.sign(sn) * Math.pow(Math.abs(sn), 2 / p))); }
  if (pts.some((q) => !(q.depth > 1))) return;
  const r = view.rect; const rgb = e.rgb || [214, 40, 40]; const al = (e.alpha ?? 0.4) * clamp((t - K[0].tt) / 0.3);
  g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip(); g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q.x, q.y) : g.moveTo(q.x, q.y))); g.closePath();
  g.fillStyle = `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${al})`; g.fill();
  g.save(); g.clip(); g.strokeStyle = `rgba(255,236,200,${al * 0.55})`; g.lineWidth = Math.max(2, r.h * 0.004); const sp = r.h * 0.03; g.beginPath(); for (let x = -r.h; x < r.w + r.h; x += sp) { g.moveTo(r.x + x, r.y + r.h); g.lineTo(r.x + x + r.h * 0.6, r.y); } g.stroke(); g.restore();
  g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q.x, q.y) : g.moveTo(q.x, q.y))); g.closePath();
  g.lineJoin = 'round'; g.lineWidth = Math.max(5, r.h * 0.011); g.strokeStyle = 'rgba(42,25,14,0.9)'; g.stroke(); g.lineWidth = Math.max(2.5, r.h * 0.0052); g.strokeStyle = 'rgba(255,232,170,0.95)'; g.stroke();
  g.restore();
}
