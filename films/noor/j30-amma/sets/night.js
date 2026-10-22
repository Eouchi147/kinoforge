// SET night: the Night of Decree. A calm, bright, still sky over sleeping flat roofs: mudbrick houses in layers, palms, a small
// mosque with a lit minaret, thin silver cloud. In "ten" a rope of ten lanterns crosses the roofs for the last ten nights (21 to 30),
// the odd nights glowing brighter. No people.
import { drawText } from '/harness/kit/film.js';
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, rng, WARM, tintAll, lightsOn, glowAt, motes, flick, igniteEnv, nightSky, makeStars, drawStars, fanous, glowLantern } from '../lib.js';

function roofs(C, seed, yBase, hMin, hMax, colA, colB, wins = 0.15) {
  const g = C.g, R = rng(seed); const [x0, , x1] = C.rect; const lit = [];
  let x = x0 - 30; while (x < x1 + 30) { const w = 60 + R() * 110, h = lerp(hMin, hMax, R()); const yb = yBase + R() * 20; const c = mixc(colA, colB, R());
    underpaint(C, (xx, yy) => mul(c, 0.8 + 0.35 * C.n.fbm(xx * 0.03, yy * 0.03, 3)), (() => { const p = new Path2D(); p.rect(x, yb - h, w, h + 400); return p; })(), 4);
    g.fillStyle = rgba(mul(c, 1.25)); g.fillRect(x - 2, yb - h - 4, w + 4, 5); // parapet catching sky light
    if (R() < 0.5) { g.fillStyle = rgba(mul(c, 0.7)); for (let k = 0; k < 3; k++) g.fillRect(x + w * (0.2 + k * 0.25), yb - h - 9, 7, 6); }
    for (let k = 0; k < 2; k++) if (R() < 0.6) { const wx = x + w * (0.25 + 0.4 * k), wy = yb - h * 0.6; const on = R() < wins; g.fillStyle = rgba(on ? hex('#3a2a18') : hex('#0e0d16')); g.beginPath(); g.moveTo(wx - 6, wy + 12); g.lineTo(wx - 6, wy); g.quadraticCurveTo(wx, wy - 9, wx + 6, wy); g.lineTo(wx + 6, wy + 12); g.closePath(); g.fill(); if (on) lit.push([wx, wy + 3, R() * 9]); }
    x += w + R() * 6; }
  return lit;
}

export default function night(S, cams) {
  const cover = (D, m = 50) => S.cover(D, cams, m); const D = { sky: 4000, town: 220, roofs2: 110, rope: 70, roofs1: 55 }; const planes = {};
  { const r = cover(D.sky, 80); const C = new Canvas(r, { seed: 1101 });
    nightSky(C, { stops: [[-1600, '#050a22'], [-400, '#0c1640'], [100, '#172660'], [380, '#24357a'], [560, '#34468a']], glow: { x: 640, y: 300, rx: 1100, ry: 500, col: hex('#4a5aa0'), a: 0.35 },
      clouds: [{ y: -60, h: 14, x0: -600, x1: 900, col: '#2a3a7a', lit: '#9aa6d8', litA: 0.5, thr: 0.56, sy: 0.03 }, { y: 140, h: 10, x0: 300, x1: 1900, col: '#304080', lit: '#a8b2e0', litA: 0.45, thr: 0.58, sy: 0.035 }] });
    planes.sky = S.plane('sky', D.sky, r, C.c); }
  // the town: the mosque dome and minaret among far roofs
  let town = []; { const r = cover(D.town, 60); r[1] = Math.max(r[1], 150); const C = new Canvas(r, { seed: 1102 }); const g = C.g;
    town = roofs(C, 1, 560, 30, 70, hex('#1c1f3a'), hex('#24284a'), 0.12);
    const dome = new Path2D(); dome.moveTo(820, 520); dome.quadraticCurveTo(822, 440, 880, 432); dome.quadraticCurveTo(938, 440, 940, 520); dome.closePath(); g.fillStyle = rgba(hex('#262a4c')); g.fill(dome); g.fillStyle = rgba(hex('#1c1f3a')); g.fillRect(800, 518, 160, 60);
    g.strokeStyle = rgba(hex('#4a5080')); g.lineWidth = 2; g.beginPath(); g.moveTo(880, 432); g.lineTo(880, 412); g.stroke(); g.beginPath(); g.arc(883, 408, 5, 0.6, 5.6); g.stroke();
    g.fillStyle = rgba(hex('#22264a')); g.fillRect(990, 330, 26, 250); g.fillRect(984, 400, 38, 8); g.fillRect(986, 330, 34, 10); g.beginPath(); g.moveTo(988, 330); g.lineTo(1003, 296); g.lineTo(1018, 330); g.closePath(); g.fill();
    g.fillStyle = rgba(hex('#4a3420')); g.fillRect(996, 344, 14, 18);
    planes.town = S.plane('town', D.town, r, C.c); }
  let near = []; { const r = cover(D.roofs2, 60); r[1] = Math.max(r[1], 300); const C = new Canvas(r, { seed: 1103 }); const g = C.g; near = roofs(C, 2, 640, 50, 110, hex('#1a1b30'), hex('#262640'), 0.1);
    // palms between the houses
    for (const [px, h, lean] of [[230, 260, -0.15], [700, 220, 0.12], [1150, 280, 0.2]]) { const yb = 640; g.strokeStyle = rgba(hex('#121226')); g.lineWidth = 7; g.lineCap = 'round'; g.beginPath(); g.moveTo(px, yb); g.quadraticCurveTo(px + lean * h * 0.4, yb - h * 0.6, px + lean * h * 0.5, yb - h); g.stroke();
      const tx = px + lean * h * 0.5, ty = yb - h; for (let k = 0; k < 9; k++) { const a = -Math.PI / 2 + (k - 4) * 0.42; const L = h * 0.36; for (let j = 1; j < 10; j++) { const u = j / 10; C.dab(tx + Math.cos(a) * L * u, ty + Math.sin(a) * L * 0.7 * u + L * 0.35 * u * u + 3, a + 0.9, L * 0.15, L * 0.04, hex('#14142a'), 0.95, 0.2); } } }
    planes.roofs2 = S.plane('roofs2', D.roofs2, r, C.c); }
  let front = []; { const r = cover(D.roofs1, 60); r[1] = Math.max(r[1], 420); const C = new Canvas(r, { seed: 1104 }); front = roofs(C, 3, 760, 70, 140, hex('#141526'), hex('#1e1e34'), 0.08); planes.roofs1 = S.plane('roofs1', D.roofs1, r, C.c); }
  const stars = makeStars(1105, [-1500, -2000, 2800, 420], 420, 1.8);
  // the rope of ten lanterns (rope plane depth), x positions and sag
  const ropeY = (x) => { const u = (x - 60) / 1160; return 370 + 110 * (1 - (2 * u - 1) ** 2); };
  const TEN = Array.from({ length: 10 }, (_, i) => { const u = (i + 0.5) / 10; const x = lerp(170, 1110, u); return { x, y: ropeY(x), n: 21 + i, odd: (21 + i) % 2 === 1 }; });
  return {
    update(F) {
      const t = F.t, g = F.g, sh = F.shot; const gg = F.glow();
      tintAll(S, 0.55); planes.sky.material.uniforms.uTint.value.set(0.85, 0.88, 1.0);
      drawStars(F, D.sky, stars, 0.9);
      for (const [lst, DD, sz] of [[town, D.town, 7], [near, D.roofs2, 10], [front, D.roofs1, 13]]) for (const [x, y, s] of lst) { const p = F.P(DD, x, y); glowAt(gg, p[0], p[1], sz * 2.4, 0.3 * flick(t, s), [255, 170, 90]); }
      { const p = F.P(D.town, 1003, 352); glowAt(gg, p[0], p[1], 40, 0.3 * flick(t, 2), [255, 180, 100]); glowAt(gg, p[0], p[1], 6, 0.9, [255, 230, 170]); }
      lightsOn(planes.town, [{ p: S.world(1003, 352, D.town), r: 9, c: WARM, k: 1.0 * flick(t, 2) }]);
      // the stillness: no wind, only a very slow drift of the silver cloud (sky plane drift) and a soft breathing glow over the town
      const tp = F.P(D.town, 640, 520); glowAt(gg, tp[0], tp[1] - 120, 700, 0.05 + 0.01 * Math.sin(t * 0.3), [150, 165, 255]);
      if (sh.mode === 'ten') {
        const og = F.og; let first = null, last = null;
        g.strokeStyle = 'rgba(18,16,24,0.95)'; g.lineWidth = 1.6 * F.K(D.rope); g.beginPath();
        for (let k = 0; k <= 60; k++) { const u = k / 60; const x = lerp(60, 1220, u), y = ropeY(x); const p = F.P(D.rope, x, y); k ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1]); } g.stroke();
        for (let i = 0; i < 10; i++) { const L = TEN[i]; const on = igniteEnv(t, sh.tenOn + i * 0.12, i, 0.5) * (L.odd ? lerp(0.55, 1.15, smoothstep(sh.oddOn, sh.oddOn + 0.8, t)) : lerp(0.55, 0.4, smoothstep(sh.oddOn, sh.oddOn + 0.8, t)));
          const p = F.P(D.rope, L.x, L.y); const s = 30 * F.K(D.rope, L.x, L.y); fanous(g, p[0], p[1] + s * 0.9, s, on, t, i + 20, { sway: 0.03, chain: s * 0.6 }); glowLantern(gg, p[0], p[1] + s * 0.9, s, on, t, i + 20, L.odd ? 1.2 : 0.8);
          if (on > 0) F.lights.push({ x: p[0], y: p[1] + s, r: 140 * s / 30, c: WARM, k: 0.35 * on });
          const na = smoothstep(sh.tenOn + i * 0.12, sh.tenOn + i * 0.12 + 0.6, t);
          if (na > 0) { drawText(og, String(L.n), { x: p[0], y: p[1] + s * 2.25, font: '500 20px "Cinzel"', color: L.odd ? '#ffe39a' : '#9a8f78', alpha: na * (L.odd ? 1 : lerp(1, 0.7, smoothstep(sh.oddOn, sh.oddOn + 0.8, t))), spacing: 2, shadow: 10, shadowColor: 'rgba(3,3,12,0.95)' }); F.ov = true; } }
        lightsOn(planes.roofs1, TEN.filter((L) => L.odd).map((L) => ({ p: S.world(L.x, L.y + 40, D.roofs1), r: 4, c: WARM, k: 0.8 * smoothstep(sh.oddOn, sh.oddOn + 0.8, t) })));
      }
      motes(gg, t, { x0: 0, y0: 0, x1: 1280, y1: 600 }, { n: 14, col: [200, 210, 255], a: 0.2, size: 1.0, seed: 61, drift: [1, -0.5] });
      F.amb = [0.95, 0.96, 1.0]; F.bloom = 0.5; F.hal = 0.2;
    },
  };
}
