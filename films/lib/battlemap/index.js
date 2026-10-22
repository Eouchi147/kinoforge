// Battle Map engine: entry point. startBattleMap({ specUrl, cuesUrl }) builds the stages from the JSON spec and drives every frame from the cue times.
// See SPEC.md. Every frame is a pure function of t (no clocks, no unseeded randomness).
import * as THREE from 'three';
import { boot, makeComposer, clamp, lerp } from '/harness/kit/film.js';
import { Clock, EASE } from './timeline.js';
import { noiseTexture, paperTexture } from './terrainShaders.js';
import { Stage, DEFAULT_LOOK } from './stage.js';
import { View, drawCard } from './overlay.js';
import { normaliseKey } from './camera.js';

const q = new URLSearchParams(location.search);
const INSET_FRAG = `precision highp float; uniform sampler2D uTex; uniform float uAlpha, uFrame, uAspect, uTime; uniform vec3 uInk, uGold; varying vec2 vUv;
  void main(){ vec2 uv = vUv; vec2 p = (uv - 0.5)*vec2(uAspect, 1.0); float bw = 0.012; vec2 q = abs(uv - 0.5);
    vec3 col = texture2D(uTex, uv).rgb; float edgeD = min(min(uv.x, 1.0 - uv.x)*uAspect, min(uv.y, 1.0 - uv.y));
    float b1 = smoothstep(bw*1.0, bw*0.8, edgeD)*uFrame; float b2 = smoothstep(0.0095, 0.0075, abs(edgeD - 0.022))*uFrame; float b3 = smoothstep(0.0, 0.004, edgeD)*uFrame;
    col = mix(col, uInk, b1); col = mix(col, uGold, b2*0.9); col = mix(col, uInk, (1.0 - b3)*uFrame);
    gl_FragColor = vec4(col, uAlpha); }`;

export async function startBattleMap({ specUrl, cuesUrl, fps = 24 }) {
  const spec = specUrl.endsWith('.js') ? (await import(new URL(specUrl, location.href).href)).default : await (await fetch(specUrl)).json(); const cues = await (await fetch(cuesUrl)).json();
  const look = { ...DEFAULT_LOOK, ...(spec.look || {}) }; const grade = { saturation: 0.95, contrast: 1.08, shadowTint: [-0.01, 0.0, 0.025], highlightTint: [0.04, 0.02, -0.01], grain: 0.03, grainSize: 1.4, vignette: 0.30, ...(spec.look?.grade || {}) };
  const clock = new Clock(cues, spec.marks || {}); const duration = cues.duration; let S = null;
  await boot({
    fps, duration, toneMapping: THREE.NeutralToneMapping, exposure: spec.look?.exposure ?? 1.0, fonts: [['Cinzel', 600], ['Cinzel', 800]],
    init: async (ctx) => {
      const { renderer, W, H } = ctx; const T0 = performance.now(); const lap = (m) => { if (q.get('dbg')) console.log('[init]', m, ((performance.now() - T0) / 1000).toFixed(2) + 's'); };
      await document.fonts.load('italic 500 20px "Cormorant Garamond"').catch(() => {});
      const shared = { uNoise: { value: noiseTexture(11) }, uPaper: { value: paperTexture(1024, 2024) } };
      const main = new Stage({ renderer, shared, spec, look, clock, aspect: W / H, name: 'main' }); lap('main stage');
      const stages = {}; for (const [name, sp] of Object.entries(spec.stages || {})) { const used = (spec.insets || []).find((i) => i.stage === name); const r = used?.rect || [0, 0, 1, 1]; stages[name] = new Stage({ renderer, shared, spec: sp, look, clock, aspect: (r[2] * W) / (r[3] * H), name }); lap('stage ' + name); }
      const post = makeComposer(renderer, main.scene, main.camera, { grade: 'none', finish: { ...grade, halation: 0, letterbox: 0 }, overlayAfterFinish: true });
      const msaa = { cur: -1 }; const setMSAA = (k) => { if (msaa.cur === k) return; msaa.cur = k; for (const rt of [post.composer.renderTarget1, post.composer.renderTarget2]) { if (rt.samples !== k) { rt.samples = k; rt.dispose(); } } };
      // insets: framed panels (or full screen) showing another stage; scrim darkens the main map behind them
      const insets = (spec.insets || []).map((e) => { const [t0, t1] = clock.span(e, 1); const r = e.rect || [0, 0, 1, 1]; const rw = Math.round(Math.min(W, r[2] * W)), rh = Math.round(Math.min(H, r[3] * H));
        const rt = new THREE.WebGLRenderTarget(rw, rh, { type: THREE.HalfFloatType, samples: e.samples ?? (r[2] * r[3] > 0.9 ? 2 : 4), depthBuffer: true }); rt.texture.colorSpace = THREE.NoColorSpace;
        const mat = new THREE.ShaderMaterial({ vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position, 1.0); }', fragmentShader: INSET_FRAG, transparent: true, depthTest: false, depthWrite: false, toneMapped: false,
          uniforms: { uTex: { value: rt.texture }, uAlpha: { value: 1 }, uFrame: { value: e.frame === false ? 0 : 1 }, uAspect: { value: rw / rh }, uTime: { value: 0 }, uInk: { value: new THREE.Color(0.012, 0.008, 0.006) }, uGold: { value: new THREE.Color(0.9, 0.62, 0.2) } } });
        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat); mesh.renderOrder = 100; mesh.frustumCulled = false; mesh.visible = false; main.camera.add(mesh);
        return { ...e, t0, t1, rect: r, rt, mat, mesh, stage: stages[e.stage], tin: e.in ?? 0.5, tout: e.out ?? 0.4 }; });
      const scrimMat = new THREE.ShaderMaterial({ vertexShader: 'void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }', fragmentShader: 'uniform float uA; void main(){ gl_FragColor = vec4(0.03, 0.015, 0.008, uA); }', transparent: true, depthTest: false, depthWrite: false, toneMapped: false, uniforms: { uA: { value: 0 } } });
      const scrim = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), scrimMat); scrim.renderOrder = 99; scrim.frustumCulled = false; scrim.visible = false; main.scene.add(scrim);
      const cards = (spec.cards || []).map((c) => { const [t0, t1] = clock.span(c, 1); return { ...c, t0, t1 }; });
      const msaaOn = (spec.msaaOn || []).map((r) => [clock.at(r[0]), clock.at(r[1])]);
      S = { ctx, spec, look, clock, cues, main, stages, post, W, H, insets, scrim, cards, setMSAA, msaaOn, shared }; lap('ready');
    },
    render: async (ctx, i, t) => {
      const { main, post, insets, scrim, cards, W, H } = S; const g = post.overlay.ctx; post.overlay.clear();
      // which inset is on screen
      const act = insets.filter((e) => t >= e.t0 - 1e-6 && t < e.t1 + e.tout); let cover = false; let scrimA = 0;
      for (const e of insets) e.mesh.visible = false;
      let pose = null; const camq = q.get('cam'); if (camq) { const c = camq.split(',').map(Number); pose = normaliseKey({ at: 0, target: [c[0], c[1]], width: c[2], pitch: c[3] ?? 89.9, yaw: c[4] ?? 0, mm: c[5] ?? 35 }, S.clock, W / H); }
      for (const e of act) { const a = clamp((t - e.t0) / e.tin) * (1 - clamp((t - e.t1) / e.tout)); const k = EASE.outBack(clamp((t - e.t0) / e.tin)); const full = e.rect[2] >= 0.999 && e.rect[3] >= 0.999;
        if (full && a >= 0.999) cover = true; scrimA = Math.max(scrimA, a * (e.scrim ?? (full ? 0 : 0.45))); }
      S.setMSAA(cover ? 0 : (q.get('msaa') !== null ? +q.get('msaa') : (S.msaaOn.some((r) => t >= r[0] && t < r[1]) ? 4 : 0)));
      const tp0 = performance.now(); main.setVisible(!cover); if (!cover) main.update(t, pose); const tp1 = performance.now();
      // render inset stages into their targets, place their HUD quads
      const cam = main.camera; const HD = 3; const hh = 2 * Math.tan(cam.fov * Math.PI / 360) * HD, ww = hh * cam.aspect;
      for (const e of act) { const a = clamp((t - e.t0) / e.tin) * (1 - clamp((t - e.t1) / e.tout)); if (a <= 0.001) continue; const k = (e.pop === false ? 1 : lerp(0.88, 1, EASE.outBack(clamp((t - e.t0) / e.tin)))) * (1 - 0.06 * clamp((t - e.t1) / e.tout));
        e.stage.camera.aspect = e.rt.width / e.rt.height; e.stage.update(t); ctx.renderer.setRenderTarget(e.rt); ctx.renderer.toneMapping = THREE.NoToneMapping; ctx.renderer.render(e.stage.scene, e.stage.camera); ctx.renderer.setRenderTarget(null); ctx.renderer.toneMapping = THREE.NeutralToneMapping;
        const r = e.rect; const cx = (r[0] + r[2] / 2) * 2 - 1, cy = 1 - (r[1] + r[3] / 2) * 2; e.mesh.position.set(cx * ww / 2, cy * hh / 2 - (1 - a) * 0.03 * HD, -HD); e.mesh.scale.set(r[2] * ww * k, r[3] * hh * k, 1); e.mesh.rotation.z = (e.tilt || 0) * Math.PI / 180 * (e.pop === false ? 0 : (1 - 0.5 * clamp((t - e.t0) / e.tin)));
        e.mat.uniforms.uAlpha.value = a; e.mesh.visible = true; e.mat.uniforms.uTime.value = t; e._k = k; e._a = a; }
      scrim.visible = scrimA > 0.002; scrim.material.uniforms.uA.value = scrimA;
      // overlay
      const full = { x: 0, y: 0, w: W, h: H };
      if (!cover) main.overlay.draw(g, t, new View(main.camera, full));
      for (const e of act) { if (!e.mesh.visible) continue; const r = e.rect; const k = e._k; const cx = (r[0] + r[2] / 2) * W, cy = (r[1] + r[3] / 2) * H; const rw = r[2] * W * k, rh = r[3] * H * k; const rect = { x: cx - rw / 2, y: cy - rh / 2 - (1 - e._a) * 0.03 * H * 0.5, w: rw, h: rh };
        g.save(); g.beginPath(); g.rect(rect.x, rect.y, rect.w, rect.h); g.clip(); g.globalAlpha = e._a; e.stage.overlay.draw(g, t, new View(e.stage.camera, rect)); g.restore(); }
      for (const c of cards) drawCard(g, c, t, W, H);
      const tp2 = performance.now(); post.render(t); if (q.get('prof')) { ctx.renderer.getContext().finish(); console.log('[prof] update', (tp1 - tp0).toFixed(0), 'overlay', (tp2 - tp1).toFixed(0), 'render', (performance.now() - tp2).toFixed(0), 'ms'); }
    },
  });
}
