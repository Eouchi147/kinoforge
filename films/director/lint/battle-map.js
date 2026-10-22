// Static checks of a Battle Map spec against its cues, run in the page by films/director/check.cjs (no rendering).
// lint(spec, cues) -> { errors: [...], warnings: [...] }. Errors are things the engine would throw on (now or at some frame)
// or that break the house rules; each message names the path in the spec so the coder seat can fix it.
import { Clock } from '/films/lib/battlemap/timeline.js';
import { ICON_NAMES } from '/films/lib/battlemap/icons.js';
import { TEAMS, KINDS } from '/films/lib/battlemap/blocks.js';

const TIME_KEYS = ['at', 'until', 'hide', 'fallAt'];
const MOVE_PROPS = ['x', 'z', 'heading', 'len', 'dep', 'bulge', 'scale', 'alpha', 'drop', 'lift', 'fade', 'sink', 'count', 'flag', 'glow'];
const LIGHT_PROPS = ['eve', 'haze', 'cloud', 'glint'];
const ARROW_COLORS = ['rome', 'carthage', 'ink', 'gold', 'cream', 'green', 'neutral'];
const EASES = ['linear', 'in', 'out', 'inOut', 'inQuad', 'outQuad', 'inOutQuad', 'smooth', 'outBack', 'inBack', 'outElastic', 'outBounce', 'step', 'spline'];
const FEATURES = ['undulate', 'hill', 'ridge', 'mountains', 'river', 'sea', 'lake', 'land', 'woods', 'farms', 'road', 'flat'];
const BAD_TEXT = /[—–]|\.\.\.|…/;

export function lint(spec, cues) {
  const errors = [], warnings = [];
  const E = (p, m) => errors.push(`${p}: ${m}`), W = (p, m) => warnings.push(`${p}: ${m}`);
  if (!spec || typeof spec !== 'object') return { errors: ['the module has no default export object'], warnings };
  const dur = cues.duration; const clock = new Clock(cues, spec.marks || {});
  const T = (p, ref) => { try { const t = clock.at(ref); if (!Number.isFinite(t)) { E(p, `time ${JSON.stringify(ref)} is not a number`); return null; }
    if (t < -0.01) E(p, `time ${JSON.stringify(ref)} = ${t.toFixed(2)} s is before the film starts`);
    else if (t > dur + 0.5 && /(^|\.)at$/.test(p)) W(p, `starts at ${t.toFixed(2)} s, after the film ends (${dur.toFixed(2)} s): never shown`); return t; }
    catch (e) { E(p, e.message); return null; } };
  for (const [k, v] of Object.entries(spec.marks || {})) T(`marks.${k}`, v);

  const stage = (sp, name) => {
    const P = (s) => (name === 'main' ? '' : `stages.${name}.`) + s;
    if (!sp.world) { E(P('world'), 'missing'); return; }
    if (!Array.isArray(sp.world.size) || sp.world.size.length !== 2) E(P('world.size'), 'must be [W, D]');
    (sp.world.features || []).forEach((f, i) => { if (!FEATURES.includes(f.type)) E(P(`world.features[${i}].type`), `unknown feature ${f.type} (known: ${FEATURES.join(' ')})`); });
    // blocks and the ids the engine makes for grids (id.i.j)
    const ids = new Set(), groups = new Set();
    for (const [id, b] of Object.entries(sp.blocks || {})) {
      groups.add(id);
      if (b.grid) { const c = b.grid.cols ?? 4, r = b.grid.ranks ?? 3; for (let j = 0; j < r; j++) for (let i = 0; i < c; i++) { ids.add(`${id}.${i}.${j}`); groups.add(`${id}.${i}.${j}`); } }
      else ids.add(id);
      if (b.team && !TEAMS[b.team]) E(P(`blocks.${id}.team`), `unknown team ${b.team} (known: ${Object.keys(TEAMS).join(' ')})`);
      if (b.kind && KINDS[b.kind] === undefined) E(P(`blocks.${id}.kind`), `unknown kind ${b.kind} (known: ${Object.keys(KINDS).join(' ')})`);
      for (const k of ['x', 'z']) if (b[k] !== undefined && !Number.isFinite(b[k])) E(P(`blocks.${id}.${k}`), 'must be a number');
    }
    const hasBlock = (n) => groups.has(n);
    const arrowIds = new Set((sp.arrows || []).map((a) => a.id).filter(Boolean));
    const span = (p, e, needEnd) => { const t0 = e.at !== undefined ? T(p + '.at', e.at) : null; let t1 = null;
      if (e.until !== undefined) t1 = T(p + '.until', e.until); else if (e.dur !== undefined) t1 = t0 + e.dur;
      if (t0 !== null && t1 !== null && t1 < t0 - 1e-6) W(p, `ends (${t1.toFixed(2)} s) before it starts (${t0.toFixed(2)} s): never shown`);
      if (needEnd && e.until === undefined && e.dur === undefined) W(p, 'no until or dur: it stays on screen to the end');
      for (const k of ['hide', 'fallAt']) if (e[k] !== undefined) T(`${p}.${k}`, e[k]);
      if (e.ease && !EASES.includes(e.ease)) E(p + '.ease', `unknown easing ${e.ease}`); return [t0, t1]; };
    (sp.moves || []).forEach((m, i) => { const p = P(`moves[${i}]`); span(p, m);
      const names = m.blocks ? (Array.isArray(m.blocks) ? m.blocks : [m.blocks]) : [m.block ?? m.group];
      for (const n of names) if (!hasBlock(n)) E(p, `unknown block or group ${n}`);
      for (const k of Object.keys(m.to || {})) if (!MOVE_PROPS.includes(k)) E(p + '.to', `unknown prop ${k} (known: ${MOVE_PROPS.join(' ')})`);
      for (const k of Object.keys(m.by || {})) if (!MOVE_PROPS.includes(k)) E(p + '.by', `unknown prop ${k}`);
      if (m.path && (!Array.isArray(m.path) || m.path.some((q) => !Array.isArray(q) || q.length < 2))) E(p + '.path', 'must be a list of [x, z]'); });
    (sp.arrows || []).forEach((a, i) => { const p = P(`arrows[${i}]`); span(p, a);
      if (!Array.isArray(a.path) || a.path.length < 2) E(p + '.path', 'needs at least two [x, z] points');
      const c = a.color || a.team; if (c && typeof c === 'string' && !ARROW_COLORS.includes(c)) W(p, `unknown colour ${c} (known: ${ARROW_COLORS.join(' ')})`); });
    const anchor = (p, it) => { if (it.block !== undefined && !hasBlock(it.block)) E(p + '.block', `unknown block ${it.block}`);
      if (it.follow !== undefined && !arrowIds.has(it.follow)) E(p + '.follow', `no arrow with id ${it.follow}`);
      if (it.block === undefined && it.follow === undefined && !it.pos && !it.screen) E(p, 'needs an anchor: pos, block, follow or screen');
      if (it.team && !TEAMS[it.team]) E(p + '.team', `unknown team ${it.team}`);
      if (it.screen && (it.screen[0] < 0.02 || it.screen[0] > 0.98 || it.screen[1] < 0.02 || it.screen[1] > 0.98)) W(p + '.screen', 'very close to the frame edge'); };
    (sp.labels || []).forEach((l, i) => { const p = P(`labels[${i}]`); span(p, l, true); anchor(p, l);
      if (typeof l.text !== 'string' || !l.text.trim()) E(p + '.text', 'missing'); else if (BAD_TEXT.test(l.text)) E(p + '.text', 'no em or en dashes and no "..." on screen'); });
    (sp.counters || []).forEach((c, i) => { const p = P(`counters[${i}]`); span(p, c, true); anchor(p, c); if (!Number.isFinite(c.to)) E(p + '.to', 'must be a number');
      if (c.suffix && BAD_TEXT.test(c.suffix)) E(p + '.suffix', 'no dashes or "..."'); });
    (sp.icons || []).forEach((c, i) => { const p = P(`icons[${i}]`); span(p, c, true); anchor(p, c);
      if (!ICON_NAMES.includes(c.icon)) E(p + '.icon', `unknown icon ${c.icon} (known: ${ICON_NAMES.join(' ')})`); });
    (sp.volleys || []).forEach((v, i) => { const p = P(`volleys[${i}]`); span(p, v);
      for (const k of ['from', 'to']) { const e = v[k]; if (!e) E(`${p}.${k}`, 'missing'); else if (e.block !== undefined && !hasBlock(e.block)) E(`${p}.${k}.block`, `unknown block ${e.block}`); } });
    (sp.light || []).forEach((l, i) => { const p = P(`light[${i}]`); span(p, l); for (const k of Object.keys(l.to || {})) if (!LIGHT_PROPS.includes(k)) E(p + '.to', `unknown light prop ${k} (known: ${LIGHT_PROPS.join(' ')})`); });
    const cam = sp.camera || []; if (!cam.length) E(P('camera'), 'needs at least one key');
    let prev = -1; cam.forEach((k, i) => { const p = P(`camera[${i}]`); const t = T(p + '.at', k.at);
      if (t !== null && t < prev - 1e-6) W(p, `keys must be in time order (${t.toFixed(2)} s comes after ${prev.toFixed(2)} s)`); if (t !== null) prev = t;
      if (k.target !== undefined && !Array.isArray(k.target)) E(p + '.target', 'must be [x, z]'); if (k.target === undefined && k.x === undefined) W(p, 'no target: looks at [0, 0]');
      if (k.pitch !== undefined && (k.pitch < 3 || k.pitch > 89.9)) E(p + '.pitch', 'must be between 3 and 89.9');
      if (k.ease && !EASES.includes(k.ease)) E(p + '.ease', `unknown easing ${k.ease}`); });
    if (cam.length && name === 'main') { const t0 = (() => { try { return clock.at(cam[0].at); } catch { return 0; } })(); if (t0 > 0.01) W(P('camera[0].at'), 'the first key should be at 0'); }
  };
  stage(spec, 'main');
  for (const [n, sp] of Object.entries(spec.stages || {})) stage(sp, n);
  (spec.insets || []).forEach((e, i) => { const p = `insets[${i}]`; if (!(spec.stages || {})[e.stage]) E(p + '.stage', `no stage ${e.stage}`);
    const t0 = e.at !== undefined ? T(p + '.at', e.at) : null; const t1 = e.until !== undefined ? T(p + '.until', e.until) : null; if (t0 !== null && t1 !== null && t1 < t0) W(p, 'ends before it starts: never shown'); });
  (spec.cards || []).forEach((c, i) => { const p = `cards[${i}]`; const t0 = T(p + '.at', c.at); if (c.until !== undefined) T(p + '.until', c.until);
    (c.lines || []).forEach((L, j) => { if (typeof L.text !== 'string') E(`${p}.lines[${j}].text`, 'missing'); else if (BAD_TEXT.test(L.text)) E(`${p}.lines[${j}].text`, 'no em or en dashes and no "..." on screen'); }); });
  (spec.msaaOn || []).forEach((r, i) => { if (!Array.isArray(r) || r.length !== 2) E(`msaaOn[${i}]`, 'must be [from, to]'); else { T(`msaaOn[${i}][0]`, r[0]); T(`msaaOn[${i}][1]`, r[1]); } });
  // the house: a title card around the title line, an end card over the outro
  const cards = (spec.cards || []).map((c) => { try { return [clock.at(c.at), c.until !== undefined ? clock.at(c.until) : clock.at(c.at) + (c.dur ?? 1), c]; } catch { return null; } }).filter(Boolean);
  const tl = cues.lines.find((l) => l.id === cues.title_line);
  if (tl && !cards.some(([a, b]) => a <= tl.end + 1.5 && b >= tl.start)) E('cards', `no title card around the title line ${tl.id} (${tl.start.toFixed(1)} to ${tl.end.toFixed(1)} s)`);
  if (!cards.some(([a, b]) => b >= dur - 0.6 && a >= dur - (cues.outro_s ?? 4) - 3)) E('cards', `no end card over the last ${(cues.outro_s ?? 4).toFixed(1)} s (the film ends at ${dur.toFixed(2)} s)`);
  return { errors, warnings };
}
