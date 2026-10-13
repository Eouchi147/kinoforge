// KINOFORGE film kit — shared helpers for scene pages. ES module; import three via the page's importmap.
//   import * as THREE from 'three';
//   import { boot, Timeline, CameraRig, fovFromMM, makeComposer, ... } from '/harness/kit/film.js';
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// ------------------------------------------------------------------ math & randomness
export function rng(seed = 1) { // mulberry32 — deterministic per seed
  let a = seed >>> 0;
  const f = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  f.range = (lo, hi) => lo + (hi - lo) * f();
  f.int = (lo, hi) => Math.floor(f.range(lo, hi + 1));
  f.pick = (arr) => arr[Math.floor(f() * arr.length)];
  f.gauss = () => { const u = 1 - f(), v = f(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  return f;
}
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const remap = (x, a, b, c, d) => c + (d - c) * clamp((x - a) / (b - a));
export const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const ease = {
  linear: (t) => t,
  inQuad: (t) => t * t, outQuad: (t) => t * (2 - t), inOutQuad: (t) => t < .5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  inCubic: (t) => t * t * t, outCubic: (t) => 1 - Math.pow(1 - t, 3), inOutCubic: (t) => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  inQuart: (t) => t * t * t * t, outQuart: (t) => 1 - Math.pow(1 - t, 4), inOutQuart: (t) => t < .5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2,
  inExpo: (t) => t === 0 ? 0 : Math.pow(2, 10 * t - 10), outExpo: (t) => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
  inOutSine: (t) => -(Math.cos(Math.PI * t) - 1) / 2, outSine: (t) => Math.sin(t * Math.PI / 2), inSine: (t) => 1 - Math.cos(t * Math.PI / 2),
  outBack: (t) => { const c = 1.70158; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); },
  outElastic: (t) => t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * (2 * Math.PI / 3)) + 1,
  // animation-principle helpers: anticipation then action then settle (returns 0..1 with a small negative dip first)
  antic: (t, dip = 0.12) => { if (t < 0.2) return -dip * Math.sin(t / 0.2 * Math.PI); const u = (t - 0.2) / 0.8; return 1 - Math.pow(1 - u, 3); },
  hold2s: (t, fps = 24) => Math.floor(t * fps / 2) * 2 / fps, // quantise time to "on 2s"
};
// smooth 1D noise for handheld / drift (sum of incommensurate sines; deterministic)
export function noise1(t, seed = 0) {
  return 0.5 * Math.sin(t * 1.0 + seed) + 0.25 * Math.sin(t * 2.3 + seed * 1.7 + 1.1) + 0.125 * Math.sin(t * 5.1 + seed * 0.3 + 2.2) + 0.0625 * Math.sin(t * 11.7 + 3.3 + seed);
}
// 2D value noise + fbm on the CPU (for canvas textures)
export function valueNoise2D(seed = 1) {
  const r = rng(seed); const P = new Uint8Array(512); const g = new Float32Array(256);
  for (let i = 0; i < 256; i++) { P[i] = i; g[i] = r(); }
  for (let i = 255; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [P[i], P[j]] = [P[j], P[i]]; }
  for (let i = 0; i < 256; i++) P[i + 256] = P[i];
  const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  const n = (x, y) => {
    const X = Math.floor(x) & 255, Y = Math.floor(y) & 255; const xf = x - Math.floor(x), yf = y - Math.floor(y);
    const a = g[P[P[X] + Y]], b = g[P[P[X + 1] + Y]], c = g[P[P[X] + Y + 1]], d = g[P[P[X + 1] + Y + 1]];
    const u = fade(xf), v = fade(yf); return lerp(lerp(a, b, u), lerp(c, d, u), v);
  };
  n.fbm = (x, y, oct = 5, lac = 2, gain = 0.5) => { let s = 0, a = 1, f = 1, norm = 0; for (let i = 0; i < oct; i++) { s += a * n(x * f, y * f); norm += a; a *= gain; f *= lac; } return s / norm; };
  return n;
}

// ------------------------------------------------------------------ timeline (shots)
export class Timeline {
  constructor(shots) { this.shots = shots.map((s, i) => ({ ...s, i })); let t = 0; for (const s of this.shots) { s.start = t; t += s.dur; } this.total = t; }
  at(t) { let s = this.shots[this.shots.length - 1]; for (const x of this.shots) if (t < x.start + x.dur) { s = x; break; } const local = t - s.start; return { i: s.i, shot: s, t: local, u: clamp(local / s.dur), start: s.start, name: s.name }; }
}

// ------------------------------------------------------------------ camera
// vertical FOV in degrees for a full-frame-equivalent focal length (24 mm sensor height)
export const fovFromMM = (mm) => 2 * Math.atan(12 / mm) * 180 / Math.PI;
export class CameraRig {
  constructor(camera) { this.cam = camera; this.pos = new THREE.Vector3(); this.target = new THREE.Vector3(); this.roll = 0; }
  lens(mm) { this.cam.fov = fovFromMM(mm); this.cam.updateProjectionMatrix(); return this; }
  // interpolate position & target between two setups: a = {pos:[x,y,z], look:[x,y,z], mm}, b likewise
  move(a, b, u, easing = ease.inOutCubic) {
    const k = easing(clamp(u));
    this.pos.set(lerp(a.pos[0], b.pos[0], k), lerp(a.pos[1], b.pos[1], k), lerp(a.pos[2], b.pos[2], k));
    this.target.set(lerp(a.look[0], b.look[0], k), lerp(a.look[1], b.look[1], k), lerp(a.look[2], b.look[2], k));
    if (a.mm && b.mm) this.lens(lerp(a.mm, b.mm, k)); else if (a.mm) this.lens(a.mm);
    return this;
  }
  set(a) { return this.move(a, a, 0); }
  // apply handheld/breathing jitter: amp in world units at the camera, rot in radians
  handheld(t, amp = 0.01, rot = 0.002, speed = 1, seed = 0) {
    this._hh = { t, amp, rot, speed, seed }; return this;
  }
  apply() {
    const c = this.cam; c.position.copy(this.pos); c.lookAt(this.target);
    if (this._hh) { const { t, amp, rot, speed, seed } = this._hh; const s = t * speed;
      c.position.x += amp * noise1(s * 0.9, seed + 1); c.position.y += amp * noise1(s * 1.1, seed + 2);
      c.rotateX(rot * noise1(s * 0.7, seed + 3)); c.rotateY(rot * noise1(s * 0.8, seed + 4)); c.rotateZ(rot * 0.5 * noise1(s * 0.5, seed + 5)); this._hh = null; }
    if (this.roll) c.rotateZ(this.roll);
    return this;
  }
}

// ------------------------------------------------------------------ procedural canvas textures
export function fbmCanvas(w, h, { seed = 1, scale = 4, oct = 5, gain = 0.5, lo = 0, hi = 255, fn = null } = {}) {
  const n = valueNoise2D(seed); const c = document.createElement('canvas'); c.width = w; c.height = h;
  const ctx = c.getContext('2d'); const img = ctx.createImageData(w, h); const d = img.data;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let v = n.fbm(x / w * scale, y / h * scale, oct, 2, gain); if (fn) v = fn(v, x / w, y / h);
    const g = lo + (hi - lo) * clamp(v); const i = (y * w + x) * 4; d[i] = d[i + 1] = d[i + 2] = g; d[i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0); return c;
}
export function canvasTexture(canvas, { srgb = true, repeat = 1, wrap = true } = {}) {
  const t = new THREE.CanvasTexture(canvas); if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  if (wrap) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat, repeat); }
  t.anisotropy = 4; return t;
}
// grayscale fbm as a DataTexture usable as bump/roughness
export function fbmTexture(w, h, opts) { const t = canvasTexture(fbmCanvas(w, h, opts), { srgb: false, ...opts }); return t; }
// a 5-step gradient map for MeshToonMaterial
export function toonGradient(steps = 4) {
  const data = new Uint8Array(steps * 4); for (let i = 0; i < steps; i++) { const v = Math.round(255 * (i / (steps - 1))); data[i * 4] = data[i * 4 + 1] = data[i * 4 + 2] = v; data[i * 4 + 3] = 255; }
  const t = new THREE.DataTexture(data, steps, 1, THREE.RGBAFormat); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t;
}

// ------------------------------------------------------------------ particles & volumetrics
const spriteVert = `attribute float aSize; attribute float aSeed; uniform float uTime; uniform float uDrift; uniform vec3 uWind; uniform float uScale; varying float vSeed; varying float vAlpha;
void main(){ vSeed=aSeed; vec3 p=position; float ph=aSeed*6.2831; p.x+=sin(uTime*0.37+ph)*uDrift+uWind.x*uTime; p.y+=cos(uTime*0.23+ph*1.3)*uDrift*0.6+uWind.y*uTime; p.z+=sin(uTime*0.31+ph*0.7)*uDrift+uWind.z*uTime;
 vec4 mv=modelViewMatrix*vec4(p,1.0); gl_PointSize=max(1.0, aSize*uScale/max(0.1,-mv.z)); vAlpha=smoothstep(0.0,1.0,sin(uTime*0.8+ph)*0.5+0.5); gl_Position=projectionMatrix*mv; }`;
const spriteFrag = `uniform vec3 uColor; uniform float uOpacity; varying float vSeed; varying float vAlpha;
void main(){ vec2 d=gl_PointCoord-0.5; float r=length(d); float a=smoothstep(0.5,0.05,r); a*=a; gl_FragColor=vec4(uColor,a*uOpacity*(0.5+0.5*vAlpha)); }`;
// soft drifting motes (dust, embers, snow, ash). box = [w,h,d] centred at `center`.
// size = world-space diameter (e.g. 0.03 for dust in a room). Call p.update(t, camera, H) each frame.
export function dustPoints({ count = 800, box = [10, 6, 10], center = [0, 0, 0], size = 0.03, color = 0xffffff, opacity = 0.5, drift = 0.1, wind = [0, 0, 0], seed = 7, blending = THREE.AdditiveBlending } = {}) {
  const r = rng(seed); const pos = new Float32Array(count * 3), sz = new Float32Array(count), sd = new Float32Array(count);
  for (let i = 0; i < count; i++) { pos[i * 3] = center[0] + (r() - .5) * box[0]; pos[i * 3 + 1] = center[1] + (r() - .5) * box[1]; pos[i * 3 + 2] = center[2] + (r() - .5) * box[2]; sz[i] = size * (0.4 + r() * 1.2); sd[i] = r(); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aSize', new THREE.BufferAttribute(sz, 1)); g.setAttribute('aSeed', new THREE.BufferAttribute(sd, 1));
  const m = new THREE.ShaderMaterial({ uniforms: { uTime: { value: 0 }, uDrift: { value: drift }, uWind: { value: new THREE.Vector3(...wind) }, uColor: { value: new THREE.Color(color) }, uOpacity: { value: opacity }, uScale: { value: 500 } }, vertexShader: spriteVert, fragmentShader: spriteFrag, transparent: true, depthWrite: false, blending });
  const p = new THREE.Points(g, m); p.update = (t, camera, H) => { m.uniforms.uTime.value = t; if (camera && H) m.uniforms.uScale.value = H / (2 * Math.tan(camera.fov * Math.PI / 360)); }; return p;
}
// additive light shaft: a cone (apex at origin pointing -Y by default) fading with distance and edge, with slow noise
const shaftVert = `varying vec3 vPos; varying vec2 vUv; varying float vNdotV; void main(){ vUv=uv; vPos=position; vec4 mv=modelViewMatrix*vec4(position,1.0); vec3 n=normalize(normalMatrix*normal); vNdotV=abs(dot(n, normalize(-mv.xyz))); gl_Position=projectionMatrix*mv; }`;
const shaftFrag = `uniform vec3 uColor; uniform float uIntensity; uniform float uTime; uniform float uLength; varying vec3 vPos; varying vec2 vUv; varying float vNdotV;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);} float n2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void main(){ float along=clamp(-vPos.y/uLength,0.0,1.0); float a=(1.0-along*0.8); a*=smoothstep(0.0,0.45,vNdotV); a*=smoothstep(0.0,0.08,along); a*=smoothstep(1.0,0.82,along);
 float nz=n2(vec2(vUv.x*5.0+uTime*0.04, along*2.5-uTime*0.06))*0.7+0.3; nz*=0.6+0.4*n2(vec2(vUv.x*17.0-uTime*0.02, along*9.0)); gl_FragColor=vec4(uColor*uIntensity*a*nz*0.35, 1.0); }`;
export function lightShaft({ length = 10, radiusTop = 0.3, radiusBottom = 2.5, color = 0xffe3b0, intensity = 1.0 } = {}) {
  const g = new THREE.CylinderGeometry(radiusTop, radiusBottom, length, 24, 1, true); g.translate(0, -length / 2, 0);
  const m = new THREE.ShaderMaterial({ uniforms: { uColor: { value: new THREE.Color(color) }, uIntensity: { value: intensity }, uTime: { value: 0 }, uLength: { value: length } }, vertexShader: shaftVert, fragmentShader: shaftFrag, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(g, m); mesh.update = (t) => { m.uniforms.uTime.value = t; }; return mesh;
}

// ------------------------------------------------------------------ post: finish pass (grade, halation, grain, vignette, letterbox, modes)
const FinishShader = {
  uniforms: {
    tDiffuse: { value: null }, resolution: { value: new THREE.Vector2(1280, 720) }, time: { value: 0 },
    exposure: { value: 1.0 }, contrast: { value: 1.0 }, saturation: { value: 1.0 }, gamma: { value: 1.0 },
    lift: { value: new THREE.Vector3(0, 0, 0) }, gain: { value: new THREE.Vector3(1, 1, 1) },
    shadowTint: { value: new THREE.Vector3(0, 0, 0) }, highlightTint: { value: new THREE.Vector3(0, 0, 0) },
    halation: { value: 0.0 }, halationThreshold: { value: 0.75 }, grain: { value: 0.05 }, grainSize: { value: 1.5 },
    vignette: { value: 0.3 }, aberration: { value: 0.0 }, letterbox: { value: 0.0 }, fade: { value: 1.0 }, weave: { value: 0.0 },
    mode: { value: 0 }, modeAmount: { value: 1.0 }, modeParams: { value: new THREE.Vector3(0, 0, 0) }, kuwaharaRadius: { value: 4 },
    palette: { value: new THREE.Vector3(8, 8, 8) }, // pixel mode: levels per channel
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform vec2 resolution; uniform float time;
    uniform float exposure, contrast, saturation, gamma; uniform vec3 lift, gain, shadowTint, highlightTint;
    uniform float halation, halationThreshold, grain, grainSize, vignette, aberration, letterbox, fade, weave;
    uniform int mode; uniform float modeAmount; uniform vec3 modeParams; uniform int kuwaharaRadius; uniform vec3 palette;
    varying vec2 vUv;
    float hash(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
    float lum(vec3 c){ return dot(c, vec3(0.2126,0.7152,0.0722)); }
    vec3 sampleAt(vec2 uv){ return texture2D(tDiffuse, uv).rgb; }
    vec3 kuwahara(vec2 uv){ vec2 px=1.0/resolution; int R=kuwaharaRadius; vec3 best=vec3(0.0); float bestVar=1e9;
      for(int s=0;s<4;s++){ vec2 off=vec2(s==1||s==3?-1.0:1.0, s>=2?-1.0:1.0); vec3 m=vec3(0.0); vec3 sq=vec3(0.0); float n=0.0;
        for(int j=0;j<=8;j++){ if(j>R) break; for(int i=0;i<=8;i++){ if(i>R) break; vec3 c=sampleAt(uv+vec2(float(i),float(j))*off*px); m+=c; sq+=c*c; n+=1.0; } }
        m/=n; sq=sq/n-m*m; float v=sq.r+sq.g+sq.b; if(v<bestVar){ bestVar=v; best=m; } }
      return best; }
    void main(){
      vec2 uv=vUv; vec2 px=1.0/resolution; float ar=resolution.x/resolution.y;
      // gate weave
      if(weave>0.0){ uv+=vec2(sin(time*7.3)*0.3+sin(time*13.1)*0.2, cos(time*5.7)*0.5)*weave*px; }
      vec2 cuv=(uv-0.5)*vec2(ar,1.0); float r2=dot(cuv,cuv);
      vec3 col;
      if(mode==1){ // CRT / VHS: curvature, chroma bleed, tape noise band, horizontal jitter
        vec2 c=uv-0.5; c*=1.0+r2*0.12*modeAmount; vec2 u2=c+0.5;
        float band=smoothstep(0.0,0.02,abs(fract(time*0.11)-u2.y)) ; float jit=(1.0-band)*0.015*hash(vec2(floor(u2.y*180.0),floor(time*60.0)))*modeAmount;
        u2.x+=jit; float bleed=2.5*px.x*modeAmount;
        col=vec3(texture2D(tDiffuse,u2+vec2(bleed,0.0)).r, texture2D(tDiffuse,u2).g, texture2D(tDiffuse,u2-vec2(bleed,0.0)).b);
        // soften chroma: average neighbours
        vec3 nb=(texture2D(tDiffuse,u2+vec2(3.0*px.x,0.0)).rgb+texture2D(tDiffuse,u2-vec2(3.0*px.x,0.0)).rgb)*0.5; col=mix(col, vec3(lum(col))+ (nb-vec3(lum(nb))), 0.5*modeAmount);
        if(u2.x<0.0||u2.x>1.0||u2.y<0.0||u2.y>1.0) col=vec3(0.0);
        uv=u2;
      } else if(mode==2){ // pixel art: pixelate to modeParams.x pixels wide
        float pw=max(modeParams.x, 32.0); vec2 g=vec2(pw, pw/ar); vec2 q=(floor(uv*g)+0.5)/g; col=sampleAt(q); uv=q;
      } else if(mode==4){ col=kuwahara(uv); }
      else { // normal: chromatic aberration at edges only
        if(aberration>0.0){ vec2 d=cuv*r2*aberration*px*40.0; col=vec3(sampleAt(uv+d).r, sampleAt(uv).g, sampleAt(uv-d).b); } else col=sampleAt(uv);
      }
      // halation: warm bleed from bright areas (cheap 12-tap ring blur of thresholded highlights)
      if(halation>0.0){ vec3 h=vec3(0.0); float rad=18.0; for(int i=0;i<12;i++){ float a=float(i)/12.0*6.2831; vec2 o=vec2(cos(a),sin(a))*rad*px; vec3 s=sampleAt(uv+o); float l=lum(s); h+=s*smoothstep(halationThreshold,1.0,l); }
        h/=12.0; col+=h*vec3(1.0,0.45,0.25)*halation*1.5; }
      // grade
      col*=exposure; col=col*gain+lift; col=pow(max(col,0.0), vec3(1.0/gamma));
      col=(col-0.5)*contrast+0.5; float l=lum(col); col=mix(vec3(l), col, saturation);
      col+=shadowTint*(1.0-smoothstep(0.0,0.6,l)) + highlightTint*smoothstep(0.4,1.0,l);
      if(mode==2){ col*=1.0-vignette*smoothstep(0.25,1.6,r2*2.2); // quantise + ordered dither
        float bx=mod(floor(uv.x*resolution.x/ (resolution.x/max(modeParams.x,32.0))),4.0), by=mod(floor(uv.y*resolution.y/(resolution.x/max(modeParams.x,32.0))),4.0);
        float bayer[16]; bayer[0]=0.;bayer[1]=8.;bayer[2]=2.;bayer[3]=10.;bayer[4]=12.;bayer[5]=4.;bayer[6]=14.;bayer[7]=6.;bayer[8]=3.;bayer[9]=11.;bayer[10]=1.;bayer[11]=9.;bayer[12]=15.;bayer[13]=7.;bayer[14]=13.;bayer[15]=5.;
        float d=(bayer[int(bx)+int(by)*4]/16.0-0.5)*modeParams.y; col=floor((col+d)*palette+0.5)/palette; }
      if(mode==3){ // halftone dots in shadows (angle modeParams.x, cell px modeParams.y)
        float ang=modeParams.x; float cell=max(modeParams.y,3.0); mat2 rot=mat2(cos(ang),-sin(ang),sin(ang),cos(ang)); vec2 p=rot*(uv*resolution); vec2 f=fract(p/cell)-0.5; float d=length(f);
        float dark=1.0-l; float dot=smoothstep(dark*0.7+0.02, dark*0.7-0.08, d); col=mix(col, col*(1.0-0.75*modeAmount), dot*smoothstep(0.25,0.75,dark)); }
      if(mode==1){ float sl=0.5+0.5*sin(uv.y*resolution.y*3.1416); col*=1.0-0.35*modeAmount*sl; col*=1.0-0.06*modeAmount*hash(vec2(time*3.0,0.5)); }
      // vignette (<=0.5 stop by default) — in pixel mode it is applied before quantisation (see above)
      if(mode!=2) col*=1.0-vignette*smoothstep(0.25,1.6,r2*2.2);
      // grain: finer in highlights
      if(grain>0.0 && mode!=2){ float g=hash(floor(uv*resolution/grainSize)+fract(time*61.7)*13.0)-0.5; col+=g*grain*(1.0-0.5*clamp(l,0.0,1.0)); }
      // letterbox bars
      if(letterbox>0.0){ float bar=(1.0-ar/letterbox)*0.5; if(uv.y<bar||uv.y>1.0-bar) col=vec3(0.0); }
      col*=fade;
      gl_FragColor=vec4(col,1.0);
    }`,
};
const OverlayShader = {
  uniforms: { tDiffuse: { value: null }, tOverlay: { value: null } },
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader: `uniform sampler2D tDiffuse, tOverlay; varying vec2 vUv; void main(){ vec4 b=texture2D(tDiffuse,vUv); vec4 o=texture2D(tOverlay,vUv); gl_FragColor=vec4(mix(b.rgb,o.rgb,o.a),1.0);} `,
};
export const GRADES = { // starting points; tune per project (R-4-07: one grade philosophy per project)
  none: {},
  noir: { saturation: 0.15, contrast: 1.25, lift: [-0.02, -0.02, -0.01], shadowTint: [0, 0.01, 0.03], highlightTint: [0.04, 0.03, 0.0], halation: 0.35, grain: 0.07, vignette: 0.4 },
  tealOrange: { saturation: 1.05, contrast: 1.08, shadowTint: [-0.02, 0.01, 0.05], highlightTint: [0.05, 0.02, -0.03], halation: 0.15, grain: 0.035, vignette: 0.25 },
  bleach: { saturation: 0.45, contrast: 1.3, gamma: 0.95, halation: 0.1, grain: 0.08, vignette: 0.35 },
  painterly: { saturation: 1.1, contrast: 1.02, halation: 0.2, grain: 0.03, vignette: 0.3, mode: 4, kuwaharaRadius: 4 },
  cel: { saturation: 1.15, contrast: 1.1, halation: 0.0, grain: 0.015, vignette: 0.15 },
  sepia: { saturation: 0.35, contrast: 1.1, shadowTint: [0.03, 0.01, -0.03], highlightTint: [0.08, 0.05, 0.0], halation: 0.3, grain: 0.06, vignette: 0.45 },
  ember: { saturation: 0.9, contrast: 1.15, shadowTint: [0.0, -0.005, 0.02], highlightTint: [0.06, 0.03, 0.0], halation: 0.4, grain: 0.05, vignette: 0.4 },
  vhs: { saturation: 0.8, contrast: 1.05, grain: 0.12, grainSize: 2, vignette: 0.5, mode: 1, modeAmount: 1.0, halation: 0.2 },
  pixel: { saturation: 1.1, contrast: 1.05, grain: 0.0, vignette: 0.2, mode: 2, modeParams: [320, 0.08, 0], palette: [6, 6, 6] },
  halftone: { saturation: 0.6, contrast: 1.2, grain: 0.04, vignette: 0.35, mode: 3, modeParams: [0.6, 5, 0], modeAmount: 1.0 },
};
export function applyGrade(uniforms, preset, overrides = {}) {
  const p = { ...GRADES[preset] || {}, ...overrides };
  for (const [k, v] of Object.entries(p)) { if (!(k in uniforms)) continue; const u = uniforms[k]; if (u.value && u.value.isVector3) u.value.set(...v); else u.value = v; }
}
/** makeComposer(renderer, scene, camera, { bloom:{strength,radius,threshold}, bokeh:{focus,aperture,maxblur}, grade:'noir', finish:{...uniform overrides}, overlay:true })
 *  returns { composer, finish (uniforms), overlay: {canvas, ctx, tex}, render(t) } */
export function makeComposer(renderer, scene, camera, { bloom = null, bokeh = null, grade = 'none', finish = {}, overlay = true, overlayAfterFinish = false, width, height } = {}) {
  const w = width || renderer.domElement.width, h = height || renderer.domElement.height;
  const composer = new EffectComposer(renderer); composer.setSize(w, h);
  composer.addPass(new RenderPass(scene, camera));
  let bokehPass = null;
  if (bokeh) { bokehPass = new BokehPass(scene, camera, { focus: bokeh.focus ?? 10, aperture: bokeh.aperture ?? 0.0005, maxblur: bokeh.maxblur ?? 0.01 }); composer.addPass(bokehPass); }
  let bloomPass = null;
  if (bloom) { bloomPass = new UnrealBloomPass(new THREE.Vector2(w, h), bloom.strength ?? 0.6, bloom.radius ?? 0.4, bloom.threshold ?? 0.8); composer.addPass(bloomPass); }
  composer.addPass(new OutputPass());
  const finishPass = new ShaderPass(FinishShader); finishPass.uniforms.resolution.value.set(w, h);
  applyGrade(finishPass.uniforms, grade, finish);
  let ov = null, ovPass = null;
  if (overlay) {
    const c = document.createElement('canvas'); c.width = w; c.height = h; const ctx = c.getContext('2d');
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.NoColorSpace; // composited in display space: no decode
    ovPass = new ShaderPass(OverlayShader); ovPass.uniforms.tOverlay.value = tex; ov = { canvas: c, ctx, tex, clear: () => ctx.clearRect(0, 0, w, h) };
  }
  if (ovPass && !overlayAfterFinish) composer.addPass(ovPass);
  composer.addPass(finishPass);
  if (ovPass && overlayAfterFinish) composer.addPass(ovPass);
  return { composer, finish: finishPass.uniforms, bloom: bloomPass, bokeh: bokehPass, overlay: ov,
    render(t) { finishPass.uniforms.time.value = t; if (ov) ov.tex.needsUpdate = true; composer.render(); } };
}

// ------------------------------------------------------------------ overlay text (titles, captions)
export function drawText(ctx, text, { x, y, font = '400 48px "Inter"', color = '#fff', align = 'center', baseline = 'middle', alpha = 1, spacing = 0, shadow = 0, shadowColor = 'rgba(0,0,0,0.8)', maxWidth = null, lineHeight = 1.25 } = {}) {
  ctx.save(); ctx.globalAlpha = alpha; ctx.font = font; ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = baseline;
  if (spacing) ctx.letterSpacing = spacing + 'px';
  if (shadow) { ctx.shadowColor = shadowColor; ctx.shadowBlur = shadow; }
  const lines = []; if (maxWidth) { const words = String(text).split(' '); let cur = ''; for (const w of words) { const test = cur ? cur + ' ' + w : w; if (ctx.measureText(test).width > maxWidth && cur) { lines.push(cur); cur = w; } else cur = test; } if (cur) lines.push(cur); } else lines.push(...String(text).split('\n'));
  const size = parseInt((font.match(/(\d+)px/) || [0, 48])[1]) * lineHeight; const y0 = y - (lines.length - 1) * size / 2;
  lines.forEach((l, i) => ctx.fillText(l, x, y0 + i * size)); ctx.restore();
}
// fade-in/out envelope for titles: returns alpha for local time t over duration d with in/out seconds
export const env = (t, d, tin = 0.4, tout = 0.4) => clamp(Math.min(t / tin, (d - t) / tout));
export async function loadFonts(list) { // e.g. [['Bebas Neue', 400], ['Inter', 700]]
  for (const [fam, w = 400] of list) { try { await document.fonts.load(`${w} 20px "${fam}"`); } catch (e) { console.log('font failed', fam, e); } }
  await document.fonts.ready;
}

// ------------------------------------------------------------------ boot: creates renderer/canvas from the query, wires KF
/** boot({ fps, duration|shots, aspect, init(ctx), render(ctx, i, t) }) — ctx = { THREE, renderer, canvas, W, H, timeline } */
export async function boot({ fps = 24, duration = null, shots = null, init, render, fonts = [], alpha = false, toneMapping = THREE.ACESFilmicToneMapping, exposure = 1.0 }) {
  const q = new URLSearchParams(location.search);
  const W = +q.get('w') || 1280, H = +q.get('h') || 720; fps = +q.get('fps') || fps;
  const canvas = document.createElement('canvas'); canvas.width = W; canvas.height = H; canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  document.body.style.margin = '0'; document.body.style.background = '#000'; document.body.appendChild(canvas);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha, powerPreference: 'high-performance' });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.toneMapping = toneMapping; renderer.toneMappingExposure = exposure; renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
  const timeline = shots ? new Timeline(shots) : null; duration = duration ?? (timeline ? timeline.total : 10);
  const ctx = { THREE, renderer, canvas, W, H, fps, timeline, q, duration };
  if (fonts.length) await loadFonts(fonts);
  await init(ctx);
  window.KF = { width: W, height: H, fps, duration, canvas, shots: shots || [], render: async (i, t) => { await render(ctx, i, t); } };
  window.KF_READY = true;
  if (q.get('preview')) { // live preview in a normal browser: loop time
    const t0 = performance.now(); const loop = async () => { const t = ((performance.now() - t0) / 1000) % duration; await render(ctx, Math.floor(t * fps), t); requestAnimationFrame(loop); }; loop();
  }
  return ctx;
}
export { THREE };

// ------------------------------------------------------------------ height map (canvas, grayscale) -> normal map canvas (tangent space, +Y up)
export function heightToNormal(src, strength = 2.0) {
  const w = src.width, h = src.height; const sctx = src.getContext('2d'); const d = sctx.getImageData(0, 0, w, h).data;
  const c = document.createElement('canvas'); c.width = w; c.height = h; const ctx = c.getContext('2d'); const out = ctx.createImageData(w, h); const o = out.data;
  const H = (x, y) => d[(((y + h) % h) * w + ((x + w) % w)) * 4] / 255;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const dx = (H(x + 1, y) - H(x - 1, y)) * strength, dy = (H(x, y + 1) - H(x, y - 1)) * strength;
    let nx = -dx, ny = dy, nz = 1; const l = Math.hypot(nx, ny, nz); nx /= l; ny /= l; nz /= l; const i = (y * w + x) * 4;
    o[i] = (nx * 0.5 + 0.5) * 255; o[i + 1] = (ny * 0.5 + 0.5) * 255; o[i + 2] = (nz * 0.5 + 0.5) * 255; o[i + 3] = 255;
  }
  ctx.putImageData(out, 0, 0); return c;
}
// blur a canvas in place (box blur radius r) — handy before heightToNormal for soft carving
export function blurCanvas(src, r = 2) { const c = document.createElement('canvas'); c.width = src.width; c.height = src.height; const g = c.getContext('2d'); g.filter = `blur(${r}px)`; g.drawImage(src, 0, 0); return c; }
