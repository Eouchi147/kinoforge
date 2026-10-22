// Battle Map engine: inked arrows. A path is smoothed, draped on the terrain and drawn on by an unseen pen (like the route in the Terrain style):
// solid arrows for movements, dashed trails for journeys, an arrowhead at the tip, a wet head while the pen is moving, a cream halo so they read on any ground.
import * as THREE from 'three';
import { catmull, resample, clamp, lerp } from './noise.js';
import { easeFn } from './timeline.js';
import { TEAMS } from './blocks.js';
import { GLSL_FOG } from './terrainShaders.js';

const VERT = /* glsl */`
attribute float aS; attribute float aSide; attribute vec2 aDir; attribute float aW;
uniform float uWExp, uD0, uHalo;
varying float vS; varying float vSide; varying float vHalfW; varying vec3 vWorld; varying float vHaloW;
void main(){
  vec3 p = position; float d = max(length(p - cameraPosition), 1.0); float k = clamp(pow(d/uD0, uWExp), 0.55, 3.2);
  float hw = aW*k; float hh = uHalo*k; float ex = hw + hh; vec2 sd = vec2(-aDir.y, aDir.x); vec3 wp = vec3(p.x + sd.x*aSide*ex, p.y, p.z + sd.y*aSide*ex);
  vS = aS; vSide = aSide*ex; vHalfW = hw; vHaloW = hh; vWorld = wp; gl_Position = projectionMatrix*viewMatrix*vec4(wp, 1.0);
}`;
const FRAG = /* glsl */`
precision highp float;
${GLSL_FOG}
uniform float uProgress, uLen, uAlpha, uHead; uniform vec3 uCol, uDark, uLight, uFogCol; uniform vec2 uDash; uniform vec4 uFog;
varying float vS; varying float vSide; varying float vHalfW; varying vec3 vWorld; varying float vHaloW;
vec3 lin(vec3 c){ return pow(c, vec3(2.2)); }
void main(){
  float hw = vHalfW; float lat = abs(vSide); float px = fwidth(lat) + 1e-4; float pxs = fwidth(vS) + 1e-4;
  if (vS > uProgress) discard;
  float dashOn = 1.0;
  if (uDash.y > 0.0) { float per = uDash.x + uDash.y; float c = vS - floor(vS/per)*per; dashOn = smoothstep(0.0, pxs, c) * (1.0 - smoothstep(uDash.x - pxs, uDash.x, c)); if (vS > uLen - uHead) dashOn = 1.0; }
  float e = hw - lat;                        // > 0 inside the stroke
  float ow = max(0.22, hw*0.14);             // ink outline
  float core = smoothstep(0.0, px, e - ow);
  float rim = smoothstep(-px, px, e);
  float halo = (1.0 - smoothstep(0.0, vHaloW + px, -e))*(1.0 - rim);
  float tipFade = smoothstep(0.0, 1.5, uProgress - vS);   // the pen's leading edge is soft
  float wet = smoothstep(uProgress - 6.0, uProgress, vS)*step(uProgress, uLen - 0.5);
  vec3 body = mix(uCol, uDark, wet*0.25);
  vec3 col = mix(uDark, body, core);
  float a = max(rim, halo*0.55)*uAlpha*dashOn*mix(0.6, 1.0, tipFade);
  col = mix(col, vec3(0.95, 0.91, 0.80), halo*(1.0 - rim));
  if (a < 0.01) discard;
  vec3 c = lin(col);
  c = bmFog(c, vWorld, uFog, uFogCol);
  gl_FragColor = vec4(c, a);
}`;
const PAL = { // arrow ink colours (display space): fill, dark outline, highlight
  rome: [[0.72, 0.12, 0.11], [0.22, 0.04, 0.03], [1.0, 0.55, 0.45]], carthage: [[0.14, 0.32, 0.74], [0.03, 0.07, 0.20], [0.6, 0.78, 1.0]],
  ink: [[0.42, 0.14, 0.10], [0.14, 0.05, 0.03], [0.9, 0.55, 0.4]], gold: [[0.96, 0.74, 0.22], [0.30, 0.17, 0.03], [1.0, 0.95, 0.65]], cream: [[0.97, 0.92, 0.78], [0.22, 0.14, 0.07], [1, 1, 1]],
  green: [[0.22, 0.62, 0.32], [0.04, 0.16, 0.07], [0.7, 0.95, 0.7]],
};

export class Arrows {
  constructor(scene, stage, defs, clock) {
    this.stage = stage; this.items = []; this.byId = {}; this.clock = clock; this.scene = scene;
    this.shared = { uFogCol: { value: new THREE.Color() }, uFog: { value: new THREE.Vector4(0.0016, 0.03, 560, 900) } };
    for (const d of defs) this.add(d);
  }
  add(d) {
    const [t0, t1] = this.clock.span(d, 1.5); const mh = this.stage.mh; const lift = d.lift ?? 3.2; const width = d.width ?? 3.2; const head = d.head === false ? 0 : (d.headLen ?? width * 3.0); const headW = d.headW ?? width * 1.45;
    let pts = d.path; if (d.smooth !== false && pts.length > 2) pts = catmull(pts, 14); const P = resample(pts, 1.4); const n = P.n;
    const rows = []; // [s, x, z, halfW]
    const taper = d.taper ?? 0.30; const tl = Math.min(P.L * 0.45, d.taperLen ?? 36);
    for (let i = 0; i < n; i++) { const s = P.s[i]; const k = taper >= 1 ? 1 : taper + (1 - taper) * Math.min(1, s / Math.max(1e-3, tl)) ** 0.7; rows.push([s, P.x[i], P.z[i], width / 2 * k]); }
    // arrowhead rows: duplicate at the head start (body width then wide), then taper to the tip
    const out = []; const hs = P.L - head;
    for (const r of rows) { if (head && r[0] >= hs) break; out.push(r); }
    if (head) { const at = (s) => { let lo = 0, hi = n - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (P.s[m] <= s) lo = m; else hi = m; } const t = (s - P.s[lo]) / Math.max(1e-6, P.s[hi] - P.s[lo]); return [lerp(P.x[lo], P.x[hi], t), lerp(P.z[lo], P.z[hi], t)]; };
      const a = at(hs); out.push([hs, a[0], a[1], width / 2]); out.push([hs + 0.01, a[0], a[1], headW]); const m = at(hs + head * 0.38); out.push([hs + head * 0.38, m[0], m[1], headW * 0.56]); const m2 = at(hs + head * 0.72); out.push([hs + head * 0.72, m2[0], m2[1], headW * 0.24]); out.push([P.L, P.x[n - 1], P.z[n - 1], 0.02]); }
    const m = out.length; const pos = new Float32Array(m * 2 * 3), aS = new Float32Array(m * 2), aSide = new Float32Array(m * 2), aDir = new Float32Array(m * 4), aW = new Float32Array(m * 2), idx = new Uint32Array((m - 1) * 6);
    for (let i = 0; i < m; i++) { const i0 = Math.max(0, i - 1), i1 = Math.min(m - 1, i + 1); let dx = out[i1][1] - out[i0][1], dz = out[i1][2] - out[i0][2]; let l = Math.hypot(dx, dz); if (l < 1e-6) { dx = out[Math.min(m - 1, i + 2)][1] - out[Math.max(0, i - 2)][1]; dz = out[Math.min(m - 1, i + 2)][2] - out[Math.max(0, i - 2)][2]; l = Math.hypot(dx, dz) || 1; } dx /= l; dz /= l;
      const y = mh(out[i][1], out[i][2]) + lift; for (let k = 0; k < 2; k++) { const v = i * 2 + k; pos[v * 3] = out[i][1]; pos[v * 3 + 1] = y; pos[v * 3 + 2] = out[i][2]; aS[v] = out[i][0]; aSide[v] = k ? 1 : -1; aDir[v * 2] = dx; aDir[v * 2 + 1] = dz; aW[v] = out[i][3]; }
      if (i < m - 1) { const a = i * 2, b = a + 1, c = a + 2, dd = a + 3, o = i * 6; idx[o] = a; idx[o + 1] = b; idx[o + 2] = c; idx[o + 3] = b; idx[o + 4] = dd; idx[o + 5] = c; } }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aS', new THREE.BufferAttribute(aS, 1)); g.setAttribute('aSide', new THREE.BufferAttribute(aSide, 1)); g.setAttribute('aDir', new THREE.BufferAttribute(aDir, 2)); g.setAttribute('aW', new THREE.BufferAttribute(aW, 1)); g.setIndex(new THREE.BufferAttribute(idx, 1)); g.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), 1e5);
    const pal = PAL[d.team || d.color || 'ink'] || PAL.ink; const dash = d.style === 'dash' ? (d.dash || [width * 1.6, width * 0.9]) : [0, 0];
    const mat = new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: FRAG, transparent: true, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -3, polygonOffsetUnits: -3,
      uniforms: { uWExp: { value: d.scaleExp ?? 0.30 }, uD0: { value: 260 }, uHalo: { value: d.halo ?? width * 0.22 }, uProgress: { value: 0 }, uLen: { value: P.L }, uAlpha: { value: 1 }, uHead: { value: head }, uCol: { value: new THREE.Color(...pal[0]) }, uDark: { value: new THREE.Color(...pal[1]) }, uLight: { value: new THREE.Color(...pal[2]) }, uDash: { value: new THREE.Vector2(...dash) }, uFogCol: this.shared.uFogCol, uFog: this.shared.uFog } });
    // pal colours are authored in display space -> the shader decodes them with lin(); keep them raw (Color constructor in r186 converts sRGB->linear when ColorManagement is on, so set raw)
    mat.uniforms.uCol.value.setRGB(...pal[0], THREE.LinearSRGBColorSpace); mat.uniforms.uDark.value.setRGB(...pal[1], THREE.LinearSRGBColorSpace); mat.uniforms.uLight.value.setRGB(...pal[2], THREE.LinearSRGBColorSpace);
    const mesh = new THREE.Mesh(g, mat); mesh.frustumCulled = false; mesh.renderOrder = 6; mesh.visible = false; this.scene.add(mesh);
    const A = { id: d.id, d, t0, t1, mesh, mat, path: P, L: P.L, ease: easeFn(d.ease || 'inOut'), fadeAt: d.fadeAt !== undefined ? this.clock.at(d.fadeAt) : (d.until !== undefined && d.hold !== true ? null : null), fadeDur: d.fadeDur ?? 0.6, end: d.hide !== undefined ? this.clock.at(d.hide) : Infinity };
    A.pointAt = (s) => { s = clamp(s, 0, P.L); let lo = 0, hi = n - 1; while (hi - lo > 1) { const mm = (lo + hi) >> 1; if (P.s[mm] <= s) lo = mm; else hi = mm; } const t = (s - P.s[lo]) / Math.max(1e-6, P.s[hi] - P.s[lo]); const x = lerp(P.x[lo], P.x[hi], t), z = lerp(P.z[lo], P.z[hi], t); return { x, z, dx: P.x[hi] - P.x[lo], dz: P.z[hi] - P.z[lo] }; };
    A.progress = (t) => this.ease01(A, t);
    this.items.push(A); if (d.id) this.byId[d.id] = A; return A;
  }
  ease01(A, t) { return A.ease(clamp((t - A.t0) / Math.max(1e-6, A.t1 - A.t0))); }
  update(t, fog) {
    this.shared.uFogCol.value.copy(fog.col); this.shared.uFog.value.copy(fog.v);
    for (const A of this.items) { const on = t >= A.t0 && t < A.end + A.fadeDur; A.mesh.visible = on; if (!on) continue; const u = this.ease01(A, t); const u2 = u; A.mat.uniforms.uProgress.value = u2 * A.L * 1.002 + (u2 >= 1 ? 1 : 0);
      A.mat.uniforms.uAlpha.value = (t < A.end ? 1 : 1 - clamp((t - A.end) / A.fadeDur)); }
  }
}
