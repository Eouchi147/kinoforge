// A hill road before dawn: lamp posts take their light one by one up the hill; the sky turns toward morning (1807).
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease } from '/harness/kit/film.js';
import { Setup, setLights, DW, DH } from './lib.js';
import { Canvas, hex, mixc, rgba, paintSky, underpaint } from './paint.js';
import { WARM, GLOW, coverCams, flick, drawLantern, line } from './common.js';

const RD = { sky: 9000, far: 1400, hill: 320, road: 80, post: 79 };
const HZ = 560; // horizon in design px
const roadX = (z) => 360 + 150 * Math.sin(z * 0.62) / z * 1.4;
const roadY = (z) => HZ + 720 / z;
const roadW = (z) => 270 / z;
const POSTS = [1.5, 2.1, 2.9, 3.9, 5.2, 6.9, 9.0, 11.8];

export function buildRoad(shots) {
  const S = new Setup('road', { pos: [0, 0, 0], mm: 35 }); const cams = coverCams(shots, 'road'); const cover = (D, m) => S.cover(D, cams, m); const planes = {};
  { const r = cover(RD.sky, 40); const C = new Canvas(r, { seed: 2801 });
    paintSky(C, { stops: [[-300, hex('#0a1030')], [200, hex('#1c2858')], [400, hex('#4a5a8a')], [520, hex('#b0887a')], [600, hex('#f0c090')], [760, hex('#f4d4a4')]], glow: { x: 360, y: 600, rx: 480, ry: 240, col: hex('#ffc890'), a: 0.6 },
      clouds: [{ y: 330, h: 24, x0: -300, x1: 1100, col: hex('#2a3460'), lit: hex('#e8a888'), litA: 0.7, sy: 0.022 }, { y: 470, h: 20, x0: -300, x1: 1100, col: hex('#4a5080'), lit: hex('#ffcfa0'), litA: 0.8, sy: 0.03, thr: 0.5 }], n: 0.9 }); C.mottle({ amt: 0.04 }); planes.sky = S.plane('sky', RD.sky, r, C.c); }
  { const r = cover(RD.far, 60); const C = new Canvas(r, { seed: 2811 }); const g = C.g, R = C.R; g.fillStyle = rgba(hex('#3a3858')); g.beginPath(); g.moveTo(r[0], 700); for (let x = r[0]; x <= r[2]; x += 20) g.lineTo(x, 585 + 26 * Math.sin(x * 0.011) + 12 * Math.sin(x * 0.031)); g.lineTo(r[2], 760); g.lineTo(r[0], 760); g.fill();
    C.blur(1.0); C.mottle({ amt: 0.04 }); planes.far = S.plane('far', RD.far, r, C.c); }
  { const r = cover(RD.hill, 60); const C = new Canvas(r, { seed: 2821 }); const g = C.g, R = C.R, n = C.n; const [x0, y0, x1, y1] = r;
    const hillTop = (x) => 575 + 40 * Math.sin(x * 0.007 + 1) + 24 * Math.sin(x * 0.019) - 70 * Math.exp(-((x - 360) * (x - 360)) / 40000);
    const p = new Path2D(); p.moveTo(x0, y1); for (let x = x0; x <= x1; x += 10) p.lineTo(x, hillTop(x)); p.lineTo(x1, y1); p.closePath();
    underpaint(C, (x, y) => mixc(hex('#262a42'), hex('#11121f'), smoothstep(560, 900, y)), p, 9); const m = C.mask((gg) => gg.fill(p));
    C.strokes({ n: C.area / 600, mask: m, color: (x, y) => mixc(hex('#343a58'), hex('#14152a'), R()), angle: () => (R() - 0.5) * 0.3, len: [14, 50], wid: [4, 9], alpha: [0.3, 0.55] });
    for (let x = x0; x < x1; x += 14 + R() * 18) { const y = hillTop(x); C.dab(x, y + 1, 0, 14 + R() * 12, 2.2, hex('#f0b080'), 0.22 + R() * 0.22, 0, 0.5); }
    for (let k = 0; k < 26; k++) { const x = 40 + R() * 640, y = hillTop(x) + 16 + R() * 40; g.fillStyle = rgba(hex('#e0a060'), 0.8); g.fillRect(x, y, 3, 3); }
    // a distant village roofline
    for (let x = 440; x < 660; x += 18 + R() * 14) { const h = 14 + R() * 18; g.fillStyle = rgba(hex('#0f0f1c')); const yb = hillTop(x) + 38; g.fillRect(x, yb - h, 16, h); g.beginPath(); g.moveTo(x - 2, yb - h); g.lineTo(x + 8, yb - h - 9); g.lineTo(x + 18, yb - h); g.fill(); }
    C.mottle({ amt: 0.04 }); planes.hill = S.plane('hill', RD.hill, r, C.c); }
  { const r = cover(RD.road, 70); const C = new Canvas(r, { seed: 2831 }); const g = C.g, R = C.R, n = C.n; const [x0, y0, x1, y1] = r;
    const gp = new Path2D(); gp.rect(x0 - 10, 602, x1 - x0 + 20, y1 - 602 + 10); const gm = C.mask((gg) => gg.fill(gp));
    underpaint(C, (x, y) => mixc(hex('#1d2036'), hex('#0b0b15'), smoothstep(600, y1, y)), gp, 10);
    C.strokes({ n: C.area / 700, mask: gm, color: () => mixc(hex('#2a3050'), hex('#10111e'), R()), angle: () => (R() - 0.5) * 0.4, len: [14, 50], wid: [4, 10], alpha: [0.3, 0.55] });
    // the road: a pale worn track winding up to the crest
    const rp = new Path2D(); const zs = []; for (let z = 1.0; z <= 40; z *= 1.05) zs.push(z); zs.reverse();
    rp.moveTo(roadX(zs[0]) - roadW(zs[0]), roadY(zs[0])); for (const z of zs) rp.lineTo(roadX(z) - roadW(z), roadY(z)); for (const z of zs.slice().reverse()) rp.lineTo(roadX(z) + roadW(z), roadY(z)); rp.closePath();
    const rc = (x, y) => mixc(hex('#4a4658'), hex('#2a2838'), smoothstep(600, y1, y)); underpaint(C, rc, rp, 8); const rm = C.mask((gg) => gg.fill(rp));
    C.strokes({ n: C.area / 1100, mask: rm, color: () => mixc(hex('#605a6c'), hex('#2c2a3a'), R()), angle: (x, y) => 0.2 + (R() - 0.5) * 0.3, len: [14, 40], wid: [3, 7], alpha: [0.3, 0.55] });
    for (let z = 1.0; z <= 30; z *= 1.07) for (const s of [-1, 1]) C.dab(roadX(z) + s * roadW(z) * 0.98, roadY(z), Math.PI / 2, Math.max(3, 40 / z), Math.max(1.4, 8 / z), hex('#0a0a14'), 0.6, 0, 0.4);
    // grass tufts along the verges
    for (let k = 0; k < 120; k++) { const z = 1.0 + R() * R() * 14; const s = R() < 0.5 ? -1 : 1; const x = roadX(z) + s * (roadW(z) * (1.15 + R() * 3)), y = roadY(z) - 1; C.dab(x, y, -Math.PI / 2 + (R() - 0.5) * 0.4, 30 / z + 4, Math.max(1.2, 5 / z), mixc(hex('#34405a'), hex('#12182a'), R()), 0.7, 0.05); }
    C.mottle({ amt: 0.05 }); planes.road = S.plane('road', RD.road, r, C.c); }
  for (const k of ['hill', 'road', 'far']) planes[k].material.uniforms.uTint.value.set(0.8, 0.82, 1.0);
  const glows = POSTS.map((z, i) => { const side = i % 2 ? 1 : -1; const x = roadX(z) + side * roadW(z) * 1.35, y = roadY(z) - 330 / z; const a = S.glow(x, y, RD.post, 130 / Math.sqrt(z) + 20, { color: GLOW, core: 40 }); const b = S.glow(x, y + 20 / z, RD.post, 900 / Math.sqrt(z), { color: [1, 0.55, 0.22], core: 5000 }); a.renderOrder = 1e6 - RD.post * 10 + 5; b.renderOrder = 1e6 - RD.post * 10 - 0.5; return { a, b, x, y, z, side }; });
  const sunA = S.glow(360, 600, RD.far - 2, 1500, { color: [1.0, 0.62, 0.34], core: 5000 }); const sunB = S.glow(360, 596, RD.far - 2, 420, { color: [1.0, 0.8, 0.55], core: 40 });
  const api = {
    key: 'road', S, planes, cams, show(v) { S.group.visible = v; },
    update(t, sh) {
      const dawn = sh.dawn ? sh.dawn(t) : 0; const tint = [lerp(0.55, 1.0, dawn), lerp(0.6, 0.95, dawn), lerp(1.0, 0.9, dawn)]; planes.sky.material.uniforms.uTint.value.set(...tint);
      sunA.material.uniforms.uI.value = 0.015 + 0.05 * dawn; sunB.material.uniforms.uI.value = 0.1 + 0.9 * dawn;
      const lights = []; glows.forEach((o, i) => { const k = sh.post ? clamp(sh.post(t, i), 0, 1) : 1; const fl = flick(t, 70 + i) * k; o.a.material.uniforms.uI.value = 1.0 * fl; o.b.material.uniforms.uI.value = 0.06 * fl; o.k = fl; const w = S.world(o.x, o.y + 8, RD.post); lights.push({ p: new THREE.Vector3(w.x, w.y, -RD.post + 3), r: 3.0, c: WARM, k: 3.0 * fl }); });
      for (const k of ['hill', 'road']) setLights(planes[k].material, lights.map((l) => ({ ...l, p: l.p.clone().setZ(-RD[k] + 3) })).slice(0, 8));
    },
    draw(g, e) {
      const { t, project, sh } = e; const P = (x, y) => project(...S.world(x, y, RD.post).toArray()); const sc = (Math.abs(P(100, 0)[0] - P(0, 0)[0])) / 100;
      glows.forEach((o, i) => { const k = sh.post ? clamp(sh.post(t, i), 0, 1) : 1; const base = P(o.x, roadY(o.z) - 2), top = P(o.x, o.y); const s = (1.0 / Math.sqrt(o.z)) * 0.7 + 0.2; line(g, base, [top[0], top[1] + 10 * sc * s], Math.max(1.6, 6 * sc / o.z), hex('#0a0810'));
        drawLantern(g, top[0], top[1], 70 * sc * s, k * flick(t, 70 + i), 0); });
    },
  };
  S.group.visible = false; return api;
}
