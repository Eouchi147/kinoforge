import * as THREE from 'three';
import { boot, CameraRig, makeComposer, dustPoints, lightShaft, drawText, env, ease } from '/harness/kit/film.js';
let scene, camera, rig, post, cube, dust, shaft;
await boot({
  fps: 24, duration: 2, fonts: [['Bebas Neue', 400]],
  init: async ({ renderer, W, H }) => {
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x05060a); scene.fog = new THREE.FogExp2(0x05060a, 0.08);
    camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 100); rig = new CameraRig(camera).lens(35);
    const key = new THREE.SpotLight(0xffd9a0, 12, 30, 0.5, 0.5, 1.2); key.position.set(3, 6, 2); key.castShadow = true; scene.add(key);
    const rim = new THREE.DirectionalLight(0x6090ff, 1.5); rim.position.set(-4, 2, -3); scene.add(rim);
    scene.add(new THREE.AmbientLight(0x202030, 0.5));
    cube = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ color: 0x806040, roughness: 0.6, metalness: 0.2 })); cube.castShadow = true; cube.position.y = 0.5; scene.add(cube);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.MeshStandardMaterial({ color: 0x202020, roughness: 0.9 })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
    dust = dustPoints({ count: 400, box: [8, 4, 8], center: [0, 1.5, 0], size: 0.03, opacity: 0.5 }); scene.add(dust);
    shaft = lightShaft({ length: 8, radiusTop: 0.4, radiusBottom: 2.5, intensity: 0.25 }); shaft.position.set(1.5, 6, 0); shaft.rotation.z = 0.3; scene.add(shaft);
    post = makeComposer(renderer, scene, camera, { bloom: { strength: 0.5, radius: 0.5, threshold: 0.9 }, grade: 'ember', finish: { letterbox: 2.39 } });
  },
  render: async (ctx, i, t) => {
    cube.rotation.y = t * 0.8; dust.update(t, camera, ctx.H); shaft.update(t);
    rig.move({ pos: [4, 2, 5], look: [0, 0.6, 0], mm: 35 }, { pos: [2.5, 1.5, 3.5], look: [0, 0.6, 0], mm: 50 }, t / 2, ease.inOutCubic).handheld(t, 0.01, 0.002).apply();
    const { ctx: c, clear } = post.overlay; clear();
    drawText(c, 'SMOKE TEST', { x: ctx.W / 2, y: ctx.H * 0.5, font: '400 120px "Bebas Neue"', color: '#e8dcc0', spacing: 12, alpha: env(t, 2, 0.5, 0.5), shadow: 20 });
    post.finish.fade.value = env(t, 2, 0.3, 0.3);
    post.render(t);
  }
});
