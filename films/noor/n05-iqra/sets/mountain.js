// SET mountain: Jabal an-Nur (the Mountain of Light) seen from the hills to its west at night. A steep rocky peak, the path that
// zigzags up its face, the small notch of the cave of Hira just under the summit, Makkah's lamps far below on the left.
// Modes (shot.mode): 'night' (default), 'dusk' (afterglow), 'light' (the horizon behind the peak fills with white-gold light),
// 'dawn' (time passing: stars wheel, the sky warms). The Prophet is never drawn: a hand lantern alone climbs or descends the path.
import { Canvas, hex, mixc, mul, rgba, clamp, lerp, smoothstep, ease, rng, det, bump, tintAll, lightsOn, THREE } from './common.js';
import { paintSky, paintRange, paintFog, paintRocks, paintTufts, ridged } from '../paint.js';
import { birds, smoke, motes, hazeBand } from '../ambient.js';
import { glowAt, handLantern, stars, flick, hash1 } from '../fx.js';

// the path up the face of the peak (design px on the peak plane, D = 1100), from the foot to the cave
export const PATH = [[452, 640], [520, 612], [596, 598], [560, 560], [618, 532], [690, 520], [652, 470], [706, 440], [760, 428], [722, 380], [770, 344], [812, 330], [784, 290], [820, 262], [838, 252]];
export const CAVE = [846, 250];
export const PEAK_D = 1100;
const ridgePeak = (x) => 640 - bump(x, 800, 150, 450) - bump(x, 690, 80, 70) - bump(x, 960, 120, 120) - bump(x, 1130, 160, 90) - 26 * ridged(x * 0.012, 4, 3) - 8 * ridged(x * 0.05, 3, 9);

// position along the path, u in 0..1 (arc length)
const segs = (() => { const L = [0]; for (let i = 1; i < PATH.length; i++) L.push(L[i - 1] + Math.hypot(PATH[i][0] - PATH[i - 1][0], PATH[i][1] - PATH[i - 1][1])); return L; })();
export function pathAt(u) {
  const d = clamp(u) * segs[segs.length - 1]; let i = 1; while (i < segs.length - 1 && segs[i] < d) i++;
  const f = (d - segs[i - 1]) / Math.max(1e-6, segs[i] - segs[i - 1]); return [lerp(PATH[i - 1][0], PATH[i][0], f), lerp(PATH[i - 1][1], PATH[i][1], f)];
}

export default function mountain(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, far: 3200, city: 1900, peak: PEAK_D, hills: 480, near: 190, fg: 80 }; const P = {}; const city = [];
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 5101 });
    paintSky(C, { stops: [[-900, hex('#020309')], [-200, hex('#04060f')], [150, hex('#0a0e2a')], [380, hex('#151a46')], [520, hex('#2a2a5c')], [600, hex('#4a3f6e')], [660, hex('#6a5070')]],
      glow: { x: 900, y: 640, rx: 900, ry: 220, col: hex('#8a6878'), a: 0.45 },
      clouds: [{ y: 120, h: 12, x0: -400, x1: 1600, col: hex('#0a0d26'), lit: hex('#20255a'), litA: 0.4, sy: 0.03 }, { y: 470, h: 9, x0: 200, x1: 1700, col: hex('#22224e'), lit: hex('#6a5880'), litA: 0.6, thr: 0.5, sy: 0.04 }] });
    const R = rng(51011); for (let i = 0; i < 520; i++) { const x = lerp(r[0], r[2], R()), y = lerp(r[1], 520, Math.pow(R(), 1.3)); const b = R(); C.g.fillStyle = rgba([215, 222, 255], 0.2 + b * 0.55); C.g.beginPath(); C.g.arc(x, y, 0.4 + b * 0.9, 0, 7); C.g.fill(); }
    C.mottle({ amt: 0.05 }); P.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.far); r[1] = Math.max(r[1], 380); const C = new Canvas(r, { seed: 5102 });
    paintRange(C, { ridge: (x) => 600 - bump(x, 120, 240, 60) - bump(x, 1250, 260, 70) - 34 * ridged(x * 0.004, 4, 1), top: hex('#1c2048'), mid: hex('#1a1d42'), base: hex('#15183a'), fall: 120, light: { dir: -1, col: hex('#3a3a70'), amt: 0.3 }, rim: hex('#6a5a86'), haze: { col: hex('#2e2c5e'), y0: 560, y1: 660, a: 0.6 } });
    C.mottle({ amt: 0.05 }); P.far = S.plane('far', D.far, r, C.c); }
  // Makkah far below on the left: a valley floor with a scatter of lamps (glows) and pale roofs
  { const r = cover(D.city); r[1] = Math.max(r[1], 520); const C = new Canvas(r, { seed: 5103 }); const R = rng(51031);
    const ridge = (x) => 610 + 10 * Math.sin(x * 0.006) + det(x, 6, 3, 2);
    paintRange(C, { ridge, top: hex('#191a3c'), mid: hex('#161736'), base: hex('#12132e'), fall: 80, light: { dir: -1, col: hex('#2a2a5a'), amt: 0.25 }, sizes: 0.7 });
    for (let i = 0; i < 260; i++) { const x = lerp(r[0], 640, Math.pow(R(), 0.8)); const y = ridge(x) + 6 + R() * 40; C.g.fillStyle = rgba(mixc(hex('#3a3456'), hex('#5a4a5a'), R()), 0.7); C.g.fillRect(x, y, 3 + R() * 6, 2 + R() * 2); if (R() < 0.35) city.push([x + 2, y + 1]); }
    C.mottle({ amt: 0.04 }); P.city = S.plane('city', D.city, r, C.c); }
  // the peak itself
  { const r = cover(D.peak); r[1] = Math.max(r[1], 100); const C = new Canvas(r, { seed: 5104 }); const g = C.g;
    const { colAt } = paintRange(C, { ridge: ridgePeak, top: hex('#2a2a52'), mid: hex('#1e1f40'), base: hex('#141530'), fall: 380, light: { dir: -1, col: hex('#4a4878'), amt: 0.42 }, shade: 0.22, rim: hex('#8a7a9e'), sizes: 1.1 });
    // boulders and ledges on the face
    const R = rng(51041); for (let i = 0; i < 160; i++) { const x = lerp(560, 1150, R()); const y = lerp(ridgePeak(x) + 10, 660, R()); if (y < ridgePeak(x) + 6) continue; const s = 4 + R() * 12; C.dab(x, y, -0.2 + (R() - 0.5) * 0.6, s * 2.2, s, mul(colAt(x, y), 0.65), 0.75, 0.2); C.dab(x - s * 0.3, y - s * 0.35, -0.3, s * 1.4, s * 0.35, mul(colAt(x, y), 1.35), 0.4, 0.1); }
    // the path: a pale worn line
    for (let i = 1; i < PATH.length; i++) { const [a, b] = [PATH[i - 1], PATH[i]]; const n = Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / 5); for (let k = 0; k < n; k++) { const f = k / n; const x = lerp(a[0], b[0], f) + (R() - 0.5) * 2, y = lerp(a[1], b[1], f) + (R() - 0.5) * 1.5; C.dab(x, y, Math.atan2(b[1] - a[1], b[0] - a[0]), 7, 2.2, hex('#4a4668'), 0.5, 0.1); } }
    // the cave of Hira: a small dark notch with an overhang
    g.fillStyle = rgba(hex('#07070f')); g.beginPath(); g.ellipse(CAVE[0], CAVE[1], 11, 7, -0.15, 0, 7); g.fill(); C.dab(CAVE[0] - 2, CAVE[1] - 9, -0.15, 30, 5, hex('#3a3860'), 0.8, 0.1);
    C.mottle({ amt: 0.06 }); P.peak = S.plane('peak', D.peak, r, C.c); }
  { const r = cover(D.hills); r[1] = Math.max(r[1], 540); const C = new Canvas(r, { seed: 5105 });
    paintRange(C, { ridge: (x) => 652 + 20 * Math.sin(x * 0.004 + 1) - bump(x, 200, 220, 40) + det(x, 8, 3, 4), top: hex('#16162e'), mid: hex('#101024'), base: hex('#0b0b1a'), fall: 160, light: { dir: -1, col: hex('#28284e'), amt: 0.3 }, rim: hex('#4a4672'), sizes: 1.2 });
    paintTufts(C, { x0: r[0], x1: r[2], base: (x) => 670 + 20 * Math.sin(x * 0.004 + 1), step: 22, h0: 6, h1: 16, col: hex('#0a0a16'), blades: 4, jitter: 30 });
    C.mottle({ amt: 0.05 }); P.hills = S.plane('hills', D.hills, r, C.c); }
  { const r = cover(D.fg, 40); r[1] = Math.max(r[1], 560); const C = new Canvas(r, { seed: 5106 });
    paintRocks(C, { rocks: [{ x: 40, y: 760, rx: 260, ry: 90 }, { x: 1260, y: 770, rx: 240, ry: 80 }], col: hex('#05050c'), lit: hex('#1c1a30'), litA: 0.4, blur: 3 }); P.fg = S.plane('fg', D.fg, r, C.c); }
  const cityGlow = city.slice(0, 60).map(([x, y], i) => S.glow(x, y, D.city, 10 + hash1(i) * 10, { color: [1.0, 0.6, 0.28], core: 160 }, P.city));
  const caveGlow = S.glow(CAVE[0], CAVE[1], D.peak, 70, { color: [1.0, 0.9, 0.62], core: 80 }, P.peak);
  const dawnCol = [1.0, 0.72, 0.6];
  return {
    planes: P, D,
    update(F) {
      const t = F.t, lt = F.lt, sh = F.shot, g = F.g, gg = F.glow(); const mode = sh.mode || 'night';
      // light levels by mode: dusk is a little brighter and warmer, night is deep blue, dawn rises over the shot
      let k = mode === 'dusk' ? 1.0 : 0.72, warm = mode === 'dusk' ? 0.12 : 0; let dawn = 0, light = 0;
      if (mode === 'dawn') { dawn = ease.inOutSine(clamp((lt - (sh.dawnAt ?? 1.5)) / (sh.dawnLen ?? 8))); k = lerp(0.62, 1.05, dawn); }
      if (sh.dark) k *= sh.dark;
      if (mode === 'light') light = ease.inOutSine(clamp((lt - (sh.lightAt ?? 0.4)) / (sh.lightLen ?? 4)));
      const tw = (pl, kk, c) => pl.material.uniforms.uTint.value.set(kk * c[0], kk * c[1], kk * c[2]);
      const skyC = [1 - 0.05 * dawn + warm * 0.4 + light * 0.7, 1 - 0.08 * dawn + light * 0.55, 1.08 - 0.25 * dawn - warm * 0.2 + light * 0.2];
      tw(P.sky, k * (1 + 0.4 * dawn) + light * 0.9, skyC); tw(P.far, k * (1 + 0.25 * dawn) + light * 0.35, [1 + 0.1 * dawn, 1, 1.05]); tw(P.city, k, [1, 1, 1.05]);
      tw(P.peak, k * (1 + 0.15 * dawn) - light * 0.25, [1 + 0.08 * dawn, 1, 1.04]); tw(P.hills, k * 0.95 + 0.1 * dawn, [1, 1, 1.05]); tw(P.fg, k, [1, 1, 1]);
      // stars: a twinkling layer high in the sky, wheeling slowly when time passes (dawn), fading as the sky warms or fills with light
      const sa = (1 - dawn) * (1 - light) * (mode === 'dusk' ? 0.55 : 1) * (sh.starsA ?? 1);
      if (sa > 0.02) { const a = F.P(D.sky, -600, -500), b = F.P(D.sky, 1900, 330); stars(gg, t, [a[0], a[1], b[0], b[1]], { n: 160, seed: 11, a: 0.7 * sa, rot: mode === 'dawn' ? -0.05 * lt / 10 : 0, pole: F.P(D.sky, 300, -1400) }); }
      // the city's lamps: a soft flicker; they fade with dawn
      cityGlow.forEach((gm, i) => { gm.visible = true; gm.material.uniforms.uI.value = 0.55 * flick(t, i) * (1 - 0.7 * dawn) * (sh.cityA ?? 1); });
      // the horizon behind the peak fills with light (the angel's coming is shown only as light)
      caveGlow.visible = (sh.caveLit ?? 0) > 0 || light > 0; caveGlow.material.uniforms.uI.value = (sh.caveLit ?? 0) + light * 1.4;
      if (light > 0.01) { const c = F.P(D.far, 880, 520); glowAt(gg, c[0], c[1], 900 * F.SC0, 0.55 * light, [255, 236, 190]); glowAt(gg, c[0], c[1] - 60, 380 * F.SC0, 0.6 * light, [255, 248, 220]);
        const pk = S.world(820, 300, D.peak); lightsOn(P.peak, [{ p: pk, r: 900, c: [1.0, 0.9, 0.7], k: 0.8 * light }]); F.bloom = 0.5 + 0.4 * light; }
      else lightsOn(P.peak, []);
      if (dawn > 0.01) { const c = F.P(D.far, 1000, 600); glowAt(gg, c[0], c[1], 1100 * F.SC0, 0.32 * dawn, [255, 170, 130]); }
      // the hand lantern on the path (no one is drawn): u from the shot's walk plan
      if (sh.walk) { const w = sh.walk; const u = lerp(w.u0, w.u1, ease.inOutSine(clamp((lt - (w.at ?? 0)) / w.dur))); const [px, py] = pathAt(u); const p = F.P(D.peak, px, py); const K = F.K(D.peak);
        handLantern(g, gg, p[0], p[1], 9 * K, t, { swing: 0.18, seed: 3 }); const wp = S.world(px, py, D.peak); lightsOn(P.peak, [{ p: wp, r: 60, c: [1.0, 0.6, 0.3], k: 1.2 }]); F.lights.push({ x: p[0], y: p[1], r: 40, c: [1.0, 0.6, 0.3], k: 0.6 }); }
      if (sh.lamp) { const p = F.P(D.peak, CAVE[0], CAVE[1] + 2); glowAt(gg, p[0], p[1], 14 * F.K(D.peak), 0.8 * sh.lamp * flick(t, 9), [255, 180, 100]); }
      // life: haze drifting across the valley, night birds over the hills at dusk, a thin smoke from the city
      hazeBand(gg, t, { y: F.P(D.city, 300, 640)[1], x0: -200, x1: 1480, n: 7, h: 50, w: 520, a: 0.05 * (1 - light), col: [150, 140, 200], speed: 6, seed: 4 });
      if (mode === 'dusk' || mode === 'dawn') birds(g, t, { x0: -80, x1: 1360, y0: 140, y1: 300, n: 5, seed: 7, size: 6, speed: 18, dir: 1, hz: 2.0, col: [16, 14, 34], a: 0.75 });
      { const c = F.P(D.city, 260, 625); smoke(g, t, c[0], c[1], { n: 7, rise: 80, wind: 12, r0: 3, r1: 18, a: 0.12, col: [120, 110, 150], life: 9, seed: 2 }); }
      motes(gg, t, { x0: 0, y0: 380, x1: 1280, y1: 720 }, { n: 12, col: [200, 200, 255], a: 0.16, size: 1.0, seed: 21, drift: [4, -2] });
      F.amb = [0.92, 0.92, 1.0];
    },
  };
}
