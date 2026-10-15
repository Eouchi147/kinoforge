// P06 "CEL" — cel-shaded storm, anime lane. 10 s / 240 frames / 4 shots.
// S1 WS  the dead lighthouse in the storm, lightning (locked-off, low)
// S2 MS  she looks up, coils, launches up the spiral stair (crane + pan follow)
// S3 CU  hands on the lever: wind-up, push, CLUNK, silence, the lamp ignites, warm light from below
// S4 WS  from the sea: the beam sweeps over the lens, hold on the lit tower
// Look: MeshToonMaterial + toonGradient(4) on everything, inverted-hull ink (constant pixel width, BackSide basic black),
// cool rim from behind, hue-shifted shadows (violet ambient + grade shadowTint). Character on 2s (ease.hold2s),
// rain on 1s, lightning 2 frames. Deterministic: seeded rng, everything a function of the frame index.
import * as THREE from 'three';
import { boot, CameraRig, makeComposer, lightShaft, ease, rng, smoothstep, clamp, lerp, noise1, toonGradient } from '/harness/kit/film.js';
import { mergeVertices, mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const FPS = 24;
const SHOTS = [
  { name: 'S1 WS dark tower in the storm', dur: 3.0 },
  { name: 'S2 MS the climb', dur: 2.8 },
  { name: 'S3 CU lever, ignition', dur: 2.2 },
  { name: 'S4 WS the beam', dur: 2.0 },
];
const FB = [0, 72, 140, 192, 240];                       // shot boundaries (frames)
const EV = { flash1: 21, flash2: 55, crash1: 30, crash2: 58, clunk: 154, ignite: 168, pass: 206 };
const shotOf = (f) => (f < FB[1] ? 0 : f < FB[2] ? 1 : f < FB[3] ? 2 : 3);
const V3 = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
const YUP = V3(0, 1, 0);
const DEG = Math.PI / 180;
const DEBUG = new URLSearchParams(location.search).get('debug') === '1';

// ------------------------------------------------------------------ world layout
const TW = { y0: 2.2, h: 16.6, rBot: 2.6, rTop: 1.95 };     // tower body y 2.2 → 18.8
const GAL_Y = TW.y0 + TW.h;                                  // gallery / lantern floor
const LAMP_C = V3(0, GAL_Y + 0.95, 0);                       // burner centre
const R_IN = 1.6;                                            // interior wall radius
const C1 = V3(20.5 * Math.cos(255 * DEG), 1.7, 20.5 * Math.sin(255 * DEG));   // S1 camera (waterline, away from the moon)
// the moon sits just above-left of the lantern as seen from C1, so the dead lamp room is silhouetted against its halo
const _ml = V3(0, GAL_Y + 2.9, 0).sub(C1).normalize();
const MOON_AZ = Math.atan2(_ml.z, _ml.x) - 9.0 * DEG, MOON_EL = Math.asin(_ml.y) + 4.5 * DEG;
const MOON_DIR = V3(Math.cos(MOON_EL) * Math.cos(MOON_AZ), Math.sin(MOON_EL), Math.cos(MOON_EL) * Math.sin(MOON_AZ));
const ST = { r0: 0.55, r1: 1.63, rise: 0.18, dth: 0.24, y0: 6.0, thick: 0.06, kMin: -16, kMax: 34 };
ST.th0 = MOON_AZ + Math.PI - 0.95;                           // her S2 path sits opposite the moon window
const WALK_R = 1.08;
const LV = { z: 0.42, len: 0.78 };                         // ignition lever: floor pivot between her and the lamp
const stepTh = (k) => ST.th0 + k * ST.dth, stepY = (k) => ST.y0 + k * ST.rise;
const WINDOWS = [-12.5, -8, -3.5, 1, 5.5, 10, 14.5, 19, 23.5, 28].map((k) => ({ th: stepTh(k), y: stepY(k) + 1.3, w: 0.32, h: 0.95 }));
const MOONWIN = { th: MOON_AZ, y: ST.y0 + 2.2, w: 0.32, h: 0.95 };   // the slit the S2 key comes through
WINDOWS.push(MOONWIN);

// ------------------------------------------------------------------ palette (sRGB hex). Toon entries are [lit albedo, designed shadow].
const PAL = {
  skyTop: 0x070a22, skyHor: 0x26305e, moonHalo: 0x6f80c4, flash: 0xd8e4ff, moonDisc: 0xe2e8ff,
  cloud: [0x8a93c4, 0x1b1f45], cloudLine: 0x0b0d22,
  hemiSky: 0xe6e4ff, hemiGnd: 0x7a8298, moon: 0xc4d0ff, fog: 0x161c3c,
  tower: [0xf0f1fb, 0x7679b8], plinth: [0xa3a5bd, 0x45467a], iron: [0x41465f, 0x121327], roof: [0x44958a, 0x163650],
  glass: [0x22305a, 0x0d1230], window: [0x121628, 0x06070f],
  rock: [0x75809f, 0x1c2140], sea: [0x3b84a6, 0x0d2140], foam: 0xb9cbec, glint: 0xd4e2ff, spray: [0xf2f6ff, 0x7684c4],
  wallIn: [0xe4ddf0, 0x504e8a], stair: [0x626a92, 0x272b4c],
  cape: [0xf7b42a, 0xc2662a], coat: [0x3a5fa6, 0x1a2252], legs: [0x332b4e, 0x110e22], boots: [0xeba428, 0xb05a24],
  skin: [0xf8d3b7, 0xb2738c], hair: [0x47283f, 0x180c22], grip: [0x6a4a3e, 0x24151c], eye: 0x1f1533, mouth: 0x7a2c3c,
  lamp: 0xffc070, beam: 0xffe0a6, cottage: [0xc8c4da, 0x47457a], cottageRoof: [0x40446e, 0x15172f], warmWin: 0xffb45a,
  line: 0x0a0916,
};
// ------------------------------------------------------------------ shared uniforms & materials
const U = { time: { value: 0 }, flash: { value: 0 }, lamp: { value: 0 } };
const OW = { value: 0.003 };          // ink width: view-space offset per metre of depth (set per frame from the lens)
const LINE_PX = 2.3;                  // ink width in px at 720p (resolution independent)
const GRAD = toonGradient(4);
// Hue-shifted shadows: every toon material carries its own designed shadow colour (uShade, "kage" colour). The ambient
// (hemisphere) lights the shade colour; direct lights add (albedo - shade) through the 4-step ramp, so a fully lit face
// shows the albedo and the unlit side shows the shade colour, whatever the hue. Default shade = hue rotated toward violet.
const AMBK = { value: 0.9 };
const TOON_PARS = `varying vec3 vViewPosition;
uniform vec3 uShade; uniform float uAmbK;
struct ToonMaterial { vec3 diffuseColor; };
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
  vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
  reflectedLight.directDiffuse += irradiance * BRDF_Lambert( max( material.diffuseColor - uShade * uAmbK, vec3( 0.0 ) ) );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
  reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( uShade );
}
#define RE_Direct RE_Direct_Toon
#define RE_IndirectDiffuse RE_IndirectDiffuse_Toon`;
function autoShade(hex) {
  const hsl = {}; new THREE.Color(hex).getHSL(hsl, THREE.SRGBColorSpace);
  let dh = 0.7 - hsl.h; if (dh > 0.5) dh -= 1; if (dh < -0.5) dh += 1;
  return new THREE.Color().setHSL((hsl.h + dh * 0.35 + 1) % 1, Math.min(1, hsl.s * 1.05 + 0.12), hsl.l * 0.42, THREE.SRGBColorSpace);
}
function toon(color, o = {}) {
  let { shade, patch, key, ...rest } = o;
  if (Array.isArray(color)) { shade = shade ?? color[1]; color = color[0]; }
  const m = new THREE.MeshToonMaterial({ color, gradientMap: GRAD, ...rest });
  m.userData.shade = { value: shade !== undefined ? new THREE.Color(shade) : autoShade(color) };
  m.onBeforeCompile = (sh) => { sh.uniforms.uShade = m.userData.shade; sh.uniforms.uAmbK = AMBK; sh.fragmentShader = sh.fragmentShader.replace('#include <lights_toon_pars_fragment>', TOON_PARS); if (patch) patch(sh); };
  m.customProgramCacheKey = () => key || 'toon';
  return m;
}
const _lineCache = new Map();
function lineMat(mul = 1, color = PAL.line) {
  const key = mul + '|' + color; if (_lineCache.has(key)) return _lineCache.get(key);
  const m = new THREE.MeshBasicMaterial({ color, side: THREE.BackSide });
  m.onBeforeCompile = (sh) => {
    sh.uniforms.uOW = OW; sh.uniforms.uOM = { value: mul };
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nuniform float uOW; uniform float uOM;')
      .replace('#include <project_vertex>', `vec4 mvPosition = modelViewMatrix * vec4( transformed, 1.0 );
        vec3 oN = normalize( normalMatrix * normal );
        mvPosition.xyz += oN * ( uOW * uOM * max( -mvPosition.z, 0.05 ) );
        gl_Position = projectionMatrix * mvPosition;`);
  };
  _lineCache.set(key, m); return m;
}
// hull geometry: positions welded so hard-edged shapes get averaged normals (a closed, gap-free shell)
function hullGeom(g) {
  const c = new THREE.BufferGeometry(); c.setAttribute('position', g.attributes.position.clone()); if (g.index) c.setIndex(g.index.clone());
  const m = mergeVertices(c, 1e-4); m.computeVertexNormals(); return m;
}
const HULLS = [];
function ink(m, mul = 1, color = PAL.line, geom = null) {
  const h = new THREE.Mesh(geom || hullGeom(m.geometry), lineMat(mul, color)); h.castShadow = false; h.receiveShadow = false; h.userData.hull = true;
  m.add(h); m.userData.hull = h; HULLS.push(h); return h;
}
function mk(geom, mat, { cast = false, recv = false, line = 0, lineColor } = {}) {
  const m = new THREE.Mesh(geom, mat); m.castShadow = cast; m.receiveShadow = recv; if (line) ink(m, line, lineColor); return m;
}

let scene, camera, rig, post, W, H;
let hemi, key, flashL, lampPt, beamSpot, sky, moonDisc, clouds, sea, seaMat, rain, girl, lamp, lever, bolts = [], sprays = [], beams = [], glare;
const EXT = [], INT = [], LANTERN_EXT = [];

// ------------------------------------------------------------------ sky, moon, clouds
function makeSky() {
  const mat = new THREE.ShaderMaterial({
    uniforms: { uTop: { value: new THREE.Color(PAL.skyTop) }, uHor: { value: new THREE.Color(PAL.skyHor) }, uMoon: { value: MOON_DIR.clone() },
      uHalo: { value: new THREE.Color(PAL.moonHalo) }, uFlash: U.flash, uFlashCol: { value: new THREE.Color(PAL.flash) } },
    vertexShader: `varying vec3 vDir; void main(){ vDir = position; vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.0); gl_Position = p.xyww; }`,
    fragmentShader: `uniform vec3 uTop, uHor, uMoon, uHalo, uFlashCol; uniform float uFlash; varying vec3 vDir;
      void main(){ vec3 d = normalize(vDir); float h = d.y;
        // painted sky: soft gradient quantised into 5 broad bands (anime background trick)
        float g = smoothstep(-0.02, 0.62, h); g = floor(g * 5.0 + 0.5) / 5.0 * 0.6 + g * 0.4;
        vec3 col = mix(uHor, uTop, g);
        float m = max(dot(d, uMoon), 0.0);
        col += uHalo * (0.5 * pow(m, 60.0) + 0.2 * pow(m, 9.0));
        col = mix(col, uFlashCol * (0.75 + 0.5 * smoothstep(0.0, 0.5, h)), uFlash);
        gl_FragColor = vec4(col, 1.0); }`,
    side: THREE.BackSide, depthWrite: false, fog: false,
  });
  const m = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), mat); m.renderOrder = -10; m.frustumCulled = false; return m;
}
function makeClouds() {
  // painted storm banks: rows of overlapping puffs with flat-ish bottoms, lit from behind by the moon (silver rims).
  // Lineless, like an anime background painting; a gap is kept around the moon so its halo reads.
  const R = rng(4242); const geos = [];
  const bank = (az, dist, base, len, size, n, flat = 0.62) => {
    const parts = [];
    for (let i = 0; i < n; i++) {
      const x = (i / (n - 1) - 0.5) * len + (R() - 0.5) * size * 0.6; const r = size * (0.55 + R() * 0.75);
      const g = new THREE.SphereGeometry(1, 22, 14); g.scale(r * (1.2 + R() * 0.5), r * flat, r * (0.8 + R() * 0.4));
      g.translate(x, base + r * flat * 0.55 + R() * size * 0.25, (R() - 0.5) * size * 0.8); parts.push(g);
    }
    for (const g of parts) {
      g.rotateY(Math.PI / 2 - az); g.translate(Math.cos(az) * dist, 0, Math.sin(az) * dist); g.computeBoundingSphere();
      const bs = g.boundingSphere; const d = bs.center.clone().sub(C1); const ang = d.angleTo(MOON_DIR); const rad = Math.atan(bs.radius * 0.8 / d.length());
      if (ang < rad + 5 * DEG) continue;            // keep the moon (and the dead lantern in front of it) clear
      geos.push(g);
    }
  };
  for (let b = 0; b < 30; b++) {
    const az = b / 30 * Math.PI * 2 + (R() - 0.5) * 0.12; const near = angDiff(az, MOON_AZ);
    const dist = 240 + R() * 150; let base = 28 + R() * 55; if (near < 0.3) base -= 34;      // keep a gap around the moon
    bank(az, dist, base, 120 + R() * 110, 20 + R() * 16, 7 + Math.floor(R() * 5));
  }
  for (let b = 0; b < 18; b++) {                     // the high deck that closes the sky over the tower
    const az = b / 18 * Math.PI * 2 + R() * 0.25; if (angDiff(az, MOON_AZ) < 0.42) continue;
    bank(az, 130 + R() * 110, 120 + R() * 60, 160, 34 + R() * 14, 6, 0.42);
  }
  return mk(mergeGeometries(geos), toon(PAL.cloud, { fog: false }));
}

// ------------------------------------------------------------------ sea (polar grid, Gerstner waves, toon + foam lines)
const WAVES_GLSL = `
uniform float uTime; uniform vec2 uOff;
varying vec3 vSeaW; varying float vSeaH; varying vec3 vSeaN;
void gw(vec2 D, float L, float A, float Q, vec2 xz, float t, inout vec3 dP, inout vec3 N){
  float k = 6.2831853 / L; float w = sqrt(9.81 * k); float ph = k * dot(D, xz) - w * t;
  float S = sin(ph), C = cos(ph);
  dP.x += Q * A * D.x * C; dP.z += Q * A * D.y * C; dP.y += A * S;
  N.x -= D.x * k * A * C; N.z -= D.y * k * A * C; N.y -= Q * k * A * S;
}
void seaWaves(vec2 xz, float d, float t, out vec3 dP, out vec3 N){
  dP = vec3(0.0); N = vec3(0.0, 1.0, 0.0);
  gw(normalize(vec2(1.0, 0.25)), 24.0, 0.85 * (1.0 - smoothstep(260.0, 420.0, d)), 0.75, xz, t, dP, N);
  gw(normalize(vec2(0.7, 0.7)), 13.0, 0.45 * (1.0 - smoothstep(90.0, 160.0, d)), 0.7, xz, t, dP, N);
  gw(normalize(vec2(1.0, -0.45)), 8.0, 0.26 * (1.0 - smoothstep(45.0, 80.0, d)), 0.65, xz, t, dP, N);
  gw(normalize(vec2(0.2, 1.0)), 4.6, 0.12 * (1.0 - smoothstep(22.0, 40.0, d)), 0.6, xz, t, dP, N);
  gw(normalize(vec2(-0.5, 1.0)), 2.9, 0.06 * (1.0 - smoothstep(16.0, 30.0, d)), 0.5, xz, t, dP, N);
  N = normalize(N);
}`;
function makeSea(maskTex) {
  const NR = 160, NA = 256; const pos = [], nrm = [], idx = [];
  const ring = (i) => (i < 100 ? i * 0.3 : 30 * Math.exp((i - 100) * 0.062));
  for (let i = 0; i <= NR; i++) { const r = ring(i); for (let j = 0; j < NA; j++) { const a = j / NA * Math.PI * 2; pos.push(r * Math.cos(a), 0, r * Math.sin(a)); nrm.push(0, 1, 0); } }
  for (let i = 0; i < NR; i++) for (let j = 0; j < NA; j++) { const a = i * NA + j, b = i * NA + (j + 1) % NA, c = (i + 1) * NA + j, d = (i + 1) * NA + (j + 1) % NA; idx.push(a, b, c, b, d, c); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3)); g.setIndex(idx);
  const seaU = { uOff: { value: new THREE.Vector2() }, uMask: { value: maskTex }, uFoamCol: { value: new THREE.Color(PAL.foam) }, uGlintCol: { value: new THREE.Color(PAL.glint) }, uMoonDir: { value: MOON_DIR.clone() }, uCrest: { value: 0.95 }, uFoamGain: { value: 1.0 } };
  const seaPatch = (sh) => {
    Object.assign(sh.uniforms, seaU, { uTime: U.time, uFlash: U.flash });
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\n' + WAVES_GLSL)
      .replace('#include <beginnormal_vertex>', `vec2 seaXZ = position.xz + uOff; float seaD = length(position.xz);
        vec3 seaDP; vec3 objectNormal; seaWaves(seaXZ, seaD, uTime, seaDP, objectNormal);`)
      .replace('#include <begin_vertex>', 'vec3 transformed = position + seaDP;')
      .replace('#include <project_vertex>', `#include <project_vertex>
        vSeaW = (modelMatrix * vec4(transformed, 1.0)).xyz; vSeaH = seaDP.y; vSeaN = objectNormal;`);
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>
        uniform float uTime; uniform float uFlash; uniform sampler2D uMask; uniform vec3 uFoamCol; uniform vec3 uGlintCol; uniform vec3 uMoonDir; uniform float uCrest; uniform float uFoamGain;
        varying vec3 vSeaW; varying float vSeaH; varying vec3 vSeaN;`)
      .replace('#include <opaque_fragment>', `
        float sn = sin(vSeaW.x * 0.9 + uTime * 1.3) * sin(vSeaW.z * 0.7 - uTime * 1.1) * 0.08 + sin(vSeaW.x * 2.7 - vSeaW.z * 1.9) * 0.03;
        float msk = texture2D(uMask, vSeaW.xz / 90.0 + 0.5).r;
        float rings = step(0.84, fract(msk * 4.0 - uTime * 0.55 + sn * 2.0)) * smoothstep(0.06, 0.18, msk);
        float hh = vSeaH + sn * 0.5;
        float crestLine = step(uCrest, hh) * (1.0 - step(uCrest + 0.08, hh));        // white line on each crest shoulder
        float crestCap = step(uCrest + 0.3, hh);                                    // small caps on the tallest peaks only
        float lowLine = step(uCrest - 0.4, hh) * (1.0 - step(uCrest - 0.36, hh)) * 0.75; // second, thinner line below
        float foam = max(max(step(0.72, msk + sn), rings), max(max(crestLine, crestCap), lowLine));
        vec3 Vv = normalize(cameraPosition - vSeaW); vec3 Rf = reflect(-Vv, normalize(vSeaN));
        float glint = step(0.9975, dot(Rf, uMoonDir));
        outgoingLight += uGlintCol * glint * 0.38;
        outgoingLight = mix(outgoingLight, uFoamCol * (1.0 + 1.6 * uFlash) * uFoamGain, clamp(foam, 0.0, 1.0));
        #include <opaque_fragment>`);
  };
  seaMat = toon(PAL.sea, { patch: seaPatch, key: 'sea' }); seaMat.userData.u = seaU;
  const m = new THREE.Mesh(g, seaMat); m.frustumCulled = false; m.receiveShadow = true; return m;
}

// ------------------------------------------------------------------ island, rocks, cottage
function buildIsland(root, rocks) {
  const rockMat = toon(PAL.rock); const R = rng(66);
  const add = (x, y, z, s, sy = 1, sx = 1) => {
    const m = mk(new THREE.DodecahedronGeometry(s, 0), rockMat, { cast: true, recv: true, line: 0.9 });
    m.position.set(x, y, z); m.scale.set(sx, sy, 1); m.rotation.set(R() * 6, R() * 6, R() * 6); root.add(m); EXT.push(m);
    rocks.push({ x, z, r: s * Math.max(sx, 1) * 0.85 }); return m;
  };
  add(0, -1.6, 0, 6.6, 0.55, 1.05);           // the mound the tower stands on
  const ring = [[5.6, -0.2, 2.4, 0.8], [6.8, -0.5, 1.8, 1.1], [7.5, 0.1, 2.9, 0.6], [5.2, 0.0, 2.1, 0.9], [8.2, -0.4, 1.6, 1.0], [6.2, 0.2, 2.6, 0.7], [4.8, 0.3, 2.2, 1.3], [7.9, -0.2, 2.0, 0.9], [6.0, -0.3, 1.5, 1.0]];
  ring.forEach(([d, y, s, sy], i) => { const a = i / ring.length * Math.PI * 2 + 0.3 + (R() - 0.5) * 0.4; add(Math.cos(a) * d, y, Math.sin(a) * d, s, sy); });
  // outcrops toward the S1 camera (foreground depth) and a few sea stacks
  add(-14, -0.5, 6, 2.6, 1.2); add(12, -0.5, 9, 2.2, 1.0); add(-9.5, -0.4, -6.5, 1.7, 0.8); add(7.5, -0.5, -8.5, 1.5, 0.7);
  // cottage: the keeper's home at the base, one warm window (the only warm thing in S1)
  const cot = new THREE.Group(); cot.position.set(-4.1, 1.55, -2.6); cot.rotation.y = 0.55; root.add(cot); EXT.push(cot);
  const wall = mk(new THREE.BoxGeometry(3.2, 2.0, 2.6), toon(PAL.cottage), { cast: true, recv: true, line: 0.85 }); wall.position.y = 1.0; cot.add(wall);
  const tri = new THREE.Shape(); tri.moveTo(-1.85, 0); tri.lineTo(1.85, 0); tri.lineTo(0, 1.25); tri.closePath();
  const roofG = new THREE.ExtrudeGeometry(tri, { depth: 3.0, bevelEnabled: false }); roofG.translate(0, 0, -1.5); roofG.rotateY(Math.PI / 2);
  const roof = mk(roofG, toon(PAL.cottageRoof), { cast: true, line: 0.85 }); roof.position.y = 2.0; cot.add(roof);
  const win = new THREE.Mesh(new THREE.PlaneGeometry(0.55, 0.62), new THREE.MeshBasicMaterial({ color: new THREE.Color(PAL.warmWin).multiplyScalar(1.6) }));
  win.position.set(0.7, 1.15, -1.31); win.rotation.y = Math.PI; cot.add(win);
  const winF = mk(new THREE.BoxGeometry(0.7, 0.78, 0.06), toon(PAL.iron), { line: 0.6 }); winF.position.set(0.7, 1.15, -1.29); winF.scale.z = 0.5; cot.add(winF);
  const door = mk(new THREE.BoxGeometry(0.75, 1.45, 0.06), toon(PAL.window), { line: 0.6 }); door.position.set(-0.6, 0.72, -1.31); cot.add(door);
}
function maskTexture(rocks) {
  const S = 512, c = document.createElement('canvas'); c.width = c.height = S; const g = c.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, S, S); g.fillStyle = '#fff';
  const toPx = (v) => (v / 90 + 0.5) * S;
  for (const r of rocks) { g.beginPath(); g.arc(toPx(r.x), toPx(r.z), Math.max(2, r.r / 90 * S), 0, Math.PI * 2); g.fill(); }
  const b = document.createElement('canvas'); b.width = b.height = S; const bg = b.getContext('2d'); bg.filter = 'blur(14px)'; bg.drawImage(c, 0, 0);
  bg.filter = 'none'; bg.globalCompositeOperation = 'lighter'; bg.globalAlpha = 0.5; bg.drawImage(c, 0, 0);
  const t = new THREE.CanvasTexture(b); t.colorSpace = THREE.NoColorSpace; t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; return t;
}

// ------------------------------------------------------------------ lighthouse exterior, lantern, lamp, lever
function buildTower(root) {
  const T = new THREE.Group(); root.add(T);
  const towerMat = toon(PAL.tower), ironMat = toon(PAL.iron), ironD = toon(PAL.iron, { side: THREE.DoubleSide }), roofMat = toon(PAL.roof, { side: THREE.DoubleSide });
  const body = mk(new THREE.CylinderGeometry(TW.rTop, TW.rBot, TW.h, 72, 1, true), towerMat, { cast: true, recv: true, line: 0.8 }); body.position.y = TW.y0 + TW.h / 2; T.add(body); EXT.push(body);
  const plinth = mk(new THREE.CylinderGeometry(3.0, 3.35, 1.7, 48), toon(PAL.plinth), { cast: true, recv: true, line: 0.85 }); plinth.position.y = TW.y0 - 0.85; T.add(plinth); EXT.push(plinth);
  const door = mk(new THREE.BoxGeometry(0.9, 1.8, 0.3), toon(PAL.window), { line: 0.7 }); const da = -2.2; door.position.set(TW.rBot * Math.cos(da), TW.y0 + 0.9, TW.rBot * Math.sin(da)); door.rotation.y = Math.PI / 2 - da; T.add(door); EXT.push(door);
  const winMat = toon(PAL.window);
  for (const w of WINDOWS) {
    const r = TW.rBot + (TW.rTop - TW.rBot) * (w.y - TW.y0) / TW.h;
    const m = mk(new THREE.BoxGeometry(w.w * 1.15, w.h, 0.12), winMat, { line: 0.6 }); m.position.set(r * Math.cos(w.th), w.y, r * Math.sin(w.th)); m.rotation.y = Math.PI / 2 - w.th; T.add(m); EXT.push(m);
  }
  const corbel = mk(new THREE.CylinderGeometry(2.55, TW.rTop, 0.55, 64), towerMat, { cast: true, recv: true, line: 0.8 }); corbel.position.y = GAL_Y - 0.36; T.add(corbel); EXT.push(corbel);
  const deck = mk(new THREE.CylinderGeometry(2.82, 2.82, 0.16, 64), ironMat, { cast: true, recv: true, line: 0.8 }); deck.position.y = GAL_Y - 0.08; T.add(deck);
  // gallery railing
  const rg = [];
  for (let i = 0; i < 30; i++) { const a = i / 30 * Math.PI * 2; const c = new THREE.CylinderGeometry(0.024, 0.024, 0.95, 6); c.translate(2.7 * Math.cos(a), GAL_Y + 0.475, 2.7 * Math.sin(a)); rg.push(c); }
  for (const [y, rr] of [[0.95, 0.035], [0.5, 0.02]]) { const t = new THREE.TorusGeometry(2.7, rr, 6, 128); t.rotateX(Math.PI / 2); t.translate(0, GAL_Y + y, 0); rg.push(t); }
  const rail = mk(mergeGeometries(rg), ironMat, { cast: true, line: 0.55 }); T.add(rail);
  // lantern (octagonal): parapet, glazing, frame, roof, vent ball, rod
  const lan = new THREE.Group(); lan.position.y = GAL_Y; T.add(lan);
  const parapet = mk(new THREE.CylinderGeometry(1.56, 1.6, 0.72, 8, 1, true), ironD, { cast: true, recv: true, line: 0.8 }); parapet.position.y = 0.36; parapet.rotation.y = Math.PI / 8; lan.add(parapet); LANTERN_EXT.push(parapet.userData.hull);
  const glassMat = toon(PAL.glass, { transparent: true, opacity: 0.42, side: THREE.DoubleSide, depthWrite: false, emissive: 0x000000 });
  const glass = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 1.75, 8, 1, true), glassMat); glass.position.y = 0.72 + 0.875; glass.rotation.y = Math.PI / 8; glass.renderOrder = 2; lan.add(glass); lamp_glass = glass;
  const fr = [];
  for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 + Math.PI / 8; const b = new THREE.BoxGeometry(0.07, 1.75, 0.07); b.rotateY(a); b.translate(1.52 * Math.sin(a), 0.72 + 0.875, 1.52 * Math.cos(a)); fr.push(b); }
  for (const y of [0.74, 1.6, 2.45]) { const c = new THREE.CylinderGeometry(1.54, 1.54, y === 1.6 ? 0.04 : 0.09, 8, 1, true); c.rotateY(Math.PI / 8); c.translate(0, y, 0); fr.push(c.toNonIndexed()); }
  const frame = mk(mergeGeometries(fr.map((g) => (g.index ? g.toNonIndexed() : g))), ironD, { cast: true, line: 0.6 }); lan.add(frame);
  const roof = mk(new THREE.ConeGeometry(1.92, 1.1, 8, 1, true), roofMat, { cast: true, recv: true, line: 0.8 }); roof.position.y = 2.45 + 0.55; roof.rotation.y = Math.PI / 8; lan.add(roof); LANTERN_EXT.push(roof.userData.hull);
  const ceil = mk(new THREE.CircleGeometry(1.55, 8), toon(PAL.iron, { side: THREE.DoubleSide })); ceil.rotation.x = Math.PI / 2; ceil.rotation.z = Math.PI / 8; ceil.position.y = 2.47; lan.add(ceil);
  const ball = mk(new THREE.SphereGeometry(0.28, 20, 14), roofMat, { cast: true, line: 0.7 }); ball.position.y = 3.72; lan.add(ball);
  const rod = mk(new THREE.CylinderGeometry(0.018, 0.03, 1.1, 6), ironMat, { line: 0.5 }); rod.position.y = 4.4; lan.add(rod);
  // the lamp: pedestal, Fresnel lens (ribbed lathe), burner sphere (emissive), rings
  lamp = new THREE.Group(); lamp.position.y = GAL_Y; T.add(lamp);
  const ped = mk(new THREE.CylinderGeometry(0.14, 0.24, 0.62, 20), ironMat, { cast: true, recv: true, line: 0.8 }); ped.position.y = 0.31; lamp.add(ped);
  const pts = []; const N = 14; for (let i = 0; i <= N; i++) { const y = -0.3 + 0.6 * i / N; const bul = Math.sqrt(Math.max(0, 1 - Math.pow(y / 0.38, 2))); pts.push(new THREE.Vector2(0.235 * bul + (i % 2 ? 0.026 : 0.0), y)); }
  // emissive map: one bright band per prism ring (lathe v runs along the profile), brightest at the bullseye belt
  const ec = document.createElement('canvas'); ec.width = 4; ec.height = 140; const eg = ec.getContext('2d');
  for (let i = 0; i < N; i++) { const mid = 1 - Math.abs((i + 0.5) / N - 0.5) * 1.3; const v = (i % 2 ? 0.95 : 0.32) * mid; const c = Math.round(255 * v); eg.fillStyle = `rgb(${c},${c},${c})`; eg.fillRect(0, 140 - (i + 1) * 10, 4, 10); }
  const etex = new THREE.CanvasTexture(ec); etex.colorSpace = THREE.SRGBColorSpace; etex.magFilter = THREE.NearestFilter;
  const lensMat = toon([0x7f9cb6, 0x1d2a4a], { transparent: true, opacity: 0.8, emissive: 0x000000, emissiveMap: etex, depthWrite: false });
  const lens = new THREE.Mesh(new THREE.LatheGeometry(pts, 40), lensMat); lens.position.y = 0.95; lens.renderOrder = 3; lamp.add(lens);
  for (const y of [0.95 - 0.31, 0.95 + 0.31]) { const r = mk(new THREE.TorusGeometry(0.2, 0.026, 8, 40), ironMat, { line: 0.7 }); r.rotation.x = Math.PI / 2; r.position.y = y; lamp.add(r); }
  const cap = mk(new THREE.ConeGeometry(0.22, 0.18, 20), ironMat, { line: 0.7 }); cap.position.y = 0.95 + 0.41; lamp.add(cap);
  const burner = new THREE.Mesh(new THREE.SphereGeometry(0.075, 24, 16), new THREE.MeshBasicMaterial({ color: 0x1a1a24 })); burner.position.y = 0.95; lamp.add(burner);
  lamp.userData = { lens, lensMat, burner, glassMat };
  // the ignition lever: floor quadrant + arm + grip bar (rotates about X; +angle tilts toward her at +z)
  lever = new THREE.Group(); lever.position.set(0, GAL_Y + 0.1, LV.z); T.add(lever);
  const quad = mk(new THREE.BoxGeometry(0.16, 0.14, 0.24), ironMat, { cast: true, line: 0.8 }); quad.position.set(0, GAL_Y + 0.05, LV.z); T.add(quad);
  const ratchet = mk(new THREE.TorusGeometry(0.15, 0.014, 6, 24, 1.4), ironMat, { line: 0.6 }); ratchet.rotation.y = Math.PI / 2; ratchet.rotation.z = Math.PI / 2 - 0.7; ratchet.position.set(0.09, GAL_Y + 0.1, LV.z); T.add(ratchet);
  const arm = mk(new THREE.CylinderGeometry(0.016, 0.022, LV.len, 10), ironMat, { cast: true, line: 0.85 }); arm.position.y = LV.len / 2; lever.add(arm);
  const grip = mk(new THREE.CylinderGeometry(0.018, 0.018, 0.28, 14), toon(PAL.grip), { cast: true, line: 0.85 }); grip.rotation.z = Math.PI / 2; grip.position.y = LV.len; lever.add(grip);
  lever.userData.handle = new THREE.Object3D(); lever.userData.handle.position.y = LV.len; lever.add(lever.userData.handle);
  return T;
}
let lamp_glass;

// ------------------------------------------------------------------ interior: wall with slit windows, stair helix, rail
function angDiff(a, b) { return Math.abs(Math.atan2(Math.sin(a - b), Math.cos(a - b))); }
function buildInterior(root) {
  const I = new THREE.Group(); root.add(I);
  const y0 = 2.6, y1 = 14.6, nTh = 128, dy = 0.125, nY = Math.round((y1 - y0) / dy);
  const cellTh = Math.PI * 2 / nTh;
  const holes = WINDOWS.map((w) => { const i0 = Math.round((w.th - w.w / R_IN / 2) / cellTh), i1 = Math.round((w.th + w.w / R_IN / 2) / cellTh); const j0 = Math.round((w.y - w.h / 2 - y0) / dy), j1 = Math.round((w.y + w.h / 2 - y0) / dy); return { i0, i1, j0, j1 }; });
  const inHole = (i, j) => holes.some((h) => { let ii = i; while (ii < h.i0) ii += nTh; while (ii >= h.i0 + nTh) ii -= nTh; return ii >= h.i0 && ii < h.i1 && j >= h.j0 && j < h.j1; });
  const pos = [], nrm = [], idx = [];
  for (let j = 0; j <= nY; j++) for (let i = 0; i <= nTh; i++) { const th = i * cellTh; pos.push(R_IN * Math.cos(th), y0 + j * dy, R_IN * Math.sin(th)); nrm.push(-Math.cos(th), 0, -Math.sin(th)); }
  for (let j = 0; j < nY; j++) for (let i = 0; i < nTh; i++) { if (inHole(i, j)) continue; const a = j * (nTh + 1) + i, b = a + 1, c = a + nTh + 1, d = c + 1; idx.push(a, b, c, b, d, c); }
  const wg = new THREE.BufferGeometry(); wg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); wg.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3)); wg.setIndex(idx);
  const wallMat = toon(PAL.wallIn);
  const wall = mk(wg, wallMat, { cast: true, recv: true }); I.add(wall);
  // jambs (window reveals, 0.7 m deep) and iron frames with ink
  const jp = [], jn = [], fr = [];
  for (const h of holes) {
    const ta = h.i0 * cellTh, tb = h.i1 * cellTh, ya = y0 + h.j0 * dy, yb = y0 + h.j1 * dy, ro = 2.45;
    const P = (t, r, y) => [r * Math.cos(t), y, r * Math.sin(t)];
    const quad = (A, B, C, D, n) => { jp.push(...A, ...B, ...C, ...A, ...C, ...D); for (let k = 0; k < 6; k++) jn.push(...n); };
    const nA = [-Math.sin(ta), 0, Math.cos(ta)], nB = [Math.sin(tb), 0, -Math.cos(tb)];
    quad(P(ta, R_IN, ya), P(ta, ro, ya), P(ta, ro, yb), P(ta, R_IN, yb), nA);
    quad(P(tb, R_IN, yb), P(tb, ro, yb), P(tb, ro, ya), P(tb, R_IN, ya), nB);
    quad(P(ta, R_IN, ya), P(tb, R_IN, ya), P(tb, ro, ya), P(ta, ro, ya), [0, 1, 0]);
    quad(P(ta, R_IN, yb), P(ta, ro, yb), P(tb, ro, yb), P(tb, R_IN, yb), [0, -1, 0]);
    const tm = (ta + tb) / 2, wdt = (tb - ta) * R_IN, hgt = yb - ya;
    for (const [bw, bh, ox, oy] of [[0.05, hgt + 0.1, -wdt / 2 - 0.02, 0], [0.05, hgt + 0.1, wdt / 2 + 0.02, 0], [wdt + 0.1, 0.05, 0, -hgt / 2 - 0.02], [wdt + 0.1, 0.05, 0, hgt / 2 + 0.02]]) {
      const b = new THREE.BoxGeometry(bw, bh, 0.05); b.translate(ox, oy, 0); b.rotateY(-Math.PI / 2 - tm); b.translate((R_IN - 0.02) * Math.cos(tm), (ya + yb) / 2, (R_IN - 0.02) * Math.sin(tm)); fr.push(b);
    }
  }
  const jg = new THREE.BufferGeometry(); jg.setAttribute('position', new THREE.Float32BufferAttribute(jp, 3)); jg.setAttribute('normal', new THREE.Float32BufferAttribute(jn, 3));
  const jamb = mk(jg, toon(PAL.wallIn, { side: THREE.DoubleSide }), { cast: true, recv: true }); I.add(jamb);
  const frames = mk(mergeGeometries(fr), toon(PAL.iron), { cast: true, recv: true, line: 0.75 }); I.add(frames);
  // stair plates (open risers, iron)
  const sg = [];
  const sector = (r0, r1, a0, a1, seg = 5) => { const s = new THREE.Shape(); for (let i = 0; i <= seg; i++) { const a = a0 + (a1 - a0) * i / seg; i === 0 ? s.moveTo(r1 * Math.cos(a), r1 * Math.sin(a)) : s.lineTo(r1 * Math.cos(a), r1 * Math.sin(a)); } for (let i = seg; i >= 0; i--) { const a = a0 + (a1 - a0) * i / seg; s.lineTo(r0 * Math.cos(a), r0 * Math.sin(a)); } s.closePath(); return s; };
  for (let k = ST.kMin; k <= ST.kMax; k++) { const th = stepTh(k); const g = new THREE.ExtrudeGeometry(sector(ST.r0, ST.r1, th - ST.dth * 0.5, th + ST.dth * 0.5), { depth: ST.thick, bevelEnabled: false, curveSegments: 1 }); g.rotateX(Math.PI / 2); g.translate(0, stepY(k), 0); sg.push(g); }
  const stairs = mk(mergeGeometries(sg), toon(PAL.stair), { cast: true, recv: true, line: 0.85 }); I.add(stairs);
  // handrail on the well side + posts every 3 steps
  class Helix extends THREE.Curve { getPoint(t, out = new THREE.Vector3()) { const k = lerp(ST.kMin, ST.kMax, t); const th = stepTh(k); return out.set(0.6 * Math.cos(th), stepY(k) + 0.86, 0.6 * Math.sin(th)); } }
  const rg = [new THREE.TubeGeometry(new Helix(), 600, 0.02, 6, false)];
  for (let k = ST.kMin; k <= ST.kMax; k += 3) { const th = stepTh(k); const c = new THREE.CylinderGeometry(0.013, 0.013, 0.86, 6); c.translate(0.6 * Math.cos(th), stepY(k) + 0.43, 0.6 * Math.sin(th)); rg.push(c); }
  const rail = mk(mergeGeometries(rg.map((g) => (g.index ? g.toNonIndexed() : g))), toon(PAL.iron), { cast: true, line: 0.6 }); I.add(rail);
  const capMat = toon(PAL.iron, { side: THREE.DoubleSide });
  const ceil = mk(new THREE.CircleGeometry(R_IN + 0.05, 48), capMat); ceil.rotation.x = Math.PI / 2; ceil.position.y = y1; I.add(ceil);
  const floor = mk(new THREE.CircleGeometry(R_IN + 0.05, 48), capMat); floor.rotation.x = -Math.PI / 2; floor.position.y = y0; I.add(floor);
  INT.push(I); return I;
}

// ------------------------------------------------------------------ rain (instanced streak quads, on 1s)
function makeRain(count, seed) {
  const R = rng(seed); const g = new THREE.InstancedBufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute([0, -1, 0, 1, -1, 0, 1, 1, 0, 0, 1, 0], 3)); g.setIndex([0, 1, 2, 0, 2, 3]);
  const off = new Float32Array(count * 3), rnd = new Float32Array(count); for (let i = 0; i < count; i++) { off[i * 3] = R(); off[i * 3 + 1] = R(); off[i * 3 + 2] = R(); rnd[i] = R(); }
  g.setAttribute('aOff', new THREE.InstancedBufferAttribute(off, 3)); g.setAttribute('aRnd', new THREE.InstancedBufferAttribute(rnd, 1)); g.instanceCount = count;
  const mat = new THREE.ShaderMaterial({
    uniforms: { uTime: U.time, uFlash: U.flash, uBoxMin: { value: V3() }, uBoxSize: { value: V3(36, 30, 36) }, uVel: { value: V3(-3.5, -26, 1.6) }, uStreak: { value: 0.034 },
      uWidthW: { value: 0.006 }, uWidthPx: { value: 0.001 }, uTower: { value: V3(0, 0, R_IN + 0.05) }, uColor: { value: new THREE.Color(0x9fb2e6) }, uLit: { value: new THREE.Color(0xffd28a) },
      uOpacity: { value: 0.42 }, uBeamPos: { value: LAMP_C.clone() }, uBeamDir0: { value: V3(1, 0, 0) }, uBeamDir1: { value: V3(-1, 0, 0) }, uBeamCos: { value: 0.99 }, uBeamOn: { value: 0 } },
    vertexShader: `attribute vec3 aOff; attribute float aRnd;
      uniform float uTime, uStreak, uWidthW, uWidthPx, uBeamCos, uBeamOn; uniform vec3 uBoxMin, uBoxSize, uVel, uTower, uBeamPos, uBeamDir0, uBeamDir1;
      varying float vA; varying float vLit; varying float vFade;
      void main(){
        vec3 v = uVel * (0.8 + 0.4 * aRnd);
        vec3 p = mod(aOff * uBoxSize + v * uTime - uBoxMin, uBoxSize) + uBoxMin;
        vec3 tail = p - v * uStreak;
        vec4 mvH = viewMatrix * vec4(p, 1.0), mvT = viewMatrix * vec4(tail, 1.0);
        vec4 mv = mix(mvH, mvT, position.x);
        vec2 sH = mvH.xy / max(-mvH.z, 0.05), sT = mvT.xy / max(-mvT.z, 0.05);
        vec2 dir = sT - sH; float dl = length(dir); dir = dl > 1e-6 ? dir / dl : vec2(0.0, -1.0);
        float depth = max(-mv.z, 0.05);
        mv.xy += vec2(-dir.y, dir.x) * position.y * max(uWidthW, uWidthPx * depth);
        vA = 1.0 - position.x;
        vFade = smoothstep(1.2, 3.2, depth) * (1.0 - smoothstep(22.0, 40.0, depth));
        vec3 tob = p - uBeamPos; float tl = length(tob); vec3 tn = tob / max(tl, 1e-3);
        vLit = uBeamOn * smoothstep(uBeamCos, uBeamCos + 0.006, max(dot(tn, uBeamDir0), dot(tn, uBeamDir1))) * (1.0 - smoothstep(35.0, 60.0, tl));
        float inside = step(length(p.xz - uTower.xy), uTower.z) * step(p.y, 23.2);
        gl_Position = inside > 0.5 ? vec4(0.0, 0.0, 2.0, 1.0) : projectionMatrix * mv;
      }`,
    fragmentShader: `uniform vec3 uColor, uLit; uniform float uOpacity, uFlash; varying float vA; varying float vLit; varying float vFade;
      void main(){ float a = vA * vA * uOpacity * vFade * (1.0 + 1.5 * vLit); vec3 c = mix(uColor * (1.0 + 2.0 * uFlash), uLit * 1.6, vLit); gl_FragColor = vec4(c, clamp(a, 0.0, 1.0)); }`,
    transparent: true, depthWrite: false,
  });
  const m = new THREE.Mesh(g, mat); m.frustumCulled = false; m.renderOrder = 5; return m;
}

// ------------------------------------------------------------------ lightning bolt ribbon (visible 2 frames)
function boltGeometry(seed, len, width) {
  const R = rng(seed); const pos = [];
  const channel = (p0, p1, w0, w1, depth) => {
    let pts = [p0.clone(), p1.clone()];
    for (let it = 0; it < 6; it++) { const np = []; for (let i = 0; i < pts.length - 1; i++) { const a = pts[i], b = pts[i + 1]; const m = a.clone().lerp(b, 0.5); m.x += (R() - 0.5) * a.distanceTo(b) * 0.6; np.push(a, m); } np.push(pts[pts.length - 1]); pts = np; }
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i], b = pts[i + 1]; const d = b.clone().sub(a).normalize(); const nx = -d.y, ny = d.x;
      const wa = lerp(w0, w1, i / (pts.length - 1)) / 2, wb = lerp(w0, w1, (i + 1) / (pts.length - 1)) / 2;
      pos.push(a.x - nx * wa, a.y - ny * wa, 0, a.x + nx * wa, a.y + ny * wa, 0, b.x + nx * wb, b.y + ny * wb, 0, a.x - nx * wa, a.y - ny * wa, 0, b.x + nx * wb, b.y + ny * wb, 0, b.x - nx * wb, b.y - ny * wb, 0);
    }
    if (depth < 2) for (let k = 0; k < 3 - depth; k++) { const i = 8 + Math.floor(R() * (pts.length - 24)); const a = pts[i]; const L = len * (0.18 + R() * 0.2) / (depth + 1); const ang = -Math.PI / 2 + (R() < 0.5 ? -1 : 1) * (0.5 + R() * 0.5); channel(a, V3(a.x + Math.cos(ang) * L, a.y + Math.sin(ang) * L, 0), w0 * 0.45, w1 * 0.2, depth + 1); }
  };
  channel(V3(0, 0, 0), V3((R() - 0.5) * len * 0.3, -len, 0), width, width * 0.35, 0);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); return g;
}
function makeBolt(seed, pos, lookAt, len, width) {
  const grp = new THREE.Group(); grp.position.copy(pos); grp.lookAt(lookAt);
  const core = new THREE.Mesh(boltGeometry(seed, len, width), new THREE.MeshBasicMaterial({ color: new THREE.Color(4.0, 4.4, 6.0), side: THREE.DoubleSide, fog: false }));
  const glow = new THREE.Mesh(boltGeometry(seed, len, width * 5), new THREE.MeshBasicMaterial({ color: new THREE.Color(0.25, 0.35, 1.0), transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false }));
  grp.add(glow, core); grp.visible = false; return grp;
}

// ------------------------------------------------------------------ wave-crash spray (cel blobs, on 2s)
function makeSpray(seed, n, scale = 1) {
  // a wave-crash plume: heavy blobs low and wide, light ones high; each stretched along its velocity, growing then
  // thinning as it falls, plus a ring of flat foam at the base. Evaluated on 2s (FX on twos).
  const R = rng(seed); const grp = new THREE.Group(); const mat = toon(PAL.spray);
  const prof = []; for (let k = 0; k <= 16; k++) { const t = k / 16; prof.push(new THREE.Vector2(Math.sin(Math.PI * t) * (1 - 0.62 * t) + 1e-3, -Math.cos(Math.PI * t) * (1 + 0.5 * t))); }
  const drop = new THREE.LatheGeometry(prof, 14); drop.computeVertexNormals();          // round head at -Y, point at +Y (trails the motion)
  const ball = new THREE.IcosahedronGeometry(1, 2); const hgD = hullGeom(drop), hgB = hullGeom(ball); const blobs = [];
  for (let i = 0; i < n; i++) {
    const tier = R(), ring = i < 8; const ang = R() * Math.PI * 2;
    const m = new THREE.Mesh(ring ? ball : drop, mat); ink(m, 0.7, 0x1c2550, ring ? hgB : hgD); grp.add(m);
    if (ring) { const sp = (3 + R() * 2) * scale; blobs.push({ m, v: V3(Math.cos(ang) * sp, 0.6 * scale, Math.sin(ang) * sp), s: (1.0 + R() * 0.5) * scale, d: R() * 0.06, flat: true }); continue; }
    const spread = 0.08 + 0.4 * R() * (1 - tier * 0.5); const sp = (6.5 + 8 * tier) * scale;
    blobs.push({ m, v: V3(Math.sin(spread) * Math.cos(ang) * sp, Math.cos(spread) * sp, Math.sin(spread) * Math.sin(ang) * sp), s: (1.25 - 0.85 * tier) * (0.6 + 0.4 * R()) * scale, d: R() * 0.1 + tier * 0.06, flat: false });
  }
  const vel = V3();
  grp.update = (age) => {
    for (const b of blobs) {
      const a = age - b.d; if (a < 0 || a > 1.8) { b.m.visible = false; continue; }
      const p = b.v.clone().multiplyScalar(a); p.y -= (b.flat ? 1.0 : 4.9) * a * a; if (p.y < -0.8) { b.m.visible = false; continue; }
      b.m.visible = true; b.m.position.copy(p);
      const grow = smoothstep(0, 0.14, a), fade = 1 - smoothstep(0.55, 1.6, a); const sc = b.s * grow * (0.25 + 0.75 * fade);
      if (b.flat) { b.m.quaternion.identity(); b.m.scale.set(sc * 1.4, sc * 0.35, sc * 1.4); continue; }
      vel.copy(b.v); vel.y -= 9.81 * a; const spd = vel.length(); b.m.quaternion.setFromUnitVectors(YUP, vel.multiplyScalar(-1 / Math.max(spd, 1e-3)));
      b.m.scale.set(sc * 0.8, sc * (0.9 + 0.09 * spd), sc * 0.8);
    }
  };
  return grp;
}

// ------------------------------------------------------------------ the girl (primitives) + rig helpers
const GD = { L1: 0.33, L2: 0.32, hipX: 0.082, hipY: -0.035, chestY: 0.12, shX: 0.14, shY: 0.225, A1: 0.22, A2: 0.2, headY: 0.4 };
const SOLE = V3(0, -0.093, 0.045), TOE = V3(0, -0.093, 0.13), WRIST = V3(0, 0.008, 0.078);
function hairGeometry() {
  const parts = [];
  const cap = new THREE.SphereGeometry(0.128, 32, 18, 0, Math.PI * 2, 0, Math.PI * 0.57); cap.rotateX(-0.42); cap.translate(0, 0.012, -0.012); parts.push(cap);
  for (const s of [1, -1]) { const b = new THREE.SphereGeometry(1, 18, 14); b.scale(0.045, 0.092, 0.088); b.rotateZ(0.12 * s); b.translate(0.097 * s, -0.04, -0.02); parts.push(b); }
  const back = new THREE.SphereGeometry(1, 20, 14); back.scale(0.112, 0.088, 0.072); back.translate(0, -0.034, -0.066); parts.push(back);
  [-0.072, -0.036, 0.0, 0.036, 0.07].forEach((x) => { const c = new THREE.ConeGeometry(0.031, 0.085, 10); c.rotateX(Math.PI); c.scale(1, 1, 0.45); c.rotateZ(-x * 2.4); c.rotateX(-0.28); c.translate(x, 0.046 - Math.abs(x) * 0.28, 0.096 - Math.abs(x) * 0.3); parts.push(c); });
  return mergeGeometries(parts);
}
function capsuleBetween(a, b, r) { const d = b.clone().sub(a); const len = d.length(); const g = new THREE.CapsuleGeometry(r, Math.max(0.0005, len), 4, 10); g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(YUP, d.normalize())); g.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2); return g; }
function handGeometry() { // a fist closed around a bar along X through the origin; wrist toward +Z
  const parts = []; const pal = new THREE.CapsuleGeometry(0.027, 0.05, 4, 10); pal.rotateZ(Math.PI / 2); pal.scale(1, 0.8, 1.15); pal.translate(0, 0.006, 0.04); parts.push(pal);
  const xs = [-0.026, -0.009, 0.008, 0.025], ln = [0.85, 1.0, 0.98, 0.88];
  xs.forEach((x, i) => { const k = ln[i]; const K = V3(x, 0.024, 0.026), P1 = V3(x, 0.029, -0.004 * k), P2 = V3(x, 0.008, -0.027 * k), P3 = V3(x, -0.018, -0.017 * k); parts.push(capsuleBetween(K, P1, 0.0095), capsuleBetween(P1, P2, 0.0088), capsuleBetween(P2, P3, 0.008)); });
  const T0 = V3(0.034, 0.0, 0.04), T1 = V3(0.032, -0.022, 0.016), T2 = V3(0.016, -0.027, -0.004); parts.push(capsuleBetween(T0, T1, 0.0105), capsuleBetween(T1, T2, 0.0095));
  return mergeGeometries(parts);
}
function bootGeometry() {
  const foot = new THREE.CapsuleGeometry(0.048, 0.11, 6, 14); foot.rotateX(Math.PI / 2); foot.scale(1, 0.8, 1); foot.translate(0, -0.055, 0.045);
  const shaft = new THREE.CylinderGeometry(0.056, 0.052, 0.15, 16); shaft.translate(0, 0.005, 0);
  return mergeGeometries([foot, shaft]);
}
function makeCape(mat) {
  const NU = 12, NV = 7, nL = (NU + 1) * (NV + 1); const id = (l, i, j) => l * nL + j * (NU + 1) + i; const idx = [];
  for (let j = 0; j < NV; j++) for (let i = 0; i < NU; i++) {
    const a = id(0, i, j), b = id(0, i + 1, j), c = id(0, i, j + 1), d = id(0, i + 1, j + 1); idx.push(a, b, c, b, d, c);
    const a2 = id(1, i, j), b2 = id(1, i + 1, j), c2 = id(1, i, j + 1), d2 = id(1, i + 1, j + 1); idx.push(a2, c2, b2, b2, c2, d2);
  }
  for (let i = 0; i < NU; i++) { let o0 = id(0, i, 0), o1 = id(0, i + 1, 0), n0 = id(1, i, 0), n1 = id(1, i + 1, 0); idx.push(o0, n0, o1, o1, n0, n1); o0 = id(0, i, NV); o1 = id(0, i + 1, NV); n0 = id(1, i, NV); n1 = id(1, i + 1, NV); idx.push(o0, o1, n0, o1, n1, n0); }
  for (let j = 0; j < NV; j++) { let oa = id(0, 0, j), ob = id(0, 0, j + 1), na = id(1, 0, j), nb = id(1, 0, j + 1); idx.push(oa, ob, na, ob, nb, na); oa = id(0, NU, j); ob = id(0, NU, j + 1); na = id(1, NU, j); nb = id(1, NU, j + 1); idx.push(oa, na, ob, ob, na, nb); }
  const g = new THREE.BufferGeometry(); const pa = new THREE.Float32BufferAttribute(new Float32Array(nL * 2 * 3), 3); g.setAttribute('position', pa); g.setIndex(idx);
  const m = new THREE.Mesh(g, mat); m.castShadow = true; m.receiveShadow = true; m.frustumCulled = false;
  const hull = new THREE.Mesh(g, lineMat(1)); hull.frustumCulled = false; m.add(hull); HULLS.push(hull);
  const tmp = V3(), rad = V3();
  m.update = (drag, ft, famp) => { // drag: chest-local hem offset (m); ft: flutter time
    for (let j = 0; j <= NV; j++) for (let i = 0; i <= NU; i++) {
      const v = j / NV, u = i / NU; const pm = lerp(1.8, 1.45, v); const ph = (u - 0.5) * 2 * pm; const r = lerp(0.132, 0.23, Math.pow(v, 0.85)); const y = lerp(0.268, -0.1, v);
      rad.set(Math.sin(ph), 0, -Math.cos(ph)); tmp.set(r * rad.x, y, r * rad.z);
      const w = Math.pow(v, 1.35) * (0.55 + 0.45 * Math.cos(ph * 0.6));
      tmp.addScaledVector(drag, w);
      const fl = famp * Math.pow(v, 1.2) * Math.sin(u * 9.0 + ft * 11.0 + v * 4.0); tmp.addScaledVector(rad, fl);
      // keep the cloth outside the body (chest ~0.13, coat skirt ~0.18 at the hem)
      const minR = lerp(0.128, 0.19, smoothstep(0.05, -0.2, tmp.y)); const rr = Math.hypot(tmp.x, tmp.z * 1.12); if (rr < minR) { const s = minR / Math.max(rr, 1e-4); tmp.x *= s; tmp.z *= s; }
      pa.setXYZ(id(0, i, j), tmp.x + rad.x * 0.008, tmp.y, tmp.z + rad.z * 0.008); pa.setXYZ(id(1, i, j), tmp.x - rad.x * 0.008, tmp.y, tmp.z - rad.z * 0.008);
    }
    pa.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere();
  };
  return m;
}
function makeGirl() {
  const G = { grp: new THREE.Group() };
  const skin = toon(PAL.skin), hair = toon(PAL.hair), cape = toon(PAL.cape), coat = toon(PAL.coat), legs = toon(PAL.legs), boots = toon(PAL.boots);
  G.catchMat = new THREE.MeshBasicMaterial({ color: 0x8fa0d0 }); G.eyeMat = new THREE.MeshBasicMaterial({ color: PAL.eye }); G.mouthMat = new THREE.MeshBasicMaterial({ color: PAL.mouth });
  G.pelvis = new THREE.Group(); G.grp.add(G.pelvis);
  G.skirt = mk(new THREE.CylinderGeometry(0.11, 0.168, 0.25, 24), coat, { cast: true, recv: true, line: 1 }); G.skirt.position.y = -0.03; G.pelvis.add(G.skirt);
  G.chest = new THREE.Group(); G.chest.position.y = GD.chestY; G.pelvis.add(G.chest);
  G.torso = mk(new THREE.CapsuleGeometry(0.104, 0.13, 6, 18), coat, { cast: true, recv: true, line: 1 }); G.torso.position.y = 0.12; G.torso.scale.set(1, 1, 0.84); G.chest.add(G.torso);
  G.neck = mk(new THREE.CapsuleGeometry(0.034, 0.06, 4, 10), skin, { cast: true, line: 1 }); G.neck.position.y = 0.29; G.chest.add(G.neck);
  G.head = new THREE.Group(); G.head.position.y = GD.headY; G.chest.add(G.head);
  G.headM = mk(new THREE.SphereGeometry(0.115, 32, 24), skin, { cast: true, recv: true, line: 1 }); G.headM.scale.set(0.97, 1.0, 0.97); G.head.add(G.headM);
  G.hairM = mk(hairGeometry(), hair, { cast: true, recv: true, line: 1 }); G.head.add(G.hairM);
  G.eyes = []; G.catches = []; G.brows = [];
  for (const s of [1, -1]) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.0195, 16, 12), G.eyeMat); e.position.set(0.042 * s, -0.006, 0.1); e.rotation.y = 0.4 * s; e.userData.base = V3(0.78, 1.34, 0.5); e.scale.copy(e.userData.base); G.head.add(e); G.eyes.push(e);
    const c = new THREE.Mesh(new THREE.SphereGeometry(0.0062, 10, 8), G.catchMat); c.position.set(0.042 * s + 0.007, 0.006, 0.108); G.head.add(c); G.catches.push(c);
    const b = new THREE.Mesh(new THREE.CapsuleGeometry(0.0045, 0.026, 3, 6), G.eyeMat); b.rotation.z = Math.PI / 2; b.position.set(0.045 * s, 0.043, 0.103); b.userData.s = s; G.head.add(b); G.brows.push(b);
  }
  G.mouth = new THREE.Mesh(new THREE.SphereGeometry(0.011, 12, 8), G.mouthMat); G.mouth.position.set(0, -0.058, 0.1); G.mouth.scale.set(1.5, 0.45, 0.5); G.head.add(G.mouth);
  G.tail = new THREE.Group(); G.tail.position.set(0, -0.035, -0.105); G.head.add(G.tail);
  const tg = new THREE.SphereGeometry(1, 18, 14); tg.scale(0.042, 0.1, 0.04); tg.translate(0, -0.085, -0.02); G.tail.add(mk(tg, hair, { cast: true, line: 1 }));
  const tie = mk(new THREE.SphereGeometry(0.022, 12, 8), cape, { line: 1 }); G.tail.add(tie);
  G.shL = new THREE.Object3D(); G.shL.position.set(GD.shX, GD.shY, -0.005); G.chest.add(G.shL);
  G.shR = new THREE.Object3D(); G.shR.position.set(-GD.shX, GD.shY, -0.005); G.chest.add(G.shR);
  G.cape = makeCape(cape); G.chest.add(G.cape);
  G.hood = mk(new THREE.SphereGeometry(1, 20, 14), cape, { cast: true, line: 1 }); G.hood.scale.set(0.11, 0.075, 0.085); G.hood.position.set(0, 0.272, -0.108); G.chest.add(G.hood);
  const seg = (r, len, mat) => { const m = mk(new THREE.CapsuleGeometry(r, Math.max(0.001, len - 2 * r), 4, 12), mat, { cast: true, recv: true, line: 1 }); m.userData.len = len; G.grp.add(m); return m; };
  G.uaL = seg(0.042, GD.A1 + 0.04, coat); G.uaR = seg(0.042, GD.A1 + 0.04, coat); G.faL = seg(0.036, GD.A2 + 0.03, coat); G.faR = seg(0.036, GD.A2 + 0.03, coat);
  G.thL = seg(0.058, GD.L1 + 0.05, legs); G.thR = seg(0.058, GD.L1 + 0.05, legs); G.shinL = seg(0.046, GD.L2 + 0.03, legs); G.shinR = seg(0.046, GD.L2 + 0.03, legs);
  const bg = bootGeometry(), bh = hullGeom(bg); G.bootL = new THREE.Mesh(bg, boots); G.bootR = new THREE.Mesh(bg, boots);
  const hg = handGeometry(), hh = hullGeom(hg); G.handL = new THREE.Mesh(hg, skin); G.handR = new THREE.Mesh(hg, skin);
  for (const m of [G.bootL, G.bootR, G.handL, G.handR]) { m.castShadow = m.receiveShadow = true; ink(m, 1, PAL.line, m === G.bootL || m === G.bootR ? bh : hh); G.grp.add(m); }
  G.handR.scale.x = -1;  // mirrored right hand
  return G;
}
function placeSeg(m, a, b) { const d = V3().subVectors(b, a); const len = d.length(); m.position.copy(a).addScaledVector(d, 0.5); m.quaternion.setFromUnitVectors(YUP, d.multiplyScalar(1 / Math.max(len, 1e-6))); m.scale.set(1, (len + 0.04) / m.userData.len, 1); }
function ik2(root, target, L1, L2, pole, out) {
  const d = V3().subVectors(target, root); const dist = clamp(d.length(), Math.abs(L1 - L2) + 1e-4, L1 + L2 - 1e-4); const dir = d.normalize();
  const cosA = clamp((L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist), -1, 1); const sinA = Math.sqrt(1 - cosA * cosA);
  const p = pole.clone().addScaledVector(dir, -pole.dot(dir)).normalize();
  out.copy(root).addScaledVector(dir, L1 * cosA).addScaledVector(p, L1 * sinA);
  return root.clone().addScaledVector(dir, dist); // the reachable end point
}
function bootXform(f, outPos, outQuat) {
  const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(f.pitch, f.yaw, 0, 'YXZ'));
  if (f.pivot === 'toe') { const qy = new THREE.Quaternion().setFromAxisAngle(YUP, f.yaw); const toeW = f.sole.clone().add(TOE.clone().sub(SOLE).applyQuaternion(qy)); outPos.copy(toeW).sub(TOE.clone().applyQuaternion(q)); }
  else outPos.copy(f.sole).sub(SOLE.clone().applyQuaternion(q));
  outQuat.copy(q);
}

// ------------------------------------------------------------------ S2 climb: pose as a function of local frame (continuous)
const CL = { crouch: 6, launch: 12, beat: 8 };
function climbPose(fl) {
  const dth = ST.dth, A = 0.75; const P = { blink: 0 };
  let thP, yP, lean, armL, armR, headP, squash = 0, sway = 0, twist = 0, fL, fR;
  if (fl < CL.launch) {
    const look = ease.outCubic(clamp(fl / 4)); const cr = fl < CL.crouch ? 0 : ease.outCubic(clamp((fl - CL.crouch) / 5));
    thP = stepTh(0) - 0.12 * dth * cr; yP = stepY(0) + 0.69 - 0.14 * cr + 0.008 * Math.sin(fl * 0.5);
    lean = 0.08 + 0.48 * cr; armL = armR = 0.12 - 1.02 * cr; headP = -0.12 - 0.42 * look; squash = 0.06 * cr;
    P.elbow = 0.4 + 0.5 * cr; fL = { k: 0 }; fR = { k: 0 };
    if (fl >= 6 && fl < 10) P.blink = fl < 8 ? 0.6 : 1.0;   // decision blink, on 2s: half, closed, open
  } else {
    const fb = fl - CL.launch; const n = Math.floor(fb / CL.beat); const u = (fb - n * CL.beat) / CL.beat; const s = n + u;
    const stanceL = n % 2 === 0;
    if (n === 0) {
      thP = stepTh(0) + dth * lerp(-0.12, 0.6, Math.pow(u, 1.43)); yP = stepY(0) + 0.55 + 0.13 * ease.outCubic(u);
      lean = lerp(0.56, 0.33, ease.outQuad(u)); armL = lerp(-0.9, A, ease.inOutSine(u)); armR = lerp(-0.9, -A, u); squash = lerp(0.06, -0.035, u);
    } else {
      thP = stepTh(0) + (s - 0.4) * dth;
      yP = stepY(n) + 0.5 - 0.035 * Math.sin(Math.PI * Math.min(u / 0.32, 1)) + 0.19 * smoothstep(0.18, 0.82, u);
      lean = 0.3 + 0.07 * Math.sin(Math.PI * Math.min(u / 0.45, 1)); armL = -A * Math.cos(Math.PI * s); armR = -armL;
      squash = u < 0.3 ? 0.05 * Math.sin(Math.PI * u / 0.3) : -0.035 * Math.sin(Math.PI * (u - 0.3) / 0.7);
    }
    headP = -0.3 + 0.05 * Math.cos(2 * Math.PI * u); sway = (stanceL ? 1 : -1) * 0.02; twist = -0.16 * (armL / A);
    P.elbow = null;
    const swingFrom = n === 0 ? 0 : n - 1, swingTo = n + 1; const stance = { k: n };
    let swing;
    if (u < 0.12) swing = { k: swingFrom, pitch: n === 0 ? 0.3 : 0.45 };
    else if (u < 0.88) swing = { air: true, from: swingFrom, to: swingTo, a: (u - 0.12) / 0.76 };
    else swing = { k: swingTo };
    if (stanceL) { fL = stance; fR = swing; } else { fR = stance; fL = swing; }
  }
  Object.assign(P, { thP, yP, lean, armL, armR, headP, squash, sway, twist, fL, fR });
  return P;
}
function climbFoot(spec, side) {
  const r = WALK_R + side * 0.085;
  if (spec.air) {
    const a = spec.a; const th = lerp(stepTh(spec.from), stepTh(spec.to), ease.inOutSine(a));
    const y = lerp(stepY(spec.from), stepY(spec.to), smoothstep(0, 1, a)) + 0.17 * Math.sin(Math.PI * Math.pow(a, 0.85));
    return { sole: V3(r * Math.cos(th), y, r * Math.sin(th)), yaw: -th, pitch: lerp(0.45, -0.18, a), pivot: 'sole', planted: false };
  }
  const th = stepTh(spec.k);
  return { sole: V3(r * Math.cos(th), stepY(spec.k), r * Math.sin(th)), yaw: -th, pitch: spec.pitch || 0, pivot: spec.pitch ? 'toe' : 'sole', planted: true };
}
// pelvis/chest frame for S2 (used for the cape spring + the rig)
function climbFrame(fl) {
  const P = climbPose(fl);
  const pel = V3(WALK_R * Math.cos(P.thP), P.yP, WALK_R * Math.sin(P.thP)).addScaledVector(V3(Math.cos(P.thP), 0, Math.sin(P.thP)), P.sway);
  return { P, pel, yaw: -P.thP };
}

// ------------------------------------------------------------------ S3 lever: keyed poses on 2s (local frames)
const LV_KEYS = [ // fl (S3 local frame, drawings on 2s), lever angle, pelvis fwd, pelvis down, lean, head pitch (+down), brow (−furrow, +raise), mouth open, eye scale
  [0, 0.38, 0.0, 0.0, 0.26, 0.24, 0, 0, 1], [2, 0.38, 0.005, 0.0, 0.27, 0.24, 0, 0, 1],                                    // hold, panting (f140-143)
  [4, 0.41, -0.025, 0.02, 0.2, 0.3, -0.6, 0, 1], [6, 0.45, -0.06, 0.045, 0.11, 0.36, -1, 0, 0.92], [8, 0.47, -0.08, 0.06, 0.06, 0.4, -1, 0, 0.9], // wind-up 6 f (f144-149): coil back
  [10, 0.36, 0.02, 0.035, 0.3, 0.28, -1, 0.2, 0.9], [12, 0.18, 0.05, 0.02, 0.42, 0.22, -1, 0.35, 0.9],                    // push 4 f (f150-153)
  [14, 0.02, 0.07, 0.025, 0.5, 0.36, -1, 0.25, 0.25], [16, 0.06, 0.072, 0.03, 0.49, 0.38, -0.8, 0.1, 0.15],               // CLUNK f154 + squeeze blink
  [18, 0.045, 0.065, 0.02, 0.45, 0.3, -0.5, 0, 0.9], [20, 0.05, 0.06, 0.015, 0.42, 0.2, -0.2, 0, 1], [22, 0.05, 0.057, 0.01, 0.41, 0.14, 0, 0, 1], // follow-through 10 f (f154-163)
  [24, 0.05, 0.057, 0.01, 0.4, 0.14, 0, 0, 1], [26, 0.05, 0.057, 0.01, 0.4, 0.13, 0, 0, 1],                                // held breath (silence f156-167)
  [28, 0.05, 0.045, 0.0, 0.36, 0.04, 1, 0.6, 1.18], [30, 0.05, 0.04, 0.0, 0.34, 0.0, 1, 0.8, 1.15], [32, 0.05, 0.04, 0.0, 0.34, 0.01, 0.9, 0.7, 1.1], // IGNITION f168: eyes wide
  [52, 0.05, 0.038, 0.0, 0.33, 0.04, 0.7, 0.55, 1.08],
];
function leverPose(fl) {
  let i = 0; while (i < LV_KEYS.length - 2 && LV_KEYS[i + 1][0] <= fl) i++;
  const a = LV_KEYS[i], b = LV_KEYS[i + 1]; const k = clamp((fl - a[0]) / (b[0] - a[0]));
  const v = a.map((x, j) => lerp(x, b[j], k));
  const P = { lev: v[1], fwd: v[2], down: v[3], lean: v[4], headP: v[5], brow: v[6], mouth: v[7], eyeS: v[8], blink: 0 };
  P.breath = 0.012 * Math.sin(fl / 24 * Math.PI * 2 * 1.6);              // still panting from the climb
  return P;
}
const S3 = { pel: V3(0.0, GAL_Y + 0.66, 1.0), yaw: Math.PI, footR: V3(0.095, GAL_Y, 0.86), footL: V3(-0.1, GAL_Y, 1.14) };
function leverFrame(fl) { const P = leverPose(fl); const pel = S3.pel.clone(); pel.z -= P.fwd; pel.y -= P.down; return { P, pel, yaw: S3.yaw }; }

// ------------------------------------------------------------------ cape/ponytail spring tables (deterministic, pre-integrated per shot)
function buildSpring(frameFn, f0, f1) {
  const dt = 1 / 96, steps = Math.ceil((f1 - f0) / 24 / dt) + 2; const pos = [], q = [];
  const chestOf = (fl) => { const F = frameFn(fl); const qq = new THREE.Quaternion().setFromEuler(new THREE.Euler(F.P.lean, F.yaw, 0, 'YXZ')); return { p: F.pel.clone().add(V3(0, GD.chestY + 0.2, 0).applyQuaternion(qq)), q: qq }; };
  for (let s = -2; s <= steps + 2; s++) { const c = chestOf((s * dt) * 24); pos.push(c.p); q.push(c.q); }
  const o = V3(), w = V3(), out = [], vel = [];
  for (let s = 0; s <= steps; s++) {
    const i = s + 2; const acc = pos[i + 1].clone().add(pos[i - 1]).addScaledVector(pos[i], -2).multiplyScalar(1 / (dt * dt));
    const v = pos[i + 1].clone().sub(pos[i - 1]).multiplyScalar(1 / (2 * dt));
    const qi = q[i].clone().invert(); acc.applyQuaternion(qi); v.applyQuaternion(qi);
    const f = acc.multiplyScalar(-1).addScaledVector(o, -95).addScaledVector(w, -8.5); f.y -= 0; w.addScaledVector(f, dt); o.addScaledVector(w, dt);
    out.push(o.clone()); vel.push(v);
  }
  return (fl) => { const s = clamp(Math.round(fl / 24 / dt), 0, out.length - 1); return { o: out[s], v: vel[s] }; };
}

// ------------------------------------------------------------------ pose the rig (shared by S2/S3)
const _p = V3(), _q = new THREE.Quaternion(), _k = V3(), _e = V3();
function poseGirl(G, frame, feet, arms, extra) {
  const { P, pel, yaw } = frame;
  G.pelvis.position.copy(pel); G.pelvis.rotation.set(0, yaw + (extra.pelvisYaw || 0), 0);
  G.chest.rotation.set(P.lean, P.twist || 0, 0, 'YXZ');
  const sq = P.squash || 0; G.torso.scale.set(1 + sq * 0.6, 1 - sq + (P.breath || 0), 0.84 * (1 + sq * 0.6));
  G.head.rotation.set((P.headP || 0) - P.lean, extra.headYaw || 0, extra.headRoll || 0, 'YXZ');
  // face
  const bl = P.blink || 0; const es = P.eyeS ?? 1;
  for (const e of G.eyes) e.scale.set(e.userData.base.x, e.userData.base.y * Math.max(0.08, 1 - bl) * es, e.userData.base.z);
  for (const c of G.catches) c.visible = bl < 0.5;
  for (const b of G.brows) { const br = P.brow || 0; b.position.y = 0.043 + 0.008 * br; b.rotation.z = Math.PI / 2 + b.userData.s * (-0.25 * br); }
  G.mouth.scale.set(1.5 - 0.4 * (P.mouth || 0), 0.45 + 1.3 * (P.mouth || 0), 0.5);
  G.grp.updateMatrixWorld(true);
  // legs
  const qy = new THREE.Quaternion().setFromAxisAngle(YUP, yaw);
  for (const [side, f, th, sh, boot] of [[1, feet.L, G.thL, G.shinL, G.bootL], [-1, feet.R, G.thR, G.shinR, G.bootR]]) {
    bootXform(f, _p, _q); boot.position.copy(_p); boot.quaternion.copy(_q);
    const hip = pel.clone().add(V3(side * GD.hipX, GD.hipY, 0).applyQuaternion(qy));
    const pole = V3(0, 0, 1).applyQuaternion(qy).add(V3(side * 0.15, 0, 0).applyQuaternion(qy));
    const end = ik2(hip, _p, GD.L1, GD.L2, pole, _k);
    if (DEBUG && f.planted && end.distanceTo(_p) > 0.002) console.log('reach miss', side, end.distanceTo(_p).toFixed(3));
    placeSeg(th, hip, _k); placeSeg(sh, _k, end);
  }
  // arms
  for (const [side, a, ua, fa, hand, shO] of [[1, arms.L, G.uaL, G.faL, G.handL, G.shL], [-1, arms.R, G.uaR, G.faR, G.handR, G.shR]]) {
    const sh = shO.getWorldPosition(V3());
    hand.position.copy(a.wrist).sub(WRIST.clone().multiply(V3(hand.scale.x, 1, 1)).applyQuaternion(a.q)); hand.quaternion.copy(a.q);
    const end = ik2(sh, a.wrist, GD.A1, GD.A2, a.pole, _e);
    if (DEBUG && a.grip && end.distanceTo(a.wrist) > 0.002) console.log('arm reach miss', side, end.distanceTo(a.wrist).toFixed(3));
    placeSeg(ua, sh, _e); placeSeg(fa, _e, end);
  }
}

// ------------------------------------------------------------------ debug probe (QC only): planted-foot world positions per frame
window.KF_P06 = {
  feet: (i) => { const n = shotOf(i); const tc = ease.hold2s(i / FPS, FPS); const flc = Math.round(tc * FPS) - FB[n]; if (n !== 1) return null;
    const P = climbPose(flc); const out = {}; for (const [k, spec, side] of [['L', P.fL, 1], ['R', P.fR, -1]]) { const f = climbFoot(spec, side); bootXform(f, _p, _q); const toe = _p.clone().add(TOE.clone().applyQuaternion(_q)); out[k] = { planted: f.planted, step: spec.k ?? null, sole: toe.toArray().map((v) => +v.toFixed(5)), heel: +(f.pitch || 0).toFixed(3) }; } return out; },
};
// ------------------------------------------------------------------ boot
let springS2, springS3, T1;
await boot({
  fps: FPS, shots: SHOTS, toneMapping: THREE.NeutralToneMapping, exposure: 1.0,
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; const { renderer } = ctx; renderer.shadowMap.type = THREE.PCFShadowMap;
    scene = new THREE.Scene(); scene.background = new THREE.Color(PAL.skyTop); scene.fog = new THREE.FogExp2(PAL.fog, 0.009);
    camera = new THREE.PerspectiveCamera(40, W / H, 0.03, 2000); rig = new CameraRig(camera);
    sky = makeSky(); scene.add(sky);
    moonDisc = new THREE.Mesh(new THREE.CircleGeometry(15, 48), new THREE.MeshBasicMaterial({ color: PAL.moonDisc, fog: false })); moonDisc.position.copy(C1).addScaledVector(MOON_DIR, 700); moonDisc.lookAt(C1); scene.add(moonDisc);
    clouds = makeClouds(); scene.add(clouds);
    const rocks = []; const world = new THREE.Group(); scene.add(world);
    buildIsland(world, rocks); buildTower(world); buildInterior(world);
    sea = makeSea(maskTexture(rocks)); scene.add(sea);
    rain = makeRain(4000, 77); scene.add(rain);
    girl = makeGirl(); scene.add(girl.grp);
    // lights: neutral hemisphere (lights the designed shadow colours), cool moon key/rim, lightning, lamp, beam spot
    hemi = new THREE.HemisphereLight(PAL.hemiSky, PAL.hemiGnd, 2.4); scene.add(hemi);
    key = new THREE.DirectionalLight(PAL.moon, 2.6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0008; key.shadow.normalBias = 0.045; key.shadow.radius = 1.2; scene.add(key, key.target);
    flashL = new THREE.DirectionalLight(0xdfe8ff, 0); scene.add(flashL, flashL.target);
    lampPt = new THREE.PointLight(PAL.lamp, 0, 4.5, 0.5); lampPt.position.copy(LAMP_C); scene.add(lampPt);
    beamSpot = new THREE.SpotLight(PAL.beam, 0, 160, 0.09, 0.4, 1.2); beamSpot.position.copy(LAMP_C); scene.add(beamSpot, beamSpot.target);
    // S1 camera: on the waterline 20.5 m out on the side away from the moon, low, 22 mm; tower on the right third
    const T0 = V3(0, 12.3, 0); const f1 = T0.clone().sub(C1).normalize(); const r1 = f1.clone().cross(YUP).normalize(); T1 = T0.clone().addScaledVector(r1, -5.0);
    const fH = V3(f1.x, 0, f1.z).normalize(), u1 = YUP;
    const at = (d, x, y) => C1.clone().addScaledVector(fH, d).addScaledVector(r1, x).addScaledVector(u1, y);
    bolts.push(makeBolt(11, at(175, 82, 74), C1, 76, 1.3)); bolts.push(makeBolt(23, at(165, -96, 58), C1, 60, 1.0)); bolts.forEach((b) => scene.add(b));
    const toCam = V3(C1.x, 0, C1.z).normalize(), side = V3(-toCam.z, 0, toCam.x);
    sprays.push(makeSpray(5, 64, 0.8)); sprays[0].position.copy(toCam.clone().multiplyScalar(6.6).addScaledVector(r1, 2.4)).setY(0.2);
    sprays.push(makeSpray(9, 44, 0.65)); sprays[1].position.copy(toCam.clone().multiplyScalar(6.4).addScaledVector(r1, -3.6)).setY(0.2); sprays.forEach((s) => scene.add(s));
    // S1 foreground rock (lower right of frame) for depth
    const fgRock = mk(new THREE.DodecahedronGeometry(2.1, 0), toon(PAL.rock), { cast: true, recv: true, line: 1.0 }); fgRock.position.copy(at(4.6, 3.3, -2.3)); fgRock.scale.set(1.3, 0.9, 1); fgRock.rotation.set(0.4, 1.1, 0.2); scene.add(fgRock); EXT.push(fgRock);
    // the beams: kit lightShaft (length 60) with an end fade patched into this instance (no visible cone caps)
    for (let k = 0; k < 2; k++) {
      const b = lightShaft({ length: 60, radiusTop: 0.28, radiusBottom: 4.4, color: PAL.beam, intensity: 0 });
      b.material.fragmentShader = b.material.fragmentShader.replace('float a=(1.0-along*0.8);', 'float a=(1.0-along*0.8)*(1.0-smoothstep(0.45,1.0,along));');
      b.position.copy(LAMP_C); b.renderOrder = 4; b.visible = false; scene.add(b); beams.push(b);
    }
    const gc = document.createElement('canvas'); gc.width = gc.height = 256; const gg = gc.getContext('2d'); const rgd = gg.createRadialGradient(128, 128, 0, 128, 128, 128);
    rgd.addColorStop(0, 'rgba(255,244,220,1)'); rgd.addColorStop(0.08, 'rgba(255,220,160,0.7)'); rgd.addColorStop(0.3, 'rgba(255,175,95,0.12)'); rgd.addColorStop(1, 'rgba(0,0,0,0)'); gg.fillStyle = rgd; gg.fillRect(0, 0, 256, 256);
    gg.globalCompositeOperation = 'lighter'; for (const [w, h, a] of [[256, 5, 0.85], [5, 120, 0.4]]) { gg.fillStyle = `rgba(255,226,180,${a})`; gg.beginPath(); gg.ellipse(128, 128, w / 2, h / 2, 0, 0, Math.PI * 2); gg.fill(); }
    const gtex = new THREE.CanvasTexture(gc); gtex.colorSpace = THREE.SRGBColorSpace;
    glare = new THREE.Sprite(new THREE.SpriteMaterial({ map: gtex, blending: THREE.AdditiveBlending, depthTest: false, depthWrite: false, transparent: true, fog: false })); glare.position.copy(LAMP_C); glare.renderOrder = 20; glare.visible = false; scene.add(glare);
    springS2 = buildSpring(climbFrame, 0, 72); springS3 = buildSpring(leverFrame, 0, 56);
    post = makeComposer(renderer, scene, camera, { bloom: { strength: 0.9, radius: 0.35, threshold: 0.6 }, grade: 'cel', overlay: false,
      finish: { shadowTint: [0.0, 0.02, 0.08], grain: 0.03, vignette: 0.2, halation: 0.0 } });
  },
  render: async (ctx, i, t) => {
    const n = shotOf(i), fl = i - FB[n];                     // shot index, local frame
    const tc = ease.hold2s(t, FPS); const flc = Math.round(tc * FPS) - FB[n];   // character drawings on 2s
    U.time.value = t;
    // ---------- visibility per shot
    for (const o of EXT) o.visible = n === 0 || n === 3;
    for (const o of INT) o.visible = n === 1;
    for (const h of LANTERN_EXT) if (h) h.visible = n !== 2;
    girl.grp.visible = n === 1 || n === 2;
    sprays.forEach((s) => (s.visible = n === 0)); beams.forEach((b) => (b.visible = n === 3)); glare.visible = n === 3;
    // ---------- lightning (2 frames each, picture + light + sky on the same frame as the thunder)
    let flash = 0; bolts.forEach((b) => (b.visible = false));
    if (i === EV.flash1 || i === EV.flash1 + 1) { flash = i === EV.flash1 ? 1 : 0.55; bolts[0].visible = true; }
    if (i === EV.flash2 || i === EV.flash2 + 1) { flash = i === EV.flash2 ? 0.85 : 0.45; bolts[1].visible = i === EV.flash2; }
    U.flash.value = flash * 0.42;
    // ---------- lamp state
    const lit = i >= EV.ignite ? 1 : 0; const sinceIg = (i - EV.ignite) / FPS;
    const flare = lit ? 1 + 0.75 * Math.exp(-sinceIg * 7) : 0; const flick = 1 + 0.05 * noise1(t * 9, 4);
    lamp.userData.burner.material.color.setRGB(lit ? 9 * flare * flick : 0.02, lit ? 6.2 * flare * flick : 0.02, lit ? 2.6 * flare : 0.03);
    lamp.userData.lensMat.emissive.setRGB(lit ? 0.75 * flare : 0, lit ? 0.42 * flare : 0, lit ? 0.12 * flare : 0);
    const glow = lit && n === 3 ? 1 : 0; lamp.userData.glassMat.emissive.setRGB(0.42 * glow, 0.24 * glow, 0.06 * glow);   // lantern glass glows only seen from outside
    // ---------- per-shot camera, lights, rain box, sea centre
    const f = post.finish; f.exposure.value = 1.0;
    let mm = 35; hemi.intensity = 2.4; key.intensity = 2.6; key.color.set(PAL.moon); flashL.intensity = 0; lampPt.intensity = 0; beamSpot.intensity = 0;
    rain.material.uniforms.uBeamOn.value = 0; rain.visible = true; scene.fog.density = 0.009; scene.fog.color.set(PAL.fog); rain.material.uniforms.uOpacity.value = 0.42; post.bloom.strength = 0.9;
    lamp.userData.glassMat.opacity = 0.42;
    const setKey = (from, target, half, near, far) => { key.position.copy(target).addScaledVector(from, (near + far) / 2); key.target.position.copy(target); const c = key.shadow.camera; c.left = c.bottom = -half; c.right = c.top = half; c.near = near; c.far = far; c.updateProjectionMatrix(); };
    if (n === 0) {
      mm = 20; rig.set({ pos: C1.toArray(), look: T1.toArray(), mm });                       // locked-off, low: authority/dread
      setKey(MOON_DIR, V3(0, 8, 0), 20, 1, 90);
      if (flash > 0) { flashL.intensity = 4.0 * flash; flashL.position.copy(i < 40 ? bolts[0].position : bolts[1].position); flashL.target.position.set(0, 8, 0); }
      sprays[0].update(ease.hold2s(t) - EV.crash1 / FPS); sprays[1].update(ease.hold2s(t) - EV.crash2 / FPS);
    } else if (n === 1) {
      // crane + pan across the open well, following her (camera on 1s, she is on 2s). Holds through her look-up and
      // crouch, reacts one drawing after the launch, eases into her pace; she out-runs it at the end (exit = cut point).
      const x = Math.max(0, (fl - 13) / CL.beat); const prog = x - (1 - Math.exp(-x * 1.4)) / 1.4;
      const thH = stepTh(0) + (prog - 0.1) * ST.dth, yH = stepY(0) + 0.69 + prog * ST.rise;
      const thC = thH + 1.3; mm = 30;               // ahead of her over the treads she is about to climb, above: she runs up toward us
      rig.pos.set(1.0 * Math.cos(thC), yH + 1.15 + 0.08 * prog, 1.0 * Math.sin(thC));
      const thL = thH + 0.12; rig.target.set(WALK_R * Math.cos(thL), yH + 0.14, WALK_R * Math.sin(thL)); rig.lens(mm);
      hemi.intensity = 2.7; key.intensity = 3.2; scene.fog.density = 0.15; scene.fog.color.set(0x0b0d26); rain.material.uniforms.uOpacity.value = 0.8;
      const mid = climbFrame(40).pel.clone().add(V3(0, 0.55, 0)); const wc = V3(R_IN * Math.cos(MOONWIN.th), MOONWIN.y, R_IN * Math.sin(MOONWIN.th));
      const dir = wc.clone().sub(mid).normalize(); setKey(dir, mid, 3.2, 0.3, 14);
    } else if (n === 2) {
      mm = 55; rig.set({ pos: [1.1, GAL_Y + 0.78, -0.9], look: [-0.2, GAL_Y + 1.02, 0.58], mm });   // behind-beside the lamp: lens FG, hands MG, face BG
      hemi.intensity = 1.6 + 0.4 * lit; key.intensity = lit ? 2.2 : 3.6; scene.fog.density = 0.004;
      setKey(V3(-0.75, 0.55, 0.6).normalize(), V3(0, GAL_Y + 0.9, 0.9), 1.6, 0.3, 10);              // moon rim from behind her
      if (lit) lampPt.intensity = 2.8 * (1 + 0.25 * (flare - 1)) * flick;   // the burner/lens carry the flare; her face keeps its features
    } else {
      mm = 30; const bob = Math.sin(t * 1.3) * 0.12, roll = Math.sin(t * 0.9 + 1) * 0.008;     // floating on the swell
      rig.set({ pos: [-15.5, 2.5 + bob, -41.0], look: [-2.6, 12.4 + bob * 0.3, 0], mm }); rig.roll = roll;
      setKey(MOON_DIR, V3(0, 8, 0), 20, 1, 90); lampPt.intensity = 7 * flick;
    }
    AMBK.value = hemi.intensity / Math.PI * 0.92;
    rig.apply(); rig.roll = 0;
    camera.updateMatrixWorld();
    // ink width: LINE_PX at 720p, constant in pixels at any resolution
    OW.value = (LINE_PX / 720) * 2 * Math.tan(camera.fov * DEG / 2);
    // rain box follows the camera (world-anchored drops), sea grid centred under the camera
    const fwd = camera.getWorldDirection(V3()); const rc = camera.position.clone().addScaledVector(fwd, 13); const ru0 = rain.material.uniforms;
    if (n === 1) { // inside: concentrate the drops just outside the two slits behind her so rain reads through the openings
      const w1 = WINDOWS[3], w2 = WINDOWS[4]; const c = V3(2.9 * (Math.cos(w1.th) + Math.cos(w2.th)) / 2, (w1.y + w2.y) / 2, 2.9 * (Math.sin(w1.th) + Math.sin(w2.th)) / 2);
      ru0.uBoxSize.value.set(8, 8, 8); ru0.uBoxMin.value.copy(c).sub(V3(4, 4, 4));
    } else { ru0.uBoxSize.value.set(36, 30, 36); ru0.uBoxMin.value.copy(rc).sub(V3(18, 15, 18)); } rain.material.uniforms.uWidthPx.value = (0.9 / 720) * 2 * Math.tan(camera.fov * DEG / 2);
    sea.position.set(Math.round(camera.position.x), 0, Math.round(camera.position.z)); seaMat.userData.u.uOff.value.set(sea.position.x, sea.position.z);
    sky.position.copy(camera.position);
    // ---------- the beam (S4): rotates with the lens; passes over the camera at EV.pass
    if (n === 3) {
      const camAz = Math.atan2(camera.position.z - LAMP_C.z, camera.position.x - LAMP_C.x); const omega = 70 * DEG;
      const az = camAz + omega * (t - EV.pass / FPS); const tilt = 6 * DEG; const half = Math.atan(4.4 / 60);
      const dirs = [0, Math.PI].map((o) => V3(Math.cos(tilt) * Math.cos(az + o), -Math.sin(tilt), Math.cos(tilt) * Math.sin(az + o)));
      beams.forEach((b, k) => { b.quaternion.setFromUnitVectors(V3(0, -1, 0), dirs[k]); b.material.uniforms.uIntensity.value = 2.2; b.update(t); });
      const toCamH = camera.position.clone().sub(LAMP_C).setY(0).normalize(); const dH = dirs[0].clone().setY(0).normalize(); const align = Math.max(0, dH.dot(toCamH));
      const g = Math.pow(smoothstep(Math.cos(half * 2.0), 1.0, align), 1.5);
      glare.scale.setScalar(2.2 + 16 * g); glare.material.opacity = 0.4 + 0.6 * g; f.exposure.value = 1 + 0.45 * g;
      beamSpot.intensity = 9000; beamSpot.target.position.copy(LAMP_C).addScaledVector(dirs[0], 50);
      const ru = rain.material.uniforms; ru.uBeamOn.value = 1; ru.uBeamDir0.value.copy(dirs[0]); ru.uBeamDir1.value.copy(dirs[1]); ru.uBeamCos.value = Math.cos(half);
    }
    // ---------- the girl
    if (n === 1) {
      const F = climbFrame(flc); const P = F.P;
      const feet = { L: climbFoot(P.fL, 1), R: climbFoot(P.fR, -1) };
      // planted feet are law: lower the pelvis if a planted leg cannot reach (no slide, ever)
      const qy = new THREE.Quaternion().setFromAxisAngle(YUP, F.yaw); let drop = 0;
      for (const [side, ft] of [[1, feet.L], [-1, feet.R]]) { if (!ft.planted) continue; bootXform(ft, _p, _q); const hip = F.pel.clone().add(V3(side * GD.hipX, GD.hipY, 0).applyQuaternion(qy)); const h2 = hip.x - _p.x, d2 = hip.z - _p.z; const maxL = GD.L1 + GD.L2 - 0.006; const hz = Math.sqrt(Math.max(0, maxL * maxL - h2 * h2 - d2 * d2)); drop = Math.max(drop, (hip.y - _p.y) - hz); }
      F.pel.y -= Math.max(0, drop);
      // arms: pumping FK in the chest frame (on 2s)
      girl.pelvis.position.copy(F.pel); girl.pelvis.rotation.set(0, F.yaw, 0); girl.chest.rotation.set(P.lean, P.twist, 0, 'YXZ'); girl.grp.updateMatrixWorld(true);
      const arm = (side, sw) => { const sh = (side > 0 ? girl.shL : girl.shR).position.clone(); const elbow = P.elbow ?? (1.2 + 0.35 * Math.max(0, sw / 0.75));
        const up = V3(side * 0.12, -Math.cos(sw), Math.sin(sw)).normalize(); const fo = V3(side * 0.05, -Math.cos(sw + elbow), Math.sin(sw + elbow)).normalize();
        const wristL = sh.clone().addScaledVector(up, GD.A1).addScaledVector(fo, GD.A2); const wrist = girl.chest.localToWorld(wristL.clone());
        const cq = girl.chest.getWorldQuaternion(new THREE.Quaternion()); const z = fo.clone().negate().applyQuaternion(cq); const x = V3(1, 0, 0).applyQuaternion(cq); const y = z.clone().cross(x).normalize(); x.copy(y).cross(z).normalize();
        const q = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
        const pole = V3(side * 0.3, -0.2, -1).applyQuaternion(cq); return { wrist, q, pole }; };
      const sp = springS2(flc - 3);                         // cape lags the body by 3 frames
      const drag = sp.o.clone().multiplyScalar(2.2).addScaledVector(sp.v, -0.09); drag.y = clamp(drag.y + Math.abs(drag.z) * 0.15, -0.1, 0.05); drag.z = clamp(drag.z, -0.2, 0.05); drag.x = clamp(drag.x, -0.08, 0.08);
      girl.cape.update(drag, tc, 0.012);
      girl.tail.rotation.set(clamp(-sp.v.z * 0.35 - sp.o.z * 4, -0.2, 1.1), 0, clamp(sp.o.x * 4, -0.4, 0.4));
      girl.catchMat.color.setRGB(0.55, 0.62, 0.85);
      poseGirl(girl, F, feet, { L: arm(1, P.armL), R: arm(-1, P.armR) }, { headYaw: -0.12 });
    } else if (n === 2) {
      const F = leverFrame(flc); const P = F.P;
      lever.rotation.x = P.lev; lever.updateMatrixWorld(true);
      const nudge = flc >= EV.clunk - FB[2] && flc < EV.clunk - FB[2] + 4 ? (flc < EV.clunk - FB[2] + 2 ? 0.006 : -0.003) : 0;   // impact nudge on the clunk (2 drawings)
      camera.position.y += nudge; camera.updateMatrixWorld();
      const hq = lever.userData.handle.getWorldQuaternion(new THREE.Quaternion()).multiply(new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), -0.55));
      const grip = (x) => { const c = lever.userData.handle.localToWorld(V3(x, 0, 0)); return { wrist: c.clone().add(WRIST.clone().applyQuaternion(hq)), q: hq.clone(), pole: V3(Math.sign(x) * 0.8, -1, 0.3), grip: true }; };
      const feet = { L: { sole: S3.footL, yaw: S3.yaw, pitch: 0, pivot: 'sole', planted: true }, R: { sole: S3.footR, yaw: S3.yaw, pitch: 0, pivot: 'sole', planted: true } };
      const sp = springS3(flc - 3);
      const drag = sp.o.clone().multiplyScalar(2.5).addScaledVector(sp.v, -0.11); drag.y = clamp(drag.y + Math.abs(drag.z) * 0.5, -0.12, 0.2); drag.z = clamp(drag.z, -0.3, 0.12); drag.x = clamp(drag.x, -0.1, 0.1);
      girl.cape.update(drag, tc, 0.008);
      girl.tail.rotation.set(clamp(-sp.v.z * 0.35 - sp.o.z * 4, -0.3, 0.9), 0, 0);
      girl.catchMat.color.setRGB(lit ? 1.0 : 0.5, lit ? 0.85 : 0.56, lit ? 0.55 : 0.8);
      poseGirl(girl, F, feet, { L: grip(-0.065), R: grip(0.065) }, { headYaw: 0.05 });
    }
    post.render(t);
  },
});
