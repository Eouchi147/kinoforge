// Battle Map engine v2: the living world. Ambient layers that run by themselves, quietly, as pure functions of t:
//  camps (tents in rows or scattered, a palisade, campfires with smoke, small figures walking between the tents),
//  walkers (small figures or riders moving along a road), smoke columns, birds (small ink flocks circling or crossing),
//  wind (gusts sweeping over the grass, banners), the river's flow (moving glints), drifting cloud shadows (terrain shader).
// spec.ambient = { wind: [x, z], gusts: 0..1, flow: { dir: [x, z], speed, glint }, camps: [...], walkers: [...], smoke: [...], birds: [...] }
import { clamp, lerp, hash01 } from './noise.js';
import { TEAMS } from './blocks.js';

const DEG = Math.PI / 180;
export class Ambient {
  constructor(stage, spec = {}, clock) {
    this.stage = stage; this.spec = spec; this.clock = clock; const w = spec.wind || [1.2, 0.4]; const wl = Math.hypot(w[0], w[1]) || 1; this.wind = w; this.windDir = [w[0] / wl, w[1] / wl];
    const win = (e) => [e.at !== undefined && !Array.isArray(e.at) ? clock.at(e.at) : -1e9, e.until !== undefined ? clock.at(e.until) : 1e9]; // positions are pos / center / path; at and until are times
    this.camps = (spec.camps || []).map((c, ci) => this.buildCamp(c, ci));
    this.walkers = (spec.walkers || []).map((wk) => { const pts = wk.path; const seg = []; let L = 0; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); L += d; } return { ...wk, seg, L, win: win(wk) }; });
    this.smoke = (spec.smoke || []).map((s) => ({ ...s, win: win(s) })); this.birds = (spec.birds || []).map((b, i) => ({ ...b, i, win: win(b) }));
  }
  buildCamp(c, ci) {
    const rot = (c.rot || 0) * DEG; const cs = Math.cos(rot), sn = Math.sin(rot); const [W, D] = c.size || [c.r * 2 || 36, c.r * 1.6 || 28]; const C0 = c.pos || c.at; const L = (u, v) => [C0[0] + u * cs - v * sn, C0[1] + u * sn + v * cs];
    const tents = [], posts = [], fires = []; const team = TEAMS[c.team || 'neutral'] || TEAMS.neutral; const seed = 911 + ci * 37;
    if ((c.style || 'grid') === 'grid') { const sp = c.spacing || 4.2; for (let v = -D / 2 + sp; v <= D / 2 - sp * 0.8; v += sp) for (let u = -W / 2 + sp; u <= W / 2 - sp * 0.8; u += sp * 1.25) { if (Math.abs(u) < sp * 0.6 || Math.abs(v) < sp * 0.5) continue; const [x, z] = L(u, v); tents.push({ x, z, fx: sn, fz: -cs, sc: 2.4 + hash01(tents.length, seed) * 0.5 }); } }
    else { const n = c.tents ?? 24; for (let k = 0; k < n; k++) { const u = (hash01(k, seed, 1) - 0.5) * W * 0.9, v = (hash01(k, seed, 2) - 0.5) * D * 0.9; const a = hash01(k, seed, 3) * 6.28; const [x, z] = L(u, v); tents.push({ x, z, fx: Math.sin(a), fz: -Math.cos(a), sc: 2.2 + hash01(k, seed, 4) * 0.7 }); } }
    if (c.tents !== undefined && tents.length > c.tents) tents.length = c.tents;
    if (c.palisade !== false) { const step = 1.9; const per = [[-W / 2, -D / 2], [W / 2, -D / 2], [W / 2, D / 2], [-W / 2, D / 2], [-W / 2, -D / 2]];
      for (let i = 0; i < 4; i++) { const [u0, v0] = per[i], [u1, v1] = per[i + 1]; const len = Math.hypot(u1 - u0, v1 - v0); const n = Math.floor(len / step); for (let k = 0; k < n; k++) { const f = k / n; const u = lerp(u0, u1, f), v = lerp(v0, v1, f); if (Math.abs(u) < 3 && Math.abs(v) > D / 2 - 0.1) continue; if (Math.abs(v) < 3 && Math.abs(u) > W / 2 - 0.1) continue; const [x, z] = L(u, v); posts.push({ x, z, fx: 0, fz: -1, sc: 1.5 + 0.2 * hash01(k, i, seed) }); } } }
    for (let k = 0; k < (c.fires ?? 3); k++) { const [x, z] = L((hash01(k, seed, 7) - 0.5) * W * 0.6, (hash01(k, seed, 8) - 0.5) * D * 0.6); fires.push({ x, z }); }
    const people = []; for (let k = 0; k < (c.people ?? 12); k++) { const wp = []; for (let q = 0; q < 3; q++) wp.push(L((hash01(k, q, seed + 1) - 0.5) * W * 0.8, (hash01(k, q, seed + 2) - 0.5) * D * 0.8)); people.push({ wp, sp: 0.5 + 0.4 * hash01(k, seed, 9), ph: hash01(k, seed, 10) * 30 }); }
    return { ...c, team, tents, posts, fires, people };
  }
  loopPos(wp, s) { let L = 0; const seg = []; for (let i = 0; i < wp.length; i++) { const a = wp[i], b = wp[(i + 1) % wp.length]; const d = Math.hypot(b[0] - a[0], b[1] - a[1]); seg.push(d); L += d; } s = ((s % L) + L) % L;
    for (let i = 0; i < wp.length; i++) { if (s <= seg[i]) { const a = wp[i], b = wp[(i + 1) % wp.length]; const f = s / seg[i]; return [lerp(a[0], b[0], f), lerp(a[1], b[1], f), (b[0] - a[0]) / seg[i], (b[1] - a[1]) / seg[i]]; } s -= seg[i]; } return [wp[0][0], wp[0][1], 1, 0]; }
  update(t) {
    const F = this.stage.blocks.figs; if (!F) return; const extra = []; const puffs = []; const mh = this.stage.mh; const W = this.wind;
    for (const c of this.camps) { const col = c.team.top;
      for (const p of c.tents) extra.push({ kind: 'tent', x: p.x, z: p.z, fx: p.fx, fz: p.fz, sc: p.sc, col: [lerp(col[0], 0.9, 0.2), lerp(col[1], 0.85, 0.2), lerp(col[2], 0.7, 0.2)] });
      for (const p of c.posts) extra.push({ kind: 'post', x: p.x, z: p.z, fx: 0, fz: -1, sc: p.sc, col });
      for (const f of c.fires) { extra.push({ kind: 'fire', x: f.x, z: f.z, fx: 0, fz: -1, sc: 1.6, col }); this.smokeAt(puffs, f.x, f.z, t, 8, 0.20, mh, W, 7); }
      for (const p of c.people) { const [x, z, dx, dz] = this.loopPos(p.wp, (t + p.ph) * p.sp); extra.push({ kind: 'light', x, z, fx: dx, fz: dz, sc: 1.05, col: [lerp(col[0], 0.85, 0.35), lerp(col[1], 0.78, 0.35), lerp(col[2], 0.62, 0.35)], bob: Math.abs(Math.sin((t + p.ph) * 6)) * 0.05, h: 0.5 }); } }
    for (const wk of this.walkers) { if (t < wk.win[0] || t > wk.win[1]) continue; const n = wk.n ?? 5; const col = (TEAMS[wk.team || 'neutral'] || TEAMS.neutral).top;
      for (let k = 0; k < n; k++) { let s = (t * (wk.speed ?? 1.2) + k * (wk.gap ?? 3.0) + (wk.offset || 0)); if (wk.loop !== false) s = ((s % wk.L) + wk.L) % wk.L; else if (s > wk.L) continue;
        let i = 0, r = s; while (i < wk.seg.length - 1 && r > wk.seg[i]) { r -= wk.seg[i]; i++; } const a = wk.path[i], b = wk.path[i + 1]; const f = clamp(r / wk.seg[i]); const x = lerp(a[0], b[0], f), z = lerp(a[1], b[1], f);
        extra.push({ kind: wk.kind || 'light', x, z, fx: (b[0] - a[0]) / wk.seg[i], fz: (b[1] - a[1]) / wk.seg[i], sc: wk.scale ?? 1.1, col, bob: Math.abs(Math.sin(t * 7 + k)) * 0.05, h: hash01(k, 3) }); } }
    for (const s of this.smoke) { if (t < s.win[0] || t > s.win[1] + 6) continue; const k = clamp((t - s.win[0]) / 3) * (1 - clamp((t - s.win[1]) / 6)); this.smokeAt(puffs, s.pos[0], s.pos[1], t, s.n ?? 12, (s.alpha ?? 0.22) * k, mh, W, s.height ?? 9, s.color); }
    F.extra = extra; F.extraPuffs = puffs;
  }
  smokeAt(out, x0, z0, t, n, alpha, mh, W, height, color) { const per = 6.5; for (let q = 0; q < n; q++) { const age = ((t / per + hash01(q, Math.round(x0 * 10), Math.round(z0 * 10))) % 1); const dt = age * per; const rise = dt * height / per * 2.2;
      const x = x0 + W[0] * dt * 1.6 + Math.sin(dt * 1.3 + q) * 0.4, z = z0 + W[1] * dt * 1.6; out.push([x, mh(x0, z0) + 1 + rise, z, 1.2 + dt * 1.4, alpha * Math.sin(Math.PI * Math.pow(age, 0.7)), color || [0.72, 0.70, 0.66]]); } }
  // birds: small ink flocks drawn over the picture, projected from their 3D positions so they sit in the world
  drawOverlay(g, t, view) {
    if (!this.birds.length) return; const H = view.rect.h; g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
    for (const B of this.birds) { if (t < B.win[0] || t > B.win[1]) continue; const n = B.n ?? 7; const r = B.r ?? 40; const sp = B.speed ?? 6; const h0 = B.h ?? 22; const fa = clamp((t - B.win[0]) / 1) * (1 - clamp((t - B.win[1]) / 1));
      for (let k = 0; k < n; k++) { let x, z, y; const ph = hash01(k, B.i, 5);
        if (B.path) { const [ax, az] = B.path[0], [bx, bz] = B.path[1]; const L = Math.hypot(bx - ax, bz - az); const s = ((t * sp + ph * 10 + (B.offset || 0)) % (L + 60)) - 30; const f = s / L; const ox = (hash01(k, 1, B.i) - 0.5) * 10, oz = (hash01(k, 2, B.i) - 0.5) * 10; x = lerp(ax, bx, f) + ox; z = lerp(az, bz, f) + oz; }
        else { const a = t * sp / r * (B.dir ?? 1) + ph * 1.2; const rr = r * (0.75 + 0.35 * hash01(k, 3, B.i)); x = B.center[0] + Math.cos(a) * rr; z = B.center[1] + Math.sin(a) * rr; }
        y = this.stage.mh(x, z) + h0 + Math.sin(t * 0.9 + ph * 6) * 2 + hash01(k, 4, B.i) * 5; const p = view.project(x, y, z); if (!p.ok || p.depth < 2) continue;
        const sz = clamp(view.pxPerUnit(p.depth) * (B.size ?? 1.3), H * 0.004, H * 0.016); const flap = Math.sin(t * (B.flap ?? 9) + ph * 20); const wy = sz * (0.35 + 0.45 * flap);
        g.globalAlpha = fa * clamp((p.depth - 2) / 8) * 0.9; g.beginPath(); g.moveTo(p.x - sz, p.y - wy); g.quadraticCurveTo(p.x - sz * 0.4, p.y - wy * 0.2, p.x, p.y + sz * 0.15); g.quadraticCurveTo(p.x + sz * 0.4, p.y - wy * 0.2, p.x + sz, p.y - wy);
        g.lineWidth = Math.max(1, sz * 0.22); g.strokeStyle = 'rgba(40,28,20,0.85)'; g.stroke(); } }
    g.restore();
  }
  setVisible(v) { /* drawn through the figure meshes and the overlay */ }
}
