// Bamberg (Kinetic): the dark city map. A street grid that draws itself, and the two graphs that grow on it:
//  - the CHAIN of accusations (arrest someone, torture, names, arrest those people ... six people name him)
//  - the WALK: Junius made to walk his own town in his mind, street by street, naming people; the names multiply.
// No invented people: nodes carry an abstract pen scrawl (a name written by a hand), never a real or made-up name.
import { clamp, lerp, ease, rng, smoothstep, noise1, rgba, mixc, keys, catmull } from './lib.js';

export function createMap(E) {
  const { W, H, U, C } = E, tw = E.tw, cream = C.cream;
  const JA = (i) => 0.028 * Math.sin(i * 2.1 + 0.7) + 0.012 * Math.sin(i * 5.3), JB = (j) => 0.035 * Math.sin(j * 1.7 + 1.9) + 0.015 * Math.sin(j * 4.1);
  const AVX = (i) => 0.02 + 0.135 * i + JA(i), CRY = (j) => 0.10 + 0.15 * j + JB(j);                      // world units: 1 = frame width
  const wobA = (i, y) => 0.011 * noise1(y * 5.1 + i * 3.7, i) + 0.006 * noise1(y * 13 + i, 4);
  const wobC = (j, x) => 0.010 * noise1(x * 5.3 + j * 2.9, j + 9) + 0.005 * noise1(x * 12 + j, 2);
  const IA = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], JC = Array.from({ length: 19 }, (_, j) => j);
  const P = (i, j) => { let x = AVX(i), y = CRY(j); for (let k = 0; k < 3; k++) { x = AVX(i) + wobA(i, y); y = CRY(j) + wobC(j, x); } return [x, y]; };
  // streets as polylines (world coords), with a reveal order
  const streets = [];
  for (const i of IA) { const pts = []; for (let k = 0; k <= 36; k++) { const y = -0.1 + k * 0.08; pts.push([AVX(i) + wobA(i, y), y]); } streets.push({ pts, w: i % 3 === 0 ? 2.0 : 1.3, a: i % 3 === 0 ? 0.50 : 0.30, ord: (i + 1) / IA.length }); }
  for (const j of JC) { const pts = []; for (let k = 0; k <= 22; k++) { const x = -0.2 + k * 0.07; pts.push([x, CRY(j) + wobC(j, x)]); } streets.push({ pts, w: j % 4 === 0 ? 2.0 : 1.3, a: j % 4 === 0 ? 0.50 : 0.30, ord: j / JC.length }); }
  { const pts = []; for (let k = 0; k <= 40; k++) { const u = k / 40, x = -0.2 + 1.5 * u, y = 1.2 + 0.55 * Math.sin(u * 5.2) * 0.5 + u * 0.9; pts.push([x, y]); } streets.push({ pts, w: 3.6, a: 0.30, ord: 0.5, river: true });      // the river: a wide soft line
    const p2 = pts.map(([x, y]) => [x + 0.015, y + 0.03]); streets.push({ pts: p2, w: 1.2, a: 0.45, ord: 0.55, river: true }); }
  for (const [x0, y0, x1, y1, bend] of [[0.05, 1.45, 1.0, 2.55, 0.12], [0.9, 1.35, 0.05, 2.2, -0.1], [0.3, 1.2, 0.8, 2.7, 0.15]]) { const pts = []; for (let k = 0; k <= 24; k++) { const u = k / 24; pts.push([lerp(x0, x1, u) + bend * Math.sin(u * Math.PI), lerp(y0, y1, u)]); } streets.push({ pts, w: 1.6, a: 0.38, ord: 0.8 }); }

  // camera: world -> screen. cx, cy world centre, z zoom (1 = world width is frame width)
  const KEYS = [[0, 0.5, 1.62, 1.0], [30, 0.5, 1.62, 1.0], [47, 0.52, 1.64, 1.0], [49.5, 0.56, 1.78, 1.04], [111, 0.5, 1.75, 1.0], [117.5, 0.5, 1.80, 1.18], [121, 0.5, 1.80, 1.16], [123.8, 0.5, 1.82, 0.92]];
  const cam = (t) => { const k = KEYS; let a = k[0], b = k[k.length - 1]; for (let n = 1; n < k.length; n++) if (t <= k[n][0]) { a = k[n - 1]; b = k[n]; break; } const u = ease.inOutSine(clamp((t - a[0]) / (b[0] - a[0] || 1))); return { cx: lerp(a[1], b[1], u) + 0.006 * noise1(t * 0.35, 1), cy: lerp(a[2], b[2], u) + 0.012 * noise1(t * 0.3, 2), z: lerp(a[3], b[3], u) }; };
  const toS = (c, wx, wy) => [(wx - c.cx) * c.z * W + W / 2, (wy - c.cy) * c.z * W + H / 2];

  // ---- streets that draw themselves; tReveal = when the drawing starts, dur = how long it takes
  function drawStreets(t, tReveal, dur, alpha, c) {
    const g = E.g; g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
    for (const s of streets) {
      const p = clamp((t - tReveal - s.ord * dur * 0.7) / (dur * 0.3 + 0.2)); if (p <= 0) continue;
      const n = Math.max(2, Math.floor(s.pts.length * ease.outQuad(p) + 1)); g.beginPath();
      for (let k = 0; k < n && k < s.pts.length; k++) { const [x, y] = toS(c, s.pts[k][0], s.pts[k][1]); if (k) g.lineTo(x, y); else g.moveTo(x, y); }
      g.strokeStyle = rgba(cream, s.a * alpha); g.lineWidth = s.w * U * (s.river ? c.z : 1); g.stroke();
    }
    g.restore();
  }

  // ---- scrawl: an abstract pen "name" (never legible), revealed left to right
  const SC = new Map();
  function scrawl(seed, len) {
    const key = seed + '|' + len; if (SC.has(key)) return SC.get(key);
    const r = rng(seed * 131 + 7), pts = [[0, 0]]; let x = 0; const xh = 5 * U, asc = 13 * U, desc = 8 * U;
    while (x < len * W) {
      const c = (4 + 4 * r()) * U, q = r();
      if (q < 0.34) pts.push([x + 0.22 * c, -xh], [x + 0.5 * c, -0.2 * xh], [x + 0.78 * c, -xh], [x + c, 0]);
      else if (q < 0.64) pts.push([x + 0.3 * c, -0.95 * xh], [x + 0.55 * c, -0.05 * xh], [x + 0.8 * c, -0.75 * xh], [x + c, 0]);
      else if (q < 0.84) pts.push([x + 0.24 * c, -0.7 * asc], [x + 0.4 * c, -asc], [x + 0.52 * c, -0.65 * asc], [x + 0.34 * c, -0.2 * asc], [x + 0.58 * c, 0], [x + c, 0]);
      else pts.push([x + 0.3 * c, -xh], [x + 0.42 * c, 0.25 * desc], [x + 0.4 * c, desc], [x + 0.12 * c, 0.85 * desc], [x + 0.3 * c, -0.1 * xh], [x + c, 0]);
      x += c; if (r() < 0.14) { x += 7 * U; pts.push([x, 0]); }
    }
    const o = { pts: catmull(pts, 4), w: x }; SC.set(key, o); return o;
  }
  function drawScrawl(g, sx, sy, seed, len, t0, t, alpha, dur = 0.35, col = cream, scale = 1) {
    const p = clamp((t - t0) / dur); if (p <= 0) return; const S = scrawl(seed, len);
    g.save(); g.translate(sx, sy); g.scale(scale, scale); g.beginPath(); g.rect(-4 * U, -30 * U, (S.w + 8 * U) * p, 60 * U); g.clip();
    g.strokeStyle = rgba(col, alpha); g.lineWidth = 1.5 * U; g.lineJoin = 'round'; g.lineCap = 'round'; g.beginPath(); S.pts.forEach(([x, y], k) => (k ? g.lineTo(x, y) : g.moveTo(x, y))); g.stroke(); g.restore();
  }

  // ---- node + edge drawing
  function node(g, sx, sy, t0, t, { r = 10, ring = true, alpha = 1, col = cream, fill = true } = {}) {
    const k = (t - t0) / 0.22; if (k <= 0) return; const e = ease.outCubic(clamp(k)), s = lerp(1.7, 1, e);
    g.save(); g.globalAlpha = clamp(k * 3) * alpha; g.strokeStyle = rgba(col, 0.9); g.lineWidth = 1.6 * U; g.beginPath(); g.arc(sx, sy, r * U * s, 0, 6.2832); g.stroke();
    if (fill) { g.fillStyle = rgba(col, 0.95); g.beginPath(); g.arc(sx, sy, r * 0.38 * U * s, 0, 6.2832); g.fill(); }
    // landing ripple
    const rk = (t - t0) / 0.5; if (rk > 0 && rk < 1) { g.globalAlpha = 0.4 * (1 - rk) * alpha; g.beginPath(); g.arc(sx, sy, (r + 22 * ease.outCubic(rk)) * U, 0, 6.2832); g.stroke(); }
    g.restore();
  }
  function edge(g, a, b, t0, dur, t, { alpha = 0.75, w = 2.2, col = cream, dash = false } = {}) {
    const p = ease.outCubic(clamp((t - t0) / dur)); if (p <= 0) return; const x = lerp(a[0], b[0], p), y = lerp(a[1], b[1], p);
    g.save(); g.strokeStyle = rgba(col, alpha); g.lineWidth = w * U; g.lineCap = 'round'; if (dash) g.setLineDash([6 * U, 6 * U]); g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(x, y); g.stroke(); g.restore();
  }

  // ================================================================ the chain (x3 to x5)
  const CH = {
    n0: { ij: [3, 10], t: tw('x3', 'someone.'), seed: 1 },
    n1: { ij: [2, 11], t: tw('x3', 'names.') + 0.35, seed: 2 }, n2: { ij: [5, 11], t: tw('x3', 'names.') + 0.5, seed: 3 },
    n3: { ij: [1, 12], t: tw('x3', 'arrest', 1) + 0.15, seed: 4 }, n4: { ij: [3, 12], t: tw('x3', 'those') + 0.1, seed: 5 },
    n5: { ij: [4, 12], t: tw('x3', 'people.') - 0.05, seed: 6 }, n6: { ij: [6, 12], t: tw('x3', 'people.') + 0.12, seed: 7 },
    J: { ij: [6, 14], t: tw('x4', "Junius's"), seed: 8, big: true },
    Wf: { ij: [5, 13], t: tw('x4', 'wife'), seed: 9 },
  };
  const SIX = [[4, 14], [5, 15], [7, 15], [8, 14], [7, 13], [3, 15]];
  const CHE = [['n0', 'n1', 0.45], ['n0', 'n2', 0.5], ['n1', 'n3', 0.3], ['n1', 'n4', 0.3], ['n2', 'n5', 0.3], ['n2', 'n6', 0.3]];
  E.chainNames = () => CH;
  function drawChain(t, c) {
    const g = E.g, pos = (k) => { const o = CH[k]; const [x, y] = P(o.ij[0], o.ij[1]); return toS(c, x, y); };
    // edges: tree
    const tEdge = { n1: tw('x3', 'names.') + 0.05, n2: tw('x3', 'names.') + 0.1, n3: tw('x3', 'arrest', 1) - 0.1, n4: tw('x3', 'those') - 0.05, n5: tw('x3', 'people.') - 0.3, n6: tw('x3', 'people.') - 0.15 };
    const par = { n1: 'n0', n2: 'n0', n3: 'n1', n4: 'n1', n5: 'n2', n6: 'n2' };
    for (const k of Object.keys(par)) edge(g, pos(par[k]), pos(k), tEdge[k], 0.32, t);
    // the wife is named: an edge from the tree to her, on "named."
    const tWifeNamed = tw('x4', 'named.');
    edge(g, pos('n6'), pos('Wf'), tWifeNamed - 0.1, 0.35, t);
    // nodes + scrawls
    for (const k of Object.keys(CH)) {
      const o = CH[k], [sx, sy] = pos(k); if (t < o.t) continue;
      if (k === 'J') { node(g, sx, sy, o.t, t, { r: 16 }); }
      else node(g, sx, sy, o.t, t, { r: 10 });
      if (k === 'Wf') E.labelAt(sx - 6 * U, sy + 34 * U, 'HIS WIFE', o.t + 0.1);
      if (k !== 'J' && k !== 'Wf') drawScrawl(g, sx + 16 * U, sy - 2 * U, o.seed, 0.07 + (o.seed % 3) * 0.015, o.t + 0.2, t, 0.9, 0.35, cream, 1.5);
    }
    // she was executed: a heavy X over her node
    const tx = tw('x4', 'executed.');
    if (t >= tx) { const [sx, sy] = pos('Wf'), p = ease.outCubic(clamp((t - tx) / 0.14)), q = ease.outCubic(clamp((t - tx - 0.1) / 0.14)), d = 17 * U; g.save(); g.strokeStyle = rgba(cream, 0.95); g.lineWidth = 3.2 * U; g.lineCap = 'round'; g.beginPath(); g.moveTo(sx - d, sy - d); g.lineTo(sx - d + 2 * d * p, sy - d + 2 * d * p); g.moveTo(sx + d, sy - d); g.lineTo(sx + d - 2 * d * q, sy - d + 2 * d * q); g.stroke(); g.restore(); }
    // six name him
    const tS = [tw('x5', 'six'), tw('x5', 'six') + 0.12, tw('x5', 'people') - 0.02, tw('x5', 'people') + 0.1, tw('x5', 'named') - 0.2, tw('x5', 'named') - 0.08];
    const [jx, jy] = pos('J');
    SIX.forEach(([i, j], n) => {
      const [x, y] = P(i, j), [sx, sy] = toS(c, x, y); if (t < tS[n]) return;
      edge(g, [sx, sy], [jx, jy], tw('x5', 'named') + n * 0.045, 0.28, t, { alpha: 0.95, w: 2.6 });
      node(g, sx, sy, tS[n], t, { r: 10 }); drawScrawl(g, sx + 16 * U, sy - 2 * U, 20 + n, 0.08, tS[n] + 0.15, t, 0.9, 0.35, cream, 1.5);
    });
    if (t >= CH.J.t) { node(g, jx, jy, CH.J.t, t, { r: 16 }); E.labelAt(jx - 24 * U, jy + 30 * U, 'JUNIUS', CH.J.t + 0.1); }
  }

  // ================================================================ the walk (l3, l4)
  const ROUTE = [[1, 9], [1, 11], [3, 11], [3, 13], [2, 13], [2, 15], [5, 15], [5, 12], [6, 12]];
  const routePts = () => ROUTE.map(([i, j]) => P(i, j));
  const WALK0 = tw('l3', 'walk'), WALK1 = tw('l3', 'people.');
  // names along the route and across the town (positions are intersections; times: along the walk, then the multiplication)
  const NAMES = []; {
    const r = rng(404); const used = new Set();
    // names the walker meets (from "and name people.")
    [[1, 11], [3, 11], [3, 13], [2, 15], [5, 15], [5, 12]].forEach(([i, j], n) => { NAMES.push({ ij: [i, j], t: tw('l3', 'name') + n * 0.11, seed: 100 + n }); used.add(i + ',' + j); });
    // the gift: a slip of cold paper, then he repeats it, then the town fills with it (accelerating)
    const t0 = tw('l4', 'repeated'), t1 = tw('l4', 'it.') + 0.9; let n = 0, tt = t0;
    for (let k = 0; k < 120; k++) {
      const i = Math.floor(r() * 8), j = 8 + Math.floor(r() * 9), key = i + ',' + j; if (used.has(key)) continue; used.add(key);
      NAMES.push({ ij: [i, j], t: tt, seed: 200 + k, late: true }); tt += lerp(0.075, 0.008, clamp(k / 60)); if (tt > t1) break; n++;
    }
  }
  E.walkNames = NAMES;
  function walkHead(t) {      // progress along the route [0..1] on a stepped, hand-led gait
    const k = clamp((t - WALK0) / (WALK1 - WALK0)); return ease.inOutSine(k) * 0.4 + k * 0.6;
  }
  function drawWalk(t, c) {
    const g = E.g, R = routePts().map(([x, y]) => toS(c, x, y)), p = walkHead(t);
    // route length
    const seg = []; let L = 0; for (let k = 1; k < R.length; k++) { const d = Math.hypot(R[k][0] - R[k - 1][0], R[k][1] - R[k - 1][1]); seg.push(d); L += d; }
    let acc = 0, head = R[0], reach = p * L;
    g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
    // street by street: three legs flash on the three beats
    const flashes = [tw('l3', 'street'), tw('l3', 'by'), tw('l3', 'street,')];
    g.beginPath(); g.moveTo(R[0][0], R[0][1]);
    for (let k = 1; k < R.length; k++) {
      const d = seg[k - 1]; if (reach <= acc) break; const u = clamp((reach - acc) / d); const hx = lerp(R[k - 1][0], R[k][0], u), hy = lerp(R[k - 1][1], R[k][1], u); g.lineTo(hx, hy); head = [hx, hy]; acc += d; if (u < 1) break;
    }
    g.strokeStyle = rgba(cream, 0.6); g.lineWidth = 3.2 * U; g.stroke();
    // legs 4,5,6 brightened as the narration says "street by street"
    for (let k = 4; k <= 6; k++) { const f0 = flashes[k - 4], a = R[k - 1], b = R[k]; if (t < f0) continue; const u = clamp((t - f0) / 0.5), w = lerp(6, 3.2, ease.outCubic(u)); g.strokeStyle = rgba(cream, lerp(0.95, 0.55, u)); g.lineWidth = w * U; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }
    g.restore();
    // pen tip
    if (t >= WALK0 && t < WALK1 + 0.4) { g.save(); g.fillStyle = rgba(cream, 1); g.beginPath(); g.arc(head[0], head[1], 5 * U, 0, 6.2832); g.fill(); g.globalAlpha = 0.25; g.beginPath(); g.arc(head[0], head[1], 13 * U, 0, 6.2832); g.fill(); g.restore(); }
    // names
    const tGift = tw('l4', 'name.') - 0.05;
    for (const nm of NAMES) {
      if (t < nm.t) continue; const [x, y] = P(nm.ij[0], nm.ij[1]), [sx, sy] = toS(c, x, y);
      node(g, sx, sy, nm.t, t, { r: nm.late ? 7 : 10, alpha: nm.late ? 0.9 : 1 }); drawScrawl(g, sx + 13 * U, sy - 2 * U, nm.seed, 0.06 + (nm.seed % 4) * 0.012, nm.t + 0.1, t, 0.9, nm.late ? 0.22 : 0.35, cream, nm.late ? 1.35 : 1.5);
    }
    // the empty slot ("when he could not think of anyone") then the slip that arrives
    const tBlank = tw('l4', 'anyone,') - 0.35, [bx, by] = (() => { const [x, y] = P(5, 10); return toS(c, x, y); })();
    if (t >= tBlank) {
      const k = clamp((t - tBlank) / 0.3); g.save(); g.setLineDash([5 * U, 5 * U]); g.strokeStyle = rgba(cream, 0.8 * k); g.lineWidth = 1.6 * U; g.beginPath(); g.arc(bx, by, 9 * U, 0, 6.2832); g.stroke(); g.restore();
      edge(g, R[R.length - 1], [bx, by], tBlank - 0.1, 0.3, t, { alpha: 0.5, dash: true });
    }
    // the court's name: a typed slip of cold paper falls into the empty slot, lands on "name." and stays
    const tg0 = tw('l4', 'gave') + 0.05;
    if (t >= tg0) {
      const k = clamp((t - tg0) / (tGift + 0.05 - tg0)), e = ease.inCubic(k), sw = 0.26 * W, sh = 0.036 * H, off = (1 - e) * 0.28 * H, rot = (1 - e) * -0.18;
      const land = (t - tGift - 0.05) * 24, sc = land < 0 ? 1 : keys(land, [[0, 1.2], [1, 1.07], [2, 0.99], [3, 1.0]]);
      g.save(); g.translate(bx + 10 * U + sw / 2, by - off); g.rotate(rot); g.scale(sc, sc); g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 14 * U; g.shadowOffsetY = 5 * U;
      g.fillStyle = '#d9dcdc'; g.fillRect(-sw / 2, -sh / 2, sw, sh); g.shadowColor = 'rgba(0,0,0,0)';
      g.fillStyle = '#14171a'; g.font = `400 ${0.021 * H}px "Special Elite"`; g.letterSpacing = (0.08 * 0.021 * H) + 'px'; g.textBaseline = 'middle'; g.textAlign = 'center'; g.fillText('NAME', 0, 1 * U); g.restore();
    }
  }
  E.labelAt = (x, y, txt, t0) => { if (E.t < t0) return; const a = clamp((E.t - t0) / 0.2); E.ink.save(); E.ink.font = `400 ${0.021 * H}px "Bebas Neue"`; E.ink.letterSpacing = (0.14 * 0.021 * H) + 'px'; E.ink.fillStyle = rgba(cream, 0.9 * a); E.ink.fillText(txt, x, y); E.ink.restore(); };
  E.mapAPI = { cam, toS, drawStreets, drawChain, drawWalk, P };
  return E.mapAPI;
}
