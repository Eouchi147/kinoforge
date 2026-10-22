// Thermopylae: film-side overlay effects, installed on top of the Battle Map engine without changing it.
//  - spec.dim:     a veil over the whole frame between two cue times ({ at, until, alpha, color:[r,g,b], stars, fadeIn, fadeOut }): the arrows block the sun, the night climb
//  - spec.regions: a shaded, hatched area drawn on the ground ({ at, until, poly, color:[r,g,b], sweep:{ at, until } }): the Persian Empire grows from Egypt to India
//  - spec.nums:    a big number plate on the screen that follows keyframes ({ keys:[[time, value], ...], plusAt, tag, suffix }): "millions" crashing down to "100,000+"
// Pure functions of t (hash based), so every frame is reproducible.
import { StageOverlay } from '/films/lib/battlemap/overlay.js';
import { clamp, lerp, hash01 } from '/films/lib/battlemap/noise.js';

const INK = '#2a190e';
const rgbs = (c, a = 1) => `rgba(${Math.round(c[0] * 255)},${Math.round(c[1] * 255)},${Math.round(c[2] * 255)},${a})`;

export function installFx() {
  const draw0 = StageOverlay.prototype.draw;
  StageOverlay.prototype.draw = function (g, t, view) {
    const sp = this.stage.spec;
    const regs = sp.regions; if (regs && regs.length) {
      if (!this._reg) this._reg = regs.map((r) => ({ ...r, t0: this.clock.at(r.at), t1: this.clock.at(r.until), s0: r.sweep ? this.clock.at(r.sweep.at) : 0, s1: r.sweep ? this.clock.at(r.sweep.until) : 0 }));
      for (const r of this._reg) { const a = clamp((t - r.t0) / (r.fadeIn ?? 0.4)) * (1 - clamp((t - r.t1) / (r.fadeOut ?? 0.5))); if (a > 0.01) drawRegion(g, t, view, this.stage, r, a); }
    }
    const dims = sp.dim; if (dims && dims.length) {
      if (!this._dim) this._dim = dims.map((d) => ({ ...d, t0: this.clock.at(d.at), t1: this.clock.at(d.until) }));
      for (const d of this._dim) { const a = clamp((t - d.t0) / (d.fadeIn ?? 0.5)) * (1 - clamp((t - d.t1) / (d.fadeOut ?? 0.5))); if (a > 0.005) drawDim(g, t, view.rect, a, d); }
    }
    draw0.call(this, g, t, view);
    const nums = sp.nums; if (nums && nums.length) {
      if (!this._nums) this._nums = nums.map((n) => ({ ...n, t0: this.clock.at(n.at), t1: this.clock.at(n.until), keys: n.keys.map(([tt, v]) => [this.clock.at(tt), v]), plusT: n.plusAt !== undefined ? this.clock.at(n.plusAt) : Infinity }));
      for (const n of this._nums) if (t >= n.t0 && t < n.t1 + 0.4) drawNum(g, t, view.rect, n);
    }
  };
}

function drawDim(g, t, r, a, d) { // a soft veil over the map; optional stars for the night
  g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip();
  const c = d.color || [0.055, 0.03, 0.012]; g.globalAlpha = a * (d.alpha ?? 0.5); g.fillStyle = rgbs(c); g.fillRect(r.x, r.y, r.w, r.h); g.globalAlpha = a;
  if (d.stars) { for (let i = 0; i < 70; i++) { const x = r.x + hash01(i, 1) * r.w, y = r.y + hash01(i, 2) * r.h * 0.5; const tw = 0.55 + 0.45 * Math.sin(t * (1.5 + hash01(i, 3) * 2) + i); const s = (0.8 + hash01(i, 4) * 1.6) * r.h / 720;
      g.globalAlpha = a * tw * 0.9; g.fillStyle = '#fff6d8'; g.fillRect(x - s, y - s * 0.4, s * 2, s * 0.8); g.fillRect(x - s * 0.4, y - s, s * 0.8, s * 2); } }
  g.restore();
}

function clipHalf(poly, xl) { // Sutherland-Hodgman against x <= xl
  const out = []; for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length]; const ain = a[0] <= xl, bin = b[0] <= xl;
    if (ain) out.push(a); if (ain !== bin) { const u = (xl - a[0]) / (b[0] - a[0]); out.push([xl, a[1] + (b[1] - a[1]) * u]); } } return out;
}
function densify(poly, step) { const out = []; for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length]; const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / step)); for (let k = 0; k < n; k++) out.push([lerp(a[0], b[0], k / n), lerp(a[1], b[1], k / n)]); } return out; }

function drawRegion(g, t, view, stage, r, a) {
  if (!r._dense) { r._dense = densify(r.poly, r.step ?? 14); r._x0 = Math.min(...r._dense.map((p) => p[0])); r._x1 = Math.max(...r._dense.map((p) => p[0])); r._holes = (r.holes || []).map((h) => densify(h, r.step ?? 14)); }
  let poly = r._dense; if (r.sweep) { const u = clamp((t - r.s0) / Math.max(0.01, r.s1 - r.s0)); const e = u * u * (3 - 2 * u); if (u <= 0) return; if (u < 1) poly = clipHalf(poly, lerp(r._x0, r._x1, e)); }
  if (poly.length < 3) return; const R = view.rect; const H = R.h; const col = r.color || [0.8, 0.12, 0.12];
  const path = (c, pl) => { const pts = pl.map(([x, z]) => view.project(x, stage.mh(x, z) + 0.6, z)); c.beginPath(); pts.forEach((p, i) => (i ? c.lineTo(p.x - R.x, p.y - R.y) : c.moveTo(p.x - R.x, p.y - R.y))); c.closePath(); };
  if (!drawRegion.cv) drawRegion.cv = document.createElement('canvas'); const cv = drawRegion.cv; if (cv.width !== Math.round(R.w) || cv.height !== Math.round(R.h)) { cv.width = Math.round(R.w); cv.height = Math.round(R.h); }
  const c = cv.getContext('2d'); c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, cv.width, cv.height); c.globalCompositeOperation = 'source-over'; c.lineJoin = 'round';
  path(c, poly); c.globalAlpha = r.alpha ?? 0.32; c.fillStyle = rgbs(col); c.fill();
  c.save(); path(c, poly); c.clip(); c.globalAlpha = 0.34; c.strokeStyle = rgbs([col[0] * 0.5, col[1] * 0.5, col[2] * 0.5]); c.lineWidth = Math.max(1.2, H * 0.0028); const sp = H * 0.022; c.beginPath();
  for (let k = -R.h; k < R.w + R.h; k += sp) { c.moveTo(k, 0); c.lineTo(k - R.h, R.h); } c.stroke(); c.restore();
  if (!r._holes.length) { path(c, poly); c.globalAlpha = 0.95; c.lineWidth = Math.max(3, H * 0.0075); c.strokeStyle = 'rgba(34,14,8,0.9)'; c.stroke(); c.lineWidth = Math.max(1.6, H * 0.0032); c.strokeStyle = rgbs([Math.min(1, col[0] + 0.15), Math.min(1, col[1] + 0.2), Math.min(1, col[2] + 0.2)]); c.stroke(); }
  else { c.globalCompositeOperation = 'destination-out'; c.globalAlpha = 1; c.fillStyle = '#000'; for (const h of r._holes) { path(c, h); c.fill(); } }
  g.save(); g.beginPath(); g.rect(R.x, R.y, R.w, R.h); g.clip(); g.globalAlpha = a; g.drawImage(cv, R.x, R.y); g.restore();
}

function numAt(n, t) { // value on the keyframes (ease out between keys)
  const K = n.keys; if (t <= K[0][0]) return K[0][1]; for (let i = 0; i < K.length - 1; i++) { if (t < K[i + 1][0]) { const u = clamp((t - K[i][0]) / Math.max(1e-6, K[i + 1][0] - K[i][0])); const e = 1 - Math.pow(1 - u, 3); return lerp(K[i][1], K[i + 1][1], e); } } return K[K.length - 1][1];
}
function drawNum(g, t, rect, n) {
  const H = rect.h; const a = clamp((t - n.t0) / 0.18) * (isFinite(n.t1) ? 1 - clamp((t - n.t1) / 0.35) : 1); if (a <= 0.01) return;
  const size = (n.size ?? 1) * H * 0.052; const age = t - n.t0; const c1 = 1.70158, c3 = c1 + 1; const x = clamp(age / 0.36); const sc = 0.55 + 0.45 * (1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2));
  const px = rect.x + n.screen[0] * rect.w, py = rect.y + n.screen[1] * rect.h; const step = n.step ?? 1000; const val = Math.round(numAt(n, t) / step) * step; const txt = val.toLocaleString('en-US') + (t >= n.plusT ? '+' : '');
  const team = n.col || [0.3, 0.2, 0.1]; const tagCol = n.tagCol || [0.98, 0.84, 0.46];
  g.save(); g.globalAlpha = a; g.translate(px, py); g.scale(sc, sc); g.translate(-px, -py);
  g.font = `800 ${size * 1.5}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.06) + 'px'; const nw = g.measureText(txt).width; g.font = `600 ${size * 0.62}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.18) + 'px'; const sw = Math.max(g.measureText(n.suffix || '').width, g.measureText(n.tag || '').width);
  const w = Math.max(nw, sw) + size * 1.6, h = size * (n.tag ? 3.6 : 2.9); const x0 = px - w / 2, y0 = py - h;
  g.shadowColor = 'rgba(25,12,4,0.5)'; g.shadowBlur = size * 0.5; g.shadowOffsetY = size * 0.2; g.beginPath(); g.roundRect(x0, y0, w, h, size * 0.34); g.fillStyle = rgbs(team, 0.93); g.fill(); g.shadowColor = 'transparent';
  g.lineWidth = Math.max(2.4, size * 0.1); g.strokeStyle = '#f6ecd0'; g.stroke(); g.beginPath(); g.roundRect(x0 + size * 0.14, y0 + size * 0.14, w - size * 0.28, h - size * 0.28, size * 0.22); g.lineWidth = 1; g.strokeStyle = 'rgba(246,236,208,0.4)'; g.stroke();
  g.textAlign = 'center'; g.textBaseline = 'alphabetic'; let yy = y0;
  if (n.tag) { g.font = `600 ${size * 0.62}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.18) + 'px'; g.fillStyle = rgbs(tagCol); g.fillText(n.tag, px, yy + size * 0.98); yy += size * 0.7; }
  g.font = `800 ${size * 1.5}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.06) + 'px'; g.fillStyle = '#fff3d2'; g.fillText(txt, px, yy + size * 1.66);
  if (n.suffix) { g.font = `600 ${size * 0.62}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.18) + 'px'; g.fillStyle = rgbs(tagCol); g.fillText(n.suffix, px, yy + size * 2.3); }
  g.restore();
}
