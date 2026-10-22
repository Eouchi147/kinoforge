// Extras that live inside the sea sets: Jamaica on the horizon, the harbour at Black River, the captain with his glass, the ship's name board,
// the hull seen from the water (one rope, one man), rain, and rings on the water.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, rng, noise1 } from '/harness/kit/film.js';
import { setLights } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, underpaint, ridged } from './paint.js';
import { WARM, GLOW, flick, line, paintPerson, drawLantern } from './common.js';
import { SHIP, YH } from './sea.js';

function paintPalm(C, x, yb, h, lean, col, lit) {
  const g = C.g, R = C.R; const tx = x + lean * h, ty = yb - h;
  g.strokeStyle = rgba(col); g.lineCap = 'round'; for (let k = 0; k < 14; k++) { const u0 = k / 14, u1 = (k + 1) / 14; const q = (u) => [lerp(x, tx, u) + Math.sin(u * 2.6) * h * 0.05, lerp(yb, ty, u)]; const a = q(u0), b = q(u1); g.lineWidth = lerp(h * 0.06, h * 0.032, u0); g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.stroke(); }
  for (let k = 0; k < 12; k++) { const a = -Math.PI + (k + 0.5) / 12 * Math.PI + (R() - 0.5) * 0.25; const L = h * (0.42 + R() * 0.2); const ex = tx + Math.cos(a) * L, ey = ty + Math.sin(a) * L * 0.55 + L * 0.42, cx = tx + Math.cos(a) * L * 0.55, cy = ty + Math.sin(a) * L * 0.7 - L * 0.12;
    g.lineWidth = Math.max(1.4, h * 0.014); g.beginPath(); g.moveTo(tx, ty); g.quadraticCurveTo(cx, cy, ex, ey); g.stroke();
    for (let s = 0.15; s < 1; s += 0.075) { const m = 1 - s; const px = m * m * tx + 2 * m * s * cx + s * s * ex, py = m * m * ty + 2 * m * s * cy + s * s * ey; for (const sd of [-1, 1]) C.dab(px, py, Math.atan2(ey - ty, ex - tx) + sd * 1.1 + 0.5, L * 0.2 * (1 - s * 0.5), Math.max(1.2, h * 0.012), mul(col, 0.85 + R() * 0.3), 0.9, 0.1, 0.8); }
    if (lit && R() < 0.5) C.dab(tx + Math.cos(a) * L * 0.5, ty + Math.sin(a) * L * 0.4, a, L * 0.3, 1.4, lit, 0.5, 0.1); }
}

export function buildExtras(ctx) {
  const { S, mood, M, cover, planes, shipG, api, f, D, seed } = ctx; const ex = {};
  if (mood === 'dusk') {
    // Jamaica: a long, hazy island ridge at the horizon. It slides past as the ship sails by.
    { const r = [-300, 560, 1500, 770]; const C = new Canvas(r, { seed: 1601 }); const g = C.g, n = C.n, R = C.R;
      const ridge = (x) => 738 - 92 * Math.exp(-(((x - 330) / 170) ** 2)) - 138 * Math.exp(-(((x - 560) / 120) ** 2)) - 104 * Math.exp(-(((x - 820) / 190) ** 2)) - 52 * Math.exp(-(((x - 60) / 190) ** 2)) - 38 * Math.exp(-(((x - 1080) / 160) ** 2)) - 22 * ridged(x * 0.012, 4, 3) - 5 * ridged(x * 0.05, 3, 4);
      const path = new Path2D(); path.moveTo(r[0], 770); for (let x = r[0]; x <= r[2]; x += 3) path.lineTo(x, ridge(x)); path.lineTo(r[2], 770); path.closePath();
      const col = (x, y) => mixc(mixc(hex('#7a5e8e'), hex('#b0808e'), smoothstep(560, 760, y)), hex('#e4a27c'), 0.35 * smoothstep(700, 770, y)); underpaint(C, col, path, 5); const m = C.mask((gg) => gg.fill(path));
      C.strokes({ n: C.area / 380, mask: m, color: col, angle: (x, y) => 0.7 * (n.fbm(x * 0.02, y * 0.02, 2) > 0.5 ? 1 : -1) + (R() - 0.5) * 0.3, len: [10, 34], wid: [3, 7], alpha: [0.4, 0.7], jv: 0.06 });
      for (let x = r[0]; x < r[2]; x += 5 + R() * 6) C.dab(x, ridge(x) + 3, Math.atan((ridge(x + 5) - ridge(x - 5)) / 10), 10 + R() * 12, 2, hex('#f1b79a'), 0.35, 0.05, 0.6);
      C.blur(0.8); const pl = S.plane('coast', 2600, r, C.c); planes.coast = pl; pl.visible = false; pl.userData.v = 62; }
    // Black River: low shore with palms and a few lit windows, a pier with two lanterns, palms in the foreground
    { const r = [-200, 640, 1000, 830]; const C = new Canvas(r, { seed: 1611 }); const R = C.R, n = C.n;
      const shore = (x) => 770 - 18 * Math.exp(-(((x - 250) / 190) ** 2)) - 26 * Math.exp(-(((x - 620) / 230) ** 2)) - 8 * ridged(x * 0.02, 3, 6);
      const path = new Path2D(); path.moveTo(r[0], 830); for (let x = r[0]; x <= r[2]; x += 3) path.lineTo(x, shore(x)); path.lineTo(r[2], 830); path.closePath();
      const col = (x, y) => mixc(hex('#3a2c4a'), hex('#1b1428'), smoothstep(shore(x), 830, y)); underpaint(C, col, path, 5); const m = C.mask((gg) => gg.fill(path));
      C.strokes({ n: C.area / 240, mask: m, color: col, angle: () => (R() - 0.5) * 0.5, len: [8, 24], wid: [3, 6], alpha: [0.4, 0.7], jv: 0.06 });
      for (let x = r[0] + 20; x < r[2]; x += 18 + R() * 40) paintPalm(C, x, shore(x) + 2, 30 + R() * 42, (R() - 0.5) * 0.25, hex('#1a1226'), hex('#7a5478'));
      for (let i = 0; i < 7; i++) { const x = lerp(10, 760, R()); const y = shore(x) + 7; C.g.fillStyle = rgba(hex('#17101f')); C.g.fillRect(x - 6, y - 8, 12, 9); }
      planes.shore = S.plane('shore', 900, r, C.c); planes.shore.visible = false; ex.shoreLights = Array.from({ length: 7 }, (_, i) => ({ x: lerp(20, 740, (i + 0.5) / 7 + (R() - 0.5) * 0.06), y: 770 - 10 })); }
    { const r = cover(70, 80); const C = new Canvas(r, { seed: 1621 }); const R = C.R; const dark = hex('#0d0914'), lit = hex('#7a4a58');
      paintPalm(C, 36, 1180, 420, 0.2, dark, lit); paintPalm(C, -30, 1230, 330, 0.36, mul(dark, 1.1), lit); paintPalm(C, 700, 1200, 260, -0.2, dark, lit);
      C.blur(1.6); planes.palms = S.plane('palms', 70, r, C.c); planes.palms.visible = false; }
    { const r = [380, 820, 900, 1000]; const C = new Canvas(r, { seed: 1631 }); const g = C.g, R = C.R; g.fillStyle = rgba(hex('#120c18')); g.fillRect(380, 900, 520, 22); for (let x = 382; x < 900; x += 5 + R() * 5) C.dab(x, 902, 0, 12, 2.2, hex('#a87a70'), 0.35, 0, 0.4);
      for (const x of [430, 560, 690, 820]) { g.fillStyle = rgba(hex('#0c0810')); g.fillRect(x - 5, 902, 10, 96); } for (const x of [500, 780]) { g.fillStyle = rgba(hex('#0c0810')); g.fillRect(x - 2, 830, 4, 74); g.fillStyle = rgba(hex('#20151a')); g.fillRect(x - 9, 826, 18, 24); }
      C.blur(0.7); planes.pier = S.plane('pier', 110, r, C.c); planes.pier.visible = false; ex.pier = [[500, 842], [780, 842]]; }
    ex.pierGlow = ex.pier.map(([x, y]) => { const gm = S.glow(x, y, 110, 70, { color: GLOW, core: 30 }, planes.pier); return gm; });
    ex.shoreGlow = ex.shoreLights.map((p) => S.glow(p.x, p.y, 900, 22, { color: GLOW, core: 40 }, planes.shore));
    // the captain on the poop with his glass (a child of the ship, so he rolls with it)
    { const r = [90, 600, 230, 706]; const C = new Canvas(r, { seed: 1641 }); paintPerson(C, { x: 158, yb: 698, h: 66, face: 1, hat: 'tricorn', coat: 0.8, flare: 1.1, col: hex('#0b0810'), rim: hex(M.rim), rimSide: -1, arms: [{ s: [11, 3], e: [24, -6], h: [33, -15] }, { s: [-10, 3], e: [-13, 18], h: [-10, 32] }] });
      const pl = S.plane('captain', 170, r, C.c); S.group.remove(pl); shipG.add(pl); ex.captain = pl; pl.visible = false; }
  }
  if (mood === 'moon') {
    // the hull seen from the water: a dark wall to the rail, a lantern on the rail, rope drawn live
    { const r = cover(60, 60); const C = new Canvas(r, { seed: 1651 }); const g = C.g, R = C.R, n = C.n; const [x0, , x1] = r; const top = (x) => 330 + 10 * Math.sin(x * 0.003 + 0.4);
      const path = new Path2D(); path.moveTo(x0 - 10, 1060); for (let x = x0 - 10; x <= x1 + 10; x += 6) path.lineTo(x, top(x)); path.lineTo(x1 + 10, 1060); path.closePath();
      const col = (x, y) => mixc(hex('#1a2040'), hex('#080b19'), smoothstep(top(x), 1030, y)); underpaint(C, col, path, 6); const m = C.mask((gg) => gg.fill(path));
      C.strokes({ n: C.area / 700, mask: m, color: col, angle: () => (R() - 0.5) * 0.04, len: [60, 200], wid: [4, 9], alpha: [0.4, 0.7], jv: 0.08, bend: 0.01 });
      for (const y of [452, 560, 700, 860]) for (let x = x0; x < x1; x += 9 + R() * 8) C.dab(x, y + (R() - 0.5) * 3, 0, 20 + R() * 30, 2.2, hex('#05060f'), 0.7, 0, 0.5);
      for (const y of [500]) for (let x = x0; x < x1; x += 8 + R() * 6) C.dab(x, y, 0, 22 + R() * 20, 3.6, hex('#4a3a3e'), 0.4, 0, 0.5);
      for (let k = 0; k < 6; k++) { const x = 90 + k * 118; g.fillStyle = rgba(hex('#04050c')); g.fillRect(x, 596, 64, 38); g.strokeStyle = rgba(hex('#8fa6dc'), 0.3); g.lineWidth = 2; g.strokeRect(x, 596, 64, 38); }
      g.fillStyle = rgba(hex('#171c38')); g.beginPath(); g.moveTo(x0 - 10, top(x0) - 22); for (let x = x0; x <= x1 + 10; x += 6) g.lineTo(x, top(x) - 22); for (let x = x1 + 10; x >= x0; x -= 6) g.lineTo(x, top(x) + 8); g.closePath(); g.fill();
      for (let x = x0; x < x1; x += 5 + R() * 5) C.dab(x, top(x) - 21, 0, 14 + R() * 14, 2.6, hex('#8fa6dc'), 0.5 + R() * 0.3, 0.02, 0.5);
      for (let x = x0; x < x1; x += 6 + R() * 8) C.dab(x, 1034 + R() * 6, 0, 14 + R() * 24, 2.4, hex('#aab8e6'), 0.35, 0.04, 0.8);
      C.mottle({ amt: 0.05 }); planes.hull = S.plane('hull', 60, r, C.c); planes.hull.visible = false; planes.hull.userData.rail = 330; }
    { const r = [380, 150, 620, 700]; const C = new Canvas(r, { seed: 1661 }); // the man: head, shoulders, arms raised to the rope
      paintPerson(C, { x: 470, yb: 650, h: 330, face: 1, hat: 'none', coat: 0.4, flare: 0.8, shoulder: 17, col: hex('#07080f'), arms: [{ s: [12, 2], e: [11, -16], h: [8, -33] }, { s: [-12, 2], e: [-11, -16], h: [-8, -33] }] });
      planes.man = S.plane('man', 58, r, C.c); planes.man.visible = false; }
    ex.railLantern = S.glow(150, 272, 60, 150, { color: GLOW, core: 40 }); ex.railLantern.renderOrder = 1e6 - 60 * 10 + 1; ex.railAura = S.glow(150, 300, 60, 900, { color: [1, 0.55, 0.22], core: 5000 }); ex.railAura.renderOrder = 1e6 - 60 * 10 + 0.6;
  }
  const rainR = rng(1699); const drops = Array.from({ length: 360 }, () => ({ x: rainR() * 900 - 90, y: rainR() * 1500, s: 0.7 + rainR() * 0.8, l: 40 + rainR() * 70 }));
  const shipPt = (lx, ly, project) => { shipG.updateMatrixWorld(true); const s = api.shipS0; const v = new THREE.Vector3((lx - SHIP.pivot[0]) * s, -(ly - SHIP.pivot[1]) * s, 0); shipG.localToWorld(v); return project(v.x, v.y, v.z); };
  return {
    planes: ex,
    update(t, sh) {
      const set = (pl, v) => { if (pl) pl.visible = !!v; };
      if (mood === 'dusk') {
        const co = planes.coast; set(co, sh.coast); if (sh.coast) { const k = sh.coast; const x = (k.x0 ?? 0) - co.userData.v * (t - (k.tp ?? k.t0)); co.position.x = co.userData.base.x + x * 2600 / f; co.material.uniforms.uOpacity.value = smoothstep(k.t0, k.t0 + 0.8, t) * (k.out ? 1 - smoothstep(k.out, k.out + 1, t) : 1); }
        const hb = !!sh.harbour; set(planes.shore, hb); set(planes.palms, hb); set(planes.pier, hb); ex.pierGlow.forEach((g, i) => { g.visible = hb; g.position.copy(S.world(ex.pier[i][0], ex.pier[i][1], 110)); g.material.uniforms.uI.value = 1.1 * flick(t, 20 + i); }); ex.shoreGlow.forEach((g, i) => { g.visible = hb; g.position.copy(S.world(ex.shoreLights[i].x, ex.shoreLights[i].y, 900)); g.material.uniforms.uI.value = 0.9 * flick(t, 30 + i) * (0.6 + 0.4 * (i % 2)); });
        if (hb) { const wp = S.world(500, 842, 110); setLights(planes.pier.material, [{ p: new THREE.Vector3(wp.x, wp.y, wp.z + 1), r: 3, c: WARM, k: 2.6 }, { p: new THREE.Vector3(S.world(780, 842, 110).x, wp.y, wp.z + 1), r: 3, c: WARM, k: 2.6 }]); }
        set(ex.captain, sh.captain); if (sh.captain) { const ss = api.shipS0; ex.captain.position.set((160 - SHIP.pivot[0]) * ss, -(653 - SHIP.pivot[1]) * ss, 0.2); ex.captain.renderOrder = api.ship.renderOrder + 0.2; }
      }
      if (mood === 'moon') { const hs = !!sh.hullSide; set(planes.hull, hs); set(planes.man, hs && sh.climber !== undefined); ex.railLantern.visible = ex.railAura.visible = hs;
        if (hs) { const lw = S.world(150, 280, 60); ex.railLantern.position.copy(lw); ex.railAura.position.copy(lw); const fl = flick(t, 9); ex.railLantern.material.uniforms.uI.value = 1.1 * fl; ex.railAura.material.uniforms.uI.value = 0.07 * fl;
          setLights(planes.hull.material, [{ p: new THREE.Vector3(lw.x, lw.y - 0.4, lw.z + 2.6), r: 3.4, c: WARM, k: 3.4 * fl }]);
          if (sh.climber !== undefined) { const c = sh.climber(t); planes.man.position.copy(planes.man.userData.base); planes.man.position.y -= c * 60 / f * 0; planes.man.userData.y = c; const base = planes.man.userData.base; planes.man.position.y = base.y - (1 - c) * 560 * 58 / f; planes.man.material.uniforms.uOpacity.value = smoothstep(0, 0.04, c); setLights(planes.man.material, [{ p: new THREE.Vector3(lw.x, lw.y - 0.4, lw.z + 2.6), r: 3.4, c: WARM, k: 2.2 * fl }]); } } }
    },
    draw(g, e) {
      const { t, sh, project } = e; const P = (x, y, Dd) => project(...S.world(x, y, Dd).toArray());
      if (mood === 'dusk' && sh.captain && sh.glass) { const a = sh.glass(t); const hand = shipPt(158 + 33 * 0.66, 698 - 79 * 0.66 - 15 * 0.66, project); const q = shipPt(158 + 33 * 0.66 + 1, 698 - 79 * 0.66 - 15 * 0.66, project); const ux = q[0] - hand[0], uy = q[1] - hand[1]; const pxPer = Math.hypot(ux, uy); const ang = Math.atan2(uy, ux) - a; const L = 24 * pxPer;
        g.lineCap = 'round'; g.strokeStyle = rgba(hex('#0b0810')); g.lineWidth = 5 * pxPer; g.beginPath(); g.moveTo(hand[0] - Math.cos(ang) * 6 * pxPer, hand[1] - Math.sin(ang) * 6 * pxPer); g.lineTo(hand[0] + Math.cos(ang) * L, hand[1] + Math.sin(ang) * L); g.stroke(); g.strokeStyle = rgba(hex('#c9a15e'), 0.9); g.lineWidth = 1.6 * pxPer; g.beginPath(); g.moveTo(hand[0] + Math.cos(ang) * L * 0.92, hand[1] + Math.sin(ang) * L * 0.92); g.lineTo(hand[0] + Math.cos(ang) * L * 1.02, hand[1] + Math.sin(ang) * L * 1.02); g.stroke(); }
      if (mood === 'dusk' && sh.nameBoard) { // the board on the quarter: ZONG, then the older name beneath
        const a = shipPt(96, 742, project), b = shipPt(196, 742, project); const ang = Math.atan2(b[1] - a[1], b[0] - a[0]); const sc = Math.hypot(b[0] - a[0], b[1] - a[1]) / 100; const w1 = sh.nameBoard.zong(t), w2 = sh.nameBoard.zorg(t);
        g.save(); g.translate(a[0], a[1]); g.rotate(ang); g.scale(sc, sc); g.fillStyle = 'rgba(14,10,12,0.9)'; g.fillRect(0, -17, 100, 25); g.strokeStyle = 'rgba(190,150,80,0.55)'; g.lineWidth = 1.2; g.strokeRect(2, -15, 96, 21);
        g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = '500 17px "Cinzel"'; g.letterSpacing = '5px'; const fl = flick(t, 3);
        g.fillStyle = `rgba(232,188,104,${(0.92 * w1 * Math.min(1, 0.7 + fl * 0.3)).toFixed(3)})`; g.fillText('ZONG', 52, -4); g.fillStyle = `rgba(232,188,104,${(0.92 * w2 * Math.min(1, 0.7 + fl * 0.3)).toFixed(3)})`; g.fillText('ZORG', 52, -4); g.restore(); }
      if (sh.rain) { const k = sh.rain(t); if (k > 0) { g.lineCap = 'round'; for (const d of drops) { const y = ((d.y + t * 1700 * d.s) % 1500) - 150, x = d.x - y * 0.2; if (!(x > -20 && x < 740)) continue; g.strokeStyle = `rgba(190,205,240,${(0.2 * k * d.s).toFixed(3)})`; g.lineWidth = 1.1 * d.s; g.beginPath(); g.moveTo(x, y); g.lineTo(x - d.l * 0.2, y + d.l); g.stroke(); }
          for (let i = 0; i < 46; i++) { const r2 = rng(Math.floor(t * 9) * 46 + i); const x = r2() * 760 - 20, y = lerp(780, 1250, Math.pow(r2(), 0.7)); const age = (t * 9) % 1; const s = (3 + (y - 760) * 0.02) * (0.3 + age); g.strokeStyle = `rgba(200,215,255,${(0.35 * (1 - age) * k).toFixed(3)})`; g.lineWidth = 1.2; g.beginPath(); g.ellipse(x, y, s * 2.4, s * 0.7, 0, 0, 6.3); g.stroke(); } } }
      if (sh.rings) for (const [t0, x, y, s] of sh.rings) { const age = t - t0; if (age < 0 || age > 3.4) continue; const k = age / 3.4; const q = P(x, y, 42); const sz = Math.abs(P(x + 100, y, 42)[0] - q[0]) / 100; for (let j = 0; j < 3; j++) { const kk = clamp(k - j * 0.09); if (kk <= 0) continue; const rr = (14 + 130 * Math.pow(kk, 0.7)) * s * sz; g.strokeStyle = `rgba(205,220,255,${(0.62 * (1 - kk) * (1 - j * 0.28)).toFixed(3)})`; g.lineWidth = (2.4 - j * 0.6) * sz * s; g.beginPath(); g.ellipse(q[0], q[1], rr, rr * 0.2, 0, 0, 6.3); g.stroke(); } }
      if (mood === 'moon' && sh.hullSide) { // the rope: from the rail down into the water; it sways, then goes taut
        const tens = sh.tension ? sh.tension(t) : 0; const rx = 470, y0 = 326, y1 = 1026; const sway = (1 - tens) * (Math.sin(t * 1.3) * 7 + Math.sin(t * 2.9 + 1) * 3) + tens * Math.sin(t * 11) * 0.8; const pts = []; for (let k = 0; k <= 24; k++) { const u = k / 24; pts.push(P(rx + sway * Math.sin(Math.PI * u) * 0.9 + (1 - tens) * 6 * u * u, lerp(y0, y1, u), 58)); }
        const sz = Math.abs(P(rx + 100, 0, 58)[0] - P(rx, 0, 58)[0]) / 100; g.lineCap = 'round'; g.strokeStyle = rgba(hex('#2a1f1a')); g.lineWidth = 8.5 * sz; g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]))); g.stroke();
        g.strokeStyle = rgba(hex('#b89868'), 0.5); g.lineWidth = 1.6 * sz; for (let k = 0; k < 24; k++) { const a = pts[k], b = pts[k + 1]; const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2; g.beginPath(); g.moveTo(mx - 3.2 * sz, my + 2 * sz); g.lineTo(mx + 3.2 * sz, my - 2 * sz); g.stroke(); }
        const w = pts[pts.length - 1]; g.strokeStyle = `rgba(205,220,255,${(0.5).toFixed(3)})`; g.lineWidth = 1.6 * sz; for (let j = 0; j < 2; j++) { const kk = ((t * 0.6 + j * 0.5) % 1); g.globalAlpha = 1 - kk; g.beginPath(); g.ellipse(w[0], w[1] + 3 * sz, (10 + 40 * kk) * sz, (2.4 + 8 * kk) * sz, 0, 0, 6.3); g.stroke(); } g.globalAlpha = 1;
        // the rail lantern
        const lk = P(150, 252, 60); line(g, P(150, 150, 60), lk, 2.2 * sz, hex('#0a0a12'), 0.95); drawLantern(g, lk[0], P(150, 282, 60)[1], 52 * sz, 1.0 * flick(t, 9), Math.sin(t * 1.1) * 0.03); }
    },
  };
}
