// Battle Map engine v2: scenes, sets and pre-planned cameras (pure JS: runs in the browser and in Node for the checks).
// A film is 5 to 9 scenes. A scene = a set (which map, time of day, haze, cloud) + a job (one dramatic question) + shots.
// A shot = a cut with a written reason (`why`), an opening frame (`from`), motivated moves (each with an ease), and so a closing frame.
// compileScenes() turns them into camera keys, light segments and insets, and runs the director's checks (CRAFT.md sections 2 to 4):
//  - camera speed limits (a real operator's speeds): a move faster than the limits is REFUSED (an error) unless it says `fast: 'reason'`;
//  - shot count and average shot length for the runtime, very short shots, jump cuts (same subject, under 30 degrees and no size step),
//    missing reasons. These are warnings, printed in the report.
import { normaliseKey, CameraTrack } from './camera.js';

export const CAMERA_LIMITS = { pan: 0.26, zoom: 0.16, yaw: 16, pitch: 12 }; // peaks: frame widths per s, ln(distance) per s, degrees per s
const POSE_KEYS = ['target', 'dist', 'width', 'pitch', 'yaw', 'mm', 'ty'];
const merge = (cur, to = {}, by = {}) => { const o = { ...cur }; for (const k of POSE_KEYS) if (to[k] !== undefined) o[k] = Array.isArray(to[k]) ? to[k].slice() : to[k];
  if (to.width !== undefined) delete o.dist; if (to.dist !== undefined) delete o.width;
  if (by.target) o.target = [o.target[0] + by.target[0], o.target[1] + by.target[1]]; for (const k of ['pitch', 'yaw', 'mm']) if (by[k] !== undefined) o[k] += by[k];
  if (by.zoom !== undefined) { if (o.width !== undefined) o.width *= by.zoom; else o.dist *= by.zoom; } return o; };
const hfov = (mm, aspect) => { const vf = 2 * Math.atan(12 / mm); return 2 * Math.atan(Math.tan(vf / 2) * aspect); };
const groundW = (p, aspect) => 2 * p.dist * Math.tan(hfov(p.mm, aspect) / 2);
const sizeClass = (p, aspect) => { const w = groundW(p, aspect); return w > 420 ? 'EWS' : w > 260 ? 'WS' : w > 150 ? 'MWS' : w > 80 ? 'MS' : 'CU'; };
const angleClass = (p) => p.pitch > 75 ? 'top' : p.pitch > 45 ? 'high' : p.pitch > 22 ? 'oblique' : 'low';
const f1 = (x) => (Math.round(x * 10) / 10).toFixed(1);

export function compileScenes(spec, clock, aspect = 16 / 9, opts = {}) {
  const scenes = (spec.scenes || []).map((s, i) => ({ ...s, i, t0: clock.at(s.at) })).sort((a, b) => a.t0 - b.t0); const out = { keys: {}, light: {}, insets: [], dissolves: [], shots: [], errors: [], warnings: [], scenes: [] };
  if (!scenes.length) return out; const dur = opts.duration ?? clock.cues?.duration ?? 150; const L = { ...CAMERA_LIMITS, ...(spec.cameraLimits || {}) };
  scenes.forEach((s, i) => { s.t1 = s.until !== undefined ? clock.at(s.until) : (scenes[i + 1] ? scenes[i + 1].t0 : dur); });
  for (const s of scenes) {
    const st = s.stage || 'main'; const keys = (out.keys[st] ||= []); const id = s.id || `S${s.i + 1}`; if (!s.job) out.warnings.push(`${id}: no job (what does the viewer learn or feel in this scene?)`);
    // the set: light at the scene's start (a cut changes it at once; a dissolve blends it), drifting through the scene
    const set = s.set || {}; const lt = (out.light[st] ||= []); const tr = s.transition || 'cut'; const blend = typeof tr === 'object' ? (tr.dur ?? 1) : 0;
    for (const [k, v] of Object.entries({ eve: set.time, haze: set.haze, cloud: set.cloud, glint: set.glint })) { if (v === undefined) continue; const a = Array.isArray(v) ? v[0] : v, b = Array.isArray(v) ? v[1] : v;
      lt.push({ at: s.t0, dur: Math.max(0.001, blend), to: { [k]: a }, ease: 'inOut' }); if (b !== a) lt.push({ at: s.t0 + blend + 0.002, until: s.t1, to: { [k]: b }, ease: 'linear' }); }
    if (s.inset) { const full = s.inset === 'full' || s.inset === true; const r = full ? { rect: [0, 0, 1, 1], frame: false, pop: false, samples: 0 } : s.inset; out.insets.push({ stage: st, at: s.t0, until: s.t1, in: blend || 0.01, out: s.outDur ?? 0.01, ...r }); }
    if (typeof tr === 'object' && tr.type === 'dissolve' && !s.inset) out.dissolves.push({ stage: st, t0: s.t0, t1: s.t0 + blend, tc: s.t0 }); // the outgoing frame (held) fades off the incoming shot
    const shots = (s.shots || []).map((sh, j) => ({ ...sh, j, t0: clock.at(sh.at ?? s.at) })).sort((a, b) => a.t0 - b.t0); if (!shots.length) out.errors.push(`${id}: a scene needs at least one shot`);
    shots.forEach((sh, j) => { sh.t1 = shots[j + 1] ? shots[j + 1].t0 : s.t1; });
    const sc = { id, name: s.name || '', job: s.job || '', t0: s.t0, t1: s.t1, stage: st, shots: [] }; out.scenes.push(sc);
    for (const sh of shots) {
      const sid = `${id}.${sh.j + 1}`; if (!sh.from) { out.errors.push(`${sid}: a shot needs an opening frame (from)`); continue; } if (!sh.why) out.warnings.push(`${sid}: no reason for the cut (why)`);
      let cur = merge({ pitch: 60, yaw: 0, mm: 35 }, sh.from); keys.push({ ...cur, at: sh.t0, cut: keys.length > 0, ease: 'linear' }); let tp = sh.t0; const open = normaliseKey({ ...cur, at: sh.t0 }, clock, aspect);
      for (const mv of (sh.moves || [])) {
        const m0 = mv.at !== undefined ? clock.at(mv.at) : tp; const m1 = mv.until !== undefined ? clock.at(mv.until) : m0 + (mv.dur ?? 3);
        if (m0 < tp - 1e-3) out.errors.push(`${sid}: move starts at ${f1(m0)} s, before the previous move ends (${f1(tp)} s)`); if (m1 > sh.t1 + 1e-3) out.warnings.push(`${sid}: a move ends at ${f1(m1)} s, after the shot is cut (${f1(sh.t1)} s)`);
        if (m0 > tp + 1e-3) keys.push({ ...cur, at: m0, ease: 'linear' });
        const prev = cur; cur = merge(cur, mv.to, mv.by); keys.push({ ...cur, at: m1, ease: mv.ease || 'inOut' }); tp = m1;
        // speed check: sample the eased move
        const a = normaliseKey({ ...prev, at: m0 }, clock, aspect), b = normaliseKey({ ...cur, at: m1, ease: mv.ease === 'spline' ? 'inOut' : (mv.ease || 'inOut') }, clock, aspect); const tr2 = new CameraTrack([a, b]); const N = 48; let peak = { pan: 0, zoom: 0, yaw: 0, pitch: 0 }; let p0 = tr2.at(m0);
        for (let q = 1; q <= N; q++) { const tq = m0 + (m1 - m0) * q / N; const p1 = tr2.at(tq); const dt = (m1 - m0) / N; const gw = (groundW(p0, aspect) + groundW(p1, aspect)) / 2;
          peak.pan = Math.max(peak.pan, Math.hypot(p1.x - p0.x, p1.z - p0.z) / gw / dt); peak.zoom = Math.max(peak.zoom, Math.abs(Math.log(p1.dist / p0.dist)) / dt); peak.yaw = Math.max(peak.yaw, Math.abs(p1.yaw - p0.yaw) / dt); peak.pitch = Math.max(peak.pitch, Math.abs(p1.pitch - p0.pitch) / dt); p0 = p1; }
        const over = Object.keys(peak).filter((k) => peak[k] > L[k] * 1.0001);
        if (over.length && !mv.fast) out.errors.push(`${sid}: move ${f1(m0)} to ${f1(m1)} s is faster than a real camera (${over.map((k) => `${k} ${peak[k].toFixed(2)} > ${L[k]}`).join(', ')}): start earlier, move less, or hold longer`);
        mv._peak = peak;
      }
      const close = normaliseKey({ ...cur, at: sh.t1 }, clock, aspect); const d = sh.t1 - sh.t0;
      const rec = { id: sid, scene: id, t0: sh.t0, t1: sh.t1, dur: d, why: sh.why || '', size: sizeClass(open, aspect), angle: angleClass(open), moves: (sh.moves || []).length, open, close, stage: st, climax: !!(s.climax || sh.climax) };
      sc.shots.push(rec); out.shots.push(rec);
    }
  }
  // edit checks
  const S = out.shots.sort((a, b) => a.t0 - b.t0); const n = S.length; const lo = Math.round(18 * dur / 150), hi = Math.round(35 * dur / 150), hard = Math.round(40 * dur / 180);
  if (out.scenes.length < 5 || out.scenes.length > 9) out.warnings.push(`scene count ${out.scenes.length} (wanted 5 to 9)`);
  if (n < lo || n > hi) out.warnings.push(`shot count ${n} for ${f1(dur)} s (wanted ${lo} to ${hi})`); if (n > hard) out.errors.push(`shot count ${n} is over the hard limit ${hard} for ${f1(dur)} s`);
  for (const r of S) if (r.dur < 2 && !r.climax) out.warnings.push(`${r.id}: ${f1(r.dur)} s shot (under 2 s is for the climax only)`);
  for (let i = 1; i < n; i++) { const a = S[i - 1], b = S[i]; if (a.stage !== b.stage) continue; const A = a.close, B = b.open; const gw = groundW(A, aspect);
    const dy = Math.abs(((B.yaw - A.yaw) % 360 + 540) % 360 - 180), dp = Math.abs(B.pitch - A.pitch), dr = Math.max(B.dist / A.dist, A.dist / B.dist), dt = Math.hypot(B.x - A.x, B.z - A.z) / gw;
    if (dy < 30 && dp < 15 && dr < 1.45 && dt < 0.3) out.warnings.push(`${a.id} > ${b.id}: jump cut (same subject, ${dy.toFixed(0)} deg, size x${dr.toFixed(2)}): change angle by 30 degrees or the size by a step`); }
  const asl = n ? S.reduce((q, r) => q + r.dur, 0) / n : 0; out.summary = { scenes: out.scenes.length, shots: n, asl, range: [lo, hi] };
  return out;
}
export function reportText(R) {
  const L = []; L.push(`${R.summary.scenes} scenes, ${R.summary.shots} shots (wanted ${R.summary.range[0]} to ${R.summary.range[1]}), average shot ${f1(R.summary.asl)} s`);
  for (const s of R.scenes) { L.push(`\n${s.id} ${s.name} [${f1(s.t0)} to ${f1(s.t1)} s${s.stage !== 'main' ? ', ' + s.stage : ''}]: ${s.job}`); for (const r of s.shots) L.push(`  ${r.id.padEnd(6)} ${f1(r.t0).padStart(6)} ${f1(r.dur).padStart(5)} s  ${r.size.padEnd(4)} ${r.angle.padEnd(8)} ${r.moves ? r.moves + ' move' + (r.moves > 1 ? 's' : '') : 'locked'}  ${r.why}`); }
  if (R.errors.length) L.push('\nERRORS\n' + R.errors.map((e) => '  ' + e).join('\n')); if (R.warnings.length) L.push('\nwarnings\n' + R.warnings.map((e) => '  ' + e).join('\n'));
  return L.join('\n');
}
// apply a compiled plan to a spec (main and stages): camera keys, light, insets. Legacy `camera` arrays are kept where no scene drives that stage.
export function applyScenes(spec, R) {
  const tgt = (st) => st === 'main' ? spec : spec.stages?.[st]; for (const [st, keys] of Object.entries(R.keys)) { const T = tgt(st); if (!T) throw new Error('scenes: unknown stage ' + st); T.camera = keys; }
  for (const [st, lt] of Object.entries(R.light)) { const T = tgt(st); T.light = [...lt, ...(T.light || [])]; }
  spec.insets = [...(spec.insets || []), ...R.insets]; spec._dissolves = R.dissolves;
}
