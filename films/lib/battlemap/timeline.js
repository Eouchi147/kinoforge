// Battle Map engine: time references (cue words, marks, strong hits) and animation tracks. Pure JS (runs in Node too).
import { clamp, lerp } from './noise.js';

export const EASE = {
  linear: (t) => t, in: (t) => t * t * t, out: (t) => 1 - Math.pow(1 - t, 3), inOut: (t) => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  inQuad: (t) => t * t, outQuad: (t) => t * (2 - t), inOutQuad: (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  smooth: (t) => t * t * t * (t * (t * 6 - 15) + 10), // smootherstep
  outBack: (t) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  inBack: (t) => { const c1 = 1.70158, c3 = c1 + 1; return c3 * t * t * t - c1 * t * t; },
  outElastic: (t) => t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI / 3)) + 1,
  outBounce: (t) => { const n = 7.5625, d = 2.75; if (t < 1 / d) return n * t * t; if (t < 2 / d) return n * (t -= 1.5 / d) * t + 0.75; if (t < 2.5 / d) return n * (t -= 2.25 / d) * t + 0.9375; return n * (t -= 2.625 / d) * t + 0.984375; },
  step: (t) => t >= 1 ? 1 : 0,
};
export const easeFn = (e) => typeof e === 'function' ? e : (EASE[e || 'inOut'] || EASE.inOut);

const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');

export class Clock {
  constructor(cues, marks = {}) { this.cues = cues; this.lines = {}; for (const l of cues.lines) this.lines[l.id] = l; this.marks = marks; this._res = new Set(); this.hits = cues.strong_hits || []; }
  word(line, word, nth = 0, edge = 'start') {
    const L = this.lines[line]; if (!L) throw new Error('unknown line ' + line);
    const w = norm(word); let n = 0, cand = null;
    for (const t of L.words) { const k = norm(t[0]); if (k === w) { if (n === nth) return edge === 'end' ? t[2] : t[1]; n++; } else if (!cand && w.length > 2 && k.startsWith(w)) cand = t; }
    if (cand) return edge === 'end' ? cand[2] : cand[1];
    throw new Error(`word "${word}" (#${nth}) not found in ${line}: ${L.text}`);
  }
  snap(t, maxd = 0.3) { let best = null, bd = maxd; for (const h of this.hits) { const d = Math.abs(h - t); if (d < bd) { bd = d; best = h; } } return best ?? t; }
  // forms: number | "l08" | "l08>" | "l08.charged" | "l08.charged>" | "l08.the#2+0.3" | "markName" | {line, word, nth, edge, offset, snap} | {mark, offset} | {hit:n} | {beat:n} | {downbeat:n}
  at(ref) {
    if (typeof ref === 'number') return ref;
    if (typeof ref === 'string') {
      const m = ref.match(/^(l\d+)(?:\.([^#>+]+?)(?:#(\d+))?)?(>)?([+-]\d*\.?\d+)?$/);
      if (m) { const off = m[5] ? parseFloat(m[5]) : 0; const L = this.lines[m[1]]; if (!L) throw new Error('unknown line ' + m[1]); if (m[2]) return this.word(m[1], m[2], m[3] ? +m[3] : 0, m[4] ? 'end' : 'start') + off; return (m[4] ? L.end : L.start) + off; }
      const mm = ref.match(/^([A-Za-z_][\w-]*)([+-]\d*\.?\d+)?$/); if (mm && this.marks[mm[1]] !== undefined) { if (this._res.has(mm[1])) throw new Error('mark cycle ' + mm[1]); this._res.add(mm[1]); const v = this.at(this.marks[mm[1]]); this._res.delete(mm[1]); return v + (mm[2] ? parseFloat(mm[2]) : 0); }
      throw new Error('bad time ref: ' + ref);
    }
    if (ref && typeof ref === 'object') {
      let t;
      if (ref.line !== undefined) { const L = this.lines[ref.line]; if (!L) throw new Error('unknown line ' + ref.line); t = ref.word !== undefined ? this.word(ref.line, ref.word, ref.nth || 0, ref.edge || 'start') : (ref.edge === 'end' ? L.end : L.start); }
      else if (ref.mark !== undefined) t = this.at(String(ref.mark));
      else if (ref.hit !== undefined) t = this.hits[ref.hit];
      else if (ref.beat !== undefined) t = this.cues.beats[ref.beat];
      else if (ref.downbeat !== undefined) t = this.cues.downbeats[ref.downbeat];
      else throw new Error('bad time ref ' + JSON.stringify(ref));
      if (ref.snap) t = this.snap(t, typeof ref.snap === 'number' ? ref.snap : 0.3);
      return t + (ref.offset || 0);
    }
    throw new Error('bad time ref ' + ref);
  }
  // an entry's start and end: {at, dur} or {at, until}
  span(e, defDur = 1) { const t0 = this.at(e.at); const t1 = e.until !== undefined ? this.at(e.until) : t0 + (e.dur ?? defDur); return [t0, t1]; }
}

// one animated scalar: sequential segments; a segment goes from the value at its start to a target with an easing
export class Track {
  constructor(v0 = 0) { this.v0 = v0; this.segs = []; }
  at(t) { // value at time t
    let v = this.v0; for (const s of this.segs) { if (t < s.t0) break; if (t >= s.t1) { v = s.b; continue; } const u = (t - s.t0) / Math.max(1e-6, s.t1 - s.t0); const e = s.ease(u); v = s.fn ? s.fn(e) : s.a + (s.b - s.a) * e; return v; } return v;
  }
  add(t0, t1, b, ease = 'inOut', opts = {}) { // b: target (or a function(e)->value when opts.fn)
    const a = this.at(t0); const seg = { t0, t1: Math.max(t1, t0 + 1e-6), a, b: opts.fn ? opts.fn(1) : b, ease: easeFn(ease), fn: opts.fn || null }; this.segs.push(seg); this.segs.sort((p, q) => p.t0 - q.t0); return this;
  }
  set(t0, v) { return this.add(t0, t0 + 1e-6, v, 'linear'); }
}
