// p03 traveler — gait planned in world space (units: H = figure height), posed on 2s, painted as a silhouette.
// Contact never slides: heel-strike rotates the foot about the heel, heel-off rotates it about the toe (R-5-07).
import { clamp, lerp, smoothstep, ease } from '/harness/kit/film.js';
import { rgba, mixc, dabOn, hex } from './paint.js';
import { rng } from '/harness/kit/film.js';

const HEEL = 0.04, TOE = 0.068, LF = HEEL + TOE, THIGH = 0.236, SHIN = 0.236;

// ------------------------------------------------------------------ plans
// contacts: [{t, foot, x}] sorted; body(t) -> x; ground(x) -> y (H units)
export function makePlan({ T, L, body, contacts, ground = () => 0, staffFoot = 1, staffAhead = 0.17, lookUp = null, stopT = null, brake = null, ignite = null }) {
  const plants = [[], []];
  contacts.forEach((c, i) => {
    // lift-off shortly after the other foot strikes (double support 12% of a step)
    const other = contacts.slice(i + 1).find((d) => d.foot !== c.foot);
    plants[c.foot].push({ t: c.t, x: c.x, off: other ? other.t + 0.12 * T : Infinity });
  });
  // the last plant of each foot in an arrival stays down for good
  if (stopT) for (const f of [0, 1]) { const pl = plants[f]; if (pl.length) pl[pl.length - 1].off = Infinity; }
  const staff = contacts.filter((c) => c.foot === staffFoot).map((c) => ({ t: c.t, x: c.x + staffAhead }));
  return { T, L, body, contacts, plants, ground, staff, lookUp, stopT, brake, ignite };
}
export function continuousPlan({ T, L, x0, v, phase0, t0, t1, ground }) {
  const body = (t) => x0 + v * t; const contacts = [];
  for (let k = Math.floor((t0 - phase0) / T) - 3; k <= Math.ceil((t1 - phase0) / T) + 3; k++) { const t = phase0 + k * T; contacts.push({ t, foot: ((k % 2) + 2) % 2, x: body(t) + 0.5 * L }); }
  return makePlan({ T, L, body, contacts, ground });
}

// ------------------------------------------------------------------ pose
function footAt(pl, t, T, ground) {
  let k = -1; for (let i = 0; i < pl.length; i++) { if (pl[i].t <= t) k = i; else break; }
  const fin = (heel, toe, a) => ({ heel, toe, a, ankle: [heel[0] + 0.03 * Math.cos(a) - 0.052 * Math.sin(a), heel[1] + 0.03 * Math.sin(a) + 0.052 * Math.cos(a)] });
  if (k < 0) k = 0;
  const p = pl[k];
  if (t < p.t) { const gy = ground(p.x); return fin([p.x - HEEL, gy], [p.x + TOE, gy], 0); }
  if (t <= p.off) {
    const gy = ground(p.x); const land = clamp((t - p.t) / (0.16 * T)); const a0 = 0.30 * (1 - ease.outQuad(land));
    if (a0 > 1e-4) { const heel = [p.x - HEEL, gy]; return fin(heel, [heel[0] + LF * Math.cos(a0), gy + LF * Math.sin(a0)], a0); }
    if (p.off !== Infinity) { const h = clamp((t - (p.off - 0.34 * T)) / (0.34 * T)); const b = -0.6 * ease.inQuad(h);
      if (b < -1e-4) { const toe = [p.x + TOE, gy]; return fin([toe[0] - LF * Math.cos(b), gy - LF * Math.sin(b)], toe, b); } }
    return fin([p.x - HEEL, gy], [p.x + TOE, gy], 0);
  }
  const q = pl[k + 1]; if (!q) { const gy = ground(p.x); return fin([p.x - HEEL, gy], [p.x + TOE, gy], 0); }
  const u = clamp((t - p.off) / (q.t - p.off)); const e = ease.inOutSine(u); const a = lerp(-0.6, 0.30, smoothstep(0.05, 0.95, u));
  const g0 = ground(p.x), g1 = ground(q.x); const toe0 = [p.x + TOE, g0]; const heel0 = [toe0[0] - LF * Math.cos(-0.6), g0 + LF * Math.sin(0.6)];
  const heel1 = [q.x - HEEL, g1]; const lift = 0.055 * Math.sin(Math.PI * Math.pow(u, 0.8)) * clamp((q.x - p.x) / 0.3, 0.3, 1);
  const heel = [lerp(heel0[0], heel1[0], e), lerp(heel0[1], heel1[1], e) + lift];
  return fin(heel, [heel[0] + LF * Math.cos(a), heel[1] + LF * Math.sin(a)], a);
}
function ik(hip, end, a, b, bendSign = 1) {
  const dx = end[0] - hip[0], dy = end[1] - hip[1]; const d = Math.min(Math.hypot(dx, dy), a + b - 1e-4);
  const c = clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1); const base = Math.atan2(dy, dx); const ang = base + bendSign * Math.acos(c);
  return [hip[0] + a * Math.cos(ang), hip[1] + a * Math.sin(ang)];
}
const lastContact = (plan, t) => { let c = null; for (const k of plan.contacts) { if (k.t <= t) c = k; else break; } return c; };
const speedAt = (plan, t) => (plan.body(t + 0.01) - plan.body(t - 0.01)) / 0.02;

// secondary motion: lantern pendulum + cloak-hem spring, integrated deterministically from tStart to t (dt = 1/480)
export function simulate(plan, tStart, t, handX) {
  const dt = 1 / 480; let phi = 0, w = 0, h = -0.05, hv = 0; const g = 9.81 / 1.75, l = 0.11; const v0 = plan.L / plan.T;
  let x0 = handX(tStart - dt), x1 = handX(tStart);
  for (let s = tStart; s < t; s += dt) {
    const x2 = handX(s + dt); const acc = (x2 - 2 * x1 + x0) / (dt * dt); x0 = x1; x1 = x2;
    const al = -(g / l) * Math.sin(phi) - 2 * 0.16 * Math.sqrt(g / l) * w - (acc / l) * Math.cos(phi); w += al * dt; phi += w * dt;
    const sp = speedAt(plan, s); const target = -0.018 - 0.05 * clamp(sp / v0, 0, 1.2); const om = 11; hv += (-om * om * (h - target) - 2 * 0.32 * om * hv) * dt; h += hv * dt;
  }
  return { phi, hem: h };
}

export function pose(plan, t, tSimStart) {
  const T = plan.T, v0 = plan.L / plan.T; const bx = plan.body(t); const sp = speedAt(plan, t); const walking = clamp(sp / v0, 0, 1);
  const c = lastContact(plan, t); const ph = c ? clamp((t - c.t) / T, 0, 1) : 0; const gb = plan.ground(bx);
  let hipY = 0.505 - 0.016 * walking * (0.5 + 0.5 * Math.cos(2 * Math.PI * ph));
  let lean = 0.075 * walking, head = -0.12 * walking - 0.02;
  if (plan.stopT) { // arrival: brake (lean back = anticipation), plant, sink-and-settle, breathe, look up
    const b = plan.brake; lean += -0.07 * smoothstep(b, b + 0.25, t) * (1 - smoothstep(plan.stopT - 0.05, plan.stopT + 0.35, t)) + 0.012 * smoothstep(plan.stopT, plan.stopT + 0.4, t);
    const ts = plan.stopT; const sink = t > ts ? 0.02 * Math.sin(Math.PI * clamp((t - ts) / 0.3)) * Math.exp(-(t - ts) * 1.5) - 0.004 * Math.sin(Math.PI * clamp((t - ts - 0.3) / 0.25)) : 0;
    hipY -= sink; hipY = lerp(hipY, 0.512 + 0.003 * Math.sin(2 * Math.PI * (t - ts) / 3.4), smoothstep(ts + 0.05, ts + 0.5, t));
    if (plan.lookUp) { const [a, z] = plan.lookUp; const k = ease.inOutCubic(clamp((t - a) / (z - a))); const over = 0.04 * Math.sin(Math.PI * clamp((t - z) / 0.25)) * (t > z ? 1 : 0); head = lerp(head, 0.62, k) + over * 0.4; lean = lerp(lean, -0.01, k); }
    if (plan.ignite && t > plan.ignite) { const r = smoothstep(plan.ignite, plan.ignite + 0.3, t) * (1 - 0.3 * smoothstep(plan.ignite + 0.3, plan.ignite + 1.0, t)); lean -= 0.02 * r; head += 0.04 * r; }
  }
  hipY += gb; // everything above the feet rides on the ground height under the body
  const hip = [bx, hipY]; const feet = [0, 1].map((f) => footAt(plan.plants[f], t, T, plan.ground));
  const knees = feet.map((f) => ik(hip, f.ankle, THIGH, SHIN, 1));
  // arms: near (lantern) swings counter to the near leg; far hand grips the staff
  const lc = c ? c.t : 0; const swing = 0.022 * walking * Math.sin(Math.PI * (t - lc) / T + (c && c.foot === 0 ? 0 : Math.PI));
  const handN = [bx + 0.155 + swing + 0.01 * (1 - walking), hipY + 0.012 + 0.01 * (1 - walking)];
  const handF = [bx + 0.125 - swing * 0.5, hipY + 0.155];
  // staff tip: planted with the far foot, swung forward between plants
  let tip = null; const S = plan.staff;
  for (let i = 0; i < S.length; i++) { if (S[i].t > t) { const prev = S[i - 1]; if (!prev) { tip = [S[i].x, plan.ground(S[i].x)]; break; }
      const lift0 = S[i].t - 0.42 * T; if (t < lift0) tip = [prev.x, plan.ground(prev.x)]; else { const u = ease.inOutSine(clamp((t - lift0) / (S[i].t - lift0))); tip = [lerp(prev.x, S[i].x, u), lerp(plan.ground(prev.x), plan.ground(S[i].x), u) + 0.05 * Math.sin(Math.PI * u)]; }
      break; } }
  if (!tip) { const l = S[S.length - 1]; tip = [l.x, plan.ground(l.x)]; }
  const sd = [handF[0] - tip[0], handF[1] - tip[1]]; const sl = Math.hypot(sd[0], sd[1]); const top = [tip[0] + sd[0] / sl * 1.1, tip[1] + sd[1] / sl * 1.1];
  const sim = simulate(plan, tSimStart, t, (s) => { const b = plan.body(s); const cc = lastContact(plan, s); const w2 = clamp(speedAt(plan, s) / v0, 0, 1); const sw = 0.022 * w2 * Math.sin(Math.PI * (s - (cc ? cc.t : 0)) / T + (cc && cc.foot === 0 ? 0 : Math.PI)); return b + 0.155 + sw; });
  const flutter = 0.012 * walking * Math.sin(2 * Math.PI * (t - lc) / T);
  return { t, bx, hip, hipY, lean, head, feet, knees, handN, handF, staff: { tip, top }, phi: sim.phi, hem: sim.hem + flutter, walking, ground: plan.ground };
}

// ------------------------------------------------------------------ drawing
const rot = (p, o, a) => { const c = Math.cos(a), s = Math.sin(a); const dx = p[0] - o[0], dy = p[1] - o[1]; return [o[0] + dx * c - dy * s, o[1] + dx * s + dy * c]; };
export const PAL = { cloak: hex('#131524'), cloakLit: hex('#2c3050'), far: hex('#1e2137'), near: hex('#14162a'), boot: hex('#111220'), staff: hex('#2b2531'), frame: hex('#1c1414'),
  paperLit: hex('#ffe0a6'), paperOff: hex('#5f586c'), rimCool: hex('#6d76a8'), rimWarm: hex('#ffc27a'), face: hex('#0b0c15') };
// M: { ox, oy, s } maps (X,Y) in H units -> screen (ox + X*s, oy - Y*s). opt: { tiny, lantern:0..1, warm:0..1 (gate light), cool:0..1, lightDir:[x,y] }
export function drawTraveler(g, P, M, opt = {}) {
  const S = (p) => [M.ox + p[0] * M.s, M.oy - p[1] * M.s]; const s = M.s; const tiny = !!opt.tiny; const minW = tiny ? 1.25 : 2;
  const hip = P.hip; const L = (p) => rot([hip[0] + p[0], hip[1] + p[1]], hip, -P.lean); // body-local -> world (lean forward = clockwise)
  // head keeps itself more upright than the torso (30% of the lean) and adds its own tilt (+ = looking up)
  const neck = L([0.012, 0.305]); const H = (p) => rot([neck[0] + p[0], neck[1] + p[1]], neck, -P.lean * 0.3 + P.head);
  const line = (a, b, w, col) => { const A = S(a), B = S(b); g.strokeStyle = rgba(col); g.lineWidth = Math.max(minW, w * s); g.lineCap = 'round'; g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.stroke(); };
  const poly = (pts, col, close = true) => { const p = new Path2D(); pts.forEach((q, i) => { const Q = S(q); i ? p.lineTo(Q[0], Q[1]) : p.moveTo(Q[0], Q[1]); }); if (close) p.closePath(); if (col) { g.fillStyle = rgba(col); g.fill(p); } return p; };
  const smooth = (pts, col) => { const P2 = pts.map(S); const p = new Path2D(); p.moveTo((P2[0][0] + P2[1][0]) / 2, (P2[0][1] + P2[1][1]) / 2);
    for (let i = 1; i <= P2.length; i++) { const a = P2[i % P2.length], b = P2[(i + 1) % P2.length]; p.quadraticCurveTo(a[0], a[1], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2); } p.closePath(); if (col) { g.fillStyle = rgba(col); g.fill(p); } return p; };
  const boot = (f, col) => { const a = f.a; const h = f.heel, t2 = f.toe; const up = [-Math.sin(a), Math.cos(a)];
    poly([[h[0] - 0.008 * up[0], h[1] + 0.0], [t2[0], t2[1]], [t2[0] + up[0] * 0.022 - 0.012 * Math.cos(a), t2[1] + up[1] * 0.022], [f.ankle[0] + up[0] * 0.01 + 0.02 * Math.cos(a), f.ankle[1] + 0.006], [f.ankle[0] - 0.024 * Math.cos(a), f.ankle[1] + 0.004], [h[0] - 0.006, h[1] + 0.03]], col); };
  // --- far side: far leg, staff, far arm   (opt.parts: 'all' | 'body' (no staff) | 'staff')
  const parts = opt.parts || 'all';
  if (parts === 'staff') { line(P.staff.tip, P.staff.top, 0.03, PAL.staff); return { staff: [S(P.staff.tip), S(P.staff.top)] }; }
  const [fN, fF] = [0, 1]; const farCol = opt.farCol || PAL.far;
  line(P.hip, P.knees[fF], 0.07, farCol); line(P.knees[fF], P.feet[fF].ankle, 0.055, farCol); boot(P.feet[fF], farCol);
  if (parts === 'all') line(P.staff.tip, P.staff.top, 0.028, PAL.staff);
  const shF = L([0.0, 0.265]); const elF = ik(shF, P.handF, 0.17, 0.16, -1); line(shF, elF, 0.06, farCol); line(elF, P.handF, 0.05, farCol);
  // --- near leg
  line(P.hip, P.knees[fN], 0.075, PAL.near); line(P.knees[fN], P.feet[fN].ankle, 0.058, PAL.near); boot(P.feet[fN], PAL.boot);
  // --- cloak (hangs from the shoulders; hem trails with motion + wind; front flares with the leading knee)
  const kf = Math.max(0, Math.max(P.knees[0][0], P.knees[1][0]) - P.bx - 0.03); const tr = P.hem; const hemY = -0.225;
  const cloakPts = [L([0.05, 0.305]), L([0.088, 0.17]), L([0.105, 0.03]), L([0.125 + kf * 0.55, hemY + 0.012]), L([0.05 + kf * 0.2, hemY - 0.012]), L([-0.04 + tr * 0.4, hemY + 0.004]),
    L([-0.135 + tr * 1.2, hemY + 0.03 + Math.max(0, -tr) * 0.25]), L([-0.125 + tr * 0.6, 0.02]), L([-0.1 + tr * 0.25, 0.17]), L([-0.07, 0.29])];
  const cloakPath = smooth(cloakPts, PAL.cloak);
  // --- hood (pointed tip trails in the wind), face opening in shadow
  const trH = Math.min(0, tr) * 0.5; const hoodPts = [H([-0.072, -0.01]), H([-0.098, 0.07]), H([-0.13 + trH, 0.165]), H([-0.055, 0.19]), H([0.025, 0.178]), H([0.075, 0.125]), H([0.083, 0.065]), H([0.058, 0.018]), H([0.035, -0.02])];
  const hoodPath = smooth(hoodPts, PAL.cloak);
  if (!tiny) { smooth([H([0.03, 0.115]), H([0.07, 0.112]), H([0.075, 0.06]), H([0.05, 0.03]), H([0.028, 0.06])], PAL.face); }
  // --- near arm (sleeve) + hand, lantern on a short bail
  const shN = L([0.03, 0.262]); const elN = ik(shN, P.handN, 0.17, 0.165, -1); line(shN, elN, 0.072, PAL.cloak); line(elN, P.handN, 0.058, PAL.cloak); line(P.handN, P.handN, 0.04, PAL.near);
  const piv = [P.handN[0], P.handN[1] - 0.012]; const lc = [piv[0] + Math.sin(P.phi) * 0.07, piv[1] - Math.cos(P.phi) * 0.07]; const lit = opt.lantern ?? 1;
  line(piv, [piv[0] + Math.sin(P.phi) * 0.03, piv[1] - Math.cos(P.phi) * 0.03], 0.008, PAL.frame);
  const lb = (p) => rot([lc[0] + p[0], lc[1] + p[1]], lc, P.phi);
  poly([lb([-0.025, 0.04]), lb([0.025, 0.04]), lb([0.03, -0.035]), lb([-0.03, -0.035])], mixc(PAL.paperOff, PAL.paperLit, lit));
  if (!tiny) { line(lb([-0.03, 0.043]), lb([0.03, 0.043]), 0.012, PAL.frame); line(lb([-0.033, -0.038]), lb([0.033, -0.038]), 0.012, PAL.frame); line(lb([0, 0.04]), lb([0, -0.035]), 0.006, mixc(PAL.frame, PAL.paperLit, 0.3)); }
  // --- light on the figure (full size only): lantern underlight, cool sky rim, warm gate rim
  if (!tiny) {
    const all = new Path2D(); all.addPath(cloakPath); all.addPath(hoodPath);
    const LC = S(lc); g.save(); g.clip(all); g.globalCompositeOperation = 'source-atop';
    const rg = g.createRadialGradient(LC[0], LC[1], 0, LC[0], LC[1], 0.24 * s); rg.addColorStop(0, rgba([255, 170, 90], 0.28 * lit)); rg.addColorStop(1, rgba([255, 150, 80], 0)); g.fillStyle = rg; g.fillRect(LC[0] - 0.4 * s, LC[1] - 0.4 * s, 0.8 * s, 0.8 * s);
    g.restore();
    if (opt.rimLayer) opt.rimLayer(all);
  }
  return { lantern: lc, bbox: null };
}
