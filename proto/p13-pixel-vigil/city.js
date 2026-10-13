// P13 city: sky dome, building boxes with gradient faces, instanced window grids (some animated), rooftop clutter.
import * as THREE from 'three';
import { rng } from '/harness/kit/film.js';
import { P, K, flat, colorBox } from './palette.js';

export function skyDome() { // banded gradient + two-tone cloud banks (value-noise thresholds -> the pixel pass steps and dithers them)
  const c = [P.skyGlow, P.skyHaze, P.skyLow, P.skyMid, P.skyTop, K(1, 1, 2), K(2, 1, 3)].map((h) => new THREE.Color(h));
  const m = new THREE.ShaderMaterial({
    uniforms: { c0: { value: c[0] }, c1: { value: c[1] }, c2: { value: c[2] }, c3: { value: c[3] }, c4: { value: c[4] }, c5: { value: c[5] }, c6: { value: c[6] }, uT: { value: 0 } },
    vertexShader: 'varying vec3 vD; void main(){ vD=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} ',
    fragmentShader: `varying vec3 vD; uniform vec3 c0,c1,c2,c3,c4,c5,c6; uniform float uT;
      float h(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
      float n(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y); }
      void main(){ vec3 d=normalize(vD); float e=d.y; vec3 col=mix(c0,c1,smoothstep(-0.02,0.07,e)); col=mix(col,c2,smoothstep(0.07,0.2,e)); col=mix(col,c3,smoothstep(0.2,0.45,e)); col=mix(col,c4,smoothstep(0.45,0.95,e));
        vec2 uv=d.xz/(d.y+0.28); uv=uv*1.1+vec2(uT,uT*0.3); float q=0.55*n(uv*1.3)+0.3*n(uv*2.7+4.1)+0.15*n(uv*5.3+9.7);
        float band=smoothstep(0.1,0.3,e)*(1.0-smoothstep(0.55,0.9,e));
        float m1=smoothstep(0.5,0.58,q)*band, m2=smoothstep(0.62,0.7,q)*band; col=mix(col,c5,m1*0.85); col=mix(col,c6,m2*0.6);
        gl_FragColor=vec4(col,1.0); }`,
    side: THREE.BackSide, depthWrite: false, depthTest: false,
  });
  const s = new THREE.Mesh(new THREE.SphereGeometry(900, 24, 16), m); s.renderOrder = -10; s.frustumCulled = false; return s;
}

const _wm = new THREE.MeshBasicMaterial({ color: 0xffffff });
const _wg = new THREE.PlaneGeometry(1, 1);
// Instanced window grid on a +z facade. pick(i,j,rnd) -> hex colour for that window. Returns {mesh, cells}
export function windowGrid(group, { x0, x1, yBot, yTop, z, ww, wh, px, py, pick, seed = 1, skip = null }) {
  const R = rng(seed); const cols = Math.max(1, Math.floor((x1 - x0 - ww) / px) + 1), rows = Math.max(1, Math.floor((yTop - yBot - wh) / py) + 1);
  const cells = []; for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) { const x = x0 + ww / 2 + i * px, y = yBot + wh / 2 + j * py; if (skip && skip(x, y)) continue; cells.push({ i, j, x, y }); }
  const mesh = new THREE.InstancedMesh(_wg, _wm, cells.length); const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(ww, wh, 1), col = new THREE.Color();
  cells.forEach((c, n) => { m4.compose(new THREE.Vector3(c.x, c.y, z), q, sc); mesh.setMatrixAt(n, m4); c.hex = pick(c.i, c.j, R, c.x, c.y); col.setHex(c.hex); mesh.setColorAt(n, col); c.n = n; });
  mesh.instanceMatrix.needsUpdate = true; mesh.instanceColor.needsUpdate = true; mesh.frustumCulled = false; group.add(mesh); return { mesh, cells };
}

// building: front face at z (faces +z), extends back by d. face = [topHex, lowHex] gradient over world y range [gy0,gy1]
export function building(group, { x0, x1, top, z, d, bottom = -60, face, side, roof, gy0 = -10, gy1 = 40 }) {
  const w = x1 - x0, h = top - bottom; const b = colorBox(w, h, d, { pz: { a: face[0], b: face[1], y0: gy0, y1: gy1 }, px: side, nx: side, py: roof, ny: side, nz: side }, { hs: 10, yc: bottom + h / 2 });
  b.position.set((x0 + x1) / 2, bottom + h / 2, z - d / 2); group.add(b); return b;
}
// small rooftop clutter on a building: stair hut, tank on legs, mast with beacon slot
export function roofClutter(group, { x0, x1, top, z, d, seed, face, roof, beacons, avoid = [] }) {
  const R = rng(seed); const n = Math.max(1, Math.round((x1 - x0) / 18));
  for (let k = 0; k < n; k++) {
    let x = x0 + (k + 0.3 + R() * 0.4) * (x1 - x0) / n; const kind = R(); for (const [a, b] of avoid) if (x >= a && x <= b) x = b + 0.5; // avoid = x-ranges kept clear (e.g. behind the watcher's head: no tangents)
    if (kind < 0.4) { const w = 3 + R() * 4, h = 1.8 + R() * 2.4; const m = colorBox(w, h, 3, { pz: face, px: face, nx: face, py: roof, nz: face }); m.position.set(x, top + h / 2, z - d * (0.3 + R() * 0.4)); group.add(m); }
    else if (kind < 0.7) { const t = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 2.6, 10), flat(face)); t.position.set(x, top + 3.6, z - d * 0.5); group.add(t);
      for (const lx of [-1.1, 1.1]) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.25, 2.4, 0.25), flat(face)); l.position.set(x + lx, top + 1.2, z - d * 0.5); group.add(l); } }
    else { const hgt = 5 + R() * 6; const mast = new THREE.Mesh(new THREE.BoxGeometry(0.28, hgt, 0.28), flat(face)); mast.position.set(x, top + hgt / 2, z - d * 0.5); group.add(mast);
      if (beacons) beacons.add(group, x, top + hgt + 0.3, z - d * 0.5 + 0.2, 1.2); }
  }
}
