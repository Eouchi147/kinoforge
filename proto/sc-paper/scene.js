// THE DRAGON WHO COULDN'T FLY — a Paper Kingdom tale. 16:9, 124 s (2976 f @ 24 fps). Cut-paper shadow theatre (P09 toolkit).
// A king who hates to be bothered; a dragon crash-lands with a crumpled wing; three comic attempts to get rid of it;
// a small girl hears the cry under the roar, refolds the wing, and the dragon flies — lighting the castle's lanterns as thanks.
// Characters never speak (instruments speak for them); a warm narrator says four lines. Puppets on 2s, cameras on 1s.
import * as THREE from 'three';
import { boot, makeComposer, ease, clamp, lerp, smoothstep, noise1, rng } from '/harness/kit/film.js';
import { VIEW, Compositor, rgb, mk, ctx2d, cut, circle, poly, piece } from '/proto/p09-paper-kingdom/paper.js';
import { PAL, ST, INK, initStyles, buildPuppets, drawKing, drawSoldier, drawDragon, dragonMouth, dragonJoints, drawFire, drawHand, drawBird, drawWing, drawCrumple, BODY } from './puppets2.js';
import { DEPTH, HOT, buildStage, drawScreen, drawScreenCU, drawFar, drawNear, drawMid, drawGround, drawFrontLeft, drawFrontRight, drawGrass, WINDOWS } from './stage2.js';
import { buildChild, drawChild, walk, STAND, mixPose, STRIDE_WALK } from './child2.js';

const FPS = 24;
export const SH = { open: 0, crash: 216, army: 480, catapult: 1008, king: 1440, turn: 1824, fold: 2208, flight: 2496, end: 2784, total: 2976 };
export const CUE = { lampUp: 0, L1: 36, bird: 150, swat: 162, harrumph: 170, fall: 228, crash: 276, rise: 300, L2: 330, roar1: 444, point: 488, march: 520, halt: 604,
  inhale: 622, fire1: 660, candles: 700, retreat: 744, hop: 760, cartIn: 1010, load: 1080, signal: 1122, launch: 1140, achoo: 1210, toe: 1270, flee: 1340,
  helmet: 1446, kingGo: 1500, puff: 1650, frizz: 1700, kingBack: 1738, girlIn: 1830, flap: 1880, roar2: 1930, whimper: 1972, L3: 2000, reach: 2130,
  fold1: 2268, fold2: 2328, fold3: 2388, liftOff: 2540, lanterns: 2600, cheer: 2690, intoLight: 2700, L4: 2792, card: 2880 };
const SHOTS = Object.entries(SH).filter(([k]) => k !== 'total').map(([k, a], j, arr) => ({ name: k, dur: ((arr[j + 1] ? arr[j + 1][1] : SH.total) - a) / FPS }));
const on2 = (i) => i - (i & 1);
function keys(K, f) { if (f <= K[0][0]) return K[0][1]; for (let j = 1; j < K.length; j++) if (f <= K[j][0]) { const [fa, va] = K[j - 1], [fb, vb, e = ease.inOutSine] = K[j]; return lerp(va, vb, e((f - fa) / (fb - fa))); } return K[K.length - 1][1]; }
const win = (f, a, b) => f >= a && f < b;
const hop = (u) => 4 * u * (1 - u);

// ================================================================ camera (P09 multiplane: layers at depth d move with true parallax)
function cam(i) {
  let c;
  if (i < SH.crash) c = { k: lerp(1.0, 1.08, ease.inOutSine(i / SH.crash)), cx: lerp(0, -60, ease.inOutSine(i / SH.crash)), cy: 0, tx: 0, ty: lerp(0, 18, i / SH.crash) };
  else if (i < SH.army) c = { k: 0.9, cx: 120, cy: 0, tx: 0, ty: 20 };
  else if (i < SH.catapult) { const u = smoothstep(CUE.march, CUE.halt + 10, i) * (1 - smoothstep(CUE.retreat + 40, CUE.retreat + 130, i)); c = { k: lerp(0.9, 1.0, u), cx: lerp(120, 330, u), cy: 0, tx: 0, ty: lerp(20, 30, u) }; }
  else if (i < SH.king) c = { k: 0.86, cx: 160, cy: -20, tx: 0, ty: 40 };
  else if (i < SH.turn) { const u = smoothstep(CUE.kingGo + 10, CUE.puff - 20, i) * (1 - smoothstep(CUE.kingBack + 10, CUE.kingBack + 70, i)); c = { k: lerp(0.95, 1.12, u), cx: lerp(60, 520, u), cy: 0, tx: 0, ty: lerp(20, 50, u) }; }
  else if (i < SH.fold) {                                                  // wide while she walks in, then push in on the meeting (her raised hand, its lowered nose)
    const u = ease.inOutSine(clamp((i - SH.turn) / (CUE.reach - 30 - SH.turn))), v = smoothstep(CUE.reach + 4, CUE.reach + 58, i), gx = girlX() + 130;
    c = { k: lerp(lerp(0.95, 1.0, u), 1.85, v), cx: lerp(lerp(150, 300, u), gx - 640, v), cy: lerp(lerp(0, -20, u), 128, v), tx: 0, ty: lerp(20, 0, v) }; }
  else if (i < SH.flight) c = { k: 1, cx: 0, cy: 0, tx: 0, ty: 0 };   // CU (own transforms)
  else if (i < SH.end) { const u = ease.inOutSine(clamp((i - SH.flight) / (CUE.lanterns + 40 - SH.flight))); c = { k: lerp(1.05, 0.84, u), cx: lerp(500, -40, u), cy: lerp(-50, -40, u), tx: 0, ty: lerp(40, 70, u) }; }   // follow it to the castle
  else c = { k: 0.84, cx: -40, cy: -40, tx: 0, ty: 70 };
  // impacts shake the theatre (2 poses)
  for (const [f0, a] of [[CUE.crash, 7], [CUE.toe, 4], [CUE.crash + 2, -4]]) if (on2(i) === f0) { c.ty += a; c.tx += a * 0.4; }
  return c;
}
function setLayer(g, c, d) { const m = c.k, s = VIEW.dpr; g.setTransform(s * m, 0, 0, s * m, s * (640 * (1 - m) - c.k * c.cx / d + c.tx), s * (360 * (1 - m) - c.k * c.cy / d + c.ty)); }
function lampB(i) {
  let B = smoothstep(0, 40, i);                                                            // the lamp comes up
  B *= 1 - 0.18 * (smoothstep(CUE.fall - 6, CUE.fall + 10, i) - smoothstep(CUE.crash, CUE.crash + 30, i));   // a shadow passes over
  if (win(i, CUE.fire1, CUE.fire1 + 40)) B += 0.25 * (1 - (i - CUE.fire1) / 40);
  B *= lerp(1, 0.86, smoothstep(SH.turn, SH.turn + 60, i)) * lerp(1, 1 / 0.86 * 1.08, smoothstep(SH.flight, CUE.lanterns, i));   // evening, then the light returns
  return B;
}

// ================================================================ the KING (on his rock; later he goes up the hill himself)
const KX = 352, KY = 492;
function kingState(i) {
  const f = on2(i);
  let x = KX, y = KY, arm = 0.2 + 0.03 * Math.sin(f / 22), lean = 0.012 * Math.sin(f / 30), crown = { dx: 0, dy: 0, rot: 0 }, frizz = 0, helmet = 0, soot = 0, face = 1, helmetFly = null;
  arm += keys([[CUE.swat - 8, 0], [CUE.swat - 4, -0.3, ease.outQuad], [CUE.swat, 2.3, ease.outCubic], [CUE.swat + 10, 2.0], [CUE.swat + 20, 0, ease.inOutCubic]], f);
  if (f >= CUE.crash) {                                                             // the crown pops, flips, lands crooked
    const u = clamp((f - CUE.crash) / 20); crown = { dx: 6 * u, dy: -70 * hop(u), rot: 0.5 * u + 2 * Math.PI * smoothstep(0, 1, u) }; lean = -0.08 * (1 - smoothstep(CUE.crash, CUE.crash + 24, f));
    if (f >= CUE.toe + 60) crown = { dx: 0, dy: 0, rot: 0.06 };                     // he finally straightens it
  }
  if (win(f, CUE.point - 8, CUE.retreat)) arm = keys([[CUE.point - 8, 0.2], [CUE.point - 2, -0.16, ease.outQuad], [CUE.point + 8, 2.35, ease.inOutCubic], [CUE.point + 12, 2.2], [CUE.march + 60, 2.2], [CUE.march + 80, 0.3]], f);
  if (win(f, CUE.retreat + 100, SH.catapult)) { arm = keys([[CUE.retreat + 100, 0.3], [CUE.retreat + 112, 2.9, ease.outCubic], [CUE.retreat + 150, 2.9], [CUE.retreat + 160, 0.2]], f); lean = 0.1 * smoothstep(CUE.retreat + 100, CUE.retreat + 112, f) * (1 - smoothstep(CUE.retreat + 150, CUE.retreat + 160, f)); }  // hand to the forehead
  if (win(f, CUE.signal - 10, CUE.toe)) arm = keys([[CUE.signal - 10, 0.2], [CUE.signal, 2.6, ease.outCubic], [CUE.signal + 8, 0.9, ease.inQuad], [CUE.signal + 30, 0.4]], f);
  if (win(f, CUE.toe, CUE.flee + 40)) { const u = (f - CUE.toe) / 14, k = Math.floor(u); if (k < 5) { y -= 34 * hop(u - k) * (1 - k * 0.12); lean = (k % 2 ? 0.14 : -0.14); arm = 1.6 + 0.6 * Math.sin(u * Math.PI); } }
  if (f >= CUE.helmet && f < SH.turn) helmet = smoothstep(CUE.helmet, CUE.helmet + 12, f) + 0.04 * Math.sin((f - CUE.helmet) / 2) * (1 - smoothstep(CUE.helmet + 12, CUE.helmet + 40, f));
  if (f >= CUE.kingGo && f < SH.turn) {                                            // down the rock, up the hill, (puff), back
    const XG = 880, YG = 578;
    if (f < CUE.kingGo + 20) { const u = (f - CUE.kingGo) / 20; x = lerp(KX, KX + 90, u); y = lerp(KY, YG, u) - 50 * hop(u); }
    else if (f < CUE.puff - 20) { const u = clamp((f - CUE.kingGo - 20) / (CUE.puff - 40 - CUE.kingGo)); x = lerp(KX + 90, XG, u); y = YG - 5 * Math.abs(Math.sin(u * 22)); arm = 2.4 + 0.15 * Math.sin(u * 22); lean = 0.04; }
    else if (f < CUE.kingBack) { x = XG; y = YG; arm = f < CUE.puff ? 2.4 : 0.1; lean = f < CUE.puff ? 0.05 : -0.05; }
    else { const u = clamp((f - CUE.kingBack) / (SH.turn - CUE.kingBack - 10)); x = lerp(XG, KX - 40, u); y = YG; face = -1; arm = 0.1; lean = 0; }
    if (f >= CUE.frizz - 30) { frizz = smoothstep(CUE.frizz - 30, CUE.frizz - 26, f); soot = 1; }
    if (f >= CUE.frizz - 26) { const u = clamp((f - CUE.frizz + 26) / 22); helmetFly = { dx: -80 * u, dy: lerp(0, 114, u) - 150 * hop(u), rot: -2.8 * u }; }   // the puff blows the helmet off: frizzled hair underneath
  }
  if (f >= SH.turn && f < SH.flight) { frizz = 1; crown = { dx: 0, dy: 0, rot: 0.06 }; }   // he's back on the rock, still frizzled
  if (f >= SH.flight) { frizz = 0.6; arm = keys([[CUE.cheer - 30, 0.2], [CUE.cheer - 20, 2.4, ease.outCubic]], f) + (f > CUE.cheer - 20 ? 0.35 * Math.sin((f - CUE.cheer) / 3) : 0); }
  return { x, y, s: 1, arm, lean, crown, frizz, helmet, soot, face, helmetFly };
}

// ================================================================ the ARMY: march up, halt, get scorched, retreat at double time
const MARCH = 4;   // steps forward: they halt just in front of the dragon's paws, never inside it
const X0 = [446, 511, 580, 645, 714, 780, 850], PH = [0, 2, 4, 0, 2, 4, 0], STRIDE = 40, GY = 578, BEAT = 60 / 108;
function soldiers(i) {
  const f = on2(i), out = [];
  for (let j = 0; j < 7; j++) {
    let x = X0[j], pose = 'H', bob = 0, spear = 0, lean = 0, face = 1, candle = 0, smoke = 0, vis = true, y = GY;
    if (f < SH.catapult) {
      const b = (f - PH[j] - CUE.march) / (BEAT * FPS);
      if (b >= 0 && b < MARCH) { const k = Math.floor(b), p = b - k; pose = p < 0.5 ? 'A' : 'B'; bob = p < 0.5 ? 1.2 : -2.2; x += STRIDE * (k + ease.inOutSine(p)); spear = 0.05 * Math.sin(p * Math.PI * 2); }
      else if (b >= MARCH) x += STRIDE * MARCH;
      if (f >= CUE.halt) spear = keys([[CUE.halt + j, 0], [CUE.halt + 10 + j, 0.95, ease.outBack]], f);
      if (f >= CUE.inhale) spear += 0.05 * noise1(f * 1.7, j * 3.1);                       // they tremble as the dragon breathes in
      if (f >= CUE.candles) { candle = 1; spear = 0.95 * (1 - smoothstep(CUE.candles + 4, CUE.candles + 14, f)); }   // spears snap upright, tips burning like birthday candles
      if (f >= CUE.retreat) {                                                                // about-face, double-time home
        face = -1; const b2 = (f - PH[j] - CUE.retreat - j * 2) / (BEAT * FPS * 0.5);
        if (b2 >= 0) { const k = Math.floor(b2), p = b2 - k; pose = p < 0.5 ? 'A' : 'B'; bob = p < 0.5 ? 1.2 : -2.2; x = X0[j] + STRIDE * MARCH - STRIDE * 1.1 * (k + ease.inOutSine(p)); }
        if (j === 6) { smoke = 1; if (b2 >= 0) { y -= 22 * hop((b2 * 0.5) % 1); } }       // the last one hops: his bottom is smoking
        if (x < -120) vis = false;
      }
    } else if (f < SH.king) {                                                                // catapult crew: two soldiers push, load, crank; then flee
      if (j > 1) vis = false;
      else {
        const cx = catapultX(f) - 70 - j * 34; x = cx; pose = (Math.floor(f / 6) % 2) ? 'A' : 'B'; bob = 0; spear = 0.9; lean = 0.18;
        if (f >= CUE.load) { pose = 'H'; lean = 0.05; }
        if (f >= CUE.flee) { face = -1; const u = (f - CUE.flee) / 60; x = cx - 600 * u; pose = (Math.floor(f / 4) % 2) ? 'A' : 'B'; if (x < -100) vis = false; }
      }
    } else if (f < SH.flight) vis = false;
    else { x = 150 + j * 52; spear = 0.0; if (f >= CUE.cheer) { spear = -0.3 + 0.3 * Math.sin((f - CUE.cheer) / 3 + j); y -= 10 * Math.max(0, Math.sin((f - CUE.cheer) / 3 + j)); } }
    if (vis) out.push({ x, y, s: 1, pose, bob, spear, lean, face, candle, smoke });
  }
  return out;
}
function drawSoldierF(g, s) { g.save(); if (s.face < 0) { g.translate(s.x, 0); g.scale(-1, 1); g.translate(-s.x, 0); } drawSoldier(g, s); g.restore(); }

// ================================================================ the CATAPULT and the BOULDER
const CAT = {};
function buildCatapult() {
  CAT.base = cut('M -62 0 L 62 0 L 54 -16 L -54 -16 Z', { seed: 950, amp: 0.6 });
  CAT.wheel = cut(circle(0, 0, 13, 22) + circle(0, 0, 3.5, 10), { seed: 951, rule: 'evenodd', amp: 0.4 });
  CAT.post = cut('M -7 -14 L 7 -14 L 5 -58 L -5 -58 Z', { seed: 952, amp: 0.4 });
  CAT.arm = cut('M -4 6 L 4 6 L 3 -88 L -3 -88 Z M -16 -86 Q 0 -72 16 -86 L 13 -96 Q 0 -86 -13 -96 Z', { seed: 953, amp: 0.4 });
  CAT.rock = cut(poly(Array.from({ length: 14 }, (_, k) => { const a = k / 14 * Math.PI * 2, r = 12 + 2.5 * Math.sin(k * 2.7); return [Math.cos(a) * r, Math.sin(a) * r]; })), { seed: 954, amp: 0.8 });
}
const catapultX = (f) => keys([[CUE.cartIn, -120], [CUE.load - 6, 600, ease.outCubic]], f);
const catArm = (f) => f < CUE.load ? -0.25 : f < CUE.launch ? keys([[CUE.load + 10, -0.25], [CUE.signal - 4, -1.25, ease.inOutCubic]], f) : keys([[CUE.launch, -1.25], [CUE.launch + 3, 0.55, ease.outQuad], [CUE.launch + 10, 0.35], [CUE.launch + 16, 0.42]], f);
function drawCatapult(g, f) {
  const x = catapultX(f), st = INK(1.1), roll = (x + 120) / 13;
  g.save(); g.translate(x, GY);
  for (const wx of [-38, 38]) { g.save(); g.translate(wx, -12); g.rotate(roll); piece(g, CAT.wheel, st); g.restore(); }
  piece(g, CAT.base, st); piece(g, CAT.post, st);
  g.save(); g.translate(0, -52); g.rotate(catArm(f)); piece(g, CAT.arm, st);
  if (f >= CUE.load - 10 && f < CUE.launch + 2) { g.translate(0, -94); piece(g, CAT.rock, st); }
  g.restore(); g.restore();
}
function aimTarget(what, f) {
  if (what === 'king') { const k = kingState(CUE.puff); return [k.x + 6, k.y - 150]; }
  const tips = soldiers(CUE.fire1).map((s) => [s.x + s.face * (-1 + 115 * Math.sin(s.spear)), s.y + s.bob - 50 - 115 * Math.cos(s.spear)]).sort((a, b) => b[0] - a[0]);
  const u = smoothstep(CUE.fire1 + 2, CUE.fire1 + 32, f), a = tips[0], b = tips[tips.length - 1];   // the jet sweeps along the row of spear tips, nearest first
  return [lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 10];
}
let LIT = null, SCAN = false;
const scrX = (X, d, c) => c.k * X + 640 * (1 - c.k) - c.k * c.cx / d + c.tx;
function litFrames() {                                                       // first frame the flying dragon's mouth is close enough for its breath to reach each window
  if (LIT) return LIT; SCAN = true; LIT = WINDOWS.map(() => Infinity);
  for (let f = CUE.liftOff; f < CUE.intoLight; f += 2) {
    const d = dragon(f), m = dragonMouth(d.pose), r = d.rot, X = BX + d.ox + DS * d.sc * (m[0] * Math.cos(r) - m[1] * Math.sin(r)), c = cam(f), mx = scrX(X, DEPTH.dragon, c);
    WINDOWS.forEach(([wx], k) => { if (LIT[k] === Infinity && mx < scrX(wx, DEPTH.mid, c) + 150) LIT[k] = f + 4; });
  }
  SCAN = false; return LIT;
}
globalThis.KF_LIT = () => litFrames();                            // the soundtrack reads these (one breath + one bell per window)
const NOSE = new Map();
function noseAt(f, dx = 0) { if (!NOSE.has(f)) { const d = dragon(f), m = dragonMouth(d.pose); NOSE.set(f, [BX + d.ox + DS * d.sc * m[0], BY + d.oy + DS * d.sc * m[1] - 6]); } const n = NOSE.get(f); return [n[0] + dx, n[1]]; }
function girlX() { return noseAt(CUE.reach + 40)[0] - 30; }        // she stops right under the nose it will lower to her
function boulderAt(f) {                                                  // out along a parabola to the dragon's face, sneezed straight back onto the king's toe
  const P0 = [catapultX(CUE.launch) + 40, GY - 140], P1 = noseAt(CUE.achoo - 18, -14), P2 = [KX + 26, KY - 14];
  if (f >= CUE.launch + 2 && f < CUE.achoo - 18) { const u = clamp((f - CUE.launch - 2) / (CUE.achoo - 20 - CUE.launch)); return [lerp(P0[0], P1[0], u), lerp(P0[1], P1[1], u) - 260 * hop(u), u * 9]; }
  if (f >= CUE.achoo - 18 && f < CUE.achoo) return [P1[0] + 4 * Math.sin(f), P1[1], 0];            // it hangs in front of the nose (comic hold)
  if (f >= CUE.achoo && f <= CUE.toe) { const u = clamp((f - CUE.achoo) / (CUE.toe - CUE.achoo)); return [lerp(P1[0], P2[0], u), lerp(P1[1], P2[1], u) - 330 * hop(u), -u * 12]; }
  if (f > CUE.toe && f < CUE.flee + 60) return [P2[0] + 18, P2[1] + 2, 0];
  return null;
}

// ================================================================ the DRAGON
export const DS = 1.2, BX = 1130, BY = GY - BODY.ground * DS;        // seated on the ground, feet on the same floor as everyone else
const RISEN = [-1.54, -1.68, -1.95, -2.41, -2.93, 2.79];
const FLOP = [2.3, 2.6, 2.9, 3.05, 3.14, 2.9];                        // dazed after the crash / bowing to the girl: neck down along the ground
const DAZE = [-1.6, -2.0, -2.6, -3.28, -3.88, 2.0];                    // dazed / peering down: neck arched forward, head hanging low (stays clear of the soldiers)
const FLY = [-2.72, -2.86, -2.97, -3.05, -3.1, 3.12];                 // in flight: neck stretched forward
const WS = [-1.25, -0.2], WFD = [1.35, 2.7], CRUMPLED = [-0.3, 2.45], FAR_REST = [0.35, 2.2];
function dragon(i) {
  const f = on2(i);
  let ox = 0, oy = 0, rot = 0, sc = 1, sx = 1, vis = true, rise = 1, lean = 0, head = 0, jaw = 0.1, wF = FAR_REST.slice(), wN = CRUMPLED.slice(), squashN = 0.55, crumple = 1, fire = 0, fireUp = 0, fly = 0, brot = 0, aim = null, daze = 0;
  let wag = 0.25 * Math.sin(f / 14);
  const br = 0.02 * Math.sin(f / 20);
  if (f < CUE.fall) vis = false;
  else if (f < CUE.crash) {                                                        // tumbling out of the sky
    const u = (f - CUE.fall) / (CUE.crash - CUE.fall); ox = lerp(420, 0, u); oy = lerp(-900, 0, u * u); rot = lerp(-1.6, 0, u) + 0.4 * Math.sin(u * 9) * (1 - u); sc = lerp(0.6, 1, u); daze = 1; wag = 1.2 * Math.sin(f / 3);
    wN = [lerp(-0.8, 0.75, u), lerp(1.8, 2.35, u)]; wF = [lerp(-1.6, -1.25, u), -0.4];
  } else {
    daze = 1 - keys([[CUE.crash, 0.0], [CUE.rise, 0.0], [CUE.rise + 40, 1.0, ease.inOutCubic]], f); head += 0.18 * daze * Math.sin(f / 5);   // woozy
    if (f < CUE.crash + 4) oy = 6 * (1 - (f - CUE.crash) / 4);       // the thump
  }
  // performance beats
  lean += 0.03 * Math.sin(f / 26);
  const roar = (a, up) => { const u = f - a; if (u < -16 || u > 44) return; const ant = smoothstep(-16, 0, u) * (1 - smoothstep(0, 4, u)); lean += 0.18 * ant - 0.12 * (smoothstep(0, 6, u) * (1 - smoothstep(30, 44, u))); head += up ? -0.45 * smoothstep(0, 8, u) * (1 - smoothstep(32, 44, u)) : 0; jaw = Math.max(jaw, 0.62 * smoothstep(0, 4, u) * (1 - smoothstep(30, 40, u))); };
  roar(CUE.roar1, true); roar(CUE.roar2, true);
  if (win(f, CUE.roar1, CUE.roar1 + 34)) { fire = keys([[CUE.roar1, 0], [CUE.roar1 + 6, 0.7, ease.outCubic], [CUE.roar1 + 22, 0.7], [CUE.roar1 + 34, 0]], f); fireUp = 1; }
  if (win(f, CUE.inhale, CUE.fire1)) { lean += 0.22 * smoothstep(CUE.inhale, CUE.fire1 - 4, f); jaw = 0.04; }                   // a long breath in (anticipation)
  if (win(f, CUE.fire1, CUE.fire1 + 44)) { const u = f - CUE.fire1; lean -= 0.12 * smoothstep(0, 4, u); jaw = 0.6; fire = keys([[0, 0], [4, 1, ease.outCubic], [30, 1], [44, 0, ease.inQuad]], u); aim = 'spears'; }
  if (win(f, CUE.launch + 20, CUE.achoo + 30)) {                                // the boulder arrives: "ah... ah... CHOO!"
    const u = f - (CUE.achoo - 30); head += -0.25 * smoothstep(0, 26, u) * (1 - smoothstep(30, 34, u)) + 0.35 * smoothstep(30, 32, u) * (1 - smoothstep(40, 56, u)); jaw = u < 30 ? 0.2 + 0.2 * smoothstep(0, 26, u) : u < 40 ? 0.5 : 0.1;
    lean += -0.06 * smoothstep(0, 26, u) + 0.16 * smoothstep(30, 32, u) * (1 - smoothstep(40, 56, u));
  }
  if (win(f, CUE.puff - 34, CUE.puff + 50)) { const u = smoothstep(CUE.puff - 34, CUE.puff - 8, f) * (1 - smoothstep(CUE.puff + 22, CUE.puff + 50, f)); daze = Math.max(daze, 0.95 * u); if (win(f, CUE.puff, CUE.puff + 12)) { fire = 0.32; jaw = 0.3; aim = 'king'; } }   // lowers its head to look at the tiny king: one small puff, right at him
  if (win(f, CUE.flap, CUE.flap + 44)) { const u = (f - CUE.flap) / 44, k = Math.floor(u * 2), p = (u * 2) % 1; wN = [lerp(CRUMPLED[0], -0.6, hop(p)), lerp(CRUMPLED[1], 1.4, hop(p))]; squashN = 0.55 + 0.1 * hop(p); }   // tries to flap: it flops
  if (f >= CUE.whimper && f < SH.fold) { const u = smoothstep(CUE.whimper, CUE.whimper + 16, f); head += 0.42 * u; lean += 0.1 * u; jaw = 0.08 + 0.06 * (f < CUE.whimper + 30 ? Math.abs(Math.sin(f / 2)) : 0); }
  if (f >= CUE.reach && f < SH.fold) { const u = smoothstep(CUE.reach, CUE.reach + 40, f); rise = 1 - 0.93 * u; head -= 0.05 * u; wN = [lerp(CRUMPLED[0], 1.4, u), CRUMPLED[1]]; }   // lowers its head and its wing to her
  if (f >= SH.flight) {                                                           // the wing is whole: spread, flap, take off, circle the castle, fly into the light
    crumple = 0; squashN = 1; wN = WS.slice(); wag = 0.4 * Math.sin(f / 8);
    const sp = smoothstep(SH.flight + 10, SH.flight + 34, f); wN = [lerp(WFD[0], WS[0], sp), lerp(WFD[1], WS[1], sp)]; wF = [lerp(WFD[0], WS[0], sp), lerp(WFD[1], WS[1], sp)];
    if (f >= CUE.liftOff - 20) { const ph = ((f - CUE.liftOff + 20) / 14) % 1, up = ph < 0.5; const a = up ? -1.7 : -0.25, b = up ? -0.5 : 0.5; wN = [a, b]; wF = [a + 0.1, b]; }
    fly = smoothstep(CUE.liftOff - 6, CUE.liftOff + 26, f); brot = -0.8 * fly;
    const fl = clamp((f - CUE.liftOff) / (CUE.intoLight - CUE.liftOff));
    const path = (u) => [-700 * ease.outSine(u), -110 * ease.outSine(u) - 30 * Math.sin(u * Math.PI) - 150 * smoothstep(0.72, 1, u)];   // climbs clear of the king before it turns   // low over the field, then along the castle so its breath can light each window
    [ox, oy] = path(fl); oy -= 60 * fly * (1 - smoothstep(0, 0.3, fl)) * 0;                      // a crouch-and-spring is in the fly blend
    rot = 0.22 * fly - 0.12 * Math.sin(fl * Math.PI * 2);
    sc = lerp(1, 0.62, fl);
    if (f >= CUE.intoLight) {                                                     // the puppeteer flips the puppet to face the light, then it flies away into it
      const u = smoothstep(CUE.intoLight + 4, SH.end, f), p0 = path(1); sx = Math.cos(Math.PI * clamp((f - CUE.intoLight) / 10));
      ox = lerp(p0[0], (HOT[0] - BX) * 0.9, u); oy = lerp(p0[1], (HOT[1] - BY) * 0.9, u); sc = lerp(0.62, 0.06, u); rot = 0.18;
    }
    if (!SCAN) for (const lf of litFrames()) if (f >= lf - 6 && f < lf + 4) { fire = Math.max(fire, 0.55 * Math.sin(Math.PI * (f - lf + 6) / 10)); jaw = 0.35; fireUp = -0.65; }   // one short breath for each window it lights
    head += -0.1 * (1 - fly); lean += 0.05 * (1 - fly);
  }
  const TAU = Math.PI * 2, base = RISEN.map((r, k) => lerp(lerp(lerp(r, DAZE[k], daze), k < 5 ? FLOP[k] - TAU : FLOP[k], 1 - rise), FLY[k], fly));
  const ang = base.map((r, k) => r + (k >= 2 ? lean * (k - 1) * 0.5 : 0) + (k === 5 ? head : 0) + (k >= 1 ? br * k * 0.4 : 0));
  return { vis, ox, oy, rot, sc, sx, pose: { ang, dy: 0, jaw, wN, wF }, body: { rot: brot, fly, wag }, squashN, crumple, fire, fireUp, aim };
}
function dragonXf(g, d) { g.translate(BX + d.ox, BY + d.oy); g.rotate(d.rot); g.scale(DS * d.sc * (Math.abs(d.sx) < 0.08 ? 0.08 * Math.sign(d.sx || 1) : d.sx), DS * d.sc); }

// ================================================================ the GIRL
function girl(i) {
  const f = on2(i); if (f < CUE.girlIn || f >= SH.fold) return null;
  const x0 = 140, x1 = girlX(), V = STRIDE_WALK * 1.4 * 1.1;
  let x = Math.min(x1, x0 + V * (f - CUE.girlIn) / FPS); if (f > CUE.roar2 && f < CUE.whimper + 20) x = Math.min(x, x0 + V * (CUE.roar2 - CUE.girlIn) / FPS);   // the roar stops her
  const walking = x < x1 && !(f > CUE.roar2 && f < CUE.whimper + 20);
  let P = walking ? walk((x - x0) / STRIDE_WALK * 1.0) : { ...STAND };
  if (f > CUE.roar2 && f < CUE.whimper) P = { ...STAND, lean: -0.14, aR: 0.8, eR: 1.4, aL: 0.6, eL: 1.3 };
  if (f >= CUE.reach - 20) { const u = smoothstep(CUE.reach - 20, CUE.reach + 10, f); P = mixPose(P, { ...STAND, aR: 2.3, eR: 0.15, lean: 0.06 }, u); }
  return { ...P, x, y: GY, s: 1.8, face: 1, look: 1, head: f >= CUE.reach - 20 ? 0.35 : 0.05, wind: (Math.floor(f / 4) % 3) * 0.66 };
}

// ================================================================ smoke puffs, candle flames, lantern glows
function puffs(g, list, f) { for (const [x, y, r, a] of list) { g.fillStyle = `rgba(70,46,34,${a})`; g.beginPath(); for (let k = 0; k < 3; k++) { const rr = r * (0.7 + 0.3 * Math.sin(k * 2.1 + f * 0.3)); g.moveTo(x + k * r * 0.5 + rr, y - k * r * 0.3); g.arc(x + k * r * 0.5, y - k * r * 0.3, rr, 0, Math.PI * 2); } g.fill(); } }
function candle(g, x, y, f, s = 1) { g.save(); g.translate(x, y); g.rotate(-Math.PI / 2 + 0.15 * Math.sin(f * 0.9)); g.scale(0.09 * s, 0.09 * s); drawFire(g, 0.5, Math.floor(f / 2)); g.restore(); }

// ================================================================ boot
let post, W, H, comp, G, M, CARD, CARD0;
await boot({
  fps: FPS, shots: SHOTS, fonts: [['IM Fell English', 400]],
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; VIEW.dpr = W / 1280;
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x000000);
    const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 10);
    post = makeComposer(ctx.renderer, scene, camera, { grade: 'sepia', finish: { saturation: 0.62, grain: 0.04, vignette: 0.33, contrast: 1.06, halation: 0.22, halationThreshold: 0.8,
      shadowTint: [0.035, 0.006, -0.03], highlightTint: [0.09, 0.04, -0.04] } });
    M = mk(W, H); G = ctx2d(M); comp = new Compositor(W, H);
    initStyles(comp.lg); buildPuppets(); buildStage(); buildChild(); buildCatapult();
    CARD = buildCard(true); CARD0 = buildCard(false);
  },
  render: async (ctx, i, t) => {
    const g = G; g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; g.filter = 'none';
    g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    if (i >= SH.fold && i < SH.flight) drawCU(g, i); else drawStage(g, i);
    if (i >= CUE.card) drawFold(g, i);
    const ov = post.overlay.ctx; ov.setTransform(1, 0, 0, 1, 0, 0); ov.globalCompositeOperation = 'copy'; ov.drawImage(M, 0, 0); ov.globalCompositeOperation = 'source-over';
    post.render(t);
  },
});

function drawStage(g, i) {
  const c = cam(i), f = on2(i), B = lampB(i);
  setLayer(g, c, DEPTH.screen); drawScreen(g, B);
  comp.layer(g, (lg) => { setLayer(lg, c, DEPTH.far); drawFar(lg); }, { mode: 'multiply', off: [-2.5, 2], blur: 3, shadow: 'rgba(70,24,6,0.25)' });
  comp.layer(g, (lg) => { setLayer(lg, c, DEPTH.near); drawNear(lg); }, { mode: 'multiply', off: [-3, 2.5], blur: 3.5, shadow: 'rgba(56,18,4,0.3)' });
  comp.layer(g, (lg) => { setLayer(lg, c, DEPTH.mid); drawMid(lg, f); }, { mode: 'multiply', off: [-3.5, 3], blur: 4, shadow: 'rgba(44,13,3,0.36)' });
  // lanterns: one by one as the dragon passes, each a warm glow in a castle window
  const LF = litFrames(), lit = LF.some((lf) => f >= lf) ? WINDOWS.length : 0;
  if (lit) { setLayer(g, c, DEPTH.mid); g.globalCompositeOperation = 'lighter'; for (let k = 0; k < lit; k++) { const [x, y] = WINDOWS[k], a = 0.55 * smoothstep(LF[k], LF[k] + 6, f) * (0.92 + 0.08 * Math.sin(f * 0.7 + k)); const gr = g.createRadialGradient(x, y, 0, x, y, 30); gr.addColorStop(0, `rgba(255,200,90,${a})`); gr.addColorStop(1, 'rgba(255,150,40,0)'); g.fillStyle = gr; g.fillRect(x - 30, y - 30, 60, 60); g.fillStyle = `rgba(255,236,170,${a})`; g.beginPath(); g.arc(x, y, 3.5, 0, Math.PI * 2); g.fill(); } g.globalCompositeOperation = 'source-over'; }
  // the dragon (behind the hillock while it sits on the hill; in front of everything once it flies)
  const d = dragon(i), flying = f >= CUE.liftOff;
  const drawD = () => {
    if (!d.vis) return;
    comp.layer(g, (lg) => { setLayer(lg, c, DEPTH.dragon); dragonXf(lg, d); drawDragon(lg, d.pose, { wingSquashN: d.squashN, crumple: d.crumple, body: d.body }); }, { off: [-5, 4], blur: 5, shadow: 'rgba(30,9,2,0.5)' });
    if (d.fire > 0) {
      const m = dragonMouth(d.pose); setLayer(g, c, DEPTH.dragon);
      if (d.aim) {                                                                // aimed breath: the flame goes from the mouth to what it must hit, and is just long enough to reach it
        const T = aimTarget(d.aim, f), mx = BX + d.ox + DS * d.sc * m[0], my = BY + d.oy + DS * d.sc * m[1], dx = T[0] - mx, dy = T[1] - my, L = Math.hypot(dx, dy);
        g.translate(mx, my); g.rotate(Math.atan2(dy, dx)); g.globalCompositeOperation = 'lighter'; const gl = g.createRadialGradient(L * 0.5, 0, 0, L * 0.5, 0, L * 0.8); gl.addColorStop(0, `rgba(255,150,50,${0.3 * d.fire})`); gl.addColorStop(1, 'rgba(255,120,30,0)'); g.fillStyle = gl; g.fillRect(-L * 0.4, -L, L * 1.8, L * 2); g.globalCompositeOperation = 'source-over';
        const reach = 230 * d.fire + 55; g.scale(L / reach, Math.min(1.3, Math.max(0.6, L / 330))); drawFire(g, d.fire, Math.floor(f / 2));   // jet length = distance to the target
      } else {
      dragonXf(g, d); g.translate(m[0], m[1]); g.rotate(d.pose.ang[5] - 0.12 + (d.fireUp > 0 ? 1.15 : d.fireUp < 0 ? d.fireUp : 0));   // fireUp < 0: breath angled down at the windows
      g.globalCompositeOperation = 'lighter'; const gl = g.createRadialGradient(150, 0, 0, 150, 0, 300); gl.addColorStop(0, `rgba(255,150,50,${0.3 * d.fire})`); gl.addColorStop(1, 'rgba(255,120,30,0)'); g.fillStyle = gl; g.fillRect(-200, -320, 700, 640); g.globalCompositeOperation = 'source-over';
      g.scale(0.85, 0.85); drawFire(g, d.fire, Math.floor(f / 2));
      }
    }
  };
  if (!flying) drawD();
  // dust from the crash
  if (win(f, CUE.crash, CUE.crash + 60)) { setLayer(g, c, DEPTH.dragon); const u = (f - CUE.crash) / 60; puffs(g, [[1060, 560 - 60 * u, 40 + 60 * u, 0.35 * (1 - u)], [1200, 550 - 80 * u, 50 + 70 * u, 0.3 * (1 - u)], [1330, 565 - 50 * u, 36 + 50 * u, 0.3 * (1 - u)]], f); }
  comp.layer(g, (lg) => { setLayer(lg, c, DEPTH.army); drawGround(lg); }, { mode: 'multiply', off: [-4, 3], blur: 4, shadow: 'rgba(36,11,2,0.4)' });
  // the paper bird the king swats (opening gag)
  if (win(f, CUE.bird - 40, CUE.swat + 40)) { const u = (f - CUE.bird + 40) / 80, swat = f >= CUE.swat ? (f - CUE.swat) / 40 : 0; comp.layer(g, (lg) => { setLayer(lg, c, DEPTH.bird); drawBird(lg, { x: lerp(900, 380, Math.min(u, 0.55) / 0.55) - 200 * swat, y: 300 + 40 * Math.sin(u * 6) - 260 * swat * swat, s: 0.3, rot: swat * 3, wing: ['up', 'mid', 'down', 'mid'][Math.floor(f / 2) % 4] }); }, { off: [-4, 3.5], blur: 4, shadow: 'rgba(40,12,2,0.35)' }); }
  // army, catapult, girl, the wandering king — all on the army plane
  const army = soldiers(i), gl = girl(i), ks = kingState(i), kingDown = f >= CUE.kingGo + 10 && f < SH.turn;
  comp.layer(g, (lg) => {
    setLayer(lg, c, DEPTH.army);
    if (f >= CUE.cartIn && f < SH.king) drawCatapult(lg, f);
    for (const s of army) drawSoldierF(lg, s);
    if (gl) drawChild(lg, gl, INK(0.9), { sticks: false });
    if (kingDown) drawKing(lg, ks);
  }, { off: [-4.5, 3.5], blur: 4, shadow: 'rgba(30,9,2,0.5)' });
  // candles on the spear tips, smoke from the singed
  setLayer(g, c, DEPTH.army);
  for (const s of army) {
    if (s.candle) { const tip = [s.x + s.face * (-1 + 115 * Math.sin(s.spear) * 1), s.y + s.bob - 50 - 115 * Math.cos(s.spear)]; g.globalCompositeOperation = 'lighter'; candle(g, tip[0], tip[1], f + s.x); g.globalCompositeOperation = 'source-over'; puffs(g, [[tip[0] + 3, tip[1] - 22 - (f % 12), 5, 0.25]], f); }
    if (s.smoke) puffs(g, [[s.x - 14 * s.face, s.y - 36 - ((f * 2) % 30), 7, 0.3], [s.x - 18 * s.face, s.y - 56 - ((f * 2 + 15) % 30), 9, 0.22]], f);
  }
  if (kingDown && f >= CUE.frizz - 30) { const k = ks; puffs(g, [[k.x + 10, k.y - 200 - ((f * 1.5) % 40), 10, 0.3 * (f < CUE.frizz ? 1 : 0.6)], [k.x - 4, k.y - 220 - ((f * 1.5 + 20) % 40), 12, 0.25]], f); if (f < CUE.frizz) puffs(g, [[k.x + 20, k.y - 150, 40, 0.5 * (1 - (f - CUE.frizz + 30) / 30)]], f); }
  const bo = boulderAt(f);
  const drawBo = () => comp.layer(g, (lg) => { setLayer(lg, c, f < CUE.achoo ? DEPTH.army : DEPTH.front); lg.translate(bo[0], bo[1]); lg.rotate(bo[2]); lg.scale(1.7, 1.7); piece(lg, CAT.rock, INK(1.1)); }, { off: [-4, 3], blur: 4, shadow: 'rgba(30,9,2,0.45)' });
  if (bo && f < CUE.achoo) drawBo();
  // front: the king's rock, the right hillock (hides the dragon's base), the king when he's on his rock
  comp.layer(g, (lg) => { setLayer(lg, c, DEPTH.front); drawFrontLeft(lg); drawFrontRight(lg); if (!kingDown) drawKing(lg, ks); }, { off: [-5, 4], blur: 5, shadow: 'rgba(30,9,2,0.5)' });
  if (bo && f >= CUE.achoo) drawBo();
  if (win(f, CUE.toe, CUE.toe + 18)) { setLayer(g, c, DEPTH.front); const u = (f - CUE.toe) / 18; puffs(g, [[KX + 10, KY - 10 - 20 * u, 10 + 22 * u, 0.4 * (1 - u)], [KX + 50, KY - 6 - 14 * u, 8 + 18 * u, 0.35 * (1 - u)]], f); }   // thud on the toe
  if (flying) drawD();
  comp.layer(g, (lg) => { setLayer(lg, c, DEPTH.grass); drawGrass(lg); }, { off: [-6, 5], blur: 6, shadow: 'rgba(30,9,2,0.45)' });
}

// ================================================================ CU: her hands refold the crumpled wing (three folds, each held)
function drawCU(g, i) {
  const f = on2(i) - SH.fold, s = VIEW.dpr;
  g.setTransform(s, 0, 0, s, 0, 0); drawScreenCU(g, 0.95);
  comp.layer(g, (lg) => { lg.setTransform(s * 1.7, 0, 0, s * 1.7, s * -560, s * -186); drawFar(lg); }, { mode: 'multiply', shadow: null, defocus: 7 });
  const F1 = CUE.fold1 - SH.fold, F2 = CUE.fold2 - SH.fold, F3 = CUE.fold3 - SH.fold;
  const stage = f < F1 ? 0 : f < F2 ? 1 : f < F3 ? 2 : 3;
  const press = [F1, F2, F3].some((a) => f >= a - 4 && f < a - 2);
  const sq = [0.45, 0.62, 0.8, 1.0][stage], w0 = [[0.55, 2.2], [0.25, 1.4], [-0.05, 0.7], [-0.35, 0.0]][stage], crump = [1, 0.66, 0.33, 0][stage];
  const lift = smoothstep(260, 288, f);
  comp.layer(g, (lg) => {
    lg.setTransform(s * 1.55, 0, 0, s * 1.55, s * 330, s * (430 - 160 * lift));
    lg.rotate(-0.25 + (press ? 0.03 : 0) - 0.3 * lift);
    drawWing(lg, [0, 0], w0, 1, 1, false, true, sq * (press ? 0.95 : 1));
    drawCrumple(lg, [0, 0], w0, sq, crump, true);
    if (stage === 3 && f < F3 + 14) { lg.globalCompositeOperation = 'lighter'; lg.fillStyle = `rgba(255,220,150,${0.25 * (1 - (f - F3) / 14)})`; lg.fillRect(-60, -200, 420, 400); lg.globalCompositeOperation = 'source-over'; }
  }, { off: [-6, 5], blur: 7, shadow: 'rgba(30,9,2,0.45)' });
  const enter = keys([[0, 0], [14, 1, ease.outCubic]], f), open = smoothstep(236, 256, f), ant = press ? 1 : 0;
  // her right hand holds the wing's outer tip (wherever the current fold puts it): fingertips sit on the paper, never in the air
  const R = (a, p) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a)];
  const tl = R(w0[0], [150 + R(w0[1], [120, -12])[0], R(w0[1], [120, -12])[1]]), tw = R(-0.25, [tl[0], tl[1] * sq]), tip = [330 + 1.55 * tw[0], 430 + 1.55 * tw[1]];
  const rr = -0.55, fo = R(rr, [0, -128]), baseR = [tip[0] - fo[0], tip[1] - fo[1], rr];
  const hand = (k) => { const lt = R(-0.25, [40, 12]), baseL = [330 + 1.55 * lt[0] - R(0.35, [0, -128])[0], 430 + 1.55 * lt[1] - R(0.35, [0, -128])[1], 0.35];   // left hand pinches the wing's root
    const base = k ? baseR : baseL, start = k ? [1130, 980] : [160, 960];
    return { x: lerp(start[0], base[0], enter) + (k ? -8 : 8) * ant + (k ? 60 : -60) * open, y: lerp(start[1], base[1], enter) + 8 * ant + 40 * open, rot: base[2] + (k ? 0.08 : -0.08) * open, s: 1.25, mirror: k === 0, curl: lerp(0.05, 0.4, smoothstep(12, 18, f)) - 0.3 * open, pinch: lerp(0, 0.8, smoothstep(12, 18, f)) - 0.6 * open, spread: 0.3 * (1 - smoothstep(10, 18, f)) + 0.25 * open }; };
  comp.layer(g, (lg) => { lg.setTransform(s, 0, 0, s, 0, 0); drawHand(lg, hand(0)); drawHand(lg, hand(1)); }, { off: [-9, 7], blur: 10, shadow: 'rgba(25,8,2,0.5)' });
}

// ================================================================ the end card: a cream sheet folds down, then the title inks in
function buildCard(words) {
  const c = mk(W, H), g = ctx2d(c), s = VIEW.dpr;
  g.fillStyle = 'rgb(246,234,206)'; g.fillRect(0, 0, W, H);
  if (!words) return c;
  g.setTransform(s, 0, 0, s, 0, 0); g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillStyle = 'rgba(52,24,10,0.55)'; g.font = 'italic 400 26px "IM Fell English"'; g.fillText('A Paper Kingdom tale', 640, 268);
  g.fillStyle = 'rgba(52,24,10,0.94)'; g.font = 'italic 400 62px "IM Fell English"'; g.fillText('The Dragon Who Couldn’t Fly', 640, 340);
  g.fillStyle = 'rgba(52,24,10,0.5)'; g.fillRect(610, 404, 60, 1.6);
  g.fillStyle = 'rgba(52,24,10,0.8)'; g.font = 'italic 400 30px "IM Fell English"'; g.fillText('Sometimes the loudest roar is a call for help.', 640, 452);
  return c;
}
function drawFold(g, i) {
  const f = on2(i) - CUE.card, u = ease.inOutCubic(clamp(f / 22)), textA = smoothstep(26, 44, f);
  if (u <= 0) return;
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); const h = H * u;
  g.fillStyle = `rgba(20,8,2,${0.45 * u})`; g.fillRect(0, h, W, H - h);
  g.drawImage(CARD0, 0, 0, W, H, 0, 0, W, h);
  if (u < 1) { const sh = g.createLinearGradient(0, h - 90, 0, h); sh.addColorStop(0, 'rgba(70,34,12,0)'); sh.addColorStop(1, `rgba(70,34,12,${0.4 * (1 - u)})`); g.fillStyle = sh; g.fillRect(0, h - 90, W, 90); }
  if (textA > 0) { g.globalAlpha = textA; g.drawImage(CARD, 0, 0); g.globalAlpha = 1; }
  g.restore();
}
