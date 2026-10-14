// P12 TERRAIN — single source of truth for picture AND sound timing (pure; imported by scene.js, run in Node by tools/timing.mjs which writes timing.json for audio.py).
export const FPS = 24;
const F = (n) => n / FPS;
export const CUT_S2 = F(87), CUT_S3 = F(183);               // first frames of S2 / S3 (the brief's 3.6 s / 7.6 s snapped to whole frames)
export const SHOT_DUR = [CUT_S2, CUT_S3 - CUT_S2, 10 - CUT_S3]; // 3.625 / 4.0 / 2.375 s
export const TIMES = {
  draw0: 0.60,            // the pen touches down at Camp II
  stop: F(201),           // 8.375 s: the route is complete, the pen lifts
  marker: F(201),         // the ring appears on the same frame (low hit + 880 Hz ring)
  silenceFrom: F(189),    // 12 frames of near-silence before the stop (R-3-06)
  campPop: F(8),          // label pops (paper hit each), snapped to frames; tarn/saddle retimed from tools/scan.mjs (anchor first inside the frame, unoccluded)
  tarnPop: F(142),        // 5.917 s
  saddlePop: F(171),      // 7.125 s
  cap1: [0.85, 3.25],     // caption 1 fade-in start / fade-out start (fades 0.5 s)
  cap2: [8.72, 10.0],
};
const ss = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
// raw pen speed (arbitrary units): pen accelerates off the paper, a hand-made wobble, a slow fade, then the pen eases down over the last 0.6 s as the ink runs dry
export function speedRaw(t) {
  const { draw0, stop } = TIMES; if (t <= draw0 || t >= stop) return 0;
  const start = ss(draw0, draw0 + 0.55, t);
  const trend = 1.0 - 0.26 * ss(2.6, 7.4, t);
  const wob = 1 + 0.11 * Math.sin(2 * Math.PI * t / 0.83 + 0.6) + 0.05 * Math.sin(2 * Math.PI * t / 0.31 + 1.9);
  const end = t > stop - 0.6 ? 0.1 + 0.9 * (1 - ss(stop - 0.6, stop, t)) : 1;
  return start * trend * wob * end;
}
const DT = 1 / 960, N = Math.round(10 / DT); const cum = new Float64Array(N + 1);
for (let i = 1; i <= N; i++) cum[i] = cum[i - 1] + 0.5 * (speedRaw((i - 1) * DT) + speedRaw(i * DT)) * DT;
const TOTAL = cum[Math.round(TIMES.stop / DT)];
export const CRUISE = 1.0; // speedRaw peak ~ trend*wob
export function progress(t) { // 0..1 fraction of the route drawn at time t
  const x = Math.min(Math.max(t, 0), 10) / DT, i = Math.floor(x); return Math.min(1, (cum[i] + (cum[Math.min(N, i + 1)] - cum[i]) * (x - i)) / TOTAL);
}
export function speedNorm(t) { return speedRaw(t) / TOTAL; } // fraction of L per second
