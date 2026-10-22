// Kinetic map card: an abstract street or region grid that draws itself, with nodes, edges and a pen route appearing on words.
// Coordinates in the spec are fractions of the frame ([0,0] top left, [1,1] bottom right). The grid is decoration, never geography.
import { clamp, lerp, ease, rng, rgba, noise1, measure, FONTS } from '../lib.js';
import { buildBlock } from '../blocks.js';

function gridLines(kind, seed, A) {                                      // lines in world units (1 = frame width); A = aspect H/W
  const L = [], r = rng(seed * 97 + 5);
  const jx = (i) => 0.028 * Math.sin(i * 2.1 + seed) + 0.012 * Math.sin(i * 5.3 + seed * 2), jy = (j) => 0.035 * Math.sin(j * 1.7 + 1.9 + seed) + 0.015 * Math.sin(j * 4.1);
  if (kind === 'streets') {
    for (let i = -2; i <= 9; i++) { const pts = [], x0 = 0.02 + 0.135 * i + jx(i); for (let k = 0; k <= 40; k++) { const y = -0.2 + k * 0.06; pts.push([x0 + 0.011 * noise1(y * 5.1 + i * 3.7, i + seed) + 0.006 * noise1(y * 13 + i, 4), y]); } L.push({ pts, w: i % 3 === 0 ? 2.0 : 1.3, a: i % 3 === 0 ? 0.5 : 0.3, ord: (i + 2) / 12 }); }
    for (let j = 0; j <= 14; j++) { const pts = [], y0 = 0.06 + 0.15 * j + jy(j); for (let k = 0; k <= 24; k++) { const x = -0.2 + k * 0.06; pts.push([x, y0 + 0.01 * noise1(x * 5.3 + j * 2.9, j + 9 + seed) + 0.005 * noise1(x * 12 + j, 2)]); } L.push({ pts, w: j % 4 === 0 ? 2.0 : 1.3, a: j % 4 === 0 ? 0.5 : 0.3, ord: j / 15 }); }
    const pts = []; for (let k = 0; k <= 40; k++) { const u = k / 40; pts.push([-0.2 + 1.5 * u, A * 0.78 + 0.28 * Math.sin(u * 5.2 + seed) * 0.5 + u * 0.3]); } L.push({ pts, w: 3.6, a: 0.28, ord: 0.5, soft: true });
    for (const [x0, y0, x1, y1, bend] of [[0.05, A * 0.4, 1.0, A * 0.9, 0.12], [0.9, A * 0.35, 0.05, A * 0.8, -0.1]]) { const p2 = []; for (let k = 0; k <= 24; k++) { const u = k / 24; p2.push([lerp(x0, x1, u) + bend * Math.sin(u * Math.PI), lerp(y0, y1, u)]); } L.push({ pts: p2, w: 1.6, a: 0.36, ord: 0.8 }); }
  } else if (kind === 'graticule') {
    for (let i = -3; i <= 11; i++) { const pts = []; for (let k = 0; k <= 40; k++) { const y = -0.2 + k * (A + 0.4) / 40; pts.push([0.1 * i + 0.1 * Math.sin(y * 1.6 + seed) * (i - 4) * 0.12 + 0.04 * Math.sin(y * 3 + i), y]); } L.push({ pts, w: i % 3 === 0 ? 1.8 : 1.1, a: i % 3 === 0 ? 0.45 : 0.26, ord: (i + 3) / 15 }); }
    for (let j = 0; j <= 12; j++) { const pts = [], y0 = 0.1 + 0.16 * j; for (let k = 0; k <= 24; k++) { const x = -0.2 + k * 0.06, u = x - 0.5; pts.push([x, y0 + 0.07 * u * u * (j - 5.5) * 0.4 + 0.012 * Math.sin(x * 4 + j)]); } L.push({ pts, w: j % 3 === 0 ? 1.8 : 1.1, a: j % 3 === 0 ? 0.45 : 0.26, ord: j / 13 }); }
  } else if (kind === 'sea') {
    for (let j = 0; j < 34; j++) { const pts = [], y0 = 0.03 + j * (A / 33), ph = r() * 6, am = 0.006 + 0.012 * r(); for (let k = 0; k <= 36; k++) { const x = -0.1 + k * 0.032; pts.push([x, y0 + am * Math.sin(x * (9 + 3 * r()) + ph) + 0.008 * Math.sin(x * 3 + j)]); } L.push({ pts, w: j % 5 === 0 ? 1.8 : 1.1, a: 0.22 + 0.3 * (j % 5 === 0 ? 1 : 0.5), ord: j / 34 }); }
  }
  return L;
}

export function map(E, c, ctx) {
  const { W, H, U } = E, th = ctx.theme, A = H / W, ink = th.ink;
  const kind = c.grid ?? 'streets', seed = c.seed ?? 3, lines = kind === 'none' ? [] : gridLines(kind, seed, A);
  const tGrid = ctx.at(c.gridOn ?? ctx.t0 + 0.1), gridDur = c.gridDur ?? 2.6, dur = Math.max(1, ctx.t1 - ctx.t0);
  const zoom = c.zoom ?? 1.12, focus = c.focus || [0.5, 0.45];
  const ZK = Array.isArray(zoom) ? zoom.map(([r, z]) => [ctx.at(r), z]).sort((a, b) => a[0] - b[0]) : null;
  const cam = (t) => {
    if (ZK) { if (t <= ZK[0][0]) return ZK[0][1]; for (let i = 1; i < ZK.length; i++) if (t <= ZK[i][0]) return lerp(ZK[i - 1][1], ZK[i][1], ease.inOutSine(clamp((t - ZK[i - 1][0]) / (ZK[i][0] - ZK[i - 1][0] || 1)))); return ZK[ZK.length - 1][1]; }
    return 1 + (zoom - 1) * ease.inOutSine(clamp((t - ctx.t0) / dur));
  };
  const toS = (fx, fy, z) => [((fx - focus[0]) * z + focus[0]) * W, ((fy - focus[1]) * z + focus[1]) * H];
  const wToS = (u, v, z) => toS(u, v / A, z);
  // nodes
  const NODES = {}; const ids = Object.keys(c.nodes || {}); let order = 0;
  for (const id of ids) {
    const n = c.nodes[id], label = n.label ? String(n.label).toUpperCase() : '';
    let t = n.on != null ? ctx.at(n.on) : null;
    if (t == null && label) { const m = ctx.clock.match(label.split(' '), ctx.t0); if (m) { const k = m.findIndex((x) => x != null); t = m[k]; } }
    if (t == null) t = ctx.t0 + 0.7 + order * 0.35; order++;
    NODES[id] = { id, ...n, label, t, xT: n.xOn != null ? ctx.at(n.xOn) : null };
  }
  const edges = (c.edges || []).map((e) => { const o = Array.isArray(e) ? { from: e[0], to: e[1], ...(e[2] || {}) } : e; if (!NODES[o.from] || !NODES[o.to]) throw new Error(`map edge refers to unknown node ${o.from} or ${o.to}`); return { ...o, t: o.on != null ? ctx.at(o.on) : Math.max(NODES[o.from].t, NODES[o.to].t) - 0.05, dur: o.dur ?? 0.4 }; });
  const routes = (c.routes || []).map((r) => {
    const pts = r.points || r.via.map((id) => { if (!NODES[id]) throw new Error('map route refers to unknown node ' + id); return [NODES[id].x, NODES[id].y]; });
    const [a, b] = r.on != null ? [ctx.at(r.on), r.until != null ? ctx.at(r.until) : ctx.at(r.on) + (r.dur ?? 2)] : [ctx.t0 + 0.5, ctx.t1 - 0.5];
    return { ...r, pts, a, b };
  });
  // text: one block for the whole card, or steps: [{ at, text }] that replace each other (each step's words match the cues from its own start)
  const stepSrc = c.steps || (c.text ? [{ at: ctx.t0, text: c.text }] : []);
  const STEPS = stepSrc.map((st, i) => { const t0 = st.at != null ? ctx.at(st.at) : ctx.t0, nx = stepSrc[i + 1], t1 = nx && nx.at != null ? ctx.at(nx.at) : ctx.t1; return { t0, t1, st }; })
    .map(({ t0, t1, st }) => ({ t0, t1, B: buildBlock(E, { ...ctx, t0, t1, from: t0 }, st.text, { pos: st.pos ?? c.pos ?? 'top', emph: st.emph ?? c.emph, accent: st.accent, align: c.align, color: c.color }) }));
  const B = STEPS.length ? { hits: STEPS.flatMap((s) => s.B.hits), lastT: Math.max(...STEPS.map((s) => s.B.lastT)) } : null;
  const bgc = th.dark ? '14,13,11' : th.parchment ? '242,233,214' : '236,238,238';
  const dim = (to, a0) => { const g = E.g, gr = g.createLinearGradient(0, 0, 0, to * H); gr.addColorStop(0, `rgba(${bgc},${a0})`); gr.addColorStop(0.8, `rgba(${bgc},${a0 * 0.8})`); gr.addColorStop(1, `rgba(${bgc},0)`); g.fillStyle = gr; g.fillRect(0, 0, W, to * H); };
  const drawNode = (g, sx, sy, t0, t, o) => {
    const k = (t - t0) / 0.22; if (k <= 0) return; const e = ease.outCubic(clamp(k)), s = lerp(1.7, 1, e), r = (o.r ?? 10) * (o.big ? 1.6 : 1), col = o.accent ? th.accent : ink;
    g.save(); g.globalAlpha = clamp(k * 3); g.strokeStyle = rgba(col, 0.92); g.fillStyle = rgba(col, 0.95); g.lineWidth = 1.7 * U;
    if (o.kind === 'none') { g.restore(); return; }
    if (o.kind === 'square') g.strokeRect(sx - r * U * s, sy - r * U * s, 2 * r * U * s, 2 * r * U * s); else { g.beginPath(); g.arc(sx, sy, r * U * s, 0, 6.2832); g.stroke(); }
    if (o.kind !== 'ring') { g.beginPath(); g.arc(sx, sy, r * 0.4 * U * s, 0, 6.2832); g.fill(); }
    const rk = (t - t0) / 0.5; if (rk > 0 && rk < 1) { g.globalAlpha = 0.4 * (1 - rk); g.beginPath(); g.arc(sx, sy, (r + 22 * ease.outCubic(rk)) * U, 0, 6.2832); g.stroke(); }
    g.restore();
  };
  const draw = (E) => {
    const t = E.t, g = E.g, z = cam(t); g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
    for (const s of lines) {
      const p = clamp((t - tGrid - s.ord * gridDur * 0.7) / (gridDur * 0.3 + 0.2)); if (p <= 0) continue;
      const n = Math.max(2, Math.floor(s.pts.length * ease.outQuad(p) + 1)); g.beginPath();
      for (let k = 0; k < n && k < s.pts.length; k++) { const [x, y] = wToS(s.pts[k][0], s.pts[k][1], z); if (k) g.lineTo(x, y); else g.moveTo(x, y); }
      g.strokeStyle = rgba(ink, s.a * (c.gridAlpha ?? 0.9)); g.lineWidth = s.w * U * (s.soft ? z : 1); g.stroke();
    }
    g.restore();
    const step = STEPS.filter((x) => t >= x.t0 - 1e-9 && t < x.t1).pop();
    if (step) dim(c.dim ?? 0.46, th.dark ? 0.85 : 0.8);
    // routes (pen walks the path)
    for (const r of routes) {
      const p = clamp((t - r.a) / Math.max(0.1, r.b - r.a)); if (p <= 0) continue; const P = r.pts.map(([x, y]) => toS(x, y, z)); const seg = []; let Ltot = 0;
      for (let k = 1; k < P.length; k++) { const d = Math.hypot(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1]); seg.push(d); Ltot += d; }
      let reach = (r.ease === 'linear' ? p : ease.inOutSine(p)) * Ltot, acc = 0, head = P[0]; g.save(); g.strokeStyle = rgba(r.accent ? th.accent : ink, 0.75); g.lineWidth = (r.w ?? 3) * U; g.lineCap = 'round'; g.lineJoin = 'round'; if (r.dash) g.setLineDash([9 * U, 8 * U]);
      g.beginPath(); g.moveTo(P[0][0], P[0][1]);
      for (let k = 1; k < P.length; k++) { const d = seg[k - 1]; if (reach <= acc) break; const u = clamp((reach - acc) / d), hx = lerp(P[k - 1][0], P[k][0], u), hy = lerp(P[k - 1][1], P[k][1], u); g.lineTo(hx, hy); head = [hx, hy]; acc += d; if (u < 1) break; }
      g.stroke(); g.setLineDash([]);
      if (r.pen !== false && p < 1) { g.fillStyle = rgba(ink, 1); g.beginPath(); g.arc(head[0], head[1], 5 * U, 0, 6.2832); g.fill(); g.globalAlpha = 0.25; g.beginPath(); g.arc(head[0], head[1], 13 * U, 0, 6.2832); g.fill(); }
      g.restore();
    }
    // edges
    for (const e of edges) {
      const p = ease.outCubic(clamp((t - e.t) / e.dur)); if (p <= 0) continue; const a = NODES[e.from], b = NODES[e.to], A0 = toS(a.x, a.y, z), B0 = toS(b.x, b.y, z);
      g.save(); g.strokeStyle = rgba(e.accent ? th.accent : ink, e.alpha ?? 0.8); g.lineWidth = (e.w ?? 2.2) * U; g.lineCap = 'round'; if (e.dash) g.setLineDash([6 * U, 6 * U]);
      g.beginPath(); g.moveTo(A0[0], A0[1]); g.lineTo(lerp(A0[0], B0[0], p), lerp(A0[1], B0[1], p)); g.stroke(); g.restore();
    }
    // nodes, labels, crosses
    for (const id of ids) {
      const n = NODES[id]; if (t < n.t) continue; const [sx, sy] = toS(n.x, n.y, z);
      drawNode(g, sx, sy, n.t, t, n);
      if (n.label) {
        const a = clamp((t - n.t - 0.08) / 0.2), I = E.ink, fs = (n.big ? 0.027 : 0.021) * H, side = n.side || 'right'; I.save(); I.font = `400 ${fs}px "Bebas Neue"`; I.letterSpacing = (0.14 * fs) + 'px'; I.fillStyle = rgba(n.accent ? th.accent : ink, 0.95 * a); I.textBaseline = 'alphabetic';
        const wd = measure(I.font, n.label, 0.14 * fs).adv, off = (n.big ? 24 : 17) * U;
        if (side === 'left') I.fillText(n.label, sx - off - wd, sy + fs * 0.33); else if (side === 'below') I.fillText(n.label, sx - wd / 2, sy + off + fs * 1.6); else if (side === 'above') I.fillText(n.label, sx - wd / 2, sy - off); else I.fillText(n.label, sx + off, sy + fs * 0.33);
        I.restore();
      }
      if (n.xT != null && t >= n.xT) { const p = ease.outCubic(clamp((t - n.xT) / 0.14)), q = ease.outCubic(clamp((t - n.xT - 0.1) / 0.14)), d = 17 * U; g.save(); g.strokeStyle = rgba(th.accent && n.accent ? th.accent : ink, 0.95); g.lineWidth = 3.2 * U; g.lineCap = 'round'; g.beginPath(); g.moveTo(sx - d, sy - d); g.lineTo(sx - d + 2 * d * p, sy - d + 2 * d * p); g.moveTo(sx + d, sy - d); g.lineTo(sx + d - 2 * d * q, sy - d + 2 * d * q); g.stroke(); g.restore(); }
    }
    if (step) step.B.draw(E);
  };
  const hits = [...(B ? B.hits : [])];
  for (const id of ids) if (NODES[id].big) hits.push([NODES[id].t, 5, 4, 0.03]);
  return { draw, hits, lastT: Math.max(ctx.t0, B ? B.lastT : 0, ...ids.map((i) => NODES[i].t)) };
}
