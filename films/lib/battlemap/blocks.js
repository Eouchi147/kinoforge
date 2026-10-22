// Battle Map engine: army blocks. Rectangular formations (slabs with a rank-and-file pattern and a small banner) that can bend into a
// crescent, advance, retreat, wheel, compress and fade; cavalry are faster wedge blocks. Geometry is rebuilt every frame on the CPU (a few
// thousand vertices) and draped on the terrain mesh heights.
import * as THREE from 'three';
import { Track, easeFn } from './timeline.js';
import { GLSL_FOG } from './terrainShaders.js';
import { clamp, lerp, resample, catmull } from './noise.js';

const DEG = Math.PI / 180;
export const TEAMS = { // display-space colours: top, side, light, ink, trim
  rome: { top: [0.78, 0.11, 0.12], side: [0.40, 0.05, 0.06], dot: [0.46, 0.04, 0.06], light: [0.96, 0.42, 0.34], ink: [0.18, 0.05, 0.05], trim: [0.98, 0.84, 0.46] },
  carthage: { top: [0.13, 0.33, 0.80], side: [0.06, 0.15, 0.42], dot: [0.05, 0.14, 0.46], light: [0.45, 0.65, 0.98], ink: [0.04, 0.07, 0.22], trim: [0.98, 0.84, 0.46] },
  neutral: { top: [0.86, 0.80, 0.64], side: [0.52, 0.46, 0.34], dot: [0.45, 0.38, 0.26], light: [0.98, 0.94, 0.82], ink: [0.20, 0.15, 0.08], trim: [0.98, 0.84, 0.46] },
  gold: { top: [0.93, 0.72, 0.20], side: [0.58, 0.40, 0.08], dot: [0.55, 0.36, 0.05], light: [1.0, 0.92, 0.55], ink: [0.25, 0.14, 0.03], trim: [1, 0.95, 0.7] },
  green: { top: [0.20, 0.60, 0.30], side: [0.08, 0.30, 0.14], dot: [0.06, 0.28, 0.12], light: [0.55, 0.88, 0.55], ink: [0.04, 0.14, 0.06], trim: [0.98, 0.84, 0.46] },
};
export const KINDS = { infantry: 0, elite: 1, cavalry: 2, light: 3, marker: 4 };

const VERT = /* glsl */`
attribute vec3 aNormal; attribute vec4 aCol; attribute vec4 aUV; attribute vec4 aMeta;
varying vec3 vNormal; varying vec4 vCol; varying vec4 vUV; varying vec4 vMeta; varying vec3 vWorld;
void main(){ vNormal = aNormal; vCol = aCol; vUV = aUV; vMeta = aMeta; vWorld = position; gl_Position = projectionMatrix*viewMatrix*vec4(position, 1.0); }
`;
const FRAG = /* glsl */`
precision highp float;
${GLSL_FOG}
uniform vec3 uSunDir, uSunCol, uSkyCol, uFogCol; uniform vec4 uFog;
varying vec3 vNormal; varying vec4 vCol; varying vec4 vUV; varying vec4 vMeta; varying vec3 vWorld;
vec3 lin(vec3 c){ return pow(c, vec3(2.2)); }
void main(){
  float kind = vMeta.x; vec3 base = vCol.rgb; float alpha = vCol.a;
  vec3 N = normalize(vNormal);
  float ndl = max(dot(N, normalize(uSunDir)), 0.0);
  float fx = vMeta.w;                                        // fade (0 solid, 1 ghost)
  vec3 col; 
  if (kind < 0.5) {            // top face: wash, rank-and-file soldiers, inked border (elite: gold trim)
    float eu = vUV.z, ev = vUV.w; vec2 l = vUV.xy; vec2 cw = vMeta.yz; float elite = step(0.2, kind);
    vec2 fl = fract(l) - 0.5; float cell = max(fwidth(l.x), fwidth(l.y));
    float R = 0.44; float dd = length(fl*cw); float dotm = 1.0 - smoothstep(R - 0.12, R + 0.10, dd);
    float cov = clamp(3.1416*R*R/(cw.x*cw.y), 0.0, 0.85);
    dotm = mix(dotm, cov, smoothstep(0.30, 0.70, cell));
    float ed = min(eu, ev); float px = fwidth(ed) + 1e-4;
    float border = 1.0 - smoothstep(0.62 - px, 0.62 + px, ed);
    float rim = 1.0 - smoothstep(0.17 - px, 0.17 + px, abs(ed - 1.05));
    vec3 trim = vec3(0.98, 0.82, 0.42);
    col = mix(base*1.10, base*0.50, dotm*0.80);
    col = mix(col, mix(base, vec3(1.0), 0.55), rim*0.60*(1.0 - elite) + rim*elite*0.0);
    col = mix(col, trim, rim*elite*0.95);
    col = mix(col, vec3(0.05, 0.035, 0.03), border*0.94);
    col = lin(col)*(0.30 + 0.62*ndl*uSunCol + uSkyCol*0.55);
    alpha *= smoothstep(0.0, px*1.4, ed);
  } else if (kind < 1.5) {     // side walls
    col = lin(base)*(0.22 + 0.55*ndl*uSunCol + uSkyCol*0.5);
  } else if (kind < 2.5) {     // flag
    vec2 f = vUV.xy; vec3 c = base; float band = smoothstep(0.34, 0.36, f.y)*(1.0 - smoothstep(0.52, 0.54, f.y));
    c = mix(c, vec3(0.98, 0.93, 0.78), band*0.9); float edge = 1.0 - smoothstep(0.0, 0.04, min(min(f.x, 1.0 - f.x), min(f.y, 1.0 - f.y))); c = mix(c, vec3(0.08, 0.05, 0.04), edge*0.8);
    col = lin(c)*(0.55 + 0.45*uSunCol);
  } else if (kind < 3.5) {     // pole / finial
    col = lin(base)*(0.7 + 0.5*uSunCol);
  } else {                     // soft ground shadow
    gl_FragColor = vec4(0.02, 0.012, 0.01, alpha*vMeta.y); return;
  }
  col = mix(col, lin(vec3(0.62, 0.60, 0.58)), fx*0.55);
  col = bmFog(col, vWorld, uFog, uFogCol);
  gl_FragColor = vec4(col, alpha);
}
`;

export class Blocks {
  constructor(scene, world, specBlocks, clock, meshH) {
    this.world = world; this.clock = clock; this.meshH = meshH; this.defs = specBlocks; this.list = [];
    this.MAXV = 60000; this.MAXI = 100000;
    const mk = (maxv, maxi) => { const g = new THREE.BufferGeometry(); const a = (n) => new THREE.BufferAttribute(new Float32Array(maxv * n), n).setUsage(THREE.DynamicDrawUsage);
      g.setAttribute('position', a(3)); g.setAttribute('aNormal', a(3)); g.setAttribute('aCol', a(4)); g.setAttribute('aUV', a(4)); g.setAttribute('aMeta', a(4)); g.setIndex(new THREE.BufferAttribute(new Uint32Array(maxi), 1).setUsage(THREE.DynamicDrawUsage)); g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e5); return g; };
    this.geo = mk(this.MAXV, this.MAXI); this.sgeo = mk(this.MAXV / 3, this.MAXI / 3);
    const uniforms = { uSunDir: { value: new THREE.Vector3(0.5, 0.5, 0.5) }, uSunCol: { value: new THREE.Color(1.2, 0.9, 0.6) }, uSkyCol: { value: new THREE.Color(0.2, 0.26, 0.4) }, uFogCol: { value: new THREE.Color() }, uFog: { value: new THREE.Vector4(0.0016, 0.03, 560, 900) } };
    this.mat = new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: FRAG, uniforms, transparent: true, depthWrite: true, side: THREE.DoubleSide });
    this.smat = new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: FRAG, uniforms, transparent: true, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
    this.mesh = new THREE.Mesh(this.geo, this.mat); this.mesh.frustumCulled = false; this.mesh.renderOrder = 4; scene.add(this.mesh);
    this.shadow = new THREE.Mesh(this.sgeo, this.smat); this.shadow.frustumCulled = false; this.shadow.renderOrder = 3; scene.add(this.shadow);
    this.uniforms = uniforms; this.byId = {};
    this.groups = {};
    for (const [id, d0] of Object.entries(specBlocks)) {
      if (d0.grid) { // a formation of many small blocks: grid { cols across the frontage, ranks in depth, gap }; the group is addressable by `id`
        const G = d0.grid; const cols = G.cols ?? 4, ranks = G.ranks ?? 3, gap = G.gap ?? 2.4; const cl = d0.len / cols - gap * (cols - 1) / cols, cd = d0.dep / ranks - gap * (ranks - 1) / ranks; const hd = (d0.heading ?? 90) * DEG;
        const fx = Math.sin(hd), fz = -Math.cos(hd), rx = Math.cos(hd), rz = Math.sin(hd); const ids = [];
        for (let j = 0; j < ranks; j++) for (let i = 0; i < cols; i++) { const a = (i - (cols - 1) / 2) * (cl + gap), f = (j - (ranks - 1) / 2) * (cd + gap); const d = { ...d0, grid: undefined, len: cl, dep: cd, x: d0.x + rx * a + fx * f, z: d0.z + rz * a + fz * f, count: (d0.count || 0) / (cols * ranks), bannerScale: d0.bannerScale ?? 0.8 };
          const cid = `${id}.${i}.${j}`; const b = this.make(cid, d); b.group = id; this.list.push(b); this.byId[cid] = b; this.groups[cid] = [cid]; ids.push(cid); }
        this.groups[id] = ids; continue; }
      const b = this.make(id, d0); this.list.push(b); this.byId[id] = b; this.groups[id] = [id];
    }
  }
  expand(m) { const names = m.blocks ? (Array.isArray(m.blocks) ? m.blocks : [m.blocks]) : [m.block ?? m.group]; const out = []; for (const n of names) { if (!this.groups[n]) throw new Error('unknown block or group ' + n); out.push(...this.groups[n]); } return out; }
  make(id, d) {
    const kind = d.kind || 'infantry'; const cav = kind === 'cavalry'; const len = d.len ?? 40, dep = d.dep ?? (cav ? 12 : 18);
    const b = { id, d, team: TEAMS[d.team || 'neutral'] || TEAMS.neutral, teamName: d.team || 'neutral', kind, kindN: KINDS[kind] ?? 0, T: {} };
    const init = { x: d.x ?? 0, z: d.z ?? 0, heading: d.heading ?? 90, len, dep, bulge: d.bulge ?? 0, alpha: d.hidden ? 0 : (d.alpha ?? 1), drop: 0, scale: d.scale ?? 1, fade: 0, count: d.count ?? 0, flag: d.flag ?? 1, lift: 0, glow: 0, sink: 0 };
    for (const k of Object.keys(init)) b.T[k] = new Track(init[k]);
    b.rest = { len: d.restLen ?? len, dep: d.restDep ?? dep }; b.height = d.height ?? (cav ? 2.4 : 3.0); b.spacing = d.spacing ?? 1.7; b.wedge = d.wedge ?? (cav ? 0.9 : 0);
    return b;
  }
  // moves: [{block, at, dur|until, to:{prop:val}, by:{prop:delta}, ease, wheel:{about:[x,z], deg}, appear, vanish, fade}]
  applyMoves(moves) {
    const items = []; for (const m of moves) { const [t0, t1] = this.clock.span(m, 1); items.push({ m, t0, t1 }); }
    items.sort((a, b) => a.t0 - b.t0);
    for (const { m, t0, t1 } of items) {
      const ids = this.expand(m); let n = 0; const members = ids.map((id) => this.byId[id]);
      for (const id of ids) {
        const b = this.byId[id]; if (!b) throw new Error('moves: unknown block ' + id); const stag = (m.stagger || 0) * n++; const s0 = t0 + stag, s1 = t1 + stag; const ease = m.ease || 'inOut';
        if (m.to) for (const [k, v] of Object.entries(m.to)) { if (!b.T[k]) throw new Error('moves: unknown prop ' + k); b.T[k].add(s0, s1, v, ease); }
        if (m.by) for (const [k, v] of Object.entries(m.by)) { const T = b.T[k]; T.add(s0, s1, T.at(s0) + v, ease); }
        if (m.wheel) { const [px, pz] = m.wheel.about; const dg = m.wheel.deg; const x0 = b.T.x.at(s0), z0 = b.T.z.at(s0), h0 = b.T.heading.at(s0); const rel = [x0 - px, z0 - pz]; const e = easeFn(ease); // clockwise-positive on the map (z south)
          const ang = (u) => dg * DEG * u; const rot = (u) => { const a = ang(u), c = Math.cos(a), s = Math.sin(a); return [px + rel[0] * c - rel[1] * s, pz + rel[0] * s + rel[1] * c]; };
          b.T.x.add(s0, s1, 0, 'linear', { fn: (u) => rot(u)[0] }); b.T.z.add(s0, s1, 0, 'linear', { fn: (u) => rot(u)[1] }); b.T.heading.add(s0, s1, 0, 'linear', { fn: (u) => h0 + dg * u }); void e; }
        if (m.squeeze) { const q = m.squeeze; const [cx, cz] = q.about; const x0 = b.T.x.at(s0), z0 = b.T.z.at(s0); b.T.x.add(s0, s1, cx + (x0 - cx) * (q.kx ?? 1), ease); b.T.z.add(s0, s1, cz + (z0 - cz) * (q.kz ?? 1), ease);
          if (q.lenK) b.T.len.add(s0, s1, b.T.len.at(s0) * q.lenK, ease); if (q.depK) b.T.dep.add(s0, s1, b.T.dep.at(s0) * q.depK, ease); }
        if (m.path) { const pts = m.path.map((p) => (typeof p === 'string' ? [0, 0] : p)); const R = resample(m.smooth === false ? pts : catmull([[b.T.x.at(s0), b.T.z.at(s0)], ...pts], 12), 1.0); const at = (u) => { const sL = clamp(u, 0, 1) * R.L; let lo = 0, hi = R.n - 1; while (hi - lo > 1) { const mm = (lo + hi) >> 1; if (R.s[mm] <= sL) lo = mm; else hi = mm; } const t2 = (sL - R.s[lo]) / Math.max(1e-6, R.s[hi] - R.s[lo]); return [lerp(R.x[lo], R.x[hi], t2), lerp(R.z[lo], R.z[hi], t2), Math.atan2(R.x[Math.min(R.n - 1, hi)] - R.x[lo], -(R.z[Math.min(R.n - 1, hi)] - R.z[lo]))]; };
          b.T.x.add(s0, s1, 0, 'linear', { fn: (u) => at(u)[0] }); b.T.z.add(s0, s1, 0, 'linear', { fn: (u) => at(u)[1] }); if (m.face !== false) { const h0 = b.T.heading.at(s0); let hl = at(0.02)[2] / DEG; while (hl - h0 > 180) hl -= 360; while (hl - h0 < -180) hl += 360; const hEnd = at(1)[2] / DEG; let he = hEnd; while (he - hl > 180) he -= 360; while (he - hl < -180) he += 360; b.T.heading.add(s0, s0 + (s1 - s0) * 0.12, hl + (m.faceOffset || 0), 'inOut'); b.T.heading.add(s0 + (s1 - s0) * 0.12, s1, he + (m.faceOffset || 0), 'linear'); } }
        if (m.appear) { const T = b.T.drop; T.add(s0 - 2e-3, s0 - 1e-3, m.appearFrom ?? 14, 'linear'); T.add(s0, s1, 0, m.appearEase || 'outBounce'); b.T.alpha.add(s0 - 2e-3, s0 - 1e-3, 0, 'linear'); b.T.alpha.add(s0 - 1e-3, s0 + Math.min(0.3, s1 - s0), 1, 'out'); }
        if (m.vanish) { b.T.alpha.add(s0, s1, 0, 'inOut'); }
        if (m.fadeTo !== undefined) { b.T.fade.add(s0, s1, m.fadeTo, ease); b.T.alpha.add(s0, s1, m.alphaTo ?? 0.25, ease); b.T.sink.add(s0, s1, m.sinkTo ?? 0.8, ease); }
      }
    }
  }
  state(b, t) { const o = {}; for (const k in b.T) o[k] = b.T[k].at(t); return o; }
  pos(id, t) { const b = this.byId[id]; return [b.T.x.at(t), b.T.z.at(t)]; }
  update(t, camera, look, sunDir) {
    const me = camera.matrixWorld.elements; const cam = { right: [me[0], me[1], me[2]], up: [me[4], me[5], me[6]], fwd: [-me[8], -me[9], -me[10]] };
    const g = this.geo, sg = this.sgeo; const P = g.attributes.position.array, Nn = g.attributes.aNormal.array, C = g.attributes.aCol.array, UV = g.attributes.aUV.array, M = g.attributes.aMeta.array, I = g.index.array;
    const sP = sg.attributes.position.array, sN = sg.attributes.aNormal.array, sC = sg.attributes.aCol.array, sUV = sg.attributes.aUV.array, sM = sg.attributes.aMeta.array, sI = sg.index.array;
    let vc = 0, ic = 0, svc = 0, sic = 0; const cx = camera.position.x, cz = camera.position.z;
    const sd = [-sunDir[0], -sunDir[2]]; const sl = Math.hypot(sd[0], sd[1]) || 1; const shDir = [sd[0] / sl, sd[1] / sl]; const shLen = clamp(1 / Math.max(0.12, Math.tan(Math.asin(clamp(sunDir[1], 0.05, 1)))), 0.5, 7) ;
    const mh = this.meshH;
    for (const b of this.list) {
      const s = this.state(b, t); if (s.alpha <= 0.004) continue; const sc = s.scale; const L = Math.max(1, s.len * sc), Dp = Math.max(0.5, s.dep * sc); const hd = s.heading * DEG;
      const fx = Math.sin(hd), fz = -Math.cos(hd), rx = Math.cos(hd), rz = Math.sin(hd); const k = s.bulge ? 8 * s.bulge / L : 0;
      const NU = 2 * Math.ceil(clamp(L / 7, 3, 12) * (Math.abs(k) > 1e-4 ? 1.4 : 1)); const NV = 3; const wedge = b.wedge * Dp; const H = Math.max(0.3, b.height) * (1 - 0.5 * s.sink); const lift = 0.12 + s.drop + s.lift;
      const col = b.team; const cols = b.kind === 'elite' ? 1 : 0; const topc = b.kind === 'cavalry' ? col.top.map((c, ci) => lerp(c, col.light[ci], 0.22)) : col.top; const sideC = col.side; const al = s.alpha;
      const vBase = vc; const cols0 = Math.max(2, Math.round(b.rest.len / b.spacing)), rows0 = Math.max(2, Math.round(b.rest.dep / b.spacing));
      const pts = []; // [i][j] -> {x,z,y, eu, ev}
      for (let i = 0; i <= NU; i++) {
        const u = -L / 2 + L * i / NU; const th = k * u; let sx, sy, ts, tc; if (Math.abs(k) < 1e-6) { sx = u; sy = 0; ts = 0; tc = 1; } else { sx = Math.sin(th) / k; sy = (Math.cos(th) - 1) / k; ts = Math.sin(th); tc = Math.cos(th); }
        const frontV = Dp / 2 + wedge * (1 - Math.abs(2 * u / L)); const row = [];
        for (let j = 0; j <= NV; j++) { const v = lerp(-Dp / 2, frontV, j / NV); const lx = sx + v * ts, ly = sy + v * tc; const wx = s.x + rx * lx + fx * ly, wz = s.z + rz * lx + fz * ly;
          const eu = Math.min(i * L / NU, (NU - i) * L / NU); const ev = wedge ? Math.min(v + Dp / 2, (frontV - v) * 0.7) : Math.min(v + Dp / 2, frontV - v);
          row.push({ x: wx, z: wz, y: mh(wx, wz), eu, ev, u, v, frontV }); }
        pts.push(row);
      }
      // top face
      for (let i = 0; i <= NU; i++) for (let j = 0; j <= NV; j++) { const p = pts[i][j]; const o = vc++; P[o * 3] = p.x; P[o * 3 + 1] = p.y + H + lift; P[o * 3 + 2] = p.z; Nn[o * 3] = 0; Nn[o * 3 + 1] = 1; Nn[o * 3 + 2] = 0;
        C[o * 4] = topc[0]; C[o * 4 + 1] = topc[1]; C[o * 4 + 2] = topc[2]; C[o * 4 + 3] = al;
        UV[o * 4] = (p.u + L / 2) / L * cols0; UV[o * 4 + 1] = (p.v + Dp / 2) / (Dp + wedge) * rows0; UV[o * 4 + 2] = p.eu; UV[o * 4 + 3] = p.ev;
        M[o * 4] = cols ? 0.25 : 0; M[o * 4 + 1] = L / cols0; M[o * 4 + 2] = (Dp + wedge) / rows0; M[o * 4 + 3] = s.fade; }
      const idx = (i, j) => vBase + i * (NV + 1) + j;
      for (let i = 0; i < NU; i++) for (let j = 0; j < NV; j++) { const a = idx(i, j), bb = idx(i + 1, j), c = idx(i, j + 1), d = idx(i + 1, j + 1); I[ic++] = a; I[ic++] = c; I[ic++] = bb; I[ic++] = bb; I[ic++] = c; I[ic++] = d; }
      // walls: perimeter loop (front edge, right end, rear edge, left end)
      const per = []; for (let i = 0; i <= NU; i++) per.push(pts[i][NV]); for (let j = NV - 1; j >= 0; j--) per.push(pts[NU][j]); for (let i = NU - 1; i >= 0; i--) per.push(pts[i][0]); for (let j = 1; j < NV; j++) per.push(pts[0][j]);
      const wc = sideC; for (let q = 0; q < per.length; q++) { const a = per[q], bq = per[(q + 1) % per.length]; let nx = bq.z - a.z, nz = -(bq.x - a.x); const nl = Math.hypot(nx, nz) || 1; nx /= nl; nz /= nl;
        // outward: compare with direction from the block centre
        const mx = (a.x + bq.x) / 2 - s.x, mz = (a.z + bq.z) / 2 - s.z; if (nx * mx + nz * mz < 0) { nx = -nx; nz = -nz; }
        const o = vc; for (const [pp, top] of [[a, 0], [bq, 0], [bq, 1], [a, 1]]) { const w = vc++; P[w * 3] = pp.x; P[w * 3 + 1] = pp.y + (top ? H + lift : lift - 0.25); P[w * 3 + 2] = pp.z; Nn[w * 3] = nx; Nn[w * 3 + 1] = 0; Nn[w * 3 + 2] = nz; C[w * 4] = wc[0]; C[w * 4 + 1] = wc[1]; C[w * 4 + 2] = wc[2]; C[w * 4 + 3] = al; UV[w * 4] = 0; UV[w * 4 + 1] = 0; UV[w * 4 + 2] = 0; UV[w * 4 + 3] = 0; M[w * 4] = 1; M[w * 4 + 1] = 0; M[w * 4 + 2] = 0; M[w * 4 + 3] = s.fade; }
        I[ic++] = o; I[ic++] = o + 1; I[ic++] = o + 2; I[ic++] = o; I[ic++] = o + 2; I[ic++] = o + 3; }
      // soft shadow: the top face shifted along the shadow direction, flat on the ground
      { const sh = shLen * (H + lift * 0.5) + 0.4; const sb = svc; for (let i = 0; i <= NU; i++) for (let j = 0; j <= NV; j++) { const p = pts[i][j]; const o = svc++; const x = p.x + shDir[0] * sh, z = p.z + shDir[1] * sh; sP[o * 3] = x; sP[o * 3 + 1] = mh(x, z) + 0.06; sP[o * 3 + 2] = z; sN[o * 3 + 1] = 1; sC[o * 4 + 3] = al; sM[o * 4] = 4; sM[o * 4 + 1] = 0.34 * (1 - 0.6 * s.fade); sUV[o * 4] = 0; }
        for (let i = 0; i < NU; i++) for (let j = 0; j < NV; j++) { const a = sb + i * (NV + 1) + j, bb = a + NV + 1, c = a + 1, d = bb + 1; sI[sic++] = a; sI[sic++] = c; sI[sic++] = bb; sI[sic++] = bb; sI[sic++] = c; sI[sic++] = d; } }
      // banner: pole + flag. The cloth is a camera-facing billboard (so it reads from a top-down view too), flapping
      if (s.flag > 0.01 && b.d.banner !== false) { const pc = pts[NU / 2][Math.min(NV, Math.max(1, Math.round(NV / 2)))]; const ph = pc.y + H + lift; const sc2 = Math.min(1.5, 0.75 + L / 80) * (b.d.bannerScale ?? 1); const poleH = 6.0 * sc2 * s.flag, fw = 4.6 * sc2, fh = 2.8 * sc2;
        const rgt = [cam.right[0], cam.right[1], cam.right[2]], upv = [cam.up[0], cam.up[1], cam.up[2]]; const nrm = [cam.fwd[0] * -1, cam.fwd[1] * -1, cam.fwd[2] * -1];
        const quad = (p0, p1, p2, p3, kind, uv, colr) => { const o = vc; const ps = [p0, p1, p2, p3]; for (let q2 = 0; q2 < 4; q2++) { const w = vc++; P[w * 3] = ps[q2][0]; P[w * 3 + 1] = ps[q2][1]; P[w * 3 + 2] = ps[q2][2]; Nn[w * 3] = nrm[0]; Nn[w * 3 + 1] = nrm[1]; Nn[w * 3 + 2] = nrm[2]; C[w * 4] = colr[0]; C[w * 4 + 1] = colr[1]; C[w * 4 + 2] = colr[2]; C[w * 4 + 3] = al; UV[w * 4] = uv[q2][0]; UV[w * 4 + 1] = uv[q2][1]; UV[w * 4 + 2] = 0; UV[w * 4 + 3] = 0; M[w * 4] = kind; M[w * 4 + 1] = 0; M[w * 4 + 2] = 0; M[w * 4 + 3] = s.fade; } I[ic++] = o; I[ic++] = o + 1; I[ic++] = o + 2; I[ic++] = o; I[ic++] = o + 2; I[ic++] = o + 3; };
        const pw = 0.20 * sc2; quad([pc.x - rgt[0] * pw, ph, pc.z - rgt[2] * pw], [pc.x + rgt[0] * pw, ph, pc.z + rgt[2] * pw], [pc.x + rgt[0] * pw, ph + poleH, pc.z + rgt[2] * pw], [pc.x - rgt[0] * pw, ph + poleH, pc.z - rgt[2] * pw], 3, [[0, 0], [1, 0], [1, 1], [0, 1]], [0.95, 0.80, 0.42]);
        const top = [pc.x, ph + poleH, pc.z]; const NS = 6; const ph0 = b.id.length * 1.7; const fc = col.top.map((c2, ci) => lerp(c2, col.light[ci], 0.15));
        const at = (u, v) => { const wv = Math.sin(t * 5.5 + u * 4.2 + ph0) * 0.18 * sc2 * u; const wl = Math.sin(t * 5.5 + u * 4.2 + ph0 + 1.2) * 0.14 * sc2 * u; return [top[0] + rgt[0] * (pw + fw * u) + upv[0] * (v * fh) + nrm[0] * wv + 0, top[1] + rgt[1] * (pw + fw * u) + upv[1] * (v * fh) + wl * 0.5, top[2] + rgt[2] * (pw + fw * u) + upv[2] * (v * fh) + nrm[2] * wv]; };
        for (let q2 = 0; q2 < NS; q2++) { const u0 = q2 / NS, u1 = (q2 + 1) / NS; quad(at(u0, -1), at(u1, -1), at(u1, 0), at(u0, 0), 2, [[u0, 0], [u1, 0], [u1, 1], [u0, 1]], fc); } }
    }
    g.setDrawRange(0, ic); sg.setDrawRange(0, sic); for (const n of ['position', 'aNormal', 'aCol', 'aUV', 'aMeta']) { g.attributes[n].needsUpdate = true; sg.attributes[n].needsUpdate = true; } g.index.needsUpdate = true; sg.index.needsUpdate = true;
    this.mesh.visible = ic > 0; this.shadow.visible = sic > 0;
  }
}
