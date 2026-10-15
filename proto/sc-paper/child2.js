// child.js — the child puppet for "The Shadow at the Pass". Feet at (0,0), faces +x, ~72 authoring px tall at s = 1.
// Every piece is cut once (fixed scissor wobble, no boiling); poses only rotate pivots, like a jointed paper puppet.
// The child carries a bundle of firewood on its back: two forked sticks rise above the head. Tiny on the child,
// they become the HORNS of the monster when the low sun throws the silhouette five times larger onto the rock wall.
import { cut, circle, piece } from '/proto/p09-paper-kingdom/paper.js';
import { lerp, clamp } from '/harness/kit/film.js';

export const LEG = { thigh: 15, shin: 14.5 };      // hip-to-knee, knee-to-sole (sole thickness ~1)
export const ARM = { up: 10.5, fore: 10 };
const C = {};
export function buildChild() {
  // pieces are authored around their own pivot (limbs hang toward +y; rotate(-a) swings them forward)
  C.thigh = cut('M -4.4 -1.5 L 4.2 -1.5 L 3.4 15.6 L -3.2 15.6 Z', { seed: 801, amp: 0.25, step: 2 });
  C.shin = cut('M -3.2 -0.8 L 3.1 -0.8 L 2.8 12.6 L 6.6 13.2 Q 8.6 13.8 8.4 15.4 L -3.2 15.4 Z', { seed: 802, amp: 0.25, step: 2 });
  C.upper = cut('M -3.1 -1.6 L 3.1 -1.6 L 2.5 11.2 L -2.5 11.2 Z', { seed: 803, amp: 0.2, step: 2 });
  C.fore = cut('M -2.4 -0.8 L 2.4 -0.8 L 2.2 9.0 Q 4.2 10.6 2.6 12.8 Q 0 14.4 -2.4 12.4 Q -3.0 10.4 -2.2 9.0 Z', { seed: 804, amp: 0.2, step: 2 });
  // tunic from the hip pivot (0,0) up to the neck (0,-24); a flared hem covers the top of the thighs
  C.torso = cut('M -10.5 9 L -8.5 2 L -7.4 -14 Q -7.6 -22 -3.2 -25 L 3.8 -25 Q 7.8 -22 7.4 -14 L 8.6 2 L 11 9 L 8 7.6 L 5 9.4 L 2 7.8 L -1 9.4 L -4 7.8 L -7 9.4 Z', { seed: 805, amp: 0.3, step: 2 });
  // head around the neck pivot (0,0): round skull, a small nose, a fringe of hair falling back
  C.head = cut('M -2.6 1.5 Q -9.6 -1.2 -9.4 -9.4 Q -9.2 -17.8 -1.2 -19.2 Q 6.4 -19.6 8.6 -12.4 L 10.6 -9.6 L 8.8 -8.6 Q 9 -4.6 6.2 -2.6 Q 3.6 0.4 2.6 1.6 Z '
    + 'M -9.6 -12 L -13.4 -10.6 L -11 -14.2 L -14.6 -15.6 L -10.2 -17.4 L -8.6 -16 Z', { seed: 806, amp: 0.25, step: 1.6 });
  C.pony = cut('M -8 -15 Q -18 -16 -22 -6 Q -20 2 -15 6 Q -17 -2 -13 -8 Q -10 -11 -7 -11 Z M -9 -18 L -15 -23 L -14 -15 L -9 -16 L -4 -22 L -5 -14 Z', { seed: 815, amp: 0.2, step: 1.2 });
  C.eye = cut(circle(5.0, -11.4, 1.05, 8), { seed: 807, amp: 0.05 });
  // the firewood bundle: a wrapped roll across the back + sticks; authored in torso space (hip pivot)
  C.roll = cut('M -18 -3 Q -21.5 -14 -16.5 -25.5 L -6 -26 Q -4 -14 -6 -2 Z', { seed: 808, amp: 0.4, step: 2 });
  C.strap = cut('M -7.4 -21.6 L 4.6 -10.4 L 4.2 -8.6 L -7.6 -19.4 Z', { seed: 809, amp: 0.15, step: 2 });
  const stick = (x0, y0, x1, y1, w, cx, cy, fork) => {          // a tapering curved stick with an optional fork near the tip
    const nx = -(y1 - y0), ny = x1 - x0, L = Math.hypot(nx, ny), ux = nx / L, uy = ny / L;
    let d = `M ${x0 + ux * w} ${y0 + uy * w} Q ${cx + ux * w * 0.6} ${cy + uy * w * 0.6} ${x1 + ux * 0.35} ${y1 + uy * 0.35} L ${x1 - ux * 0.35} ${y1 - uy * 0.35} Q ${cx - ux * w * 0.6} ${cy - uy * w * 0.6} ${x0 - ux * w} ${y0 - uy * w} Z `;
    if (fork) { const [fx, fy, tx, ty] = fork; d += `M ${fx - 0.8} ${fy + 0.6} L ${tx - 0.3} ${ty} L ${tx + 0.4} ${ty + 0.2} L ${fx + 0.9} ${fy - 0.4} Z `; }
    return d;
  };
  C.sticks = cut(
    stick(-9, -14, 7, -64, 1.8, -17, -50, [-1.2, -55, 6.5, -52]) +       // front horn: rises behind the head, curls forward over it
    stick(-12, -13, -19, -63, 1.8, -29, -40, [-24.5, -48, -31, -51]) +    // back horn: sweeps out behind, then up
    stick(-13, -10, -34, -32, 1.3, -24, -24, null) +                       // spines along the back
    stick(-14, -6, -33, -16, 1.2, -24, -13, null) +
    stick(-12, -12, -27, -44, 1.1, -22, -30, null),
    { seed: 810, amp: 0.15, step: 1.5 });
  C.scarf = cut('M -2.6 -1.6 L 3 -1.6 L 3 2.4 L -2.6 2.6 Z', { seed: 811, amp: 0.15, step: 1.5 });
  C.tail = [0, 1, 2].map((k) => cut(`M 0 -1.6 Q -7 ${-2.6 + k * 1.6} -15 ${-0.8 + k * 2.2} L -16.5 ${2.8 + k * 1.4} L -13.8 ${1.6 + k * 1.8} Q -7 ${2.6 + k} 0 2.2 Z`, { seed: 812 + k, amp: 0.15, step: 1.5 }));
}

// ---------------------------------------------------------------- pose helpers
// P: { x, y, s, face (+1 right / -1 left), squash (x-scale for the turn in-between), lean, hipY (hip height above the feet; null = from legs),
//      tL, kL, tR, kR (thigh forward angle, knee bend), aL, eL, aR, eR (shoulder forward angle, elbow bend), head (tilt, + = chin up), look (+1 forward / -1 back over the shoulder),
//      wind (scarf flutter phase 0..2), blink }
export function legDrop(t, k) { return LEG.thigh * Math.cos(t) + LEG.shin * Math.cos(t - k); }
export function hipFromLegs(P) { return Math.max(legDrop(P.tL, P.kL), legDrop(P.tR, P.kR)); }

function limb(g, a, b, angA, bend, PA, PB, len, st) {      // two-segment limb drawn from its root pivot
  g.save(); g.rotate(-angA); piece(g, PA, st); g.translate(0, len); g.rotate(bend); piece(g, PB, st); g.restore();
}
// st = piece style (INK for the puppet, a flat fill for the cast shadow); hot = optional brighter rim style for the CU
export function drawChild(g, P, st, { hot = null, hotW = 0, sticks = true } = {}) {
  const hip = P.hipY ?? hipFromLegs(P);
  g.save(); g.translate(P.x, P.y); g.scale(P.s * P.face * (P.squash ?? 1), P.s);
  g.translate(0, -hip);
  // far side first (the same black paper: overlaps merge, the silhouette reads as one figure)
  g.save(); g.rotate(P.lean); g.translate(0.5, -22);
  limb(g, null, null, P.aL, -P.eL, C.upper, C.fore, ARM.up, st); g.restore();
  limb(g, null, null, P.tL, P.kL, C.thigh, C.shin, LEG.thigh, st);
  g.save(); g.rotate(P.lean);
  if (sticks) { piece(g, C.sticks, st); piece(g, C.roll, st); }
  piece(g, C.torso, st); if (sticks) piece(g, C.strap, st);
  g.restore();
  limb(g, null, null, P.tR, P.kR, C.thigh, C.shin, LEG.thigh, st);
  g.save(); g.rotate(P.lean); g.translate(0, -24);
  piece(g, C.scarf, st);
  const w = P.wind ?? 0; g.save(); g.translate(-1, 0.4); g.rotate(-0.12 + 0.07 * Math.sin(w * Math.PI)); piece(g, C.tail[((Math.floor(w * 1.5) % 3) + 3) % 3], st); g.restore();
  g.save(); g.rotate(-(P.head ?? 0)); if ((P.look ?? 1) < 0) g.scale(-1, 1);
  piece(g, C.head, hot ? { ...st, rimStyle: hot, rimW: hotW } : st); if (!sticks) piece(g, C.pony, st);
  g.restore(); g.restore();
  // near arm last
  g.save(); g.rotate(P.lean); g.translate(-0.5, -22);
  if (hot) { g.rotate(-P.aR); piece(g, C.upper, { ...st, rimStyle: hot, rimW: hotW }); g.translate(0, ARM.up); g.rotate(-P.eR); piece(g, C.fore, { ...st, rimStyle: hot, rimW: hotW }); }
  else limb(g, null, null, P.aR, -P.eR, C.upper, C.fore, ARM.up, st);
  g.restore();
  g.restore();
}

// ---------------------------------------------------------------- gaits (phase p in cycles; returns joint angles)
export const STRIDE_WALK = 2 * 2 * 29.5 * Math.sin(0.40) * 0.92;   // distance per full cycle (two steps), sole-locked approx
export const STRIDE_RUN = 2 * 2 * 29.5 * Math.sin(0.70) * 1.05;
export function walk(p, amp = 0.40) {
  const a = 2 * Math.PI * p;
  const tR = amp * Math.sin(a), tL = amp * Math.sin(a + Math.PI);
  const kn = (ph) => 0.08 + 0.75 * Math.max(0, Math.sin(ph - 0.6)) ** 1.4;   // the knee folds while the leg swings through
  return { tR, tL, kR: kn(a), kL: kn(a + Math.PI), aR: -0.42 * Math.sin(a), aL: 0.42 * Math.sin(a), eR: 0.35, eL: 0.35, lean: 0.06 };
}
export function run(p) {
  const a = 2 * Math.PI * p;
  const tR = 0.70 * Math.sin(a), tL = 0.70 * Math.sin(a + Math.PI);
  const kn = (ph) => 0.2 + 1.45 * Math.max(0, Math.sin(ph - 0.4)) ** 1.2;
  return { tR, tL, kR: kn(a), kL: kn(a + Math.PI), aR: -0.95 * Math.sin(a), aL: 0.95 * Math.sin(a), eR: 1.35, eL: 1.35, lean: 0.26 };
}
export const STAND = { tR: 0.03, tL: -0.03, kR: 0.06, kL: 0.06, aR: 0.05, aL: -0.05, eR: 0.25, eL: 0.25, lean: 0.02 };
export const CROUCH = { tR: 1.75, tL: 1.55, kR: 2.55, kL: 2.65, aR: 0.6, aL: 0.4, eR: 1.6, eL: 1.7, lean: 0.62, head: -0.2 };
export const SIT = { tR: 1.95, tL: 1.85, kR: 2.75, kL: 2.65, aR: 1.05, aL: 0.95, eR: 0.95, eL: 1.0, lean: 0.16, head: -0.38, hipY: 5.5 };
export function mixPose(A, B, u) {
  const out = {}; for (const k of new Set([...Object.keys(A), ...Object.keys(B)])) if (k !== 'hipY') out[k] = lerp(A[k] ?? 0, B[k] ?? 0, clamp(u));
  out.hipY = lerp(A.hipY ?? hipFromLegs(A), B.hipY ?? hipFromLegs(B), clamp(u));   // resolve the hip height of each pose, then blend
  return out;
}
