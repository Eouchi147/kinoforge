// Battle Map engine: 2D overlay drawn on top of the picture: names that pop in at a narration word, soldier counters, icons, arrow volleys, title and end cards.
// Everything is projected from 3D anchors on the map (so it follows the camera) and set in code. No em or en dashes, no "..." on screen.
import * as THREE from 'three';
import { clamp, lerp, hash01 } from './noise.js';
import { EASE } from './timeline.js';
import { drawIcon } from './icons.js';
import { TEAMS } from './blocks.js';

const INK = '#2a190e', CREAM = '#f6ecd0';
const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const _v = new THREE.Vector3();

export class View { // a camera + a pixel rectangle on the output
  constructor(camera, rect) { this.camera = camera; this.rect = rect; }
  project(x, y, z) { _v.set(x, y, z); const c = this.camera; const cv = _v.clone().applyMatrix4(c.matrixWorldInverse); const depth = -cv.z; _v.project(c); const r = this.rect;
    return { x: r.x + (_v.x * 0.5 + 0.5) * r.w, y: r.y + (0.5 - _v.y * 0.5) * r.h, depth, ndcx: _v.x, ndcy: _v.y, ok: depth > 1 && Math.abs(_v.x) < 1.4 && Math.abs(_v.y) < 1.4 }; }
  pxPerUnit(depth) { return this.rect.h / (2 * Math.tan(this.camera.fov * Math.PI / 360) * Math.max(depth, 1)); }
}
const wrapText = (g, text, maxW) => { const words = text.split(' '); const lines = []; let cur = ''; for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } if (cur) lines.push(cur); return lines; };

export function drawPlate(g, text, x, y, px, o = {}) { // cream map plate with a team-colour border; (x,y) = bottom-centre; returns the plate rect
  const team = o.teamC || [0.3, 0.2, 0.1]; g.save(); g.font = `600 ${px}px "Cinzel"`; g.letterSpacing = Math.round(px * 0.08) + 'px';
  const lines = String(text).split('\n'); const lh = px * 1.22; const tw = Math.max(...lines.map((l) => g.measureText(l).width)); const padX = px * 0.78, padY = px * 0.52; const w = tw + padX * 2, h = lines.length * lh + padY * 2 - (lh - px) * 0.6;
  const rx = x - w / 2, ry = y - h; g.shadowColor = 'rgba(30,15,5,0.45)'; g.shadowBlur = px * 0.5; g.shadowOffsetY = px * 0.18;
  g.beginPath(); g.roundRect(rx, ry, w, h, px * 0.28); const gr = g.createLinearGradient(0, ry, 0, ry + h); gr.addColorStop(0, '#f8efd4'); gr.addColorStop(1, '#ead9aa'); g.fillStyle = gr; g.fill(); g.shadowColor = 'transparent';
  g.lineWidth = Math.max(2, px * 0.12); g.strokeStyle = rgb(team, 0.95); g.stroke(); g.beginPath(); g.roundRect(rx + px * 0.14, ry + px * 0.14, w - px * 0.28, h - px * 0.28, px * 0.16); g.lineWidth = 1; g.strokeStyle = 'rgba(60,36,14,0.45)'; g.stroke();
  g.fillStyle = INK; g.textAlign = 'center'; g.textBaseline = 'middle'; lines.forEach((l, i) => g.fillText(l, x + px * 0.04, ry + padY + lh * (i + 0.5) - (lh - px) * 0.3)); g.restore(); return { x: rx, y: ry, w, h };
}
export function drawOutlined(g, text, x, y, px, o = {}) { // cream text with a dark outline (no plate)
  g.save(); g.font = `${o.weight || 600} ${px}px "${o.font || 'Cinzel'}"`; g.letterSpacing = Math.round(px * (o.track ?? 0.12)) + 'px'; g.textAlign = 'center'; g.textBaseline = o.base || 'alphabetic'; g.lineJoin = 'round'; g.miterLimit = 2;
  g.lineWidth = px * 0.2; g.strokeStyle = 'rgba(34,20,11,0.95)'; g.strokeText(text, x, y); g.fillStyle = o.color || CREAM; g.fillText(text, x, y); g.restore();
}
const popScale = (age) => 0.55 + 0.45 * EASE.outBack(clamp(age / 0.36));

export class StageOverlay {
  constructor(stage, spec, clock) {
    this.stage = stage; this.clock = clock; const win = (e, def = Infinity) => { const t0 = clock.at(e.at); const t1 = e.until !== undefined ? clock.at(e.until) : (e.dur !== undefined ? t0 + e.dur : def); return [t0, t1]; };
    this.labels = (spec.labels || []).map((e) => { const [t0, t1] = win(e); return { ...e, t0, t1 }; });
    this.counters = (spec.counters || []).map((e) => { const [t0, t1] = win(e); const [c0, c1] = [t0, t0 + (e.countDur ?? 1.6)]; return { ...e, t0, t1, c0, c1 }; });
    this.icons = (spec.icons || []).map((e) => { const [t0, t1] = win(e); return { ...e, t0, t1 }; });
    this.volleys = (spec.volleys || []).map((e) => { const [t0, t1] = clock.span(e, 1.2); return { ...e, t0, t1 }; });
    this.rings = []; this.sp = {};
  }
  anchor(it, t, view) { // world anchor of an item -> [x, y, z] or null (screen anchored)
    const st = this.stage; if (it.screen) return null;
    let x, z, y = 0;
    if (it.follow) { const A = st.arrows.byId[it.follow]; if (!A) return [0, 0, 0]; const s = A.progress(t) * A.L; const p = A.pointAt(s); x = p.x; z = p.z; it._dir = Math.sign(p.dx) || 1; }
    else if (it.block) { const ids = st.blocks.groups[it.block] || [it.block]; let sx = 0, sz = 0, n = 0, ym = 0; for (const id of ids) { const b = st.blocks.byId[id]; const s = st.blocks.state(b, t); if (s.alpha < 0.02 && ids.length > 1) continue; sx += s.x; sz += s.z; n++; ym = Math.max(ym, (b.height || 2) + 1.0 + (s.drop || 0)); } n = n || 1; x = sx / n + (it.ox || 0); z = sz / n + (it.oz || 0); y = ym + (it.top === false ? 0 : 2.0) + (ids.length > 1 ? (it.lift ?? 8) : 0); }
    else { x = it.pos[0]; z = it.pos[1]; }
    return [x, st.mh(x, z) + y + (it.y || 0), z];
  }
  draw(g, t, view) {
    const st = this.stage; const H = view.rect.h; const baseR = this.pxBase || 1;
    for (const v of this.volleys) if (t >= v.t0 && t < v.t1 + (v.flight ?? 0.9) + 0.3) this.drawVolley(g, v, t, view);
    for (const it of this.icons) if (t >= it.t0 && t < it.t1 + 0.4) this.drawIconItem(g, it, t, view);
    for (const it of this.labels) if (t >= it.t0 && t < it.t1 + 0.4) this.drawLabel(g, it, t, view);
    for (const it of this.counters) if (t >= it.t0 && t < it.t1 + 0.4) this.drawCounter(g, it, t, view);
  }
  fade(it, t, outDur = 0.35) { return clamp((t - it.t0) / 0.18) * (isFinite(it.t1) ? 1 - clamp((t - it.t1) / outDur) : 1); }
  place(it, t, view) { // -> {x, y, scalePxPerUnit, ok}
    const r = view.rect; const A = this.anchor(it, t, view);
    if (!A) return { x: r.x + it.screen[0] * r.w, y: r.y + it.screen[1] * r.h, ppu: 1, ok: true, screen: true };
    const p = view.project(A[0], A[1], A[2]); const edge = Math.min(1 - Math.abs(p.ndcx), 1 - Math.abs(p.ndcy)); return { x: p.x, y: p.y, ppu: view.pxPerUnit(p.depth), ok: p.depth > 1 && edge > -0.05, edge, depth: p.depth };
  }
  drawLabel(g, it, t, view) {
    const a = this.fade(it, t); if (a <= 0.01) return; const P = this.place(it, t, view); if (!P.ok) return; const H = view.rect.h; const size = (it.size ?? 1) * H * (it.big ? 0.050 : 0.036); const age = t - it.t0; const sc = popScale(age);
    const team = it.team ? TEAMS[it.team] : null; const edgeA = P.screen ? 1 : clamp((P.edge ?? 1) / 0.08);
    g.save(); g.globalAlpha = a * edgeA; const dx = (it.dx || 0) * H, dy = (it.dy ?? -0.06) * H; const ax = P.x, ay = P.y; const px = P.x + dx, py = P.y + dy; const lift = !P.screen ? 0 : 0;
    g.translate(px, py - lift); g.scale(sc, sc); g.translate(-px, -(py - lift));
    if (it.leader !== false && !P.screen && (Math.abs(dy) > size * 0.9 || Math.abs(dx) > size)) { g.beginPath(); g.moveTo(px, py + size * 0.1); g.lineTo(ax, ay); g.lineWidth = Math.max(3, size * 0.14); g.strokeStyle = 'rgba(30,16,8,0.9)'; g.stroke(); g.lineWidth = Math.max(1.4, size * 0.05); g.strokeStyle = CREAM; g.stroke();
      g.beginPath(); g.arc(ax, ay, Math.max(3, size * 0.14), 0, 7); g.fillStyle = team ? rgb(team.top) : '#f6ecd0'; g.fill(); g.lineWidth = 2; g.strokeStyle = INK; g.stroke(); }
    if (it.style === 'text') drawOutlined(g, it.text, px, py, size, { weight: it.weight || 600, color: it.color, track: it.track });
    else drawPlate(g, it.text, px, py + size * 0.55, size, { teamC: team ? team.top : null });
    g.restore();
  }
  drawCounter(g, it, t, view) {
    const a = this.fade(it, t); if (a <= 0.01) return; const P = this.place(it, t, view); if (!P.ok) return; const H = view.rect.h; const size = (it.size ?? 1) * H * 0.052; const age = t - it.t0; const sc = popScale(age);
    const u = clamp((t - it.c0) / Math.max(0.01, it.c1 - it.c0)); const e = 1 - Math.pow(1 - u, 3); const val = Math.round(lerp(it.from ?? 0, it.to, e) / (it.step ?? 100)) * (it.step ?? 100);
    const txt = val.toLocaleString('en-US'); const team = it.team ? TEAMS[it.team] : TEAMS.neutral; const dx = (it.dx || 0) * H, dy = (it.dy ?? -0.12) * H; const px = P.x + dx, py = P.y + dy;
    g.save(); g.globalAlpha = a * (P.screen ? 1 : clamp((P.edge ?? 1) / 0.08)); g.translate(px, py); g.scale(sc, sc); g.translate(-px, -py);
    g.font = `800 ${size * 1.5}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.06) + 'px'; const nw = g.measureText(txt).width; g.font = `600 ${size * 0.62}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.18) + 'px'; const sw = g.measureText((it.suffix || 'SOLDIERS')).width;
    const w = Math.max(nw, sw) + size * 1.5, h = size * 2.5; const x0 = px - w / 2, y0 = py - h;
    if (it.leader !== false && !P.screen) { g.beginPath(); g.moveTo(px, py); g.lineTo(P.x, P.y); g.lineWidth = Math.max(3, size * 0.12); g.strokeStyle = 'rgba(30,16,8,0.9)'; g.stroke(); g.lineWidth = Math.max(1.4, size * 0.05); g.strokeStyle = CREAM; g.stroke(); }
    g.shadowColor = 'rgba(25,12,4,0.5)'; g.shadowBlur = size * 0.5; g.shadowOffsetY = size * 0.2; g.beginPath(); g.roundRect(x0, y0, w, h, size * 0.34); g.fillStyle = rgb(team.side, 0.92); g.fill(); g.shadowColor = 'transparent';
    g.lineWidth = Math.max(2.4, size * 0.1); g.strokeStyle = '#f6ecd0'; g.stroke(); g.beginPath(); g.roundRect(x0 + size * 0.14, y0 + size * 0.14, w - size * 0.28, h - size * 0.28, size * 0.22); g.lineWidth = 1; g.strokeStyle = 'rgba(246,236,208,0.4)'; g.stroke();
    g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.font = `800 ${size * 1.5}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.06) + 'px'; g.fillStyle = '#fff3d2'; g.fillText(txt, px, y0 + size * 1.58);
    g.font = `600 ${size * 0.62}px "Cinzel"`; g.letterSpacing = Math.round(size * 0.18) + 'px'; g.fillStyle = rgb(team.light); g.fillText(it.suffix || 'SOLDIERS', px, y0 + size * 2.22); g.restore();
  }
  drawIconItem(g, it, t, view) {
    const a = this.fade(it, t, 0.3); if (a <= 0.01) return; const P = this.place(it, t, view); if (!P.ok && !P.screen) return; const age = t - it.t0;
    const H = view.rect.h; const size = P.screen ? (it.size ?? 0.2) * H : (it.size ?? 12) * P.ppu * (it.zoom ?? 1); const pop = it.anim === 'none' ? 1 : popScale(age);
    let bob = 0, rot = 0; if (it.anim === 'bounce') bob = -Math.abs(Math.sin(age * 5.5)) * size * 0.18; if (it.anim === 'walk') { bob = -Math.abs(Math.sin(age * 7)) * size * 0.06; rot = Math.sin(age * 7) * 0.035; } if (it.anim === 'sway') rot = Math.sin(age * 3) * 0.07;
    const flip = it.flip ?? (it._dir ? it._dir < 0 : false); const spin = it.anim === 'slam' ? clamp((age - 0.1) / 0.18) : 1; const team = it.team || undefined;
    // icon slides (pos2) or hops (hop) between two anchors
    let x = P.x + (it.dx || 0) * H, y = P.y + (it.dy || 0) * H;
    if (it.hop) { const hp = it.hop; const sw = hp.swaps.map((r) => this.clock.at(r)); const dur = hp.dur ?? 0.28; const ids = hp.between; let cur = hp.start ?? 0, fromI = cur, toI = cur, u = 1; for (let k = 0; k < sw.length; k++) { if (t >= sw[k]) { fromI = cur; cur = (cur + 1) % ids.length; toI = cur; u = clamp((t - sw[k]) / dur); } }
      const a0 = this.sp[ids[fromI]], a1 = this.sp[ids[toI]]; if (!a0 || !a1) return; const e = EASE.inOut(u); x = lerp(a0.x, a1.x, e); y = lerp(a0.y - a0.size * (hp.up ?? 0.95), a1.y - a1.size * (hp.up ?? 0.95), e) - Math.sin(Math.PI * e) * size * 0.55; }
    if (it.id) this.sp[it.id] = { x, y, size };
    g.save(); g.globalAlpha = a * (P.screen ? 1 : clamp((P.edge ?? 1) / 0.08)); g.translate(x, y + bob); g.scale(pop, pop); g.translate(-x, -(y + bob)); drawIcon(g, it.icon, x, y + bob, Math.max(10, size), { flip, team, t: age, rot, fill: it.fill }); g.restore();
  }
  drawVolley(g, v, t, view) { // a spread of arrows lofted on arcs from one block/area onto another
    const st = this.stage; const n = v.n ?? 36; const flight = v.flight ?? 0.9; const team = TEAMS[v.team || 'carthage'] || TEAMS.carthage; const sp = v.spread ?? 0.35; const H = view.rect.h;
    const pt = (e, t2) => { if (e.block) { const b = st.blocks.byId[e.block]; const s = st.blocks.state(b, t2); return [s.x, s.z, Math.max(s.len, s.dep) * 0.35]; } return [e[0], e[1], e[2] ?? 8]; };
    const A = pt(v.from, v.t0), B = pt(v.to, v.t1); g.save(); g.lineCap = 'round';
    for (let i = 0; i < n; i++) { const t0 = v.t0 + (v.t1 - v.t0) * hash01(i, 11, v.t0 * 10 | 0) * (1 - 0.0); const age = t - t0; if (age < 0 || age > flight + 0.25) continue; const u = clamp(age / flight);
      const sx = A[0] + (hash01(i, 3) - 0.5) * 2 * A[2], sz = A[1] + (hash01(i, 5) - 0.5) * 2 * A[2], ex = B[0] + (hash01(i, 7) - 0.5) * 2 * B[2], ez = B[1] + (hash01(i, 9) - 0.5) * 2 * B[2];
      const arc = (v.arc ?? 34) * (0.85 + 0.3 * hash01(i, 13)); const pos = (uu) => { const x = lerp(sx, ex, uu), z = lerp(sz, ez, uu); const y = st.mh(x, z) + 3 + 4 * arc * uu * (1 - uu); return view.project(x, y, z); };
      const head = pos(u), tail = pos(Math.max(0, u - 0.16)); if (!head.ok) continue; const fade = age > flight ? 1 - clamp((age - flight) / 0.25) : 1;
      g.globalAlpha = fade * (v.alpha ?? 0.95); g.beginPath(); g.moveTo(tail.x, tail.y); g.lineTo(head.x, head.y); g.lineWidth = Math.max(1.6, H * 0.0034); g.strokeStyle = 'rgba(30,16,8,0.95)'; g.stroke();
      g.lineWidth = Math.max(0.9, H * 0.0016); g.strokeStyle = rgb(team.light); g.stroke();
      if (u < 1) { const dxp = head.x - tail.x, dyp = head.y - tail.y; const l = Math.hypot(dxp, dyp) || 1; const ux = dxp / l, uy = dyp / l; const hs = Math.max(3, H * 0.0075); g.beginPath(); g.moveTo(head.x + ux * hs * 0.6, head.y + uy * hs * 0.6); g.lineTo(head.x - ux * hs + uy * hs * 0.55, head.y - uy * hs - ux * hs * 0.55); g.lineTo(head.x - ux * hs - uy * hs * 0.55, head.y - uy * hs + ux * hs * 0.55); g.closePath(); g.fillStyle = 'rgba(30,16,8,0.95)'; g.fill(); }
      else { g.beginPath(); g.moveTo(head.x, head.y); g.lineTo(head.x, head.y - H * 0.012); g.lineWidth = Math.max(1.4, H * 0.003); g.strokeStyle = 'rgba(30,16,8,0.9)'; g.stroke(); } }
    g.restore();
  }
}

// ------------------------------------------------------------------ cards (title, end card, big words), drawn in full-screen space
const ornament = (g, x, y, w, a) => { g.save(); g.globalAlpha *= a; g.strokeStyle = 'rgba(244,214,130,0.95)'; g.lineWidth = 2; g.beginPath(); g.moveTo(x - w / 2, y); g.lineTo(x - 16, y); g.moveTo(x + 16, y); g.lineTo(x + w / 2, y); g.stroke(); g.beginPath(); g.moveTo(x, y - 8); g.lineTo(x + 8, y); g.lineTo(x, y + 8); g.lineTo(x - 8, y); g.closePath(); g.fillStyle = 'rgba(244,214,130,0.95)'; g.fill(); g.restore(); };
export function drawCard(g, c, t, W, H) {
  const t0 = c.t0, t1 = c.t1; if (t < t0 || t > t1 + 0.6) return; const age = t - t0; const fin = clamp(age / (c.fadeIn ?? 0.35)), fout = isFinite(t1) ? 1 - clamp((t - t1) / (c.fadeOut ?? 0.5)) : 1; const a = fin * fout; if (a <= 0.001) return;
  g.save();
  if (c.fill) { g.globalAlpha = a * (c.fillAlpha ?? 1); g.fillStyle = c.fill; g.fillRect(0, 0, W, H); g.globalAlpha = 1; }
  if (c.scrim) { g.globalAlpha = a * c.scrim; const gr = g.createRadialGradient(W / 2, H / 2, H * 0.1, W / 2, H / 2, H * 0.95); gr.addColorStop(0, c.scrimCenter ? c.scrimCenter : 'rgba(20,10,4,0.55)'); gr.addColorStop(1, 'rgba(10,5,2,1)'); g.fillStyle = gr; g.fillRect(0, 0, W, H); if (c.band) { g.globalAlpha = a * c.band; g.fillStyle = 'rgba(12,6,3,1)'; g.fillRect(0, H * 0.30, W, H * 0.40); } }
  (c.lines || []).forEach((L, i) => {
    const la = clamp((age - (L.delay ?? i * 0.28)) / 0.3); if (la <= 0) return; const sc = L.pop === false ? 1 : 1 + 0.22 * (1 - EASE.outBack(clamp((age - (L.delay ?? i * 0.28)) / 0.5)));
    const px = (L.size ?? 0.08) * H; const x = (L.x ?? 0.5) * W, y = (L.y ?? 0.5) * H; g.save(); g.globalAlpha = a * la; g.translate(x, y); g.scale(sc, sc); g.translate(-x, -y);
    g.font = `${L.italic ? 'italic ' : ''}${L.weight ?? 800} ${px}px "${L.font || 'Cinzel'}"`; g.letterSpacing = Math.round(px * (L.track ?? 0.1)) + 'px'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round';
    if (L.shadow !== false) { g.shadowColor = 'rgba(0,0,0,0.65)'; g.shadowBlur = px * 0.35; g.shadowOffsetY = px * 0.06; } g.lineWidth = px * 0.16; g.strokeStyle = L.stroke || 'rgba(34,18,8,0.95)'; g.strokeText(L.text, x + px * 0.03, y);
    g.shadowColor = 'transparent'; const gr = g.createLinearGradient(0, y - px * 0.5, 0, y + px * 0.5); gr.addColorStop(0, L.colorTop || L.color || '#fff0c4'); gr.addColorStop(1, L.colorBottom || L.color || '#e8b94f'); g.fillStyle = gr; g.fillText(L.text, x + px * 0.03, y); g.restore(); });
  for (const o of (c.ornaments || [])) ornament(g, (o.x ?? 0.5) * W, o.y * H, o.w * W, a * clamp((age - 0.2) / 0.4));
  g.restore();
}
