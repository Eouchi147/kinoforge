// Dark Corners, "As They Say" (Kleidion, 1014): Lantern Road style, 9:16, painted 2.5D multiplane. See NOTES.md for the shot list.
// Every frame is a pure function of (i, t): seeded painting, time-driven animation, no clocks. Painted sets are built lazily, once per set.
import * as THREE from 'three';
import { boot, drawText, ease, clamp, lerp, smoothstep } from '/harness/kit/film.js';
import { Post, Setup, DW, DH, fovV } from './kf.js';
import { buildShots, buildCaptions, LABELS } from './shots.js';
import { SETS } from './sets/index.js';

const FILM = await (await fetch('./film.json')).json();
const CUES = await (await fetch('./cues.json')).json();
const SHOTS = buildShots(CUES, FILM.duration);
const CAPS = buildCaptions(CUES);
let scene, camera, post, W, H, SC; const insts = new Map(); const tv = new THREE.Vector3();

// ---- camera: keyframes {x,y,z,pan,tilt,roll,mm}, eased between keys; a little handheld breath
const CAMD = { x: 0, y: 0, z: 0, pan: 0, tilt: 0, roll: 0, mm: 35 };
// "glide": a camera operator's move: ease in over the first quarter, a steady middle, ease out over the last quarter
ease.glide = (u) => { const a = 0.25, v = 1 / (1 - a); return u < a ? v * u * u / (2 * a) : u < 1 - a ? v * (u - a / 2) : 1 - v * (1 - u) * (1 - u) / (2 * a); };
function camPose(sh, lt) {
  const ks = sh.cam; let a = ks[0], b = ks[ks.length - 1];
  if (ks.length === 1) b = a; else { for (let i = 0; i < ks.length - 1; i++) { if (lt <= ks[i + 1][0]) { a = ks[i]; b = ks[i + 1]; break; } } }
  const span = Math.max(1e-6, b[0] - a[0]); const u = clamp((lt - a[0]) / span); const k = (ease[b[2] || sh.ease || 'glide'] || ease.glide)(u);
  const o = {}; for (const key of Object.keys(CAMD)) o[key] = lerp(a[1][key] ?? CAMD[key], b[1][key] ?? CAMD[key], k);
  if (sh.breath) { const q = sh.breath; o.x += q * Math.sin(lt * 0.9) * 0.4; o.y += q * Math.sin(lt * 0.7 + 1) * 0.3; o.pan += 0.0007 * q * Math.sin(lt * 0.6); o.tilt += 0.0006 * q * Math.sin(lt * 0.8 + 2); }
  if (sh.shake) for (const [t0, amp, dur] of sh.shake) { const d = lt - t0; if (d >= 0 && d < (dur || 0.5)) { const e = Math.exp(-d * 7) * amp; o.x += e * 0.5 * Math.sin(d * 63); o.y += e * 0.4 * Math.sin(d * 51 + 1); o.pan += e * 0.0012 * Math.sin(d * 47); } }
  return o;
}
function applyCam(cam, c) { cam.fov = fovV(c.mm); cam.aspect = DW / DH; cam.position.set(c.x, c.y, c.z); cam.rotation.set(c.tilt, c.pan, c.roll, 'YXZ'); cam.updateProjectionMatrix(); cam.updateMatrixWorld(true); }
const sampleCams = (sh) => { const out = []; for (let i = 0; i <= 6; i++) { const c = new THREE.PerspectiveCamera(30, DW / DH, 0.1, 30000); applyCam(c, camPose({ ...sh, breath: 0, shake: null }, sh.dur * i / 6)); out.push(c); } return out; };
const shotAt = (t) => { let s = SHOTS[SHOTS.length - 1]; for (const x of SHOTS) if (t < x.t1) { s = x; break; } return s; };

function ensureSet(id) {
  let inst = insts.get(id); if (inst) { inst.used = performance.now(); return inst; }
  const def = SETS[id]; if (!def) throw new Error('no set ' + id);
  const S = new Setup(id); scene.add(S.group); const cams = SHOTS.filter((s) => s.set === id).flatMap(sampleCams);
  const t0 = performance.now(); const api = def(S, cams, { W, H, SHOTS }); inst = { S, api, used: performance.now(), id };
  // upload every painted texture now (not in the first frame of the shot)
  for (const p of S.planes) { const tx = p.material.uniforms.map.value; if (tx.image && tx.image.getContext) tx.image.getContext('2d').getImageData(0, 0, 1, 1); post.r.initTexture(tx); }
  post.r.resetState(); post.glowTex.needsUpdate = true; post.detailTex.needsUpdate = true; post.overlayTex.needsUpdate = true;
  if (new URLSearchParams(location.search).get('prof')) console.log(`set ${id}: ${(performance.now() - t0).toFixed(0)} ms, planes ${S.planes.length}, glows ${S.glows.length}`);
  { const hide = (new URLSearchParams(location.search).get('hide') || '').split(','); for (const p of S.planes) if (hide.includes(p.userData.name)) p.visible = false; }
  insts.set(id, inst);
  if (insts.size > 3) { let old = null; for (const v of insts.values()) if (v.id !== id && (!old || v.used < old.used)) old = v; if (old) { old.S.dispose(); insts.delete(old.id); } }
  return inst;
}

await boot({
  fps: FILM.fps, duration: FILM.duration, toneMapping: THREE.NoToneMapping,
  fonts: [['Cormorant Garamond', 'italic 400'], ['Cormorant Garamond', 400], ['Cinzel', 500]],
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; SC = W / DW;
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x0b0d1e); camera = new THREE.PerspectiveCamera(30, DW / DH, 0.1, 30000);
    post = new Post(ctx.renderer, scene, camera, W, H, { kr: 2 });
    window.__kf = { SHOTS, CAPS, shotAt, camPose, audit };
  },
  render: async (ctx, i, t) => {
    const sh = shotAt(t); const idx = SHOTS.indexOf(sh); const dz = sh.dissolve && idx > 0 && t - sh.t0 < sh.dissolve ? sh.dissolve : 0;
    if (dz) {
      // dissolve (time passing): the leaving shot keeps living for the length of the dissolve, then the new shot is laid over it
      const prev = SHOTS[idx - 1]; drawShot(ctx, prev, t, { text: false, hold: true });
      if (!copyCv) { copyCv = document.createElement('canvas'); copyCv.width = W; copyCv.height = H; copyG = copyCv.getContext('2d'); }
      copyG.setTransform(1, 0, 0, 1, 0, 0); copyG.clearRect(0, 0, W, H); copyG.drawImage(ctx.renderer.domElement, 0, 0, W, H);
      drawShot(ctx, sh, t, { text: true, under: copyCv, underA: 1 - ease.inOutSine(clamp((t - sh.t0) / dz)) });
    } else drawShot(ctx, sh, t, { text: true });
  },
});
let copyCv = null, copyG = null;

function drawShot(ctx, sh, t, { text = true, under = null, underA = 0, hold = false } = {}) {
  const inst = ensureSet(sh.set); const lt = hold ? Math.min(t - sh.t0, sh.dur) : t - sh.t0, u = clamp(lt / sh.dur);
  for (const v of insts.values()) v.S.group.visible = v === inst;
  applyCam(camera, camPose(sh, t - sh.t0));
  const g = post.clearDetail(); const gg = post.clearGlow(); const og = post.clearOverlay();
  const world = new THREE.Vector3(), Kv = new THREE.Vector3();
  const F = { q: Object.fromEntries(new URLSearchParams(location.search)), t, lt, u, i: 0, shot: sh, cam: camera, S: inst.S, g, post, lights: [], amb: [1, 1, 1], bloom: 0.5, hal: 0.25, fade: 1, flash: 0, W, H, SC,
    glow: () => post.glowOn(),
    W: (D, sx, sy) => { const v = new THREE.Vector3((sx / DW) * 2 - 1, -((sy / DH) * 2 - 1), 0.5).unproject(camera); v.sub(camera.position).normalize(); const k = (-D - camera.position.z) / v.z; return camera.position.clone().addScaledVector(v, k); },
    P: (D, x, y) => { inst.S.world(x, y, D, tv).project(camera); return [(tv.x * 0.5 + 0.5) * DW, (-tv.y * 0.5 + 0.5) * DH]; },
    K: (D, x = DW / 2, y = DH / 2) => { const a = inst.S.world(x, y, D, world).clone().project(camera), b = inst.S.world(x + 40, y, D, Kv).project(camera); return ((b.x - a.x) * 0.5 * DW) / 40; },
  };
  inst.api.update(F);
  // slow drift of the sky (cloud shadows) and any plane that asks for it (mist, fog): a gentle sway, never a runaway slide; wind time for grass strips
  for (const p of inst.S.planes) { const d = p.userData; p.material.uniforms.uTime.value = t; const amp = d.drift != null ? d.drift * 11 : (/^sky/.test(d.name) ? 80 : 0);
    if (amp) p.position.x = d.base.x + amp * Math.sin((2 * Math.PI * t) / (d.drift != null ? 70 : 170) + (d.D % 7)) * d.D / inst.S.f; }
  let ov = false;
  if (under) { og.save(); og.setTransform(1, 0, 0, 1, 0, 0); og.globalAlpha = underA; og.drawImage(under, 0, 0, W, H); og.restore(); og.setTransform(post.sc, 0, 0, post.sc, 0, 0); ov = true; }
  if (text) {
    for (const c of CAPS) { const a = smoothstep(c.in, c.in + 0.3, t) * (1 - smoothstep(c.out - 0.3, c.out, t)); if (a > 0.003) { ov = true; capDraw(og, c.text, a, sh.capShade ?? 0.42); } }
    for (const L of LABELS) { const a = smoothstep(L.in, L.in + 0.5, t) * (1 - smoothstep(L.out - 0.5, L.out, t)); if (a > 0.003) { ov = true; labelDraw(og, L, a); } }
    if (sh.card) { ov = true; cardDraw(og, sh, t); }
    if (sh.words) for (const w of sh.words) { const a = smoothstep(w.in, w.in + (w.fi ?? 0.9), t) * (1 - smoothstep(w.out - (w.fo ?? 0.8), w.out, t)); if (a > 0.003) { ov = true; drawText(og, w.text, { x: DW / 2, y: w.y ?? 400, font: w.font ?? '500 44px "Cinzel"', color: w.color ?? '#e8c878', alpha: a, spacing: w.spacing ?? 8, shadow: 18, shadowColor: 'rgba(3,3,12,0.95)' }); } }
  }
  if (ov) post.markOverlay();
  let fade = F.fade; if (sh.fadeIn) fade *= ease.inOutSine(clamp(lt / sh.fadeIn)); if (sh.fadeOut) fade *= 1 - ease.inOutSine(clamp((lt - (sh.dur - sh.fadeOut)) / sh.fadeOut));
  if (t < 0.25) fade *= ease.inOutSine(clamp(t / 0.25));
  post.render(t, { fade, lights: F.lights, amb: F.amb, bloom: F.bloom, hal: F.hal });
}


// camera audit (?audit=1 in the console, or window.__kf.audit()): speed of every move as a camera operator would feel it
function audit() {
  const out = []; const hf = 2 * Math.atan(0.5625 * 12 / 35) , vf = 2 * Math.atan(12 / 35);
  for (const sh of SHOTS) { let mp = 0, mt = 0, mz = 0, mx = 0; const n = Math.max(8, Math.round(sh.dur * 6));
    for (let i = 0; i < n; i++) { const t0 = sh.dur * i / n, t1 = sh.dur * (i + 1) / n; const a = camPose({ ...sh, breath: 0, shake: null }, t0), b = camPose({ ...sh, breath: 0, shake: null }, t1); const dt = t1 - t0;
      mp = Math.max(mp, Math.abs(b.pan - a.pan) / dt / (2 * Math.atan(0.5625 * 12 / a.mm))); mt = Math.max(mt, Math.abs(b.tilt - a.tilt) / dt / (2 * Math.atan(12 / a.mm))); mz = Math.max(mz, Math.abs(Math.log(b.mm / a.mm)) / dt);
      mx = Math.max(mx, Math.hypot(b.x - a.x, b.y - a.y, b.z - a.z) / dt * FREFpx(sh)); }
    out.push({ id: sh.id, set: sh.set, t0: +sh.t0.toFixed(2), dur: +sh.dur.toFixed(2), panPctW: +(mp * 100).toFixed(1), tiltPctH: +(mt * 100).toFixed(1), zoomPct: +(mz * 100).toFixed(1), dollyPxAt170: +mx.toFixed(1) }); }
  return out;
}
const FREFpx = () => 1866.7 / 170;

// ---- type
function capDraw(og, text, a, shade = 0.42) {
  const lines = wrap(og, text, 560, 'italic 400 34px "Cormorant Garamond"'); const y0 = 1008 - (lines.length - 1) * 21;
  og.save(); const gr = og.createLinearGradient(0, 880, 0, 1160); gr.addColorStop(0, 'rgba(4,4,14,0)'); gr.addColorStop(1, `rgba(4,4,14,${shade * a})`); og.fillStyle = gr; og.fillRect(0, 880, DW, 400); og.restore();
  lines.forEach((l, i) => drawText(og, l, { x: DW / 2, y: y0 + i * 42, font: 'italic 400 34px "Cormorant Garamond"', color: '#efe6d3', alpha: a, spacing: 0.5, shadow: 12, shadowColor: 'rgba(3,3,12,0.95)' }));
}
function wrap(g, text, maxW, font) { g.save(); g.font = font; const words = text.split(' '); const lines = []; let cur = ''; for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } if (cur) lines.push(cur); g.restore(); return lines; }
function labelDraw(og, L, a) {
  drawText(og, L.text, { x: DW / 2, y: L.y ?? 150, font: '500 30px "Cinzel"', color: '#ead9b4', alpha: a, spacing: 7, shadow: 10, shadowColor: 'rgba(3,3,12,0.9)' });
  if (L.sub) drawText(og, L.sub, { x: DW / 2, y: (L.y ?? 150) + 40, font: 'italic 400 26px "Cormorant Garamond"', color: '#d8cdb8', alpha: a * 0.92, spacing: 1.2, shadow: 10, shadowColor: 'rgba(3,3,12,0.9)' });
}
function cardDraw(og, sh, t) {
  const c = sh.card; const lt = t - (c.at ?? sh.t0); if (lt < 0) return; const dy = c.dy ?? 0;
  const a1 = ease.outCubic(clamp((lt - (c.t1 ?? 0.3)) / 1.0)), a2 = ease.outCubic(clamp((lt - (c.t2 ?? 1.2)) / 1.0)); const fo = c.out ? 1 - smoothstep((c.at != null ? sh.t1 - c.at : sh.dur) - c.out, (c.at != null ? sh.t1 - c.at : sh.dur), lt) : 1;
  og.save(); og.globalAlpha = 1;
  drawText(og, 'DARK CORNERS', { x: DW / 2, y: 585 + dy, font: '500 52px "Cinzel"', color: '#ead9b4', alpha: a1 * fo, spacing: 11, shadow: 16, shadowColor: 'rgba(3,3,12,0.9)' });
  const wl = 250 * a2 * fo; og.globalAlpha = 0.7 * a2 * fo; og.fillStyle = '#c9a55a'; og.fillRect(DW / 2 - wl / 2, 622 + dy, wl, 1.5); og.globalAlpha = 1;
  drawText(og, 'As They Say', { x: DW / 2, y: 676 + dy, font: 'italic 400 64px "Cormorant Garamond"', color: '#efe6d3', alpha: a2 * fo, spacing: 1.5, shadow: 16, shadowColor: 'rgba(3,3,12,0.9)' });
  og.restore();
}
