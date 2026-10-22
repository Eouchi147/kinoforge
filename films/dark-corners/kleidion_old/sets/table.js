// SET table: close still lifes on a dark wooden table by lamplight: the tally plank (forty years of war), the wax seal on an order,
// the cup of cold water and the oil lamp that gutters out. Everything animated is drawn in the detail layer; the wood is painted once.
import { Canvas, hex, mixc, mul, rgba, underpaint, clamp, lerp, smoothstep, ease, noise1, rng, WARM, fireFlick, tintAll, lightsOn, nn } from './common.js';
import { glowAt, embers, hash1 } from '../figs.js';
import { paintDesk, paintSheet } from './page.js';

export default function table(S, cams) {
  const cover = (D, m) => S.cover(D, cams, m); const D = { desk: 10, plank: 9.9, sheet: 9.8 }; const planes = {};
  { const r = cover(D.desk, 60); const C = new Canvas(r, { seed: 6001 }); paintDesk(C); planes.desk = S.plane('desk', D.desk, r, C.c); }
  { const w = 560, h = 190, C = new Canvas([0, 0, w, h], { q: 1.4, seed: 6011 }); const R = C.R; const path = new Path2D(); path.roundRect(2, 2, w - 4, h - 4, 6);
    const base = (x, y) => mul(mixc(hex('#8a6a46'), hex('#6a4c32'), nn.fbm(x * 0.006, y * 0.03, 3)), 0.9); underpaint(C, base, path, 6); const m = C.mask((g) => g.fill(path));
    C.strokes({ n: w * h / 260, mask: m, color: base, angle: () => (R() - 0.5) * 0.04, len: [40, 150], wid: [2, 5], alpha: [0.35, 0.7], jv: 0.1, bend: 0.01 });
    C.g.strokeStyle = 'rgba(20,12,8,0.5)'; C.g.lineWidth = 3; C.g.stroke(path);
    const pl = S.plane('plank', D.plank, [80, 520, 640, 710], C.c); pl.rotation.z = -0.025; planes.plank = pl; }
  { const w = 400, h = 540, c = paintSheet(w, h, 6021); const pl = S.plane('sheet', D.sheet, [160, 380, 560, 920], c); pl.rotation.z = 0.04; planes.sheet = pl; }
  tintAll(S, 0.3);
  const candles = [{ x: 690, y: 330 }, { x: 40, y: 1120 }];
  const flame = (g, x, y, K, f, t, i, size = 1) => { const hf = 26 * K * size * (0.9 + 0.2 * f); g.fillStyle = rgba([255, 205, 120], 0.95); g.beginPath(); g.moveTo(x - 5 * K * size, y); g.quadraticCurveTo(x - 6 * K * size, y - hf * 0.6, x + 1.5 * K * Math.sin(t * 7 + i), y - hf); g.quadraticCurveTo(x + 7 * K * size, y - hf * 0.5, x + 5 * K * size, y); g.fill(); g.fillStyle = rgba([255, 245, 215], 0.9); g.beginPath(); g.ellipse(x, y - hf * 0.28, 2.2 * K * size, hf * 0.22, 0, 0, 7); g.fill(); };
  return {
    planes,
    update(F) {
      const t = F.t, g = F.g, sh = F.shot, lt = F.lt; tintAll(S, sh.base ?? 0.3); planes.plank.visible = sh.mode === 'tally'; planes.sheet.visible = sh.mode === 'seal'; const gl = F.glow(); const mode = sh.mode;
      const lampPos = mode === 'cup' ? { x: 200, y: 700 } : null;
      const cs = mode === 'cup' ? [] : candles; const fl = cs.map((c, i) => fireFlick(t, i * 3.3 + 1));
      const out = sh.gutter ? 1 - smoothstep(sh.gutter[0], sh.gutter[1], t) : 1; // lamp strength
      const lamp = lampPos ? { ...lampPos, f: fireFlick(t, 5) * out } : null;
      const mk = (Dp) => { const l = cs.map((c, i) => ({ p: S.world(c.x, c.y, Dp), r: 3.2 * (Dp / 10) * (S.f / 1866), c: WARM, k: 1.5 * fl[i] })); if (lamp) l.push({ p: S.world(lamp.x + 54, lamp.y - 30, Dp), r: 3.4 * (Dp / 10) * (S.f / 1866), c: WARM, k: 2.0 * lamp.f }); return l; };
      lightsOn(planes.desk, mk(D.desk)); lightsOn(planes.plank, mk(D.plank)); lightsOn(planes.sheet, mk(D.sheet));
      for (let i = 0; i < cs.length; i++) { const c = cs[i]; const p = F.P(D.desk, c.x, c.y), K = F.K(D.desk, c.x, c.y); glowAt(gl, p[0], p[1], 240 * K * fl[i], 0.16, [255, 150, 70]); glowAt(gl, p[0], p[1], 26 * K, 0.9 * fl[i]);
        if (p[0] > -80 && p[0] < 800 && p[1] > -80 && p[1] < 1360) { g.fillStyle = rgba(hex('#cfc3a0')); g.fillRect(p[0] - 9 * K, p[1], 18 * K, 70 * K); flame(g, p[0], p[1], K, fl[i], t, i); } F.lights.push({ x: p[0], y: p[1], r: 300 * K, c: WARM, k: 0.5 * fl[i] }); }
      if (mode === 'tally') {
        const [t0, t1, n] = sh.marks; const cnt = n * ease.inOutSine(clamp((t - t0) / (t1 - t0))); const P = (x, y) => F.P(D.plank, x, y), K = F.K(D.plank, 360, 600);
        const pc = P(360, 615); const sx = K * Math.cos(-0.025), sy = K; g.save(); g.translate(pc[0], pc[1]); g.rotate(0.025); g.scale(K, K); // plank-local px, origin at the middle
        const per = 5, cols = 8, gw = 62; for (let i = 0; i < Math.floor(cnt); i++) { const grp = Math.floor(i / per), k = i % per; const row = Math.floor(grp / 4), col = grp % 4; const gx = -228 + col * 150, gy = -42 + row * 72;
          const fresh = Math.max(0, 1 - (cnt - i) * 1.2); const a = 0.95; const draw = (x0, y0, x1, y1) => { g.strokeStyle = 'rgba(12,8,6,0.92)'; g.lineWidth = 6; g.lineCap = 'round'; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); g.strokeStyle = `rgba(255,200,130,${0.35 + 0.4 * fresh})`; g.lineWidth = 1.6; g.beginPath(); g.moveTo(x0 + 3, y0 + 1); g.lineTo(x1 + 3, y1 + 1); g.stroke(); };
          const jit = (hash1(i * 7.1) - 0.5) * 3; if (k < 4) draw(gx + k * 15 + jit, gy - 24, gx + k * 15 + jit * 0.6, gy + 24); else draw(gx - 8, gy + 18, gx + 62, gy - 18); }
        g.restore(); const hp = F.P(D.plank, 360, 615); glowAt(gl, hp[0], hp[1], 330 * K, 0.07, [255, 170, 90]);
      }
      if (mode === 'key') {
        const kp = F.P(D.desk, 360, 640), K = F.K(D.desk, 360, 640); g.save(); g.translate(kp[0], kp[1]); g.rotate(-0.32 + 0.02 * Math.sin(t * 0.5)); g.scale(K, K);
        const iron = (a) => `rgba(${34 + a},${30 + a},${34 + a},1)`; g.lineCap = 'round'; g.lineJoin = 'round';
        g.fillStyle = 'rgba(0,0,0,0.35)'; g.beginPath(); g.ellipse(14, 40, 300, 18, 0, 0, 7); g.fill();
        g.strokeStyle = iron(0); g.lineWidth = 34; g.beginPath(); g.moveTo(-170, 0); g.lineTo(250, 0); g.stroke();
        g.lineWidth = 30; g.strokeStyle = iron(0); g.beginPath(); g.arc(-230, 0, 62, 0, 7); g.stroke();
        g.fillStyle = iron(0); g.fillRect(170, 0, 30, 100); g.fillRect(222, 0, 28, 74); g.fillRect(150, 70, 100, 30);
        g.lineWidth = 6; g.strokeStyle = 'rgba(255,190,120,0.55)'; g.beginPath(); g.moveTo(-170, -10); g.lineTo(250, -10); g.stroke(); g.beginPath(); g.arc(-230, 0, 74, 3.4, 5.2); g.stroke();
        g.lineWidth = 3; g.strokeStyle = 'rgba(255,230,190,0.4)'; g.beginPath(); g.moveTo(-170, -14); g.lineTo(250, -14); g.stroke();
        const gx = sh.glint ? lerp(-280, 260, clamp((t - sh.glint) / 0.7)) : -999; if (gx > -280 && gx < 260) { const gr = g.createRadialGradient(gx, -12, 2, gx, -12, 60); gr.addColorStop(0, 'rgba(255,245,220,0.9)'); gr.addColorStop(1, 'rgba(255,200,140,0)'); g.fillStyle = gr; g.fillRect(gx - 60, -72, 120, 120); }
        g.restore(); glowAt(gl, kp[0], kp[1], 260 * K, 0.1, [255, 160, 80]);
      }
      if (mode === 'seal') {
        const sp = F.P(D.sheet, 360, 650), K = F.K(D.sheet, 360, 650); g.save(); g.translate(sp[0], sp[1]); g.rotate(0.04); g.scale(K, K);
        g.strokeStyle = 'rgba(38,24,14,0.7)'; g.lineWidth = 1.5; g.lineCap = 'round'; for (let i = 0; i < 9; i++) { const R = rng(500 + i); const y = -190 + i * 26; const w = 250 + 40 * R(); let x = -160; g.beginPath(); while (x < -160 + w) { const l = 10 + 20 * R(); g.moveTo(x, y); g.quadraticCurveTo(x + l * 0.5, y - 8 * (0.3 + R()), x + l, y); x += l + 6; } g.stroke(); }
        const sa = sh.sealAt; const wax = smoothstep(sa, sa + 0.25, t), r0 = 44 * ease.outCubic(wax); const wy = 150;
        if (wax > 0) { g.fillStyle = rgba(hex('#701818')); g.beginPath(); for (let k = 0; k < 18; k++) { const an = k / 18 * 6.283, r = r0 * (0.92 + 0.12 * hash1(k * 2.3)); k ? g.lineTo(Math.cos(an) * r, wy + Math.sin(an) * r) : g.moveTo(Math.cos(an) * r, wy + Math.sin(an) * r); } g.closePath(); g.fill(); g.fillStyle = rgba(hex('#a42a28'), 0.8); g.beginPath(); g.ellipse(-10, wy - 14, r0 * 0.4, r0 * 0.22, -0.4, 0, 7); g.fill();
          g.strokeStyle = rgba(hex('#4a0c0c'), 0.9); g.lineWidth = 4; g.beginPath(); g.moveTo(0, wy - r0 * 0.5); g.lineTo(0, wy + r0 * 0.5); g.moveTo(-r0 * 0.34, wy - r0 * 0.15); g.lineTo(r0 * 0.34, wy - r0 * 0.15); g.stroke(); g.lineWidth = 2; g.beginPath(); g.arc(0, wy, r0 * 0.7, 0, 7); g.stroke(); }
        const st = t < sa ? clamp(1 - (sa - t) / 0.5) : 1 - smoothstep(sa + 0.15, sa + 0.8, t); const sy = wy - (1 - ease.inQuad(st)) * 230 - (t >= sa ? 0 : 0);
        if (st > 0.01 && t < sa + 0.9) { g.fillStyle = rgba(hex('#2a2018')); g.fillRect(-16, sy - 110, 32, 100); g.fillStyle = rgba(hex('#8a7040')); g.beginPath(); g.ellipse(0, sy - 6, 40, 14, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#3a2c20')); g.beginPath(); g.ellipse(0, sy - 2, 38, 11, 0, 0, 7); g.fill(); }
        g.restore(); glowAt(gl, sp[0], sp[1] + 150 * K, 160 * K, 0.12 + 0.2 * wax, [255, 120, 80]);
      }
      if (mode === 'cup') {
        const lp = F.P(D.desk, lamp.x, lamp.y), LK = F.K(D.desk, lamp.x, lamp.y); const cx = 470, cy = 880; const cp = F.P(D.desk, cx, cy), CK = F.K(D.desk, cx, cy);
        // oil lamp: clay body, a small spout, the flame (shrinks and dies at `gutter`)
        g.fillStyle = rgba(hex('#2a1c14')); g.beginPath(); g.ellipse(lp[0], lp[1] + 18 * LK, 54 * LK, 20 * LK, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#4a3020')); g.beginPath(); g.moveTo(lp[0] - 44 * LK, lp[1] + 14 * LK); g.quadraticCurveTo(lp[0], lp[1] - 18 * LK, lp[0] + 56 * LK, lp[1] + 2 * LK); g.lineTo(lp[0] + 40 * LK, lp[1] + 24 * LK); g.lineTo(lp[0] - 40 * LK, lp[1] + 24 * LK); g.fill();
        const fo = Math.max(0, lamp.f); if (fo > 0.03) { flame(g, lp[0] + 54 * LK, lp[1] + 2 * LK, LK, fo, t, 9, 1.5 * Math.min(1, fo)); glowAt(gl, lp[0] + 54 * LK, lp[1] - 20 * LK, 380 * LK * fo, 0.2 * fo, [255, 150, 70]); glowAt(gl, lp[0] + 54 * LK, lp[1] - 12 * LK, 30 * LK * fo, 0.9 * fo); F.lights.push({ x: lp[0] + 54 * LK, y: lp[1], r: 380 * LK, c: WARM, k: 0.7 * fo }); }
        if (sh.gutter && t > sh.gutter[0]) { const u = t - sh.gutter[0]; for (let k = 0; k < 4; k++) { const a = smoothstep(0, 0.6, u - k * 0.15) * (1 - smoothstep(1.2, 2.6, u - k * 0.15)); if (a > 0) { g.strokeStyle = `rgba(190,180,200,${0.3 * a})`; g.lineWidth = 3 * LK; g.beginPath(); g.moveTo(lp[0] + 54 * LK, lp[1]); g.bezierCurveTo(lp[0] + 54 * LK + 18 * LK * Math.sin(u * 3 + k), lp[1] - 40 * LK, lp[0] + 54 * LK - 14 * LK, lp[1] - 80 * LK, lp[0] + 54 * LK + 20 * LK * Math.sin(u * 2 + k), lp[1] - 130 * LK * (0.6 + 0.2 * k)); g.stroke(); } } }
        // the cup (clay, wide mouth) with water; the jug pours from above-right
        const lift = sh.lift ? smoothstep(sh.lift[0], sh.lift[1], t) * (1 - smoothstep(sh.lift[2], sh.lift[3], t)) : 0; const pour = sh.pour ? smoothstep(sh.pour[0], sh.pour[0] + 0.3, t) * (1 - smoothstep(sh.pour[1] - 0.2, sh.pour[1], t)) : 0;
        const water = sh.pour ? clamp((t - sh.pour[0]) / (sh.pour[1] - sh.pour[0])) : (sh.full ? 1 : 0); const drunk = sh.lift ? smoothstep(sh.lift[1], sh.lift[2], t) : 0;
        const wl = water * (1 - 0.75 * drunk); const ox = 0, oy = -lift * 140 * CK, tilt = -lift * 0.5; g.save(); g.translate(cp[0] + ox, cp[1] + oy); g.rotate(tilt); g.scale(CK, CK);
        g.fillStyle = rgba(hex('#241810')); g.beginPath(); g.ellipse(0, 6, 54, 12, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#5a3a28')); g.beginPath(); g.moveTo(-52, -86); g.lineTo(52, -86); g.lineTo(38, 0); g.quadraticCurveTo(0, 12, -38, 0); g.closePath(); g.fill();
        g.fillStyle = rgba(hex('#7a4e34'), 0.6); g.beginPath(); g.moveTo(-52, -86); g.lineTo(-30, -86); g.lineTo(-24, 0); g.lineTo(-38, 0); g.fill(); g.fillStyle = rgba(hex('#1c1210')); g.beginPath(); g.ellipse(0, -86, 52, 14, 0, 0, 7); g.fill();
        if (wl > 0.01) { const wy = -12 - wl * 62; g.fillStyle = rgba([160, 190, 220], 0.55 + 0.3 * wl); g.beginPath(); g.ellipse(0, wy, 44 + wl * 4, 10 + wl * 3, 0, 0, 7); g.fill(); g.strokeStyle = rgba([220, 235, 255], 0.6); g.lineWidth = 1.6; g.beginPath(); g.ellipse(0, wy, 30, 6.5, 0, 0, 7); g.stroke(); if (pour > 0.1) for (let k = 0; k < 3; k++) { const u = ((t * 1.2 + k / 3) % 1); g.strokeStyle = rgba([230, 240, 255], 0.5 * (1 - u)); g.beginPath(); g.ellipse(0, wy, 6 + u * 34, 2 + u * 7, 0, 0, 7); g.stroke(); } }
        g.restore();
        if (pour > 0.02) { const jp = F.P(D.desk, 640, 640), JK = F.K(D.desk, 640, 640); const tilt2 = 0.75 * pour; const mouthx = cp[0] + 8 * CK, mouthy = cp[1] - 150 * CK;
          g.save(); g.translate(mouthx + 70 * JK, mouthy - 60 * JK); g.rotate(-tilt2 * 0.0 - 0.7 * pour); g.scale(JK, JK); g.fillStyle = rgba(hex('#4a3020')); g.beginPath(); g.ellipse(0, 0, 60, 74, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#5a3a28')); g.fillRect(-20, -112, 40, 44); g.fillStyle = rgba(hex('#7a4e34'), 0.5); g.beginPath(); g.ellipse(-22, -10, 14, 48, 0, 0, 7); g.fill(); g.restore();
          g.strokeStyle = rgba([200, 225, 250], 0.75 * pour); g.lineWidth = 5 * CK; g.lineCap = 'round'; g.beginPath(); g.moveTo(mouthx + 30 * JK, mouthy - 20 * JK); g.quadraticCurveTo(mouthx + 14 * CK, mouthy + 20 * CK, mouthx + 6 * CK, cp[1] - 30 * CK - water * 62 * CK); g.stroke(); }
        else if (!sh.hideJug) { const jp = F.P(D.desk, 600, 940), JK = F.K(D.desk, 600, 940); g.fillStyle = rgba(hex('#3a2418')); g.beginPath(); g.ellipse(jp[0], jp[1], 66 * JK, 18 * JK, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#52341f')); g.beginPath(); g.ellipse(jp[0], jp[1] - 74 * JK, 62 * JK, 76 * JK, 0, 0, 7); g.fill(); g.fillStyle = rgba(hex('#5a3a28')); g.fillRect(jp[0] - 20 * JK, jp[1] - 170 * JK, 40 * JK, 46 * JK); g.fillStyle = rgba(hex('#8a5a3a'), 0.4); g.beginPath(); g.ellipse(jp[0] - 22 * JK, jp[1] - 80 * JK, 14 * JK, 48 * JK, 0, 0, 7); g.fill(); }
      }
      embers(gl, t, { x0: 0, y0: 100, x1: 720, y1: 1250 }, 18, { size: 1.2, col: [255, 200, 120], a: 0.35, wind: 4, speed: 8, rise: 0.4, seed: 17 });
      F.amb = [0.85, 0.85, 0.85]; F.bloom = 0.4;
    },
  };
}
