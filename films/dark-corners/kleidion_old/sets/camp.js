// SET camp: Samuel's Bulgarian camp on a hillside at night: tents, a big fire, many small fires up the slope, red banners, and across
// the valley the cooler lights of the Byzantine camp. Samuel stands by the fire as a tall cloaked silhouette.
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged, clamp, lerp, smoothstep, ease, noise1, rng, WARM, det, bump, igniteEnv, flick, fireFlick, tintAll, lightsOn, nn } from './common.js';
import { paintSky, paintRange, pineTree, paintFog, paintTufts, paintRocks } from '../paint.js';
import { person, banner, glowAt, torch, embers, hash1, PAL, STRIDE } from '../figs.js';

function tent(C, x, yb, w, h, col, lit, door = true) {
  const g = C.g, R = C.R; const p = new Path2D(); p.moveTo(x - w / 2, yb); p.quadraticCurveTo(x - w * 0.22, yb - h * 0.55, x + (R() - 0.5) * 3, yb - h); p.quadraticCurveTo(x + w * 0.22, yb - h * 0.55, x + w / 2, yb); p.closePath();
  g.fillStyle = rgba(col); g.fill(p); g.save(); g.clip(p); const gr = g.createLinearGradient(x - w / 2, 0, x + w / 2, 0); gr.addColorStop(0, rgba(lit, 0.5)); gr.addColorStop(0.5, rgba(col, 0)); gr.addColorStop(1, rgba([0, 0, 0], 0.35)); g.fillStyle = gr; g.fillRect(x - w, yb - h - 2, w * 2, h + 4);
  g.strokeStyle = rgba(mul(col, 0.6), 0.6); g.lineWidth = Math.max(0.8, w * 0.01); for (let i = -3; i <= 3; i++) { g.beginPath(); g.moveTo(x, yb - h); g.lineTo(x + i * w * 0.15, yb); g.stroke(); } g.restore();
  if (door) { g.fillStyle = rgba(hex('#0b0810')); g.beginPath(); g.moveTo(x - w * 0.09, yb); g.lineTo(x - w * 0.05, yb - h * 0.34); g.lineTo(x + w * 0.05, yb - h * 0.34); g.lineTo(x + w * 0.09, yb); g.closePath(); g.fill(); }
  g.strokeStyle = rgba(mul(col, 0.5)); g.lineWidth = Math.max(1.2, w * 0.014); g.beginPath(); g.moveTo(x, yb - h); g.lineTo(x, yb - h - h * 0.12); g.stroke();
}

export default function camp(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { sky: 6000, peaks: 2400, far: 900, mid: 420, near: 130, fg: 50 }; const planes = {}; const fires = { far: [], mid: [] };
  { const r = cover(D.sky); const C = new Canvas(r, { seed: 811 });
    paintSky(C, { stops: [[-500, hex('#060820')], [0, hex('#0b0f33')], [300, hex('#161c4e')], [500, hex('#2a2f68')], [600, hex('#44447c')], [680, hex('#5d5388')]], glow: { x: 560, y: 650, rx: 600, ry: 200, col: hex('#8a6a8a'), a: 0.4 },
      clouds: [{ y: 180, h: 12, x0: -300, x1: 1000, col: hex('#10143c'), lit: hex('#2a3070'), litA: 0.5, sy: 0.03 }, { y: 420, h: 9, x0: -100, x1: 1000, col: hex('#222862'), lit: hex('#5a5090'), litA: 0.6, thr: 0.5, sy: 0.04 }] });
    const R = rng(8111); for (let i = 0; i < 160; i++) { const x = lerp(r[0], r[2], R()), y = lerp(r[1], 560, R() * R()); C.g.fillStyle = rgba([220, 225, 255], 0.25 + R() * 0.6); C.g.beginPath(); C.g.arc(x, y, 0.5 + R() * 1.0, 0, 7); C.g.fill(); }
    C.mottle({ amt: 0.05 }); planes.sky = S.plane('sky', D.sky, r, C.c); }
  { const r = cover(D.peaks); r[1] = Math.max(r[1], 250); r[3] = Math.min(r[3], 760); const C = new Canvas(r, { seed: 821 });
    paintRange(C, { ridge: (x) => 640 - bump(x, 160, 190, 200) - bump(x, 460, 140, 150) - bump(x, 660, 120, 100) - 30 * ridged(x * 0.0065, 4, 5), top: hex('#232a58'), mid: hex('#2a3062'), base: hex('#343a70'), fall: 190, light: { dir: -1, col: hex('#4a5088'), amt: 0.4 }, shade: 0.18, haze: { col: hex('#3a3f78'), y0: 580, y1: 700, a: 0.6 }, snow: { y: 480, col: hex('#7a82b0'), amt: 0.7 }, rim: hex('#7a78aa') });
    C.mottle({ amt: 0.05 }); planes.peaks = S.plane('peaks', D.peaks, r, C.c); }
  // the Byzantine camp on the far ridge: a string of cool lights, purple pennants
  { const r = cover(D.far); r[1] = Math.max(r[1], 520); r[3] = Math.min(r[3], 800); const C = new Canvas(r, { seed: 831 }); const R = rng(8311);
    const ridge = (x) => 690 + 12 * Math.sin(x * 0.01) - bump(x, 520, 150, 30) + det(x, 8, 3, 6);
    paintRange(C, { ridge, top: hex('#262b5c'), mid: hex('#1e2350'), base: hex('#171b40'), fall: 100, light: { dir: -1, col: hex('#363c78'), amt: 0.3 }, rim: hex('#5a5f98'), sizes: 0.9, haze: { col: hex('#3a3f78'), y0: 740, y1: 800, a: 0.5 } });
    for (let i = 0; i < 26; i++) { const x = lerp(r[0] + 20, r[2] - 20, R()); const yb = ridge(x) + 6 + R() * 26; tent(C, x, yb, 22 + R() * 12, 14 + R() * 8, hex('#1b1e46'), hex('#4a4a88'), false); fires.far.push([x + (R() - 0.5) * 20, yb + 2]); }
    C.mottle({ amt: 0.05 }); planes.far = S.plane('far', D.far, r, C.c); }
  { const r = cover(D.mid); r[1] = Math.max(r[1], 640); r[3] = Math.min(r[3], 940); const C = new Canvas(r, { seed: 841 }); const R = rng(8411);
    const ridge = (x) => 800 + 22 * Math.sin(x * 0.008 + 1) + det(x, 10, 4, 7);
    paintRange(C, { ridge, top: hex('#1c2048'), mid: hex('#15193a'), base: hex('#10132e'), fall: 150, light: { dir: -1, col: hex('#2a3068'), amt: 0.25 }, rim: hex('#4a4a88'), sizes: 1.0 });
    for (let i = 0; i < 18; i++) { const x = lerp(r[0] + 20, r[2] - 20, R()); const yb = ridge(x) + 18 + R() * 70; tent(C, x, yb, 34 + R() * 24, 24 + R() * 14, hex('#1e1c34'), hex('#6a4a50')); fires.mid.push([x + 30 + R() * 20, yb + 6]); }
    C.mottle({ amt: 0.05 }); planes.mid = S.plane('mid', D.mid, r, C.c); }
  { const r = cover(D.near, 40); r[1] = Math.max(r[1], 860); const C = new Canvas(r, { seed: 851 }); const R = rng(8511); const g = C.g;
    const ridge = (x) => 950 + 10 * Math.sin(x * 0.007) + det(x, 8, 3, 9);
    paintRange(C, { ridge, top: hex('#1d1c34'), mid: hex('#17162a'), base: hex('#0f0e1c'), fall: 300, light: { dir: -1, col: hex('#3a2c3c'), amt: 0.25 }, rim: hex('#6a4a50'), sizes: 1.2 });
    // trampled ground around the fire
    C.strokes({ n: 120, box: [150, 1040, 600, 1180], color: () => hex('#2a2226'), angle: () => (R() - 0.5) * 0.2, len: [20, 60], wid: [6, 12], alpha: [0.4, 0.7], jv: 0.1 });
    for (const [x, yb, w, h, col] of [[90, 1000, 200, 250, '#241c36'], [610, 980, 190, 230, '#2a1c30'], [330, 940, 130, 160, '#211a30'], [520, 960, 110, 140, '#1e1a2e'], [-10, 1130, 240, 300, '#1c1628'], [700, 1150, 250, 300, '#1a1426']]) tent(C, x, yb, w, h, hex(col), hex('#9a5a4a'));
    // logs, a spit, bundles
    for (let i = 0; i < 6; i++) { g.save(); g.translate(300 + (R() - 0.5) * 90, 1128 + R() * 16); g.rotate((R() - 0.5) * 0.9); g.fillStyle = rgba(hex('#1a1210')); g.fillRect(-26, -4, 52, 8); g.fillStyle = rgba(hex('#5a3a28'), 0.5); g.fillRect(-26, -4, 52, 2); g.restore(); }
    for (let i = 0; i < 28; i++) { const x = lerp(r[0], r[2], R()), y = lerp(1000, 1300, R()); const s = 3 + R() * 6; C.dab(x, y, -0.3, s * 2, s, hex('#0d0c18'), 0.9, 0.2); }
    paintTufts(C, { x0: r[0], x1: r[2], base: (x) => 1250 + 20 * Math.sin(x * 0.02), step: 16, h0: 14, h1: 32, col: hex('#0a0914'), blades: 5, jitter: 10 });
    C.mottle({ amt: 0.05 }); planes.near = S.plane('near', D.near, r, C.c); }
  { const r = cover(D.fg, 40); r[1] = Math.max(r[1], 1080); const C = new Canvas(r, { seed: 861 });
    paintRocks(C, { rocks: [{ x: 0, y: 1300, rx: 220, ry: 100 }, { x: 740, y: 1310, rx: 240, ry: 110 }], col: hex('#06060e'), lit: hex('#241c30'), litA: 0.4, blur: 3 }); planes.fg = S.plane('fg', D.fg, r, C.c); }
  tintAll(S, 1);
  const farGlow = fires.far.map(([x, y]) => S.glow(x, y, D.far, 26, { color: [0.62, 0.7, 1.0], core: 140 }, planes.far)); // cool lights across the valley
  const midGlow = fires.mid.map(([x, y]) => S.glow(x, y, D.mid, 40, { color: [1.0, 0.55, 0.22], core: 120 }, planes.mid));
  const FIRE = { x: 330, y: 1126 }; const SAM = { x: 478, y: 1146, h: 330 };
  return {
    planes, D,
    update(F) {
      const t = F.t, sh = F.shot, g = F.g, S_ = F.S; const fl = fireFlick(t, 1); const ign = (i, base = 0) => clamp(igniteEnv(t, (sh.fireT0 ?? 0) + base + i * (sh.fireStep ?? 0.05), i), 0, 1.5);
      const lit = sh.lit ?? 1; const dim = sh.dim ?? 1;
      farGlow.forEach((gm, i) => { const on = sh.far === false ? 0 : (sh.farStagger ? ign(i, sh.farT0 ?? 0) : 1); gm.visible = on > 0.01; gm.material.uniforms.uI.value = 0.9 * on * flick(t, i * 1.3) * dim; });
      midGlow.forEach((gm, i) => { const on = sh.farStagger ? ign(i, (sh.farT0 ?? 0) + 0.4) : 1; gm.visible = on > 0.01; gm.material.uniforms.uI.value = 0.9 * on * flick(t, i * 2.1) * dim * lit; });
      const fp = F.P(D.near, FIRE.x, FIRE.y), K = F.K(D.near, FIRE.x, FIRE.y); const gg = F.glow();
      // big fire: logs aflame, flames drawn as layered teardrops, glow, sparks
      const fa = lit * dim;
      if (fa > 0.01) { for (let k = 0; k < 7; k++) { const a = (k - 3) * 0.28; const hf = (70 + 36 * Math.cos(k * 1.1)) * K * (0.85 + 0.3 * fireFlick(t, k)) * fa; const sw = Math.sin(t * 7 + k * 1.9) * 7 * K; const x = fp[0] + (k - 3) * 11 * K;
          g.fillStyle = rgba([255, 140, 50], 0.9); g.beginPath(); g.moveTo(x - 12 * K, fp[1]); g.quadraticCurveTo(x - 14 * K + sw * 0.3, fp[1] - hf * 0.55, x + sw, fp[1] - hf); g.quadraticCurveTo(x + 14 * K + sw * 0.3, fp[1] - hf * 0.5, x + 12 * K, fp[1]); g.fill();
          g.fillStyle = rgba([255, 215, 120], 0.95); g.beginPath(); g.moveTo(x - 6 * K, fp[1]); g.quadraticCurveTo(x - 7 * K + sw * 0.2, fp[1] - hf * 0.4, x + sw * 0.6, fp[1] - hf * 0.66); g.quadraticCurveTo(x + 7 * K, fp[1] - hf * 0.35, x + 6 * K, fp[1]); g.fill(); }
        glowAt(gg, fp[0], fp[1] - 50 * K, 120 * K, 0.9 * fa * fl); glowAt(gg, fp[0], fp[1] - 60 * K, 520 * K, 0.32 * fa * fl, [255, 130, 60]);
        embers(gg, t, { x0: fp[0] - 40 * K, y0: fp[1] - 330 * K, x1: fp[0] + 40 * K, y1: fp[1] - 40 * K }, 36, { size: 1.6 * K + 0.5, col: [255, 170, 80], a: 0.9, wind: 14, rise: 1, seed: 2 });
        F.lights.push({ x: fp[0], y: fp[1] - 70 * K, r: 430 * K, c: WARM, k: 1.4 * fa * fl });
        const fw = S_.world(FIRE.x, FIRE.y - 60, D.near); lightsOn(planes.near, [{ p: fw, r: 240 * D.near / S_.f * 1.0, c: WARM, k: 2.6 * fa * fl }]); lightsOn(planes.fg, []); }
      // figures around the fire: sitting men (low silhouettes), Samuel standing
      if (sh.people !== false) {
        const sitters = [[250, 1160], [405, 1170], [200, 1140], [455, 1150], [150, 1176]];
        for (let i = 0; i < sitters.length; i++) { const p = F.P(D.near, sitters[i][0], sitters[i][1]); const hh = 150 * K; g.fillStyle = rgba(hex('#100c18')); g.beginPath(); g.moveTo(p[0] - 0.2 * hh, p[1]); g.quadraticCurveTo(p[0] - 0.22 * hh, p[1] - 0.45 * hh, p[0], p[1] - 0.55 * hh); g.quadraticCurveTo(p[0] + 0.22 * hh, p[1] - 0.45 * hh, p[0] + 0.2 * hh, p[1]); g.fill(); g.beginPath(); g.arc(p[0] + 0.02 * hh, p[1] - 0.66 * hh, 0.07 * hh, 0, 7); g.fill(); }
        if (!sh.noSamuel) { const p = F.P(D.near, SAM.x, SAM.y); const h = SAM.h * K; const sf = F.P(D.near, FIRE.x, FIRE.y - 60);
          person(g, { x: p[0], y: p[1], h, face: -1, ph: 0, walk: 0, col: hex('#241830'), col2: hex('#3a2848'), dark: hex('#140e1c'), hood: false, skinCol: hex('#140e1c'), crown: true, cape: hex('#5a1c24'), head: 0.02 * Math.sin(t * 0.7), hem: 0.08, warm: { x: sf[0], y: sf[1], r: 380 * K, a: 0.28 * fa } }); }
      }
      // banners
      if (sh.banners !== false) for (const [bx, by, h, dir, seed] of [[150, 1000, 360, 1, 1], [560, 976, 330, -1, 2]]) { const p = F.P(D.near, bx, by); banner(g, { x: p[0], y: p[1], h: h * K, w: 130 * K, t, dir, col: PAL.red, colLit: PAL.redLit, trim: hex('#d8b868'), emblem: 'none', seed, amp: 0.1 }); }
      F.amb = [0.9, 0.85, 0.95]; F.bloom = 0.55;
      tintAll(S_, 0.9 * dim + 0.05, [1, 1, 1.05]);
    },
  };
}
