// Beats 5 to 9: who he was, the fear, the method and the chain of accusations on the dark city map (15.3 to 49.6 s).
import { clamp, ease, rgba } from './lib.js';
import { createMap } from './map.js';

export function buildCtx(E) {
  const { C, W, H, U } = E, tw = E.tw, cream = C.cream, M = createMap(E);
  const S = [];
  const dim = (to = 0.45, a0 = 0.8) => { const g = E.g, gr = g.createLinearGradient(0, 0, 0, to * H); gr.addColorStop(0, `rgba(14,13,11,${a0})`); gr.addColorStop(0.8, `rgba(14,13,11,${a0 * 0.8})`); gr.addColorStop(1, 'rgba(14,13,11,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, to * H); };
  const L = (s, extra = {}) => E.line({ color: cream, ...s, ...extra });
  const stack = (specs, top, gap, extra = {}) => { for (const s of E.stack(specs, top, gap).lines) L(s, extra); };

  // ---------------------------------------------------------------- x1: His name was Johannes Junius. He lived in Bamberg, in Germany.
  S.push({
    name: 'x1a johannes junius', t0: 15.30, bg: 'dark',
    hits: [[tw('x1', 'Johannes'), 4, 4, 0.03], [tw('x1', 'Junius.'), 6, 5, 0.05]],
    draw(E) {
      stack([
        { txt: 'HIS NAME WAS', font: 'B', cap: 0.040, ls: 0.16, times: [tw('x1', 'his'), tw('x1', 'name'), tw('x1', 'was')] },
        { txt: 'JOHANNES', font: 'B', fit: 1.0, maxCap: 0.105, ls: 0.02, times: tw('x1', 'Johannes'), curve: E.HEAVY },
        { txt: 'JUNIUS.', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.03, times: tw('x1', 'Junius.'), curve: E.PAYOFF },
      ], 0.26, 0.026);
    },
  });
  S.push({
    name: 'x1b he lived in bamberg', t0: 18.70, bg: 'dark',
    hits: [[tw('x1', 'Bamberg,'), 5, 5, 0.04]],
    draw(E) {
      const t = E.t, c = M.cam(t); M.drawStreets(t, 18.85, 2.6, 0.9, c); dim(0.50, 0.85);
      L({ txt: 'JOHANNES JUNIUS', font: 'B', cap: 0.030, ls: 0.14, base: 0.185, times: 18.72, mode: 'pop', alpha: 0.55 });
      stack([
        { txt: 'HE LIVED IN', font: 'B', cap: 0.040, ls: 0.16, times: [tw('x1', 'he'), tw('x1', 'lived'), tw('x1', 'in')] },
        { txt: 'BAMBERG,', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.03, times: tw('x1', 'Bamberg,'), curve: E.PAYOFF },
        { txt: 'IN GERMANY.', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.04, times: [tw('x1', 'in', 1), tw('x1', 'Germany.')], curve: E.HEAVY },
      ], 0.235, 0.026);
    },
  });

  // ---------------------------------------------------------------- x2: the fear, the hunt
  {
    const tA = 21.38, tB = 24.40, tL = 28.95;
    S.push({
      name: 'x2 witches, storms, the hunt', t0: 21.40, bg: 'dark',
      hits: [[tw('x2', 'witches'), 4, 4, 0.03], [tw('x2', 'storms,'), 3, 3, 0.02], [tw('x2', 'sickness'), 3, 3, 0.02], [tw('x2', 'harvests.'), 5, 4, 0.04], [tw('x2', 'Bamberg'), 4, 4, 0.03], [tw('x2', 'down.'), 7, 6, 0.06]],
      draw(E) {
        const t = E.t, c = M.cam(t); M.drawStreets(t, 18.85, 2.6, 0.9, c); dim(0.70, 0.78);
        if (t < tB) stack([
          { txt: 'AT THAT TIME,', font: 'B', cap: 0.038, ls: 0.14, times: [tw('x2', 'at'), tw('x2', 'that'), tw('x2', 'time,')] },
          { txt: 'MANY PEOPLE', font: 'B', fit: 1.0, maxCap: 0.07, ls: 0.03, times: [tw('x2', 'many'), tw('x2', 'people')] },
          { txt: 'BELIEVED', font: 'B', fit: 1.0, maxCap: 0.10, ls: 0.03, times: tw('x2', 'believed'), curve: E.HEAVY },
        ], 0.235, 0.026);
        else if (t < tL) {
          stack([
            { txt: 'WITCHES CAUSED', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.06, times: [tw('x2', 'witches'), tw('x2', 'caused')], curves: [E.HEAVY, null] },
            { txt: 'STORMS', font: 'B', fit: 0.9, maxCap: 0.08, ls: 0.03, times: tw('x2', 'storms,') },
            { txt: 'SICKNESS', font: 'B', fit: 0.9, maxCap: 0.08, ls: 0.03, times: tw('x2', 'sickness') },
            { txt: 'FAILED', font: 'B', fit: 0.9, maxCap: 0.08, ls: 0.03, times: tw('x2', 'failed') },
            { txt: 'HARVESTS.', font: 'B', fit: 0.9, maxCap: 0.08, ls: 0.03, times: tw('x2', 'harvests.'), curve: E.PAYOFF },
          ], 0.17, 0.020);
        } else stack([
          { txt: 'AND THE RULERS', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.04, times: [tw('x2', 'and', 1), tw('x2', 'the'), tw('x2', 'rulers')] },
          { txt: 'OF BAMBERG', font: 'B', fit: 1.0, maxCap: 0.07, ls: 0.03, times: [tw('x2', 'of'), tw('x2', 'Bamberg')], curves: [null, E.HEAVY] },
          { txt: 'DECIDED TO', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.04, times: [tw('x2', 'decided'), tw('x2', 'to')] },
          { txt: 'HUNT THEM', font: 'B', fit: 1.0, maxCap: 0.08, ls: 0.03, times: [tw('x2', 'hunt'), tw('x2', 'them')], curves: [E.HEAVY, null] },
          { txt: 'DOWN.', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.04, times: tw('x2', 'down.'), curve: E.PAYOFF },
        ], 0.165, 0.016);
      },
    });
  }

  // ---------------------------------------------------------------- x3: the method (the chain starts to grow)
  {
    const tB1 = 35.40, tB2 = 36.90, tB3 = 39.55;
    S.push({
      name: 'x3 their method', t0: 33.10, bg: 'dark',
      hits: [[tw('x3', 'simple.'), 5, 5, 0.04], [tw('x3', 'Torture'), 5, 5, 0.04], [tw('x3', 'names.'), 6, 5, 0.05], [tw('x3', 'people.'), 6, 5, 0.05]],
      draw(E) {
        const t = E.t, c = M.cam(t); M.drawStreets(t, 18.85, 2.6, 0.9 * (t < 35.4 ? 0.7 : 1), c); M.drawChain(t, c); dim(0.42, 0.85);
        if (t < tB1) stack([
          { txt: 'THEIR METHOD', font: 'B', fit: 1.0, maxCap: 0.07, ls: 0.03, times: [tw('x3', 'their'), tw('x3', 'method')] },
          { txt: 'WAS SIMPLE.', font: 'B', fit: 1.0, maxCap: 0.09, ls: 0.03, times: [tw('x3', 'was'), tw('x3', 'simple.')], curves: [null, E.PAYOFF] },
        ], 0.22, 0.026);
        else if (t < tB2) stack([{ txt: 'ARREST SOMEONE.', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.03, times: [tw('x3', 'arrest'), tw('x3', 'someone.')], curves: [E.HEAVY, E.HEAVY] }], 0.22, 0.02);
        else if (t < tB3) stack([
          { txt: 'TORTURE THEM', font: 'B', fit: 1.0, maxCap: 0.065, ls: 0.03, times: [tw('x3', 'torture'), tw('x3', 'them')], curves: [E.PAYOFF, null] },
          { txt: 'UNTIL THEY GIVE', font: 'B', fit: 0.8, maxCap: 0.04, ls: 0.05, times: [tw('x3', 'until'), tw('x3', 'they'), tw('x3', 'give')] },
          { txt: 'NAMES.', font: 'B', fit: 0.85, maxCap: 0.085, ls: 0.04, times: tw('x3', 'names.'), curve: E.PAYOFF },
        ], 0.18, 0.022);
        else stack([
          { txt: 'THEN ARREST', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.04, times: [tw('x3', 'then'), tw('x3', 'arrest', 1)] },
          { txt: 'THOSE PEOPLE.', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, times: [tw('x3', 'those'), tw('x3', 'people.')], curves: [null, E.PAYOFF] },
        ], 0.19, 0.022);
      },
    });
  }
  S.push({
    name: 'x4 his wife named, executed', t0: 41.60, bg: 'dark',
    hits: [[tw('x4', "Junius's"), 4, 4, 0.03], [tw('x4', 'named.'), 5, 5, 0.04], [tw('x4', 'executed.'), 7, 6, 0.06]],
    draw(E) {
      const t = E.t, c = M.cam(t); M.drawStreets(t, 18.85, 2.6, 0.9, c); M.drawChain(t, c); dim(0.42, 0.85);
      const tB = 44.40;
      if (t < tB) stack([
        { txt: "JUNIUS'S WIFE", font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.03, times: [tw('x4', "Junius's"), tw('x4', 'wife')], curves: [E.HEAVY, null] },
        { txt: 'WAS NAMED.', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, times: [tw('x4', 'was'), tw('x4', 'named.')], curves: [null, E.PAYOFF] },
      ], 0.20, 0.024);
      else stack([
        { txt: 'SHE WAS', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.08, times: [tw('x4', 'she'), tw('x4', 'was', 1)] },
        { txt: 'EXECUTED.', font: 'B', fit: 1.0, maxCap: 0.095, ls: 0.03, times: tw('x4', 'executed.'), curve: E.PAYOFF },
      ], 0.20, 0.024);
    },
  });
  S.push({
    name: 'x5 six people named him', t0: 47.00, bg: 'dark',
    hits: [[tw('x5', 'six'), 7, 6, 0.06], [tw('x5', 'him.'), 5, 5, 0.04]],
    draw(E) {
      const t = E.t, c = M.cam(t); M.drawStreets(t, 18.85, 2.6, 0.9, c); M.drawChain(t, c); dim(0.40, 0.85);
      stack([
        { txt: 'THEN', font: 'B', cap: 0.035, ls: 0.2, times: tw('x5', 'then') },
        { txt: 'SIX', font: 'B', fit: 0.5, maxCap: 0.15, ls: 0.03, times: tw('x5', 'six'), curve: E.PAYOFF },
        { txt: 'PEOPLE NAMED HIM.', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.04, times: [tw('x5', 'people'), tw('x5', 'named'), tw('x5', 'him.')], curves: [null, E.HEAVY, E.HEAVY] },
      ], 0.155, 0.02);
    },
  });
  E.M = M;
  return S;
}
