// Kinetic engine: entry point. startKinetic({ specUrl, cuesUrl }) builds a whole 9:16 film from a spec (see SPEC.md).
// Canvas 2D only (no WebGL in the render path). Every frame is a pure function of its index: no clocks, no unseeded randomness.
// Query: ?w=&h= (render size, default 720x1280), ?safe=1 (draw the platform-UI safe mask), ?captions=1 (burn captions from the cues).
import { mk, rng, clamp } from './lib.js';
import { createEngine, FPS } from './engine.js';
import { PAD, BAKERS, bakeInkNoise, bakeVignette, bakeGrain } from './textures.js';
import { Clock } from './timeline.js';
import { compile } from './compile.js';

const FONT_CSS = ['bebas-neue/index.css', 'cormorant-garamond/latin-500-italic.css', 'cormorant-garamond/latin-600-italic.css', 'special-elite/latin-400.css', 'im-fell-english/latin-400.css', 'im-fell-english/latin-400-italic.css'];
const FONT_LOAD = [['400 40px "Bebas Neue"', 'ABC'], ['italic 500 40px "Cormorant Garamond"', 'Hisa,.'], ['italic 600 40px "Cormorant Garamond"', 'Hisa,.'], ['400 40px "Special Elite"', 'Hisa,.'], ['400 40px "IM Fell English"', 'Hisa,.'], ['italic 400 40px "IM Fell English"', 'Hisa,.']];
const SAFE = { x0: 0.11, x1: 0.78, y0: 0.15, y1: 0.65 };

export async function startKinetic({ specUrl, cuesUrl, fps = FPS } = {}) {
  const Q = new URLSearchParams(location.search);
  const W = +Q.get('w') || 720, H = +Q.get('h') || 1280, U = H / 1280, DBG_SAFE = Q.get('safe') === '1';
  try {
    const spec = specUrl.endsWith('.js') ? (await import(new URL(specUrl, location.href).href)).default : await (await fetch(specUrl)).json();
    const cues = await (await fetch(cuesUrl)).json();
    const clock = new Clock(cues, spec.marks || {}), DURATION = cues.duration;
    await Promise.all(FONT_CSS.map((f) => new Promise((res) => { const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = '/harness/node_modules/@fontsource/' + f; l.onload = l.onerror = res; document.head.appendChild(l); })));
    for (const [spec2, txt] of FONT_LOAD) await document.fonts.load(spec2, txt);
    await document.fonts.ready;

    const canvas = mk(W, H); canvas.style.width = W + 'px'; canvas.style.height = H + 'px'; document.body.style.cssText = 'margin:0;background:#000'; document.body.appendChild(canvas);
    const g = canvas.getContext('2d'), INK = mk(W, H), ink = INK.getContext('2d');
    const E = createEngine(W, H, g, ink, clock); E.duration = DURATION;
    const look = { vignette: 0.30, grain: 0.045, ...(spec.look || {}) };
    const { cards, warnings, bgs } = compile(E, spec, clock);
    const PAPER = {}; for (const b of bgs) PAPER[b] = BAKERS[b](W + 2 * PAD, H + 2 * PAD, U);
    const INKNOISE = bakeInkNoise(W, H, U), VIG = bakeVignette(W, H, look.vignette), GRAIN = bakeGrain(W + 80, H + 80, look.grain);
    window.KF_WARNINGS = warnings; for (const w of warnings) console.warn('[kinetic] ' + w);

    const HITS = [];                                                         // [frame, amplitude px @1280, length frames, exposure kick]
    for (const k of cards) for (const [t, amp = 5, len = 5, kick = 0.03] of k.hits) HITS.push([Math.ceil(t * FPS - 1e-6), amp, len, kick]);
    const shakeAt = (f) => { let dx = 0, dy = 0, kick = 0; for (const [f0, amp, len, kk] of HITS) { const d = f - f0; if (d >= 0 && d < len) { const e = Math.pow(1 - d / len, 1.5); dx += amp * e * Math.cos(d * 2.6 + f0); dy += amp * e * Math.sin(d * 3.3 + f0 * 0.7); if (d < 2) kick = Math.max(kick, kk * (d === 0 ? 1 : 0.4)); } } return [dx * U * (look.shake ?? 1), dy * U * (look.shake ?? 1), kick]; };
    const capOn = Q.get('captions') === '1' || (spec.captions && spec.captions !== false);
    const capCfg = typeof spec.captions === 'object' ? spec.captions : {};

    function drawCaptions(t) {
      const L = clock.cues.lines.find((l) => t >= Math.min(l.start, l.words[0][1]) - 0.02 && t <= l.end + 0.25); if (!L) return;
      const shown = L.words.filter((w) => w[1] <= t).map((w) => w[0]); if (!shown.length) return;
      const fs = (capCfg.size ?? 0.0165) * H, y0 = (capCfg.y ?? 0.70) * H, maxW = 0.67 * W; g.save(); g.font = `400 ${fs * 1.5}px "Special Elite"`; g.textBaseline = 'alphabetic'; g.lineJoin = 'round';
      const rows = []; let cur = ''; for (const w of L.words.map((x) => x[0])) { const tt = cur ? cur + ' ' + w : w; if (cur && g.measureText(tt).width > maxW) { rows.push(cur); cur = w; } else cur = tt; } rows.push(cur);
      const done = shown.length; let n = 0;
      rows.forEach((row, r) => { const ws = row.split(' '); let x = 0.11 * W; for (let i = 0; i < ws.length; i++) { n++; const a = n <= done ? 1 : 0.0; const w = ws[i] + ' '; if (a) { g.lineWidth = 4 * U; g.strokeStyle = 'rgba(0,0,0,0.7)'; g.strokeText(ws[i], x, y0 + r * fs * 1.9); g.fillStyle = 'rgba(245,238,222,0.95)'; g.fillText(ws[i], x, y0 + r * fs * 1.9); } x += g.measureText(w).width; } });
      g.restore();
    }

    function renderFrame(f, t) {
      g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none'; g.shadowBlur = 0; g.shadowColor = 'rgba(0,0,0,0)';
      g.textRendering = 'geometricPrecision'; g.fontKerning = 'normal';
      const [sx, sy, kick] = shakeAt(f);
      E.f = f; E.t = t; E.over = [];
      ink.setTransform(1, 0, 0, 1, 0, 0); ink.clearRect(0, 0, W, H); ink.globalAlpha = 1; ink.globalCompositeOperation = 'source-over'; ink.filter = 'none'; ink.shadowBlur = 0; ink.shadowColor = 'rgba(0,0,0,0)';
      ink.textRendering = 'geometricPrecision'; ink.fontKerning = 'normal';
      const active = cards.filter((k) => t >= k.t0 - 1e-9 && t < k.t1 - 1e-9), bgCard = [...active].reverse().find((k) => !k.over) || null;
      g.save(); g.translate(sx, sy);
      if (bgCard) g.drawImage(PAPER[bgCard.bg], -PAD, -PAD); else { g.fillStyle = '#070606'; g.fillRect(-PAD, -PAD, W + 2 * PAD, H + 2 * PAD); g.drawImage(PAPER.dark, -PAD, -PAD); }
      for (const k of active) { E.lt = t - k.t0; E.theme = k.theme; k.draw(E, E.lt); }
      ink.globalCompositeOperation = 'destination-out'; ink.drawImage(INKNOISE, 0, 0); ink.globalCompositeOperation = 'source-over';
      g.drawImage(INK, 0, 0);
      for (const fn of E.over) fn(g);
      g.restore();
      if (bgCard && kick > 0 && bgCard.theme.dark) { g.fillStyle = `rgba(239,230,210,${kick})`; g.fillRect(0, 0, W, H); }
      if (bgCard) {                                              // fades: a card can fade in from black and fade out to black
        let a = 0; if (bgCard.exit === 'fade') a = Math.max(a, clamp((t - (bgCard.t1 - bgCard.exitDur)) / bgCard.exitDur)); if (bgCard.enter === 'fade') a = Math.max(a, 1 - clamp((t - bgCard.t0) / bgCard.enterDur));
        if (a > 0) { g.fillStyle = `rgba(7,6,6,${a})`; g.fillRect(0, 0, W, H); }
      }
      if (capOn) drawCaptions(t);
      g.drawImage(VIG, 0, 0);
      const r = rng(f * 7919 + 13); g.drawImage(GRAIN, -Math.floor(r() * 80), -Math.floor(r() * 80));
      if (DBG_SAFE) {
        g.save(); g.fillStyle = 'rgba(255,0,200,0.30)'; const x0 = SAFE.x0 * W, x1 = SAFE.x1 * W, y0 = SAFE.y0 * H, y1 = SAFE.y1 * H;
        g.fillRect(0, 0, W, y0); g.fillRect(0, y1, W, H - y1); g.fillRect(0, y0, x0, y1 - y0); g.fillRect(x1, y0, W - x1, y1 - y0);
        g.strokeStyle = 'rgba(0,255,255,0.95)'; g.lineWidth = 2; g.strokeRect(x0, y0, x1 - x0, y1 - y0); g.restore();
      }
    }
    window.KF = { width: W, height: H, fps: FPS, duration: DURATION, canvas, warnings, cards: cards.map((k) => ({ type: k.type, name: k.name, t0: k.t0, t1: k.t1, over: k.over, bg: k.bg, lastT: k.lastT })),
      shots: cards.filter((k) => !k.over).map((k) => ({ name: k.name, dur: k.t1 - k.t0 })), render: async (i, t) => { renderFrame(i, t); } };
    window.KF_READY = true;
  } catch (e) { window.KF_ERROR = String(e && e.message || e); console.error('[kinetic] ' + window.KF_ERROR); throw e; }
}
