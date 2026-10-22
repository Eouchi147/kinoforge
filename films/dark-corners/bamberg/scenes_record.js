// Movements 3 and 4 (49.2 to 86 s): THE RECORD (cold court paper, typed print) and THE LETTER'S TRUTH (Junius's own hand against the record).
// Scenes: record1 (the page slides in from the right: 28 June), record2 (that page leaves upward: two days later), letter2 (his page is dropped on the record).
import { clamp, ease, lerp, rgba, keys, withScale, measure, FONTS, noise1, prefixAdv } from './lib.js';
import { makeKit } from './kit.js';

export function buildRecord(E) {
  const { C, W, H, U, AX, MEAS } = E, tw = E.tw, K = C.cold, ink = C.ink, kit = makeKit(E), B = kit.block;
  const S = [];
  const TY = (s) => E.line({ font: 'T', mode: 'type', color: K, perChar: 0.045, ls: 0, ...s });            // typed court print
  const BL = (s) => E.line({ color: K, ...s });                                                       // set display type
  const header = (t0, a = 1) => { E.line({ txt: 'COURT RECORD', font: 'T', mode: 'type', color: K, cap: 0.0185, ls: 0.22, base: 0.178, times: ['COURT', 'RECORD'].map((_, i) => t0 + i * 0.28), alpha: a, perChar: 0.045 }); E.rule(AX, AX + MEAS, 0.19 * H, t0 + 0.2, 0.3, Math.max(2, 0.0021 * H), rgba(K, 0.55 * a), E.ink); };

  // ================================================================ record1: "In court, a woman said she saw him dancing with witches in the forest. ... The judges didn't care."
  S.push({
    name: 'M3 record 1: 28 June, testimony', t0: 49.2, bg: 'cold', trans: { kind: 'slideIn', dir: 'right', dur: 0.66, ease: 'inOutCubic' },
    hits: [[49.946, 4, 5], [tw('a3', 'judges') + 0.05, 6, 5]],        // a date stamped on the page; the black bar of the judges struck across the answer
    draw(E) {
      const t = E.t, tA2 = 55.05, tA3 = 59.60;
      header(49.50);
      if (t < tA3) BL({ txt: '28 JUNE 1628', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, base: 0.285, times: tw('a1', 'court,'), mode: 'stamp', pivotX: AX });
      if (t < tA2 + 0.2) [
        { txt: 'A WOMAN SAID SHE SAW', words: ['a', 'woman', 'said', 'she', 'saw'] },
        { txt: 'HIM DANCING WITH', words: ['him', 'dancing', 'with'] },
        { txt: 'WITCHES IN THE FOREST.', words: ['witches', 'in', 'the', 'forest.'] },
      ].forEach((l, k) => TY({ txt: l.txt, cap: 0.0225, base: 0.37 + k * 0.055, times: l.words.map((w) => tw('a1', w, w === 'in' ? 1 : 0)), out: tA2, outDur: 0.18 }));
      else if (t < tA3) {
        [{ txt: 'HE ASKED HER HOW', words: ['he', 'asked', 'her', 'how'] }, { txt: 'SHE COULD HAVE', words: ['she', 'could', 'have'] }, { txt: 'SEEN THAT.', words: ['seen', 'that.'] }]
          .forEach((l, k) => TY({ txt: l.txt, cap: 0.0225, base: 0.37 + k * 0.05, times: l.words.map((w) => tw('a2', w)) }));
        TY({ txt: 'SHE SAID:', cap: 0.0235, ls: 0.06, base: 0.545, times: [tw('a2', 'she', 1), tw('a2', 'said:')] });
      }
      if (t >= tw('a2', 'I') - 0.02) {
        const id = BL({ txt: "I DON'T KNOW.", font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, base: t < tA3 ? 0.625 : 0.60, times: [tw('a2', 'I'), tw('a2', "don't"), tw('a2', 'know.')], curves: [null, null, E.PAYOFF] });
        const ts = tw('a3', 'judges') + 0.05;      // the judges: a black bar strikes the answer out
        if (t >= ts) { const p = ease.outCubic(clamp((t - ts) / 0.22)), y = id.base - id.cap * 0.5; E.ink.fillStyle = K; E.ink.fillRect(AX - 6 * U, y - 0.011 * H, (id.inkW + 12 * U) * p, 0.022 * H); }
      }
      if (t >= tA3 - 0.05) for (const s of E.stk([
        { txt: 'THE JUDGES', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.03, times: [tw('a3', 'the'), tw('a3', 'judges')], curves: [null, E.HEAVY] },
        { txt: "DIDN'T CARE.", font: 'B', fit: 1.0, maxCap: 0.095, ls: 0.03, times: [tw('a3', "didn't"), tw('a3', 'care.')], curves: [E.HEAVY, E.PAYOFF] },
      ], 0.20, 0.3).lines) BL(s);
    },
  });

  // ================================================================ record2: "Two days later, they tortured him. The court wrote down that he felt no pain."
  // The first page leaves upward and the next page of the record is under it. The day number rolls like an odometer: 28, 29, 30 (time passing, not three slams).
  S.push({
    name: 'M3 record 2: two days later, no pain', t0: 61.30, bg: 'cold', trans: { kind: 'slideOut', dir: 'top', dur: 0.56, ease: 'inOutCubic' },
    hits: [[tw('t2', 'pain.'), 7, 6]],                                  // the stamp NO PAIN strikes the page
    draw(E) {
      const t = E.t, I = E.ink; header(61.50);
      // the date: day number on a roller, the rest set as a stamp
      const spec = { txt: '28 JUNE 1628', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, base: 0.285 }, G = E.geo(spec), ln = G.ln, cap = G.cap, adv2 = prefixAdv(ln, 3);
      const rest = measure(ln.font, 'J', ln.ls);
      const tA = tw('t1', 'days'), tB = tw('t1', 'later,'), days = ['28', '29', '30'], idx = t < tA ? 0 : t < tB ? 1 : 2, tl = idx === 0 ? 61.62 : idx === 1 ? tA : tB;
      const roll = ease.outCubic(clamp((t - tl) / 0.28)), dayCell = (s, off, a) => { I.save(); I.beginPath(); I.rect(G.ox - 4 * U, G.base - cap * 1.12, adv2 * 0.95, cap * 1.3); I.clip(); I.font = ln.font; I.letterSpacing = ln.ls + 'px'; I.fillStyle = rgba(K, a); I.fillText(s, G.ox, G.base + off); I.restore(); };
      if (t >= 61.55) {
        const a0 = clamp((t - 61.55) / 0.12);
        if (idx === 0) dayCell(days[0], 0, a0); else { dayCell(days[idx - 1], -roll * cap * 1.25, 1 - roll); dayCell(days[idx], (1 - roll) * cap * 1.25, roll); }
        E.line({ txt: 'JUNE 1628', font: 'B', em: G.size / H, ls: 0.04, x: G.ox + adv2 - rest.l, base: 0.285, times: 61.55, mode: 'stamp', pivotX: G.ox + adv2, color: K });
      }
      TY({ txt: 'TWO DAYS LATER', cap: 0.0235, ls: 0.12, base: 0.34, times: [tw('t1', 'two'), tw('t1', 'days'), tw('t1', 'later,')], out: 64.50, outDur: 0.18 });
      if (t < 64.72) for (const s of E.stk([
        { txt: 'THEY', font: 'B', cap: 0.04, ls: 0.2, times: tw('t1', 'they') },
        { txt: 'TORTURED', font: 'B', fit: 1.0, maxCap: 0.095, ls: 0.03, times: tw('t1', 'tortured'), curve: E.PAYOFF },
        { txt: 'HIM.', font: 'B', fit: 0.5, maxCap: 0.095, ls: 0.03, times: tw('t1', 'him.'), curve: E.HEAVY },
      ], 0.40, 0.3).lines) BL({ ...s, out: 64.50, outDur: 0.2 });
      // t2: the court wrote down that he felt no pain (stamped, boxed)
      if (t >= tw('t2', 'the') - 0.05) {
        TY({ txt: 'THE COURT WROTE', cap: 0.0235, ls: 0.06, base: 0.36, times: [tw('t2', 'the'), tw('t2', 'court'), tw('t2', 'wrote')] });
        TY({ txt: 'DOWN THAT', cap: 0.0235, ls: 0.06, base: 0.41, times: [tw('t2', 'down'), tw('t2', 'that')] });
        BL({ txt: 'HE FELT', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.04, base: 0.495, times: [tw('t2', 'he'), tw('t2', 'felt')], curves: [null, E.HEAVY] });
        const st = { txt: 'NO PAIN.', font: 'B', fit: 0.9, maxCap: 0.09, ls: 0.05, x: AX + 0.034 * H, base: 0.625, times: [tw('t2', 'no'), tw('t2', 'pain.')], curves: [E.HEAVY, E.PAYOFF] };
        const S2 = E.geo(st), cx = S2.inkL + S2.inkW / 2, cy = S2.base - S2.cap / 2, pad = 0.02 * H, rot = -0.035;
        I.save(); I.translate(cx, cy); I.rotate(rot); I.translate(-cx, -cy);
        E.line({ ...st, color: K }, E.f, t);
        const tp = tw('t2', 'pain.'), k = E.f - Math.ceil(tp * 24 - 1e-6);
        if (k >= 0) { const sc = keys(k, [[0, 1.10], [1, 1.035], [2, 1.0]]), bw = S2.inkW + 2 * pad, bh = S2.cap + 2 * pad; withScale(I, cx, cy, sc, () => { I.strokeStyle = K; I.lineWidth = 0.0085 * H; I.lineJoin = 'miter'; I.strokeRect(cx - bw / 2, cy - bh / 2, bw, bh); I.lineWidth = 0.003 * H; I.strokeRect(cx - bw / 2 - 0.012 * H, cy - bh / 2 - 0.012 * H, bw + 0.024 * H, bh + 0.024 * H); }); }
        I.restore();
      }
    },
  });

  // ================================================================ letter2: "In his letter, he wrote something very different. They crushed his thumbs ... pulled him up by a rope, and dropped him. Eight times."
  // His page is dropped on the court's (it lands on the music hit 67.895): his own hand against the record.
  const em = Math.min(E.emFit('C', 'They crushed', 0.92), 0.075), P = 0.088, hand = (l, k, seed, extra = {}) => E.hand({ ...l, em, color: ink, seed, ...extra });
  const HL = [
    { txt: 'They crushed', base: 0.205, times: [tw('t3', 'They'), tw('t3', 'crushed')] }, { txt: 'his thumbs', base: 0.205 + P, times: [tw('t3', 'his', 1), tw('t3', 'thumbs')] },
    { txt: 'until blood', base: 0.205 + 2 * P, times: [tw('t3', 'until'), tw('t3', 'blood')] }, { txt: 'came out', base: 0.205 + 3 * P, times: [tw('t3', 'came'), tw('t3', 'out')] },
    { txt: 'from under', base: 0.205 + 4 * P, times: [tw('t3', 'from'), tw('t3', 'under')] }, { txt: 'his nails.', base: 0.205 + 5 * P, times: [tw('t3', 'his', 2), tw('t3', 'nails.')] },
  ];
  const TIE = [
    { txt: 'They tied', base: 0.205, times: [tw('t4', 'They'), tw('t4', 'tied')] }, { txt: 'his hands', base: 0.205 + P, times: [tw('t4', 'his'), tw('t4', 'hands')] },
    { txt: 'behind', base: 0.205 + 2 * P, times: [tw('t4', 'behind')] }, { txt: 'his back,', base: 0.205 + 3 * P, times: [tw('t4', 'his', 1), tw('t4', 'back,')] },
  ];
  const PULL = [
    { txt: 'pulled', base: 0.205, times: [tw('t4', 'pulled')] }, { txt: 'him up', base: 0.205 + P, times: [tw('t4', 'him'), tw('t4', 'up')] }, { txt: 'by a rope,', base: 0.205 + 2 * P, times: [tw('t4', 'by'), tw('t4', 'a'), tw('t4', 'rope,')] },
  ];
  const tDrop = 81.58, tImp0 = tDrop + 0.22, T8 = [83.56, 83.87, 84.22, 84.50, 84.80, 85.08, 85.40, 85.72], tCue = 79.95;
  const HIGH = 0.31, LOW = 0.465, PEAK = 0.385, ropeX = 0.5 * W;
  const bounce = (s) => (s < 0 ? 0 : 0.02 * Math.exp(-9 * s) * Math.sin(s * 32));
  const yHang = (t) => {                                                    // the hanging word: baseline (H units) as a pure function of time
    if (t < tDrop) return HIGH + (t > 80.5 ? 0.0035 * Math.sin(t * 38) * clamp((t - 80.5) / 0.6) : 0);
    if (t < tImp0) return lerp(HIGH, LOW, ease.inQuad(clamp((t - tDrop) / 0.22)));
    let rest = LOW + bounce(t - tImp0);
    for (let j = 0; j < T8.length; j++) { const T = T8[j], rs = T - 0.21, fs = T - 0.09; if (t >= rs && t < fs) return lerp(LOW, PEAK, ease.outCubic((t - rs) / (fs - rs))); if (t >= fs && t < T) return lerp(PEAK, LOW, ease.inQuad((t - fs) / (T - fs))); if (t >= T) rest = LOW + bounce(t - T); if (t < rs) break; }
    return rest;
  };
  E.tally = { x0: AX, y0: 0.612 * H, hh: 0.03 * H, sp: 0.032 * W };
  S.push({
    name: 'M4 letter 2: thumbs, rope, eight times', t0: 67.395, bg: 'cream', trans: { kind: 'slideIn', dir: 'top', dur: 0.5, ease: 'inCubic' },
    // jobs: the page lands on the record (67.895); the rope load comes down (81.8); each of the eight falls (a shake per fall is the fall itself)
    hits: [[67.895, 8, 6], [tImp0, 9, 7], ...T8.map((T) => [T, 6, 5])],
    draw(E) {
      const t = E.t, g = E.g, I = E.ink;
      if (t < 70.98) B([
        { txt: 'IN HIS LETTER,', font: 'B', cap: 0.035, ls: 0.16, times: [tw('t3', 'in'), tw('t3', 'his'), tw('t3', 'letter,')] },
        { txt: 'HE WROTE SOMETHING', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.04, times: [tw('t3', 'he'), tw('t3', 'wrote'), tw('t3', 'something')] },
        { txt: 'VERY', font: 'B', cap: 0.05, ls: 0.2, times: tw('t3', 'very') },
        { txt: 'DIFFERENT.', font: 'B', fit: 1.0, maxCap: 0.105, ls: 0.03, times: tw('t3', 'different.'), curve: E.PAYOFF },
      ], 0.19, { color: ink, out: 70.84, outDur: 0.2 });
      else if (t < 75.35) {
        const a = 1 - clamp((t - 75.02) / 0.3); I.save(); I.globalAlpha = a;
        HL.forEach((l, k) => E.hand({ ...l, em, color: ink, trem: () => 0.5 + 0.12 * k, seed: 40 + k, squash: k === 1 ? { w: 1, k: (tt) => 1 - 0.30 * ease.outCubic(clamp((tt - tw('t3', 'thumbs') - 0.12) / 0.2)) } : null }));
        const tt = tw('t3', 'thumbs') + 0.04, p = ease.outCubic(clamp((t - tt) / 0.22));       // the plates close on "thumbs": the one image of the act, objects only
        if (t >= tt) {
          const w = E.handWord({ ...HL[1], em }, 1), cy = w.base - w.cap * 0.45, h = w.cap * 2.0, pw = 0.016 * W, gap = 6 * U, wc = (w.x0 + w.x1) / 2, hw = (w.x1 - w.x0) / 2;
          const sq = 1 - 0.30 * ease.outCubic(clamp((t - tw('t3', 'thumbs') - 0.12) / 0.2)), tx = hw * sq + gap; I.fillStyle = ink;
          const xl = lerp(w.x0 - 0.14 * W, wc - tx - pw, p), xr = lerp(w.x1 + 0.14 * W, wc + tx, p);
          I.fillRect(xl, cy - h / 2, pw, h); I.fillRect(xr, cy - h / 2, pw, h); I.fillRect(xr + pw, cy - 3 * U, 0.025 * W, 6 * U); I.fillRect(xr + pw + 0.025 * W - 2 * U, cy - 11 * U, 6 * U, 22 * U);
        }
        I.restore();
      }
      if (t >= 75.1 && t < 78.40) TIE.forEach((l, k) => E.hand({ ...l, em, color: ink, trem: () => 0.6, seed: 60 + k, out: 78.10, outDur: 0.25 }));
      if (t >= 78.1 && t < tCue + 0.3) PULL.forEach((l, k) => E.hand({ ...l, em, color: ink, trem: () => 0.65, seed: 70 + k, out: tCue - 0.06, outDur: 0.22 }));
      if (t >= tCue) {                                                  // the rope draws down from the top edge and the word hangs on its end
        const yb = yHang(t) * H, fz = 0.105 * H, fnt = FONTS.C(fz), m = measure(fnt, 'him', 0), top = yb - measure(fnt, 'h', 0).asc - 0.016 * H;
        const draw0 = ease.outCubic(clamp((t - tCue) / 0.35)), yEnd = lerp(-0.02 * H, top, draw0);
        I.save(); I.strokeStyle = ink; I.lineCap = 'round'; I.lineWidth = 7 * U; I.beginPath(); I.moveTo(ropeX, -0.02 * H); I.lineTo(ropeX, yEnd); I.stroke();
        I.globalCompositeOperation = 'destination-out'; I.lineWidth = 2.2 * U; for (let y = -0.02 * H; y < yEnd; y += 9 * U) { I.beginPath(); I.moveTo(ropeX - 4 * U, y + 4 * U); I.lineTo(ropeX + 4 * U, y - 2 * U); I.stroke(); }
        I.globalCompositeOperation = 'source-over'; I.fillStyle = ink; I.beginPath(); I.arc(ropeX, yEnd + 3 * U, 6 * U, 0, 6.2832); I.fill();
        if (draw0 >= 0.85) { I.font = fnt; I.letterSpacing = '0px'; I.textAlign = 'left'; I.textBaseline = 'alphabetic'; I.globalAlpha = clamp((draw0 - 0.85) / 0.15); I.fillStyle = ink; I.fillText('him', ropeX - m.adv / 2, yb); }
        I.restore();
      }
      if (t >= tw('t4', 'Eight')) {
        E.line({ txt: 'EIGHT TIMES.', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.06, base: 0.585, times: [tw('t4', 'Eight'), tw('t4', 'times.')], curves: [E.HEAVY, E.PAYOFF], color: ink });
        // the tally: seven strokes and one slash, one per fall (it is the count the next scene inherits)
        const { y0, hh, sp } = E.tally; I.save(); I.strokeStyle = ink; I.lineCap = 'round'; I.lineWidth = 3.4 * U;
        T8.forEach((T, j) => { if (t < T) return; const p = ease.outCubic(clamp((t - T) / 0.07)), x = AX + (j < 5 ? Math.min(j, 3) : 4 + (j - 5)) * sp + 0.005 * W * noise1(j, 4); I.beginPath();
          if (j === 4) { I.moveTo(AX - 4 * U, y0 + hh * 0.85); I.lineTo(AX - 4 * U + (3 * sp + 14 * U) * p, y0 + hh * 0.85 - hh * 0.7 * p); } else { I.moveTo(x, y0); I.lineTo(x + 2 * U * noise1(j, 7), y0 + hh * p); } I.stroke(); });
        I.restore();
      }
    },
  });
  return S;
}
