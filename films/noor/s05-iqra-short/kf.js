// NOOR / Lantern Road core, PORTRAIT 9:16 for the short: the frame is 720x1280 design px, but the sets keep the film's
// 16:9 design space (origin 640,360, reference focal 1050 px), so the same painted sets are reframed by the camera. Derived from proto/p03-lantern-road/lib.js; the proto stays untouched.
// - multiplane Setup in a 1280x720 design frame (planes are painted in design px as seen by a 35 mm reference camera)
// - relightable paint material, additive glow sprites
// - a lean post chain that costs about a third of the kit's: half-res Kuwahara, 2-level cheap bloom, one final pass that
//   also composites the fine-brush detail layer (figures, banners) and the crisp text overlay.
import * as THREE from 'three';
import { FullScreenQuad } from 'three/addons/postprocessing/Pass.js';

export const DW = 720, DH = 1280, CX = 640, CY = 360;
export const FREF = (720 / 24) * 35;                    // reference focal length in design px (35 mm on a 24 mm tall sensor)
export const fovV = (mm) => 2 * Math.atan(12 / mm) * 180 / Math.PI;
export const NL = 8;                                    // max lights per painted plane

const SRGB = `vec3 srgbToLin(vec3 c){ return c*(c*(c*0.305306011+0.682171111)+0.012522878); }`;

export function tex(canvas, { mip = true } = {}) {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.NoColorSpace; t.premultiplyAlpha = true;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.generateMipmaps = mip; t.minFilter = mip ? THREE.LinearMipmapLinearFilter : THREE.LinearFilter; t.magFilter = THREE.LinearFilter;
  t.anisotropy = 1; t.needsUpdate = true; return t;
}

const planeVert = `varying vec2 vUv; varying vec3 vW;
void main(){ vUv=uv; vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`;
// wind: uSway = (amplitude in uv, ground line v (0 bottom .. 1 top), spatial frequency); texels above the ground line lean and shimmer with time (grass strips: ground line 0)
const planeFrag = `${SRGB}
uniform sampler2D map; uniform float uOpacity; uniform vec3 uTint; uniform vec2 uOffset; uniform vec3 uSway; uniform float uTime; uniform int uNL; uniform vec4 uLP[${NL}]; uniform vec3 uLC[${NL}];
varying vec2 vUv; varying vec3 vW;
void main(){
  vec2 uvq=vUv+uOffset;
  if(uSway.x>0.0){ float hgt=clamp((vUv.y-uSway.y)/max(0.05,1.0-uSway.y),0.0,1.0); uvq.x+=uSway.x*hgt*(sin(uTime*1.7+vUv.x*uSway.z)+0.6*sin(uTime*2.9+vUv.x*uSway.z*2.3+1.3)+0.5*sin(uTime*0.6)); }
  vec4 p=texture2D(map, uvq); if(p.a<0.002) discard;
  vec3 c=srgbToLin(clamp(p.rgb/p.a,0.0,1.0));
  vec3 L=vec3(0.0);
  for(int i=0;i<${NL};i++){ if(i>=uNL) break; vec3 d=vW-uLP[i].xyz; float r=uLP[i].w; float f=1.0/(1.0+dot(d,d)/(r*r)); L+=uLC[i]*f*f; }
  vec3 lit=mix(c, vec3(dot(c, vec3(0.2126,0.7152,0.0722))), 0.65);
  float a=p.a*uOpacity; gl_FragColor=vec4((c*uTint + lit*L*1.25)*a, a);
}`;
export function paintMaterial(map) {
  return new THREE.ShaderMaterial({
    uniforms: { map: { value: map }, uOpacity: { value: 1 }, uTint: { value: new THREE.Vector3(1, 1, 1) }, uOffset: { value: new THREE.Vector2() }, uSway: { value: new THREE.Vector3() }, uTime: { value: 0 },
      uNL: { value: 0 }, uLP: { value: Array.from({ length: NL }, () => new THREE.Vector4()) }, uLC: { value: Array.from({ length: NL }, () => new THREE.Vector3()) } },
    vertexShader: planeVert, fragmentShader: planeFrag, transparent: true, depthTest: false, depthWrite: false,
    blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
    blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor,
  });
}
// lights: [{ p: Vector3 (world), r: radius(m), c: [r,g,b] linear, k: intensity }]
export function setLights(mat, lights) {
  const u = mat.uniforms; let n = 0;
  for (const l of lights) { if (n >= NL) break; if (!(l.k > 0.0005)) continue; u.uLP.value[n].set(l.p.x, l.p.y, l.p.z, l.r); u.uLC.value[n].set(l.c[0] * l.k, l.c[1] * l.k, l.c[2] * l.k); n++; }
  u.uNL.value = n;
}

// additive glow sprite (round) or soft rectangle (lit window)
const glowFrag = `uniform vec3 uColor; uniform float uI; uniform float uCore; uniform float uShape; uniform vec2 uRect; varying vec2 vUv;
void main(){
  vec2 d=(vUv-0.5)*2.0; float v;
  if(uShape<0.5){ float r=length(d); if(r>1.0) discard; v=pow(1.0-r,2.6)*0.5 + exp(-r*r*10.0)*0.35 + (uCore<3000.0 ? exp(-r*r*uCore)*2.2 : 0.0); }
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
export class Setup {
  constructor(name) { this.name = name; this.f = FREF; this.group = new THREE.Group(); this.group.visible = false; this.planes = []; this.glows = []; }
  world(px, py, D, out = new THREE.Vector3()) { const s = D / this.f; return out.set((px - CX) * s, -(py - CY) * s, -D); }
  plane(name, D, rect, canvas, { order = null, mip = true } = {}) {
    const [x0, y0, x1, y1] = rect; const s = D / this.f;
    const mat = paintMaterial(tex(canvas, { mip }));
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry((x1 - x0) * s, (y1 - y0) * s), mat);
    const c = this.world((x0 + x1) / 2, (y0 + y1) / 2, D); mesh.position.copy(c); mesh.frustumCulled = false;
    mesh.renderOrder = order ?? (1e6 - D * 10); mesh.userData = { name, D, rect, base: c.clone() };
    this.group.add(mesh); this.planes.push(mesh); return mesh;
  }
  glow(px, py, D, sizePx, opts = {}, parent = null) {
    const s = D / this.f; const g = glowMesh({ size: sizePx * s, ...opts }); this.world(px, py, D, g.position);
    g.renderOrder = (parent ? parent.renderOrder : 1e6 - D * 10) + 0.5; g.userData = { D, px, py, sizePx }; g.visible = false; this.group.add(g); this.glows.push(g); return g;
  }
  // design-px rect that covers everything the given (posed) cameras see on the plane at depth D
  cover(D, cams, margin = 24) {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; const v = new THREE.Vector3(), dir = new THREE.Vector3(); const zP = -D, s = D / this.f;
    for (const cam of cams) for (let i = 0; i <= 4; i++) for (let j = 0; j <= 4; j++) {
      v.set(-1 + i / 2, -1 + j / 2, 0.5).unproject(cam); dir.copy(v).sub(cam.position).normalize(); if (dir.z > -0.02) continue; const k = (zP - cam.position.z) / dir.z;
      const px = CX + (cam.position.x + dir.x * k) / s, py = CY - (cam.position.y + dir.y * k) / s;
      x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py);
    }
    return [Math.floor(x0 - margin), Math.floor(y0 - margin), Math.ceil(x1 + margin), Math.ceil(y1 + margin)];
  }
  dispose() {
    for (const p of this.planes) { const t = p.material.uniforms.map.value; if (t.image && t.image.width) { t.image.width = 1; t.image.height = 1; } t.dispose(); p.material.dispose(); p.geometry.dispose(); }
    for (const g of this.glows) { g.material.dispose(); g.geometry.dispose(); }
    this.group.removeFromParent(); this.planes = []; this.glows = [];
  }
}

// ------------------------------------------------------------------ lean post chain
const QUAD_VERT = `varying vec2 vUv; void main(){ vUv=position.xy*0.5+0.5; gl_Position=vec4(position.xy,0.0,1.0); }`;
const mkMat = (frag, uniforms) => new THREE.ShaderMaterial({ uniforms, vertexShader: QUAD_VERT, fragmentShader: frag, depthTest: false, depthWrite: false });

const BLOOM_DOWN = `uniform sampler2D tMap, tGlow; uniform vec2 uPx; uniform float uThr, uGlow; varying vec2 vUv;
vec3 dec(vec3 c){ return c*(c*(c*0.305306011+0.682171111)+0.012522878); }
void main(){ vec3 s=vec3(0.0); for(int j=0;j<2;j++) for(int i=0;i<2;i++) s+=texture2D(tMap, vUv+(vec2(float(i),float(j))-0.5)*uPx*2.0).rgb; s*=0.25;
  float l=max(s.r,max(s.g,s.b)); s*=smoothstep(uThr, uThr+0.5, l); if(uGlow>0.5) s+=dec(texture2D(tGlow,vUv).rgb)*1.4; gl_FragColor=vec4(s,1.0); }`;
const BLUR = `uniform sampler2D tMap; uniform vec2 uDir; varying vec2 vUv;
void main(){ vec3 s=texture2D(tMap,vUv).rgb*0.2270; s+=(texture2D(tMap,vUv+uDir*1.3846).rgb+texture2D(tMap,vUv-uDir*1.3846).rgb)*0.3162; s+=(texture2D(tMap,vUv+uDir*3.2308).rgb+texture2D(tMap,vUv-uDir*3.2308).rgb)*0.0703; gl_FragColor=vec4(s,1.0); }`;
// Kuwahara at half resolution (each sample is a bilinear 2x2 average of the full-res frame)
const KUW = `uniform sampler2D tMap; uniform vec2 uPx; varying vec2 vUv;
void main(){ vec3 best=vec3(0.0); float bv=1e9;
  for(int s=0;s<4;s++){ vec2 off=vec2(s==1||s==3?-1.0:1.0, s>=2?-1.0:1.0); vec3 m=vec3(0.0), q=vec3(0.0); float n=0.0;
    for(int j=0;j<=KR;j++) for(int i=0;i<=KR;i++){ vec3 c=texture2D(tMap, vUv+vec2(float(i),float(j))*off*uPx).rgb; m+=c; q+=c*c; n+=1.0; }
    m/=n; q=q/n-m*m; float v=q.r+q.g+q.b; if(v<bv){ bv=v; best=m; } }
  gl_FragColor=vec4(best,1.0); }`;

const FINAL = `precision highp float;
uniform sampler2D tPaint, tBloomA, tBloomB, tDetail, tOverlay, tGlow; uniform float uHasGlow; uniform vec2 uRes; uniform float uTime, uFade, uHasOv, uBloom, uHal, uTone;
uniform vec3 uFlash; uniform int uNDL; uniform vec4 uDLP[${NL}]; uniform vec3 uDLC[${NL}]; uniform vec3 uAmb; uniform float uKr;
varying vec2 vUv;
float hash(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
float lum(vec3 c){ return dot(c, vec3(0.2126,0.7152,0.0722)); }
vec3 enc(vec3 c){ c=max(c,0.0); return mix(c*12.92, 1.055*pow(c,vec3(1.0/2.4))-0.055, step(0.0031308,c)); }
vec3 dec(vec3 c){ return c*(c*(c*0.305306011+0.682171111)+0.012522878); }
vec4 kuwD(vec2 uv){ vec2 px=1.0/uRes; vec4 best=vec4(0.0); float bv=1e9;
  for(int s=0;s<4;s++){ vec2 off=vec2(s==1||s==3?-1.0:1.0, s>=2?-1.0:1.0); vec4 m=vec4(0.0), q=vec4(0.0); float n=0.0;
    for(int j=0;j<=1;j++) for(int i=0;i<=1;i++){ vec4 c=texture2D(tDetail, uv+vec2(float(i),float(j))*off*px); m+=c; q+=c*c; n+=1.0; }
    m/=n; q=q/n-m*m; float v=q.r+q.g+q.b+q.a; if(v<bv){ bv=v; best=m; } }
  return best; }
void main(){
  vec3 lin=texture2D(tPaint, vUv).rgb;
  if(uHasGlow>0.5) lin+=dec(texture2D(tGlow, vUv).rgb);
  vec3 bl=texture2D(tBloomA, vUv).rgb*0.55 + texture2D(tBloomB, vUv).rgb*0.7;
  lin+=bl*uBloom;
  vec3 col=enc(lin);
  // detail layer (figures, banners, fine objects): fine Kuwahara, relit by the scene's lanterns, same grade as everything else
  vec2 px1=1.0/uRes; float near=texture2D(tDetail,vUv).a+texture2D(tDetail,vUv+px1*vec2(2.0,2.0)).a+texture2D(tDetail,vUv-px1*vec2(2.0,2.0)).a+texture2D(tDetail,vUv+px1*vec2(2.0,-2.0)).a+texture2D(tDetail,vUv+px1*vec2(-2.0,2.0)).a;
  if(near>0.001){ vec4 d=kuwD(vUv);
    if(d.a>0.002){ vec3 c=clamp(d.rgb/d.a,0.0,1.0); vec3 cl=dec(c); vec3 L=vec3(0.0); vec2 fp=vUv*vec2(${DW}.0,${DH}.0);
      for(int i=0;i<${NL};i++){ if(i>=uNDL) break; vec2 dd=fp-uDLP[i].xy; float r=uDLP[i].z; float f=1.0/(1.0+dot(dd,dd)/(r*r)); L+=uDLC[i]*f*f; }
      vec3 lit=mix(cl, vec3(lum(cl)), 0.65); cl=cl*uAmb + lit*L*1.25; c=enc(cl);
      col=mix(col, c, clamp(d.a,0.0,1.0)); } }
  // halation: warm bleed from the wide bloom, highlights only
  col+=texture2D(tBloomB, vUv).rgb*vec3(1.0,0.45,0.25)*uHal;
  // grade (the proto's single grade)
  col=(col-0.5)*1.04+0.5; float l=lum(col); col=mix(vec3(l), col, 1.1);
  col+=vec3(-0.008,0.0,0.035)*(1.0-smoothstep(0.0,0.6,l)) + vec3(0.05,0.022,-0.02)*smoothstep(0.4,1.0,l);
  vec2 cuv=(vUv-0.5)*1.2; float r2=dot(cuv,cuv); col*=1.0-0.35*smoothstep(0.25,1.6,r2*2.2);
  float g=hash(floor(vUv*uRes/1.5)+fract(uTime*61.7)*13.0)-0.5; col+=g*0.035*(1.0-0.5*clamp(l,0.0,1.0));
  // canvas weave
  vec2 p=vUv*uRes*(720.0/uRes.y); float th=hash(vec2(floor(p.y/2.0), 3.7))*0.6 + hash(vec2(floor(p.x/2.0), 9.1))*0.4; float fib=hash(floor(p/vec2(5.0,2.0)))*0.5;
  float w=(th*0.8+fib*0.4)-0.6; float m=lum(col); col*=1.0+w*0.03*(0.4+2.0*m*(1.0-m));
  col=mix(col, uFlash, 0.0); col*=uFade;
  if(uHasOv>0.5){ vec4 o=texture2D(tOverlay,vUv); col=mix(col,o.rgb,o.a); }
  gl_FragColor=vec4(col,1.0);
}`;

export class Post {
  constructor(renderer, scene, camera, W, H, { kr = 2 } = {}) {
    this.r = renderer; this.scene = scene; this.camera = camera; this.W = W; this.H = H;
    const rt = (w, h, type = THREE.HalfFloatType) => new THREE.WebGLRenderTarget(Math.max(2, Math.round(w)), Math.max(2, Math.round(h)), { type, depthBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBAFormat });
    this.rt0 = rt(W, H); this.rtP = rt(W / 2, H / 2);
    this.a1 = rt(W / 4, H / 4); this.a2 = rt(W / 4, H / 4); this.b1 = rt(W / 8, H / 8); this.b2 = rt(W / 8, H / 8);
    this.quad = new FullScreenQuad(null);
    this.mDown = mkMat(BLOOM_DOWN, { tMap: { value: null }, tGlow: { value: null }, uPx: { value: new THREE.Vector2() }, uThr: { value: 0.8 }, uGlow: { value: 0 } });
    this.mBlur = mkMat(BLUR, { tMap: { value: null }, uDir: { value: new THREE.Vector2() } });
    this.mKuw = mkMat(KUW.replace(/KR/g, String(kr)), { tMap: { value: null }, uPx: { value: new THREE.Vector2(1 / W, 1 / H) } });
    // detail + overlay canvases (CPU raster; uploaded each frame)
    const mkc = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; };
    this.detailCanvas = mkc(); this.dg = this.detailCanvas.getContext('2d', { willReadFrequently: true });
    this.overlayCanvas = mkc(); this.og = this.overlayCanvas.getContext('2d', { willReadFrequently: true });
    const ct = (c) => { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.premultiplyAlpha = true; t.generateMipmaps = false; t.minFilter = t.magFilter = THREE.LinearFilter; return t; };
    this.detailTex = ct(this.detailCanvas); this.overlayTex = ct(this.overlayCanvas); this.overlayTex.premultiplyAlpha = false;
    this.glowCanvas = document.createElement('canvas'); this.glowCanvas.width = Math.round(W / 2); this.glowCanvas.height = Math.round(H / 2); this.gg = this.glowCanvas.getContext('2d', { willReadFrequently: true });
    this.glowTex = ct(this.glowCanvas); this.glowTex.premultiplyAlpha = false; this.hasGlow = false;
    this.mFinal = mkMat(FINAL, { tPaint: { value: this.rtP.texture }, tBloomA: { value: this.a1.texture }, tBloomB: { value: this.b1.texture }, tDetail: { value: this.detailTex }, tOverlay: { value: this.overlayTex }, tGlow: { value: this.glowTex }, uHasGlow: { value: 0 },
      uRes: { value: new THREE.Vector2(W, H) }, uTime: { value: 0 }, uFade: { value: 1 }, uHasOv: { value: 0 }, uBloom: { value: 0.5 }, uHal: { value: 0.25 }, uTone: { value: 1 }, uFlash: { value: new THREE.Vector3() },
      uNDL: { value: 0 }, uDLP: { value: Array.from({ length: NL }, () => new THREE.Vector4()) }, uDLC: { value: Array.from({ length: NL }, () => new THREE.Vector3()) }, uAmb: { value: new THREE.Vector3(1, 1, 1) }, uKr: { value: 1 } });
    this.mFinal.defines = {};
    this.hasOverlay = false; this.sc = W / DW; this.overlayDirty = true;
  }
  pass(mat, target) { this.quad.material = mat; this.r.setRenderTarget(target); this.quad.render(this.r); }
  clearDetail() { const g = this.dg; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, this.W, this.H); g.setTransform(this.sc, 0, 0, this.sc, 0, 0); return g; }
  clearOverlay() { const g = this.og; g.setTransform(1, 0, 0, 1, 0, 0); if (this.overlayDirty) g.clearRect(0, 0, this.W, this.H); this.overlayDirty = false; this.hasOverlay = false; g.setTransform(this.sc, 0, 0, this.sc, 0, 0); return g; }
  // additive glow canvas (half res): fill black, then draw with 'lighter' (radial gradients). Call glowOn() once per frame before drawing.
  clearGlow() { const g = this.gg; g.setTransform(1, 0, 0, 1, 0, 0); this.hasGlow = false; g.globalCompositeOperation = 'source-over'; g.setTransform(this.sc / 2, 0, 0, this.sc / 2, 0, 0); return g; }
  glowOn() { if (!this.hasGlow) { const g = this.gg; g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-over'; g.fillStyle = '#000'; g.fillRect(0, 0, this.glowCanvas.width, this.glowCanvas.height); g.restore(); g.globalCompositeOperation = 'lighter'; this.hasGlow = true; } return this.gg; }
  markOverlay() { this.hasOverlay = true; this.overlayDirty = true; }
  render(t, { fade = 1, lights = [], amb = [1, 1, 1], bloom = 0.5, hal = 0.25 } = {}) {
    const r = this.r, W = this.W, H = this.H;
    if (this.hasGlow) this.glowTex.needsUpdate = true;   // upload this frame's glows before the bloom reads them (Kleidion read the previous frame's)
    r.setRenderTarget(this.rt0); r.setClearColor(0x05060f, 1); r.clear(); r.render(this.scene, this.camera);
    this.mDown.uniforms.tMap.value = this.rt0.texture; this.mDown.uniforms.tGlow.value = this.glowTex; this.mDown.uniforms.uGlow.value = this.hasGlow ? 1 : 0; this.mDown.uniforms.uPx.value.set(1 / W, 1 / H); this.pass(this.mDown, this.a1);
    this.mBlur.uniforms.tMap.value = this.a1.texture; this.mBlur.uniforms.uDir.value.set(1.6 / (W / 4), 0); this.pass(this.mBlur, this.a2);
    this.mBlur.uniforms.tMap.value = this.a2.texture; this.mBlur.uniforms.uDir.value.set(0, 1.6 / (H / 4)); this.pass(this.mBlur, this.a1);
    this.mDown.uniforms.tMap.value = this.a1.texture; this.mDown.uniforms.uPx.value.set(4 / W, 4 / H); this.mDown.uniforms.uThr.value = -1.0; this.mDown.uniforms.uGlow.value = 0; this.pass(this.mDown, this.b1); this.mDown.uniforms.uThr.value = 0.8;
    this.mBlur.uniforms.tMap.value = this.b1.texture; this.mBlur.uniforms.uDir.value.set(2.4 / (W / 8), 0); this.pass(this.mBlur, this.b2);
    this.mBlur.uniforms.tMap.value = this.b2.texture; this.mBlur.uniforms.uDir.value.set(0, 2.4 / (H / 8)); this.pass(this.mBlur, this.b1);
    this.mKuw.uniforms.tMap.value = this.rt0.texture; this.mKuw.uniforms.uPx.value.set(2 / W, 2 / H); this.pass(this.mKuw, this.rtP);
    const u = this.mFinal.uniforms; u.uTime.value = t; u.uFade.value = fade; u.uHasOv.value = this.hasOverlay ? 1 : 0; u.uHasGlow.value = this.hasGlow ? 1 : 0; if (this.hasGlow) this.glowTex.needsUpdate = true; u.uBloom.value = bloom; u.uHal.value = hal; u.uAmb.value.set(amb[0], amb[1], amb[2]);
    let n = 0; for (const l of lights) { if (n >= NL) break; if (!(l.k > 0.0005)) continue; u.uDLP.value[n].set(l.x, l.y, l.r, 0); u.uDLC.value[n].set(l.c[0] * l.k, l.c[1] * l.k, l.c[2] * l.k); n++; } u.uNDL.value = n;
    this.detailTex.needsUpdate = true; if (this.hasOverlay) this.overlayTex.needsUpdate = true;
    this.pass(this.mFinal, null);
  }
}
