// Bamberg (Kinetic): small shared helpers for the scene files (text blocks, the dim behind type, a paper-bound hand block).
import { clamp, ease, lerp, rgba } from './lib.js';

export function makeKit(E) {
  const { W, H, U, C } = E;
  const kit = {};
  // a block of lines stacked with optical spacing; `out` fades the whole block (a clean exchange, never a pop)
  kit.block = (specs, top, o = {}) => {
    const { color = C.cream, out, outDur = 0.22, alpha, k = 0.36, lo, hi } = o, st = E.stk(specs, top, k, lo, hi);
    const ex = {}; if (out != null) { ex.out = out; ex.outDur = outDur; } if (alpha != null) ex.alpha = alpha;
    for (const s of st.lines) E.line({ color, ...s, ...ex });
    return st;
  };
  // the dim behind the type on a busy ground: a long soft fall-off from the top so the map never fights the words
  kit.dim = (to = 0.5, a0 = 0.8) => {
    const g = E.g, gr = g.createLinearGradient(0, 0, 0, to * H); gr.addColorStop(0, `rgba(12,11,9,${a0})`); gr.addColorStop(0.45, `rgba(12,11,9,${a0 * 0.82})`); gr.addColorStop(0.8, `rgba(12,11,9,${a0 * 0.30})`); gr.addColorStop(1, 'rgba(12,11,9,0)');
    g.fillStyle = gr; g.fillRect(0, 0, W, to * H);
  };
  // alpha of an element that exists between a and b with a fade of d at both ends
  kit.win = (t, a, b, d = 0.2) => clamp((t - a) / d) * (1 - clamp((t - b) / d));
  return kit;
}
