// P12 "TERRAIN" — a cinematic map explainer in 10 s. A 3D relief that reads as an engraved, hand-painted map lit by a low warm sun;
// a dashed ink route is drawn across it by an unseen pen; the camera follows the pen down into the pass; the trail ends at a black tarn.
// Lane: edutainment. Look: parchment + sage/ochre washes, engraved contours, the one saturated accent is the route's ink (#7a1f1f).
import * as THREE from 'three';
import { boot, CameraRig, makeComposer, dustPoints, drawText, ease, smoothstep, clamp, lerp } from '/harness/kit/film.js';
import { WORLD } from './terrain.js';
import { sunVector } from './bake.js';
import { buildWorld } from './world.js';
import * as TM from './timing.js';
import { POSE, kS2 } from './camera.js';
import { INK, makeTerrainMaterial, makeRibbonGeometry, makeRouteMaterial, makeRiverMaterial, makeSky, noiseTexture, paperTexture, terrainGeometry } from './materials.js';

const SHOTS = [
  { name: 'S1 top-down, the pen starts at Camp II', dur: TM.SHOT_DUR[0], mm: 35 },
  { name: 'S2 tilt + descend following the pen', dur: TM.SHOT_DUR[1], mm: 35 },
  { name: 'S3 low oblique, the trail ends at the tarn', dur: TM.SHOT_DUR[2], mm: 28 },
];
const CAP1 = 'They left Camp II on the ninth of October.', CAP2 = 'The trail ends here.';
const CREAM = '#f4e9cc', OUTLINE = 'rgba(34,20,11,0.93)';

let scene, camera, rig, post, W, H, world, terrainMat, routeMat, riverMat, sky, dust, labels, anchors, curMS = 4, msaaFixed = false;
const q = new URLSearchParams(location.search);
const v3 = (a) => new THREE.Vector3(a[0], a[1], a[2]);

await boot({
  fps: 24, shots: SHOTS, fonts: [['Cinzel', 600]], toneMapping: THREE.NeutralToneMapping, exposure: 1.0,
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; const { renderer } = ctx; const T0 = performance.now(); const lap = (m) => { if (q.get('dbg')) console.log('[init]', m, ((performance.now() - T0) / 1000).toFixed(2) + 's'); };
    await document.fonts.load('italic 500 20px "Cormorant Garamond"'); // kit limitation: loadFonts() cannot request an italic face
    world = buildWorld({ res: 1.0 }); lap('world (terrain+erosion+route+bake+upsample)');
    const { T, route, river, map } = world;
    // ---- textures
    const mapTex = new THREE.DataTexture(map.data, map.nx, map.nz, THREE.RGBAFormat, THREE.FloatType);
    mapTex.minFilter = mapTex.magFilter = THREE.LinearFilter; mapTex.wrapS = mapTex.wrapT = THREE.ClampToEdgeWrapping; mapTex.generateMipmaps = false; mapTex.needsUpdate = true;
    const mesh = terrainGeometry(WORLD, world.hAt, 1.25);
    const meshTex = new THREE.DataTexture(mesh.heights, mesh.gx + 1, mesh.gz + 1, THREE.RedFormat, THREE.FloatType);
    meshTex.minFilter = meshTex.magFilter = THREE.NearestFilter; meshTex.wrapS = meshTex.wrapT = THREE.ClampToEdgeWrapping; meshTex.generateMipmaps = false; meshTex.needsUpdate = true;
    const paper = paperTexture(1024, 2024); lap('paper');
    const shared = {
      uNoise: { value: noiseTexture(11) }, uPaper: { value: paper }, uMap: { value: mapTex }, uMesh: { value: meshTex },
      uMapOrg: { value: new THREE.Vector4(map.x0 - 0.5 * map.res, map.z0 - 0.5 * map.res, 1 / (map.res * map.nx), 1 / (map.res * map.nz)) },
      uMeshOrg: { value: new THREE.Vector4(WORLD.x0, WORLD.z0, 1 / mesh.step, 0) },
      uFogCol: { value: new THREE.Color() }, uFog: { value: new THREE.Vector4(0.012, 0.028, 150, 235) },
      uSunCol: { value: new THREE.Color() }, uSkyCol: { value: new THREE.Color() }, uBounce: { value: new THREE.Color() }, uInkCol: { value: new THREE.Color() }, uRouteCol: { value: INK.col.clone() },
    };
    // ---- scene
    scene = new THREE.Scene(); scene.background = new THREE.Color(0xd9c9a8);
    camera = new THREE.PerspectiveCamera(35, W / H, 1.5, 3000); rig = new CameraRig(camera);
    terrainMat = makeTerrainMaterial(shared); const terrain = new THREE.Mesh(mesh.geometry, terrainMat); terrain.frustumCulled = false; scene.add(terrain);
    riverMat = makeRiverMaterial(shared); const riverMesh = new THREE.Mesh(makeRibbonGeometry(river, (s) => 0.42 + 0.40 * s / river.L), riverMat); riverMesh.frustumCulled = false; riverMesh.renderOrder = 1; scene.add(riverMesh);
    routeMat = makeRouteMaterial(shared, route.L); const routeMesh = new THREE.Mesh(makeRibbonGeometry(route, () => 0.90), routeMat); routeMesh.frustumCulled = false; routeMesh.renderOrder = 2; scene.add(routeMesh);
    if (q.get('lift')) { routeMat.uniforms.uLift.value = +q.get('lift'); riverMat.uniforms.uLift.value = +q.get('lift'); }
    sky = makeSky(shared); scene.add(sky);
    const sv = sunVector(T.layout.sun.azimuthDeg, T.layout.sun.elevationDeg); sky.material.uniforms.uSunDir.value.set(sv[0], sv[1], sv[2]);
    dust = dustPoints({ count: 700, box: [200, 150, 260], center: [-20, 85, -100], size: 0.30, color: 0xfff1d6, opacity: 0.0, drift: 0.8, wind: [0.25, 0.04, 0.1], seed: 12 }); dust.frustumCulled = false; scene.add(dust);
    // ---- anchors for the projected labels (3D points on the map)
    const camp = T.camp, tarn = [T.lake.cx, T.sample(T.lake.cx, T.lake.cz), T.lake.cz], sad = T.saddle, end = route.at(route.L);
    anchors = { camp: [camp[0], T.sample(camp[0], camp[1]), camp[1]], tarn: [tarn[0], tarn[1], tarn[2]], saddle: [sad[0], T.sample(sad[0], sad[1]) + 3, sad[1]], end };
    labels = [
      { text: 'CAMP II', a: anchors.camp, pop: TM.TIMES.campPop, mode: 'above', lift: 26 },
      { text: 'THE BLACK TARN', a: anchors.tarn, pop: TM.TIMES.tarnPop, mode: 'on', lift: 0 },
      { text: 'THE SADDLE', a: anchors.saddle, pop: TM.TIMES.saddlePop, mode: 'above', lift: 24 },
    ];
    terrainMat.uniforms.uCamp.value.set(camp[0], camp[1], 1.7, 0); terrainMat.uniforms.uMark.value.set(end[0], end[2], -1, 4.6);
    // ---- post: sepia, tuned (the brief: saturation 0.55, warm highlight tint, slightly blue shadow tint, grain 0.04, vignette 0.4, no letterbox)
    post = makeComposer(renderer, scene, camera, { grade: 'sepia', finish: { saturation: 0.55, contrast: 1.12, shadowTint: [-0.012, 0.0, 0.03], highlightTint: [0.04, 0.026, 0.0], halation: 0, grain: 0.04, grainSize: 1.4, vignette: 0.4, letterbox: 0 } });
    msaaFixed = q.get('msaa') !== null; curMS = msaaFixed ? +q.get('msaa') : 4; setMSAA(curMS); // kit bug workaround: composer targets have no MSAA by default (the skyline aliases)
    lap('scene built');
  },
  render: async (ctx, i, t) => {
    const sh = ctx.timeline.at(t); const n = sh.i, u = sh.u; const { T, route } = world;
    // --- camera: S1 locked-off (the only motion is ink), S2 one eased move (rest -> rest), S3 locked-off
    const camq = q.get('cam');
    if (camq) { const p = camq.split(',').map(Number); rig.set({ pos: p.slice(0, 3), look: p.slice(3, 6), mm: p[6] || 35 }); }
    else if (n === 0) rig.set(POSE.s1); else if (n === 1) rig.move(POSE.s2a, POSE.s2b, u, kS2); else rig.set(POSE.s3);
    rig.apply(); camera.updateMatrixWorld(true);
    if (!msaaFixed) setMSAA(n === 0 || (n === 1 && u < 0.34) ? 0 : 4); // MSAA (a third of the frame cost in SwiftShader) only once there is a skyline / ridge-over-ridge edge: the sheet seen from above has none
    // --- the colour script: warm sun thinning toward the end, haze thickening as we drop into the valley
    const dim = lerp(1.0, 0.84, smoothstep(3.0, 9.0, t)), haze = lerp(0.15, 1.3, smoothstep(3.4, 8.0, t));
    const U = terrainMat.uniforms;
    U.uSunCol.value.setRGB(1.40 * dim, 1.07 * dim, 0.72 * dim); U.uSkyCol.value.setRGB(0.20, 0.25, 0.36); U.uBounce.value.setRGB(0.15, 0.105, 0.065); U.uInkCol.value.setRGB(0.085, 0.052, 0.034);
    U.uFogCol.value.setRGB(0.86, 0.76, 0.62); U.uFog.value.set(0.0035 * haze, 0.028, 185, 275);
    sky.material.uniforms.uHorizon.value.setRGB(0.86, 0.76, 0.62); sky.material.uniforms.uZenith.value.setRGB(0.60, 0.68, 0.80); sky.material.uniforms.uSunGlow.value.setRGB(0.55, 0.32, 0.14);
    // --- the pen, the marker
    routeMat.uniforms.uProgress.value = TM.progress(t) * route.L;
    U.uMark.value.z = t >= TM.TIMES.marker ? t - TM.TIMES.marker : -1; U.uLook.value.w = +(q.get('dbgmode') || 0);
    dust.material.uniforms.uOpacity.value = 0.55 * smoothstep(3.6, 6.5, t); dust.update(t, camera, H);
    // --- overlay: captions + projected labels
    const { ctx: c, clear } = post.overlay; clear();
    drawCaptions(c, t); drawLabels(c, t);
    post.render(t);
  },
});

// composer targets: samples can only change by re-creating the targets (the S1 top-down frames and the first third of the tilt have no silhouettes to anti-alias)
function setMSAA(k) { curMS = k; for (const rt of [post.composer.renderTarget1, post.composer.renderTarget2]) { if (rt.samples !== k) { rt.samples = k; rt.dispose(); } } }

// ------------------------------------------------------------------ overlay helpers
function occlusion(a) { // soft terrain occlusion of an anchor seen from the camera (heightfield march)
  const cp = camera.position; let worst = 0; const N = 36;
  for (let k = 1; k < N - 2; k++) { const f = k / N; const x = cp.x + (a[0] - cp.x) * f, y = cp.y + (a[1] - cp.y) * f, z = cp.z + (a[2] - cp.z) * f; const ex = world.hAt(x, z) - y; if (ex > worst) worst = ex; }
  return 1 - clamp((worst - 0.5) / 3.0);
}
function drawLabels(c, t) {
  const px = Math.round(H * 0.0182); const v = new THREE.Vector3();
  for (const L of labels) {
    const age = t - L.pop; if (age < 0) continue;
    v.set(L.a[0], L.a[1], L.a[2]).project(camera); if (v.z > 1 || v.z < -1) continue;
    const sx = (v.x * 0.5 + 0.5) * W, sy = (0.5 - v.y * 0.5) * H;
    const edge = Math.min(smoothstep(0.0, 0.07, 1 - Math.abs(v.x)), smoothstep(0.0, 0.10, 1 - Math.abs(v.y)));
    const vis = occlusion(L.a);
    const a = smoothstep(0, 0.22, age) * edge * vis; if (a <= 0.01) continue;
    const sc = 0.82 + 0.18 * ease.outBack(clamp(age / 0.34)); // pop: fade + scale with a small overshoot
    c.save(); c.translate(sx, sy - L.lift * sc); c.scale(sc, sc); c.globalAlpha = a;
    c.font = `600 ${px}px "Cinzel"`; c.letterSpacing = Math.round(px * 0.2) + 'px'; c.textAlign = 'center'; c.textBaseline = 'alphabetic'; c.lineJoin = 'round'; c.miterLimit = 2;
    if (L.mode === 'above') { // hairline leader from the label down to the anchor
      c.strokeStyle = OUTLINE; c.lineWidth = 2.4; c.beginPath(); c.moveTo(0, 4); c.lineTo(0, L.lift * 0.62); c.stroke(); c.strokeStyle = CREAM; c.lineWidth = 0.9; c.beginPath(); c.moveTo(0, 4); c.lineTo(0, L.lift * 0.62); c.stroke();
    }
    c.lineWidth = 3.0; c.strokeStyle = OUTLINE; c.strokeText(L.text, 0.5 * px * 0.2, 0); c.fillStyle = CREAM; c.fillText(L.text, 0.5 * px * 0.2, 0);
    c.restore();
  }
}
function drawCaptions(c, t) {
  const caps = [[CAP1, TM.TIMES.cap1[0], TM.TIMES.cap1[1]], [CAP2, TM.TIMES.cap2[0], TM.TIMES.cap2[1]]]; const fs = Math.round(H * 0.056);
  for (const [text, t0, t1] of caps) {
    const a = clamp((t - t0) / 0.5) * (1 - clamp((t - t1) / 0.5)); if (a <= 0) continue;
    const g = c.createLinearGradient(0, H * 0.66, 0, H); g.addColorStop(0, 'rgba(24,14,8,0)'); g.addColorStop(1, `rgba(24,14,8,${0.42 * a})`); c.fillStyle = g; c.fillRect(0, H * 0.66, W, H * 0.34);
    drawText(c, text, { x: W * 0.07, y: H * 0.875, font: `italic 500 ${fs}px "Cormorant Garamond"`, align: 'left', color: CREAM, alpha: a, spacing: 1, shadow: 10, shadowColor: 'rgba(20,10,4,0.95)' });
  }
}
