// NOOR · The Descent · Night Five · Iqra. Lantern Road style (painted 2.5D multiplane, motivated light), 16:9, 24 fps.
// Every frame is a pure function of (i, t): seeded painting, time-driven animation, no clocks. Sets are painted lazily, once each.
// The picture follows audio/mix.m4a through cues.json (never retimed). Shot list: shots.js and NOTES.md.
// Depiction rules: no prophet, angel, Companion or named person is ever drawn. Light, places and objects carry the story.
import * as THREE from 'three';
import { boot, drawText, ease, clamp, lerp, smoothstep } from '/harness/kit/film.js';
import { Post, Setup, DW, DH, fovV } from './kf.js';
import { buildShots, buildCaptions, buildLabels, FONT } from './shots.js';
import { SETS } from './sets/index.js';
import { drawOverlays } from './type.js';

const FILM = await (await fetch('./film.json')).json();
const CUES = await (await fetch('./cues.json')).json();
const SHOTS = buildShots(CUES, FILM.duration);
const CAPS = buildCaptions(CUES);
const LABELS = buildLabels(CUES);
let scene, camera, post, W, H, SC; const insts = new Map(); const tv = new THREE.Vector3();

const CAMD = { x: 0, y: 0, z: 0, pan: 0, tilt: 0, roll: 0, mm: 35 };
ease.glide = (u) => { const a = 0.25, v = 1 / (1 - a); return u < a ? v * u * u / (2 * a) : u < 1 - a ? v * (u - a / 2) : 1 - v * (1 - u) * (1 - u) / (2 * a); };
function camPose(sh, lt) {
  const ks = sh.cam; let a = ks[0], b = ks[ks.length - 1];
  if (ks.length === 1) b = a; else { for (let i = 0; i < ks.length - 1; i++) { if (lt <= ks[i + 1][0]) { a = ks[i]; b = ks[i + 1]; break; } } }
  const span = Math.max(1e-6, b[0] - a[0]); const u = clamp((lt - a[0]) / span); const k = (ease[b[2] || sh.ease || 'glide'] || ease.glide)(u);
  const o = {}; for (const key of Object.keys(CAMD)) o[key] = lerp(a[1][key] ?? CAMD[key], b[1][key] ?? CAMD[key], k);
  if (sh.breath) { const q = sh.breath; o.x += q * Math.sin(lt * 0.9) * 0.4; o.y += q * Math.sin(lt * 0.7 + 1) * 0.3; o.pan += 0.0006 * q * Math.sin(lt * 0.6); o.tilt += 0.0005 * q * Math.sin(lt * 0.8 + 2); }
  return o;
}
function applyCam(cam, c) { cam.fov = fovV(c.mm); cam.aspect = DW / DH; cam.position.set(c.x, c.y, c.z); cam.rotation.set(c.tilt, c.pan, c.roll, 'YXZ'); cam.updateProjectionMatrix(); cam.updateMatrixWorld(true); }
const sampleCams = (sh) => { const out = []; for (let i = 0; i <= 6; i++) { const c = new THREE.PerspectiveCamera(30, DW / DH, 0.1, 30000); applyCam(c, camPose({ ...sh, breath: 0 }, sh.dur * i / 6)); out.push(c); } return out; };
const shotAt = (t) => { let s = SHOTS[SHOTS.length - 1]; for (const x of SHOTS) if (t < x.t1) { s = x; break; } return s; };

function ensureSet(id) {
  let inst = insts.get(id); if (inst) { inst.used = performance.now(); return inst; }
  const def = SETS[id]; if (!def) throw new Error('no set ' + id);
  const S = new Setup(id); scene.add(S.group); const cams = SHOTS.filter((s) => s.set === id).flatMap(sampleCams);
  const t0 = performance.now(); const api = def(S, cams, { W, H, SHOTS, CUES }); inst = { S, api, used: performance.now(), id };
  for (const p of S.planes) { const tx = p.material.uniforms.map.value; if (tx.image && tx.image.getContext) tx.image.getContext('2d').getImageData(0, 0, 1, 1); post.r.initTexture(tx); }
  post.r.resetState(); post.glowTex.needsUpdate = true; post.detailTex.needsUpdate = true; post.overlayTex.needsUpdate = true;
  if (new URLSearchParams(location.search).get('prof')) console.log(`set ${id}: ${(performance.now() - t0).toFixed(0)} ms, planes ${S.planes.length}`);
  insts.set(id, inst);
  if (insts.size > 3) { let old = null; for (const v of insts.values()) if (v.id !== id && (!old || v.used < old.used)) old = v; if (old) { old.S.dispose(); insts.delete(old.id); } }
  return inst;
}

await boot({
  fps: FILM.fps, duration: FILM.duration, toneMapping: THREE.NoToneMapping,
  fonts: [['Cormorant Garamond', 'italic 400'], ['Cormorant Garamond', 400], ['Cinzel', 500], ['Amiri Quran', 400]],
  init: async (ctx) => {
    try { await document.fonts.load('40px "Amiri Quran"', 'ٱقۡرَأۡ بِٱسۡمِ'); } catch (e) {}
    W = ctx.W; H = ctx.H; SC = W / DW;
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x04060f); camera = new THREE.PerspectiveCamera(30, DW / DH, 0.1, 30000);
    post = new Post(ctx.renderer, scene, camera, W, H, { kr: 2 });
    window.__kf = { SHOTS, CAPS, LABELS, shotAt };
  },
  render: async (ctx, i, t) => {
    const sh = shotAt(t); const idx = SHOTS.indexOf(sh); const dz = sh.dissolve && idx > 0 && t - sh.t0 < sh.dissolve ? sh.dissolve : 0;
    if (dz) {
      const prev = SHOTS[idx - 1]; drawShot(ctx, prev, t, { text: false, hold: true });
      if (!copyCv) { copyCv = document.createElement('canvas'); copyCv.width = W; copyCv.height = H; copyG = copyCv.getContext('2d'); }
      copyG.setTransform(1, 0, 0, 1, 0, 0); copyG.clearRect(0, 0, W, H); copyG.drawImage(ctx.renderer.domElement, 0, 0, W, H);
      drawShot(ctx, sh, t, { text: true, under: copyCv, underA: 1 - ease.inOutSine(clamp((t - sh.t0) / dz)) });
    } else drawShot(ctx, sh, t, { text: true });
  },
});
let copyCv = null, copyG = null;

function drawShot(ctx, sh, t, { text = true, under = null, underA = 0, hold = false } = {}) {
  const inst = ensureSet(sh.set); const lt = hold ? Math.min(t - sh.t0, sh.dur + 1.5) : t - sh.t0;
  for (const v of insts.values()) v.S.group.visible = v === inst;
  applyCam(camera, camPose(sh, lt));
  const g = post.clearDetail(); post.clearGlow(); const og = post.clearOverlay();
  const world = new THREE.Vector3(), Kv = new THREE.Vector3();
  const F = { q: Object.fromEntries(new URLSearchParams(location.search)), t, lt, u: clamp(lt / sh.dur), shot: sh, cam: camera, S: inst.S, g, post, lights: [], amb: [1, 1, 1], bloom: 0.5, hal: 0.25, fade: 1, W, H, SC, SC0: 1, CUES,
    glow: () => post.glowOn(),
    P: (D, x, y) => { inst.S.world(x, y, D, tv).project(camera); return [(tv.x * 0.5 + 0.5) * DW, (-tv.y * 0.5 + 0.5) * DH]; },
    K: (D, x = DW / 2, y = DH / 2) => { const a = inst.S.world(x, y, D, world).clone().project(camera), b = inst.S.world(x + 40, y, D, Kv).project(camera); return ((b.x - a.x) * 0.5 * DW) / 40; },
  };
  inst.api.update(F);
  for (const p of inst.S.planes) { const d = p.userData; p.material.uniforms.uTime.value = t; const amp = d.drift != null ? d.drift * 11 : (/^sky/.test(d.name) ? 60 : 0);
    if (amp) p.position.x = d.base.x + amp * Math.sin((2 * Math.PI * t) / (d.drift != null ? 70 : 170) + (d.D % 7)) * d.D / inst.S.f; }
  let ov = false;
  if (under) { og.save(); og.setTransform(1, 0, 0, 1, 0, 0); og.globalAlpha = underA; og.drawImage(under, 0, 0, W, H); og.restore(); og.setTransform(post.sc, 0, 0, post.sc, 0, 0); ov = true; }
  if (text) ov = drawOverlays(og, F, { CAPS, LABELS, CUES, FILM }) || ov;
  if (ov) post.markOverlay();
  let fade = F.fade; if (sh.fadeIn) fade *= ease.inOutSine(clamp(lt / sh.fadeIn)); if (sh.fadeOut) fade *= 1 - ease.inOutSine(clamp((lt - (sh.dur - sh.fadeOut)) / sh.fadeOut));
  if (t < 0.6) fade *= ease.inOutSine(clamp(t / 0.6));
  { const left = FILM.duration - t; if (left < 0.6) fade *= ease.inOutSine(clamp(left / 0.6)); }
  post.render(t, { fade, lights: F.lights, amb: F.amb, bloom: F.bloom, hal: F.hal });
}
