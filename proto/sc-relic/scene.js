// P05 "RELIC" — game-cinematic trailer grammar in 10 s (cold open → reveal → turn → silence → title → tag).
// Lane: epic cinematic. Look: ember grade, 2.39 scope, volumetric shafts, single accent colour (ember red) reserved for the relic's waking.
import * as THREE from 'three';
import { boot, CameraRig, makeComposer, dustPoints, lightShaft, drawText, env, ease, rng, fbmCanvas, canvasTexture, smoothstep, clamp, lerp, noise1, heightToNormal, blurCanvas } from '/harness/kit/film.js';

const SHOTS = [
  { name: 'S1 cold open ECU runes', dur: 2.2, mm: 100 },
  { name: 'S2 crane reveal wide', dur: 3.0, mm: 24 },
  { name: 'S3 push-in MCU wake', dur: 2.4, mm: 50 },
  { name: 'S4 black silence', dur: 0.5 },
  { name: 'S5 title + tag', dur: 1.9 },
];
let scene, camera, rig, post, dust, embers, shafts = [], monolith, runeMat, runeCanvas, runeCtx, glyphMask, godLight, W, H;
const R = rng(1105);

function glyphCanvas(w = 512, h = 2048, opaque = false) {
  // carved script: angular glyphs in columns, as white strokes (transparent bg for alpha masking, or black bg for height maps)
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  if (opaque) { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); } g.strokeStyle = '#fff'; g.lineCap = 'round'; g.lineJoin = 'round';
  const cols = 3, rows = 26, cw = w / cols, rh = h / rows;
  for (let cx = 0; cx < cols; cx++) for (let ry = 2; ry < rows - 2; ry++) {
    if (R() < 0.12) continue; // gaps
    const x0 = cx * cw + cw * 0.22, y0 = ry * rh + rh * 0.18, gw = cw * 0.56, gh = rh * 0.64; const n = R.int(2, 5);
    g.lineWidth = 7 + R() * 5; g.beginPath();
    for (let k = 0; k < n; k++) { const ax = x0 + R() * gw, ay = y0 + R() * gh, bx = x0 + R() * gw, by = y0 + R() * gh; g.moveTo(ax, ay); g.lineTo(bx, by); if (R() < 0.5) g.lineTo(x0 + R() * gw, y0 + R() * gh); }
    g.stroke(); if (R() < 0.4) { g.beginPath(); g.arc(x0 + R() * gw, y0 + R() * gh, 6 + R() * 8, 0, Math.PI * 2); g.stroke(); }
  }
  return c;
}
function rockTexture(size = 1024, seed = 3) {
  const base = fbmCanvas(size, size, { seed, scale: 6, oct: 7, gain: 0.6, lo: 8, hi: 150, fn: (v) => Math.pow(v, 1.4) });
  const g = base.getContext('2d'); const n = fbmCanvas(size, size, { seed: seed + 9, scale: 24, oct: 3, lo: 0, hi: 255 });
  g.globalAlpha = 0.35; g.globalCompositeOperation = 'multiply'; g.drawImage(n, 0, 0); g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; // fine speckle
  // cracks
  g.strokeStyle = 'rgba(0,0,0,0.55)'; g.lineWidth = 2;
  for (let i = 0; i < 60; i++) { g.beginPath(); let x = R() * size, y = R() * size; g.moveTo(x, y); for (let k = 0; k < 8; k++) { x += (R() - .5) * 120; y += (R() - .5) * 120; g.lineTo(x, y); } g.stroke(); }
  return base;
}
function displacedRock(geom, amp, seed) {
  const p = geom.attributes.position; const r = rng(seed); const n = 1 + Math.floor(p.count / 2000);
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i); const d = amp * (Math.sin(x * 0.9 + seed) * Math.cos(z * 1.3) + 0.5 * Math.sin(y * 2.1 + x * 0.4) + 0.3 * Math.sin(z * 3.7 + y * 1.1)); const len = Math.hypot(x, y, z) || 1; p.setXYZ(i, x + d * x / len, y + d * y / len, z + d * z / len); }
  geom.computeVertexNormals(); return geom;
}

await boot({
  fps: 24, shots: SHOTS, fonts: [['Cinzel', 400], ['Cinzel', 700], ['Cormorant Garamond', 400]],
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; const { renderer } = ctx;
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x030304); scene.fog = new THREE.FogExp2(0x06050b, 0.022);
    camera = new THREE.PerspectiveCamera(30, W / H, 0.05, 200); rig = new CameraRig(camera);
    const rockTex = canvasTexture(rockTexture(1024, 3), { repeat: 3 }); const rockBump = canvasTexture(fbmCanvas(512, 512, { seed: 5, scale: 10, oct: 5 }), { srgb: false, repeat: 3 });
    const rockMat = new THREE.MeshStandardMaterial({ map: rockTex, bumpMap: rockBump, bumpScale: 0.35, color: 0x6e5f52, roughness: 1.0, metalness: 0.0 });
    // cavern: a big displaced sphere seen from inside
    const cavMat = new THREE.MeshStandardMaterial({ map: canvasTexture(rockTexture(1024, 3), { repeat: 8 }), color: 0xcdbba8, roughness: 1.0, side: THREE.BackSide }); const cav = new THREE.Mesh(displacedRock(new THREE.SphereGeometry(26, 96, 64), 2.2, 11), cavMat); cav.position.y = 8; scene.add(cav);
    // floor: rubble field
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80, 80, 80), rockMat); floor.rotation.x = -Math.PI / 2; const fp = floor.geometry.attributes.position; for (let i = 0; i < fp.count; i++) { const x = fp.getX(i), y = fp.getY(i); fp.setZ(i, 0.35 * Math.sin(x * 0.7) * Math.cos(y * 0.9) + 0.15 * Math.sin(x * 2.3 + y * 1.7)); } floor.geometry.computeVertexNormals(); floor.receiveShadow = true; scene.add(floor);
    const rubbleMat = rockMat.clone(); rubbleMat.color.set(0x6a5c4e);
    for (let i = 0; i < 70; i++) { const s = 0.15 + R() * 0.9; const m = new THREE.Mesh(displacedRock(new THREE.DodecahedronGeometry(s, 1), s * 0.25, i), rubbleMat); const a = R() * Math.PI * 2, d = 1.4 + R() * 9; m.position.set(Math.cos(a) * d, s * 0.35, Math.sin(a) * d); m.rotation.set(R() * 6, R() * 6, R() * 6); m.castShadow = m.receiveShadow = true; scene.add(m); }
    // broken columns for scale
    for (let i = 0; i < 5; i++) { const h = 3 + R() * 5; const col = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.6, h, 10), rubbleMat); const a = 0.6 + i * 1.1; col.position.set(Math.cos(a) * 9, h / 2 - 0.2, Math.sin(a) * 9 - 2); col.rotation.z = (R() - .5) * 0.15; col.castShadow = true; scene.add(col); }
    // the relic monolith with carved runes (emissive reveal animated per frame)
    const seedState = R(); // keep RNG stream stable
    glyphMask = glyphCanvas(512, 2048, false); const R2 = rng(1105); // same glyph layout for the opaque copy
    const glyphBlack = (() => { const c = document.createElement('canvas'); c.width = 512; c.height = 2048; const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, 512, 2048); g.drawImage(glyphMask, 0, 0); return c; })();
    runeCanvas = document.createElement('canvas'); runeCanvas.width = 512; runeCanvas.height = 2048; runeCtx = runeCanvas.getContext('2d');
    const emis = new THREE.CanvasTexture(runeCanvas); emis.colorSpace = THREE.SRGBColorSpace;
    // stone colour with the grooves darkened, plus a carved normal map (grooves soft-edged) over fine rock grain
    const mt = document.createElement('canvas'); mt.width = 512; mt.height = 2048; const mg = mt.getContext('2d'); const rt = rockTexture(512, 21); for (let k = 0; k < 4; k++) mg.drawImage(rt, 0, k * 512);
    mg.globalAlpha = 0.8; mg.globalCompositeOperation = 'multiply'; mg.drawImage(glyphBlack, 0, 0); mg.globalCompositeOperation = 'source-over'; mg.globalAlpha = 1; // grooves go dark
    const invG = document.createElement('canvas'); invG.width = 512; invG.height = 2048; const ig = invG.getContext('2d'); ig.fillStyle = '#fff'; ig.fillRect(0, 0, 512, 2048); ig.globalCompositeOperation = 'difference'; ig.drawImage(glyphBlack, 0, 0); ig.globalCompositeOperation = 'source-over';
    mg.globalAlpha = 0.45; mg.drawImage(invG, 0, 0); mg.globalAlpha = 1; // lift the stone around the grooves slightly
    const heightC = blurCanvas(invG, 2); const hg = heightC.getContext('2d'); hg.globalAlpha = 0.3; hg.drawImage(fbmCanvas(512, 512, { seed: 31, scale: 14, oct: 5 }), 0, 0, 512, 2048); // grain in the height
    const normalTex = new THREE.CanvasTexture(heightToNormal(heightC, 3.2)); normalTex.colorSpace = THREE.NoColorSpace;
    runeMat = new THREE.MeshStandardMaterial({ map: canvasTexture(mt, { wrap: false }), normalMap: normalTex, normalScale: new THREE.Vector2(1.2, 1.2), roughness: 0.95, color: 0x6a6058, emissive: 0xff3a10, emissiveMap: emis, emissiveIntensity: 0 });
    monolith = new THREE.Mesh(new THREE.BoxGeometry(1.4, 7, 0.7, 1, 1, 1), [rubbleMat, rubbleMat, rubbleMat, rubbleMat, runeMat, runeMat]); monolith.position.y = 3.5; monolith.rotation.y = 0.22; monolith.castShadow = monolith.receiveShadow = true; scene.add(monolith);
    // a lone pilgrim for scale (silhouette, rim-lit), facing the relic
    const silk = new THREE.MeshStandardMaterial({ color: 0x15110f, roughness: 0.95 });
    const pilgrim = new THREE.Group(); const cloak = new THREE.Mesh(new THREE.ConeGeometry(0.42, 1.55, 14), silk); cloak.position.y = 0.78; const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.5, 4, 10), silk); torso.position.y = 1.35; const head = new THREE.Mesh(new THREE.SphereGeometry(0.14, 12, 10), silk); head.position.y = 1.72; const hood = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.35, 10), silk); hood.position.y = 1.78; const staff = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.025, 2.0, 6), silk); staff.position.set(0.3, 1.0, 0.05);
    pilgrim.add(cloak, torso, head, hood, staff); pilgrim.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; }); pilgrim.position.set(0.9, 0.05, 3.4); pilgrim.lookAt(0, 0.05, 0); scene.add(pilgrim); window._pilgrim = pilgrim;
    // lights: god light from above (motivated: a crack in the cavern roof), cool rim from the left, no fill (8:1+)
    godLight = new THREE.SpotLight(0xffe2b8, 2400, 70, 0.42, 0.85, 1.4); godLight.position.set(3, 24, 6); godLight.target.position.set(0, 2, 0); godLight.castShadow = true; godLight.shadow.mapSize.set(2048, 2048); godLight.shadow.bias = -0.0008; godLight.shadow.radius = 6; scene.add(godLight, godLight.target);
    const rim = new THREE.DirectionalLight(0x8fa4d8, 2.4); rim.position.set(-6, 7, -9); scene.add(rim); const rim2 = new THREE.SpotLight(0xc9d6ff, 900, 30, 0.6, 0.7, 1.4); rim2.position.set(-3, 9, -6); rim2.target.position.set(0.9, 1, 3.4); scene.add(rim2, rim2.target);
    scene.add(new THREE.HemisphereLight(0x3a3450, 0x1a1410, 1.6));
    const wallLight = new THREE.SpotLight(0xd9c6a8, 9000, 90, 0.55, 0.9, 1.5); wallLight.position.set(6, 22, 4); wallLight.target.position.set(-4, 8, -20); scene.add(wallLight, wallLight.target);
    // the relic's own light (grows in S3)
    const relicLight = new THREE.PointLight(0xff4a1a, 0, 14, 1.8); relicLight.position.set(0, 2.5, 0); scene.add(relicLight); monolith.userData.light = relicLight;
    // volumetric shafts + dust
    for (let i = 0; i < 3; i++) { const s = lightShaft({ length: 27, radiusTop: 0.25 + i * 0.15, radiusBottom: 1.6 + i * 0.5, color: 0xffd9a8, intensity: 0.55 - i * 0.12 }); s.position.set(3 + (i - 1) * 2.2, 25, 6 - i * 1.5); const dir = new THREE.Vector3((i - 1) * 1.5, 0, 0).sub(s.position).normalize(); s.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir); shafts.push(s); scene.add(s); }
    dust = dustPoints({ count: 1600, box: [14, 18, 14], center: [1, 9, 2], size: 0.045, opacity: 0.35, drift: 0.25, seed: 4 }); scene.add(dust);
    embers = dustPoints({ count: 1500, box: [5, 9, 5], center: [0, 4.5, 0], size: 0.05, color: 0xff6a2a, opacity: 0.0, drift: 0.35, wind: [0.1, 0.9, 0.05], seed: 9 }); scene.add(embers);
    post = makeComposer(renderer, scene, camera, { bloom: { strength: 0.7, radius: 0.5, threshold: 0.75 }, grade: 'ember', finish: { letterbox: 2.39, halation: 0.4, grain: 0.055, vignette: 0.42, aberration: 0.12 }, overlayAfterFinish: true });
  },
  render: async (ctx, i, t) => {
    const sh = ctx.timeline.at(t); const u = sh.u; const n = sh.i;
    // --- relic wake amount: 0 until S3, ramps during S3, full in S5
    const wake = n < 2 ? 0 : n === 2 ? ease.inQuart(u) : 1;
    // emissive reveal: glyphs light from the bottom up with a hot leading edge
    runeCtx.clearRect(0, 0, 512, 2048); runeCtx.fillStyle = '#000'; runeCtx.fillRect(0, 0, 512, 2048);
    if (wake > 0) { const y = 2048 * (1 - wake * 1.05); const grd = runeCtx.createLinearGradient(0, y - 220, 0, y + 60); grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(0.7, 'rgba(255,210,170,1)'); grd.addColorStop(1, 'rgba(0,0,0,0)');
      runeCtx.fillStyle = grd; runeCtx.fillRect(0, y - 220, 512, 2048); runeCtx.globalCompositeOperation = 'destination-in'; runeCtx.drawImage(glyphMask, 0, 0); runeCtx.globalCompositeOperation = 'source-over'; }
    runeMat.emissiveMap.needsUpdate = true; runeMat.emissiveIntensity = 2.8 * wake * (0.85 + 0.15 * noise1(t * 9, 3)); monolith.userData.light.intensity = 220 * wake * (0.9 + 0.1 * noise1(t * 7, 1));
    embers.material.uniforms.uOpacity.value = 0.75 * smoothstep(0.05, 0.6, wake);
    dust.update(t, camera, H); embers.update(t, camera, H); shafts.forEach(s => s.update(t));
    godLight.intensity = 2400 * (0.92 + 0.08 * noise1(t * 1.3, 8));
    // --- camera per shot (every move motivated: S1 locked-off dread; S2 crane = reveal/scale; S3 push-in = realization)
    if (n === 0) { rig.move({ pos: [1.1, 2.6, 1.75], look: [0.15, 2.2, 0.0], mm: 90 }, { pos: [1.05, 2.55, 1.7], look: [0.15, 2.25, 0.0], mm: 90 }, u, ease.linear); }
    else if (n === 1) { rig.move({ pos: [-3.2, 0.5, 12.5], look: [0, 2.6, 0], mm: 24 }, { pos: [-2.2, 5.0, 14.5], look: [0, 4.2, 0], mm: 24 }, u, ease.inOutSine); }
    else if (n === 2) { rig.move({ pos: [1.32, 1.95, 4.22], look: [0, 2.6, 0], mm: 40 }, { pos: [1.12, 1.98, 3.72], look: [0, 2.8, 0], mm: 40 }, u, ease.inOutCubic).handheld(t, 0.004 * (0.5 + wake), 0.0012 * (0.5 + wake), 1.6, 2); }
    else { rig.set({ pos: [1.12, 1.98, 3.72], look: [0, 2.8, 0], mm: 40 }); }
    rig.apply();
    // --- fades, black, titles
    const f = post.finish; f.fade.value = 1;
    if (n === 0) f.fade.value = Math.min(1, t / 0.6);
    if (n === 1) f.fade.value = 1;
    if (n === 2) f.fade.value = 1;
    if (n === 3) f.fade.value = 0; // hard black (silence)
    const { ctx: c, clear } = post.overlay; clear();
    if (n === 4) {
      f.fade.value = 0.0; // keep the scene black; the title is the only light
      const a = env(sh.t, sh.shot.dur, 0.25, 0.5); const glow = 30 + 40 * Math.max(0, 1 - sh.t * 1.5);
      drawText(c, 'RELIC', { x: W / 2, y: H * 0.47, font: `700 ${Math.round(H * 0.24)}px "Cinzel"`, color: `rgba(255,236,210,${a})`, spacing: Math.round(H * 0.045), shadow: glow, shadowColor: 'rgba(255,90,30,0.95)' });
      if (sh.t > 0.75) drawText(c, 'It was never buried.', { x: W / 2, y: H * 0.64, font: `400 ${Math.round(H * 0.045)}px "Cormorant Garamond"`, color: `rgba(230,200,170,${env(sh.t - 0.75, sh.shot.dur - 0.75, 0.5, 0.4)})`, spacing: 2 });
    }
    post.render(t);
  },
});
