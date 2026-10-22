// The shot list against cues.json (times in seconds on the film's timeline; cuts sit on narration and on strong music hits).
// Camera keys: [localTime, {x,y,z,pan,tilt,roll,mm}, easeName]. Planes are painted as seen from the reference camera (0,0,0, pan 0, tilt 0, 35 mm).
import { clamp } from '/harness/kit/film.js';

export function buildShots(cues, duration) {
  const L = Object.fromEntries(cues.lines.map((l) => [l.id, l]));
  const wd = (id, word, nth = 0) => { const ws = L[id].words.filter((w) => w[0].toLowerCase().replace(/[^a-z0-9']/g, '') === word.toLowerCase()); return ws[nth][1]; };
  const list = [];
  let t = 0;
  const C = (x = 0, y = 0, z = 0, pan = 0, tilt = 0, mm = 35, roll = 0) => ({ x, y, z, pan, tilt, mm, roll });
  const look = (px, py, mm = 35, x = 0, y = 0, z = 0, roll = 0) => ({ x, y, z, pan: -Math.atan((px - 360) / 1866.7), tilt: -Math.atan((py - 640) / 1866.7), mm, roll });
  const S = (id, set, t1, o = {}) => { const sh = { id, set, t0: t, t1: t1 ?? duration, cam: [[0, C()]], ...o }; sh.dur = sh.t1 - sh.t0; t = sh.t1; list.push(sh); return sh; };

  // ---- the promise (0 to 18.6): the long road at dusk, the lanterns, the page
  S('o1a', 'road', 2.554, { mode: 'captives', cam: [[0, C(-6, 4, 0, 0.0, 0, 32)], [2.554, C(-2, 3, 0, 0, 0, 34)]], breath: 1 });
  S('o1b', 'road', 5.371, { mode: 'captives', cam: [[0, C(30, 2, 0, -0.02, -0.04, 46)], [2.817, C(42, 1, 0, -0.03, -0.06, 50)]], breath: 1 });
  S('o2a', 'road', 8.429, { mode: 'lanterns', groups: [{ u: 0.9, on: 5.9, seed: 1 }, { u: 0.72, on: 6.339, seed: 2 }, { u: 0.55, on: 6.525, seed: 3 }, { u: 0.36, on: 6.92, seed: 4 }, { u: 0.2, on: 7.477, seed: 5 }].map((g) => ({ ...g, dir: -1, v: 9, t: 0, n: 9 })), cam: [[0, C(0, 4, 0, 0.0, 0.0, 30)], [3.058, C(8, 6, 0, 0.0, 0.01, 33)]], breath: 1 });
  S('o2b', 'march', 10.937, { mode: 'blind', h: 430, T: 1.4, cam: [[0, C(0, 0, 0)], [2.508, C(1.78, 0, 0), 'linear']], breath: 0.3 });
  S('o3a', 'page', 12.19, { capShade: 0.72, cam: [[0, look(330, 300, 30)], [1.25, look(340, 330, 32)]] });
  S('o3b', 'page', 15.78, { capShade: 0.72, cam: [[0, look(360, 560, 33)], [3.59, look(360, 640, 38)]] });
  S('title', 'road', 18.646, { mode: 'title', dark: 0.62, groups: [{ u: 0.62, on: 15.9, seed: 1, dir: 1 }, { u: 0.4, on: 16.2, seed: 2, dir: 1 }, { u: 0.2, on: 16.5, seed: 3, dir: 1 }].map((g) => ({ ...g, v: 5, t: 15.78, n: 9 })), card: { t1: 0.5, t2: 1.4, out: 0.35 }, cam: [[0, C(0, 5, 0, 0, 0, 30)], [2.866, C(0, 7, 0, 0, 0.02, 31)]], fadeIn: 0.5 });
  // ---- Basil and Samuel (18.6 to 34.2): Constantinople at dusk, the Bulgarian camp, the tally of forty years
  S('x1a', 'city', 19.969, { noBasil: true, windows: 0.3, cam: [[0, look(235, 640, 52)], [1.323, look(235, 600, 58)]], breath: 1 });
  S('x1b', 'city', 22.686, { windows: 0.35, cam: [[0, look(505, 880, 46)], [2.717, look(505, 860, 52)]], breath: 0.8 });
  S('x1c', 'city', 25.728, { windows: 0.45, lamps: [23.174, 23.8, 24.009, 24.567, 24.776], cam: [[0, look(470, 900, 42)], [3.042, { ...look(380, 800, 30), z: 20, y: 6 }]], breath: 0.8 });
  S('x2a', 'camp', 29.489, { fireT0: 25.8, fireStep: 0.12, farStagger: true, farT0: 25.9, cam: [[0, look(380, 900, 30)], [3.761, look(430, 960, 38)]], breath: 1 });
  S('x2b', 'camp', 31.811, { noSamuel: true, people: false, banners: false, farStagger: true, farT0: 29.45, fireT0: 0, lit: 0.0, cam: [[0, look(380, 690, 46)], [2.322, look(360, 700, 50)]], breath: 1 });
  S('x2c', 'table', 34.992, { mode: 'tally', marks: [31.95, 34.5, 39], base: 0.3, cam: [[0, look(360, 620, 36)], [3.181, look(360, 640, 40)]], breath: 0.8 });
  // ---- the ambush and the dead (34.99 to 44.6)
  S('x3a', 'gorge', 36.27, { mode: 'ride', riders: 7, hits: [], cam: [[0, look(360, 760, 30)], [1.278, look(360, 760, 32)]], breath: 1 });
  S('x3b', 'gorge', 38.73, { mode: 'ride', flee: true, riders: 6, hits: [36.27, 37.222], cam: [[0, look(360, 840, 34)], [2.46, look(360, 900, 36)]], breath: 2 });
  S('x3c', 'field', 40.821, { mode: 'dead', fx: 330, fy: 980, cam: [[0, look(360, 760, 28)], [2.091, look(350, 860, 32)]], breath: 1 });
  S('x3d', 'field', 43.305, { mode: 'dead', fx: 330, fy: 1010, rise: 43.0, cam: [[0, look(380, 930, 46)], [2.484, look(360, 960, 54)]], breath: 0.6 });
  S('x3e', 'field', 44.606, { mode: 'dead', fx: 330, fy: 1010, rise: 43.0, cam: [[0, look(380, 960, 54)], [1.301, look(360, 980, 58)]], breath: 0.6 });
  // ---- the wall (44.6 to 62.3)
  S('w1a', 'pass', 46.602, { mode: 'build', cam: [[0, look(360, 700, 28)], [1.996, look(360, 690, 31)]], breath: 1, embers: true });
  S('w1b', 'pass', 50.921, { mode: 'build', cam: [[0, look(330, 1000, 40, 0, 0, 0)], [4.319, look(380, 880, 36)]], breath: 1 });
  S('w1c', 'pass', 54.892, { mode: 'build', cam: [[0, look(360, 640, 30)], [3.971, look(360, 590, 38)]], breath: 1 });
  S('w1d', 'table', 55.844, { mode: 'key', glint: 55.0, base: 0.3, cam: [[0, look(360, 640, 36)], [0.952, look(360, 640, 42)]], breath: 0.6 });
  S('w2a', 'pass', 58.468, { mode: 'attack', hits: [56.424, 56.587, 57.702], waves: [{ t0: 55.9, seed: 1, yStop: 760, run: 1.6, hold: 0.7, back: 1.2, n: 38 }], cam: [[0, look(360, 900, 33)], [2.624, look(360, 850, 36)]], breath: 1.5 });
  S('w2b', 'pass', 60.488, { mode: 'attack', hits: [58.468, 59.4], waves: [{ t0: 58.2, seed: 2, yStop: 770, run: 1.4, hold: 0.6, back: 1.0, n: 40 }], cam: [[0, look(300, 780, 44)], [2.02, look(380, 760, 48)]], breath: 1.5 });
  S('w2c', 'pass', 62.341, { mode: 'held', cam: [[0, look(360, 650, 40)], [1.853, look(360, 640, 42)]], breath: 0.5, embers: true });
  // ---- the general over the mountain, the rout (62.3 to 74.1)
  S('t1a', 'pass', 65.248, { mode: 'column', night: 1, speed: 130, s0: 0, cam: [[0, look(450, 440, 34)], [2.907, look(430, 500, 36)]], breath: 1 });
  S('t1b', 'pass', 68.801, { mode: 'column', night: 1, speed: 190, s0: 378, cam: [[0, look(400, 540, 36)], [3.553, look(380, 640, 34)]], breath: 1 });
  S('t2a', 'pass', 70.728, { mode: 'flare', night: 1, rout: 68.95, hits: [68.917, 69.103, 69.6, 70.2], embers: true, cam: [[0, look(360, 640, 34)], [1.927, look(360, 620, 38)]], breath: 2, shake: [[0.1, 1, 0.5]] });
  S('t2b', 'pass', 71.819, { mode: 'flare', night: 0.95, rout: 68.95, hits: [70.728, 71.425], embers: true, cam: [[0, look(330, 600, 44)], [1.091, look(350, 590, 46)]], breath: 2 });
  S('t2c', 'pass', 74.118, { mode: 'captives', night: 0.8, cam: [[0, look(360, 1000, 34)], [2.299, look(360, 960, 36)]], breath: 1.2 });
  // ---- the flight of Samuel (74.1 to 82.7), the fires, the governor (82.7 to 90.9)
  S('s1a', 'field', 76.742, { mode: 'chase', search: false, fire: true, cam: [[0, look(360, 900, 32)], [2.624, look(380, 920, 34)]], breath: 1 });
  S('s1b', 'field', 78.832, { mode: 'mount', liftAt: 99, search: false, fire: true, cam: [[0, look(460, 900, 40)], [2.09, look(450, 920, 44)]], breath: 1 });
  S('s1c', 'field', 80.829, { mode: 'mount', liftAt: 0.2, search: false, fire: true, cam: [[0, look(440, 900, 44)], [1.997, look(430, 920, 46)]], breath: 1 });
  S('s1d', 'field', 82.686, { mode: 'gallop', search: true, fire: true, cam: [[0, look(380, 880, 34)], [1.857, look(300, 840, 38)]], breath: 2 });
  S('r1a', 'camp', 85.31, { noSamuel: true, people: false, banners: true, farStagger: false, fireT0: 82.826, fireStep: 0.12, lit: 1, cam: [[0, look(380, 900, 30)], [2.624, look(400, 940, 34)]], breath: 1 });
  S('r1b', 'gorge', 90.878, { mode: 'column', men: 9, fallAt: 87.4, t0: 85.31, hits: [85.867, 86.912, 87.4, 89.141, 89.466], cam: [[0, look(360, 760, 30)], [5.568, look(360, 740, 34)]], breath: 1, fadeOut: 1.3 });
  // ---- the order, the page (90.9 to 100.8)
  S('b1', 'table', 93.344, { mode: 'seal', sealAt: 91.951, base: 0.3, cam: [[0, look(360, 600, 32)], [2.466, look(360, 700, 40)]], breath: 0.8 });
  S('b2a', 'page', 97.199, { capShade: 0.72, cam: [[0, look(360, 480, 32)], [3.855, look(360, 620, 36)]] });
  S('b2b', 'page', 100.774, { capShade: 0.72, cam: [[0, look(360, 700, 38)], [3.575, look(360, 700, 44)]] });
  // ---- the long road home (100.8 to 112.4)
  S('b3a', 'road', 104.35, { mode: 'lanterns', groups: [{ u: 0.84, on: 101.193, seed: 6 }, { u: 0.66, on: 101.82, seed: 7 }, { u: 0.5, on: 102.284, seed: 8 }, { u: 0.3, on: 102.9, seed: 9 }, { u: 0.14, on: 103.5, seed: 10 }].map((g) => ({ ...g, dir: -1, v: 9, t: 100.774, n: 9 })), cam: [[0, C(-4, 6, 0, 0.0, 0.0, 30)], [3.576, C(6, 5, 0, 0.0, 0.0, 34)]], breath: 1 });
  S('b3b', 'march', 109.923, { mode: 'blind', h: 460, T: 1.4, lampOn: 104.559, cam: [[0, C(0, 0, 0)], [5.573, C(3.9, 0, 0), 'linear']], breath: 0.3 });
  S('b3c', 'road', 112.358, { mode: 'lanterns', dark: 0.66, groups: [0.88, 0.74, 0.62, 0.5, 0.4, 0.3, 0.2, 0.12].map((u, i) => ({ u, on: 105 + i * 0.5, seed: 11 + i, dir: -1, v: 7, t: 109.923, n: 9 })), cam: [[0, C(0, 8, 0, 0.0, 0.01, 28)], [2.435, C(0, 12, 0, 0, 0.03, 31)]], breath: 1 });
  // ---- Prilep: Samuel sees them coming, the cup, the end (112.4 to 128.9)
  S('d1a', 'prilep', 114.196, { lanterns: [11, 112.5, 114.0], samuel: { x: 190, h: 300 }, cam: [[0, look(330, 880, 30)], [1.838, look(340, 860, 32)]], breath: 1 });
  S('d1b', 'prilep', 115.334, { lanterns: [11, 100, 101], samuel: { x: 190, h: 300 }, cam: [[0, look(230, 880, 46)], [1.138, look(240, 860, 52)]], breath: 0.8 });
  S('d1c', 'prilep', 116.75, { lanterns: [11, 100, 101], samuel: { x: 190, h: 300 }, collapse: 115.6, guard: true, cam: [[0, look(240, 900, 48)], [1.416, look(250, 1000, 44)]], breath: 0.8 });
  S('d2a', 'table', 119.025, { mode: 'cup', base: 0.3, cam: [[0, look(380, 800, 34)], [2.275, look(390, 820, 38)]], breath: 0.8 });
  S('d2b', 'table', 122.021, { mode: 'cup', pour: [119.2, 121.6], base: 0.3, cam: [[0, look(430, 820, 40)], [2.996, look(450, 840, 44)]], breath: 0.8 });
  S('d2c', 'table', 124.087, { mode: 'cup', full: true, lift: [122.1, 122.7, 123.3, 123.8], gutter: [123.9, 125.4], hideJug: true, base: 0.3, cam: [[0, look(430, 800, 38)], [2.066, look(400, 780, 36)]], breath: 0.8 });
  S('d2d', 'table', 125.574, { mode: 'cup', gutter: [124.4, 125.4], hideJug: true, base: 0.25, cam: [[0, look(260, 700, 40)], [1.487, look(250, 700, 44)]], breath: 0.8 });
  S('d3a', 'prilep', 127.408, { dawn: true, window: 126.9, cam: [[0, look(540, 560, 34)], [1.834, look(545, 540, 44)]], breath: 0.8 });
  S('d3b', 'prilep', 128.866, { dawn: true, window: 1, cam: [[0, look(400, 700, 32)], [1.458, look(380, 720, 30)]], breath: 0.8 });
  // ---- but was it true? Two manuscripts disagree (128.9 to 144.9)
  S('q1a', 'page', 130.914, { capShade: 0.72, cam: [[0, look(372, 1330, 34)], [2.048, look(372, 1400, 36)]] });
  S('q1b', 'page', 133.933, { capShade: 0.72, cam: [[0, look(372, 1440, 36)], [3.019, look(372, 1520, 38)]] });
  S('q1c', 'page', 137.578, { capShade: 0.72, cam: [[0, look(372, 1540, 40)], [3.645, look(372, 1580, 46)]] });
  S('q1d', 'page', 140.388, { capShade: 0.72, cam: [[0, look(372, 1620, 42)], [2.81, look(372, 1760, 36)]] });
  S('q2', 'page', 144.939, { capShade: 0.72, cam: [[0, look(360, 700, 42)], [1.2, look(360, 720, 40)], [3.2, look(366, 1150, 22)], [4.551, look(366, 1150, 21)]] });
  // ---- the Bulgar Slayer, then the road (144.9 to 169.05)
  S('f1a', 'camp', 149.513, { people: true, noSamuel: true, farStagger: false, fireT0: 0, lit: 1, cam: [[0, look(380, 900, 32)], [4.574, look(420, 940, 38)]], breath: 1 });
  S('f1b', 'city', 151.905, { windows: 0.5, cam: [[0, look(505, 880, 46)], [2.392, look(505, 860, 50)]], breath: 0.8 });
  S('f1c', 'city', 153.832, { windows: 0.5, words: [{ text: 'THE BULGAR SLAYER', in: 152.1, out: 156.4, y: 190 }], cam: [[0, look(505, 870, 42)], [1.927, look(505, 850, 40)]], breath: 0.8 });
  S('f1d', 'city', 156.758, { windows: 0.5, words: [{ text: 'THE BULGAR SLAYER', in: 152.1, out: 156.4, y: 190 }], cam: [[0, look(505, 840, 56)], [2.926, look(505, 840, 62)]], breath: 0.8 });
  S('f1e', 'city', 160.891, { noBasil: true, cycle: { t0: 156.758, t1: 160.891, n: 1 }, cam: [[0, look(430, 820, 36)], [4.133, look(380, 780, 30)]], breath: 0.8 });
  S('f2a', 'road', 162.749, { mode: 'lanterns', dark: 0.6, groups: [0.8, 0.6, 0.44, 0.3, 0.18].map((u, i) => ({ u, on: 0, seed: 21 + i, dir: 1, v: 5, t: 160.891, n: 9 })), cam: [[0, C(0, 5, 0, 0, 0, 30)], [1.858, C(0, 6, 0, 0, 0.01, 31)]], breath: 0.8 });
  S('f2b', 'road', 166.449, { mode: 'lanterns', dark: 0.55, groups: [0.8, 0.6, 0.44, 0.3, 0.18].map((u, i) => ({ u, on: 0, off: 162.9 + i * 0.7, seed: 21 + i, dir: 1, v: 5, t: 160.891, n: 9 })), cam: [[0, C(0, 6, 0, 0, 0.01, 31)], [3.7, C(0, 8, 0, 0, 0.02, 33)]], breath: 0.8 });
  S('end', 'road', null, { mode: 'end', dark: 0.5, groups: [], card: { t1: 0.5, t2: 1.4 }, cam: [[0, C(0, 8, 0, 0, 0.02, 33)], [2.6, C(0, 9, 0, 0, 0.02, 34)]], breath: 0.5 });
  return list;
}

// captions from the word timings (lines break at sentence ends; long ones at a comma): split at sentence ends and long runs
export function buildCaptions(cues) {
  const caps = [];
  for (const l of cues.lines) {
    const ws = l.words; let a = 0;
    for (let i = 0; i < ws.length; i++) {
      const w = ws[i][0]; const end = /[.?!]$/.test(w) || (/,$/.test(w) && i - a >= 6) || i === ws.length - 1 || i - a >= 13;
      if (end) { const grp = ws.slice(a, i + 1); caps.push({ text: grp.map((x) => x[0]).join(' '), in: Math.max(0, grp[0][1] - 0.08), out: grp[grp.length - 1][2] + 0.55 }); a = i + 1; }
    }
  }
  return caps;
}
export const LABELS = [
  { text: 'THE BALKANS', sub: '1014', in: 0.7, out: 4.0, y: 150 },
  { text: 'BASIL II', sub: 'Eastern Roman emperor', in: 20.0, out: 23.4, y: 150 },
  { text: 'CONSTANTINOPLE', in: 23.9, out: 26.2, y: 150 },
  { text: 'SAMUEL', sub: 'tsar of the Bulgarians', in: 29.7, out: 33.0, y: 150 },
  { text: 'KLEIDION PASS', sub: 'summer 1014', in: 44.8, out: 49.5, y: 150 },
  { text: 'NIKEPHOROS XIPHIAS', sub: 'Byzantine general', in: 62.6, out: 66.4, y: 150 },
  { text: 'PRILEP', sub: 'October 1014', in: 112.5, out: 116.0, y: 150 },
  { text: '1014 TO 1018', in: 145.1, out: 148.8, y: 150 },
];
