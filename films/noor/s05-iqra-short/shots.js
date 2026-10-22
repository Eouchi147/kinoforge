// The short's shot plan (9:16): three pieces of the film, each one place. Times come from cues.json (made by make_short.py).
// Lenses are short (18 to 26 mm) because the sets were painted for a 16:9 frame: at 20 mm one design px is one screen px.
export const FONT = {};
export function buildShots(cues, duration) {
  const L = Object.fromEntries(cues.lines.map((l) => [l.id, l])); const G = Object.fromEntries(cues.segments.map((s) => [s.name, s]));
  const wd = (id, w, n = 0) => { const k = w.toLowerCase().replace(/[^a-z0-9]/g, ''); const ws = L[id].words.filter((x) => x[0].toLowerCase().replace(/[^a-z0-9]/g, '').startsWith(k)); return (ws[Math.min(n, ws.length - 1)] || L[id].words[0])[1]; };
  const look = (px, py, mm = 22) => ({ x: 0, y: 0, z: 0, pan: -Math.atan((px - 640) / 1050), tilt: -Math.atan((py - 360) / 1050), mm });
  const list = []; let t = 0;
  const S = (id, set, t1, o = {}) => { const sh = { id, set, t0: t, t1: t1 ?? duration, cam: [[0, look(640, 360)]], breath: 0.3, ...o }; sh.dur = sh.t1 - sh.t0; t = sh.t1; list.push(sh); return sh; };
  // 1. the hook and the word: the sky fills with gold light, the word writes itself
  S('w', 'sky', G.word.t1, { mode: 'word', word: { ar: 'iqra', at: wd('e3', 'Iqra') - 0.2, dur: 1.4, en: 'READ', enAt: wd('e3', 'Read') }, hook: cues.marks.hook, cam: [[0, look(640, 250, 20)], [G.word.t1, look(640, 240, 22)]] });
  // 2. the first words: the illuminated panel, verse by verse (a dissolve hides the join in the sound)
  S('v', 'sky', G.verses.t1, { mode: 'verse', card: 'verse', dissolve: 0.5, cam: [[0, look(640, 300, 20)], [G.verses.t1 - G.verses.t0, look(640, 290, 21)]], breath: 0.15 });
  // 3. what it means: the mountain at night, the word stays with us, then the series tag
  S('m', 'mountain', null, { mode: 'night', lamp: 0.7, card: 'read', dissolve: 0.5, endAt: L.m2.end + 0.2, cam: [[0, look(800, 330, 20)], [duration - G.meaning.t0, look(810, 310, 22)]] });
  return list;
}
export function buildCaptions(cues) {
  const caps = [];
  for (const l of cues.lines) {
    if (/^v\d/.test(l.id)) continue;
    const ws = l.words; const disp = l.text.split(/\s+/); let a = 0; const timeOf = (k) => ws[Math.min(ws.length - 1, Math.round(k * (ws.length - 1) / Math.max(1, disp.length - 1)))];
    for (let i = 0; i < disp.length; i++) { const w = disp[i]; const end = /[.?!:]$/.test(w) || (/,$/.test(w) && i - a >= 4) || i === disp.length - 1 || i - a >= 8;
      if (end) { const s0 = timeOf(a), s1 = timeOf(i); caps.push({ text: disp.slice(a, i + 1).join(' '), in: Math.max(0, s0[1] - 0.1), out: s1[2] + 0.4 }); a = i + 1; } }
  }
  caps.sort((x, y) => x.in - y.in); for (let i = 0; i < caps.length - 1; i++) caps[i].out = Math.min(caps[i].out, caps[i + 1].in + 0.05);
  return caps;
}
export function buildLabels() { return []; }
