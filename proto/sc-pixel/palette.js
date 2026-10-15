// P13 palette + flat-shaded material helpers. Colours are written as k-triples (0..6) = the kit's 7 output levels per channel
// (palette [6,6,6] -> floor(c*6+.5)/6), so flat areas land exactly on a level and never speckle under the Bayer dither.
import * as THREE from 'three';

const LV = [0, 43, 85, 128, 170, 213, 255];
export const K = (r, g, b) => (LV[r] << 16) | (LV[g] << 8) | LV[b];

export const P = {
  // sky: banded gradient (dithered by the finish pass)
  skyTop: K(0, 0, 1), skyMid: K(0, 1, 2), skyLow: K(1, 1, 3), skyHaze: K(2, 1, 3), skyGlow: K(3, 1, 3),
  cloud: K(1, 1, 2), cloudHi: K(1, 2, 3),
  // buildings by depth (far = hazier / lighter, near = darker + more contrast)
  farFace: K(1, 1, 3), farSide: K(1, 1, 2), farTop: K(2, 2, 3),
  midFace: K(0, 2, 3), midSide: K(0, 1, 2), midTop: K(1, 3, 4),
  nearFace: K(0, 1, 2), nearFaceLo: K(0, 2, 3), nearSide: K(0, 0, 1), nearTop: K(0, 2, 3),
  inkFace: K(0, 0, 1), inkSide: K(0, 0, 0), inkTop: K(0, 1, 2),
  // windows
  winDark: K(0, 1, 2), winDim: K(0, 2, 3), winTeal: K(0, 3, 3), winCyan: K(0, 4, 5), winPale: K(2, 4, 5), winMag: K(4, 0, 3),
  // neon
  cyan: K(0, 5, 6), cyanDim: K(0, 3, 4), cyanHot: K(3, 6, 6), mag: K(6, 0, 4), magDim: K(3, 0, 3), magHot: K(6, 2, 6),
  // the one warm accent
  amber: K(6, 4, 0), amberHot: K(6, 5, 1), amberDim: K(4, 2, 0), amberGlow: K(2, 1, 0),
  // rain
  rainFg: K(3, 5, 6), rainBg: K(1, 3, 4),
  white: K(6, 6, 6), black: K(0, 0, 0),
};

const _flat = new Map();
export function flat(hex, opts = {}) { // cached unlit material (the whole look is authored colour, no scene lighting)
  const key = hex + '|' + (opts.side || 0);
  if (!_flat.has(key)) _flat.set(key, new THREE.MeshBasicMaterial({ color: hex, side: opts.side || THREE.FrontSide }));
  return _flat.get(key);
}
export const vcMat = new THREE.MeshBasicMaterial({ vertexColors: true });

// Box whose faces carry their own colours (optionally a vertical gradient on a face): c = { pz:[top,bot]|hex, px, nx, py, ny, nz }
// BoxGeometry face order: px, nx, py, ny, pz, nz (4 verts each). +z faces the camera in this scene.
// A face spec is a hex, an array [topHex, lowHex] over the box height, or {a:top, b:low, y0, y1} gradient over world y (yc = world y of the box centre).
export function colorBox(w, h, d, c, { hs = 1, yc = 0 } = {}) {
  const g = new THREE.BoxGeometry(w, h, d, 1, hs, 1); const pos = g.attributes.position, nor = g.attributes.normal; const col = new Float32Array(pos.count * 3);
  const A = new THREE.Color(), B = new THREE.Color(), T = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const nx = nor.getX(i), ny = nor.getY(i), nz = nor.getZ(i);
    const f = nx > 0.5 ? 'px' : nx < -0.5 ? 'nx' : ny > 0.5 ? 'py' : ny < -0.5 ? 'ny' : nz > 0.5 ? 'pz' : 'nz';
    let spec = c[f] ?? c.def ?? P.inkFace; if (Array.isArray(spec)) spec = { a: spec[0], b: spec[1], y0: yc - h / 2, y1: yc + h / 2 };
    if (typeof spec === 'object') { const t = Math.min(1, Math.max(0, (pos.getY(i) + yc - spec.y0) / (spec.y1 - spec.y0))); A.setHex(spec.b); B.setHex(spec.a); T.copy(A).lerp(B, t); } else T.setHex(spec);
    col[i * 3] = T.r; col[i * 3 + 1] = T.g; col[i * 3 + 2] = T.b;
  }
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  return new THREE.Mesh(g, vcMat);
}
export function slab(w, h, hex) { return new THREE.Mesh(new THREE.PlaneGeometry(w, h), flat(hex)); } // flat colour quad facing +z

// Additive glow around a sign: falloff from the sign's own outline (box or circle SDF), so the halo hugs the shape. Banded + dithered by the
// pixel pass, so it reads as a hand-placed pixel glow. reach = metres of glow beyond the outline.
export function halo(w, h, hex, { reach = 1.5, power = 1.6, intensity = 0.5, circle = false, mix = false } = {}) {
  const m = new THREE.ShaderMaterial({
    uniforms: { uColor: { value: new THREE.Color(hex) }, uI: { value: intensity }, uHalf: { value: new THREE.Vector2(w / 2, h / 2) }, uReach: { value: reach }, uPow: { value: power }, uCircle: { value: circle ? 1 : 0 }, uMix: { value: mix ? 1 : 0 } },
    vertexShader: 'varying vec2 vP; uniform vec2 uHalf; uniform float uReach; void main(){ vec2 p=position.xy*(uHalf+vec2(uReach))*2.0; vP=p; gl_Position=projectionMatrix*modelViewMatrix*vec4(p,0.0,1.0);} ',
    fragmentShader: 'varying vec2 vP; uniform vec3 uColor; uniform float uI; uniform vec2 uHalf; uniform float uReach; uniform float uPow; uniform float uCircle; uniform float uMix; void main(){ vec2 q=abs(vP)-uHalf; float d=length(max(q,0.0))+min(max(q.x,q.y),0.0); if(uCircle>0.5) d=length(vP)-uHalf.x; d=max(d,0.0); float a=pow(clamp(1.0-d/uReach,0.0,1.0),uPow); if(uMix>0.5) gl_FragColor=vec4(uColor,a*uI); else gl_FragColor=vec4(uColor*uI*a,1.0);} ',
    transparent: true, depthWrite: false, blending: mix ? THREE.NormalBlending : THREE.AdditiveBlending,
  });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), m); mesh.userData.mat = m; mesh.renderOrder = 5; return mesh;
}
