// Agincourt: film-side overlay effects, installed on top of the Battle Map engine without changing it.
//  - rain: slanted streaks over the whole frame between two cue times (spec.rain = [{ at, until, density, fadeIn, fadeOut }])
//  - teams: extra colours for blocks and plates (stakes, mud)
// Pure functions of t (hash based), so every frame is reproducible.
import { StageOverlay } from '/films/lib/battlemap/overlay.js';
import { TEAMS } from '/films/lib/battlemap/blocks.js';
import { clamp, hash01 } from '/films/lib/battlemap/noise.js';

export function installFx() {
  TEAMS.wood = { top: [0.62, 0.42, 0.22], side: [0.30, 0.18, 0.08], dot: [0.30, 0.18, 0.08], light: [0.85, 0.64, 0.38], ink: [0.15, 0.09, 0.04], trim: [0.98, 0.84, 0.46] };
  const draw0 = StageOverlay.prototype.draw;
  StageOverlay.prototype.draw = function (g, t, view) {
    const rains = this.stage.spec.rain; if (rains && rains.length) {
      if (!this._rain) this._rain = rains.map((r) => { const t0 = this.clock.at(r.at), t1 = this.clock.at(r.until); return { ...r, t0, t1 }; });
      for (const r of this._rain) { const a = clamp((t - r.t0) / (r.fadeIn ?? 0.8)) * (1 - clamp((t - r.t1) / (r.fadeOut ?? 0.8))); if (a > 0.01) drawRain(g, t, view.rect, a, r.density ?? 1, r.tilt ?? 0.22); }
    }
    const dims = this.stage.spec.dim; if (dims && dims.length) {
      if (!this._dim) this._dim = dims.map((d) => ({ ...d, t0: this.clock.at(d.at), t1: this.clock.at(d.until) }));
      for (const d of this._dim) { const a = clamp((t - d.t0) / (d.fadeIn ?? 0.5)) * (1 - clamp((t - d.t1) / (d.fadeOut ?? 0.5))); if (a > 0.005) drawDim(g, t, view.rect, a, d); }
    }
    draw0.call(this, g, t, view);
  };
}

function drawDim(g, t, r, a, d) { // a soft dark veil over the map; optional theatre curtains for the playbill
  g.save(); g.beginPath(); g.rect(r.x, r.y, r.w, r.h); g.clip(); g.globalAlpha = a * d.alpha; g.fillStyle = 'rgb(14,7,3)'; g.fillRect(r.x, r.y, r.w, r.h); g.globalAlpha = a;
  if (d.curtains) {
    const w = r.w * 0.15; const sway = Math.sin(t * 1.3) * 2;
    for (const side of [0, 1]) {
      const x0 = side ? r.x + r.w - w : r.x; const gr = g.createLinearGradient(x0, 0, x0 + w, 0);
      if (side) { gr.addColorStop(0, '#8c1a26'); gr.addColorStop(1, '#3a0810'); } else { gr.addColorStop(0, '#3a0810'); gr.addColorStop(1, '#8c1a26'); }
      g.fillStyle = gr; g.beginPath(); g.moveTo(x0, r.y); g.lineTo(x0 + w, r.y);
      g.bezierCurveTo(x0 + w + (side ? -8 : 8) + sway, r.y + r.h * 0.3, x0 + w + (side ? 10 : -10), r.y + r.h * 0.7, x0 + w + (side ? 4 : -4), r.y + r.h); g.lineTo(x0, r.y + r.h); g.closePath(); g.fill();
      g.strokeStyle = 'rgba(20,4,8,0.55)'; g.lineWidth = Math.max(2, r.h * 0.006);
      for (let k = 1; k < 7; k++) { const fx = x0 + w * k / 7 + Math.sin(k * 1.7 + t * 0.8) * 1.5; g.beginPath(); g.moveTo(fx, r.y); g.lineTo(fx + (side ? -3 : 3), r.y + r.h); g.stroke(); }
      g.strokeStyle = 'rgba(244,214,130,0.9)'; g.lineWidth = Math.max(2, r.h * 0.006); const ex = side ? x0 + 3 : x0 + w - 3; g.beginPath(); g.moveTo(ex, r.y); g.lineTo(ex + (side ? 4 : -4), r.y + r.h); g.stroke();
    }
    const vh = r.h * 0.07; g.fillStyle = '#7a1420'; g.beginPath(); g.moveTo(r.x, r.y); g.lineTo(r.x + r.w, r.y); g.lineTo(r.x + r.w, r.y + vh * 0.7);
    const n = 9; for (let k = n; k >= 0; k--) { const x = r.x + r.w * k / n; const xm = r.x + r.w * (k - 0.5) / n; if (k < n) g.quadraticCurveTo(xm, r.y + vh * 1.5, x, r.y + vh * 0.7); }
    g.closePath(); g.fill(); g.strokeStyle = 'rgba(244,214,130,0.9)'; g.lineWidth = Math.max(2, r.h * 0.006); g.stroke();
  }
  g.restore();
}

function drawRain(g, t, rect, a, density, tilt) {
  const n = Math.round(150 * density); const H = rect.h, W = rect.w; g.save(); g.beginPath(); g.rect(rect.x, rect.y, W, H); g.clip(); g.lineCap = 'round';
  const len = H * 0.05;
  for (let pass = 0; pass < 2; pass++) {
    g.beginPath();
    for (let i = 0; i < n; i++) {
      const sp = 1.15 + hash01(i, 2) * 0.7; const ph = hash01(i, 3); const u = ((ph + t * sp * 0.9) % 1.15) - 0.075; const y = rect.y + u * H * 1.0 - len; const x = rect.x + hash01(i, 1) * W * 1.15 + H * tilt * 0.4;
      const xx = x - (u * H) * tilt; g.moveTo(xx, y); g.lineTo(xx - len * tilt, y + len);
    }
    if (pass === 0) { g.globalAlpha = a * 0.5; g.lineWidth = Math.max(2.4, H * 0.0042); g.strokeStyle = 'rgba(28,38,56,1)'; } else { g.globalAlpha = a * 0.9; g.lineWidth = Math.max(1.2, H * 0.0018); g.strokeStyle = 'rgba(224,236,248,1)'; }
    g.stroke();
  }
  g.restore();
}
