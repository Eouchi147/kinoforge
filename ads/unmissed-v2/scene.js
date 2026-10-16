// "The Catch" (Unmissed v2): the scene.
// window.KF = { duration, fps: 30, render(i, t) }; KF_READY after fonts, textures and ad.json.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { seg, lerp, ease, mulberry, words, rise, fitStage } from '/ads/lib/motion.js';
import { CARD_W, CARD_H, KIND_LIST, cardTexture, glowTexture, radialTexture, makeCard } from './cards.js';
import { makeRing, makeHalo, makeDust } from './ring.js';
import { buildSpecs, place, RING_R, ZP } from './choreo.js';

const $ = (s) => document.querySelector(s);
const q = fitStage($('#stage'));
const RW = +q.get('w') || 1920, RH = +q.get('h') || 1080;
const AD = await (await fetch('./ad.json')).json();
const cue = AD.cues, DURATION = AD.duration;
await document.fonts.ready; await Promise.all([...document.fonts].map((f) => f.load().catch(() => {})));
await document.fonts.load('700 40px Inst'); await document.fonts.load('500 40px Inst'); await document.fonts.load('500 30px Mono');

// ---- renderer, scene, camera, post
const canvas = $('#gl');
const renderer = new THREE.WebGLRenderer({ canvas, preserveDrawingBuffer: true, antialias: true });
renderer.setPixelRatio(1); renderer.setSize(RW, RH, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.setClearColor(0x05070f, 1);
const scene = new THREE.Scene(); scene.background = new THREE.Color('#05070f'); scene.fog = new THREE.FogExp2('#05070f', 0.021);
const camera = new THREE.PerspectiveCamera(32, 16 / 9, 0.1, 220);
const rt = new THREE.WebGLRenderTarget(RW, RH, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt); composer.setPixelRatio(1); composer.setSize(RW, RH);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(RW, RH), 0.5, 0.6, 0.85); composer.addPass(bloom);
composer.addPass(new OutputPass());

// ---- the stream clock: W(t) is "distance travelled" so the river can start slow, speed up, and ease out for the logo
const SPD = (t) => (0.42 + 0.58 * ease.inOutCubic(seg(t, 0, 5.5))) * (1 - 0.88 * ease.inOutCubic(seg(t, 9.6, 11.2)));
const DT = 1 / 240, WT = [0]; for (let i = 1; i <= 240 * 24; i++) WT.push(WT[i - 1] + SPD(i * DT) * DT);
const Wf = (t) => { const x = Math.min(Math.max(t, 0), 23.9) / DT, i = Math.floor(x); return lerp(WT[i], WT[i + 1], x - i); };

// ---- the ring group: glass ring, halo, node, sprites that live in the ring's plane
const ring = new THREE.Group(); scene.add(ring);
const ringMesh = makeRing(), halo = makeHalo(RING_R); ring.add(ringMesh, halo);
const dotTex = radialTexture([[0, 'rgba(255,255,255,1)'], [0.25, 'rgba(160,205,255,.8)'], [0.6, 'rgba(60,130,255,.25)'], [1, 'rgba(30,90,255,0)']]);
const shockTex = radialTexture([[0, 'rgba(0,0,0,0)'], [0.4, 'rgba(0,0,0,0)'], [0.47, 'rgba(121,180,255,.9)'], [0.5, 'rgba(200,225,255,1)'], [0.53, 'rgba(121,180,255,.7)'], [0.62, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']]);
const sprite = (tex, order = 7) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, fog: false })); s.renderOrder = order; s.visible = false; s.frustumCulled = false; ring.add(s); return s; };
const node = new THREE.Mesh(new THREE.SphereGeometry(0.17, 20, 14), new THREE.MeshBasicMaterial({ color: new THREE.Color().setRGB(0.5, 1.5, 3.2), fog: false }));
node.position.set(RING_R * Math.sin(Math.PI / 6), RING_R * Math.cos(Math.PI / 6), 0.02); node.renderOrder = 6; ring.add(node);   // one o'clock
const nodeHalo = sprite(dotTex, 6), headGlow = sprite(dotTex), shock = sprite(shockTex), bigFlash = sprite(dotTex, 8), streak = sprite(dotTex, 8);
const pool = Array.from({ length: 16 }, () => sprite(dotTex));
const dust = makeDust(340, mulberry(77), dotTex); scene.add(dust);

// ---- cards
const specs = buildSpecs(cue);
const texByKind = {}; for (const k of KIND_LIST) texByKind[k] = cardTexture(k, renderer);
const gTex = glowTexture(), cardGeo = new THREE.PlaneGeometry(CARD_W, CARD_H), glowGeo = new THREE.PlaneGeometry(CARD_W * 1.45, CARD_H * 2.1);
const cards = specs.map((s) => { const m = makeCard(s.kind, texByKind[s.kind], gTex, cardGeo, glowGeo); m.visible = false; scene.add(m); return { s, m }; });
const catches = specs.filter((s) => s.type === 'catch');
for (const c of catches) c.phiEnd = c.th - Math.PI * 2 * 1.15;
const tmp = { pos: new THREE.Vector3(), quat: new THREE.Quaternion(), scale: 1, op: 1, glow: 0.35 };

// ---- text
const gapsW = words($('#gaps .l')), nameW = words($('#name .l')), tag1W = words($('#tag1 .l')), tag2W = words($('#tag2 .l'));
const inout = ease.inOutCubic;
const clampN = (x, a, b) => Math.min(b, Math.max(a, x));

function camera_(t) {
  const a = inout(seg(t, cue.ringForm, 10.4)), logo = ease.inOutQuint(seg(t, 10.6, 11.5));
  const az = lerp(-0.3, 0.2, inout(seg(t, 0, cue.ringForm))) * (1 - a);
  const el = (0.07 + 0.045 * Math.sin(t * 0.7)) * (1 - a);
  let d = lerp(lerp(16.6, 14.6, seg(t, 0, cue.ringForm)), 11.2, a); d = lerp(d, 18.3, logo);
  camera.position.set(d * Math.sin(az) * Math.cos(el), d * Math.sin(el), d * Math.cos(az) * Math.cos(el));
  camera.up.set(Math.sin(0.02 * Math.sin(t * 0.5) * (1 - a)), 1, 0).normalize();
  camera.lookAt(0, 0, 0); camera.updateMatrixWorld(true);
  return { a, logo };
}

function render(t) {
  const { a, logo } = camera_(t);
  // ---- the ring: draws as a hairline, blooms into glass on the downbeat, takes energy from every absorbed card, becomes the logo
  const draw = inout(seg(t, cue.ringDraw, cue.ringForm - 0.05));
  const form = ease.outExpo(seg(t, cue.ringForm, cue.ringForm + 0.7)), body = ease.outCubic(seg(t, cue.ringForm, cue.ringForm + 0.5));
  ring.visible = t > cue.ringDraw - 0.05;
  const rot = inout(seg(t, cue.ringForm, 10.3));
  ring.rotation.set(0.17 * (1 - rot), -0.62 * (1 - rot), 0);
  ring.scale.setScalar(lerp(1, 0.5, logo)); ring.position.set(0, 2.48 * logo, 0);
  ring.updateMatrixWorld(true);
  let energy = 0.5; let absorbed = 0;
  for (const c of catches) { const age = t - c.tAb; if (age >= 0) { absorbed++; energy += 0.10 * Math.exp(-age * 8); } }
  energy += 0.30 * absorbed / catches.length + 0.55 * Math.exp(-Math.max(0, t - cue.ignite) * 2.6) * (t >= cue.ignite ? 1 : 0) + 0.25 * Math.exp(-Math.max(0, t - cue.ringForm) * 3) * (t >= cue.ringForm ? 1 : 0);
  const U = ringMesh.material.uniforms;
  U.uDraw.value = draw >= 0.999 ? 1.0 : draw; U.uTube.value = lerp(0.012, 0.2, form); U.uBody.value = body; U.uHair.value = lerp(0.9, 0.05, body);
  U.uEnergy.value = energy; U.uSweep.value = 0.8 + t * 0.95; U.uCam.value.copy(camera.position);
  halo.material.uniforms.uI.value = form * (0.5 + 0.55 * energy);
  const nodeP = ease.outBack(seg(t, cue.ringForm + 0.05, cue.ringForm + 0.4), 2.2) * (1 + 0.05 * Math.sin(t * 3.1));
  node.scale.setScalar(Math.max(0.0001, nodeP)); nodeHalo.visible = nodeP > 0.01; nodeHalo.position.copy(node.position); nodeHalo.scale.setScalar(1.15 * nodeP * (1 + 0.1 * Math.sin(t * 3.1))); nodeHalo.material.opacity = 0.75;
  // the pen that draws the hairline
  const hd = t > cue.ringDraw && t < cue.ringForm + 0.05;
  headGlow.visible = hd; if (hd) { const ang = Math.PI / 2 - draw * Math.PI * 2; headGlow.position.set(RING_R * Math.cos(ang), RING_R * Math.sin(ang), 0.05); headGlow.scale.setScalar(0.7 + 0.5 * draw); headGlow.material.opacity = 1 - seg(t, cue.ringForm - 0.05, cue.ringForm + 0.1); }
  // the shock ring and flash when the glass forms
  const fa = t - cue.ringForm; shock.visible = fa >= 0 && fa < 1.0;
  if (shock.visible) { shock.position.set(0, 0, 0.03); shock.scale.setScalar(lerp(5.5, 26, ease.outCubic(fa / 1.0))); shock.material.opacity = 0.5 * Math.pow(1 - fa / 1.0, 1.6); }
  // absorb flashes
  pool.forEach((s, i) => { const c = catches[i], age = t - c.tAb; s.visible = age >= 0 && age < 0.5;
    if (s.visible) { s.position.set(RING_R * Math.cos(c.phiEnd), RING_R * Math.sin(c.phiEnd), 0.1); const p = age / 0.5; s.scale.setScalar(1.0 + 3.4 * ease.outCubic(p)); s.material.opacity = 1.0 * Math.pow(1 - p, 1.7); } });
  const ia = t - cue.ignite, ig = ia >= 0 && ia < 0.9;
  bigFlash.visible = ig; streak.visible = ig;
  if (ig) { bigFlash.position.set(0, 0, 0.2); bigFlash.scale.setScalar(lerp(9, 24, ease.outCubic(ia / 0.9))); bigFlash.material.opacity = 0.5 * Math.pow(1 - ia / 0.9, 2.2);
    streak.position.set(0, 0, 0.2); streak.scale.set(lerp(18, 46, ease.outCubic(ia / 0.9)), 0.9, 1); streak.material.opacity = 0.7 * Math.pow(1 - ia / 0.9, 1.6); }
  // ---- cards
  for (const { s, m } of cards) { const ok = place(s, t, Wf, ring, camera.position, tmp); m.visible = ok;
    if (ok) { m.position.copy(tmp.pos); m.quaternion.copy(tmp.quat); m.scale.setScalar(tmp.scale); m.userData.mat.opacity = tmp.op; m.userData.gm.opacity = tmp.glow * tmp.op; } }
  // ---- dust: depth cue, drifting with the river
  dust.userData.update(Wf(t) * 9); dust.material.opacity = 0.75 * ease.outCubic(seg(t, 0, 0.8)) * (1 - 0.5 * logo);
  bloom.strength = 0.5 + 0.35 * Math.exp(-Math.max(0, ia) * 3.6) * (ia >= 0 ? 1 : 0) + 0.2 * Math.exp(-Math.max(0, fa) * 3.5) * (fa >= 0 ? 1 : 0);

  // ---- HTML: fade up from black, the one overlay, the end card
  $('#fade').style.opacity = 1 - ease.outCubic(seg(t, 0, 0.4));
  $('#gaps').style.visibility = t > 5.4 && t < 7.4 ? 'visible' : 'hidden';
  rise(gapsW, t, 5.65, { stagger: 0.2, dur: 0.8, tOut: 6.7, outDur: 0.4 });
  rise(nameW, t, cue.logo, { dur: 1.0 }); rise(tag1W, t, cue.tagline, { dur: 0.9 }); rise(tag2W, t, cue.tagline2, { dur: 0.9 });
  $('#ai').style.opacity = ease.outCubic(seg(t, 15.2, 16.0)) * 0.9;
}

window.__dbg = { renderer, scene, camera, composer, bloom, rt, ring, dust, cards };
window.KF = { duration: DURATION, fps: 30, async render(i, t) { render(t); composer.render(); } };
// warm up once (compiles shaders, uploads textures) so the first real frame is not slow
render(8.0); composer.render(); render(0); composer.render();
window.KF_READY = true;
