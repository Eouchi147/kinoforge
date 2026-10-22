// SET sky: the lantern sky over dark hills. "title": one lantern rises alone (the series motif). "full": thirty lanterns hang and
// drift at different depths (the thirty nights), slowly rising. "dawn": the same sky as morning comes up behind the hills
// (Eid morning): stars and lanterns fade, the horizon warms.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, rng, ease, WARM, tintAll, lightsOn, glowAt, motes, flick, nightSky, makeStars, drawStars, fanous, glowLantern, paintRange, paintFog, paintTufts, ridged, paintSky } from '../lib.js';

export default function sky(S, cams) {
  const cover = (D, m = 50) => S.cover(D, cams, m); const D = { sky: 4000, far: 1200, hills: 160, fg: 30 }; const planes = {};
  { const r = cover(D.sky, 80); const C = new Canvas(r, { seed: 1301 }); nightSky(C, { stops: [[-1600, '#02030a'], [-400, '#050818'], [100, '#0b1334'], [400, '#18204c'], [560, '#26305e']], glow: { x: 640, y: 520, rx: 1000, ry: 220, col: hex('#3c3c70'), a: 0.4 } }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.sky - 100, 80); const C = new Canvas(r, { seed: 1302 });
    paintSky(C, { stops: [[-1600, hex('#1a2a5a')], [-300, hex('#3a5a96')], [150, hex('#7a8ab8')], [380, hex('#d8a890')], [520, hex('#f4c890')], [620, hex('#ffe0b0')]], glow: { x: 760, y: 560, rx: 600, ry: 160, col: hex('#fff0c8'), a: 0.6 },
      clouds: [{ y: 260, h: 12, x0: -600, x1: 1800, col: hex('#8a7aa0'), lit: hex('#ffd0a0'), litA: 0.8, thr: 0.55, sy: 0.03 }, { y: 80, h: 14, x0: 200, x1: 2200, col: hex('#6a78a8'), lit: hex('#f0c0b0'), litA: 0.6, thr: 0.58, sy: 0.03 }], n: 0.8 });
    planes.dawn = S.plane('dawn', D.sky - 100, r, C.c); planes.dawn.material.uniforms.uOpacity.value = 0; }
  { const r = cover(D.far, 60); r[1] = Math.max(r[1], 250); const C = new Canvas(r, { seed: 1303 });
    paintRange(C, { ridge: (x) => 520 + 40 * (ridged(x * 0.002, 4, 3) - 0.5) + 20 * Math.sin(x * 0.003), top: hex('#1a1d40'), mid: hex('#141834'), base: hex('#0e1028'), fall: 160, light: { dir: 1, col: hex('#3a3c6c'), amt: 0.3 }, haze: { col: hex('#262a56'), y0: 520, y1: 640, a: 0.5 } });
    planes.far = S.plane('far', D.far, r, C.c); }
  const homes = []; { const r = cover(D.hills, 60); r[1] = Math.max(r[1], 350); const C = new Canvas(r, { seed: 1304 }); const g = C.g; const ridge = (x) => 610 + 30 * (ridged(x * 0.004, 3, 8) - 0.5) + 25 * Math.sin(x * 0.0045 + 2);
    paintRange(C, { ridge, top: hex('#121426'), mid: hex('#0e1020'), base: hex('#080a16'), fall: 100, light: { dir: 1, col: hex('#2a2c50'), amt: 0.25 } });
    const R = rng(5); for (let i = 0; i < 26; i++) { const x = lerp(r[0] + 40, r[2] - 40, R()); const yb = ridge(x) + 8 + R() * 30; const w = 22 + R() * 30, h = 14 + R() * 16; g.fillStyle = rgba(mixc(hex('#16162a'), hex('#22223a'), R())); g.fillRect(x - w / 2, yb - h, w, h); if (R() < 0.45) homes.push([x + (R() - 0.5) * w * 0.4, yb - h * 0.5, R() * 9]); }
    paintTufts(C, { x0: r[0], x1: r[2], base: ridge, step: 7, h0: 6, h1: 16, col: hex('#0c0e1c'), blades: 4 });
    planes.hills = S.plane('hills', D.hills, r, C.c); planes.hills.material.uniforms.uSway.value.set(0.0008, 0.0, 14); }
  { const r = cover(D.fg, 60); r[1] = Math.max(r[1], 500); const C = new Canvas(r, { seed: 1305 }); paintTufts(C, { x0: r[0], x1: r[2], base: (x) => 760 + 16 * Math.sin(x * 0.01), step: 6, h0: 30, h1: 90, col: hex('#06070e'), blades: 6, lean: 0.1 }); C.blur(1.5); planes.fg = S.plane('fg', D.fg, r, C.c); planes.fg.material.uniforms.uSway.value.set(0.004, 0.0, 6); }
  const stars = makeStars(1306, [-1500, -2200, 2800, 470], 420, 2.0);
  // thirty lanterns at depths 260..900 m, spread over the sky; each with its own drift
  const R = rng(1307); const LANT = Array.from({ length: 30 }, (_, i) => ({ D: lerp(260, 900, R()), x: lerp(80, 1200, (i + R()) / 30), y: lerp(60, 430, R()), ph: R() * 6.28, sp: 0.6 + R() * 0.8, i }));
  LANT.sort((a, b) => b.D - a.D);
  return {
    update(F) {
      const t = F.t, g = F.g, sh = F.shot; const gg = F.glow();
      const dawn = sh.mode === 'dawn' ? ease.inOutSine(smoothstep(sh.dawn[0], sh.dawn[1], t)) : 0;
      planes.dawn.material.uniforms.uOpacity.value = dawn;
      tintAll(S, lerp(0.45, 0.75, dawn), [1, 1, 1], (p) => p === planes.dawn); planes.dawn.material.uniforms.uTint.value.set(lerp(0.5, 0.95, dawn), lerp(0.5, 0.9, dawn), lerp(0.5, 0.85, dawn));
      planes.sky.material.uniforms.uTint.value.set(0.8, 0.82, 0.96);
      drawStars(F, D.sky, stars, 0.95 * (1 - dawn));
      for (const [x, y, s] of homes) { const p = F.P(D.hills, x, y); const k = flick(t, s) * (1 - 0.7 * dawn); glowAt(gg, p[0], p[1], 14, 0.35 * k, [255, 180, 100]); glowAt(gg, p[0], p[1], 2.5, 0.9 * k, [255, 226, 160]); }
      if (sh.mode === 'title') {
        const u = ease.inOutSine(smoothstep(sh.rise[0], sh.rise[1] + 6, t)); const x = 640 + 14 * Math.sin(t * 0.5), y = lerp(640, 470, u); const p = F.P(320, x, y); const s = 26 * F.K(320, x, y);
        fanous(g, p[0], p[1], s, 1, t, 3, { sway: 0.04 }); glowLantern(gg, p[0], p[1], s, 1, t, 3, 1.3); F.lights.push({ x: p[0], y: p[1], r: 200, c: WARM, k: 0.5 });
      } else {
        for (const L of LANT) { const rise = (t - (sh.fillFrom ?? sh.t0)) * 2.2 * L.sp; const x = L.x + 10 * Math.sin(t * 0.3 * L.sp + L.ph), y = L.y - rise - 30 * dawn; const p = F.P(L.D, x, y); const K = F.K(L.D, x, y); const s = 30 * K * (380 / L.D);
          if (p[1] < -60 || p[1] > 800) continue; const vis = 1 - smoothstep(0.35, 0.85, dawn); if (vis <= 0.01) continue; g.save(); g.globalAlpha = vis;
          fanous(g, p[0], p[1], s, 1, t, L.i + 40, { sway: 0.05 }); g.restore(); glowLantern(gg, p[0], p[1], s, vis, t, L.i + 40, 1.1); }
        lightsOn(planes.hills, LANT.slice(-6).map((L) => ({ p: S.world(L.x, L.y + 160, D.hills), r: 40, c: WARM, k: 0.35 * (1 - dawn) })));
      }
      if (dawn > 0) { const p = F.P(D.sky - 100, 760, 600); glowAt(gg, p[0], p[1], 900, 0.18 * dawn, [255, 200, 140]); }
      motes(gg, t, { x0: 0, y0: 420, x1: 1280, y1: 720 }, { n: 18, col: [214, 236, 150], a: 0.4 * (1 - dawn), size: 1.3, seed: 81, drift: [3, -1] });
      F.amb = [lerp(0.95, 1.0, dawn), lerp(0.95, 0.96, dawn), 1.0]; F.bloom = 0.5; F.hal = 0.25;
    },
  };
}
