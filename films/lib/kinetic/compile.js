// Kinetic engine: compile a spec (list of cards on the cue timeline) into timed, drawable cards. Throws on anything that would
// silently drift from the audio (unknown cue line or word, unknown card type), and on em / en dashes or "..." in any text.
import { rgba } from './lib.js';
import { bgName } from './textures.js';
import { CARDS, DEFAULT_BG } from './cards/index.js';

const BAD = /[\u2014\u2013]|\.\.\.|\u2026/;
function scan(v, path) {
  if (typeof v === 'string') { if (BAD.test(v)) throw new Error(`${path}: no em dash, en dash or "..." allowed in text: ${JSON.stringify(v)}`); }
  else if (Array.isArray(v)) v.forEach((x, i) => scan(x, `${path}[${i}]`));
  else if (v && typeof v === 'object') for (const k of Object.keys(v)) scan(v[k], `${path}.${k}`);
}

export const THEMES = (accent) => ({
  dark: { dark: true, ink: '#efe6d2', accent, paper: '#0e0d0b' },
  paper: { dark: false, ink: '#14171a', accent, paper: '#eceeee' },
  parchment: { dark: false, parchment: true, ink: '#1a1612', accent, paper: '#f2e9d6' },
});

export function compile(E, spec, clock) {
  const duration = clock.duration, warnings = [], accent = spec.accent || '#cf3b2e';
  const themes = THEMES(accent), look = spec.look || {};
  const snapOn = look.snap !== false, snapD = typeof look.snap === 'number' ? look.snap : 0.12;
  const raw = spec.cards || []; if (!raw.length) throw new Error('spec.cards is empty');
  scan(spec.cards, 'cards'); scan([spec.title, spec.series], 'spec');

  // ---- start of a card
  const lineLead = (id) => {
    const L = clock.lines[id], first = Math.min(L.start, L.words[0][1]);
    let prevEnd = 0; for (const o of clock.cues.lines) if (o.end <= first + 1e-6 && o.end > prevEnd) prevEnd = o.end;
    return Math.max(first - 0.12, (prevEnd + first) / 2, 0);
  };
  const startOf = (ref, where) => {
    if (typeof ref === 'string' && /^[A-Za-z_]\w*$/.test(ref) && clock.lines[ref]) return lineLead(ref);
    try { return clock.at(ref); } catch (e) { throw new Error(`${where}: ${e.message}`); }
  };
  let cards = raw.map((c, i) => {
    const where = `card ${i} (${c.type})`;
    if (!CARDS[c.type]) throw new Error(`${where}: unknown card type "${c.type}". Types: ${Object.keys(CARDS).join(', ')}`);
    let t0;
    if (c.at != null) t0 = startOf(c.at, where);
    else if (c.line) t0 = startOf(c.line, where);
    else if (c.type === 'end') t0 = duration - (clock.cues.end_card_s ?? 2.6);
    else throw new Error(`${where}: needs "at" (a time reference) or "line"`);
    return { raw: c, i, where, type: c.type, t0, over: !!c.over };
  });
  const base = cards.filter((c) => !c.over).sort((a, b) => a.t0 - b.t0 || a.i - b.i);
  const overs = cards.filter((c) => c.over);
  // ---- end of a card and build
  const out = [];
  const build = (k, t1) => {
    const c = k.raw; k.t1 = t1;
    if (!(k.t1 > k.t0)) throw new Error(`${k.where}: ends (${k.t1.toFixed(2)}) before it starts (${k.t0.toFixed(2)})`);
    const bg = k.over ? (c.bg ? bgName(c.bg) : null) : bgName(c.bg || DEFAULT_BG[c.type] || 'dark');
    let th = themes[bg || 'dark'];
    if (k.over && !bg) { const under = base.find((b) => k.t0 >= b.t0 && k.t0 < b.t1); th = themes[under ? under.bg : 'dark']; }
    k.bg = bg; k.theme = th;
    const ctx = { E, clock, spec, card: c, t0: k.t0, t1: k.t1, theme: th, from: c.from != null ? startOf(c.from, k.where) : k.t0,
      at: (r) => { try { return clock.at(r); } catch (e) { throw new Error(`${k.where}: ${e.message}`); } },
      snap: (t) => (snapOn ? clock.snap(t, snapD) : t), warn: (m) => warnings.push(`${k.where}: ${m}`) };
    let r; try { r = CARDS[c.type](E, c, ctx); } catch (e) { if (/^card \d/.test(e.message)) throw e; throw new Error(`${k.where}: ${e.message}`); }
    k.draw = r.draw; k.hits = r.hits || []; k.lastT = r.lastT ?? k.t0;
    if (c.hold != null && c.until == null) k.t1 = Math.min(k.t1, k.lastT + c.hold);
    k.exit = c.exit || 'cut'; k.exitDur = c.exitDur ?? 0.3; k.enter = c.enter || 'cut'; k.enterDur = c.enterDur ?? 0.3;
    k.name = c.name || `${k.type} ${c.at ?? c.line ?? ''}`;
    out.push(k);
  };
  base.forEach((k, j) => { const nxt = base[j + 1]; k.bg = bgName(k.raw.bg || DEFAULT_BG[k.type] || 'dark'); k.t1 = k.raw.until != null ? clock.at(k.raw.until) : (nxt ? nxt.t0 : duration); });
  base.forEach((k) => build(k, k.t1));
  for (const k of overs) {
    const c = k.raw, under = base.find((b) => k.t0 >= b.t0 && k.t0 < b.t1);
    const t1 = c.until != null ? clock.at(c.until) : c.dur != null ? k.t0 + c.dur : (under ? under.t1 : duration);
    build(k, t1);
  }
  out.sort((a, b) => a.t0 - b.t0 || (a.over ? 1 : 0) - (b.over ? 1 : 0));
  // ---- style checks (warnings, not errors)
  const acc = raw.filter((c) => c.accent).length; if (acc > (spec.accentMax ?? 1)) warnings.push(`accent colour used on ${acc} cards (house style: once)`);
  for (let i = 0; i < out.length; i++) { const k = out[i]; if (k.over) continue; if (k.t1 - k.t0 < 0.5) warnings.push(`${k.where}: only ${(k.t1 - k.t0).toFixed(2)} s long`); }
  const gaps = out.filter((k) => !k.over); let tt = 0;
  for (const k of gaps) { if (k.t0 > tt + 1.0) warnings.push(`blank dark gap ${tt.toFixed(1)} to ${k.t0.toFixed(1)} s (add a card or use until/hold deliberately)`); tt = Math.max(tt, k.t1); }
  if (tt < duration - 1.0) warnings.push(`nothing on screen after ${tt.toFixed(1)} s (film is ${duration.toFixed(1)} s)`);
  return { cards: out, warnings, bgs: [...new Set(out.map((k) => k.bg).filter(Boolean).concat(['dark']))] };
}
