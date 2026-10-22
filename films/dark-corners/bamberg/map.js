// Bamberg (Kinetic): the town plan. A schematic, hand-made plan of the old town of Bamberg (NOT a survey): the Regnitz splitting around
// the island town, the cathedral hill on the west bank drawn as contour rings with the cathedral on top, the dense lanes of the island,
// the market-garden strips to the south east. No street is named on it. It draws itself line by line, and two graphs grow on it:
//  - the CHAIN of accusations (arrest someone, torture, names, arrest those people ... six people name him)
//  - the WALK: Junius made to walk his own town in his mind, street by street, naming people; the names multiply.
// Nodes carry an abstract pen scrawl (a name written by a hand, never legible): no invented people. Everything is a pure function of time.
import { clamp, lerp, ease, rng, smoothstep, noise1, rgba, keys, catmull } from './lib.js';

export function createMap(E) {
  const { W, H, U, C } = E, tw = E.tw, cream = C.cream;

  // ------------------------------------------------------------------ the plan (world units: 1 = frame width at zoom 1; y grows south)
  const xc = (y) => 0.50 + 0.05 * Math.sin(y * 1.9 + 0.6) + 0.02 * Math.sin(y * 4.3 + 1);
  const bump = (y) => Math.pow(Math.sin(Math.PI * clamp((y + 0.05) / 2.45)), 0.55);
  const hw = (y) => 0.205 * bump(y);
  const xL = (y) => xc(y) - hw(y) + 0.006 * noise1(y * 6, 3), xR = (y) => xc(y) + hw(y) + 0.006 * noise1(y * 6.5, 5);
  const R = rng(1628);
  const streets = [];
  const add = (pts, kind, w, a, extra = {}) => { const bb = pts.reduce((b, p) => [Math.min(b[0], p[0]), Math.min(b[1], p[1]), Math.max(b[2], p[0]), Math.max(b[3], p[1])], [1e9, 1e9, -1e9, -1e9]); const s = { pts, kind, w, a, bb, id: streets.length, ...extra }; streets.push(s); return s; };
  const vline = (fn, y0, y1, step = 0.035) => { const out = []; for (let y = y0; y <= y1 + 1e-9; y += step) out.push([fn(y), y]); return out; };
  const lane = (x0, y0, x1, y1, seed, amp = 0.012) => {            // a hand-drawn lane between two points: perpendicular wobble, pinned at both ends
    const len = Math.hypot(x1 - x0, y1 - y0), n = Math.max(3, Math.ceil(len / 0.03)), nx = -(y1 - y0) / len, ny = (x1 - x0) / len, out = [];
    for (let k = 0; k <= n; k++) { const u = k / n, o = amp * noise1(u * len * 15 + seed, seed) * Math.pow(Math.sin(Math.PI * u), 0.6); out.push([lerp(x0, x1, u) + nx * o, lerp(y0, y1, u) + ny * o]); }
    return out;
  };
  const Y0 = 0.10, Y1 = 2.22;
  // the two arms of the river, and the single river outside the island
  const armL = vline((y) => xL(y), -0.35, 2.75, 0.04), armR = vline((y) => xR(y), -0.35, 2.75, 0.04);
  const off = (pts, d) => pts.map((p, i) => { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)]; let tx = b[0] - a[0], ty = b[1] - a[1]; const l = Math.hypot(tx, ty) || 1; return [p[0] - (ty / l) * d, p[1] + (tx / l) * d]; });
  add(armL, 'water', 0, 0, { arm: 'L' }); add(armR, 'water', 0, 0, { arm: 'R' });
  const banks = [off(armL, -0.019), off(armL, 0.019), off(armR, -0.019), off(armR, 0.019)];
  banks.forEach((b) => add(b, 'bank', 2.0, 0.55));
  // the island: three long streets, many cross lanes
  const S1 = add(vline((y) => xc(y) + 0.004 * noise1(y * 5, 1), Y0, Y1), 'spine', 2.9, 0.62, { name: 'S1' });
  const S2 = add(vline((y) => xc(y) - 0.46 * hw(y) + 0.005 * noise1(y * 6, 2), Y0 + 0.05, Y1 - 0.05), 'spine', 1.9, 0.46, { name: 'S2' });
  const S3 = add(vline((y) => xc(y) + 0.46 * hw(y) + 0.005 * noise1(y * 6, 7), Y0 + 0.05, Y1 - 0.05), 'spine', 1.9, 0.46, { name: 'S3' });
  const crossLanes = [];
  for (let y = 0.14, k = 0; y < 2.16; y += 0.05 + 0.045 * R(), k++) {
    const yy = y, wl = hw(yy); if (wl < 0.04) continue;
    const part = R(); let xa = xL(yy) + 0.028, xb = xR(yy) - 0.028;                    // most lanes cross the island; some end in a T on a spine
    if (k % 5 !== 0) { if (part < 0.22) xb = xc(yy) + 0.46 * hw(yy) * (R() < 0.5 ? 1 : 0.0); else if (part < 0.44) xa = xc(yy) - 0.46 * hw(yy) * (R() < 0.5 ? 1 : 0.0); }
    const l = add(lane(xa, yy + 0.012 * noise1(k, 2), xb, yy + 0.02 * noise1(k, 3), 10 + k, 0.014), 'lane', k % 5 === 0 ? 1.7 : 1.15, k % 5 === 0 ? 0.46 : 0.34, { y: yy, k, full: k % 5 === 0 });
    crossLanes.push(l);
  }
  // alleys: short crooked lanes that leave a lane or a spine at a right angle and die in a courtyard
  { const parents = streets.filter((s) => s.kind === 'lane' || s.kind === 'spine'); const rA = rng(55);
    for (let n = 0; n < 150; n++) { const p = parents[Math.floor(rA() * parents.length)], i = 1 + Math.floor(rA() * (p.pts.length - 2)), a = p.pts[i - 1], b = p.pts[i + 1], tl = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, side = rA() < 0.5 ? -1 : 1, len = 0.035 + 0.075 * rA();
      const x0 = p.pts[i][0], y0 = p.pts[i][1], x1 = x0 + side * (-(b[1] - a[1]) / tl) * len, y1 = y0 + side * ((b[0] - a[0]) / tl) * len; if (y0 < 0.12 || y0 > 2.18) continue;
      const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, h2 = hw(my); if (p.kind === 'lane' && (x1 < xL(y1) + 0.03 || x1 > xR(y1) - 0.03) && (x0 > xL(y0) && x0 < xR(y0))) continue;
      add(lane(x0, y0, x1, y1, 300 + n, 0.008), 'alley', 0.95, 0.28); } }
  // quays: the street along each outer bank
  const QL = add(banks[0].map(([x, y]) => [x - 0.026, y]).filter((p) => p[1] > 0.0 && p[1] < 2.3), 'quay', 2.1, 0.5), QR = add(banks[3].map(([x, y]) => [x + 0.026, y]).filter((p) => p[1] > 0.0 && p[1] < 2.3), 'quay', 2.1, 0.5);
  // bridges: every fourth cross lane carries on over both arms to the quays and out into the districts
  const east = [], west = [];
  crossLanes.forEach((l, i) => {
    if (i % 4 !== 1) return; const yy = l.y, xl = xL(yy), xr = xR(yy);
    add(lane(xl + 0.028, yy, xl - 0.030, yy + 0.004, 40 + i, 0.002), 'bridge', 3.0, 0.62); add(lane(xr - 0.028, yy, xr + 0.030, yy + 0.004, 60 + i, 0.002), 'bridge', 3.0, 0.62);
    west.push(add(lane(xl - 0.030, yy + 0.004, xl - 0.18 - 0.14 * R(), yy + 0.05 * (R() - 0.5), 80 + i, 0.012), 'lane', 1.3, 0.38));
    east.push(add(lane(xr + 0.030, yy + 0.004, xr + 0.22 + 0.24 * R(), yy + 0.05 * (R() - 0.5), 100 + i, 0.012), 'lane', 1.3, 0.38));
  });
  // east bank: three north-south streets and short connecting lanes
  for (const [dx, y0, y1, k] of [[0.20, 0.25, 2.0, 1], [0.34, 0.30, 1.9, 2], [0.47, 0.5, 1.5, 3]]) {
    const pts = vline((y) => xR(y) + dx + 0.018 * noise1(y * 4 + k, k), y0, y1, 0.04); add(pts, 'lane', dx < 0.3 ? 1.6 : 1.2, dx < 0.3 ? 0.42 : 0.34);
    for (let y = y0 + 0.09; y < y1 - 0.05; y += 0.10 + 0.05 * R()) add(lane(xR(y) + 0.045, y, xR(y) + dx + 0.018 * noise1(y * 4 + k, k), y + 0.02 * (R() - 0.5), 120 + y * 10, 0.01), 'lane', 1.0, 0.3);
  }
  // the cathedral hill on the west bank: contour rings, a winding road, radial lanes, the precinct
  const HC = [xL(0.92) - 0.23, 0.90];
  const contours = [];
  for (let k = 1; k <= 7; k++) {
    const rr = 0.045 * k, pts = []; for (let a = 0; a <= 6.2832 + 1e-6; a += 0.12) { const wob = 1 + 0.12 * noise1(a * 2.2 + k * 1.7, 9) + 0.05 * noise1(a * 5, k); pts.push([HC[0] + Math.cos(a) * rr * 0.92 * wob, HC[1] + Math.sin(a) * rr * 1.45 * wob]); }
    contours.push(pts); add(pts, 'contour', 1.0, 0.13 + 0.015 * (7 - k), { closed: true });
  }
  { const pts = []; for (let a = 0; a < 7.8; a += 0.14) { const rr = 0.30 - a * 0.027; pts.push([HC[0] + Math.cos(a + 0.8) * rr * 0.95, HC[1] + Math.sin(a + 0.8) * rr * 1.45]); } add(pts, 'hill', 1.9, 0.48); }
  for (let k = 0; k < 7; k++) { const a = k * 0.9 + 0.3, r0 = 0.30, r1 = 0.07; add(lane(HC[0] + Math.cos(a) * r0 * 0.95, HC[1] + Math.sin(a) * r0 * 1.45, HC[0] + Math.cos(a + 0.5) * r1, HC[1] + Math.sin(a + 0.5) * r1 * 1.45, 140 + k, 0.014), 'hill', 1.1, 0.30); }
  add(lane(xL(0.70) - 0.03, 0.70, HC[0] + 0.18, HC[1] - 0.30, 160, 0.02), 'hill', 1.8, 0.46); add(lane(xL(1.18) - 0.03, 1.18, HC[0] + 0.20, HC[1] + 0.30, 161, 0.02), 'hill', 1.8, 0.46);
  const precinct = []; for (let a = 0; a <= 6.2832 + 1e-6; a += 0.3) precinct.push([HC[0] + Math.cos(a) * 0.085, HC[1] + Math.sin(a) * 0.125]); add(precinct, 'wall', 1.4, 0.34, { closed: true, dash: true });
  // market-garden strips in the south east: long narrow plots (no buildings)
  const strips = []; for (let k = 0; k < 18; k++) { const y = 1.62 + k * 0.034, x0 = xR(y) + 0.58, x1 = x0 + 0.48 + 0.04 * noise1(k, 4); strips.push([[x0, y], [x1, y + 0.004 * noise1(k, 1)]]); add(strips[k], 'field', 0.9, 0.16); }
  // the town gate and a road leaving to the north east (so the plan runs off the frame, not ends)
  add(lane(xR(0.2) + 0.5, 0.15, xR(0.2) + 0.05, 0.45, 170, 0.03), 'lane', 1.3, 0.36);

  // order the lines are drawn in: from the island's heart outward
  const CEN = [0.5, 1.15];
  for (const s of streets) { const m = s.pts[s.pts.length >> 1]; s.ord = clamp(Math.hypot(m[0] - CEN[0], (m[1] - CEN[1]) * 0.55) / 1.1); }

  // buildings: small footprints set along the streets, rejected when they hit water, the cathedral, another building or the garden strips
  const blocks = []; {
    const rr = rng(77), cell = 0.02, grid = new Map(), key = (x, y) => Math.floor(x / cell) + ',' + Math.floor(y / cell);
    const nearWater = (x, y) => { const h = hw(y); return h > 0.02 && (Math.abs(x - xL(y)) < 0.034 || Math.abs(x - xR(y)) < 0.034); };
    const PLAZA = [[0.46, 0.75, 0.055], [0.52, 1.30, 0.05], [0.47, 1.85, 0.05], [0.88, 0.95, 0.045]];
    const ok = (x, y, r0) => { if (nearWater(x, y)) return false; for (const [px, py, pr] of PLAZA) if (Math.hypot(x - px, y - py) < pr) return false; if (Math.hypot((x - HC[0]) / 0.1, (y - HC[1]) / 0.145) < 1) return false; if (x > xR(y) + 0.5 && y > 1.58) return false; for (let gx = -2; gx <= 2; gx++) for (let gy = -2; gy <= 2; gy++) { const l = grid.get(key(x + gx * cell, y + gy * cell)); if (l) for (const b of l) if (Math.hypot(b.x - x, b.y - y) < 0.7 * (b.r + r0)) return false; } return true; };
    for (const s of streets) {
      if (!['spine', 'lane', 'quay', 'hill', 'alley'].includes(s.kind)) continue;
      let carry = 0;
      for (let i = 0; i < s.pts.length - 1; i++) {
        const [ax, ay] = s.pts[i], [bx, by] = s.pts[i + 1], len = Math.hypot(bx - ax, by - ay), ux = (bx - ax) / len, uy = (by - ay) / len, nx = -uy, ny = ux;
        for (let d = carry; d < len; d += 0.0235) for (const side of [-1, 1]) {
          if (rr() > (s.kind === 'hill' ? 0.55 : 0.94)) continue;
          const bl = 0.019 + 0.005 * rr(), bd = 0.016 + 0.004 * ((s.id * 7) % 5) + 0.003 * rr(), o = 0.0085 + bd / 2, x = ax + ux * d + nx * side * o, y = ay + uy * d + ny * side * o, r0 = Math.max(bl, bd) * 0.6;
          if (!ok(x, y, r0)) continue; const b = { x, y, ux, uy, hl: bl / 2, hd: bd / 2, r: r0, bk: Math.min(5, Math.floor(Math.hypot(x - CEN[0], (y - CEN[1]) * 0.6) / 0.28)) }; blocks.push(b);
          const k = key(x, y); if (!grid.has(k)) grid.set(k, []); grid.get(k).push(b);
        }
        carry = ((carry - len) % 0.0235 + 0.0235) % 0.0235;
      }
    }
  }

  // ------------------------------------------------------------------ camera: world -> screen
  // key = [t, cx, cy, z]. The plan is first seen whole, settles, pushes in on "hunt them down", frames the chain, then goes to street level for the walk.
  const KEYS = [[0, 0.36, 0.92, 0.95], [18.7, 0.36, 0.92, 0.95], [24.0, 0.45, 1.00, 1.06], [29.0, 0.50, 1.06, 1.14], [33.0, 0.50, 1.08, 1.24], [36.0, 0.50, 1.15, 1.20], [41.5, 0.50, 1.24, 1.14],
    [47.0, 0.50, 1.32, 1.02], [49.2, 0.50, 1.34, 1.0]];
  const camKeys = (t, K) => { let a = K[0], b = K[K.length - 1]; if (t <= K[0][0]) return { cx: K[0][1], cy: K[0][2], z: K[0][3] }; for (let n = 1; n < K.length; n++) if (t <= K[n][0]) { a = K[n - 1]; b = K[n]; break; } const u = ease.inOutSine(clamp((t - a[0]) / (b[0] - a[0] || 1))); return { cx: lerp(a[1], b[1], u), cy: lerp(a[2], b[2], u), z: lerp(a[3], b[3], u) }; };
  const toS = (c, wx, wy) => [(wx - c.cx) * c.z * W + W / 2, (wy - c.cy) * c.z * W + H / 2];
  const wob = (t) => ({ dx: 0.004 * noise1(t * 0.35, 1), dy: 0.006 * noise1(t * 0.3, 2) });

  // ------------------------------------------------------------------ draw the plan
  const inView = (c, bb, m = 0.1) => { const [x0, y0] = toS(c, bb[0], bb[1]), [x1, y1] = toS(c, bb[2], bb[3]); return !(x1 < -m * W || x0 > W * (1 + m) || y1 < -m * H || y0 > H * (1 + m)); };
  function drawPlan(t, tReveal, dur, alpha, c) {
    const g = E.g; g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
    g.fillStyle = `rgba(9,8,7,${0.93 * smoothstep(tReveal - 0.1, tReveal + 0.9, t) * alpha})`; g.fillRect(0, 0, W, H);          // the plan is drawn on dark paper laid over the desk
    const zU = Math.sqrt(c.z);
    // buildings first (beneath the lines), faded in by distance from the heart of the island
    const tb0 = tReveal + dur * 0.45;
    for (let bk = 0; bk < 6; bk++) {
      const p = smoothstep(tb0 + bk * dur * 0.09, tb0 + bk * dur * 0.09 + dur * 0.35, t) * alpha; if (p <= 0) continue;
      g.beginPath(); for (const b of blocks) { if (b.bk !== bk) continue; const [sx, sy] = toS(c, b.x, b.y); if (sx < -30 || sx > W + 30 || sy < -30 || sy > H + 30) continue; const s = c.z * W, ax = b.ux * b.hl * s, ay = b.uy * b.hl * s, bx = -b.uy * b.hd * s, by = b.ux * b.hd * s; g.moveTo(sx - ax - bx, sy - ay - by); g.lineTo(sx + ax - bx, sy + ay - by); g.lineTo(sx + ax + bx, sy + ay + by); g.lineTo(sx - ax + bx, sy - ay + by); g.closePath(); }
      g.fillStyle = rgba(cream, 0.085 * p); g.fill(); g.strokeStyle = rgba(cream, 0.30 * p); g.lineWidth = 1.0 * U; g.stroke();
    }
    // water: the two arms as soft bands with ripple dashes
    for (const s of streets) {
      if (s.kind !== 'water') continue; const p = smoothstep(tReveal, tReveal + dur * 0.5, t) * alpha; if (p <= 0 || !inView(c, s.bb, 0.3)) continue;
      g.beginPath(); s.pts.forEach(([x, y], k) => { const [sx, sy] = toS(c, x, y); k ? g.lineTo(sx, sy) : g.moveTo(sx, sy); });
      g.strokeStyle = rgba(cream, 0.055 * p); g.lineWidth = 0.038 * c.z * W; g.stroke();
      g.save(); g.setLineDash([7 * U, 13 * U]); g.lineDashOffset = -t * 5 * U; g.strokeStyle = rgba(cream, 0.20 * p); g.lineWidth = 1 * U; g.stroke(); g.restore();
    }
    // lines, drawn on in order
    for (const s of streets) {
      if (s.kind === 'water' || !inView(c, s.bb)) continue;
      const p = clamp((t - tReveal - s.ord * dur * 0.62) / (dur * 0.38 + 0.2)); if (p <= 0) continue;
      const n = Math.max(2, Math.floor(s.pts.length * ease.outQuad(p) + 1)); g.beginPath();
      for (let k = 0; k < n && k < s.pts.length; k++) { const [x, y] = toS(c, s.pts[k][0], s.pts[k][1]); if (k) g.lineTo(x, y); else g.moveTo(x, y); }
      if (s.closed && p >= 1) g.closePath();
      g.save(); if (s.dash) g.setLineDash([6 * U, 7 * U]); g.strokeStyle = rgba(cream, Math.min(1, s.a * 1.25) * alpha); g.lineWidth = s.w * U * 1.1 * (s.kind === 'contour' ? 1 : Math.min(1.5, 0.85 + 0.15 * zU)); g.stroke(); g.restore();
    }
    // the island of the town hall, the cathedral, one small touch each (unlabelled)
    const pc = smoothstep(tReveal + dur * 0.7, tReveal + dur * 1.0, t) * alpha;
    if (pc > 0) {
      const [dx, dy] = toS(c, HC[0], HC[1]), s = c.z * W; g.fillStyle = rgba(cream, 0.30 * pc); g.strokeStyle = rgba(cream, 0.75 * pc); g.lineWidth = 1.2 * U;
      g.fillRect(dx - 0.034 * s, dy - 0.012 * s, 0.068 * s, 0.024 * s); g.strokeRect(dx - 0.034 * s, dy - 0.012 * s, 0.068 * s, 0.024 * s);
      for (const [ox, oy] of [[-0.034, -0.05], [0.034, -0.05], [-0.034, 0.05], [0.034, 0.05]]) { g.fillRect(dx + ox * s - 0.007 * s, dy + oy * s * 0.6 - 0.011 * s, 0.014 * s, 0.022 * s); g.strokeRect(dx + ox * s - 0.007 * s, dy + oy * s * 0.6 - 0.011 * s, 0.014 * s, 0.022 * s); }
      const yy = 1.02, [rx, ry] = toS(c, xL(yy), yy); g.beginPath(); g.ellipse(rx, ry, 0.022 * s, 0.045 * s, 0, 0, 6.2832); g.fillStyle = rgba(cream, 0.10 * pc); g.fill(); g.stroke(); g.fillStyle = rgba(cream, 0.34 * pc); g.fillRect(rx - 0.011 * s, ry - 0.016 * s, 0.022 * s, 0.032 * s);
    }
    g.restore();
  }

  // ------------------------------------------------------------------ geometry helpers for graphs
  const verts = []; for (const s of streets) if (['spine', 'lane', 'quay', 'hill', 'alley'].includes(s.kind)) for (const p of s.pts) verts.push(p);
  const snap = (x, y) => { let b = verts[0], bd = 1e9; for (const p of verts) { const d = (p[0] - x) ** 2 + (p[1] - y) ** 2; if (d < bd) { bd = d; b = p; } } return b; };
  const segInter = (a, b, c, d) => { const r = [b[0] - a[0], b[1] - a[1]], s = [d[0] - c[0], d[1] - c[1]], den = r[0] * s[1] - r[1] * s[0]; if (Math.abs(den) < 1e-12) return null; const u = ((c[0] - a[0]) * s[1] - (c[1] - a[1]) * s[0]) / den, v = ((c[0] - a[0]) * r[1] - (c[1] - a[1]) * r[0]) / den; return u >= 0 && u <= 1 && v >= 0 && v <= 1 ? { u, v } : null; };
  const inter = (A, B) => { for (let i = 0; i < A.pts.length - 1; i++) for (let j = 0; j < B.pts.length - 1; j++) { const h = segInter(A.pts[i], A.pts[i + 1], B.pts[j], B.pts[j + 1]); if (h) return { a: i + h.u, b: j + h.v, x: lerp(A.pts[i][0], A.pts[i + 1][0], h.u), y: lerp(A.pts[i][1], A.pts[i + 1][1], h.u) }; } return null; };
  const sub = (S, pa, pb) => { const out = [], fw = pb >= pa, at = (p) => { const i = Math.min(S.pts.length - 2, Math.floor(p)), u = p - i; return [lerp(S.pts[i][0], S.pts[i + 1][0], u), lerp(S.pts[i][1], S.pts[i + 1][1], u)]; }; out.push(at(pa)); if (fw) { for (let i = Math.floor(pa) + 1; i <= Math.floor(pb); i++) out.push(S.pts[i]); } else { for (let i = Math.ceil(pa) - 1; i >= Math.ceil(pb); i--) out.push(S.pts[i]); } out.push(at(pb)); return out; };

  // ================================================================ the chain (x3 to x5)
  const CHW = { n0: [0.50, 1.04], n1: [0.34, 1.19], n2: [0.66, 1.19], n3: [0.24, 1.33], n4: [0.43, 1.33], n5: [0.57, 1.33], n6: [0.76, 1.33], Wf: [0.78, 1.47], J: [0.50, 1.55] };
  const CH = {
    n0: { t: tw('x3', 'someone.'), seed: 1 }, n1: { t: tw('x3', 'names.') + 0.35, seed: 2 }, n2: { t: tw('x3', 'names.') + 0.5, seed: 3 },
    n3: { t: tw('x3', 'arrest', 1) + 0.15, seed: 4 }, n4: { t: tw('x3', 'those') + 0.1, seed: 5 }, n5: { t: tw('x3', 'people.') - 0.05, seed: 6 }, n6: { t: tw('x3', 'people.') + 0.12, seed: 7 },
    J: { t: tw('x4', "Junius's"), seed: 8, big: true }, Wf: { t: tw('x4', 'wife'), seed: 9 },
  };
  for (const k of Object.keys(CH)) { CH[k].w = snap(CHW[k][0], CHW[k][1]); }
  const SIX = [[0.34, 1.50], [0.26, 1.62], [0.36, 1.76], [0.64, 1.76], [0.74, 1.62], [0.66, 1.50]].map(([x, y]) => snap(x, y));
  E.chainNames = () => CH;

  function scrawl(seed, len) {
    const key = seed + '|' + len; if (scrawl.C.has(key)) return scrawl.C.get(key);
    const r = rng(seed * 131 + 7), pts = [[0, 0]]; let x = 0; const xh = 6.5 * U, asc = 16 * U, desc = 9 * U;
    while (x < len * W) {
      const c = (5 + 4 * r()) * U, q = r();
      if (q < 0.34) pts.push([x + 0.22 * c, -xh], [x + 0.5 * c, -0.2 * xh], [x + 0.78 * c, -xh], [x + c, 0]);
      else if (q < 0.64) pts.push([x + 0.3 * c, -0.95 * xh], [x + 0.55 * c, -0.05 * xh], [x + 0.8 * c, -0.75 * xh], [x + c, 0]);
      else if (q < 0.84) pts.push([x + 0.24 * c, -0.7 * asc], [x + 0.4 * c, -asc], [x + 0.52 * c, -0.65 * asc], [x + 0.34 * c, -0.2 * asc], [x + 0.58 * c, 0], [x + c, 0]);
      else pts.push([x + 0.3 * c, -xh], [x + 0.42 * c, 0.25 * desc], [x + 0.4 * c, desc], [x + 0.12 * c, 0.85 * desc], [x + 0.3 * c, -0.1 * xh], [x + c, 0]);
      x += c; if (r() < 0.14) { x += 8 * U; pts.push([x, 0]); }
    }
    const o = { pts: catmull(pts, 4), w: x }; scrawl.C.set(key, o); return o;
  }
  scrawl.C = new Map();
  function drawScrawl(g, sx, sy, seed, len, t0, t, alpha, dur = 0.4, col = cream, lw = 1.7) {
    const p = clamp((t - t0) / dur); if (p <= 0) return; const S = scrawl(seed, len);
    g.save(); g.translate(sx, sy); g.beginPath(); g.rect(-4 * U, -30 * U, (S.w + 8 * U) * p, 60 * U); g.clip();
    g.strokeStyle = rgba(col, alpha); g.lineWidth = lw * U; g.lineJoin = 'round'; g.lineCap = 'round'; g.beginPath(); S.pts.forEach(([x, y], k) => (k ? g.lineTo(x, y) : g.moveTo(x, y))); g.stroke(); g.restore();
  }
  function node(g, sx, sy, t0, t, { r = 10, alpha = 1, col = cream } = {}) {
    const k = (t - t0) / 0.22; if (k <= 0) return; const e = ease.outCubic(clamp(k)), s = lerp(1.7, 1, e);
    g.save(); g.globalAlpha = clamp(k * 3) * alpha; g.strokeStyle = rgba(col, 0.92); g.lineWidth = 1.8 * U; g.fillStyle = 'rgba(14,13,11,0.82)'; g.beginPath(); g.arc(sx, sy, r * U * s, 0, 6.2832); g.fill(); g.stroke();
    g.fillStyle = rgba(col, 0.95); g.beginPath(); g.arc(sx, sy, r * 0.38 * U * s, 0, 6.2832); g.fill();
    const rk = (t - t0) / 0.55; if (rk > 0 && rk < 1) { g.globalAlpha = 0.4 * (1 - rk) * alpha; g.beginPath(); g.arc(sx, sy, (r + 24 * ease.outCubic(rk)) * U, 0, 6.2832); g.stroke(); }
    g.restore();
  }
  function edge(g, a, b, t0, dur, t, { alpha = 0.78, w = 2.4, col = cream, dash = false } = {}) {
    const p = ease.outCubic(clamp((t - t0) / dur)); if (p <= 0) return; const x = lerp(a[0], b[0], p), y = lerp(a[1], b[1], p);
    g.save(); g.strokeStyle = rgba(col, alpha); g.lineWidth = w * U; g.lineCap = 'round'; if (dash) g.setLineDash([6 * U, 6 * U]); g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(x, y); g.stroke(); g.restore();
  }
  function drawChain(t, c) {
    const g = E.g, pos = (k) => toS(c, CH[k].w[0], CH[k].w[1]);
    const tEdge = { n1: tw('x3', 'names.') + 0.05, n2: tw('x3', 'names.') + 0.1, n3: tw('x3', 'arrest', 1) - 0.1, n4: tw('x3', 'those') - 0.05, n5: tw('x3', 'people.') - 0.3, n6: tw('x3', 'people.') - 0.15 };
    const par = { n1: 'n0', n2: 'n0', n3: 'n1', n4: 'n1', n5: 'n2', n6: 'n2' };
    for (const k of Object.keys(par)) edge(g, pos(par[k]), pos(k), tEdge[k], 0.34, t);
    edge(g, pos('n6'), pos('Wf'), tw('x4', 'named.') - 0.1, 0.38, t);
    for (const k of Object.keys(CH)) {
      const o = CH[k], [sx, sy] = pos(k); if (t < o.t) continue;
      node(g, sx, sy, o.t, t, { r: k === 'J' ? 17 : 11 });
      if (k !== 'J' && k !== 'Wf') drawScrawl(g, sx + 17 * U, sy - 2 * U, o.seed, 0.085 + (o.seed % 3) * 0.012, o.t + 0.2, t, 0.92);
    }
    if (t >= CH.Wf.t) { const [sx, sy] = pos('Wf'); E.labelAt(sx - 26 * U, sy + 38 * U, 'HIS WIFE', CH.Wf.t + 0.1); }
    const tx = tw('x4', 'executed.');                                          // she was executed: a heavy X over her node
    if (t >= tx) { const [sx, sy] = pos('Wf'), p = ease.outCubic(clamp((t - tx) / 0.14)), q = ease.outCubic(clamp((t - tx - 0.1) / 0.14)), d = 19 * U; g.save(); g.strokeStyle = rgba(cream, 0.96); g.lineWidth = 3.4 * U; g.lineCap = 'round'; g.beginPath(); g.moveTo(sx - d, sy - d); g.lineTo(sx - d + 2 * d * p, sy - d + 2 * d * p); g.moveTo(sx + d, sy - d); g.lineTo(sx + d - 2 * d * q, sy - d + 2 * d * q); g.stroke(); g.restore(); }
    const tS = [tw('x5', 'six'), tw('x5', 'six') + 0.12, tw('x5', 'people') - 0.02, tw('x5', 'people') + 0.1, tw('x5', 'named') - 0.2, tw('x5', 'named') - 0.08];
    const [jx, jy] = pos('J');
    SIX.forEach(([x, y], n) => {
      const [sx, sy] = toS(c, x, y); if (t < tS[n]) return;
      edge(g, [sx, sy], [jx, jy], tw('x5', 'named') + n * 0.045, 0.3, t, { alpha: 0.95, w: 2.8 });
      node(g, sx, sy, tS[n], t, { r: 11 }); drawScrawl(g, sx + (x > 0.5 ? 17 : -17) * U - (x > 0.5 ? 0 : scrawl(20 + n, 0.08).w), sy - 2 * U, 20 + n, 0.08, tS[n] + 0.15, t, 0.92);
    });
    if (t >= CH.J.t) { node(g, jx, jy, CH.J.t, t, { r: 17 }); E.labelAt(jx - 30 * U, jy + 40 * U, 'JUNIUS', CH.J.t + 0.1); }
  }

  // ================================================================ the walk (l3, l4): a route that really follows three streets
  const lane1 = crossLanes.find((l) => l.y > 1.00), lane2 = crossLanes.find((l) => l.y > 1.30), lane3 = crossLanes.find((l) => l.y > 1.62);
  const i1 = inter(S1, lane1), i2 = inter(S2, lane1), i3 = inter(S2, lane2), i4 = inter(S3, lane2), i5 = inter(S3, lane3), i6 = inter(S1, lane3);
  const LEGS = [sub(S1, i1.a - 3, i1.a), sub(lane1, i1.b, i2.b), sub(S2, i2.a, i3.a), sub(lane2, i3.b, i4.b), sub(S3, i4.a, i5.a), sub(lane3, i5.b, i6.b)];
  const ROUTE = []; LEGS.forEach((l, k) => l.forEach((p, j) => { if (k && !j) return; ROUTE.push(p); }));
  const routeLen = []; let RL = 0; for (let k = 1; k < ROUTE.length; k++) { RL += Math.hypot(ROUTE[k][0] - ROUTE[k - 1][0], ROUTE[k][1] - ROUTE[k - 1][1]); routeLen.push(RL); }
  const legEnds = []; { let acc = 0; LEGS.forEach((l) => { for (let k = 1; k < l.length; k++) acc += Math.hypot(l[k][0] - l[k - 1][0], l[k][1] - l[k - 1][1]); legEnds.push(acc); }); }
  const routeAt = (u) => { const d = clamp(u) * RL; let k = routeLen.findIndex((x) => x >= d); if (k < 0) k = routeLen.length - 1; const d0 = k ? routeLen[k - 1] : 0, f = (d - d0) / ((routeLen[k] - d0) || 1); return [lerp(ROUTE[k][0], ROUTE[k + 1][0], f), lerp(ROUTE[k][1], ROUTE[k + 1][1], f)]; };
  const WALK0 = tw('l3', 'walk'), WALK1 = tw('l3', 'street,') + 0.45;
  const walkHead = (t) => { const k = clamp((t - WALK0) / (WALK1 - WALK0)); return ease.inOutSine(k) * 0.35 + k * 0.65; };
  // names along the route (stations at the corners), then the gift and the multiplication
  const STAT = [i1, i2, i3, i4, i5, i6].map((q) => [q.x, q.y]);
  const NAMES = []; {
    STAT.forEach((p, n) => NAMES.push({ w: p, t: tw('l3', 'name') + n * 0.11, seed: 100 + n }));
    const r = rng(404), used = STAT.slice(), t0 = tw('l4', 'repeated'), t1 = tw('l4', 'it.') + 0.9; let tt = t0;
    for (let k = 0; k < 400; k++) {
      const p = verts[Math.floor(r() * verts.length)]; if (p[1] < 0.2 || p[1] > 2.1 || p[0] < 0.18 || p[0] > 1.25) continue; if (used.some((q) => Math.hypot(q[0] - p[0], q[1] - p[1]) < 0.065)) continue;
      used.push(p); NAMES.push({ w: p, t: tt, seed: 200 + k, late: true }); tt += lerp(0.085, 0.009, clamp(NAMES.length / 70)); if (tt > t1) break;
    }
  }
  E.walkNames = NAMES;
  // camera for the walk: follows the pen with a lag (a pure function of time), goes down to street level, then pulls back over the town as the names multiply
  const T3 = tw('l3', 'they'), T4 = tw('l4', 'when');
  const walkCam = (t) => {
    const z = keys(t, [[T3 - 0.4, 0.95], [WALK0 - 0.1, 0.98], [WALK0 + 1.7, 1.55], [WALK1, 1.62], [T4 + 0.6, 1.40], [tw('l4', 'name.') - 0.5, 1.05], [tw('l4', 'it.') + 0.4, 0.88]]);
    let hx = 0, hy = 0, n = 0; for (let s = 0; s <= 8; s++) { const [x, y] = routeAt(walkHead(Math.max(WALK0, t - s * 0.14))); hx += x; hy += y; n++; }
    hx /= n; hy /= n;
    const fo = smoothstep(T4 - 0.2, tw('l4', 'it.') + 0.4, t), lead = smoothstep(WALK0 - 0.2, WALK0 + 1.5, t);
    return { cx: lerp(lerp(0.5, hx, lead), 0.58, fo), cy: lerp(lerp(1.15, hy, lead), 1.25, fo) + 0.012 * noise1(t * 0.3, 2), z };
  };
  const cam = (t) => { const c = t >= T3 - 0.5 ? walkCam(t) : camKeys(t, KEYS); const w = wob(t); return { cx: c.cx + w.dx, cy: c.cy + w.dy, z: c.z }; };

  function drawWalk(t, c) {
    const g = E.g, Rs = ROUTE.map(([x, y]) => toS(c, x, y)), p = walkHead(t);
    const segs = []; let L = 0; for (let k = 1; k < Rs.length; k++) { const d = Math.hypot(Rs[k][0] - Rs[k - 1][0], Rs[k][1] - Rs[k - 1][1]); segs.push(d); L += d; }
    let acc = 0, head = Rs[0]; const reach = p * routeLen[routeLen.length - 1] / RL * L;
    const reachW = p * RL; let accW = 0;
    g.save(); g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); g.moveTo(Rs[0][0], Rs[0][1]);
    for (let k = 1; k < Rs.length; k++) { const dW = routeLen[k - 1] - (k > 1 ? routeLen[k - 2] : 0); if (reachW <= accW) break; const u = clamp((reachW - accW) / dW); const hx = lerp(Rs[k - 1][0], Rs[k][0], u), hy = lerp(Rs[k - 1][1], Rs[k][1], u); g.lineTo(hx, hy); head = [hx, hy]; accW += dW; if (u < 1) break; }
    g.strokeStyle = rgba(cream, 0.7); g.lineWidth = 3.4 * U; g.stroke();
    // "street by street": the three legs that carry the words flash on their beats
    const flashes = [tw('l3', 'street'), tw('l3', 'by'), tw('l3', 'street,')], legPts = [LEGS[1], LEGS[2], LEGS[3]];
    legPts.forEach((l, i) => { const f0 = flashes[i]; if (t < f0) return; const u = clamp((t - f0) / 0.55), w = lerp(7, 3.4, ease.outCubic(u)); g.strokeStyle = rgba(cream, lerp(0.98, 0.7, u)); g.lineWidth = w * U; g.beginPath(); l.forEach(([x, y], k) => { const [sx, sy] = toS(c, x, y); k ? g.lineTo(sx, sy) : g.moveTo(sx, sy); }); g.stroke(); });
    g.restore();
    if (t >= WALK0 && t < WALK1 + 0.5) { g.save(); g.fillStyle = rgba(cream, 1); g.beginPath(); g.arc(head[0], head[1], 5.5 * U, 0, 6.2832); g.fill(); g.globalAlpha = 0.25; g.beginPath(); g.arc(head[0], head[1], 15 * U, 0, 6.2832); g.fill(); g.restore(); }
    for (const nm of NAMES) {
      if (t < nm.t) continue; const [sx, sy] = toS(c, nm.w[0], nm.w[1]); if (sx < -60 || sx > W + 60 || sy < -40 || sy > H + 40) continue;
      node(g, sx, sy, nm.t, t, { r: nm.late ? 7.5 : 11, alpha: nm.late ? 0.92 : 1 }); drawScrawl(g, sx + 14 * U, sy - 2 * U, nm.seed, 0.06 + (nm.seed % 4) * 0.012, nm.t + 0.1, t, 0.92, nm.late ? 0.22 : 0.4, cream, nm.late ? 1.4 : 1.7);
    }
    // the empty slot ("when he could not think of anyone"), then the typed slip of cold paper the court drops into it
    const tBlank = tw('l4', 'anyone,') - 0.35, last = STAT[STAT.length - 1], slot = [last[0] + 0.11, last[1] - 0.045], [bx, by] = toS(c, slot[0], slot[1]), [lx, ly] = toS(c, last[0], last[1]);
    if (t >= tBlank) { const k = clamp((t - tBlank) / 0.3); g.save(); g.setLineDash([5 * U, 5 * U]); g.strokeStyle = rgba(cream, 0.85 * k); g.lineWidth = 1.8 * U; g.beginPath(); g.arc(bx, by, 10 * U, 0, 6.2832); g.stroke(); g.restore(); edge(g, [lx, ly], [bx, by], tBlank - 0.1, 0.3, t, { alpha: 0.5, dash: true }); }
    const tGift = tw('l4', 'name.') - 0.05, tg0 = tw('l4', 'gave') + 0.05;
    if (t >= tg0) {
      const k = clamp((t - tg0) / (tGift + 0.05 - tg0)), e = ease.inCubic(k), sw = 0.26 * W, sh = 0.036 * H, offy = (1 - e) * 0.28 * H, rot = (1 - e) * -0.18;
      const land = (t - tGift - 0.05) * 24, sc = land < 0 ? 1 : keys(land, [[0, 1.12], [1, 1.04], [2, 0.995], [3, 1.0]]);
      g.save(); g.translate(bx + 10 * U + sw / 2, by - offy); g.rotate(rot); g.scale(sc, sc); g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 14 * U; g.shadowOffsetY = 5 * U;
      g.fillStyle = '#d9dcdc'; g.fillRect(-sw / 2, -sh / 2, sw, sh); g.shadowColor = 'rgba(0,0,0,0)';
      g.fillStyle = '#14171a'; g.font = `400 ${0.021 * H}px "Special Elite"`; g.letterSpacing = (0.08 * 0.021 * H) + 'px'; g.textBaseline = 'middle'; g.textAlign = 'center'; g.fillText('NAME', 0, 1 * U); g.restore();
    }
  }
  E.labelAt = (x, y, txt, t0) => { if (E.t < t0) return; const a = clamp((E.t - t0) / 0.2); E.ink.save(); E.ink.font = `400 ${0.023 * H}px "Bebas Neue"`; E.ink.letterSpacing = (0.14 * 0.023 * H) + 'px'; E.ink.fillStyle = rgba(cream, 0.92 * a); E.ink.fillText(txt, x, y); E.ink.restore(); };
  E.mapAPI = { cam, toS, drawPlan, drawChain, drawWalk };
  E.mapDebug = { streets: streets.length, blocks: blocks.length, RL, legs: LEGS.map((l) => l.length) };
  return E.mapAPI;
}
