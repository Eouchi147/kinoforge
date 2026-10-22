// Movements 1 and 2 (0 to 49.2 s): THE PROMISE (a date, a cell, a letter, the title) and THE TOWN (who he was, the plan of Bamberg, the chain of accusations).
// Scenes: desk1 (0 to 6.35), letter1 (6.35 to 9.28, slides onto the desk), desk2 (9.28 to 49.2, the letter is pulled away; title; the map).
import { clamp, ease, lerp, rgba } from './lib.js';
import { createMap } from './map.js';
import { makeKit } from './kit.js';

export function buildOpen(E) {
  const { C, W, H, U, AX, MEAS } = E, tw = E.tw, cream = C.cream, ink = C.ink, kit = makeKit(E), B = kit.block, M = createMap(E);
  E.M = M;
  const S = [];

  // ================================================================ desk1: "In 1628, a German mayor was arrested and accused of being a witch. In prison,"
  S.push({
    name: 'M1 desk: 1628, mayor, witch, prison', t0: 0, bg: 'dark',
    // job of each hit: the date is stamped onto the desk (a stamp strikes a surface)
    hits: [[0.65, 3, 5]],
    draw(E) {
      const t = E.t, tYear = 0.625, tOut1 = 3.40, tOut2 = 5.97;
      // the anchor: WHEN. It stays while the story clauses change, and leaves when the place (a cell) replaces it.
      const al = 1 - clamp((t - tOut2) / 0.14);
      if (al > 0) {
        E.line({ txt: 'IN', font: 'B', cap: 0.026, ls: 0.3, base: 0.172, times: tw('o1', 'in'), color: cream, alpha: al });
        const Y = E.line({ txt: '1628', font: 'B', cap: 0.118, ls: 0.01, base: 0.315, times: tYear, mode: 'stamp', smear: true, color: cream, alpha: al });
        E.rule(E.AX, E.AX + Y.inkW, 0.33 * H, tYear + 0.14, 0.2, Math.max(2, 0.0021 * H), rgba(cream, 0.5 * al));
      }
      if (t < tOut1 + 0.3) B([
        { txt: 'A GERMAN MAYOR', font: 'B', fit: 1.0, ls: 0.02, times: [tw('o1', 'a'), tw('o1', 'German'), tw('o1', 'mayor')] },
        { txt: 'WAS ARRESTED', font: 'B', fit: 1.0, ls: 0.01, times: [tw('o1', 'was'), tw('o1', 'arrested')], curves: [null, E.HEAVY] },
      ], 0.375, { out: tOut1, outDur: 0.2, k: 0.3 });
      if (t >= tw('o1', 'and') - 0.05 && t < tOut2 + 0.2) B([
        { txt: 'AND ACCUSED', font: 'B', fit: 1.0, ls: 0.02, times: [tw('o1', 'and'), tw('o1', 'accused')] },
        { txt: 'OF BEING A', font: 'B', fit: 1.0, ls: 0.03, times: [tw('o1', 'of'), tw('o1', 'being'), tw('o1', 'a', 1)] },
        { txt: 'WITCH.', font: 'B', fit: 1.0, maxCap: 0.105, ls: 0.04, times: tw('o1', 'witch.'), curve: E.PAYOFF },
      ], 0.362, { out: tOut2, outDur: 0.14, k: 0.3 });
      // the place: a cell. Seven hairlines of light fall from the top and the lower half of the desk takes their stripes.
      const t0 = tw('o2', 'prison,');
      if (t >= tw('o2', 'in') - 0.02) {
        const g = E.g;
        for (let k = 0; k < 7; k++) { const x = (0.13 + k * 0.12) * W, p = ease.outCubic(clamp((t - t0 - k * 0.04) / 0.28)); if (p > 0) { g.fillStyle = rgba(cream, 0.16); g.fillRect(x, 0, Math.max(2, 3 * U), H * p); g.fillStyle = rgba(cream, 0.032 * p); g.fillRect(x + 0.014 * W, 0.66 * H, 0.05 * W, 0.34 * H); } }
        for (const s of E.stk([
          { txt: 'IN', font: 'B', cap: 0.05, ls: 0.1, times: tw('o2', 'in') },
          { txt: 'PRISON', font: 'B', fit: 1.0, maxCap: 0.13, ls: 0.02, times: t0, curve: E.PAYOFF },
        ], 0.30, 0.3).lines) E.line({ color: cream, ...s });
      }
    },
  });

  // ================================================================ letter1: "he wrote a secret letter to his daughter." The letter is laid on the desk while he writes it.
  S.push({
    name: 'M1 letter: he wrote a secret letter', t0: 6.35, bg: 'cream', trans: { kind: 'slideIn', dir: 'bottom', dur: 0.62, ease: 'outCubic' },
    // job: the page lands on the desk (no shake: it is laid, not dropped)
    draw(E) {
      E.line({ txt: 'HE WROTE', font: 'B', cap: 0.045, ls: 0.14, base: 0.205, times: [tw('o2', 'he'), tw('o2', 'wrote')], color: ink });
      const em = E.emFit('C', 'daughter.', 0.74), P = 0.105, hd = (txt, row, ts, seed) => E.hand({ txt, em, base: 0.31 + row * P, times: ts, color: ink, trem: () => 0.5, seed });
      hd('a secret', 0, [tw('o2', 'a'), tw('o2', 'secret')], 3); hd('letter', 1, [tw('o2', 'letter')], 4); hd('to his', 2, [tw('o2', 'to'), tw('o2', 'his')], 5);
      const D = hd('daughter.', 3, [tw('o2', 'daughter.')], 6);
      E.stroke(AX, AX + D.inkW * 0.98, (0.31 + 3 * P) * H + 0.018 * H, tw('o2', 'daughter.') + 0.36, 0.34, 0.007 * H, ink, { seed: 9 });   // the underline: he stresses "daughter"
    },
  });

  // ================================================================ desk2: the letter is set aside; "Everything you're about to hear really happened"; the title; HIS NAME; the plan of Bamberg; the chain
  const tTitle = 13.15, tMorph = [18.52, 19.12];
  S.push({
    name: 'M1/M2 desk: really happened, title, Junius, the town, the chain', t0: 9.28, bg: 'dark', trans: { kind: 'slideOut', dir: 'bottom', dur: 0.6, ease: 'outCubic' },
    // jobs: the title stamp strikes the desk; the rest of the hits are carried by the type landing, not by shakes
    hits: [[tTitle, 3, 5]],
    draw(E) {
      const t = E.t, g = E.g;
      // ---- "Everything you're about to hear really happened."  (a pledge: it holds on HAPPENED, then is cleared before the title)
      if (t < 13.0) B([
        { txt: "EVERYTHING YOU'RE", font: 'B', fit: 1.0, maxCap: 0.045, ls: 0.04, times: [tw('o3', 'Everything'), tw('o3', "you're")] },
        { txt: 'ABOUT TO HEAR', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.03, times: [tw('o3', 'about'), tw('o3', 'to'), tw('o3', 'hear')] },
        { txt: 'REALLY', font: 'B', fit: 1.0, maxCap: 0.105, ls: 0.04, times: tw('o3', 'really'), curve: E.HEAVY },
        { txt: 'HAPPENED.', font: 'B', fit: 1.0, maxCap: 0.1, ls: 0.03, times: tw('o3', 'happened.'), curve: E.PAYOFF },
      ], 0.20, { out: 12.72, outDur: 0.3, k: 0.3 });
      // ---- the series title
      if (t >= tTitle - 0.05 && t < 15.35) E.titleCard(tTitle, 15.05, 0.24);
      // ---- HIS NAME WAS JOHANNES JUNIUS. then the name settles into the corner and becomes a label while the town draws itself under it
      if (t >= tw('x1', 'his') - 0.05 && t < 21.4) {
        const u = ease.inOutCubic(clamp((t - tMorph[0]) / (tMorph[1] - tMorph[0]))), top = 0.26, st = E.stk([
          { txt: 'HIS NAME WAS', font: 'B', cap: 0.040, ls: 0.16, times: [tw('x1', 'his'), tw('x1', 'name'), tw('x1', 'was')] },
          { txt: 'JOHANNES', font: 'B', fit: 1.0, maxCap: 0.105, ls: 0.02, times: tw('x1', 'Johannes'), curve: E.HEAVY },
          { txt: 'JUNIUS.', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.03, times: tw('x1', 'Junius.'), curve: E.PAYOFF },
        ], top, 0.3);
        const kick = st.lines[0], nm = st.lines.slice(1), yA = (nm[0].base - E.geo(nm[0]).cap) * H, Yf = 0.150 * H, s = lerp(1, 0.30, u), fade = 1 - clamp((t - 21.25) / 0.25);
        E.line({ color: cream, ...kick, out: tMorph[0], outDur: 0.25 });
        E.ink.save(); E.ink.translate(AX, yA + (Yf - yA) * u); E.ink.scale(s, s); E.ink.translate(-AX, -yA); E.ink.globalAlpha = fade * (1 - 0.35 * u);
        for (const l of nm) E.line({ color: cream, ...l });
        E.ink.restore();
      }
      // ---- the town: drawn on the desk line by line from the island outward
      if (t >= 18.6) {
        const c = M.cam(t); M.drawPlan(t, 18.85, 3.8, 1.0, c);
        if (t >= 33) M.drawChain(t, c);
        kit.dim(t < 33 ? 0.62 : 0.50, t < 21.3 ? 0.86 : 0.84);
      }
      if (t >= tw('x1', 'He') - 0.05 && t < 21.5) B([
        { txt: 'HE LIVED IN', font: 'B', cap: 0.040, ls: 0.16, times: [tw('x1', 'He'), tw('x1', 'lived'), tw('x1', 'in')] },
        { txt: 'BAMBERG,', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.03, times: tw('x1', 'Bamberg,'), curve: E.PAYOFF },
        { txt: 'IN GERMANY.', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.04, times: [tw('x1', 'in', 1), tw('x1', 'Germany.')], curve: E.HEAVY },
      ], 0.285, { out: 21.3, outDur: 0.2 });
      // ---- the fear, then the hunt (the camera pushes in on the town while "hunt them down" is said)
      if (t >= 21.3 && t < 24.4) B([
        { txt: 'AT THAT TIME,', font: 'B', cap: 0.038, ls: 0.14, times: [tw('x2', 'at'), tw('x2', 'that'), tw('x2', 'time,')] },
        { txt: 'MANY PEOPLE', font: 'B', fit: 1.0, maxCap: 0.07, ls: 0.03, times: [tw('x2', 'many'), tw('x2', 'people')] },
        { txt: 'BELIEVED', font: 'B', fit: 1.0, maxCap: 0.10, ls: 0.03, times: tw('x2', 'believed'), curve: E.HEAVY },
      ], 0.235, { out: 24.34, outDur: 0.2 });
      if (t >= 24.3 && t < 29.2) B([
        { txt: 'WITCHES CAUSED', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.06, times: [tw('x2', 'witches'), tw('x2', 'caused')], curves: [E.HEAVY, null] },
        { txt: 'STORMS', font: 'B', fit: 0.9, maxCap: 0.08, ls: 0.03, times: tw('x2', 'storms,') },
        { txt: 'SICKNESS', font: 'B', fit: 0.9, maxCap: 0.08, ls: 0.03, times: tw('x2', 'sickness') },
        { txt: 'FAILED', font: 'B', fit: 0.9, maxCap: 0.08, ls: 0.03, times: tw('x2', 'failed') },
        { txt: 'HARVESTS.', font: 'B', fit: 0.9, maxCap: 0.08, ls: 0.03, times: tw('x2', 'harvests.'), curve: E.PAYOFF },
      ], 0.17, { out: 28.95, outDur: 0.22, k: 0.3 });
      if (t >= 28.9 && t < 33.1) B([
        { txt: 'AND THE RULERS', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.04, times: [tw('x2', 'and', 1), tw('x2', 'the'), tw('x2', 'rulers')] },
        { txt: 'OF BAMBERG', font: 'B', fit: 1.0, maxCap: 0.07, ls: 0.03, times: [tw('x2', 'of'), tw('x2', 'Bamberg')], curves: [null, E.HEAVY] },
        { txt: 'DECIDED TO', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.04, times: [tw('x2', 'decided'), tw('x2', 'to')] },
        { txt: 'HUNT THEM', font: 'B', fit: 1.0, maxCap: 0.08, ls: 0.03, times: [tw('x2', 'hunt'), tw('x2', 'them')], curves: [E.HEAVY, null] },
        { txt: 'DOWN.', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.04, times: tw('x2', 'down.'), curve: E.PAYOFF },
      ], 0.165, { out: 33.0, outDur: 0.2, k: 0.28 });
      // ---- the method: the chain of accusations grows on the town
      if (t >= 33.0 && t < 35.45) B([
        { txt: 'THEIR METHOD', font: 'B', fit: 1.0, maxCap: 0.07, ls: 0.03, times: [tw('x3', 'their'), tw('x3', 'method')] },
        { txt: 'WAS SIMPLE.', font: 'B', fit: 1.0, maxCap: 0.09, ls: 0.03, times: [tw('x3', 'was'), tw('x3', 'simple.')], curves: [null, E.PAYOFF] },
      ], 0.22, { out: 35.4, outDur: 0.18 });
      if (t >= 35.35 && t < 36.95) B([{ txt: 'ARREST SOMEONE.', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.03, times: [tw('x3', 'arrest'), tw('x3', 'someone.')], curves: [E.HEAVY, E.HEAVY] }], 0.22, { out: 36.9, outDur: 0.18 });
      if (t >= 36.85 && t < 39.6) B([
        { txt: 'TORTURE THEM', font: 'B', fit: 1.0, maxCap: 0.065, ls: 0.03, times: [tw('x3', 'torture'), tw('x3', 'them')], curves: [E.PAYOFF, null] },
        { txt: 'UNTIL THEY GIVE', font: 'B', fit: 0.8, maxCap: 0.04, ls: 0.05, times: [tw('x3', 'until'), tw('x3', 'they'), tw('x3', 'give')] },
        { txt: 'NAMES.', font: 'B', fit: 0.85, maxCap: 0.085, ls: 0.04, times: tw('x3', 'names.'), curve: E.PAYOFF },
      ], 0.17, { out: 39.55, outDur: 0.2 });
      if (t >= 39.5 && t < 41.65) B([
        { txt: 'THEN ARREST', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.04, times: [tw('x3', 'then'), tw('x3', 'arrest', 1)] },
        { txt: 'THOSE PEOPLE.', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, times: [tw('x3', 'those'), tw('x3', 'people.')], curves: [null, E.PAYOFF] },
      ], 0.18, { out: 41.55, outDur: 0.18 });
      if (t >= 41.5 && t < 44.5) B([
        { txt: "JUNIUS'S WIFE", font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.03, times: [tw('x4', "Junius's"), tw('x4', 'wife')], curves: [E.HEAVY, null] },
        { txt: 'WAS NAMED.', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, times: [tw('x4', 'was'), tw('x4', 'named.')], curves: [null, E.PAYOFF] },
      ], 0.19, { out: 44.42, outDur: 0.2 });
      if (t >= 44.35 && t < 47.1) B([
        { txt: 'SHE WAS', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.08, times: [tw('x4', 'she'), tw('x4', 'was', 1)] },
        { txt: 'EXECUTED.', font: 'B', fit: 1.0, maxCap: 0.095, ls: 0.03, times: tw('x4', 'executed.'), curve: E.PAYOFF },
      ], 0.19, { out: 47.05, outDur: 0.2 });
      if (t >= 47.0) B([
        { txt: 'THEN', font: 'B', cap: 0.035, ls: 0.2, times: tw('x5', 'then') },
        { txt: 'SIX', font: 'B', fit: 0.5, maxCap: 0.15, ls: 0.03, times: tw('x5', 'six'), curve: E.PAYOFF },
        { txt: 'PEOPLE NAMED HIM.', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.04, times: [tw('x5', 'people'), tw('x5', 'named'), tw('x5', 'him.')], curves: [null, E.HEAVY, E.HEAVY] },
      ], 0.155, { k: 0.3 });
    },
  });
  return S;
}
