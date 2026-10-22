// NOOR · Tonight's Juz · Juz Thirty (Juz Amma). Lantern Road style, 16:9, painted 2.5D multiplane. Shot list: shots.js and NOTES.md.
// Every frame is a pure function of (i, t): seeded painting, time-driven animation, no clocks. Painted sets are built lazily, once per set.
// Layers: painted planes (relit by lamps) -> Kuwahara + bloom + grade (kf.js Post) -> detail layer (objects, lanterns) -> crisp overlay
// (captions, Arabic, titles, teaching graphics; never painterly, never covered by the grade).
import * as THREE from 'three';
import { boot, drawText, ease, clamp, lerp, smoothstep } from '/harness/kit/film.js';
import { Post, Setup, DW, DH, fovV } from './kf.js';
import { buildShots, buildCaptions } from './shots.js';
import { drawGfx } from './gfx.js';
import { SETS } from './sets/index.js';

const FILM = await (await fetch('./film.json')).json();
const CUES = await (await fetch('./cues.json')).json();
const SHOTS = buildShots(CUES, FILM.duration);
const CAPS = buildCaptions(CUES);
let scene, camera, post, W, H, SC; const insts = new Map(); const tv = new THREE.Vector3();

const CAMD = { x: 0, y: 0, z: 0, pan: 0, tilt: 0, roll: 0, mm: 35 };
ease.glide = (u) => { const a = 0.25, v = 1 / (1 - a); return u < a ? v * u * u / (2 * a) : u < 1 - a ? v * (u - a / 2) : 1 - v * (1 - u) * (1 - u) / (2 * a); };
function camPose(sh, lt) {
  const ks = sh.cam; let a = ks[0], b = ks[ks.length - 1];
  if (ks.length === 1) b = a; else { for (let i = 0; i < ks.length - 1; i++) { if (lt <= ks[i + 1][0]) { a = ks[i]; b = ks[i + 1]; break; } } }
  const span = Math.max(1e-6, b[0] - a[0]); const u = clamp((lt - a[0]) / span); const k = (ease[b[2] || sh.ease || 'glide'] || ease.glide)(u);
  const o = {}; for (const key of Object.keys(CAMD)) o[key] = lerp(a[1][key] ?? CAMD[key], b[1][key] ?? CAMD[key], k);
  if (sh.breath) { const q = sh.breath; o.x += q * Math.sin(lt * 0.9) * 0.25; o.y += q * Math.sin(lt * 0.7 + 1) * 0.18; o.pan += 0.0005 * q * Math.sin(lt * 0.6); o.tilt += 0.0004 * q * Math.sin(lt * 0.8 + 2); }
  return o;
}
function applyCam(cam, c) { cam.fov = fovV(c.mm); cam.aspect = DW / DH; cam.position.set(c.x, c.y, c.z); cam.rotation.set(c.tilt, c.pan, c.roll, 'YXZ'); cam.updateProjectionMatrix(); cam.updateMatrixWorld(true); }
const sampleCams = (sh) => { const out = []; for (let i = 0; i <= 6; i++) { const c = new THREE.PerspectiveCamera(30, DW / DH, 0.1, 60000); applyCam(c, camPose({ ...sh, breath: 0 }, sh.dur * i / 6)); out.push(c); } return out; };
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

let copyCv = null, copyG = null;
await boot({
  fps: FILM.fps, duration: FILM.duration, toneMapping: THREE.NoToneMapping,
  fonts: [['Cormorant Garamond', 'italic 400'], ['Cormorant Garamond', 400], ['Cormorant Garamond', 'italic 500'], ['Cinzel', 500], ['Amiri Quran', 400]],
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; SC = W / DW;
    try { await document.fonts.load('400 40px "Amiri Quran"', 'عَمَّ'); } catch (e) { console.log('amiri failed', e); }
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x04060f); camera = new THREE.PerspectiveCamera(30, DW / DH, 0.1, 60000);
    post = new Post(ctx.renderer, scene, camera, W, H, { kr: 2 });
    window.__kf = { SHOTS, CAPS, shotAt, camPose };
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

function drawShot(ctx, sh, t, { text = true, under = null, underA = 0, hold = false } = {}) {
  const inst = ensureSet(sh.set); const lt = hold ? Math.min(t - sh.t0, sh.dur) : t - sh.t0;
  for (const v of insts.values()) v.S.group.visible = v === inst;
  applyCam(camera, camPose(sh, lt));
  const g = post.clearDetail(); post.clearGlow(); const og = post.clearOverlay();
  const world = new THREE.Vector3(), Kv = new THREE.Vector3();
  const F = { q: Object.fromEntries(new URLSearchParams(location.search)), t, lt, u: clamp(lt / sh.dur), shot: sh, cam: camera, S: inst.S, g, og, post, lights: [], amb: [1, 1, 1], bloom: 0.5, hal: 0.25, fade: 1, W, H, SC, CUES,
    glow: () => post.glowOn(),
    P: (D, x, y) => { inst.S.world(x, y, D, tv).project(camera); return [(tv.x * 0.5 + 0.5) * DW, (-tv.y * 0.5 + 0.5) * DH]; },
    K: (D, x = DW / 2, y = DH / 2) => { const a = inst.S.world(x, y, D, world).clone().project(camera), b = inst.S.world(x + 40, y, D, Kv).project(camera); return ((b.x - a.x) * 0.5 * DW) / 40; },
  };
  inst.api.update(F);
  let ovSet = !!F.ov;
  for (const p of inst.S.planes) { const d = p.userData; p.material.uniforms.uTime.value = t; if (d.drift) p.position.x = d.base.x + d.drift * 11 * Math.sin((2 * Math.PI * t) / 70 + (d.D % 7)) * d.D / inst.S.f; }
  let ov = ovSet;
  if (under) { og.save(); og.setTransform(1, 0, 0, 1, 0, 0); og.globalAlpha = underA; og.drawImage(under, 0, 0, W, H); og.restore(); og.setTransform(post.sc, 0, 0, post.sc, 0, 0); ov = true; }
  if (text) {
    if (sh.gfx && drawGfx(og, F, sh.gfx)) ov = true;
    if (sh.card) { ov = true; cardDraw(og, sh, t); }
    for (const c of CAPS) { if (sh.noCap && sh.noCap.includes(c.id)) continue; const a = smoothstep(c.in, c.in + 0.3, t) * (1 - smoothstep(c.out - 0.3, c.out, t)); if (a > 0.003) { ov = true; capDraw(og, c.text, a, sh.capShade ?? 0.45); } }
  }
  if (ov) post.markOverlay();
  let fade = F.fade; if (sh.fadeIn) fade *= ease.inOutSine(clamp(lt / sh.fadeIn)); if (sh.fadeOut) fade *= 1 - ease.inOutSine(clamp((lt - (sh.dur - sh.fadeOut)) / sh.fadeOut));
  if (t < 0.6) fade *= ease.inOutSine(clamp(t / 0.6)); if (t > FILM.duration - 0.6) fade *= ease.inOutSine(clamp((FILM.duration - t) / 0.6));
  post.render(t, { fade, lights: F.lights, amb: F.amb, bloom: F.bloom, hal: F.hal });
}

// ---- type
function capDraw(og, text, a, shade = 0.45) {
  const font = 'italic 400 31px "Cormorant Garamond"'; const lines = wrap(og, text, 980, font); const y0 = 648 - (lines.length - 1) * 19;
  og.save(); const gr = og.createLinearGradient(0, 560, 0, 720); gr.addColorStop(0, 'rgba(4,4,14,0)'); gr.addColorStop(1, `rgba(4,4,14,${shade * a})`); og.fillStyle = gr; og.fillRect(0, 560, DW, 160); og.restore();
  lines.forEach((l, i) => drawText(og, l, { x: DW / 2, y: y0 + i * 38, font, color: '#efe6d3', alpha: a, spacing: 0.4, shadow: 12, shadowColor: 'rgba(3,3,12,0.95)' }));
}
function wrap(g, text, maxW, font) { g.save(); g.font = font; const words = text.split(' '); const lines = []; let cur = ''; for (const w of words) { const tt = cur ? cur + ' ' + w : w; if (g.measureText(tt).width > maxW && cur) { lines.push(cur); cur = w; } else cur = tt; } if (cur) lines.push(cur); g.restore(); return lines; }
// title and end cards
function cardDraw(og, sh, t) {
  const c = sh.card; const lt = t - c.at; if (lt < 0) return; const len = (c.until ?? sh.t1) - c.at;
  const fo = 1 - smoothstep(len - (c.out ?? 0.8), len, lt); const A = (d) => ease.outCubic(clamp((lt - d) / 1.1)) * fo;
  const y = c.y ?? 300;
  drawText(og, 'NOOR', { x: DW / 2, y, font: '500 66px "Cinzel"', color: '#ecd9a8', alpha: A(0.2), spacing: 22, shadow: 18, shadowColor: 'rgba(3,3,12,0.9)' });
  const wl = 300 * A(0.9); og.save(); og.globalAlpha = 0.75 * A(0.9); og.fillStyle = '#c9a227'; og.fillRect(DW / 2 - wl / 2, y + 44, wl, 1.5); og.restore();
  drawText(og, c.line1, { x: DW / 2, y: y + 90, font: 'italic 400 44px "Cormorant Garamond"', color: '#efe6d3', alpha: A(1.3), spacing: 1.2, shadow: 16, shadowColor: 'rgba(3,3,12,0.9)' });
  if (c.line2) drawText(og, c.line2, { x: DW / 2, y: y + 140, font: '500 22px "Cinzel"', color: '#d9c48e', alpha: A(1.9), spacing: 6, shadow: 12, shadowColor: 'rgba(3,3,12,0.9)' });
  if (c.ar) { og.save(); og.font = '400 64px "Amiri Quran"'; og.direction = 'rtl'; og.textAlign = 'center'; og.textBaseline = 'middle'; og.globalAlpha = A(2.5); og.shadowColor = 'rgba(255,190,100,0.55)'; og.shadowBlur = 24; og.fillStyle = '#f2d27a'; og.fillText(c.ar, DW / 2, y - 120); og.restore(); }
}
