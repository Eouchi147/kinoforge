// The shot list against cues.json (times in seconds on the film's timeline; cuts sit on narration and on strong music hits).
// Camera keys: [localTime, {x,y,z,pan,tilt,roll,mm}, easeName]. Planes are painted as seen from the reference camera (0,0,0, pan 0, tilt 0, 35 mm).
import { clamp } from '/harness/kit/film.js';

export function buildShots(cues, duration) {
  const L = Object.fromEntries(cues.lines.map((l) => [l.id, l]));
  const wd = (id, word, nth = 0) => { const ws = L[id].words.filter((w) => w[0].toLowerCase().replace(/[^a-z0-9']/g, '') === word.toLowerCase()); return ws[nth][1]; };
  const list = [];
  let t = 0;
  const C = (x = 0, y = 0, z = 0, pan = 0, tilt = 0, mm = 35, roll = 0) => ({ x, y, z, pan, tilt, mm, roll });
  const S = (id, set, t1, o = {}) => { const sh = { id, set, t0: t, t1: t1 ?? duration, cam: [[0, C()]], ...o }; sh.dur = sh.t1 - sh.t0; t = sh.t1; list.push(sh); return sh; };

  // ---- the promise (0 to 18.6): the long road at dusk, the lanterns, the page
  S('o1a', 'road', 2.554, { mode: 'captives', cam: [[0, C(-6, 4, 0, 0.0, 0, 32)], [2.554, C(-2, 3, 0, 0, 0, 34)]], breath: 1 });
  S('o1b', 'road', 5.371, { mode: 'captives', cam: [[0, C(30, 2, 0, -0.02, -0.04, 46)], [2.817, C(42, 1, 0, -0.03, -0.06, 50)]], breath: 1 });
  S('o2a', 'road', 8.429, { mode: 'lanterns', groups: [{ u: 0.9, on: 5.9, seed: 1 }, { u: 0.72, on: 6.339, seed: 2 }, { u: 0.55, on: 6.525, seed: 3 }, { u: 0.36, on: 6.92, seed: 4 }, { u: 0.2, on: 7.477, seed: 5 }].map((g) => ({ ...g, dir: -1, v: 9, t: 5.371 - 5.371, n: 9 })), cam: [[0, C(0, 4, 0, 0.0, 0.0, 30)], [3.058, C(8, 6, 0, 0.0, 0.01, 33)]], breath: 1 });
  S('o2b', 'march', 10.937, { mode: 'blind', cam: [[0, C(0, 0, 0, 0, 0, 35)], [2.5, C(2.2, 0, 0, 0, 0, 35)]], breath: 0.6 });
  S('o3a', 'page', 12.19, { mode: 'sky', cam: [[0, C(0, 0, 0, 0, 0, 30)], [1.25, C(0, 0, 0, 0, 0, 33)]] });
  S('o3b', 'page', 15.78, { mode: 'sky', cam: [[0, C(0, 0, 0, 0, 0, 33)], [3.59, C(0, 0, 0, 0, 0, 40)]] });
  S('title', 'road', 18.646, { mode: 'title', dark: 0.62, groups: [{ u: 0.62, on: 15.9, seed: 1, dir: 1 }, { u: 0.4, on: 16.2, seed: 2, dir: 1 }, { u: 0.2, on: 16.5, seed: 3, dir: 1 }].map((g) => ({ ...g, v: 5, t: 15.78, n: 9 })), card: { t1: 0.5, t2: 1.4 }, cam: [[0, C(0, 5, 0, 0, 0, 30)], [2.866, C(0, 7, 0, 0, 0.02, 31)]], fadeIn: 0.5 });
  S('end', 'road', null, {});
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
export const LABELS = [];
