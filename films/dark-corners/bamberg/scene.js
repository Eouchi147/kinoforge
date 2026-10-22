// Dark Corners, "A Hundred Thousand Good Nights" (Bamberg, 1628), re-made in the KINOFORGE Kinetic style. 9:16, 24 fps.
// Canvas 2D only (no WebGL in the render path: the finish pass is baked in 2D). Every frame is a pure function of its index.
// The picture follows the sound: every landing time comes from cues.json (narration word times). ?safe=1 draws the platform-UI mask.
// The film is eight movements played on ONE desk (see NOTES.md). A scene is a stretch of the desk; scenes meet by a transition that has a reason:
// a document slides onto / off the desk, ink bleeds from the tally into the dark, a hard cut only where a hit lands.
import { mk, clamp, lerp, ease, smoothstep, rng, noise1 } from './lib.js';
import { createEngine, FPS } from './engine.js';
import { PAD, bakeDark, bakeGlow, bakeCream, bakeCold, bakeInkNoise, bakeVignette, bakeGrain } from './textures.js';
import { buildOpen } from './scenes_open.js';
import { buildRecord } from './scenes_record.js';
import { buildPlea } from './scenes_plea.js';
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
const INKNOISE = bakeInkNoise(W, H, U), VIG = bakeVignette(W, H), GRAIN = bakeGrain(W + 80, H + 80), GLOW = bakeGlow(W, H);
E.duration = DURATION; E.PAPER = PAPER; E.PAD = PAD; E.INK = INK; E.INKNOISE = INKNOISE;

// ---- scenes: each starts at t0 (the start of its entering transition) and runs to the next t0
const SCENES = [...buildOpen(E), ...buildRecord(E), ...buildPlea(E), ...buildEnd(E)].sort((a, b) => a.t0 - b.t0);
const HITS = [];                                                         // [frame, amplitude px @1280, length frames]: only physical impacts (a stamp, a page landing, rope, cover)
for (const s of SCENES) for (const [t, amp = 4, len = 5] of s.hits || []) HITS.push([Math.ceil(t * FPS - 1e-6), amp, len]);
const shakeAt = (f) => { let dx = 0, dy = 0, a = 0; for (const [f0, amp, len] of HITS) { const d = f - f0; if (d >= 0 && d < len) { const e = Math.pow(1 - d / len, 1.5); dx += amp * e * Math.cos(d * 2.6 + f0); dy += amp * e * Math.sin(d * 3.3 + f0 * 0.7); a = Math.max(a, amp); } } return [dx * U, dy * U, a * U]; };
const sceneIdx = (t) => { let k = 0; for (let i = 0; i < SCENES.length; i++) if (t >= SCENES[i].t0 - 1e-9) k = i; else break; return k; };

// ---- offscreen layers for rendering one scene at a time (two sets, so a transition can hold the outgoing and the incoming scene)
const mkLayer = () => { const c = mk(W, H), k = mk(W, H); const o = { c, g: c.getContext('2d'), k, ki: k.getContext('2d') }; return o; };
const LA = mkLayer(), LB = mkLayer();
const candle = (t) => 0.80 + 0.12 * noise1(t * 5.3, 4) + 0.07 * noise1(t * 13.1, 9);             // a candle's slow breathing, never a strobe

function resetCtx(c) { c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over'; c.filter = 'none'; c.shadowBlur = 0; c.shadowColor = 'rgba(0,0,0,0)'; c.textRendering = 'geometricPrecision'; c.fontKerning = 'normal'; c.letterSpacing = '0px'; c.textAlign = 'left'; c.textBaseline = 'alphabetic'; }

// draw scene sc at time t into layer L (background, content, ink layer with its dropout, candle)
function renderScene(sc, t, L) {
  resetCtx(L.g); resetCtx(L.ki); L.ki.clearRect(0, 0, W, H);
  E.g = L.g; E.ink = L.ki; E.f = Math.round(t * FPS); E.t = t; E.lt = t - sc.t0; E.sc = sc; E.over = [];
  if (sc.bg && sc.bg !== 'none') L.g.drawImage(PAPER[sc.bg], -PAD, -PAD); else if (sc.bg === 'none') L.g.clearRect(0, 0, W, H);
  if (sc.bg === 'dark') { L.g.save(); L.g.globalCompositeOperation = 'lighter'; L.g.globalAlpha = candle(t) * 0.42; L.g.drawImage(GLOW, 0, 0); L.g.restore(); }
  sc.draw(E, E.lt);
  L.ki.globalCompositeOperation = 'destination-out'; L.ki.drawImage(INKNOISE, 0, 0); L.ki.globalCompositeOperation = 'source-over';
  if (!sc.noInk) {
    if (sc.bg === 'cream' || sc.bg === 'cold') { L.g.save(); L.g.filter = `blur(${0.7 * U}px)`; L.g.globalAlpha = 0.4; L.g.drawImage(L.k, 0, 0); L.g.restore(); }       // ink spreads a hair into the fibres
    L.g.drawImage(L.k, 0, 0);
  }
  for (const fn of E.over) fn(L.g);
  if (sc.bg === 'cream') { L.g.save(); L.g.globalCompositeOperation = 'soft-light'; L.g.globalAlpha = 0.5 * (candle(t) - 0.5); L.g.drawImage(GLOW, 0, 0); L.g.restore(); }
}

// ---- transitions: composite outgoing layer A and incoming layer B onto the main canvas
const NZ = (() => { const w = Math.ceil(W / 3), h = Math.ceil(H / 3), a = new Float32Array(w * h), r = rng(5); const gw = 9, gh = 14, gv = Array.from({ length: (gw + 2) * (gh + 2) }, () => r()); const f = (t) => t * t * (3 - 2 * t);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { let s = 0, amp = 1, nrm = 0; for (let o = 0; o < 4; o++) { const fx = x / w * gw * (1 << o), fy = y / h * gh * (1 << o), ix = Math.floor(fx), iy = Math.floor(fy), ux = f(fx - ix), uy = f(fy - iy), idx = (xx, yy) => ((yy % (gh + 2)) * (gw + 2) + (xx % (gw + 2))); const v = (gv[idx(ix, iy)] * (1 - ux) + gv[idx(ix + 1, iy)] * ux) * (1 - uy) + (gv[idx(ix, iy + 1)] * (1 - ux) + gv[idx(ix + 1, iy + 1)] * ux) * uy; s += v * amp; nrm += amp; amp *= 0.5; } a[y * w + x] = s / nrm; }
  return { w, h, a }; })();
const MASK = mk(NZ.w, NZ.h), MASKG = MASK.getContext('2d'), RIM = mk(NZ.w, NZ.h), RIMG = RIM.getContext('2d'), TMP = mk(W, H), TMPG = TMP.getContext('2d');

function transition(sc, t, A, B) {
  const tr = sc.trans, p = clamp((t - sc.t0) / tr.dur), e = (ease[tr.ease || 'inOutCubic'] || ease.inOutCubic)(p);
  g.drawImage(A.c, 0, 0);
  const edgeShadow = (x0, y0, x1, y1, a, ext) => { const gr = g.createLinearGradient(x0, y0, x1, y1); gr.addColorStop(0, `rgba(0,0,0,${a})`); gr.addColorStop(1, 'rgba(0,0,0,0)'); return gr; };
  const dirv = { bottom: [0, 1], top: [0, -1], right: [1, 0], left: [-1, 0] }[tr.dir || 'bottom'];
  if (tr.kind === 'slideIn') {                                         // B arrives over A from `dir` (the page is laid on the desk / on the page below)
    const ox = dirv[0] * (1 - e) * W, oy = dirv[1] * (1 - e) * H, ext = 0.07 * H, a = 0.62 * (1 - 0.45 * e);
    g.save(); g.globalAlpha = 1; g.fillStyle = `rgba(0,0,0,${0.18 * Math.sin(Math.PI * e)})`; g.fillRect(0, 0, W, H); g.restore();
    if (dirv[1]) { const ey = dirv[1] > 0 ? oy : H + oy, sgn = dirv[1] > 0 ? -1 : 1; g.fillStyle = edgeShadow(0, ey, 0, ey + sgn * ext, a); g.fillRect(0, Math.min(ey, ey + sgn * ext), W, ext); }
    else { const ex = dirv[0] > 0 ? ox : W + ox, sgn = dirv[0] > 0 ? -1 : 1; g.fillStyle = edgeShadow(ex, 0, ex + sgn * ext, 0, a); g.fillRect(Math.min(ex, ex + sgn * ext), 0, ext, H); }
    g.drawImage(B.c, ox, oy);
  } else if (tr.kind === 'slideOut') {                                 // A leaves `dir`, uncovering B
    g.drawImage(B.c, 0, 0);
    const ox = dirv[0] * e * W, oy = dirv[1] * e * H, ext = 0.06 * H, a = 0.55 * (1 - 0.4 * e);
    if (dirv[1]) { const ey = dirv[1] > 0 ? oy : H + oy, sgn = dirv[1] > 0 ? -1 : 1; g.fillStyle = edgeShadow(0, ey, 0, ey + sgn * ext, a); g.fillRect(0, Math.min(ey, ey + sgn * ext), W, ext); }
    else { const ex = dirv[0] > 0 ? ox : W + ox, sgn = dirv[0] > 0 ? -1 : 1; g.fillStyle = edgeShadow(ex, 0, ex + sgn * ext, 0, a); g.fillRect(Math.min(ex, ex + sgn * ext), 0, ext, H); }
    g.drawImage(A.c, ox, oy);
  } else if (tr.kind === 'bleed') {                                    // ink spreads from a point (the tally) and turns the page to dark; B is seen through the stain
    const [cx, cy] = tr.at, rad = Math.hypot(Math.max(cx, W - cx), Math.max(cy, H - cy)) * 1.15, k = NZ.w / W, img = MASKG.createImageData(NZ.w, NZ.h), rim = RIMG.createImageData(NZ.w, NZ.h), d = img.data, r2 = rim.data, R = e * (rad + 0.35 * rad);
    for (let y = 0; y < NZ.h; y++) for (let x = 0; x < NZ.w; x++) {
      const dist = Math.hypot(x / k - cx, (y / k - cy) * 0.92), n = NZ.a[y * NZ.w + x], v = (R - dist - (n - 0.5) * 0.7 * rad) / (0.12 * rad), a = clamp(v), o = (y * NZ.w + x) * 4;
      d[o] = d[o + 1] = d[o + 2] = 255; d[o + 3] = Math.round(255 * a * a * (3 - 2 * a));
      const rv = clamp(1 - Math.abs(v - 0.1) / 0.9) * (v > -1.2 ? 1 : 0); r2[o] = 22; r2[o + 1] = 12; r2[o + 2] = 5; r2[o + 3] = Math.round(120 * rv * (a < 1 ? 1 : 0.0));
    }
    MASKG.putImageData(img, 0, 0); RIMG.putImageData(rim, 0, 0);
    g.save(); g.imageSmoothingEnabled = true; g.drawImage(RIM, 0, 0, W, H); g.restore();           // the wet dark rim in the page itself
    TMPG.globalCompositeOperation = 'source-over'; TMPG.clearRect(0, 0, W, H); TMPG.drawImage(B.c, 0, 0); TMPG.globalCompositeOperation = 'destination-in'; TMPG.imageSmoothingEnabled = true; TMPG.drawImage(MASK, 0, 0, W, H); TMPG.globalCompositeOperation = 'source-over';
    g.drawImage(TMP, 0, 0);
  } else {                                                             // 'fade': a dissolve, only for a change of world
    g.save(); g.globalAlpha = p; g.drawImage(B.c, 0, 0); g.restore();
  }
}

function renderFrame(f, t) {
  resetCtx(g);
  const k = sceneIdx(t), sc = SCENES[k], [sx, sy, amp] = shakeAt(f);
  g.save();
  if (amp > 0) { const s = 1 + (2 * amp + 2) / W; g.translate(W / 2 + sx, H / 2 + sy); g.scale(s, s); g.translate(-W / 2, -H / 2); }
  const inTrans = sc.trans && k > 0 && t < sc.t0 + sc.trans.dur;
  if (inTrans) { renderScene(SCENES[k - 1], t, LA); renderScene(sc, t, LB); transition(sc, t, LA, LB); }
  else { renderScene(sc, t, LA); g.drawImage(LA.c, 0, 0); }
  g.restore();
  g.drawImage(VIG, 0, 0);
  const r = rng(f * 7919 + 13); g.drawImage(GRAIN, -Math.floor(r() * 80), -Math.floor(r() * 80));
  if (DBG_SAFE) {
    g.save(); g.fillStyle = 'rgba(255,0,200,0.30)'; const x0 = SAFE.x0 * W, x1 = SAFE.x1 * W, y0 = SAFE.y0 * H, y1 = SAFE.y1 * H;
    g.fillRect(0, 0, W, y0); g.fillRect(0, y1, W, H - y1); g.fillRect(0, y0, x0, y1 - y0); g.fillRect(x1, y0, W - x1, y1 - y0);
    g.strokeStyle = 'rgba(0,255,255,0.95)'; g.lineWidth = 2; g.strokeRect(x0, y0, x1 - x0, y1 - y0); g.restore();
  }
}
// the engine reads E.g / E.ink while drawing; restore the main canvas for anything that runs outside renderScene
window.KF = { width: W, height: H, fps: FPS, duration: DURATION, canvas, shots: SCENES.map((s, i) => ({ name: s.name || 's' + i, dur: ((SCENES[i + 1] ? SCENES[i + 1].t0 : DURATION) - s.t0) })), render: async (i, t) => { renderFrame(i, t); } };
window.KF_READY = true;
