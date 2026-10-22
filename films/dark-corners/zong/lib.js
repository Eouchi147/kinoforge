// p03 scene-local helpers: multiplane placement, relightable paint material, glow sprites, fine-brush detail pass.
// (Kept out of harness/kit on purpose, scene-local per the author brief.)
import * as THREE from 'three';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

export const DW = 720, DH = 1280;                 // portrait design frame (9:16); everything is painted in these px
export const fFromMM = (mm) => (DH / 24) * mm;    // focal length in design px (24 mm sensor height <-> 1280 px frame)
export const NL = 8;                              // max lights per painted plane

const SRGB = `vec3 srgbToLin(vec3 c){ return c*(c*(c*0.305306011+0.682171111)+0.012522878); }`; // fast sRGB->linear fit

// Canvas -> texture. Canvas2D stores premultiplied sRGB; we upload it premultiplied and *undecoded* so filtering/mips
// are alpha-correct (no dark fringes), then un-premultiply + decode in the shader.
export function tex(canvas, { mip = true } = {}) {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.NoColorSpace; t.premultiplyAlpha = true;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.generateMipmaps = mip; t.minFilter = mip ? THREE.LinearMipmapLinearFilter : THREE.LinearFilter; t.magFilter = THREE.LinearFilter;
  t.anisotropy = 1; t.needsUpdate = true; return t;
}

const planeVert = `varying vec2 vUv; varying vec3 vW;
void main(){ vUv=uv; vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`;
const planeFrag = `${SRGB}
uniform sampler2D map; uniform float uOpacity; uniform vec2 uWipe; uniform vec3 uTint; uniform vec2 uOffset; uniform int uNL; uniform vec4 uLP[${NL}]; uniform vec3 uLC[${NL}];
varying vec2 vUv; varying vec3 vW;
void main(){
  vec4 p=texture2D(map, vUv+uOffset); if(p.a<0.002) discard;
  float wp=smoothstep(uWipe.x, uWipe.x-uWipe.y, vUv.x); if(wp<=0.001) discard; p.a*=wp; p.rgb*=wp;
  vec3 c=srgbToLin(clamp(p.rgb/p.a,0.0,1.0));
  vec3 L=vec3(0.0);
  for(int i=0;i<${NL};i++){ if(i>=uNL) break; vec3 d=vW-uLP[i].xyz; float r=uLP[i].w; float f=1.0/(1.0+dot(d,d)/(r*r)); L+=uLC[i]*f*f; }
  vec3 lit=mix(c, vec3(dot(c, vec3(0.2126,0.7152,0.0722))), 0.65);
  float a=p.a*uOpacity; gl_FragColor=vec4((c*uTint + lit*L*1.25)*a, a);
}`;
export function paintMaterial(map) {
  return new THREE.ShaderMaterial({
    uniforms: { map: { value: map }, uOpacity: { value: 1 }, uWipe: { value: new THREE.Vector2(2, 0.001) }, uTint: { value: new THREE.Vector3(1, 1, 1) }, uOffset: { value: new THREE.Vector2() },
      uNL: { value: 0 }, uLP: { value: Array.from({ length: NL }, () => new THREE.Vector4()) }, uLC: { value: Array.from({ length: NL }, () => new THREE.Vector3()) } },
    vertexShader: planeVert, fragmentShader: planeFrag, transparent: true, depthTest: false, depthWrite: false,
    blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
    blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor,
  });
}
// lights: [{ p: Vector3, r: radius(m), c: [r,g,b] (linear, already x intensity) }]
export function setLights(mat, lights) {
  const u = mat.uniforms; let n = 0;
  for (const l of lights) { if (n >= NL) break; if (!(l.k > 0.0005)) continue; u.uLP.value[n].set(l.p.x, l.p.y, l.p.z, l.r); u.uLC.value[n].set(l.c[0] * l.k, l.c[1] * l.k, l.c[2] * l.k); n++; }
  u.uNL.value = n;
}

// additive glow sprite (round) or soft rectangle (lit window). HDR colour drives bloom/halation.
const glowFrag = `uniform vec3 uColor; uniform float uI; uniform float uCore; uniform float uShape; uniform vec2 uRect; varying vec2 vUv;
void main(){
  vec2 d=(vUv-0.5)*2.0; float v;
  if(uShape<0.5){ float r=length(d); if(r>1.0) discard; v=pow(1.0-r,2.6)*0.5 + exp(-r*r*10.0)*0.35 + (uCore<3000.0 ? exp(-r*r*uCore)*2.2 : 0.0); } // uCore>=3000: halo only
  else { vec2 q=abs(d)/uRect; float inner=(1.0-smoothstep(0.8,1.05,q.x))*(1.0-smoothstep(0.8,1.05,q.y)); float r=length(max(q-1.0,0.0)*uRect); v=inner + (1.0-inner)*0.42*exp(-r*r*22.0); }
  gl_FragColor=vec4(uColor*v*uI, 1.0);
}`;
const glowVert = `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`;
export function glowMesh({ size = 1, color = [1.0, 0.62, 0.28], core = 60, shape = 0, rect = [0.5, 0.5] } = {}) {
  const m = new THREE.ShaderMaterial({
    uniforms: { uColor: { value: new THREE.Vector3(...color) }, uI: { value: 0 }, uCore: { value: core }, uShape: { value: shape }, uRect: { value: new THREE.Vector2(...rect) } },
    vertexShader: glowVert, fragmentShader: glowFrag, transparent: true, depthTest: false, depthWrite: false,
    blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.ZeroFactor, blendDstAlpha: THREE.OneFactor,
  });
  const g = new THREE.Mesh(new THREE.PlaneGeometry(size, size), m); g.frustumCulled = false; return g;
}

// ------------------------------------------------------------------ multiplane setup
// A "setup" = one camera position with a stack of painted planes. Planes are painted in *design px* as seen from the
// setup's reference camera (pos, looking down -z, untilted); a plane at depth D maps 1 design px -> D/f metres.
export class Setup {
  constructor(name, { pos = [0, 0, 0], mm = 35 }) {
    this.name = name; this.pos = pos; this.mm = mm; this.f = fFromMM(mm); this.group = new THREE.Group(); this.group.visible = false;
    this.planes = []; this.glows = [];
  }
  world(px, py, D, out = new THREE.Vector3()) { const s = D / this.f; return out.set(this.pos[0] + (px - DW / 2) * s, this.pos[1] - (py - DH / 2) * s, this.pos[2] - D); }
  pxPerM(D) { return this.f / D; }
  // add a painted canvas covering design rect [x0,y0,x1,y1] at depth D
  plane(name, D, rect, canvas, { order = null } = {}) {
    const [x0, y0, x1, y1] = rect; const s = D / this.f;
    const mat = paintMaterial(tex(canvas));
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry((x1 - x0) * s, (y1 - y0) * s), mat);
    const c = this.world((x0 + x1) / 2, (y0 + y1) / 2, D); mesh.position.copy(c); mesh.frustumCulled = false;
    mesh.renderOrder = order ?? (1e6 - D * 10); mesh.userData = { name, D, rect, base: c.clone() };
    this.group.add(mesh); this.planes.push(mesh); return mesh;
  }
  glow(px, py, D, sizePx, opts = {}, parent = null) {
    const s = D / this.f; const g = glowMesh({ size: sizePx * s, ...opts }); this.world(px, py, D, g.position);
    g.renderOrder = (parent ? parent.renderOrder : 1e6 - D * 10) + 0.5; g.userData = { D, px, py }; this.group.add(g); this.glows.push(g); return g;
  }
  // design-px rect that covers everything any of `cams` sees on the plane at depth D (cams already posed)
  cover(D, cams, margin = 28) {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; const v = new THREE.Vector3(), dir = new THREE.Vector3(); const zP = this.pos[2] - D, s = D / this.f;
    for (const cam of cams) for (let i = 0; i <= 4; i++) for (let j = 0; j <= 4; j++) {
      v.set(-1 + i / 2, -1 + j / 2, 0.5).unproject(cam); dir.copy(v).sub(cam.position).normalize(); const k = (zP - cam.position.z) / dir.z;
      const px = DW / 2 + (cam.position.x + dir.x * k - this.pos[0]) / s, py = DH / 2 - (cam.position.y + dir.y * k - this.pos[1]) / s;
      x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py);
    }
    return [Math.floor(x0 - margin), Math.floor(y0 - margin), Math.ceil(x1 + margin), Math.ceil(y1 + margin)];
  }
}

// ------------------------------------------------------------------ fine-brush detail pass
// Composites a screen-space canvas (tiny figure, ropes, posts) AFTER the kit's finish pass, applying the *same* grade,
// vignette and grain formula (copied uniforms each frame), a small-radius Kuwahara (fine brush) and a canvas weave.
const DetailShader = {
  uniforms: {
    tDiffuse: { value: null }, tDetail: { value: null }, resolution: { value: new THREE.Vector2(DW, DH) }, time: { value: 0 },
    exposure: { value: 1 }, contrast: { value: 1 }, saturation: { value: 1 }, gamma: { value: 1 },
    lift: { value: new THREE.Vector3() }, gain: { value: new THREE.Vector3(1, 1, 1) }, shadowTint: { value: new THREE.Vector3() }, highlightTint: { value: new THREE.Vector3() },
    grain: { value: 0.03 }, grainSize: { value: 1.5 }, vignette: { value: 0.3 }, fade: { value: 1 }, kr: { value: 1 }, weave: { value: 0.03 }, useDetail: { value: 1 },
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader: `
    uniform sampler2D tDiffuse, tDetail; uniform vec2 resolution; uniform float time;
    uniform float exposure, contrast, saturation, gamma; uniform vec3 lift, gain, shadowTint, highlightTint;
    uniform float grain, grainSize, vignette, fade, weave, useDetail; uniform int kr; varying vec2 vUv;
    float hash(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
    float lum(vec3 c){ return dot(c, vec3(0.2126,0.7152,0.0722)); }
    vec4 kuw(vec2 uv){ if(kr<=0) return texture2D(tDetail, uv); vec2 px=1.0/resolution; vec4 best=vec4(0.0); float bv=1e9;
      for(int s=0;s<4;s++){ vec2 off=vec2(s==1||s==3?-1.0:1.0, s>=2?-1.0:1.0); vec4 m=vec4(0.0), q=vec4(0.0); float n=0.0;
        for(int j=0;j<=2;j++){ if(j>kr) break; for(int i=0;i<=2;i++){ if(i>kr) break; vec4 c=texture2D(tDetail, uv+vec2(float(i),float(j))*off*px); m+=c; q+=c*c; n+=1.0; } }
        m/=n; q=q/n-m*m; float v=q.r+q.g+q.b+q.a; if(v<bv){ bv=v; best=m; } }
      return best; }
    void main(){
      vec3 col=texture2D(tDiffuse, vUv).rgb; float ar=resolution.x/resolution.y;
      vec2 px1=1.0/resolution; float near=texture2D(tDetail, vUv).a+texture2D(tDetail, vUv+px1*vec2(2.0,2.0)).a+texture2D(tDetail, vUv-px1*vec2(2.0,2.0)).a+texture2D(tDetail, vUv+px1*vec2(2.0,-2.0)).a+texture2D(tDetail, vUv+px1*vec2(-2.0,2.0)).a;
      if(useDetail>0.5 && near>0.001){ vec4 d=kuw(vUv);
        if(d.a>0.002){ vec3 c=clamp(d.rgb/d.a,0.0,1.0);
          c*=exposure; c=c*gain+lift; c=pow(max(c,0.0), vec3(1.0/gamma)); c=(c-0.5)*contrast+0.5; float l=lum(c); c=mix(vec3(l), c, saturation);
          c+=shadowTint*(1.0-smoothstep(0.0,0.6,l)) + highlightTint*smoothstep(0.4,1.0,l);
          vec2 cuv=(vUv-0.5)*vec2(ar,1.0); float r2=dot(cuv,cuv); c*=1.0-vignette*smoothstep(0.25,1.6,r2*2.2);
          if(grain>0.0){ float g=hash(floor(vUv*resolution/grainSize)+fract(time*61.7)*13.0)-0.5; c+=g*grain*(1.0-0.5*clamp(l,0.0,1.0)); }
          c*=fade; col=mix(col, c, clamp(d.a,0.0,1.0)); } }
      // canvas weave: screen-fixed thread noise (static, so it never swims), strongest in the mids
      vec2 p=vUv*resolution*(720.0/resolution.y);
      float th=hash(vec2(floor(p.y/2.0), 3.7))*0.6 + hash(vec2(floor(p.x/2.0), 9.1))*0.4;
      float fib=hash(floor(p/vec2(5.0,2.0)))*0.5;
      float w=(th*0.8+fib*0.4)-0.6; float m=lum(col); col*=1.0+w*weave*(0.4+2.0*m*(1.0-m));
      gl_FragColor=vec4(col,1.0);
    }`,
};
export function makeDetailPass(post, W, H) {
  const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d', { willReadFrequently: true }); // CPU raster: cheap per-frame upload
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.premultiplyAlpha = true; t.generateMipmaps = false;
  t.minFilter = THREE.LinearFilter; t.magFilter = THREE.LinearFilter;
  const pass = new ShaderPass(DetailShader); pass.uniforms.tDetail.value = t; pass.uniforms.resolution.value.set(W, H);
  // insert right after the finish pass (before the after-finish overlay)
  const passes = post.composer.passes; let idx = passes.length; for (let i = 0; i < passes.length; i++) if (passes[i].uniforms && passes[i].uniforms.kuwaharaRadius) idx = i + 1;
  post.composer.insertPass(pass, idx);
  const sync = (time) => { const f = post.finish, u = pass.uniforms; for (const k of ['exposure', 'contrast', 'saturation', 'gamma', 'grain', 'grainSize', 'vignette', 'fade']) u[k].value = f[k].value;
    for (const k of ['lift', 'gain', 'shadowTint', 'highlightTint']) u[k].value.copy(f[k].value); u.time.value = time; t.needsUpdate = true; };
  return { canvas: c, g, pass, sync, clear: () => { g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, W, H); } };
}
