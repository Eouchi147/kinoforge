// Beats 1 to 4: the opening promise (0 to 13 s) and the series title card (13 to 15.3 s).
import { clamp, ease, rgba } from './lib.js';

export function buildOpen(E) {
  const { C, W, H, U, AX, MEAS } = E, tw = E.tw;
  const cream = C.cream, ink = C.ink;
  const S = [];

  // ---------------------------------------------------------------- o1: "In 1628, a German mayor was arrested and accused of being a witch."
  {
    const tYear = 0.625, tOut1 = 3.40;
    S.push({
      name: 'o1 1628, a mayor arrested', t0: 0, bg: 'dark',
      hits: [[tYear, 7, 5, 0.05], [tw('o1', 'arrested'), 4, 4, 0.03], [tw('o1', 'witch.'), 5, 5, 0.04]],
      draw(E) {
        const Y = E.line({ txt: '1628', font: 'B', cap: 0.118, ls: 0.01, base: 0.285, times: tYear, mode: 'stamp', smear: true, color: cream });
        E.rule(E.AX, E.AX + Y.inkW, 0.30 * H, tYear + 0.14, 0.2, Math.max(2, 0.0021 * H), rgba(cream, 0.5));
        const b1 = E.stack([
          { txt: 'A GERMAN MAYOR', font: 'B', fit: 1.0, ls: 0.02, times: [tw('o1', 'a'), tw('o1', 'German'), tw('o1', 'mayor')] },
          { txt: 'WAS ARRESTED', font: 'B', fit: 1.0, ls: 0.01, times: [tw('o1', 'was'), tw('o1', 'arrested')], curves: [null, E.HEAVY] },
        ], 0.345, 0.024);
        for (const s of b1.lines) E.line({ ...s, color: cream, out: tOut1 });
        const b2 = E.stack([
          { txt: 'AND ACCUSED', font: 'B', fit: 1.0, ls: 0.02, times: [tw('o1', 'and'), tw('o1', 'accused')] },
          { txt: 'OF BEING A', font: 'B', fit: 1.0, ls: 0.03, times: [tw('o1', 'of'), tw('o1', 'being'), tw('o1', 'a', 1)] },
          { txt: 'WITCH.', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.04, times: tw('o1', 'witch.'), curve: E.PAYOFF },
        ], 0.345, 0.024);
        for (const s of b2.lines) E.line({ ...s, color: cream });
      },
    });
  }

  // ---------------------------------------------------------------- o2: "In prison, he wrote a secret letter to his daughter."
  {
    S.push({
      name: 'o2a in prison', t0: 5.95, bg: 'dark',
      hits: [[tw('o2', 'prison,'), 5, 4, 0.04]],
      draw(E) {
        const t0 = tw('o2', 'prison,');
        // cell bars: seven hairlines that draw down from the top edge on the word
        for (let k = 0; k < 7; k++) { const x = (0.13 + k * 0.12) * W, p = ease.outCubic(clamp((E.t - t0 - k * 0.04) / 0.25)); if (p > 0) { E.g.fillStyle = rgba(cream, 0.16); E.g.fillRect(x, 0, Math.max(2, 3 * U), H * p); } }
        for (const s of E.stack([
          { txt: 'IN', font: 'B', cap: 0.05, ls: 0.1, times: tw('o2', 'in') },
          { txt: 'PRISON', font: 'B', fit: 1.0, maxCap: 0.13, ls: 0.02, times: t0, curve: E.PAYOFF },
        ], 0.30, 0.03).lines) E.line({ ...s, color: cream });
      },
    });
    S.push({
      name: 'o2b he wrote a secret letter', t0: tw('o2', 'he'), bg: 'cream',
      hits: [[tw('o2', 'he'), 10, 6, 0.0]],
      draw(E) {
        E.line({ txt: 'HE WROTE', font: 'B', cap: 0.045, ls: 0.14, base: 0.205, times: [tw('o2', 'he'), tw('o2', 'wrote')], color: ink });
        const em = E.emFit('C', 'a secret letter', 0.97);
        E.hand({ txt: 'a secret letter', em, base: 0.34, times: [tw('o2', 'a'), tw('o2', 'secret'), tw('o2', 'letter')], color: ink, trem: () => 0.5, seed: 3 });
        E.hand({ txt: 'to his daughter.', em: E.emFit('C', 'to his daughter.', 0.97), base: 0.47, times: [tw('o2', 'to'), tw('o2', 'his'), tw('o2', 'daughter.')], color: ink, trem: () => 0.5, seed: 4 });
        E.stroke(AX, AX + 0.60 * MEAS, 0.49 * H, tw('o2', 'daughter.') + 0.5, 0.4, 0.008 * H, ink, { seed: 9 });
      },
    });
  }

  // ---------------------------------------------------------------- o3: "Everything you're about to hear really happened."
  S.push({
    name: 'o3 really happened', t0: 9.35, bg: 'dark',
    hits: [[tw('o3', 'about'), 3, 4, 0.02], [tw('o3', 'happened.'), 6, 5, 0.05]],
    draw(E) {
      const b = E.stack([
        { txt: "EVERYTHING YOU'RE", font: 'B', fit: 1.0, maxCap: 0.045, ls: 0.04, times: [tw('o3', 'Everything'), tw('o3', "you're")] },
        { txt: 'ABOUT TO HEAR', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.03, times: [tw('o3', 'about'), tw('o3', 'to'), tw('o3', 'hear')] },
        { txt: 'REALLY', font: 'B', fit: 1.0, maxCap: 0.105, ls: 0.04, times: tw('o3', 'really'), curve: E.HEAVY },
        { txt: 'HAPPENED.', font: 'B', fit: 1.0, maxCap: 0.1, ls: 0.03, times: tw('o3', 'happened.'), curve: E.PAYOFF },
      ], 0.20, 0.024);
      for (const s of b.lines) E.line({ ...s, color: cream });
    },
  });

  // ---------------------------------------------------------------- the series title card
  {
    const tT = 13.15;
    S.push({
      name: 'title card', t0: 12.9, bg: 'dark',
      hits: [[tT, 6, 5, 0.05]],
      draw(E) { E.titleCard(tT, 15.05, 0.22); },
    });
  }
  return S;
}
