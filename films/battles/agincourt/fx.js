// Agincourt: film-side overlay effects, installed on top of the Battle Map engine without changing it:
//  - rain: slanted streaks over the whole frame between two cue times (spec.rain = [{ at, until, density, fadeIn, fadeOut }])
// Pure functions of t (hash based), so every frame is reproducible.
import { StageOverlay } from '/films/lib/battlemap/overlay.js';
import { clamp, hash01 } from '/films/lib/battlemap/noise.js';

export function installFx() {
  const draw0 = StageOverlay.prototype.draw;
  StageOverlay.prototype.draw = function (g, t, view) {
    const rains = this.stage.spec.rain; if (rains && rains.length) {
      if (!this._rain) this._rain = rains.map((r) => { const t0 = this.clock.at(r.at), t1 = this.clock.at(r.until); return { ...r, t0, t1 }; });
      for (const r of this._rain) { const a = clamp((t - r.t0) / (r.fadeIn ?? 0.8)) * (1 - clamp((t - r.t1) / (r.fadeOut ?? 0.8))); if (a > 0.01) drawRain(g, t, view.rect, a, r.density ?? 1, r.tilt ?? 0.22); }
    }
    draw0.call(this, g, t, view);
  };
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
