// Dark Corners: "The Ship Called Care" (the Zong, 1781), re-made in the KINOFORGE Lantern Road style. 9:16, 179.4 s, 24 fps.
// A living painting: 2.5D multiplane sets painted procedurally (p03 brush engine), lit by motivated light, one lantern as the motif.
// Picture follows the original mix (audio/mix.m4a, cues.json). See NOTES.md for the shot list.
import * as THREE from 'three';
import { boot, makeComposer, drawText, ease, clamp, lerp, smoothstep } from '/harness/kit/film.js';
import { makeDetailPass, DW, DH } from './lib.js';
import { poseCamera } from './common.js';
import { buildSea } from './sea.js';
import { buildDoc } from './docs.js';
import { buildDeck } from './deck.js';
import { buildCourt } from './court.js';
import { buildLantern } from './lantern.js';
import { buildSection } from './section.js';
import { buildStreet } from './street.js';
import { buildRoad } from './road.js';
import { SHOTS, LABELS, captionsFrom, TITLE, END } from './shots.js';

const FILM = await (await fetch('./film.json')).json();
const CUES = await (await fetch('./cues.json')).json();
const FPS = FILM.fps, DUR = FILM.duration;
const CAPS = captionsFrom(CUES);
const BUILD = {
  'street': () => buildStreet(SHOTS),
  'road': () => buildRoad(SHOTS),
  'section': () => buildSection(SHOTS),
  'lantern:night': () => buildLantern('night', SHOTS), 'lantern:dusk': () => buildLantern('dusk', SHOTS), 'lantern:dawn': () => buildLantern('dawn', SHOTS),
  'court': () => buildCourt(SHOTS),
  'deck': () => buildDeck(SHOTS),
  'doc:claim': () => buildDoc('claim', SHOTS), 'doc:ledger': () => buildDoc('ledger', SHOTS), 'doc:rule': () => buildDoc('rule', SHOTS), 'doc:quote': () => buildDoc('quote', SHOTS), 'doc:kb': () => buildDoc('kb', SHOTS),
  'sea:dusk': () => buildSea('dusk', SHOTS), 'sea:moon': () => buildSea('moon', SHOTS), 'sea:dawn': () => buildSea('dawn', SHOTS),
};
let scene, camera, post, detail, W, H, SC; const cache = new Map(); let ctxR; const tv = new THREE.Vector3();
const MAXLIVE = 3;

function disposeSet(s) { s.S.group.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) { const m = o.material; if (m.uniforms && m.uniforms.map && m.uniforms.map.value) m.uniforms.map.value.dispose(); m.dispose(); } }); scene.remove(s.S.group); }
function getSet(key, tag) {
  let s = cache.get(key);
  if (!s) {
    const t0 = performance.now(); s = BUILD[key](); scene.add(s.S.group);
    for (const p of s.S.planes) { const tx = p.material.uniforms.map.value; tx.image.getContext('2d').getImageData(0, 0, 1, 1); ctxR.renderer.initTexture(tx); }
    cache.set(key, s); if (ctxR.q.get('prof')) console.log(`built ${key} in ${(performance.now() - t0).toFixed(0)} ms`);
    while (cache.size > MAXLIVE) { const old = [...cache.keys()].find((k) => k !== key && k !== tag); if (!old) break; disposeSet(cache.get(old)); cache.delete(old); }
  }
  return s;
}
const shotAt = (t) => { for (let i = 0; i < SHOTS.length; i++) if (t < SHOTS[i].t1) return SHOTS[i]; return SHOTS[SHOTS.length - 1]; };
const project = (x, y, z) => { tv.set(x, y, z).project(camera); return [(tv.x * 0.5 + 0.5) * W, (-tv.y * 0.5 + 0.5) * H]; };

await boot({
  fps: FPS, duration: DUR, toneMapping: THREE.NoToneMapping,
  fonts: [['Cormorant Garamond', 'italic 400'], ['Cormorant Garamond', 400], ['Cinzel', 500], ['IM Fell English', 400], ['IM Fell English', 'italic 400']],
  init: async (ctx) => {
    ctxR = ctx; W = ctx.W; H = ctx.H; SC = H / DH;
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x0b0d1e);
    camera = new THREE.PerspectiveCamera(30, W / H, 0.05, 40000);
    post = makeComposer(ctx.renderer, scene, camera, {
      bloom: { strength: 0.5, radius: 0.42, threshold: 0.8 }, grade: 'painterly', overlayAfterFinish: true,
      finish: { saturation: 1.1, contrast: 1.04, shadowTint: [-0.008, 0.0, 0.035], highlightTint: [0.05, 0.022, -0.02], halation: 0.25, grain: 0.035, vignette: 0.35 },
    });
    post.finish.kuwaharaRadius.value = +(ctx.q.get('kr') || 3);
    detail = makeDetailPass(post, W, H);
    window.__zong = { SHOTS, cache };
  },
  render: async (ctx, i, t) => {
    const sh = shotAt(t); const set = sh.set && BUILD[sh.set] ? getSet(sh.set) : null;
    for (const [k, s] of cache) s.S.group.visible = s === set;
    const tl = t - sh.t0, u = clamp(tl / (sh.t1 - sh.t0));
    poseCamera(camera, sh.cam ? sh.cam(tl, u) : { mm: 35 });
    detail.clear(); const g = detail.g; const { ctx: oc, clear } = post.overlay; clear();
    let useDetail = 0;
    if (set) { set.update(t, sh, tl, u); if (set.draw) { set.draw(g, { t, tl, u, sh, project, W, H }); useDetail = 1; } }
    detail.pass.uniforms.useDetail.value = useDetail; detail.sync(t);
    // ---- words on screen (crisp, after the finish pass)
    { let ca = 0; for (const c of CAPS) ca = Math.max(ca, smoothstep(c.in, c.in + 0.22, t) * (1 - smoothstep(c.out - 0.28, c.out, t)));
      const sk = sh.set && sh.set.startsWith('doc:') ? 0.62 : (sh.set.startsWith('lantern:') ? 0.5 : 0.28); if (ca > 0.002) { const y0 = 0.70 * H, gr = oc.createLinearGradient(0, y0, 0, H); gr.addColorStop(0, 'rgba(4,4,12,0)'); gr.addColorStop(0.55, `rgba(4,4,12,${(sk * ca).toFixed(3)})`); gr.addColorStop(1, `rgba(4,4,12,${(sk * ca).toFixed(3)})`); oc.fillStyle = gr; oc.fillRect(0, y0, W, H - y0); } }
    for (const c of CAPS) { const a = smoothstep(c.in, c.in + 0.22, t) * (1 - smoothstep(c.out - 0.28, c.out, t)); if (a > 0.002) drawCaption(oc, c.text, a); }
    for (const l of LABELS) { const a = smoothstep(l.in, l.in + 0.7, t) * (1 - smoothstep(l.out - 0.7, l.out, t)); if (a > 0.002) drawLabel(oc, l.lines, a, l.y); }
    if (sh.words) for (const w of sh.words(t)) { if (w.a > 0.002) drawText(oc, w.text, { x: W / 2, y: w.y * H, font: w.sub ? `italic 400 ${Math.round(w.px * SC)}px "Cormorant Garamond"` : `500 ${Math.round(w.px * SC)}px "Cinzel"`, color: w.col || '#eadfc6', alpha: w.a, spacing: (w.sub ? 1.2 : 8) * SC, shadow: 14 * SC, shadowColor: 'rgba(3,3,12,0.9)' }); }
    drawCards(oc, t);
    let fade = ease.inOutSine(clamp(t / 0.25)); if (sh.fadeIn) fade *= ease.inOutSine(clamp(tl / sh.fadeIn)); if (sh.fadeOut) fade *= ease.inOutSine(clamp((sh.t1 - t) / sh.fadeOut));
    if (t > DUR - 0.12) fade *= clamp((DUR - t) / 0.12);
    post.finish.fade.value = fade;
    post.render(t);
  },
});

function drawCaption(oc, text, a) {
  drawText(oc, text, { x: W / 2, y: 0.865 * H, font: `italic 400 ${Math.round(37 * SC)}px "Cormorant Garamond"`, color: '#f3ead6', alpha: a, spacing: 0.5 * SC, shadow: 16 * SC, shadowColor: 'rgba(3,3,12,0.95)', maxWidth: 580 * SC, lineHeight: 1.22 });
}
function drawLabel(oc, lines, a, y = 0.105) {
  lines.forEach((ln, k) => { const main = k === 0; drawText(oc, ln, { x: W / 2, y: (y * H) + k * 44 * SC, font: main ? `500 ${Math.round(31 * SC)}px "Cinzel"` : `italic 400 ${Math.round(29 * SC)}px "Cormorant Garamond"`, color: main ? '#eadfc6' : '#d9cdb4', alpha: a * (main ? 1 : 0.92), spacing: (main ? 6 : 1.2) * SC, shadow: 12 * SC, shadowColor: 'rgba(3,3,12,0.9)' }); });
}
function drawCards(oc, t) {
  for (const c of [TITLE, END]) { const a = smoothstep(c.in, c.in + 0.8, t) * (1 - smoothstep(c.out - 0.4, c.out, t)); if (a < 0.002) continue;
    drawText(oc, 'DARK CORNERS', { x: W / 2, y: 0.46 * H, font: `500 ${Math.round(60 * SC)}px "Cinzel"`, color: '#efe3c8', alpha: a, spacing: 13 * SC, shadow: 18 * SC, shadowColor: 'rgba(3,3,12,0.9)' });
    const b = smoothstep(c.in + 0.5, c.in + 1.2, t) * (1 - smoothstep(c.out - 0.4, c.out, t)); if (b > 0.002) drawText(oc, 'The Ship Called Care', { x: W / 2, y: 0.46 * H + 76 * SC, font: `italic 400 ${Math.round(48 * SC)}px "Cormorant Garamond"`, color: '#e4d8bd', alpha: b, spacing: 1.2 * SC, shadow: 14 * SC, shadowColor: 'rgba(3,3,12,0.9)' }); }
}
