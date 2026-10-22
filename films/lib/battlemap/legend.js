// Battle Map engine v2: the legend, a motion-graphics frame around the battlefield.
//  - sides panel (default top-left): a title block, then each side (banner, name, commander, strength counter), each entry
//    animating in on the narration word that first names it;
//  - key panel (default bottom-left): the unit types used (military unit symbols) and the key places (lettered badges that match
//    markers pinned on the map; when a place is introduced a hairline links its legend row to its marker for a moment);
//  - scale bar and compass (bottom-right) in a cartographic style, shown on high (map-like) views only.
// Everything is a pure function of t. Sizes scale with the frame height so the panels read at phone size.
import { clamp, lerp } from './noise.js';
import { drawIcon, UNIT_GLYPH } from './icons.js';
import { TEAMS } from './blocks.js';
import { FONTS } from './overlay.js';

const INK = '#2a190e', PAPER = 'rgba(246,238,216,0.93)', HALO = 'rgba(244,234,210,0.92)';
const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);
const inWin = (wins, t, fin = 0.5, fout = 0.5) => { let a = 0; for (const [t0, t1] of wins) a = Math.max(a, clamp((t - t0) / fin) * (1 - clamp((t - t1) / fout))); return a; };

// turn the legend's places into map markers on their stage (called before the stages are built)
export function legendMarkers(spec) {
  const L = spec.legend; if (!L) return; for (const p of (L.places || [])) { if (!p.pos) continue; const st = p.stage ? spec.stages?.[p.stage] : spec; if (!st) throw new Error('legend place ' + p.id + ': unknown stage ' + p.stage);
    (st.markers ||= []).push({ id: p.id, at: p.at, until: p.until, pos: p.pos, y: p.y ?? 0, glyph: p.glyph, letter: p.letter, team: p.team, label: p.label === false ? null : (p.label || p.name.toUpperCase()), labelUntil: p.labelUntil, labelDur: p.labelDur, size: p.markerSize, dx: p.dx, dy: p.dy, ldx: p.ldx, ldy: p.ldy, align: p.align }); }
}

export class Legend {
  constructor(spec, clock) {
    const L = spec.legend || null; this.L = L; this.clock = clock; if (!L) return; const at = (r) => clock.at(r);
    const wins = (w, def) => (w || def || []).map((p) => [at(p[0]), at(p[1])]);
    this.show = wins(L.show, [[0, 1e9]]); this.keyShow = wins(L.key?.show, this.show.map((p) => p.slice())); this.scaleShow = wins(L.scale?.show, this.show.map((p) => p.slice()));
    this.title = L.title ? { ...L.title, t0: at(L.title.at ?? 0) } : null;
    this.sides = (L.sides || []).map((s) => ({ ...s, t0: at(s.at), ts: s.strengthAt !== undefined ? at(s.strengthAt) : null, tc: s.commanderAt !== undefined ? at(s.commanderAt) : at(s.at), tdim: s.dimAt !== undefined ? at(s.dimAt) : null }));
    this.units = (L.units || []).map((u) => ({ ...u, t0: at(u.at) })); this.places = (L.places || []).map((p) => ({ ...p, t0: at(p.at), t1: p.until !== undefined ? at(p.until) : 1e9 }));
    this.focus = (L.focus || []).map((f) => ({ ...f, t0: at(f.at), t1: at(f.until) }));
    this.corner = L.corner || 'tl'; this.keyCorner = L.key?.corner || 'bl'; this.unitM = L.scale?.unitM ?? 20; this.compass = L.compass !== false; this.scaleOn = L.scale !== false;
  }
  focusK(id, t) { let k = 0; for (const f of this.focus) if (f.entry === id) k = Math.max(k, clamp((t - f.t0) / 0.3) * (1 - clamp((t - f.t1) / 0.4))); return k; }
  panel(g, x, y, w, h, a, k) { g.save(); g.globalAlpha = a; g.shadowColor = 'rgba(30,15,5,0.35)'; g.shadowBlur = 14 * k; g.shadowOffsetY = 4 * k; g.beginPath(); g.roundRect(x, y, w, h, 5 * k); g.fillStyle = PAPER; g.fill(); g.shadowColor = 'transparent';
    g.lineWidth = 1.2 * k; g.strokeStyle = 'rgba(42,25,14,0.85)'; g.stroke(); g.beginPath(); g.roundRect(x + 4 * k, y + 4 * k, w - 8 * k, h - 8 * k, 3 * k); g.lineWidth = 0.9 * k; g.strokeStyle = 'rgba(170,120,45,0.7)'; g.stroke(); g.restore(); }
  draw(g, t, W, H, ctx = {}) {
    if (!this.L) return; const k = H / 720 * (this.L.scaleUI ?? 1.08); this.rows = {};
    this.drawSides(g, t, W, H, k); this.drawKey(g, t, W, H, k, ctx); if (this.scaleOn || this.compass) this.drawScale(g, t, W, H, k, ctx);
  }
  drawSides(g, t, W, H, k) {
    const a = inWin(this.show, t, 0.6, 0.5); if (a <= 0.01) return; const pad = 14 * k, w = 318 * k; const items = [];
    if (this.title) items.push({ h: 66 * k, t0: this.title.t0, draw: (x, y, ag) => { g.save(); g.globalAlpha *= ag; g.textBaseline = 'alphabetic'; g.font = `600 ${18 * k}px "${FONTS.display}"`; g.letterSpacing = Math.round(1.8 * k) + 'px'; g.fillStyle = INK; g.fillText(this.title.text, x, y + 24 * k);
      if (this.title.sub) { g.font = `italic 600 ${18 * k}px "${FONTS.text}"`; g.letterSpacing = '0px'; g.fillStyle = 'rgba(42,25,14,0.85)'; g.fillText(this.title.sub, x, y + 47 * k); }
      g.beginPath(); g.moveTo(x, y + 58 * k); g.lineTo(x + (w - pad * 2) * eo((t - this.title.t0) / 0.6), y + 58 * k); g.lineWidth = 1 * k; g.strokeStyle = 'rgba(170,120,45,0.9)'; g.stroke(); g.restore(); } });
    for (const s of this.sides) items.push({ h: 64 * k, t0: s.t0, id: s.id || s.team, draw: (x, y, ag) => { const team = TEAMS[s.team] || TEAMS.neutral; const fk = this.focusK(s.id || s.team, t); const dim = s.tdim !== null ? clamp((t - s.tdim) / 1.2) : 0;
      g.save(); g.globalAlpha *= ag * (1 - 0.35 * dim); if (fk > 0) { g.beginPath(); g.roundRect(x - 6 * k, y + 2 * k, w - pad * 2 + 12 * k, 60 * k, 4 * k); g.fillStyle = `rgba(232,196,120,${0.35 * fk})`; g.fill(); }
      drawIcon(g, s.banner || 'banner', x + 20 * k, y + 60 * k, 54 * k, { team: team.top, t: t - s.t0, halo: false });
      g.textBaseline = 'alphabetic'; g.font = `700 ${19 * k}px "${FONTS.display}"`; g.letterSpacing = Math.round(1.6 * k) + 'px'; g.fillStyle = rgb(team.top, 0.72); g.fillText(s.name, x + 50 * k, y + 28 * k);
      if (s.commander && t >= s.tc) { g.globalAlpha *= clamp((t - s.tc) / 0.4); g.font = `italic 600 ${18 * k}px "${FONTS.text}"`; g.letterSpacing = '0px'; g.fillStyle = INK; g.fillText(s.commander, x + 50 * k, y + 50 * k); g.globalAlpha /= Math.max(1e-3, clamp((t - s.tc) / 0.4)); }
      if (s.strength && s.ts !== null && t >= s.ts) { const u = eo((t - s.ts) / 1.1); const v = Math.round(s.strength * u / 1000) * 1000; g.textAlign = 'right'; g.font = `800 ${21 * k}px "${FONTS.display}"`; g.letterSpacing = '0px'; g.fillStyle = rgb(team.top, 0.72); g.fillText(v.toLocaleString('en-US'), x + w - pad * 2, y + 28 * k);
        g.font = `600 ${11 * k}px "${FONTS.display}"`; g.letterSpacing = Math.round(1.4 * k) + 'px'; g.fillStyle = 'rgba(42,25,14,0.8)'; g.fillText(s.strengthLabel || 'SOLDIERS', x + w - pad * 2, y + 44 * k); }
      g.restore(); } });
    this.stack(g, t, items, this.corner, w, pad, a, W, H, k, 'sides');
  }
  drawKey(g, t, W, H, k, ctx) {
    const a = inWin(this.keyShow, t, 0.6, 0.5); if (a <= 0.01 || (!this.units.length && !this.places.length)) return; const pad = 12 * k, w = 268 * k; const items = []; const rowH = 36 * k;
    const head = (txt, t0) => items.push({ h: 24 * k, t0, draw: (x, y, ag) => { g.save(); g.globalAlpha *= ag; g.font = `600 ${12 * k}px "${FONTS.display}"`; g.letterSpacing = Math.round(2.2 * k) + 'px'; g.fillStyle = 'rgba(42,25,14,0.75)'; g.textBaseline = 'alphabetic'; g.fillText(txt, x, y + 17 * k); g.restore(); } });
    if (this.units.length) { head(this.L.key?.unitsTitle || 'FORCES', Math.min(...this.units.map((u) => u.t0)));
      for (const u of this.units) items.push({ h: rowH, t0: u.t0, id: u.id || u.kind, draw: (x, y, ag) => { const team = TEAMS[u.team || 'neutral']; const fk = this.focusK(u.id || u.kind, t); g.save(); g.globalAlpha *= ag;
        if (fk > 0) { g.beginPath(); g.roundRect(x - 5 * k, y + 1 * k, w - pad * 2 + 10 * k, rowH - 2 * k, 4 * k); g.fillStyle = `rgba(232,196,120,${0.35 * fk})`; g.fill(); }
        if (u.teams) u.teams.forEach((tm, i) => drawIcon(g, u.glyph || UNIT_GLYPH[u.kind] || 'u-infantry', x + 13 * k + i * 27 * k, y + rowH - 4 * k, 28 * k, { team: (TEAMS[tm] || team).top, halo: false }));
        else drawIcon(g, u.glyph || UNIT_GLYPH[u.kind] || 'u-infantry', x + 18 * k, y + rowH - 2 * k, 36 * k, { team: team.top, halo: false });
        g.font = `600 ${18 * k}px "${FONTS.text}"`; g.fillStyle = INK; g.textBaseline = 'middle'; g.letterSpacing = '0px'; g.fillText(u.name, x + (u.teams ? 34 + 27 * (u.teams.length - 1) : 46) * k, y + rowH * 0.56); g.restore(); } }); }
    if (this.places.length) { head(this.L.key?.placesTitle || 'PLACES', Math.min(...this.places.map((p) => p.t0)));
      for (const p of this.places) items.push({ h: rowH, t0: p.t0, t1: p.t1, id: p.id, draw: (x, y, ag) => { const team = p.team ? TEAMS[p.team] : null; g.save(); g.globalAlpha *= ag; const r = 10.5 * k, bx = x + 10 * k, by = y + rowH * 0.52;
        g.beginPath(); g.arc(bx, by, r, 0, 7); g.fillStyle = team ? rgb(team.top) : INK; g.fill(); g.font = `700 ${13 * k}px "${FONTS.display}"`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = '#f6ecd0'; g.fillText(p.letter || '', bx, by + 0.5 * k);
        if (p.glyph) drawIcon(g, p.glyph, x + 40 * k, y + rowH - 3 * k, 30 * k, { team: p.team ? team.top : undefined, halo: false });
        g.textAlign = 'left'; g.font = `600 ${18 * k}px "${FONTS.text}"`; g.fillStyle = INK; g.fillText(p.name, x + 62 * k, y + rowH * 0.56); g.restore();
        // the link: a hairline from the badge to the place's marker on the map while it is introduced
        const age = t - p.t0; const m = ctx.markers?.[p.id]; if (m && age < 3.2) { const la = clamp(age / 0.25) * (1 - clamp((age - 2.4) / 0.8)) * ag; const u = eo((age - 0.15) / 0.7); if (la > 0.01 && u > 0) { const sx = bx + r, sy = by; const ex = lerp(sx, m.x, u), ey = lerp(sy, m.y, u);
          g.save(); g.globalAlpha = la; g.setLineDash([5 * k, 4 * k]); g.beginPath(); g.moveTo(sx, sy); g.lineTo(ex, ey); g.lineWidth = 3.2 * k; g.strokeStyle = HALO; g.stroke(); g.lineWidth = 1.3 * k; g.strokeStyle = INK; g.stroke(); g.setLineDash([]); g.restore(); } } } }); }
    this.stack(g, t, items, this.keyCorner, w, pad, a, W, H, k, 'key');
  }
  stack(g, t, items, corner, w, pad, a, W, H, k, name) { // rows grow in as they appear; the panel grows with them
    let h = pad * 1.4; const vis = []; for (const it of items) { const u = eo((t - it.t0) / 0.45); const gone = it.t1 !== undefined ? eo((t - it.t1) / 0.45) : 0; const hh = it.h * u * (1 - gone); if (hh <= 0.2) continue; vis.push({ it, y: h, ag: clamp((t - it.t0 - 0.1) / 0.4) * (1 - gone), hh }); h += hh; }
    if (!vis.length) return; h += pad * 0.6; const m = 22 * k; const slide = (1 - eo(a)) * 30 * k;
    const x = corner[1] === 'l' ? m - slide : W - m - w + slide; const y = corner[0] === 't' ? m : H - m - h;
    this.panel(g, x, y, w, h, a, k); g.save(); g.globalAlpha = a; g.beginPath(); g.rect(x, y, w, h); g.clip();
    for (const v of vis) { g.save(); g.translate((1 - eo((t - v.it.t0) / 0.5)) * -10 * k, 0); v.it.draw(x + pad, y + v.y, v.ag); g.restore(); } g.restore();
  }
  drawScale(g, t, W, H, k, ctx) {
    const a0 = inWin(this.scaleShow, t, 0.6, 0.5); const pose = ctx.pose; if (!pose || !ctx.view || a0 <= 0.01) return; const a = a0 * clamp((pose.pitch - 48) / 10); if (a <= 0.01) return;
    const v = ctx.view; const ty = ctx.ground ? ctx.ground(pose.x, pose.z) : 0; const p0 = v.project(pose.x, ty, pose.z); const ppu = v.pxPerUnit(p0.depth); if (!isFinite(ppu) || ppu <= 0) return;
    const target = W * 0.13; const m0 = target / ppu * this.unitM; const pow = Math.pow(10, Math.floor(Math.log10(m0))); const nice = [1, 2, 5, 10].map((q) => q * pow).reduce((b, q) => Math.abs(q - m0) < Math.abs(b - m0) ? q : b); const len = nice / this.unitM * ppu;
    const x1 = W - 26 * k, x0 = x1 - len, y = H - 30 * k; g.save(); g.globalAlpha = a;
    const seg = 4; for (let i = 0; i < seg; i++) { g.beginPath(); g.rect(x0 + len * i / seg, y - 4 * k, len / seg, 6 * k); g.fillStyle = i % 2 ? '#f4ead2' : INK; g.fill(); } g.beginPath(); g.rect(x0, y - 4 * k, len, 6 * k); g.lineWidth = 1.2 * k; g.strokeStyle = INK; g.stroke();
    g.font = `600 ${15 * k}px "${FONTS.text}"`; g.textBaseline = 'alphabetic'; g.lineJoin = 'round'; const lab = nice >= 1000 ? (nice / 1000) + ' km' : nice + ' m'; const tx = (s, x, al) => { g.textAlign = al; g.lineWidth = 4 * k; g.strokeStyle = HALO; g.strokeText(s, x, y - 9 * k); g.fillStyle = INK; g.fillText(s, x, y - 9 * k); }; tx('0', x0, 'center'); tx(lab, x1, 'right');
    if (this.compass) { const pn = v.project(pose.x, ty, pose.z - 30); const ang = Math.atan2(pn.x - p0.x, -(pn.y - p0.y)); const cx = x1 - 14 * k, cy = y - 50 * k, R = 15 * k;
      g.beginPath(); g.arc(cx, cy, R + 3 * k, 0, 7); g.fillStyle = 'rgba(244,234,210,0.85)'; g.fill(); g.lineWidth = 1 * k; g.strokeStyle = INK; g.stroke(); g.save(); g.translate(cx, cy); g.rotate(ang);
      g.beginPath(); g.moveTo(0, -R); g.lineTo(5 * k, 2 * k); g.lineTo(0, -1 * k); g.closePath(); g.fillStyle = INK; g.fill(); g.beginPath(); g.moveTo(0, -R); g.lineTo(-5 * k, 2 * k); g.lineTo(0, -1 * k); g.closePath(); g.fillStyle = '#a3241c'; g.fill();
      g.beginPath(); g.moveTo(0, R * 0.8); g.lineTo(4 * k, -1 * k); g.lineTo(-4 * k, -1 * k); g.closePath(); g.lineWidth = 1 * k; g.strokeStyle = INK; g.stroke();
      g.font = `700 ${11 * k}px "${FONTS.display}"`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = INK; g.fillText('N', 0, -R - 8 * k); g.restore(); }
    g.restore();
  }
}
