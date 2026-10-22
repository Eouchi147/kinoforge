// Kinetic engine: time references (cue lines and words, marks, strong hits) and the word matcher that gives text its automatic timing.
// Same reference forms as the Battle Map engine ("o1", "o1>", "o1.word", "o1.word>", "o1.the#1", "o1.word+0.3", marks, objects).
// Pure JS (runs in Node too).
export const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
const ONES = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'];
const TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'];
export function numNorm(n) { n = +n; if (!(n >= 0 && n < 100) || n !== Math.floor(n)) return null; return n < 20 ? ONES[n] : TENS[Math.floor(n / 10)] + (n % 10 ? ONES[n % 10] : ''); }

export class Clock {
  constructor(cues, marks = {}) {
    this.cues = cues; this.marks = marks; this._res = new Set(); this.hits = cues.strong_hits || []; this.lines = {}; this.flat = [];
    for (const l of cues.lines) { this.lines[l.id] = l; l.words.forEach((w, i) => this.flat.push({ n: norm(w[0]), t: w[1], e: w[2], line: l.id, i, text: w[0] })); }
    this.flat.sort((a, b) => a.t - b.t);
    this.duration = cues.duration;
  }
  word(line, word, nth = 0, edge = 'start') {
    const L = this.lines[line]; if (!L) throw new Error('unknown line ' + line);
    const w = norm(word); let n = 0, cand = null;
    for (const t of L.words) { const k = norm(t[0]); if (k === w) { if (n === nth) return edge === 'end' ? t[2] : t[1]; n++; } else if (!cand && w.length > 2 && k.startsWith(w)) cand = t; }
    if (cand) return edge === 'end' ? cand[2] : cand[1];
    throw new Error(`word "${word}" (#${nth}) not found in ${line}: ${L.text}`);
  }
  snap(t, maxd = 0.3) { let best = null, bd = maxd; for (const h of this.hits) { const d = Math.abs(h - t); if (d < bd) { bd = d; best = h; } } return best ?? t; }
  // forms: number | "o1" | "o1>" | "o1.word" | "o1.word>" | "o1.the#2+0.3" | "markName" | {line, word, nth, edge, offset, snap} | {mark, offset} | {hit:n} | {beat:n} | {downbeat:n}
  at(ref) {
    if (typeof ref === 'number') return ref;
    if (typeof ref === 'string') {
      const m = ref.match(/^([A-Za-z_][A-Za-z0-9_]*)(?:\.([^#>+]+?)(?:#(\d+))?)?(>)?([+-]\d*\.?\d+)?$/);
      if (m) {
        const off = m[5] ? parseFloat(m[5]) : 0;
        if (this.lines[m[1]]) { const L = this.lines[m[1]]; if (m[2]) return this.word(m[1], m[2], m[3] ? +m[3] : 0, m[4] ? 'end' : 'start') + off; return (m[4] ? L.end : L.start) + off; }
        if (!m[2] && !m[4] && this.marks[m[1]] !== undefined) { if (this._res.has(m[1])) throw new Error('mark cycle ' + m[1]); this._res.add(m[1]); const v = this.at(this.marks[m[1]]); this._res.delete(m[1]); return v + off; }
        throw new Error('unknown cue line or mark "' + m[1] + '" in time ref "' + ref + '"');
      }
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
  span(e, defDur = 1) { const t0 = this.at(e.at); const t1 = e.until !== undefined ? this.at(e.until) : t0 + (e.dur ?? defDur); return [t0, t1]; }
  // the cue line that is being spoken at (or next after) t
  lineAt(t) { let best = null; for (const l of this.cues.lines) { if (t >= l.start - 0.6 && t <= l.end + 0.05) return l; if (l.start > t && !best) best = l; } return best; }
  // Automatic timing: for each display word find the matching cue word, scanning forward from time `from`.
  // Returns an array of times (null where nothing matched; callers fill the gaps), or null when nothing matched at all.
  match(words, from, { window = 9, to = 1e9 } = {}) {
    let ptr = 0; while (ptr < this.flat.length && this.flat[ptr].t < from - 0.35) ptr++;
    const out = new Array(words.length).fill(null); let any = false;
    for (let i = 0; i < words.length; i++) {
      const wn = norm(words[i]); if (!wn) continue; const nn = /^\d+$/.test(wn) ? numNorm(wn) : null;
      for (let k = ptr; k < Math.min(this.flat.length, ptr + window); k++) {
        const c = this.flat[k]; if (c.t > to) break;
        const hit = c.n === wn || (nn && c.n === nn) || (wn.length > 2 && c.n.length > 2 && (c.n.startsWith(wn) || wn.startsWith(c.n)));
        if (hit) { out[i] = c.t; ptr = k + 1; any = true; break; }
      }
    }
    return any ? out : null;
  }
}
// fill null entries by interpolating between known neighbours (ends extrapolate by `step`)
export function fillGaps(ts, t0, t1, step = 0.22) {
  const n = ts.length, out = ts.slice(); const known = out.map((v, i) => (v == null ? -1 : i)).filter((i) => i >= 0);
  if (!known.length) { for (let i = 0; i < n; i++) out[i] = n === 1 ? t0 : t0 + (t1 - t0) * (i / Math.max(1, n - 1)); return out; }
  for (let i = 0; i < n; i++) {
    if (out[i] != null) continue;
    let a = -1, b = -1; for (let j = i - 1; j >= 0; j--) if (ts[j] != null) { a = j; break; } for (let j = i + 1; j < n; j++) if (ts[j] != null) { b = j; break; }
    if (a >= 0 && b >= 0) out[i] = ts[a] + (ts[b] - ts[a]) * ((i - a) / (b - a)); else if (a >= 0) out[i] = ts[a] + (i - a) * step; else out[i] = ts[b] - (b - i) * step;
  }
  return out;
}
