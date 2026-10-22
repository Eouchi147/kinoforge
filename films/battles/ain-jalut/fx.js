// Ain Jalut: film-side effects installed on top of the Battle Map engine (no engine fork).
//  - spec.ink: territory that spreads over the ground like ink. One item = { at, spread, team colour, origin:[x,z], blobs:[[x,z,r],...] }.
//    The blobs are baked into a canvas (outline then fill, so overlaps stay one flat colour), draped on the terrain as one mesh under the blocks.
//  - spec.bar: a timeline bar that grows across the lower third (the Mamluks' 250+ years).
// Pure functions of t, so every frame is reproducible.
import * as THREE from 'three';
import { Stage } from '/films/lib/battlemap/stage.js';
import { StageOverlay, drawOutlined } from '/films/lib/battlemap/overlay.js';
import { clamp, hash01 } from '/films/lib/battlemap/noise.js';
import { EASE } from '/films/lib/battlemap/timeline.js';

const K = 1.45; // canvas pixels per map unit for the ink layer

function buildInk(stage) {
  const W = stage.world.W, D = stage.world.D, items = stage.spec.ink || []; if (!items.length) return null;
  const clock = stage.clock; const cw = Math.round(W * K), ch = Math.round(D * K);
  const canvas = document.createElement('canvas'); canvas.width = cw; canvas.height = ch; const scratch = document.createElement('canvas'); scratch.width = cw; scratch.height = ch;
  const tex = new THREE.CanvasTexture(canvas); tex.colorSpace = THREE.SRGBColorSpace; tex.generateMipmaps = false; tex.minFilter = THREE.LinearFilter;
  // a grid draped on the terrain, 6 map units per cell
  const step = 6; const nx = Math.ceil(W / step), nz = Math.ceil(D / step); const pos = new Float32Array((nx + 1) * (nz + 1) * 3), uv = new Float32Array((nx + 1) * (nz + 1) * 2), idx = [];
  for (let j = 0; j <= nz; j++) for (let i = 0; i <= nx; i++) { const x = -W / 2 + (i / nx) * W, z = -D / 2 + (j / nz) * D; const p = j * (nx + 1) + i; pos[p * 3] = x; pos[p * 3 + 1] = stage.mh(x, z) + 0.45; pos[p * 3 + 2] = z; uv[p * 2] = i / nx; uv[p * 2 + 1] = 1 - j / nz; if (i < nx && j < nz) { const a = p, b = p + 1, c = p + nx + 1, d = c + 1; idx.push(a, c, b, b, c, d); } }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); geo.setIndex(idx);
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, toneMapped: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
  const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false; mesh.renderOrder = 2; stage.scene.add(mesh);
  const prep = items.map((it) => { const t0 = clock.at(it.at); const o = it.origin || [0, 0]; const dmax = Math.max(1, ...it.blobs.map((b) => Math.hypot(b[0] - o[0], b[1] - o[1])));
    return { ...it, t0, t1: it.until !== undefined ? clock.at(it.until) : Infinity, dmax, o, bl: it.blobs.map((b, n) => ({ x: b[0], z: b[1], r: b[2], d: Math.hypot(b[0] - o[0], b[1] - o[1]) / dmax, n })) }; });
  const g = canvas.getContext('2d'), s = scratch.getContext('2d'); let last = '';
  const poly = (c, b, R) => { c.beginPath(); const N = 40; for (let a = 0; a <= N; a++) { const th = a / N * Math.PI * 2; const w = 1 + 0.16 * Math.sin(th * 3 + b.n * 1.9) + 0.09 * Math.sin(th * 5 + b.n * 4.1) + 0.05 * Math.sin(th * 9 + b.n); const x = (b.x + Math.cos(th) * R * w + W / 2) * K, y = (b.z + Math.sin(th) * R * w * 0.92 + D / 2) * K; a ? c.lineTo(x, y) : c.moveTo(x, y); } c.closePath(); };
  return { mesh, update(t) {
    const rs = []; for (const it of prep) { const fade = it.t1 === Infinity ? 1 : 1 - clamp((t - it.t1) / (it.fadeOut ?? 0.8)); for (const b of it.bl) { const tb = it.t0 + (it.spread ?? 3) * b.d; const u = clamp((t - tb) / (it.grow ?? 0.9)); rs.push(Math.round(EASE.outQuad(u) * b.r * 10) / 10, Math.round(fade * 100)); } }
    mesh.visible = rs.some((v, i) => i % 2 === 0 && v > 0);
    const key = rs.join(','); if (key === last) return; last = key;
    g.clearRect(0, 0, cw, ch); let k = 0;
    for (const it of prep) { const col = it.color || [0.14, 0.34, 0.86], dark = it.dark || [0.04, 0.09, 0.3]; const css = (c) => `rgb(${Math.round(c[0] * 255)},${Math.round(c[1] * 255)},${Math.round(c[2] * 255)})`;
      s.clearRect(0, 0, cw, ch); s.lineJoin = 'round'; let any = false; const R = []; for (const b of it.bl) { R.push(rs[k]); k += 2; }
      const fade = rs[k - 1] / 100;
      for (let pass = 0; pass < 2; pass++) it.bl.forEach((b, i) => { if (R[i] <= 0.3) return; any = true; poly(s, b, R[i]); if (pass === 0) { s.lineWidth = 5.5; s.strokeStyle = css(dark); s.stroke(); } s.fillStyle = css(col); s.fill(); });
      if (any) { g.globalAlpha = (it.alpha ?? 0.6) * fade; g.drawImage(scratch, 0, 0); g.globalAlpha = 1; } }
    tex.needsUpdate = true; } };
}

export function installFx() {
  const upd0 = Stage.prototype.update;
  Stage.prototype.update = function (t, pose) { if (this._ink === undefined) this._ink = buildInk(this); if (this._ink) this._ink.update(t); return upd0.call(this, t, pose); };
  const draw0 = StageOverlay.prototype.draw;
  StageOverlay.prototype.draw = function (g, t, view) {
    draw0.call(this, g, t, view);
    const bars = this.stage.spec.bar; if (bars && bars.length) { if (!this._bar) this._bar = bars.map((b) => ({ ...b, t0: this.clock.at(b.at), t1: this.clock.at(b.until), tg: this.clock.at(b.growEnd), te: b.endAt !== undefined ? this.clock.at(b.endAt) : undefined })); for (const b of this._bar) if (t >= b.t0 && t < b.t1 + 0.5) drawBar(g, t, view.rect, b); }
  };
}

function drawBar(g, t, r, b) {
  const a = clamp((t - b.t0) / 0.35) * (1 - clamp((t - b.t1) / 0.5)); if (a <= 0.01) return; const H = r.h, W = r.w; const x0 = r.x + W * 0.12, x1 = r.x + W * 0.88, y = r.y + H * (b.y ?? 0.84), bh = H * 0.052;
  const u = EASE.inOut(clamp((t - b.t0 - 0.3) / Math.max(0.1, b.tg - b.t0 - 0.3))); const xe = x0 + (x1 - x0) * u;
  g.save(); g.globalAlpha = a; g.shadowColor = 'rgba(25,12,4,0.5)'; g.shadowBlur = H * 0.02; g.shadowOffsetY = H * 0.008; g.beginPath(); g.roundRect(x0 - 6, y - 6, x1 - x0 + 12, bh + 12, bh * 0.5); g.fillStyle = 'rgba(246,236,208,0.95)'; g.fill(); g.shadowColor = 'transparent'; g.lineWidth = 3; g.strokeStyle = '#2a190e'; g.stroke();
  if (xe > x0 + 2) { g.save(); g.beginPath(); g.roundRect(x0, y, x1 - x0, bh, bh * 0.5); g.clip(); const gr = g.createLinearGradient(x0, 0, x1, 0); gr.addColorStop(0, '#c52a2a'); gr.addColorStop(1, '#e8a02e'); g.fillStyle = gr; g.fillRect(x0, y, xe - x0, bh); g.restore(); }
  g.lineWidth = 2; g.strokeStyle = 'rgba(42,25,14,0.75)'; for (let k = 1; k < 5; k++) { const x = x0 + (x1 - x0) * k / 5; g.beginPath(); g.moveTo(x, y + bh * 0.12); g.lineTo(x, y + bh * 0.88); g.stroke(); }
  drawOutlined(g, b.startText || '1260', x0, y - H * 0.022, H * 0.044, { weight: 800 });
  if (b.te !== undefined && t >= b.te) { const age = t - b.te; const sc = 0.6 + 0.4 * EASE.outBack(clamp(age / 0.4)); g.save(); g.translate(x1, y - H * 0.022); g.scale(sc, sc); drawOutlined(g, b.endText, 0, 0, H * 0.056, { weight: 800, color: '#ffe08a' }); g.restore(); }
  g.restore();
}
