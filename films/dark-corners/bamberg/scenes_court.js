// Beats 10 to 13: the court record. Cold paper, typed print, black stamp. 49.6 to 67.9 s.
import { clamp, ease, rgba, keys, withScale } from './lib.js';

export function buildCourt(E) {
  const { C, W, H, U, AX, MEAS } = E, tw = E.tw, K = C.cold;
  const S = [];
  const TY = (s) => E.line({ font: 'T', mode: 'type', color: K, perChar: 0.045, ...s });            // typed court print
  const BL = (s) => E.line({ color: K, ...s });                                                       // slammed display type
  const stack = (specs, top, gap, fn = BL) => { for (const s of E.stack(specs, top, gap).lines) fn(s); };
  const header = (t0, txt, a = 1) => { TY({ txt, cap: 0.0185, ls: 0.22, base: 0.178, times: txt.split(' ').map((_, i) => t0 + i * 0.28), alpha: a }); E.rule(AX, AX + MEAS, 0.19 * H, t0 + 0.2, 0.3, Math.max(2, 0.0021 * H), rgba(K, 0.55 * a), E.ink); };

  // ---------------------------------------------------------------- a1 to a3: 28 June 1628, the testimony
  {
    const tA2 = 55.05, tA3 = 59.60;
    S.push({
      name: 'a1-a3 court record, 28 June', t0: 49.60, bg: 'cold',
      hits: [[49.67, 8, 6, 0], [tw('a1', 'court,'), 4, 4, 0], [tw('a2', 'know.'), 5, 5, 0], [tw('a3', 'judges'), 7, 6, 0], [tw('a3', 'care.'), 6, 5, 0]],
      draw(E) {
        const t = E.t, ink = E.ink;
        if (t < tA3) {
          header(49.63, 'COURT RECORD');
          BL({ txt: '28 JUNE 1628', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, base: 0.285, times: tw('a1', 'court,'), mode: 'stamp', pivotX: AX });
        }
        if (t < tA2) {
          const L = [
            { txt: 'A WOMAN SAID SHE SAW', words: ['a', 'woman', 'said', 'she', 'saw'] },
            { txt: 'HIM DANCING WITH', words: ['him', 'dancing', 'with'] },
            { txt: 'WITCHES IN THE FOREST.', words: ['witches', 'in', 'the', 'forest.'] },
          ];
          L.forEach((l, k) => TY({ txt: l.txt, cap: 0.0235, ls: 0.02, base: 0.37 + k * 0.055, times: l.words.map((w, wi) => tw('a1', w, (w === 'in' ? 1 : 0))), out: tA2 }));
          // the word that matters
        } else if (t < tA3) {
          const Q = [
            { txt: 'HE ASKED HER HOW', words: ['he', 'asked', 'her', 'how'], id: 'a2' },
            { txt: 'SHE COULD HAVE', words: ['she', 'could', 'have'], id: 'a2' },
            { txt: 'SEEN THAT.', words: ['seen', 'that.'], id: 'a2' },
          ];
          Q.forEach((l, k) => TY({ txt: l.txt, cap: 0.0235, ls: 0.02, base: 0.37 + k * 0.05, times: l.words.map((w) => tw('a2', w)) }));
          TY({ txt: 'SHE SAID:', cap: 0.0235, ls: 0.06, base: 0.545, times: [tw('a2', 'she', 1), tw('a2', 'said:')] });
        }
        if (t >= tw('a2', 'I') - 0.02) {
          const id = BL({ txt: "I DON'T KNOW.", font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, base: t < tA3 ? 0.625 : 0.60, times: [tw('a2', 'I'), tw('a2', "don't"), tw('a2', 'know.')], curves: [null, null, E.PAYOFF] });
          // the judges: a black bar strikes the answer out
          const ts = tw('a3', 'judges') + 0.05;
          if (t >= ts) { const p = ease.outCubic(clamp((t - ts) / 0.22)), y = id.base - id.cap * 0.5; ink.fillStyle = K; ink.fillRect(AX - 6 * U, y - 0.011 * H, (id.inkW + 12 * U) * p, 0.022 * H); }
        }
        if (t >= tA3) {
          stack([
            { txt: 'THE JUDGES', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.03, times: [tw('a3', 'the'), tw('a3', 'judges')], curves: [null, E.HEAVY] },
            { txt: "DIDN'T CARE.", font: 'B', fit: 1.0, maxCap: 0.095, ls: 0.03, times: [tw('a3', "didn't"), tw('a3', 'care.')], curves: [E.HEAVY, E.PAYOFF] },
          ], 0.20, 0.024);
        }
      },
    });
  }

  // ---------------------------------------------------------------- t1: two days later, 30 June, they tortured him
  S.push({
    name: 't1 30 June, tortured', t0: 61.62, bg: 'cold',
    hits: [[tw('t1', 'two'), 4, 4, 0], [tw('t1', 'days'), 4, 4, 0], [tw('t1', 'later,'), 6, 5, 0], [tw('t1', 'tortured'), 9, 6, 0]],
    draw(E) {
      const t = E.t, a = tw('t1', 'days'), b = tw('t1', 'later,');
      header(61.64, 'COURT RECORD');
      const txt = t < a ? '28 JUNE 1628' : t < b ? '29 JUNE 1628' : '30 JUNE 1628', t0 = t < a ? tw('t1', 'two') : t < b ? a : b;
      BL({ txt, font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, base: 0.285, times: t < a ? 61.64 : t0, mode: 'stamp', pivotX: AX });
      TY({ txt: 'TWO DAYS LATER', cap: 0.0235, ls: 0.12, base: 0.34, times: [tw('t1', 'two'), tw('t1', 'days'), tw('t1', 'later,')] });
      stack([
        { txt: 'THEY', font: 'B', cap: 0.04, ls: 0.2, times: tw('t1', 'they') },
        { txt: 'TORTURED', font: 'B', fit: 1.0, maxCap: 0.095, ls: 0.03, times: tw('t1', 'tortured'), curve: E.PAYOFF },
        { txt: 'HIM.', font: 'B', fit: 0.5, maxCap: 0.095, ls: 0.03, times: tw('t1', 'him.'), curve: E.HEAVY },
      ], 0.40, 0.024);
    },
  });

  // ---------------------------------------------------------------- t2: the court wrote down that he felt no pain (stamped)
  S.push({
    name: 't2 felt no pain', t0: 64.60, bg: 'cold',
    hits: [[tw('t2', 'felt'), 4, 4, 0], [tw('t2', 'pain.'), 11, 7, 0]],
    draw(E) {
      const t = E.t, ink = E.ink;
      header(64.62, 'COURT RECORD');
      TY({ txt: 'THE COURT WROTE', cap: 0.0235, ls: 0.06, base: 0.255, times: [tw('t2', 'the'), tw('t2', 'court'), tw('t2', 'wrote')] });
      TY({ txt: 'DOWN THAT', cap: 0.0235, ls: 0.06, base: 0.305, times: [tw('t2', 'down'), tw('t2', 'that')] });
      BL({ txt: 'HE FELT', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.04, base: 0.415, times: [tw('t2', 'he'), tw('t2', 'felt')], curves: [null, E.HEAVY] });
      // NO PAIN. : the stamp
      const ts = tw('t2', 'no'), st = { txt: 'NO PAIN.', font: 'B', fit: 1.0, maxCap: 0.105, ls: 0.05, base: 0.565, times: [tw('t2', 'no'), tw('t2', 'pain.')], curves: [E.HEAVY, E.PAYOFF] };
      const G = E.geo(st), cx = G.inkL + G.inkW / 2, cy = G.base - G.cap / 2, pad = 0.022 * H, rot = -0.035;
      ink.save(); ink.translate(cx, cy); ink.rotate(rot); ink.translate(-cx, -cy);
      E.line({ ...st, color: K }, E.f, t);
      const tp = tw('t2', 'pain.'), k = (E.f - Math.ceil(tp * 24 - 1e-6));
      if (k >= 0) {
        const sc = keys(k, [[0, 1.12], [1, 1.04], [2, 1.0]]), bw = G.inkW + 2 * pad, bh = G.cap + 2 * pad;
        withScale(ink, cx, cy, sc, () => { ink.strokeStyle = K; ink.lineWidth = 0.0085 * H; ink.lineJoin = 'miter'; ink.strokeRect(cx - bw / 2, cy - bh / 2, bw, bh); ink.lineWidth = 0.003 * H; ink.strokeRect(cx - bw / 2 - 0.012 * H, cy - bh / 2 - 0.012 * H, bw + 0.024 * H, bh + 0.024 * H); });
      }
      ink.restore();
    },
  });
  return S;
}
