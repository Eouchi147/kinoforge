// The shot plan against cues.json: 9 scenes, 29 shots (average 5.8 s). Every cut has a written reason in NOTES.md.
// Times are seconds on the film's timeline. Cuts sit on a story beat: the end of a sentence, the first word of the next, or a strong music hit.
// Camera keys: [localTime, {x,y,z,pan,tilt,roll,mm}, easeName]. Every move is a "glide" (ease in, steady middle, ease out) at speeds a camera operator can make
// (pushes under 5 % per second, pans under 8 % of the frame per second). Planes are painted as seen from the reference camera (0,0,0, pan 0, tilt 0, 35 mm).
import { clamp } from '/harness/kit/film.js';

export function buildShots(cues, duration) {
  const list = [];
  let t = 0;
  const C = (x = 0, y = 0, z = 0, pan = 0, tilt = 0, mm = 35, roll = 0) => ({ x, y, z, pan, tilt, mm, roll });
  const look = (px, py, mm = 35, x = 0, y = 0, z = 0, roll = 0) => ({ x, y, z, pan: -Math.atan((px - 360) / 1866.7), tilt: -Math.atan((py - 640) / 1866.7), mm, roll });
  const S = (id, set, t1, o = {}) => { const sh = { id, set, t0: t, t1: t1 ?? duration, cam: [[0, C()]], breath: 0.35, ...o }; sh.dur = sh.t1 - sh.t0; t = sh.t1; list.push(sh); return sh; };
  const lampsOnRoad = (u, t0, dir, v, n = 9, extra = {}) => ({ u, t: t0, dir, v, n, ...extra });

  // ================= SCENE 1: THE ROAD (0 to 12.19). Who walks the long road at dusk?
  // 1a: a captive column descends the switchbacks at a real walking pace; the lanterns light group by group on the hits; the escort halts and lets them go on
  S('r1a', 'road', 8.429, { mode: 'army', cam: [[0, { ...look(360, 690, 30), y: 7, z: 0 }], [8.43, { ...look(350, 840, 33), y: 3, z: -22 }]], breath: 0.5,
    lit: [5.9, 6.339, 6.525, 6.92, 7.477], litRest: [7.7, 8.4], halt: [4.2, 5.4] });
  // 1b: change of scale: close on one lantern group, hands on shoulders, as the word "Blind." lands; the image holds under the first words of the next line
  S('r1b', 'march', 12.19, { mode: 'blind', h: 430, T: 1.4, lampOn: 5.9, cam: [[0, C(0, 0, 0)], [3.761, C(2.66, 0, 0), 'linear']], breath: 0 });
  // ================= SCENE 2: THE PAGE (12.19 to 18.65). Who wrote it down? The manuscript writes itself, the light draws back, the title
  S('p2a', 'page', 18.646, { capShade: 0.72, scribe: [12.2, 15.3], dimTo: 0.5, dimAt: [15.6, 17.4], card: { t1: 0.45, t2: 1.35, out: 0.4, at: 16.2, dy: -310 },
    cam: [[0, look(330, 300, 31)], [2.4, look(350, 520, 32)], [6.456, { ...look(362, 650, 26), z: 0 }]] });
  // ================= SCENE 3: TWO ENEMIES (18.65 to 34.99). Who are they, and how long have they been at war?
  // 3a: the emperor in his city: the skyline, then the man; the lamps of Constantinople light on the hits
  S('c3a', 'city', 25.728, { windows: 0.3, windowsTo: [0.3, 0.6], lamps: [23.174, 23.8, 24.009, 24.567, 24.776], cam: [[0, look(400, 830, 27)], [7.08, { ...look(500, 900, 36), z: 0 }]], breath: 0.6 });
  // 3b: the enemy: Samuel at his fire; at the hit the camera lifts and the far camp lights up across the valley
  S('c3b', 'camp', 31.811, { fireT0: 25.8, fireStep: 0.12, farStagger: true, farT0: 29.4, midT0: 25.9, cam: [[0, look(430, 1010, 36)], [2.6, look(430, 1000, 36)], [6.08, look(390, 760, 33)]], breath: 0.6 });
  // 3c: new information: the forty years, one notch at a time (the plank fills on the narration)
  S('c3c', 'table', 34.992, { mode: 'tally', marks: [31.95, 34.5, 39], base: 0.3, cam: [[0, look(360, 640, 34)], [3.18, look(360, 640, 39)]], breath: 0.3 });
  // ================= SCENE 4: NEAR-DEATH (34.99 to 44.6). How close did each of them come to dying?
  // 4a: Basil's ambush: riders in the gorge, stones from the rim on the hits, one cloak turns and escapes toward us
  S('n4a', 'gorge', 38.73, { mode: 'ride', riders: 6, hits: [36.27, 37.222], cam: [[0, look(360, 780, 30)], [3.74, look(360, 810, 33)]], breath: 0.6 });
  // 4b: Samuel among the dead: the night field, the push toward one still figure, a breath, and at the end he lifts his head
  S('n4b', 'field', 44.606, { mode: 'dead', fx: 330, fy: 1000, rise: 43.0, cam: [[0, look(360, 780, 30)], [5.876, look(350, 985, 42)]], breath: 0.4 });
  // ================= SCENE 5: KLEIDION (44.6 to 76.74). Will the wall hold?
  // 5a: the wall goes up: one long slow dolly from the gorge floor, workers and carts everywhere, dust in the afterglow
  S('k5a', 'pass', 54.892, { mode: 'build', embers: true, cam: [[0, { ...look(360, 735, 27), z: 0, y: -2 }], [10.286, { ...look(360, 650, 28), z: -46, y: 3 }]], breath: 0.5 });
  // 5b: the name: the iron key on the table; a single glint
  S('k5b', 'table', 56.424, { mode: 'key', glint: 55.7, base: 0.3, cam: [[0, look(360, 640, 36)], [1.53, look(360, 640, 40)]], breath: 0.3 });
  // 5c: Basil attacks again and again: the same view, three waves, the wall holds; we hold on it after the last wave
  S('k5c', 'pass', 62.341, { mode: 'attack', hits: [56.424, 56.587, 57.702, 58.468, 60.488], waves: [{ t0: 56.0, seed: 1, yStop: 770, run: 2.0, hold: 0.8, back: 1.4, n: 40 }, { t0: 58.35, seed: 2, yStop: 780, run: 1.8, hold: 0.7, back: 1.3, n: 40 }, { t0: 60.3, seed: 3, yStop: 790, run: 1.6, hold: 0.4, back: 1.2, n: 30 }],
    cam: [[0, { ...look(360, 760, 30), z: -6, y: 1 }], [5.917, { ...look(360, 690, 33), z: -14, y: 1 }]], breath: 0.7 });
  // 5d: time passes (a dissolve): night; the general's torches cross the mountain and come down behind the wall
  S('k5d', 'pass', 68.801, { mode: 'column', night: 1, dissolve: 1.0, cam: [[0, look(470, 410, 32)], [6.46, look(400, 600, 34)]], breath: 0.4 });
  // 5e: the rout and its price: flares behind the wall, the defenders run; then the camera comes down to the captives on the floor
  S('k5e', 'pass', 76.742, { mode: 'rout', night: 1, rout: 68.95, hits: [68.917, 69.103, 69.6, 70.2], embers: true, captivesFrom: 72.9,
    shake: [[0.1, 1, 0.5]], cam: [[0, look(360, 640, 33)], [4.1, look(360, 650, 35)], [7.94, look(360, 1010, 33)]], breath: 0.5 });
  // ================= SCENE 6: THE ESCAPE AND THE GORGE (76.74 to 90.88). Is the war over?
  // 6a: pursuers close in, the son lifts his father into the saddle, they ride away from us into the dark; the camera follows them
  S('e6a', 'field', 82.686, { mode: 'escape', t0: 76.742, fire: true, cam: [[0, look(420, 900, 32)], [2.8, look(430, 905, 33)], [5.94, look(520, 830, 35)]], breath: 0.5 });
  // 6b: not over: the Bulgarian fires are relit one by one
  S('e6b', 'camp', 85.31, { noSamuel: true, banners: true, farStagger: false, fireT0: 82.826, fireStep: 0.12, lit: 1, cam: [[0, look(380, 920, 31)], [2.624, look(400, 960, 34)]], breath: 0.5 });
  // 6c: the governor's men in a gorge: stones, dust, a banner that lies down
  S('e6c', 'gorge', 90.878, { mode: 'column', men: 9, fallAt: 87.4, t0: 85.31, hits: [85.867, 86.912, 87.4, 89.141, 89.466], cam: [[0, look(360, 770, 30)], [5.568, look(360, 740, 33)]], breath: 0.5 });
  // ================= SCENE 7: THE ORDER (90.88 to 112.36). What did Basil order, and how was it written?
  S('o7a', 'table', 93.344, { mode: 'seal', sealAt: 91.951, base: 0.3, cam: [[0, look(360, 600, 32)], [2.466, look(360, 690, 38)]], breath: 0.3 });
  S('o7b', 'page', 100.774, { capShade: 0.72, cam: [[0, look(360, 470, 32)], [3.0, look(360, 560, 34)], [7.43, look(360, 700, 38)]] });
  S('o7c', 'road', 103.95, { mode: 'groups', dark: 0.7, groups: [0.84, 0.66, 0.5, 0.3, 0.14].map((u, i) => lampsOnRoad(u, 100.774, -1, 1.1, 9, { on: [101.193, 101.82, 102.284, 102.9, 103.5][i], seed: 6 + i })), cam: [[0, { ...look(360, 760, 30), y: 8 }], [3.176, { ...look(350, 830, 31), y: 4, z: -10 }]], breath: 0.4 });
  S('o7d', 'march', 108.6, { mode: 'blind', h: 460, T: 1.4, lampOn: 104.559, cam: [[0, C(0, 0, 0)], [4.65, C(3.29, 0, 0), 'linear']], breath: 0 });
  S('o7e', 'road', 112.358, { mode: 'groups', dark: 0.66, groups: [0.88, 0.76, 0.66, 0.56, 0.47, 0.38, 0.3, 0.22, 0.14].map((u, i) => lampsOnRoad(u, 108.6, -1, 1.1, 9, { on: 0, seed: 11 + i })), cam: [[0, { ...look(360, 800, 29), y: 9 }], [3.758, { ...look(360, 880, 31), y: 5, z: -14 }]], breath: 0.4 });
  // ================= SCENE 8: PRILEP (112.36 to 128.87). What does Samuel do when he sees them?
  S('l8a', 'prilep', 116.75, { lanterns: [14, 112.5, 114.6], samuel: { x: 170, h: 360 }, collapse: 115.6, guard: true, cam: [[0, look(300, 930, 30)], [4.392, look(290, 905, 34)]], breath: 0.5 });
  S('l8b', 'table', 125.191, { mode: 'cup', pour: [119.2, 121.6], lift: [122.1, 122.7, 123.3, 123.8], gutter: [123.9, 125.4], base: 0.3, cam: [[0, look(380, 800, 33)], [8.441, look(280, 740, 38)]], breath: 0.3 });
  S('l8c', 'prilep', 128.866, { dawn: true, window: 127.4, dissolve: 1.0, cam: [[0, look(520, 600, 32)], [3.675, look(545, 560, 37)]], breath: 0.4 });
  // ================= SCENE 9: AS THEY SAY (128.87 to 169.05). Was it true, and what is left?
  S('a9a', 'page', 140.108, { capShade: 0.72, cam: [[0, look(372, 1060, 26)], [2.4, look(372, 1060, 26)], [6.9, look(372, 1500, 37)], [11.242, look(372, 1620, 41)]] });
  S('a9b', 'page', 144.906, { capShade: 0.72, cam: [[0, look(360, 700, 36)], [1.5, look(360, 700, 36)], [4.798, look(366, 1120, 25)]] });
  S('a9c', 'camp', 149.513, { people: true, noSamuel: true, banners: true, farStagger: false, lit: 1, cam: [[0, look(380, 930, 30)], [4.607, look(410, 950, 34)]], breath: 0.6 });
  S('a9d', 'city', 160.891, { windows: 0.5, words: [{ text: 'THE BULGAR SLAYER', in: 152.1, out: 156.4, y: 190 }], fadeBasil: [155.9, 157.0], cycle: { t0: 156.8, t1: 160.891, n: 1 }, cam: [[0, look(505, 880, 40)], [7.2, look(500, 860, 46)], [11.378, look(430, 820, 34)]], breath: 0.5 });
  S('a9e', 'road', null, { mode: 'groups', dark: 0.58, groups: [0.8, 0.6, 0.44, 0.3, 0.18].map((u, i) => lampsOnRoad(u, 160.891, 1, 1.1, 9, { on: 0, off: 162.9 + i * 0.55 + (i === 4 ? 0.6 : 0), seed: 21 + i })), card: { t1: 0.5, t2: 1.4, at: 166.449 }, cam: [[0, { ...look(360, 760, 30), y: 6 }], [8.158, { ...look(360, 700, 33), y: 14 }]], breath: 0.4 });
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
  // a caption leaves before the next one arrives: no two lines of type are ever on screen together
  caps.sort((x, y) => x.in - y.in); for (let i = 0; i < caps.length - 1; i++) caps[i].out = Math.min(caps[i].out, caps[i + 1].in + 0.05);
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
