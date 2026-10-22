// Static checks of a Battle Map spec against its cues, run in the page by films/director/check.cjs (no rendering).
// lint(spec, cues) -> { errors: [...], warnings: [...] }. Errors are things the engine would throw on (now or at some frame)
// or that break the house rules; each message names the path in the spec so the coder seat can fix it.
import { Clock, EASE } from '/films/lib/battlemap/timeline.js';
import { ICON_NAMES } from '/films/lib/battlemap/icons.js';
import { TEAMS, KINDS } from '/films/lib/battlemap/blocks.js';
import { normaliseKey, CameraTrack } from '/films/lib/battlemap/camera.js';

const TIME_KEYS = ['at', 'until', 'hide', 'fallAt'];
const MOVE_PROPS = ['x', 'z', 'heading', 'len', 'dep', 'bulge', 'scale', 'alpha', 'drop', 'lift', 'fade', 'sink', 'count', 'flag', 'glow'];
const LIGHT_PROPS = ['eve', 'haze', 'cloud', 'glint'];
const ARROW_COLORS = ['rome', 'carthage', 'ink', 'gold', 'cream', 'green', 'neutral'];
const EASES = [...Object.keys(EASE), 'spline'];   // whatever the engine knows
const FEATURES = ['undulate', 'hill', 'ridge', 'mountains', 'river', 'sea', 'lake', 'land', 'woods', 'farms', 'road', 'flat'];
const BAD_TEXT = /[—–]|\.\.\.|…/;

export async function lint(spec, cues, opts = {}) {
  const errors = [], warnings = []; const aspect = opts.aspect || 16 / 9; const craft = opts.craft || {};
  const cuts = []; const cam = { worst: [] };
  const E = (p, m) => errors.push(`${p}: ${m}`), W = (p, m) => warnings.push(`${p}: ${m}`);
  if (!spec || typeof spec !== 'object') return { errors: ['the module has no default export object'], warnings };
  const dur = cues.duration; const clock = new Clock(cues, spec.marks || {});
  const T = (p, ref) => { try { const t = clock.at(ref); if (!Number.isFinite(t)) { E(p, `time ${JSON.stringify(ref)} is not a number`); return null; }
    if (t < -0.01) E(p, `time ${JSON.stringify(ref)} = ${t.toFixed(2)} s is before the film starts`);
    else if (t > dur + 0.5 && /(^|\.)at$/.test(p)) W(p, `starts at ${t.toFixed(2)} s, after the film ends (${dur.toFixed(2)} s): never shown`); return t; }
    catch (e) { E(p, e.message); return null; } };
  for (const [k, v] of Object.entries(spec.marks || {})) T(`marks.${k}`, v);

  // CRAFT.md 4: real time. A pan crosses the frame in 4 s or more; a push is 5 to 10 % of the frame per second.
  const cameraSpeed = (keys, p, stageName) => {   // average speed of each move between two keys (a cut is not a move)
    let K; try { K = keys.map((k, i) => ({ ...normaliseKey(k, clock, aspect), i })).sort((x, y) => x.t - y.t); } catch { return; }
    const C = craft.camera; const width = (q) => 2 * q.dist * ((12 / q.mm) * aspect);   // ground width in view near the target
    for (let j = 1; j < K.length; j++) { const a = K[j - 1], b = K[j]; const dt = b.t - a.t; if (b.cut || dt <= 0.05) continue;
      const w = (width(a) + width(b)) / 2, d = (a.dist + b.dist) / 2, pitch = (a.pitch + b.pitch) / 2;
      const lateral = (Math.hypot(b.x - a.x, b.z - a.z) + d * Math.cos(pitch * Math.PI / 180) * Math.abs(b.yaw - a.yaw) * Math.PI / 180) / w / dt;
      const push = Math.abs(Math.log(b.dist / a.dist)) / dt; const r = Math.max(lateral / C.pan_frames_per_s, push / C.push_per_s);
      if (r <= 1.25) continue;
      const msg = `camera move from ${a.t.toFixed(1)} to ${b.t.toFixed(1)} s is too fast (${lateral.toFixed(2)} frame widths/s, limit ${C.pan_frames_per_s}; push ${(push * 100).toFixed(0)} %/s, limit ${(C.push_per_s * 100).toFixed(0)} %): start it earlier, move less, or cut (CRAFT.md 4)`;
      (r > (C.hard_factor || 2) ? E : W)(`${p}[${b.i}]`, msg); }
  };

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
      if (e.ease && !EASES.includes(e.ease)) W(p + '.ease', `unknown easing ${e.ease} (falls back to inOut)`); return [t0, t1]; };
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
      if (it.team && typeof it.team === 'string' && !TEAMS[it.team]) W(p + '.team', `unknown team ${it.team} (drawn without a team colour)`);
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
    const cam = sp.camera || []; if (!cam.length && !(spec.scenes || []).length) E(P('camera'), 'needs at least one key (or a v2 `scenes` list)');
    let prev = -1; cam.forEach((k, i) => { const p = P(`camera[${i}]`); const t = T(p + '.at', k.at);
      if (t !== null && t < prev - 1e-6) W(p, `keys must be in time order (${t.toFixed(2)} s comes after ${prev.toFixed(2)} s)`); if (t !== null) prev = t;
      if (k.target !== undefined && !Array.isArray(k.target)) E(p + '.target', 'must be [x, z]'); if (k.target === undefined && k.x === undefined) W(p, 'no target: looks at [0, 0]');
      if (k.pitch !== undefined && (k.pitch < 3 || k.pitch > 89.9)) E(p + '.pitch', 'must be between 3 and 89.9');
      if (k.ease && !EASES.includes(k.ease)) W(p + '.ease', `unknown easing ${k.ease} (falls back to inOut)`); });
    if (cam.length && craft.camera) cameraSpeed(cam, P('camera'), name);
    for (const [i, k] of cam.entries()) if (k.cut) { try { cuts.push({ t: clock.at(k.at), why: k.why, path: P(`camera[${i}]`) }); } catch {} }
    if (cam.length && name === 'main') { const t0 = (() => { try { return clock.at(cam[0].at); } catch { return 0; } })(); if (t0 > 0.01) W(P('camera[0].at'), 'the first key should be at 0'); }
  };
  stage(spec, 'main');
  for (const [n, sp] of Object.entries(spec.stages || {})) stage(sp, n);
  (spec.insets || []).forEach((e, i) => { const p = `insets[${i}]`; if (!(spec.stages || {})[e.stage]) E(p + '.stage', `no stage ${e.stage}`);
    const t0 = e.at !== undefined ? T(p + '.at', e.at) : null; const t1 = e.until !== undefined ? T(p + '.until', e.until) : null; if (t0 !== null && t1 !== null && t1 < t0) W(p, 'ends before it starts: never shown'); });
  (spec.cards || []).forEach((c, i) => { const p = `cards[${i}]`; const t0 = T(p + '.at', c.at); if (c.until !== undefined) T(p + '.until', c.until);
    (c.lines || []).forEach((L, j) => { if (typeof L.text !== 'string') E(`${p}.lines[${j}].text`, 'missing'); else if (BAD_TEXT.test(L.text)) E(`${p}.lines[${j}].text`, 'no em or en dashes and no "..." on screen'); }); });
  (spec.msaaOn || []).forEach((r, i) => { if (!Array.isArray(r) || r.length !== 2) E(`msaaOn[${i}]`, 'must be [from, to]'); else { T(`msaaOn[${i}][0]`, r[0]); T(`msaaOn[${i}][1]`, r[1]); } });
  for (const [i, e] of (spec.insets || []).entries()) { const full = !e.rect || (e.rect[2] >= 0.999 && e.rect[3] >= 0.999); if (!full) continue;
    try { cuts.push({ t: clock.at(e.at), why: e.why, path: `insets[${i}]` }); if (e.until !== undefined) cuts.push({ t: clock.at(e.until), why: e.why_out || e.why, path: `insets[${i}].until` }); } catch {} }
  for (const [i, c] of (spec.cards || []).entries()) { try { cuts.push({ t: clock.at(c.at), why: c.why || 'card', path: `cards[${i}]`, card: true }); } catch {} }
  const ts = [...new Set(cuts.map((c) => Math.round(c.t * 10) / 10))].filter((t) => t > 0.2 && t < dur - 0.2).sort((a, b) => a - b);
  let stats = { shots: ts.length + 1, avg_shot_s: +(dur / (ts.length + 1)).toFixed(2), cuts: cuts.filter((c) => !c.card).map((c) => ({ t: +c.t.toFixed(2), why: c.why || null, path: c.path })) };
  // Battle Map v2: the engine's own scene compiler (shots, camera speed limits, shot count, short shots, jump cuts)
  if ((spec.scenes || []).length) {
    let SC = null; try { SC = await import('/films/lib/battlemap/scenes.js'); } catch {}
    if (SC && SC.compileScenes) { try { const R = SC.compileScenes(spec, clock, aspect, { duration: dur });
        for (const e of R.errors || []) errors.push('scenes: ' + e); for (const w of R.warnings || []) warnings.push('scenes: ' + w);
        const S = R.shots || []; if (S.length) stats = { shots: S.length, avg_shot_s: +((R.summary && R.summary.asl) || dur / S.length).toFixed(2),
          cuts: [...stats.cuts, ...S.slice(1).map((r) => ({ t: +r.t0.toFixed(2), why: r.why || null, path: `shot ${r.id}` }))] }; }
      catch (e) { errors.push('scenes: ' + (e.message || e)); } }
  }
  // the house: a title card around the title line, an end card over the outro
  const cards = (spec.cards || []).map((c) => { try { return [clock.at(c.at), c.until !== undefined ? clock.at(c.until) : clock.at(c.at) + (c.dur ?? 1), c]; } catch { return null; } }).filter(Boolean);
  const tl = cues.lines.find((l) => l.id === cues.title_line);
  if (tl && !cards.some(([a, b]) => a <= tl.end + 1.5 && b >= tl.start)) E('cards', `no title card around the title line ${tl.id} (${tl.start.toFixed(1)} to ${tl.end.toFixed(1)} s)`);
  if (!cards.some(([a, b]) => b >= dur - 0.6 && a >= dur - (cues.outro_s ?? 4) - 3)) E('cards', `no end card over the last ${(cues.outro_s ?? 4).toFixed(1)} s (the film ends at ${dur.toFixed(2)} s)`);
  return { errors, warnings, stats };
}
