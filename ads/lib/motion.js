// Motion helpers for code-built ads (rendered by harness/dom-render.cjs). Everything is a pure function of time t,
// so any frame can be rendered on its own and the result is identical every run.
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const lerp = (a, b, p) => a + (b - a) * p;
export const ease = {
  outExpo: (p) => (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p)),
  inExpo: (p) => (p <= 0 ? 0 : Math.pow(2, 10 * p - 10)),
  outCubic: (p) => 1 - Math.pow(1 - p, 3),
  inCubic: (p) => p * p * p,
  inOutCubic: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
  inOutQuint: (p) => (p < 0.5 ? 16 * p ** 5 : 1 - Math.pow(-2 * p + 2, 5) / 2),
  outBack: (p, s = 1.70158) => 1 + (s + 1) * Math.pow(p - 1, 3) + s * Math.pow(p - 1, 2),
  // damped spring from 0 to 1: overshoots once or twice and settles
  spring: (p, z = 0.38, w = 16) => (p <= 0 ? 0 : 1 - Math.exp(-z * w * p) * Math.cos(w * Math.sqrt(1 - z * z) * p)),
};
export const mulberry = (seed) => () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

// Split an element's text into masked words: <span class=m><span class=w>word</span></span>. Returns the inner spans.
export function words(el) {
  const parts = el.textContent.trim().split(/\s+/);
  el.innerHTML = parts.map((w) => `<span class="m"><span class="w">${w}</span></span>`).join(' ');
  return [...el.querySelectorAll('.w')];
}
// Split into letters (for tracking and per-letter moves).
export function letters(el) {
  const s = el.textContent; el.innerHTML = [...s].map((c) => `<span class="l">${c === ' ' ? '&nbsp;' : c}</span>`).join('');
  return [...el.querySelectorAll('.l')];
}
// Words rise out of their mask, staggered; then leave upward at tOut (if given).
export function rise(spans, t, tIn, { stagger = 0.06, dur = 0.7, tOut = null, outDur = 0.35, blur = 0 } = {}) {
  spans.forEach((s, k) => {
    const pin = ease.outExpo(seg(t, tIn + k * stagger, tIn + k * stagger + dur));
    const pout = tOut == null ? 0 : ease.inCubic(seg(t, tOut + k * stagger * 0.5, tOut + k * stagger * 0.5 + outDur));
    const y = (1 - pin) * 135 - pout * 135;
    s.style.transform = `translate3d(0, ${y}%, 0)`;
    s.style.filter = blur ? `blur(${(1 - pin) * blur + pout * blur}px)` : '';
  });
}
export const show = (el, on) => { el.style.visibility = on ? 'visible' : 'hidden'; };
export function fitStage(stage) {
  const q = new URLSearchParams(location.search); const w = +q.get('w') || 1920, h = +q.get('h') || 1080;
  stage.style.transform = `scale(${w / 1920}, ${h / 1080})`; stage.style.transformOrigin = '0 0';
  return q;
}
