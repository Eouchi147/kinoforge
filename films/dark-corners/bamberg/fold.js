// Bamberg (Kinetic): the fold of the letter. A real paper fold: each flap is cut into slices and bent about its hinge (the free end leads a little), seen with
// a touch of perspective, shaded by a lamp from the north (a vertical flap goes dark, the flat top catches the light), with the back face of the paper
// (the same fibre, a shade warmer, the writing showing through mirrored) and a cast shadow on whatever lies below. Pure function of (theta_top, theta_bottom).
import { clamp, lerp } from './lib.js';

const LIGHT = [-0.38, 0.925];                       // lamp direction in (y = north negative, z = up)
export function drawFlap(g, { front, back, sheetW, sheetH, srcTop, hinge, dirSign, L, theta, U, N = 18, perspD = 3.2 }) {
  if (theta <= 0.002) return;
  const bend = (u) => clamp(theta * (1 + 0.30 * (u - 0.4) * Math.sin(theta)), 0, Math.PI);
  const ys = [hinge], zs = [0], am = [];
  for (let i = 0; i < N; i++) { const um = (i + 0.5) / N, a = bend(um); am.push(a); ys.push(ys[i] + dirSign * (L / N) * Math.cos(a)); zs.push(zs[i] + (L / N) * Math.sin(a)); }
  const cy = sheetH / 2, persp = (z) => 1 / (1 - z / (perspD * sheetH));
  // cast shadow on what lies below: south of the flap's ground trace, from the hinge outward
  const zf = zs[N], yg = ys[N] + 0.41 * zf, ya = Math.min(hinge, yg), yb = Math.max(hinge, yg) + 0.41 * zf + 6 * U;
  const k = Math.pow(Math.sin(theta), 0.8);
  if (k > 0.01) { const gr = g.createLinearGradient(0, ya, 0, yb); const dark = `rgba(20,12,4,${0.36 * k})`; if (dirSign < 0) { gr.addColorStop(0, 'rgba(20,12,4,0)'); gr.addColorStop(Math.min(0.98, (hinge - ya) / (yb - ya)), dark); gr.addColorStop(1, 'rgba(20,12,4,0)'); } else { gr.addColorStop(0, 'rgba(20,12,4,0)'); gr.addColorStop(Math.min(0.98, (hinge - ya) / (yb - ya) + 0.0001), dark); gr.addColorStop(1, 'rgba(20,12,4,0)'); }
    g.fillStyle = gr; g.fillRect(sheetW * 0.015, ya, sheetW * 0.97, yb - ya); }
  for (let i = 0; i < N; i++) {
    const u0 = i / N, u1 = (i + 1) / N, a = am[i], yy0 = cy + (ys[i] - cy) * persp(zs[i]), yy1 = cy + (ys[i + 1] - cy) * persp(zs[i + 1]), wm = (persp(zs[i]) + persp(zs[i + 1])) / 2;
    const sr0 = dirSign < 0 ? srcTop + L - u0 * L : srcTop + u0 * L, sr1 = dirSign < 0 ? srcTop + L - u1 * L : srcTop + u1 * L, srcMin = Math.min(sr0, sr1), srcLen = Math.abs(sr1 - sr0), ymin = sr0 < sr1 ? yy0 : yy1, kk = (yy1 - yy0) / (sr1 - sr0);
    const isBack = Math.cos(a) < 0;
    let ny, nz; if (dirSign < 0) { ny = Math.sin(a); nz = Math.cos(a); } else { ny = -Math.sin(a); nz = Math.cos(a); }
    if (isBack) { ny = -ny; nz = -nz; }
    const lam = Math.max(0, ny * LIGHT[0] + nz * LIGHT[1]), shade = 0.58 * Math.pow(1 - lam / LIGHT[1], 1.15);
    g.save(); g.translate(sheetW / 2, ymin); g.scale(wm, kk);
    g.drawImage(isBack ? back : front, 0, srcMin, sheetW, srcLen + 0.6, -sheetW / 2, 0, sheetW, srcLen + 0.6);
    if (isBack) { g.globalAlpha = 0.10; g.drawImage(front, 0, srcMin, sheetW, srcLen + 0.6, -sheetW / 2, 0, sheetW, srcLen + 0.6); g.globalAlpha = 1; }
    g.fillStyle = `rgba(28,16,6,${shade})`; g.fillRect(-sheetW / 2, 0, sheetW, srcLen + 0.6);
    g.restore();
  }
  // the lit edge of the free end and the crease at the hinge
  const yEnd = cy + (ys[N] - cy) * persp(zs[N]), wEnd = sheetW * persp(zs[N]);
  g.save(); g.strokeStyle = `rgba(255,246,222,${0.35 * (1 - Math.abs(theta - Math.PI / 2) / (Math.PI / 2))})`; g.lineWidth = 1.4 * U; g.beginPath(); g.moveTo(sheetW / 2 - wEnd / 2, yEnd); g.lineTo(sheetW / 2 + wEnd / 2, yEnd); g.stroke(); g.restore();
}

// the whole folded sheet in sheet-local coordinates (0..sheetW, 0..sheetH). thetaT: top third folds down (0..pi), thetaB: bottom third folds up (0..pi).
export function drawSheet(g, { front, back, sheetW, sheetH, thetaT, thetaB, U, shadow = 1, addr = 0, addrFn = null }) {
  const h3 = sheetH / 3;
  // the sheet's own shadow on the desk, then the middle third (it never moves)
  g.save(); g.shadowColor = `rgba(0,0,0,${0.75 * shadow})`; g.shadowBlur = 30 * U; g.shadowOffsetX = 5 * U; g.shadowOffsetY = 12 * U; g.fillStyle = '#d9cdb0';
  const top = thetaT > 0.02 ? h3 : 0, bot = thetaB > 0.02 ? 2 * h3 : sheetH; g.fillRect(0, top, sheetW, bot - top); g.restore();
  if (thetaT <= 0.02) g.drawImage(front, 0, 0, sheetW, h3, 0, 0, sheetW, h3);
  g.drawImage(front, 0, h3, sheetW, h3, 0, h3, sheetW, h3);
  if (thetaB <= 0.02) g.drawImage(front, 0, 2 * h3, sheetW, h3, 0, 2 * h3, sheetW, h3);
  drawFlap(g, { front, back, sheetW, sheetH, srcTop: 0, hinge: h3, dirSign: -1, L: h3, theta: thetaT, U });
  drawFlap(g, { front, back, sheetW, sheetH, srcTop: 2 * h3, hinge: 2 * h3, dirSign: 1, L: h3, theta: thetaB, U });
  // thickness of the stack once folded: the layers show as thin lines on the edges
  const done = clamp((Math.min(thetaT, thetaB) - 2.5) / 0.6);
  if (done > 0) { g.save(); g.globalAlpha = done; g.fillStyle = 'rgba(70,48,24,0.35)'; g.fillRect(0, h3, sheetW, 1.5 * U); g.fillRect(0, 2 * h3 - 1.5 * U, sheetW, 1.5 * U); g.fillStyle = 'rgba(255,248,230,0.35)'; g.fillRect(0, h3 + 2.2 * U, sheetW, 1 * U); g.fillRect(0, 2 * h3 - 3.4 * U, sheetW, 1 * U); g.fillStyle = 'rgba(60,40,18,0.18)'; g.fillRect(0, 2 * h3 - 1.5 * U, sheetW, 4 * U); g.restore(); }
  if (addr > 0 && addrFn) addrFn(g, addr, h3);
}
