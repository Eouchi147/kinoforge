// P09 "PAPER KINGDOM" — cut-paper shadow theatre, 10 s @ 24 fps (240 f), 1280x720.
// Pure Canvas 2D drawn into the kit overlay over a black three.js scene, so the kit's finish pass gives ONE grade
// (sepia tuned warm: saturation 0.5, grain 0.04, vignette 0.35). Multiplane camera: every paper card has a depth d and
// the camera (k zoom, cx/cy truck, cz dolly, tx/ty tilt) maps it with true parallax. Characters animate on 2s.
// Deterministic: all animation keyed to the integer frame; seeded shapes built once. Authoring space is 1280x720.
import * as THREE from 'three';
import { boot, makeComposer, ease, clamp, lerp, smoothstep, noise1 } from '/harness/kit/film.js';
import { VIEW, Compositor, rgb, mk, ctx2d } from './paper.js';
import { PAL, initStyles, buildPuppets, drawKing, drawSoldier, drawDragon, dragonMouth, drawFire, drawHand, drawBird, drawFolded } from './puppets.js';
import { DEPTH, buildStage, drawScreen, drawScreenCU, drawFar, drawNear, drawMid, drawGround, drawFrontLeft, drawFrontRight, drawGrass } from './stage.js';

// ================================================================ timing (integer frames: cuts and audio cues share exact times)
const FPS = 24, SF = [72, 72, 58, 38];                      // 240 f = 10.000 s
const S0 = [0, 72, 144, 202];
const SHOTS = [
  { name: 'S1 WS 35mm locked: the king commands, the army marches L-R', dur: SF[0] / FPS },
  { name: 'S2 EWS low 28mm dolly-in: the dragon rises, breathes fire', dur: SF[1] / FPS },
  { name: 'S3 CU 85mm locked: a child folds the dragon into a bird', dur: SF[2] / FPS },
  { name: 'S4 WS 40mm locked tableau: the bird flies into the light', dur: SF[3] / FPS },
];
const shotOf = (i) => { let n = 0; while (n < 3 && i >= S0[n + 1]) n++; return { n, f: i - S0[n] }; };
const on2 = (i) => i - (i & 1);                             // puppets: every drawing held for 2 frames
function keys(K, f) {                                       // [[frame, value, easeIntoThisKey], ...]
  if (f <= K[0][0]) return K[0][1];
  for (let j = 1; j < K.length; j++) if (f <= K[j][0]) { const [fa, va] = K[j - 1], [fb, vb, e = ease.inOutSine] = K[j]; return lerp(va, vb, e((f - fa) / (fb - fa))); }
  return K[K.length - 1][1];
}
export const BEAT = 60 / 108, T0 = 3.0 - 4 * BEAT;          // toy march: step-off at 0.778 s, 4 beats, the 5th lands ON the S2 cut

// ================================================================ multiplane camera
function camFor(n, f) {
  if (n === 0) return { k: 1, cx: 0, cy: 0, cz: 0, tx: 0, ty: 0 };
  if (n === 1) { const t = f / FPS, te = t < 0.5 ? t * t : t - 0.25; return { k: 0.8, cx: 300, cy: 70, cz: 1 - 1 / (1 + 0.02 * te), tx: 0, ty: 150 }; } // dolly 2 %/s on the army plane (on 1s)
  return { k: 0.84, cx: 120, cy: -20, cz: 0, tx: 0, ty: 64 };            // S4: wider, horizon lower: room for the bird to rise into the light
}
function setLayer(g, cam, d) {
  const m = cam.k * d / (d - cam.cz), ox = -cam.k * cam.cx / (d - cam.cz) + cam.tx, oy = -cam.k * cam.cy / (d - cam.cz) + cam.ty, s = VIEW.dpr;
  g.setTransform(s * m, 0, 0, s * m, s * (640 * (1 - m) + ox), s * (360 * (1 - m) + oy));
}

// ================================================================ the KING (on his rock, front layer)
function kingState(i, n) {
  const k = on2(i); let arm, lean;
  if (n <= 1) {      // anticipation dip back (f6-12), raise with overshoot (f12-20), settle (f20-28), then a slow breath
    arm = keys([[6, 0.2], [12, -0.16, ease.outQuad], [20, 2.55, ease.inOutCubic], [24, 2.26, ease.outQuad], [28, 2.35]], k) + (k > 28 ? 0.03 * Math.sin((k - 28) / 20 * Math.PI) : 0);
    lean = keys([[6, 0], [12, -0.04], [20, 0.05], [28, 0.025]], k);
  } else {
    const f = k - S0[3];
    arm = keys([[1, 2.35], [9, 0.04, ease.inOutCubic], [12, 0.27, ease.outQuad], [14, 0.2]], f);       // falls, small bounce, settled by S4 f14
    lean = keys([[1, 0.025], [9, -0.02], [14, 0]], f);
  }
  return { x: 352, y: 492, s: 1, arm, lean };
}
// ================================================================ the ARMY (7 identical soldiers, staggered phase)
const X0 = [446, 511, 580, 645, 714, 780, 850], PH = [0, 2, 4, 0, 2, 4, 0], STRIDE = 40, GY = 578;
function soldierState(j, i, n) {
  const f = on2(i) - PH[j], b = (f / FPS - T0) / BEAT; let x = X0[j], pose = 'H', bob = 0, spear = 0, lean = 0;
  if (b >= 0 && b < 4) { const k = Math.floor(b), p = b - k; pose = p < 0.5 ? 'A' : 'B'; bob = p < 0.5 ? 1.2 : -2.2; x += STRIDE * (k + ease.inOutSine(p)); spear = 0.05 * Math.sin(p * Math.PI * 2); lean = 0.03; }
  else if (b >= 4) { const p = b - 4; x += STRIDE * 4 + 6 * smoothstep(0, 0.5, p); pose = p < 0.45 ? 'A' : 'H'; bob = p < 0.45 ? 1.2 : 0; }
  else if (b > -0.6) bob = 1.8 * Math.sin((b + 0.6) / 0.6 * Math.PI);                 // anticipation: a small dip before the step-off
  if (n === 1) {
    const f2 = on2(i) - S0[1];
    spear = keys([[14 + 2 * j, 0], [22 + 2 * j, 0.87, ease.outBack]], f2);
    if (f2 >= 24) spear += (f2 < 48 ? 0.03 : 0.065) * noise1(on2(i) * 1.9, j * 3.1);   // the spears tremble (on 2s)
    lean = -0.06 * smoothstep(48, 54, f2);
  } else if (n === 3) {
    const f4 = on2(i) - S0[3];
    spear = keys([[0, 0.87], [1 + j, 0.87], [7 + j, 1.75, ease.inOutCubic]], f4) + 0.04 * (1 - smoothstep(0, 6, f4)) * noise1(on2(i) * 1.9, j * 3.1);   // all lowered by S4 f13
    lean = -0.06 * (1 - smoothstep(2, 12, f4));
  }
  return { x, y: GY, s: 1, pose, bob, spear, lean };
}
// ================================================================ the DRAGON (S2), base hidden behind the front-right hillock
export const DS = 1.6, BX = 1350, BY = 760;
const RISEN = [-1.54, -1.68, -1.95, -2.41, -2.93, 2.79], COIL = [-1.58, -1.6, -1.66, -1.78, -1.95, -2.3], REAR = [0, 0, 0.04, 0.1, 0.18, 0.32];
const WF = [1.35, 2.7], WS = [-1.25, -0.2];
export function dragonPose(f) {     // f = S2-local frame (on 2s); f may exceed 71 for the CU (held end pose)
  const rise = keys([[4, 0], [36, 1.04, ease.inOutCubic], [44, 1.0]], f);
  const rear = keys([[36, 0], [46, 1], [48, -0.7, ease.outQuad], [56, -0.45], [72, -0.35]], f);
  const ang = RISEN.map((r, k) => { const u = clamp((rise - 0.07 * k) / (1 - 0.07 * 5)); return lerp(COIL[k], r, rise >= 1 ? rise : ease.inOutSine(u)) + REAR[k] * rear; });
  const br = f > 44 ? 0.035 * Math.sin((f - 44) / 30 * Math.PI * 2) : 0;
  const w = (lag, da) => [keys([[24 + lag, WF[0]], [38 + lag, WS[0] + da - 0.12, ease.inOutCubic], [44 + lag, WS[0] + da]], f) + br, keys([[28 + lag, WF[1]], [42 + lag, WS[1] - 0.2, ease.inOutCubic], [48 + lag, WS[1]]], f) + br * 1.5];
  return { ang, dy: (1 - Math.min(1, rise)) * 1000, jaw: keys([[0, 0.1], [36, 0.16], [46, 0.02], [48, 0.62, ease.outQuad], [56, 0.48], [72, 0.4]], f), wN: w(0, 0), wF: w(3, -0.24), claw: 2.1 + 0.5 * smoothstep(30, 48, f) };
}
const fireAmt = (f) => keys([[46, 0], [48, 0.55, ease.outCubic], [54, 1, ease.outCubic], [58, 1], [66, 0, ease.inQuad]], f);   // bursts ON f120 with the whoosh

// ================================================================ S3: the CU fold (shape swaps on 2s with 6-frame holds)
export const FOLD = { d1: 22, d2: 32, bird: 42 };          // S3-local frames of the three creases (= snaps in audio.py)
const CU = { x: 640, y: 352, s: 1.7, ox: -20, oy: -320 }, BIRD_CU = { x: 640, y: 350, s: 2.0 };
const cuXf = (lg) => { const s = VIEW.dpr * CU.s; lg.setTransform(s, 0, 0, s, VIEW.dpr * (CU.x - CU.s * CU.ox), VIEW.dpr * (CU.y - CU.s * CU.oy)); };
const foldStage = (f) => f < FOLD.d1 - 2 ? 0 : f < FOLD.d1 ? 0.5 : f < FOLD.d2 - 2 ? 1 : f < FOLD.d2 ? 1.5 : f < FOLD.bird - 2 ? 2 : f < FOLD.bird ? 2.5 : 3;
function handsAt(f) {
  const enter = keys([[0, 0], [12, 1, ease.outCubic]], f);
  const stage = f < FOLD.d1 ? 0 : f < FOLD.d2 ? 1 : f < FOLD.bird ? 2 : 3;
  const G = [[[471, 528, 0.3], [798, 622, -0.45]], [[474, 524, 0.3], [790, 616, -0.43]], [[548, 512, 0.25], [735, 512, -0.25]], [[550, 514, 0.22], [732, 512, -0.22]]][stage];
  const antic = [FOLD.d1 - 4, FOLD.d2 - 4, FOLD.bird - 4].some((a) => f >= a && f < a + 2) ? 1 : 0;   // 2-frame press before each crease
  const open = smoothstep(48, 52, f);
  const hand = (k, start) => ({ x: lerp(start[0], G[k][0], enter) + (k ? -6 : 6) * antic + (k ? 10 : -10) * open, y: lerp(start[1], G[k][1], enter) + 8 * antic + 10 * open, rot: G[k][2] + (k ? 0.06 : -0.06) * antic + (k ? 0.1 : -0.1) * open,
    s: 1.35, mirror: k === 0, curl: lerp(0.05, 0.45, smoothstep(12, 16, f)) - 0.32 * open, pinch: lerp(0, 0.8, smoothstep(12, 16, f)) - 0.55 * open, spread: 0.35 * (1 - smoothstep(10, 16, f)) + 0.25 * open });
  return [hand(0, [180, 940]), hand(1, [1120, 980])];
}

// ================================================================ boot (optional ?prof=1 logs per-layer CPU time)
const PROF = new URLSearchParams(location.search).get('prof'); let _pt = 0;
const tick = (name) => { if (!PROF) return; const now = performance.now(); if (name) console.log('prof', name, (now - _pt).toFixed(1)); _pt = now; };
let post, W, H, comp, G, M;
await boot({
  fps: FPS, shots: SHOTS, fonts: [],
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; VIEW.dpr = W / 1280;
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x000000);
    const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 10);
    post = makeComposer(ctx.renderer, scene, camera, { grade: 'sepia', finish: {
      saturation: 0.5, grain: 0.04, vignette: 0.35, contrast: 1.06, halation: 0.2, halationThreshold: 0.8,
      shadowTint: [0.035, 0.006, -0.03], highlightTint: [0.09, 0.04, -0.04] } });
    M = mk(W, H); G = ctx2d(M); comp = new Compositor(W, H);   // all 2D work on CPU-raster canvases; one copy into the overlay per frame
    initStyles(comp.lg); buildPuppets(); buildStage();
  },
  render: async (ctx, i, t) => {
    const g = G; g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; g.filter = 'none';
    g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    const { n, f } = shotOf(i);
    if (n === 2) drawCU(g, i, f); else drawStage(g, i, n, f);
    const ov = post.overlay.ctx; ov.setTransform(1, 0, 0, 1, 0, 0); ov.globalCompositeOperation = 'copy'; ov.drawImage(M, 0, 0); ov.globalCompositeOperation = 'source-over'; tick('copy');
    const _t0 = performance.now(); post.render(t); if (PROF) console.log('prof post', (performance.now() - _t0).toFixed(1));
  },
});

function drawStage(g, i, n, f) {
  const cam = camFor(n, f), f2 = on2(i) - S0[n]; tick();
  let B = 1; if (n === 1) B = 1 - 0.12 * smoothstep(4, 36, f) + 0.12 * fireAmt(f2); else if (n === 3) B = 1 + 0.2 * ease.inOutSine(clamp(f / 24));
  setLayer(g, cam, DEPTH.screen); drawScreen(g, B); tick('screen');
  comp.layer(g, (lg) => { setLayer(lg, cam, DEPTH.far); drawFar(lg); }, { mode: 'multiply', off: [-2.5, 2], blur: 3, shadow: 'rgba(70,24,6,0.25)' }); tick('far');
  comp.layer(g, (lg) => { setLayer(lg, cam, DEPTH.near); drawNear(lg); }, { mode: 'multiply', off: [-3, 2.5], blur: 3.5, shadow: 'rgba(56,18,4,0.3)' });
  comp.layer(g, (lg) => { setLayer(lg, cam, DEPTH.mid); drawMid(lg, on2(i)); }, { mode: 'multiply', off: [-3.5, 3], blur: 4, shadow: 'rgba(44,13,3,0.36)' }); tick('mid');
  if (n === 1) {
    const dp = dragonPose(f2);
    comp.layer(g, (lg) => { setLayer(lg, cam, DEPTH.dragon); lg.translate(BX, BY + dp.dy); lg.scale(DS, DS); drawDragon(lg, dp); }, { off: [-5, 4], blur: 5, shadow: 'rgba(30,9,2,0.5)' });
    const fa = fireAmt(f2);
    if (fa > 0) {
      const m = dragonMouth(dp); setLayer(g, cam, DEPTH.dragon); g.translate(BX + m[0] * DS, BY + dp.dy + m[1] * DS); g.rotate(dp.ang[5] - 0.12);
      const gl = g.createRadialGradient(170, 0, 0, 170, 0, 320); gl.addColorStop(0, `rgba(255,150,50,${0.32 * fa})`); gl.addColorStop(1, 'rgba(255,120,30,0)');
      g.globalCompositeOperation = 'lighter'; g.fillStyle = gl; g.fillRect(-200, -340, 720, 680); g.globalCompositeOperation = 'source-over';
      g.scale(DS * 0.85, DS * 0.85); drawFire(g, fa, Math.floor(f2 / 2));
    }
  }
  comp.layer(g, (lg) => { setLayer(lg, cam, DEPTH.army); drawGround(lg); }, { mode: 'multiply', off: [-4, 3], blur: 4, shadow: 'rgba(36,11,2,0.4)' });
  if (n === 3) {
    const f4 = on2(i) - S0[3], u = clamp(f4 / 22), seq = ['up', 'mid', 'down', 'down', 'mid', 'up'];
    const wing = f4 < 22 ? seq[Math.floor(f4 / 2) % 6] : 'mid';
    const bx = lerp(700, 790, ease.inOutSine(u)) + 14 * Math.sin(u * Math.PI), by = lerp(500, 292, ease.inOutSine(u)) - 0.6 * Math.max(0, f4 - 22);
    comp.layer(g, (lg) => { lg.setTransform(VIEW.dpr, 0, 0, VIEW.dpr, 0, 0); drawBird(lg, { x: bx, y: by, s: 0.86, rot: -0.12 * Math.sin(u * Math.PI), wing }); }, { off: [-4, 3.5], blur: 4, shadow: 'rgba(40,12,2,0.35)' });
  }
  comp.layer(g, (lg) => { setLayer(lg, cam, DEPTH.army); for (let j = 0; j < 7; j++) drawSoldier(lg, soldierState(j, i, n)); }, { off: [-4.5, 3.5], blur: 4, shadow: 'rgba(30,9,2,0.5)' }); tick('soldiers');
  comp.layer(g, (lg) => { setLayer(lg, cam, DEPTH.front); drawFrontLeft(lg); drawFrontRight(lg); drawKing(lg, kingState(i, n)); }, { off: [-5, 4], blur: 5, shadow: 'rgba(30,9,2,0.5)' }); tick('front');
  comp.layer(g, (lg) => { setLayer(lg, cam, DEPTH.grass); drawGrass(lg); }, { off: [-6, 5], blur: 6, shadow: 'rgba(30,9,2,0.45)' }); tick('grass');
}

function drawCU(g, i, f) {
  const f3 = on2(i) - S0[2], s = VIEW.dpr;
  g.setTransform(s, 0, 0, s, 0, 0); drawScreenCU(g, 1);
  comp.layer(g, (lg) => { lg.setTransform(s * 1.7, 0, 0, s * 1.7, s * -560, s * -186); drawFar(lg); }, { mode: 'multiply', shadow: null, defocus: 7 });
  const stage = foldStage(f3), tilt = [FOLD.d1 - 4, FOLD.d2 - 4, FOLD.bird - 4].some((a) => f3 >= a && f3 < a + 2) ? 0.03 : 0;
  comp.layer(g, (lg) => {
    if (stage < 2) { cuXf(lg); lg.rotate(tilt); drawFolded(lg, dragonPose(72 + f3), stage); }
    else { lg.setTransform(s, 0, 0, s, 0, 0); lg.translate(BIRD_CU.x, BIRD_CU.y); lg.rotate(tilt); drawBird(lg, { x: 0, y: -6 * smoothstep(48, 52, f3), s: BIRD_CU.s, rot: 0, wing: 'rest', stage: stage === 2 ? 'd2' : stage === 2.5 ? 'ib3' : undefined }); }
  }, { off: [-6, 5], blur: 7, shadow: 'rgba(30,9,2,0.45)' });
  const hands = handsAt(f3);
  comp.layer(g, (lg) => { lg.setTransform(s, 0, 0, s, 0, 0); for (const h of hands) drawHand(lg, h); }, { off: [-9, 7], blur: 10, shadow: 'rgba(25,8,2,0.5)' });
}
