// SET mountain: Jabal an-Nur at night seen from the valley of Makkah, a steep rocky peak; near its summit a small warm light marks
// the cave of Hira (a light only: no figure). Below, a few lamps in low flat-roofed houses; haze in the valley; stars.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, rng, WARM, tintAll, lightsOn, glowAt, motes, flick, igniteEnv, nightSky, makeStars, drawStars, paintRange, paintFog, paintRocks, ridged } from '../lib.js';

export const peak = (x) => { const d = (x - 690) / 260; return 150 + 300 * (1 - Math.exp(-d * d * 1.3)) + 34 * Math.abs(d) * (ridged(x * 0.012, 3, 9) - 0.5) + 16 * (ridged(x * 0.03, 2, 4) - 0.5); };

export default function mountain(S, cams) {
  const cover = (D, m = 50) => S.cover(D, cams, m); const D = { sky: 4000, far: 1500, peak: 600, hills: 200, fg: 40 }; const planes = {};
  { const r = cover(D.sky, 80); const C = new Canvas(r, { seed: 1001 }); nightSky(C, { stops: [[-1200, '#02030a'], [-100, '#050818'], [260, '#0c1336'], [420, '#1a2050'], [560, '#2a2f5c']], glow: { x: 400, y: 470, rx: 900, ry: 200, col: hex('#3c3a6a'), a: 0.35 } }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.far, 60); r[1] = Math.max(r[1], 250); const C = new Canvas(r, { seed: 1002 });
    paintRange(C, { ridge: (x) => 430 + 50 * (ridged(x * 0.0025, 4, 2) - 0.5) + 25 * Math.sin(x * 0.003 + 1), top: hex('#1a1f44'), mid: hex('#141836'), base: hex('#0e1128'), fall: 180, light: { dir: -1, col: hex('#363b6c'), amt: 0.3 }, haze: { col: hex('#272c56'), y0: 420, y1: 560, a: 0.5 } });
    planes.far = S.plane('far', D.far, r, C.c); }
  { const r = cover(D.peak, 60); r[1] = Math.max(r[1], 100); const C = new Canvas(r, { seed: 1003 });
    paintRange(C, { ridge: peak, top: hex('#2c2a3c'), mid: hex('#1e1d2c'), base: hex('#121220'), fall: 300, light: { dir: -1, col: hex('#56588a'), amt: 0.45 }, shade: 0.25, rim: hex('#7a7aa8'), haze: { col: hex('#22264c'), y0: 470, y1: 600, a: 0.6 }, sizes: 0.8 });
    planes.peak = S.plane('peak', D.peak, r, C.c); }
  // valley haze between the peak and the foothills
  { const r = cover(D.hills + 40, 60); r[1] = Math.max(r[1], 250); const C = new Canvas(r, { seed: 1006 }); paintFog(C, { y: (x) => 520 + 20 * Math.sin(x * 0.005), h: 36, col: hex('#323866'), top: hex('#4c5088'), a: 0.55, density: 0.7 }); planes.fog = S.plane('fog', D.hills + 40, r, C.c); planes.fog.userData.drift = 1.6; }
  // foothills with a few flat-roofed houses and lamps
  const lamps = []; { const r = cover(D.hills, 60); r[1] = Math.max(r[1], 300); const C = new Canvas(r, { seed: 1004 }); const g = C.g; const [x0, y0, x1, y1] = r;
    const ridge = (x) => 560 + 30 * (ridged(x * 0.004, 3, 6) - 0.5) + 18 * Math.sin(x * 0.006);
    paintRange(C, { ridge, top: hex('#1a1a28'), mid: hex('#141420'), base: hex('#0c0c16'), fall: 120, light: { dir: -1, col: hex('#3a3a60'), amt: 0.25 } });
    const R = rng(33); for (let i = 0; i < 46; i++) { const x = lerp(x0 + 40, x1 - 40, R()); const yb = ridge(x) + 14 + R() * 70; const w = 18 + R() * 26, h = 12 + R() * 14;
      g.fillStyle = rgba(mixc(hex('#16141e'), hex('#201c2a'), R())); g.fillRect(x - w / 2, yb - h, w, h); g.fillStyle = rgba(hex('#16141e')); g.fillRect(x - w / 2, yb - h, w, 2.5);
      if (R() < 0.3) { const wx = x + (R() - 0.5) * w * 0.5, wy = yb - h * 0.55; g.fillStyle = rgba(hex('#1a1410')); g.fillRect(wx - 2.5, wy - 3, 5, 6); lamps.push([wx, wy, R() * 10]); } }
    planes.hills = S.plane('hills', D.hills, r, C.c); }
  { const r = cover(D.fg, 60); r[1] = Math.max(r[1], 480); const C = new Canvas(r, { seed: 1005 }); paintRocks(C, { rocks: [{ x: 120, y: 720, rx: 260, ry: 90 }, { x: 1180, y: 740, rx: 300, ry: 100 }], col: hex('#0a0a12'), lit: hex('#2a2c4a'), litA: 0.35, blur: 2 }); planes.fg = S.plane('fg', D.fg, r, C.c); }
  const stars = makeStars(1007, [-1200, -1600, 2500, 460], 320, 2.0); const CAVE = [742, 232];
  return {
    update(F) {
      const t = F.t, g = F.g, sh = F.shot; const gg = F.glow();
      tintAll(S, 0.5); planes.sky.material.uniforms.uTint.value.set(0.78, 0.8, 0.95); planes.fog.material.uniforms.uTint.value.set(0.55, 0.55, 0.65);
      drawStars(F, D.sky, stars, 0.95);
      // the cave: a small warm light high on the peak, brightening gently on "the first words"
      const on = 0.45 + 0.55 * smoothstep(sh.caveOn ?? 1e9, (sh.caveOn ?? 1e9) + 2.5, t); const fl = flick(t, 4); const cp = F.P(D.peak, CAVE[0], CAVE[1]);
      glowAt(gg, cp[0], cp[1], 90 * on, 0.16 * on * fl, [255, 170, 90]); glowAt(gg, cp[0], cp[1], 9, 0.85 * on, [255, 220, 150]);
      lightsOn(planes.peak, [{ p: S.world(CAVE[0], CAVE[1], D.peak), r: 26, c: WARM, k: 1.2 * on * fl }]);
      // house lamps in the valley, each with its own flicker
      for (const [x, y, s] of lamps) { const p = F.P(D.hills, x, y); const k = flick(t, s); glowAt(gg, p[0], p[1], 14, 0.4 * k, [255, 180, 100]); glowAt(gg, p[0], p[1], 3, 0.9, [255, 226, 160]); }
      lightsOn(planes.hills, lamps.slice(0, 8).map(([x, y, s]) => ({ p: S.world(x, y, D.hills), r: 6, c: WARM, k: 0.8 * flick(t, s) })));
      // dust in the cold air
      motes(gg, t, { x0: 0, y0: 300, x1: 1280, y1: 700 }, { n: 16, col: [170, 180, 255], a: 0.25, size: 1.0, seed: 51, drift: [6, -1] });
      F.amb = [0.95, 0.95, 1.0]; F.bloom = 0.5; F.hal = 0.22;
    },
  };
}
