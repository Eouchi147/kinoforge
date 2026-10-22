// The shot list (times from cues.json; every cut sits on a strong music hit or a narration start) + words on screen.
import { ease, clamp, lerp, smoothstep } from '/harness/kit/film.js';

const KEYS = ['x', 'y', 'z', 'mm', 'yaw', 'pitch', 'roll'];
const L = (a, b, k) => { const o = {}; for (const key of KEYS) { const av = a[key] ?? (key === 'mm' ? 35 : 0), bv = b[key] ?? av; o[key] = lerp(av, bv, k); } return o; };
// camera move from pose a to pose b over the shot, eased
export const mv = (a, b, e = ease.inOutSine) => (tl, u) => L(a, b, e(u));
export const still = (a) => () => a;

// [id, start]: each shot runs to the next start; every start is a strong music hit or a narration start
const SEQ = [['o1a', 0], ['o1b', 4.18], ['o2a', 6.943], ['o2b', 9.868], ['o3', 11.61], ['title', 14.582], ['x1a', 17.461], ['x1b', 20.503], ['x1c', 24.799], ['x2a', 28.305], ['x2b', 31.161], ['x2c', 35.109], ['x4', 38.15],
  ['m1a', 42.446], ['m1b', 45.883], ['m2a', 50.875], ['m2b', 54.195], ['m3a', 58.375], ['m3b', 60.743], ['m3c', 64.969], ['d1', 70.542], ['d2a', 75.117], ['d2b', 77.949], ['d3', 81.107], ['r1a', 84.2], ['r1b', 86.75],
  ['r3a', 90.395], ['r3b', 94.993], ['r3c', 98.244], ['p1a', 100.96], ['p1b', 103.909], ['a1a', 106.4], ['a1b', 109.064], ['a1c', 111.734], ['c1', 115.589], ['c2', 120.581], ['c3a', 124.993], ['c3b', 127.57],
  ['e1a', 131.332], ['e1b', 136.719], ['e1c', 139.436], ['e2', 142.965], ['j1a', 146.611], ['j1b', 151.185], ['j2a', 155.388], ['j2b', 158.639], ['f1a', 162.075], ['f1b', 165.117], ['f2a', 167.114], ['f2b', 172.315], ['f3', 174.032], ['end', 176.8], ['_', 179.4]];
const def = {};
const D = (n, o) => { def[n] = o; };

// ---- 1 to 2: the ship at golden dusk (o1)
D('o1a', { set: 'sea:dusk', cam: mv({ x: -5, z: 0, mm: 35 }, { x: 4, z: -30, mm: 35 }, ease.inOutSine), ship: { sc: 0.34, x: 300, y: 782 }, drift: 0.6 });
D('o1b', { set: 'sea:dusk', cam: mv({ x: 0, y: 0, z: -20, mm: 35 }, { x: -3, y: 1, z: -60, mm: 35 }), ship: { sc: 0.82, x: 410, y: 905 } });
D('x1a', { set: 'sea:dusk', cam: mv({ x: -4, y: 0, z: 0, mm: 35 }, { x: 2, y: 0, z: -22, mm: 35 }), ship: { sc: 0.66, x: 360, y: 852 } });

// ---- documents (candlelit parchment). dAt(X, Y, z): frame design point (X, Y) of the paper, zoomed by z (metres toward the page)
const dAt = (X, Y, z) => ({ x: (X - 360) * 0.0067, y: (640 - Y) * 0.0067, z, mm: 35 });
const rowsInk = (t0, dt, n = 10) => Object.fromEntries(Array.from({ length: n }, (_, i) => ['p' + i, t0 + i * dt]));
D('o2b', { set: 'doc:claim', cam: mv(dAt(380, 380, -1.5), dAt(380, 470, -4.0)), ink: { h: 9.95, l1: 10.15, l2: 10.7 } });
D('x4', { set: 'doc:ledger', cam: mv(dAt(440, 330, -3.0), dAt(440, 760, -3.2), ease.inOutCubic), ink: { h: 38.25, hn: 38.7, hp: 38.9, ...rowsInk(40.3, 0.17) } });
D('m3a', { set: 'doc:rule', cam: mv(dAt(360, 300, -2.6), dAt(360, 330, -3.4)), ink: { h: 58.5 } });
D('m3b', { set: 'doc:rule', cam: mv(dAt(360, 480, -3.4), dAt(360, 520, -3.9)), ink: { h: 0, a1: 60.8, a2: 63.3 } });
D('m3c', { set: 'doc:rule', cam: mv(dAt(360, 740, -3.4), dAt(360, 800, -4.0)), ink: { h: 0, a1: 0, a2: 0, b1: 65.0, b1b: 66.5, b2: 68.2 } });
D('c1', { set: 'doc:claim', cam: mv(dAt(360, 420, -2.4), dAt(360, 640, -3.6)), ink: { h: 115.8, l1: 116.45, l2: 117.2, l3: 119.0, l4: 120.0 } });
D('c3b', { set: 'doc:quote', cam: mv(dAt(360, 520, -2.6), dAt(360, 600, -3.6)), ink: { q0: 127.2, q1: 127.33, q2: 128.6, q3: 129.5 } });
D('j1b', { set: 'doc:kb', cam: mv(dAt(360, 500, -2.6), dAt(360, 610, -3.8)), ink: { h: 151.2, k1: 151.3, k2: 152.7, k3: 154.0 } });
D('f1a', { set: 'doc:ledger', cam: mv(dAt(250, 560, -3.8), dAt(300, 640, -4.0)), ink: { h: 0, hn: 0, hp: 0, ...rowsInk(0, 0) } });
D('f1b', { set: 'doc:ledger', cam: mv(dAt(300, 620, -4.0), dAt(560, 640, -3.4), ease.inOutCubic), ink: { h: 0, hn: 0, hp: 0, ...rowsInk(0, 0) } });

// ---- the night deck
D('d1', { set: 'deck', casksOn: false, cam: mv({ x: -0.25, z: 0 }, { x: 0.2, z: -1.5 }), swing: 0.24, period: 3.6 });
D('d2a', { set: 'deck', casksOn: false, cam: mv({ z: -3.2, yaw: -0.045, pitch: 0.05 }, { z: -4.2, yaw: -0.03, pitch: 0.04 }), swing: 0.3, period: 3.3 });
D('d2b', { set: 'deck', casksOn: false, cam: mv({ x: 0.1, z: -1.5 }, { x: 0.3, z: -4.4, yaw: 0.07, pitch: -0.01 }), swing: 0.14, period: 3.8 });
D('d3', { set: 'deck', casksOn: false, cam: mv({ x: -0.2, z: -2.2, yaw: 0.03 }, { x: 0.35, z: -2.6, yaw: 0 }), swing: 0.06, period: 4.4, moonK: 0.85 });
D('m2b', { set: 'deck', cam: mv({ z: -1.2, pitch: -0.2, yaw: 0.01 }, { z: -4.8, pitch: -0.275, yaw: 0.032 }), swing: 0.08, period: 4, casks: { level: () => 0.13 }, drips: [[55.8, 1.1], [57.6, 1.8], [60.0, 2.4]] });
D('r1b', { set: 'deck', cam: mv({ x: -0.1, z: -1.0, pitch: -0.14 }, { x: 0.15, z: -2.8, pitch: -0.2 }), swing: 0.12, period: 3, rain: () => 1, casks: { level: (t, i) => 0.12 + 0.82 * ease.inOutSine(clamp((t - (86.9 + 0.28 * i)) / 1.5)), ripples: true } });
D('r3a', { set: 'deck', casksOn: false, cam: mv({ x: -0.1, z: -1.5, pitch: -0.3 }, { x: 0.2, z: -2.6, pitch: -0.33 }), swing: 0.2, period: 3.4, chainMode: 'coil', chainAt: [360, 1230], chainScale: 1.35 });
D('r3c', { set: 'deck', casksOn: false, cam: mv({ x: 0.4, z: -1.2, yaw: 0.05 }, { x: 0.55, z: -3.0, yaw: 0.07, pitch: 0.01 }), swing: 0.14, period: 3.6, chainMode: 'hang' });

// ---- the court
D('o2a', { set: 'court', cam: mv({ z: -1, y: 0.1 }, { z: -5, y: 0.05 }) });
D('c2', { set: 'court', cam: mv({ x: 0.2, z: -2.5, yaw: 0.02 }, { x: 0.8, z: -6, yaw: 0.075, pitch: -0.03 }), jury: true });
D('c3a', { set: 'court', cam: mv({ x: -0.5, z: -2.4, yaw: -0.07 }, { x: -0.4, z: -5.2, yaw: -0.075, pitch: -0.035 }), lawyer: true });
D('j1a', { set: 'court', cam: mv({ z: -2.5, pitch: 0.05 }, { z: -6.8, pitch: 0.06 }), rain: (t) => smoothstep(149.9, 150.5, t) });
D('j2a', { set: 'court', cam: mv({ z: -3.5 }, { z: -8.0, pitch: 0.03 }), judge: false, jury: false, candleOff: { chand0: 155.7, chand4: 156.0, chand2: 156.35, chand6: 156.6, chand1: 156.9, chand5: 157.15, chand3: 157.45, chand7: 157.7, bench: 157.9, table: 158.2 } });
D('j2b', { set: 'court', cam: mv({ x: -0.9, z: -3.0, yaw: -0.14, pitch: -0.1 }, { x: -0.9, z: -5.0, yaw: -0.15, pitch: -0.11 }), judge: false, jury: false, candleOff: { chand0: 0, chand1: 0, chand2: 0, chand3: 0, chand4: 0, chand5: 0, chand6: 0, chand7: 0, bench: 0, table: 0, dock: 161.2 } });

// ---- the lantern (the motif): o3 in the dark, x1c at dusk ("care"), f3 the dawn it goes out in
D('o3', { set: 'lantern:night', cam: mv({ z: -0.5, y: -0.05 }, { z: -3.2, y: 0.05 }, ease.inOutSine), flame: () => 1 });
D('x1c', { set: 'lantern:dusk', cam: mv({ z: -3.8, x: 0.05 }, { z: -2.2, x: -0.02 }), flame: () => 1 });
D('f3', { set: 'lantern:dawn', cam: mv({ z: -4.0, y: 0.05 }, { z: -0.8, y: 0.0 }, ease.inOutSine), flame: (t) => 1 - smoothstep(176.05, 176.55, t) * 1, smoke: (t) => (t > 176.3 ? clamp((t - 176.3) / 1.1) : 0), bgK: (t) => 0.62 + 0.38 * smoothstep(174.0, 176.7, t), fadeOut: 0.0 });

// ---- the sea: Jamaica passing, the captain's glass, the name board, moon, rain, rings, the rope, dawn, Black River
D('title', { set: 'sea:moon', ship: null, cam: mv({ x: -3, z: 0 }, { x: 3, z: -8 }), drift: 0.4 });
D('x1b', { set: 'sea:dusk', nameBoard: { zong: (t) => smoothstep(20.8, 21.6, t) * (1 - smoothstep(23.7, 24.1, t)), zorg: (t) => smoothstep(23.8, 24.4, t) }, ship: (tl, u) => ({ sc: lerp(1.75, 2.05, ease.inOutSine(u)), x: lerp(690, 760, ease.inOutSine(u)), y: lerp(1030, 1060, u) }), cam: mv({ x: 0, y: 0, z: 0 }, { x: -0.1, y: 0.1, z: -8 }) });
D('m1a', { set: 'sea:dusk', coast: { t0: 43.9, tp: 42.446, x0: 300 }, ship: { sc: 0.5, x: 310, y: 786 }, cam: mv({ x: -4, z: 0 }, { x: 5, z: -20 }), drift: 0.6 });
D('m1b', { set: 'sea:dusk', coast: { t0: 43.9, tp: 42.446, x0: 300 }, captain: true, glass: (t) => { const up = smoothstep(46.2, 46.8, t) * (1 - smoothstep(47.9, 48.5, t)); return -1.05 + 1.5 * up; },
  ship: (tl, u) => { const k = ease.inOutSine(clamp((tl - 2.2) / 2.6)); return { sc: lerp(1.5, 0.66, k), x: lerp(570, 380, k), y: lerp(980, 850, k) }; }, cam: mv({ x: 0, z: 0 }, { x: 0.3, z: -10 }), drift: 0.8 });
D('m2a', { set: 'sea:moon', ship: { sc: 0.3, x: 380, y: 776 }, cam: mv({ x: 2, z: 0 }, { x: -2, z: -14 }), drift: 0.5 });
D('r1a', { set: 'sea:moon', ship: { sc: 0.52, x: 370, y: 810 }, roll: 2.2, rain: (t) => smoothstep(84.3, 85.3, t), cam: mv({ x: -2, z: 0 }, { x: 2, z: -18 }), drift: 0.8 });
D('r3b', { set: 'sea:moon', ship: null, cam: mv({ x: -1.5, y: -0.25, z: 0 }, { x: 1.2, y: -0.2, z: -6 }), drift: 0.5,
  rings: [[94.99, 200, 960, 1.0], [95.4, 470, 1010, 1.1], [95.74, 330, 1100, 1.2], [96.2, 560, 930, 0.9], [96.76, 130, 1060, 1.1], [96.92, 430, 1170, 1.3], [97.2, 260, 1000, 1.0], [97.5, 600, 1080, 1.1], [97.8, 360, 940, 0.9], [98.0, 500, 1130, 1.2]] });
D('p1a', { set: 'sea:moon', ship: null, hullSide: true, tension: (t) => smoothstep(103.2, 103.7, t), cam: mv({ x: 0, y: -0.3, z: 0, pitch: 0.0 }, { x: 0.05, y: -0.3, z: -3, pitch: 0.02 }), drift: 0.5 });
D('p1b', { set: 'sea:moon', ship: null, hullSide: true, climber: (t) => ease.inOutSine(clamp((t - 104.0) / 2.2)), tension: () => 1, cam: mv({ x: 0.05, y: -0.3, z: -3, pitch: 0.02 }, { x: 0.05, y: 0.1, z: -4.5, pitch: 0.17 }, ease.inOutSine), drift: 0.5 });
D('a1a', { set: 'sea:dawn', ship: { sc: 0.4, x: 330, y: 778 }, cam: mv({ x: -2, z: 0 }, { x: 2, z: -10 }), drift: 0.5, fadeIn: 0.6 });
D('a1b', { set: 'sea:dusk', harbour: true, ship: { sc: 0.78, x: 300, y: 868 }, roll: 0.5, cam: mv({ x: -2, y: 0.1, z: 0 }, { x: 2.5, y: 0.05, z: -14 }), drift: 0.3 });

// ---- the ship in section: one small light per person
const W17 = (t) => smoothstep(29.1, 29.5, t);
D('x2a', { set: 'section', cam: mv({ x: 0, y: -0.2, z: 0 }, { x: 0, y: 0.4, z: -2.5 }), dots: (t) => ({ crew: clamp((t - 29.2) / 0.9) * 17, cap: 0, dim: 0, keep: 440, fade: 0 }),
  words: (t) => [{ text: '17', y: 0.17, px: 120, a: smoothstep(29.2, 29.8, t) * (1 - smoothstep(31.0, 31.5, t)) }, { text: 'crew', y: 0.235, px: 40, sub: true, a: smoothstep(29.5, 30.0, t) * (1 - smoothstep(31.0, 31.5, t)), col: '#dce8ff' }] });
D('x2b', { set: 'section', cam: mv({ x: 0, y: 0.3, z: -2.0 }, { x: 0, y: -0.6, z: -3.8 }, ease.inOutCubic), dots: (t) => ({ crew: 17, cap: clamp((t - 31.55) / 2.9) * 440, dim: 0, keep: 440, fade: 0 }),
  words: (t) => { const n = Math.round(clamp((t - 31.55) / 2.9) * 440 / 10) * 10; return [{ text: String(n >= 440 ? 440 : n), y: 0.14, px: 120, a: smoothstep(31.6, 32.1, t), col: '#ffd9a0' }, { text: 'captives', y: 0.205, px: 40, sub: true, a: smoothstep(32.2, 32.8, t), col: '#ffd9a0' }]; } });
D('x2c', { set: 'section', cam: mv({ x: 0, y: -0.5, z: -3.6 }, { x: 0, y: 0.1, z: -0.4 }, ease.inOutSine), dots: (t) => ({ crew: 17, cap: 440, dim: smoothstep(35.0, 35.9, t) * (1 - smoothstep(37.2, 37.9, t)), keep: 440, fade: 0 }),
  words: (t) => [{ text: '440', y: 0.14, px: 120, a: 1 - smoothstep(37.4, 38.0, t), col: '#ffd9a0' }, { text: 'captives', y: 0.205, px: 40, sub: true, a: 1 - smoothstep(37.4, 38.0, t), col: '#ffd9a0' }] });
D('a1c', { set: 'section', cam: mv({ x: 0, y: -0.1, z: -1.0 }, { x: 0, y: -0.3, z: -3.0 }), dots: (t) => ({ crew: 17, cap: 440, dim: 0, keep: 208, fade: smoothstep(111.9, 114.4, t) }),
  words: (t) => { const k = smoothstep(111.9, 114.4, t); const n = Math.round(lerp(440, 208, k)); return [{ text: String(n), y: 0.14, px: 120, a: 1, col: '#ffd9a0' }, { text: 'alive', y: 0.205, px: 40, sub: true, a: smoothstep(112.5, 113.2, t), col: '#ffd9a0' }]; } });

// ---- the lane: Equiano, Sharp, the letter; and the lit window
D('e1a', { set: 'street', sh: false, eqX: () => 0, cam: mv({ x: -0.2, z: 0 }, { x: 0.2, z: -14 }) });
D('e1b', { set: 'street', sh: false, cam: mv({ x: 0.55, y: 0.5, z: -26, pitch: -0.02 }, { x: 0.6, y: 0.45, z: -29, pitch: -0.02 }) });
D('e1c', { set: 'street', shX: (t) => (1 - ease.outCubic(clamp((t - 139.55) / 1.6))) * 240, letter: (t) => ({ k: clamp((t - 141.7) / 0.9) }), cam: mv({ x: 0.25, y: 0.1, z: -16 }, { x: 0.4, y: 0.15, z: -21 }) });
D('e2', { set: 'street', writing: true, eq: false, sh: false, handLamp: false, cam: mv({ x: -1.4, y: 0.2, z: -12, yaw: -0.08, pitch: -0.04 }, { x: -1.6, y: 0.05, z: -50, yaw: -0.07, pitch: -0.06 }, ease.inOutSine) });

// ---- the road: the lamps take their light one by one, then the morning
const postAt = (t0, dt) => (t, i) => clamp((t - (t0 + i * dt)) / 0.5);
D('f2a', { set: 'road', post: postAt(167.7, 0.62), dawn: (t) => smoothstep(167.1, 173.0, t) * 0.35, cam: mv({ x: 0.0, y: -0.15, z: 0, pitch: 0.0 }, { x: 0.1, y: 0.2, z: -8, pitch: 0.02 }) });
D('f2b', { set: 'road', post: () => 1, dawn: (t) => 0.35 + 0.65 * smoothstep(172.3, 176.0, t), cam: mv({ x: 0.1, y: 0.4, z: -9, pitch: 0.05 }, { x: 0.05, y: 0.55, z: -16, pitch: 0.08 }), words: (t) => [{ text: '1807', y: 0.30, px: 120, a: smoothstep(172.5, 173.3, t) * (1 - smoothstep(173.8, 174.03, t)) }] });
const SHOTS = [];
for (let i = 0; i + 1 < SEQ.length; i++) {
  const n = SEQ[i][0]; const d = def[n] || {};
  SHOTS.push({ id: n, t0: SEQ[i][1], t1: SEQ[i + 1][1], set: d.set || null, cam: d.cam || still({ mm: 35 }), ship: d.ship, drift: d.drift, ...d });
}
export { SHOTS };

// ---- words on screen
export const LABELS = [
  { in: 0.5, out: 5.9, lines: ['THE CARIBBEAN', '1781'] },
  { in: 17.6, out: 24.4, lines: ['THE ZONG', 'once the Dutch ship Zorg'] },
  { in: 42.5, out: 49.6, lines: ['JAMAICA', '27 November 1781'] },
  { in: 70.3, out: 75.0, lines: ['29 NOVEMBER 1781'] },
  { in: 81.1, out: 84.0, lines: ['1 DECEMBER 1781'] },
  { in: 109.1, out: 115.5, lines: ['BLACK RIVER, JAMAICA', '22 December 1781'] },
  { in: 121.0, out: 124.9, lines: ['LONDON', '6 March 1783'] },
  { in: 125.0, out: 127.5, lines: ["THE OWNERS' LAWYER", 'in court, 1783'] },
  { in: 131.4, out: 139.3, lines: ['OLAUDAH EQUIANO', 'and Granville Sharp, 19 March 1783'] },
  { in: 146.7, out: 151.0, lines: ["COURT OF KING'S BENCH", '22 May 1783'] },
];
export const TITLE = { in: 14.9, out: 17.4 };
export const END = { in: 176.8, out: 179.4 };

// narration captions: one per sentence, from the word timings (the quoted line is set as a document instead)
export function captionsFrom(cues) {
  const out = [];
  for (const line of cues.lines) {
    let cur = []; const flush = () => { if (!cur.length) return; out.push({ text: cur.map((w) => w[0]).join(' '), in: cur[0][1] - 0.05, out: cur[cur.length - 1][2] + 0.3 }); cur = []; };
    for (const w of line.words) { if (line.quote && /court:$/.test(cur.map((x) => x[0]).join(' ') + ' ' + w[0]) === false && cur.some((x) => /court:$/.test(x[0]))) break; cur.push(w); if (/[.?]$/.test(w[0]) || (line.quote && /court:$/.test(w[0]))) flush(); }
    flush();
  }
  return out;
}
