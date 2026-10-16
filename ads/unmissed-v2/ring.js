// The glass ring of "The Catch": a torus built in the vertex shader (so the tube can grow from a hairline to glass),
// lit by a procedural studio environment (soft boxes and blue rim light) with a fresnel body, plus node, halo and dust.
import * as THREE from 'three';

const VERT = `
uniform float uR, uTube;
attribute vec2 tuv;
varying vec2 vT; varying vec3 vN; varying vec3 vWN; varying vec3 vWP; varying vec3 vV;
void main(){
  float a = 1.5707963 - tuv.x * 6.2831853, b = tuv.y * 6.2831853;
  float rr = uR + uTube * cos(b);
  vec3 p = vec3(rr * cos(a), rr * sin(a), uTube * sin(b));
  vec3 n = vec3(cos(b) * cos(a), cos(b) * sin(a), sin(b));
  vT = tuv; vWN = normalize(mat3(modelMatrix) * n); vec4 wp = modelMatrix * vec4(p, 1.0); vWP = wp.xyz;
  vec4 mv = viewMatrix * wp; vN = normalize(normalMatrix * n); vV = -mv.xyz;
  gl_Position = projectionMatrix * mv;
}`;

const FRAG = `
precision highp float;
uniform float uDraw, uEnergy, uSweep, uHair, uBody;
uniform vec3 uCam;
varying vec2 vT; varying vec3 vN; varying vec3 vWN; varying vec3 vWP; varying vec3 vV;
vec3 env(vec3 d){
  float up = d.y * 0.5 + 0.5;
  vec3 c = mix(vec3(0.004, 0.012, 0.045), vec3(0.06, 0.16, 0.42), pow(up, 1.4));
  c += vec3(0.55, 0.75, 1.0) * 5.0 * pow(max(dot(d, normalize(vec3(0.55, 0.85, 0.55))), 0.0), 36.0);   // key soft box
  c += vec3(0.14, 0.42, 1.0) * 2.4 * pow(max(dot(d, normalize(vec3(-0.85, -0.25, 0.45))), 0.0), 7.0);      // blue rim light
  c += vec3(0.62, 0.52, 1.0) * 1.6 * pow(max(dot(d, normalize(vec3(0.7, -0.7, -0.3))), 0.0), 12.0);        // violet kicker
  c += vec3(0.35, 0.6, 1.0) * 0.9 * exp(-pow(d.y * 5.0 + 0.2, 2.0));                                        // horizon streak
  return c;
}
void main(){
  if (vT.x > uDraw) discard;
  vec3 N = normalize(vN), V = normalize(vV), Nw = normalize(vWN), Vw = normalize(uCam - vWP);
  float nv = clamp(abs(dot(N, V)), 0.0, 1.0);
  float F = 0.06 + 0.94 * pow(1.0 - nv, 3.2);
  vec3 refl = env(reflect(-Vw, Nw));
  vec3 rfr = env(refract(-Vw, Nw, 0.72));
  float ang = vT.x * 6.2831853;
  float sw = pow(0.5 + 0.5 * cos(ang - uSweep), 4.0);                    // a highlight that travels round the ring
  vec3 deep = vec3(0.012, 0.07, 0.30), blue = vec3(0.18, 0.49, 1.0), accent = vec3(0.47, 0.71, 1.0);
  vec3 body = (deep * (0.35 + 0.65 * nv) + rfr * vec3(0.10, 0.22, 0.55) * 0.55) * uBody;      // dark blue glass, a little refracted light
  vec3 rim = mix(blue, accent, sw) * pow(1.0 - nv, 2.2) * (0.55 + 1.1 * sw) * uBody;           // rim light, never white
  float core = pow(nv, 36.0);                                              // the thin refracted line down the middle of the tube
  vec3 col = body + rim + refl * F * 0.9 * uBody + accent * core * (0.18 + 0.7 * sw) * uBody;
  col *= 0.35 + uEnergy * 0.5;
  float head = exp(-max(uDraw - vT.x, 0.0) * 55.0) * step(vT.x, uDraw) * step(uDraw, 0.999);
  col += uHair * vec3(0.47, 0.71, 1.0) * (0.55 + 2.2 * head);
  gl_FragColor = vec4(col, 1.0);
}`;

export function makeRing() {
  const U = 192, Vs = 28, pos = [], tuv = [], idx = [];
  for (let i = 0; i <= U; i++) for (let j = 0; j <= Vs; j++) { pos.push(0, 0, 0); tuv.push(i / U, j / Vs); }
  for (let i = 0; i < U; i++) for (let j = 0; j < Vs; j++) { const a = i * (Vs + 1) + j, b = a + Vs + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('tuv', new THREE.Float32BufferAttribute(tuv, 2)); geo.setIndex(idx);
  const mat = new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: FRAG, side: THREE.DoubleSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uR: { value: 3 }, uTube: { value: 0.012 }, uDraw: { value: 0 }, uEnergy: { value: 0.3 }, uSweep: { value: 0 }, uHair: { value: 0.6 }, uBody: { value: 0 }, uCam: { value: new THREE.Vector3() } } });
  const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false; mesh.renderOrder = 5;
  return mesh;
}

// soft halo disc in the ring's plane: brightest on the ring's circle
export function makeHalo(R) {
  const mat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uI: { value: 0 }, uR: { value: R } },
    vertexShader: 'varying vec2 vp; void main(){ vp = position.xy; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: 'varying vec2 vp; uniform float uI, uR; void main(){ float r = length(vp); float d = (r - uR) / 0.95; float g = exp(-d * d) * 0.20 + exp(-d * d * 0.2) * 0.012; g *= smoothstep(uR * 1.75, uR * 1.05, r);'
      + ' gl_FragColor = vec4(vec3(0.16, 0.42, 1.0) * g * uI, 1.0); }' });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(R * 3.6, R * 3.6), mat); m.position.z = -0.12; m.renderOrder = 4; m.frustumCulled = false; return m;
}

export function makeDust(n, rnd, tex) {
  const g = new THREE.BufferGeometry(), p = new Float32Array(n * 3), base = [];
  for (let i = 0; i < n; i++) { base.push([(rnd() - 0.5) * 44, (rnd() - 0.5) * 24, -110 + rnd() * 130, 0.5 + rnd() * 0.9]); }
  g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  const m = new THREE.PointsMaterial({ map: tex, size: 0.2, sizeAttenuation: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.8, color: 0x79b4ff, fog: true });
  const pts = new THREE.Points(g, m); pts.frustumCulled = false;
  pts.userData.update = (flow) => {
    for (let i = 0; i < n; i++) { const b = base[i]; let z = b[2] + flow * b[3]; z = ((z + 110) % 130 + 130) % 130 - 110; p[i * 3] = b[0]; p[i * 3 + 1] = b[1]; p[i * 3 + 2] = z; }
    g.attributes.position.needsUpdate = true;
  };
  return pts;
}
