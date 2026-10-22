// Dark Corners, "A Hundred Thousand Good Nights" (Bamberg, 1628), re-made in the KINOFORGE Kinetic style. 9:16, 24 fps.
// Canvas 2D only (no WebGL in the render path: the finish pass is baked in 2D). Every frame is a pure function of its index.
// The picture follows the sound: every landing time comes from cues.json (narration word times). ?safe=1 draws the platform-UI mask.
import { mk, clamp, smoothstep, rng } from './lib.js';
import { createEngine, FPS } from './engine.js';
import { PAD, bakeDark, bakeCream, bakeCold, bakeInkNoise, bakeVignette, bakeGrain } from './textures.js';
import { buildOpen } from './scenes_open.js';
import { buildCtx } from './scenes_ctx.js';
import { buildCourt } from './scenes_court.js';
import { buildLetter } from './scenes_letter.js';
import { buildTurn } from './scenes_turn.js';
import { buildEnd } from './scenes_end.js';

const Q = new URLSearchParams(location.search);
const W = +Q.get('w') || 720, H = +Q.get('h') || 1280, U = H / 1280, DBG_SAFE = Q.get('safe') === '1';
const SAFE = { x0: 0.11, x1: 0.78, y0: 0.15, y1: 0.65 };
const film = await (await fetch('./film.json')).json();
const cues = await (await fetch('./cues.json')).json();
const DURATION = film.duration, TOTAL = Math.round(DURATION * FPS);

const canvas = mk(W, H); canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
document.body.appendChild(canvas);
const g = canvas.getContext('2d');
const INK = mk(W, H), ink = INK.getContext('2d');
const E = createEngine(W, H, g, ink, cues);
E.C = { dark: '#0e0d0b', cream: '#efe6d2', ink: '#1a1612', cold: '#14171a', coldInk: '#14171a', red: '#cf3b2e', warm: '#efe6d2' };

await document.fonts.load('400 40px "Bebas Neue"', 'ABC');
for (const spec of ['italic 500 40px "Cormorant Garamond"', 'italic 600 40px "Cormorant Garamond"', '400 40px "Special Elite"', '400 40px "IM Fell English"', 'italic 400 40px "IM Fell English"']) await document.fonts.load(spec, 'Hisa,.');
await document.fonts.ready;

const PAPER = { dark: bakeDark(W + 2 * PAD, H + 2 * PAD, U), cream: bakeCream(W + 2 * PAD, H + 2 * PAD, U), cold: bakeCold(W + 2 * PAD, H + 2 * PAD, U) };
const INKNOISE = bakeInkNoise(W, H, U), VIG = bakeVignette(W, H), GRAIN = bakeGrain(W + 80, H + 80);
E.duration = DURATION; E.PAPER = PAPER; E.PAD = PAD; E.INK = INK; E.INKNOISE = INKNOISE;

// ---- scenes: contiguous cuts, each starts at t0 and runs to the next t0
const SCENES = [...buildOpen(E), ...buildCtx(E), ...buildCourt(E), ...buildLetter(E), ...buildTurn(E), ...buildEnd(E).S].sort((a, b) => a.t0 - b.t0);
const HITS = [];                                                         // [frame, amplitude px @1280, length frames, exposure kick]
for (const s of SCENES) for (const [t, amp = 5, len = 5, kick = 0.03] of s.hits || []) HITS.push([Math.ceil(t * FPS - 1e-6), amp, len, kick]);
const shakeAt = (f) => { let dx = 0, dy = 0, kick = 0; for (const [f0, amp, len, k] of HITS) { const d = f - f0; if (d >= 0 && d < len) { const e = Math.pow(1 - d / len, 1.5); dx += amp * e * Math.cos(d * 2.6 + f0); dy += amp * e * Math.sin(d * 3.3 + f0 * 0.7); if (d < 2) kick = Math.max(kick, k * (d === 0 ? 1 : 0.4)); } } return [dx * U, dy * U, kick]; };
const sceneAt = (t) => { let s = SCENES[0]; for (const x of SCENES) if (t >= x.t0 - 1e-9) s = x; else break; return s; };

function renderFrame(f, t) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none'; g.shadowBlur = 0; g.shadowColor = 'rgba(0,0,0,0)';
  g.textRendering = 'geometricPrecision'; g.fontKerning = 'normal';
  const sc = sceneAt(t), [sx, sy, kick] = shakeAt(f);
  E.f = f; E.t = t; E.lt = t - sc.t0; E.sc = sc; E.over = [];
  ink.setTransform(1, 0, 0, 1, 0, 0); ink.clearRect(0, 0, W, H); ink.globalAlpha = 1; ink.globalCompositeOperation = 'source-over'; ink.filter = 'none'; ink.shadowBlur = 0; ink.shadowColor = 'rgba(0,0,0,0)';
  ink.textRendering = 'geometricPrecision'; ink.fontKerning = 'normal';
  g.save(); g.translate(sx, sy);
  if (sc.bg && sc.bg !== 'none') g.drawImage(PAPER[sc.bg], -PAD, -PAD);
  sc.draw(E, E.lt);
  ink.globalCompositeOperation = 'destination-out'; ink.drawImage(INKNOISE, 0, 0); ink.globalCompositeOperation = 'source-over';
  if (!sc.noInk) g.drawImage(INK, 0, 0);
  for (const fn of E.over) fn(g);
  g.restore();
  if (kick > 0 && sc.bg === 'dark') { g.fillStyle = `rgba(239,230,210,${kick})`; g.fillRect(0, 0, W, H); }
  g.drawImage(VIG, 0, 0);
  const r = rng(f * 7919 + 13); g.drawImage(GRAIN, -Math.floor(r() * 80), -Math.floor(r() * 80));
  if (DBG_SAFE) {
    g.save(); g.fillStyle = 'rgba(255,0,200,0.30)'; const x0 = SAFE.x0 * W, x1 = SAFE.x1 * W, y0 = SAFE.y0 * H, y1 = SAFE.y1 * H;
    g.fillRect(0, 0, W, y0); g.fillRect(0, y1, W, H - y1); g.fillRect(0, y0, x0, y1 - y0); g.fillRect(x1, y0, W - x1, y1 - y0);
    g.strokeStyle = 'rgba(0,255,255,0.95)'; g.lineWidth = 2; g.strokeRect(x0, y0, x1 - x0, y1 - y0); g.restore();
  }
}

window.KF = { width: W, height: H, fps: FPS, duration: DURATION, canvas, shots: SCENES.map((s, i) => ({ name: s.name || 's' + i, dur: ((SCENES[i + 1] ? SCENES[i + 1].t0 : DURATION) - s.t0) })), render: async (i, t) => { renderFrame(i, t); } };
window.KF_READY = true;
