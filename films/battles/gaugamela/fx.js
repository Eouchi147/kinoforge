// Gaugamela: one film-side map graphic, installed over the Battle Map engine without changing it.
//  - spec.zones: [{ y, rgb, alpha, p, keys: [{ t, c: [x, z], rx, rz }] }]  a territory (rounded shape, fine hatching, inked edge)
//    laid on the map that grows between keys: the Persian Empire passing to Alexander, then his empire from Greece to India.
// A pure function of t, so every frame is reproducible.
import { StageOverlay } from '/films/lib/battlemap/overlay.js';
import { clamp } from '/films/lib/battlemap/noise.js';

export function installFx() {
  const draw0 = StageOverlay.prototype.draw;
  StageOverlay.prototype.draw = function (g, t, view) {
    const sp = this.stage.spec;
    if (sp.zones && sp.zones.length) {
      if (!this._zones) this._zones = sp.zones.map((e) => ({ ...e, keys: e.keys.map((k) => ({ ...k, tt: this.clock.at(k.t) })) }));
      for (const e of this._zones) drawZone(g, t, view, e);
    }
    draw0.call(this, g, t, view);
  };
}

const ease = (u) => u * u * (3 - 2 * u);
function drawZone(g, t, view, e) {
  const K = e.keys; if (t < K[0].tt) return; let a = K[0], b = K[0], u = 0;
  for (let i = 0; i < K.length - 1; i++) { if (t >= K[i].tt) { a = K[i]; b = K[i + 1]; u = clamp((t - a.tt) / Math.max(1e-3, b.tt - a.tt)); } }
  if (t >= K[K.length - 1].tt) { a = b = K[K.length - 1]; u = 1; }
  const w = ease(u); const c = [a.c[0] + (b.c[0] - a.c[0]) * w, a.c[1] + (b.c[1] - a.c[1]) * w]; const rx = a.rx + (b.rx - a.rx) * w, rz = a.rz + (b.rz - a.rz) * w; if (rx < 1) return;
  const p = e.p ?? 3, N = 72; const pts = []; for (let i = 0; i < N; i++) { const th = i / N * Math.PI * 2; const cs = Math.cos(th), sn = Math.sin(th); pts.push(view.project(c[0] + rx * Math.sign(cs) * Math.pow(Math.abs(cs), 2 / p), e.y ?? 3, c[1] + rz * Math.sign(sn) * Math.pow(Math.abs(sn), 2 / p))); }
  if (pts.some((q) => !(q.depth > 1))) return;
  const r = view.rect; const rgb = e.rgb || [189, 31, 31]; const al = (e.alpha ?? 0.3) * clamp((t - K[0].tt) / 0.5);
  const path = () => { g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q.x, q.y) : g.moveTo(q.x, q.y))); g.closePath(); };
  g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip();
  path(); g.fillStyle = `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${al})`; g.fill();
  g.save(); path(); g.clip(); g.strokeStyle = `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${al * 0.9})`; g.lineWidth = Math.max(1, r.h * 0.0016); const sp = r.h * 0.016; g.beginPath(); for (let x = -r.h; x < r.w + r.h; x += sp) { g.moveTo(r.x + x, r.y + r.h); g.lineTo(r.x + x + r.h * 0.6, r.y); } g.stroke(); g.restore();
  path(); g.lineJoin = 'round'; g.lineWidth = Math.max(3, r.h * 0.0055); g.strokeStyle = 'rgba(244,234,210,0.85)'; g.stroke(); g.lineWidth = Math.max(1.4, r.h * 0.0024); g.strokeStyle = `rgba(${Math.round(rgb[0] * 0.7)},${Math.round(rgb[1] * 0.7)},${Math.round(rgb[2] * 0.7)},${Math.min(1, al * 3)})`; g.stroke();
  g.restore();
}
