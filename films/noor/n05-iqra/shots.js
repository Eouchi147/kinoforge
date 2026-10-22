// The shot plan against cues.json (times come from the narration, never typed in). 9 scenes, 20 shots.
// Camera keys: [localTime, {x,y,z,pan,tilt,mm}, ease]; look(px, py, mm) aims the camera at a design-px point of the reference frame.
// Every cut has a reason (new place, new information, change of scale, time passing); see NOTES.md.
export const FONT = { cap: 'italic 400 30px "Cormorant Garamond"', label: '500 26px "Cinzel"', sub: 'italic 400 24px "Cormorant Garamond"', ar: '"Amiri Quran"' };

export function buildShots(cues, duration) {
  const L = Object.fromEntries(cues.lines.map((l) => [l.id, l]));
  const st = (id) => L[id].start, en = (id) => L[id].end;
  const wd = (id, w, n = 0, edge = 0) => { const key = w.toLowerCase().replace(/[^a-z0-9]/g, ''); const ws = L[id].words.filter((x) => x[0].toLowerCase().replace(/[^a-z0-9]/g, '').startsWith(key)); const x = ws[Math.min(n, ws.length - 1)]; if (!x) throw new Error(`no word ${w} in ${id}`); return x[1 + edge]; };
  const look = (px, py, mm = 35, x = 0, y = 0, z = 0) => ({ x, y, z, pan: -Math.atan((px - 640) / 1050), tilt: -Math.atan((py - 360) / 1050), mm });
  const list = []; let t = 0;
  const S = (id, set, t1, o = {}) => { const sh = { id, set, t0: t, t1: t1 ?? duration, cam: [[0, look(640, 360)]], breath: 0.35, ...o }; sh.dur = sh.t1 - sh.t0; t = sh.t1; list.push(sh); return sh; };
  const cut = (id) => st(id) - 0.12;               // cut a breath before the first word of a line
  const T = cues.marks.title, E = cues.marks.end;

  // SCENE 1, cold open: a dark mountain under the stars; one tiny lamp burns high in the rock. Quiet.
  S('o1', 'mountain', T[0] - 0.2, { mode: 'night', dark: 0.62, lamp: 0.9, cityA: 0.5, cam: [[0, { ...look(760, 330, 30), z: 0 }], [T[0], { ...look(800, 300, 38), z: -40 }]], breath: 0.2 });
  // the title: a lantern rises into the night sky; the series and the night arrive with it
  S('title', 'sky', cut('w1'), { mode: 'title', rise: [0.2, T[1] - T[0] + 1.0], card: 'title', cam: [[0, look(640, 380, 32)], [T[1] - T[0] + 1.2, look(640, 330, 34)]], breath: 0.2 });
  // SCENE 2, where: the mountain at dusk, then inside the cave, then the names
  S('a1', 'mountain', cut('w2'), { mode: 'dusk', cam: [[0, look(720, 400, 30)], [en('w1') - cut('w1') + 1.5, look(760, 380, 33)]] });
  S('a2', 'cave', cut('w3'), { mode: 'dusk', cam: [[0, look(640, 380, 30)], [en('w2') - cut('w2') + 1, look(640, 370, 33)]] });
  S('a3', 'mountain', cut('w4'), { mode: 'dusk', cam: [[0, look(800, 330, 55)], [en('w3') - cut('w3') + 1.4, look(830, 290, 66)]],
    labels: [{ text: 'JABAL AN-NUR', sub: 'the Mountain of Light', in: wd('w3', 'Jabal'), out: wd('w3', 'cave') - 0.2, x: 250, y: 120 },
             { text: 'HIRA', sub: 'the cave', in: wd('w3', 'Hira'), out: cut('w4') + 0.1, at: ['peak', 846, 250], x: 480, y: 150 }] });
  // SCENE 3, the valley below: loud life, statues around the Kaaba
  S('b1', 'valley', cut('w6'), { mode: 'dusk', cam: [[0, look(860, 400, 32)], [cut('w6') - cut('w4'), look(560, 410, 36)]], breath: 0.4 });
  // SCENE 4, one man climbs: we only see his lantern on the path
  S('c1', 'mountain', cut('w8'), { mode: 'night', walk: { u0: 0.0, u1: 0.5, at: 0.4, dur: cut('w8') - cut('w6') - 0.4 }, cam: [[0, look(560, 540, 46)], [cut('w8') - cut('w6'), look(680, 450, 50)]] });
  S('c2', 'mountain', cut('w9'), { mode: 'night', walk: { u0: 0.5, u1: 1.0, at: 0, dur: cut('w9') - cut('w8') - 0.8 }, cam: [[0, look(740, 400, 64)], [cut('w9') - cut('w8'), look(810, 300, 74)]],
    labels: [{ text: 'AL-AMIN', sub: 'the one you can trust', in: wd('w8', 'called') - 0.1, out: en('w8') + 0.6, x: 250, y: 120 }] });
  S('d1', 'cave', cut('e1'), { mode: 'night', lamp: 1, cam: [[0, look(560, 470, 34)], [cut('e1') - cut('w9'), look(600, 480, 40)]] });
  // SCENE 5, the night: light fills the cave and the sky. No figure is ever shown.
  S('e1', 'cave', cut('e2'), { mode: 'light', lamp: 1, lightAt: wd('e1', 'alone') - cut('e1') - 0.6, lightLen: 3.5, cam: [[0, look(640, 360, 36)], [cut('e2') - cut('e1'), look(650, 330, 46)]] });
  S('e2', 'mountain', cut('e3'), { mode: 'light', lightAt: 0, lightLen: 1.2, lamp: 1, cityA: 0.6, cam: [[0, look(800, 380, 34)], [cut('e3') - cut('e2'), look(810, 360, 38)]] });
  S('e3', 'sky', cut('e4'), { mode: 'word', word: { ar: 'iqra', at: wd('e3', 'Iqra') - 0.2, dur: 1.4, en: 'READ', enAt: wd('e3', 'Read') }, cam: [[0, look(640, 360, 36)], [cut('e4') - cut('e3'), look(640, 350, 40)]], breath: 0.2 });
  S('e4', 'cave', cut('e6'), { mode: 'pulses', lamp: 1, pulses: [wd('e4', 'answered'), wd('e5', 'Read')], cam: [[0, look(640, 330, 46)], [cut('e6') - cut('e4'), look(640, 340, 54)]] });
  // change of scale: down to the mat and the lamp, the place where he sits, as the third ask comes
  S('e6', 'cave', cut('e7'), { mode: 'pulses', lamp: 1, pulses: [wd('e6', 'Three'), wd('e6', 'Three', 1)], cam: [[0, look(600, 560, 58)], [cut('e7') - cut('e6'), look(620, 540, 64)]] });
  // SCENE 6, the first words: an illuminated panel fills, verse by verse
  S('v', 'sky', cut('m1'), { mode: 'verse', verse: true, card: 'verse', cam: [[0, look(640, 380, 34)], [cut('m1') - cut('e7'), look(640, 360, 37)]], breath: 0.15 });
  // SCENE 7, what it means; the lantern hurries home; the doorway
  S('f1', 'mountain', cut('m3'), { mode: 'night', lamp: 0.7, card: 'read', cam: [[0, look(740, 360, 30)], [cut('m3') - cut('m1'), look(760, 350, 33)]] });
  S('f2', 'mountain', cut('m4'), { mode: 'night', walk: { u0: 1.0, u1: 0.0, at: 0.3, dur: cut('m4') - cut('m3') - 0.3 }, cam: [[0, look(780, 330, 50)], [cut('m4') - cut('m3'), look(560, 560, 44)]] });
  S('f3', 'house', cut('m5'), { mode: 'night', cam: [[0, look(640, 380, 32)], [cut('m5') - cut('m4'), look(640, 400, 37)]] });
  // SCENE 8, time passing: the stars wheel over the mountain and dawn comes up (a dissolve: time)
  S('f4', 'mountain', cut('l1'), { mode: 'dawn', dissolve: 1.2, dawnAt: 2.0, dawnLen: Math.max(4, cut('l1') - cut('m5') - 3), cam: [[0, look(700, 360, 28)], [cut('l1') - cut('m5'), look(720, 340, 30)]] });
  // SCENE 9, the lantern sky: tonight's one lantern rises with the word; the end card
  S('l', 'sky', null, { mode: 'lantern', dissolve: 1.0, rise: [wd('l1', 'lantern') - cut('l1') - 0.3, 9], word: { ar: 'iqra', at: wd('l1', 'word') - cut('l1') + 0.2 }, endAt: E[0], card: 'end',
    cam: [[0, look(640, 420, 30)], [duration - cut('l1'), look(640, 360, 33)]], breath: 0.2 });
  for (const s of list) { s.t0abs = s.t0; }
  return list;
}

// captions: one narration sentence (or a long clause) at a time; none during the verse panel (it carries the meaning itself)
export function buildCaptions(cues) {
  const caps = [];
  for (const l of cues.lines) {
    if (/^v\d/.test(l.id)) continue;
    const ws = l.words; const disp = l.text.split(/\s+/); let a = 0;
    // display words follow the display text (the voice read a spelled-out form for some names); timing from the spoken words
    const n = Math.min(ws.length, disp.length); const timeOf = (k) => ws[Math.min(ws.length - 1, Math.round(k * (ws.length - 1) / Math.max(1, disp.length - 1)))];
    for (let i = 0; i < disp.length; i++) {
      const w = disp[i]; const end = /[.?!:]$/.test(w) || (/,$/.test(w) && i - a >= 6) || i === disp.length - 1 || i - a >= 14;
      if (end) { const s0 = timeOf(a), s1 = timeOf(i); caps.push({ text: disp.slice(a, i + 1).join(' '), in: Math.max(0, s0[1] - 0.1), out: s1[2] + 0.5 }); a = i + 1; }
    }
    void n;
  }
  caps.sort((x, y) => x.in - y.in); for (let i = 0; i < caps.length - 1; i++) caps[i].out = Math.min(caps[i].out, caps[i + 1].in + 0.05);
  return caps;
}
export function buildLabels() { return []; }
