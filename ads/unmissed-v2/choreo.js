// Choreography of the cards: where every card is at time t. Pure functions of t (seeded layout), so any frame renders alone.
// Four kinds of card: HERO (surges toward camera on its word), STREAM (the river of notifications), GAP (slips past the camera
// edges into the dark) and CATCH (bends into the ring, orbits once, is absorbed with a flash).
import * as THREE from 'three';
import { seg, lerp, ease, mulberry } from '/ads/lib/motion.js';

export const ZP = 16;           // the plane the stream is timed against (about where the camera sits)
export const RING_R = 3.0;      // centre line of the glass ring
const TAU = Math.PI * 2;
const E = new THREE.Euler(0, 0, 0, 'YXZ');
const qa = new THREE.Quaternion(), qb = new THREE.Quaternion();
const v1 = new THREE.Vector3(), v2 = new THREE.Vector3();

export function buildSpecs(cue) {
  const r = mulberry(20261016), S = [];
  const kinds = ['call', 'message', 'lead', 'missed', 'enquiry'];
  let kc = 0; const nextKind = () => kinds[(kc++ * 2 + (r() < 0.5 ? 1 : 0)) % 5];
  // HERO: two cards per word, landing on the word's beat (the VO word is on the beat; the card is readable there)
  const H = [
    ['call', cue.calls, -2.5, 0.55, 5.0, 0.2, 0.03], ['missed', cue.calls + 0.1, 3.0, -1.2, 2.4, -0.25, -0.04],
    ['message', cue.messages, 2.6, 0.75, 4.8, -0.22, 0.03], ['message', cue.messages + 0.1, -3.2, -1.05, 2.6, 0.24, -0.04],
    ['lead', cue.leads, -1.9, 0.95, 6.4, 0.16, -0.02], ['enquiry', cue.leads + 0.1, 3.0, -0.8, 3.2, -0.22, 0.04],
  ];
  for (const [kind, tW, x, y, zL, yaw, roll] of H) S.push({ type: 'hero', kind, tW, x, y, zL, yaw, roll });
  // STREAM: the river, with a hollow in the middle (where the ring will form)
  const TP = [0.9, 1.35, 1.7, 2.15, 2.55, 3.0, 3.4, 3.85, 4.2, 4.55, 4.95, 5.35, 5.8];
  TP.forEach((tp, i) => { const th = i * 2.399 + 0.6, rad = i >= 10 ? 7.2 + r() * 2 : 4.6 + r() * 3.4;
    S.push({ type: 'stream', kind: nextKind(), tp, v: 9 + r() * 5, x: Math.cos(th) * rad * 1.25, y: Math.sin(th) * rad * 0.72, yaw: (r() - 0.5) * 0.7, pitch: (r() - 0.5) * 0.3, roll: (r() - 0.5) * 0.32, spin: (r() - 0.5) * 0.5 }); });
  // GAP: the ones that slip. They keep streaming, then veer off past the frame edges or away into the dark.
  const GV = [4.45, 4.6, 4.78, 4.92, 5.08, 5.24, 5.4, 5.56, 5.74, 5.92, 6.1];
  GV.forEach((tV, i) => { const side = i % 2 ? 1 : -1, away = i % 5 === 3;
    S.push({ type: 'gap', kind: nextKind(), tV, tp: tV + 0.95, v: 16, x: side * (4.2 + r() * 3.2), y: (r() - 0.5) * 6.4, ax: side * (5 + r() * 3), ay: (r() - 0.5) * 7, dz: away ? -22 : 0,
      yaw: -side * 0.3, pitch: 0, roll: (r() - 0.5) * 0.25, tum: side * (0.7 + r() * 1.0) }); });
  // CATCH: 16 cards arrive from the dark, bend into the ring, orbit it, and are absorbed one by one up to the ignition beat
  const N = 16;
  for (let k = 0; k < N; k++) { const th = k * 2.399 + 1.1;
    S.push({ type: 'catch', k, kind: kinds[(k * 3 + 1) % 5], th, rad: 5.2 + r() * 3.2, v: 11 + r() * 3, tB: cue.ringForm - 0.05 + k * 0.0555, tAb: 9.6 + k * (cue.ignite - 9.6) / (N - 1),
      Ro: 3.75 + (k % 3) * 0.12, zoff: ((k % 3) - 1) * 0.34, yaw: (r() - 0.5) * 0.5, pitch: (r() - 0.5) * 0.25, roll: (r() - 0.5) * 0.3 }); }
  return S;
}

function euler(q, pitch, yaw, roll) { E.set(pitch, yaw, roll, 'YXZ'); q.setFromEuler(E); return q; }

// out: { pos, quat, scale, op, glow }. Returns false when the card is not on screen at t.
export function place(c, t, W, ring, camPos, out) {
  let op = 1, sc = 1, glow = 0;
  if (c.type === 'hero') {
    const s0 = seg(t, c.tW - 0.7, c.tW); if (t < c.tW - 0.7) return false;
    const s = 1 - Math.pow(1 - s0, 2.6), dt = t - c.tW, ex = Math.max(0, dt - 0.55);
    let z = lerp(-20, c.zL, s); if (dt > 0) z += 1.1 * dt; z += 15 * ex * ex;
    out.pos.set(c.x + Math.sign(c.x) * 7 * ex * ex, c.y + 1.6 * ex * ex, z);
    euler(out.quat, 0, c.yaw * (1 - 0.5 * s) + Math.sign(c.x) * -0.5 * ex, c.roll);
    sc = 1 + (dt > 0 ? 0.1 * Math.exp(-dt * 12) : 0); glow = (dt > 0 ? 0.9 * Math.exp(-dt * 7) : 0);
    op = (1 - seg(ex, 0.08, 0.42)) * ease.outCubic(seg(t, c.tW - 0.7, c.tW - 0.3));
  } else if (c.type === 'stream' || c.type === 'gap') {
    const z0 = ZP - c.v * (W(c.tp) - W(t));
    out.pos.set(c.x, c.y, z0);
    if (c.type === 'gap') {
      const u = Math.max(0, t - c.tV); out.pos.x += c.ax * u * u; out.pos.y += c.ay * u * u; out.pos.z += c.dz * u;
      euler(out.quat, 0, c.yaw + c.tum * u, c.roll + 0.3 * u * c.tum); op = 1 - seg(u, c.dz ? 0.7 : 1.1, c.dz ? 1.5 : 1.5);
    } else euler(out.quat, c.pitch, c.yaw + c.spin * (t - c.tp) * 0.5, c.roll);
    if (z0 < -105) return false;
  } else {   // catch
    if (t >= c.tAb) return false;
    const u = t - c.tB, zl = -8 + c.v * u; if (zl < -105) return false;
    const e = ease.inOutCubic(seg(t, c.tB, c.tB + 0.7)), p = seg(t, c.tB + 0.35, c.tAb);
    const phi = c.th - TAU * 1.15 * (0.55 * p + 0.45 * (1 - (1 - p) * (1 - p)));
    const ab = ease.inCubic(seg(t, c.tAb - 0.3, c.tAb)), Rr = lerp(c.Ro, RING_R, ab);
    v1.set(Math.cos(c.th) * c.rad, Math.sin(c.th) * c.rad, zl);
    v2.set(Math.cos(phi) * Rr, Math.sin(phi) * Rr, c.zoff * (1 - ab)); ring.localToWorld(v2);
    out.pos.copy(v1).lerp(v2, e);
    euler(qa, c.pitch, c.yaw, c.roll); qb.copy(ring.quaternion); out.quat.copy(qa).slerp(qb, e);
    sc = lerp(1, 0.62, e) * (1 - ab * 0.96); op = 1 - seg(ab, 0.75, 1); glow = 0.3 * e;
  }
  // gone when it is behind or inside the camera
  v1.copy(out.pos).sub(camPos); const d = v1.length();
  if (c.type !== 'catch') { op *= ease.outCubic(seg(d, 1.2, 4.5)); if (out.pos.z > camPos.z - 0.8) return false; }
  if (op <= 0.003) return false;
  out.scale = sc; out.op = op; out.glow = glow; return true;
}
