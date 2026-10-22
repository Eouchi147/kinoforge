// Battle Map engine: the engraved sheet. The map's look (parchment, watercolour washes by height, engraved contours, hatching,
// trees, fields, water, roads) is baked ONCE into a big texture; every frame then only lights it (baked low sun, evening sun, sky,
// drifting cloud shadows) and hazes it. That keeps the per-frame cost low in SwiftShader.
import * as THREE from 'three';
import { rng } from './noise.js';

export const GLSL_NOISE = /* glsl */`
uniform sampler2D uNoise;
float hash11(float p){ p = fract(p*.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y)*p3.z); }
float vn(vec2 p){ vec2 i = floor(p); vec2 f = fract(p); f = f*f*(3.0 - 2.0*f); return texture2D(uNoise, (i + f + 0.5)/256.0).r; }
float vn2(vec2 p){ vec2 i = floor(p); vec2 f = fract(p); f = f*f*(3.0 - 2.0*f); return texture2D(uNoise, (i + f + 0.5)/256.0).g; }
`;

export const GLSL_FOG = /* glsl */`
vec3 bmFog(vec3 col, vec3 wp, vec4 uFog, vec3 uFogCol){
  vec3 ray = wp - cameraPosition; float D = max(length(ray), 0.001); float k = uFog.y; float dy = ray.y; float kd = k*dy/D; float opt;
  if (abs(kd) < 1e-4) opt = uFog.x*exp(-k*cameraPosition.y)*D; else opt = uFog.x*exp(-k*cameraPosition.y)*(1.0 - exp(-k*dy))/kd;
  float a = 1.0 - exp(-max(opt, 0.0)); float edge = smoothstep(uFog.z, uFog.w, length(wp.xz - cameraPosition.xz));
  return mix(col, uFogCol, max(a, edge));
}`;
const FULLSCREEN_VERT = /* glsl */`varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

// ------------------------------------------------------------------ the sheet bake
const SHEET_FRAG = /* glsl */`
precision highp float;
${GLSL_NOISE}
uniform sampler2D uMap, uFeat, uFid, uPaper;
uniform vec4 uMapOrg;   // origin.xy, 1/size.xy   (height / light map)
uniform vec4 uFeatOrg;  // origin.xy, 1/size.xy   (feature SDF map)
uniform vec4 uWorld;    // x0, z0, W, D
uniform vec4 uStyle;    // contour interval, px per unit, contour weight, hatch weight
uniform vec3 uPal[6]; uniform float uPalH[6]; uniform float uPalW;
uniform vec4 uTone;     // paper amount, wash amount, tree density, field amount
varying vec2 vUv;
vec3 mixc(vec3 a, vec3 b, float t){ return mix(a, b, clamp(t, 0.0, 1.0)); }
float lineMask(float c, float halfPx){            // anti-aliased line family at integer values of c; denser than ~4 px fades to mean coverage
  float fw = fwidth(c) + 1e-6; float d = abs(fract(c + 0.5) - 0.5)/fw;
  float m = 1.0 - smoothstep(halfPx - 0.6, halfPx + 0.6, d);
  float cov = clamp(2.0*halfPx*fw, 0.0, 0.62);
  return mix(m, cov, smoothstep(0.20, 0.50, fw));
}
vec2 muv(vec2 xz){ return (xz - uMapOrg.xy)*uMapOrg.zw; }
vec2 fuv(vec2 xz){ return (xz - uFeatOrg.xy)*uFeatOrg.zw; }
void main(){
  vec2 xz = uWorld.xy + vUv*uWorld.zw; float S = uStyle.y;
  vec4 M = texture2D(uMap, muv(xz)); float h = M.r, sunT = M.g, skyT = M.b;
  vec2 e = uMapOrg.zw*1.0;
  float hx = texture2D(uMap, muv(xz) + vec2(e.x, 0.0)).r - texture2D(uMap, muv(xz) - vec2(e.x, 0.0)).r;
  float hz = texture2D(uMap, muv(xz) + vec2(0.0, e.y)).r - texture2D(uMap, muv(xz) - vec2(0.0, e.y)).r;
  float slope = 0.5*length(vec2(hx, hz));
  vec4 Fe = texture2D(uFeat, fuv(xz));   // water, woods, farms, road  (SDF, positive inside)
  // ---- paper
  vec3 paper = vec3(0.945, 0.895, 0.760);
  float pg1 = texture2D(uPaper, xz/170.0).r, pg2 = texture2D(uPaper, xz/43.0 + 0.37).r, pg3 = texture2D(uPaper, xz/13.0 + 0.71).r;
  float cloudN = vn(xz*0.016);
  paper *= 0.94 + 0.12*cloudN; paper *= 1.0 + (pg1 - 0.5)*0.16 + (pg2 - 0.5)*0.12 + (pg3 - 0.5)*0.06;
  paper = mix(paper, vec3(0.74, 0.58, 0.36), smoothstep(0.66, 0.85, vn(xz*0.037 + 3.3))*0.14);
  // ---- hypsometric washes with wobbly thresholds
  float hw = h + (vn(xz*0.028 + 9.0) - 0.5)*5.0;
  vec3 w = uPal[0];
  for (int i = 1; i < 6; i++) w = mix(w, uPal[i], smoothstep(uPalH[i] - uPalW, uPalH[i] + uPalW, hw));
  { float g1 = smoothstep(0.40, 0.72, vn(xz*0.022 + 31.0)), g2 = smoothstep(0.50, 0.78, vn2(xz*0.035 + 11.0));   // pasture greens and sun-dried patches
    w = mix(w, w*vec3(0.80, 0.97, 0.70), g1*0.38*smoothstep(14.0, 4.0, hw)); w = mix(w, w*vec3(1.04, 0.92, 0.80), g2*0.45*smoothstep(14.0, 4.0, hw)); }
  float rock = smoothstep(0.55, 1.10, slope + (vn(xz*0.10 + 5.0) - 0.5)*0.4)*smoothstep(10.0, 28.0, hw);
  w = mix(w, vec3(0.62, 0.52, 0.42), rock*0.55);
  float wd = 0.78 + 0.22*smoothstep(0.1, 0.9, vn(xz*0.05 + 21.0));
  float gran = (texture2D(uPaper, xz/9.0 + 0.2).r - 0.5)*0.18;
  vec3 col = mix(paper, w, clamp((0.88*wd + gran)*uTone.y, 0.0, 1.0));
  float shade = 1.0 - clamp(sunT*1.0, 0.0, 1.0);
  float lum0 = clamp(sunT*0.8 + skyT*0.35, 0.0, 1.0);
  // ---- water (rivers, sea, lakes): wash, engraved ripples, inked shoreline, sandy bleed
  float wsd = Fe.r; float aaw = fwidth(wsd)*0.9 + 1e-3;
  float inW = smoothstep(-aaw, aaw, wsd);
  float sandy = (1.0 - smoothstep(0.0, 2.4 + 1.2*vn(xz*0.5), -wsd))*(1.0 - inW);
  col = mix(col, mix(col, vec3(0.93, 0.84, 0.62), 0.7), sandy*0.8);
  float deepK = smoothstep(0.0, 9.0, wsd);
  vec3 wcol = mix(vec3(0.56, 0.74, 0.76), vec3(0.20, 0.45, 0.66), deepK);
  wcol *= 0.94 + 0.10*vn(xz*0.30 + 7.0);
  float rip = lineMask(wsd*0.62 + (vn(xz*0.35) - 0.5)*0.6, 0.55*max(S/6.0, 0.6))*(1.0 - smoothstep(2.0, 26.0, wsd))*0.62;
  float wavN = vn(xz*vec2(0.55, 1.9) + 4.0); float wav = smoothstep(0.72, 0.80, wavN)*smoothstep(1.0, 8.0, wsd)*0.45;   // open-water dashes
  wcol = mix(wcol, vec3(0.08, 0.20, 0.36), max(rip, wav));
  col = mix(col, wcol, inW);
  float shoreL = 1.0 - smoothstep(0.10, 0.10 + 0.22, abs(wsd + 0.02*vn(xz*2.0)));
  col = mix(col, vec3(0.10, 0.12, 0.14), shoreL*0.88);
  // ---- roads: pale dusty track with thin edge lines
  float rsd = Fe.a; float aar = fwidth(rsd)*0.9 + 1e-3; float inR = smoothstep(-aar, aar, rsd)*(1.0 - inW);
  col = mix(col, vec3(0.90, 0.82, 0.62)*(0.96 + 0.06*vn(xz*0.8)), inR*0.9);
  col = mix(col, vec3(0.30, 0.22, 0.14), (1.0 - smoothstep(0.05, 0.05 + 0.18, abs(rsd)))*0.55*(1.0 - inW));
  // ---- fields: patchwork of tilled strips
  float fsd = Fe.b; float aaf = fwidth(fsd)*0.9 + 1e-3;
  float inF = smoothstep(-aaf, aaf, fsd)*(1.0 - inW)*(1.0 - inR);
  if (fsd > -1.0) {
    vec4 Fi = texture2D(uFid, fuv(xz)); float ty = floor(Fi.r + 0.5), ang = Fi.g*3.14159265, tn = Fi.b;
    vec3 fc = ty < 1.5 ? vec3(0.62, 0.70, 0.34) : ty < 2.5 ? vec3(0.90, 0.78, 0.40) : ty < 3.5 ? vec3(0.74, 0.60, 0.36) : ty < 4.5 ? vec3(0.50, 0.62, 0.34) : vec3(0.84, 0.72, 0.46);
    fc *= 0.90 + 0.18*tn;
    float sv = dot(xz, vec2(-sin(ang), cos(ang)))/(0.9 + 0.35*tn);
    float stripe = lineMask(sv, 0.55*max(S/6.0, 0.6));
    fc = mix(fc, fc*vec3(0.62, 0.58, 0.50), stripe*0.55);
    col = mix(col, fc, inF*uTone.w);
    col = mix(col, vec3(0.20, 0.16, 0.08), (1.0 - smoothstep(0.06, 0.06 + 0.20, abs(fsd)))*0.60*(1.0 - inW)*(1.0 - inR));
  }
  // ---- ground texture: engraved grass tufts scattered over open ground
  float tuft = 0.0;
  { float cs = 3.3; vec2 g = xz/cs; vec2 id = floor(g), f = fract(g); vec2 c = 0.5 + (vec2(hash21(id + 1.3), hash21(id + 7.7)) - 0.5)*0.55;
    float dens = (0.35 + 0.65*smoothstep(0.25, 0.7, vn(xz*0.03 + 70.0)))*(1.0 - smoothstep(0.5, 1.1, slope))*(1.0 - inW)*(1.0 - inR)*(1.0 - inF)*(1.0 - smoothstep(-1.0, 1.5, Fe.g));
    float keep = step(hash21(id + 4.1), dens*0.62); vec2 p = (f - c)*cs;   // local, in units
    vec2 pa = p; float sg = 1e3;
    for (int k = 0; k < 3; k++) { float fk = float(k) - 1.0; vec2 tip = vec2(fk*0.30, -0.52 + 0.10*abs(fk)); vec2 b = vec2(fk*0.06, 0.12); vec2 ba = tip - b; float hh = clamp(dot(pa - b, ba)/dot(ba, ba), 0.0, 1.0); sg = min(sg, length(pa - b - ba*hh)); }
    float aa = (fwidth(xz.x) + fwidth(xz.y))*0.6 + 1e-4; tuft = (1.0 - smoothstep(0.075 - aa*0.5, 0.075 + aa, sg))*keep; }
  // ---- engraved contours (wobbly, weighted heavier in the shade), tone lines in deep shadow
  float wob = (vn(xz*0.045 + 40.0) - 0.5)*0.55 + (vn(xz*0.55 + 3.0) - 0.5)*0.16;
  float hc = h + wob; float iv = uStyle.x;
  float lm = lineMask(hc/iv, mix(0.50, 0.95, shade)*max(S/6.0, 0.6))*mix(0.40, 0.88, shade);
  float li = lineMask(hc/(iv*5.0), mix(0.85, 1.35, shade)*max(S/6.0, 0.6))*0.80;
  float lh = lineMask(hc/(iv*0.25), 0.40*max(S/6.0, 0.6))*smoothstep(0.72, 0.95, shade)*0.34;
  float lines = clamp(max(max(lm, li), lh)*(0.82 + 0.18*vn(xz*2.1 + 9.0))*uStyle.z, 0.0, 1.0)*(1.0 - inW)*(1.0 - 0.55*inF);
  // engraver's 45-degree hatch on the shaded faces
  float hAmt = smoothstep(0.46, 0.14, lum0);
  float hs1 = lineMask(((xz.x + xz.y)*0.7071 + (vn(xz*0.30 + 17.0) - 0.5)*1.0)/1.10, mix(0.16, 0.70, hAmt)*max(S/6.0, 0.6))*smoothstep(0.10, 0.40, hAmt);
  float hatch = clamp(hs1*uStyle.w, 0.0, 1.0)*(1.0 - inW);
  vec3 ink = vec3(0.20, 0.13, 0.08);
  // ---- trees (hex-offset lattice of stamped trees inside the woods)
  float wsdw = Fe.g; float treeAlpha = 0.0; vec3 treeCol = vec3(0.0); float treeShadow = 0.0;
  if (wsdw > -3.5) {
    float cs = 2.9; vec2 g = xz/cs; g.x += 0.5*mod(floor(g.y), 2.0); vec2 id = floor(g), f = fract(g);
    vec2 jit = (vec2(hash21(id), hash21(id + 9.1)) - 0.5)*0.26; vec2 c = 0.5 + jit; float rr = 0.36 + 0.09*hash21(id + 3.3);
    vec2 cw = ((id + c) - vec2(0.5*mod(id.y, 2.0), 0.0))*cs;       // world position of the tree centre
    float inside = texture2D(uFeat, fuv(cw)).g; float keep = step(hash21(id + 5.7), uTone.z)*smoothstep(0.25, 1.4, inside);
    float dd = length(f - c); float aa = (fwidth(xz.x) + fwidth(xz.y))*0.6/cs + 1e-4;
    float disc = (1.0 - smoothstep(rr - aa, rr + aa, dd))*keep;
    float rim = (1.0 - smoothstep(0.035, 0.035 + aa*1.5, abs(dd - rr)))*keep;
    vec2 dir = (f - c)/max(dd, 1e-3); float lit = dot(dir, normalize(vec2(-0.7, -0.55)))*0.5 + 0.5;
    vec3 leaf = mix(vec3(0.27, 0.42, 0.20), vec3(0.58, 0.72, 0.30), smoothstep(0.25, 0.95, lit)*(1.0 - dd/rr*0.35));
    leaf *= 0.9 + 0.2*hash21(id + 1.9);
    float sd2 = length((f - c) - vec2(0.12, 0.10)*1.0); float sh = (1.0 - smoothstep(rr*0.9 - aa, rr*1.1 + aa, sd2))*keep*(1.0 - disc);
    treeShadow = sh; treeAlpha = max(disc, rim*0.95); treeCol = mix(leaf, ink, rim);
    float wedge = smoothstep(-1.0, 0.8, wsdw);
    treeAlpha *= wedge; treeShadow *= wedge;
  }
  col = mix(col, col*vec3(0.55, 0.52, 0.42), treeShadow*0.55*(1.0 - inW));
  col = mix(col, treeCol, treeAlpha*(1.0 - inW));
  col = mix(col, vec3(0.30, 0.28, 0.10), tuft*0.55*(1.0 - treeAlpha));
  col = mix(col, ink, lines*0.80*(1.0 - 0.7*treeAlpha));
  col = mix(col, ink, hatch*0.42*(1.0 - treeAlpha));
  gl_FragColor = vec4(clamp(col, 0.0, 1.0), inW);
}
`;

export function sheetUniforms(world, tex, style) {
  const { map, F, FID, x0, z0, W, D, res, nx, nz } = world;
  const mapTex = new THREE.DataTexture(map.data, map.nx, map.nz, THREE.RGBAFormat, THREE.FloatType);
  mapTex.minFilter = mapTex.magFilter = THREE.LinearFilter; mapTex.wrapS = mapTex.wrapT = THREE.ClampToEdgeWrapping; mapTex.generateMipmaps = false; mapTex.needsUpdate = true;
  const featTex = new THREE.DataTexture(F, nx, nz, THREE.RGBAFormat, THREE.FloatType); featTex.minFilter = featTex.magFilter = THREE.LinearFilter; featTex.wrapS = featTex.wrapT = THREE.ClampToEdgeWrapping; featTex.generateMipmaps = false; featTex.needsUpdate = true;
  const fidTex = new THREE.DataTexture(FID, nx, nz, THREE.RGBAFormat, THREE.FloatType); fidTex.minFilter = fidTex.magFilter = THREE.NearestFilter; fidTex.wrapS = fidTex.wrapT = THREE.ClampToEdgeWrapping; fidTex.generateMipmaps = false; fidTex.needsUpdate = true;
  return { mapTex, featTex, fidTex,
    mapOrg: new THREE.Vector4(x0 - 0.5 * map.res, z0 - 0.5 * map.res, 1 / (map.res * map.nx), 1 / (map.res * map.nz)),
    featOrg: new THREE.Vector4(x0 - 0.5 * res, z0 - 0.5 * res, 1 / (res * nx), 1 / (res * nz)) };
}

export const DEFAULT_PALETTE = [ // [height, display-space colour]
  [-4, [0.72, 0.74, 0.50]], [1, [0.85, 0.79, 0.54]], [5, [0.88, 0.76, 0.50]], [11, [0.82, 0.64, 0.42]], [22, [0.72, 0.56, 0.42]], [40, [0.66, 0.60, 0.55]],
];

export function bakeSheet(renderer, world, shared, style = {}) {
  const U = sheetUniforms(world, null, style);
  const ppu = style.pxPerUnit ?? 7; const maxTex = Math.min(style.maxTex ?? 4096, renderer.capabilities.maxTextureSize);
  let BW = Math.round(world.W * ppu), BH = Math.round(world.D * ppu); const k = Math.min(1, maxTex / BW, maxTex / BH); BW = Math.round(BW * k); BH = Math.round(BH * k);
  const S = BW / world.W; const pal = style.palette || DEFAULT_PALETTE;
  const pad = (a, n) => { const r = a.slice(); while (r.length < n) r.push(r[r.length - 1]); return r.slice(0, n); };
  const P = pad(pal, 6);
  const mat = new THREE.ShaderMaterial({ vertexShader: FULLSCREEN_VERT, fragmentShader: SHEET_FRAG, depthTest: false, depthWrite: false, glslVersion: null,
    uniforms: { uNoise: shared.uNoise, uPaper: shared.uPaper, uMap: { value: U.mapTex }, uFeat: { value: U.featTex }, uFid: { value: U.fidTex }, uMapOrg: { value: U.mapOrg }, uFeatOrg: { value: U.featOrg },
      uWorld: { value: new THREE.Vector4(world.x0, world.z0, world.W, world.D) }, uStyle: { value: new THREE.Vector4(style.contour ?? 1.5, S, style.contourWeight ?? 1.0, style.hatchWeight ?? 1.0) },
      uPal: { value: P.map((p) => new THREE.Vector3(...p[1])) }, uPalH: { value: P.map((p) => p[0]) }, uPalW: { value: style.paletteSoft ?? 4.0 },
      uTone: { value: new THREE.Vector4(1, style.wash ?? 1.0, style.trees ?? 0.9, style.fields ?? 1.0) } } });
  const rt = new THREE.WebGLRenderTarget(BW, BH, { type: THREE.UnsignedByteType, format: THREE.RGBAFormat, minFilter: THREE.LinearMipmapLinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: true, depthBuffer: false, anisotropy: 4 });
  rt.texture.colorSpace = THREE.NoColorSpace;
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat); quad.frustumCulled = false; const sc = new THREE.Scene(); sc.add(quad); const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const prev = renderer.getRenderTarget(); const tm = renderer.toneMapping; renderer.toneMapping = THREE.NoToneMapping;
  renderer.setRenderTarget(rt); renderer.render(sc, cam); renderer.setRenderTarget(prev); renderer.toneMapping = tm;
  mat.dispose(); quad.geometry.dispose();
  return { sheet: rt.texture, rt, U, size: [BW, BH] };
}

// ------------------------------------------------------------------ the live terrain: sheet x light x haze
const TERRAIN_VERT = /* glsl */`varying vec3 vWorld; void main(){ vWorld = position; gl_Position = projectionMatrix*viewMatrix*vec4(position, 1.0); }`;
const TERRAIN_FRAG = /* glsl */`
precision highp float;
${GLSL_NOISE}
${GLSL_FOG}
uniform sampler2D uSheet, uMap;
uniform vec4 uMapOrg;
uniform vec4 uWorld;       // x0, z0, W, D
uniform vec3 uSunCol, uSkyCol, uBounce, uSunColB, uFogCol;
uniform vec4 uFog;         // density at y=0, height falloff, edge start, edge end (distance from camera on the ground)
uniform vec4 uAtm;         // eve (0..1), cloud strength, cloud time, glint
uniform vec4 uGrade;       // tone steps strength, world-edge fade width, spotlight, unused
varying vec3 vWorld;
vec3 lin(vec3 c){ return pow(c, vec3(2.2)); }
void main(){
  vec2 xz = vWorld.xz; vec2 uv = (xz - uWorld.xy)/uWorld.zw; vec4 S = texture2D(uSheet, uv); vec2 muv = (xz - uMapOrg.xy)*uMapOrg.zw; vec4 M = texture2D(uMap, muv);
  float eve = uAtm.x; float sunT = mix(M.g, M.a, eve); float skyT = M.b;
  float cl = vn(xz*0.0085 + vec2(uAtm.z*0.9, uAtm.z*0.35)); cl += 0.5*vn2(xz*0.021 + vec2(-uAtm.z*0.6, 3.7)); cl /= 1.5; float cloud = 1.0 - uAtm.y*smoothstep(0.50, 0.72, cl);
  vec3 sunCol = mix(uSunCol, uSunColB, eve);
  vec3 light = sunCol*sunT*cloud + uSkyCol*skyT + uBounce*(0.25 + 0.75*(1.0 - skyT));
  { float Ls = dot(light, vec3(0.3, 0.55, 0.15)) + 1e-4; float qs = Ls*5.0; float Lq = (floor(qs) + smoothstep(0.55, 0.95, fract(qs)))/5.0; light *= mix(1.0, Lq/Ls, uGrade.x); }
  vec3 col = lin(S.rgb)*light;
  float water = S.a;
  if (water > 0.5) { float g = vn(xz*vec2(2.4, 5.5) + vec2(uAtm.z*1.7, uAtm.z*0.6)); float sp = smoothstep(0.80, 0.97, g)*uAtm.w*clamp(sunT*1.4 + 0.2, 0.0, 1.0); col += vec3(1.0, 0.82, 0.5)*sp*0.55; }
  // haze: height fog + distance edge + the world's own edge (so a low camera never sees past the sheet)
  vec3 fogged = bmFog(col, vWorld, uFog, uFogCol); float a = 0.0;
  float ex = min(min(xz.x - uWorld.x, uWorld.x + uWorld.z - xz.x), min(xz.y - uWorld.y, uWorld.y + uWorld.w - xz.y)); float wedge = 1.0 - smoothstep(0.0, uGrade.y, ex);
  col = mix(fogged, uFogCol, wedge);
  gl_FragColor = vec4(col, 1.0);
}
`;
export function makeTerrainMaterial(shared, world, sheet, uMapTex, uMapOrg) {
  return new THREE.ShaderMaterial({ vertexShader: TERRAIN_VERT, fragmentShader: TERRAIN_FRAG, side: THREE.FrontSide,
    uniforms: { uNoise: shared.uNoise, uSheet: { value: sheet }, uMap: { value: uMapTex }, uMapOrg: { value: uMapOrg }, uWorld: { value: new THREE.Vector4(world.x0, world.z0, world.W, world.D) },
      uSunCol: { value: new THREE.Color(1.4, 1.05, 0.7) }, uSunColB: { value: new THREE.Color(1.5, 0.7, 0.35) }, uSkyCol: { value: new THREE.Color(0.2, 0.25, 0.36) }, uBounce: { value: new THREE.Color(0.15, 0.1, 0.06) }, uFogCol: { value: new THREE.Color(0.86, 0.76, 0.62) },
      uFog: { value: new THREE.Vector4(0.002, 0.03, 520, 820) }, uAtm: { value: new THREE.Vector4(0, 0.25, 0, 1) }, uGrade: { value: new THREE.Vector4(0.45, 60, 0, 0) } } });
}

// ------------------------------------------------------------------ sky dome
export function makeSky(shared) {
  const mat = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, depthTest: false, fog: false,
    uniforms: { uHorizon: { value: new THREE.Color() }, uZenith: { value: new THREE.Color() }, uSunDir: { value: new THREE.Vector3() }, uSunGlow: { value: new THREE.Color() }, uNoise: shared.uNoise },
    vertexShader: `varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix*viewMatrix*vec4(position + cameraPosition, 1.0); }`,
    fragmentShader: `precision highp float; uniform vec3 uHorizon, uZenith, uSunGlow, uSunDir; uniform sampler2D uNoise; varying vec3 vDir;
      void main(){ vec3 d = normalize(vDir); float hgt = clamp(d.y, 0.0, 1.0); float t = pow(smoothstep(0.0, 0.55, hgt), 0.7);
        vec3 col = mix(uHorizon, uZenith, t);
        float g = max(dot(d, normalize(uSunDir)), 0.0); col += uSunGlow*(pow(g, 4.0)*0.55 + pow(g, 40.0)*1.0 + pow(g, 900.0)*2.5);
        float az = atan(d.x, d.z); float band = texture2D(uNoise, vec2(az*1.4, hgt*11.0)/256.0*17.0).b; float band2 = texture2D(uNoise, vec2(az*3.1 + 5.0, hgt*40.0)/256.0*9.0).g;
        col *= 0.97 + 0.06*band; col = mix(col, col*vec3(1.08, 1.02, 0.92), smoothstep(0.45, 0.8, band2)*smoothstep(0.12, 0.3, hgt)*0.7*(1.0 - smoothstep(0.35, 0.6, hgt)));
        gl_FragColor = vec4(col, 1.0); }` });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(3000, 40, 24), mat); mesh.renderOrder = -10; mesh.frustumCulled = false; return mesh;
}

// ------------------------------------------------------------------ textures
export function noiseTexture(seed = 11) {
  const r = rng(seed); const n = 256; const d = new Uint8Array(n * n * 4); for (let i = 0; i < d.length; i++) d[i] = Math.floor(r() * 256);
  const t = new THREE.DataTexture(d, n, n, THREE.RGBAFormat, THREE.UnsignedByteType); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.magFilter = t.minFilter = THREE.LinearFilter; t.generateMipmaps = false; t.needsUpdate = true; return t;
}
function periodicNoise(seed, per) {
  const r = rng(seed); const g = new Float32Array(per * per); for (let i = 0; i < g.length; i++) g[i] = r();
  return (x, y) => { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi; const x0 = ((xi % per) + per) % per, y0 = ((yi % per) + per) % per, x1 = (x0 + 1) % per, y1 = (y0 + 1) % per; const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    const a = g[y0 * per + x0], b = g[y0 * per + x1], c = g[y1 * per + x0], d = g[y1 * per + x1]; return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v; };
}
export function paperTexture(size = 1024, seed = 2024) { // tileable paper: cloudy tone + grain + fibres + specks (a multiplier around 0.5)
  const c = document.createElement('canvas'); c.width = c.height = size; const g = c.getContext('2d'); const img = g.createImageData(size, size); const d = img.data;
  const pers = [5, 10, 20, 40, 80, 160, 320], amps = [0.30, 0.22, 0.17, 0.13, 0.09, 0.06, 0.04]; const N = pers.map((p, i) => periodicNoise(seed + i * 7, p)); const R = rng(seed + 99);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) { let v = 0, a = 0; for (let k = 0; k < pers.length; k++) { v += amps[k] * N[k](x / size * pers[k], y / size * pers[k]); a += amps[k]; } v = v / a; v = 0.5 + (v - 0.5) * 1.5 + (R() - 0.5) * 0.12; const o = (y * size + x) * 4; d[o] = d[o + 1] = d[o + 2] = Math.max(0, Math.min(255, v * 255)); d[o + 3] = 255; }
  g.putImageData(img, 0, 0);
  const wrap = (fn) => { for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) { g.save(); g.translate(dx * size, dy * size); fn(); g.restore(); } };
  for (let i = 0; i < 2000; i++) { const x = R() * size, y = R() * size, a = R() * Math.PI * 2, len = 6 + R() * 38, bend = (R() - 0.5) * len * 0.5; const light = R() < 0.5;
    g.strokeStyle = light ? `rgba(255,255,255,${0.10 + R() * 0.14})` : `rgba(0,0,0,${0.06 + R() * 0.10})`; g.lineWidth = 0.5 + R() * 0.8; g.lineCap = 'round';
    const near = x < 50 || y < 50 || x > size - 50 || y > size - 50; const draw = () => { g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * len * 0.5 - Math.sin(a) * bend, y + Math.sin(a) * len * 0.5 + Math.cos(a) * bend, x + Math.cos(a) * len, y + Math.sin(a) * len); g.stroke(); };
    if (near) wrap(draw); else draw(); }
  for (let i = 0; i < 500; i++) { const x = R() * size, y = R() * size, rr = 0.5 + R() * 1.3; g.fillStyle = `rgba(0,0,0,${0.10 + R() * 0.2})`; wrap(() => { g.beginPath(); g.arc(x, y, rr, 0, 6.2832); g.fill(); }); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 1; t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; return t;
}
// the relief mesh (CPU heights, one draw call)
export function terrainGeometry(world, step = 2.0) {
  const { x0, x1, z0, z1, hAt } = world; const gx = Math.round((x1 - x0) / step), gz = Math.round((z1 - z0) / step); const pos = new Float32Array((gx + 1) * (gz + 1) * 3); const idx = new Uint32Array(gx * gz * 6);
  for (let j = 0; j <= gz; j++) for (let i = 0; i <= gx; i++) { const x = x0 + i * (x1 - x0) / gx, z = z0 + j * (z1 - z0) / gz; const k = j * (gx + 1) + i; pos[k * 3] = x; pos[k * 3 + 1] = hAt(x, z); pos[k * 3 + 2] = z; }
  let q = 0; for (let j = 0; j < gz; j++) for (let i = 0; i < gx; i++) { const a = j * (gx + 1) + i, b = a + 1, c = a + gx + 1, d = c + 1; idx[q++] = a; idx[q++] = c; idx[q++] = b; idx[q++] = b; idx[q++] = c; idx[q++] = d; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setIndex(new THREE.BufferAttribute(idx, 1)); g.computeBoundingSphere();
  const sx = (x1 - x0) / gx, sz = (z1 - z0) / gz; const Y = (i, j) => pos[(j * (gx + 1) + i) * 3 + 1];
  const mh = (x, z) => { const fx = Math.min(gx - 1e-6, Math.max(0, (x - x0) / sx)), fz = Math.min(gz - 1e-6, Math.max(0, (z - z0) / sz)); const i = Math.floor(fx), j = Math.floor(fz), tx = fx - i, tz = fz - j;
    const a = Y(i, j), b = Y(i + 1, j), c = Y(i, j + 1), d = Y(i + 1, j + 1); return tx + tz <= 1 ? a + (b - a) * tx + (c - a) * tz : d + (c - d) * (1 - tx) + (b - d) * (1 - tz); };  // exactly the rendered triangles
  return { geometry: g, mh };
}
