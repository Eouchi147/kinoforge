// Beats 14 and 15: Junius's letter against the record. Cream parchment, his shaky hand, the thumbscrew plates, the rope. 67.9 to 86.4 s.
import { clamp, ease, lerp, rgba, keys, withScale, mkLine, FONTS, measure, noise1 } from './lib.js';

export function buildLetter(E) {
  const { C, W, H, U, AX, MEAS } = E, tw = E.tw, ink = C.ink;
  const S = [];
  const BI = (s) => E.line({ color: ink, ...s });
  const stack = (specs, top, gap) => { for (const s of E.stack(specs, top, gap).lines) BI(s); };
  const SEED = 40;

  // ---------------------------------------------------------------- t3: "In his letter, he wrote something very different. They crushed his thumbs until blood came out from under his nails."
  {
    const tCut = 67.90, tOutA = 70.95;
    const em = E.emFit('C', 'from under his nails.', 0.96);
    const HL = [
      { txt: 'They crushed his thumbs', base: 0.215, times: [tw('t3', 'They'), tw('t3', 'crushed'), tw('t3', 'his', 1), tw('t3', 'thumbs')] },
      { txt: 'until blood came out', base: 0.320, times: ['until', 'blood', 'came', 'out'].map((w) => tw('t3', w)) },
      { txt: 'from under his nails.', base: 0.425, times: [tw('t3', 'from'), tw('t3', 'under'), tw('t3', 'his', 2), tw('t3', 'nails.')] },
    ];
    S.push({
      name: 't3 his letter: thumbs', t0: tCut, bg: 'cream',
      hits: [[tCut, 11, 6, 0], [tw('t3', 'different.'), 6, 5, 0], [tw('t3', 'thumbs'), 9, 6, 0], [tw('t3', 'nails.'), 5, 5, 0]],
      draw(E) {
        const t = E.t;
        if (t < tOutA) stack([
          { txt: 'IN HIS LETTER,', font: 'B', cap: 0.035, ls: 0.16, times: [tw('t3', 'in'), tw('t3', 'his'), tw('t3', 'letter,')] },
          { txt: 'HE WROTE SOMETHING', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.04, times: [tw('t3', 'he'), tw('t3', 'wrote'), tw('t3', 'something')] },
          { txt: 'VERY', font: 'B', cap: 0.05, ls: 0.2, times: tw('t3', 'very') },
          { txt: 'DIFFERENT.', font: 'B', fit: 1.0, maxCap: 0.105, ls: 0.03, times: tw('t3', 'different.'), curve: E.PAYOFF },
        ], 0.19, 0.026);
        else {
          HL.forEach((l, k) => E.hand({ ...l, em, color: ink, trem: (tk) => 0.55 + 0.25 * k, seed: SEED + k, squash: k === 0 ? { w: 3, k: (tt) => 1 - 0.30 * ease.outCubic(clamp((tt - tw('t3', 'thumbs') - 0.12) / 0.2)) } : null }));
          // the plates close on "thumbs"
          const tt = tw('t3', 'thumbs') + 0.04, p = ease.outCubic(clamp((t - tt) / 0.22));
          if (t >= tt) {
            const w = E.handWord({ ...HL[0], em }, 3), cy = w.base - w.cap * 0.45, h = w.cap * 2.0, pw = 0.016 * W, gap = 6 * U, wc = (w.x0 + w.x1) / 2, hw = (w.x1 - w.x0) / 2;
            const sq = 1 - 0.30 * ease.outCubic(clamp((t - tw('t3', 'thumbs') - 0.12) / 0.2)), tx = hw * sq + gap;
            E.ink.save(); E.ink.fillStyle = ink;
            const xl = lerp(w.x0 - 0.14 * W, wc - tx - pw, p), xr = lerp(w.x1 + 0.14 * W, wc + tx, p);
            E.ink.fillRect(xl, cy - h / 2, pw, h); E.ink.fillRect(xr, cy - h / 2, pw, h);
            E.ink.fillRect(xr + pw, cy - 3 * U, 0.025 * W, 6 * U); E.ink.fillRect(xr + pw + 0.025 * W - 2 * U, cy - 11 * U, 6 * U, 22 * U);      // the screw and its handle
            E.ink.restore();
          }
        }
      },
    });
  }

  // ---------------------------------------------------------------- t4: tied, pulled, dropped. Eight times.
  {
    const tCut = 75.12, tCue = 79.95, em = E.emFit('C', 'behind his back,', 0.96);
    const TIE = [
      { txt: 'They tied his hands', base: 0.215, times: ['They', 'tied', 'his', 'hands'].map((w) => tw('t4', w)) },
      { txt: 'behind his back,', base: 0.320, times: [tw('t4', 'behind'), tw('t4', 'his', 1), tw('t4', 'back,')] },
    ];
    const PULL = [
      { txt: 'pulled him up', base: 0.215, times: [tw('t4', 'pulled'), tw('t4', 'him'), tw('t4', 'up')] },
      { txt: 'by a rope,', base: 0.320, times: [tw('t4', 'by'), tw('t4', 'a'), tw('t4', 'rope,')] },
    ];
    const tDrop = 81.58, tImp0 = tDrop + 0.22, T8 = [83.56, 83.87, 84.22, 84.50, 84.80, 85.08, 85.40, 85.72];
    const HIGH = 0.31, LOW = 0.465, PEAK = 0.385, ropeX = 0.5 * W;
    // the hanging word: y (baseline, H units) as a pure function of time
    const bounce = (s) => (s < 0 ? 0 : 0.02 * Math.exp(-9 * s) * Math.sin(s * 32));
    const yHang = (t) => {
      if (t < tDrop) return HIGH + (t > 80.5 ? 0.0035 * Math.sin(t * 38) * clamp((t - 80.5) / 0.6) : 0);
      if (t < tImp0) return lerp(HIGH, LOW, ease.inQuad(clamp((t - tDrop) / 0.22)));
      let rest = LOW + bounce(t - tImp0);
      for (let j = 0; j < T8.length; j++) {
        const T = T8[j], rs = T - 0.21, fs = T - 0.09, prevT = j ? T8[j - 1] : tImp0;
        if (t >= rs && t < fs) return lerp(LOW, PEAK, ease.outCubic((t - rs) / (fs - rs)));
        if (t >= fs && t < T) return lerp(PEAK, LOW, ease.inQuad((t - fs) / (T - fs)));
        if (t >= T) rest = LOW + bounce(t - T);
        if (t < rs) break;
      }
      return rest;
    };
    S.push({
      name: 't4 tied, pulled, dropped, eight times', t0: tCut, bg: 'cream',
      hits: [[tImp0, 10, 7, 0], ...T8.map((T, j) => [T, 8, 5, 0])],
      draw(E) {
        const t = E.t, g = E.g, I = E.ink;
        if (t < 78.10) TIE.forEach((l, k) => E.hand({ ...l, em, color: ink, trem: () => 0.6, seed: 60 + k, out: 0 }));
        else if (t < tCue) PULL.forEach((l, k) => E.hand({ ...l, em, color: ink, trem: () => 0.65, seed: 70 + k }));
        if (t >= tCue) {
          // the rope draws down from the top edge, the word hangs on its end
          const yb = yHang(t) * H, fz = 0.105 * H, fnt = FONTS.C(fz), m = measure(fnt, 'him', 0), top = yb - measure(fnt, 'h', 0).asc - 0.016 * H;
          const draw0 = ease.outCubic(clamp((t - tCue) / 0.35)), yEnd = lerp(-0.02 * H, top, draw0);
          I.save(); I.strokeStyle = ink; I.lineCap = 'round'; I.lineWidth = 7 * U; I.beginPath(); I.moveTo(ropeX, -0.02 * H); I.lineTo(ropeX, yEnd); I.stroke();
          I.globalCompositeOperation = 'destination-out'; I.lineWidth = 2.2 * U;                                // the twist: slanted gaps along the rope
          for (let y = -0.02 * H + (((t * 0) % 1) * 9 * U); y < yEnd; y += 9 * U) { I.beginPath(); I.moveTo(ropeX - 4 * U, y + 4 * U); I.lineTo(ropeX + 4 * U, y - 2 * U); I.stroke(); }
          I.globalCompositeOperation = 'source-over'; I.fillStyle = ink; I.beginPath(); I.arc(ropeX, yEnd + 3 * U, 6 * U, 0, 6.2832); I.fill();
          if (draw0 >= 0.85) { const a = clamp((draw0 - 0.85) / 0.15); I.font = fnt; I.letterSpacing = '0px'; I.textAlign = 'left'; I.textBaseline = 'alphabetic'; I.globalAlpha = a; I.fillStyle = ink; I.fillText('him', ropeX - m.adv / 2, yb); }
          I.restore();
        }
        if (t >= tw('t4', 'Eight')) {
          BI({ txt: 'EIGHT TIMES.', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.06, base: 0.585, times: [tw('t4', 'Eight'), tw('t4', 'times.')], curves: [E.HEAVY, E.PAYOFF] });
          // tally: seven strokes and one slash, one per fall
          const y0 = 0.612 * H, hh = 0.03 * H, sp = 0.032 * W;
          I.save(); I.strokeStyle = ink; I.lineCap = 'round'; I.lineWidth = 3.4 * U;
          T8.forEach((T, j) => {
            if (t < T) return; const p = ease.outCubic(clamp((t - T) / 0.07)), grp = j < 5 ? 0 : 1, k = j < 4 ? j : j - 5 + (j >= 5 ? 0 : 0), x = AX + (j < 5 ? Math.min(j, 3) : 4 + (j - 5)) * sp + 0.005 * W * noise1(j, 4);
            I.beginPath();
            if (j === 4) { I.moveTo(AX - 4 * U, y0 + hh * 0.85); I.lineTo(AX - 4 * U + (3 * sp + 14 * U) * p, y0 + hh * 0.85 - hh * 0.7 * p); }
            else { I.moveTo(x, y0); I.lineTo(x + 2 * U * noise1(j, 7), y0 + hh * p); }
            I.stroke();
          });
          I.restore();
        }
      },
    });
    E.hang = { yHang };
  }
  return S;
}
