// P13 "PIXEL VIGIL" — on a rain-soaked neon rooftop a watcher waits for a signal; across the street one amber window lights.
// Lane: retro / epic pixel art. Three.js scene -> kit `pixel` grade (320 px wide, 7 levels/channel, Bayer dither). See NOTES.md.
import * as THREE from 'three';
import { boot, makeComposer, clamp, fovFromMM } from '/harness/kit/film.js';
import { P, K } from './palette.js';
import { skyDome } from './city.js';
import { buildWorld, WATCHER, BL_X0 } from './world.js';
import { poseWatcher } from './watcher.js';
import { paintOverlay } from './rain.js';

const SHOTS = [
  { name: 'S1 wide parallax truck R->L', dur: 87 / 24 },   // frames 0-86
  { name: 'S2 MS low angle, locked', dur: 86 / 24 },        // frames 87-172 (cut at 7.2 s = f172.8 -> f173)
  { name: 'S3 telephoto MCU + slot, locked', dur: 67 / 24 }, // frames 173-239
];
const CUT2 = 87, CUT3 = 173, LIGHT = 130;
let scene, camera, post, world, sky, W, H;

// ---- S1: pan (lens shift, all depths equally) + truck (per-layer parallax), both in whole art pixels
const F1 = 210, PAN = 70, TRUCK = 130, DNEAR = 7.3, PAN_END = 74;
function prof(u, a = 0.1, c = 0.7) { const v = 1 / (a / 2 + (c - a) + (1 - c) / 2); if (u < a) return 0.5 * v * u * u / a; if (u < c) return 0.5 * v * a + v * (u - a); const d = 1 - c, x = u - c; return 0.5 * v * a + v * (c - a) + v * x - 0.5 * v * x * x / d; }
const CAMS = [
  { pos: [-1.75, 1.5, 8.0], yaw: 0, pitch: 4, mm: 28 },
  { pos: [0.9, 0.5, 4.8], yaw: 0, pitch: 13, mm: 35 },
  { pos: [2.0, 0.7, 6.7], yaw: 11, pitch: 8, mm: 85 },
];
function setCam(c) {
  camera.position.set(...c.pos); const y = c.yaw * Math.PI / 180, p = c.pitch * Math.PI / 180;
  camera.lookAt(camera.position.x - Math.sin(y) * Math.cos(p) * 100, camera.position.y + Math.sin(p) * 100, camera.position.z - Math.cos(y) * Math.cos(p) * 100);
  camera.fov = fovFromMM(c.mm); camera.updateProjectionMatrix();
}
function windowW(f, t) { // the amber accent: dark until LIGHT, then ignition flash, settle, and a gentle pulse in S3
  const { wMat, wHalo, group } = world.W; const u = wHalo.userData.mat.uniforms; const mull = group.children[2].material;
  if (f < LIGHT) { wMat.color.setHex(K(0, 0, 1)); mull.color.setHex(K(0, 1, 2)); u.uI.value = 0; return; }
  mull.color.setHex(K(4, 2, 0));
  if (f < LIGHT + 2) { wMat.color.setHex(P.amber); u.uI.value = 0.35; }
  else if (f < LIGHT + 6) { wMat.color.setHex(P.amberHot); u.uI.value = 1.0; }
  else { const p = f >= CUT3 ? 0.5 + 0.5 * Math.sin(2 * Math.PI * (t - CUT3 / 24) / 1.7) : 0.3; wMat.color.setHex(p > 0.82 ? P.amberHot : P.amber); u.uI.value = 0.78 + 0.22 * p; }
}

const _v = new THREE.Vector3();
function toArt(x, y, z) { _v.set(x, y, z).project(camera); return [(_v.x * 0.5 + 0.5) * 320, (1 - (_v.y * 0.5 + 0.5)) * 180, _v.z]; }
function reflections(f) { // screen-space reflection streaks of the B1 neon in the wet roof, just below the parapet; skipped behind the watcher
  const par = toArt(0, 0.5, 0.1)[1]; const wx = toArt(WATCHER.x, 1.0, WATCHER.z); const wHalf = f < CUT2 ? 10 : f < CUT3 ? 30 : 34; const out = [];
  if (par > 176) return out;
  for (const s of world.neon.signs) { if (s.g.parent.name !== 'b1') continue; s.g.getWorldPosition(_v); const [x, , z] = toArt(_v.x, _v.y, _v.z); if (x < 2 || x > 318 || Math.abs(x - wx[0]) < wHalf) continue;
    const big = s.kind === 'ring' ? 1.3 : 1; out.push({ x, y0: par, len: Math.min(30, (f < CUT2 ? 14 : 22) * big), hex: s.hexNow, hex2: s.hex2Now, dim: s.dim, level: s.level, wide: s.kind === 'ring' || s.kind === 'eq' }); }
  return out;
}
await boot({
  fps: 24, shots: SHOTS, fonts: [], toneMapping: THREE.NoToneMapping,
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; scene = new THREE.Scene(); scene.background = new THREE.Color(P.skyTop);
    camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 1500);
    sky = skyDome(); scene.add(sky); world = buildWorld(scene);
    post = makeComposer(ctx.renderer, scene, camera, { grade: 'pixel', finish: { saturation: 1.0, contrast: 1.0, grain: 0.0, vignette: 0.0, modeParams: [320, 0.08, 0], palette: [6, 6, 6] }, overlay: true });
    post.overlay.tex.colorSpace = THREE.NoColorSpace; // overlay colours are authored as final display values
    window.__p13 = { world, camera, post };
  },
  render: async (ctx, i, t) => {
    const f = i, shot = f < CUT2 ? 0 : f < CUT3 ? 1 : 2, blk = W / 320;
    poseWatcher(world.watcher, f, { x0: WATCHER.x, z0: WATCHER.z, windowOn: LIGHT });
    world.neon.update(f); world.beacons.update(t); world.roof.update(f); windowW(f, t);
    world.bl.position.x = BL_X0 - 0.805 * Math.floor(f / 7);
    setCam(CAMS[shot]);
    if (shot === 0) {
      const r = 1 - prof(clamp(f / PAN_END)); camera.setViewOffset(W, H, -Math.round(PAN * r) * blk, 0, W, H);
      for (const L of world.layers) L.g.position.x = Math.round(TRUCK * (DNEAR / L.depth) * r) * L.depth / F1;
    } else { camera.clearViewOffset(); for (const L of world.layers) L.g.position.x = 0; }
    sky.position.copy(camera.position); sky.material.uniforms.uT.value = Math.floor(f / 6) * 0.012;
    paintOverlay(post.overlay.ctx, W, H, f, { rain: 1, vignette: 0.2, refl: reflections(f) });
    post.render(t);
  },
});
