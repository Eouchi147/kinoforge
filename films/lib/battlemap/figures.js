// Battle Map engine v2: armies as many small soldier figures standing on movement trays (like wargame miniatures on a map).
// - Each block is laid out as a grid of figures (rank and file) that follows the block's tracks (x z heading len dep bulge scale alpha fade).
// - Every figure stands on a tray tile; tiles of one block tile into a clean formation with an inked perimeter (reads top down).
// - A spacing solver keeps units from overlapping: where two blocks meet they meet at a FRONT (ranks compress, a dust line rises).
// - Casualties thin the ranks (figures shrink and sink away), never wounds. Appear = rank by rank from the front; vanish = thinning.
// Pure function of t: every random choice is a hash of the block id and the figure index.
import * as THREE from 'three';
import { GLSL_FOG } from './terrainShaders.js';
import { clamp, lerp, hash01 } from './noise.js';

const DEG = Math.PI / 180;
const strHash = (s) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; };
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };

// ------------------------------------------------------------------ figure geometry (local: x right, y up, z forward; one figure fits in a 1 x 1 cell)
// roles: 0 team cloth, 1 metal, 2 shield (team dark), 3 wood, 4 horse (per-instance coat), 5 leather/dark, 6 gold trim, 7 elephant grey, 8 team light (crest)
function builder() {
  const P = [], N = [], R = [];
  const tri = (a, b, c, role) => { const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2], vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2]; let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l;
    for (const p of [a, b, c]) { P.push(p[0], p[1], p[2]); N.push(nx, ny, nz); R.push(role); } };
  const quad = (a, b, c, d, role) => { tri(a, b, c, role); tri(a, c, d, role); };
  // a box (optionally tapered: top half-widths tx, tz) centred on (cx, cz), from y0 to y1
  const box = (cx, cz, hx, hz, y0, y1, role, tx = hx, tz = hz, bottom = false) => {
    const b = [[cx - hx, y0, cz - hz], [cx + hx, y0, cz - hz], [cx + hx, y0, cz + hz], [cx - hx, y0, cz + hz]], t = [[cx - tx, y1, cz - tz], [cx + tx, y1, cz - tz], [cx + tx, y1, cz + tz], [cx - tx, y1, cz + tz]];
    quad(t[3], t[2], t[1], t[0], role); if (bottom) quad(b[0], b[1], b[2], b[3], role);
    for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; quad(b[k], b[k2], t[k2], t[k], role); } };
  // an oriented slab (for necks, lances): from point a to point b with half sizes
  const beam = (a, b, hw, role) => { const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]; const L = Math.hypot(...d); const u = d.map((v) => v / L); let s = Math.abs(u[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0];
    let r = [u[1] * s[2] - u[2] * s[1], u[2] * s[0] - u[0] * s[2], u[0] * s[1] - u[1] * s[0]]; const rl = Math.hypot(...r); r = r.map((v) => v / rl * hw); let q = [u[1] * r[2] - u[2] * r[1], u[2] * r[0] - u[0] * r[2], u[0] * r[1] - u[1] * r[0]]; const ql = Math.hypot(...q); q = q.map((v) => v / ql * hw);
    const c = (p, sr, sq) => [p[0] + r[0] * sr + q[0] * sq, p[1] + r[1] * sr + q[1] * sq, p[2] + r[2] * sr + q[2] * sq];
    const A = [c(a, -1, -1), c(a, 1, -1), c(a, 1, 1), c(a, -1, 1)], B = [c(b, -1, -1), c(b, 1, -1), c(b, 1, 1), c(b, -1, 1)];
    for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; quad(A[k], A[k2], B[k2], B[k], role); } quad(B[0], B[1], B[2], B[3], role); };
  // a pyramid-ish helmet: square base, apex
  const cap = (cx, cy, cz, r, h, role) => { const b = [[cx - r, cy, cz - r], [cx + r, cy, cz - r], [cx + r, cy, cz + r], [cx - r, cy, cz + r]]; const ap = [cx, cy + h, cz]; for (let k = 0; k < 4; k++) tri(b[k], b[(k + 1) % 4], ap, role); };
  const plate = (cx, cy, cz, hw, hh, role, lean = 0.08) => { // a vertical plate facing +z (shield)
    quad([cx - hw, cy - hh, cz], [cx + hw, cy - hh, cz], [cx + hw, cy + hh, cz + lean * -0.0], [cx - hw, cy + hh, cz], role);
    quad([cx - hw, cy - hh, cz - 0.03], [cx - hw, cy + hh, cz - 0.03], [cx + hw, cy + hh, cz - 0.03], [cx + hw, cy - hh, cz - 0.03], 5); };
  const done = () => { const g = new THREE.InstancedBufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('aN', new THREE.Float32BufferAttribute(N, 3)); g.setAttribute('aRole', new THREE.Float32BufferAttribute(R, 1)); return g; };
  return { box, beam, cap, plate, tri, quad, done };
}
function infantryGeo(elite = false) {
  const B = builder();
  B.box(0, 0, 0.17, 0.11, 0.0, 0.34, 5, 0.15, 0.10);              // legs
  B.box(0, 0, 0.19, 0.12, 0.34, 0.66, 0, 0.16, 0.11);             // tunic and torso
  B.box(0, 0, 0.085, 0.085, 0.66, 0.80, 1, 0.08, 0.08);           // head in a helmet
  B.cap(0, 0.80, 0, 0.10, 0.09, 1);
  if (elite) B.box(0, -0.01, 0.025, 0.10, 0.86, 0.98, 8, 0.02, 0.08); // crest
  B.plate(-0.03, 0.42, 0.15, elite ? 0.17 : 0.15, elite ? 0.25 : 0.21, 2); // shield on the front
  B.plate(-0.03, 0.42, 0.152, elite ? 0.06 : 0.05, elite ? 0.07 : 0.06, 6); // boss
  B.beam([0.22, 0.10, 0.04], [0.22, 1.10, 0.09], 0.016, 3);       // spear
  B.cap(0.22, 1.09, 0.09, 0.026, 0.09, 1);
  return B.done();
}
function lightGeo() { // skirmishers and archers: no big shield, a bow stave
  const B = builder();
  B.box(0, 0, 0.15, 0.10, 0.0, 0.32, 5, 0.13, 0.09); B.box(0, 0, 0.17, 0.11, 0.32, 0.62, 0, 0.15, 0.10); B.box(0, 0, 0.08, 0.08, 0.62, 0.78, 5, 0.075, 0.075);
  B.beam([0.20, 0.22, 0.08], [0.24, 0.62, 0.16], 0.02, 3); B.beam([0.24, 0.62, 0.16], [0.20, 1.02, 0.08], 0.02, 3);
  return B.done();
}
function cavalryGeo() {
  const B = builder();
  B.box(0, 0.26, 0.05, 0.06, 0.0, 0.46, 4); B.box(0, -0.26, 0.05, 0.06, 0.0, 0.46, 4);   // leg pairs (front, back)
  B.box(0.08, 0.26, 0.04, 0.05, 0.0, 0.44, 4); B.box(-0.08, -0.26, 0.04, 0.05, 0.0, 0.44, 4);
  B.box(0, 0, 0.13, 0.40, 0.42, 0.70, 4, 0.12, 0.38);             // barrel
  B.beam([0, 0.62, 0.30], [0, 0.92, 0.50], 0.075, 4);             // neck
  B.beam([0, 0.92, 0.48], [0, 0.82, 0.66], 0.06, 4);              // head
  B.box(0, 0.02, 0.135, 0.16, 0.64, 0.74, 0);                     // saddle cloth (team)
  B.box(0, -0.02, 0.15, 0.10, 0.74, 1.08, 0, 0.13, 0.09);         // rider
  B.box(0, -0.02, 0.075, 0.075, 1.08, 1.22, 1); B.cap(0, 1.22, -0.02, 0.09, 0.08, 1);
  B.beam([0.17, 0.80, -0.30], [0.17, 1.30, 0.56], 0.02, 3);       // lance
  B.beam([0, 0.58, -0.40], [0, 0.40, -0.48], 0.03, 5);            // tail
  return B.done();
}
function elephantGeo() {
  const B = builder();
  for (const [x, z] of [[-0.18, 0.28], [0.18, 0.28], [-0.18, -0.26], [0.18, -0.26]]) B.box(x, z, 0.09, 0.09, 0.0, 0.52, 7);
  B.box(0, 0, 0.30, 0.46, 0.46, 1.02, 7, 0.26, 0.40);             // body
  B.box(0, 0.54, 0.20, 0.16, 0.66, 1.06, 7, 0.17, 0.13);          // head
  B.plate(-0.24, 0.92, 0.50, 0.06, 0.15, 7); B.plate(0.24, 0.92, 0.50, 0.06, 0.15, 7); // ears
  B.beam([0, 0.78, 0.68], [0, 0.20, 0.82], 0.05, 7);              // trunk
  B.beam([0.09, 0.72, 0.66], [0.10, 0.60, 0.86], 0.02, 6); B.beam([-0.09, 0.72, 0.66], [-0.10, 0.60, 0.86], 0.02, 6); // tusks
  B.box(0, -0.05, 0.27, 0.30, 1.02, 1.08, 0);                     // blanket
  B.box(0, -0.08, 0.18, 0.18, 1.08, 1.30, 3);                     // tower
  B.box(0, -0.08, 0.08, 0.08, 1.30, 1.50, 0); B.cap(0, 1.50, -0.08, 0.07, 0.07, 1); // rider
  return B.done();
}
export const FIG_KINDS = { // geometry, cell spacing (front, depth) in map units, figure scale (fraction of the cell), tray
  infantry: { geo: () => infantryGeo(false), sp: [1.7, 1.7], sc: 1.15 },
  elite: { geo: () => infantryGeo(true), sp: [1.6, 1.6], sc: 1.2 },
  light: { geo: lightGeo, sp: [2.1, 2.1], sc: 1.05, loose: 0.35 },
  archers: { geo: lightGeo, sp: [2.0, 2.0], sc: 1.05, loose: 0.2 },
  cavalry: { geo: cavalryGeo, sp: [2.2, 2.8], sc: 1.55 },
  elephant: { geo: elephantGeo, sp: [4.4, 5.0], sc: 2.9 },
  marker: null,
};

const VERT = /* glsl */`
attribute vec3 aN; attribute float aRole;
attribute vec4 iPos;   // xyz, scale
attribute vec4 iDir;   // forward x, z, bob, lean
attribute vec4 iCol;   // team rgb, coat hash
attribute vec4 iMeta;  // fade (grey), light rgb packed? (x: fade, y: elite trim, z: unused, w: unused)
attribute vec3 iLight;
varying vec3 vN; varying vec3 vCol; varying vec3 vWorld; varying float vFade;
uniform vec3 uMetal, uWood, uDark, uGold, uGrey;
void main(){
  vec2 f = normalize(iDir.xy); vec2 r = vec2(-f.y, f.x); // forward (sin h, -cos h) -> right (cos h, sin h)
  float s = iPos.w; vec3 p = position*s; p.y += iDir.z; p.z += p.y*iDir.w;
  vec3 wp = vec3(iPos.x + r.x*p.x + f.x*p.z, iPos.y + p.y, iPos.z + r.y*p.x + f.y*p.z);
  vec3 n = vec3(r.x*aN.x + f.x*aN.z, aN.y, r.y*aN.x + f.y*aN.z);
  vN = n; vWorld = wp; vFade = iMeta.x;
  int role = int(aRole + 0.5); vec3 c = iCol.rgb;
  if (role == 1) c = uMetal; else if (role == 2) c = iCol.rgb*0.62; else if (role == 3) c = uWood; else if (role == 5) c = uDark; else if (role == 6) c = uGold; else if (role == 7) c = uGrey; else if (role == 8) c = iLight;
  else if (role == 4) { float h = iCol.a; c = h < 0.35 ? vec3(0.42, 0.26, 0.15) : h < 0.65 ? vec3(0.55, 0.33, 0.18) : h < 0.85 ? vec3(0.24, 0.17, 0.12) : vec3(0.72, 0.68, 0.62); }
  vCol = c;
  gl_Position = projectionMatrix*viewMatrix*vec4(wp, 1.0);
}`;
const FRAG = /* glsl */`
precision highp float;
${GLSL_FOG}
uniform vec3 uSunDir, uSunCol, uSkyCol, uFogCol; uniform vec4 uFog;
varying vec3 vN; varying vec3 vCol; varying vec3 vWorld; varying float vFade;
vec3 lin(vec3 c){ return pow(c, vec3(2.2)); }
void main(){
  vec3 N = normalize(vN); float ndl = max(dot(N, normalize(uSunDir)), 0.0); float up = N.y*0.5 + 0.5;
  vec3 base = mix(vCol, vec3(0.55, 0.53, 0.50), vFade*0.5);
  vec3 col = lin(base)*(0.20 + 0.85*ndl*uSunCol + uSkyCol*(0.35 + 0.45*up));
  col = bmFog(col, vWorld, uFog, uFogCol);
  gl_FragColor = vec4(col, 1.0);
}`;
// trays: one tile per figure, tiled into a formation; inked perimeter; a soft contact shadow under each figure
const TVERT = /* glsl */`
attribute vec4 iPos;   // xyz, unused
attribute vec4 iDir;   // forward x, z, width, depth
attribute vec4 iCol;   // tray rgb, alpha
attribute vec4 iEdge;  // left, right, back, front (1 = perimeter)
attribute vec4 iMeta;  // shadow offset in tile units (x right, y forward), shadow size, fade
varying vec2 vUv; varying vec4 vEdge; varying vec4 vCol; varying vec3 vWorld; varying vec4 vMeta; varying vec2 vSz;
void main(){
  vec2 f = normalize(iDir.xy); vec2 r = vec2(-f.y, f.x);
  vec2 l = position.xz*vec2(iDir.z, iDir.w);
  vec3 wp = vec3(iPos.x + r.x*l.x + f.x*l.y, iPos.y, iPos.z + r.y*l.x + f.y*l.y);
  vUv = position.xz + 0.5; vEdge = iEdge; vCol = iCol; vWorld = wp; vMeta = iMeta; vSz = iDir.zw;
  gl_Position = projectionMatrix*viewMatrix*vec4(wp, 1.0);
}`;
const TFRAG = /* glsl */`
precision highp float;
${GLSL_FOG}
uniform vec3 uSunCol, uSkyCol, uFogCol; uniform vec4 uFog; uniform float uSunY;
varying vec2 vUv; varying vec4 vEdge; varying vec4 vCol; varying vec3 vWorld; varying vec4 vMeta; varying vec2 vSz;
vec3 lin(vec3 c){ return pow(c, vec3(2.2)); }
void main(){
  vec2 p = vUv*vSz; // units from the tile's back-left corner
  float bw = 0.30; float aa = fwidth(p.x) + fwidth(p.y) + 1e-4;
  float dl = p.x, dr = vSz.x - p.x, db = p.y, df = vSz.y - p.y;
  float e = 0.0; e = max(e, vEdge.x*(1.0 - smoothstep(bw - aa, bw + aa, dl))); e = max(e, vEdge.y*(1.0 - smoothstep(bw - aa, bw + aa, dr)));
  e = max(e, vEdge.z*(1.0 - smoothstep(bw - aa, bw + aa, db))); e = max(e, vEdge.w*(1.0 - smoothstep(bw - aa, bw + aa, df)));
  float hi = 0.0; float bw2 = bw + 0.22; hi = max(hi, vEdge.x*(1.0 - smoothstep(bw2 - aa, bw2 + aa, dl))); hi = max(hi, vEdge.y*(1.0 - smoothstep(bw2 - aa, bw2 + aa, dr))); hi = max(hi, vEdge.z*(1.0 - smoothstep(bw2 - aa, bw2 + aa, db))); hi = max(hi, vEdge.w*(1.0 - smoothstep(bw2 - aa, bw2 + aa, df)));
  vec2 c = vSz*0.5 + vMeta.xy; vec2 q = (p - c)/max(vMeta.z, 0.05); float sh = exp(-dot(q, q)*2.2);
  vec3 col = vCol.rgb; col = mix(col, col*1.25 + 0.06, (hi - e)*0.6); col = mix(col, col*0.55, sh*0.45); col = mix(col, vec3(0.06, 0.045, 0.035), e*0.92);
  col = mix(col, vec3(0.62, 0.60, 0.56), vMeta.w*0.45);
  col = lin(col)*(0.32 + 0.75*uSunCol*uSunY + uSkyCol*0.6);
  col = bmFog(col, vWorld, uFog, uFogCol);
  gl_FragColor = vec4(col, vCol.a);
}`;
// dust and smoke puffs: soft lit sprites
const PVERT = /* glsl */`
attribute vec4 aP;    // xyz, size (units)
attribute vec4 aC;    // rgb, alpha
uniform float uPx;    // pixels per unit at distance 1
varying vec4 vC; varying vec3 vWorld; varying float vSeed;
void main(){ vec4 mv = viewMatrix*vec4(aP.xyz, 1.0); gl_Position = projectionMatrix*mv; gl_PointSize = clamp(aP.w*uPx/max(-mv.z, 1.0), 1.0, 220.0); vC = aC; vWorld = aP.xyz; vSeed = fract(aP.x*0.137 + aP.z*0.311); }`;
const PFRAG = /* glsl */`
precision highp float;
${GLSL_FOG}
uniform vec3 uFogCol; uniform vec4 uFog; uniform sampler2D uNoise;
varying vec4 vC; varying vec3 vWorld; varying float vSeed;
vec3 lin(vec3 c){ return pow(c, vec3(2.2)); }
void main(){ vec2 q = gl_PointCoord*2.0 - 1.0; float d = dot(q, q); if (d > 1.0) discard;
  float n = texture2D(uNoise, gl_PointCoord*0.35 + vSeed*7.0).r; float a = (1.0 - smoothstep(0.15, 1.0, d))*(0.65 + 0.7*n)*vC.a; if (a < 0.004) discard;
  vec3 col = lin(vC.rgb)*(0.9 + 0.2*(1.0 - gl_PointCoord.y)); col = bmFog(col, vWorld, uFog, uFogCol); gl_FragColor = vec4(col, clamp(a, 0.0, 1.0)); }`;

export class Figures {
  constructor(scene, world, uniforms, shared, opts = {}) {
    this.world = world; this.scene = scene; this.uniforms = uniforms; this.opts = opts;
    const U = { ...uniforms, uMetal: { value: new THREE.Vector3(0.72, 0.68, 0.60) }, uWood: { value: new THREE.Vector3(0.62, 0.50, 0.34) }, uDark: { value: new THREE.Vector3(0.24, 0.17, 0.12) }, uGold: { value: new THREE.Vector3(0.95, 0.78, 0.38) }, uGrey: { value: new THREE.Vector3(0.56, 0.53, 0.50) } };
    this.mat = new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: FRAG, uniforms: U, side: THREE.DoubleSide });
    this.meshes = {}; this.cap = {};
    this.tmat = new THREE.ShaderMaterial({ vertexShader: TVERT, fragmentShader: TFRAG, uniforms: { ...uniforms, uSunY: { value: 1 } }, transparent: true, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
    this.pmat = new THREE.ShaderMaterial({ vertexShader: PVERT, fragmentShader: PFRAG, uniforms: { uFogCol: uniforms.uFogCol, uFog: uniforms.uFog, uNoise: shared.uNoise, uPx: { value: 400 } }, transparent: true, depthWrite: false });
    this.tiles = this.instanced(new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2), { iPos: 4, iDir: 4, iCol: 4, iEdge: 4, iMeta: 4 }, 20000, this.tmat, 3);
    const pg = new THREE.BufferGeometry(); this.PMAX = 3000; pg.setAttribute('aP', new THREE.BufferAttribute(new Float32Array(this.PMAX * 4), 4).setUsage(THREE.DynamicDrawUsage)); pg.setAttribute('aC', new THREE.BufferAttribute(new Float32Array(this.PMAX * 4), 4).setUsage(THREE.DynamicDrawUsage)); pg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(this.PMAX * 3), 3));
    this.puffs = new THREE.Points(pg, this.pmat); this.puffs.frustumCulled = false; this.puffs.renderOrder = 8; scene.add(this.puffs);
  }
  instanced(base, attrs, max, mat, order = 5) {
    const g = base.isInstancedBufferGeometry ? base : new THREE.InstancedBufferGeometry().copy(base); const arr = {};
    for (const [k, n] of Object.entries(attrs)) { const a = new THREE.InstancedBufferAttribute(new Float32Array(max * n), n).setUsage(THREE.DynamicDrawUsage); g.setAttribute(k, a); arr[k] = a; }
    g.instanceCount = 0; g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e5); const m = new THREE.Mesh(g, mat); m.frustumCulled = false; m.renderOrder = order; this.scene.add(m); return { mesh: m, g, a: arr, max, n: 0 };
  }
  kindMesh(kind) {
    if (this.meshes[kind]) return this.meshes[kind]; const K = FIG_KINDS[kind]; if (!K) return null;
    const M = this.instanced(K.geo(), { iPos: 4, iDir: 4, iCol: 4, iMeta: 4, iLight: 3 }, 12000, this.mat, 5); this.meshes[kind] = M; return M;
  }
  // lay out one block: -> {pts: [{x,z,fx,fz,row,col,edge,h,vis,...}], meta}
  layout(b, s, t, speed) {
    const K = FIG_KINDS[b.figKind]; const sp = b.cell; const sc = s.scale; const L = Math.max(1, s.len * sc), Dp = Math.max(0.5, s.dep * sc); const hd = s.heading * DEG;
    const fx = Math.sin(hd), fz = -Math.cos(hd), rx = Math.cos(hd), rz = Math.sin(hd); const k = s.bulge ? 8 * s.bulge / L : 0; const wedge = b.wedge * Dp;
    const cols = b.cols, rows = b.rows; const pts = b._pts || (b._pts = []); pts.length = 0; const loose = K?.loose ?? 0; const seed = b.seed;
    const cw = L / cols; const live = clamp(s.alpha * 1.25); const fade = s.fade;
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
      const id = j * cols + i; const h1 = hash01(seed, id, 1), h2 = hash01(seed, id, 2), h3 = hash01(seed, id, 3);
      const u0 = -L / 2 + cw * (i + 0.5); const ju = (h1 - 0.5) * cw * (0.18 + loose); const frontV = Dp / 2 + wedge * (1 - Math.abs(2 * u0 / L));
      const vf = (j + 0.5) / rows; const v0 = lerp(frontV, -Dp / 2, vf); const jv = (h2 - 0.5) * (Dp / rows) * (0.16 + loose); const dv = (frontV + Dp / 2) / rows;
      let sx, sy, ts, tc; if (Math.abs(k) < 1e-6) { sx = u0; sy = 0; ts = 0; tc = 1; } else { const th = k * u0; sx = Math.sin(th) / k; sy = (Math.cos(th) - 1) / k; ts = Math.sin(th); tc = Math.cos(th); }
      const lx = sx + v0 * ts, ly = sy + v0 * tc; const gx = s.x + rx * lx + fx * ly, gz = s.z + rz * lx + fz * ly;
      const jx = (rx * tc - fx * ts) * ju + (rx * ts + fx * tc) * jv, jz = (rz * tc - fz * ts) * ju + (rz * ts + fz * tc) * jv; const x = gx + jx, z = gz + jz; // jitter along the arc tangent and normal
      const ffx = rx * ts + fx * tc, ffz = rz * ts + fz * tc; // facing along the arc
      // appear: rank by rank from the front; vanish/casualties: thinning by hash
      const order = (j / Math.max(1, rows - 1)) * 0.75 + h3 * 0.25; let vis = smooth(order * 0.8, order * 0.8 + 0.2, live);
      if (fade > 0) { const keep = 0.30 + 0.70 * h1; vis *= 1 - smooth(keep - 0.12, keep, fade * 1.05); }
      pts.push({ x, z, jx, jz, fx: ffx, fz: ffz, i, j, cw: Math.min(cw, Math.abs(cw)), dv, vis, h1, h2, h3, edge: [i === 0 ? 1 : 0, i === cols - 1 ? 1 : 0, j === rows - 1 ? 1 : 0, j === 0 ? 1 : 0] });
    }
    return pts;
  }
  // the spacing solver: opposing (or unrelated) blocks never interpenetrate; they meet at a front and compress
  solve(active) {
    const fronts = []; const n = active.length;
    for (const A of active) { let cx = 0, cz = 0, c = 0; for (const p of A.pts) { if (p.vis < 0.05) continue; cx += p.x; cz += p.z; c++; } A.c = c ? [cx / c, cz / c] : [A.s.x, A.s.z]; A.cn = c; let r = 0; for (const p of A.pts) if (p.vis >= 0.05) r = Math.max(r, Math.hypot(p.x - A.c[0], p.z - A.c[1])); A.r = r; }
    for (let a = 0; a < n; a++) for (let b2 = a + 1; b2 < n; b2++) {
      const A = active[a], B = active[b2]; if (!A.cn || !B.cn) continue; if (A.b.group && A.b.group === B.b.group) continue; if (A.b.d.solid === false || B.b.d.solid === false) continue;
      const dx = B.c[0] - A.c[0], dz = B.c[1] - A.c[1]; const D = Math.hypot(dx, dz); if (D > A.r + B.r + 2) continue;
      const nx = D > 1e-3 ? dx / D : 1, nz = D > 1e-3 ? dz / D : 0; const tx = -nz, tz = nx;
      let la0 = 1e9, la1 = -1e9, lb0 = 1e9, lb1 = -1e9; for (const p of A.pts) { if (p.vis < 0.05) continue; const l = p.x * tx + p.z * tz; la0 = Math.min(la0, l); la1 = Math.max(la1, l); } for (const p of B.pts) { if (p.vis < 0.05) continue; const l = p.x * tx + p.z * tz; lb0 = Math.min(lb0, l); lb1 = Math.max(lb1, l); }
      const w0 = Math.max(la0, lb0), w1 = Math.min(la1, lb1); if (w1 - w0 < 0.5) continue; const m = Math.max(A.b.cell[0], B.b.cell[0]);
      let sa = -1e9, sb = 1e9; for (const p of A.pts) { if (p.vis < 0.05) continue; const l = p.x * tx + p.z * tz; if (l < w0 - m || l > w1 + m) continue; sa = Math.max(sa, p.x * nx + p.z * nz); } for (const p of B.pts) { if (p.vis < 0.05) continue; const l = p.x * tx + p.z * tz; if (l < w0 - m || l > w1 + m) continue; sb = Math.min(sb, p.x * nx + p.z * nz); }
      const gap = (A.b.cell[1] + B.b.cell[1]) * 0.42; if (sa + gap <= sb) continue;
      const wa = A.b.d.weight ?? 1, wb = B.b.d.weight ?? 1; const contact = (sa * wb + sb * wa) / (wa + wb) + (gap * 0.5) * (wb - wa) / (wa + wb) * 0; const W = 3.2;
      const clampSide = (P, sign, lim) => { for (const p of P) { const l = p.x * tx + p.z * tz; const wl = smooth(w0 - m * 1.5, w0 - m * 0.3, l) * (1 - smooth(w1 + m * 0.3, w1 + m * 1.5, l)); if (wl <= 0) continue;
        const s0 = (p.x * nx + p.z * nz) * sign; const L0 = lim * sign; const z0 = L0 - W; if (s0 <= z0) continue; const s1 = z0 + W * (1 - Math.exp(-(s0 - z0) / W)); const d = (s1 - s0) * wl * sign; p.x += nx * d; p.z += nz * d; p.front = Math.max(p.front || 0, wl * clamp((s0 - z0) / W)); } };
      clampSide(A.pts, 1, contact - gap * 0.5); clampSide(B.pts, -1, contact + gap * 0.5);
      fronts.push({ cx: nx * contact + tx * (w0 + w1) / 2, cz: nz * contact + tz * (w0 + w1) / 2, tx, tz, nx, nz, half: (w1 - w0) / 2, k: clamp((sa + gap - sb) / 4), A, B });
    }
    return fronts;
  }
  update(t, blocks, list, camera, sunDir, wind = [1.2, 0.4]) {
    const mh = blocks.meshH; const active = [];
    for (const b of list) { if (!b.figKind) continue; const s = blocks.state(b, t); if (s.alpha <= 0.004) continue;
      const sp = blocks.speedOf(b, t); const pts = this.layout(b, s, t, sp); active.push({ b, s, pts, speed: sp }); }
    const fronts = this.solve(active); this.fronts = fronts;
    // write instances
    for (const k in this.meshes) this.meshes[k].n = 0; const T = this.tiles; T.n = 0;
    const sd = [-sunDir[0], -sunDir[2]]; const sl = Math.hypot(sd[0], sd[1]) || 1; const shLen = clamp(0.55 / Math.max(0.15, Math.tan(Math.asin(clamp(sunDir[1], 0.05, 1)))), 0.1, 2.2);
    this.tmat.uniforms.uSunY.value = clamp(sunDir[1] * 2.2, 0.2, 1.0);
    for (const A of active) {
      const { b, s, pts, speed } = A; const M = this.kindMesh(b.figKind); const team = b.team; const col = team.top; const light = team.light; const trayC = b.d.tray ?? team.tray ?? [lerp(col[0] * 0.78, 0.80, 0.18), lerp(col[1] * 0.78, 0.72, 0.18), lerp(col[2] * 0.78, 0.56, 0.18)];
      const scl = (FIG_KINDS[b.figKind]?.sc ?? 1) * Math.min(b.cell[0], b.cell[1]) * (b.d.figScale ?? 1) * 0.78; const moving = clamp(speed / 3); const cav = b.figKind === 'cavalry' || b.figKind === 'elephant';
      const bobAmp = cav ? 0.10 : 0.05; const freq = cav ? 9 : 6.5; const sink = s.sink;
      for (const p of pts) {
        const y = mh(p.x, p.z); const fl = Math.hypot(p.fx, p.fz) || 1; const ffx = p.fx / fl, ffz = p.fz / fl;
        // tray tile
        if (T.n < T.max && s.alpha > 0.01) { const o = T.n++; const a = T.a; const tw = p.cw, td = p.dv;
          a.iPos.array.set([p.x - p.jx, y + 0.10 + (b.seed % 7) * 0.004, p.z - p.jz, 0], o * 4); a.iDir.array.set([ffx, ffz, tw * 1.03, td * 1.03], o * 4);
          a.iCol.array.set([trayC[0], trayC[1], trayC[2], clamp(s.alpha * 1.5) * (0.35 + 0.65 * clamp(p.vis * 3)) * (b.d.trayAlpha ?? 0.9)], o * 4); a.iEdge.array.set(p.edge, o * 4);
          const shx = (sd[0] / sl) * shLen * scl * 0.9, shz = (sd[1] / sl) * shLen * scl * 0.9;           a.iMeta.array.set([shx * (-ffz) + shz * ffx, shx * ffx + shz * ffz, scl * 0.55 * p.vis, s.fade], o * 4); }
        if (!M || p.vis < 0.02 || M.n >= M.max) continue;
        const o = M.n++; const a = M.a; const ph = p.h1 * 6.283 + t * freq * (0.92 + 0.16 * p.h2); const bob = Math.abs(Math.sin(ph)) * bobAmp * moving * scl * 1.5 + (1 - p.vis) * -0.6 * scl - sink * 0.0;
        const idle = Math.sin(t * 0.7 + p.h3 * 20) * 0.05 * (1 - moving); const lean = moving * (cav ? 0.10 : 0.06) + (p.front || 0) * 0.10;
        const ix = p.x + idle * ffx * 0.0, iz = p.z; const scFig = scl * (0.25 + 0.75 * p.vis) * (0.94 + 0.12 * p.h2);
        a.iPos.array.set([ix, y + 0.12, iz, scFig], o * 4); a.iDir.array.set([ffx + Math.sin(t * 0.5 + p.h1 * 9) * 0.03 * (1 - moving), ffz, bob, lean], o * 4); a.iCol.array.set([lerp(col[0], light[0], 0.18), lerp(col[1], light[1], 0.18), lerp(col[2], light[2], 0.18), p.h3], o * 4); a.iMeta.array.set([s.fade, 0, 0, 0], o * 4); a.iLight.array.set(light, o * 3);
      }
    }
    // ambient figures (camps, walkers) added by the ambient layer
    if (this.extra) for (const e of this.extra) { const M = this.kindMesh(e.kind); if (!M || M.n >= M.max) continue; const o = M.n++; const a = M.a; a.iPos.array.set([e.x, mh(e.x, e.z) + 0.1, e.z, e.sc], o * 4); a.iDir.array.set([e.fx, e.fz, e.bob || 0, 0], o * 4); a.iCol.array.set([e.col[0], e.col[1], e.col[2], e.h || 0.3], o * 4); a.iMeta.array.set([0, 0, 0, 0], o * 4); a.iLight.array.set(e.col, o * 3); }
    for (const k in this.meshes) { const M = this.meshes[k]; M.g.instanceCount = M.n; for (const at of Object.values(M.a)) { at.needsUpdate = true; at.updateRanges = []; at.addUpdateRange?.(0, M.n * at.itemSize); } M.mesh.visible = M.n > 0; }
    T.g.instanceCount = T.n; for (const at of Object.values(T.a)) { at.needsUpdate = true; at.updateRanges = []; at.addUpdateRange?.(0, T.n * at.itemSize); } T.mesh.visible = T.n > 0;
    this.dust(t, active, fronts, blocks, wind);
  }
  // dust: puffs born behind moving blocks (stateless: each puff slot is born on a cycle and evaluated at its birth time) and along fronts
  dust(t, active, fronts, blocks, wind) {
    const P = this.puffs.geometry.attributes.aP.array, C = this.puffs.geometry.attributes.aC.array; let n = 0; const mh = blocks.meshH; const dc = this.opts.dustColor || [0.86, 0.76, 0.58];
    const push = (x, y, z, size, a, c = dc) => { if (n >= this.PMAX || a < 0.004) return; P[n * 4] = x; P[n * 4 + 1] = y; P[n * 4 + 2] = z; P[n * 4 + 3] = size; C[n * 4] = c[0]; C[n * 4 + 1] = c[1]; C[n * 4 + 2] = c[2]; C[n * 4 + 3] = a; n++; };
    const amt = this.opts.dust ?? 1;
    if (amt > 0) for (const A of active) { const b = A.b; if (b.d.dust === false) continue; const per = 2.6; const K = Math.min(26, Math.ceil(A.s.len * A.s.scale / 6) + 3) * (b.figKind === 'cavalry' ? 2 : 1);
      for (let q = 0; q < K; q++) { const h = hash01(b.seed, q, 77); const age = ((t / per + h) % 1); const tb = t - age * per; const sb = blocks.state(b, tb); if (sb.alpha < 0.3) continue; const spd = blocks.speedOf(b, tb); const k = clamp((spd - 0.6) / 4); if (k <= 0) continue;
        const hd = sb.heading * DEG; const fx = Math.sin(hd), fz = -Math.cos(hd), rx = Math.cos(hd), rz = Math.sin(hd); const u = (hash01(b.seed, q, 78) - 0.5) * sb.len * sb.scale, v = -sb.dep * sb.scale * (0.2 + 0.5 * hash01(b.seed, q, 79));
        let x = sb.x + rx * u + fx * v, z = sb.z + rz * u + fz * v; const dt = age * per; x += wind[0] * dt * 1.4; z += wind[1] * dt * 1.4; const y = mh(x, z) + 0.6 + dt * 1.1;
        const a = k * 0.22 * amt * Math.sin(Math.PI * clamp(age * 1.15)) * (b.figKind === 'cavalry' ? 1.3 : 1); push(x, y, z, 3.5 + dt * 3.2, a); } }
    if (amt > 0) for (const F of fronts) { const K = Math.min(40, Math.ceil(F.half * 2 / 2.5) + 2); for (let q = 0; q < K; q++) { const h = hash01(q, 91, (F.A.b.seed ^ F.B.b.seed) & 0xffff); const per = 2.2; const age = ((t / per + h) % 1); const dt = age * per;
        const l = (hash01(q, 92, 3) - 0.5) * 2 * F.half; let x = F.cx + F.tx * l + wind[0] * dt, z = F.cz + F.tz * l + wind[1] * dt; const y = mh(x, z) + 0.5 + dt * 0.9;
        push(x, y, z, 2.8 + dt * 2.6, 0.30 * amt * F.k * Math.sin(Math.PI * age)); } }
    if (this.extraPuffs) for (const e of this.extraPuffs) push(e[0], e[1], e[2], e[3], e[4], e[5]);
    const g = this.puffs.geometry; g.setDrawRange(0, n); g.attributes.aP.needsUpdate = true; g.attributes.aC.needsUpdate = true; this.puffs.visible = n > 0; this.nPuffs = n;
  }
  setPx(camera, H) { this.pmat.uniforms.uPx.value = H / (2 * Math.tan(camera.fov * Math.PI / 360)); }
  setVisible(v) { for (const k in this.meshes) this.meshes[k].mesh.visible = v && this.meshes[k].n > 0; this.tiles.mesh.visible = v && this.tiles.n > 0; this.puffs.visible = v && (this.nPuffs || 0) > 0; }
}
export { strHash };
