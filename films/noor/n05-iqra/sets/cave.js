// SET cave: inside Hira, looking out through its mouth over the night valley. Rough rock walls frame the opening; on the floor a
// woven mat, a leather water skin, a little cloth with dates and a small clay oil lamp. Nobody is in the frame: the place he
// has just sat in, or the camera where he sits. Modes: 'dusk' (no lamp, cool light from outside), 'night' (the lamp burns),
// 'light' (the mouth and the sky fill with white-gold light that spills over the walls), 'pulses' (that light breathes three times).
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, ease, rng, det, bump, lightsOn } from './common.js';
import { paintSky, paintRange, ridged } from '../paint.js';
import { motes, hazeBand } from '../ambient.js';
import { glowAt, stars, flick, hash1 } from '../fx.js';

const MOUTH = (a) => { const r = 1 + 0.16 * Math.sin(a * 3 + 1) + 0.09 * Math.sin(a * 7 + 2) + 0.05 * Math.sin(a * 13); return [640 + Math.cos(a) * 270 * r, 330 + Math.sin(a) * 190 * r * (Math.sin(a) > 0 ? 0.9 : 1.15)]; };
const LAMP = [470, 598], DATES = [760, 640], SKIN = [930, 600];

export default function cave(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, far: 2800, city: 1700, wall: 170, floor: 130, fg: 70 }; const P = {}; const city = [];
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 7101 });
    paintSky(C, { stops: [[-600, hex('#04060f')], [100, hex('#0a0e2a')], [330, hex('#161a46')], [440, hex('#2e2c5e')], [520, hex('#5a466c')]], glow: { x: 700, y: 520, rx: 700, ry: 160, col: hex('#8a6878'), a: 0.4 } });
    const R = rng(71011); for (let i = 0; i < 380; i++) { const x = lerp(r[0], r[2], R()), y = lerp(r[1], 430, Math.pow(R(), 1.2)); const b = R(); C.g.fillStyle = rgba([215, 222, 255], 0.2 + b * 0.55); C.g.beginPath(); C.g.arc(x, y, 0.4 + b * 0.8, 0, 7); C.g.fill(); }
    P.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.far); r[1] = Math.max(r[1], 300); const C = new Canvas(r, { seed: 7102 });
    paintRange(C, { ridge: (x) => 470 - bump(x, 380, 200, 50) - bump(x, 900, 240, 70) - 26 * ridged(x * 0.006, 4, 4), top: hex('#1a1d44'), mid: hex('#15183a'), base: hex('#101230'), fall: 100, light: { dir: -1, col: hex('#363670'), amt: 0.3 }, rim: hex('#6a5a86'), haze: { col: hex('#2a2a5a'), y0: 470, y1: 560, a: 0.5 } });
    P.far = S.plane('far', D.far, r, C.c); }
  { const r = cover(D.city); r[1] = Math.max(r[1], 420); const C = new Canvas(r, { seed: 7103 }); const R = rng(71031);
    const ridge = (x) => 520 + 8 * Math.sin(x * 0.007) + det(x, 5, 2, 1);
    paintRange(C, { ridge, top: hex('#17183a'), mid: hex('#131432'), base: hex('#0f102a'), fall: 80, sizes: 0.7, light: { dir: -1, col: hex('#262650'), amt: 0.2 } });
    for (let i = 0; i < 200; i++) { const x = lerp(380, 900, R()); const y = ridge(x) + 4 + R() * 30; C.g.fillStyle = rgba(mixc(hex('#3a3456'), hex('#5a4a5a'), R()), 0.7); C.g.fillRect(x, y, 2 + R() * 5, 1.5 + R() * 2); if (R() < 0.3) city.push([x + 2, y + 1]); }
    P.city = S.plane('city', D.city, r, C.c); }
  // the rock walls around the mouth (the hole is cut out of the painted wall)
  { const r = cover(D.wall, 60); const C = new Canvas(r, { seed: 7104 }); const g = C.g; const n = C.n; const R = rng(71041);
    const hole = new Path2D(); for (let i = 0; i <= 64; i++) { const [x, y] = MOUTH(i / 64 * Math.PI * 2); i ? hole.lineTo(x, y) : hole.moveTo(x, y); } hole.closePath();
    const all = new Path2D(); all.rect(r[0] - 10, r[1] - 10, r[2] - r[0] + 20, r[3] - r[1] + 20);
    const colAt = (x, y) => { const f = n.fbm(x * 0.006, y * 0.006, 4); const facet = n.fbm(x * 0.014 + 3, y * 0.01, 3); let c = mixc(hex('#1c1828'), hex('#2e2838'), f); c = mixc(c, hex('#4a3e4a'), smoothstep(0.55, 0.75, facet) * 0.6); return mul(c, 0.8 + 0.3 * smoothstep(700, 200, Math.hypot(x - 640, y - 330))); };
    underpaint(C, colAt, null, 8);
    C.strokes({ n: C.area / 700, color: colAt, angle: (x, y) => Math.atan2(y - 330, x - 640) + Math.PI / 2 + (R() - 0.5) * 0.7, len: [20, 70], wid: [8, 18], alpha: [0.45, 0.8], jv: 0.08, bend: 0.2 });
    C.strokes({ n: C.area / 1600, color: (x, y) => mul(colAt(x, y), 0.6), angle: () => R() * 6.28, len: [10, 40], wid: [3, 7], alpha: [0.35, 0.6], jv: 0.1, bend: 0.3 });
    // cracks and ledges
    g.strokeStyle = 'rgba(8,6,14,0.55)'; g.lineWidth = 2; for (let i = 0; i < 40; i++) { let x = lerp(r[0], r[2], R()), y = lerp(r[1], r[3], R()); g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (R() - 0.5) * 40; y += 8 + R() * 20; g.lineTo(x, y); } g.stroke(); }
    // a lit lip around the mouth (the night sky catches the edge)
    for (let i = 0; i < 260; i++) { const a = i / 260 * Math.PI * 2; const [x, y] = MOUTH(a); const [x2, y2] = MOUTH(a + 0.03); C.dab(x + (x - 640) * 0.03, y + (y - 330) * 0.03, Math.atan2(y2 - y, x2 - x), 14 + R() * 10, 4 + R() * 5, hex('#5a4e66'), 0.5 + R() * 0.3, 0.1); }
    g.save(); g.globalCompositeOperation = 'destination-out'; g.fill(hole); g.restore();
    C.mottle({ amt: 0.06 }); P.wall = S.plane('wall', D.wall, r, C.c); }
  // the floor: worn rock, a woven mat, the water skin, dates on a cloth, the clay lamp
  { const r = cover(D.floor, 40); r[1] = Math.max(r[1], 520); const C = new Canvas(r, { seed: 7105 }); const g = C.g; const n = C.n; const R = rng(71051);
    const top = (x) => 548 + 14 * Math.sin(x * 0.01) + det(x, 6, 2, 5);
    const fl = new Path2D(); fl.moveTo(r[0] - 10, r[3] + 10); for (let x = r[0] - 10; x <= r[2] + 10; x += 4) fl.lineTo(x, top(x)); fl.lineTo(r[2] + 10, r[3] + 10); fl.closePath();
    const colAt = (x, y) => mul(mixc(hex('#241e2a'), hex('#3a3038'), n.fbm(x * 0.008, y * 0.02, 4)), 0.75 + 0.35 * smoothstep(720, 560, y));
    underpaint(C, colAt, fl, 6); const m = C.mask((gg) => gg.fill(fl));
    C.strokes({ n: C.area / 600, mask: m, color: colAt, angle: () => (R() - 0.5) * 0.4, len: [20, 60], wid: [6, 12], alpha: [0.45, 0.75], jv: 0.08, bend: 0.1 });
    // the mat: a trapezoid in perspective, warp and weft
    const mat = [[520, 600], [880, 600], [960, 712], [440, 712]]; const mp = new Path2D(); mp.moveTo(...mat[0]); for (const p of mat.slice(1)) mp.lineTo(...p); mp.closePath();
    g.fillStyle = rgba(hex('#5a4630')); g.fill(mp); g.save(); g.clip(mp);
    for (let k = 0; k < 40; k++) { const u = k / 40; const y = lerp(600, 712, u * u * 0.4 + u * 0.6); g.strokeStyle = rgba(k % 2 ? hex('#7a6040') : hex('#4a3826'), 0.8); g.lineWidth = 1.6 + u * 1.4; g.beginPath(); g.moveTo(300, y); g.lineTo(1100, y); g.stroke(); }
    for (let k = 0; k < 36; k++) { const u = k / 36; g.strokeStyle = rgba(hex('#3a2a1c'), 0.45); g.lineWidth = 1; g.beginPath(); g.moveTo(lerp(520, 880, u), 600); g.lineTo(lerp(440, 960, u), 712); g.stroke(); }
    g.restore(); g.strokeStyle = rgba(hex('#2a1e14'), 0.8); g.lineWidth = 2.5; g.stroke(mp);
    // water skin: a soft leather bag lying on its side, a tied neck
    g.fillStyle = rgba(hex('#3a2a20')); g.beginPath(); g.ellipse(SKIN[0], SKIN[1], 62, 34, -0.2, 0, 7); g.fill(); g.beginPath(); g.ellipse(SKIN[0] + 64, SKIN[1] - 18, 16, 9, -0.6, 0, 7); g.fill();
    g.fillStyle = rgba(hex('#6a4a34'), 0.6); g.beginPath(); g.ellipse(SKIN[0] - 14, SKIN[1] - 14, 34, 11, -0.25, 0, 7); g.fill(); g.strokeStyle = rgba(hex('#1c140e')); g.lineWidth = 3; g.beginPath(); g.moveTo(SKIN[0] + 52, SKIN[1] - 26); g.lineTo(SKIN[0] + 56, SKIN[1] - 8); g.stroke();
    // a small cloth with dates
    g.fillStyle = rgba(hex('#8a7a5e')); g.beginPath(); g.moveTo(DATES[0] - 56, DATES[1] - 8); g.lineTo(DATES[0] + 52, DATES[1] - 14); g.lineTo(DATES[0] + 66, DATES[1] + 26); g.lineTo(DATES[0] - 62, DATES[1] + 30); g.closePath(); g.fill();
    for (let i = 0; i < 9; i++) { const x = DATES[0] + (hash1(i) - 0.5) * 70, y = DATES[1] + 6 + (hash1(i + 9) - 0.5) * 20; g.fillStyle = rgba(hex('#4a2414')); g.beginPath(); g.ellipse(x, y, 9, 5, hash1(i + 3) * 3, 0, 7); g.fill(); g.fillStyle = rgba(hex('#8a4a2a'), 0.7); g.beginPath(); g.ellipse(x - 2, y - 2, 4, 1.6, hash1(i + 3) * 3, 0, 7); g.fill(); }
    // the clay oil lamp (its flame is drawn per frame)
    g.fillStyle = rgba(hex('#6a4430')); g.beginPath(); g.ellipse(LAMP[0], LAMP[1], 30, 13, 0, 0, 7); g.fill(); g.beginPath(); g.moveTo(LAMP[0] + 20, LAMP[1] - 6); g.lineTo(LAMP[0] + 44, LAMP[1] - 12); g.lineTo(LAMP[0] + 40, LAMP[1] + 2); g.closePath(); g.fill();
    g.fillStyle = rgba(hex('#8a5a3e'), 0.7); g.beginPath(); g.ellipse(LAMP[0] - 4, LAMP[1] - 5, 18, 5, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#1a100a')); g.beginPath(); g.ellipse(LAMP[0], LAMP[1] - 6, 6, 2.5, 0, 0, 7); g.fill();
    C.mottle({ amt: 0.06 }); P.floor = S.plane('floor', D.floor, r, C.c); }
  { const r = cover(D.fg, 40); const C = new Canvas(r, { seed: 7106 }); const g = C.g; const R = rng(71061);
    // out-of-focus rock edges at the top corners and the left side: the cave is small
    for (const [x, y, rx, ry] of [[80, -40, 380, 200], [1240, -30, 360, 190], [-60, 520, 200, 380]]) { g.fillStyle = rgba(hex('#07060c')); g.beginPath(); for (let i = 0; i <= 40; i++) { const a = i / 40 * 6.283; const k = 1 + 0.18 * Math.sin(a * 5 + x) + 0.08 * Math.sin(a * 11); const px = x + Math.cos(a) * rx * k, py = y + Math.sin(a) * ry * k; i ? g.lineTo(px, py) : g.moveTo(px, py); } g.fill(); }
    C.blur(4); P.fg = S.plane('fg', D.fg, r, C.c); }
  const back = S.glow(640, 380, D.far, 1300, { color: [1.0, 0.9, 0.7], core: 5000 }, P.far); const backCore = S.glow(640, 360, D.far, 420, { color: [1.0, 0.97, 0.88], core: 5000 }, P.far);
  const cityGlow = city.slice(0, 40).map(([x, y], i) => S.glow(x, y, D.city, 8 + hash1(i) * 8, { color: [1.0, 0.6, 0.28], core: 160 }, P.city));
  const tw = (pl, k, c = [1, 1, 1]) => pl.material.uniforms.uTint.value.set(k * c[0], k * c[1], k * c[2]);
  return {
    planes: P, D,
    update(F) {
      const t = F.t, lt = F.lt, sh = F.shot, g = F.g, gg = F.glow(); const mode = sh.mode || 'night';
      let light = 0;
      if (mode === 'light') light = ease.inOutSine(clamp((lt - (sh.lightAt ?? 0.5)) / (sh.lightLen ?? 3.5)));
      if (mode === 'pulses') { light = 0.42; for (const p of sh.pulses || []) { const d = t - p; if (d > -0.6 && d < 3) light += 0.45 * Math.exp(-(((d - 0.3) / 0.8) ** 2)); } }
      const dusk = mode === 'dusk' ? 1 : 0; const lampOn = sh.lamp ? 1 : 0; const fl = flick(t, 2);
      tw(P.sky, (dusk ? 1.0 : 0.8) + light * 0.8, [1 + light * 0.6, 1 + light * 0.45, 1.05 + light * 0.1]); tw(P.far, (dusk ? 0.95 : 0.75) + light * 0.6, [1 + light * 0.3, 1 + light * 0.2, 1.05]);
      tw(P.city, 0.8 + light * 0.3); tw(P.wall, (dusk ? 0.55 : 0.42) + light * 0.25, [1, 0.98, 1.05]); tw(P.floor, (dusk ? 0.55 : 0.45) + light * 0.25); tw(P.fg, 1);
      const a = F.P(D.sky, -300, -500), b = F.P(D.sky, 1600, 420); stars(gg, t, [a[0], a[1], b[0], b[1]], { n: 90, seed: 41, a: 0.75 * (1 - light) * (dusk ? 0.5 : 1) });
      cityGlow.forEach((gm, i) => { gm.visible = true; gm.material.uniforms.uI.value = 0.5 * flick(t, i) * (1 - 0.6 * light); });
      // light from the mouth (outside -> in) and from the lamp
      const mouth = S.world(640, 330, D.wall + 200); const lamp = S.world(LAMP[0] + 6, LAMP[1] - 20, D.floor);
      const L = []; if (light > 0.01) L.push({ p: mouth, r: 260, c: [1.0, 0.92, 0.72], k: 2.4 * light });
      if (lampOn) L.push({ p: lamp, r: 60, c: [1.0, 0.55, 0.22], k: 2.2 * fl }); if (dusk) L.push({ p: mouth, r: 220, c: [0.6, 0.55, 0.8], k: 0.7 });
      lightsOn(P.wall, L); lightsOn(P.floor, L);
      back.visible = light > 0.01; back.material.uniforms.uI.value = 0.36 * light; backCore.visible = light > 0.01; backCore.material.uniforms.uI.value = 0.5 * light;
      if (light > 0.01) { F.bloom = 0.5 + 0.45 * light; F.hal = 0.25 + 0.2 * light; }
      if (lampOn) { const p = F.P(D.floor, LAMP[0] + 40, LAMP[1] - 14); const K = F.K(D.floor); const h = 16 * K * fl;
        g.fillStyle = 'rgba(255,170,70,0.95)'; g.beginPath(); g.moveTo(p[0] - 4 * K, p[1]); g.quadraticCurveTo(p[0] - 5 * K, p[1] - h * 0.6, p[0] + Math.sin(t * 6) * 1.5 * K, p[1] - h); g.quadraticCurveTo(p[0] + 5 * K, p[1] - h * 0.5, p[0] + 4 * K, p[1]); g.fill();
        g.fillStyle = 'rgba(255,240,200,0.95)'; g.beginPath(); g.ellipse(p[0], p[1] - h * 0.3, 1.6 * K, h * 0.25, 0, 0, 7); g.fill();
        glowAt(gg, p[0], p[1] - h * 0.4, 40 * K, 0.8 * fl, [255, 180, 90]); glowAt(gg, p[0], p[1] - h * 0.4, 240 * K, 0.22 * fl, [255, 140, 60]); F.lights.push({ x: p[0], y: p[1], r: 300 * K, c: [1.0, 0.55, 0.22], k: 1.0 * fl }); }
      hazeBand(gg, t, { y: F.P(D.city, 640, 520)[1], x0: 300, x1: 1000, n: 5, h: 30, w: 360, a: 0.05 * (1 - light), col: [150, 140, 210], speed: 5, seed: 8 });
      motes(gg, t, { x0: 200, y0: 120, x1: 1080, y1: 700 }, { n: 22, col: light > 0.1 ? [255, 236, 200] : [255, 200, 150], a: 0.18 + 0.4 * light + 0.1 * lampOn, size: 1.2, seed: 13, drift: [3, -2] });
      F.amb = [0.9, 0.88, 0.98];
    },
  };
}
