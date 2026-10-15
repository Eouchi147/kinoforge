// P12 TERRAIN — materials: terrain (baked low-sun lighting + watercolour washes + engraved contours + hatching + tarn + symbols),
// ink ribbons (route: dashes, bleed, wet head, ink running dry; river), sky dome, and the procedural paper / noise textures.
import * as THREE from 'three';
import { rng } from './terrain.js';

// ------------------------------------------------------------------ shared GLSL
export const GLSL_COMMON = /* glsl */`
uniform sampler2D uNoise;
uniform sampler2D uPaper;
uniform sampler2D uMap;      // RGBA32F: height, sun term, sky term, lake rho  (0.5 unit texels)
uniform vec4 uMapOrg;        // origin.xy, 1/size.xy
uniform vec3 uFogCol;
uniform vec4 uFog;           // x density at y=0, y height falloff k, z edge fade start, w end
float hash11(float p){ p = fract(p*.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y)*p3.z); }
float vn(vec2 p){ vec2 i = floor(p); vec2 f = fract(p); f = f*f*(3.0 - 2.0*f); return texture2D(uNoise, (i + f + 0.5)/256.0).r; }
float vn2(vec2 p){ vec2 i = floor(p); vec2 f = fract(p); f = f*f*(3.0 - 2.0*f); return texture2D(uNoise, (i + f + 0.5)/256.0).g; }
float fbm3(vec2 p){ return (vn(p)*0.5 + vn2(p*2.03 + 7.1)*0.25 + vn(p*4.1 + 13.7)*0.125)/0.875; }
vec2 muv(vec2 xz){ return (xz - uMapOrg.xy)*uMapOrg.zw; }
vec3 lin(vec3 c){ return pow(c, vec3(2.2)); }
vec3 applyFogK(vec3 col, vec3 wp, float kf){
  vec3 ray = wp - cameraPosition; float D = max(length(ray), 0.001); float k = uFog.y; float dy = ray.y; float kd = k*dy/D; float opt;
  if (abs(kd) < 1e-4) opt = uFog.x*exp(-k*cameraPosition.y)*D; else opt = uFog.x*exp(-k*cameraPosition.y)*(1.0 - exp(-k*dy))/kd;
  float a = 1.0 - exp(-max(opt, 0.0));
  float edge = smoothstep(uFog.z, uFog.w, length(wp.xz - cameraPosition.xz));
  return mix(col, uFogCol, max(a*kf, edge));
}
vec3 applyFog(vec3 col, vec3 wp){ return applyFogK(col, wp, 1.0); }
`;

// ------------------------------------------------------------------ terrain
const TERRAIN_VERT = /* glsl */`
varying vec3 vWorld;
void main(){ vWorld = position; gl_Position = projectionMatrix*viewMatrix*vec4(position, 1.0); }
`;
const TERRAIN_FRAG = /* glsl */`
precision highp float;
${GLSL_COMMON}
uniform vec3 uSunCol, uSkyCol, uBounce, uInkCol, uRouteCol;
uniform vec4 uCamp;      // x, z, size, 0
uniform vec4 uMark;      // x, z, age seconds (<0 hidden), ring radius
uniform vec4 uLook;      // x contour weight, y hatch weight, z wash strength, w unused
varying vec3 vWorld;

float sdTri(vec2 p, vec2 q){ p.x = abs(p.x); vec2 a = p - q*clamp(dot(p,q)/dot(q,q), 0.0, 1.0); vec2 b = p - q*vec2(clamp(p.x/q.x, 0.0, 1.0), 1.0);
  float s = -sign(q.y); vec2 d = min(vec2(dot(a,a), s*(p.x*q.y - p.y*q.x)), vec2(dot(b,b), s*(p.y - q.y))); return -sqrt(d.x)*sign(d.y); }
// line family at integer values of c, anti-aliased in pixels; when the lines get denser than ~4 px they fade to their mean coverage (no moire)
float lineMask(float c, float halfPx){
  float fw = fwidth(c) + 1e-6; float d = abs(fract(c + 0.5) - 0.5)/fw;
  float m = 1.0 - smoothstep(halfPx - 0.6, halfPx + 0.6, d);
  float cov = clamp(2.0*halfPx*fw, 0.0, 0.62);
  return mix(m, cov, smoothstep(0.20, 0.50, fw));
}

void main(){
  vec2 xz = vWorld.xz; vec2 uv = muv(xz);
  vec4 M = texture2D(uMap, uv); float h = M.r, sunT = M.g, skyT = M.b, rho = M.a;
  vec2 e = uMapOrg.zw; // 1 world unit in uv
  float hx = texture2D(uMap, uv + vec2(e.x, 0.0)).r - texture2D(uMap, uv - vec2(e.x, 0.0)).r;
  float hz = texture2D(uMap, uv + vec2(0.0, e.y)).r - texture2D(uMap, uv - vec2(0.0, e.y)).r;
  float slope = 0.5*length(vec2(hx, hz));

  // ---- paper: warm cream, cloudy tone, fibres, foxing
  vec3 paper = lin(vec3(0.925, 0.868, 0.715));
  float pg1 = texture2D(uPaper, xz/160.0).r, pg2 = texture2D(uPaper, xz/41.0 + 0.37).r, pg3 = texture2D(uPaper, xz/13.0 + 0.71).r;
  float cloud = fbm3(xz*0.018);
  paper *= 0.92 + 0.15*cloud;
  paper *= 1.0 + (pg1 - 0.5)*0.20 + (pg2 - 0.5)*0.14 + (pg3 - 0.5)*0.07;
  float fox = smoothstep(0.60, 0.80, fbm3(xz*0.04 + 3.3))*0.20;
  paper = mix(paper, lin(vec3(0.66, 0.47, 0.26)), fox);

  // ---- hypsometric watercolour washes (wobbly thresholds so bands never look like clean steps)
  float hw = h + (fbm3(xz*0.03 + 9.0) - 0.45)*8.0;
  vec3 c0 = lin(vec3(0.52, 0.68, 0.38)), c1 = lin(vec3(0.72, 0.76, 0.40)), c2 = lin(vec3(0.86, 0.75, 0.44)), c3 = lin(vec3(0.84, 0.60, 0.33)), c4 = lin(vec3(0.68, 0.50, 0.36)), c5 = lin(vec3(0.64, 0.61, 0.61));
  vec3 w = c0;
  w = mix(w, c1, smoothstep( 7.0, 12.0, hw));
  w = mix(w, c2, smoothstep(18.0, 24.0, hw));
  w = mix(w, c3, smoothstep(31.0, 38.0, hw));
  w = mix(w, c4, smoothstep(46.0, 54.0, hw));
  w = mix(w, c5, smoothstep(62.0, 70.0, hw));
  float rock = smoothstep(0.70, 1.20, slope + (fbm3(xz*0.11 + 5.0) - 0.45)*0.5)*smoothstep(14.0, 34.0, hw);
  w = mix(w, lin(vec3(0.58, 0.46, 0.36)), rock*0.5);
  float snow = smoothstep(72.0, 84.0, hw)*(1.0 - smoothstep(0.95, 1.7, slope + (fbm3(xz*0.09 + 2.0) - 0.45)*0.4));
  float wd = 0.70 + 0.30*smoothstep(0.1, 0.9, fbm3(xz*0.05 + 21.0));          // wash density: pooled and thin patches
  float gran = (texture2D(uPaper, xz/9.0 + 0.2).r - 0.5)*0.22;               // pigment granulation
  vec3 alb = mix(paper, w, clamp((0.80*wd + gran)*uLook.z, 0.0, 1.0));
  alb = mix(alb, paper*1.05, snow*0.92);                                     // snow = bare paper

  // ---- light: baked low warm sun (with cast shadows) + cool sky fill + warm ground bounce
  vec3 light = uSunCol*sunT + uSkyCol*skyT + uBounce*(0.25 + 0.75*(1.0 - skyT));
  { float Ls = dot(light, vec3(0.3, 0.55, 0.15)) + 1e-4; float qs = Ls*7.0; float Lq = (floor(qs) + smoothstep(0.55, 0.95, fract(qs)))/7.0; light *= mix(1.0, Lq/Ls, uLook.w > 0.0 && uLook.w < 0.5 ? 0.0 : 0.62); }   // soft-stepped tone: a printed wash, not a smooth CG gradient
  vec3 col = alb*light;
  float lum = dot(light, vec3(0.3, 0.55, 0.15));
  float tone = clamp(lum*0.85, 0.0, 1.0);

  // ---- engraved contours: wobbly (hand-drawn), Tanaka-weighted (heavier in the shade), extra hatch contours only in deep shade
  float wob = (fbm3(xz*0.045 + 40.0) - 0.45)*2.2 + (vn(xz*0.55 + 3.0) - 0.5)*0.40;
  float hc = h + wob; float shade = 1.0 - clamp(sunT*1.15, 0.0, 1.0);
  float lm = lineMask(hc/3.0, mix(0.52, 1.0, shade))*mix(0.55, 0.92, shade);
  float li = lineMask(hc/15.0, mix(0.95, 1.45, shade))*0.95;
  float lh = lineMask(hc/0.75, 0.40)*smoothstep(0.70, 0.95, shade)*0.36;                // the engraver's tone: more contour lines where it is darker
  float lh2 = lineMask(hc/1.5, 0.44)*smoothstep(0.36, 0.72, shade)*0.40;
  // engraved relief shading: thin 45-degree world-space strokes whose weight follows the shade (cross-hatched only in the deepest shadow)
  float hAmt = smoothstep(0.46, 0.12, tone);
  float hv = smoothstep(0.62, 0.92, abs(normalize(cameraPosition - vWorld).y));   // the hatch only exists when the sheet is seen from above (it reads as a wire mesh at a low angle)
  float hs1 = lineMask(((xz.x + xz.y)*0.7071 + (vn(xz*0.30 + 17.0) - 0.5)*1.1)/1.15, mix(0.18, 0.78, hAmt))*smoothstep(0.10, 0.40, hAmt)*hv;
  float hs2 = 0.0;
  // vegetation stipple: engraved dots in the lowlands, clumped by a slow noise (fades to its mean coverage when the dots get finer than the pixels)
  float veg = smoothstep(24.0, 9.0, hw)*smoothstep(0.75, 0.30, slope)*(0.25 + 0.75*smoothstep(0.30, 0.65, fbm3(xz*0.05 + 50.0)));
  vec2 sg = xz/1.15; vec2 sid = floor(sg), sf = fract(sg); vec2 sc = 0.5 + (vec2(hash21(sid), hash21(sid + 17.3)) - 0.5)*0.72; float fwg = fwidth(sg.x) + fwidth(sg.y);
  float srad = 0.17 + 0.08*hash21(sid + 3.7); float dotm = (1.0 - smoothstep(srad - fwg, srad + fwg, length(sf - sc)))*step(hash21(sid + 5.1), veg);
  float stip = mix(dotm, veg*3.14159*srad*srad, smoothstep(0.25, 0.6, fwg));
  float inkv = 0.80 + 0.20*vn(xz*2.1 + 9.0);
  float lines = clamp(max(max(lm, li), max(lh, lh2))*inkv*uLook.x, 0.0, 1.0);
  float hatch = clamp(max(hs1, hs2)*inkv*uLook.y, 0.0, 1.0);
  float waterOff = smoothstep(0.98, 1.06, rho);               // 0 inside the tarn, 1 on land
  vec3 ink = uInkCol*(0.55 + 0.45*clamp(lum, 0.0, 1.0));
  col = mix(col, lin(vec3(0.12, 0.17, 0.08))*(0.6 + 0.4*clamp(lum, 0.0, 1.0)), stip*0.62*waterOff*(1.0 - lines));
  col = mix(col, ink, lines*0.92*waterOff);
  col = mix(col, ink, hatch*0.50*waterOff);

  // ---- the tarn: black ink wash, engraved ripple lines, dark shoreline, bleed onto the paper
  float aaR = fwidth(rho)*1.1 + 1e-4;
  float inWater = 1.0 - smoothstep(1.0 - aaR, 1.0 + aaR, rho);
  float bleed = (1.0 - smoothstep(1.0, 1.22 + 0.10*vn(xz*0.8), rho))*(1.0 - inWater);
  col = mix(col, col*lin(vec3(0.40, 0.47, 0.56)), bleed*0.55);
  vec3 water = lin(vec3(0.020, 0.032, 0.050));
  float rz = xz.y*1.35 + (vn(xz*vec2(0.12, 0.9)) - 0.5)*1.6; float rl = lineMask(rz, 0.55);
  float rim = smoothstep(0.62, 1.0, rho);
  float shoreLine = smoothstep(0.04, 0.0, abs(rho - 0.93 - 0.02*vn(xz*1.3)))*0.5 + smoothstep(0.03, 0.0, abs(rho - 0.84))*0.25;
  vec3 wcol = water + lin(vec3(0.20, 0.28, 0.34))*(rl*0.30*(0.4 + rim) + shoreLine*0.5);
  wcol += lin(vec3(0.5, 0.45, 0.35))*0.05*max(0.0, sunT);
  col = mix(col, wcol, inWater);
  col = mix(col, ink*0.7, smoothstep(0.05, 0.0, abs(rho - 1.0))*0.85);

  // ---- map symbols in the route's ink: Camp II tent + ring, last-known-point marker with ripples
  vec3 rc = uRouteCol*(0.62 + 0.38*clamp(lum, 0.0, 1.0));
  { vec2 p = (xz - uCamp.xy)/uCamp.z; p.y += 0.75; float d = sdTri(p, vec2(0.95, 1.5))*uCamp.z; float aa = fwidth(d) + 1e-4; float fillm = 1.0 - smoothstep(-aa, aa, d);
    float ring = smoothstep(aa*1.5, 0.0, abs(length(xz - uCamp.xy) - uCamp.z*2.6) - 0.18); col = mix(col, rc, max(fillm*0.95, ring*0.8)); }
  if (uMark.z >= 0.0) {
    float age = uMark.z; vec2 q = xz - uMark.xy; float r = length(q); float aa = fwidth(r) + 1e-4; float RR = uMark.w;
    float pop = 1.0 - exp(-age*14.0)*cos(age*30.0);                      // overshoot-settle appear
    float R0 = RR*pop; float lw = 0.30 + 0.03*RR;
    float ring0 = smoothstep(lw + aa, lw - aa*0.5, abs(r - R0)); float dot0 = 1.0 - smoothstep(0.17*RR*pop - aa, 0.17*RR*pop + aa, r);
    float inner = smoothstep(lw*0.7 + aa, lw*0.7 - aa*0.5, abs(r - R0*0.62))*0.55;
    float cyc = 1.35; float a1 = fract((age - 0.35)/cyc), a2 = fract((age - 0.35 - 0.45)/cyc);
    float on1 = step(0.35, age), on2 = step(0.8, age);
    float rp1 = smoothstep(lw*0.9 + aa, lw*0.9 - aa*0.5, abs(r - (RR + a1*RR*2.8)))*pow(1.0 - a1, 1.6)*on1;
    float rp2 = smoothstep(lw*0.9 + aa, lw*0.9 - aa*0.5, abs(r - (RR + a2*RR*2.8)))*pow(1.0 - a2, 1.6)*on2*0.7;
    float ma = clamp(max(max(ring0, dot0), max(inner, max(rp1, rp2))), 0.0, 1.0); col = mix(col, rc*0.95, ma); }

  if (uLook.w > 0.5) { // debug views: 1 height, 2 sun/sky bake, 3 contour phase, 4 albedo, 5 light, 6 lines+hatch
    vec3 dbg = vec3(0.0);
    if (uLook.w < 1.5) dbg = vec3(h/100.0); else if (uLook.w < 2.5) dbg = vec3(sunT, skyT, 0.0); else if (uLook.w < 3.5) dbg = vec3(fract(hc/4.0)); else if (uLook.w < 4.5) dbg = alb; else if (uLook.w < 5.5) dbg = light*0.5; else dbg = vec3(lines, hatch, 0.0);
    gl_FragColor = vec4(dbg, 1.0); return; }
  gl_FragColor = vec4(applyFogK(col, vWorld, 1.0 - 0.8*inWater), 1.0);   // black ink stays black (less haze on the tarn)
}
`;
export function makeTerrainMaterial(shared) {
  return new THREE.ShaderMaterial({ vertexShader: TERRAIN_VERT, fragmentShader: TERRAIN_FRAG, side: THREE.FrontSide,
    uniforms: { ...shared, uCamp: { value: new THREE.Vector4(0, 0, 1.7, 0) }, uMark: { value: new THREE.Vector4(0, 0, -1, 4.6) }, uLook: { value: new THREE.Vector4(1, 1, 1, 0) } } });
}

// ------------------------------------------------------------------ ink ribbons (route + river)
// vertices ride exactly on the rendered terrain mesh (same triangulation, uMesh = the mesh's vertex heights), then lift a hair above it
const RIBBON_VERT = /* glsl */`
precision highp float;
${GLSL_COMMON}
uniform sampler2D uMesh; uniform vec4 uMeshOrg;   // x0, z0, 1/step
attribute float aS; attribute float aSide; attribute vec2 aDir; attribute float aW;
uniform float uWExp, uD0, uLift;
varying float vS; varying float vSide; varying float vHalfW; varying vec3 vWorld;
float meshH(vec2 xz){
  ivec2 ts = textureSize(uMesh, 0); vec2 g = (xz - uMeshOrg.xy)*uMeshOrg.z; vec2 gi = clamp(floor(g), vec2(0.0), vec2(ts) - 2.0); vec2 f = clamp(g - gi, 0.0, 1.0); ivec2 i0 = ivec2(gi);
  float a = texelFetch(uMesh, i0, 0).r, b = texelFetch(uMesh, i0 + ivec2(1, 0), 0).r, c = texelFetch(uMesh, i0 + ivec2(0, 1), 0).r, d = texelFetch(uMesh, i0 + ivec2(1, 1), 0).r;
  return (f.x + f.y <= 1.0) ? a + (b - a)*f.x + (c - a)*f.y : d + (c - d)*(1.0 - f.x) + (b - d)*(1.0 - f.y);
}
void main(){
  vec3 p = position; float d = max(length(p - cameraPosition), 1.0);
  float hw = aW*pow(d/uD0, uWExp);
  vec2 sd = vec2(-aDir.y, aDir.x);
  vec2 xz = p.xz + sd*aSide*hw;
  vec3 wp = vec3(xz.x, meshH(xz) + uLift, xz.y);
  vS = aS; vSide = aSide; vHalfW = hw; vWorld = wp;
  gl_Position = projectionMatrix*viewMatrix*vec4(wp, 1.0);
}
`;
const ROUTE_FRAG = /* glsl */`
precision highp float;
${GLSL_COMMON}
uniform float uProgress, uLen;
uniform vec3 uCol, uWetCol, uBleedCol;
uniform vec2 uDash;
uniform float uDryLen;
varying float vS; varying float vSide; varying float vHalfW; varying vec3 vWorld;
void main(){
  float hw = vHalfW; float lat = vSide*hw;
  float pixLat = fwidth(lat), pixS = fwidth(vS);                          // derivatives before any discard
  float dry = smoothstep(uLen - uDryLen, uLen, vS);                       // the ink runs dry toward the last known point
  float period = uDash.x + uDash.y;
  float cell = floor(vS/period); float r1 = hash11(cell*1.7 + 3.1), r2 = hash11(cell*2.9 + 11.3), r3 = hash11(cell*5.3 + 17.9);
  float dlen = uDash.x*(0.84 + 0.30*r1)*(1.0 - 0.55*dry);
  float st = (period - dlen)*(0.15 + 0.7*r2);
  float sc = vS - cell*period;
  float en = min(st + dlen, uProgress - cell*period);
  if (en < st) discard;
  float mid = 0.5*(st + en), hl = 0.5*(en - st);
  float dd = length(vec2(max(abs(sc - mid) - hl, 0.0), lat));
  float rCore = hw*0.50*(0.88 + 0.24*r3)*(1.0 - 0.38*dry);
  float edgeN = (vn(vWorld.xz*3.3 + cell*1.3) - 0.5)*0.30*hw;
  float pix = (pixLat + pixS)*0.45 + 1e-4;
  float core = 1.0 - smoothstep(rCore - pix, rCore + pix, dd + edgeN);
  float halo = (1.0 - smoothstep(rCore*0.55, hw, dd))*0.42*(1.0 - 0.6*dry);   // ink bleed: wider, darker underline
  float wet = smoothstep(uProgress - 6.5, uProgress, vS);
  float grain = texture2D(uPaper, vWorld.xz/37.0 + 0.5).r;
  vec3 ink = mix(uCol, uWetCol, wet*0.85);
  vec4 M = texture2D(uMap, muv(vWorld.xz)); float lum = 0.62 + 0.38*clamp(M.g*0.85 + M.b*0.5, 0.0, 1.0);
  vec3 col = mix(uBleedCol, ink, core)*lum;
  float a = max(core*(0.97 - 0.30*dry - 0.10*grain), halo*0.85);
  if (a < 0.004) discard;
  gl_FragColor = vec4(applyFog(col, vWorld), a);
}
`;
const RIVER_FRAG = /* glsl */`
precision highp float;
${GLSL_COMMON}
varying float vS; varying float vSide; varying float vHalfW; varying vec3 vWorld;
void main(){
  float hw = vHalfW; float lat = abs(vSide)*hw; float pix = fwidth(lat)*0.8 + 1e-4;
  float wob = (vn(vec2(vS*0.9, 3.0)) - 0.5)*0.22*hw + (vn(vWorld.xz*2.6) - 0.5)*0.16*hw;
  float core = 1.0 - smoothstep(hw*0.62 - pix, hw*0.62 + pix, lat + wob);
  float halo = (1.0 - smoothstep(hw*0.2, hw, lat))*0.28;
  vec3 ink = lin(vec3(0.27, 0.37, 0.47));
  vec4 M = texture2D(uMap, muv(vWorld.xz)); float lum = 0.55 + 0.45*clamp(M.g*0.85 + M.b*0.5, 0.0, 1.0);
  float grain = texture2D(uPaper, vWorld.xz/37.0).r;
  float a = max(core*(0.92 - 0.12*grain), halo);
  if (a < 0.004) discard;
  gl_FragColor = vec4(applyFog(ink*lum, vWorld), a);
}
`;
export function makeRibbonGeometry(path, widthFn) {
  const n = path.n; const pos = new Float32Array(n * 2 * 3), aS = new Float32Array(n * 2), aSide = new Float32Array(n * 2), aDir = new Float32Array(n * 2 * 2), aW = new Float32Array(n * 2); const idx = new Uint32Array((n - 1) * 6);
  for (let i = 0; i < n; i++) {
    const i0 = Math.max(0, i - 1), i1 = Math.min(n - 1, i + 1); let dx = path.x[i1] - path.x[i0], dz = path.z[i1] - path.z[i0]; const l = Math.hypot(dx, dz) || 1; dx /= l; dz /= l;
    for (let k = 0; k < 2; k++) { const v = i * 2 + k; pos[v * 3] = path.x[i]; pos[v * 3 + 1] = path.y[i]; pos[v * 3 + 2] = path.z[i]; aS[v] = path.s[i]; aSide[v] = k ? 1 : -1; aDir[v * 2] = dx; aDir[v * 2 + 1] = dz; aW[v] = widthFn(path.s[i], i); }
    if (i < n - 1) { const a = i * 2, b = a + 1, c = a + 2, d = a + 3, o = i * 6; idx[o] = a; idx[o + 1] = b; idx[o + 2] = c; idx[o + 3] = b; idx[o + 4] = d; idx[o + 5] = c; }
  }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aS', new THREE.BufferAttribute(aS, 1)); g.setAttribute('aSide', new THREE.BufferAttribute(aSide, 1)); g.setAttribute('aDir', new THREE.BufferAttribute(aDir, 2)); g.setAttribute('aW', new THREE.BufferAttribute(aW, 1)); g.setIndex(new THREE.BufferAttribute(idx, 1));
  g.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 40, -40), 700); return g;
}
// route inks are authored in display space and pre-compensated so that after the sepia grade (saturation 0.55) the line lands near #7a1f1f
export const INK = { col: new THREE.Color().setRGB(Math.pow(0.66, 2.2), Math.pow(0.06, 2.2), Math.pow(0.06, 2.2)), wet: new THREE.Color().setRGB(Math.pow(0.30, 2.2), Math.pow(0.02, 2.2), Math.pow(0.02, 2.2)), bleed: new THREE.Color().setRGB(Math.pow(0.40, 2.2), Math.pow(0.05, 2.2), Math.pow(0.05, 2.2)) };
export function makeRouteMaterial(shared, L) {
  return new THREE.ShaderMaterial({ vertexShader: RIBBON_VERT, fragmentShader: ROUTE_FRAG, transparent: true, depthWrite: false, depthTest: true, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
    uniforms: { ...shared, uWExp: { value: 0.30 }, uD0: { value: 197 }, uLift: { value: 0.16 }, uProgress: { value: 0 }, uLen: { value: L }, uDryLen: { value: 12 }, uDash: { value: new THREE.Vector2(4.2, 1.9) },
      uCol: { value: INK.col.clone() }, uWetCol: { value: INK.wet.clone() }, uBleedCol: { value: INK.bleed.clone() } } });
}
export function makeRiverMaterial(shared) {
  return new THREE.ShaderMaterial({ vertexShader: RIBBON_VERT, fragmentShader: RIVER_FRAG, transparent: true, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
    uniforms: { ...shared, uWExp: { value: 0.35 }, uD0: { value: 197 }, uLift: { value: 0.1 } } });
}

// ------------------------------------------------------------------ sky
export function makeSky(shared) {
  const mat = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, depthTest: false, fog: false,
    uniforms: { uHorizon: { value: new THREE.Color() }, uZenith: { value: new THREE.Color() }, uSunDir: { value: new THREE.Vector3() }, uSunGlow: { value: new THREE.Color() }, uNoise: shared.uNoise },
    vertexShader: `varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix*viewMatrix*vec4(position + cameraPosition, 1.0); }`,
    fragmentShader: `precision highp float; uniform vec3 uHorizon, uZenith, uSunGlow, uSunDir; uniform sampler2D uNoise; varying vec3 vDir;
      void main(){ vec3 d = normalize(vDir); float hgt = clamp(d.y, 0.0, 1.0); float t = pow(smoothstep(0.0, 0.62, hgt), 0.75);
        vec3 col = mix(uHorizon, uZenith, t);
        float g = max(dot(d, normalize(uSunDir)), 0.0); col += uSunGlow*(pow(g, 5.0)*0.55 + pow(g, 48.0)*0.9);
        float az = atan(d.x, d.z); float band = texture2D(uNoise, vec2(az*1.2, hgt*9.0)/256.0*17.0).b; col *= 0.985 + 0.03*band;   // faint wash streaks
        gl_FragColor = vec4(col, 1.0); }` });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(1400, 40, 24), mat); mesh.renderOrder = -10; mesh.frustumCulled = false; return mesh;
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
export function paperTexture(size = 1024, seed = 2024) { // tileable paper: cloudy tone + grain + fibres + specks (values are a multiplier around 0.5)
  const c = document.createElement('canvas'); c.width = c.height = size; const g = c.getContext('2d'); const img = g.createImageData(size, size); const d = img.data;
  const pers = [5, 10, 20, 40, 80, 160, 320], amps = [0.30, 0.22, 0.17, 0.13, 0.09, 0.06, 0.04]; const N = pers.map((p, i) => periodicNoise(seed + i * 7, p)); const R = rng(seed + 99);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) { let v = 0, a = 0; for (let k = 0; k < pers.length; k++) { v += amps[k] * N[k](x / size * pers[k], y / size * pers[k]); a += amps[k]; } v = v / a; v = 0.5 + (v - 0.5) * 1.5 + (R() - 0.5) * 0.12; const o = (y * size + x) * 4; d[o] = d[o + 1] = d[o + 2] = Math.max(0, Math.min(255, v * 255)); d[o + 3] = 255; }
  g.putImageData(img, 0, 0);
  const wrap = (fn) => { for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) { g.save(); g.translate(dx * size, dy * size); fn(); g.restore(); } };
  for (let i = 0; i < 2600; i++) { const x = R() * size, y = R() * size, a = R() * Math.PI * 2, len = 6 + R() * 38, bend = (R() - 0.5) * len * 0.5; const light = R() < 0.5;
    g.strokeStyle = light ? `rgba(255,255,255,${0.10 + R() * 0.14})` : `rgba(0,0,0,${0.06 + R() * 0.10})`; g.lineWidth = 0.5 + R() * 0.8; g.lineCap = 'round';
    const near = x < 50 || y < 50 || x > size - 50 || y > size - 50; const draw = () => { g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * len * 0.5 - Math.sin(a) * bend, y + Math.sin(a) * len * 0.5 + Math.cos(a) * bend, x + Math.cos(a) * len, y + Math.sin(a) * len); g.stroke(); };
    if (near) wrap(draw); else draw(); }
  for (let i = 0; i < 700; i++) { const x = R() * size, y = R() * size, rr = 0.5 + R() * 1.3; g.fillStyle = `rgba(0,0,0,${0.10 + R() * 0.2})`; wrap(() => { g.beginPath(); g.arc(x, y, rr, 0, 6.2832); g.fill(); }); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 1; /* 8 costs ~0.4 s/frame at grazing angles in SwiftShader for a <0.2/255 difference */ t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; return t;
}
// the relief mesh, displaced by the same heights the shader reads; returns the vertex heights too (the ribbons ride this exact triangulation)
export function terrainGeometry(world, hAt, step = 1.25) {
  const { x0, x1, z0, z1 } = world; const gx = Math.round((x1 - x0) / step), gz = Math.round((z1 - z0) / step); const pos = new Float32Array((gx + 1) * (gz + 1) * 3); const idx = new Uint32Array(gx * gz * 6); const heights = new Float32Array((gx + 1) * (gz + 1));
  for (let j = 0; j <= gz; j++) for (let i = 0; i <= gx; i++) { const x = x0 + i * (x1 - x0) / gx, z = z0 + j * (z1 - z0) / gz; const k = j * (gx + 1) + i; const h = hAt(x, z); heights[k] = h; pos[k * 3] = x; pos[k * 3 + 1] = h; pos[k * 3 + 2] = z; }
  let q = 0; for (let j = 0; j < gz; j++) for (let i = 0; i < gx; i++) { const a = j * (gx + 1) + i, b = a + 1, c = a + gx + 1, d = c + 1; idx[q++] = a; idx[q++] = c; idx[q++] = b; idx[q++] = b; idx[q++] = c; idx[q++] = d; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setIndex(new THREE.BufferAttribute(idx, 1)); g.computeBoundingSphere();
  return { geometry: g, heights, gx, gz, step: (x1 - x0) / gx };
}
