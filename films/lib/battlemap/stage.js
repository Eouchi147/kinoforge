// Battle Map engine: a Stage = one map (terrain + blocks + arrows + overlay items + camera + light). The film has a main stage and optional
// inset stages (a second little map shown as a framed panel, or full screen).
import * as THREE from 'three';
import { fovFromMM, lerp } from '/harness/kit/film.js';
import { buildWorldData } from './worldgen.js';
import { bakeSheet, makeTerrainMaterial, makeSky, terrainGeometry } from './terrainShaders.js';
import { Track } from './timeline.js';
import { normaliseKey, CameraTrack, poseToCamera } from './camera.js';
import { Blocks } from './blocks.js';
import { Arrows } from './arrows.js';
import { StageOverlay } from './overlay.js';

export const DEFAULT_LOOK = {
  sun: [1.25, 0.92, 0.55], sunEve: [1.5, 0.62, 0.28], sky: [0.20, 0.26, 0.42], bounce: [0.15, 0.10, 0.055], fog: [0.93, 0.78, 0.58], horizon: [0.95, 0.80, 0.60], zenith: [0.45, 0.62, 0.82],
  horizonEve: [0.98, 0.52, 0.28], zenithEve: [0.30, 0.30, 0.52], glowEve: [1.1, 0.42, 0.12],
  fogDensity: 0.0016, fogFalloff: 0.028, edgeStart: 560, edgeEnd: 900, worldEdge: 70, cloud: 0.28, steps: 0.45, glint: 1.0,
};
const col3 = (a) => new THREE.Color(a[0], a[1], a[2]);

export class Stage {
  constructor({ renderer, shared, spec, look, clock, aspect, name }) {
    this.name = name; this.spec = spec; this.clock = clock; this.look = { ...DEFAULT_LOOK, ...look, ...(spec.look || {}) }; const Lk = this.look;
    this.world = buildWorldData(spec.world); const world = this.world;
    this.baked = bakeSheet(renderer, world, shared, spec.world.style || {});
    this.scene = new THREE.Scene(); this.scene.background = col3(Lk.horizon);
    this.camera = new THREE.PerspectiveCamera(35, aspect, 1.0, 8000); this.scene.add(this.camera);
    const { geometry, mh } = terrainGeometry(world, spec.world.meshStep || 2.5); this.mh = mh; world.mh = mh;
    this.terrainMat = makeTerrainMaterial(shared, world, this.baked.sheet, this.baked.U.mapTex, this.baked.U.mapOrg);
    this.terrain = new THREE.Mesh(geometry, this.terrainMat); this.terrain.frustumCulled = false; this.scene.add(this.terrain);
    this.sky = makeSky(shared); this.scene.add(this.sky);
    this.blocks = new Blocks(this.scene, world, spec.blocks || {}, clock, mh); this.blocks.applyMoves(spec.moves || []);
    this.arrows = new Arrows(this.scene, this, spec.arrows || [], clock);
    this.light = {}; for (const k of ['eve', 'haze', 'cloud', 'glint']) this.light[k] = new Track(k === 'cloud' ? Lk.cloud : k === 'eve' ? 0 : 1);
    for (const l of (spec.light || [])) { const [t0, t1] = clock.span(l, 1); for (const [k, v] of Object.entries(l.to)) { if (!this.light[k]) throw new Error('light: unknown prop ' + k); this.light[k].add(t0, t1, v, l.ease || 'inOut'); } }
    this.cam = new CameraTrack((spec.camera || []).map((k) => normaliseKey(k, clock, aspect)));
    this.overlay = new StageOverlay(this, spec, clock);
    this.pose = null; this.visible = true;
  }
  setVisible(v) { this.terrain.visible = v; this.sky.visible = v; this.blocks.mesh.visible = v && this.blocks.mesh.visible; this.blocks.shadow.visible = v && this.blocks.shadow.visible; this.visible = v; }
  update(t, poseOverride = null) {
    const { world, camera, terrainMat, sky, blocks, arrows, look: Lk } = this;
    const pose = poseOverride || this.cam.at(t) || { x: 0, z: 0, ty: 0, dist: 300, pitch: 60, yaw: 0, mm: 35, shake: 0 }; this.pose = pose;
    const cp = poseToCamera(pose, world.hAt(pose.x, pose.z), camera, null);
    camera.position.set(...cp.pos); camera.lookAt(new THREE.Vector3(...cp.look)); camera.fov = fovFromMM(cp.mm); camera.updateProjectionMatrix(); camera.updateMatrixWorld(true);
    const L = {}; for (const k in this.light) L[k] = this.light[k].at(t); const eve = L.eve; const U = terrainMat.uniforms;
    U.uSunCol.value.setRGB(...Lk.sun); U.uSunColB.value.setRGB(...Lk.sunEve); U.uSkyCol.value.setRGB(...Lk.sky); U.uBounce.value.setRGB(...Lk.bounce);
    const fog = col3(Lk.fog); U.uFogCol.value.copy(fog); U.uFog.value.set(Lk.fogDensity * L.haze, Lk.fogFalloff, Lk.edgeStart, Lk.edgeEnd); U.uAtm.value.set(eve, L.cloud, t * 0.05, Lk.glint * L.glint); U.uGrade.value.set(Lk.steps, Lk.worldEdge, 0, 0);
    const hz = col3(Lk.horizon), ze = col3(Lk.zenith); hz.lerp(col3(Lk.horizonEve), eve); ze.lerp(col3(Lk.zenithEve), eve);
    if (eve > 0) { fog.lerp(hz, eve); U.uFogCol.value.copy(fog); }
    sky.material.uniforms.uHorizon.value.copy(hz); sky.material.uniforms.uZenith.value.copy(ze); sky.material.uniforms.uSunGlow.value.setRGB(...[lerp(0.6, Lk.glowEve[0], eve), lerp(0.34, Lk.glowEve[1], eve), lerp(0.14, Lk.glowEve[2], eve)]);
    const sv = world.spec.sun || { azimuth: 300, elevation: 24 }, se = world.spec.sunEve || { azimuth: 288, elevation: 6 }; const az = lerp(sv.azimuth, se.azimuth, eve) * Math.PI / 180, el = lerp(sv.elevation, se.elevation, eve) * Math.PI / 180;
    const sunDir = [Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)]; sky.material.uniforms.uSunDir.value.set(...sunDir);
    const bu = blocks.uniforms; bu.uFogCol.value.copy(U.uFogCol.value); bu.uFog.value.copy(U.uFog.value); bu.uSkyCol.value.copy(U.uSkyCol.value); bu.uSunCol.value.copy(U.uSunCol.value).lerp(U.uSunColB.value, eve); bu.uSunDir.value.set(...sunDir);
    blocks.update(t, camera, Lk, sunDir); if (new URLSearchParams(location.search).get('nb')) { blocks.mesh.visible = false; blocks.shadow.visible = false; } arrows.update(t, { col: U.uFogCol.value, v: U.uFog.value });
  }
}
