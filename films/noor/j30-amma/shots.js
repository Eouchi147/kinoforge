// The shot plan against cues.json: 9 scenes, 20 shots. Every cut has a written reason (NOTES.md and the comment on each shot).
// Times come from the narration (line starts, word starts): the picture follows the sound and never changes it.
// Camera keys: [localTime, {x,y,z,pan,tilt,mm}]. Moves are slow "glides" (ease in, steady middle, ease out): pushes under 5 % per second.
// Planes are painted as seen from the reference camera (0,0,0, pan 0, tilt 0, 35 mm) in a 1280x720 design frame (focal 1050 px).
import { clamp } from '/harness/kit/film.js';

const F0 = 1050;
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9']/g, '');
export function resolver(cues) {
  const L = Object.fromEntries(cues.lines.map((l) => [l.id, l]));
  const word = (l, w, nth = 0) => { const want = norm(w); let k = 0; for (const x of l.words) { const h = norm(x[0]); if (h.startsWith(want) || (want.length > 3 && (h.includes(want) || (want.startsWith(h) && h.length > 2)))) { if (k === nth) return x; k++; } } return null; };
  return (ref) => {
    if (typeof ref === 'number') return ref;
    let off = 0; const m = /([+-]\d+(\.\d+)?)$/.exec(ref); if (m) { off = +m[1]; ref = ref.slice(0, m.index); }
    if (ref.startsWith('mark:')) { const [k, i] = ref.slice(5).split('#'); return cues.marks[k][+(i || 0)] + off; }
    const endish = ref.endsWith('>'); if (endish) ref = ref.slice(0, -1);
    const [id, w] = ref.split('.'); const l = L[id]; if (!l) throw new Error('no line ' + id);
    if (!w) return (endish ? l.end : l.start) + off;
    const [ww, nth] = w.split('#'); const x = word(l, ww, +(nth || 0));
    if (!x) { console.warn('no word', ref); return (endish ? l.end : l.start) + off; }
    return (endish ? x[2] : x[1]) + off;
  };
}

export function buildShots(cues, duration) {
  const T = resolver(cues); const list = []; let t = 0;
  const C = (x = 0, y = 0, z = 0, pan = 0, tilt = 0, mm = 35) => ({ x, y, z, pan, tilt, mm });
  const look = (px, py, mm = 35, x = 0, y = 0, z = 0) => ({ x, y, z, pan: -Math.atan((px - 640) / F0), tilt: -Math.atan((py - 360) / F0), mm });
  // aim the camera (at x,y,z) at a design point (px,py) on a plane at depth D: correct for near planes when the camera has moved
  const lookAt = (px, py, D, mm = 35, x = 0, y = 0, z = 0) => { const wx = (px - 640) * D / F0, wy = -(py - 360) * D / F0, dz = D + z; return { x, y, z, pan: -Math.atan((wx - x) / dz), tilt: Math.atan((wy - y) / Math.hypot(dz, wx - x)), mm }; };
  // a cut lands 0.15 s before the first word of a line, never inside the line before it
  const cut = (id) => { const l = cues.lines.find((x) => x.id === id); const i = cues.lines.indexOf(l); const prev = i > 0 ? cues.lines[i - 1].end + 0.05 : 0; return Math.max(prev, l.start - 0.15); };
  const S = (id, set, t1, o = {}) => { const sh = { id, set, t0: t, t1: t1 ?? duration, cam: [[0, C()]], breath: 0.3, ...o }; sh.dur = sh.t1 - sh.t0; t = sh.t1; list.push(sh); return sh; };
  const tt = (a) => T(a); const title = cues.marks.title; const endAt = cues.marks.end[0];

  // ===== SCENE 1: THE STUDY (cold open). A quiet room, one lamp, an open mushaf: the place where a juz is read tonight.
  S('s01', 'study', title[0], { mode: 'room', cam: [[0, look(640, 380, 28, 0, 0.2, 0)], [title[0] + 0.3, look(700, 420, 34, 0, 0, -0.9)]], breath: 0.25 });
  // ===== SCENE 2: TITLE over the night sky: one lantern rises (the series motif). Cut: the title is a new place, the sky.
  S('s02', 'sky', cut('w1'), { mode: 'title', rise: [title[0], cut('w1') + 1], card: { at: title[0] + 0.15, until: cut('w1'), line1: "Tonight's Juz", line2: 'JUZ THIRTY · JUZ AMMA', ar: cues.arabic.amma, y: 330 },
    cam: [[0, look(640, 420, 30)], [cut('w1') - title[0], look(640, 380, 31)]], breath: 0.2 });
  // ===== SCENE 3: THIRTY PARTS. The path of thirty lanterns: the Qur'an in thirty parts, one each night.
  // 3a wide: the whole path up the hill, every lantern dark; the thirty arches draw above it as "thirty parts" is said.
  const litStart = tt('w2.Many'), litEnd = tt('w2>') - 0.3; const lastOn = tt('w3.last');
  const lampTimes = Array.from({ length: 30 }, (_, i) => i < 29 ? litStart + (litEnd - litStart) * (i / 28) : lastOn);
  S('s03', 'path', cut('w2'), { mode: 'wide', lamps: lampTimes, cam: [[0, look(640, 340, 26, 0, 0.4, 0)], [cut('w2') - cut('w1'), look(640, 330, 28, 0, 0.4, -1.5)]],
    gfx: [{ type: 'arches', n: 30, at: tt('w1.thirty'), out: cut('w2') + 99, lit: lampTimes, y: 92 }, { type: 'label', text: 'THIRTY PARTS', sub: 'each part is called a juz', at: tt('w1.juz') - 0.3, out: cut('w2') + 0.2, y: 150 }] });
  // 3b: change of scale: closer, the camera climbs with the lanterns as they light one night at a time; the last one lights on "the last one".
  S('s04', 'path', tt('w3.People') - 0.1, { mode: 'climb', lamps: lampTimes, cam: [[0, look(560, 520, 34, 0, 0, -6)], [tt('w3.People') - cut('w2'), look(720, 210, 36, 0, 0.6, -10)]],
    gfx: [{ type: 'arches', n: 30, at: 0, out: 9999, lit: lampTimes, y: 92 }, { type: 'label', text: 'JUZ THIRTY', sub: 'the last part', at: lastOn + 0.1, out: 9999, y: 150 }] });
  // ===== SCENE 4: THE NAME. Cut on "People call it": we leave the hill for the page where the first word is written.
  S('s05', 'page', cut('w4'), { mode: 'amma', cam: [[0, look(640, 330, 40)], [cut('w4') - tt('w3.People') + 0.1, look(640, 340, 44)]],
    gfx: [{ type: 'arabic', key: 'amma', at: tt('w3.Amma') - 0.2, dur: 1.4, x: 640, y: 300, size: 150, glow: 0.5 }, { type: 'label', text: 'JUZ AMMA', sub: 'named for its first word', at: tt('w3.Amma') + 0.6, out: 9999, y: 520, small: true }] });
  // new information (how many surahs): the page pulls back and thirty-seven rosettes fill as the number counts up
  S('s06', 'page', cut('e1'), { mode: 'grid', cam: [[0, look(640, 360, 32)], [cut('e1') - cut('w4'), look(640, 360, 34)]],
    gfx: [{ type: 'grid37', at: tt('w4.holds'), settle: tt('w4.surahs') + 0.4, out: 9999 }, { type: 'count', to: 37, at: tt('w4.holds'), settle: tt('w4.surahs') + 0.4, x: 640, y: 150, label: 'SURAHS', out: 9999 }] });
  // ===== SCENE 5: THREE TREASURES. Back in the study, a niche with three lanterns; they light as the narration names three.
  S('s07', 'study', cut('t1a'), { mode: 'niche', niche: [tt('e1.three') - 0.1, tt('e1.three') + 0.5, tt('e1.treasures') + 0.2], cam: [[0, look(310, 320, 40, 0, 0, -1.2)], [cut('t1a') - cut('e1'), look(310, 315, 46, 0, 0, -2.0)]] });
  // ===== SCENE 6: AL-ALAQ. The page: the first treasure's name in its gold band.
  S('s08', 'page', cut('t1b'), { mode: 'band', cam: [[0, look(640, 330, 40)], [cut('t1b') - cut('t1a'), look(640, 320, 43)]],
    gfx: [{ type: 'cartouche', key: 'alaq', num: 'THE FIRST TREASURE', name: 'SURAH AL-ALAQ', at: tt('t1a.Surah') - 0.3, out: 9999, y: 330 }] });
  // the place it came down: Jabal an-Nur at night, the cave a small light near the summit (no figure)
  S('s09', 'mountain', cut('t1c'), { mode: 'far', caveOn: tt('t1b.first'), cam: [[0, look(640, 360, 30)], [cut('t1c') - cut('t1b'), look(660, 330, 36, 0, 0, -2)]],
    gfx: [{ type: 'label', text: 'JABAL AN-NUR', sub: 'the cave of Hira', at: tt('t1b.cave') - 0.6, out: cut('t1c') + 0.3, y: 96 }] });
  // the words themselves: 96:1 written in gold, its meaning under it; then "the end and the beginning" brackets
  S('s10', 'page', cut('t2a'), { mode: 'verse', noCap: ['t1c'], cam: [[0, look(640, 320, 38)], [cut('t2a') - cut('t1c'), look(640, 330, 42)]],
    gfx: [{ type: 'arabic', key: '96:1', at: tt('t1c') - 0.1, dur: 2.6, x: 640, y: 290, size: 70, glow: 0.35, meaning: 'Read, in the name of your Lord, who created.', meaningAt: tt('t1c') + 0.4, ref: 'AL-ALAQ 96:1' },
      { type: 'bracket', left: 'THE LAST PART', right: 'THE FIRST WORDS', at: tt('t1d.last'), out: 9999, y: 505 }] });
  // ===== SCENE 7: AL-QADR. The bright, still night over sleeping roofs.
  S('s11', 'night', cut('t2c'), { mode: 'wide', noCap: ['t2b'], cam: [[0, look(640, 420, 28, 0, 0.3, 0)], [cut('t2c') - cut('t2a'), look(640, 380, 30, 0, 0.3, -1)]],
    gfx: [{ type: 'cartouche', key: 'qadr', num: 'THE SECOND TREASURE', name: 'SURAH AL-QADR', at: tt('t2a.Surah') - 0.3, out: tt('t2b') - 0.4, y: 230 },
      { type: 'arabic', key: '97:1', at: tt('t2b.We') - 0.2, dur: 2.2, x: 640, y: 200, size: 60, glow: 0.35, meaning: 'We sent it down on the Night of Decree.', meaningAt: tt('t2b.We') + 0.3, ref: 'AL-QADR 97:1' }] });
  // closer: the verse about a thousand months, then the count that turns it into a lifetime
  S('s12', 'night', cut('t2e'), { mode: 'close', noCap: ['t2c'], cam: [[0, look(620, 300, 36, 0, 0.6, -2)], [cut('t2e') - cut('t2c'), look(620, 290, 39, 0, 0.6, -3)]],
    gfx: [{ type: 'arabic', key: '97:3', at: tt('t2c') - 0.1, dur: 2.2, x: 640, y: 200, size: 60, glow: 0.35, meaning: 'The Night of Decree is better than a thousand months.', meaningAt: tt('t2c') + 0.3, out: tt('t2d') - 0.2, ref: 'AL-QADR 97:3' },
      { type: 'count', to: 1000, from: 0, at: tt('t2d.thousand') - 0.4, settle: tt('t2d.months') + 0.3, x: 640, y: 210, label: 'MONTHS', commas: true, out: 9999, then: { text: '= MORE THAN 83 YEARS', at: tt('t2d.eighty') - 0.1 } }] });
  // new information (when the night is): the last ten nights as ten lanterns on a rope over the roofs, the odd nights brighter
  S('s13', 'night', cut('t3a'), { mode: 'ten', tenOn: tt('t2e.ten') - 0.2, oddOn: tt('t2e.odd') - 0.1, cam: [[0, look(640, 300, 32, 0, 0.5, -1)], [cut('t3a') - cut('t2e'), look(640, 300, 34, 0, 0.5, -2)]],
    gfx: [{ type: 'label', text: 'THE LAST TEN NIGHTS', sub: 'seek it on the odd nights', at: tt('t2e.last') - 0.2, out: 9999, y: 96 }] });
  // ===== SCENE 8: AL-IKHLAS. Back to the page: four short verses landing one by one.
  const ik = cues.lines.find((l) => l.id === 't3b');
  S('s14', 'page', cut('t3c'), { mode: 'ikhlas', noCap: ['t3b'], cam: [[0, look(640, 360, 38)], [cut('t3c') - cut('t3a'), look(640, 360, 41)]],
    gfx: [{ type: 'cartouche', key: 'ikhlas', num: 'THE THIRD TREASURE', name: 'SURAH AL-IKHLAS', at: tt('t3a.Surah') - 0.3, out: tt('t3b') - 0.3, y: 330 },
      { type: 'ikhlas', out: 9999, lines: [{ key: '112:1', at: tt('t3b.Say') - 0.2, meaning: 'Say: He is Allah, the One.' }, { key: '112:2', at: tt('t3b.Allah#1') - 0.2, meaning: 'Allah, the One everyone turns to.' },
        { key: '112:3', at: tt('t3b.He#1') - 0.2, meaning: 'He has no child, and He was not born.' }, { key: '112:4', at: tt('t3b.And#1') - 0.2, meaning: 'And there is nothing like Him.' }] }] });
  // the page pulls back: one third of a circle fills with gold as the hadith is told
  S('s15', 'page', cut('m1'), { mode: 'third', cam: [[0, look(640, 360, 33)], [cut('m1') - cut('t3c'), look(640, 360, 31)]],
    gfx: [{ type: 'label', text: 'SURAH AL-IKHLAS', sub: 'four short verses', at: cut('t3c') + 0.2, out: 9999, y: 96 }, { type: 'third', at: tt('t3c.equal') - 0.2, settle: tt('t3c.third') + 0.6, out: 9999, x: 640, y: 300, r: 120, label: "ONE THIRD OF THE QUR'AN" }] });
  // ===== SCENE 9: BEFORE SLEEP. A child's room at night, nobody in it: the lamp is low, the blanket folded.
  S('s16', 'bedroom', cut('m3'), { mode: 'wide', cam: [[0, look(640, 380, 28, 0, 0, 0)], [cut('m3') - cut('m1'), look(660, 390, 31, 0, 0, -0.8)]],
    gfx: [{ type: 'pair', a: { key: 'falaq', name: 'AL-FALAQ', at: tt('m1.Falaq') - 0.3 }, b: { key: 'nas', name: 'AN-NAS', at: tt('m1.Nas') - 0.2 }, out: tt('m2') - 0.1, y: 210, xa: 600, xb: 960 },
      { type: 'label', text: 'EVERY NIGHT BEFORE SLEEP', sub: 'al-Ikhlas, al-Falaq and an-Nas', at: tt('m2.Every') + 0.3, out: cut('m3') + 0.3, y: 96 }] });
  // closer, to the lamp turned low by the bed: "you can do the same"
  S('s17', 'bedroom', cut('l1'), { mode: 'close', dim: [tt('m3'), tt('m3>') + 1.5], cam: [[0, lookAt(960, 490, 8, 36, 0, 0, -2.0)], [cut('l1') - cut('m3'), lookAt(950, 492, 8, 39, 0, 0, -2.4)]] });
  // ===== SCENE 10: THE FULL SKY. Thirty lanterns over the hills; the lamp; dawn.
  S('s18', 'sky', cut('l2'), { mode: 'full', fillFrom: cut('l1'), cam: [[0, look(640, 470, 26)], [cut('l2') - cut('l1'), look(640, 340, 28)]], breath: 0.2 });
  // the lamp that must not go out: a close, steady flame (the study's lamp)
  S('s19', 'study', cut('l3'), { mode: 'lamp', cam: [[0, lookAt(945, 585, 6, 50, 0, 0, -2.4)], [cut('l3') - cut('l2'), lookAt(945, 582, 6, 54, 0, 0, -2.5)]], breath: 0.1 });
  // time passes (dissolve): dawn comes up over the hills, the lanterns fade into morning; end card
  S('s20', 'sky', null, { mode: 'dawn', dawn: [cut('l3'), endAt + 1.5], dissolve: 1.4, card: { at: endAt, until: duration, line1: 'Thirty Nights of Light', y: 190, out: 0.9 },
    cam: [[0, look(640, 380, 28)], [duration - cut('l3'), look(640, 400, 29)]], breath: 0.15 });
  return list;
}

// captions: the DISPLAY text of each line (cues text), split at sentence ends; times from the spoken word timings (mapped by word position)
export function buildCaptions(cues) {
  const caps = [];
  for (const l of cues.lines) {
    const disp = l.text.split(' '); const ws = l.words; if (!ws || !ws.length) { caps.push({ text: l.text, in: l.start, out: l.end + 0.5, id: l.id }); continue; }
    const at = (i) => ws[clamp(Math.round(i * ws.length / disp.length), 0, ws.length - 1)];
    let a = 0;
    for (let i = 0; i < disp.length; i++) {
      const w = disp[i]; const end = /[.?!:]$/.test(w) || (/,$/.test(w) && i - a >= 7) || i === disp.length - 1 || i - a >= 14;
      if (end) { const s = at(a), e = at(i + 1 >= disp.length ? disp.length - 1 : i); caps.push({ text: disp.slice(a, i + 1).join(' '), in: Math.max(0, s[1] - 0.08), out: (i === disp.length - 1 ? ws[ws.length - 1][2] : e[2]) + 0.5, id: l.id }); a = i + 1; }
    }
  }
  caps.sort((x, y) => x.in - y.in); for (let i = 0; i < caps.length - 1; i++) caps[i].out = Math.min(caps[i].out, caps[i + 1].in + 0.05);
  return caps;
}
