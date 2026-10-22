// SET sky: the open night over the mountains of Makkah. Used for the title (a lantern rises), the word (the sky fills with
// gold light: the angel's coming is shown only as light), the verse panel (a calm night behind the illuminated frame) and the
// lantern sky at the end (tonight's one lantern rises, carrying the word). Nothing in this set is a person.
import { Canvas, hex, mixc, mul, rgba, clamp, lerp, smoothstep, ease, rng, det, bump, lightsOn } from './common.js';
import { paintSky, paintRange, ridged } from '../paint.js';
import { hazeBand, motes } from '../ambient.js';
import { glowAt, stars, fanous, flick } from '../fx.js';

export default function sky(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, band: 5000, peak: 2400, hills: 700 }; const P = {};
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 6101 });
    paintSky(C, { stops: [[-900, hex('#020308')], [-300, hex('#04060f')], [100, hex('#080b22')], [400, hex('#11153c')], [560, hex('#1e2050')], [680, hex('#33305e')]],
      glow: { x: 640, y: 700, rx: 1000, ry: 220, col: hex('#5a4a70'), a: 0.4 }, clouds: [{ y: 560, h: 10, x0: -400, x1: 1700, col: hex('#191a44'), lit: hex('#4a4070'), litA: 0.5, thr: 0.52, sy: 0.04 }] });
    const R = rng(61011); for (let i = 0; i < 900; i++) { const x = lerp(r[0], r[2], R()), y = lerp(r[1], 600, Math.pow(R(), 1.2)); const b = R(); C.g.fillStyle = rgba([215, 222, 255], 0.15 + b * 0.55); C.g.beginPath(); C.g.arc(x, y, 0.35 + b * 0.85, 0, 7); C.g.fill(); }
    C.mottle({ amt: 0.04 }); P.sky = S.plane('sky', D.sky, r, C.c); }
  // a faint band of the Milky Way across the sky (a soft painted veil on its own plane)
  { const r = cover(D.band); const C = new Canvas(r, { seed: 6102 }); const n = C.n; const R = rng(61021);
    const band = (x, y) => Math.exp(-(((y - (80 + (x - 640) * -0.35)) / 120) ** 2)) * smoothstep(0.35, 0.75, n.fbm(x * 0.004, y * 0.008, 4));
    C.strokes({ n: C.area / 500, mask: band, minMask: 0.05, color: () => hex('#6a6aa0'), angle: () => -0.33 + (R() - 0.5) * 0.2, len: [40, 120], wid: [10, 24], alpha: [0.03, 0.08], aMul: (x, y, m) => m, jv: 0.05 });
    for (let i = 0; i < 700; i++) { const x = lerp(r[0], r[2], R()), y = lerp(r[1], r[3], R()); if (band(x, y) < 0.2) continue; C.g.fillStyle = rgba([220, 225, 255], 0.3 + R() * 0.5); C.g.fillRect(x, y, 1, 1); }
    C.blur(1.2); P.band = S.plane('band', D.band, r, C.c); }
  { const r = cover(D.peak); r[1] = Math.max(r[1], 380); const C = new Canvas(r, { seed: 6103 });
    paintRange(C, { ridge: (x) => 640 - bump(x, 760, 120, 210) - bump(x, 520, 200, 60) - bump(x, 1040, 180, 90) - 20 * ridged(x * 0.01, 4, 2), top: hex('#14163a'), mid: hex('#101230'), base: hex('#0b0c24'), fall: 200, light: { dir: -1, col: hex('#2c2c5c'), amt: 0.35 }, rim: hex('#5a5080'), sizes: 1.0 });
    C.mottle({ amt: 0.05 }); P.peak = S.plane('peak', D.peak, r, C.c); }
  { const r = cover(D.hills); r[1] = Math.max(r[1], 560); const C = new Canvas(r, { seed: 6104 });
    paintRange(C, { ridge: (x) => 680 + 14 * Math.sin(x * 0.005) + det(x, 8, 3, 3), top: hex('#0c0c1e'), mid: hex('#08081a'), base: hex('#060612'), fall: 120, light: { dir: -1, col: hex('#1e1e40'), amt: 0.3 }, rim: hex('#3a3866'), sizes: 1.1 });
    C.mottle({ amt: 0.05 }); P.hills = S.plane('hills', D.hills, r, C.c); }
  const back = S.glow(640, 300, D.sky, 2400, { color: [1.0, 0.76, 0.42], core: 5000 }, P.sky); const backCore = S.glow(640, 300, D.sky, 900, { color: [1.0, 0.95, 0.82], core: 5000 }, P.sky);
  const tw = (pl, k, c = [1, 1, 1]) => pl.material.uniforms.uTint.value.set(k * c[0], k * c[1], k * c[2]);
  return {
    planes: P, D,
    update(F) {
      const t = F.t, lt = F.lt, sh = F.shot, g = F.g, gg = F.glow(); const mode = sh.mode;
      let gold = 0; if (mode === 'word') gold = ease.inOutSine(clamp((lt + 0.2) / 1.2)) * (1 - smoothstep(sh.dur - 0.6, sh.dur, lt) * 0.5);
      tw(P.sky, 0.85 + gold * 0.45, [1 + 0.5 * gold, 1 + 0.35 * gold, 1.05]); tw(P.band, 1 - gold * 0.7); tw(P.peak, 0.85 - gold * 0.3); tw(P.hills, 0.85 - gold * 0.3);
      const a = F.P(D.sky, -700, -700), b = F.P(D.sky, 2000, 520);
      stars(gg, t, [a[0], a[1], b[0], b[1]], { n: 240, seed: 31, a: 0.75 * (1 - gold), big: 0.06 });
      back.visible = gold > 0.01; back.material.uniforms.uI.value = 0.4 * gold; backCore.visible = gold > 0.01; backCore.material.uniforms.uI.value = 0.22 * gold; if (gold > 0.01) F.bloom = 0.5 + 0.3 * gold;
      if (mode === 'verse') { const u = ease.inOutSine(clamp(lt / 3)); glowAt(gg, F.DW / 2, F.DH * 0.53, 640, 0.18 * u, [255, 200, 120]); }
      // the lantern rising: title and end
      if (sh.rise) { const [r0, rl] = sh.rise; const u = ease.inOutSine(clamp((lt - r0) / rl)); const y = lerp(F.DH + 100, mode === 'title' ? F.DH * 0.81 : F.DH * 0.35, u); const x = F.DW / 2 + 30 * Math.sin(lt * 0.35);
        const s = mode === 'title' ? 62 : 96; fanous(g, gg, x, y, s, t, { lit: 1, sway: 0.03 }); F.lanternPos = [x, y, s];
        F.lights.push({ x, y, r: 300, c: [1.0, 0.6, 0.3], k: 0.5 });
        if (mode === 'lantern') { // the warm light it throws on the ridge as it passes
          lightsOn(P.peak, [{ p: S.world(x, y + 120, D.peak), r: 600, c: [1.0, 0.6, 0.3], k: 0.5 * (1 - u) + 0.15 }]); }
      }
      hazeBand(gg, t, { y: F.DH * 0.9, x0: -200, x1: F.DW + 200, n: 6, h: 40, w: 560, a: 0.05, col: [150, 140, 210], speed: 5, seed: 3 });
      motes(gg, t, { x0: 0, y0: F.DH * 0.4, x1: F.DW, y1: F.DH }, { n: 14, col: [255, 210, 160], a: 0.18 + 0.3 * gold, size: 1.1, seed: 9, drift: [3, -4] });
      F.amb = [0.95, 0.92, 1.0];
    },
  };
}
